# Claude prompt — LIT-FULL WP-1 independent re-review remediation R4

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13`

## Authority and objective

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment. Remediate all three findings in
`project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md`:

- **WP1-R3R-1, Blocking:** the canonical B2-S matrix says both that B2-N replaces
  `sudo` and that `sudo` remains inside the resulting inventoried tree;
- **WP1-R3R-2, Blocking:** the compact gate says “4 or 4′” even for combinations
  that require both §0.2 closure and separate design prerequisites; and
- **WP1-R3R-3, Important:** superseded R3-authorization pointer text was kept only
  in an external scratchpad instead of a durable, indexed repository snapshot.

Produce one self-contained cumulative WP-1 R4 remediation proposal, the archival
erratum required below, and a durable handback. Do not edit or replace any earlier
WP-1 proposal, handback or review. Do not decide BQ-2 or BQ-3, approve an
exception, open or execute implementation-plan §0.2 change control, accept WP-1,
establish concrete Route 3 or authorize WP-2.

## Required complete reading

Before drafting or editing anything, read these files completely from first byte
through EOF. Targeted searches do not substitute for complete reads. Continue in
bounded, non-overlapping chunks if output is truncated.

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md`;
7. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md`;
8. `docs/review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-authority.md`;
9. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-claude-prompt.md`;
10. `docs/review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation.md`;
11. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
12. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`; and
13. `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`.

Record line counts, byte counts and SHA-256 digests for all thirteen files in the
handback. Also verify this prompt's byte count and SHA-256 against its separate R4
authority record before any edit. If a required file is missing, unreadable or
does not match the identity named by its authority, write the handback with a
precise `HARD STOP` and make no substantive proposal.

## Deliverables and permitted edits

Create only these new durable deliverables:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-handback.md`;
3. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md`.

On a successful return, update only these current-state locations:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 only of `docs/implementation-plan.md`; and
- the restriction banner only in `docs/operations/disposable-test-server.md`.

Also add one link to the R3 pointer-archive erratum in each of these existing
archive indexes, without editing any archived snapshot:

- `docs/review/handover-archive/README.md`;
- `docs/project-management/status-archive/README.md`;
- `docs/implementation-plan-archive/README.md`; and
- `docs/operations/disposable-test-server-archive/README.md`.

The controller has archived the current R3-returned pointers before activating
this assignment. Do not replace, rewrite or regenerate those snapshots.

The returned pointers must link the R4 proposal, handback, authority, exact
prompt and independent R3 re-review. They must retain every standing no-host and
retained-evidence restriction and say that WP-1 remains `changes requested` and
not accepted, BQ-2 and BQ-3 remain undecided, concrete Route 3 remains
unestablished, and WP-2 is not authorized. Do not edit registers, accepted
records, authorities, exact prompts, prior deliverables or historical snapshots.

## Required remediation

### 1. Make the B2-S/B2-N process-tree result unambiguous

Correct proposal §§0.1, 2.2, 7.4, 9.3, 10.1, 12.2, 13.2 and every dependent
summary where needed. Preserve these distinctions:

- PD-2a = B2-S means the current `sudo`-started form begins at `sudo` and cannot
  meet LR-2;
- B2-N is the separate, loader-free privileged-start design required to replace
  that current start for every in-set act before WP-2 can rely on B2-S;
- after B2-N, an in-set act's resulting inventoried tree begins at B2-N's
  loader-free start path and contains no `sudo`;
- an act PD-2b classifies out is not started by B2-N; its current `sudo` plus
  distribution-client path remains outside the boundary under EX-3 and requires
  complete §0.2 closure;
- B2-N changes how an in-set act starts, not whether it is in the set, and does
  not erase EX-2 or EX-3; and
- B2-S still decides no membership question. PD-2b remains required for both
  acts under both PD-2a answers.

In canonical Table A, replace the false statement that `sudo` remains inside the
tree after B2-N. In §12.2, answer the “`sudo` outside every inventoried tree” row
without a yes/no contradiction: for in-set B2-S acts, `sudo` is absent because
B2-N replaces it; for out acts, the entire existing `sudo` path is outside the
boundary under EX-3 and is not inventoried as a root procedure.

### 2. Make cumulative gate prerequisites exact

Correct §0.2 step 5 from “steps 1–3 and 4 or 4′” to “steps 1–3 and every
applicable item among 4 and 4′”, or exact equivalent wording.

Mechanically verify every one of the sixteen worked combinations against this
rule:

- all require independent acceptance of WP-1 and recorded PD-2a, PD-2b and PD-3;
- every exception requires its complete §0.2 item;
- every B2-S combination requires B2-N;
- every B3-IN combination requires the installer design; and
- a combination needing both governance closure and design prerequisites remains
  blocked until both are complete.

Do not weaken union rule U6 or the exact successor-gate paragraph. Carry this
exact paragraph, word for word, into the R4 proposal and all four returned
current-state pointers:

> **Gate before WP-2.** Independent Codex re-review of the R4 remediation and
> Peter's recorded BQ-2 and BQ-3 decisions, including PD-2a, PD-2b and PD-3, are
> always necessary. If either chosen answer contains an exception, including
> EX-1, EX-2 or EX-3 under BC-4, the complete implementation-plan §0.2
> change-control process must close before WP-2 may be prompted, authorized or
> rely on that boundary. A Peter decision on BQ-2 or BQ-3 is not by itself §0.2
> approval. Every separately required design prerequisite must also exist under
> its own authority and independent review before WP-2 may rely on it. If Peter
> retains literal no-exception LIT-FULL, WP-2 remains blocked until the required
> loader-free privileged-start and, where B3-IN is selected, installer designs
> make the boundary attainable, or Peter withdraws the affected design. BC-2
> remains unresolved for any later WP-9 selection. WP-1 remains changes-requested
> and is not accepted; BQ-2 and BQ-3 are undecided.

### 3. Record the missing R3-authorization snapshot honestly

Create the required R3 pointer-archive erratum. It must:

- state that the exact pre-R3-return pointer bytes are not present in the
  repository and must not be reconstructed or claimed verbatim without matching
  evidence;
- record the four pre-edit SHA-256 digests from R3 handback §3, including the
  abbreviated values exactly as the handback records them, and explain that the
  handback does not contain their full values except where it separately gives
  them;
- link the R3 authority, exact prompt, proposal and handback as the durable
  substantive authorization/return evidence;
- state that this erratum does not recreate the missing snapshots, change any
  decision, authorize work or make WP-1 acceptable;
- identify this R4 authority as the authority for the erratum; and
- state the forward control: current-state text must be snapshotted and indexed
  before replacement, and a task prompt may not prohibit a governing §16.3
  archival obligation without an approved governing-document change.

Add one accurate entry for this erratum to each of the four archive indexes.
Do not invent text from the lost scratchpad, claim a digest match that cannot be
performed, or modify an archived snapshot.

### 4. Preserve all prior corrections and boundaries

Carry forward without regression:

- PD-2a, PD-2b and PD-3 remain independent and required in every combination;
- every act classified out under either PD-2a answer carries EX-3 and a separate
  complete §0.2 item;
- every act classified in retains its later-WP role;
- B3-OUT adds EX-2 and B3-IN adds the installer design;
- EX-3 is not an LR-4 exception; LR-4 reaches DI-2 only when `AP-2` is in the set;
- governance prerequisites, design prerequisites and later WP work stay separate;
- FR-1 remains a documentation amendment, not a pre-WP-2 design package;
- `H-1R` is named in PD-3 without asserting an invocation literal;
- COR-01 through COR-16 remain sixteen corrections;
- the reproduced R8 count remains eight lines and eleven occurrences;
- BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided or unapproved;
- concrete Route 3 remains unestablished; and
- no successor implementation is authorized.

Do not perform a new boundary audit, invent a new exception, change a
recommendation direction, design B2-N or the installer, or perform WP-2 work.

## Acceptance checklist for the return

The cumulative R4 proposal, erratum and handback must make it possible for Codex
to verify:

1. all thirteen required reads reached EOF and this prompt matched its authority
   pin before any edit;
2. WP1-R3R-1, WP1-R3R-2 and WP1-R3R-3 are explicitly addressed;
3. no post-B2-N in-set path contains `sudo`, while out acts remain wholly outside
   the boundary under EX-3;
4. the compact gate requires every applicable governance and design prerequisite;
5. all sixteen combinations remain mechanically consistent with U1 through U7;
6. the exact R4 successor gate appears in the proposal and all four returned
   pointers;
7. the archive erratum records the historical gap without fabricating content and
   is linked by all four archive indexes;
8. the controller-created R3-return snapshots remain unchanged;
9. all R3 corrections and earlier R2 corrections remain intact;
10. BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided/unapproved;
11. concrete Route 3 remains unestablished and no successor is authorized;
12. prior deliverables and accepted records are unchanged; and
13. no prohibited operation occurred.

## Return state and handback contents

On success, use the exact terminal text:

`WP-1 R4 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`

The handback must list every file created or changed; complete-read evidence;
this prompt's verified identity; the proposal and erratum's exact line counts,
byte counts and SHA-256 digests; the precise correction for each finding; checks
and exact results; unresolved Peter decisions and governance gates; checks not
run; and an explicit statement that no prohibited operation occurred.

## Prohibited work

Do not use SSH or connect to any host. Do not access retained evidence, secrets,
credentials, player data, production, staging, `oracle-test`, Foundry or a
database. Do not perform network research, package operations, installation,
implementation, configuration or infrastructure edits, launcher work, builds,
tests, formatters, service/database operations, cleanup, workspace recreation,
OH-S4/OH-S4p or later work, H-1/H-2, activation, rollback, commit or push.

Do not open or execute §0.2 change control, approve a baseline change, make a
Product Owner decision beyond faithfully recording this authority, accept the
proposal, create WP-2 authority, or edit anything outside the explicitly
permitted deliverables, four pointer locations and four archive-index entries. A
conflict with these limits is a `HARD STOP`, not permission to expand scope.

## Review gate

The return accepts nothing. Independent Codex re-review is mandatory. Peter's
later recorded PD-2a, PD-2b and PD-3 decisions, complete §0.2 closure for every
selected exception-bearing answer, and every applicable separately authorized
and reviewed design prerequisite are required before WP-2 can be prepared or
authorized.
