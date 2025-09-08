import logging
from argparse import SUPPRESS, Namespace, _SubParsersAction
from pathlib import Path
from typing import List, Optional, Union

from openi.commands import BaseOpeniCLICommand
from openi.refactor.constants import DEFAULT_MAX_WORKERS, DEFAULT_SAVE_PATH
from openi.refactor.plugins.errors import OpeniError
from openi.refactor.sdk import openi_download_file, openi_upload_file

logger = logging.getLogger(__name__)


class DatasetCommands(BaseOpeniCLICommand):
    @staticmethod
    def register_subcommand(parser: _SubParsersAction):
        """
        dataset command
        """
        parser_dataset = parser.add_parser(
            "dataset",
            help="{upload,download} 上传/下载启智AI协作平台的数据集",
            description="上传/下载启智AI协作平台的数据集",
            aliases=["d"],
        )
        parser_dataset._action_groups.pop()
        subparsers_dataset = parser_dataset.add_subparsers(
            title="commands",
            dest="commands",
        )
        subparsers_dataset.required = True

        # Add subcommand
        DownloadCommand.register_subcommand(subparsers_dataset)
        UploadCommand.register_subcommand(subparsers_dataset)


class BaseDatasetCommand:
    def __init__(self, args):
        self.args = args


class DownloadCommand(BaseDatasetCommand):
    @staticmethod
    def register_subcommand(subparsers_dataset):
        """
        download subcommand
        """
        download_parser = subparsers_dataset.add_parser(
            "download",
            help="下载数据集, openi dataset download -h 查看更多说明",
            # usage="openi dataset download REPO_ID FILENAME [--cluster CLUSTER] [--save_path PATH] [--force]",
            description="下载数据集，须提供数据集完整名称，下载公开数据集无需登录",
        )
        download_parser._action_groups.pop()

        """
        arguments
        """
        download_parser_args = download_parser.add_argument_group("arguments")
        download_parser_args.add_argument(
            "repo_id",
            help="数据集完整名称，格式为`拥有者/数据集名`",
        )

        """
        optional arguments
        """
        download_parser_optional_args = download_parser.add_argument_group("optional arguments")
        download_parser_optional_args.add_argument(
            "-f",
            "--filename",
            dest="filename",
            metavar="FILENAME",
            default=None,
            required=False,
            help="选填: 指定下载数据集中的`单个文件`或`多个文件`（使用逗号隔开），不填写此参数则会下载整个数据集",
        )
        download_parser_optional_args.add_argument(
            "-d",
            "--local_dir",
            dest="local_dir",
            metavar="LOCAL_DIR",
            default=None,
            required=False,
            help="选填: 指定本地的保存目录，不填写默认在当前路径创建数据集名称目录",
        )
        download_parser_optional_args.add_argument(
            "-w",
            "--max_workers",
            dest="max_workers",
            metavar="MAX_WORKERS",
            default=DEFAULT_MAX_WORKERS,
            required=False,
            help=f"选填: 并行下载的最大文件数，不填写默认为{DEFAULT_MAX_WORKERS}",
        )
        download_parser_optional_args.add_argument(
            "--force",
            dest="force",
            action="store_true",
            required=False,
            help="选填: 不使用此参数时，若本地已存在同名文件则会跳过下载；\n填入该参数时会强制下载，并加上数字后缀以避免覆盖本地文件",
        )
        download_parser_optional_args.add_argument(
            "--token",
            dest="token",
            required=False,
            help=SUPPRESS,
        )
        download_parser_optional_args.add_argument(
            "--endpoint",
            dest="endpoint",
            required=False,
            help=SUPPRESS,
        )
        download_parser.set_defaults(func=lambda args: DownloadCommand(args))

    def __init__(self, args: Namespace) -> None:
        self.repo_id: str = args.repo_id
        self.filename: Union[str, None] = args.filename

        self.local_dir: Union[str, Path] = args.local_dir
        self.force: bool = args.force
        self.max_workers: int = int(args.max_workers)

        self.token: Optional[str] = args.token
        self.endpoint: Optional[str] = args.endpoint

    def run(self):
        openi_download_file(
            repo_id=self.repo_id,
            repo_type="dataset",
            filename=self.filename,
            local_dir=self.local_dir,
            force=self.force,
            max_workers=self.max_workers,
            token=self.token,
            endpoint=self.endpoint,
        )


class UploadCommand(BaseDatasetCommand):
    @staticmethod
    def register_subcommand(subparsers_dataset):
        """
        upload subcommand
        """
        upload_parser = subparsers_dataset.add_parser(
            "upload",
            help="上传数据集, openi dataset upload -h 查看更多说明",
            # usage="openi dataset upload REPO_ID FILE_PATH",
            description="上传数据集，须提供数据集完整名称，用户需要有上传权限",
        )
        upload_parser._action_groups.pop()

        """
        arguments
        """
        upload_parser_args = upload_parser.add_argument_group("arguments")
        upload_parser_args.add_argument(
            "repo_id",
            help="数据集完整名称，格式为`拥有者/数据集名`",
        )
        upload_parser_args.add_argument(
            "file_or_folder_path",
            help="待上传文件的本地路径，可填入`单个文件`或`文件夹`；填入文件夹时，上传将会保留内部子目录结构及所有文件，但不会包含根目录",
        )

        """
        optional arguments
        """
        upload_parser_optional_args = upload_parser.add_argument_group("optional arguments")
        upload_parser_optional_args.add_argument(
            "-n",
            "--upload_name",
            dest="upload_name",
            metavar="UPLOAD_NAME",
            required=False,
            help="选填: 设置文件上传后的存储路径及文件名。例如填入 `test/image.jpg` 文件将保存在数据集内的 `test` 子目录下。\n上传文件夹时此设置无效。",
            # help="选填: 设置文件上传后在数据集内的文件名，可用此参数添加上传后的子目录；\n需填入上传后在数据集内部的完整名称，如`test/image.jpg`。\n上传文件夹时此参数无效",
        )
        upload_parser_optional_args.add_argument(
            "-w",
            "--max_workers",
            dest="max_workers",
            metavar="MAX_WORKERS",
            default=DEFAULT_MAX_WORKERS,
            required=False,
            help=f"选填: 并行上传时的最大文件数，不填写默认为{DEFAULT_MAX_WORKERS}",
        )
        upload_parser_optional_args.add_argument(
            "--token",
            dest="token",
            required=False,
            help=SUPPRESS,
        )
        upload_parser_optional_args.add_argument(
            "--endpoint",
            dest="endpoint",
            required=False,
            help=SUPPRESS,
        )
        upload_parser.set_defaults(func=lambda args: UploadCommand(args))

    def __init__(self, args: Namespace) -> None:
        self.repo_id: str = args.repo_id
        self.file_or_folder_path: str = args.file_or_folder_path
        self.upload_name: Union[str, None] = args.upload_name
        self.max_workers: int = int(args.max_workers)
        self.token: Optional[str] = args.token
        self.endpoint: Optional[str] = args.endpoint

    def run(self):
        openi_upload_file(
            repo_id=self.repo_id,
            file_or_folder_path=self.file_or_folder_path,
            upload_name=self.upload_name,
            repo_type="dataset",
            max_workers=self.max_workers,
            token=self.token,
            endpoint=self.endpoint,
        )
