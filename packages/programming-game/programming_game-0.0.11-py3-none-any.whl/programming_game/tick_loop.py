import asyncio
import importlib
import time
from typing import TYPE_CHECKING, cast

import msgspec
import websockets

from programming_game.logging import logger
from programming_game.protocol import ClientProtocol
from programming_game.schema.intents import BaseIntent, SendIntent, SendIntentValue
from programming_game.structure.callable_script_wrapper import CallableScriptWrapper
from programming_game.structure.game_state import GameState, InternalGameState
from programming_game.structure.instance import Instance
from programming_game.structure.instance_character import InstanceCharacter
from programming_game.structure.on_tick_response import PostDelayedIntent, TickPause

if TYPE_CHECKING:
    from programming_game.client import GameClient


class TickLoopMixin(ClientProtocol):
    """
    Mixin für den zentralen Tick-Loop und die Instanz-Initialisierung.

    Extrahiert aus client.py für bessere Modularität.
    Folgt dem Muster der anderen Mixins (DecoratorMixin, MessageProcessingMixin).
    Bietet _initialize_instance und _central_tick_loop bereit.
    Abhängigkeiten: self._instances, self._config, self._db_client, self._on_event_handlers.
    """

    async def _initialize_instance(
        self: "GameClient", instance_id: str, character_id: str
    ) -> InstanceCharacter:
        instance = self._instances.get(instance_id)
        if not instance:
            instance = Instance(time=0, instance_id=instance_id)
            self._instances[instance_id] = instance
        if character_id not in instance.characters:
            script = None
            game_state = InternalGameState(instance_id=instance_id, character_id=character_id)
            if not self._config.DISABLE_LOOP and self._setup_character_handler:
                if self._setup_character_handler["is_instance_method"]:
                    class_name = self._setup_character_handler["class_name"]
                    module = self._setup_character_handler["module"]
                    mod = importlib.import_module(module)
                    cls = getattr(mod, class_name)
                    if not hasattr(self, "_setup_instance"):
                        self._setup_instance = cls()
                    script = await self._setup_character_handler["func"](
                        self._setup_instance, instance_id, character_id
                    )
                else:
                    script = await self._setup_character_handler["func"](instance_id, character_id)

            current_time = time.time()
            fast_delay = self._config.FAST_LOOP_DELAY

            if not script:
                character = InstanceCharacter(
                    tick_time=fast_delay,
                    next_tick_time=current_time + fast_delay,
                    character_id=character_id,
                    instance=instance,
                    game_state=game_state,
                )
                instance.characters[character_id] = character
                logger.warning("Created character without script or loop disabled in config")
            elif hasattr(script, "on_tick"):
                # Traditional script object
                character = InstanceCharacter(
                    tick_time=fast_delay,
                    next_tick_time=current_time + fast_delay,
                    _script=script,
                    character_id=character_id,
                    instance=instance,
                    game_state=game_state,
                )
                instance.characters[character_id] = character
            elif callable(script):
                # New callable-based script
                wrapped_script = CallableScriptWrapper(_callable=script)
                character = InstanceCharacter(
                    tick_time=fast_delay,
                    next_tick_time=current_time + fast_delay,
                    _script=wrapped_script,
                    character_id=character_id,
                    instance=instance,
                    game_state=game_state,
                )
                instance.characters[character_id] = character
            else:
                logger.warning(
                    f"Failed to setup character {character_id} in instance {instance_id}. "
                    f"Expected script object or callable, got {type(script)}. Not starting character task!"
                )

        return instance.characters[character_id]

    async def _central_tick_loop(self: "GameClient"):
        """Central tick loop for all characters."""
        while (
            self._is_running and self._websocket and self._websocket.state == websockets.protocol.State.OPEN
        ):
            try:
                current_time = time.time()
                for instance_id, instance in list(self._instances.items()):
                    for char_id, character in list(instance.characters.items()):
                        if current_time >= character.next_tick_time:
                            try:
                                character.next_tick_time = current_time + self._config.FAST_LOOP_DELAY
                                if character._script is None:
                                    logger.warning(
                                        f"No script for character {char_id} in instance {instance_id}"
                                    )
                                    character.next_tick_time = current_time + 2
                                    continue
                                if character.game_state.player is None:
                                    logger.warning(
                                        f"Player is None for character {char_id} in instance {instance_id}"
                                    )
                                    character.next_tick_time = current_time + 2
                                    continue

                                result = await character._script.on_tick(
                                    cast(GameState, character.game_state)
                                )
                                intent_to_send = None
                                match result:
                                    case None | bool():
                                        pass
                                    case BaseIntent():
                                        intent_to_send = result
                                        character.next_tick_time = current_time + self._config.SLOW_LOOP_DELAY
                                    case PostDelayedIntent():
                                        intent_to_send = result.intent
                                        character.next_tick_time = max(
                                            result.time + current_time, character.next_tick_time
                                        )
                                    case TickPause():
                                        character.next_tick_time = current_time + result.time
                                        continue
                                    case _:
                                        logger.warning(
                                            f"Unknown on_tick response for {char_id}: {type(result)}"
                                        )
                                        continue
                                if instance_id == "overworld" or instance_id.startswith("instance-"):
                                    units = character.units
                                    if char_id not in units:
                                        logger.debug(f"Character {char_id} not found in units")
                                        character.next_tick_time = current_time + self._config.FAST_LOOP_DELAY
                                        continue

                                    char = units[char_id]
                                    if intent_to_send and intent_to_send != char.intent:
                                        # Log outgoing intent to database
                                        if self._db_client:
                                            try:
                                                await self._db_client.log_intent(
                                                    intent_type=type(result).__name__,
                                                    data=msgspec.to_builtins(result),
                                                    character_id=char_id,
                                                    instance_id=instance_id,
                                                    user_id=self._credentials.get("id")
                                                    if self._credentials
                                                    else None,
                                                )
                                            except Exception:
                                                logger.error(
                                                    f"Failed to log outgoing intent: {type(result).__name__}",
                                                    exc_info=True,
                                                )

                                        await self._send_msg(
                                            SendIntent(
                                                value=SendIntentValue(
                                                    c=char_id,
                                                    i=instance_id,
                                                    unitId=char_id,
                                                    intent=intent_to_send,
                                                )
                                            )
                                        )
                                        character.last_intent_time = current_time
                                        logger.debug(f"Sending intent for {char_id}: {result}")
                            except Exception as e:
                                logger.error(f"Error in on_tick for {char_id}: {e}", exc_info=True)
                                character.next_tick_time = current_time + self._config.ERROR_LOOP_DELAY
                await asyncio.sleep(0.05)  # Minimal sleep for CPU efficiency
            except Exception:
                logger.error("Error in central tick loop", exc_info=True)
                await asyncio.sleep(5)
