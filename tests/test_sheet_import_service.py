"""Phase 2 acceptance: identity import is idempotent, previewable and atomic.

Every fixture here is synthetic. No live Sheet row, player name or Discord id
appears in this file.
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from adapters.sheets.character_import import parse_character_rows
from application.audit import ActorCapability, AuditSource
from application.imports import (
    ImportIssueSeverity,
    SheetCharacterImportReport,
    SheetImportAction,
    SheetRowMapping,
)
from application.sheet_import import SheetCharacterImportService
from domain.identity import Character
from tests.fakes import FakeStore, unit_of_work_factory

TAB = "Characters"


def row(name: str, *, long_name: str = "", player: str = "testplayer01", level: str = "4", active: str = "1"):
    return {
        "Character Name (short)": name,
        "Character Name (long)": long_name,
        "Player Name": player,
        "Character Level": level,
        "Active": active,
    }


def service(store: FakeStore, **kwargs) -> tuple[SheetCharacterImportService, object]:
    factory = unit_of_work_factory(store)
    return SheetCharacterImportService(factory, **kwargs), factory


def test_a_dry_run_reports_what_it_would_create_and_writes_nothing():
    store = FakeStore()
    importer, factory = service(store)

    outcome = importer.run(parse_character_rows([row("Test Smith A")]), sheet_tab=TAB)

    assert outcome.dry_run is True
    assert outcome.applied is False
    assert outcome.count(SheetImportAction.CREATED) == 1
    assert store.characters == {}
    assert store.sheet_row_mappings == []
    assert factory.units[0].committed_count == 0
    assert factory.units[0].rolled_back_count == 1


def test_applying_creates_the_character_its_mapping_and_its_audit_row():
    store = FakeStore()
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("Test Smith A", long_name="Test Smith Alpha")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert outcome.applied is True
    entry = outcome.entries[0]
    assert entry.action is SheetImportAction.CREATED
    character = store.characters[entry.character_id]
    assert character.display_name == "Test Smith A"
    assert character.long_name == "Test Smith Alpha"
    assert character.level == 4
    assert character.active is True

    mapping = store.sheet_row_mappings[0]
    assert (mapping.sheet_tab, mapping.row_index) == (TAB, 3)
    assert mapping.character_id == character.id

    event = store.audit_events[0]
    assert event.action == "sheet_import.character.created"
    assert event.entity_id == str(character.id)
    assert event.source is AuditSource.IMPORT
    assert event.actor_capability is ActorCapability.SYSTEM
    assert event.actor_discord_user_id is None
    assert event.correlation_id == outcome.correlation_id


def test_repeating_an_unchanged_import_creates_no_duplicate_and_no_audit_noise():
    store = FakeStore()
    importer, _ = service(store)
    rows = [row("Test Smith A"), row("Test Smith B")]

    importer.run(parse_character_rows(rows), sheet_tab=TAB, dry_run=False)
    second = importer.run(parse_character_rows(rows), sheet_tab=TAB, dry_run=False)

    assert second.count(SheetImportAction.UNCHANGED) == 2
    assert second.count(SheetImportAction.CREATED) == 0
    assert len(store.characters) == 2
    assert len(store.sheet_row_mappings) == 2
    assert len(store.audit_events) == 2  # from the first run only


def test_a_changed_row_updates_the_mapped_character_and_records_the_change():
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A", level="4")]),
        sheet_tab=TAB,
        dry_run=False,
    )
    character_id = first.entries[0].character_id

    second = importer.run(
        parse_character_rows([row("Test Smith A", level="5", active="0")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert second.entries[0].action is SheetImportAction.UPDATED
    assert second.entries[0].character_id == character_id
    updated = store.characters[character_id]
    assert updated.level == 5
    assert updated.active is False
    assert updated.version == 1

    change = store.audit_events[-1]
    assert change.action == "sheet_import.character.updated"
    assert change.payload["changes"] == {
        "level": {"from": 4, "to": 5},
        "active": {"from": True, "to": False},
    }


def test_a_renamed_row_never_mints_a_second_character_for_the_same_mapping():
    """The row is the import key; the name is a mutable attribute (ADR 0005).

    The mapping still resolves, so the renamed row is not a new character. What
    it is instead — an in-place rename, or a row that moved while its former
    occupant was renamed — is the thing the importer cannot know, so the run
    stops with the mapped character untouched rather than guessing either way.
    """
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False
    )
    character_id = first.entries[0].character_id

    second = importer.run(
        parse_character_rows([row("Test Smith Renamed")]), sheet_tab=TAB, dry_run=False
    )

    assert second.applied is False
    assert second.entries[0].action is SheetImportAction.BLOCKED
    assert second.entries[0].character_id == character_id
    assert len(store.characters) == 1
    assert store.characters[character_id].display_name == "Test Smith A"


def test_a_moved_row_is_blocked_rather_than_duplicated_or_silently_re_keyed():
    store = FakeStore()
    importer, _ = service(store)
    importer.run(parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False)

    # The same character now appears one row lower, so its row key is unmapped.
    moved = importer.run(
        parse_character_rows([row("Test Filler X"), row("Test Smith A")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert moved.applied is False
    assert all(e.action is SheetImportAction.BLOCKED for e in moved.entries)
    assert {issue.code for issue in moved.issues} == {
        # Row 3 now carries a different name than the character it maps to,
        # and that character is listed at row 4.
        "row_identity_shift",
        # Row 4 is unmapped and names a character the platform already holds.
        "unmapped_name_collision",
    }
    # Nothing at all was written, including the row that was individually valid.
    assert len(store.characters) == 1
    assert "Test Filler X" not in {c.display_name for c in store.characters.values()}


def test_two_characters_swapping_rows_is_blocked_on_both_rows():
    store = FakeStore()
    importer, _ = service(store)
    importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    swapped = importer.run(
        parse_character_rows([row("Test Smith B"), row("Test Smith A")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert swapped.applied is False
    assert [e.action for e in swapped.entries] == [SheetImportAction.BLOCKED] * 2
    assert {i.code for i in swapped.issues} == {"row_identity_shift"}


def test_one_blocked_row_prevents_the_whole_run_from_committing():
    store = FakeStore()
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("Test Smith A"), row("", level="bad")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert outcome.applied is False
    assert outcome.has_errors
    assert store.characters == {}
    assert store.audit_events == []


def test_parse_errors_are_carried_into_the_import_outcome():
    store = FakeStore()
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("Test Smith A", level="99")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert {issue.code for issue in outcome.issues} == {"out_of_range"}
    assert outcome.applied is False


def test_a_missing_player_warns_without_blocking_the_import():
    store = FakeStore()
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("Test Smith A", player="")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert outcome.applied is True
    assert outcome.warning_count == 1
    assert outcome.error_count == 0
    # Ownership stays a Council decision: nothing here grants access.
    assert outcome.count(SheetImportAction.CREATED) == 1


def test_a_mapped_row_absent_from_the_source_warns_and_changes_nothing():
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )
    surviving = first.entries[0].character_id

    second = importer.run(
        parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False
    )

    absent = [i for i in second.issues if i.code == "absent_from_source"]
    assert [i.row_number for i in absent] == [4]
    assert absent[0].severity is ImportIssueSeverity.WARNING
    assert second.applied is True
    assert len(store.characters) == 2  # the absent character is never removed
    assert store.characters[surviving].active is True


def test_a_dangling_mapping_is_blocked_rather_than_re_created():
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False
    )
    del store.characters[first.entries[0].character_id]

    second = importer.run(
        parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False
    )

    assert second.entries[0].action is SheetImportAction.BLOCKED
    assert any(issue.code == "dangling_mapping" for issue in second.issues)
    assert second.applied is False


def test_tabs_are_independent_import_namespaces():
    store = FakeStore()
    importer, _ = service(store)
    importer.run(parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False)

    other = importer.run(
        parse_character_rows([row("Test Smith A")]),
        sheet_tab="Retired",
        dry_run=False,
    )

    # Same name, different tab, no mapping: the collision guard still refuses
    # to mint a second character for a name the platform already holds.
    assert other.entries[0].action is SheetImportAction.BLOCKED
    assert other.applied is False


def test_an_empty_import_is_a_clean_no_op():
    store = FakeStore()
    importer, _ = service(store)

    outcome = importer.run(
        SheetCharacterImportReport(candidates=(), issues=()),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert outcome.entries == ()
    assert outcome.issues == ()
    assert outcome.applied is True


def test_a_dry_run_and_the_apply_that_follows_it_agree():
    store = FakeStore()
    importer, _ = service(store)
    report = parse_character_rows([row("Test Smith A"), row("Test Smith B")])

    preview = importer.run(report, sheet_tab=TAB)
    applied = importer.run(report, sheet_tab=TAB, dry_run=False)

    assert [(e.row_number, e.action) for e in preview.entries] == [
        (e.row_number, e.action) for e in applied.entries
    ]
    # The ids differ: a rolled-back rehearsal cannot reserve an identity.
    assert {e.character_id for e in preview.entries} != {
        e.character_id for e in applied.entries
    }


def test_each_run_carries_its_own_correlation_id():
    store = FakeStore()
    importer, _ = service(store)
    report = parse_character_rows([row("Test Smith A")])

    first = importer.run(report, sheet_tab=TAB, dry_run=False)
    second = importer.run(
        parse_character_rows([row("Test Smith A", level="5")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert first.correlation_id != second.correlation_id
    assert {event.correlation_id for event in store.audit_events} == {
        first.correlation_id,
        second.correlation_id,
    }


# --------------------------------------------------------------------------- #
# Mapped-name changes: rename or shift, and the importer must not guess.
#
# Each of these describes an edit a Council member can make to the Sheet in one
# sitting. A mapped semantic name change is *never* applied automatically: an
# in-place rename and a permutation whose displaced characters were renamed to
# fresh names produce identical input, so committing either reading is a guess,
# and the wrong guess writes one character's identity onto another with nothing
# afterwards to notice. A change of capitalisation alone is not a semantic name
# change and is still an ordinary update.
# --------------------------------------------------------------------------- #


def test_an_inserted_row_beside_a_rename_is_blocked_rather_than_committed():
    """The uncaught case: the shift check cannot see a character that was renamed.

    Row 3's mapping points at 'Test Smith A'. The Sheet now reads a new name on
    row 3 and a renamed 'Test Smith A' on row 4. Read as a rename, row 3 gives
    the existing character the newcomer's identity and row 4 mints a duplicate;
    read as an insertion, nothing has been renamed at all. Neither reading is
    provable, so the run stops.
    """
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False
    )
    original_id = first.entries[0].character_id

    shifted = importer.run(
        parse_character_rows([row("Test Newcomer Z"), row("Test Smith Renamed")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert shifted.applied is False
    assert shifted.entries[0].action is SheetImportAction.BLOCKED
    assert {issue.code for issue in shifted.issues} == {"mapped_name_change"}
    # The character kept its name, and no second character was invented for it.
    assert store.characters[original_id].display_name == "Test Smith A"
    assert len(store.characters) == 1


def test_a_rename_is_blocked_when_the_displaced_row_failed_validation():
    """A malformed row is missing from the name index, so the shift check is blind.

    Rows moved down by one and the displaced character's new row carries an
    unusable level, so 'Test Smith A' is not among the candidates at all. The
    mapped-name change on row 3 must not be reported, or later applied, as a
    rename on the strength of an index that could not see the row.
    """
    store = FakeStore()
    importer, _ = service(store)
    importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    shifted = importer.run(
        parse_character_rows(
            [
                row("Test Newcomer Z"),
                row("Test Smith A", level="not-a-level"),
                row("Test Smith B"),
            ]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert shifted.applied is False
    blocked = {entry.row_number: entry.action for entry in shifted.entries}
    assert blocked[3] is SheetImportAction.BLOCKED
    codes = {issue.code for issue in shifted.issues}
    assert "mapped_name_change" in codes
    assert {"Test Smith A", "Test Smith B"} == {
        character.display_name for character in store.characters.values()
    }


def test_several_shifted_rows_with_one_renamed_are_all_blocked():
    store = FakeStore()
    importer, _ = service(store)
    importer.run(
        parse_character_rows(
            [row("Test Smith A"), row("Test Smith B"), row("Test Smith C")]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    shifted = importer.run(
        parse_character_rows(
            [
                row("Test Newcomer Z"),
                row("Test Smith A Renamed"),
                row("Test Smith B"),
                row("Test Smith C"),
            ]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert shifted.applied is False
    assert all(
        entry.action is SheetImportAction.BLOCKED for entry in shifted.entries
    )
    assert {issue.code for issue in shifted.issues} == {
        "mapped_name_change",
        "row_identity_shift",
        "unmapped_name_collision",
    }
    assert {character.display_name for character in store.characters.values()} == {
        "Test Smith A",
        "Test Smith B",
        "Test Smith C",
    }


def test_a_rename_onto_a_name_another_character_holds_is_blocked():
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )
    renamed_id = first.entries[0].character_id

    collision = importer.run(
        parse_character_rows([row("Test Smith B"), row("Test Smith B Long")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert collision.applied is False
    assert any(issue.code == "name_collision" for issue in collision.issues)
    assert store.characters[renamed_id].display_name == "Test Smith A"


def test_a_single_mapped_name_change_is_reported_for_reconciliation():
    """The case that used to commit, and the reason it must not.

    One row's name changes and the rest of the run is spotless: no row added or
    removed, nothing malformed, no dangling mapping, no name found elsewhere and
    no collision. That reads like an in-place rename — and it is *also* exactly
    what a swap of two mapped rows looks like when both displaced characters are
    renamed to fresh names (see the permutation tests below). The importer
    reports the change and stops instead of choosing a reading.
    """
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )
    renamed_id = first.entries[0].character_id
    audit_before = list(store.audit_events)

    renamed = importer.run(
        parse_character_rows([row("Test Smith A Renamed"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert renamed.applied is False
    assert renamed.entries[0].action is SheetImportAction.BLOCKED
    assert renamed.entries[1].action is SheetImportAction.UNCHANGED
    assert [issue.code for issue in renamed.issues] == ["mapped_name_change"]
    # The refusal tells the operator what to reconcile, in both names.
    message = renamed.issues[0].message
    assert "Test Smith A" in message and "Test Smith A Renamed" in message
    assert store.characters[renamed_id].display_name == "Test Smith A"
    assert len(store.characters) == 2
    assert store.audit_events == audit_before


def test_swapped_rows_with_fresh_names_are_blocked_rather_than_crossed():
    """The permutation the six former run-level signals could not see.

    Rows 3 and 4 exchange places and both characters are renamed to names the
    platform has never held. Every signal the previous implementation consulted
    is false — no parse error, no creation, no absent mapping, no dangling
    mapping, neither old name appears elsewhere, neither new name collides — so
    it committed `Test Fresh X` onto the character at row 3 and `Test Fresh Y`
    onto the character at row 4. Read by physical row, that is exactly backwards,
    and nothing afterwards could tell: the audit rows record two renames.
    """
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )
    a_id, b_id = (entry.character_id for entry in first.entries)
    mappings_before = list(store.sheet_row_mappings)
    audit_before = list(store.audit_events)

    permuted = importer.run(
        parse_character_rows([row("Test Fresh X"), row("Test Fresh Y")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert permuted.applied is False
    assert [entry.action for entry in permuted.entries] == [
        SheetImportAction.BLOCKED,
        SheetImportAction.BLOCKED,
    ]
    assert {issue.code for issue in permuted.issues} == {"mapped_name_change"}
    # Neither identity moved, neither mapping was re-keyed, and no run that
    # wrote nothing may leave a success row behind.
    assert store.characters[a_id].display_name == "Test Smith A"
    assert store.characters[b_id].display_name == "Test Smith B"
    assert store.sheet_row_mappings == mappings_before
    assert store.audit_events == audit_before


def test_a_three_row_cycle_with_fresh_names_is_blocked_atomically():
    """The same input shape at length three: A→B→C→A, every name fresh."""
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows(
            [row("Test Smith A"), row("Test Smith B"), row("Test Smith C")]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )
    identities = {
        entry.character_id: store.characters[entry.character_id].display_name
        for entry in first.entries
    }
    mappings_before = list(store.sheet_row_mappings)
    audit_before = list(store.audit_events)

    cycled = importer.run(
        parse_character_rows(
            [row("Test Fresh X"), row("Test Fresh Y"), row("Test Fresh Z")]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert cycled.applied is False
    assert [entry.action for entry in cycled.entries] == [
        SheetImportAction.BLOCKED
    ] * 3
    assert {issue.code for issue in cycled.issues} == {"mapped_name_change"}
    assert [issue.row_number for issue in cycled.issues] == [3, 4, 5]
    assert {
        character_id: character.display_name
        for character_id, character in store.characters.items()
    } == identities
    assert store.sheet_row_mappings == mappings_before
    assert store.audit_events == audit_before


def test_two_independent_looking_renames_are_blocked_with_no_structural_signal():
    """Two changed rows, and every former `_RunStructure` signal still false.

    This is the swap test's twin: identical structure, but the two new names are
    not a permutation of anything. The importer cannot tell the two inputs apart
    — that is the whole point — so both must stop. The assertions below pin each
    former signal at false, so the test would still be meaningful if a run-level
    heuristic were ever reintroduced.
    """
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows(
            [row("Test Smith A"), row("Test Smith B"), row("Test Smith C")]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )
    before = {
        entry.character_id: store.characters[entry.character_id]
        for entry in first.entries
    }

    changed = importer.run(
        parse_character_rows(
            [row("Test Fresh X"), row("Test Smith B"), row("Test Fresh Z")]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    codes = {issue.code for issue in changed.issues}
    # No parse error, no creation, no absent mapping, no dangling mapping, no
    # detected shift and no collision: the six signals that used to decide this.
    assert codes == {"mapped_name_change"}
    assert changed.applied is False
    assert [entry.action for entry in changed.entries] == [
        SheetImportAction.BLOCKED,
        SheetImportAction.UNCHANGED,
        SheetImportAction.BLOCKED,
    ]
    assert store.characters == before


def test_the_dry_run_and_the_apply_reach_the_same_reconciliation_decision():
    """A rehearsal that refuses must be the same refusal, and still write nothing."""
    store = FakeStore()
    importer, factory = service(store)
    importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )
    committed = dict(store.characters)
    report = parse_character_rows([row("Test Fresh X"), row("Test Fresh Y")])

    preview = importer.run(report, sheet_tab=TAB)
    applied = importer.run(report, sheet_tab=TAB, dry_run=False)

    assert preview.dry_run is True and applied.dry_run is False
    assert preview.applied is False and applied.applied is False
    assert [(e.row_number, e.action, e.character_id) for e in preview.entries] == [
        (e.row_number, e.action, e.character_id) for e in applied.entries
    ]
    assert [(i.row_number, i.code, i.message) for i in preview.issues] == [
        (i.row_number, i.code, i.message) for i in applied.issues
    ]
    assert store.characters == committed
    assert [unit.committed_count for unit in factory.units[-2:]] == [0, 0]


def test_the_non_identity_fields_still_update_under_an_unchanged_name():
    """Refusing renames must not freeze the rows that carry no identity claim."""
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows(
            [row("Test Smith A", long_name="Test Smith Alpha", level="4")]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )
    character_id = first.entries[0].character_id

    second = importer.run(
        parse_character_rows(
            [
                row(
                    "Test Smith A",
                    long_name="Test Smith Alpha the Second",
                    level="5",
                    active="0",
                )
            ]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert second.applied is True
    assert second.entries[0].action is SheetImportAction.UPDATED
    updated = store.characters[character_id]
    assert updated.display_name == "Test Smith A"
    assert updated.long_name == "Test Smith Alpha the Second"
    assert updated.level == 5
    assert updated.active is False
    assert store.audit_events[-1].payload["changes"] == {
        "long_name": {
            "from": "Test Smith Alpha",
            "to": "Test Smith Alpha the Second",
        },
        "level": {"from": 4, "to": 5},
        "active": {"from": True, "to": False},
    }


def test_correcting_a_names_capitalisation_is_an_update_not_a_refusal():
    """Case is not identity: the parser and the platform both fold it away.

    A re-cased name is not a *semantic* name change under the comparison rule
    this importer documents, so it cannot be a moved row either — the folded
    name still resolves to the same character. It stays an ordinary update, and
    the run beside it still creates a new row.
    """
    store = FakeStore()
    importer, _ = service(store)
    first = importer.run(
        parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False
    )
    character_id = first.entries[0].character_id

    recased = importer.run(
        parse_character_rows([row("TEST SMITH A"), row("Test Newcomer Z")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert recased.applied is True
    assert recased.entries[0].action is SheetImportAction.UPDATED
    assert store.characters[character_id].display_name == "TEST SMITH A"


def test_repeating_an_unchanged_import_is_never_refused():
    store = FakeStore()
    importer, _ = service(store)
    rows = [row("Test Smith A"), row("Test Smith B"), row("Test Smith C")]
    importer.run(parse_character_rows(rows), sheet_tab=TAB, dry_run=False)

    repeated = importer.run(parse_character_rows(rows), sheet_tab=TAB, dry_run=False)

    assert repeated.applied is True
    assert repeated.issues == ()
    assert repeated.count(SheetImportAction.UNCHANGED) == 3
    assert len(store.audit_events) == 3  # the first run's creations only


def test_a_blocked_run_rolls_back_characters_mappings_and_audit_events():
    store = FakeStore()
    importer, _ = service(store)
    importer.run(
        parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False
    )
    committed_characters = dict(store.characters)
    committed_mappings = list(store.sheet_row_mappings)
    committed_audit = list(store.audit_events)

    blocked = importer.run(
        parse_character_rows(
            [
                row("Test Smith A"),
                row("Test Newcomer Z"),
                row("", level="unusable"),
            ]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert blocked.applied is False
    assert store.characters == committed_characters
    assert store.sheet_row_mappings == committed_mappings
    assert store.audit_events == committed_audit


def test_a_failure_part_way_through_a_run_rolls_the_whole_run_back():
    """The transaction is the unit, including when the failure is not ours.

    The operator entry point translates this into an exit code and a safe
    message; what matters here is that the store is untouched by the time it
    does, so 'nothing was written' is a fact rather than a hope.
    """
    class FailAfter:
        """Succeeds `limit` times, then fails the way a lost connection does."""

        def __init__(self, limit: int) -> None:
            self.limit = limit
            self.calls = 0

        def __call__(self):
            self.calls += 1
            if self.calls > self.limit:
                raise RuntimeError("the database went away")
            return uuid4()

    store = FakeStore()
    importer, factory = service(store, character_ids=FailAfter(1))

    with pytest.raises(RuntimeError):
        importer.run(
            parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
            sheet_tab=TAB,
            dry_run=False,
        )

    assert factory.units[-1].committed_count == 0
    assert factory.units[-1].rolled_back_count == 1
    assert store.characters == {}
    assert store.sheet_row_mappings == []
    assert store.audit_events == []


def test_a_pre_existing_unmapped_character_is_never_adopted_by_name():
    """Identity is the mapping. A same-named character is a finding, not a match."""
    store = FakeStore()
    existing = Character(id=uuid4(), display_name="Test Smith A", level=9)
    store.characters[existing.id] = existing
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("Test Smith A", level="4")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert outcome.entries[0].action is SheetImportAction.BLOCKED
    assert store.characters[existing.id].level == 9


# --------------------------------------------------------------------------- #
# Unicode normalisation: "capitalisation only" is not arbitrary case folding.
#
# The exemption above lets a re-cased name import without a human, on the
# argument that the folded name still denotes the same identity. That argument
# holds only while the fold used to *exempt* a change is no wider than the fold
# used to *find* a collision. `casefold()` is wider than capitalisation — it
# expands `ß` to `ss` — so exempting on `casefold()` while looking up on
# `lower()` let a semantic rename through the exemption and then past the
# collision check that should have caught it anyway.
#
# The policy these tests pin: capitalisation-only is the narrow relation,
# the collision key is the wide one, and every non-exact spelling change is
# looked up before anything is written.
# --------------------------------------------------------------------------- #


def seed_character(store: FakeStore, name: str, *, row_number: int | None = None):
    """Put a character into the committed store, optionally mapped to a row."""
    character = Character(id=uuid4(), display_name=name, level=4)
    store.characters[character.id] = character
    if row_number is not None:
        store.sheet_row_mappings.append(SheetRowMapping(character.id, TAB, row_number))
    return character


def test_a_sharp_s_expansion_is_a_semantic_name_change_not_a_capitalisation_fix():
    """`Test Straße` -> `Test STRASSE` changes letters, not just their case.

    `casefold()` folds both to `test strasse`, which is why treating
    `casefold()` equality as "capitalisation only" was wrong: the two names are
    not the same word re-cased, and applying the change would rewrite an
    identity on the strength of a fold nothing else in the platform agrees with.
    """
    store = FakeStore()
    mapped = seed_character(store, "Test Straße", row_number=3)
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("Test STRASSE")]), sheet_tab=TAB, dry_run=False
    )

    assert outcome.applied is False
    assert outcome.entries[0].action is SheetImportAction.BLOCKED
    assert [issue.code for issue in outcome.issues] == ["mapped_name_change"]
    assert store.characters[mapped.id].display_name == "Test Straße"
    assert store.audit_events == []


def test_a_sharp_s_expansion_never_commits_two_characters_under_one_name():
    """The reported reproduction, and the only evidence that matters.

    The platform holds `Test Straße` and `Test STRASSE` as two characters. The
    mapped `Test Straße` row now reads `Test STRASSE`. The uncorrected importer
    called that a permitted capitalisation update, skipped the collision lookup
    on the strength of it, and committed two characters holding the exact same
    display name with no blocking issue reported.
    """
    store = FakeStore()
    mapped = seed_character(store, "Test Straße", row_number=3)
    other = seed_character(store, "Test STRASSE")
    mappings_before = list(store.sheet_row_mappings)
    versions_before = {
        character_id: character.version
        for character_id, character in store.characters.items()
    }
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("Test STRASSE")]), sheet_tab=TAB, dry_run=False
    )

    assert outcome.applied is False
    assert outcome.entries[0].action is SheetImportAction.BLOCKED
    assert "name_collision" in {issue.code for issue in outcome.issues}
    # Both identities, both versions, the mapping and the audit log are as they
    # were. Two characters must never end a run holding one display name.
    assert store.characters[mapped.id].display_name == "Test Straße"
    assert store.characters[other.id].display_name == "Test STRASSE"
    assert {
        character_id: character.version
        for character_id, character in store.characters.items()
    } == versions_before
    assert store.sheet_row_mappings == mappings_before
    assert store.audit_events == []
    assert len({c.display_name for c in store.characters.values()}) == 2


def test_an_unmapped_sharp_s_variant_never_mints_a_second_character():
    """Creation uses the same collision key, so normalisation cannot fork identity."""
    store = FakeStore()
    existing = seed_character(store, "Test Straße")
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("Test STRASSE")]), sheet_tab=TAB, dry_run=False
    )

    assert outcome.applied is False
    assert [issue.code for issue in outcome.issues] == ["unmapped_name_collision"]
    assert list(store.characters) == [existing.id]
    assert store.sheet_row_mappings == []
    assert store.audit_events == []


def test_a_capitalisation_only_change_onto_a_taken_name_is_a_collision():
    """Even the permitted change is looked up first: it can still be taken.

    `Test Smith A` -> `TEST SMITH A` is capitalisation alone, but another
    character already claims that comparison identity, so applying it would
    leave two characters answering to one name.
    """
    store = FakeStore()
    mapped = seed_character(store, "Test Smith A", row_number=3)
    other = seed_character(store, "test smith a")
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("TEST SMITH A")]), sheet_tab=TAB, dry_run=False
    )

    assert outcome.applied is False
    assert outcome.entries[0].action is SheetImportAction.BLOCKED
    assert [issue.code for issue in outcome.issues] == ["name_collision"]
    assert str(other.id) in outcome.issues[0].message
    assert store.characters[mapped.id].display_name == "Test Smith A"
    assert store.characters[other.id].display_name == "test smith a"
    assert store.audit_events == []


def test_a_capitalisation_only_change_applies_when_nobody_else_claims_the_name():
    """The permitted case, stated against the collision lookup rather than around it."""
    store = FakeStore()
    mapped = seed_character(store, "Test Smith A", row_number=3)
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows([row("TEST SMITH A")]), sheet_tab=TAB, dry_run=False
    )

    assert outcome.applied is True
    assert outcome.entries[0].action is SheetImportAction.UPDATED
    assert store.characters[mapped.id].display_name == "TEST SMITH A"
    assert store.audit_events[-1].payload["changes"]["display_name"] == {
        "from": "Test Smith A",
        "to": "TEST SMITH A",
    }


def test_an_exact_non_ascii_name_is_unchanged_and_idempotent():
    """An unchanged non-ASCII name costs no lookup and produces no issue."""
    store = FakeStore()
    mapped = seed_character(store, "Test Straße", row_number=3)
    importer, _ = service(store)

    first = importer.run(
        parse_character_rows([row("Test Straße")]), sheet_tab=TAB, dry_run=False
    )
    second = importer.run(
        parse_character_rows([row("Test Straße")]), sheet_tab=TAB, dry_run=False
    )

    assert (first.applied, second.applied) == (True, True)
    assert first.entries[0].action is SheetImportAction.UNCHANGED
    assert second.entries[0].action is SheetImportAction.UNCHANGED
    assert first.issues == () and second.issues == ()
    assert store.characters[mapped.id].display_name == "Test Straße"
    assert store.audit_events == []


def test_the_dry_run_and_the_apply_agree_on_a_normalisation_refusal():
    """A rehearsal that refuses a normalisation change refuses it identically."""
    store = FakeStore()
    seed_character(store, "Test Straße", row_number=3)
    seed_character(store, "Test STRASSE")
    committed = dict(store.characters)
    importer, factory = service(store)
    report = parse_character_rows([row("Test STRASSE")])

    preview = importer.run(report, sheet_tab=TAB)
    applied = importer.run(report, sheet_tab=TAB, dry_run=False)

    assert preview.dry_run is True and applied.dry_run is False
    assert preview.applied is False and applied.applied is False
    assert [(e.row_number, e.action, e.character_id) for e in preview.entries] == [
        (e.row_number, e.action, e.character_id) for e in applied.entries
    ]
    assert [(i.row_number, i.code, i.message) for i in preview.issues] == [
        (i.row_number, i.code, i.message) for i in applied.issues
    ]
    assert store.characters == committed
    assert [unit.committed_count for unit in factory.units[-2:]] == [0, 0]


def test_a_valid_update_beside_a_normalisation_refusal_rolls_back_with_it():
    """One refusal rolls back the whole run: characters, mappings, versions, audit.

    Row 3 is an ordinary non-identity update that would commit on its own, row 4
    is the normalisation refusal, and row 5 is a creation. Nothing survives.
    """
    store = FakeStore()
    ordinary = seed_character(store, "Test Smith A", row_number=3)
    sharp = seed_character(store, "Test Straße", row_number=4)
    seed_character(store, "Test STRASSE")
    characters_before = dict(store.characters)
    mappings_before = list(store.sheet_row_mappings)
    importer, _ = service(store)

    outcome = importer.run(
        parse_character_rows(
            [
                row("Test Smith A", long_name="Test Smith Alpha", level="7"),
                row("Test STRASSE"),
                row("Test Newcomer Z"),
            ]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert outcome.applied is False
    assert outcome.entries[0].action is SheetImportAction.UPDATED
    assert outcome.entries[1].action is SheetImportAction.BLOCKED
    assert outcome.entries[2].action is SheetImportAction.CREATED
    assert store.characters == characters_before
    assert store.characters[ordinary.id].level == 4
    assert store.characters[ordinary.id].version == 0
    assert store.characters[sharp.id].display_name == "Test Straße"
    assert store.sheet_row_mappings == mappings_before
    assert store.audit_events == []
