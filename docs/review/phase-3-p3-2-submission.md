# Phase 3 · P3.2 submission — member reads, identity reconciliation, access administration

Package: P3.2 · Owner: Claude (working Technical Lead) · Date: 2026-08-17 ·
Branch: `docs/platform-plan` · Base commit: `3cd16a8` · P3.G2 accepted
2026-08-18 by change-log entry C-P3.2-D

This submission replaces the previous P3.2 submission entirely. That one
implemented a deferred-apply workflow and **raised**, rather than resolved, a
contradiction between four accepted contract passages about where the
`character_access` row is written. The maintainer has now resolved it. This
submission describes what the resolution required, what was removed, and what
was proved.

**Read §2 first.** It is the maintainer's decision and the controlled-contract
corrections that carry it. §5 is a blocking identity-integrity defect the
independent review reproduced, and its remediation.

**§10 is new (2026-08-17).** It is the remediation of the two findings from the
independent P3.2 *implementation* review — a blocking R-28 defect that reported
revoked links as active, and an important migration-0010 gap that let a decided
proposal carry no reason. Both are **submitted for independent re-review**; §10.6
records what each finding required, what changed, and the before/after evidence.

**Only the maintainer can accept P3.G2.** The independent implementation and
distinct security-focused reviews are recorded in §11; the maintainer accepted
the gate on 2026-08-18 through change-log entry C-P3.2-D.

---

## 1. Scope

### 1.1 Delivered

| # | Deliverable | Where |
|---|---|---|
| 1 | Framework-free My Characters and character-detail queries (R-20, R-21) | `application/web/characters.py`, `adapters/web/portal_routes.py` |
| 2 | Object-level authorization for linked characters and Council-wide reach | `CharacterAccessRepository.access_for`, `characters.py` |
| 3 | Council grant/revoke/default commands with reasons, optimistic versions, atomic audit, one-active-owner invariant | `application/web/character_access.py` |
| 4 | Administrator-only role-capability mapping commands (R-32–R-34, R-38) | `portal_routes.py`, `application/web/role_mappings.py` (P3.1) |
| 5 | **C-04**: `python -m tools.identity_migration --dry-run --player-tab Players` — the evidence run, and the only thing in Phase 3 that reads Google; `Players` is the maintainer-confirmed one-time input and remains explicit | `tools/identity_migration.py`, `adapters/sheets/identity_evidence.py`, `IdentityEvidenceRunService` |
| 6 | Council review and per-proposal decision (R-28–R-30), **where a confirmation creates the link** | `application/web/identity_evidence.py`, `adapters/web/templates/identity_migration.html` |
| 7 | Bounded search/selection of Discord identities without relying on display names | `IdentityCandidateRepository.search`, R-24 |
| 8 | The identity-linking boundary (R-35–R-37) | `application/web/account_identities.py` |
| 9 | Route/view-model implementations and minimal contract templates | `adapters/web/templates/*.html`, `application/web/view_models.py` |
| 10 | Migration revision **0010**, describing the approved final P3.2 schema, and its runtime grants | `migrations/versions/0010_identity_link_proposals.py`, `infra/postgresql/runtime-grants.sql.tmpl` |
| 11 | The mandatory request-boundary order (F3) | `portal_routes.py::_preamble` |
| 12 | Operator runbook for the temporary C-04 environment and its retirement | `docs/operations/identity-evidence-migration.md` |

### 1.2 Explicitly deferred, and not attempted here

- **P3.3's surface.** No snapshot-import, durable-job or audit-search route exists;
  `tests/web/test_structural_guards.py` asserts each is `404` in this build.
- **Stage D of M-1.** The legacy `character_access.discord_user_id` columns remain.
- **Game-state migration.** Only the identity-linkage evidence is migrated
  (delivery plan §4, migration contract §9).
- **P3.4's production frontend.** The templates here are the minimum needed to
  exercise the contracts.
- **Two active Discord identities per platform account** — deferred by the
  maintainer as **OD-47**; the current fail-closed behaviour is retained (§8, D5).
- **I-06 / A-05 / OD-17** carry forward unchanged; see §8.

---

## 2. The maintainer's decision, and the controlled corrections

### 2.1 The contradiction, and how it was resolved

Four accepted passages disagreed about where the Sheet-era `character_access` row
is written. §7.2 of the migration contract put it in a third pipeline step,
`C-05 --apply`; §7.5 of the same document, §5.1 of the route-authorization
contract and TC-MIG-09/11/13 of the test traceability all put it at the Council
confirmation. The previous delivery implemented §7.2 and asked for a ruling
rather than editing a controlled baseline to match its own code.

**Peter Duscha ruled on 2026-08-17 in favour of immediate activation**, recorded
through the repository's change process:

| Record | Where |
|---|---|
| Change-log entry **C-P3.2-A** — full impact assessment, added/removed scope, risks, testing and operational effect, and the dated approval | `docs/project-management/change-log.md` |
| Decision **OD-46** — the authoritative ruling text | `docs/discovery/open-decisions.md` |
| Decision **OD-47** — the deferred multiple-identity question | `docs/discovery/open-decisions.md` |
| Management index rows for both | `docs/project-management/decision-register.md` |

### 2.2 The authoritative workflow

```text
C-04 --dry-run --player-tab             R-28 / R-29 / R-30
read legacy Sheet evidence         ->   review one proposal at a time
write proposals only                    confirm: create link + audits atomically
write no character_access               reject: decision + audit, no link
```

| Stage | Command / route | Writes | Never |
|---|---|---|---|
| C-04 | `--dry-run --player-tab Players` | `identity_migration_runs`, `identity_link_proposals`, `identity_link_proposal_candidates` | a `character_access` row; any Google write |
| R-29 | confirm one proposal | the `character_access` row through `CharacterAccessService.grant()`, the character's version bump, the proposal's `confirmed` transition naming that access row, `character_access.granted` and `identity_migration.confirmed` — **one transaction** | a resolution of any kind; anything the request body names |
| R-30 | reject one proposal | `decided_at`, `decided_by_account_id`, `decision_reason`, `identity_migration.rejected` | a link, under any circumstances |

**C-05 is withdrawn.** Its identifier is retired rather than reused, so a
reference to it in an older document reads as withdrawn.

### 2.3 Every controlled passage corrected, consistently

Corrected together rather than one at a time — editing a single contract to make
the contradiction less visible was the failure mode the previous submission
refused to commit:

| Document | Change |
|---|---|
| `phase-3-identity-migration-contract.md` | Amendment note at the head; **§7.2** rewritten as the two-stage pipeline with immediate activation and the Google-as-legacy-input statement; **§7.3.1 added** — the duplicate-player-name refusal, with the rejected alternative recorded; **§7.4** states that `confirmed` counts active links; **§7.5** restates idempotency, atomicity and the concurrency guarantee; **§7.7 added** — Google is temporary, lives outside the platform runtime, and is retired after the verification window; **§7.7.5** names `Players` and, per `C-P3.2-B`, gives the *current* reason the argument stays required — a default would make one-time migration input enduring runtime configuration and remove the wrong-tab guard — rather than the pre-`C-P3.2-B` reason that the name was unverified; traceability rows added for TC-MIG-17/18 |
| `phase-3-route-authorization-contract.md` | §5.1 R-28–R-30 gains the **R-29 activates immediately** paragraph — live capability resolution, atomicity, the fixed `co_owner` access kind, the refusals — and an explicit "R-30 remains a rejection only"; §8 command register: C-04's row names the required `--player-tab`, and **C-05 is recorded as withdrawn** |
| `phase-3-test-traceability.md` | TC-MIG-09, TC-MIG-11 and TC-MIG-13 sharpened to the ruled workflow; **TC-MIG-17** (duplicate player names) and **TC-MIG-18** (no Google in the platform runtime) added, with summary rows |
| `phase-3-view-model-contract.md` | VM-10 gains `character_version`, `resulting_access_kind`, `candidate_subjects_truncated`, `candidate_count`, `decided` and `outstanding`; `applied_at`, apply outcomes and apply totals removed; the **four states and no fifth** rule stated |
| `phase-3-logical-schema.md` | §11 rows corrected: `character_access` is written by the Council service R-25 and R-29 share, and `identity_link_proposals` names both its writers and its `RESTRICT` grant key |
| `phase-3-configuration-and-dependency-contract.md` | §1.2 records the deliberate absence of any Google client library and points at the operator runbook |

---

## 3. Implementation remediation

### 3.1 R-29 activates immediately

`IdentityMigrationService.confirm()` now, in the route's one transaction:

1. authenticates and resolves Council capability **server-side for this
   request** (`enter_mutation` → `WebAuthorizationContext` → `require_council()`
   in the service as well, because a service that trusts its caller to have
   checked is a service with one caller that forgot);
2. enforces CSRF, origin, host and body bounds — the P3.2 matrix row for R-29 is
   unchanged and `test_p3_2_request_boundary.py` still asserts the mandatory
   order;
3. takes one proposal id and a required bounded reason;
4. loads the proposal server-side and confirms only when its evidence resolved to
   exactly one Discord subject;
5. refuses ambiguous, unresolved, missing, stale and already-decided proposals;
6. creates the link through **`CharacterAccessService.grant()`** — the same
   *object* R-25 uses, not a second construction of the class (composition builds
   it once and passes it to both);
7. attributes the grant to the confirming member's live context; and
8. persists the confirmation, the access row, the character version change, the
   grant audit and the migration-confirmation audit together, rolling all of them
   back if any fails.

Three independent controls make a retry, a double submit and two concurrent
confirmations produce one durable authorization: the conditional version bump
inside `grant()`, `uq_character_access_one_active_link_account`, and `decide()`'s
conditional update on the proposal still being outstanding.

Optimistic concurrency is preserved where the accepted contracts require it: the
confirm form carries the character's `version`, exactly as R-25's grant form
does, because a confirmation now changes the character.

### 3.2 The deferred-apply architecture is removed

Not disabled, not left unused — removed, and its absence is asserted
(`test_no_apply_surface_survives_anywhere_in_the_command`):

| Removed | Was |
|---|---|
| `IdentityMigrationApplyService`, `ApplyOutcome`, `ApplyRefused`, `ProposalOutcome`, `APPLY_*` | the apply service and its vocabulary |
| `RecordedCouncilDecision`, `NotAConfirmedDecision`, the `LinkAuthority` protocol | a second grant authority, constructible from a database row, existing only because C-05 had no session. `grant()` now takes `WebAuthorizationContext` |
| `--apply`, `--run-id`, `execute_apply`, `run_apply_command`, `render_apply` | the command surface and its report |
| `lock_run`, `newer_run_exists`, `persisted_proposal_count`, `undecided_confirmable_count`, `confirmed_unapplied`, `apply_counts`, `mark_applied`, `mark_run_applied` | the repository's apply methods, run locks and superseded-run rules |
| `identity_migration_runs.applied_at`, `.apply_correlation_id`, `ck_..._apply_state` | run apply state |
| `identity_link_proposals.applied_at`, `.apply_outcome`, and four constraints (`only_a_confirmation_applies`, `apply_state`, `apply_outcome_value`, `only_an_applied_confirmation_grants`) | proposal apply state |
| `MigrationRun.applied_at`, `MigrationTotals.granted`/`.adopted`, `LinkProposal.applied`/`.apply_outcome`, `ApplyOutcomeCode` | VM-10's apply fields |
| `confirmed-not-applied`, `applied-granted`, `applied-already-linked`, run applied/not-applied notices, the apply-totals list | template states |

**What was preserved**, because it remains necessary: durable decision fields
(`decided_at`, `decided_by_account_id`, `decision_reason`), candidate evidence
and its child table, provenance, correlation ids, and `granted_access_id` — which
is now what records *which* access row a confirmation created.

Migration 0010 is uncommitted in this worktree and is **rewritten** to describe
the approved final schema. **No applied migration (0001–0009) is edited.**
`adapters/database/tables.py` is kept exactly aligned, and three parity cases
assert it by column, by constraint name and by constraint expression.

The four apply constraints are replaced by **one**:

```sql
CHECK ((granted_access_id IS NOT NULL) = (resolution = 'confirmed'))
  -- ck_identity_link_proposals_a_confirmation_is_a_link
```

It says the whole pipeline. A `proposed`, `ambiguous`, `unresolved` or `rejected`
row carrying a grant is refused — so "C-04 authorized something" and "a rejection
created a link" are not storable states — and a `confirmed` row naming no access
row is refused too, so the withdrawn deferred-apply workflow is
*unrepresentable* in this schema rather than merely unimplemented. Both halves
are asserted as the restricted runtime role.

### 3.3 C-04 is narrow and temporary

- reads through the read-only Google boundary, only `Characters C` and the player
  tab's `A`/`B`/`D`; no game-state column;
- creates balanced run, proposal and candidate evidence in PostgreSQL;
- creates **no** `character_access` row and no authorization — and cannot:
  `IdentityEvidenceRunService` holds no access service, no access repository and
  no audit repository, which is asserted over the object's slots, and the schema
  refuses a grant on every row it can write;
- performs no Google write — the reader has one method and the AST allowlist over
  `read_only.py` admits `spreadsheets`, `values`, `get`, `execute` and nothing
  else;
- reports bounded control totals and identifiers with no personal data;
- fails safely on bad dependencies, credentials, layout, mappings or source data,
  with a stable exit code per class.

**`--player-tab` is required.** The previous delivery defaulted it to
`"Players"` before that name had been verified, so the constant was deleted from
the adapter rather than retained as operational truth. Peter Duscha subsequently
confirmed on 2026-08-17 that the one-time C-04 source tab is in fact **`Players`**
(`C-P3.2-B`). It remains a required argument: the confirmation supplies an
operator input and does not turn Google or the tab name into portal configuration.

**Google stays out of the platform runtime.** `requirements-web.txt` and
`requirements-web.lock` name no Google package (both are byte-identical to the
pre-P3.2 baseline; `git status` reports neither as modified).
`docs/operations/identity-evidence-migration.md` documents the separate temporary
operator environment, the read-only credential, the verification step and the
retirement — revoke, delete, unset, destroy — and states plainly that **C-04
cannot be run from `venv-web`, by design.**

### 3.4 R-28 and VM-10

R-28 shows the states that exist: outstanding proposed evidence,
ambiguous/unresolved evidence, confirmed links that are **active now**, and
rejected proposals. `confirmed but not applied`, apply outcomes, apply totals and
run apply status are gone.

The confirm form states what it is about to do before doing it — the character,
the proposed stable Discord identity (a snowflake; the names beside it carry the
standing "names are evidence" notice), the resulting access kind `co_owner`, the
character version, and the required reason. The access kind is the server's and
the form carries no field for it. **No bulk-confirm control was added.**

---

## 4. Simplification recorded, not smuggled

Beyond the removals §3.2 lists, one boundary was simplified: `grant()` took a
`LinkAuthority` protocol with two implementations, and now takes
`WebAuthorizationContext`. All four callers (R-25, R-26, R-27, R-29) are request
handlers holding a live resolution. An authority type with one implementation is
indirection; one constructible from a database row is a second way for an
authorization to be attributed. `WebAuthorizationContext.audit_source` is kept
and its docstring corrected — the service reads it rather than hard-coding
`WEB`, so origin stays a property of who is acting.

---

## 5. The blocking duplicate-player-name defect

### 5.1 What it was

`application/web/identity_evidence.py` built the player join as a dict
comprehension keyed by the normalized player name:

```python
players = {
    DisplayName(player.player_name).identity_key: player
    for player in player_rows
    if player.player_name.strip()
}
```

Two Sheet rows called `Ada` and `ADA` are one key. The later row silently
overwrote the earlier one, so **the order of rows in a spreadsheet decided which
Discord identity every character naming that player would be proposed for** — and
a Council member confirming that proposal would have created a real
authorization for whichever person the layout happened to favour.
`adapters/sheets/identity_evidence.py` supplied no upstream uniqueness guarantee.

### 5.2 How it fails closed

Not a product decision, and not resolvable by choosing a row. Migration contract
**§7.3.1** now requires the **whole C-04 run to be refused** when two player-tab
rows share one normalized key. `resolve()` builds the index through
`_index_players`, which collects collisions and raises `DuplicatePlayerNames`
**before any character row is examined** and before anything is written.

Why refuse the run rather than persist the affected characters as non-confirmable
evidence — the other option the maintainer allowed:

- the refusal happens before the run row exists, so there is no partial run and
  no control total for a duplicate to hide inside;
- per-character treatment would report a *source-integrity* defect as an ordinary
  `ambiguous` row, inside a §7.4 balance computed over a player set the run had
  already decided was self-consistent;
- it is order-independent by construction — it depends on the *set* of keys.

The uniqueness rule lives with the resolver, not in the Sheets adapter, because
it is the same `domain/names.py` normalization the resolution rules use and §7.3
forbids a second implementation of "are these the same name?". The adapter's
docstring says so where a reader would look for the check.

The refusal message carries **counts only** — colliding keys and rows involved.
The remedy is operational and belongs to whoever owns the spreadsheet: resolve
the duplicate there and re-run. Nothing in this workflow writes to Google.

### 5.3 Evidence (TC-MIG-17)

| Property required | Case |
|---|---|
| Exact and normalized duplicates with different Discord names produce no confirmable proposal | `test_a_duplicate_player_name_refuses_the_run_in_either_row_order` (3 pairs), `test_duplicate_player_names_refuse_the_run_whatever_the_row_order` (command level, 2 pairs) |
| Row order cannot change the outcome | both cases above are parametrized over **both orders**; the assertion is that the two orders agree, because disagreement *was* the defect |
| Duplicates cannot be hidden by the control totals | `test_a_duplicate_is_not_reported_as_an_ordinary_ambiguity` — not even the unambiguous character in the same run gets a proposal, and no run row exists |
| The command-level transaction writes no partial run on a refusal | same case, plus `test_duplicate_player_names_refuse_the_run_whatever_the_row_order`: zero runs, zero proposals, zero candidates, zero access rows, zero audit events |
| Safe output reveals neither player names nor Discord identities | `test_the_refusal_names_counts_and_no_personal_data` (resolver) and `test_the_duplicate_refusal_names_no_player_and_no_discord_identity` (command, over stdout **and** stderr) |
| Every colliding key is counted, not only the first | `test_the_refusal_counts_every_colliding_key_not_only_the_first` |
| The refusal does not depend on a character naming the duplicate | `test_the_refusal_is_raised_before_any_character_is_examined` |
| The guard is narrow — a working spreadsheet is not refused | `test_distinct_player_names_are_not_a_duplicate`, `test_blank_player_names_are_not_keys_and_cannot_collide` |

Recorded limit, stated rather than discovered: `DisplayName.identity_key`
normalizes and case-folds but does **not** trim, so `"Ada"` and `" Ada "` are two
keys. The duplicate check uses that one shared policy rather than a second,
slightly different comparison. It does not reach production — the Sheets adapter
strips every cell it reads, on both sides of the join — and the test module says
so where the case list would otherwise look incomplete.

---

## 6. Verification evidence

Every numbered requirement of the handover's minimum evidence list, and where it
is proved.

| # | Required | Case |
|---|---|---|
| 1 | C-04 balances every source row, writes proposals/candidates, no access | `test_c04_writes_balanced_evidence_and_not_one_access_row`; the constraint with the application bypassed in `test_the_database_refuses_an_unbalanced_run_with_the_application_bypassed`; the structural half in `test_the_evidence_run_service_can_reach_no_grant_at_all` and `test_the_database_refuses_a_grant_on_anything_but_a_confirmation` |
| 2 | C-04 reads through a read-only boundary and never writes the Sheet | `test_the_sheet_boundary_offers_no_write_at_all` — reader capability, AST allowlist over `read_only.py`, Google-import allowlist over the other three modules, and the `spreadsheets.readonly` scope |
| 3 | Ambiguous, unresolved, duplicate-player and unmapped evidence fails closed | `test_an_undecidable_proposal_cannot_be_confirmed_by_the_service` (×2), `test_an_undecidable_proposal_grants_no_access_even_when_submitted` (×2, direct HTTP), §5.3's eight duplicate cases, `test_a_source_row_with_no_stable_character_mapping_refuses_the_whole_run`, `test_the_service_refuses_unmapped_rows_before_writing_anything` |
| 4 | R-29 creates one link and its audits atomically through `CharacterAccessService` with the live confirming context | `test_r29_creates_the_link_its_audits_and_the_decision_atomically`; the wiring in `test_r29_grants_through_the_one_shared_service`, which asserts over the composition source that **one** `CharacterAccessService` is constructed and shared |
| 5 | Audit, proposal-transition, grant and commit failures produce nothing partial | `test_an_injected_audit_failure_rolls_the_whole_confirmation_back` (×2, both events), `test_a_failed_proposal_transition_rolls_the_grant_back_with_it`, `test_an_injected_grant_failure_leaves_no_decision_and_no_version_bump`, `test_a_commit_failure_leaves_no_partial_confirmation` |
| 6 | Direct HTTP cannot confirm ambiguous/unresolved proposals or substitute a subject, account, actor, access kind or authority | `test_an_undecidable_proposal_grants_no_access_even_when_submitted`, `test_a_confirmation_cannot_substitute_any_authorization_bearing_value` — six substitution fields submitted, all ignored |
| 7 | Repeated and concurrent confirmations produce one durable effect | `test_a_second_confirmation_of_one_proposal_changes_nothing_twice`, `test_two_concurrent_confirmations_produce_one_durable_effect` (two real connections on a barrier) |
| 8 | Stale proposal/character state is refused safely | `test_a_stale_character_version_refuses_before_writing_anything`, `test_a_link_created_between_the_run_and_the_confirmation_is_refused`, `test_a_missing_proposal_is_a_404_shaped_refusal`, `test_a_proposal_whose_subject_has_no_account_is_unreachable` |
| 9 | R-30 rejects once, audits atomically, creates no link | `test_r30_rejects_an_outstanding_proposal_and_creates_no_link`; the schema half in `test_the_runtime_role_cannot_give_an_unconfirmed_proposal_a_grant` |
| 10 | Ordinary members, revoked members, non-members and stale-role sessions cannot reach either Council mutation | `test_p3_2_matrix.py` (81 passed), `test_p3_2_capability_resolution.py` (26), `test_p3_2_emergency_boundary.py` (34) |
| 11 | Runtime-role database constraints prevent bypasses | `test_p3_2_runtime_grants_and_bounds.py` (28), including both halves of `a_confirmation_is_a_link` as the restricted role |
| 12 | C-04 adds no Google dependency to the portal runtime | `test_the_portal_runtime_needs_no_google_package` (**TC-MIG-18**) — requirement/lock files, plus a **subprocess** import probe on a clean interpreter asserting the portal drags in no `google*` module |
| 13 | Migration/metadata parity and upgrade/downgrade/upgrade | `test_migration_0010_round_trip.py` (7): declared inventory at head, full round trip compared constraint-for-constraint and index-for-index, the downgrade's data cost, no third JSONB column, and three parity cases (columns/nullability, constraint names, constraint expressions) |
| 14 | The guarded backup/restore/rerun evidence still passes, guard unweakened | `test_identity_migration_backup_restore.py` (2) — dump → C-04 → drop schema → restore → C-04 again against `freedom_test`; the Unix-socket and disposable-name guards are asserted before it dumps and are **unchanged** |
| 15 | **R-28 never calls a revoked confirmation active** (TC-MIG-19, §10) | `test_r28_never_calls_a_revoked_confirmation_active`, `test_another_active_link_cannot_make_a_revoked_confirmation_look_active`, `test_a_rejected_proposal_carries_no_link_state_at_all`; the retained active case in `test_r28_renders_outstanding_confirmed_and_rejected_states` |
| 16 | **A decided proposal cannot lack its reason, under the restricted runtime role** (TC-MIG-20, §10) | `test_the_runtime_role_cannot_confirm_a_proposal_with_no_reason`, `…cannot_reject_a_proposal_with_no_reason`, `…cannot_decide_with_a_blank_reason`, `test_an_outstanding_proposal_cannot_carry_a_decision_reason`, `test_valid_r29_and_r30_transitions_still_pass_every_constraint` |

### 6.1 Commands run, with exact results

All against the guarded disposable database `freedom_test`
(`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`), **serially**. The
portal and bot suites share the one disposable database and one suite's
session-scoped fixture migrates it from `base` while the other is using it;
overlapping them fabricates dozens of failures. Every count below is from a run
with nothing else touching the database.

| # | Command | Result |
|---|---|---|
| 1 | `./venv-web/bin/python -m pytest tests/web/test_identity_migration_command.py` | **51 passed** |
| 2 | `… tests/web/test_identity_evidence_resolver.py` | **38 passed** |
| 3 | `… tests/web/test_p3_2_matrix.py` | **81 passed, 54 skipped** |
| 4 | `… tests/web/test_character_access_invariants.py` | **13 passed** |
| 5 | `… tests/web/test_migration_0010_round_trip.py` | **7 passed** |
| 6 | `… tests/web/test_identity_migration_backup_restore.py` | **2 passed** |
| 7 | `… tests/web/test_p3_2_request_boundary.py` | **19 passed** |
| 8 | `… tests/web/test_p3_2_success_cells.py` | **48 passed** |
| 9 | `… tests/web/test_p3_2_emergency_boundary.py` | **34 passed** |
| 10 | `… tests/web/test_p3_2_identity_invariants.py` | **15 passed** |
| 11 | `… tests/web/test_p3_2_capability_resolution.py` | **26 passed** |
| 12 | `… tests/web/test_p3_2_runtime_grants_and_bounds.py` | **28 passed** |
| 13 | `… tests/web/test_structural_guards.py` | **47 passed** |
| 14 | `./venv-web/bin/python -m pytest tests/web` (complete portal suite) | **1080 passed, 54 skipped, 0 failed** |
| 15 | `./venv/bin/python -m pytest tests --ignore=tests/web` (complete bot suite, disposable database configured) | **2272 passed, 0 failed** |
| 16 | `./venv-web/bin/python -m compileall -q application adapters tools tests/web migrations/versions helpers` | exit 0 |
| 17 | `git diff --check` | exit 0 |
| 18 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | 14 files, all OK |
| 19 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest -q tests/web/test_identity_migration_command.py tests/web/test_structural_guards.py tests/web/test_p3_2_runtime_grants_and_bounds.py` (after `C-P3.2-B` documentation reconciliation) | **126 passed, 21 deprecation warnings, 0 skipped, 0 failed** |

#### 6.1.1 The `C-P3.2-B` rationale reconciliation, re-verified

The pass recorded in §7 corrected four rationales that still argued from a fact
`C-P3.2-B` had superseded, and normalised two quoted invocations. Every check
below was re-run afterwards, serially, with nothing else touching `freedom_test`.
`$DB` is `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`.

| # | Command | Result |
|---|---|---|
| 20 | `$DB ./venv-web/bin/python -m pytest -q tests/web/test_identity_migration_command.py tests/web/test_identity_evidence_resolver.py` | **89 passed**, 7 warnings, 0 skipped, 0 failed (3.53s) |
| 21 | `$DB ./venv-web/bin/python -m pytest -q tests/web/test_character_access_invariants.py tests/web/test_migration_0010_round_trip.py tests/web/test_identity_migration_backup_restore.py tests/web/test_structural_guards.py tests/web/test_p3_2_runtime_grants_and_bounds.py` | **97 passed**, 14 warnings, 0 skipped, 0 failed (6.56s) |
| 22 | `$DB ./venv-web/bin/python -m pytest -q tests/web` (complete portal suite) | **1080 passed, 54 skipped**, 280 warnings, 0 failed (48.68s) |
| 23 | `$DB ./venv/bin/python -m pytest -q tests --ignore=tests/web` (complete bot suite) | **2272 passed**, 1 warning, 0 failed (2m14s) |
| 24 | `./venv-web/bin/python -m compileall -q application adapters tools tests/web migrations/versions helpers` | exit 0 |
| 25 | `git diff --check` | exit 0 |
| 26 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | 14 files, all OK |
| 27 | `grep -h '^revision\|^down_revision' migrations/versions/*.py` | chain `0001 → … → 0010` unbroken; `0010` still descends from `0009` |

Runs 22 and 23 reproduce runs 14 and 15 exactly, which is the expected result:
this pass changed comments, docstrings and prose only, and no test asserts over
the text it changed. Migration/metadata parity is inside run 21
(`test_migration_0010_round_trip.py`, 7 cases: declared inventory at head, the
`upgrade → downgrade → upgrade` round trip compared constraint-for-constraint and
index-for-index, the absence of `applied_at`/`apply_outcome`/`apply_correlation_id`,
and the three parity cases over columns, nullability, constraint names and
constraint expressions).

**Still not run, and still unavailable.** No formatter, linter or type checker is
configured in this repository — re-confirmed in this pass: there is no
`pyproject.toml`, `setup.cfg`, `.flake8`, `ruff.toml`, `mypy.ini`, `tox.ini` or
pre-commit configuration, and `requirements-dev.txt` / `requirements-web-dev.txt`
contain only `pytest`, `pytest-asyncio` and `beautifulsoup4`. The 500-actor
benchmark was not re-run. **C-04 has not been run against the live spreadsheet**,
and this pass does not authorize one: the tab name is confirmed, the separate
operator environment is not provisioned, and no live Google, Discord, Foundry or
production PostgreSQL access was made.

**The 54 skips are all one case** —
`test_p3_2_matrix.py::test_every_route_answers_the_documented_status_for_every_caller_state`
skipping its permitted cells, which `test_p3_2_success_cells.py` asserts instead.
No database test is skipped: `freedom_test` was available for every run.

Migration consistency: the revision chain `0001 → … → 0010` is unbroken
(`down_revision` inspected across `migrations/versions/`), and
`tests/test_migration_safety.py` passes inside run 15.

**Checks not run, and why.** No formatter, linter or type checker is configured
in this repository — there is no `pyproject.toml`, `setup.cfg`, `.flake8`,
`ruff.toml`, `mypy.ini`, `tox.ini` or pre-commit configuration, and
`requirements-dev.txt` / `requirements-web-dev.txt` contain only `pytest`,
`pytest-asyncio` and `beautifulsoup4`. None was run, because none was available
to run. Adding one is a focused change this package did not make. The full
500-actor benchmark (`tests/benchmark_snapshot_500.py`) was not re-run; it is
exercised through `tests/test_benchmark_harness.py`, which passes inside run 15.
C-04 has **not** been run against the live spreadsheet. The maintainer has now
confirmed the one-time player-tab input as `Players`; the remaining prerequisite
is provisioning the separate temporary operator environment and following the
runbook. This submission does not authorize a live run.

**Nothing was deployed, committed or pushed. No live service or data was mutated.
Google Sheets was never contacted** — every test supplies canned raw values
through the reader port. No production Discord, Foundry or PostgreSQL instance
was touched.

---

## 7. Worktree and diff account

Uncommitted on `docs/platform-plan` at base `3cd16a8`. **27 modified files, 38
untracked.**

| File | Change in this remediation |
|---|---|
| `application/web/identity_evidence.py` | Rewritten: two-stage docstring; `_index_players` and `DuplicatePlayerNames`; `IdentityMigrationApplyService` and its types removed; `confirm()` creates the link; `AlreadyLinked` added; `overview()`/`_proposal_view` lose apply state and gain `character_version` and `resulting_access_kind`; the invocation quoted in `IdentityEvidenceRunService`'s docstring names `Players` rather than a `NAME` placeholder |
| `application/web/character_access.py` | `LinkAuthority`, `RecordedCouncilDecision` and `NotAConfirmedDecision` removed; `grant()` takes `WebAuthorizationContext`; module docstring records why |
| `application/web/view_models.py` | VM-10: `ApplyOutcomeCode` → `ConfirmedAccessKind`; `character_version` and `resulting_access_kind` added; `applied`, `apply_outcome`, `MigrationRun.applied_at`, `granted`, `adopted` removed |
| `application/web/capabilities.py` | `audit_source` docstring corrected (no `LinkAuthority`, no C-05) |
| `adapters/web/portal_routes.py` | R-29 parses `version`, calls `confirm(expected_version=…)`; docstring describes the atomic activation and the absent substitution parameters |
| `adapters/web/composition.py` | `access_service=character_access` passed to `IdentityMigrationService` — the same object R-25 gets; comments corrected |
| `adapters/web/repositories.py` | `decide()` takes `granted_access_id`; the eight C-05 methods removed; class docstring corrected |
| `adapters/web/templates/identity_migration.html` | Three proposal states; the confirm summary (character, subject, access kind, version); hidden `version`; apply notices and totals removed; still no bulk control |
| `migrations/versions/0010_identity_link_proposals.py` | Rewritten to the approved final schema: five apply columns and five constraints removed, replaced by `a_confirmation_is_a_link`; docstring records the removal and why the columns are dropped rather than left nullable, and its lifecycle table quotes the invocation with `--player-tab Players` |
| `adapters/database/tables.py` | Kept exactly aligned with 0010 |
| `adapters/sheets/identity_evidence.py` | `PLAYER_TAB` deleted; docstring records where the uniqueness rule lives and why it is not here; the `PLAYER_RANGE` comment now gives the `C-P3.2-B` reason for the absent constant (one-time migration input must not become enduring command configuration) instead of asserting the tab name is unrecorded |
| `tools/identity_migration.py` | C-05 removed entirely; `--player-tab` required; `DuplicatePlayerNames` translated; report points at the Council confirmation rather than a second command |
| `.env.example` | The read-only credential is documented as C-04's too, with the temporary-migration framing and a pointer to the runbook |
| `docs/operations/identity-evidence-migration.md` | **New.** The operator runbook: separate environment, credentials, invocation, exit codes, the three refusals, verify-then-retire, and what the command never does |
| `docs/discovery/sheet-inventory.md`, `docs/review/phase-3-p3-4-gemini-readiness-report.md` | `C-P3.2-B`: record `Players` as the confirmed one-time input and remove the stale active C-05 command inventory |
| `docs/contracts/*`, `docs/discovery/open-decisions.md`, `docs/project-management/*` | §2.3's controlled corrections and the change record |
| `tests/web/test_identity_migration_command.py` | Rewritten (51 cases) around `C-04 → R-28 → R-29/R-30`; the `PLAYER_TAB`, `C04_ARGV` and command-line-case rationales corrected to `C-P3.2-B`. The fixture tab stays deliberately **not** `Players` — driving the command with a different name is what proves it reads the operator's argument and not a name the code remembers |
| `tests/web/test_identity_evidence_resolver.py` | Eight duplicate-player cases (TC-MIG-17) and the docstring that names the defect |
| `tests/web/test_migration_0010_round_trip.py` | Inventory, parity and downgrade fixture updated to the final schema; asserts the apply columns are **absent** |
| `tests/web/test_p3_2_runtime_grants_and_bounds.py` | Fixture updated; both halves of `a_confirmation_is_a_link` asserted as the restricted role, in separate transactions |
| `tests/web/test_identity_migration_backup_restore.py` | Helper docstring corrected |

**The `C-P3.2-B` rationale reconciliation.** The documentation pass that recorded
`Players` updated the facts but left four *reasons* arguing from the fact it had
just superseded — that the tab name was unrecorded and any name in the code would
be an unverified guess. That is now false in the direction that matters: the Sheet
inventory §2.1 records `Players`, and `C-P3.2-B` gives the standing reason the
argument remains required, which is that a default would turn one-time migration
input into enduring runtime configuration and remove the explicit wrong-tab guard.
Corrected in `phase-3-identity-migration-contract.md` §7.7.5,
`adapters/sheets/identity_evidence.py`, and three places in
`tests/web/test_identity_migration_command.py`; two quoted invocations that still
read `--player-tab NAME` now read `--player-tab Players`, matching the command
register and the runbook. **No behaviour, schema, route, constraint, argument
requirement or test assertion changed**, the runbook §3 already carried the correct
reason and is untouched, and the file counts above are unchanged (27 modified, 38
untracked).

**The independent-review remediation (§10), on top of the above.** The same 27
modified and 38 untracked files — no file added or removed.

| File | Change in the finding-1/finding-2 remediation |
|---|---|
| `adapters/web/repositories.py` | `IdentityProposalRepository.granted_link_state()` and `.confirmed_link_counts()` added — the exact `granted_access_id` joined to `character_access.active`, one bounded query each; `decision_counts()` docstring says it is the historical decision and nothing else |
| `application/web/identity_evidence.py` | `overview()` reads both new queries and sets `confirmed` from the **active** count; `_proposal_view()` takes the page's link states and sets `link_state` keyed on the proposal; the docstrings state why activation is not inferred from the character or the account |
| `application/web/view_models.py` | `LinkProposal.link_state`; `MigrationTotals.confirmed_revoked`; `balances()`'s second equation gains the term |
| `adapters/web/templates/identity_migration.html` | The `confirmed-and-revoked` state and its `data-link-state`; the `confirmed_revoked` total; `confirmed` relabelled *link active now*; the header rationale records C-P3.2-C |
| `migrations/versions/0010_identity_link_proposals.py`, `adapters/database/tables.py` | `ck_identity_link_proposals_a_decision_states_its_reason`, identical name and expression in both; docstring records the runtime-role gap it closes |
| `tests/web/test_identity_migration_command.py` | Three new cases (TC-MIG-19) and an R-26 `revoke()` helper that goes through `CharacterAccessService` |
| `tests/web/test_p3_2_runtime_grants_and_bounds.py` | Five new cases (TC-MIG-20) and a `decidable` fixture; each violation in its own transaction |
| `tests/web/test_migration_0010_round_trip.py` | The new constraint added to the declared inventory |
| `docs/contracts/*`, `docs/project-management/change-log.md`, `docs/project-management/decision-register.md` | §10.3's controlled corrections and C-P3.2-C |

**No unrelated change.** No applied migration is edited. No disposable-database
guard is weakened. No runtime grant is weakened, narrowed or widened. No real player, Sheet, Discord, Foundry or production data
appears anywhere: every snowflake used is outside the range Discord has issued
and every name is invented.

---

## 8. Deviations, decisions and residual risks

| # | Item | Status |
|---|---|---|
| D1 | **VM-10 additions.** `LinkProposal` gains `character_version`, `resulting_access_kind`, `candidate_subjects_truncated` and `candidate_count`; `MigrationTotals` gains `outstanding`. `candidate_subjects` keeps its documented maximum of ten and `balances()` keeps §7.4's two equations. Recorded in the corrected VM-10 text | Recorded deviation, now in the contract |
| D2 | **Unmapped source rows refuse the run** rather than being counted or dropped. No contract sentence covers the case; the choice follows plan §0.5 | Recorded |
| D3 | **`already_linked` is keyed on the (character, subject) pair**, per §7.3's *"for that account"*, so a second authorized user for a character is still proposed | Recorded |
| D4 | **`col_to_index` moved** from `helpers/utils.py` to `adapters/sheets/columns.py`, with a re-export, so `helpers` does not import from `adapters` | Recorded |
| D5 | **No constraint forbids two active identities per provider per account.** Deferred by the maintainer as **OD-47**; the current fail-closed behaviour (`503`, never a tiebreak) is retained | Deferred by decision |
| D6 | **`identity_key` does not trim.** §5.3's recorded limit; the adapter strips both sides, so it cannot reach production | Recorded |
| D7 | **VM-10 gains `LinkProposal.link_state` and `MigrationTotals.confirmed_revoked`**, and §7.4's second balance gains a term. Required to close finding 1 without either lying about a revoked link or losing it from the arithmetic. Ruled by the maintainer on 2026-08-17 and recorded as change-log entry **C-P3.2-C**; the contracts are corrected, not only the code. The `resolution` vocabulary is unchanged and no decision state is added | Recorded; contract corrected under C-P3.2-C |
| R1 | **Resolved 2026-08-17:** Peter Duscha confirmed `Players` as the one-time C-04 source tab (`C-P3.2-B`). `--player-tab Players` remains required so the migration input stays explicit and does not become portal configuration | **Resolved; operator must still verify the tab exists before the live run** |
| R2 | **C-04 cannot run from `venv-web`**, by design. The separate operator environment (§3.3, runbook) is a prerequisite of running the migration at all | Accepted by C-P3.2-A |
| R3 | **R-29 now writes an authorization on a request path.** Its request-boundary controls, live capability resolution, optimistic concurrency and atomic audit are the controls that matter and are the ones a security review should press on | Open for the security-focused review |
| R4 | The TC-MIG-07 drill drops and restores `public` in the disposable database. Destructive by nature; its Unix-socket and disposable-name guards are asserted before it dumps and are unchanged | Accepted; guarded |
| R5 | `AccountRepository.discord_subject()` fails closed on an ambiguity, and no operator surface *names* such an account. A diagnostic belongs with P3.3's audit views | Accepted for now |
| R6 | Response/view-model content verification is partial: R-24, R-32, R-35 and R-36 are asserted by status and notice code only; the other six read routes have rendered-content assertions | Accepted, narrow |
| R7 | **A proposal from a superseded C-04 run is still confirmable by id.** R-28 renders `latest_run()` only, but `IdentityProposalRepository.proposal()` is keyed on the proposal id alone, so a confirmation arriving from a page rendered before a second evidence run — or hand-made — reaches an older run's proposal and links the subject *that* run recorded. Surfaced by this pass; no accepted contract sentence forbids it, and §7.6 makes older proposals deliberately durable, so it is recorded rather than changed. The controls that still apply: live Council resolution and CSRF on the request, a required reason, the character's optimistic version, `AlreadyLinked`, the run id in both audit events, and revocation through R-26. The removed `newer_run_exists` check belonged to the withdrawn apply architecture and was not a control on this path | Open for the security-focused review; a decision to refuse a superseded run's proposal would be a contract change |
| I-06 / A-05 | Carried forward unchanged | Open |
| OD-17 | The Discord bot still does not consult `character_access`. Neither closed nor widened here | Owned by Phase 5 |

---

## 9. Traceability status

| Row | Status |
|---|---|
| TC-MIG-08 | **Delivered** — balanced totals from the command, plus the constraint with the application bypassed |
| TC-MIG-09 | **Delivered as written.** C-04 writes no access row and cannot; only an R-29 confirmation does, in the same transaction as its decision. The §9 contradiction of the previous submission is resolved and this row needs no correction |
| TC-MIG-10 | **Delivered** — ambiguity persists in full, is unconfirmable at the service and by direct HTTP, and grants nothing |
| TC-MIG-11 | **Delivered** — every created link names the confirming Council member (resolved live), a reason and a correlation id, atomically with both audit events; repeated and concurrent confirmations produce one durable effect |
| TC-MIG-12 | **Delivered** — reader capability, the AST allowlist over `read_only.py`, the Google-import allowlist over the other three modules, and the `spreadsheets.readonly` scope |
| TC-MIG-13 | **Delivered as written** — the injected audit failure is during the confirmation, and grant, transition and commit failures are covered beside it |
| TC-MIG-17 | **Delivered** (new) — §5.3 |
| TC-MIG-18 | **Delivered** (new) — requirement files, subprocess import probe, lazy import |
| TC-MIG-19 | **Delivered** (new, §10) — the revoked confirmation is not labelled active, not counted as active, not re-decided and not rescued by another link on the same character; the active case is retained |
| TC-MIG-20 | **Delivered** (new, §10) — four refusals and both permitted transitions as the restricted runtime role, with migration/metadata parity and the round trip still passing |
| TC-MIG-04 (revision 0010) | **Delivered** — round trip plus the downgrade's data cost |
| TC-MIG-07 | **Delivered and automated** (the contract classes it `supervised`; the drill script remains the operator procedure) |
| TC-ACC-01…07, TC-ID-01…08, TC-CAP-01…11, TC-OBJ-01…07, TC-BG-05b/c/e | Unchanged by this remediation; their suites pass in this tree (§6.1 runs 4, 8–12) |
| TC-OBJ-05 | **Not applicable to P3.2** — job ids are P3.3's |

**No row is now delivered "under a reading".** The previous submission's §9
contradiction is closed by C-P3.2-A, and every TC-MIG row above is delivered
against its contract text as that text currently stands.

---

## 10. Independent implementation review — remediation of findings 1 and 2

Date: 2026-08-17. Scope: the two findings from the independent P3.2
implementation review, and nothing else. P3.3 was not begun, nothing was
deployed, C-04 was not run against Google Sheets, and no unrelated change was
made. Migration 0010 is still uncommitted and was corrected in place; **no
applied migration (0001–0009) was edited.**

### 10.1 Finding 1 — R-28 falsely reported revoked links as active

**The defect.** `overview()` took `confirmed` from
`IdentityProposalRepository.decision_counts()` — the *historical* resolution —
and `_proposal_view()` exposed that resolution without the current state of the
exact `granted_access_id`. `identity_migration.html` therefore rendered **every**
confirmed proposal as `confirmed-and-active` and said the link *"is active now"*.
After the supported R-26 revocation workflow (§7.5) that is false: the proposal is
still historically confirmed, and its `character_access` row is inactive.

**The contract problem, and the maintainer's ruling.** The accepted language could
not express the resulting state. §7.4 defined `confirmed` as **active links**;
VM-10 said *"four states and no fifth"*; and a confirmed-then-revoked proposal is
neither an active link nor a rejection, so it also fell out of §7.4's second
balance. Rather than invent a state in code, the choice was put to the maintainer
with both candidate resolutions. Peter Duscha ruled on 2026-08-17, recorded as
change-log entry **C-P3.2-C**: keep §7.4's *"`confirmed` counts active links"*
sentence exactly as written and add a **balanced** `confirmed_revoked` bucket
beside it. The rejected alternative — making `confirmed` the historical count with
non-balancing sub-totals — was declined because it leaves the most prominent
number on the Council screen unable to answer *"how many links did this run
produce?"*.

**What was implemented.**

| Requirement | How |
|---|---|
| Activation from the exact `granted_access_id` | `IdentityProposalRepository.granted_link_state()` and `.confirmed_link_counts()` join `identity_link_proposals.granted_access_id` to `character_access.id` and read `character_access.active`. The join is keyed on the proposal, so no other link on the same character or account is reachable from it |
| The historical fact is immutable | Nothing writes to `identity_link_proposals` on this path at all. `resolution` stays `confirmed`; the decider, reason, `decided_at`, `granted_access_id` and both audit events are untouched, and the proposal remains undecidable again (`decide()` is still conditional on it being outstanding) |
| VM-10 is honest | `LinkProposal.link_state: Literal["active","revoked"] \| None` — `None` on every row that created no link, so *"no link exists"* and *"the link was revoked"* are different values rather than the same falsy one. No `resolution` value is added |
| Totals stay arithmetically honest | `confirmed` = active confirmations, `confirmed_revoked` = the rest. `balances()` now checks `confirmed + confirmed_revoked + rejected + outstanding = proposed + ambiguous + unresolved`. Total by construction: `a_confirmation_is_a_link` makes `granted_access_id` non-null exactly on a confirmed row and the FK is `RESTRICT`, so the join loses nothing |
| The template never over-claims | `is active now` is rendered only under `resolution == 'confirmed' and link_state == 'active'`. A revoked one renders `data-status="confirmed-and-revoked"` and says the access row *"has since been revoked… is not active now"*, while stating that the confirmation itself stands |
| Bounded, no N+1 | Two set-based queries per page load: one `IN`-list over the rendered page's proposals, one `GROUP BY` aggregate for the run's totals. Neither grows with page size beyond the page, and neither is per row |

**Files changed:** `adapters/web/repositories.py` (two new read methods),
`application/web/identity_evidence.py` (`overview()`, `_proposal_view()` and their
rationale), `application/web/view_models.py` (`LinkProposal.link_state`,
`MigrationTotals.confirmed_revoked`, `balances()`),
`adapters/web/templates/identity_migration.html` (the revoked rendering, the
`confirmed_revoked` total, the header rationale).

### 10.2 Finding 2 — decided proposals could have a NULL reason

**The defect.** Migration 0010 enforced only
`decision_reason IS NULL OR length(trim(decision_reason)) > 0`, which permits
`confirmed` and `rejected` rows with `decision_reason IS NULL`. The application
service validates the reason, but the restricted runtime role holds direct
`UPDATE` on `identity_link_proposals`, so the database admitted a half-decided row
that the contracts require a reason for.

**What was implemented.** One new check constraint, in migration 0010 and in
`adapters/database/tables.py` with an identical name and an identical expression:

```sql
ck_identity_link_proposals_a_decision_states_its_reason
  CHECK ((resolution IN ('confirmed', 'rejected')) = (decision_reason IS NOT NULL))
```

Paired with the existing
`ck_identity_link_proposals_decision_reason_not_blank`, which stays unchanged, the
two together give exactly the required rule: `proposed`, `ambiguous` and
`unresolved` carry `decision_reason IS NULL`; `confirmed` and `rejected` carry a
non-null, non-blank trimmed reason. Two constraints rather than one composite
expression, deliberately — one answers *"is there a reason at all?"* and the other
*"is it worth reading?"*, and a single constraint would report the wrong fact for
half the failures it catches.

The existing consistency rules for `decided_at`, `decided_by_account_id` and
`granted_access_id` (`decision_state`, `decider`, `a_confirmation_is_a_link`) are
untouched. **No runtime grant was weakened, narrowed or widened**, and nothing
relies on service validation to close the finding: every case in §10.4 is executed
as the restricted role with the application absent.

### 10.3 The controlled contracts, reconciled

Corrected consistently rather than in code alone, all under C-P3.2-C:

| Document | Correction |
|---|---|
| `phase-3-identity-migration-contract.md` §7.4 | Second balance gains `confirmed_revoked`; the *"`confirmed` counts active links"* sentence is **unchanged**; new paragraphs state why the bucket exists and that a revoked confirmation is counted, not re-decided |
| …§7.5 | The *Reversible* bullet now says what R-28 does after a revocation, so reversibility and the report agree |
| `phase-3-view-model-contract.md` VM-10 | `link_state` and `confirmed_revoked` in the type sketch; the heading is clarified to **four *decision* states** with the no-apply-state rule preserved verbatim; a state table maps every `(resolution, link_state)` pair to its rendering; the exact-grant rule is stated |
| `phase-3-route-authorization-contract.md` §5.1 | New R-28 paragraph: current linkage from the exact `granted_access_id`, no inference from other links, no re-decision, bounded reads |
| `phase-3-test-traceability.md` | **Addition only:** TC-MIG-19, TC-MIG-20, two coverage-map rows, and a dated amendment note. No existing row rewritten or removed |
| `docs/project-management/change-log.md` | **C-P3.2-C**, with the alternatives considered, what is preserved, and an explicit statement that it does not approve P3.G2 |

The logical schema needed no change: §11's row for `identity_link_proposals`
records the key, foreign keys, uniqueness, writers, readers and retention, and
none of those moved.

### 10.4 The new regression cases, and that they reproduce the reviewed failure

Both findings were proved by **temporarily reverting the fix, running the new
cases, and restoring** — not by observing that the suite is green.

**Finding 1** (`tests/web/test_identity_migration_command.py`, 3 new cases):

| Case | Asserts |
|---|---|
| `test_r28_never_calls_a_revoked_confirmation_active` | `C-04 → R-29 confirm → R-26 revoke → R-28`. Not labelled `confirmed-and-active`; the string `is active now` absent from the page; `confirmed-and-revoked` present; `confirmed` total `0` and `confirmed_revoked` `1`; `data-balances="true"`; `resolution` still `confirmed` with the same `decided_at`, decider, reason and `granted_access_id`; the access row present, `active=false`, `revoked_at` set, keeping the reason it was **granted** for; `identity_migration.confirmed`, `character_access.granted` and `character_access.revoked` each present exactly once; no confirm control returns |
| `test_another_active_link_cannot_make_a_revoked_confirmation_look_active` | The same character carries a second, unrelated **active** link to a different account, granted outside the run. The revoked confirmation still reads revoked and the totals are unmoved — the guard against the obvious wrong fix, `"does this character have an active link?"` |
| `test_a_rejected_proposal_carries_no_link_state_at_all` | A rejection renders `data-status="rejected"` with **no** `data-link-state` attribute anywhere, so an honest revoked rendering cannot be reached by rendering every non-active row the same way |

Retained unchanged: `test_r28_renders_outstanding_confirmed_and_rejected_states`
still proves a newly confirmed, non-revoked link renders as active, and the first
new case re-asserts that state before revoking.

*Reproduction, before the fix.* With the template condition and the
`confirmed` total reverted to their reviewed form, the first two cases fail with:

```text
>       assert 'data-status="confirmed-and-active"' not in page.text
E       'data-status="confirmed-and-active"' is contained here:
E                  <p data-status="confirmed-and-active">
E                       Confirmed. This character's access row was created by the
E                       confirmation and is active now.
```

which is the reviewed defect verbatim. `2 failed, 1 passed`. Both files were
restored from a byte-for-byte backup afterwards and the suite re-run.

**Finding 2** (`tests/web/test_p3_2_runtime_grants_and_bounds.py`, 5 new cases,
all executed under `SET ROLE freedom_runtime_test` with the real
`infra/postgresql/runtime-grants.sql.tmpl` applied, each violation in its own
transaction):

| Case | Asserts |
|---|---|
| `test_the_runtime_role_cannot_confirm_a_proposal_with_no_reason` | A direct `UPDATE` to `confirmed` with `decision_reason = NULL` — every other rule of a confirmation satisfied — is refused, naming `a_decision_states_its_reason` |
| `test_the_runtime_role_cannot_reject_a_proposal_with_no_reason` | The same for `rejected` |
| `test_the_runtime_role_cannot_decide_with_a_blank_reason` | A whitespace-only reason on a decided row is refused, naming `decision_reason_not_blank` |
| `test_an_outstanding_proposal_cannot_carry_a_decision_reason` | A reason on an undecided row is refused — the equivalence's other direction |
| `test_valid_r29_and_r30_transitions_still_pass_every_constraint` | A valid confirmation and a valid rejection both succeed and land with their reasons, so the denial evidence is not proving that the table stopped working |

*Reproduction, before the fix.* With the new constraint stripped from both
migration 0010 and `tables.py`, three of the five fail — `DID NOT RAISE`, i.e. the
database **accepted** a `confirmed` row with no reason, a `rejected` row with no
reason, and a reason on an outstanding row. The blank-reason case passes before
and after (the older constraint already covered it) and the valid-transition case
passes both ways; both are correct outcomes and are recorded rather than
presented as new coverage. `3 failed, 2 passed`. Both files were restored from
backup and the suite re-run.

### 10.5 Verification, with exact results

Serially against the guarded disposable database `freedom_test`
(`$DB` is `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`), with nothing
else touching it. Run 28 is the handover's narrow set.

| # | Command | Result |
|---|---|---|
| 28 | `$DB ./venv-web/bin/python -m pytest -q tests/web/test_identity_migration_command.py tests/web/test_character_access_invariants.py tests/web/test_p3_2_runtime_grants_and_bounds.py tests/web/test_migration_0010_round_trip.py` | **107 passed**, 25 warnings, 0 skipped, 0 failed (7.54s) |
| 29 | `$DB ./venv-web/bin/python -m pytest -q tests/web` (complete portal suite) | **1088 passed, 54 skipped**, 284 warnings, 0 failed (48.66s) |
| 30 | `$DB ./venv/bin/python -m pytest -q tests --ignore=tests/web` (complete bot suite) | **2272 passed**, 1 warning, 0 failed (2m13s) |
| 31 | `./venv-web/bin/python -m compileall -q application adapters tools tests/web migrations/versions helpers` | exit 0 |
| 32 | `git diff --check` | exit 0 |
| 33 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | 14 files, **all OK**, 0 non-OK |
| 34 | `grep -h '^revision\|^down_revision' migrations/versions/*.py` | chain `0001 → … → 0010` unbroken; `0010` still descends from `0009` |

The portal suite moves 1080 → **1088**: the eight new cases and no others. The bot
suite is unchanged at 2272, as expected — nothing in this remediation is reachable
from it. Migration/metadata parity, the constraint inventory at head and
`upgrade → downgrade → upgrade` are inside runs 28 and 29
(`test_migration_0010_round_trip.py`, 7 cases), and they pass **with** the new
constraint in both declarations.

**Checks not run, and why — unchanged from §6.1.** No formatter, linter or type
checker is configured in this repository (no `pyproject.toml`, `setup.cfg`,
`.flake8`, `ruff.toml`, `mypy.ini`, `tox.ini` or pre-commit configuration;
`requirements-dev.txt` and `requirements-web-dev.txt` contain only `pytest`,
`pytest-asyncio` and `beautifulsoup4`). None was run because none was available to
run. The 500-actor benchmark was not re-run; it is exercised through
`tests/test_benchmark_harness.py` inside run 30. **C-04 has not been run against
the live spreadsheet** and this pass does not authorize one. No live Google,
Discord, Foundry or production PostgreSQL access was made, nothing was committed,
pushed or deployed, and no live service or production data was mutated. The 54
skips remain the single `test_p3_2_matrix.py` case whose permitted cells
`test_p3_2_success_cells.py` asserts instead; no database test is skipped.

**Worktree.** 27 modified files and 38 untracked, unchanged — this remediation
added no file and removed none. Unrelated worktree changes are preserved.

### 10.6 Status of the two findings

**Finding 1 (blocking) and Finding 2 (important) are submitted for independent
re-review.** Neither is claimed closed here, and neither is claimed closed on the
strength of the existing suite passing: each has new cases that were shown to fail
against the reviewed code and pass against the corrected code, quoted in §10.4.

The one item a re-reviewer should press on first is **D7 / C-P3.2-C**: finding 1
could not be closed without amending controlled contract language, the maintainer
ruled which amendment to make, and the reviewer should confirm that the amended
§7.4, VM-10 and route-contract text are mutually consistent and that the
implementation says exactly what they say — in particular that no fifth
*decision* state was introduced, that a revoked confirmation is never rewritten,
and that the second balance still accounts for every proposal.

**P3.G2 remains open. Only the maintainer can accept it**, after independent
implementation re-review and a distinct security-focused re-review by a reviewer
that did not implement this work.

---

## 11. Independent P3.G2 implementation and security review

Date: 2026-08-18. Reviewer: Codex, independent of the Claude implementation.
Scope: the complete 67-file accepted P3.2 snapshot, including the route matrix, live
capability resolution, object authorization, CSRF/origin/body preamble,
identity and character-access services, C-04/R-28/R-29/R-30, repositories,
runtime grants, migration 0010, templates, controlled contracts and recovery
documentation.

### 11.1 Findings and remediation

1. **Blocking — concurrent R-37 requests could strand an account.** The service
   counted active identities and then conditionally retired one target row. Two
   transactions aimed at the account's two different identities could both read
   two and retire one, leaving zero usable identities. A deterministic barrier
   regression reproduced two successful unlinks. `AccountRepository` now locks
   the stable `platform_accounts` parent row; the service re-reads target state
   under that lock before counting and retiring. The regression now produces one
   unlink, one refusal and one remaining active identity (TC-ID-07).
2. **Blocking — superseded C-04 evidence could still create authorization.** A
   proposal id from an older run remained confirmable after a newer run committed,
   so a corrected rerun did not revoke the stale page's power to create a real
   `character_access` row. A regression reproduced the grant. `_decidable()` now
   refuses every non-latest run, and `decide()` independently includes latest-run
   membership in its conditional update so a newer run committed during a request
   rolls back the grant, version bump, decision and audits together (TC-MIG-21).

Both cases were added first and observed failing against the reviewed code. No
other blocking or important security, authorization, identity, atomicity,
migration, secret-disclosure or contract finding remains open. The accepted
read-only Sheet credential fallback remains unchanged.

### 11.2 Verification

| Command | Result |
|---|---|
| targeted reproductions before remediation | concurrent unlink: two unlinks; superseded proposal: confirmation succeeded — both failed their new assertions |
| targeted cases after remediation | **2 passed** |
| P3.2 authorization/identity/migration slice | **191 passed**, 96 pre-existing HTTPX warnings |
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/python -m pytest -q tests/web` | **1103 passed, 54 skipped**, 284 pre-existing HTTPX warnings |
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q tests --ignore=tests/web` | **2272 passed**, 1 pre-existing dependency warning |

The 54 skips remain the intentional `test_p3_2_matrix.py` permitted cells that
the per-route success suite asserts. No database test was skipped. No live
Google, Discord, Foundry or production PostgreSQL service was contacted.

### 11.3 Recommendation

The independent implementation and distinct security-focused reviews are
complete. The maintainer accepted P3.G2 through change-log entry C-P3.2-D.

---

Nothing was deployed. No live service or data was mutated. Google Sheets was
never contacted. P3.3 has not started. Unrelated user changes in the worktree are
preserved.

P3.2 completed its **independent implementation re-review and distinct
security-focused review**. **P3.G2 was accepted by the maintainer on
2026-08-18; P3.3 may begin under its own package contract and gate.**
