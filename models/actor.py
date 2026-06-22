from __future__ import annotations
from typing import Dict, Any
from connectors.sheets import get_values, batch_update
from helpers.utils import safe_int, safe_number, col_to_index
from .resource import Resource
from .lifestyle import Lifestyle
from .skills import Skills
from models.item import Item

class Actor:
    COLUMNS = {
        'name': 'A',
        'inspiration': 'D',
        'badge': 'E',
        'level': 'F',
        'missions': 'G',
        'last_played': 'H',
        'downtime': 'I',
        'living_weeks': 'J',
        'bastion_flag': 'K',
        'bastion_maintenance': 'L',
        'bastion_turn_flag': 'M',
        'lifestyle': 'N',
        'aristocratic_flag': 'O',
        'platinum': 'P',
        'gold': 'Q',
        'silver': 'R',
        'copper': 'S',
        'moradinium': 'T',
        'downtime_progress': 'V',
        'crp': 'W',
        'skills': 'X',
        'proficiencies': 'Y',
        'languages': 'Z',
        'notable_items': 'AA',
        'masterpiece': 'AB',
        'debt': 'AC',
        'no_shows': 'AK',
        'active_flag': 'AL'
    }

    def __init__(self, name=""):
        self.name = name
        self.row_index = None
        self.lifestyle = Lifestyle()
        self.resources = Resource()
        self.skills = Skills()
        self.items = []
        self.debt = Resource()
        self.stats: Dict[str, Any] = {}
        self.inspiration = ""
        self.level = 1
        self.missions = ""
        self.last_played = ""
        self.no_shows = 0
        self.active_flag = 0
        self.badge = ""
        self.aristocratic_flag = 0
        self.notable_items = ""
        self.masterpiece = ""

    def get_summary(self) -> str:
        parts = [
            f"**Name:** {self.name}",
            f"**Level:** {self.level}",
            f"**Badge:** {self.badge}",
            self.lifestyle.get_summary(),
        ]
        if self.lifestyle.bastion.bastion_flag:
            parts.append(self.lifestyle.bastion.get_summary())
        parts.append(self.resources.get_summary(include_money=True, include_moradinium=True, include_downtime=True))
        return "\n".join(parts)

    def load_from_sheet(self):
        rows = get_values("Characters!A3:AL150", value_render_option="UNFORMATTED_VALUE")
        for idx, row in enumerate(rows, start=3):
            if len(row) > 0 and str(row[0]).strip().lower() == str(self.name).strip().lower():
                self.row_index = idx
                def get_val(col):
                    c = self.COLUMNS[col]
                    c_idx = col_to_index(c)
                    return row[c_idx] if c_idx < len(row) else ""
                self.name = str(get_val('name') or self.name)
                self.inspiration = get_val('inspiration') or ""
                self.badge = get_val('badge') or "Bronze"
                self.level = safe_int(get_val('level'), default=1)
                self.missions = get_val('missions') or ""
                self.last_played = get_val('last_played')
                self.no_shows = safe_int(get_val('no_shows'), default=0)
                self.active_flag = safe_int(get_val('active_flag'), default=0)
                self.notable_items = str(get_val('notable_items') or "").strip()
                self.masterpiece = str(get_val('masterpiece') or "").strip()
                self.items = Item.parse_notable_items(self.notable_items)

                self.lifestyle.load_from_sheet_data(get_val)
                self.resources.load_from_sheet_data(get_val)
                self.skills.load_from_sheet_data(get_val)
                return
        raise ValueError(f"Actor '{self.name}' could not be found in the records.")

    def save_to_sheet(self):
        if self.row_index is None:
            raise ValueError(f"Actor '{self.name}' was not loaded from the sheet; row unknown.")
        updates = []
        def add_update(col, val):
            c = self.COLUMNS[col]
            updates.append({
                "range": f"Characters!{c}{self.row_index}:{c}{self.row_index}",
                "values": [[val]]
            })
        self.notable_items = Item.serialize_notable_items(self.items)

        add_update('name', self.name)
        add_update('inspiration', self.inspiration)
        add_update('badge', self.badge)
        add_update('level', self.level)
        add_update('missions', self.missions)
        add_update('last_played', self.last_played)
        add_update('no_shows', self.no_shows)
        add_update('active_flag', self.active_flag)
        add_update('notable_items', self.notable_items)
        add_update('masterpiece', self.masterpiece)
        
        for model in (self.lifestyle, self.resources, self.skills):
            for col, val in model.get_sheet_data().items():
                add_update(col, val)
        batch_update(updates)
