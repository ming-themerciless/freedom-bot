# Project-review remediation handback — 2026-09-09, R2

Returned to Codex. **Nothing here is closed on the implementer's authority.**
Passing tests close no package gate and authorize no operational execution.

**This is a design, test and document pass.** No production harness source
changed. The corrected C-8 mechanism is **submitted for technical review, not
accepted and not implemented**, and this submission stops at that checkpoint.

| Finding | Severity | Disposition |
|---|---|---|
| **PR-20260909-R2-1** — proposed guards omit execution-time effects | Blocking | **Conceded in full.** The whole-lifecycle ledger, the per-effect enforcement points and the execution-time guard are in the revised design. Two injected reproductions added |
| **PR-20260909-R2-2** — installed bytes not bound to verified bytes | Blocking | **Conceded in full.** The `[proved]` label and the second revision's P3 are withdrawn. A complete capture-to-recovery contract replaces them. One injected reproduction added |
| **PR-20260909-R2-3** — alternatives rest on a false equivalence | Important | **Conceded in full.** The blanket impossibility statements are withdrawn and replaced with a four-class × eight-candidate comparison. Dated errata added |
| **EH-R16-1** | Blocking | **Open**, with its existing identity. Not renumbered, not partially closed, not claimed fixed by documentation |
| Prior Finding 3 | Important | Codex recommends closure for the current working tree. The synthetic skills fixture, sanitized crafting report and production alias fix are **preserved and untouched**. §5 corrects the previous handback's history claim |

Review-input manifest digest, unchanged and **not execution approval**:
`ec1e3e70b5d24aca911df9e4dcd394361ebffdb04b9587434cb74386756f2839`.
Do not pass it to `--execute`.

---

## 1. The revised design, and its pending acceptance

**Path:**
[`docs/review/phase-5-0-evidence-harness-c8-ownership-design-r16-3.md`](phase-5-0-evidence-harness-c8-ownership-design-r16-3.md).
**Status: submitted for technical review, not accepted, not implemented.**
It supersedes `phase-5-0-evidence-harness-c8-ownership-design-r16-2.md`, which
is not accepted, which in turn superseded the rejected
`phase-5-0-evidence-harness-c8-ownership-design-r16.md`.

Its §0 cross-references every R2 finding to the sections answering it. It keeps
observations, assumptions, proof obligations, proposed acceptance decisions and
unresolved dependencies in separate, named sections, and it preserves the second
revision's two correct concessions and its permissions inventory.

### 1.1 R2-1 — the whole lifecycle, not cleanup

§3 is an operation-by-operation ledger of all 139 execution steps and 47 cleanup
steps, in five phases. Each row names the object or bytes acted on, how the
operation resolves it, the ownership claim its correctness depends on, the
enforcement point that exists today, and the one proposed. §2 fixes the
vocabulary the review required: an **observed baseline**, a **vector allowlist**,
a **held object reference** and an **exclusion boundary** are four different
things, and the design states which one each step rests on.

Two facts the ledger establishes rather than asserts:

* between the identity read in `B3-01` and the single comparison at `CL-37` the
  harness **holds no descriptor at all** — every step is a separate process and
  identity is re-derived by name;
* the executor's `_revalidate()` and `_revalidate_cleanup()` are vector-allowlist
  operations. They re-check the argument string and establish no current
  ownership of anything. The second revision's implementation table was read as
  though they did.

`G-2` generates a `statroot` guard immediately before **each** root-dependent
step, in the execution plan and in cleanup, with a plan-generation immediacy
clause. Counted against the plan the current tree generates rather than
estimated: **94 execution-side guards and 34 cleanup-side, 128 in total.** §6.5
tabulates refusal, uncertainty, residue and recovery for each substitution
situation, including the ones `G-2` does not catch. §6.3 adds the installed case
program's integrity as a prerequisite of each use rather than a single early
reading, §6.6 states the guards' own trust chain, and §6.7 keeps independently
safe recovery with its separate ownership basis stated.

**The whole-lifecycle requirement is not narrowed to cleanup**, and the review's
own example — a root replaced after `B3-01` and before the next `install -d` —
is answered as a case where no guard exists at all, not as a residual interval.

### 1.2 R2-2 — bytes, not pathnames

The unconditional `[proved]` label and the second revision's P3 are **withdrawn**.
§5 replaces them with a five-clause contract: obtain the original bytes before
the first configuration mutation; establish the on-disk copy against them;
make recoverability a **prerequisite of the materialization gate**; restore from
the held buffer, so the bytes written are the bytes checked because they are the
same object; and state what is still not proved.

`G-1` implements the contract on the **already-injected materializer** — a
bounded read side and a content-bearing write side — so it adds no case-program
verb, no privilege, no identity and no executable. The captured bytes never
enter an observation, a record or the journal; only their SHA-256 does. §6.1.4
covers destination safety, the staged-write-then-`rename` sequence that makes a
partial write impossible, interruption, restart, restoration order and
retention. §6.1.5 states what a lost buffer costs.

Two things this pass deliberately did **not** do: it did not solve source
substitution while ignoring destination substitution — that is R-C8-5, named
with its actor and interval — and it did not carry the second revision's
`digest` verb forward as the recommendation. The verb is kept in §7.3 as the
documented fallback if the materializer widening is refused, **without** its
proof label and with its remaining window stated.

One design constraint surfaced that the second revision missed:
`MAX_MATERIALIZED_BYTES` is 4096, sized for the 975-byte reviewed replacement.
The **original** file the contract must capture is a distribution default with
its comment header and is commonly larger. Reusing the constant would make the
capture refuse on an ordinary target. `G-1` needs its own reviewed bound, and
the value cannot be chosen from this repository. Recorded as proof obligation
§13.1-5.

### 1.3 R2-3 — an accurate comparison

§9 separates whole-root replacement, deeper-directory replacement, final-entry
replacement and in-place content mutation, and compares eight candidates across
all four with implementation cost, operational prerequisite and authorization
impact.

Withdrawn, with the correct statement in each case:

* the blanket *"cannot exist on Linux"*, narrowed to two true and narrow facts —
  no primitive returns a descriptor to a newly created **directory**, and Linux
  has no `funlinkat(2)`, so every removal names a final component;
* *"the benefit is already obtained by comparing the root's identity"* —
  false. `rename(2)` states that open descriptors for the renamed object are
  unaffected; a pathname identity comparison describes an instant and stabilises
  no later lookup;
* the `/proc/self/fd/3/journal/000001.seal` example — it fixes the first
  component only; `journal` is still resolved by name.

§9.5 supplies the exclusion boundary the second revision never considered: the
only non-root actor that can replace the seven probe subjects is the
`freedomsheet` account **this run creates**, with `--system --no-create-home
--shell /usr/sbin/nologin`; every process it runs is a synchronous waited child
of the boundary except one `systemd-run` transient unit, whose `LoadState` can
be checked before any removal. Where the check does not pass, the subjects are
reported preserved rather than removed. §9.5 also states what happens if the
exclusion cannot be proved, and keeps one premise — whether `useradd --system`
leaves the password field locked — as an explicit assumption, not a fact.

§9.6 evaluates a protected namespace as a trust-boundary design requiring
evidence and does **not** propose it. §9.7 states what is not asserted:
descriptors do not solve every race, DAC does not exclude an unrestricted root,
and an interface limitation does not prove there is no safer architecture.

---

## 2. Changes implemented, versus changes proposed and not implemented

### 2.1 Implemented in this submission

| File | Change |
|---|---|
| `docs/review/phase-5-0-evidence-harness-c8-ownership-design-r16-3.md` | **new** — the revised design, submitted for technical review |
| `docs/review/project-review-remediation-2026-09-09-r2-handback.md` | **new** — this document |
| `tests/phase_5_0_evidence/test_r13_remediation.py` | `FakeHost` now models **object identity and byte content**, records what each effect consumed as `Consumption` entries, and applies scripted substitutions through an `injections` hook immediately before a named step. `FakeMaterializer` records the bytes it writes |
| `tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | three new injected reproductions; the descendant case rewritten from a structural check into an injected substitution; module docstring corrected |
| `docs/review/project-review-remediation-2026-09-09-handback.md` | dated erratum appended, five corrections, original text preserved |
| `docs/review/phase-5-0-evidence-harness-c8-ownership-design-r16-2.md` | dated superseded banner added, original text preserved |
| `docs/review/Handover information`, `docs/project-management/status.md` | pointer updated |

**No file under `tools/` changed.** No generated artifact was hand-edited. No
verb, argument kind, arity, privilege, identity, executable, target fact or
execution surface was added.

### 2.2 Proposed and deliberately not implemented

| Id | What | Gate it waits on |
|---|---|---|
| `G-0` | five root-parent target facts, five `mkroot` observation keys | maintainer, on Codex's recommendation; the values need the read-only preflight |
| `G-1` | the materializer's bounded capture and content-bearing restore | **maintainer — it widens a privileged interface** |
| §7.3 | the fallback `digest` verb, if `G-1` is refused | maintainer — it adds a verb |
| `G-2` | 128 execution- and cleanup-side root identity guards | Codex technical acceptance |
| `G-3` | installed case-program integrity as a per-use prerequisite | Codex technical acceptance |
| `G-4` | quiescence check before removing the seven probe subjects | Codex technical acceptance |
| R-C8-1, R-C8-2, R-C8-3′, R-C8-4′, R-C8-5 | five residuals, each with actor, prerequisite, interval, consequence and alternative | maintainer, via Codex. **None accepted** |

Test cases 13–29 of the design's §10.2 model the proposal. They are **not
written**, because they cannot be until the mechanism exists, and **model-level
tests are not implementation evidence**.

---

## 3. Evidence-label corrections

**The descendant-replacement case is corrected.** Its previous form ran an
unchanged `FakeHost` and checked that configured paths were removed. That is
structural evidence that no descendant identity is consulted; it is not an
injected substitution of an object, and the R2 review was right to say so. It
now unlinks the subject and creates a different object under the same name in
the interval before `B4-19`, and asserts that the eventual `rm` consumed the
**replacement's identity**, distinguished by value from the created object's,
with its bytes — while the root's identity stays correct and every guard agrees.

That required strengthening the shared fake, because a set of path names cannot
model a substitution: the name is still there afterwards, which is the property
the finding is about. `FakeHost` now carries a per-path identity and content, a
`Consumption` log naming what each effect acted on, and an `injections` hook
that applies a substitution in the interval immediately before a named step.
Existing assertions were **not weakened** to accommodate it — the additions are
additive and the whole harness suite passes unchanged apart from the three new
cases.

**Three reproductions added**, all asserting commands and bytes rather than a
state label:

1. the root replaced between `B3-01` and the first `install -d` — every
   provisioning command, both flag changes and both configuration captures are
   issued afterwards, and **no `statroot` is issued anywhere in the execution
   phase**, which states structurally that there is no guard there to race;
2. the root replaced before `B5-C6-08` — the flag change and both captures are
   issued against the replacement;
3. a recovery input replaced before `CL-02` — the **bytes** that reach the live
   `pg_hba.conf` are the substituted bytes, the run reports S-C with no
   configuration risk, no retained recovery input and no operator procedure.

**Every case in that module remains visibly labelled a defect reproduction**, in
the module docstring and in each test's own docstring. A green run of it is
evidence that EH-R16-1 is open. The two controls beside them — ordinary cleanup
reaching S-C, and independently safe reversals proceeding when the guard fails —
are unchanged, so the reproductions cannot pass against a cleanup that never
ran. **No configured suite fails and no failing suite is left unexplained.**

---

## 4. Verification — commands, interpreters, results, skips

Serially, `TEST_DATABASE_URL` **explicitly unset** on every command, in the order
the prompt sets out, against the tree being submitted.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_r13_remediation.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
git diff --check
```

**Results are recorded in §4.1 below against the final submitted tree.**

### 4.1 Results

| Command selection | Result |
|---|---|
| `tests/phase_5_0_evidence/test_no_execution.py` | **193 passed** |
| `tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | **16 passed** — 13 before this pass, plus the three new injected reproductions |
| `tests/phase_5_0_evidence/test_r13_remediation.py` | **54 passed**, unchanged in count after the `FakeHost` strengthening |
| `tests/phase_5_0_evidence` | **1391 passed** — 1388 before this pass, plus the three new cases |
| `tests/test_*.py` | **2990 passed, 326 skipped**, one dependency deprecation warning |
| `tests/web` | **1610 passed, 1362 skipped** |
| `node --test foundry-module/tests/*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| `python -m compileall` on the two changed files | clean |
| `git diff --check` | clean |

### 4.2 Interpreters, identified accurately

The canonical test environment remains `/opt/freedom-blades/runtime/venv-web` on
`oracle-test`. **It was not contacted.** The two interpreters below are the
prior fallbacks the prompt names for this restricted local pass only, verified
present before use, and neither is the canonical default.

| Path | Verified | Used for |
|---|---|---|
| `/opt/discord-bots/venv-web/bin/python` | yes — Python 3.12.3, pytest importable | harness and web suites |
| `/opt/discord-bots/venv/bin/python` | yes — Python 3.12.3, pytest and `discord` importable | bot suite |
| `/opt/freedom-blades/runtime/venv-web/bin/python` | the path exists on **this** host and has **no pytest** | **not used** |

A path existing on this host establishes nothing about `oracle-test`.

### 4.3 Skips are unverified assertions

`TEST_DATABASE_URL` was unset for every command, so every database-marked
assertion skipped. The documented figure for a real database run is **80** web
skips; the figures in §4.1 are far higher and are therefore **unverified
assertions, not successful integration evidence.** Nothing in this submission
establishes any PostgreSQL behaviour.

### 4.4 Tooling not configured or unavailable

Distinguished from a pass rather than reported as one: **no formatter, linter or type checker is configured in this
repository.** There is no `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`,
`.pylintrc`, `mypy.ini`, `ruff.toml` or pre-commit configuration; `pytest.ini` is
the one configured tool. `black`, `ruff`, `flake8`, `mypy`, `pylint` and
`shellcheck` are none of them installed on this host. That is an unavailable and
unconfigured toolchain, **not** a passing one, and no result is claimed for any
of them. `compileall` on the two changed Python files and `git diff --check` are
what was available to run, and both were clean.

### 4.5 Checks not run, by restriction

No SSH; no `oracle-test` synchronization, inspection or provisioning; no
database operation; no destructive drill; no service change; no credential
access; no generated-vector execution; no `--execute`; no armed real boundary or
materializer. Every effect in every test is injected. The read-only target
preflight was **not** performed — it remains authorized and assigned to Codex,
and this handback neither performs it nor expands its scope — and the twelve
reviewed target facts remain `UNCONFIRMED`.

---

## 5. Historical-claim correction

The previous handback's §3.3 asserted that the sanitized material *"is in
commits before this session."* **That assertion is withdrawn.** It is corrected
by dated erratum E-5 in that document and set out in full in r16-3 §12.

Observed, by read-only inspection of this repository only:

| Check | Result |
|---|---|
| `git status --porcelain` on the sanitized report | untracked (`??`) |
| `git ls-files --error-unmatch` on it | not known to Git |
| `git log --all --oneline -- <report>` | no commits |
| `git log --all --oneline -S <former test name>` | no commits |
| `git status` on `tests/test_skills.py` and `models/skills.py` | modified, uncommitted |

**What that establishes:** within the scope of those commands — this working
tree and the refs reachable from it — the report is untracked and no reachable
commit contains it or the former test name. **What it does not:** it is not
proof of absence from any remote or unreachable object, and equally nothing
observed supports a claim of historical exposure. No remote was contacted, no
history was rewritten, and the removed material is reproduced nowhere.

The synthetic skills fixture, the sanitized crafting report and the production
alias fix are preserved. That work is not reopened, and the bot was not
restarted or contacted.

---

## 6. Manifest applicability and integrity

**Regeneration is not applicable to this pass.** No file in `COVERED_SOURCES`
changed: every change is under `tests/` or `docs/`, neither of which the manifest
covers. Verified rather than asserted — the plan and manifest were regenerated
through the **non-executing** CLI path twice, the two generations compared byte
for byte with each other, and both compared byte for byte with the supplied
artifacts:

```text
python -m tools.phase_5_0_evidence.execution.cli --manifest-out … --render …
run 1 vs run 2: manifest identical, concrete plan identical
run 1 vs docs/review/phase-5-0-evidence-harness-review-manifest.json: identical
run 1 vs docs/review/phase-5-0-evidence-harness-concrete-plan.md: identical
manifest_version: 9, unchanged
```

The 32 covered sources were re-hashed **independently of the harness**, directly
from disk with `hashlib`, against the manifest's own `source_digests`: 32
entries, the same set as `COVERED_SOURCES`, **0 mismatches**. The recomputed
review-input digest is
`ec1e3e70b5d24aca911df9e4dcd394361ebffdb04b9587434cb74386756f2839`, unchanged,
and the generated plan reports `is_executable=False`, three unresolved C-7 cases
and twelve unconfirmed facts — ten `E7` identity facts and the two interpreter
facts.

No new manifest version was invented and no generated artifact was hand-edited.
The digest is **review input only** and must not be passed to `--execute`.

---

## 7. Preserved gates and current project state

Re-asserted against this tree rather than assumed:

* the R16 observed-refusal correction — observed refusal stays distinct from the
  expected `J-26`;
* partial Band-7 coverage and eligibility reporting stay separate from passing
  outcomes and from overall completeness;
* Band-7 producers stay explicitly unresolved, and a supplied observation still
  cannot establish that a missing producer exists;
* the accepted C-6 immutable-flag experiments, the executor's six gates, the
  pre-existing-object protections and the configuration-recovery safeguards are
  unchanged;
* `is_executable` is `False` for the independent EH-R16-4 reason;
* no Package 5.0 product tooling or table was built.

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**. The
shipped plan retains three unresolved C-7 cases, twelve unconfirmed facts and
`is_executable=False`. Migration 0014, product implementation, deployment,
cutover and Package 5.1+ remain unauthorized.

---

## 8. Remaining gaps, proposed expansions, residual decisions, checks not run

* **EH-R16-1 is open.** The mechanism is unimplemented and the defect is live in
  the tree, now demonstrated by injected substitution rather than by structure
  alone.
* **Three items need a maintainer decision** before implementation: `G-0`'s five
  parent target facts, `G-1`'s materializer widening, and — only if `G-1` is
  refused — the fallback `digest` verb.
* **Five residuals are unaccepted**: R-C8-1, R-C8-2, R-C8-3′, R-C8-4′ and the
  newly named R-C8-5. Each states its actor, prerequisite, interval, consequence
  and alternative. R-C8-4′ **reverses** the second revision's recommendation to
  accept the seven probe removals blanket.
* **Five proof obligations are open**, in r16-3 §13.1: the root parent's
  ownership and mode; whether `useradd --system` leaves the password field
  locked; `openat2(2)` availability, only if candidate 4 is preferred; that the
  transient unit is the only asynchronous `freedomsheet` process; and the two
  live configuration files' sizes, needed to choose `G-1`'s capture bound. The
  first and last are read-only preflight observations and are Codex's.
* **`H-1` / `D5.0-12` / `OD-65`** — the group-writable worktree the guards' own
  bootstrap program comes from — is unchanged and not addressed here.
* **Checks not run** are §4.5.

Stopping here for Codex's technical review of the revised design. Implementation
follows only an accepted mechanism, and only once any required maintainer
expansion and residual decisions are recorded. No decision may be inferred from
this handback, from a passing suite, or from a reviewer finding the proposal
clearer than its predecessor.
