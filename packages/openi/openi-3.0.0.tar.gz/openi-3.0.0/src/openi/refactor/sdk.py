import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List, Literal, Union

from openi.refactor.constants import DARK_GREY_TEXT, DEFAULT_MAX_WORKERS, RED, RESET
from openi.refactor.service.downloader import DownloadArgs, DownloadService
from openi.refactor.service.notification import notice_serivce
from openi.refactor.service.uploader import UploadArgs, UploadService

logger = logging.getLogger(__name__)


def openi_download_file(
    repo_id: str,
    repo_type: Literal["dataset", "model"] = "dataset",
    filename: Union[str, List[str], None] = None,
    local_dir: Union[str, Path, None] = None,
    force: bool = False,
    max_workers: int = DEFAULT_MAX_WORKERS,
    endpoint: Union[str, None] = None,
    token: Union[str, None] = None,
) -> None:
    """
    Download a file from OpenI platform.
    :param repo_id: The ID of the repository.
    :param repo_type: The type of the repository, either "dataset" or "model".
    :param filename: The name of the file to download. If None, all files will be downloaded.
    :param local_dir: The local directory where the file will be saved.
    :param force: If True, will overwrite existing cached files.
    :param max_workers: The maximum number of concurrent workers for downloading.
    :param endpoint: The API endpoint to use. If None, the default endpoint will be used.
    :param token: The authentication token for the OpenI platform.
    """

    user_args = DownloadArgs(
        subject_name=repo_id,
        subject_type=1 if repo_type == "dataset" else 2,
        file_name=filename,
        local_dir=local_dir,
        force=force,
        max_workers=max_workers,
        endpoint=endpoint,
        token=token,
    )
    service = DownloadService(user_args)
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        logger.warning("Download interrupted by user.")
        print(f"{RED}✗ 下载已被用户中断。{RESET}")
        sys.exit(130)


def openi_upload_file(
    repo_id: str,
    file_or_folder_path: Union[str, List[str], Path],
    upload_name: Union[str, None] = None,
    repo_type: Literal["dataset", "model"] = "dataset",
    max_workers: int = DEFAULT_MAX_WORKERS,
    endpoint: Union[str, None] = None,
    token: Union[str, None] = None,
):
    """
    Upload a file or folder to OpenI platform.
    :param repo_id: The ID of the repository.
    :param file_or_folder_path: The path to the file or folder to upload.
    :param upload_name: The name to use for the uploaded file or folder. If None, the original name will be used.
    :param repo_type: The type of the repository, either "dataset" or "model".
    :param max_workers: The maximum number of concurrent workers for uploading.
    :param endpoint: The API endpoint to use. If None, the default endpoint will be used.
    :param token: The authentication token for the OpenI platform.
    """

    user_args = UploadArgs(
        subject_name=repo_id,
        subject_type=1 if repo_type == "dataset" else 2,
        file_or_folder_path=file_or_folder_path,
        max_workers=max_workers,
        upload_name=upload_name,
        endpoint=endpoint,
        token=token,
    )
    service = UploadService(user_args)
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        logger.warning("Upload interrupted by user.")
        print(f"{RED}✗ 上传已被用户中断。{RESET}")
        sys.exit(130)


def download_zipall(
    repo_id: str,
    repo_type: Literal["dataset", "model"] = "dataset",
    local_dir: Union[str, Path] = os.getcwd(),
    force: bool = False,
    endpoint: Union[str, None] = None,
    token: Union[str, None] = None,
):
    pass


def openi_upload_folder(
    repo_id: str,
    folder_path: Union[str, Path],
    repo_type: Literal["dataset", "model"] = "dataset",
    max_workers: int = DEFAULT_MAX_WORKERS,
    endpoint: Union[str, None] = None,
    token: Union[str, None] = None,
):
    """
    Upload a folder to OpenI platform.
    """
    pass


def notice(off: Union[bool, None] = None):
    """
    print the lastest notice from OpenI platform.
    :param off: If True or False, will not print the notice. And turn off/on the notice service.
               If None, will not change the settings, but will print the notice.
    """
    notice_serivce(off=off)
