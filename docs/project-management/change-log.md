# Baseline and change log

This is the approval record for material project-plan changes. Entries are
append-only; a correction adds a new entry that supersedes an earlier one.

| Version / change | Date | Requester | Summary | Scope / schedule / risk effect | Reviews | Approval |
|---|---|---|---|---|---|---|
| v1.0 | 2026-08-02 | Peter Duscha | Adds document control, accountable roles, gate governance, success measures, dependency map, RAID/decision/status controls and decomposes oversized roadmap work | Technical product scope preserved; schedule ranges become non-commitment planning inputs; exposes existing Phase 2 and Phase 5 risks | Reviewed for internal consistency and local-link validity by Codex | **Accepted by Peter Duscha on 2026-08-02** |
| v1.1 | 2026-08-02 | Peter Duscha | Rejects ADR 0008; removes Phase 2 migration of Sheet-era state; assigns each field group’s one-time migration to its typed domain package | Removes interim state/bootstrap/correction scope from Phase 2; adds package-level reconciliation, recovery and cutover evidence later; reduces double-migration and weak-constraint risk; Phase 2 implementation/remediation must be re-estimated | Plan and acceptance-criteria review by Codex; technical implementation re-review still required after remediation | **Accepted by Peter Duscha on 2026-08-02 in this review conversation** |
| v1.2 | 2026-08-02 | Peter Duscha | Closes the v1.1 management-review findings: deferred legacy comparisons, read-only Phase 3, exhaustive migration allocation, universal mutation-test matrix, boundary-specific gate evidence, superseded Phase 2 plan and executable next actions | Removes contradictory Phase 2/3 scope; adds one accountable package for every known legacy field; increases planning/evidence work before later mutation packages but reduces omission, double-authority and unverifiable-gate risk | Best-practice project-management review and consistency amendments by Codex; implementation and replacement package-plan review remain pending | **Accepted by Peter Duscha through the instruction to amend the plan on 2026-08-02** |
| v1.3 | 2026-08-02 | Peter Duscha | Requires every multi-valued Google Sheet source to migrate into normalized relational reference/child/junction tables with foreign keys | Prohibits delimited, JSON/JSONB, PostgreSQL-array and generic key/value list storage; adds schema-design, migration-control-total and PostgreSQL constraint evidence to each owning package | Architecture/project-control amendment by Codex; package schemas remain subject to independent review | **Accepted by Peter Duscha through the explicit relational-table direction on 2026-08-02** |
| v1.4 | 2026-08-02 | Peter Duscha | Clarifies that relational normalization applies to authoritative multi-valued operational domain facts, using typed owned child rows when no shared definition identity exists | Retains strict migration integrity while exempting bounded immutable evidence, audit context, diagnostics, preserved external payloads and disposable presentation caches from artificial decomposition; exceptions cannot become operational authority | Architecture clarification by Codex; no implementation gate is bypassed | **Accepted by Peter Duscha through explicit confirmation on 2026-08-02** |
| v1.5 | 2026-08-02 | Peter Duscha | Closes the v1.4 management-review findings: preserves scalar aggregates as opening facts, governs vocabularies, makes source allocation machine-readable, adds schema readiness and correction gates, fixes dependencies and separates Phase 5 cutover from Sheet retirement | Prevents invented history and vocabulary identities; adds manifest/register/schema review work before packages; strengthens traceability, referential integrity and retirement controls without adding committed dates | Best-practice project-management amendment by Codex; replacement Phase 2 and future package plans remain subject to readiness/review | **Accepted by Peter Duscha through the instruction to amend the plan on 2026-08-02** |

| v1.5 clarification C-1 | 2026-08-02 | Peter Duscha | Splits RAID dependency D-01 into D-01a/D-01b, registers the I-05 identity ruling as proposed decision OD-42, corrects A-02/A-03 and the Phase 2 critical path for the now-existing restricted role and available example exports, and tightens the Independent Reviewer wording at mandatory checkpoints | No roadmap, phase order, release boundary, scope, authority, privacy, architecture, data-ownership or release criterion changes. Dependency granularity, evidence status and reviewer wording only; the reviewer change strengthens an existing control and weakens none | Prepared with the replacement Phase 2 remediation plan; independent review of that plan pending | **Accepted by Peter Duscha on 2026-08-02** |
| v1.5 clarification C-2 | 2026-08-02 | Peter Duscha | Records four rulings taken with the acceptance of the replacement Phase 2 remediation plan: OD-42 (display-name identity policy, closing I-05); the disposition of `tools/import_sheet_characters.py`; the security-review assignment; and the timing of the §9.4 operational windows | No roadmap, phase order or release-boundary change. OD-42 confirms and completes an existing identity policy without adding a schema constraint; the CLI ruling reverts an uncommitted modification and allocates the tool's disposition to package 5.1, which the migration register already owns; the review and window rulings are delivery controls. Releases packages R1–R3 to start; R4 remains blocked on the §9.4 values | Recommendations from the working Technical Lead (Claude); independent review of the remediated implementation still required | **Accepted by Peter Duscha on 2026-08-02** |

## v1.5 clarification C-2 — rulings recorded with the plan acceptance

- **Replacement plan (D-1):** `docs/review/phase-2-v1.5-remediation-plan.md` is
  **accepted** as the executable Phase 2 remediation plan. The superseded
  `phase-2-package-plan.md` remains non-executable.
- **OD-42 / I-05 (D-2):** ruled as recommended. Display names are not unique
  identities; multiple characters may share one; stable character IDs and
  external Actor IDs provide identity; any legacy name-based candidate lookup
  fails closed when more than one candidate exists. **No unique display-name
  constraint is added.** I-05 is closed; R-01's residual narrows accordingly.
- **`tools/import_sheet_characters.py` (D-3):** the I-02 modifications are
  reverted to the committed state and the tool is recorded as **dormant**, with
  its disposition owned by package **5.1**. It is not a Phase 2 write path, which
  is what allows threshold T-6 to be asserted cleanly. This removes no accepted
  I-01 work.
- **Security review (D-5):** Codex performs both the independent review and a
  **distinct, separately reported** security-focused pass covering
  authorization, artifact handling, audit content and runtime grants. The
  implementer never reviews their own work.
- **Windows (D-4):** the §9.4 values — rehearsal window, observation period and
  preview/apply runtime budget — are required **before package R4** rather than
  before any work. R1–R3 are released to start; R4 is not ready until they are
  set.

**Classification: clarification, not a new baseline version.** As with C-1, no
§0.2 trigger for a new baseline is met: OD-42 completes an identity policy the
accepted record already established in three of its four clauses and adds no
schema object; the CLI ruling reverts uncommitted work within scope that
baseline v1.1 already removed; and the review and window rulings are delivery
controls. Scope, phase order, release criteria and target ranges are unchanged.

## v1.5 clarification C-1 — baseline classification

**Classification: clarification under §0.2, not a new baseline version.** §0.2
requires a new baseline version only *"when the roadmap or release boundary
changes"*. Assessed against the five §0.2 triggers:

- **scope** — unchanged. No requirement, deliverable, package or acceptance
  criterion is added, removed or reallocated. D-01a/D-01b restate the same
  satisfaction conditions at the granularity they actually apply to.
- **authority** — unchanged in substance. The Independent Reviewer wording
  removes an ambiguity (*"where practical"* read as optional at mandatory
  checkpoints) by stating the control that §16.4 and the gate-authority table
  already impose. It tightens; a tightening of a review control cannot weaken a
  gate invariant, and the deferral outcome it names is an existing gate state.
- **privacy, architecture, data ownership** — untouched. OD-42 is *recorded as
  proposed*; it takes effect only when the Acceptance Authority rules it, and
  recording a proposal is not a decision.
- **release criteria, phase order, target range** — untouched. The corrected
  critical path re-sequences nothing that was previously approved; it replaces a
  five-step summary that omitted plan approval, implementation and
  implementation re-review with the eight steps those documents already require.

A dated entry is therefore required and given; a new baseline version is not.
**If** the Acceptance Authority rules OD-42, that ruling is a data-ownership
decision and receives its own dated entry — still without a new baseline, since
it changes no roadmap or release boundary.

## v1.5 impact assessment

- **Affected requirements:** §§7.3, 12 Phase 5, 13, 15 and 20; migration and
  vocabulary registers; Phase 2 readiness/status.
- **Reason:** scalar counters/dates cannot support reconstructed event history;
  reference tables require governed identity sources; prose-only coverage was
  insufficient evidence of exhaustive allocation.
- **Scope/schedule:** owning packages add opening-baseline models, vocabulary
  decisions, reviewed ER/schema tables, correction workflows and manifest
  checks. Estimates are updated at package readiness; no unbaselined target is
  converted into a calendar commitment.
- **Risk:** eliminates synthetic-history and accidental-vocabulary risks and
  reduces omitted/duplicate source risk. Unresolved Campaign Counter semantics
  remain explicit and block its Phase 8 migration behavior.
- **Testing/operations:** machine-readable manifest checks exact profile/player/
  linkage coverage and package validity; package gates require schema,
  correction, migration and PostgreSQL evidence; Sheet retirement remains
  blocked by every later legacy row.

## v1.4 impact assessment

- **Affected requirements:** §7.3.1, §15 and the migration register.
- **Reason:** preserve the intended relational integrity without inventing
  meaningless global reference entities or decomposing immutable evidence and
  audit/provenance context into operational tables.
- **Scope/schedule:** no authoritative migration scope is removed. Free-form
  owned collections use typed child rows; shared vocabularies use definition
  plus junction tables. Evidence/metadata exceptions require bounded storage,
  access and retention review rather than domain normalization.
- **Risk/control:** prevents both serialized operational state and dogmatic
  over-normalization. An exception cannot drive authoritative calculation,
  satisfy a migration or become editable state; crossing that boundary requires
  normalization and a package gate.

## v1.3 impact assessment

- **Affected requirements:** §§7.3, 13 and 15; every package owning a
  multi-valued legacy field; the controlled migration register.
- **Reason:** use relational identity, referential integrity, uniqueness and
  typed constraints rather than preserving spreadsheet list encodings.
- **Scope/schedule:** package schema and migration work increases for vocabulary
  definitions, child/junction tables and unresolved-value workflows. Estimates
  must include that work before readiness; no existing calendar commitment is
  changed because those packages are not baselined.
- **Risk:** lowers orphan, typo, duplicate, inconsistent-vocabulary and opaque-
  query risks; raises up-front mapping effort and explicit unresolved-data work.
- **Testing/operations:** adds real PostgreSQL foreign-key, uniqueness, delete-
  behavior, control-total and idempotent migration tests. Serialized collection
  storage is a blocking schema-review finding unless separately approved by ADR.

## v1.2 impact assessment

- **Affected requirements:** §§6, 12 Phases 2, 3 and 5, 13, 15 and 20;
  Phase 2 package planning; project status; legacy migration controls.
- **Reason:** baseline v1.1 left impossible legacy comparisons, premature Phase
  3 correction tests, an executable stale package plan and no exhaustive
  field-to-package allocation.
- **Scope:** Phase 3 is explicitly read-only for game state; correction UI moves
  to typed migration packages. Phase 2 reports `legacy_authority_deferred` when
  no accepted database value exists. Every known character/player field has one
  accountable migration package.
- **Schedule/capacity:** Phase 2 remains not ready pending a replacement estimate
  and named capacity. Later package estimates must include their allocated
  migrations and the universal persistent-mutation evidence matrix.
- **Risk:** reduces fabricated comparison, orphan-field, duplicate-authority and
  premature-web-mutation risks; adds register maintenance controlled by Data
  Owner review and change control.
- **Testing/operations:** adds a mandatory matrix for authorization, boundaries,
  concurrency, constraints, injected failures, migration/rerun, recovery,
  runtime-role bypass, monitoring and staging; gate evidence is selected by the
  actual web, Discord, CLI and database surfaces.
- **Approval/evidence:** defines the Phase 2 Data Owner attestation contents and
  durable storage without committing real Actor data.

## v1.1 impact assessment

- **Affected requirements:** §§6.1, 6.2, 6.5, 7.3, 12 Phase 2 and 15.
- **Reason:** avoid creating a weakly constrained generic store that would be
  migrated again before the owning domain rules and schemas exist.
- **Alternative rejected:** ADR 0008's temporary profile-driven state and
  balance tables.
- **Removed scope:** Phase 2 Sheet bootstrap, generic character-state storage,
  and Foundry-to-database corrections for unmigrated fields.
- **Added/deferred scope:** every typed domain package owns one deterministic
  migration, reconciliation, correction workflow, rollback and cutover gate.
- **Schedule/capacity:** Phase 2 must be re-estimated after removal of rejected
  implementation; later package estimates must include migration and Data Owner
  review. No calendar commitment is inferred.
- **Risk:** lowers weak-constraint and double-migration risk; extends the period
  in which the legacy Sheet path remains operational and therefore increases
  dependency/cutover exposure managed by R-06 and package feature flags.
- **Testing/operations:** Phase 2 retains parser, identity, mapping,
  authorization, PostgreSQL concurrency, role-denial, backup/restore and real
  rehearsal evidence. Later packages receive explicit migration, injected
  failure, reconciliation, authorization, audit, restore and rollback criteria.
- **Security/data authority:** no dual writes; legacy authority continues per
  field until an approved typed-package cutover. Existing production writes are
  not frozen prematurely.

## Required fields for later entries

Every material entry must identify:

- affected requirement, milestone and release;
- reason and alternatives considered;
- added/removed scope;
- dependency and critical-path effect;
- estimate/forecast and capacity effect;
- new or changed risks;
- testing, migration, security and operational effect;
- Product Owner recommendation;
- Technical Lead and specialist reviews; and
- dated Acceptance Authority decision.
