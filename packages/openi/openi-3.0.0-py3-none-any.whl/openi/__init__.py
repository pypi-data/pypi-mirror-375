import asyncio
import os
import sys

from openi._login import login, logout, whoami
from openi.refactor.constants import BOLD, DIM, RESET
from openi.refactor.core import OpeniRouter
from openi.refactor.plugins.log import setup_logging
from openi.refactor.sdk import notice, openi_download_file, openi_upload_file

from .downloader import download_file, download_model, download_model_file
from .uploader import upload_file, upload_model, upload_model_file

setup_logging()

# if windows machine, do not set uvloop
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    try:
        import uvloop
    except ImportError:
        import subprocess

        print(f"{DIM}Module {BOLD}`uvloop`{RESET} {DIM}undetected, installing...{RESET}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-qq", "uvloop"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
