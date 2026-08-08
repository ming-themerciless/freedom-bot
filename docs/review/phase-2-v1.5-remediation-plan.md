# Phase 2 remediation package plan — controlled baseline v1.5

Status: **Accepted by Peter Duscha, Acceptance Authority, on 2026-08-02.**
Packages **R1–R3 are released to start**; **R4 is not ready** until the §9.4
windows are set. **Phase 2 itself remains NOT READY and its gate is deferred** —
acceptance of this plan authorizes the remediation work, not the milestone.

Date: 2026-08-02 (drafted and accepted)

Rulings taken with this acceptance are recorded in
`docs/project-management/change-log.md` clarification C-2 and summarized in §12.

Supersedes: [`phase-2-package-plan.md`](phase-2-package-plan.md), which remains
readable as the historical plan for the rejected ADR 0008 implementation and
must not be executed.

Baseline: controlled baseline v1.5, implementation plan §12 Phase 2 and §20.

Repository state this plan is written against: `HEAD` is
`9432ded3aa960ed3be7532f05776c6458cff014f`; the I-02 implementation is present
in the working tree and **uncommitted**; nothing has been committed or pushed.

---

## 0. What this document is

It is the replacement remediation plan required by implementation plan §20
action 1. It decomposes the remaining Phase 2 work into four evidence-bearing
packages, states what each removes and what each preserves, and records the
estimates, owners, thresholds and evidence a gate decision will need.

It is **not** an implementation, an approval, or a gate. No code was changed
while it was written. No real export was read. No migration, backup or role
drill was run.

### 0.1 Authority and delivery resources

| Role | Holder |
|---|---|
| Product Sponsor / Acceptance Authority | Peter Duscha |
| Product Owner | Peter Duscha |
| Data Owner | Peter Duscha |
| Operations Owner | Peter Duscha |
| Delivery Lead | Peter Duscha |
| Working Technical Lead and proposed implementer | Claude |
| Required Independent Reviewer | Codex |
| Security-focused review | **Codex, as a distinct and separately reported pass** (ruled 2026-08-02) — covering authorization, artifact handling, audit content and runtime grants across R1–R4. It is reported separately from the independent review so that neither absorbs the other |

**Agent and tool names in this plan — Claude, Codex, Gemini — are delivery
resources, not authority.** They implement, review and recommend. Peter Duscha
retains accountable authority for every decision, gate, risk acceptance and
release in this plan, and records each one himself. An agent recommendation is
evidence for a decision, never the decision.

Per implementation plan §0.3 and `docs/project-management/README.md`, the Phase
2 gate is a mandatory review checkpoint (§16.4, *import/reconciliation*).
**A different Independent Reviewer than the implementer is required. If none is
available, the package remains `deferred`** — it is not approved, not
conditionally approved, and not closed on the implementer's own recommendation.

### 0.2 The four packages

| Package | Outcome |
|---|---|
| **R1** | Artifact, parser and profile remediation |
| **R2** | Identity, mappings and reconciliation |
| **R3** | Authorization, provenance and audit |
| **R4** | PostgreSQL and operational evidence |

They are implemented in order R1 → R2 → R3 → R4. R2 depends on R1's profile
shape, R3 on R2's apply path, and R4 on the final retained schema that R1–R3
determine.

---

## 1. Controlling decisions this plan is bound by

1. **ADR 0008 is rejected.** No generic character-state, balance or transaction
   representation survives.
2. **Phase 2 does not migrate Google Sheet character state**, and creates no
   interim editable representation of it.
3. **Sheet-era state stays on the accepted legacy path** until its typed owning
   package — named in `docs/project-management/data-migration-register.md` —
   migrates it once into a normalized relational model.
4. **Phase 2 is limited to** immutable supported Foundry export ingestion;
   bounded, checksum-first artifact validation; stable character identity and
   external Actor mappings; deterministic preview and reconciliation;
   `legacy_authority_deferred` reporting for fields with no accepted typed
   PostgreSQL authority; snapshot-only projections with provenance;
   current-role authorization rechecked at apply; atomic and idempotent import;
   immutable provenance and safe audit; and PostgreSQL concurrency, constraint,
   recovery and restricted-role evidence.
5. **Phase 3 remains read-only for character game state** and has not begun.
6. **No live Foundry storage access.** `/home/foundry/shared/worlds/the-guild/data/actors`
   is never opened; direct LevelDB or database reads are prohibited in every
   phase (ADR 0006, `.agents/AGENTS.md`).
7. **The two maintainer-authorized example exports** at
   `/opt/discord-bots/foundry-actor-exports` were not read during planning.
   Their contents are never committed, never copied into tests, and never
   rendered into logs, reports or this handoff.
8. **The active folder is `Characters (active)`**, and its stable folder
   identity comes from the supported export artifact, never from live Foundry
   storage.

### 1.1 Phase 2 scope boundary

**In scope:** the ten items in decision 4 above.

**Out of scope, explicitly:**

| Excluded | Why |
|---|---|
| Any migration of Sheet-era character state into PostgreSQL | Baseline v1.1/v1.5; each typed package owns its own one-time migration |
| Generic `character_state_values`, `character_balances`, `character_transactions` | ADR 0008 rejected |
| Snapshot-to-database corrections of any field | No accepted typed authority exists for the affected fields; correction workflows belong to the owning package (plan §12 Phase 5) |
| A Sheet-era value bootstrap | Rejected scope; the accepted legacy path remains authoritative |
| Phase 3 routes, templates, sessions, OAuth, CSRF | Plan §12 Phase 3; Phase 3 is not open |
| A live HTTP Foundry connector or any write-back to Foundry | Plan §12 Phase 7; ADR 0006 keeps one-way, read-only |
| Foundry LevelDB access of any kind | ADR 0006, `.agents/AGENTS.md` |
| The magic-item catalogue and `item_definitions` | Package 5.6a |
| Deleting or altering `connectors/sheets.py` or live bot Sheet behaviour | Plan §1, §15; the live bot still requires it |
| Committing, pushing or any Git mutation during planning | This engagement's instruction |

---

## 2. Package R1 — Artifact, parser and profile remediation

### 2.1 Exact outcome

The supported export contract, the checksum-first bounded ingestion path and the
fail-closed parser survive **unchanged in behaviour**, while the field profile
is redesigned so that a field with no accepted typed PostgreSQL authority
reports `legacy_authority_deferred` and names its owning package — and so that
no classification anywhere in the profile can be read as permission for Phase 2
to write a legacy field.

### 2.2 Included scope

- Preserve the ADR 0006 boundary and the deterministic export contract in
  `docs/rules/foundry-export-contract.md` **without revision**: no live access,
  no LevelDB, world-not-instance identity, exact `(core, system)` version tuple,
  platform-owned stable IDs, no write-back, content-addressed immutability,
  bounded folder set, folder identity as (stable folder ID, displayed path).
- Preserve checksum-before-parse, and the size, depth, shape and structural
  bounds, at exactly the limits the accepted contract states (§2.7 below).
- Preserve fail-closed validation of exporter schema, world, core/system
  version tuple and selected folder identity.
- **Redesign the field profile.** Replace the ADR 0008 correction/storage
  vocabulary (`CorrectionMode`, `Storage`, `ValueKind`, `SnapshotMode.COUNCIL_CORRECTABLE`)
  with an authority classification per field:
  - `snapshot_only` — read for display or calculation, never stored as an
    editable copy;
  - `database_authority` — an accepted typed PostgreSQL authority exists, so a
    real comparison is possible;
  - `legacy_authority_deferred` — no accepted typed PostgreSQL authority
    exists; the field names its owning migration package and **no equality
    comparison is performed or reported**;
  - `ignored` — deliberately not read.
- Every field currently classified `legacy_authority_deferred` carries the
  owning package from `data-migration-register.md`, and a consistency check ties
  the two together.
- Preserve exhaustiveness: every supported snapshot path has exactly one
  classification, unknown paths are reported and never writable, and a new
  supported schema field fails closed.
- Preserve snapshot-only calculation inputs and their provenance (snapshot
  checksum plus profile version).
- Rewrite `docs/rules/field-ownership.md` so the intended target owner and the
  current authority state are visibly separate, and no row implies a Phase 2
  correction control.
- Bump the profile version; the change makes every outstanding preview stale by
  construction.

### 2.3 Explicit exclusions

- No change to the export contract's limits, encoding rules or required fields.
  Any change is a §0.2 change-control item, not a remediation decision.
- No new snapshot path is added to the supported set.
- No correction mode, correction service or writable classification survives in
  any form, including as a "documentation-only" field that code can read.
- No Sheet column is read by anything in this package.

### 2.4 Dependencies and decisions

- **Depends on:** nothing beyond the accepted Phase 1 schema and the migration
  register/manifest, which supply the owning-package names. This is dependency
  **D-01a** and only D-01a; per-vocabulary readiness (D-01b) is not a Phase 2
  dependency because Phase 2 migrates nothing.
- **Decisions consumed:** OD-41 (closed — ADR 0008 rejected), OD-30, OD-14,
  ADR 0006 as amended.
- **Decisions required before this package starts:** none.

### 2.5 Files likely retained, modified or removed

| File | Disposition |
|---|---|
| `application/foundry/artifact.py` | retain unchanged |
| `application/foundry/parser.py` | retain unchanged |
| `docs/rules/foundry-export-contract.md` | retain unchanged |
| `domain/foundry.py` | retain unchanged |
| `domain/snapshot_values.py` | retain and modify — drop comparison machinery reachable only from rejected correction paths |
| `domain/field_profile.py` | retain and modify — authority classification replaces correction/storage/value-kind |
| `domain/foundry_profile.py` | retain and modify — reclassify every legacy field, bump version |
| `application/foundry/extraction.py` | retain and modify — extractors for deferred fields become report-only, never comparison inputs |
| `docs/rules/field-ownership.md` | retain and modify — target owner and authority state separated |
| `tests/test_field_profile.py`, `tests/test_field_ownership_document.py`, `tests/test_snapshot_values.py`, `tests/test_snapshot_extraction.py` | retain and modify |
| `tests/test_snapshot_artifact.py`, `tests/test_snapshot_parser.py`, `tests/foundry_fixtures.py` | retain unchanged |

### 2.6 Objective acceptance criteria

1. Every supported snapshot path resolves to exactly one classification; an
   unknown path yields `None` and is reported, never a default.
2. A synthetic Actor carrying a new supported-schema key produces an unclassified
   path and fails the run closed.
3. Every profile field with no accepted typed PostgreSQL authority reports
   `legacy_authority_deferred` **and** an owning package name that exists in
   `data-migration-manifest.json`.
4. No profile field is both `legacy_authority_deferred` and comparable; asking
   for an equality comparison on such a field raises rather than answers.
5. The profile exposes no correction mode, writable classification, or
   selectable-field allowlist. A grep-level and an API-level test both hold.
6. Snapshot-only roll inputs remain available and carry snapshot checksum plus
   profile version; a missing required input produces the defined typed refusal
   and never a default value.
7. Artifact and bundle limits equal §2.7 exactly; a limit change fails a test
   that names the accepted contract.
8. `field-ownership.md` and `domain/foundry_profile.py` remain mutually
   exhaustive under `tests/test_field_ownership_document.py`.

### 2.7 Inherited artifact and import limits

These are inherited from the accepted export contract **unchanged**. Any
revision requires §0.2 change control before implementation, not during it.

| Bound | Limit | Source |
|---|---|---|
| Artifact size | ≤ 64 MiB | contract §1; `DEFAULT_MAX_BYTES` |
| Nesting depth | ≤ 64 | contract §1; `DEFAULT_MAX_DEPTH` |
| `actors` entries | ≤ 500 | contract §2.6; `BundleLimits.max_actors` |
| `folders` entries | ≤ 64 | contract §2.5; `BundleLimits.max_folders` |
| Selected folders | 1–8 | contract §2.5; `BundleLimits.max_selected_folders` |
| Items per Actor | ≤ 4000 | contract; `BundleLimits.max_items_per_actor` |
| Unknown-path report | ≤ 50 listed, total counted separately | `FieldProfile.unknown_paths` |
| Preview/apply wall-clock budget | to be set by the Operations Owner before the gate; see §9 missing information | — |

### 2.8 Named tests

Retained and re-pointed: `tests/test_snapshot_artifact.py` (13 refusal tests),
`tests/test_snapshot_parser.py`, `tests/test_field_profile.py`,
`tests/test_field_ownership_document.py`, `tests/test_snapshot_extraction.py`.

Required new or rewritten test classes:

- `test_field_profile.py::test_every_deferred_field_names_an_owning_package_in_the_manifest`
- `test_field_profile.py::test_a_deferred_field_cannot_be_compared`
- `test_field_profile.py::test_the_profile_exposes_no_correction_or_writable_classification`
- `test_field_profile.py::test_a_new_supported_schema_field_fails_closed` (retained)
- `test_field_profile.py::test_snapshot_only_inputs_cannot_be_selected_for_database_write`
- `test_snapshot_artifact.py::test_the_accepted_contract_limits_are_unchanged`

### 2.9 PostgreSQL and operational evidence

None specific to R1: this package touches no schema. Its evidence is unit-level
and document-level. The profile version change is exercised as a staleness
input in R2 and against PostgreSQL in R4.

### 2.10 Security and privacy implications

- Ingestion bounds are the first line against a hostile or malformed artifact,
  and this package must not relax them while reorganising the profile.
- Removing `council-correctable` removes an entire write surface reachable from
  an uploaded file. That is the largest single security reduction in the
  remediation.
- The artifact must remain absent from `__repr__`, logs, refusal messages and
  reports; refusals name a checksum, a limit and an offset, never content.

### 2.11 Rollback and recovery effect

None. R1 changes no persistent state. Reverting it is a code revert.

### 2.12 Effort, confidence, assumptions

| Optimistic | Likely | Pessimistic |
|---|---|---|
| 2.0 | 3.0 | 4.5 |

Focused implementer-days, excluding maintainer decision time and the §8 review
allowance. **Confidence: medium-high.** The parser and artifact layers are
already accepted in shape; the risk is concentrated in the profile rewrite
touching a large parametrised test surface.

Assumptions: the migration register and manifest are authoritative for owning
packages and need no new rows; the export contract needs no revision.

### 2.13 Review and remediation allowance

Covered by the pooled allowance in §8. Security-focused review is required for
artifact handling.

### 2.14 Accountable roles

Implementer: Claude (working Technical Lead). Independent Reviewer: Codex.
Data Owner for the classification: Peter Duscha. Acceptance Authority: Peter
Duscha.

---

## 3. Package R2 — Identity, mappings and reconciliation

### 3.1 Exact outcome

Deterministic preview and reconciliation over a validated snapshot: every Actor
in the selected folder is accounted for as mapped, a create candidate, or
explicitly unresolved; mappings are stable and deliberately established, never
inferred from a name; legacy fields report `legacy_authority_deferred` instead
of a fabricated comparison; and a preview binds to exact inputs so that any
change to them applies nothing.

### 3.2 Included scope

- Preserve stable Actor/world mapping keyed on (world ID, external Actor ID),
  with the platform character ID independent of the Foundry `_id`, and the
  re-link fingerprint retained as human evidence only.
- Preserve deliberate identity establishment: a mapping is a Council act, never
  a name match (ADR 0006).
- **Duplicate display names are permitted as display data.** Two Actors sharing
  a display name under distinct external IDs are two create candidates. A legacy
  name-based candidate lookup **fails closed when more than one candidate
  exists** — subject to maintainer acceptance of I-05/OD-42 (§5). The current
  single-value claim lookup collapses duplicates and is corrected here.
- Replace field comparison for deferred fields: a `legacy_authority_deferred`
  row reports the field, its owning package and the snapshot value's presence,
  and performs **no** equality comparison and no match/difference claim.
- Retain real comparison only where an accepted typed PostgreSQL authority
  exists, producing the Foundry-out-of-date warning on mismatch and no warning
  on a match.
- **Exact preview binding.** A preview records: snapshot checksum, selected
  world ID, selected folder ID, folder path, field-profile version, exporter
  schema version, the database aggregate versions it read, and the idempotency
  request key. Apply rechecks every one. Any difference is a stale preview that
  applies nothing and records at most one safe refused attempt.
- No implicit deletion, deactivation or unmapping: an Actor absent from a later
  snapshot warns and changes nothing.
- Preserve snapshot-only projections with provenance for later roll consumers.

### 3.3 Explicit exclusions

- No selected-correction mechanism, no field selection list, no allowlist of
  writable fields; `FieldSelection` and its binding participation are removed.
- No character game-state write of any kind.
- No unique display-name constraint, index or stored identity key is added
  (§5).
- No name-based automatic mapping, in any fallback or convenience path.
- No web or Discord surface.

### 3.4 Dependencies and decisions

- **Depends on:** R1 (profile shape and version are preview inputs); D-01a.
- **Decisions required before this package starts:** **OD-42 / I-05** (§5). If
  it is not ruled, R2 proceeds on the existing accepted policy — names are not
  identities, mapping is never by name — and the duplicate-candidate behaviour
  remains an open item that keeps the gate deferred.
- **Decisions consumed:** ADR 0006 as amended, OD-35 (ID assigned at row
  creation), OD-12.

### 3.5 Files likely retained, modified or removed

| File | Disposition |
|---|---|
| `application/foundry/reconciliation.py` | retain and modify — deferred reporting replaces comparison; candidate lookup returns all candidates and fails closed on more than one |
| `application/foundry/import_service.py` | retain and modify — preview/binding retained, selection machinery removed |
| `application/foundry/roll_inputs.py` | retain unchanged |
| `application/snapshots.py` | retain and modify — `SnapshotRecord`, `SnapshotImportRecord`, `ExternalActorMapping`, `PlatformInitialization` retained; `CharacterTransaction` and `TransactionKind` removed |
| `application/character_state.py` | **remove as rejected scope** — it is the read model over the rejected stores and the only supplier of comparison values for legacy fields |
| `domain/names.py`, `tests/test_display_name_policy.py` | retain unchanged (accepted I-01 work) |
| `tests/test_snapshot_reconciliation.py`, `tests/test_snapshot_import_service.py` | retain and modify |
| `tests/test_snapshot_roll_inputs.py`, `tests/test_foundry_identity.py` | retain unchanged |

### 3.6 Objective acceptance criteria

1. Every Actor in the selected folder appears in the report exactly once as
   `mapped`, `create candidate`, or `unresolved` with a stated reason. The count
   of report entries equals the Actor count of the selected folder.
2. A renamed Actor under a stable external ID remains the same character; no new
   character is created.
3. Two Actors sharing a display name under distinct external IDs produce two
   create candidates and no error.
4. An unmapped Actor whose display name is already claimed by **one or more**
   characters is an explicit unresolved blocking issue naming every candidate;
   the run applies nothing.
5. Every legacy field produces a `legacy_authority_deferred` row naming its
   owning package, and produces no `match`, `differs` or warning verdict.
6. A field with accepted typed authority produces a warning on mismatch and no
   warning on a match.
7. Preview persists nothing: no character, mapping, snapshot or import row.
8. Changing any single bound input — snapshot bytes, folder, profile version,
   exporter schema, or a database aggregate version — makes the preview stale
   and applies nothing.
9. An Actor absent from a later snapshot warns and produces zero deletions,
   deactivations or unmappings.
10. Repeating an identical preview produces a byte-identical report.

### 3.7 Named tests

Retained and re-pointed: `tests/test_snapshot_reconciliation.py`,
`tests/test_snapshot_import_service.py` (staleness suite),
`tests/test_snapshot_roll_inputs.py`.

Required new or rewritten test classes:

- `test_snapshot_reconciliation.py::test_every_actor_is_mapped_a_create_candidate_or_explicitly_unresolved`
- `test_snapshot_reconciliation.py::test_two_characters_may_share_a_display_name`
- `test_snapshot_reconciliation.py::test_an_ambiguous_legacy_candidate_lookup_fails_closed_and_names_every_candidate`
- `test_snapshot_reconciliation.py::test_a_legacy_field_reports_deferred_authority_and_its_owning_package`
- `test_snapshot_reconciliation.py::test_a_legacy_field_is_never_reported_as_matching_or_differing`
- `test_snapshot_import_service.py::test_the_preview_binding_covers_every_declared_input` (table-driven over the binding's fields, so a new unbound input fails)
- `test_snapshot_import_service.py::test_no_service_api_accepts_a_field_selection`

### 3.8 PostgreSQL and operational evidence

Preview-writes-nothing and stale-preview refusal are proven against real
PostgreSQL in R4, not only against fakes.

### 3.9 Security and privacy implications

- Ambiguous identity is the highest-consequence failure in the milestone;
  failing closed on multiple candidates is the control.
- Reports name stable external IDs, counts and field keys. They must not render
  Actor payloads, and the deferred-authority row must not leak a legacy value it
  is not comparing.

### 3.10 Rollback and recovery effect

Preview is side-effect free, so recovery for this package is "discard the
preview". Apply-path recovery belongs to R3 and R4.

### 3.11 Effort, confidence, assumptions

| Optimistic | Likely | Pessimistic |
|---|---|---|
| 2.5 | 4.0 | 6.0 |

**Confidence: medium.** The residual risk is the preview binding: two defects
were found there during I-02, and removing the selection list changes the shape
of the binding rather than merely shortening it.

Assumptions: OD-42 is ruled as recommended; the accepted I-01 name-comparison
policy in `domain/names.py` is not reopened.

### 3.12 Review and remediation allowance

Pooled, §8. Independent review focus: the binding, and the candidate-lookup
fail-closed path.

### 3.13 Accountable roles

Implementer: Claude. Independent Reviewer: Codex. Data Owner for identity
outcomes: Peter Duscha.

---

## 4. Package R3 — Authorization, provenance and audit

### 4.1 Exact outcome

An import applies under **current** Guild Council authorization, commits its
snapshot record, created characters, external mappings, import record and audit
event in one PostgreSQL transaction or none of them, is idempotent under retry
and safe under concurrency, and records refusals without claiming or exposing
partial state — with every rejected correction, Sheet-bootstrap and generic-state
service, table, CLI and audit claim removed.

### 4.2 Included scope

- Current Guild Council authorization resolved **at apply**, from the
  authorization port, never carried from the preview. Revocation between preview
  and apply refuses the action.
- Platform Administrator alone does not imply Council import authority: folder
  selection and import triggering remain separate permissions.
- Atomic apply across snapshot record, characters, mappings, import record and
  audit event. An audit-write failure rolls back the import; a state failure
  writes no success audit.
- A refused attempt may be recorded in a separate transaction under the same
  correlation ID with a safe failure category, claiming no partial state.
- Database-enforced idempotency: the request key identifies an attempt; the
  (snapshot, folder, profile version) triple identifies an applied input, and
  only an applied row claims it. Repeats return the original result.
- Concurrency: two concurrent or overlapping applies produce exactly one durable
  effect and one audit effect.
- Safe audit content: checksum, actor, capability, action, time, reason,
  correlation ID and structured before/after facts — never artifact bytes,
  credentials, raw exception text or unrelated Actor data.
- **Removal of rejected scope:** the correction services and their audit claims;
  the Sheet-era value bootstrap; the generic state, balance and transaction
  repositories and their protocols; and every audit/traceability statement that
  asserts Phase 2 corrects a database-managed field.
- The supervised **first-import** bootstrap mode is retained, because plan §6.4
  and §6.5 require it: one-time, against an uninitialized dataset, with an
  explicit flag and a named supervisor, self-disabling on first success. What is
  removed is the **Sheet-era value** bootstrap, not the supervised first
  snapshot import.

### 4.3 Explicit exclusions

- No correction of any character field, by any actor, through any interface.
- No compensating-transaction machinery; Phase 2 has no balance to compensate.
- No second-approver workflow (one currently authorized Council member remains
  sufficient, plan §8.2).
- No audit update or delete use case, and no application path that could
  construct one.
- No Discord or web authorization surface; the port is the boundary.

### 4.4 Dependencies and decisions

- **Depends on:** R2 (the apply path and its binding).
- **Decisions required:** none new.
- **Decision to confirm with the maintainer:** the disposition of
  `tools/import_sheet_characters.py` (§6, decision D-3), because the four
  identity fields it writes are allocated to package 5.1 in the migration
  register.

### 4.5 Files likely retained, modified or removed

| File | Disposition |
|---|---|
| `application/authorization.py` | retain unchanged |
| `application/audit.py` | retain unchanged |
| `application/foundry/import_service.py` | retain and modify — `_apply_selections` and the correction dependency removed |
| `application/corrections.py` | **remove as rejected scope** |
| `application/bootstrap.py` | retain and modify — the supervised **snapshot** first-import gate stays (plan §6.4/§6.5); its role as the Sheet-era bootstrap gate is removed |
| `tools/bootstrap_manager.py` | retain and modify — supervised snapshot bootstrap CLI; no Sheet-era path |
| `tools/import_sheet_characters.py` | **requires decision** (D-3) |
| `tests/test_corrections.py` | **remove as rejected scope** |
| `tests/test_sheet_bootstrap_boundary.py` | retain and modify — the "connectors/ext/models untouched" and layering assertions are worth keeping; the Sheet-bootstrap-equivalence assertions are removed |
| `tests/test_bootstrap_cli.py` | retain and modify |

### 4.6 Objective acceptance criteria

1. An ordinary member is denied; one currently authorized Council member
   succeeds; authorization revoked between preview and apply refuses.
2. A Platform Administrator without Council authority cannot apply an import;
   folder selection alone grants nothing.
3. Injected failure at each of parser, character write, mapping write, import
   record and audit write leaves characters, mappings, snapshots and import
   records unchanged, writes no success audit, and records at most one safe
   refused event.
4. A duplicate request key returns the original result and produces no second
   durable effect and no second audit effect.
5. Two concurrent applies of the same input produce exactly one applied row.
6. No repository protocol, service or CLI in the retained tree exposes an update
   or delete for an audit or history record. Enforced by an API-shape test, not
   a convention.
7. `grep` and import-graph tests prove no module imports a removed correction,
   bootstrap-value or generic-state symbol.
8. Audit payloads contain no artifact bytes, credential, DSN or traceback; a
   test asserts the rendered payload against an allowlist of keys.

### 4.7 Named tests

Retained and re-pointed: the authorization, atomicity, idempotency and refusal
suites in `tests/test_snapshot_import_service.py`;
`tests/test_audit_events.py`.

Required new or rewritten test classes:

- `test_snapshot_import_service.py::test_authorization_is_rechecked_at_apply_not_carried_from_the_preview` (retained)
- `test_snapshot_import_service.py::test_platform_administrator_alone_cannot_apply_an_import`
- `test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state` (parametrised over the failure points in criterion 3)
- `test_snapshot_import_service.py::test_the_audit_payload_contains_only_allowlisted_keys`
- New `tests/test_rejected_scope_absent.py` — a package-level test class asserting that the rejected modules, tables, repository APIs and CLI paths do not exist and are not importable. This is the test that keeps the rejected scope from returning quietly.

### 4.8 PostgreSQL and operational evidence

Atomicity, idempotency, concurrency and append-only enforcement are proven
against real PostgreSQL in R4. R3 delivers the behaviour and its application
tests; R4 delivers the database proof.

### 4.9 Security and privacy implications

- Current-role authorization at apply is the control that makes a stale preview
  harmless after a role change.
- Removing the correction path removes the only Phase 2 route from an uploaded
  file to a character field.
- Safe refusal is a privacy control as much as an integrity one: a refusal must
  not disclose what it would have changed.

### 4.10 Rollback and recovery effect

An apply is one transaction, so recovery from a failed apply is the rollback
itself. Operationally: identify the last applied (snapshot, folder, profile)
triple, re-run the same immutable input, and rely on idempotency. Never repair a
partial import by row edits. The removal of the generic state tables **reduces**
the recovery surface: there is no half-migrated character state to reconcile.

### 4.11 Effort, confidence, assumptions

| Optimistic | Likely | Pessimistic |
|---|---|---|
| 2.0 | 3.0 | 4.5 |

**Confidence: medium-high.** Most of this package is deletion plus re-pointing
of an already-tested apply path. The uncertainty is how much of
`import_service.py`'s ordering must be re-derived once selections are gone.

Assumptions: the supervised first-import bootstrap remains in scope per plan
§6.4/§6.5; D-3 is ruled before the package closes.

### 4.12 Review and remediation allowance

Pooled, §8. **Security-focused review is required** for authorization and audit
content.

### 4.13 Accountable roles

Implementer: Claude. Independent Reviewer: Codex. Security reviewer: as
designated by Peter Duscha. Acceptance Authority: Peter Duscha.

---

## 5. Package R4 — PostgreSQL and operational evidence

### 5.1 Exact outcome

A schema containing only the retained Phase 2 tables, applied by a replacement
migration; runtime grants covering exactly those tables; and executed evidence —
constraint, concurrency, rollback, append-only, upgrade/downgrade/upgrade,
backup/restore/rerun, and direct `freedom_runtime_test` denial — followed, after
implementation review, by the maintainer-supervised preview of the real exports
and the Data Owner attestation.

### 5.2 Included scope

**Replacement migration strategy from the uncommitted state.** Migration
`0002_foundry_snapshot_and_character_state.py` is uncommitted and has been
applied only to the disposable `freedom_test` database. It is therefore
**replaced in place** rather than corrected by a follow-on migration: the
"never edit an applied migration" rule in plan §14.3 protects migrations that
exist in committed history or a durable environment, and this one is in
neither. Concretely:

1. `alembic downgrade base` against `freedom_test`, then drop and recreate the
   disposable database, so no rejected table survives in any environment;
2. delete and rewrite `0002` as `0002_foundry_snapshot_and_identity.py`
   containing only the retained objects;
3. `alembic upgrade head` on the empty database and `alembic check` to prove the
   metadata and the migration agree;
4. record in the submission that revision `0002` was replaced before it ever
   entered committed history, with the reason.

Retained schema objects: `foundry_snapshots`; `snapshot_imports`;
`platform_initialization`; the provenance columns
`external_actor_mappings.established_by_snapshot_id` and `.folder_id`; the
append-only triggers on `audit_events`, `foundry_snapshots` and
`snapshot_imports`.

Removed schema objects: `character_state_values`, `character_balances`,
`character_transactions`, and the `character_transactions` append-only trigger.

**Runtime grants for the final retained tables only.** The current
`infra/postgresql/runtime-grants.sql.tmpl` must not be applied as it stands: it
grants the rejected tables. It is rewritten to grant
`SELECT, INSERT, UPDATE, DELETE` on the operational tables and `SELECT, INSERT`
only on `audit_events`, `foundry_snapshots`, `snapshot_imports` and
`platform_initialization`, with `UPDATE`, `DELETE` and `TRUNCATE` revoked on
each of those four.

**Executed evidence**, all against real PostgreSQL:

- constraint evidence: unique `(world_id, external_actor_id)`, unique
  `(character_id, world_id)`, unique snapshot checksum, the partial unique index
  on applied `(snapshot_id, folder_id, profile_version)`, foreign-key
  `RESTRICT` behaviour, and the check constraints;
- concurrency evidence: two threads on two engines applying the same input,
  producing exactly one applied row;
- rollback evidence: injected failures at the R3 failure points, leaving no row
  behind;
- append-only evidence: trigger refusal of `UPDATE` and `DELETE` on each
  append-only table, including for the schema owner;
- migration evidence: `upgrade → downgrade → upgrade` against `freedom_test`,
  plus `alembic check`;
- backup/restore evidence: back up, run an import, restore, prove the restored
  schema/table/row inventory matches the pre-drill inventory, then re-run the
  same immutable input and prove idempotent identity and audit effects;
- **restricted-role evidence, live.** `freedom_runtime_test` exists, is
  `NOLOGIN`, non-superuser, cannot create roles or databases, cannot replicate
  and cannot bypass RLS; `foundry` is a member. Evidence method: as `foundry`,
  `SET ROLE freedom_runtime_test`, then (a) perform each allowed operation and
  show it succeeds, and (b) attempt `UPDATE`, `DELETE` and `TRUNCATE` on every
  append-only table and show each is rejected, capturing the SQLSTATE. `RESET
  ROLE` afterwards. This replaces the previous template-review-only evidence.

**Supervised real-export preview**, performed by the maintainer **only after the
implementation review closes**, producing the reconciliation report and the Data
Owner attestation defined by implementation plan §12 Phase 2: export SHA-256,
exporter and profile versions, selected world/folder, total Actors, and the
count and identifier of every mapped, create-candidate and explicitly unresolved
Actor, with the disposition and reason for each unresolved identity, and a
statement that no artifact or real Actor payload was committed.

### 5.3 Explicit exclusions

- No real artifact, Actor payload, or export-derived fixture is committed, at
  any point, in any form.
- No drill runs against a production or shared database; `freedom_test` only.
- No grant is applied to a production role.
- No schema object is created for a future package's field group.
- No destructive drill is run before the plan is approved — none was run during
  planning.

### 5.4 Dependencies and decisions

- **Depends on:** R1–R3 (the final retained schema), and on the implementation
  review closing before the real-export preview.
- **Environment:** disposable database `freedom_test`; owner/test login
  `foundry`; restricted role `freedom_runtime_test`; Unix-domain socket; this
  host.
- **Decisions required:** the rehearsal window (§9), which is Peter's to set.

### 5.5 Files likely retained, modified or removed

| File | Disposition |
|---|---|
| `migrations/versions/0002_foundry_snapshot_and_character_state.py` | **remove as rejected scope**, replaced by a rewritten `0002` |
| `adapters/database/tables.py` | retain and modify — three table definitions removed, snapshot/import/initialization retained |
| `adapters/database/repositories.py` | retain and modify — state, balance and transaction repositories removed |
| `adapters/database/unit_of_work.py` | retain and modify — the removed repositories dropped from the shared session |
| `application/repositories.py` | retain and modify — the corresponding protocols removed |
| `infra/postgresql/runtime-grants.sql.tmpl` | retain and modify — final retained tables only |
| `infra/postgresql/backup-restore-drill.sh` | retain and modify — cover the retained Phase 2 tables |
| `tests/test_snapshot_database.py` | retain and modify |
| `tests/test_runtime_grants.py` | retain and modify — add live `SET ROLE` denial |
| `tests/fakes.py` | retain and modify |
| `tests/test_database_schema.py`, `tests/test_database_postgresql.py`, `tests/test_migration_safety.py`, `tests/test_database_backup_restore.py` | retain and modify |
| `docs/operations/foundry-snapshot-import.md` | retain and modify |
| `docs/operations/sheet-import.md` | supersede documentation |
| `docs/review/phase-2-i-02-submission.md` | supersede documentation — superseded by a new submission |
| `tests/test_submission_traceability.py` | retain and modify — re-point at the new submission |

### 5.6 Objective acceptance criteria

1. `alembic upgrade head` on an empty database, `alembic downgrade base`, and
   `upgrade head` again all succeed; `alembic check` reports no new operations.
2. The applied schema contains **zero** generic character-state, balance or
   transaction tables. Asserted by an inventory test, not by inspection.
3. Every append-only table rejects `UPDATE` and `DELETE` at the database level,
   including for the schema owner.
4. Under `SET ROLE freedom_runtime_test`: every allowed operation succeeds, and
   every applicable `UPDATE`, `DELETE` and `TRUNCATE` on an append-only table is
   denied, with the SQLSTATE recorded.
5. Backup restore reproduces the pre-drill schema, table and row inventory
   exactly, and the importer re-runs on the restored database with no duplicate
   identity, mapping, import or audit effect.
6. Two concurrent applies produce exactly one applied row and one audit effect.
7. The supervised real-export preview accounts for every Actor and produces zero
   unexplained identity discrepancies.
8. `git status` and a diff scan show no artifact, Actor payload, export-derived
   fixture, credential or DSN added anywhere in the tree.

### 5.7 Named tests

Retained and re-pointed: `tests/test_snapshot_database.py`,
`tests/test_runtime_grants.py`, `tests/test_migration_safety.py`,
`tests/test_database_backup_restore.py`, `tests/test_database_schema.py`.

Required new or rewritten test classes:

- `test_runtime_grants.py::test_set_role_denies_update_on_every_append_only_table`
- `test_runtime_grants.py::test_set_role_denies_delete_on_every_append_only_table`
- `test_runtime_grants.py::test_set_role_denies_truncate_on_every_append_only_table`
- `test_runtime_grants.py::test_set_role_permits_the_allowed_operations`
- `test_database_schema.py::test_no_generic_state_balance_or_transaction_table_exists`
- `test_database_backup_restore.py::test_restore_matches_the_pre_drill_inventory_and_supports_idempotent_rerun`
- `test_snapshot_database.py::test_two_concurrent_applies_produce_one_effect` (retained)

### 5.8 PostgreSQL and operational evidence

This package **is** the operational evidence. Every item in §5.2 is executed and
its exact command and result reported in the submission, with any check that
could not be run stated as not run rather than implied.

### 5.9 Security and privacy implications

- The grants rewrite is the highest-consequence file in the package: a grant on
  a removed table is harmless, but a missing `REVOKE` on a retained append-only
  table silently weakens the history guarantee. Security-focused review is
  required for it.
- The real-export preview is the only point in Phase 2 where real player data is
  processed. It runs supervised, after review, writes no artifact into the
  repository, and produces an attestation using stable external IDs and counts
  rather than player detail.
- Backup artifacts from the drill contain synthetic data only and are removed
  after the drill.

### 5.10 Rollback and recovery effect

The package delivers the documented recovery path: pre-migration backup, an
exercised restore, an idempotent re-run, and a documented owner-side procedure
for the exceptional case where a trigger must be disabled. Rollback triggers are
in §7.

### 5.11 Effort, confidence, assumptions

| Optimistic | Likely | Pessimistic |
|---|---|---|
| 2.5 | 4.0 | 6.5 |

**Confidence: medium.** The drills are mechanical; the uncertainty is in how
much test rework the schema reduction forces across the four database suites,
and in the first live `SET ROLE` evidence, which has never been run here.

Assumptions: `freedom_test` and `freedom_runtime_test` remain available;
maintainer time for the supervised preview is scheduled (§9); the exports match
the accepted contract — if they do not, R2 §3.2's fail-closed validation is
correct behaviour and the contract change goes through §0.2, which is R-02's
contingency.

### 5.12 Review and remediation allowance

Pooled, §8. **Security-focused review is required** for runtime grants.
Operations Owner recommendation is required for the drills, and Data Owner
recommendation for the attestation.

### 5.13 Accountable roles

Implementer: Claude. Independent Reviewer: Codex. Operations Owner: Peter
Duscha. Data Owner: Peter Duscha. Acceptance Authority: Peter Duscha.

---

## 6. I-05 / OD-42 — display-name identity ruling

**Ruled by Peter Duscha, Acceptance Authority, on 2026-08-02, as recommended.
I-05 is closed.** It was put as a proposed maintainer ruling, never an agent
assumption; the authoritative text is in `docs/discovery/open-decisions.md`
under OD-42, indexed in `docs/project-management/decision-register.md`.

### 6.1 The ruling

> Display names are not unique identities. Multiple characters may share a
> display name. Stable character IDs and external Actor IDs provide identity.
> Any legacy name-based candidate lookup fails closed when more than one
> candidate exists.

### 6.2 What the accepted plan already establishes, with exact citations

Three of the four clauses are already unambiguous in accepted material:

| Clause | Established by |
|---|---|
| Display names are not identities | `.agents/AGENTS.md` § *Architecture → Domain*: *"Use stable IDs for actors and records. Display names are mutable and are not identities."* Implementation plan §3, governing principle 6: *"Stable IDs identify users, characters, and external records. Names are mutable display values."* |
| Stable IDs provide identity, and labels are never keys | Implementation plan §7.3.1: *"Reference identities use stable internal IDs; display labels are mutable and never serve as foreign keys."* ADR 0006 § *Idempotency*: the Foundry `_id` is *"a mapping key, not an identity"*; `characters.id` stays a platform UUID |
| Identity is never established from a name | ADR 0006 § *Mapping is Council-established, never inferred*: *"Never by name matching."* Carried forward intact by the 2026-08-02 amendment, § *What this amendment does not change* |
| Duplicates can occur and must be reported | Implementation plan §12 Phase 2, mandatory tests: *"malformed Actor data, duplicate external Actor ID, duplicate display name, missing mapping and ambiguous mapping"* — a scenario the import must report |

### 6.3 What is genuinely open, and why a ruling is still needed

The accepted record did not state whether a duplicate display name may
**persist** in PostgreSQL, nor what a legacy name-based candidate lookup does
when it finds **more than one** candidate. Silence there had been read two
incompatible ways: as licence to add a unique constraint, and as licence to pick
the first candidate. Both readings were available, which is why OD-42 was ruled
explicitly rather than I-05 being declared already closed by the existing text.

### 6.4 What the ruling does and does not change

- **Does not** add a unique constraint or index on `characters.display_name`,
  and does not add a stored identity key. A uniqueness rule would make a
  legitimate in-world situation — two characters called *Grim* — an import
  failure and a data-repair task. Application enforcement is accepted
  deliberately.
- **Does** require the reconciliation candidate lookup to return **all**
  candidates and refuse the run when more than one exists. The current
  single-value claim lookup collapses duplicates and is a defect under this
  ruling; correcting it is inside R2's scope and is criterion 3.6.4.
- **Does** close I-05 and narrow R-01's residual to the legacy bot's own
  comparison, which remains outside Phase 2.

---

## 7. Required disposition analysis

Every affected I-02 file or coherent file group, classified. **Nothing is
deleted during this planning run**; this table is the proposal that
implementation would execute after approval.

### 7.1 Application layer

| File / group | Disposition | Reason |
|---|---|---|
| `application/character_state.py` | **remove as rejected scope** | The read model over `character_state_values` / `character_balances` / `character_transactions`. It exists only to serve comparisons and corrections of fields that have no accepted typed authority |
| `application/corrections.py` | **remove as rejected scope** | Standard/protected/compensating corrections of database-managed fields. Correction workflows belong to the typed owning package (plan §12 Phase 5, §6.2) |
| `application/bootstrap.py` | **retain and modify** | The supervised **first snapshot import** gate is required by plan §6.4 and §6.5 and is not rejected scope. Its use as the Sheet-era value bootstrap gate is removed, as is its dependency on the removed stores |
| `application/snapshots.py` | **retain and modify** | `SnapshotRecord`, `SnapshotImportRecord`, `ExternalActorMapping`, `PlatformInitialization` retained; `CharacterTransaction` and `TransactionKind` removed with the ledger |
| `application/authorization.py` | **retain unchanged** | Current-effective-privilege resolution at apply is exactly what the remediated scope needs |
| `application/audit.py` | **retain unchanged** | Append-only audit events, unchanged by the removal |
| `application/foundry/artifact.py` | **retain unchanged** | Checksum-before-parse and bounded ingestion are preserved verbatim |
| `application/foundry/parser.py` | **retain unchanged** | Contract, deployment, folder-graph and identity validation are preserved verbatim |
| `application/foundry/extraction.py` | **retain and modify** | Extraction stays; values for deferred fields become report-only and must not feed a comparison |
| `application/foundry/reconciliation.py` | **retain and modify** | Deferred-authority reporting replaces legacy comparison; candidate lookup returns all candidates and fails closed |
| `application/foundry/import_service.py` | **retain and modify** | Preview, binding, atomic apply and idempotency retained; `FieldSelection`, `_apply_selections` and the corrections dependency removed |
| `application/foundry/roll_inputs.py` | **retain unchanged** | Snapshot-only projections with provenance are in scope |
| `application/sheet_import.py`, `application/imports.py` | **retain unchanged** | Accepted I-01 work; not modified by I-02 |

### 7.2 Domain layer

| File / group | Disposition | Reason |
|---|---|---|
| `domain/field_profile.py` | **retain and modify** | Redesign: authority classification replaces `CorrectionMode`, `Storage`, `ValueKind` and `SnapshotMode.COUNCIL_CORRECTABLE`. Exhaustiveness, fail-closed enumeration and versioning are preserved |
| `domain/foundry_profile.py` | **retain and modify** | Every legacy field is reclassified `legacy_authority_deferred` with its owning package; the profile version is bumped |
| `domain/foundry.py` | **retain unchanged** | Snapshot identity value objects |
| `domain/snapshot_values.py` | **retain and modify** | Normalisation and the distinction between *different* and *unable to compare* survive; comparison machinery reachable only from removed correction paths is dropped |
| `domain/names.py` | **retain unchanged** | Accepted I-01 shared comparison policy |

### 7.3 Persistence and infrastructure

| File / group | Disposition | Reason |
|---|---|---|
| `migrations/versions/0002_foundry_snapshot_and_character_state.py` | **remove as rejected scope** | Creates the three rejected tables. Replaced in place per §5.2 because it is uncommitted and exists only in a disposable database |
| `adapters/database/tables.py` | **retain and modify** | `foundry_snapshots`, `snapshot_imports`, `platform_initialization` and the mapping provenance columns retained; the three rejected tables removed |
| `adapters/database/repositories.py` | **retain and modify** | Snapshot, import, mapping and initialization repositories retained; state, balance and transaction repositories removed |
| `adapters/database/unit_of_work.py` | **retain and modify** | One shared session retained — it is what makes an import atomic; the removed repositories are dropped from it |
| `application/repositories.py` | **retain and modify** | The corresponding protocols removed; `ExternalActorMappingRepository`'s deliberate absence of a name lookup is preserved |
| `infra/postgresql/runtime-grants.sql.tmpl` | **retain and modify** | Rewritten for the final retained tables. **Must not be applied in its current form** — it grants rejected tables |
| `infra/postgresql/backup-restore-drill.sh` | **retain and modify** | Extended to the retained Phase 2 tables |

### 7.4 Operator entry points

| File / group | Disposition | Reason |
|---|---|---|
| `tools/bootstrap_manager.py` | **retain and modify** | The supervised snapshot bootstrap CLI stays; any Sheet-era path and any reference to removed stores is dropped |
| `tools/import_sheet_characters.py` | **retain and modify — revert to committed state** (ruled 2026-08-02) | I-02 modified this accepted I-01 tool into a Sheet-era bootstrap. The Sheet-era bootstrap is rejected scope, and the tool's four identity fields are allocated to package **5.1** in the migration register. **Ruling:** revert the I-02 modifications (profile scope check, supervisor requirement, one-time gate, exit code 6) to the committed state, and record the tool as **dormant** with its disposition owned by package 5.1. It is not a Phase 2 write path, which is what lets threshold T-6 be asserted cleanly. No accepted I-01 work is discarded |

### 7.5 Tests

| File / group | Disposition | Reason |
|---|---|---|
| `tests/test_snapshot_artifact.py`, `tests/test_snapshot_parser.py`, `tests/test_foundry_identity.py`, `tests/test_snapshot_roll_inputs.py`, `tests/foundry_fixtures.py` | **retain unchanged** | Cover retained behaviour |
| `tests/test_field_profile.py`, `tests/test_field_ownership_document.py`, `tests/test_snapshot_values.py`, `tests/test_snapshot_extraction.py` | **retain and modify** | Re-pointed at the authority classification |
| `tests/test_snapshot_reconciliation.py`, `tests/test_snapshot_import_service.py` | **retain and modify** | Deferred reporting, ambiguity fail-closed, selection removal |
| `tests/test_snapshot_database.py`, `tests/test_runtime_grants.py`, `tests/fakes.py`, `tests/test_database_schema.py`, `tests/test_database_postgresql.py` | **retain and modify** | Reduced schema; live `SET ROLE` evidence added |
| `tests/test_corrections.py` | **remove as rejected scope** | Tests the removed correction services. **This is where the deliberate skip disappears**: `test_every_database_managed_field_has_a_correction_path` skipped `character.downtime_progress`; with correction scope removed, the skip has no subject and is not reclassified but deleted with its module |
| `tests/test_sheet_bootstrap_boundary.py` | **retain and modify** | The layering and "live bot untouched" assertions are worth keeping; the Sheet-bootstrap-equivalence assertions go |
| `tests/test_bootstrap_cli.py` | **retain and modify** | Supervised snapshot bootstrap only |
| `tests/test_submission_traceability.py` | **retain and modify** | Re-pointed at the new submission document |
| `tests/snapshot_harness.py` | **retain and modify** | Harness minus the removed stores |
| New `tests/test_rejected_scope_absent.py` | **new** | Asserts the rejected modules, tables, repository APIs and CLI paths are absent and non-importable |

### 7.6 Documentation

| File / group | Disposition | Reason |
|---|---|---|
| `docs/adr/0006-foundry-integration-boundary.md` | **retain unchanged** | The amendment is accepted and its decisions are preserved by this plan |
| `docs/adr/0008-profile-driven-character-state.md` | **retain unchanged** | Correctly marked Rejected; retained as the considered alternative |
| `docs/rules/foundry-export-contract.md` | **retain unchanged** | The accepted contract |
| `docs/rules/field-ownership.md` | **retain and modify** | Target owner and current authority state separated; no row implies a Phase 2 correction control |
| `docs/operations/foundry-snapshot-import.md` | **retain and modify** | Correction and Sheet-bootstrap procedures removed; the replacement migration, grants and drill procedures added |
| `docs/operations/sheet-import.md` | **supersede documentation** | Its subject — the narrow Sheet-era bootstrap — is rejected scope. Under the D-3 ruling the document reverts to describing the dormant committed tool, with a note that its migration disposition belongs to package 5.1 |
| `docs/review/phase-2-i-02-submission.md` | **supersede documentation** | Evidence record of the superseded implementation; a new submission replaces it for the gate |
| `docs/review/phase-2-package-plan.md` | **supersede documentation** | Already marked superseded; a pointer to this plan was added |
| `docs/review/phase-2-submission.md`, `docs/review/phase-0-submission.md`, `docs/review/phase-1-submission.md` | **retain unchanged** | Accepted historical records |

---

## 8. Acceptance thresholds

Objective, and each one is a gate condition rather than an aspiration.

| # | Threshold | Measured by |
|---|---|---|
| T-1 | **Zero partial commits** in every injected failure path | Parametrised injected-failure tests at each failure point; row counts before and after are equal |
| T-2 | **Exactly one durable effect** for duplicate and concurrent applies | One applied `snapshot_imports` row, one audit effect, no second character or mapping, under retry and under two concurrent threads on real PostgreSQL |
| T-3 | **Zero unexplained identity discrepancies** at the real rehearsal | The Data Owner attestation records a disposition and reason for every unresolved identity; any unexplained one blocks the gate |
| T-4 | **Every Actor accounted for** | Report entries = Actor count of the selected folder; each is mapped, a create candidate, or explicitly unresolved |
| T-5 | **Zero retained generic state, balance, correction or transaction tables or repository APIs** | Schema inventory test plus `tests/test_rejected_scope_absent.py` |
| T-6 | **Zero Phase 2 write path for a legacy Sheet field** | API-shape and import-graph tests; resolution of D-3 |
| T-7 | **Zero real Actor payloads in Git, tests or logs** | Diff scan, `.gitignore` check, `__repr__`/log assertions, and the attestation statement |
| T-8 | **All applicable restricted-role mutation attempts denied** | `SET ROLE freedom_runtime_test`; `UPDATE`, `DELETE`, `TRUNCATE` on every append-only table rejected, SQLSTATE recorded; allowed operations succeed |
| T-9 | **Backup restore matches the pre-drill schema, table and row inventory and supports idempotent rerun** | Inventory diff is empty; the re-run produces no duplicate identity, mapping, import or audit effect |
| T-10 | **Exact parser and artifact limits inherited from the accepted contract**, or explicitly revised through change control | The limits test in §2.7; any change carries a dated change-log entry |
| T-11 | **The deliberate skip is gone.** The full suite reports no skip attributable to unresolved correction scope | Full-suite run; the `character.downtime_progress` correction test is removed with its module, not re-skipped |
| T-12 | **Independent review closure** of every blocking security, identity, atomicity, migration and recovery finding | Reviewer record plus re-review |

---

## 9. Estimates, capacity and windows

### 9.1 Three-point totals

Focused implementer-days for one implementer. Excludes maintainer decision time
and maintainer-supervised rehearsal time.

| Package | Optimistic | Likely | Pessimistic |
|---|---|---|---|
| R1 — Artifact, parser and profile | 2.0 | 3.0 | 4.5 |
| R2 — Identity, mappings and reconciliation | 2.5 | 4.0 | 6.0 |
| R3 — Authorization, provenance and audit | 2.0 | 3.0 | 4.5 |
| R4 — PostgreSQL and operational evidence | 2.5 | 4.0 | 6.5 |
| **Implementation subtotal** | **9.0** | **14.0** | **21.5** |
| Independent review and remediation allowance | 3.0 | 5.0 | 8.0 |
| **Total** | **12.0** | **19.0** | **29.5** |

The historical Phase 2 range of 8–15 working days is superseded for the
remaining work, as plan §12 Phase 2 already records.

### 9.2 Review and remediation allowance

The 3.0 / 5.0 / 8.0 allowance covers one full independent review pass across all
four packages, the security-focused review of authorization, artifact handling,
audit content and runtime grants, remediation of blocking and important
findings, and one re-review. Blocking findings are fixed and re-reviewed before
any dependent work starts. If a second full review pass is needed, that is a
forecast variance to report under §0.4, not silent compression.

### 9.3 Capacity and environment

- One focused implementer; no parallel packages.
- Named environment: this host; disposable database `freedom_test`; owner/test
  login `foundry`; restricted role `freedom_runtime_test`; Unix-domain socket.
  No other database is touched.
- Maintainer decisions and the supervised rehearsal are not on the implementer's
  clock.
- No real Council snapshot, `.env`, credential, live Sheet, live Foundry,
  Discord or production database is read at any point in R1–R3. R4's real-export
  preview is maintainer-supervised, after implementation review.

### 9.4 Windows and thresholds still to be supplied by the maintainer

These are §20 readiness items this plan cannot supply. **Ruled 2026-08-02: they
are required before package R4, not before any work.** R1–R3 need no maintainer
window and are released to start; R4 remains `not ready` until all four exist,
and the gate cannot close without them.

1. **Maintainer availability window** for decisions and gate approval.
2. **Date or bounded window for the supervised real-export rehearsal.**
3. **Monitoring / observation period** after the rehearsal before the gate
   decision. **Set 2026-08-05 by Peter Duscha:** zero hours; perform immediate
   post-run verification, then stop the disposable endpoint and clean its
   rehearsal state. There is no retained Phase 2 service/state for a longer
   observation to measure.
4. **Preview and apply wall-clock runtime budget** for a 500-Actor artifact.
   **Set 2026-08-05 by Peter Duscha:** 5 seconds for preview and 5 seconds for a
   fresh apply on this named host. These are Phase 2 rehearsal acceptance
   thresholds, not production capacity promises or application timeouts. Based
   on `phase-2-r4-500-actor-benchmark.md` and independently reproduced by
   Codex.

Items 3 and 4 are closed. Items 1 and 2 remain open until Peter schedules the
supervised decision/gate session and real-export rehearsal.

---

## 10. Rollback triggers

Any of these stops the affected package and returns it to the maintainer rather
than being worked around:

- an injected-failure test leaves any row behind (T-1);
- a concurrent or duplicate apply produces two durable effects (T-2);
- the real-export preview produces an identity discrepancy nobody can explain
  (T-3), or an Actor that is neither mapped, a create candidate, nor explicitly
  unresolved (T-4);
- the restored backup's inventory differs from the pre-drill inventory (T-9);
- any restricted-role mutation attempt succeeds (T-8);
- the real export does not satisfy the accepted contract — in which case the
  correct behaviour is refusal, and the contract change goes through §0.2
  change control (R-02's contingency);
- a blocking review finding in security, identity, atomicity, migration or
  recovery remains open at the gate.

---

## 11. Readiness assessment

Against `docs/project-management/README.md`, *management definition of ready*:

Reassessed 2026-08-02, after the plan acceptance and the four rulings.

| Criterion | R1–R3 | R4 |
|---|---|---|
| Outcome, included scope and exclusions written | **Met** — §§2–4 | **Met** — §5 |
| Predecessor gates approved | **Met** — Phase 1 accepted 2026-07-31 | **Met** |
| Blocking decisions and dependencies closed | **Met** — OD-41 and OD-42 closed; D-3 ruled; D-01a's register half is satisfied by the controlled migration register and manifest, and its implementation half is precisely what R1–R3 deliver and the gate verifies | **Met** for decisions |
| Named Product Owner, Technical Lead, implementer, reviewer | **Met** — §0.1 | **Met** |
| Decomposed small enough to estimate and review | **Met** — 3.0–4.0 likely days each | **Met** |
| Estimate assumptions, capacity, confidence, contingency recorded | **Met** — §§2.12, 3.11, 4.11, 9 | **Met** — §5.11 |
| Acceptance criteria objective and traced to tests or supervised checks | **Met** — §§2.6, 3.6, 4.6, 8 | **Met** — §5.6 |
| Development, disposable database and staging environments available | **Met** — `freedom_test` and `freedom_runtime_test` verified available | **Partly met** — no separate staging environment exists; the plan does not assume one and runs its drills on the disposable database |
| Material risks have owners, mitigations and triggers | **Met** — RAID R-01, R-02, R-05, R-09; §10 | **Met** |
| Operational windows and thresholds fixed | not applicable | **Not met** — §9.4 items 1–4 |

**Conclusion: R1–R3 meet the management definition of ready and are released to
start. R4 does not**, and cannot, until the four §9.4 values are set. Phase 2
itself remains not ready and its gate deferred; this plan's acceptance
authorizes remediation work, not the milestone.

---

## 12. Acceptance Authority decisions

All recorded by Peter Duscha on 2026-08-02. Durable record: change-log
clarifications C-1 and C-2.

| # | Decision | Outcome |
|---|---|---|
| **D-1** | Approve this replacement plan as the executable Phase 2 remediation plan under baseline v1.5 | **Accepted.** The superseded `phase-2-package-plan.md` stays non-executable |
| **D-2** | Rule OD-42 and close I-05 (§6) | **Ruled as recommended.** Display names are not unique identities; duplicates permitted; ambiguous legacy candidate lookup fails closed; **no unique constraint added**. I-05 closed |
| **D-3** | Disposition of `tools/import_sheet_characters.py` (§7.4) | **Revert to the committed state; record as dormant; disposition owned by package 5.1.** Lets T-6 be asserted cleanly without discarding accepted I-01 work |
| **D-4** | Timing of the §9.4 windows | **Required before R4, not before any work.** R1–R3 released to start; R4 `not ready` until all four values exist |
| **D-5** | Security-focused reviewer | **Codex, as a distinct and separately reported pass**, alongside its independent review. The implementer never reviews its own work |
| **D-6** | Approve change-log clarification C-1 | **Accepted** — the D-01 split, OD-42 registration, A-02/A-03 corrections and Independent Reviewer wording |

### 12.1 What remains outstanding

Only §9.4 items 1–4, and they block **R4 alone**. Everything else needed to
begin R1 is closed.

---

## 13. What this plan does not claim

- It does not claim the Phase 2 gate, or that Phase 2 is ready. Acceptance of
  this plan authorizes remediation work only.
- It does not claim any remediation has been implemented. As at 2026-08-02,
  none has.
- It does not claim any drill, migration, backup or role test has been run.
  None was, during planning.
- It does not claim the real exports were read. They were not.
- It does not close the mandatory §16.4 independent review, which applies to the
  remediated **implementation** and is still required.
- It does not authorize Phase 3.
