#!/usr/bin/env python3
import urllib.request
import json
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import NamedTuple, Optional, Any, List, Dict
from abc import ABCMeta, abstractmethod
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import io
import subprocess
import os


PROJECT_ORIGINAL_LOCALE = "en_US"
PROJECT_ORIGINAL_LOCALE_SHORT = "en"
PROJECT_LOCALE = "es_ES"
PROJECT_LOCALE_SHORT = "es"
PROJECT_TARGET_GAME_VERSION = "1.4.1-2"

PROJECT_DIR = Path(__file__).parent.parent
LOCALIZE_ME_PACKS_DIR = PROJECT_DIR / "packs"
LOCALIZE_ME_MAPPING_FILE = PROJECT_DIR / "packs-mapping.json"
COMPILER_WORK_DIR = PROJECT_DIR / ".trpack-compiler"
DOWNLOADS_DIR = COMPILER_WORK_DIR / "download"
DOWNLOADS_STATE_FILE = COMPILER_WORK_DIR / "downloads-state.json"
CROSSLOCALE_SCAN_FILE = COMPILER_WORK_DIR / f"scan-{PROJECT_TARGET_GAME_VERSION}.json"
# CROSSLOCALE_PROJECT_DIR = COMPILER_WORK_DIR / "project"
NETWORK_TIMEOUT = 5
NETWORK_THREADS = 10

COMPILER_WORK_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)
# CROSSLOCALE_PROJECT_DIR.mkdir(exist_ok=True)

crosslocale_bin = (PROJECT_DIR / "crosslocale").with_suffix(".exe" if os.name == "nt" else "")
if not crosslocale_bin.exists():
  # fall back to finding the binary in PATH
  crosslocale_bin = "crosslocale"


class ComponentMeta(NamedTuple):
  id: str
  modification_timestamp: Optional[datetime]


class ComponentDownloader(metaclass=ABCMeta):

  @abstractmethod
  def fetch_list(self) -> List[ComponentMeta]:
    raise NotImplementedError()

  @abstractmethod
  def fetch_component(self, component: ComponentMeta):
    raise NotImplementedError()


class WeblateApiComponentDownloader(ComponentDownloader):
  HOST = "https://weblate.crosscode.ru"

  def fetch_list(self) -> List[ComponentMeta]:
    components: List[ComponentMeta] = []
    next_api_url = f"{self.HOST}/api/projects/crosscode/components/"
    while next_api_url is not None:
      print(f"fetching {next_api_url}")
      with urllib.request.urlopen(next_api_url, timeout=NETWORK_TIMEOUT) as response:
        api_response = json.load(response)
        next_api_url = api_response["next"]
        for component in api_response["results"]:
          components.append(ComponentMeta(id=component["slug"], modification_timestamp=None))
    return components

  def fetch_component(self, component: ComponentMeta) -> None:
    download_url = f"{self.HOST}/download/crosscode/{component.id}/{PROJECT_LOCALE}"
    print(f"fetching {download_url}")
    with urllib.request.urlopen(download_url, timeout=NETWORK_TIMEOUT) as response:
      with open(DOWNLOADS_DIR / f"{component.id}.po", "wb") as output_file:
        while True:
          buf = response.read(io.DEFAULT_BUFFER_SIZE)
          if not buf:
            break
          output_file.write(buf)


class NginxApiComponentDownloader(ComponentDownloader):
  HOST = "https://stronghold.crosscode.ru"

  def fetch_list(self) -> List[ComponentMeta]:
    components: List[ComponentMeta] = []
    api_url = f"{self.HOST}/__json__/~weblate/download/crosscode/{PROJECT_LOCALE}/components/"
    print(f"fetching {api_url}")
    with urllib.request.urlopen(api_url, timeout=NETWORK_TIMEOUT) as response:
      for file_meta in json.load(response):
        if file_meta["type"] == "file" and file_meta["name"].endswith(".po"):
          mtime = parsedate_to_datetime(file_meta["mtime"])
          components.append(ComponentMeta(id=file_meta["name"][:-3], modification_timestamp=mtime))
    return components

  def fetch_component(self, component: ComponentMeta) -> None:
    download_url = f"{self.HOST}/__json__/~weblate/download/crosscode/{PROJECT_LOCALE}/components/{component.id}.po"
    print(f"fetching {download_url}")
    with urllib.request.urlopen(download_url, timeout=NETWORK_TIMEOUT) as response:
      with open(DOWNLOADS_DIR / f"{component.id}.po", "wb") as output_file:
        while True:
          buf = response.read(io.DEFAULT_BUFFER_SIZE)
          if not buf:
            break
          output_file.write(buf)


def main() -> None:
  print("==> reading the downloads state")
  downloads_state: Dict[str, ComponentMeta] = {}
  try:
    with open(DOWNLOADS_STATE_FILE, "r") as file:
      downloads_state_json = json.load(file)
      if downloads_state_json["version"] == 1:
        for c_id, c_data in downloads_state_json["data"].items():
          downloads_state[c_id] = ComponentMeta(
            c_id, datetime.fromtimestamp(c_data["mtime"], timezone.utc)
          )
  except FileNotFoundError:
    pass

  downloader: ComponentDownloader = NginxApiComponentDownloader()
  print("==> downloading the list of components")
  remote_components_list = downloader.fetch_list()

  components_to_fetch_list: List[ComponentMeta] = []
  for remote_meta in remote_components_list:
    local_meta = downloads_state.get(remote_meta.id)
    if (
      local_meta is None or remote_meta.modification_timestamp is None or
      local_meta.modification_timestamp is None or
      remote_meta.modification_timestamp > local_meta.modification_timestamp
    ):
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

    download_url = f"https://raw.githubusercontent.com/dmitmel/crosslocale-scans/main/scan-{PROJECT_TARGET_GAME_VERSION}.json"
    print(f"fetching {download_url}")
    with urllib.request.urlopen(download_url, timeout=NETWORK_TIMEOUT) as response:
      with open(CROSSLOCALE_SCAN_FILE, "wb") as output_file:
        while True:
          buf = response.read(io.DEFAULT_BUFFER_SIZE)
          if not buf:
            break
          output_file.write(buf)

  print("==> starting the translation pack compiler")
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
          "mtime": component_meta.modification_timestamp.timestamp(),
        } for component_meta in downloads_state.values()
      },
    }
    json.dump(downloads_state_json, file, ensure_ascii=False, indent=2)
    file.write("\n")

  print("==> done!")


if __name__ == "__main__":
  main()
