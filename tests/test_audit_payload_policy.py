"""What may reach an append-only audit row, asserted per action (finding I-2).

The arrangement this replaces was one test, over one action
(`snapshot_import.applied`), asserting `set(payload) <= allowed`. Three things
were wrong with it and each is covered here:

- **it accepted any subset**, so an empty payload passed and a key silently
  disappearing was invisible. Every policy below has *required* keys, and both
  directions are asserted;
- **it omitted refusals and character creation.** The latter was carrying an
  Actor-derived `display_name` that no policy had ever considered;
- **it used the ordinary fixture**, whose values are plausible. These tests use
  an adversarial Actor whose every field is a marker string, so "the value did
  not leak" is an assertion rather than a coincidence of the fixture.

The policy itself is enforced at the point of writing by
`application/foundry/audit_policy.enforced`, so these tests check a rule the
code applies rather than a convention the code merely happens to follow.
`test_the_policy_is_enforced_when_the_row_is_written` is what holds that.
"""
from __future__ import annotations

import pytest

from application.foundry import audit_policy
from application.foundry.audit_policy import (
    BOOTSTRAP_COMPLETED,
    BOOTSTRAP_REFUSED,
    CHARACTER_CREATED,
    IMPORT_APPLIED,
    IMPORT_REFUSED,
    POLICIES,
    AuditPolicyError,
    enforced,
)
from application.foundry.import_service import ImportRefused, REFUSAL_CODES
from application.foundry.reconciliation import ISSUE_CODES
from domain.foundry_profile import PROFILE
from tests import foundry_fixtures as fx
from tests import snapshot_harness as harness

#: Every one of these is a value the platform must never copy into permanent
#: history. They are planted in the Actor's *game-state* fields — name, race,
#: class, background, feat, bastion, item — which is exactly the data an import
#: reads and must not record.
MARKERS = {
    "name": "MARKER-NAME'; DROP TABLE audit_events;--",
    "race": "MARKER-RACE",
    "class_identifier": "marker-class",
    "class_name": "MARKER-CLASSNAME",
    "background": "MARKER-BACKGROUND",
    "feat": "MARKER-FEAT",
    "item": "MARKER-ITEM postgresql://user:pw@host/db",
    "language": "MARKER-LANGUAGE",
}


def adversarial_actor(actor_id: str = fx.FIRST_ACTOR_ID) -> dict:
    return fx.actor(
        actor_id,
        name=MARKERS["name"],
        race=MARKERS["race"],
        class_identifier=MARKERS["class_identifier"],
        class_name=MARKERS["class_name"],
        background=MARKERS["background"],
        feats=(MARKERS["feat"],),
        custom_languages=MARKERS["language"],
        magic_items=(fx.magic_item(MARKERS["item"]),),
    )


def adversarial_bundle():
    return fx.bundle(actors=(adversarial_actor(),))


def apply_adversarial(bench, *, request_key="req-1"):
    artifact = bench.artifact(adversarial_bundle())
    preview = bench.imports.preview(artifact, request_key=request_key)
    return artifact, bench.imports.apply(
        artifact, preview, discord_user_id=harness.COUNCIL_USER
    )


def events(bench, action: str):
    return [event for event in bench.store.audit_events if event.action == action]


def payload_of(bench, action: str):
    matching = events(bench, action)
    assert matching, f"no {action} event was recorded"
    return dict(matching[0].payload)


# -- the policy applies to both directions, for every action -------------------


@pytest.mark.parametrize("action", sorted(POLICIES), ids=lambda value: value)
def test_every_policy_declares_at_least_one_required_key(action: str):
    """A policy with nothing required is the defect this replaces."""
    assert POLICIES[action].required, f"{action} would accept an empty payload"


def test_an_unapproved_key_is_refused():
    with pytest.raises(AuditPolicyError, match="unapproved key"):
        enforced(
            CHARACTER_CREATED,
            {
                "snapshot_checksum": "a" * 64,
                "profile_version": PROFILE.version,
                "external_actor_id": fx.FIRST_ACTOR_ID,
                "folder_id": fx.ACTIVE_FOLDER_ID,
                "display_name": "Somebody",
            },
        )


def test_a_missing_required_key_is_refused():
    """The direction the previous test could not see."""
    with pytest.raises(AuditPolicyError, match="missing required key"):
        enforced(CHARACTER_CREATED, {"snapshot_checksum": "a" * 64})


def test_an_empty_payload_is_refused():
    for action in POLICIES:
        with pytest.raises(AuditPolicyError):
            enforced(action, {})


def test_an_action_with_no_policy_cannot_write_at_all():
    with pytest.raises(AuditPolicyError, match="no audit payload policy"):
        enforced("snapshot_import.something_new", {"anything": 1})


def test_the_policy_is_enforced_when_the_row_is_written(monkeypatch):
    """Not merely available to be checked afterwards.

    Driven by breaking the summary the applied payload is built from: a key
    nobody approved appears in it, and the *apply* must fail. If the policy were
    only a test rather than the write path's own rule, the row would simply be
    recorded and this would pass.
    """
    from application.foundry.reconciliation import ReconciliationReport

    original = ReconciliationReport.summary
    monkeypatch.setattr(
        ReconciliationReport,
        "summary",
        lambda self: {**original(self), "actor_names": ["Brightlantern"]},
    )
    bench = harness.build()
    artifact = bench.artifact()
    preview = bench.imports.preview(artifact, request_key="req-1")

    with pytest.raises(AuditPolicyError):
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    # …and the transaction that would have written it rolled back with it.
    assert bench.store.audit_events == []
    assert bench.store.characters == {}
    assert bench.store.snapshot_imports == []


# -- applied -------------------------------------------------------------------


def test_the_applied_payload_holds_exactly_its_policy():
    bench = harness.build()

    apply_adversarial(bench)
    payload = payload_of(bench, IMPORT_APPLIED)
    policy = POLICIES[IMPORT_APPLIED]

    assert policy.required <= set(payload)
    assert set(payload) <= policy.allowed
    assert set(payload) - policy.allowed == set()


def test_the_applied_payload_carries_no_actor_value():
    bench = harness.build()

    apply_adversarial(bench)
    rendered = repr(payload_of(bench, IMPORT_APPLIED))

    for marker in MARKERS.values():
        assert marker not in rendered, f"{marker!r} reached the applied audit row"


def test_the_applied_payload_carries_no_sql_credential_or_traceback():
    bench = harness.build()

    apply_adversarial(bench)
    rendered = repr(payload_of(bench, IMPORT_APPLIED))

    for unsafe in (
        "DROP TABLE",
        "postgresql://",
        "Traceback",
        "psycopg",
        "[SQL:",
        "password",
    ):
        assert unsafe not in rendered


def test_the_applied_payloads_vocabularies_are_closed():
    """`issue_codes` and the deferred map are vocabularies, not free text."""
    bench = harness.build()
    bench.add_character("Old Name", actor_id=fx.FIRST_ACTOR_ID)

    apply_adversarial(bench)
    payload = payload_of(bench, IMPORT_APPLIED)

    assert set(payload["issue_codes"]) <= ISSUE_CODES
    assert set(payload["fields_differing"]) <= set(PROFILE.fields)
    assert set(payload["legacy_authority_deferred"]) <= set(PROFILE.fields)
    assert set(payload["legacy_authority_deferred"].values()) <= set(
        PROFILE.owning_packages().values()
    )


# -- S-1: the request key is minimized before it reaches permanent history -----
#
# The security review found that `request_key` accepts any printable text up to
# 255 characters and was copied verbatim into the applied audit payload. Length
# and control-character validation stop a row being corrupted; they do nothing
# about a caller putting a player name, an address or a credential into
# append-only history that Council and Platform Administrators can search.
#
# Everything below uses a synthetic key. The address is in `.invalid`, which is
# reserved and can never resolve, and the name and token-shaped string were
# invented here. No real credential or personal datum is in this file.

PRIVATE_LOOKING_KEY = (
    "MARKER-KEY player=Testperson Nobody email=nobody@example.invalid "
    "token=MARKER-TOKEN-abcdef0123456789"
)

#: Checked one at a time, so the assertion cannot pass merely because the whole
#: string was re-spaced or truncated somewhere on the way in.
PRIVATE_FRAGMENTS = (
    "MARKER-KEY",
    "Testperson Nobody",
    "nobody@example.invalid",
    "MARKER-TOKEN-abcdef0123456789",
    "player=",
    "email=",
    "token=",
)


def test_the_applied_payload_carries_a_digest_and_never_the_request_key():
    from application.foundry.import_service import request_key_digest

    bench = harness.build()

    apply_adversarial(bench, request_key=PRIVATE_LOOKING_KEY)
    payload = payload_of(bench, IMPORT_APPLIED)

    assert payload["request_key_digest"] == request_key_digest(PRIVATE_LOOKING_KEY)
    assert "request_key" not in payload
    for fragment in PRIVATE_FRAGMENTS:
        assert fragment not in repr(payload)


def test_the_raw_key_stays_in_the_lookup_column_and_reaches_no_audit_row():
    """Where it is kept, and the total over everything permanent."""
    bench = harness.build()

    apply_adversarial(bench, request_key=PRIVATE_LOOKING_KEY)

    # Kept exactly where the idempotency lookup needs it, and there only.
    assert [r.request_key for r in bench.store.snapshot_imports] == [
        PRIVATE_LOOKING_KEY
    ]
    rendered = repr(
        [
            (event.action, event.entity_id, dict(event.payload))
            for event in bench.store.audit_events
        ]
    )
    assert bench.store.audit_events
    for fragment in PRIVATE_FRAGMENTS:
        assert fragment not in rendered, f"{fragment!r} reached an audit row"
    # …nor into the immutable import record's own summary.
    for record in bench.store.snapshot_imports:
        for fragment in PRIVATE_FRAGMENTS:
            assert fragment not in repr(dict(record.summary))


def test_the_digest_is_deterministic_and_distinguishes_distinct_keys():
    from application.foundry.import_service import request_key_digest

    keys = [
        PRIVATE_LOOKING_KEY,
        PRIVATE_LOOKING_KEY + " ",
        PRIVATE_LOOKING_KEY.upper(),
        "req-1",
        "req-2",
        "council-interaction-12345",
        "",
    ]
    digests = [request_key_digest(key) for key in keys]

    # Deterministic for the same key…
    assert digests == [request_key_digest(key) for key in keys]
    # …and no collision across the matrix, so it identifies an attempt.
    assert len(set(digests)) == len(keys)
    assert all(len(digest) == 64 for digest in digests)
    # Domain-separated: not the bare SHA-256 of the key, so it cannot be
    # confused with, or looked up against, a digest of the same text elsewhere.
    import hashlib

    assert request_key_digest("req-1") != hashlib.sha256(b"req-1").hexdigest()


def test_the_policy_rejects_the_old_raw_request_key_outright():
    """Not deprecated, not optional: undeclared, so `enforced()` refuses it."""
    bench = harness.build()
    artifact = bench.artifact(adversarial_bundle())
    preview = bench.imports.preview(artifact, request_key="req-1")
    payload = dict(payload_of_would_be(bench, artifact, preview))

    assert "request_key" not in POLICIES[IMPORT_APPLIED].allowed
    with pytest.raises(AuditPolicyError, match="unapproved key"):
        enforced(IMPORT_APPLIED, {**payload, "request_key": "req-1"})
    # And the policy's required set is exactly what the write site produces.
    assert set(payload) - POLICIES[IMPORT_APPLIED].allowed == set()
    assert POLICIES[IMPORT_APPLIED].required <= set(payload)


def payload_of_would_be(bench, artifact, preview):
    """The applied payload this apply actually writes, captured from history."""
    bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)
    return payload_of(bench, IMPORT_APPLIED)


@pytest.mark.parametrize(
    "provoke",
    ["applied", "duplicate", "refused", "concurrent"],
    ids=lambda value: value,
)
def test_no_path_puts_the_raw_key_into_audit_or_safe_error_output(provoke: str):
    """Applied, duplicate, refused and concurrent, over one adversarial key."""
    from application.errors import UniquenessConflict

    bench = harness.build()
    artifact = bench.artifact(adversarial_bundle())
    messages: list[str] = []

    if provoke == "applied":
        apply_adversarial(bench, request_key=PRIVATE_LOOKING_KEY)
    elif provoke == "duplicate":
        apply_adversarial(bench, request_key=PRIVATE_LOOKING_KEY)
        apply_adversarial(bench, request_key=PRIVATE_LOOKING_KEY)
    elif provoke == "refused":
        apply_adversarial(bench, request_key=PRIVATE_LOOKING_KEY)
        other = bench.artifact(fx.bundle(actors=(adversarial_actor(fx.SECOND_ACTOR_ID),)))
        preview = bench.imports.preview(other, request_key=PRIVATE_LOOKING_KEY)
        with pytest.raises(ImportRefused) as refusal:
            bench.imports.apply(other, preview, discord_user_id=harness.COUNCIL_USER)
        assert refusal.value.code == "request_key_conflict"
        messages.append(str(refusal.value))
    else:
        preview = bench.imports.preview(artifact, request_key=PRIVATE_LOOKING_KEY)
        bench.factory.fail_on = "external_actor_mappings"
        bench.factory.failure = UniquenessConflict("external_actor_mapping.world_actor")
        with pytest.raises(ImportRefused) as refusal:
            bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)
        assert refusal.value.code == "concurrent_import"
        messages.append(str(refusal.value))

    rendered = repr(
        [dict(event.payload) for event in bench.store.audit_events]
    ) + repr([dict(record.summary) for record in bench.store.snapshot_imports])
    assert bench.store.audit_events
    for fragment in PRIVATE_FRAGMENTS:
        assert fragment not in rendered, f"{fragment!r} reached permanent history"
        for message in messages:
            assert fragment not in message, f"{fragment!r} reached a safe message"


def test_traceability_survives_the_minimization():
    """An event can still be tied to its attempt, its operation and its run.

    The three identifiers answer three different questions, which is why the
    digest is not a duplicate of one of the others: the correlation id is per
    attempt and so cannot group a retry with its original, and the operation
    digest deliberately excludes the key and so cannot group by attempt at all.
    """
    from application.foundry.import_service import request_key_digest

    bench = harness.build()

    _, outcome = apply_adversarial(bench, request_key=PRIVATE_LOOKING_KEY)
    event = events(bench, IMPORT_APPLIED)[0]
    record = bench.store.snapshot_imports[0]

    # Attempt identity, without the key: the digest links the event to the row
    # holding the key, and to any later event recorded under the same key.
    assert event.payload["request_key_digest"] == request_key_digest(
        record.request_key
    )
    # Operation identity: what was applied.
    assert event.payload["operation_digest"] == record.operation_digest
    assert event.payload["operation_digest"] == outcome.operation_digest
    # Run identity: this attempt's own events, including its character creations.
    assert event.correlation_id == record.correlation_id
    assert all(
        created.correlation_id == record.correlation_id
        for created in events(bench, CHARACTER_CREATED)
    )


# -- character creation --------------------------------------------------------


def test_the_created_character_payload_holds_exactly_its_policy():
    bench = harness.build()

    apply_adversarial(bench)
    payload = payload_of(bench, CHARACTER_CREATED)
    policy = POLICIES[CHARACTER_CREATED]

    assert set(payload) == policy.required
    assert policy.optional == frozenset()


def test_the_created_character_payload_no_longer_carries_a_display_name():
    """The I-2 decision, asserted as the absence it is.

    Identity evidence is `entity_id` — the platform's own UUID — plus the Actor
    id, folder and snapshot that establish where the character came from. The
    display name is mutable, Actor-derived, already stored on `characters`, and
    is the one field B-2 shows goes stale. It is not identity evidence.
    """
    bench = harness.build()

    apply_adversarial(bench)
    event = events(bench, CHARACTER_CREATED)[0]

    assert "display_name" not in event.payload
    assert MARKERS["name"] not in repr(dict(event.payload))
    # …and the identity it *does* carry is the platform's own.
    character_id = next(iter(bench.store.characters))
    assert event.entity_id == str(character_id)
    assert event.payload["external_actor_id"] == fx.FIRST_ACTOR_ID


def test_no_audit_row_anywhere_carries_an_actor_value():
    """The total, rather than one action at a time."""
    bench = harness.build()

    apply_adversarial(bench)
    rendered = repr(
        [dict(event.payload) for event in bench.store.audit_events]
    )

    assert bench.store.audit_events
    for marker in MARKERS.values():
        assert marker not in rendered


# -- refusals, including the new conflict and concurrency events ---------------


def refuse(bench, *, code_expected: str):
    """Provoke a recorded refusal and return its payload."""
    artifact = bench.artifact(
        fx.bundle(
            folders=(
                fx.folder(fx.ACTIVE_FOLDER_ID, "Characters (active)"),
                fx.folder(fx.ARCHIVE_FOLDER_ID, "Characters (retired)"),
            ),
            selected_folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID),
            actors=(
                adversarial_actor(),
                adversarial_actor(fx.SECOND_ACTOR_ID),
            ),
        )
    )
    preview = bench.imports.preview(
        artifact, request_key="req-1", folder_id=fx.ACTIVE_FOLDER_ID
    )
    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(
            artifact,
            preview,
            discord_user_id=harness.COUNCIL_USER,
            folder_id=fx.ARCHIVE_FOLDER_ID,
        )
    assert refusal.value.code == code_expected
    return payload_of(bench, IMPORT_REFUSED)


def test_the_refused_payload_holds_exactly_its_policy():
    bench = harness.build()

    payload = refuse(bench, code_expected="stale_preview")
    policy = POLICIES[IMPORT_REFUSED]

    assert set(payload) == policy.required
    assert payload["applied"] is False


def test_the_refused_payload_carries_no_actor_value_or_refusal_prose():
    """A refusal message names the inputs that moved; the row records a code."""
    bench = harness.build()

    payload = refuse(bench, code_expected="stale_preview")
    rendered = repr(payload)

    for marker in MARKERS.values():
        assert marker not in rendered
    # The message is for the operator in the moment, not for permanent history.
    assert "reason" not in payload
    assert "message" not in payload
    for unsafe in ("Traceback", "psycopg", "[SQL:", "postgresql://"):
        assert unsafe not in rendered


def test_a_request_key_conflict_records_a_policy_compliant_refusal():
    """The new idempotency-conflict event, covered by the same policy."""
    bench = harness.build()
    apply_adversarial(bench, request_key="req-1")

    other = bench.artifact(
        fx.bundle(actors=(adversarial_actor(fx.SECOND_ACTOR_ID),))
    )
    preview = bench.imports.preview(other, request_key="req-1")
    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(other, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "request_key_conflict"
    payload = payload_of(bench, IMPORT_REFUSED)
    assert set(payload) == POLICIES[IMPORT_REFUSED].required
    assert payload["refusal_code"] == "request_key_conflict"
    for marker in MARKERS.values():
        assert marker not in repr(payload)


def test_a_concurrency_refusal_records_a_policy_compliant_refusal():
    """The new concurrency-refusal event, covered by the same policy."""
    from application.errors import UniquenessConflict

    bench = harness.build()
    artifact = bench.artifact(adversarial_bundle())
    preview = bench.imports.preview(artifact, request_key="req-1")
    bench.factory.fail_on = "external_actor_mappings"
    bench.factory.failure = UniquenessConflict("external_actor_mapping.world_actor")

    with pytest.raises(ImportRefused) as refusal:
        bench.imports.apply(artifact, preview, discord_user_id=harness.COUNCIL_USER)

    assert refusal.value.code == "concurrent_import"
    payload = payload_of(bench, IMPORT_REFUSED)
    assert set(payload) == POLICIES[IMPORT_REFUSED].required
    assert payload["refusal_code"] == "concurrent_import"
    # The rule name is a vocabulary this codebase owns, and it is not recorded
    # here at all — the refusal code is the classification history keeps.
    assert "external_actor_mapping.world_actor" not in repr(payload)


def test_every_recorded_refusal_code_is_declared():
    bench = harness.build()

    refuse(bench, code_expected="stale_preview")

    for event in events(bench, IMPORT_REFUSED):
        assert event.payload["refusal_code"] in REFUSAL_CODES


# -- the bootstrap's two events ------------------------------------------------


def test_the_bootstrap_completion_payload_holds_exactly_its_policy():
    from application.authorization import SupervisedBootstrap
    from application.bootstrap import BootstrapGate

    bench = harness.build()
    artifact = bench.artifact(adversarial_bundle())
    gate = BootstrapGate(bench.factory, profile=PROFILE)
    service = type(bench.imports)(
        bench.factory,
        deployment=bench.imports._deployment,
        profile=PROFILE,
        bootstrap_gate=gate,
    )
    preview = service.preview(artifact, request_key="req-1")

    service.apply(
        artifact, preview, bootstrap=SupervisedBootstrap("Peter Duscha")
    )

    payload = payload_of(bench, BOOTSTRAP_COMPLETED)
    assert set(payload) == POLICIES[BOOTSTRAP_COMPLETED].required
    assert payload["supervisor"] == "Peter Duscha"
    for marker in MARKERS.values():
        assert marker not in repr(payload)


def test_the_bootstrap_refusal_payload_carries_no_free_text_reason():
    """The removed prose channel, asserted as removed."""
    import inspect

    from application.bootstrap import BootstrapGate

    signature = inspect.signature(BootstrapGate.record_refusal)

    assert "reason" not in signature.parameters
    assert "reason" not in POLICIES[BOOTSTRAP_REFUSED].allowed


def test_the_policy_module_documents_every_key_it_allows():
    """Each allowed key appears in the written data classification.

    The finding asked for these to be reviewed as data classes rather than
    grandfathered. This is the mechanical half of that: a key added to a policy
    without a sentence saying what class of data it is fails here.
    """
    documentation = audit_policy.__doc__ or ""

    for policy in POLICIES.values():
        for key in policy.allowed:
            assert f"`{key}`" in documentation, (
                f"{key!r} is allowed by {policy.action} but the policy module "
                "does not say what class of data it is"
            )
