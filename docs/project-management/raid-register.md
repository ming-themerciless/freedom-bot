# RAID register

Status date: 2026-08-02

Scale: probability and impact are `Low`, `Medium` or `High`. The Delivery Lead
updates status and due dates; the named role owns the response. A person's name
must replace each role assignment before the affected work starts.

## Risks

| ID | Risk | Probability | Impact | Owner | Mitigation / trigger / contingency | Status |
|---|---|---|---|---|---|---|
| R-01 | Sheet row identity ambiguity corrupts character identity | Medium | High | Data Owner | Fail closed on mapped semantic name changes; one shared display-name comparison policy (`domain/names.py`) used by parser, service and both repositories; regression and PostgreSQL tests. Trigger: any unexplained name/mapping change. Contingency: stop import, roll back, reconcile mappings deliberately. | Active; mitigation independently reviewed by Codex and accepted by Peter Duscha on 2026-08-02. Residual: the database still enforces no display-name uniqueness, and the legacy bot lookup uses its own comparison |
| R-02 | Real Foundry snapshot differs from synthetic contract | High | High | Data Owner | Versioned exhaustive profile and supervised rehearsal. Trigger: unknown path/version/shape. Contingency: reject snapshot and revise contract through change control. | Active |
| R-03 | Phase 5 scope cannot fit its roadmap range | High | High | Delivery Lead | Split into gated work packages and estimate each after discovery. Trigger: any package not meeting ready criteria. Contingency: rebaseline release scope; never compress tests or gates. | Active |
| R-04 | Authorization gap permits mutation of another character | Medium | High | Security Reviewer | Resolve OD-16/17/39; server-side linked-character and role checks; denial tests. Trigger: any unauthenticated or cross-character success. Contingency: disable affected command/feature until fixed. | Active |
| R-05 | PostgreSQL-only behavior is missed when integration tests are skipped | Medium | High | Technical Lead | Maintain disposable guarded database and require database evidence at mutation/import gates. Trigger: skipped required DB suite. Contingency: gate remains deferred. | Active |
| R-06 | Cutover or rollback loses live-bot availability | Medium | High | Operations Owner | Feature flags, backups, rehearsed restore/rollback, monitoring and verification window. Trigger: failed health/reconciliation check. Contingency: return to accepted Sheet-backed path within documented recovery objective. | Active |
| R-07 | Foundry or dnd5e version changes invalidate integration | Medium | Medium | Technical Lead | Explicit supported versions and fail-safe negotiation. Trigger: deployment version outside range. Contingency: stop import/sync pending contract update. | Active |
| R-08 | Catalogue content creates licensing or provenance exposure | Medium | High | Product Owner | Pinned provenance, allowlist, minimum authorized content, legal review where needed. Trigger: uncertain redistribution right. Contingency: retain identifiers/source references only. | Future |
| R-09 | Reviewer or maintainer capacity delays critical gates | High | Medium | Delivery Lead | Book review windows in phase plan; expose queue in status. Trigger: no reviewer by ready date. Contingency: reforecast, not self-approve. | Active |
| R-10 | Requirements continue growing inside active phases | High | High | Product Owner | Controlled baseline and impact-assessed change requests. Trigger: new mandatory outcome after phase start. Contingency: defer or rebaseline with explicit approval. | Active |

## Assumptions

| ID | Assumption | Owner | Validation / deadline | Status |
|---|---|---|---|---|
| A-01 | One focused implementer is the basis of roadmap effort ranges | Delivery Lead | Confirm capacity before each phase baseline | Unvalidated |
| A-02 | A guarded disposable PostgreSQL environment remains available | Operations Owner | Confirm before every database gate | Previously demonstrated; reconfirm per gate |
| A-03 | Maintainers can provide a supervised immutable Foundry snapshot rehearsal | Data Owner | Required before Phase 2 gate | Unvalidated operationally |
| A-04 | The legacy Sheet-backed bot remains the rollback implementation until approved cutover | Operations Owner | Validate at each Phase 5 cutover | Active |

## Issues

| ID | Issue | Owner | Resolution condition | Status |
|---|---|---|---|---|
| I-01 | Phase 2 mapped-name normalization semantics differ between Python and PostgreSQL lookup | Technical Lead | Shared policy plus service/PostgreSQL regression evidence and re-review | **Closed 2026-08-02** — implementation and PostgreSQL evidence independently reviewed by Codex; accepted by Peter Duscha. The database-enforcement residual remains I-05 |
| I-05 | `characters.display_name` has no database uniqueness rule, so the shared comparison policy is enforced by the importer alone | Data Owner | A decided uniqueness policy and a migration storing/indexing the identity key, or a recorded acceptance that the application enforces it | Open — raised 2026-08-02 as the residual of I-01 |
| I-02 | Phase 2 Foundry snapshot milestone is incomplete | Technical Lead | All §12 Phase 2 deliverables and gate evidence complete | Open |
| I-03 | Package-specific implementer/reviewer capacity is not yet recorded | Delivery Lead | Record agent assignments and Peter's decision/review availability during package readiness | Managed per package |
| I-04 | Proposed baseline v1.0 is not accepted | Acceptance Authority | Approval recorded in change log | Closed 2026-08-02 |

## Dependencies

| ID | Dependency | Needed by | Owner | Satisfied when | Status |
|---|---|---|---|---|---|
| D-01 | Approved field ownership/profile | Phase 2 import | Data Owner | Versioned exhaustive profile accepted | In progress |
| D-02 | Phase 2 data-integrity gate | Phase 3 | Acceptance Authority | Gate decision is approved | Open |
| D-03 | Accepted visual prototype and stable view-model contracts | Phase 3 frontend | Product Owner / Technical Lead | Separate visual gate and backend contract approval close | Open |
| D-04 | Shared ledger/idempotency/domain foundations | Phase 5 mutations | Technical Lead | Phase 4 gate approved | Open |
| D-05 | Catalogue and inventory foundations | Phase 5 crafting | Product Owner / Data Owner | Package 5.6a gate approved | Open |
| D-06 | Mission and attendance records | Phase 9 settlement | Product Owner | Phase 8 gate approved | Open |
| D-07 | Basic Bastion state | Phase 11 facilities | Product Owner | Phase 10 gate approved | Open |
