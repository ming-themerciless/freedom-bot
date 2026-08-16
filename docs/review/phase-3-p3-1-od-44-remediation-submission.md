# Phase 3 P3.1 — OD-44 completion-binding remediation submission

**Prepared:** 2026-08-14 · **Package:** P3.1 post-decision remediation · **Owner:**
Claude (Working Technical Lead) · **Status:** **Submitted for Codex independent
implementation re-review and a separately reported security-focused re-review.
Not accepted. P3.G1 is open. P3.2 has not started.**

**Authority:** Peter Duscha's 2026-08-14 rulings on I-07/OD-44 and I-08/OD-45,
recorded in
[`phase-3-p3-1-sm-01-completion-binding-decision.md`](phase-3-p3-1-sm-01-completion-binding-decision.md) §7
and
[`phase-3-p3-1-tc-bg-05-http-evidence-decision.md`](phase-3-p3-1-tc-bg-05-http-evidence-decision.md) §5,
and the task in `docs/review/Handover information`.

**Predecessors, preserved unedited:**
[`phase-3-p3-1-submission.md`](phase-3-p3-1-submission.md) and
[`phase-3-p3-1-remediation-submission.md`](phase-3-p3-1-remediation-submission.md).
Nothing in either was rewritten; this is a dated addition, and the records that
point at them were amended by addition too.

---

## 1. Outcome in one table

| Finding | Ruling | Disposition |
|---|---|---|
| 1 — a session is not durably bound to a consumed OAuth transaction | OD-44, Option 1 with the single-FK refinement | **Remediated.** Migration 0009, the atomic completion claim, the bound session, 30 new portal tests and 4 new migration tests, 4 mutations run and reverted, all killed |
| 3 — required break-glass HTTP evidence conflicts with package order | OD-45, Option 1 | **No code change, and none was authorized.** No P3.2 route was added; no HTTP evidence was waived. §4 evidences the absence |

**P3.G1 is not ready and is not closed. P3.2 has not started. Nothing is
committed.**

**One reading of the ruling is declared rather than assumed** — the unique index
is scoped to non-rotated sessions. §3.3 states the problem, the alternatives and
why this reading preserves both of the ruling's stated purposes. It is the one
item on which I ask for explicit confirmation.

---

## 2. OD-44 mapped to implementation

### 2.1 The ruling, clause by clause

| Ruled clause | Where it is implemented | Tests |
|---|---|---|
| `oauth_transactions` gains `completion_claimed_at TIMESTAMPTZ NULL` | `migrations/versions/0009_oauth_completion_binding.py` `upgrade()`; `adapters/database/tables.py` `oauth_transactions` | TC-AUTH-14 · `test_0009_upgrades_downgrades_and_re_upgrades_with_its_documented_cost`, `test_the_downgrade_is_reversible_on_an_empty_database` |
| `sessions` gains `oauth_transaction_id UUID NULL` referencing `oauth_transactions.id` with `RESTRICT` | 0009 `upgrade()`; `tables.py` `sessions` | TC-AUTH-14 · `test_the_binding_foreign_key_declares_restrict` (read from `pg_constraint`, not from the revision source); TC-AUTH-13e · `test_the_database_refuses_a_session_naming_a_transaction_that_does_not_exist` |
| `sessions.oauth_transaction_id` is `UNIQUE` | 0009 `upgrade()` unique index `uq_sessions_oauth_transaction_id`, scoped `WHERE rotated_from_session_id IS NULL` — **see §3.3** | TC-AUTH-13e · `test_the_database_refuses_a_second_completion_session_for_one_transaction` |
| A check constraint requires it exactly when `auth_method = 'discord_oauth'`, and null for WebAuthn and recovery-grant sessions | 0009 `ck_sessions_oauth_transaction_binding`, transcribed exactly: `(auth_method = 'discord_oauth') = (oauth_transaction_id IS NOT NULL)` | TC-AUTH-13e · `test_the_database_refuses_a_discord_oauth_session_with_no_transaction`, `test_the_database_refuses_a_break_glass_session_that_names_a_transaction[webauthn]`, `[recovery_grant]` |
| No reverse `oauth_transactions.session_id` column or foreign key | **Absent.** The table's complete column list is `id, state_hash, pkce_verifier_ciphertext, nonce, key_version, return_path, provider_key, created_at, expires_at, consumed_at, completion_claimed_at, client_ip_hash` — no session reference of any kind. `sessions` carries exactly three foreign keys, all `RESTRICT`: `oauth_transaction_id → oauth_transactions.id`, `platform_account_id → platform_accounts.id`, `rotated_from_session_id → sessions.id`. The schema contract §9.2 states the absence | Structural: `tests/test_database_postgresql.py::test_migration_matches_table_metadata` fails if the metadata and the migration disagree; `test_every_foreign_key_declares_delete_behaviour` covers the new key |
| Completion claim, account/identity and membership effects, token storage, bound session creation and success audit commit atomically in one database transaction after provider I/O | `application/web/oauth.py` `OAuthLoginService.complete()`; the caller's single `engine.begin()` in `adapters/web/app.py` `_in_transaction` | TC-AUTH-13g · `test_a_failure_at_any_step_rolls_the_whole_completion_back` (6 parameters), `test_a_commit_failure_after_a_complete_call_leaves_no_session_and_no_claim` |
| The provider call remains outside every database transaction | Unchanged. `exchange()`/`verify()` are awaited between the `consume` and `complete` threadpool calls, each of which owns its own transaction | Unchanged structural evidence; `test_a_provider_failure_after_consumption_leaves_a_consumed_unclaimed_transaction` (4 parameters) exercises the seam |
| Verifier recovery and erasure remain one statement before provider I/O | Unchanged — `OAuthTransactionRepository.consume` is untouched | Existing TC-AUTH-12 (a)–(d), still passing |
| A consumed transaction may remain uncompleted, cannot be replayed, and must never yield a session unless the claim succeeds | The claim is the first statement of `complete()`; a refusal rolls it back | TC-AUTH-13f · `test_the_process_death_seam_leaves_no_session_and_no_replayable_transaction` |

### 2.2 Changed production files

| File | Change |
|---|---|
| `migrations/versions/0009_oauth_completion_binding.py` | **New.** The two columns, the `RESTRICT` foreign key, the unique index, both check constraints, and a precondition that refuses with a count and a remedy rather than letting `ADD CONSTRAINT` fail. Reversible |
| `adapters/database/tables.py` | The same objects in SQLAlchemy metadata, so `alembic check` keeps them from drifting apart |
| `adapters/web/repositories.py` | `OAuthTransactionRepository.claim_completion()`; `SessionRepository.create(oauth_transaction_id=…)`; `SessionRecord.oauth_transaction_id`, populated by `resolve()` and `live_sessions()`; `purge_expired()` now skips referenced rows (§3.4) |
| `application/web/oauth.py` | `complete(transaction_id=…)`; the claim as its first statement; the typed refusal; the bound session. Also one **documentation correction**: the docstring claimed a non-member's membership projection was "still recorded", which is false — the refusal raises before `record()` and rolls the transaction back regardless, as TC-AUTH-08 already asserted. No behaviour changed |
| `application/web/sessions.py` | `begin(oauth_transaction_id=…)` passed straight through; `rotate_if_privileges_changed` carries the binding forward |
| `application/web/refusals.py` | `LoginRefusalReason.COMPLETION_NOT_CLAIMABLE`, deliberately **not** in `ROUTE_RECORDED_REASONS` — the service describes it, the recorder writes it once |
| `adapters/web/app.py` | One argument added to the `complete` closure. The route's structure, ordering and terminal exits are unchanged |

**Migrations 0006, 0007 and 0008 were not edited.** `git status` shows them
untracked and unmodified since their submission.

### 2.3 The claim statement

```sql
UPDATE oauth_transactions
   SET completion_claimed_at = :now
 WHERE id = :id
   AND consumed_at IS NOT NULL
   AND completion_claimed_at IS NULL
RETURNING id
```

Each predicate refuses a different thing, and `claim_completion()` returns
whether a row matched. Zero rows raises `AuthenticationFailure(code=
"transaction_unknown")` carrying a `FailureAudit` whose payload is
`{"reason": "completion_not_claimable"}` — a typed, safely audited refusal, not a
warning, and never a session. The browser-facing code is drawn from the existing
closed `_LOGIN_FAILURE_CODES` set; the operator-facing reason is finer, which is
the split TC-AUTH-11 already established.

---

## 3. What is not a transcription of the ruling, and why

Everything in this section is declared for the reviewers rather than assumed.

### 3.1 The claim is the **first** statement of `complete()`

The ruling lists it first; this implementation takes that literally, and it
buys a property worth naming. A refused completion writes nothing at all — no
account, no external identity, no membership projection, no token grant. That is
asserted, not merely intended:
`test_a_direct_completion_without_a_claimable_transaction_is_refused` checks
`platform_accounts` is empty on every one of its three parameters, and
`test_two_concurrent_completions_produce_one_session_and_one_refusal` asserts
exactly one account after the race.

### 3.2 The membership refusal still comes after the claim

ADR 0004's non-member rejection runs after the claim and rolls it back with
everything else, leaving the transaction consumed-and-unclaimed — the same
terminal state as process death, and equally unreplayable. TC-AUTH-08 is
unchanged and still passes.

### 3.3 The unique index is scoped to non-rotated sessions — **the one declared reading**

**The problem.** Transcribed literally, two ruled clauses cannot both hold while
N-08 privilege rotation exists:

- the check constraint requires `oauth_transaction_id` for **every**
  `discord_oauth` session; and
- a table-wide `UNIQUE (oauth_transaction_id)` permits each transaction id to
  appear on **one** session row.

A rotation creates a *new* session row for the same login. Under the literal
pair it would need the transaction id and could not have it. Rotating a Discord
OAuth session would become impossible, and N-08 would silently stop protecting
the platform's main authentication method — an outcome the ruling plainly did not
intend, and one that the handover forbids ("do not weaken or redesign …
expiry/revocation/rotation").

**What was chosen.** The check constraint is transcribed **exactly**. The unique
index carries the predicate `WHERE rotated_from_session_id IS NULL`, which scopes
uniqueness to exactly the set a *completion* can create.

**Why this reading and not the other one.** The alternative was to relax the
check constraint instead — permitting a null binding on rotated rows — and keep
the table-wide `UNIQUE`. That was rejected: it would allow a `discord_oauth`
session row that names no transaction, which is precisely the forbidden state
SM-01 exists to make impossible, and it would move the guarantee for rotated
sessions back onto a chain of foreign keys rather than a single constraint. Both
of the ruling's stated purposes survive the scoping intact:

| The ruling's stated purpose | Preserved? |
|---|---|
| "the `CHECK` refuses an OAuth session with no transaction" | **Yes, in full.** The constraint is unmodified and applies to every row, rotated or not |
| "the `UNIQUE` refuses a second session for the same transaction" | **Yes, for the thing it protects.** A second *completion* produces a non-rotated row and is refused, by the claim and again by the index |

What the predicate additionally permits is a rotation chain for one login, which
is the thing N-08 exists to produce. It is evidenced by
`test_rotation_carries_the_binding_forward_without_a_second_claim`, which asserts
the rotated row names the same transaction, names its predecessor, and that the
transaction still carries exactly one claim.

**Residual risk RR-15**, newly recorded in the threat model: two concurrent
rotations of one session could in principle produce two live sessions sharing a
transaction id. That is **pre-existing and not introduced here** — N-08 rotation
could already produce two live sessions from one login — and no production route
calls `rotate_if_privileges_changed` in this build (§5.2). The unscoped `UNIQUE`
would not have fixed it either; it would have removed rotation. The P3.2 package
that wires rotation into the request path must serialize it.

**If the Acceptance Authority prefers the other reading**, the change is one
predicate in 0009, one in `tables.py`, one relaxed check constraint and one test.
I did not take that decision unilaterally in either direction, which is why it is
in §1's summary.

### 3.4 `purge_expired` now skips referenced rows

Not ruled, and necessary. `sessions.oauth_transaction_id` is `RESTRICT`, and a
session outlives its transaction **by design** — N-07's twelve hours against
N-04's ten minutes — so N-04's reaper meets referenced rows in ordinary
operation, not only in a contrived case. Left alone, the first such row would
abort the whole cleanup.

`OAuthTransactionRepository.purge_expired` therefore excludes referenced rows by
predicate. `RESTRICT` remains the backstop for any deletion written without it.
`test_the_expiry_reaper_skips_a_transaction_a_session_still_names` asserts both
halves: the unreferenced expired row beside it *is* deleted, so the predicate is a
skip and not a no-op, and a raw `DELETE` of the referenced row is refused by the
database.

**No production caller exists yet** — `purge_expired` has no call site in
`application/`, `adapters/` or `tools/` in this build — so this changes no live
behaviour. It removes a landmine from whoever wires the cleanup job in a later
package.

### 3.5 A bound `expires_at` predicate was considered and rejected

A consumed-but-unclaimed transaction stays claimable until N-04's reaper removes
it. Adding `AND expires_at > :now` to the claim would close that, and would also
refuse a legitimate login whose provider round trip crossed the ten-minute
boundary. The window is unreachable through any route — the callback's only path
to `complete()` runs through a consumption that now matches zero rows — so the
availability cost was judged the larger harm. Recorded as **RR-05a** for the
security pass rather than decided silently.

---

## 4. OD-45: what was and was not done

Nothing was implemented for finding 3, and nothing needed to be.

| Claim | Evidence |
|---|---|
| **No P3.2 route was added** | `adapters/web/app.py`'s `DEFERRED_ROUTES` is unchanged, and `tests/web/test_structural_guards.py::test_a_route_owned_by_a_later_package_is_absent_from_this_build` passes in the run reported in §7. R-33, R-34 and R-38 do not exist in this build |
| **No test-only substitute route was added** | The new test module registers no route and constructs no second application factory. It drives the real `create_app` client, the real services, and raw SQL |
| **No HTTP evidence was waived** | The traceability rows for TC-BG-05b/c/e are unchanged from Peter's ruling: their direct-HTTP portions are marked mandatory P3.G2 evidence. The delivery plan's P3.G1 section repeats that this gate does not accept the break-glass HTTP boundary |
| **No early P3.2 work** | The only files touched outside documentation are the seven in §2.2 and four test files |

The traceability contract's header gained a dated amendment note recording the
addition of TC-AUTH-13/14 and pointing at the OD-45 allocation. That note
**describes** the allocation Peter ruled; it does not restate it as a waiver.

---

## 5. The mechanical enumerations

### 5.1 Every terminal exit of R-04 `GET /auth/discord/callback`

Read from `adapters/web/app.py` after the change, and cross-checked by walking
the function's AST for `return` and `raise` nodes. The route has **nine** `return`
statements in its own body (the two others the AST reports are inside the
`consume` and `complete` closures, which return into the route rather than out of
it) and **no** `raise`. Those nine cover the fifteen logical exits below, which
are the same fifteen as the previous remediation: **no terminal exit was added,
removed or reordered.**

| # | Exit | Caller sees | Refusal audit | Reason recorded |
|---|---|---|---|---|
| E1 | Callback rate limit spent (N-18) | `303` `failure=rate_limited`, `Retry-After` | one | `rate_limited` |
| E2 | No transaction cookie | `303` `failure=transaction_unknown` | one | `callback_parameters_missing` |
| E3 | No `state` | same | one | `callback_parameters_missing` |
| E4 | No `code` | same | one | `callback_parameters_missing` |
| E5 | Transaction cookie is not a UUID | same | one | `transaction_cookie_malformed` |
| E6 | Consumption matched zero rows | `303` `failure=transaction_unknown` | one | `transaction_not_live_or_state_mismatch` |
| E7 | Verifier ciphertext failed its AAD binding | `303` `failure=state_mismatch` | one | `verifier_binding_failed` |
| E8 | `ProviderUnavailable` at `exchange()` | `303` `failure=provider_error` | one | `provider_unavailable` |
| E9 | `ProviderUnavailable` at `verify()` | same | one | `provider_unavailable` |
| E10 | `ProviderRefused` at `exchange()` | same | one | `provider_refused` |
| E11 | `ProviderRefused` at `verify()` | same | one | `provider_refused` |
| E12 | Not a guild member | `403` VM-02 | one | `not_a_guild_member` |
| **E13a** | **Completion claim matched zero rows (new)** | `303` `failure=transaction_unknown` | one | `completion_not_claimable` |
| E13b | Any other `AuthenticationFailure` from `complete()` | `303` with its code | one | as described by the service |
| E14 | **Success** | `303` to the return path, session cookie set | — | `auth.login.succeeded` |
| E15 | Unhandled exception | `500` VM-20, correlation id only | none — **deliberately** | a programmer defect must stay visible; no blanket `except` was added |

**E13a introduces no new branch.** It arrives at the existing
`except AuthenticationFailure` around `complete()`, which calls
`recorder.record_failure(failure)` — and `OAuthRefusalRecorder.record_failure` is
a no-op after the first write, so an attempt cannot produce two refusal events.
`completion_not_claimable` is deliberately absent from `ROUTE_RECORDED_REASONS`,
because a reason recorded in both places is exactly the double-audit TC-AUTH-11
forbids. Evidenced by
`test_a_direct_completion_without_a_claimable_transaction_is_refused`, which
asserts the described payload, and by the unchanged
`tests/web/test_oauth_refusal_audit.py` (all 11 terminal exits, still passing).

### 5.2 Every production path capable of creating a web session

Enumerated mechanically:

```text
INSERT INTO sessions            → adapters/web/repositories.py:257   (exactly one)
  caller                        → application/web/sessions.py:111    (SessionService.begin, exactly one)
    begin() production callers  → application/web/oauth.py:395       (S1)
                                  application/web/breakglass.py:291  (S2)
                                  application/web/breakglass.py:351  (S3)
                                  application/web/sessions.py:188    (S4)
```

| # | Path | Auth method | Binding | Does it need an OAuth transaction? |
|---|---|---|---|---|
| S1 | `OAuthLoginService.complete()` (R-04) | `discord_oauth` | The id it claimed, in the same transaction | **Yes.** The check constraint requires it and the claim supplies it |
| S2 | `BreakGlassService.complete_assertion()` (R-08) | `webauthn` | `None` | **No**, and the constraint *refuses* one |
| S3 | `BreakGlassService.redeem_recovery_grant()` (R-09) | `recovery_grant` | `None` | **No**, and the constraint refuses one |
| S4 | `SessionService.rotate_if_privileges_changed()` | inherits the record's | Carried forward from the rotated row | **No second claim.** It cannot create a *first* session: it requires a resolved live record |

S4 has **no production caller in this build** — `grep -rn
"rotate_if_privileges_changed" application/ adapters/ tools/` finds only its
definition — which is why RR-15 is bounded. The four `tools/` operator commands
issue and invalidate grants, revoke sessions and enrol credentials; **none of
them creates a session**.

Both non-OAuth paths are asserted unchanged by
`test_break_glass_sessions_are_created_exactly_as_before`, and the whole
break-glass suite (`test_break_glass_login.py`, `test_break_glass_escalation.py`)
passes unmodified.

---

## 6. Schema, transaction boundary and failure semantics

### 6.1 The objects 0009 creates

| Object | Definition | What it refuses |
|---|---|---|
| `oauth_transactions.completion_claimed_at` | `TIMESTAMPTZ NULL` | — (the claim's target) |
| `ck_oauth_transactions_completion_requires_consumption` | `completion_claimed_at IS NULL OR consumed_at IS NOT NULL` | A completion for a transaction whose verifier was never recovered |
| `sessions.oauth_transaction_id` | `UUID NULL` | — |
| `fk_sessions_oauth_transaction_id_oauth_transactions` | `REFERENCES oauth_transactions(id) ON DELETE RESTRICT` | A binding to a row that does not exist; and deleting a transaction a session still names |
| `uq_sessions_oauth_transaction_id` | `UNIQUE (oauth_transaction_id) WHERE rotated_from_session_id IS NULL` | A second completion-created session for one transaction |
| `ck_sessions_oauth_transaction_binding` | `(auth_method = 'discord_oauth') = (oauth_transaction_id IS NOT NULL)` | An unbound Discord OAuth session; a bound break-glass session |

Every one of these is exercised with the application bypassed entirely — raw
`INSERT`/`UPDATE`/`DELETE` — in TC-AUTH-13e.

### 6.2 The transaction boundary

```text
  R-04 (async)                                     database transactions
  ─────────────────────────────────────────────    ─────────────────────
  rate limit                                       T0  (own)
  cookie / state / code validation                 —   (no I/O)
  services.oauth.consume(...)                      T1  (own)  ← verifier recovered and erased
  provider.exchange()                              ── NONE ── ← network
  provider.verify()                                ── NONE ── ← network
  services.oauth.complete(...)                     T2  (own)
      1. claim_completion            ← refusal point
      2. account + external identity
      3. membership projection
      4. encrypted token grant
      5. session INSERT carrying oauth_transaction_id
      6. auth.login.succeeded audit
  refusal audit, if any                            T3  (own, after T1/T2 rolled back)
```

No database transaction is open across `exchange()` or `verify()`. T2 contains
no provider I/O of any kind.

### 6.3 Failure and restart semantics

| Event | Resulting durable state |
|---|---|
| Provider unavailable or refusing, at either call | Transaction consumed, verifier gone, **unclaimed**. No session, no token grant, no success audit. One refusal audit |
| Any write inside T2 fails (6 tested) | T2 rolls back entirely. The claim is **released**; no session, no token grant, no account. The exception reaches the safe-error handler |
| The commit itself fails / the worker dies before `COMMIT` | Identical to the row above. `complete()` returning is not a login; the commit is |
| Process death between T1 and T2 | Transaction consumed-and-unclaimed, no session. The retried callback is refused at the **consumption**, not at the claim. The row is reaped 24 h after expiry |
| Callback replayed or duplicated | Refused at the consumption. One session, one success audit, one claim, after two deliveries |
| A second `complete()` after a successful login | Refused at the **claim** — the second serialization point, which is the one that survives the provider round trip |
| Two concurrent completions | One session, one refusal, one account. The loser blocks on the row lock, re-evaluates and matches zero rows |
| Audit write fails | Shares T2; rolls back with it. A login that cannot be recorded does not happen |

Restart semantics are automated as far as they can be without killing an
uncontrolled process: `test_the_process_death_seam_leaves_no_session_and_no_
replayable_transaction` commits the consumption, never performs the completion,
asserts the durable state a killed worker leaves, and then drives the retried
callback through the real route. **Killing a real worker mid-transaction is not
automated and is not claimed.**

---

## 7. Verification

Every command below was run on this host against the guarded disposable database
`freedom_test`, proved through the existing static target guard
(`assert_disposable_target`, `UNIX_SOCKET_ONLY`) and the live Unix-socket
identity guard (`verify_connected_unix_socket_target`). Neither guard was
weakened, mocked or bypassed. **No test was skipped**; a skipped PostgreSQL test
is not database evidence, and there are none in these runs.

The two suites were run **serially**. They share one database, and an earlier
attempt to overlap them produced spurious failures that were an artefact of the
overlap; the numbers below are from clean serial runs.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' /opt/discord-bots/venv-web/bin/python -m pytest -q tests/web` | **299 passed**, 14 warnings, 0 failed, 0 skipped (baseline before this work: 269) |
| `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' /opt/discord-bots/venv/bin/python -m pytest -q` | **2257 passed**, 1 warning, 0 failed, 0 skipped (baseline before this work: 2252) |
| `/opt/discord-bots/venv/bin/alembic check` | `No new upgrade operations detected.` One pre-existing `SAWarning` from `migrations/env.py:133` about a `dialect_options` argument, unrelated to this change |
| `/opt/discord-bots/venv-web/bin/python -m compileall -q application adapters domain tools migrations tests` | Clean |
| `/opt/discord-bots/venv/bin/python -m compileall -q application adapters domain tools migrations tests` | Clean |
| `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | Every file `OK`; **zero** non-`OK` lines. The frozen visual assets are untouched |
| `git diff --check` | Clean |

Targeted runs, run first as the handover requires:

| Command | Result |
|---|---|
| `pytest -q tests/web/test_oauth_completion_binding.py` | 30 passed |
| `pytest -q tests/test_oauth_completion_binding_migration.py` | 4 passed |
| `pytest -q tests/test_database_postgresql.py -k migration` | 2 passed (`test_migrations_apply_to_empty_postgresql_and_downgrade`, `test_migration_matches_table_metadata`) |
| `pytest -q tests/web/test_sessions.py tests/web/test_security_controls.py` | 46 passed |

The guarded upgrade → downgrade → re-upgrade rehearsal through 0009 is
`tests/test_oauth_completion_binding_migration.py`, which drives Alembic through
the same subprocess helper the rest of the suite uses, so both guards apply to
every step. Live runtime-grant tests (`tests/test_runtime_grants.py`,
`tests/test_runtime_grants_live.py`) are part of the 2257 and pass unchanged;
0009 needs no grant change (§8).

### 7.1 Warnings

All 14 portal warnings are the **same** pre-existing `DeprecationWarning` from
`httpx` about per-request `cookies=` — one per test that drives the callback with
a cookie argument:

```text
tests/web/test_oauth_completion_binding.py: 9 warnings
tests/web/test_oauth_flow.py:               4 warnings
tests/web/test_sessions.py:                 1 warning
```

The nine from the new module use the same idiom as the four that were already
there. The single bot-suite warning is the pre-existing
`DeprecationWarning: import audioop`. **No new warning class was introduced**,
and the count rose only by the number of new tests that set a cookie.

### 7.2 Formatter, linter and type checker

**None is configured in this repository**, and one was not introduced. There is
no `pyproject.toml`, `setup.cfg`, `.ruff.toml`, `.flake8` or `mypy.ini`;
`requirements-dev.txt` and `requirements-web-dev.txt` contain `pytest`,
`pytest-asyncio` and `beautifulsoup4` and nothing else; neither virtualenv
contains `ruff`, `black`, `flake8`, `mypy` or `pylint`. Adding a toolchain during
a security remediation would be an unrelated change to every file it touched.
This is reported as an accurate absence, not as a passing check.

### 7.3 Evidence deliberately not produced

| Evidence | Why |
|---|---|
| Direct-HTTP portions of TC-BG-05b/c/e | Allocated to P3.G2 by OD-45. R-33/R-34/R-38 do not exist. **Not waived** |
| Staging-class checks (TC-OPS-01…05, TC-PERF-01…03, TC-LIM-02) | Staging does not exist (RAID I-06). Unchanged by this work |
| Browser, real-device and assistive-technology evidence | No browser or device was driven. Nothing here renders a new view |
| Live Discord, production database, Foundry, Google Sheet | Never contacted. The provider is a synthetic double; the guild snowflake is synthetic and outside Discord's issued range |
| Killing a real worker process mid-transaction | Not automated; §6.3 says exactly how far the seam evidence goes |
| Deployment of any kind | Nothing was deployed, no Caddy or systemd change was made, and no OAuth provider registration was touched |

---

## 8. Mutations run and reverted

Each mutation was applied to the working tree, the full portal suite was run, the
failures recorded, and the mutation reverted from a byte-identical backup. `grep
-rn "MUTATION" application/ adapters/ migrations/ tests/` afterwards returns
nothing from this work, and the final verification in §7 was run after every
revert.

| # | Mutation | Suite result | Killed by |
|---|---|---|---|
| **M1** | Remove the completion claim: `if not self._transactions.claim_completion(...)` → `if False:` in `complete()` | **9 failed**, 290 passed | `test_one_consumed_transaction_produces_one_bound_session_and_one_success_audit`; `test_a_direct_completion_without_a_claimable_transaction_is_refused[unknown]`, `[unconsumed]`, `[already_claimed]`; `test_a_completion_naming_a_different_transaction_than_the_one_consumed_is_refused`; `test_a_replayed_callback_creates_no_second_session_or_success_audit`; `test_a_second_completion_after_a_successful_login_is_refused`; `test_two_concurrent_completions_produce_one_session_and_one_refusal`; `test_a_failure_at_any_step_rolls_the_whole_completion_back[_transactions-claim_completion]` |
| **M2** | Omit `oauth_transaction_id=transaction_id` from Discord OAuth session creation | **9 failed**, 290 passed | `test_one_consumed_transaction_produces_one_bound_session_and_one_success_audit`; `test_a_replayed_callback_creates_no_second_session_or_success_audit`; `test_a_second_completion_after_a_successful_login_is_refused`; `test_two_concurrent_completions_produce_one_session_and_one_refusal`; `test_a_failure_at_any_step_rolls_the_whole_completion_back[_audit-record]`; `test_a_commit_failure_after_a_complete_call_leaves_no_session_and_no_claim`; `test_oauth_flow.py::test_a_member_login_creates_one_session_and_one_audit_event`; `test_oauth_refusal_audit.py::test_the_successful_path_writes_no_refusal_event`; `test_sessions.py::test_the_session_cookie_attributes_are_exactly_the_policy` |
| **M3a** | Remove the unique binding: drop `uq_sessions_oauth_transaction_id` from migration 0009 **and** from the metadata | **1 failed**, 298 passed | `test_the_database_refuses_a_second_completion_session_for_one_transaction` |
| **M3b** | Otherwise allow a second completion: drop `AND completion_claimed_at IS NULL` from the claim statement | **4 failed**, 295 passed | `test_a_direct_completion_without_a_claimable_transaction_is_refused[already_claimed]`; `test_a_second_completion_after_a_successful_login_is_refused`; `test_two_concurrent_claims_produce_one_winner_and_one_refusal`; `test_two_concurrent_completions_produce_one_session_and_one_refusal` |

**Reading M3a honestly.** One test — the direct-database one — is what stands
between this build and a silently missing unique index. That is the correct
number rather than a thin one: the index is *defence in depth*. The application
path is already refused by M3b's claim, so a mutation that removes only the index
should be caught only by the test that bypasses the application. A larger failure
count there would mean some other test was depending on the index to do the
claim's job.

**One disclosure about M3a.** Because that mutation removed the index from the
`upgrade()` and the `drop_index` from `downgrade()`, the disposable database was
left holding a schema whose `downgrade base` then failed on the restored
revision. It was repaired with a single `CREATE UNIQUE INDEX IF NOT EXISTS`
matching the revision exactly, and every subsequent run — including the
`downgrade base` / `upgrade head` the fixtures perform, `alembic check`, and the
0009 rehearsal — passes from that state. The disposable database is the only
database that was touched.

---

## 9. Migration 0009: upgrade, downgrade, re-upgrade and cost

The rehearsal is executable, in
`tests/test_oauth_completion_binding_migration.py`.

1. **`0008 → 0009`** adds both columns, the foreign key, the unique index and
   both check constraints. A bound Discord OAuth session is insertable.
2. **`0009 → 0008`** drops them. **Every session row survives** and keeps
   working: the table returns to exactly its pre-0009 shape, in which a
   `discord_oauth` session carries no transaction reference. What is destroyed is
   the record of which transaction produced which session, and every
   `completion_claimed_at`. Nothing reconstructs them.
3. **`0008 → 0009` again refuses**, naming the count and the remedy, and leaves
   the database at 0008 rather than half-applying:

   ```text
   Revision 0009 refused: 1 Discord OAuth session row(s) predate the completion
   binding and cannot be bound … End those logins and re-run:
   DELETE FROM sessions WHERE auth_method = 'discord_oauth';
   ```

4. **After the remedy** the re-upgrade succeeds, with the binding column back and
   empty. The test asserts each of these, including that the refused revision
   deleted nothing on its way out.

**This was found by running it, not by reasoning about it.** The first draft of
this document claimed the re-upgrade would succeed and leave an unmaintainable
row; the rehearsal failed, because `ADD CONSTRAINT` validates existing rows. The
revision now counts and refuses first, in the style revision 0007 already
established, so an operator meets a cause and a remedy rather than a constraint
name.

**Revoking is not sufficient**, and the documentation says so explicitly: the
constraint is evaluated over every row, and a revoked row is still a row.
`tools/session_revoke.py` does not prepare a database for this revision.

**Rollback cost, stated plainly:** a downgrade past 0009 costs every Discord
OAuth login in progress and nothing else. No history is lost — a login is
recorded by the append-only `auth.login.succeeded` audit event, not by the
session row. `docs/operations/web-portal.md` §3.5 carries the operator sequence.

**Deployment and configuration impact:** none beyond running the migration. No
environment variable was added, changed or removed; `.env.example` is untouched
by this work. **Runtime grants are unchanged**: 0009 adds columns to `sessions`
and `oauth_transactions`, both already in the `SELECT, INSERT, UPDATE` band, and
creates no table. `infra/postgresql/runtime-grants.sql.tmpl` was not edited.

---

## 10. Every changed file

### 10.1 Production code and migrations

| File | New? |
|---|---|
| `migrations/versions/0009_oauth_completion_binding.py` | **new** |
| `adapters/database/tables.py` | modified |
| `adapters/web/repositories.py` | modified |
| `adapters/web/app.py` | modified |
| `application/web/oauth.py` | modified |
| `application/web/sessions.py` | modified |
| `application/web/refusals.py` | modified |

### 10.2 Tests

| File | New? | Why it changed |
|---|---|---|
| `tests/web/test_oauth_completion_binding.py` | **new** | TC-AUTH-13, 30 tests |
| `tests/test_oauth_completion_binding_migration.py` | **new** | TC-AUTH-14, 4 tests |
| `tests/web/conftest.py` | modified | `seed_oauth_transaction` helper; `sessions` moved **before** `oauth_transactions` in the cleanup order, because the binding FK is `RESTRICT` and the cleanup obeys the constraint rather than weakening it to `CASCADE` |
| `tests/web/test_sessions.py` | modified | 10 `begin()` call sites now supply the binding a `discord_oauth` session requires |
| `tests/web/test_security_controls.py` | modified | 1 `begin()` call site, same reason |

No existing assertion was removed or weakened. The changes are the argument the
new constraint requires, added explicitly at each site rather than hidden in a
helper, so a reviewer sees the binding where the session is created.

### 10.3 Contracts and records — all amended by dated addition

| File | Amendment |
|---|---|
| `docs/contracts/phase-3-logical-schema.md` | §9.1's binding row, the scoped unique index with its rationale, the rollback consequence and the retention interaction; §9.2's purge behaviour |
| `docs/contracts/phase-3-state-machines.md` | SM-01's forbidden row states the scoping; SM-02's rotation row states that the binding is carried forward |
| `docs/contracts/phase-3-test-traceability.md` | TC-AUTH-13 and TC-AUTH-14 added to §2; §18 coverage row added; dated header note |
| `docs/contracts/phase-3-threat-model.md` | T-05a's residual is now specific; RR-05a and RR-15 added |
| `docs/operations/web-portal.md` | 0009 in the revision table; new §3.5 on the precondition, the remedy and the rollback cost; the grants statement |
| `docs/review/phase-3-delivery-plan.md` | P3.G1 now names the OD-44 evidence and revisions 0006–**0009** |
| `docs/discovery/open-decisions.md` | OD-44 records the implementation and the declared reading |
| `docs/project-management/change-log.md` | **C-P3.1-E**, a new dated entry |
| `docs/project-management/{status,raid-register,decision-register}.md` | I-07 and OD-44 move from "to be implemented" to "implemented, re-review outstanding" |

Nothing was deleted from any historical submission.

---

## 11. Residual risk

| # | Risk | Severity | Disposition |
|---|---|---|---|
| RR-05a | A consumed-but-unclaimed transaction stays claimable by an **in-process** caller until N-04's reaper removes it | Low | No route can reach it. Bounding by `expires_at` was rejected (§3.5). Any P3.2 package adding a second completion caller must be reviewed against it |
| RR-15 | The scoped unique index would permit two concurrent rotations of one session to share a transaction id | Low | Pre-existing, not introduced here; no production caller for rotation in this build. P3.2 must serialize rotation |
| — | The declared reading in §3.3 | — | **Asked, not assumed.** Confirmation requested with the reviews |

Unchanged and still open from the earlier submissions: I-06 (no staging), the
three declared P3.1 deviations (nullable `role_capability_mappings.created_by_
account_id`, the added `WEB_SECRET_KEY_CLIENT_DIGEST`, the added
`webauthn_challenges` table), and the OD-45 P3.G2 HTTP blocker.

---

## 12. Dirty-worktree account

The working tree was already dirty when this task began, and this remediation is
a small part of it. Separated so a reviewer can tell the three apart:

| Origin | Paths |
|---|---|
| **This remediation (2026-08-14)** | The 7 production files in §10.1, the 5 test files in §10.2, and the documentation in §10.3 — plus this document |
| **Peter's decision-record edits (2026-08-14, before this task)** | The two decision notes; the OD-44/OD-45 entries in `open-decisions.md`, `decision-register.md`, `raid-register.md`, `status.md` and change-log `C-P3.1-D`; the already-amended SM-01 rows, schema §9.1/§9.2 columns and threat-model T-05a. **This remediation added to those; it rewrote none of them** |
| **Pre-existing P3.0/P3.1 work, untouched here** | `.env.example`, `.gitignore`, `adapters/database/repositories.py`, `application/audit.py`, `docs/adr/README.md` and ADR 0010, `infra/postgresql/runtime-grants.sql.tmpl`, `pytest.ini`, `requirements*`, migrations 0006–0008, the rest of `adapters/web/`, `application/web/`, `tests/web/`, `tools/`, `docs/contracts/`, `docs/operations/web-portal.md`'s existing sections, and every earlier `docs/review/` document |

`docs/review/Handover information` shows as modified; that predates this task and
was not edited by it. Every unrelated change was preserved. **No commit was
made**, and none was authorized.

---

## 13. What is requested

1. **Codex independent implementation re-review** of finding 1's remediation:
   migration 0009, the claim, the bound session creation, the route change, the
   repository changes and the tests.
2. **A separately reported security-focused re-review**, with particular
   attention to §3.3's declared reading, §3.4's purge change, and RR-05a.
3. **The Acceptance Authority's confirmation** of the scoped unique index, or an
   instruction to take the other reading.

P3.G1 is **not** marked ready and is **not** closed. P3.2 and P3.3 have not
started. No Gemini production integration, deployment, Caddy change, OAuth
provider registration, production or staging database access, live Discord
access, Foundry mutation or Google Sheet mutation occurred, and nothing was
committed.

---

`P3.1 OD-44 remediation submitted for Codex independent and distinct security re-review; P3.G1 remains open and P3.2 has not started.`
