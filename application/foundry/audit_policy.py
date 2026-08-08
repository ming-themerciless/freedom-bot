"""What each audited import action may record, as policy rather than as a test.

An audit row is append-only in the application, in the ORM and in PostgreSQL: a
trigger refuses `UPDATE` and `DELETE` even for the schema owner. Whatever gets
into one is there permanently. So "what may go in" has to be a rule the code
enforces, not a list a test happens to agree with.

Independent review found (I-2) that the previous arrangement was the weaker
thing: a single test covering a single action, accepting *any subset* of an
allowlist — so an empty payload passed — and saying nothing at all about
refusals or about character creation, which was carrying an Actor-derived
`display_name` nobody had ruled on. This module replaces it with:

- a policy per action, with **required** and **optional** keys, so both an
  unapproved key and a missing one are failures;
- `enforced()`, called at every `audit.record` site in the import path, so the
  policy is applied when the row is written rather than checked afterwards; and
- a written data classification for every field, below, so a later reader can
  see what was decided rather than infer it from a set literal.

## The data classification

Every key falls into one of four classes. Nothing is grandfathered: the class is
the argument for the key being here at all.

**Platform-generated identifiers and counts.** `snapshot_checksum`,
`profile_version`, `preview_token`, `operation_digest`, `characters_created`,
`actors`, `mapped`, `unmapped`, `blocked`, `absent`, `errors`, `warnings`,
`stale_platform_display_names`, `canonical_encoding`, `applied`, `mode`. Derived
by this platform from its own computation. No Actor content survives a count.

**Closed vocabularies owned by this codebase.** `issue_codes` (validated by
`ReconciliationIssue`), `refusal_code` (validated against
`import_service.REFUSAL_CODES`), `fields_differing` and the keys of
`legacy_authority_deferred` (profile field keys), and its values (migration
package names). A test asserts each is drawn from its declared vocabulary, so
none of them is a free-text channel wearing a vocabulary's name.

**Foundry deployment structure.** `folder_id`, `folder_path`, `exporter`,
`external_actor_id`. Artifact-derived, and deliberately kept: `folder_path` is
what a Council member actually confirmed in the preview, and an audit row that
could not say which folder was imported would not be evidence of anything.
These describe the *world's organisation*, not a character's state — no score,
balance, item, level, class or name is among them.

**Minimized stand-ins for caller-supplied text.** `request_key_digest`. The
request key itself is caller-supplied text of up to 255 printable characters,
and the security review found (S-1) that copying it verbatim into an audit
payload made permanent, searchable history an arbitrary channel: length and
character validation stop a row being corrupted, not a caller putting a player
name, an email address or a credential in one. The verbatim key survives in
exactly one place, `snapshot_imports.request_key`, because that column *is* the
idempotency lookup and an exact match is what it does. Everywhere permanent
carries `request_key_digest` instead — a domain-separated, version-stable
SHA-256 (`import_service.request_key_digest`). It is deterministic, so every
event of one attempt still groups together; it is one-way, so the row no longer
holds the text; and its name cannot be mistaken for the key's. It is not a
secret and is never authorization.

**Operator identity.** `supervisor` is the named human who supervised the
one-time bootstrap: attribution is the entire point of recording the bootstrap
at all.

## The submission actions

`snapshot_submission.accepted` and `snapshot_submission.refused` record that an
artifact *arrived*, not that anything was applied. Their keys fall into the same
four classes, and the ones that are new here are classified below.

**Platform-generated identifiers and counts.** `size_bytes` and `actor_count`
are counts this platform derived from its own parse of the bundle — never from
what the client claimed. `duplicate` and `recorded` are booleans about the
attempt: `duplicate` says these exact bytes or this exact key had already been
submitted, and `recorded` is always `False` on a refusal, stated rather than
implied so a refused row cannot be read as an outcome nobody recorded.

`recorded` replaced a key named `stored`, under implementation review finding
I-1. The artifact is written before the transaction commits, deliberately, so a
refusal raised because directory durability could not be acknowledged can leave
a correct content-addressed file behind. `stored: false` asserted that it had
not. What a refusal actually establishes is that nothing was *recorded*, and the
key now says that and no more. No row carried the old key: the action is new in
this package and has never been committed to a real database.

**Foundry deployment structure.** `world_id` and `selected_folder_ids` say which
world and which folders the artifact carries. Like `folder_path`, they describe
the world's organisation — no score, balance, item, level, class or name is
among them — and an audit row that could not say which world a snapshot came
from would not be evidence of anything.

**Closed vocabularies owned by this codebase.** `received_via` is
`application.snapshots.SnapshotSource`: `operator` or `foundry_module`, the two
chains of custody an artifact can have. `artifact_code` is drawn from
`submission.ARTIFACT_REFUSAL_CODES`, which a test asserts is exactly the set of
codes `artifact.py` and `parser.py` can raise, so a new parser refusal cannot
reach append-only history unclassified.

**Operator-chosen identity.** `service_principal_id` is the configured token
naming which credential presented the artifact. It is validated by
`ServicePrincipal` to a short id-shaped string, it is chosen by an operator
rather than supplied per request, and it is *not* the credential — the secret
never leaves configuration and never reaches a row. It is required because a
module submission has no acting Discord user: without it the row would name
nobody at all.

**What is deliberately absent.** There is no reconciliation summary on either
action, because a submission reconciled nothing; those counts belong to the
import a Council member later confirms. There is no request key, no artifact
byte, no filename and no endpoint.

## Traceability, and why the digest is not a duplicated identifier

Three identifiers do three different jobs, and dropping any of them would lose
an answer:

- `correlation_id` (a column on the event, not a payload key) ties one *attempt*
  together — its import row, its character-created events, its refusal. It is
  new for every attempt, so it cannot group a retry with the original.
- `operation_digest` says *what was applied* — the bound inputs of the operation.
  It contains no request key at all, by design, so it cannot group by attempt
  identity either.
- `request_key_digest` is the only one that is a stable function of the request
  key. It is what lets an operator holding the key an interaction actually sent
  find every event recorded under it, across the original and its retries,
  without permanent history holding the key.

`preview_token` is not a fourth: it is a digest over the binding *including* the
volatile aggregate versions, so two attempts under the same key legitimately
differ in it.

## What was removed

`snapshot_import.character.created` carried `display_name`, taken from the
Foundry Actor. It is **not** necessary identity evidence and has been removed.
The character's identity is `entity_id` — the platform's own stable UUID — and
its provenance is `external_actor_id` + `folder_id` + `snapshot_checksum`, all
of which are already here. The display name is Actor-derived game-visible data;
it is stored mutably on `characters.display_name`, where it can be read at any
time; and finding B-2 establishes that it is precisely the field that goes stale
when a player renames in Foundry. An immutable audit row asserting a mutable
value, as identity evidence it is not, was the weakest possible reason to keep
it.

`bootstrap.refused` carried a free-text `reason`. A written prose field is an
unbounded channel into append-only history, and `refusal_code` already carries
the classification an operator filters on. It has been removed rather than
grandfathered; the method has no caller, so nothing depended on it.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


class AuditPolicyError(ValueError):
    """A payload did not match its action's policy. The row is not written."""


@dataclass(frozen=True, slots=True)
class AuditPayloadPolicy:
    """What one action's payload must contain, and what it may contain."""

    action: str
    required: frozenset[str]
    optional: frozenset[str] = frozenset()

    @property
    def allowed(self) -> frozenset[str]:
        return self.required | self.optional


#: Keys every reconciliation summary contributes. They travel together because
#: they are produced together by `ReconciliationReport.summary()`; splitting them
#: here would let one drop out unnoticed.
_SUMMARY_KEYS = frozenset(
    {
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
        "fields_differing",
        "stale_platform_display_names",
        "legacy_authority_deferred",
    }
)

IMPORT_APPLIED = "snapshot_import.applied"
IMPORT_REFUSED = "snapshot_import.refused"
CHARACTER_CREATED = "snapshot_import.character.created"
BOOTSTRAP_COMPLETED = "bootstrap.completed"
BOOTSTRAP_REFUSED = "bootstrap.refused"
SUBMISSION_ACCEPTED = "snapshot_submission.accepted"
SUBMISSION_REFUSED = "snapshot_submission.refused"

POLICIES: Mapping[str, AuditPayloadPolicy] = MappingProxyType(
    {
        policy.action: policy
        for policy in (
            AuditPayloadPolicy(
                action=IMPORT_APPLIED,
                required=_SUMMARY_KEYS
                | {
                    "mode",
                    # The digest of the request key, never the key (S-1). The
                    # old `request_key` is not optional and not deprecated: it
                    # is undeclared, so `enforced()` refuses a payload carrying
                    # it and the raw key cannot reach an audit row by mistake.
                    "request_key_digest",
                    "operation_digest",
                    "preview_token",
                    "characters_created",
                },
                # Only for a supervised bootstrap; a Council import has no
                # supervisor, and `None` is written rather than the key omitted.
                optional=frozenset({"supervisor"}),
            ),
            AuditPayloadPolicy(
                action=IMPORT_REFUSED,
                # Deliberately *not* the whole summary: a refusal applied
                # nothing, so counts of what it would have done are not
                # evidence. A code, a scope and the issue vocabulary are.
                required=frozenset(
                    {
                        "refusal_code",
                        "folder_id",
                        "profile_version",
                        "errors",
                        "warnings",
                        "issue_codes",
                        "applied",
                    }
                ),
            ),
            AuditPayloadPolicy(
                action=CHARACTER_CREATED,
                required=frozenset(
                    {
                        "snapshot_checksum",
                        "profile_version",
                        "external_actor_id",
                        "folder_id",
                    }
                ),
            ),
            AuditPayloadPolicy(
                action=BOOTSTRAP_COMPLETED,
                required=frozenset(
                    {"supervisor", "profile_version", "snapshot_checksum"}
                ),
            ),
            AuditPayloadPolicy(
                action=BOOTSTRAP_REFUSED,
                required=frozenset({"supervisor", "refusal_code", "applied"}),
            ),
            AuditPayloadPolicy(
                action=SUBMISSION_ACCEPTED,
                # A submission records that an artifact *exists*. It applied
                # nothing, so there is no reconciliation summary here and no
                # count of what an import would do — those belong to the import
                # that a Council member later confirms.
                required=frozenset(
                    {
                        "snapshot_checksum",
                        "size_bytes",
                        "actor_count",
                        "world_id",
                        "exporter",
                        "selected_folder_ids",
                        "canonical_encoding",
                        # The configured principal token, a closed vocabulary
                        # the operator chose. Not a credential, and validated by
                        # `ServicePrincipal` to a short id-shaped string.
                        "service_principal_id",
                        "request_key_digest",
                        "received_via",
                        "duplicate",
                    }
                ),
            ),
            AuditPayloadPolicy(
                action=SUBMISSION_REFUSED,
                required=frozenset(
                    {
                        "refusal_code",
                        "service_principal_id",
                        "request_key_digest",
                        # Always `False`. Stated rather than implied, so a row
                        # cannot be read as a submission whose outcome is
                        # unclear. It claims only that nothing was *recorded* —
                        # see the classification above for why the old `stored`
                        # claimed more than a refusal can establish.
                        "recorded",
                    }
                ),
                # `artifact_code` is absent unless the bundle itself was
                # refused; `snapshot_checksum` is absent when the bytes were
                # refused before they could be hashed — an over-sized artifact
                # is never held in memory long enough to have an identity.
                optional=frozenset({"artifact_code", "snapshot_checksum"}),
            ),
        )
    }
)


def enforced(action: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return `payload` if its action's policy permits it, or refuse to write it.

    Called at the point of recording, so the policy is what actually decides
    what reaches an append-only table. An action with no policy is refused
    outright: a new audited action must be classified before it can write
    anything, which is the moment somebody notices they are about to put an
    Actor's data into permanent history.

    Both directions are checked. An unapproved key is the obvious failure; a
    *missing required* key is the one the previous test could not see, because
    accepting any subset of an allowlist accepts an empty payload.
    """
    policy = POLICIES.get(action)
    if policy is None:
        raise AuditPolicyError(
            f"{action!r} has no audit payload policy. Declare one in "
            "application/foundry/audit_policy.py — including which class of "
            "data each key is — before this action writes to append-only "
            "history."
        )
    keys = set(payload)
    unapproved = sorted(keys - policy.allowed)
    missing = sorted(policy.required - keys)
    if unapproved or missing:
        raise AuditPolicyError(
            f"The {action!r} audit payload does not match its policy: "
            + (f"unapproved key(s) {unapproved}. " if unapproved else "")
            + (f"missing required key(s) {missing}. " if missing else "")
            + "Nothing was recorded."
        )
    return dict(payload)
