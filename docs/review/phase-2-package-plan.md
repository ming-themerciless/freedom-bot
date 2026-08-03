# Phase 2 package plan — I-02 Foundry snapshot milestone

Status: **Superseded 2026-08-02; remains non-executable under controlled
baseline v1.5.**
This is retained as the historical plan for the rejected ADR 0008
implementation. A replacement four-package remediation plan with named owners,
three-point estimates, environment readiness and operational rehearsal windows
is required by implementation plan §20 before work resumes.

**The replacement is
[`phase-2-v1.5-remediation-plan.md`](phase-2-v1.5-remediation-plan.md), drafted
2026-08-02 and awaiting independent review and Acceptance Authority approval.
Execute that plan, not this one.** Nothing below is authorized; this file exists
only so the superseded reasoning stays readable.

Starting point: commit `1695122` (accepted Sheet identity slice, I-01 closed),
with `9432ded` adding only the prompt document. The worktree was clean at the
start of this work; nothing that existed after `1695122` has been discarded.

## 1. What this milestone is, and what it is not

I-02 is the **incomplete Phase 2 Foundry snapshot milestone**. The accepted Sheet
identity slice is the existing part of package 2.4 and is *not* the Foundry
milestone. This plan does not close Phase 2, approve its gate, conduct the
supervised real-snapshot rehearsal, or begin Phase 3.

### Scope exclusions, stated explicitly

| Excluded | Why |
|---|---|
| Phase 3 web routes, templates, sessions, OAuth, CSRF | Plan §12 Phase 3; the prompt forbids scaffolding them here |
| A live HTTP Foundry connector, any Foundry write-back | Plan §12 Phase 7; ADR 0006 keeps one-way read-only |
| Foundry LevelDB access of any kind | `.agents/AGENTS.md`; ADR 0006 |
| Phase 5 command migrations (`/info`, `/xchange`, lifestyle, …) | Plan §12 Phase 5 packages, each with its own gate |
| The magic-item catalogue and `item_definitions` (§7.4) | Phase 5.6a; Phase 2 compares item identity, it does not import a catalogue |
| Deleting or altering `connectors/sheets.py` or live bot Sheet behaviour | Plan §1, §15; maintainer ruling |
| A general Google Sheets synchronisation framework | Plan §15 |
| The real-snapshot rehearsal against maintainer data | A separate maintainer-supervised gate check |
| Committing, pushing, or any git mutation | Prompt |

### Decisions this plan does **not** take by convenience

Anything touching data authority, correction semantics, privacy/retention,
authorization, schema identity or rollback strategy that is not already settled
by a maintainer ruling is raised in the handoff as an open decision, and the
affected field profile row is marked `UNRESOLVED` with apply disabled for it.
One such decision is raised by this work and is listed in §6.

## 2. Package breakdown, dependencies and evidence mapping

Effort is a three-point range (optimistic / likely / pessimistic) in focused
implementer-days for one implementer, excluding maintainer decision time, and
excluding the independent review and remediation allowance in §4. Confidence is
the implementer's confidence that the *likely* figure is not exceeded by more
than the pessimistic figure.

### 2.1 — Immutable artifact, parser, exporter contract, exhaustive field profile

**Depends on:** nothing beyond the accepted Phase 1 schema.

Delivers:

- ADR 0006 amended in place: the offline-snapshot rejection and the `"_id": null`
  premise are superseded, and the still-valid decisions (no LevelDB, no
  Manager-initiated live access, world-not-instance identity, exact version
  tuple, platform-owned stable IDs, no write-back) are preserved verbatim;
- a versioned, deterministic Council-side export bundle contract
  (`docs/rules/foundry-export-contract.md`), created through a supported Foundry
  UI/macro action, carrying exporter schema/version, world identity, core and
  system versions, export time, the folder graph needed to present a path, every
  Actor's real `_id` and folder ID, canonicalisation rules, and nothing else;
- bounded safe ingestion with SHA-256 computed **before** parsing, and refusal of
  oversized, deeply nested, archive, executable, path-bearing and unknown
  top-level input;
- a parser validating schema, world, core/system version, folder graph and Actor
  identity, rejecting ambiguous, missing and duplicate Actor/folder IDs;
- the exhaustive versioned field profile: every supported snapshot path has
  exactly one snapshot mode, every database-managed field exactly one correction
  mode, unknown paths are reported and never writable, and an unclassified new
  path fails closed;
- small synthetic fixtures shaped like the contract. No real Actor content.

**Evidence:** `tests/test_foundry_export_contract.py`,
`tests/test_snapshot_artifact.py`, `tests/test_snapshot_parser.py`,
`tests/test_field_profile.py`, and the table-driven classification test that
makes an unclassified field a test failure.

**Effort:** 2.0 / 3.0 / 4.5 days. **Confidence: medium-high.** The contract is
new but the shape is fully determined by discovery evidence.

### 2.2 — Preview, mapping, reconciliation, snapshot-only projections, idempotent import

**Depends on:** 2.1 (profile version and parsed snapshot are preview inputs).

Delivers dry-run preview writing no character or mapping state; explicit stable
external mappings established deliberately and never by name; a deterministic
reconciliation report; snapshot-only projections for later roll consumers, with
provenance and a typed refusal rather than a default; Foundry-out-of-date
warnings for database-owned mismatches; no implicit deletion, deactivation or
unmapping; atomic apply; idempotency keyed on checksum + folder + profile;
optimistic concurrency and stale-preview refusal.

**Evidence:** `tests/test_snapshot_preview.py`,
`tests/test_snapshot_reconciliation.py`, `tests/test_snapshot_import_service.py`,
`tests/test_snapshot_roll_inputs.py`, and the PostgreSQL integration tests in
`tests/test_snapshot_import_database.py`.

**Effort:** 3.0 / 4.5 / 7.0 days. **Confidence: medium.** Stale-binding and
concurrency semantics are where the residual risk sits.

### 2.3 — Correction, current-role authorization, append-only audit controls

**Depends on:** 2.1 (correction modes) and 2.2 (snapshot-sourced corrections).

Delivers framework-independent correction services for standard, protected and
compensating corrections; one current Council authorization, rechecked at apply
rather than only at preview; state, mappings, reconciliation effects,
transaction entries and success audit in one PostgreSQL transaction; audit
failure rolling back state; at most one safe attempted/refused event after
rollback under the same correlation ID; a new migration carrying the storage,
the append-only triggers and the runtime-role grants.

**Evidence:** `tests/test_corrections.py`, `tests/test_authorization.py`,
`tests/test_corrections_database.py`, `tests/test_runtime_grants.py` (extended),
and the PostgreSQL runtime-role denial tests.

**Effort:** 3.0 / 4.5 / 6.5 days. **Confidence: medium.** Carries the one open
schema-identity decision in §6.

### 2.4 — The narrow Sheet/manual bootstrap boundary

**Depends on:** 2.1 (only the finalized profile can say what is Sheet-era).

Delivers the decision and its documentation: what of the existing Phase 2 Sheet
importer survives the amended field profile, what is retained, what is
de-scoped, and why; a validated manual bootstrap path producing identical
database state and audit semantics; and proof that `connectors/sheets.py` and
the live bot's Sheet behaviour are untouched.

**Evidence:** `tests/test_sheet_bootstrap_boundary.py`, the existing
`tests/test_sheet_import_*.py` suites left green, and a diff review of
`connectors/`, `models/` and `ext/`.

**Effort:** 1.0 / 1.5 / 2.5 days. **Confidence: high.**

### 2.5 — Bootstrap mode, PostgreSQL evidence, documentation and handoff

**Depends on:** 2.2, 2.3, 2.4.

Delivers the one-time supervised bootstrap as an explicit operational mode;
PostgreSQL concurrency, runtime-role, failure and recovery evidence; the §13.3
traceability table; operations, rollback and retention documentation; and the
rewritten Phase 2 submission. Ends at the review handoff.

**Evidence:** `tests/test_bootstrap.py`, `tests/test_bootstrap_database.py`,
`docs/operations/foundry-snapshot-import.md`, and
`docs/review/phase-2-submission.md`.

**Effort:** 2.5 / 3.5 / 5.0 days. **Confidence: medium-high.**

### Totals

| | Optimistic | Likely | Pessimistic |
|---|---|---|---|
| Implementation (2.1–2.5) | 11.5 | 17.0 | 25.5 |
| Independent review and remediation allowance (§4) | 3.0 | 5.0 | 8.0 |
| **Total** | **14.5** | **22.0** | **33.5** |

The historical Phase 2 range of 8–15 working days is superseded for the
remaining work; plan §12 Phase 2 already records that it must be re-estimated.

## 3. Delivery order and review stops

Packages are implemented in the order 2.1 → 2.2 → 2.3 → 2.4 → 2.5. At the end of
each package: run its narrow tests, then inspect the diff, before continuing.
The full configured suite is run at the end of 2.5 and its exact commands and
results are reported in the submission.

## 4. Review and remediation allowance

Phase 2 is an import/reconciliation milestone, so plan §16.4 requires
independent Codex review. The allowance above covers one full review pass, the
remediation of blocking and important findings, and one re-review. Blocking
findings involving security, data integrity, authorization, migrations or
atomicity are fixed and re-reviewed before any dependent work starts.

## 5. Capacity and assumptions

- One focused implementer; no parallel packages.
- Maintainer decisions are not on the implementer's clock and are excluded.
- The disposable `freedom_test` PostgreSQL database on this host is available
  over the Unix-domain socket; no other database is touched.
- No real Council snapshot, `.env`, credential, live Sheet, live Foundry,
  Discord or production database is read at any point.

## 6. Open decision raised by this work

**OD-41 — the Phase 2 representation of database-managed current-state fields.**

Phase 2 must let one Council member correct *every* database-managed
current-state field, and must test that field by field. Those fields do not yet
have Phase 4/5 domain tables, and plan §7.3 explicitly says not to create every
future table in the first migration.

This work implements a **profile-driven current-state store**: one row per
(character, profile field key) for standard and protected fields, plus a
balance-and-append-only-transaction pair for compensating fields, with the
versioned field profile supplying the key set, the value type and the correction
mode. See [ADR 0008](../adr/0008-profile-driven-character-state.md).

That is a schema-identity decision. It is recorded, not assumed: the ADR is
**Proposed**, the handoff lists it as unmet pending maintainer acceptance, and
the alternative — modelling each field group as its own normalized table now,
ahead of the Phase 5 package that owns it — is stated there in full.
