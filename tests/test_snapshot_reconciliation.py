"""Reconciliation reports; it never writes, never deletes and never guesses.

Two properties carry most of the weight here after the ADR 0008 rejection:

- a field with no accepted typed authority is **reported and never compared**,
  so the report can say "Foundry holds this, the platform holds nothing, and
  package X owns the migration" without ever claiming agreement; and
- an ambiguous name-based candidate lookup **fails closed**, because under
  OD-42 a display name is not an identity and several characters may share one.
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from application.foundry.reconciliation import ActorOutcome, IssueSeverity
from domain.foundry_profile import PROFILE
from domain.snapshot_values import ComparisonOutcome
from tests import foundry_fixtures as fx
from tests import snapshot_harness as harness

FIXTURE_NAME = harness.FIXTURE_DISPLAY_NAME


def preview(bench, document=None, *, request_key="req-1", **kwargs):
    return bench.imports.preview(
        bench.artifact(document), request_key=request_key, **kwargs
    )


def issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


# -- every Actor is accounted for ----------------------------------------------


def test_every_actor_is_mapped_a_create_candidate_or_explicitly_unresolved():
    """Threshold T-4, asserted as a total rather than as three separate cases."""
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)
    document = fx.bundle(
        actors=(
            fx.actor(fx.FIRST_ACTOR_ID),
            fx.actor(fx.SECOND_ACTOR_ID, name="Unmapped Newcomer"),
        )
    )

    report = preview(bench, document).report

    assert len(report.entries) == 2
    assert (
        report.count(ActorOutcome.MAPPED)
        + report.count(ActorOutcome.UNMAPPED)
        + report.count(ActorOutcome.BLOCKED)
        == len(report.entries)
    )
    assert all(entry.outcome is not None for entry in report.entries)


def test_an_unmapped_actor_is_a_create_candidate_not_a_name_match():
    bench = harness.build()

    report = preview(bench).report

    assert report.count(ActorOutcome.UNMAPPED) == 1
    assert not report.blocked
    assert report.entries[0].character_id is None


def test_a_mapped_actor_that_agrees_produces_no_warning():
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    report = preview(bench).report

    assert report.count(ActorOutcome.MAPPED) == 1
    assert report.error_count == 0
    assert "foundry_out_of_date" not in issue_codes(report)


def test_the_report_is_deterministic():
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    first = preview(bench).report.summary()
    second = preview(bench).report.summary()

    assert first == second


# -- deferred authority --------------------------------------------------------


def test_a_legacy_field_reports_deferred_authority_and_its_owning_package():
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    entry = preview(bench).report.entries[0]

    deferred = {row.field_key: row.owning_package for row in entry.deferred}
    assert deferred["character.race"] == "5.1"
    assert deferred["wallet.balance_copper"] == "5.2"
    assert deferred["inventory.magic_items"] == "5.6a"
    assert set(deferred) == set(PROFILE.owning_packages())


def test_a_legacy_field_is_never_reported_as_matching_or_differing():
    """The load-bearing negative. A deferred row carries no verdict at all."""
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    entry = preview(bench).report.entries[0]

    compared = {comparison.field_key for comparison in entry.comparisons}
    deferred = {row.field_key for row in entry.deferred}

    assert compared & deferred == set()
    assert compared == {"character.display_name"}
    # There is no `result` on a deferred row to misread as agreement.
    for row in entry.deferred:
        assert not hasattr(row, "result")
        assert not hasattr(row, "outcome")


def test_a_deferred_field_says_whether_foundry_holds_a_value_but_not_what():
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    entry = preview(bench).report.entries[0]
    race = next(row for row in entry.deferred if row.field_key == "character.race")

    assert race.snapshot_has_value is True
    # The Actor's actual race is "Synthetic Human"; the row must not carry it.
    assert "Synthetic" not in repr(race)


def test_the_deferred_warning_names_the_owning_package():
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    report = preview(bench).report
    warnings = [i for i in report.issues if i.code == "legacy_authority_deferred"]

    assert warnings
    assert all(w.severity is IssueSeverity.WARNING for w in warnings)
    assert any("package 5.1" in w.message for w in warnings)
    # Deferral is never a reason to refuse an import.
    assert not report.blocked


# -- the one comparable field --------------------------------------------------


def test_a_renamed_actor_under_a_stable_id_stays_the_same_character():
    bench = harness.build()
    character = bench.add_character("Old Name", actor_id=fx.FIRST_ACTOR_ID)
    document = fx.bundle(actors=(fx.actor(name="Brand New Name"),))

    report = preview(bench, document).report
    entry = report.entries[0]

    assert entry.outcome is ActorOutcome.MAPPED
    assert entry.character_id == character.id
    # The rename is a real, comparable difference: the platform wrote that
    # display name itself, so it has something to disagree with.
    assert "character.display_name" in {c.field_key for c in entry.differences}


def test_a_matching_display_name_produces_no_difference():
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    entry = preview(bench).report.entries[0]
    comparison = next(
        c for c in entry.comparisons if c.field_key == "character.display_name"
    )

    assert comparison.result.outcome is ComparisonOutcome.MATCH
    assert entry.differences == ()


# -- B-2: which record a rename makes stale ------------------------------------
#
# `domain/foundry_profile.py` has always said that players rename in Foundry and
# that a difference therefore means the *platform's* display record is stale.
# The reconciliation used to route every difference through
# `foundry_out_of_date`, tell the operator PostgreSQL was authoritative and ask
# them to update Foundry — which is an instruction to undo the rename. These
# tests pin the direction rather than merely the existence of a difference.


def renamed(bench, *, was="Old Name", now="Brand New Name"):
    character = bench.add_character(was, actor_id=fx.FIRST_ACTOR_ID)
    document = fx.bundle(actors=(fx.actor(name=now),))
    return character, preview(bench, document).report


def test_a_foundry_rename_reports_the_platform_display_record_as_stale():
    bench = harness.build()

    character, report = renamed(bench)
    entry = report.entries[0]

    assert entry.stale_platform_display_name is True
    stale = [i for i in report.issues if i.code == "platform_display_name_stale"]
    assert len(stale) == 1
    assert stale[0].severity is IssueSeverity.WARNING
    assert stale[0].character_id == character.id
    assert stale[0].actor_id == fx.FIRST_ACTOR_ID


def test_a_foundry_rename_never_reports_foundry_as_out_of_date():
    """The specific wrong answer, named."""
    bench = harness.build()

    _, report = renamed(bench)
    entry = report.entries[0]
    comparison = next(
        c for c in entry.comparisons if c.field_key == "character.display_name"
    )

    assert "foundry_out_of_date" not in issue_codes(report)
    assert comparison.differs is True
    assert comparison.warns_foundry_is_out_of_date is False
    assert comparison.stales_platform_display_name is True


def test_a_foundry_rename_never_advises_changing_foundry():
    """Read as prose, because prose is what an operator acts on."""
    bench = harness.build()

    _, report = renamed(bench)
    message = next(
        i.message for i in report.issues if i.code == "platform_display_name_stale"
    )

    lowered = message.lower()
    assert "do not change the foundry actor" in lowered
    for instruction in (
        "update the foundry actor",
        "rename the foundry actor",
        "revert",
    ):
        assert instruction not in lowered
    # …and it says the identity survived, which is the operator's real question.
    assert "identity" in lowered and "mapped" in lowered


def test_a_foundry_rename_leaves_the_character_mapped_and_unmodified():
    bench = harness.build()

    character, report = renamed(bench)
    entry = report.entries[0]

    assert entry.outcome is ActorOutcome.MAPPED
    assert entry.character_id == character.id
    # Phase 2 writes no character field. The rename is a report, not an update.
    assert bench.store.characters[character.id].display_name == "Old Name"
    assert bench.store.characters[character.id].version == 0
    assert not report.blocked


def test_a_rename_summary_names_the_direction_but_neither_name():
    bench = harness.build()

    _, report = renamed(bench, was="Aurelia Vance", now="Aurelia Stormcaller")
    summary = report.summary()

    assert summary["fields_differing"] == ["character.display_name"]
    assert summary["stale_platform_display_names"] == 1
    assert "platform_display_name_stale" in summary["issue_codes"]
    assert "foundry_out_of_date" not in summary["issue_codes"]
    # Value-minimized: the direction is recorded, the two names are not.
    rendered = repr(summary)
    for name in ("Aurelia", "Vance", "Stormcaller"):
        assert name not in rendered


def test_a_matching_name_counts_no_stale_platform_display_record():
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    report = preview(bench).report

    assert report.summary()["stale_platform_display_names"] == 0
    assert report.entries[0].stale_platform_display_name is False


def test_the_profile_declares_the_direction_rather_than_the_reconciliation():
    """The direction is a property of the field, checked at its source.

    If a later package gives another field database authority, it must state its
    own direction: `ProfileField` refuses to construct without one.
    """
    from domain.field_profile import DifferenceDirection

    display_name = PROFILE.profile_field("character.display_name")

    assert (
        display_name.difference_direction
        is DifferenceDirection.PLATFORM_DISPLAY_NAME_STALE
    )
    assert display_name.stales(DifferenceDirection.PLATFORM_DISPLAY_NAME_STALE)
    # The enum member's value *is* the issue code, so the two cannot drift.
    assert (
        DifferenceDirection.PLATFORM_DISPLAY_NAME_STALE.value
        == "platform_display_name_stale"
    )


# -- identity ambiguity, OD-42 -------------------------------------------------


def test_two_actors_sharing_a_display_name_are_two_create_candidates():
    bench = harness.build()
    document = fx.bundle(
        actors=(
            fx.actor(fx.FIRST_ACTOR_ID, name="Twin"),
            fx.actor(fx.SECOND_ACTOR_ID, name="Twin"),
        )
    )

    report = preview(bench, document).report

    assert report.count(ActorOutcome.UNMAPPED) == 2
    assert not report.blocked


def test_two_characters_may_share_a_display_name():
    """OD-42: a shared display name is legitimate, not a defect to reject."""
    bench = harness.build()
    first = bench.add_character("Grim", actor_id=fx.FIRST_ACTOR_ID)
    second = bench.add_character("Grim", actor_id=fx.SECOND_ACTOR_ID)
    document = fx.bundle(
        actors=(
            fx.actor(fx.FIRST_ACTOR_ID, name="Grim"),
            fx.actor(fx.SECOND_ACTOR_ID, name="Grim"),
        )
    )

    report = preview(bench, document).report

    assert report.count(ActorOutcome.MAPPED) == 2
    assert not report.blocked
    assert {entry.character_id for entry in report.entries} == {first.id, second.id}


def test_an_ambiguous_legacy_candidate_lookup_fails_closed_and_names_every_candidate():
    bench = harness.build()
    first = bench.add_character("Grim", character_id=uuid4())
    second = bench.add_character("Grim", character_id=uuid4())
    document = fx.bundle(actors=(fx.actor(name="Grim"),))

    report = preview(bench, document).report

    assert report.blocked
    collision = next(
        issue for issue in report.issues if issue.code == "unmapped_name_collision"
    )
    assert str(first.id) in collision.message
    assert str(second.id) in collision.message
    assert "2 existing character(s)" in collision.message
    # No candidate is chosen, so no single character is implicated.
    assert collision.character_id is None
    assert bench.store.characters.keys() == {first.id, second.id}


def test_a_single_claimant_still_blocks_because_a_name_is_not_an_identity():
    bench = harness.build()
    existing = bench.add_character(FIXTURE_NAME)

    report = preview(bench).report

    assert report.blocked
    collision = next(
        issue for issue in report.issues if issue.code == "unmapped_name_collision"
    )
    assert collision.character_id == existing.id
    assert "not an identity" in collision.message


def test_a_dangling_mapping_blocks_rather_than_creating_a_character():
    bench = harness.build()
    character = bench.add_character("Ghost", actor_id=fx.FIRST_ACTOR_ID)
    del bench.store.characters[character.id]

    report = preview(bench).report

    assert report.blocked
    assert "dangling_mapping" in issue_codes(report)


# -- absence -------------------------------------------------------------------


def test_an_absent_actor_warns_and_deletes_nothing():
    bench = harness.build()
    character = bench.add_character("Retired Adventurer", actor_id=fx.SECOND_ACTOR_ID)

    report = preview(bench).report

    assert not report.blocked
    assert [absent.character_id for absent in report.absent] == [character.id]
    warning = next(i for i in report.issues if i.code == "absent_from_snapshot")
    assert warning.severity is IssueSeverity.WARNING
    assert "Nothing is deleted, deactivated or unmapped" in warning.message
    # And the character really is untouched.
    assert bench.store.characters[character.id].active is True
    assert len(bench.store.external_actor_mappings) == 1


# -- unknown paths -------------------------------------------------------------


def test_an_unclassified_path_is_reported_per_actor_and_never_written():
    bench = harness.build()
    extended = fx.actor()
    extended["system"]["synthetics"] = {"newRuleInput": 1}

    report = preview(bench, fx.bundle(actors=(extended,))).report

    assert "unknown_snapshot_path" in issue_codes(report)
    assert report.entries[0].unknown_paths[0].path == "system.synthetics.newRuleInput"
    # A warning, not a refusal: an unclassified field is left alone.
    assert not report.blocked


# -- preview writes nothing ----------------------------------------------------


def test_a_preview_persists_no_character_or_mapping():
    bench = harness.build()

    preview(bench)

    assert bench.store.characters == {}
    assert bench.store.external_actor_mappings == []
    assert bench.store.audit_events == []
    assert bench.store.snapshots == {}


def test_a_preview_rolls_back_rather_than_committing():
    bench = harness.build()

    preview(bench)

    units = bench.factory.units
    assert all(unit.committed_count == 0 for unit in units)
    assert any(unit.rolled_back_count for unit in units)


# -- the safe summary ----------------------------------------------------------


def test_the_import_summary_carries_counts_and_identifiers_but_no_actor_values():
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    summary = preview(bench).report.summary()
    rendered = repr(summary)

    assert summary["actors"] == 1
    assert summary["mapped"] == 1
    assert summary["snapshot_checksum"]
    # Deferred fields appear as key → owning package, and nothing else.
    assert summary["legacy_authority_deferred"]["character.race"] == "5.1"
    # No Actor field value rides into the record the audit event quotes.
    for leaked in ("Synthetic Human", "paladin", "Entertainer", "3345"):
        assert leaked not in rendered


# -- the durable facts: what a stored summary can be read back as (B-1R) -------
#
# `snapshot_imports.summary` is what an already-applied import can be answered
# with on a retry, so it has to be a value with a type rather than whatever a
# `jsonb` column happens to hold. These cover the two directions and the refusals
# in between.


def test_the_summary_is_exactly_the_rendering_of_the_facts():
    """One producer. A second renderer could drift from what is stored."""
    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)

    report = preview(bench).report

    assert report.summary() == report.facts().summary()


def test_facts_round_trip_through_a_stored_summary():
    from application.foundry.reconciliation import ReconciliationFacts

    bench = harness.build()
    bench.add_character(FIXTURE_NAME, actor_id=fx.FIRST_ACTOR_ID)
    facts = preview(bench).report.facts()

    # Through JSON as well as through the dataclass, because that is the trip a
    # `jsonb` column actually makes: tuples arrive back as lists.
    import json

    restored = ReconciliationFacts.from_summary(json.loads(json.dumps(facts.summary())))

    assert restored == facts
    assert restored.summary() == facts.summary()


def test_a_summary_missing_a_declared_key_is_refused():
    from application.foundry.reconciliation import (
        ReconciliationFacts,
        ReconciliationFactsError,
    )

    bench = harness.build()
    summary = preview(bench).report.summary()
    del summary["issue_codes"]

    with pytest.raises(ReconciliationFactsError, match="missing key"):
        ReconciliationFacts.from_summary(summary)


def test_a_summary_carrying_an_undeclared_key_is_refused():
    """A key nobody declared means a version this code cannot faithfully read."""
    from application.foundry.reconciliation import (
        ReconciliationFacts,
        ReconciliationFactsError,
    )

    bench = harness.build()
    summary = {**preview(bench).report.summary(), "actor_names": ["Somebody"]}

    with pytest.raises(ReconciliationFactsError, match="undeclared key"):
        ReconciliationFacts.from_summary(summary)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("actors", "1"),
        ("actors", True),
        ("actors", -1),
        ("canonical_encoding", 1),
        ("issue_codes", "absent_from_snapshot"),
        ("issue_codes", [1]),
        ("legacy_authority_deferred", ["character.race"]),
        ("legacy_authority_deferred", {"character.race": 5}),
        ("snapshot_checksum", 42),
    ],
    ids=lambda value: repr(value),
)
def test_a_mistyped_summary_value_is_refused_rather_than_coerced(key, value):
    from application.foundry.reconciliation import (
        ReconciliationFacts,
        ReconciliationFactsError,
    )

    bench = harness.build()
    summary = {**preview(bench).report.summary(), key: value}

    with pytest.raises(ReconciliationFactsError):
        ReconciliationFacts.from_summary(summary)


def test_reading_a_summary_back_never_quotes_what_it_held():
    """The failure is read by an operator; the row's content is not for it."""
    from application.foundry.reconciliation import (
        ReconciliationFacts,
        ReconciliationFactsError,
    )

    summary = {"snapshot_checksum": "a" * 64, "MARKER-KEY": "MARKER-VALUE"}

    with pytest.raises(ReconciliationFactsError) as failure:
        ReconciliationFacts.from_summary(summary)

    assert "MARKER-KEY" in str(failure.value)  # a key, which is a name
    assert "MARKER-VALUE" not in str(failure.value)  # never the value
    assert "a" * 64 not in str(failure.value)
