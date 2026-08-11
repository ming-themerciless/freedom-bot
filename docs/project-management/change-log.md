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

| v1.5 clarification C-3 | 2026-08-04 | Peter Duscha | Records the Phase 2 I-03 snapshot submission package: a Foundry v14 module, a scoped-service-principal HTTPS submission endpoint, restricted artifact storage and a Council preview contract | No roadmap, phase order or release-boundary change. Brings forward the **read-only submission half** of the Phase 7 module and its scoped credential, and introduces one non-browser HTTP route ahead of Phase 3 without creating any portal, session, OAuth or CSRF surface. Adds one additive, reversible migration (`0004`) and one proposed ADR (`0009`). Submission applies nothing; apply authority, field ownership and the Phase 2 gate evidence are unchanged | Package plan and impact assessment by the working Technical Lead (Claude), `docs/review/phase-2-i-03-package-plan.md`; **independent implementation review and separate security-focused review still required** | **Not yet decided.** Recorded for the Acceptance Authority |

| v1.5 clarification C-4 | 2026-08-04 | Peter Duscha | Accepts ADR 0009: the snapshot submission endpoint is a stdlib WSGI application, and FastAPI is not introduced by the Phase 2 I-03 package | No roadmap, phase order or release-boundary change. ADR 0002 is unchanged — FastAPI remains the recorded choice for the Phase 3 web application, and the WSGI application mounts inside it unchanged. Adds no dependency. Accepts the architectural decision **only**: the I-03 implementation still requires independent implementation review and a separate security-focused review, and no further HTTP surface is authorized | Proposed by the working Technical Lead (Claude) in `docs/adr/0009-snapshot-submission-http-boundary.md`, with alternatives recorded | **Accepted by Peter Duscha on 2026-08-04** |
| v1.5 clarification C-8 | 2026-08-05 | Peter Duscha | Accepts retention decision D-c for database-unclaimed raw Foundry snapshot artifacts | No scope, authority, architecture, phase-order or release-boundary change. Raw artifacts are retained at most 30 days and deleted sooner after their rehearsal, retry or incident closes; checksum, provenance and sanitized audit remain permanent | Operations procedure and I-03 package-plan amendment; independent implementation review remains required for the complete Phase 2 gate | **Accepted by Peter Duscha on 2026-08-05** |
| v1.5 clarification C-9 | 2026-08-05 | Peter Duscha | Sets Phase 2 R4 observation and synthetic 500-Actor runtime thresholds | No scope, authority, architecture, phase-order or release-boundary change. Rehearsal observation is immediate verification followed by shutdown/cleanup; acceptance thresholds are 5 seconds preview and 5 seconds fresh apply on the named host | Synthetic PostgreSQL benchmark and Codex independent reproduction; real-export rehearsal remains pending | **Accepted by Peter Duscha on 2026-08-05** |

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

## v1.5 clarification C-3 — Phase 2 I-03 snapshot submission package

Recorded 2026-08-04 by the working Technical Lead. **The Acceptance Authority
has not decided it.** The full package plan and impact assessment is
[`../review/phase-2-i-03-package-plan.md`](../review/phase-2-i-03-package-plan.md);
this entry is the change-control summary the required-fields list below asks for.

- **Affected requirements:** §6.3 and §6.4 (the artifact and its provenance),
  §12 Phase 2 (import and reconciliation), §12 Phase 7 (the Foundry module and
  its scoped credential), §12.0 (the Phase 3 gate releases production portal
  integration), §7.1 (`service_principals`) and §9.2–9.3 (web and infrastructure
  security).
- **Reason:** the maintainer requires snapshot submission without SSH, without
  locating a Foundry database and without manually placing a file on the server.
- **Added scope:** `foundry-module/`; the submission application service;
  restricted, content-addressed artifact storage; one WSGI route; a Council
  preview contract; migration `0004`; ADR `0009`.
- **Removed scope:** none. The file-based operator path remains, as a documented
  fallback.
- **Phase-boundary effect:** brings forward the **read-only submission half** of
  Phase 7's module and scoped authentication. Live sync, retries, diagnostics,
  Council shared-field proposals and every write-back remain unstarted, and no
  Phase 7 gate criterion is claimed. Introduces one HTTP route ahead of Phase 3
  that authenticates a bearer service credential rather than a browser session,
  so no cookie, CSRF, OAuth, session or template surface is created. The Council
  preview route is inert without a Phase 3 authentication composition and
  answers `503`.
- **Dependency and critical-path effect:** none claimed. Phase 2's gate still
  requires the supervised active-folder rehearsal and the Data Owner
  attestation, neither of which this package performs.
- **Estimate and capacity:** not re-baselined here; the Delivery Lead owns the
  forecast.
- **New risks:** a persisted artifact class at rest (Actor mechanics), and a
  credential held on Foundry clients. Both are assessed in the package plan §5
  and controlled by restricted storage with documented retention, and by a
  submit-only scope whose worst case is an unwanted **pending** artifact.
- **Testing:** exporter canonicalisation and contract tests under `node --test`;
  storage atomicity, containment and cleanup; HTTP authentication, limits,
  checksum, idempotency and concurrency; preview authorization; PostgreSQL
  constraint, concurrency and append-only evidence; and one cross-language
  contract test binding the exporter's real output to the real parser.
- **Migration:** `0004_snapshot_submission_provenance`, additive and reversible;
  upgrade/downgrade/upgrade rehearsed against the disposable database. No
  applied migration edited; no runtime grant changed.
- **Security and data authority:** unchanged. Submission is not import. Apply
  still requires a currently authorized Guild Council member and still re-checks
  every bound input at commit. No field changes owner and none moves from
  `legacy`.
- **Operational effect:** a new artifact root with its own permissions,
  retention and backup treatment; proxy body and timeout limits that must match
  the 64 MiB artifact ceiling; credential issue, rotation and revocation
  procedures. All in
  [`../operations/foundry-snapshot-submission.md`](../operations/foundry-snapshot-submission.md).
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** **both required and neither performed.**
- **Acceptance Authority decision:** pending.

## v1.5 clarification C-4 — Phase 2 I-03 independent-review remediation

Recorded 2026-08-04 by the working Technical Lead. **The Acceptance Authority
has not decided it, and no finding is closed on the implementer's authority.**
Full record:
[`../review/phase-2-i-03-remediation-submission.md`](../review/phase-2-i-03-remediation-submission.md);
re-review request:
[`../review/phase-2-i-03-remediation-review-request.md`](../review/phase-2-i-03-remediation-review-request.md).

- **Affected requirements:** §9.2 (web security — CORS, credential handling),
  §6.4 (restricted artifact storage), §12 Phase 2 and Phase 7 as amended by C-3.
  No requirement changes ownership, authority or scope.
- **Reason:** the two independent reviews of the I-03 package returned three
  Blocking findings (B-1, S-B-1, S-B-2) and three others (I-1, I-2, S-I-1).
  `../review/phase-2-i-03-codex-review.md` and
  `../review/phase-2-i-03-codex-security-review.md`.
- **Added scope:** `adapters/http/cors.py`; a per-submission credential prompt in
  the Foundry module dialog; enforced artifact-storage preconditions with a
  startup check; a truthful durability contract. One new configuration variable,
  `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS`.
- **Removed scope:** the `submissionCredential` Foundry world setting. Foundry
  14.365 delivers every world-scoped setting value to every connecting client
  (`dist/packages/world.mjs`, an unfiltered `Setting.dump()`), and offers no
  setting option that is a read boundary, so no setting can hold a secret.
- **Alternatives considered and rejected:** a short-lived token exchange (a
  second HTTP route, reserved to Peter under ADR 0009 — carried forward as
  decision D-a); `scope: "client"` browser storage (leaves a reusable bearer at
  rest in a browser profile for no benefit over a password manager).
- **Phase-boundary effect:** none. No new route, no new capability, no new
  caller, no Phase 3 surface. ADR 0009 carries a dated clarification that a CORS
  preflight is the same route's contract rather than a second route.
- **Dependency and critical-path effect:** none added. Phase 2 I-03 remains
  behind independent implementation re-review and a separate security re-review,
  and now also behind two maintainer-supervised checks (operations §8.1, §8.2).
- **Estimate/forecast and capacity effect:** none recorded; this is remediation
  inside an already-planned package.
- **New or changed risks:** **R7 — the browser workflow is still unverified from
  a real browser.** Recorded in the RAID register and in the package plan
  amendment. Risks R1 and R2 of the package plan are strengthened rather than
  changed.
- **Testing effect:** module tests 78 (was 72); the six named narrow suites 220;
  full Python suite 1788, zero skips. No formatter, linter or type checker was
  run, because none is configured in this repository and none is installed.
- **Migration effect:** none. No schema change, no new migration, no edited
  migration; `alembic check` reports no new upgrade operations.
- **Security effect:** removes a reusable bearer from state readable by every
  client of the Foundry world; enforces restricted artifact storage against
  pre-existing paths; adds a bounded, allowlisted browser-origin policy with no
  cookie authority.
- **Operational effect:** one new required configuration variable for the
  browser workflow; **a deployment whose artifact root is permissive,
  wrongly-owned, symlinked or on a filesystem that cannot `fsync` a directory
  will now refuse to start**; credential rotation no longer touches Foundry; a
  documented read-only procedure for identifying database-unclaimed artifacts.
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** **both required and neither performed.**
- **Acceptance Authority decision:** pending. Decisions D-a (short-lived token
  exchange), D-b (whether this process may repair storage permissions) and D-c
  (retention for database-unclaimed artifacts) are reserved to Peter.
- **Superseded in part by C-5.** Two of the findings this entry described as
  remediated were reopened by the second independent re-review. Read C-5 with
  it; nothing in this entry closed a finding, and its I-1 and S-B-2 statements
  are no longer the current position.

## v1.5 clarification C-5 — Phase 2 I-03 second remediation (I-1, S-B-2)

Recorded 2026-08-04 by the working Technical Lead, after the second independent
implementation and security re-review of the I-03 remediation. **No finding is
closed, no gate is claimed, and the Acceptance Authority has not decided it.**
Full record: the same
[`../review/phase-2-i-03-remediation-submission.md`](../review/phase-2-i-03-remediation-submission.md)
and
[`../review/phase-2-i-03-remediation-review-request.md`](../review/phase-2-i-03-remediation-review-request.md),
both amended.

- **Affected requirements:** §6.4 (restricted artifact storage), §12 Phase 2
  operational evidence. No requirement changes ownership, authority or scope.
- **Reason:** the re-review found two of the six findings still open. **I-1**:
  the first remediation corrected the named messages and left the equivalent
  claims in the unresolved-concurrency and replay refusal paths and in every
  `ArtifactStorageError`, all of which can run after the artifact store has
  already published bytes. **S-B-2**: the enforced storage checks were made by
  pathname, so the validated root could be replaced between the check and each
  later create, open, publish or directory `fsync`.
- **Added scope:** a declared `StorageOutcome` on every storage failure, so what
  a refusal claims about the store is a decision rather than an inherited
  sentence; a root **directory descriptor** to which every filesystem operation
  is anchored, with an explicit lifecycle owned by the composition root; a
  startup check that no untrusted account can rename entries above the root; a
  repository-wide regression check on the prohibited claim.
- **Removed scope:** none.
- **Alternatives considered and rejected:** another pathname re-check before each
  use (moves the race window rather than removing it); repairing an unsafe root
  (D-b remains Peter's and is unchanged); relying on `__del__` alone for the
  descriptor's lifetime (explicit `close()` plus a context manager instead, with
  finalization as a backstop only).
- **Phase-boundary effect:** none. No new route, no new capability, no new
  caller, no Phase 3 surface, no schema change.
- **Dependency and critical-path effect:** none added. I-03 remains behind an
  independent implementation re-review (I-1, and preservation of I-2), a
  separate security re-review (S-B-2, and preservation of S-B-1/S-I-1) and the
  two maintainer-supervised checks (operations §8.1, §8.2).
- **Estimate/forecast and capacity effect:** none recorded; remediation inside
  an already-planned package.
- **New or changed risks:** R1 and R2 of the package plan are strengthened. The
  residual is now stated precisely: the anchoring is proven against pathname
  substitution and against type, owner and mode as this process observes them,
  **not** by a cross-account experiment, and no automated test creates a second
  POSIX account.
- **Testing effect:** module tests 81 (was 78); the six named narrow suites 232;
  full Python suite 1912, zero skips. Still no formatter, linter or type checker
  configured or installed, and none was added.
- **Migration effect:** none. No schema change, no new migration, no edited
  migration; `alembic check` reports no new upgrade operations.
- **Security effect:** a pathname replacement of the artifact root can no longer
  redirect a create, open, publication, read or directory `fsync`; the
  precondition that made such a replacement stageable is refused at startup; no
  failure message asserts a filesystem state it did not establish.
- **Operational effect:** **moving or replacing the artifact root now requires a
  service restart** — the running service refuses `root_replaced` rather than
  following the name. A deployment whose root has an ancestor writable by
  another account, without the sticky bit, **will refuse to start**
  (`root_ancestor_untrusted`). Both are documented in operations §5.6 and
  `.env.example`.
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** **both required and neither performed.**
- **Acceptance Authority decision:** pending. D-a, D-b and D-c are unchanged and
  remain reserved to Peter.
- **Superseded in part by C-6.** The third re-review found the S-B-2 remediation
  described here materially correct about *where* operations resolve, and found a
  separate defect in *how* the final entry was published. C-6 also reopens the
  I-1 statement above. Nothing in this entry closed a finding.

## v1.5 clarification C-6 — Phase 2 I-03 third remediation (publication, I-1, test evidence)

Recorded 2026-08-05 by the working Technical Lead, after the third independent
implementation and security re-review. **No finding is closed, no gate is
claimed, and the Acceptance Authority has not decided it.** Full record: the same
[`../review/phase-2-i-03-remediation-submission.md`](../review/phase-2-i-03-remediation-submission.md)
and
[`../review/phase-2-i-03-remediation-review-request.md`](../review/phase-2-i-03-remediation-review-request.md),
both amended again.

- **Affected requirements:** §6.4 (immutable, content-addressed, restricted
  artifact storage), §6.5 (atomicity), §12 Phase 2 operational evidence. No
  requirement changes ownership, authority or scope.
- **Reason:** three findings.
  1. **Blocking — publication could overwrite an unvalidated entry.** The
     anchoring accepted in C-5 fixed which directory the final entry was created
     in. Publication itself remained `os.replace`, which is atomic about
     *replacing*: a checksum-named entry appearing between the `_holds()` check
     and the rename was removed and overwritten without being examined,
     contradicting immutability, refusal-not-repair, evidence preservation and
     "no artifact is implicitly deleted".
  2. **Important — `StorageOutcome.UNRESOLVED` made an unproven claim.** The
     conservative *default* asserted that nothing already held had been changed
     or removed, which finding 1 made false.
  3. **Important — the storage tests were not reproducible.** On the review host,
     `/` and `/tmp` are owned by uid 65534, and the startup ancestor rule refused
     32 tests before they reached their own assertions. The submitted count of
     1912 could not be independently reproduced.
- **Added scope:** publication by `os.link`, which creates the checksum entry or
  fails `EEXIST` and never removes what is already there; full revalidation of a
  concurrent winner through the anchored descriptor; a third `StorageOutcome`
  (`PRESERVED`) distinguishing "an entry was refused and left as found" from
  "there was nothing there"; a startup probe proving the filesystem supports
  hard links *and* refuses a link over an existing name (`link_unsupported`);
  `TrustedAncestors` as an injectable policy object so automated evidence is
  hermetic; a structural guard making cleanup unable to name anything but a
  temporary.
- **Removed scope:** none. No route, no capability, no retention decision.
- **Alternatives considered and rejected:** a pathname existence check followed
  by `os.replace` (the same race in a different shape, and explicitly refused by
  the review); `renameat2(RENAME_NOREPLACE)` (equivalent guarantee in one
  syscall, but the standard library exposes no wrapper and a hand-rolled `ctypes`
  syscall stub in the path holding every exported Actor's mechanics is a worse
  trade than one extra `unlink` — recorded in operations §5.6 and the adapter
  docstring); relaxing the production ancestor-ownership rule to make the tests
  pass (treated as a security-policy change reserved to Peter, and **not made**);
  broadly monkeypatching `os.stat`/`os.lstat` in the suite (would have stopped
  the root and target checks testing real behaviour).
- **Phase-boundary effect:** none. No new route, no new capability, no new
  caller, no Phase 3 surface, no schema change.
- **Dependency and critical-path effect:** none added. I-03 remains behind an
  independent implementation re-review, a separate security re-review and the two
  maintainer-supervised checks (operations §8.1, §8.2).
- **Estimate/forecast and capacity effect:** none recorded.
- **New or changed risks:** R-15 restated; new **R-16** (the artifact root's
  filesystem must support hard links) and **R-17** (the ancestor rule is a
  statement about the host and is a genuine deployment prerequisite that no test
  seam removes). See the RAID register.
- **Testing effect:** module tests 81, unchanged; the named narrow suites 372;
  full Python suite **1941**, zero skips. The suite was additionally run under a
  throwaway harness reporting `/` and `/tmp` as owned by uid 65534 — the review
  host's condition — and passed there too, which is the evidence finding 3 asked
  for. Still no formatter, linter or type checker configured or installed, and
  none was added.
- **Migration effect:** none. No schema change, no new migration, no edited
  migration; `alembic check` reports no new upgrade operations.
- **Security effect:** an entry under a checksum name that this service did not
  write and has not validated can no longer be destroyed by a submission. A
  concurrent writer of identical bytes converges rather than overwriting. No
  failure message, including the conservative default, asserts a filesystem state
  it did not establish.
- **Operational effect:** **the artifact root must be on a filesystem supporting
  hard links** (ext4, XFS, Btrfs, ZFS, tmpfs; not FAT/exFAT or some network
  mounts). The service proves this at startup and refuses `link_unsupported`
  otherwise. A new recovery procedure covers an unexpected entry found under a
  checksum name — preserve it, do not delete it. Both are documented in
  operations §5.6, §9 and `.env.example`.
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** **both required and neither performed.**
- **Acceptance Authority decision:** pending. D-a, D-b and D-c are unchanged and
  remain reserved to Peter.

## v1.5 clarification C-7 — Phase 2 I-03 fourth remediation (evidence accuracy, I-3R-1)

Recorded 2026-08-05 by the working Technical Lead, after the third independent
implementation and security re-review returned its reports. At submission no
finding was closed and no gate was claimed. **The later independent re-review
and Acceptance Authority decision closing I-3R-1 are recorded below; no I-03 or
Phase 2 gate decision is implied.**
Full record:
[`../review/phase-2-i-03-fourth-remediation-submission.md`](../review/phase-2-i-03-fourth-remediation-submission.md),
with the re-review request at
[`../review/Handover information`](../review/Handover%20information).

- **Affected requirements:** §6.4 (immutable, content-addressed, restricted
  artifact storage) and §13.3 (review-gate evidence). No requirement changes
  ownership, authority or scope, and no acceptance criterion is reinterpreted.
- **Reason:** one Important **evidence-accuracy** finding, I-3R-1. The third
  re-review accepted the publication mechanism, I-1, I-2, root anchoring, S-B-1
  and S-I-1, and found that the third-remediation review request claimed "no
  temporary survives success or an ordinary failure" on the grounds that
  `_discard` runs on every path. Running `_discard` is not removal: it swallows
  `OSError` by design, and
  `test_a_failing_cleanup_leaves_the_published_artifact_alone` had already
  proved that a *successful* store can leave one private `.incoming-*` hard
  link. The implementation, the operations document and the test were right;
  the review evidence was not, and a false structural-guarantee table could
  have misled a storage-capacity or hygiene assessment.
- **What is superseded:** the temporary-cleanup row of the third-remediation
  structural-guarantee table, marked as superseded in place rather than
  rewritten. **C-6 is not otherwise superseded** — it did not repeat the claim,
  and the publication mechanism it records is unchanged and was not reopened.
- **Added scope:** none in the service. The corrected contract is stated
  consistently across the adapter docstring, the operations document,
  `.env.example`, the review record and the controlled records; operations §5.6
  gains "Temporary files left by a failed cleanup", a read-only, age-bounded,
  link-count-aware detection procedure; three tests in
  `tests/test_artifact_store.py` prove that procedure's rule against synthetic
  files.
- **Removed scope:** none.
- **Alternatives considered and rejected:** making the old sentence true by
  changing publication — rejected outright. The `os.link` design and the
  test-only bounded ancestor walk were both accepted by the third re-review and
  were not reopened, and no contradictory evidence was found. Making cleanup
  failure fail the submission — rejected: it would turn a correctly published
  artifact into a refusal over an `unlink`, which is the failure direction I-2
  exists to prevent. Adding a listing or deletion capability to the service so
  it could clean up after itself — rejected: it would broaden the service's
  filesystem authority beyond "create a temporary, and unlink one created in
  the attempt that is running", which is the property that makes a cleanup
  failure structurally unable to delete an artifact.
- **Dependency and critical-path effect:** none. The independent re-review was
  completed on 2026-08-05; the remaining critical path is the supervised and
  owner-controlled evidence followed by the Acceptance Authority's gate
  decision.
- **Estimate/forecast and capacity effect:** none.
- **New or changed risks:** **R-18 added** — leftover temporaries accumulate
  unnoticed and consume storage (Low/Low, Operations Owner). **R-9 in the
  package plan sharpened**: "a failed cleanup cannot delete a published
  artifact" was true and incomplete; what it can do is leave storage behind
  that nobody is told about. **D-11 added** to the package plan: detection is an
  operator procedure, deliberately not an application capability.
- **Testing effect:** three new tests (94 in `tests/test_artifact_store.py`, was
  91), all synthetic and read-only, exercising the documented `find` rule
  through the real `find`. No test was deleted or weakened, and the existing
  cleanup-failure test is preserved unchanged.
- **Migration effect:** none. No schema, no migration, no data.
- **Security effect:** none claimed. No security-relevant code or contract
  changed — publication, anchoring, the credential boundary and the CORS policy
  are untouched — so no new security re-review is requested. The security
  reviewer's own third report had already described the best-effort cleanup
  correctly.
- **Operational effect:** operators gain a documented way to find leftover
  temporaries and a rule for reading the link count before removing one; whoever
  sizes the artifact filesystem is told that leftovers are possible after a
  successful store. **How often the procedure should be run has not been
  decided**, and nothing automates it.
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** the narrow independent implementation
  re-review was completed by Codex on 2026-08-05 and returned no Blocking,
  Important or Optional finding; it confirms I-3R-1 is resolved and the final
  traceability claims are truthful. Recorded in
  `docs/review/phase-2-i-03-fourth-remediation-codex-re-review.md`. No further
  security re-review was required, for the reason above.
- **Acceptance Authority decision:** Peter Duscha accepted the independent
  recommendation and closed I-3R-1 on 2026-08-05. This closes that finding only;
  it does not accept I-03 or close the Phase 2 gate. D-a, D-b and D-c are
  unchanged and remain reserved to Peter, and the retention question D-c also
  covers how often leftover-temporary hygiene should run.

## v1.5 clarification C-8 — database-unclaimed artifact retention D-c

Recorded and accepted by Peter Duscha on 2026-08-05.

- **Affected requirements:** Phase 2 rollback/recovery and snapshot-retention
  acceptance criterion; I-03 restricted artifact operations.
- **Reason:** database-unclaimed raw snapshots can be necessary for retry or
  incident investigation but contain sensitive Actor mechanics and must not be
  retained indefinitely.
- **Added/removed scope:** none. This decides the lifetime of an existing
  artifact class; it adds no route, mutation or automatic deletion.
- **Decision:** retain a database-unclaimed raw snapshot for at most 30 days and
  delete it sooner when its rehearsal, retry or incident closes. Preserve its
  checksum, provenance and sanitized audit record permanently. Investigate and
  report before deletion; the maximum does not authorize erasing evidence for
  an open incident.
- **Dependency and critical-path effect:** closes retention decision D-c. Other
  Phase 2 supervised evidence, performance thresholds, owner recommendations
  and the gate decision remain pending.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** narrows indefinite sensitive-artifact retention without
  weakening incident evidence handling.
- **Testing and migration effect:** none; policy/documentation only, no schema
  or executable-code change.
- **Security and operational effect:** bounds raw Actor-payload retention;
  operations §5.6 carries the investigation and deletion procedure.
- **Product/Data/Operations Owner recommendation:** accepted by Peter Duscha in
  those roles for this decision only.
- **Technical and independent review:** no implementation was introduced by the
  decision. The complete Phase 2 package still requires its final independent
  gate recommendation.
- **Acceptance Authority decision:** **accepted by Peter Duscha on 2026-08-05.**
  This accepts D-c only and does not accept I-03 or close Phase 2.

## v1.5 clarification C-9 — Phase 2 R4 observation and runtime thresholds

Recorded and accepted by Peter Duscha on 2026-08-05.

- **Affected requirements:** Phase 2 remediation plan §9.4 items 3 and 4.
- **Reason:** package R4 requires numeric observation and 500-Actor performance
  thresholds rather than subjective terms.
- **Decision:** use a zero-hour observation period with immediate post-run
  verification, endpoint shutdown and disposable-state cleanup. Accept 5
  seconds for preview and 5 seconds for fresh apply as Phase 2 rehearsal
  thresholds on this named host.
- **Evidence:** `docs/review/phase-2-r4-500-actor-benchmark.md`; Codex also ran
  the exact benchmark from a verified-empty `freedom_test` database and
  reproduced the 793.866 ms preview maximum, 1,313.291 ms fresh-apply maximum,
  5-second recommendations and clean return to Alembic `0004`.
- **Added/removed scope:** none. These are gate/rehearsal acceptance thresholds,
  not production capacity promises, application timeouts or new monitoring.
- **Dependency and critical-path effect:** closes §9.4 items 3 and 4. Items 1
  and 2—the bounded maintainer/gate availability and real-export rehearsal
  window—remain open and continue to block R4 readiness.
- **Estimate/forecast and capacity effect:** no calendar forecast is created.
- **Risk effect:** gives the rehearsal an objective performance refusal point;
  host-specific synthetic evidence does not predict production capacity.
- **Testing and migration effect:** 500-Actor harness and regression evidence;
  no schema or migration change. Full suite reported 1,954 passed with one
  dependency warning.
- **Security and operational effect:** benchmark used synthetic data and the
  local Unix-socket `freedom_test` database. Immediate cleanup retains no
  rehearsal service or raw state for continuing observation.
- **Product/Data/Operations Owner recommendation:** accepted by Peter Duscha in
  those roles for this decision only.
- **Technical and independent review:** Gemini produced the benchmark; Codex
  reviewed its safety corrections and independently reproduced the threshold
  inputs.
- **Acceptance Authority decision:** **accepted by Peter Duscha on 2026-08-05.**
  This closes only §9.4 items 3 and 4 and does not accept I-03 or Phase 2.

## v1.5 correction C-10 — canonical key order in the Foundry export contract

Recorded 2026-08-09. Ruled by Peter Duscha the same day, on finding RA-2 from
Rehearsal A.

> **Partly superseded by [C-12](#v15-correction-c-12--the-canonical-key-boundary-is-232--2-corrects-c-10),
> 2026-08-10.** The direction below — ECMAScript own-property order rather than
> plain code-point order — stands, and closing RA-2 stands. **The boundary
> stated below is wrong**: `[0, 2**53-1]` is the *integer index*, and ordinary
> object enumeration hoists only *array indices*, which end at `2**32 - 2`. The
> "Decision" and "Testing effect" bullets below should be read as corrected by
> C-12. This entry is left otherwise intact as the record of what was ruled on
> 2026-08-09.

- **Affected requirements:** `docs/rules/foundry-export-contract.md` §1
  ("Object keys"), new §1.0; `application/foundry/parser.py:canonical_bytes`;
  the `non_canonical_encoding` warning text in
  `application/foundry/reconciliation.py`.
- **Reason:** the contract required object keys "sorted by Unicode code point,
  at every depth", and **no conforming exporter could satisfy it**. dnd5e keys
  scale-value advancements by class level, so real Actors carry `{"1":…,"4":…,
  "10":…}`; ECMAScript places integer-index keys first in ascending numeric
  order, so a browser exporter emits `"1","4","10"` however it sorts. Verified
  against the shipped module rather than assumed: `canonical.js` sorts the key
  array to `["1","10","4"]` correctly, then rebuilds an object and the engine
  reorders it on insertion. `canonical_encoding` was therefore false for every
  real world and true only for synthetic fixtures — a flag structurally unable
  to carry information.
- **Decision:** adopt ECMAScript own-property order as the contract's canonical
  order — integer-index keys (canonical decimal integers in `[0, 2**53-1]`)
  first in ascending numeric order, then all other keys by Unicode code point.
- **Alternatives considered:** require such maps to be emitted as JSON arrays,
  which changes the wire shape and every consumer of it; or drop the
  canonical-encoding claim entirely, which discards a genuine
  cross-exporter comparability property. Both were rejected as larger than the
  defect.
- **Added/removed scope:** none. No field, aggregate, route or migration is
  affected, and nothing became writable or comparable that was not before.
- **Dependency and critical-path effect:** closes RA-2. **The Foundry module is
  unchanged and requires no version bump** — the exporter always conformed to
  the new rule; the contract had described something else. Module `1.0.5`
  remains the installed, rehearsed build of record.
- **Estimate/forecast and capacity effect:** none; no calendar forecast exists.
- **Risk effect:** removes a permanently-false report that would have trained
  operators to ignore a warning. The second half of the rule — string keys by
  code point — is this contract's own, not ECMAScript's, because the language
  would use insertion order there and a canonical form may not depend on that.
- **Testing effect:** four new parser tests pin numeric-before-string ordering,
  the array-index definition (`"01"`, `"-1"`, `"1.0"` are string keys), and
  recursion through nested lists and objects. Full suite 1,781 passed, 208
  skipped (database-dependent, no `TEST_DATABASE_URL` in this session).
- **Migration effect:** none. Artifact identity is the SHA-256 of the original
  bytes and is untouched; the Manager still never re-serialises an artifact.
  Duplicate detection never depended on canonicalisation.
- **Security and operational effect:** none. The warning text was also
  corrected: it claimed "two exports of an unchanged world will not compare
  equal", which was false — an exporter's own output is deterministic.
- **Product/Data/Operations Owner recommendation:** accepted by Peter Duscha in
  those roles for this decision.
- **Technical Lead and specialist reviews:** implemented by Claude, who also
  raised RA-2. **It carries no independent review**; it is part of the set going
  to the Independent Reviewer with the Phase 2 gate evidence.
- **Acceptance Authority decision:** **ruled by Peter Duscha on 2026-08-09.**
  This closes RA-2 and accepts no implementation beyond it; it does not close
  the Phase 2 gate.

## v1.5 correction C-11 — performance threshold restated per megabyte (amends C-9)

Recorded 2026-08-09. Ruled by Peter Duscha the same day, on finding RA-5 from
Rehearsal B.

- **Affected requirements:** change-log **C-9** (Phase 2 remediation plan §9.4
  items 3 and 4); `tests/benchmark_snapshot_500.py`;
  `docs/review/phase-2-r4-500-actor-benchmark.md` as the evidence C-9 rests on.
- **Reason:** C-9 accepted "5 seconds for preview and 5 seconds for fresh apply"
  measured in wall-clock seconds against an **Actor count**, using synthetic
  Actors of 2,182 bytes. Rehearsal B previewed real Actors of 508,975 bytes —
  **233× larger** — and took 9.566 s, breaching the threshold while producing 0
  errors, 0 warnings and a complete reconciliation. Throughput was **587 ms/MB
  against the benchmark's 728 ms/MB**: the real run is *faster* per megabyte. A
  count-based threshold measures the corpus, not the code. Discovery finding
  F-F5 had already recorded that "an actor is 1.1–3.3 MB of JSON" before the
  benchmark was written, so the corpus was known to be unrepresentative.
- **Decision:** three parts.
  1. The Phase 2 gate criterion is **throughput: ≤ 1,200 ms per megabyte**,
     measured from the slowest sample. Observed 587 (real) and 728 (synthetic).
  2. C-9's 5-second figures are **retained as synthetic smoke-test context and
     are no longer gate criteria.** They are not deleted: they remain the record
     of what was measured on that corpus.
  3. The absolute 9.566 s is recorded as a **Phase 3 architecture input**, not a
     Phase 2 pass/fail — see below.
- **Alternatives considered:** re-baselining the wall-clock number against a
  real-sized corpus, which keeps a figure that must be re-derived whenever the
  folder grows; and dropping the threshold, which was explicitly rejected — it
  is the only control that would catch an N+1 query or a quadratic parse.
- **Added/removed scope:** none.
- **Dependency and critical-path effect:** closes RA-5. Removes a breach that
  would otherwise have had to be argued or waived at the gate.
- **Estimate/forecast and capacity effect:** none. This is still not a
  production capacity promise, exactly as C-9 said of itself.
- **Risk effect:** replaces a criterion that could pass a bad implementation on
  a small corpus, and fail a good one on a real corpus, with one that does
  neither. **Phase 3 consequence:** at 9.566 s for 32 Actors and growing, the
  Council preview cannot be a synchronous HTTP handler; it needs a background
  job or progressive response. That constraint is now recorded in the plan's
  Phase 3 section rather than waiting to be rediscovered during implementation.
- **Testing effect:** `THROUGHPUT_LIMIT_MS_PER_MB` and a `throughput_gate`
  block are in the benchmark harness, reported whether or not they pass. Three
  new tests pin the unit, the breach reporting, and that the gate measures the
  slowest sample rather than the median — a median would let one pathological
  run hide behind six good ones. Suite: 1,784 passed, 208 skipped.
- **Migration effect:** none.
- **Security and operational effect:** none.
- **Product/Data/Operations Owner recommendation:** accepted by Peter Duscha in
  those roles for this decision.
- **Technical Lead and specialist reviews:** proposed and implemented by Claude,
  who also raised RA-5. **No independent review**; it goes to the Independent
  Reviewer with the Phase 2 gate evidence.
- **Acceptance Authority decision:** **ruled by Peter Duscha on 2026-08-09.**
  Closes RA-5. Closes no gate.

## v1.5 correction C-12 — the canonical key boundary is `2**32 - 2` (corrects C-10)

Recorded 2026-08-10 on **finding I-1** of the independent Phase 2 gate review
(`docs/review/Handover information`). **Proposed; not yet ruled.**

- **Affected requirements:** `docs/rules/foundry-export-contract.md` §1 and
  §1.0; `application/foundry/parser.py` (`_MAX_ARRAY_INDEX`,
  `_canonical_key_order`, `canonical_bytes`); change-log **C-10**, which this
  entry corrects.
- **Reason:** C-10 adopted ECMAScript own-property order but wrote the boundary
  as "integer index … `[0, 2**53 - 1]`". `OrdinaryOwnPropertyKeys` hoists
  **array indices** — `ToString(ToUint32(P))` is `P`, and `ToUint32(P) ≠
  2**32 - 1` — which end at `4294967294`. An *integer index* is a
  `String.prototype`/typed-array concept ordinary object enumeration never
  consults. This was an **observed cross-language disagreement**, not a wording
  slip: for `{"5000000000":…,"10000000000":…}` the shipped exporter emitted
  `{"10000000000":…,"5000000000":…}` (both are ordinary string keys to it, so
  code point decides) while the Python verifier sorted them numerically and
  emitted the other order. Every artifact carrying a canonical decimal key of
  ten or more digits would have been reported non-canonical against a
  conforming exporter. The committed fixture could not see it: its
  integer-looking keys are dnd5e class levels, which are array indices under
  either rule.
- **Decision:** the canonical order is array-index keys — canonical decimals in
  `[0, 2**32 - 2]` — first in ascending numeric order, then every other key by
  Unicode code point. The second half remains this contract's own, as C-10 said.
- **Alternatives considered:** changing the exporter to sort all numeric-looking
  keys numerically, which is impossible — the engine's hoisting is not
  something a script can opt out of for an ordinary object; and emitting such
  maps as arrays, rejected by C-10 already as larger than the defect.
- **Added/removed scope:** none.
- **Dependency and critical-path effect:** **the Foundry module is unchanged,
  byte for byte, and keeps version `1.0.5`.** The exporter always implemented
  the corrected rule — `canonical.js` sorts the key array by code point, rebuilds
  an object, and the engine hoists exactly the array indices — so only the
  verifier and the contract described something else. `1.0.5` remains the
  installed, rehearsed build of record, and the rehearsals' evidence is
  unaffected. `canonical.js`'s header comment still describes the *sort* rather
  than the emitted order; it is deliberately not edited, because editing an
  installed and rehearsed build's bytes under the same version is what the
  version identity control (CL3-I-2) exists to prevent. Carried to the next
  version bump.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes a false `canonical_encoding = false` for conforming
  real exports — the same class of permanently-wrong report C-10 removed, one
  boundary further out. **Rehearsal B's recorded `canonical_encoding = yes` is
  not disproved**: the real artifact evidently held no key at this boundary. It
  is the claim that C-10 was correct and complete that is corrected here.
- **Testing effect:** a new `foundry-module/tests/emit-canonical.mjs` runs
  caller-chosen documents through the shipped `canonicalBytes`, which is what
  makes the boundary reachable from a cross-language test at all. Eight boundary
  documents are asserted three ways in `tests/test_exporter_contract.py` — the
  exporter's bytes, the verifier's bytes, and that they are equal — covering
  `"0"`, `"4294967294"`, `"4294967295"`, `"5000000000"`/`"10000000000"`, the old
  bound's own values, the noncanonical forms `"01"`, `"-1"`, `"1.0"`, `" 1"`,
  `"+1"`, `"1e2"`, and recursion through nested objects and arrays. Mirrored in
  `foundry-module/tests/canonical.test.mjs` and pinned for the verifier alone in
  `tests/test_snapshot_parser.py`.
- **Migration effect:** none. Artifact identity is still the SHA-256 of the
  original bytes; no stored row changes.
- **Security and operational effect:** none.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex as independent
  review finding I-1; implemented by Claude. Returns to the Independent Reviewer
  with the corrected package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.

## v1.5 correction C-13 — lost-pin recovery requires settlement, not a timeout

Recorded 2026-08-10 on **finding B-1** of the independent Phase 2 gate review.
**Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  and §6 step 10; `docs/review/phase-2-i-03-cl3-remediation.md` and
  `docs/review/phase-2-supervised-rehearsal-2026-08-09.md`, both of which
  recorded CL3-B-1 as closed.
- **Reason:** the procedure told the operator to wait until the final
  "request/timeout has finished", query, repeat once, and then authorize a fresh
  export on a miss. **A client timeout establishes only that the browser stopped
  waiting.** The reload does not cancel the POST — `wsgiref.simple_server` runs
  a handler to completion whether or not anyone is listening — so both queries
  can run before the server transaction commits, both miss, a fresh export is
  authorized, and the original commits afterwards. The fresh export carries its
  own checksum, so the uniqueness constraint cannot merge them: one real
  submission becomes two pending artifacts. The whole-episode window correction
  (CL3-B-1) fixed a different false miss and left this one.
- **Decision:** a miss may not be recorded until **settlement** is positively
  established and recorded — either **S-A**, the process that served the episode
  has exited (an exited process commits nothing), or **S-B**, that same process
  has answered a later probe, which on a single-threaded server proves every
  earlier handler already returned. Both are corroborated by `pg_stat_activity`
  showing no transaction in flight. A fourth outcome, **Unsettled**, is added
  beside hit/miss/ambiguous and is an incident, not a miss. The repeat-once rule
  survives for operator error but is explicitly no longer what makes a miss safe.
- **Alternatives considered:** a settlement *deadline* derived from the proxy's
  `read_timeout`/`write_timeout`, rejected because those bound Caddy's patience
  and not the upstream handler — `wsgiref.simple_server` enforces no request
  deadline of its own, so the deadline would have been a guess wearing a
  number's clothes. Also considered and rejected: persisting the pin so recovery
  needs no server evidence, which the standing confidentiality constraint
  forbids (no Actor data or credential in browser-readable Foundry settings).
- **Added/removed scope:** none. No code path, route, schema or credential
  changes; the endpoint behaves exactly as before.
- **Dependency and critical-path effect:** reopens and then re-closes CL3-B-1.
  **S-B is a property of `wsgiref.simple_server` and does not survive Phase 3's
  concurrent `freedom-web` process**; replacing it is recorded as a Phase 3
  obligation in §9. S-A holds under any server.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes the last reachable path from one real submission to
  two pending artifacts. Costs a delay when settlement cannot be established,
  which is the intended direction to fail in.
- **Testing effect:** `tests/test_snapshot_recovery_settlement.py` reproduces
  the late-commit sequence deterministically against the real submission service
  (a gated `commit`, two misses while the transaction is open, the commit
  landing afterwards), and exercises the settlement probe against a real
  `wsgiref.simple_server` over the real WSGI application. That second test was
  checked against a threaded server as a negative control and **fails** there
  with the message the Phase 3 obligation predicts, so it is not vacuous.
  `tests/test_snapshot_recovery_documentation.py` gains four tests pinning the
  settlement step, the unsettled outcome and the Phase 3 note.
- **Migration effect:** none.
- **Security and operational effect:** operational only, and it is the point.
  The probe is unauthenticated by design so that it is refused `401` before a
  principal exists, writing no audit event, no snapshot row and no artifact —
  recovery must not write. §6 step 10 also now states that the injector must
  fault the POST rather than the CORS preflight (finding RA-4), and that step 10
  does **not** exercise the late-commit case.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex as independent
  review finding B-1; implemented by Claude. Returns to the Independent Reviewer
  with the corrected package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.
- **Superseded in part by C-14.** The re-review of this entry found S-B as
  written still inferring accept order from issuance order. S-B is now two
  conditions, S-B.1 and S-B.2; read C-14 with this entry. Nothing else here
  changes, and S-A is untouched.

## v1.5 correction C-14 — S-B needs proof the delivery path has drained

Recorded 2026-08-10 on the **re-review of C-13**, which held finding B-1 open.
**Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1 (S-B) and §5.4 (proxy configuration).
- **Reason:** C-13's S-B argued that because the settlement probe is *issued*
  after the episode's last attempt, a single-threaded server must *accept* it
  after that attempt. That does not follow. `wsgiref.simple_server` guarantees
  serial handling in **accept** order, and the submission reaches it through
  Caddy while the probe is sent straight to loopback. A submission Caddy is
  still holding has not reached the endpoint at all, so the endpoint can answer
  the later probe first, the query can then miss, and the submission can be
  accepted and commit afterwards — the same false miss C-13 set out to remove,
  reached by a different route. `pg_stat_activity` cannot cover it either: a
  request that has not reached the application has no backend to observe.
- **Decision:** S-B becomes two conditions, and the second is worthless without
  the first. **S-B.1** requires positive, recorded evidence that nothing can
  still be delivered: the client is gone and the submitting GM confirms no
  attempt since the episode's last; Caddy's `caddy_http_requests_in_flight`
  gauge reads zero for every series of the server fronting this endpoint; and
  the endpoint's current connections are recorded, each of them necessarily
  established before the probe's. The gauge is labelled by server and handler
  and not by route, so a host busy with unrelated traffic cannot satisfy it —
  §9 states that as an honest "cannot establish" rather than working around it. **S-B.2**
  is the probe, unchanged. The settlement argument is restated as an explicit
  chain whose only claim about issuance order is the one S-B.1 observes. An
  unreadable or non-zero in-flight counter is an **unsettled** episode, and §9
  now states the maintainer-authorized way out of one: stopping the endpoint
  process converts it into S-A.
- **Alternatives considered:** a settlement deadline (rejected in C-13, and the
  reasoning is unchanged). Replacing S-B outright with an application-level
  in-flight or quiescence mechanism was considered and **deferred, not
  rejected**: it is the better answer and it is already the recorded Phase 3
  obligation, but it is a code change to the submission path during a gate
  re-review, and S-B.1 is obtainable today from configuration and read-only
  observation. §9 records that such a mechanism would retire S-B.1 as well.
- **Added/removed scope:** §5.4 now requires Caddy's per-server metrics to be
  enabled, so the counter S-B.1 reads exists. No code path, route, schema or
  credential changes; the endpoint behaves exactly as before.
- **Dependency and critical-path effect:** none beyond C-13's. S-B.1 depends on
  Caddy being the only path to the endpoint and on it reporting what it holds;
  §9 records both, and records that another hop in front of the endpoint
  reopens the same gap.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** closes the remaining path from one real submission to two
  pending artifacts. Costs a delay whenever drain cannot be evidenced, which is
  the intended direction to fail in.
- **Testing effect:** `tests/test_snapshot_recovery_settlement.py` gains two
  tests. One reproduces the false miss S-B.1 exists to prevent — the probe's
  connection accepted and answered, and both queries run, before the
  submission's connection is made at all. The other establishes what S-B.1
  buys: with the submission connected and sent but **not yet accepted, read or
  handled**, the probe still cannot be answered first. That second test is the
  case the C-13 test did not reach, because it waited until the submission was
  already inside its commit. Both were checked against a threaded server as a
  negative control; the ordering test fails there with the message the Phase 3
  obligation predicts, and the false-miss reproduction passes there as it
  should, since it does not depend on serial handling.
  `tests/test_snapshot_recovery_documentation.py` gains three tests pinning
  S-B.1, the §5.4 metrics requirement and the unsettled outcome's new trigger.
- **Migration effect:** none.
- **Security and operational effect:** operational. The added evidence is two
  read-only observations on loopback — Caddy's admin metrics and the socket
  table — and the probe is unchanged and still writes nothing. Caddy's admin
  API stays loopback-only.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex when re-reviewing
  C-13's remediation of B-1; implemented by Claude. **Carries no independent
  review** and returns to the Independent Reviewer with the package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.
- **Superseded by C-15.** The re-review of this entry found that
  `caddy_http_requests_in_flight` does not mean what S-B.1 needed it to mean.
  S-B.1 and S-B.2 are both **withdrawn**; read C-15 instead. S-A survives, in a
  corrected and stricter form.

## v1.5 correction C-15 — settlement is a stopped endpoint, not an observed drain

Recorded 2026-08-10 on the **re-review of C-14**, which held finding B-1 open for
the third time. **Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1, step 3, a new step 4, and §5.4 (proxy configuration); §6 step 10's
  settlement note.
- **Reason:** C-14's S-B.1 rested on Caddy's `caddy_http_requests_in_flight`
  reading zero as evidence that the proxy held nothing. Caddy documents that
  gauge more narrowly, as the requests **currently being handled**
  ([metrics](https://caddyserver.com/docs/metrics)). It does not cover a
  connection Caddy has accepted whose request has not entered the instrumented
  handler, nor body bytes still arriving over an established HTTP/1.1, HTTP/2 or
  HTTP/3 connection; closing or reloading the Foundry page does not establish
  that what the browser already transmitted has been consumed; and sampling the
  gauge and then the socket table is two observations rather than one atomic
  drain. So the false miss survived C-14: the submission has been sent but has
  not entered the handler, the gauge reads zero, the query misses twice, and the
  request is then handled and commits. C-13's S-A had a smaller version of the
  same hole — it accepted "a process that started after the episode", and the
  proxy can hand the episode's stranded request to a replacement process as
  readily as to the original.
- **Decision:** settlement stops being an observation of what is in flight and
  becomes a **state**: the endpoint is not running, and does not run again until
  the outcome has been recorded. The probe (S-B.2) and the gauge (S-B.1) are
  **withdrawn**, and a settlement recorded from either is not a settlement. S-A
  is now four recorded parts: the process that served the episode is gone
  (`ps`/`ss`, by start time); **nothing is listening on the port**, a replacement
  process being explicitly insufficient; the path through Caddy is confirmed dead
  by a `502`/`503` from Caddy itself; and the endpoint stays down through the
  query and the recording. `pg_stat_activity` corroboration is unchanged. The
  argument is that every commit on this path begins with an accept, and an
  unserved port accepts nothing — wherever the request happens to be. A new
  **step 4** then covers the residual after the restart: following a fresh
  submission, the step-2 query is re-run over the widened window, and a second
  acceptance event whose checksum is not the fresh submission's is an
  **ambiguous** outcome and a defect in this procedure, resolved by superseding
  one artifact through the documented correction flow rather than by the Council
  reviewing both.
- **Alternatives considered:** an *actual* proxy drain — stopping Caddy or
  removing the route — which stops new intake but takes down every other service
  on the host to reconcile one snapshot, where stopping the endpoint alone is
  both narrower and strictly stronger. An **application-level in-flight or
  quiescence mechanism**, the reviewer's preferred answer, remains
  **deferred, not rejected**: it is what §9 now records as the Phase 3
  improvement, and it is the only way to settle an episode without a stop. A
  settlement deadline stays rejected for C-13's reasons. Persisting the pin stays
  rejected under the confidentiality constraint.
- **Added/removed scope:** §5.4 no longer requires Caddy's per-server metrics —
  nothing in the document reads them now — and instead requires that **no
  upstream retry window** stand in front of the endpoint (`lb_try_duration` unset,
  no second proxy or queue), because a hop that holds a refused request would let
  a stranded submission arrive after the endpoint returns. Where metrics are kept
  for monitoring, §5.4 now shows the current global `{ metrics }` form; the nested
  `servers { metrics }` form still adapts on the installed Caddy 2.10.2 but
  `caddy adapt` warns it is removed in the next major version. Step 4 is added
  scope for the operator. No code path, route, schema or credential changes.
- **Dependency and critical-path effect:** S-A no longer depends on the
  endpoint's concurrency model, so it holds unchanged for Phase 3's `freedom-web`;
  what was a Phase 3 *obligation to repair* becomes a Phase 3 *improvement*,
  namely settling without taking the service down. It does depend on Caddy being
  the single path and on that path failing a refused request, which §5.4 records.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes the reachable false miss that survived C-13 and C-14,
  at the cost of a deliberate endpoint stop during recovery — acceptable for a
  hand-started rehearsal process, and the reason the Phase 3 improvement is
  recorded. Step 4 makes the remaining residual detectable rather than assumed
  away.
- **Testing effect:** `tests/test_snapshot_recovery_settlement.py` replaces the
  two probe-ordering tests with the two that establish S-A against a real
  `wsgiref.simple_server` over the real WSGI application: a submission
  **connected, fully sent and waiting unaccepted** at the endpoint commits
  nothing when the endpoint stops without serving it, and a delivery attempted
  after the stop is refused at the socket while what committed before the stop
  stays visible to the query. The first was checked against a negative control
  that serves the queue instead of stopping — it fails there, so it discriminates
  the stop. The late-commit reproduction and the withdrawn probe's false miss are
  both retained. `tests/test_snapshot_recovery_documentation.py` pins the single
  condition and its four parts, the named defects of both withdrawn conditions,
  §5.4's retry-window requirement and non-deprecated metrics form, the unsettled
  triggers, and step 4.
- **Migration effect:** none.
- **Security and operational effect:** operational. Recovery still writes
  nothing: the two remaining observations are read-only, and the confirming
  request through Caddy cannot reach the application because the endpoint is
  down. Stopping the endpoint is maintainer-authorized because it deliberately
  aborts in-flight work — a rollback, not a loss.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex when re-reviewing
  C-14's remediation of B-1; implemented by Claude. **Carries no independent
  review.** B-1 is **not** recorded as closed: the reviewer holds it open, and
  closing it is the reviewer's to do.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.
- **Superseded in part by C-18.** The re-review of this entry found the stop
  correct and its **scope** wrong: it covers the endpoint and not the path in
  front of it, so a request the proxy holds and has not yet dialled upstream for
  survives the down window and commits after the restart. S-A.1 and S-A.2 survive;
  **S-A.3 is withdrawn and inverted** — a `502` from Caddy now means Caddy is
  running — and S-A.4 becomes S-D. Read C-18 instead.

## v1.5 correction C-16 — an NFC key collision is a refusal, and both halves normalise keys

Recorded 2026-08-10, on the open defect
`docs/review/phase-2-canonical-nfc-key-collision.md` (found while remediating
finding I-1) and on the maintainer instruction to fix both implementations
together, add the refusal code and bump the exporter version before Phase 2
closes. **Proposed; not yet ruled.**

- **Affected requirements:** `docs/rules/foundry-export-contract.md` §1
  ("Unicode") and a new §1.2; `foundry-module/scripts/canonical.js` (`normalise`,
  header comment) and both module manifests, now **`1.0.6`**;
  `foundry-module/scripts/transport.js` (`SERVER_ARTIFACT_CODES`);
  `application/foundry/parser.py` (`_ordered`, new `_nfc_keys`, `canonical_bytes`,
  `parse_snapshot`); `application/foundry/submission.py`
  (`ARTIFACT_REFUSAL_CODES`); the review record above, which is closed by this
  entry.
- **Reason:** the encoder sorted an object's keys by their **pre**-NFC form and
  inserted them under their **post**-NFC form. Two distinct keys sharing an NFC
  form — `é` as U+00E9 and as U+0065 U+0301 — therefore wrote to the same
  property of the result, the second write won, and **the first value was
  silently dropped**, with no refusal, warning or record. That is precisely the
  outcome `canonical.js`'s own header says the contract exists to make
  impossible, and the one path in the encoder that lost data instead of refusing
  (§1.1 refuses an `undefined` value and an `undefined` array element). The
  Python verifier meanwhile did not normalise keys at all, so for the same input
  it emitted a document carrying **the same key twice** — a canonical form of
  nothing — and disagreed with the exporter for every non-NFC key. A third
  cross-language disagreement after RA-2 and I-1, in the same family.
- **Decision:** normalise before sorting, and **refuse a collision** in both
  implementations under one new code, `nfc_key_collision`. A merge is not
  available: the two keys are different properties of a Foundry document and no
  rule in this repository says which one an operator meant. The Manager refuses
  the artifact for the same reason, which makes this the one place
  canonicalisation is enforced rather than reported — a colliding document has no
  canonical form and cannot have come from a conforming exporter, where a merely
  non-canonical one is a conforming exporter's bytes in another order and stays a
  warning. The operator remedy is to rename one property in Foundry and export
  again. A **single** non-NFC key is not a collision and is normalised, not
  refused.
- **Alternatives considered:** resolving the collision by keeping the first or
  last key, rejected because the survivor would be chosen by the code-point order
  of the pre-NFC forms — a property of neither the data nor the operator's
  intent — and because it is data loss either way; refusing in the exporter only,
  which would leave the verifier emitting an invalid duplicate-key form and
  replace one cross-language disagreement with another; and normalising keys
  without refusing in the Manager, rejected because a document with no canonical
  form has nothing for `canonical_encoding` to report truthfully.
- **Added/removed scope:** the verifier now also normalises **string values** to
  NFC, which §1 always required and it never did. Without it the two
  implementations still disagreed over the boundary this entry claims to close:
  a decomposed value was reproduced verbatim and the artifact reported
  canonical, when the exporter would have emitted the composed form and
  different bytes. No field, route, schema or migration changes.
- **Dependency and critical-path effect:** **the module changes, so it is
  `1.0.6`**, and `1.0.5` is superseded. `exporter.version` reaches
  `foundry_snapshots.exporter_version` and checksum-bearing audit history, so
  two behaviourally different builds may not share a version string (CL3-I-2);
  this is the version bump the C-12 comment correction was carried against, and
  that correction is made here. **Rehearsals A and B were performed on `1.0.5`**
  and remain the evidence of record for that build; before any further rehearsal
  or supervised submission, `1.0.6` must be the build those instances actually
  serve. It was installed on `foundry1` and `foundry3` on 2026-08-10 and recorded
  in `docs/review/phase-2-module-1.0.6-install-2026-08-10.md`; **neither instance
  has been restarted**, so until they are, an export could still stamp `1.0.5`. For every document whose keys are already NFC — which is every ASCII
  key, and so every artifact either rehearsal produced — `1.0.6` emits **the same
  bytes** as `1.0.5`: normalisation is the identity there, so sorting before or
  after it cannot differ.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes the only path by which an Actor value could disappear
  from an export without a refusal. **Reachability against real data was never
  demonstrated and is still not claimed** — Foundry document keys are
  predominantly ASCII schema names and ids, and neither rehearsal artifact was
  examined for non-NFC keys; the candidates are `flags` namespaces and
  user-supplied map keys. The fix is worth making regardless, because the
  contract's claim is that data cannot vanish from an export without a refusal.
  The new refusal is reachable by an artifact no conforming exporter produces,
  so it cannot refuse a submission that would previously have been accepted and
  correct.
- **Testing effect:** the two tests that held the defect open are converted to
  the fixed behaviour and now run — the node `todo` is a real test and the strict
  `xfail` in `tests/test_snapshot_parser.py` is gone. `foundry-module/tests/canonical.test.mjs`
  covers both insertion orders, a nested collision whose message names the path
  and no value, a lone non-NFC key, and that normalisation precedes the sort.
  `tests/test_snapshot_parser.py` mirrors all four for the verifier, pins NFC
  normalisation of string values, and asserts `parse_snapshot` refuses a
  colliding artifact **with its checksum attached**.
  `tests/test_exporter_contract.py` adds an NFC boundary in the shape C-12
  established: five documents asserted three ways — the shipped exporter's bytes,
  the verifier's bytes, and that they are equal — plus one document both
  implementations must refuse with the same code.
  `foundry-module/tests/emit-canonical.mjs` reports a refusal as
  `{"code":…,"index":…}` on stderr with exit 1, so the cross-language test can
  assert *which* refusal rather than pattern-matching a stack trace.
  `tests/test_snapshot_submission.py` already walks both modules' syntax trees
  and holds `ARTIFACT_REFUSAL_CODES` and the module's `SERVER_ARTIFACT_CODES` to
  exactly the parser's codes, so the new code had to be declared in all three
  places to pass.
- **Migration effect:** none. Artifact identity is still the SHA-256 of the
  original bytes, no stored row changes, and no artifact previously accepted
  becomes invalid.
- **Security and operational effect:** operational only, and one deployment step:
  install `1.0.6` before the next supervised export. Refusal messages name the
  path and never a key's value, as every refusal in both files already does.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** the defect was found and recorded by
  Claude on 2026-08-10 and confirmed by the independent reviewer, who ruled that
  leaving the regression tests as `todo`/`xfail` left the release vulnerable and
  directed that both implementations be fixed together. Implemented by Claude.
  **Carries no independent review**, and goes to the Independent Reviewer with
  the rest of the returned package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.
  This closes the defect record; it closes no gate.

## v1.5 correction C-17 — canonical numbers are ECMAScript's, not `json.dumps`'s

Recorded 2026-08-10 on the **Blocking finding** of the independent review of the
C-16 package. **Proposed; not yet ruled.**

- **Affected requirements:** `docs/rules/foundry-export-contract.md` §1
  ("Numbers") and a new §1.3; `application/foundry/parser.py` (new `_double`,
  `_shortest_decimal`, `_ecmascript_number`, `_serialise`; `_ordered` renamed
  `_normalised`; `canonical_bytes`); `application/foundry/submission.py`
  (`ARTIFACT_REFUSAL_CODES`); `foundry-module/scripts/transport.js`
  (`SERVER_ARTIFACT_CODES`) and both module manifests, now **`1.0.7`**.
- **Reason:** the verifier encoded numbers with `json.dumps`, whose float
  formatting is a **different function** from `JSON.stringify`'s. Python
  switches to exponent notation at `1e16` and below `1e-4` and zero-pads the
  exponent; ECMAScript switches at `1e21` and below `1e-6` and does not. So the
  exporter emits `100000000000000000000` and `1e-7` where the verifier emitted
  `1e+20` and `1e-07`, and a conforming artifact containing either was reported
  `canonical_encoding = false`. This is the third instance of one defect — after
  C-12's key boundary and C-16's NFC boundary — in which both implementations
  were self-consistent and disagreed with each other, and it is the same
  consequence each time: the flag reports a defect in a conforming exporter, so
  the canonical-contract remediation and the stable-export diagnostic it feeds
  are not trustworthy. The earlier boundary tables could not see it: every
  number in the golden bundle and in both of them is a small integer, which the
  two languages format identically. `json.dumps` also wrote a Python `float`
  `9.0` as `9.0`, which the exporter — having one number type — writes as `9`.
- **Decision:** a contract number is an IEEE-754 double written as
  `Number::toString` writes it, stated as a rule table in §1.3 rather than by
  naming a library function. An integer literal is read as the double a browser
  would have read it as, so an artifact carrying `9007199254740993` is reported
  non-canonical against `9007199254740992`. A literal outside the double range
  has no canonical form and is a **refusal** under the exporter's own code,
  `non_finite_number`; `-0` does have one (`0`) and is reported, not refused,
  which is a deliberate asymmetry with the exporter and is written down as one.
- **Alternatives considered:** constraining the exporter to a number domain both
  languages format alike — rejected, because the domain would exclude ordinary
  dnd5e values and the exporter cannot control what Foundry holds; and matching
  Python's formatting in the exporter, which is impossible for the same reason
  C-12 gave for key order: `JSON.stringify` is `Number::toString` and a script
  cannot opt an ordinary number out of it.
- **Added/removed scope:** none.
- **Dependency and critical-path effect:** **the exporter's output is unchanged,
  byte for byte.** `canonical.js` has always delegated numbers to
  `JSON.stringify`, so, as with C-12, only the verifier and the contract
  described something else. The module bytes change for one reason only — the
  new refusal code is added to the client's bounded `SERVER_ARTIFACT_CODES`
  list — and that is a version bump to **`1.0.7`** under the version identity
  control (CL3-I-2), not a change to what is exported. **`1.0.7` was installed on
  `foundry1` and `foundry3` on 2026-08-10 23:24:18 UTC**
  ([record](../review/phase-2-module-1.0.7-install-2026-08-10.md)), replacing
  `1.0.6`, and both worlds were launched at 23:40, which is what reloads the
  package registry `exporter.version` is read from. No supervised export has been
  taken with it, and both rehearsals remain evidence for `1.0.5`, the build they
  exercised.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes a false `canonical_encoding = false` for conforming
  real exports, one boundary further out again — and this one is reachable by
  ordinary data, not only by a contrived key: dnd5e carries fractional values
  (encumbrance multipliers, spell scaling, currency weight), and any of them
  outside `[1e-4, 1e16)` produced the wrong flag. **Rehearsal B's recorded
  `canonical_encoding = yes` is not disproved**; the real artifact evidently held
  no number at these thresholds. The new refusal is reachable only by an artifact
  no conforming exporter produces, so it cannot refuse a submission that would
  previously have been accepted and correct — it replaces an uncaught
  `ValueError` from `json.dumps(allow_nan=False)`, which was not a refusal at
  all. Encoding is now a pure-Python pass rather than a C one: measured at
  **+100 ms** on a 1.2 MB, 500-Actor bundle against the 5-second preview
  threshold set by C-9 and the ~740 ms preview measured in
  `docs/review/phase-2-r4-500-actor-benchmark.md`.
- **Testing effect:** eleven number-boundary documents are asserted three ways in
  `tests/test_exporter_contract.py` in the shape C-12 established — the shipped
  exporter's bytes, the verifier's bytes, and that they are equal — covering both
  notation thresholds from both sides, multi-digit exponents, both ends of the
  double range, integer literals past `2**53`, negatives, decimal-point
  placement, and recursion. A fortieth-value `PRECISION_SPREAD` asserts the two
  languages compute the same shortest round-tripping digits, which is the half of
  `Number::toString` neither implementation writes itself. Two further
  cross-language tests pin the refusal both must raise and the one asymmetry.
  `tests/test_snapshot_parser.py` pins the verifier's half as a twenty-row table
  that also records what `json.dumps` used to write, and asserts the refusal
  reaches `parse_snapshot` **with its checksum attached** and the end-to-end flag
  for `1e-7` against `1e-07`. `foundry-module/tests/canonical.test.mjs` pins that
  `serialise` delegates numbers to `JSON.stringify`. The syntax-tree tests in
  `tests/test_snapshot_submission.py` again forced the new code to be declared in
  all three places.
- **Migration effect:** none. Artifact identity is still the SHA-256 of the
  original bytes, no stored row changes, and no artifact previously accepted
  becomes invalid.
- **Security and operational effect:** operational. The deployment step this
  entry called for — install `1.0.7` in place of `1.0.6` before the next
  supervised export — was **carried out on 2026-08-10**, and carrying it out
  corrected a claim this entry made: `exporter.version` is read from the server's
  package registry, which reloads at **world launch** rather than at process
  start, so "neither instance has been restarted" never preserved `1.0.5`. Both
  instances launched worlds at 20:55 that day, six minutes after `1.0.6` went in.
  The refusal message names the path and never a value, as every refusal in both
  files already does.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by the independent reviewer
  as the Blocking finding on the C-16 package; implemented by Claude. **Carries
  no independent review**, and returns to the Independent Reviewer with the rest
  of the package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.

## v1.5 correction C-18 — settlement terminates the whole ingress path, and step 4 retires the route

Recorded 2026-08-10 on the **re-review of C-15**, which held finding B-1 open for
the fourth time, and on the maintainer's ruling of 2026-08-10 between the two
routes the reviewer offered. **Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1, step 3 and step 4, and §5.4 (proxy configuration); §6 step 10's
  settlement note.
- **Reason:** C-15 settled an episode by stopping the **upstream endpoint**. That
  disposes of every request that had reached the endpoint, and not of a request the
  proxy has accepted, or is still reading, and has **not yet dialled upstream
  for**. Such a request is not in the endpoint's accept queue, so the stop does not
  reach it, and it has made no upstream attempt, so §5.4's "no upstream retry
  window" does not govern it either — that rule addresses a retry after a *refused*
  dial, and this request's **first** dial has not happened. It happens whenever the
  proxy gets to it, which under C-15's own step 4 can be after the endpoint has been
  restarted; the episode then commits behind a settled miss that has already
  authorized a fresh export. C-15's step 4 detects that afterwards, and **detection
  is not prevention**. The same reading condemns C-15's **S-A.3**, which nobody had
  questioned: it confirmed settlement by receiving a `502`/`503` from Caddy, and a
  `502` is Caddy's own answer, so receiving one establishes that Caddy is running.
- **Decision:** settlement remains a **state** rather than an observation, and
  becomes a state of the whole path in three parts. **S-A** — the endpoint is not
  running: S-A.1 the process that served the episode is gone, S-A.2 nothing is
  listening on its port. **S-I** — the ingress in front of it is **terminated, not
  drained**: S-I.1 no Caddy process exists, S-I.2 nothing is listening on `:80` or
  `:443`, TCP and UDP, S-I.3 nothing will bring either back, S-I.4 confirmed from
  off the host that the public name answers from no origin. **S-D** — all of it
  stays down through steps 2 and 3 until the outcome is recorded. Termination
  rather than a reload or a drain is the point: a reload leaves a running process
  deciding what to do with what it already holds, which is what no observation
  available to the operator can establish, and Caddy's grace period is not relied
  upon because S-I.1 reads the absence of the process. **Step 4 gains the
  prevention half**: after a settled miss the §5.4 `handle` block is removed and
  the endpoint returns behind a single-use `/recovery/<nonce>/…` path, the
  retirement is verified from off the host before the GM submits, and the GM
  re-points the module's `submissionEndpoint`. A request held by a hop this host
  cannot terminate then carries an address that no longer reaches the application.
  The confirming query is unchanged and is now described as the detector behind the
  preventer.
- **Alternatives considered:** the reviewer offered two routes, and the maintainer
  ruled for this one. The other — an **application-level mechanism that rejects
  pre-settlement requests after restart**, such as a submission epoch or one-time
  recovery token the endpoint requires — is deterministic and covers hops that
  cannot be terminated, and it stays **deferred, not rejected**, as the Phase 3
  improvement §9 already records. The reasons recorded with the ruling: it adds no
  unreviewed code to the submission path during a gate re-review, where the
  procedural route removes the class of claim the previous two remediations died on
  rather than adding a new one; and it should be designed against Phase 3's
  concurrent server rather than retrofitted to `wsgiref.simple_server`. Stopping
  Caddy was considered and **rejected** by C-15 as too costly; that judgement is
  reversed here, because the narrower stop it preferred does not settle the
  question, so the comparison was never between two settlements. An *actual proxy
  drain* — a reload, or removing the route and reloading — is rejected for the
  reason above: it leaves the process running.
- **Added/removed scope:** §5.4 requires a **terminable ingress** — one proxy, on
  this host, under a supervisor the operator can stop — so that a hop added in
  front of Caddy cannot appear unnoticed. The no-upstream-retry-window requirement
  is **kept and bounded**: it is worth requiring, and it is explicitly no longer
  what makes a miss safe. Route retirement and its verification are added scope for
  the operator, as is stopping and restarting Caddy. No code path, schema or
  credential changes; the recovery route is a temporary Caddyfile change restored
  when the episode closes.
- **Dependency and critical-path effect:** settlement no longer depends on whether
  Caddy fails or holds a request whose dial is refused, nor on what the Cloudflare
  edge does with a request it holds. It newly depends on the ingress being
  terminable from this host. S-A, S-I and S-D are all independent of the endpoint's
  concurrency model, so they hold unchanged for Phase 3's `freedom-web`.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes the reachable false miss that survived C-13, C-14 and
  C-15, at the cost of **host-wide downtime** for the duration of a reconciliation:
  Caddy fronts every service on this host, all three Foundry instances among them.
  That is acceptable for a hand-started Phase 2 rehearsal and is the reason the
  Phase 3 improvement is recorded. It also lengthens step 1 to seven recorded
  conditions across two processes plus the database check, which makes the standing
  question of whether **Unsettled** is reachable in practice harder rather than
  easier.
- **Observation, and two corrections it forced.** Caddy's half was exercised on
  2026-08-10 against a real Caddy 2.10.2, on an isolated rig with `admin off` and a
  stub upstream; the production instance was not stopped, reconfigured or reloaded.
  The finding itself was **reproduced**: a request the proxy had accepted with no
  upstream connection made survived the endpoint stop and was answered `201` after
  the restart, and the same episode with the proxy terminated delivered nothing.
  `uri strip_prefix` and the `502` inversion behaved as written. Two things did
  not. **Step 4 expected a `404` from the retired path and gets an empty `200`**:
  deleting a `handle` block produces whatever the rest of the site does with an
  unmatched path, which on these hostnames would be Foundry's answer, so the
  retirement is now the explicit `handle /api/v1/foundry/snapshots { respond 410 }`
  and step 4 checks for `410`. And **S-I.2 can pass while S-I.1 fails**, which §9
  now records with three timings rather than a caution.
- **S-I exercised against the production Caddy, 2026-08-10**, in
  maintainer-authorized windows. With one request held open on the origin's own
  listener — accepted over TLS 1.3, unrouted, the state a lost-pin episode is
  defined by — the listeners closed in **0.5 ms**, the process ended **4.3 s**
  later, and the held connection **closed with nothing delivered**: S-I's core
  claim, on the instance this procedure runs on rather than on a model. With
  nothing in flight the same stop completed in **4 ms**, so **the delay tracks what
  the proxy is holding rather than being a fixed cost**, and a rehearsal on an idle
  host would show the fast case and teach the wrong expectation. The public name
  answered `521` from Cloudflare throughout, on the submission path and the site
  root alike — the edge's own answer, neither Caddy's `502` nor anything the
  application could give — and the unit's `Restart=` is `no`. Production also
  carries a **UDP `:443`** listener, which is what makes S-I.2's UDP check
  necessary here rather than precautionary. Step 4's retirement against production
  remains unobserved: it needs a route that does not currently exist there.
- **Testing effect:** `tests/test_snapshot_recovery_settlement.py` gains two tests
  that are **each other's control**: a real proxy holding a complete request it has
  not dialled upstream for commits it across the restart when only the endpoint is
  stopped — the regression test for the finding — and the same episode with the
  proxy terminated as well ends with the request gone and nothing arriving after
  the restart. Deleting the terminate call from the second makes it fail where the
  proxy forwards, so the control is committed rather than described, which the
  first three remediations could not say.
  `tests/test_snapshot_recovery_documentation.py` gains two tests and updates six,
  pinning S-I's four parts, the inverted `502` check, the stated cost, S-D, the
  third withdrawn condition with its defect, §5.4's terminable-ingress requirement
  and bounded retry window, and step 4's retirement, verification and ordering.
- **Migration effect:** none.
- **Security and operational effect:** operational. Recovery still writes nothing:
  every added observation is read-only, and the two requests made through the
  public name are unauthenticated and empty and reach no application. The recovery
  route is a second way in and is therefore single-use, verified, and removed when
  the episode closes; §5.4 says so. Stopping Caddy is maintainer-authorized because
  it takes the site down deliberately.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex when re-reviewing
  C-15's remediation of B-1; the route chosen by the maintainer; implemented by
  Claude. **Carries no independent review**, and returns to the Independent
  Reviewer with the package. B-1 is **not** recorded as closed: the reviewer holds
  it open, and closing it is the reviewer's to do.
- **Acceptance Authority decision:** **none recorded.** The maintainer ruled on the
  route this entry takes; that is not a decision on the entry.

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
