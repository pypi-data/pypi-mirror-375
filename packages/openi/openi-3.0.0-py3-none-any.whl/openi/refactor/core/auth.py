import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from openi.refactor.constants import DEFAULT_ENDPOINT, TOKEN_FILE_PATH


@dataclass
class OpeniAuth:
    endpoint: str
    token: Optional[str] = None


def read_local_auth() -> Optional[dict]:
    """
    Load saved `token.json` on local machine
    """
    auth_filepath = TOKEN_FILE_PATH or Path.home() / ".openi" / "token.json"
    try:
        return json.loads(auth_filepath.read_text())

    except FileNotFoundError:
        # logger.error(f"No token file found at `{TOKEN_FILE_PATH}`.")
        return None

    except json.decoder.JSONDecodeError:
        # logger.error(f"Invalid JSON format at `{TOKEN_FILE_PATH}`.")
        return None

    except Exception as e:
        # logger.error(f"Unknown Error: {repr(e)}")
        raise None


def set_basic_auth(endpoint: Optional[str] = None, token: Optional[str] = None) -> OpeniAuth:
    """Set the credentials for Basic Auth on the session object
    Priority:
        1. provided arguments
        2. local saved token.json
        3. environment variables
    """
    # get from saved token file
    token_saved, endpoint_saved = None, None
    saved_auth = read_local_auth()
    if saved_auth:
        token_saved = saved_auth.get("token", None)
        endpoint_saved = saved_auth.get("endpoint", None)

    # get from environment variables
    token_env = os.getenv("OPENI_TOKEN", None)
    endpoint_env = os.getenv("OPENI_ENDPOINT", None)

    return OpeniAuth(
        token=token or token_saved or token_env,
        endpoint=endpoint or endpoint_saved or endpoint_env or DEFAULT_ENDPOINT,
    )
