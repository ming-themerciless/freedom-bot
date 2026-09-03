"""The submission use case: validation, storage, provenance and idempotency.

Every fixture here is synthetic by construction. No real Actor, export or
snapshot is used, and the artifact store is a per-test temporary directory.
"""
from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest

from adapters.artifacts.filesystem import FilesystemArtifactStore
from application.admissions import AdmissionState
from application.audit import ActorCapability, AuditSource
from application.authorization import NotAuthorizedError
from application.errors import PersistenceError, UniquenessConflict
from application.foundry.audit_policy import (
    POLICIES,
    SUBMISSION_ACCEPTED,
    SUBMISSION_REFUSED,
)
from application.foundry.submission import (
    ARTIFACT_REFUSAL_CODES,
    REFUSAL_CODES,
    SUBMISSION_SCOPE,
    SnapshotSubmissionService,
    SubmissionReceipt,
    SubmissionRefused,
    request_key_digest,
)
from application.idempotency import IdempotencyRecord, IdempotencyStatus
from application.service_principals import ServicePrincipal, ServicePrincipalScope
from application.snapshots import SnapshotSource
from domain.foundry import OBSERVED_DEPLOYMENT
from tests import foundry_fixtures as fx
from tests.fakes import FakeStore, admit, close_admission, unit_of_work_factory

SUBMITTER = ServicePrincipal(
    principal_id="foundry-the-guild",
    scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
)
KEY = "foundry-module:test-key"


@pytest.fixture()
def store() -> FakeStore:
    # An open admission generation for the submitting credential, exactly as
    # `tools.submission_admission open` creates in a deployment. Without one the
    # endpoint refuses every submission, which is the state a fresh install is
    # in and which `test_submission_admission.py` covers on purpose.
    store = FakeStore()
    admit(store, SUBMITTER.principal_id)
    return store


@pytest.fixture()
def artifacts(tmp_path: Path) -> FilesystemArtifactStore:
    store = FilesystemArtifactStore(tmp_path / "artifacts")
    yield store
    store.close()


@pytest.fixture()
def service(store, artifacts) -> SnapshotSubmissionService:
    return SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )


def payload(document=None) -> bytes:
    return fx.encode(document or fx.bundle())


def digest_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# -- the happy path -----------------------------------------------------------


def test_a_valid_submission_records_pending_provenance(service, store):
    data = payload()

    receipt = service.submit(data, principal=SUBMITTER, request_key=KEY)

    assert receipt.status == "pending"
    assert receipt.checksum == digest_of(data)
    assert receipt.actor_count == 1
    assert receipt.duplicate is False
    assert receipt.world_id == OBSERVED_DEPLOYMENT.world_id
    assert [folder.folder_id for folder in receipt.folders] == [fx.ACTIVE_FOLDER_ID]
    assert receipt.folders[0].path == "/actors/Characters/Characters (active)"

    record = store.snapshots[receipt.checksum]
    assert record.received_via is SnapshotSource.FOUNDRY_MODULE
    assert record.submitted_by_principal == "foundry-the-guild"
    assert record.artifact_location == f"snapshot/{receipt.checksum}.json"


def test_a_submission_applies_nothing(service, store):
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    assert store.characters == {}
    assert store.external_actor_mappings == []
    assert store.snapshot_imports == []
    assert store.initialization is None


def test_the_artifact_bytes_are_stored_and_readable_back(service, artifacts):
    data = payload()

    receipt = service.submit(data, principal=SUBMITTER, request_key=KEY)

    assert artifacts.load(receipt.checksum).raw_bytes() == data


def test_the_receipt_carries_no_actor_name_or_mechanic(service):
    receipt = service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    rendered = str(receipt.as_payload())
    assert "Testcharacter" not in rendered
    assert "Brightlantern" not in rendered
    assert "paladin" not in rendered
    assert "abilities" not in rendered


# -- authorization ------------------------------------------------------------


def test_a_principal_without_the_scope_cannot_submit(service, store, artifacts):
    wrong_scope = ServicePrincipal(
        principal_id="reader", scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT})
    )
    # Constructed with the scope, then stripped, because `ServicePrincipal`
    # refuses to exist with no scope at all.
    object.__setattr__(wrong_scope, "scopes", frozenset())

    with pytest.raises(NotAuthorizedError) as refusal:
        service.submit(payload(), principal=wrong_scope, request_key=KEY)

    assert refusal.value.code == "out_of_scope"
    assert store.snapshots == {}
    # The store was never even created: the scope check precedes everything.
    assert not artifacts.root.exists()


def test_an_out_of_scope_refusal_names_no_other_scope(service):
    principal = ServicePrincipal(
        principal_id="reader", scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT})
    )
    object.__setattr__(principal, "scopes", frozenset())
    with pytest.raises(NotAuthorizedError) as refusal:
        service.submit(payload(), principal=principal, request_key=KEY)
    assert "reader" not in str(refusal.value)


# -- checksum -----------------------------------------------------------------


def test_a_claimed_checksum_that_matches_is_accepted(service):
    data = payload()
    receipt = service.submit(
        data, principal=SUBMITTER, request_key=KEY, claimed_checksum=digest_of(data)
    )
    assert receipt.checksum == digest_of(data)


def test_a_claimed_checksum_that_disagrees_stores_nothing(service, store, artifacts):
    data = payload()

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(
            data, principal=SUBMITTER, request_key=KEY, claimed_checksum="f" * 64
        )

    assert refusal.value.code == "checksum_mismatch"
    assert store.snapshots == {}
    assert not artifacts.contains(digest_of(data))


def test_the_server_digest_wins_over_the_claim(service):
    """The claim is compared to, never used as, the identity."""
    data = payload()
    receipt = service.submit(
        data,
        principal=SUBMITTER,
        request_key=KEY,
        claimed_checksum=digest_of(data).upper(),
    )
    assert receipt.checksum == digest_of(data)


# -- artifact and bundle refusals ---------------------------------------------


@pytest.mark.parametrize(
    ("data", "artifact_code"),
    [
        (b"", "empty_artifact"),
        (b"\xef\xbb\xbf{}", "byte_order_mark"),
        (b"PK\x03\x04 not a bundle", "unsupported_container"),
        (b"{not json", "malformed_json"),
    ],
)
def test_unacceptable_bytes_are_refused_before_anything_is_stored(
    service, store, artifacts, data, artifact_code
):
    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(data, principal=SUBMITTER, request_key=KEY)

    assert refusal.value.code == "artifact_rejected"
    assert refusal.value.artifact_code == artifact_code
    assert store.snapshots == {}


def test_a_bundle_from_an_unsupported_deployment_is_refused(service, store):
    document = fx.bundle(
        world={
            "id": OBSERVED_DEPLOYMENT.world_id,
            "title": "The Guild",
            "coreVersion": "13.999",
            "systemId": "dnd5e",
            "systemVersion": "5.3.3",
        }
    )

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(fx.encode(document), principal=SUBMITTER, request_key=KEY)

    assert refusal.value.artifact_code == "unsupported_deployment"
    assert store.snapshots == {}


def test_a_noncanonical_bundle_is_accepted_but_flagged(service):
    """A differently encoded bundle is a valid snapshot with its own identity."""
    import json

    document = fx.bundle()
    data = (json.dumps(document, indent=2) + "\n").encode("utf-8")

    receipt = service.submit(data, principal=SUBMITTER, request_key=KEY)

    assert receipt.canonical_encoding is False
    assert receipt.checksum == digest_of(data)


def test_an_oversized_artifact_is_refused_without_being_hashed(
    service, store, artifacts
):
    from application.foundry.artifact import IngestionLimits

    small = SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
        ingestion_limits=IngestionLimits(max_bytes=32),
    )

    with pytest.raises(SubmissionRefused) as refusal:
        small.submit(payload(), principal=SUBMITTER, request_key=KEY)

    assert refusal.value.artifact_code == "artifact_too_large"
    # Refused before it could be hashed, so there is no identity to report.
    assert refusal.value.checksum is None


# -- request keys and idempotency ---------------------------------------------


@pytest.mark.parametrize("key", ["", "   ", "x" * 256, "with\nnewline", "bell\x07"])
def test_an_unusable_request_key_is_refused(service, store, key):
    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key=key)

    assert refusal.value.code == "invalid_request_key"
    assert store.snapshots == {}


# P4-PG4. `validate_key()` acted on the key before establishing that it was
# text, so a malformed request key left this boundary as a raw `AttributeError`
# or `TypeError` rather than through the documented refusal. This is the third
# production caller of the shared validator; the other two are covered in
# `tests/test_p4_commands.py`.
@pytest.mark.parametrize(
    "key",
    [1, 0, 123, True, False, 1.0, None, b"foundry-module:test-key", ["k"], ("k",)],
)
def test_a_malformed_request_key_keeps_the_documented_refusal(service, store, key):
    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key=key)

    assert refusal.value.code == "invalid_request_key"
    assert store.snapshots == {}
    assert store.idempotency == {}


def test_a_valid_request_key_still_submits_and_is_stored_verbatim(service, store):
    """The guard: the correction narrows malformed input and nothing else."""
    receipt = service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    assert receipt.duplicate is False
    assert len(store.snapshots) == 1
    assert [key for _, key in store.idempotency] == [KEY]


def test_same_key_same_bytes_returns_the_original_receipt(service):
    data = payload()
    first = service.submit(data, principal=SUBMITTER, request_key=KEY)
    second = service.submit(data, principal=SUBMITTER, request_key=KEY)

    assert second.duplicate is True
    assert second.snapshot_id == first.snapshot_id
    assert second.correlation_id == first.correlation_id
    assert second.checksum == first.checksum
    assert second.actor_count == first.actor_count


def test_a_retry_never_creates_a_second_snapshot_or_artifact(service, store, artifacts):
    data = payload()
    service.submit(data, principal=SUBMITTER, request_key=KEY)
    service.submit(data, principal=SUBMITTER, request_key=KEY)

    assert len(store.snapshots) == 1
    assert len(list(artifacts.root.glob("*.json"))) == 1
    assert len(store.idempotency) == 1
    # A same-key retry replays the original receipt before the audit write.
    # Lost-pin recovery must therefore include the first attempt's event.
    assert len(store.audit_events) == 1
    assert store.audit_events[0].payload["duplicate"] is False


def test_same_key_different_bytes_is_a_typed_conflict(service, store):
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    other = fx.encode(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),)))

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(other, principal=SUBMITTER, request_key=KEY)

    assert refusal.value.code == "request_key_conflict"
    assert digest_of(other) not in store.snapshots


def test_same_bytes_under_another_key_is_one_artifact_identity(
    service, store, artifacts
):
    data = payload()
    first = service.submit(data, principal=SUBMITTER, request_key="key-a")
    second = service.submit(data, principal=SUBMITTER, request_key="key-b")

    assert second.snapshot_id == first.snapshot_id
    assert second.duplicate is True
    assert len(store.snapshots) == 1
    assert len(list(artifacts.root.glob("*.json"))) == 1
    # Two attempts, two receipts, one artifact.
    assert len(store.idempotency) == 2
    assert len(store.audit_events) == 2
    assert [event.payload["duplicate"] for event in store.audit_events] == [
        False,
        True,
    ]


def test_the_stored_receipt_is_a_completed_record_of_what_was_returned(service, store):
    receipt = service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    record = store.idempotency[(SUBMISSION_SCOPE, KEY)]
    assert record.status is IdempotencyStatus.COMPLETED
    assert SubmissionReceipt.from_payload(record.response).snapshot_id == receipt.snapshot_id


def test_an_unreadable_stored_receipt_fails_closed(service, store):
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    spent = store.idempotency[(SUBMISSION_SCOPE, KEY)]
    store.idempotency[(SUBMISSION_SCOPE, KEY)] = type(spent)(
        scope=spent.scope,
        key=spent.key,
        request_hash=spent.request_hash,
        status=spent.status,
        response={"status": "pending"},
        # Carried over: only the *response* is being corrupted here. Dropping the
        # admission would make this a test of the fence instead of a test of an
        # unreadable receipt, and the fence has its own file.
        admission_id=spent.admission_id,
    )

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    assert refusal.value.code == "original_result_unavailable"


# -- concurrency --------------------------------------------------------------


def test_losing_the_snapshot_race_resolves_by_re_reading_the_winner(
    store, artifacts, monkeypatch
):
    """A lost race on the checksum resolves to the winner's identity, once.

    The conflict is injected rather than seeded: the losing attempt must
    discover the winner by re-reading, which is the behaviour that distinguishes
    "somebody else got there first" from "assume it was me".
    """
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )
    data = payload()
    winner = service.submit(data, principal=SUBMITTER, request_key="winner")

    # The next attempt believes the checksum is free, then loses the insert —
    # exactly what a concurrent commit between the read and the write looks like.
    raised: list[bool] = []
    real_factory = service._unit_of_work_factory

    class Racing:
        def __init__(self, wrapped):
            self._wrapped = wrapped

        def __enter__(self):
            unit = self._wrapped.__enter__()
            if not raised:
                unit.snapshots = _LosingSnapshots(raised)
            return unit

        def __exit__(self, *args):
            return self._wrapped.__exit__(*args)

    monkeypatch.setattr(
        service, "_unit_of_work_factory", lambda: Racing(real_factory())
    )

    second = service.submit(data, principal=SUBMITTER, request_key="loser")

    assert raised == [True]
    assert second.snapshot_id == winner.snapshot_id
    assert second.duplicate is True
    assert len(store.snapshots) == 1
    assert len(list(artifacts.root.glob("*.json"))) == 1


class _LosingSnapshots:
    """Reports the checksum free, then loses the insert race for it."""

    def __init__(self, raised: list[bool]) -> None:
        self._raised = raised

    def get_by_checksum(self, checksum):
        return None

    def add(self, record):
        self._raised.append(True)
        raise UniquenessConflict("foundry_snapshot.checksum")


def test_an_unresolvable_conflict_is_never_reported_as_a_duplicate(
    store, artifacts, monkeypatch
):
    """A conflict on a rule nobody can resolve refuses, rather than inventing a receipt."""
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )

    class Exploding:
        def __init__(self, wrapped):
            self._wrapped = wrapped

        def __getattr__(self, name):
            return getattr(self._wrapped, name)

        def __enter__(self):
            unit = self._wrapped.__enter__()
            unit.snapshots = _RaisingSnapshots()
            return unit

        def __exit__(self, *args):
            return self._wrapped.__exit__(*args)

    monkeypatch.setattr(service, "_unit_of_work_factory", lambda: Exploding(factory()))

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    assert refusal.value.code == "concurrent_submission"


class _RaisingSnapshots:
    def get_by_checksum(self, checksum):
        return None

    def add(self, record):
        raise UniquenessConflict("something.nobody.classified")


def test_a_persistence_error_is_not_resolved_into_a_successful_no_op(
    store, artifacts, monkeypatch
):
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )

    class Broken:
        def __init__(self, wrapped):
            self._wrapped = wrapped

        def __getattr__(self, name):
            return getattr(self._wrapped, name)

        def __enter__(self):
            unit = self._wrapped.__enter__()
            unit.snapshots = _FailingSnapshots()
            return unit

        def __exit__(self, *args):
            return self._wrapped.__exit__(*args)

    monkeypatch.setattr(service, "_unit_of_work_factory", lambda: Broken(factory()))

    with pytest.raises(PersistenceError):
        service.submit(payload(), principal=SUBMITTER, request_key=KEY)


class _FailingSnapshots:
    def get_by_checksum(self, checksum):
        return None

    def add(self, record):
        raise PersistenceError("08006")


# -- audit --------------------------------------------------------------------


def test_an_accepted_submission_writes_one_safe_audit_event(service, store):
    receipt = service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    (event,) = store.audit_events
    assert event.action == SUBMISSION_ACCEPTED
    assert event.entity_id == receipt.checksum
    assert event.source is AuditSource.FOUNDRY
    assert event.actor_capability is ActorCapability.SERVICE_PRINCIPAL
    assert event.actor_discord_user_id is None
    assert event.correlation_id == receipt.correlation_id
    assert event.payload["service_principal_id"] == "foundry-the-guild"
    assert event.payload["received_via"] == "foundry_module"
    assert event.payload["duplicate"] is False


def test_the_audit_payload_holds_a_digest_and_never_the_request_key(service, store):
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    (event,) = store.audit_events
    assert event.payload["request_key_digest"] == request_key_digest(KEY)
    assert KEY not in str(event.payload)


def test_the_request_key_digest_is_domain_separated_from_the_import_one(service):
    from application.foundry.import_service import request_key_digest as import_digest

    assert request_key_digest(KEY) != import_digest(KEY)


def test_a_refusal_writes_one_refused_event_claiming_no_state(service, store):
    with pytest.raises(SubmissionRefused):
        service.submit(b"{not json", principal=SUBMITTER, request_key=KEY)

    (event,) = store.audit_events
    assert event.action == SUBMISSION_REFUSED
    assert event.payload["refusal_code"] == "artifact_rejected"
    assert event.payload["artifact_code"] == "malformed_json"
    assert event.payload["recorded"] is False
    assert event.payload["service_principal_id"] == "foundry-the-guild"


# -- durability is not confirmed, so nothing is recorded (I-2) ---------------


def test_an_unconfirmed_durability_failure_commits_no_database_state(
    service, store, artifacts, monkeypatch
):
    """Review finding I-2. `_fsync_directory` used to swallow its failures, so a
    submission could reach a durable database commit while the persistence of
    the artifact's directory entry had never been established — a row pointing
    at a rename that a power loss could undo, which is the exact state the
    store-before-record ordering exists to prevent.

    The store now refuses, and the refusal has to leave the database with
    nothing: no snapshot row, no idempotency receipt, no accepted event.
    """
    import os
    import stat as stat_module

    real = os.fsync

    def refuse_directories(descriptor: int) -> None:
        if stat_module.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError(5, "injected directory fsync failure")
        real(descriptor)

    monkeypatch.setattr(os, "fsync", refuse_directories)

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    assert refusal.value.code == "storage_unavailable"
    assert store.snapshots == {}
    assert store.idempotency == {}
    assert [event.action for event in store.audit_events] == [SUBMISSION_REFUSED]


def test_an_unconfirmed_durability_failure_reports_only_what_it_knows(
    service, store, monkeypatch
):
    """It may not claim the filesystem is unchanged: by this point the bytes are
    published under their checksum name and are correct. What it knows is that
    nothing was recorded and that a retry is safe (review finding I-1)."""
    import os
    import stat as stat_module

    real = os.fsync

    def refuse_directories(descriptor: int) -> None:
        if stat_module.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError(5, "injected")
        real(descriptor)

    monkeypatch.setattr(os, "fsync", refuse_directories)

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    message = str(refusal.value)
    assert "nothing was recorded" in message
    assert "safe" in message
    assert "nothing was stored" not in message.lower()
    (event,) = store.audit_events
    assert event.payload["recorded"] is False


def test_a_retry_after_an_unconfirmed_durability_failure_succeeds(
    service, store, artifacts, monkeypatch
):
    """Content addressing is what makes this a retry rather than a second
    submission: the same key and the same bytes complete, against one file."""
    import os
    import stat as stat_module

    real = os.fsync

    def refuse_directories(descriptor: int) -> None:
        if stat_module.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError(5, "injected")
        real(descriptor)

    monkeypatch.setattr(os, "fsync", refuse_directories)
    with pytest.raises(SubmissionRefused):
        service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    monkeypatch.undo()

    receipt = service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    assert receipt.checksum == digest_of(payload())
    assert receipt.duplicate is False
    assert len(store.snapshots) == 1
    assert len(list(artifacts.root.glob("*.json"))) == 1


# -- what a refusal may claim about the filesystem (I-1) ----------------------
#
# The first remediation corrected the two messages a reviewer had named. The
# second review found the rest, so this enumerates *every* `SubmissionRefused`
# path and checks the claim rather than checking the paths somebody remembered.
#
# The ordering is what makes this necessary: `_store_and_record` writes the
# artifact before the transaction commits, so any refusal raised from inside or
# after it may leave a correct content-addressed file that no row points at.


#: Every refusal reachable *after* `_store_and_record` has run, or against state
#: an earlier submission already made durable. None of these may say the
#: filesystem is unchanged, and none may claim that nothing at all was recorded
#: — an earlier winning submission may have recorded a great deal.
AFTER_THE_STORE_HAS_RUN = frozenset(
    {
        "storage_unavailable",
        "concurrent_submission",
        "request_key_conflict",
        "original_result_unavailable",
    }
)

#: Of those, the ones that can also be reached when an *earlier* submission has
#: already recorded something. These may not say "nothing was recorded" without
#: qualification either: they have to name whose attempt they are talking about.
SPEAKS_FOR_ITSELF_ONLY = frozenset(
    {
        "concurrent_submission",
        "request_key_conflict",
        "original_result_unavailable",
    }
)

PROHIBITED_CLAIM = "nothing was stored"


def refuse(service, **kwargs) -> SubmissionRefused:
    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(**kwargs)
    return refusal.value


class _KeyRaceLost:
    """Loses the request-key race, and the winner cannot be read back.

    `_replay_stored`'s unresolvable branch: the conflict names a rule, so a row
    exists, but `find` cannot produce it. Modelled rather than mocked away,
    because this is one of the paths whose message the review found false.
    """

    def __init__(self, wrapped) -> None:
        self._wrapped = wrapped

    def find(self, scope, key):
        return None

    def add(self, record):
        raise UniquenessConflict("idempotency_key.scope_key")


def test_an_unresolvable_key_race_speaks_only_about_this_attempt(
    store, artifacts, monkeypatch
):
    """`_replay_stored`. The store has already run and another submission really
    did record something — so "nothing was stored" was false twice over."""
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )

    class Racing:
        def __init__(self, wrapped):
            self._wrapped = wrapped

        def __getattr__(self, name):
            return getattr(self._wrapped, name)

        def __enter__(self):
            unit = self._wrapped.__enter__()
            unit.idempotency = _KeyRaceLost(unit.idempotency)
            return unit

        def __exit__(self, *args):
            return self._wrapped.__exit__(*args)

    monkeypatch.setattr(service, "_unit_of_work_factory", lambda: Racing(factory()))

    refusal = refuse(
        service, data=payload(), principal=SUBMITTER, request_key=KEY
    )

    assert refusal.code == "concurrent_submission"
    message = str(refusal).lower()
    assert PROHIBITED_CLAIM not in message
    assert "this attempt recorded nothing" in message
    # The bytes really are there, which is why the old wording was wrong.
    assert len(list(artifacts.root.glob("*.json"))) == 1


def test_an_unresolvable_uniqueness_conflict_makes_no_filesystem_claim(
    store, artifacts, monkeypatch
):
    """`_persist`'s final branch — the one the review named by line number."""
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )

    class Exploding:
        def __init__(self, wrapped):
            self._wrapped = wrapped

        def __getattr__(self, name):
            return getattr(self._wrapped, name)

        def __enter__(self):
            unit = self._wrapped.__enter__()
            unit.snapshots = _RaisingSnapshots()
            return unit

        def __exit__(self, *args):
            return self._wrapped.__exit__(*args)

    monkeypatch.setattr(service, "_unit_of_work_factory", lambda: Exploding(factory()))

    refusal = refuse(service, data=payload(), principal=SUBMITTER, request_key=KEY)

    assert refusal.code == "concurrent_submission"
    message = str(refusal).lower()
    assert PROHIBITED_CLAIM not in message
    assert "this attempt recorded nothing" in message
    assert "cannot create a second snapshot" in message
    # `_store_and_record` ran twice before this refusal, and the artifact it
    # wrote is still there. That is the fact the old message denied.
    assert len(list(artifacts.root.glob("*.json"))) == 1


def test_a_spent_key_refusal_does_not_deny_the_earlier_submission(service, artifacts):
    """`request_key_conflict`. Something *was* recorded under this key — by the
    submission that spent it. The refusal has to be about this attempt only."""
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    other = payload(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),)))

    refusal = refuse(service, data=other, principal=SUBMITTER, request_key=KEY)

    assert refusal.code == "request_key_conflict"
    message = str(refusal).lower()
    assert PROHIBITED_CLAIM not in message
    assert "this attempt recorded nothing" in message
    assert "earlier submission's record is unchanged" in message
    assert len(list(artifacts.root.glob("*.json"))) == 1


def test_an_unreadable_receipt_refusal_does_not_deny_the_earlier_submission(
    service, store
):
    """`original_result_unavailable`. The receipt cannot be read; the row it
    belongs to is still there, and so is the artifact it names."""
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    (identity,) = store.idempotency
    record = store.idempotency[identity]
    store.idempotency[identity] = IdempotencyRecord(
        scope=record.scope,
        key=record.key,
        request_hash=record.request_hash,
        status=record.status,
        response={"status": "pending"},
        # Only the response is being corrupted; the receipt still belongs to the
        # generation that earned it.
        admission_id=record.admission_id,
    )

    refusal = refuse(service, data=payload(), principal=SUBMITTER, request_key=KEY)

    assert refusal.code == "original_result_unavailable"
    message = str(refusal).lower()
    assert PROHIBITED_CLAIM not in message
    assert "this attempt recorded nothing" in message
    assert "earlier submission's record is unchanged" in message


def test_an_unconfirmed_durability_refusal_leaves_the_correct_target_in_place(
    service, artifacts, monkeypatch
):
    """The `durability_unconfirmed` case stated as the review asked: the message
    makes no filesystem claim *while* the correct target is demonstrably there,
    unmodified, and is what the retry re-uses."""
    import os
    import stat as stat_module

    data = payload()
    real = os.fsync

    def refuse_directories(descriptor: int) -> None:
        if stat_module.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError(5, "injected")
        real(descriptor)

    monkeypatch.setattr(os, "fsync", refuse_directories)

    refusal = refuse(service, data=data, principal=SUBMITTER, request_key=KEY)

    assert refusal.code == "storage_unavailable"
    assert PROHIBITED_CLAIM not in str(refusal).lower()
    published = artifacts.root / f"{digest_of(data)}.json"
    assert published.read_bytes() == data


def test_a_pre_storage_refusal_may_be_specific_without_being_broad(service):
    """The other direction. A path that genuinely ran before the store may say
    so — narrowly, about the store — rather than reaching for a phrase that is
    only accidentally true here."""
    refusal = refuse(
        service,
        data=payload(),
        principal=SUBMITTER,
        request_key=KEY,
        claimed_checksum="0" * 64,
    )

    message = str(refusal).lower()
    assert refusal.code == "checksum_mismatch"
    assert PROHIBITED_CLAIM not in message
    assert "the artifact store was never asked to hold these bytes" in message


def test_no_refusal_this_service_can_raise_claims_the_filesystem_is_unchanged(
    service, store, artifacts, monkeypatch
):
    """The enumeration itself: every declared refusal code, actually raised.

    A per-message assertion elsewhere proves one path. This proves the set — and
    fails if a code is added to `REFUSAL_CODES` without a way to reach it here,
    which is what stops the enumeration going quietly out of date.
    """
    import os
    import stat as stat_module

    seen: dict[str, str] = {}

    def record(**kwargs) -> None:
        refusal = refuse(service, **kwargs)
        seen[refusal.code] = str(refusal)

    record(data=b"{not json", principal=SUBMITTER, request_key=KEY)
    record(data=payload(), principal=SUBMITTER, request_key="")
    record(
        data=payload(),
        principal=SUBMITTER,
        request_key=KEY,
        claimed_checksum="0" * 64,
    )
    service.submit(payload(), principal=SUBMITTER, request_key="spent")
    record(
        data=payload(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),))),
        principal=SUBMITTER,
        request_key="spent",
    )

    (identity,) = [key for key in store.idempotency if key[1] == "spent"]
    original = store.idempotency[identity]
    store.idempotency[identity] = IdempotencyRecord(
        scope=original.scope,
        key=original.key,
        request_hash=original.request_hash,
        status=original.status,
        response={"status": "pending"},
        admission_id=original.admission_id,
    )
    record(data=payload(), principal=SUBMITTER, request_key="spent")
    store.idempotency[identity] = original

    # C-24. The fence, reached the way an operator reaches it: the generation is
    # closed between two submissions. Reopened afterwards — which no real
    # deployment can do — because every later branch in this enumeration needs a
    # credential that can still write.
    admission = close_admission(store, SUBMITTER.principal_id)
    record(data=payload(), principal=SUBMITTER, request_key="fenced")
    store.submission_admissions[SUBMITTER.principal_id] = replace(
        admission, state=AdmissionState.OPEN
    )

    class Exploding:
        def __init__(self, wrapped):
            self._wrapped = wrapped

        def __getattr__(self, name):
            return getattr(self._wrapped, name)

        def __enter__(self):
            unit = self._wrapped.__enter__()
            unit.snapshots = _RaisingSnapshots()
            return unit

        def __exit__(self, *args):
            return self._wrapped.__exit__(*args)

    real_factory = service._unit_of_work_factory
    monkeypatch.setattr(
        service, "_unit_of_work_factory", lambda: Exploding(real_factory())
    )
    record(
        data=payload(fx.bundle(actors=(fx.actor(fx.THIRD_ACTOR_ID),))),
        principal=SUBMITTER,
        request_key="raced",
    )
    monkeypatch.undo()

    real = os.fsync

    def refuse_directories(descriptor: int) -> None:
        if stat_module.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError(5, "injected")
        real(descriptor)

    monkeypatch.setattr(os, "fsync", refuse_directories)
    record(
        data=payload(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),))),
        principal=SUBMITTER,
        request_key="durability",
    )
    monkeypatch.undo()

    assert set(seen) == REFUSAL_CODES, (
        "every declared refusal code must be reachable here, so that the claim "
        "each one makes is checked rather than assumed"
    )
    for code, message in seen.items():
        assert PROHIBITED_CLAIM not in message.lower(), code
    for code in AFTER_THE_STORE_HAS_RUN:
        assert "record" in seen[code].lower(), (
            f"{code} can be raised after the artifact was published, so what it "
            "establishes is about the record, not about the filesystem"
        )
    for code in SPEAKS_FOR_ITSELF_ONLY:
        assert "this attempt" in seen[code].lower(), (
            f"{code} can be raised while another submission's record exists, so "
            "it must name whose attempt recorded nothing"
        )


def test_every_refusal_code_is_declared(service, store):
    """No refusal escapes with a code outside the closed vocabulary."""
    attempts = [
        (b"{not json", KEY),
        (payload(), ""),
    ]
    seen = set()
    for data, key in attempts:
        with pytest.raises(SubmissionRefused) as refusal:
            service.submit(data, principal=SUBMITTER, request_key=key)
        seen.add(refusal.value.code)
    assert seen <= REFUSAL_CODES


def test_the_declared_artifact_codes_are_exactly_the_parser_s(service):
    """A new parser refusal cannot slip into audit history unclassified."""
    found: set[str] = set()
    for name in ("artifact.py", "parser.py"):
        source = (
            Path(__file__).resolve().parents[1]
            / "application"
            / "foundry"
            / name
        ).read_text()
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            function = node.func
            called = (
                function.id
                if isinstance(function, ast.Name)
                else getattr(function, "attr", None)
            )
            if called not in {"SnapshotRejected", "refuse"}:
                continue
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                found.add(first.value)
    assert found == set(ARTIFACT_REFUSAL_CODES)


def test_foundry_module_refusal_codes_match_the_real_submission_boundary():
    """A server boundary change cannot silently become a generic client error."""
    root = Path(__file__).resolve().parents[1]
    wsgi = ast.parse((root / "adapters/http/wsgi.py").read_text())
    boundary_codes = set(REFUSAL_CODES)

    # These are the WSGI paths that can answer a snapshot POST (plus routing
    # refusals for the configured endpoint). Preview has its own caller and
    # vocabulary and is deliberately excluded.
    for node in wsgi.body:
        if not isinstance(node, ast.ClassDef) or node.name != "SnapshotSubmissionApplication":
            continue
        for function in node.body:
            if not isinstance(function, ast.FunctionDef) or function.name not in {
                "__call__", "_route", "_submit"
            }:
                continue
            for call in ast.walk(function):
                if not isinstance(call, ast.Call) or not call.args:
                    continue
                called = getattr(call.func, "id", getattr(call.func, "attr", None))
                first = call.args[0]
                if (
                    called == "_error"
                    and isinstance(first, ast.Constant)
                    and isinstance(first.value, str)
                ):
                    boundary_codes.add(first.value)

    # Submission authorization supplies this typed dynamic code; artifact
    # size is produced by both the WSGI read bound and parser classification.
    boundary_codes.update({"out_of_scope", "artifact_too_large"})

    transport = (root / "foundry-module/scripts/transport.js").read_text()
    declaration = re.search(
        r"SERVER_REFUSAL_CODES\s*=\s*new Set\(\[(.*?)\]\)",
        transport,
        re.DOTALL,
    )
    assert declaration is not None
    module_codes = set(re.findall(r'"([a-z][a-z0-9_]*)"', declaration.group(1)))

    assert module_codes == boundary_codes, (
        f"missing from module: {sorted(boundary_codes - module_codes)}; "
        f"not exposed by server: {sorted(module_codes - boundary_codes)}"
    )


def test_foundry_module_artifact_codes_match_the_parser_contract():
    """A new diagnostic code cannot become hidden or attacker-controlled."""
    root = Path(__file__).resolve().parents[1]
    transport = (root / "foundry-module/scripts/transport.js").read_text()
    declaration = re.search(
        r"SERVER_ARTIFACT_CODES\s*=\s*new Set\(\[(.*?)\]\)",
        transport,
        re.DOTALL,
    )
    assert declaration is not None
    module_codes = set(re.findall(r'"([a-z][a-z0-9_]*)"', declaration.group(1)))

    assert module_codes == set(ARTIFACT_REFUSAL_CODES), (
        f"missing from module: {sorted(set(ARTIFACT_REFUSAL_CODES) - module_codes)}; "
        f"not emitted by server: {sorted(module_codes - set(ARTIFACT_REFUSAL_CODES))}"
    )


def test_both_submission_actions_have_an_enforced_payload_policy():
    assert SUBMISSION_ACCEPTED in POLICIES
    assert SUBMISSION_REFUSED in POLICIES
    assert "request_key" not in POLICIES[SUBMISSION_ACCEPTED].allowed
    assert "request_key" not in POLICIES[SUBMISSION_REFUSED].allowed


# -- the one fenced replay boundary (review finding C-24-R1) ------------------
#
# A stored successful receipt is a durable acceptance being handed back, so the
# invariant forbids returning one after the presenting credential's generation
# has closed exactly as it forbids writing a new row. Two branches could return
# one — an ordinary same-key retry, and recovery after a lost
# `idempotency_key.scope_key` race — and only the first checked. These tests
# cover both callers of the single boundary that now answers for them, and the
# structural assertion that no third branch can appear.


class _LosesTheKeyRace:
    """The request-key race, as the loser experiences it.

    `find` answers `None` because the winner had not committed when this
    transaction looked, and `add` raises exactly the rule
    `adapters/database/translation.py` produces for a real 23505. `on_conflict`
    runs at the instant the race is lost, which is where a settlement commits in
    the counterexample: the loser's transaction has just been rolled back, so it
    holds no lock and nothing delays the closure.

    Installed on the **first** unit of work only. Every later one — the fenced
    replay, the refusal record — is the ordinary fake, so what the replay reads
    is the winner's committed row and the admission's committed state.
    """

    def __init__(self, wrapped, on_conflict) -> None:
        self._wrapped = wrapped
        self._on_conflict = on_conflict

    def find(self, scope, key):
        return None

    def add(self, record):
        if self._on_conflict is not None:
            self._on_conflict()
        raise UniquenessConflict("idempotency_key.scope_key")


class _RacingUnit:
    def __init__(self, wrapped, on_conflict) -> None:
        self._wrapped = wrapped
        self._on_conflict = on_conflict

    def __getattr__(self, name):
        return getattr(self._wrapped, name)

    def __enter__(self):
        unit = self._wrapped.__enter__()
        unit.idempotency = _LosesTheKeyRace(unit.idempotency, self._on_conflict)
        return unit

    def __exit__(self, *args):
        return self._wrapped.__exit__(*args)


def lose_the_key_race(service, factory, monkeypatch, *, on_conflict=None) -> None:
    """Make this service's next submission lose the request-key race."""
    opened = {"count": 0}

    def build():
        unit = factory()
        opened["count"] += 1
        return _RacingUnit(unit, on_conflict) if opened["count"] == 1 else unit

    monkeypatch.setattr(service, "_unit_of_work_factory", build)


def test_a_lost_key_race_cannot_replay_a_receipt_across_a_closure(
    store, artifacts, monkeypatch
):
    """**The C-24-R1 counterexample.** Two requests, one key, then settlement.

    The winner commits its receipt while the generation is open. The loser's
    transaction is rolled back by the uniqueness conflict, releasing the shared
    lock; settlement then closes the generation and commits; and only then does
    the loser go looking for the winner's receipt.

    Before the remediation it got one, because recovery from the race read the
    row in a bare transaction: no lock, no admission, no generation check. The
    invariant forbids that as squarely as it forbids a post-closure write, and
    a module that received it would report success for an episode the operator
    has already recorded as settled.
    """
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )
    winner = service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    accepted = len(store.audit_events)

    lose_the_key_race(
        service,
        factory,
        monkeypatch,
        on_conflict=lambda: close_admission(store, SUBMITTER.principal_id),
    )

    refusal = refuse(service, data=payload(), principal=SUBMITTER, request_key=KEY)

    assert refusal.code == "admission_closed"
    # Nothing of the loser's survives, and nothing of the winner's is retracted.
    assert len(store.snapshots) == 1
    assert len(store.idempotency) == 1
    assert store.idempotency[(SUBMISSION_SCOPE, KEY)].response["snapshot_id"] == str(
        winner.snapshot_id
    )
    accepted_events = [
        event for event in store.audit_events if event.action == SUBMISSION_ACCEPTED
    ]
    assert len(accepted_events) == accepted


def test_a_lost_key_race_replays_the_winner_while_the_generation_is_open(
    store, artifacts, monkeypatch
):
    """The control. Without the closure the loser still gets its answer.

    This is what makes the test above about the fence rather than about the
    race: the same interleaving, one committed closure apart, and the ordinary
    idempotent outcome is unchanged.
    """
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )
    winner = service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    lose_the_key_race(service, factory, monkeypatch)
    loser = service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    assert loser.snapshot_id == winner.snapshot_id
    assert loser.correlation_id == winner.correlation_id
    assert loser.duplicate is True
    assert len(store.snapshots) == 1
    assert len(store.idempotency) == 1


def test_a_lost_key_race_refuses_a_receipt_earned_by_another_admission(
    store, artifacts, monkeypatch
):
    """The race path is bound to the *presenting* credential, not the record.

    `(scope, key)` is one namespace across every credential, so the recovery
    credential can lose a race for a key the old generation spent. Answering
    would hand the new generation a receipt describing the old one's acceptance
    — and it is the record's own `admission_id` that refuses, which is why
    authorization may never be recovered from the row being replayed.
    """
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    close_admission(store, SUBMITTER.principal_id)
    recovery = ServicePrincipal(
        principal_id="foundry-the-guild-r1",
        scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
    )
    admit(store, recovery.principal_id, generation=2)

    lose_the_key_race(service, factory, monkeypatch)
    refusal = refuse(service, data=payload(), principal=recovery, request_key=KEY)

    assert refusal.code == "admission_closed"
    assert refusal.admission_generation == 2, "the generation it *does* hold"
    assert len(store.idempotency) == 1


def test_a_same_key_retry_refuses_a_receipt_earned_by_another_admission(
    store, artifacts
):
    """The other caller of the boundary, reaching the same check.

    An ordinary retry — no race at all — carrying a key the old generation spent
    into a credential that holds a new one. `_store_and_record` no longer
    answers this itself; it hands the question to the same fenced operation the
    race uses, which is the point of the consolidation.
    """
    service = SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    close_admission(store, SUBMITTER.principal_id)
    recovery = ServicePrincipal(
        principal_id="foundry-the-guild-r1",
        scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
    )
    admit(store, recovery.principal_id, generation=2)

    refusal = refuse(service, data=payload(), principal=recovery, request_key=KEY)

    assert refusal.code == "admission_closed"
    assert refusal.admission_generation == 2
    assert len(store.idempotency) == 1


def test_a_lost_key_race_still_refuses_a_key_spent_on_other_bytes(
    store, artifacts, monkeypatch
):
    """Consolidation did not lose the digest check the race path always had."""
    factory = unit_of_work_factory(store)
    service = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )
    service.submit(payload(), principal=SUBMITTER, request_key=KEY)

    lose_the_key_race(service, factory, monkeypatch)
    refusal = refuse(
        service,
        data=payload(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),))),
        principal=SUBMITTER,
        request_key=KEY,
    )

    assert refusal.code == "request_key_conflict"


def _module_tree() -> ast.Module:
    return ast.parse(
        (
            Path(__file__).resolve().parents[1]
            / "application"
            / "foundry"
            / "submission.py"
        ).read_text()
    )


def _callers_of(module: ast.Module, names: set[str]) -> dict[str, set[str]]:
    """For each name, the functions in this module that call it."""
    found: dict[str, set[str]] = {name: set() for name in names}
    for node in ast.walk(module):
        if not isinstance(node, ast.FunctionDef):
            continue
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            called = getattr(call.func, "id", getattr(call.func, "attr", None))
            if called in found:
                found[called].add(node.name)
    return found


def test_no_stored_receipt_is_returned_outside_the_one_fenced_boundary():
    """**Review finding C-24-R1 as a structural assertion, not a habit.**

    The defect was never a missing `if`. It was that two branches could each
    turn a stored record back into a successful receipt, so the invariant lived
    in whichever of them a later author remembered — and one of them did not.

    So this enumerates the production paths mechanically instead of trusting a
    reading. A `SubmissionReceipt` is constructed in exactly two places: the
    acceptance that earns one, and the rebuild of a stored one. The rebuild is
    called from exactly one place, and that place is the fenced boundary. A
    future conflict-recovery branch that reads a receipt back for itself fails
    here whether or not its author remembered the admission.
    """
    module = _module_tree()
    callers = _callers_of(module, {"_replay", "from_payload", "SubmissionReceipt"})

    assert callers["SubmissionReceipt"] == {"_store_and_record", "_replay"}, (
        "a receipt is constructed by the acceptance that earns it and by the "
        "rebuild of a stored one, and nowhere else"
    )
    assert callers["from_payload"] == {"_replay"}
    assert callers["_replay"] == {"_fenced_replay"}


def test_the_fenced_boundary_performs_the_whole_principal_bound_check():
    """The boundary is only worth consolidating on if it is complete.

    Named calls and attributes rather than behaviour, deliberately: the
    behavioural tests above prove each check refuses, and this proves they are
    all in the one operation those tests exercise — so removing one is a test
    failure here even if some other path happens to still refuse.
    """
    module = _module_tree()
    boundary = next(
        node
        for node in ast.walk(module)
        if isinstance(node, ast.FunctionDef) and node.name == "_fenced_replay"
    )
    called = {
        getattr(call.func, "id", getattr(call.func, "attr", None))
        for call in ast.walk(boundary)
        if isinstance(call, ast.Call)
    }
    read = {node.attr for node in ast.walk(boundary) if isinstance(node, ast.Attribute)}

    # The lock, taken before any receipt is read; the admission resolved from
    # the authenticated principal's own id; the openness test; the check that
    # the stored record was earned under that admission; and the digest check.
    assert "hold_against_closure" in called
    assert "find_for_principal" in called
    assert "_replay" in called
    assert {"principal_id", "is_open", "admission_id"} <= read

    statements = [
        node
        for node in boundary.body
        if isinstance(node, ast.With)
    ]
    assert statements, "the boundary must own one transaction"
    first = statements[0].body[0]
    assert (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Call)
        and getattr(first.value.func, "attr", None) == "hold_against_closure"
    ), "the fence lock must be the transaction's first statement"


# -- receipt round trip -------------------------------------------------------


def test_a_receipt_round_trips_through_its_stored_payload(service):
    receipt = service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    assert SubmissionReceipt.from_payload(receipt.as_payload()) == receipt


@pytest.mark.parametrize(
    "mutate",
    [
        lambda payload: payload.pop("checksum"),
        lambda payload: payload.update(extra=1),
        lambda payload: payload.update(status="applied"),
        lambda payload: payload.update(actor_count="two"),
        lambda payload: payload.update(snapshot_id="not-a-uuid"),
        lambda payload: payload.update(duplicate="yes"),
        lambda payload: payload.update(folders=[{"folder_id": "x"}]),
    ],
)
def test_a_malformed_stored_receipt_is_never_patched_up(service, mutate):
    from application.foundry.submission import SubmissionReceiptError

    stored = service.submit(payload(), principal=SUBMITTER, request_key=KEY).as_payload()
    mutate(stored)

    with pytest.raises(SubmissionReceiptError):
        SubmissionReceipt.from_payload(stored)


def test_a_receipt_identifier_is_a_uuid(service):
    receipt = service.submit(payload(), principal=SUBMITTER, request_key=KEY)
    assert isinstance(receipt.snapshot_id, UUID)
    assert isinstance(receipt.correlation_id, UUID)
