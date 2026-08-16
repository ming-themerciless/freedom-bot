# Phase 3 P3.1 — settings-construction validation remediation

**Date:** 2026-08-15 · **Package:** P3.1 · **Owner:** Claude (implementing
Technical Lead) · **Change record:** C-P3.1-L

**Status: submitted for review. Nothing here is accepted.** P3.G1 remains open
pending fresh independent implementation and distinct security-focused
re-reviews plus maintainer acceptance. **P3.2 and P3.3 have not started** — no
worker behaviour, no P3.2 route, no P3.2 service was written. **RAID I-09 and
I-10 are both still open.** Passing tests are evidence, not acceptance.

---

## 0. Correction — N-23's lease is exactly 60 seconds (2026-08-15)

**Independent review found this submission's reading of N-23 wrong, and the
implementation with it.** `WORKER_BOUNDS` defined
`"lease_seconds": PolicyBound(minimum=1, maximum=60, policy="N-23")`, which
treats 60 as a ceiling and accepts every exact integer from 1 to 60. The accepted
row does not say "at most 60 seconds":

```text
N-23 | Job lease | 60 seconds, heartbeat at most every 20 seconds
```

The sentence gives the lease as a **value** and the heartbeat interval as a
**maximum**, and the distinction is deliberate. SM-05 renews with
`lease_expires_at = now() + 60s`; the logical schema's claim and renewal
statements write the same 60; the operational contract's recovery bound
(`N-23 + N-44`, at most ≈225 s across three claims) is calculated from a
60-second lease. A lease of 1 second was therefore never a permitted tightening
— it contradicted the accepted documents, and ordinary heartbeat scheduling
would have lost a live claim under it.

**What this correction changes:**

- `application/web/config.py` now defines
  `"lease_seconds": PolicyBound(minimum=60, maximum=60, policy="N-23")`, the same
  exact-value shape `concurrency` (N-41) and `trusted_proxy_hops` (N-34) already
  had. `heartbeat_seconds` is unchanged at 1…20.
- **The §9.1 "open question" below is withdrawn.** `lease_seconds=1,
  heartbeat_seconds=20` was never evidence that an ordering rule was missing; it
  was evidence that the lease bound was wrong. With the lease fixed at 60, every
  accepted heartbeat is already far inside it and there is nothing for an
  ordering rule to catch. **No relationship involving N-45 was added**, and none
  may be added without a separately accepted policy decision. The N-23 question
  does **not** block P3.3.
- The claim below that "every worker number is a ceiling with a floor of one" was
  wrong for two of the six and is corrected in §3.1.

**What it does not change.** N-23 itself, the state machine, the logical schema,
the operational contract, worker behaviour, migrations, routes, services,
environment-variable names, defaults outside the single authority, and
deployment topology are all untouched. `.env.example` already shipped
`WORKER_LEASE_SECONDS=60` and is unchanged. P3.2 and P3.3 remain unstarted, and
P3.G1 and RAID I-09/I-10 remain open.

Every statement in the sections below that predates this correction is marked
where it is affected. Evidence for the correction is
`docs/review/phase-3-p3-1-n-23-exact-lease-remediation-submission.md`.

---

## 1. Scope

Two connected deliverables, in one package because the second cannot honestly be
built on the first until the first is correct:

1. **Blocking defect A** — the shared session-policy validator did not require an
   *exact* built-in `int`, so a comparison-overriding `int` subclass reached
   `SessionPolicy` and made N-66 inoperative for the third time.
2. **Blocking defect B (RAID I-10)** — `RateLimitSettings`, `BoundsSettings`,
   `WebAuthnSettings`, `DatabasePoolSettings` and `WorkerSettings` had no
   construction-time validation, so an object outside the accepted register could
   exist and be trusted by the limiter, the middleware, WebAuthn verification,
   engine composition or future worker code.

**Not in scope, and not done:** P3.2, P3.3, any route, any worker behaviour, any
change to an accepted numeric value, environment-variable name, database schema,
migration, deployment topology or authorization policy. None was required and
none was made.

---

## 2. The two root causes, with reproducible counterexamples

### 2.1 Defect A — `isinstance(value, int)` is not "is an integer"

The reviewed rule, in `application/web/config.py`:

```python
if not isinstance(value, int) or isinstance(value, bool):
```

It refuses `bool` and every float. It accepts **every other subclass of `int`**.
A subclass may override `__lt__`, `__gt__`, `__le__` and `__ge__`, and Python
gives the right-hand operand's reflected comparison priority when the right-hand
type is a subclass of the left's. `_enforce_session_limit` compares
`len(live) >= maximum`, so when `maximum` is such a subclass, *it* answers.

**Before — verbatim, against the reviewed implementation:**

```python
class LyingInt(int):
    def __lt__(self, other): return False
    def __gt__(self, other): return False
    def __le__(self, other): return False
    def __ge__(self, other): return False

settings = dataclasses.replace(
    VALID_SESSION_SETTINGS, max_sessions_per_account=LyingInt(10)
)
policy = SessionPolicy.derive(settings)
```

```
type: <class 'LyingInt'>
10 >= max: False
100 >= max: False
```

No `object.__new__`, no mutation of a frozen instance, no private helper, no
forged `SessionPolicy`, no skipped `__post_init__` — the supported public
constructor, and both gates accepted it. `_enforce_session_limit` then revoked
nothing for any live-session population: **N-66 inoperative.**

**After — same script, unchanged:**

```
ValueError: these session settings do not satisfy the accepted policy register:
max_sessions_per_account must be an exact built-in int — never a bool, never a
float whether integral-looking, fractional, infinite or NaN, and never an int
subclass, whose comparison methods can answer anything — not 10 of type LyingInt
```

The refusal happens at `dataclasses.replace()`, one layer earlier than the gate
the finding reached.

### 2.2 Defect B — validation by one producer is not an invariant of a type

`WebSettings.from_environment()` parsed and bounded the configured strings before
constructing the five types. That protects the ordinary environment path and
makes no invariant of the types themselves.

**Before:**

```python
RateLimitSettings(window_minutes=1, oauth_starts_per_ip=10_000, ...)   # accepted
BoundsSettings(max_request_bytes=64 * 1024 * 1024, ...)                # accepted
WebAuthnSettings(rp_id="", user_verification="discouraged", ...)       # accepted
DatabasePoolSettings(pool_size=500, statement_timeout_ms=3_600_000)    # accepted
WorkerSettings(enabled=1, lease_seconds=86_400, ...)                   # accepted
```

**After:** each raises `ValueError` naming the field and the accepted bound or
shape, from `__post_init__`, at direct construction and at
`dataclasses.replace()` alike.

**What is *not* claimed.** No HTTP caller constructs these objects, and no
environment-string exploit was demonstrated or exists. The defect is that a
supported Python construction and composition boundary did not enforce its
contract — the same shape found five times in the session work — and that tests,
operator code and future composition changes can build an invalid graph without
bypassing any frozen-object protection.

---

## 3. Field, authority and consumer inventory

Every row was traced from the environment variable through the settings object to
every runtime consumer. Comments and prior submissions were treated as claims to
verify.

### 3.1 Registered numbers

Every field below carries the same accepted type — an **exact** built-in `int` — so the type column is folded into this sentence rather than repeated thirty times.

#### `RateLimitSettings`

| Field | Accepted range | Authority | Environment variable |
|---|---|---|---|
| `window_minutes` | 1…10 | N-18/N-30 | `WEB_RATE_LIMIT_WINDOW_MINUTES` |
| `oauth_starts_per_ip` | 1…10 | N-18 | `WEB_RATE_LIMIT_OAUTH_STARTS` |
| `oauth_callbacks_per_ip` | 1…20 | N-18 | `WEB_RATE_LIMIT_OAUTH_CALLBACKS` |
| `webauthn_assertions_per_ip` | 1…5 | N-32 | `WEB_RATE_LIMIT_WEBAUTHN_PER_IP` |
| `webauthn_assertions_per_account` | 1…10 | N-32 | `WEB_RATE_LIMIT_WEBAUTHN_PER_ACCOUNT` |
| `webauthn_account_window_minutes` | 1…60 | N-32 | `WEB_RATE_LIMIT_WEBAUTHN_ACCOUNT_WINDOW_MINUTES` |
| `recovery_attempts_per_ip` | 1…3 | N-33 | `WEB_RATE_LIMIT_RECOVERY_PER_IP` |
| `recovery_attempts_per_grant` | 1…5 | N-33 | `WEB_RATE_LIMIT_RECOVERY_PER_GRANT` |
| `cleanup_after_minutes` | 10…60 | N-31 | `WEB_RATE_LIMIT_CLEANUP_MINUTES` |

#### `BoundsSettings`

| Field | Accepted range | Authority | Environment variable |
|---|---|---|---|
| `max_request_bytes` | 1024…1048576 | N-19 | `WEB_MAX_REQUEST_BYTES` |
| `trusted_proxy_hops` | **exactly 1** | N-34 | `WEB_TRUSTED_PROXY_HOPS` |
| `membership_cache_seconds` | 1…300 | N-09 | `WEB_MEMBERSHIP_CACHE_SECONDS` |
| `membership_grace_seconds` | 1…900 | N-10 | `WEB_MEMBERSHIP_GRACE_SECONDS` |
| `audit_page_size_default` | 1…50 | N-21 | `WEB_AUDIT_PAGE_SIZE_DEFAULT` |
| `audit_page_size_max` | 1…100 | N-21 | `WEB_AUDIT_PAGE_SIZE_MAX` |
| `poll_min_seconds` | **≥ 2, no ceiling** | N-22 | `WEB_POLL_MIN_SECONDS` |

#### `WebAuthnSettings`

| Field | Accepted range | Authority | Environment variable |
|---|---|---|---|
| `recovery_grant_minutes` | 1…10 | N-14 | `WEB_RECOVERY_GRANT_MINUTES` |

#### `DatabasePoolSettings`

| Field | Accepted range | Authority | Environment variable |
|---|---|---|---|
| `pool_size` | 1…5 | N-53 | `WEB_DATABASE_POOL_SIZE` |
| `max_overflow` | **0**…5 | N-53 | `WEB_DATABASE_MAX_OVERFLOW` |
| `pool_timeout_seconds` | 1…5 | N-53 | `WEB_DATABASE_TIMEOUT_SECONDS` |
| `statement_timeout_ms` | 100…10000 | N-53 | `WEB_DATABASE_STATEMENT_TIMEOUT_MS` |

#### `WorkerSettings`

| Field | Accepted range | Authority | Environment variable |
|---|---|---|---|
| `concurrency` | **exactly 1** | N-41 | `WORKER_CONCURRENCY` |
| `lease_seconds` | **exactly 60** (corrected 2026-08-15 — see §0; this table read `1…60`) | N-23 | `WORKER_LEASE_SECONDS` |
| `heartbeat_seconds` | 1…20 | N-23 | `WORKER_HEARTBEAT_SECONDS` |
| `max_attempts` | 1…3 | N-43 | `WORKER_MAX_ATTEMPTS` |
| `attempt_timeout_seconds` | 1…300 | N-45 | `WORKER_ATTEMPT_TIMEOUT_SECONDS` |
| `queue_max_depth` | 1…5 | N-42 | `WORKER_QUEUE_MAX_DEPTH` |

Every range above except the corrected lease is the one the environment reader
already applied, and **no accepted value changed**: N-23's lease was, and remains,
60 seconds. What changed on 2026-08-15 is that the runtime entry stopped reading
that 60 as a ceiling (§0).

**Four** entries are recorded explicitly because they are not plain ceilings:
`max_overflow` floors at zero (no overflow at all is a legitimate tightening),
`trusted_proxy_hops` is an exact value (neither zero nor two is a tightening of
N-34), `lease_seconds` is an exact value for the same reason (a shorter lease is
not a tightening of a lease the state machine and schema both write as 60), and
`poll_min_seconds` is a floor with no accepted ceiling — N-22 states none, and
inventing one would be new policy.

The sentence this paragraph replaced said every worker number was a ceiling with
a floor of one. That was true of four of the six and never of `concurrency` or,
correctly read, of `lease_seconds`.

### 3.2 Non-numeric fields and their accepted shapes

| Field | Accepted shape | Authority | Where enforced |
|---|---|---|---|
| `WebAuthnSettings.rp_id` | non-empty lowercase hostname | N-60 | type; **equality with the public origin's host stays at S-09** |
| `WebAuthnSettings.rp_name` | non-empty display string | §2.2 | type |
| `WebAuthnSettings.allowed_origins` | non-empty tuple of exact origins (one token, no spaces) | N-60 | type; **subset-of-public-origin stays at S-09** |
| `WebAuthnSettings.user_verification` | exactly `"required"` | N-60 | type and reader |
| `WorkerSettings.enabled` | exact `bool` | S-11 | type; the "false in the web process" half stays at S-11 |
| `WorkerSettings.artifact_root` | absolute `Path`, or `None` | S-12 | type; the ownership/mode/link checks stay in the Phase 2 store |
| `SessionSettings` cookie names | non-empty; `__Host-` iff secure | N-05/S-03 | type (unchanged) |

The relational rules are deliberately left where both sides are in scope. A type
that does not carry `WEB_PUBLIC_ORIGIN` cannot decide whether an origin is the
right one; a weaker syntactic re-check inside the type would be a second, worse
copy of S-09.

### 3.3 Cross-field relationships

| Relationship | Accepted? | Enforced? |
|---|---|---|
| `audit_page_size_default` ≤ `audit_page_size_max` | **Yes** — N-21 states a default of 50 within a maximum of 100 | Yes, in `BoundsSettings.__post_init__`, from one read of each field |
| worker `heartbeat_seconds` < `lease_seconds` | **Not stated, and not needed** (corrected 2026-08-15) | **No** — and none is required; see §0 and §9.1 |
| worker `attempt_timeout_seconds` vs `lease_seconds` | Not stated | No |
| `membership_grace_seconds` ≥ `membership_cache_seconds` | Not stated | No |

N-23 states a lease **value** of 60 seconds and a heartbeat **maximum** of 20
seconds. No accepted document states an ordering rule between them, and with the
lease corrected to exactly 60 (§0) none is needed: every accepted heartbeat is
already far inside every accepted lease, so an ordering rule would refuse nothing
that is not already refused. The row above previously read "Not stated anywhere"
and pointed at §9.1 as an open question; that question is withdrawn.

No relationship involving N-45's per-attempt cap is enforced, because no accepted
document states one. A rule that "sounds sensible" is still new policy, and the
accepted route for new policy is a controlled decision, not a constructor.

### 3.4 Consumers, and whether they exist in P3.1

| Field(s) | Production consumer | Active in P3.1? |
|---|---|---|
| `RateLimitSettings` — the four per-IP budgets and the window | `RateLimiter.check_ip` via `_budget_for`; reached by `/v1/auth/discord/start`, `/auth/discord/callback`, the two WebAuthn routes and the recovery route | **Yes** |
| `RateLimitSettings.webauthn_assertions_per_account`, `webauthn_account_window_minutes` | `RateLimiter.check_account` | **Yes** |
| `RateLimitSettings.recovery_attempts_per_grant` | `BreakGlassService.redeem_recovery_grant` (N-33's per-grant cap) | **Yes** |
| `RateLimitSettings.cleanup_after_minutes` | `RateLimiter.sweep` (N-31) | **Yes** |
| `BoundsSettings.max_request_bytes` | `BodyBound` middleware, before routing | **Yes** |
| `BoundsSettings.trusted_proxy_hops` | `ClientAddressPolicy`, which every rate-limit bucket and client digest is keyed by | **Yes** |
| `BoundsSettings.membership_cache_seconds`, `membership_grace_seconds` | `MembershipProjection.is_fresh` / `within_grace` exist and apply them; **no P3.1 route calls either** | **No** — P3.2 |
| `BoundsSettings.audit_page_size_default`, `audit_page_size_max` | none | **No** — P3.2 |
| `BoundsSettings.poll_min_seconds` | none | **No** — P3.3 |
| `WebAuthnSettings.rp_id`, `allowed_origins` | `BreakGlassService.begin_assertion` and `complete_assertion` | **Yes** |
| `WebAuthnSettings.user_verification` | **none** — the assertion path passes the constant `UserVerificationRequirement.REQUIRED` and `require_user_verification=True` | **No** (see §9.2) |
| `WebAuthnSettings.rp_name` | none | **No** |
| `WebAuthnSettings.recovery_grant_minutes` | **none** — `tools/emergency_recovery.py` uses its own `GRANT_MINUTES = 10` | **No** (see §9.2) |
| `DatabasePoolSettings` — all four | `build_engine` → `create_engine` and the `statement_timeout` connect argument | **Yes** |
| `WorkerSettings.enabled` | S-11 startup refusal | **Yes** |
| `WorkerSettings.artifact_root` | S-12 startup check and `/healthz` | **Yes** |
| `WorkerSettings` — lease, heartbeat, max attempts, attempt timeout, queue depth | none | **No** — **P3.3 obligation** |

---

## 4. The construction model

### 4.1 One runtime definition per number

`application/web/config.py` now holds:

- **`PolicyBound`** — `minimum`, `maximum` (`None` for a floor with no accepted
  ceiling) and the `N-nn` policy id. `default` is *derived* (`maximum`, or
  `minimum` for a floor), because a separately written default is a second number
  that can drift from the bound it should equal. `is_exact` is `minimum ==
  maximum`.
- **`policy_number_problem(field, value, bound)`** — the single definition of
  accepted type and range. Type first: `type(value) is not int` is reported as a
  type problem rather than compared against a bound it cannot meaningfully be
  compared with — a comparison the value itself may be answering.
- **`settings_numeric_problems(values, bounds)`** — collects rather than
  short-circuits, so a caller learns about every problem at once. An unregistered
  key raises `KeyError` rather than passing unchecked.
- **`_registered_numbers(instance, bounds)`** — reads every registered field
  exactly once, into locals.
- **`canonical_settings(value, expected)`** — the consumer-side half; see §4.3.

Six register tables cite it, and each is read by exactly two places: the
environment reader and the `__post_init__` of the type carrying the field.

| Table | Numbers |
|---|---|
| `SESSION_CEILINGS` → `SESSION_BOUNDS` (derived, not restated) | N-04, N-06, N-07, N-15, N-66 |
| `RATE_LIMIT_BOUNDS` | N-18, N-30, N-31, N-32, N-33 |
| `REQUEST_BOUNDS` | N-09, N-10, N-19, N-21, N-22, N-34 |
| `WEBAUTHN_BOUNDS` | N-14 |
| `DATABASE_POOL_BOUNDS` | N-53 |
| `WORKER_BOUNDS` | N-23, N-41, N-42, N-43, N-45 |

`SETTINGS_NUMERIC_BOUNDS` maps each type to its table, published so the tests
parameterise from the register instead of restating it.

### 4.2 Every enforcement point

| Boundary | What runs there |
|---|---|
| `_Reader.registered_integer(variable, field, table)` | The **decision** is `policy_number_problem`; only the operator-facing wording is produced locally, from `PolicyBound.requirement()`, which is never given a value and therefore cannot echo one. `PolicyBound.refusal_for()` tags `S-10` when the number would *loosen* an accepted policy (above a ceiling, either side of an exact value, below a floor) and leaves a merely malformed value untagged, so `S-10` keeps one meaning. |
| `SessionSettings.__post_init__` | `session_policy_problems` → `settings_numeric_problems(values, SESSION_BOUNDS)` → `policy_number_problem`, plus the N-05 cookie pair from one read of `cookie_secure`. |
| `SessionPolicy.__post_init__` and `SessionPolicy.derive()` | `_validate_policy_values` → `validate_session_policy_values` → the same function. Unchanged in structure; it inherits the corrected type rule. |
| `RateLimitSettings.__post_init__` | `RATE_LIMIT_BOUNDS`. |
| `BoundsSettings.__post_init__` | `REQUEST_BOUNDS`, plus N-21's relationship from the same single read of each field. |
| `WebAuthnSettings.__post_init__` | `WEBAUTHN_BOUNDS`, plus the four accepted shapes. |
| `DatabasePoolSettings.__post_init__` | `DATABASE_POOL_BOUNDS`. |
| `WorkerSettings.__post_init__` | `WORKER_BOUNDS`, plus the exact `bool` and the `Path \| None`. |
| `build_engine`, `RateLimiter.__init__`, `create_app`, `BreakGlassService.__init__`, `_check_artifact_root` / `build_health_view` | `canonical_settings` — one read per field, validated, base type returned. |

**No independently injectable policy object was created and no second bounds
source exists.** The tables are module-level constants referenced by name inside
each `__post_init__`, never looked up through `self` or `type(self)` — a subclass
that redefined a class attribute would otherwise be able to supply its own,
looser register, which is exactly the overridable-authority shape OD-44's F2
found.

### 4.3 Reading a subclass is not reading what its constructor saw

The five types are subclassable, and a subclass's property or `__getattribute__`
may answer differently on a second read. A consumer that reads a value once at
construction and again per request therefore has no guarantee that what it
validated is what it uses.

`canonical_settings(value, expected)` reads each declared field of `expected`
exactly once and rebuilds the **base** type from those locals, whose
`__post_init__` validates them. What comes back is an ordinary frozen instance
with no overridden reads left in it. It is applied at the five seams above. Two
of them changed behaviour materially:

- `RateLimiter` previously kept whatever it was handed and re-read a budget on
  **every check**; it now reads the nine numbers once, at construction.
- `BreakGlassService` previously re-read the relying party and the per-grant cap
  from the settings tree on **every assertion and every redemption**; it now
  reads them once, at construction.

### 4.4 Aggregation is preserved by reader fallbacks

Rule 7 of the handover and principle 2 of the configuration contract require that
`WebSettings.from_environment()` report *every* problem. A settings constructor
raising mid-collection would cost the operator the rest of the list, so every
accessor records the problem and then returns an **accepted** value:

- `registered_integer` returns `bound.default`;
- `_read_bounds` tightens `audit_page_size_default` to the configured maximum
  after recording the N-21 relationship problem;
- `_read_webauthn` substitutes `unset.invalid` for a malformed relying party,
  `("https://unset.invalid",)` for malformed origins, and `"required"` for a
  refused user verification — after the S-09/S-10 checks have run, so no spurious
  problem is added.

`.invalid` is the reserved TLD (RFC 2606). **No fallback is ever a value the
process runs under**: a run that recorded a problem raises `ConfigurationError`
and returns no settings at all.

---

## 5. Why `type(value) is int`, and why `isinstance` is insufficient

`isinstance(value, int)` answers "does this participate in the `int` hierarchy",
which is not the question the enforcement asks. The enforcement asks whether a
comparison against this value means what it says.

1. **`bool` is an `int`.** `True` is a maximum of one and `False` a maximum of
   zero. The reviewed rule already excluded it — by name, one subclass at a time.
2. **Every other `int` subclass is also an `int`,** and a subclass may override
   `__lt__`, `__gt__`, `__le__` and `__ge__`. When the right-hand operand's type
   is a subclass of the left's, Python tries the **right** operand's reflected
   method first. `len(live) >= maximum` therefore asks the subclass. A subclass
   answering `False` to everything makes the limit inoperative while remaining,
   to `isinstance` and to an `int` annotation, an integer.
3. **Excluding subclasses by name does not close it.** Excluding `bool` closed
   one member of the class of values; the finding constructed another in four
   lines. Naming members is the same error as patching `float("nan")` while
   `10.0`, `2.5` and `inf` still passed.
4. **An annotation is not enforcement.** `max_sessions_per_account: int` was
   already written and already true of `LyingInt(10)`.
5. **A coercion is not a refusal.** `int(value)` would accept the input and then
   change it, turning a policy violation into a silent reinterpretation.
6. **Checking one comparison result asks the value to grade itself.** A subclass
   overriding the comparison the check uses answers the check too.

`type(value) is int` is the only formulation that names the property the
comparison depends on: this is the built-in integer, whose comparisons are the
built-in comparisons. It is stated as a type for the same reason the float rule
was — it covers the class rather than the member a review happened to construct.

---

## 6. Files changed, and why

| File | Change |
|---|---|
| `application/web/config.py` | `PolicyBound`, `policy_number_problem`, `settings_numeric_problems`, `_registered_numbers`, `_refuse`, `canonical_settings`; `SESSION_BOUNDS` derived from `SESSION_CEILINGS`; `session_policy_problem` reduced to a call of the shared definition (this is defect A's correction); five register tables and `SETTINGS_NUMERIC_BOUNDS`; `__post_init__` on the five types; `_Reader.registered_integer`, with `_Reader.integer` narrowed to the two variables that carry no policy bound; readers rewritten to take every bound and default from the tables; `_is_origin_shaped`; the two `.invalid` fallbacks |
| `application/web/sessions.py` | **Unchanged.** Both policy gates already went through the shared definition, so defect A's correction reached them without an edit — which is the property the previous remediation was for |
| `application/web/rate_limit.py` | `RateLimiter.__init__` canonicalises its settings: nine numbers read once and validated, instead of re-read per check |
| `application/web/breakglass.py` | `BreakGlassService.__init__` canonicalises `settings.webauthn` and `settings.rate_limits`; the assertion, verification and grant paths read the held values |
| `application/web/startup.py` | `_check_artifact_root` and `build_health_view` canonicalise `settings.worker`; `_artifact_root_ok` takes the path its caller already read instead of reading it again |
| `adapters/web/composition.py` | `build_engine` canonicalises the pool before the four engine arguments are derived from it |
| `adapters/web/app.py` | `create_app` canonicalises the request bounds once, before `BodyBound` and `ClientAddressPolicy` are given them |
| `tests/web/test_session_exact_integer_policy.py` | **New.** 22 cases, TC-AUTH-19(m) |
| `tests/web/test_settings_construction_validation.py` | **New.** 145 cases at the time of this submission, TC-STRUCT-07 and TC-LIM-06. The N-23 correction (§0) later took it to 165 |
| `docs/contracts/phase-3-numeric-policy-register.md` | Appended: the exact built-in type, and the one-`PolicyBound`-per-number enforcement map. No value changed |
| `docs/contracts/phase-3-configuration-and-dependency-contract.md` | Appended: where §2.2's bounds now hold. No variable added, renamed or removed |
| `docs/contracts/phase-3-test-traceability.md` | Appended: TC-AUTH-19(m), TC-STRUCT-07, TC-LIM-06. Addition only; no row rewritten or removed |
| `docs/project-management/raid-register.md` | I-09 amended a sixth time; I-10 amended and **left open** |
| `docs/project-management/status.md` | Sixth 2026-08-15 update, appended |
| `docs/project-management/change-log.md` | C-P3.1-L appended |
| `docs/review/phase-3-settings-construction-validation-gap.md` | A pointer to this submission, above the preserved finding text. Nothing closed |

No migration, no schema, no `.env.example`, no `requirements*`, no systemd unit,
no operations document changed. **No operator contract changed**, which is what
§9.2's honest gaps are about rather than a reason to edit one.

---

## 7. Tests, mapped to every requirement in the handover

### 7.1 Defect A — `tests/web/test_session_exact_integer_policy.py` (22 cases)

| Handover requirement | Case |
|---|---|
| `SessionSettings` construction and `replace()` refuse the subclass **for every registered field** | `test_settings_construction_refuses_a_comparison_overriding_int_subclass` ×6, parameterised from `SESSION_CEILINGS`, each using that field's own accepted number so only the type is at issue; the subclass is first shown to satisfy the old predicate and to answer `False` to every comparison |
| The shared definition refuses it for every field, and still accepts the plain integer | `test_the_shared_definition_itself_refuses_the_subclass_for_every_field` |
| `SessionPolicy` construction and `replace()` refuse it for every field the policy carries | `test_a_directly_constructed_policy_refuses_a_lying_maximum`; `test_a_policy_duration_cannot_be_a_lying_int_at_all` ×4 (a non-`timedelta` is refused before any comparison); `test_a_lying_duration_is_reduced_to_an_exact_int_before_the_register_sees_it` (the duration-shaped route, proved through the public boundary) |
| `derive()` refuses a genuine subclass whose inherited construction saw a valid integer and whose one later read lies; **exactly one derivation read** | `test_derivation_refuses_a_settings_subclass_that_answers_a_lying_int_later`; `test_derivation_refuses_the_lying_int_on_every_field_the_policy_carries` ×5. Both assert the read delta is exactly 1 |
| The real session service against disposable PostgreSQL cannot exceed N-66 | `test_the_repository_cannot_be_built_from_settings_that_lie` (the reproduction halts at the supported repository constructor, before any statement is compiled); `test_the_live_session_bound_still_holds_against_real_postgresql` (eleven logins → ten live, oldest durably revoked as `session_limit`, one audit event with `limit = 10`, read from a fresh connection after commit) |
| A falsification/control showing the old predicate admits the value and makes `len(live) >= maximum` false | `test_the_old_predicate_would_have_admitted_the_value_and_disabled_the_limit` |
| All existing NaN, infinity, float, bool, bound, aggregation, lifetime, rotation, touch, classification and audit cases remain green | The whole pre-existing suite: 587 portal tests, 0 failed, 0 skipped |

### 7.2 Defect B — `tests/web/test_settings_construction_validation.py` (145 cases at submission; 165 after the §0 correction)

| Handover requirement | Case |
|---|---|
| Accepted lower and upper/exact boundaries survive unchanged | `test_both_accepted_boundaries_are_carried_exactly`, parameterised over **every** registered field of all six types, asserting value *and* exact type, at direct construction and `replace()` |
| Below-floor and above-ceiling / non-exact refused | `test_a_number_outside_the_register_is_refused`, `minimum - 1` and `maximum + 1`, both routes |
| Integral and fractional floats, NaN, ±infinity, `True`, `False`, comparison-overriding `int` subclass refused | `test_only_an_exact_built_in_int_is_accepted`, eight values × every field × both routes, each carrying an in-range number so range is never what refuses it |
| Errors identify the field | asserted in the case above; the environment boundary is §7.2's aggregation cases |
| Accepted non-integer shapes | `test_webauthn_shapes_are_enforced_at_construction` (11 cases), `test_worker_shapes_are_enforced_at_construction` (5), `test_the_worker_artifact_root_may_be_absent_or_absolute` |
| Cross-field relationships | `test_the_audit_default_page_size_cannot_exceed_its_maximum` (including equality accepted, and via `replace()`); `test_no_relationship_is_invented_between_the_worker_or_membership_bounds` proves the unstated ones are **not** enforced. **Corrected 2026-08-15 (§0):** that case previously used `lease_seconds=1, heartbeat_seconds=20` as its worker example. That pair is now refused for its lease, by `test_the_previously_documented_counterexample_no_longer_constructs`, and the worker example of an unenforced relationship is N-45's attempt timeout against the lease. No ordering rule was added |
| An invalid later subclass read wherever a value is read again, with the read count asserted | `test_the_engine_is_never_built_from_a_pool_that_lies`, `..._limiter_...`, `..._application_...`, `..._break_glass_...`, `..._startup_checks_...`; `test_canonicalisation_refuses_a_duck_type_and_returns_the_base_type` ×5 |
| Multi-error environment test spanning several types: one `ConfigurationError`, all names, no sentinels, no premature `ValueError` | `test_invalid_variables_across_several_types_raise_one_redacted_error` (7 variables across 4 types); `test_a_malformed_relying_party_and_origin_still_aggregate`; `test_a_valid_environment_is_still_accepted_and_carries_the_register` as the control |
| A stricter accepted value is preserved | `test_a_stricter_accepted_value_is_preserved_and_not_replaced_by_a_default`; and at the consumer, `test_a_stricter_configured_budget_is_the_one_the_limiter_enforces` |
| `RateLimitSettings` consumer evidence — IP, account, recovery-grant paths | `test_the_limiter_spends_exactly_the_configured_ip_budget` (all four actions), `..._account_budget`, `..._stricter_configured_budget...`, `test_the_recovery_grant_attempt_cap_the_service_reads_is_the_validated_one` |
| `BoundsSettings` consumer evidence, without claiming an absent consumer | `test_the_body_bound_middleware_applies_the_configured_limit` (413 before routing at a stricter bound, and not refused just under it), `test_the_client_address_policy_holds_the_exact_accepted_hop_count`, `test_the_membership_bounds_are_validated_but_have_no_p3_1_route_consumer`, `test_the_audit_page_and_polling_bounds_have_no_p3_1_consumer_at_all` |
| `WebAuthnSettings` consumer evidence | `test_the_challenge_carries_the_configured_relying_party` (rpId and `required` on the payload the browser receives), `test_the_verification_origins_are_the_configured_ones`, `test_the_break_glass_service_is_never_built_from_a_relying_party_that_lies` |
| `DatabasePoolSettings` — a stable seam, exact arguments, never reaching SQLAlchemy when invalid | `test_the_engine_is_never_built_from_a_pool_that_lies`. **No database is connected**: `create_engine` is replaced with a spy |
| `WorkerSettings` — construction now, only implemented consumers, later ones named as P3.3 | `test_the_worker_bounds_are_valid_now_and_their_consumers_are_a_p3_3_obligation`, `test_a_web_process_that_claims_jobs_still_refuses_to_start` |
| **N-23's lease is exactly 60** (added 2026-08-15, §0) | Module section 3.1: `test_the_accepted_n_23_lease_value_is_sixty_seconds`, `test_the_lease_is_registered_as_an_exact_value_and_behaves_as_one`, `test_a_lease_that_is_not_the_accepted_value_is_refused` ×6, `test_only_an_exact_built_in_int_is_an_acceptable_lease`, `test_replacing_the_lease_on_a_valid_worker_refuses_at_construction` ×3, `test_the_previously_documented_counterexample_no_longer_constructs`, `test_the_accepted_heartbeat_boundaries_are_unchanged`, `test_a_worker_whose_lease_lies_on_a_later_read_is_refused_by_canonicalisation`, `test_the_environment_accepts_an_unset_lease_as_the_registered_value`, `test_the_environment_accepts_the_accepted_lease_written_out`, `test_the_environment_refuses_a_lease_either_side_of_the_accepted_sixty` ×2, `test_an_invalid_lease_still_aggregates_with_other_types` |

---

## 8. Falsification

Run rather than asserted, and **without editing any reviewed file on disk**. Both
plugins live outside the worktree (in the session scratchpad) and are loaded with
`-p`; each restores the previous model in memory only.

### 8.1 Plugin A — the reviewed `isinstance` predicate restored

```
PYTHONPATH=<scratchpad> TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv-web/bin/python -m pytest tests/web/test_session_exact_integer_policy.py \
  tests/web/test_session_policy_numeric_validation.py -q -p falsify_session_isinstance
→ 16 failed, 34 passed
```

- **16 of the 22 new cases discriminate.** Every construction, `replace()`,
  policy-construction, derivation, repository and control case fails against the
  old predicate.
- **6 are non-regression only** and are named rather than counted: the four
  `test_a_policy_duration_cannot_be_a_lying_int_at_all` parameters and
  `test_a_lying_duration_is_reduced_to_an_exact_int_before_the_register_sees_it`
  (they exercise the `timedelta` gate, which the defect never went through) and
  `test_the_live_session_bound_still_holds_against_real_postgresql` (it runs on
  ordinary configuration, so it holds under either predicate — it is the control
  proving N-66 works, not a discriminator).
- **All 28 cases of the pre-existing `test_session_policy_numeric_validation.py`
  stay green.** That module contained no counterexample for this defect.

### 8.2 Plugin B — the previous reader-only model restored

`__post_init__` removed in memory from the five I-10 types.

```
PYTHONPATH=<scratchpad> TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv-web/bin/python -m pytest tests/web -q -p falsify_no_post_init
→ 81 failed, 506 passed
```

- **81 of the 145 new cases discriminate** — every construction, `replace()`,
  shape, cross-field, subclass-seam and canonicalisation case.
- **64 are non-regression only**: the accepted-boundary cases (a valid value is
  accepted with or without validation), the `SessionSettings` parameters (that
  type kept its `__post_init__`), the consumer-behaviour cases that run on valid
  configuration, and the environment cases that the reader already refused.
- **All 442 pre-existing portal tests stay green** (506 − 64). The pre-existing
  suite contained no counterexample for I-10 either.

### 8.3 State restored

`git status --short` was captured before and after both runs and is byte-identical
(64 entries). No tracked file changed, and no plugin, cache or monkeypatch was
left in the repository. This is **not** mutation testing and is not described as
such: **no mutation tool is configured in this repository and none was run.**

---

## 9. Honest gaps, open questions and unavailable evidence

### 9.1 ~~Open question for the maintainer — worker bound relationships~~ — **withdrawn 2026-08-15**

**This question was raised on a false premise and is withdrawn.** It is left in
place, struck, rather than deleted, because the reviewers who read it need to
know it was answered and how.

It read: N-23 states a 60-second lease and a heartbeat of at most 20 seconds, and
N-45 a 300-second per-attempt cap; no accepted document states an ordering rule
between them; `lease_seconds=1, heartbeat_seconds=20` is inside the register as
written and is operationally nonsensical; and a decision was therefore requested
on whether `heartbeat_seconds < lease_seconds` should be added to the accepted
contract, as a **P3.3 prerequisite**.

**What was actually wrong.** `lease_seconds=1` was never inside the register. It
was inside the *implementation*, which had read N-23's lease value as a ceiling
(§0). The register states one lease: 60 seconds. With the runtime entry corrected
to exactly 60, the nonsensical configuration no longer constructs, and it halts
at `WorkerSettings` because the **lease** is invalid — not because of any
ordering rule, of which none was added.

**Consequences, stated plainly:**

- **No maintainer decision is requested on the lease/heartbeat ordering.** There
  is nothing left for such a rule to refuse.
- **No relationship involving N-45 has been accepted, and none was added.** That
  remains outside any accepted contract; adding one would require a separately
  accepted policy decision.
- **Nothing here blocks P3.3.** The earlier "P3.3 prerequisite" framing lapses
  with the premise. What P3.3 still owns is the *consumer* evidence for the
  lease, heartbeat, attempt, timeout and queue bounds (§9.3), which is a
  different obligation and is unchanged.

### 9.2 Validated fields with no runtime consumer

Reported because "it is bounded" and "it is used" are different claims:

- **`WEB_WEBAUTHN_USER_VERIFICATION`.** The assertion path passes the constant
  `UserVerificationRequirement.REQUIRED` and `require_user_verification=True`
  rather than the configured value. Behaviour therefore matches N-60 and cannot
  be loosened by configuration — which is stricter than reading the setting —
  but the setting has no consumer. It was left as it is: wiring the constant to
  configuration would make an accepted security value configurable, which is a
  loosening dressed as tidiness. Flagged for the security review to confirm.
- **`WEB_RECOVERY_GRANT_MINUTES`.** `tools/emergency_recovery.py` issues grants
  from its own `GRANT_MINUTES = 10`. Both are N-14's ten, so there is no policy
  conflict, and correcting the divergence would change an operator contract this
  remediation was not scoped to touch. Recorded for the next package that touches
  the recovery path.
- **`WebAuthnSettings.rp_name`** has no consumer at all.

### 9.3 Consumers that belong to later packages

`membership_cache_seconds` and `membership_grace_seconds` have a helper that
applies them and **no P3.1 route that calls it** (P3.2). `audit_page_size_*` and
`poll_min_seconds` have no consumer at all (P3.2/P3.3). The worker's lease,
heartbeat, attempt, timeout and queue bounds have no consumer (**P3.3
obligation**, named in TC-LIM-06). None of these was manufactured to produce
evidence.

### 9.4 Checks not run

- **No browser, staging, device or live-service check was run.** None is possible:
  staging does not exist (RAID I-06), and this change has no rendered surface.
- **No live Discord, Foundry, production database or external service was
  contacted.** All database evidence is the guarded disposable `freedom_test`.
- **No mutation testing.** No mutation tool is configured; §8 is falsification of
  the previous *implementation*, not mutation coverage.
- **No formatter, linter or type checker was run, because none is configured.**
  Verified rather than assumed: no `pyproject.toml`, `setup.cfg`, `.ruff.toml`,
  `.flake8`, `mypy.ini`, `tox.ini` or pre-commit configuration exists in the
  repository, and neither virtualenv has `ruff`, `mypy`, `flake8` or `black`
  installed. Compilation under both configured interpreters was run instead.

### 9.5 Residual limits of the correction itself

- The **relational** configuration rules (S-02, S-05, S-09) necessarily remain at
  the environment boundary, because no sub-dataclass carries both sides. A
  directly constructed `WebAuthnSettings` can therefore hold a well-shaped
  relying party that is the *wrong* one; §7.2's break-glass case states this
  explicitly rather than implying otherwise.
- `WebSettings` itself and `DiscordProviderSettings` were **not** given
  construction-time validation. They are outside the five types I-10 names and
  outside this handover's scope; `DiscordProviderSettings` in particular carries
  the scope tuple and redirect URI, whose rules are relational. Recorded as a
  candidate for the reviewers to consider, not as work silently done or silently
  skipped.
- `canonical_settings` defends a consumer against a lying subclass; it cannot
  defend against a lying `WebSettings` that returns a different sub-object each
  time it is asked. The composition root reads each sub-object once at the seams
  listed in §4.2, which bounds that to the same one-read discipline.

---

## 10. Verification — fresh results, in the required order

All runs are from after the final edit. Nothing is recycled.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_exact_integer_policy.py -q --deselect …::test_the_repository_cannot_be_built_from_settings_that_lie --deselect …::test_the_live_session_bound_still_holds_against_real_postgresql` | **20 passed, 2 deselected** |
| 2 | `… -m pytest tests/web/test_settings_construction_validation.py -q -k "boundaries or refused or exact_built_in or shapes or audit_default or relationship or absent_or_absolute or aggregate or redacted or valid_environment or canonicalisation or lies"` | **130 passed, 15 deselected** |
| 3 | `… -m pytest tests/web/test_settings_construction_validation.py -q -k "limiter or body_bound or client_address or membership or audit_page or challenge or verification_origins or recovery_grant_lifetime or worker_bounds or claims_jobs or engine"` | **27 passed, 118 deselected** |
| 4 | `… -m pytest …::test_the_live_session_bound_still_holds_against_real_postgresql …::test_the_repository_cannot_be_built_from_settings_that_lie tests/web/test_session_policy_numeric_validation.py tests/web/test_rate_limits_and_outage.py -q` | **42 passed** |
| 5 | `… -m pytest tests/web/test_session_touch_lifetime.py tests/web/test_session_rotation_lifetime.py tests/web/test_session_rotation_integrity.py tests/web/test_sessions.py tests/web/test_structural_guards.py tests/web/test_settings_construction_validation.py tests/web/test_session_exact_integer_policy.py -q` | **301 passed, 1 warning** |
| 6 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest tests/web -q` | **587 passed, 0 failed, 0 skipped**, 14 warnings, 24.02 s |
| 7 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest -q` | **2260 passed, 0 failed, 0 skipped**, 1 warning, 129.86 s |
| 8 | `./venv/bin/python -m compileall -q application adapters tools tests` and the same under `./venv-web/bin/python` | Both **OK**; both interpreters are CPython 3.12.3 |
| 9 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | **`No new upgrade operations detected.`** One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| 10 | Formatter / linter / type checker | **None configured** — established by inspection (§9.4), not assumed |
| 11 | `git diff --check` | **Clean**, exit 0 |
| 12 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 `OK`, 0 non-`OK`** |

**Database target.** Every database run used
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`, the guarded disposable
target confirmed under RAID A-02: it resolves through `assert_disposable_target`,
`current_database()` is `freedom_test`, and both `inet_server_addr()` and
`inet_client_addr()` are null. No other database was contacted.

**Warnings.** The 14 portal warnings are the pre-existing `httpx` per-request
cookie `DeprecationWarning`s; the bot suite's single warning is the pre-existing
`audioop` deprecation from `discord.player`. Neither is new and neither is
related to this change.

---

## 11. Security, availability, configuration, deployment and rollback impact

- **Security.** Strictly a tightening. N-66's live-session bound is enforceable
  again against the reported bypass; the authentication and recovery throttles
  (N-18, N-32, N-33), the request body bound (N-19), the client-address
  determination (N-34) and the WebAuthn relying party (N-60) can no longer be
  weakened by constructing a settings object or by a subclass that answers
  differently on a later read. No control was relaxed and no authority widened.
  No permanent password, no widened Council capability, no change to the
  break-glass boundary.
- **Availability.** The pool topology (N-53) is bounded by construction, so an
  invalid pool cannot reach SQLAlchemy. The refusals are startup-time, not
  request-time: a misconfigured process refuses to start rather than degrading
  under load. Two additional startup refusals are possible where none was before
  (a malformed relying-party identifier and a non-`required` user verification),
  both of which were already S-09/S-10 refusals through their variables; no
  previously accepted environment becomes invalid.
- **Configuration.** No variable added, renamed or removed; no accepted value
  changed; `.env.example` untouched. A stricter configured value is proved to
  survive unchanged. Two refusal-*message* changes are worth naming because a
  reviewer will see them in a diff and neither weakens anything: (a) a variable
  whose value is outside its `PolicyBound` now produces **one** problem stating
  the accepted range rather than, in the `poll_min_seconds` case, two — the
  variable is still named and still tagged `S-10`; and (b) `WEB_BIND_PORT` above
  65535 is refused untagged rather than as `S-10`, because it carries no `N-nn`
  bound and `S-10` means "configuration may not loosen an accepted policy". Both
  still refuse startup.
- **Deployment.** No systemd unit, topology, port, path or credential change. No
  operator procedure changed, so no operations document was edited.
- **Schema and migration.** None. Migrations 0006–0009 were not touched, because
  both defects and both corrections are entirely in runtime validation.
- **Rollback.** Reverting the changed modules restores the previous behaviour
  exactly; nothing persisted changed shape or meaning, and no data written under
  this change differs from data written before it.

---

## 12. Dirty-worktree accounting

`git status --short` reported **64 entries before this remediation and 65 after**,
the single addition being this submission document. This is the extensive
intentional dirty worktree the handover describes; nothing was staged, committed,
pushed, stashed, reverted or rewritten, and all changes are left **unstaged and
uncommitted**.

- **Tracked files this remediation modified (3):**
  `docs/project-management/raid-register.md`,
  `docs/project-management/status.md` and
  `docs/project-management/change-log.md`. All three were **already** modified in
  the worktree before this work began, and all three are appended to rather than
  rewritten, so each keeps its existing ` M` entry instead of adding one.
- **Tracked files this remediation did *not* touch** include
  `docs/review/Handover information` (the maintainer's own modification),
  `docs/review/phase-3-delivery-plan.md`, `.env.example`, `pytest.ini`, the
  Phase 2 adapters and repositories, and every migration.
- **Untracked directories this remediation changed files inside:**
  `application/web/`, `adapters/web/`, `docs/contracts/` and `tests/web/`. Git
  reports each of these as a **single** `??` entry, so files added or edited
  inside them do not change the entry count. The two new test modules are
  `tests/web/test_session_exact_integer_policy.py` and
  `tests/web/test_settings_construction_validation.py`; every other file touched
  inside them is listed in §6.
- **Untracked files at the top level of `docs/review/`:** this document is new —
  the one new entry — and
  `phase-3-settings-construction-validation-gap.md` was already untracked and is
  appended to above its preserved finding text.
- **Everything else in the 64 pre-existing entries pre-dates this remediation** —
  the Phase 3 P3.0/P3.1 work, migrations 0006–0009, the operator tools, the
  earlier submissions and the modified Phase 2 files. None of it was touched.
- The falsification runs changed **nothing**: §8.3 records an identical
  `git status --short` before and after them, and both plugins live outside the
  worktree.
- No secret was read, printed, committed or modified. `.env`, `yt-cookies.txt`
  and every credential file were left alone.

---

## 13. Reviewer focus

### 13.1 Independent implementation review

1. **Try to reach an enforcement comparison with a value that is not an exact
   built-in `int`,** by any route: the session limit, a rate-limit budget, the
   body bound, the pool size. Include a subclass that lies only on a later read,
   and a subclass that redefines a class attribute — the register tables are
   referenced by module name inside each `__post_init__` specifically so that
   cannot redirect them; confirm that.
2. **Check that no bound is written twice.** Each number should appear in exactly
   one `PolicyBound`. Grep for the numbers themselves in `application/web/` and
   `adapters/web/`.
3. **Check the reader's fallbacks.** Every refusal must be followed by an
   accepted value, or aggregation breaks. Try several simultaneously invalid
   variables of each kind — numeric, relying party, origins, user verification,
   the N-21 pair — and confirm one `ConfigurationError` naming all of them.
4. **Check the read-once seams.** `build_engine`, `RateLimiter.__init__`,
   `create_app`, `BreakGlassService.__init__`, `build_health_view`. Is there a
   consumer that still re-reads a settings attribute after validation?

### 13.2 Distinct security-focused review

1. **N-66, again.** Three bypasses have now been found in this control. Assume a
   fourth shape exists.
2. **The throttles.** Can a `RateLimitSettings` reach `RateLimiter` without
   passing `canonical_settings`? Can a budget be made to answer differently
   between the check and the decision?
3. **The relying party.** §9.5 states the limit honestly: the type enforces shape,
   not identity. Is the S-09 relational check reachable in every path that builds
   a `WebAuthnSettings`, or only through `from_environment`?
4. **`WEB_WEBAUTHN_USER_VERIFICATION`** (§9.2) — confirm that hard-coding N-60's
   `required` while validating the setting is the right resolution, rather than
   wiring the setting through.
5. **Redaction.** The constructors name a field *and its value*; the environment
   boundary must not. Confirm no path renders a constructor message into a
   `ConfigurationError` or a log.

### 13.3 Operations / availability review

1. **The pool and statement timeout** (N-53) — are the bounds right, and is a
   startup refusal the correct failure mode for each?
2. ~~**The worker relationship question in §9.1** — a decision is requested before
   P3.3 starts.~~ **Withdrawn 2026-08-15 (§0): no decision is requested.** N-23's
   lease is exactly 60, the nonsensical configuration that prompted the question
   no longer constructs, and no ordering rule was added. What is worth an
   availability reviewer's attention instead is the *corrected* entry itself:
   confirm that an exact 60-second lease is the right runtime bound against
   SM-05's `now() + 60s`, the schema's claim and renewal statements, and the
   `N-23 + N-44` recovery calculation, and that refusing a 59- or 61-second
   `WORKER_LEASE_SECONDS` at startup is the correct failure mode.
3. **The two `.invalid` placeholders** — confirm that a process can never run on
   one (it cannot: a recorded problem raises), and that they never reach a log.

---

## 14. Conclusion

**P3.G1 remains open** pending fresh independent implementation and distinct
security-focused re-reviews plus maintainer acceptance. **P3.2 and P3.3 have not
started.** **RAID I-09 and I-10 are both still open**, and neither should be
closed until both re-reviews find no blocker and Peter records acceptance.
**Passing tests do not constitute acceptance.**
