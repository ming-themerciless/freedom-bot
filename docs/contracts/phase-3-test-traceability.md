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

## 5. Identity, accounts and linking — P3.1/P3.2

| ID | Test | Level | Evidence |
|---|---|---|---|
| TC-ID-01 | An account survives unlinking a provider: sessions, `character_access` and audit attribution all still resolve | service | automated (database) |
| TC-ID-02 | Sessions and `character_access` reference account ids only; no query in the web module filters by a Discord snowflake | structural + service | automated |
| TC-ID-03 | `(provider_key, subject)` uniqueness is enforced by the database, including against a **retired** row | real PostgreSQL constraint | automated (database) |
| TC-ID-04 | Retiring an identity keeps the row and keeps historical audit attribution readable | service | automated (database) |
| TC-ID-05 | **Structural:** `external_identities` has no display-name, username or email column, and no code path links accounts by any name-like value | AST/schema introspection | automated |
| TC-ID-06 | Name-collision parametrization: identical usernames, case variants, NFC/NFD variants, homoglyphs, and identical global names never merge or auto-link accounts | service | automated (database) |
| TC-ID-07 | Unlinking the last usable identity is refused; for the protected account, enrolled credentials count as the recovery route and for an ordinary member they do not | service | automated (database) |
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
| TC-MIG-09 | M-2 writes **no** `character_access` row; only R-29 confirmation does | service | automated (database) |
| TC-MIG-10 | Ambiguous and unresolved proposals are not confirmable, persist across runs, and grant no access even when the browser submits a confirmation | service + direct HTTP | automated (database) |
| TC-MIG-11 | Every created link names the confirming Council member, a reason and a correlation ID in one atomic transaction with its audit event | service | automated (database) |
| TC-MIG-12 | The Sheet is never written: the read-only boundary is exercised and a write attempt through the adapter raises | service | automated |
| TC-MIG-13 | Injected audit-write failure during confirmation rolls back the grant | service | automated (database) |
| TC-MIG-14 | **The constraint swap round-trips.** `upgrade → downgrade → upgrade` of the revision that replaces `ck_audit_events_human_action_has_an_actor` leaves an identical schema and identical data; the downgrade restores the legacy constraint `NOT VALID`, and does so successfully **on a database that already contains account-attributed rows** — the case a validating restore would fail | real PostgreSQL | automated (database) |
| TC-MIG-15 | **Constraint inventory.** After the revision, the check constraints on `audit_events`, `snapshot_imports` and `foundry_snapshots` equal the inventory documented in schema §6.2.1 exactly: the account-aware check present, the legacy Discord-only check absent, `foundry_snapshots` unchanged, nothing extra. Guards against a later migration quietly reintroducing a Discord-only attribution rule | schema introspection | automated (database) |
| TC-MIG-16 | Control totals T7 and T8 hold; a deliberately corrupted fixture makes T8 fail and aborts the migration | real PostgreSQL | automated (database) |

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
| TC-STRUCT-01 | **The application's registered route set equals the accepted inventory exactly** — no extra route, no missing route (route contract §1) | route introspection vs. parsed document | automated |
| TC-STRUCT-02 | The implemented view-model set equals the documented `vm-1` set, with matching field names and types | introspection vs. parsed document | automated |
| TC-STRUCT-03 | JSONB appears only on the two columns justified under plan §7.3.1, and no new generic key/value character-state table exists (extends `tests/test_rejected_scope_absent.py`) | schema introspection | automated (database) |
| TC-STRUCT-04 | **No character-game-state correction endpoint exists**: no route, no application service, and forged submissions to plausible paths mutate nothing | structural + direct HTTP | automated (database) |
| TC-STRUCT-05 | The web process cannot import the bot's `config.py` | import graph | automated |
| TC-STRUCT-06 | Every startup refusal S-01…S-15 is exercised with deliberately wrong configuration and refuses with the documented typed error, naming variables and never values | unit | automated |
| TC-STRUCT-07 | **Added 2026-08-15 (settings-construction remediation, RAID I-10).** The five public settings types are valid by construction, parameterised from `SETTINGS_NUMERIC_BOUNDS` rather than from restated numbers. For **every** registered integer on `RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`, `DatabasePoolSettings`, `WorkerSettings` and `SessionSettings`: both accepted boundaries survive with value and exact type intact; `minimum - 1` and `maximum + 1` are refused (and a field whose register entry is a floor with no ceiling, N-22, accepts a large value rather than inventing one); an entry whose register bounds are **equal** is exercised as the one accepted value it is — N-41's concurrency, N-34's proxy hop count and N-23's lease — rather than as two boundaries that happen to coincide; integral and fractional floats, NaN, ±infinity, `True`, `False` and a comparison-overriding `int` subclass are each refused with the field named; and direct construction and `dataclasses.replace()` apply the identical rule. The accepted non-numeric shapes are enforced too — relying-party hostname and lowercase form, non-empty display name, non-empty tuple of exact origins, N-60's exact `required` user verification, an exact `bool` for `WORKER_ENABLED` and an absolute `Path` or `None` for the artifact root — and N-21's one accepted cross-field rule is enforced at the object owning both fields, from one read of each, with equality accepted. Relationships the contracts do **not** state (membership grace versus cache, N-45's attempt timeout against the lease) are proved **not** enforced, deliberately. **N-23's lease is proved to be an exact value of 60 seconds** (corrected 2026-08-15): 60 constructs and is carried unchanged, 59 and 61 are both refused as `S-10` at direct construction, at `dataclasses.replace()` and at the environment boundary with the variable named and the supplied value absent, an unset variable yields the register-derived 60, floats, non-finite floats, `True`, `False` and a comparison-overriding `int` subclass carrying 60 are all refused, a subclass whose later read of the lease lies is refused by canonicalisation, the accepted heartbeat boundaries of 1 and 20 are proved unchanged with 0 and 21 refused, and the previously documented `lease_seconds=1, heartbeat_seconds=20` is proved to **halt at `WorkerSettings` construction because the lease is invalid** — with the refusal proved to name only the lease, so no ordering rule is implied or enforced. Every seam that reads a settings value again — engine composition, limiter construction, application composition, break-glass construction and the startup health view — refuses a genuine subclass whose single later read lies, with the read count asserted as exactly one, and canonicalisation refuses a duck type and returns the base type. `WebSettings.from_environment()` still raises **one** `ConfigurationError` for seven invalid variables spanning four types, naming all seven, echoing none of their sentinel values and never leaking a `ValueError` from a constructor | unit + composition seam | automated |
| TC-VM-01 | Every view model is frozen, slotted, and contains no mutable collection | introspection | automated |
| TC-VM-02 | Every sequence field enforces its documented bound and sets `truncated` rather than exceeding it | unit | automated |
| TC-VM-03 | A `MigrationDeferred` entry cannot carry a value, and every legacy field renders with the package named in `data-migration-manifest.json` | unit + manifest cross-check | automated |
| TC-VM-04 | Reconciliation warnings render as closed-vocabulary codes; no artifact-sourced free text reaches a response | unit | automated |
| TC-VM-05 | `level = None` renders as "not recorded", never `0` | unit | automated |

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
| Legacy identity evidence fully accounted for, never auto-authorizing | P3.2 | TC-MIG-08…13 |
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
