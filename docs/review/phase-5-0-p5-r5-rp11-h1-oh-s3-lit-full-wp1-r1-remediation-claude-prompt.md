# Claude prompt — LIT-FULL WP-1 independent-review remediation R1

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R1-20261007-10`

## Authority and objective

Peter Duscha authorizes repository-only remediation of the two findings in
`project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1.md`:

- **WP1-R1, Blocking:** the four current-state pointers omit mandatory §0.2
  change control before WP-2 may rely on either recommended BC-4 exception; and
- **WP1-R2, Important:** the original executor did not read the accepted
  cumulative R8 proposal completely as the exact prompt required.

Produce one self-contained cumulative WP-1 R1 remediation proposal and durable
handback. Do not edit or replace the original WP-1 proposal or handback. Do not
decide BQ-2 or BQ-3, approve BC-4, open §0.2 change control or authorize WP-2.

## Required complete reading

Before drafting or editing anything, read **each file below completely, from
first byte through EOF**. Targeted searches and selected sections are not a
substitute. Record line counts and SHA-256 digests in the handback as evidence
that each complete file was the reviewed version.

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md`;
5. `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1.md`;
6. `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
7. `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1-authority.md`;
8. `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-claude-prompt.md`;
9. `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-boundary-proposal.md`;
10. `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-handback.md`;
11. `phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`;
12. `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md`;
13. `phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`; and
14. `phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`.

Items 5 through 14 are under `docs/review/`. Do not claim completion until all
fourteen reads have reached EOF. If tool output truncates, continue in bounded
chunks. If any file is missing, unreadable, internally inconsistent in a way
that prevents remediation, or differs from the identity named by its authority,
write the handback with a precise `HARD STOP` and make no substantive proposal.

## Deliverables

Create only these new durable deliverables:

1. `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-proposal.md`;
2. `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-handback.md`.

Also update only the four current-state pointers on return:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- implementation-plan §20 only; and
- the restriction banner only in
  `docs/operations/disposable-test-server.md`.

Do not edit the independent review, G-1 decision, authority, exact prompts,
accepted R8/R2 records, original WP-1 deliverables, registers, archive indexes
or historical snapshots.

## Required remediation

### 1. Close WP1-R1 without changing the boundary

The cumulative proposal must make the successor gate exact:

- independent Codex re-review and Peter's recorded BQ-2/BQ-3 decisions are
  always necessary;
- if either chosen answer contains an LR exception, including EX-1 or EX-2
  under BC-4, the complete implementation-plan §0.2 change-control process must
  close **before WP-2 may be prompted, authorized or rely on that boundary**;
- a Peter decision on BQ-2/BQ-3 is not by itself §0.2 approval;
- if Peter retains literal no-exception LIT-FULL, WP-2 remains blocked until a
  separately authorized, reviewed loader-free privileged-start design makes
  the boundary attainable, or Peter withdraws the affected design; and
- BC-2 remains explicitly unresolved for any later WP-9 selection unless the
  complete-record audit establishes that an accepted decision already resolves
  it. Do not infer such a decision.

Show the decision/gate flow in a compact table. Carry the same exact gate into
all four current-state pointers. They must say **changes requested** and must not
describe WP-1 as accepted or BQ-2/BQ-3 as decided.

### 2. Close WP1-R2 through a complete-record audit

After the required complete reads, re-audit every substantive claim in the
original WP-1 return. The cumulative remediation proposal must:

1. enumerate the final proposed root-procedure and `sudo`-started-path sets,
   explicitly disposing of OS-6, H-1R, AP-2, `attest`, H-1, RB-1 and RS-1;
2. verify every caller, first image, controlled-image status and DI-1 through
   DI-6 mapping against the complete accepted record;
3. distinguish accepted fact, textual observation and new recommendation;
4. state whether the complete reading adds, removes or changes any original
   WP-1 claim, and give an exact old-to-new correction table;
5. restate BQ-2 and BQ-3 alternatives and recommendations in plain language,
   but keep both pending Peter's decision;
6. state every LR exception, §0.2 change, new design package and downstream WP
   dependency each alternative requires;
7. resolve the original review questions Q-1 through Q-6 where the accepted
   record permits; where it does not, convert the question into an exact Peter
   decision or separately authorized investigation rather than leaving an
   ambiguous reviewer question;
8. correct the original checklist's reference to "three" questions when it
   lists six, and provide a complete remediation acceptance checklist; and
9. preserve the commissioned facts: BQ-1 is R3-ROOT for investigation, BQ-4
   permits no dynamic child, concrete Route 3 remains unestablished, and WP-2
   through WP-7 remain separately gated.

Do not perform WP-2's system-call-intent inventory. A minimal boundary mapping
of already accepted DI delegations is allowed; no implementation inventory,
protocol design or new external citation is authorized.

### 3. Return state

If the audit succeeds, use terminal text
`WP-1 R1 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`.

The handback must list:

- every file created or changed;
- the complete-read evidence requested above;
- exact proposal byte count and SHA-256;
- checks performed and exact results;
- all changes from the original WP-1 proposal;
- unresolved Peter decisions and governance gates;
- checks not run; and
- an explicit statement that no prohibited operation occurred.

## Prohibited work

Do not use SSH or connect to any host. Do not access retained evidence, secrets,
credentials, player data, production, staging, `oracle-test`, Foundry or a
database. Do not perform network research, package operations, installation,
implementation, configuration or infrastructure edits, launcher work, builds,
tests, formatters, service/database operations, cleanup, workspace recreation,
OH-S4/OH-S4p or later work, H-1/H-2, activation, rollback, commit or push.

Do not open or execute §0.2 change control, approve a baseline change, make a
Product Owner decision, accept the proposal or create WP-2 authority. Do not
edit anything outside the explicitly permitted deliverables and four pointer
locations. A conflict with these limits is a `HARD STOP`, not permission to
expand scope.

## Review gate

The return accepts nothing. Independent Codex re-review is mandatory. Peter's
later recorded BQ-2/BQ-3 decisions, and §0.2 closure if an exception path is
chosen, are required before WP-2 can be prepared or authorized.

