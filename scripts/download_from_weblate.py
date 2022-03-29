#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import traceback
import urllib.error
from abc import abstractmethod
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime as parse_rfc2822_date
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Protocol

import internal_utils

PROJECT_ORIGINAL_LOCALE = "en_US"
PROJECT_ORIGINAL_LOCALE_WEBLATE = "en"
PROJECT_LOCALE = "es_ES"
PROJECT_LOCALE_WEBLATE = "es"
PROJECT_TARGET_GAME_VERSION = "1.4.2-1"

CROSSLOCALE_BIN_NAME = "crosslocale"
PROJECT_DIR = Path(__file__).parent.parent
LOCALIZE_ME_PACKS_DIR = PROJECT_DIR / "packs"
LOCALIZE_ME_MAPPING_FILE = PROJECT_DIR / "packs-mapping.json"
WORK_DIR = PROJECT_DIR / ".trpack-compiler"
DOWNLOADS_DIR = WORK_DIR / "download"
DOWNLOADS_STATE_FILE = WORK_DIR / "downloads-state.json"
CROSSLOCALE_SCAN_FILE = WORK_DIR / f"scan-{PROJECT_TARGET_GAME_VERSION}.json"
NETWORK_TIMEOUT = 60
NETWORK_THREADS = 10


class ComponentMeta(NamedTuple):
  id: str
  modification_timestamp: Optional[datetime]


class ComponentDownloader(Protocol):

  @abstractmethod
  def fetch_list(self) -> List[ComponentMeta]:
    raise NotImplementedError()

  @abstractmethod
  def fetch_component(self, component: ComponentMeta) -> None:
    raise NotImplementedError()


class WeblateApiComponentDownloader(ComponentDownloader):
  HOST = "https://weblate.openkrosskod.org"

  def fetch_list(self) -> List[ComponentMeta]:
    components: List[ComponentMeta] = []
    next_api_url = f"{self.HOST}/api/projects/crosscode/statistics/{PROJECT_LOCALE_WEBLATE}/"
    while next_api_url is not None:
      with internal_utils.http_request(next_api_url, timeout=NETWORK_TIMEOUT) as (_, reader):
        api_response = json.load(reader)
        next_api_url = api_response["next"]
        for stats_obj in api_response["results"]:
          c_id = stats_obj["component"]
          if c_id == "glossary":
            continue
          mtime: Optional[datetime] = None
          mtime_str: Optional[str] = stats_obj["last_change"]
          if mtime_str is not None:
            mtime = datetime.fromisoformat(
              mtime_str[:-1] + "+00:00" if mtime_str.endswith("Z") else mtime_str
            )
          components.append(ComponentMeta(id=c_id, modification_timestamp=mtime))
    return components

  def fetch_component(self, component: ComponentMeta) -> None:
    download_url = f"{self.HOST}/download/crosscode/{component.id}/{PROJECT_LOCALE_WEBLATE}"
    with internal_utils.http_request(download_url, timeout=NETWORK_TIMEOUT) as (_, reader):
      with open(DOWNLOADS_DIR / f"{component.id}.po", "wb") as output_file:
        shutil.copyfileobj(reader, output_file)


class NginxApiComponentDownloader(ComponentDownloader):
  HOST = "https://stronghold.openkrosskod.org"

  def fetch_list(self) -> List[ComponentMeta]:
    components: List[ComponentMeta] = []
    api_url = f"{self.HOST}/__json__/~weblate/download/crosscode/{PROJECT_LOCALE}/components/"
    with internal_utils.http_request(api_url, timeout=NETWORK_TIMEOUT) as (_, reader):
      for file_meta in json.load(reader):
        if file_meta["type"] == "file" and file_meta["name"].endswith(".po"):
          mtime = parse_rfc2822_date(file_meta["mtime"])
          components.append(ComponentMeta(id=file_meta["name"][:-3], modification_timestamp=mtime))
    return components

  def fetch_component(self, component: ComponentMeta) -> None:
    download_url = f"{self.HOST}/__json__/~weblate/download/crosscode/{PROJECT_LOCALE}/components/{component.id}.po"
    with internal_utils.http_request(download_url, timeout=NETWORK_TIMEOUT) as (_, reader):
      with open(DOWNLOADS_DIR / f"{component.id}.po", "wb") as output_file:
        shutil.copyfileobj(reader, output_file)


def main() -> None:
  WORK_DIR.mkdir(exist_ok=True)
  DOWNLOADS_DIR.mkdir(exist_ok=True)

  print("==> reading the downloads state")
  downloads_state: Dict[str, ComponentMeta] = {}
  try:
    with open(DOWNLOADS_STATE_FILE, "r") as file:
      downloads_state_json = json.load(file)
      if downloads_state_json["version"] == 1:
        for c_id, c_data in downloads_state_json["data"].items():
          c_mtime: Optional[float] = c_data["mtime"]
          downloads_state[c_id] = ComponentMeta(
            id=c_id,
            modification_timestamp=datetime.fromtimestamp(c_mtime, timezone.utc)
            if c_mtime is not None else None,
          )
  except FileNotFoundError:
    pass

  downloader: ComponentDownloader = WeblateApiComponentDownloader()
  print("==> downloading the list of components")
  remote_components_list = downloader.fetch_list()

  components_to_fetch_list: List[ComponentMeta] = []
  for remote_meta in remote_components_list:
    local_meta = downloads_state.get(remote_meta.id)
    should_fetch: bool

    if local_meta is None:
      # We don't have this component download, it has probably been created
      should_fetch = True
    else:
      # Notice that missing timestamps mean that the component has never been
      # modified so far
      remote_mtime = remote_meta.modification_timestamp
      local_mtime = local_meta.modification_timestamp

      if remote_mtime is None and local_mtime is None:
        # We have downloaded an empty component and there are still no changes
        # affecting it
        should_fetch = False
      elif remote_mtime is not None and local_mtime is None:
        # Got the first ever changes!
        should_fetch = True
      elif remote_mtime is None and local_mtime is not None:
        # We have already downloaded some changed version of the component, but
        # it has probably been reset to an empty state since.
        should_fetch = True
      elif remote_mtime is not None and local_mtime is not None:
        # The sane and normal code path.
        should_fetch = remote_mtime > local_mtime
      else:
        raise Exception("unreachable")

    if should_fetch:
      components_to_fetch_list.append(remote_meta)

  with ThreadPool(NETWORK_THREADS) as pool:
    print(f"==> downloading {len(components_to_fetch_list)} component(s) from Weblate")

    def callback(component: ComponentMeta) -> ComponentMeta:
      downloader.fetch_component(component)
      return component

    for component in pool.imap_unordered(callback, components_to_fetch_list):
      print(f"downloaded {component.id}")
      downloads_state[component.id] = component

  if not CROSSLOCALE_SCAN_FILE.exists():
    print(f"==> downloading the scan database for v{PROJECT_TARGET_GAME_VERSION}")

    download_urls = [
      "https://raw.githubusercontent.com/dmitmel/crosscode-localization-data/main/scan.json",
      f"https://raw.githubusercontent.com/dmitmel/crosslocale-scans/main/scan-{PROJECT_TARGET_GAME_VERSION}.json"
    ]
    for i, download_url in enumerate(download_urls):
      try:
        with internal_utils.http_request(download_url, timeout=NETWORK_TIMEOUT) as (_, reader):
          with open(CROSSLOCALE_SCAN_FILE, "wb") as output_file:
            shutil.copyfileobj(reader, output_file)
        break
      except urllib.error.HTTPError:
        if i < len(download_url) - 1:
          traceback.print_exc()
        else:
          raise

  print("==> starting the translation pack compiler")
  crosslocale_bin = PROJECT_DIR / CROSSLOCALE_BIN_NAME
  if os.name == "nt":
    crosslocale_bin = crosslocale_bin.with_suffix(".exe")
  if not crosslocale_bin.exists():
    # fall back to finding the binary in PATH
    crosslocale_bin = CROSSLOCALE_BIN_NAME
  subprocess.run(
    [
      crosslocale_bin,
      "convert",
      f"--scan={CROSSLOCALE_SCAN_FILE}",
      "--format=po",
      f"--original-locale={PROJECT_ORIGINAL_LOCALE}",
      "--remove-untranslated",
      "--compact",
      "--output-format=lm-tr-pack",
      f"--output={LOCALIZE_ME_PACKS_DIR}",
      "--splitter=lm-file-tree",
      "--mapping-lm-paths",
      f"--mapping-output={LOCALIZE_ME_MAPPING_FILE}",
      "--",
      DOWNLOADS_DIR,
    ],
    check=True,
  )

  print("==> writing the downloads state")
  with open(DOWNLOADS_STATE_FILE, "w") as file:
    downloads_state_json: Any = {
      "version": 1,
      "data": {
        component_meta.id: {
          "mtime":
            component_meta.modification_timestamp.timestamp()
            if component_meta.modification_timestamp is not None else None,
        } for component_meta in downloads_state.values()
      },
    }
    json.dump(downloads_state_json, file, ensure_ascii=False, indent=2)
    file.write("\n")

  print("==> done!")


if __name__ == "__main__":
  main()
