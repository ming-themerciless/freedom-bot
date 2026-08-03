# RAID register

Status date: 2026-08-02

Scale: probability and impact are `Low`, `Medium` or `High`. The Delivery Lead
updates status and due dates; the named role owns the response. A person's name
must replace each role assignment before the affected work starts.

## Risks

| ID | Risk | Probability | Impact | Owner | Mitigation / trigger / contingency | Status |
|---|---|---|---|---|---|---|
| R-01 | Sheet row identity ambiguity corrupts character identity | Medium | High | Data Owner | Fail closed on mapped semantic name changes; one shared display-name comparison policy (`domain/names.py`) used by parser, service and both repositories; regression and PostgreSQL tests. Trigger: any unexplained name/mapping change. Contingency: stop import, roll back, reconcile mappings deliberately. | Active; mitigation independently reviewed by Codex and accepted by Peter Duscha on 2026-08-02. Residual narrowed 2026-08-02 by OD-42: the absence of database display-name uniqueness is now a deliberate accepted decision, not an open gap, so the remaining residual is that the legacy bot lookup uses its own comparison until its owning package migrates |
| R-02 | Real Foundry snapshot differs from synthetic contract | High | High | Data Owner | Versioned exhaustive profile and supervised rehearsal. Trigger: unknown path/version/shape. Contingency: reject snapshot and revise contract through change control. | Active |
| R-03 | Phase 5 scope cannot fit its roadmap range | High | High | Delivery Lead | Split into gated work packages and estimate each after discovery. Trigger: any package not meeting ready criteria. Contingency: rebaseline release scope; never compress tests or gates. | Active |
| R-04 | Authorization gap permits mutation of another character | Medium | High | Security Reviewer | Resolve OD-16/17/39; server-side linked-character and role checks; denial tests. Trigger: any unauthenticated or cross-character success. Contingency: disable affected command/feature until fixed. | Active |
| R-05 | PostgreSQL-only behavior is missed when integration tests are skipped | Medium | High | Technical Lead | Maintain disposable guarded database and require database evidence at mutation/import gates. Trigger: skipped required DB suite. Contingency: gate remains deferred. | Active |
| R-06 | Cutover or rollback loses live-bot availability | Medium | High | Operations Owner | Feature flags, backups, rehearsed restore/rollback, monitoring and verification window. Trigger: failed health/reconciliation check. Contingency: return to accepted Sheet-backed path within documented recovery objective. | Active |
| R-07 | Foundry or dnd5e version changes invalidate integration | Medium | Medium | Technical Lead | Explicit supported versions and fail-safe negotiation. Trigger: deployment version outside range. Contingency: stop import/sync pending contract update. | Active |
| R-08 | Catalogue content creates licensing or provenance exposure | Medium | High | Product Owner | Pinned provenance, allowlist, minimum authorized content, legal review where needed. Trigger: uncertain redistribution right. Contingency: retain identifiers/source references only. | Future |
| R-09 | Reviewer or maintainer capacity delays critical gates | High | Medium | Delivery Lead | Book review windows in phase plan; expose queue in status. Trigger: no reviewer by ready date. Contingency: reforecast, not self-approve. | Active |
| R-10 | Requirements continue growing inside active phases | High | High | Product Owner | Controlled baseline and impact-assessed change requests. Trigger: new mandatory outcome after phase start. Contingency: defer or rebaseline with explicit approval. | Active |
| R-11 | Longer legacy-Sheet operation causes drift or cutover failure before typed packages migrate all fields | Medium | High | Operations Owner / Data Owner | No dual writes; characterize each field group; package-owned deterministic migration, reconciliation totals, feature-flag cutover and rehearsed rollback. Trigger: unexplained source/target difference or legacy behavior without a typed replacement. Contingency: keep that field on the legacy path and defer its cutover. | Active — introduced by baseline v1.1 |
| R-12 | A legacy field is omitted, duplicated or migrated by the wrong package | Low | High | Data Owner | Controlled exhaustive migration register, automated profile/inventory consistency check and one accountable package per row. Trigger: new/renamed source field or conflicting target. Contingency: stop the affected package/cutover and amend the register through change control. | Active — introduced by baseline v1.2 |
| R-13 | A scalar legacy aggregate is expanded into invented event history or an uncontrolled vocabulary creates duplicate identities | Medium | High | Data Owner / Product Owner | Typed opening facts, no-synthetic-history rule, machine-readable source manifest and controlled vocabulary register. Trigger: migration proposes events unsupported by source records or creates a definition from unmatched text. Contingency: stop migration, preserve explicit unresolved data and obtain a Data Owner ruling. | Active — introduced by baseline v1.5 |

## Assumptions

| ID | Assumption | Owner | Validation / deadline | Status |
|---|---|---|---|---|
| A-01 | One focused implementer is the basis of roadmap effort ranges | Delivery Lead | Confirm capacity before each phase baseline | Unvalidated |
| A-02 | A guarded disposable PostgreSQL environment remains available, including a restricted runtime role that can be assumed for denial evidence | Operations Owner | Confirm before every database gate | **Partly validated 2026-08-02.** The disposable database `freedom_test` and the owner/test login `foundry` are available. The temporary restricted role `freedom_runtime_test` now **exists** and can be assumed: it is `NOLOGIN`, non-superuser, cannot create roles or databases, cannot replicate, cannot bypass RLS, and `foundry` is a member able to `SET ROLE freedom_runtime_test`. Role creation is therefore no longer an evidence gap. Outstanding: applying the runtime grants for the **final retained** schema and running direct denial tests under that role |
| A-03 | Maintainers can provide a supervised immutable Foundry snapshot rehearsal | Data Owner | Required before Phase 2 gate | **Partly validated 2026-08-02.** Two maintainer-authorized example exports exist outside the repository at `/opt/discord-bots/foundry-actor-exports`, so artifact availability is no longer assumed. The supervised real-export preview rehearsal itself remains **unperformed**, and no export was read during package planning |
| A-04 | The legacy Sheet-backed bot remains the rollback implementation until approved cutover | Operations Owner | Validate at each Phase 5 cutover | Active |

## Issues

| ID | Issue | Owner | Resolution condition | Status |
|---|---|---|---|---|
| I-01 | Phase 2 mapped-name normalization semantics differ between Python and PostgreSQL lookup | Technical Lead | Shared policy plus service/PostgreSQL regression evidence and re-review | **Closed 2026-08-02** — implementation and PostgreSQL evidence independently reviewed by Codex; accepted by Peter Duscha. The database-enforcement residual remains I-05 |
| I-05 | `characters.display_name` has no database uniqueness rule, so the shared comparison policy is enforced by the importer alone | Data Owner | A decided identity/uniqueness policy recorded as a maintainer ruling, or a recorded acceptance that the application enforces it | **Closed 2026-08-02** by OD-42, ruled by Peter Duscha: display names are not unique identities, multiple characters may share one, stable character IDs and external Actor IDs provide identity, and any legacy name-based candidate lookup fails closed when more than one candidate exists. No unique display-name constraint is added; the application enforcement is accepted deliberately. Package R2 implements the multi-candidate fail-closed lookup |
| I-02 | Phase 2 implementation contains the rejected ADR 0008 interim state/bootstrap/correction path | Technical Lead | Baseline the replacement plan; remove rejected scope; implement deferred legacy reporting; close Codex blocking findings; pass current-baseline §12 evidence; complete operational rehearsals | Open — not ready for remediation until replacement plan is accepted |
| I-03 | Package-specific implementer/reviewer capacity is not yet recorded | Delivery Lead | Record agent assignments and Peter's decision/review availability during package readiness | Managed per package |
| I-04 | Proposed baseline v1.0 is not accepted | Acceptance Authority | Approval recorded in change log | Closed 2026-08-02 |

## Dependencies

D-01 was split on 2026-08-02 into D-01a and D-01b. The single row conflated a
Phase 2 precondition with a per-package one and therefore made every future
vocabulary decision read as a Phase 2 blocker, which it is not: Phase 2
classifies and defers legacy fields, and migrates none of them. The split is a
clarification of dependency granularity, not a scope change; no register row,
package allocation or gate criterion is altered by it.

| ID | Dependency | Needed by | Owner | Satisfied when | Status |
|---|---|---|---|---|---|
| D-01a | Exhaustive snapshot classification, accountable legacy disposition, and proof that no interim editable Sheet-state representation exists | Phase 2 import only | Data Owner | Every supported snapshot path carries exactly one classification and an unknown path fails closed; every known legacy source/profile field has exactly one accountable owning package in the migration register/manifest and is reported as `legacy_authority_deferred` rather than compared; and no Phase 2 table, repository API or write path holds a second editable copy of a legacy Sheet field | In progress — the sole register dependency of the Phase 2 gate |
| D-01b | Readiness of each controlled vocabulary in `data-vocabulary-register.md` | Only the typed migration package that uses that vocabulary | Data Owner | For that package alone: source identity, version, alias/merge policy, licensing/provenance, retirement behavior, steward and unresolved-value workflow are decided and dated | Open per package. **Vocabulary readiness does not block Phase 2**, which classifies and reports legacy fields without migrating, normalizing or writing them |
| D-02 | Phase 2 data-integrity gate | Phase 3 | Acceptance Authority | Gate decision is approved | Open |
| D-03 | Accepted visual prototype and stable view-model contracts | Phase 3 frontend | Product Owner / Technical Lead | Separate visual gate and backend contract approval close | Open |
| D-04 | Shared ledger/idempotency/domain foundations | Phase 5 mutations | Technical Lead | Phase 4 gate approved | Open |
| D-05 | Catalogue and inventory foundations | Phase 5 crafting | Product Owner / Data Owner | Package 5.6a gate approved | Open |
| D-06 | Mission and attendance records | Phase 9 settlement | Product Owner | Phase 8 gate approved | Open |
| D-07 | Basic Bastion state | Phase 11 facilities | Product Owner | Phase 10 gate approved | Open |
