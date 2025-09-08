import asyncio
import gc
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from pprint import pprint
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from openi.refactor.constants import (
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
from openi.refactor.core.dataclass import (
    UploadCompleteDirectArgs,
    UploadDirectArgs,
    UploadGetChunksArgs,
    UploadGetMultipartUrlArgs,
    UploadNewMultipartArgs,
)
from openi.refactor.core.router import OpeniRouter
from openi.refactor.plugins.errors import OpeniError, UploadError
from openi.refactor.plugins.progress import ProgressBarSession, ProgressBarTask, readable_bytes
from openi.refactor.service.file_manager import (
    UploadFile,
    export_failed_files,
    get_file_md5,
    get_local_dir_files,
    read_complete_file,
    read_file_chunk_iterator,
    remove_parent_dir,
)
from openi.refactor.service.notification import get_global_notice_off, print_notification
from openi.refactor.service.validators import run_user_args_validators, validate_storage_limit
from openi.refactor.utils.utils import batched

logger = logging.getLogger(__name__)


@dataclass
class UploadArgs:
    subject_name: str
    subject_type: int
    file_or_folder_path: Union[str, List[str], Path]
    max_workers: int
    upload_name: Union[str, None] = None
    endpoint: Union[str, None] = None
    token: Union[str, None] = None

    def __post_init__(self):
        self.subject_type = 1
        self.max_workers = max(1, min(self.max_workers, MAX_WORKERS))

        if isinstance(self.file_or_folder_path, str):
            names = self.file_or_folder_path.split(",")
            if len(names) > 1:
                self.file_or_folder_path = [name.strip() for name in names if name.strip()]

    def display(self) -> None:
        print(self)
        for arg in self.__dict__.values():
            print(f"type: {type(arg)}, value: {arg}")


class UploadService:
    def __init__(self, user_args: UploadArgs):
        self.client = OpeniRouter(endpoint=user_args.endpoint, token=user_args.token)
        self.user_args = user_args
        self.subject_id: str = ""
        self.file_info_list: List[UploadFile] = []
        self.failed_filenames: List[str] = []
        self.direct_filenames: List[str] = []  # for direct upload files
        self.success_filenames: List[str] = []  # for successful uploads

    async def run(self) -> None:
        try:
            # server noitification
            if not get_global_notice_off():
                await print_notification()

            # validate user args
            await run_user_args_validators(asdict(self.user_args))

            # check auth
            await self.check_auth()

            # set_file_lis
            await self.set_file_list()
            await self.check_storage()

            # submit
            summary: List[ProgressBarTask] = await self.submit_upload_progress()
            for s in summary:
                if s.error:
                    # self.failed_filenames.append(s.desc)
                    print(s.error)
                    logger.error(f"file failed for {s.desc}: {s.error}")

        except Exception as e:
            logger.error(f"UploadService run failed: {str(e)}")
            raise e from None

        finally:
            total_count = len(self.file_info_list)
            success_count = len(self.success_filenames)
            failed_count = total_count - success_count

            if failed_count > 0:
                print(f"共上传 {total_count} 个文件，成功: {GREEN}{success_count}{RESET}, 失败: {RED}{failed_count}{RESET}")
                success_set = set(self.success_filenames)
                self.failed_filenames = [
                    file_obj.name for file_obj in self.file_info_list if file_obj.name not in success_set
                ]
                if failed_count <= 10:
                    print(f"{ITALIC}{DIM}失败文件: {', '.join(self.failed_filenames)}{RESET}")
                else:
                    try:
                        file_path = await export_failed_files(
                            local_dir=FAILED_FILES_LOG_DIR,
                            mode="upload",
                            repo_name=self.user_args.subject_name,
                            repo_type="dataset" if self.user_args.subject_type == 1 else "model",
                            failed=self.failed_filenames,
                        )
                        print(f"{ITALIC}{DIM}查看完整失败文件列表: {file_path}{RESET}")
                        logger.info(f"Failed files exported to: {file_path}")
                    except Exception as e:
                        logger.error(f"Unable to export failed files: {e}")
                        print(e)

            await self._upload_direct_file_batch_complete()
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

            can_upload = subject_info.get("data", {}).get("can_edit_file", False)
            if not can_upload:
                raise OpeniError(
                    f"User does not have permission to upload files to repo {self.user_args.subject_name}."
                )

            subject_id = subject_info.get("data", {}).get("id", None)
            if not subject_id:
                raise OpeniError(f"repo uuid is None.") from None
            self.subject_id = subject_id

        except Exception as e:
            raise e from None

    async def set_file_list(self) -> None:
        print(f"{ITALIC}正在获取本地文件{ELLIPSIS}{ELLIPSIS} {RESET}")

        file_list: List[UploadFile] = []
        user_path_list = self.user_args.file_or_folder_path
        """
        1. str or Path, sinlge path,file or folder
        2. List[str], multiple paths
        """
        if isinstance(user_path_list, (str, Path)):
            user_path_list = [user_path_list]

        for user_path in user_path_list:
            user_path = Path(user_path)

            if not user_path.exists():
                raise OpeniError(f"File or folder {user_path} does not exist.")

            if user_path.is_file():
                file_list.append(
                    UploadFile(
                        name=self.user_args.upload_name or user_path.name,
                        path=user_path,
                    )
                )

            if user_path.is_dir():
                file_paths = await get_local_dir_files(user_path)
                if not file_paths:
                    raise OpeniError(f"Directory {user_path} is empty.")
                file_list = [
                    UploadFile(
                        name=await remove_parent_dir(file_path, user_path),
                        path=file_path,
                    )
                    for file_path in file_paths
                ]
        # pprint(file_list)
        print(
            f"{ITALIC}本地共找到 {YELLOW}{len(file_list)}{RESET} {ITALIC}个文件。开始上传 `{self.user_args.subject_name}` {ELLIPSIS}{ELLIPSIS}"
        )
        self.file_info_list = file_list

    async def check_storage(self) -> None:
        owner_name = self.user_args.subject_name.split("/")[0]
        total_size = sum(file_obj.size for file_obj in self.file_info_list)
        logger.info(f"Total size of files to upload: {total_size} bytes")

        summary = await self.client.storage_summary(
            subject_id=self.subject_id, subject_type=self.user_args.subject_type
        )
        remains: int = summary.get("remaining_storage", 0)
        limit: int = summary.get("storage_limit", 0)

        if remains < total_size and limit != -1:
            raise UploadError(
                f"剩余存储配额 {readable_bytes(remains)}，本地文件总大小 {readable_bytes(total_size)}，已超出存储配额，请查看 {owner_name} 用户的存储配额详情。"
            )

    async def upload_file_stream(self, file_obj: UploadFile) -> AsyncGenerator[int, Any]:
        try:
            await file_obj.prepare()
            _generator = self._upload_with_chunks if file_obj.total_chunks_count > 1 else self._upload_direct_file

            async for progress in _generator(file_obj):
                yield progress

            self.success_filenames.append(file_obj.name)  # 添加成功上传的文件名

        except Exception as e:
            # logger.error(f"upload_file_stream: {str(e)}")
            raise e

    async def _upload_direct_file(self, file_obj: UploadFile) -> AsyncGenerator[int, Any]:
        try:
            direct_upload_resp = await self.client.upload_get_direct_url(
                UploadDirectArgs(
                    file_name=file_obj.name,
                    subject_id=self.subject_id,
                    subject_type=self.user_args.subject_type,
                    file_type=file_obj.file_type_for_api,
                    size=file_obj.size,
                )
            )
            if not direct_upload_resp or direct_upload_resp.get("code", -1) != 0:
                raise OpeniError(f"Failed to get chunks for {file_obj.name}: {direct_upload_resp}")
            url = direct_upload_resp.get("data", {}).get("url", "")

            file_data = await read_complete_file(file_obj.path)
            etag = await self.client.async_put_with_url(url=url, data=file_data)
            if not etag:
                raise OpeniError(f"Failed to direct upload {file_obj.name}, size {file_obj.size} bytes.")

            yield file_obj.size  # 返回已上传的文件大小
            self.direct_filenames.append(file_obj.name)

        except Exception as e:
            # logger.error(f"_upload_direct_file: {str(e)}")
            raise e

    async def _upload_direct_file_batch_complete(self) -> None:
        try:
            # print(f"self.direct_filenames {','.join(self.direct_filenames)}")
            if not self.direct_filenames:
                return

            complete_resp = await self.client.upload_complete_direct(
                UploadCompleteDirectArgs(
                    file_name_list=self.direct_filenames,
                    subject_id=self.subject_id,
                    subject_type=self.user_args.subject_type,
                )
            )
            if not complete_resp or complete_resp.get("code", -1) != 0:
                logger.error(f"Failed to batch complete url for direct uploads: {self.direct_filenames}")
                raise OpeniError(f"Failed to batch complete url for direct uploads: {complete_resp}")

            self.direct_filenames = []  # 清空已完成的直接上传文件列表
        except Exception as e:
            # logger.error(f"_upload_direct_file_batch_complete: {str(e)}")
            raise e

    async def _upload_with_chunks(self, file_obj: UploadFile) -> AsyncGenerator[int, Any]:
        try:
            file_obj.md5 = await get_file_md5(file_obj.path, file_obj.chunk_size)
            get_chunks_resp = await self.client.upload_get_chunks(
                UploadGetChunksArgs(
                    subject_id=self.subject_id,
                    subject_type=self.user_args.subject_type,
                    file_name=file_obj.name,
                    md5=file_obj.md5,
                )
            )
            if not get_chunks_resp or get_chunks_resp.get("code", -1) != 0:
                raise OpeniError(f"Failed to get chunks for {file_obj.name}: {get_chunks_resp}")
            upoload_subject_id = get_chunks_resp.get("data", {}).get("subjectId", "")
            file_obj.upload_uuid = get_chunks_resp.get("data", {}).get("uuid", "")
            file_obj.uploaded_chunks = get_chunks_resp.get("data", {}).get("chunks", []) or []
            file_obj.uploaded = get_chunks_resp.get("data", {}).get("uploaded", 0)
            if file_obj.uploaded:
                yield file_obj.size
                return

            if not file_obj.upload_uuid:
                new_multipart_resp = await self.client.upload_new_multipart(
                    UploadNewMultipartArgs(
                        subject_id=self.subject_id,
                        subject_type=self.user_args.subject_type,
                        file_name=file_obj.name,
                        size=file_obj.size,
                        md5=file_obj.md5,
                        total_chunk_counts=file_obj.total_chunks_count,
                        file_type=file_obj.file_type_for_api,
                    )
                )
                if not new_multipart_resp or new_multipart_resp.get("code", -1) != 0:
                    raise OpeniError(f"Failed to create new multipart upload for {file_obj.name}: {new_multipart_resp}")
                file_obj.upload_uuid = new_multipart_resp.get("data", {}).get("uuid", "")

            file_obj.start_from_chunk = len(file_obj.uploaded_chunks) or 1
            file_obj.completed_size = file_obj.chunk_size * (file_obj.start_from_chunk - 1)

            yield file_obj.completed_size

            async for chunk_number, chunk_data in read_file_chunk_iterator(
                file_path=file_obj.path,
                chunk_size=file_obj.chunk_size,
                start_from_chunk=file_obj.start_from_chunk,
            ):
                get_multipart_url_resp = await self.client.upload_get_multipart_url(
                    UploadGetMultipartUrlArgs(
                        uuid=file_obj.upload_uuid,
                        chunk_number=chunk_number,
                        size=len(chunk_data),
                    )
                )
                if not get_multipart_url_resp or get_multipart_url_resp.get("code", -1) != 0:
                    raise OpeniError(f"Failed to get multipart URL for {file_obj.name}: {get_multipart_url_resp}")
                url = get_multipart_url_resp.get("data", {}).get("url", "")

                etag = await self.client.async_put_with_url(
                    url=url,
                    data=chunk_data,
                )
                if not etag:
                    raise OpeniError(f"Failed to upload chunk {chunk_number} for {file_obj.name}")

                yield len(chunk_data)
                file_obj.etags.append(etag)

            complete_resp = await self.client.upload_complete_multipart(file_obj.upload_uuid)
            if not complete_resp or complete_resp.get("code", -1) != 0:
                raise OpeniError(f"Failed to complete multipart upload for {file_obj.name}: {complete_resp}")

        except Exception as e:
            # logger.error(f"_upload_with_chunks: {str(e)}")
            raise e

    async def submit_upload_progress(self) -> List[ProgressBarTask]:
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

        # for log
        start_time = time.time()
        last_batch_time = start_time
        batch_count = 0
        logger.info(f"开始上传 {total} 个文件，最大并发数: {max_workers}")

        summary: List[ProgressBarTask] = []
        with session:
            semaphore = asyncio.Semaphore(max_workers)
            for batch in batched(self.file_info_list, FILE_BATCH_SIZE):
                # for log
                batch_count += 1
                current_time = time.time()
                total_elapsed = current_time - start_time
                batch_elapsed = current_time - last_batch_time
                logger.info(f"开始处理第 {batch_count} 批次，包含 {len(list(batch))} 个文件")
                logger.info(f"总运行时间: {total_elapsed:.2f}秒，距离上次批次: {batch_elapsed:.2f}秒")

                batched_tasks: List[ProgressBarTask] = [
                    ProgressBarTask(
                        desc=file_obj.name,
                        total=file_obj.size,
                        initial=file_obj.completed_size,
                        iter_func=self.upload_file_stream,
                        iter_args=dict(file_obj=file_obj),
                    )
                    for file_obj in list(batch)
                ]

                async def run_task_with_semaphore(task: ProgressBarTask):
                    async with semaphore:
                        try:
                            return await run_task_func(task)
                        except Exception as e:
                            # logger.error(f"run_task_with_semaphore: {str(e)}")
                            raise e

                try:
                    batch_start = time.time()
                    await asyncio.gather(*(run_task_with_semaphore(t) for t in batched_tasks), return_exceptions=False)

                except Exception as e:
                    logger.error(f"第 {batch_count} 批次处理失败: {str(e)}")
                    raise e

                finally:
                    await self._upload_direct_file_batch_complete()

                batch_end = time.time()
                batch_duration = batch_end - batch_start
                logger.info(f"第 {batch_count} 批次完成，耗时: {batch_duration:.2f}秒")

                last_batch_time = current_time
                gc.collect()  # 强制垃圾回收，清理上传任务的内存占用

            summary = session.get_tasks_summary()

        return summary
