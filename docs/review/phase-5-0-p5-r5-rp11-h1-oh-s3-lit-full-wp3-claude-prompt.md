# Proposed Claude prompt — LIT-FULL WP-3 loader-free interface contract

Proposed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-20261009-20`

Status: **prepared for independent review; not accepted, assigned or executable**

## Authority and objective

Peter Duscha has accepted WP-2 of the commissioned LIT-FULL/R3-ROOT readiness
sequence. If, and only if, Peter later accepts this exact prompt and names an
executor, execute **WP-3 only** from §9.5 of the accepted cumulative R8
proposal.

Produce a repository-only, cumulative loader-free interface contract for the
accepted DI-1 through DI-6 delegations and the SA-2 stop-unit call. State what
each in-scope static root image sends and receives, the value forms and
completion/failure semantics, and the accepted version-bound source supporting
each claim. Answer exactly Q3-1, Q3-2, Q3-3, Q3-4, Q3-5, Q3-6, Q3-7, Q3-9 and
Q3-11 from the accepted WP-2 inventory.

This proposed prompt creates no execution authority. A different independent
reviewer must review its exact pinned bytes, and Peter must separately accept
and activate it before WP-3 can start.

## Required reading

Before working, read completely, first byte through EOF, except where a named
portion is expressly sufficient:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`;
7. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md`;
8. `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`;
9. `docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md`;
10. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`;
11. `docs/review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md`;
12. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md`;
13. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md`;
14. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md`;
15. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md`;
16. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
17. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-handback.md`;
18. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5.md`; and
19. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-acceptance.md`.

The accepted R8 proposal, accepted OH-S2 R2 citation record, accepted WP-1 R6
boundary and accepted WP-2 R5 inventory govern. Earlier superseded rounds are
comparison evidence only and must not be spliced into the cumulative result.

Before the first edit, record in working notes each required item's path, line
count, byte count and SHA-256. The handback must contain that complete reading
ledger and state that the required reading was completed before editing. If a
required item cannot be read as specified, return `HARD STOP` without editing
the interface contract.

## Fixed accepted boundary

Preserve without reinterpretation:

- LIT-FULL under R3-ROOT is the readiness path under investigation; it is not
  selected for implementation and concrete Route 3 is not established.
- The in-scope procedures are exactly RT-1 through RT-5, SA-1 (`start`) and
  SA-2 (`stop`). The unprivileged entry remains outside the root-procedure set.
- F-1 remains B2-F with both lifecycle acts in and B3-OUT. EX-1 and EX-2 are
  effective only for their approved BC-4 uses; EX-3 is not selected.
- H-1, RB-1, RS-1 and H-1R remain outside the set. B2-N and a Python-free
  installer are not prerequisites.
- No dynamic child is admitted beneath a first design-controlled root image.
  Every retained process creation must ultimately be a fork continuing in a
  static image or an `execve` of a design-controlled static image; no
  distribution executable is an admissible replacement.
- WP-2's operation rows, blocking classes, call-site unit, residuals,
  interruption states and unknown states are accepted inputs. A signal attempt
  is not proof of exit and a missing record is not proof of absence.
- The only retained replacement child intent is the DI-6 authorization
  subject. DI-1 through DI-5 and the stop-unit command children are historical,
  not replacement children.
- Q6-6 and Q6-7 remain unanswered. In particular, WP-3 must not decide whether
  SN-10/A-I-16 extends to the BS-4 terminal disarm, how unknown effect maps to
  a non-child interaction, or whether AM-0 repeats AP-0's unterminated-record
  condition.
- BC-2 remains a later WP-9 question.

## Source authority and citation discipline

WP-3 is a citation slice of the accepted OH-S2 class. Use only the repository
sources expressly authorized by the accepted records above. Do not browse,
download, query a host, inspect installed binaries or packages, or introduce a
fact from memory.

Every interface claim must cite the exact accepted source passage that supports
it and identify the applicable observed version where the claim is
version-bound: systemd `259.5-0ubuntu3.4` and polkit `127-2ubuntu1.1`. Separate:

1. accepted source facts;
2. mechanical derivations from those facts;
3. proposed interface obligations; and
4. facts still missing.

A proposed obligation is not an established upstream fact. If the authorized
repository sources do not support a fact required to answer a Q3 question,
record the exact missing fact and return `HARD STOP`; do not manufacture a
citation, silently defer a WP-3-owned question, or perform new research.

## Deliverables

Create exactly:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-handback.md`.

The interface contract must be cumulative and self-contained. It must include:

1. the fixed scope, source hierarchy, fact classes and version boundary;
2. a closed interface roster covering DI-1 through DI-6 plus the SA-2
   stop-unit call, mapped to all 41 logical call sites from WP-2;
3. request, response, value encoding, completion, cancellation and failure
   semantics for each interface, without selecting a programming language,
   client library or syscall sequence;
4. a citation matrix mapping every material contract statement to accepted
   systemd or polkit source text, or to an expressly identified accepted design
   requirement;
5. an exact Q3 closure table for Q3-1, Q3-2, Q3-3, Q3-4, Q3-5, Q3-6, Q3-7,
   Q3-9 and Q3-11, with no additional Q3 identifier invented or omitted;
6. a WP-4 input table stating what WP-4 may rely on and what remains outside
   WP-3;
7. reconciliation showing that every WP-2 row tagged with a Q3 identifier and
   every logical DI/stop call site is covered by the applicable contract;
8. an acceptance checklist; and
9. the stop-rule result.

### Required Q3 outcomes

- **Q3-1:** define the loader-free unit-state read and typed value form for all
  properties named by WP-2, including unloaded units and own-start-pre reads.
- **Q3-2:** define transient holder-service creation, its complete property
  set, job/completion semantics and loaded-name refusal.
- **Q3-3:** define creation of the backstop timer and service, their property
  sets, relationship and completion semantics.
- **Q3-4:** define timer disarm for all three DI-4 sites, including already
  stopped/not-loaded behavior, without answering Q6-6 or Q6-7.
- **Q3-5:** define a noninteractive Polkit decision equal to the accepted
  `pkcheck` intent for the action, `unit`/`verb` details and process subject;
  derive `authorized`, `not-authorized` and `error` from authority results, not
  from the command-line exit-status contract that does not carry over.
- **Q3-6:** define how DI-6's subject identity `(pid, start time, uid)` is
  conveyed to DI-5 and recorded as an interface fact. WP-4 retains creation of
  the subject and its exact process mechanics.
- **Q3-7:** define SA-2's stop-unit request, job/completion/result semantics,
  inactive/not-loaded behavior, start-pre exclusion and root authorization.
- **Q3-9:** state the interface facts required to obtain every explicit unit
  and manager baseline property, including hidden/explicit-only behavior and
  any printed-form dependency the accepted normalization still has.
- **Q3-11:** cite or fail closed on the direct on-disk/kernel acquisition facts
  for host, operator, repository and installed-package baseline values. Do not
  select a mechanism the accepted sources do not establish.

## What WP-3 must not do

Do not:

- design the static images, choose a language or library, name an exact syscall
  sequence, implement parsing, set memory/stack bounds, or settle `EINTR` and
  blocking mechanics (WP-4);
- choose the DI-6 process-creation mechanism or body (WP-4);
- create a proof/evidence plan (WP-5), equivalence disposition (WP-6), size or
  review-cost estimate (WP-7), or WP-9 decision;
- answer Q6-6, Q6-7 or any non-Q3 deferred question;
- weaken any accepted failure, residual, interruption or unknown-effect
  contract;
- add a dynamic child, distribution executable, SCDC/BC-3 exception, new
  baseline exception or scope change;
- claim that an interface call has an elapsed-time bound merely because WP-2
  records a class-E budget for the historical child wait;
- edit the accepted WP-2 inventory, an earlier prompt, handback, review,
  acceptance record, historical snapshot, application source, infrastructure
  source, configuration, test or retained-evidence artifact; or
- prepare or authorize WP-4 through WP-7.

## Checks and terminal evidence

Allowed checks are repository-only reads and searches, link/path checks,
`wc -l -c`, `sha256sum`, mechanical parsing of Markdown tables,
`git diff --check` and read-only Git status/diff.

The handback must report the reading ledger; every deliverable's line, byte and
SHA-256 identity where non-self-referential; files created and edited; the
interface, call-site, Q3 and citation reconciliation counts; exact checks and
results; checks not run and why; every question left for WP-4 through WP-7;
and confirmation that no prohibited action occurred.

Do not run application or hook suites, builds, formatters or linters. They are
outside this documentation/citation authority and cannot establish the
interface-source claims.

## Return and current-state handling

Before replacing the four current-state pointers at terminal return, preserve
their exact WP-3-authorization state in dated snapshots beside the canonical
files and add each SHA-256 to its archive index. Do not rewrite an earlier
snapshot.

Then update only:

1. `docs/review/Handover information`;
2. `docs/project-management/status.md`;
3. implementation-plan §20; and
4. the restriction banner in
   `docs/operations/disposable-test-server.md`.

The pointers must say either `WP-3 INTERFACE CONTRACT RETURNED — INDEPENDENT
REVIEW PENDING` or `HARD STOP` with the exact unsupported required fact. They
must preserve baseline v1.8, the fixed F-1/EX boundary, the no-host restriction
and the separate WP-4 through WP-7 gates.

## Prohibited operations

Do not use SSH or connect to any host. Do not access retained evidence,
secrets, credentials, player data, production, staging, `oracle-test`, Foundry
or a database. Do not perform network research, fresh fact collection, package
operations, installation, implementation, configuration/infrastructure edits,
launcher work, builds, tests, formatters, service/database operations, cleanup,
workspace recreation, OH-S4/OH-S4p or later work, H-1/H-2, activation,
rollback, commit or push.

The R5 and H-0G retained paths remain untouched pending separately gated LC-3
through LC-5 authority.

## Terminal state and review gate

Return terminal text `WP-3 INTERFACE CONTRACT RETURNED` only after both
deliverables, the required snapshots/index entries and all four current-state
pointers are complete and mutually consistent. Otherwise return `HARD STOP`
with the precise unsupported fact or source conflict.

The return does not accept WP-3, authorize WP-4, establish concrete Route 3 or
select LIT-FULL for implementation. Independent review of the complete WP-3
return and Peter's later acceptance are required before a WP-4 prompt or
authority may be prepared.
