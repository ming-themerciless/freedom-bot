# C-24 independent-review remediation — handoff

Recorded 2026-08-12. Remediates the two findings returned by the independent
review of the C-24 submission-admission fence, and returns the package for
independent re-review.

**This work carries no independent approval. It does not close C-24, does not
close B-1, and does not close the Phase 2 gate.** Tests are evidence, not
acceptance authority. The durable admission design is retained in full; nothing
in it is withdrawn, and no observation-based settlement condition is revived.

---

## 1. Root cause and remediation

### Blocking — a uniqueness-conflict replay bypassed the fence

**Root cause.** The invariant forbids a closed generation from producing *either*
a new acceptance *or* a returned successful receipt. Two production branches
could return a stored receipt, and only one of them enforced that:

- `_store_and_record()`'s ordinary same-key replay was fenced — shared advisory
  lock, admission of the authenticated principal, openness, `admission_id` match;
- `_persist()`'s recovery from a lost `idempotency_key.scope_key` race called
  `_replay_stored()`, which opened a fresh transaction, read the winning row,
  rolled back and returned it. No lock, no admission, no openness requirement,
  no check that the receipt was earned under the presenting credential's
  generation.

The invariant lived in whichever branch its author remembered. One did not.

**Remediation.** `_replay_stored()` is deleted. Both ways of discovering that a
key is already spent now reach **one** principal-bound operation,
`SnapshotSubmissionService._fenced_replay`, which within a single transaction:

1. takes the shared side of the admission lock **before reading any receipt** —
   the only thing that orders a write-nothing replay against a closure, since it
   takes no foreign key and therefore no `KEY SHARE` lock;
2. resolves the admission of the principal id **the request authenticated as**,
   never a globally current generation and never the principal on the stored row;
3. requires that admission to remain open;
4. requires the stored record's `admission_id` to equal that admission's id;
5. applies the request-digest check `_replay()` has always made; and
6. builds the receipt inside the block, so the lock still holds when the answer
   is decided, then rolls back.

`_store_and_record()` no longer replays. On finding a spent key it raises the
private `_RequestKeyAlreadySpent`, which never escapes `_persist()`. The
authenticated `ServicePrincipal` is passed through recovery; no authorization is
taken from the stored record, from a current generation, or from caller data.

`_persist()`'s nested `try` became one bounded loop with a single
`_store_and_record` call site and a single decision point per conflict rule.

### Important — an absent SQLSTATE does not prove no commit

**Root cause.** `classify_database_failure` read "no SQLSTATE" as "could not
connect" and told the operator, for `close`, that no generation was closed and
the fence was unchanged. A connection can be lost while PostgreSQL is processing
or acknowledging `COMMIT`; the server may have committed while the client sees
only a driver error. The claim was an inference the evidence does not support —
and it is the one claim that, believed, authorizes a fresh export against a
generation that may already be settled.

**Remediation.** The phase is recorded, not inferred. `CommandProgress` is marked
inside the `with engine.begin()` block of `open` and `close`. A SQLSTATE-less
failure is then classified by that mark, and a server SQLSTATE continues to mean
the server answered and the transaction did not commit.

---

## 2. The consolidated boundary, and every production receipt path

Enumerated mechanically over `application/foundry/submission.py`, and asserted by
`test_no_stored_receipt_is_returned_outside_the_one_fenced_boundary`:

| Line | Path | Origin of the receipt |
|---|---|---|
| 465 | `submit` → `return self._submit(...)` | delegation |
| 532 | `_submit` → `return self._persist(...)` | delegation |
| 566 | `_persist` → `return self._store_and_record(...)` | delegation |
| 579 | `_persist` → `return self._fenced_replay(...)` (retry) | delegation |
| 598 | `_persist` → `return self._fenced_replay(...)` (race) | delegation |
| 817 | `_store_and_record` → `return receipt` | **acceptance**, constructed in the committed transaction |
| 905 | `_fenced_replay` → `return receipt` | **stored**, the value of `_replay(...)` |
| 993 | `_replay` → `return SubmissionReceipt(...)` | **stored**, rebuilt from `from_payload` |
| 388 | `SubmissionReceipt.from_payload` → `return cls(...)` | parse only; called from `_replay` alone |

A `SubmissionReceipt` therefore originates in exactly two places: the acceptance
that earns one, and the rebuild of a stored one. The rebuild is reachable only
through `_replay`, which is called only from `_fenced_replay`. No path can return
a stored successful receipt without crossing the principal-bound fence.

`adapters/http/wsgi.py` constructs no receipt; it renders what the service
returns. **No new repository interface was needed** — the boundary uses
`hold_against_closure`, `find_for_principal` and `idempotency.find`, all already
on `UnitOfWork` and implemented by both the SQLAlchemy and fake units of work.

---

## 3. The PostgreSQL race ordering, and what was observed

`tests/test_submission_admission_postgresql.py::test_a_request_that_loses_the_key_race_cannot_replay_across_a_closure`,
against the disposable `freedom_test` database, using the real
`SnapshotSubmissionService` over `SqlAlchemyUnitOfWork`. Every rendezvous is a
`threading.Event`; there are no sleeps.

1. The loser takes the shared lock, resolves P's open generation N, looks up the
   request key, finds nothing, and **pauses there**.
2. The winner runs to completion on another thread and commits its accepted
   receipt under N. (`ACCEPTANCES == 1`.)
3. The loser wakes, stores its identical bytes, sees the winner's snapshot row
   under `READ COMMITTED`, and loses the key on the database's own unique index:
   a real 23505, translated to `UniquenessConflict("idempotency_key.scope_key")`,
   with the session rolled back — **releasing the shared advisory lock**.
   Verified by instrumenting `_persist`'s branches during development: both race
   tests take the `idempotency_key.scope_key` arm, not the pre-check arm.
4. The loser pauses **between transactions**, holding no lock, and settlement
   closes N and commits — delayed by nothing.
5. The loser enters `_fenced_replay`.

**Observed outcome:** `SubmissionRefused("admission_closed")`, `worker.result is
None`. One `foundry_snapshots` row, one `idempotency_keys` row for the scope, one
`snapshot_submission.accepted` event. The winner's receipt still names admission
N and still names its snapshot. `submission_admissions.state = 'closed'`, and a
further submission under the old credential refuses with no new acceptance.

**Control** (`..._replays_while_the_generation_is_open`): the identical ordering
with step 4 omitted returns the winner's receipt with `duplicate=True`, the same
`snapshot_id` and `correlation_id`, one snapshot and one acceptance.

---

## 4. The commit-ambiguity model and its operator surface

| Evidence | Conclusion | Exit |
|---|---|---|
| Server SQLSTATE present | The server answered; the transaction did not commit | 4, 5, 6 as before |
| No SQLSTATE, no transaction established | Nothing was sent, nothing was written | **3** |
| No SQLSTATE, transaction established | **Outcome unknown — Unsettled** | **7** |

Exit 7 never says the fence is unchanged, never says the transition did not
commit, and never suggests a blind retry. It directs the operator to reconnect
and run `show`, then to confirm the transition through
`submission_admissions.correlation_id` / `closed_correlation_id` against its
append-only `snapshot_submission.admission_opened` / `.admission_closed` event,
and states that `close` is idempotent once verified while an ambiguous `open`
must be verified before another principal or generation is attempted. It carries
no traceback, URL, credential, parameter or SQL.

**A statement-phase loss is reported as unknown too**, although no `COMMIT` was
sent in that case. Separating it would mean trusting the client's account of how
far it got, which is exactly what a lost connection makes unreliable. False
uncertainty costs one `show`; a false assertion that settlement did not occur
costs a duplicate accepted export.

---

## 5. Files, interfaces, documentation, migrations

| File | Change |
|---|---|
| `application/foundry/submission.py` | `_fenced_replay` added; `_replay_stored` removed; `_RequestKeyAlreadySpent` added; `_persist` restructured; `_store_and_record`'s replay branch removed |
| `tools/submission_admission.py` | `CommandProgress`, `EXIT_OUTCOME_UNKNOWN = 7`, `TRANSITIONS`, `_outcome_unknown`; `classify_database_failure` takes `progress`; `open_admission`/`close_admission` take and mark it; `main` threads it |
| `tests/test_snapshot_submission.py` | 5 application tests, 2 syntax-tree tests |
| `tests/test_submission_admission_postgresql.py` | the race and its control; `PausingIdempotency`; `sequenced_service` with a per-unit gate plan |
| `tests/test_submission_admission_tool.py` | 8 classification tests, 4 injected-fault tests; existing call sites pass `progress` |
| `docs/operations/foundry-snapshot-submission.md` | exit-code table gains 7; new §5.2.1; §9's Unsettled rule corrected |
| `docs/project-management/change-log.md` | entry **C-24-R** |
| `docs/project-management/status.md` | Phase 2 row extended |

**Interfaces:** no repository protocol changed. **Migration 0005 is unchanged**;
its schema contract is untouched, so no rehearsal was required and none was run.
**No production service, database, proxy, Foundry instance, credential or real
snapshot was touched.** All fixtures are synthetic; the only database used is the
declared disposable `freedom_test`.

---

## 6. Named regression tests and mutations

**Mutation A — restore the unfenced `_replay_stored()`.** Applied, run, reverted,
re-run green. Killed by 4 tests:

- `test_a_request_that_loses_the_key_race_cannot_replay_across_a_closure` —
  fails with `isinstance(None, SubmissionRefused)`, i.e. the mutant **returned a
  successful receipt after the closure**, which is the defect itself;
- `test_no_stored_receipt_is_returned_outside_the_one_fenced_boundary` — fails
  naming `_replay_stored` as an extra caller of `_replay`;
- `test_a_lost_key_race_cannot_replay_a_receipt_across_a_closure` and
  `test_a_lost_key_race_refuses_a_receipt_earned_by_another_admission` — both
  `DID NOT RAISE SubmissionRefused`.

The control, `..._replays_while_the_generation_is_open`, **passes** under the
mutation, which is what makes the pair evidence about the fence and not the race.

**Mutation B — restore `sqlstate is None => definitely nothing committed`.**
Applied, run, reverted, re-run green. Killed by 9 tests, decisively
`test_a_lost_commit_acknowledgement_never_claims_the_fence_is_unchanged`, plus
`test_a_connection_lost_after_the_transaction_began_is_an_unknown_outcome`
(open/close), `test_an_unknown_outcome_never_claims_the_transition_did_not_commit`
(open/close), `test_an_unknown_close_says_a_verified_close_may_simply_be_repeated`,
`test_an_unknown_open_says_it_must_be_verified_before_another_is_attempted`,
`test_a_failure_during_the_closure_is_reported_as_an_unknown_outcome` and
`test_verification_after_an_unknown_outcome_finds_the_closure_and_its_evidence`.

---

## 7. Commands run

```bash
./venv/bin/pytest -q tests/test_snapshot_submission.py \
    tests/test_submission_admission_postgresql.py \
    tests/test_submission_admission_tool.py          # 125 passed (baseline)
./venv/bin/pytest -q                                  # 1967 passed, 253 skipped
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv/bin/pytest -q                              # 2220 passed, 0 skipped
(cd foundry-module && npm test)                       # 155 pass, 0 fail
git diff --check                                      # clean
./venv/bin/python -m compileall -q adapters application domain tools tests migrations
APP_ENVIRONMENT=test DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv/bin/alembic check                          # no new upgrade operations
```

Before this pass: 1952 passed / 247 skipped, and 2199 passed with
`TEST_DATABASE_URL`. The 21 new tests account for the difference exactly (15
without a database, 6 requiring one).

**No formatter, linter or type checker is configured in this repository** — there
is no `pyproject.toml`, `setup.cfg`, `.flake8` or `mypy.ini`, and
`requirements-dev.txt` declares only `pytest`. None was introduced here. New code
follows the surrounding style and its line lengths.

---

## 8. Deployment, operational and rollback implications

- **Deployment:** application and operator-tool code only. No migration, no
  schema change, no configuration change, no new privilege, no credential
  material. A deployment that skipped this change would be in the state the
  Blocking finding is open against.
- **Operational:** one new exit code (7) and one new verification procedure
  (§5.2.1). Operators trained on "any non-zero exit means nothing was closed"
  must be retrained: that is true of 1–6 and **false of 7**.
- **Performance:** an ordinary same-key retry now costs one extra short
  read-only transaction. Submission retries are rare and this path writes
  nothing.
- **Rollback:** reverting the application change reinstates the Blocking finding.
  Reverting the CLI change reinstates a false assurance during settlement.
  Neither has a data component; there is nothing to migrate back.

---

## 9. Limitations, and what is not proven

- **The commit-acknowledgement fault is modelled by a narrow double at the
  transaction boundary.** The transaction commits for real against the real
  database and the error replaces the reply. What is simulated is the loss of the
  reply, not any behaviour of PostgreSQL, and nothing here is offered as evidence
  about PostgreSQL's internals. A genuine mid-`COMMIT` connection loss was not
  injected through the real driver, because it cannot be produced
  deterministically from a test.
- **A statement-phase loss is classified as unknown although nothing committed.**
  That is a deliberate, documented loss of precision in the safe direction, not a
  limit of the mechanism.
- **The fake unit of work cannot lose a real race.** The application-level tests
  model the interleaving; the PostgreSQL tests are the evidence that it happens.
- **No production or staging system was exercised**, and no procedure was run as
  an operator procedure. §5.2.1 has been executed only against `freedom_test`.
- **Nothing here re-establishes anything about C-24's own design.** The evidence
  for the fence remains the C-24 record; this pass tests only what it changed.
- The instrumented confirmation that both race tests take the
  `idempotency_key.scope_key` arm was a development-time check; it is not carried
  as a permanent assertion, though `sequenced_service`'s gate plan would fail if
  the loser stopped opening a second transaction.

---

## 10. Status

**Superseded by the independent re-review and Acceptance Authority decision on
2026-08-12.** The re-review returned no findings and recommended closure. Peter
Duscha accepted that recommendation and directed the package to be committed and
work to proceed toward Phase 3. C-24 and B-1 are closed and the Phase 2 gate is
accepted. See `phase-2-c-24-independent-re-review-2026-08-12.md`.
