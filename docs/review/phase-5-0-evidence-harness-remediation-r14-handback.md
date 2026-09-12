# R14 remediation handback — ownership baseline correction, 2026-09-09

Submitted for **independent Codex review**. Nothing here is closed, nothing is
approved, and this grants no execution authority. `EH-R13-1` and `EH-R14-1`
remain the reviewer's to dispose of. Package 5.0 remains `not ready`, `P5.0-R5`
remains **Blocking** and `OD-62` remains **Open**.

Reviewed manifest of the tree submitted here, for identification only:

```text
79ed6ed615b3a2eeb74e5b07d51f76bac0e4b0d4451f636436cf1aec523e7324
```

The R13.2 digest `8875b165b32f5a0929770380571c15ae4a102cd80f4ebb8979a17c7698690cb4`
is **superseded** and must never be passed to `--execute`. Neither may this one:
the plan is not executable, and `--execute` refuses it three times over.

## R14.1 The conceded defect

**EH-R14-1 is conceded in full, and the audit it asked for found the same defect
twice more.** R13 proved an object absent with a **failure** wherever its tool
had one. Three of the six ownership baselines did that, and not one of the three
statuses means *absent*.

| Baseline | R13's proof of absence | What that status actually reports |
|---|---|---|
| `R-B-DB` | `psql` exit 2, connecting to the evidence database | a **connection** failure. `pg_database.datallowconn = false` produces it for a database that plainly exists |
| `R-B-ROLE` | `psql` exit 3 from `SET ROLE` | **any** statement error under `ON_ERROR_STOP=1` — a permission refusal, a catalog failure, a rejection by a different server version |
| `R-B-ROOT` | `stat` exit 1 | every failure coreutils' `stat` has. ENOENT, ENOTDIR, ELOOP, ENAMETOOLONG, EACCES and EIO are one number |

`R-B-PG` did not cover any of them. It connects to the `postgres` database, and
a successful connection to one database says nothing about whether another
exists — which is exactly the reviewer's `datallowconn` case.

The consequence in each case was the same, and it is the reason the finding is
Blocking: the baseline was satisfied, ownership was established, the creation
then failed because the object was already there, and the derived cleanup was
entitled to remove it.

## R14.2 Exact pre-fix evidence

Produced from the **R13.2 tree**, through the injected fakes in
`tests/phase_5_0_evidence/test_r13_remediation.py`, before any file was changed.
It reproduces the reviewer's case and extends it to the two baselines the review
asked to have audited. No host, socket, database or process was involved.

For each row: seed the object, make its baseline return the status R13 treated
as absence, and make the creation return 3.

```text
--- EH-R14-1 database, connection probe exit 2 while the database exists
creation B6-03 stopped_at B6-03
baseline_satisfied True
object_survives False
removal_requested ['CL-08: /usr/bin/psql … --command DROP DATABASE IF EXISTS fb_evidence_p5_0']

--- EH-R14-2 role, SET ROLE exit 3 while the role exists
creation B6-04 stopped_at B6-04
baseline_satisfied True
object_survives False
removal_requested ['CL-07: /usr/bin/psql … --command DROP ROLE IF EXISTS freedom_migration_coordinator']

--- EH-R14-3 filesystem, stat exit 1 while the root exists
creation B3-01 stopped_at B3-01
baseline_satisfied True
object_survives False
removal_requested ['CL-37: /usr/bin/rmdir -- /var/lib/fb-evidence-p5-0']
```

`object_survives False` is the finding: in all three the pre-existing object was
gone from the fake host's object set at the end of the run. The first row
reproduces the review's output exactly, `B6-03` and `CL-08` included.

The reproduction is preserved as executable assertions rather than as a
transcript. `tests/phase_5_0_evidence/test_r14_remediation.py`'s first three
tests are the same three host states, asserting the properties that now hold
instead; each carries the pre-fix output in its docstring.

## R14.3 What changed, and why the three corrections differ

### The two PostgreSQL baselines: a listing the server returns

Absence is now proved by a **successful** catalog reading, not by a failure.
Both baselines run against the `postgres` database — never against the object
they are asking about, because connectability is not observability:

```text
R-B-DB   psql … --tuples-only --no-align --dbname postgres --command SELECT datname FROM pg_database
R-B-ROLE psql … --tuples-only --no-align --dbname postgres --command SELECT rolname FROM pg_roles
```

The reviewed grammar admits no string literal — `'`, `*`, `>` and `<` are
refused as argument characters, deliberately — so the listing cannot be filtered
and the query names nothing. The two names it is asked about therefore travel
beside the vector, in a new `CommandStep.catalog_question`, which the review
manifest pins:

| Baseline | Subject, which must be absent | Control, which must be present |
|---|---|---|
| `R-B-DB` | `fb_evidence_p5_0` | `postgres` |
| `R-B-ROLE` | `freedom_migration_coordinator` | `postgres` |

`R-B-PG` establishes the control as a fact rather than an assumption: it
connects *as* `postgres` *to* `postgres`, so both names exist when it succeeds.

A new capture policy, `catalog_membership`, turns one listing into exactly two
yes/no answers and records nothing else. That is not an efficiency: the listing
is other people's database and role names, which this harness has no business
putting in an artifact, and the predefined `pg_*` roles alone are three times
`MAX_VALUE_LENGTH`. The subject and control are names a reviewer already
approved; every other name in the listing leaves no trace.

**Three states, and only one grants ownership.**

| State | Observation | Effect |
|---|---|---|
| absent | `control_present=yes`, `subject_present=no`, exit 0 | ownership established |
| present | `subject_present=yes` | run stops at the baseline, nothing created, nothing removed |
| unknown | non-zero exit, no control in the listing, a line that is not a catalog name, or no declared question | run stops, **no ownership**, nothing removed |

Unknown is the state R13 had no representation for, and it is why *"the catalog
was unreachable"* can no longer read as *"the object is not there"*.

### The filesystem baseline: blocked, not approximated

`stat` cannot express the equivalent, and neither can anything else this plan is
permitted to run:

* `stat`, `lsattr` and `getcap` report absence only as a generic failure;
* `namei` reports each path component, but *which* failure a component had is in
  its message text — locale- and version-dependent host prose, which R14
  forbids parsing; and
* no permitted creation reports pre-existence uniquely the way `groupadd` and
  `useradd` report exit 9. `install -d` succeeds on a directory that is already
  there, and `install` overwrites a file that is.

The two ways out — admitting another executable, or reading unrestricted error
text — are the grammar changes the finding rules out. So the baseline is
**declared unresolved as conflict C-8** rather than approximated:

* `R-B-ROOT` remains, as a **precondition only**. Exit 0 soundly means something
  is there and rightly stops the run; exit 1 now establishes nothing;
* the 29 path mutations under the root are owned by nothing. The executor's
  ownership gate refuses the first `install` **before the command exists**, so
  the plan creates no file;
* their reversals remain in the cleanup plan and can never become applicable,
  because a mutation that cannot be created cannot be reached; and
* `UnresolvedStep` gained `blocks_mutation_ids`, so *which* objects a blocked
  baseline leaves unowned is machine-checkable and manifest-pinned rather than a
  claim in prose.

This harness now leaves filesystem residue to §2.13.2b's operator recovery
rather than removing a directory it could not prove it made.

## R14.4 Baseline-by-baseline proof obligations

The complete audit. `test_r14_remediation.py` asserts this table over the
generated plan, so a new baseline taking a generic failure as absence fails the
suite rather than a review.

| Baseline | Steps | Proof of absence | Unique? |
|---|---|---|---|
| `getent group` / `getent passwd` | 7 | exit 2 | **yes, kept.** `getent(1)` documents 2 as *one or more supplied key could not be found in the database*, distinct from 1 for a missing argument or unknown database and 3 for an unsupported enumeration |
| `R-B-ROOT` (`stat`) | 1 | — | **no, blocked.** C-8; establishes nothing |
| `R-B-DB` (`psql`) | 1 | exit 0 plus a compared listing | **yes, replaced.** A successful reading, with a control that separates absent from unknown |
| `R-B-ROLE` (`psql`) | 1 | exit 0 plus a compared listing | **yes, replaced.** Same |
| `R-B-UNIT` (`systemctl show`) | 1 | exit 0 and `LoadState=not-found` | **yes, kept.** A successful command whose compared answer names the state |

Ownership coverage moves from 10 baselines over **41** mutations to 10 baselines
over **12**, with **29** blocked. The two `postgres_config_line` mutations are in
neither set, unchanged: their reversal is a restore of a byte-exact pre-change
capture, not a removal.

A structural guard was added at plan-build time as well: a baseline that reads a
catalog may establish ownership **only of its own subject**. Proving one name
absent and claiming another is the same substitution one level up, and it is now
a `PlanRefused`.

## R14.5 Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/capture.py` | new `CatalogQuestion`; new `CATALOG_MEMBERSHIP` policy, its reader, its two keys and its refusal marker; `sanitize` takes the question and refuses one handed to any other policy |
| `tools/phase_5_0_evidence/plan.py` | `CommandStep.catalog_question`, required for that policy, refused for every other, and restricted to owning its own subject |
| `tools/phase_5_0_evidence/concrete_plan.py` | `R-B-DB` and `R-B-ROLE` rewritten as catalog readings; `R-B-ROOT` demoted to a precondition; new C-8 blocker; `UnresolvedStep.blocks_mutation_ids`; `_psql(tuples_only=…)`; `R-B-PG`'s purpose corrected; the band-0 audit table |
| `tools/phase_5_0_evidence/execution/boundary.py` | `ProcessBoundary.run` and both implementations carry the question through to the sanitizer |
| `tools/phase_5_0_evidence/execution/executor.py` | passes `step.catalog_question`, from the plan and never from the run |
| `tools/phase_5_0_evidence/review_manifest.py` | pins per-step `catalog_question` and per-blocker `blocks_mutation_ids`; `catalog_baseline_count` in the digest; `MANIFEST_VERSION` **6 → 7** |
| `tools/phase_5_0_evidence/execution/cli.py` | §5c gains *how* each baseline proves absence and a blocked-baseline table; the dry-run summary reports blocked mutations |
| `tests/phase_5_0_evidence/test_r14_remediation.py` | **new**, 43 tests |
| `tests/phase_5_0_evidence/harness_fixtures.py` | one shared `runnable_plan()`, replacing six copies, and it now says what it suspends |
| `tests/phase_5_0_evidence/test_r13_remediation.py` | `FakeHost` models both catalogs; the deleted-object completeness test admits owned **or** blocked and refuses the third state |
| `tests/phase_5_0_evidence/test_concrete_plan.py`, `test_executor.py` | C-8 in the conflict roll call and in the dry-run output |
| six other suite modules | fake boundaries accept the new keyword; local `runnable_plan()` copies removed |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated, never hand-edited |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated |

The manifest version moves to 7 because a digest approved under 6 covered a plan
whose three baselines proved absence with a failure. That is a different plan,
not a differently rendered one, so it stops matching rather than being
reinterpreted.

No production file was changed. The dirty worktree was preserved; nothing was
staged, committed or reset.

## R14.6 Post-fix tests

`tests/phase_5_0_evidence/test_r14_remediation.py`, 43 tests, every one across
injected fakes:

* the reviewer's reproduction and both audit extensions, now stopping at the
  baseline with the object intact and no removal requested;
* **five unknown states** per PostgreSQL baseline — non-zero exit, no control,
  an unparsable line, no declared question, no observation at all — each
  establishing no ownership;
* the positive direction, so the correction is not merely a way to refuse;
* `getent`'s other statuses, 0, 1, 3 and 4, none of which satisfies a baseline;
* the audit over the generated plan, and the exact roll call of what each
  surviving baseline compares;
* C-8's declaration, its 29 blocked mutations, that no blocked mutation is also
  owned, that the submitted plan is refused at the executor's second gate, and
  that even with every blocker waived the run still stops before the first
  `install`;
* the reading itself: seven listings including an error sentence, a padded row
  and an empty one, plus the assertion that no name it read reaches an
  observation; and
* the manifest pin, including that changing only the subject changes the digest.

**Meaningful error states are tested, not only present and absent**, and the fake
was corrected as the review asked: `FakeHost` now models both catalogs as
listings answered from its object set, so a failed read is no longer modelled as
an absent object.

### Exact results, from the tree submitted

Run serially, in the prescribed order, with `TEST_DATABASE_URL` explicitly
**unset**.

| # | Command | Result |
|---|---|---|
| 1 | `pytest -q tests/phase_5_0_evidence/test_no_execution.py` | **181 passed** |
| 2 | `pytest -q tests/phase_5_0_evidence/test_r14_remediation.py tests/phase_5_0_evidence/test_r13_remediation.py` | **96 passed** |
| 3 | `pytest -q tests/phase_5_0_evidence` | **1255 passed** |
| 4 | `pytest -q -rs tests/test_*.py` | **2988 passed, 326 skipped** |
| 5 | `pytest -q -rs tests/web` | **1610 passed, 1362 skipped** |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `compileall tools/phase_5_0_evidence tests/phase_5_0_evidence` | exit 0 |
| 8 | `git diff --check` | clean |

Before the fix, tests 1 and 3 stood at 181 and 1211 on the R13.2 tree; the three
reproductions in R14.2 were run against that tree and are reproduced above.

**The skip counts are the restriction, not a pass.** `TEST_DATABASE_URL` is
unset under this prompt, so every database-marked test skipped: 326 in the bot
suite and 1362 in the web suite, against the 80 that a properly configured
disposable PostgreSQL would leave. **No database-backed assertion in this
submission was executed**, and no earlier passing total is reused.

**Interpreters, reported as the fallbacks they are.** The canonical oracle-test
interpreter is `/opt/freedom-blades/runtime/venv-web/bin/python`. A file exists
at that path on this workspace host, and it is not that interpreter: it has no
`pytest`. Tests 1–3 and 5 ran under `/opt/discord-bots/venv-web/bin/python` and
test 4 under `/opt/discord-bots/venv/bin/python`, both explicitly labelled local
fallbacks. Nothing was run on `oracle-test`.

**Configured tooling, reported honestly.** No formatter, linter or type checker
is configured in this repository: there is no `pyproject.toml`, `setup.cfg`,
`.flake8`, `mypy.ini`, `ruff.toml` or pre-commit configuration, and none of
`black`, `ruff`, `flake8` or `mypy` is installed in either virtualenv. They were
not run because there is nothing configured to run, not because they were
skipped. `compileall` and a whitespace/conflict-marker scan of every changed
file stand in their place; `git diff --check` covers the tracked files only,
because the harness tree is still untracked.

### Generated artifacts, verified against independent regeneration

Both were produced by

```sh
python -m tools.phase_5_0_evidence.execution.cli \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

which is a dry run: it prints what would run and starts nothing. They were then
generated a second time to a scratch directory and compared byte for byte:
**identical**.

| Artifact | SHA-256 of the file |
|---|---|
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | `4af28cf8db3b95cab28dcdab40593bcf0c53cf31eee418e90b9f5338523fe48a` |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | `965a6e0418f4a5a0cabced9cb24b2986d5ef3711cccb0184f1934a8dcda809ee` |

| Figure | R13.2 | This tree |
|---|---|---|
| Covered sources | 30 | 30, unchanged |
| Command steps | 127 | 127, unchanged |
| Cleanup steps | 46 | 46, unchanged |
| Mutations | 43 | 43, unchanged |
| Expectation contracts | 64 | **66** |
| Ownership baselines | 10 steps over 41 mutations | 10 steps over **12** |
| Blocked mutations | 0 | **29** |
| Unresolved items | 6 | **7** |
| Conflicts | C-6, C-7 | **C-6, C-7, C-8** |
| `executable` | False | False |
| Manifest version | 6 | **7** |

**Changed vectors: two.** `R-B-DB` and `R-B-ROLE`. No other step's argument
vector, run-as identity, binding site, materialization or cleanup vector
changed. The digest also changes because seven covered sources changed.

## R14.7 Remaining design decisions

**C-8 is new and is the one this remediation raises.** It needs a maintainer
decision on exactly one of three, followed by independent review:

1. **admit a creation whose pre-existence status is unique and documented**, so
   filesystem ownership comes from the creation rather than from a probe, as it
   does for `groupadd` and `useradd`. This widens `PERMITTED_EXECUTABLES`;
2. **approve a bounded structural reading of `namei`'s per-component output**,
   with its reviewed key set, its value shapes and its treatment of a component
   whose failure is not distinguishable all written down. This widens the
   observation surface and depends on an output format no reviewed document
   pins; or
3. **accept that this harness never removes a filesystem object**, and record
   §2.13.2b operator recovery as the only path cleanup — in which case the 29
   reversals are withdrawn from the cleanup plan rather than left inapplicable.

Option 3 needs no new mechanism and is the smallest; it is also the one that
changes what a completed run leaves behind, which is an operations decision
rather than an implementation one. **No option is adopted here.**

Everything else the R13 prompts left open is unchanged: **C-6 and C-7 remain
unresolved**, all **twelve unsupplied target facts remain unconfirmed**, no
immutable-flag operation was added, no Band 7 ingestion stage was built, no
observation was invented and no narrower execution scope was approved.

## R14.8 Operational restrictions observed

No SSH. `oracle-test` was not contacted, inspected or synchronized. No generated
vector was run, `--execute` was not used, no real process boundary or
materializer was armed, no database operation was performed and the destructive
backup/restore drill was not run. `TEST_DATABASE_URL` was left unset throughout.
No host object was created and no `git` write was performed. General
administrative access to the disposable server was not treated as permission for
any of it.

## R14.9 What this submission does not do

It does not close `EH-R13-1` or `EH-R14-1`; both are the independent reviewer's
to dispose of. It closes no other finding, confirms no assumption and adopts no
option. A new digest identifies review input and grants no execution authority.

Package 5.0 remains **not ready**. `P5.0-R5` remains **Blocking** and `OD-62`
remains **Open**. No product implementation, migration `0014`, deployment,
cutover or Package 5.1+ work is authorized, and none was performed.
