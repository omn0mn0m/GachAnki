from __future__ import annotations

from typing import Union, overload

from degeneranki.vendor.typing_extensions import Literal

from degeneranki.vendor.storage3._async import AsyncStorageClient
from degeneranki.vendor.storage3._sync import SyncStorageClient
from degeneranki.vendor.storage3.constants import DEFAULT_TIMEOUT
from degeneranki.vendor.storage3.utils import __version__

__all__ = ["create_client", "__version__"]


@overload
def create_client(
    url: str, headers: dict[str, str], *, is_async: Literal[True]
) -> AsyncStorageClient:
    ...


@overload
def create_client(
    url: str, headers: dict[str, str], *, is_async: Literal[False]
) -> SyncStorageClient:
    ...


def create_client(
    url: str, headers: dict[str, str], *, is_async: bool, timeout: int = DEFAULT_TIMEOUT
) -> Union[AsyncStorageClient, SyncStorageClient]:
    if is_async:
        return AsyncStorageClient(url, headers, timeout)
    else:
        return SyncStorageClient(url, headers, timeout)
