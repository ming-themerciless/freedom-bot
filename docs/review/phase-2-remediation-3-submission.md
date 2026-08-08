# Phase 2 remediation 3 — findings B-1R and S-1

Status: **In progress. Phase 2 is NOT closed and this document does not claim
its gate.** Prepared by the implementing agent (Claude) as working Technical
Lead. Independent re-review by Codex is required by plan §16.4
(*import/reconciliation*), with a **separate** security-focused pass; the
Acceptance Authority (Peter Duscha) records the gate decision.
**You recommend; you do not approve.**

Date: 2026-08-03

Answers:

- [`phase-2-remediation-2-codex-re-review.md`](phase-2-remediation-2-codex-re-review.md) — finding **B-1R**
- [`phase-2-remediation-2-codex-security-re-review.md`](phase-2-remediation-2-codex-security-re-review.md) — finding **S-1**

Supersedes for the milestone conclusion:
[`phase-2-remediation-2-submission.md`](phase-2-remediation-2-submission.md),
which remains the evidence record for the tree those two reviews read. The seven
findings it answered (B-1, B-2, I-1…I-4, O-1) were accepted by the re-review and
are **not** reopened here.

Starting point: `HEAD` is `c8a3da9`
(`c8a3da91c875ef64a578545b3a946352d5594c35`), unchanged from remediation 2.
**Nothing has been committed or pushed.** The work continues the same
uncommitted tree on branch `docs/platform-plan`; every remediation-2 change is
preserved.

The supervised real-export rehearsal was **not** performed. Neither prohibited
source was accessed (§9).

---

## 1. Disposition, finding by finding

| Finding | Disposition | Where |
|---|---|---|
| **B-1R** — an identical retry mixed the original durable result with a new reconciliation report | **Fixed.** A retry's result is reconstructed *entirely* from the immutable row the original apply committed — identity, counts, operation digest and a typed `ReconciliationFacts` read back from `snapshot_imports.summary`. Nothing is recomputed, and the duplicate path has no parameter a caller's report could enter through | §2 |
| **S-1** — a printable request key was an arbitrary permanent audit channel | **Fixed.** The verbatim key survives only in `snapshot_imports.request_key`, the column the idempotency lookup matches on. Permanent history carries `request_key_digest`, a domain-separated version-stable SHA-256; the old `request_key` payload key is *undeclared*, so the write-time policy refuses it. Refused rows are keyed by the digest too, and no refusal message quotes the key | §3 |

**No migration was added or changed.** The reconstruction is faithful from
columns that already exist (§2.3), so §7's migration checklist is confirmatory
rather than required — it was run anyway (§6.5).

Nothing in the handover's §5 *"Decisions already accepted — do not reopen"* was
changed. Specifically: the operation-digest field cut is untouched; authorization
is still rechecked at apply and is not part of the digest;
`platform_display_name_stale` and the absent `display_name` are unchanged;
comparable-field readers remain a construction-time invariant; database
exceptions still translate to typed errors classified by SQLSTATE; `0003`
remains a follow-on migration that fails closed; the runtime-grants template is
untouched; the negative guards are untouched; every artifact limit is unchanged.

---

## 2. B-1R — a retry returns the original result

### 2.1 The defect, restated

`_duplicate_of()` said it returned the original result. It returned the original
import's `import_id`, `correlation_id` and mutation counts beside a
**reconciliation report it computed at retry time** against the database as it
then stood.

Those two describe different instants, and the gap opens immediately rather than
eventually. The first apply's report says *one unmapped Actor, one create
candidate*; a reconciliation run one second later says *one mapped Actor*,
because the first apply created the mapping. Later unrelated state — another
character, a character claiming the imported Actor's display name, a second
import — moves it further, up to and including reporting a blocking error for an
import that committed cleanly. The receipt was a document describing no single
event.

The regression test that stood here
(`test_a_retry_receipt_describes_one_operation_and_mixes_nothing`) asserted only
that the report object was not the caller's and carried the same checksum. The
defect satisfied both. It has been removed, and §2.5 lists what replaced it.

### 2.2 What "the original result" is, given what is durable

The full `ReconciliationReport` is **not durable and deliberately never will
be**. Its per-Actor entries carry Actor names; its `ComparisonResult`s carry
Foundry and platform field values; its issue messages interpolate both. Storing
it would put exactly the data the accepted audit-content ruling keeps out of
append-only history — the same ruling that removed `display_name` from the
character-created payload and that S-1 extends.

What *is* durable, and always has been, is `snapshot_imports.summary`: counts,
identifiers and closed vocabularies, and no Actor value. That is the
reconciliation the platform permanently asserts about an import. So the original
result of an import is its identity, its counts and **those** facts.

This is the one judgement call in B-1R worth challenging, and §8.1 states it
plainly for that purpose.

### 2.3 The typed representation

`application/foundry/reconciliation.py` gains `ReconciliationFacts` — a frozen,
slotted value object with one field per summary key:

```
snapshot_checksum  folder_id  folder_path  profile_version  exporter
canonical_encoding  actors  mapped  unmapped  blocked  absent  errors
warnings  issue_codes  fields_differing  stale_platform_display_names
legacy_authority_deferred
```

Three things make it a representation rather than a cast:

- **One producer.** `ReconciliationReport.facts()` builds it from the report's
  own fields; `ReconciliationReport.summary()` is now *defined as*
  `facts().summary()`. There is no second renderer to drift from what is stored
  (`test_snapshot_reconciliation.py::test_the_summary_is_exactly_the_rendering_of_the_facts`).
- **A validated inverse.** `ReconciliationFacts.from_summary()` requires exactly
  the declared keys with the declared types — no missing key, no undeclared key,
  no coercion; `bool` is rejected where an `int` is declared, and negative counts
  are rejected. A `jsonb` column is a mapping of whatever was put in it, and
  casting one would have made "the original facts" mean "whatever the row holds"
  (`test_snapshot_reconciliation.py::test_facts_round_trip_through_a_stored_summary`,
  `test_snapshot_reconciliation.py::test_a_summary_missing_a_declared_key_is_refused`,
  `test_snapshot_reconciliation.py::test_a_summary_carrying_an_undeclared_key_is_refused`,
  `test_snapshot_reconciliation.py::test_a_mistyped_summary_value_is_refused_rather_than_coerced`).
- **A single table.** `_FACT_TYPES` drives both directions, so a field added to
  the facts without a row cannot round-trip and a row without a field fails
  construction.

**No new column, and no migration.** Every fact is already in `summary`, which
`0002` created and which the append-only trigger and the runtime role already
protect. That is the smallest possible change consistent with the handover's
instruction to persist additional typed facts only if reconstruction is
otherwise unfaithful.

### 2.4 The result, and where each field comes from

`ImportOutcome` is now the receipt, and every field except two is a durable fact
of the import named by `import_id`:

| Field | First apply | Retry |
|---|---|---|
| `status`, `import_id`, `correlation_id` | the record just written | the record read back |
| `snapshot_checksum` | the artifact in hand | `facts.snapshot_checksum` — the stored one |
| `operation_digest` | recomputed from the artifact | the record's own column |
| `created_count`, `updated_count`, `warning_count` | the record just written | the record read back |
| `reconciliation` | `report.facts()` — the facts stored on that record | `from_summary(record.summary)` |
| `duplicate` | `False` | `True` |
| `report` | the report this run reconciled and applied | `None` |

`result_facts()` is every durable fact as one mapping. `duplicate` is excluded
because it describes *this attempt* rather than the import; `report` because it
is the narrative of a run rather than something the import recorded. The
contract is then a single equality, and that is what the tests assert.

`_duplicate_of(record, unit_of_work)` takes **no report parameter**. "The caller
cannot supply the original result" is a property of the signature, asserted
directly (`test_snapshot_import_service.py::test_the_duplicate_path_cannot_be_handed_a_report_at_all`),
not a rule a future caller has to remember.

`ImportOutcome.refusal_code` was removed. It was never set by any path — refusals
raise `ImportRefused` — and a receipt type that can claim a refusal code
contradicts "every field is a durable fact of an applied import".

**Failing closed.** `_original_facts()` refuses rather than inventing, in two
cases, both as a typed `original_result_unavailable` refusal that writes no
durable state: a record that is not `APPLIED` (defence in depth — a refused row
is keyed so that no lookup can reach it), and a summary that will not read back,
which can only mean a version skew between the code that wrote it and the code
reading it. The message names the applied import so an operator can read the row
directly (`test_snapshot_import_service.py::test_an_unreadable_original_summary_is_refused_not_invented`).

### 2.5 B-1R evidence, requirement by requirement

| Handover requirement | Test |
|---|---|
| 1. first apply and exact retry have equivalent immutable facts | `test_snapshot_import_service.py::test_a_retry_returns_result_facts_equal_to_the_original_applys`, `…::test_a_retrys_facts_are_the_ones_the_original_import_recorded` |
| 2. still equivalent after unrelated state changed | `test_snapshot_import_service.py::test_a_retry_is_unchanged_after_unrelated_state_has_moved`, `test_snapshot_database.py::test_a_retry_is_unchanged_after_the_database_has_moved_on` |
| 3. does not reuse or accept the caller's report | `test_snapshot_import_service.py::test_a_retry_does_not_use_the_callers_preview_report`, `…::test_the_duplicate_path_cannot_be_handed_a_report_at_all` |
| 4. same key / different operation still refused, no earlier receipt | `test_snapshot_import_service.py::test_the_same_key_with_a_different_artifact_is_refused`, `…::test_the_same_key_with_a_different_folder_is_refused`, `…::test_the_same_key_with_a_changed_profile_version_is_refused`, `…::test_a_conflicting_key_returns_no_receipt_for_the_earlier_import`, `…::test_a_conflicting_key_claimed_concurrently_is_refused_not_duplicated` |
| 5. same-key concurrency: one effect, loser equivalent to winner | `test_snapshot_import_service.py::test_a_lost_request_key_race_returns_the_winner_as_a_typed_duplicate`, `test_snapshot_database.py::test_two_concurrent_applies_of_the_same_key_produce_one_effect`, `…::test_conflict_resolution_reads_the_winning_row_from_postgresql` |
| 6. same-input / different-key concurrency: truthful duplicate of the actual winner | `test_snapshot_import_service.py::test_a_lost_input_race_under_a_different_key_is_also_a_typed_duplicate`, `test_snapshot_database.py::test_two_concurrent_applies_of_the_same_input_produce_one_effect` |
| 7. no second audit event, import row, character or mapping | `test_snapshot_import_service.py::test_a_retry_writes_no_second_record_character_mapping_or_audit`, `test_snapshot_database.py::test_a_retry_writes_no_second_row_event_character_or_mapping` |
| 8. PostgreSQL exercises storage *and* reconstruction | `test_snapshot_database.py::test_the_stored_summary_is_exactly_the_result_the_apply_returned`, `…::test_a_retry_returns_the_original_facts_reconstructed_from_postgresql`, `…::test_a_retry_of_the_same_operation_returns_the_original_record` |

`assert_typed_and_consistent()` in `test_snapshot_database.py` — the helper every
threaded race asserts through — now compares `result_facts()` **whole** instead of
five fields, and asserts the loser has no report of its own. A receipt that mixed
a fresh reconciliation in would fail every concurrency test rather than none of
them.

`test_a_retry_is_unchanged_after_the_database_has_moved_on` closes the loop by
showing what a recomputation *would* have said: after the import, a fresh
preview reports `mapped == 1, unmapped == 0`, while the retry's result correctly
reports `unmapped == 1, mapped == 0, created_count == 1`.

### 2.6 What retains remediation-2 behaviour

Verified unchanged, with the tests that hold each:

- same key + same operation → typed duplicate, no second durable effect
  (§2.5 rows 1, 7);
- same key + different artifact / folder / folder path / profile / exporter →
  `request_key_conflict`, **no** earlier receipt (§2.5 row 4);
- the applied-input uniqueness rule is untouched
  (`test_snapshot_database.py::test_the_same_input_cannot_be_applied_twice`,
  `test_snapshot_database.py::test_a_refused_attempt_does_not_claim_the_input_identity`);
- authorization is re-resolved before any idempotency result is returned —
  `_resolve_authority()` still runs first in `apply()`
  (`test_snapshot_import_service.py::test_authorization_is_rechecked_at_apply_not_carried_from_the_preview`,
  `test_snapshot_import_service.py::test_the_authorization_port_is_asked_again_for_the_apply`,
  `test_snapshot_import_service.py::test_a_platform_administrator_alone_cannot_apply_an_import`);
- a concurrency loser re-reads a real winning row in a fresh transaction, and an
  unexpected failure is never a duplicate
  (`test_snapshot_import_service.py::test_an_unresolvable_conflict_is_refused_rather_than_called_a_duplicate`,
  `test_snapshot_import_service.py::test_a_persistence_failure_is_never_resolved_into_a_duplicate`,
  `test_snapshot_database.py::test_an_unresolvable_conflict_against_postgresql_is_a_typed_safe_refusal`);
- no caller-supplied preview or report is trusted (§2.5 row 3).

---

## 3. S-1 — the raw request key leaves permanent audit history

### 3.1 The defect, restated

`request_key` accepts any nonblank printable text up to 255 characters and was
copied verbatim into the `snapshot_import.applied` audit payload. Length and
control-character validation bound the *column*; they do nothing about a caller
placing a player name, an email address, a token or unrelated private text into
append-only history that Council and Platform Administrators can search. A
second copy in the audit event was not made exposure-free by the first copy
being necessary.

### 3.2 Where the key now lives

**One place: `snapshot_imports.request_key`.** That column is the idempotency
rule — `find_by_request_key` matches it exactly — so the verbatim text is
genuinely required there and nowhere else. Four other places carried it, and
none of them do now:

1. **The applied audit payload** carries `request_key_digest`, and the raw key is
   *undeclared* in the policy, so `enforced()` refuses any payload containing it
   rather than tolerating it (`test_audit_payload_policy.py::test_the_policy_rejects_the_old_raw_request_key_outright`).
2. **The `request_key_conflict` refusal message** quoted `existing.request_key`.
   A refusal message is the one part of a refusal that gets pasted into a ticket
   or a chat channel. It now says "This request key" and names only which bound
   inputs differ.
3. **The refused row's key** was `caller_key[:room] + ":refused:" + correlation_id`
   — a second verbatim copy in an append-only table, in a row nothing ever looks
   up by key. It is now `refused:<request_key_digest>:<correlation_id>`, which
   still keeps two refusals of one key distinct and is fixed-width, so the column
   bound holds by construction rather than by truncating the caller's text.
4. **Import summaries** never carried it and still do not, asserted directly.

Nothing logs it. The only logging helper in this path,
`adapters/safe_logging.log_expected_failure`, records a fixed category and an
exception class name and nothing else; no call site in the import path passes a
request key to any logger.

### 3.3 The digest construction

```python
REQUEST_KEY_DIGEST_DOMAIN = "freedom-blades/snapshot-import/request-key/v1"

def request_key_digest(request_key: str) -> str:
    return hashlib.sha256(
        f"{REQUEST_KEY_DIGEST_DOMAIN}\n{request_key}".encode("utf-8")
    ).hexdigest()
```

**Domain-separated**, so a request-key digest can never coincide with an
operation digest, a snapshot checksum or any other SHA-256 this codebase
produces over the same text; comparing two of them compares two request keys and
nothing else. **Versioned**, so the construction can change without new digests
silently appearing to be old ones — changing the string breaks grouping visibly,
which is exactly what a silent redefinition would hide. Deterministic, so two
events of one attempt still group; one-way, so the row no longer holds the text.

### 3.4 Is a separate digest necessary?

The handover asks this directly. Yes, and the reason is that the other three
identifiers cannot answer the question it answers:

| Identifier | Answers | Why it cannot replace the digest |
|---|---|---|
| `correlation_id` | which events belong to this **attempt** | new for every attempt, so it cannot group a retry with its original |
| `operation_digest` | **what** was applied | deliberately excludes the request key, so it says nothing about attempt identity — two different keys applying the same operation share it |
| `preview_token` | the full binding of one preview | includes the *volatile* aggregate versions, so two attempts under one key legitimately differ in it |

`request_key_digest` is the only stable function of the request key, and is
therefore the only way an operator holding a key can find every event recorded
under it. `operation_digest` was **added** to the applied payload at the same
time: it was named in the audit-policy data classification but no policy used
it, so the event could say who and when but not what. Together the three cover
attempt, operation and run (`test_audit_payload_policy.py::test_traceability_survives_the_minimization`).

### 3.5 Policy and written classification

`application/foundry/audit_policy.py` — the module whose docstring *is* the data
classification, enforced by `test_the_policy_module_documents_every_key_it_allows`:

- the "Caller-supplied and operator identity" class is replaced by
  **"Minimized stand-ins for caller-supplied text"** (`request_key_digest`,
  with the finding, the reasoning and the explicit statement that it is not a
  secret and never authorization) and **"Operator identity"** (`supervisor`);
- a new section documents the three identifiers and why the digest is not a
  duplicated one;
- `IMPORT_APPLIED.required` gains `request_key_digest` and `operation_digest` and
  loses `request_key`. Because `enforced()` checks *both* directions, the old key
  is now a hard failure and the new ones are mandatory — neither can be dropped
  silently.

`ImportOutcome`, `SnapshotImportRecord`, the `snapshot_imports.request_key`
column comment and `_require_valid_request_key` all now say, at the point a
reader meets them, that the input validation bounds the column and the digest is
what bounds the exposure.

### 3.6 S-1 evidence, requirement by requirement

Every fixture below uses a synthetic key: `MARKER-KEY player=Testperson Nobody
email=nobody@example.invalid token=MARKER-TOKEN-abcdef0123456789`. The address is
in `.invalid`, a reserved TLD that can never resolve; the name and the
token-shaped string were invented for the test. **No real credential or personal
datum is in any fixture.** Fragments are asserted individually, so an assertion
cannot pass because the string was re-spaced or truncated on the way in.

| Handover requirement | Test |
|---|---|
| 1. adversarial key stored only in the lookup column | `test_audit_payload_policy.py::test_the_raw_key_stays_in_the_lookup_column_and_reaches_no_audit_row`, `test_snapshot_database.py::test_the_raw_request_key_is_stored_only_in_the_lookup_column` |
| 2. no audit action or payload contains the key or its substrings | the same two, plus `test_audit_payload_policy.py::test_the_applied_payload_carries_a_digest_and_never_the_request_key` |
| 3. deterministic, and no collision across the matrix | `test_audit_payload_policy.py::test_the_digest_is_deterministic_and_distinguishes_distinct_keys` |
| 4. required/optional keys match exactly; the old raw key is rejected | `test_audit_payload_policy.py::test_the_policy_rejects_the_old_raw_request_key_outright`, `…::test_the_applied_payload_holds_exactly_its_policy`, `…::test_every_policy_declares_at_least_one_required_key` |
| 5. applied, duplicate, refused and concurrent paths introduce no raw key into audit content or safe error output | `test_audit_payload_policy.py::test_no_path_puts_the_raw_key_into_audit_or_safe_error_output` (parametrized over all four), `test_snapshot_database.py::test_a_refused_attempt_stores_no_request_key_text_at_all` |
| 6. traceability survives through the digest, correlation ID and operation identity | `test_audit_payload_policy.py::test_traceability_survives_the_minimization` |

Supporting: `test_snapshot_import_service.py::test_a_refused_attempt_records_the_operation_it_attempted`
(the refused row is keyed by digest and contains no `req-1`),
`test_snapshot_import_service.py::test_an_over_long_request_key_still_produces_a_recordable_refusal`,
`test_snapshot_import_service.py::test_two_refusals_of_the_same_key_are_two_distinct_rows`,
`test_snapshot_import_service.py::test_a_hostile_request_key_is_refused_where_it_arrives`,
`test_snapshot_import_service.py::test_the_record_itself_refuses_an_unwritable_request_key`.

The `test_snapshot_database.py` variant renders **every row of every retained
table** — `audit_events`, `foundry_snapshots`, `snapshot_imports` (excluding the
lookup column), `characters`, `external_actor_mappings` — and asserts no fragment
appears anywhere. A narrower query would only have proved the columns its author
thought of.

Database idempotency was not weakened: the unique constraint on `request_key`,
the partial unique index on applied input, and both `find_*` lookups are
unchanged. Request-key validation was not removed. Nothing accepts a digest in
place of a key.

---

## 4. Traceability — code, tests and documentation

### 4.1 Code

| File | Change | Finding |
|---|---|---|
| `application/foundry/reconciliation.py` | new `ReconciliationFacts`, `ReconciliationFactsError`, `_FACT_TYPES`, `_checked()`; `ReconciliationReport.facts()`; `summary()` redefined as its rendering | B-1R |
| `application/foundry/import_service.py` | `ImportOutcome` restructured (`reconciliation`, `operation_digest`, `warning_count`, optional `report`, `result_facts()`, `refusal_code` removed); `_duplicate_of()` reads the record only; new `_original_facts()`; new `request_key_digest()` and `REQUEST_KEY_DIGEST_DOMAIN`; `_refused_key()` digest-based; `request_key_conflict` message no longer quotes the key; applied payload swaps `request_key` for `request_key_digest` and adds `operation_digest`; new refusal code `original_result_unavailable`; module docstring | B-1R, S-1 |
| `application/foundry/audit_policy.py` | data classification rewritten for the digest; new traceability section; `IMPORT_APPLIED` policy updated | S-1 |
| `application/snapshots.py` | `SnapshotImportRecord` docstring and validation comment state where the key lives and what bounds the exposure | S-1 |
| `adapters/database/tables.py` | `snapshot_imports.request_key` column comment (comment only — **no schema change**) | S-1 |
| `tools/bootstrap_manager.py` | `render()` split into `_report_lines()` / `_facts_lines()`; a duplicate prints the original import's recorded counts and issue codes and names the import, instead of a fresh reconciliation under an "already applied" heading | B-1R |
| `docs/operations/foundry-snapshot-import.md` | §5 "What a duplicate result contains"; new §5a identifier table, digest recipe and operator warning; §9 checklist item | B-1R, S-1 |

No migration, no schema change, no dependency change, no configuration change.

### 4.2 Tests added or changed

| File | Added | Changed |
|---|---|---|
| `tests/test_snapshot_import_service.py` | 9 tests (§2.5, §3.6) | `test_a_retry_receipt_describes_one_operation_and_mixes_nothing` **removed** — it encoded the defect; the two lost-race tests now compare `result_facts()` whole; the refused-key and hostile-key tests assert the digest form |
| `tests/test_audit_payload_policy.py` | 6 S-1 tests | `test_the_applied_payload_records_the_callers_own_request_key_verbatim` **removed** — it asserted the defect as a declared decision |
| `tests/test_snapshot_database.py` | 7 tests (4 × B-1R, 2 × S-1, 1 storage) | `assert_typed_and_consistent()` compares `result_facts()` whole; one summary read moved to `outcome.reconciliation` |
| `tests/test_snapshot_reconciliation.py` | 6 round-trip / validation tests for `ReconciliationFacts` | — |
| `tests/test_bootstrap_cli.py` | `test_a_duplicate_prints_the_original_imports_own_record` | — |
| `tests/test_rejected_scope_absent.py` | — | one summary read moved to `outcome.reconciliation` |
| `tests/test_submission_traceability.py` | — | `SUBMISSION` / `SUPERSEDED` repointed at this document and remediation 2 |

Two tests were **deleted rather than adjusted**, and both deliberately: each
asserted the behaviour its finding identifies as the defect, so weakening them
would have left a test that reads as evidence while proving the wrong thing.

---

## 5. Commands run, and their results

Every command below was run in this working tree. Nothing is quoted that was not
executed.

### 5.1 Focused tests

```
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
    tests/test_snapshot_import_service.py tests/test_audit_payload_policy.py \
    tests/test_snapshot_reconciliation.py tests/test_bootstrap_cli.py
168 passed in 0.52s
```

```
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
    tests/test_snapshot_database.py
47 passed in 2.46s
```

### 5.2 The complete suite

```
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q
1566 passed, 1 warning in 8.97s
```

**Skips: none.** `-rs` was used to confirm it; there is no skip attributable to
this scope or to any other.

**Warnings: one**, and it is pre-existing and unrelated —
`venv/lib/python3.12/site-packages/discord/player.py:29: DeprecationWarning:
'audioop' is deprecated and slated for removal in Python 3.13`. It is raised by
`discord.py` at import, predates this work and is unchanged by it.

### 5.3 Concurrency, against real PostgreSQL

```
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
    tests/test_snapshot_database.py -k "concurrent or conflict_resolution or race" -v
tests/test_snapshot_database.py::test_the_stored_mapping_traces_to_the_snapshot_and_the_folder PASSED
tests/test_snapshot_database.py::test_two_concurrent_applies_of_the_same_input_produce_one_effect PASSED
tests/test_snapshot_database.py::test_two_concurrent_applies_of_the_same_key_produce_one_effect PASSED
tests/test_snapshot_database.py::test_a_concurrent_loser_never_escapes_as_a_driver_exception PASSED
tests/test_snapshot_database.py::test_a_concurrent_refusal_records_a_safe_audit_payload PASSED
tests/test_snapshot_database.py::test_conflict_resolution_reads_the_winning_row_from_postgresql PASSED
6 passed, 41 deselected in 1.28s
```

Two and three real connections, two real transactions, one durable effect, and a
loser whose `result_facts()` equal the winner's.

### 5.4 Injected-failure atomicity, including the audit write

```
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
    tests/test_snapshot_import_service.py -k "injected or audit_write_failure or record_write_failure or partial" -v
tests/test_snapshot_import_service.py::test_an_audit_write_failure_rolls_back_the_import PASSED
tests/test_snapshot_import_service.py::test_a_record_write_failure_leaves_no_partial_state PASSED
tests/test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state[snapshots] PASSED
tests/test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state[characters] PASSED
tests/test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state[external_actor_mappings] PASSED
tests/test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state[snapshot_imports] PASSED
tests/test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state[audit] PASSED
7 passed, 75 deselected in 0.07s
```

### 5.5 Live restricted-role and grants tests

```
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
    tests/test_runtime_grants_live.py -v
44 passed in 1.03s
```

Not skipped. The suite runs as the existing `freedom_runtime_test` role, seeds
hostile `PUBLIC` grants and asserts PostgreSQL's effective privileges afterwards.

### 5.6 Migrations

No migration was added or changed, so this is confirmatory. It was run anyway,
against `freedom_test` only:

```
$ DATABASE_URL=postgresql+psycopg:///freedom_test APP_ENVIRONMENT=test ./venv/bin/python -m alembic downgrade base
$ DATABASE_URL=postgresql+psycopg:///freedom_test APP_ENVIRONMENT=test ./venv/bin/python -m alembic upgrade head
$ DATABASE_URL=postgresql+psycopg:///freedom_test APP_ENVIRONMENT=test ./venv/bin/python -m alembic current
$ DATABASE_URL=postgresql+psycopg:///freedom_test APP_ENVIRONMENT=test ./venv/bin/python -m alembic check
INFO  [alembic.runtime.migration] Running downgrade 0003 -> 0002, Bind a request key to the operation it was spent on.
INFO  [alembic.runtime.migration] Running downgrade 0002 -> 0001, Create the Phase 2 snapshot, import and provenance schema.
INFO  [alembic.runtime.migration] Running downgrade 0001 -> , Create Phase 1 identity and transaction foundation.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001, Create Phase 1 identity and transaction foundation.
INFO  [alembic.runtime.migration] Running upgrade 0001 -> 0002, Create the Phase 2 snapshot, import and provenance schema.
INFO  [alembic.runtime.migration] Running upgrade 0002 -> 0003, Bind a request key to the operation it was spent on.
0003 (head)
No new upgrade operations detected.
```

`alembic check` reporting no new upgrade operations is the evidence that the
`tables.py` edit was a comment and changed no schema. The `0003` isolated
downgrade/upgrade and its preconditions were exercised in remediation 2 and are
unchanged; the full suite re-runs `downgrade base` / `upgrade head` in its own
fixtures on every run.

### 5.7 Byte-compilation, and the configured tooling

```
$ ./venv/bin/python -m compileall -q application adapters domain tools tests migrations
(no output; exit status 0)
```

**There is no formatter, linter or type checker configured by this repository.**
`pytest.ini` is the only tool configuration present; there is no `pyproject.toml`,
`setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini` or `ruff.toml`, and
`requirements-dev.txt` contains only `pytest`. `venv/bin` holds no `ruff`,
`black`, `flake8`, `mypy`, `isort` or `pylint`. Stated explicitly, as the
handover requires: none was run because none is configured, and introducing one
would be an unrelated change.

### 5.8 Scan of the working tree

```
$ git status --porcelain
 M adapters/database/repositories.py      M tests/fakes.py
 M adapters/database/tables.py            M tests/test_bootstrap_cli.py
 M adapters/database/unit_of_work.py      M tests/test_field_profile.py
 M application/bootstrap.py               M tests/test_rejected_scope_absent.py
 M application/errors.py                  M tests/test_runtime_grants.py
 M application/foundry/import_service.py  M tests/test_runtime_grants_live.py
 M application/foundry/reconciliation.py  M tests/test_snapshot_database.py
 M application/snapshots.py               M tests/test_snapshot_import_service.py
 M docs/operations/foundry-snapshot-import.md
 M "docs/review/Handover information"     M tests/test_snapshot_reconciliation.py
 M domain/field_profile.py                M tests/test_submission_traceability.py
 M domain/foundry_profile.py              M tools/bootstrap_manager.py
 M infra/postgresql/runtime-grants.sql.tmpl
?? adapters/database/translation.py       ?? docs/review/phase-2-remediation-2-submission.md
?? application/foundry/audit_policy.py    ?? docs/review/phase-2-remediation-3-submission.md
?? docs/review/phase-2-codex-findings-ba42467.md
?? migrations/versions/0003_import_operation_digest.py
?? docs/review/phase-2-remediation-2-codex-re-review.md
?? tests/test_audit_payload_policy.py
?? docs/review/phase-2-remediation-2-codex-security-re-review.md

(rendered two-up for width; the untracked files and 24 modified files are the
remediation-2 tree plus this remediation's changes. Nothing was removed.)
```

```
$ git diff --stat
 application/foundry/import_service.py      | 721 ++++++++++++++++++++---
 application/foundry/reconciliation.py      | 559 +++++++++++++++---
 application/snapshots.py                   |  58 +-
 adapters/database/tables.py                |  13 +
 tools/bootstrap_manager.py                 |  81 ++-
 docs/operations/foundry-snapshot-import.md |  62 +-
 tests/test_snapshot_import_service.py      | 901 +++++++++++++++++++++++++++--
 tests/test_snapshot_database.py            | 644 ++++++++++++++++++++-
 tests/test_snapshot_reconciliation.py      | 239 ++++++++
 tests/test_bootstrap_cli.py                |  41 ++
 tests/test_rejected_scope_absent.py        | 308 +++++++++-
 tests/test_submission_traceability.py      |  28 +-
 ... (24 files changed, 4276 insertions(+), 614 deletions(-) — the cumulative
 total for the whole uncommitted tree, not this remediation alone, since
 remediation 2 is also uncommitted)
```

Checked, and clean:

- **Secrets** — no key material, token, password, DSN or connection string was
  added. The only credential-shaped strings introduced are the synthetic
  `MARKER-TOKEN-…` and `nobody@example.invalid` test markers, which exist
  precisely to prove they do *not* reach history.
- **Foundry artifacts and Actor data** — nothing was added. Every fixture remains
  synthetic by construction in `tests/foundry_fixtures.py`; no file was added
  under any snapshot or export path.
- **Unsafe request-key logging** — none. No logger call in the import path
  receives a request key; `adapters/safe_logging.py` is unchanged and records a
  fixed category and an exception class name only.
- **Prohibited paths** — `grep -inE "foundry-actor-exports|shared/worlds|the-guild/data/actors"`
  over `git diff` returns two hits, both inside `docs/review/Handover
  information`, where they appear in the *prohibition itself* ("Do not read,
  enumerate, copy or otherwise access either prohibited source"). No code, test,
  fixture or document references either path, and neither was accessed (§9).
- **Unrelated changes** — none. The diff touches the import service, the
  reconciliation module, the audit policy, the snapshot records, one table
  comment, the operator tool's renderer, one operations document and the tests.
- **Migration reversibility** — no migration changed.

---

## 6. Security and privacy implications

**Improved.**

- Permanent, searchable audit history can no longer receive arbitrary
  caller-supplied text through the request key. The only remaining copy is in a
  column whose purpose is exact matching, and refused attempts no longer keep
  even that.
- Refusal messages — the part of a refusal most likely to be pasted somewhere
  else — no longer quote the key.
- Audit traceability improved rather than degraded: `operation_digest` now
  appears in the applied event, which it did not before, so an event can be tied
  to *what* was applied and not only to who, when and under which correlation ID.
- The retry receipt no longer leaks the *current* state of the database to a
  caller who is merely retrying. Under the old behaviour a retry's report was a
  live reconciliation — including, for instance, the display names of characters
  claiming a name. It is now the bounded facts the import recorded.

**Not changed.** Authorization is still re-resolved at apply before any
idempotency result is returned; Platform Administrator alone is still
insufficient; the bootstrap is still a separate one-time path; artifact parsing,
limits and the prohibition on live Foundry storage are untouched; database
exceptions still translate to typed errors carrying only a SQLSTATE; the
runtime-grants template is untouched.

**Residual, and stated plainly.** `request_key_digest` is an unkeyed SHA-256. It
is a data-minimisation control, not a secret: anyone who can guess a specific key
can confirm it by digesting it. No unkeyed digest can do better, and a keyed one
was rejected here because it would put a secret into an application service and
rotating it would silently break the grouping the digest exists to provide. The
control that matters for a *low-entropy* key is the outer boundary — Phase 3
should supply an opaque identifier (the Discord interaction ID) rather than
letting a human type one. §8.3 records this as an open item rather than a
resolved one.

---

## 7. Deployment, rollback and recovery

**Deployment.** No migration, no schema change, no configuration change, no new
dependency. Deploying this is a code deployment.

**Data implications.** None to existing rows. `snapshot_imports.summary` is read
in a new way, not written in a new way — the value stored is byte-identical to
what the previous code stored, which
`test_snapshot_database.py::test_the_stored_summary_is_exactly_the_result_the_apply_returned`
holds. No durable environment has ever run `0002` or `0003`, so there are no
pre-existing rows anywhere but the disposable `freedom_test`.

**Forward compatibility, and the one operational consequence worth stating.**
`ReconciliationFacts.from_summary()` fails closed. If a future change adds a key
to the summary, a retry of an import applied *before* that change will be
refused with `original_result_unavailable` rather than answered with partial
facts. That is the intended posture — the alternative is a receipt with invented
facts — but it is a real consequence, and the refusal message names the applied
import so an operator can read the row directly. The applied import itself
remains valid and readable; nothing about it is lost.

**Rollback.** Revert the code. There is nothing to undo in the database. A
reverted deployment reads the same `summary` values it always did; the only
behavioural difference is that audit rows written while this code was deployed
carry `request_key_digest` and `operation_digest` where older rows carry
`request_key`. Both are readable; neither breaks the other. Older audit rows are
**not** rewritten — they are append-only, and any raw request key already in one
stays there. §8.4 records that.

**Recovery.** Unchanged. The §7 procedure in
`docs/operations/foundry-snapshot-import.md` is untouched, and
`test_snapshot_database.py::test_restore_matches_the_pre_drill_inventory_and_supports_idempotent_rerun`
still passes.

---

## 8. The weakest judgement calls — please challenge these

### 8.1 "The original result" is the bounded facts, not a full report

A retry returns `ReconciliationFacts` and `report is None`. The argument is in
§2.2: the full report is not durable and must not become durable, because it
quotes Actor names and field values that the accepted audit-content ruling — and
S-1 itself — keep out of append-only history.

The alternative readings a reviewer might hold:

- *this is "hiding/removing the report", which the handover forbids.* I read that
  prohibition as forbidding the removal of reconciliation **from the result**, and
  the result does carry reconciliation, on both paths, equal on both paths. What
  is absent from a retry is the narrative of a run that did not happen.
- *persist the full report instead.* I rejected this: it would put Actor names,
  field values and interpolated messages into an append-only table, which is the
  opposite of the other blocking finding in this same remediation.

If the reviewer's reading is the first one, the fix is a decision about what may
be persisted, and that is a maintainer decision rather than mine to make quietly.

### 8.2 A retry's `report` is `None` rather than a third state

`None` says "this attempt reconciled nothing". A reviewer may prefer an explicit
type over `None`. I chose `None` with a documented field and a class docstring
that states the invariant; the operator tool branches on it explicitly, and one
CLI test covers the branch.

### 8.3 The digest is unkeyed

§6, "Residual". A reviewer may judge that a low-entropy request key needs more
than an unkeyed digest before the rehearsal. My view is that the remaining risk
belongs to the outer boundary — constrain what a caller may send — and that this
is Phase 3 work, but the security reviewer may reasonably rule otherwise.

### 8.4 Existing audit rows are not rewritten

They cannot be: `audit_events` is append-only in the application, the ORM and a
PostgreSQL trigger. Any raw request key written by earlier code stays in history.
Today that is only the disposable `freedom_test`, so nothing real is exposed — but
the reviewer should confirm they agree that is the right disposition rather than
one to be revisited if a durable environment ever runs this code before the fix.

### 8.5 Removing `ImportOutcome.refusal_code`

Dead — never set by any path — and contradictory to a type whose every field is a
durable fact of an applied import. It is nevertheless a public-shape change
beyond the literal minimum, and a reviewer may prefer it kept.

### 8.6 Two tests deleted rather than adjusted

`test_a_retry_receipt_describes_one_operation_and_mixes_nothing` and
`test_the_applied_payload_records_the_callers_own_request_key_verbatim` each
asserted the behaviour its finding identifies as defective. Adjusting them would
have left tests that read as evidence for something they no longer prove. Both
have named replacements in §2.5 and §3.6.

---

## 9. Prohibited sources and Actor data

Confirmed, for this remediation:

- **`/opt/discord-bots/foundry-actor-exports` was not read, enumerated, copied
  or otherwise accessed.**
- **`/home/foundry/shared/worlds/the-guild/data/actors` was not read,
  enumerated, copied or otherwise accessed.**
- No live Foundry LevelDB was accessed.
- No real Actor artifact, payload, name, field value or export was added to the
  repository. Every fixture used or added is synthetic by construction.
- No database other than the disposable `freedom_test` was touched, and no
  database was dropped.
- The supervised real-export rehearsal was **not** performed.

---

## 10. Remaining risks and unmet Phase 2 gate items

Unmet, and none of them mine to close:

1. **The supervised real-export reconciliation rehearsal — PENDING.** Not
   performed; explicitly outside this remediation's authority.
2. **Data Owner attestation — PENDING.** Not claimed.
3. **Backup/restore rehearsal against a real dataset — PENDING.** The drill test
   covers the mechanism against synthetic data only.
4. **Operational windows and retention periods — unset.** Owner decisions.
5. **Acceptance Authority gate decision — PENDING.** This document does not
   claim it.

Risks carried forward:

- `characters.display_name` still has no database-level fold or uniqueness rule;
  `find_by_display_name` scans and folds in Python. Bounded and documented, with
  a stated threshold (~2,000 rows, or any request path calling it).
- A low-entropy request key remains confirmable by anyone who can guess it
  (§6, §8.3).
- `ReconciliationFacts.from_summary()` fails closed across a future summary
  change (§7).

---

## 11. Request for independent review

Codex is asked, as **Independent Reviewer** under plan §16.4, for:

1. an **independent implementation re-review** of B-1R — in particular whether
   the bounded facts are a faithful "original result" (§8.1), whether the
   reconstruction is genuinely temporal-state-free, and whether the retained
   remediation-2 behaviours in §2.6 really are retained; and
2. a **separate security-focused pass** on S-1 — the digest construction, the
   completeness of the removal, the residual unkeyed-digest risk (§8.3), and the
   disposition of pre-existing audit rows (§8.4).

Please report the two separately, as before. **You recommend; you do not
approve.** The Acceptance Authority records the Phase 2 gate decision, and Phase
2 remains open and unapproved.
