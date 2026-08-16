# P3.1 — OD-44 session-touch policy remediation submission

**Date:** 2026-08-15 · **Package:** Phase 3 P3.1 · **Owner:** Claude (working
Technical Lead) · **Status:** *Submitted for a new Codex independent
implementation re-review and a separately reported security-focused re-review.*
**Not accepted. P3.G1 remains open. P3.2 has not started.**

This submission does not overwrite any predecessor. It follows
`phase-3-p3-1-od-44-session-lifetime-remediation-submission.md` and leaves every
earlier dated submission unedited.

---

## 1. The remaining bypass, and what it meant

Codex's independent implementation and security re-reviews of 2026-08-15 returned
**one blocking finding** against the session-lifetime remediation submitted
earlier the same day. The finding is narrow and it is correct.

### What the previous remediation actually established

It corrected `SessionService.touch()` to select the idle duration from the
authentication method persisted on the trusted `SessionRecord`, and had
`SessionRepository.touch()` verify that method inside its conditional write. The
service path became correct, and it remains correct.

### What it claimed but did not establish

The repository's own API still took two independent arguments:

```python
SessionRepository(connection).touch(
    break_glass_session_id,
    now=now,
    idle=timedelta(minutes=60),               # N-06's ordinary window
    expected_auth_method=AuthMethod.WEBAUTHN,  # the row's OWN, correct method
)
```

The statement's predicate was `auth_method = :expected_auth_method`. It compared
a **method** against the row. It had no view whatever of the `idle` value passed
beside it. So the call above matched: the method was true, the duration was
false, and the row's idle window was extended to
`LEAST(now + 60 minutes, absolute_expires_at)` — for a break-glass session, its
sixty-minute absolute bound.

**Security consequence.** N-15 gives an emergency session fifteen minutes of idle
life *and* sixty minutes of absolute life. A break-glass session resolves to
exactly `{platform_administrator}`. Through this API, such a session could be
kept alive to its absolute bound with no re-authentication, which is the whole of
its lifetime — so N-15's idle value was, once again, inoperative for anyone
calling the repository directly. The absolute bound still held; that is why the
defect is easy to look past, and it is not a defence. "No extension beyond the
absolute bound" is a statement about the sixty-minute value, not a licence to
ignore the fifteen-minute one.

**The test offered as proof did not exercise it.** The replaced test supplied
`AuthMethod.DISCORD_OAUTH` against a break-glass row. That mismatch is refused —
by the method predicate, correctly — but a refusal of a **false method** is not
evidence about a **false duration paired with a true method**. The two are
different propositions, and only the first was tested.

**Records that were therefore false**, and are corrected by this submission:
TC-AUTH-19(h), SM-02's forbidden-transition row, logical schema §9.1's third
load-bearing property, T-05d's mitigation, and the C-P3.1-G change record and its
submission — each asserting that the ordinary window could not reach a break-glass
row "from either layer".

**Reachability, stated plainly.** No P3.1 HTTP route calls `touch()`; the
portal's request path does not exist yet. The bypass was therefore latent, and so
is its correction. That does not reduce the requirement: P3.2 is intended to
consume exactly this API, and N-15 must be structural before request-path wiring
exists rather than after it.

---

## 2. The correction

### 2.1 The policy object (`application/web/sessions.py`)

`SessionIdlePolicy` is a frozen, validated, complete mapping from `AuthMethod` to
idle `timedelta`, built by `from_settings(SessionSettings)` — N-06's
`idle_minutes` for `discord_oauth`, N-15's `emergency_idle_minutes` for both
break-glass methods. It is stored as ordered pairs rather than a `dict` so the
value object is genuinely immutable and comparable, and its constructor refuses:

- a mapping that omits any `AuthMethod` (an unmapped method would make the
  statement's `CASE` yield `NULL`, `make_interval` yield `NULL`, and `LEAST`
  — which discards `NULL` — return `absolute_expires_at`: the largest window the
  bypass could ever have produced, arrived at silently);
- a mapping that names a method twice; and
- any non-positive window.

It deliberately does **not** require the emergency window to be shorter than the
ordinary one. `WEB_SESSION_IDLE_MINUTES` may be configured down to 1 while
`WEB_EMERGENCY_SESSION_IDLE_MINUTES` ceilings at 15, so that ordering is a
property of the accepted defaults and not of every configuration the contract
permits; asserting it here would refuse a configuration the contract allows.

### 2.2 The enforcing statement (`adapters/web/repositories.py`)

`SessionRepository.__init__` now requires `idle_policy` as a keyword-only
argument, and `touch()` is:

```python
def touch(self, session_id: UUID, *, now: datetime) -> TouchedSession | None:
```

There is no duration, deadline or authentication-method parameter. One
conditional `UPDATE`, generated from the injected policy:

```sql
UPDATE sessions
   SET last_seen_at = CAST(:now AS timestamptz),
       idle_expires_at = LEAST(
           CAST(:now AS timestamptz)
               + make_interval(secs => CASE auth_method
                           WHEN :method_0 THEN CAST(:idle_seconds_0 AS double precision)
                           WHEN :method_1 THEN CAST(:idle_seconds_1 AS double precision)
                           WHEN :method_2 THEN CAST(:idle_seconds_2 AS double precision)
                       END),
           absolute_expires_at
       )
 WHERE id = :id
   AND auth_method IN (:method_0, :method_1, :method_2)
   AND revoked_at IS NULL
   AND idle_expires_at > CAST(:now AS timestamptz)
   AND absolute_expires_at > CAST(:now AS timestamptz)
RETURNING id, last_seen_at, idle_expires_at, absolute_expires_at
```

- **The window is chosen from the row.** `CASE auth_method` reads the column of
  the row being written, inside the write. Nothing a caller holds participates.
- **No literal duration exists in the adapter or the SQL.** The `CASE` arms and
  the `IN` list are generated from the policy; every value is a bind parameter
  originating in `SessionSettings`. The only interpolated text is generated
  parameter *names* (`:method_0`, `:idle_seconds_0`, …) from `enumerate`, never
  data.
- **`auth_method IN (…)` refuses an ungoverned method** rather than defaulting
  it. No reachable row can fail it — `ck_sessions_auth_method` admits exactly the
  three values the policy covers — and it is present because the alternative
  failure mode is the silent `NULL`-interval path described in §2.1.
- **Everything else is unchanged**: the same three liveness conditions, strict at
  both bounds, the clamp in the statement, `absolute_expires_at` in no `SET`
  clause, and a zero-row result returned as `None` for the service to type.

### 2.3 The service (`application/web/sessions.py`)

`SessionService.touch(record, *, now)` keeps its signature and now selects
nothing: it calls `self._sessions.touch(record.id, now=now)`. The record is still
the parameter — it is the caller's evidence that it resolved a session before
continuing it — but its `auth_method` is **not** forwarded, because a second copy
of the method travelling as an argument is precisely the thing that could
disagree with the row.

`bounds_for()` is unchanged in meaning and now takes its idle half from the same
`SessionIdlePolicy`, built in the service constructor through the same
`from_settings` factory. One derivation of the rule, run by both layers; the
service holds no independent copy of the numbers.

The refusal message no longer says "under this authentication method", since a
mismatched method is no longer among the refusal's causes.

### 2.4 Where policy is selected — the three layers, kept distinct

| Layer | What it does |
|---|---|
| **Configuration** (`SessionSettings`, `WEB_SESSION_IDLE_MINUTES`, `WEB_EMERGENCY_SESSION_IDLE_MINUTES`) | Owns the numbers. N-06 and N-15 are read here and nowhere else |
| **Composition** (`WebComposition.services`, `tools/session_revoke.py`) | Builds `SessionIdlePolicy.from_settings(...)` **once** and injects it. Validation failure is a startup failure |
| **Database** (the conditional `UPDATE`) | Enforces liveness — unrevoked, strictly inside both bounds — and selects the window from the persisted `auth_method`. No check constraint establishes liveness; `idle_expires_at <= absolute_expires_at` relates the two bounds to each other and neither of them to `now` |
| **Service** | Raises the typed `SessionTouchRefused` on a zero-row write and reports the persisted bounds |
| **HTTP** | **Absent in P3.1.** No route calls `touch()` |

### 2.5 What was preserved

Untouched and unregressed: the stale-record refusal and both strict bounds, the
absolute clamp, the never-written `absolute_expires_at`, the typed refusal and
persisted-result reporting, the rotation chain's lifetime and integrity,
provider-bound completion, AAD-bound PKCE handling, transaction-cookie/state
binding, opaque tokens, encrypted grants, audit atomicity, authorization,
CSRF/origin/security headers, rate limits, append-only history, runtime grants,
migration guards and the frozen visual assets. Migrations 0006–0008 were not
edited; **0009 was not changed**, because this finding is an interface and
policy-composition correction and needed no schema change. OD-45 is unchanged, no
P3.2 route was added, no direct-HTTP evidence was waived, and no dependency was
added.

---

## 3. Files changed and callers reviewed

**Production (4):**

| File | Change |
|---|---|
| `application/web/sessions.py` | New `SessionIdlePolicy`; `SessionService` builds one and uses it in `bounds_for`; `touch()` passes no duration or method; refusal docstrings and the module contract corrected; `__all__` extended |
| `adapters/web/repositories.py` | New `_touch_statement()` policy-driven statement builder; `SessionRepository.__init__` requires `idle_policy`; `touch(session_id, *, now)`; unused `timedelta` import removed; `TextClause` imported |
| `adapters/web/composition.py` | Builds `SessionIdlePolicy.from_settings(settings.session)` and injects it into `SessionRepository` |
| `tools/session_revoke.py` | Constructs the policy from its stated-unused bounds and passes it; comment explains why a revoke-only tool supplies one |

**Every caller and construction site, reviewed deliberately:**

| Site | Outcome |
|---|---|
| `adapters/web/composition.py:127` — `SessionRepository(...)` | Updated; the production injection point |
| `tools/session_revoke.py:101` — `SessionRepository(...)` | Updated; C-07 revocation only, never refreshes |
| `application/web/sessions.py` — `SessionService.touch` | Updated; the only caller of `SessionRepository.touch` |
| `tests/web/test_session_touch_lifetime.py` | Updated; uses a `_repository()` helper that constructs it as composition does |
| HTTP routes (`adapters/web/app.py`) | **None call `touch()`.** Verified by search; unchanged |
| `SessionRepository` protocol | There is no separate protocol/ABC for it — the service is duck-typed against the concrete repository, as before. Nothing to update, stated rather than left implicit |

**Tests (1):** `tests/web/test_session_touch_lifetime.py` — TC-AUTH-19(d)
rewritten, module contract updated, two `SessionRepository(connection)`
constructions routed through the new helper.

**Contracts and operations (5):** `docs/contracts/phase-3-state-machines.md`,
`docs/contracts/phase-3-logical-schema.md`,
`docs/contracts/phase-3-test-traceability.md`,
`docs/contracts/phase-3-threat-model.md`, `docs/operations/web-portal.md` — each
amended in place with a dated amendment that states what the previous wording
claimed and why it was false. No historical review record was rewritten.

**Project management (4):** `status.md` (appended), `raid-register.md` (I-09
amended), `change-log.md` (new record **C-P3.1-H**), `decision-register.md`
(OD-44 addendum continued; **no decision and no numeric value changed**).

**New (1):** this submission.

---

## 4. Tests — TC-AUTH-19, and what each case proves

`tests/web/test_session_touch_lifetime.py`, 25 tests, all against real
PostgreSQL with injected timestamps and **no sleeps**.

The inadequate mismatched-method test was **replaced**, not retained. It is not
kept as evidence of a separate property, because the property it established —
"a false method is refused" — is no longer meaningful: the method is not an
argument at all.

| Required evidence | Test | Result |
|---|---|---|
| 1. Direct repository touch of a Discord OAuth row applies N-06 | `test_a_direct_repository_touch_of_an_oauth_row_applies_the_ordinary_window` | pass |
| 2. Direct repository touch of WebAuthn and recovery-grant rows applies N-15 | `test_a_direct_repository_touch_of_a_break_glass_row_applies_the_emergency_window[WEBAUTHN]`, `[RECOVERY_GRANT]` | pass |
| 3. The supported signature has no `idle`, duration, deadline or method argument | `test_the_repository_touch_signature_admits_no_duration_or_method` — asserts the parameter set is exactly `{self, session_id, now}` **and** that eleven forbidden spellings are absent | pass |
| 4. The exact former bypass is **impossible**, not merely refused | `test_the_former_bypass_is_unavailable_rather_than_merely_refused[WEBAUTHN]`, `[RECOVERY_GRANT]` — the row's **true** method plus N-06's duration raises `TypeError`; four alternative spellings likewise; the complete row is then compared byte-for-byte and the supported call still refreshes it to `now + 15m` | pass |
| 5. The service still applies the same correct values | `test_an_oauth_session_touched_inside_its_window_receives_the_ordinary_idle`, `test_a_break_glass_session_touched_inside_its_window_receives_the_emergency_idle[×2]` | pass |
| 6. Stale records cannot revive idle-expired unrevoked rows | `test_a_stale_oauth_record_…`, `test_a_stale_break_glass_record_…[×2]` | pass (unchanged) |
| 7. Exact idle and absolute boundaries remain refused | `test_a_touch_exactly_at_the_idle_bound_is_refused`, `test_a_touch_exactly_at_the_absolute_bound_is_refused`, `test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it` | pass (unchanged) |
| 8. Accepted touches remain clamped and never change the absolute bound | `test_repeated_refreshes_converge_on_the_absolute_bound_and_never_pass_it` | pass (unchanged) |
| 9. Zero-row writes remain typed refusals leaving the complete row unchanged | `test_the_service_raises_the_typed_refusal_when_no_row_is_updated` plus `_assert_refused_and_untouched` in every refusal case | pass (unchanged) |
| 10. Touch/revoke concurrency | `test_a_concurrent_refresh_and_revocation_never_leaves_a_refreshed_live_session` — barrier rendezvous, two engines, real `READ COMMITTED` contention, no sleep | pass (unchanged) |
| 11. Rotation lifetime and integrity unchanged in meaning and passing | `test_session_rotation_lifetime.py` (TC-AUTH-18), `test_session_rotation_integrity.py` — **not edited by this remediation** | pass |

**Added beyond the required list**, because the new interface introduces state
that would otherwise be untested:

| Test | Property |
|---|---|
| `test_the_repository_cannot_be_constructed_without_an_idle_policy` | The policy is required; no construction site can silently default it |
| `test_an_idle_policy_must_cover_every_authentication_method` | A partial, duplicated or non-positive policy is refused where it is built |
| `test_the_configured_policy_is_the_one_the_numeric_register_names` | The configured mapping is N-06/N-15, and the service derives the same mapping from the same settings — the two layers cannot disagree |
| `test_a_row_whose_method_the_policy_does_not_govern_is_refused` | The `IN` predicate refuses rather than defaults. Made observable by dropping `ck_sessions_auth_method` inside a **rolled-back** transaction — the technique TC-AUTH-19c and TC-AUTH-18d already use. The row is a WebAuthn one, because relabelling a `discord_oauth` row would violate `ck_sessions_oauth_transaction_binding` instead and prove nothing about this predicate |
| `test_the_service_selects_the_idle_duration_and_the_caller_cannot` | Retained; the service signature admits no duration or method |

**Behavioural evidence first.** Cases 1, 2 and 5 establish that the *right*
window is applied; the signature assertions establish that there is no second way
to ask. Neither is offered alone.

---

## 5. Mutation testing

Thirteen mutants. Each anchor was asserted to match **exactly once** in its file
before application; each was applied, the focused suite run, and the file restored
from pristine bytes with the restoration verified by SHA-256; the focused suite
was rerun after the final restoration.

Focused suite: `tests/web/test_session_touch_lifetime.py`,
`test_session_rotation_lifetime.py`, `test_session_rotation_integrity.py`,
`test_sessions.py` — **64 passed** at baseline and after restoration.

| # | Mutation | Result | First killing test |
|---|---|---|---|
| M1 | Restore independent per-call duration selection (`idle=`/`expected_auth_method=` re-added and honoured) | **killed** | `test_the_repository_touch_signature_admits_no_duration_or_method`; also killed **behaviourally** by `test_the_former_bypass_is_unavailable_rather_than_merely_refused[×2]`, verified in a separate targeted run |
| M2 | Map WebAuthn to N-06 | **killed** | `…receives_the_emergency_idle[WEBAUTHN]` |
| M3 | Map recovery-grant to N-06 | **killed** | `…receives_the_emergency_idle[RECOVERY_GRANT]` |
| M4 | Swap the ordinary and emergency mappings | **killed** | `…receives_the_ordinary_idle` |
| M5 | Remove `revoked_at IS NULL` | **killed** | `test_a_revoked_session_cannot_be_touched` |
| M6 | Remove `idle_expires_at > :now` | **killed** | `test_a_stale_oauth_record_cannot_touch_an_idle_expired_unrevoked_row` |
| M7 | Remove `absolute_expires_at > :now` | **killed** | `test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it` |
| M8 | Make the idle comparison inclusive (`>=`) | **killed** | `test_a_touch_exactly_at_the_idle_bound_is_refused` |
| M9 | Make the absolute comparison inclusive (`>=`) | **killed** | `test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it` |
| M10 | Remove the absolute clamp (`LEAST` dropped) | **killed** | `test_repeated_refreshes_converge_on_the_absolute_bound_and_never_pass_it` |
| M11 | Silently accept a zero-row update (return a recomputed `RefreshedSession` instead of raising) | **killed** | `test_a_stale_oauth_record_cannot_touch_an_idle_expired_unrevoked_row` |
| M12 | Change `absolute_expires_at` during touch (`+ 600s` in the `SET` clause) | **killed** | `…receives_the_ordinary_idle` |
| M13 | Remove the governed-method `IN` predicate | **killed** | `test_a_row_whose_method_the_policy_does_not_govern_is_refused` |

**13 applied, 13 killed, 0 survived.** No mutant is reported as equivalent.

**Honest notes on two of them.** M7 and M9 are only observable inside the
rolled-back `ck_sessions_idle_within_absolute` drop: for every row the constraint
permits, `idle_expires_at > :now` already implies `absolute_expires_at > :now`, so
without that test they would be equivalent mutants. M13 is likewise only
observable inside a rolled-back `ck_sessions_auth_method` drop; today no reachable
row can fail that predicate, and the test says so rather than implying the guard
is exercised in ordinary operation.

**Restoration verified by digest** after the matrix:

```
adapters/web/repositories.py  3390ac1490058445cf7a92bb56ba2164e2ed46fd97fdeb5c9cf59e964266aa6c
application/web/sessions.py   9bde310ada21d2afb7f749ad8f6061f22aa1fd186bab87d8a854439f2cef728e
```

The mutation harness itself lives outside the repository, in the session
scratchpad, and no part of it was committed or left in the tree.

---

## 6. Verification

Every command below was run. Environment guard: the disposable `freedom_test`
PostgreSQL database via `TEST_DATABASE_URL`. Only synthetic data was used. No
live Discord, Foundry, Google Sheets, staging or production system was contacted.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_touch_lifetime.py -q` | **25 passed**, 0 failed, 0 skipped |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_touch_lifetime.py tests/web/test_session_rotation_lifetime.py tests/web/test_session_rotation_integrity.py tests/web/test_sessions.py -q` | **64 passed**, 0 failed, 0 skipped, 1 warning |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_oauth_completion_binding.py tests/web/test_identity_migration.py tests/test_oauth_completion_binding_migration.py -q` | **53 passed**, 9 warnings |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web -q` | **362 passed**, 0 failed, **0 skipped**, 14 warnings, 23.8s |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests -q` | **2260 passed**, 0 failed, 0 skipped, 1 warning, 136.5s |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests/test_database_schema.py tests/test_database_postgresql.py tests/test_runtime_grants.py tests/test_rejected_scope_absent.py -q` | **94 passed**, 1 warning |
| `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | `No new upgrade operations detected.` One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| `./venv-web/bin/python -m compileall -q adapters application tests` | Clean |
| `./venv/bin/python -m compileall -q models helpers ext main.py config.py` | Clean |
| `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 files `OK`, 0 non-`OK`** |
| `git diff --check` | Clean — no whitespace errors |
| Deterministic PostgreSQL concurrency evidence | TC-AUTH-19e (touch/revoke barrier rendezvous, two engines) and TC-AUTH-18e (concurrent rotation) — pass, no sleeps |
| Mutation matrix (§5) | 13 run, 13 killed, restoration verified by digest, focused suite rerun after restoration |

**Warnings.** The portal suite's 14 warnings are pre-existing `httpx`
`DeprecationWarning`s about per-request cookies, in `test_sessions.py`,
`test_oauth_completion_binding.py` and `test_oauth_flow.py`. The bot suite's single
warning is `audioop` deprecation from `discord/player.py`. None is new and none
comes from the changed code.

**No skipped database test counts as evidence, and none was skipped.** The
disposable database was available and both suites ran with zero skips.

**Formatter, linter and type checker: none is configured in this repository.**
Stated only after checking: there is no `pyproject.toml`, `setup.cfg`, `.flake8`,
`.ruff.toml`, `mypy.ini`, `tox.ini` or `.pre-commit-config.yaml`, and neither
`requirements-dev.txt` nor `requirements-web-dev.txt` lists a formatter, linter or
type checker. `compileall` under both interpreters is the available static check
and it was run.

**Deliberately unrun evidence.** Every staging-class, browser-class and
real-device-class check remains unrun, because staging does not exist (RAID I-06):
TC-LIM-02, TC-SEC-07's browser half, TC-OPS-01…05, TC-PERF-01…03. The direct-HTTP
portions of TC-BG-05b/c/e remain allocated to P3.G2 under OD-45 and are **not**
waived. No P3.2 route was added to produce HTTP evidence for this change, and no
deployment, staging or production system was touched.

**Suite counts.** Predecessor submissions' portal counts are superseded by this
run and were **not** edited in place. Current authoritative figures: **portal 362
passed / 0 failed / 0 skipped** (354 previously; the eight new tests are §4's
added cases), **bot 2260 passed / 0 failed / 0 skipped**.

---

## 7. Reachability now versus required future safety

Three statements, kept apart because conflating them is how the first remediation
came to claim more than it had:

1. **What is enforced in the database today.** The conditional `UPDATE` refuses a
   revoked, idle-expired or absolute-expired row, refuses a row whose method the
   policy does not govern, chooses the window from the row's own `auth_method`,
   clamps to the absolute bound and never writes it. That is enforced now,
   against real PostgreSQL, and is what the tests exercise.
2. **What is trusted configuration.** N-06 and N-15 live in `SessionSettings`,
   are validated there, and reach the statement as an injected immutable mapping.
   The adapter contains no duration. A policy that does not cover every method
   fails at composition, which is startup.
3. **What is not yet reachable.** No P3.1 HTTP route calls `touch()`. This
   correction is proven at the service and repository boundary and **not** in
   request handling. The P3.2 package that wires it must treat
   `SessionTouchRefused` — and `SessionRotationRefused` — as **end-the-session**
   outcomes: clear the cookie, treat the request as unauthenticated, never retry
   as authenticated and never fall back to serving the request.

Neither an authentication-method equality predicate nor a check constraint is
claimed to do anything it does not do: the first validates a method and never a
duration, and `ck_sessions_idle_within_absolute` relates the two bounds to each
other and neither to `now`.

---

## 8. Migration, deployment and rollback impact

**Migration: none.** No migration was added or edited. 0006–0008 were not touched
and 0009 needed no schema or metadata change — `alembic check` reports no new
upgrade operations. The defect and the correction are both in interface and
policy composition.

**Deployment.** Code-only, in the `freedom-web` process. No new environment
variable, no configuration contract change, no dependency, no runtime-grant
change, no service-file change. `WEB_SESSION_IDLE_MINUTES` and
`WEB_EMERGENCY_SESSION_IDLE_MINUTES` keep their meanings, defaults and ceilings.

**Rollback.** Revert the four production files. There is no data change to undo
and no schema state to reconcile; a rolled-back deployment reintroduces the
bypass, which is the reason the finding is blocking rather than advisory.

**Operational effect.** None observable today, because no route calls the
refresh. Documented behaviour is tightened: a break-glass idle window is fifteen
minutes at *every* layer, not only when reached through `SessionService`.

---

## 9. Dirty-worktree account

The worktree was dirty before this work began and is preserved. **Nothing
pre-existing was cleaned, reverted or reorganized**, and none of it is attributed
to this remediation.

**Changed by this remediation** (§3): four production files, one test file, five
contract/operations documents, four project-management documents, and this
submission. Nothing else.

**Pre-existing and untouched by this remediation** — modified: `.env.example`,
`.gitignore`, `adapters/database/repositories.py`, `adapters/database/tables.py`,
`application/audit.py`, `docs/adr/README.md`, `docs/discovery/open-decisions.md`,
`docs/review/phase-3-delivery-plan.md`,
`infra/postgresql/runtime-grants.sql.tmpl`, `pytest.ini`, `requirements-dev.txt`,
`tests/benchmark_snapshot_500.py`, `tests/conftest.py`,
`tests/test_benchmark_harness.py`, `tests/test_database_postgresql.py`,
`tests/test_database_schema.py`, `tests/test_rejected_scope_absent.py`,
`tests/test_runtime_grants.py`, `tests/test_snapshot_database.py`. Untracked and
carrying earlier uncommitted P3.1 work: `adapters/web/`, `application/web/`,
`docs/contracts/`, `docs/operations/web-portal.md`, `migrations/versions/0006–0009`,
`requirements-web*.txt`, `tests/web/`, `tests/web_fixtures.py`, `tools/*.py` and
the earlier `docs/review/phase-3-*` submissions.

**A note the reviewer needs when reading `git status`.** `adapters/web/`,
`application/web/`, `docs/contracts/` and `docs/operations/web-portal.md` are
**untracked**, so Git reports them as `??` and `git diff --stat` shows **no**
hunks for the four production files this remediation changed. The
project-management files *are* tracked, so their diffs are large — but most of
that volume is earlier uncommitted P3.1 work, **not** this change. §3 is the
authoritative list of what this remediation altered.

Nothing was committed, pushed or staged. `docs/review/Handover information` shows
as modified; that is the prompt file as supplied.

---

## 10. Residual risks

Listed as residuals, not as completed controls.

| # | Residual |
|---|---|
| RR-A | **P3.2 request handling is still unproven.** No HTTP route calls `touch()`, so this correction is proven at the service and repository boundary only. The P3.2 package must handle `SessionTouchRefused` and `SessionRotationRefused` as end-the-session outcomes. Until then it is a contract, not observed behaviour |
| RR-B | **Two predicates remain unreachable in production.** The absolute liveness predicate and the governed-method `IN` predicate are both unobservable through any row the check constraints permit; their evidence comes from rolled-back constraint drops. They are defence in depth against a future migration relaxing a constraint, and are exercised nowhere else |
| RR-C | **The policy object is still constructible directly.** `SessionIdlePolicy` validates completeness, uniqueness and positivity, but a caller with composition access can build a mapping with deliberately wrong values. That is inherent to configured policy — the same is true of the environment variables — and the control is that it is *configuration*, injected once and validated, rather than a per-call argument. It is not claimed to be tamper-proof against code that owns the composition root |
| RR-D | **The emergency window is not asserted to be shorter than the ordinary one**, deliberately (§2.1), because the configuration contract permits an ordinary window as short as one minute. A misconfiguration that made emergency sessions idle longer than ordinary ones would be accepted by this validation |
| RR-E | **Touch/rotation concurrency is not asserted**, because no reachable P3.1 sequence produces it. If P3.2 introduces a path where a refresh and a privilege rotation contend, that sequence needs its own deterministic evidence |
| RR-F | **`last_seen_at` is not updated on a refused refresh.** A refusal writes nothing at all, so an operator cannot distinguish "no requests arrived" from "requests arrived and were refused" by reading the session row |
| RR-G | **The C-P3.1-G change record's rejected-alternative list is reversed in part** (§ decision-register addendum). If the Acceptance Authority reads "derive the duration inside the repository" as a policy question rather than a layering one, it should be ruled explicitly rather than left to this submission's reading |

---

## 11. What is requested

- A **new Codex independent implementation re-review** of this remediation.
- A **separately reported, security-focused re-review**, distinct from the
  implementation pass.

The Technical Lead asks specifically that both passes attempt the bypass rather
than reading for it: construct a break-glass session and try to obtain N-06's
window through the repository by any supported route, including through the policy
object and through every construction site; and check that no site defaults the
policy.

**This submission claims neither Codex acceptance nor Acceptance Authority
approval.** No gate is marked ready, accepted or closed. Nothing was committed,
pushed or staged; no deployment, staging or production system was touched; no live
Discord, Foundry or Google Sheets service was contacted. P3.2 was not started and
no P3.2 route was added.

P3.1 OD-44 session-touch policy remediation submitted for Codex independent and
distinct security re-review; **P3.G1 remains open** pending those reviews and the
maintainer's acceptance decision.
