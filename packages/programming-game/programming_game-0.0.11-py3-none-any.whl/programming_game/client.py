import asyncio
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

import msgspec
import websockets
import websockets.protocol

from .config import load_config
from .decorators import DecoratorMixin
from .message_processing import MessageProcessingMixin
from .protocol import ClientProtocol
from .schema.items import AnyItem
from .tick_loop import TickLoopMixin
from .utils.item_cache import ItemStorageMixin

if TYPE_CHECKING:
    from .db import DBClient

from collections import defaultdict

from .logging import logger
from .schema.events import AnyEvent
from .schema.intents import AnyIntent
from .structure.game_state import GameState
from .structure.instance import Instance
from .structure.on_tick_response import (
    OnTickResponse,
)

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


# noinspection PyPep8Naming
class GameClient(DecoratorMixin, MessageProcessingMixin, ItemStorageMixin, TickLoopMixin):
    _central_task: asyncio.Task[None] | None = None

    def __init__(
        self: ClientProtocol,
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

        self._setup_character_handler: dict[str, Any] | None = None
        self._on_event_handlers: dict[
            type[AnyEvent], list[Callable[[AnyEvent, GameState], Coroutine[Any, Any, None]]]
        ] = defaultdict(list)

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

    async def connect(self, server_url: str | None = None) -> None:
        self.load_items_and_constants()

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
                    logger.debug("Connection established successfully!")
                    await self._send(
                        {
                            "type": "credentials",
                            "value": dict(id=self._config.GAME_CLIENT_ID, key=self._config.GAME_CLIENT_KEY),
                            "version": self._client_version or "0.0.1",
                        }
                    )
                    loop = self._central_tick_loop()
                    self._central_task = asyncio.create_task(loop)

                    async for message_str in websocket:
                        if message := self.parse_message(message_str):
                            await self.handle_message(message)

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"Connection closed: {e}. Reconnecting in {self._reconnect_delay} seconds...")
            except ConnectionRefusedError:
                logger.error(f"Connection refused. Reconnecting in {self._reconnect_delay} seconds...")
            except Exception:
                logger.error(
                    f"A critical error occurred. Reconnecting in {self._reconnect_delay} seconds...",
                    exc_info=True,
                )
            finally:
                # Cancel central tick task on disconnect
                if self._central_task and not self._central_task.done():
                    self._central_task.cancel()

                # Reset runtime data for characters
                for instance in self._instances.values():
                    for character in instance.characters.values():
                        character.last_intent_time = 0.0

                # Clear instances to prevent memory leak on reconnect
                logger.debug(f"Clearing _instances with {len(self._instances)} instances")
                self._instances.clear()
                logger.debug("_instances cleared")

                self._websocket = None
                if self._is_running:
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(self._reconnect_delay * 2, 60)  # Exponential backoff, max 60s

    async def disconnect(self) -> None:
        """Gracefully disconnects from the server."""
        # logger.info("Disconnecting from server...")
        self._is_running = False

        # Cancel central task
        if self._central_task and not self._central_task.done():
            self._central_task.cancel()

        # Reset runtime data for characters
        self._instances.clear()

        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            await self._websocket.close()
        self._websocket = None

        # Shutdown DB client
        if self._db_client:
            await self._db_client.shutdown()

        logger.info("Disconnected successfully.")
