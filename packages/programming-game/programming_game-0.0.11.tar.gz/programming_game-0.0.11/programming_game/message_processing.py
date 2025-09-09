from typing import TYPE_CHECKING

import msgspec

from .logging import logger
from .protocol import ClientProtocol
from .schema.events import AnyEvent
from .schema.messages import EventsMessage, ServerMessage, VersionMessage
from .structure.instance_character import InstanceCharacter

if TYPE_CHECKING:
    from .client import GameClient


class MessageProcessingMixin(ClientProtocol):
    """
    Mixin für das Parsen von Nachrichten und das Ausführen von Events.

    Folgt dem Muster der bestehenden Mixins (z.B. DecoratorMixin, EventMixin):
    - Bietet Methoden für Message-Processing bereit.
    - Nahtlose Integration durch Vererbung in GameClient.
    - Abhängigkeiten: self._instances, self._on_event_handlers, self._db_client.
    """

    @staticmethod
    def parse_message(message_str: str) -> ServerMessage | None:
        """Parsed eine rohe WebSocket-Nachricht und validiert sie mit msgspec."""
        message = msgspec.json.decode(message_str)
        try:
            if message.get("type") == "events":
                for _instance_id, chars in message.get("value", {}).items():
                    for char_id, events in chars.items():
                        replace = []
                        for event in events:
                            # Invalid intent in event entfernen
                            if event[0] == "connectionEvent":
                                for unit in event[1].get("units", []).values():
                                    if unit["intent"]:
                                        try:
                                            msgspec.convert(unit["intent"], type=AnyEvent)
                                        except msgspec.ValidationError:
                                            unit["intent"] = None
                            # Alle Events prüfen
                            event[1]["type"] = event[0]
                            try:
                                msgspec.convert(event[1], type=AnyEvent)
                                replace.append(event[1])
                            except msgspec.ValidationError as e:
                                del event[1]["type"]
                                logger.warning(
                                    f"Error decoding event: {char_id} {event[0]} {e} {event[1]}",
                                    exc_info=False,
                                )
                        chars[char_id] = replace
        except Exception as e:
            logger.error(f"Error in parse_message: {e}", exc_info=True)
            return None
        try:
            return msgspec.convert(message, type=ServerMessage)
        except msgspec.ValidationError:
            logger.error(f"Invalid message: {message}", exc_info=True)
            return None

    async def handle_message(self: "GameClient", message: ServerMessage) -> None:
        """Handhabt validierte Server-Nachrichten."""
        try:
            if isinstance(message, EventsMessage):
                for instance_id, chars in message.value.items():
                    for char_id, events in chars.items():
                        character_instance = await self._initialize_instance(instance_id, char_id)
                        await self._update_state(character_instance, events)
            elif isinstance(message, VersionMessage):
                self._server_version = message.value
                logger.info(f"Server version: {message.value}")
        except Exception as e:
            logger.error(f"Error in handle_message: {e}", exc_info=True)

    async def _update_state(
        self: "GameClient", character_instance: InstanceCharacter, event_list: list[AnyEvent]
    ) -> None:
        """Aktualisiert den State basierend auf Events und ruft Handler auf."""
        char_id = character_instance.character_id
        instance_id = character_instance.instance.instance_id

        for event in event_list:
            character_instance.handle_event(event, self)
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

            # DB-Logging für Events
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
