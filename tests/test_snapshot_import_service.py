"""Apply: authorization at apply time, atomicity, idempotency, staleness."""
from __future__ import annotations

import pytest

from application.authorization import AuthorizationContext, NotAuthorizedError
from application.foundry.import_service import (
    ImportRefused,
    SnapshotImportService,
)
from application.snapshots import ImportMode, ImportStatus
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from tests import foundry_fixtures as fx
from tests import snapshot_harness as harness
from tests.fakes import InjectedFailure


def apply_once(bench, *, request_key="req-1", document=None, user=harness.COUNCIL_USER, **kwargs):
    artifact = bench.artifact(document)
    preview = bench.imports.preview(artifact, request_key=request_key, **kwargs)
    return bench.imports.apply(artifact, preview, discord_user_id=user)


# -- the happy path ------------------------------------------------------------


def test_a_clean_import_creates_a_character_a_mapping_and_a_record():
    bench = harness.build()

    outcome = apply_once(bench)

    assert outcome.applied
    assert outcome.created_count == 1
    assert len(bench.store.characters) == 1
    mapping = bench.store.external_actor_mappings[0]
    assert mapping.external_actor_id == fx.FIRST_ACTOR_ID
    assert mapping.world_id == "the-guild"
    assert mapping.folder_id == fx.ACTIVE_FOLDER_ID
    assert len(bench.store.snapshot_imports) == 1


def test_every_applied_character_and_mapping_traces_to_the_snapshot_and_actor():
    bench = harness.build()

    outcome = apply_once(bench)

    snapshot = bench.store.snapshots[outcome.snapshot_checksum]
    mapping = bench.store.external_actor_mappings[0]
    assert mapping.established_by_snapshot_id == snapshot.id
    record = bench.store.snapshot_imports[0]
    assert record.status is ImportStatus.APPLIED
    assert record.mode is ImportMode.COUNCIL
    assert record.actor_discord_user_id == harness.COUNCIL_USER
    assert record.profile_version == PROFILE.version
    assert record.summary["snapshot_checksum"] == outcome.snapshot_checksum


def test_the_relink_fingerprint_records_name_class_and_level():
    bench = harness.build()

    apply_once(bench)

    fingerprint = bench.store.external_actor_mappings[0].relink_fingerprint
    assert "Testcharacter Brightlantern" in fingerprint
    assert "paladin" in fingerprint
    assert "level 9" in fingerprint


def test_an_imported_character_starts_with_identity_and_nothing_else():
    """The import establishes identity and a mapping, and stops there.

    Level, long name and every other field stay unset — not because a
    correction has not run yet, but because Phase 2 has no way to set them at
    all. The owning migration package supplies them.
    """
    bench = harness.build()

    apply_once(bench)

    character = next(iter(bench.store.characters.values()))
    assert character.display_name
    assert character.level is None
    assert character.long_name is None
    # And there is no store for anything else to have been written into.
    assert not hasattr(bench.store, "state_values")
    assert not hasattr(bench.store, "balances")
    assert not hasattr(bench.store, "transactions")


def test_the_success_audit_names_the_snapshot_the_actor_and_the_authority():
    bench = harness.build()

    outcome = apply_once(bench)

    actions = {event.action for event in bench.store.audit_events}
    assert actions == {"snapshot_import.applied", "snapshot_import.character.created"}
    applied = next(
        e for e in bench.store.audit_events if e.action == "snapshot_import.applied"
    )
    assert applied.entity_id == outcome.snapshot_checksum
    assert applied.actor_discord_user_id == harness.COUNCIL_USER
    assert applied.actor_capability.value == "guild_council"
    assert applied.correlation_id == outcome.correlation_id
    assert applied.payload["profile_version"] == PROFILE.version


# -- authorization -------------------------------------------------------------


def test_one_council_member_is_sufficient():
    bench = harness.build()

    outcome = apply_once(bench)

    assert outcome.applied
    # One person, no second approver anywhere in the record.
    assert bench.store.snapshot_imports[0].supervisor is None


def test_an_ordinary_member_is_denied():
    bench = harness.build()
    bench.authorization.grant(
        AuthorizationContext(discord_user_id=harness.ORDINARY_USER, guild_member=True)
    )

    with pytest.raises(NotAuthorizedError) as denial:
        apply_once(bench, user=harness.ORDINARY_USER)

    assert denial.value.code == "not_guild_council"
    assert bench.store.characters == {}


def test_a_non_member_is_denied():
    bench = harness.build()

    with pytest.raises(NotAuthorizedError) as denial:
        apply_once(bench, user=999000000000000001)

    assert denial.value.code == "not_a_guild_member"


def test_a_platform_administrator_alone_cannot_apply_an_import():
    bench = harness.build()
    bench.authorization.grant(
        AuthorizationContext(
            discord_user_id=harness.ORDINARY_USER,
            guild_member=True,
            platform_administrator=True,
        )
    )

    with pytest.raises(NotAuthorizedError) as denial:
        apply_once(bench, user=harness.ORDINARY_USER)

    assert denial.value.code == "not_guild_council"


def test_authorization_is_rechecked_at_apply_not_carried_from_the_preview():
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    # The role is revoked between preview and apply.
    bench.authorization.revoke(harness.COUNCIL_USER)

    with pytest.raises(NotAuthorizedError):
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)
    assert bench.store.characters == {}


def test_the_authorization_port_is_asked_again_for_the_apply():
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")
    asked_after_preview = len(bench.authorization.asked)

    bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert len(bench.authorization.asked) > asked_after_preview


def test_an_import_without_authority_or_bootstrap_is_refused():
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(artifact, preview)

    assert refusal.value.code == "no_authority"


def test_an_import_cannot_be_both_a_bootstrap_and_a_council_action():
    from application.authorization import SupervisedBootstrap

    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(
            artifact,
            preview,
            discord_user_id=harness.COUNCIL_USER,
            bootstrap=SupervisedBootstrap("Peter Duscha"),
        )

    assert refusal.value.code == "ambiguous_authority"


# -- staleness -----------------------------------------------------------------


def test_a_changed_snapshot_makes_the_preview_stale():
    bench = harness.build()
    original = bench.artifact()
    preview = bench.imports.preview(original, request_key="req-1")
    other = bench.artifact(fx.bundle(actors=(fx.actor(name="Different Name"),)))

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(other, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "stale_preview"
    assert "snapshot artifact" in str(refusal.value)
    assert bench.store.characters == {}


def test_a_changed_database_version_makes_the_preview_stale():
    bench = harness.build()
    character = bench.add_character(
        harness.FIXTURE_DISPLAY_NAME, actor_id=fx.FIRST_ACTOR_ID
    )
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    # Somebody else corrects the character in between.
    from dataclasses import replace

    bench.store.characters[character.id] = replace(
        bench.store.characters[character.id], version=1
    )

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "stale_preview"
    assert "a character that this import would touch" in str(refusal.value)


def test_a_changed_profile_version_makes_the_preview_stale():
    from dataclasses import replace as dataclass_replace

    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")
    stale = dataclass_replace(
        preview, binding=dataclass_replace(preview.binding, profile_version="1999-01-01.1")
    )

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(artifact, stale, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "stale_preview"
    assert "field-profile version" in str(refusal.value)


def test_an_administrator_folder_change_between_preview_and_apply_is_stale():
    bench = harness.build()
    document = fx.bundle(
        folders=(
            fx.folder(fx.ACTIVE_FOLDER_ID, "Characters (active)"),
            fx.folder(fx.ARCHIVE_FOLDER_ID, "Characters (retired)"),
        ),
        selected_folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID),
        actors=(
            fx.actor(fx.FIRST_ACTOR_ID),
            fx.actor(fx.SECOND_ACTOR_ID, name="Other", folder_id=fx.ARCHIVE_FOLDER_ID),
        ),
    )
    artifact = bench.artifact(document)
    preview = bench.imports.preview(
        artifact, request_key="req-1", folder_id=fx.ACTIVE_FOLDER_ID
    )

    # The administrator changes the selected folder before the Council member
    # confirms. The apply is told what is selected *now*.
    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(
            artifact,
            preview,
            discord_user_id=harness.COUNCIL_USER,
            folder_id=fx.ARCHIVE_FOLDER_ID,
        )

    assert refusal.value.code == "stale_preview"
    assert "folder changed" in str(refusal.value)
    assert bench.store.characters == {}


def test_an_unchanged_folder_selection_applies_normally():
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    outcome = bench.imports.apply(
        artifact,
        preview,
        discord_user_id=harness.COUNCIL_USER,
        folder_id=fx.ACTIVE_FOLDER_ID,
    )

    assert outcome.applied


def test_a_stale_preview_records_one_refused_attempt_and_no_success():
    bench = harness.build()
    original = bench.artifact()
    preview = bench.imports.preview(original, request_key="req-1")
    other = bench.artifact(fx.bundle(actors=(fx.actor(name="Different Name"),)))

    with pytest.raises(ImportRefused):
        bench.imports.apply(other, preview, discord_user_id=harness.COUNCIL_USER)

    records = bench.store.snapshot_imports
    assert [record.status for record in records] == [ImportStatus.REFUSED]
    actions = [event.action for event in bench.store.audit_events]
    assert actions == ["snapshot_import.refused"]
    refusal_event = bench.store.audit_events[0]
    assert refusal_event.payload["applied"] is False
    assert refusal_event.correlation_id == records[0].correlation_id


def test_a_refusal_audit_carries_no_traceback_or_artifact_content():
    bench = harness.build()
    original = bench.artifact()
    preview = bench.imports.preview(original, request_key="req-1")
    other = bench.artifact(fx.bundle(actors=(fx.actor(name="Different Name"),)))

    with pytest.raises(ImportRefused):
        bench.imports.apply(other, preview, discord_user_id=harness.COUNCIL_USER)

    rendered = repr(bench.store.audit_events[0].payload)
    assert "Traceback" not in rendered
    assert "Brightlantern" not in rendered
    assert "Different Name" not in rendered


# -- blocking issues -----------------------------------------------------------


def test_a_blocked_run_applies_nothing():
    bench = harness.build()
    bench.add_character("Testcharacter Brightlantern")

    with pytest.raises(ImportRefused) as refusal:
        apply_once(bench)

    assert refusal.value.code == "blocked"
    assert len(bench.store.characters) == 1
    assert bench.store.external_actor_mappings == []


def test_one_blocked_actor_refuses_the_whole_run():
    # The run is the unit: a valid Actor beside a blocked one is not imported.
    bench = harness.build()
    bench.add_character("Second Actor")
    document = fx.bundle(
        actors=(
            fx.actor(fx.FIRST_ACTOR_ID, name="Clean Actor"),
            fx.actor(fx.SECOND_ACTOR_ID, name="Second Actor"),
        )
    )

    with pytest.raises(ImportRefused):
        apply_once(bench, document=document)

    assert len(bench.store.characters) == 1
    assert bench.store.external_actor_mappings == []


# -- idempotency and concurrency ------------------------------------------------


def test_repeating_the_same_request_returns_the_original_result():
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")
    first = bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    second = bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert second.duplicate is True
    assert second.import_id == first.import_id
    assert len(bench.store.characters) == 1
    assert len(bench.store.snapshot_imports) == 1


def test_reapplying_the_same_input_under_a_new_request_key_is_a_typed_duplicate():
    bench = harness.build()
    artifact = bench.artifact()
    first = bench.imports.apply(
        artifact,
        bench.imports.preview(artifact, request_key="req-1"),
        discord_user_id=harness.COUNCIL_USER,
    )

    second = bench.imports.apply(
        artifact,
        bench.imports.preview(artifact, request_key="req-2"),
        discord_user_id=harness.COUNCIL_USER,
    )

    assert second.duplicate is True
    assert second.import_id == first.import_id
    # A successful no-op: no second character, no second mapping, no second
    # audit effect.
    assert len(bench.store.characters) == 1
    assert len(bench.store.external_actor_mappings) == 1
    assert len(bench.store.snapshot_imports) == 1


def test_a_second_import_of_a_different_snapshot_is_a_new_reconciliation_event():
    bench = harness.build()
    artifact = bench.artifact()
    bench.imports.apply(
        artifact,
        bench.imports.preview(artifact, request_key="req-1"),
        discord_user_id=harness.COUNCIL_USER,
    )
    later = bench.artifact(fx.bundle(exported_at="2026-08-03T09:15:00Z"))

    outcome = bench.imports.apply(
        later,
        bench.imports.preview(later, request_key="req-2"),
        discord_user_id=harness.COUNCIL_USER,
    )

    assert outcome.applied
    assert outcome.duplicate is False
    assert len(bench.store.snapshots) == 2
    # The same Actor is already mapped, so nothing was created a second time.
    assert len(bench.store.characters) == 1


def test_a_refused_attempt_does_not_block_the_corrected_retry():
    bench = harness.build()
    bench.add_character("Testcharacter Brightlantern")
    with pytest.raises(ImportRefused):
        apply_once(bench, request_key="req-1")

    # The collision is resolved by removing the unmapped duplicate.
    bench.store.characters.clear()

    outcome = apply_once(bench, request_key="req-2")

    assert outcome.applied


# -- injected failures ----------------------------------------------------------


def test_an_audit_write_failure_rolls_back_the_import():
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")
    for unit in bench.factory.units:
        unit.fail_on = "audit"
    bench.factory.units.clear()

    def failing_factory():
        unit = _next_unit(bench)
        unit.fail_on = "audit"
        return unit

    bench.imports._unit_of_work_factory = failing_factory  # noqa: SLF001

    with pytest.raises(InjectedFailure):
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert bench.store.characters == {}
    assert bench.store.external_actor_mappings == []
    assert bench.store.audit_events == []
    assert bench.store.snapshot_imports == []


def test_a_record_write_failure_leaves_no_partial_state():
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    def failing_factory():
        unit = _next_unit(bench)
        unit.fail_on = "snapshot_imports"
        return unit

    bench.imports._unit_of_work_factory = failing_factory  # noqa: SLF001

    with pytest.raises(InjectedFailure):
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert bench.store.characters == {}
    assert bench.store.snapshots == {}


def _next_unit(bench):
    from tests.fakes import FakeUnitOfWork

    unit = FakeUnitOfWork(bench.store)
    bench.factory.units.append(unit)
    return unit


def test_a_wrong_deployment_is_refused_with_no_transaction_opened():
    from application.foundry.artifact import SnapshotRejected

    bench = harness.build()
    document = fx.bundle()
    document["world"]["systemVersion"] = "9.9.9"

    with pytest.raises(SnapshotRejected) as refusal:
        bench.imports.preview(bench.artifact(document), request_key="req-1")

    assert refusal.value.code == "unsupported_deployment"
    assert bench.factory.units == []


def test_a_tampered_artifact_cannot_inherit_another_snapshot_identity():
    from application.foundry.artifact import SnapshotArtifact, SnapshotRejected
    from domain.foundry import SnapshotChecksum

    bench = harness.build()
    honest = fx.encode(fx.bundle())
    tampered = fx.tamper(honest, find=b"Brightlantern", replace=b"Brightlantexn")
    forged = SnapshotArtifact(tampered, SnapshotChecksum.of(honest))

    with pytest.raises(SnapshotRejected) as refusal:
        bench.imports.parse(forged)

    assert refusal.value.code == "checksum_mismatch"


def test_the_service_needs_no_network_or_live_foundry():
    # Constructing and running the whole use case touches a factory, a profile
    # and a deployment tuple. There is no client, no URL and no socket.
    bench = harness.build()

    outcome = apply_once(bench)

    assert outcome.applied
    assert isinstance(bench.imports, SnapshotImportService)
    assert OBSERVED_DEPLOYMENT.world_id == "the-guild"


# -- the binding covers what it claims to --------------------------------------


def test_the_preview_binding_covers_every_declared_input():
    """Every bound field is compared, and every comparison is reportable.

    Table-driven off the dataclass rather than off a hand-written list, so
    adding a field to `PreviewBinding` without teaching `differences` about it
    fails here instead of silently becoming an input nobody rechecks. That is
    the exact defect class this test exists for: a binding that looks complete
    and quietly is not.
    """
    import dataclasses

    from application.foundry.import_service import PreviewBinding

    bound = {f.name for f in dataclasses.fields(PreviewBinding)}

    assert bound == set(PreviewBinding._DESCRIPTIONS), (
        "a bound input is missing a refusal description, or vice versa"
    )


@pytest.mark.parametrize(
    ("field_name", "replacement"),
    [
        ("snapshot_checksum", "f" * 64),
        ("world_id", "some-other-world"),
        ("folder_id", "OtherFolder000001"),
        ("folder_path", "/actors/Somewhere Else"),
        ("profile_version", "9999-01-01.9"),
        ("exporter", "other-exporter 9.9"),
        ("aggregate_versions", (("00000000-0000-0000-0000-000000000000", 7),)),
        ("request_key", "a-different-attempt"),
    ],
)
def test_every_bound_input_is_reported_when_it_moves(field_name, replacement):
    """Each field, changed one at a time, names itself in the refusal."""
    import dataclasses

    from application.foundry.import_service import PreviewBinding

    original = PreviewBinding(
        snapshot_checksum="a" * 64,
        world_id="the-guild",
        folder_id=fx.ACTIVE_FOLDER_ID,
        folder_path="/actors/Characters (active)",
        profile_version=PROFILE.version,
        exporter="synthetic 1.0",
        aggregate_versions=(),
        request_key="req-1",
    )
    moved = dataclasses.replace(original, **{field_name: replacement})

    changes = original.differences(moved)

    assert changes == (PreviewBinding._DESCRIPTIONS[field_name],)
    assert original.token() != moved.token()


def test_no_service_api_accepts_a_field_selection():
    """There is no route from a snapshot value into a character field.

    Checked at the signature, because that is where such a route would
    reappear: an optional `selected_corrections` argument reintroduced for
    convenience is the whole rejected design in one keyword.
    """
    import inspect

    from application.foundry import import_service

    for name in ("preview", "apply"):
        parameters = set(
            inspect.signature(getattr(SnapshotImportService, name)).parameters
        )
        assert not parameters & {
            "selected_corrections",
            "selections",
            "corrections",
        }, f"{name}() accepts a correction selection"

    constructor = set(inspect.signature(SnapshotImportService.__init__).parameters)
    assert "corrections" not in constructor

    for banned in ("FieldSelection", "CorrectionService", "CorrectionRequest"):
        assert not hasattr(import_service, banned), (
            f"{banned} is back in the import service"
        )


# -- injected failure at every write point --------------------------------------


@pytest.mark.parametrize(
    "failure_point",
    ["snapshots", "characters", "external_actor_mappings", "snapshot_imports", "audit"],
)
def test_each_injected_failure_point_leaves_no_partial_state(failure_point):
    """Threshold T-1: zero partial commits, at every write the import makes.

    Parametrised over the write points rather than written out for the two that
    were easiest to reach, because "no partial commit" is a claim about all of
    them and a spot check is not evidence for it.
    """
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    for unit in bench.factory.units:
        unit.fail_on = failure_point
    bench.factory.fail_on = failure_point

    with pytest.raises(InjectedFailure):
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert bench.store.characters == {}
    assert bench.store.external_actor_mappings == []
    assert bench.store.snapshots == {}
    assert bench.store.snapshot_imports == []
    successes = [
        event
        for event in bench.store.audit_events
        if event.action == "snapshot_import.applied"
    ]
    assert successes == []


def test_the_audit_payload_contains_only_allowlisted_keys():
    """Safe audit content, plan §6.5.

    An allowlist rather than a denylist: a new payload key has to be considered
    and added here, which is the point at which somebody notices they are about
    to write an Actor's data into an append-only table.
    """
    bench = harness.build()

    outcome = apply_once(bench)

    applied = next(
        e for e in bench.store.audit_events if e.action == "snapshot_import.applied"
    )
    allowed = {
        "snapshot_checksum",
        "folder_id",
        "folder_path",
        "profile_version",
        "exporter",
        "canonical_encoding",
        "actors",
        "mapped",
        "unmapped",
        "blocked",
        "absent",
        "errors",
        "warnings",
        "issue_codes",
        "fields_out_of_date",
        "legacy_authority_deferred",
        "mode",
        "supervisor",
        "request_key",
        "preview_token",
        "characters_created",
    }

    assert set(applied.payload) <= allowed, (
        f"unexpected audit payload key(s): {set(applied.payload) - allowed}"
    )
    rendered = repr(applied.payload)
    for leaked in ("Synthetic Human", "paladin", "Entertainer", "Brightlantern"):
        assert leaked not in rendered
    assert outcome.applied
