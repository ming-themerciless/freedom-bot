# Project governance

Status: Accepted with baseline v1.0 on 2026-08-02

This directory contains the management controls for the Freedom Blades
Platform. The technical scope remains governed by
[`docs/implementation-plan.md`](../implementation-plan.md).

## Solo-maintainer operating model

Peter Duscha is the Product Sponsor, Acceptance Authority, Product Owner, Data
Owner, Operations Owner and Delivery Lead. Agents may implement, coordinate and
independently review work. For each package, Peter designates an implementing
agent as working Technical Lead and, where practical, a different agent as
Independent Reviewer. Security-sensitive packages receive a separate security-
focused review. Agent reviews are recommendations; Peter records gate and risk-
acceptance decisions.

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
occurs. Status uses accepted deliverables, not subjective percentages.

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
