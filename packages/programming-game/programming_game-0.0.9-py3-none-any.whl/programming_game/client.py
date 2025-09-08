import asyncio
import importlib
import inspect
import time
import uuid
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, get_args

import msgspec
import websockets
import websockets.protocol

from .config import load_config
from .schema.items import AnyItem
from .utils.item_cache import ItemStorageMixin

if TYPE_CHECKING:
    from .db import DBClient

from collections import defaultdict

from .logging import logger
from .schema.events import AnyEvent
from .schema.intents import AnyIntent, BaseIntent, SendIntent, SendIntentValue
from .schema.messages import EventsMessage, ServerMessage, VersionMessage
from .structure.callable_script_wrapper import CallableScriptWrapper
from .structure.game_state import GameState
from .structure.instance import Instance
from .structure.instance_character import InstanceCharacter
from .structure.on_tick_response import OnTickResponse, OnTickResponseType, PostDelayedIntent, PreDelayedIntent

try:
    from .db import DBClient

    _db_available = True
except ImportError:
    DBClient = type(None)  # type: ignore
    _db_available = False

json_encoder = msgspec.json.Encoder()
json_decoder = msgspec.json.Decoder()

OnLoopHandler = Callable[[GameState], Coroutine[Any, Any, AnyIntent | None]]
OnEventHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]
OnLoopHandlerWithEvents = Callable[[GameState, list[AnyEvent]], Coroutine[Any, Any, AnyIntent | None]]

CallableScript = Callable[[], Coroutine[Any, Any, "OnTickResponse"]]
OnSetupCharacter = Callable[[GameState], Coroutine[Any, Any, Any | CallableScript]]


@dataclass
class TaskMetadata:
    """Metadata for tracking character tasks."""
    task_id: str
    instance_id: str
    character_id: str
    task: asyncio.Task[Any]
    start_time: float
    player_name: str | None = None


def parse_message(message_str: str) -> ServerMessage | None:
    message = json_decoder.decode(message_str)
    try:
        if message.get("type") == "events":
            for _instance_id, chars in message.get("value", {}).items():
                for char_id, events in chars.items():
                    replace = []
                    for event in events:
                        # if there is a invalid intent in the event, remove it
                        if event[0] == "connectionEvent":
                            for unit in event[1].get("units", []).values():
                                if unit["intent"]:
                                    try:
                                        msgspec.convert(unit["intent"], type=AnyIntent)
                                    except msgspec.ValidationError:
                                        unit["intent"] = None
                        # check all events
                        event[1]["type"] = event[0]
                        try:
                            msgspec.convert(event[1], type=AnyEvent)
                            replace.append(event[1])
                        except msgspec.ValidationError as e:
                            del event[1]["type"]
                            logger.warning(
                                f"Error deconding event: {char_id} {event[0]} {e} {event[1]}",
                                exc_info=False,
                            )
                    chars[char_id] = replace
    except Exception as e:
        logger.error(f"Error in parse_message: {e}", exc_info=True)
        return
    try:
        return msgspec.convert(message, type=ServerMessage)
    except msgspec.ValidationError:
        logger.error(f"Invalid message: {message}", exc_info=True)
        return


# noinspection PyPep8Naming
class GameClient(ItemStorageMixin):
    def __init__(
        self,
        log_level: str = "INFO",
        enable_db: bool = False,
        database_url: str | None = None,
        user_id: str | None = None,
        user_secret: str | None = None,
        server_url: str | None = None,
        disable_loop: bool = False,
    ):
        self._log_level = log_level
        self._websocket: websockets.WebSocketClientProtocol | None = None  # type: ignore
        self._time = 0
        self._instances: dict[str, Instance] = {}
        self._items: dict[str, AnyItem] = {}
        self._constants: Any = {}
        self._is_running = False
        self._reconnect_delay = 1

        self._server_version: str | None = None
        self._client_version: str | None = None

        self._setup_character_handler: dict | None = None
        self._on_event_handlers: dict[type, list[OnEventHandler]] = defaultdict(list)

        # Task registry for tracking running character tasks
        self._running_tasks: dict[str, TaskMetadata] = {}

        self._config = load_config(
            database_url=database_url,
            user_id=user_id,
            user_secret=user_secret,
            server_url=server_url,
            disable_loop=disable_loop,
        )

        # Optional DB integration
        self._db_client: DBClient | None = None
        if enable_db and _db_available:
            self._db_client = DBClient(self._config.DATABASE_URL)
        elif enable_db and not _db_available:
            logger.warning(
                "DB integration requested but dependencies not installed. Install with: pip install programming-game[db]"
            )
        if self._config.SLOW_LOOP_DELAY < 0.3:
            logger.error(
                "SLOW_LOOP_DELAY is too low. It should be at least 0.3 seconds to prevent server throttling."
            )
            raise ValueError(
                "SLOW_LOOP_DELAY is too low. It should be at least 0.3 seconds to prevent server throttling."
            )

    def setup_character(self) -> Callable[[OnSetupCharacter], OnSetupCharacter]:
        def decorator(func: OnSetupCharacter) -> OnSetupCharacter:
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            is_instance_method = params and params[0].name == "self"
            class_name = None
            module = None
            if is_instance_method:
                qualname = func.__qualname__
                class_name = qualname.rsplit(".", 1)[0]
                module = func.__module__
            self._setup_character_handler = {
                "func": func,
                "is_instance_method": is_instance_method,
                "class_name": class_name,
                "module": module,
            }
            logger.debug(f"✅ Funktion '{func.__name__}' registriert")
            return func

        return decorator

    def on_event(self, event_type: type | tuple | list):
        def decorator(func: OnEventHandler) -> OnEventHandler:
            extracted_types = get_args(event_type)
            if extracted_types:
                types_to_register = list[Any](extracted_types)
            elif isinstance(event_type, list | tuple):
                types_to_register = event_type
            else:
                types_to_register = [event_type]

            for etype in types_to_register:
                if inspect.isclass(etype):
                    self._on_event_handlers[etype].append(func)
                    logger.debug(f"✅ Funktion '{func.__name__}' registriert für Event '{etype.__name__}'")
                else:
                    logger.warning(f"⚠️ Warnung: '{etype}' ist kein gültiger Typ und wird ignoriert.")
            return func

        return decorator

    # DB integration methods
    async def get_db_session(self) -> Any:
        """Get a database session for user operations."""
        if self._db_client:
            return await self._db_client.get_session()
        else:
            raise RuntimeError("Database integration not enabled. Set enable_db=True in constructor.")

    async def queue_event(self, event_data: dict[str, Any], user_id: str | None = None):
        """Queue a user-defined event for logging to database."""
        if self._db_client:
            await self._db_client.queue_user_event(event_data, user_id)
        else:
            logger.warning("Database integration not enabled. Event not queued.")

    def get_running_tasks(self) -> list[TaskMetadata]:
        """Get a list of all currently running character tasks.

        Returns:
            List of TaskMetadata objects containing task information.
        """
        # Clean up completed tasks from registry
        keys_to_remove = []
        for task_key, metadata in self._running_tasks.items():
            if metadata.task.done():
                keys_to_remove.append(task_key)

        for key in keys_to_remove:
            self._running_tasks.pop(key, None)

        return list(self._running_tasks.values())

    def get_task_by_id(self, task_id: str) -> TaskMetadata | None:
        """Get a specific task by its ID.

        Args:
            task_id: The unique task identifier

        Returns:
            TaskMetadata if found, None otherwise
        """
        for metadata in self._running_tasks.values():
            if metadata.task_id == task_id and not metadata.task.done():
                return metadata
        return None

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task by its ID.

        Args:
            task_id: The unique task identifier

        Returns:
            True if task was found and cancelled, False otherwise
        """
        metadata = self.get_task_by_id(task_id)
        if metadata:
            metadata.task.cancel()
            task_key = f"{metadata.instance_id}:{metadata.character_id}"
            self._running_tasks.pop(task_key, None)
            logger.info(f"🛑 Cancelled task {task_id} for character {metadata.character_id}")
            return True
        return False

    async def _initialize_instance(self, instance_id: str, character_id: str) -> InstanceCharacter:
        logger.debug(f"🏗️ _initialize_instance called for {instance_id}:{character_id}")
        instance = self._instances.get(instance_id)
        if not instance:
            logger.info(f"📦 Creating new instance {instance_id}")
            instance = Instance(time=0, instance_id=instance_id)
            self._instances[instance_id] = instance
        if character_id not in instance.characters:
            logger.info(f"👤 Adding character {character_id} to instance {instance_id}")
            script = None
            game_state = GameState(instance_id=instance_id, character_id=character_id)
            if not self._config.DISABLE_LOOP and self._setup_character_handler:
                if self._setup_character_handler["is_instance_method"]:
                    class_name = self._setup_character_handler["class_name"]
                    module = self._setup_character_handler["module"]
                    mod = importlib.import_module(module)
                    cls = getattr(mod, class_name)
                    if not hasattr(self, "_setup_instance"):
                        self._setup_instance = cls()
                    script = await self._setup_character_handler["func"](self._setup_instance, game_state)
                else:
                    script = await self._setup_character_handler["func"](game_state)

            if not script:
                character = InstanceCharacter(
                    tick_time=self._config.FAST_LOOP_DELAY,
                    character_id=character_id,
                    instance=instance,
                    game_state=game_state,
                )
                instance.characters[character_id] = character
                logger.warning("Created character without script or loop disabled in config")
            elif hasattr(script, "on_tick"):
                # Traditional script object
                character = InstanceCharacter(
                    tick_time=self._config.FAST_LOOP_DELAY,
                    _script=script,
                    character_id=character_id,
                    instance=instance,
                    game_state=game_state,
                )
                instance.characters[character_id] = character
                self._start_character_task(instance_id, character_id)
            elif callable(script):
                # New callable-based script
                wrapped_script = CallableScriptWrapper(_callable=script)
                character = InstanceCharacter(
                    tick_time=self._config.FAST_LOOP_DELAY,
                    _script=wrapped_script,
                    character_id=character_id,
                    instance=instance,
                    game_state=game_state,
                )
                instance.characters[character_id] = character
                self._start_character_task(instance_id, character_id)
            else:
                logger.warning(
                    f"Failed to setup character {character_id} in instance {instance_id}. "
                    f"Expected script object or callable, got {type(script)}. Not starting character task!"
                )

        return instance.characters[character_id]

    def _start_character_task(self, instance_id: str, character_id: str) -> None:
        """Start or restart a character tick task."""
        logger.info(f"🔄 Attempting to start tick task for character {character_id} in instance {instance_id}")
        instance = self._instances.get(instance_id)
        if not instance or character_id not in instance.characters:
            logger.warning(f"❌ Cannot start task for unknown character {character_id} in {instance_id}")
            return

        character = instance.characters[character_id]

        # Cancel existing task if any
        if character._tick_task and not character._tick_task.done():
            logger.info(f"🛑 Cancelling existing tick task for character {character_id} in {instance_id}")
            # Remove from task registry if it exists
            task_key = f"{instance_id}:{character_id}"
            self._running_tasks.pop(task_key, None)
            character._tick_task.cancel()

        # Only create task if websocket is connected (has running event loop)
        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            # Create new task
            task = asyncio.create_task(self._character_tick_loop(instance_id, character_id))
            character._tick_task = task

            # Generate unique task ID and store in registry
            task_id = str(uuid.uuid4())
            task_key = f"{instance_id}:{character_id}"

            # Get player name for better identification
            player_name = None
            if character.game_state.player:
                player_name = character.game_state.player.name

            task_metadata = TaskMetadata(
                task_id=task_id,
                instance_id=instance_id,
                character_id=character_id,
                task=task,
                start_time=time.time(),
                player_name=player_name
            )

            self._running_tasks[task_key] = task_metadata

            def log_task_exception(task: asyncio.Task[Any]):
                if not task.cancelled() and (exc := task.exception()):
                    logger.error(
                        f"💥 Character tick task for {character_id} in {instance_id} ended unexpectedly!",
                        exc_info=exc,
                    )
                else:
                    logger.info(f"✅ Character tick task for {character_id} in {instance_id} completed normally")
                # Remove from registry when task completes
                self._running_tasks.pop(task_key, None)

            task.add_done_callback(log_task_exception)
            logger.info(f"✅ Started tick task {task_id} for character {character_id} in instance {instance_id}")
        else:
            # Just mark that we need to start this task when websocket connects
            character._tick_task = None  # Placeholder
            logger.info(f"⏳ Queued tick task for character {character_id} in instance {instance_id} (websocket not ready)")

    async def _send(self, message: dict[str, Any]):
        if self._websocket:
            msg_str = json_encoder.encode(message).decode("utf-8")
            # logger.debug(f"Sending message: {msg_str}")
            await self._websocket.send(msg_str)

    async def _send_msg(self, data: msgspec.Struct):
        if self._websocket:
            msg_str = json_encoder.encode(data).decode("utf-8")
            # logger.debug(f"message: {msg_str}")
            await self._websocket.send(msg_str)

    async def _update_state(self, character_instance: InstanceCharacter, event_list: list[AnyEvent]):
        char_id = character_instance.character_id
        instance_id = character_instance.instance.instance_id

        logger.debug(f"🔄 Updating state for {char_id} in {instance_id} with {len(event_list)} events")

        for event in event_list:
            logger.debug(f"🔄 Processing event: {type(event).__name__}")
            await character_instance.handle_event(event, self)
            event_type = type(event)

            if event_type in self._on_event_handlers:
                for handler in self._on_event_handlers[event_type]:
                    try:
                        await handler(event, character_instance.game_state)
                    except Exception:
                        logger.error(
                            f"An error occurred in the on_event callback for event: {event_type.__name__}",
                            exc_info=True,
                        )

            # Collect events for on_loop handler if they match specified types
            # if self._on_loop_event_types and event_type in self._on_loop_event_types:
            #    character_instance.recent_events.append(event)

            # Log incoming event to database
            if self._db_client:
                try:
                    await self._db_client.log_event(
                        event_type=event_type.__name__,
                        direction="in",
                        data=msgspec.to_builtins(event),
                        character_id=char_id,
                        instance_id=instance_id,
                        user_id=self._credentials.get("id") if self._credentials else None,
                    )
                except Exception:
                    logger.error(f"Failed to log incoming event: {event_type.__name__}", exc_info=True)

    async def _character_tick_loop(self, instance_id: str, char_id: str):
        """Per-character tick loop with dynamic sleep intervals."""
        logger.info(f"🚀 Starting tick loop for character {char_id} in instance {instance_id}")
        instance = self._instances.get(instance_id)
        if not instance or char_id not in instance.characters:
            logger.warning(f"❌ Character {char_id} in instance {instance_id} no longer exists at loop start")
            return

        character = instance.characters[char_id]

        while self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            try:
                instance = self._instances.get(instance_id)
                if not instance or char_id not in instance.characters:
                    logger.warning(f"❌ Character {char_id} in instance {instance_id} no longer exists during loop - breaking")
                    break

                character_state = instance.characters[char_id]
                if instance_id == "overworld" or instance_id.startswith("instance-"):
                    units = character_state.units
                    if char_id not in units:
                        logger.debug(f"Character {char_id} not found in units in loop")
                        await asyncio.sleep(1)
                        continue

                    char = units[char_id]
                    try:
                        intent_to_send: AnyIntent | None = None
                        pre_intent_delay = 0.0
                        post_intent_delay = self._config.SLOW_LOOP_DELAY
                        without_intent_delay = self._config.FAST_LOOP_DELAY
                        logger.debug(f"🔄 Calling on_tick for {char_id}")
                        result: OnTickResponse = await character_state._script.on_tick()
                        logger.debug(f"🔄 on_tick returned: {type(result).__name__} = {result}")
                        match result:
                            case None:
                                logger.debug(f"🔄 on_tick returned None, no action")
                                pass
                            case BaseIntent():
                                intent_to_send = result
                                logger.debug(f"🔄 on_tick returned intent: {result}")
                            case PreDelayedIntent():
                                pre_intent_delay = pre_intent_delay
                                intent_to_send = result.intent
                                logger.debug(f"🔄 on_tick returned PreDelayedIntent: {result}")
                            case PostDelayedIntent():
                                post_intent_delay = max(result.time, post_intent_delay)
                                intent_to_send = result.intent
                                logger.debug(f"🔄 on_tick returned PostDelayedIntent: {result}")
                            case OnTickResponseType():
                                logger.debug(f"🔄 on_tick returned OnTickResponseType, no action")
                                pass
                            case _:
                                logger.warning(f"🔄 on_tick returned unexpected type: {type(result)} = {result}")
                                raise DeprecationWarning(
                                    f"""The on_tick callback should return a correct type: {type(result)}"""
                                )
                        player_name = (
                            character.game_state.player.name if character.game_state.player else "Unknown"
                        )
                        if intent_to_send and intent_to_send != char.intent:
                            # Log outgoing intent to database
                            if self._db_client:
                                try:
                                    await self._db_client.log_intent(
                                        intent_type=type(result).__name__,
                                        data=msgspec.to_builtins(result),
                                        character_id=char_id,
                                        instance_id=instance_id,
                                        user_id=self._credentials.get("id") if self._credentials else None,
                                    )
                                except Exception:
                                    logger.error(
                                        f"Failed to log outgoing intent: {type(result).__name__}",
                                        exc_info=True,
                                    )

                            if pre_intent_delay:
                                logger.debug(
                                    f"{player_name} delaying {pre_intent_delay} before sinding: {intent_to_send}"
                                )
                                await asyncio.sleep(result.time)
                            await self._send_msg(
                                SendIntent(
                                    value=SendIntentValue(
                                        c=char_id, i=instance_id, unitId=char_id, intent=intent_to_send
                                    )
                                )
                            )
                            logger.debug(
                                f"{player_name} after {time.time() - character.last_intent_time:4.2f} pausing {post_intent_delay}: Sending intent for {char_id}: {result}"
                            )
                            character.last_intent_time = time.time()
                            await asyncio.sleep(post_intent_delay)
                        else:
                            await asyncio.sleep(without_intent_delay)
                    except Exception as e:
                        logger.error(f"Error in on_loop_handler for {char_id}: {e}", exc_info=True)
                        await asyncio.sleep(self._config.ERROR_LOOP_DELAY)
                    finally:
                        # Clear recent events after processing
                        # character.recent_events.clear()
                        pass

            except Exception:
                logger.error(
                    f"💥 An error occurred in character tick loop for {char_id} (probably in your on_tick logic). Pausing for 5 seconds.",
                    exc_info=True,
                )
                await asyncio.sleep(5)

        logger.info(f"🏁 Tick loop ended for character {char_id} in instance {instance_id}")

    async def handle_message(self, message: ServerMessage) -> None:
        try:
            if type(message) is EventsMessage:
                logger.debug(f"📨 Processing EventsMessage with {len(message.value)} instances")
                for instance_id, chars in message.value.items():
                    for char_id, events in chars.items():
                        logger.debug(f"📨 Processing {len(events)} events for character {char_id} in instance {instance_id}")
                        logger.debug(f"📨 Events: {[type(e).__name__ for e in events]}")
                        character_instance = await self._initialize_instance(instance_id, char_id)
                        await self._update_state(character_instance, events)
            elif type(message) is VersionMessage:
                self._server_version = message.value
                logger.info(f"📡 Server version: {message.value}")
        except Exception as e:
            logger.error(f"💥 Error in handle_message: {e}", exc_info=True)

    async def connect(self, server_url: str | None = None) -> None:
        await self.load_items_and_constants()

        if not self._setup_character_handler and not self._config.DISABLE_LOOP:
            raise RuntimeError(
                "No setup_character handler registered. Use @client.setup_character decorator or disable loop in configuration."
            )
        self._is_running = True

        # Initialize DB if enabled
        if self._db_client:
            await self._db_client.initialize()
        if server_url:
            self._config.SERVER_URL = server_url
        while self._is_running:
            logger.info(f"Connecting to server at {self._config.SERVER_URL}...")
            try:
                async with websockets.connect(self._config.SERVER_URL) as websocket:
                    self._websocket = websocket
                    self._reconnect_delay = 1  # Reset reconnect delay on successful connection
                    logger.info("✅ Connection established successfully!")
                    await self._send(
                        {
                            "type": "credentials",
                            "value": dict(id=self._config.GAME_CLIENT_ID, key=self._config.GAME_CLIENT_KEY),
                            "version": self._client_version or "0.0.1",
                        }
                    )

                    # Start tick tasks for existing characters
                    logger.info(f"🔄 Starting tick tasks for existing characters after connection ({len(self._instances)} instances)")
                    for instance_id, instance in self._instances.items():
                        for char_id in instance.characters:
                            self._start_character_task(instance_id, char_id)

                    # Also start any queued tasks (characters with tick_task = None)
                    logger.info("🔄 Starting queued tick tasks")
                    for instance_id, instance in self._instances.items():
                        for char_id, character in instance.characters.items():
                            if character._tick_task is None:  # Queued task
                                self._start_character_task(instance_id, char_id)

                    async for message_str in websocket:
                        if message := parse_message(message_str):
                            await self.handle_message(message)

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"🔌 Connection closed: {e}. Reconnecting in {self._reconnect_delay} seconds...")
            except ConnectionRefusedError:
                logger.error(f"🚫 Connection refused. Reconnecting in {self._reconnect_delay} seconds...")
            except Exception:
                logger.error(
                    f"💥 A critical error occurred. Reconnecting in {self._reconnect_delay} seconds...",
                    exc_info=True,
                )
            finally:
                # Cancel all character tasks on disconnect
                logger.info(f"🛑 Cancelling all character tasks on disconnect ({len(self._instances)} instances)")
                for instance in self._instances.values():
                    for character in instance.characters.values():
                        if character._tick_task and not character._tick_task.done():
                            logger.info(f"🛑 Cancelling tick task for character {character.character_id} in {instance.instance_id}")
                            character._tick_task.cancel()
                        # Reset runtime data
                        character._tick_task = None
                        character.last_intent_time = 0.0  # character.recent_events.clear()

                # Clear task registry
                logger.info(f"🗑️ Clearing task registry ({len(self._running_tasks)} tasks)")
                self._running_tasks.clear()

                # Clear instances to prevent memory leak on reconnect
                logger.info(f"🗑️ Clearing _instances with {len(self._instances)} instances to prevent memory leak")
                self._instances.clear()
                logger.info("✅ _instances cleared")

                self._websocket = None
                if self._is_running:
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(self._reconnect_delay * 2, 60)  # Exponential backoff, max 60s

    async def disconnect(self) -> None:
        """Gracefully disconnects from the server."""
        # logger.info("Disconnecting from server...")
        self._is_running = False

        # Cancel all character tasks
        for instance in self._instances.values():
            for character in instance.characters.values():
                if character._tick_task and not character._tick_task.done():
                    character._tick_task.cancel()
                # Reset runtime data
                character._tick_task = None
                character.last_intent_time = 0.0  # character.recent_events.clear()

        # Clear task registry
        logger.info(f"🗑️ Clearing task registry on disconnect ({len(self._running_tasks)} tasks)")
        self._running_tasks.clear()

        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            await self._websocket.close()
        self._websocket = None

        # Shutdown DB client
        if self._db_client:
            await self._db_client.shutdown()

        logger.info("Disconnected successfully.")
