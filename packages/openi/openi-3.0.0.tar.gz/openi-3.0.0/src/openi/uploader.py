import logging
from pathlib import Path
from typing import List, Literal, Optional, Union

from openi.refactor.constants import MAX_FILE_SIZE
from openi.refactor.service.notification import get_global_notice_off, notice_serivce
from openi.refactor.utils.deprecate import deprecated

from ._exceptions import (
    DatasetNotFound,
    EmptyFolderError,
    FileSizeError,
    FileTypeError,
    KeyboardInterruptError,
    LocalDirNotFound,
    LocalPathNotFound,
    ModelNotFoundError,
    OpenIError,
    ServerFileExistsError,
    UnauthorizedError,
    UploadError,
    validate_openi_args,
)
from ._file import UploadFile, check_zip_integrity, get_file_size, get_local_dir_files, is_zip, zip_local_dir
from ._tqdm import FileProgressBar, create_pbar
from .api import OpenIApi
from .utils import convert_bytes

logger = logging.getLogger(__name__)


def upload_with_tqdm(
    api: OpenIApi,
    dataset_or_model_id: str,
    local_file: UploadFile,
    upload_name: str,
    upload_mode: Literal["dataset", "model"],
    upload_type: int = 1,
    pbar: Optional[FileProgressBar] = None,
) -> Optional[Union[BaseException, OpenIError]]:
    """
    Uploads a file to OpenI API using tqdm for progress tracking.
    """
    err: Optional[Union[BaseException, OpenIError]] = None

    if not pbar:
        pbar = create_pbar(display_name=upload_name, size=local_file.size)

    try:
        pbar.uploading()

        for progress in api.upload_file_iterator(
            filepath=local_file.path,
            dataset_or_model_id=dataset_or_model_id,
            file_md5=local_file.md5,
            file_size=local_file.size,
            total_chunks_count=local_file.total_chunks_count,
            upload_mode=upload_mode,
            upload_name=upload_name,
            upload_type=upload_type,
            chunk_size=local_file.chunk_size,
        ):
            pbar.update(progress)

        if pbar.n == local_file.size:
            pbar.completed()

    except KeyboardInterrupt:
        pbar.failed()
        err = KeyboardInterruptError(
            "上传未完成，部分内容已保存到云端; 再次上传时，文件将会被断点续传",
        )

    except ServerFileExistsError as e:
        pbar.skipped(f"{local_file.name} 该文件已上传")
        err = e

    except Exception as e:
        pbar.failed()
        err = e

    finally:
        pbar.refresh()
        pbar.close()

    return err


@deprecated("数据集已改版，请使用 `openi_upload_file()` 替代，部分参数有变化。")
@validate_openi_args
def upload_file(
    repo_id: str,
    file: Union[Path, str],
    token: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> str:
    """Uploads a file to the specified repository.

    Args:
        file (Union[Path, str]): The file to upload.
        repo_id (str): The repository ID to upload to.
        token (Optional[str], optional): The OpenI API token. Defaults to None.
        endpoint (Optional[str], optional): The OpenI API endpoint. Defaults to None.

    Returns:
        str: The URL of the uploaded file.
    """
    api = OpenIApi(token=token, endpoint=endpoint)

    if api.get_repo_access_right(repo_id=repo_id) != "write":
        raise UnauthorizedError()

    dataset = api.get_dataset_info(repo_id=repo_id)
    if not dataset:
        raise DatasetNotFound(
            repo_id=repo_id,
            dataset_url=api.get_dataset_url(repo_id),
        )

    path = Path(file) if isinstance(file, str) else file
    if not path.exists():
        raise LocalPathNotFound(path)

    if path.name.find(" ") != -1:
        if path.is_dir():
            raise UploadError(
                f"`{path}` 文件夹打包失败。数据集文件不允许有空格，请修改文件夹名称后重新尝试上传",
            )
        else:
            raise UploadError(
                f"`{path.name}` 数据集文件不允许有空格，请修改文件名后重新尝试上传",
            )

    file_size = get_file_size(path)
    if not api.check_storage_quota(file_size):
        raise UploadError("本次上传文件总大小已超出存储配额，请先删除已有数据集文件或模型")

    if path.is_dir():
        try:
            zip_path = zip_local_dir(local_dir=path)
        except FileExistsError:
            zip_path = path.with_suffix(".zip")
            raise UploadError(
                f"`{zip_path}` 压缩文件已存在，无法重复打包。请直接上传压缩文件",
            )
        except FileNotFoundError:
            raise EmptyFolderError(path)
    else:
        if not is_zip(path):
            raise FileTypeError(path)
        zip_path = path
        err = check_zip_integrity(file_path=zip_path)
        if err:
            raise OpenIError(f"{file} 不是合法的压缩包文件，校验失败：{err}")

    local_file: UploadFile = UploadFile(path=zip_path)
    if local_file.size > MAX_FILE_SIZE:
        raise FileSizeError(
            f"文件大小 {convert_bytes(local_file.size)} 超过限制, " f"单次上传最大支持 {convert_bytes(MAX_FILE_SIZE)}",
        )
    logger.info(local_file)

    err = upload_with_tqdm(
        api=api,
        dataset_or_model_id=dataset.id,
        local_file=local_file,
        upload_name=local_file.name,
        upload_mode="dataset",
    )

    if path.is_dir():
        zip_path.unlink(missing_ok=True)

    api.close()

    if err is not None:
        raise err

    url = api.get_dataset_url(repo_id=repo_id)
    # print(f"文件成功上传到：{url}")

    return url


@validate_openi_args
def upload_model_file(
    repo_id: str,
    model_name: str,
    file: Union[Path, str],
    upload_name: Optional[str] = None,
    token: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> str:
    """Uploads a model file to the specified repository.

    Args:
        file (Union[Path, str]): The file to upload.
        repo_id (str): The repository ID to upload to.
        model_name (str): The model name to upload to.
        upload_name (Optional[str], optional): The name of the uploaded file. Defaults to None.
        token (Optional[str], optional): The OpenI API token. Defaults to None.
        endpoint (Optional[str], optional): The OpenI API endpoint. Defaults to None.

    Returns:
        str: The URL of the uploaded file.
    """
    api = OpenIApi(token=token, endpoint=endpoint)
    if not get_global_notice_off():
        notice_serivce()

    aimodel = api.get_model_info(repo_id=repo_id, model_name=model_name)
    if not aimodel:
        raise ModelNotFoundError(
            model_name=model_name,
            model_list_url=api.get_repo_models_url(repo_id=repo_id),
        )
    if not aimodel.isCanOper:
        raise UnauthorizedError()
    if aimodel.modelType != 1:
        raise UploadError(
            f"模型类型不正确，只能上传本地导入的模型",
        )

    local_file: UploadFile = UploadFile(path=file)
    upload_name = local_file.name if not upload_name else upload_name.lstrip("/")

    if not local_file.exists():
        raise LocalPathNotFound(local_file.path)

    if local_file.size > MAX_FILE_SIZE:
        raise FileSizeError(
            f"文件大小 {convert_bytes(local_file.size)} 超过限制, " f"单次上传最大支持 {convert_bytes(MAX_FILE_SIZE)}",
        )

    file_size = get_file_size(local_file.path)
    if not api.check_storage_quota(file_size):
        raise UploadError("本次上传文件总大小已超出存储配额，请先删除已有数据集文件或模型")

    err = upload_with_tqdm(
        api=api,
        dataset_or_model_id=aimodel.id,
        local_file=local_file,
        upload_name=upload_name,
        upload_mode="model",
    )

    api.close()

    if err is not None:
        raise err

    url = api.get_model_url(repo_id=repo_id, model_name=model_name)
    print(f"文件成功上传到：{url}")

    return url


@validate_openi_args
def upload_model(
    repo_id: str,
    model_name: str,
    folder: Union[Path, str],
    token: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> Optional[str]:
    """Uploads entire model to the specified repository.

    Args:
        folder (Union[Path, str]): The folder containing the model files.
        repo_id (str): The repository ID to upload to.
        model_name (str): The model name to upload to.
        token (Optional[str], optional): The OpenI API token. Defaults to None.
        endpoint (Optional[str], optional): The OpenI API endpoint. Defaults to None.

    Returns:
        Optional[str]: The URL of the uploaded model.
    """
    api = OpenIApi(token=token, endpoint=endpoint)
    if not get_global_notice_off():
        notice_serivce()

    aimodel = api.get_model_info(repo_id=repo_id, model_name=model_name)
    if not aimodel:
        raise ModelNotFoundError(
            model_name=model_name,
            model_list_url=api.get_repo_models_url(repo_id=repo_id),
        )
    if not aimodel.isCanOper:
        raise UnauthorizedError()
    if aimodel.modelType != 1:
        raise UploadError(
            f"模型类型不正确，只能上传本地导入的模型",
        )

    local_dir = folder
    if not isinstance(local_dir, Path):
        local_dir = Path(local_dir).absolute()

    if not local_dir.is_dir():
        raise LocalDirNotFound(local_dir)

    file_size = get_file_size(local_dir)
    if not api.check_storage_quota(file_size):
        raise UploadError("本次上传文件总大小已超出存储配额，请先删除已有数据集文件或模型")

    filepath_list: List[Path] = get_local_dir_files(local_dir=local_dir)
    if not filepath_list:
        raise EmptyFolderError(local_dir)
    filepath_list.sort(key=lambda file: file.stat().st_size)

    completed_count = 0
    raise_err: Optional[Union[BaseException, OpenIError]] = None
    for filepath in filepath_list:
        upload_name = filepath.relative_to(local_dir).as_posix()
        local_file: UploadFile = UploadFile(path=filepath, name=upload_name)

        err = upload_with_tqdm(
            api=api,
            dataset_or_model_id=aimodel.id,
            local_file=local_file,
            upload_name=local_file.name,
            upload_mode="model",
        )
        if not isinstance(err, ServerFileExistsError):
            raise_err = err
        if isinstance(err, KeyboardInterruptError):
            api.close()
            raise err
        else:
            completed_count += 1

    api.close()

    if completed_count == len(filepath_list):
        url = api.get_model_url(repo_id=repo_id, model_name=model_name)
        print(f"模型上传成功：{url}")
        return url
    else:
        print(f"\n{raise_err}; 模型上传出错，请重新上载")
        return None
