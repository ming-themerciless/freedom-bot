# Phase 3 P3.1 — N-23 exact worker lease remediation

**Date:** 2026-08-15 · **Package:** P3.1 · **Owner:** Claude (implementing
Technical Lead) · **Change record:** C-P3.1-M · **Corrects:** C-P3.1-L and
[`phase-3-p3-1-settings-construction-validation-remediation-submission.md`](phase-3-p3-1-settings-construction-validation-remediation-submission.md)

**Status: submitted for review. Nothing here is accepted.** P3.G1 remains open
pending fresh independent implementation and distinct security-focused
re-reviews, an availability review of the pool and worker bounds, and maintainer
acceptance. **RAID I-09 and I-10 are both still open.** **P3.2 and P3.3 have not
started** — no worker behaviour, no route and no service was written. Passing
tests are evidence, not acceptance.

---

## 1. The corrected result, first

`WorkerSettings.lease_seconds` now accepts exactly the built-in integer `60`.

```python
# application/web/config.py — the one runtime N-23 lease definition
"lease_seconds": PolicyBound(minimum=60, maximum=60, policy="N-23"),
```

`heartbeat_seconds` is **unchanged** at an exact built-in `int` in 1…20. No
second copy of 60 was created: the reader, the constructor and the tests all read
this one entry, and no ordering rule between the lease and the heartbeat — or
involving N-45 — was added.

The change is one `PolicyBound`, its explanatory comment, twenty test cases and
the descriptions that were inaccurate. It is a correction to the implementation
and to what was written about it, **not a new baseline decision**.

---

## 2. Root cause, and why N-23 already resolves the apparent ordering problem

### 2.1 What was wrong

C-P3.1-L defined the entry as:

```python
"lease_seconds": PolicyBound(minimum=1, maximum=60, policy="N-23"),
```

That treats 60 as a **ceiling** and accepts every exact built-in integer from 1
through 60 as a job lease. The accepted register row does not say "at most 60
seconds":

```text
N-23 | Job lease | 60 seconds, heartbeat at most every 20 seconds
```

One sentence, two different kinds of number. The lease is given as a **value**;
the heartbeat interval is given as a **maximum**. Reading both halves as ceilings
is what produced the defect.

### 2.2 Why 60 is a value, on the accepted documents' own terms

| Accepted document | What it states |
|---|---|
| `docs/contracts/phase-3-state-machines.md` SM-05 | the `running → running` heartbeat transition writes `lease_expires_at = now() + 60s` |
| `docs/contracts/phase-3-logical-schema.md` | the job claim and lease-renewal statements write the same 60; §10.1's recovery reasoning is `N-23 + N-44` = 60 s + 15 s |
| `docs/contracts/phase-3-operational-contract.md` | the reaper's liveness signal ("should never exceed `N-23 + N-44`") and the wedged-worker procedure ("the lease expires within N-23") are both calculated from a 60-second lease |
| `docs/contracts/phase-3-numeric-policy-register.md` N-44 | "every 15 seconds — **three checks inside one 60-second lease**" |

A one-second lease is therefore not a tightening of N-23. It contradicts SM-05's
renewal, invalidates the recovery bound every operational threshold is derived
from, and — with a heartbeat accepted up to every 20 seconds — would lose a live
claim between beats, handing running work to the reaper.

### 2.3 Why the ordering question is withdrawn rather than answered

C-P3.1-L raised an open maintainer question: whether
`heartbeat_seconds < lease_seconds` should be added to the accepted contract. Its
evidence was that `lease_seconds=1, heartbeat_seconds=20` was "inside the register
as written and operationally nonsensical".

It was not inside the register. It was inside the **implementation**, and it
existed only because the implementation had broadened N-23. The register states
one lease: 60 seconds.

With the lease corrected to exactly 60:

- every accepted heartbeat (1…20) is already far shorter than every accepted
  lease (exactly 60), so an ordering rule would refuse nothing that is not
  already refused;
- **no ordering rule was added, and none is needed**;
- **no relationship involving N-45 has been accepted**, and none was invented —
  a 300-second attempt timeout against a 60-second lease remains an unstated
  relationship, deliberately not enforced;
- **nothing about N-23 blocks P3.3.** What P3.3 still owns is the *consumer*
  evidence for the worker's lease, heartbeat, attempt, timeout and queue bounds,
  which is a different obligation and is unchanged.

`PolicyBound` already had the exact-value shape this needs, because N-41's
`concurrency` and N-34's `trusted_proxy_hops` use it: `is_exact` is
`maximum == minimum`, `default` is the accepted value, `requirement()` renders
"must be exactly 60 (N-23)." with no supplied value in it, and `refusal_for()`
tags **both** directions `S-10`, because neither side of an exact value is a
tightening. No mechanism was added; the right one was selected.

---

## 3. Exact files changed

| File | Change |
|---|---|
| `application/web/config.py` | `WORKER_BOUNDS["lease_seconds"]` becomes `PolicyBound(minimum=60, maximum=60, policy="N-23")`; the table comment is rewritten to state why N-23 yields one exact value and one ceiling, and to record that no lease/heartbeat ordering is needed. **Nothing else in the module changed** — no second validator, constructor branch, environment reader, consumer or helper restates 60 |
| `tests/web/test_settings_construction_validation.py` | New module section 3.1 (20 cases) and three corrections to existing cases; see §4 |
| `docs/contracts/phase-3-numeric-policy-register.md` | New dated section "N-23's lease is a value, not a ceiling", plus a block-quoted correction attached to the settings-construction commentary that claimed only two entries were not plain ceilings. **The accepted N-23 row in §7 is untouched** |
| `docs/contracts/phase-3-configuration-and-dependency-contract.md` | New dated section on `WORKER_LEASE_SECONDS`. No variable added, renamed or removed; §2.2's Worker table and §2.3's fifteen refusals untouched |
| `docs/contracts/phase-3-test-traceability.md` | Amendment note (explicitly *not* addition-only — it corrects two clauses the previous amendment introduced); TC-STRUCT-07 and TC-LIM-06 corrected. No row removed |
| `docs/review/phase-3-p3-1-settings-construction-validation-remediation-submission.md` | New §0 correction banner; §3.1's `1…60` row and the "three entries are not plain ceilings" paragraph corrected; §3.3's relationship row corrected; §7.2 gains an N-23 row and its case count is annotated; §9.1 struck and rewritten as withdrawn; §13.3's request for a decision struck and replaced |
| `docs/project-management/raid-register.md` | I-10 amended by **appending** a dated correction to its status cell; the previous text is preserved. **I-10 left open** |
| `docs/project-management/status.md` | Seventh 2026-08-15 update **appended above** the sixth, which is preserved unchanged; the status-date line updated |
| `docs/project-management/change-log.md` | **C-P3.1-M appended.** C-P3.1-L is preserved verbatim |

**Not changed, deliberately:** N-23 itself, `phase-3-state-machines.md`,
`phase-3-logical-schema.md`, `phase-3-operational-contract.md`,
`phase-3-delivery-plan.md`, `.env.example` (it already ships
`WORKER_LEASE_SECONDS=60`), every migration, every route, every service, every
adapter, `infra/`, `requirements*`, and every operations document. No worker
execution was implemented to test this setting.

---

## 4. Tests — added, corrected, and why they discriminate

The module parameterises from `WORKER_BOUNDS` throughout, so no test restates a
policy number. The one deliberate exception is named below and exists to bind the
runtime table to the accepted row; a binding expressed in terms of the thing it
binds would assert nothing.

### 4.1 New — module section 3.1, "N-23's lease is one value, not a range" (20 cases)

| Case | What it proves | Fails against `1…60`? |
|---|---|---|
| `test_the_accepted_n_23_lease_value_is_sixty_seconds` | 60 constructs and is carried; 59 and 61 are refused. **The one place the accepted number is written outside the register** | **Yes** |
| `test_the_lease_is_registered_as_an_exact_value_and_behaves_as_one` | `default ± 1` are both refused, and the message says *exactly* and cites N-23 | **Yes** |
| `test_a_lease_that_is_not_the_accepted_value_is_refused` ×6 | 0, −1, −60, **1** (the old floor), **20** (the heartbeat maximum) and 86 400 are refused | **Yes** for `1` and `20` |
| `test_only_an_exact_built_in_int_is_an_acceptable_lease` | `60.0`, `60.5`, NaN, ±inf, `True`, `False` and `LyingInt(60)` are refused with a type message, each carrying the accepted number so range is never what refuses it | No — non-regression |
| `test_replacing_the_lease_on_a_valid_worker_refuses_at_construction` ×3 | `dataclasses.replace()` refuses 59, 61 and the comparison-overriding subclass | **Yes** for 59 |
| `test_the_previously_documented_counterexample_no_longer_constructs` | `lease_seconds=1, heartbeat_seconds=20` halts at `WorkerSettings`, **and the refusal names only the lease** — so no ordering rule is implied | **Yes** |
| `test_the_accepted_heartbeat_boundaries_are_unchanged` | 1 and 20 accepted, 0 and 21 refused, with the lease still at its accepted value | No — non-regression, and that is the point |
| `test_a_worker_whose_lease_lies_on_a_later_read_is_refused_by_canonicalisation` | a genuine subclass that passes its inherited construction gate and lies on the next read is refused by `canonical_settings`, **read exactly once**; a valid object is rebuilt as the exact base type | **Yes** |
| `test_the_environment_accepts_an_unset_lease_as_the_registered_value` | an unset `WORKER_LEASE_SECONDS` yields the register-derived exact value, as an exact `int` | No — non-regression |
| `test_the_environment_accepts_the_accepted_lease_written_out` | the explicit string `"60"` — what `.env.example` ships — still starts | No — non-regression |
| `test_the_environment_refuses_a_lease_either_side_of_the_accepted_sixty` ×2 | `"59"` and `"61"` refuse with `S-10`, the variable **named**, the supplied value **absent**, and the wording stating *exactly* and citing N-23 | **Yes** (both: 59 was accepted; 61's wording was a range) |
| `test_an_invalid_lease_still_aggregates_with_other_types` | a 59 lease plus two sentinel-valued variables from two other settings types produce **one** `ConfigurationError` with ≥3 problems, no sentinel echoed, and no `ValueError` escaping a constructor | **Yes** |

Every case is a behaviour test. None asserts source text, an annotation or a
signature.

### 4.2 Corrected existing cases

| Case | Correction |
|---|---|
| `test_both_accepted_boundaries_are_carried_exactly` | An entry whose register bounds are **equal** is now exercised as the one accepted value it is, instead of running the same number twice under the names of two boundaries. This affects `concurrency` (N-41), `trusted_proxy_hops` (N-34) and now `lease_seconds` (N-23). The "either side is refused" half is where it belongs, in the refusal case |
| `test_a_stricter_accepted_value_is_preserved_and_not_replaced_by_a_default` | Its worker representative was `WORKER_LEASE_SECONDS="30"`, which is now refused. It is `WORKER_HEARTBEAT_SECONDS="10"` — the half of N-23 that *is* a maximum, and therefore the honest worker case for "a stricter accepted value survives". The refused 30-second lease is covered by the environment case above |
| `test_no_relationship_is_invented_between_the_worker_or_membership_bounds` | Its worker example was the withdrawn counterexample. It is now N-45's 300-second attempt timeout against the 60-second lease — a genuinely unstated relationship that is genuinely not enforced. The membership half is unchanged |

`test_a_number_outside_the_register_is_refused` and
`test_only_an_exact_built_in_int_is_accepted` needed no edit: they derive from the
register, so the lease's refused neighbours became 59 and 61 automatically.

---

## 5. Falsification, and proof the worktree was restored

**This is falsification of the previous implementation, not mutation testing. No
mutation tool is configured in this repository and none was run.**

A pytest plugin held **outside** the worktree restores only the reviewed entry,
in memory, before the test modules are imported:

```python
old_worker["lease_seconds"] = web_config.PolicyBound(minimum=1, maximum=60, policy="N-23")
```

Nothing else is touched — no file is written, no source is edited, no other bound
is altered.

```
PYTHONPATH=<scratchpad> TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv-web/bin/python -m pytest tests/web -q -p falsify_lease_1_to_60
→ 10 failed, 597 passed, 14 warnings in 22.65 s
```

The ten failures are exactly the discriminating cases marked **Yes** in §4.1:

```
test_the_accepted_n_23_lease_value_is_sixty_seconds
test_the_lease_is_registered_as_an_exact_value_and_behaves_as_one
test_a_lease_that_is_not_the_accepted_value_is_refused[the-old-floor]
test_a_lease_that_is_not_the_accepted_value_is_refused[the-heartbeat-maximum]
test_replacing_the_lease_on_a_valid_worker_refuses_at_construction[one-second-short]
test_the_previously_documented_counterexample_no_longer_constructs
test_a_worker_whose_lease_lies_on_a_later_read_is_refused_by_canonicalisation
test_the_environment_refuses_a_lease_either_side_of_the_accepted_sixty[fifty-nine]
test_the_environment_refuses_a_lease_either_side_of_the_accepted_sixty[sixty-one]
test_an_invalid_lease_still_aggregates_with_other_types
```

**Every other portal test stays green**, including all 145 cases the previous
package delivered: the pre-existing suite contained no counterexample for this
defect either. The ten non-discriminating new cases are non-regression evidence
and are labelled as such in §4.1 rather than counted as discrimination.

**State restored.** `git status --short` was captured immediately before and
immediately after the falsification run and is byte-identical (65 entries). No
tracked file changed; the plugin lives in the session scratchpad, not in the
repository, and no cache or monkeypatch was left behind.

---

## 6. Verification — fresh results, in the required order

All runs are from after the final edit. Nothing is recycled.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest tests/web/test_settings_construction_validation.py -q -k "lease or heartbeat or counterexample"` | **26 passed, 139 deselected** |
| 2 | `… -m pytest tests/web/test_settings_construction_validation.py -q` | **165 passed** (145 before this change) |
| 3 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest tests/web -q` | **607 passed, 0 failed, 0 skipped**, 14 warnings |
| 4 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest -q` | **2260 passed, 0 failed, 0 skipped**, 1 warning |
| 5 | `./venv/bin/python -m compileall -q application adapters tools tests` and the same under `./venv-web/bin/python` | Both **OK**; both interpreters are CPython 3.12.3 |
| 6 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | **`No new upgrade operations detected.`** One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| 7 | `git diff --check` | **Clean**, exit 0 |
| 8 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 `OK`, 0 non-`OK`** |
| 9 | Formatter / linter / type checker | **None configured** — see below |
| 10 | Falsification (§5) | **10 failed, 597 passed**; worktree byte-identical before and after |

**Zero skips is the reported output, not an assumption.** Both suite runs printed
their totals with no `skipped` term; the `0 skipped` above is that output.

**Database target.** Every database run used
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`, the guarded disposable
target under RAID A-02. **`TEST_DATABASE_URL` was set for every run**, so no
PostgreSQL case is reported as passing when it in fact skipped. No other database
was contacted; no live Discord, Foundry or external service was contacted.

**Formatter, linter and type checker: none configured, established by
inspection.** No `pyproject.toml`, `setup.cfg`, `.ruff.toml`, `.flake8`,
`mypy.ini`, `tox.ini` or pre-commit configuration exists at the repository root,
and neither `venv/bin` nor `venv-web/bin` contains `ruff`, `mypy`, `flake8`,
`black`, `pylint` or `isort`. Compilation under both configured interpreters was
run instead.

**Warnings.** The 14 portal warnings are the pre-existing `httpx` per-request
cookie `DeprecationWarning`s; the bot suite's single warning is the pre-existing
`audioop` deprecation from `discord.player`. Neither is new and neither relates to
this change.

**Checks that could not be run.** No browser, staging, device or live-service
check was run, and none is possible: staging does not exist (RAID I-06) and this
change has no rendered surface. No mutation testing (§5). No worker consumer
evidence — implementing worker execution to test this setting would start P3.3,
which has not been authorised.

---

## 7. Documentation and history corrections

Every statement introduced by the settings-construction remediation that said or
implied one of the five errors named in the review was located and corrected:

| Claim | Where it appeared | Correction |
|---|---|---|
| N-23's lease is `1…60` | `config.py` comment; submission §3.1 table; RAID I-10 | Corrected to an exact 60, with the reason, in each place |
| Every worker number is a ceiling with a floor of one | `config.py` comment; submission §3.1 prose ("three entries are not plain ceilings") | Corrected: **four** entries are not plain ceilings, and `concurrency` never was one either |
| `lease_seconds=1, heartbeat_seconds=20` is inside the accepted register | submission §3.3 and §9.1; test docstring; RAID I-10; status | Corrected everywhere; the pair is now proved refused, for its lease |
| An additional heartbeat-less-than-lease decision is required | submission §9.1 and §13.3; register commentary; RAID I-10; status; change log C-P3.1-L | **Withdrawn** as raised on a false premise, in each place, with the reason |
| The N-23 ordering question blocks P3.3 | submission §9.1; RAID I-10; status | Corrected: it does not. P3.3 owns the worker **consumers**, which is a different and unchanged obligation |

**The accepted documents were not rewritten to match the buggy code.** The N-23
row, SM-05, the logical schema and the operational calculations remain 60 seconds
and remain the authority.

**Append-only management history is preserved.** The RAID register's I-10 cell is
**appended to**, keeping the previous text intact; `status.md` gains a seventh
dated update **above** the sixth, which is unchanged; `change-log.md` gains
C-P3.1-M and leaves C-P3.1-L verbatim. The two contract documents gain new dated
sections, and the numeric register's earlier commentary carries a block-quoted
correction rather than an edit. The earlier submission — a review artefact rather
than a management ledger — carries a §0 correction banner and inline markers at
each affected statement, so a reviewer reading it in order cannot act on the old
claim.

It is stated plainly, in each of those places, that the independent review found
the earlier `1…60` interpretation wrong.

---

## 8. Security and availability implications

- **Security.** A tightening, and a small one. `WORKER_LEASE_SECONDS` gains two
  refusals (59 and 61, and everything else that is not 60) and loses none. The
  refusal remains redacted: the variable is named, the supplied value never
  appears, and `PolicyBound.requirement()` cannot echo one because it is never
  given one. No authorization, session, rate-limit, WebAuthn or audit behaviour
  is touched. No control was relaxed and no authority widened.
- **Availability.** An improvement, and the reason this finding matters. Under
  the previous entry a deployment could configure a lease shorter than the
  heartbeat interval it also configured, so a healthy worker's claim would expire
  between beats and the reaper would requeue live work — duplicated execution,
  and `attempts` consumed against N-43's cap of three. That is now
  unconstructible. The failure mode is a **startup refusal**, not a request-time
  degradation: a misconfigured process does not start rather than misbehaving
  under load. No previously *accepted* deployment becomes invalid, because the
  accepted lease was always 60 and `.env.example` already ships it.
- **What is not claimed.** No exploit, no environment-string bypass and no
  production impact is claimed. P3.1 reads only `enabled` (S-11) and
  `artifact_root` (S-12) from `WorkerSettings`; the lease has no runtime consumer
  yet, which is precisely why fixing it now — before P3.3 activates it — is the
  cheap moment.

---

## 9. Unchanged configuration, deployment, migration and rollback facts

- **Configuration.** No variable added, renamed or removed. No accepted value
  changed. `.env.example` is **unchanged** and already contained
  `WORKER_LEASE_SECONDS=60`. An unset variable still means the accepted value.
- **Deployment.** No systemd unit, topology, port, path, credential or
  runtime-grant change. No operator procedure changed, so no operations document
  was edited.
- **Schema and migration.** None. Migrations 0006–0009 were not touched; the
  correction is entirely in runtime validation.
- **Rollback.** Reverting `application/web/config.py` restores the previous
  behaviour exactly. Nothing persisted changed shape or meaning, and no data
  written under this change differs from data written before it.
- **Secrets.** No secret was read, printed, committed or modified. `.env`,
  `yt-cookies.txt` and every credential file were left alone. The final diff was
  reviewed for secrets, generated files, unrelated edits, policy restatements and
  accidental changes to accepted contracts; none was found.

---

## 10. Remaining honest gaps, and review focus

Unchanged and still true:

- the worker's lease, heartbeat, attempt, timeout and queue **consumers** are
  P3.3's — the claim statement, the heartbeat, the reaper and the attempt cap.
  None was implemented here;
- **no new relationship involving N-45 has been accepted**, and none was added;
- `WEB_WEBAUTHN_USER_VERIFICATION` and `WEB_RECOVERY_GRANT_MINUTES` are validated
  but have no runtime consumer, as previously documented;
- N-09/N-10 have no P3.1 route consumer, and N-21/N-22 have none at all;
- **P3.G1 and RAID I-09/I-10 remain open**, pending the required independent,
  security-focused and availability-focused reviews and maintainer acceptance.

**Neither deliverable, I-10, P3.1, P3.G1 nor any review gate is accepted or
closed, and none is described as such merely because tests pass.**

Suggested reviewer focus:

1. **Confirm the exact 60 against the accepted sources** — SM-05's
   `now() + 60s`, the schema's claim and renewal statements, and the
   `N-23 + N-44` recovery calculation. If any of them is read differently, this
   is the finding to raise.
2. **Confirm 60 is written once.** Search for any second occurrence outside
   `WORKER_BOUNDS` — a validator, a constructor branch, an environment reader, a
   consumer, a test helper. There should be exactly one deliberate exception, the
   register-to-row binding case named in §4.1.
3. **Confirm no ordering rule crept in.** `WorkerSettings.__post_init__` should
   contain no comparison between the lease, the heartbeat and the attempt
   timeout.
4. **Confirm the redaction.** A refused `WORKER_LEASE_SECONDS` must name the
   variable and never its value, and must aggregate rather than raise.
5. **Confirm the availability judgement** in §8 — in particular that a startup
   refusal is the correct failure mode for a 59- or 61-second lease.

---

## 11. Worktree state

`git status --short` reported **65 entries before this remediation and 66 after**,
the single addition being this document. Nothing was staged, committed, pushed,
stashed, reverted or rewritten.

- **Tracked files this remediation modified (3):**
  `docs/project-management/raid-register.md`,
  `docs/project-management/status.md` and
  `docs/project-management/change-log.md`. All three were **already** modified in
  the worktree before this work began and are appended to rather than rewritten,
  so each keeps its existing ` M` entry.
- **Untracked directories this remediation changed files inside:**
  `application/web/`, `docs/contracts/` and `tests/web/`. Git reports each as a
  single `??` entry, so edits inside them do not change the entry count.
- **`docs/review/phase-3-p3-1-settings-construction-validation-remediation-submission.md`**
  was already untracked and is corrected in place.
- **`docs/review/Handover information`** — the maintainer's own modification —
  was not touched, and neither was any other pre-existing entry.
- **All changes are left unstaged and uncommitted.**
