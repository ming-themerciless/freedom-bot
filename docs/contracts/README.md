# Contracts

Accepted and proposed interface contracts for the Freedom Blades platform:
routes, view models, logical schema, state machines, configuration and the
security design that governs them.

A contract here is **not** an implementation authorization. Each states its own
status. A `Proposed` contract has no force until the Acceptance Authority records
its gate decision.

## Phase 3 — P3.0 contract and security design baseline

Status: **Accepted 2026-08-13; P3.G0 closed.** Peter Duscha accepted the complete
remediated contract/security baseline after Codex independent architecture and
security-focused re-review, including corrected N-43, widened N-65, new N-67,
ADR 0010, R-38 and mapping provenance. See
[`../review/phase-3-p3-0-remediation-submission.md`](../review/phase-3-p3-0-remediation-submission.md)
for the finding-by-finding change map. Acceptance authorizes Claude to begin P3.1
once its disposable-PostgreSQL prerequisite is confirmed. P3.0 itself added no
runtime code, and its named implementation tests remain unrun until their owning
packages implement them.

Read in this order:

| # | Artifact | What it settles |
|---|---|---|
| 1 | [`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md) | Every numeric policy, defined once. All other artifacts cite `N-nn` |
| 2 | [`phase-3-route-authorization-contract.md`](phase-3-route-authorization-contract.md) | The closed set of P3.1–P3.3 routes, the authorization chain, the seven-role matrices and the eighth caller state, denial codes, and the proof that UI hiding is not authorization |
| 3 | [`phase-3-view-model-contract.md`](phase-3-view-model-contract.md) | Version `vm-1`: typed, bounded, pre-authorized view models and the escaping rules. Frozen for Gemini at P3.G2/P3.G3 |
| 4 | [`phase-3-logical-schema.md`](phase-3-logical-schema.md) | The ER model and schema decision table required by plan §7.3.1 |
| 5 | [`phase-3-identity-migration-contract.md`](phase-3-identity-migration-contract.md) | Staged, reversible migration off Discord-keyed authorization, and the Council-confirmed Sheet-era evidence pipeline |
| 6 | [`phase-3-state-machines.md`](phase-3-state-machines.md) | OAuth, session, break-glass, identity linking, jobs, the membership projection and mapping provenance, with forbidden transitions and failure behaviour |
| 7 | [`phase-3-threat-model.md`](phase-3-threat-model.md) | Assets, boundaries, attackers, 54 threats, controls, residual risks and verification mapping |
| 8 | [`phase-3-configuration-and-dependency-contract.md`](phase-3-configuration-and-dependency-contract.md) | The smallest justified dependency set, the typed configuration contract and fifteen startup refusals |
| 9 | [`phase-3-operational-contract.md`](phase-3-operational-contract.md) | Topology, the public perimeter, the worker finding, the kill switch, monitoring and recovery |
| 10 | [`phase-3-test-traceability.md`](phase-3-test-traceability.md) | Every acceptance and mandatory-test row expanded into named tests, with evidence classes |

Related records outside this directory:

- [`../adr/0010-provider-neutral-identity-and-emergency-administration.md`](../adr/0010-provider-neutral-identity-and-emergency-administration.md)
  — the proposed ADR this package rests on;
- [`../review/phase-3-delivery-plan.md`](../review/phase-3-delivery-plan.md) —
  the accepted plan, and the authoritative source for every §7/§8/§9 value;
- [`../review/phase-3-p3-0-submission.md`](../review/phase-3-p3-0-submission.md)
  — the P3.0 handoff: inventory, decisions, assumptions, residual risks, commands
  run and the review request.

## Conventions

- **One authoritative definition.** A number lives in the numeric register; a
  route lives in the route contract; a table lives in the schema. Other documents
  cite an identifier rather than copying a value.
- **Status lines are load-bearing.** `Proposed` means exactly that.
- **Absences are contracts too.** Several controls here are the absence of a
  route, a column or a capability, and each names the test that keeps it absent.
