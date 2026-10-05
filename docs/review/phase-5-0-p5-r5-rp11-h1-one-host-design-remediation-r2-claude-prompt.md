# Claude task — remediate death/reboot activation cleanup in the `oracle-test` one-host H-1 design

Work ID: `C-P5.0-R5-RP11-H1-D3-R2`

Assignee: Claude

Scope: repository documentation and read-only repository inspection only

Output: revise
`docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`
in place and add a clearly dated **D3-R2 remediation and handback** section

## Objective

Remediate exactly Blocking finding `OH-H1-D3-R1-1`: D3-R1 defers cleanup
after process/session loss or reboot until a later actor reaches the host,
allowing a Polkit grant authorized for one pass and one boot to remain live
after that pass or in a later boot.

Preserve the accepted OH-D-1 through OH-D-9 dispositions and the D3-R1
publication/recovery contract. Return a revised, still-inactive design for
independent Codex re-review. Do not begin H-0, implementation or any host step.

## Governing inputs

Read the canonical repository instructions and current-state documents first,
including the active restriction banner. Then read completely:

- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2-authority.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md);
- [`project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md`](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md);
- [`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md), including D3-R1;
- the D3-R1 authority and prompt;
- the accepted D1-R2, D2-R2, I-7 and I-7-R1 records cited by the proposal;
- the C11 and D2 proposals in the sections cited by the proposal; and
- `docs/operations/disposable-test-server.md`.

Treat the decision record as authoritative. Do not reopen OH-D-1 through
OH-D-9, `OH-H1-D3-1`, or the D3-R1 write-ahead publication and separately
authorized RB-1 design.

## Required remediation

Replace D3-R1's deferred human-first-action cleanup after death, session loss
or reboot with an exact fail-closed design that enforces all of these
conditions:

1. A-2 authorizes `ACT` for exactly one pass and one boot.
2. No live Polkit grant exists before A-2 or remains after the pass.
3. Loss of the ACT/pass process, loss of the interactive session, power loss
   and reboot do not depend on a later human action to disable the grant.
4. The live grant is disabled first; `pass-a.json` is then removed.
5. Cleanup is automatic under A-2 and remains distinct from separately
   authorized H-1 rollback RB-1.
6. No cleanup claims success without durable evidence and a post-check.

Choose the smallest defensible mechanism. A boot-cleared active-rule location,
an automatically invoked startup cleanup mechanism, or another design may be
proposed, but Claude must not assume unsupported Polkit or systemd behavior.
Any mechanism-dependent behavior must be tied to a version-bound citation or
an explicit H-0/PO proof obligation and must fail closed if that obligation is
not met. If no mechanism can satisfy the contract without a new maintainer
choice, return **BLOCKED REMEDIATION** with the exact choice and smallest safe
options instead of silently choosing.

Specify the selected design at the same mechanical level as D3-R1, including:

- paths, owners, groups, modes, identities and digests;
- publication/removal ordering and filesystem durability boundaries;
- how the mechanism is installed or staged without creating a standing grant;
- binding to A-2, activation ID, pass ID, H-1/H-2 records and boot ID;
- behavior at every boundary before and after the live grant appears;
- process death, session loss, power loss and reboot at every activation state;
- repeated, interrupted and concurrent cleanup;
- how a foreign, damaged or unverifiable object is retained and escalated;
- the exact ST-1/ST-1+R terminal mapping;
- immutable success, failure and cleanup evidence, including what survives a
  reboot and how returned copies are digest/length bound under OH-D-9;
- version-bound PO-11/PO-20 facts and the corresponding H-0 observations;
- implementation and crash-injection tests required in a later authorized
  slice; and
- rollback/recovery consequences without making RB-1 automatic.

Explicitly withdraw or replace residual RR-2 and every statement that cleanup
after death or reboot waits for the next actor. Reconcile AC-10, the “When it
runs” list, the state tables, §4.3.4 ordering, §4.6.3 reboot behavior,
traceability, successor slices, security/operational implications and the
review-focus list.

## Validation required

This is a documentation-only task. Perform repository-local, read-only
consistency checks sufficient to show that:

- no governing text permits the active grant to survive the authorized pass
  or boot pending later human action;
- every death, session-loss, power-loss and reboot boundary reaches verified
  ST-1 or a precise ST-1+R HARD STOP without an attributable live grant;
- `pass-a.json` cleanup remains automatic;
- H-1 rollback remains separately authorized and never automatic;
- OH-D-1 through OH-D-9 and the accepted D3-R1 publication protocol are not
  weakened;
- no host command, executable assignment or implementation is added; and
- Markdown and repository diff checks pass.

Do not run project test suites: no implementation is authorized or changed.

## Required outcome

Return one of:

- **DESIGN REMEDIATION READY FOR RE-REVIEW:** `OH-H1-D3-R1-1` is addressed
  mechanically and the revised proposal is internally consistent; or
- **BLOCKED REMEDIATION:** identify the exact remaining contradiction or
  missing maintainer decision and the smallest safe successor needed.

Do not declare `OH-H1-D3-2` or `OH-H1-D3-R1-1` closed. Only Codex may
recommend closure after independent re-review, and Peter retains acceptance
authority.

## Handback contents

The revised proposal's D3-R2 section must include:

- outcome and concise recommendation;
- requirements and governing sections examined;
- exact disposition of `OH-H1-D3-R1-1`;
- the corrected automatic cleanup contract;
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
