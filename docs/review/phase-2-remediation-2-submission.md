# Phase 2 remediation 2 — findings B-1, B-2, I-1…I-4, O-1

Status: **In progress. Phase 2 is NOT closed and this document does not claim
its gate.** Prepared by the implementing agent (Claude) as working Technical
Lead. Independent re-review by Codex is required by plan §16.4
(*import/reconciliation*), with a **separate** security-focused pass; the
Acceptance Authority records the gate decision.

Date: 2026-08-03

Answers: the independent implementation review and separate security pass of
commit `ba42467`, whose findings are recorded in
[`Handover information`](Handover%20information).

Supersedes for the milestone conclusion:
[`phase-2-remediation-submission.md`](phase-2-remediation-submission.md), which
remains the evidence record for `ba42467` as reviewed.

Starting point: `HEAD` is `c8a3da9`. **Nothing has been committed or pushed.**

The supervised real-export rehearsal was **not** performed. Neither prohibited
source was read (§8.7).

---

## 1. Disposition, finding by finding

| Finding | Disposition | Where |
|---|---|---|
| **B-1** — bind idempotency keys to the original operation | **Fixed.** Request-key idempotency now means *same key and same bound operation*. A new immutable `snapshot_imports.operation_digest` records what the key was spent on; reuse for anything else is a typed `request_key_conflict` refusal and returns no receipt | §2 |
| **B-2** — display-name reconciliation direction | **Fixed.** A rename in Foundry now reports the **platform** display record as stale, under its own issue code, and never advises changing Foundry | §3 |
| **I-1** — translate concurrency and constraint losers safely | **Fixed.** The adapter translates every uniqueness violation into `UniquenessConflict` naming a rule and everything else into `PersistenceError`; no SQL, parameters, values, connection strings, tracebacks or driver internals cross the boundary. A loser is resolved by re-reading the winning row, or refused | §4 |
| **I-2** — audit content allowlists as actual policy | **Fixed.** Per-action policies with required *and* optional keys, enforced at the point of writing. `display_name` removed from character creation; `reason` removed from the bootstrap refusal | §5 |
| **I-3** — validate comparable-field readers before reconciliation | **Fixed.** A construction-time invariant with a typed, safe configuration error | §6.1 |
| **I-4** — strengthen negative guards without treating them as boundaries | **Fixed.** Concatenation folded, decisive evidence added (migrated schema inventory, import graph, behavioural no-write-path), and every guard documents what it does and does not prove | §6.2 |
| **O-1** — normalize or verify `PUBLIC` privileges | **Fixed.** The false claim is corrected and the template now revokes all privileges from `PUBLIC` on every retained table. The live suite seeds hostile `PUBLIC` grants, applies the template, and asserts effective privileges | §6.3 |

Nothing in §"Decisions already accepted by the independent review" was reopened.
ADR 0008 remains rejected and no snapshot-to-game-state write path was added —
now proven behaviourally as well as structurally (§6.2).

---

## 2. B-1 — a request key is bound to the operation it was spent on

### The defect

`_apply_within_transaction` returned the stored record on the request key alone.
Presenting a different artifact, folder, profile or exporter under a spent key
therefore produced an `ImportOutcome` carrying the **first** import's
`import_id` and `correlation_id` beside the **second** artifact's checksum and
the caller's own report — one receipt describing no single operation.

### The fix

`OPERATION_FIELDS` names the bound inputs that identify an operation:
`snapshot_checksum`, `world_id`, `folder_id`, `folder_path`, `profile_version`,
`exporter`. `operation_digest()` is the single place their SHA-256 is computed,
used both by `PreviewBinding.operation_digest()` and by the apply's own
recomputation from the artifact in hand.

Two `PreviewBinding` fields are deliberately excluded, and both exclusions are
load-bearing:

- **`aggregate_versions`** is volatile by design. A genuine retry runs against a
  database the first attempt already changed, so including it would make every
  retry look like a reuse — failing closed on the one case idempotency exists
  for.
- **`request_key`** is the lookup, not the operation. Digesting the key with the
  operation would make every stored digest trivially match its own key.

`test_the_operation_fields_classify_every_bound_input` asserts the classification
against the dataclass's own fields, so a new bound input must be classified as
one or the other rather than silently omitted.

On lookup, `_require_same_operation` compares the stored digest with the one
computed from the artifact being presented. Equal is a retry; unequal raises
`request_key_conflict`, naming *which* bound inputs differ and quoting none of
their values. A matched retry's report is **recomputed** rather than taken from
the caller's preview, so no field of the returned receipt is caller-supplied.

Authorization is deliberately **not** part of the digest, and this is a decision
rather than an omission: `_resolve_authority` runs before the idempotency check
on every apply, so an unauthorized caller cannot retrieve a receipt at all, and
a second Council member retrying the same operation should receive the original
result rather than a conflict.

`request_key` is also now validated as input — bounded at 255 characters,
printable, non-blank — at `preview` and again at `apply`, with
`SnapshotImportRecord` refusing an unwritable key as a last line of defence. It
is written verbatim into append-only history, so it is validated rather than
trusted as an opaque handle.

### Tests

| Requirement from the finding | Test |
|---|---|
| same key + same exact input returns the original result | `test_snapshot_import_service.py::test_the_same_key_and_the_same_input_returns_the_original_result`; `test_snapshot_database.py::test_a_retry_of_the_same_operation_returns_the_original_record` |
| same key + different artifact checksum is refused | `test_snapshot_import_service.py::test_the_same_key_with_a_different_artifact_is_refused`; `test_snapshot_database.py::test_a_reused_key_with_a_different_artifact_is_refused_by_postgresql` |
| same key + different selected folder is refused | `test_snapshot_import_service.py::test_the_same_key_with_a_different_folder_is_refused` |
| same key + changed profile/binding input is refused | `test_snapshot_import_service.py::test_the_same_key_with_a_changed_profile_version_is_refused` |
| checksum, report, import ID and correlation ID describe one operation | `test_snapshot_import_service.py::test_a_retry_receipt_describes_one_operation_and_mixes_nothing`; `test_snapshot_import_service.py::test_a_conflicting_key_returns_no_receipt_for_the_earlier_import` |
| sequential key collision leaves one durable effect and no misleading success audit | `test_snapshot_import_service.py::test_a_conflicting_key_writes_a_refusal_and_no_success_audit` |
| concurrent key collision leaves one durable effect | `test_snapshot_database.py::test_two_concurrent_applies_of_the_same_key_produce_one_effect` |
| the conflict check also applies on the concurrent path | `test_snapshot_import_service.py::test_a_conflicting_key_claimed_concurrently_is_refused_not_duplicated`; `test_snapshot_database.py::test_a_reused_key_claimed_by_a_different_operation_is_refused_on_the_conflict_path` |
| the digest is the same computed either way | `test_snapshot_import_service.py::test_the_binding_and_the_apply_compute_the_same_operation_digest`; `test_snapshot_database.py::test_the_stored_operation_digest_is_the_binding_of_the_applied_operation` |
| the binding is a schema rule, not only an application one | `test_snapshot_database.py::test_the_database_refuses_an_import_row_without_an_operation_digest` |
| a request key is a bounded printable token | `test_snapshot_import_service.py::test_a_hostile_request_key_is_refused_where_it_arrives`; `test_snapshot_import_service.py::test_the_record_itself_refuses_an_unwritable_request_key`; `test_snapshot_import_service.py::test_the_record_itself_refuses_an_absent_operation_digest`; `test_snapshot_import_service.py::test_an_over_long_request_key_still_produces_a_recordable_refusal` |
| a refused attempt records what it attempted and does not answer a retry | `test_snapshot_import_service.py::test_a_refused_attempt_records_the_operation_it_attempted` |
| the refusal vocabulary is closed | `test_snapshot_import_service.py::test_every_refusal_code_is_declared` |

The applied-input uniqueness rule was not weakened: the partial unique index on
`(snapshot_id, folder_id, profile_version) WHERE status = 'applied'` is
unchanged, and `test_the_same_input_cannot_be_applied_twice` and
`test_a_refused_attempt_does_not_claim_the_input_identity` still pass.

---

## 3. B-2 — a rename in Foundry makes the *platform* record stale

### The defect

`domain/foundry_profile.py` had always said that players rename in Foundry, so a
difference means the platform's display record is stale. The reconciliation said
the opposite: every comparable difference became `foundry_out_of_date`, asserted
"the database … is authoritative", and instructed the operator to "update the
Foundry Actor manually" — an instruction to undo a rename a player deliberately
made.

### The fix

Direction is now a property of the **field**, declared in the domain profile and
read by the reconciliation.

`DifferenceDirection` has two members, and each member's value *is* the issue
code raised for it, so the declaration and the vocabulary an operator reads
cannot drift. `ProfileField.difference_direction` has **no default**: a field
with database authority that does not state its direction fails to construct.
That is the part that keeps "generic database-owned field semantics correct for
fields introduced by later typed packages" — a future comparable field cannot
inherit "Foundry is out of date" from the field that happened to be written
first.

`character.display_name` declares `PLATFORM_DISPLAY_NAME_STALE`. Its issue says
the platform record is the stale one, says *do not* change the Foundry Actor,
and says the character stays mapped to the same Actor (OD-42). No display-name
update is performed; Phase 2 still writes no character field.

Vocabulary and documentation:

- `report.summary()["fields_out_of_date"]` → **`fields_differing`**. The old key
  asserted a direction the summary had not established; the new one states what
  it knows (which field keys disagreed) and leaves direction to `issue_codes`.
- a new `stale_platform_display_names` **count** — scale without names.
- `docs/operations/foundry-snapshot-import.md` documents
  `platform_display_name_stale` and corrects the `foundry_out_of_date` entry,
  noting that no field carries that direction in Phase 2.

### Tests

| Requirement from the finding | Test |
|---|---|
| remains mapped to the same character | `test_snapshot_reconciliation.py::test_a_foundry_rename_leaves_the_character_mapped_and_unmodified` |
| reports the platform display record as stale | `test_snapshot_reconciliation.py::test_a_foundry_rename_reports_the_platform_display_record_as_stale` |
| does not report Foundry as stale | `test_snapshot_reconciliation.py::test_a_foundry_rename_never_reports_foundry_as_out_of_date` |
| does not advise changing Foundry | `test_snapshot_reconciliation.py::test_a_foundry_rename_never_advises_changing_foundry` |
| performs no display-name update | `test_snapshot_reconciliation.py::test_a_foundry_rename_leaves_the_character_mapped_and_unmodified`; `test_rejected_scope_absent.py::test_a_renamed_actor_does_not_update_the_display_name_either` |
| accurate, value-minimized summary | `test_snapshot_reconciliation.py::test_a_rename_summary_names_the_direction_but_neither_name`; `test_snapshot_reconciliation.py::test_a_matching_name_counts_no_stale_platform_display_record` |
| direction is declared on the field | `test_snapshot_reconciliation.py::test_the_profile_declares_the_direction_rather_than_the_reconciliation`; `test_field_profile.py::test_a_field_with_database_authority_must_declare_its_difference_direction`; `test_field_profile.py::test_a_deferred_field_may_not_declare_a_difference_direction` |
| against PostgreSQL, including the stored summary | `test_snapshot_database.py::test_a_tampered_artifact_is_a_different_snapshot_in_the_database` |

---

## 4. I-1 — concurrency and constraint losers are typed and safe

### The defect

Concurrent applies could lose on snapshot, character, mapping, import or commit
uniqueness and escape as raw SQLAlchemy exceptions, whose string form carries the
failing statement, its bound parameters and PostgreSQL's own `DETAIL:` line —
which quotes the conflicting values. The PostgreSQL test accepted **any**
exception, so this would have passed it unchanged.

### The fix

`adapters/database/translation.py` wraps the session the unit of work hands to
every repository. Wrapping the session rather than each repository method is
deliberate: a repository that forgot to wrap one `execute` would leak, and
nothing could see the omission.

- A violation whose SQLSTATE is `23505`/`23P01` becomes
  `UniquenessConflict(rule)`, where `rule` is a stable application name
  (`snapshot_import.request_key`) mapped from the constraint name read out of
  psycopg's structured diagnostics — never parsed from the message, which is
  localisable and carries the offending values.
- **Every other** `IntegrityError` becomes `PersistenceError`. This matters:
  `IntegrityError` is wider than "somebody else won", and filing a foreign-key
  or check violation as a conflict would send a caller looking for a winning row
  that does not exist — the precise mislabelling the finding forbids.
- Any other `SQLAlchemyError` becomes `PersistenceError` carrying only the
  SQLSTATE.
- Every path rolls back **before** raising, and raises `from None`, because a
  chained `__cause__` puts the statement and its parameters back into any
  rendered traceback.

`SnapshotImportService._resolve_conflict` resolves a conflict in a *fresh*
transaction, in a deliberate order: this operation's request key (digest
checked, per B-1) → this operation's applied input → otherwise a typed
`concurrent_import` refusal. The third branch is the honest one: with no winning
row describing this operation, a duplicate receipt would name an import that
does not exist. `PersistenceError` is never resolved at all.

Zero partial commits and one audit effect are unaffected: the resolution happens
after the losing transaction has already rolled back, and it writes nothing but
the ordinary refusal record.

### Tests

The PostgreSQL tests no longer accept arbitrary exceptions.

| Requirement from the finding | Test |
|---|---|
| same-input race, one durable effect, typed loser | `test_snapshot_database.py::test_two_concurrent_applies_of_the_same_input_produce_one_effect` |
| same-key race | `test_snapshot_database.py::test_two_concurrent_applies_of_the_same_key_produce_one_effect` |
| the loser is typed — arbitrary exceptions rejected | `test_snapshot_database.py::test_a_concurrent_loser_never_escapes_as_a_driver_exception` |
| the losing result is internally consistent | `assert_typed_and_consistent`, used by all three |
| refusal/audit payload is safe | `test_snapshot_database.py::test_a_concurrent_refusal_records_a_safe_audit_payload` |
| the resolution's branches, deterministically | `test_snapshot_database.py::test_conflict_resolution_reads_the_winning_row_from_postgresql`; `test_snapshot_database.py::test_an_unresolvable_conflict_against_postgresql_is_a_typed_safe_refusal`; `test_snapshot_database.py::test_a_reused_key_claimed_by_a_different_operation_is_refused_on_the_conflict_path` |
| an unexpected failure is not a duplicate | `test_snapshot_database.py::test_a_foreign_key_violation_is_a_persistence_error_not_a_conflict`; `test_snapshot_import_service.py::test_a_persistence_failure_is_never_resolved_into_a_duplicate` |
| the classification is by SQLSTATE | `test_snapshot_database.py::test_a_unique_violation_carries_a_conflict_sqlstate`; `test_snapshot_database.py::test_a_check_violation_does_not_carry_a_conflict_sqlstate` |
| constraint violations reach callers typed | `test_snapshot_database.py::test_a_world_actor_pair_can_only_be_mapped_once`; `test_snapshot_database.py::test_a_character_has_one_mapping_per_world` |
| application-level branches | `test_snapshot_import_service.py::test_a_lost_request_key_race_returns_the_winner_as_a_typed_duplicate`; `test_snapshot_import_service.py::test_a_lost_input_race_under_a_different_key_is_also_a_typed_duplicate`; `test_snapshot_import_service.py::test_an_unresolvable_conflict_is_refused_rather_than_called_a_duplicate` |

`assert_safe` checks the message **and** the rendered traceback for SQL,
parameters, `DETAIL:`/`Key (` diagnostics, driver names, connection strings and
Actor values, and asserts the cause chain is severed.

The threaded races prove the constraints fire and the invariants hold; which
branch of the resolution a loser takes depends on scheduling. The three
deterministic tests drive each branch against PostgreSQL on every run, and the
fake-level tests reproduce the ordering of a real race — the winner commits at
the moment the loser's insert fails — without threads.

---

## 5. I-2 — audit payload policy

### The defect

One test, over one action, asserting `set(payload) <= allowed`. It accepted any
subset including an empty payload; it said nothing about refusals; and it said
nothing about `snapshot_import.character.created`, which was writing an
Actor-derived `display_name` no policy had considered.

### The fix

`application/foundry/audit_policy.py` declares a policy per action, with
**required** and **optional** keys, and `enforced()` is called at every
`audit.record` site in the import and bootstrap paths — so the policy decides
what reaches an append-only table rather than describing what did. An action
with no policy cannot write at all.

Policies: `snapshot_import.applied`, `snapshot_import.refused` (which covers the
new `request_key_conflict` and `concurrent_import` events),
`snapshot_import.character.created`, `bootstrap.completed`,
`bootstrap.refused`.

**Every field is classified in writing** in the module docstring, in four
classes — platform-generated identifiers and counts; closed vocabularies owned by
this codebase; Foundry deployment structure; caller-supplied and operator
identity — and a test fails if a policy allows a key the classification does not
mention. The specific fields the finding asked about:

- **`supervisor`** — kept. The named human who supervised the one-time
  bootstrap; attribution is the entire reason for recording the bootstrap.
- **`request_key`** — kept, and now validated as a bounded printable token
  before it can arrive. It is already stored verbatim in
  `snapshot_imports.request_key` because that column *is* the idempotency rule,
  so the event adds no exposure, and it is what lets an event be traced to an
  attempt.
- **`folder_path`** — kept. It is what a Council member actually confirmed; an
  audit row that could not say which folder was imported would not be evidence.
  World structure, not character state.
- **`exporter`** — kept. Deployment metadata.
- **`issue_codes`** — kept, and now a **closed vocabulary**:
  `ReconciliationIssue` refuses a code not in `ISSUE_CODES`, so it cannot be a
  free-text channel wearing a vocabulary's name. `refusal_code` likewise against
  `REFUSAL_CODES`.
- **`preview_token`** — kept. An opaque SHA-256 digest.

**Removed.** `display_name` on `snapshot_import.character.created`. It is not
necessary identity evidence: `entity_id` is the platform's own UUID and
`external_actor_id` + `folder_id` + `snapshot_checksum` are the provenance. The
display name is Actor-derived, mutable, already stored on `characters`, and —
per B-2 — is precisely the field that goes stale. An immutable row asserting a
mutable value as identity evidence it is not was the weakest possible reason to
keep it.

**Removed.** `reason` on `bootstrap.refused`, a free-prose channel into
append-only history. `refusal_code` carries the classification an operator
filters on. The method had no caller, so nothing depended on it.

### Tests

`tests/test_audit_payload_policy.py` (26 tests). Every action is asserted in
both directions — required keys present, unapproved keys absent — using an
**adversarial** Actor whose name, race, class, background, feat, language and
item are marker strings including SQL and a connection string, so "the value did
not leak" is an assertion rather than a property of a tame fixture.

Notable: `test_the_policy_is_enforced_when_the_row_is_written` breaks the
summary the applied payload is built from and requires the *apply* to fail, so
the policy is proven to be the write path's own rule; and
`test_no_audit_row_anywhere_carries_an_actor_value` states the property as a
total rather than one action at a time.

---

## 6. The remaining findings

### 6.1 I-3 — comparable-field readers are a construction invariant

`_DATABASE_VALUES` raised `LookupError` the first time a run reached a
database-authority field with no reader — after an operator had produced and
confirmed a preview. It is now `ComparableFieldReaders`, validated against the
profile in `SnapshotImportService.__init__` before anything else, raising a typed
`ReconciliationConfigurationError` that names the field keys and the profile
version and nothing about a database, an artifact or an Actor. `reconcile()`
takes the readers as a required argument, so the composition decision cannot
drift back inside the run.

The domain `FieldProfile` stays independent of the persistence-facing
`Character`: the readers live in the application layer, and
`test_the_domain_profile_holds_no_persistence_reader` asserts the domain module
does not mention `Character` at all.

Tests: `test_snapshot_import_service.py::test_readers_must_cover_every_comparable_field_in_the_profile`,
`test_snapshot_import_service.py::test_the_service_refuses_to_be_constructed_with_an_unreadable_field`,
`test_snapshot_import_service.py::test_the_accepted_profile_composes_a_complete_reader_set`,
`test_snapshot_import_service.py::test_the_domain_profile_holds_no_persistence_reader`.

### 6.2 I-4 — negative guards, and what each proves

`_code_of` now folds `+`-concatenated string constants, closing the evasion the
review named. The file's docstring states plainly that source scans are hygiene
and not a security boundary — they catch reintroduction by inattention, not by
`getattr`, a runtime-assembled name or a config file — and that no broad
raw-text scan was added, because the migration and `application/snapshots.py`
deliberately *explain* the rejection and a text scan would flag exactly that
documentation.

The decisive evidence is now asserted here too:

- migrated PostgreSQL schema inventory —
  `test_the_migrated_schema_contains_no_rejected_table`,
  `test_the_migrated_schema_is_exactly_the_retained_set`;
- the import graph, resolved by importing rather than reading —
  `test_the_public_import_graph_reaches_no_rejected_module`;
- **behavioural**, against PostgreSQL —
  `test_an_import_writes_no_character_game_state_field`,
  `test_a_second_import_of_a_changed_actor_still_writes_no_field`,
  `test_a_renamed_actor_does_not_update_the_display_name_either`. An Actor
  carrying every kind of value the profile classifies is imported, then
  re-imported with a changed race, class, level, abilities and currency, and the
  `characters` row is compared column by column before and after.

The scan's own strength and its limit are themselves tested:
`test_the_folding_scan_catches_a_concatenated_table_name` and
`test_the_folding_scan_does_not_claim_to_catch_a_runtime_name`.

### 6.3 O-1 — `PUBLIC` privileges

The template claimed its `REVOKE … FROM __APP_ROLE__` statements "handled rights
held by `PUBLIC`". They did not and could not: revoking from a role does not
touch a privilege the role holds *through* `PUBLIC`, of which every role in the
cluster is a member. One `GRANT ALL ON audit_events TO PUBLIC` would have given
the runtime role `UPDATE`, `DELETE` and `TRUNCATE` on append-only history with
nothing in the template to take it away.

The claim is corrected and the behaviour with it. `runtime-grants.sql.tmpl` now
issues `REVOKE ALL PRIVILEGES ON <every retained table> FROM PUBLIC` before the
intended grants, and `REVOKE CREATE ON SCHEMA public FROM PUBLIC`. On a clean
cluster this is a no-op — which is the point: it makes the ACL state a property
of applying the template rather than of nothing ever having gone wrong.

The live suite proves **effective privileges**, not SQL text:

- `test_hostile_public_grants_would_widen_the_role_if_nothing_revoked_them` —
  the premise, proven rather than assumed, so the rest is not vacuous;
- `test_the_template_removes_public_drift_from_append_only_tables` (parametrised
  over four tables × three privileges) — seed hostile grants, apply the
  template, assert `has_table_privilege` is false and `PUBLIC` holds nothing;
- `test_the_template_leaves_public_holding_nothing_on_any_retained_table`;
- `test_the_template_preserves_the_runtime_roles_intended_operations` — the
  normalisation must not take away what the role is meant to have;
- `test_public_drift_cannot_let_the_runtime_role_delete_the_initialization_row`
  — the specific escalation, re-opening the supervised bootstrap;
- `test_the_denials_still_hold_as_the_role_after_public_drift` — the same
  conclusion reached a second way, by executing the statements under `SET ROLE`.

`tests/test_runtime_grants.py` now says in its docstring that it reads text and
what that is and is not worth, and adds
`test_every_retained_table_has_its_public_privileges_revoked`,
`test_public_is_not_left_able_to_create_in_the_schema` and
`test_the_template_makes_no_grant_to_public`.

One implementation note found while writing this evidence: `SET ROLE` is
transactional, so the rollback each denial requires silently returns the session
to the owner. The role is now re-assumed and re-asserted before every statement;
without that the loop would have passed while proving nothing after its first
iteration.

---

## 7. Migration and runtime-grant implications

### 7.1 A new migration `0003`, and why `0002` was not replaced

`0003_import_operation_digest.py` adds `snapshot_imports.operation_digest`
(`VARCHAR(64) NOT NULL`) with a `~ '^[0-9a-f]{64}$'` check constraint.

The finding permitted replacing `0002` in place "only if [the same reasoning]
remains factually valid". **It does not.** `0002`'s own docstring rests on two
conditions — never committed, and never applied to a durable environment. The
second still holds; the first does not: `0002` was committed in `ba42467` and is
part of the history now under independent review. The accepted plan's wording
("replacing uncommitted migration `0002` in place remains acceptable only while
it is true that the former revision existed solely in disposable
`freedom_test`") was a statement about the *earlier* revision `0002` replaced,
not a standing licence.

So `0002` is left exactly as reviewed, and this is an ordinary additive,
reversible migration — which is also what `.agents/AGENTS.md` asks for.

The column is `NOT NULL` with no backfill. No durable environment has ever run
`0002`; the only database that has is the disposable `freedom_test`, which every
test run migrates from empty. If the `SET NOT NULL` ever met rows it would fail
loudly, which is the correct outcome: there is no truthful digest for a row
written before the binding existed, and a fabricated one in an append-only table
would assert that a past import was bound to inputs nobody verified.

**Rollback:** `alembic downgrade 0002` drops the constraint and the column. It is
exercised in §8.

### 7.2 Runtime grants

`infra/postgresql/runtime-grants.sql.tmpl` changed as described in §6.3. It is
applied after migrations, as before; it is idempotent over repeated application
(`test_the_template_is_idempotent_over_repeated_application`).

**Deployment note.** `REVOKE ALL PRIVILEGES … FROM PUBLIC` and `REVOKE CREATE ON
SCHEMA public FROM PUBLIC` affect *every* role that was relying on a `PUBLIC`
grant, not only the runtime role. No such consumer exists in this deployment —
the schema owner `foundry` and the runtime role are the only principals — but a
maintainer adding a reporting or backup role must grant it explicitly rather
than through `PUBLIC`. This is flagged rather than assumed harmless.

---

## 8. Commands run, and their exact results

All against the disposable `freedom_test` database over the Unix-domain socket.

### 8.1 Full suite

```
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q
```

**1523 passed, 1 warning in 8.10s.** No failures, no errors, no skips. The one warning is a pre-existing
`DeprecationWarning` from `discord.player` importing `audioop`; it is unrelated
to this scope.

No skips attributable to this scope. `freedom_runtime_test` exists, so the live
restricted-role tests ran rather than skipping.

### 8.2 Focused suites

| Suite | Result |
|---|---|
| `tests/test_audit_payload_policy.py` | 26 passed |
| `tests/test_snapshot_import_service.py` | 75 passed |
| `tests/test_snapshot_database.py` | 41 passed |
| `tests/test_snapshot_reconciliation.py` | 27 passed |
| `tests/test_field_profile.py` | 137 passed |
| `tests/test_rejected_scope_absent.py` | 29 passed |
| `tests/test_runtime_grants.py` | 8 passed |
| `tests/test_runtime_grants_live.py` | 44 passed |
| `tests/test_submission_traceability.py` | 54 passed |

### 8.3 Injected-failure atomicity

```
… -m pytest -q -k "injected or atomic or rolls_back or rollback"
12 passed, 1511 deselected
```

### 8.4 Migration

```
DATABASE_URL=postgresql+psycopg:///freedom_test APP_ENVIRONMENT=test \
  ./venv/bin/python -m alembic downgrade base   # 0003 → 0002 → 0001 → base
  ./venv/bin/python -m alembic upgrade head     # → 0001 → 0002 → 0003
  ./venv/bin/python -m alembic current          # 0003 (head)
  ./venv/bin/python -m alembic check            # No new upgrade operations detected.
```

`0003` alone, down and up:

```
alembic downgrade 0002   → column absent (information_schema count 0)
alembic upgrade head     → operation_digest | NO | character varying
alembic check            → No new upgrade operations detected.
```

### 8.5 Live restricted-role operations, including hostile `PUBLIC` cleanup

Covered by `tests/test_runtime_grants_live.py` (44 passed), which seeds
`GRANT ALL PRIVILEGES ON <table> TO PUBLIC` for all twelve retained tables,
applies the rendered template, and then asserts effective privileges both through
`has_table_privilege` and by executing the statements under `SET ROLE`.

### 8.6 Two-connection concurrency

Covered by the four threaded tests in §4 plus the three deterministic
resolution tests. Every loser is `ImportRefused` or a typed duplicate; none is a
driver exception; `assert_safe` holds for each.

### 8.7 Prohibited-source and payload scan

```
git status --short                       # 22 modified, 5 new files; no data files
git diff HEAD | grep -n 'foundry-actor-exports\|shared/worlds\|the-guild/data/actors'
```

The only matches are lines **1819–1820 of the diff**, which are the prohibited-
source list inside `docs/review/Handover information` itself. Neither
`/opt/discord-bots/foundry-actor-exports` nor
`/home/foundry/shared/worlds/the-guild/data/actors` was read, listed or opened at
any point. Pre-existing references to the export directory in
`docs/discovery/` and `docs/project-management/` are untouched.

`docs/review/Handover information` shows as modified in `git status`. That change predates this remediation — it was already uncommitted when this work started — and was left exactly as found, per the instruction to preserve unrelated user changes.

Every fixture value added by this remediation is synthetic by construction: the
adversarial Actor's fields are `MARKER-*` strings invented for the tests, per
`docs/discovery/fixture-strategy.md` §1. No real Actor payload was added.

### 8.8 Checks that could not be run

The repository configures **no** formatter, linter or type checker
(`requirements-dev.txt` is `-r requirements.txt` and `pytest>=8.2,<9`; there is
no ruff/black/mypy configuration). None was run, and this submission does not
claim otherwise. Adding one is out of this remediation's scope.

---

## 9. Files changed

### New

| File | Purpose |
|---|---|
| `adapters/database/translation.py` | I-1: constraint → rule mapping, SQLSTATE classification, `TranslatingSession` |
| `application/foundry/audit_policy.py` | I-2: per-action payload policy, written data classification, `enforced()` |
| `migrations/versions/0003_import_operation_digest.py` | B-1: `snapshot_imports.operation_digest` |
| `tests/test_audit_payload_policy.py` | I-2: 26 tests |
| `docs/review/phase-2-remediation-2-submission.md` | this document |

### Modified

| File | Change |
|---|---|
| `application/foundry/import_service.py` | B-1 binding and conflict refusal; I-1 conflict resolution; I-2 enforcement; request-key validation; closed `REFUSAL_CODES` |
| `application/foundry/reconciliation.py` | B-2 direction; I-2 closed `ISSUE_CODES`; I-3 `ComparableFieldReaders`; summary vocabulary |
| `application/snapshots.py` | B-1 `operation_digest`; request-key validation |
| `application/errors.py` | I-1 `UniquenessConflict`, `PersistenceError` |
| `application/bootstrap.py` | I-2 policy enforcement; `reason` removed |
| `adapters/database/unit_of_work.py` | I-1 `TranslatingSession` |
| `adapters/database/repositories.py` | B-1 `operation_digest` read/write |
| `adapters/database/tables.py` | B-1 column and check constraint |
| `domain/field_profile.py` | B-2 `DifferenceDirection`, required on database-authority fields |
| `domain/foundry_profile.py` | B-2 `character.display_name` declares its direction |
| `infra/postgresql/runtime-grants.sql.tmpl` | O-1 |
| `docs/operations/foundry-snapshot-import.md` | B-2 operator guidance |
| `tests/fakes.py` | typed conflicts matching the adapter's rule names; injectable failure |
| `tests/test_snapshot_import_service.py`, `tests/test_snapshot_database.py`, `tests/test_snapshot_reconciliation.py`, `tests/test_field_profile.py`, `tests/test_rejected_scope_absent.py`, `tests/test_runtime_grants.py`, `tests/test_runtime_grants_live.py` | the tests above |
| `tests/test_submission_traceability.py` | points at this submission; superseded records are not rewritten |

---

## 10. Remaining risks and unmet gate criteria

| Item | State |
|---|---|
| supervised real-export rehearsal | **PENDING — a maintainer action. Not performed, and not attempted.** |
| Data Owner attestation | **Not given.** |
| plan §9.4 operational windows | **Unset.** |
| Phase 2 gate | **Not claimed.** |
| independent re-review | **Requested below. Not performed.** |
| security re-review | **Requested below. Not performed.** |

Risks this remediation leaves open, stated rather than buried:

1. **The fake-level race tests simulate ordering; they do not race.** The
   PostgreSQL tests race for real, and the resolution branches are driven
   deterministically against PostgreSQL, but no test observes a loser taking a
   *specific* branch under genuine contention. I consider the combination
   sufficient; a reviewer may not.
2. **`_resolve_conflict` is called directly by three tests.** Calling a private
   method is deliberate — the alternative is a test that exercises the branch
   only when the scheduler cooperates — but it couples those tests to an
   internal name.
3. **`request_key` remains caller-supplied text in an append-only row.** It is
   bounded and printable and it is the idempotency key, so I judged removing it
   worse than keeping it. This is a decision, not an oversight, and it is the
   one I would most expect a security reviewer to want to overturn.
4. **The `PUBLIC` revoke is broader than the runtime role.** See §7.2.
5. **No formatter, linter or type checker exists to run.** §8.8.
6. **`0002` was not replaced, so the schema now needs two migrations to reach
   head.** I believe this is the correct reading of the constraint I was given;
   if the Acceptance Authority reads it otherwise, folding `0003` into `0002`
   is a small change.

---

## 11. Request for independent re-review

To **Codex, as Independent Reviewer** (plan §16.4, *import/reconciliation*):

Please re-review this remediation, and please provide the **separate,
separately reported security-focused pass** required by ruling D-5 (2026-08-02),
covering authorization, artifact handling, audit content and runtime grants.
Keeping the two reports distinct matters — a security concern absorbed into a
general review is easy to lose.

Specific things worth your attention, because they are where I made a judgement
rather than followed an instruction:

- the exclusion of `aggregate_versions` and `request_key` from the operation
  digest (§2), and the exclusion of the caller's authority from it;
- the decision to keep `request_key` in the audit payload (§5, risk 3);
- the decision to remove `display_name` from `snapshot_import.character.created`
  rather than document a narrow policy for it (§5);
- the decision to add `0003` rather than replace `0002` (§7.1);
- whether `PersistenceError` carrying a SQLSTATE is more disclosure than you
  want (§4);
- whether the `PUBLIC` revoke's breadth needs a deployment note stronger than
  §7.2.

**You recommend; you do not approve.** Peter Duscha records the gate decision. I
have not approved this work and do not claim the gate.

## 12. What this submission does not claim

- It does not claim the Phase 2 gate.
- It does not claim the supervised rehearsal was performed or attempted.
- It does not claim Data Owner attestation.
- It does not claim the unset §9.4 operational windows.
- It does not claim a formatter, linter or type checker was run.
- It does not authorize Phase 3.
