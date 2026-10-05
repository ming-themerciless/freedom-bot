# Claude task — remediate the `oracle-test` one-host H-1 design

Work ID: `C-P5.0-R5-RP11-H1-D3-R1`  
Assignee: Claude  
Scope: repository documentation and read-only repository inspection only  
Output: revise
`docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`
in place and add a clearly dated **D3-R1 remediation and handback** section

## Objective

Remediate exactly the two Blocking findings in Codex's independent review of
the one-host design:

1. `OH-H1-D3-1` — the H-1 publication journal cannot recover every final path
   created immediately before a crash or journal failure; and
2. `OH-H1-D3-2` — ACT/DEACT lacks the mechanical publication, identity,
   record, partial-failure and automatic-cleanup contract required by U-8.

Incorporate Peter Duscha's accepted OH-D-1 through OH-D-9 dispositions. Return
a revised, still-inactive design for independent Codex re-review. Do not begin
H-0, implementation or any host step.

## Governing inputs

Read the canonical repository instructions and current-state documents first,
including the active restriction banner. Then read completely:

- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-authority.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md`](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md);
- [`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md);
- the original D3 authority and prompt;
- the accepted D1-R2, D2-R2, I-7 and I-7-R1 records cited by the proposal;
- the C11 and D2 proposals in the sections cited by the proposal;
- the H-1 preparation handback and prerequisite decisions; and
- `docs/operations/disposable-test-server.md`.

Treat the decision record as authoritative for OH-D-1 through OH-D-9. Do not
reopen those choices or silently weaken them.

## Accepted decisions to incorporate

The remediation must reflect all nine accepted dispositions, especially:

- the current workspace host is production and is never a source, controller,
  relay, destination, fallback or rollback target;
- later repository retrieval is direct from the canonical Git remote on
  `oracle-test`, with public access if available and any required read-only
  credential subject to separate authority;
- operator and executor processes run locally on `oracle-test` as `ubuntu`;
- the capture root is local and its loss of observer independence is explicit;
- synchronization/retrieval is outside Pass A and the trusted path;
- `NoNewPrivileges=yes` remains, and the identified privileged Pass A acts are
  `not_run`;
- ST-1 is an authority boundary, not privilege-inert against `ubuntu`;
- A-2 authorizes ACT for one pass and one boot, and DEACT is mandatory and
  automatically authorized at every terminal state;
- H-1 installation rollback remains separately authorized, while activation
  cleanup is automatic and removes both the active Polkit rule and
  `pass-a.json`; and
- the retained file on `oracle-test` is authoritative, with SHA-256 and byte
  length binding every returned copy.

## Required remediation

### 1. Crash-consistent H-1 publication and recovery (`OH-H1-D3-1`)

Replace the current `link(T, P)` followed by `created P ...` journal ordering
with an exact crash-consistent protocol. It must specify, for every file and
directory mutation:

- the durable intent recorded before mutation;
- the identity, digest, owner, mode and intended final path bound by that
  intent;
- file-data, journal and parent-directory fsync ordering;
- the namespace operation and its no-replace semantics;
- the durable completion/commit record;
- recovery after a stop at every boundary, including immediately before and
  after the final name appears;
- how recovery proves that a final or temporary path belongs to this run
  without removing an unrelated pre-existing path;
- how an unverifiable path is classified, retained and escalated;
- exact ST-0.x/ST-1 terminal-state mapping; and
- which recovery actions are part of the separately authorized H-1 rollback.

Do not solve the finding by weakening pre-existing-path refusal, deleting
uncertain paths, treating the crash window as residual risk, or automatically
rolling back H-1 contrary to OH-D-8.

The revised design must explicitly prove that a future H-1 is not permanently
blocked by a path the accepted recovery protocol can safely attribute, while
still refusing to remove anything it cannot attribute.

### 2. Complete ACT/DEACT contract (`OH-H1-D3-2`)

Specify ACT and DEACT at the same mechanical level as H-1. Include:

- deterministic activation identifier grammar and one-pass/one-boot binding;
- activation run/evidence paths, owners, groups and modes;
- a closed activation-record schema, canonical serialization, destination,
  SHA-256 and byte-length rules;
- exact binding to A-2, the H-1 and H-2 records, boot ID, `pass-a.json`, the
  staged rule and the active rule;
- fail-closed handling of every pre-existing target and temporary path;
- crash-consistent publication and recovery using the corrected protocol from
  item 1;
- exact partial states for failure before, between and after publication of
  `pass-a.json`, the active rule and the activation record;
- automatic, pre-authorized cleanup at ACT failure and every pass terminal
  state, removing both activation files when their identities are proven;
- mandatory ordering that disables the live grant first;
- handling when either path cannot be safely attributed or removed;
- retained immutable success/failure/cleanup evidence after activation files
  are removed;
- post-cleanup verification of ST-1; and
- reboot, process death and repeated/incomplete DEACT behavior.

The design must distinguish automatic **activation cleanup**, which Peter has
decided, from separately authorized **H-1 installation rollback**. It must not
leave `pass-a.json` for a later authority after an ACT failure. It must not
claim that a live rule has been removed unless durable evidence and a
post-check establish that result.

### 3. Consistency repair

Update every affected section, table and traceability row in the proposal so
that it agrees with the corrected protocol and accepted decisions. At minimum
reconcile:

- the outcome and recommendation;
- OH-D-1 through OH-D-9, marking them decided rather than open;
- ST-0.x, ST-1.x, ST-2 and ST-3;
- H-1 publication, terminal states and RB-1;
- ACT, DEACT and activation records;
- A-2/H-2/H-2b ordering;
- successor slices and gates;
- the requirement-to-design traceability table;
- security, production-isolation, operational and rollback implications; and
- the list of decisions still required.

Preserve a clear change history: do not erase the original BLOCKED DESIGN
analysis or make it appear that D3 initially contained the remediation. The
new D3-R1 section must state exactly which earlier paragraphs it replaces or
amends.

## Validation required

This is a documentation-only task. Perform repository-local, read-only
consistency checks sufficient to show that:

- every occurrence of OH-D-1 through OH-D-9 has the accepted disposition;
- no text still describes the production server as a possible source;
- no text leaves `pass-a.json` after ACT failure;
- every activation terminal path reaches verified ST-1 or reports a precise
  HARD STOP with the live grant disabled if its identity can be proven;
- H-1 rollback is never made automatic;
- no host command, executable H-0/H-1 assignment or implementation is added;
  and
- Markdown and repository diff checks pass.

Do not run project test suites: no implementation is authorized or changed.

## Required outcome

Return one of:

- **DESIGN REMEDIATION READY FOR RE-REVIEW:** both Blocking findings are
  addressed mechanically and the revised proposal is internally consistent;
  or
- **BLOCKED REMEDIATION:** identify the exact remaining contradiction or
  missing maintainer decision and the smallest safe successor needed.

Do not declare either finding closed. Only Codex may recommend closure after
independent re-review, and Peter retains acceptance authority.

## Handback contents

The revised proposal's D3-R1 section must include:

- outcome and concise recommendation;
- the requirements and governing sections examined;
- exact disposition of `OH-H1-D3-1` and `OH-H1-D3-2`;
- the corrected publication/recovery and ACT/DEACT contracts;
- affected sections, tables and successor slices;
- files changed;
- commands/checks run and exact results;
- checks not run and why;
- security, production-isolation, operational and rollback implications;
- proposed independent-review focus; and
- an explicit statement that no host, network, credential, implementation or
  execution authority was used.

Stop after writing the repository-only remediation return. Do not update
current status, Handover, §20, the decision register or the active restriction;
Codex records the result after independent re-review.
