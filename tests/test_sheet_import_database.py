"""The identity import against real PostgreSQL and the real migration.

The fake-repository suite in `test_sheet_import_service.py` proves the decisions
the importer makes. This one proves they survive the schema: that a dry run
leaves an empty database, that a second run finds nothing to do, and that a run
which must be refused leaves no half-import behind.

Every row here is synthetic.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text

from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from adapters.sheets.character_import import parse_character_rows
from application.imports import SheetImportAction, SheetRowMapping
from application.sheet_import import SheetCharacterImportService
from domain.identity import Character
from tests.display_name_cases import CASES, NameCase

pytestmark = pytest.mark.database

TAB = "Characters"


def row(name: str, *, level: str = "4", active: str = "1"):
    return {
        "Character Name (short)": name,
        "Character Name (long)": f"{name} the Synthetic",
        "Player Name": "testplayer01",
        "Character Level": level,
        "Active": active,
    }


@pytest.fixture()
def importer(committed_database) -> SheetCharacterImportService:
    return SheetCharacterImportService(lambda: SqlAlchemyUnitOfWork(committed_database))


def counts(engine) -> dict[str, int]:
    with engine.connect() as connection:
        return {
            table: connection.execute(
                text(f"SELECT count(*) FROM {table}")  # noqa: S608 - fixed table names
            ).scalar_one()
            for table in ("characters", "sheet_row_mappings", "audit_events")
        }


def test_a_dry_run_against_postgresql_writes_nothing(importer, committed_database):
    outcome = importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
    )

    assert outcome.count(SheetImportAction.CREATED) == 2
    assert outcome.applied is False
    assert counts(committed_database) == {
        "characters": 0,
        "sheet_row_mappings": 0,
        "audit_events": 0,
    }


def test_applying_then_repeating_the_import_creates_no_duplicates(
    importer, committed_database
):
    rows = [row("Test Smith A"), row("Test Smith B"), row("Test Smith C")]

    first = importer.run(parse_character_rows(rows), sheet_tab=TAB, dry_run=False)
    second = importer.run(parse_character_rows(rows), sheet_tab=TAB, dry_run=False)

    assert first.count(SheetImportAction.CREATED) == 3
    assert second.count(SheetImportAction.UNCHANGED) == 3
    assert counts(committed_database) == {
        "characters": 3,
        "sheet_row_mappings": 3,
        "audit_events": 3,
    }


def test_a_refused_run_leaves_no_partially_imported_row(importer, committed_database):
    """The valid rows of a blocked run must not commit on their own."""
    importer.run(parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False)
    before = counts(committed_database)

    refused = importer.run(
        parse_character_rows(
            # Row 3 keeps its mapping; rows 4 and 5 are new and individually valid;
            # row 6 is malformed and blocks the run.
            [row("Test Smith A"), row("Test Smith B"), row("Test Smith C"), row("Test Smith D", level="nine")]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert refused.applied is False
    # The malformed row never became a candidate; the two new valid ones were
    # planned in full, and still did not reach the database.
    assert refused.count(SheetImportAction.CREATED) == 2
    assert counts(committed_database) == before


def test_a_refused_name_change_leaves_the_database_exactly_as_it_was(
    importer, committed_database
):
    """A row inserted beside a name change: nothing commits, including the newcomer.

    The fake-repository suite proves the decision; this proves the rollback is
    the database's, so an operator who sees "Nothing was written" is reading a
    fact about PostgreSQL rather than about a model of it.
    """
    importer.run(
        parse_character_rows([row("Test Smith A")]), sheet_tab=TAB, dry_run=False
    )
    before = counts(committed_database)

    refused = importer.run(
        parse_character_rows([row("Test Newcomer Z"), row("Test Smith Renamed")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert refused.applied is False
    assert {issue.code for issue in refused.issues} == {"mapped_name_change"}
    assert counts(committed_database) == before
    with committed_database.connect() as connection:
        names = connection.execute(text("SELECT display_name FROM characters")).scalars().all()
    assert names == ["Test Smith A"]


def test_a_fresh_name_permutation_rolls_back_characters_mappings_and_audit(
    importer, committed_database
):
    """The identity-crossing case, refused through the real schema.

    Two mapped rows exchange places and both characters are renamed to names the
    platform has never held. Nothing in the input distinguishes that from two
    in-place renames, so the run must stop — and every effect of it, in all three
    tables, must go with it. The mapping rows are checked by `(row_index,
    character_id)` pair rather than by count, because a silent re-key would keep
    the count identical while crossing the two identities.
    """
    first = importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )
    before = counts(committed_database)

    def identity_state() -> tuple[tuple, ...]:
        with committed_database.connect() as connection:
            return tuple(
                connection.execute(
                    text(
                        "SELECT m.row_index, c.id, c.display_name, c.version "
                        "FROM sheet_row_mappings m "
                        "JOIN characters c ON c.id = m.character_id "
                        "WHERE m.sheet_tab = :tab ORDER BY m.row_index"
                    ),
                    {"tab": TAB},
                ).all()
            )

    committed_identities = identity_state()
    assert [state.display_name for state in committed_identities] == [
        "Test Smith A",
        "Test Smith B",
    ]

    permuted = importer.run(
        parse_character_rows([row("Test Fresh X"), row("Test Fresh Y")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert permuted.applied is False
    assert {issue.code for issue in permuted.issues} == {"mapped_name_change"}
    assert [issue.row_number for issue in permuted.issues] == [3, 4]
    assert counts(committed_database) == before
    assert identity_state() == committed_identities
    # No success audit row from the refused run: the audit table still holds
    # only the two creations from the run that did commit.
    with committed_database.connect() as connection:
        correlation_ids = connection.execute(
            text("SELECT DISTINCT correlation_id FROM audit_events")
        ).scalars().all()
    assert correlation_ids == [first.correlation_id]


# --------------------------------------------------------------------------- #
# Unicode normalisation, against the real schema and the real adapter.
#
# The application suite proves these decisions against fakes. None of that is
# evidence about PostgreSQL: the defect being closed here existed *because* the
# adapter compared names with SQL `lower()` while the service exempted changes
# with Python `casefold()`, and a fake repository agreed with neither. So the
# cases below run the whole path — parser, service, SQLAlchemy adapter,
# migrated schema, real transaction.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("case", CASES, ids=[case.label for case in CASES])
def test_the_postgresql_repository_matches_the_shared_display_name_policy(
    committed_database, case: NameCase
):
    """The adapter answers for the whole comparison domain, not the SQL part of it.

    `func.lower()` cannot express this: PostgreSQL leaves `ß` alone, so the
    sharp-s rows below would return nothing and the caller would be told a
    claimed name is free.
    """
    stored = Character(id=uuid4(), display_name=case.stored, level=4)
    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(stored)
        unit_of_work.commit()

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        found = unit_of_work.characters.find_by_display_name(case.imported)

    assert bool(found) is case.claims_same_identity
    if case.claims_same_identity:
        assert [character.id for character in found] == [stored.id]
        assert found[0].display_name == case.stored


def test_a_sharp_s_expansion_never_commits_two_characters_under_one_name(
    importer, committed_database
):
    """The reported reproduction, through the migrated schema.

    The database holds `Test Straße` mapped to row 3 and `Test STRASSE`
    unmapped. Row 3 now reads `Test STRASSE`. The uncorrected importer called
    that a permitted capitalisation update, skipped the collision lookup, and
    committed two rows of `characters` with an identical `display_name`.
    """
    mapped = Character(id=uuid4(), display_name="Test Straße", level=4)
    other = Character(id=uuid4(), display_name="Test STRASSE", level=4)
    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(mapped)
        unit_of_work.characters.add(other)
        unit_of_work.sheet_row_mappings.add(SheetRowMapping(mapped.id, TAB, 3))
        unit_of_work.commit()
    before = counts(committed_database)

    refused = importer.run(
        parse_character_rows([row("Test STRASSE")]), sheet_tab=TAB, dry_run=False
    )

    assert refused.applied is False
    assert "name_collision" in {issue.code for issue in refused.issues}
    assert counts(committed_database) == before
    with committed_database.connect() as connection:
        identities = connection.execute(
            text("SELECT id, display_name, version FROM characters ORDER BY display_name")
        ).all()
        mappings = connection.execute(
            text(
                "SELECT character_id, row_index FROM sheet_row_mappings "
                "WHERE sheet_tab = :tab ORDER BY row_index"
            ),
            {"tab": TAB},
        ).all()
    assert [(state.display_name, state.version) for state in identities] == [
        ("Test STRASSE", 0),
        ("Test Straße", 0),
    ]
    assert [(m.character_id, m.row_index) for m in mappings] == [(mapped.id, 3)]


def test_a_capitalisation_only_change_onto_a_taken_name_is_refused_by_postgresql(
    importer, committed_database
):
    """The permitted change is still looked up, and PostgreSQL sees the holder."""
    mapped = Character(id=uuid4(), display_name="Test Smith A", level=4)
    other = Character(id=uuid4(), display_name="test smith a", level=4)
    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(mapped)
        unit_of_work.characters.add(other)
        unit_of_work.sheet_row_mappings.add(SheetRowMapping(mapped.id, TAB, 3))
        unit_of_work.commit()
    before = counts(committed_database)

    refused = importer.run(
        parse_character_rows([row("TEST SMITH A")]), sheet_tab=TAB, dry_run=False
    )

    assert refused.applied is False
    assert [issue.code for issue in refused.issues] == ["name_collision"]
    assert counts(committed_database) == before
    with committed_database.connect() as connection:
        names = connection.execute(
            text("SELECT display_name FROM characters ORDER BY display_name")
        ).scalars().all()
    assert names == ["Test Smith A", "test smith a"]


def test_an_unmapped_sharp_s_variant_creates_no_second_character_in_postgresql(
    importer, committed_database
):
    """Creation uses the same key, so a normalisation disagreement cannot fork identity."""
    existing = Character(id=uuid4(), display_name="Test Straße", level=4)
    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(existing)
        unit_of_work.commit()
    before = counts(committed_database)

    refused = importer.run(
        parse_character_rows([row("Test STRASSE")]), sheet_tab=TAB, dry_run=False
    )

    assert refused.applied is False
    assert [issue.code for issue in refused.issues] == ["unmapped_name_collision"]
    assert counts(committed_database) == before
    assert before == {"characters": 1, "sheet_row_mappings": 0, "audit_events": 0}


def test_a_valid_update_beside_a_normalisation_refusal_rolls_back_in_postgresql(
    importer, committed_database
):
    """A mixed run: one real update, one normalisation refusal, one creation.

    All three effects — the character row, its version, its mapping and the
    audit event — go back together. The mapping rows are compared as
    `(row_index, character_id)` pairs rather than by count, because a silent
    re-key would leave the count identical.
    """
    ordinary = Character(id=uuid4(), display_name="Test Smith A", level=4)
    sharp = Character(id=uuid4(), display_name="Test Straße", level=4)
    other = Character(id=uuid4(), display_name="Test STRASSE", level=4)
    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        for character in (ordinary, sharp, other):
            unit_of_work.characters.add(character)
        unit_of_work.sheet_row_mappings.add(SheetRowMapping(ordinary.id, TAB, 3))
        unit_of_work.sheet_row_mappings.add(SheetRowMapping(sharp.id, TAB, 4))
        unit_of_work.commit()
    before = counts(committed_database)

    def identity_state() -> tuple[tuple, ...]:
        with committed_database.connect() as connection:
            return tuple(
                connection.execute(
                    text(
                        "SELECT c.id, c.display_name, c.level, c.version, m.row_index "
                        "FROM characters c "
                        "LEFT JOIN sheet_row_mappings m ON m.character_id = c.id "
                        "ORDER BY c.display_name"
                    )
                ).all()
            )

    committed_identities = identity_state()

    refused = importer.run(
        parse_character_rows(
            [row("Test Smith A", level="7"), row("Test STRASSE"), row("Test Newcomer Z")]
        ),
        sheet_tab=TAB,
        dry_run=False,
    )

    assert refused.applied is False
    assert refused.count(SheetImportAction.UPDATED) == 1
    assert refused.count(SheetImportAction.CREATED) == 1
    assert refused.count(SheetImportAction.BLOCKED) == 1
    assert counts(committed_database) == before
    assert identity_state() == committed_identities


def test_the_dry_run_and_the_apply_agree_on_a_normalisation_refusal_in_postgresql(
    importer, committed_database
):
    """A rehearsal that refuses must refuse identically, and still write nothing."""
    mapped = Character(id=uuid4(), display_name="Test Straße", level=4)
    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(mapped)
        unit_of_work.sheet_row_mappings.add(SheetRowMapping(mapped.id, TAB, 3))
        unit_of_work.commit()
    before = counts(committed_database)
    report = parse_character_rows([row("Test STRASSE")])

    preview = importer.run(report, sheet_tab=TAB)
    applied = importer.run(report, sheet_tab=TAB, dry_run=False)

    assert preview.applied is False and applied.applied is False
    assert [(i.row_number, i.code, i.message) for i in preview.issues] == [
        (i.row_number, i.code, i.message) for i in applied.issues
    ]
    assert {issue.code for issue in applied.issues} == {"mapped_name_change"}
    assert counts(committed_database) == before


def test_a_second_import_updates_the_mapped_character_in_place(
    importer, committed_database
):
    first = importer.run(
        parse_character_rows([row("Test Smith A", level="4")]),
        sheet_tab=TAB,
        dry_run=False,
    )
    character_id = first.entries[0].character_id

    importer.run(
        parse_character_rows([row("Test Smith A", level="5", active="0")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        character = unit_of_work.characters.get(character_id)
    assert (character.level, character.active, character.version) == (5, False, 1)
    assert counts(committed_database)["characters"] == 1


def test_the_audit_trail_ties_one_run_together_by_correlation_id(
    importer, committed_database
):
    outcome = importer.run(
        parse_character_rows([row("Test Smith A"), row("Test Smith B")]),
        sheet_tab=TAB,
        dry_run=False,
    )

    with committed_database.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT entity_id, action, source, actor_capability, payload "
                "FROM audit_events WHERE correlation_id = :correlation_id"
            ),
            {"correlation_id": outcome.correlation_id},
        ).all()

    assert len(rows) == 2
    assert {r.action for r in rows} == {"sheet_import.character.created"}
    assert {r.source for r in rows} == {"import"}
    assert {r.actor_capability for r in rows} == {"system"}
    assert {r.entity_id for r in rows} == {
        str(entry.character_id) for entry in outcome.entries
    }
    assert {r.payload["row_index"] for r in rows} == {3, 4}
