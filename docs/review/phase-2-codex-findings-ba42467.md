# Phase 2 remediation — findings to fix and return for independent re-review

You are Claude, the working Technical Lead and implementer for the Phase 2
remediation. Codex completed the mandatory independent implementation review and
separate security-focused pass of commit `ba42467`. The recommendation was
**remediate before the supervised real-export rehearsal**.

Implement every finding below, add proportionate tests, run the complete evidence
suite against disposable `freedom_test`, and prepare a remediation submission for
Codex to re-review. Do not perform the supervised real-export rehearsal and do not
read either of these prohibited sources:

- `/opt/discord-bots/foundry-actor-exports`
- `/home/foundry/shared/worlds/the-guild/data/actors`

Do not push. Preserve unrelated user changes. Destructive database work is allowed
only against `freedom_test`, after positively confirming the target and that it can
be recreated or restored. Follow `.agents/AGENTS.md`, the controlled
`docs/implementation-plan.md`, and the accepted
`docs/review/phase-2-v1.5-remediation-plan.md`. Do not reopen rejected ADR 0008 or
add any snapshot-to-game-state write path.

## Required remediation

### B-1 — Bind idempotency keys to the original operation (Blocking)

At `application/foundry/import_service.py` around the existing
`find_by_request_key` early return, a reused request key currently returns the old
record solely by key. A different artifact, folder, profile, exporter, or other
bound input can therefore be presented under the old key and receive a
contradictory duplicate receipt: the old import identity/correlation ID together
with the new checksum and caller-supplied report.

Make request-key idempotency mean **same key and same bound operation**. A retry of
the identical operation must return the original result without a second durable
effect. Reuse of the key for different input must fail closed with a typed, safe
conflict/refusal and must not return a mixed receipt. Persist whatever immutable
binding identity is needed; if this changes migration `0002`, apply the same
replacement-in-place reasoning only if it remains factually valid and document the
change. Do not weaken the separate applied-input uniqueness rule.

Tests must cover at least:

- same key + same exact input returns the original result;
- same key + different artifact checksum is refused;
- same key + different selected folder is refused;
- same key + changed profile/binding input is refused;
- returned checksum, report, import ID, and correlation ID all describe one
  operation and can never be mixed;
- sequential and concurrent key collisions leave exactly one durable effect and
  no misleading success audit.

### B-2 — Correct display-name reconciliation direction (Blocking)

`domain/foundry_profile.py` correctly says that a later Actor rename means the
platform display record is stale. However, `application/foundry/reconciliation.py`
currently routes every comparable mismatch through `foundry_out_of_date`, says
PostgreSQL is authoritative, and instructs the operator to update Foundry.

Make `character.display_name` produce truthful, field-specific directionality. It
must preserve stable Actor/character identity, change nothing automatically, and
must never tell an operator to undo the Foundry rename. A distinct typed outcome or
issue code such as `platform_display_name_stale` is preferable to special prose
hidden behind the generic `foundry_out_of_date` result. Keep generic database-owned
field semantics correct for fields introduced by later typed packages.

Update the safe summary vocabulary and documentation consistently. Tests must
prove that a stable-ID rename:

- remains mapped to the same character;
- reports the platform display record as stale;
- does not report Foundry as stale or advise changing Foundry;
- performs no display-name update in Phase 2;
- produces an accurate, value-minimized summary/audit representation.

### I-1 — Translate concurrency and constraint losers safely (Important,
security-relevant)

Concurrent applies can lose on snapshot, character, mapping, import, or commit
uniqueness and escape as raw SQLAlchemy/driver exceptions. The current PostgreSQL
test accepts any exception. Translate expected database races into a typed
duplicate or typed safe refusal, as appropriate after re-reading the winning row.
Do not expose SQL, parameters, Actor values, connection strings, tracebacks, or
driver internals. Unexpected database failures must still roll back and surface
through a controlled application error boundary rather than being mislabeled as a
successful duplicate.

Strengthen PostgreSQL tests so they reject arbitrary exceptions. Cover same-input
and overlapping-input races, assert one durable effect, assert the losing result is
typed and internally consistent, and assert any refusal/audit payload is safe. The
implementation must continue to satisfy zero partial commits and one audit effect.

### I-2 — Make audit content allowlists actual policy (Important,
security-relevant)

The existing allowlist test covers only `snapshot_import.applied`, accepts any
subset (including an empty payload), and omits refusal and
`snapshot_import.character.created`. The latter currently carries an Actor-derived
`display_name` outside the tested policy.

Define explicit per-action audit payload policies for:

- applied import;
- refused/attempted import;
- character identity creation;
- any new idempotency-conflict or concurrency-refusal event.

Tests must assert both the required keys and the absence of unapproved keys for
every action. They must use adversarial synthetic values and prove that game-state
values, raw artifact content, SQL/tracebacks, connection strings, and unnecessary
Actor data do not enter append-only records. Decide explicitly whether the created
character's display name is necessary identity evidence. If retained, document and
test that narrow policy; if unnecessary, remove it. Review `supervisor`, request
keys, folder paths, exporter descriptions, issue codes, and preview tokens as data
classes rather than automatically grandfathering current behavior.

### O-1 — Normalize or verify `PUBLIC` privileges (Optional hardening, but fix it)

`infra/postgresql/runtime-grants.sql.tmpl` says its `REVOKE` handles rights held by
`PUBLIC`, but it revokes only from `__APP_ROLE__`. Correct the claim and the
deployment behavior. Prefer explicitly revoking prohibited table privileges from
`PUBLIC` for every retained table, while preserving only the runtime role's intended
operations. If project policy requires a different mechanism, prove through live
effective-privilege tests that `PUBLIC` ACL drift cannot make the runtime role able
to update, delete, or truncate protected history or delete
`platform_initialization`.

The live grants suite must seed or simulate hostile `PUBLIC` grants, apply the
template, then prove the final effective privileges—not merely parse SQL text.

### I-3 — Validate comparable-field readers before reconciliation (Important)

`application/foundry/reconciliation.py::_DATABASE_VALUES` currently raises
`LookupError` only when reconciliation encounters a database-authority field with
no reader. Make this a construction/startup invariant of the reconciliation/import
composition so an accepted service cannot begin work with an unreadable comparable
field. Keep the domain `FieldProfile` independent of persistence-specific
`Character` readers. Add a test that constructing the service/comparator with a
database-authority field but no registered reader fails immediately with a clear,
safe configuration error.

### I-4 — Strengthen negative guards without treating them as security boundaries

Review `tests/test_rejected_scope_absent.py` and related guards. The current
AST-unparse table scan can be evaded by string concatenation. Retain scoped checks
that do not flag explanatory prose, but ensure the decisive evidence remains actual
ORM metadata, migrated PostgreSQL schema inventory, public API/import graph, and
behavioral tests proving no snapshot value can reach a character game-state field.
Do not add broad raw-text scans that fail on documentation. Document what each guard
does and does not prove.

## Decisions already accepted by the independent review

Do not churn these areas unless required by the fixes above:

- The profile may contain only fields fed by supported snapshot paths. Fields with
  no Foundry representation remain governed by the migration register.
- Deferred fields should carry presence, owning package, and safe unavailability
  reason—not the Foundry value.
- Recomputed `report.blocked` is a valid way to catch a new unmapped display-name
  collision between preview and apply.
- Parser/deployment/limit changes should refuse rather than apply under stale
  assumptions.
- Replacing uncommitted migration `0002` in place remains acceptable only while it
  is true that the former revision existed solely in disposable `freedom_test`.
- Current-role authorization is correctly re-resolved at apply; Platform
  Administrator alone must continue to confer no Council authority.
- Exact inherited bounds remain 64 MiB, depth 64, at most 500 Actors, at most 64
  folders, 1–8 selected folders, and at most 4000 items per Actor.

## Verification and evidence required

Run and report exact results for:

1. the full pytest suite with `TEST_DATABASE_URL` targeting only
   `postgresql+psycopg:///freedom_test`, with no skips attributable to this scope;
2. focused new tests for every finding above;
3. live restricted-role operations, including hostile `PUBLIC`-grant cleanup;
4. two-connection concurrency tests whose loser is typed and safe;
5. `alembic upgrade head`, downgrade/upgrade, and `alembic check` if the migration
   changes;
6. the existing injected-failure atomicity suite;
7. a repository/diff scan confirming no real Actor payload or prohibited source was
   accessed or added.

Do not claim the Phase 2 gate, the supervised rehearsal, Data Owner attestation, or
the unset §9.4 operational windows.

## Deliverable

Create a new remediation submission under `docs/review/` that includes:

- a finding-by-finding disposition for B-1, B-2, I-1 through I-4, and O-1;
- precise code/test/document traceability;
- migration and runtime-grant implications;
- exact commands and results;
- remaining risks and unmet gate criteria;
- an explicit request for Codex independent re-review and separate security
  re-review.

Then hand the work back without approving it yourself.
