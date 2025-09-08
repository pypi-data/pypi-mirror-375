import traceback
from typing import Optional

from openi.refactor.constants import BOLD, DARK_GREY_TEXT, DIM, GREEN, MAGENTA, RED, RESET, YELLOW


class OpeniError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"{RED}✗ {self.message}{RESET}"

    def __repr__(self):
        return f"{RED}✗ {self.message}{RESET}"


class OpeniWarning(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"{YELLOW}! {self.message}{RESET}"

    def __repr__(self):
        return f"{YELLOW}! {self.message}{RESET}"


class OpeniNotFoundError(OpeniError):
    def __init__(self, message: str):
        super().__init__(message)


class RequestError(Exception):
    """Custom exception for request errors."""

    def __init__(self, message: str, server_msg: Optional[str] = None, status_code: int = 500):
        if server_msg:
            message = f"{message}\n{RED}✗ Server Message: {server_msg}{RESET}"

        super().__init__(message)
        self.status_code = status_code


class RequestTimeoutError(RequestError):
    """Custom exception for request timeout errors."""

    def __init__(self, message: str = "Request timed out."):
        message = f"{RED}✗ {message}{RESET}"
        super().__init__(message)


class RequestConnectionError(RequestError):
    """Custom exception for connection errors."""

    def __init__(self, message: str = "Failed to connect to the server."):
        message = f"{RED}✗ {message}{RESET}"
        super().__init__(message)


class UploadError(RequestError):
    """Custom exception for rate limit errors."""

    def __init__(self, message: str):
        message = f"{RED}✗ {message}{RESET}"
        super().__init__(message)


def err2str(e: Exception) -> str:
    if isinstance(e, (OpeniError, OpeniWarning)):
        return str(e)

    return "".join(traceback.format_exception(type(e), e, e.__traceback__)).strip()
