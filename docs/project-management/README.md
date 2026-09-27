# Project governance

Status: Accepted with controlled baseline v1.6 on 2026-08-27; Phase 3 gate
approved 2026-08-28; Phase 4 gate approved 2026-08-29; Phase 5.0 selected for
readiness planning, with product implementation not yet authorized. A bounded
pre-implementation evidence harness was authorized 2026-09-02 to resolve the
P5.0-R4/P5.0-R5 readiness evidence; it is not Package 5.0 implementation.

This directory contains the management controls for the Freedom Blades
Platform. The technical scope remains governed by
[`docs/implementation-plan.md`](../implementation-plan.md).

Current delivery state is recorded in [`status.md`](status.md), and the current
assignment and task-specific restrictions are recorded in
[`Handover information`](../review/Handover%20information). Historical status
and handover snapshots are indexed under [`status-archive/`](status-archive/)
and [`handover-archive/`](../review/handover-archive/) respectively. Archived
text is retained evidence and never grants current authority.

The present P5.0-R5 action is repository-only drafting of a bounded
operational-evidence authorization prompt. P5.0-R5 remains Blocking,
`plan.is_executable=False`, and Package 5.0 remains not ready. The current
handover, rather than an older evidence-harness prompt, controls what may be
done now.

## Solo-maintainer operating model

Peter Duscha is the Product Sponsor, Acceptance Authority, Product Owner, Data
Owner, Operations Owner and Delivery Lead. Agents may implement, coordinate and
independently review work. For each package, Peter designates an implementing
agent as working Technical Lead.

**At a mandatory review checkpoint — every gate in the implementation plan's
§16.4 reviewer-checkpoint list, and every gate whose subject row in the gate-
authority table below requires an Independent Reviewer recommendation — an
Independent Reviewer who did not implement the work is required.** If no such
reviewer is available, the package remains `deferred`; it is not approved,
conditionally approved, or self-reviewed by its implementer. The phrase *where
practical* applies only to reviews that are not mandated by those two lists,
such as optional second opinions on non-gated work.

Security-sensitive packages receive a separate security-focused review. Agent
reviews are recommendations; Peter records gate and risk-acceptance decisions.

Capacity means the availability of one maintainer for decisions, operational
checks and gate approval plus agent delivery/review capacity. It does not imply
employees or a standing team. Until availability is known for a package, its
effort range is not converted into a promised calendar date.

## Management definition of ready

A phase or independently gated work package may start only when:

- its outcome, included scope and exclusions are written;
- predecessor gates are approved or an approved exception is recorded;
- blocking decisions and dependencies are closed;
- Product Owner, Technical Lead, implementer and required reviewer roles have
  named assignees;
- the work is decomposed into deliverables small enough to estimate and review;
- estimate assumptions, capacity, confidence and contingency are recorded;
- acceptance criteria are objective and trace to tests or supervised checks;
- required development, disposable database and staging environments are
  available; and
- material risks have owners, mitigations and triggers in the RAID register.

Failure to meet readiness means the item remains `not ready`; it is not treated
as late implementation.

## Management definition of done

A phase or work package is done only when:

- every committed deliverable and acceptance criterion has evidence;
- relevant narrow and full test suites have passed, with skips explained;
- required PostgreSQL, security, migration and operational evidence uses the
  environment specified by the implementation plan;
- documentation, configuration, recovery and monitoring are current;
- no blocking finding remains open;
- important findings are closed or explicitly scheduled and accepted by the
  appropriate owner without weakening a gate invariant;
- the Independent Reviewer records a recommendation;
- the accountable gate authority records `approved` in the status and change
  records; and
- dependent work has not begun before that approval.

## Gate process

Each gate has four possible decisions:

- `approved`: all exit criteria are met; dependent work may start;
- `conditionally approved`: only non-blocking actions remain, each with owner
  and due date; no action may weaken a security, identity, authorization,
  migration, atomicity, financial-integrity or production-reliability criterion;
- `rejected`: blocking evidence or defects remain; dependent work may not start;
- `deferred`: review has not occurred or required evidence is unavailable.

The gate package contains the requirements traceability table, test and check
results, skipped evidence, review findings, migration/recovery exercise,
configuration and deployment effects, RAID changes and requested decision.

Gate authority is role-based:

| Gate subject | Required recommendation | Approval authority |
|---|---|---|
| Architecture/schema | Technical Lead, Data Owner, Independent Reviewer | Acceptance Authority |
| Import/migration | Data Owner, Operations Owner, Independent Reviewer | Acceptance Authority |
| Authentication/security/privacy | Security Reviewer, Independent Reviewer | Acceptance Authority |
| Rules/economy/settlement | Product Owner, Data Owner, Independent Reviewer | Acceptance Authority |
| Deployment/cutover | Technical Lead, Security Reviewer, Operations Owner | Acceptance Authority |
| Visual/accessibility | Product Owner, accessibility reviewer | Product Owner |

The implementer cannot act as the sole independent reviewer or approve their own
gate.

## Estimation and forecasting

Roadmap target ranges are rough-order estimates. A phase plan records:

- work packages and dependencies;
- available implementer and reviewer capacity;
- optimistic, most-likely and pessimistic effort;
- assumptions and confidence level;
- explicit review, remediation, rehearsal and deployment effort; and
- contingency matched to the RAID register.

Only accepted work enters the committed forecast. Optional work and unresolved
decisions remain outside it. Forecasts use calendar dates only after capacity and
review availability are known.

## Status cadence

During active work, update [`status.md`](status.md) at least weekly and whenever
a gate decision, critical risk, material scope change or critical-path blocker
occurs. Status uses accepted deliverables, not subjective percentages. Keep the
file limited to controlling current state, the immediate gate sequence and
archive links. Move superseded or historical blocks verbatim into a dated file
beside `status.md` so its original relative links remain valid, index it under
[`status-archive/`](status-archive/), record its archival hash there, and do not
rewrite the archived evidence.

Keep [`Handover information`](../review/Handover%20information) limited to the
active assignment, controlling restrictions, immediate handoff and archive
links. Move consumed or superseded blocks verbatim into a dated file under
`docs/review/` so its original relative links remain valid, and index it under
[`handover-archive/`](../review/handover-archive/). Dedicated prompts, handbacks,
reviews, decisions and registers remain the durable records; archive movement
changes none of their dispositions or authorities.

## Communication and escalation

- The Delivery Lead circulates the status record to the Product Owner,
  Technical Lead and affected specialist owners at least weekly during active
  delivery.
- A proposed scope or baseline change is raised before implementation through
  `change-log.md`.
- A security, privacy, identity, financial-integrity, data-loss or production-
  reliability issue is escalated immediately to the relevant specialist owner
  and Acceptance Authority; dependent work stops at the gate.
- A decision or dependency that reaches its required-by milestone unresolved is
  reported as `not ready`, with forecast impact. It is not converted into an
  implementation assumption.
- Gate decisions and accepted residual risks are recorded in writing; meeting
  notes or an agent response alone are not the durable approval record.
