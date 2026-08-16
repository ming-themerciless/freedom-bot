# P3.1 OD-44 — session-policy numeric validation (remediation submission)

Date: 2026-08-15 · Package: Phase 3 P3.1 · Owner: Claude (implementing Technical
Lead) · Baseline: implementation plan v1.5, `phase-3-delivery-plan.md` accepted
2026-08-13.

Reviewed inputs, both dated 2026-08-15:

- [`phase-3-p3-1-od-44-session-bounds-construction-codex-review.md`](phase-3-p3-1-od-44-session-bounds-construction-codex-review.md)
  — Blocking **F1**;
- [`phase-3-p3-1-od-44-session-bounds-construction-codex-security-review.md`](phase-3-p3-1-od-44-session-bounds-construction-codex-security-review.md)
  — Blocking **S1**.

**Gate status: P3.G1 remains open.** Nothing in this document accepts anything.
The remediation is submitted for a fresh independent implementation re-review and
a separately reported security-focused re-review, and then maintainer acceptance.
**P3.2 has not started and no part of it is claimed.** RAID I-09 is amended, not
closed.

---

## 1. Scope

Narrow completion of one blocking defect in the session-policy numeric
validation, plus the regression tests and controlled-document updates that were
missing from the worktree. No new design, no new feature, no new variable, no
schema or migration change, and no change to any accepted numeric value.

---

## 2. The two Codex reports describe **one** blocking defect

Stated explicitly, because the two reports were produced separately and could be
mistaken for two findings:

**F1 (implementation review) and S1 (security-focused review) are the same
defect, seen from two directions.** F1 describes the mechanism — a validator that
admits a value outside the numeric policy's type. S1 describes the consequence —
loss of the accepted per-account live-session limit. There is one root cause, one
correction, and one set of regressions; each report's "required remediation"
section is satisfied by the same work.

Nothing in either report is left unaddressed, and no additional defect was found
during this remediation.

---

## 3. Root cause: divergent type semantics between settings and derived policy

The `SESSION_CEILINGS` register gave both enforcement gates the same **bounds**,
and left each of them to state independently what a value of these fields may
**be**:

| Gate | What it required |
|---|---|
| `SessionSettings.__post_init__` | an actual `int`, **not** a `bool`, positive, no greater than its ceiling |
| the derived-policy gate (`_validate_policy_values`) | `value < 1` is a problem; `value > ceiling` is a problem |

Two ordering comparisons are **not** a whole-number rule. `float("nan")` is
neither `< 1` nor `> ceiling`, so both comparisons are false and the value was
accepted. `SessionPolicy.__post_init__` delegated to the same incomplete
validator, so it added no independent check.

The value then reached `SessionService._enforce_session_limit`, whose loop is

```python
while len(live) >= maximum:
```

`len(live)` is an `int`; `maximum` was NaN. The comparison is false for **every**
live-session count, the loop never runs, nothing is revoked, no audit event is
written — **N-66 was inoperative.**

**Why it was reachable without forgery.** `SessionPolicy.derive()` accepts
subclasses of `SessionSettings` deliberately, so what it reads is not necessarily
what `SessionSettings.__post_init__` observed. A subclass whose inherited
construction sees the valid stored integer can answer differently on the single
later derivation read. No `object.__new__`, no mutation of a frozen instance, no
forged `SessionPolicy` and no private helper is required — only the supported
repository constructor.

The deeper cause is the one the review named: **the rule had two definitions**,
and the second one drifted. The correction is not a third guard.

---

## 4. The final shared invariant, and every enforcement point

### 4.1 The invariant

For every field in the authoritative register (`SESSION_CEILINGS` in
`application/web/config.py`, mirroring `phase-3-numeric-policy-register.md`):

1. the value is an actual `int`;
2. `bool` is refused — `bool` subclasses `int`, so `True` would be a maximum of
   one and `False` a maximum of zero, neither of which is a number an operator can
   have meant;
3. **all** floats are refused, as a class: integral-looking (`10.0`), fractional,
   `+inf`, `-inf` and NaN alike. The rule is expressed as a type precisely so it
   is not a list of the values one review happened to find;
4. the value is positive;
5. the value is no greater than its registered ceiling — every bound is a ceiling
   with a floor of 1 (S-10), so a deployment may tighten an accepted policy and
   never loosen it;
6. accepted stricter integers remain accepted, unchanged;
7. the exact value read and validated during derivation is the exact value stored
   in `SessionPolicy` and used by repository and service behaviour; and
8. environment loading still aggregates every problem and still names variables
   without ever naming a value.

### 4.2 The one definition

`application/web/config.py`, beside the ceilings table it reads:

- `session_policy_problem(field_name, value) -> str | None` — the single runtime
  statement of (1)–(5) for one field, returning the *first* problem so a
  wrong-typed value is reported as wrong-typed rather than also compared against a
  bound it cannot meaningfully be compared with;
- `session_policy_problems(values) -> list[str]` — the same, collected rather than
  short-circuited, over the subset of register fields a caller holds;
- `validate_session_policy_values(values, *, subject)` — raises `ValueError`
  naming every problem.

A key that is not in `SESSION_CEILINGS` raises `KeyError` rather than being
silently unchecked.

### 4.3 Every enforcement point

| Point | Calls | Covers |
|---|---|---|
| `SessionSettings.__post_init__` (`config.py`) | `session_policy_problems` over **all six** register fields, plus the cookie-shape rules (N-05/S-03) that belong to this type alone | any construction of settings — reader, test, operator tool, direct Python, `dataclasses.replace` |
| `SessionPolicy.derive()` (`sessions.py`) | `_validate_policy_values` → `validate_session_policy_values` over the **five** lifetime fields, on locals read exactly once | the one supported construction, including from a `SessionSettings` **subclass** |
| `SessionPolicy.__post_init__` (`sessions.py`) | the same function, after converting the stored `timedelta`s back to whole minutes/hours | direct construction and `dataclasses.replace` of a policy |
| `_Reader.integer` (`config.py`) | `SESSION_CEILINGS` for ceiling and accepted default | the environment boundary — records the problem and returns an **in-range** fallback so collection continues |

Point (7) of the invariant holds mechanically: `derive()` reads each attribute
once into a local (`sessions.py:171-175`), validates the locals
(`sessions.py:176-182`), and constructs from **those same locals**
(`sessions.py:183-189`). There is no second read for a property to answer
differently, and no re-derivation between validation and storage. `grep` confirms
the only consumer of the maximum is `_enforce_session_limit` via
`self._policy` (`sessions.py:525`), and the only producer is
`SessionPolicy.derive(settings)` at `adapters/web/repositories.py:381`.

### 4.4 What was deliberately **not** done

Each of these was named in the prompt as an unacceptable shortcut, and none is
present:

- NaN is not special-cased — the rule is a type rule;
- no annotation is relied on for enforcement (`_validate_policy_values` annotates
  its parameters `object` on purpose: they are where unvalidated numbers arrive);
- `SessionSettings` is not made unsubclassable — `derive()` accepts subclasses by
  design, and the honest fix is to fully validate what it reads;
- no reflection, source inspection or caller introspection is used;
- no type or range logic is duplicated into another layer;
- precise direct-construction errors are preserved (`ValueError` naming field
  **and value**, which is correct at a boundary whose inputs are literals in code,
  a test or an operator tool);
- safe aggregated `ConfigurationError` reporting is preserved at the environment
  boundary (variables named, values never).

---

## 5. Files changed, and why

### 5.1 Implementation — inspected and validated, **not** changed by me

The prompt states that the worktree already contained a partial implementation
and instructs that it be treated as unverified. It was, and I am explicit about
what I did:

| File | State on entry | Action |
|---|---|---|
| `application/web/config.py` | already held `SESSION_CEILINGS`, `session_policy_problem`, `session_policy_problems`, `validate_session_policy_values`, and `SessionSettings.__post_init__` calling the shared definition | **inspected, traced, falsified, left unchanged** |
| `application/web/sessions.py` | `_validate_policy_values` already delegated to `validate_session_policy_values`; `SessionPolicy.__post_init__` and `derive()` already routed through it | **inspected, traced, falsified, left unchanged** |
| `adapters/web/repositories.py` | already derived its policy and accepted none | **inspected, unchanged** |
| `adapters/web/composition.py`, `tools/session_revoke.py` | already the two supported construction sites, both passing a real `SessionSettings` | **inspected, unchanged** |

I did not assume the comments proved correctness. The complete runtime data path
was traced by reading it, by enumerating every consumer of
`max_sessions_per_account`, and by **executing** Codex's own reproduction, which
now refuses:

```text
REFUSED: these session bounds do not satisfy the accepted numeric policy register:
max_sessions_per_account must be a whole number of the unit its name gives — an
int, and never a bool, a float or a non-finite value — not nan
reads 2
```

`reads 2` is the reproduction's own counter: one read during inherited
construction, one during derivation. Both halves of the reported shape are
present, and the refusal is at the derivation read.

**Conclusion: no implementation correction was necessary, and none was made.** If
a re-reviewer disagrees with that judgement, §11 names exactly where to look.

### 5.2 Tests — new

| File | Why |
|---|---|
| `tests/web/test_session_policy_numeric_validation.py` | **New.** 28 cases, mapped one-to-one to the eight required proofs in §6. Placed in its own module rather than appended to `test_session_touch_lifetime.py` because it is about a different invariant (the *type* of the register's numbers) and because a reviewer should be able to run the evidence for this finding alone |

No test was removed, weakened, renamed or replaced.

### 5.3 Controlled documents — appended to, never rewritten

| File | Change |
|---|---|
| `docs/contracts/phase-3-numeric-policy-register.md` | New subsection "What these numbers *are*", recording the **type** half of the accepted fields and where its single definition lives. **No numeric value changed** |
| `docs/contracts/phase-3-logical-schema.md` §9.1 | Addendum: "reading each value exactly once" is only worth something if that read is validated completely; both gates now call one definition |
| `docs/contracts/phase-3-test-traceability.md` | TC-AUTH-19 gains **(l)**; new row **TC-SESS-08b** |
| `docs/project-management/status.md` | Fifth 2026-08-15 update, appended above the fourth |
| `docs/project-management/change-log.md` | New entry **C-P3.1-K** with every required field |
| `docs/project-management/decision-register.md` | OD-44 addendum, fifth entry of the day; **no decision changed** |
| `docs/project-management/raid-register.md` | I-09 amended a fifth time; resolution criteria extended |

**Neither Codex review report was edited.** The history of the earlier failed
approaches is preserved verbatim in every one of these documents; each amendment
is additive and dated.

`docs/operations/web-portal.md` was checked and **not** changed: its §4.3 text
describes refusal and absolute-bound behaviour, none of which this correction
touches.

---

## 6. Regression tests, mapped one-to-one to every requirement

All in `tests/web/test_session_policy_numeric_validation.py`. Every case goes
through a real boundary — `SessionSettings(...)`/`replace`, `SessionPolicy(...)`,
`SessionPolicy.derive()`, `WebSettings.from_environment()`, or the service against
real PostgreSQL. **No annotation assertion, no signature assertion, no
source-text assertion, and no private-helper test is offered in place of boundary
behaviour.**

| # | Requirement | Test(s) | Cases |
|---|---|---|---|
| 1 | `replace()`/direct `SessionPolicy` construction refuses `nan`, `inf`, `-inf`, `10.0`, a fractional float, `True`, `False` as `max_sessions_per_account` | `test_a_directly_constructed_policy_refuses_a_maximum_that_is_not_an_int` (parameterised ×7; each exercises **both** `replace()` and direct construction), `test_the_accepted_maximum_is_an_int_so_the_session_limit_comparison_is_real` | 8 |
| 2 | `derive()` refuses a genuine `SessionSettings` subclass whose inherited construction sees a valid integer and whose single later derivation read returns NaN; attribute read exactly once during derivation | `test_derivation_refuses_a_settings_subclass_that_answers_nan_after_construction` | 1 |
| 3 | The same lying shape refused for a representative wrong type on another registered field, proving the validator is shared and not special-cased to N-66 | `test_derivation_refuses_the_lying_shape_on_every_registered_field` (×4: `idle_minutes=60.0`, `emergency_idle_minutes=15.0`, `absolute_hours=True`, `emergency_absolute_minutes=nan`) | 4 |
| 4 | Every register field accepts `1` and its exact ceiling and refuses `0` and ceiling-plus-one, at the appropriate boundary, parameterised from the register | `test_every_registered_field_accepts_one_and_its_ceiling_at_settings_construction` (×6, all of `SESSION_CEILINGS`), `test_every_lifetime_field_holds_the_same_bounds_at_the_derivation_boundary` (×5, the fields the policy carries) | 11 |
| 5 | Environment loading with several invalid session variables raises one `ConfigurationError`, names every affected variable, contains no supplied value; sentinels asserted absent | `test_several_invalid_session_variables_raise_one_error_naming_all_and_echoing_none`, plus the control `test_the_same_environment_is_accepted_when_the_session_variables_are_in_register` | 2 |
| 6 | Real PostgreSQL: ten live sessions under a maximum of ten, then an eleventh, durably revokes the oldest with reason `session_limit` and creates the audit event | `test_the_eleventh_live_session_under_a_maximum_of_ten_durably_revokes_the_oldest` | 1 |
| 7 | Real PostgreSQL: a stricter accepted maximum enforces exactly that configured integer | `test_a_stricter_configured_maximum_is_enforced_exactly_and_not_a_default` | 1 |
| 8 | Existing refresh, rotation, classification, boundary, refusal, concurrency, audit and configuration tests remain green | the whole portal suite — §7 | 420 |

**Total new cases: 28.** Portal suite 392 → 420.

### 6.1 The lying subclass is honest to the reported threat

`_lying_settings()` builds a genuine subclass that **inherits**
`__post_init__` — it does not override it — and asserts so before returning:

```python
assert type(settings).__post_init__ is SessionSettings.__post_init__
assert len(reads) == 1   # inherited construction read and validated the good value
```

Bypassing `__post_init__` would reproduce a *different and weaker* defect than the
one reviewed, so it is not done. Each derivation case then asserts the read count
delta is exactly `1`, which is the "checked one value, used another" half of the
claim.

### 6.2 Requirement 4, honestly scoped

Requirement 4's **accept** half runs through real `SessionSettings` objects at
both boundaries, and at the derivation boundary the stored value is checked in the
policy's own unit — proving the validated number is the number the policy carries.

Its **refuse** half cannot use a real `SessionSettings` at the derivation
boundary, because one holding `0` or ceiling-plus-one is no longer constructible.
It uses the lying subclass, which is the same route the finding used, and is the
only honest way to present that gate with an out-of-register value.

`oauth_transaction_minutes` is in the register and on `SessionSettings` but is not
carried by `SessionPolicy`, so its boundary is settings construction only. That is
stated in the test module rather than silently skipped.

### 6.3 Order-independence and leak safety

No test in the new module patches a module global, monkeypatches a table, drops a
constraint, or mutates shared state. There is no temporary production
table/constraint patch in this remediation, so no rollback/restoration discipline
is invoked — and none is claimed. The two database cases use the suite's existing
autouse `clean_portal_tables` fixture and assert their outcomes from **fresh
connections after commit**, so what is proved is durable state rather than a
returned value. Requirement 7 builds a second `WebComposition` on the same
disposable engine and disposes of nothing the session-scoped fixture owns.

### 6.4 Falsification: these tests fail against the reviewed implementation

Claiming a test "would have failed before" is worthless unless run. It was run,
**without editing any file in the worktree**: a pytest plugin held only in the
session scratchpad replaced `application.web.sessions._validate_policy_values`
in memory with the reviewed two-ordering-comparison form, leaving
`SessionSettings.__post_init__` as it is — which is exactly the divergence that
was the defect.

```text
$ … pytest tests/web/test_session_policy_numeric_validation.py -q -p reviewed_implementation_plugin
F..FFF..FFFFF...............
9 failed, 19 passed in 1.20s
```

The nine failures:

```text
test_a_directly_constructed_policy_refuses_a_maximum_that_is_not_an_int[nan]
test_a_directly_constructed_policy_refuses_a_maximum_that_is_not_an_int[integral-float]
test_a_directly_constructed_policy_refuses_a_maximum_that_is_not_an_int[fractional-float]
test_a_directly_constructed_policy_refuses_a_maximum_that_is_not_an_int[True]
test_derivation_refuses_a_settings_subclass_that_answers_nan_after_construction
test_derivation_refuses_the_lying_shape_on_every_registered_field[idle_minutes-integral-float]
test_derivation_refuses_the_lying_shape_on_every_registered_field[emergency_idle-integral-float]
test_derivation_refuses_the_lying_shape_on_every_registered_field[absolute_hours-bool]
test_derivation_refuses_the_lying_shape_on_every_registered_field[emergency_absolute-nan]
```

And, in the same run, the **entire pre-existing session-lifetime suite stayed
green**:

```text
$ … pytest tests/web/test_session_touch_lifetime.py -q -p reviewed_implementation_plugin
54 passed in 1.63s
```

That is the review's point demonstrated rather than accepted on authority: the 54
passing tests Codex was shown contained no counterexample.

**Which cases do *not* discriminate, stated rather than glossed.** `-inf` and
`False` are refused by the old validator too (both are `< 1`), and requirement
4's bounds cases were already enforced by the ordering comparisons; they are
completeness, not counterexamples. Requirements 6 and 7 also pass against the old
code, because the composition's configured maximum is a real `int` — they are
**non-regression** evidence that the reviews explicitly asked for (S1's fourth
required item), not proof of the fix. The `emergency_absolute-nan` case fails
under the old code with `cannot convert float NaN to integer` from `timedelta`
rather than with the register's message; it detects the defect, but by a weaker
route than the maximum does, and is offered on that basis.

---

## 7. Verification

Every command below was run **after** the final edit, in the order the prompt
requires, on this worktree. **No result is recycled from an earlier submission.**

**Disposable database target evidence.**
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` — a Unix-domain socket to
the disposable test database, which is the only target the repository's guards
permit.

```text
$ psql -Atc "select current_database(), inet_server_addr() is null" freedom_test
freedom_test|t
```

`tests/conftest.py`'s `assert_disposable_target` / `verify_connected_unix_socket_target`
guards were active throughout. No production database, no `freedom_dev`, no
non-test target, no live service, no real credential and no player data was
contacted.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_policy_numeric_validation.py -q -k "not eleventh and not stricter"` | **26 passed**, 0 failed, 0 skipped, 2 deselected, 0 warnings |
| 2 | `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_policy_numeric_validation.py -q -k "eleventh or stricter"` | **2 passed**, 0 failed, 0 skipped, 26 deselected, 0 warnings |
| 3 | `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_session_policy_numeric_validation.py tests/web/test_session_touch_lifetime.py tests/web/test_session_rotation_lifetime.py tests/web/test_session_rotation_integrity.py tests/web/test_sessions.py tests/web/test_structural_guards.py -q` | **162 passed**, 0 failed, 0 skipped, 1 warning |
| 4 | `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web -q` | **420 passed**, 0 failed, **0 skipped**, 14 warnings, 23.7 s |
| 5 | `TEST_DATABASE_URL=… ./venv/bin/python -m pytest tests -q` | **2260 passed**, 0 failed, 0 skipped, 1 warning, 131.1 s |
| 6 | `./venv-web/bin/python -m compileall -q adapters application tests tools` | Clean |
| 6 | `./venv/bin/python -m compileall -q models helpers ext main.py config.py` | Clean |
| 7 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | `No new upgrade operations detected.` One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| 8 | `git diff --check` | Clean — no whitespace errors |
| 9 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 `OK`, 0 non-`OK`** |

Also run, and reported in §6.4: the falsification harness (9 failed / 19 passed
on the new module; 54 passed on the pre-existing lifetime module).

**Portal suite count: 392 → 420**, the 28 new cases. **No test was removed,
skipped, weakened or replaced**, and no assertion was relaxed to make a suite
green. Bot suite unchanged at 2260.

**Warnings.** The portal suite's 14 are the pre-existing `httpx`
per-request-cookie `DeprecationWarning`s in `test_sessions.py`,
`test_oauth_completion_binding.py` and `test_oauth_flow.py`. The bot suite's single
warning is `audioop` deprecation from `discord/player.py`. None is new, and none
originates in the changed code. The new module emits none.

**Formatter, linter and type checker: none is configured in this repository.**
Re-checked for this submission rather than restated — there is no
`pyproject.toml`, `setup.cfg`, `.flake8`, `.ruff.toml`, `mypy.ini`, `tox.ini` or
`.pre-commit-config.yaml`, and neither `requirements-dev.txt` nor
`requirements-web-dev.txt` lists one. **No command was invented.** `compileall`
under both interpreters is the available static check and it was run.

**Mutation testing was not run for this remediation, and none is claimed.** The
falsification run in §6.4 is the direct evidence that the new tests discriminate;
mutation is a reasonable reviewer request and is not pre-empted with a partial
matrix.

**Deliberately not run, and not claimed.** Every staging-class, browser-class,
real-device-class, external-service and direct-HTTP check. Staging does not exist
(RAID I-06). No P3.1 HTTP route calls `touch()`, and none creates a session
through a browser, so there is no request path to exercise for this correction.
OD-45's direct-HTTP portions remain mandatory blocking evidence at P3.G2 and are
**not** waived here. No network probe, no scanner and no external security service
was used.

---

## 8. Security impact

**Strictly a tightening. No control was relaxed.**

- **N-66 is restored.** The accepted per-account live-session bound is enforced
  again, and is now enforced against *how the number is built* rather than only
  against how it is compared. The security consequence S1 identified — an
  unbounded population of live credentials for one account, so a stolen or
  forgotten session need never be displaced — is closed. Requirement 6 proves the
  eleventh session durably revokes the oldest with reason `session_limit` and
  writes the corresponding audit event; requirement 7 proves a **stricter**
  configured maximum is the one enforced, so the control is the operator's number
  and not a default that happened to hold.
- **The auditability half is preserved.** The revocation is recorded as
  `auth.session.revoked` with the session's id and `{"reason": "session_limit",
  "limit": <maximum>}` — which is what lets an account holder who never used
  eleven browsers notice.
- **The failure mode was silent, which is why the type rule matters.** A NaN
  maximum raised nothing, logged nothing and produced no refusal; the control
  simply stopped acting. Refusing at construction converts a silent loss of
  control into a loud one.
- **No new attack surface.** No route, no variable, no dependency, no credential
  scope and no privilege was added or widened.

---

## 9. Confirmation that the established controls did not regress

Each was re-checked against the code and is covered by the suites in §7 (items 3
and 4), all green:

| Control | Status |
|---|---|
| `SessionRepository.touch(session_id, *, now)` accepts no caller-supplied method, duration, policy or bounds | **Unchanged.** Signature assertions and behavioural repository-only cases in `test_session_touch_lifetime.py` pass |
| The persisted row's `auth_method` selects its idle window | **Unchanged** |
| Unclassified methods fail closed and visibly | **Unchanged** — `UnclassifiedAuthMethod` at import and at repository construction |
| Refresh is one conditional `UPDATE` with strict idle and absolute liveness predicates | **Unchanged** |
| Refreshed idle expiry clamped to the original absolute expiry | **Unchanged** |
| `absolute_expires_at` absent from the touch `SET` clause | **Unchanged** |
| Zero updated rows becomes `SessionTouchRefused` at the service boundary | **Unchanged** |
| Repository and service constructors regain no independently injectable policy source | **Unchanged** — `SessionService.__init__` still takes `(sessions, token_grants, audit)` |
| Repository and service share the same derived policy instance | **Unchanged** — `service.policy is repository.policy` still asserted with `is` |
| Caller-owned transaction and audit behaviour | **Unchanged** |
| N-66 effective: the eleventh live session revokes the oldest and audits it before creating the new session | **Restored and proved twice** — TC-SESS-08 (pre-existing) and TC-SESS-08b (new) |

**No schema or migration change was expected, and none was made.** Revisions
0006–0009 were not edited. `alembic check` reports no new upgrade operations. No
case arose in which a migration appeared necessary.

---

## 10. Configuration, deployment, database, migration and rollback impact

- **Configuration.** **No variable added, renamed or removed; no accepted value
  changed.** `.env.example` needs no edit. `WEB_MAX_SESSIONS_PER_ACCOUNT` and its
  five siblings keep their names, ceilings and defaults. The only
  operator-visible behaviour is unchanged from the previous package: an
  out-of-range value is refused at startup, naming the variable and never the
  value.
- **Deployment.** No change. No new dependency, no systemd unit change, no
  runtime-grant change, no proxy change, no lockfile change.
- **Database and migration.** **None.** The defect and its correction are entirely
  in runtime validation. No table, column, constraint, index or grant changed.
- **Rollback.** Unaffected. Reverting the changed files restores the previous
  behaviour with no data implication, because nothing persisted changed shape or
  meaning. There is no forward data migration to undo.

---

## 11. Complete accounting for the pre-existing dirty worktree

Branch: `docs/platform-plan`. `git status --short` recorded **before** any edit
listed **62 entries** of intentional uncommitted Phase 3 work. **All unrelated
work was preserved. Nothing was staged, committed, pushed, stashed, reverted or
rewritten; no secret was read or modified; no live service was contacted; no
non-test database was used.**

After this remediation the count is **63**, and the single added line is

```text
?? docs/review/phase-3-p3-1-od-44-session-policy-numeric-validation-remediation-submission.md
```

Every other file this remediation touched is either an already-modified tracked
file or lives inside an already-untracked directory (`tests/web/`,
`docs/contracts/`), so it produces no new status line. Nothing appears in the
staged column.

**Changed by this remediation:**

- `tests/web/test_session_policy_numeric_validation.py` — **new**, inside the
  untracked `tests/web/` tree
- `docs/contracts/phase-3-numeric-policy-register.md`,
  `docs/contracts/phase-3-logical-schema.md`,
  `docs/contracts/phase-3-test-traceability.md` — inside the untracked
  `docs/contracts/` tree; **appended to**
- `docs/project-management/status.md`, `change-log.md`, `decision-register.md`,
  `raid-register.md` — tracked, already modified, **appended to only**
- `docs/review/phase-3-p3-1-od-44-session-policy-numeric-validation-remediation-submission.md`
  — **new**

**Inspected and deliberately left unchanged** (see §5.1):
`application/web/config.py`, `application/web/sessions.py`,
`adapters/web/repositories.py`, `adapters/web/composition.py`,
`tools/session_revoke.py`.

**Pre-existing and untouched by this remediation:** everything else in
`git status` — `.env.example`, `.gitignore`, `adapters/database/*`,
`application/audit.py`, `docs/adr/*`, `docs/discovery/open-decisions.md`,
`docs/review/Handover information`, `docs/review/phase-3-delivery-plan.md` and
every other `docs/review/` record including **both Codex review reports**,
`infra/postgresql/*`, `migrations/versions/0006–0009`, `pytest.ini`,
`requirements*`, `tests/conftest.py`, `tests/web_fixtures.py`, the other
`tests/web/*` modules, the other `tests/*` modules, `tools/*` and
`docs/operations/web-portal.md`. All were already present when this task began.

One temporary artefact was created **outside the worktree**, in the session
scratchpad, and no copy of it is in the repository: the falsification plugin
described in §6.4.

---

## 12. Unresolved risks and concrete reviewer focus

**Stated without minimising.**

1. **I did not write the implementation under review here.** It was present in
   the worktree when this task began, and my contribution is inspection,
   falsification, the regression suite and the documentation. A re-reviewer should
   weigh §5.1 accordingly and should independently satisfy themselves that no
   correction was needed, rather than taking my judgement that none was.
2. **`SessionPolicy` remains a public, nameable frozen dataclass.** It is derived
   and never accepted, and its `__post_init__` validates the register, but a
   reviewer should decide whether "derived, never accepted" is a strong enough
   boundary or whether the type should become module-private. Carried forward
   unchanged from the previous submission, because it is unchanged.
3. **The other `WebSettings` sub-dataclasses have not been audited for the same
   shape.** `RateLimitSettings`, `BoundsSettings`, `WorkerSettings`,
   `WebAuthnSettings` and `DatabasePoolSettings` carry accepted numeric policies
   (N-18, N-21, N-23, N-31…N-33, N-41…N-45, N-53) and, unlike `SessionSettings`,
   have **no** construction-time validation at all — their bounds are enforced by
   the environment reader only. That is the F1 shape from the previous package,
   surviving in five other types. It is out of this remediation's narrow scope and
   is reported as a **known gap**, not as complete work. It is the single most
   valuable thing a reviewer could ask to be scheduled next.
4. **`touch()` is still unreachable from any P3.1 HTTP route.** This correction is
   proven at the service and repository boundary and against real PostgreSQL, not
   in request handling. The P3.2 package that wires it **must** treat
   `SessionTouchRefused` and `SessionRotationRefused` as end-the-session outcomes
   — clear the cookie, treat the request as unauthenticated — and never as
   retries.
5. **Mutation testing was not run** (§7).
6. **This is the fifth correction of the same authority in one day.** The pattern
   in each previous failure was reasoning from the absence of one entry point. The
   pattern in *this* one was different and worth naming: two gates that agreed on
   the bounds and silently disagreed on the type. Both are the same underlying
   error — a rule with more than one definition.

**Requested reviewer focus, concretely:**

- attempt to reach `_enforce_session_limit` with a `max_sessions_per_account` that
  is not an `int`, by **any** route: `SessionSettings` construction and
  `dataclasses.replace`, subclassing `SessionSettings` (properties,
  `__getattribute__`, `__getattr__`, descriptors, metaclasses), `SessionPolicy`
  construction and `replace`, subclassing `SessionPolicy`,
  `SessionRepository.__init__`, `SessionService.__init__`,
  `WebComposition.services()`, `tools/session_revoke.py`, and the environment
  reader;
- check that the value validated in `derive()` is provably the value stored — the
  claim in §4.3 point (7) — including under a `SessionSettings` subclass whose
  attribute is a descriptor rather than a `__getattribute__` override;
- check whether `session_policy_problem`'s "first problem only" behaviour can hide
  a second problem an operator needs;
- confirm the register's new type paragraph matches the code, since the register
  is the authority and the code mirrors it; and
- decide whether risk 3 — the five unvalidated settings types — should block
  P3.G1 or be scheduled as its own package.

---

## 13. Stop condition and gate statement

All changes are left **unstaged and uncommitted**.

Passing tests are **evidence, not review acceptance**. Nothing in this document
accepts, closes or waives anything, and the 420/2260 green results above are
offered as the input to a review rather than as its outcome.

**P3.G1 remains open**, pending fresh independent implementation and
security-focused re-reviews and maintainer acceptance. **P3.2 has not started, and
no part of it is claimed.** RAID I-09 is amended, not closed.
