import asyncio
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
from urllib.parse import urlencode

from openi.refactor.core.auth import OpeniAuth, set_basic_auth
from openi.refactor.core.dataclass import (
    UploadCompleteDirectArgs,
    UploadDirectArgs,
    UploadGetChunksArgs,
    UploadGetMultipartUrlArgs,
    UploadNewMultipartArgs,
)
from openi.refactor.core.session import OpeniSession, SyncWrapper
from openi.refactor.plugins.errors import UploadError

logger = logging.getLogger(__name__)


class OpeniRouter:
    def __init__(self, endpoint: Optional[str] = None, token: Optional[str] = None):
        self.auth: OpeniAuth = set_basic_auth(endpoint=endpoint, token=token)
        self._async = OpeniSession(endpoint=self.auth.endpoint, token=self.auth.token)
        self._sync = SyncWrapper(self._async)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        await self._async.close()

    async def notification(self):
        resp = await self._async.get("/sdk/notification", log_response=True)
        return resp.json()

    def auth_user_info_sync(self) -> Dict[str, Any]:
        resp = self._sync.get("/user")
        return resp.json()

    async def auth_user_info(self) -> Dict[str, Any]:
        resp = await self._async.get("/user", log_response=True)
        return resp.json()

    async def user_info(self, username: str) -> Dict[str, Any]:
        resp = await self._async.get(f"/users/{username}")
        return resp.json()

    async def repo_info(self, subject_name: str) -> Dict[str, Any]:
        resp = await self._async.get(f"/repos/{subject_name}", log_response=True)
        return resp.json()

    """
    Dataset APIs
    """

    async def dataset_query(self, subject_name: str) -> Dict[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok",
            "data": {
                "id": "xxxx",
                "name": "testDataset04",
                "tags": [
                    "tag1",
                    "tag2"
                ],
                "licenses": "MIT2.0",
                "tasks": [
                    "NLP"
                ],
                "is_private": true,
                "use_count": 0,
                "download_count": 0,
                "num_stars": 1,
                "created_unix": 1749520932,
                "updated_unix": 1749799093,
                "size": 134198,
                "owner_name": "xxxx",
                "is_collected": true,
                "can_edit_file": true,
                "can_manage": true,
                "can_download": true,
                "Owner": {
                    "ID": 1,
                    "LowerName": "xxxx",
                    "Name": "xxxxx",
                    "FullName": "",
                    "Email": "xxxx@136.com",
                    "Language": "zh-CN",
                    "Description": "dasdsa",
                    "RelAvatarLink": "/user/avatar/xxxx/-1?xxxx",
                    "NumMembers": 0,
                    "IsOrganization": false,
                    "CreatedUnix": 1645178182,
                    "UpdatedUnix": 1750056077
                }
            }
        }
        """
        params = {
            "dataset_name": subject_name,
        }
        resp = await self._async.get("/dataset", params=params, log_response=True)
        return resp.json()

    async def dataset_meta(self, subject_name: str) -> Dict[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok",
            "data": {
                "ContentLength": 134198,
                "ContentType": "application/zip"
            }
        }
        """
        params = {
            "dataset_name": subject_name,
        }
        resp = await self._async.get("/download/meta", params=params)
        return resp.json()

    async def dataset_file_meta(self, subject_name: str, file_name: str) -> Tuple[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok",
            "data": {
                "ContentLength": 27,
                "ContentType": "binary/octet-stream"
            }
        }
        """
        params = {
            "dataset_name": subject_name,
            "file_name": file_name,
            "parent_dir": "",
        }
        resp = await self._async.get("/dataset/file/meta", params=params)
        return (file_name, resp.json())

    async def dataset_filelist(self, subject_name: str, parent_dir: str = "", marker: str = None) -> Dict[str, Any]:
        params = {
            "dataset_name": subject_name,
            "parent_dir": parent_dir,
            "page_size": "",
            "marker": marker,
        }
        resp = await self._async.get("/dataset/files", params=params)
        return resp.json()

    async def dataset_download_file_stream(
        self,
        subject_name: str,
        file_name: str,
        cache_size: int = 0,
    ) -> AsyncGenerator[bytes, None]:
        params = {
            "dataset_name": subject_name,
            "file_name": file_name,
            "parent_dir": "",
        }
        headers = {"Range": f"bytes={cache_size}-"} if cache_size > 0 else {}
        async for chunk in self._async.stream("/dataset/file", params=params, headers=headers):
            yield chunk

    async def dataset_download_zipall_stream(self, subject_name: str) -> AsyncGenerator[bytes, None]:
        params = {
            "dataset_name": subject_name,
        }
        async for chunk in self._async.stream("/dataset/download", params=params):
            yield chunk

    """
    Upload APIs
    """

    async def async_put_with_url(self, url: str, **kwargs) -> Optional[str]:
        resp = await self._async.put(url, **kwargs)
        return resp.headers.get("ETag", None)

    async def storage_summary(self, subject_id: str, subject_type: str) -> dict:
        """
        {
            "storage_limit":0,
            "dataset_used_storage":0,
            "model_used_storage":0,
            "used_storage":0,
            "remaining_storage":0
        }
        """
        params = {
            "subject_id": subject_id,
            "subject_type": subject_type,
        }
        resp = await self._async.get("/storage/summary", params=params, log_response=True)
        return resp.json()

    async def upload_get_direct_url(self, params: UploadDirectArgs) -> Dict[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok",
            "data": {
                "url": "xxxx"
            }
        }
        """
        resp = await self._async.get("/upload/direct/get_upload_url", params=asdict(params))
        if not resp.json() or resp.json().get("code", 99) == 99:
            logger.error(f"code 99 error with /direct/get_upload_url: {resp.text}")
            raise UploadError(f"Failed with /direct/get_upload_url, server message: {resp.text}")
        return resp.json()

    async def upload_complete_direct(self, json_body: UploadCompleteDirectArgs) -> Dict[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok"
        }
        """
        params = asdict(json_body)
        file_name_list = params.pop("file_name_list", [])
        json_body = dict(file_name_list=file_name_list)
        resp = await self._async.post(
            "/upload/direct/complete_upload", params=params, json=json_body, log_response=True
        )
        return resp.json()

    async def upload_get_chunks(self, params: UploadGetChunksArgs) -> Dict[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok",
            "data": {
                "uuid": "xxxx",
                "uploaded": 0,
                "chunks": [],
                "subjectId": "xxxx",
                "fileName": "xxxx.txt"
            }
        }
        """
        resp = await self._async.get("/upload/get_chunks", params=asdict(params), log_response=True)
        if not resp.json() or resp.json().get("code", 99) == 99:
            logger.error(f"code 99 error with /get_chunks: {resp.text}")
            raise UploadError(f"Failed with /get_chunks, server message: {resp.text}")
        return resp.json()

    async def upload_new_multipart(self, params: UploadNewMultipartArgs) -> Dict[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok",
            "data": {
                "uuid": "xxxx"
            }
        }
        """
        resp = await self._async.get("/upload/new_multipart", params=asdict(params), log_response=True)
        if not resp.json() or resp.json().get("code", 99) == 99:
            logger.error(f"code 99 error with /new_multipart: {resp.text}")
            raise UploadError(f"Failed with /new_multipart, server message: {resp.text}")
        return resp.json()

    async def upload_get_multipart_url(self, params: UploadGetMultipartUrlArgs) -> Dict[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok",
            "data": {
                "url": "xxxx"
            }
        }
        """
        resp = await self._async.get("/upload/get_multipart_url", params=asdict(params), log_response=True)
        if not resp.json() or resp.json().get("code", 99) == 99:
            logger.error(f"code 99 error with /get_multipart_url: {resp.text}")
            raise UploadError(f"Failed with /get_multipart_url, server message: {resp.text}")
        return resp.json()

    async def upload_complete_multipart(self, uuid: str) -> Dict[str, Any]:
        """
        {
            "code": 0,
            "msg": "ok"
        }
        """
        params = {
            "uuid": uuid,
        }
        resp = await self._async.post("/upload/complete_multipart", params=dict(uuid=uuid), log_response=True)
        return resp.json()


import asyncio
from pprint import pprint
from typing import Any, Dict, List

from openi.refactor.core.auth import OpeniAuth, set_basic_auth


async def test():
    async with OpeniRouter() as client:
        print(client.auth)
        auth_user = await client.auth_user_info()
        pprint(auth_user)

        print("\033[1;31mAPI RESULT:\033[0m")
        # result = await client.auth_user_info()
        # pprint(result)
        async for c in client.dataset_download_file_stream(
            subject_name="xxxx/xxxx",
            file_name="xxxxz",
            cache_size=0,
        ):
            print(c)


if __name__ == "__main__":
    asyncio.run(test())
