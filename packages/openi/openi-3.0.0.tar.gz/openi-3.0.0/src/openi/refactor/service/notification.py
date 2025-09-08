import asyncio
import json
import logging
import os
from pprint import pprint
from typing import Any, Dict, List, Union

from openi.refactor.constants import BOLD, DARK_GREY_TEXT, DIM, GREEN, MAGENTA, RESET, TOKEN_FILE_PATH, YELLOW
from openi.refactor.core.router import OpeniRouter

logger = logging.getLogger(__name__)


def notice_serivce(off: Union[bool, None] = None):
    if isinstance(off, bool):
        set_global_notice(off)
        if off:
            print(f"{DARK_GREY_TEXT}{BOLD}全局通知已关闭。{RESET}")
        else:
            print(f"{DARK_GREY_TEXT}{BOLD}全局通知已开启。{RESET}")
        return

    else:
        asyncio.run(print_notification())


async def print_notification(client: Union[OpeniRouter, None] = None) -> None:
    if not client:
        client = OpeniRouter()

    messages_raw = await client.notification()
    messages = messages_raw.get("messages", [])
    if not messages:
        return

    for m in messages:
        print_notify_message(m.get("msg", ""), level=m.get("level", "info"))

    print(f"{DIM}* 你可以使用 openi notice --off 命令，或者 openi.notice(off=True) 函数关闭此全局通知。{RESET}\n")


def print_notify_message(msg: str, level: str = "info") -> None:
    if level == "notify":
        print(f"{GREEN}{msg}{RESET}")

    if level == "info":
        print(f"{MAGENTA}{msg}{RESET}")

    if level == "warning":
        print(f"{YELLOW}{msg}{RESET}")


def get_global_notice_off() -> bool:
    """
    Get the global notice setting from the local token file.
    """
    try:
        config = json.loads(TOKEN_FILE_PATH.read_text())
        return config.get("global_notice_off", False)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("(FileNotFoundError, json.JSONDecodeError) for token file, return `global_notice_off=False`.")
        return False
    except Exception as e:
        logger.error(f"An error occurred while reading the token file: {e}")
        return False


def set_global_notice(off: bool) -> None:
    """
    Set the global notice setting in the local token file.
    """
    try:
        config = json.loads(TOKEN_FILE_PATH.read_text())
        config["global_notice_off"] = off
        TOKEN_FILE_PATH.write_text(json.dumps(config, indent=4))
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("(FileNotFoundError, json.JSONDecodeError) for token file, creating new token file.")
        config = {"global_notice_off": off}
        TOKEN_FILE_PATH.write_text(json.dumps(config, indent=4))
    except Exception as e:
        logger.error(f"An error occurred while updating the token file: {e}")
