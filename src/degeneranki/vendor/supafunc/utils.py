from degeneranki.vendor.httpx import AsyncClient as AsyncClient  # noqa: F401
from degeneranki.vendor.httpx import Client as BaseClient

__version__ = "0.3.3"


class SyncClient(BaseClient):
    def aclose(self) -> None:
        self.close()
