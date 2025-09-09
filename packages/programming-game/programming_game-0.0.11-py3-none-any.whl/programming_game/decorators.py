import inspect
from collections.abc import Callable, Coroutine
from typing import Any, get_args

from programming_game.logging import logger
from programming_game.protocol import ClientProtocol
from programming_game.schema.events import AnyEvent
from programming_game.structure.game_state import GameState


# Mixin-Klasse, die die konkrete Implementierung der Decorator-Methoden bereitstellt.
# GameClient wird von dieser Mixin erben, um die Funktionalität nahtlos zu integrieren.
# Die Handler-Attribute werden hier initialisiert und verwaltet.
class DecoratorMixin(ClientProtocol):
    def setup_character(
        self,
    ) -> Callable[
        [Callable[[str, str], Coroutine[Any, Any, Any]]],
        Callable[[str, str], Coroutine[Any, Any, Any]],
    ]:
        """Decorator für die Registrierung des setup_character Handlers.

        Refaktorisierung: Diese Methode wurde aus client.py (ursprünglich Zeilen 143-162) extrahiert.
        Sie analysiert die Signatur der Funktion, um zu prüfen, ob es sich um eine Instanzmethode handelt,
        und speichert die Metadaten für spätere Verwendung in _initialize_instance.

        Args:
            func: Die Async-Funktion, die bei Character-Initialisierung aufgerufen wird.

        Returns:
            Die unveränderte Funktion (für Dekorator-Kompatibilität).
        """

        def decorator(
            func: Callable[[str, str], Coroutine[Any, Any, Any]],
        ) -> Callable[[str, str], Coroutine[Any, Any, Any]]:
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
            return func

        return decorator

    def on_event(
        self, event_type: type[AnyEvent] | tuple[type[AnyEvent], ...] | list[type[AnyEvent]]
    ) -> Callable[
        [Callable[[AnyEvent, GameState], Coroutine[Any, Any, None]]],
        Callable[[AnyEvent, GameState], Coroutine[Any, Any, None]],
    ]:
        """Dekorator für die Registrierung von Event-Handlern.

        Refaktorisierung: Diese Methode wurde aus client.py (ursprünglich Zeilen 165-183) extrahiert.
        Sie extrahiert Event-Typen aus dem Argument (unterstützt Type, Tuple oder List) und registriert
        den Handler in _on_event_handlers. Dies ermöglicht globale Event-Callbacks, ergänzend zu per-Character Handlern.

        Args:
            event_type: Der Event-Typ (oder Tupel/Liste davon), für den der Handler registriert wird.
            func: Die Async-Funktion, die bei passendem Event aufgerufen wird (erhält Event und GameState).

        Returns:
            Die unveränderte Funktion.
        """

        def decorator(
            func: Callable[[AnyEvent, GameState], Coroutine[Any, Any, None]],
        ) -> Callable[[AnyEvent, GameState], Coroutine[Any, Any, None]]:
            extracted_types = get_args(event_type)
            if extracted_types:
                types_to_register = list(extracted_types)
            elif isinstance(event_type, tuple | list):
                types_to_register = list(event_type)
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
