from __future__ import annotations
from typing import Tuple
from helpers.utils import safe_int
from .resource import Resource

def get_level_group(level: int) -> Tuple[int, int]:
    if 1 <= level <= 4: return (1,4)
    if 5 <= level <= 8: return (5,8)
    if 9 <= level <= 12: return (9,12)
    if 13 <= level <= 16: return (13,16)
    return (17,20)

class Bastion:
    MAX_SPECIAL_FACILITIES = {
        ((1, 4), 'wretched'): 0,
        ((1, 4), 'modest'): 0,
        ((1, 4), 'comfortable'): 0,
        ((1, 4), 'wealthy'): 0,
        ((1, 4), 'aristocratic'): 0,
        ((5, 8), 'wretched'): 0,
        ((5, 8), 'modest'): 0,
        ((5, 8), 'comfortable'): 1,
        ((5, 8), 'wealthy'): 2,
        ((5, 8), 'aristocratic'): 2,
        ((9, 12), 'wretched'): 0,
        ((9, 12), 'modest'): 0,
        ((9, 12), 'comfortable'): 2,
        ((9, 12), 'wealthy'): 4,
        ((9, 12), 'aristocratic'): 5,
        ((13, 16), 'wretched'): 0,
        ((13, 16), 'modest'): 0,
        ((13, 16), 'comfortable'): 3,
        ((13, 16), 'wealthy'): 5,
        ((13, 16), 'aristocratic'): 6,
        ((17, 20), 'wretched'): 0,
        ((17, 20), 'modest'): 0,
        ((17, 20), 'comfortable'): 4,
        ((17, 20), 'wealthy'): 6,
        ((17, 20), 'aristocratic'): 7,
    }

    def __init__(self, lifestyle_type="modest"):
        self.bastion_flag = 0
        self.weeks_of_maintenance = 0
        self.turn_available_flag = 0
        self.facilities = []
        self.lifestyle_type = (lifestyle_type or "modest").lower()

    def load_from_sheet_data(self, get_val):
        from helpers.utils import safe_int
        self.bastion_flag = safe_int(get_val('bastion_flag'), default=0)
        self.weeks_of_maintenance = safe_int(get_val('bastion_maintenance'), default=0)
        self.turn_available_flag = safe_int(get_val('bastion_turn_flag'), default=0)

    def get_sheet_data(self) -> dict[str, any]:
        return {
            'bastion_flag': self.bastion_flag,
            'bastion_maintenance': self.weeks_of_maintenance,
            'bastion_turn_flag': self.turn_available_flag
        }

    def get_max_special_facilities(self, level):
        level_group = get_level_group(level)
        return self.MAX_SPECIAL_FACILITIES.get((level_group, self.lifestyle_type), 1)

    def get_summary(self) -> str:
        if not self.bastion_flag:
            return "**Bastion:** None"
        return (f"**Bastion:** Owned\n"
                f"**Maintenance weeks open:** {self.weeks_of_maintenance}\n"
                f"**Turn available:** {bool(self.turn_available_flag)}")

    def maintain_bastion(self, actor_resources: Resource, level: int, special_facilities=None):
        if self.bastion_flag == 0:
            raise ValueError("No bastion is under your stewardship.")
        if self.turn_available_flag == 0:
            raise ValueError("No bastion turn remains available this cycle.")
        if special_facilities is None or special_facilities <= 0:
            special_facilities = self.get_max_special_facilities(level)
        cost = self.weeks_of_maintenance * special_facilities * 5
        actor_resources.deduct(gold=cost)
        self.weeks_of_maintenance = 0
        self.turn_available_flag = 0
        return cost