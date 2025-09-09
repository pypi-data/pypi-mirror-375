from dataclasses import dataclass

from programming_game.schema.items import AnyItem, Item
from programming_game.schema.units import NPC, AnyUnit, Monster, Player


@dataclass()
class GetInventoryResponseItem:
    item: Item
    inventory_count: float


class InternalGameState:
    character_id: str
    instance_id: str
    units: dict[str, AnyUnit]
    items: dict[str, AnyItem]

    def __init__(self, character_id: str, instance_id: str):
        self.instance_id = instance_id
        self.character_id = character_id
        self.units = {}
        self.items = {}

    def get_inventory(self, filter: type[Item] | None = None) -> dict[str, GetInventoryResponseItem]:
        if not self.player:
            return {}
        items = {}
        for item_id, count in self.player.inventory.items():
            item = self.items.get(item_id)
            if item:
                if filter and not isinstance(item, filter):
                    continue
                items[item_id] = GetInventoryResponseItem(item=item, inventory_count=count)
        return items

    # noinspection PyTypeChecker
    @property
    def player(self) -> Player | None:
        """Returns the player unit if it exists. (won't exist before first tick maybe)"""
        if self.character_id not in self.units:
            return None
        unit = self.units[self.character_id]
        if isinstance(unit, Player):
            return unit
        return None

    @property
    def monster(self) -> tuple[Monster, ...]:
        return tuple(unit for unit in self.units.values() if isinstance(unit, Monster))

    @property
    def npc(self) -> tuple[NPC, ...]:
        return tuple(unit for unit in self.units.values() if isinstance(unit, NPC))


# used to cast because on script side the player is never null when called in on_tick
class GameState(InternalGameState):
    player: Player
