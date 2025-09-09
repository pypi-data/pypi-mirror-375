import os

import msgspec

from ..protocol import ClientProtocol
from ..schema.items import AnyItem


class ItemCacheStorage(msgspec.Struct):
    server_version: str
    items: dict[str, AnyItem]
    constants: dict[str, float | int | str]


class ItemStorageMixin(ClientProtocol):
    def load_items_and_constants(self) -> None:
        cache_file = "item_cache.yaml"
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                data = f.read()
            item_cache = msgspec.yaml.decode(data, type=ItemCacheStorage)
            self._items = item_cache.items
            self._constants = item_cache.constants
            self._client_version = item_cache.server_version

    def set_items_and_constants(
        self, items: dict[str, AnyItem], constants: dict[str, float | int | str]
    ) -> None:
        self._items = items
        self._constants = constants

        if not self._server_version:
            raise ValueError("server_version not set")

        item_cache = ItemCacheStorage(server_version=self._server_version, items=items, constants=constants)
        data = msgspec.yaml.encode(item_cache)
        with open("item_cache.yaml", "wb") as f:
            f.write(data)
