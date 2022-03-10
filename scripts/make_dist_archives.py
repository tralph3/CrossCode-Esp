#!/usr/bin/env python3

import glob
import json
import shutil
import subprocess
import urllib.parse
from pathlib import Path
from tarfile import TarFile
from typing import List, Optional, Type

import internal_utils

PROJECT_DIR = Path(__file__).parent.parent
WORK_DIR = PROJECT_DIR / "dist"
DOWNLOADS_DIR = WORK_DIR / "download"

MOD_FILES_PATTERNS = [
  "ccmod.json",
  "icon*.png",
  "LICENSE*",
  "README*",
  "packs-mapping.json",
  "src/**/*.js",
  "packs/**/*.json",
  "assets/**/*.png",
]

LOCALIZE_ME_DOWNLOAD_COMMIT = "cd84932c815297c6777fafcf4e5fcfbc0d3d6cc3"
CCLOADER3_DOWNLOAD_DATE = "20220208223224"
ULTIMATE_UI_DOWNLOAD_VERSION = "1.3.3", "1.1.0"
NETWORK_TIMEOUT = 5


def main() -> None:
  WORK_DIR.mkdir(exist_ok=True)
  DOWNLOADS_DIR.mkdir(exist_ok=True)

  print("==> downloading dependencies")

  localize_me_file = download_dependency(
    f"https://github.com/L-Sherry/Localize-me/tarball/{LOCALIZE_ME_DOWNLOAD_COMMIT}",
    filename=f"Localize-me-{LOCALIZE_ME_DOWNLOAD_COMMIT}.tgz",
  )

  ccloader_file = download_dependency(
    f"https://stronghold.openkrosskod.org/~dmitmel/ccloader3/{CCLOADER3_DOWNLOAD_DATE}/ccloader_3.0.0-alpha_quick-install.tar.gz",
    filename=f"ccloader-{CCLOADER3_DOWNLOAD_DATE}.tgz",
  )

  ultimate_ui_file = download_dependency(
    f"https://github.com/CCDirectLink/crosscode-ru/releases/download/v{ULTIMATE_UI_DOWNLOAD_VERSION[0]}/ultimate-localized-ui_v{ULTIMATE_UI_DOWNLOAD_VERSION[1]}.tgz",
    filename=f"ultimate-localized-ui-{ULTIMATE_UI_DOWNLOAD_VERSION[1]}.tgz",
  )

  print("==> collecting metadata")

  with open(PROJECT_DIR / "ccmod.json", "r") as manifest_file:
    manifest = json.load(manifest_file)
    mod_id: str = manifest["id"]
    mod_version: str = manifest["version"]

  mod_files: List[str] = []
  for pattern in MOD_FILES_PATTERNS:
    mod_files.extend(
      str(Path(path).relative_to(PROJECT_DIR))
      for path in glob.iglob(str(PROJECT_DIR / pattern), recursive=True)
    )
  # Note that paths here are sorted as strings and not as lists of their
  # components, in other words, the path separators will also be taken into
  # account when sorting.
  mod_files.sort()

  commiter_time = int(
    subprocess.run(
      ["git", "log", "--max-count=1", "--date=unix", "--pretty=format:%cd"],
      check=True,
      stdout=subprocess.PIPE,
    ).stdout
  )

  print("==> making packages")

  all_archive_adapters: List[Type[internal_utils.ArchiveAdapter]] = [
    internal_utils.TarGzArchiveAdapter,
    internal_utils.ZipArchiveAdapter,
  ]
  for archive_cls in all_archive_adapters:

    def archive_add_mod_files(archived_prefix: Path) -> None:
      print("+ adding mod files")
      for file in mod_files:
        archive.add_real_file(
          str(PROJECT_DIR / file),
          str(archived_prefix / file),
          recursive=False,
          mtime=commiter_time,
        )

    def archive_add_dependency(
      archived_prefix: Path, dependency_path: Path, strip_components: int
    ) -> None:
      print(f"+ adding files from {dependency_path.name}")
      with TarFile.gzopen(dependency_path) as dependency_archive:
        for file_info in dependency_archive:
          archived_path = str(
            Path(
              archived_prefix,
              *Path(file_info.name).parts[strip_components:],
            )
          )
          if file_info.isreg():
            file_reader = dependency_archive.extractfile(file_info)
            assert file_reader is not None
            archive.add_file_entry(archived_path, file_reader.read(), mtime=file_info.mtime)
          elif file_info.issym():
            archive.add_symlink_entry(archived_path, file_info.linkname, mtime=file_info.mtime)
          elif file_info.isdir():
            # Directories are deliberately ignored because the previous setup
            # didn't put them into resulting archives, and their entries are
            # useless to us anyway.
            pass
          else:
            # Other file types (character devices, block devices and named
            # pipes) are UNIX-specific and can't be handled by Zip, but it's
            # not like they are used in dependencies anyway. Correction: well,
            # after checking APPNOTE.TXT section 4.5.7 I noticed that these
            # exotic file types may be supported, but it's not like any modding
            # projects use those.
            pass

    archive_name = f"{mod_id}_v{mod_version}{archive_cls.DEFAULT_EXTENSION}"
    print(f"making {archive_name}")
    with archive_cls.create(WORK_DIR / archive_name) as archive:
      archive_add_mod_files(Path(mod_id))

    archive_name = f"{mod_id}_quick-install_v{mod_version}{archive_cls.DEFAULT_EXTENSION}"
    print(f"making {archive_name}")
    with archive_cls.create(WORK_DIR / archive_name) as archive:
      archive_add_mod_files(Path("assets", "mods", mod_id))
      archive_add_dependency(Path("assets", "mods", "Localize-me"), localize_me_file, 1)
      archive_add_dependency(Path("assets", "mods"), ultimate_ui_file, 0)
      archive_add_dependency(Path(), ccloader_file, 0)

  print("==> done!")


def download_dependency(url: str, filename: Optional[str] = None) -> Path:
  if filename is None:
    filename = urllib.parse.urlparse(url).path
    filename = filename[filename.rfind("/") + 1:]
  download_path = DOWNLOADS_DIR / filename

  try:
    if download_path.exists():
      return download_path

    with internal_utils.http_request(url, timeout=NETWORK_TIMEOUT) as (_, reader):
      with open(download_path, "wb") as file:
        shutil.copyfileobj(reader, file)
  except BaseException:
    download_path.unlink()
    raise

  return download_path


if __name__ == "__main__":
  main()
