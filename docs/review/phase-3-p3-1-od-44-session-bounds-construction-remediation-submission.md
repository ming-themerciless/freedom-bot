# P3.1 OD-44 — session settings/bounds construction model (remediation submission)

**Date:** 2026-08-15 · **Package:** Phase 3 P3.1 · **Author:** Claude (Working
Technical Lead) · **Change record:** C-P3.1-J

**Status: submitted, not accepted.** This remediation requires a **fresh
independent implementation review** and a **separate, separately reported
security-focused re-review**. **P3.G1 remains open. P3.2 has not started.** No
acceptance is claimed or implied by anything in this document.

All changes are left **unstaged and uncommitted**.

---

## 1. Root cause of F1, F2 and F3

The three counterexamples are not three defects. They are one design mistake seen
from three angles: **an extensible policy object was made the authority boundary
for a numeric security policy.** Each previous remediation moved the invalid
pairing to a new position on that object and then argued that the new position was
closed, without asking whether the object should exist.

| | What was claimed | What was true |
|---|---|---|
| **F1** | "`SessionSettings` is validated at load, so `from_settings()` need only check positivity" | The reader is one of several documented builders. `SessionSettings` was a public frozen dataclass with no `__post_init__`, so `SessionSettings(..., emergency_idle_minutes=60, ...)` was a valid object and the policy derived from it returned sixty minutes for **both** break-glass methods. Validating at one builder cannot make invalid instances of a public type impossible |
| **F2** | "There is no supported shape in which an `AuthMethod` and a `timedelta` are named together" | The shape was `__iter__`, and the SQL generator consumed it. `class ForgedPolicy(SessionIdlePolicy)` overriding `__iter__` inherited the supported factory and replaced what the database used, while `for_method()` went on answering fifteen minutes. Ordinary subclassing — the previous submission's framing of this as process-memory forgery was wrong |
| **F3** | "One instance is built at the composition root and injected into both layers" | True of the composition root, and only of it. `SessionService.__init__()` took a policy beside the repository and required no relationship between them, so the property held by convention at two call sites rather than by construction |

The common failure is **arguing from the absence of one entry point**. A closed
`__init__` says nothing about a classmethod that constructs `cls`; a closed
constructor says nothing about the numbers it reads; correct wiring says nothing
about what an exported constructor permits. The only durable answer is to make the
authority not be a thing callers can hold.

### Recorded reproduction, before the correction

Run against the unmodified worktree at the start of this remediation:

```
F1 webauthn: 1:00:00 recovery: 1:00:00
F2 isinstance: True for_method: 0:15:00 iter: 1:00:00
F2 SQL params: {'idle_seconds_0': 3600.0, 'idle_seconds_1': 3600.0, 'idle_seconds_2': 3600.0}
F3 SessionService accepts independent policy: True
```

F2's third line is the decisive one: those are the bind parameters the real
`_touch_statement()` produced from the forged policy — **3600 seconds for every
method**, including `webauthn` and `recovery_grant`, from an object whose
`for_method()` reported 900.

### The same probes after the correction

```
F1 closed: these session settings do not satisfy the accepted numeric policy register: emergency_idle_minutes=60 exceeds …
F1 boundary 15 accepted
F1 boundary 16 refused
F2 SessionIdlePolicy exists? False
F2 SQL idle seconds: {'idle_seconds_0': 3600.0, 'idle_seconds_1': 900.0, 'idle_seconds_2': 900.0}
F2 methods: {'method_0': 'discord_oauth', 'method_1': 'recovery_grant', 'method_2': 'webauthn'}
F3 SessionService params: ['self', 'sessions', 'token_grants', 'audit']
```

---

## 2. Final construction and ownership model

```text
environment ──▶ SessionSettings          (frozen; __post_init__ enforces
                     │                    SESSION_CEILINGS — N-04/06/07/15/66)
                     │  passed once, by value
                     ▼
              SessionRepository(connection, settings=…)
                     │
                     ├─ SessionPolicy.derive(settings)   ← reads each number ONCE
                     │      · validates the register again, in a free function
                     │      · five durations/counts with fixed roles
                     │      · no mapping, no __iter__, nothing to override
                     │
                     ├─ _touch_statement(policy)         ← walks AuthMethod and
                     │      asks session_class_of(); binds :idle_seconds_n
                     │
                     └─ .policy  (read-only)
                              │
                              ▼
              SessionService(sessions=repository, …)
                     └─ self._policy = sessions.policy   ← no second argument
```

**Authority.** `SessionSettings` is the sole numeric authority and it is now
valid by construction. `SessionRepository` is the sole *derivation* site within a
graph. `SessionService` is a consumer. There is no third party.

**Dependency direction.** Configuration → repository → service. The direction is
chosen rather than incidental: the repository is the layer that *must* have the
numbers, because they are compiled into its conditional `UPDATE` at construction
time. Deriving them anywhere else would mean passing them down, and a value passed
is a value that can be a different one.

**Classification.** Which of the two windows a method receives is
`application/web/capabilities.py`'s `_SESSION_CLASSES` — an explicit, exhaustive
table. `AuthMethod.is_break_glass` is now a lookup in it, not
`not is_ordinary_provider`.

### Why no second authority remains

| Former second authority | Why it is gone |
|---|---|
| `SessionIdlePolicy`'s constructor / factory | The class is **deleted**. Nothing pairs a method with a duration anywhere in the codebase |
| The policy's `__iter__`, consumed by the SQL generator | Nothing is iterated. `_touch_statement` walks `AuthMethod` itself and calls `session_class_of()` per member |
| A policy object passed into `SessionRepository` | The constructor takes `(connection, *, settings)`. There is no parameter of any name through which a policy can enter |
| A policy or settings object passed into `SessionService` | The constructor takes `(sessions, token_grants, audit)`. Bounds are read from `sessions.policy` |
| `WebComposition.session_idle_policy` | Removed. The composition holds no bounds of its own to drift from the repository's |
| `SessionService._settings` (used for N-66 and the absolute bounds) | `max_sessions_per_account` and both absolute bounds moved onto `SessionPolicy`, so the service reads one object |
| `not is_ordinary_provider` as an implicit classifier | Replaced by an explicit table with an import-time completeness check |

### Every supported construction site

| Site | Construction | Bounds source |
|---|---|---|
| `adapters/web/composition.py` → `WebComposition.services()` | `SessionRepository(connection, settings=settings.session)`, then `SessionService(sessions=session_repository, token_grants=…, audit=…)` | the repository's derivation of `settings.session` |
| `tools/session_revoke.py` (C-07 operator command) | the same two lines, from a module-level `SessionSettings` at the accepted register values | the repository's derivation of that literal |
| `tests/web/*` | `_repository(composition, connection)` → `SessionRepository(connection, settings=composition.settings.session)` | identical to production |

There is no fourth. Neither constructor has a default, so a future site cannot
acquire bounds silently.

### Why F1, F2 and F3 are no longer expressible

- **F1** — `SessionSettings.__post_init__` refuses any value outside
  `SESSION_CEILINGS`. The offending object cannot be constructed by the reader, a
  test, a tool or direct Python, so nothing downstream can read a sixty-minute
  emergency window. `SessionPolicy.derive()` re-checks the same register in a free
  function, which is the form of the check that no subclass can override, and it
  reads each field **exactly once** into a local, so a subclass whose field is a
  property cannot answer 15 to the validator and 60 to the SQL.
- **F2** — refused earlier than "refused": the type does not exist, and the type
  that replaced it is *derived, never accepted*. A `SessionPolicy` subclass can
  still be written (Python is Python, and claiming otherwise would be the kind of
  assertion this review rejected before), but it has no parameter through which to
  reach a repository, and the SQL generator reads no overridable member. The test
  writes such a subclass, confirms it really is forged, and then shows every
  keyword refusing it while PostgreSQL still applies N-15 to the row.
- **F3** — not constructible: `SessionService` has no policy or settings
  parameter, and `service.policy is repository.policy` holds by assignment rather
  than by wiring discipline.

### What did **not** change

The conditional `UPDATE` is byte-for-byte the same shape:

```sql
UPDATE sessions
   SET last_seen_at = :now,
       idle_expires_at = LEAST(:now + make_interval(secs => CASE auth_method … END),
                               absolute_expires_at)
 WHERE id = :id
   AND auth_method IN (…)
   AND revoked_at IS NULL
   AND idle_expires_at > :now
   AND absolute_expires_at > :now
RETURNING id, last_seen_at, idle_expires_at, absolute_expires_at
```

`touch(session_id, *, now)` still accepts no method and no duration; both expiry
comparisons are still strict; the idle clamp is still `LEAST(…,
absolute_expires_at)`; `absolute_expires_at` still appears in no `SET` clause;
zero updated rows are still the typed `SessionTouchRefused`, whose eventual HTTP
handling must **end the session, not retry it as authenticated**; transactions are
still owned by the caller; liveness is still decided by PostgreSQL inside the
write.

---

## 3. Files changed, and why

| File | Change | Finding |
|---|---|---|
| `application/web/capabilities.py` | Added `SessionClass`, `UnclassifiedAuthMethod`, the explicit `_SESSION_CLASSES` table, `unclassified_methods()`, `require_complete_classification()` (called at import) and `session_class_of()`. `AuthMethod.is_break_glass` / `is_ordinary_provider` are now lookups | Requirement 5 |
| `application/web/config.py` | Added `SESSION_CEILINGS` (one table of ceiling + policy id) and `SessionSettings.__post_init__`. `_read_session` reads bounds from the register instead of restating them. `_Reader.integer` and the cookie-name checks now follow a recorded problem with an **in-range** fallback | F1 (+ collateral, §6) |
| `application/web/sessions.py` | **Deleted** `SessionIdlePolicy`, `_classified_durations`, `_validated_durations`. Added `SessionPolicy` (+ `derive`, `idle_for`, `absolute_for`, `bounds_for`) and the free function `_validate_policy_values`. `SessionService.__init__` lost `settings` and `idle_policy` and reads `sessions.policy` | F1, F2, F3 |
| `adapters/web/repositories.py` | `SessionRepository(connection, *, settings)` derives and owns the policy; exposes `.policy`. `_touch_statement` walks `AuthMethod` and classifies, instead of iterating its argument | F2, F3 |
| `adapters/web/composition.py` | Removed `session_idle_policy`; both construction sites use the revised model | F3 |
| `tools/session_revoke.py` | Same revised model; the placeholder settings are now a real, register-valid `SessionSettings` | Requirement 9 |
| `tests/web/test_session_touch_lifetime.py` | Replaced the superseded policy-construction tests with TC-AUTH-19(k); rewrote the `_repository` helper and the module preamble | §4 |
| `tests/web/test_structural_guards.py` | Added the aggregation regression test for the reader fallback | §6 |
| Controlled documents | `phase-3-state-machines.md` (SM-02 + forbidden transition), `phase-3-logical-schema.md` §9.1, `phase-3-numeric-policy-register.md` (enforcement location), `phase-3-threat-model.md` (T-05d), `phase-3-test-traceability.md` (TC-AUTH-19), `status.md`, `decision-register.md`, `raid-register.md` (I-09), `change-log.md` (C-P3.1-J), `operations/web-portal.md` §4.3 | §5 |

**Deleted deliberately.** `_validated_durations`'s completeness and uniqueness
checks are gone rather than retained. The previous submission itself recorded that
no caller could reach them, and the prompt is explicit that dead validation and
tests that call private helpers to preserve the appearance of an invariant are not
to be kept. What replaced them is a check with a **reachable production path**:
`require_complete_classification()` runs at import of `capabilities.py`, and its
reachable condition — a member added to `AuthMethod` without a table entry — is
exactly what requirement 5 asks to fail visibly.

---

## 4. Regression evidence, mapped to each requirement

All in `tests/web/test_session_touch_lifetime.py` unless noted. Every one runs
against real PostgreSQL where it makes a database claim; none uses a mock or
SQLite.

| # | Required | Test |
|---|---|---|
| 1 | `emergency_idle_minutes=60` refused before a repository can refresh; 15 accepted, 16 refused | `test_out_of_register_session_settings_are_refused_at_construction` (every register field, both directions, ceiling and 1 accepted), `test_the_emergency_idle_boundary_is_fifteen_accepted_and_sixteen_refused`, `test_the_f1_sequence_cannot_reach_a_refresh_at_all` (runs F1's sequence in order against PostgreSQL, asserts the row is byte-identical, then shows N-15 applied to the same row), `test_settings_cannot_be_edited_after_construction_to_get_around_the_register` |
| 2 | The subclass/overridden-iteration sequence cannot influence SQL or obtain a 60-minute break-glass refresh; prefer structural elimination; prove the replacement against PostgreSQL | `test_no_type_pairs_an_authentication_method_with_a_duration` (the class is gone; `SessionPolicy` has no `__iter__`; the repository's parameters are `connection`+`settings`), `test_the_refresh_statement_is_generated_from_classification_not_from_an_argument` (asserts the **bind parameters** the write uses), `test_a_subclassed_policy_cannot_be_given_to_a_repository` (writes a genuinely forged subclass, shows no keyword accepts it, then proves N-15 from PostgreSQL on a persisted break-glass row), `test_deriving_a_policy_from_a_lying_settings_subclass_validates_what_it_uses`, `test_a_directly_constructed_policy_is_still_held_to_the_register`, `test_a_policy_is_derived_from_settings_and_not_from_a_duck_type` |
| 3 | A graph cannot be built with two bounds sources; execute the former mismatch sequence | `test_a_service_cannot_be_given_a_second_bounds_source` (two genuinely different valid configurations — 5 vs 60 minute ordinary window — attempted through four keywords, then `service.policy is repository.policy`), `test_the_composition_gives_each_graph_one_bounds_source` |
| 4 | Persisted WebAuthn and recovery-grant rows get the emergency window; Discord OAuth gets the ordinary one | `test_an_oauth_session_touched_inside_its_window_receives_the_ordinary_idle`, `test_a_break_glass_session_touched_inside_its_window_receives_the_emergency_idle` (both methods), `test_non_default_settings_map_by_classification_against_the_database`, `test_classification_holds_for_every_accepted_configuration` (including ordinary **shorter** than emergency) |
| 5 | Every exact idle and absolute boundary refused; stale, revoked and unknown rows cannot be revived | TC-AUTH-19b/c group, unchanged and re-run: stale OAuth and both break-glass stale records, absolute-expired, revoked, and the exact-boundary cases including the rolled-back `ck_sessions_idle_within_absolute` drop |
| 6 | Accepted refreshes clamp to the original absolute expiry and never update it | `test_repeated_refreshes_converge_on_the_absolute_bound_and_never_pass_it`, plus the `absolute_expires_at` assertion in every accepted-refresh case |
| 7 | Zero-row refresh remains `SessionTouchRefused` at the service boundary | `test_the_service_raises_the_typed_refusal_when_no_row_is_updated` |
| 8 | Refresh/revocation concurrency safe against real PostgreSQL | `test_a_concurrent_refresh_and_revocation_never_leaves_a_refreshed_live_session` (two engines, barrier rendezvous, no sleeps) |
| 9 | All creation, rotation, refresh and operator-tool construction sites use the one model | `test_every_supported_session_construction_site_uses_the_one_model` (exercises the operator tool's settings and both constructors), `test_creation_bounds_and_refresh_use_the_same_derived_policy` (per method, creation bound vs what the database wrote), `test_the_repository_cannot_be_constructed_without_settings` |
| 10 | A synthetic/future method causes a startup/construction refusal, not a silent window | `test_every_authentication_method_is_explicitly_classified`, `test_an_unclassified_future_method_is_refused_by_the_completeness_check`, `test_an_unclassified_method_refuses_repository_construction`, `test_the_classification_is_restored_after_the_patched_case` |

### Honest scope of the requirement-10 evidence

`AuthMethod` is a closed enum; a test cannot add a member to it. The requirement is
therefore proved from two directions, and neither is presented as more than it is:

1. **The guard's logic, on real code, with a synthetic enum.**
   `unclassified_methods()` and `require_complete_classification()` are generic
   over the enum and the table precisely so a test can hand them a synthetic
   `FutureAuthMethod` with an unclassified `service_token` member. This proves the
   check and its message are correct for exactly the condition a future method
   creates. It does **not** prove that someone editing `AuthMethod` will run it.
2. **That it runs, on the production table.** `require_complete_classification` is
   called at import of `capabilities.py`, so an unclassified member makes the
   module unimportable — a startup failure. The construction half is proved by
   removing `RECOVERY_GRANT` from the production table with `monkeypatch` and
   observing `SessionRepository(...)` raise `UnclassifiedAuthMethod`; the *table*
   is patched rather than the enum because the enum cannot be extended, and that
   is the same condition from the branching code's point of view. Restoration is
   asserted in its own test rather than trusted.

### Database-constraint discipline

No production check or database constraint was weakened. The two tests that need
an otherwise-unreachable row (`ck_sessions_auth_method`,
`ck_sessions_idle_within_absolute`) drop the constraint **inside a transaction they
roll back** and then assert, on a fresh connection, that the constraint is present
in `pg_constraint` and the row's `auth_method` is unchanged. Both are pre-existing
and unmodified.

### Tests that would have passed before, and are therefore not offered as new evidence

The new tests import `SessionPolicy`, `SESSION_CEILINGS`, `session_class_of` and
`UnclassifiedAuthMethod`, none of which existed before this remediation, so they
cannot be run against the pre-correction tree; that is stated plainly rather than
dressed up as "they fail before". The behavioural evidence that the properties did
**not** hold before is the recorded reproduction in §1, which was produced by the
unmodified code and includes the real `_touch_statement()` binding 3600 seconds for
`webauthn`.

---

## 5. Documentation amended

Earlier dated review records were **not** rewritten; every amendment is appended
and dated, and each preserves the failed approach it replaces.

| Document | Amendment |
|---|---|
| `docs/contracts/phase-3-state-machines.md` | SM-02's idle-refresh mechanism cell and the "break-glass session receiving the ordinary idle window" forbidden transition now describe the derived model; the preamble records the fourth amendment and its three counterexamples |
| `docs/contracts/phase-3-logical-schema.md` §9.1 | The statement row's provenance sentence corrected; a fourth dated amendment records that the previous "no supported shape at any layer" conclusion was false in two ways, and states what replaced it |
| `docs/contracts/phase-3-numeric-policy-register.md` | New subsection recording **where** the session bounds became enforceable, and that the ceiling doubles as the accepted default. **No value changed** |
| `docs/contracts/phase-3-threat-model.md` T-05d | Fourth amendment: F1/F2/F3 and the structural correction |
| `docs/contracts/phase-3-test-traceability.md` | TC-AUTH-19 gains **(k)** |
| `docs/project-management/status.md` | Fourth 2026-08-15 update, prepended; header status line updated |
| `docs/project-management/decision-register.md` | Fourth OD-44 addendum. **No decision changed** |
| `docs/project-management/raid-register.md` | I-09 amended a fourth time; resolution criteria extended |
| `docs/project-management/change-log.md` | New record **C-P3.1-J** |
| `docs/operations/web-portal.md` §4.3 | Operator-facing fourth amendment, in operator language, with the explicit note that no configurable value, variable name, schema object or deployment step changed |

Two things are stated in those documents rather than smoothed over: Python
annotations are **not** described as runtime enforcement anywhere, and no property
is claimed from correct production wiring where an exported constructor permits a
conflicting graph — which is precisely the error F3 recorded.

---

## 6. One collateral change, called out rather than folded in

`SessionSettings` is constructed **inside** `_read_session`, so making its
constructor strict would have broken the configuration module's rule 2 — *every
problem is reported, not the first*. An operator with four bad session bounds
would have seen a `ValueError` naming one, instead of a `ConfigurationError`
naming four.

The fix is to make the reader's documented fallback actually usable:
`_Reader.integer` now returns the clamped in-range value after recording the
problem, and `_read_session` falls back to the default cookie name after recording
a cookie-shape problem. A run that recorded a problem still never returns settings.

This is load-bearing and was verified, not assumed. With the clamp, four bad
session variables produce a `ConfigurationError` naming all of them; with the
pre-fix accessor restored at runtime, the same environment raises
`ValueError: … idle_minutes=90 exceeds …` and the aggregation is lost.
`test_every_out_of_range_session_bound_is_reported_in_one_pass` is the regression
test, and the seven existing S-10 refusal cases in `test_structural_guards.py` are
unchanged and still pass.

---

## 7. Verification

Every command below was run **after** this remediation, on this worktree. No
earlier result is repeated.

**Database target safety.** `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`
— a Unix-domain socket to the disposable database. `psql -Atc "select
current_database(), inet_server_addr() is null" freedom_test` → `freedom_test|t`,
confirming the local socket. `tests/conftest.py`'s disposable-database guards were
active throughout; production and `freedom_dev` were never contacted.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_touch_lifetime.py -q` | **54 passed**, 0 failed, 0 skipped |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_touch_lifetime.py tests/web/test_session_rotation_lifetime.py tests/web/test_session_rotation_integrity.py tests/web/test_sessions.py tests/web/test_structural_guards.py -q` | **134 passed**, 0 failed, 0 skipped, 1 warning |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web -q` | **392 passed**, 0 failed, **0 skipped**, 14 warnings, 24.3 s |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests -q` | **2260 passed**, 0 failed, 0 skipped, 1 warning, 131.8 s |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests/test_database_schema.py tests/test_database_postgresql.py tests/test_runtime_grants.py tests/test_rejected_scope_absent.py tests/test_oauth_completion_binding_migration.py -q` | **101 passed**, 0 failed, 0 skipped, 1 warning |
| `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | `No new upgrade operations detected.` One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| `./venv-web/bin/python -m compileall -q adapters application tests tools` | Clean |
| `./venv/bin/python -m compileall -q models helpers ext main.py config.py` | Clean |
| `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 `OK`, 0 non-`OK`** |
| `git diff --check` | Clean — no whitespace errors |

**Portal suite count: 381 → 392.** Ten of the eleven additions are the TC-AUTH-19(k)
cases and their parameterisations; the eleventh is the configuration-aggregation
regression test. **No test was removed.** The superseded policy-construction tests
were **replaced** by stronger ones covering the same invariants against the
revised boundary; the tests that called `_validated_durations` directly were
deleted along with the helper, as the prompt requires.

**Warnings.** The portal suite's 14 warnings are the pre-existing `httpx`
per-request-cookie `DeprecationWarning`s in `test_sessions.py`,
`test_oauth_completion_binding.py` and `test_oauth_flow.py`. The bot suite's single
warning is `audioop` deprecation from `discord/player.py`. None is new and none
originates in the changed code.

**Formatter, linter and type checker: none is configured in this repository.**
Re-checked for this submission rather than restated: there is no `pyproject.toml`,
`setup.cfg`, `.flake8`, `.ruff.toml`, `mypy.ini`, `tox.ini` or
`.pre-commit-config.yaml`, and neither `requirements-dev.txt` nor
`requirements-web-dev.txt` lists one. `compileall` under both interpreters is the
available static check and it was run.

**Mutation testing was not run, and none is claimed.** The prompt makes it useful
only after the direct counterexamples are closed; they are closed and demonstrated
by the recorded before/after reproductions in §1. Running it is a reasonable
reviewer request and is not being pre-empted with a partial matrix.

**Deliberately unrun.** Every staging-class, browser-class, real-device-class and
direct-HTTP check remains unrun. Staging does not exist (RAID I-06); no P3.1 route
calls `touch()`, so there is no HTTP path to exercise; and OD-45's direct-HTTP
portions remain mandatory blocking evidence at P3.G2 against the real P3.2 routes
and are **not** waived here.

---

## 8. Security, configuration, deployment, migration and rollback impact

- **Security.** Strictly a tightening. N-15's fifteen-minute idle window now holds
  against how the bounds are *built*, not only against how they are called or
  constructed; an unclassified future authentication method fails closed and
  loudly instead of inheriting a window; and every session bound is enforced at
  every construction of the type that carries it. No control was relaxed, and the
  atomic, PostgreSQL-authoritative liveness properties are unchanged.
- **Configuration.** **No variable added, renamed or removed; no accepted value
  changed; no deployment value changed.** `.env.example` needs no edit. The only
  operator-visible difference is that an out-of-range value is now refused by the
  settings type as well as by the reader — the same refusal, one layer earlier.
- **Deployment.** No change. No new dependency, no systemd unit change, no
  runtime-grant change, no proxy change.
- **Migration and schema.** **None**, and none was needed: the defect and its
  correction are entirely in construction and composition. Migrations 0006–0009
  were not edited. `alembic check` reports no new upgrade operations.
- **Rollback.** Unaffected. Reverting these files restores the previous behaviour
  with no data implication, because nothing persisted changed shape or meaning.

---

## 9. Complete accounting for the pre-existing dirty worktree

The worktree contains 59 entries of intentional uncommitted Phase 3 work, on
branch `docs/platform-plan`. **All unrelated changes were preserved; nothing was
staged, committed, pushed, stashed or reverted, and no secret was read or
modified.**

Files this remediation touched (all pre-existing except the last):

- `application/web/capabilities.py`, `application/web/config.py`,
  `application/web/sessions.py` — inside the untracked `application/web/` tree
- `adapters/web/repositories.py`, `adapters/web/composition.py` — inside the
  untracked `adapters/web/` tree
- `tools/session_revoke.py` — untracked
- `tests/web/test_session_touch_lifetime.py`,
  `tests/web/test_structural_guards.py` — inside the untracked `tests/web/` tree
- `docs/contracts/phase-3-state-machines.md`,
  `docs/contracts/phase-3-logical-schema.md`,
  `docs/contracts/phase-3-numeric-policy-register.md`,
  `docs/contracts/phase-3-threat-model.md`,
  `docs/contracts/phase-3-test-traceability.md`,
  `docs/operations/web-portal.md` — inside the untracked `docs/contracts/` and
  `docs/operations/` trees
- `docs/project-management/status.md`, `decision-register.md`,
  `raid-register.md`, `change-log.md` — tracked, modified, **appended to only**
- `docs/review/phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md`
  — **new**

Everything else in `git status` — including `docs/review/Handover information`,
`.env.example`, `.gitignore`, the `adapters/database/`, `migrations/`,
`infra/`, `requirements-*` and benchmark changes — is untouched by this
remediation and was already present when it began.

---

## 10. Unresolved risks and requested reviewer focus

**Stated without minimising:**

1. **`SessionPolicy` is a public frozen dataclass and is therefore nameable.** It
   is *derived and never accepted*, so no supported constructor lets one in, and
   its `__post_init__` validates the register — but a reviewer should decide
   whether "derived, never accepted" is a strong enough boundary or whether the
   type should become module-private. This is the residual most similar in kind to
   F1/F2 and it is flagged deliberately rather than argued away.
2. **`touch()` is still unreachable from any P3.1 HTTP route.** This correction is
   proven at the service and repository boundary, not in request handling. The
   P3.2 package that wires it **must** treat `SessionTouchRefused` and
   `SessionRotationRefused` as end-the-session outcomes — clear the cookie, treat
   the request as unauthenticated — and never as retries. Unchanged from previous
   submissions and repeated because it remains true.
3. **The requirement-10 evidence is two-part by necessity** (§4). A reviewer who
   considers the synthetic-enum technique insufficient should say so; the
   alternative would be changing `AuthMethod`'s member values to carry the
   classification, which was rejected because `.value` is the persisted
   `auth_method` column.
4. **Mutation testing has not been run for this remediation** (§7).
5. **This is the fourth correction of the same authority in one day.** The pattern
   in each previous failure was arguing from the absence of one entry point. A
   reviewer's most useful question is not "is this entry point closed" but "what is
   the complete set of ways the two numbers reach `make_interval`".

**Requested reviewer focus.** Attempt to obtain N-06's sixty-minute window for a
persisted WebAuthn or recovery-grant row by **any** route: the `SessionSettings`
constructor and `dataclasses.replace`, `SessionPolicy.derive`, subclassing either
type, `SessionRepository.__init__`, `SessionService.__init__`, the operator tool,
and any construction site not listed in §2. Then check whether any *other* accepted
numeric policy in `WebSettings` has the F1 shape — a public settings dataclass whose
bounds only the environment reader enforces. This remediation fixed
`SessionSettings`; it did not audit the other settings types, and that is a known
gap rather than an oversight being reported as complete.

---

## 11. Stop condition

All changes are left **unstaged and uncommitted**.

**P3.G1 remains open**, pending a fresh independent implementation review, a
separate security-focused re-review, and maintainer acceptance. **P3.2 has not
started, and no part of it is claimed.** I-09 is amended, not closed. Nothing in
this document accepts anything.
