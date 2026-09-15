# Claude — reserved-laboratory mechanism implementation

Date: 2026-09-13. Authorization: C-P5.0-LAB-I.
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).
Prior checkpoint: [LAB-1 R3 re-review](project-review-2026-09-13-lab1-rereview-r3.md).

## Assignment

Implement, in the repository, the accepted r6 reserved-laboratory mechanism and
the bounded producer code needed to answer C-7 and EH-R16-1. Add local tests and
return one implementation handback for independent Codex technical and security
review.

This authorization is for **repository changes and local tests only**. It does
not authorize use or modification of the disposable server.

## Governing context

Before planning or changing anything, read completely:

1. `.agents/AGENTS.md`;
2. the implementation plan reading map and §§0, 12 (Package 5.0), 13, 16 and 20;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
5. runner contract r6, especially §§0–9;
6. the LAB-1 R3 re-review and its two preceding remediation handbacks; and
7. the current Package 5.0 plan, status, decision register and RAID register.

Inspect Git status and preserve all unrelated and reviewer-authored changes.
Trace every affected call from admission through mutation, cleanup, terminal
publication and successor admission before editing.

## Authorized implementation scope

Implement the r6 mechanism represented by its §6 exact-diff inventory:

- `execution/descriptors.py`: descriptor inventory, dual-mode directory opens,
  `fstat` identity binding and refusal of unregistered descriptors;
- the four closed descriptor-relative case-program verbs and their bounded
  `DIRFD`, `OPEN_MODE` and `COMPONENT` arguments;
- executor descriptor issuance, quiescence gates, and required pre/post checks;
- ordered capture/publication and verify-and-write restoration with every r6
  durability barrier;
- the independent recovery store;
- the cooperative host-lock adapter over the pre-existing lock, including
  re-seal, record validation, ledger survey and fail-closed admission;
- durable reservation lifecycle storage, verified-first-use initialization,
  state-machine validation and the r6 terminal-publication ordering;
- the seven-participant run ledger, stored-start reservation binding, shared
  history validation, completion/recovery records and successor survey;
- integration points for all seven participants enumerated by r6, while keeping
  actual server commands and operational execution unreachable in this task;
- bounded repository-side producers/adapters for the three C-7 cases:
  `JNL-51-PROVENANCE-OMITTED`, `JNL-47-NO-GENERATION-ON-FAILURE`, and
  `JNL-47-RECOVERY-STATE`; and
- repository-owned provisioning definitions for r6 §7 V1–V5, V7 and V9. These
  are definitions for later review, not permission to apply them.

Preserve the accepted shared-identity design: all seven participants are
intended to run as `ubuntu`. Do not create a multi-account alternative. V6, V8
and V10 remain **unconfirmed target facts**, not values to infer or hardcode.

## Required safety properties

- No path may mutate from a pathname re-resolution after ownership was checked.
  Bind effects to the verified descriptors and bytes required by r6.
- An absent, malformed, unsupported, contradictory, wrong-target or unsealed
  lifecycle record refuses. Absence is never treated as a clean host.
- A free process lock, elapsed deadline, clean wrapper exit or absent quarantine
  is never sufficient reuse evidence.
- Every participant records durable in-progress state before its first relevant
  effect and durable completion only after its exact completion evidence holds.
- An unsettled or unreadable run blocks every successor, including reset.
- Recovery is attributable, append-only and never reuses an identity.
- The harness terminal sequence remains r6 §5.12: validate stored reservation
  binding, decide release, durably publish release, durably publish participant
  completion, then release the lock.
- Cleanup and recovery preserve the exact canonical procedures already accepted
  under LAB-1. Do not reopen or weaken schema-3 run-record validation.
- Fixed refusals must not expose paths beyond the bounded operator-facing fields,
  hostile bytes, operating-system exception text, credentials or player data.
- `is_executable` must remain `False` until C-7, EH-R16-1 and every target fact
  are genuinely resolved and independently reviewed. Do not force it true for a
  test or generated artifact.

## Tests and falsification

Write failing-before tests for each new mechanism where an implementation seam
already exists, and add negative controls that fail when the load-bearing check
is removed. Cover every r6 §9 `[P]` row and retain the `[M]` rows. At minimum,
exercise:

- descriptor substitution before and after checks, wrong descriptor mode,
  wrong identity and unregistered descriptor refusal;
- missing/held lock; free lock with non-terminal history; malformed, stale,
  cross-target and contradictory lifecycle records;
- missing/unreadable ledger; wrong participant, run, identity, filename,
  reservation or completion evidence; duplicate terminal entries;
- interruption at every publication barrier, process restart versus power-loss
  model, visible-but-not-durable publication and successor re-seal refusal;
- all seven participant profiles, unsettled-run blocking, attributable recovery
  and the reset's lack of exemption;
- terminal publication failure between release and completion;
- residue and configuration recovery independently and together;
- each C-7 producer's positive case, false-success control and importer binding;
  synthetic feasibility must not be relabelled operational evidence; and
- structural guards proving that no local test invokes SSH, synchronization,
  provisioning, database mutation, a real materializer/boundary, or `--execute`.

Regenerate the concrete plan and review manifest only through the non-executing
CLI if a covered source changes. Generate twice, compare bytes, independently
recompute every covered-source hash, and report the new digest as **review input
only**. Never pass it to `--execute`.

## Explicit prohibitions

Do not perform SSH, synchronization, server inspection, preflight, permission or
group changes, `systemd-tmpfiles`, provisioning, creation of `/run` or `/var/lib`
objects, database operations, destructive drills, service changes, dependency
installation, generated-vector execution, `--execute`, real boundary or
materializer use, migration, deployment, cutover, commit, push, reset, history
rewrite or bot restart. Do not read credentials or secret files.

Do not mark V6, V8, V10 or any other target fact confirmed. Do not close C-7,
EH-R16-1, P5.0-R5 or OD-62, declare Package 5.0 ready, approve a digest for
execution, or claim operational evidence. Implementation evidence and target
evidence are different things.

Use only available local interpreters with `TEST_DATABASE_URL` unset. Follow the
canonical skip-count rules: every skip is unverified. Distinguish unavailable
formatters, linters and type checkers from passing checks.

## Handback and stop point

Return one dated handback containing:

- requirement-to-code and r6 §9 traceability;
- files and interfaces added or changed;
- failing-before, passing-after and negative-control evidence;
- security analysis of descriptor binding, lifecycle durability, identities,
  participant completion, recovery and refusal messages;
- generated-artifact reproduction and review-only digest, if changed;
- exact local commands, interpreters, results, skips and unavailable checks;
- configuration/provisioning definitions added, explicitly noting none applied;
- rollback for repository changes;
- every unconfirmed target fact and unresolved gate; and
- focused questions for independent technical and security review.

Stop after the handback. The next checkpoint is independent Codex review. No
read-only preflight, provisioning or execution follows automatically.
