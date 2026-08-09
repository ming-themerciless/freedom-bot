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
