# Claude — reserved-laboratory implementation remediation

Date: 2026-09-14. Authorization: C-P5.0-LAB-I-R1.
Review to answer:
[Codex technical and security review](project-review-2026-09-13-reserved-laboratory-implementation.md).
Original implementation:
[Claude handback](phase-5-0-reserved-laboratory-implementation-handback.md).
Design basis:
[runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

## Assignment

Repair **PR-20260913-LABI-1**, **PR-20260913-LABI-2** and
**PR-20260913-LABI-3** in one bounded repository pass. Add failing-before public
regressions and conjunct-level negative controls, integrate the reservation and
descriptor mechanism through the actual repository entry points required by
C-P5.0-LAB-I, regenerate review artifacts through the non-executing path when
required, and return one remediation handback for independent Codex technical
and security re-review.

This authorization is for repository changes and local tests with
`TEST_DATABASE_URL` unset only. It does not authorize use or modification of
the disposable server and does not authorize any real participant, generated
vector or `--execute` path to run.

## Governing context

Before planning or changing anything, read completely:

1. `.agents/AGENTS.md`;
2. the implementation-plan reading map and §§0, 12 (Package 5.0), 13, 16 and
   20;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. runner contract r6, especially §§0–9;
6. the Codex review named above and the implementation handback it reviews;
7. the active Package 5.0 plan, project status, decision register and RAID
   register; and
8. the existing implementations and tests for the CLI, executor, boundary,
   materializer, descriptor inventory, recovery store, lifecycle record, run
   ledger and all seven `PARTICIPATING_ENTRY_POINTS`.

Inspect Git status and preserve every unrelated and reviewer-authored change.
Trace the actual call graph from each participant's admission through its first
effect, durable completion or recovery, and successor admission. Trace the
harness additionally through capture, first mutation, cleanup/restoration,
terminal publication and lock release. Do not infer integration from an
isolated class or a test-only constructor.

## Finding 1 — bind the recovery destination before mutation can be permitted

The submitted `RecoveryStore.publish()` accepts a caller-supplied destination,
verifies only stored-copy bytes and sets `mutation_permitted` from barrier
membership. Codex reproduced a publication with
`destination=/wrong/destination` returning both `published=True` and
`mutation_permitted=True`, although restoration must refuse that record.

Required behavior:

- Define the reviewed configuration capture set at the integration boundary:
  exact component, exact destination and exact correspondence between stored
  copy, record and restoration target. A caller must not be able to substitute
  an arbitrary absolute destination.
- Validate the entire requested set **before** creating the recovery run
  directory or writing any temporary, copy or record. Missing, additional,
  duplicate, malformed, cross-directory or mismatched component/destination
  entries refuse with no publication and `mutation_permitted=False`.
- Publication verification must establish the same one-to-one record/copy/
  destination correspondence that `restore_configuration()` consumes, not
  merely compare copy digests.
- `mutation_permitted=True` only when the exact reviewed set is durably
  published, all five barriers returned success and the complete basis verifies.
- Restart discovery and restoration must apply the same binding and refuse
  orphan copies, orphan records, duplicate destinations, wrong run IDs,
  mismatched copy names and records naming another destination.
- Refusals remain fixed and bounded. Do not include hostile destination text,
  bytes or raw operating-system messages.

Add public regressions for Codex's wrong-destination reproduction and every set
shape above. First run them unchanged against the submitted implementation and
record the failures. Add a negative control that removes only the destination/
correspondence binding and causes the wrong-destination publication to permit
mutation again. Retain positive multi-file publication, discovery and restore
coverage so the correction cannot pass by refusing every input.

## Finding 2 — ownership identity is mandatory, never optional

The submitted `_open_and_verify()` and `remove_object()` compare only when the
recorded identity is truthy. Codex created a file outside the effect issuer,
never called `record_identity()`, and the public `remove_object()` deleted it
while returning `recorded_identity=''`.

Required behavior:

- A non-empty creating-step identity for the exact `(directory_role, name)` is
  a mandatory prerequisite of setting flags, clearing flags and removal.
- The immediate pre-check must find an object and its identity must equal that
  mandatory record. Missing record, absent object and unequal identity are
  three refusing inputs, all before `ioctl` or `unlinkat`/`rmdir`.
- Equality is the only admitting branch. Do not encode the rule as optional
  truthiness, a default empty value or a comparison skipped for absence.
- Preserve the accepted distinction: the pre-check detects substitution before
  removal; quiescence is the prevention for the final-component interval; the
  post-check establishes absence only and never which inode was removed.
- Ensure every production creation path records the identity at the point r6
  specifies, rather than relying on callers to remember a separate optional
  call later.

Add public failing-before regressions for set, clear and removal without a
recorded identity; absent-at-pre-check for each applicable operation; and an
unequal identity. Assert that the target object survives every refusal. Add
single-conjunct negative controls for the mandatory-record, present-object and
equality checks. Keep positive descriptor-bound effects and the documented
post-check limitation covered.

## Finding 3 — integrate the mechanism through the real call graph

The submitted `LaboratorySession`, `ParticipantRunLedger`, `RecoveryStore` and
`DescriptorBoundEffects` are consumed only by tests. The CLI still builds the
legacy `ExecutingRunner` over `SubprocessBoundary` and `SystemMaterializer`;
descriptor transfer is not connected to process launch; and none of the six
non-harness participant paths uses the shared lock and ledger protocol.

Required integration:

1. Give each of the seven entries in `PARTICIPATING_ENTRY_POINTS` a repository-
   owned integration point that:
   - takes or waits for the pre-existing cooperative lock;
   - re-seals, reads and validates the lifecycle record and ledger in r6 §5.6
     order;
   - refuses before its first relevant effect unless admission succeeds;
   - durably publishes `participant_started` before that effect;
   - derives and durably publishes completion only after that participant's
     exact profile evidence; and
   - leaves an interrupted or unreadable run blocking every successor,
     including reset, until attributable recovery is published.
2. Integrate the harness CLI and executor with the same session, record and
   ledger objects. Preserve r6 §5.12 exactly: validate the stored reservation
   binding, decide release, publish release durably, publish harness completion
   durably, then release the lock.
3. Connect executor descriptor issuance and declared transfer to the boundary
   launch. `DIRFD` remains an index into the declared inherited table; remap or
   inherit exactly the descriptors named by that table, clear `FD_CLOEXEC` only
   for them, and transfer no synchronizable descriptor. An undeclared, closed,
   wrongly mapped or non-directory descriptor refuses.
4. Route P1/P1b/P2/P4/L3 through `DescriptorBoundEffects`; route pre-M1 capture
   through `RecoveryStore`; require its corrected `mutation_permitted`; and
   route restoration through the verify-and-write implementation. The old
   pathname-based `install` and `chattr` steps must no longer be emitted or
   executable for these effects.
5. Reduce `plan.PERMITTED_EXECUTABLES` from 22 to r6 §6.4's 20 by removing
   `/usr/bin/install` and `/usr/bin/chattr`, update the generator and reviewed
   vectors accordingly, and prove neither executable remains reachable.
6. Keep every operational gate closed. `is_executable` remains False;
   `REAL_EXECUTION_REFUSAL` remains unconditional; the actual target facts stay
   unconfirmed. Integration is repository wiring, not permission to invoke it.

Add structural and behavioral tests that fail against the submitted tree and
prove:

- all seven integration points share the one admission and ledger protocol;
- none reaches its first effect before a durable start;
- each exact completion profile is required, with reset receiving no exemption;
- an interrupted participant blocks all seven successors;
- the executable CLI branch is wired to the mechanism even though the standing
  refusal prevents it from running;
- the executor uses the corrected recovery and descriptor effects instead of
  the legacy materializer/command steps;
- the boundary receives the declared descriptor table and no synchronizable
  descriptor; and
- `install` and `chattr` are absent from the allowlist, generated plan and
  executable call graph.

For each load-bearing integration check, provide a focused reversal or negative
control that makes the corresponding test fail. A source-code substring guard
alone is not proof of ordering or runtime composition; pair structural checks
with behavior over injected local fakes or `tmp_path` stores.

## D1 and D2 contract deviations

Codex's review found the existing choices technically reasonable but not
retroactively authorized by r6:

- `linkat` followed by `unlinkat` may replace
  `renameat2(RENAME_NOREPLACE)` only after the controlled contract explicitly
  names its two-syscall, two-name interruption state and preserves the
  unexplained temporary; and
- the short-lived `.`-relative listing descriptor must be added explicitly to
  the complete descriptor inventory and permitted-use table.

Do not silently edit an accepted contract and present the edit as approved. In
the remediation handback, provide the exact proposed r6 amendment for these two
points as a separately reviewable documentation delta, or identify an existing
maintainer disposition that already authorizes it. Until accepted, keep V6
unconfirmed and do not claim either deviation closed. Do not add a broader
`ctypes` exception or widen the trusted syscall/descriptor surface merely to
avoid documenting the decision.

## Preserved architecture and scope

- Continue reusing `lifecycle_storage`'s codec, state machine, participant
  validator, publication order and terminal sequence. Do not create a second
  reader or a weaker participant-specific admission path.
- Keep the accepted shared-identity design: all seven participants are intended
  to be `ubuntu`. Do not invent a multi-account alternative. V10 remains an
  unconfirmed target fact.
- Keep `DescriptorInventory` responsible for its long-lived descriptors. Do
  not let per-publication adapters close them.
- Bound caller-controlled run and reservation identifiers before they become
  filenames, role labels or refusal fields.
- Preserve the LAB-1 schema-3 canonical recovery procedures and raw read-back
  byte equality. Do not reopen, weaken or renormalize them.
- C-7's producer adapter remains synthetic feasibility only. Do not relabel it
  operational evidence or mark any C-7 case covered.
- Do not change production bot, web or database behavior. The integration
  wrappers may be defined and locally exercised with fakes; they may not be
  invoked against real participants in this assignment.

## Test and artifact procedure

1. Add the public regressions first and run them against the submitted
   implementation. Preserve and report their exact failing-before output.
2. Implement the smallest cohesive correction that closes all three findings.
3. Run narrow affected tests, the structural no-execution suite and the complete
   `tests/phase_5_0_evidence` suite locally with `TEST_DATABASE_URL` unset.
4. Run the available bot, web and Foundry suites only within the local-only
   restriction. Report every skip as unverified and distinguish unavailable
   tools from passing checks.
5. Run `git diff --check` and the configured formatter, linter and type checker
   if present. Do not install missing tools or dependencies.
6. If any covered source changes, regenerate the concrete plan and review
   manifest only through the non-executing CLI. Generate at least twice,
   compare bytes, independently recompute every covered-source hash and report
   the new digest as **review input only**. Never pass it to `--execute`.
7. Inspect the final diff for secrets, unrelated changes, unsafe refusal text,
   generated debris and any route that can bypass the standing execution
   refusal.

## Explicit prohibitions

Do not perform SSH, synchronization, server inspection, preflight, permission
or group changes, `systemd-tmpfiles`, provisioning, creation of `/run` or
`/var/lib` objects, database operations, destructive drills, service changes,
dependency installation, generated-vector execution, `--execute`, real
boundary or materializer use, migration, deployment, cutover, commit, push,
reset, history rewrite or bot restart. Do not read credentials or secret files.

Do not mark V6, V8, V10 or any target fact confirmed. Do not close C-7,
EH-R16-1, P5.0-R5, OD-62 or any review finding on the implementer's authority;
declare Package 5.0 ready; approve a digest; or claim operational evidence.

## Handback and stop point

Return one dated remediation handback containing:

- a finding-by-finding disposition with requirement-to-code traceability;
- the complete seven-participant and harness call graph before and after;
- files and interfaces added, changed or retired;
- exact failing-before, passing-after and negative-control evidence;
- security analysis of recovery destination binding, ownership binding,
  descriptor transfer, participant ordering, interruption and refusal text;
- the proposed, not self-approved D1/D2 contract delta;
- generated-artifact reproduction and the review-only digest, if changed;
- exact local commands, interpreters, results, skips and unavailable checks;
- rollback for repository changes;
- every unconfirmed target fact and unresolved finding/gate; and
- focused questions for independent re-review.

Stop after the handback. The next checkpoint is independent Codex technical and
security re-review. No preflight, provisioning or execution follows
automatically.

