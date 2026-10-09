# Proposed Claude prompt — LIT-FULL WP-2 system-call-intent inventory

Proposed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-20261009-13`

Status: **prepared for independent review; not accepted, assigned or executable**

## Authority and objective

Peter Duscha commissioned the LIT-FULL/R3-ROOT readiness sequence in dependency
order and has now accepted WP-1, recorded the F-1 boundary, approved EX-1 and
EX-2 through implementation-plan §0.2 and adopted controlled baseline v1.8.

If, and only if, Peter later accepts this exact prompt and names an executor,
execute **WP-2 only** from §9.5 of the accepted cumulative R8 proposal. Produce
a repository-only, complete system-call-intent inventory of every operation of
every in-scope root procedure. The inventory is the input to WP-3 through WP-7;
it does not design their interfaces or images.

This proposed prompt creates no authority. It does not authorize WP-2 until an
independent reviewer has reviewed it and Peter has accepted the exact prompt.

## Required reading

Before working, read completely, first byte through EOF:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
5. `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
6. `phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`;
7. `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md`;
8. `phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`;
9. `project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md`;
10. `phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md` and
    `project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md`;
11. `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md`;
12. `project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md`;
13. `project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md`;
14. `project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-assessment.md`;
15. `project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md`.

The cumulative R8 and WP-1 R6 proposals govern; earlier superseded proposal
rounds are comparison evidence only and need not be spliced into them.

## Fixed accepted boundary

Treat the following as fixed authority, not questions:

- The path is **LIT-FULL under R3-ROOT**. The unprivileged `ubuntu` entry remains
  Python and is outside the root-procedure set.
- The in-scope procedure set is exactly **RT-1 through RT-5 plus SA-1 and
  SA-2**: consume, hold, stop-post, backstop, `attest`, the `AP-2` static
  `start` role and the OS-6 static `stop` role.
- Under EX-1, each `sudo`-started in-scope procedure begins at the first
  design-controlled static image. `sudo`, and nothing else, is outside its
  inventoried tree as an LR-2 launch-preamble exception.
- Under EX-2, the installer class H-1, RB-1, RS-1 and H-1R is outside the root-
  procedure set, with HB-1 accepted. Do not inventory installer operations as
  WP-2 procedures and do not assert an H-1R invocation literal.
- **No EX-3** exists. Both lifecycle acts are in the set.
- BQ-4 permits **no dynamic child** in an in-scope procedure's process tree.
  Every process-creation intent must ultimately be a fork continuing in a
  static image or an `execve` of a design-controlled static image. An
  `execve` of a distribution program is not an admissible WP-2 result.
- B2-N and a Python-free installer are not prerequisites for this combination.
- BC-2 remains a later WP-9 question and is not a WP-2 decision.
- Concrete Route 3 remains unestablished. This inventory must not claim
  otherwise.

The scope header and role roster in the inventory are the FR-1 documentation
amendment: they record the accepted boundary and name the `start` and `stop`
roles in the commissioned work. They do not amend a historical proposal or
perform WP-3 through WP-7.

## Deliverables

Create exactly these durable deliverables:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md`.

### Operation-inventory requirements

The inventory must be cumulative, self-contained and reviewable without
consulting an earlier WP-2 draft. It must:

1. state the fixed F-1 scope and exclusions exactly as above;
2. define fact tags that distinguish accepted text, mechanically derived
   inventory statements and unresolved later-package obligations;
3. give each procedure and every material sub-role a stable identifier, caller,
   beginning boundary, accepted current implementation and accepted failure
   contract;
4. use R8 §7.3 rows 1 through 22—including 3a through 3g—as the minimum
   taxonomy, then extend it to **every accepted operation and call** of every
   in-scope procedure;
5. keep rows per procedure and sub-role rather than collapsing shared helpers
   into a single unexplained row;
6. inventory at system-call intent all process creation, credential change,
   descriptor handling, filesystem and metadata access, locks, clocks, sleeps,
   polling, signal receipt, signal sending, identity validation, reaping,
   hashing, parsing, journal/record publication, synchronization and unit/
   authorization interactions that accepted behavior requires;
7. include the complete SN-I-1 through SN-I-4, SN-4 validation and reap-attempt
   surface represented by rows 3a through 3g, with WB, RE, GD and child-state
   consequences traced rather than summarized away;
8. classify every process-creation row as either a fork that continues in a
   static image or an `execve` of a design-controlled static image. Where WP-3
   or WP-4 must choose the exact mechanism, record the required intent and the
   later owner without choosing a distribution executable, wire protocol,
   language, library or syscall sequence;
9. map every current DI-1 through DI-6 delegation to the procedure/sub-role and
   operation intents that replace it, including DI-2 for `start` and the named
   stop function for `stop`. This is an input list for WP-3, not the loader-free
   interface contract;
10. trace every accepted procedure step to at least one operation row and every
    operation row back to accepted text. Provide closed coverage and
    reconciliation tables for procedures, steps, R8 §7.3 taxonomy rows,
    DI-1 through DI-6, SN/WB/RE/GD and the added `start`/`stop` roles;
11. record blocking class, bounded count or manager deadline only where the
    accepted record supplies it. Do not turn a class-X call or a scheduled-
    waiting budget into an elapsed-time bound;
12. preserve accepted fail-closed outcomes, interruption states, residuals and
    “unknown” states. Do not convert a signal attempt into proof of exit or a
    missing record into proof of absence;
13. identify each exact question deferred to WP-3, WP-4, WP-5, WP-6 or WP-7,
    without answering it in WP-2;
14. include an acceptance checklist and an explicit table of inputs WP-3 may
    and may not rely on; and
15. apply the stop rule: if any accepted function appears to require a dynamic
    child or cannot be inventoried without changing accepted behavior, return a
    precise `HARD STOP` identifying the function. Do not propose SCDC or silently
    create a BC-3 exception.

### What WP-2 must not do

Do not:

- design or select a D-Bus, Polkit or other loader-free interface (WP-3);
- select an implementation language, exact syscall sequence, static-image
  architecture, parser, memory/stack bound, blocking implementation or `EINTR`
  handling (WP-4);
- design a proof/evidence method (WP-5), equivalence disposition (WP-6), or
  size/review-cost estimate (WP-7);
- perform external citation research or add a claim not already accepted;
- collect MF-1 through MF-9 or any host fact;
- invent an invocation for H-1R;
- edit any accepted proposal, acceptance/approval record, historical snapshot,
  application source, infrastructure source, configuration, test or evidence
  artifact; or
- select LIT-FULL for implementation or claim concrete Route 3 is established.

## Return and current-state handling

Before replacing any of the four current-state pointers on return, preserve the
then-current WP-2 authorization state verbatim in dated snapshots beside the
canonical files and add their SHA-256 values to the four existing archive
indexes. Do not rewrite any earlier snapshot.

Then update only:

1. `docs/review/Handover information`;
2. `docs/project-management/status.md`;
3. implementation-plan §20; and
4. the restriction banner in `docs/operations/disposable-test-server.md`.

Those pointers must say either:

- `WP-2 OPERATION INVENTORY RETURNED — INDEPENDENT REVIEW PENDING`; or
- `HARD STOP` with the exact blocking function and no invented solution.

They must preserve baseline v1.8, the F-1 boundary, the no-host restriction and
the separate gates for WP-3 through WP-7. The handback must list files changed,
source coverage, reconciliation counts, checks run, checks not run, unresolved
later-WP questions and an explicit statement that no prohibited action occurred.

## Prohibited operations

Do not use SSH or connect to any host. Do not access retained evidence, secrets,
credentials, player data, production, staging, `oracle-test`, Foundry or a
database. Do not perform network research, package operations, installation,
implementation, configuration/infrastructure edits, launcher work, builds,
tests, formatters, service/database operations, cleanup, workspace recreation,
OH-S4/OH-S4p or later work, H-1/H-2, activation, rollback, commit or push.

Repository-only searches, reads, Markdown editing, link/path checks,
`wc -l -c`, `sha256sum`, `git diff --check` and read-only Git status/diff are
allowed. Do not run application or hook suites; they cannot prove a
documentation-only inventory.

## Terminal state and review gate

Return terminal text `WP-2 OPERATION INVENTORY RETURNED` only after both
deliverables, required snapshots/index entries and all four current-state
pointers are complete and mutually consistent. Otherwise return `HARD STOP`
with the precise reason.

The return does not accept WP-2, authorize WP-3, establish concrete Route 3 or
select LIT-FULL for implementation. Independent Codex review of the complete
WP-2 return and Peter's later acceptance are required before any WP-3 prompt or
authority may be prepared.
