import asyncio
import gc
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from pprint import pprint
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple, Union

from openi.refactor.constants import (
    BOLD,
    DARK_GREY_TEXT,
    DIM,
    ELLIPSIS,
    FAILED_FILES_LOG_DIR,
    FILE_BATCH_SIZE,
    GREEN,
    ITALIC,
    MAX_TASK_BAR_DISPLAY,
    MAX_WORKERS,
    OVERALL_TITLE,
    RED,
    RESET,
    YELLOW,
)
from openi.refactor.core.router import OpeniRouter
from openi.refactor.plugins.errors import OpeniError, OpeniWarning, RequestError
from openi.refactor.plugins.progress import ProgressBarSession, ProgressBarTask
from openi.refactor.service.file_manager import CacheFile, export_failed_files, save_file_stream_iterator
from openi.refactor.service.notification import get_global_notice_off, print_notification
from openi.refactor.service.validators import run_user_args_validators
from openi.refactor.utils.utils import batched

logger = logging.getLogger(__name__)


@dataclass
class DownloadArgs:
    subject_name: str
    subject_type: int
    file_name: Union[str, List[str], None]
    local_dir: Union[str, Path, None]
    force: bool
    max_workers: int
    endpoint: Union[str, None]
    token: Union[str, None]

    def __post_init__(self):
        self.subject_type = 1
        self.max_workers = max(1, min(self.max_workers, MAX_WORKERS))

        if isinstance(self.file_name, str):
            names = self.file_name.split(",")
            if len(names) > 1:
                self.file_name = [name.strip() for name in names if name.strip()]

        if not self.local_dir:
            subject_real_name = self.subject_name.split("/")[-1]
            self.local_dir = Path.cwd() / subject_real_name
        if isinstance(self.local_dir, str):
            self.local_dir = Path(self.local_dir)
        os.makedirs(self.local_dir, exist_ok=True)

    def display(self) -> None:
        print(self)
        for arg in self.__dict__.values():
            print(f"type: {type(arg)}, value: {arg}")


class DownloadService:
    def __init__(self, user_args: DownloadArgs):
        self.client = OpeniRouter(endpoint=user_args.endpoint, token=user_args.token)
        self.user_args: DownloadArgs = user_args
        self.file_info_list: List[CacheFile] = []
        self.file_warning_list: List[str] = []
        self.failed_filenames: List[str] = []
        self.success_filenames: List[str] = []

    async def run(self) -> None:
        try:
            if not get_global_notice_off():
                await print_notification()

            # validate user args
            await run_user_args_validators(asdict(self.user_args))

            # check auth
            await self.check_auth()

            # set_file_list
            await self.set_file_list()

            # submit
            summary: List[ProgressBarTask] = await self.submit_download_progress()
            for s in summary:
                if s.error:
                    # self.failed_filenames.append(s.desc)
                    print(s.error)
                    logger.error(f"Failed download for {s.desc}: {s.error}")

        except Exception as e:
            logger.error(f"DownloadService run failed: {str(e)}")
            raise e from None

        finally:
            total_count = len(self.file_info_list)
            success_count = len(self.success_filenames)
            failed_count = total_count - success_count

            if failed_count > 0:
                print(
                    f"共下载 {len(self.file_info_list)} 个文件，成功: {GREEN}{success_count}{RESET}, 失败: {RED}{failed_count}{RESET}"
                )
                success_set = set(self.success_filenames)
                self.failed_filenames = [
                    file_obj.name for file_obj in self.file_info_list if file_obj.name not in success_set
                ]
                if failed_count <= 10:
                    print(f"{ITALIC}{DIM}失败文件: {', '.join(self.failed_filenames)}")
                else:
                    try:
                        file_path = await export_failed_files(
                            local_dir=FAILED_FILES_LOG_DIR,
                            mode="download",
                            repo_name=self.user_args.subject_name,
                            repo_type="dataset" if self.user_args.subject_type == 1 else "model",
                            failed=self.failed_filenames,
                        )
                        print(f"{ITALIC}{DIM}查看完整失败文件列表: {file_path}{RESET}")
                    except Exception as e:
                        logger.error(f"Unable to export failed files: {e}")
                        print(e)

            await self.client.close()

    async def check_auth(self) -> None:
        try:
            subject_info = await self.client.dataset_query(self.user_args.subject_name)
            if not subject_info:
                raise OpeniError("Response is empty. Chekc the log for more details.")

            resp_code = subject_info.get("code", -1)
            if resp_code == 9004:
                raise OpeniError(subject_info.get("msg", "Repo not found")) from None
            if resp_code != 0:
                raise OpeniError(f"Failed to query repo: {subject_info}")

            # can_download = subject_info.get("data", {}).get("can_download", False)
            # if not can_download:
            #     raise OpeniError(
            #         f"User does not have permission to download files from repo {self.user_args.subject_name}."
            #     )

            subject_id = subject_info.get("data", {}).get("id", None)
            if not subject_id:
                raise OpeniError(f"repo uuid is None.") from None
            self.subject_id = subject_id

        except Exception as e:
            raise e from None

    async def exclude_existed_files(self, file_list: List[CacheFile]) -> Tuple[List[CacheFile], List[CacheFile]]:
        """
        Exclude files that already exist in the local directory.
        :param file_list: List of CacheFile objects to check.
        :return: Filtered list of CacheFile objects that do not exist locally.
        """
        existed, not_exist = [], []
        for file_obj in file_list:
            if not Path(file_obj.file_path).exists() or self.user_args.force:
                not_exist.append(file_obj)
            else:
                existed.append(file_obj)
        return existed, not_exist

    async def set_file_list(self) -> None:
        """
        2种情况：
        a)传入单个或多个文件名, str, list[str]
        b)不传入,None,下载整个数据集或模型
        """
        file_list: List[CacheFile] = []
        filenames = self.user_args.file_name
        print(f"{ITALIC}`{self.user_args.subject_name}` 获取文件列表中{ELLIPSIS}{ELLIPSIS}")

        if not filenames:
            file_list_resp = await list_all_files(
                client=self.client,
                subject_name=self.user_args.subject_name,
            )
            file_list = [
                CacheFile(
                    name=item["FileName"],
                    size=item["Size"],
                    local_dir=self.user_args.local_dir,
                )
                for item in file_list_resp
            ]

        if isinstance(filenames, (str, list)):
            if isinstance(filenames, str):
                filenames = filenames.split(",")
            file_list_resp: List[Dict[str, Any]] = await asyncio.gather(
                *[
                    self.client.dataset_file_meta(subject_name=self.user_args.subject_name, file_name=f)
                    for f in filenames
                ]
            )
            for t in file_list_resp:
                name: str = t[0]
                resp: dict = t[1]
                if resp.get("code") == 0:
                    file_info = resp.get("data", {})
                    file_list.append(
                        CacheFile(
                            name=name,
                            size=file_info.get("ContentLength", 0),
                            local_dir=self.user_args.local_dir,
                        )
                    )

        print(f"- {ITALIC}云端共找到 {YELLOW}{len(file_list)}{RESET} {ITALIC}个文件。")
        if not file_list:
            raise OpeniError(
                f"No files found for repo `{self.user_args.subject_name}` with file name(s) `{self.user_args.file_name}`."
            )

        self.file_warning_list, self.file_info_list = await self.exclude_existed_files(file_list)
        if self.file_warning_list:
            print(
                f"- {ITALIC}本地已存在 {YELLOW}{len(self.file_warning_list)}{RESET} {ITALIC}个文件。若要强制下载，请添加 `force=True` 或 `--force` 参数。"
            )
        if len(self.file_info_list):
            print(f"- {ITALIC}开始下载 {YELLOW}{len(self.file_info_list)}{RESET} {ITALIC}个文件{ELLIPSIS}{ELLIPSIS}")

        print(f"- 本地保存目录 {DIM}{self.user_args.local_dir.absolute().as_posix()}{RESET}")

    async def save_file_stream(self, file_obj: CacheFile) -> AsyncGenerator[int, Any]:
        try:
            # # 如果文件已存在且不强制下载，则返回
            # file_path = Path(file_obj.file_path)
            # if file_path.exists() and not self.user_args.force:
            #     file_size = file_path.stat().st_size
            #     if file_size == file_obj.size:
            #         yield file_size
            #         self.file_warning_list.append(file_obj.name)
            #         return

            if self.user_args.force:
                await file_obj.delete_cache_file()

            # total_size = file_obj.size
            cache_size = max(0, file_obj.cache_size)
            save_path = Path(file_obj.cache_path)
            if save_path.exists() and save_path.is_file():
                yield save_path.stat().st_size

            async for chunk_size in save_file_stream_iterator(
                save_path=save_path,
                file_stream=self.client.dataset_download_file_stream,
                file_stream_kwargs=dict(
                    subject_name=self.user_args.subject_name,
                    file_name=file_obj.name,
                    cache_size=cache_size,
                ),
            ):
                yield chunk_size
                # if total_size > 0:
                #     total_size -= chunk_size

            # yield total_size  # Yield remaining size if not fully downloaded, it's ok if it's 0, for download_zipall

            completed = await file_obj.as_completed()
            if not completed:
                raise OpeniError(
                    f"`{file_obj.name}` Failed to complete download. Please use `--force` to delete cache files and retry downloading."
                )

            self.success_filenames.append(file_obj.name)

        except Exception as e:
            raise e  # raise OpeniError(f"Failed to save file {save_path}: {e}")

    async def submit_download_progress(self) -> List[ProgressBarTask]:
        session: ProgressBarSession = ProgressBarSession()
        total = len(self.file_info_list)
        total_bytes = sum(file_obj.size for file_obj in self.file_info_list)
        if total > 1:
            session.enable_overall_progress(
                total_tasks=total,
                overall_desc=OVERALL_TITLE,
                max_workers=self.user_args.max_workers,
                total_bytes=total_bytes,
            )
        max_workers = self.user_args.max_workers
        run_task_func = session.run_task_without_bar if total >= MAX_TASK_BAR_DISPLAY else session.run_task

        summary: List[ProgressBarTask] = []
        with session:
            semaphore = asyncio.Semaphore(max_workers)
            for batch in batched(self.file_info_list, FILE_BATCH_SIZE):
                batched_tasks: List[ProgressBarTask] = [
                    ProgressBarTask(
                        desc=file_obj.name,
                        total=file_obj.size,
                        initial=0,
                        iter_func=self.save_file_stream,
                        iter_args=dict(file_obj=file_obj),
                    )
                    for file_obj in list(batch)
                ]

                async def run_task_with_semaphore(task: ProgressBarTask):
                    async with semaphore:
                        return await run_task_func(task)

                try:
                    await asyncio.gather(*(run_task_with_semaphore(t) for t in batched_tasks))
                except Exception as e:
                    raise e
                gc.collect()  # 强制垃圾回收，清理任务的内存占用

            summary = session.get_tasks_summary()

        return summary


from typing import Any, Dict, List


async def list_all_files(client, subject_name: str, parent_dir: str = "", marker: str = None) -> List[Dict[str, Any]]:
    """
    Recursively list all files in a dataset directory, handling pagination.
    """
    all_files = []

    while True:
        # 调用文件列表接口，传递 marker 参数（如果有）
        if marker:
            raw_file_list = await client.dataset_filelist(
                subject_name=subject_name, parent_dir=parent_dir, marker=marker
            )
        else:
            raw_file_list = await client.dataset_filelist(subject_name=subject_name, parent_dir=parent_dir)
        # print(f"Raw file list: {raw_file_list}")

        file_list = raw_file_list.get("data", {}).get("file_list", [])
        for item in file_list:
            file_name = item["FileName"]
            is_dir = item["IsDir"]

            # 拼接完整路径（注意：根目录不要加斜杠）
            full_path = f"{parent_dir}/{file_name}" if parent_dir else file_name

            if is_dir:
                # 递归查找子目录
                sub_files = await list_all_files(client, subject_name, parent_dir=full_path)
                all_files.extend(sub_files)
            else:
                # 修改 FileName 为完整路径
                item["FileName"] = full_path
                all_files.append(item)

        # 检查是否还有下一页
        has_next = raw_file_list.get("data", {}).get("has_next", False)
        marker = raw_file_list.get("data", {}).get("marker", None)
        if not has_next or not marker:
            break

    return all_files


if __name__ == "__main__":
    pass
