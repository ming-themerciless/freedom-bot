"""The bot must not overwrite a change it never read.

`Actor` loads a snapshot of its row, the command then rolls dice and waits on
Discord, and only then does the row get written. Three other writers touch the
same rows in that window — the Guild Council by hand, the weekly living-cost
macro on column J, and Frank's interest macro on column AC (OD-07, OD-36) — and
the old whole-row write reverted whatever any of them had done.

`connectors.sheets` is replaced in `sys.modules` before it is ever imported.
The real module reads `config`, which reads `.env`, and no test in this
repository may touch credentials; `models.actor` imports it lazily inside its
methods so that the substitution is all that is needed.
"""
from __future__ import annotations

import sys
import types

import pytest


def _install_stub(monkeypatch, *, values, batch):
    module = types.ModuleType("connectors.sheets")
    module.get_values = values
    module.batch_update = batch
    monkeypatch.setitem(sys.modules, "connectors.sheets", module)
    return module


class FakeSheet:
    """A Characters tab that records reads and writes, and can be edited under us."""

    def __init__(self, rows: dict[int, list]):
        #: row number -> the row's cells, A onwards
        self.rows = rows
        self.writes: list[dict] = []
        self.reads: list[str] = []

    def get_values(self, a1_range, value_render_option="UNFORMATTED_VALUE"):
        self.reads.append(a1_range)
        _, cells = a1_range.split("!", 1)
        if cells.startswith("A3:AL"):
            last = max(self.rows) if self.rows else 2
            return [self.rows.get(number, []) for number in range(3, last + 1)]
        # A single-cell name check: "A17:A17"
        row_number = int(cells.split(":")[0][1:])
        row = self.rows.get(row_number)
        return [[row[0]]] if row else []

    def batch_update(self, updates, value_input_option="USER_ENTERED"):
        self.writes.extend(updates)

    def written_columns(self) -> set[str]:
        return {
            update["range"].split("!")[1].split(":")[0].rstrip("0123456789")
            for update in self.writes
        }

    def written_value(self, column: str):
        for update in self.writes:
            letters = update["range"].split("!")[1].split(":")[0].rstrip("0123456789")
            if letters == column:
                return update["values"][0][0]
        raise AssertionError(f"column {column} was not written")


def character_row(
    name: str,
    *,
    level: int = 5,
    downtime: float = 10.0,
    living_weeks: int = 2,
    gold: int = 50,
    debt: int = 0,
) -> list:
    """A Characters row A..AL with only the cells these tests care about set."""
    row = [""] * 38
    row[0] = name  # A  name
    row[4] = "Bronze"  # E  badge
    row[5] = level  # F  level
    row[8] = downtime  # I  downtime
    row[9] = living_weeks  # J  living weeks -- the weekly macro's column
    row[13] = "modest"  # N  lifestyle
    row[16] = gold  # Q  gold
    row[28] = debt  # AC Frank -- the interest macro's column
    row[36] = 0  # AK no shows
    row[37] = 1  # AL active
    return row


@pytest.fixture()
def sheet(monkeypatch):
    fake = FakeSheet({3: character_row("Test Smith A"), 4: character_row("Test Smith B")})
    _install_stub(monkeypatch, values=fake.get_values, batch=fake.batch_update)
    return fake


@pytest.fixture()
def actor_module(sheet):
    from models import actor as actor_module

    return actor_module


# --------------------------------------------------------------------------- #
# Only what changed is written
# --------------------------------------------------------------------------- #


def test_an_unchanged_actor_writes_nothing_at_all(sheet, actor_module):
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()

    actor.save_to_sheet()

    assert sheet.writes == []


def test_only_the_changed_cells_are_written(sheet, actor_module):
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()

    actor.resources.gold += 25

    actor.save_to_sheet()

    assert sheet.written_columns() == {"Q"}
    assert sheet.written_value("Q") == 75


def test_a_macro_accrual_during_the_command_survives_the_save(sheet, actor_module):
    """The living-cost macro adds a week to column J while the command runs.

    Under the whole-row write the save put J back to its load-time value and the
    week owed simply vanished — invisibly, because nothing compares the two.
    """
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()

    # The weekly macro fires: column J goes from 2 to 3.
    sheet.rows[3][9] = 3

    actor.resources.gold += 10
    actor.save_to_sheet()

    assert "J" not in sheet.written_columns()
    assert sheet.rows[3][9] == 3


def test_a_council_edit_to_an_unrelated_field_survives_the_save(sheet, actor_module):
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()

    # A Council member corrects the badge and the level while the command runs.
    sheet.rows[3][4] = "Silver"
    sheet.rows[3][5] = 6

    actor.resources.downtime -= 5
    actor.save_to_sheet()

    assert sheet.written_columns() == {"I"}
    assert sheet.rows[3][4] == "Silver"
    assert sheet.rows[3][5] == 6


def test_franks_interest_column_is_never_written(sheet, actor_module):
    """Column AC is macro-owned; this model reads it nowhere and writes it never."""
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()

    actor.resources.gold += 1
    actor.save_to_sheet()

    assert "AC" not in sheet.written_columns()


def test_an_actor_that_was_never_loaded_refuses_to_write(sheet, actor_module):
    actor = actor_module.Actor("Test Smith A")

    with pytest.raises(ValueError, match="was not loaded"):
        actor.sheet_updates()


# --------------------------------------------------------------------------- #
# The row is a position, not an identity
# --------------------------------------------------------------------------- #


def test_a_row_that_moved_under_the_actor_refuses_the_write(sheet, actor_module):
    """A row inserted above shifts this character down; the snapshot's row now
    belongs to somebody else, and writing to it would move one character's money
    onto another's sheet."""
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()
    actor.resources.gold += 100

    # A Council member inserts a row: everything below moves down one.
    sheet.rows = {
        3: character_row("Test Newcomer Z"),
        4: character_row("Test Smith A"),
        5: character_row("Test Smith B"),
    }

    with pytest.raises(actor_module.StaleSheetRowError):
        actor.save_to_sheet()

    assert sheet.writes == []


def test_two_characters_sharing_a_name_are_refused_rather_than_guessed(
    sheet, actor_module
):
    sheet.rows[5] = character_row("Test Smith A", gold=9999)

    actor = actor_module.Actor("Test Smith A")

    with pytest.raises(actor_module.AmbiguousActorError):
        actor.load_from_sheet()

    assert sheet.writes == []


def test_a_missing_character_still_reports_not_found(sheet, actor_module):
    actor = actor_module.Actor("Test Nobody Q")

    with pytest.raises(ValueError, match="could not be found"):
        actor.load_from_sheet()


def test_the_name_check_reads_only_the_one_cell_it_needs(sheet, actor_module):
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()
    actor.resources.gold += 1

    actor.save_to_sheet()

    assert sheet.reads[-1] == "Characters!A3:A3"


def test_a_save_that_writes_nothing_does_not_even_check_the_row(sheet, actor_module):
    """No write, no risk, no extra API call on the commonest read-only path."""
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()
    reads_after_load = len(sheet.reads)

    actor.save_to_sheet()

    assert len(sheet.reads) == reads_after_load


def test_a_second_save_writes_only_what_changed_since_the_first(sheet, actor_module):
    actor = actor_module.Actor("Test Smith A")
    actor.load_from_sheet()
    actor.resources.gold += 10
    actor.save_to_sheet()
    sheet.writes.clear()

    actor.resources.downtime -= 5
    actor.save_to_sheet()

    assert sheet.written_columns() == {"I"}


# --------------------------------------------------------------------------- #
# A trade confirms both rows before it writes either
# --------------------------------------------------------------------------- #


def test_a_trade_verifies_both_rows_before_writing_either(sheet, actor_module):
    from models.trade import Trade

    buyer = actor_module.Actor("Test Smith A")
    buyer.load_from_sheet()
    seller = actor_module.Actor("Test Smith B")
    seller.load_from_sheet()

    # The seller's row moves after both were loaded.
    sheet.rows[4] = character_row("Test Someone Else")

    from models.resource import Resource

    with pytest.raises(actor_module.StaleSheetRowError):
        Trade(buyer=buyer, seller=seller, price=Resource(gold=5)).perform_trade()

    assert sheet.writes == []


def test_a_clean_trade_writes_both_sides_in_one_batch(sheet, actor_module):
    from models.resource import Resource
    from models.trade import Trade

    buyer = actor_module.Actor("Test Smith A")
    buyer.load_from_sheet()
    seller = actor_module.Actor("Test Smith B")
    seller.load_from_sheet()

    Trade(buyer=buyer, seller=seller, price=Resource(gold=5)).perform_trade()

    ranges = {update["range"] for update in sheet.writes}
    assert ranges == {"Characters!Q3:Q3", "Characters!Q4:Q4"}
