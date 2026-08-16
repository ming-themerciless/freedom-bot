# Phase 3 P3.1 — OD-44 provider-binding and rotation-integrity remediation submission

**Prepared:** 2026-08-14 · **Package:** P3.1, second post-decision remediation ·
**Owner:** Claude (Working Technical Lead) · **Status:** **Submitted for Codex
independent implementation re-review and a separately reported security-focused
re-review. Not accepted. P3.G1 is open. P3.2 has not started.**

**Authority.** Peter Duscha's 2026-08-14 addition to the I-07/OD-44 decision
record,
[`phase-3-p3-1-sm-01-completion-binding-decision.md`](phase-3-p3-1-sm-01-completion-binding-decision.md) §8:
the partial unique index
`UNIQUE (oauth_transaction_id) WHERE rotated_from_session_id IS NULL` is the
authoritative interpretation of OD-44, **conditionally** on rotation integrity.
Together with Codex's two blocking items, recorded in
`docs/review/Handover information`.

**Predecessors, preserved unedited:**
[`phase-3-p3-1-submission.md`](phase-3-p3-1-submission.md),
[`phase-3-p3-1-remediation-submission.md`](phase-3-p3-1-remediation-submission.md)
and
[`phase-3-p3-1-od-44-remediation-submission.md`](phase-3-p3-1-od-44-remediation-submission.md).
Nothing in any of them was rewritten. The decision record, the contracts and the
project records were amended by **dated addition**; §9.3 lists every one.

**Peter approved an interpretation, not an implementation.** §8 of the decision
record authorizes this remediation and states the conditions it must meet. It does
not accept the code, and this submission does not claim it does: Codex must verify
that the conditions were implemented.

---

## 1. Outcome in one table

| Item | Disposition |
|---|---|
| **Blocking finding 1** — the completion claim did not bind the transaction's recorded provider | **Remediated.** `AND provider_key = :provider_key` in the claim; the expected key derived from `VerifiedCompletion`, an indivisible verified provider result; a typed interface change so tokens and identity each carry the key their adapter stamped. 9 new tests (TC-AUTH-15), 1 mutation run and killed |
| **Blocking condition 2** — the approved partial index requires a linear, non-crossing rotation chain | **Remediated.** One partial unique index, two composite rotation foreign keys, one locked transactional rotation operation, and no creation path that accepts a rotation label. 15 new portal tests (TC-AUTH-16) and 3 new migration tests (TC-AUTH-17), 5 mutations run and killed |
| Migration 0009 | **Updated in place** (uncommitted and not accepted). 0006–0008 untouched. Upgrade/downgrade/re-upgrade rehearsed, both preconditions executable |
| OD-45 | **Unchanged.** No P3.2 route added, no HTTP evidence waived |
| P3.G1 | **Open.** P3.2 has not started. Nothing is committed, deployed, or run against production or staging |

Suite movement: portal **299 → 323**, bot **2257 → 2260**. No test was removed,
weakened, or marked skip.

---

## 2. Blocking finding 1 — the completion is bound to the recorded provider

### 2.1 The finding, restated in the terms of the code

Before this change the claim was:

```sql
UPDATE oauth_transactions SET completion_claimed_at = :now
 WHERE id = :id AND consumed_at IS NOT NULL AND completion_claimed_at IS NULL
RETURNING id
```

and `OAuthLoginService.complete()` separately took an `identity: VerifiedIdentity`
whose `provider_key` it used for account resolution, token storage and the success
audit. Those are two independent facts and nothing required them to agree. A
caller inside the process holding another provider's verified identity and tokens
could therefore spend a consumed Discord transaction: the claim matched, an
account was resolved under the *other* provider's key, and a session was created
that named a Discord transaction.

The existing `test_a_completion_naming_a_different_transaction_than_the_one_consumed_is_refused`
did not cover it — it supplied a second **unconsumed transaction**, which the
`consumed_at` predicate already refused, and never a second **provider**.

### 2.2 What now enforces it

**The claim carries the predicate** (`adapters/web/repositories.py`,
`OAuthTransactionRepository.claim_completion`):

```sql
UPDATE oauth_transactions SET completion_claimed_at = :now
 WHERE id = :id
   AND consumed_at IS NOT NULL
   AND completion_claimed_at IS NULL
   AND provider_key = :provider_key
RETURNING id
```

The comparison is inside the claiming statement, not in a read before it, for the
same reason the `state_hash` comparison is inside `consume()`: a check that is not
part of the claiming update is a check with a window between it and the claim.

**The expected key is derived from what was verified, not from the route.**
`complete()` no longer takes `identity` and `tokens` as two arguments. It takes
one `completion: VerifiedCompletion`, and reads `completion.provider_key`.

### 2.3 The typed interface change, and why it is the smallest one

The handover asked whether the token result carries provider identity strongly
enough for a provider-neutral future adapter. It did not: `ProviderTokens` had no
provider field at all, so "these tokens and this identity came from one provider"
was not expressible. Three changes make it expressible, and no more than three:

| Change | File | Why |
|---|---|---|
| `ProviderTokens` gains `provider_key`, stamped by the adapter from its own constant | `application/web/providers.py`, `adapters/web/discord_provider.py` | A token result that cannot say where it came from cannot support a binding. The key is **never** read from a provider response — a value the provider supplies is a value the provider can change, which is exactly the unverifiable claim the handover forbids inventing |
| `VerifiedCompletion(identity, tokens)`, frozen, refusing construction when the two keys differ (`ProviderResultMismatch`) | `application/web/providers.py` | There is no moment at which a mismatched pair exists as a value something could be trusted with. `complete()` accepts only this type, so the two halves cannot be handed in separately |
| `IdentityProvider.verify()` must refuse another provider's tokens, and the Discord adapter does (`ProviderRefused`) | `application/web/providers.py`, `adapters/web/discord_provider.py` | Without it, an adapter is a laundering step: feed it provider B's tokens, receive provider A's identity, and the pair now agrees. Refused before the first outbound request, so B's bearer token is never presented to A |

`VerifiedIdentity` already carried `provider_key` and is unchanged. No capability,
no membership decision and no new field crosses the provider boundary.

### 2.4 Refusal behaviour

A provider mismatch is the **existing** typed completion refusal, unchanged in
every observable way:

- `AuthenticationFailure(code="transaction_unknown")`, the same code as an unknown,
  unconsumed or already-claimed id;
- the described `FailureAudit` payload is `{"reason": "completion_not_claimable"}`
  — no provider key, no subject, no token, no code, no state, no verifier, no
  exception text;
- the claim is rolled back with the caller's transaction, so the row stays
  **consumed and unclaimed** — the same terminal state as process death, and
  equally unreplayable;
- no account, external identity, membership projection, token grant, session or
  success audit is created. The claim is the first statement of `complete()`, so
  the refusal happens before any of them is attempted;
- exactly one `auth.login.refused` event is written, by the existing
  `OAuthRefusalRecorder` at the outer boundary, in its own transaction after the
  work transaction rolled back (TC-AUTH-11 unchanged).

**The branches are deliberately indistinguishable to the caller.** A refusal that
said *which* predicate failed would tell a prober whether a transaction id exists
and which provider it belongs to.

### 2.5 Provider and network I/O stayed outside every database transaction

`exchange()` and `verify()` are still awaited between the `consume` and `complete`
threadpool calls, each of which owns its own transaction. `VerifiedCompletion` is
constructed in the route, in memory, between the two — it performs no I/O. Nothing
in this change moves a network call inside a transaction, and nothing persists or
logs a code, state, verifier, token, raw response, cookie or exception text.

### 2.6 Evidence (TC-AUTH-15, `tests/web/test_oauth_completion_binding.py`)

| Required proof | Test |
|---|---|
| 1. A consumed Discord transaction cannot complete with another provider's verified identity/token result | `test_a_consumed_transaction_cannot_be_completed_by_another_provider` (and the reverse direction, `test_a_transaction_recorded_for_another_provider_is_not_completable_by_discord`) |
| 2. Consuming transaction A does not authorize a result associated with transaction B or another provider | `test_consuming_one_transaction_does_not_authorize_another_providers_result` — a genuinely consumed transaction, then both substitutions |
| 3. Provider mismatch leaves the transaction consumed and unclaimed and leaves no account, identity, membership, token grant, session or success audit | asserted in all three above through `_every_effect_count`, which counts sessions, token grants, success audits, accounts, external identities **and** membership projections |
| 4. Matching-provider success, replay, concurrent completion, rollback and exactly-one refusal audit remain correct | `test_the_matching_provider_still_completes_and_claims_exactly_once` (the control: the predicate refuses a mismatch and nothing else); `test_a_provider_mismatched_completion_writes_exactly_one_refusal_audit`; and the unchanged TC-AUTH-13c/d/g tests, all still passing |
| 5. A mutation removing the provider predicate is killed | M1 in §8 |
| The derivation is trustworthy | `test_a_completion_cannot_be_built_from_two_providers_results`; `test_an_adapter_refuses_to_verify_another_providers_tokens`; `test_the_discord_adapter_stamps_and_checks_its_own_provider_key` — the last against the **real** `DiscordIdentityProvider` over a mocked transport, so the double's behaviour is not the only evidence |
| The statement itself | `test_the_claim_statement_refuses_a_foreign_provider_key_directly` — the repository method, with the service out of the way |

The second provider in these tests is `FakeDiscordProvider(provider_key="another-provider")`.
It is a real double producing a real verified result; no `VerifiedIdentity` or
`ProviderTokens` is hand-constructed to make a refusal easy.

### 2.7 What was **not** done, deliberately

- **No second provider was registered or implemented.** ADR 0010 D7 reserves that
  for its own package. The finding is reachable today only by an in-process
  caller, which is precisely why the control had to be durable rather than
  ordering.
- **No route-level provider comparison was added.** `consume()` returns the row's
  `provider_key` and the route could compare it against the adapter it is about to
  call. That would be route ordering — the thing the finding says must not be what
  stands between a caller and a session — and it would add a second copy of the
  rule that can drift from the enforcing one.

---

## 3. Blocking condition 2 — the rotation chain is linear and does not cross

### 3.1 Why the condition exists

The approved predicate scopes uniqueness to rows with
`rotated_from_session_id IS NULL`, so **rotated** rows may share their root's
transaction id. That is correct only if the set permitted to share it is exactly
one linear chain per login. If a session could acquire two successors, or a
rotation could change account, method or binding, the predicate would be a hole in
the completion binding rather than an accommodation of N-08.

### 3.2 What PostgreSQL now enforces, declaratively

Added to `sessions` by migration 0009 and to the SQLAlchemy metadata:

| Object | Rule |
|---|---|
| `UNIQUE (rotated_from_session_id) WHERE rotated_from_session_id IS NOT NULL` | At most one successor per predecessor — no branch, so never two live descendants of one login. Partial because every chain's root has no predecessor and there are many roots |
| `FOREIGN KEY (rotated_from_session_id, platform_account_id, auth_method) REFERENCES sessions (id, platform_account_id, auth_method)` | A rotation's account and authentication method **are** its predecessor's |
| `FOREIGN KEY (rotated_from_session_id, oauth_transaction_id) REFERENCES sessions (id, oauth_transaction_id)` | A rotation's OAuth binding **is** its predecessor's |
| `UNIQUE (id, platform_account_id, auth_method)`, `UNIQUE (id, oauth_transaction_id)` | The targets those keys require. `id` is the primary key, so both are trivially unique |

**The `MATCH SIMPLE` analysis, because it is load-bearing.** Both keys are
satisfied without a lookup when any referencing column is null, and each null case
is the wanted one:

- a **root** session has `rotated_from_session_id IS NULL` — no predecessor to
  agree with, and neither key applies;
- a **break-glass rotation** has `oauth_transaction_id IS NULL`, so the binding key
  does not apply — while the account-and-method key still holds it to its
  predecessor and `ck_sessions_oauth_transaction_binding` independently refuses it
  a transaction id;
- a **`discord_oauth` rotation cannot shed its binding** by nulling the column: the
  check constraint would then require a different `auth_method`, and the
  account-and-method key refuses that. The two constraints close on each other.

`MATCH FULL` was considered and rejected: it requires all-null-or-all-non-null, so
it would make break-glass rotation impossible — a working control turned into an
outage. **No trigger was added.** The handover permits one only with a documented
assessment showing it is the smallest reliable option; it is not, because the two
foreign keys plus one locked statement sequence cover the same ground with
mechanisms already in use in this schema.

### 3.3 What the single transactional operation enforces

Liveness is a `now()` comparison and cannot be an index predicate or a check
constraint, so it lives in `SessionRepository.rotate()` — one method, in the
caller's transaction:

1. `SELECT id, platform_account_id, auth_method, oauth_transaction_id FROM sessions
   WHERE id = :id AND revoked_at IS NULL AND NOT EXISTS (a row naming it) FOR UPDATE`;
2. insert the successor **from that locked row's own values** — the caller supplies
   no account, no method and no binding;
3. `UPDATE … SET revoked_at, revocation_reason WHERE id = :id AND revoked_at IS NULL`,
   asserted to affect one row.

Zero rows at step 1 returns `None`, which `SessionService.rotate()` turns into the
typed `SessionRotationRefused`. A caller's account/method disagreement with the
locked row is also `None`: the composite keys would refuse the insert anyway, but
an `IntegrityError` at that point would surface as a `500` where a typed refusal
belongs.

**Concurrency is decided by PostgreSQL.** Two rotations of one session meet at the
row lock. The winner revokes the predecessor in the same transaction; the loser
blocks, re-evaluates `revoked_at IS NULL` under `READ COMMITTED` when the winner
commits, matches zero rows and is refused. One successor, one refusal, one live
descendant. There is no sleep in any test and no retry in the code.

### 3.4 The evasion the condition names explicitly

> a caller cannot label an arbitrary session as a rotation merely to evade the
> root-session unique index

Two independent reasons it cannot:

1. **In the database.** To hold transaction `T`, a row labelled a rotation must
   name a predecessor that itself holds `T` (binding key). The only rows holding
   `T` are that login's own chain, and each of them can have at most one successor.
   `test_a_row_cannot_be_labelled_a_rotation_to_reuse_another_logins_transaction`
   proves both halves — the mislabelled rotation and the direct second root.
2. **In the application.** `rotated_from_session_id` is no longer writable by any
   creation path. `SessionRepository.create()` and `SessionService.begin()` lost
   their `rotated_from` parameter entirely; the label is produced only by
   `rotate()`, from a locked predecessor.
   `test_no_creation_path_accepts_a_rotation_label` asserts this from the
   signatures, because a comment saying so would not fail.

### 3.5 One behavioural consequence, stated rather than buried

**Rotation no longer re-runs the N-66 session limit.** It previously ran because
rotation went through `begin()`. Running it is now actively wrong: a rotation
replaces a session rather than adding one, so the live population is unchanged and
the bound cannot be crossed by rotating — and if the predecessor happened to be the
account's oldest live session, the limit would revoke it and the rotation would
then refuse its own predecessor. Creation still enforces N-66 unchanged.

### 3.6 Evidence (TC-AUTH-16, `tests/web/test_session_rotation_integrity.py`; TC-AUTH-17, `tests/test_oauth_completion_binding_migration.py`)

| Required proof | Test |
|---|---|
| Duplicate successor rejection | `test_the_database_refuses_a_second_successor_for_one_session` (database, application bypassed); `test_a_second_rotation_of_the_same_predecessor_is_refused` (service, typed) |
| Cross-account rejection | `test_the_database_refuses_a_rotation_that_changes_account`; `test_a_rotation_into_another_account_is_refused_by_the_service` |
| Cross-auth-method rejection | `test_the_database_refuses_a_rotation_that_changes_authentication_method`; `test_a_rotation_into_another_authentication_method_is_refused_by_the_service` |
| Cross-binding rejection | `test_the_database_refuses_a_rotation_that_changes_the_oauth_binding`; `test_a_row_cannot_be_labelled_a_rotation_to_reuse_another_logins_transaction` |
| Revoked / already-rotated predecessor refusal | `test_a_revoked_predecessor_cannot_be_rotated`; `test_a_second_rotation_of_the_same_predecessor_is_refused`; `test_an_unknown_predecessor_cannot_be_rotated` |
| Valid OAuth rotation | `test_an_oauth_rotation_chain_stays_linear_and_carries_one_binding` — two generations, one binding, one live session, each predecessor revoked |
| Valid break-glass rotation | `test_a_break_glass_rotation_stays_unbound_to_any_oauth_transaction` |
| Deterministic concurrent rotation | `test_two_concurrent_rotations_produce_one_successor_and_one_refusal` — two connections, `threading.Barrier`, no sleep |
| The objects exist, are `RESTRICT`, and carry exactly their declared columns | `test_the_rotation_keys_declare_restrict_and_reference_the_predecessors_own_values` (read from `pg_constraint`), `test_the_linear_rotation_index_is_unique_and_scoped_to_rotations` (read from `pg_indexes`) |
| Mutations removing each new integrity control are killed | M2–M6 in §8 |

---

## 4. Preserved controls and scope

Nothing below was weakened, and each was re-run rather than assumed:

| Control | State |
|---|---|
| AAD-bound PKCE recovery and erasure as one statement | `consume()` untouched. TC-AUTH-12 passes unchanged |
| Transaction-cookie / `state` binding | Untouched |
| Opaque sessions, encrypted token grants, expiry, revocation | Untouched; `create()` lost only its rotation parameter |
| Atomic success audit, exactly-one refusal audit | Unchanged boundary; the new refusal joins it (§2.4) and is asserted |
| Authorization, CSRF, origin and security headers, rate limits, safe errors | Untouched |
| Append-only history | Untouched. No migration touches `audit_events` |
| Runtime grants | Unchanged. 0009 adds indexes and constraints to `sessions`, already in the `SELECT, INSERT, UPDATE` band, and creates no table. `tests/test_runtime_grants.py` passes |
| Frozen visual assets | `sha256sum -c` reports every file `OK` |
| Read-only character-state boundary | Untouched |
| OD-45 | Unchanged. No P3.2 route added; no HTTP evidence waived |
| Migrations 0006–0008 | Not edited |

---

## 5. The mechanical enumerations

### 5.1 Every terminal exit of R-04 `GET /auth/discord/callback`

Re-enumerated from the current source, in order.

| # | Condition | Response | Audit | Session |
|---|---|---|---|---|
| 1 | N-18 budget spent | `303 …?failure=rate_limited`, `Retry-After` | one, `rate_limited` | none |
| 2 | No cookie, no `state` or no `code` | `303 …?failure=transaction_unknown` | one, `callback_parameters_missing` | none |
| 3 | Cookie is not a UUID | `303 …?failure=transaction_unknown` | one, `transaction_cookie_malformed` (the bytes are never echoed) | none |
| 4 | `consume()` matched zero rows, or the verifier failed its AAD binding | `303 …?failure=<code>` | one, described by the service | none |
| 5 | `ProviderUnavailable` at `exchange()` or `verify()` | `303 …?failure=provider_error` | one, `provider_unavailable` | none |
| 6 | `ProviderRefused` at `exchange()` or `verify()` — **including another provider's tokens offered to an adapter** | `303 …?failure=provider_error` | one, `provider_refused` | none |
| 7 | `complete()` refused: unknown, unconsumed, already-claimed, or **provider mismatch** | `303 …?failure=transaction_unknown` | one, `completion_not_claimable` | none |
| 8 | `complete()` refused: not a guild member | `403` VM-02 | one, `not_a_guild_member` | none |
| 9 | Success | `303` to the allowlisted return path, session cookie set | one `auth.login.succeeded`, in the completion transaction | one, bound |
| 10 | **Defect path:** any unhandled exception, including `ProviderResultMismatch` if an adapter ever returned an identity and tokens naming different providers | `500` VM-20, correlation id only | none (it is not a refusal) | none — the transaction rolled back |

Exit 10 is disclosed rather than hidden. It is unreachable with a conforming
adapter: the route calls one adapter twice, and `verify()` refuses tokens that are
not its own, so the two halves cannot disagree. It is deliberately not converted
into a refusal — a genuine defect must stay visible, which is the same rule
`discord_provider.py` already states about not wrapping its reads in a blanket
`except`. No new class of exit was introduced: an unhandled exception inside the
completion transaction was already possible and is already exercised
(TC-AUTH-13g).

### 5.2 Every production path that can create a web session

| # | Path | Method | Binding |
|---|---|---|---|
| 1 | `OAuthLoginService.complete()` → `SessionService.begin()` (`application/web/oauth.py:428`) | `discord_oauth` | the claimed transaction id, in the same transaction as the claim and the success audit |
| 2 | `EmergencyAccessService._create_emergency_session()` → `begin()` (`application/web/breakglass.py:351`) | `webauthn` | none, and the check constraint refuses one |
| 3 | `EmergencyAccessService` recovery-grant login → `begin()` (`application/web/breakglass.py:291`) | `recovery_grant` | none, same constraint |

There is no fourth. `grep -rn "\.begin(" application adapters tools` outside test
code returns exactly these three, and none of them can produce a rotation: the
parameter no longer exists.

### 5.3 Every production path that can rotate a session

| # | Path | Callers today |
|---|---|---|
| 1 | `SessionService.rotate_if_privileges_changed()` → `SessionService.rotate()` → `SessionRepository.rotate()` | **none in P3.1.** No route calls it; it is the N-08 mechanism the P3.2 request path will use |
| 2 | `SessionService.rotate()` directly | none in production code |

`grep -rn "rotate" application adapters tools` outside tests returns only
`application/web/sessions.py`. That P3.1 has no route caller is unchanged by this
work and is stated again because it bounds the exposure of the condition being
remediated — and because the P3.2 package that wires rotation in must handle
`SessionRotationRefused` as an end-the-session outcome, never a retry (recorded in
the threat model against T-05c).

---

## 6. Migration 0009

### 6.1 What it now creates

Unchanged from the previous submission: `oauth_transactions.completion_claimed_at`
with its check constraint; `sessions.oauth_transaction_id` with the `RESTRICT`
foreign key, the partial unique index `WHERE rotated_from_session_id IS NULL`, and
the `discord_oauth`-equivalence check constraint.

Added by this remediation: `uq_sessions_rotated_from_session_id`,
`uq_sessions_rotation_identity`, `uq_sessions_rotation_binding`,
`fk_sessions_rotation_account_method` and `fk_sessions_rotation_oauth_binding`,
all dropped in `downgrade()` in reverse order.

0009 is uncommitted and was not accepted, so it was updated rather than superseded
by a 0010 — as the handover directs. **0006–0008 were not edited**; `git status`
shows them untracked and unmodified.

### 6.2 The second precondition

`_refuse_nonlinear_rotations()` counts, before adding anything, (a) rotations whose
account or authentication method disagrees with their predecessor's and (b)
predecessors named by more than one successor, and refuses with both counts and the
remedy `DELETE FROM sessions WHERE rotated_from_session_id IS NOT NULL;`. Neither
shape can be produced by `SessionService`; the count exists because `ADD
CONSTRAINT` validates existing rows and would otherwise present a constraint name
where an operator needs a cause. It needs no third count for the OAuth binding:
the first precondition has already established that no `discord_oauth` session
survives to carry one.

Offline mode skips both counts, as before, and the notice in the emitted script
explains that the constraints still refuse — what is lost offline is the
explanation, not the protection.

### 6.3 Rehearsal and rollback consequences

`tests/test_oauth_completion_binding_migration.py` executes upgrade → downgrade →
refused re-upgrade → remedy → successful re-upgrade, now asserting the rotation
objects appear and disappear with the rest, and separately drives the branched-chain
precondition to its refusal and through its remedy. Alembic runs in a subprocess
through the same guarded helper, so the static target guard and the live
Unix-socket identity check apply to every step, and `head` is restored in `finally`.

**Rollback cost is unchanged in kind and unchanged in size.** The new objects
constrain shape rather than carry data, so losing them costs nothing extra: a
downgrade past 0009 still costs every Discord OAuth login (those rows must be
deleted, not merely revoked, before the binding can be restored), and now also
requires that no branched or crossing rotation chain exists. `docs/operations/web-portal.md`
§3.5 records both preconditions and both remedies for the operator.

---

## 7. Verification

Every command was run on this host against the guarded disposable database
`freedom_test`, through the existing static target guard
(`assert_disposable_target`, `UNIX_SOCKET_ONLY`) and the live Unix-socket identity
guard (`verify_connected_unix_socket_target`). Neither guard was weakened, mocked
or bypassed. **No test was skipped.** The two suites share one database and were
run serially.

Narrow first, as the handover requires:

| Command | Result |
|---|---|
| `pytest -q tests/web/test_oauth_completion_binding.py` | **39 passed** (30 before) |
| `pytest -q tests/web/test_session_rotation_integrity.py` | **15 passed** (new file) |
| `pytest -q tests/test_oauth_completion_binding_migration.py` | **7 passed** (4 before) |
| `pytest -q tests/web/test_sessions.py tests/web/test_provider_classification.py` | **56 passed** |

Then complete:

| Command | Result |
|---|---|
| `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest -q tests/web` | **323 passed**, 14 warnings, 0 failed, 0 skipped |
| `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest -q tests` | **2260 passed**, 1 warning, 0 failed, 0 skipped |
| `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | `No new upgrade operations detected.` — the metadata and the revision agree, including all five new objects. One pre-existing `SAWarning` from `migrations/env.py:133` about a `dialect_options` argument, unrelated |
| `./venv-web/bin/python -m compileall -q application adapters domain tools migrations tests` | Clean |
| `./venv/bin/python -m compileall -q application adapters domain tools migrations tests` | Clean |
| `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | Every file `OK`; zero non-`OK` lines |
| `git diff --check` | Clean |
| `grep -rn "MUTATION" application/ adapters/ migrations/ tests/` | One hit, and it is not from this work: a pre-existing comment in `tests/benchmark_snapshot_500.py` reading "NO MUTATION ALLOWED IF DIRTY". Every mutation marker introduced below was reverted |

The 0009 rehearsal, the schema/constraint tests, the runtime-grant tests
(`tests/test_runtime_grants.py`, `tests/test_runtime_grants_live.py`) and the
deterministic PostgreSQL concurrency tests are inside those two runs and pass
unchanged.

**One note on `alembic check`.** It is run with `APP_ENVIRONMENT=test` against
`freedom_test`. Without it the command defaults to `development`, and the
configuration guard correctly refuses a `freedom_test` URL under that environment.
No development or production database was touched.

### 7.1 Warnings

Unchanged in class. The 14 portal warnings are all the same pre-existing `httpx`
`DeprecationWarning` about per-request `cookies=`; the single bot-suite warning is
the pre-existing `DeprecationWarning: import audioop`. **No new warning class was
introduced**, and the portal count did not rise: none of the 24 new tests drives
the callback with a cookie argument.

### 7.2 Formatter, linter and type checker

**None is configured in this repository, and none was introduced.** There is no
`pyproject.toml`, `setup.cfg`, `.ruff.toml`, `.flake8` or `mypy.ini`;
`requirements-dev.txt` and `requirements-web-dev.txt` contain `pytest`,
`pytest-asyncio` and `beautifulsoup4` and nothing else; neither virtualenv contains
`ruff`, `black`, `flake8`, `mypy` or `pylint`. This is reported as an accurate
absence, not as a passing check. Adding a toolchain during a security remediation
would be an unrelated change to every file it touched.

### 7.3 Evidence deliberately not produced

| Evidence | Why |
|---|---|
| Direct-HTTP portions of TC-BG-05b/c/e | Allocated to P3.G2 by OD-45. R-33/R-34/R-38 do not exist. **Not waived** |
| A cross-provider login driven over HTTP | P3.1 registers exactly one provider (ADR 0010 D7). Registering a second to produce HTTP evidence would be unauthorized P3.2-shaped work. The finding is exercised where it lives: at the service, the repository statement and the typed boundary |
| Staging-class checks (TC-OPS-01…05, TC-PERF-01…03, TC-LIM-02) | Staging does not exist (RAID I-06) |
| Browser, real-device and assistive-technology evidence | Nothing here renders a new view |
| Live Discord, production or development database, Foundry, Google Sheet | Never contacted. The provider is a synthetic double; the guild snowflake is synthetic and outside Discord's issued range |
| Killing a real worker process mid-transaction | Not automated; the process-death seam is committed-consumption plus an absent completion, as before |
| Deployment of any kind | Nothing was deployed; no Caddy, systemd or provider registration was touched |

---

## 8. Mutations run and reverted

Each mutation was applied to the working tree from a byte-identical backup, the
relevant suite run, the failures recorded, and the mutation reverted. The
disposable database's schema was reset before and after every migration mutation,
so no mutation's leftovers could contaminate the next run's `downgrade base`. The
final verification in §7 was run after every revert.

| # | Mutation | Result | Killed by |
|---|---|---|---|
| **M1** | Drop `AND provider_key = :provider_key` from the completion claim | **5 failed**, 34 passed | `test_a_consumed_transaction_cannot_be_completed_by_another_provider`; `test_a_transaction_recorded_for_another_provider_is_not_completable_by_discord`; `test_consuming_one_transaction_does_not_authorize_another_providers_result`; `test_a_provider_mismatched_completion_writes_exactly_one_refusal_audit`; `test_the_claim_statement_refuses_a_foreign_provider_key_directly` |
| **M2** | Remove `uq_sessions_rotated_from_session_id` from 0009 | **1 failed**, 14 passed | `test_the_database_refuses_a_second_successor_for_one_session` |
| **M3** | Remove `fk_sessions_rotation_account_method` from 0009 | **2 failed**, 13 passed | `test_the_database_refuses_a_rotation_that_changes_account`; `test_the_database_refuses_a_rotation_that_changes_authentication_method` |
| **M4** | Remove `fk_sessions_rotation_oauth_binding` from 0009 | **2 failed**, 13 passed | `test_the_database_refuses_a_rotation_that_changes_the_oauth_binding`; `test_a_row_cannot_be_labelled_a_rotation_to_reuse_another_logins_transaction` |
| **M5** | Drop `AND revoked_at IS NULL` from the locked predecessor read | **2 failed**, 13 passed | `test_a_revoked_predecessor_cannot_be_rotated`; `test_two_concurrent_rotations_produce_one_successor_and_one_refusal` |
| **M6** | Remove the account/method equality check in `rotate()` | **2 failed**, 13 passed | `test_a_rotation_into_another_account_is_refused_by_the_service`; `test_a_rotation_into_another_authentication_method_is_refused_by_the_service` |

**Reading M2–M4 honestly.** Each is killed by one or two tests, and that is the
correct number rather than a thin one: these are *defence in depth* behind the
locked operation, so a mutation that removes only the constraint should be caught
only by the tests that bypass the application. A larger count would mean some
other test had been depending on a constraint to do the service's job. M5 and M6
are the converse — they remove the service's rules and are killed by the
service-level tests, including the race.

---

## 9. Every changed file

### 9.1 Production code and migrations

| File | Change |
|---|---|
| `application/web/providers.py` | `ProviderTokens.provider_key`; `VerifiedCompletion` with its construction-time agreement check; `ProviderResultMismatch`; the `IdentityProvider` obligations |
| `adapters/web/discord_provider.py` | Stamps `provider_key` on the token result from its own constant; `verify()` refuses another provider's tokens |
| `application/web/oauth.py` | `complete(completion=…)` instead of `(identity=…, tokens=…)`; the expected provider key derived from the verified result and passed to the claim |
| `adapters/web/repositories.py` | `claim_completion(provider_key=…)` with the fourth predicate; `SessionRepository.rotate()`; `create()` lost `rotated_from` |
| `application/web/sessions.py` | `SessionRotationRefused`; `SessionService.rotate()`; `begin()` lost `rotated_from`/`revocation_reason_for_old`; `rotate_if_privileges_changed()` delegates; N-66 not re-run on rotation (§3.5) |
| `adapters/web/app.py` | Constructs `VerifiedCompletion` between the two provider calls and passes it to `complete()`. Route structure, ordering and terminal exits otherwise unchanged |
| `adapters/database/tables.py` | The five new objects in metadata, so `alembic check` keeps them from drifting from the revision |
| `migrations/versions/0009_oauth_completion_binding.py` | The five new objects, the second precondition, the matching downgrades, and the docstring section recording the condition |

### 9.2 Tests

| File | Change |
|---|---|
| `tests/web/test_oauth_completion_binding.py` | Updated to the new `complete()` signature; **+9 tests** (TC-AUTH-15) and the `_every_effect_count` helper |
| `tests/web/test_session_rotation_integrity.py` | **New. 15 tests** (TC-AUTH-16) |
| `tests/test_oauth_completion_binding_migration.py` | **+3 tests** (TC-AUTH-17) and rotation-object assertions inside the existing rehearsal |
| `tests/web_fixtures.py` | `FakeDiscordProvider` stamps its key and refuses another provider's tokens, matching the real adapter |
| `tests/web/conftest.py` | `seed_oauth_transaction(provider_key=…)` |
| `tests/web/test_provider_classification.py` | Its hand-built `ProviderTokens` names `discord` |

### 9.3 Contracts and records — all amended by dated addition

| File | Amendment |
|---|---|
| `docs/review/phase-3-p3-1-sm-01-completion-binding-decision.md` | **§8 new**: the conditional approval, the provider-binding finding, and what the ruling does not do. §1–§7 unchanged |
| `docs/contracts/phase-3-state-machines.md` | SM-01 gains the provider-binding forbidden transition; SM-02 gains four forbidden transitions, the locked rotation mechanism and the concurrent-rotation failure row |
| `docs/contracts/phase-3-logical-schema.md` | §9.1 gains the rotation objects, the `MATCH SIMPLE` analysis and the liveness note; §9.2 records `provider_key`'s role in the claim and the full claim statement |
| `docs/contracts/phase-3-test-traceability.md` | TC-AUTH-15, TC-AUTH-16, TC-AUTH-17 and three coverage-map rows |
| `docs/contracts/phase-3-threat-model.md` | T-05b and T-05c new; RR-15 recorded **closed**, original text preserved |
| `docs/operations/web-portal.md` | 0009's row extended; §3.5 gains the second precondition, its remedy and its rollback consequence |
| `docs/discovery/open-decisions.md` | OD-44 gains the second ruling |
| `docs/project-management/change-log.md` | **C-P3.1-F** new |
| `docs/project-management/decision-register.md` | OD-44 row records the conditional confirmation and the implementation |
| `docs/project-management/raid-register.md` | I-07 row records both re-review items and their remediation |
| `docs/project-management/status.md` | Status line, narrative, decision table and next-update section; suite counts corrected to 323/2260 |

---

## 10. Residual risks

| # | Risk | Level | Disposition |
|---|---|---|---|
| RR-05a | A consumed-but-unclaimed transaction stays claimable by an **in-process** caller until N-04's reaper removes it | Low | Unchanged and now narrower: such a caller must additionally hold a verified result from the *recorded* provider. No route can reach it |
| RR-15 | Two concurrent rotations could produce two live sessions sharing a transaction id | — | **Closed** by this remediation; the race is proved rather than argued (TC-AUTH-16d) |
| New | The provider-binding finding is exercised at the service, the statement and the typed boundary, not over HTTP, because P3.1 registers one provider | Low | Stated in §7.3. The P3.2/provider package that registers a second provider must add the HTTP-level case |
| New | `SessionRotationRefused` has no production caller yet, so its handling is unproven in a request path | Low | Recorded against T-05c: the P3.2 package that wires N-08 rotation in must treat it as an end-the-session outcome, never a retry |
| New | The two composite unique keys exist only as foreign-key targets and add write cost to `sessions` | Low | Accepted. `sessions` is a small, low-write table bounded by N-66 and 30-day retention; the alternative was a trigger |

---

## 11. Dirty-worktree account

The worktree was dirty on arrival and is dirty now, deliberately: **nothing is
committed**, and no unrelated change was reverted, staged or tidied.

- `docs/review/Handover information` shows as modified. That is the task prompt
  itself, modified by the maintainer before this work began. It was read and not
  written.
- The other 22 modified tracked files and every untracked path listed by
  `git status` predate this task, with the exceptions below.
- Changed by this work: the 8 production files in §9.1, the 6 test files in §9.2,
  the 11 documents in §9.3, and one new document — this one. `tests/web/test_session_rotation_integrity.py`
  and this submission are the only new files.
- `git diff --check` is clean. No secret, credential, `.env`, service-account
  file, generated artefact or player datum was read, written or moved.
- The only database touched at any point was `freedom_test`. Its schema was reset
  between migration mutations, which is what a disposable database is for.

---

## 12. What is requested

1. **Codex independent implementation re-review** of this remediation.
2. **A separately reported Codex security-focused re-review** of the same.

Both are asked to verify specifically that the conditions in decision record §8
were implemented — the provider binding of the completion claim, and the seven
rotation-integrity properties — rather than to re-read the package from the start.

**No Acceptance Authority approval of this implementation is claimed.** Peter
approved the partial-index interpretation conditionally; whether the conditions
were met is Codex's finding to make.

P3.1 OD-44 provider-binding and rotation-integrity remediation submitted for Codex independent and distinct security re-review; P3.G1 remains open and P3.2 has not started.
