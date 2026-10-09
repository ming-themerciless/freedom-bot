# Claude prompt — LIT-FULL WP-1 independent re-review remediation R2

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R2-20261008-11`

## Authority and objective

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment. Remediate all four findings in
`project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation.md`:

- **WP1-R1R-1, Blocking:** the R1 proposal's canonical alternative table
  incorrectly classifies B2-F-B/EX-3 as an LR-4 exception, contradicting its own
  COR-09, COR-16 and §7.5;
- **WP1-R1R-2, Important:** the §2.2 decision matrix presents FR-1 as both a
  pre-WP-2 design package and a documentation-only amendment;
- **WP1-R1R-3, Important:** the proposed BQ-3 decision sentence promotes the
  inferred H-1R verified-exec-stub invocation to fact; and
- **WP1-R1R-4, Optional:** the correction count says fourteen where the record
  enumerates sixteen.

Produce one self-contained cumulative WP-1 R2 remediation proposal and a durable
handback. Do not edit or replace either earlier WP-1 proposal or handback, the R1
proposal or handback, or either independent review. Do not decide BQ-2 or BQ-3,
approve any exception, open or execute implementation-plan §0.2 change control,
accept WP-1, establish concrete Route 3 or authorize WP-2.

## Required reading

Before drafting or editing anything, read these files completely from first byte
through EOF. Targeted searches do not substitute for these reads. If output is
truncated, continue in bounded, non-overlapping chunks until EOF.

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-proposal.md`;
7. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-handback.md`;
8. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-authority.md`;
9. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-claude-prompt.md`;
10. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
11. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`; and
12. `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`.

Record line counts, byte counts and SHA-256 digests for all twelve files in the
handback. Also verify this prompt's byte count and SHA-256 against its separate R2
authority record before any edit. If a required file is missing, unreadable or
does not match the identity named by its authority, write the handback with a
precise `HARD STOP` and make no substantive proposal.

## Deliverables and permitted pointer edits

Create only these new durable deliverables:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-proposal.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-handback.md`.

On a successful return, update only these four current-state locations:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 only of `docs/implementation-plan.md`; and
- the restriction banner only in `docs/operations/disposable-test-server.md`.

The returned pointers must link the R2 proposal, handback, authority, exact prompt
and both independent reviews. They must retain all standing no-host and retained-
evidence restrictions and say that WP-1 remains `changes requested` and not
accepted, BQ-2 and BQ-3 remain undecided, concrete Route 3 remains unestablished,
and WP-2 is not authorized. Do not edit registers, archive indexes, historical
snapshots, accepted records, authorities, exact prompts or prior deliverables.

## Required remediation

### 1. Correct EX-3 without changing the boundary

Correct R1 proposal §10.1 and every dependent R2 summary so they agree with
COR-09 and COR-16:

- LR-4 applies to a root procedure in the final set and reaches DI-2 only if
  `AP-2` is in that set;
- under B2-F-B, `AP-2` and/or the OS-6 stop are outside the set, so their
  exclusion is not a free-standing LR-4 exception;
- EX-3 is the proposed wider BC-4 boundary exception for whichever whole
  `sudo`-started acts Peter leaves outside the set;
- do not silently expand BC-4, invent an LR-4 exception, treat EX-3 as BC-3, or
  decide whether either act belongs in the set; and
- preserve the rule that every exception-bearing choice requires complete §0.2
  closure before WP-2 may be prompted, authorized or rely on the boundary.

The R2 proposal must contain one canonical table that accurately states every LR
exception, §0.2 item, pre-WP-2 prerequisite, new design package and downstream WP
effect for B2-S, B2-F-A, B2-F-B, B3-OUT, B3-IN and mixed BQ-2 answers.

### 2. Repair the sequencing matrix

Replace the ambiguous §2.2 column/row formulation. Keep these categories
separate:

- **governance prerequisite before WP-2:** independent acceptance of WP-1,
  Peter's BQ-2/BQ-3 decisions, and complete §0.2 closure for any selected
  exception-bearing answer;
- **separate design prerequisite before WP-2:** B2-N for B2-S, and the
  Python-free installer/loader-free verified-exec design needed for a literal
  B3-IN path where applicable; and
- **work allocated to WP-2 through WP-7 after the gate:** FR-1's `start` and
  `stop` roles, their inventory, interfaces, images, proof, mapping and estimate.

Do not call FR-1 a completed pre-WP-2 design package. If it is a documentation
amendment that records the selected boundary and adds roles to the commissioned
work, say exactly that and show which later WP owns each design activity.

### 3. Keep H-1R fact and inference separate

Preserve the complete audit's finding that the accepted record does not state an
H-1R invocation literal and that use of the verified-exec stub is an observation/
inference, not an accepted fact. The proposed BQ-3 decision sentence must:

- name H-1R expressly so it is not silently omitted from Peter's classification;
- avoid asserting that H-1R runs through the stub or any other unstated literal;
- classify H-1R only at the level the accepted record supports: a separately
  authorized root re-record operation, read-only plus record write, implemented
  as a subcommand of the one tool in the accepted design; and
- either leave the invocation for a later separately authorized design record or
  state the inference expressly outside the text Peter is asked to approve.

Do not perform a new invocation design and do not remove H-1R from PD-3.

### 4. Correct and audit the correction count

Use **sixteen** consistently for COR-01 through COR-16. Search the new cumulative
proposal, handback and four returned pointers for stale references to fourteen
corrections. Distinguish the twelve required complete-read records from the
sixteen corrections so the numbers cannot be confused.

### 5. Preserve the already-correct successor gate

Carry this exact paragraph, word for word, into the R2 proposal and all four
current-state pointers:

> **Gate before WP-2.** Independent Codex re-review of the R2 remediation and
> Peter's recorded BQ-2 and BQ-3 decisions are always necessary. If either chosen
> answer contains an LR exception, including EX-1 or EX-2 under BC-4, the complete
> implementation-plan §0.2 change-control process must close before WP-2 may be
> prompted, authorized or rely on that boundary. A Peter decision on BQ-2 or BQ-3
> is not by itself §0.2 approval. If Peter retains literal no-exception LIT-FULL,
> WP-2 remains blocked until a separately authorized, reviewed loader-free
> privileged-start design makes the boundary attainable, or Peter withdraws the
> affected design. BC-2 remains unresolved for any later WP-9 selection. WP-1
> remains changes-requested and is not accepted; BQ-2 and BQ-3 are undecided.

The change from “R1 remediation” to “R2 remediation” is the only change from the
previous exact gate paragraph. Do not weaken, broaden or reinterpret it.

## Acceptance checklist for the return

The cumulative R2 proposal and handback must make it possible for Codex to verify:

1. all twelve required reads reached EOF and this prompt matched its authority pin;
2. WP1-R1R-1 through WP1-R1R-4 are each explicitly closed;
3. EX-3 is not called an LR-4 exception when `AP-2` is outside the set;
4. the decision matrix separates governance gates, pre-WP-2 design prerequisites
   and WP-2-through-WP-7 work;
5. the BQ-3 sentence names H-1R without asserting an unestablished invocation;
6. COR-01 through COR-16 are counted as sixteen everywhere;
7. the exact successor gate appears in the proposal and all four pointers;
8. BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided/unapproved;
9. concrete Route 3 remains unestablished and no successor is authorized;
10. prior deliverables and accepted records are unchanged; and
11. no prohibited operation occurred.

## Return state and handback contents

On success, use the exact terminal text:

`WP-1 R2 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`

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
proposal, create WP-2 authority, or edit anything outside the explicitly permitted
deliverables and four pointer locations. A conflict with these limits is a
`HARD STOP`, not permission to expand scope.

## Review gate

The return accepts nothing. Independent Codex re-review is mandatory. Peter's
later recorded BQ-2/BQ-3 decisions, and complete §0.2 closure for any selected
exception-bearing answer, are required before WP-2 can be prepared or authorized.
