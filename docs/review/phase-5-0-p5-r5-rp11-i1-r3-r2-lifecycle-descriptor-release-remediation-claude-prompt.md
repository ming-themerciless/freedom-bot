# Claude prompt — lifecycle-store descriptor-release remediation

Prompt ID: `C-P5.0-R5-RP11-I1-R3-R2`

Date: 2026-09-28

State: **assigned by Peter Duscha's instruction; repository-only remediation;
no host or operational authority**

## 1. Assignment

Claude, repair the production file-descriptor ownership defect exposed during
`C-P5.0-R5-RP11-I1-R3-R1`. `DurableRecordStore.read_record_bytes` and its
publication path in `tools/phase_5_0_evidence/lifecycle_storage.py` acquire
descriptors through `PosixFilesystem` without releasing them. The returned
diagnosis attributes 963 leaked descriptors across four older laboratory test
modules to those paths and reports only about 49 descriptors of headroom in the
whole evidence suite at a 1024 soft limit.

This is a narrow production reliability remediation. Do not change the RP-11
retained-alias design, the pending unadmitted-pair policy, or the test-side RP-11
cleanup delivered by R1.

Read, in order, before planning or editing:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 13, 14,
   16 and 20 and the Package 5.0 acceptance criteria;
3. `docs/review/Handover information`;
4. the first restriction banners and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-09-28-p5-r5-rp11-i1-r3.md`;
6. the R1 prompt and
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-handback.md`,
   especially §§6, 7.5 and 8;
7. `tools/phase_5_0_evidence/lifecycle_storage.py`, especially
   `DurableRecordStore.read_record_bytes` and `publish`;
8. `PosixFilesystem.release` and its ownership contract in
   `tools/phase_5_0_evidence/execution/descriptors.py`;
9. the lifecycle/laboratory fixtures and directly affected tests, especially
   `tests/phase_5_0_evidence/test_lab_integration.py`; and
10. `tools/phase_5_0_evidence/review_manifest.py`, the review manifest, the
    generated concrete plan and their structural/no-execution tests.

The R5 requirements remain the accepted baseline. All later RP-11 requirements,
source and digests remain proposed, unwired and unaccepted. A regenerated
manifest is review input, not approval.

## 2. Required correction

Establish explicit ownership for every descriptor acquired by the two affected
store paths and release it exactly once on every reachable success and failure
path.

At minimum:

* `read_record_bytes` must release the descriptor after a successful read and
  after a read refusal/failure;
* the publication path must release its created temporary-file descriptor after
  successful publication and after every injected or real failure occurring
  after acquisition;
* no release may occur if acquisition itself failed;
* no descriptor owned by `DescriptorInventory` may be released;
* a descriptor number must never be retried after `release` reports failure;
* release failure must not be silently converted into success. Preserve the
  existing fail-closed result model and report a truthful refusal when the
  mechanism cannot establish successful release; and
* the existing byte, history, exclusivity, rename, durability-barrier and
  interruption semantics must remain unchanged.

Use structured cleanup rather than duplicating release calls across branches.
Do not use raw `os.close` in `lifecycle_storage.py`; keep ownership inside the
`PosixFilesystem` abstraction. If the present result types cannot truthfully
represent a release failure without a broader contract change, stop and report
the exact conflict instead of weakening the failure.

Audit only the immediately adjacent `DurableRecordStore` paths for the same
ownership pattern. If another leak is demonstrated there, include the smallest
coherent fix and explain it. Do not turn this into a repository-wide descriptor
refactor.

## 3. Regression proof

Add leak-sensitive tests that exercise the production paths, not merely fixture
cleanup. Tests must prove descriptor-table stability across repeated operations
and must fail against the pre-remediation implementation.

Cover at least:

1. repeated successful reads;
2. a read failure after acquisition;
3. repeated successful publications;
4. every existing injected publication failure after descriptor acquisition,
   including data synchronization, rename and record-entry synchronization;
5. a write refusal/failure after acquisition;
6. a release failure, including its fail-closed outcome and the no-retry rule;
7. acquisition failure, proving no attempted release of an unowned descriptor;
   and
8. preservation of the interrupted-publication artifacts and barrier reporting
   already required by the lifecycle contract.

Prefer deterministic filesystem ownership instrumentation. A Linux
`/proc/self/fd` count may supplement it but must not be the sole oracle. Do not
mask the defect with an autouse cleanup fixture, garbage collection, suite
reordering, test splitting, or a raised descriptor limit.

## 4. Manifest and generated artifacts

`lifecycle_storage.py` is covered source. Therefore:

1. increment `MANIFEST_VERSION` once with a precise version-history entry for
   this correction;
2. regenerate the existing review manifest and concrete plan only through the
   established harness dry-run workflow;
3. prove both artifacts are deterministic by a second dry run or the existing
   byte-identity check;
4. update directly affected manifest/generated-plan expectations; and
5. report full SHA-256 values for every changed covered source and generated
   artifact.

Do not manually manufacture generated bytes. Do not run the harness with
`--execute`. Do not describe the new digest as accepted, pinned or executable.

## 5. Required verification

Use `/opt/freedom-blades/runtime/venv-web/bin/python`. Every pytest invocation
must explicitly unset `TEST_DATABASE_URL`, set `PYTHONDONTWRITEBYTECODE=1`, use
`-p no:cacheprovider`, run serially and include `-rs`.

Run, from fresh processes where applicable:

1. the new focused descriptor regressions and directly affected lifecycle/lab
   modules;
2. RP-11 capture and retention tests, to prove this change does not disturb R1;
3. directly affected structural, manifest, concrete-plan and no-execution
   tests;
4. all of `tests/phase_5_0_evidence` as one process with its soft descriptor
   limit lowered to exactly 1024; and
5. the same whole package once at the default soft limit.

Zero skips are required in focused and whole-package selections. Record exact
pass/fail/skip totals and warnings. Do not raise the limit or split/reorder the
whole-package run. Also compile changed Python, run scoped `git diff --check`,
verify new Markdown links and independently recompute reported hashes.

Do not run the full bot or web suites. Do not use `oracle-test`.

## 6. Deliverables and authorized files

Authorized edits are limited to:

* `tools/phase_5_0_evidence/lifecycle_storage.py`;
* the smallest directly affected files under `tests/phase_5_0_evidence/`;
* `tools/phase_5_0_evidence/review_manifest.py`;
* `docs/review/phase-5-0-evidence-harness-review-manifest.json`;
* `docs/review/phase-5-0-evidence-harness-concrete-plan.md`;
* a new handback at
  `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r2-lifecycle-descriptor-release-remediation-handback.md`;
* and, on return only, the four current-state pointers: `docs/review/Handover
  information`, `docs/project-management/status.md`, implementation-plan §20
  and the first disposable-server restriction banner.

The handback must include:

* the exact ownership defect and correction;
* a success/failure-path ownership table;
* regression tests and why they fail on the old implementation;
* exact commands, process boundaries, limits, results and warnings;
* files changed with before/after SHA-256 values;
* manifest version/digest and artifact determinism evidence;
* scoped Git status and `git diff --check` result;
* checks not run and why; and
* focused questions for mandatory independent Codex re-review.

Preserve unrelated worktree changes. Do not edit historical handbacks, reviews,
decision records or acceptance records. Stop after the handback and pointer
updates.

## 7. Boundaries and stop conditions

The pending unadmitted-pair choice is independent and does not block this
assignment. Do not record Peter's choice, change option-1 source semantics,
edit the decision proposal, or close RP11-I1-R3-1.

Stop and return the exact blocker if the repair requires changing the
`PosixFilesystem.release` contract, I3 behavior, accepted R5 requirements,
C-11, launcher configuration, another RP, MD-1 through MD-6, architecture,
data authority, authorization or operational strategy. Do not bypass a stop by
weakening an assertion, suppressing a release failure or expanding scope.

This assignment authorizes repository reads, the scoped edits above and local
synthetic tests under pytest temporary directories. It does **not** authorize
SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled writes, reboot, verifier, evidence band,
harness `--execute`, real participants, a real capture root, operational paths,
protected historical artifacts, secrets scanning, commits or pushes. Do not
read secrets or print the environment. A guard refusal is a stop condition.

## 8. Return state

Return for independent Codex technical, security, operational and evidence
review, then stop. Do not mark the production defect or any earlier finding
closed. RP-11 remains unmet; its requirements, implementation and digest remain
unaccepted and unwired; neither pass is executable; P5.0-R5 remains Blocking;
OD-62 G-A remains conditional; `plan.is_executable=False`; and Package 5.0
remains not ready.
