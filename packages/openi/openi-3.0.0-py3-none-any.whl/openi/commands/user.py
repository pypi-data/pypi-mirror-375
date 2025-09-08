import logging
from argparse import _SubParsersAction

from openi.commands import BaseOpeniCLICommand
from openi.refactor.constants import DEFAULT_ENDPOINT
from openi.refactor.sdk import notice

from .._exceptions import UnauthorizedError
from .._login import login, logout, whoami
from openi.refactor.constants import RED, BOLD,RESET

logger = logging.getLogger(__name__)


class UserCommands(BaseOpeniCLICommand):
    @staticmethod
    def register_subcommand(parser: _SubParsersAction):
        login_parser = parser.add_parser(
            "login",
            usage="openi login [ token] [-e endpoint] [-h]",
            help="使用启智社区令牌登录并保存到本地",
            description="使用启智社区网页端生成的令牌登录: https://openi.pcl.ac.cn/user/settings/applications",
        )
        login_parser.add_argument(
            "-t",
            "--token",
            dest="token",
            metavar="",
            default=None,
            type=str,
            required=False,
            help="选填: 启智社区令牌，填写此参数将会跳过命令行输入",
        )
        login_parser.add_argument(
            "-e",
            "--endpoint",
            dest="endpoint",
            metavar="",
            default=DEFAULT_ENDPOINT,
            type=str,
            required=False,
            help="选填: 仅内部使用",  # "For internal distribution only",
        )
        login_parser.set_defaults(func=lambda args: LoginCommand(args))

        whoami_parser = parser.add_parser(
            "whoami",
            usage="openi whoami [-h]",
            help="查询当前登录用户",
            description="查询当前登录用户",
        )
        whoami_parser.set_defaults(func=lambda args: WhoamiCommand(args))

        logout_parser = parser.add_parser(
            "logout",
            usage="openi logout [-h]",
            help="退出登录并删除本地保存的令牌",
            description="退出登录并删除本地保存的令牌",
        )
        logout_parser.set_defaults(func=lambda args: LogoutCommand(args))

        notice_parser = parser.add_parser(
            "notice",
            usage="openi notice [-h]",
            help="查看平台最新公告",
            description="查看平台最新公告",
        )
        notice_parser.add_argument(
            "--off",
            dest="off",
            action="store_true",
            required=False,
            help=f"选填: {RED}{BOLD}关闭{RESET}全局通知",
        )
        notice_parser.add_argument(
            "--on",
            dest="on",
            action="store_true",
            required=False,
            help=f"选填: {RED}{BOLD}开启{RESET}全局通知，若同时传入--on和--off，则只有--off生效",
        )
        notice_parser.set_defaults(func=lambda args: NoticeCommand(args))


class BaseUserCommand:
    def __init__(self, args):
        self.args = args


class LoginCommand(BaseUserCommand):
    def run(self):
        login(token=self.args.token, endpoint=self.args.endpoint)


class LogoutCommand(BaseUserCommand):
    def run(self):
        logout()


class WhoamiCommand(BaseUserCommand):
    def run(self):
        try:
            _ = whoami()
        except UnauthorizedError:
            print("Not logged in")
            exit()


class NoticeCommand(BaseUserCommand):
    def run(self):
        # off=true，忽略on的值
        turn_off = self.args.off

        if not turn_off:
            if self.args.on:
                # off=false，on=true，开启通知
                turn_off = False
            else:
                # off=false，on=false，只打印
                turn_off = None
        notice(off=turn_off)
