import gzip
import io
import os
import shutil
import stat
import tarfile
import time
import urllib.parse
import urllib.request
import zipfile
from abc import abstractmethod
from contextlib import contextmanager
from http.client import HTTPResponse
from tarfile import TarFile, TarInfo
from types import TracebackType
from typing import IO, Any, Callable, Generator, Optional, Protocol, Tuple, Type, Union
from zipfile import ZipFile, ZipInfo

StrPath = Union[str, "os.PathLike[str]"]


@contextmanager
def http_request(
  url: str,
  timeout: Optional[float] = None
  # TODO: retry on failure
) -> Generator[Tuple[HTTPResponse, io.BufferedIOBase], None, None]:
  print(f"fetching {url}")
  req = urllib.request.Request(url)
  req.add_header("Accept-Encoding", "gzip")

  res: object
  with urllib.request.urlopen(req, timeout=timeout) as res:
    if not isinstance(res, HTTPResponse):
      raise Exception("Not an HTTP request")
    reader: io.BufferedIOBase = res

    # <https://github.com/kurtmckee/feedparser/blob/727ee7f08f77d8f0a0f085ec3dfbc58e09f69a4b/feedparser/http.py#L166-L188>
    content_encoding = res.getheader("content-encoding")
    if content_encoding == "gzip":
      reader = gzip.GzipFile(fileobj=res)

    yield res, reader


class ArchiveAdapter(Protocol):
  """
  Taken from <https://github.com/dmitmel/ccloader3/blob/77e09dbb09abbc1b454b82c7467a0e92a14dc3ab/scripts/create-dist-archive.py>.
  """

  _DEFAULT_FILE_MODE = 0o644
  _SYMLINK_FILE_MODE = 0o777
  _DEFAULT_DIR_MODE = 0o755

  FileFilter = Callable[[str], bool]

  DEFAULT_EXTENSION: str

  @classmethod
  @abstractmethod
  def create(cls, path: StrPath) -> "ArchiveAdapter":
    raise NotImplementedError()

  @abstractmethod
  def __enter__(self) -> "ArchiveAdapter":
    raise NotImplementedError()

  @abstractmethod
  def __exit__(
    self,
    exc_type: Optional[Type[BaseException]],
    exc_value: Optional[BaseException],
    traceback: Optional[TracebackType],
  ) -> Optional[bool]:
    raise NotImplementedError()

  @abstractmethod
  def add_file_entry(self, name: str, data: bytes, mtime: int = 0) -> None:
    raise NotImplementedError()

  @abstractmethod
  def add_symlink_entry(self, name: str, target: str, mtime: int = 0) -> None:
    raise NotImplementedError()

  @abstractmethod
  def add_dir_entry(self, name: str, mtime: int = 0) -> None:
    raise NotImplementedError()

  @abstractmethod
  def add_real_file(
    self,
    path: str,
    archived_path: str,
    recursive: bool = True,
    predicate: Optional[FileFilter] = None,
    mtime: Optional[int] = None,
  ) -> None:
    raise NotImplementedError()


class TarGzArchiveAdapter(ArchiveAdapter):
  """
  Taken from <https://github.com/dmitmel/ccloader3/blob/77e09dbb09abbc1b454b82c7467a0e92a14dc3ab/scripts/create-dist-archive.py#L57-L105>.
  """

  DEFAULT_EXTENSION = ".tgz"

  @classmethod
  def create(cls, path: StrPath) -> "TarGzArchiveAdapter":
    # GzipFile has to be created manually if we want reproducibility...
    # <https://bugs.python.org/issue31526>
    fileobj = gzip.GzipFile(path, "wb", mtime=0)
    try:
      t: Any = TarFile(path, "w", fileobj, format=tarfile.GNU_FORMAT)
      # This will close the underlying GzipFile to be closed when the TarFile is
      # closed. The field name probably deciphers to "external file object".
      t._extfileobj = False
      return cls(t)
    except BaseException:
      # Safeguard, taken from the `TarFile.gzopen` function.
      fileobj.close()
      raise

  def __init__(self, inner: TarFile) -> None:
    self._inner = inner

  def __enter__(self) -> "TarGzArchiveAdapter":
    self._inner.__enter__()
    return self

  def __exit__(
    self,
    exc_type: Optional[Type[BaseException]],
    exc_value: Optional[BaseException],
    traceback: Optional[TracebackType],
  ) -> Optional[bool]:
    return self._inner.__exit__(exc_type, exc_value, traceback)

  def add_file_entry(self, name: str, data: bytes, mtime: int = 0) -> None:
    return self._add_entry(
      name,
      tarfile.REGTYPE,
      self._DEFAULT_FILE_MODE,
      mtime,
      len(data),
      io.BytesIO(data),
    )

  def add_symlink_entry(self, name: str, target: str, mtime: int = 0) -> None:
    return self._add_entry(name, tarfile.SYMTYPE, self._SYMLINK_FILE_MODE, mtime, 0, None, target)

  def add_dir_entry(self, name: str, mtime: int = 0) -> None:
    return self._add_entry(name, tarfile.DIRTYPE, self._DEFAULT_DIR_MODE, mtime, 0, None)

  def _add_entry(
    self,
    name: str,
    type: bytes,
    mode: int,
    mtime: int,
    size: int,
    data: Optional[IO[bytes]],
    linkname: str = "",
  ) -> None:
    info = TarInfo(name)
    info.type = type
    info.mode = mode
    info.size = size
    info.mtime = mtime
    info.linkname = linkname
    return self._inner.addfile(info, data)

  def add_real_file(
    self,
    path: str,
    archived_path: str,
    recursive: bool = True,
    predicate: Optional[ArchiveAdapter.FileFilter] = None,
    mtime: Optional[int] = None,
  ) -> None:
    return self._inner.add(
      path,
      arcname=archived_path,
      recursive=recursive,
      filter=lambda info: self._reset_tarinfo(info, predicate, mtime),
    )

  def _reset_tarinfo(
    self,
    info: TarInfo,
    predicate: Optional[ArchiveAdapter.FileFilter],
    mtime: Optional[int],
  ) -> Optional[TarInfo]:
    if predicate is not None and not predicate(info.name):
      return None

    # remove user and group IDs as they are irrelevant for distribution and
    # may require subsequent `chown`ing on multi-tenant systems
    info.uid = 0
    info.uname = ""
    info.gid = 0
    info.gname = ""

    if mtime is not None:
      info.mtime = mtime

    return info


class ZipArchiveAdapter(ArchiveAdapter):
  """
  Taken from <https://github.com/dmitmel/ccloader3/blob/77e09dbb09abbc1b454b82c7467a0e92a14dc3ab/scripts/create-dist-archive.py#L108-L165>.
  """

  DEFAULT_EXTENSION = ".zip"

  @classmethod
  def create(cls, path: StrPath) -> "ZipArchiveAdapter":
    return cls(ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, strict_timestamps=False))

  def __init__(self, inner: ZipFile) -> None:
    self._inner = inner

  def __enter__(self) -> "ZipArchiveAdapter":
    self._inner.__enter__()
    return self

  def __exit__(
    self,
    exc_type: Optional[Type[BaseException]],
    exc_value: Optional[BaseException],
    traceback: Optional[TracebackType],
  ) -> Optional[bool]:
    return self._inner.__exit__(exc_type, exc_value, traceback)

  def add_file_entry(self, name: str, data: bytes, mtime: int = 0) -> None:
    return self._add_entry(name, (stat.S_IFREG | self._DEFAULT_FILE_MODE) << 16, mtime, data)

  def add_symlink_entry(self, name: str, target: str, mtime: int = 0) -> None:
    return self._add_entry(name, (stat.S_IFLNK | self._SYMLINK_FILE_MODE) << 16, mtime, target)

  def add_dir_entry(self, name: str, mtime: int = 0) -> None:
    if not name.endswith("/"):
      name += "/"
    external_attr = (stat.S_IFDIR | self._DEFAULT_DIR_MODE) << 16
    external_attr |= 0x10  # MS-DOS directory flag
    return self._add_entry(name, external_attr, mtime, b"")

  def _add_entry(self, name: str, external_attr: int, mtime: int, data: Union[bytes, str]) -> None:
    info = ZipInfo(name, self._prepare_zipinfo_date_time(mtime))
    info.external_attr = external_attr
    self._set_zipinfo_compression(info)
    self._inner.writestr(info, data)

  def add_real_file(
    self,
    path: str,
    archived_path: str,
    recursive: bool = True,
    predicate: Optional[ArchiveAdapter.FileFilter] = None,
    mtime: Optional[float] = None,
  ) -> None:
    info = ZipInfo.from_file(path, archived_path, strict_timestamps=False)
    self._set_zipinfo_compression(info)
    if mtime is None:
      mtime = os.stat(path).st_mtime
    info.date_time = self._prepare_zipinfo_date_time(mtime)

    if predicate is not None and not predicate(info.filename):
      return

    if info.is_dir():
      self._inner.open(info, "w").close()
      if recursive:
        for f in sorted(os.listdir(path)):
          self.add_real_file(
            os.path.join(path, f),
            os.path.join(archived_path, f),
            recursive=recursive,
            predicate=predicate,
          )
    else:
      with open(path, "rb") as src, self._inner.open(info, "w") as dest:
        shutil.copyfileobj(src, dest, 1024 * 8)

  def _set_zipinfo_compression(self, zipinfo: ZipInfo) -> None:
    inner_any: Any = self._inner
    zipinfo_any: Any = zipinfo
    zipinfo_any.compress_type = inner_any.compression
    zipinfo_any._compresslevel = inner_any.compresslevel

  def _prepare_zipinfo_date_time(self, timestamp: float) -> Tuple[int, int, int, int, int, int]:
    # Apparently, the `ZipInfo.from_file` function of the standard library uses
    # `time.localtime` by default, thus making the archive not reproducible if
    # the system timezone is changed.
    date_time: Tuple[int, ...] = time.gmtime(timestamp)[0:6]

    # The following code was copied from the `zipfile` module due to the lack
    # of a better option.
    inner_any: Any = self._inner
    strict_timestamps: bool = inner_any._strict_timestamps
    if not strict_timestamps:
      if date_time[0] < 1980:
        date_time = (1980, 1, 1, 0, 0, 0)
      elif date_time[0] > 2107:
        date_time = (2107, 12, 31, 23, 59, 59)

    if date_time[0] < 1980:
      raise ValueError("ZIP does not support timestamps before 1980")

    return date_time
