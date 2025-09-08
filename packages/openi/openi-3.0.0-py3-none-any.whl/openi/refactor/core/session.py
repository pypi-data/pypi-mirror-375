import asyncio
import logging
from dataclasses import dataclass
from pprint import pprint
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from openi.refactor.constants import MAX_WORKERS
from openi.refactor.plugins.errors import RequestConnectionError, RequestError

logger = logging.getLogger(__name__)


class OpeniSession:
    def __init__(self, endpoint: str, token: Optional[str] = None):
        self.token = token
        self.endpoint = endpoint.rstrip("/")
        self.base_url = f"{self.endpoint}/api/v1"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(10.0, read=30.0, write=30.0),
            limits=httpx.Limits(
                max_connections=MAX_WORKERS,  # 全局最大连接数
                max_keepalive_connections=MAX_WORKERS,  # 保持连接池
            ),
        )

    async def stream(self, path: str, **kwargs) -> AsyncGenerator[bytes, None]:
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            async with self.client.stream("GET", path, follow_redirects=True, headers=headers, **kwargs) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error: {e}")
            raise RequestError(f"HTTP error: {e}", server_msg=e.response.text, status_code=e.response.status_code)
        except httpx.HTTPError as e:
            logger.error(f"HTTP ConnectTimeout error: {e}")
            raise RequestConnectionError(f"HTTP ConnectTimeout {e}")
        except Exception as e:
            logger.error(f"HTTP error: {e}")
            raise e

    async def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        if self.token and method != "PUT":
            headers["Authorization"] = f"Bearer {self.token}"
        log_response = kwargs.pop("log_response", False)
        try:
            response = await self.client.request(method, path, headers=headers, **kwargs)
            response.raise_for_status()
            if log_response:
                logger.info(f"Respond: {response.status_code} {path} {response.text}")
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RequestError(f"HTTP error: {e}", server_msg=response.text, status_code=response.status_code)
        except httpx.ConnectTimeout as e:
            logger.error(f"HTTP ConnectTimeout error: {e}")
            raise RequestConnectionError(f"HTTP ConnectTimeout {e}")
        except Exception as e:
            logger.error(f"HTTP error: {e}")
            raise e

    async def get(self, path: str, **kwargs) -> httpx.Response:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> httpx.Response:
        return await self.request("PUT", path, **kwargs)

    async def _stream(self, path: str, **kwargs) -> httpx.Response:
        return await self.request("GET", path, follow_redirects=True, **kwargs)

    async def close(self):
        await self.client.aclose()


class SyncWrapper:
    """将 async 接口同步封装（主要用于 API 层调用）"""

    def __init__(self, session: OpeniSession):
        self.session = session

    def get(self, path: str, **kwargs) -> httpx.Response:
        return asyncio.run(self.session.get(path, **kwargs))

    def post(self, path: str, **kwargs) -> httpx.Response:
        return asyncio.run(self.session.post(path, **kwargs))

    def put(self, path: str, **kwargs) -> httpx.Response:
        return asyncio.run(self.session.put(path, **kwargs))
