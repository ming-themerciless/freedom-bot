# Claude task — remediate the remaining one-host activation-cleanup defects

Work ID: `C-P5.0-R5-RP11-H1-D3-R3`

Assignee: Claude

Scope: repository documentation and read-only repository inspection only

Output: revise
`docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`
in place and add a clearly dated **D3-R3 remediation and handback** section

## Objective

Remediate exactly the two Blocking findings in Codex's D3-R2 independent
re-review:

1. `OH-H1-D3-R2-1` — periodic observation leaves the Polkit grant live for a
   normal interval after the pass process has reached its terminal state; and
2. `OH-H1-D3-R2-2` — grant-priority mode removes the rule but intentionally
   leaves attributable `pass-a.json` and tree P indefinitely when evidence
   remains unwritable.

Preserve the accepted OH-D-1 through OH-D-9 dispositions, the closed
`OH-H1-D3-1` publication/recovery work, and the D3-R2 boot-cleared `/run` plus
PID-1 supervision direction that held. Return a revised, still-inactive design
for independent Codex re-review. Do not begin H-0, implementation or any host
step.

## Governing inputs

Read the canonical repository instructions and current-state documents first,
including the active restriction banner. Then read completely:

- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3-authority.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md);
- [`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md), including D3-R1 and D3-R2;
- the D3-R2 authority and prompt;
- the accepted C11 and D2 proposal sections cited by D3-R2; and
- `docs/operations/disposable-test-server.md`.

Treat the accepted decision and prior closure as authoritative. Do not reopen
OH-D-1 through OH-D-9, `OH-H1-D3-1`, the D3-R1 write-ahead publication
protocol, separately authorized RB-1, or D3-R2's boot-cleared activation-file
placement unless a direct contradiction makes the return **BLOCKED
REMEDIATION**.

## Required remediation

### 1. Couple cleanup to the pass terminal transition (`OH-H1-D3-R2-1`)

Replace polling as the mechanism claimed to establish the post-pass grant
boundary. The design must satisfy the accepted OH-D-7 statement literally:
no live Polkit grant may remain after the pass.

Specify a mechanical coupling in which the pass terminal transition itself
triggers or includes grant-first cleanup. Address at least:

- normal exit, early failure, signal death, timeout and operator interruption;
- the exact systemd unit relationship and ordering, including which process
  or unit owns the terminal transition;
- behavior if the cleanup process cannot execute, is killed or times out;
- whether the capture unit may be reported terminal before the grant is
  disabled;
- how the holder, `ExecStopPost=`, backstop and any remaining observation fit
  together without two concurrent cleanup owners;
- the exact state transition at which the pass is terminal and the evidence
  proving the grant is already absent at that point; and
- the version-bound PO-21 facts and corresponding H-0 observations required
  for every systemd behavior used.

Polling may remain only as a recovery/backstop mechanism. Do not solve the
finding by increasing the polling rate, describing the exposure as bounded,
or redefining an already-terminal capture process as still running merely
because cleanup has not happened. If the platform cannot mechanically satisfy
the accepted absolute boundary, return **BLOCKED REMEDIATION** and identify
the smallest exact maintainer decision needed; do not weaken OH-D-7.

### 2. Complete automatic cleanup when evidence is unwritable (`OH-H1-D3-R2-2`)

Amend grant-priority mode so that, after it removes and post-checks an
A1-intact live rule, it also safely and automatically removes attributable
`pass-a.json` and activation directories. The design must cover:

- failure to create an attempt directory or journal;
- journal write or fsync failure before and after grant removal;
- identity/digest re-verification immediately before each removal;
- an unlink or directory-removal failure;
- repeated and concurrent stop-post/backstop attempts;
- what can and cannot be claimed without a durable removal record;
- the exact ST-1/ST-1+R result when cleanup succeeds but evidence cannot be
  persisted; and
- how a later attempt or attestation distinguishes “removed without a record”
  from a foreign or damaged object without deleting anything unrelated.

Evidence failure may reduce what the record claims; it must not cause an
otherwise attributable activation object to be left indefinitely. An
unverifiable or foreign object remains retained and escalated under the
existing fail-closed rules.

### 3. Consistency repair

Update every affected state table, event matrix, proof, traceability row,
successor slice, validation claim and security/operational implication. At a
minimum reconcile §4.2.5-R2(g) through (n), the D3-R2 latency statement, GP,
the pass-terminal rows, PO-21, OH-S4/OH-S8b and §13. Preserve history by
labelling superseded D3-R2 text and adding a new D3-R3 section; do not make it
appear that D3-R2 originally contained the correction.

## Validation required

This is a documentation-only task. Perform repository-local, read-only
consistency checks sufficient to show that:

- no governing text relies on polling to establish the post-pass grant
  boundary;
- no normal or failure path reports the pass terminal while an attributable
  grant remains live;
- evidence-write failure never leaves an A1-intact `pass-a.json` or activation
  directory solely because a write-ahead record cannot be created;
- success is never claimed without the required durable evidence and
  post-check;
- `/run` boot clearing, automatic process-death cleanup and separately
  authorized RB-1 are preserved;
- OH-D-1 through OH-D-9 and the accepted D3-R1 publication protocol are not
  weakened;
- no host command, executable assignment or implementation is added; and
- Markdown and repository diff checks pass.

Do not run project test suites: no implementation is authorized or changed.

## Required outcome

Return one of:

- **DESIGN REMEDIATION READY FOR RE-REVIEW:** both R2 findings are addressed
  mechanically and the revised proposal is internally consistent; or
- **BLOCKED REMEDIATION:** identify the exact remaining contradiction or
  missing maintainer decision and the smallest safe successor needed.

Do not declare `OH-H1-D3-2`, `OH-H1-D3-R1-1`, `OH-H1-D3-R2-1` or
`OH-H1-D3-R2-2` closed. Only Codex may recommend closure after independent
re-review, and Peter retains acceptance authority.

## Handback contents

The revised proposal's D3-R3 section must include:

- outcome and concise recommendation;
- requirements and governing sections examined;
- exact disposition of both R2 findings;
- the corrected pass-terminal coupling and evidence-unwritable cleanup
  contracts;
- affected sections, tables, proof obligations and successor slices;
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
