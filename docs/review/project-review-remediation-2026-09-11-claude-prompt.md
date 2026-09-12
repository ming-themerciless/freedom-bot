# Claude — bounded remediation of the September 11 review

Date: 2026-09-11. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Review: [project-review-2026-09-11.md](project-review-2026-09-11.md).

## Objective and scope

Keep the reserved-laboratory direction. Correct the six findings in one bounded
pass and return for Codex technical review. VM work remains deferred; ADR 0011
remains Proposed. Do not restart architecture selection or expand the harness
beyond the mechanisms needed to answer these findings.

This prompt applies the existing local remediation authorization. It permits
repairs to the pure reservation/admission/release decisions, bounded synthetic
producers, their tests, and supporting design/evidence documentation. It does
**not** accept the proposed privileged runner or authorize its implementation.

Before work, read `.agents/AGENTS.md` completely; the implementation plan's
reading map, §§0, 16, 20 and the relevant Phase 5/testing requirements;
`docs/review/Handover information`; and the restriction banner and instructions
in `docs/operations/disposable-test-server.md`. Then read:

- the September 11 review, all six findings and its verification limits;
- `phase-5-0-reserved-laboratory-direction.md`, the preceding Claude prompt,
  handback and runner contract;
- package-plan §§2.12–2.13, especially Algorithm C1/C2/C5, §2.13.2b and JNL-47;
- the affected reservation, feasibility, cleanup, executor, boundary,
  materializer and case-program source and tests; and
- the existing C-8 ownership/recovery findings and contracts referenced by the
  review, plus current generated plan and manifest.

Check Git status and preserve unrelated changes. Do not stage, commit, push,
reset or rewrite history. Preserve the CRP correction, its tests and synthetic
fixtures; it received a positive technical recommendation and needs no further
maintenance change in this pass. Do not restart the bot.

## 1. Correct the evidence ordering first — PR-20260911-5

The approved sequence is C1 probe **including cleanup**, C2 validation, then C5
first persistent generation artifact. Cleanup failure at C1 stops every later
step. Generation/row absence means creation was never reached, not that an
already-created generation was deleted.

Repair `feasibility.py` and its tests to model this sequence. Use an injected
publication sink that records attempted publication and synthetic artifacts;
assert both that publication was not reached and that no artifact/row exists
after each stage failure and both cleanup-failure variants. The successful
control must reach publication. An intentionally misordered negative control
must publish early and fail classification. Do not produce absence by simply
passing constant `False` values to the classifier.

Keep this a minimal ordering model, not a second coordinator implementation.
Retain corrupt/missing-output, duplicate-input and failure coverage relevant to
the producer interfaces. Distinguish actual harness observations from model
observations and future product acceptance tests.

Add a dated correction to the old handback's §3.4 rationale; preserve the
historical submission. Reassess all three C-7 dispositions against the corrected
ordering. Withdraw the incorrect creation-then-deletion rationale. If a
readiness/implementation evidence split is still necessary, submit the exact
remaining criterion, why a bounded model cannot establish it, its later named
acceptance test and your recommendation for Peter. Do not assume approval or
change the package acceptance criteria. All three cases stay unresolved in the
shipped execution plan pending independent producer review.

## 2. Repair the local decision API — PR-20260911-3 and PR-20260911-4

Implement the decision half using injected observations only. No host lock,
durable writer or operational integration is built in this pass.

Admission must receive explicit lifecycle evidence for the named host. Distinguish
verified first use, a verified released predecessor, missing/unreadable history,
an active/recovering predecessor, and quarantine. A free process lock, complete
service inventory, elapsed deadline or absent quarantine argument cannot stand
in for verified release. Bind predecessor/release observations to the correct
host and reservation. Specify the durable record's eventual ordering in the
contract so a crash before quarantine publication cannot erase an active run.

Release must distinguish an unobserved residue check from an observed empty
result. Omitted, unknown or incomplete evidence refuses release/quarantines as
appropriate. Audit public transitions: `advance()` must not admit a reservation
or release one without the corresponding validated decision. Keep recovery
separate from admission, preserve quarantine across timeout/lock loss, and
specify how verified operator recovery permits a **new** reservation without
resuming the quarantined run.

Add regressions before repairing the reported cases. At minimum cover:

- a free/readable lock with missing lifecycle history;
- an expired/crashed predecessor with no verified release, including a crash
  after effects but before a quarantine record could be published;
- a predecessor release for the wrong host or run;
- omitted residue evidence versus observed-empty and observed-present residue;
- evidence-free admission/release through public transition helpers;
- orphaned children, delayed transactions and interrupted recovery;
- verified first use, verified predecessor release and completed operator
  recovery as distinct positive controls; and
- continued refusal of real execution while the ownership remedy is unaccepted.

Do not claim these pure decisions persist or enforce a reservation. Name the
eventual adapter responsibilities separately from what this pass implements.

## 3. Revise the runner contract — PR-20260911-1, -2 and -6

Write `phase-5-0-reserved-laboratory-runner-contract-r2.md`, marked **submitted
for technical review, not accepted and not implemented**. Supersede the prior
contract explicitly and preserve it. Produce one concrete preferred mechanism
and a complete operation table, not a new architecture survey.

### Effect ownership (-1)

For creation, provisioning, payload installation/use, flag changes, experiments
and cleanup, name the exact object/bytes, resolution operation, descriptor owner
and lifetime, prerequisite, and enforcement immediately before the effect.
Explain descriptor custody across separate process invocations and privilege
transitions. Account for the actual replacements of pathname-based `install`,
`chattr`, removal and payload-use operations; four added verb names are not an
implementation contract for those effects.

A held descriptor keeps referencing its original inode after pathname
replacement. Comparing that descriptor with its own baseline does not discover
replacement. A held parent plus `unlinkat` still resolves the final entry;
`RENAME_NOREPLACE` does not bind the source entry to a previously checked inode.
Specify exclusion/quiescence or another concrete protection for each remaining
lookup interval. Account for this run's experimental writers separately from
trusted administrators. If safety cannot be established, refuse dependent
effects and preserve independent recovery.

Verify syscall claims against the primary documentation linked by the review.
Separate documented semantics, proposed guarantees and operational assumptions.

### Independent recovery (-2)

Specify how exact pre-change bytes are captured, verified and durably retained
outside experimental writable custody **before the first configuration
mutation**. Include location/owner/parent permissions, size and read-failure
handling, digest/metadata binding, publication durability, restart discovery,
retention and disposal conditions. Explain how recovery remains possible if R
is replaced or unavailable and the executor's memory is lost.

An unspecified operator copy is not a safeguard. The current
`cleanup.RECOVERY_PROCEDURE` uses `R/before`; either propose the exact independent
procedure and its prerequisites or refuse mutation when no trustworthy basis
exists. Bind the verified buffer to the written bytes and address destination
custody, partial writes/interruption, restoration order, reload and verification.
Do not implement the capture/restore writer during this pass.

### Cooperative lock and lifecycle storage (-6)

Specify one workable lock protocol for all seven participating entry points,
including test suites, synchronization and dependency updates. Name the creator,
directory/file ownership and modes, identities that open/write the lock or record,
when the stable lock is held, and when lifecycle state becomes durable. Account
for first setup, crash, restart and release without automatic takeover.

Ordinary participants cannot create or unlink entries in a root-owned 0755
directory. Precreation conflicts with the submitted O_EXCL protocol. Evaluate
the review's preferred persistent lock inode plus separately protected lifecycle
record against the actual participant identities, and specify a successful
normal path as well as refusal paths. Describe every required provisioning or
permission change explicitly; none is approved by calling the adapter
unprivileged. No host lock adapter or provisioning is implemented here.

### Exact diff and proof obligations

For the selected mechanism, enumerate changed modules/interfaces, arguments,
syscalls, descriptor transfer, executable/verb allowlists, identities, permissions,
sudoers/capabilities, durable storage and manifest coverage. Do not infer a zero
permission delta from unchanged executable names.

Supply a bounded matrix covering root, descendant and final-entry substitution;
replacement after a successful check; in-place capture mutation; capture failure
before mutation; wrong destination; executor restart/lost memory; interrupted
restore; unknown surviving writers; and successful controls. Model tests must
track original/replacement identities and bytes actually affected. Label them as
proposal models, not implementation proof. Keep existing unfixed-behavior
reproductions visibly labelled and useful.

LAB-1 remains **Important**. Include its exact proposed reporting-contract fix
and regression expectations in this contract, preserving configuration recovery
and residue recovery as distinct procedures. Its cleanup mechanism change stays
behind this design checkpoint; do not silently implement it through the producer
repair or weaken the reproduction to make the record pass.

## 4. Restrictions and verification

No SSH, target inspection, synchronization, provisioning, database operation,
service mutation, credential access, generated-vector execution, `--execute`,
armed real boundary/materializer or new privileged mechanism implementation.
Only local synthetic tests with injected effects are allowed. No VM expansion,
migration 0014, product implementation, deployment, cutover or Package 5.1+.

Retain the operational-ineligibility control, missing-coverage controls,
`is_executable=False`, real-execution refusal and twelve unconfirmed target
facts. The later Codex read-only preflight remains after implementation review;
this prompt neither performs nor expands it. Current digest
`bbb3854fbdffae00696544465f1cd7bbdf22ad18583056490a6735444800e4fa` is review
input only and must not be passed to `--execute`.

Verify fallback interpreter availability/version before use. These are local
exceptions; the canonical environment remains the documented runtime venv on
`oracle-test`. Run structural checks first, changed focused regressions next,
then complete available suites. Keep bot and web serial and TEST_DATABASE_URL
unset. In particular, the web fallback lacks `discord`; use the bot interpreter
for skills tests.

```bash
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py
# Include any additional focused regression modules changed in this pass.
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_skills.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test 'foundry-module/tests/'*.test.mjs
git diff --check
```

Run scoped compileall on changed Python files and configured lint/type/format
checks; report unavailable or unconfigured tooling separately. Report every skip
as unverified. The previous review observed harness 1490, bot 3016/326 skipped,
web 1610/1362 skipped and Foundry 171. These are comparison figures, not results
for the new tree; the database-enabled web skip baseline is 80.

If covered source changes, regenerate through the non-executing manifest/render
CLI twice, compare bytes and independently recompute all covered hashes. Never
hand-edit generated artifacts or record unperformed producer review. Explain any
coverage-list change. The resulting digest remains review input only.

## 5. Consolidated handback

Write `project-review-remediation-2026-09-11-handback.md` with a disposition table
for PR-20260911-1 through -6 and LAB-1. Identify implemented local fixes, named
regressions and before/after observations separately from proposed privileged
changes. Link the revised contract, give the exact permission delta and remaining
proof obligations, and state whether any corrected criterion decision remains
necessary. Include exact commands, interpreters, results, skips, manifest checks,
unrun checks and the next step's owner and required evidence.

Add dated errata to superseded claims and update the active handover/status
pointers concisely. Preserve prior reviews and do not close findings on your own
authority. Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**
and EH-R16-1 **Open** pending review.

Return after this local pass. Codex technical acceptance of the revised mechanism
and any required maintainer permission/criterion decisions precede privileged
implementation; implementation review precedes the later target preflight and
separate execution decision. Passing tests does not advance those gates.
