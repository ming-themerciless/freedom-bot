# Claude task — design the local `oracle-test` H-1 topology amendment

Work ID: `C-P5.0-R5-RP11-H1-D3`  
Assignee: Claude  
Scope: repository documentation and read-only repository inspection only  
Output: `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`

## Objective

Prepare a decision-ready amendment to the accepted RP-11 static-launcher
design so that H-1 installation and the complete later test/evidence workflow
run locally on the disposable Linux server `oracle-test` under its existing
unprivileged `ubuntu` account.

The Freedom-Blades production server and production Foundry service are
outside scope and must remain untouched. The amendment must remove the
superseded assumption that a separate repository/controller host drives
`oracle-test`, without weakening the selected LB-2S security, evidence,
authorization, failure or rollback properties.

This task designs the change only. Do not implement it, inspect a host, build
or install anything, or write an H-1 execution assignment.

## Governing inputs

Read the canonical repository instructions and current-state documents first,
including the active restriction banner. Then read completely or in the
relevant cited sections:

- [`project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-topology-correction.md`](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-topology-correction.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-prerequisite-decisions.md`](project-review-2026-10-04-p5-r5-rp11-h1-prerequisite-decisions.md), treating U-1 and U-3 as superseded and U-2/U-4 … U-10 as still effective;
- [`project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation.md`](project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation.md);
- [`phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md`](phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md), especially §§2–6 and its prerequisite matrix;
- the accepted D1-R2 launch-boundary decision and D2-R2 acceptance;
- `phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`, especially §§4.4.3, 6.5, 7.9, 9 and 11–15;
- `phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`, especially §§5.11–5.15, 6.2 and 6.3;
- the I-7 and I-7-R1 implementation reviews and acceptance;
- `docs/operations/disposable-test-server.md`; and
- the current evidence manifest, launcher sources and relevant tests, without
  treating them as execution authority.

Distinguish static-launcher H-1 and R-5 from unrelated findings and package
RAID items with the same short names.

## Required design amendment

The proposal must be exact enough for independent security and operations
review. It must address all of the following.

### 1. One-host topology and trust boundaries

- Define `oracle-test` as both H-1 installation host and later local
  test/evidence host.
- Bind the operator to the existing `ubuntu` account, subject to a later
  read-only identity preflight.
- Remove any requirement for SSH or rsync from a separate controller during
  the evidence pass. Identify any pre-pass synchronization that remains and
  keep it outside the trusted execution path.
- Trace every process, file, credential, descriptor, environment source and
  privilege transition from the operator request through the evidence entry.
- Reassess every assumption whose truth depended on controller and target
  being different hosts. Do not merely replace hostnames.
- State mechanically that the production server is neither inspected nor a
  source, destination, controller, fallback or rollback target.

### 2. Installation, activation and standing authority

- Resolve U-8: H-1 must not leave a usable Polkit start grant before the later
  pass authorization. Specify the exact staged/inert and activation states,
  which files exist in each state, who changes state, and the separate
  authority required.
- Amend the present five-file H-1 model explicitly rather than silently
  contradicting it.
- Specify exact target paths, owners, groups, modes, parent-directory
  requirements, ACL and file-capability rules for every installed or staged
  file.
- Define fail-closed pre-existing-path handling, atomic installation order,
  temporary names, rename semantics, partial-failure handling and whether
  rollback is automatic or separately authorized.
- Ensure no stage starts, stops or enables the unit and no stage can execute an
  evidence pass without the later explicit authorization.

### 3. H-1 record and H-2 comparison

- Resolve U-7 with a canonical record identifier, schema, deterministic
  serialization, destination, owner/group/mode, digest procedure and explicit
  A-2/H-2 binding.
- Include the complete effective unit-property and manager-default baseline
  that H-2 later re-reports, as well as `FragmentPath`, empty `DropInPaths` and
  `NeedDaemonReload=no`.
- Include all launcher, D9-2, PO-17, PO-18 and package-version facts required
  by D2 §5.11 and C11 §4.4.3.7.
- Define the PO-17 `binfmt_misc` matching algorithm mechanically.
- Record no environment content or secret values.

### 4. Host facts and citations

- Define the later read-only H-0 fact set for `oracle-test`: stable host
  identity, `ubuntu` identity, architecture/kernel, PID 1, systemd, polkit,
  glibc and CPython versions and package provenance, required binaries,
  target/parent-path state, unit/drop-in collisions and read-only
  `binfmt_misc` state.
- Define exact permitted command classes without supplying an executable H-0
  assignment in this task.
- Preserve the rule that no environment content, secrets, application data,
  database state or retained R4/R5 paths are inspected.
- Incorporate U-9 as a numbered, version-specific glibc/dynamic-loader proof
  obligation.
- Order D9-1, PO-8, PO-11, PO-12, PO-14 and PO-15 citation work after H-0;
  put PO-14 first where possible, because refutation withdraws LB-2S for that
  systemd version.

### 5. Launcher source and local build

- Apply U-4 to `oracle-test`: specify how a later separately authorized pinned
  rebuild becomes the installation source and is verified against
  `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572`,
  `expected.sha256`, the manifest and the accepted R5/D9-3 record.
- Keep retained R5 output as evidence, not an implicit installation source.
- Explain how build/staging paths remain distinct from installed paths and
  from retained evidence, and how cleanup authority remains separate.

### 6. Failure, rollback and terminal states

- Define the design-level PASS, INVALID RUN and HARD STOP boundaries for H-1.
- Define rollback for every mutation state, digest-guarded against removing an
  unrelated pre-existing file, followed by only the required
  `daemon-reload`; never touch a capture root, database or production host.
- Address reboot, package-version drift, kernel/systemd updates and a changed
  `ubuntu` identity or repository ownership.

### 7. Decisions, slices and traceability

- Give exact proposed wording for the remaining C11 M-/D-decisions needed to
  fix implementation bytes; do not claim blanket acceptance from U-6.
- State which earlier C11/D2 paragraphs are replaced, amended or retained.
- Provide a requirement-to-design traceability table covering U-1 through
  U-10, P-1 through P-10 from the preparation handback, D9-1 through D9-4,
  PO-8, PO-11, PO-12, PO-14, PO-15, PO-17 and PO-18.
- Provide bounded successor slices and their review gates. Separate H-0,
  citation work, repository implementation, launcher build/staging, H-1
  preparation, H-1 execution and H-2.

## Required outcome

Return one of:

- **DESIGN READY FOR REVIEW:** a complete proposed amendment satisfying every
  item above, still inactive; or
- **BLOCKED DESIGN:** exact unresolved contradictions or missing maintainer
  decisions, with the smallest safe successor needed to resolve each one.

Do not choose a new authorization, credential, architecture, rollback or
evidence semantic that Peter has not decided. Clearly distinguish a proposed
design from an accepted one.

## Handback contents

The output must include:

- outcome and concise recommendation;
- requirements and exact governing sections examined;
- the complete proposed amendment or blocking analysis;
- assumptions invalidated by the one-host topology;
- decisions preserved, superseded and still required;
- files created or changed;
- commands/checks run and exact results;
- checks not run and why;
- security, production-isolation, operational and rollback implications;
- proposed independent-review focus; and
- an explicit statement that no host, implementation or execution authority
  was used.

Stop after writing the repository-only proposal. Do not update current status,
Handover or §20; Codex records the return after independent review.

