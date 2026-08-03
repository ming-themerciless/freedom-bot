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
