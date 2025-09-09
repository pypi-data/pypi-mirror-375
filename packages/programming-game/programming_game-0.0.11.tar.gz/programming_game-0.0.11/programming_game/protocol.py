from collections.abc import Callable, Coroutine
from typing import Any, Protocol

from programming_game.schema.events import AnyEvent
from programming_game.schema.items import AnyItem
from programming_game.structure.game_state import GameState


class ClientProtocol(Protocol):
    _setup_character_handler: dict[str, Any]
    _on_event_handlers: dict[type[AnyEvent], list[Callable[[AnyEvent, GameState], Coroutine[Any, Any, None]]]]
    _items: dict[str, AnyItem]
    _constants: dict[str, float | int | str]
    _server_version: str | None
    _client_version: str | None
