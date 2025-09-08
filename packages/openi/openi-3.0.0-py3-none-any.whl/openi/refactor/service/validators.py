import asyncio
import re
from typing import Any, List

from openi.refactor.constants import REPO_ID_REGEX
from openi.refactor.core.router import OpeniRouter
from openi.refactor.plugins.errors import OpeniError


async def validate_storage_limit(size: int, subject_id: str, subject_type: str, client: OpeniRouter) -> dict:
    summary = await client.storage_summary(subject_id=subject_id, subject_type=subject_type)
    remains: int = summary.get("remaining_storage", 0)
    limit: int = summary.get("storage_limit", 0)
    # print(f"check_storage_quota(): {summary}")
    return remains > size or limit == -1


# validator 注册器
user_args_validators: List[callable] = []


def user_args_register_validator(func):
    user_args_validators.append(func)
    return func


@user_args_register_validator
async def validate_subject_name(ctx: dict) -> None:
    subject_name: str = ctx.get("subject_name", "")
    if not re.match(REPO_ID_REGEX, subject_name):
        raise OpeniError(f"Invalid repo_id: {subject_name}. Must match format of `username/reponame`.")


@user_args_register_validator
async def validate_subject_type(ctx: dict) -> None:
    subject_type: int = ctx.get("subject_type", 0)
    if subject_type not in [1, 2]:
        raise OpeniError(f"Invalid subject_type: {subject_type}. Must be dataset or model.")


async def run_user_args_validators(ctx: dict) -> None:
    tasks = [v(ctx) for v in user_args_validators]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    errors = [e for e in results if isinstance(e, Exception)]
    if errors:
        msg = "\n".join([str(e) for e in errors])
        raise OpeniError(f"Invalid user arguments. Please check the input parameters:\n{msg}")
