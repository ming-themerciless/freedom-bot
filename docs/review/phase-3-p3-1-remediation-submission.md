# Phase 3 P3.1 remediation submission — after Codex independent and security review

**Prepared:** 2026-08-14 · **Package:** P3.1 remediation · **Owner:** Claude
(Working Technical Lead) · **Status:** **Submitted for review. Not accepted.
P3.G1 is open. Peter ruled both decision requests on 2026-08-14; the OD-44
completion-binding implementation remains outstanding.**

**Authority:** `docs/review/Handover information` — Codex's independent
implementation review and distinct security-focused review of P3.1.

**Predecessor:** [`phase-3-p3-1-submission.md`](phase-3-p3-1-submission.md),
whose superseded claims are annotated in place in its new §0. Nothing in that
document was deleted.

---

## 1. Outcome in one table

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | A session is not durably bound to a consumed OAuth transaction | Blocking | **Not remediated. Blocked on a maintainer decision.** The finding is a material contract contradiction; the required decision note is [`phase-3-p3-1-sm-01-completion-binding-decision.md`](phase-3-p3-1-sm-01-completion-binding-decision.md). No code was changed for it |
| 2 | OAuth refusal auditing is incomplete | Blocking | **Remediated.** One refusal-recording boundary, all eleven terminal exits, 72 new tests, three mutations run and reverted |
| 3 | Required break-glass HTTP evidence conflicts with package order | Blocking | **Corrected as far as authorized. Blocked on a maintainer decision** for the contract change; note at [`phase-3-p3-1-tc-bg-05-http-evidence-decision.md`](phase-3-p3-1-tc-bg-05-http-evidence-decision.md). The overstated claim is corrected now |
| 4 | Migration reporting is inaccurate | Important | **Remediated.** The false sentence is superseded and replaced with the exact facts, in the submission and in the operations document. Migration 0006 was **not** altered |

**P3.G1 is not ready and is not closed. P3.2 has not started.**

---

## 2. Finding 1 — not remediated, and why that is the correct outcome

The handover instructed: *"If Peter has not already approved a contract-compatible
option in repository context, stop implementation of this finding after producing
the decision note and report the blocker."*

I searched the repository record before starting: `docs/discovery/open-decisions.md`,
`docs/project-management/decision-register.md` (OD-43 closes the ADR 0010 design,
not this), `docs/project-management/status.md`, `docs/project-management/raid-register.md`
and `docs/project-management/change-log.md` entry C-P3.1. **No approval of an
SM-01 mechanism change exists.**

The decision note therefore states the contradiction precisely, separates the
security outcome from the prescribed mechanism, presents four bounded options
with their failure and restart semantics, recommends one, and lists every
contract, ADR, schema, migration, test and operational passage that would need
amendment. It is not implemented.

**Summary of the contradiction:** SM-01 requires session creation to run *in the
same transaction as the consumption*. Schema §9.2.1 makes verifier recovery and
erasure one statement, and PKCE requires that verifier to be presented to Discord
**before** the identity a session attests is known. So the prescribed transaction
necessarily spans a provider network round trip — which the accepted
no-transaction-across-provider-I/O invariant forbids. No ordering of the current
mechanism satisfies both.

**Recommended option:** a durable one-way completion binding — an atomic
completion claim on the consumed transaction plus `sessions.oauth_transaction_id`
carrying a `UNIQUE` and a `CHECK`, so the forbidden state is refused by the
database rather than by route ordering. It preserves the invariant, needs one new
migration, and edits no already-submitted migration.

**Residual exposure until it is decided:** unchanged from what Codex found.
`OAuthLoginService.complete()` receives no transaction id and cannot prove from
durable state that a completion corresponds to a transaction. Route ordering is
the only thing preventing the forbidden state today. There is one production
caller and it orders the steps correctly (§3.2), so the defect is currently
unreachable through HTTP — but it is prevented by control flow, not by structure,
and that is exactly the finding.

---

## 3. The mechanical enumerations

### 3.1 Every terminal exit of R-04 `GET /auth/discord/callback`

Read directly from `adapters/web/app.py` after remediation. "Audit before" is the
state Codex reviewed.

| # | Exit | Caller sees | Audit **before** | Audit **now** | Reason recorded |
|---|---|---|---|---|---|
| E1 | Callback rate limit spent (N-18) | `303` `failure=rate_limited`, `Retry-After` | **none** | one | `rate_limited` |
| E2 | No transaction cookie | `303` `failure=transaction_unknown` | **none** | one | `callback_parameters_missing` |
| E3 | No `state` | same | **none** | one | `callback_parameters_missing` |
| E4 | No `code` | same | **none** | one | `callback_parameters_missing` |
| E5 | Transaction cookie is not a UUID | same | **none** | one | `transaction_cookie_malformed` |
| E6 | Consumption matched zero rows (unknown, expired, replayed, raced, `state` mismatch) | `303` `failure=transaction_unknown` | one | one | `transaction_not_live_or_state_mismatch` |
| E7 | Verifier ciphertext failed its AAD binding | `303` `failure=state_mismatch` | one | one | `verifier_binding_failed` |
| E8 | `ProviderUnavailable` at `exchange()` | `303` `failure=provider_error` | **none** | one | `provider_unavailable` |
| E9 | `ProviderUnavailable` at `verify()` | same | **none** | one | `provider_unavailable` |
| E10 | `ProviderRefused` at `exchange()` | same | **none** | one | `provider_refused` |
| E11 | `ProviderRefused` at `verify()` | same | **none** | one | `provider_refused` |
| E12 | Not a guild member | `403` VM-02 | one | one | `not_a_guild_member` |
| E13 | Any other `AuthenticationFailure` from `complete()` | `303` with its code | one | one | as described by the service |
| E14 | **Success** | `303` to the return path, session cookie set | `auth.login.succeeded` | unchanged | — |
| E15 | Unhandled exception | `500` VM-20, correlation id only | none | none — **deliberately** | a programmer defect must stay visible; no blanket `except` was added |

Five exits — E1, E2/E3/E4, E5, E8/E9, E10/E11 — wrote nothing. All now record
exactly one event.

Three refusals reach the browser before the route function runs, from middleware
registered in `create_app`. They are not OAuth callback refusals and are listed
for completeness: `HostGuard` (unknown `Host`), `KillSwitch` (operator kill file
present) and `BodyBound` (request body over N-27). None can create a session.

### 3.2 Every production path capable of creating a web session

`SessionRepository.create` is the only statement that inserts into `sessions`, and
`SessionService.begin()` is its only caller. `begin()` has four callers:

| # | Path | Entry point | Authenticates through |
|---|---|---|---|
| S1 | `OAuthLoginService.complete()` | R-04 | Discord OAuth: consumed transaction → provider exchange → provider verify → guild membership |
| S2 | `BreakGlassService.complete_assertion()` | R-08 | A WebAuthn assertion against a pre-enrolled credential (SM-03) |
| S3 | `BreakGlassService.redeem_recovery_grant()` | R-09 | A host-issued, hashed, single-use, 10-minute grant (N-14). **No route can issue one** |
| S4 | `SessionService.rotate_if_privileges_changed()` | any authenticated request | An **existing** valid session row; it cannot create a first session |

S1 is the path finding 1 concerns. S2 and S3 have their own durable single-use
mechanisms (challenge consumption; the conditional grant update) and are unaffected
by that finding. S4 cannot begin a session from an unauthenticated request.

The `tools/` operator commands issue and invalidate grants, revoke sessions and
enrol credentials. **None of them creates a session**; `session_revoke.py` only
revokes.

---

## 4. Finding 2 — remediated

### 4.1 The boundary

`application/web/refusals.py` is new. It holds:

- `LoginRefusalReason` — the closed, non-secret vocabulary in §3.1's last column;
- `OAuthRefusalRecorder` — constructed once per callback attempt, records **at
  most one** event for that attempt, in its **own** transaction.

`record()` is a no-op after the first write, so "exactly one" is a property of the
object rather than a rule a future editor must remember. `record_failure()` writes
the event a service already described in its `FailureAudit`, and marks the attempt
recorded — which is what prevents the double audit on E6/E7/E12/E13.

The route was changed to call the recorder on all eleven refusing exits.
`adapters/web/app.py` gained one helper, `_record_refusal`, which crosses the
threadpool seam because the write is PostgreSQL work.

### 4.2 The decisions the handover asked to be made explicitly

**A rate-limited callback is one authentication-attempt audit, not a rate-limit
audit and not both.** N-18's refusal is a terminal outcome of an authentication
attempt, so it is `auth.login.refused` with reason `rate_limited`. Two events for
one refused callback would break TC-AUTH-11 in the direction hardest to notice: a
reviewer counting refusals would double every throttled attempt. Documented in the
module docstring and asserted by the parametrization.

**Entity naming.** A refusal names an `oauth_transaction` only where a *validated*
identifier exists — a cookie value that parsed as a UUID (E6–E11). Otherwise it
names the stable non-sensitive category `oauth_callback` / `unbound` (E1–E5). The
malformed cookie is attacker input and is **never** echoed. E12 names the verified
`external_identity` instead, which is a more useful and equally non-secret fact.

**What may appear in a payload:** a reason, and — where validated — a transaction
id. Never the authorization code, `state`, PKCE verifier, provider token, cookie
value, raw provider response, client address, exception text or credential
material.

**A failed refusal audit is not swallowed.** It propagates to the safe-error
handler and the caller sees VM-20 with a correlation id. No session exists on any
refusal path, so this cannot convert a refusal into a login — it converts a
refusal into a safe error, the same fail-closed direction SM-01 requires of the
success path. No blanket `except Exception` was added anywhere.

### 4.3 Malformed provider data is now a classified refusal, not a `500`

`adapters/web/discord_provider.py` previously called `response.json()` unguarded
and coerced `expires_in` with a bare `int()`. A provider answering `200` with an
HTML proxy error page, a JSON array, or `expires_in: "soon"` produced an unhandled
`JSONDecodeError`, `AttributeError` or `ValueError` — an internal `500` on the
callback, which N-25 forbids.

Four narrow readers were added — `_json_object`, `_text`, `_seconds`, `_role_ids`
— each guarding one expectation. There is still **no** blanket `except Exception`
in the module, so a genuine defect in our code still surfaces as one. Two
deliberate non-failures:

- an unreadable `expires_in` yields a **short** token lifetime (clamped to 60 s),
  not a login outage;
- an unreadable `roles` array yields **fewer** roles and never more — a role id
  that cannot be read must not become a role that was not granted, and must not
  lock every member out on a cosmetic provider change either.

`ProviderRefused` messages carry none of the provider's body, asserted directly.

### 4.4 Evidence

`tests/web/test_oauth_refusal_audit.py` — **26 tests.** Two parametrizations over
all eleven branches of §3.1 plus five properties the parametrization cannot state.
Each branch asserts, for the attempt's own correlation id: the safe response and
the correlation id the caller was shown; no session row; no OAuth token grant;
exactly one refusal event with the expected action, entity type and reason; no
success event anywhere; and no secret or attacker-controlled raw value in the
audit payload, the audit entity id, the response body, the `Location` header or
the **application's** log. A second identical callback still creates no session
and still records exactly one event.

Two notes on how the assertions are scoped, because both were nearly wrong:

- "exactly one" is scoped **to the attempt's correlation id**, not to the table.
  The rate-limit branch spends its budget by issuing twenty callbacks, each of
  which correctly records its own refusal. The contract's unit is the attempt.
- the log assertion excludes `httpx`/`httpcore`/`asyncio`, which are the **test
  client's** loggers. `httpx` logs the request line of every call the test makes,
  including the authorization code the test itself constructed, before any
  application code runs. Including it would assert something about `httpx`, not
  about the portal.

`tests/web/test_provider_classification.py` — **46 tests.** The **real**
`DiscordIdentityProvider` driven through `httpx.MockTransport`: transport failure,
read timeout, 429, 500, 503, 400, 401, missing access token, null access token,
non-JSON body, JSON array, JSON string, empty body, malformed and missing identity
subject, an id that is an object, member-read 403/429/500/transport failure, and
eight `roles` shapes. A `404` from the member read remains a **fact** (not a
member), not an outage. No socket is opened and no host is resolved; **no
production Discord application or guild was contacted.**

`tests/web_fixtures.py` — `FakeDiscordProvider` gained
`unavailable_at_exchange`, `unavailable_at_verify` and `refuse_verify`, because a
double that can only fail "somewhere" cannot tell a test which of the two network
calls was exercised.

### 4.5 Mutations run and reverted

Each mutation restored the pre-remediation early return, the whole portal suite
was run, and the mutation was reverted. `adapters/web/app.py` is byte-identical to
its pre-mutation state (verified by restoring from a copy taken before the first
mutation, then re-running the suite green).

| Mutation | Killed by | Count |
|---|---|---|
| **M1** — provider outage returns without recording | `test_every_terminal_callback_refusal_writes_exactly_one_audit_event[provider_unavailable_at_exchange]`, `…[provider_unavailable_at_verification]`, `test_a_replayed_refused_callback_still_creates_no_session[provider_unavailable_at_exchange]`, `…[provider_unavailable_at_verification]`, `test_a_refusal_that_cannot_be_recorded_does_not_become_a_login` | 5 failed, 264 passed |
| **M2** — missing cookie/state/code returns without recording | `…[missing_transaction_cookie]`, `…[missing_state]`, `…[missing_authorization_code]` in **both** parametrizations | 6 failed, 263 passed |
| **M3** — rate-limited callback returns without recording | `…[callback_rate_limited]` in both parametrizations | 2 failed, 267 passed |

The double-audit direction is covered by
`test_the_recorder_writes_once_even_if_a_branch_records_twice`, which asserts the
property on the object rather than through a route.

---

## 5. Finding 3 — corrected as far as authorized

The decision note is
[`phase-3-p3-1-tc-bg-05-http-evidence-decision.md`](phase-3-p3-1-tc-bg-05-http-evidence-decision.md).
**No P3.2 route was added. No contract was edited.** The recommendation is Option
1: reallocate the direct-HTTP portions of TC-BG-05b/c/e to P3.2/P3.G2, keeping the
service and constraint evidence at P3.G1, with the outstanding HTTP evidence
recorded as a named P3.G2 blocker.

Corrected without waiting, because these are claim corrections rather than
contract changes: §6 below reports the portions separately; the original
submission's §10 rows are annotated as superseded (its new §0, corrections C1 and
C3); P3.G1 is not marked ready or closed; and no mocked function call is presented
as direct-HTTP evidence anywhere.

---

## 6. Corrected traceability for TC-BG-05a…05e and TC-AUTH-11

| Test | Portion | Level | Status | Evidence |
|---|---|---|---|---|
| TC-BG-05a | Service refusal, all four capabilities; no row written; refusal event written | service + database | **Implemented, passing** | `test_a_continuity_scoped_create_is_refused_and_recorded` |
| TC-BG-05b | Direct HTTP to R-33, R-34, R-38 with a break-glass session | direct HTTP | **UNRUN — allocated to P3.G2 by OD-45** | R-33/R-34/R-38 are P3.2's and are absent by design; evidence remains mandatory |
| TC-BG-05c | Service half of the escalation sequence: BG session → allowed mapping → ordinary login → capability set is `{platform_administrator}` with scope `emergency_continuity` | service + database | **Implemented, passing** | `test_the_whole_escalation_sequence_is_refused` |
| TC-BG-05c | HTTP half: every Council route, every import route and R-38 refuse the continuity-scoped session | direct HTTP | **UNRUN — allocated to P3.G2 by OD-45** | Those routes do not exist in this build; evidence remains mandatory |
| TC-BG-05d | Check constraint refuses the insert with the application bypassed, under runtime **and** owner roles | real PostgreSQL constraint | **Implemented, passing** | `test_the_constraint_refuses_the_same_thing_with_the_application_bypassed` |
| TC-BG-05e | Service half: ratification flips provenance, rotates sessions, restores full scope; second ratification and the reverse transition are refused by the trigger | service + database | **Implemented, passing** | `test_ratification_by_a_full_scope_administrator_restores_full_scope`, `test_ratification_is_one_way_and_happens_once` |
| TC-BG-05e | HTTP half: R-38 by `BG` or `AC` returns `403` | direct HTTP | **UNRUN — allocated to P3.G2 by OD-45** | R-38 is P3.2's; evidence remains mandatory |
| TC-AUTH-11 | Success writes exactly one event, no secret | service + database | **Implemented, passing** | `test_a_member_login_creates_one_session_and_one_audit_event`, `test_the_successful_path_writes_no_refusal_event` |
| TC-AUTH-11 | **Refusal** writes exactly one event, same correlation id, no secret — **every** terminal exit | direct HTTP + database | **Implemented, passing** (previously **overstated**) | `test_oauth_refusal_audit.py`, 26 tests over the eleven exits of §3.1 |

---

## 7. Finding 4 — corrected migration reporting

The superseded sentence was: *"No historical row is read, updated or deleted."*
The accurate facts:

1. **`discord_users` rows are read.** `_backfill_accounts` selects every row with
   no `('discord', id)` external identity and derives one account and one identity
   from each. The table is not modified.
2. **`character_access` rows are updated**, intentionally: `platform_account_id`
   and `granted_by_account_id` are set from the identity table, resolved through
   `discord_user_id` and `granted_by_discord_user_id`. Nothing else on the row
   changes; no row is inserted or deleted. This is the point of stage A — those
   columns must carry attribution before stage B can make them `NOT NULL`.
3. **The append-only tables are not rewritten** by the attribution
   column/constraint work: `audit_events` gains a nullable column and has its
   attribution check swapped; `snapshot_imports` gains a nullable column and a
   strengthened `NOT VALID` constraint; `foundry_snapshots` gains a nullable
   column and its foreign key.
4. **Catalogue-only DDL does not fire the append-only row trigger.** `ADD COLUMN`
   without a default, `ADD CONSTRAINT … NOT VALID` and `DROP CONSTRAINT` are
   catalogue operations and PostgreSQL row triggers do not fire for DDL, so
   migration 0002's trigger is neither dropped, disabled nor evaded — it is never
   reached.
5. **The `xmin` evidence proves the specifically seeded append-only rows were not
   rewritten**, across the constraint swap only. It does not prove — and was never
   capable of proving — that migration 0006 read or wrote no historical data
   anywhere. Those are two different claims and only the first is evidenced.

**Migration 0006 was not altered.** The prose was corrected to match the
migration, not the other way round.

Corrected in: the original submission's new §0 (correction C2) with an inline
supersession note at §6.3; `docs/operations/web-portal.md` §3.2a, a new table
naming exactly which existing rows are read and written; and the change-log entry
recorded below.

### 7.1 The migration, control-total and history tests, re-run, and what each proves

All 27 passed. `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
./venv-web/bin/python -m pytest tests/web/test_identity_migration.py
tests/web/test_audit_attribution.py` — **27 passed in 15.85s**.

| Test | What it actually proves |
|---|---|
| `test_stage_a_gives_every_discord_user_one_account_and_one_active_identity` | The backfill **read** `discord_users` and produced exactly one account and one active identity per row. This is the read the old prose denied |
| `test_the_character_access_row_resolves_to_its_own_users_accounts` | The `character_access` **update** resolved each row to the account of its *own* Discord user — control total T6's property, at row level |
| `test_re_running_the_backfill_inserts_nothing` | Idempotency comes from the mapping constraint, not a flag |
| `test_each_stage_round_trips_leaving_identical_data` | `upgrade → downgrade → upgrade` per stage leaves the data identical |
| `test_history_is_byte_identical_across_the_swap_including_its_row_versions` | For the **seeded `audit_events` rows only**, `xmin` is unchanged across the constraint swap: no row *was written*. It says nothing about `discord_users`, `character_access`, `snapshot_imports` or `foundry_snapshots` |
| `test_append_only_denial_still_holds_after_the_swap` | The 0002 trigger still refuses `UPDATE`/`DELETE` afterwards — it was never suspended |
| `test_the_constraint_inventory_of_all_three_tables_is_exactly_as_documented` | T8's property: no later migration can quietly reintroduce a Discord-only attribution rule |
| `test_foundry_snapshots_gained_a_column_and_no_constraint` | The narrowest of the three changes is exactly as narrow as claimed |
| `test_validating_the_new_constraint_succeeds_and_modifies_nothing` | `VALIDATE CONSTRAINT` scans without writing |
| `test_the_swap_round_trips_on_a_database_holding_account_attributed_rows` | The downgrade restores the legacy constraint `NOT VALID` so a restore over account-attributed rows does not half-apply |
| `test_before_the_swap_…`, `test_account_attributed_inserts_succeed_in_both_forms`, `test_an_unattributed_human_action_is_rejected_by_the_database` / `…_by_the_python_guard` (5 capabilities each), `test_machine_capabilities_remain_valid_with_no_attribution_at_all` (2) | The attribution rule was **replaced, not relaxed**: its subject widened from a Discord user to an identified person, and an unattributed human action is still refused by both the database and `application/audit.py` |
| `test_stage_b_enforces_both_index_sets_at_once`, `test_stage_c_keeps_the_shadow_current_and_refuses_an_unexpressible_row`, `test_the_protected_bootstrap_mapping_is_inserted_by_the_migration` | Stages B and C, and the seeded protected row |

---

## 8. Changed files, exactly

### 8.1 New (production)

```
application/web/refusals.py
```

### 8.2 Modified (production)

| File | Change |
|---|---|
| `adapters/web/app.py` | The callback constructs one `OAuthRefusalRecorder` and records on all eleven refusing exits; new `_record_refusal` helper; two imports |
| `adapters/web/discord_provider.py` | Guarded payload readers `_json_object`, `_text`, `_seconds`, `_role_ids`; malformed provider data becomes `ProviderRefused` instead of an unhandled `500` |

### 8.3 New (tests)

```
tests/web/test_oauth_refusal_audit.py        26 tests
tests/web/test_provider_classification.py    46 tests
```

### 8.4 Modified (tests)

| File | Change |
|---|---|
| `tests/web_fixtures.py` | `FakeDiscordProvider` gains `unavailable_at_exchange`, `unavailable_at_verify`, `refuse_verify` |

### 8.5 Documentation and records

```
docs/review/phase-3-p3-1-remediation-submission.md            (this document, new)
docs/review/phase-3-p3-1-sm-01-completion-binding-decision.md (new — finding 1)
docs/review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md   (new — finding 3)
docs/review/phase-3-p3-1-submission.md                        (new §0 + four inline supersession notes; nothing deleted)
docs/operations/web-portal.md                                 (new §3.2a)
docs/project-management/{status,raid-register,change-log}.md  (dated controlled entries)
```

**No migration was added, edited or removed.** No contract under `docs/contracts/`
was edited. No ADR was edited. `.env`, `yt-cookies.txt` and every credential file
are untouched, and `design-prototype/` is untouched.

---

## 9. Security, privacy, migration, rollback and operational effects

**Security.** The platform now records every terminal login refusal, which is the
control an incident review depends on: previously an attacker probing the callback
with a forged cookie, a spent transaction or during a provider outage left no
trace distinguishable from an attempt that never happened. Malformed provider data
no longer produces an unhandled `500`. Every property Codex asked to be preserved
is preserved: single-use AAD-bound PKCE recovery, opaque database-backed sessions,
token encryption and deletion, CSRF/origin/header controls, N-65/N-67, protected
mapping immutability, append-only history, runtime least privilege, and the frozen
visual prototype (14/14 manifest entries verify).

**Privacy.** The refusal vocabulary is closed and non-secret. No client address
reaches an audit payload — the rate limiter continues to store only a keyed
digest. No cookie value, provider response body, exception text or credential
material is recorded. A malformed cookie is recorded as a category, never echoed.

**Data migration.** None. No migration was added or changed, and `alembic check`
reports no new upgrade operations.

**Rollback.** Unchanged. The rollback costs of 0006/0007/0008 are as recorded in
the original submission §6.4 and `docs/operations/web-portal.md` §3.3. The
remediation adds no schema and therefore no new rollback cost.

**Operational.** One new audit action *value* — none: the action is the existing
`auth.login.refused`. Refusal **volume** rises, because five branches that
recorded nothing now record one row each; a callback flood is bounded by N-18 at
20 per source address per 10 minutes, so the added volume is bounded by the same
limit that already bounded the attempts.

---

## 10. Verification — every command and its exact result

Run 2026-08-14 on this host. `$DB` is
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`.

### 10.1 The guarded database identity, proven first

| Check | Result |
|---|---|
| `psql --dbname=freedom_test -c 'SELECT current_database(), inet_server_addr(), inet_client_addr()'` | `freedom_test`, both addresses **null** |
| `assert_disposable_target(url, expected_database='freedom_test', runtime_url=$DATABASE_URL, policy=UNIX_SOCKET_ONLY)` | **accepted** |
| `verify_connected_unix_socket_target(connection, expected_database='freedom_test')` | **accepted**; `('freedom_test', None, None)` |

Both addresses null is a Unix-domain socket, which a TCP tunnel cannot present.
The guards are the repository's own; neither was weakened, mocked or bypassed. No
credential is recorded here or anywhere in this package.

### 10.2 Focused, then complete

| # | Command | Result |
|---|---|---|
| 1 | `$DB ./venv-web/bin/python -m pytest -q tests/web/test_oauth_refusal_audit.py` | **26 passed**, 2.13s |
| 2 | `$DB ./venv-web/bin/python -m pytest -q tests/web/test_provider_classification.py` | **46 passed**, 0.10s |
| 3 | `$DB ./venv-web/bin/python -m pytest tests/web/test_identity_migration.py tests/web/test_audit_attribution.py` | **27 passed**, 15.85s |
| 4 | `$DB ./venv-web/bin/python -m pytest -q tests/web` | **269 passed**, 0 failed, 0 skipped, 5 warnings, 21.32s |
| 5 | `$DB ./venv/bin/python -m pytest -q` | **2252 passed**, 0 failed, 0 skipped, 1 warning, 125.46s |
| 6 | `$DB ./venv/bin/python -m pytest -q tests/test_runtime_grants.py tests/test_runtime_grants_live.py` | **56 passed**, 1.50s |
| 7 | `alembic downgrade base → upgrade head → downgrade base → upgrade head` against `freedom_test` | head `0008` both times; no error |
| 8 | `./venv/bin/alembic check` | **No new upgrade operations detected** |
| 9 | `./venv-web/bin/python -m compileall -q application adapters domain tools migrations tests` | exit 0 |
| 10 | `./venv/bin/python -m compileall -q …` | exit 0 |
| 11 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 12 | `git diff --check` | exit 0, no output |
| 13 | `./venv/bin/python -m pytest -q` (no `TEST_DATABASE_URL`) | **1999 passed, 253 skipped** — the skips refuse rather than pass without a guarded database |
| 14 | `./venv-web/bin/python -m pytest -q tests/web` (no `TEST_DATABASE_URL`) | **93 passed, 176 skipped** — the 93 are the structural, configuration and provider-classification tests, which need no database |

**Counts, reconciled.** `tests/web` 197 → **269** (+26 refusal, +46 provider
classification). The bot suite 2251 → **2252**: the single added case is
`tests/test_storage_claim_vocabulary.py::test_no_python_message_claims_the_filesystem_is_unchanged[application/web/refusals.py]`,
an existing repository-wide guard that automatically covers the new module. It
passes.

The warnings are unchanged in kind: one `audioop` deprecation from `py-cord` on
Python 3.12 (pre-existing), and five `httpx` per-request-cookie deprecations in
pre-existing portal tests. The new tests add none — they send cookies as an
explicit `Cookie` header.

### 10.3 Formatter, linter and type checker

**None is configured or installed**, re-verified for this remediation exactly as
P3.1 recorded it: no `pyproject.toml`, `setup.cfg`, `.flake8`, `ruff.toml` or
`mypy.ini` exists, and `black`, `ruff`, `flake8`, `mypy`, `pyright`, `isort` and
`pylint` are absent from both virtualenvs. `compileall` was run in both as the
nearest available check. **No such dependency was introduced** — choosing one is a
repository-wide change and remains an open maintainer decision.

### 10.4 Evidence deliberately **not** claimed

| Class | Why |
|---|---|
| `staging` | **Staging does not exist** (issue I-06). Unchanged by this remediation |
| `browser`, `real-device`, `assistive-technology` | P3.4's package, Peter's hardware, and not scheduled |
| Live Discord | Every provider interaction in the tests is a scripted double or an `httpx.MockTransport`. **No production Discord application or guild was contacted** |
| TC-BG-05b, and the HTTP halves of 05c and 05e | Blocked on the finding-3 decision. Reported as **unrun**, not as passing |
| Finding 1's concurrency and mutation evidence | Not yet produced. OD-44 now authorizes the implementation; the evidence is required with that remediation |

---

## 11. Residual risks and remaining blockers

| # | Item | State |
|---|---|---|
| **B1** | **Finding 1 is unremediated.** A session is still not durably bound to a consumed OAuth transaction; route ordering is the only thing preventing the forbidden state | **Blocking. Awaiting Peter's decision** on the SM-01 note |
| **B2** | Finding 3's evidence allocation is now ruled by OD-45: TC-BG-05b and the HTTP halves of 05c/05e belong to P3.2/P3.G2 | **Decision resolved 2026-08-14.** The HTTP evidence remains mandatory and blocks P3.G2, not P3.G1 |
| 3 | A refusal that cannot be audited becomes a `500` rather than a clean redirect. Deliberate and fail-closed, but it is a visible availability effect if the audit table ever becomes unwritable | Accepted; documented in `refusals.py` |
| 4 | The refusal vocabulary is closed **in Python**, not by a database check constraint on `payload->>'reason'`. A future caller could write a different string | Recorded; a constraint would be a schema change and is not authorized here |
| 5 | Everything carried forward from the original submission §12: A-05 unvalidated (no WebAuthn credential enrolled on any host), RR-13's persistence gain, RR-03's boundary burst, RR-02's prefetch, the stage-C trigger proven on synthetic rows only, unmeasured audit-volume performance, and no static analysis toolchain | Unchanged |

---

## 12. Clean-worktree and diff account

`git status --porcelain` on branch `docs/platform-plan`. The tree still contains
**three** layers, separated here so a reviewer can tell them apart. Nothing was
committed and no branch was created.

### 12.1 Pre-existing P3.0 documentation — not P3.1's and not this remediation's

```
 M docs/adr/README.md
 M docs/discovery/open-decisions.md
 M docs/project-management/decision-register.md
?? docs/adr/0010-provider-neutral-identity-and-emergency-administration.md
?? docs/contracts/                                   (11 files, none edited here)
?? docs/review/phase-3-p3-0-remediation-claude-prompt.md
?? docs/review/phase-3-p3-0-remediation-submission.md
?? docs/review/phase-3-p3-0-submission.md
?? docs/review/phase-3-p3-1-claude-prompt.md
```

### 12.2 P3.1's original implementation — unchanged by this remediation except where §8 says

Everything in the original submission §4: `application/web/`, `adapters/web/`,
`tests/web/`, `migrations/versions/000{6,7,8}_*`, the five `tools/` modules, the
three `requirements-web*` files, `docs/operations/web-portal.md`, and the
twenty-two modified files it lists.

### 12.3 This remediation's own changes

Exactly the fourteen paths in §8: one new production module, two modified
production modules, two new test modules, one modified test-fixture module, three
new review documents, and five modified documentation/record files
(`phase-3-p3-1-submission.md`, `web-portal.md`, `status.md`, `raid-register.md`,
`change-log.md`). **No migration, no contract, no ADR, no `.env`-adjacent file and
no `design-prototype/` file is among them.**

Several of those paths are *untracked* rather than *modified* in
`git status --porcelain`, because P3.0 and P3.1 are both uncommitted: a change
inside `application/web/`, `adapters/web/`, `tests/web/`,
`tests/web_fixtures.py`, `docs/operations/web-portal.md` or
`docs/review/phase-3-p3-1-submission.md` does not appear as ` M` at all. The
three files that do appear as newly ` M` because of this remediation are
`docs/project-management/{status,raid-register,change-log}.md`; every other
`M` line in the tree predates it.

---

## 13. Review request

**Codex independent implementation review** is requested over:

1. the refusal boundary — whether `OAuthRefusalRecorder`'s "at most one" property
   holds for every path, including a branch that raises after recording;
2. the enumeration in §3.1 and §3.2 — whether any terminal exit or
   session-creating path is missing from either;
3. the provider payload readers — whether any remaining unguarded read in
   `discord_provider.py` can still produce an unhandled `500`, and whether the
   two deliberate non-failures (clamped lifetime, dropped role ids) fail closed;
4. the correction in §7 against migration 0006 as written; and
5. whether findings 1 and 3 are correctly stopped for decision rather than
   silently implemented.

**A separately reported security-focused pass** is requested over:

1. what a refusal payload can contain, on every branch, including whether the
   `external_identity` entity id on E12 is acceptable as recorded;
2. the audit-volume and correlation-id properties as an abuse surface — whether
   an attacker can use the new writes to amplify load past what N-18 bounds;
3. the decision that a rate-limited callback is one authentication-attempt audit
   rather than a separate rate-limit audit;
4. the residual exposure of finding 1 as stated in §2, and whether the
   recommended completion binding closes it; and
5. whether the `500`-on-unwritable-audit behaviour is the right fail-closed
   direction, or whether a refusal should degrade to an unrecorded redirect.

---

P3.1 remediation submitted for Codex independent and distinct security re-review; P3.G1 remains open and P3.2 has not started.
