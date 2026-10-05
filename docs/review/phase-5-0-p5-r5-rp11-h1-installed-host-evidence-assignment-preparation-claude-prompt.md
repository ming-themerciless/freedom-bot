# Claude task — prepare the static-launcher H-1 installed-host evidence assignment

Work ID: `C-P5.0-R5-RP11-H1-A1`  
Assignee: Claude  
Scope: repository documentation and read-only repository inspection only  
Output: `docs/review/phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md`

## Objective

Prepare a decision-ready proposal for the static-launcher **H-1 installed-host
evidence step** that supplies D9-4 and establishes PO-17 and PO-18 at the
installation moment.

If, and only if, every prerequisite and installable input already exists and
can be bound exactly, write the proposed execution assignment to:

`docs/review/phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment.md`

If the repository is not ready for an exact, safely executable H-1 assignment,
do not fabricate one. Return a **BLOCKED PREPARATION** handback that identifies
every missing prerequisite, the authority and review gate needed to create it,
the required order, and the proposed path and scope of each bounded successor
assignment.

Do not access `oracle-test`, use SSH or rsync, install or remove anything,
invoke `systemctl`, inspect retained R4/R5 host paths, build a launcher, create
the pass configuration, alter repository implementation, commit or push.

## Governing inputs

Read the canonical instructions and current-state documents first. Then read
at least:

- `docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass-acceptance.md`;
- `docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass.md`;
- `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md`;
- `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`, especially §§5.11, 6.2, 6.3 and 12;
- `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`, especially §§4.4.3.4–4.4.3.7, 6.5, 7.9, 11–14;
- the accepted D1-R2 and D2-R2 decision/review records and implementation
  handbacks they cite;
- the current review manifest and concrete plan, without treating either as
  execution authority; and
- all repository files proposed for installation, their tests and their
  generating/binding code.

Keep the static-launcher H-1 distinct from unrelated findings or RAID entries
also named `H-1`, and keep static-launcher R-5 distinct from package RAID item
`P5.0-R5`.

## Mandatory readiness audit

Independently establish and report, with paths and exact evidence:

1. Whether each of the five H-1 inputs exists in reviewed repository form:
   the systemd unit, polkit rule, `rp11-launch`, bootstrap and pass
   configuration (or a deterministic, reviewed construction for the latter).
2. Whether the installable launcher bytes are available and are exactly the
   bytes accepted by D9-2/D9-3, including the expected SHA-256 and the binding
   to `expected.sha256`, the manifest and the accepted R5 record. A retained
   remote output is not silently a repository installation source.
3. Whether D9-1 is complete for the prospective installed kernel series, or
   what read-only host facts and source citations must precede mutation.
4. Whether PO-14 and PO-15 have sufficient version-specific citations and
   checks for the prospective installed systemd version. Do not infer them
   from the design alone.
5. Whether PO-8, PO-11 and PO-12 citations required by the H-1 record are
   complete for the relevant systemd, polkit, glibc and CPython versions.
6. Whether the exact target paths, owners, groups, modes, ACL/file-capability
   requirements, parent-directory requirements, unit properties, manager
   properties and package-version commands are fully specified.
7. Whether installation ordering, atomic replacement behavior, pre-mutation
   capture, failure handling and rollback are complete and compatible with
   the governing designs.
8. Whether the H-1 record has a canonical schema, serialization, destination,
   ownership/mode, digest procedure and later A-2/H-2 binding. The record must
   contain no environment content.
9. Whether a proposed H-1 run can avoid services/databases, capture roots,
   secrets, production data and any evidence-harness execution.
10. Every unresolved decision. Do not choose a path that changes architecture,
    authority, installation source, rollback or evidence semantics.

The initial repository inventory on 2026-10-04 found these expected paths
absent: `infra/systemd/rp11-capture-pass-a.service`,
`infra/polkit/50-freedom-blades-rp11.rules`,
`tools/phase_5_0_evidence/execution/rp11_entry.py`, and
`tools/phase_5_0_evidence/execution/entry_environment.py`; it also found no
committed `infra/rp11-launch/rp11-launch`. Verify this yourself and trace any
renamed or generated equivalent. Absence is a readiness fact, not permission
to implement the missing material in this task.

## Requirements if READY

Only if the audit establishes readiness, the proposed H-1 assignment must be
standalone and mechanically executable. It must:

- name one executor, one target host identity, one invocation, exact reviewed
  inputs with SHA-256 and byte lengths, exact commands and exact allowed
  substitutions;
- start with identity, repository-state, authority, prerequisite, target-path
  and pre-mutation checks, and stop before mutation on any mismatch;
- separate read-only prerequisite evidence from the explicit mutation point;
- install exactly the five approved files with their exact owners, groups and
  modes, using a fail-closed order that never exposes a partially usable unit;
- run only the necessary `systemctl daemon-reload` and read-only manager
  queries; it must not start, stop or enable the unit;
- verify the installed launcher digest against `expected.sha256`, the manifest
  and the pass configuration; verify owner `root:root`, mode `0755`, no
  set-ID bits, no file capability, no write-granting ACL, and root-owned,
  non-group/world-writable parents through `/`;
- establish PO-17 by checking every enabled `binfmt_misc` registration against
  the launcher's first 128 bytes using its magic, mask and offset, or record
  that `binfmt_misc` is not mounted;
- establish PO-18 by recording `x86_64`, the exact kernel release and that it
  is at least 5.9;
- record every launcher fact required by D2 §5.11, every installation fact
  required by D1-R2 §4.4.3.7, and the required version-specific citations;
- require `FragmentPath=/etc/systemd/system/rp11-capture-pass-a.service`, empty
  `DropInPaths`, `NeedDaemonReload=no`, and the exact effective properties
  specified by the accepted design;
- write the H-1 record deterministically, root-owned and non-writable by the
  operator, then report its SHA-256 for later A-2/H-2 binding;
- define PASS, INVALID RUN and HARD STOP precisely, with a complete handback
  and closing record for every terminal state;
- retain sufficient bounded evidence for independent Codex review without
  recording environment content or secrets;
- include exact rollback commands for all five installed files and
  `daemon-reload`, state when rollback is automatic versus separately
  authorized, and never touch a capture root; and
- explicitly state that H-1 does not authorize H-2, D9-5, PO-16, starting the
  unit, an evidence pass, RP-11 wiring, service/database mutation, cleanup of
  R4/R5 evidence, commit or push.

Include the resolved Gemini invocation for the proposed assignment, but label
it **proposed and inactive** until independent Codex review and Peter's later
acceptance/activation:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

## Handback

Write the handback whether the outcome is READY or BLOCKED PREPARATION. Report:

- the outcome and its evidence;
- requirements examined and exact governing sections;
- prerequisite matrix and dependency order;
- files created or changed;
- proposed assignment SHA-256 and byte length, if one is produced;
- commands/checks run and exact results;
- checks not run and why;
- security, operational and rollback implications;
- unresolved decisions and proposed reviewer focus; and
- an explicit statement that no host action or execution authority was used.

Stop after the repository-only handback. Codex independently reviews the
return; Peter alone may accept a successor assignment and activate an executor.
