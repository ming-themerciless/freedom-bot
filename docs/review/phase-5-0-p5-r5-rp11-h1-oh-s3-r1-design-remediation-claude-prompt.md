# Claude prompt — OH-S3 R1 activation and Route 3 design remediation

Status: **authorized by Peter Duscha on 2026-10-07, subject to the matching
authority record and prompt identity pin**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R1-20261007-01`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-claude-prompt.md. Produce one cumulative decision-ready proposal that repairs the activation design for PO-20(f), PO-21(c), PO-21(s) and PO-11(d), replaces rejected Route 1 with a concrete Route 3 design, and defines the gated MF-1 through MF-8 and OH-S4p follow-on plan. Do not access any host, retained evidence, secret, credential or player data; do not implement, build, test, clean, activate, commit or push. Stop after the durable proposal, handback and current-state pointers are ready for independent Codex review.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only design-remediation assignment. The matching authority record
pins this prompt's byte count and SHA-256.

This assignment ends at `OH-S3 R1 DESIGN REMEDIATION READY FOR REVIEW` or its
first defined `HARD STOP`. It creates no acceptance and no successor authority.
Independent Codex review and Peter's later recorded decision are mandatory.

No SSH or other host connection, `oracle-test`, production, staging, Foundry or
database access, retained-evidence access, secret, credential or player-data
access, network research, package operation or installation, implementation or
configuration edit, launcher retarget or rebuild, application test, build,
service/database mutation, repository or host cleanup, workspace recreation,
OH-S4p or later slice, H-1/H-2, activation, rollback, commit or push is
authorized.

## Required reading and initial checks

Before editing, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 14, 16, 17 and 20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. the accepted cumulative OH-S2 R2 citation record, R2 handback and R2
   acceptance;
6. the accepted cumulative R3 H-0 completeness proposal and acceptance;
7. the cumulative one-host design amendment, especially §§4.1–4.7 and its
   D3-R6 cumulative amendments;
8. the operational draft
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
   as the future consumer, without editing it;
9. the accepted C11 launcher contract and relevant D2 records cited by the
   one-host design; and
10. the R1-F1 residual-risk acceptance only for current closure state.

Inspect `git status` and preserve unrelated changes. Verify this prompt's exact
byte count and SHA-256 against its authority before any edit. A mismatch is
`HARD STOP: OH-S3 R1 prompt identity mismatch`.

Do not use recursive searches rooted at the repository, a workspace root, the
user's home, `/opt`, `/var`, `/tmp` or `/`. Search only exact named documents
or explicit safe tracked-file allowlists. Never read or test a secret-bearing
path.

## Required design outcome A — repaired activation design

Produce a closed replacement design for the accepted activation mechanism that
addresses all four returned items without weakening LB-2S, A-2, the start-only
grant, one-start-attempt rule, no-follow source-consumption contract, evidence
durability, or fail-closed boundaries:

1. **PO-20(f):** replace every assumption that a lock is released when a
   process ends with the correct last-reference-to-open-file-description rule.
   Specify descriptor ownership, inheritance prevention, close points and
   failure behavior so no longer-lived process can retain the lock.
2. **PO-21(c):** remove any claim that `ExecStopPost=` runs for every cause.
   Design the independent recovery/backstop path for cases where PID 1 cannot
   spawn it, and state which failure remains outside the authorized guarantee.
3. **PO-21(s):** replace strict or every-transition timestamp assumptions with
   a valid discriminator. Define exactly how attempts, inactive/failed states,
   `reset-failed`, reload/re-exec and same-microsecond observations are handled.
4. **PO-11(d):** do not invent a Polkit reload-time bound and do not poll
   indefinitely. Choose and justify a finite fail-closed design for `ACT`,
   consume, `DEACT`, backstop and verification. Separate an operational timeout
   from any claim about Polkit internals.

The proposal must include revised state machines, terminal-cause tables,
authority windows, recovery ownership, evidence records, invariants, negative
tests and exact amendments needed in the one-host design and operational draft.
It must state whether any accepted decision needs Peter to choose among options;
where a choice is unavoidable, provide a recommendation and bounded alternatives
rather than silently choosing.

## Required design outcome B — concrete Route 3

Replace rejected Route 1 with a concrete Route 3 design. Route 3 must eliminate
the ambient CPython-startup dependency refuted by PO-12/AS-8, including
`PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__`, `MIMALLOC_*`, manager-global
environment inputs and dynamic-loader inputs for root helper processes.

The proposal must:

1. define the executable/runtime boundary for the entry, consume helper,
   holder, `ExecStopPost=` helper and backstop;
2. inventory every accepted Role A–H occurrence previously tied to
   `/usr/bin/python3.12` or `/usr/bin/python3.14` and give its Route 3
   disposition;
3. specify reproducible source, build, pinning, digest, ownership, installation,
   update, rollback and drift contracts without performing them;
4. preserve the C11 launcher, D9 and I-7 security objectives and identify every
   claim that needs re-review;
5. decide whether PO-12′ and PO-19 remain necessary under Route 3, and if so
   narrow them to their actual consumers;
6. define the byte-level PO-17/OH-S4p boundary for the proposed launcher image;
7. provide failure and recovery behavior for missing, altered, wrongly owned or
   incompatible Route 3 artifacts; and
8. compare the chosen Route 3 with at least one bounded alternative and explain
   why the recommendation has the smaller trusted/runtime surface.

Do not implement Route 3, change launcher bytes, edit service templates or
select a third-party artifact through new network research. If repository
evidence is insufficient to choose a safe concrete Route 3, return a
decision-ready set of exact alternatives and a `HARD STOP` rather than inventing
facts.

## MF-1 through MF-8 and successor gates

Create a complete fact-disposition table for MF-1 through MF-8. For each fact,
state whether Route 3 eliminates it, narrows it, leaves it unchanged or moves it
to another consumer. Define the minimum future observing slice, privilege,
exact-path scope, evidence, drift trigger and dependent gate. Do not collect any
fact.

Define the successor order and review gates for at least:

- any maintainer decision required by this proposal;
- operational-draft incorporation (OH-S3 successor if separately needed);
- Route 3 implementation and security review;
- OH-S4p byte-level launcher review;
- read-only MF fact collection;
- OH-S5/rebuild evidence where still applicable; and
- H-1 readiness.

No successor is authorized by naming it.

## Deliverables

Create:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-proposal.md`
   — a self-contained cumulative decision-ready proposal;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-handback.md`
   — the complete durable handback.

Update only these current-state pointers:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner in `docs/operations/disposable-test-server.md`.

Do not edit accepted historical evidence, the operational draft, source code,
tests, configuration, service files, migrations, archive snapshots, archive
indexes, the decision register or the change log.

The handback must report prompt identity, terminal state, requirements covered,
files changed, exact repository documents consulted, commands and checks, checks
not run, security implications, unresolved decisions and reviewer focus. It
must distinguish pre-existing changes and confirm no host, retained-evidence,
secret, network, implementation, build, test, cleanup, commit or push action.

Mark the authority and prompt consumed in all four pointers. Do not claim Codex
or Peter acceptance and do not authorize or propose activation of a successor.

## Verification

Run only bounded local documentation checks:

- recompute prompt byte count and SHA-256 before work and at handback;
- verify links introduced in the six allowed files by explicit target list;
- check trailing whitespace in the six allowed files;
- run `git diff --check` only for the four tracked pointer files and the two new
  deliverables;
- compare every returned item and MF identifier against the accepted R2 record;
- verify that the proposal contains no command or language granting host,
  implementation, cleanup, activation, commit or push authority; and
- review the six-file diff.

Do not run application tests, hook tests, formatters, builds, package tools,
network checks or remote-host checks.

End the handback exactly:

`OH-S3 R1 design remediation awaits independent Codex review; no host, implementation, cleanup, OH-S4p or later slice is authorized.`
