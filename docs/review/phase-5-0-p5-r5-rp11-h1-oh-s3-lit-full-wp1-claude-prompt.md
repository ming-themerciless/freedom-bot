# Claude prompt — LIT-FULL WP-1 boundary proposal

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-20261007-09`

## Authority and objective

Peter Duscha has accepted DEC-1 through DEC-6 as recommended and commissioned
the LIT-FULL Route 3 readiness investigation recorded in
`project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`.

Execute **WP-1 only** from §9.5 of the accepted cumulative R8 proposal. Produce
a repository-only boundary proposal that states which procedures are in scope,
where each begins and whether any exception would be required. The proposal
must make BQ-2 and BQ-3 understandable and decision-ready for Peter. It must not
silently answer them on his behalf.

This assignment does not authorize WP-2 or any later package.

## Required reading

Before working, read completely:

1. `.agents/AGENTS.md`;
2. the reading map, §0, §16 and §20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
5. `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
6. the accepted R8 proposal, especially §§2.4, 4, 5, 7.5a, 9.1 through 9.7,
   11, 12 and 13; and
7. the R8 acceptance record and accepted OH-S2 R2 citation record linked from
   the active handover.

The accepted records are authority. Do not rewrite their findings, decisions,
citations, residuals or technical mechanisms.

## Fixed direction

- The investigated path is **LIT-FULL under R3-ROOT**, not LIT-DR1.
- BQ-1 is therefore recorded as R3-ROOT for this investigation: the
  `ubuntu`-run entry may remain Python and is outside the root-procedure set.
- LIT-FULL satisfies LR-1 through LR-6 literally. BQ-4 therefore permits no
  dynamic child in a root procedure's process tree. Do not introduce SCDC or
  another exception.
- SSW, SCDC and ACCEPT-X1 remain scope-change alternatives and are not selected.
- WITHDRAW remains available only as a later Peter decision; it is not this
  assignment's direction.

## Deliverables

Create:

1. `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-boundary-proposal.md`; and
2. `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-handback.md`.

The boundary proposal must:

1. enumerate every accepted root procedure implicated by R8 §9.1 and map its
   accepted name, caller, current first root image, controlled first image and
   relevant DI-1 through DI-6 delegation;
2. state the R3-ROOT entry boundary separately so no reader can mistake the
   `ubuntu` entry for a root procedure;
3. analyze BQ-2 for each `sudo`-started path, including `attest` and AP-2,
   showing the consequences of beginning the procedure at `sudo` versus at the
   first image controlled by the design;
4. analyze BQ-3 for H-1, RB-1 and RS-1, including the verified-exec stub and
   installer/removal actions, showing the consequences of including or
   excluding that class;
5. state a technically reasoned recommendation for BQ-2 and BQ-3, with an exact
   proposed boundary sentence Peter could approve, while marking both as
   **pending Peter's decision**;
6. identify every place where the recommendation would require an exception,
   baseline change or follow-on redesign. If an LR exception is required, stop
   and report it rather than treating it as approved;
7. record BQ-4 as no dynamic-child exception under the commissioned LIT-FULL
   direction and explain how that constrains WP-2 through WP-4;
8. provide a complete WP-1 acceptance checklist and an explicit list of inputs
   WP-2 may rely on only after Peter decides BQ-2 and BQ-3; and
9. distinguish statements derived from accepted repository text from new
   recommendations. Do not invent host facts or external citations.

Do not perform WP-2's system-call-intent operation inventory. A minimal list of
DI delegations needed to define boundaries is allowed; a new implementation
inventory is not.

On return, update only the four current-state pointers—`docs/review/Handover
information`, `docs/project-management/status.md`, implementation-plan §20 and
the disposable-server restriction banner—to say WP-1 returned and awaits
independent Codex review and Peter's BQ-2/BQ-3 decisions. Preserve all current
restrictions and archive links. Do not archive or delete prior evidence.

## Prohibited work

Do not use SSH or connect to any host. Do not access retained evidence, secrets,
credentials, player data, production, staging, `oracle-test`, Foundry or a
database. Do not perform network research, package operations, installation,
implementation, configuration edits, launcher work, builds, tests, formatters,
service/database operations, cleanup, workspace recreation, OH-S4/OH-S4p or
later work, H-1/H-2, activation, rollback, commit or push.

Do not edit application code, infrastructure code, accepted proposals,
acceptance records or historical snapshots. If required information is absent
or authorities conflict, write the handback with a precise `HARD STOP` and do
not infer an answer.

## Return and review gate

Return terminal text `WP-1 BOUNDARY PROPOSAL RETURNED` only when both deliverable
files and all four current-state pointer updates are complete and mutually
consistent. The handback must list files changed, checks performed, unresolved
questions and an explicit statement that no prohibited operation occurred.

The return does not accept the proposal. Independent Codex review and Peter's
recorded BQ-2/BQ-3 decisions are required before a separately prompted and
authorized WP-2 assignment.

