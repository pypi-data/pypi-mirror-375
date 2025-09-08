from pathlib import Path
from typing import Literal

OPENI_LOGO_ASCII = """\n
         ██████╗   ██████╗  ███████╗  ███╗   ██╗  ██████╗
        ██╔═══██╗  ██╔══██╗ ██╔════╝  ████╗  ██║    ██╔═╝
        ██║   ██║  ██████╔╝ █████╗    ██╔██╗ ██║    ██║
        ██║   ██║  ██╔═══╝  ██╔══╝    ██║╚██╗██║    ██║
        ╚██████╔╝  ██║      ███████╗  ██║ ╚████║  ██████╗
         ╚═════╝   ╚═╝      ╚══════╝  ╚═╝  ╚═══╝  ╚═════╝\n
"""
CLI_DESCRIPTION = "         OpenI command line tool 启智AI协作平台命令行工具"

REPO_ID_REGEX = r"^[.a-zA-Z0-9_-]+/[.a-zA-Z0-9_-]+$"
REPO_INFO_REGEX = r"[\w\d]+/[\w\d]+"
TOKEN_REGEX = r"^[0-9a-z]{40}$"

DEFAULT_ENDPOINT = "https://openi.pcl.ac.cn"
AI_MODEL_VERSION_FILE = "openi_resource.version"
FILE_CACHE_PREFIX = ".openi--cache--"

HTTP_MAX_RETRIES: int = 3
HTTP_RETRY_DELAY: float = 1

# file storage
UPLOAD_TYPE = {"gpu": 0, "npu": 1}
CHUNK_SIZE = 1024 * 1024 * 64  # 64MB
MAX_FILE_SIZE = 1024 * 1024 * 1024 * 200  # 200GB
DOWNLOAD_RATES = 1024 * 1024 * 5

# api
OPENI_ROOT = Path.home() / ".openi"
if not OPENI_ROOT.exists():
    OPENI_ROOT.mkdir(parents=True)

TOKEN_FILE_PATH = Path(OPENI_ROOT) / "token.json"
if not TOKEN_FILE_PATH.exists():
    TOKEN_FILE_PATH.touch()

LOG_FILE_ROOT = Path(OPENI_ROOT) / "logs"
if not LOG_FILE_ROOT.exists():
    LOG_FILE_ROOT.mkdir(parents=True)

LOG_FILE = LOG_FILE_ROOT / "openi.log"
if not LOG_FILE.exists():
    LOG_FILE.touch()
LOG_LEVEL = "INFO"

FAILED_FILES_LOG_DIR = Path(OPENI_ROOT) / "failed--files"
if not FAILED_FILES_LOG_DIR.exists():
    FAILED_FILES_LOG_DIR.mkdir(parents=True)

DEFAULT_SAVE_PATH = Path.cwd()
if not DEFAULT_SAVE_PATH.exists():
    DEFAULT_SAVE_PATH.mkdir(parents=True)

UPLOAD_MODE = Literal["dataset", "model"]
UPLOAD_ENDPOINT = dict(dataset="/attachments", model="/attachments/model")
UPLOAD_ID_PARAM = dict(dataset="dataset_id", model="modeluuid")

ELLIPSIS = "…"
DESC_WIDTH = 25
DESC_PREFIX = f"({ELLIPSIS})"
OVERALL_TITLE = "已处理文件"
OVERALL_DESC = "{max_workers} workers | {desc}:"
FILE_BATCH_SIZE = 100
DEFAULT_MAX_WORKERS = 10
MAX_WORKERS = 100
MAX_TASK_BAR_DISPLAY = 200

"""
colored text
"""
MAGENTA = "\033[35m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
DARK_GREY_TEXT = "\033[90m"
RED = "\033[31m"
