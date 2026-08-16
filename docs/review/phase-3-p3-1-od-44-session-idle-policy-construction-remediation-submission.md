# P3.1 — OD-44 session idle-policy construction remediation submission

**Date:** 2026-08-15 · **Package:** Phase 3 P3.1 · **Owner:** Claude (working
Technical Lead) · **Status:** *Submitted for a new Codex independent
implementation re-review and a separately reported security-focused re-review.*
**Not accepted. P3.G1 remains open. P3.2 has not started.**

This submission does not overwrite any predecessor. It follows
`phase-3-p3-1-od-44-session-touch-policy-remediation-submission.md` and leaves
every earlier dated submission and review record unedited.

---

## 1. The bypass, restated precisely, and its security consequence

Codex's independent re-review of 2026-08-15 returned **one blocking finding**
against the session-touch policy remediation submitted earlier the same day. The
finding is correct, and it is the same authority in a third position rather than
a new defect.

### What the previous remediation did

It removed `idle` and `expected_auth_method` from `SessionRepository.touch()`,
leaving the supported signature `touch(session_id, *, now)`, and moved the
method-to-window mapping into a new `SessionIdlePolicy` injected at construction.
The conditional `UPDATE` selects the duration with `CASE auth_method` over bind
parameters generated from that policy. That much is sound and is unchanged here.

### What it did not do

`SessionIdlePolicy` was a frozen dataclass. Its **generated public constructor**
took the mapping:

```python
@dataclass(frozen=True, slots=True)
class SessionIdlePolicy:
    durations: tuple[tuple[AuthMethod, timedelta], ...]
```

So the authority the API no longer accepted per call, it accepted per
construction:

```python
ordinary = timedelta(minutes=60)
policy = SessionIdlePolicy(tuple((method, ordinary) for method in AuthMethod))
repository = SessionRepository(connection, idle_policy=policy)
repository.touch(break_glass_session_id, now=now)
```

That mapping is **complete** (it names all three methods), **duplicate-free**
(each exactly once) and **positive** (sixty minutes each) — which is the entire
set of invariants `__post_init__` enforced. The constructor accepted it. The
generated `CASE` then selected sixty minutes for a persisted `webauthn` or
`recovery_grant` row, and `LEAST(now + 60 minutes, absolute_expires_at)` handed
that row its sixty-minute emergency absolute bound.

**Consequence.** N-15's fifteen-minute idle limit is inoperative for the whole
life of a session that resolves to `{platform_administrator}` (N-12). An
emergency session could sit unattended for the full sixty minutes of its absolute
lifetime while the documented rule says fifteen. The invalid pairing had moved
from the per-touch call into repository construction; it had not become
structurally impossible.

### Why the tests did not catch it

`test_an_idle_policy_must_cover_every_authentication_method` proved exactly the
three invariants the constructor enforced: completeness, uniqueness, positivity.
It never attempted a mapping that is **internally valid and semantically false**.
That is the whole gap, and it is why two statements in the previous submission
were untrue as written:

| Previous claim | Status |
|---|---|
| "There is no supported call shape in which a method and a duration can be paired, correctly or otherwise" | **False.** It reasoned about calls. The pairing lived in the constructor. |
| "built from `SessionSettings` and injected once at composition" | **False of the composition.** See §2. |

### The related composition defect

`WebComposition.services()` constructed a policy for `SessionRepository`, while
`SessionService.__init__()` independently constructed another from
`SessionSettings`:

```python
# adapters/web/composition.py                     # application/web/sessions.py
SessionRepository(                                 self._idle_policy = (
    connection,                                        SessionIdlePolicy.from_settings(settings)
    idle_policy=SessionIdlePolicy.from_settings(   )
        settings.session
    ),
)
```

Production gave both the same `settings.session`, so the two objects agreed and
nothing misbehaved. They were nevertheless **two derivations, not one instance**,
and an alternate construction site giving the repository one `SessionSettings`
and the service another would have left what a login's bounds are *created* with
disagreeing with what a refresh *applies* — with no test able to see it, because
no test compared the objects.

### Reachability, stated rather than smoothed over

**No P3.1 HTTP route calls `touch()`.** The defect was not reachable through
request handling in the delivered package, and neither is its correction: what
follows is proven at the service and repository boundary. That limits present
exposure; it does not waive the defect. P3.2 is intended to consume this
boundary, and N-15 must be structural *before* that wiring exists — the same
position taken for T-05c and T-05d and recorded again in RAID I-09.

---

## 2. The correction

The smallest cohesive change that makes the invalid mapping unrepresentable
rather than validated-and-rejected.

### 2.1 The policy has no public constructor

`application/web/sessions.py`:

```python
class SessionIdlePolicy:
    __slots__ = ("_ordinary", "_emergency")

    def __init__(self, *arguments: object, **keywords: object) -> None:
        raise TypeError(
            "SessionIdlePolicy has no public constructor: a caller that could "
            "name an authentication method beside a duration could give a "
            "break-glass session N-06's idle window (N-15). Build it with "
            "SessionIdlePolicy.from_settings(settings) and inject the result."
        )

    @classmethod
    def from_settings(cls, settings: SessionSettings) -> SessionIdlePolicy:
        ordinary = timedelta(minutes=settings.idle_minutes)
        emergency = timedelta(minutes=settings.emergency_idle_minutes)
        _validated_durations(_classified_durations(ordinary, emergency))
        policy = object.__new__(cls)
        object.__setattr__(policy, "_ordinary", ordinary)
        object.__setattr__(policy, "_emergency", emergency)
        return policy
```

**Why this cannot express an arbitrary mapping.** The only supported way to
obtain a policy is `from_settings`, whose single parameter is `SessionSettings` —
two integers among other unrelated session configuration. There is no parameter
of type `AuthMethod`, no parameter of type `timedelta`, and no parameter that is
a sequence or mapping of either. The method-to-window association is produced
entirely inside the module by `_classified_durations`, which iterates `AuthMethod`
itself:

```python
def _classified_durations(ordinary, emergency):
    return tuple(
        (method, emergency if method.is_break_glass else ordinary)
        for method in sorted(AuthMethod, key=lambda method: method.value)
    )
```

A mapping that omits a method, repeats one, or gives WebAuthn the ordinary value
is not a mapping this function can emit, and it is the only producer the class
has. `__init__` is defined and refuses rather than being left absent, so
`SessionIdlePolicy(...)` — under any argument spelling — is one explicit,
greppable refusal instead of an object with unfilled slots.

`__setattr__` and `__delattr__` refuse, so an injected policy cannot be rewritten
underneath the components holding it. No `__eq__` is defined, so `==` is identity:
a test asserting that two layers share a policy cannot be silently weakened into
a value comparison.

This does **not** rely on documentation, naming, underscore privacy, type hints
or a convention to use `from_settings()`. It also does not pretend Python can
stop a caller that reaches for `object.__new__` or rewrites process memory; the
required trust boundary is the supported application/repository API, and across
that boundary no method/duration pairing and no duration-selection parameter
exists.

### 2.2 Numbers stay in configuration; the policy owns only classification

`SessionSettings` remains the sole numeric source. `application/web/config.py`
validates both values at load with their register ceilings —
`WEB_SESSION_IDLE_MINUTES` (minimum 1, ceiling 60, policy N-06) and
`WEB_EMERGENCY_SESSION_IDLE_MINUTES` (minimum 1, ceiling 15, policy N-15). The
policy adds no range rule of its own and, in particular, **asserts no
`emergency < ordinary` invariant**: the contract permits an ordinary window
shorter than, equal to, or longer than the emergency one, and inventing that
constraint would refuse accepted configurations.

The structural invariant is method classification, and it holds for every
accepted pair of values: `discord_oauth` derives the configured ordinary value;
`webauthn` and `recovery_grant` each derive the configured emergency value.
Classification is `AuthMethod.is_break_glass`, i.e. `not is_ordinary_provider`,
so a future authentication method is governed automatically and governed as
break-glass — the shorter window — unless it is explicitly made the ordinary
provider. That is the safe direction for a default and it is documented as such.

### 2.3 One instance, built once, injected everywhere

`adapters/web/composition.py` builds the policy in `WebComposition.__init__` and
`services()` passes **that object**:

```python
self.session_idle_policy = SessionIdlePolicy.from_settings(settings.session)
...
session_repository = SessionRepository(connection, idle_policy=self.session_idle_policy)
session_service   = SessionService(..., idle_policy=self.session_idle_policy)
```

It is process-lifetime rather than per-request: it is immutable, it depends on
nothing but configuration, and building it once means a non-positive configured
window refuses the composition at startup rather than on the first refresh.

`SessionService.__init__` now takes `idle_policy` as a **required** keyword
argument and derives nothing. A default would be exactly how the second
derivation survived the previous review. Both `SessionRepository` and
`SessionService` expose a read-only `idle_policy` property so the single-instance
property is assertable with `is` rather than through a private attribute; the
object returned is immutable and offers no way to name a method beside a
duration, so this widens nothing.

### 2.4 What is deliberately unchanged

The conditional `UPDATE` is byte-for-byte the same statement:

```sql
UPDATE sessions
   SET last_seen_at = CAST(:now AS timestamptz),
       idle_expires_at = LEAST(
           CAST(:now AS timestamptz)
               + make_interval(secs => CASE auth_method WHEN … THEN … END),
           absolute_expires_at
       )
 WHERE id = :id
   AND auth_method IN (…)
   AND revoked_at IS NULL
   AND idle_expires_at > CAST(:now AS timestamptz)
   AND absolute_expires_at > CAST(:now AS timestamptz)
 RETURNING id, last_seen_at, idle_expires_at, absolute_expires_at
```

- one conditional `UPDATE` as the serialization boundary;
- the duration selected from the persisted row's `auth_method` inside the atomic
  write, configured N-06 for Discord OAuth and configured N-15 for both
  break-glass methods;
- the intended id, a governed persisted method, `revoked_at IS NULL`,
  `idle_expires_at > now` and `absolute_expires_at > now`, **strict** at both
  bounds — equality remains expired;
- `idle_expires_at` clamped to the existing `absolute_expires_at` in that same
  statement, and `absolute_expires_at` in no `SET` clause: touch never writes or
  extends it;
- a zero-row update remains a typed `SessionTouchRefused` at the service layer,
  leaving the complete row unchanged; the caller response remains **end the
  session, clear its cookie, do not retry as authenticated**;
- outer transaction ownership preserved; no preliminary liveness query, cache,
  route-ordering assumption, sleep, retry loop or trigger was added;
- no duration literal and no unexplained 60/15 appears in the adapter or the SQL.

---

## 3. Every changed file, construction site and caller

| File | Change |
|---|---|
| `application/web/sessions.py` | `SessionIdlePolicy` rewritten: no public constructor, `from_settings(SessionSettings)` as the only factory, mapping derived from `AuthMethod.is_break_glass` via new module-private `_classified_durations`, invariants moved to module-private `_validated_durations`, immutable via `__setattr__`/`__delattr__`, `for_method` refuses non-`AuthMethod`, `__iter__` regenerated from the two stored durations. `SessionService.__init__` takes a required `idle_policy` and no longer derives one; read-only `idle_policy` property added. Module docstring property 5 corrected. |
| `adapters/web/repositories.py` | Read-only `idle_policy` property on `SessionRepository`. `_touch_statement`, the SQL and `touch()` are unchanged. |
| `adapters/web/composition.py` | `session_idle_policy` built in `__init__` (added to `__slots__`) and injected into both `SessionRepository` and `SessionService` in `services()`. |
| `tools/session_revoke.py` | The already-present unused policy is now passed to `SessionService` as well as to `SessionRepository`; comment updated. |
| `tests/web/test_session_touch_lifetime.py` | `_repository()` helper uses `composition.session_idle_policy`; the two superseded policy tests replaced by the eleven TC-AUTH-19f cases in §4; module docstring extended with the third finding. |

**Every construction site of either component, and its policy source:**

| Site | `SessionRepository` | `SessionService` | Policy source |
|---|---|---|---|
| `adapters/web/composition.py:services()` | yes | yes | `self.session_idle_policy` — one instance, both |
| `tools/session_revoke.py:main()` | yes | yes | `_UNUSED_IDLE_POLICY` — one instance, both |
| `tests/web/test_session_touch_lifetime.py:_repository()` | yes | no | `composition.session_idle_policy` |
| `tests/web/test_session_touch_lifetime.py` (two classification cases) | yes | no | `SessionIdlePolicy.from_settings(replace(settings, …))` — deliberately non-default settings |

**Every caller of either touch API** is unchanged: `SessionService.touch(record,
*, now)` calls `SessionRepository.touch(record.id, now=now)`, and the only
callers of the service method are the tests in
`tests/web/test_session_touch_lifetime.py`. There is still **no P3.1 HTTP route**
that calls either.

---

## 4. Test evidence — TC-AUTH-19

Injected timestamps and real PostgreSQL throughout; no sleep anywhere in the
module. `tests/web/test_session_touch_lifetime.py` collects **44** tests, up from
25. Mapping to the prompt's fourteen required items:

| # | Required evidence | Test |
|---|---|---|
| 1 | Direct repository touch of Discord OAuth applies configured N-06 | `test_a_direct_repository_touch_of_an_oauth_row_applies_the_ordinary_window` |
| 2 | Direct repository touch of WebAuthn and recovery-grant applies configured N-15 | `test_a_direct_repository_touch_of_a_break_glass_row_applies_the_emergency_window[…]` (both methods) |
| 3 | The touch signature is exactly `(session_id, now)` | `test_the_repository_touch_signature_admits_no_duration_or_method` |
| 4 | The previous per-touch bypass is unavailable | `test_the_former_bypass_is_unavailable_rather_than_merely_refused[…]` |
| 5 | The all-ordinary mapping cannot be created or injected | `test_the_policy_admits_no_method_to_duration_mapping_at_construction`, `test_the_all_ordinary_policy_cannot_reach_the_database_at_all[…]`, `test_the_only_supported_policy_factory_takes_settings_and_nothing_else` |
| 6 | A mapping with only one break-glass method mis-assigned is unrepresentable | `test_the_policy_admits_no_method_to_duration_mapping_at_construction` (parameterised over both break-glass methods) |
| 7 | Non-default valid settings, including ordinary **shorter** than emergency, still map by classification | `test_classification_holds_for_every_accepted_configuration[60-15 / 30-10 / 1-1 / 5-15]`, `test_non_default_settings_map_by_classification_against_the_database[…]` |
| 8 | Repository and service hold the **same** policy instance | `test_the_composition_injects_one_policy_instance_into_both_layers`, `test_the_service_requires_an_injected_policy_and_derives_none` |
| 9 | Creation/rotation bounds and repository refresh use the same configured mapping | `test_creation_bounds_and_refresh_use_the_same_configured_mapping[…]` (all three methods) |
| 10 | Partial, duplicate, unknown-method, zero and negative input refused at construction with no permissive fallback | `test_a_non_positive_configured_window_is_refused_where_the_policy_is_built`, `test_a_partial_or_duplicated_mapping_is_refused_by_the_derivation_guard`, `test_a_window_is_defined_for_authentication_methods_and_nothing_else`, `test_the_repository_cannot_be_constructed_without_an_idle_policy` |
| 11 | Stale records cannot revive expired rows; exact bounds refused; accepted touches clamped, absolute unchanged | `test_a_stale_oauth_record_…`, `test_a_stale_break_glass_record_…[…]`, `test_an_absolute_expired_session_cannot_be_touched`, `test_a_revoked_session_cannot_be_touched`, `test_a_touch_exactly_at_the_idle_bound_is_refused`, `test_a_touch_exactly_at_the_absolute_bound_is_refused`, `test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it`, `test_repeated_refreshes_converge_on_the_absolute_bound_and_never_pass_it` |
| 12 | Zero-row writes remain typed refusals with the complete row unchanged | `test_the_service_raises_the_typed_refusal_when_no_row_is_updated` plus `_assert_refused_and_untouched` in every refusal case |
| 13 | Touch/revoke concurrency remains safe | `test_a_concurrent_refresh_and_revocation_never_leaves_a_refreshed_live_session` |
| 14 | Rotation lifetime and integrity tests unchanged in meaning and passing | `tests/web/test_session_rotation_lifetime.py`, `tests/web/test_session_rotation_integrity.py` — **not edited**; 83 pass with the touch and session suites |

**Item 5 is not satisfied by asserting a keyword is absent.** The finding's own
four-line sequence is executed in order —

```python
forged = SessionIdlePolicy(tuple((method, ORDINARY_IDLE) for method in AuthMethod))
SessionRepository(connection, idle_policy=forged)
```

— and shown to halt at line one with `TypeError`, with the target row proved
byte-identical afterwards (complete-row comparison, no successor, no audit event)
and the supported call then applying N-15 to the same row. Because the constructor
is intentionally unavailable, this is combined with narrow interface inspection:
the class's public callables are exactly `{from_settings, for_method}`,
`from_settings` takes `settings` alone, `__dataclass_fields__` is absent (so no
generated constructor and no `dataclasses.replace` route back), and `__slots__` is
`("_ordinary", "_emergency")` rather than a caller-supplied mapping.

**Honest scope note on item 10.** Since the constructor was closed, *no supported
API can present a partial or duplicated mapping* — the only producer is
`_classified_durations`, which derives it from the enum. Those two checks survive
as a guard on that derivation, and
`test_a_partial_or_duplicated_mapping_is_refused_by_the_derivation_guard` calls
the module-private `_validated_durations` **directly** and says in its docstring
that it is evidence the guard works, not evidence a caller can reach it. Only the
positivity check is reachable from configuration, and it is exercised through
`from_settings`. "Unknown method" is only meaningful as *not an `AuthMethod`*
(the enum is closed); the persisted-string case has its own separate control, the
statement's `auth_method IN (…)` predicate, proved by
`test_a_row_whose_method_the_policy_does_not_govern_is_refused` under a
rolled-back `ck_sessions_auth_method` drop.

### Mapping to contracts

| Anchor | Where |
|---|---|
| TC-AUTH-19 | `docs/contracts/phase-3-test-traceability.md`, row rewritten with a new clause (j) |
| N-06 / N-15 | `docs/contracts/phase-3-numeric-policy-register.md` — **values unchanged**; classification and single-source ownership described in §2.2 above |
| SM-02 | `docs/contracts/phase-3-state-machines.md`, `active → active` cell and the "break-glass session receiving the ordinary idle window" forbidden-transition row |
| T-05d | `docs/contracts/phase-3-threat-model.md`, mitigation column amended |

---

## 5. Mutation evidence

Sixteen mutants, each anchored uniquely with **exactly one** match required
(three anchors needed two-line context because the same predicate text appears in
`rotate()`'s locked read; the harness refuses to apply a mutant whose anchor
matches other than once). Each was applied to pristine bytes, run against
`tests/web/test_session_touch_lifetime.py`,
`tests/web/test_session_rotation_lifetime.py`,
`tests/web/test_session_rotation_integrity.py` and `tests/web/test_sessions.py`,
then reverted and the file digest compared with the pristine one before the next
mutant.

| # | Mutation | Result | Killed by |
|---|---|---|---|
| M1 | Reopen arbitrary public method/duration-pair construction | **KILLED** | `test_the_policy_admits_no_method_to_duration_mapping_at_construction` |
| M2 | Assign the ordinary value to WebAuthn | **KILLED** | `…receives_the_emergency_idle[WEBAUTHN]` |
| M3 | Assign the ordinary value to recovery-grant | **KILLED** | `…receives_the_emergency_idle[RECOVERY_GRANT]` |
| M4 | Swap ordinary and emergency method classification | **KILLED** | `test_an_oauth_session_touched_inside_its_window_receives_the_ordinary_idle` |
| M5 | Independently rebuild a different service policy | **KILLED** | `test_the_composition_injects_one_policy_instance_into_both_layers` |
| M6 | Remove liveness predicate `revoked_at IS NULL` | **KILLED** | `test_a_revoked_session_cannot_be_touched` |
| M7 | Remove liveness predicate `idle_expires_at > now` | **KILLED** | `test_a_stale_oauth_record_cannot_touch_an_idle_expired_unrevoked_row` |
| M8 | Remove liveness predicate `absolute_expires_at > now` | **KILLED** | `test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it` |
| M9 | Remove the governed-method predicate `auth_method IN (…)` | **KILLED** | `test_a_row_whose_method_the_policy_does_not_govern_is_refused` |
| M10 | Make the idle expiry comparison inclusive | **KILLED** | `test_a_touch_exactly_at_the_idle_bound_is_refused` |
| M11 | Make the absolute expiry comparison inclusive | **KILLED** | `test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it` |
| M12 | Remove the absolute clamp | **KILLED** | `test_repeated_refreshes_converge_on_the_absolute_bound_and_never_pass_it` |
| M13 | Treat a zero-row update as success | **KILLED** | `test_a_stale_oauth_record_cannot_touch_an_idle_expired_unrevoked_row` |
| M14 | Write and extend the absolute expiration | **KILLED** | `…receives_the_emergency_idle[WEBAUTHN]` |
| M15 | Let an injected policy be rewritten after construction | **KILLED** | `test_a_built_policy_cannot_be_rewritten_afterwards` |
| M16 | Let `for_method()` default a non-`AuthMethod` to the ordinary window | **KILLED** | `test_a_window_is_defined_for_authentication_methods_and_nothing_else` |

**16 applied, 16 killed. No mutant survived, and none is reported as equivalent.**

**Honest notes.** M8 and M11 are observable only inside the rolled-back
`ck_sessions_idle_within_absolute` drop: for every row that constraint permits,
`idle_expires_at > :now` already implies `absolute_expires_at > :now`, so without
that test they would be equivalent mutants. M9 is likewise observable only inside
the rolled-back `ck_sessions_auth_method` drop; no reachable row can fail that
predicate today, and the test says so rather than implying the guard runs in
ordinary operation. M5 is behaviourally equivalent under production settings —
it is killed by an identity assertion, which is precisely the point of §2.3, and
this is stated so the reviewer is not misled into reading it as a behavioural
kill.

**Restoration verified by digest** after the matrix, and the focused suite rerun
after final restoration (83 passed):

```
application/web/sessions.py    8d13c3c0f9cc67499d4808e8727472d19c3a783f922d69bd999c45531b33dfac
adapters/web/repositories.py   600d1157f284509397d2007d1e612a31b951340c4e70de5f323d3de25fd34fa2
```

For completeness, the digests of the other files changed by this remediation:

```
adapters/web/composition.py                     c639a2a277a1c5ae70b495a62b5719b47722eb97a409a84f8c06115458a79adf
tools/session_revoke.py                         9abb9b76ba0981287a80e0ac5d8226f121fdb707c175f38a68d8a716a5c9b546
tests/web/test_session_touch_lifetime.py        36d1082a0fd45d1e86bd2ed10ccc9b4bf96df8c96b0da8369e254534dee34250
```

The mutation harness lives outside the repository, in the session scratchpad. No
part of it was added to the tree.

---

## 6. Verification

Every command below was run. Environment guard: the disposable `freedom_test`
PostgreSQL database via `TEST_DATABASE_URL`, Unix-domain socket only. Only
synthetic data was used. No live Discord, Foundry, Google Sheets, staging or
production system was contacted; nothing was staged, committed or pushed.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_touch_lifetime.py -q` | **44 passed**, 0 failed, 0 skipped |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_touch_lifetime.py tests/web/test_session_rotation_lifetime.py tests/web/test_session_rotation_integrity.py tests/web/test_sessions.py -q` | **83 passed**, 0 failed, 0 skipped, 1 warning |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_oauth_completion_binding.py tests/web/test_identity_migration.py tests/web/test_operator_commands.py -q` | **57 passed**, 0 failed, 0 skipped, 9 warnings |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web -q` | **381 passed**, 0 failed, **0 skipped**, 14 warnings, 24.0s |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests -q` | **2260 passed**, 0 failed, 0 skipped, 1 warning, 142.6s |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests/test_database_schema.py tests/test_database_postgresql.py tests/test_runtime_grants.py tests/test_rejected_scope_absent.py tests/test_oauth_completion_binding_migration.py -q` | **101 passed**, 0 failed, 0 skipped, 1 warning |
| `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | `No new upgrade operations detected.` One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| `./venv-web/bin/python -m compileall -q adapters application tests tools` | Clean |
| `./venv/bin/python -m compileall -q models helpers ext main.py config.py` | Clean |
| `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 files `OK`, 0 non-`OK`** |
| `git diff --check` | Clean — no whitespace errors |
| Deterministic PostgreSQL concurrency evidence | TC-AUTH-19e (touch/revoke barrier rendezvous across two engines) and TC-AUTH-18e (concurrent rotation) pass; no sleeps |
| Mutation matrix (§5) | 16 run, 16 killed, restoration verified by digest, focused suite rerun after final restoration |

**The portal suite count rose from 362 to 381** — the 19 additional collected
tests are the TC-AUTH-19f cases and their parameterisations. No test was removed;
the two superseded policy tests were **replaced** by stronger ones covering the
same invariants plus the construction boundary.

**Warnings.** The portal suite's 14 warnings are pre-existing `httpx`
`DeprecationWarning`s about per-request cookies, in `test_sessions.py`,
`test_oauth_completion_binding.py` and `test_oauth_flow.py`. The bot suite's
single warning is `audioop` deprecation from `discord/player.py`. None is new and
none comes from the changed code.

**No skipped database test is counted as evidence, and none was skipped.** The
disposable database was available and every suite ran with zero skips.

**Formatter, linter and type checker: none is configured in this repository.**
Re-checked for this submission rather than restated: there is no
`pyproject.toml`, `setup.cfg`, `.flake8`, `.ruff.toml`, `mypy.ini`, `tox.ini` or
`.pre-commit-config.yaml`, and neither `requirements-dev.txt` nor
`requirements-web-dev.txt` lists one. `compileall` under both interpreters is the
available static check and it was run.

**Deliberately unrun evidence.** Every staging-class, browser-class,
real-device-class and direct-HTTP check remains unrun. Staging does not exist
(RAID I-06); no P3.1 route calls `touch()`, so there is no HTTP path to exercise;
and OD-45's direct-HTTP portions remain mandatory blocking evidence at P3.G2
against the real P3.2 routes and are **not** waived here.

---

## 7. Documentation amended

Earlier dated review records were **not** rewritten. The following governing
contracts and project-management records were amended where their present
assertions were false:

| Document | Amendment |
|---|---|
| `docs/contracts/phase-3-state-machines.md` | Header amendment note extended; SM-02 `active → active` cell; the "break-glass session receiving the ordinary idle window" forbidden-transition row — both now describe classification inside a policy with no public constructor, and record that two earlier mechanisms named there did not hold |
| `docs/contracts/phase-3-logical-schema.md` | §9.1 property 3 gains a third amendment stating that the earlier "no supported call shape" conclusion reasoned about calls while the pairing lived in construction; the enforcing-statement table row notes the policy's single factory |
| `docs/contracts/phase-3-threat-model.md` | T-05d mitigation amended with the constructor-level bypass, the composition defect, and the closed construction boundary |
| `docs/contracts/phase-3-test-traceability.md` | TC-AUTH-19 gains clause (j); the summary property row now covers construction as well as calls |
| `docs/operations/web-portal.md` | §4.3 records the third correction in operator terms and restates that no configurable value, schema object or deployment step changed |
| `docs/project-management/status.md` | Third 2026-08-15 update appended, not rewritten |
| `docs/project-management/raid-register.md` | I-09 amended again; resolution now also requires that no supported API admit a caller-*constructed* mapping and that both layers demonstrably hold one instance |
| `docs/project-management/change-log.md` | New entry **C-P3.1-I** with reason, alternatives rejected, scope, risk, testing and approval fields |
| `docs/project-management/decision-register.md` | Third OD-44 addendum for 2026-08-15; **no decision and no accepted numeric value changed** |

The documentation distinguishes, as required: numeric ownership by validated
configuration (§2.2); structural method classification within the policy (§2.1,
§2.2); one policy instance injected at composition (§2.3); persisted-method
selection and liveness enforcement in the atomic database statement (§2.4);
service translation of zero rows into typed refusal (§2.4); and the absent P3.1
HTTP touch caller (§1, §6).

---

## 8. Migration, deployment and rollback impact

**None.**

- **Migration:** no migration was added or edited. `0006`–`0009` are untouched;
  `alembic check` reports no new upgrade operations. This is an interface and
  composition correction and requires no schema change.
- **Deployment:** no configuration variable, default, ceiling or runtime grant
  changed, and this remediation did not touch `.env.example` (its pre-existing
  modification in the worktree belongs to earlier P3 work). A deployment carrying the current
  configuration behaves identically; a deployment whose `WEB_SESSION_IDLE_MINUTES`
  or `WEB_EMERGENCY_SESSION_IDLE_MINUTES` were somehow non-positive would now fail
  at composition construction rather than at first refresh — that configuration is
  already refused at load, so this is a second gate and not a new failure mode.
- **Rollback:** unaffected. Reverting the five changed files restores the previous
  behaviour with no data or schema consequence, because no persisted state,
  column, constraint or index is involved.
- **Dependencies:** none added. No manifest changed.

---

## 9. Worktree accounting and residual risks

**The worktree is dirty and was preserved.** `git status` before and after this
work shows the same set of unrelated modified and untracked paths from earlier
P3.0/P3.1 work — `adapters/web/`, `application/web/`, `docs/contracts/`,
`tests/web/`, `tools/`, `migrations/versions/0006`–`0009`, `requirements-web*`,
and the modified tracked files under `adapters/database/`, `application/audit.py`,
`tests/` and `docs/`. Nothing was cleaned, reverted, reorganised, staged,
committed or pushed. No historical submission was rewritten. The files this
remediation changed are the five in §3 plus the nine documents in §7, and nothing
else.

The final diff was reviewed for secrets, real player data, unsafe logs, generated
artefacts and unrelated edits: none found. All test data is synthetic; the
disposable-database guard (`ConnectionPolicy.UNIX_SOCKET_ONLY` against
`freedom_test`) was in force for every run.

**Residual risks, stated rather than described away:**

1. **Reachability is still boundary-level.** No P3.1 HTTP route calls `touch()`.
   This correction is proven at the service and repository boundary and not in
   request handling. The P3.2 package that wires it must treat
   `SessionTouchRefused` and `SessionRotationRefused` as end-the-session outcomes,
   never retries — carried in T-05c/T-05d and I-09.
2. **Python-level forgery is out of scope and not claimed against.** A caller
   executing `object.__new__(SessionIdlePolicy)` plus `object.__setattr__`, raw
   SQL, or process-memory edits can still produce whatever it likes. The claim is
   about the supported application/repository API only.
3. **A future `AuthMethod` is classified automatically as break-glass** unless
   made the ordinary provider. That is the safe direction, but it is a silent
   default and a reviewer adding a method should confirm it is the intended one.
   The `auth_method IN (…)` predicate still refuses a *persisted* method string
   outside the enum.
4. **This is the third correction of the same authority in one day.** Two previous
   submissions asserted that the pairing was unrepresentable and were wrong about
   where it lived. The re-reviews are asked to test the property directly rather
   than to read this document's claim of it — see §10.
5. **The `_validated_durations` completeness and uniqueness checks are now
   unreachable from any supported caller** and are tested by direct invocation of
   a module-private function. If a reviewer judges that unacceptable as evidence,
   the honest alternative is to delete those two checks, and that trade is
   flagged here rather than resolved unilaterally.

---

## 10. What is requested

A **fresh independent implementation review** and a **separately reported
security-focused review** of this remediation.

The reviews are specifically asked to attempt the bypass rather than read about
it: obtain N-06's sixty-minute window for a persisted `webauthn` or
`recovery_grant` row by **any** route the module exposes — the repository API, the
service API, the policy factory, direct construction under any argument spelling,
attribute assignment on an injected policy, and any second `SessionSettings`
supplied to one layer and not the other — and check every `SessionRepository` and
`SessionService` construction site for a second derivation or a default.

**This submission claims neither Codex acceptance nor Acceptance Authority
approval.** P3.G1 remains open. P3.2 has not started and no P3.2 route was added.
OD-45 is unchanged and no direct-HTTP evidence is waived.
