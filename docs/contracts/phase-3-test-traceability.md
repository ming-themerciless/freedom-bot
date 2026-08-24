# Phase 3 acceptance and test traceability

Status: **Accepted 2026-08-13 at P3.G0.** No test in this document had been
written or run by P3.0; owning implementation packages must produce the evidence.

Revised 2026-08-13 by the P3.0 remediation. TC-BG-05 is **withdrawn** — it
asserted the wrong outcome — and replaced by TC-BG-05a…05e. TC-JOB-05 and
TC-JOB-13 are rewritten against the corrected N-43. New: TC-AUTH-12, TC-AUD-09…14,
TC-MIG-14…16, TC-CAP-08…11, TC-JOB-15, TC-JOB-16, TC-BG-15. No test is removed
except the one that was wrong, and its replacement is larger than it was.

Amended 2026-08-14 by the OD-44 remediation, by **addition only**: TC-AUTH-13
(the durable completion binding) and TC-AUTH-14 (the migration 0009 rehearsal)
are new in §2, and §18's coverage map gains their rows.

Amended 2026-08-17 by the P3.2 independent-review remediation, by **addition
only**: TC-MIG-19 (R-28 never calls a revoked confirmation active) and TC-MIG-20
(the database refuses a half-decided proposal under the restricted runtime role)
are new in §6, with two coverage-map rows in §18. Nothing existing was rewritten;
the case proving that a newly confirmed, non-revoked link renders as active is
retained inside TC-MIG-19.

Amended 2026-08-18 by the P3.G2 security review: TC-MIG-21 (superseded
evidence cannot authorize) is new in §6, and TC-ID-07 now includes the
concurrent different-row unlink that proves the last-identity invariant is
atomic. No existing acceptance is weakened.

Amended again 2026-08-18 by the P3.3 **effect-publication** remediation, by
**addition and one correction**: TC-JOB-27…TC-JOB-37 and TC-MIG-23 are new in
§21.4b — the cancellation of a committed effect, the recovery that replaces the
reaper's two branches over one, its atomicity and idempotence, and the two check
constraints falsified rather than assumed. TC-JOB-22's claim is **corrected rather
than weakened**: it said the requeued retry produced the result as a duplicate,
and under the recovery design the job is not requeued at all, no attempt is spent,
and the result is published from the payload the commit fence made durable. No
existing acceptance is weakened.

Amended 2026-08-18 by the P3.3 **migration-rollback** remediation, by **addition
and one scope correction**: TC-MIG-24…TC-MIG-30 are new in §21.4c — the rollback
boundary of revision 0013 against a database that has processed a normal apply.
**TC-MIG-23's scope is corrected rather than weakened**: it was being read as
evidence that a populated database round-trips, and it is not — its module seeds
only `audit_events`, so it is empty-schema evidence. The case itself is unchanged
and still passes; what changed is what it is allowed to be cited for. No existing
acceptance is weakened.

Amended 2026-08-19 by the P3.3 **third migration-rollback correction**, by
**addition and one scope correction**: TC-MIG-37 is new in §21.4c — the condition
that a writer starting under the migration's *granted* `ACCESS EXCLUSIVE` lock
cannot commit until that transaction ends. **TC-MIG-32's scope is corrected
rather than weakened**: it was named and cited for that condition and proves
PostgreSQL lock-queue fairness instead, because the migration's lock request is
ungranted throughout it. The case itself is unchanged and still passes; its test
function is renamed to what it proves. No existing acceptance is weakened.

Amended 2026-08-19 by the P3.3 **fourth migration-rollback correction**, by
**strengthening one case's evidence**: TC-MIG-37's lock observation is bound to
the fence writer's own backend and transaction. As first written it accepted any
ungranted `RowExclusiveLock` on `reconciliation_jobs` and asserted only that the
request was not the migration's, so an unrelated queued session could satisfy it
while the intended writer had not yet reached the fence. The requirement the row
records is unchanged; what changed is that the committed assertions now enforce
the identity the submission's transcript showed. Falsified deterministically and
recorded in the P3.3 submission §17. No case is renamed, no case is weakened, and
no existing acceptance is weakened.

Amended 2026-08-19 by the P3.3 **fifth migration-rollback correction**, by
**addition only**: TC-MIG-38…TC-MIG-41 in §21.4c hold TC-MIG-37's own
**failure-path cleanup** to the mandatory requirement that cleanup stay bounded
and release every connection, transaction, thread and process on every
assertion-failure path. The case's `finally` block killed a surviving migration
child and then collected it with an unbounded `communicate()`, so a stall could
hang cleanup before the `alembic_version` row lock, the holder connection and the
writer thread were released. TC-MIG-37's own requirement, assertions and result
are unchanged — a passing case never exercised the defective path. Falsified
deterministically and recorded in the P3.3 submission §18. No case is renamed and
no existing acceptance is weakened.

Amended 2026-08-19 by the P3.3 **sixth migration-rollback correction**, by
**addition only**: TC-MIG-42…TC-MIG-44 in §21.4c cover the half of that same
cleanup requirement the fifth correction did not establish. Its release also
called `holding.rollback()` and `holder.close()` synchronously, with no
enforceable timeout and neither counted by the ceiling it documented, so a
blocked rollback prevented the close, the independent disposal and the writer
join from being reached at all, and a blocked close prevented the writer join.
TC-MIG-38…TC-MIG-41's requirements, assertions and results are unchanged and
TC-MIG-37 keeps every assertion it has; what is added is the two non-returning
database paths, driven by deterministic stand-ins, and the passing-path mirror.
Falsified deterministically and recorded in the P3.3 submission §19. No case is
renamed and no existing acceptance is weakened.

Amended 2026-08-18 by the P3.3 implementation re-review remediation, by
**addition only**: TC-JOB-17…TC-JOB-26 (the commit fence's races and the runtime bookkeeping) and
TC-OPS-06…TC-OPS-17 (N-24's sweep against real PostgreSQL) are new in §21, with
their coverage rows below. Two earlier claims are **corrected rather than
weakened**: N-24's evidence row said "the sweep reads `expires_at`" for a command
that could not run at all, and N-45's row credited the abandon path to TC-JOB-16
without any case proving that an abandoned attempt commits nothing. Both now name
the cases that prove them.

Amended again 2026-08-14 by the OD-44 re-review remediation, also by **addition
only**: TC-AUTH-15 (the completion's provider binding), TC-AUTH-16 (rotation-chain
integrity) and TC-AUTH-17 (migration 0009's rotation objects and its second
precondition) are new in §2, with three coverage-map rows in §18. Nothing existing was
rewritten. The OD-45 allocation of the direct-HTTP portions of TC-BG-05b/c/e to
P3.G2 is recorded in §4's rows and in the delivery plan §11; those rows are
**not** waived and remain blocking evidence at that gate.

Amended 2026-08-15 by the OD-44 session-lifetime remediation, again by **addition
only**: TC-AUTH-18 (a rotation cannot revive an expired session or extend a
login) and TC-AUTH-19 (an idle refresh cannot revive an expired session or apply
the wrong method's idle policy) are new in §2, with two coverage-map rows in §18.
Nothing existing was rewritten, and no row was removed. Both cases are evidence
for P3.G1, which remains open.

Amended 2026-08-15 by the settings-construction remediation, again by
**addition only**: TC-AUTH-19 gains sub-case (m) (a registered session number
must be an *exact* built-in `int`), and TC-STRUCT-07 (the five public settings
types are valid by construction, RAID I-10) and TC-LIM-06 (their real consumers
use the validated values) are new rows in §13 and §17. No row was rewritten or
removed. All three are evidence for P3.G1, which remains open.

Amended 2026-08-15 by the **N-23 exact-lease remediation**. This one is *not*
addition only: it corrects two clauses that the amendment above introduced and
that independent review found wrong. TC-STRUCT-07 recorded "worker
heartbeat/lease ordering" as a relationship the contracts do not state and that
the tests prove **not** enforced, illustrated by `lease_seconds=1,
heartbeat_seconds=20`. N-23's lease is a **value** of 60 seconds, not a ceiling,
so that configuration was never inside the register and the illustration was
false. TC-STRUCT-07 now requires the lease to be proved an exact value and
requires the withdrawn counterexample to be proved refused; TC-LIM-06's worker
clause is corrected to match. **No accepted numeric value changed and no row was
removed**; the N-23 row in the numeric register is unchanged and remains the
authority. Both rows remain evidence for P3.G1, which remains open.

Amended 2026-08-16 by the **canonical settings-graph remediation**, by **addition
only**: TC-STRUCT-08 (one canonical settings graph per web process, including the
identity provider, and a completeness contract for the declared graph that is
derived independently of it) is a new row in §15. No row was rewritten or
removed. It is evidence for P3.G1, which remains open.

Amended 2026-08-16 by the **request-authority and lifecycle remediation**, by
**addition only**: TC-STRUCT-10 (production request code holds the objects the
factory accepted and reads nothing from `app.state`) and TC-STRUCT-11 (the ASGI
lifecycle owns the composition's process-lifetime resources, on a normal shutdown
**and on a refused startup**, and a partially constructed composition releases an
owned engine) are new rows in §15. No row was rewritten or removed.

Amended 2026-08-16 by the **P3.G1 security-review remediation**, by **addition
only**: TC-BG-16 (one credential shares one N-32 per-account assertion budget
across source addresses, a refused assertion spends it, and an unresolved
credential is refused identically so the budget is not an account-existence
oracle) and TC-BG-17 (N-33's per-grant attempt counter advances durably against a
matched non-live grant from several source addresses and refuses the sixth) are
new rows in §4. **§18 is unchanged**: it maps the delivery plan's §11 rows, and
the rate-limit cases have never had one — TC-BG-11 does not appear there either —
so adding one would have invented an accepted requirement row rather than
recording evidence. TC-BG-11's existing per-address
scope is unchanged and remains as written; the two new rows are the *second*
halves of N-32 and N-33 that it never covered. TC-LIM-06's account-budget clause
is unchanged and now names TC-BG-16 as its route-consumer evidence. No row was
rewritten or removed and no accepted numeric value changed. Both are evidence for
P3.G1, which remains open.

Amended 2026-08-24 by the **P3.5 supervised-session remediation**, by **addition
only**: TC-BG-18 (every *counted* break-glass refusal writes exactly one
`auth.emergency.refused` event carrying the correlation reference the caller was
shown), TC-BG-19 (N-32's issuance and assertion budgets are separate, and a
cancelled ceremony no longer spends the verification budget), TC-BG-20
(`auth.logout` records the authority derived from the persisted authentication
method, for every session class the platform can create) and TC-BG-21 (a refused
redemption is classified `consumed` / `expired` / `invalidated` / `unknown` with
the grant record id, while the four remain one indistinguishable answer to the
caller) are new rows in §4; TC-OPS-18 (`/healthz` reports the identity provider
from a bounded, unauthenticated, side-effect-free probe rather than a literal) is
a new row in §21. Every one of them answers a finding the supervised session
raised — S-5, S-7, S-6, S-9 and S-4 respectively — and **not one was found by the
existing suite**, which is why each is written against the real routes and the
real adapter rather than against the service alone. TC-BG-11's per-address scope
is unchanged in substance and now exercises R-08 rather than R-07, because after
the N-32a split R-07 no longer spends the assertion budget it was asserting on.
No row was rewritten or removed; one accepted numeric register gains N-32a, which
is recorded in the numeric policy register and **pending maintainer acceptance**.

Amended 2026-08-16 by the **test clock-authority remediation**, by **addition
only**: TC-STRUCT-08 gains a clause requiring the cases that write
`oauth_transactions` and `webauthn_challenges` rows to derive the row's creation
and its expiry from **one** clock, and requiring a regression that fails against a
clock captured outside the operation. No row was rewritten or removed, no accepted
value changed, and no production behaviour is in scope. It is evidence for P3.G1,
which remains open.

Amended again 2026-08-16 by that remediation's **independent implementation
re-review**, by **addition only**: the clause above described the absence of a
module-level clock as asserted over the AST, and no such assertion existed. It now
does — TC-STRUCT-08 gains a second clause requiring an AST regression over the
module itself — and the clause is stated below rather than the earlier wording
left standing as a claim. No row was rewritten or removed, no accepted value
changed, and no production behaviour is in scope. P3.G1 remains open.

Amended a third time 2026-08-16 by the **independent re-review of that AST
regression**, by **addition only**: the clause above says lambda bodies are
deliberately not walked, and offered "they run when a case calls them" as the
reason. That is true of a stored lambda and false of one invoked where it is
written — `NOW = (lambda: datetime.now(timezone.utc))()` runs its body during the
import and was reported clean. TC-STRUCT-08 gains a clause **superseding** the
lambda-body wording: an invoked lambda's body is import-time code and must be
walked, while a stored, returned or passed lambda's body must remain excluded.
The earlier wording is left in place and marked superseded rather than edited. No
row was rewritten or removed, no accepted value changed, and no production
behaviour is in scope. P3.G1, RAID I-09 and RAID I-10 remain open.

Amended a fourth time 2026-08-16 by the **independent re-review of that lambda
correction**, by **addition only**: the clause above requires an invoked lambda's
body to be walked and states that such a lambda is recognisable where it is
written, without resolving a name. The detector recognised only `ast.Lambda` and a
chain of `ast.Call`, so `NOW = (reader := lambda: datetime.now(timezone.utc))()`
and its curried form `NOW = (factory := lambda: lambda: datetime.now(timezone
.utc))()()` — both of which execute their bodies during the import, and neither of
which requires a name to be resolved — were reported clean. TC-STRUCT-08 gains a
clause **superseding** the recognition half of the previous clause: the walk must
look **through** a named expression in a callable position, because `(reader := L)`
answers the very object it binds to the call standing beside it. The previous
wording is left in place and marked superseded rather than edited. No row was
rewritten or removed, no accepted value changed, the invariant is not narrowed, and
no production behaviour is in scope. P3.G1, RAID I-09 and RAID I-10 remain open.

**No §18 or §19 row is amended, and none is added.** The delivery plan's §11
table and the implementation plan's §12 mandatory-test list contain no
process-lifecycle or startup-refusal requirement for these rows to hang from, and
inventing one would be an edit to an accepted requirement set rather than a
traceability entry. TC-STRUCT-10 and TC-STRUCT-11 are evidence for P3.G1 and for
RAID I-09 and I-10, all three of which remain open.

Package: P3.0 · Owner: Claude · Implemented by the owning package in each row.

This expands every acceptance criterion and mandatory-test row in
`docs/review/phase-3-delivery-plan.md` §11 and implementation plan §12 Phase 3
into named test cases or parametrized groups. **No row from either source is
removed**; `not applicable` appears nowhere, because nothing was found to be
inapplicable.

## 1. Conventions

| Prefix | Subject | Typical level |
|---|---|---|
| `TC-AUTH` | OAuth flow | service + direct HTTP |
| `TC-SESS` | Sessions | service + direct HTTP |
| `TC-BG` | Break-glass | service + direct HTTP + CLI |
| `TC-ID` | Accounts and external identities | unit + real PostgreSQL |
| `TC-MIG` | Migrations | real PostgreSQL |
| `TC-CAP` | Capability resolution and mappings | service + direct HTTP |
| `TC-OBJ` | Object-level authorization | service + direct HTTP |
| `TC-ACC` | `character_access` invariants | real PostgreSQL |
| `TC-JOB` | Durable jobs | real PostgreSQL, concurrency, restart |
| `TC-AUD` | Audit | real PostgreSQL + runtime role |
| `TC-SEC` | Web security controls | direct HTTP |
| `TC-LIM` | Bounds and limits | direct HTTP + proxy parity |
| `TC-OUT` | Provider outage | service with a faulted double |
| `TC-VM` | View-model contracts | unit |
| `TC-STRUCT` | Structural absence/equality guards | unit, AST/route introspection |
| `TC-UI` | Templates, keyboard, focus, responsive | browser automation |
| `TC-PERF` | Measured performance | staging, supervised |
| `TC-OPS` | Operational procedures | supervised rehearsal |

**Evidence classes**, following the discipline the visual handoff established:

| Class | Meaning |
|---|---|
| `automated` | Runs in the committed suite on every change |
| `automated (database)` | Requires disposable PostgreSQL; `database` marker |
| `supervised` | A maintainer runs it and records the result |
| `staging` | Requires the staging environment, which does not exist yet |
| `real-device` | Requires Peter's own hardware |
| `assistive-technology` | Requires a screen reader; **not yet planned or scheduled** |

**Role matrix `[MATRIX]`** means the test is parametrized over all seven caller
states of route contract §3.1 — `U`, `N`, `M`, `C`, `A`, `CA`, `BG` — asserting
the exact expected status for each, and asserting that a refusal changed no state
and wrote no success audit event.

The eighth caller state, `AC` (continuity-scoped administrator), has no matrix
column by design: every cell's `BG` value applies to it unchanged (route contract
§3.3). It is not left to that rule alone — **TC-CAP-09 re-runs the entire
inventory as `AC` and asserts cell-for-cell equality with the `BG` column**, so a
route that drifts apart from the rule fails a test rather than passing a reading.

## 2. Authentication — P3.1

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-AUTH-01 | `oauth_start` mints a transaction, sets the host-only cookie, and redirects to Discord with exactly N-03 scopes and N-02 redirect | direct HTTP | automated |
| TC-AUTH-02 | Callback with a mismatched `state` is refused; no session row is created | direct HTTP | automated (database) |
| TC-AUTH-03 | Callback without the transaction cookie is refused, even with a valid `state` | direct HTTP | automated (database) |
| TC-AUTH-04 | Replaying a consumed transaction is refused; the second attempt matches zero rows | service | automated (database) |
| TC-AUTH-05 | A transaction older than N-04 is refused | service | automated (database) |
| TC-AUTH-06 | Return-target parametrization: `//evil.example`, `https://evil.example`, `/\evil`, `javascript:`, a path not on the allowlist, and a valid path — only the last redirects | direct HTTP | automated |
| TC-AUTH-07 | **PKCE verifier storage.** The stored value is ciphertext: no column of `oauth_transactions` contains the verifier's plaintext or its SHA-256 (the second assertion is what would have caught the contradicted contract), and the plaintext appears in no response, log line or audit payload | service + database | automated (database) |
| TC-AUTH-12 | **PKCE verifier recovery is bound and single-use.** (a) The callback recovers the original verifier and completes the exchange; (b) the same ciphertext moved to another transaction row fails to decrypt, raising rather than returning a value; (c) after consumption the ciphertext columns are null and a second callback recovers nothing and is refused; (d) two concurrent callbacks yield exactly one exchange | service + real PostgreSQL concurrency | automated (database) |
| TC-AUTH-08 | **Non-member callback creates no session** and answers `403` with VM-02 (ADR 0004's rejection step) | direct HTTP | automated (database) |
| TC-AUTH-09 | N-18 limits: the 11th start and the 21st callback from one source address in 10 minutes are refused | direct HTTP | automated (database) |
| TC-AUTH-10 | The rate limiter counts across processes: two application instances sharing one database enforce one budget | service | automated (database) |
| TC-AUTH-11 | Login and refusal both write exactly one audit event with a correlation ID and no token, code, state or verifier | service | automated (database) |
| TC-AUTH-13 | **The durable completion binding (OD-44).** (a) one consumed transaction produces exactly one bound session, one claim and one success audit; (b) a **direct** `complete()` call holding a genuinely verified identity but an unknown, unconsumed, already-claimed or mismatched transaction id is refused with no session, token grant, account or success audit — the case route ordering cannot cover; (c) a replayed callback and a second direct completion after a successful login each add no second session or success audit; (d) two concurrent claims, and two concurrent whole completions, produce one winner and one refusal under a barrier rendezvous with no timing sleep; (e) with the application bypassed entirely, the database refuses an unbound `discord_oauth` session, a bound WebAuthn or recovery-grant session, a second completion session for one transaction, a session naming a nonexistent transaction and a claim on a transaction never consumed, and refuses to delete a transaction a session still names; (f) a provider failure at either call after consumption leaves the transaction consumed-and-unclaimed with no session, and the process-death seam leaves the same state with the retried callback refused at the consumption; (g) an injected failure at each of the six writes inside the completion transaction, and a failure between the last statement and the commit, each roll the whole completion back and release the claim; (h) WebAuthn and recovery-grant session creation is unchanged, and N-08 rotation carries the binding forward without a second claim | service + direct HTTP + real PostgreSQL concurrency and constraints | automated (database) |
| TC-AUTH-14 | **Migration 0009 rehearsal.** Upgrade adds the columns, foreign key, unique index and check constraint; downgrade drops them and keeps every session row; the re-upgrade **refuses** while unbindable `discord_oauth` sessions exist, naming the count and the remedy and leaving the database at 0008; after the remedy it succeeds with the binding empty. The binding foreign key is asserted `RESTRICT` from the catalogue | migration + real PostgreSQL | automated (database) |
| TC-AUTH-15 | **The completion is bound to the transaction's recorded provider (OD-44 §8.1).** (a) a consumed Discord transaction cannot be completed with another provider's verified identity and tokens, and a transaction recorded for another provider cannot be completed with a Discord result — both directions; (b) consuming transaction A authorizes neither another provider's result for A nor A's result for another provider's transaction B; (c) the matching provider still completes, claims once and binds the session, so the predicate refuses a mismatch and nothing else; (d) a provider-mismatched completion leaves **no** account, external identity, membership projection, token grant, session or success audit, leaves the transaction consumed-and-unclaimed, and writes exactly one `auth.login.refused` event at the existing boundary — carrying a reason category and nothing else; (e) the claim statement itself refuses a foreign provider key and accepts the recorded one; (f) `VerifiedCompletion` refuses to hold two providers' halves, an adapter refuses to verify another provider's tokens, and the real Discord adapter stamps its own key on the token result | service + repository + real PostgreSQL | automated (database) |
| TC-AUTH-16 | **The rotation chain is linear and does not cross (OD-44 §8 condition).** (a) an OAuth chain of two rotations carries one binding, revokes each predecessor and leaves exactly one live session, and a break-glass rotation stays unbound to any transaction; (b) a second rotation of one predecessor, a revoked predecessor, an unknown predecessor, another account's and another authentication method's are each a typed `SessionRotationRefused` that revokes nothing and creates nothing; (c) with the application bypassed, the database refuses a second successor, a rotation that changes account, method or OAuth binding, and a row labelled a rotation in order to reuse another login's transaction — while the root-session unique index still refuses the direct second root; (d) two concurrent rotations under a barrier rendezvous produce one successor and one refusal, with one live descendant and no branch, and no test sleeps; (e) no creation path accepts a rotation label, asserted from the signatures | service + repository + real PostgreSQL concurrency and constraints | automated (database) |
| TC-AUTH-17 | **Migration 0009's rotation objects.** The unique rotation index and both composite rotation foreign keys appear on upgrade and disappear on downgrade; each key is `RESTRICT` and carries exactly its declared referencing and referenced columns, read from `pg_constraint`; the index is unique and scoped `WHERE rotated_from_session_id IS NOT NULL`, read from `pg_indexes`; and a pre-existing branched chain makes the upgrade **refuse** with the count and the remedy, leaving the database at 0008 until the remedy is applied | migration + real PostgreSQL | automated (database) |
| TC-AUTH-18 | **A rotation cannot revive an expired session or extend a login (N-07, N-15).** (a) an idle-expired but still unrevoked OAuth session, and idle-expired WebAuthn and recovery-grant sessions, cannot be rotated from a `SessionRecord` resolved while they were valid — the stale-record path, which never re-resolves the token; (b) the successor inherits the predecessor's `absolute_expires_at` exactly and its idle window is clamped to that inheritance, so a chain of rotations carries the one bound the login at its root set, for ordinary and break-glass chains alike; (c) at the absolute boundary the clamp holds and one second past it the successor cannot itself be rotated; (d) the absolute predicate is made observable by dropping `ck_sessions_idle_within_absolute` inside a rolled-back transaction and presenting the locked read with the row the constraint forbids; (e) two concurrent rotations under a barrier rendezvous still produce one successor and one typed refusal, and the survivor carries the root's bound; (f) every refusal leaves the predecessor row, its revocation fields and both expirations unchanged and writes no successor and no rotation audit | service + repository + real PostgreSQL concurrency and constraints | automated (database) |
| TC-AUTH-19 | **An idle refresh cannot revive an expired session or apply the wrong method's idle policy (N-06, N-15).** (a) a valid OAuth session refreshed inside its window receives N-06's sixty minutes clamped to its **unchanged** absolute bound, and valid WebAuthn and recovery-grant sessions receive N-15's fifteen — not the ordinary duration; (b) repeated refreshes converge on the absolute bound, never change it and never pass it, and the session still dies there; (c) a stale OAuth record, and stale WebAuthn and recovery-grant records, cannot refresh an idle-expired but unrevoked row; an absolute-expired session and a revoked session are likewise refused; (d) refreshes exactly at the idle bound and exactly at the absolute bound are refused, with the same record accepted one microsecond earlier, so both comparisons are strict; (e) the absolute predicate is made observable by the same rolled-back constraint drop TC-AUTH-18d uses; (f) every refusal leaves the **complete** session row byte-identical and writes no audit and no successor; (g) the service raises the typed `SessionTouchRefused` whenever the conditional write affects no row, so a zero-row update is never reported as success; (h) **rewritten 2026-08-15 (second session-lifetime review).** The previous (h) asserted the service signature and a repository refusal of a *mismatched* `expected_auth_method`, and concluded that the ordinary window could not reach a break-glass row from either layer. The mismatch case never exercised the bypass, which was the row's **correct** method supplied beside the ordinary duration, and the conclusion was therefore unsupported; that test has been replaced rather than retained. (h) now establishes, through the repository alone with no service in front of it: a direct touch of a Discord OAuth row applies N-06; a direct touch of a WebAuthn row and of a recovery-grant row applies N-15; `SessionRepository.touch()` takes `(session_id, now)` and no duration, deadline or authentication-method argument under any spelling; the exact former pairing raises `TypeError` and leaves the row unchanged, while the supported call still refreshes it; the repository cannot be constructed without an idle policy; a policy that omits a method, repeats one, or carries a non-positive window is refused where it is built; the configured policy is N-06/N-15 as the numeric register states them; and a row whose method the policy does not govern is refused rather than defaulted, proved by dropping `ck_sessions_auth_method` inside a rolled-back transaction; (i) a concurrent refresh and revocation of one session leave it revoked in both interleavings, with a losing refresh typed-refused rather than reviving it; (j) **added 2026-08-15 (third session-lifetime review).** (h) closed the *call* boundary while leaving the *construction* boundary open: `SessionIdlePolicy` was a frozen dataclass whose generated constructor took `tuple[tuple[AuthMethod, timedelta], ...]`, and the complete, duplicate-free, positive mapping that gives every method N-06's window was accepted, so a repository built with it applied sixty minutes to persisted break-glass rows. (j) establishes, against the new construction boundary: the finding's exact all-ordinary mapping, the subtler variant assigning the ordinary window to only one break-glass method, and every other spelling of "hand me the mapping" (positional, keyword, dict, no argument) are refused by a constructor that does not exist, before any database work; the finding's full four-line sequence — build the policy, construct a repository with it, touch a break-glass row — halts at line one with the row unchanged, and the supported call then applies N-15 to the same row; the class's only public callables are `from_settings` and `for_method`, `from_settings` takes `settings` alone, and no dataclass machinery survives to regenerate a constructor; a built policy refuses attribute assignment and deletion; classification holds for every accepted configuration, including `idle_minutes` **below** `emergency_idle_minutes`, both in the mapping and through the conditional write against real PostgreSQL; the composition root's repository and service hold the **same policy instance** (`is`, across two `services()` calls), the service constructor requires `idle_policy` with no default, and what a login's bounds are created with equals what a refresh applies for each method; a non-positive configured window is refused at `from_settings`; the partial and duplicated mappings are refused by the derivation guard, called directly and reported as unreachable from any supported API; and `for_method` refuses anything that is not an `AuthMethod` rather than defaulting it to the ordinary window; (k) **added 2026-08-15 (idle-policy-construction review).** (j) closed the policy's constructor while leaving three counterexamples: a directly constructed `SessionSettings` with `emergency_idle_minutes=60` was accepted and made the derived policy give both break-glass methods sixty minutes (F1); the refresh statement was generated from the policy's public overridable `__iter__`, so a subclass inheriting the supported factory replaced the SQL's mapping while `for_method()` still reported fifteen minutes (F2); and `SessionService` accepted a policy beside the repository without requiring identity, so a graph could create sessions under one window and refresh them under another (F3). (k) establishes, against the revised model: every register bound is refused at `SessionSettings` construction in both directions with the ceiling and 1 accepted, and `emergency_idle_minutes` boundary 15 accepted and 16 refused; the F1 sequence — build the settings, construct a repository, refresh a persisted break-glass row — halts at line one with the row byte-identical, and the supported construction then applies N-15 to that same row; `SessionIdlePolicy` no longer exists, `SessionPolicy` has no `__iter__` and holds five fixed roles, and the repository's constructor takes a connection and settings alone; the parameters the conditional write is bound with classify (`discord_oauth`→N-06, `webauthn`/`recovery_grant`→N-15) rather than repeating one window; a `SessionPolicy` subclass overriding `__post_init__` and `idle_for` is genuinely forged and cannot be given to a repository under any keyword, and the persisted break-glass row still receives N-15 from PostgreSQL; a `SessionSettings` subclass whose field answers 15 then 60 is read exactly once, so the validated value is the value in the SQL, and one that answers 60 always is refused; a duck type is refused; the former mismatch sequence is executed with two different valid configurations and no keyword carries the second, with `service.policy is repository.policy` afterwards; the composition holds no policy of its own and every graph's service and repository share one object; creation bounds equal refresh bounds per method against the database; all three construction sites (composition, operator tool, tests) use the one model and the tool carries no second bounds source; and an authentication method with no explicit classification refuses — proved twice, once through the real guard given a synthetic enum with an unclassified member, and once by removing an entry from the production table and observing `SessionRepository` construction raise `UnclassifiedAuthMethod`, with restoration asserted afterwards; (l) **added 2026-08-15 (session-bounds-construction review).** (k) closed the construction boundary while leaving the two gates holding different *type* semantics for the same numbers: `SessionSettings.__post_init__` required an actual `int` excluding `bool`, while the derived-policy gate restated the rule as `value < 1` and `value > ceiling` only, and `float("nan")` makes both comparisons false — so a non-finite `max_sessions_per_account` survived derivation and `len(live) >= maximum` was false for every live-session count, leaving N-66 inoperative. Codex's implementation review (F1) and its distinct security pass (S1) report this one defect from two perspectives. (l) establishes, against the shared definition: `dataclasses.replace()` and direct `SessionPolicy` construction each refuse `nan`, `inf`, `-inf`, `10.0`, a fractional float, `True` and `False` as `max_sessions_per_account`, and the accepted maximum is an `int` so the enforcement comparison is a real one; a **genuine** `SessionSettings` subclass — inheriting `__post_init__`, so ordinary construction observes the valid stored integer — whose single later derivation read answers NaN is refused, with the attribute asserted to be read exactly once during derivation; the same lying shape is refused for a representative wrong type on four other registered fields (`idle_minutes=60.0`, `emergency_idle_minutes=15.0`, `absolute_hours=True`, `emergency_absolute_minutes=nan`), each of which passed both of the reviewed implementation's ordering comparisons, proving the validator is shared and not special-cased to N-66; every field in `SESSION_CEILINGS`, parameterised from the register rather than restated, accepts `1` and its exact ceiling and refuses `0` and ceiling-plus-one at settings construction, and every field the policy carries holds the same bounds at the derivation boundary with the stored value checked in the policy's own unit; environment loading with six invalid session variables raises **one** `ConfigurationError` naming all six and containing none of the recognisable sentinel values supplied, with an in-register control case accepted; and, against the disposable real PostgreSQL fixture, TC-SESS-08b; (m) **added 2026-08-15 (settings-construction review).** (l) made both gates share one definition and left that definition stating the type rule as `isinstance(value, int) and not isinstance(value, bool)`, which refuses `bool` and every float and accepts **every other subclass of `int`**. An `int` subclass may override `__lt__`, `__gt__`, `__le__` and `__ge__`, and Python gives the right-hand subclass's reflected comparison priority, so `len(live) >= maximum` is answered by the subclass: `dataclasses.replace(VALID_SESSION_SETTINGS, max_sessions_per_account=LyingInt(10))` survived settings construction **and** `SessionPolicy.derive()`, and `_enforce_session_limit` then saw false for every live-session count — N-66 inoperative again, with no `object.__new__`, no frozen-object mutation, no private helper, no forged policy and no skipped `__post_init__`. The accepted rule is the exact built-in type, `type(value) is int`. (m) establishes: for **every** field in the register, a comparison-overriding `int` subclass carrying that field's own accepted number is refused at direct `SessionSettings` construction and at `dataclasses.replace()`, with the subclass first shown to satisfy the old predicate and to answer `False` to every comparison; the one shared definition refuses it for every field while still accepting the plain integer, so the rule refuses a type and not a value; `SessionPolicy(...)` and `replace()` refuse it as `max_sessions_per_account`, and the four duration fields refuse it outright because a value that is not a `timedelta` never reaches a comparison; a genuine `timedelta` subclass whose `total_seconds()` returns a comparison-overriding float is reduced to an exact `int` before the register sees it, proved by an out-of-register lying duration being refused and an in-register one accepted; `SessionPolicy.derive()` refuses a genuine `SessionSettings` subclass — inheriting `__post_init__`, so construction observed the valid stored integer — whose single later read answers the subclass, for every field the policy carries, with the derivation read count asserted as exactly one; `SessionRepository` cannot be constructed from such settings at all, so the reproduction halts before any statement is compiled; a falsification control reconstructs the old predicate and shows it **admitting** the value and `10 >= maximum`, `100 >= maximum` and `10_000 >= maximum` all false; and eleven logins against the disposable real PostgreSQL fixture leave exactly ten live sessions with the oldest durably revoked as `session_limit` and one audit event carrying `limit = 10` | service + repository + real PostgreSQL concurrency and constraints | automated (database) |

## 3. Sessions — P3.1

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-SESS-01 | The cookie value is not the session id; the stored value is its hash | unit | automated |
| TC-SESS-02 | Session id rotates on login; the pre-login cookie is dead immediately | direct HTTP | automated (database) |
| TC-SESS-03 | A detected capability change rotates the session and revokes the old row with reason `rotation` | service | automated (database) |
| TC-SESS-04 | Idle expiry (N-06) and absolute expiry (N-07) both refuse; an idle refresh never extends past the absolute bound | service | automated (database) |
| TC-SESS-05 | Logout revokes server-side, deletes the OAuth token record (N-11) and clears the cookie; the old cookie then fails | direct HTTP | automated (database) |
| TC-SESS-06 | A role revoked at the provider stops granting capability within N-09 on reads and immediately on mutations | service | automated (database) |
| TC-SESS-07 | C-07 revokes every session for an account; each is refused on its next request | CLI + HTTP | automated (database) |
| TC-SESS-08 | N-66: creating the 11th session revokes the oldest and audits it | service | automated (database) |
| TC-SESS-08b | **Added 2026-08-15 (session-policy numeric-validation remediation).** N-66 proved durable, and proved to be the *configured* integer. Against the disposable real PostgreSQL fixture: with the accepted maximum of ten, ten live sessions leave nothing revoked and no audit event, and the eleventh durably revokes exactly the oldest with reason `session_limit` — asserted from a fresh connection after commit — leaving the live population at ten and writing exactly one `auth.session.revoked` event naming that session with `limit = 10`; and with a **stricter** accepted maximum of three (S-10 permits tightening), a second composition built from that configuration holds the live population at exactly three across two further logins, revoking the two oldest in order with `limit = 3`, so the enforced bound is the configured integer and not the ceiling or another default. This is the control the NaN defect disabled: a non-finite maximum makes `len(live) >= maximum` false for every count, so the same sequences produced eleven live sessions, no revocation and no audit event | service + real PostgreSQL | automated (database) |
| TC-SESS-09 | Cookie attributes are exactly N-05, including the `__Host-` prefix when secure | direct HTTP | automated |
| TC-SESS-10 | The CSRF token is derived, not stored: no column holds it, and it changes when the session rotates | unit + database | automated |

## 4. Break-glass — P3.1

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-BG-01 | WebAuthn assertion succeeds for an enrolled credential and creates a session with N-15 bounds and `auth_method='webauthn'` | service | automated (database) |
| TC-BG-02 | **Break-glass succeeds while the Discord provider is entirely unavailable** (faulted double refusing every call) | service | automated (database) |
| TC-BG-03 | A decreasing `sign_count` refuses the login and audits it | service | automated (database) |
| TC-BG-04 | `[MATRIX]` A break-glass session is refused on every Council route and every import route (N-65), and resolves to exactly `{platform_administrator}` even when the same account's Discord roles include Council | service + direct HTTP | automated (database) |
| ~~TC-BG-05~~ | **Withdrawn.** It asserted that a break-glass mapping change *succeeds* and checked only the emergency session's own capability set. That is the wrong question: the attack arranges authority for a later ordinary session, and this test would have passed while the platform was escalatable. Replaced by TC-BG-05a…05e | — | — |
| TC-BG-05a | **Direct service:** for each of `guild_council`, `dm`, `character_owner`, `guild_member`, a continuity-scoped caller's mapping create is refused `emergency_scope_refused`; no row is written; a `role_capability_mapping_events` refusal row **is** written naming the attempted capability | service | automated (database) |
| TC-BG-05b | **P3.G1 service/constraint; P3.G2 direct HTTP.** The direct-HTTP portion issues the same parametrization straight to R-33 with a break-glass session, **without ever rendering R-32**, and requires `403` with no change. Repeat for R-34 against an existing `guild_council` mapping and for R-38. The HTTP portion is mandatory P3.G2 evidence against the real P3.2 routes, not P3.G1 evidence and not waived | service + direct HTTP | automated (database) |
| TC-BG-05c | **The sequence, end to end.** P3.G1 proves the service/database sequence: break-glass session → create the one mapping it *is* allowed (`platform_administrator` for role X) → ordinary Discord login as a member holding role X → resolved capability set is `{platform_administrator}` with administrator scope `emergency_continuity`. P3.G2 must then prove by direct HTTP that every Council route, every import route and R-38 refuse, attempt R-33 for `guild_council` and assert refusal, and assert `uq_snapshot_imports_applied_input` shows no import. **No sequence of BG mapping changes followed by ordinary login yields Council or import authority** | service + direct HTTP | automated (database) |
| TC-BG-05d | **Constraint, not code:** an `INSERT` issued directly against the database with `created_under_scope = 'emergency_continuity'` and `capability = 'guild_council'` is refused by the check constraint, with the runtime role and with the owner role. The application is bypassed entirely | real PostgreSQL constraint | automated (database) |
| TC-BG-05e | **Ratification is the only exit, and it is one-way.** P3.G1 proves the service/database transition, rotation and one-way trigger. P3.G2 proves through the real R-38 route that a full-scope administrator on an ordinary-provider session can ratify and that `BG` or `AC` receives `403`. Both portions are required before P3.G2 closes | service + direct HTTP | automated (database) |
| TC-BG-15 | **Account-attributed emergency audit.** With the Discord provider entirely faulted, a break-glass login and an allowed mapping repair each commit their state change and their audit event in one transaction, with `actor_platform_account_id` set and `actor_discord_user_id` null. This is the end-to-end proof that the constraint swap of schema §6.3 delivers the availability half of OD-43 | service | automated (database) |
| TC-BG-06 | Recovery grant: C-01 stores only a hash; the printed token appears in no row, log or audit payload | CLI + database | automated (database) |
| TC-BG-07 | Recovery grant replay is refused; expiry at N-14 is refused; a grant with a different `purpose` is refused | service | automated (database) |
| TC-BG-08 | Two concurrent redemptions of one grant: exactly one session is created | real PostgreSQL concurrency | automated (database) |
| TC-BG-09 | Issuing a second grant invalidates the first in the same transaction (N-61) | service | automated (database) |
| TC-BG-10 | **No HTTP route can issue a grant or enrol a credential** — route inventory contains neither, and a constructed request to the plausible paths is `404` | structural + HTTP | automated |
| TC-BG-11 | N-32/N-33 limits refuse the 6th assertion and the 4th recovery attempt per window | direct HTTP | automated (database) |
| TC-BG-12 | Every attempt and outcome is audited with the credential/grant **record id**, account, time, source and correlation — and never a secret | service | automated (database) |
| TC-BG-13 | Lost response after consumption: the grant is spent, one session exists, the audit shows exactly one consumption | service | automated (database) |
| TC-BG-14 | C-03 refuses to retire a credential that would leave the protected account with fewer than two (N-13) | CLI | automated (database) |
| TC-BG-16 | **Added 2026-08-16 (security-review remediation; evidence wording corrected at P3.G1 acceptance).** N-32's *per-account* half at the route: ten refused assertions for one enrolled credential, each from a different source address so the per-address budget never decides, are all `403 invalid`; the eleventh is `429 rate_limited` with `Retry-After`; the table holds exactly one account bucket carrying all eleven and no session exists. The budget is therefore consumed in a transaction the refusal does not roll back. **And it is not an oracle:** the same sequence against an invented credential id produces the same statuses and coarse error codes at the same attempts, spending an equivalent per-credential budget whose bucket carries a keyed digest rather than the credential id. Correlation identifiers intentionally differ per request, and literal response-body or `Retry-After` equality is not claimed | direct HTTP | automated (database) |
| TC-BG-17 | **Added 2026-08-16 (security-review remediation).** N-33's *per-grant* half, against a grant the token **matches** but that is no longer live: five attempts from five different source addresses each advance the stored `attempt_count` durably after their refusal rolled back, the sixth is refused `rate_limited` with the cap's refusal audited and no session created, and a successful redemption spends one attempt of the same counter | direct HTTP | automated (database) |
| TC-BG-18 | **Added 2026-08-24 (supervised-session finding S-5 / security finding S1).** Every *counted* break-glass refusal writes exactly one `auth.emergency.refused` event whose correlation id is the reference the caller was shown: R-07's issuance limiter, R-08's per-address limiter, R-08's per-account and per-credential budgets, R-08's malformed body, R-09's per-address limiter, R-09's empty token, and R-09's per-grant cap. The per-account refusal names the protected account; the per-credential refusal names neither an account nor the presented id. One attempt produces one row whether the reason was recorded by the route or described by the service. The malformed-body and empty-token refusals are moved **after** their limiter so that they are counted before they are recorded, which is what makes recording them safe | direct HTTP | automated (database) |
| TC-BG-19 | **Added 2026-08-24 (supervised-session finding S-7 / security finding S3).** N-32a: challenge issuance and assertion verification hold separate per-address budgets. The eleventh issuance from one address is `429`; the sixth verification from one address is `429`; and ten complete issue-then-verify pairs from one address show every issuance served with the *assertion* budget deciding — so a cancelled authenticator prompt no longer spends the budget the next real attempt needs | direct HTTP | automated (database) |
| TC-BG-20 | **Added 2026-08-24 (supervised-session finding S-6 / security finding S2).** `auth.logout` records `platform_administrator` for both break-glass methods, named separately, with the platform account attributed and no Discord user — the shape migration 0006's constraint swap exists to permit — and still records `guild_member` for an ordinary Discord session whether that person also holds Council or administrator capability. The attribution is looked up from an explicit table keyed on the **persisted** `sessions.auth_method`; a method absent from that table fails at import, proven over a synthetic enum because `AuthMethod` is closed | service + database | automated (database) |
| TC-BG-21 | **Added 2026-08-24 (supervised-session finding S-9 / security finding S4).** A redemption the single conditional `UPDATE` refuses is classified read-only, in the same transaction, into `consumed`, `expired`, `invalidated` or `unknown`, with the non-secret grant record id on the first three and no reference on the last. All four produce a byte-identical caller response — same status, same failure code, differing only in the per-request correlation reference. The classification consumes nothing, writes nothing and does not advance the attempt counter, and neither the token nor its hash reaches the payload | direct HTTP + service | automated (database) |

## 5. Identity, accounts and linking — P3.1/P3.2

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-ID-01 | An account survives unlinking a provider: sessions, `character_access` and audit attribution all still resolve | service | automated (database) |
| TC-ID-02 | Sessions and `character_access` reference account ids only; no query in the web module filters by a Discord snowflake | structural + service | automated |
| TC-ID-03 | `(provider_key, subject)` uniqueness is enforced by the database, including against a **retired** row | real PostgreSQL constraint | automated (database) |
| TC-ID-04 | Retiring an identity keeps the row and keeps historical audit attribution readable | service | automated (database) |
| TC-ID-05 | **Structural:** `external_identities` has no display-name, username or email column, and no code path links accounts by any name-like value | AST/schema introspection | automated |
| TC-ID-06 | Name-collision parametrization: identical usernames, case variants, NFC/NFD variants, homoglyphs, and identical global names never merge or auto-link accounts | service | automated (database) |
| TC-ID-07 | Unlinking the last usable identity is refused; for the protected account, enrolled credentials count as the recovery route and for an ordinary member they do not; two concurrent unlinks of different identities serialize and leave one active | service + concurrency | automated (database) |
| TC-ID-08 | A forged `platform_account_id` in a grant form is ignored: the target is resolved from the selected snowflake server-side | direct HTTP | automated (database) |

## 6. Migrations — P3.1/P3.2

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-MIG-01 | Stage A backfill: every `discord_users` row yields exactly one account and one active Discord identity | real PostgreSQL | automated (database) |
| TC-MIG-02 | Control totals T1–T6 hold; a deliberately corrupted fixture makes T6 fail and aborts the migration | real PostgreSQL | automated (database) |
| TC-MIG-03 | Re-running stage A inserts nothing (idempotent), including after an injected mid-run failure | real PostgreSQL | automated (database) |
| TC-MIG-04 | `upgrade → downgrade → upgrade` for each of stages A, B and C leaves an identical schema and identical data | real PostgreSQL | automated (database) |
| TC-MIG-05 | Stage B enforces both the Discord-keyed and account-keyed unique indexes simultaneously; violating either is rejected | real PostgreSQL constraint | automated (database) |
| TC-MIG-06 | Stage C's shadow trigger keeps `discord_user_id` current for rows written by the new path, and refuses a row whose account has no active Discord identity | real PostgreSQL | automated (database) |
| TC-MIG-07 | Backup/restore rerun: dump, run the stage, restore, run again — same result | supervised, disposable database | supervised |
| TC-MIG-08 | M-2 dry run produces balanced totals; an unbalanced report refuses to proceed | service | automated (database) |
| TC-MIG-09 | M-2's C-04 run writes **no** `character_access` row and no authorization of any kind; only an R-29 confirmation does, and it does so in the same transaction as its decision | service | automated (database) |
| TC-MIG-10 | Ambiguous and unresolved proposals are not confirmable, persist across runs, and grant no access even when the browser submits a confirmation | service + direct HTTP | automated (database) |
| TC-MIG-11 | Every created link names the confirming Council member — resolved live, server-side, on the confirming request — a reason and a correlation ID, in one atomic transaction with the proposal transition and both audit events. Repeated and concurrent confirmations produce one durable effect | service + direct HTTP | automated (database) |
| TC-MIG-12 | The Sheet is never written: the read-only boundary is exercised and a write attempt through the adapter raises | service | automated |
| TC-MIG-13 | Injected audit-write failure during confirmation rolls back the grant. So do an injected grant failure, an injected proposal-transition failure and an injected commit failure: none leaves a partial link, decision, version bump or audit success | service | automated (database) |
| TC-MIG-14 | **The constraint swap round-trips.** `upgrade → downgrade → upgrade` of the revision that replaces `ck_audit_events_human_action_has_an_actor` leaves an identical schema and identical data; the downgrade restores the legacy constraint `NOT VALID`, and does so successfully **on a database that already contains account-attributed rows** — the case a validating restore would fail | real PostgreSQL | automated (database) |
| TC-MIG-15 | **Constraint inventory.** After the revision, the check constraints on `audit_events`, `snapshot_imports` and `foundry_snapshots` equal the inventory documented in schema §6.2.1 exactly: the account-aware check present, the legacy Discord-only check absent, `foundry_snapshots` unchanged, nothing extra. Guards against a later migration quietly reintroducing a Discord-only attribution rule | schema introspection | automated (database) |
| TC-MIG-16 | Control totals T7 and T8 hold; a deliberately corrupted fixture makes T8 fail and aborts the migration | real PostgreSQL | automated (database) |
| TC-MIG-17 | **Duplicate player-name keys refuse the whole C-04 run** (migration contract §7.3.1). Exact and normalized duplicates carrying different Discord names produce no confirmable proposal; row order cannot change the outcome; the refusal writes no run, so no control total can hide the duplicate; and the operator-facing message names counts only — no player name and no Discord identity | service + command | automated (database) |
| TC-MIG-18 | **C-04 needs no Google dependency in the platform runtime.** The portal's requirement and lock files name no Google package, the portal application imports none on any startup or request path, and C-04's Google import is lazy and refuses with a typed operator message when absent | import graph + dependency files | automated |
| TC-MIG-19 | **R-28 never calls a revoked confirmation active** (VM-10; migration contract §7.4, §7.5). `C-04 → R-29 confirm → R-26 revoke → R-28`: the page does not label the proposal `confirmed-and-active`, does not state that it is active now, and excludes it from the active-confirmed total while counting it in `confirmed_revoked` so the second balance still closes. The historical confirmation, its decider, its reason, its `granted_access_id` and both audit events survive intact, and the proposal cannot be decided again. Another active link on the same character or account cannot make it read as active, and a newly confirmed, non-revoked link still renders active | service + direct HTTP | automated (database) |
| TC-MIG-20 | **The database refuses a half-decided proposal, under the restricted runtime role.** A direct `UPDATE` to `confirmed` or to `rejected` with `decision_reason IS NULL` is refused by `ck_identity_link_proposals_a_decision_states_its_reason`; a blank or whitespace-only reason is refused by `ck_identity_link_proposals_decision_reason_not_blank`; an outstanding row carrying a reason is refused; and valid R-29 and R-30 transitions still succeed. Migration/metadata constraint names and expressions stay identical and the revision still round-trips | real PostgreSQL constraint | automated (database) |
| TC-MIG-21 | **A superseded evidence run cannot authorize.** After a newer C-04 run commits, R-29/R-30 refuse proposals from every older run. The service gives the stale request a typed conflict and the conditional decision update independently requires the latest run, so a newer run committed during confirmation rolls the link, decision, version bump and audits back together | service + real PostgreSQL transaction | automated (database) |

## 7. Capability and role mappings — P3.1/P3.2

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-CAP-01 | Capability comes from **role snowflakes**, never role names; a renamed role changes nothing | service | automated (database) |
| TC-CAP-02 | `[MATRIX]` Administrator does not imply Council and Council does not imply administrator, on every route in the inventory | direct HTTP + service | automated (database) |
| TC-CAP-03 | The protected bootstrap mapping cannot be updated, deleted, demoted or have `protected` cleared — refused by the database trigger with the runtime role and with the owner role | real PostgreSQL | automated (database) |
| TC-CAP-04 | No sequence of ordinary mapping changes removes administrator capability (union semantics), including inserting a conflicting mapping | service | automated (database) |
| TC-CAP-05 | A second protected mapping and a second protected account are both refused | real PostgreSQL constraint | automated (database) |
| TC-CAP-06 | Mapping changes and refusals are recorded in the append-only mapping-event table | service | automated (database) |
| TC-CAP-07 | A forged capability name or role id in a request body changes nothing | direct HTTP | automated |
| TC-CAP-08 | **Administrator scope resolution**, parametrized: authority from the protected mapping → `full`; authority only from an emergency-provenance mapping → `emergency_continuity`; authority from both → `full`; break-glass session → `emergency_continuity` whatever its mappings say | service | automated (database) |
| TC-CAP-09 | `[MATRIX]` **`AC` mirrors `BG` exactly.** The whole route inventory is re-run for a continuity-scoped ordinary-provider session and every response is asserted cell-for-cell identical to the `BG` column (route contract §3.3) | direct HTTP | automated (database) |
| TC-CAP-10 | Ratification restores full scope, and the affected sessions rotate on the detected privilege change (N-08) rather than carrying the old scope to their next request | service | automated (database) |
| TC-CAP-11 | Every mapping attempt, applied or refused, writes exactly one `role_capability_mapping_events` row carrying operation, outcome, refusal code, attempted capability, auth method, scope and correlation id | service | automated (database) |

## 8. Object-level authorization — P3.2/P3.3

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-OBJ-01 | `[MATRIX]` Every route in the inventory, for every caller state, returns exactly the documented status | direct HTTP | automated (database) |
| TC-OBJ-02 | Cross-character substitution: a member with characters A and B requesting character C gets `404`, identical to a nonexistent UUID | direct HTTP | automated (database) |
| TC-OBJ-03 | A member with several linked characters sees exactly their own set, and the default-character flag is theirs alone | service | automated (database) |
| TC-OBJ-04 | Council reach is role-derived: a Council member reads any character with **no** `character_access` row existing for them | service | automated (database) |
| TC-OBJ-05 | Job ids are worth nothing to a member: `403` is returned before the job row is read, proven by asserting no query ran | service | automated (database) |
| TC-OBJ-06 | **Denial happens without rendering:** every refusal test issues the request directly, never having fetched the page containing the control | direct HTTP | automated |
| TC-OBJ-07 | Denial responses carry no object detail: the `404` body for an inaccessible character is byte-identical to that for an absent one | direct HTTP | automated |

## 9. `character_access` invariants — P3.2

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-ACC-01 | Grant, revoke and default-change each write one atomic audit event; an injected audit failure rolls the change back | service | automated (database) |
| TC-ACC-02 | At most one active `owner` per character, enforced by the database under concurrent grants | real PostgreSQL concurrency | automated (database) |
| TC-ACC-03 | At most one active default character per **account**, enforced under concurrency | real PostgreSQL concurrency | automated (database) |
| TC-ACC-04 | Optimistic concurrency: a stale `version` is refused `409` with the current state and applies nothing | direct HTTP | automated (database) |
| TC-ACC-05 | Revocation keeps the historical row with its reason, timestamps and correlation id; re-granting inserts a new row | service | automated (database) |
| TC-ACC-06 | A blank or missing reason is refused `422` | direct HTTP | automated |
| TC-ACC-07 | Revoking the last active owner is permitted and surfaces the OD-37 unresolved-owner state rather than failing silently | service | automated (database) |

## 10. Durable jobs — P3.3

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-JOB-01 | A job is created `queued` and no work happens in the request | service | automated (database) |
| TC-JOB-02 | Two workers cannot claim one attempt (`FOR UPDATE SKIP LOCKED`), proven with two real connections | real PostgreSQL concurrency | automated (database) |
| TC-JOB-03 | Heartbeat extends the lease; a write from a worker that is not the lease owner changes nothing | real PostgreSQL | automated (database) |
| TC-JOB-04 | Process restart mid-attempt: the lease expires, the reaper requeues, a worker completes it, and **exactly one** durable effect exists | real PostgreSQL restart simulation | automated (database) |
| TC-JOB-05 | **Attempts one through exhaustion, on real PostgreSQL.** A job is claimed, its lease is expired by moving `lease_expires_at` into the past, and the reaper runs — three times. After expiry 1 and 2 the job is `queued` with `attempts` 1 then 2, `lease_owner` null and `failure_code` null, so **an expired lease is never recorded as `failed` while attempts remain** (N-23, N-43). After expiry 3 the job is `failed` with `attempts_exhausted`, `finished_at` set and `attempts = 3`. At no point is the job `running` without a live lease after the reaper has run, and at no point does a claim raise a constraint violation | real PostgreSQL | automated (database) |
| TC-JOB-06 | `completed` is impossible without a committed result row — attempted directly against the database, refused by the check constraint | real PostgreSQL constraint | automated (database) |
| TC-JOB-07 | Double-click, retry with the same request key, and two browsers all yield one job, one durable effect and one success audit event | direct HTTP + database | automated (database) |
| TC-JOB-08 | Two concurrent applies of the same input: one commits, the other returns the original receipt as a duplicate | real PostgreSQL concurrency | automated (database) |
| TC-JOB-09 | Folder change (R-41), profile-version change, snapshot change and aggregate-version change each make an outstanding preview `stale` with the correct `stale_reason`, and a confirmation then applies nothing | service + direct HTTP | automated (database) |
| TC-JOB-10 | Council role revoked between preview and apply: the apply is refused at re-resolution | service | automated (database) |
| TC-JOB-11 | Cancellation cancels `queued` immediately, `running` at the next heartbeat, and **never** a committed apply (`409`) | service | automated (database) |
| TC-JOB-12 | N-42 queue bound refuses the 6th queued job with a typed result and creates no row | service | automated (database) |
| TC-JOB-13 | **Two concurrent reapers, and no job left `running`.** Two real connections run the reaper statement simultaneously against a set of expired leases spanning `attempts` 1, 2 and 3. Assertions: each job is transitioned exactly once (one `RETURNING` row across both reapers, and `version` incremented by exactly one); the `attempts < 3` jobs are `queued` and the `attempts = 3` jobs are `failed` with `attempts_exhausted`; `attempts` is unchanged by the reaper on every branch; **no job is `running` after the pass**; and a bounded sweep of the whole table finds no job whose lease expired more than `N-23 + N-44` ago in any state. There is no "4th claim": TC-JOB-05's third expiry is where the job terminates | real PostgreSQL concurrency | automated (database) |
| TC-JOB-14 | No job payload, result, response or log line contains raw artifact bytes or Actor content beyond the bounded blocked-entry set | service + response inspection | automated |
| TC-JOB-15 | **The stranded state is unrepresentable.** A direct `UPDATE … SET state='queued'` on a job with `attempts = 3` is refused by `CHECK (state <> 'queued' OR attempts < 3)`; a direct claim of such a job matches zero rows; and `attempts` cannot exceed 3 | real PostgreSQL constraint | automated (database) |
| TC-JOB-16 | **Worker self-abandon races the reaper.** A worker that exceeds N-45 while its lease has already expired and been reaped writes nothing: its `AND lease_owner = $2` update matches zero rows, the job keeps the reaper's outcome, and no second `attempts` increment or second terminal verdict appears. Run in both orders | real PostgreSQL concurrency | automated (database) |

## 11. Audit — P3.3

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-AUD-01 | `[MATRIX]` Audit search is reachable by `C`, `A`, `CA` and `BG` only | direct HTTP | automated (database) |
| TC-AUD-02 | Pagination is bounded: default 50, maximum 100, cursor-based; a request for 1000 is clamped, and no offset scan occurs | direct HTTP | automated (database) |
| TC-AUD-03 | A tampered or unsigned cursor is refused, never silently reset (N-64) | direct HTTP | automated |
| TC-AUD-04 | **No application route or repository operation updates or deletes an audit row**, and a direct `UPDATE`/`DELETE` through the restricted runtime role is rejected by the trigger | structural + real PostgreSQL | automated (database) |
| TC-AUD-05 | Historical rows written before the migration still render an actor, resolved through `external_identities`, including after that identity is retired | service | automated (database) |
| TC-AUD-06 | Rendered audit content excludes raw snapshot bytes, secrets and exception detail while retaining actor, action, source, time, reason, correlation id and before/after facts | response inspection | automated |
| TC-AUD-07 | An unrecognized payload key renders as a redacted key, never as its value | unit | automated |
| TC-AUD-08 | There is no audit export, mutation or deletion route in the inventory | structural | automated |
| TC-AUD-09 | **History is unchanged by the constraint swap.** Rows seeded before the revision are identical after it — count, ids, `actor_discord_user_id`, `actor_capability`, `payload`, `occurred_at` — and each row's `xmin` is unchanged, which is the strongest available evidence that no row was rewritten rather than merely that it looks the same | real PostgreSQL | automated (database) |
| TC-AUD-10 | **New account-attributed inserts succeed**, both forms: an ordinary-provider event (`guild_council`, account set, Discord null) and a break-glass event (`platform_administrator`, account set, Discord null). Both would have been refused before the swap, and the test asserts that too, against a database at the previous revision | real PostgreSQL | automated (database) |
| TC-AUD-11 | **An unattributed human action is rejected**, parametrized over every human capability, with both attribution columns null — by the check constraint, and separately by `application/audit.py`'s account-aware guard | service + real PostgreSQL | automated (database) |
| TC-AUD-12 | **`system` and `service_principal` actions remain valid** with both attribution columns null, exactly as before the swap | real PostgreSQL | automated (database) |
| TC-AUD-13 | **Append-only denial still holds after the swap.** `UPDATE` and `DELETE` on `audit_events` are refused for the restricted runtime role (no grant) and for the owner role (the migration-0002 trigger), **including an `UPDATE` that touches only the new column** — the statement a well-meaning backfill would issue | real PostgreSQL | automated (database) |
| TC-AUD-14 | `VALIDATE CONSTRAINT` on the new check and the new foreign key succeeds against a database seeded with legacy-shaped rows, and modifies nothing | real PostgreSQL | automated (database) |

## 12. Web security controls — P3.1, verified again in P3.4

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-SEC-01 | `[MATRIX]` Every cookie-authenticated mutation is refused without a CSRF token, with a foreign session's token, and with a token from a rotated session | direct HTTP | automated (database) |
| TC-SEC-02 | CSRF is rejected **before** the application service runs, proven by asserting the service was never called | service seam | automated |
| TC-SEC-03 | A mutation with a missing or foreign `Origin` is refused `403` | direct HTTP | automated |
| TC-SEC-04 | An unknown `Host` is refused `400` before routing | direct HTTP | automated |
| TC-SEC-05 | Exact response headers on every `/v1/*` response: CSP equal to N-26, `nosniff`, `Referrer-Policy`, COOP, CORP, `Permissions-Policy`, and `Cache-Control: no-store` on authenticated responses | direct HTTP | automated |
| TC-SEC-06 | No `Access-Control-Allow-*` header appears on any `/v1/*` response, and the Phase 2 submission route's exact-origin allowlist still behaves as before | direct HTTP | automated |
| TC-SEC-07 | The OAuth redirect completes under the exact N-26 policy: a `GET` start is a navigation, so `form-action 'self'` does not apply | direct HTTP + staging browser | automated + staging |
| TC-SEC-08 | Jinja autoescaping is enabled for every configured extension, and **zero** templates use `\|safe` | structural | automated |
| TC-SEC-09 | Escaping parametrization: `<script>`, `"><img onerror>`, `{{7*7}}`, a 10 000-character name, RTL overrides and NFC/NFD variants in Actor names, reasons, usernames and audit values all render inert and bounded | response inspection | automated |
| TC-SEC-10 | No template contains an `hx-on:` attribute (route contract §6.4) | structural | automated |
| TC-SEC-11 | No view-model field reaches a `<script>` context anywhere in the rendered corpus | structural | automated |
| TC-SEC-12 | A raised internal exception produces VM-20 with a correlation id only; the response contains no path, SQL, exception text or stack frame, and the log line contains no token or player data | direct HTTP + log capture | automated |
| TC-SEC-13 | No route serves a raw snapshot artifact; the plausible paths are `404`, and the artifact store has no listing | structural + HTTP | automated |
| TC-SEC-14 | **Added 2026-08-19 (accepted D-03 correction, item D-03-1).** Every asset is same-origin. No template and no file in the M-01 static root contains `http://`, `https://`, `//cdn.`, a jsDelivr/unpkg/cdnjs host, `fonts.googleapis.com`, `fonts.gstatic.com` or an `@import url(...)`, and no template or asset name references `design-prototype/`. This is the backend half of what TC-UI-06 will assert over the production corpus; it does not claim to be TC-UI-06, which remains P3.4's to write | structural | automated |

## 13. Bounds and limits — P3.1/P3.3

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-LIM-01 | A body over N-19 is refused `413` before it is read | direct HTTP | automated |
| TC-LIM-02 | **Proxy/application parity:** the configured Caddy limit and the application limit are asserted equal from the deployed configuration, for both the general and the snapshot route (N-55, N-20) | configuration + supervised | supervised (staging) |
| TC-LIM-03 | Unsupported content types are refused; a multipart upload to a form route is refused | direct HTTP | automated |
| TC-LIM-04 | Malicious filenames in a submission are never used for storage or display (existing Phase 2 behaviour, re-asserted at the portal boundary) | service | automated |
| TC-LIM-05 | Audit filter bounds (N-63) and polling floor (N-22) are enforced; a faster poll receives a back-off | direct HTTP | automated |
| TC-LIM-06 | **Added 2026-08-15 (settings-construction remediation, RAID I-10).** The bounds a consumer *uses* are the validated ones, proved at the consumer rather than at the constructor. `RateLimitSettings`: each of the four per-address budgets and N-32's per-account budget is spent to its exact configured value and the next attempt refused, the retry hint is bounded by the configured window, a **stricter** accepted budget of two is the one enforced rather than the ceiling, and the break-glass service holds the validated N-33 per-grant cap. `BoundsSettings`: a stricter accepted `max_request_bytes` refuses a body one byte over it with `413` **before routing** while a body under it is not refused, and the client-address policy holds N-34's exact single hop. N-09/N-10 are proved at `MembershipProjection.is_fresh`/`within_grace` and **reported as having no P3.1 route consumer**; N-21 and N-22 are reported as having **no P3.1 consumer at all**, their consumer evidence being an obligation of the package that adds the consumer. `WebAuthnSettings`: the minted challenge carries the configured relying party and `required` user verification, and the service holds the validated origin tuple. `DatabasePoolSettings`: engine construction is intercepted at a stable seam and the four validated numbers are proved passed exactly, including the `statement_timeout` connect argument, and an invalid pool never reaches SQLAlchemy at all. `WorkerSettings`: `enabled` is proved by S-11's refusal and the remaining bounds are proved valid by construction — including N-23's lease as an **exact 60** and its heartbeat as an unchanged ceiling of 20 (corrected 2026-08-15) — with lease, heartbeat, attempt, timeout and queue consumer evidence recorded as a **named P3.3 obligation** rather than manufactured here | service + direct HTTP + composition seam | automated (database) |

## 14. Provider outage — P3.1/P3.3

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-OUT-01 | With the provider faulted, protected **reads** succeed within N-10's grace using the last successful observation | service | automated (database) |
| TC-OUT-02 | With the provider faulted, every mutation is refused **immediately**, without consuming the grace | service | automated (database) |
| TC-OUT-03 | After the grace is exhausted, every protected route answers `503` with VM-03 and exposes no protected data | direct HTTP | automated (database) |
| TC-OUT-04 | A provider failure never writes an absence: "refresh failed" and "membership absent" are distinguished, and a 429 storm does not revoke anybody | service | automated (database) |

## 15. View models and structural guards

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-STRUCT-01 | **The application's registered route set equals the accepted inventory exactly** — no extra route, no missing route (route contract §1). **Amended 2026-08-19 (accepted D-03 correction, item D-03-1), by addition:** the assertion built its compared set from `getattr(route, "methods", …)`, which is empty for a Starlette `Mount`, so a mount contributed nothing and `app.mount("/anything", …)` added a whole URL subtree without failing anything. A second half now asserts the registered `Mount` objects against `MOUNT_INVENTORY` and against route contract §1.2's mount table, in both directions, plus the count — so declaring a second mount in both places is still a visible edit to a test. Falsified against a deliberately reintroduced undeclared mount, with the route half shown to pass unchanged against the same mutation (which is the blindness being closed), and the tree restored and verified by digest | route **and mount** introspection vs. parsed document | automated |
| TC-STRUCT-02 | The implemented view-model set equals the documented `vm-1` set, with matching field names and types | introspection vs. parsed document | automated |
| TC-STRUCT-03 | JSONB appears only on the two columns justified under plan §7.3.1, and no new generic key/value character-state table exists (extends `tests/test_rejected_scope_absent.py`) | schema introspection | automated (database) |
| TC-STRUCT-04 | **No character-game-state correction endpoint exists**: no route, no application service, and forged submissions to plausible paths mutate nothing | structural + direct HTTP | automated (database) |
| TC-STRUCT-05 | The web process cannot import the bot's `config.py` | import graph | automated |
| TC-STRUCT-06 | Every startup refusal S-01…S-15 is exercised with deliberately wrong configuration and refuses with the documented typed error, naming variables and never values | unit | automated |
| TC-STRUCT-07 | **Added 2026-08-15 (settings-construction remediation, RAID I-10).** The five public settings types are valid by construction, parameterised from `SETTINGS_NUMERIC_BOUNDS` rather than from restated numbers. For **every** registered integer on `RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`, `DatabasePoolSettings`, `WorkerSettings` and `SessionSettings`: both accepted boundaries survive with value and exact type intact; `minimum - 1` and `maximum + 1` are refused (and a field whose register entry is a floor with no ceiling, N-22, accepts a large value rather than inventing one); an entry whose register bounds are **equal** is exercised as the one accepted value it is — N-41's concurrency, N-34's proxy hop count and N-23's lease — rather than as two boundaries that happen to coincide; integral and fractional floats, NaN, ±infinity, `True`, `False` and a comparison-overriding `int` subclass are each refused with the field named; and direct construction and `dataclasses.replace()` apply the identical rule. The accepted non-numeric shapes are enforced too — relying-party hostname and lowercase form, non-empty display name, non-empty tuple of exact origins, N-60's exact `required` user verification, an exact `bool` for `WORKER_ENABLED` and an absolute `Path` or `None` for the artifact root — and N-21's one accepted cross-field rule is enforced at the object owning both fields, from one read of each, with equality accepted. Relationships the contracts do **not** state (membership grace versus cache, N-45's attempt timeout against the lease) are proved **not** enforced, deliberately. **N-23's lease is proved to be an exact value of 60 seconds** (corrected 2026-08-15): 60 constructs and is carried unchanged, 59 and 61 are both refused as `S-10` at direct construction, at `dataclasses.replace()` and at the environment boundary with the variable named and the supplied value absent, an unset variable yields the register-derived 60, floats, non-finite floats, `True`, `False` and a comparison-overriding `int` subclass carrying 60 are all refused, a subclass whose later read of the lease lies is refused by canonicalisation, the accepted heartbeat boundaries of 1 and 20 are proved unchanged with 0 and 21 refused, and the previously documented `lease_seconds=1, heartbeat_seconds=20` is proved to **halt at `WorkerSettings` construction because the lease is invalid** — with the refusal proved to name only the lease, so no ordering rule is implied or enforced. Every seam that reads a settings value again — engine composition, limiter construction, application composition, break-glass construction and the startup health view — refuses a genuine subclass whose single later read lies, with the read count asserted as exactly one, and canonicalisation refuses a duck type and returns the base type. `WebSettings.from_environment()` still raises **one** `ConfigurationError` for seven invalid variables spanning four types, naming all seven, echoing none of their sentinel values and never leaking a `ValueError` from a constructor | unit + composition seam | automated |
| TC-STRUCT-08 | **Added 2026-08-16 (canonical settings-graph remediation, RAID I-09/I-10).** A web process holds **one** settings graph and uses it everywhere. `canonical_settings` descends the whole declared graph, reading every field once and returning exact base types at every depth including `SecretKey`, `EncryptionKey` and `ConnectionIdentity`; a genuine subclass built **truthfully** and made to lie only after construction is refused at the canonicalisation boundary — with the hostile field proved read exactly once in that phase, and with `create_engine` and the provider builder proved never called — for a wrong type and for an out-of-register later answer across `session`, `rate_limits`, `bounds`, `worker`, `webauthn` and `database_pool`. Accepted later answers are proved not to reach behaviour or durable state: the OAuth transaction's expiry (N-04) and its stored row, the repository's derived idle bound (N-06), the break-glass challenge expiry and relying party, the login-transaction cookie's `Max-Age`, the session cookie name the routes answer to, the body bound (N-19), the trusted hop count (N-34), the recorded client digest and the sealed PKCE verifier's key version all use the canonicalised value, and the caller's object is proved **never read again** after composition. `create_app` takes exactly one configuration authority — neither and both are typed refusals naming no value — and refuses a composition whose graph or **provider** was replaced after construction. The identity provider is proved not to be a second authority: a real `DiscordIdentityProvider` built from a second valid graph cannot enter a composition through any supported constructor, the authorization URL and the token-exchange body carry the composition's canonical client id and redirect URI, an injected `httpx` client supplies transport and never the timeout or the no-redirect rule, and the test-adapter seam still answers R-03. The declared `CANONICAL_SETTINGS_GRAPH` is proved **complete against a topology derived from the dataclasses' own annotations** rather than from the mapping itself — every participating type has an entry including leaves, every settings-valued field and supported tuple is classified, every declared field exists on its owner, and an unknown container or an optional node fails closed — with falsification cases showing that deleting a nested classification, deleting a type entry, or leaving a synthetic nested field unclassified all make the check fail. Canonicalising a settings type the graph does not declare is refused at runtime rather than treated as a leaf. The environment boundary is proved unchanged: five invalid variables, named exactly as `.env.example` documents them, still raise **one** `ConfigurationError` naming all five, echoing none of their sentinel values, and reporting nothing else. **Amended 2026-08-16 (provider/engine authority remediation):** the two claims about `create_app` refusing a composition whose graph or provider was *replaced after construction* are superseded — both replacements are now refused at the assignment itself, so the cases assert the refusal and the unchanged held object rather than a later factory call, and the provider comparison `_require_provider_from()` is removed. What `create_app` still requires, and is still proved to detect, is a `WebComposition` **subclass** whose `settings` property answers something other than the canonical graph. See TC-STRUCT-09. **Amended 2026-08-16 (test clock-authority remediation), by addition:** the consumer cases that prove N-04's expiry on durable state must derive the row's creation and its expiry from **one** clock, and the row must be proved to carry it. `oauth_transactions.created_at` is stamped by the application (`repositories.utcnow()`) and `webauthn_challenges.created_at` by PostgreSQL (`server_default = now()`), while `expires_at` comes from the injected clock, and `ck_oauth_transactions_expiry_after_creation` / `ck_webauthn_challenges_expiry_after_creation` compare them — so a case injecting an instant captured at module import has two authorities and a result that depends on elapsed wall time. Required: each affected operation takes its instant from inside its own transaction (PostgreSQL's transaction timestamp, with the repository's clock bound to the same reading); a regression asserts on **both** tables that `expires_at - created_at` is exactly the accepted N-04 lifetime, which is false for any non-zero elapsed time under an import-time clock; and a second regression proves the constraint live by injecting a deliberately stale instant and requiring PostgreSQL to refuse both rows. Neither may pass by extending a lifetime, suppressing a constraint, faking the database, sleeping, or ceasing to assert the accepted value. **Amended 2026-08-16 (that remediation's independent implementation re-review), by addition:** the absence of a module-import clock was described as asserted over the AST when nothing parsed the module, so it is now asserted. A regression parses `tests/web/test_canonical_settings_graph.py` itself and fails if any code that runs **at import** reads or constructs an instant — module-level statements, class bodies, decorator expressions and the default arguments of the functions it declares are all walked; function, method and lambda bodies, imports and annotations are deliberately not, because they are respectively the operation's own clock, not a clock at all, and unevaluated under `from __future__ import annotations`. `timedelta` and `timezone` are not findings: a duration and a fixed offset are not instants, and rejecting them would state a broader invariant than the one claimed. The detector is falsified against a reintroduced `NOW = datetime.now(timezone.utc)`, against a fixed module-scope `datetime(...)` constructor, against a capture hidden in a default argument, and against an alias binding `datetime.now` without calling it; and it is proved to accept the imports, `pytestmark`, the declarations, a module-level `timedelta` duration, the `OperationClock` fixture and every function-scoped datetime arithmetic in the module. It must inspect AST semantics rather than text: the clean module contains seven literal occurrences of `datetime.now(timezone.utc)` in comments, docstrings and synthetic test inputs, all of which a `grep` guard would report and none of which is executable code. **Amended 2026-08-16 (independent re-review of that AST regression), by addition — this clause supersedes the lambda-body sentence above.** "Function, method and lambda bodies are deliberately not walked" was accurate for functions and methods and wrong for a lambda invoked where it is written: `NOW = (lambda: datetime.now(timezone.utc))()` executes its body during the import and the detector reported it clean, so the regression did not enforce the invariant it stated. Required instead: the detector must decide a lambda by **when its body runs**. A lambda that the source shows being invoked in place — the callable of an import-time call, including the curried `(lambda: lambda: ...)()()` — has its body walked and the capture reported at the source line of the `datetime` reference; a lambda that is stored, returned or passed as an argument keeps its body excluded, because that body runs when its holder calls it; and lambda defaults remain walked in both cases. The existing treatment of function and method bodies, imports, annotations, `timedelta`, `timezone`, class bodies and decorators is unchanged, and the accepted examples must still produce no findings. Falsification must include the invoked form, the curried form and the stored-lambda negative control, against the real module and restored byte-for-byte. The detector remains **name-based**: a clock reached through a helper the module names something else, or a lambda called through a variable, is outside it and is declared as a limit rather than implied to be covered. **Amended 2026-08-16 (independent re-review of that lambda correction), by addition — this clause supersedes in part the recognition half of the clause above.** "Invoked where it is written" was the right rule and the detector applied it too literally: it recognised only an `ast.Lambda` or a chain of `ast.Call`, so a lambda wearing a walrus — `NOW = (reader := lambda: datetime.now(timezone.utc))()`, and the curried `NOW = (factory := lambda: lambda: datetime.now(timezone.utc))()()` — was reported clean although both bodies execute during the import and neither needs a separately stored name resolved. Required instead: a callable position must be read **through** an `ast.NamedExpr`, which evaluates its operand and answers that same object to the call standing beside it in the same expression. The unwrapping decides only whether the body runs: the named expression's target is still walked as import-time code, so a target that is itself one of the instant names remains a finding, and lambda defaults remain walked exactly as before. The boundary must be stated and must be exact — a **selection** (`(f if flag else g)()`) is not unwrapped, because the source does not say which body runs — and a lambda bound in one statement and called through its name in a later one must remain outside the guard and declared as a limit, since resolving it is the interprocedural analysis this guard does not attempt. Falsification must include both named-expression reproducers, the stored-and-called negative control, and the pre-correction detector reporting nothing for the same inputs, against the real module and restored byte-for-byte. **Amended 2026-08-16 (independent re-review of that named-expression correction), by addition — this clause supersedes in part the conditional-expression boundary stated above.** "A selection is not unwrapped, because the source does not say which body runs" is true of `if flag` and false of an AST literal: `NOW = ((lambda: datetime.now(timezone.utc)) if True else (lambda: None))()` captures an instant at import and the AST names the branch that runs, so no data flow and no set of possible bodies is involved — yet the detector reported it clean, because `_invoked_lambda()` did not handle `ast.IfExp` at all, and the existing control used a **name** as its test and so never exercised the broader claim. Required instead: a callable position must select the reachable branch of an `ast.IfExp` whose test is an **exact** boolean literal (`test.value is True` or `is False`, identity and not truthiness), then continue through the supported lambda/call/named-expression chain. The change must stay AST-syntactic: a name, a comparison, a boolean operator, an `ast.BoolOp`, or a constant that is merely truthy such as `1` or `'yes'` must **not** be evaluated or unwrapped, and each remains a declared limit asserted as a case. The visitor must preserve ordinary evaluation — the conditional's test always runs and is always walked; when the test is a literal only the **selected** expression is walked, because Python never evaluates the other, so a capture written in the dead branch (including a lambda default there) is not reported while the selected branch's defaults still are. Findings must remain deterministic, source ordered and duplicate-free, and every construct the earlier clauses cover must report exactly as before. Falsification must include the literal-`True` and literal-`False` positives with the clock in each selectable branch, a clock in the condition, the curried and named-expression compositions, and the preserved name-conditioned selection as the negative boundary control, against the real module and restored byte-for-byte | unit + AST + composition seam + direct HTTP | automated (database for the consumer half) |
| TC-STRUCT-09 | **Added 2026-08-16 (P3.G1 provider/engine authority remediation, RAID I-09/I-10).** The identity provider and the database engine a web process uses are **derived** from its canonical settings graph and cannot be supplied or replaced. `WebComposition.__init__` and `create_app` are proved — by pinned parameter sets, by annotations naming neither `IdentityProvider` nor `Engine`, and by interpreter refusals of `provider=`, `provider_double=` and `engine=` — to admit no provider and no engine; a genuine delegating `IdentityProvider` wrapping a real `DiscordIdentityProvider` built from a second complete valid graph (which the removed concrete-class exclusion admitted, asserted) reaches no production construction, and the composition built from graph A holds a provider whose configuration object **is** graph A's `discord`; the suite's own substitution path refuses a real Discord adapter from another graph, echoing no client id, guild id, redirect URI or secret. After `create_app()`, assignment to `composition.provider`, to the private slot behind it, to `composition.engine` and to `composition.settings` are all refused with the held object proved unchanged, and replacing `app.state.composition` is proved not to change which provider answers R-03 or R-04 — both routes are then driven and the startup provider is shown to be the object that answered. The authorization URL and the token-exchange body carry the composition's canonical client id, redirect URI and endpoint, and the injected transport carries the canonical timeout and the no-redirect rule. On the engine half: `build_engine` is proved called exactly once with the canonical graph object (not the caller's), the url and the four N-53 pool numbers SQLAlchemy receives are that graph's, the resource checks receive the same graph and the same engine instance by identity, a request's transaction is shown to write on that engine, a production-owned engine is disposed exactly once by `aclose()` while a lent one is not disposed at all, and the test-only factory refuses an engine naming another database or dialling TCP. The substitution path is proved to live under `tests/` and to be imported by no module under `adapters/`, `application/`, `domain/`, `tools/` or `helpers/` | unit + composition seam + direct HTTP | automated (database for the engine and route halves) |
| TC-STRUCT-10 | **Added 2026-08-16 (P3.G1 request-authority and lifecycle remediation, RAID I-09/I-10).** What a request reads is what `create_app()` accepted, not what a mutable namespace answers. The factory builds one frozen `RequestAuthority` from the canonical graph it accepted — settings, address policy and Jinja environment — and passes it into route registration and the exception handler; the removed `_settings(request)`, `_client_digest`, `_user_agent_digest`, `_origin_is_ours` and `_render` helpers each read `request.app.state.settings` per call, which gave an already-validated application a second complete settings graph to serve from through one ordinary assignment. An application built from graph A has **all four** diagnostic references (`settings`, `composition`, `templates`, `address_policy`) replaced with objects built from a second **independently valid** graph B, and graph A is then proved to still govern, through public behaviour and durable state: the accepted mutation `Origin` (both directions), the CSRF key a synchronizer token is verified under (forged under B refused, genuine under A accepted while the session is live), the session cookie name the routes answer to and clear, the login-transaction cookie's `Max-Age` (N-04), the client-IP and user-agent digest keys read back off `oauth_transactions` and `sessions`, the graph the health view is handed (by identity), the provider that answers R-03/R-04 and the engine the request's transaction opens on, and the Jinja environment whose `autoescape` is set once (TC-SEC-08). The substituted address policy is proved never consulted. The structural half is asserted over the **AST** rather than by text search: no module under `adapters/`, `application/`, `domain/`, `helpers/` or `tools/` reads `<...>.app.state.<name>`, the only permitted accesses being the four diagnostic **writes** inside `create_app`; the detector itself is falsified against a reintroduced per-request read, against writes alone, and against a read inside the factory, and the four diagnostic writes are asserted still present so the operator's view was not what got removed | unit + AST + direct HTTP + durable state | automated (database) |
| TC-STRUCT-11 | **Added 2026-08-16 (P3.G1 request-authority and lifecycle remediation, RAID I-09/I-10); coverage extended the same day by its re-review to failed startup and partial construction, and again by the P3.G1 test-clock-authority re-review to the one-way composition lifecycle.** The ASGI lifecycle — not a caller, and not a test — owns the composition's process-lifetime resources on **every** exit. Every case drives the real lifespan protocol through `tests/web/lifespan.py`, because `httpx.ASGITransport` never opens a `lifespan` scope and a case that assumed otherwise would pass with no lifespan installed at all. **Normal shutdown:** the provider that served R-03 inside the lifespan is closed exactly once on the way out; a production-**owned** engine is disposed exactly once and not before; a **lent** engine is never disposed; replacing `app.state.composition` mid-lifespan redirects neither the close nor the disposal and leaves the intruder's untouched; a provider close that raises still disposes the owned engine, surfaces as `lifespan.shutdown.failed`, and renders no configured secret in the exception or the protocol message; the at-most-once rule holds across a completed lifespan, a second lifespan over the same composition, a direct `aclose()` and two concurrent calls; and `_cleanup_started` is proved to select nothing, the provider and engine remaining write-once. **Refused startup:** the resource checks (S-12/S-14/S-15) run inside the lifespan, so a refusal answers `lifespan.startup.failed` and never `lifespan.startup.complete`, surfaces the **original typed `ConfigurationError`** with its `S-nn` intact, never enters the block where requests are served, and still closes the provider exactly once and disposes an owned engine exactly once while leaving a lent one alone — the path that previously returned no application at all and therefore ran no cleanup. All four diagnostic `app.state` references replaced with graph B's before startup redirect neither the checks (which are proved handed the accepted graph and the accepted engine **by identity**) nor the cleanup. A provider close that fails while unwinding a refusal is proved **not** to replace it: the `ConfigurationError` stays at the head and the transport failure is reachable in its context chain. No configured secret appears in the surfaced exception, its whole chained context, the `lifespan.startup.failed` message's traceback, or anything logged. The success path is proved unchanged, including that `startup_warnings` is still recorded and that the factory itself now runs no check. **Partial construction:** a `WebComposition.__init__` that fails after building an owned engine disposes it before re-raising, and one holding a lent engine does not. **One lifetime, claimed once:** `WebComposition` moves one way through `new -> started -> closing -> closed`, `__setattr__` refuses every backward or sideways write to that state, and the lifespan claims the composition **before** the resource checks and before any request is served. A second application over a closed composition, a second entry of the *same* application's lifespan, and a startup attempted while the first is still serving each answer `lifespan.startup.failed` with `CompositionLifecycleError` and never `lifespan.startup.complete`; the refusal runs no resource check (they cannot detect the condition — a disposed engine silently builds a replacement pool), closes nothing (the live claimant's provider is proved untouched and still serving R-03), and leaves the provider closed and the owned engine disposed exactly once in total; and the refusal names no configured value in the exception, its context chain or the protocol message. An unclaimed composition may still be closed, and is then refused a startup like any other | unit + real ASGI lifespan protocol + direct HTTP | automated (database for the lent-engine and request halves) |
| TC-VM-01 | Every view model is frozen, slotted, and contains no mutable collection | introspection | automated |
| TC-VM-02 | Every sequence field enforces its documented bound and sets `truncated` rather than exceeding it | unit | automated |
| TC-VM-03 | A `MigrationDeferred` entry cannot carry a value, and every legacy field renders with the package named in `data-migration-manifest.json` | unit + manifest cross-check | automated |
| TC-VM-04 | Reconciliation warnings render as closed-vocabulary codes; no artifact-sourced free text reaches a response | unit | automated |
| TC-VM-05 | `level = None` renders as "not recorded", never `0` | unit | automated |
| TC-VM-06 | **Added 2026-08-19 (accepted D-03 correction, item D-03-6).** VM-22 `DeniedView` carries exactly `state` and `reason` — asserted as equality, not containment, because an **added** field is the defect — and `DenialCategory` remains the closed six-member vocabulary. Every generic denial on the portal and import surfaces is proved to construct `DeniedView` and never `NonMemberView`, read over the source of both `_denied` helpers; the non-member page is proved to keep VM-02 with its guild name, check time and correlation id, which is intentionally permitted recovery context. Falsified by reintroducing a `correlation` field, populating it and printing it in `denied.html`: twelve cases across three modules fail, including the pre-existing TC-OBJ-07 case, and the tree is restored and verified by digest | introspection + source + direct HTTP | automated (database for the response half) |
| TC-STATIC-01 | **Added 2026-08-19 (accepted D-03 correction, item D-03-1).** M-01 serves `GET` and `HEAD` only. `HEAD` returns the same `Cache-Control` and `Content-Length` as `GET` with an empty body; `POST`, `PUT`, `PATCH` and `DELETE` are `405` **identically** for a path that exists and one that does not, so a mutation method cannot become a directory listing one request at a time | direct HTTP | automated |
| TC-STATIC-02 | M-01 serves only the one approved root. A sibling of the static directory holding real files (`adapters/web/templates/`) is unreachable, and so is the package source above it | direct HTTP | automated |
| TC-STATIC-03 | Traversal, encoded traversal, dotfiles, directories and missing files all answer a safe `404` carrying no directory listing, exception text, filesystem path or stack frame, and a grammar refusal is **byte-identical** to a missing file so the grammar is not enumerable. Six traversal encodings are used and five are verified by ASGI-scope inspection to arrive at the application as `/static/../…` rather than being normalised away by the client; the grammar is proved load-bearing rather than decorative by `.gitkeep`, which Starlette's own root check would happily serve and only the grammar refuses | direct HTTP + unit | automated |
| TC-STATIC-04 | The host check applies to an asset exactly as to a page (`400` on an unknown `Host`, N-01), and the kill switch leaves `/static/` serving **while** every `/v1/*` route answers `503` — both halves in one case, because a test asserting only the exemption would pass against a kill switch that had stopped working. The exemption is proved to be a prefix and not a bypass: an untrusted host is still `400` on a static path while the switch is engaged | direct HTTP | automated |
| TC-STATIC-05 | Fingerprinted assets (`<stem>.<16 lowercase hex>.<ext>`) receive `public, max-age=31536000, immutable`; everything else receives `public, max-age=0, must-revalidate`, including four near-misses (15 hex, 17 hex, uppercase hex, a non-hex letter) that must fall to the conservative branch. The header is proved independent of the caller: a request carrying a session cookie still receives the cacheable value rather than `no-store`, and the six §7.2 security headers still apply to every asset | unit table + direct HTTP | automated |
| TC-STATIC-06 | A static response sets and refreshes **no** cookie — asserted with no cookie presented and with a session and login-transaction cookie presented, the second being the case that would catch an asset fetch extending an idle timeout (N-06) — and the surface requires no session, capability, CSRF token or `Origin` | direct HTTP | automated |
| TC-STATIC-07 | Route contract §1.2's URL grammar, as a seventeen-row table over accepted and refused segments, plus the boundary assertion that the repository-owned static root ships **only** its empty `.gitkeep`: no production CSS, no vendored HTMX, no emblem and no visual asset of any kind is added by the D-03 correction | unit | automated |

## 16. Frontend, accessibility and responsive — P3.4

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-UI-01 | Every page renders at 320, 768 and 1280 CSS pixels with no horizontal body overflow | browser automation | automated (browser) |
| TC-UI-02 | 200% reflow does not lose content or function | browser automation | automated (browser) |
| TC-UI-03 | Primary navigation and every control are keyboard reachable with a visible focus indicator | browser automation | automated (browser) |
| TC-UI-04 | `prefers-reduced-motion` suppresses transitions while preserving focus indicators | browser automation | automated (browser) |
| TC-UI-05 | Empty, loading, stale, denied, validation and system-error states each render from a real view model | browser automation | automated (browser) |
| TC-UI-06 | No production template imports, links to or serves anything under `design-prototype/` | structural | automated |
| TC-UI-07 | Contrast of production surfaces meets WCAG 2.2 AA | source-derived tool + supervised | supervised |
| TC-UI-08 | **Real-device check** on Peter's hardware | manual | **real-device** |
| TC-UI-09 | **Screen-reader traversal** of login, My Characters, character detail, reconciliation and audit | manual | **assistive-technology — not yet scheduled** |

TC-UI-08 and TC-UI-09 cannot be satisfied by automation and must not be reported
as passing on automated evidence. The visual handoff already classifies
assistive-technology traversal as `not tested`; Phase 3 does not inherit a pass
from the prototype.

## 17. Performance and operations — P3.3/P3.5

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-PERF-01 | Measure worker peak resident memory for a real 32-Actor folder and for a synthetic worst-case at the N-20 bound; compare against N-47 | supervised, staging | **staging** |
| TC-PERF-02 | **Measure a real-folder apply end to end** — never measured to date (RR-06) | supervised, staging | **staging** |
| TC-PERF-03 | Under a running preview, the portal still answers `/healthz` and a status poll within a stated bound | staging | **staging** |
| TC-OPS-01 | Kill switch: engage layer 1, confirm the portal refuses, confirm the bot and Foundry are unaffected, release | supervised | supervised |
| TC-OPS-02 | Backup, restore and rollback rehearsal on a disposable database | supervised | supervised |
| TC-OPS-03 | Staging end-to-end: OAuth login, member read, Council link change, folder selection, preview, confirm, audit search | staging | **staging** |
| TC-OPS-04 | Deployment gate item 9: every startup refusal observed refusing on the deployed configuration | supervised | supervised (staging) |
| TC-OPS-05 | Monitoring output contains no identity, character or token data | supervised | supervised |

## 18. Coverage of the delivery plan §11 rows

Every row of the accepted table, with its expanded tests. No row is dropped.

| Delivery plan §11 requirement | Owning package | Tests |
|---|---|---|
| Unauthenticated users cannot access protected data | P3.1 | TC-OBJ-01, TC-OBJ-06 |
| Discord outage still permits narrow Server Administrator recovery | P3.1 | TC-BG-02, TC-BG-04, TC-OUT-01…03 |
| Break-glass cannot acquire Council or character authority | P3.1/P3.2 | TC-BG-04, TC-BG-05a…05e, TC-CAP-02, TC-CAP-08…11 |
| Recovery grant is host-local, hashed, single-use, 10-minute | P3.1 | TC-BG-06…09, TC-BG-10, TC-BG-13 |
| Platform accounts survive provider unlink/retirement | P3.0–P3.2 | TC-ID-01, TC-ID-03, TC-ID-04, TC-ID-07, TC-MIG-02, TC-AUD-05 |
| Account-attributed human events are legal without rewriting history | P3.1 | TC-AUD-09…TC-AUD-14, TC-MIG-14…16, TC-BG-15 |
| Emergency authority is not convertible into later Council/import authority | P3.1/P3.2 | TC-BG-05a…05e, TC-CAP-08…11 |
| Every job reaches a terminal state | P3.3 | TC-JOB-05, TC-JOB-13, TC-JOB-15, TC-JOB-16 |
| PKCE verifier is recoverable, bound and single-use | P3.1 | TC-AUTH-07, TC-AUTH-12 |
| A Discord OAuth session is the unique durable product of one consumed transaction (OD-44) | P3.1 | TC-AUTH-13, TC-AUTH-14 |
| A completion cannot be performed by a provider other than the one its transaction records (OD-44 §8.1) | P3.1 | TC-AUTH-15 |
| A session rotation chain is linear and cannot cross an account, method or OAuth binding (OD-44 §8) | P3.1 | TC-AUTH-16, TC-AUTH-17 |
| A rotation cannot revive an expired session, and a chain lives no longer than the login at its root (N-07, N-15) | P3.1 | TC-AUTH-18 |
| An idle refresh cannot revive an expired session, extend the absolute bound, or give a break-glass session the ordinary idle window — and no supported API admits the pairing that would ask for one, whether as a call argument or as a constructed policy (N-06, N-15) | P3.1 | TC-AUTH-19 |
| No name/email auto-link can merge accounts | P3.1/P3.2 | TC-ID-05, TC-ID-06, TC-MIG-10 |
| Non-member/member/Council/administrator matrix for every protected endpoint | P3.1–P3.3 | TC-OBJ-01 `[MATRIX]`, TC-CAP-02 |
| Council uses stable role ID; administrator does not imply Council | P3.1/P3.3 | TC-CAP-01, TC-CAP-02, TC-CAP-07 |
| Revoked membership/role and privilege change | P3.1/P3.3 | TC-SESS-03, TC-SESS-06, TC-JOB-10 |
| Multiple linked characters and object substitution | P3.2 | TC-OBJ-02, TC-OBJ-03 |
| Character-link grant/revoke/default changes | P3.2 | TC-ACC-01…07 |
| Legacy identity evidence fully accounted for, never auto-authorizing | P3.2 | TC-MIG-08…13, TC-MIG-17 |
| Google is legacy migration input only, and no platform runtime depends on it | P3.2 | TC-MIG-18 |
| R-28 reports current linkage, not a stale confirmation, and the totals stay balanced | P3.2 | TC-MIG-19 |
| A decided proposal cannot lack its reason, whatever writes it | P3.2 | TC-MIG-20 |
| Superseded identity evidence remains durable but cannot create authorization | P3.2 | TC-MIG-21 |
| Only administrator manages role-capability mappings; protected mapping survives | P3.2 | TC-CAP-03…06 |
| Ordinary member cannot see or call import | P3.3/P3.4 | TC-OBJ-01, TC-OBJ-06, TC-OBJ-05 |
| Administrator folder change invalidates preview | P3.3 | TC-JOB-09 |
| Council confirmation exact scope | P3.3/P3.4 | TC-JOB-09, TC-VM-04, TC-UI-05 |
| No character-game-state correction endpoint | P3.0–P3.5 | TC-STRUCT-01, TC-STRUCT-04 |
| Legacy fields show migration package and no control | P3.2–P3.4 | TC-VM-03 |
| CSRF, origin, cookie and safe redirects | P3.1 | TC-SEC-01…04, TC-AUTH-06, TC-SESS-09 |
| Request/file limits, content type and malicious filename | P3.1/P3.3 | TC-LIM-01…04 |
| Escaped Actor, warning and user-controlled text | P3.2–P3.4 | TC-SEC-08…11, TC-VM-04 |
| Async job restart/lease/retry/recovery | P3.3 | TC-JOB-02…06, TC-JOB-13, TC-JOB-15, TC-JOB-16 |
| Double-click, retry and two-browser concurrent apply | P3.3 | TC-JOB-07, TC-JOB-08 |
| Audit search authorization and bounded pagination | P3.3 | TC-AUD-01…03 |
| Audit update/delete impossible | P3.3 | TC-AUD-04, TC-AUD-08 |
| Raw snapshot unauthorized download and disclosure | P3.1/P3.3 | TC-SEC-13, TC-JOB-14 |
| Security headers and CSP | P3.1/P3.4 | TC-SEC-05, TC-SEC-07 |
| Responsive/keyboard/focus/reduced motion/error states | P3.4 | TC-UI-01…05, TC-UI-07…09 |
| Migration apply/downgrade/upgrade and recovery | each schema package/P3.5 | TC-MIG-04, TC-MIG-07, TC-OPS-02 |
| Full gate package | P3.5 | §13.3 checklist; TC-OPS-01…05, TC-PERF-01…03 |

## 19. Coverage of implementation plan §12 Phase 3 mandatory tests

| Plan §12 Phase 3 mandatory test | Tests |
|---|---|
| Access matrix for every import, profile and audit endpoint, direct HTTP as well as hidden controls | TC-OBJ-01, TC-OBJ-06 |
| Council role or membership revoked between preview and apply | TC-JOB-10 |
| CSRF refusal, size limits, unsupported content type, malicious filename, escaped text, unauthorized raw-snapshot download | TC-SEC-01, TC-LIM-01…04, TC-SEC-09, TC-SEC-13 |
| Administrator folder/profile change invalidates a preview; confirmation shows changed scope | TC-JOB-09 |
| Double-click, retry, two-browser concurrent apply | TC-JOB-07, TC-JOB-08 |
| Cross-character identifier substitution | TC-OBJ-02 |
| No character-game-state correction endpoint; forged submissions mutate nothing | TC-STRUCT-04 |
| Every legacy field renders `migration deferred` plus its package | TC-VM-03 |
| Council/administrator audit search with bounded pagination; others cannot read | TC-AUD-01, TC-AUD-02 |
| No route or repository can update/delete audit; runtime-role mutation rejected | TC-AUD-04 |
| Audit rendering excludes raw bytes, secrets and unsafe detail while retaining required facts | TC-AUD-06, TC-AUD-07 |

## 20. Checks that require evidence Phase 3 does not yet have

Labelled explicitly, per the P3.0 prompt.

| Test | Missing precondition |
|---|---|
| TC-LIM-02, TC-OPS-03, TC-OPS-04, TC-PERF-01…03, TC-SEC-07 (browser half) | **Staging does not exist** (delivery plan §10) |
| TC-UI-08 | Peter's own device |
| TC-UI-09 | A screen reader and a person to drive it; **not yet planned or scheduled**, and inherited as `not tested` from the visual baseline |
| Any real-data measurement | Real snapshots are operational inputs and are never committed as fixtures (plan §6.4) |

A gate recommendation that treats any of these as passing on automated evidence
would be misreporting, and the P3.5 evidence package must carry them as their own
class.

### P3.G1 acceptance carry-forward — I-06 and A-05

Peter accepted P3.1 and closed P3.G1 on 2026-08-16 without representing the
missing evidence above as passing. The following conditions remain explicit:

- **I-06 stays open.** It does not block P3.2. Before staging/production exposure
  and final Phase 3 production-readiness acceptance, a named staging build must
  pass TC-LIM-02, TC-SEC-07's browser half, TC-OPS-01…05 and TC-PERF-01…03 at
  their required evidence levels. Store the date, environment and build identity,
  results, explained failures or skips, and Operations Owner plus required
  reviewer acceptance.
- **A-05 stays open.** It does not block P3.2. Before public staging/production
  exposure, the Operations Owner must record the host/environment and date,
  confirm at least two enabled real WebAuthn credentials using the protected
  operator/startup check without recording credential material, and obtain the
  Security Reviewer's break-glass-readiness confirmation.

Neither condition is waived by P3.G1 acceptance or by an automated green suite.

## 21. P3.3 evidence map — added 2026-08-18, by addition only

Where each P3.3-owned row's evidence lives. **No accepted row is rewritten**; this
records which module carries which obligation, so a reviewer can go from a
requirement to the case that holds it without reading seven files to find out.

Every module below runs against real PostgreSQL through the disposable-database
guards, and several drive two real connections with explicit barriers. None
contacts a live Discord, Google, Foundry or production service, and none uses
real player, Actor or credential data: the artifacts are the synthetic Phase 2
bundles and the accounts are the synthetic portal ones.

### 21.1 Durable jobs — §10

| Row | Module | Case |
|---|---|---|
| TC-JOB-01 | `tests/web/test_p3_3_jobs.py` | `…a_job_is_created_queued_and_no_work_happens_in_the_request` — and `snapshot_imports` and the result table are asserted empty, so "no work" is a fact about the database rather than about the handler |
| TC-JOB-02 | `test_p3_3_jobs.py` | `…two_workers_cannot_claim_one_attempt` — two real connections with both transactions open, so `SKIP LOCKED` is the only thing that can decide |
| TC-JOB-03 | `test_p3_3_jobs.py` | `…a_heartbeat_extends_the_lease_and_a_stranger_changes_nothing`, extended to **every** worker write (complete, fail, stale, cancel, abandon), plus `…the_fencing_token_stops_a_worker_publishing_after_it_reclaims` |
| TC-JOB-04 | `tests/web/test_p3_3_worker.py` | `…a_worker_crash_after_the_effect_commits_leaves_one_effect_and_a_readable_job` — the commit lands, the publication does not, the reaper requeues, a worker finishes, and exactly one import exists |
| TC-JOB-05 | `test_p3_3_jobs.py` | `…attempts_one_through_exhaustion_on_real_postgresql` — all three expiries, with `queued`/`failed`, `attempts`, `lease_owner`, `failure_code` and `finished_at` asserted at each, and no fourth claim |
| TC-JOB-06 | `test_p3_3_jobs.py` | `…completed_is_impossible_without_a_committed_result` — a direct `UPDATE`, refused by `ck_reconciliation_jobs_completed_has_a_result` |
| TC-JOB-07 | `test_p3_3_jobs.py` | `…a_double_click_yields_one_job_and_one_audit_event` and `…two_browsers_confirming_the_same_preview_resolve_to_one_apply` |
| TC-JOB-08 | `test_p3_3_jobs.py` | `…two_concurrent_inserts_of_one_live_apply_leave_one` — two real connections; the partial unique index decides |
| TC-JOB-09 | `test_p3_3_jobs.py` | `…a_folder_change_invalidates_every_outstanding_job_atomically`, `…a_confirmation_of_a_stale_preview_applies_nothing_and_says_why`, `…a_preview_past_n46_cannot_be_confirmed`, `…a_wrong_preview_token_is_refused`; and `test_p3_3_worker.py`'s `…a_moved_scope_is_detected_inside_the_attempt_and_applies_nothing` for the aggregate-version half |
| TC-JOB-10 | `test_p3_3_jobs.py` (request boundary) and `test_p3_3_worker.py` (commit boundary) | `…council_revoked_between_preview_and_apply_is_refused` and `…council_revoked_after_the_confirmation_refuses_the_apply_at_the_commit`. **Two windows, not one**: a caller who lost Council before submitting, and authority lost after the job was enqueued when no request is involved at all |
| TC-JOB-11 | `test_p3_3_jobs.py` | `…cancellation_of_a_running_job_is_a_request_not_a_state`, `…a_committed_apply_cannot_be_cancelled`, `…cancellation_racing_completion_leaves_exactly_one_outcome` |
| TC-JOB-12 | `test_p3_3_jobs.py` | `…the_queue_bound_refuses_the_sixth_job_and_creates_no_row` |
| TC-JOB-13 | `test_p3_3_jobs.py` | `…two_concurrent_reapers_transition_each_job_exactly_once` — two real connections at a barrier, over jobs at `attempts` 1, 2 and 3; one `RETURNING` row per job across both, `version` incremented by exactly one, `attempts` unchanged, and a sweep asserting nothing is left `running` with a dead lease |
| TC-JOB-14 | `tests/web/test_p3_3_disclosure_and_bounds.py` | `…a_rendered_job_page_contains_no_artifact_bytes_or_location` — the store's own reference is asserted absent too, and `test_p3_3_worker.py` asserts the stored summary carries no Actor content |
| TC-JOB-15 | `test_p3_3_jobs.py` | `…the_stranded_state_is_unrepresentable` — three attempts, three refusals, plus `…a_terminal_state_cannot_omit_its_reason` and `…running_and_holding_a_lease_are_the_same_fact_in_both_directions` |
| TC-JOB-16 | `test_p3_3_jobs.py` | `…worker_self_abandon_races_the_reaper_in_both_orders`, parametrized over both orders, plus `…self_abandon_at_the_last_attempt_fails_the_job_directly` |

### 21.2 Audit — §11

| Row | Module | Case |
|---|---|---|
| TC-AUD-01 | `test_p3_3_matrix.py`, `test_p3_3_success_cells.py` | the `[MATRIX]` parametrization, and the four permitted states asserted per route |
| TC-AUD-02 | `tests/web/test_p3_3_audit_search.py` | `…pagination_is_bounded_and_a_request_for_a_thousand_is_clamped`, plus `…no_count_star_is_issued_over_the_audit_table`, which captures **every statement** the request issues and asserts none counts audit rows |
| TC-AUD-03 | `test_p3_3_audit_search.py` | `…a_tampered_or_unsigned_cursor_is_refused_never_reset` — three shapes, including a cursor minted for the **snapshot** listing, which is what the scope string exists for |
| TC-AUD-04 | `test_p3_3_audit_search.py` | `…no_application_repository_offers_an_audit_update_or_delete` (over the AST, not by grep), `…the_audit_search_repository_declares_no_write_method`, `…the_schema_owner_cannot_rewrite_audit_history` (the trigger, including an update touching only the new column), and `…the_runtime_role_holds_exactly_the_accepted_p3_3_grants` |
| TC-AUD-05 | `test_p3_3_audit_search.py` | `…a_historical_row_resolves_its_actor_through_a_retired_identity` |
| TC-AUD-06 | `test_p3_3_audit_search.py` | `…a_rendered_audit_row_retains_the_facts_it_must_and_no_others` — the payload carries raw artifact text, a bearer token and a stack frame under undeclared keys, and every one is absent from the response |
| TC-AUD-07 | `test_p3_3_audit_search.py` | `…an_unrecognized_payload_key_renders_as_a_redacted_key`, plus `…every_payload_key_this_repository_writes_is_classified`, which parses every `AuditEvent(payload={…})` literal in the repository |
| TC-AUD-08 | `test_p3_3_audit_search.py`, `tests/web/test_structural_guards.py` | `…there_is_no_audit_export_mutation_or_deletion_route` and `…a_mutation_on_a_read_only_path_is_not_allowed` |

### 21.3 The rows P3.3 shares with earlier packages

| Row | Where P3.3's portion lives |
|---|---|
| TC-OBJ-01, TC-OBJ-06 | `test_p3_3_matrix.py` — the §6.2 matrix **parsed from the contract**, issued directly, never rendering the page that carries the control |
| TC-OBJ-05 | `test_p3_3_matrix.py` `…a_member_learns_nothing_from_a_job_id` — a real job id and an absent one produce the same status **and the same body** |
| TC-CAP-01/02/07 | `test_p3_3_matrix.py`, including `…an_administrator_alone_cannot_preview_or_apply` and `…council_alone_cannot_select_a_folder` |
| TC-CAP-09 | `test_p3_3_matrix.py` `…a_continuity_scoped_administrator_matches_the_break_glass_column` — the whole inventory re-run as `AC`, which is a **guild member**, so any check that confined emergency scope by testing membership would let it through R-41 |
| TC-SESS-03/06 | the `U` and `N` columns of the matrix, and the navigation/fragment split asserted in `test_structural_guards.py` |
| TC-LIM-01/03/04/05 | `test_p3_3_disclosure_and_bounds.py` — the contract's **per-route** body bounds (tighter than N-19), the multipart refusal, malicious folder ids refused as input, and the N-22 floor in both `Retry-After` and the poll hint |
| TC-SEC-09 | `test_p3_3_disclosure_and_bounds.py` — parametrized over the accepted hostile set on the two fields that can carry external text: a blocked Actor's name and an audit `reason` |
| TC-SEC-13 | `test_p3_3_disclosure_and_bounds.py` `…no_p3_3_path_serves_an_artifact_even_to_council` — issued **as Council**, the caller most entitled |
| TC-OUT-01…04 | `test_p3_3_disclosure_and_bounds.py`, each with a stored token grant so the request genuinely reaches the provider; a read uses the grace, every mutation is refused immediately and enqueues nothing, and a failed refresh writes no absence |
| TC-VM-01…05 | `test_structural_guards.py`'s existing introspection, which now covers VM-14/15/17/18; TC-VM-04 additionally in `test_p3_3_disclosure_and_bounds.py` |
| TC-STRUCT-01/02 | unchanged and now asserting the **complete** inventory: `DEFERRED_ROUTES` and `DEFERRED_VIEW_MODELS` are both empty |

### 21.4 TC-LIM-06's named P3.3 obligation, discharged

TC-LIM-06 recorded lease, heartbeat, attempt, timeout and queue consumer
evidence as **a named P3.3 obligation** rather than manufacturing it in P3.1,
and reported N-21 and N-22 as having no P3.1 consumer at all. All of it now has
one:

| Number | Consumer | Evidence |
|---|---|---|
| N-23 lease (exact 60) | the claim and heartbeat statements | `test_p3_3_worker.py` `…the_worker_consumes_the_validated_lease_and_attempt_bounds` — the interval PostgreSQL wrote is compared to the configured value, at claim and at renewal |
| N-23 heartbeat (≤ 20) | `WorkerRuntime`'s loop period | same case; the runtime waits on the configured value |
| N-43 attempts (3) | the claim predicate, the reaper and the self-abandon | `test_p3_3_jobs.py` TC-JOB-05 and TC-JOB-13 drive it to exhaustion |
| N-45 attempt timeout (300) | the runtime's hard cap | `WorkerComposition` is asserted to hold the canonical 300; the abandon *statement* is TC-JOB-16, and that an abandoned attempt commits **nothing** is TC-JOB-18 (2026-08-18) |
| N-42 queue depth (5) | `ReconciliationJobService.enqueue_preview` | `test_p3_3_jobs.py` TC-JOB-12 fills to the **configured** depth and asserts the next is refused |
| N-41 concurrency (1) | one in-flight job per runtime | `test_p3_3_worker.py` `…two_workers_running_concurrently_execute_one_job_each`, and TC-JOB-24 for the thread the runtime could not stop (2026-08-18) |
| N-21 pagination | R-49 | `test_p3_3_audit_search.py` — default and clamped maximum both read from the configured bounds |
| N-22 poll floor | R-44 | `test_p3_3_disclosure_and_bounds.py` — `Retry-After` and the poll hint both carry it, and agree |
| N-24 retention | `tools.job_retention` | **Corrected 2026-08-18.** The earlier claim described a command that could not run: its `UPDATE … SET result_id = NULL` violated `CHECK ((state = 'completed') = (result_id IS NOT NULL))` for every completed job. TC-OPS-06…17 now run the production transaction against real PostgreSQL — every eligibility shape, the parent/apply graph, report mode, audit rollback, idempotence and the `--limit` refusals. The **staging** rehearsal of a real sweep on real volume is still not claimed |
| N-46 preview validity | `enqueue_apply` | `test_p3_3_jobs.py` `…a_preview_past_n46_cannot_be_confirmed` |
| N-44 reaper interval | `WorkerRuntime.tick` | exercised by every reaper case; its *liveness* signal is the `expired_leases` health check |

### 21.4a The commit fence and the retention sweep (added 2026-08-18)

| Case | What it proves | Evidence |
|---|---|---|
| TC-JOB-17 | A cancellation landing after the executor's last cooperative check and before the import commit leaves **no** import, character, mapping or success-audit row, and the job ends `cancelled` | `test_p3_3_effect_fence.py` `…cancellation_after_the_last_python_check…` |
| TC-JOB-18 | A timeout self-abandon in the same window leaves no effect from the abandoned attempt; the job requeues | same file, `…self_abandon_in_the_commit_window…[timeout-requeues]` |
| TC-JOB-19 | A kill-switch self-abandon at the last attempt leaves no effect; the job fails with `attempts_exhausted` | same file, `…[kill-switch-at-the-last-attempt-fails]` |
| TC-JOB-20 | Lease expiry, a reaper requeue and a **new claim by another worker** while the original thread continues: the old token mutates nothing and the successor owns the job | same file, `…reaped_lease_and_a_new_claim…` |
| TC-JOB-21 | The apply committing immediately before a cancellation: one import, a `completed` durable outcome, and the cancellation **refused** | same file, `…apply_that_commits_first_refuses_the_cancellation…` |
| TC-JOB-22 | A crash after the effect commits and before the result is published: the job is **not** reaped, no attempt is spent, and the recovery pass publishes one `completed` result over one import. **Corrected 2026-08-18** by the effect-publication remediation, which changed the intermediate state: it used to be `queued`, and the result used to come from re-executing the attempt and finding a duplicate | same file, `…crash_between_the_effect_and_the_result…` |
| TC-JOB-23 | The **same worker instance** reclaiming with a new token cannot make its old attempt valid again | same file, `…same_instance_reclaiming…` |
| TC-JOB-24 | A worker holding an execution thread it could not stop claims nothing else and reports it | same file, the two outstanding-attempt cases |
| TC-JOB-25 | R-41's invalidation landing in the commit window leaves no effect; the job ends `stale` | same file, `…invalidation_in_the_commit_window_leaves_no_effect` |
| TC-JOB-26 | Neither R-41 nor R-46 can make an apply whose effect committed `stale`, while an ordinary live job in the same statement still is | same file, `…apply_whose_effect_committed_can_no_longer_be_made_stale` |
| TC-MIG-22 | Migration 0012 round-trips (upgrade → downgrade → upgrade) with an identical catalogue and untouched append-only history, compared on `xmin` | `test_migration_0012_round_trip.py` |
| TC-OPS-06 | An expired completed preview and its result are removed | `test_p3_3_job_retention.py` |
| TC-OPS-07 | An expired completed apply goes while its `snapshot_imports` receipt survives | same file |
| TC-OPS-08 | A `stale` preview whose result is linked only from the result side is removed | same file |
| TC-OPS-09 | `failed`/`cancelled` jobs with and without result rows follow the documented terminal-age policy | same file (four parameterisations) |
| TC-OPS-10 | An old job whose result has **not** expired is retained | same file |
| TC-OPS-11 | A `queued` or `running` job is never removed | same file |
| TC-OPS-12 | An expired preview with an unexpired apply child retains the whole graph | same file |
| TC-OPS-13 | A wholly eligible preview/apply graph is removed with no FK or check failure | same file |
| TC-OPS-14 | Mixed eligible and ineligible graphs under one `--limit`: only the removable ones go, and the counts say so | same file |
| TC-OPS-15 | Report mode writes nothing and audits nothing | same file (both the sweep object and the command) |
| TC-OPS-16 | An injected audit failure — a real `BEFORE INSERT` trigger — rolls back every deletion | same file |
| TC-OPS-17 | Immutable rows are unchanged but for the sweep's own bounded event; a repeated sweep removes zero; zero, negative and excessive `--limit` values are refused **before** a connection is opened | same file |
| TC-OPS-18 | **Added 2026-08-24 (supervised-session finding S-4 / security finding S5).** `/healthz` reports `identity_provider` from a probe, not a literal. The adapter issues one `GET` to the least-privileged documented endpoint with no `Authorization` header, no client id, no client secret and no scope; classifies 5xx and 429 as unavailable and any other answer as reachable, matching the rule the rest of the adapter uses; answers `False` rather than raising for a transport failure, a timeout or any unexpected error, so a degraded provider cannot turn the health endpoint into a `500`; and bounds the request by its own ceiling, tighter than the configured API timeout. The route carries the boolean into the report, so an unreachable provider yields `503`/`degraded` with `identity_provider: false` while every other check still answers for itself. No socket is opened by the test | `tests/web/test_provider_health_probe.py` |

### 21.4b Effect-publication recovery (added 2026-08-18)

Every case is in `tests/web/test_p3_3_effect_recovery.py` unless stated, runs
against real PostgreSQL, and asserts the durable rows — `snapshot_imports`,
`characters`, `external_actor_mappings`, the `snapshot_import.applied` audit
event, the result row and the completion event — rather than a return value.

| Case | What it proves | Evidence |
|---|---|---|
| TC-JOB-27 | The finding's own interleaving, through the HTTP route: effect commits, process dies, lease expires, the production reaper declines the row, **R-45 is refused `409` with `already_applied`**, `cancel_requested_at` is never written, no audit event claims a cancellation was requested, and the next recovery completes the job with no second effect | `…r45_refuses_to_cancel_an_effect_awaiting_recovery` |
| TC-JOB-28 | The `queued` branch of `request_cancel` refuses a committed effect, and the control: an ordinary `queued` job is still cancelled outright | `…queued_branch_of_r45_refuses_a_committed_effect`, `…ordinary_queued_job_is_still_cancelled_outright` |
| TC-JOB-29 | R-45, R-41's `mark_stale`, R-46's `invalidate_for_snapshot` and the worker's self-abandon are **all** refused over a committed effect, **both before and after lease expiry**, and the job stays recoverable through all of it | `…cancellation_and_invalidation_cannot_win_before_or_after_lease_expiry` |
| TC-JOB-30 | The effect commits on **attempt three**, the process dies, the lease expires: the job ends `completed` rather than `failed`, `attempts` is still 3, and no fourth attempt is granted | `…effect_committed_on_the_last_attempt_is_completed_not_failed` |
| TC-JOB-31 | Neither reaper branch fires over a committed effect at **any** attempt count, and the control: ordinary expired leases are still requeued and still exhausted, in the same pass | `…reaper_leaves_a_committed_effect_for_publication_at_every_attempt_count` (3 parameterisations), `…expired_lease_with_no_committed_effect_is_still_reaped` |
| TC-JOB-32 | The recovered result names the original immutable import, carries its committed counts, reports `duplicate: false` and `recovered: true`, reproduces the fence's stored summary key for key, and the completion event says the same from the same summary and names the lease that stopped answering | `…recovered_result_names_the_original_import_and_says_it_was_recovered` |
| TC-JOB-33 | Repeated recovery and reaper passes produce **exactly one** result row and **one** completion audit event | `…repeated_recovery_passes_publish_once` |
| TC-JOB-34 | Concurrent recovery serializes to one publication: a second connection holding the production row lock makes a concurrent pass write nothing, and two real runtimes racing produce one result | `…two_recovery_passes_serialize_to_one_publication`, `…concurrent_recovery_threads_publish_exactly_one_result` |
| TC-JOB-35 | An injected audit failure — a real committed `BEFORE INSERT` trigger — rolls the result row and the state transition back together, and the pass is safely retryable afterwards with nothing cleaned up | `…audit_failure_during_recovery_rolls_the_publication_back` |
| TC-JOB-36 | A **live** lease is left to the worker that holds it; recovery acts only once the lease has lapsed. A stalled worker still recovers, because `tick` reaps and publishes before it consults its own state | `…live_lease_is_left_to_the_worker_that_holds_it`, `…tick_recovers_even_while_the_worker_is_stalled` |
| TC-JOB-37 | Direct SQL cannot write `failed`, `cancelled` or `stale` over a committed effect (`committed_effect_is_never_denied`), and cannot record a committed effect without its publication payload (`effect_result_accompanies_the_fence`) — with the control that an ordinary job still reaches every terminal state | `…direct_sql_cannot_write_a_state_that_denies_a_committed_effect` (3 parameterisations), `…committed_effect_cannot_be_recorded_without_its_publication`, `…ordinary_job_still_reaches_every_terminal_state` |
| TC-MIG-23 | **On an empty/unused schema** (this module seeds only `audit_events`), migration 0013 round-trips (upgrade → downgrade → upgrade) with an identical catalogue and untouched append-only history compared on `xmin`; the downgrade leaves 0012's column and constraint alone; `upgrade()` refuses a database holding a pre-0013 committed effect **before** it adds anything, naming the remedy; and the logical-schema document records the column and both constraints. **Not evidence for a data-bearing rollback** — that is §21.4c | `test_migration_0013_round_trip.py` |

Every case above was first run against the pre-remediation implementation and
failed there; the reproduction is recorded in the P3.3 submission.

### 21.4c Migration 0013's rollback boundary (added 2026-08-18)

Every case is in `tests/web/test_migration_0013_rollback_boundary.py`, drives the
**production** Alembic revisions through the suite's guarded subprocess helper,
and runs against real PostgreSQL. The committed effects are produced by the
production apply path — a real preview, a real apply, a real commit fence and a
real `snapshot_imports` receipt — not by seeding a row into a shape the platform
never writes. Nothing is stubbed and no schema is hand-approximated.

| Case | What it proves | Evidence |
|---|---|---|
| TC-MIG-24 | A database holding a **truthfully completed apply** — its receipt, its durable result, its fence columns — is refused a downgrade of 0013. The refusal names both counts and the operator's action, and happens **before** either constraint or the column is dropped | `…refuses_a_published_committed_effect` |
| TC-MIG-25 | A database holding a **committed but unpublished** effect is refused the same way, **and the ability to publish it survives**: `WorkerRuntime.recover()` afterwards publishes exactly the result the fence made durable, key for key, with the `recovered` marker | `…refuses_a_committed_but_unpublished_effect` |
| TC-MIG-26 | The two populations are counted **separately** in the refusal, because they cost differently, and the message carries counts rather than a row dump | `…names_both_populations_separately` |
| TC-MIG-27 | The refused database is **unchanged and usable**: the job, result, immutable receipt and append-only audit rows all compare equal on `xmin`, the catalogue fingerprint is identical, `alembic_version` is still `0013`, and the effect it holds can still be published | `…leaves_history_untouched_and_the_database_usable` |
| TC-MIG-28 | **Below** the boundary the downgrade is genuinely supported with realistic rows — a completed preview and its result, a failed apply, a refused import receipt, append-only audit history — and `upgrade → downgrade → upgrade` restores the identical catalogue with every durable row unchanged on `xmin` | `…succeeds_below_the_boundary_with_realistic_rows` |
| TC-MIG-29 | A migration that fails part-way leaves the **complete** pre-migration schema and data, never a partial state, in **both** directions: a downgrade interrupted after its first `DROP CONSTRAINT` succeeds leaves 0013 whole with `alembic_version` unmoved; a refused upgrade from 0012 adds no column, creates no constraint and leaves every row untouched | `…an_interrupted_downgrade_leaves_the_complete_pre_migration_schema`, `…an_interrupted_upgrade_leaves_the_complete_pre_migration_schema_and_rows` |
| TC-MIG-30 | The offline (`--sql`) downgrade script carries the **same guard as executable SQL**, emitted before the first `DROP`, rather than a comment; and `docs/operations/web-portal.md` records the boundary the migration enforces | `…the_offline_downgrade_script_carries_the_same_guard`, `…the_operations_document_records_the_rollback_boundary` |
| TC-MIG-31 | **The guard decides under a lock.** With a real worker/effect transaction held open immediately before its commit, the real `alembic downgrade 0012` is observed waiting at `LOCK TABLE reconciliation_jobs IN ACCESS EXCLUSIVE MODE` — proved from `pg_stat_activity.query`, not from a sleep — then sees the fence the worker commits, refuses before any drop, and leaves revision, schema, payload, receipt and the ability to publish intact | `…a_downgrade_started_during_an_in_flight_effect_refuses_after_it_commits` |
| TC-MIG-32 | **Lock-queue fairness, and only that** (re-scoped 2026-08-19). While the migration's `ACCESS EXCLUSIVE` request is still **ungranted** — queued behind an ordinary reader — a fence writer arriving afterwards cannot overtake it: the writer's `ROW EXCLUSIVE` request is observed ungranted behind the migration's pending request, and the refusal counts only the pre-existing effect. It makes **no** claim about a lock the migration was granted; that is TC-MIG-37. Previously named `…arriving_after_the_lock_cannot_commit_until_it_finishes` and cited for TC-MIG-37's condition, which it never proved | `…a_fence_writer_arriving_behind_a_pending_lock_request_cannot_overtake_it` |
| TC-MIG-33 | **Offline atomicity, positionally.** One `BEGIN;` and one `COMMIT;`; lock → guard → count → refusal → drops in that order; and no transaction control between the lock and the last drop, so the lock is never released mid-guard | `…the_offline_script_locks_inside_its_own_transaction_before_it_decides` |
| TC-MIG-34 | The **generated script**, applied with `psql` as an operator would, waits at its own lock and refuses an effect that commits while it waits | `…the_generated_script_refuses_an_effect_that_commits_while_it_waits` |
| TC-MIG-35 | **Approved N-24 retention reopens the boundary truthfully.** A real completed apply, the production retention transaction with its normal audit behaviour, then `0013 → 0012 → 0013` with exact catalogue parity and every surviving immutable row unchanged on `xmin` | `…approved_retention_reopens_the_boundary_and_the_round_trip_is_exact` |
| TC-MIG-37 | **A writer starting under the migration's *granted* lock cannot commit until that transaction ends** (added 2026-08-19). Every step is read from `pg_locks`/`pg_stat_activity`, never from a sleep: the production `alembic downgrade 0012` transaction holds a **granted** `AccessExclusiveLock` on `reconciliation_jobs`; the same backend pid, `virtualtransaction` and `xact_start` still hold it when the writer has queued, so no `COMMIT` or other boundary intervened; only then does the production `hold_for_effect` fence begin, for an apply job it has really claimed; its `ROW EXCLUSIVE` request is observed **ungranted** — and, since the 2026-08-19 fourth correction, that request is bound to the writer itself: the writer announces its backend pid from inside its own transaction over a bounded queue, the poll matches **only** that pid, `pg_stat_activity` for that pid must be the production `hold_for_effect` statement rather than `seed_import`, connection setup or an unrelated session, and the transaction identity observed while it is queued (`pid`, `virtualtransaction`, `backend_xid`, `xact_start`) must be **identical** to the one re-observed holding the granted lock, idle, with the fence run and not committed; the migration transaction then ends by rollback; and only afterwards is that same transaction released and commits, leaving one committed effect the migration provably never saw, with the three rolled-back objects restored and the catalogue fingerprint unchanged. The migration is held after the grant by locking Alembic's own `alembic_version` row **from the test** — no production module, no revision statement and no emitted SQL is changed, and no production pause hook exists. **Scope stated exactly:** this does not bind the granted lock to the guard's own `LOCK TABLE` (the three `ALTER TABLE` statements each require that mode anyway, so it passes against a guard with the statement removed); the lock's placement *before the count* is TC-MIG-31, which fails against that mutation | `…a_fence_writer_starting_under_the_held_lock_cannot_commit_until_it_ends` |
| TC-MIG-38 | **TC-MIG-37's failure-path cleanup is bounded and total** (added 2026-08-19). The same scenario — the `alembic_version` row held from outside Alembic, the production `alembic downgrade 0012` holding a **granted** `AccessExclusiveLock` while blocked on that row, and the production `hold_for_effect` fence issued behind it from a writer that announced its own backend pid — is driven to a **controlled** assertion failure at two named points: while the writer is queued behind the migration's lock (the migration child **alive**), and after the fence has executed and is parked before its `COMMIT` (the migration transaction already ended). Measured from the moment of failure, the release returns inside an explicit ceiling; the migration child is **reaped** rather than merely signalled; the writer thread, its transaction and the holder's transaction and connection are released; `pg_locks`/`pg_stat_activity` show no `ACCESS EXCLUSIVE`/`ROW EXCLUSIVE` lock on `reconciliation_jobs`, no open transaction for the writer's backend and no surviving migration backend; the killed migration's drops are rolled back and the catalogue fingerprint is unchanged; and the **original** assertion is what surfaces, with nothing attached to it. The child is wrapped in `_RecordingChild`, which delegates every call to the real `subprocess.Popen` and adds only a record of the `timeout` each collection carried — so the case asserts that the collection was **bounded at the call**, which is the only way a real child can falsify the defect: `SIGKILL` collects a real Alembic process immediately, so an unbounded `communicate()` returns at once and no timing, reaping or residue assertion can see it | `…the_held_lock_cleanup_is_bounded_and_total_when_the_case_fails` (2 parameters) |
| TC-MIG-39 | **Cleanup is bounded even when the migration child will not die**, which no real child can be made to do on demand. Against an injected fake process, cleanup collects the child **with a timeout, twice, and never once without one** — the pre-fix defect asserted directly on what the child was asked — returns well inside its ceiling, **reports** the stuck child rather than swallowing it, and still completes every other step: the writer is released and joined, the row lock rolled back and the holder closed. The real PostgreSQL concurrency evidence is TC-MIG-38 and TC-MIG-37, which falsify the defect in their own right; this case exists only for the branch where the child genuinely never dies | `…the_held_lock_cleanup_is_bounded_when_the_migration_child_will_not_die` |
| TC-MIG-40 | **The earliest failure paths are bounded too**: a failure before the migration child exists and before `writer.start()` — the same shape as a failure before the pid announcement — still releases the commit event, rolls back the row lock and closes the holder, does **not** join an unstarted thread, and reports no problem it does not have | `…the_held_lock_cleanup_is_bounded_before_the_migration_or_the_writer_starts` |
| TC-MIG-41 | **A cleanup problem is reported without replacing the failure under diagnosis.** When cleanup cannot release something, the original assertion is re-raised unchanged and the cleanup's problems are attached to it as notes; on the **passing** path an unreported cleanup problem becomes the failure instead, because bounded, total cleanup is part of what these cases claim | `…a_cleanup_problem_is_reported_without_replacing_the_failure_under_diagnosis` |
| TC-MIG-42 | **Cleanup is bounded when the holder's `rollback()` never returns** (added 2026-08-19, sixth correction). The path the fifth correction's ceiling did not count: `release()` called `self._holding.rollback()` on the calling thread, and nothing bounds that call — catching its exception describes an operation that ended, it does not bound one that never does. Against a deterministic stand-in that blocks exactly where the real call would, the release returns inside its **complete** documented ceiling and well inside the stand-in's period; the blocked step is **reported**, naming the call and its bound; **every later step is still attempted** and the six-step order is asserted from a recorded list rather than read off the source; the writer's commit event is set and its bounded join really joins the parked writer; the connection is **not** closed out from under the thread still inside it and the independent backend disposal is attempted in its place; the thread left owning the call is a daemon, is recorded on the cleanup, and owns a connection detached from its pool before anything blocked; and the assertion under diagnosis surfaces with the cleanup problems as notes. Asserted **at the call** — that the rollback was not made on the calling thread — so the pre-fix shape is caught even on a run where it happened to return quickly | `…the_held_lock_cleanup_is_bounded_when_the_row_lock_rollback_never_returns` |
| TC-MIG-43 | **Cleanup is bounded when `holder.close()` never returns**, the mirror path, with the same properties asserted and one more specific to it: the rollback provably **completed** before the close blocked, so what blocked is the close and not something inherited from the step before it | `…the_held_lock_cleanup_is_bounded_when_closing_the_holder_never_returns` |
| TC-MIG-44 | **A blocked database cleanup call fails a case that otherwise passed**, for both calls. `_released()` has no failure to preserve on the passing path, so an unreported cleanup problem has to become the failure — otherwise a case could pass while leaving a live backend holding the `alembic_version` row lock in the **shared** disposable database | `…a_blocked_database_cleanup_call_fails_the_case_that_otherwise_passed` (2 parameters) |
| TC-MIG-36 | **An unpublished effect blocks at any age**, because retention removes only terminal jobs — asserted with a sweep ten years in the future — and **fixture portability**: the realistic module runs green with pytest's base temporary directory below a deliberately untrusted parent, while the production-default control still refuses that parent | `…an_unpublished_effect_blocks_the_downgrade_at_any_age`, `…the_realistic_rollback_cases_run_below_an_untrusted_parent`, `…the_production_ancestor_rule_still_refuses_an_untrusted_parent` |

TC-MIG-24 … TC-MIG-30 were first run against the pre-remediation migration and
failed there — **8 failed, 1 passed** — for the intended reason: the downgrade
succeeded on a database holding a truthfully completed apply, and the re-upgrade
then refused. The transcript is in the P3.3 submission §14.7.1.

TC-MIG-31 and TC-MIG-32 have their **own, separate** pre-fix evidence, taken
against the guard with only its `LOCK TABLE` statement removed: the migration was observed waiting
at `ALTER TABLE reconciliation_jobs DROP CONSTRAINT
ck_reconciliation_jobs_committed_effect_is_never_denied` — the count had already
run under its own MVCC snapshot and seen zero, and only the DDL was queued behind
the worker, which is the unsafe interleaving itself. The fixture-portability
defect (TC-MIG-36) has its own separate before/after evidence and is **not** the
red phase of the concurrency regression; the two are different defects.

TC-MIG-37 is new in the 2026-08-19 correction and is **not** offered as a
regression for the guard's lock placement — it passes against the
`LOCK TABLE`-removed guard, which was verified rather than assumed, and the
verification is recorded in the P3.3 submission §16.2. What it is a regression
for is the exclusion property itself: if a writer beginning under the granted
lock could commit before the migration transaction ended, step 4 would observe a
granted `ROW EXCLUSIVE` request or a completed fence and the case would fail.
Since the 2026-08-19 fourth correction it is additionally a regression for the
**identity** of that exclusion: with the writer deterministically held before its
fence and only an unrelated session queued for the same mode on the same
relation, the old broad predicate is satisfied and the corrected one cannot be
(P3.3 submission §17.3).

TC-MIG-38…TC-MIG-41 are new in the 2026-08-19 **fifth** correction and are about
TC-MIG-37's **cleanup**, not its property. They are cited for exactly one claim —
that a failing TC-MIG-37 releases every connection, transaction, thread and
process within an explicit bound, and that a cleanup problem is reported rather
than substituted for the assertion under diagnosis. They are **not** additional
evidence for the exclusion property, for the guard's lock placement or for the
rollback boundary, and TC-MIG-37's own scope statement above is unchanged.
TC-MIG-39…TC-MIG-41 use an injected fake process and stand-in holder objects for
branches a real Alembic child cannot be made to take on demand; the real
PostgreSQL concurrency case is TC-MIG-38, which drives the production revision and
the production fence statement. Falsification: against the pre-fix
`kill(); communicate()` shape, **both TC-MIG-38 parameters** fail — the surviving
child collected with `timeout=None`, and the already-exited child not collected at
all — as do TC-MIG-39 and TC-MIG-41 (P3.3 submission §18.4). TC-MIG-40 correctly
still passes: it has no migration child for the mutation to reach.

TC-MIG-42…TC-MIG-44 are new in the 2026-08-19 **sixth** correction and have the
same scope as TC-MIG-38…TC-MIG-41 and no wider: they are about TC-MIG-37's
cleanup, and are **not** evidence for the exclusion property, the guard's lock
placement or the rollback boundary. They use deterministic stand-ins for the two
non-returning database calls because neither branch can be produced on demand
from healthy PostgreSQL — which is precisely why the fifth correction's real
database regression and its instant fake transaction and connection falsified
neither. The real PostgreSQL cleanup evidence remains TC-MIG-38. Falsification:
restoring an unbounded direct `self._holding.rollback()` fails TC-MIG-42 and
TC-MIG-44's `rollback` parameter; restoring an unbounded direct
`self._holder.close()` fails TC-MIG-43 and TC-MIG-44's `close` parameter; both
fail deterministically and neither hangs. The fifth correction's `communicate()`
falsification is retained and reruns unchanged (P3.3 submission §19.4).

Metadata parity at head is unchanged and remains
`tests/test_database_postgresql.py::test_migration_matches_table_metadata`
(`alembic check`); this remediation adds no metadata.

### 21.5 What P3.3 does **not** claim

Unchanged from §20, and one of them is worse than it looks:

- **TC-PERF-02 has never been measured, at all.** Rehearsal B previewed a real
  32-Actor folder in 9.566 s and **applied nothing**; the 500-Actor benchmark's
  1.31 s apply used synthetic Actors ~233× smaller than real ones (RA-5). P3.3
  delivers the durable job model that measurement needs and **does not simulate
  the measurement**. No number in this package is a real-folder apply.
- **TC-PERF-01** — worker peak resident memory against N-47's 1 GiB guard — is
  unmeasured. The guard is a guard, not a measurement.
- **TC-PERF-03**, **TC-LIM-02**, **TC-SEC-07's browser half** and **TC-OPS-01…05**
  remain unrun because staging does not exist (I-06).

A gate recommendation that treated any of these as passing on the automated
evidence above would be misreporting.

## 22. D-03 correction evidence map — added 2026-08-19, by addition only

Nothing in §§1–21 is rewritten. This section maps the six accepted decisions of
change-log `C-P3.4-A` to the tests that hold them, so a reviewer can go from a
decision to its evidence without reading the whole table.

| Item | Accepted decision | Rows | Module |
|---|---|---|---|
| D-03-1 | Application-served `/static/` surface, mounts inside the closed inventory | TC-STATIC-01…07, TC-SEC-14, TC-STRUCT-01 (mount half) | `tests/web/test_static_asset_surface.py`, `tests/web/test_structural_guards.py`, `tests/web/test_security_controls.py` |
| D-03-2 | `ConfirmScope` defined in `vm-1` | contract-vs-implementation field and order equality; the presence rule; the re-read rule | `tests/web/test_d03_contract_correction.py` |
| D-03-3 | `CharacterFilters` defined in `vm-1` | contract-vs-implementation field and order equality; the search-fact rule | `tests/web/test_d03_contract_correction.py` |
| D-03-4 | VM-13's `csrf_token` recorded; provenance claim corrected | field present and documented; the retracted claim absent from the source **and** still absent from the accepted P3.2 submission; R-37 still refuses a missing, forged and borrowed token | `tests/web/test_d03_contract_correction.py` |
| D-03-5 | R-36 recorded as `200` HTML · VM-13 (`denied`) | `200` with no `Location`; the corrected contract row parsed and asserted; `additional_provider` still single-member | `tests/web/test_d03_contract_correction.py` |
| D-03-6 | Dedicated `DeniedView` (VM-22) | TC-VM-06; byte-identity re-asserted under the new carrier on both route surfaces; authorization-before-lookup; VM-02's non-member page preserved | `tests/web/test_d03_contract_correction.py`, `tests/web/test_structural_guards.py` |

### 22.1 What this correction does **not** claim

- **TC-UI-06 is not delivered.** TC-SEC-14 asserts the same-origin and
  `design-prototype/` rules over the *current* template corpus and the new static
  root. The delivery-plan row belongs to P3.4 and to the production corpus that
  does not exist yet.
- **No browser, real-device, screen-reader, staging or production evidence** is
  produced or claimed. Every row above is a source, unit or in-process ASGI
  response check. TC-UI-07, TC-UI-08 and TC-UI-09 are untouched.
- **No performance claim.** TC-PERF-01…03 remain unmeasured, as §21.5 records.
  Serving assets from `freedom-web` is an accepted design trade recorded in
  operational contract §4.4, not a measured one.
- **The static root is empty.** No production asset exists to test, so no test
  claims one does.

## 23. Shell/navigation contract evidence — added 2026-08-23, by addition only

C35-05/R35-17. No accepted row is rewritten.

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-SHELL-01 | Each accepted caller state (`N`, `M`, `C`, `A`, `CA`) is offered exactly its accepted destinations | unit | `test_shell_navigation_contract.py::test_each_caller_state_is_offered_exactly_its_accepted_destinations` |
| TC-SHELL-02 | The anonymous shell offers only anonymous destinations, and no logout or token | unit | `::test_the_anonymous_shell_offers_only_anonymous_destinations` |
| TC-SHELL-03 | No authenticated caller is ever shown `Login` (F-17's original symptom) | unit | `::test_an_authenticated_caller_is_never_offered_login` |
| TC-SHELL-04 | Platform administrator acquires no Council navigation | unit | `::test_platform_administrator_does_not_acquire_council_navigation` |
| TC-SHELL-05 | Continuity scope (N-65) is offered only role capabilities and identities, even when the caller also holds Council | unit | `::test_break_glass_is_offered_only_what_its_scope_permits`, `::test_continuity_scope_strips_council_navigation_even_from_a_council_holder` |
| TC-SHELL-06 | A valid session gets logout and that session's own CSRF token | unit | `::test_a_valid_session_gets_logout_and_the_session_s_own_token` |
| TC-SHELL-07 | Missing, malformed, expired and revoked sessions yield no logout and no token | unit | `::test_no_session_means_no_logout_and_no_token` |
| TC-SHELL-08 | At most one destination is current, resolved by longest prefix | unit | `::test_the_current_page_is_resolved_by_longest_match`, `::test_at_most_one_destination_is_ever_current` |
| TC-SHELL-09 | **Hiding a link does not deny a route** — the guard refuses independently | direct HTTP | `::test_hiding_a_link_does_not_deny_the_route` |
| TC-SHELL-10 | **Naming a destination does not bypass a route** | direct HTTP | `::test_rendering_a_link_would_not_bypass_a_guard` |
| TC-SHELL-11 | The header renders only the shell's links, marks exactly one current, and carries no button but the sign-out submit | template | `test_p3_4_shell_and_components.py` |

| TC-SHELL-12 | **Request boundary**: every caller state's rendered frame, through the real preamble, refresh, `authorize()`, render and template | direct HTTP + database | `test_shell_request_boundary.py`, 28 cases |
| TC-SHELL-13 | An authenticated caller **denied** a route still receives their own frame and logout token, not the anonymous one | direct HTTP | `::test_a_denied_page_still_carries_the_authenticated_frame` |
| TC-SHELL-14 | The rendered logout token ends the session; missing, empty, wrong and **another session's** token are each refused `403` and leave the session alive | direct HTTP | `::test_the_rendered_token_logs_the_caller_out`, `::test_logout_refuses_*` |
| TC-SHELL-15 | A refresh that adds or **removes** authority moves the frame with the route decision | direct HTTP, at the `_close` seam | `::test_a_refresh_that_*` |
| TC-SHELL-16 | `home_href` is always a destination the caller may reach | unit + request boundary | `::test_the_brand_destination_is_one_this_caller_may_reach` |
| TC-SHELL-17 | **Public full pages** carry the caller's own frame: anonymous for anonymous, malformed, empty, expired and revoked; authenticated with sign-out for member, administrator and break-glass | direct HTTP | `::test_a_public_page_*` |
| TC-SHELL-18 | A public page whose caller's authority is **not fresh** renders the conservative session-only frame, without making a provider call | direct HTTP | `::test_a_public_page_gives_a_stale_caller_the_conservative_frame` |
| TC-SHELL-19 | A logout token rendered on a **public** page ends the session | direct HTTP | `::test_a_public_page_logout_token_actually_works` |
| TC-SHELL-21 | A request with **no cookie** renders the public page without resolving a session at all | direct HTTP | `::test_no_cookie_performs_no_session_lookup` |
| TC-SHELL-22 | Malformed, overlong and unknown-but-well-formed tokens each render the anonymous shell | direct HTTP | `::test_an_unusable_token_renders_the_anonymous_shell` |
| TC-SHELL-23 | A degraded session store renders `503` with security headers and `no-store`, **never** an anonymous `200` | direct HTTP | `::test_a_degraded_session_store_does_not_render_an_anonymous_success` |
| TC-SHELL-24 | An unexpected implementation error reaches the safe-error boundary as `500`, disclosing no message, class, traceback, module, database target or SQL | direct HTTP | `::test_an_unexpected_error_reaches_the_safe_error_boundary` |
| TC-SHELL-25 | Cancellation is not converted into a rendered page | direct HTTP | `::test_cancellation_is_not_converted_into_anonymous_rendering` |
| TC-SHELL-26 | A degraded page discloses no cookie value, account id, session id, capability or provider detail | direct HTTP | `::test_a_degraded_or_error_page_discloses_no_caller_material` |
| TC-SHELL-27 | A protected request resolves its session **exactly once** — the public helper adds no second resolution | direct HTTP | `::test_a_protected_request_still_resolves_its_session_once` |
| TC-SHELL-20 | A refusal from a failed refresh renders `503` with the conservative authenticated frame — sign-out available, no privileged link, no capability/session/provider leakage | direct HTTP | `::test_a_service_degraded_refusal_*`, `::test_a_degraded_page_leaks_no_*` |

**Not covered here, and stated rather than implied:** no browser has rendered this
frame. TC-UI-01/02 remain **Not Run**, and the supervised browser evidence for
logout and navigation belongs to the staging package with them. TC-SHELL-15 drives
the refresh at the `_close` seam rather than through a real provider round trip:
`_refresh_plan()` returns `None` without a stored OAuth token grant and the seeded
callers have none, so an end-to-end Discord refresh is **not** exercised.
