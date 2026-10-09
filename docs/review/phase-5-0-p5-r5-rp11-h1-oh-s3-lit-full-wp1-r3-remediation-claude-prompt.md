# Claude prompt — LIT-FULL WP-1 independent re-review remediation R3

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R3-20261008-12`

## Authority and objective

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment. Remediate both findings in
`project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation.md`:

- **WP1-R2R-1, Blocking:** the R2 decision matrices omit PD-2b and conditional
  EX-3 on the B2-S path, allowing a required decision and §0.2 gate to disappear;
  and
- **WP1-R2R-2, Optional:** proposal §13.1 retains the stale, non-reproducing count
  of nine `sudo -n` lines in R8 instead of the reproduced count of eight.

Produce one self-contained cumulative WP-1 R3 remediation proposal and a durable
handback. Do not edit or replace any earlier WP-1 proposal, handback or review.
Do not decide BQ-2 or BQ-3, approve an exception, open or execute implementation-
plan §0.2 change control, accept WP-1, establish concrete Route 3 or authorize
WP-2.

## Required complete reading

Before drafting or editing anything, read these files completely from first byte
through EOF. Targeted searches do not substitute for the complete reads. Continue
in bounded, non-overlapping chunks if output is truncated.

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-proposal.md`;
7. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-handback.md`;
8. `docs/review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-authority.md`;
9. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-claude-prompt.md`;
10. `docs/review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation.md`;
11. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
12. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`; and
13. `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`.

Record line counts, byte counts and SHA-256 digests for all thirteen files in the
handback. Also verify this prompt's byte count and SHA-256 against its separate R3
authority record before any edit. If a required file is missing, unreadable or
does not match the identity named by its authority, write the handback with a
precise `HARD STOP` and make no substantive proposal.

## Deliverables and permitted pointer edits

Create only these new durable deliverables:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md`.

On a successful return, update only these four current-state locations:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 only of `docs/implementation-plan.md`; and
- the restriction banner only in `docs/operations/disposable-test-server.md`.

The returned pointers must link the R3 proposal, handback, authority, exact
prompt and the independent R2 re-review. They must retain every standing no-host
and retained-evidence restriction and say that WP-1 remains `changes requested`
and not accepted, BQ-2 and BQ-3 remain undecided, concrete Route 3 remains
unestablished, and WP-2 is not authorized. Do not edit registers, archive indexes,
historical snapshots, accepted records, authorities, exact prompts or prior
deliverables.

## Required remediation

### 1. Restore the missing B2-S decision dimension

Correct proposal §§2.2, 10.1 and 12.2 and every dependent summary. Preserve these
facts and distinctions:

- **PD-2a** decides where a `sudo`-started root procedure begins: B2-F at the
  first design-controlled image, or B2-S at `sudo`;
- **PD-2b remains independently required under both PD-2a answers** and decides,
  separately for `AP-2` and the OS-6 `stop`, whether each act belongs to the
  final root-procedure set;
- **PD-3** independently decides B3-OUT or B3-IN;
- B2-S by itself decides no membership question and does not put either act in
  or out of the set;
- for every act classified **in** under B2-S, B2-N must provide the loader-free
  privileged start, and its `start` or `stop` role remains allocated across
  WP-2 through WP-7 after the gate;
- for every act classified **out** under B2-S, EX-3 remains a proposed wider
  BC-4 boundary exception for that whole act, and complete §0.2 change control
  must close before WP-2 may be prompted, authorized or rely on the boundary;
- B3-OUT independently adds EX-2 and its §0.2 item;
- B3-IN independently adds the Python-free installer / loader-free verified-exec
  design prerequisite; and
- B2-N does not erase EX-2 or EX-3 and does not substitute for their §0.2 closure.

The cumulative R3 proposal must contain one unambiguous canonical matrix. Use
one of these forms:

1. an explicit Cartesian matrix covering both PD-2a answers × all four PD-2b
   membership combinations × both PD-3 answers; or
2. three orthogonal tables, one for each decision dimension, followed by a
   mechanical union rule and worked rows for every B2-S membership combination.

Whichever form is used must make every combination mechanically derivable and
state, without cross-reference ambiguity:

- all three recorded Peter decisions required before WP-2;
- each LR or boundary exception and its complete §0.2 item;
- each separate pre-WP-2 design prerequisite;
- each role and activity allocated to WP-2 through WP-7; and
- the resulting WP-2 status.

Do not describe B2-S as making `start` and `stop` absent. Under B2-S their
presence follows PD-2b; B2-N changes how an included role starts, not whether the
role is in the set.

### 2. Make the successor gate cover EX-3 expressly

Carry this exact paragraph, word for word, into the R3 proposal and all four
returned current-state pointers:

> **Gate before WP-2.** Independent Codex re-review of the R3 remediation and
> Peter's recorded BQ-2 and BQ-3 decisions, including PD-2a, PD-2b and PD-3, are
> always necessary. If either chosen answer contains an exception, including
> EX-1, EX-2 or EX-3 under BC-4, the complete implementation-plan §0.2
> change-control process must close before WP-2 may be prompted, authorized or
> rely on that boundary. A Peter decision on BQ-2 or BQ-3 is not by itself §0.2
> approval. If Peter retains literal no-exception LIT-FULL, WP-2 remains blocked
> until a separately authorized, reviewed loader-free privileged-start design
> makes the boundary attainable, or Peter withdraws the affected design. BC-2
> remains unresolved for any later WP-9 selection. WP-1 remains changes-requested
> and is not accepted; BQ-2 and BQ-3 are undecided.

This is a dependent correction required by WP1-R2R-1: EX-3 is a boundary
exception rather than an LR-4 exception, so the gate must not be phrased in a way
that can exclude an EX-3-only B2-S combination.

### 3. Correct the stale count

Change proposal §13.1 Q-2 from nine `sudo -n` lines in R8 to the reproduced count
of **eight**. Search the cumulative R3 proposal and handback for any other place
that presents nine as the reproduced R8 line count. Preserve the distinction
between eight matching lines and eleven occurrences. Do not change any conclusion
on the basis of this editorial correction.

### 4. Preserve the R2 corrections and boundaries

Carry forward without regression:

- EX-3 is not an LR-4 exception; LR-4 reaches DI-2 only when `AP-2` is in the set;
- governance prerequisites, separate design prerequisites and later WP work stay
  separate;
- FR-1 remains a documentation amendment, not a pre-WP-2 design package;
- H-1R is named in PD-3 without asserting an invocation literal, and its
  verified-exec-stub invocation remains an inference outside Peter's proposed
  sentence;
- COR-01 through COR-16 remain sixteen corrections, distinct from the thirteen
  complete-read records required by this prompt;
- BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided or unapproved;
- concrete Route 3 remains unestablished; and
- no successor is authorized.

Do not perform a new boundary audit, invent a new exception, change a
recommendation direction, design B2-N or the installer, or perform WP-2 work.

## Acceptance checklist for the return

The cumulative R3 proposal and handback must make it possible for Codex to verify:

1. all thirteen required reads reached EOF and this prompt matched its authority
   pin before any edit;
2. WP1-R2R-1 and WP1-R2R-2 are explicitly closed;
3. PD-2a, PD-2b and PD-3 appear as governance prerequisites in every complete
   BQ-2/BQ-3 combination;
4. every B2-S act classified out carries EX-3 and complete §0.2 closure;
5. every B2-S act classified in retains its later-WP role after B2-N;
6. B3-OUT adds EX-2 and B3-IN adds its separate installer design prerequisite in
   every combination;
7. the canonical matrix has no collapsed or unclassified decision dimension;
8. the exact successor gate appears in the proposal and all four returned
   pointers;
9. the reproduced R8 count is eight lines and eleven occurrences everywhere;
10. all four R2 corrections remain intact;
11. BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided/unapproved;
12. concrete Route 3 remains unestablished and no successor is authorized;
13. prior deliverables and accepted records are unchanged; and
14. no prohibited operation occurred.

## Return state and handback contents

On success, use the exact terminal text:

`WP-1 R3 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`

The handback must list every file created or changed; complete-read evidence;
this prompt's verified identity; the proposal's exact line count, byte count and
SHA-256; the precise correction for each review finding; checks and exact results;
unresolved Peter decisions and governance gates; checks not run; and an explicit
statement that no prohibited operation occurred.

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
permitted deliverables and four pointer locations. A conflict with these limits
is a `HARD STOP`, not permission to expand scope.

## Review gate

The return accepts nothing. Independent Codex re-review is mandatory. Peter's
later recorded PD-2a, PD-2b and PD-3 decisions, and complete §0.2 closure for any
selected exception-bearing answer, are required before WP-2 can be prepared or
authorized.
