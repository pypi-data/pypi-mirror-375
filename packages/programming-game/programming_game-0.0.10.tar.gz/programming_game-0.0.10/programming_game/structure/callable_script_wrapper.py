from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from programming_game.structure.instance_character import ScriptProtocol

from .game_state import GameState
from .on_tick_response import OnTickResponse

CallableScript = Callable[[], Coroutine[Any, Any, OnTickResponse]]


@dataclass
class CallableScriptWrapper(ScriptProtocol):
    """
    Wrapper class for callable-based scripts.

    Allows setup_character to return a simple async function instead of a full script object.
    """

    _callable: CallableScript

    async def on_tick(self, game_state: GameState) -> OnTickResponse:
        return await self._callable(game_state)
