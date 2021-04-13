#!/usr/bin/env python3
import urllib.request
import json
from multiprocessing.pool import ThreadPool
from pathlib import Path
import typing
from abc import ABCMeta, abstractmethod
from datetime import datetime
from email.utils import parsedate_to_datetime
import io
import subprocess

PROJECT_ORIGINAL_LOCALE = "en_US"
PROJECT_ORIGINAL_LOCALE_SHORT = "en"
PROJECT_LOCALE = "es_ES"
PROJECT_LOCALE_SHORT = "es"
CROSSLOCALE_BIN = "crosslocale"

PROJECT_DIR = Path(__file__).parent.parent
CROSSLOCALE_SCAN_FILE = PROJECT_DIR / "scan.json"
LOCALIZE_ME_PACKS_DIR = PROJECT_DIR / "packs"
LOCALIZE_ME_MAPPING_FILE = PROJECT_DIR / "packs-mapping.json"
TMP_DIR = PROJECT_DIR / ".trpack-compiler"
DOWNLOADS_DIR = TMP_DIR / "download"
CROSSLOCALE_PROJECT_DIR = TMP_DIR / "project"
NETWORK_TIMEOUT = 5
NETWORK_THREADS = 10

TMP_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)
CROSSLOCALE_PROJECT_DIR.mkdir(exist_ok=True)


class ComponentMeta(typing.NamedTuple):
    slug: str
    modification_timestamp: typing.Optional[datetime]


class ComponentDownloader(metaclass=ABCMeta):
    @abstractmethod
    def fetch_list(self) -> typing.Iterable[ComponentMeta]:
        raise NotImplementedError()

    @abstractmethod
    def fetch_component(self, component: ComponentMeta):
        raise NotImplementedError()


class WeblateApiComponentDownloader(ComponentDownloader):
    HOST = "https://weblate.crosscode.ru"

    def fetch_list(self) -> typing.Iterable[ComponentMeta]:
        components = []
        next_api_url = f"{self.HOST}/api/projects/crosscode/components/"
        while next_api_url is not None:
            print(f"fetching {next_api_url}")
            with urllib.request.urlopen(
                next_api_url, timeout=NETWORK_TIMEOUT
            ) as response:
                api_response = json.load(response)
                next_api_url = api_response["next"]
                for component in api_response["results"]:
                    components.append(
                        ComponentMeta(
                            slug=component["slug"], modification_timestamp=None
                        )
                    )
        return components

    def fetch_component(self, component: ComponentMeta) -> None:
        download_url = (
            f"{self.HOST}/download/crosscode/{component.slug}/{PROJECT_LOCALE}"
        )
        print(f"fetching {download_url}")
        with urllib.request.urlopen(download_url, timeout=NETWORK_TIMEOUT) as response:
            with open(DOWNLOADS_DIR / f"{component.slug}.po", "wb") as output_file:
                while True:
                    buf = response.read(io.DEFAULT_BUFFER_SIZE)
                    if not buf:
                        break
                    output_file.write(buf)


class NginxApiComponentDownloader(ComponentDownloader):
    HOST = "https://stronghold.crosscode.ru"

    def fetch_list(self) -> typing.Iterable[ComponentMeta]:
        components = []
        api_url = f"{self.HOST}/__json__/~weblate/download/crosscode/{PROJECT_LOCALE}/components/"
        print(f"fetching {api_url}")
        with urllib.request.urlopen(api_url, timeout=NETWORK_TIMEOUT) as response:
            for file_meta in json.load(response):
                if file_meta["type"] == "file" and file_meta["name"].endswith(".po"):
                    mtime = parsedate_to_datetime(file_meta["mtime"])
                    components.append(
                        ComponentMeta(
                            slug=file_meta["name"][:-3], modification_timestamp=mtime
                        )
                    )
        return components

    def fetch_component(self, component: ComponentMeta) -> None:
        download_url = f"{self.HOST}/__json__/~weblate/download/crosscode/{PROJECT_LOCALE}/components/{component.slug}.po"
        print(f"fetching {download_url}")
        with urllib.request.urlopen(download_url, timeout=NETWORK_TIMEOUT) as response:
            with open(DOWNLOADS_DIR / f"{component.slug}.po", "wb") as output_file:
                while True:
                    buf = response.read(io.DEFAULT_BUFFER_SIZE)
                    if not buf:
                        break
                    output_file.write(buf)


def main() -> None:
    downloader: ComponentDownloader = NginxApiComponentDownloader()
    print("==> downloading the list of components")
    components_list = downloader.fetch_list()

    with ThreadPool(NETWORK_THREADS) as pool:
        print("==> downloading the .po files from Weblate")

        def callback(component: ComponentMeta) -> ComponentMeta:
            downloader.fetch_component(component)
            return component

        for component in pool.imap_unordered(callback, components_list):
            print(f"downloaded {component.slug}")

    subprocess.run(
        [
            CROSSLOCALE_BIN,
            "convert",
            "--scan={}".format(CROSSLOCALE_SCAN_FILE),
            "--format=po",
            "--original-locale={}".format(PROJECT_ORIGINAL_LOCALE),
            "--remove-untranslated",
            "--compact",
            "--output-format=lm-tr-pack",
            "--output={}".format(LOCALIZE_ME_PACKS_DIR),
            "--splitter=lm-file-tree",
            "--mapping-lm-paths",
            "--mapping-output={}".format(LOCALIZE_ME_MAPPING_FILE),
            "--",
            DOWNLOADS_DIR,
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
