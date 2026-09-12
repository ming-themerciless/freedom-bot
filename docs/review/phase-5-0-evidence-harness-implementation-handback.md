# Package 5.0 evidence harness — implementation handback

Current revision: **R13.2 — the five R13 findings, and a plan that now reports
the evidence it cannot produce**, 2026-09-08. Everything below the R13.2 section
is retained as review history: the R13 section describes the tree the R13 review
read, the R12 section the one before it, and so on back through R3, including its
`UNASSIGNED` target statements, which are historical facts about those
submissions.

---

# R13.2 — ownership, retained recovery inputs, enforced prerequisites, declared gaps, and a written artifact

Date: 2026-09-08

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Input: `docs/review/phase-5-0-evidence-harness-r13-independent-review.md` —
**changes requested, pre-execution approval withheld**, four Blocking findings
and one Important. Reviewed digest
`d91e996977d91bbd6229fa0311df46ff13494611cb6cdd8a4234a077ded9e402`, superseded
by this submission and never execution authority.

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by the R13 review's own instruction to
*"return these findings to the implementer for bounded remediation and
independent re-review"*. That authority covers unprivileged code, focused-test,
controlled-documentation and generated-artifact work only. **It does not
authorize `--execute`, an armed real process boundary or materializer, execution
of a generated vector, SSH, inspection or mutation of `oracle-test`, any
privileged or mutation-bearing command, a database operation on the disposable
target, the destructive backup/restore drill, Package 5.0 product implementation,
migration `0014`, deployment, cutover, OD-62's binding ruling, or Package 5.1+.
None of those occurred.** The two interpreter facts and the ten `E7` facts remain
`UNCONFIRMED` and were not supplied.

## R13.2.0 The headline, stated before the detail

**`ConcretePlan.is_executable` is now `False`.** That is not a regression and it
is not incidental: EH-R13-4 found two whole groups of required evidence absent
from a plan that reported itself complete, and the honest correction — the one
the finding explicitly offers, and the only one available inside the R12/R13
boundary — is to declare them. Six required cases are now `UnresolvedStep`s under
two new conflicts, the executor's second gate refuses a plan carrying any of
them, and **there is therefore no run to be classified complete while a required
band is missing.** The new digest is review material describing a plan that is
deliberately not runnable.

## R13.2.1 EH-R13-1 — cleanup can delete pre-existing and unreached objects

**Conceded in full, including the part filtering does not fix.**

R12 ran the entire declared cleanup once any mutation had been attempted. The
`mutations_reached` list existed, was recorded and was never read. `R-02` checked
one group's absence and nothing else checked anything's, so a creation returning
*"already exists"* was followed by deletion of the existing object, and a run
that stopped in Band 2 went on to drop a database no step had created.

### The correction: ownership, established before the change

A cleanup step may reverse a mutation only when **all three** hold:

1. **a baseline step observed the subject absent before anything changed**;
2. **the run attempted the mutation** — recorded before the boundary is called,
   so an unknown launch outcome still counts as attempted; and
3. **no creation reported the object already there.**

The third is the half the review said filtering does not reach. A `groupadd`
exiting 9 *did* attempt its mutation, so an attempt filter would still delete the
group; `CommandStep.preexisting_statuses` names that exit, the executor
**withdraws** ownership, and the reversal is skipped and reported.

### Band 0 grew an ownership baseline — eleven steps, forty-one mutations

| Step | Vector | Absence is | Establishes |
|---|---|---|---|
| `R-02`, `R-B-G-*` | `getent group NAME` | exit 2 | the four created groups, and both memberships into `freedomjournal` |
| `R-B-A-*` | `getent passwd NAME` | exit 2 | the three created accounts |
| `R-B-ROOT` | `stat --format=%F <root>` | exit 1 | **twenty-nine** path mutations — every directory, file and file attribute under the root |
| `R-B-PG` | `psql --dbname postgres --command "SELECT 1"` | — | nothing; it is the **positive control** for the two below |
| `R-B-DB` | `psql --dbname fb_evidence_p5_0 --command "SELECT 1"` | exit 2 | the disposable database |
| `R-B-ROLE` | `psql --dbname postgres --command "SET ROLE freedom_migration_coordinator"` | exit 3 | the coordinator role |
| `R-B-UNIT` | `systemctl show --property=LoadState fb-evidence-s4.service` | `not-found` | the transient unit |

Four judgement calls, stated rather than buried:

* **One `stat` covers twenty-nine path mutations.** A directory that does not
  exist contains no file and no attributed inode. `_contained_mutation_ids()`
  **checks** the containment and refuses a declared path that is not under the
  root, rather than assuming it.
* **`R-B-DB` and `R-B-ROLE` are exit-status probes, not queries.** The reviewed
  vector grammar refuses `'`, `*` and `>` as arguments — deliberately — so
  `SELECT … WHERE datname = 'x'` cannot be written and must not be. A connection
  attempt and a `SET ROLE` name their subject as an identifier, read nothing and
  change nothing. `SET ROLE` is session-local.
* **Hence `R-B-PG`.** Both probes are satisfied by a **non-zero** psql exit, and
  a stopped server or a moved socket also exits non-zero — so without an ordinary
  connection that succeeds, *absent* and *unreachable* would be one observation
  and the run would claim ownership of objects it had never been able to look
  for. It is the same control-then-proof shape cleanup's post-reload
  verification already uses.
* **The two `postgres_config_line` mutations have no baseline, by contract.**
  Their reversal is a **restore** of a byte-exact pre-change capture, not a
  removal, and the executor already refuses to write the configuration unless
  that capture step was satisfied. `test_the_generated_plan_gives_every_deleted_
  object_a_baseline` asserts the partition in both directions.

### Ownership is checked before the change, not before the reversal

`ExecutingRunner._run_steps` refuses a mutation-bearing step whose mutations are
not all owned **before the boundary is called**, so a run that reached a creation
with no baseline changed nothing and has nothing to decide about afterwards.

### The applicable cleanup, and what is reported instead

`CleanupPlan.applicable(attempted=…, owned=…, withdrawn=…)` returns the steps
this run may carry out and a `SkippedCleanupStep` for every one it may not, each
with a fixed reason: `NOT_ATTEMPTED`, `NOT_OWNED`, `OWNERSHIP_WITHDRAWN` or
`CONFIGURATION_NOT_REACHED`. The reload and both verifications remove nothing, so
they apply **exactly when a restore applies** — that is the review's *"unreached
PostgreSQL configuration must not be restored or reloaded merely because an
OS-group creation was attempted"*, and it is now structural. `Configuration
Restoration` is built from the *applicable* declarations, so a run that never
reached a configuration mutation does not report an unrestored file as a risk it
created. `_declared_residue` is likewise narrowed to the applicable steps, except
on the path where cleanup failed before an applicability was derived, where the
whole declared plan is used because at that point nothing is known.

`CleanupOutcome` gains `preserved`: objects deliberately left because this run
did not create them. They are not residue and they are reported, because an
operator reading *"cleanup complete"* beside an object of that name needs to know
which of the two it is.

## R13.2.2 EH-R13-2 — failed configuration recovery deletes its recovery inputs

**Conceded.** With `CL-01`'s restore failing, R12 reported S-B and then requested
`rm --force -- …/before/pg_ident.conf` and `…/pg_hba.conf` — the two byte-exact
captures an operator would have restored from. The claim that *"no cleanup step
depends on an earlier step's success"* was true of the reversals and false of
these two.

`CleanupStep.requires_satisfied` names the cleanup steps that must have been
**satisfied** before a step may run. The generator links every capture removal —
and every directory that still holds one — to the complete configuration phase:
`CL-01`, `CL-02` (the two restores), `CL-03` (the single reload), `CL-04` (the
post-reload control) and `CL-05` (the refusal proof). The executor skips such a
step when its requirement is unmet, records it with the fixed
`RECOVERY_INPUT_RETAINED` reason, and reports the retained paths in
`CleanupOutcome.retained_recovery_inputs` alongside `RECOVERY_PROCEDURE` — four
bounded operator steps that name only objects the plan already declares and that
this harness does **not** perform, because §2.13.2b is explicit that residue is
never automatically cleaned.

One refinement the finding did not ask for and the implementation needs: the
requirement is evaluated against the **applicable** configuration phase. A run
that never changed a configuration file has nothing to recover, and retaining its
captures there would report a recovery input for a restoration that was never
owed.

Coverage: restore-, reload- **and** verification-failure are each a separate
parametrised regression, and each asserts the files are **still present on the
fake host** and that no `rm` naming them reached the boundary — not merely that
a call was absent or that the state classified as S-B. A successful restoration
removes them, so the retention is conditional rather than a permanent exemption.

## R13.2.3 EH-R13-3 — non-identity prerequisites ignore their observations

**Conceded, and the review's instruction to check capture formats against the
producing executable found a second defect.**

### The gate now covers every observation

`contract_for()` returns `None` for `EXIT_STATUS_ONLY` and **for nothing else**.
Nine policies that recorded an observation and were decided by their exit status
now carry a contract, compared at the same point and under the same fail-closed
rules the two case-program verbs already had — missing, duplicated, unreadable,
malformed, unexpected or unequal is a refusal that names the reviewed key and no
observed value.

Two shapes of contract:

* **derived**, from reviewed constants — `case_runtime`, `case_identity` and,
  new here, `capability_masks`. `P-01` observes the **launching process**, which
  *is* `E7`, so its four values are four of the same ten reviewed target facts
  and are read from that one source. Two statements of one fact are two things
  that can disagree; and
* **declared**, on the step, in the same closed comparison vocabulary, pinned in
  the review manifest and rendered in the plan's new §5b. `plan.CommandStep`
  refuses a step that records an observation and declares nothing, and
  `declared_contract()` refuses a declaration that does not cover **every key its
  policy emits** — so the declaration cannot quietly leave one out.

### The capture-format defect this uncovered

`_capability_masks` looked for `CapInh:`, `CapPrm:`, `CapEff:`, `CapBnd:` and
`CapAmb:` at the start of a line. **Those are `/proc/<pid>/status` field names,
and `capsh --print` prints none of them.** Against real `capsh` output the reader
found no mask at all; the review's synthetic `CapBnd: 0000000000000000`
satisfied a reader no `capsh` could satisfy. The format was verified against the
executable itself (libcap `capsh --print`, read locally for its **output shape**
and for no host fact) and the reader now takes what `capsh` prints: the bounding
and ambient **name sets**, the securebits from the line's hexadecimal field, and
`no-new-privs`. The name lists are converted to masks on the observation side —
by total lookup in the one closed name table, an unknown name making the value
`unreadable` — because the complete bounding set of a root process is
forty-one names and about seven hundred characters, six times
`capture.MAX_VALUE_LENGTH`.

Two further formats were narrowed for the same reason:

* **`_attribute_flags`** records `append_only` and `immutable` as a yes/no each
  and no other letter. The whole sorted letter set could not be compared against
  a reviewed expectation without the plan knowing the host's filesystem: `e` —
  *extent format* — is on every ext4 inode and absent elsewhere, so the expected
  letter set was a host fact wearing a plan constant's clothes.
* **`_group_members` and `_account_identity`** write the literal `none` for an
  empty set. An empty *value* is the capture boundary's marker for *"nothing was
  read"*, and `freedomcoord`, `freedomsheet` and `fbprobe` have — per §2.12.2 —
  no explicit member, so their true observation could never have satisfied a
  contract while its emptiness was spelled that way.

### Where each expectation comes from

| Policy | Expected value's source |
|---|---|
| `capability_masks` | `capability.E7_TARGET_FACTS` — reviewed, `UNCONFIRMED` |
| `case_runtime` / `case_identity` | unchanged from R12/R13 |
| `group_members` / `account_identity` | `identity.CANONICAL_GROUPS` and `CANONICAL_ACCOUNTS` — §2.12.2's canonical table, compared **as a set and in both directions** |
| `mount_facts` | `approved_target.APPROVED_TARGET_FACTS` — the filesystem type and backing device Peter Duscha **confirmed** on 2026-09-05 |
| `attribute_flags` | the flags this plan's own `chattr` sets |
| `file_mode` / `file_capabilities` | the mode and owner this plan's own `install` sets; `case_runtime.CASE_PROGRAM_MODE` |
| `unit_directives` | the `--property=` values this plan's own `systemd-run` sets |
| `case_result` | the step's own verb and satisfying statuses, derived in one place so the exit status and the observation cannot disagree |

### The two shape-only comparisons, enumerated and justified

`NUMBER_PRESENT` and `TEXT_PRESENT` check that a value is present, unique and
well-formed, and do not compare it. They are used for exactly two things — a
`--system` uid or gid the plan cannot know before `useradd` runs, and a byte
count or file size that depends on what a disposable file holds when the
operation runs — every use carries a written `uncompared_because`, and
`test_a_value_that_is_not_compared_says_why` enumerates the complete key set so
the exemption cannot quietly widen. `TEXT_ANY_OF` exists for one situation the
reviewed design itself creates: §5.2 states the same kernel check as `EPERM` in
one sentence and `EACCES` in another, which `_ACCESS_DENIAL_STATUSES` already
admits both exit statuses for.

### Coverage

Both of the review's reproductions are regressions — an empty bounding set from
`P-01` and `freedomjournal:x:5004:freedomcoord,freedomsheet,fbprobe` from
`B2-10` — each driven through the **real sanitizer** from raw synthetic command
output, each asserting the run stops and that **no step after it reached the
boundary**. Missing, unreadable, duplicated and unexpected observations are
parametrised across the observation-bearing steps, the `/proc`-shaped `capsh`
line is asserted to produce no observation at all, and the positive direction —
compliant output satisfying the contract — is asserted too, so the refusals are
about the values rather than about an unsatisfiable contract.

## R13.2.4 EH-R13-4 — required evidence cases absent from the executable plan

**Conceded. Reported rather than implemented, which is the branch the finding
offers and the only one inside the standing boundary.**

`required_cases.py` states the required cases as data, and
`check_case_coverage()` refuses a plan in which one is neither **produced** by a
step nor **declared unresolved**. There is no third state, and that is what makes
`is_executable` a statement about completeness rather than about what the
generator happened to attempt.

Six cases are declared unresolved under two new conflicts:

* **C-6, Band 5** — `JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE`,
  `JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE`, `JNL-50-E5-CLEAR-THEN-DENIED-OPEN`. All
  three are about the **immutable** flag, and the reviewed case program's closed
  verb table reads and clears `FS_APPEND_FL` and nothing else. Adding
  `FS_IMMUTABLE_FL` operations widens the verb set, the arities and what a
  bounded `ioctl` may do — which the R12 and R13 boundaries explicitly forbid
  this remediation from doing on its own authority. **An `+a` approximation was
  considered and rejected**: it would produce a passing record for a case about
  `+i`, which is worse than a declared gap.
* **C-7, Band 7** — `JNL-51-PROVENANCE-OMITTED`,
  `JNL-47-NO-GENERATION-ON-FAILURE`, `JNL-47-RECOVERY-STATE`. The band's
  classifiers are pure functions over supplied observations and nothing supplies
  any. What is missing is a **supplied-observation ingestion stage**: a new input
  surface on the one component that can construct a boundary able to start
  privileged processes, so its shape, trust boundary and validation are a
  maintainer decision and an independent review.

The seven `B5-E*` steps also lost the case ids they should never have carried.
They observe an identity and perform no capability-matrix operation, and
attributing `JNL-49-<identity>`/`JNL-50-<identity>` to them made the matrix look
present in a plan containing none of it. They now carry
`CAP-IDENTITY-<identity>`, and a regression asserts no `CASE_IDENTITY` step
carries a `JNL-49`/`JNL-50` id.

**Decision required.** Two maintainer decisions are returned, not taken: whether
the reviewed case program's verb table gains immutable-flag operations, and what
a bounded supplied-observation ingestion stage looks like — or, in either case, a
separately approved narrower execution scope that excludes the band and says so
in the artifact.

## R13.2.5 EH-R13-5 — the CLI reports an artifact written without writing one

**Conceded.** `artifact written : {outcome.artifact_admissible}` printed an
**eligibility** answer under a **persistence** label, and no file was ever
written.

`execution/artifact.py` is the bounded path. It writes the **run record** — what
ran, in order, with the sanitized observations, what stopped the run, and what
cleanup did, skipped, preserved and retained — then **reads the bytes back from
disk and validates them** against the run before returning a path. Every failure
is a `RunRecordRefused`, and the CLI reports the fixed reason rather than a path.
Two lines replace the one: `artifact eligible:` and `run record       :`.

It is deliberately **not** the classified evidence artifact. Producing a set of
`EvidenceRecord`s requires the band classification Band 7 has no caller for
(C-7), and writing a file of the right shape with the cases that happen to be
available would be the same defect in a new place. `document_type` says which
document it is, in the document.

Bounds: observation values are checked against `capture.MAX_VALUE_LENGTH` — the
same bound the capture boundary applies — and reviewed fields against a separate,
larger bound, because §2.13.5c's `capsh` constructions carry one legitimate
six-hundred-character argument.

## R13.2.6 Every prior boundary, preserved

Unchanged and asserted by the retained R11/R12/R13 suites: the interpreter path
and its exact `-I -S` prefix; the closed case-program verbs, arities, modes and
path grammar; `PERMITTED_EXECUTABLES`; the delegated `capsh` and `systemd-run`
tail validation; the four late-bound names and their substitution sites; the
symlink target and cleanup primitive; target-root validation; the `ctypes`
exception at one file, one function and one literal `PR_GET_SECUREBITS`; the
materialization destinations and bytes; the process and materializer arming
rules; the six executor gates; `E7`'s twelve-key contract and its ordering
requirement; and the authority required to establish reviewed target facts and to
execute the harness. No forbidden token was added to any cleanup vector, and no
recursive or wildcard removal is expressible.

Two reviewed surfaces were **widened**, both narrowly and both stated here:
`UNIT_DIRECTIVES` gained the `LoadState` key and became a variable-key policy
(`systemctl show` prints exactly the properties asked for), and `capture` now
imports `capability.ALL_CAPABILITY_NAMES` for the name-to-bit lookup. Neither
adds an executable, a path, a verb or a privilege.

## R13.2.7 Generated artifacts

Regenerated from covered sources, generated **twice** and compared byte for byte
— identical both times — and every covered source independently re-hashed against
the manifest's recorded digest, with no mismatch.

| | R13 | R13.2 |
|---|---|---|
| covered sources | 28 | **30** (`required_cases.py`, `execution/artifact.py`) |
| command steps | 116 | **127** |
| cleanup steps | 46 | 46 |
| declared mutations | 43 | 43 |
| unresolved items | 0 | **6** (C-6, C-7) |
| `is_executable` | True | **False** |
| manifest version | 5 | **6** |
| harness version | 0.6.0-pre-execution | **0.7.0-pre-execution** |

New manifest digest, **review material only, not execution authority**:

`8875b165b32f5a0929770380571c15ae4a102cd80f4ebb8979a17c7698690cb4`

The manifest gained `required_cases` (each with the step that produces it or the
conflict that blocks it), `expectations.launcher_capabilities`, and per step
`observation_expectations`, `establishes_ownership_of` and
`preexisting_statuses`. The rendered plan gained §5b (reviewed observation
expectations) and §5c (ownership baselines). No generated file was hand-edited.

## R13.2.8 Verification, exactly as run — and its limits, stated first

**The documented environment is `oracle-test`, and the active pre-execution
restrictions prohibit SSH to it.** Every figure below is from the **local
fallback** interpreters, which is the same limit the R13 review recorded. Three
of them are degraded relative to the prescribed run and are marked.

| Command | Result |
|---|---|
| `env -u TEST_DATABASE_URL … venv-web … pytest -q -rs tests/phase_5_0_evidence` | **1210 passed**, no skips |
| `env -u TEST_DATABASE_URL … venv-web … pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **181 passed** |
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test … venv-web … pytest -q -rs tests/web` | **2892 passed, 80 skipped** — the documented 80-skip baseline |
| `TEST_DATABASE_URL=… … venv … pytest -q -rs tests/test_*.py` | **3310 passed, 2 failed, 2 skipped** |
| `node --test "foundry-module/tests/"*.test.mjs` | **fail 0** |
| `compileall` over the changed Python, both interpreters | clean |
| `git diff --check` | clean |

**The two bot-suite failures are environmental and pre-existing.**
`test_a_role_whose_sql_identity_differs_refuses_against_postgresql` and
`test_a_newline_bearing_role_refuses_against_postgresql`, both in
`tests/test_database_backup_restore.py`, fail with `InsufficientPrivilege:
permission denied to create role` — the local database user lacks `CREATEROLE`.
Neither test imports anything this change touches; the only file outside
`tools/phase_5_0_evidence/` and `tests/phase_5_0_evidence/` that this submission
modifies is `tests/web/test_p3_4_static_assets.py`, whose scope guard needed the
two new harness sources declared, and which passes.

A first bot-suite run reported 26 failures and 26 errors from leftover state in
the shared local `freedom_test` database — finding F-6's shape, on a local
database that is not the disposable-server one. A clean re-run reduced it to the
two above; both figures are reported rather than only the better one.

**Not run, and why.** The prescribed `oracle-test` run under
`/opt/freedom-blades/runtime/venv-web/bin/python`; the destructive
backup/restore drill; any privileged, mutation-bearing or `--execute` invocation;
any host inspection; any operation against the disposable target's PostgreSQL.
The pristine-schema drill failure the R13 review names is unaffected by this
submission and was not investigated. Formatter, linter and type checker remain
unconfigured in this repository and none was introduced.

## R13.2.9 Confirmation

No host was inspected and no host was mutated. No SSH ran. No account, group,
file, directory, database object, HBA line, identity-map line or transient unit
was created on any host. No generated vector was executed, no process boundary or
materializer was armed, and no reviewed target fact was supplied: the two
interpreter facts and the ten `E7` facts remain `UNCONFIRMED` and the executor
refuses on each of them before any command starts. `capsh --print` was run **on
this development workstation** to read the *output format of the executable*, as
the review's *"check capture formats against the specific producing executable"*
requires; nothing from it is a fact about `oracle-test` and no value from it
entered an expectation. The full dirty worktree was preserved; nothing was reset,
reverted, staged, committed or pushed.

## R13.2.10 Residuals and judgement calls

1. **`is_executable` is `False`, and Package 5.0 stays `not ready`.** P5.0-R5
   remains Blocking and OD-62 remains Open. Two maintainer decisions are
   returned in §R13.2.4.
2. **`no_new_privs` from `capsh --print` is version-dependent.** A libcap old
   enough not to print `(no-new-privs=…)` produces no such key and the contract's
   `MISSING_KEY` refusal fires. That is the intended direction — an unread
   prerequisite is a refusal — and it is a residual because it would stop a run
   for a benign reason on an older libcap.
3. **`R-B-DB` and `R-B-ROLE` infer absence from a psql exit status.** `R-B-PG`
   excludes *unreachable*; it does not exclude every other cause of a non-zero
   exit. A query would be exact and cannot be written under the reviewed vector
   grammar, which refuses string literals.
4. **One `stat` establishes ownership of twenty-nine paths.** Sound — a
   directory that does not exist contains nothing — and it is one observation
   rather than twenty-nine, which is a smaller evidential surface than a
   per-path baseline would be.
5. **Two shape-only comparisons exist**, enumerated and justified in
   §R13.2.3. A reviewer who disagrees that a run-time-allocated `--system` uid
   should be recorded at all would remove the key rather than the comparison.
6. **The run record is not the evidence artifact**, and cannot be while C-7 is
   open. §R13.2.5 says so in the document itself.
7. **`P-02` is retained unchanged** and still has no semantic contract: it is a
   `capsh --decode` of a documented constant with `EXIT_STATUS_ONLY`, so there is
   no observation to compare. It is named here because a reader checking
   *"every prerequisite is now enforced"* should not have to discover it.

## R13.2.11 Request

Codex independent pre-execution re-review of the five corrections, and in
particular of:

1. whether ownership-before-change plus attempt plus withdrawal is the right
   closure for EH-R13-1, and whether the four judgement calls in §R13.2.1 hold;
2. whether retaining recovery inputs until restore, reload **and** both
   post-reload observations succeed is the right condition, and whether the
   bounded operator procedure is adequate;
3. whether the declared-expectation mechanism is the right shape for EH-R13-3,
   whether the three corrected capture formats match their producing executables,
   and whether the two shape-only comparisons are acceptable where they are used;
4. **the two maintainer decisions in §R13.2.4** — the case program's verb table,
   and the supplied-observation ingestion stage — or a separately approved
   narrower execution scope; and
5. whether the run record is the right document and the right bound.

Work stops here. Package 5.0 remains **not ready**, P5.0-R5 remains **Blocking**,
OD-62 remains **Open**, and no authorization in force permits reading the
interpreter or `E7` target facts or running this harness.

---

# R13 — the eighth identity

Date: 2026-09-07

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r13-prompt.md`. That
authority covers unprivileged code, focused-test, controlled-documentation and
generated-artifact work only. **It does not authorize `--execute`, an armed real
process boundary or materializer, execution of a generated vector, SSH, host
inspection or mutation, any privileged or mutation-bearing command, mutation of
`oracle-test`, a database operation, the destructive backup/restore drill,
Package 5.0 product implementation, migration `0014`, deployment, cutover,
OD-62's binding ruling, or Package 5.1+. None of those occurred.**

Outcome: **EH-R12-1 is remediated.** R12's accepted `P-05` semantic gate, its
`E1 … E6`/`E8` identity contracts, its bounded `PR_GET_SECUREBITS` call, and
R11's Option-B vector grammar, C-3 symlink boundary, C-5 late binding, C-1 root
boundary and C-4 materializer are preserved unchanged. The generated plan still
reports **zero unresolved design conflicts** and `executable: True`. Nothing was
executed. No finding is closed by this submission, no readiness item moves, no
assumption is confirmed, no operational check is discharged, and Package 5.0
remains `not ready`; P5.0-R5 remains Blocking.

## R13.0 The finding, conceded before its correction

**EH-R12-1 is correct and is conceded without qualification.**

The R12 authority required every `E1 … E8` identity to call
`prctl(PR_GET_SECUREBITS)` inside the final interpreted case-program process and
to compare the complete twelve-value identity observation before any dependent
operation could run or be interpreted. R12 delivered that for **seven**
identities and excluded the eighth. It did so deliberately and wrote the
exclusion into five places:

* `expectations.identity_contract()` raised `PlanRefused` for `E7`;
* `expectations.CONSTRUCTED_IDENTITIES` was the seven, under a name that read as
  though it were the set of identities a `CASE_IDENTITY` step may name;
* `plan.CONSTRUCTED_IDENTITY` was the shape `E[1-6]|E8`, so a step naming `E7`
  was refused at construction;
* `review_manifest` and `execution/cli.py` each skipped `E7` explicitly; and
* `test_expectations.py::test_e7_has_no_identity_contract` **asserted that an
  `E7` identity step is rejected**, so the suite defended the gap.

The R12 handback then said, in §R12.12, that *"every `E1 … E8` identity's final
securebits is read by `prctl(PR_GET_SECUREBITS)` inside the exec'd process and
compared"*. That sentence was false for `E7`, and it is withdrawn.

### Why `P-01` and `P-02` were not a substitute

The substitution was *"`P-01` and `P-02` are the observations it is classified
from"*. They are not, in three independent respects:

1. **Neither runs the case program.** `P-01` is `capsh --print` and `P-02` is
   `capsh --decode=0x000001ffffffffff`. §2.13.5c's assertion contract is about
   the process the reviewed vector produces — *"inside the exec'd process, and
   before the operation under test"* — and neither of these is that process.
2. **Neither reads the final securebits.** `capsh --print` prints the securebits
   of **`capsh`'s own** process, before any `execve` of the interpreter. That is
   the same category of error as EH-R11-2: a statement about an intermediate
   state standing in for the state that attributes the operation. `P-02` reads
   nothing at all about the running process; it expands a documented mask into
   capability names.
3. **Between them they do not cover the required key set.** `P-01` covers the
   launcher's bounding set. Neither covers `E7`'s effective uid, effective gid,
   complete supplementary group set, `CapInh`, `CapPrm`, `CapEff`, `CapAmb`,
   `NoNewPrivs` or final securebits as **one compared observation**, and
   `P-02`'s subject — a documented mask read from `/proc/1/status` on a different
   host on 2026-08-31 — is not a fact about the target at all.

`P-01` and `P-02` are **retained, unchanged, and still generated**. They are
separate root/target preflight evidence and they remain that. What R13 adds is
the observation they never were.

### The premise R12 reasoned from, and why it does not carry

R12's premise — *"`E7` is constructed by no vector"* — is true. §2.13.5c says so:
`E7` is **"no invocation.** The harness's own process, root, no securebit set and
no drop of any kind." What does not follow is that it cannot be **observed**. The
`identity` verb takes no argument, performs no operation, and reports the same
twelve values whatever produced the process it runs in. Running it directly, as
root, through the same reviewed Option-B vector observes `E7` exactly as running
it behind `capsh` observes `E1`.

The confusion is visible in the vocabulary itself, which is why the vocabulary
changed: *constructed* is a statement about **how an identity is produced**, and
R12 used a set named for it as though it were a statement about **which
identities are observed**.

## R13.1 The new step — `P-06`

Generated in `_case_program_prerequisites()`, immediately after `P-05`:

| Field | Value |
|---|---|
| step id | `P-06` |
| band | `capability` |
| `run_as` | `root` |
| `argv` | `/opt/freedom-blades/runtime/venv-web/bin/python -I -S /var/lib/fb-evidence-p5-0/bin/case identity` |
| `role` | `StepRole.PREREQUISITE` |
| `capture` | `CapturePolicy.CASE_IDENTITY` |
| `identity_name` | `E7` |
| `bindings` | none |
| `satisfying_statuses` | `(0,)` |
| `evidence_case_ids` | `CAP-E7-IDENTITY`, `CAP-E7-ENVIRONMENT` |

**The vector is the exact direct Option-B vector**, built by
`case_runtime.build_case_vector(APPROVED_TARGET, "identity")` and therefore
validated by `validate_case_vector()`: one absolute interpreter path in position
0, `-I -S` complete and in order, the case-program path through
`DisposableTarget.contained_path()` so it is strictly inside the validated
disposable root, the verb `identity` from the closed table, and its exact arity
of zero. There is **no `capsh`**, no `--secbits=`, no `--drop=`, no `--uid=`, no
option of any kind after the program path, and no late-bound account or group
substitution — `CommandStep` now refuses an `E7` step that declares a binding
site or that runs as anything but `root`.

Because it runs the `identity` verb, it reaches `_do_identity()` in the case
program, which reads `uid`, `gid` and `groups` from `os`, the five masks and
`NoNewPrivs` from `/proc/self/status`, and the **final securebits** from the
already-bounded `prctl(PR_GET_SECUREBITS)` — after `execve`, in the final
interpreted process. That code path is unchanged from R12; `E7` now uses it.

### Ordering

`P-06` is the **second** step in the plan that runs the case program, and the
first that runs it after the runtime has been established. `P-05` deliberately
stays ahead of it, so the identity is observed through an interpreter already
compared against its reviewed digest, version, resolved path and isolation rather
than the other way round.

`concrete_plan._validate_root_identity_ordering()` asserts this over the
**generated** plan rather than leaving it to a comment. It requires exactly one
`E7` identity observation — none would be the finding again, two would leave
which one a dependent operation depends on undecided — and it requires every
root case-program **operation** to appear after it. The two observation verbs are
excluded and named: `case_runtime.OBSERVATION_VERBS` is `runtime` and `identity`,
which *"make no filesystem change and take no path"*, and neither reports
anything whose meaning depends on which identity ran it.

Because the executor stops the whole run at the first unsatisfied step, an `E7`
mismatch prevents every later step from reaching the boundary or being
interpreted. That is asserted end to end, not argued.

## R13.2 The twelve-value contract, and where each value comes from

`expectations.root_identity_contract()` builds `E7`'s contract. It compares the
**same twelve keys** as the seven constructed identities, and that is enforced
mechanically rather than by inspection: `ObservationContract.__post_init__` now
refuses any `CASE_IDENTITY` contract whose key set is not exactly
`expectations.IDENTITY_KEYS`. A narrower `E7` contract — one that quietly omitted
the securebits it has no reviewed fact for — is the finding in a new shape, and
it cannot be built.

| Key | Comparison | Expected value, and its source |
|---|---|---|
| `verb` | text | the literal `identity` — the case program's own, as for the other seven |
| `result` | text | the literal `returned` — likewise |
| `uid` | number | reviewed target fact `E7_TARGET_FACTS["uid"]` |
| `gid` | number | reviewed target fact `E7_TARGET_FACTS["gid"]` |
| `groups` | number **set** | reviewed target fact `E7_TARGET_FACTS["groups"]` |
| `cap_inh` | hex | reviewed target fact `E7_TARGET_FACTS["cap_inh"]` |
| `cap_prm` | hex | reviewed target fact `E7_TARGET_FACTS["cap_prm"]` |
| `cap_eff` | hex | reviewed target fact `E7_TARGET_FACTS["cap_eff"]` |
| `cap_bnd` | hex | reviewed target fact `E7_TARGET_FACTS["cap_bnd"]` |
| `cap_amb` | hex | reviewed target fact `E7_TARGET_FACTS["cap_amb"]` |
| `no_new_privs` | number | reviewed target fact `E7_TARGET_FACTS["no_new_privs"]` |
| `securebits` | hex | reviewed target fact `E7_TARGET_FACTS["securebits"]` |

**Why every environment value is a reviewed target fact rather than a
derivation.** The seven constructed identities have two independent sources the
observation cannot supply: §2.13.5c's seven-step derivation from `M`, and the
numbers the **bound** vector asked the kernel for. `E7` has neither. There is no
`M`, because nothing is dropped and nothing is raised; there is no bound vector,
because nothing is substituted. Its uid, gid, supplementary set, masks,
`NoNewPrivs` and securebits are facts about the **host the harness runs on** —
which is exactly what §2.13.5c means when it labels `E7`'s masks
*"environment-derived"* and *"not derived — read"*.

So each is stated from outside, in the same sense
`case_runtime.EXPECTED_INTERPRETER_SHA256` and `EXPECTED_INTERPRETER_REAL_PATH`
are, and verified on the host by an independent reviewer.

**Nothing is learned from the run being judged.** Not from `P-01`, not from
`P-02`, not from `E7`'s own observation, not from `/proc`, `id` or `capsh`. A
source-level test asserts that `root_identity_contract`'s executable body names
`capability.e7_expected_values()` and none of those.

**§2.13.5c's 2026-08-31 host row was not copied into an executable
expectation.** It could not have been quietly, either: `EvidenceIdentity.
expected_masks()` now **raises** for `E7` rather than returning
`DOCUMENTED_ROOT_MASK`. R12 returned that reading from the same method that
derives the other seven identities' masks from `M`, which made a documented host
value indistinguishable from a derivation and available to anything that asked
for an expectation. The documented row is now `capability.documented_root_masks()`
— review material for `CAP-E7-ENVIRONMENT`, which `classify_root_masks()`
compares the host's PID-1 mask with and reports `INCONCLUSIVE` on disagreement —
and it is reachable from no contract.

## R13.3 The ten reviewed `E7` target facts, and their current state

All ten ship **`UNCONFIRMED`** in this tree. None was supplied, and supplying one
requires reading `oracle-test`, which no authorization in force grants.

| Reviewed fact | Shape a stated value must have | State in this tree |
|---|---|---|
| `E7.uid` | decimal, ≤ 10 digits | **UNCONFIRMED** |
| `E7.gid` | decimal, ≤ 10 digits | **UNCONFIRMED** |
| `E7.groups` | comma-separated decimals | **UNCONFIRMED** |
| `E7.cap_inh` | lower-case hex, ≤ 16 digits, no `0x` | **UNCONFIRMED** |
| `E7.cap_prm` | lower-case hex, ≤ 16 digits, no `0x` | **UNCONFIRMED** |
| `E7.cap_eff` | lower-case hex, ≤ 16 digits, no `0x` | **UNCONFIRMED** |
| `E7.cap_bnd` | lower-case hex, ≤ 16 digits, no `0x` | **UNCONFIRMED** |
| `E7.cap_amb` | lower-case hex, ≤ 16 digits, no `0x` | **UNCONFIRMED** |
| `E7.no_new_privs` | decimal, ≤ 10 digits | **UNCONFIRMED** |
| `E7.securebits` | lower-case hex, ≤ 2 digits — `0 … SECUREBITS_MAX` | **UNCONFIRMED** |

Each is stated in the **exact text form the case program prints**, so what a
reviewer approves is what is compared. The shapes are the capture boundary's own:
a value the boundary could never report is refused as unconfirmed here rather
than compared against forever — the rule
`case_runtime.interpreter_real_path_confirmed()` already applies to the resolved
interpreter path. The securebits shape's two hexadecimal digits are exactly
`0 … 0xff`, which is `SECUREBITS_MAX`, and a test asserts the two agree.

**What is needed.** The Operations Owner states, for **`oracle-test` as it is
now**, and the independent reviewer verifies there: the uid and gid the harness
process executes as; its complete supplementary group set; its `CapInh`,
`CapPrm`, `CapEff`, `CapBnd` and `CapAmb`; its `NoNewPrivs`; and the securebits
`prctl(PR_GET_SECUREBITS)` returns in it. **The 2026-08-31 values in package-plan
§2.13.5c do not discharge this**, and were not used: they were read from a
different host, and `CAP_LAST_CAP` differing would make the three full masks
wrong. Supplying a fact edits a covered source, which changes the manifest
digest, which is the re-review the substitution should trigger.

### How an unconfirmed fact refuses, before any process starts

Two gates, and the second would still hold if the first were removed:

1. **`ExecutingRunner.__post_init__` — gate 4.** `capability.
   unconfirmed_e7_facts()` is consulted at **construction**, before `execute()`
   is called and therefore before the boundary is reached at all. A single
   unconfirmed fact refuses the whole run and names which facts are outstanding
   — **names only**, which are constants this package declares, never values and
   never host facts. The gate is fail-closed over the set: nine facts out of ten
   is not nine tenths of a comparison, it is a contract with a free variable.
2. **`capability.e7_expected_values()`.** It raises while any fact is
   unconfirmed, so `root_identity_contract()` cannot be built, so
   `contract_for()` raises, so `ExecutingRunner._expectation_refusal` records
   `EXPECTATION_NOT_CONSTRUCTED` and the step is **not satisfied**. There is no
   path on which an unconfirmed fact becomes a comparison that passes.

The executor's gate list is now **six**, not five — the R12 docstring said five
while the code already had a sixth (the resolved-path fact) folded into a
sentence about the digest. That is corrected. **Two facts and ten facts refuse
today**, all on unsupplied reviewed target facts, and no refusal was converted
into a warning.

## R13.4 The mismatch and refusal matrix

`E7` uses the same fixed classification vocabulary as every other contract, and
no classification names an observed value, path, digest, identifier or exception
text.

| Condition | Classification | Test |
|---|---|---|
| no observation at all | `NO_OBSERVATIONS` | `test_every_refusal_category_is_a_fixed_safe_classification`, `test_e7_exiting_zero_is_not_a_pass` |
| observations that are not sanitized pairs | `MALFORMED_OBSERVATIONS` | `test_every_refusal_category_is_a_fixed_safe_classification` |
| a reviewed key absent | `MISSING_KEY` + the reviewed key | `test_a_missing_e7_key_names_the_reviewed_key_and_nothing_else` (10 cases) |
| a reviewed key twice | `DUPLICATED_KEY` + the reviewed key | `test_every_refusal_category_…`, `test_e7_exiting_zero_is_not_a_pass` |
| a value the capture boundary could not read | `UNREADABLE_VALUE` + the reviewed key | same |
| a name outside the reviewed key set | `UNEXPECTED_KEY` | same |
| a value that is not equal | `UNEQUAL_VALUE` + the reviewed key | `test_one_mismatch_in_each_e7_field_category_is_refused` (12 cases) |
| the contract could not be built | `EXPECTATION_NOT_CONSTRUCTED` | `test_the_run_refuses_when_the_e7_contract_cannot_be_built` |

Every field category is covered by its own mismatch: `uid`, `gid`, `groups`,
each of `cap_inh`, `cap_prm`, `cap_eff`, `cap_bnd`, `cap_amb`, `no_new_privs`,
`securebits`, and the two literals `verb` and `result`.

### The regression tests the prompt names, and where each is

`tests/phase_5_0_evidence/test_root_identity.py` is new — **90 cases**. All R12
tests are retained. Statements that encoded the exclusion were corrected in place
across four existing modules — `test_expectations.py` (the renamed set and
constructor, the replaced `E7` test, the plan's identity set, the shape
agreement, and the `CommandStep` case that used `E7` as an invalid name),
`test_concrete_plan.py` (`P-06`'s position, and the Band-5 test's prose and a new
assertion that all eight are observed), `test_bands.py` and
`test_case_program.py` — and nothing else was changed.

| Required proof | Test |
|---|---|
| exactly one `E7` `CASE_IDENTITY` step, plus the seven existing ones | `test_the_plan_carries_exactly_one_e7_identity_step_and_the_seven_others` |
| the exact direct Option-B `identity` vector, no `capsh`, inside the validated target | `test_the_e7_step_is_the_exact_direct_option_b_identity_vector` |
| runs as root, declares no late-bound substitution | `test_the_e7_step_runs_as_root_and_substitutes_nothing`, `test_a_step_naming_e7_may_not_bind_or_assume_another_identity` |
| the contract has exactly the same twelve keys as `E1 … E6`/`E8` | `test_e7s_contract_has_the_same_twelve_keys_as_the_other_seven`, `test_the_contract_cannot_be_built_with_a_narrower_key_set` |
| each expected value comes from a reviewed target fact, not the observation | `test_every_expected_e7_value_comes_from_its_reviewed_target_fact` (10), `test_no_expected_e7_value_is_read_from_an_observation`, `test_supplying_a_fact_changes_the_contract_where_it_is_supplied` |
| every unconfirmed fact refuses before the process boundary is called | `test_the_shipped_e7_facts_refuse_the_executor`, `test_one_unconfirmed_fact_refuses_before_any_command_starts` (10), `test_every_unconfirmed_fact_is_reported_and_the_set_is_fail_closed` |
| a complete matching observation satisfies the contract | `test_the_complete_matching_observation_satisfies_the_contract`, `test_the_whole_plan_runs_when_the_e7_observation_matches` |
| one mismatch per field category is inconclusive | `test_one_mismatch_in_each_e7_field_category_is_refused` (12) |
| missing, duplicated, unreadable, malformed, unexpected — fixed classifications | `test_every_refusal_category_is_a_fixed_safe_classification` (6), `test_a_missing_e7_key_names_the_reviewed_key_and_nothing_else` (10) |
| a mismatch stops every `E7`-attributed dependent operation | `test_an_e7_mismatch_stops_every_dependent_operation`, `test_e7_exiting_zero_is_not_a_pass` (11) |
| the securebits comes from the real observation path, not a vector or `P-01`/`P-02` | `test_the_e7_vector_carries_no_securebits_option_to_infer_from`, `test_the_case_program_reads_e7s_securebits_through_prctl`, `test_p01_and_p02_are_retained_unchanged_and_are_not_the_e7_observation` |
| the ordering is checked, not described | `test_the_e7_observation_precedes_every_root_case_program_operation`, `test_the_generator_refuses_a_plan_whose_e7_observation_is_late` |
| the facts ship unconfirmed in the submitted tree | `test_the_facts_ship_unconfirmed_in_the_tree_being_submitted` (read from the source, so a monkeypatch cannot make it pass) |
| the manifest pins the facts and their state | `test_the_manifest_pins_e7s_facts_and_their_confirmed_state`, `test_the_manifest_digest_changes_when_a_reviewed_e7_fact_changes` |

The reviewed `E7` facts the tests inject — `harness_fixtures.REVIEWED_E7_FACTS` —
are **deliberately synthetic and deliberately not §2.13.5c's row**: the masks are
`0x1234` and the supplementary set is `0,4242`, so a contract that had fallen
back to `DOCUMENTED_ROOT_MASK` fails rather than passes. `uid` and `gid` are `0`
because `E7` **is** root and no honest fixture makes it otherwise. **Nothing in
the suite is a fact about `oracle-test`.**

**No test changes this process's credentials, capabilities or securebits, and no
test requires root.** The `prctl` cases are driven across the same fixed injected
native boundary R12 introduced.

## R13.5 The vocabulary that encoded the defect, replaced

| Was | Is | Why |
|---|---|---|
| `expectations.CONSTRUCTED_IDENTITIES` — the seven | `expectations.CAPSH_CONSTRUCTED_IDENTITIES` — the seven | accurate: a statement about how they are produced |
| — | `expectations.OBSERVED_IDENTITIES` — all eight | the set a `CASE_IDENTITY` step may name, which is what the old name read as |
| `expectations.identity_contract()` | `expectations.constructed_identity_contract()` | it builds the `capsh` construction's contract and refuses `E7` **because `E7`'s source is different**, not because `E7` is unobservable |
| — | `expectations.root_identity_contract()` | `E7`'s |
| — | `expectations.ROOT_IDENTITY`, `expectations.IDENTITY_KEYS` | `E7` was spelled as a literal in five places, each of which excluded it |
| `plan.CONSTRUCTED_IDENTITY` = `E[1-6]\|E8` | `plan.OBSERVED_IDENTITY` = `E[1-8]`, plus `plan.ROOT_IDENTITY_NAME` | the validator no longer refuses the step the design requires |
| `EvidenceIdentity.expected_masks()` returning `E7`'s documented row | it raises for `E7`; `capability.documented_root_masks()` returns the documented row | a documented host reading is not a derivation and is not an executable expectation |

**`E7` is not described as `capsh`-constructed anywhere.** The old name was not
made to fit; it was replaced.

## R13.6 What was preserved, and asserted so

Unchanged, byte for byte or in substance, with their whole R11 and R12 test sets
still passing:

* the interpreter path and the exact `-I -S` prefix (`INTERPRETER_PATH`,
  `INTERPRETER_FLAGS`);
* the closed case-program verbs, arities, modes and path grammar (`CASE_VERBS`,
  `OPEN_MODES`, `WRITE_MODES`, `GENERATION_LINK_NAME`, `validate_case_vector`) —
  **no verb was added**; `P-06` uses the existing `identity` verb;
* `plan.PERMITTED_EXECUTABLES`;
* the delegated `capsh` and `systemd-run` tail validation;
* the four late-bound names and the three substitution sites per constructed
  identity — `P-06` adds none, and the plan still declares **21**;
* the symlink target and the `rm --force` cleanup primitive;
* target-root validation, including `root_or_contained_path()`;
* the `ctypes` exception — still one file, one function, one literal
  `PR_GET_SECUREBITS` operation; `execution/case_program.py` was **not modified
  in this revision at all**;
* `materialization.py` and `execution/materializer.py`, untouched;
* the arming rules — the boundary and the materializer are still constructed
  armed in exactly one place each, inside the CLI's `--execute` branch; and
* the authority required to establish reviewed target facts and to execute the
  harness.

`P-05`'s eleven-key contract and its enforcement point are unchanged.
`ExecutingRunner._expectation_refusal` is unchanged; it now selects one more
contract through the same `contract_for()` call.

## R13.7 Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/capability.py` | `E7_TARGET_FACTS` and their sentinel, shapes and predicates; `e7_expected_values()`; `documented_root_masks()`; `expected_masks()` refuses `E7`; `declared_identity` takes the documented row for `E7` |
| `tools/phase_5_0_evidence/expectations.py` | `ROOT_IDENTITY`, `IDENTITY_KEYS`, `OBSERVED_IDENTITIES`, `CAPSH_CONSTRUCTED_IDENTITIES`; `root_identity_contract()`; `identity_contract` → `constructed_identity_contract`; the twelve-key guard in `ObservationContract`; `contract_for` dispatches on `E7` |
| `tools/phase_5_0_evidence/plan.py` | `OBSERVED_IDENTITY` = `E[1-8]`; `ROOT_IDENTITY_NAME`; an `E7` step may declare no binding site and must run as `root` |
| `tools/phase_5_0_evidence/concrete_plan.py` | `P-06`; `_validate_root_identity_ordering()` and its call in `build_concrete_plan`; `_case_program_verb()`; the Band-5 and `P-05` prose corrected |
| `tools/phase_5_0_evidence/execution/executor.py` | gate 4 — the `E7` facts; the gate docstring corrected from five to six |
| `tools/phase_5_0_evidence/review_manifest.py` | `expectations.root_identity`; `case_identity` restricted to the seven by name; facts read through the module; `MANIFEST_VERSION` **5** |
| `tools/phase_5_0_evidence/execution/cli.py` | renders `E7`'s row, its ten facts and their state; `_unconfirmed_target_facts()` in the dry-run summary |
| `tools/phase_5_0_evidence/__init__.py` | the `capability` row; `HARNESS_VERSION` **0.6.0-pre-execution** |
| `tests/phase_5_0_evidence/test_root_identity.py` | **new.** 90 cases |
| `tests/phase_5_0_evidence/harness_fixtures.py` | `REVIEWED_E7_FACTS` and `supply_reviewed_e7_facts()` |
| `tests/phase_5_0_evidence/test_expectations.py` | the renamed set and constructor; `test_e7_has_no_identity_contract` replaced by `test_e7_has_a_contract_of_its_own_and_not_the_constructed_one`; the plan's identity set is now all eight; the module docstring's scope corrected |
| `tests/phase_5_0_evidence/test_concrete_plan.py` | `P-06` joins the case-program prerequisites; its position asserted |
| `tests/phase_5_0_evidence/test_bands.py` | `expected_masks()` refuses `E7`; the documented row read through its own accessor |
| `tests/phase_5_0_evidence/test_case_program.py` | the derived-securebits sweep is over the seven; the `E7` range is in `test_root_identity.py` |
| `tests/phase_5_0_evidence/test_executor.py`, `test_executor_cleanup.py`, `test_late_binding.py` | the `E7` facts in the autouse fixture |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | **regenerated** |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | **regenerated** |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section |
| `docs/review/Handover information` | R13 returned to Codex |

**No other file in the worktree was touched.** `git status` is what it was before
this work started, plus one new test module. `execution/case_program.py`,
`capture.py`, `case_runtime.py`, `binding.py`, `cleanup.py`, `materialization.py`,
`targets.py`, `approved_target.py` and every band module were not modified.

## R13.8 The generated artifacts

Both were generated **twice** and compared byte for byte: `cmp` reported no
difference for either the concrete plan or the review manifest, and the dry-run
stdout was identical too. All **28** covered-source digests were independently
re-hashed from the tree and compared with the manifest's own `source_digests` —
**no mismatch**. Neither artifact was hand-edited.

| Fact | Value |
|---|---|
| Manifest schema version | **5** (was 4) |
| Harness version | **0.6.0-pre-execution** (was 0.5.0-pre-execution) |
| Evidence schema version | 3, unchanged |
| Steps | **116** (was 115) |
| Expectation contracts | **9** (was 8) |
| Binding sites | 21, unchanged |
| Materializations | 2, unchanged |
| Mutations | 43, unchanged |
| Cleanup steps | 46, unchanged |
| Unresolved design conflicts | **0** |
| `executable` | **True** |
| Review-manifest digest, R12 (**superseded**) | `6f555c13f4b7f19eb440886cb08e3709057f3776af9d088da51880e82c87d733` |
| **Review-manifest digest, R13** | `057c84a96225bfb8e1b02f4502619015b06b8dbc050342423ade25be4f3b7ae5` |
| Target confirmation token (unchanged) | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#ceb58ad1f9f0e070` |

Both artifacts were produced by

```sh
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

which is a dry run — it prints what would run and starts nothing. **The R12
digest `6f555c13…` is superseded and must never be passed to `--execute`.** The
R13 digest is **review material only, not execution authority**, and the executor
refuses this plan on twelve unsupplied reviewed target facts regardless of what
digest it is given.

The manifest version moves to 5 because `expectations` changed shape:
`case_identity` is now the seven `capsh` constructs by name, and a new
`root_identity` block carries `E7`'s user, its ten facts and each fact's
confirmed state. A digest approved under version 4 covered a plan in which `E7`
had no identity step and no compared observation at all; that is a different
plan, so it stops matching rather than being reinterpreted.

## R13.9 Verification — exact results from the final R13 tree

Every figure was produced from the tree being submitted, **serially**, with the
documented interpreters and `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`
exported.

| # | Command | Result |
|---|---|---|
| 1 | `venv … pytest -q -rs tests/phase_5_0_evidence` | **1088 passed** |
| 2 | `venv-web … pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **1147 passed** |
| 3 | `venv … pytest -q -rs tests/test_database_backup_restore.py tests/test_filesystem_layout.py` with the seven deselected | **56 passed, 7 deselected** |
| 4 | `venv … pytest -q -rs tests/test_*.py` with the same seven deselected | **3153 passed, 7 deselected**, 1 warning (`audioop` deprecation, pre-existing) |
| 5 | `venv-web … pytest -q -rs tests/web` | **2840 passed, 80 skipped** — the documented figure |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `venv … -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| 7 | `venv-web … -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| 8 | `git diff --check` | clean |

The evidence suite went from 998 to **1088** — the 90 cases in
`test_root_identity.py`. Runs 3 and 4 are unchanged from R12 because
`tests/test_*.py` does not match the `tests/phase_5_0_evidence/` directory; the
figure is reported from this tree, not carried over.

**The web suite's 80 skips are the documented figure**, and `-rs` printed the
reason for each. They are two reasons and eighty cases, both matrix modules
declining to re-assert a permitted cell the per-route success case already
covers: 54 in `tests/web/test_p3_2_matrix.py:155` and 26 in
`tests/web/test_p3_3_matrix.py:198`, each *"permitted cells are asserted by the
per-route success cases"*. **No skip is an environment gate**, which matters
because the two facts `.agents/AGENTS.md` names — the wrong interpreter reports
`No module named pytest`, and an unexported `TEST_DATABASE_URL` yields roughly
*1141 passed, 1362 skipped* and still exits 0 — make a green run easy to produce
and worthless. `TEST_DATABASE_URL` was exported for every run above.

### The seven destructive cases, deselected by authority

The same seven as R8 §R8.8, R9 §R9.6, R10 §R10.6, R11 §R11.8 and R12 §R12.9,
deselected **by node id** so pytest reports them as deselected rather than
skipping them silently. All are in `tests/test_database_backup_restore.py`:

1. `test_the_drill_accepts_an_explicit_unix_socket_directory`
2. `test_backup_and_restore_round_trip_preserves_data`
3. `test_the_drill_leaves_the_runtime_roles_privileges_intact`
4. `test_the_drill_fails_when_the_privilege_state_is_not_restored`
5. `test_the_drill_preserves_pristine_schema_ownership_and_privileges`
6. `test_the_drill_fails_when_schema_privileges_are_not_restored`
7. `test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure`

**They are not claimed to pass against this tree**; they need a
maintainer-authorized run. Nothing in R13 touches the drill, its script or its
documentation.

### What was not run, and could not be

* **The evidence harness itself.** No `--execute`, no armed `SubprocessBoundary`,
  no armed `SystemMaterializer`, no generated vector, no `capsh`, no
  `systemd-run`, no `chattr`, no `install`, no `psql`.
* **The destructive backup/restore drill**, and the seven cases above.
* **Every privileged or mutation-bearing command in the plan** — all 43 declared
  mutations and all 46 cleanup steps exist only as reviewed argument vectors.
* **Any database operation** beyond the suite's own disposable `freedom_test`.
* **`prctl(PR_GET_SECUREBITS)` against a constructed identity.** The only real
  call in the suite is a read against this unprivileged test process, asserting
  shape and range and not a particular securebits word.

## R13.10 No host inspection and no host mutation

**`oracle-test` was not contacted.** No SSH, no `ssh`, `scp`, `rsync`, `ansible`
or any other remote invocation was run; no socket was opened to `138.2.182.39`;
nothing was read from it and nothing was written to it. No interpreter digest, no
resolved path and no `E7` fact was read from any host — this one included: the
suite's `REVIEWED_E7_FACTS` are literals chosen in
`tests/phase_5_0_evidence/harness_fixtures.py`, and the new module was written
under `test_no_execution.py`'s existing suite-wide guards, which scan **every**
`*.py` in `tests/phase_5_0_evidence/` and assert that no module imports `pwd` or
`grp`, names `subprocess`, reads `os.environ` or `TEST_DATABASE_URL`, or carries
the `database` marker. Those guards do not cover `os.getuid` or file reads, and
this handback does not claim they do: `test_root_identity.py` reads two
repository sources — `capability.py`, to assert the ten facts ship
`UNCONFIRMED` in the tree being submitted, and `expectations.py`, to assert
`root_identity_contract`'s body names no observation — and reads nothing else and
no host state at all. Its `prctl` cases are driven across the same fixed injected
native boundary R12 introduced; no test changes this process's credentials,
capabilities or securebits.

No `.env`, service-account JSON, token, OAuth secret, database URL or Foundry
credential was read, printed, committed or modified. No production data, live
Discord, Sheets, Foundry or external service was contacted.

The worktree is unchanged apart from the files in §R13.7. Nothing was reset,
reverted, staged, committed or pushed; the pre-existing dirty worktree — the
modified `models/skills.py`, `infra/postgresql/backup-restore-drill.sh`, the
several documentation files and the untracked review prompts — is exactly as it
was.

## R13.11 Judgement calls, residuals and newly discovered dependencies

1. **Where `P-06` sits, and what counts as an `E7`-attributed operation.** The
   prompt requires the observation to precede *"every E7-attributed dependent
   operation"*. I read that as **every case-program operation the root harness
   performs**, because §2.13.5c's assertion contract is about the case program's
   processes, and I excluded two classes explicitly:
   * **the two observation verbs**, which change nothing, take no path and report
     nothing identity-dependent — `P-05` in particular runs first on purpose, so
     the identity is observed through an established interpreter; and
   * **the earlier root steps**, which are Band 0's discovery, Band 2's
     provisioning, Band 3's `install`/`chattr` construction and `P-01` … `P-04`.
     They establish the target and the case program rather than asserting what an
     identity could or could not do, and the plan attributes no evidence case to
     `E7` among them. No observation could precede them in any event: the case
     program does not exist until Band 3 installs it, which is the same
     constraint `P-03`, `P-04` and `P-05` already sit under.

   **This is a judgement, and it is the one place a reviewer might reasonably
   draw the line differently.** If Codex holds that the provisioning and
   hierarchy-construction steps are also `E7`-attributed, the observation cannot
   simply move earlier — the case program would not exist — and the design
   question is whether a **second** observation is needed after installation or
   whether those steps need a different attribution. I did not decide that;
   the check and this paragraph state the boundary rather than hide it.

2. **`E7`'s uid, gid and groups are reviewed target facts, not constants.** It
   would have been easy to write `uid == 0` and `gid == 0` as literals, and it
   would have been wrong twice over: the prompt requires each environment value
   to have an explicit reviewed target-fact constant, and the harness's *complete
   supplementary group set* is genuinely a property of how the process was
   launched. `uid` and `gid` being `0` on the target is very likely and is still
   a statement about the target that a reviewer should verify rather than one the
   harness should assume.

3. **`expected_masks()` now raises for `E7`.** This is slightly beyond the
   literal ask, and it is why: the prompt forbids the documented 2026-08-31 row
   from becoming an executable expectation, and leaving that row reachable from
   the same method that produces the other seven identities' expectations makes
   the prohibition a convention rather than a property. `declared_identity()` —
   the records tier's builder, used by the band classifier — takes
   `documented_root_masks()` instead, so `CAP-E7-ENVIRONMENT` is unaffected.

4. **The executor's gate count was five in prose and six in code.** R12 added the
   resolved-path gate without updating the docstring's enumeration. Corrected
   here to six; the code's behaviour did not change.

5. **`P-06`'s evidence case ids.** It carries `CAP-E7-IDENTITY` — new — beside
   the existing `CAP-E7-ENVIRONMENT`. The two are different claims: the
   environment case compares the **documented** mask with the host's PID-1 mask
   and reports `INCONCLUSIVE` on disagreement; the identity case compares the
   **reviewed target facts** with what the final interpreted process actually
   reports. Both are retained.

6. **Newly discovered dependency: ten more unconfirmed reviewed target facts.**
   The harness now refuses on twelve rather than two. That is a larger
   operational block than R12's, and it is the honest consequence of the finding:
   `E7`'s identity was previously *assumed*, and an assumption costs nothing to
   state. What is needed is in §R13.3.

7. **Residual, unchanged from R12 and restated because it is still open.**
   §R11.9 items 3–6 are untouched and nothing here rules on them. `A-5.0-5`
   remains unconfirmed. `OD-62` remains open. The C-2 Option-B ruling, the C-3
   symlink boundary and the C-5 late-binding design are as R11 left them and as
   R12 preserved them.

8. **What this revision does not claim.** It does not claim the plan is correct
   evidence — no case has run. It does not claim `E7`'s reviewed facts are right
   — none has been stated. It does not claim the seven destructive cases pass. It
   does not close a finding, move a readiness item, confirm an assumption or
   discharge an operational check.

## R13.12 Status, stated exactly

* **EH-R12-1: remediated.** `E7` is a `CASE_IDENTITY` step with the exact direct
  Option-B `identity` vector, run as the harness's root identity, ordered before
  every root case-program operation, and compared against the same twelve
  reviewed keys as the other seven. `P-01` and `P-02` are retained unchanged as
  separate preflight evidence.
* **The plan is fully specified.** Zero unresolved design conflicts,
  `executable: True` on paper. **That is not permission to execute it.**
* **It is not authorized to run, and it cannot.** Six gates; **two of them refuse
  today**, on twelve unsupplied reviewed target facts between them.
* **Package 5.0 remains `not ready`. P5.0-R5 remains Blocking.** No finding is
  closed, no readiness item moves, no assumption is confirmed, and no operational
  check is discharged by this submission.

## R13.13 Request for Codex independent R13 pre-execution review

Please review, in this order:

1. `capability.E7_TARGET_FACTS`, its shapes, `e7_expected_values()` and
   `documented_root_masks()` — that no documented host value can reach an
   executable expectation, and that the fact set is fail-closed;
2. `expectations.root_identity_contract()` and the twelve-key guard in
   `ObservationContract.__post_init__` — that `E7`'s contract is neither narrower
   than the others' nor able to learn a value from the observation it judges;
3. `concrete_plan._case_program_prerequisites`'s `P-06` and
   `_validate_root_identity_ordering()` — the vector, the absence of bindings,
   and specifically **the two exclusions in §R13.11 item 1**, which is the
   judgement call in this submission;
4. `ExecutingRunner.__post_init__` gate 4 — that it refuses at construction,
   before the boundary exists;
5. `tests/phase_5_0_evidence/test_root_identity.py` — that the matrix is complete
   and that no test states a fact about `oracle-test`; and
6. the regenerated `docs/review/phase-5-0-evidence-harness-concrete-plan.md` §3.1b
   and the manifest's `expectations.root_identity`.

Then, if the finding is disposed of, the outstanding decision is the operational
one in §R13.3: whether to authorize an Operations Owner reading of the twelve
reviewed target facts on `oracle-test`, and by whom they are independently
verified. **OD-62 remains open until the required operational evidence and
independent review exist.**

---

# R12 — the semantic expectations, and the one native call

Date: 2026-09-07

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r12-prompt.md`. That
authority covers unprivileged code, focused-test, controlled-documentation and
generated-artifact work only. **It does not authorize `--execute`, an armed real
process boundary or materializer, execution of a generated vector, SSH, host
inspection or mutation, any privileged or mutation-bearing command, mutation of
`oracle-test`, a database operation, the destructive backup/restore drill,
Package 5.0 product implementation, migration `0014`, deployment, cutover,
OD-62's binding ruling, or Package 5.1+. None of those occurred.**

Outcome: **EH-R11-1 and EH-R11-2 are remediated.** R11's accepted Option-B
vector grammar, C-3 symlink boundary, C-5 late binding, C-1 root boundary and
C-4 materializer are preserved unchanged. The generated plan still reports zero
unresolved items and `executable: True`. Nothing was executed. No finding is
closed by this submission, no readiness item moves, no assumption is confirmed,
no operational check is discharged, and Package 5.0 remains `not ready`;
P5.0-R5 remains Blocking.

## R12.0 Both findings, conceded before their corrections

**EH-R11-1 is correct and is conceded without qualification.** `P-05` ran the
reviewed vector, the case program printed eleven facts about the runtime, and
`capture.sanitize` bounded every one of them — and then `ExecutingRunner`
computed `satisfied` from `step.is_satisfied_by(result.exit_status)` and nothing
else. The observation was stored in `StepOutcome.observations` and never read.
A run in which the interpreter was a different executable, its digest a
different value, `isolated=no`, `third_party_importable=yes` or the installed
case program a different file would have been recorded as a **pass**, and the
run would have continued into every dependent case. The R11 handback described
`P-05` as *"the interpreter preflight"*; it was a preflight that compared
nothing.

**EH-R11-2 is correct and is conceded without qualification.** R11 §R11.9 item 2
stated the limitation plainly and treated it as acceptable. It was not: package
plan §2.13.5c's assertion contract names securebits in the same table as the
five capability masks and `NoNewPrivs`, and says it is read from
`prctl(PR_GET_SECUREBITS)` *"because `/proc/self/status` does not report them"*.
Substituting *"a `--secbits=4` option appears in the vector"* asserts an
**intent** communicated to `capsh`, not the **state** of the process after
`execve`. Worse, R11 also derived the rest of the identity from intent: the five
masks and `NoNewPrivs` were captured and, like the runtime facts, never
compared.

Both findings have the same root cause and it is worth naming: the harness had a
sanitation boundary and no comparison boundary. R12 adds the second one, as a
typed, closed, reviewed contract rather than as assertions scattered through the
executor.

## R12.1 EH-R11-1 — how the P-05 expectation is constructed, and where it is enforced

### The contract

`tools/phase_5_0_evidence/expectations.py` is new, planning tier, and is the only
place an expectation is stated. `case_runtime_contract()` returns an
`ObservationContract` over **eleven** expectations — exactly the key set
`capture.CapturePolicy.CASE_RUNTIME` records, which
`test_expectations.py::test_the_contract_covers_exactly_the_capture_policys_key_set`
asserts, so neither half can be edited alone:

| Key | Comparison | Expected value, and its source |
|---|---|---|
| `verb` | text | `runtime` — literal |
| `result` | text | `returned` — literal |
| `interpreter` | text | `case_runtime.INTERPRETER_PATH` |
| `interpreter_real` | text | `case_runtime.EXPECTED_INTERPRETER_REAL_PATH` — **a reviewed target fact, new in R12** (§R12.6) |
| `python_version` | text | `case_runtime.INTERPRETER_PYTHON_VERSION` |
| `interpreter_sha256` | text | `case_runtime.EXPECTED_INTERPRETER_SHA256` — the R11 reviewed target fact |
| `isolated` | text | `yes` |
| `no_site` | text | `yes` |
| `third_party_importable` | text | `no` |
| `case_program` | text | `case_runtime.case_program_path(target)`, from the **approved target's** validated root |
| `case_program_sha256` | text | the **review manifest's covered-source digest** for `case_runtime.CASE_PROGRAM_SOURCE` |

### Why none of it is circular

The prompt asked for the manifest-derived case-program digest to be bound
without creating a circular self-approval. It can be, and the sequencing is what
makes it so. `ExecutingRunner.__post_init__` does this, in this order:

1. builds `ReviewManifest.build(self.plan, self.source_bytes)` — the CLI has read
   exactly `COVERED_SOURCES` and nothing else;
2. **refuses** unless the reviewer's supplied digest matches the aggregate over
   those bytes; and
3. only then binds `self._case_program_sha256 = manifest.digest_for(
   CASE_PROGRAM_SOURCE)`.

So the expectation is the digest of bytes the reviewer has already approved, by
the same gate that already decided the run may proceed at all. It is not a hash
the executor computes for itself of an unapproved file, it is not read back from
`<root>/bin/case`, and it is not taken from `P-05`'s output. `install` copies
bytes, so the source digest **is** the installation digest — the property R10
showed a compiled program cannot have — and that is what removes the need for a
third reviewed fact.
`test_expectations.py::test_the_comparison_uses_the_manifests_digest_not_the_installed_file`
changes the reviewed bytes and shows the preflight then fails on
`case_program_sha256`.

The two interpreter facts stay externally supplied. Nothing in this change reads
`oracle-test`, and `test_expectations.py::test_both_shipped_interpreter_facts_are_unconfirmed_in_the_source`
asserts the sentinels against the source.

### Where the comparison happens

`ExecutingRunner._expectation_refusal()` is called from `_run_steps` on the
`CommandResult` **the executor actually receives**, immediately after capture
sanitation and before `satisfied` is computed:

```python
expectation_refusal = ""
if not result.timed_out and not result.launch_failure:
    expectation_refusal = self._expectation_refusal(step, argv, result)
satisfied = (
    not result.timed_out
    and not result.launch_failure
    and step.is_satisfied_by(result.exit_status)
    and not expectation_refusal
)
```

There is no path from a contract-bearing step to `StepOutcome.satisfied`,
`state.satisfied_steps` or any dependent execution decision that does not pass
through the comparison. A step whose contract cannot be **built** — a
`CASE_IDENTITY` step naming no identity, an unknown identity, or a bound vector
the numeric options cannot be read out of — is refused with
`EXPECTATION_NOT_CONSTRUCTED` rather than treated as having no contract. It is
not special-cased in rendering, in the handback prose or anywhere else.

## R12.2 The complete mismatch/refusal matrix

`ObservationContract.check()` returns the empty string only when every expected
key is present **exactly once**, is readable, and equals its expected value.
Everything else is one of six fixed classifications:

| Condition | Classification | Names the key? |
|---|---|---|
| no observation at all | `NO_OBSERVATIONS` | — |
| the recorded observations are not sanitized name/value pairs | `MALFORMED_OBSERVATIONS` | — |
| a name outside the reviewed key set is present | `UNEXPECTED_KEY` | **no** — the name is host-supplied |
| an expected key is absent | `MISSING_KEY` | yes, the reviewed key |
| an expected key appears twice | `DUPLICATED_KEY` | yes, the reviewed key |
| a value is empty or `unreadable` | `UNREADABLE_VALUE` | yes, the reviewed key |
| a value is readable and different | `UNEQUAL_VALUE` | yes, the reviewed key |
| the contract could not be constructed | `EXPECTATION_NOT_CONSTRUCTED` | — |

**No classification carries an observed path, digest, identifier, value or
exception text.** The key names it does carry are members of the contract's own
declared set — reviewed vocabulary, not host output — and
`test_expectations.py::test_no_refusal_names_an_observed_value` proves a planted
path, a planted digest and an unexpected key name each fail to appear.

**One capture-boundary change was needed.** R11's `_case_observations` kept the
**first** occurrence of a repeated key and dropped the rest silently, so a
duplicate was invisible to anything downstream. It now marks that key
`unreadable`, which is an INCONCLUSIVE observation — a result — where a silently
preferred first value was a result nobody could tell apart from a clean one.
This narrows the boundary; it broadens nothing.

### Tests, against the list the prompt names

Every case below is in `tests/phase_5_0_evidence/test_expectations.py`, and each
is proved **twice**: against the contract directly, and end-to-end through
`ExecutingRunner` over the real plan with `P-05` exiting **0**.

| Required case | Test |
|---|---|
| no observations | `test_no_observation_at_all_is_refused`, `test_p05_exiting_zero_is_not_a_pass[no observations]` |
| one missing key | `test_one_missing_key_is_refused` (parameterized over all eleven) |
| a duplicate key | `test_a_duplicated_key_is_refused` (all eleven) |
| an unreadable value | `test_an_unreadable_value_is_refused`, `test_an_empty_value_is_refused` (all eleven) |
| wrong interpreter path | `test_every_wrong_value_is_refused[interpreter]` |
| wrong resolved path | `…[interpreter_real]` |
| wrong Python version | `…[python_version]` |
| wrong interpreter digest | `…[interpreter_sha256]` |
| `isolated=no` | `…[isolated]` |
| `no_site=no` | `…[no_site]` |
| `third_party_importable=yes` | `…[third_party_importable]` |
| wrong case-program path | `…[case_program]` |
| wrong case-program digest | `…[case_program_sha256]` |
| the exact complete set passes | `test_the_exact_complete_observation_satisfies_the_contract`, `test_the_whole_plan_runs_when_every_observation_matches` |
| no dependent case reaches the boundary after a mismatch | `test_no_dependent_case_reaches_the_boundary_after_a_preflight_mismatch` |

The last one asserts the property directly rather than by inference: it takes the
step ids **after** `P-05` in the generated plan and asserts that the injected
boundary was never called for any of them and that no `StepOutcome` exists for
any of them.

## R12.3 EH-R11-2 — how the final securebits is read and compared

### Read

`execution/case_program.py` gains `_prctl_get_securebits()`, which calls
`prctl(PR_GET_SECUREBITS)` inside the final interpreted case-program process —
after `capsh` has applied the seven-step credential and capability construction
and after `execve`, and before the operation whose attribution depends on that
identity, which is a **later step**, because the `identity` verb performs no
operation at all.

The call returns the raw pair `(return value, errno)` and **decides nothing**.
`_securebits_text()` applies the three rules:

1. `-1` is the failure convention — the errno read beside the call is reported by
   **name** from `errno.errorcode`;
2. a non-integer or a boolean is refused; and
3. a value outside `0 … SECUREBITS_MAX` (`0xff`; `securebits.h` defines bits
   0 … 7) is refused, because it is not a securebits word.

That split is deliberate: it puts the range check before the value can be
emitted, and it makes every failure branch drivable across a fixed injected
boundary without needing a kernel that fails on demand.

A refusal raises `ObservationUnavailable`, which `main()` reports as
`verb=…, result=unobserved, errno=<name|none>` and **exit 66**
(`EXIT_OBSERVATION_UNAVAILABLE`, mirrored in `case_runtime`). 66 is distinct from
every refusal code and is in no step's `satisfying_statuses`, so *"the identity
could not be observed"* can never be recorded as *"the kernel refused the
operation"*, as *"the vector was wrong"* or as a pass. The sanitized observation
of that output carries `verb` and `result` and no reviewed identity key, so the
contract additionally refuses it for a missing key.

`CapturePolicy.CASE_IDENTITY` gains `securebits`, shaped by a new, deliberately
narrow `securebits` pattern: one or two lower-case hexadecimal digits. A
sixteen-digit value — the shape a capability mask has — is `unreadable` here,
because a sixteen-digit value would be evidence that something other than
securebits was read.

### Compared

`expectations.identity_contract()` states **twelve** expectations per identity —
again exactly the policy's key set:

| Key | Comparison | Source of the expectation |
|---|---|---|
| `verb`, `result` | text | literals `identity` / `returned` |
| `uid`, `gid` | number | the **bound** vector's `--uid=` / `--gid=` |
| `groups` | number **set** | the bound vector's `--groups=` |
| `cap_inh`, `cap_prm`, `cap_eff`, `cap_bnd`, `cap_amb` | hex, by value | `EvidenceIdentity.expected_masks()` |
| `no_new_privs` | number | `0` |
| `securebits` | hex, by value | `EvidenceIdentity.expected_masks()['securebits']` = `SECBIT_NO_SETUID_FIXUP` = `0x4` |

The three numeric credentials come from the vector rather than from a constant
because the four disposable names do not exist until Band 2 creates them — that
is C-5's whole premise. The vector is an **independent source from the
observation**: its numbers were resolved by the injected NSS boundary from the
four reviewed names, before `execve`, and the observation is what the kernel
reports afterwards. Masks are compared **by value**, so a zero-padded
`0000000000000200` and `200` are the same mask and `40` is still not `4`; groups
are compared as a set, because the kernel holds a set and recording the order
would compare something §2.13.5c does not state.

`CommandStep` gains `identity_name`, required for a `CASE_IDENTITY` step and
forbidden on any other, validated against a closed shape at construction, and
**pinned in the review manifest** — so which contract applies to which step is
something a reviewer approves rather than something the executor infers from a
step id.

### Tests, against the list the prompt names

| Required case | Test |
|---|---|
| `PR_GET_SECUREBITS` returning `0x0` and `0x4` | `test_case_program.py::test_the_reviewed_securebits_values_are_reported_as_bounded_hex` |
| `prctl` returning `-1` | `test_a_failed_prctl_reports_its_errno_through_the_fixed_failure_path` (a named errno **and** an unmapped one → `UNKNOWN`) |
| malformed, negative or out-of-range output | `test_a_malformed_or_out_of_range_securebits_is_refused` (12 cases, including a boundary answer that is not the pair the native call returns) |
| missing `securebits` capture | `test_expectations.py::test_a_missing_or_unreadable_identity_value_is_refused` |
| malformed `securebits` capture | `test_a_malformed_securebits_capture_is_refused_by_the_capture_boundary` |
| every E1…E8 expected securebits | `test_every_identitys_expected_securebits_is_the_derived_value`, `test_case_program.py::test_every_constructed_identitys_expected_securebits_can_be_reported` — **corrected in R13: these exercised the seven `capsh`-constructed identities, not eight. `E7` is `test_root_identity.py`** |
| one mismatch per identity field category | `test_one_mismatch_in_each_identity_field_category_is_refused` — uid, gid, groups, each of the five masks, `NoNewPrivs`, securebits, plus verb and result |
| a mismatch makes the case inconclusive and stops its dependent operation | `test_an_identity_mismatch_stops_the_run_before_its_dependent_operation`, parameterized over all seven constructed identities |
| exit 66 reaches the run | `test_an_unobservable_securebits_makes_the_identity_verb_exit_66`, `test_an_out_of_range_securebits_exits_66_and_names_no_errno` |
| no other module can import `ctypes` or make a native call | `test_no_execution.py`, §R12.4 |

**No test changes this process's credentials, capabilities or securebits, and no
test requires root.** Setting securebits is `PR_SET_SECUREBITS`, which needs
`CAP_SETPCAP`; the program contains no setter to call, and
`test_the_native_boundary_is_read_only_and_has_no_setter` asserts — over the
source with comments and string literals removed — that neither
`PR_SET_SECUREBITS`, nor `capset`, nor the number 28 appears anywhere in the
code, and that the file's only `PR_*` constant is `PR_GET_SECUREBITS = 27`. The
one test that calls the real `prctl` is a **read** against this unprivileged test
process and asserts the value's shape and range, not a particular securebits
word.

## R12.4 The exact scope of the `ctypes` exception, and its mechanical guard

The exception is **one file, one function, one operation**. `ctypes` remains a
member of `FORBIDDEN_IMPORTS` for the whole planning tier and for every execution
tier module but `case_program.py`, and `test_no_execution.py` now asserts each of
these:

| Guard | Test |
|---|---|
| only `case_program.py` may import `ctypes` | `test_only_the_boundary_module_may_import_subprocess` (extended) |
| no planning-tier module may import it, by `import` or `from` | `test_no_planning_tier_module_imports_ctypes` |
| no other module in **either** tier may even name `ctypes`, `cdll`, `CDLL`, `windll`, `pythonapi`, `dlopen`, `LoadLibrary`, `restype` or `argtypes` in code | `test_no_module_but_the_case_program_performs_a_native_call` |
| `ctypes` is used through five permitted attributes only — `CDLL`, `c_int`, `c_ulong`, `get_errno`, `set_errno`; `cast`, `POINTER`, `memmove`, `string_at`, `pythonapi`, `addressof` are refused | `test_the_native_call_is_the_literal_prctl_get_securebits_and_nothing_else` |
| exactly one `CDLL` call, its argument the **literal `None`** (the process's already-loaded C runtime — no library is named and none can be supplied), with `use_errno=True` as a literal | same |
| exactly one symbol bound on the loaded handle, and it is the literal `prctl` | same |
| both halves of a fixed signature (`argtypes`, `restype`) are declared | same |
| exactly one invocation, its first argument the literal `PR_GET_SECUREBITS` **name** and every remaining argument a literal `0`; no keywords | same |
| `PR_GET_SECUREBITS` is a module-level literal constant equal to 27 | same |
| the native function takes **no argument at all**, so no library, symbol, operation or raw argument can be passed to it | same |
| `getattr`/`setattr`/`delattr` are forbidden outright in the execution tier, and `getattr` is permitted in the planning tier only over a declared dataclass instance | `test_no_module_looks_a_symbol_up_by_name` |
| `globals`, `locals`, `vars`, `importlib`, `__import__`, `sys.modules` and `__builtins__` are refused in both tiers | same |

There is no reusable arbitrary-FFI helper: `_prctl_get_securebits()` takes
nothing, returns a pair of `int`s, and is called from one place.

`test_no_module_looks_a_symbol_up_by_name` replaces a blanket ban that would have
been false. The planning tier already used `getattr` in four places over its own
dataclasses — `approved_target`'s field-for-field comparison, `records`'
serialization, `plan`'s and `concrete_plan`'s required-field checks — and none of
those is a symbol lookup. Rather than weaken the rule globally, the guard is
stated per tier and is **stricter** where the native call lives: the execution
tier may not use it at all.

## R12.5 What was preserved, and asserted so

Unchanged, byte for byte or in substance, and their whole R11 test set still
passes:

* the interpreter path and the exact `-I -S` prefix (`case_runtime`'s
  `INTERPRETER_PATH` / `INTERPRETER_FLAGS`);
* the closed case-program verbs, arities, modes and path grammar
  (`CASE_VERBS`, `OPEN_MODES`, `WRITE_MODES`, `validate_case_vector`);
* `plan.PERMITTED_EXECUTABLES`;
* the delegated `capsh` and `systemd-run` tail validation;
* the four late-bound names and the three substitution sites per identity;
* the symlink target and the `rm --force` cleanup primitive;
* target-root validation, including `root_or_contained_path()`;
* `materialization.py` and `execution/materializer.py`, untouched; and
* the arming rules — the boundary and the materializer are still constructed
  armed in exactly one place each, inside the CLI's `--execute` branch.

The **interpreter digest refusal was not converted into a warning**; it is
unchanged, and a second refusal was added beside it rather than a relaxation.

## R12.6 The newly discovered dependency — the expected resolved interpreter path

`P-05` reports `interpreter_real`, and R12 requires every key of that
observation to be compared. `interpreter_real` has no honest derivation:
`INTERPRETER_PATH` names a virtual environment's `bin/python`, which on a normal
CPython venv is a symbolic link to an interpreter **outside** the environment, so
a rule requiring `interpreter_real == interpreter` would refuse the reviewed host,
and a rule deriving the expectation from the observation would be the tautology
`P-05` exists to avoid.

So it is stated from outside, exactly as the digest is:
`case_runtime.EXPECTED_INTERPRETER_REAL_PATH`, a **second reviewed target fact**,
carrying the sentinel `UNCONFIRMED` in this tree, with
`interpreter_real_path_confirmed()` False, the manifest recording
`expected_interpreter_real_path_confirmed: false`, and the executor refusing
before it starts anything.

**What is needed:** the Operations Owner states, and the independent reviewer
verifies on `oracle-test`, the path
`/opt/freedom-blades/runtime/venv-web/bin/python` resolves to. Supplying it edits
a covered source, which changes the manifest digest, which is the re-review the
substitution should trigger — the same property the R11 digest fact has.

The gate is shape-checked as well as presence-checked: a relative path, a `..`
segment, an over-long value or a character the capture boundary strips is refused
as unconfirmed, because an expectation no observation could ever equal is a
preflight that can only fail rather than one that compares.

## R12.7 Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/expectations.py` | **new.** The typed, closed contracts, the four comparisons, the fixed refusal vocabulary, and the two builders |
| `tools/phase_5_0_evidence/execution/case_program.py` | the one native call; `_securebits_text` and its three refusals; `ObservationUnavailable`; `securebits` in the identity verb; `EXIT_OBSERVATION_UNAVAILABLE`; `PR_GET_SECUREBITS`; `SECUREBITS_MAX` |
| `tools/phase_5_0_evidence/execution/executor.py` | `_expectation_refusal` and its call site before `satisfied`; the manifest-derived case-program digest; gate 2b |
| `tools/phase_5_0_evidence/case_runtime.py` | `EXPECTED_INTERPRETER_REAL_PATH` and its sentinel and predicate; `SECUREBITS_MAX`; `EXIT_OBSERVATION_UNAVAILABLE` |
| `tools/phase_5_0_evidence/capture.py` | `securebits` in `CASE_IDENTITY` and its narrow shape; a repeated key is now `unreadable` rather than silently dropped |
| `tools/phase_5_0_evidence/plan.py` | `CommandStep.identity_name`, required for `CASE_IDENTITY` and forbidden elsewhere; `CONSTRUCTED_IDENTITY` |
| `tools/phase_5_0_evidence/concrete_plan.py` | `identity_name` on each `B5-E*`; `P-05` and `B5-E*` expected-result/refusal prose restated as observed rather than assumed |
| `tools/phase_5_0_evidence/review_manifest.py` | `expectations` section; per-step `identity_name`; the two new `case_runtime` facts, `securebits_max` and `exit_observation_unavailable`; `digest_for()`; `expectation_step_count` in the digest; `MANIFEST_VERSION` **4**; `expectations.py` covered |
| `tools/phase_5_0_evidence/execution/cli.py` | renders §3.1b and the resolved-path fact; reports the contract count in the dry run; passes the manifest's source digest to `render_plan` |
| `tools/phase_5_0_evidence/__init__.py` | the module table; `HARNESS_VERSION` **0.5.0-pre-execution** |
| `tools/phase_5_0_evidence/execution/__init__.py` | the tier table's `case_program` row, the `ctypes` paragraph, and the status paragraph |
| `tests/phase_5_0_evidence/test_expectations.py` | **new.** 136 cases: the contract key by key, the identity contract field by field, and the executor end to end |
| `tests/phase_5_0_evidence/harness_fixtures.py` | **new.** The positive observation fixture the three run-driving modules share |
| `tests/phase_5_0_evidence/test_no_execution.py` | `expectations` in the planning tier; the `ctypes` exception and its eleven mechanical clauses; the per-tier `getattr` rule; the suite scan widened from `test_*.py` to `*.py` |
| `tests/phase_5_0_evidence/test_case_program.py` | the securebits observation, the injected native boundary, and the read-only assertion |
| `tests/phase_5_0_evidence/test_executor.py` | gate 2b; the resolved-path shape; `satisfying()` scripts observations; `render_plan`'s third argument |
| `tests/phase_5_0_evidence/test_executor_cleanup.py`, `test_late_binding.py` | the second reviewed fact in the fixture; `satisfying()` scripts observations |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | **regenerated** |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | **regenerated** |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section |
| `docs/review/Handover information` | R12 returned to Codex |

**No other file in the worktree was touched.** `git status` is what it was before
this work started, plus the two new sources and two new test modules.

## R12.8 The generated artifacts

Both were generated **twice** and compared byte for byte: `cmp` reported no
difference for either the concrete plan or the review manifest. All **28**
covered-source digests were independently re-hashed from the tree and compared
with the manifest's own `source_digests` — **no mismatch**; 27 as before, plus
`expectations.py`. Neither artifact was hand-edited.

```
DRY RUN — nothing was executed.
  target                : oracle-test:/var/lib/fb-evidence-p5-0
  steps planned         : 115
  materializations      : 2 (written by nothing; this boundary is not armed)
  binding sites declared: 21 (resolved by nothing; no account database was read)
  expectation contracts : 8 (compared by nothing; no observation was made)
  mutations declared    : 43
  cleanup steps derived : 46
  unresolved conflicts  : 0 (none)
  review manifest digest: 6f555c13f4b7f19eb440886cb08e3709057f3776af9d088da51880e82c87d733
  executable            : True
```

**The R11 digest `dfa61a57…` is superseded** and must never be passed to
`--execute`; `MANIFEST_VERSION` is now 4, so it cannot match in any case. The R12
digest is
`6f555c13f4b7f19eb440886cb08e3709057f3776af9d088da51880e82c87d733`, and **it is
not execution authority either.** It is a value to submit for review, and it will
change again the moment either interpreter fact of §R12.6 and §R11.3 is supplied
— which is the re-review those substitutions should trigger.

The manifest's new `expectations` section pins what a reviewer approves: the
eleven `case_runtime` key/value pairs, and, per constructed identity, the user,
primary group, supplementary groups, five masks, `NoNewPrivs` and securebits. The
three run-resolved numbers are deliberately **not** there — the reviewed vector
pins the four names in `steps[].bindings`, and the numbers exist only in the
bound vector, for the length of one `execve`.

## R12.9 Verification — exact results from the final R12 tree

Every figure was produced from the tree being submitted, **serially**, with the
documented interpreters and `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`
exported.

| # | Command | Result |
|---|---|---|
| 1 | `venv … pytest -q -rs tests/phase_5_0_evidence` | **998 passed** |
| 2 | `venv-web … pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **1057 passed** |
| 3 | `venv … pytest -q -rs tests/test_database_backup_restore.py tests/test_filesystem_layout.py` with the seven deselected | **56 passed, 7 deselected** |
| 4 | `venv … pytest -q -rs tests/test_*.py` with the same seven deselected | **3153 passed, 7 deselected**, 1 warning (`audioop` deprecation, pre-existing) |
| 5 | `venv-web … pytest -q -rs tests/web` | **2840 passed, 80 skipped — the documented figure** |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `venv … -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| 7 | `venv-web … -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| 8 | `git diff --check` | clean |

The evidence suite went from 778 to **998** — 136 new cases in
`test_expectations.py`, plus the securebits and native-boundary cases in
`test_case_program.py` and the guard cases in `test_no_execution.py`. The bot
suite went from 3152 to **3153**; the web suite is unchanged at 2840 with the
documented **80** skips, whose reasons `-rs` printed (54 + 26 permitted-cell
rows asserted by the per-route success cases).

**One methodological note, reported rather than smoothed over.** My first attempt
at runs 4 and 5 overlapped: run 4 was still going in the background when I
started run 5. Both reported failures — 3 failed / 5 errors and 5 failed
respectively. That is finding F-6, which `.agents/AGENTS.md` states explicitly:
the two suites share one disposable database, so a parallel run is not a faster
verification, it is a different one. **The figures in the table above are from
strictly serial re-runs, and they are the ones I am claiming.** The overlapping
run's numbers are not evidence of anything and are recorded here only so nobody
has to wonder what happened.

**The seven destructive drill integration cases are deselected by authority, not
passed and not silently skipped.** They are the same seven named in R8 handback
§R8.8, R9 §R9.6, R10 §R10.6 and R11 §R11.8, deselected by node id, and pytest
reported them as deselected in runs 3 and 4. **The destructive drill was not
run.**

## R12.10 What did not happen

* **No `--execute`.** The CLI's `--execute` branch was not invoked, at any point,
  under any argument. No `SubprocessBoundary(armed=True)` and no
  `SystemMaterializer(armed=True)` was constructed outside the test suite's
  assertions that the unarmed defaults refuse.
* **No generated vector was executed.** No `capsh`, `systemd-run`, `psql`,
  `install`, `chattr`, `useradd` or case-program invocation from the plan ran.
* **No host inspection or mutation.** No SSH. `oracle-test` was neither read nor
  written. Neither interpreter fact was established, and neither could have been
  from this machine.
* **No database operation.** `TEST_DATABASE_URL` names the existing disposable
  `freedom_test` and was used only by the standing suites, exactly as the
  contributor workflow requires.
* **No destructive drill**, no Package 5.0 product implementation, no migration
  `0014`, no deployment, no cutover, no OD-62 ruling, no Package 5.1+ work.
* **No unrelated file touched.** The dirty worktree that existed before this work
  is preserved; nothing was reset, reverted, staged, committed or pushed.
* **No secret, credential, `.env`, service-account file or player datum was read,
  written or serialized.** The one file read outside the repository was
  `/proc/self/status`, by the case program's own identity verb, inside the test
  suite, about the test process.

**One local read is worth naming explicitly, because it is a native call.**
`prctl(PR_GET_SECUREBITS)` runs against **this** process when
`test_case_program.py` exercises the identity verb. It is a read; it changes
nothing; it needs no privilege; and its result on this machine is `0`. No
`PR_SET_SECUREBITS` call exists anywhere in the repository.

## R12.11 Judgement calls and residuals

1. **A second reviewed target fact is a new dependency, not a workaround.** It is
   §R12.6, and it is returned rather than resolved. I considered and rejected
   two derivations: `interpreter_real == interpreter` (refuses a normal venv) and
   *"inside the environment"* (same). Both would have made `P-05` a preflight
   that cannot pass on the reviewed host, which is worse than one that is
   honestly blocked on a stated fact.
2. **The E-identity steps' `StepRole` is unchanged.** They remain `STANDALONE`
   rather than becoming `CONTROL`. The executor stops the run at the first
   unsatisfied step whatever its role, so a mismatched identity already prevents
   every later case from being executed **or** interpreted — which is strictly
   stronger than marking the band's controls failed. Changing the role would
   change a reviewed field for no additional safety, so I left it and am
   flagging it rather than deciding it silently.
3. **The duplicate-key change is a narrowing of an R11 boundary.** R11's
   first-occurrence rule was documented and deliberate; it was also invisible
   downstream. I changed it because a duplicate must be *observable* for the new
   contract to refuse it, and marking the key `unreadable` broadens nothing.
   Codex may prefer a distinct classification; the current one is INCONCLUSIVE,
   which is the same thing the shape check already produces.
4. **The positive observation fixture is production-derived.** The suite's
   `satisfying()` boundaries script the observation from
   `ObservationContract.expected_observations()`, so they cannot prove that the
   real program emits the right keys. That proof is elsewhere and is explicit:
   `test_case_program.py::test_the_identity_verbs_emitted_keys_are_exactly_the_policys_key_set`
   compares `_do_identity()`'s own keys with the policy's, and
   `test_expectations.py::test_the_contract_covers_exactly_the_capture_policys_key_set`
   compares the policy's with the contract's. The three together close the loop;
   any one alone would not.
5. **`harness_fixtures.py` is not a `conftest.py`.** A `conftest.py` would have
   been the one file in the suite directory that the source-level guards' `test_*.py`
   glob did not read. I widened both guards to `*.py` **and** used an explicitly
   imported module, so the shared fixture is scanned like everything else.
6. **§5.2's two errnos for one operation** and the four other residuals of R11
   §R11.9 items 3–6 are unchanged and still open. Nothing here rules on them.
7. **`EXIT_OBSERVATION_UNAVAILABLE` is a new exit status in a reviewed table.**
   66, distinct from 0, 1, 10–16, 64 and 65, and in no step's
   `satisfying_statuses`. It is pinned in the manifest's `case_runtime` section.

## R12.12 Status, stated exactly

* **EH-R11-1: remediated.** `P-05` is a semantic prerequisite. Exit 0 is
  necessary and not sufficient.
* **EH-R11-2: remediated.** Every `E1 … E8` identity's final securebits is read
  by `prctl(PR_GET_SECUREBITS)` inside the exec'd process and compared, along
  with the uid, gid, complete supplementary set, five masks and `NoNewPrivs`.
  **Withdrawn in R13 as false for `E7`.** R12 delivered this for the seven
  `capsh`-constructed identities and excluded the eighth; that was Codex's
  Blocking finding **EH-R12-1**, and it is remediated in §R13. The sentence is
  left standing here, marked, because this section is the record of what R12
  submitted.
* **The plan is fully specified.** Zero unresolved items, `executable: True`.
* **It is not authorized to run, and it cannot.** Five gates; **two of them
  refuse today**, both on unsupplied reviewed target facts.
* **Package 5.0 remains `not ready`. P5.0-R5 remains Blocking.** No finding is
  closed, no readiness item moves, no assumption is confirmed, and no operational
  check is discharged by this submission.

## R12.13 Request for Codex independent R12 pre-execution review

Please review, in this order:

1. `tools/phase_5_0_evidence/expectations.py` — the contract, the comparisons and
   the refusal vocabulary;
2. `ExecutingRunner._expectation_refusal` and its call site — that the comparison
   is on the received `CommandResult`, after sanitation, before satisfaction;
3. `execution/case_program.py`'s `_prctl_get_securebits` /
   `_securebits_text` — the bounded native call;
4. `tests/phase_5_0_evidence/test_no_execution.py` — that the `ctypes` exception
   is asserted rather than asserted-about; and
5. §3.1b of the regenerated concrete plan and the `expectations` section of the
   regenerated manifest — the values themselves.

Then, if you concur, please return the R12 digest
`6f555c13f4b7f19eb440886cb08e3709057f3776af9d088da51880e82c87d733` as reviewed
material only. **Execution still requires a separate maintainer authorization,
and both interpreter target facts before it could start.**

---

# Superseded — R11: conflict C-2 resolved as Option B, and C-3 and C-5 with it

Date: 2026-09-07

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r11-prompt.md`, and the
ruling Peter Duscha accepted on **2026-09-06** — package plan §2.12.2 and
change-log **C-P5.0-AH**, resolving R10's returned conflict **C-2 with Option
B**. That authority covers unprivileged code, focused-test, controlled-
documentation and generated-artifact work only. **It does not authorize
`--execute`, an armed real process boundary or materializer, execution of a
generated vector, SSH, host inspection or mutation, any privileged or
mutation-bearing command, mutation of `oracle-test`, a database operation, the
destructive backup/restore drill, Package 5.0 product implementation, migration
`0014`, deployment, cutover, OD-62's binding ruling, or Package 5.1+. None of
those occurred.**

Outcome: **C-2, C-3 and C-5 are resolved; C-1's ruled boundary and R10's C-4
materializer are preserved unchanged. The generated plan reports zero unresolved
items and `executable: True`.** Nothing was executed. No finding is closed by
this submission, no readiness item moves, no assumption is confirmed, no
operational check is discharged, and Package 5.0 remains `not ready`; P5.0-R5
remains Blocking.

## R11.0 The one thing to read first: `executable: True` is not permission

The prompt asked for a plan with no unresolved items and `executable: True` "on
paper", and said in the same breath that the state "is **not** permission to
execute it". The harness now makes that separation structural rather than
verbal.

`ConcretePlan.is_executable` answers one question — *is every part of the
reviewed design expressed as a reviewed vector?* — and it is now True. Whether
the plan may run is a **different** question, answered by five independent gates
in `ExecutingRunner.__post_init__`, and **one of them refuses today**:

| Gate | State |
|---|---|
| 1. the target is the approved one, field for field | holds |
| 2. the plan carries no unresolved conflict | holds — this is what changed |
| **3. the interpreter's expected SHA-256 is a stated reviewed fact** | **refuses: it is `UNCONFIRMED`** |
| 4. the confirmation token is exact | requires an operator |
| 5. the reviewer's digest matches the recomputed manifest | requires Codex |

Gate 3 is new, and §R11.3 explains why it exists and why the fact could not be
supplied here. **A `--execute` invocation of this tree refuses before it starts
anything**, and that is a property of the object graph rather than of a
convention.

## R11.1 C-2 — Option B, and why the interpreter did not join the command surface

R10 recorded Option B's cost as *"a general-purpose interpreter joins
`PERMITTED_EXECUTABLES`"*. **It did not.** `plan.PERMITTED_EXECUTABLES` is
byte-for-byte unchanged, and the interpreter is admitted by one dedicated
validator and by nothing else.

### Where the interpreter is enforced — three boundaries

* **At planning.** `case_runtime.validate_case_vector()` is a **positional match
  against a fixed shape**, not a check that the vector contains the right
  things: element 0 is the one approved absolute interpreter path, elements 1–2
  are `-I -S` in that order, element 3 is `case_program_path(target)` — validated
  through `DisposableTarget.contained_path()`, so strictly inside the confirmed
  disposable root — element 4 is a key of the closed `CASE_VERBS` table, and the
  rest is exactly that verb's arity and argument kinds. `plan.validate_argv()`
  calls it whenever `argv[0]` is the interpreter, and refuses `argv[0]` that is
  neither a permitted distribution binary nor the interpreter.
* **At the two executables that exec something else.** `capsh` names the program
  it runs with `--shell=` and passes the arguments after `--`; `systemd-run`
  runs the whole vector after `--`. For both, the program the kernel actually
  runs is the **tail**, so `plan._validate_delegated_vector()` reassembles that
  tail and puts it through the same grammar. A `capsh` step with two `--shell=`
  options, with a `--shell=` the grammar does not admit, or with an empty tail —
  an interactive shell — is refused. The rule is applied to those two
  executables **by name**, so `chattr +a -- PATH` and `rm --force -- PATH` are
  unaffected.
* **Immediately before `execve`.** `ExecutingRunner._revalidate_vector()` runs
  `validate_argv` again on the vector that is about to be handed to the boundary
  — and for a late-bound step that is the **substituted** vector, so the
  Option-B prefix and the case-program grammar are re-checked after
  substitution, not only before it.

A fourth boundary is the program itself: it reads `sys.flags.isolated` and
`sys.flags.no_site`, compares `sys.argv[0]` with its own `CASE_PROGRAM_PATH`
constant, and re-derives verb, arity, argument kinds and path containment from
its own constants. A check made only by the caller is a check an edited caller
can skip.

### What is refused

Refused at planning **and** by the program: an unknown verb; a wrong arity; a
trailing argument; an argument to a verb that takes none; an unreviewed `open`
flag combination or write mode; an additional interpreter flag; an omitted `-I`
or `-S`; a reordered prefix; `-c`; `-m`; a relative interpreter; a second or
different interpreter; an arbitrary script path; a case-program path outside the
disposable root; a relative target; a target with a `..` segment; the disposable
root itself; a prefix-sharing sibling root; and any symlink target but the one
reviewed relative generation name.

### The case program

`tools/phase_5_0_evidence/execution/case_program.py`, one file, no build step.
It implements only the operations the package-plan cases already require —
`open` with six reviewed flag combinations, `pwrite`, `append`, `ftruncate`,
`rename`, `unlink`, `symlink`, `statvfs`, `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`,
a bounded identity observation and the interpreter preflight. It invokes no
shell, executes no other program, opens no socket, imports no database driver,
accepts no path outside the disposable root, writes only its own 17 reviewed
bytes, and reads exactly two files named as literals: `/proc/self/status` and
`sys.executable`.

**Installed bytes are source bytes.** The generated step is
`install --mode 0755 --owner root --group root <repo source> <root>/bin/case`.
`install` copies; there is no compiler, no code generation and no download, so
the review manifest's `source_digests` entry for
`tools/phase_5_0_evidence/execution/case_program.py` —
`f519be06a002837cfda4f596019c64addabf7e001793c6dda3ec240a4aa2d7f7` in this tree
— **is** the installation digest. This is the property R10 §R10.0 showed a
compiled program cannot have.

### The complete verb/path grammar

```text
<interpreter> -I -S <root>/bin/case <verb> [<argument> …]
```

| Verb | Arity | Arguments |
|---|---|---|
| `open` | 2 | `open_mode`, `target_path` |
| `pwrite` | 2 | `write_mode`, `target_path` |
| `append` | 1 | `target_path` |
| `ftruncate` | 2 | `write_mode`, `target_path` |
| `rename` | 2 | `target_path`, `target_path` |
| `unlink` | 1 | `target_path` |
| `symlink` | 2 | `target_path`, `link_name` |
| `statvfs` | 1 | `target_path` |
| `getflags` | 1 | `target_path` |
| `clearflags` | 1 | `target_path` |
| `identity` | 0 | — |
| `runtime` | 0 | — |

`open_mode` ∈ `rdonly`, `wronly`, `wronly-trunc`, `wronly-append`,
`wronly-append-trunc`, `create-excl`. `write_mode` ∈ `wronly`, `wronly-append`.
`link_name` is the single relative name `000001.journal`. `target_path` is
absolute, normalized, free of relative segments and **strictly inside** the
validated disposable root.

### The errno reaches the exit status, and why that matters

`plan.CommandStep` forbids a mutation-bearing step from recording more than its
exit status — a rule R11 did **not** relax. Stage 4's `S4-2` is mutation-bearing
(it starts the transient unit) and its whole evidentiary content is the
difference between `EROFS` and `EACCES`. So the case program maps a closed set
of errnos to distinct exit statuses (`EPERM` 10, `EACCES` 11, `EROFS` 12,
`ENOTTY` 13, `EOPNOTSUPP` 14, `EEXIST` 15, `ENOENT` 16), and a step declares
`satisfying_statuses=refused_with("EROFS")` — *reviewed in advance, in the
manifest*. It is strictly stronger than the `refusal_required` "any non-zero
exit" this replaces for these cases: a vector the program itself refused exits
**64**, which satisfies no case, so "the harness was misconfigured" can never be
recorded as "the boundary denied".

## R11.2 C-3 — the symlink, through the reviewed case program

`B3-12` is `<interpreter> -I -S <root>/bin/case symlink <root>/journal/current
000001.journal`, run as `root`, declaring mutation
`file:/var/lib/fb-evidence-p5-0/journal/current`. The link path must be absolute
and strictly inside the disposable root; the target must be exactly the reviewed
relative generation name. An absolute target, a `..`, a separator and any other
generation name are refused at planning and again by the program.

**No `ln`, no `cp -s` and no other general filesystem executable was added.**
`PERMITTED_EXECUTABLES` is unchanged. Cleanup is the existing `FILE` reversal —
`rm --force -- <path>`, which removes a symbolic link and exits 0 on an absent
one — so no new cleanup primitive and no new mutation kind was needed, and the
existing S-A/S-B/S-C state machine is untouched.

## R11.3 The interpreter prerequisite, and exactly what its digest covers

`P-05` is the preflight, and it establishes the runtime **by running the
reviewed vector itself**: `<interpreter> -I -S <root>/bin/case runtime`, as a
`PREREQUISITE`, immediately after `P-03`/`P-04` and before any dependent case.
It records the interpreter's absolute path and resolved path, its major/minor
version, the SHA-256 of its executable bytes, whether `-I` and `-S` are actually
in effect, whether any third-party distribution is importable, and the installed
case program's own digest.

**The expected digest is a reviewed target fact and is `UNCONFIRMED` in this
tree.** Establishing it requires reading `oracle-test`, which no authorization in
force grants, and learning it from the run being judged would make the preflight
a check against itself. So `case_runtime.EXPECTED_INTERPRETER_SHA256` carries the
sentinel, `interpreter_digest_confirmed()` is False, the manifest records
`expected_interpreter_sha256_confirmed: false`, and **gate 3 of the executor
refuses**. This is the dependency the prompt told me to return rather than
resolve, and it is returned in §R11.9 as a named request.

**What the digest covers.** The interpreter executable's own bytes, and nothing
else. It does **not** cover the operating system, the dynamic loader, `libc`,
`libpython`, any other shared library, or the Python standard library on disk.
Those are **disposable-host prerequisites**, exactly as they already are for
`capsh`, `chattr`, `install`, `lsattr`, `psql`, `systemd-run`, `systemctl`,
`getent`, `id`, `stat`, `findmnt`, `namei`, `getcap`, `useradd`, `groupadd`,
`gpasswd`, `userdel`, `groupdel`, `rm` and `rmdir` — none of which the harness
hashes either. Claiming more for this one executable than the harness claims for
any other would be false.

The interpreter named is
`/opt/freedom-blades/runtime/venv-web/bin/python`, the Python 3.12 runtime
`docs/operations/disposable-test-server.md` documents for `oracle-test`. Under
`-I -S` the virtual environment's `site-packages` is not on `sys.path` at all —
`-S` skips `site`, and `-I` additionally removes the script's directory and the
user site directory and ignores `PYTHONPATH` — so "imports no third-party
distribution" is a property of the vector, checked again by the program and
reported as `third_party_importable`.

## R11.4 C-5 — the four names, the declared sites, and what may not change

`tools/phase_5_0_evidence/binding.py` is the rule.

* **The reviewed vector carries names.** `--gid=freedomsheet`,
  `--groups=freedomsheet,freedomjournal`, `--uid=freedomsheet`. The manifest
  pins those, not numbers, because the accounts do not exist until Band 2
  creates them and a pinned number is a number nobody verified.
* **Each step declares its sites.** `CommandStep.bindings` names the exact
  argument index, the kind, and the exact names; `validate_sites()` refuses at
  **plan construction** a site whose argument is not exactly
  `prefix + ",".join(names)`. The declaration and the vector cannot drift.
* **Exactly four names.** `freedomcoord`, `freedomsheet`, `fbprobe`,
  `freedomjournal`. `root`, `postgres`, `discordbot` and `freedomweb` are
  refused: they are existing host identities the run neither creates nor names
  numerically.
* **Exactly one lookup result.** Resolution goes through the injected
  `IdentityLookup` — `boundary.SystemIdentityLookup`, which already refuses a
  duplicated record, refuses a direct answer that disagrees with the single
  enumerated one, and refuses an absent name.
* **The numeric form is validated.** A `bool`, a non-integer, zero, a negative
  value and anything above `2**31 - 1` are each refused, as is a group list
  whose names resolve to fewer distinct numbers than it has members.
* **Nothing outside a declared site may change.** After substitution the bound
  vector is compared with the symbolic one element by element, and a difference
  at an undeclared index — or a change of length — is refused.
* **Then the whole final vector is revalidated**, through `validate_argv`
  against the plan's target, which for these `capsh` steps re-checks the
  Option-B interpreter prefix and the case-program grammar of the tail. Only
  then is the boundary called.

Binding happens **before** cleanup responsibility is taken on, so a run that
cannot resolve an identity has not yet touched anything for that step. Dry-run
generation and every test use injected results; no test in this suite imports
`pwd` or `grp`, which `test_no_execution.py` asserts.

The manifest gains a per-step `bindings` array and `binding_site_count` in the
digest, so the permitted sites are part of what a reviewer approves.

## R11.5 The `P-03`/`P-04` ordering, ruled rather than inherited

R10 §R10.7 item 4 flagged this and left it open. It is settled: a prerequisite
whose subject does not yet exist is not a prerequisite. `P-03` (`getcap`) and
`P-04` (`stat`) are now generated **immediately after the install that creates
the case program and before any step that runs it**, with `P-05` as the first
use. Their ids, their `capability` band and what they assert are unchanged.
`test_concrete_plan.py::test_the_case_program_prerequisites_sit_between_its_install_and_its_first_use`
asserts the ordering, and
`::test_prerequisites_about_the_host_come_before_every_mutation` keeps the rule
for every prerequisite whose subject *is* the host.

## R11.6 What C-1 and C-4 look like after this change

**Unchanged, and asserted so.** `targets.root_or_contained_path()` is untouched;
it is still a separate method rather than a relaxation of `contained_path()`,
still used in exactly two places, and the only root cleanup vector is still a
non-recursive `rmdir`. `materialization.py` is untouched — the same closed
two-file table, the same pinned digests, the same `postgres:postgres 0640`, the
same capture-before-write rule, the same restore path — and
`execution/materializer.py` is untouched. Their whole R10 test set still passes.

One guard was **narrowed** rather than preserved: `plan.validate_argv` used to
admit any absolute path inside the disposable root as `argv[0]`, on the
assumption that a case binary would be exec'd directly. Under Option B the case
program is an argument and never `argv[0]`, so that exception is now a hole
admitting an arbitrary program, and it is gone.
`test_plan_and_cleanup.py::test_a_program_inside_the_disposable_root_is_no_longer_an_executable`
is the regression.

## R11.7 Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/case_runtime.py` | **new.** The interpreter, its flags, the reviewed digest fact, the closed verb grammar, the validator, and the errno→exit-status table |
| `tools/phase_5_0_evidence/binding.py` | **new.** C-5: the four names, the declared sites, the numeric-form rules and the change-outside-a-site refusal |
| `tools/phase_5_0_evidence/execution/case_program.py` | **new.** The reviewed payload — twelve verbs, its own four self-refusals, no shell, no process, no third-party import |
| `tools/phase_5_0_evidence/plan.py` | `validate_argv` admits the interpreter only through the grammar and validates `capsh`/`systemd-run` tails; the case-binary-as-`argv[0]` exception removed; `CommandStep.bindings` |
| `tools/phase_5_0_evidence/capability.py` | `ALL_CAPABILITY_NAMES`; `capsh_argv` takes the complete case-program vector and emits `--shell=<interpreter> -- …` |
| `tools/phase_5_0_evidence/capture.py` | four new closed policies — `CASE_RESULT`, `CASE_IDENTITY`, `CASE_RUNTIME`, `UNIT_DIRECTIVES` — each an allowlisted key set with a per-field shape |
| `tools/phase_5_0_evidence/concrete_plan.py` | the case-program install; `P-03`/`P-04` relocated and `P-05` added; the `JNL-52` access matrix; Stage 1, Stage 2, Stage 3's `statvfs` and Stage 4; `E1 … E6` and `E8`; four new declared mutations; **every `UnresolvedStep` gone** |
| `tools/phase_5_0_evidence/review_manifest.py` | three new covered sources; the `case_runtime` section; per-step `bindings`; `MANIFEST_VERSION` **3**; `binding_site_count` in the digest |
| `tools/phase_5_0_evidence/execution/executor.py` | gate 3; the injected `identity_lookup`; `_bind` and its final-vector revalidation; the tightened executable check |
| `tools/phase_5_0_evidence/execution/cli.py` | renders §1.1 (the runtime and the grammar) and §3.1a (the binding sites); reports the binding-site count in the dry run |
| `tools/phase_5_0_evidence/__init__.py` | the module table; `HARNESS_VERSION` **0.4.0-pre-execution** |
| `tools/phase_5_0_evidence/execution/__init__.py` | the tier table and the status paragraph |
| `tests/phase_5_0_evidence/test_case_program.py` | **new.** 74 cases: the grammar positively and negatively, the two tiers' tables, source/install identity, and every operation |
| `tests/phase_5_0_evidence/test_late_binding.py` | **new.** 34 cases: the sites, the substitution, the fail-closed outcomes and the executor's ordering |
| `tests/phase_5_0_evidence/test_no_execution.py` | `binding` and `case_runtime` in the planning tier; `case_program` declared in the execution tier with three new guards |
| `tests/phase_5_0_evidence/test_concrete_plan.py` | the interpreter exceptions; the no-unresolved-item assertion; the capability-band vectors; the `P-03`/`P-04`/`P-05` ordering |
| `tests/phase_5_0_evidence/test_bands.py` | `capsh_argv`'s vector form, and a new refusal for a bare program path |
| `tests/phase_5_0_evidence/test_executor.py` | the supplied-fact fixture, the injected lookup, the new gate-3 tests, the synthetic unresolved item |
| `tests/phase_5_0_evidence/test_executor_cleanup.py` | the supplied-fact fixture and the injected lookup |
| `tests/phase_5_0_evidence/test_plan_and_cleanup.py` | the narrowed `argv[0]` rule |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | **regenerated** |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | **regenerated** |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section |
| `docs/review/Handover information` | R11 returned to Codex |

**No other file in the worktree was touched.** `git status` is what it was before
this work started, plus the three new sources and two new test modules.

## R11.8 Verification — exact results from the final R11 tree

Every figure below was produced from the tree being submitted, serially, with
the documented interpreters and `TEST_DATABASE_URL` exported.

| # | Command | Result |
|---|---|---|
| 1 | `venv … pytest -q -rs tests/phase_5_0_evidence` | **778 passed** |
| 2 | `venv-web … pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **837 passed** |
| 3 | `venv … pytest -q -rs tests/test_database_backup_restore.py tests/test_filesystem_layout.py` with the seven deselected | **56 passed, 7 deselected** |
| 4 | `venv … pytest -q -rs tests/test_*.py` with the same seven deselected | **3152 passed, 7 deselected** |
| 5 | `venv-web … pytest -q -rs tests/web` | **2840 passed, 80 skipped — the documented figure** |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `venv … -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| 7 | `venv-web … -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| 8 | `venv … -m tools.phase_5_0_evidence.execution.cli` | dry run; see below |
| 9 | `git diff --check` | clean |

**The seven destructive drill integration cases are deselected by authority, not
passed and not silently skipped.** They are the same seven named in R8 handback
§R8.8, R9 §R9.6 and R10 §R10.6. **The destructive drill was not run.**

### The dry run

```
DRY RUN — nothing was executed.
  target                : oracle-test:/var/lib/fb-evidence-p5-0
  steps planned         : 115
  materializations      : 2 (written by nothing; this boundary is not armed)
  binding sites declared: 21 (resolved by nothing; no account database was read)
  mutations declared    : 43
  cleanup steps derived : 46
  unresolved conflicts  : 0 (none)
  review manifest digest: dfa61a575315803c6bb2f9ee39ec3bf4e2fcd7f25e895b5fdacb1acf58b454e0
  executable            : True
```

### The generated artifacts

Both were generated **twice** and compared byte for byte: `cmp` reported no
difference for either the concrete plan or the review manifest. All **27**
covered-source digests were independently re-hashed from the tree with **no
mismatch** — 24 as before, plus `binding.py`, `case_runtime.py` and
`execution/case_program.py`. Neither artifact was hand-edited.

**The R10 digest `594b4f65…` is superseded** and must never be passed to
`--execute`; `MANIFEST_VERSION` is now 3, so it cannot match in any case. The
R11 digest is
`dfa61a575315803c6bb2f9ee39ec3bf4e2fcd7f25e895b5fdacb1acf58b454e0`, and **it is
not execution authority either.** It is a value to submit for review, and it will
change again the moment the interpreter fact of §R11.3 is supplied — which is the
re-review that substitution should trigger.

## R11.9 Judgement calls, residuals and one newly discovered dependency

1. **The interpreter's expected SHA-256 is unsupplied, and the executor refuses
   while it is.** This is the dependency the prompt asked me to return rather
   than resolve. What is needed: the Operations Owner states, and the
   independent reviewer verifies on `oracle-test`, the SHA-256 of
   `/opt/freedom-blades/runtime/venv-web/bin/python`'s executable bytes. Editing
   `case_runtime.EXPECTED_INTERPRETER_SHA256` changes a covered source and
   therefore the manifest digest, so the substitution is re-reviewed rather than
   absorbed.
2. **Securebits is not observed.** `EvidenceIdentity.expected_masks()` states a
   securebits value for `E1 … E8`, and the kernel exposes securebits through
   `prctl(2)` and through no file. Reading it would need `ctypes`, which the
   execution tier forbids and which `test_no_execution.py` asserts is absent. So
   the case program's `identity` verb reports uid, gid, the supplementary gids,
   the five capability masks and `NoNewPrivs` — and **not** securebits, which is
   established by the `--secbits=4` option `capsh` applies and fails on rather
   than read back. Every affected step says so in its `expected_refusal`. A run
   that must observe securebits needs a separate reviewed mechanism.
3. **§5.2 states two different errnos for the same operation.** Case 2 expects
   `open(seal, O_WRONLY)` → `EPERM` for `freedomsheet`; case 4 expects the same
   operation on the same immutable inode → `EACCES` for `freedomcoord`. On Linux
   `inode_permission()` checks `IS_IMMUTABLE` **before** the discretionary check,
   so both would be `EPERM`. This is a package-plan inconsistency and not this
   generator's to rule on, so every negative access case is satisfied by
   **either** refusal code and the exact errno is recorded for the classifier.
   Codex may want to correct §5.2.
4. **The negative `JNL-52` cases assert a `create`, not an unlink or a rename.**
   §5.2 says "create, unlink or rename". All three are admissible refusals, and
   only the create leaves nothing behind when it is wrongly permitted — an
   unexpected file in `…/journal` makes the derived non-recursive `rmdir` fail
   and is reported as residue, whereas an unexpected unlink would have destroyed
   a declared object before anyone read the result. It is a narrowing, stated
   rather than assumed.
5. **Stage 4 uses one transient unit name twice.** `S4-1` starts
   `fb-evidence-s4.service` with `--collect`, so it is removed the moment it
   exits and the name is free; `S4-2` starts it without, so the failed unit stays
   loaded and `S4-3` can read the directive set that was actually applied. One
   declared mutation, one `systemctl stop` reversal, and the unit §2.13.2a names.
6. **Stage 1 reorders its own cases.** `C-6` runs before `C-4`, the rename is
   bracketed by a rename-back, and `C-5` is last, because each case's subject is
   the file the next one names. The rename's destination is a **declared
   mutation**, so a rename that succeeded beside a rename-back that did not
   leaves a named object cleanup removes rather than unnamed residue.
7. **`P-4`'s and the denial probes' targets are deliberately *not* declared
   mutations.** Each is expected to be refused, so nothing is created; a
   `refusal`-shaped step that declared a mutation would also be barred by
   `CommandStep`'s own rule. If the boundary failed to refuse, the unexpected
   object makes `rmdir` fail and is reported as residue — visible, not deleted.
8. **`HARNESS_VERSION` is 0.4.0-pre-execution and `MANIFEST_VERSION` is 3.** Both
   invalidate every previously circulated digest, deliberately.
9. **The case program duplicates one constant.** It cannot import
   `approved_target` — under `-I` nothing outside the standard library is
   importable, which is the isolation the whole vector exists to obtain — so the
   disposable root is written out a second time.
   `test_no_execution.py::test_the_case_programs_root_is_the_approved_targets_root`
   is what stops the two copies drifting.
10. **The case program's source is read from the repository tree on the
    disposable host.** `install`'s source is
    `/opt/freedom-blades/platform/tools/phase_5_0_evidence/execution/case_program.py`,
    the path `docs/operations/disposable-test-server.md` records for
    `oracle-test`. The executor recomputes the manifest from the tree it runs
    from and refuses unless it matches the reviewer's digest, so the installed
    bytes are bytes whose digest the run has already verified — but a reviewer
    should see stated that this makes the synchronized repository tree a
    prerequisite of the run, alongside the distribution executables.

## R11.10 What did not happen

**Nothing was executed.** No `--execute`, no armed process boundary, no armed
materializer, no armed case program, no generated vector, no SSH, no connection
to `oracle-test` and no inspection of it. No privileged command, no `sudo`, no
`su`, no `systemd-run`, no `systemctl`, no `chattr`, no `capsh`, no `useradd`,
`groupadd`, `usermod`, `gpasswd`, `install`, `chmod` or `chown`. No PostgreSQL
DDL, DML, configuration change or reload. No account, group, file, directory,
database object, HBA line, identity-map line, symbolic link or transient unit
was created, modified or removed anywhere. **No file was written to any
PostgreSQL configuration directory on any host**, and **no interpreter was
hashed on any host** — the expected digest is unsupplied precisely because
obtaining it was not authorized. The only files the suite writes are under
pytest's `tmp_path`. The destructive backup/restore drill was not run. No host
account database was read: no test in this suite imports `pwd` or `grp`, and
`test_no_execution.py` asserts it.

## R11.11 What this submission claims, and what it does not

**Claims.** C-2 is resolved as Option B, with the interpreter admitted by one
dedicated validator at three boundaries and re-checked a fourth time by the
program. C-3 is implemented through that program's `symlink` verb without a new
executable or a new cleanup primitive. C-5 binds exactly four names at declared
sites, validates the numeric form, refuses any change outside a site, and
revalidates the complete final vector before process creation. C-1's ruled
boundary and C-4's materializer are preserved with their tests intact, and one
guard was narrowed rather than kept. The generated artifacts are reproducible and
were reproduced.

**Does not claim.** No finding is closed — that is Codex's call. No gate moves;
Package 5.0 remains `not ready` and P5.0-R5 remains Blocking. Checks C-1, C-3 and
C-4 remain **not run**. No assumption is confirmed and no evidence was collected.
`executable: True` is a statement about the plan and not about permission: gate 3
refuses today, and gates 4 and 5 need an operator and a reviewer.

## R11.12 Request for Codex independent pre-execution review

Three things, and they are separable:

1. **Review the Option-B mechanism** — the grammar, the three planning
   boundaries, the program's own refusals, and whether the errno-to-exit-status
   table is the right way to give a mutation-bearing step its attribution.
2. **Review C-3 and C-5** — in particular the binding sites, the
   change-outside-a-site comparison, and the final-vector revalidation.
3. **Rule on the residuals in §R11.9** — above all the unsupplied interpreter
   digest (item 1), the unobserved securebits (item 2), and §5.2's contradictory
   errnos (item 3).

A separate independent Codex pre-execution review **and** explicit later
maintainer authorization remain required before anything executes. Nothing in a
clean review of this submission is authority to run it.

---

# R10 — conflict C-4 resolved; C-2 returned as the one open decision

Date: 2026-09-06

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r10-prompt.md`, and the
ruling Peter Duscha accepted on **2026-09-06** — package plan §2.12.2's
post-R9 disposition and change-log **C-P5.0-AG**. That authority covers
unprivileged code, focused-test, controlled-documentation and generated-artifact
work only. **It does not authorize `--execute`, an armed real process boundary,
execution of a generated vector, SSH, host inspection or mutation, any privileged
or mutation-bearing command, execution of the destructive backup/restore drill,
Package 5.0 product implementation, migration `0014`, deployment, cutover,
OD-62's binding ruling, or Package 5.1+. None of those occurred.**

Outcome: **C-1 is preserved with regressions and C-4 is resolved. C-2 is returned
unresolved, under the prompt's own stop clause, and C-3 and C-5 reduce to it.
The plan therefore reports `executable: False` and this submission does not reach
the "no unresolved items" state the prompt asks for.** Nothing was executed. No
finding is closed by this submission, no readiness item moves, no assumption is
confirmed, no operational check is discharged, and Package 5.0 remains `not
ready`; P5.0-R5 remains Blocking.

## R10.0 The decision this submission returns, stated first

The prompt and the Handover both say the same thing: *"If satisfying this
requires adding a new trusted runtime, compiler assumption, broad executable or
policy choice, stop and return the exact decision and impact instead of silently
enlarging the trusted computing base."* **C-2 requires exactly that, and it is
returned rather than answered.**

### Why C-2 cannot be resolved without a runtime decision

`…/bin/case` is a file the kernel must `execve` — under `capsh --shell=` for
`E1 … E8`, and as the payload of the Stage-4 transient unit. A file the kernel
can `execve` is one of exactly two things:

1. **a compiled binary**, which needs a compiler on `oracle-test`; or
2. **a script with a shebang**, which needs an interpreter.

There is no third form, so the conflict is not *"nobody has written the program
yet"*. It is *"the harness has no trusted runtime to run one in"*.

### Why the compiled form additionally fails C-2's own requirement

The prompt requires that the program's *"installed bytes and digest … be
reviewable and covered by the manifest"*. The review manifest is computed before
execution, from repository sources. A compiled program's installed bytes are the
**compiler's output**, which is not knowable at manifest time and varies with
toolchain version and flags, so its digest cannot be pinned in advance. Shipping
a binary built elsewhere is the *"downloaded/precompiled opaque binary"* the same
paragraph refuses. **Only an interpreted script satisfies "installed bytes = the
reviewed source bytes"**, which is what makes the digest pinnable — and an
interpreted script is a runtime.

### The three shapes, and the exact impact of each

| Option | What it costs | What it breaks |
|---|---|---|
| **A — return the decision** *(taken)* | C-2, C-3 and C-5 stay unresolved; `executable: False`; `PERMITTED_EXECUTABLES` unchanged; no new runtime, compiler or broad executable | the prompt's "no unresolved items" outcome is not reached in this submission |
| **B — explicit interpreter in the vector** | the reviewed vector names the interpreter, so the reviewed vector is still the vector that runs; installed bytes are the reviewed source bytes and the digest pins | a **general-purpose interpreter joins `PERMITTED_EXECUTABLES`** — the "broad executable" the stop clause names. On `oracle-test` the declared interpreter is the `/opt/freedom-blades/runtime/venv-web` Python 3.12.14 of `docs/operations/disposable-test-server.md`, whose `site-packages` are outside the review manifest, so bytes that affect the probe's behaviour would sit outside the reviewed digest |
| **C — shebang, vector names only `…/bin/case`** | `PERMITTED_EXECUTABLES` is unchanged and the digest still pins | the program actually executed is the interpreter, which **the reviewed vector does not name** — the indirection the whole argument-vector discipline exists to prevent. `P-03` and `P-04` would then assert the file capabilities and mode of the *script*, not of the interpreter that runs, so two Band-1 prerequisites would be asserting about the wrong file |
| **D — compile C on the target** | source stays in the repository | adds a compiler to the permitted set and a build step that mutates the target, and the **installed bytes cannot be pinned in the manifest**, which is the property C-2 explicitly requires |

**Option A is taken**, on Peter Duscha's ruling recorded in this session. The
decision Codex and the maintainer are asked for is between B, C and D — or a
fourth shape neither the prompt nor this handback has found.

### What C-2 blocks, and what it does not

* **C-3** — `…/journal/current` is a symbolic link. The R10 brief places
  `symlink` among the case program's verbs and refuses admitting `ln` merely to
  obtain one operation, so C-3 waits on C-2. Its alternative resolution — a
  ruling that the disposable facsimile does not need the symlink — remains open
  and needs no runtime.
* **C-5** — every `E1 … E8` invocation execs the case program. A late-binding
  rule implemented now would resolve four names into a vector that still cannot
  be generated, which is **a mechanism with no consumer**; `.agents/AGENTS.md`
  is explicit that abstractions are not added without a real consumer, so it is
  deferred with C-2 rather than built speculatively. This is a judgement call and
  is flagged again in §R10.7.
* **C-4** — independent of all of it, and resolved below.

## R10.1 C-1 — the ruled target-root boundary, preserved and pinned

The ruling (package plan §2.12.2, change-log **C-P5.0-AG**) is accepted, and
`targets.py`'s prose now records it as accepted rather than as a conflict being
submitted. **No code changed**: `root_or_contained_path()` is untouched, it is
still a separate method rather than a relaxation of `contained_path()`, and it is
still used in exactly two places — the root's own `DIRECTORY` mutation validation
and the `rmdir` reversal derived from it.

What is new is the regression set the prompt requires, in
`tests/phase_5_0_evidence/test_targets.py` and `test_concrete_plan.py`:

| Requirement | Test |
|---|---|
| `/`, `/var/lib`, the repository root, production paths, shallow paths, unresolved variables, globs, metacharacters, sibling paths and `..` escapes remain refused | `test_the_root_exception_refuses_everything_it_did_before` — 22 parametrized cases, including a **prefix-sharing sibling** (`…-r1x`) and an escape to the parent itself |
| the exception admits the target's own root and its descendants, and nothing else | `test_the_root_exception_admits_the_targets_own_root_and_its_descendants` |
| ordinary mutation paths still require containment | `test_an_ordinary_mutation_path_still_requires_strict_containment` |
| the exception does not weaken target admissibility | `test_the_root_exception_still_refuses_an_unconfirmed_or_unassigned_target` |
| the only root cleanup vector is non-recursive `rmdir` | `test_the_only_vector_that_removes_the_root_is_a_non_recursive_rmdir` — one reversal, `("/usr/bin/rmdir", "--", root)`, and no other step in the plan names the root as an object to remove |
| one creation, one reversal | `test_the_root_is_created_by_exactly_one_step_and_reversed_by_exactly_one` |
| unexpected content causes visible cleanup residue rather than deletion | `test_an_unexpectedly_non_empty_root_is_reported_as_residue_not_deleted` — state S-B, the path named in full, the next invocation refusing, and no recursive form anywhere in the message |

**The exception was not generalized and no second cleanup primitive was added.**

## R10.2 C-4 — the bounded materialization mechanism

Two halves, in two tiers, and neither can do the other's job.

### The planning half — `tools/phase_5_0_evidence/materialization.py`

A **closed table of two files**, covered by the review manifest, in the tier that
has no file access at all. There is no function that takes a path and some bytes.
Each `MaterializedFile` validates on construction:

* the **filename** is one of `targets.POSTGRES_CONFIG_FILES` — two names, and no
  third; `postgresql.conf` is refused;
* every **line** is within a narrow ASCII set: no tab, no NUL, no embedded
  newline, no non-ASCII byte;
* the **owner, group and mode** are pinned to `postgres:postgres 0640` — the
  exact values the reviewed cleanup restore reinstalls with, so a materialization
  cannot leave the file in a state the restore would change;
* the total content is within `MAX_MATERIALIZED_BYTES` (4096); and
* the **content digest is a written constant**, compared with the content. An
  edited rule that is not accompanied by a deliberate edit to the digest is a
  `PlanRefused` **at import**, not a quietly different file.

`reviewed_configuration(target)` derives the bytes from `target.database_name` —
§2.12.3's one `__PROD_DB__` substitution — and then checks the pinned digest, so
a target whose database is not the approved one produces different bytes and is
**refused** rather than written.

**The file is replaced whole rather than prepended to, and that is a stated
choice.** §2.12.3's ordering claim reads like an insertion; implementing it as
one would require **reading the live host file first**, which C-4 forbids. The
synthetic file therefore carries the five coordinator rules and then one broader
`local all all peer` rule beneath them, which is the ordering relation the case
asserts. That trailing rule is load-bearing rather than cosmetic: the reload, the
post-reload control and both `psql` drops connect over the local socket as
`postgres`, and a file without it would lock the harness out of its own cleanup.
The byte-exact pre-change capture in `…/before/` is what the reviewed cleanup
reinstalls, unchanged.

**The bytes are checked by the band's own analysis, not by transcription.**
`test_materialization.py::test_the_reviewed_hba_bytes_satisfy_the_bands_own_ordering_analysis`
runs `hba.analyse_hba()` over them — the function the evidence band runs on a
supplied file, which knows nothing about this table — and asserts
`ordering_holds is True`, `findings == ()`, and the peer line at index 0 as the
first rule matching the coordinator role. `analyse_ident()` reports
`mapping_is_exact` with exactly one map line.

### The executing half — `tools/phase_5_0_evidence/execution/materializer.py`

The one place in the harness that puts bytes on disk, declared in
`test_no_execution.py::EXECUTION_TIER_NAMES` exactly as `boundary.py` is. Four
independent checks, each of which would have to be defeated separately:

1. the planning tier already fixed the content, by a digest written as a constant
   and inside the manifest;
2. the executor compares the destination with `DisposableTarget.config_path()`
   immediately before the call;
3. **this module re-derives admissibility from the guards without consulting the
   plan** — `POSTGRES_CONFIG_FILES` plus `validate_postgres_config_directory`,
   so `/etc/passwd`, `postgresql.conf`, a production hierarchy, the repository
   worktree and a relative segment are refused here as well as there; and
4. it re-hashes the bytes it was handed, at the point of the write.

The write is `os.open(destination, O_WRONLY | O_TRUNC | O_NOFOLLOW)` — **no
`O_CREAT`**, so it can only ever replace a file the capture step has already
copied, and `O_NOFOLLOW` is what makes the preceding `lstat` meaningful against a
link swapped in afterwards. `test_the_write_can_neither_create_a_file_nor_follow_a_link`
reads those three flags off the single `os.open` call in the module's AST.

Refusals are a fixed vocabulary, `MATERIALIZATION_FAILURES`, exactly as
`LAUNCH_FAILURES` is: no path, account, id or operating-system message reaches a
run outcome.

### The executor

`MaterializeStep`s are held in `ExecutionPlan.materializations`, **not** in
`steps`: they have no `argv`, and a list whose members sometimes have one is a
list every reader has to check. Each declares two orderings, both validated at
plan construction — the `capture_step_id` whose success it requires and the
`after_step_id` it runs immediately after — and a plan whose capture is ordered
*after* its materialization is refused.

Responsibility for cleanup begins **before** the write, exactly as it does before
a command: the declared mutation is recorded first, so a materialization whose
outcome is never learned gets the full derived restore → one reload → control →
proof. The `materializer` field defaults to `RecordingMaterializer`, which writes
nothing and reports `materializer-not-armed`, so an executor assembled without
one refuses the step, stops the run and cleans up — it never writes silently.

### What C-4 changed in the generated artifacts

* `B6-M1` and `B6-M2` appear in a new **§3.2** of the concrete plan, with their
  destination, owner, group, mode, byte count, SHA-256, both orderings and the
  **complete bytes** inline;
* the two `postgres_config_line` traceability rows no longer read *"not reached
  by any generated step"* — they read `B6-M1 → CL-02` and `B6-M2 → CL-01`;
* the unresolved list drops from 16 items to **14**, and `C-4` no longer appears
  among the conflicts; and
* the review manifest gains a `materializations` section and
  `MANIFEST_VERSION` is **2**, so a digest approved under version 1 — which
  covered a plan that could not write a file — stops matching rather than being
  reinterpreted as one that can.

## R10.3 What was deliberately not built

* **No general write-file interface**, no shell redirection, no heredoc, no
  `tee`, no `sed -i`, and no host-file read. `PERMITTED_EXECUTABLES` is
  **unchanged**.
* **No new mutation kind.** `POSTGRES_CONFIG_LINE` already existed and its
  restore/reload/verify cleanup phase already existed; C-4 supplied the missing
  *performer*, not a new reversal.
* **No late-binding mechanism** (C-5), for the reason in §R10.0: it would have no
  consumer.
* **No case program, no interpreter, no compiler, no `ln`** (C-2, C-3).
* **No change to the R9 behaviour**: canonical explicit group inverses, two-way
  membership consistency, exact-one NSS classification, fixed safe-launch
  classifications, guaranteed cleanup and the corrected backup-drill wording are
  untouched. `identity.py`'s bytes are unchanged, which the manifest's source
  digest shows.

## R10.4 Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/materialization.py` | **new.** The closed two-file table, its pinned digests and its construction guards |
| `tools/phase_5_0_evidence/execution/materializer.py` | **new.** The one place bytes are written, its four checks and its fixed refusal vocabulary |
| `tools/phase_5_0_evidence/plan.py` | `MaterializeStep`; `ExecutionPlan.materializations` and its validation; `materializations_after()` |
| `tools/phase_5_0_evidence/concrete_plan.py` | generates `B6-M1`/`B6-M2`; removes the two C-4 unresolved items; traceability counts materializations as performers; the unresolved items now name the one open runtime decision |
| `tools/phase_5_0_evidence/execution/executor.py` | the injected `materializer`, `_materialize_after`, `_revalidate_materialization`, `_RunState.satisfied_steps` |
| `tools/phase_5_0_evidence/execution/cli.py` | renders §3.2; reports the materialization count in the dry run; arms `SystemMaterializer` on the one `--execute` line |
| `tools/phase_5_0_evidence/review_manifest.py` | two new covered sources; `materializations`; `MANIFEST_VERSION` 2; `materialization_count` in the digest |
| `tools/phase_5_0_evidence/targets.py` | **prose only.** `root_or_contained_path()`'s docstring records the C-1 ruling as accepted |
| `tests/phase_5_0_evidence/test_materialization.py` | **new.** 41 cases: the reviewed bytes, and every way the mechanism refuses |
| `tests/phase_5_0_evidence/test_targets.py` | the C-1 regression set |
| `tests/phase_5_0_evidence/test_concrete_plan.py` | the C-1 plan-level regressions; the conflict set is now `{C-2, C-3, C-5}` |
| `tests/phase_5_0_evidence/test_executor.py` | `FakeMaterializer`; seven materialization cases |
| `tests/phase_5_0_evidence/test_executor_cleanup.py` | `FakeMaterializer`, `RaisingMaterializer`; the cleanup guarantee and the interruption path for a materialization |
| `tests/phase_5_0_evidence/test_no_execution.py` | both tier declarations extended |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | **regenerated** |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | **regenerated** |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section |
| `docs/review/Handover information` | R10 returned to Codex |

## R10.5 Conflicts mapped to implementation and named tests

| Conflict | Disposition | Implementation | Tests |
|---|---|---|---|
| **C-1** | preserved; ruling recorded | `targets.root_or_contained_path` (unchanged), `cleanup._rmdir` | `test_targets.py::test_the_root_exception_refuses_everything_it_did_before`, `::test_the_root_exception_admits_the_targets_own_root_and_its_descendants`, `::test_an_ordinary_mutation_path_still_requires_strict_containment`, `::test_the_root_exception_still_refuses_an_unconfirmed_or_unassigned_target`; `test_concrete_plan.py::test_the_only_vector_that_removes_the_root_is_a_non_recursive_rmdir`, `::test_the_root_is_created_by_exactly_one_step_and_reversed_by_exactly_one`, `::test_an_unexpectedly_non_empty_root_is_reported_as_residue_not_deleted` |
| **C-2** | **returned unresolved** | none | `test_concrete_plan.py::test_the_plan_is_not_executable_while_conflicts_remain` |
| **C-3** | **returned unresolved**, reduces to C-2 | none | as above |
| **C-4** | **resolved** | `materialization.py`, `execution/materializer.py`, `plan.MaterializeStep`, `concrete_plan._band_6`, `executor._materialize_after` | the whole of `test_materialization.py`; `test_executor.py::test_a_materialization_is_handed_exactly_the_reviewed_bytes`, `::test_a_materialization_runs_immediately_after_the_step_it_names`, `::test_a_materialization_records_no_argument_vector`, `::test_an_unapplied_materialization_stops_the_run_and_cleans_up`, `::test_an_executor_assembled_without_a_materializer_refuses_to_write`, `::test_a_materialization_refuses_when_its_capture_step_was_not_satisfied`, `::test_a_materialization_whose_destination_drifted_is_refused_twice_over`; `test_executor_cleanup.py::test_a_materializer_that_raises_still_runs_the_whole_derived_cleanup`, `::test_an_interruption_during_a_materialization_cleans_up_then_propagates` |
| **C-5** | **returned unresolved**, reduces to C-2 | none | `test_concrete_plan.py::test_the_capability_band_generates_no_vector_and_says_why` |

## R10.6 Verification — exact results from the final R10 tree

Every figure below was produced from the tree being submitted, serially, with the
documented interpreters, and `TEST_DATABASE_URL` exported.

| # | Command | Result |
|---|---|---|
| 1 | `venv … pytest -q -rs tests/phase_5_0_evidence` | **648 passed** |
| 2 | `venv … pytest -q -rs tests/test_database_backup_restore.py tests/test_filesystem_layout.py` with the seven deselected | **56 passed, 7 deselected** |
| 3 | `venv-web … pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **707 passed** |
| 4 | `venv … pytest -q -rs tests/test_*.py` with the same seven deselected | **3149 passed, 7 deselected** |
| 5 | `venv-web … pytest -q -rs tests/web` | **2840 passed, 80 skipped — the documented figure** |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `venv … -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| 8 | `venv … -m tools.phase_5_0_evidence.execution.cli` | dry run; see below |
| 9 | `git diff --check` | clean |

**The seven destructive drill integration cases are deselected by authority, not
passed and not silently skipped.** They are the same seven named in R8 handback
§R8.8 and R9 §R9.6. **The destructive drill was not run.**

### The dry run

```
DRY RUN — nothing was executed.
  target                : oracle-test:/var/lib/fb-evidence-p5-0
  steps planned         : 64
  materializations      : 2 (written by nothing; this boundary is not armed)
  mutations declared    : 39
  cleanup steps derived : 42
  unresolved conflicts  : 14 (C-2, C-3, C-5)
  review manifest digest: 594b4f6595a4e656d806682ccd3573fe7b312d0c829914eb657b616966a683a2
  executable            : False
```

### The generated artifacts

Both were generated **twice** and compared byte for byte: `cmp` reported no
difference for either the concrete plan or the review manifest. All **24**
covered-source digests were independently re-hashed from the tree with **no
mismatch** — 22 as before, plus `materialization.py` and
`execution/materializer.py`. Neither artifact was hand-edited.

**The R9 digest `a3b59f2e…` is superseded** — eight covered sources changed — and
must never be passed to `--execute`. The R10 digest is
`594b4f6595a4e656d806682ccd3573fe7b312d0c829914eb657b616966a683a2`, and **it is
not execution authority either.** It is a value to submit for review.

## R10.7 Judgement calls, flagged rather than buried

1. **C-5's late-binding rule is not implemented.** The prompt asks for it; every
   consumer of it execs the case program of C-2, so building it now would add a
   mechanism with nothing to abstract, against `.agents/AGENTS.md`. Codex may
   reasonably disagree and ask for it as a stand-alone reviewable unit.
2. **The synthetic `pg_hba.conf` replaces the file whole**, and adds a
   `local all all peer` rule the pre-change file's own content is not consulted
   about. It is the only shape C-4 permits without a host-file read, it applies
   to the disposable instance only, and the byte-exact capture is restored — but
   it is a design choice a reviewer should see stated rather than infer.
3. **`MANIFEST_VERSION` is bumped to 2.** This invalidates every previously
   circulated digest, deliberately.
4. **`P-03`/`P-04`'s ordering is still unresolved**, and still inherited rather
   than ruled: they are generated in the Band-1 position the design gives them
   while their subject is a file Band 3 creates. Resolving C-2 has to settle it.

## R10.8 What did not happen

**Nothing was executed.** No `--execute`, no armed process boundary, no armed
materializer, no generated vector, no SSH, no connection to `oracle-test` and no
inspection of it. No privileged command, no `sudo`, no `su`, no `systemd-run`,
no `chattr`, no `setcap`, no `capsh`, no `useradd`, `groupadd`, `usermod`,
`gpasswd`, `install`, `chmod` or `chown`. No PostgreSQL DDL, DML, configuration
change or reload. No account, group, file, directory, database object, HBA line,
identity-map line or transient unit was created, modified or removed anywhere.
**No file was written to any PostgreSQL configuration directory on any host**;
the only files the suite writes are under pytest's `tmp_path`. The destructive
backup/restore drill was not run. No host account database was read: no test in
this suite imports `pwd` or `grp`, and `test_no_execution.py` asserts it.

## R10.9 What this submission claims, and what it does not

**Claims.** C-1's ruled boundary is preserved and now has regressions for every
property the prompt lists. C-4 is resolved by a bounded mechanism whose content,
destination, ownership, mode and digest are pinned in the plan and the manifest,
and which is refused on a content or digest mismatch, an unreviewed destination,
an existing-object type mismatch or an incomplete capture. The generated
artifacts are reproducible and were reproduced.

**Does not claim.** No finding is closed — that is Codex's call. No gate moves;
Package 5.0 remains `not ready` and P5.0-R5 remains Blocking. Checks C-1, C-3 and
C-4 remain **not run**. No assumption is confirmed and no evidence was collected.
**The prompt's required end state — no unresolved items and `executable: True` —
is not reached**, and this handback does not present a partial resolution as one.

## R10.10 Request for Codex independent pre-execution review

Two things are asked for, and they are separable:

1. **Review C-1's regressions and C-4's mechanism** on their own merits — in
   particular whether the whole-file synthetic `pg_hba.conf` of §R10.2 is the
   right shape, and whether the four independent destination checks are enough.
2. **Rule on C-2's runtime**, or refer it to Peter Duscha. §R10.0 states the four
   options and their exact impact. C-3 and C-5 follow from it, and nothing in
   this package can reach `executable: True` until it is decided.

A separate independent Codex pre-execution review **and** explicit maintainer
authorization remain required before anything executes.

---

# R9 — the group inverse corrected across the whole table, and where the drill's runtime-role refusal actually happens

Date: 2026-09-06

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r9-prompt.md`, and the
representation ruling Peter Duscha accepted on **2026-09-06** — package plan
§2.12.2's R9 amendment and change-log **C-P5.0-AF**. That authority covers
unprivileged code, focused-test, controlled-documentation and generated-artifact
work only. **It does not authorize `--execute`, an armed real process boundary,
execution of a generated vector, SSH, host inspection or mutation, any
privileged or mutation-bearing command, execution of the destructive
backup/restore drill, Package 5.0 product implementation, migration `0014`,
deployment, cutover, OD-62's binding ruling, or Package 5.1+. None of those
occurred.**

Outcome: **both findings are conceded and corrected. Nothing was executed. No
finding is closed by this submission, no readiness item moves, no assumption is
confirmed, no operational check is discharged, and Package 5.0 remains `not
ready`; P5.0-R5 remains Blocking.**

## R9.0 The two findings, conceded before their corrections

### EH-R8-2 — **Conceded in full.**

R8 defined the inverse table's member column correctly — the **fourth field of
`getent group`**, a group's *explicit* member list — corrected the one row the R7
ruling had touched, and then reported four older rows with the same defect and
left them standing. `freedomcoord`, `freedomsheet`, `discordbot` and `fbprobe`
each listed, in their inverse row, the account whose *primary* group they are.

That was a real `JNL-52` correctness defect on a host provisioned exactly as
§2.12.2 and §2.13.3 require: `useradd` does not add an account to its own primary
group's explicit list, so `getent group freedomcoord`, `getent group
freedomsheet` and `getent group fbprobe` report an **empty** fourth field and
`getent group discordbot` reports `freedomweb` alone.
`classify_group_membership` compares as an exact set, so all four
`JNL-52-GROUP-*` cases failed with the account reported as a *missing* member,
`membership_matrix_holds()` was then false, and **every `JNL-52` access case that
reads it as a precondition was gated off**. It failed closed — nothing ran on the
strength of it — but it made the required evidence uncollectable on a correct
host, which is the whole point of the check.

**I raised it in R8 §R8.3 and §R8.11 and did not fix it**, because correcting it
was a membership decision I had no authority to make. Peter Duscha has now made
it, and this remediation applies it exactly.

The same review also identified the row the inverse never had: `foundry`'s
identity row has named `users` as a supplementary group throughout, and no
inverse row stated it. That is a membership stated half-way — the P5.0-SR2 shape
and stop condition **10p** — and R8's guard did not catch it because the guard
was scoped to the one ruled row. Peter Duscha ruled that row too: `users`:
`foundry` only.

### DS-R8-2 — **Conceded in full.**

The drill's exit-code contract said that exit `2` meant *"the drill refused
before touching anything"*, and the operations guide said the two runtime-role
refusals happened *"in step 3b, before `DROP SCHEMA`, so nothing is dumped,
dropped or restored"*.

**The second half of each sentence was true and the first half was false.** The
runtime-role decision is in step 3b, which runs **after** step 1's `pg_dump`,
step 2's `sha256sum`, the creation and `chmod 700` of the work directory, and the
read-only inventories of steps 3 and 3b. A dump, its `.sha256`,
`inventory-before.txt` and `grants-before.txt` are therefore already on disk when
the refusal fires. Nothing destructive has happened — `SCHEMA_DROPPED=1`,
`DROP SCHEMA public CASCADE` and the restore are all in steps 4 and 5 — so the
database is exactly as it was and no recovery is required, but an operator told
that nothing was touched will not go looking for the artifacts, and may reasonably
conclude that a work directory containing a dump means the drill got further than
it did.

**Where the false claims were, precisely.** Two places, both corrected:
`infra/postgresql/backup-restore-drill.sh`'s `# Exit codes:` header, and
`docs/operations/database-development.md`'s runtime-role section. The R8 handback
§R8.5 and the R8 handover did **not** repeat them — both say only that the
refusal is in step 3b and precedes `SCHEMA_DROPPED=1`, which is accurate — so
there is no historical handback sentence to withdraw. This section states the
ordering in full so the current handback carries it.

## R9.1 The corrected inverse, row by row

Peter Duscha's ruling, applied exactly and nowhere widened:

| Group row | Members before R9 | Members after R9 | Why |
|---|---|---|---|
| `freedomcoord` | `{freedomcoord}` | **`{}`** | `freedomcoord` is that account's *primary* group and nobody's supplementary one |
| `freedomsheet` | `{freedomsheet}` | **`{}`** | same |
| `discordbot` | `{discordbot, freedomweb}` | **`{freedomweb}`** | `freedomweb` is a real supplementary membership and stays; `discordbot`'s own account is not an explicit member of its own primary group |
| `fbprobe` | `{fbprobe}` | **`{}`** | same as the first two |
| `users` | **absent** | **`{foundry}`** | added. The identity half already stated `foundry -> users`; the inverse carried no row for it, so the membership was stated half-way |
| `postgres` | `{}` | unchanged | corrected by R8 |
| `ssl-cert` | `{postgres}` | unchanged | a supplementary membership, correctly explicit |
| `freedomjournal` | `{freedomcoord, freedomsheet}` | unchanged | both supplementary; already correct |
| `sudo` | `{foundry}` | unchanged | supplementary; already correct |

**No account's primary group or complete supplementary set changed.** The
identity half of `CANONICAL_ACCOUNTS` is byte-for-byte what it was, and
`test_the_r9_corrected_inverse_rows_are_exact` asserts every one of those rows so
a later edit cannot let the ruling drift into a membership change.

The four rows are **kept with the empty set rather than deleted**, for the reason
R8 kept the `postgres` row: an empty explicit list is a claim worth failing on —
an account explicitly added to `freedomcoord` would read `…/archive` through a
group — and a deleted row would make its `JNL-52-GROUP-*` case *unclassifiable*
rather than failed. `classify_group_membership` refuses a group it has no
canonical row for.

## R9.2 The consistency guard, generalized

`_the_ruled_row_is_stated_in_both_tables()` is replaced by
`_the_two_halves_of_the_table_agree()`. R8's guard walked one ruled account;
this one walks the whole table, still at import time, still failing closed so
every consumer fails with it.

It enforces three properties, and **the primary group participates in none of
them**:

1. **No account's primary group is also one of its supplementary groups.** The
   two columns of the identity half cannot claim the same membership in two
   different senses.
2. **Every supplementary group an identity row names has an inverse row, and
   that row lists the account.** This is the direction the missing `users` row
   failed.
3. **Every explicit member of an inverse row** is an account this table covers,
   is **not** the account whose primary group that row is, and names the group as
   supplementary.

Property 3's middle clause is the one that makes EH-R8-1 and EH-R8-2
non-regressible: writing an account back into its own primary group's row is now
an `ObservationRefused` at import, naming the finding, for all five rows
(`postgres` and the four corrected). Its first clause is the R9 prompt's bar on
inferring a member: an inverse row listing a name outside
`CANONICAL_ACCOUNTS` — a host account, say — refuses rather than being accepted.

The primary group continues to be verified where a host actually reports it:
`CanonicalAccount.primary_group` against `id`, in `classify_account_identity`,
and through the credential chain `_from_canonical` →
`RequiredIdentity.__post_init__` → `_resolve`.

**Two symbols removed.** `identity.PRE_EXISTING_PRIMARY_IN_INVERSE` — R8's
reported-defect hold — is gone, with its test and its module prose; the property
it recorded is now asserted as a property
(`test_no_inverse_row_treats_a_primary_membership_as_an_explicit_one` requires
the conflating set to be **empty**, so a fifth such row cannot appear either).
`identity.R7_RULED_ACCOUNT` is gone with it: its documented reason was that the
guard was *"about a specific ruled row rather than a sweeping claim about a table
this remediation is not authorized to rewrite"*, and after the ruling that
sentence is false. **This is a judgement call inside the finding's scope, flagged
here rather than left to be noticed** — see §R9.7.

## R9.3 DS-R8-2 — what the corrected text says, and what it deliberately keeps

**The ordering, stated once.** Steps 1–3b: work directory, `pg_dump`,
`sha256sum`, `row_counts` → `inventory-before.txt`, `grant_inventory` →
`grants-before.txt`, then the runtime-role cardinality decision and the
role-name validation. Steps 3c–6b: `schema-grants.sql` and its checksum,
`SCHEMA_DROPPED=1`, `DROP SCHEMA public CASCADE`, `pg_restore`, grant
re-application, and the two comparisons. **Both `2` refusals are inside the
first group and every destructive command is inside the second.**

**What is now said, in all three places.** A dump and diagnostic artifacts may
already exist; no schema is dropped and nothing is restored; the database is in
exactly the state it was in; and **no recovery is required**. The last clause
matters operationally — it is the difference between a work directory an operator
may delete and one they must restore from.

**What is deliberately kept.** Gate 0a's refusal — a non-disposable database
name — really does happen before the work directory is created, and exit `3`
really does touch nothing. The exit-code contract now distinguishes the branches
instead of flattening them, and
`test_gate_0a_still_refuses_before_the_work_directory_exists` pins the contrast
by asserting the directory does not exist.

**The DS-R8-1 code is untouched.** The prompt permits a change only if a focused
regression exposes a defect, and none did: the cardinality decision, the
record-preserving split, the `^[A-Za-z_][A-Za-z0-9_]{0,62}$` validation and the
ordering are exactly as R8 left them. What changed in the script is the header
comment, one comment inside step 3b, and the two refusal messages — which now
state what exists rather than leaving the operator to infer it from the exit code.

**A test that was weaker than it read.** DS-R8-1's
`test_the_cardinality_test_no_longer_reads_a_string_its_separator_was_deleted_from`
asserted `index(refusal) < index("SCHEMA_DROPPED=1") < index("DROP SCHEMA")`
over the **raw source**. Both of the first two phrases also occur in *comments* —
the exit-code contract quotes the refusal text, and step 3b's comment names
`SCHEMA_DROPPED=1` — so the assertion was ordering prose, and it happened to hold
only because the header comment came first. Correcting the header moved that
prose and made it visible. The assertion now runs over the comment-stripped
`code` the same test already computes, so it is the ordering of the executable
statements, and a line asserting that `pg_dump` precedes the refusal was added —
which is the DS-R8-2 fact itself, pinned in the script.

## R9.4 Files changed, and why

| File | Why |
|---|---|
| `tools/phase_5_0_evidence/identity.py` | EH-R8-2: the four ruled inverse rows corrected in place, the ruled `users` row added, `PRE_EXISTING_PRIMARY_IN_INVERSE` and `R7_RULED_ACCOUNT` removed, the import-time guard generalized to the whole table in both directions, module and `CanonicalGroup` documentation updated |
| `tests/phase_5_0_evidence/test_bands.py` | EH-R8-2 regressions: the both-directions relation, the five exact ruled sets, the no-primary-in-inverse property, and six drift cases against the generalized guard. The pinned-hold test is removed with the hold |
| `tests/phase_5_0_evidence/test_boundary_identity.py` | the manifest-digest test extended from one corrected inverse row to all six, so every row the ruling touched is inside the reviewed digest |
| `tests/phase_5_0_evidence/test_no_execution.py` | a suite-wide AST guard that no test in `tests/phase_5_0_evidence` imports `pwd` or `grp` — the corrected rows must be decided from §2.12.2, never from whichever host runs the suite |
| `infra/postgresql/backup-restore-drill.sh` | DS-R8-2: the exit-code contract distinguishes gate 0a from step 3b and states what exists; step 3b's comment and both refusal messages say precisely what was and was not touched. **No executable logic changed** |
| `docs/operations/database-development.md` | DS-R8-2: the *"nothing is dumped"* sentence withdrawn and replaced with the precise ordering, the artifacts named, and a pointer from the gate-0a sentence to the later refusal |
| `tests/test_database_backup_restore.py` | five DS-R8-2 regressions against the existing stubbed-client boundary, plus the ordering assertion strengthened to run over code rather than comments |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated; never hand-edited |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated; never hand-edited |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section |
| `docs/review/Handover information` | R9 identified as the current handover, all previous handovers preserved below |

`docs/review/phase-5-0-package-plan.md` §2.12.2 **already carried the R9 ruling
and the corrected inverse table** when this remediation began — the ruling text,
the four sets, the `users` row and its inverse-table entry are in the tree as
found, and I changed nothing in it. Nothing else was touched. No product
application code, bot behavior, migration, database schema, deployment file,
roadmap, project status, RAID entry, unrelated decision, or accepted membership
ruling was changed, and the rest of the dirty worktree — other contributors'
in-flight work — was preserved exactly as found. **No change-log entry was
written**: C-P5.0-AF already records this decision, and R9 makes no new one.

## R9.5 Every requirement of the prompt, mapped to named code and tests

### EH-R8-2

| Requirement | Code | Test |
|---|---|---|
| `CANONICAL_GROUPS` carries exactly the four corrected explicit-member sets and the ruled `users` inverse row | `identity.CANONICAL_GROUPS` | `test_the_r9_corrected_inverse_rows_are_exact` |
| `PRE_EXISTING_PRIMARY_IN_INVERSE` and all tests / current-state prose treating those rows as an accepted hold are removed | the constant, its comment block and its `__all__` entry are gone; `CanonicalGroup` and the module docstring rewritten | `test_no_inverse_row_treats_a_primary_membership_as_an_explicit_one` asserts `not hasattr(identity, "PRE_EXISTING_PRIMARY_IN_INVERSE")` |
| the R8 handback account of what R8 submitted is preserved | §R8 and everything below it is untouched | — |
| every supplementary membership in `CANONICAL_ACCOUNTS` appears in the inverse | `_the_two_halves_of_the_table_agree`, direction 1 | `test_the_two_halves_of_the_canonical_table_agree_in_both_directions`; `test_the_table_cannot_be_edited_into_disagreement` cases 1 and 2 |
| every explicit inverse member is stated as supplementary by that account | same, direction 2 | same test; drift cases 3 and 5 |
| primary groups do not participate in the relation | the `account.primary_group == group.name` refusal, and the primary-also-supplementary refusal | drift cases 4 (five rows) and 6; `test_no_inverse_row_treats_a_primary_membership_as_an_explicit_one` |
| every canonical supplementary membership is represented in the inverse; `users = {foundry}` added exactly | `CanonicalGroup("users", frozenset({"foundry"}), …)` | `test_the_two_halves_of_the_canonical_table_agree_in_both_directions` names the six-pair relation exactly |
| no member inferred from the host or from outside the controlled table | direction 2's `CANONICAL_ACCOUNTS.get(member) is None` refusal | drift case 5; `test_no_test_in_this_suite_reads_the_host_account_database` |
| the accepted `postgres` row is preserved | `CANONICAL_ACCOUNTS["postgres"]`, unchanged | `test_the_ruled_postgres_row_is_in_both_halves_of_the_canonical_table`, `test_the_canonical_table_states_the_ruled_postgres_row_exactly_once` |
| `MembershipRule.EXACT`, fixed safe launch classifications, exact-one NSS lookup, manifest binding, guaranteed cleanup preserved | `boundary.py`, `executor.py`, `review_manifest.py`, `cleanup.py` — **all unchanged by R9** | `test_exact_is_the_only_membership_rule_that_exists`, `test_every_classification_the_boundary_can_return_is_in_the_fixed_set`, the four R6 duplicate-record tests, `test_executor_cleanup.py` — untouched and green |
| unexpected or missing supplementary membership refuses before process creation | `_resolve`, unchanged | `test_the_ruled_membership_missing_on_the_host_refuses`, `test_a_host_configured_group_outside_the_ruled_set_never_reaches_the_child`, `test_an_empty_ruled_set_passes_no_group_and_still_rejects_every_extra` (each asserts `recorder.calls == []`) |
| drift fails at import/validation | `_the_two_halves_of_the_table_agree()`, called at module scope | `test_the_table_cannot_be_edited_into_disagreement`, six cases |
| the corrected policy is covered by the review-manifest digest | `identity.py` ∈ `COVERED_SOURCES` | `test_changing_the_reviewed_postgres_policy_changes_the_manifest_digest`, extended to all six corrected rows |
| no test reads the host account database or starts a real process | injected `IdentityLookup` / `AccountDatabase`; synthetic tables written in the test files | `test_no_test_in_this_suite_reads_the_host_account_database` (AST, whole suite), `test_this_file_reads_no_account_and_starts_no_process`, and the structural guards in `test_no_execution.py`, none weakened |

### DS-R8-2

| Requirement | Code | Test |
|---|---|---|
| exit `2` no longer claims *"before touching anything"* for the runtime-role branch | the `# Exit codes:` header, rewritten per branch | `test_the_exit_code_contract_no_longer_claims_nothing_was_touched` |
| the operations guide no longer says *"nothing is dumped"* | `database-development.md`, runtime-role section | `test_the_operations_guide_states_the_runtime_role_refusal_accurately` |
| the precise statement — artifacts may exist, no drop, no restore, state intact, no recovery required | both refusal messages, the header, the guide | `test_the_runtime_role_refusal_leaves_the_dump_and_says_so` (asserts the four artifacts exist, `schema-grants.sql` does not, and the message says both halves), `test_the_malformed_role_refusal_makes_the_same_true_claim` |
| the ordering is stated where the decision is | step 3b's comment; the guide's *"Where these two refusals happen"* paragraph | `test_the_cardinality_test_no_longer_reads_a_string_its_separator_was_deleted_from`, now over code, with `pg_dump` asserted before the refusal |
| DS-R8-1's cardinality and role-name validation code preserved unless a regression exposes a defect | step 3b's executable statements, byte-identical | the seven DS-R8-1 regressions, all still green |
| tested statically or through the existing stubbed-client boundary; the drill is not run | the same PATH shim, and two source-reading tests | every DS-R8-2 test is static or uses `run_drill_against_stubs`; no database is contacted |

## R9.6 Verification — exact results from the final R9 tree

Run serially, in this order, against the tree being submitted, with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported:

| # | Command | Result |
|---|---|---|
| 1 | `venv … pytest -q -rs tests/phase_5_0_evidence` | **564 passed**, 0 failed, 0 skipped |
| 2 | `venv … pytest -q -rs tests/test_database_backup_restore.py tests/test_filesystem_layout.py` *(seven integration cases deselected — see below)* | **56 passed**, 0 failed, 0 skipped, **7 deselected** |
| 3 | `venv-web … pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **623 passed**, 0 failed, 0 skipped |
| 4 | `venv … pytest -q -rs tests/test_*.py` *(same seven deselected)* | **3147 passed**, 0 failed, 0 skipped, **7 deselected**, 1 warning (`audioop` deprecation, pre-existing) |
| 5 | `venv-web … pytest -q -rs tests/web` | **2840 passed, 80 skipped**, 0 failed — the 80 being the documented correct figure, all from the two matrix files' permitted cells |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass**, 0 fail, 0 skipped |
| 7 | `venv … compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | **clean** |
| 8 | `venv … -m tools.phase_5_0_evidence.execution.cli` | **dry run**, 64 / 39 / 42 / 16, digest `a3b59f2e…`, `executable: False` |
| 9 | `git diff --check` | **clean** |

### Not run by authority — the seven destructive drill integration cases

The prompt forbids executing the destructive backup/restore drill, and these
cases in `tests/test_database_backup_restore.py` run the real round trip
(dump → **drop schema** → restore) against `freedom_test`. They were
**deselected by node id, not skipped silently**, and pytest reported them as
deselected in runs 2 and 4:

1. `test_the_drill_accepts_an_explicit_unix_socket_directory`
2. `test_backup_and_restore_round_trip_preserves_data`
3. `test_the_drill_leaves_the_runtime_roles_privileges_intact`
4. `test_the_drill_fails_when_the_privilege_state_is_not_restored`
5. `test_the_drill_preserves_pristine_schema_ownership_and_privileges`
6. `test_the_drill_fails_when_schema_privileges_are_not_restored`
7. `test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure`

**Their substance is unchanged by R9** — no executable statement in the drill
changed, and the exact `sed`-pipeline and `psql -f "${SCHEMA_GRANTS}"` strings
cases 4 and 6 assert on are byte-identical to the R8 tree. They are **not claimed
to pass against this tree**; they need a maintainer-authorized run.
`test_recovery_instructions_match_database_development_documentation`, which is
static and reads the amended operations document, **was** run and passed.

The evidence-harness suite went from 561 to **564**: four regressions added and
two removed in `test_bands.py` (one renamed and generalized, one deleted with the
hold), plus the suite-wide account-database guard. The bot suite went from 3142
to **3147** with the same seven cases deselected — five DS-R8-2 regressions added.

**Determinism of the generated artifacts.** Both were generated **twice** into a
scratch directory and compared byte for byte before being written into
`docs/review/`, and the written files were then diffed against the second
generation:

- concrete plan, both generations: `sha256 feeee2008db396715abda45958712f567790c9c077e68b441ed608c6395a782d` — identical
- review manifest, both generations: `sha256 b9c85dfba07c9f5e20fd95dfd7476b164019389a35b1990e1ecd7285048ac675` — identical

Neither was hand-edited, and neither digest was copied into an execution command.
Every one of the 22 covered-source digests in the committed manifest was
independently re-hashed against the working tree: **22 checked, 0 mismatches.**

### The digest

| | Value |
|---|---|
| Review-manifest digest, R7 (**superseded**) | `15e131bfdce8fa8366aa97f19e233c249de4f1855492edac9a6fa4d758dcf176` |
| Review-manifest digest, R8 (**superseded**) | `5961403b3e9d1698b3a22bbe2e4fde2115bee9438ce53d0821f3fbf9f989d790` |
| Review-manifest digest, R9 | `a3b59f2e7075c8fdc9941f1f4b062329bfc10b0232aae33daa0d9e348ad0e165` |
| Target confirmation token (unchanged) | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#ceb58ad1f9f0e070` |

The R8 digest names a tree that no longer exists — `identity.py` is a covered
source and it changed — and **must never be passed to `--execute`**. The R9
digest is a value for Codex to review, not permission to execute, and the
executor refuses this plan regardless while its sixteen conflicts stand.

**What changed in the plan, and what did not.** A representation correction, not
a plan change. Every structural number is identical to R8 and R7: 64 steps, 39
mutations, 42 cleanup steps, 16 unresolved conflicts across C-2 … C-5,
`executable: False`. The only differences in either generated artifact are the
`identity.py` source digest and the aggregate digest that depends on it — which
is the property the design requires: the policy is inside the reviewed bytes.

## R9.7 Two judgement calls, flagged rather than buried

1. **`identity.R7_RULED_ACCOUNT` removed.** The prompt named
   `PRE_EXISTING_PRIMARY_IN_INVERSE` and not this. I removed it because its only
   purpose was to scope the guard to one row, its docstring said so explicitly,
   and prompt requirement 3 replaces that scoping with a whole-table relation —
   leaving the constant would have left a false sentence in a reviewed source.
   Nothing outside `identity.py` and one test line referenced it. If Codex would
   rather it stayed, it is a three-line restoration.
2. **The DS-R8-1 ordering assertion strengthened, not merely preserved.** Moving
   the header comment made the old assertion compare comment text; I could have
   re-anchored it on the new comment and left the weakness. Reading it over the
   already-computed comment-stripped `code` makes it assert the executable
   ordering instead, which is what its docstring always claimed. This is a test
   strengthened inside DS-R8-2's scope, not a DS-R8-1 redesign — the script's
   executable statements are unchanged.

## R9.8 What did not happen

- **Nothing was executed.** The CLI ran as a dry run only. `--execute`, the
  confirmation token and every reviewed digest were never passed.
- **No real `SubprocessBoundary` was armed**, and no generated vector ran.
- **No SSH connection was made**, and `oracle-test` was not contacted, read or
  mutated in any way.
- **No host account or group database was inspected.** Not by the harness, not by
  the tests, and not by me: the corrected rows were derived from §2.12.2's
  identity half, from Peter Duscha's ruling and from the documented meaning of the
  `getent group` fourth field. A new suite-wide AST guard now makes that a
  property of the suite rather than a statement in a handback.
- **No account or group was created, modified or removed anywhere.** The ruling
  is representational; it changes how §2.12.2 is written down, not what any host
  is configured to be.
- **No privileged or mutation-bearing command ran.**
- **No database operation of any kind was performed**, and **the destructive
  backup/restore drill was not run.** The DS-R8-2 tests never contact PostgreSQL:
  they read files, or run the script against stub executables on a temporary
  `PATH`.
- **No production or staging system was touched**, and no deployment or cutover
  step was taken.
- **No product application code, bot behavior, migration, schema, deployment
  file, roadmap, project status or RAID entry was changed**, and migration `0014`
  does not exist.
- **No other contributor's work was reset, reverted, staged, committed, pushed or
  deleted.** The worktree was dirty on arrival and is dirty in the same places,
  plus this remediation's files.

## R9.9 What this submission claims, and what it does not

**Claims:** the four ruled explicit-member sets and the ruled `users` inverse row
are applied exactly and change no account's memberships; the consistency guard now
covers the whole table in both directions and excludes primary membership from the
relation; the R8 hold and its scoping constant are gone with their prose; the
drill's exit-code contract, operations guide, refusal messages and tests now state
where the runtime-role refusal happens and what exists when it does; and the
checks in §R9.6 were run against this exact tree and produced those exact figures.

**Claims no:** execution approval, readiness consequence, assumption
confirmation, operational-check discharge, gate closure, or finding closure.
**Closing EH-R8-2 and DS-R8-2 is Codex's call, not mine.** Package 5.0 remains
`not ready`. **P5.0-R5 remains Blocking.** Checks C-1, C-3 and C-4 remain not run
— `JNL-52` can now pass on a correctly provisioned host, which is a precondition
for collecting C-4's evidence and is not that evidence. The sixteen unresolved
conflicts are unresolved, `executable` is `False`, and it should be. The seven
drill integration cases named in §R9.6 are **not run by authority** and are not
claimed to pass against this tree.

## R9.10 Request for Codex independent pre-execution re-review

R9 is returned to Codex for independent pre-execution re-review. The two
judgement calls in §R9.7 are the places I would rather be disagreed with
explicitly than not seen. No R9 result authorizes harness execution, privileged
evidence gathering, a database operation, a destructive drill or any Package 5.0
gate movement.

---

# R8 — the inverse-table semantics, and the backup drill's runtime-role cardinality

Date: 2026-09-06

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r8-prompt.md`. That prompt
authorizes unprivileged code, test, controlled-documentation and
generated-artifact work only, as **two independently authorized maintenance
slices**: EH-R8-1 is evidence-harness pre-execution remediation, DS-R8-1 is a
backup-drill correctness repair, and neither was used to widen the other. **It
does not authorize `--execute`, an armed `SubprocessBoundary`, execution of a
generated vector, SSH, host account or group inspection, any privileged or
mutation-bearing command, mutation of `oracle-test`, execution of the
destructive backup drill, Package 5.0 product implementation, migration `0014`,
production or staging mutation, deployment, cutover, OD-62's binding ruling, or
Package 5.1+. None of those occurred.**

Outcome: **both findings are conceded and corrected. Nothing was executed. No
finding is closed by this submission, no readiness item moves, no assumption is
confirmed, no operational check is discharged, and Package 5.0 remains `not
ready`; P5.0-R5 remains Blocking.**

## R8.0 The two findings, conceded before their corrections

### EH-R8-1 — Blocking. **Conceded in full.**

R7 added `CanonicalGroup("postgres", frozenset({"postgres"}))` to the group
inverse and widened the import-time guard to require an inverse row for
`account.supplementary | {account.primary_group}`. That was wrong, and it was
wrong in the precise way the finding states.

`ObservedGroup.members` is documented in the same module as *"the fourth field"*
of `getent group`. That field is a group's **explicit** member list. An account's
**primary** membership lives in its passwd record and does not appear there:
`useradd` does not add an account to its own primary group's member list, and
`getent group postgres` on a correctly provisioned host reports
`postgres:x:<gid>:` with the fourth field empty. `capture._group_members` parses
exactly that field and injects nothing.

So R7 turned the ruled fact *"`postgres`'s primary group is `postgres`"* into the
different, unruled fact *"the `postgres` group explicitly lists `postgres` as a
member"*, and `classify_group_membership` compares as an exact set. **A host
configured exactly as Peter Duscha ruled would have failed
`JNL-52-GROUP-postgres`**, `membership_matrix_holds()` would have returned false,
and every `JNL-52` access case gated on it would have been gated off — so the
positive PostgreSQL evidence R7 existed to unblock remained blocked. I did not
see this in R7; handback §R7.7 item 2 flagged the exactness of the two new
inverse rows as a judgement call but not the category error underneath it.

### DS-R8-1 — Important. **Conceded in full.**

The drill assigned `RUNTIME_ROLE="$(detect_runtime_role | tr -d '[:space:]')"`
and only then tested `RUNTIME_ROLE` for `$'\n'`. `tr` had already deleted every
newline, so **the ambiguity branch could never execute**. Two grantees arrived as
one concatenated identifier, the drill printed it as *"Runtime role: …"*, set
`SCHEMA_DROPPED=1`, dropped the `public` schema, and only discovered the problem
at step 5b when `runtime-grants.sql.tmpl` named a role that does not exist —
after the destructive step, with the disposable database empty and needing the
documented recovery.

## R8.1 Primary versus explicit membership, stated once

The two halves of §2.12.2 are **two different relations over one ruled fact
set**, not one relation written twice. R7 read them as the second.

| | Identity table (`CANONICAL_ACCOUNTS`) | Group inverse (`CANONICAL_GROUPS`) |
|---|---|---|
| What a row states | one account's **primary** group and its **complete** supplementary set | one group's **explicit** member list |
| What observes it | `id <name>` | the **fourth field** of `getent group <name>` |
| Where a *primary* membership appears | here | **never** |
| Where a *supplementary* membership appears | here, in `supplementary` | here, in `members` |
| Which classifier compares it | `classify_account_identity` | `classify_group_membership` |

A supplementary membership is therefore stated twice on purpose — that is stop
condition **10p**, and the reason the import-time guard exists. A primary
membership is stated **once**, in the identity table, because there is only one
place a host reports it.

## R8.2 The final inverse-table semantics, and every affected row

`CanonicalGroup.members` is now documented as **exact and explicit**: the fourth
field of `getent group`, containing supplementary members only.

| Group row | Members before R8 | Members after R8 | Why |
|---|---|---|---|
| `postgres` | `{postgres}` | **`{}`** | corrected. `postgres` is the account's *primary* group, so its explicit list is empty. The row is **kept**, not dropped: the empty set is a claim worth failing on — an account explicitly added to `postgres` would hold the cluster's data directory through a group, and that is a finding — and dropping the row would make `JNL-52-GROUP-postgres` unclassifiable instead. Emptiness is not a new ruling: §2.12.2's identity half is complete and no identity row names `postgres` as a supplementary group, so the empty set is what the controlled table already implies |
| `ssl-cert` | `{postgres}` | `{postgres}` | **unchanged.** This is the ruled *supplementary* membership, so it is an explicit `getent group` member and it is listed exactly once |
| `freedomjournal` | `{freedomcoord, freedomsheet}` | unchanged | both are supplementary memberships; already correct |
| `sudo` | `{foundry}` | unchanged | supplementary; already correct |
| `freedomcoord` | `{freedomcoord}` | **unchanged — reported, not corrected** | see §R8.3 |
| `freedomsheet` | `{freedomsheet}` | **unchanged — reported, not corrected** | see §R8.3 |
| `discordbot` | `{discordbot, freedomweb}` | **unchanged — reported, not corrected** | `freedomweb` is correct (supplementary); `discordbot` is the same error. See §R8.3 |
| `fbprobe` | `{fbprobe}` | **unchanged — reported, not corrected** | see §R8.3 |

The ruled facts are untouched: primary group `postgres`, complete supplementary
set exactly `ssl-cert`, `provisioned_by_package=False`. **No new membership
ruling was sought or inferred**, and no host was inspected.

## R8.3 The audit of the rest of the table — reported, and deliberately not fixed

Prompt requirement 6 asked me to audit the other canonical rows for the same
representation error and to stop before widening. **Four pre-existing rows have
it.**

`freedomcoord`, `freedomsheet`, `discordbot` and `fbprobe` each list, in their
inverse row, the account whose *primary* group they are.

**Exact impact.** On a host provisioned as §2.12.2 and §2.13.3 require:

- `getent group freedomcoord`, `getent group freedomsheet` and
  `getent group fbprobe` report an **empty** fourth field — provisioning creates
  each account with that primary group and adds it to no explicit list;
- `getent group discordbot` reports `freedomweb` alone — the `freedomweb`
  membership is a real supplementary one and is correctly stated; the
  `discordbot` entry beside it is not;
- `classify_group_membership` compares as an exact set, so all four
  `JNL-52-GROUP-*` cases **fail**, each reporting the account as a *missing*
  member;
- `membership_matrix_holds()` is then false, and every `JNL-52` access case that
  reads it as a precondition is gated off.

**This is a `JNL-52` correctness defect on a correctly configured host, not an
execution-safety one.** It fails closed: nothing runs on the strength of a
failed case, and no credential is widened by it.

**Why R8 does not correct it.** These four rows are §2.12.2 *policy* for
identities that neither the R7 ruling nor this prompt touches, and correcting
them is not mechanically required to make the `postgres` row internally truthful
— the corrected import-time guard is scoped to the ruled row and passes without
them changing. Changing them would be a membership decision I have no authority
to make, and the prompt is explicit: *"report them with exact impact and stop
before widening"*. They are therefore recorded in three places and left exactly
as found:

1. `identity.PRE_EXISTING_PRIMARY_IN_INVERSE`, a documented constant in the
   reviewed source, so a reader of the covered file sees the defect;
2. package-plan §2.12.2's R8 amendment, under *"Reported, not corrected"*; and
3. `test_the_pre_existing_primary_in_inverse_rows_are_reported_not_changed`,
   which pins the set in **both** directions — it fails if one is silently
   corrected without a ruling, and it fails if a fifth appears.

**This is a decision request for the Security Reviewer and the maintainer, not a
finding I am closing.**

## R8.4 The import-time guard, rewritten

`_the_ruled_row_is_stated_in_both_tables()` no longer unions the primary group
into the explicit-member relation. It checks the **supplementary** membership in
both directions:

1. every group `postgres`'s identity row names as supplementary has an inverse
   row, and that row lists `postgres`; and
2. every inverse row that lists `postgres` is one the identity row names as
   supplementary.

Direction 2 is new, and it is what makes R7's representation an **import
failure** rather than a silent regression: writing the account back into its own
primary group's row makes that row list an account whose supplementary set does
not contain it, and the refusal names EH-R8-1.

The primary group continues to be verified where a host actually reports it:
`CanonicalAccount.primary_group` against `id`, in `classify_account_identity`,
and through the credential chain `_from_canonical` → `RequiredIdentity.__post_init__`
→ `_resolve`.

The guard remains scoped to the ruled row, for the reason §R8.3 gives.

## R8.5 Runtime-role cardinality — how it is preserved, and where refusal occurs

**Preserved.** `detect_runtime_role`'s output is captured whole into
`RUNTIME_ROLE_REPORT` by a plain command substitution — which strips *trailing*
newlines and preserves internal ones, and which still fails the drill under
`set -e` if `psql` fails — and then split into `RUNTIME_ROLE_ROWS` by
`while IFS= read -r`. A line that is empty or entirely blank is skipped rather
than counted, because that is what a zero-row `psql -tA` result looks like.
Nothing *inside* a record is touched at that point. Cardinality is answered by
`${#RUNTIME_ROLE_ROWS[@]}`, a count of records, not by inspecting a string the
separator has been deleted from.

**Where refusal occurs.** All of this is in **step 3b**. `SCHEMA_DROPPED=1` and
`DROP SCHEMA public CASCADE` are in **step 4**. The ordering is asserted
textually against the script itself, so it is a property of the file rather than
of one execution:
`test_the_cardinality_test_no_longer_reads_a_string_its_separator_was_deleted_from`
requires `index(refusal) < index("SCHEMA_DROPPED=1") < index("DROP SCHEMA public CASCADE")`.

**The three answers.**

- **zero rows** — the existing documented no-runtime-role path, unchanged: step
  5b prints *"Skipped: no runtime role held grants before the destroy."*
- **exactly one row** — only now is the name extracted. Surrounding whitespace is
  trimmed with parameter expansion; **nothing internal is stripped and nothing is
  concatenated**, so a malformed name stays visibly malformed. It is then
  validated against `^[A-Za-z_][A-Za-z0-9_]{0,62}$` — a plain unquoted PostgreSQL
  identifier within `NAMEDATALEN`. Anything else exits **2** before the schema is
  dropped and before the name reaches `sed` or SQL. The rule is deliberately
  narrower than PostgreSQL allows (`$` is a legal identifier character; a quoted
  role may contain anything): every supported runtime role in this repository —
  `freedom_runtime`, `freedom_runtime_test` — has this shape, and every excluded
  character is special to `sed`'s replacement text, to the shell, or to SQL. No
  unvalidated role is interpolated anywhere.
- **more than one row** — exit **2**, naming the roles found, before
  `SCHEMA_DROPPED=1`.

The query itself is unchanged and remains non-interactive. **The schema-owner /
ACL artifact, its checksum and the recovery-instruction remediation already in
the dirty tree were not reverted or redesigned**; steps 3c, 5b, 6 and 6b are
untouched, and the exact `sed`-pipeline string that
`test_the_drill_fails_when_the_privilege_state_is_not_restored` matches on is
byte-identical.

## R8.6 Files changed, and why

| File | Why |
|---|---|
| `tools/phase_5_0_evidence/identity.py` | EH-R8-1: `CanonicalGroup` documented as the **explicit** `getent group` relation; the `postgres` inverse row's members corrected to the empty set; the import-time guard rewritten to check the supplementary membership in both directions without unioning the primary group; `PRE_EXISTING_PRIMARY_IN_INVERSE` added as the reported audit of the four pre-existing rows; module docstring states the two-relation distinction |
| `tests/phase_5_0_evidence/test_bands.py` | EH-R8-1 regressions: the corrected `JNL-52` classification, the guard's new direction, the account-side primary-group check, and the pinned audit |
| `tests/phase_5_0_evidence/test_boundary_identity.py` | the two canonical-row assertions corrected to the explicit-member representation, and the manifest-digest test extended to cover the corrected inverse row |
| `docs/review/phase-5-0-package-plan.md` | §2.12.2 only: the R8 amendment defining the member column's semantics, the corrected `postgres` inverse row, and the *"reported, not corrected"* record of the four pre-existing rows |
| `infra/postgresql/backup-restore-drill.sh` | DS-R8-1: record-preserving cardinality decision in step 3b, the reachable multiple-role refusal, role-name validation before any interpolation, and the corrected exit-code documentation |
| `tests/test_database_backup_restore.py` | DS-R8-1 regressions, run against a non-destructive stubbed client boundary |
| `docs/operations/database-development.md` | the drill's contract changed: a new documented `2` refusal and the role-name rule |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated; never hand-edited |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated; never hand-edited |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section |
| `docs/review/Handover information` | R8 identified as the current handover, all previous handovers preserved below |

Nothing else was touched. No product application code, bot behavior, migration,
database schema, deployment file, roadmap, project status, RAID entry, unrelated
decision, or accepted `postgres` supplementary-group ruling was changed, and the
rest of the dirty worktree — other contributors' in-flight work — was preserved
exactly as found. **No change-log entry was written**: the prompt's expected-change
list does not include it, and R8 records no new governance decision.

## R8.7 Every requirement of the prompt, mapped to named code and tests

### EH-R8-1

| Requirement | Code | Test |
|---|---|---|
| the R7 ruling is preserved exactly — primary `postgres`, supplementary exactly `ssl-cert` | `identity.CANONICAL_ACCOUNTS["postgres"]`, unchanged | `test_the_ruled_postgres_row_is_in_both_halves_of_the_canonical_table`, `test_the_canonical_table_states_the_ruled_postgres_row_exactly_once` |
| the inverse table's semantics are defined precisely | `CanonicalGroup` docstring; module docstring; package plan §2.12.2 R8 amendment | `test_a_primary_group_is_not_an_explicit_getent_group_member` |
| the false requirement that the `postgres` row list `postgres` is removed | `CanonicalGroup("postgres", frozenset(), …)` | `test_the_ruled_postgres_row_is_in_both_halves_of_the_canonical_table` asserts `frozenset()`; `test_a_primary_group_is_not_an_explicit_getent_group_member` proves the empty observation now **passes** |
| the guard verifies supplementary membership in both directions without unioning the primary group | `_the_ruled_row_is_stated_in_both_tables` | `test_the_ruled_row_cannot_be_stated_in_only_one_of_the_two_tables` (three refusal cases, including the re-introduced R7 representation) |
| the primary group is still verified through the account row and classifier | `classify_account_identity`; `_from_canonical` → `RequiredIdentity.__post_init__` → `_resolve` | `test_the_account_side_still_decides_the_primary_group`, `test_the_contract_row_is_derived_from_the_canonical_row` |
| `ssl-cert -> postgres` stays exact | `CANONICAL_GROUPS["ssl-cert"]`, unchanged | `test_a_primary_group_is_not_an_explicit_getent_group_member` (missing → FAILED, unexpected → FAILED) |
| `ssl-cert` lists `postgres` exactly once | the set is a `frozenset` of one | `test_the_ruled_postgres_row_is_in_both_halves_of_the_canonical_table` asserts the count |
| an observed `postgres` group with no explicit members is not rejected | `classify_group_membership` | `test_a_primary_group_is_not_an_explicit_getent_group_member` |
| a missing or unexpected supplementary group still refuses before a process exists | `_resolve`, unchanged | `test_the_ruled_membership_missing_on_the_host_refuses`, `test_a_host_configured_group_outside_the_ruled_set_never_reaches_the_child` (both assert `recorder.calls == []`) |
| the other canonical rows are audited and reported, not silently changed | `identity.PRE_EXISTING_PRIMARY_IN_INVERSE`; §R8.3 | `test_the_pre_existing_primary_in_inverse_rows_are_reported_not_changed` |
| the corrected policy is covered by the review-manifest digest | `identity.py` ∈ `COVERED_SOURCES` | `test_changing_the_reviewed_postgres_policy_changes_the_manifest_digest`, extended to the corrected inverse row |
| `MembershipRule.EXACT`, the fixed `LAUNCH_FAILURES` vocabulary, manifest binding, R5 cleanup and R6 exact-one NSS lookup preserved | `boundary.py`, `executor.py`, `review_manifest.py` — **all unchanged by R8** | `test_exact_is_the_only_membership_rule_that_exists`, `test_every_classification_the_boundary_can_return_is_in_the_fixed_set`, the four R6 duplicate-record tests, `test_executor_cleanup.py` — all untouched and green |
| no test reads the real host account/group database or starts a process | injected `IdentityLookup` / `AccountDatabase` | `test_this_file_reads_no_account_and_starts_no_process`; the structural guards in `test_no_execution.py`, none weakened |

No test was weakened to accept both the old and corrected representations: every
assertion on the `postgres` inverse row states `frozenset()` exactly, and the
guard test refuses the old representation explicitly.

### DS-R8-1

| Requirement | Code | Test |
|---|---|---|
| record boundaries preserved while deciding zero / one / more | `RUNTIME_ROLE_REPORT` + `RUNTIME_ROLE_ROWS` array | `test_the_cardinality_test_no_longer_reads_a_string_its_separator_was_deleted_from` |
| more than one distinct row refuses with exit `2` | step 3b | `test_two_distinct_runtime_roles_refuse_with_exit_status_two` |
| the refusal precedes `SCHEMA_DROPPED=1` and `DROP SCHEMA` | step 3b precedes step 4 | `test_the_multiple_role_refusal_happens_before_the_schema_is_dropped` (no `DROP SCHEMA` and no `pg_restore` in the invocation log, no `RECOVERY REQUIRED`); the textual ordering assertion in the static test |
| the name is extracted only after exactly one row is established; nothing internal stripped or concatenated | trim-ends parameter expansion after the count | `test_one_runtime_role_is_retained_exactly_and_reaches_grant_reapplication` |
| zero rows keep the documented no-runtime-role path | the `== 0` branch | `test_zero_runtime_roles_follow_the_existing_empty_path` |
| the query stays non-interactive; no unvalidated role reaches `sed` or SQL | `psql -tAX -v ON_ERROR_STOP=1`, unchanged; `^[A-Za-z_][A-Za-z0-9_]{0,62}$` | `test_a_role_name_that_is_not_a_plain_identifier_refuses_before_any_destruction` (8 cases: dash, space, `;`-injection, slash, embedded quote, leading digit, `$`, 64 characters) |
| whitespace removal cannot concatenate two records into an accepted role | the count precedes the trim | `test_whitespace_removal_cannot_concatenate_two_records_into_one_role` — `app` + `role` must refuse, and `approle` must appear in no output and no log |
| the schema-owner / ACL / checksum remediation is preserved, not reverted | steps 3c, 5b, 6, 6b — unchanged | `test_recovery_instructions_match_database_development_documentation` (run); the seven integration cases in §R8.8 (**not run by authority**) |
| the drill is not run under this prompt | — | every DS-R8-1 test runs against a stubbed `psql`/`pg_dump`/`pg_restore` PATH shim; no database is contacted |

**The non-destructive boundary, and its control.** The DS-R8-1 tests run the
**real drill script** with a temporary `PATH` whose `psql`, `pg_dump` and
`pg_restore` are stubs that answer the gate-0e query, return a scripted grantee
list, and append every invocation to a log. That log is what makes *"the refusal
happened before the destructive command"* an assertion rather than an inference.
`test_one_runtime_role_is_retained_exactly_and_reaches_grant_reapplication` is
the **positive control**: through the same shim, with one well-formed role, the
drill does reach `DROP SCHEMA` and does report `Restore verified`, so an absent
drop in the refusal tests is attributable to the refusal and not to the shim.
No database was created, connected to, dumped, dropped or restored.

## R8.8 Verification — exact results from the final R8 tree

Run serially, in this order, against the tree being submitted, with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported:

| # | Command | Result |
|---|---|---|
| 1 | `venv … pytest -q -rs tests/phase_5_0_evidence` | **561 passed**, 0 failed, 0 skipped |
| 2 | `venv … pytest -q -rs tests/test_database_backup_restore.py tests/test_filesystem_layout.py` *(seven integration cases deselected — see below)* | **51 passed**, 0 failed, 0 skipped, **7 deselected** |
| 3 | `venv-web … pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **620 passed**, 0 failed, 0 skipped |
| 4 | `venv … pytest -q -rs tests/test_*.py` *(same seven deselected)* | **3142 passed**, 0 failed, 0 skipped, **7 deselected**, 1 warning (`audioop` deprecation, pre-existing) |
| 5 | `venv-web … pytest -q -rs tests/web` | **2840 passed, 80 skipped**, 0 failed — the 80 being the documented correct figure, all from the two matrix files' permitted cells |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass**, 0 fail, 0 skipped |
| 7 | `venv … compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | **clean** |
| 8 | `venv … -m tools.phase_5_0_evidence.execution.cli` | **dry run**, 64 / 39 / 42 / 16, digest `5961403b…`, `executable: False` |
| 9 | `git diff --check` | **clean** |

The evidence-harness suite went from 558 to **561**: three regressions added, and
three existing tests extended in place rather than duplicated
(`test_the_ruled_postgres_row_is_in_both_halves_of_the_canonical_table`,
`test_the_ruled_row_cannot_be_stated_in_only_one_of_the_two_tables`,
`test_changing_the_reviewed_postgres_policy_changes_the_manifest_digest`).
The bot suite went from 3135 to **3142** with seven cases deselected — **14**
DS-R8-1 regressions added, seven integration cases withheld.

### Not run by authority — the seven destructive drill integration cases

The prompt forbids executing the destructive backup/restore drill, and these
cases in `tests/test_database_backup_restore.py` run the real round trip
(dump → **drop schema** → restore) against `freedom_test`. They were
**deselected by node id, not skipped silently**, and pytest reported them as
deselected in runs 2 and 4:

1. `test_the_drill_accepts_an_explicit_unix_socket_directory`
2. `test_backup_and_restore_round_trip_preserves_data`
3. `test_the_drill_leaves_the_runtime_roles_privileges_intact`
4. `test_the_drill_fails_when_the_privilege_state_is_not_restored`
5. `test_the_drill_preserves_pristine_schema_ownership_and_privileges`
6. `test_the_drill_fails_when_schema_privileges_are_not_restored`
7. `test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure`

**Their substance is unchanged by R8** — steps 3c, 5b, 6 and 6b are untouched,
and the exact `sed`-pipeline and `psql -f "${SCHEMA_GRANTS}"` strings that cases
4 and 6 assert on are byte-identical to the R7 tree. They are **not claimed to
pass against this tree**; they need a maintainer-authorized run.
`test_recovery_instructions_match_database_development_documentation`, which is
static, **was** run and passed, including against the amended operations
document.

The evidence-harness suite went from 561 to **564**: four regressions added and
two removed in `test_bands.py` (one renamed and generalized, one deleted with the
hold), plus the suite-wide account-database guard. The bot suite went from 3142
to **3147** with the same seven cases deselected — five DS-R8-2 regressions added.

**Determinism of the generated artifacts.** Both were generated **twice** into a
scratch directory and compared byte for byte before being written into
`docs/review/`, and the written files were then diffed against the first
generation:

- concrete plan, both generations: `sha256 e160395ed584e7b2ed22a6f35476068136f1bd19bf70431e756b70607aa649eb` — identical
- review manifest, both generations: `sha256 dbaa03a222de3a1257cb5a4a5cdba59255eef56148e52506b944bcd089bdee66` — identical

Neither was hand-edited, and neither digest was copied into an execution
command. Every one of the 22 covered-source digests in the committed manifest was
independently re-hashed against the working tree: **22 checked, 0 mismatches.**

### The digest

| | Value |
|---|---|
| Review-manifest digest, R6 (**superseded**) | `18bb5ccd1cc0845b2bbc397b0acb4943b6c1f2d02ad8b3f64590905f942a9fc6` |
| Review-manifest digest, R7 (**superseded**) | `15e131bfdce8fa8366aa97f19e233c249de4f1855492edac9a6fa4d758dcf176` |
| Review-manifest digest, R8 | `5961403b3e9d1698b3a22bbe2e4fde2115bee9438ce53d0821f3fbf9f989d790` |
| Target confirmation token (unchanged) | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#ceb58ad1f9f0e070` |

The R7 digest names a tree that no longer exists — `identity.py` is a covered
source and it changed — and **must never be passed to `--execute`**. The R8
digest is a value for Codex to review, not permission to execute, and the
executor refuses this plan regardless while its sixteen conflicts stand.

**What changed in the plan, and what did not.** A representation correction, not
a plan change. Every structural number is identical to R7: 64 steps, 39
mutations, 42 cleanup steps, 16 unresolved conflicts across C-2 … C-5,
`executable: False`. Only the digest moved, which is the property the design
requires — the policy is inside the reviewed bytes.

## R8.9 What did not happen

- **Nothing was executed.** The CLI ran as a dry run only. `--execute`, the
  confirmation token and every reviewed digest were never passed.
- **No real `SubprocessBoundary` was armed**, and no generated vector ran.
- **No SSH connection was made**, and `oracle-test` was not contacted, read or
  mutated in any way.
- **No host account or group database was inspected.** Not by the harness, not by
  the tests, and not by me to decide the corrected representation — it was
  derived from the controlled table and from the documented meaning of the
  `getent group` fourth field, not from a host. Every identity test injects a
  synthetic account database written in the test file.
- **No privileged or mutation-bearing command ran.**
- **No database operation of any kind was performed**, and **the destructive
  backup/restore drill was not run.** The DS-R8-1 tests never contact
  PostgreSQL: they run the script against stub executables on a temporary
  `PATH`.
- **No production or staging system was touched**, and no deployment or cutover
  step was taken.
- **No product application code, bot behavior, migration, schema, deployment
  file, roadmap, project status or RAID entry was changed**, and migration
  `0014` does not exist.
- **No other contributor's work was reset, reverted, staged, committed, pushed or
  deleted.** The worktree was dirty on arrival and is dirty in the same places,
  plus this remediation's files.

## R8.10 What this submission claims, and what it does not

**Claims:** EH-R8-1's representation error is corrected without changing the
ruled membership; DS-R8-1's ambiguity guard is reachable and its refusal precedes
the destructive step; the four pre-existing rows with the same shape are reported
with their exact impact and left unchanged; and the checks in §R8.8 were run
against this exact tree and produced those exact figures.

**Claims no:** execution approval, readiness consequence, assumption
confirmation, operational-check discharge, gate closure, or finding closure.
**Closing EH-R8-1 and DS-R8-1 is Codex's call, not mine.** Package 5.0 remains
`not ready`. **P5.0-R5 remains Blocking.** Checks C-1, C-3 and C-4 remain not
run. The sixteen unresolved conflicts are unresolved, `executable` is `False`,
and it should be. The seven drill integration cases named in §R8.8 are **not run
by authority** and are not claimed to pass against this tree.

## R8.11 Request for Codex independent pre-execution re-review

R8 is returned to Codex for independent re-review. Two things in it are
decisions rather than mechanical corrections, and I would rather they were
disagreed with explicitly than not seen:

1. **Keeping the `postgres` inverse row with an empty member set**, rather than
   deleting it. The prompt permitted either. I kept it because the empty set is
   a claim worth failing on and deleting the row would make
   `JNL-52-GROUP-postgres` unclassifiable — but the empty set is a claim the
   ruling did not itself make, derived from the completeness of §2.12.2's
   identity half. If Codex would rather primary groups were simply outside the
   inverse, that is a one-row deletion in each table.
2. **The four pre-existing rows in §R8.3, left unchanged.** They are a real
   `JNL-52` correctness defect on a correctly configured host. Correcting them
   is a membership decision, and I have no authority to make it. **This needs a
   maintainer ruling or an explicit Codex instruction**, and until it has one,
   `JNL-52`'s group half cannot pass on a correctly provisioned host.

No R8 result authorizes harness execution, privileged evidence gathering, a
database operation, a destructive drill or any Package 5.0 gate movement.

---

# R7 — the ruled `postgres` membership

Date: 2026-09-06

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r7-prompt.md`, **and gated on
the maintainer ruling that prompt requires**. That prompt authorizes unprivileged
code, test, controlled-documentation and generated-artifact work only. **It does
not authorize `--execute`, an armed `SubprocessBoundary`, execution of a
generated vector, SSH, host account or group inspection, any privileged or
mutation-bearing command, mutation of `oracle-test`, Package 5.0 product
implementation, migration `0014`, deployment, cutover, OD-62's binding ruling, or
Package 5.1+. None of those occurred.**

Outcome: **EH-R6-1's blocked positive half is now corrected. EH-R6-2 was Closed
by Codex against R6 and is preserved unchanged. Nothing was executed. No finding
is closed by this submission, no assumption is confirmed, no readiness item
moves, and Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.**

## R7.0 The ruling this remediation was gated on

The R7 prompt authorized no change until Peter Duscha recorded two facts. Both
were recorded on **2026-09-06**, in this session, after the prompt's decision
request was returned to him:

| # | Fact required by the prompt | Ruling |
|---|---|---|
| 1 | whether R6 handback **§R6.4 Option A** is accepted | **Accepted**, on Codex's recommendation |
| 2 | the exact **complete** supplementary-group set permitted for the `postgres` operating-system account | **exactly `ssl-cert`**, with primary group `postgres` |

The maintainer's words, quoted rather than paraphrased, were: *"I have no idea
about the decisions so I can't decide this. Therefore, go with codexes
recommendations, please."* — which supplied fact 1 and **not** fact 2, Codex's
recommendation being explicitly *"not a maintainer ruling"* that *"does not
select the group set"*. The set was therefore put back to him as a separate,
single question with the three candidate answers priced, and he selected
**`ssl-cert` only**. No set was inferred, no host was inspected to produce one,
and the prompt's prohibition on inferring `ssl-cert` was not treated as
satisfied by Codex's *"very likely"* remark in §R6.4.

The ruling is now controlled: package-plan **§2.12.2** carries it, and change-log
**C-P5.0-AE** is the governance record that makes it so.

**What the ruling does not do.** It grants no execution authority, confirms no
assumption, closes no readiness item, and moves no gate. It decides one
membership.

## R7.1 The findings, stated before the corrections

### EH-R6-1 — Blocking. **Conceded, and it remained Blocking before this remediation.**

R6 removed R5's `MembershipRule.AS_CONFIGURED` pass-through and made the
`postgres` row `UNDECIDED`, which fails closed. That was the correct half. The
half R6 could not do was state the permitted set, because no controlled source
did — §2.12.2 covered six identities and `postgres` was not one of them. The
consequence, conceded plainly: **the PostgreSQL evidence and the `psql` cleanup
reversals could not execute at all.** R6 was a hold, not a resolution, and Codex
was right to leave the finding Blocking.

### EH-R6-2 — Important. **Closed by Codex against R6, and preserved.**

Codex's re-review confirmed that account and group records are counted rather
than deduplicated, that the direct `getpwnam`/`getgrnam` answer must agree with
the sole enumerated record in name and both numbers, and that the safe failure
vocabulary is preserved. **R7 changes nothing in `SystemIdentityLookup` or
`SystemAccountDatabase`**, and the tests that hold the finding closed are
untouched and still pass — `test_two_account_records_refuse_however_they_are_numbered`,
`test_two_group_records_refuse_however_they_are_numbered`,
`test_a_direct_answer_that_contradicts_the_one_record_refuses` and
`test_zero_matching_records_are_absent_rather_than_inconsistent`.

## R7.2 Review evidence reproduced before editing

The R6 disposition was reproduced against the unedited tree before anything was
changed, so that what follows is a difference from a verified starting point
rather than from a described one:

| Check | R6 disposition | Reproduced here |
|---|---|---|
| `pytest tests/phase_5_0_evidence` | 550 passed | **550 passed** |
| `compileall` | clean | **clean** |
| CLI dry run | 64 steps, 39 mutations, 42 cleanup steps, 16 unresolved conflicts | **identical** |
| digest | `18bb5ccd1cc0845b2bbc397b0acb4943b6c1f2d02ad8b3f64590905f942a9fc6` | **identical** |
| `executable` | `False` | **`False`** |

**The R6 digest is superseded.** Covered sources changed, so
`18bb5ccd…` names a tree that no longer exists and must never be passed to
`--execute`. The R7 digest is
`15e131bfdce8fa8366aa97f19e233c249de4f1855492edac9a6fa4d758dcf176`, and it is
**not** execution authority either.

## R7.3 Files changed, and why

| File | Why |
|---|---|
| `docs/review/phase-5-0-package-plan.md` | §2.12.2 gains **one** `postgres` identity row and the two inverse group rows it requires, plus a dated amendment note stating the ruling and its three limits |
| `docs/project-management/change-log.md` | **C-P5.0-AE**, the single governance record that makes the ruling controlled. No other change-log content is touched |
| `tools/phase_5_0_evidence/identity.py` | the canonical row, transcribed once; the two inverse group rows; and one import-time guard that the ruled row is stated in both halves of the table |
| `tools/phase_5_0_evidence/execution/boundary.py` | the `UNDECIDED` row becomes `_from_canonical("postgres")`; `MembershipRule.UNDECIDED`, `MembershipUndecided` and `UNDECIDED_MEMBERSHIP` are **deleted**; the module contract and one classification comment are corrected |
| `tools/phase_5_0_evidence/execution/executor.py` | one comment only. It said `postgres` *"cannot run"*; it now states the ruled membership and the run-as/act-on distinction. `PERMITTED_RUN_AS` is derived and unchanged in form |
| `tests/phase_5_0_evidence/test_boundary_identity.py` | the credential regressions |
| `tests/phase_5_0_evidence/test_bands.py` | the canonical-table and `JNL-52` regressions |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated; never hand-edited |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated; never hand-edited |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section |
| `docs/review/Handover information` | R7 identified as returned to Codex, prior handovers preserved below |

Nothing else was touched. No product application code, migration, schema,
deployment file, infrastructure script, roadmap, project status, RAID entry or
unrelated decision was changed, and the rest of the dirty worktree — other
contributors' in-flight work — was preserved exactly as found.

## R7.4 The canonical row, traced through to the credential

The point of the design is that the membership is stated **once**. Here is the
whole path, in order:

1. **§2.12.2**, the canonical membership table — the ruled row, in prose and in
   both of the table's halves.
2. **`identity.CANONICAL_ACCOUNTS["postgres"]`** —
   `CanonicalAccount("postgres", "postgres", frozenset({"ssl-cert"}), "not asserted", False)`.
   The transcription, and the only place the set appears in code.
3. **`identity.CANONICAL_GROUPS`** — `ssl-cert` and `postgres` inverse rows,
   each listing `postgres` exactly.
4. **`identity._the_ruled_row_is_stated_in_both_tables()`**, run at import: the
   groups the identity row names have inverse rows, and those rows list the
   account back. A half-stated membership fails the **import**.
5. **`boundary._from_canonical("postgres")`** — reads (2). It restates nothing.
6. **`RequiredIdentity.__post_init__`** — refuses, while the contract table is
   being built, any row that disagrees with (2) in primary group, supplementary
   set or provisioning flag.
7. **`resolve_credential` → `_resolve`** — unconditional set **equality** in
   both directions against (2), then each name resolved to a numeric gid.
8. **`SubprocessBoundary.run`** — `user=`, `group=` and `extra_groups=` all three
   passed explicitly, from (7), before `subprocess.run` exists.
9. **`executor.PERMITTED_RUN_AS`** — `frozenset(IDENTITY_CONTRACT)`, derived, so
   the names a step may name cannot drift from the contract.
10. **`review_manifest.COVERED_SOURCES`** — contains `identity.py`, so (2) is
    inside the digest. Changing the ruled policy changes the digest.

There is no step in that chain where a host's configuration contributes to the
permitted set, and no branch that substitutes a default for something it could
not resolve.

## R7.5 Every requirement of the prompt, mapped to code and tests

| Requirement | Code | Test |
|---|---|---|
| §2.12.2 contains exactly one `postgres` row with the ruled primary and complete supplementary set | package plan §2.12.2 | `test_the_canonical_table_states_the_ruled_postgres_row_exactly_once` |
| the inverse group-to-members table is updated consistently | §2.12.2 inverse; `CANONICAL_GROUPS` | same test; `test_the_ruled_row_cannot_be_stated_in_only_one_of_the_two_tables` |
| `postgres` added once to `CANONICAL_ACCOUNTS`, transcribed exactly, marked an existing host identity | `identity.py` | `test_the_canonical_table_states_the_ruled_postgres_row_exactly_once` (asserts `provisioned_by_package is False`) |
| `IDENTITY_CONTRACT["postgres"]` is `_from_canonical(...)` and `EXACT` | `boundary.py` | `test_the_contract_row_is_derived_from_the_canonical_row` |
| `UNDECIDED` and `UNDECIDED_MEMBERSHIP` removed entirely; no unused escape hatch; no second policy source | `boundary.py` | `test_exact_is_the_only_membership_rule_that_exists` |
| unconditional exact set equality preserved | `_resolve`, unchanged | `test_a_host_configured_group_outside_the_ruled_set_never_reaches_the_child`, `test_the_ruled_membership_missing_on_the_host_refuses` |
| a missing or unexpected group refuses **before** the account database is read far enough to create a process | `_resolve`, before `subprocess.run` | both of the above assert `recorder.calls == []` |
| no parent or host-configured group outside the canonical set reaches `extra_groups=` | `_resolve` returns `required.supplementary` only | `test_the_postgres_credential_does_not_move_with_the_launchers_groups` |
| the exact numeric GIDs reach `extra_groups=` in deterministic order | `_resolve` sorts names, then numbers | `test_extra_groups_is_a_sorted_list_of_numbers_and_does_not_vary`, `test_the_ruled_postgres_set_reaches_the_child_as_its_numeric_gid` |
| an empty ruled set passes `extra_groups=[]` and still rejects every unexpected group | `_resolve` | `test_an_empty_ruled_set_passes_no_group_and_still_rejects_every_extra` |
| changing the parent process's groups cannot change the child credential | `_resolve` reads no caller state | `test_the_postgres_credential_does_not_move_with_the_launchers_groups`, `test_changing_the_parent_processs_groups_cannot_change_the_child_keywords` |
| changing the canonical `postgres` policy changes the review-manifest digest | `identity.py` ∈ `COVERED_SOURCES` | `test_changing_the_reviewed_postgres_policy_changes_the_manifest_digest` |
| canonical/contract drift fails closed | `RequiredIdentity.__post_init__` | `test_the_contract_cannot_drift_from_the_canonical_table` (four cases: widened, narrowed, re-labelled, uncovered account) |
| identical and contradictory duplicate records still refuse — EH-R6-2 preserved | `SystemIdentityLookup`, **unchanged** | the four R6 duplicate-record tests, untouched |
| the fixed safe `LAUNCH_FAILURES` vocabulary is preserved | `boundary.py` | `test_every_classification_the_boundary_can_return_is_in_the_fixed_set`, `test_no_classification_carries_lookup_or_operating_system_text` |
| R5's guaranteed-cleanup behaviour is preserved | `executor.py`, unchanged in substance | `test_executor_cleanup.py`, untouched |
| no test reads the real account/group database or starts a real process | injected `IdentityLookup` / `AccountDatabase` | `test_this_file_reads_no_account_and_starts_no_process`, and the structural tests in `test_no_execution.py`, none weakened |

## R7.6 What the empty-set requirement is, and is not

The prompt required that *"an empty ruled set, **if selected**, passes
`extra_groups=[]` and still rejects every unexpected group"*. The set selected
was **not** empty, so the conditional does not fire for `postgres`. The
behaviour is nonetheless asserted, on the two rows §2.12.2 does state as empty —
`fbprobe` and `discordbot` — because `extra_groups=[]` being passed
**explicitly** rather than omitted is the R5 defect, and it should be held by a
test regardless of which row happens to exercise it.

## R7.7 Three judgement calls, surfaced rather than buried

These are decisions I made inside the ruling's scope. Each is reversible, and I
would rather Codex disagree with them explicitly than not see them.

1. **The shell, password and home columns say *not asserted*.** The ruling
   covered the membership. `postgres`'s shell on a Debian-derived host is very
   likely `/bin/bash`, and writing that in would have been exactly the kind of
   unreviewed host fact this finding is about, in a different column. No code
   reads `CanonicalAccount.shell`, so nothing is weakened by the honest value.
2. **The inverse rows assert exact membership.** §2.12.2's rule is that
   `getent group` reports exactly the listed members and *"an unexpected member
   is a finding, not a difference"*. `ssl-cert = {postgres}` follows that rule.
   It is a claim the ruling did not itself make, and it is **fail-closed**: if
   `oracle-test` has another member of `ssl-cert`, `JNL-52-GROUP-ssl-cert` fails
   and the Operations Owner has a finding, rather than the harness passing
   quietly. If Codex would rather the inverse rows were absent, that is a one-row
   change in each table.
3. **The import-time guard is scoped to the ruled row.** I first wrote it over
   every account, and it failed immediately: §2.12.2's inverse carries no row for
   `foundry`'s `users`, nor for primary groups generally. **That is a pre-existing
   property of §2.12.2 that predates this remediation**, and R7 has no authority
   to change it — so the guard checks the row R7 adds, and the gap is reported
   here rather than silently fixed or silently widened into an import failure.
   It is raised for the Security Reviewer's attention, not corrected.

## R7.8 What changed in the plan, and what did not

The ruling changed a credential policy, not the plan's shape. The dry run is
identical in every structural number:

| | R6 | R7 |
|---|---|---|
| steps planned | 64 | **64** |
| mutations declared | 39 | **39** |
| cleanup steps derived | 42 | **42** |
| unresolved conflicts | 16 (C-2, C-3, C-4, C-5) | **16 (C-2, C-3, C-4, C-5)** |
| `executable` | `False` | **`False`** |
| digest | `18bb5ccd…` | **`15e131bf…`** |

The digest moved and nothing else did, which is the property the finding
required: the policy is inside the reviewed bytes.

## R7.9 Verification — exact results from the final R7 tree

Run serially, in this order, against the tree being submitted, with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported:

| # | Command | Result |
|---|---|---|
| 1 | `venv … pytest -q -rs tests/phase_5_0_evidence` | **558 passed**, 0 failed, 0 skipped |
| 2 | `venv-web … pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **617 passed**, 0 failed, 0 skipped |
| 3 | `venv … pytest -q -rs tests/test_*.py` | **3135 passed**, 0 failed, 0 skipped, 1 warning (`audioop` deprecation, pre-existing) |
| 4 | `venv-web … pytest -q -rs tests/web` | **2840 passed, 80 skipped**, 0 failed — the 80 being the documented correct figure, all from the two matrix files' permitted cells |
| 5 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass**, 0 fail, 0 skipped |
| 6 | `venv … compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | **clean** |
| 7 | `venv … -m tools.phase_5_0_evidence.execution.cli` | **dry run**, 64 / 39 / 42 / 16, digest `15e131bf…`, `executable: False` |
| 8 | `git diff --check` | **clean** |

The evidence-harness suite went from 550 to 558: six regressions added, two
replaced in place.

The evidence-harness suite went from 561 to **564**: four regressions added and
two removed in `test_bands.py` (one renamed and generalized, one deleted with the
hold), plus the suite-wide account-database guard. The bot suite went from 3142
to **3147** with the same seven cases deselected — five DS-R8-2 regressions added.

**Determinism of the generated artifacts.** Both were generated **twice** and
compared byte for byte:

- concrete plan, both generations: `sha256 6d1578c335814d5a11191be650cbd5e16a6c307ff24fb3084bd5e70c38a7d7e7` — identical
- review manifest, both generations: `sha256 71d4b8c2fd9713e1a0b8b415b69675d2939cec8427b2004fbde7d62555bb62e3` — identical

Neither was hand-edited, and neither digest was copied into an execution
command. Every one of the 22 covered-source digests in the committed manifest
was independently re-hashed against the working tree: **22 checked, 0
mismatches.**

## R7.10 What did not happen

- **Nothing was executed.** The CLI ran as a dry run only. `--execute`, the
  confirmation token and every reviewed digest were never passed.
- **No real `SubprocessBoundary` was armed**, and no generated vector ran.
- **No SSH connection was made**, and `oracle-test` was not contacted, read or
  mutated in any way.
- **No host account or group database was inspected.** Not by the harness, not
  by the tests, and not by me to decide the ruling — the maintainer was asked
  instead. Every test injects a synthetic account database written in the test
  file.
- **No privileged or mutation-bearing command ran**, and no database operation
  of any kind was performed by this remediation.
- **No product code, migration, schema, deployment file or infrastructure
  script was touched**, and migration `0014` does not exist.
- **No other contributor's work was reset, reverted, staged, committed, pushed
  or deleted.** The worktree was dirty on arrival and is dirty in the same
  places, plus this remediation's files.

## R7.11 What this submission claims, and what it does not

**Claims:** EH-R6-1's positive half is corrected against a recorded maintainer
ruling; EH-R6-2 remains closed and untouched; the permitted `postgres` credential
is stated in one reviewed place, pinned by the manifest digest, and fails closed
in both directions; and the checks in §R7.9 were run against this exact tree and
produced those exact figures.

**Claims no:** execution approval, readiness consequence, assumption
confirmation, gate closure, or finding closure. **Closing EH-R6-1 is Codex's
call, not mine.** Package 5.0 remains `not ready`. **P5.0-R5 remains Blocking.**
Checks C-1, C-3 and C-4 remain not run. The sixteen unresolved conflicts are
unresolved, `executable` is `False`, and it should be.

## R7.12 Request for Codex independent pre-execution re-review

R7 is returned to Codex for independent pre-execution re-review. A separate
independent review **and** explicit maintainer authority are still required
before anything executes, and no result in this submission supplies either.

Specific attention is requested on the three judgement calls in §R7.7 — the
*not asserted* columns, the exactness of the two inverse group rows, and the
deliberately narrow scope of the import-time guard together with the
pre-existing `users` gap it declines to fix.

---

# R6 — the `postgres` credential policy, and exactly one account record

Date: 2026-09-06

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r6-prompt.md`. **That prompt
authorizes unprivileged code and test remediation only. It does not authorize
`--execute`, an armed `SubprocessBoundary`, SSH, host or NSS inspection, or any
privileged or mutation-bearing command, and none occurred.**

Outcome: **EH-R6-1 and EH-R6-2 are conceded. EH-R6-2 is corrected in full.
EH-R6-1's unreviewed authority is removed and the identity now fails closed, but
the finding's *positive* half — the exact permitted `postgres` supplementary
set — is not corrected here, because no controlled document decides it.
§R6.4 is the decision request the prompt asks for in that case. R6 is therefore
submitted as a partial, blocked remediation. Nothing was executed. No finding is
closed, no assumption is confirmed, no readiness item moves, and Package 5.0
remains `not ready`.**

## R6.0 Both findings, conceded before their corrections

### EH-R6-1 — Blocking: `postgres` credentials were not review-bound. **Conceded.**

R5 gave `postgres` a `MembershipRule.AS_CONFIGURED` row, and `_resolve()` then
took the branch `effective = frozenset(observed)` — the account's **currently
configured** supplementary groups, passed through to `extra_groups=` unchanged.

The finding is right about why that is not a contract. Those memberships are
stated by no reviewed document; they are not in §2.12.2's identity table; and
they appear in no file `review_manifest.COVERED_SOURCES` pins, so they are
outside the aggregate digest a reviewer approves. A `usermod -aG` on the target
between Codex's approval of a digest and the run would therefore change the
credential vector a privileged step executes under **without changing a single
reviewed byte**, and the digest would still match. The whole mechanism the
manifest exists to provide — *the thing that runs is the thing that was
reviewed* — did not cover the identity the command runs as.

R5's own defence of the choice does not survive the finding either. The handback
argued that no present evidence case depends on `postgres`'s groups. That is an
argument about today's cases, not about the authority the child is given, and
EH-R5-1 was itself the finding that a credential the harness constructs rather
than the reviewed design states is inadmissible. "No case reads it" is not the
same claim as "no reviewed source states it, and it is therefore not part of the
approved execution identity". The second claim is the one that matters and it
was true of R5's implementation.

### EH-R6-2 — Important: identical duplicate account records passed. **Conceded.**

`SystemIdentityLookup.account()` built

```python
distinct = {(record.pw_uid, record.pw_gid) for record in pwd.getpwall()
            if record.pw_name == name}
if len(distinct) > 1: ...refuse
```

Two records collapse to one set member whenever their numbers happen to match,
so a duplicated `passwd` entry with identical UID and GID was **accepted** — in
direct contradiction of the contract R5's own handback documented (*"a duplicated
record refuses, because which identity a step would assume is then not
decidable"*). `group_id()` had the same shape over `gr_gid` and the same defect.
The finding's extension to group records is correct and is fixed with it.

The defect is not merely theoretical about numbers agreeing: two records are two
authorities, they can be served by different NSS sources, and which one a later
`getpwnam` resolves is not a property this harness should be deciding by noticing
that today's answers coincide.

## R6.1 Review evidence reproduced before editing

Run against the submitted R5 tree, before any change:

| Command | Result |
|---|---|
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence tests/test_skills.py tests/test_filesystem_layout.py` | **599 passed**, 1 warning, 0 skipped |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py` | **59 passed** |
| `/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli` | dry run: **64 steps, 39 mutations, 42 cleanup steps, 16 unresolved across C-2 … C-5**, digest `b709eb20cd58726897cffc5791bd9712ae05d9214961e9957e3bc0cbcde9a344`, `executable: False` |
| `git diff --check` | clean, exit 0 |

All four reproduce Codex's figures exactly, including the submitted digest. The
one warning is `discord/player.py`'s `audioop` deprecation, from the installed
library. **These green results do not cover either finding**, which is the
prompt's own point: no test asserted what `AS_CONFIGURED` let through, and no
test constructed a duplicated account record. No existing test was weakened.

## R6.2 Files changed, and why

| File | Change | Why |
|---|---|---|
| `tools/phase_5_0_evidence/execution/boundary.py` | `MembershipRule.AS_CONFIGURED` **removed**; `MembershipRule.UNDECIDED` and `MembershipUndecided` added; `RequiredIdentity.__post_init__` cross-checks every row against `identity.CANONICAL_ACCOUNTS`; `UNDECIDED_MEMBERSHIP` derived from the table; `resolve_credential()` refuses an undecided row before any lookup call; `_resolve()` requires set **equality** unconditionally; new `AccountDatabase` protocol, `SystemAccountDatabase`, `_the_one_record()`, and a rewritten `SystemIdentityLookup`; module documentation corrected | **EH-R6-1** and **EH-R6-2** |
| `tools/phase_5_0_evidence/execution/executor.py` | one comment beside `PERMITTED_RUN_AS`, which said `postgres` *"runs the database steps"* | that sentence is now false, and R5's other Blocking finding was in part a false claim in reviewed documentation. `PERMITTED_RUN_AS` still derives from `IDENTITY_CONTRACT` and is otherwise untouched |
| `tests/phase_5_0_evidence/test_boundary_identity.py` | the two tests that encoded the R5 `postgres` rule rewritten; **fourteen added**, in two new sections; `FakeAccountDatabase` added below the lookup | EH-R6-1's and EH-R6-2's required regressions. **44 tests collected**, up from 28 |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated | two covered sources changed, so their digests and the aggregate changed |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated | it carries the review-manifest digest |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section | the prompt's R6 handback |
| `docs/review/Handover information` | new current handover at the top | returning control to Codex |

**Nothing else was touched.** No production application code, bot behaviour,
migration, database schema, deployment file, infrastructure script, roadmap,
project status, RAID entry, decision register or change-log record was modified.
No `PERMITTED_EXECUTABLES` entry, no argument vector, no declared mutation, no
cleanup step and no target fact changed: the regenerated plan still carries **64
steps, 39 mutations, 42 cleanup steps and 16 unresolved steps** across C-2, C-3,
C-4 and C-5, and the executor still refuses it. The five conflicts of §R4.C are
unchanged and remain open for Codex's ruling.

### The regenerated digest

| | Value |
|---|---|
| Review-manifest digest, R5 (**superseded**) | `b709eb20cd58726897cffc5791bd9712ae05d9214961e9957e3bc0cbcde9a344` |
| Review-manifest digest, R6 | `18bb5ccd1cc0845b2bbc397b0acb4943b6c1f2d02ad8b3f64590905f942a9fc6` |
| Target confirmation token (unchanged) | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#ceb58ad1f9f0e070` |

Both artifacts were produced by

```sh
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

which is a dry run — it prints what would run and starts nothing — and which was
run **twice**, producing byte-identical files both times (`cmp`, exit 0, on each).
No generated digest was hand-edited. **A new digest is a value for Codex to
review, not permission to execute**, and the executor refuses this plan
regardless while its conflicts stand.

## R6.3 The `postgres` identity, stated exactly

### There is no pass-through left

`MembershipRule` now has exactly two values, and the suite asserts that:

| Value | Meaning | Can a credential be constructed? |
|---|---|---|
| `EXACT` | §2.12.2 states this account's **complete** supplementary list | yes — and only if the host's set **equals** it |
| `UNDECIDED` | no controlled document states this account's supplementary groups | **no.** The row refuses before the account database is read |

`AS_CONFIGURED` is deleted rather than left unused, because an enum value that
passes a host's configuration through is an authority a later edit can reach for.
There is no pass-through, wildcard, subset-only or caller-inherited membership
path anywhere in the module: `_resolve()` now checks set equality in **both**
directions unconditionally, so even a rule added later without a decision about
its membership gets exact-equality treatment rather than a pass-through.

### One source, and it cannot drift

`RequiredIdentity.__post_init__` validates every row against
`identity.CANONICAL_ACCOUNTS` while the table is being built, so the module does
not import if the two disagree:

- a row for an account §2.12.2 covers must match its primary group, its complete
  supplementary set and its provisioning flag;
- a row for an account §2.12.2 does **not** cover may not state a supplementary
  set at all — that would be a membership stated outside the canonical table,
  which is stop condition **10p** — and may only be `EXACT` if it is the
  superuser row, whose set is empty; and
- an account §2.12.2 *does* cover may not be declared `UNDECIDED`.

So the four things the prompt requires to derive from one source do:
`identity.CANONICAL_ACCOUNTS` is the source; `IDENTITY_CONTRACT` transcribes it
through `_from_canonical()` and is cross-checked per row; `PERMITTED_RUN_AS` is
`frozenset(IDENTITY_CONTRACT)`; and the credentials are built from the contract's
resolved numbers. The membership **evidence** classifier
(`identity.classify_group_membership`) reads the same table, and applies the same
set-equality rule to it.

### What the `postgres` row is now

| `run_as` | Primary group | Supplementary groups | Rule | Effect |
|---|---|---|---|---|
| `root` | `root` | none | exact | runs, launcher must already be euid/egid 0 |
| **`postgres`** | `postgres` | **none stated by any reviewed source** | **undecided** | **refused before a process exists** |
| `freedomcoord` | `freedomcoord` | `freedomjournal` | exact | runs |
| `freedomsheet` | `freedomsheet` | `freedomjournal` | exact | runs |
| `fbprobe` | `fbprobe` | none | exact | runs |
| `discordbot` | `discordbot` | none | exact | runs |
| `freedomweb` | `freedomweb` | `discordbot` | exact | runs |

The `postgres` row is **kept in the table**, and that is deliberate: the set of
names a step may name has to stay closed and reviewable, and deleting the row
would make `postgres` look like an identity the plan never had rather than one
whose policy is missing. What it cannot do is run. `resolve_credential()` raises
`MembershipUndecided` **before** `lookup.account()` is called, so no host read
contributes to the refusal, and `run()` maps it to the existing
`identity-not-in-contract` classification: the contract names the identity but
describes nothing that can be constructed from it. No new classification was
added; `LAUNCH_FAILURES` is the same fourteen strings.

**`ssl-cert` was not assumed.** In source it appears only in the synthetic host
table inside `test_boundary_identity.py`, where it exists precisely to prove that
a host-configured group does **not** reach the child; its other occurrences are
this handback, the R6 prompt's own warning about it, and R5's superseded section
below. No design document states it, no host was read for it, and it is not
policy here.

## R6.4 The decision request — the exact `postgres` supplementary set

**This is the blocked half of EH-R6-1, returned rather than inferred**, as the
prompt directs when the controlled documents do not decide the set.

### What was searched, and what was found

| Source | What it says about the `postgres` operating-system account's groups |
|---|---|
| Package plan **§2.12.2**, the canonical membership table | **Nothing.** It covers six identities — `freedomcoord`, `freedomsheet`, `discordbot`, `freedomweb`, `foundry`, `fbprobe` — and `postgres` is not one of them, in either the identity table or the group inverse |
| Package plan elsewhere | `postgres:postgres` appears only as the **ownership** of `/var/run/postgresql` in observation **H-3** and as `--owner postgres --group postgres` in `install` vectors. Both are file ownership, not account membership |
| `docs/review/phase-5-0-evidence-harness-execution-plan.md` | names `postgres` as the `run_as` of the `psql` and `install` steps; states no membership for it |
| `docs/operations/disposable-test-server.md` | PostgreSQL 16 profile, socket, roles and client path; **no OS account memberships** |
| The evidence-harness authorization draft, implementation prompt, and the R3/R5 remediation prompts | no occurrence of a `postgres` group or membership |
| `docs/implementation-plan.md` | no `postgres` OS-account membership |

The controlled design therefore **does not decide it**, and §2.12.2's own rule —
*every identity, primary group and supplementary group in Package 5.0 appears
here and nowhere else*, with stop condition **10p** making a membership stated
elsewhere a defect — means the gap cannot be filled by writing one into
`identity.py`, `boundary.py` or a new record beside them. Doing so would be a
membership stated outside the canonical table.

### The options, and what each costs

| # | Option | Security effect | Operational effect |
|---|---|---|---|
| **A** | Add a `postgres` row to **§2.12.2** with its exact primary group and exact permitted supplementary set, then transcribe it here through `_from_canonical()` and make the rule `EXACT` | The strongest: the permitted set becomes reviewed text, is pinned by the manifest digest through `identity.py`, and a host that differs refuses. Extends §2.12.2 to an account the package does not provision, which is a scope decision, not a code one | Database steps run once the host matches. **Requires the maintainer to state the set** — on a Debian-derived host that is very likely `ssl-cert`, but this remediation does not assert that |
| **B** | Declare the set **exact and empty** in §2.12.2 | Also fully review-bound and fail-closed, and it asserts a completeness claim §2.12.2 has never made about this account | On a stock Debian/Ubuntu host `postgres` is normally in `ssl-cert`, so the first `psql` step would refuse — a refusal caused by harness policy rather than by the authority under test, which is the class of outcome EH-R5-1 exists to prevent |
| **C** | Keep the row `UNDECIDED` — **the state this submission is in** | Fully fail-closed and invents nothing; the pass-through is gone | The plan's three `postgres` steps in the `postgresql` band and its four `postgres` cleanup reversals cannot execute, so the PostgreSQL half of the evidence — and the `psql` restore/reload cleanup that follows it — cannot be produced even after the other conflicts are resolved. This is a hold, not a resolution |
| **D** | Give the database steps `run_as="root"` instead | Removes the question by removing the identity — but changes the authority under test. Peer authentication matches the **account name**, so the steps would no longer exercise the identity the design says performs them | Would change reviewed argument vectors and the plan's identity assignments — outside this prompt's scope, and a design change rather than a remediation |

### What a ruling would change

Whichever option is chosen, the affected artifacts are: package plan **§2.12.2**
(A and B only); `tools/phase_5_0_evidence/identity.py`'s `CANONICAL_ACCOUNTS`
(A and B); the `postgres` row of `IDENTITY_CONTRACT` in
`tools/phase_5_0_evidence/execution/boundary.py`; the regressions in
`tests/phase_5_0_evidence/test_boundary_identity.py`; and — because both source
files are covered — the **review-manifest digest**, which is exactly the property
the finding required and which
`test_changing_the_reviewed_postgres_policy_changes_the_manifest_digest`
demonstrates.

**Asked of the maintainer and Codex:** which of A, B, C or D, and — under A — the
exact permitted supplementary set. Nothing here selects one, and no allowlist was
inferred from any host.

## R6.5 Exactly one NSS record, and it must agree

`SystemIdentityLookup` now reads through an injected `AccountDatabase`.
`SystemAccountDatabase` is the only implementation that touches `pwd`, `grp` and
`os`, and it is deliberately thin: it converts records to tuples and lets
`KeyError` and `OSError` out unchanged. Every decision about what a record
*means* is the lookup's, so there is one place to read those rules and one place
to test them — and the class the finding is about is the class the suite
exercises, rather than a fake standing in for it.

For both `account(name)` and `group_id(name)`:

1. the direct `getpwnam` / `getgrnam` answer must exist, or the identity is
   **absent** → `IdentityAbsent` → `identity-unknown`;
2. the enumerated records matching that name are **counted, not deduplicated**,
   by `_the_one_record()`. Zero is **absent**; two or more — *identical or
   contradictory* — is `IdentityInconsistent` → `identity-inconsistent`; and
3. the direct answer and that single enumerated record must agree **completely**:
   name, and both numeric identifiers. A database that answers one thing directly
   and enumerates another is contradicting itself, and this run does not choose
   between the two.

`supplementary_group_names()` still maps gids to names, and each name it returns
is resolved again through `group_id()` before it becomes a credential — so a
reverse mapping that does not round-trip to exactly one named record is refused
there, by the rules above.

**Fixed safe output is preserved.** No NSS record, UID, GID, group name or
exception text reaches a `CommandResult`: `run()` maps each `IdentityRefusal`
subclass to one of the fourteen `LAUNCH_FAILURES` strings, and
`test_the_real_lookups_refusals_reach_the_boundary_as_fixed_classifications`
asserts that neither the numbers nor the account name appear in the result's
`repr`. `test_no_classification_carries_lookup_or_operating_system_text` is
unchanged and still plants a sentinel in every message the lookup can raise.

## R6.6 Every requirement, mapped to code and tests

### EH-R6-1

| Requirement | Code | Test |
|---|---|---|
| the reviewed source contains exactly one `postgres` row | `boundary.IDENTITY_CONTRACT`, `UNDECIDED_MEMBERSHIP` | `test_postgres_is_the_one_row_no_reviewed_source_decides` |
| the execution identity contract derives from the canonical source | `RequiredIdentity.__post_init__`, `_from_canonical` | `test_every_membership_comes_from_the_canonical_table_and_not_from_here`, `test_the_contract_cannot_drift_from_the_canonical_table` |
| the permitted exact set reaches `extra_groups=` as numeric GIDs | `_resolve`, `ResolvedCredential.as_keywords` | `test_every_exact_row_reaches_extra_groups_as_numeric_gids`, `test_a_non_root_account_passes_its_numeric_ids_and_supplementary_groups`, `test_the_real_lookup_builds_the_exact_credential_from_one_record_each` |
| a missing required group refuses before the process starter is called | `_resolve` | `test_a_required_membership_missing_at_execution_time_refuses` |
| an unexpected group refuses before the process starter is called | `_resolve` | `test_an_unexpected_membership_refuses_where_the_list_is_exact`, `test_a_host_configured_group_never_reaches_the_child` |
| the parent process's groups cannot affect the result | `_resolve`, `as_keywords` | `test_changing_the_parent_processs_groups_cannot_change_the_child_keywords`, `test_a_non_member_receives_no_inherited_supplementary_group` |
| no `AS_CONFIGURED`, pass-through, wildcard, subset-only or inherited path | `MembershipRule`, `_resolve` | `test_undecided_is_the_only_alternative_to_an_exact_set` |
| the manifest changes when the permitted `postgres` identity changes | `review_manifest.COVERED_SOURCES` | `test_changing_the_reviewed_postgres_policy_changes_the_manifest_digest` |
| source/contract/evidence drift fails closed | `RequiredIdentity.__post_init__` | `test_the_contract_cannot_drift_from_the_canonical_table` |
| refusals stay inside the fixed vocabulary | `run()`, `LAUNCH_FAILURES` | `test_every_classification_the_boundary_can_return_is_in_the_fixed_set`, `test_a_host_configured_group_never_reaches_the_child` |
| no host or `oracle-test` read turned current state into policy | — | §R6.4: the policy is **not stated**, and the gap is returned |

### EH-R6-2

| Requirement | Code | Test |
|---|---|---|
| exactly one account and group record succeeds | `SystemIdentityLookup.account`, `.group_id` | `test_exactly_one_account_and_group_record_resolves` |
| two identical account records refuse | `_the_one_record` | `test_two_account_records_refuse_however_they_are_numbered[identical]` |
| two contradictory account records refuse | `_the_one_record` | `…[contradictory]` |
| two identical group records refuse | `_the_one_record` | `test_two_group_records_refuse_however_they_are_numbered[identical]` |
| two contradictory group records refuse | `_the_one_record` | `…[contradictory]` |
| the direct record must agree with the sole enumerated one | `account`, `group_id` | `test_a_direct_answer_that_contradicts_the_one_record_refuses` |
| zero records refuse safely, as *unknown* | `account`, `group_id`, `_the_one_record` | `test_zero_matching_records_are_absent_rather_than_inconsistent` |
| fixed safe output — no record, id, group or exception text | `run()` | `test_the_real_lookups_refusals_reach_the_boundary_as_fixed_classifications`, `test_no_classification_carries_lookup_or_operating_system_text` |
| lookup stays injectable; no test reads a real database | `AccountDatabase`, `SystemAccountDatabase` | `test_the_lookups_default_database_is_the_system_one`, `test_this_file_reads_no_account_and_starts_no_process` |

## R6.7 EH-R5-2 is preserved unchanged in substance

The guaranteed-cleanup structure was not rewritten. `executor.py`'s only change
is one comment beside `PERMITTED_RUN_AS`; `_RunState`, `execute()`,
`_conclude()`, the interruption path, the unexpected-exception path, the
cleanup-step revalidation, the S-B construction and the second-invocation refusal
are byte-identical to R5. `PERMITTED_RUN_AS` still derives from
`IDENTITY_CONTRACT`, which is what keeps it bound to the corrected source.

All of R5's cleanup regressions remain green: `test_executor_cleanup.py` passes
in full, including the exception, interruption, cleanup-failure,
non-admissibility and second-invocation-refusal paths.

## R6.8 Verification, run against the submitted tree

Serially, with the documented interpreters, and
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported for the two
full suites:

| Command | Result |
|---|---|
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | **550 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **609 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3135 passed**, 0 failed, 0 skipped, 1 warning |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2840 passed**, 0 failed, **80 skipped**, 1137 warnings |
| `node --test "foundry-module/tests/"*.test.mjs` | **171 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean, exit 0 |
| `/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli` | dry run: 64 steps, 39 mutations, 42 cleanup steps, 16 unresolved, digest `18bb5ccd…`, `executable: False` |
| `git diff --check` | clean, exit 0 |

The web suite retains **exactly 80** expected permission-matrix skips — 54 from
`test_p3_2_matrix.py` and 26 from `test_p3_3_matrix.py`, both *"permitted cells
are asserted by the per-route success cases"*. The 1137 warnings and the single
bot-suite warning are unchanged from R5 and come from installed libraries.

Every figure above was produced from **this** tree; none is carried over. The
harness suite is 550 rather than R5's 534 because fourteen tests were added — two
of them parametrised into two cases each — and two were rewritten in place. Formatter, linter and
type checker remain **not configured**; no tooling was added and no such check is
claimed.

## R6.9 What did not happen

- **No process boundary ran.** `SubprocessBoundary` was never armed outside the
  `armed=True` construction inside tests, whose process starter is replaced by a
  recorder before any test touches it. `--execute` was never passed.
- **No host account or group database was read.** `SystemIdentityLookup` is
  exercised only through `FakeAccountDatabase`, written in the test file. The
  suite still asserts that the test module imports none of `pwd`, `grp` or `os`.
- **No SSH, no `oracle-test`, no privileged command, no mutation.** Nothing was
  run on the disposable target and no connection to it was made. Production and
  staging were not accessed. No account, group, file, PostgreSQL object,
  configuration line or transient unit was created anywhere.
- **No host was inspected to decide policy.** §R6.4's search covers documents
  only; the local host's `postgres` memberships were not read, and are not the
  basis of anything here.
- The worktree is preserved exactly as found. Nothing was reset, reverted,
  staged, committed or pushed, and no other contributor's file was deleted.

## R6.10 What this submission claims, and what it does not

**Requested:** Codex's independent pre-execution re-review of R6.

**Claimed:** EH-R6-2 is corrected in full. EH-R6-1's unreviewed authority is
removed and the identity fails closed; its permitted set is returned as the
decision request in §R6.4 rather than inferred.

**Not claimed.** No finding is closed — EH-R6-1 and EH-R6-2 are Codex's to
decide, and EH-R6-1 additionally needs a maintainer ruling. No assumption is
confirmed; no operational check is run; no readiness item moves. The five
conflicts of §R4.C remain open, including C-1's ruling request. P5.0-R5 remains
**Blocking**; P5.0-R1 and P5.0-R4 are untouched; A-5.0-3, A-5.0-4 and A-5.0-5
remain unconfirmed; checks C-1, C-3 and C-4 remain **not run**; OD-62 remains
Open with G-A provisional; **Package 5.0 remains `not ready`**; and migration
`0014`, product implementation, production or staging mutation, deployment,
cutover and Package 5.1+ remain unauthorized.

---

# R5 — the real process boundary's credential contract, and guaranteed cleanup

Date: 2026-09-06

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r5-prompt.md`. **That prompt
authorizes unprivileged code and test remediation only. It does not authorize
`--execute`, an armed `SubprocessBoundary` outside tests, or any privileged or
mutation-bearing command, and none occurred.**

Outcome: **EH-R5-1 and EH-R5-2 are conceded and corrected, with the injected-
lookup and injected-boundary regressions the finding text requires. Nothing was
executed. No finding is closed, no assumption is confirmed, no readiness item
moves, and Package 5.0 remains `not ready`.**

## R5.0 Both findings, conceded before their corrections

### EH-R5-1 — Blocking: the real process boundary constructed the wrong identity. **Conceded.**

`SubprocessBoundary.run()` passed `user=run_as` and `extra_groups=[]` for each
non-root step and omitted `group=`. The comment beside it claimed that `user=`
selects the account's primary group when `group=` is not given. **That is false.**
`subprocess` treats the three as separate credential controls: between `fork`
and `exec` it calls `setgroups(extra_groups)`, then `setgid(group)`, then
`setuid(user)`, and a control it is not given is simply not applied. The child
therefore kept the **launching process's primary group**, and `extra_groups=[]`
deliberately **cleared every supplementary group** — including `freedomjournal`,
which is exactly the membership `JNL-52`'s positive traversal and the isolation
cases depend on.

The consequence is the one the finding states and is worse than a wrong result:
a positive control could fail, or a refusal could occur, **because of how the
harness built the identity** rather than because of the authority under test.
Such a result is not admissible evidence, and a fake `ProcessBoundary` cannot
detect it — every R4 test injected one, so nothing in the R4 suite ever looked
at a credential keyword.

The root path was the same defect in the other direction: `run_as="root"`
passed **no** credential keyword at all, so a root step meant *"whatever
identity launched the CLI"*.

### EH-R5-2 — Blocking: unexpected exceptions bypassed cleanup. **Conceded.**

`ExecutingRunner.execute()` called the boundary inside its step loop and reached
`_clean_up()` only after the loop exited normally. There was no `try`/`finally`
or equivalent guard around mutation-bearing execution. An unexpected `OSError`,
a capture or sanitizer failure, an ordinary programming error, a
`KeyboardInterrupt` or any other exception raised after a mutation had been
reached unwound straight past cleanup and left accounts, groups, files,
PostgreSQL objects, effective authentication configuration or a transient unit
behind.

The class docstring said the opposite — *"Cleanup runs whenever a mutation was
reached, whether the run finished, was stopped, timed out or raised"* — so the
defect was also a false claim in the reviewed documentation. Because the harness
modifies authentication configuration and host identities, this is a
production-reliability and recovery defect even on a disposable target. The
finding is correct as written.

## R5.1 Review evidence reproduced before editing

Run against the submitted R4 tree, before any change:

| Command | Result |
|---|---|
| `/opt/discord-bots/venv/bin/python -m pytest -q tests/phase_5_0_evidence tests/test_skills.py tests/test_filesystem_layout.py` | **546 passed**, 1 warning |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py` | **59 passed** |
| `git diff --check` | clean, exit 0 |

Both totals and the clean whitespace check reproduce Codex's exactly. The one
warning is `discord/player.py`'s `audioop` deprecation, from the installed
library. **These green results did not cover either defect**, which is the
finding's own point: no test asserted a credential keyword, and no test raised
inside a mutation-bearing run. Neither suite was weakened to accommodate the
corrections, and no fake-boundary result is offered anywhere below as evidence
of operating-system credential behaviour.

## R5.2 Files changed, and why

| File | Change | Why |
|---|---|---|
| `tools/phase_5_0_evidence/execution/boundary.py` | the identity contract, the injected `IdentityLookup`, `resolve_credential()`, explicit `user=`/`group=`/`extra_groups=` on every call, the fixed `LAUNCH_FAILURES` vocabulary, and the corrected module and class documentation | **EH-R5-1**. The false primary-group claim is removed and replaced by the contract that makes it unnecessary |
| `tools/phase_5_0_evidence/execution/executor.py` | `_RunState`; `execute()` restructured around the step loop with an interruption path and an unexpected-exception path; `_conclude()` as the single cleanup caller; per-step and per-cleanup-step exception translation; cleanup-step revalidation; the S-B outcome for a cleanup that could not be carried out; `PERMITTED_RUN_AS` derived from the boundary's contract | **EH-R5-2**, and the corrected cleanup claim in the module docstring |
| `tests/phase_5_0_evidence/test_boundary_identity.py` | **new**: 28 tests over the credential contract, asserting the actual keyword arguments passed to the process starter | EH-R5-1's required regressions |
| `tests/phase_5_0_evidence/test_executor_cleanup.py` | **new**: 24 tests over exception, interruption and cleanup-failure semantics, with boundaries that raise at controlled steps | EH-R5-2's required regressions |
| `tests/phase_5_0_evidence/test_no_execution.py` | one declared exemption: `test_boundary_identity.py` may **name** the process starter, and two new assertions make that narrower than the blanket rule it replaces | asserting real credential keywords requires replacing what the boundary calls; the exemption is declared rather than assumed |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated | two covered sources changed, so their digests and the aggregate changed |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated | it carries the review-manifest digest |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section | the prompt's R5 handback |
| `docs/review/Handover information` | new current handover at the top | returning control to Codex |

**Nothing else was touched.** No production application code, bot behaviour,
migration, database schema, deployment file, infrastructure script, roadmap,
project status, RAID entry, decision register or change-log record was modified.
No `PERMITTED_EXECUTABLES` entry, no argument vector, no declared mutation, no
cleanup step and no target fact changed — the regenerated plan still carries 64
steps, 39 mutations, 42 cleanup steps and 16 unresolved steps across C-2, C-3,
C-4 and C-5, and the executor still refuses it. The five conflicts of §R4.C are
unchanged and remain open for Codex's ruling. No allowlist was modified: the two
new test modules are under `tests/`, which the scope guard does not police.

### The regenerated digest

| | Value |
|---|---|
| Review-manifest digest, R4 (**superseded**) | `205e501ed04adf5b1fcefc1d4a24fc36b3e6a791f07cb4dbf924d1af6722a57b` |
| Review-manifest digest, R5 | `b709eb20cd58726897cffc5791bd9712ae05d9214961e9957e3bc0cbcde9a344` |
| Target confirmation token (unchanged) | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#ceb58ad1f9f0e070` |

It changed because `boundary.py` and `executor.py` are covered sources, which is
the mechanism working as designed: an edit after a review invalidates the
approval. **A new digest is a value for Codex to review, not permission to
execute.** No generated digest was hand-edited; both artifacts were produced by

```sh
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

which is a dry run — it prints what would run and starts nothing — and which was
run twice, producing byte-identical files both times.

## R5.3 The credential contract, stated exactly

### The table

`IDENTITY_CONTRACT` in `boundary.py` is closed and is the only thing a `run_as`
may name. `executor.PERMITTED_RUN_AS` is now **derived from it**, so the two
closed sets cannot drift.

| `run_as` | UID/GID source | Primary group | Supplementary groups | Rule | Provisioned by the harness |
|---|---|---|---|---|---|
| `root` | the account database's `root` | `root` | none | exact | no — and the launcher must already be effective UID/GID 0 |
| `postgres` | the account database's `postgres` | `postgres` | **as configured on the host** | as-configured | no |
| `freedomcoord` | §2.12.2 | `freedomcoord` | `freedomjournal` | exact | yes |
| `freedomsheet` | §2.12.2 | `freedomsheet` | `freedomjournal` | exact | yes |
| `fbprobe` | §2.12.2 | `fbprobe` | none | exact | yes |
| `discordbot` | §2.12.2 | `discordbot` | none | exact | no |
| `freedomweb` | §2.12.2 | `freedomweb` | `discordbot` | exact | no |

The five §2.12.2 rows are **transcribed from `identity.CANONICAL_ACCOUNTS`**, not
restated: `_from_canonical()` reads that table, so §2.12.2 remains the single
place a membership is stated — remediation R11-B and security finding P5.0-SR2 —
and a correction there is a correction to the credentials a child receives.
`test_every_membership_comes_from_the_canonical_table_and_not_from_here` asserts
that for all five.

### Resolution, in order, all of it before a process exists

1. `run_as` must be a row of the table. A name that is not one is refused;
   there is no default and blank is not a member.
2. For the `root` row only: the harness process must **already** be effective
   UID 0 and GID 0. A non-root launcher is refused here, so `run_as="root"` can
   never mean *"whatever identity launched the CLI"*.
3. `lookup.account(name)` gives the numeric UID and primary GID. An absent
   account refuses; a duplicated record refuses, because which identity a step
   would assume is then not decidable; a record whose name does not round-trip
   refuses.
4. `lookup.group_id(primary_group)` must return **the same GID** the account
   record carries. A host where those disagree is a host this run does not use.
5. The `root` row must resolve to 0/0. **Every other row must not**: a
   non-superuser row resolving to UID 0 or GID 0 is a malformed identity, not a
   step that may run.
6. `lookup.supplementary_group_names(name, gid)` gives the configured
   supplementary groups, excluding the primary. Under **exact**, this set must
   equal the contract's set — a missing required membership refuses, and an
   unexpected extra one refuses, which is the same rule
   `identity.classify_group_membership` applies to the evidence itself. Under
   **as-configured**, the required set (empty) must be present and the observed
   set is passed through unchanged.
7. Each resulting group name is resolved to a GID; an unresolvable name refuses,
   a GID of 0 under a non-superuser row refuses, and two names resolving to the
   same GID refuses.
8. `user=`, `group=` and `extra_groups=` are then **all three** passed to
   `subprocess.run` beside the reviewed vector. `extra_groups` carries the
   supplementary GIDs only; the primary group is `group=`, which `setgid`
   establishes.

Nothing is inherited: not the caller's UID, not its primary group, not its
supplementary groups. The credentials are a function of the contract and of the
account database, which is what
`test_changing_the_parent_processs_groups_cannot_change_the_child_keywords`
asserts by running the same identity under two callers that differ in every way
that could be inherited.

### `postgres` — the one row §2.12.2 does not describe. **A point for Codex.**

§2.12.2 states memberships for six accounts and `postgres` is not one of them.
Two options were available and neither is free:

- declare its supplementary list **exact and empty**. On a Debian-derived host
  `postgres` is normally a member of `ssl-cert`, so this would refuse the first
  `psql` step — a refusal for a harness defect, which is precisely the class of
  outcome EH-R5-1 exists to prevent — and it would assert a completeness claim
  the reviewed table never made; or
- declare it **as-configured**: assert the primary group, require nothing more,
  and pass the account's configured supplementary groups through unchanged.

The second is implemented, because it invents no membership and erases none, and
because no evidence case depends on `postgres`'s groups: it runs the database
steps, where peer authentication matches the **account name**, and the identity
bands are `freedomcoord`, `freedomsheet`, `fbprobe`, `discordbot` and
`freedomweb`, all of which are exact. **This is a judgement, and it is offered
for Codex's ruling rather than presented as settled**; the alternative is a
§2.12.2 row for `postgres`, after which the rule becomes `EXACT` with a one-line
change.

### What no refusal says

Every refusal is one of the fourteen strings in `LAUNCH_FAILURES`. The lookup
exceptions carry readable messages for a traceback and **none of them reaches a
`CommandResult`**: `run()` maps each class to a fixed classification.
`test_no_classification_carries_lookup_or_operating_system_text` plants a
sentinel containing a UID, a GID, a group name and an errno in every message the
lookup and the process starter can raise and asserts that none of it appears in
any field of any result;
`test_every_classification_the_boundary_can_return_is_in_the_fixed_set` reads
`boundary.py` as text so a classification added on a branch no test takes still
has to be declared.

### What was not used

No `sudo`, `su`, shell, `setpriv`, `capsh`, helper executable, mutable
environment variable or wrapper appears in any argument vector. The reviewed
vector is the vector passed to the process starter; the credentials are keyword
arguments beside it, and
`test_a_non_root_account_passes_its_numeric_ids_and_supplementary_groups`
asserts both halves of that in the same call.

## R5.4 Exception, interruption and cleanup-failure semantics

### When cleanup becomes this run's responsibility

**Before the command, not after it.** A step's declared mutation ids are recorded
**before** the boundary is invoked, so a mutation whose launch outcome is never
learned — the call raised, the argument evaluation raised, the operator
interrupted, the process may or may not have started — is treated as
*potentially reached* and the full derived cleanup runs. Nothing decides cleanup
from what a command reported, because a command that reported nothing is exactly
the case that matters.

The rule's boundary is therefore the recording, and it is where the two required
regressions sit on either side: an exception during the step's **revalidation**
is before it and runs no destructive cleanup; an exception at or after the
recording is after it and runs the whole cleanup.

### The paths out of `execute()`

| Path | What is recorded | Cleanup | Result |
|---|---|---|---|
| every step satisfied | — | runs once | S-C, artifact admissible |
| a step unsatisfied, timed out, or safely refused at launch | `stopped_at`, `stop_reason` | runs once if a mutation was reached | S-A or S-B, not admissible |
| a step's revalidation refuses | `stopped_at`, `launch_failure = validation-refused` | runs once if a mutation was reached | not admissible |
| the boundary or its sanitizer raises | `launch_failure = boundary-failure`; the exception is dropped where it is raised | runs once | not admissible |
| any other exception | `stop_reason = UNEXPECTED_EXECUTION_FAILURE`, a constant | runs once | not admissible |
| `KeyboardInterrupt` / `SystemExit` | `stop_reason = OPERATOR_INTERRUPTION`, a constant | runs once, **before** the interruption propagates | re-raised; `last_outcome` carries what happened |
| an interruption **during** cleanup | the runner is marked uncertain and blocked | not resumed | re-raised; the next invocation refuses |
| the cleanup machinery itself fails | the steps that ran are preserved | not repeated | **S-B**, naming only declared residue |

Cleanup runs **exactly once** on every one of them: `_conclude()` is its single
caller and refuses a second invocation. `execute()` has no path — return,
exception or interruption — that does not pass through it.

### The two facts are kept apart

The execution failure is `RunOutcome.stopped_at` / `stop_reason`; the cleanup
result is `RunOutcome.cleanup`. A cleanup that succeeded never makes a failed run
look successful — `test_an_execution_exception_with_successful_cleanup_is_still_a_failed_run`
— and a cleanup that failed never erases what stopped the run —
`test_execution_failure_plus_cleanup_failure_preserves_both_and_is_s_b`.
`_RunState.stop()` keeps the **first** stop, so a later failure while unwinding
cannot overwrite what actually stopped the run.

### Nothing is suppressed

`KeyboardInterrupt` and `SystemExit` are re-raised, after cleanup has finished.
Neither `execute()` nor the cleanup loop catches `BaseException` to stay alive:
the interruption path re-raises explicitly, and the one place that must act while
an interruption is in flight — recording that cleanup did not complete — is a
`finally` on a flag rather than a handler.

### A cleanup that cannot be carried out

If the cleanup machinery fails rather than one of its steps, the outcome is
constructed as **S-B**, exit 3, with:

- residue taken from the **declared** cleanup plan — every object a reversal step
  removes that no step was observed to remove — so the names come from the
  reviewed plan and never from the host or the exception; and
- one effective-configuration risk sentence stating that nothing this run created
  is proved removed and any temporary authentication configuration is not proved
  restored or reloaded.

It is never S-C, `artifact_admissible` is never true, and **the next invocation
refuses rather than cleaning it** — §2.13.2b. An uncertain cleanup refuses with
its own message, because *"what it left behind is unknown"* is a stronger reason
to refuse than a known residue, not a weaker one.

### A failed cleanup step does not stop the rest

The derived plan has no step whose safety depends on an earlier one having
succeeded — the ordering is a dependency order for *effectiveness*, and every
step is non-destructive when its object is absent — so stopping would leave more
behind than continuing. A cleanup step that raises, or that fails its
revalidation, is recorded as unsatisfied, its object becomes residue, and the
remaining steps still run. It cannot claim S-C.

### Cleanup is now revalidated too

Every cleanup step passes the same guards as a reviewed step immediately before
it runs: the whole vector through `plan.validate_argv` against the plan's target,
the executable against the permitted set, the identity against the closed set,
the timeout against zero. Cleanup runs the destructive half of the plan; the
object that reaches that loop is no more obliged to be the object that was
reviewed than the object that reaches the step loop. It remains derived, bounded
and non-recursive, and no cleanup command is written by anyone.

## R5.5 Requirement-to-code-to-test traceability

### EH-R5-1

| Requirement | Code | Test |
|---|---|---|
| resolve the account before process creation to numeric UID, primary GID and the exact supplementary list | `boundary.resolve_credential`, `boundary.SystemIdentityLookup` | `test_boundary_identity.py::test_a_non_root_account_passes_its_numeric_ids_and_supplementary_groups` |
| pass `user=`, `group=` and `extra_groups=` explicitly | `ResolvedCredential.as_keywords`, `SubprocessBoundary.run` | `…::test_a_non_root_account_passes_its_numeric_ids_and_supplementary_groups`, `…::test_root_is_constructed_explicitly_rather_than_inherited` |
| a `freedomjournal` member retains that supplementary group | `MembershipRule.EXACT` branch of `_resolve` | `…::test_a_freedomjournal_member_keeps_the_membership_the_cases_depend_on` |
| a non-member receives no inherited supplementary group | same | `…::test_a_non_member_receives_no_inherited_supplementary_group`, `…::test_the_one_supplementary_group_an_existing_host_identity_has_is_kept` |
| the caller's groups cannot change the child's | credentials are resolved from the contract only | `…::test_changing_the_parent_processs_groups_cannot_change_the_child_keywords` |
| do not erase a target account's required configured groups | `MembershipRule.AS_CONFIGURED` branch | `…::test_the_configured_groups_of_the_as_configured_row_are_preserved` |
| distinguish harness-provisioned from existing host identities | `RequiredIdentity.provisioned_by_harness`, `_from_canonical` | `…::test_the_two_kinds_of_identity_are_distinguished`, `…::test_every_membership_comes_from_the_canonical_table_and_not_from_here` (5 cases), `…::test_postgres_is_the_one_row_the_canonical_table_does_not_describe` |
| an omitted or unknown account or group refuses before process creation | `IdentityAbsent` path | `…::test_an_absent_account_or_group_refuses_before_process_creation`, `…::test_an_identity_that_is_not_a_contract_row_is_refused` |
| a duplicated record refuses | `SystemIdentityLookup.account`/`group_id` | `…::test_a_duplicated_account_or_group_refuses` |
| an inconsistent or malformed identity refuses | `_resolve`'s round-trip and superuser checks | `…::test_an_account_whose_primary_group_does_not_round_trip_refuses`, `…::test_a_non_root_row_that_resolves_to_a_superuser_id_refuses` |
| a required membership missing at execution time refuses | `MembershipRefused` path | `…::test_a_required_membership_missing_at_execution_time_refuses` |
| an unexpected membership refuses where the list is exact | same | `…::test_an_unexpected_membership_refuses_where_the_list_is_exact` |
| a non-root launcher cannot run a root step as itself | `SubprocessBoundary._credential_for` | `…::test_a_non_root_launcher_cannot_run_a_root_step_as_itself` (3 cases) |
| root is explicit and validated | same, plus the `root` row | `…::test_root_is_constructed_explicitly_rather_than_inherited` |
| lookup and construction stay inside the boundary or an injected resolver | `IdentityLookup` protocol, injected on `SubprocessBoundary` | `test_no_execution.py::test_no_module_opens_reads_or_writes_a_file` (the planning tier still reads nothing), `test_boundary_identity.py::test_this_file_reads_no_account_and_starts_no_process` |
| fixed safe classifications, with no lookup or OS text | `LAUNCH_FAILURES`, `_refusal` | `…::test_no_classification_carries_lookup_or_operating_system_text`, `…::test_every_classification_the_boundary_can_return_is_in_the_fixed_set`, `…::test_the_operating_systems_own_refusals_are_classifications_too` |
| the closed identity set does not drift from the contract | `executor.PERMITTED_RUN_AS = frozenset(IDENTITY_CONTRACT)` | `…::test_the_contract_covers_exactly_the_identities_a_step_may_name`, `test_executor.py::test_every_step_runs_as_one_of_the_closed_identity_set` |
| no test starts a real process or reads the host account database | the injected lookup and the replaced process starter | `test_no_execution.py::test_the_one_test_that_names_the_process_starter_cannot_reach_it`, `test_boundary_identity.py::test_this_file_reads_no_account_and_starts_no_process` |

### EH-R5-2

| Requirement | Code | Test |
|---|---|---|
| exceptions before the first mutation run no destructive cleanup | the recording point in `_run_steps` | `test_executor_cleanup.py::test_an_exception_before_the_first_mutation_runs_no_destructive_cleanup`, `…::test_an_exception_before_the_first_step_stops_without_cleanup` |
| an exception immediately before the first mutation-bearing call follows the documented responsibility rule | same | `…::test_an_exception_immediately_before_the_first_mutation_call_still_cleans_up` |
| exceptions from the first and each representative later mutation class run cleanup exactly once | `execute` / `_conclude` | `…::test_an_exception_at_each_mutation_class_runs_the_whole_cleanup_once` (8 cases, one per mutation kind that a generated step performs) |
| exceptions from sanitization/capture handling follow the same path | the per-step handler in `_run_steps` | `…::test_a_capture_or_sanitizer_failure_follows_the_same_cleanup_path` |
| `KeyboardInterrupt` and `SystemExit` run cleanup before propagation | `execute`'s interruption path | `…::test_an_interruption_runs_cleanup_before_it_propagates` (2 cases) |
| an ordinary exception plus successful cleanup remains a failed, non-admissible run | `RunOutcome.artifact_admissible`, `_RunState.stop` | `…::test_an_execution_exception_with_successful_cleanup_is_still_a_failed_run` |
| execution failure plus cleanup failure preserves both facts and yields S-B | `_conclude` | `…::test_execution_failure_plus_cleanup_failure_preserves_both_and_is_s_b` |
| a cleanup-boundary exception cannot skip the remaining steps and cannot claim S-C | `_run_cleanup_plan`'s per-step handler | `…::test_a_cleanup_boundary_exception_does_not_skip_the_remaining_steps` |
| cleanup remains subject to per-step and identity validation and timeouts | `_revalidate_cleanup`, `_revalidate_vector` | `…::test_a_cleanup_step_is_revalidated_immediately_before_it_runs` |
| a cleanup that cannot complete is a typed S-B naming only declared residue | `_cleanup_did_not_complete`, `_declared_residue` | `…::test_a_failure_of_the_cleanup_machinery_is_s_b_and_names_declared_residue` |
| a mutation whose launch outcome is uncertain is treated as reached | the recording point | `…::test_an_exception_immediately_before_the_first_mutation_call_still_cleans_up` |
| no second invocation after uncertain or failed cleanup | `_refuse_when_blocked`, `_cleanup_uncertain` | `…::test_an_interruption_during_cleanup_propagates_and_blocks_the_next_run`, `…::test_a_rerun_after_an_unresolved_effective_configuration_is_refused`, `…::test_a_failure_of_the_cleanup_machinery_is_s_b_and_names_declared_residue`, `test_executor.py::test_failed_cleanup_blocks_a_rerun_rather_than_retrying_it` |
| no exception text is serialized | `UNEXPECTED_EXECUTION_FAILURE`, `OPERATOR_INTERRUPTION`, `LAUNCH_BOUNDARY_FAILURE` | `…::test_no_exception_text_reaches_the_recorded_outcome` |
| no exception path writes an evidence artifact | `artifact_admissible` is False on every one | every test above asserts it; `test_executor.py::test_the_executor_neither_reads_nor_writes_an_expected_digest` still holds at source level |
| the ordinary path is unchanged | — | `…::test_a_completed_run_still_reaches_s_c_and_cleans_up_once`, and the whole of `test_executor.py` unchanged |

`test_an_exception_at_each_mutation_class_runs_the_whole_cleanup_once` is
parametrised over the **eight** mutation kinds that a generated step performs:
`os_group`, `os_account`, `group_membership`, `directory`, `file`,
`file_attribute`, `postgres_database` and `postgres_role`. The two remaining
declared kinds, `postgres_config_line` and `transient_unit`, have no generated
step — their steps are among the returned conflicts C-4 and C-2 — so no
exception can be raised at one; their reversals are still exercised, because the
whole derived cleanup runs in every case above.

## R5.6 Validation — exact results from this tree

Run serially against the final tree on **2026-09-06**, with the documented
interpreters. Every figure below is from this tree; **R4's totals are
superseded** and are retained in the R4 section as history about the tree R4
submitted.

| Command | Result |
|---|---|
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | **534 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **593 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3135 passed**, 0 failed, 0 skipped, 1 warning |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2840 passed**, 0 failed, **80 skipped**, 1137 warnings |
| `node --test "foundry-module/tests/"*.test.mjs` | **171 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean, exit 0, no output |
| `git diff --check` | clean, exit 0 |

`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` was exported for the
bot and web suites, and the two were run **serially** because they share the one
disposable database — finding F-6.

**One correction to the prompt's verification block, reported rather than
absorbed.** It places the `export` between the bot suite and the web suite.
`.agents/AGENTS.md` is explicit that the variable must be exported for *both*:
run without it, the bot suite reports **2813 passed, 322 skipped** and still
exits 0, which is precisely the green run that proves nothing the working
agreement warns about. Both runs were made; the table reports the one with the
database configured, and the 322-skip figure is recorded here so that neither is
mistaken for the other.

**The 80 web skips are exactly the established baseline**, and `-rs` gives both
reasons: 54 from `tests/web/test_p3_2_matrix.py:155` and 26 from
`tests/web/test_p3_3_matrix.py:198`, each *"permitted cells are asserted by the
per-route success cases"*. No new skip was introduced anywhere.

**The harness suite is 534 rather than R4's 481** because of the 52 new tests in
the two new modules and the one new test in `test_no_execution.py`. No
existing test was deleted, weakened or made conditional; the R4 suite is intact
and green, including every test that constrains what the executor may do.

**Checks not run.** No formatter, linter or type checker is configured in this
repository, so none was run. That is not a claim the code would pass one, and no
tooling was introduced.

## R5.7 Confirmations

- **No real process boundary ran.** `SubprocessBoundary(armed=True)` is
  constructed nowhere outside `cli.main`'s `--execute` branch, which was never
  taken, and it is constructed nowhere in the suite. The credential tests replace
  the boundary module's process starter with a recorder before the boundary is
  used at all, and `test_no_execution.py` asserts at source level that the one
  test module naming it neither imports it nor names it in code.
- **No privileged or mutation-bearing command ran.** No `sudo`, `su`,
  `systemd-run`, `capsh`, `useradd`, `userdel`, `groupadd`, `groupdel`,
  `usermod`, `gpasswd`, `chattr`, `setpriv`, `install` outside the workspace,
  PostgreSQL DDL or DML, configuration reload, service change or cleanup step was
  executed. `--execute` was never passed.
- **No target object was created.** No account, group, membership, directory,
  file, attribute, database, role, HBA line, identity-map line or transient unit
  exists on `oracle-test` or anywhere else as a result of this work. **Nothing
  was run on `oracle-test` at all**, and no SSH connection to it was made.
- **No privileged read, socket, HTTP request, database connection or external
  service access** was performed by the harness. The only database contacted was
  `freedom_test`, by the repository's own suites, over a Unix-domain socket.
- **Production and staging were not accessed.** No production `sudoers`,
  `pg_hba.conf` or `pg_ident.conf` was read; no Discord, Foundry, Google Drive,
  Google Sheets, credential, player datum or live character state was touched.
- **The host's account and group database was not read.** The new lookup is
  called only immediately before a step runs, and no step ran. Every test injects
  a table written in the test file.
- **Secrets and privacy.** No `.env`, service-account JSON, token, OAuth secret,
  database URL or Foundry credential was read, printed, committed or modified. No
  player data, character state, Discord identifier or Sheet content appears in any
  added or changed file; every fixture is synthetic, and the UIDs and GIDs in
  `test_boundary_identity.py` are written in that file rather than read from a
  host, and assert nothing about one.
- **Invariants preserved.** The default invocation still executes nothing and
  every test still executes nothing; argument vectors remain absolute, shell-free
  and covered by the manifest; cleanup remains derived, bounded and
  non-recursive; and the executor still refuses the submitted plan because its
  conflicts stand.
- **Worktree.** Nothing was reset, reverted, staged, committed, pushed or
  reformatted. Every unrelated change present at the start is preserved, including
  the concurrent live-bot defect fix and the disposable-server documentation work
  belonging to other contributors.

## R5.8 Status, stated exactly

- EH-R5-1 and EH-R5-2: **corrected and submitted for re-review. Neither is
  closed** — that is Codex's to decide.
- The five conflicts of §R4.C: **unchanged and open**, including C-1's request
  for a ruling on the guard widening.
- The `postgres` membership rule: **a new judgement offered for a ruling**
  (§R5.3), not a settled fact.
- Evidence harness execution: **not run**.
- P5.0-R5: **Blocking**. P5.0-R1 and P5.0-R4: untouched.
- A-5.0-3, A-5.0-4, A-5.0-5: **unconfirmed**. Checks C-1, C-3, C-4: **not run**.
- OD-62: **Open**, G-A provisional.
- Package 5.0: **`not ready`**. Migration `0014`, product implementation,
  production or staging mutation, deployment, cutover and Package 5.1+:
  **unauthorized**.

## R5.9 Request for Codex independent pre-execution re-review

**Codex's independent pre-execution re-review is requested** of:

1. **the credential contract in §R5.3** — whether the resolution order,
   `EXACT`/`AS_CONFIGURED` split and refusal set construct exactly the E1–E8
   identity vector the reviewed plan declares, and whether any evidence case
   depends on a group the contract does not carry;
2. **the `postgres` row specifically** — whether `AS_CONFIGURED` is accepted, or
   whether §2.12.2 should gain a `postgres` row and the rule become `EXACT`;
3. **the root precondition** — whether validating an already-root launcher *and*
   constructing 0/0/[] explicitly is the intended reading of *"never let
   `run_as="root"` mean whatever identity launched the CLI"*;
4. **the responsibility rule in §R5.4** — whether recording a step's mutations
   before the call, and therefore cleaning up after a command that may never have
   started, is the boundary the finding intends;
5. **the cleanup-failure semantics** — whether the constructed S-B outcome names
   enough, names only declared facts, and is correctly unreachable by S-C;
6. **the one test exemption** in `test_no_execution.py` — whether naming the
   process starter in a single test module, under the two narrower assertions
   that replace the blanket rule, is an acceptable way to assert real credential
   keywords, or whether the blanket rule should stand and the keywords be
   asserted some other way; and
7. **the regenerated digest**
   `b709eb20cd58726897cffc5791bd9712ae05d9214961e9957e3bc0cbcde9a344` and the
   regenerated concrete plan, which differ from R4's only in the digest line and
   the two changed source digests.

**Work stops here.** The executor is not run, no armed boundary is constructed,
no evidence object is created, no finding is closed, no assumption is confirmed,
no readiness item moves, and no authority is requested beyond the re-review
above.

---

# R4 — concrete vectors, derived cleanup, review manifest and executing runner

Date: 2026-09-05

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by the concrete-plan prompt of
2026-09-05. **That prompt authorizes implementation and dry-run validation
only. It does not authorize first privileged execution, and none occurred.**

Outcome: **the canonical approved target, the generated concrete argument
vectors, the derived cleanup, the review manifest and its digest, and a separate
executing runner behind four gates are submitted for independent pre-execution
review. Nothing was executed. Five conflicts block sixteen steps and are
returned rather than inferred around.**

## R4.0 The three things to read first

1. **§R4.C — the five conflicts.** Four of them are steps the reviewed design
   describes that **no argument vector can express** with the permitted
   executable set, and the fifth is a change to a reviewed guard. The prompt says
   to stop and return the exact conflict rather than infer permission, so the
   generator emits them as `UnresolvedStep` values — no `argv`, unreachable by
   the executor — and `ExecutingRunner` refuses any plan carrying one. The plan
   as submitted is therefore **not runnable, by construction**, and that is the
   correct state rather than a shortfall being smuggled past.
2. **§R4.D — two latent defects the concrete stage reached.** `EH-R4-1`: the
   `FILE_ATTRIBUTE` reversal could not be constructed under any input, because
   its `chattr -i -a` contains `-a`, a member of `FORBIDDEN_CLEANUP_TOKENS`. R3's
   suite asserted the reversal *table* had an entry per kind, not that the entry
   produced a step. `EH-R4-2`: every reversal ran as `root`, so `DROP ROLE` and
   `DROP DATABASE` would have asked peer authentication for a PostgreSQL role
   called `root`, been refused, and produced S-B for a defect in the plan's own
   cleanup. Both are the same shape as EH-R3-2's second blocker: a path no test
   had ever constructed.
3. **§R4.C-1 — the one guard this work changed.** The run creates its own root,
   and `DisposableTarget.contained_path()` refuses the root, so the root
   directory could not be declared as a mutation and cleanup could not remove it.
   A new, separate `root_or_contained_path()` admits exactly one more path. It is
   submitted for a ruling, not presented as settled.

## R4.1 Exact files changed and added

### Added — planning tier (still no process, no network, no file I/O)

| File | What it owns |
|---|---|
| `tools/phase_5_0_evidence/approved_target.py` | the **one** construction of the approved target, the confirmed environment facts, the identity digest, the confirmation token, and `require_approved_target()` |
| `tools/phase_5_0_evidence/concrete_plan.py` | the generator: 39 declared mutations, 64 argument vectors, 16 `UnresolvedStep`s, and the mutation-to-cleanup traceability table |
| `tools/phase_5_0_evidence/capture.py` | the closed `CapturePolicy` set and its sanitizers — pure text processing, so it lives in the planning tier and a step's policy is part of what the manifest digests |
| `tools/phase_5_0_evidence/review_manifest.py` | the deterministic manifest, `COVERED_SOURCES`, the exit classifications and the aggregate digest |

### Added — execution tier (`tools/phase_5_0_evidence/execution/`)

| File | What it owns |
|---|---|
| `execution/__init__.py` | the tier's contract: what each module may do and what none may |
| `execution/boundary.py` | `ProcessBoundary`, `CommandResult`, `SubprocessBoundary`, `RecordingBoundary`, the fixed environment and the timeout table. **The only file in the repository that imports `subprocess`** |
| `execution/executor.py` | `ExecutingRunner` — the four gates, per-step revalidation, the stop conditions, and derived cleanup after the first reached mutation |
| `execution/cli.py` | the only entry point that can reach the executor; `--execute`, `--confirm-target`, `--reviewed-digest`; `--manifest`, `--manifest-out`, `--render` |

### Changed

| File | Change | Why |
|---|---|---|
| `tools/phase_5_0_evidence/targets.py` | new `DisposableTarget.root_or_contained_path()` | **C-1**: the run creates its own root and cleanup must remove it. `contained_path()` is unchanged and still refuses the root |
| `tools/phase_5_0_evidence/plan.py` | new `StepRole`; `CommandStep` gains `role`, `satisfying_statuses`, `refusal_required`, `capture` and `is_satisfied_by()`; the `DIRECTORY` mutation validates through `root_or_contained_path()` | a step's expectation becomes machine-checkable and reviewed rather than prose; a mutation-bearing step may record only its exit status and may not require a refusal |
| `tools/phase_5_0_evidence/cleanup.py` | `_clear_attributes` emits `chattr -ia`; `psql` reversals gain `--no-password` and `--host`; `psql` reversals run as `postgres`; `_rmdir` uses `root_or_contained_path()` | **EH-R4-1**, **EH-R4-2**, and the non-interactive property a bounded run needs |
| `tests/phase_5_0_evidence/test_no_execution.py` | two declared tiers; an exhaustive scan that fails on a module in neither; `subprocess` permitted in exactly one named file; no shell anywhere; import performs no I/O; the planning tier never imports the execution tier | the property the whole package rests on, restated for a package that now contains an executor |
| `tests/web/test_p3_4_static_assets.py` | the four new planning modules and the four execution-tier paths declared in `PERMITTED_PHASE_5_0_EVIDENCE_HARNESS` | the harness's own allowlist, under the harness's own authorization. **No other allowlist was touched** |
| `docs/review/phase-5-0-evidence-harness-execution-plan.md` | new §0 distinguishing template from generated plan; the now-false whole-package no-`subprocess` claim corrected; §§5–6 marked as template; §9 and §10 updated | the prompt's *"do not silently replace historical placeholder documentation"* |

### Added — tests

| File | Proves |
|---|---|
| `tests/phase_5_0_evidence/test_approved_target.py` | the canonical target carries exactly the approved facts, and a one-field deviation is refused **for every compared field** |
| `tests/phase_5_0_evidence/test_concrete_plan.py` | no placeholder survives generation; every path is the approved one; only two files are written outside the root; nothing resolves through `PATH`; cleanup ordering, breadth and traceability; the capture sanitisers against planted secret sentinels; the manifest |
| `tests/phase_5_0_evidence/test_executor.py` | the four gates, the stop conditions, cleanup after **every** mutation prefix, S-B blocking a rerun, and that no test in the file can start a process |

### Added — generated artifacts

| File | What it is |
|---|---|
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | the concrete plan, rendered deterministically for line-by-line review |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | the machine-readable manifest the digest is computed over |

**No production application code, migration, database schema, deployment file,
roadmap, project-status, RAID, decision-register or change-log record was
touched.** `models/skills.py` and `tests/test_skills.py` remain Gemini's
concurrent live-bot defect fix and were not modified; that fix is now declared in
its own `PERMITTED_LIVE_BOT_DEFECT_FIXES` allowlist and the scope guard passes.

## R4.2 The approved target, exactly

| Fact | Value |
|---|---|
| Host | `oracle-test` |
| IPv4 | `138.2.182.39` |
| Operating system | `Ubuntu 26.04.1 LTS`, `x86_64` |
| Active kernel | `7.0.0-31-generic` |
| Filesystem root | `/var/lib/fb-evidence-p5-0` |
| Filesystem | `ext4` on `/dev/sda1` |
| PostgreSQL instance | `16/main`, port `5432` |
| PostgreSQL socket | `/var/run/postgresql` |
| PostgreSQL configuration | `/etc/postgresql/16/main` |
| Disposable database | `fb_evidence_p5_0` |
| Confirmed by | Peter Duscha, Operations Owner, **2026-09-05** |

Constructed once, in `approved_target.APPROVED_TARGET`, with the disposability
statement naming Peter and the 2026-09-05 decision carried on the value itself.
It still passes every existing validation: absolute paths, a root three levels
deep with an `fb-evidence-` last component, an `fb_evidence_`-prefixed database
that is none of the forbidden names, no volatile or forbidden root, and a
configuration directory that must name a PostgreSQL instance and admits two
filenames.

**Target assignment: complete. Generic-kernel baseline issue: resolved.** Neither
is reopened anywhere in this submission.

## R4.3 What was generated

| | Count |
|---|---|
| Declared mutations | **39** |
| Generated argument vectors | **64** |
| Derived cleanup steps | **42** |
| Unresolved steps | **16**, across conflicts C-2, C-3, C-4, C-5 |
| Review-manifest digest | `205e501ed04adf5b1fcefc1d4a24fc36b3e6a791f07cb4dbf924d1af6722a57b` |
| Target confirmation token | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#ceb58ad1f9f0e070` |

The complete plan and cleanup are
`docs/review/phase-5-0-evidence-harness-concrete-plan.md`, generated
deterministically from the same tree; the machine-readable form is
`…-review-manifest.json`. Both are reproduced by

```sh
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

which is a **dry run**: it prints what would run and starts nothing.

### Properties the suite checks over every generated vector

- no `<TARGET_*>`, `<EVIDENCE_DB>`, `<PG_CONFIG_DIR>`, `<PG_SOCKET_DIR>`,
  environment variable, `~`, glob or shell metacharacter;
- every executable an absolute path, and in `PERMITTED_EXECUTABLES` or inside the
  disposable root — nothing resolves through `PATH`;
- arguments are tuples passed to process execution; no vector is a string and no
  string is concatenated into one;
- every mutation is declared before a step can perform it, and every declared
  mutation is bound to the approved target;
- every step carries a run-as identity from a closed set, a purpose, its evidence
  cases, the exit statuses that satisfy it and what it may record;
- controls precede the cases that depend on them, in every band that has both,
  and prerequisites precede every mutation;
- the complete PostgreSQL OS-user/role mapping `freedomcoord →
  freedom_migration_coordinator` is carried on both configuration mutations, and
  neither half is defaulted;
- only `pg_hba.conf` and `pg_ident.conf` are written outside
  `/var/lib/fb-evidence-p5-0`, and both are inside `/etc/postgresql/16/main`;
- PostgreSQL is **reloaded** and never restarted — no `restart`, no
  `postgresql@16-main`, no `pg_ctl` appears in any vector;
- `fb_evidence_p5_0` appears and `freedom_test` never does.

### The one source path outside the root, declared

`install` cannot create a file without a source, so every empty artefact is
created with `/usr/bin/install … /dev/null <path>`. `/dev/null` is named as a
**source** and never as a destination, it is a kernel-provided character device,
and it is neither production configuration nor player data. It is declared here
rather than left for a reviewer to notice.

## R4.C The five conflicts — returned, not inferred around

### C-1 — the disposable root cannot be declared as a mutation. *A reviewed guard changed; a ruling is requested.*

`install --directory /var/lib/fb-evidence-p5-0` is the first provisioning step,
so the root is an object the run creates and cleanup must remove. But
`DisposableTarget.contained_path()` refuses `normalized == self.root_path`, so
the root's `DIRECTORY` mutation could not be declared, and without the
declaration cleanup has no `rmdir` for it and the run leaves the root behind —
residue, and therefore S-B on every otherwise clean run.

**What was done.** A new, separate `DisposableTarget.root_or_contained_path()`
that returns the root itself or delegates to `contained_path()`.
`contained_path()` is unchanged and still refuses the root. The new method is
used in exactly two places: the root's `DIRECTORY` mutation validation and the
`rmdir` reversal derived from it.

**Why it is defensible, and why it is still a ruling for Codex.** The root is the
most-validated path in the package — `validate_mutation_root()` has already
refused `/`, every `FORBIDDEN_ROOTS` entry and every ancestor of one, the
repository worktree, every `tmpfs` root, anything shallower than three levels and
anything not `fb-evidence-`-prefixed — and `rmdir` removes it only when empty, so
a root still holding an undeclared artefact is reported as residue rather than
deleted. It is nonetheless a change to a guard R1–R3 reviewed, and the prompt is
explicit that a weakened guard is a conflict to return. **Codex should rule
whether this widening is accepted, or whether the root should instead be an
operator-created precondition outside the harness.**

### C-2 — the probe program and the Band-5 case binary have no reviewed source. *Blocking; 13 steps.*

§2.13.2a Stage 1 is six operations, Stage 2 is nine, Stage 4 is four, and §5.2's
`JNL-52` matrix is eight — and every one of them is `open(2)` with specific
flags, `rename(2)`, `unlink(2)`, `pwrite(2)` or `FS_IOC_GETFLAGS`, whose **errno
is the evidence**. §2.13.5c's `capsh --shell=` execs a case binary at
`<root>/bin/case`. Nothing in the reviewed design says what that program is, what
it contains, or how it is produced, and no permitted executable performs those
syscalls: `namei` resolves a path, it does not open one `O_WRONLY`.

**Not invented.** A program that runs under constructed capability identities and
decides what a refusal means is exactly the thing that must not be written
without review.

**One ordering question comes with it.** §4 lists `P-03`/`P-04` — the case
binary's file-capability and mode prerequisites — among the Band-1 checks
asserted *"before anything is constructed"*, and their subject is a file Band 3
creates. The generator emits them in the position the design gives them and says
so in the step's own purpose; resolving C-2 has to settle where they actually
run rather than letting the position be inherited.

**Generated anyway, because these *are* commands:** the two `namei -l` positive
traverse controls (`JNL-52` cases 5 and 7), `chattr`/`lsattr` for every attribute
the design sets and reads back, `findmnt` for Stage 3's mount facts, and
`getcap`/`stat` for the case binary's file-capability and mode prerequisites. The
`file:<root>/bin/case` mutation **is** declared, so cleanup removes the binary if
a later approved run creates it.

**What would resolve it.** A reviewed probe/case program: its source, its exact
operations per case, its exit-status encoding, and how it is placed inside the
root without a shell.

### C-3 — `<root>/journal/current` is a symlink and nothing permitted creates one. *Blocking; 1 step.*

§2.13.3 specifies it. `install` copies; `ln -s` and `cp -s` are not in
`PERMITTED_EXECUTABLES` and adding either is a broader executable, which the
prompt names as a conflict to return.

**No mutation is declared for it**, deliberately: cleanup must not name a path
the plan cannot create.

**What would resolve it.** Either a reviewed addition of `/usr/bin/ln` restricted
to `-s` with both operands inside the disposable root, or a ruling that the
disposable facsimile does not need the symlink.

### C-4 — the five HBA lines and the one identity-map line are file *content*. *Blocking; 2 steps.*

§2.12.3's lines have to be written into `/etc/postgresql/16/main/pg_hba.conf` and
`pg_ident.conf`. No permitted executable writes content: `install` copies a file
that must already exist, and there is no `tee`, no `sed -i` and no redirection.
Producing the replacement file first moves the same problem one step earlier.

**Everything around it is generated:** both byte-exact `install` captures into
`<root>/before/`, `CREATE DATABASE`, `CREATE ROLE … PASSWORD NULL CONNECTION
LIMIT 2`, `SELECT pg_reload_conf()`, the positive control connection, the two
identity denials and the TCP denial. Both configuration mutations are declared,
so cleanup's restore → one reload → control → proof phase already exists and
already covers them.

**What would resolve it.** A reviewed, bounded file-materialisation mechanism in
the executor: exactly the reviewed line set, only to a path `config_path()`
returns, only after the capture succeeded, with the produced bytes pinned in the
manifest.

### C-5 — `capsh` takes numeric ids for accounts the run has not yet created. *Blocking; 8 steps.*

`capsh --uid=`, `--gid=` and `--groups=` are numeric. `freedomsheet`,
`freedomcoord`, `fbprobe` and `freedomjournal` do not exist until Band 2 creates
them on the target, so the numbers are not knowable at plan time — and §2.13.5c
already says the harness resolves them "with `getpwnam`/`getgrnam` **at run
time**". A symbolic form is a placeholder the planner refuses, and a guessed
number is a number nobody verified. Every invocation additionally execs the
case binary of C-2.

E7 is listed among the eight for completeness and needs nothing: it has no
invocation by design, and P-01/P-02 are the observations it is classified from.

**What would resolve it.** A reviewed late-binding rule — resolve exactly the
four names this run creates, immediately before the step, refuse any other name,
re-validate the constructed vector, and pin the **symbolic** form rather than the
numbers in the review manifest — plus C-2.

### Conflicts not raised

No new target value was needed, no production read was needed, no broader path
was needed beyond the `/dev/null` source declared above, and no new mutation kind
was needed. `PERMITTED_EXECUTABLES` is **unchanged**.

## R4.D Two latent defects reached by generating a real plan

### EH-R4-1 — the `FILE_ATTRIBUTE` reversal could not be constructed under any input

`_clear_attributes` emitted `("/usr/bin/chattr", "-i", "-a", "--", path)`. `-a` is
a member of `FORBIDDEN_CLEANUP_TOKENS` — it is there because `-a` means
`--archive` to `cp` and `rm` — so `CleanupStep.__post_init__` refused every
attribute reversal outright. The first real plan with an attribute mutation was
the first input that ever built one.

R3's suite asserted `set(_REVERSALS) == set(MutationKind)`. That is a claim about
a table having an entry, not about the entry producing a step, and it is the same
class of gap as EH-R3-2's second blocker.

**Fixed** by emitting `chattr -ia` — one valid `chattr` mode argument that clears
both flags — so the guard keeps its meaning for every executable to which `-a`
really is a breadth option. **Regression:**
`test_concrete_plan.py::test_every_mutation_kind_can_actually_build_a_reversal`
constructs a reversal for all ten kinds.

### EH-R4-2 — every cleanup reversal ran as `root`, including the `psql` ones

`CleanupPlan.for_mutations()` set `run_as="root"` for every reversal. `psql` over
the local socket as `root` asks peer authentication for a PostgreSQL role called
`root`, which the disposable instance does not have — so `DROP ROLE` and `DROP
DATABASE` would have been refused for an authentication reason, cleanup would not
have completed, and the run would have reported **S-B for a defect in its own
cleanup plan**.

**Fixed** by deriving the identity from the executable — `postgres` for `psql`,
`root` otherwise — so a reversal added later cannot forget it.

### A third, smaller correction

The `psql` reversals carried neither `--no-password` nor `--host`. A cleanup step
that prompts is a cleanup step that hangs. Both are now on every `psql` vector in
the package, matching the reload and verification steps that already had them.

## R4.4 The executing runner

Separate from `DryRunRunner`, in a separate tier, behind four gates — all at
construction, all before a process exists, none skippable and none with a
`--force`:

| # | Gate | Refusal |
|---|---|---|
| 1 | the plan's target is the approved one, field for field | `TargetRefused`, naming every differing field and both values |
| 2 | the plan carries no unresolved conflict | `ExecutorRefused` — **this is the gate the submitted plan fails** |
| 3 | the confirmation token is exact, compared with `hmac.compare_digest` | `ExecutorRefused` |
| 4 | the reviewer's digest matches the manifest recomputed from the live tree | `ExecutorRefused`, printing what this tree computes and saying it is a value to submit, not authority to run |

### Reachability

Not through import: `main` runs only under `__main__`, importing the CLI arms
nothing, and `SubprocessBoundary()` is unarmed by default and refuses to start
anything. A **default invocation is a dry run** — it constructs a
`RecordingBoundary`, an object with no path to a process. The real boundary is
constructed on exactly one line, inside the `--execute` branch, and armed on that
same line.

### Execution properties

- `CommandStep.argv` is executed directly. `shell=False` is written as a literal
  at the one call site; there is no `os.system`, no shell script, no `eval`, no
  command concatenation and no `PATH` resolution — `argv[0]` is always absolute.
- Every step is **revalidated immediately before execution**: the whole vector
  through `plan.validate_argv` against the plan's target, the executable against
  the permitted set, the identity against the closed set, the timeout against
  zero.
- The declared `run_as` is honoured through `subprocess`'s own `user=` parameter,
  which sets the child's credentials between `fork` and `exec`. Deliberately not
  a wrapper binary: `setpriv` or `su` in the vector would mean the reviewed
  vector is not the vector that runs. A blank identity cannot exist — a step with
  one cannot be constructed — and an unknown one is refused before execution.
  Nothing defaults to `root`.
- A minimal fixed environment; the inherited one is discarded whole. `LC_ALL=C`
  so an operator's locale cannot change what a run observes, and the explicit
  PostgreSQL 16 client directory plus `PGCONNECT_TIMEOUT=10` for `psql`.
- Bounded timeouts on every step, 30–120 seconds by executable. `stdin` is
  `/dev/null` and `cwd` is `/`.
- Only sanitized observations are captured, through a closed `CapturePolicy` set
  declared **per step in the reviewed plan**. Raw output never leaves
  `boundary.py`; `CommandResult` has no field that could hold it, and standard
  error is recorded only as *whether it was non-empty*. A mutation-bearing step
  may record nothing but its exit status.
- The run **stops on the first unsatisfied step** — where "satisfied" is what the
  reviewed plan says, so `getent`'s exit 2 on an absent group is satisfied and
  exit 0 is not — and a dependent case is not interpreted after a control in its
  band failed.
- **Derived cleanup runs whenever a mutation was reached**, once, never retried.
  Cleanup failure is S-B with the residue named by absolute path and the
  effective-configuration risk named in full, and the next invocation refuses
  while residue remains.
- No artifact is written unless the run completed, cleanup reached S-C and every
  step was satisfied.

### The digest is a reviewer's input, not the tree's own

The executor recomputes the manifest from the live tree and compares it with a
value supplied on the command line. It reads no expected digest from a file and
writes none — `test_executor.py::test_the_executor_neither_reads_nor_writes_an_
expected_digest` proves that at source level. Editing any covered source changes
the recomputed digest and the run refuses; the approved value comes from Codex.

## R4.5 Derived cleanup, and its traceability

Generated from the 39 declared mutations by `CleanupPlan.for_mutations()` — 42
steps, nobody hand-writes one. The complete
**mutation-to-cleanup traceability table** is §5 of the generated concrete plan;
every one of the 39 has exactly one reversal, and the suite asserts that rather
than the table asserting it.

Order, as generated and as checked by `ordering_holds()` and by the suite:

1. restore `pg_ident.conf`, then `pg_hba.conf`, each from its byte-exact
   pre-change capture under `<root>/before/`;
2. **one** reload, after every restore;
3. the control — an ordinary local `postgres` connection must succeed;
4. the proof — `freedomcoord` asking for `freedom_migration_coordinator` must be
   **refused**, while the role still exists;
5. stop the transient unit; then `DROP ROLE`, then `DROP DATABASE`, both under
   the restored rules;
6. clear attributes, then remove the files they were on;
7. `rmdir` each directory, deepest first, ending at the root;
8. remove group memberships, then accounts, then groups.

Bounded: no generated argv contains `-r`, `-R`, `-rf`, `-fr`, `--recursive`,
`--no-preserve-root`, `-a` or `*`; `rm --force` takes one named path and `rmdir`
one empty directory; every path is inside the root except the two configuration
files. Re-runnable in the documented sense — no step performs a destructive act
when its object is absent, and every `psql` reversal carries `IF EXISTS`. Nothing
pre-existing is ever cleaned: only declared objects have reversals.

## R4.6 Requirement-to-code-to-test traceability

| Requirement | Code | Test |
|---|---|---|
| one canonical typed construction of the approved target | `approved_target.APPROVED_TARGET` | `test_approved_target.py::test_the_canonical_target_carries_exactly_the_approved_facts`, `…::test_the_confirmed_environment_is_the_one_peter_named_and_codex_verified` |
| a disposability statement naming Peter and the 2026-09-05 decision | `approved_target.DISPOSABILITY_STATEMENT` | `…::test_the_disposability_statement_names_the_decision_and_its_owner` |
| the target still passes every existing validation | `targets.validate_mutation_root`, `validate_database_name`, `validate_postgres_config_directory` | `…::test_the_approved_target_still_passes_every_structural_guard` |
| a one-field deviation refused, for every field | `approved_target.target_deviations`, `require_approved_target` | `…::test_a_one_field_deviation_is_refused` (7 cases), `…::test_every_compared_field_has_a_deviation_case` |
| generated vectors contain no placeholder | `concrete_plan.build_concrete_plan` | `test_concrete_plan.py::test_no_generated_argument_carries_a_placeholder_or_a_variable` |
| vectors match only the approved root, database, socket and configuration directory | same | `…::test_every_path_is_inside_the_target_or_is_one_of_the_named_exceptions`, `…::test_the_generated_plan_names_the_approved_database_and_never_freedom_test`, `…::test_every_psql_step_uses_the_approved_socket_directory` |
| only `pg_hba.conf` and `pg_ident.conf` written outside the root | `targets.config_path` | `…::test_only_pg_hba_and_pg_ident_are_written_outside_the_target_root` |
| no command resolves through `PATH` | `plan.validate_argv`, `executor._revalidate` | `…::test_no_generated_command_resolves_through_path` |
| no shell execution is possible | `boundary.SubprocessBoundary` | `test_no_execution.py::test_no_execution_tier_module_can_reach_a_shell`, `…::test_only_the_boundary_module_may_import_subprocess`, `test_concrete_plan.py::test_no_generated_vector_names_a_shell_or_a_privilege_helper` |
| no undeclared mutation can execute | `plan.ExecutionPlan.__post_init__` | `test_concrete_plan.py::test_an_undeclared_mutation_cannot_be_planned`, `…::test_every_mutation_bearing_step_declares_its_mutations` |
| the dry-run path executes nothing | `cli.main`, `boundary.RecordingBoundary` | `test_executor.py::test_the_default_cli_invocation_executes_nothing`, `…::test_the_recording_boundary_starts_nothing`, `…::test_the_real_boundary_is_unarmed_by_default_and_refuses_to_start_anything` |
| execution requires the explicit flag and the exact token | `cli.build_parser`, `ExecutingRunner.__post_init__` | `…::test_the_cli_defaults_to_not_executing`, `…::test_the_cli_refuses_execute_without_the_token_or_the_digest`, `…::test_execution_requires_the_exact_confirmation_token` (7 cases) |
| the executor refuses an unreviewed plan digest | `ExecutingRunner.__post_init__`, `review_manifest.digests_match` | `…::test_execution_refuses_when_no_reviewed_digest_is_supplied`, `…::test_execution_refuses_an_unreviewed_plan_digest`, `…::test_a_changed_source_file_invalidates_a_previously_reviewed_digest`, `…::test_the_executor_neither_reads_nor_writes_an_expected_digest` |
| a plan whose target differs is refused | `approved_target.require_approved_target` | `…::test_the_executor_refuses_a_plan_whose_target_is_not_the_approved_one`, `…::test_the_executor_refuses_an_unassigned_or_unconfirmed_target` |
| identity transitions cannot default or be blank | `CommandStep.__post_init__`, `executor.PERMITTED_RUN_AS`, `boundary` | `…::test_an_identity_cannot_be_blank_and_cannot_default`, `…::test_every_step_runs_as_one_of_the_closed_identity_set`, `…::test_an_identity_transition_is_not_composed_into_the_argument_vector` |
| bounded timeouts stop the run | `boundary.timeout_for`, `ExecutingRunner.execute` | `…::test_every_step_has_a_bounded_non_zero_timeout`, `…::test_a_timeout_stops_the_run` |
| positive-control failures prevent dependent interpretation | `ExecutingRunner.execute` | `…::test_a_positive_control_failure_prevents_dependent_interpretation`, `test_concrete_plan.py::test_the_positive_controls_precede_the_cases_that_depend_on_them` |
| interruption after each mutation prefix produces the correct derived cleanup | `ExecutingRunner._clean_up` | `test_executor.py::test_interruption_after_each_mutation_prefix_still_runs_the_whole_derived_cleanup` (every prefix), `…::test_a_run_that_reached_no_mutation_runs_no_cleanup` |
| partial configuration mutation restores every reached file, reloads and verifies | `CleanupPlan.for_mutations` | `test_concrete_plan.py::test_a_partial_run_that_reached_one_configuration_file_still_gets_the_whole_phase` |
| restore before reload, reload before verify, verify before dropping | `CleanupPlan.ordering_holds` | `test_concrete_plan.py::test_configuration_is_restored_reloaded_verified_then_roles_dropped`, `test_executor.py::test_cleanup_restores_before_reloading_and_reloads_before_verifying` |
| failed cleanup is S-B and blocks a rerun | `classify_cleanup`, `ExecutingRunner.execute` | `test_executor.py::test_failed_cleanup_blocks_a_rerun_rather_than_retrying_it`, `…::test_an_unrestored_configuration_file_is_s_b_and_names_the_risk`, `…::test_a_proof_that_succeeded_means_the_mapping_may_still_be_effective`, `…::test_cleanup_is_never_retried_within_a_run` |
| recursive, wildcard, broad, unresolved and out-of-target cleanup is unrepresentable | `FORBIDDEN_CLEANUP_TOKENS`, `CleanupStep.__post_init__`, `contained_path` | `test_concrete_plan.py::test_no_generated_cleanup_step_can_express_a_recursive_or_broad_removal`, `…::test_directories_are_removed_deepest_first_and_only_with_rmdir`, `…::test_a_cleanup_step_outside_the_target_cannot_be_generated` |
| attributes removed before files; memberships before users before groups | declaration order + reverse generation | `…::test_attributes_are_cleared_before_their_files_are_removed`, `…::test_memberships_are_removed_before_users_and_users_before_groups` |
| captured output is sanitized and cannot carry a secret sentinel | `capture.sanitize`, `_shaped` | `…::test_a_planted_secret_sentinel_cannot_reach_an_observation` (all 8 policies), `test_executor.py::test_only_sanitized_observations_are_recorded`, `…::test_a_command_result_has_no_field_that_could_hold_raw_output` |
| importing every harness module performs no I/O or process execution | both tiers | `test_no_execution.py::test_importing_every_module_in_the_package_performs_no_io`, `…::test_the_planning_tier_never_imports_the_execution_tier`, `…::test_no_module_in_the_package_escapes_both_tiers` |
| every mutation kind's reversal can be built | `cleanup._REVERSALS` | `test_concrete_plan.py::test_every_mutation_kind_can_actually_build_a_reversal` (EH-R4-1) |

**Every test uses fakes or the injected process boundary. None performs a
privileged mutation, and none can: `test_executor.py` injects `FakeBoundary`
throughout, and the real boundary is never armed anywhere in the suite.**

## R4.7 Validation — exact results from this tree

Run serially with `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`
exported. The work was done on 2026-09-05; the **final confirming run of the
full bot, web and Foundry suites against the submitted tree crossed midnight and
completed on 2026-09-06**, and the figures below are that run's. Stating the
date exactly matters here for the same reason the figures do: a total carried
over from a different tree, or a different day's tree, is an assertion about a
state that no longer exists.

| Command | Result |
|---|---|
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | **481 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **540 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3135 passed**, 0 failed, 0 skipped, 1 warning |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2840 passed**, 0 failed, **80 skipped**, 1137 warnings |
| `node --test "foundry-module/tests/"*.test.mjs` | **171 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean, no output |
| `git diff --check` | clean, exit 0 |

**The one warning in the bot suite** is `discord/player.py`'s `audioop`
deprecation, from the installed library and not from this repository.

**The 80 web skips are exactly the established baseline**, and `-rs` gives both
reasons: 54 from `tests/web/test_p3_2_matrix.py:155` and 26 from
`tests/web/test_p3_3_matrix.py:198`, each *"permitted cells are asserted by the
per-route success cases"*. No new skip was introduced.

**`test_p3_4_static_assets.py::test_no_unrelated_production_files_modified`
passes.** The `models/skills.py` violation R3 reported is resolved: that live-bot
defect fix is now declared in its own `PERMITTED_LIVE_BOT_DEFECT_FIXES`
allowlist, by its own owner, as R3 asked. This submission added only the eight
harness paths to `PERMITTED_PHASE_5_0_EVIDENCE_HARNESS` and touched no other
allowlist.

**Every figure above is from this tree**, run serially after the final edit. The
harness suite is 481 rather than R3's 339 because of the three new test modules
and the rewritten no-execution scan; the bot suite is 3135 rather than 3119 and
the web suite 2840 rather than 2835 because of concurrent authorized work by
others, not because of this submission.

The generated artifacts are reproducible: rendering twice produces byte-identical
files, verified by `diff`.

## R4.8 Confirmations

- **No privileged or mutation-bearing command ran.** No `sudo`, `su`,
  `systemd-run`, capability-bearing `capsh`, `useradd`, `groupadd`, `usermod`,
  `gpasswd`, `chattr`, `setpriv`, `install` outside the workspace, PostgreSQL
  DDL/DML, configuration reload, service change or destructive cleanup. The
  executor was never armed; `SubprocessBoundary(armed=True)` is constructed
  nowhere outside `cli.main`'s `--execute` branch, which was never taken.
- **No target object was created.** No account, group, membership, directory,
  file, attribute, database, role, HBA line, identity-map line or transient unit
  exists on `oracle-test` or anywhere else as a result of this work. Nothing was
  run on `oracle-test` at all.
- **Production and staging were not accessed.** No production `sudoers`,
  `pg_hba.conf` or `pg_ident.conf` was read. No Discord, Foundry, Google Drive,
  Google Sheets, credential, player datum or live character state was touched. No
  network call was made. The only database contacted was `freedom_test`, by the
  repository's own suites, over a Unix-domain socket.
- **Secrets.** No `.env`, service-account JSON, token, OAuth secret, database URL
  or Foundry credential was read, printed, committed or modified.
- **Privacy.** No player data, character state, Discord identifier or Sheet
  content appears in any added or changed file. Every fixture is synthetic. The
  authentication mapping is an identity and a role name and carries no rule text,
  address, method or credential.
- **Worktree.** Nothing was reset, reverted, staged, committed, pushed or
  reformatted. Every unrelated change present at the start is preserved.

## R4.9 Failures, skips, warnings and checks not run

- **Checks not run.** No formatter, linter or type checker is configured in this
  repository, so none was run. That is not a claim the code would pass one, and
  no tooling was introduced.
- **Not run, deliberately.** The executor. No band, no case, no privileged read.
  Every band remains a function over observations that do not exist.
- **Not resolvable here.** The five conflicts in §R4.C. They need a maintainer or
  reviewer decision, not more implementation.
- Suite-level failures, skips and warnings are in the §R4.7 table exactly as
  reported.

## R4.10 Status, stated exactly

- Target assignment: **complete**.
- Generic-kernel baseline issue: **resolved**.
- Concrete vectors and executor: **submitted for review, not approved**.
- Evidence harness execution: **not run**.
- P5.0-R5: **open**.
- Package 5.0: **not ready**.
- Migration `0014` and product implementation: **unauthorized**.
- P5.0-R1, P5.0-R4: untouched. A-5.0-3, A-5.0-4, A-5.0-5: unconfirmed. C-1, C-3,
  C-4 (the *checks*, not this section's conflict ids): **not run**. OD-62:
  Open, G-A provisional. Package 5.1+: unauthorized.

## R4.11 Request for Codex pre-execution review

**Codex's independent pre-execution review is requested** of:

1. **the five conflicts in §R4.C**, and in particular whether **C-1**'s guard
   widening is accepted or whether the disposable root should be an
   operator-created precondition instead;
2. **the generated concrete plan** — every one of the 64 argument vectors, line
   by line, in `phase-5-0-evidence-harness-concrete-plan.md`;
3. **the derived cleanup** and its 39-row traceability table, and specifically
   whether the ordering claim in §R4.5 holds for every interruption prefix;
4. **the executor's four gates**, and whether the digest mechanism genuinely
   prevents the tree from approving itself;
5. **the two tiers** — whether `execution/` is an honest boundary or an evasion
   of the no-execution scan, and whether `test_no_execution.py`'s exhaustive
   partition closes that question;
6. **the capture policies** — whether the closed set and its per-field shape
   validation are narrow enough that nothing a command prints can reach an
   artifact; and
7. **EH-R4-1 and EH-R4-2** in §R4.D, and whether any comparable never-constructed
   path remains.

**Work stops here.** The executor is not run, no P5 evidence object is created,
no finding is closed, no assumption is confirmed, and no authority is requested
beyond the review above.

## Post-R3 target assignment — no execution yet

Peter Duscha named and confirmed `oracle-test`, root
`/var/lib/fb-evidence-p5-0`, PostgreSQL `16/main`, configuration directory
`/etc/postgresql/16/main`, socket `/var/run/postgresql`, and database
`fb_evidence_p5_0` as the exact disposable target. He confirmed Ubuntu 26.04
with the generic 7.x kernel as the future production baseline. Codex verified
the booted `7.0.0-31-generic` kernel and the target prerequisites and accepted
the target assignment.

The harness remains unexecuted. Its current runner is deliberately dry-run-only
and its published vectors remain non-runnable placeholders. The next bounded
work is concrete vector/cleanup regeneration and a separately reviewed executor,
followed by Codex pre-execution review. P5.0-R5 therefore remains open and
Package 5.0 remains `not ready`.

---

# R3 — pre-execution remediation, 2026-09-05

Date: 2026-09-05

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Outcome: **the two Blocking findings and the Important documentation finding are
remediated in the harness, its tests, the execution plan and this handback. No
privileged or mutation-bearing evidence command has been run. No finding,
assumption, readiness item or operational check is closed, passed or confirmed,
and Package 5.0 remains `not ready`.**

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-r3-prompt.md`.

Target: **`UNASSIGNED`**. No disposable host, filesystem or PostgreSQL instance
was named, invented or requested.

## R3.1 The three findings, conceded before their corrections

### EH-R3-1 — Blocking: R2 changed the contract without migrating its tests. **Conceded.**

R2 correctly moved dependent classification from a duplicated control status to
an actual `EvidenceRecord` and introduced an explicit `CaseRole`. It did not
carry that change through the tests. They still omitted the required
`case_role`, passed the removed `positive_control_status`, passed
`control_status=` where the band classifiers now take `control=`, constructed
dependent `AccessCase` and `CapabilityCase` values with the default `STANDALONE`
role, and built `CleanupStep` through the superseded
`mutation_id`/`absent_statuses` interface. The focused suite therefore failed
before it could prove the R2 security property, and the handback recorded an
older **289 passed** figure that was not evidence about the submitted tree. The
finding is correct as written.

**It was worse than an unmigrated suite.** The regressions EH-R2-1's own
"required regressions" list demanded — a missing control, a duplicate case id, a
self-reference, a cycle, a cross-band reference, an inadmissible reference, and
order-independent resolution — had **never been written at all**. R2 shipped the
reference-graph resolution in `records.py` with no test exercising any of it.
They exist now.

### EH-R3-2 — Blocking: PostgreSQL configuration cleanup cannot be planned. **Conceded.**

`CleanupPlan.for_mutations()` creates a post-reload refusal verification for each
`POSTGRES_CONFIG_LINE`, and `_verification_refusal_step()` used
`mutation.maps_os_user` as the step's `run_as`. The pair was required only by
`Mutation.validate_against()`, which `CleanupPlan.for_mutations()` never called,
so an ordinary configuration mutation carrying only `file_path` travelled into
step construction and was refused there as a blank `run_as` — after part of the
plan had been assembled, with a message about a step rather than about the
mutation, and before the restore, reload and verification ordering could be
inspected at all. The data model genuinely permitted an invalid plan state. The
finding is correct as written.

**A second blocker sat behind the first on the same path, and is reported
because fixing the first is what reached it.** `_verification_refusal_step()`
set `refusal_required=True` while leaving `satisfying_statuses` at its default
`(0,)`, and `CleanupStep.__post_init__` refuses that combination outright — a
step that must be refused is satisfied by any non-zero exit and by no zero one.
The refusal proof could therefore never be constructed under any input. R2's
configuration phase was unreachable in two independent ways, and no test
exercised it; both are corrected below.

### EH-R3-3 — Important: handback and traceability describe the wrong tree. **Conceded.**

The handback remained titled pre-execution R1, described schema version 2 and
the removed status-based APIs, and recorded totals from a tree that no longer
exists. The implementation declares `EVIDENCE_SCHEMA_VERSION = 3` and harness
version `0.3.0-pre-execution`. The finding is correct as written. This section is
the correction; the R1 material below is retained as history and its superseded
claims are marked.

## R3.2 The pre-fix result, reproduced before anything was edited

The focused suite was run against the submitted R2 tree, unmodified, before a
single edit:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py
```

**35 failed, 309 passed** — exactly the figure Codex reports. The failures were
ten in `test_bands.py`, nine in `test_plan_and_cleanup.py` and sixteen in
`test_records.py`, and their causes were the stale calls and the cleanup-plan
construction failure the findings name. They are not expected red tests and none
remains.

## R3.3 Files changed, and why each is in scope

| File | Change | Why |
|---|---|---|
| `tools/phase_5_0_evidence/plan.py` | `Mutation.__post_init__` now validates a `POSTGRES_CONFIG_LINE`'s authentication mapping through a new `_validate_authentication_mapping()`; a new `_OS_ACCOUNT_NAME` pattern | EH-R3-2: the incomplete-mapping state is refused where the mutation is declared |
| `tools/phase_5_0_evidence/cleanup.py` | `for_mutations()` validates every declared mutation against the target before building a step; new `_require_complete_mapping()`; `_verification_refusal_step()` takes its identity and role from it and sets `satisfying_statuses=()`; module docstring gains the EH-R3-2 contract | EH-R3-2: the plan is refused at mutation/plan validation, and the refusal proof can be constructed at all |
| `tests/phase_5_0_evidence/test_records.py` | migrated to `CaseRole` and control records; the reference-graph regressions EH-R2-1 required and R2 never wrote | EH-R3-1 |
| `tests/phase_5_0_evidence/test_bands.py` | identity, capability and filesystem cases migrated to declared roles and `control=` records; the band's own role table asserted | EH-R3-1 |
| `tests/phase_5_0_evidence/test_plan_and_cleanup.py` | current `CleanupStep` vocabulary; complete-mapping fixtures; the EH-R3-2 regressions | EH-R3-1, EH-R3-2 |
| `docs/review/phase-5-0-evidence-harness-execution-plan.md` | §2 mapping declarations, §6 cleanup ordering and properties, §8 schema, banner position | EH-R3-2, EH-R3-3 |
| `docs/review/phase-5-0-evidence-harness-implementation-handback.md` | this section | EH-R3-3 |
| `docs/review/Handover information` | the current handover returning control to Codex | the prompt's return step |

**No production application code, migration, database schema, deployment file,
roadmap, project-status, RAID, decision-register or change-log record was
touched.** `tests/web/test_p3_4_static_assets.py` was **not** changed in R3; its
R1 allowlist already covers every harness path, and §R3.6 records the one place
that matters.

## R3.4 The final `CaseRole` and control-record API

A record's relation to the control contract is a **declared, validated,
serialized** fact, and its control's result is read from the control's own
record.

| Role | Names a control | May be referenced as one | Classified beside |
|---|---|---|---|
| `CONTROL` | never | yes, by a dependent case in the same band | its own observations |
| `DEPENDENT` | **always, exactly one** | never | the named control's **record** |
| `STANDALONE` | never | never | its own observations |

`STANDALONE` is inert in the reference graph in both directions, which is what
makes it the safe default and `CONTROL` the role a band chooses deliberately.

`resolve_control_status()` reads the status off the control record and refuses,
in this order: a role that is not a `CaseRole`; a non-dependent case that names a
control; a dependent case that names none; a self-reference; a dependent case
whose control record was not supplied; a record whose `case_id` is not the one
declared; a control from another band — `filesystem` and `identity` both have a
case called `C-1`, so an unscoped id is ambiguous and a control that ran in
another band held different variables fixed; and a referenced record that is not
a `CONTROL`.

`classify()` then applies the standing order: **no observation → `NOT_RUN`;
identity asserted and mismatched → `INCONCLUSIVE`; a control that did not pass →
`INCONCLUSIVE`; an unattributable observation → `INCONCLUSIVE`; observed ≠
expected → `FAILED`; otherwise `PASSED`.** No route into `EvidenceRecord` accepts
a `status`, a `reason` or a control status; `__post_init__` recomputes all three
and refuses a supplied value that disagrees.

The three band case tables declare the role beside the reference and check that
the two say the same thing: `filesystem.ProbeCase` (validated for the whole table
at import), `identity.AccessCase` and `capability.CapabilityCase`.

**No compatibility alias was added.** There is no path that restores a
caller-controlled control status, in the code or in the tests.

## R3.5 Schema version 3, and its compatibility behaviour

`EVIDENCE_SCHEMA_VERSION` is **3** and `HARNESS_VERSION` is
`0.3.0-pre-execution`. Version 3 is the version in which:

- a record declares `case_role`; and
- `positive_control_status` is **gone from the serialized schema** — a dependent
  record stores only `positive_control_case_id`, and the status comes from the
  referenced record.

Compatibility is refusal, not tolerance, in both directions:

- an artifact whose `schema_version` is not 3 is refused rather than compared
  with one this harness produced;
- `_require_exact_keys()` refuses an unknown key and a missing key alike, so a
  stored `positive_control_status` left over from version 2 is an
  `ObservationRefused` and not a field quietly ignored; and
- an unrecognized `case_role` value is refused, because a record outside the
  control graph is not admissible evidence.

`deserialize_records()` resolves the whole reference graph — existence,
uniqueness, self-reference, cycles, then role and band — **before** it constructs
anything, so a cycle is reported as a cycle rather than discovered by recursing
into it, and records are built control-first so file order does not affect what a
reference resolves to.

## R3.6 The corrected configuration cleanup ordering and mapping contract

**The contract.** A `POSTGRES_CONFIG_LINE` mutation carries a **complete,
validated** `(maps_os_user, maps_postgres_role)` pair. That is the first of the
two designs the finding offers, chosen because the proof step *is* the mapping:
it runs as the identity and asks for the role, so the mutation that created the
mapping is the only place that knows it, and a separate declaration would be a
second place for the same fact to be wrong.

**Enforced three times, earliest first, and never defaulted:**

1. `plan.Mutation.__post_init__` → `_validate_authentication_mapping()` refuses a
   configuration mutation with no file, no mapping, half a mapping, a blank half,
   an OS identity that is not a usable account name, or a role that would have to
   be quoted. All are `PlanRefused`, raised where the mutation is declared —
   before a plan exists.
2. `CleanupPlan.for_mutations()` calls `mutation.validate_against(target)` for
   **every** declared mutation before it builds a single step, so a plan is
   refused whole rather than half-assembled.
3. `_require_complete_mapping()` refuses a blank half at the last point before it
   could become a step's `run_as` or `--username`.

**No half is ever defaulted.** There is no fallback identity and no fallback
role, and the refusal messages say so: `foundry`, `postgres`, `freedomcoord`,
`freedomsheet` and every other identity that exists on some host are not
substitutes for a mapping the run did not declare. The pair the execution plan
declares for M-25 and M-26 — `freedomcoord` → `freedom_migration_coordinator` —
is stated explicitly in the plan and in the test fixtures, and is a value the run
would create in the disposable environment, not a default the code supplies.

**The ordering, as generated:**

| Order | Kind | What it does |
|---|---|---|
| CL-01 … | `RESTORE` | one `install` of the byte-exact pre-change capture per configuration file, for every file the run reached |
| then | `RELOAD` | exactly one `SELECT pg_reload_conf()`, after every restore |
| then | `VERIFY` control | an ordinary local connection as `postgres` must **succeed** |
| then | `VERIFY` proof | a connection as the mapped identity asking for the mapped role must be **refused**, one per distinct mapping, while the role still exists |
| then | `REVERSAL` | every other mutation, in the exact reverse of declaration order — including `DROP ROLE` and `DROP DATABASE`, which therefore connect under the restored rules |

`ordering_holds()` checks three claims rather than describing them: every restore
precedes the reload, there is at most one reload and it precedes every
verification, and it precedes every `psql` reversal.

**Completion does not rest on exit status.** `ConfigurationRestoration.problems()`
treats an unrestored file, an unattempted reload, a failed reload, an unmade
post-reload observation, a failed control connection and an unproven mapping each
as an unresolved effective-configuration risk, and every unknown is `None` rather
than `False` because an unmade observation is not a passed one. Any of them makes
`classify_cleanup()` return state **S-B** with exit code 3 and the risk named in
full — the same state as filesystem residue, for the same reason. `configuration`
is a required argument, so a run that mutated `pg_hba.conf` cannot reach S-C by
saying nothing about it.

**Partial setup.** A run that reached only one configuration file gets the whole
phase over that file: the restore that was reached, the one reload, the control
and the applicable proof. There is no path on which a file is restored and not
reloaded, or reloaded with nothing observed after it.

**Still bounded.** Cleanup remains non-recursive — `-r`, `-R`, `-rf`, `-fr`,
`--recursive`, `--no-preserve-root`, `-a` and `*` are refused in any generated or
hand-written step, directories go through `rmdir`, files through `rm --force` on
one named path — re-runnable in its documented sense, and bounded to the
disposable context, with the two PostgreSQL configuration files the only paths
outside the root and `config_path()` the only way to name them.

## R3.7 Requirement-to-code-to-test traceability, R2 and R3

Every R2 and R3 requirement, mapped to named code and named tests. All tests are
in `tests/phase_5_0_evidence/`.

### EH-R2-1 — the control is a derived cross-record fact

| Requirement | Code | Test |
|---|---|---|
| resolve the reference to exactly one record in the same artifact and derive the status from it | `records.resolve_control_status`, `deserialize_records`, `validate_artifact` | `test_records.py::test_a_negative_case_whose_control_did_not_pass_cannot_be_passed`, `…::test_a_passing_control_lets_an_otherwise_matching_dependent_case_pass` |
| never trust a duplicated serialized status | `EvidenceRecord.to_mapping` (the field is absent), `_require_exact_keys` | `…::test_the_serialized_schema_carries_no_duplicated_control_status`, `…::test_a_record_field_this_schema_does_not_know_is_refused_rather_than_ignored` |
| remove `positive_control_status` from the serialized schema | `records.EvidenceRecord` | `…::test_the_serialized_schema_carries_no_duplicated_control_status` |
| an explicit validated contract distinguishing controls, reads and dependent cases | `records.CaseRole`, `filesystem.ProbeCase`, `identity.AccessCase`, `capability.CapabilityCase` | `…::test_a_role_and_a_reference_that_disagree_are_refused_in_either_direction`, `test_bands.py::test_the_case_table_declares_a_role_for_every_case_and_checks_it`, `…::test_an_access_case_whose_role_and_reference_disagree_is_refused`, `…::test_a_capability_case_whose_role_and_reference_disagree_is_refused` |
| reject missing and duplicate ids, self-reference, cycles and inadmissible references | `records._resolve_reference_graph`, `index_by_case_id`, `resolve_control_status` | `test_records.py::test_a_dependent_case_given_no_control_record_is_refused`, `…::test_a_case_that_names_itself_as_its_own_control_is_refused`, `…::test_a_reference_resolved_to_the_wrong_record_is_refused`, `…::test_an_inadmissible_control_reference_is_refused`, `…::test_a_duplicate_case_id_in_one_artifact_is_refused`, `…::test_a_self_referential_or_cyclic_stored_artifact_is_refused`, `…::test_a_stored_reference_to_a_record_the_artifact_lacks_is_refused` |
| a dependent negative case is inconclusive unless its actual control passed | `records.classify` | `…::test_a_negative_case_whose_control_did_not_pass_cannot_be_passed[failed|inconclusive|not_run]`, `test_bands.py::test_a_failing_stage_one_control_makes_every_stage_two_case_inconclusive`, `…::test_an_access_denial_is_not_interpreted_without_its_traverse_control`, `…::test_an_e4_refusal_beside_a_control_that_did_not_clear_the_flag_is_inconclusive`, `…::test_erofs_in_s4_2_without_a_passing_s4_0_attributes_nothing` |
| changing a stored status cannot create a pass | `EvidenceRecord.__post_init__` on the deserialization route | `test_records.py::test_a_stored_artifact_cannot_be_edited_into_a_pass_by_its_control`, `…::test_tampering_with_a_serialized_status_or_reason_is_refused_on_read_back` |
| record order does not affect resolution | `deserialize_records` (control-first construction) | `…::test_record_order_does_not_affect_what_a_reference_resolves_to` |
| cross-band and cross-artifact references fail closed | `resolve_control_status`, `validate_artifact` | `…::test_a_control_from_another_band_is_refused`, `…::test_an_artifact_whose_control_is_absent_from_it_is_refused`, `…::test_an_artifact_whose_control_record_is_not_the_one_it_publishes_is_refused` |
| valid round trips survive | `serialize_records`/`deserialize_records` | `…::test_a_full_round_trip_preserves_every_field`, `…::test_serialization_is_byte_identical_for_the_same_observations` |

### EH-R2-2 and EH-R3-2 — effective configuration, and the mapping it needs

| Requirement | Code | Test |
|---|---|---|
| restore every reached configuration file before one reload | `CleanupPlan.for_mutations` step 1, `ordering_holds` | `test_plan_and_cleanup.py::test_a_complete_mapping_plans_the_whole_configuration_phase_in_order`, `…::test_the_configuration_restore_reinstalls_the_pre_change_capture` |
| the reload precedes the control, each proof, and every step whose safety depends on it | `ordering_holds` | `…::test_a_complete_mapping_plans_the_whole_configuration_phase_in_order` |
| completion depends on observations, not exit status | `ConfigurationRestoration.problems`, `classify_cleanup` | `…::test_cleanup_completion_does_not_rest_on_exit_status_alone` |
| restore, reload, control or proof failure yields S-B and names the risk | `classify_cleanup` | `…::test_any_unfinished_configuration_step_is_s_b_and_names_the_risk` (six cases) |
| partial setup still restores, reloads and verifies | `CleanupPlan.for_mutations` | `…::test_a_partial_setup_that_reached_one_file_still_restores_reloads_and_verifies` |
| a complete mapping is required at mutation/plan validation, with `PlanRefused` | `Mutation._validate_authentication_mapping`, `CleanupPlan.for_mutations` | `…::test_a_configuration_mutation_without_a_complete_mapping_cannot_be_declared` (seven cases), `…::test_a_configuration_mutation_naming_no_file_cannot_be_declared` |
| no blank `run_as`, username or role reaches a `CleanupStep` | `_require_complete_mapping` | `…::test_no_blank_identity_or_role_can_reach_a_cleanup_step` |
| no production identity is defaulted | none — there is no default | the refusal text asserted by the two tests above |
| only a configuration line may carry a mapping | `Mutation.__post_init__` | `…::test_a_mutation_of_another_kind_cannot_carry_an_authentication_mapping` |
| reverse declaration order preserved | `CleanupPlan.for_mutations` step 4 | `…::test_cleanup_runs_in_reverse_declaration_order` |
| cleanup remains non-recursive and bounded | `FORBIDDEN_CLEANUP_TOKENS`, `CleanupStep.__post_init__`, `_REVERSALS`, `contained_path` | `…::test_a_hand_written_recursive_cleanup_step_is_refused` (six vectors), `…::test_a_hand_written_cleanup_step_that_reverses_nothing_is_refused`, `…::test_no_generated_cleanup_step_can_express_a_recursive_removal`, `…::test_cleanup_of_a_path_outside_the_target_is_refused`, `…::test_every_mutation_kind_has_exactly_one_reversal` |
| the two §2.13.2b claims stay separate | `classify_cleanup` | `…::test_the_cleanup_state_machine_separates_its_two_claims`, `…::test_residue_is_reported_by_absolute_path_and_never_cleaned`, `…::test_a_run_that_declared_no_configuration_mutation_has_nothing_to_restore` |

### EH-R3-1 — the tests reach the rules they are named for

| Requirement | Where |
|---|---|
| every record declares `CaseRole` explicitly | every construction in `test_records.py`, `test_bands.py` |
| a dependent case supplies the actual control record | `test_records.dependent()`, `test_bands.seal_denial()`, `test_bands.e6_control()`, `test_bands.passing_probe()` |
| a test of a malformed relationship reaches its intended rule | `test_bands.py::test_a_case_naming_a_control_without_its_identity_is_refused` — role declared, control record supplied, so the refusal is the missing `control_identity_name` and not a second omission |
| a test named for a failed control supplies one | `test_records.failed_control/inconclusive_control/not_run_control`, `test_bands.py::test_an_e4_refusal_beside_a_control_that_did_not_clear_the_flag_is_inconclusive` |
| cleanup tests use the current vocabulary | `test_plan_and_cleanup.py` throughout: `kind`, `run_as`, `mutation_ids`, `satisfying_statuses` |

## R3.8 Test results, exactly as run against this tree

Run serially, with `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`
exported, on 2026-09-05.

| Command | Result |
|---|---|
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | **339 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **393 passed, 1 failed** — see §R3.9; the failure is not the harness |
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3119 passed**, 0 failed, 0 skipped, 1 warning |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2835 passed, 1 failed**, **80 skipped**, 1137 warnings — the same single failure |
| `node --test "foundry-module/tests/"*.test.mjs` | **171 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean, no output |
| `git diff --check` | **one report, in `tests/test_skills.py` — not a file this work touched**; `git diff --check` restricted to the harness, `tests/web` and `docs/review` is clean |

**The web skips are exactly the established 80**, and `-rs` reports both reasons:
54 from `tests/web/test_p3_2_matrix.py:155` and 26 from
`tests/web/test_p3_3_matrix.py:198`, each *"permitted cells are asserted by the
per-route success cases"*. No new skip was introduced.

**Every figure above is from this tree.** The R1 totals — 289, 3117, 2836 — are
**superseded** and are retained below only as history. The bot suite is 3119
rather than 3117 because of the two `Skills` regression tests added by the
concurrent live-bot fix described in §R3.9, not because of this work; the harness
suite is 339 rather than 289 because R3 migrated the existing tests and added the
regressions R2 owed.

**Checks not run, and why.**

- No formatter, linter or type checker is configured in this repository, so none
  was run. This is not a claim that the code would pass one, and no tooling was
  introduced.
- No privileged case was run to increase coverage. Every band remains a function
  over observations that do not exist yet.

## R3.9 The one failing test: a concurrent authorized live-bot fix, undeclared in the scope guard

`tests/web/test_p3_4_static_assets.py::test_no_unrelated_production_files_modified`
**fails**, and the harness is not the cause. The guard reports:

```
Unpermitted models modification detected in working tree: models/skills.py
```

**What the change is.** `models/skills.py` and `tests/test_skills.py` were
modified at 10:46 UTC on 2026-09-05, during this session, by **Gemini**, as an
immediate production defect fix on the **live** Freedom bot. The reported defect:
a character with **Expert Herbalist** could not craft an uncommon healing potion.
The cause is a vocabulary mismatch between two Sheet columns — column X carries
artisan vocabulary (`Expert Herbalist`) while `/craft` and column Y carry tool
vocabulary (`Herbalism Kit`) — and `Skills._clean_tool_name()` reduced each to its
first word, so `Herbalist` and `Herbalism` never matched and the tool level fell
back to `journeyman`. The fix normalises three artisan/tool alias pairs
(`herbalist`/`herbalism` → `Herbalism`, `forger`/`forgery` → `Forgery`,
`thief`/`thieves` → `Thieves`) and adds two regression tests, one of which
reproduces the reported case directly. That is `.agents/AGENTS.md`'s rule for a
bug fix, and the bot's continued reliability is the first item of the approved
product direction.

**It is authorized work, and it is not this submission's.** Neither file was in
the `git status` snapshot this session started from, and the **35 failed / 309
passed** pre-fix run in §R3.2 included this same guard test and it passed then.
Evaluating `scope_violation` over every path in the current working tree confirms
`models/skills.py` is the **only** rejected path and that every evidence-harness
path is accepted.

**I did not touch it, and I did not add it to the allowlist.** Not because its
authority is in doubt — it is a live-bot fix and it is legitimate — but because
that allowlist entry is a **scope declaration**, and the only authorization it
could be filed under here is the Package 5.0 evidence-harness authorization,
which does not cover a `Skills` crafting fix. Declaring it there would attribute
Gemini's change to this remediation and put it inside the artifact Codex is
reviewing as R3. The entry belongs with the `Skills` fix's own record, under
whatever authority that emergency fix carries, and it is one line in
`tests/web/test_p3_4_static_assets.py` when its owner adds it. The R3 prompt also
limits changes to the harness, its tests, the execution plan, this handback and
the handover, and forbids altering product application code.

The worktree is preserved exactly as found; nothing was reset, reverted, staged,
committed or reformatted.

**Consequence, stated plainly.** The prescribed web suite is not green on this
tree, so the harness is not presented as verified against a fully green
repository. The 339-test focused harness suite passes under both documented
interpreters, the bot suite passes at 3119 — two of which are the new `Skills`
regressions — and the web suite passes in every respect except this one guard.
The guard is doing exactly the job it exists to do: it has caught a real,
undeclared production modification. Declaring it is the `Skills` fix's step, not
R3's.

## R3.10 Secrets, privacy, external state and unrelated diff

- **Secrets.** No `.env`, service-account JSON, token, OAuth secret, database URL
  or Foundry credential was read, printed, committed or modified. The harness
  reads no file at all. `TEST_DATABASE_URL` was exported for the suites exactly
  as `.agents/AGENTS.md` documents and names the disposable Unix-socket test
  database.
- **Privacy.** No player data, character state, Discord identifier or Google
  Sheet content appears in any file added or changed. Every fixture is synthetic.
  The authentication mapping recorded in the plan and the fixtures is an identity
  and a role name; no rule text, address, method or credential appears anywhere.
- **External state.** No Discord, Google, Foundry or network call. No production
  database, service, unit, account, group, file or credential was touched. The
  only database contacted was `freedom_test`, by the repository's own suites,
  over a Unix-domain socket.
- **Unrelated diff.** `models/skills.py` and `tests/test_skills.py` are Gemini's
  concurrent authorized live-bot defect fix and were left untouched (§R3.9).
  `docs/review/phase-5-0-evidence-harness-remediation-prompt.md` and
  `…-r3-prompt.md` are the maintainer's. Nothing was reset, reverted, staged,
  committed, pushed or reformatted.

## R3.11 What this delivery does **not** claim

- **No finding is closed.** EH-R3-1, EH-R3-2 and EH-R3-3 are Codex's to close.
  P5.0-R1, P5.0-R4 and P5.0-R5 are untouched; P5.0-R5 remains **Blocking**.
- **No assumption is confirmed.** A-5.0-3, A-5.0-4 and A-5.0-5 remain
  unconfirmed.
- **No check is passed.** C-1, C-3 and C-4 remain **not run**.
- **No readiness consequence.** Package 5.0 remains **`not ready`**. Migration
  `0014`, production schema, production application behavior, deployment,
  authority transition, cutover, the binding OD-62 ruling and Package 5.1+ remain
  unauthorized.
- **The target remains `UNASSIGNED`.** No disposable host, filesystem or
  PostgreSQL instance was named, invented or requested, and Peter was not asked
  to name one.
- **No privileged or mutation-bearing evidence command ran.** No `sudo`, `su`,
  `systemd-run`, `chattr`, `setcap`, `setpriv`, capability-bearing `capsh`,
  `useradd`, `groupadd`, `usermod`, `gpasswd`, `install` outside the workspace,
  `chmod`/`chown` outside the workspace, PostgreSQL DDL/DML, configuration
  reload, service change, network call or destructive cleanup. No account, group,
  file, directory, database object, HBA line, identity-map line or transient unit
  was created. `/etc/sudoers.d` and the PostgreSQL configuration were not read
  through any identity.

## R3.12 Request

**Codex independent pre-execution re-review** of:

1. the EH-R3-1 migration — whether every migrated test now reaches the rule its
   name claims, and whether the reference-graph regressions R2 owed are the right
   set;
2. the EH-R3-2 contract — whether requiring the complete mapping on the
   configuration mutation is the right one of the finding's two designs, and
   whether three enforcement points is the right depth rather than duplication;
3. the second, previously unreachable defect reported in EH-R3-2's concession —
   `refusal_required` with a default `satisfying_statuses` — and whether any
   comparable path remains untested;
4. schema version 3's refusal behaviour, including whether refusing a stored
   version-2 `positive_control_status` key rather than ignoring it is the right
   compatibility posture;
5. the corrected execution-plan §§2, 6 and 8; and
6. **§R3.9** — Gemini's concurrent authorized live-bot fix to `models/skills.py`,
   which fails the repository scope guard because it is not yet declared in the
   allowlist. I have deliberately left both the fix and the allowlist alone, so
   that the declaration is filed under that fix's authority rather than folded
   into this submission. Codex should confirm that is the right disposition.

Work stops here. No target is selected, no execution authority is requested, the
harness is not executed, and no finding is closed.

---

# Superseded — implementation handback, pre-execution R1

**This section describes the R1 tree.** Its API descriptions, its schema-version
claim (`1 → 2`) and its test totals (289 / 3117 / 2836) are **superseded** by the
R3 section above and are retained as review history. The harness now declares
`EVIDENCE_SCHEMA_VERSION = 3` and `HARNESS_VERSION = "0.3.0-pre-execution"`, a
record declares a `CaseRole`, and `positive_control_status` no longer exists.

Date: 2026-09-03

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Outcome: **unprivileged scaffolding complete; no privileged or mutation-bearing
evidence command has been run; no finding, assumption or check is closed**

Authority: the bounded pre-implementation evidence-harness authorization Peter
Duscha approved on 2026-09-02, continued by
`docs/review/phase-5-0-evidence-harness-remediation-prompt.md`.

Baseline: commit `212b72d`, the closed Phase 4 baseline.

---

## 1. The four findings, conceded before their corrections

### EH-R1 — Blocking: caller-controlled evidence status. **Conceded.**

`EvidenceRecord` accepted a caller-supplied `status` and `reason` and its
constructor compared them with nothing. A caller could therefore serialize
`status="passed"` for observations the classifier evaluates as failed or
inconclusive, and the only check present — that a `PASSED` record had *some*
observation — did not compare that observation with the expectation. Evidence used
at a security or operational gate could contradict its own observations. The
finding is correct as written.

**Correction.** The classification result is now authoritative on every route into
the class.

- `EvidenceRecord.for_case()` **derives** `status` and `reason` from the expected
  outcome, the observation, the identity assertion and the positive control. It
  does not accept them. Every band uses it and nothing else.
- Direct dataclass construction remains possible — `from_mapping()` needs it — and
  `__post_init__` **recomputes** the classification and refuses any supplied
  `status` or `reason` that disagrees. There is no unchecked path and no
  test-only path: the check is in the constructor, so both routes pass through it.
- `deserialize_records()` reads an artifact back **through that constructor**,
  which is what makes reading a stored artifact a check rather than a parse.
- A related hole is closed alongside: a record naming a positive control without
  its status, or carrying a control status with no case id, is refused. A control
  that cannot be identified cannot be re-checked by a reviewer, and a named
  control that did not run is `NOT_RUN`, which classifies as `INCONCLUSIVE`.

One input to `classify()` beyond the observations was added and is stated here
because it is the only one: `attribution_refusal`. It carries §2.13.2a's
attribution table — an `EACCES` where Stage 1 has already proved discretionary
access permits the operation says the *target* is mis-provisioned, and the
section's answer is `inconclusive`, not `failed`. It is computed by the band from
the observation rather than chosen by a caller, and **it can only ever move a
result away from `PASSED`**; `test_an_attribution_refusal_can_only_move_a_result_
away_from_passed` asserts that no value of it produces a pass.

### EH-R2 — Blocking: contradictory outcomes are representable. **Conceded.**

`Outcome` documented that exactly one of `errno_name`, `exit_status` and `value`
was meaningful and validated only that a success carried no errno. A failed result
could carry `EPERM`, exit status `0` and a value simultaneously; the fields the
comparison ignored survived into the artifact; and deserialization applied no
rule at all. The finding is correct as written.

**Correction.** `Outcome` now carries an `OperationKind`, and the grammar is
closed:

| Kind | Success | Refusal |
|---|---|---|
| `SYSCALL` | the call returned; no errno, no exit status, no value | `errno_name`, a symbolic name this platform knows |
| `COMMAND` | `exit_status == 0` | a non-zero `exit_status` |
| `OBSERVATION` | `value` — the mask, mount property, mode or digest that was read | *not representable*; a read that failed is a `SYSCALL` refusal |

Four factories name the four admissible shapes — `returned()`, `refused()`,
`exited()`, `read()` — and the constructor enforces the same grammar, so a direct
construction that contradicts itself is refused rather than accepted and
documented against.

Rejected, each with a table-driven regression:

- more than one result representation (two, and three);
- an errno paired with success;
- exit status zero represented as a refusal;
- a non-zero exit status represented as success, unless a documented case supplies
  a non-blank `nonzero_success_rationale` — no currently authorized band does, and
  the rationale is refused on any other kind so it cannot silently excuse
  something else;
- a blank, lower-case, non-symbolic or platform-unknown errno name;
- a syscall refusal carrying no errno at all — *"an outcome with no usable result
  representation"*, and a refusal whose cause is unrecorded attributes nothing;
- a command with no exit status, an observation with no value, and an observation
  that did not succeed.

**Nothing is silently discarded.** `Outcome.from_mapping()` and
`EvidenceRecord.from_mapping()` refuse an unknown key and a missing key alike, and
an artifact whose `schema_version` is not this harness's is refused rather than
compared. A kind mismatch between expectation and observation is a `FAILED` case
with a reason naming both kinds — which is what makes `P-9`'s `ENOTTY` a failed
probe rather than a comparison the classifier tries to make.

`EVIDENCE_SCHEMA_VERSION` is bumped `1 → 2`, because the record's field set
changed. **Superseded:** the current schema version is **3**, and version 3 also
removes `positive_control_status` and adds `case_role` (§R3.5).

### EH-R3 — Important: repository scope guard is red. **Conceded.**

`tests/web/test_p3_4_static_assets.py::test_no_unrelated_production_files_modified`
was correctly reporting `tools/phase_5_0_evidence/` as an undeclared
production-path modification, and the prescribed web suite was failing because of
it.

**Correction.** A **separately named** allowlist,
`PERMITTED_PHASE_5_0_EVIDENCE_HARNESS`, declares the fourteen harness paths in
both the forms git emits — the collapsed untracked-directory entry and the
individual files for when the directory is tracked.

- `WATCHED_PRODUCTION_PREFIXES` is **unchanged**: `tools/` stays watched in full.
- No prefix was added to `UNPOLICED_WITHIN_WATCHED`.
- It is **not** folded into `PERMITTED_PHASE_4_PRODUCTION`: two authorizations,
  two lists, asserted disjoint by
  `test_the_evidence_harness_allowlist_is_separate_from_the_phase_4_one`.
- Seven synthetic paths that are not in this tree prove the guard still refuses an
  unrelated `tools/` path — including an **undeclared module inside the declared
  package** (`tools/phase_5_0_evidence/executor.py`,
  `…/subprocess_runner.py`). An executing runner added to this harness would have
  to be declared here before the suite went green, which is why the allowlist is a
  file list and not a directory.

### EH-R4 — Important: the authorized handback is incomplete. **Conceded.**

Only the record/error foundation existed. Every unprivileged deliverable of the
original implementation prompt is now present; §3 maps each to code and tests.

---

## 2. Files created and changed, and why each is in scope

### Created — `tools/phase_5_0_evidence/`

| File | Why it is in scope |
|---|---|
| `targets.py` | the disposable-target validation and forbidden path/database guards the prompt requires |
| `plan.py` | argument-vector command planning, mutation declaration, and the dry-run-only runner |
| `cleanup.py` | bounded, reverse-order, re-runnable cleanup derived from declared mutations, and §2.13.2b's S-A/S-B/S-C state machine |
| `sudoers.py` | **C-1**: analysis of drop-in content an authorized reader supplies |
| `hba.py` | pre-change and post-change `pg_hba.conf` / `pg_ident.conf` ordering and breadth analysis |
| `identity.py` | **C-4** / `JNL-52`: §2.12.2's canonical membership table and the access matrix |
| `capability.py` | `JNL-49` / `JNL-50`: `E1 … E8`, the `capsh` construction, the declared masks and the two control forms |
| `filesystem.py` | **C-3** / §2.13.2a: the four probe stages and the attribution table |
| `manifest.py` | `JNL-46`: the two manifest functions and the closed two-region partition |
| `provenance.py` | `JNL-51` / `JNL-53`: the four provenance facts, and the missing-provenance refusal |
| `journal.py` | P5.0-R5: generation lifecycle, five refusal conditions, and the named operator recovery |

### Changed — `tools/phase_5_0_evidence/`

| File | Change |
|---|---|
| `records.py` | rewritten for EH-R1 and EH-R2; adds `OperationKind`, the four factories, `for_case()`, `from_mapping()`/`deserialize_records()` and the constructor-level classification check |
| `__init__.py` | schema version `1 → 2`, harness version `0.1.0 → 0.2.0-pre-execution`, and a module table — **superseded: now 3 and `0.3.0-pre-execution`** |
| `errors.py` | unchanged |

### Created — `tests/phase_5_0_evidence/`

`test_records.py`, `test_targets.py`, `test_plan_and_cleanup.py`,
`test_analysis.py`, `test_bands.py`, `test_no_execution.py`. **289 tests —
superseded; the current figure is 339 (§R3.8).** None
needs root, a database, a network, systemd or any host state; asserted by
`test_no_execution.py::test_no_test_in_this_suite_needs_root_or_a_database`, which
reads every other file in the suite.

### Created — `docs/review/`

| File | Why |
|---|---|
| `phase-5-0-evidence-harness-execution-plan.md` | the required exact command and cleanup artifact, banner **NOT EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED**, target **`UNASSIGNED`** |
| `phase-5-0-evidence-harness-implementation-handback.md` | this document |

### Changed — outside the harness

| File | Change | Why it is in scope |
|---|---|---|
| `tests/web/test_p3_4_static_assets.py` | one new allowlist, one branch in `scope_violation`, and four new tests (three parametrised) | EH-R3. It is the only production-adjacent file touched, and the change is additive: no existing entry, prefix or assertion was removed or weakened |

**No controlled record was edited.** `docs/implementation-plan.md`,
`docs/project-management/status.md`, `change-log.md`, `raid-register.md`,
`decision-register.md` and `docs/discovery/open-decisions.md` are untouched.

---

## 3. Requirement-to-code-to-test traceability

| Original prompt requirement | Code | Test |
|---|---|---|
| C-1 `sudoers` metadata/content capture and validation | `sudoers.analyse_sudoers_drop_in`, `summarize_c1` | `test_analysis.py::test_the_specified_drop_in_is_safe`, `…nopasswd…`, `…wildcard…`, `…missing_required_default…`, `…wrongly_owned_or_moded…`, `…c1_finds_an_unrelated_drop_in…` |
| pre-/post-change HBA and identity-map ordering analysis | `hba.analyse_hba`, `analyse_ident`, `parse_hba`, `parse_ident` | `test_analysis.py::test_the_specified_ordering_holds…`, `…broad_rule_above…`, `…broad_rule_below…`, `…absent_peer_line…`, `…missing_reject_line…`, `…include_directive…`, `…unclassifiable_line…`, `…identity_map_must_be_one_literal_line` |
| OD-64 peer-authentication positive/negative identity matrix | execution plan §5.5 B6-08/B6-09, classified by `hba` + `records` | `test_analysis.py` ordering tests; the connection attempts themselves are unrun |
| C-3 `FS_APPEND_FL` positive control and `O_TRUNC` refusal attribution | `filesystem.STAGE_1`, `STAGE_2`, `attribute_observation`, `attribution_refusal_for`, `classify_probe_case` | `test_bands.py::test_a_failing_stage_one_control…`, `…eaccess_in_stage_two_is_inconclusive…`, `…enotty_from_getflags…`, `…case_that_names_a_control_refuses_when_its_status_is_not_supplied` — **superseded test name; it is now `…_refuses_when_its_record_is_not_supplied`, and §R3.7 has the current mapping** |
| C-4 / `JNL-52` identity, group and filesystem-access checks | `identity.CANONICAL_ACCOUNTS`, `CANONICAL_GROUPS`, `classify_group_membership`, `classify_account_identity`, `classify_access`, `membership_matrix_holds` | `test_bands.py::test_the_canonical_membership_is_matched_as_a_set…`, `…complete_supplementary_list_means_exhaustive`, `…access_denial_is_not_interpreted_without_its_traverse_control`, `…membership_matrix_gates_the_access_cases` |
| `JNL-49`/`JNL-50` capability masks, securebits, positive controls, exact `errno` | `capability.EvidenceIdentity`, `expected_masks`, `capsh_argv`, `declared_identity`, `control_form_for`, `classify_capability_case`, `classify_launcher_bounding_set`, `classify_root_masks` | `test_bands.py::test_every_declared_mask_is_reproduced_by_the_derivation`, `…e7s_masks_are_read…`, `…e8_carries_freedomjournal…`, `…e1_and_e2_differ_in_exactly_one_capability…`, `…e4_and_e6_differ_in_exactly_cap_fowner`, `…two_control_forms…`, `…capsh_invocation_never_asks_to_add_to_a_bounding_set`, `…short_launcher_bounding_set…`, `…identity_assertion_fails_is_inconclusive`, `…isolating_control_for_an_e4_refusal_is_e6_and_not_e2` |
| `JNL-46` manifest-function equivalence | `manifest.source_manifest_digest`, `deployment_manifest_digest`, `classify_manifest_equivalence`, `classify_partition` | `test_bands.py::test_the_source_manifest_digest_is_order_independent…`, `…two_manifest_functions_are_different_functions`, `…duplicate_deployed_name…`, `…entry_class_git_cannot_express…`, `…equivalence_names_which_comparison_disagreed`, `…unaccounted_file_is_refused…` |
| `JNL-51` reviewed-source provenance, **especially missing-provenance refusal** | `provenance.classify_missing_provenance`, `classify_provenance_agreement`, `classify_worktree_isolation` | `test_bands.py::test_the_missing_provenance_case_refuses_and_creates_nothing`, `…present_provenance_record_makes_the_omission_case_fail`, `…generation_artifact_surviving_the_refusal_fails_the_case`, `…deploy_path_reads_no_file_in_the_group_writable_worktree` |
| `JNL-53` W11a deployed-source/provenance self-check | `provenance.classify_provenance_agreement` (`JNL-53-J27-sm-recomputed`) | `test_bands.py::test_the_four_way_provenance_comparison_names_the_source_that_disagreed`, `…apr_that_is_not_root_owned_read_only…` |
| journal creation, sealing, missing/corrupt/reset/stale/cross-generation refusal and recovery for P5.0-R5 | `journal.diagnose`, `classify_generation_state`, `RECOVERY_PROCEDURE`, `classify_recovery`, `p5_0_r5_evidence_complete` | `test_bands.py::test_each_condition_is_diagnosed_as_itself`, `…each_condition_produces_its_own_named_refusal`, `…case_that_refuses_for_the_wrong_reason_fails`, `…emptied_journal_cannot_look_like_a_fresh_one`, `…recovery_procedure…`, `…coverage_is_reported_as_coverage_and_not_as_a_closure` |
| deterministic cleanup/residue reporting | `cleanup.CleanupPlan`, `classify_cleanup`, `CleanupOutcome` | `test_plan_and_cleanup.py::test_every_mutation_kind_has_exactly_one_reversal`, `…reverse_declaration_order`, `…no_cleanup_step_is_destructive_when_its_object_is_absent`, `…no_generated_cleanup_step_can_express_a_recursive_removal`, `…hand_written_recursive_cleanup_step_is_refused`, `…cleanup_of_a_path_outside_the_target…`, `…configuration_restore_reinstalls_the_pre_change_capture`, `…cleanup_state_machine_separates_its_two_claims`, `…residue_is_reported_by_absolute_path_and_never_cleaned` |
| explicit disposable-target validation and every forbidden path/database guard | `targets` | `test_targets.py`, 21 refused synthetic roots plus the database, account, containment and configuration-path guards |
| argument-vector command and mutation planning | `plan.validate_argv`, `Mutation`, `CommandStep`, `ExecutionPlan` | `test_plan_and_cleanup.py`, 16 refused synthetic vectors plus the declaration and target rules |
| the dry-run-only runner | `plan.DryRunRunner`, `PlannedInvocation` | `…only_runner_records_intent_and_executes_nothing`, `…runner_has_no_execute_method_of_any_kind`, `test_no_execution.py::test_the_only_runner_the_package_defines_is_the_dry_run_one` |
| no module executes, imports `subprocess`/sockets/HTTP/a database driver | every module | `test_no_execution.py`, six checks × fourteen modules |

---

## 4. Safety invariants, and how each is enforced rather than intended

| Invariant | Enforcement |
|---|---|
| No module may execute a command | `test_no_execution.py` parses every module and refuses `subprocess`, `asyncio`, `multiprocessing`, `pty`, `signal`, `select`, `shlex`, `ctypes`, `importlib`, plus `system`, `popen`, `exec*`, `spawn*`, `fork*`, `posix_spawn*`, `eval`, `exec`, `compile`, `__import__`, `run`, `check_output`, `check_call`, `call`, `Popen` |
| No module may import or reach a socket, HTTP, or a database driver | the same scan refuses `socket`, `ssl`, `http`, `urllib`, `requests`, `telnetlib`, `webbrowser`, `psycopg`, `psycopg2`, `sqlalchemy`, and a text scan refuses `https?://`, `postgresql://`, `postgresql+`, `connect(` |
| No module reads or writes a file | the same scan refuses `open()`, `read_text`, `read_bytes`, `write_text`, `write_bytes`. **This is what makes C-1 safe to leave with an authorized human**: the harness cannot read `/etc/sudoers.d` even if a future edit wanted it to |
| Explicit absolute targets; `/`, the repository root, `/var/lib`, ancestors, production databases, unresolved variables, globs and metacharacter construction refused | `targets.validate_mutation_root`, `validate_database_name`, `validate_absolute_path`, `validate_postgres_config_directory`; `plan.validate_argv` |
| Records contain no command output, file content, environment, credentials, tokens, keys, player data or unrelated configuration | `EvidenceRecord.detail` is scalars only, validated on construction; `Outcome` carries an errno name, an exit status or one bounded read value; C-1 and HBA findings carry codes, indices, classes and digests — asserted by `test_no_c1_finding_reproduces_a_rule_from_the_file` and `test_no_evidence_finding_carries_an_address_or_an_option_string` |
| A failed positive control, identity mismatch, unexpected mask, securebit, UID/GID/group set, errno or mount property is failed or inconclusive — never passed | `records.classify` checks identity, then control, then attribution, then the result; `capability.control_form_for` refuses a non-isolating control outright |
| Cleanup cannot express recursive deletion of a broad or unresolved path | `cleanup._REVERSALS` is the only generator, `FORBIDDEN_CLEANUP_TOKENS` is checked on every generated argv, directories go through `rmdir`, and every path passes `contained_path()` |
| No network call, PostgreSQL connection, systemd call, external-service call, privileged command or host mutation in tests | the whole suite is pure functions over supplied values; no fixture, no marker, no environment variable |

---

## 5. The execution plan, and the target

`docs/review/phase-5-0-evidence-harness-execution-plan.md` carries the exact
proposed commands as argument vectors, grouped by identity and evidence case, with
before-state capture, expected safe result, expected refusal, stop result, the
twenty-seven objects the run would create, the reverse-order cleanup, the evidence
artifact each band produces, and the authorization mapping.

**The target is `UNASSIGNED`.** Peter has named no disposable host, filesystem or
PostgreSQL instance, so the harness carries `DisposableTarget.unassigned()` and
every mutation-bearing use refuses. No target was invented.

Every target-derived path in the plan is written as `<TARGET_ROOT>`,
`<EVIDENCE_DB>` or `<PG_CONFIG_DIR>`. That form is not merely a reading
convention: `plan.validate_argv` **refuses** any argument containing `<` or `>`,
so the document's vectors cannot be lifted and run. They must be regenerated by
the harness against a named target, and that regeneration is what re-applies every
guard. `test_the_execution_plan_documents_placeholder_tokens_cannot_be_run` pins
it.

The plan's banner, first line and last line, is **NOT EXECUTED — CODEX
PRE-EXECUTION REVIEW REQUIRED**.

---

## 6. Test results, exactly as run

**Superseded in full. These are R1 figures against a tree that no longer
exists; §R3.8 has the current ones.** They are retained because the R1 handback
cited them and a reader comparing revisions needs to see which numbers moved.

Run serially, in this order, against the tree being submitted, with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported.

| Command | Result |
|---|---|
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | **289 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3117 passed**, 0 failed, **0 skipped**, 1 warning |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2836 passed**, 0 failed, **80 skipped**, 1137 warnings |
| `node --test "foundry-module/tests/"*.test.mjs` | **171 passed**, 0 failed, 0 skipped |
| `/opt/discord-bots/venv/bin/python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean, no output |
| `git diff --check` | clean, no output |

**The web skips are exactly the established 80**, and `-rs` reports both reasons:
54 from `tests/web/test_p3_2_matrix.py:155` and 26 from
`tests/web/test_p3_3_matrix.py:198`, each *"permitted cells are asserted by the
per-route success cases"*. No new skip was introduced.

**A run that did not count, reported because it happened.** I first started the
bot suite in the background while the web suite was running. AGENTS.md is explicit
that the two share one disposable database (finding F-6) and must run serially,
and the concurrent run produced 4 failures and 12 errors in the bot suite and 1
failure in the web suite, all `UndefinedTable: relation "audit_events" does not
exist` — the other suite's `alembic downgrade base`. Both were re-run serially and
are the figures in the table above. No result from the concurrent run is cited
anywhere.

**Checks not run, and why.**

- No formatter, linter or type checker is configured in this repository, so none
  was run. This is not a claim that the code would pass one.
- No privileged case was run to increase coverage. Every band is exercised over
  supplied observations, and **not one observation in this handback came from a
  privileged command**.
- The `-p no:randomly` flag appears in no reported run; the figures above are from
  plain invocations.

---

## 7. Secrets, privacy, external state and unrelated diff

- **Secrets.** No `.env`, service-account JSON, token, OAuth secret, database URL
  or Foundry credential was read, printed, committed or modified. The harness
  reads no file at all. `TEST_DATABASE_URL` was exported for the suites exactly as
  AGENTS.md documents and names the disposable Unix-socket test database.
- **Privacy.** No player data, character state, Discord identifier or Google Sheet
  content appears in any file added or changed. Every fixture is synthetic.
- **External state.** No Discord, Google, Foundry or network call. No production
  database, service, unit, account, group, file or credential was touched. The
  only database contacted was `freedom_test`, by the repository's own suites, over
  a Unix-domain socket.
- **Unrelated diff** (**superseded**; §R3.10 describes the current worktree).
  `git status` shows `docs/review/Handover information`
  modified and `docs/review/phase-5-0-evidence-harness-remediation-prompt.md`
  untracked. Both are the maintainer's, both predate this work, and neither was
  touched. Nothing was reset, reverted, staged, committed, pushed or reformatted.
  `git diff --stat` for tracked files is two files: the maintainer's handover note
  and `tests/web/test_p3_4_static_assets.py`.

---

## 8. Discrepancies found, reported rather than corrected

Four in the operational runbook. None was edited: the runbook is a controlled
document and the remediation prompt forbids changing controlled records.

1. **`docs/review/phase-5-0-gemini-operational-evidence-runbook.md` lines 88 and
   123 name a `sudoers` drop-in `freedom-coord-run`.** No such file exists in the
   package plan. §2.12.5 and §2.12.4 name
   `/etc/sudoers.d/freedom-migration-coordinator` and
   `/etc/sudoers.d/freedom-journal-admin`, and `freedom-coord-run` appears nowhere
   else in the repository. A C-1 inspection following the runbook would `cat` a
   path that does not exist, print `NOT FOUND`, and leave the real drop-in unread.
2. **Line 422: *"Total: 96 case records (12 × 8)"* for `JNL-49`/`JNL-50`.** The
   package plan gives twelve cases each — twenty-four in total — and **each case
   names one identity**; they are not run once per identity. The multiplication
   would inflate the evidence count fourfold.
3. **The runbook's C-3-E-1 procedure is not §2.13.2a's probe.** Step C3-1 creates
   the target with `touch` as root inside `…/probe`, so the file is
   `root:root`, and step C3-2 then attempts `O_TRUNC` as `freedomsheet`. That is
   the revision-5 defect §2.13.2a exists to correct: *"every negative case would
   have failed on discretionary permissions whether or not `FS_APPEND_FL` did
   anything."* §2.13.2a requires the probe file to be
   `freedomsheet:freedomsheet 0600` and requires Stage 1's six controls to pass
   first. The runbook's version has no Stage 1, no Stage 3, no Stage 4 and one of
   Stage 2's nine cases.
4. **C-4-D-1 step 4 uses `id freedomcoord | grep -c freedomsheet`.** A substring
   count cannot establish the set equality §2.12.2 requires — it would match a
   group whose name merely contains the string, and it cannot detect an
   *unexpected third* group at all. The harness compares as a set
   (`identity.classify_account_identity`).

The execution plan follows the package plan and the logical schema where they and
the runbook disagree, and says so.

---

## 9. What this delivery does **not** claim

- **No finding is closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are untouched; P5.0-R5
  remains **Blocking**. `journal.p5_0_r5_evidence_complete()` reports *coverage*
  and says in its own return value that coverage is not a closure recommendation.
- **No assumption is confirmed.** A-5.0-3, A-5.0-4 and A-5.0-5 remain
  unconfirmed.
- **No check is passed.** C-1, C-3 and C-4 remain not run. Every classifier in
  this package is a function over observations that **do not exist yet**.
- **No readiness consequence.** Package 5.0 remains **`not ready`**. Migration
  `0014`, production schema, production application behavior, deployment,
  authority transition, cutover, the binding OD-62 ruling and Package 5.1+ remain
  unauthorized, and nothing here implements or approaches any of them.
- **No privileged or mutation-bearing evidence command ran.** No `sudo`, `su`,
  `systemd-run`, `chattr`, `setcap`, `setpriv`, capability-bearing `capsh`,
  `useradd`, `groupadd`, `usermod`, `gpasswd`, `install` outside the workspace,
  `chmod`/`chown` outside the workspace, PostgreSQL DDL/DML, configuration reload,
  service change, network call or destructive cleanup. No account, group, file,
  directory, database object, HBA line, identity-map line or transient unit was
  created. `/etc/sudoers.d` and the PostgreSQL configuration were not read through
  any identity.

---

## 10. Request

**Superseded by §R3.12.** The R1 request read:

**Codex independent pre-execution re-review** of:

1. the EH-R1 correction — that the classifier is authoritative on every route into
   `EvidenceRecord`, including deserialization, and that `attribution_refusal` is
   a safe one-directional input;
2. the EH-R2 grammar — that the closed outcome table is the right closure for the
   authorized bands, and that the `nonzero_success_rationale` escape hatch is
   acceptable given that no band uses it;
3. the EH-R3 allowlist — that fourteen declared paths in a separately named list
   is the right narrowness, and that the falsification set is adequate;
4. the completeness of the bands against §§2.10–2.13, the logical schema and the
   evidence contract, and in particular whether any evidence case the authorized
   bands require has no classifier here;
5. the four runbook discrepancies in §8, and whether any of them changes the
   evidence contract rather than only the runbook; and
6. **the execution plan itself** — every argument vector, every declared mutation,
   the cleanup order, and the stop conditions — noting that the target is
   `UNASSIGNED` and that Peter must name and confirm one, and authorize the two
   privileged production-host reads, before any of it can be regenerated let alone
   run.

Work stops here.
