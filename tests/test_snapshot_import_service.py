"""Apply: authorization at apply time, atomicity, idempotency, staleness."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from application.authorization import AuthorizationContext, NotAuthorizedError
from application.foundry.import_service import (
    ImportRefused,
    SnapshotImportService,
    request_key_digest,
)
from application.foundry.reconciliation import (
    ComparableFieldReaders,
    ReconciliationConfigurationError,
)
from application.audit import ActorCapability
from application.snapshots import ImportMode, ImportStatus
from domain.field_profile import (
    DifferenceDirection,
    FieldAuthority,
    FieldProfile,
    ProfileField,
    SnapshotField,
    SnapshotMode,
)
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from domain.identity import Character
from domain.snapshot_values import Comparison
from tests import foundry_fixtures as fx
from tests import snapshot_harness as harness
from tests.fakes import (
    FakeAuthorization,
    FakeStore,
    InjectedFailure,
    unit_of_work_factory,
)

#: A character to read comparable values off, for the reader-coverage test.
_CHARACTER = Character(id=uuid4(), display_name="Reader Coverage Probe")


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


def test_the_audit_payload_matches_the_declared_policy():
    """Safe audit content, plan §6.5.

    The substance of this moved to `tests/test_audit_payload_policy.py` under
    finding I-2: one action accepting any subset of an allowlist was not a
    policy. What remains here is the link — an applied import writes a payload
    its action's policy accepts — so a reader of the apply tests is pointed at
    where the rule actually lives.
    """
    from application.foundry.audit_policy import IMPORT_APPLIED, POLICIES

    bench = harness.build()

    outcome = apply_once(bench)

    applied = next(
        e for e in bench.store.audit_events if e.action == IMPORT_APPLIED
    )
    policy = POLICIES[IMPORT_APPLIED]
    assert policy.required <= set(applied.payload)
    assert set(applied.payload) <= policy.allowed
    assert outcome.applied


# -- I-3: an unreadable comparable field is a composition fault ----------------
#
# `_compare_fields` used to raise `LookupError` the first time a run reached a
# database-authority field with no registered reader. That is the wrong moment:
# an operator has already produced and confirmed a preview, and the failure is
# an untyped one that says nothing useful about configuration. The invariant now
# holds at construction, so a service that cannot read its own comparable fields
# never begins work.


def unreadable_profile() -> FieldProfile:
    """A profile giving database authority to a field nothing can read."""
    return FieldProfile(
        version="test-unreadable-field",
        fields={
            "character.mystery": ProfileField(
                key="character.mystery",
                label="A field a later package migrated",
                authority=FieldAuthority.DATABASE,
                comparison=Comparison.NORMALIZED_TEXT,
                difference_direction=DifferenceDirection.FOUNDRY_OUT_OF_DATE,
            )
        },
        snapshot_fields=(
            SnapshotField(
                path="system.mystery",
                mode=SnapshotMode.REPORTED,
                profile_field="character.mystery",
            ),
        ),
    )


def test_readers_must_cover_every_comparable_field_in_the_profile():
    with pytest.raises(ReconciliationConfigurationError) as refusal:
        ComparableFieldReaders({}, profile=unreadable_profile())

    message = str(refusal.value)
    assert "character.mystery" in message
    assert "test-unreadable-field" in message
    # A configuration error, not a leak: it names field keys and the profile
    # version and nothing about a database, an artifact or an Actor.
    for unsafe in ("SELECT", "psycopg", "Traceback", "postgresql://"):
        assert unsafe not in message


def test_the_service_refuses_to_be_constructed_with_an_unreadable_field():
    """The decisive assertion: it fails *at construction*, not at apply."""
    store = FakeStore()

    with pytest.raises(ReconciliationConfigurationError, match="character.mystery"):
        SnapshotImportService(
            unit_of_work_factory(store),
            deployment=OBSERVED_DEPLOYMENT,
            profile=unreadable_profile(),
            authorization=FakeAuthorization.with_council(harness.COUNCIL_USER),
        )


def test_the_accepted_profile_composes_a_complete_reader_set():
    readers = ComparableFieldReaders.default(PROFILE)

    for profile_field in PROFILE.comparable_fields():
        assert readers.read(profile_field.key, _CHARACTER) is not None


def test_the_domain_profile_holds_no_persistence_reader():
    """`FieldProfile` stays independent of `Character`, per I-3.

    The readers are an application-layer composition concern. A profile that
    knew how to read a `Character` would be the domain depending on
    persistence, which the architecture rule in `.agents/AGENTS.md` forbids.
    """
    import domain.field_profile as field_profile

    source = Path(field_profile.__file__).read_text(encoding="utf-8")
    assert "Character" not in source
    assert "domain.identity" not in source
    for profile_field in PROFILE.fields.values():
        assert not hasattr(profile_field, "read")
        assert not hasattr(profile_field, "reader")


# -- B-1: a request key is bound to the operation it was spent on --------------
#
# The defect the independent review found: `find_by_request_key` returned the
# earlier record on the key alone. A caller could therefore present a *different*
# artifact, folder, profile or exporter under a spent key and receive the first
# import's identity and correlation ID beside the second's checksum and its own
# report — one receipt describing two operations, written to append-only
# history. Idempotency now means same key **and** same bound operation.


def two_folder_document():
    return fx.bundle(
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


def test_the_operation_fields_classify_every_bound_input():
    """A new bound input cannot be silently left out of the operation identity.

    `PreviewBinding`'s fields are the bound inputs. Each is either part of the
    operation's identity or explicitly one of the two that cannot be — the
    volatile aggregate versions, and the request key itself.
    """
    from application.foundry.import_service import OPERATION_FIELDS, PreviewBinding

    bound = {
        name for name in PreviewBinding.__annotations__ if not name.startswith("_")
    }

    assert set(OPERATION_FIELDS) <= bound
    assert bound - set(OPERATION_FIELDS) == {"aggregate_versions", "request_key"}


def test_the_binding_and_the_apply_compute_the_same_operation_digest():
    """One digest, computed two ways, or the check proves nothing."""
    from application.foundry.import_service import operation_digest

    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")
    snapshot = bench.imports.parse(artifact)

    assert preview.binding.operation_digest() == operation_digest(
        {
            "snapshot_checksum": snapshot.checksum.hex_digest,
            "world_id": snapshot.world.world_id,
            "folder_id": fx.ACTIVE_FOLDER_ID,
            "folder_path": snapshot.folder_identity(fx.ACTIVE_FOLDER_ID).path,
            "profile_version": PROFILE.version,
            "exporter": snapshot.exporter.describe(),
        }
    )


def test_the_same_key_and_the_same_input_returns_the_original_result():
    """The case idempotency exists for: a retry, not a second import."""
    bench = harness.build()
    artifact = bench.artifact()

    first = apply_once(bench, request_key="req-1")
    # A genuine retry re-previews and re-applies the identical operation.
    retry_preview = bench.imports.preview(artifact, request_key="req-1")
    second = bench.imports.apply(
        artifact, retry_preview, discord_user_id=harness.COUNCIL_USER
    )

    assert second.duplicate is True
    assert second.applied is False
    assert second.import_id == first.import_id
    assert second.correlation_id == first.correlation_id
    # Exactly one durable effect.
    assert len(bench.store.characters) == 1
    assert len(bench.store.snapshot_imports) == 1
    assert len(bench.store.external_actor_mappings) == 1


# -- B-1R: a retry returns the *original* result, not a fresh one -------------
#
# The defect the re-review found. `_duplicate_of` combined the original import's
# durable facts — its id, correlation id and counts — with a reconciliation
# report computed against the database at retry time. Immediately after an
# import those two describe different moments: the original report says "one
# unmapped Actor, one create candidate" and the retry's says "already mapped".
# The test that used to live here asserted only that the report was
# service-generated and carried the same checksum, which the defect satisfied.


def retry_of(bench, artifact, *, request_key="req-1"):
    """A genuine retry: re-preview and re-apply the identical operation."""
    preview = bench.imports.preview(artifact, request_key=request_key)
    return preview, bench.imports.apply(
        artifact, preview, discord_user_id=harness.COUNCIL_USER
    )


def test_a_retry_returns_result_facts_equal_to_the_original_applys():
    """The contract, stated as the equality it is."""
    bench = harness.build()
    artifact = bench.artifact()
    first = apply_once(bench, request_key="req-1")

    _, second = retry_of(bench, artifact)

    assert second.duplicate is True
    assert second.result_facts() == first.result_facts()
    # Including the reconciliation, which is where the two used to disagree.
    assert second.reconciliation == first.reconciliation
    assert second.reconciliation.unmapped == 1
    assert second.reconciliation.mapped == 0


def test_a_retrys_facts_are_the_ones_the_original_import_recorded():
    """Read from the immutable row, not recomputed and not from the caller."""
    bench = harness.build()
    artifact = bench.artifact()
    first = apply_once(bench, request_key="req-1")
    record = bench.store.snapshot_imports[0]

    _, second = retry_of(bench, artifact)

    assert second.import_id == record.id
    assert second.correlation_id == record.correlation_id
    assert second.created_count == record.created_count
    assert second.warning_count == record.warning_count
    assert second.operation_digest == record.operation_digest
    # The stored summary *is* the returned reconciliation, both times.
    assert record.summary == first.reconciliation.summary()
    assert record.summary == second.reconciliation.summary()


def test_a_retry_is_unchanged_after_unrelated_state_has_moved(monkeypatch):
    """The moment the original defect is visible, and then some.

    After the first apply the Actor is mapped, so a reconciliation run now
    reports it as mapped where the original reported an unmapped create
    candidate. Unrelated characters and a name collision move it further. None of
    it may reach the retry's result.
    """
    bench = harness.build()
    artifact = bench.artifact()
    first = apply_once(bench, request_key="req-1")

    # Unrelated later state: another character, and one that claims the imported
    # Actor's display name — which would block a fresh reconciliation outright.
    bench.add_character("Unrelated Later Character")
    bench.add_character(harness.FIXTURE_DISPLAY_NAME)

    _, second = retry_of(bench, artifact)

    assert second.result_facts() == first.result_facts()
    assert second.reconciliation.blocked == 0
    assert second.reconciliation.errors == 0


def test_a_retry_does_not_use_the_callers_preview_report():
    """Neither the object nor its facts, even when the caller alters them.

    The preview handed to the retry carries a report claiming a hundred created
    Actors and a blocking error. It is the caller's object; a receipt built from
    it would be a caller-authored record of a Council import.
    """
    from dataclasses import replace as replace_dataclass

    from application.foundry.reconciliation import (
        IssueSeverity,
        ReconciliationIssue,
    )
    from application.foundry.import_service import SnapshotPreview

    bench = harness.build()
    artifact = bench.artifact()
    first = apply_once(bench, request_key="req-1")

    retry_preview = bench.imports.preview(artifact, request_key="req-1")
    tampered_report = replace_dataclass(
        retry_preview.report,
        entries=retry_preview.report.entries * 100,
        issues=(
            ReconciliationIssue(
                code="dangling_mapping",
                message="fabricated",
                severity=IssueSeverity.ERROR,
            ),
        ),
    )
    tampered_preview = SnapshotPreview(
        binding=retry_preview.binding,
        report=tampered_report,
        selectable_folders=retry_preview.selectable_folders,
    )

    second = bench.imports.apply(
        artifact, tampered_preview, discord_user_id=harness.COUNCIL_USER
    )

    assert second.result_facts() == first.result_facts()
    assert second.reconciliation.actors == 1
    assert second.reconciliation.errors == 0
    assert second.report is None


def test_the_duplicate_path_cannot_be_handed_a_report_at_all():
    """The structural half: there is no parameter to pass one through.

    A signature that accepts an original result is a signature somebody can pass
    the wrong one to. This asserts the shape rather than trusting the callers.
    """
    import inspect

    from application.foundry.import_service import SnapshotImportService

    parameters = inspect.signature(SnapshotImportService._duplicate_of).parameters

    assert set(parameters) == {"self", "record", "unit_of_work"}


def test_a_retry_writes_no_second_record_character_mapping_or_audit():
    bench = harness.build()
    artifact = bench.artifact()
    apply_once(bench, request_key="req-1")
    before = (
        list(bench.store.snapshot_imports),
        dict(bench.store.characters),
        list(bench.store.external_actor_mappings),
        list(bench.store.audit_events),
    )

    retry_of(bench, artifact)

    assert list(bench.store.snapshot_imports) == before[0]
    assert dict(bench.store.characters) == before[1]
    assert list(bench.store.external_actor_mappings) == before[2]
    assert list(bench.store.audit_events) == before[3]
    applied = [
        e for e in bench.store.audit_events if e.action == "snapshot_import.applied"
    ]
    assert len(applied) == 1


def test_an_unreadable_original_summary_is_refused_not_invented():
    """Fail closed: no facts are better than fabricated ones.

    The only way a stored summary can fail to read back is a version skew
    between the code that wrote it and the code reading it. The answer is a typed
    refusal naming the applied import, never a receipt whose reconciliation was
    made up to fill the gap.
    """
    from dataclasses import replace as replace_dataclass

    bench = harness.build()
    artifact = bench.artifact()
    apply_once(bench, request_key="req-1")
    bench.store.snapshot_imports[0] = replace_dataclass(
        bench.store.snapshot_imports[0],
        summary={"snapshot_checksum": "a" * 64},
    )

    preview = bench.imports.preview(artifact, request_key="req-1")
    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "original_result_unavailable"
    assert "missing key" in str(refusal.value)
    # Still exactly one applied import; the refusal claimed no state.
    applied = [
        r for r in bench.store.snapshot_imports if r.status is ImportStatus.APPLIED
    ]
    assert len(applied) == 1


def test_the_same_key_with_a_different_artifact_is_refused():
    bench = harness.build()
    apply_once(bench, request_key="req-1")

    tampered = bench.artifact(
        fx.bundle(actors=(fx.actor(fx.FIRST_ACTOR_ID, name="Somebody Else"),))
    )
    preview = bench.imports.preview(tampered, request_key="req-1")

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(tampered, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "request_key_conflict"
    assert "the snapshot artifact" in str(refusal.value)
    # One durable import, and it is still the first one.
    applied = [r for r in bench.store.snapshot_imports if r.status is ImportStatus.APPLIED]
    assert len(applied) == 1
    assert len(bench.store.characters) == 1


def test_the_same_key_with_a_different_folder_is_refused():
    bench = harness.build()
    document = two_folder_document()
    artifact = bench.artifact(document)
    preview = bench.imports.preview(
        artifact, request_key="req-1", folder_id=fx.ACTIVE_FOLDER_ID
    )
    bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    # Same artifact, same key, the *other* selected folder.
    other = bench.imports.preview(
        artifact, request_key="req-1", folder_id=fx.ARCHIVE_FOLDER_ID
    )
    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(
            artifact,
            other,
            discord_user_id=harness.COUNCIL_USER,
            folder_id=fx.ARCHIVE_FOLDER_ID,
        )

    assert refusal.value.code == "request_key_conflict"
    assert "the selected folder" in str(refusal.value)
    # The archived Actor was not imported under the active folder's key.
    assert len(bench.store.characters) == 1


def test_the_same_key_with_a_changed_profile_version_is_refused():
    from dataclasses import replace as replace_dataclass

    bench = harness.build()
    artifact = bench.artifact()
    apply_once(bench, request_key="req-1")

    # A new profile version is exactly what a re-classified field produces.
    later = SnapshotImportService(
        bench.factory,
        deployment=OBSERVED_DEPLOYMENT,
        profile=replace_dataclass(PROFILE, version="2099-01-01.1"),
        authorization=bench.authorization,
    )
    preview = later.preview(artifact, request_key="req-1")

    with pytest.raises(ImportRefused) as refusal:
        later.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "request_key_conflict"
    assert "the field-profile version" in str(refusal.value)


def test_a_conflicting_key_returns_no_receipt_for_the_earlier_import():
    """The specific defect: no mixed receipt, not even a partly correct one."""
    bench = harness.build()
    first = apply_once(bench, request_key="req-1")

    tampered = bench.artifact(
        fx.bundle(actors=(fx.actor(fx.FIRST_ACTOR_ID, name="Somebody Else"),))
    )
    preview = bench.imports.preview(tampered, request_key="req-1")

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(tampered, preview, discord_user_id=harness.COUNCIL_USER)

    # An exception, so there is no outcome object at all — and the refusal
    # carries neither the earlier import's id nor its correlation id.
    rendered = str(refusal.value)
    assert str(first.import_id) not in rendered
    assert str(first.correlation_id) not in rendered
    assert refusal.value.report is not None


def test_a_conflicting_key_writes_a_refusal_and_no_success_audit():
    bench = harness.build()
    apply_once(bench, request_key="req-1")
    applied_before = [
        e for e in bench.store.audit_events if e.action == "snapshot_import.applied"
    ]

    tampered = bench.artifact(
        fx.bundle(actors=(fx.actor(fx.FIRST_ACTOR_ID, name="Somebody Else"),))
    )
    preview = bench.imports.preview(tampered, request_key="req-1")
    with pytest.raises(ImportRefused):
        bench.imports.apply(tampered, preview, discord_user_id=harness.COUNCIL_USER)

    applied_after = [
        e for e in bench.store.audit_events if e.action == "snapshot_import.applied"
    ]
    refusals = [
        e for e in bench.store.audit_events if e.action == "snapshot_import.refused"
    ]
    assert applied_after == applied_before
    assert len(refusals) == 1
    assert refusals[0].payload["refusal_code"] == "request_key_conflict"
    assert refusals[0].payload["applied"] is False


def test_a_refused_attempt_records_the_operation_it_attempted():
    bench = harness.build()
    artifact = bench.artifact(two_folder_document())
    preview = bench.imports.preview(
        artifact, request_key="req-1", folder_id=fx.ACTIVE_FOLDER_ID
    )

    # The administrator changes the selected folder before the apply: a stale
    # preview, which is refused and recorded.
    with pytest.raises(ImportRefused):
        bench.imports.apply(
            artifact,
            preview,
            discord_user_id=harness.COUNCIL_USER,
            folder_id=fx.ARCHIVE_FOLDER_ID,
        )

    # The refusal row keys itself apart from the caller's key, so the corrected
    # retry is not mistaken for it — and it still records what was attempted.
    refused = [r for r in bench.store.snapshot_imports if r.status is ImportStatus.REFUSED]
    assert len(refused) == 1
    assert refused[0].request_key != "req-1"
    # Keyed by the digest of the caller's key rather than by the key (S-1): a
    # refused row is never looked up by key, so it keeps no copy of the text.
    assert refused[0].request_key.startswith(
        f"refused:{request_key_digest('req-1')}:"
    )
    assert "req-1" not in refused[0].request_key
    assert refused[0].operation_digest == preview.binding.operation_digest()
    # …and it does not satisfy an idempotency lookup, so the corrected retry
    # under the same key is not answered with this refusal.
    assert bench.store.snapshot_imports[0].request_key != "req-1"


def test_an_over_long_request_key_still_produces_a_recordable_refusal():
    """A refusal must survive its own key, or the record of it is lost.

    The refused key is now fixed-width by construction — a prefix, a digest and
    a correlation id — so the column bound holds for any accepted key rather than
    by truncating the caller's text to fit.
    """
    from application.foundry.import_service import _refused_key
    from application.snapshots import REQUEST_KEY_MAX_LENGTH

    key = "k" * REQUEST_KEY_MAX_LENGTH
    refused = _refused_key(key, uuid4())

    assert len(refused) <= REQUEST_KEY_MAX_LENGTH
    assert refused.startswith(f"refused:{request_key_digest(key)}:")
    assert "kkk" not in refused


def test_two_refusals_of_the_same_key_are_two_distinct_rows():
    """Or recording the second refusal would itself be a uniqueness violation."""
    from application.foundry.import_service import _refused_key

    first = _refused_key("req-1", uuid4())
    second = _refused_key("req-1", uuid4())

    assert first != second
    assert first.split(":")[1] == second.split(":")[1]


@pytest.mark.parametrize(
    "hostile",
    [
        "x" * 256,
        "req\x00-1",
        "req\n-1",
        "req\x1b[31m-1",
        "   ",
    ],
    ids=["too-long", "null-byte", "newline", "escape-sequence", "blank"],
)
def test_a_hostile_request_key_is_refused_where_it_arrives(hostile: str):
    """It is written verbatim into the idempotency lookup column.

    So it is validated as input rather than trusted as an opaque handle, and the
    refusal happens at `preview` — before any parsing, reading or writing. This
    bounds the *column*; keeping the text out of audit history is
    `request_key_digest`'s job (S-1), which the audit-policy tests cover.
    """
    bench = harness.build()
    artifact = bench.artifact()

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.preview(artifact, request_key=hostile)

    assert refusal.value.code == "invalid_request_key"
    assert bench.store.snapshot_imports == []
    assert bench.store.audit_events == []


def test_the_record_itself_refuses_an_unwritable_request_key():
    """The last line of defence, below the service's own validation."""
    from application.snapshots import SnapshotImportRecord

    with pytest.raises(ValueError, match="printable text"):
        SnapshotImportRecord(
            snapshot_id=uuid4(),
            folder_id="f",
            folder_path="/actors/x",
            profile_version=PROFILE.version,
            request_key="req\x00-1",
            operation_digest="a" * 64,
            status=ImportStatus.APPLIED,
            mode=ImportMode.COUNCIL,
            actor_capability=ActorCapability.GUILD_COUNCIL,
            summary={},
            correlation_id=uuid4(),
        )


def test_the_record_itself_refuses_an_absent_operation_digest():
    from application.snapshots import SnapshotImportRecord

    with pytest.raises(ValueError, match="SHA-256 digest of the operation"):
        SnapshotImportRecord(
            snapshot_id=uuid4(),
            folder_id="f",
            folder_path="/actors/x",
            profile_version=PROFILE.version,
            request_key="req-1",
            operation_digest="",
            status=ImportStatus.APPLIED,
            mode=ImportMode.COUNCIL,
            actor_capability=ActorCapability.GUILD_COUNCIL,
            summary={},
            correlation_id=uuid4(),
        )


# -- I-1: a lost race is translated, never guessed at --------------------------


def lose_to(bench, *, on: str, rule: str, winner):
    """Make the next apply lose a race on `rule`, after `winner` has committed.

    The callable form of the injection hook is what makes the ordering right:
    the winning transaction commits *at the moment* this attempt fails, so the
    losing service resolves the conflict against a database that already holds
    the winner — exactly as a real concurrent apply would.
    """
    from application.errors import UniquenessConflict

    def fail():
        # One-shot: a race is lost once. Clearing the factory's injection means
        # the *resolution* transaction — which is a new unit of work — runs
        # against the store for real, which is the behaviour under test.
        bench.factory.fail_on = None
        bench.factory.failure = None
        winner()
        return UniquenessConflict(rule)

    bench.factory.fail_on = on
    bench.factory.failure = fail


def test_a_lost_request_key_race_returns_the_winner_as_a_typed_duplicate():
    """The loser re-reads the winning row rather than assuming anything."""
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    # The winner is a second service over the same store, applying the identical
    # operation under the identical key. It commits as this attempt inserts.
    rival = SnapshotImportService(
        unit_of_work_factory(bench.store),
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=bench.authorization,
    )
    won: list = []

    def winner():
        rival_preview = rival.preview(artifact, request_key="req-1")
        won.append(
            rival.apply(artifact, rival_preview, discord_user_id=harness.COUNCIL_USER)
        )

    lose_to(
        bench, on="snapshot_imports", rule="snapshot_import.request_key", winner=winner
    )

    loser = bench.imports.apply(
        artifact, preview, discord_user_id=harness.COUNCIL_USER
    )

    assert won[0].applied is True
    # Typed, and internally consistent: it points at the winning row and at
    # nothing of its own. Compared whole (B-1R) rather than field by field — the
    # loser's result is the winner's original result, reconciliation included.
    assert loser.duplicate is True
    assert loser.applied is False
    assert loser.result_facts() == won[0].result_facts()
    assert loser.report is None
    # Exactly one durable effect.
    assert len(bench.store.snapshot_imports) == 1
    assert len(bench.store.characters) == 1
    assert len(bench.store.external_actor_mappings) == 1


def test_a_lost_input_race_under_a_different_key_is_also_a_typed_duplicate():
    """Overlapping input, different key: still one effect, still typed."""
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-mine")
    rival = SnapshotImportService(
        unit_of_work_factory(bench.store),
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=bench.authorization,
    )
    won: list = []

    def winner():
        rival_preview = rival.preview(artifact, request_key="req-theirs")
        won.append(
            rival.apply(artifact, rival_preview, discord_user_id=harness.COUNCIL_USER)
        )

    lose_to(
        bench,
        on="external_actor_mappings",
        rule="external_actor_mapping.world_actor",
        winner=winner,
    )

    loser = bench.imports.apply(
        artifact, preview, discord_user_id=harness.COUNCIL_USER
    )

    assert loser.duplicate is True
    # A truthful duplicate *of the actual winner*: the whole original result,
    # not the loser's own reconciliation wearing the winner's identifiers.
    assert loser.result_facts() == won[0].result_facts()
    assert loser.report is None
    assert len(bench.store.characters) == 1
    assert len(bench.store.external_actor_mappings) == 1
    applied = [
        r for r in bench.store.snapshot_imports if r.status is ImportStatus.APPLIED
    ]
    assert len(applied) == 1


def test_an_unresolvable_conflict_is_refused_rather_than_called_a_duplicate():
    """Nothing this operation can name won, so a duplicate receipt would lie."""
    from application.errors import UniquenessConflict

    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    # A collision with no corresponding winning import row: whatever claimed the
    # mapping, it was not an import of this operation.
    bench.factory.fail_on = "external_actor_mappings"
    bench.factory.failure = UniquenessConflict("external_actor_mapping.world_actor")

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "concurrent_import"
    assert bench.store.characters == {}
    applied = [
        e for e in bench.store.audit_events if e.action == "snapshot_import.applied"
    ]
    assert applied == []


def test_a_conflicting_key_claimed_concurrently_is_refused_not_duplicated():
    """The B-1 check applies on the concurrent path too, not only the early one."""
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    other = bench.artifact(
        fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID, name="Somebody Else"),))
    )
    rival = SnapshotImportService(
        unit_of_work_factory(bench.store),
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=bench.authorization,
    )

    def winner():
        rival_preview = rival.preview(other, request_key="req-1")
        rival.apply(other, rival_preview, discord_user_id=harness.COUNCIL_USER)

    lose_to(
        bench, on="snapshot_imports", rule="snapshot_import.request_key", winner=winner
    )

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "request_key_conflict"


def test_a_persistence_failure_is_never_resolved_into_a_duplicate():
    """`PersistenceError` is a controlled boundary, not a conflict.

    The distinction is the whole of the "must still roll back and surface
    through a controlled application error boundary rather than being
    mislabeled as a successful duplicate" requirement.
    """
    from application.errors import PersistenceError, UniquenessConflict

    assert not issubclass(PersistenceError, UniquenessConflict)
    assert not issubclass(UniquenessConflict, PersistenceError)

    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")
    bench.factory.fail_on = "snapshot_imports"
    bench.factory.failure = PersistenceError("40001")

    with pytest.raises(PersistenceError) as failure:
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert failure.value.sqlstate == "40001"
    assert bench.store.characters == {}
    assert bench.store.snapshot_imports == []
    successes = [
        e for e in bench.store.audit_events if e.action == "snapshot_import.applied"
    ]
    assert successes == []


def test_every_refusal_code_is_declared():
    """The refusal vocabulary is closed; an audit filter can rely on it."""
    import ast
    import inspect

    from application.foundry import import_service

    tree = ast.parse(inspect.getsource(import_service))
    raised = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "ImportRefused"
        and node.args
        and isinstance(node.args[0], ast.Constant)
    }

    assert raised, "no refusal codes were found; the scan is broken"
    assert raised <= import_service.REFUSAL_CODES, (
        f"undeclared refusal code(s): {raised - import_service.REFUSAL_CODES}"
    )
