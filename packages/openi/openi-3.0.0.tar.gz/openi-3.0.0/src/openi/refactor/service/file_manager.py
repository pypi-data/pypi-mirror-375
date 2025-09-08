import hashlib
import json
import logging
import math
import mimetypes
import os
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Iterator, List, Literal, Optional, Tuple, Union
from zipfile import ZipFile

import aiofiles

from openi.refactor.constants import AI_MODEL_VERSION_FILE, CHUNK_SIZE, FILE_CACHE_PREFIX
from openi.refactor.plugins.errors import OpeniError

logger = logging.getLogger(__name__)


class UploadFile:
    """
    file object for upload
    """

    def __init__(self, path: Union[str, Path], name: Optional[str] = None, chunk_size: int = CHUNK_SIZE):
        if isinstance(path, str):
            path = Path(path).absolute()

        self.path = path
        self.name: str = name if name else path.name
        self.chunk_size = chunk_size

        """
        fill in when uploading process starts
        """
        self.total_chunks_count: int = 0
        self.md5: str = ""
        self.file_type_for_api: str = ""

        self.upload_uuid: str = ""
        self.uploaded: bool = False
        self.uploaded_chunks: List[int] = []
        self.start_from_chunk: int = 1
        self.completed_size: int = 0

        self.etags: List[str] = []

    def __repr__(self):
        return_str: str = "UploadFile("
        for attr in self.__dict__:
            return_str += f"{attr}={getattr(self, attr)}, "
        return_str = return_str.rstrip(", ") + ")"
        return return_str

    def exists(self) -> bool:
        if self.path.exists() and self.path.is_file():
            return True
        else:
            return False

    def is_zip(self) -> bool:
        suffixes = "".join(self.path.suffixes)
        return ".zip" in suffixes or ".tar.gz" in suffixes

    @property
    def size(self) -> int:
        return self.path.stat().st_size

    async def prepare(self) -> None:
        try:
            self.total_chunks_count = await get_file_total_chunks_count(self.path, self.chunk_size)
            self.file_type_for_api = await get_file_type_for_api(self.path)
        except Exception as e:
            logger.error(f"Error preparing file {self.name}: {e}")
            raise OpeniError(f"Error preparing file {self.name}: {e}")


async def get_file_type_for_api(file_path: Union[str, Path]) -> Optional[str]:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type


async def get_file_md5(file_path: Union[str, Path], chunk_size: int = CHUNK_SIZE) -> str:
    # upload_mode: Literal["model", "dataset"],
    m = hashlib.md5()
    async with aiofiles.open(file_path, "rb") as f:
        while True:
            data = await f.read(chunk_size)
            if not data:
                break
            md5_data = data[: 1024 * 1024]  # if upload_mode == "dataset" else data
            m.update(md5_data)
    return m.hexdigest()


async def get_file_total_chunks_count(file_path: Union[str, Path], chunk_size: int = CHUNK_SIZE) -> int:
    file_size = file_path.stat().st_size
    if file_size == 0:
        return 1
    return math.ceil(file_size / chunk_size)


async def remove_parent_dir(file_path: Union[str, Path], parent_dir_cut: Union[str, Path]) -> str:
    if isinstance(file_path, str):
        file_path = Path(file_path).absolute()

    if isinstance(parent_dir_cut, str):
        parent_dir_cut = Path(parent_dir_cut).absolute()

    # remove the parent directory from the file path
    if parent_dir_cut in file_path.parents:
        return file_path.relative_to(parent_dir_cut).as_posix()
    else:
        return file_path.as_posix()


EXCLUED_FILES = {".DS_Store", "Thumbs.db", ".git", ".gitignore", AI_MODEL_VERSION_FILE}


async def get_local_dir_files(local_dir: Path) -> List[Path]:
    """
    Returns a list of filepath in given directory.
    """
    return [file for file in local_dir.rglob("*") if file.is_file() and file.name not in EXCLUED_FILES]


async def read_complete_file(file_path: Union[str, Path]) -> bytes:
    """
    Read the complete file content.

    Args:
        file_path (Union[str, Path]): local file path

    Returns:
        bytes: file content
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    async with aiofiles.open(file_path, "rb") as f_reader:
        return await f_reader.read()


async def read_file_chunk_iterator(
    file_path: Union[str, Path],
    chunk_size: int = CHUNK_SIZE,
    start_from_chunk: int = 1,
) -> AsyncGenerator[Tuple[int, bytes], None]:
    """
    Iterate over file chunks data.

    Args:
        filepath (Union[str, Path]): local file path
        chunk_size (int, optional): chunk size.
        start_from_chunk (int, optional): start from chunk. Defaults to 1.

    Yields:
        Tuple[int, bytes]: chunk number and chunk data
    """

    if isinstance(file_path, str):
        file_path = Path(file_path)

    if file_path.stat().st_size == 0:
        yield 1, b""

    chunk_number = start_from_chunk

    async with aiofiles.open(file_path, "rb") as f_reader:
        await f_reader.seek((start_from_chunk - 1) * chunk_size)
        while True:
            chunk_data = await f_reader.read(chunk_size)
            if not chunk_data:
                break

            yield chunk_number, chunk_data

            chunk_number += 1


class CacheFile:
    """
    file object for download
    """

    def __init__(
        self,
        name: Union[Path, str],
        size: int,
        local_dir: Union[Path, str],
        force: bool = False,
    ):
        self.name = name
        self.size = size
        self.local_dir = local_dir
        self.force = force

        self.file_path = os.path.join(local_dir, name)

        real_name = Path(name).name
        sub_dir = Path(name).parent.as_posix()
        cache_file = os.path.join(sub_dir, f"{FILE_CACHE_PREFIX}{real_name}")
        self.cache_path = os.path.join(local_dir, cache_file)

        # if force:
        #     self.force_download()

        # if not self.cache_path.exists():
        #     self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        #     self.cache_path.touch(exist_ok=True)

    def __repr__(self):
        return_str: str = "CacheFile("
        for attr in self.__dict__:
            return_str += f"{attr}={getattr(self, attr)}, "
        return_str = return_str.rstrip(", ") + ")"
        return return_str

    @property
    def cache_size(self) -> int:
        if not Path(self.cache_path).exists():
            return 0

        return Path(self.cache_path).stat().st_size

    async def as_completed(self, rename_existing: bool = True) -> bool:
        try:
            if self.cache_size != self.size:
                logger.error(f"{self.file_path}, size mismatch, cache file not completed")
                return False

            if rename_existing and Path(self.file_path).exists():
                self.file_path = await rename_existing_file(self.file_path)

            Path(self.cache_path).rename(self.file_path)
            return True

        except Exception as e:
            logger.error(f"Error completing cache file {self.name}: {e}")
            raise OpeniError(f"Error completing cache file {self.name}: {e}")

    async def delete_cache_file(self) -> None:
        # self.file_path.unlink(missing_ok=True)
        Path(self.cache_path).unlink(missing_ok=True)


async def save_file_stream_iterator(
    save_path: Union[str, Path],
    file_stream: AsyncGenerator[bytes, None],
    file_stream_kwargs: dict = {},
) -> AsyncGenerator[int, None]:
    """
    Write file stream to disk.

    Args:
        save_path (Union[str, Path]): The path to save the file.
        file_stream (AsyncGenerator[bytes, None]): The stream of bytes to write.
        file_stream_kwargs (dict): Additional arguments for the stream. Defaults to None.

    Yields:
        AsyncGenerator[int, None]: The number of bytes written.
    """
    if isinstance(save_path, str):
        save_path = Path(save_path).absolute()
    save_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(save_path, "ab") as f:
        async for chunk in file_stream(**file_stream_kwargs):
            await f.write(chunk)
            yield len(chunk)


async def rename_existing_file(filepath: Union[str, Path]) -> str:
    """Renames a file by adding a digital suffix in case of conflicts.

    Args:
        filepath (Path): The path to the file to rename.

    Returns:
        Path: The new path of the renamed file.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath).absolute()

    stem, suffix = filepath.stem, filepath.suffix

    # special handling for '.tar.gz' files
    if suffix == ".gz" and ".tar" in stem:
        stem = Path(stem).stem
        suffix = ".tar.gz"

    i = 1
    new_filepath = filepath
    while new_filepath.exists():
        new_filepath = filepath.with_name(f"{stem}({i}){suffix}")
        i += 1

    return new_filepath.as_posix()


async def export_failed_files(local_dir: str, mode: str, repo_name: str, repo_type: str, failed: List[str]) -> str:
    await delete_failed_files_log(Path(local_dir), dayspan=7)

    repo_name = repo_name.replace("/", "_")
    file_name = f"openi--failed--{repo_type}--{mode}--{repo_name}--{datetime.today().strftime('%y%m%d%H%M%S')}"
    file_path = Path(local_dir) / Path(file_name)
    if not file_path.exists():
        file_path.touch()
    content = ", ".join(failed)
    async with aiofiles.open(file_path, "w") as f:
        await f.write(content)

    return file_path.as_posix()


async def delete_failed_files_log(local_dir: str, dayspan: int = 7) -> None:
    """
    Delete failed files log older than date_span days.
    """
    if not local_dir.exists():
        return

    now = datetime.now()
    for file in local_dir.iterdir():
        if file.is_file():
            file_date = datetime.fromtimestamp(file.stat().st_mtime)
            if (now - file_date).days > dayspan:
                file.unlink(missing_ok=True)


"""
unused functions, but kept for reference
"""


def is_file(filepath: Path) -> bool:
    return filepath.is_file()


def is_dir(filepath: Path) -> bool:
    return filepath.is_dir()


def is_zip(filepath: Path) -> bool:
    suffixes = "".join(filepath.suffixes)
    return ".zip" in suffixes or ".tar.gz" in suffixes


def get_folder_size(local_dir: Union[str, Path]) -> int:
    return sum(f.stat().st_size for f in local_dir.rglob("*") if f.is_file())


def file_chunk_by_part(
    filepath: Path,
    part_number: int,
    chunk_size: int = CHUNK_SIZE,
) -> bytes:
    file_size = filepath.stat().st_size

    start = 0 or (part_number - 1) * chunk_size
    end = min(part_number * chunk_size, file_size)
    if start >= end or part_number == 0:
        return b""

    with open(filepath, "rb") as f_reader:
        f_reader.seek(start)
        return f_reader.read(end - start)


def split_subdir_name(filename: str) -> Tuple[str, str]:
    """
    Split the filename into subdirectory and name.

    Args:
        filename (str): The name of the file.

    Returns:
        Tuple[str, str]: The subdirectory and the name of the file.
    """
    as_path = Path(filename.lstrip("/"))
    return as_path.parent.as_posix(), as_path.name


def zip_local_dir(local_dir: Path) -> Path:
    """
    Zip the given directory.
    """

    zip_path = local_dir.with_suffix(".zip")
    if zip_path.exists():
        raise FileExistsError(zip_path)

    if not any(local_dir.iterdir()):
        raise FileNotFoundError(local_dir)

    with ZipFile(zip_path, "w") as zipper:
        for file in local_dir.rglob("*"):
            if file.is_file():
                zipper.write(file, file.relative_to(local_dir))

    return zip_path


# def check_zip_integrity(zip_filepath: Union[str, Path]) -> Optional[str]:
#     if isinstance(zip_filepath, Path):
#         zip_filepath = zip_filepath.as_posix()

#     try:
#         with zipfile.ZipFile(zip_filepath, "r") as zip_ref:
#             zip_ref.testzip()
#         return None
#     except zipfile.BadZipfile as e:
#         return repr(e)
#     except Exception as e:
#         return repr(e)


def check_zip_integrity(file_path: Union[str, Path]) -> Optional[str]:
    if isinstance(file_path, Path):
        file_path = file_path.as_posix()

    try:
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.testzip()
            return None
        elif tarfile.is_tarfile(file_path):
            with tarfile.open(file_path, "r:*") as tar_ref:
                tar_ref.getmembers()
            return None
        else:
            raise ValueError(f"{file_path} is not a valid archive file.")
    except (Exception, zipfile.BadZipfile, tarfile.TarError) as e:
        return repr(e)


if __name__ == "__main__":
    # Example usage
    test_path = Path("~/Downloads/test.py")

    import asyncio

    result = asyncio.run(get_file_type_for_api(test_path))
    print(result)
