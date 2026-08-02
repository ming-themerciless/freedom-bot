from __future__ import annotations
from typing import Any, Dict
from helpers.utils import safe_int, safe_number, col_to_index
from .resource import Resource
from .lifestyle import Lifestyle
from .skills import Skills
from models.item import Item

#: The tab every read and write in this module addresses.
SHEET_TAB = "Characters"

#: Sentinel for "this field had no value when the row was loaded", so that an
#: Actor which was never loaded still writes every managed cell.
_NOT_LOADED = object()


class StaleSheetRowError(ValueError):
    """The Sheet row this Actor was loaded from no longer holds this character.

    A `ValueError` so that the commands, which already report `ValueError` as a
    safe ephemeral message, refuse the action instead of writing one character's
    state onto another's row.
    """


class AmbiguousActorError(ValueError):
    """More than one row carries this character's name."""


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
        #: The managed cells exactly as this row read at load time. `sheet_updates`
        #: diffs against it so a command writes only what it changed.
        self._loaded_cells: Dict[str, Any] = {}

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
        from connectors.sheets import get_values

        rows = get_values(f"{SHEET_TAB}!A3:AL150", value_render_option="UNFORMATTED_VALUE")
        wanted = str(self.name).strip().lower()
        matches = [
            (idx, row)
            for idx, row in enumerate(rows, start=3)
            if len(row) > 0 and str(row[0]).strip().lower() == wanted
        ]
        if not matches:
            raise ValueError(f"Actor '{self.name}' could not be found in the records.")
        if len(matches) > 1:
            # First-match-wins would pick a row arbitrarily and then write to it.
            # Which character that is cannot be determined from a name, so the
            # command refuses rather than mutating a coin flip.
            raise AmbiguousActorError(
                f"More than one character is recorded under '{self.name}' "
                f"(rows {', '.join(str(index) for index, _ in matches)}). "
                "Please ask the Guild Council to resolve the duplicate."
            )

        idx, row = matches[0]
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
        self._loaded_cells = self._managed_cells()

    def _managed_cells(self) -> Dict[str, Any]:
        """Every managed field's current value, keyed as `COLUMNS` is.

        This is the whole of what this model owns on the row. Cells outside it —
        the player name, the Foundry-side character mechanics, and Frank's
        interest in column AC — are read by nobody here and written by nobody
        here, and stay that way.
        """
        cells: Dict[str, Any] = {
            'name': self.name,
            'inspiration': self.inspiration,
            'badge': self.badge,
            'level': self.level,
            'missions': self.missions,
            'last_played': self.last_played,
            'no_shows': self.no_shows,
            'active_flag': self.active_flag,
            'notable_items': Item.serialize_notable_items(self.items),
            'masterpiece': self.masterpiece,
        }
        for model in (self.lifestyle, self.resources, self.skills):
            cells.update(model.get_sheet_data())
        return cells

    def sheet_updates(self):
        """The cells this Actor changed since it was loaded.

        Writing every managed cell back was a lost update waiting to happen: the
        row is written from a snapshot taken before the command ran its dice
        rolls and Discord round trips, so anything another writer changed in
        between was silently reverted. There are three other writers — the Guild
        Council by hand, the weekly living-cost macro on column J, and Frank's
        interest macro on column AC (OD-07, OD-36) — and none of them can be
        asked to wait.

        Writing only what changed does not make the read-modify-write atomic;
        the Sheets API has no compare-and-set. It removes the whole class of
        losses where the two writers touched *different* fields, which is nearly
        all of them, and leaves a genuinely contended single cell as the
        remaining case. See `docs/review/phase-2-submission.md`.
        """
        if self.row_index is None:
            raise ValueError(f"Actor '{self.name}' was not loaded from the sheet; row unknown.")
        cells = self._managed_cells()
        self.notable_items = cells['notable_items']

        updates = []
        for key, value in cells.items():
            if self._loaded_cells.get(key, _NOT_LOADED) == value:
                continue
            column = self.COLUMNS[key]
            updates.append({
                "range": f"{SHEET_TAB}!{column}{self.row_index}:{column}{self.row_index}",
                "values": [[value]]
            })
        return updates

    def verify_sheet_row(self):
        """Confirm the row still holds this character, immediately before writing.

        `row_index` is a position, and a position is not an identity: inserting
        or deleting a row above this one moves every row below it, so a snapshot
        taken at load time can address a different character by the time the
        command finishes. One single-cell read closes that window to the width
        of a single API call, and fails closed if it has already moved.
        """
        from connectors.sheets import get_values

        if self.row_index is None:
            raise ValueError(f"Actor '{self.name}' was not loaded from the sheet; row unknown.")
        cell = f"{SHEET_TAB}!A{self.row_index}:A{self.row_index}"
        rows = get_values(cell, value_render_option="UNFORMATTED_VALUE")
        found = str(rows[0][0]).strip() if rows and rows[0] else ""
        if found.lower() != str(self.name).strip().lower():
            raise StaleSheetRowError(
                "The records moved while this action was in progress, so nothing "
                "was changed. Please try again."
            )

    def save_to_sheet(self):
        from connectors.sheets import batch_update

        updates = self.sheet_updates()
        if not updates:
            return
        self.verify_sheet_row()
        batch_update(updates)
        self._loaded_cells = self._managed_cells()
