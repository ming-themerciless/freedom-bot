"""The display-name comparison rule, and every layer that has to agree with it.

The Phase 2 normalisation defect was not a wrong fold. It was two folds: the
import service exempted a mapped-name change as "capitalisation only" using
`casefold()`, and the repositories looked collisions up using `lower()`. Each
was defensible alone; together they let `Test Straße` be imported as
`Test STRASSE` as a permitted re-capitalisation, skip the collision lookup on
the strength of that, and commit two characters holding one display name.

So these tests assert the rule and then assert that the parser, the fake
repository and the import service reach it by the same route. The PostgreSQL
repository is held to the same table in `test_sheet_import_database.py`, where a
real database is available.

Every name here is synthetic.
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from adapters.sheets.character_import import parse_character_rows
from application.imports import SheetImportAction, SheetRowMapping
from application.sheet_import import SheetCharacterImportService
from domain.identity import Character
from domain.names import DisplayName
from tests.display_name_cases import CASES, NameCase
from tests.fakes import FakeStore, unit_of_work_factory

TAB = "Characters"

IDS = [case.label for case in CASES]


def row(name: str, *, player: str = "testplayer01"):
    return {
        "Character Name (short)": name,
        "Character Name (long)": "",
        "Player Name": player,
        "Character Level": "4",
        "Active": "1",
    }


# --------------------------------------------------------------------------- #
# The rule itself.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_the_policy_classifies_every_case_as_the_table_says(case: NameCase):
    stored = DisplayName(case.stored)
    imported = DisplayName(case.imported)

    assert imported.is_exactly(stored) is case.is_exact
    assert (
        imported.differs_only_in_capitalization(stored) is case.is_capitalization_only
    )
    assert imported.is_semantic_change_from(stored) is case.is_semantic
    assert imported.claims_same_identity_as(stored) is case.claims_same_identity


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_the_three_relations_are_mutually_exclusive_and_exhaustive(case: NameCase):
    """Exactly one of exact, capitalisation-only and semantic holds."""
    stored = DisplayName(case.stored)
    imported = DisplayName(case.imported)

    held = [
        imported.is_exactly(stored),
        imported.differs_only_in_capitalization(stored),
        imported.is_semantic_change_from(stored),
    ]
    assert held.count(True) == 1


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_nothing_identity_neutral_escapes_the_collision_key(case: NameCase):
    """The containment the whole correction rests on.

    An exact match and a capitalisation-only change are the two changes the
    importer may apply without a human. Both must be visible to the collision
    lookup, or a change could be exempted from the identity refusal *and* skip
    the check that would have caught it — which is the reported defect.
    """
    stored = DisplayName(case.stored)
    imported = DisplayName(case.imported)

    if imported.is_exactly(stored) or imported.differs_only_in_capitalization(stored):
        assert imported.claims_same_identity_as(stored)


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_every_relation_is_symmetric(case: NameCase):
    """Which name is the stored one must not change the answer."""
    stored = DisplayName(case.stored)
    imported = DisplayName(case.imported)

    assert imported.is_exactly(stored) is stored.is_exactly(imported)
    assert imported.claims_same_identity_as(
        stored
    ) is stored.claims_same_identity_as(imported)
    assert imported.differs_only_in_capitalization(
        stored
    ) is stored.differs_only_in_capitalization(imported)


def test_the_capitalisation_fold_is_narrower_than_the_identity_fold():
    """Stated once, directly: the two folds are deliberately different.

    `casefold()` expands `ß` into `ss`; `lower()` does not. The wide fold claims
    identities, so a false collision costs a reconciliation. The narrow fold
    exempts changes from review, so a false exemption costs a character its
    identity. They must not be swapped.
    """
    sharp = DisplayName("Test Straße")
    expanded = DisplayName("Test STRASSE")

    assert sharp.claims_same_identity_as(expanded)
    assert not sharp.differs_only_in_capitalization(expanded)
    assert expanded.is_semantic_change_from(sharp)


def test_a_name_is_never_rewritten_by_being_compared():
    """The value object decides; it does not normalise what is stored."""
    raw = "Test Ölrún"

    assert DisplayName(raw).raw == raw
    assert Character(id=uuid4(), display_name=raw).name.raw == raw


# --------------------------------------------------------------------------- #
# The layers, against the same table.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_the_parser_reports_a_duplicate_exactly_when_the_names_claim_one_identity(
    case: NameCase,
):
    report = parse_character_rows([row(case.stored), row(case.imported, player="p2")])

    duplicates = [issue for issue in report.issues if issue.code == "duplicate"]
    assert bool(duplicates) is case.claims_same_identity
    if case.claims_same_identity:
        assert duplicates[0].row_number == 4
        assert [candidate.row_number for candidate in report.candidates] == [3]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_the_fake_repository_matches_exactly_when_the_names_claim_one_identity(
    case: NameCase,
):
    store = FakeStore()
    stored = Character(id=uuid4(), display_name=case.stored, level=4)
    store.characters[stored.id] = stored
    unit = unit_of_work_factory(store)()

    with unit:
        found = unit.characters.find_by_display_name(case.imported)

    assert bool(found) is case.claims_same_identity
    if case.claims_same_identity:
        assert [character.id for character in found] == [stored.id]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_the_import_service_decides_each_case_the_way_the_table_classifies_it(
    case: NameCase,
):
    """One mapped row, nobody else holding the name: the relation alone decides.

    `exact` is idempotent, `capitalization` applies as an update, and `semantic`
    stops the run with the stored identity untouched.
    """
    store = FakeStore()
    stored = Character(id=uuid4(), display_name=case.stored, level=4)
    store.characters[stored.id] = stored
    store.sheet_row_mappings.append(SheetRowMapping(stored.id, TAB, 3))
    importer = SheetCharacterImportService(unit_of_work_factory(store))

    outcome = importer.run(
        parse_character_rows([row(case.imported)]), sheet_tab=TAB, dry_run=False
    )

    entry = outcome.entries[0]
    if case.is_exact:
        assert (outcome.applied, entry.action) == (True, SheetImportAction.UNCHANGED)
        assert store.characters[stored.id].display_name == case.stored
    elif case.is_capitalization_only:
        assert (outcome.applied, entry.action) == (True, SheetImportAction.UPDATED)
        assert store.characters[stored.id].display_name == case.imported
    else:
        assert (outcome.applied, entry.action) == (False, SheetImportAction.BLOCKED)
        assert {issue.code for issue in outcome.issues} == {"mapped_name_change"}
        assert store.characters[stored.id].display_name == case.stored
        assert store.audit_events == []
