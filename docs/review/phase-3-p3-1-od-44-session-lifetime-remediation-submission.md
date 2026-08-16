# P3.1 — OD-44 session-lifetime remediation submission

**Date:** 2026-08-15 · **Package:** Phase 3 P3.1 · **Owner:** Claude (working
Technical Lead) · **Status:** *Submitted for a new Codex independent
implementation re-review and a separately reported security-focused re-review.*
**Not accepted. P3.G1 remains open. P3.2 has not started.**

This submission does not overwrite any predecessor. It follows
`phase-3-p3-1-od-44-provider-binding-remediation-submission.md` and leaves every
earlier dated submission unedited.

---

## 1. What was found, and what it meant

Codex's independent re-review of 2026-08-15 returned **two blocking findings**,
both in the session idle refresh. A third defect was found while correcting them
and is remediated in the same change. The rotation-lifetime finding from
2026-08-14 was already corrected in code at review time but its governing records
still made false claims; those are completed here.

### Finding 1 — `touch()` could revive an idle-expired session

`SessionRepository.touch()` updated a row whenever
`id = :id AND revoked_at IS NULL` held.

`revoked_at IS NULL` establishes only that nobody has **ended** the session. An
idle-expired row stays unrevoked until some read observes it and marks it —
`resolve()` does that, but only for the request that happens to arrive. So a
caller that obtained a valid `SessionRecord`, and then called `touch()` after the
session's idle bound had passed, moved `idle_expires_at` back into the future.

**Security consequence.** An expired session is revived and stays live until its
absolute bound — up to 12 hours for a Discord session (N-07), 60 minutes for a
break-glass one (N-15). The idle bound exists so that an unattended browser, or a
cookie captured and used later, stops working; this defect removed that property
for any caller holding a record. It is the same stale-record class Codex found in
`rotate()` on 2026-08-14, in the other continuation operation.

Calling `resolve()` first is **not** the control, and the correction does not rely
on it: time advances after resolution, the record is a value the caller already
holds, and the write is the serialization boundary. The comparison has to be in
the statement that performs the write.

### Finding 2 — `touch()` gave break-glass sessions the ordinary idle window

`SessionService.touch()` always passed `SessionSettings.idle_minutes`. It never
consulted the persisted session's authentication method.

**Security consequence.** WebAuthn and recovery-grant sessions received N-06's
60-minute idle proposal instead of N-15's 15 minutes, bounded only by the
60-minute absolute clamp. N-15's idle value was therefore **inoperative for the
whole life of an emergency session**: a break-glass session — which resolves to
`platform_administrator` — could sit unattended for its entire absolute lifetime
instead of dying after fifteen minutes. Formally the session still never passed
its absolute bound, which is why the defect is easy to miss; but "no extension
beyond the absolute bound" is a statement about the 60-minute value, not a licence
to ignore the 15-minute one.

Reachability is stated rather than smoothed over: **no P3.1 production route calls
`touch()`**, so this was latent. That does not make it acceptable. The delivered
session service claims N-15 behaviour, P3.2 will consume it, and the control has
to be correct before that caller exists.

### Finding 3 (found during remediation) — a refused refresh was reported as success

`touch()` returned `None` unconditionally and never inspected `rowcount`. A
zero-row update — which is exactly the shape of every refusal above — was
indistinguishable from a successful refresh. Any caller would have continued as
though the session had been extended.

---

## 2. The correction

One cohesive change across two files. No migration, no dependency, no new
mechanism.

### 2.1 The enforcing statement (`adapters/web/repositories.py`)

```sql
UPDATE sessions
   SET last_seen_at = CAST(:now AS timestamptz),
       idle_expires_at = LEAST(
           CAST(:now AS timestamptz) + make_interval(secs => :seconds),
           absolute_expires_at
       )
 WHERE id = :id
   AND auth_method = :auth_method
   AND revoked_at IS NULL
   AND idle_expires_at    > CAST(:now AS timestamptz)
   AND absolute_expires_at > CAST(:now AS timestamptz)
 RETURNING id, last_seen_at, idle_expires_at, absolute_expires_at
```

Every property required of the fix is a property of this one statement:

| Requirement | How this statement satisfies it |
|---|---|
| One atomic conditional operation | One `UPDATE`. No preliminary read, cache, sleep, retry or trigger |
| Unrevoked and strictly inside both bounds | The three predicates, evaluated by PostgreSQL at write time |
| Equality at either bound is expired | Both comparisons are `>`, matching `resolve()`'s `<=` refusal |
| Duration from the persisted method, not the caller | The service selects it from the record's `auth_method`; this statement **verifies** that method (`AND auth_method = :auth_method`), mirroring `rotate()`'s `expected_*` arguments |
| Clamped to the existing absolute bound | `LEAST(…, absolute_expires_at)`, in SQL so no caller can pass a later value and have it taken |
| Touch never changes the absolute value | `absolute_expires_at` appears in no `SET` clause |
| A refusal writes nothing | Zero rows matched; a zero-row `UPDATE` changes nothing, writes no audit and creates no successor |
| Callers cannot misreport state | `RETURNING` yields the typed immutable `TouchedSession`, so the caller reports what PostgreSQL decided rather than recomputing `now + idle` |

New typed result: `TouchedSession(id, last_seen_at, idle_expires_at,
absolute_expires_at)` — a frozen, slotted dataclass beside `RotatedSession`.

### 2.2 The policy boundary (`application/web/sessions.py`)

```python
def touch(self, record, *, now: datetime) -> RefreshedSession:
    bounds = self.bounds_for(record.auth_method)
    refreshed = self._sessions.touch(
        record.id, now=now, idle=bounds.idle,
        expected_auth_method=record.auth_method,
    )
    if refreshed is None:
        raise SessionTouchRefused(...)
    return RefreshedSession(...)
```

- **The signature changed deliberately**, from `touch(session_id, *, now)` to
  `touch(record, *, now)`. The prompt's condition 9 is met rather than worked
  around: a bare id carries no trusted authentication method, so no correct policy
  decision can be made from it. The service now takes the trusted `SessionRecord`
  that `resolve()` produced. Its two callers were reviewed and updated (both are
  tests — no P3.1 route calls `touch()`).
- **`bounds_for` remains the single policy selector.** N-06/N-07 for
  `discord_oauth`, N-15 for `webauthn` and `recovery_grant`. The duration is
  passed as a `timedelta` and rendered with `make_interval(secs => …)`, so no unit
  is lost between the register and the statement, and the accepted numbers stay
  out of the adapter layer.
- **`SessionTouchRefused`** is new — narrowly named, alongside
  `SessionRotationRefused`, and documented with the caller's required response:
  **end the session; do not retry it as though still authenticated.**
- **`RefreshedSession`** carries the persisted bounds outward.

Transaction ownership is unchanged — the caller's transaction — and no provider
or network I/O moved into a database transaction.

### 2.3 What was preserved

The rotation-lifetime correction present at review time was **not** regressed or
reimplemented. Verified present and unchanged: the locked selection's idle and
absolute liveness predicates; inheritance of the predecessor's exact
`absolute_expires_at`; the successor idle clamp; no caller-supplied rotation
absolute expiration; `RotatedSession`/`IssuedSession` reporting persisted bounds;
one successor per predecessor; equality of account, method and OAuth binding
across a rotation; no caller-supplied rotation label; atomic successor insertion
and predecessor revocation; deterministic one-winner/one-typed-refusal
concurrency; OAuth-free WebAuthn and recovery-grant chains.

Also unweakened: the provider-bound atomic completion claim, `VerifiedCompletion`,
provider-token checks, AAD-bound PKCE recovery/erasure, transaction-cookie/state
binding, opaque tokens, encrypted token grants, expiry/revocation, atomic success
audit, exactly-one refusal audit, authorization, CSRF/origin/security headers,
rate limits, safe errors, append-only history, runtime grants, migration guards
and the frozen visual assets.

### 2.4 The corrected rotation test setup

`test_a_rotation_at_the_absolute_boundary_cannot_reach_past_it` prepared its
break-glass row with a single `touch()` that reached the 60-minute boundary
**only because touch was applying the ordinary 60-minute window to a WebAuthn
session** — the defect in Finding 2. Its old comment acknowledged this and called
it out of scope.

The setup is now a sequence of five refreshes at +10, +20, +30, +40 and +50
minutes, each inside the fifteen-minute window the previous one opened, each
asserting that the absolute bound did not move. This is the honest shape of the
request traffic the test stands in for, it reaches the same state (`idle_expires_at
== boundary`), and it depends on nothing that violates N-15. **The boundary
assertion was neither weakened nor deleted** — the test still asserts
`successor.idle_expires_at == boundary` with its original message, and still
asserts that one second past the boundary the successor cannot be rotated.

---

## 3. Files changed

| File | Change |
|---|---|
| `adapters/web/repositories.py` | `SessionRepository.touch()` rewritten as the conditional `UPDATE` above, with `expected_auth_method` and an `idle: timedelta`; new `TouchedSession`; `timedelta` added to the `datetime` import |
| `application/web/sessions.py` | `SessionService.touch()` takes the record, selects bounds from its method, raises `SessionTouchRefused`; new `RefreshedSession` and `SessionTouchRefused`; module docstring point 4 corrected to state that neither continuation may act on a session past either bound |
| `tests/web/test_session_touch_lifetime.py` | **New.** TC-AUTH-19, 17 tests |
| `tests/web/test_session_rotation_lifetime.py` | Setup of `test_a_rotation_at_the_absolute_boundary_cannot_reach_past_it` corrected (§2.4) |
| `tests/web/test_sessions.py` | One `touch()` call site updated to the record signature |
| `docs/contracts/phase-3-state-machines.md` | SM-02 rotation, idle-refresh and `expired` cells corrected; two forbidden transitions added; dated amendment note |
| `docs/contracts/phase-3-logical-schema.md` | §9.1 gains "Liveness is enforced by the statement, not by the constraints", with both exact statements, the three load-bearing properties and the three-layer distinction |
| `docs/contracts/phase-3-test-traceability.md` | TC-AUTH-18 and TC-AUTH-19 rows in §2, two §18 coverage-map rows, dated amendment note |
| `docs/contracts/phase-3-threat-model.md` | T-05d added; dated amendment note |
| `docs/contracts/phase-3-numeric-policy-register.md` | N-07, N-08, N-15 clarified — **no accepted value changed** |
| `docs/operations/web-portal.md` | §4.3 states the real break-glass idle window; new §4.3a on refusal/termination behaviour and operational impact |
| `docs/project-management/raid-register.md` | I-09 appended |
| `docs/project-management/status.md` | Dated 2026-08-15 update appended above the preserved previous status line |
| `docs/project-management/change-log.md` | C-P3.1-G appended |
| `docs/project-management/decision-register.md` | Dated OD-44 addendum; no decision changed |
| `docs/review/phase-3-p3-1-od-44-session-lifetime-remediation-submission.md` | **New.** This document |

**Migrations 0006–0008 were not edited. Migration 0009 was not changed** — the
defect and its fix are both in the repository and application boundary, and no
schema or metadata change was required. No dependency was added.

---

## 4. Tests

`tests/web/test_session_touch_lifetime.py` — **TC-AUTH-19**, 17 tests, all against
real PostgreSQL with injected timestamps. No sleeps anywhere in the module. The
stale-record condition is exercised explicitly throughout: resolve while valid,
advance **only** the injected `now`, then call `touch()` without resolving again.
Assertions are against persisted timestamps, not merely the returned exception.

| Required proof | Test |
|---|---|
| 1. Valid OAuth touch → N-06, clamped, absolute unchanged | `test_an_oauth_session_touched_inside_its_window_receives_the_ordinary_idle` |
| 2. Valid WebAuthn and recovery-grant → N-15, not the ordinary duration | `test_a_break_glass_session_touched_inside_its_window_receives_the_emergency_idle` *(parametrized over both methods; asserts the value is **not** what the ordinary duration would have produced)* |
| 3. Stale OAuth record cannot touch an idle-expired unrevoked row | `test_a_stale_oauth_record_cannot_touch_an_idle_expired_unrevoked_row` *(asserts `revoked_at IS NULL` before acting, so the row really is unmarked)* |
| 4. Stale WebAuthn and recovery-grant records likewise | `test_a_stale_break_glass_record_cannot_touch_an_idle_expired_unrevoked_row` *(parametrized)* |
| 5. Absolute-expired session cannot be touched | `test_an_absolute_expired_session_cannot_be_touched` |
| 6. Exact idle-bound and exact absolute-bound touches refused | `test_a_touch_exactly_at_the_idle_bound_is_refused` *(and accepted one microsecond earlier, so the refusal is the boundary)*; `test_a_touch_exactly_at_the_absolute_bound_is_refused` |
| 7. Every refusal leaves the row unchanged, no audit, no successor | `_assert_refused_and_untouched`, used by every refusal test — compares the **complete** row (`dict(after) == dict(before)`), not only the fields the statement would have written |
| 8. Repeated valid touches never change or pass the absolute bound | `test_repeated_refreshes_converge_on_the_absolute_bound_and_never_pass_it` *(and the session still dies at the bound)* |
| 9. Typed refusal when the conditional write affects no row | `test_the_service_raises_the_typed_refusal_when_no_row_is_updated` |
| 10. The API cannot supply the ordinary duration for a break-glass session | `test_the_service_selects_the_idle_duration_and_the_caller_cannot` *(signature assertion)*; `test_the_repository_refuses_a_mismatched_expected_authentication_method` *(direct repository guard, parametrized, with the matching method still accepted so the refusal is not a dead statement)* |
| 11. Existing rotation-lifetime tests pass after setup correction | `tests/web/test_session_rotation_lifetime.py`, 24 tests, all passing |
| 12. Deterministic concurrency in a reachable sequence | `test_a_concurrent_refresh_and_revocation_never_leaves_a_refreshed_live_session` |
| — | `test_a_revoked_session_cannot_be_touched` — the predicate that was already there |
| — | `test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it` — §5 |

**On the concurrency test (12).** The transaction paths were inspected before
writing it. `touch()` and `revoke()` are both `UPDATE`s carrying
`revoked_at IS NULL`, so they genuinely contend on one row under `READ COMMITTED`;
the loser blocks, re-evaluates when the winner commits, and PostgreSQL decides.
The property asserted is the one the implementation actually provides: **the
session ends revoked in both interleavings, and a refresh that lost is typed-refused
rather than reviving a session an operator has just ended.** It is deliberately
*not* a claim that one thread always wins — that would be an invented concurrency
guarantee. Touch/rotation contention is not separately claimed: no reachable P3.1
sequence runs them concurrently, and asserting an outcome for a sequence the
application cannot produce would be the same invention.

---

## 5. Mutation testing

Nine mutants, each a single textual substitution in production code, each run
against `test_session_touch_lifetime.py`, `test_session_rotation_lifetime.py` and
`test_sessions.py` (41 tests). Harness:
`/tmp/…/scratchpad/mutate.py` (outside the repository).

| # | Mutant | Result |
|---|---|---|
| M1 | Remove the touch **idle**-expiry predicate | **KILLED** — 4 failed |
| M2 | Remove the touch **absolute**-expiry predicate | **KILLED** — 1 failed |
| M3 | Idle bound inclusive (`>` → `>=`) | **KILLED** — 1 failed |
| M4 | Absolute bound inclusive (`>` → `>=`) | **KILLED** — 1 failed |
| M5 | Select the ordinary idle duration for every session | **KILLED** — 2 failed |
| M6 | Silently accept a zero-row touch | **KILLED** — 9 failed |
| M7 | Remove the idle-to-absolute clamp | **KILLED** — 3 failed |
| M8 | Touch changes the absolute expiration | **KILLED** — 7 failed |
| M9 | Remove the expected-authentication-method predicate | **KILLED** — 2 failed |

**No mutant is claimed equivalent.** Two required work to kill honestly, and both
are reported in full because the first attempt at each was wrong:

**The harness's own first run was invalid and is reported rather than discarded.**
The initial mutants for M1–M4 were anchored on the predicate line alone — but
`rotate()`'s locked read carries the identical predicate at the identical
indentation and appears earlier in the file, so those substitutions mutated
**rotation** and were "killed" by rotation tests in code the mutant never touched.
M3 and M4 survived, which is what exposed it. The anchors were widened to the
complete touch `WHERE` clause (unique by `auth_method` and the `RETURNING` list),
and the harness now asserts each anchor matches **exactly once** before applying.
The table above is the corrected run.

**M4 was genuinely equivalent until a test was added for it — and the test, not
the code, is what changed.** `ck_sessions_idle_within_absolute` guarantees
`idle_expires_at <= absolute_expires_at` for every row the database accepts, so
whenever `absolute_expires_at = now`, the idle predicate has already refused the
row; an inclusive absolute comparison is therefore unobservable through any
reachable row. Rather than declare it equivalent, the constraint-drop test
(§below) was extended: inside the rolled-back transaction it sets
`absolute_expires_at` to exactly `now` while the idle window is still live, which
isolates that one comparison. `>` refuses; `>=` would hand the row a fresh idle
window at the instant its lifetime ended. **No production code was altered to
make a mutant killable.**

**The absolute-predicate observability technique** (M2, M4) follows TC-AUTH-18c:
`ALTER TABLE sessions DROP CONSTRAINT ck_sessions_idle_within_absolute` inside a
transaction that is rolled back — PostgreSQL DDL is transactional, so nothing
outside it ever sees the missing constraint or the forbidden row. The test then
verifies from `pg_constraint` that the constraint is back and that the row's real
`absolute_expires_at` is intact.

**Restoration.** Every mutated file was restored from an in-memory copy of its
original bytes and verified byte-identical by SHA-256 against a digest taken
before any mutation:

```
adapters/web/repositories.py  60a7e0ac0eefba5d82a01a7b40f605d556f15682d47dfdc46ed0f56260a4ddfd
application/web/sessions.py   a9ee01387b59469c2a743c45e19a8315505dee4c8bd3dd1b41df63166d8732f9
```

The suite was re-run after restoration: `41 passed`.

---

## 6. Verification

Every command below was run. Environment guard: the disposable
`freedom_test` PostgreSQL database, via `TEST_DATABASE_URL`. Only synthetic data
was used. No live Discord, Foundry, Google Sheets, staging or production system
was contacted.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_touch_lifetime.py tests/web/test_session_rotation_lifetime.py tests/web/test_session_rotation_integrity.py tests/web/test_sessions.py -q` | **56 passed**, 0 failed, 0 skipped, 1 warning |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web -q` | **354 passed**, 0 failed, **0 skipped**, 14 warnings, 22.23s |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests -q` | **2260 passed**, 0 failed, 0 skipped, 1 warning, 131.67s |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_oauth_completion_binding.py -q` | **39 passed**, 9 warnings |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests/test_database_schema.py tests/test_database_postgresql.py tests/test_runtime_grants.py tests/test_rejected_scope_absent.py -q` | **94 passed**, 1 warning |
| `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | `No new upgrade operations detected.` One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| `./venv-web/bin/python -m compileall -q adapters application tests` | Clean |
| `./venv/bin/python -m compileall -q models helpers ext main.py config.py` | Clean |
| `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 files `OK`, 0 non-`OK`** |
| `git diff --check` | Clean — no whitespace errors |
| Mutation matrix (§5) | 9 run, 9 killed, restoration verified |

**Warnings.** The portal suite's 14 warnings are pre-existing `DeprecationWarning`s
from `httpx` about per-request cookies, in `test_sessions.py`,
`test_oauth_completion_binding.py` and `test_oauth_flow.py`. The bot suite's single
warning is `audioop` deprecation from `discord/player.py`. None is new, and none
comes from the changed code.

**No skipped database test counts as evidence, and none was skipped.** The
disposable database was available; both suites ran with zero skips.

**Formatter, linter and type checker: none is configured in this repository.**
That is stated only after checking — there is no `pyproject.toml`, `setup.cfg`,
`.flake8`, `.ruff.toml`, `mypy.ini`, `tox.ini` or `.pre-commit-config.yaml`, and
neither `requirements-dev.txt` nor `requirements-web-dev.txt` lists a formatter,
linter or type checker. `compileall` under both interpreters is the available
static check and it was run.

**Deliberately unrun evidence.** Every staging-class, browser-class and
real-device-class check remains unrun, because staging does not exist (RAID I-06):
TC-LIM-02, TC-SEC-07's browser half, TC-OPS-01…05, TC-PERF-01…03. The direct-HTTP
portions of TC-BG-05b/c/e remain allocated to P3.G2 under OD-45 and are **not**
waived. No P3.2 route was added to produce HTTP evidence for this change.

---

## 7. Layer distinction, migration, deployment and rollback

**Three layers, stated separately because conflating them is how the original
records became false:**

1. **Database enforcement.** The schema enforces that the two bounds relate
   correctly to each other (`idle_expires_at <= absolute_expires_at`), that a
   rotation chain cannot branch or cross, and the OAuth binding rules. **It does
   not and cannot enforce liveness** — that is a `now()` comparison, and `now()` is
   not immutable, which is the same reason the partial index on live sessions is
   not possible. Any claim that a check constraint stops a stale record from
   reviving an idle window is false, and no document in this change makes it.
2. **Application-service behaviour.** Liveness, the method-specific idle policy,
   the clamp and the typed refusals live in the two conditional statements and the
   service around them. This is where the corrections are, and this is the level at
   which all evidence in §4 and §5 was produced.
3. **The absent P3.1 HTTP caller.** No P3.1 route calls `touch()`. Rotation is
   reachable via `rotate_if_privileges_changed`; the idle refresh is not reachable
   from a request at all. The refusal handling documented in
   `web-portal.md` §4.3a is a **contract P3.2 must meet**, not behaviour running
   today.

**Migration impact: none.** No migration file was created or edited. `alembic
check` reports no drift.

**Deployment impact: none.** No configuration, environment variable, systemd unit,
runtime grant or dependency changed. `.env.example` is untouched by this work.

**Rollback consequences.** Reverting this change restores both defects and the
silent zero-row success; it requires no database action, because nothing about the
schema or the data changed. Rows written by the corrected `touch()` are
indistinguishable from rows the old one would have written for a *live* ordinary
session — the difference is only which refreshes are refused and which duration a
break-glass session gets — so there is no forward-only data migration and no
rollback data hazard.

---

## 8. Suite counts corrected

The predecessor submissions' portal-suite counts are superseded by this run and
were **not** edited in place. Current authoritative figures: **portal 354 passed /
0 failed / 0 skipped**; **bot 2260 passed / 0 failed / 0 skipped**. Where an
earlier document asserts a smaller portal count, this submission's figure is the
current one; the earlier documents remain as the dated record of their own runs.

---

## 9. Dirty-worktree account

The worktree was dirty before this work began and is preserved. **Nothing
pre-existing was cleaned, reverted or reorganized**, and none of it is attributed
to this remediation.

**Changed by this remediation** (§3): two production files, three test files
(one new), six contract/operations documents, four project-management documents,
and this submission.

**Pre-existing and untouched by this remediation** — modified: `.env.example`,
`.gitignore`, `adapters/database/repositories.py`, `adapters/database/tables.py`,
`application/audit.py`, `docs/adr/README.md`, `docs/discovery/open-decisions.md`,
`docs/review/phase-3-delivery-plan.md`,
`infra/postgresql/runtime-grants.sql.tmpl`, `pytest.ini`,
`requirements-dev.txt`, `tests/benchmark_snapshot_500.py`, `tests/conftest.py`,
`tests/test_benchmark_harness.py`, `tests/test_database_postgresql.py`,
`tests/test_database_schema.py`, `tests/test_rejected_scope_absent.py`,
`tests/test_runtime_grants.py`, `tests/test_snapshot_database.py`.

**A note the reviewer needs when reading `git status`.** `adapters/web/`,
`application/web/`, `docs/contracts/` and `docs/operations/web-portal.md` are
**untracked directories/files** carrying the whole uncommitted P3.1 package. Git
therefore reports them as `??` rather than showing a diff, and `git diff --stat`
shows **no** hunks for the two production files this remediation changed. The
project-management files *are* tracked, so their diffs are large — but most of
that volume is earlier uncommitted P3.1 work, **not** this change. §3 is the
authoritative list of what this remediation altered.

Nothing was committed, pushed or staged. `docs/review/Handover information` shows
as modified; that is the prompt file as supplied.

---

## 10. Residual risks

| # | Residual |
|---|---|
| RR-A | **P3.2 request handling is still unproven.** No HTTP route calls `touch()`, so the correction is proven at the service and repository boundary only. The P3.2 package must handle `SessionTouchRefused` and `SessionRotationRefused` as end-the-session outcomes — clear the cookie, treat the request as unauthenticated — and must not retry or fall back to serving the request. Until then this is a contract, not observed behaviour |
| RR-B | **The absolute predicate remains unreachable in production.** `ck_sessions_idle_within_absolute` makes it unobservable through any legitimate row; its evidence comes from a rolled-back constraint drop. It is defence in depth against a future migration relaxing the clamp, and it is exercised nowhere else |
| RR-C | **Touch/rotation concurrency is not asserted**, because no reachable P3.1 sequence produces it. If P3.2 introduces a request path where an idle refresh and a privilege rotation can contend, that sequence needs its own deterministic evidence |
| RR-D | **`last_seen_at` on a refused refresh is deliberately not updated.** A refusal writes nothing at all, so an operator cannot distinguish "no requests arrived" from "requests arrived and were refused" by reading the session row. Refusals are visible through audit events on revocation, not through the session row |
| RR-E | The clarified readings of N-07, N-08 and N-15 are recorded as clarifications because no numeric value changed. If the Acceptance Authority considers any of them a reinterpretation rather than a clarification, it should go through the register's §5 change control instead |

---

## 11. What is requested

- A **new Codex independent implementation re-review** of this remediation.
- A **separately reported, security-focused re-review**, distinct from the
  implementation pass.

The Technical Lead asks that both passes test the stale-record path specifically —
resolve while valid, advance only the injected `now`, continue the session without
re-resolving — and check both boundary comparisons for strictness, since an
inclusive absolute comparison is an equivalent mutant for every row the check
constraint permits and is only falsifiable inside a rolled-back constraint drop.

**This submission claims neither Codex acceptance nor Acceptance Authority
approval.** No gate is marked ready, accepted or closed. Nothing was committed,
pushed or staged; no deployment, staging or production system was touched; no live
Discord, Foundry or Google Sheets service was contacted.

P3.1 OD-44 session-lifetime remediation submitted for Codex independent and distinct security re-review; P3.G1 remains open and P3.2 has not started.
