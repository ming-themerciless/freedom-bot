# Phase 2 remediation submission — packages R1–R4

Status: **In progress. Phase 2 is NOT closed and this document does not claim
its gate.** Prepared by the implementing agent (Claude) as working Technical
Lead. Independent review by Codex is required by plan §16.4
(*import/reconciliation*), with a separate security-focused pass; the Acceptance
Authority records the gate decision.

Date: 2026-08-03

Plan: [`phase-2-v1.5-remediation-plan.md`](phase-2-v1.5-remediation-plan.md),
accepted by Peter Duscha on 2026-08-02.

Supersedes for the milestone conclusion:
[`phase-2-i-02-submission.md`](phase-2-i-02-submission.md), which remains the
evidence record of the rejected ADR 0008 implementation.

Starting point: `HEAD` is `9432ded`. **Nothing has been committed or pushed.**

---

## 1. What each package delivered

| Package | Delivered |
|---|---|
| **R1** | Field profile redesigned around authority rather than correction: `snapshot_only` / `reported` / `ignored` paths, `database_authority` / `legacy_authority_deferred` fields. Artifact, parser and export contract preserved unchanged. Rejected correction and generic-state modules removed |
| **R2** | Deferred-authority reporting; ambiguous candidate lookup fails closed per OD-42; preview binding widened to world, folder path and exporter; selection machinery removed |
| **R3** | Bootstrap narrowed to the supervised *first snapshot import*; Sheet-era value bootstrap removed; rejected-scope guard; injected-failure matrix across every write point; audit payload allowlist |
| **R4** | Schema reduced to the retained tables; migration `0002` replaced; runtime grants rewritten; live restricted-role denial evidence; migration and backup/restore drills |

## 2. The three shaping decisions, and where each is enforced

**No field is writable from a snapshot.** ADR 0008 was rejected, so there is no
correction mode, no selection list and no service that could apply one. The
profile carries no classification meaning "writable"
(`test_field_profile.py::test_the_profile_exposes_no_correction_or_writable_classification`),
the import service accepts no selection
(`test_snapshot_import_service.py::test_no_service_api_accepts_a_field_selection`),
and the rejected modules cannot be imported
(`test_rejected_scope_absent.py::test_a_rejected_module_cannot_be_imported`).

**A field with no accepted typed authority is reported, never compared.**
`FieldProfile.comparison_for` raises for a deferred field rather than returning
"not comparable", so no caller can obtain a value it might read as agreement
(`test_field_profile.py::test_a_deferred_field_cannot_be_compared`). The
reconciliation carries deferred rows in a separate type with no verdict field at
all (`test_snapshot_reconciliation.py::test_a_legacy_field_is_never_reported_as_matching_or_differing`).

**A display name is not an identity.** Under OD-42 several characters may share
one; the candidate lookup returns every candidate and refuses when there is more
than one
(`test_snapshot_reconciliation.py::test_an_ambiguous_legacy_candidate_lookup_fails_closed_and_names_every_candidate`).
No uniqueness constraint was added.

## 3. Files changed

### Redesigned

| File | Change |
|---|---|
| `domain/field_profile.py` | authority classification replaces correction/storage/value-kind |
| `domain/foundry_profile.py` | every legacy field deferred with its owning package; version `2026-08-02.1` → `2026-08-03.1` |
| `application/foundry/reconciliation.py` | deferred reporting; multi-candidate fail-closed; reads characters rather than a state model |
| `application/foundry/import_service.py` | selection machinery removed; binding widened and centralised in `_bind` |
| `infra/postgresql/runtime-grants.sql.tmpl` | retained tables only |
| `docs/rules/field-ownership.md` | target ownership and current authority separated |

### Removed as rejected scope

`application/character_state.py`, `application/corrections.py`,
`tests/test_corrections.py`, the three generic repositories and their
unit-of-work wiring, `CharacterTransaction`/`TransactionKind`, and migration
`0002_foundry_snapshot_and_character_state.py`.

`tools/import_sheet_characters.py` was reverted to its committed state under
ruling D-3 and is recorded as dormant, with its disposition owned by package
5.1.

### Added

`migrations/versions/0002_foundry_snapshot_and_identity.py`,
`tests/test_rejected_scope_absent.py`, `tests/test_runtime_grants_live.py`.

### Unchanged, deliberately

`application/foundry/artifact.py`, `application/foundry/parser.py`,
`application/foundry/roll_inputs.py`, `application/authorization.py`,
`application/audit.py`, `domain/foundry.py`, `domain/names.py`,
`docs/rules/foundry-export-contract.md`, and every ADR.

`connectors/`, `ext/`, `models/`, `helpers/`, `main.py` and `config.py` are
byte-for-byte unchanged.

## 4. Replacement migration strategy

Revision `0002` was **replaced in place** rather than corrected by a follow-on
migration. It was uncommitted and had been applied only to the disposable
`freedom_test` database — never to committed history and never to a durable
environment — so plan §14.3's "applied migrations are never edited" did not
attach to it. The reasoning is recorded in the new revision's docstring so the
substitution is visible rather than inferred from a diff.

Retained objects: `foundry_snapshots`, `snapshot_imports`,
`platform_initialization`, the provenance columns on
`external_actor_mappings`, and append-only triggers on `audit_events`,
`foundry_snapshots` and `snapshot_imports`.

Removed objects: `character_state_values`, `character_balances`,
`character_transactions` and the transaction table's trigger.

## 5. Traceability

Every acceptance criterion mapped to a named automated test or an identified
supervised check.

### 5.1 Artifact, parser and profile

| Criterion | Evidence |
|---|---|
| every supported path has exactly one classification | `test_field_profile.py::test_every_snapshot_path_has_exactly_one_mode` |
| a new supported field fails closed | `test_field_profile.py::test_a_new_supported_schema_field_fails_closed`, `…::test_a_new_item_document_type_fails_closed` |
| every deferred field names an owning package | `test_field_profile.py::test_every_deferred_field_names_an_owning_package` |
| the package exists in the controlled manifest | `test_field_ownership_document.py::test_every_owning_package_exists_in_the_migration_manifest` |
| a deferred field cannot be compared | `test_field_profile.py::test_a_deferred_field_cannot_be_compared` |
| no correction or writable classification is exposed | `test_field_profile.py::test_the_profile_exposes_no_correction_or_writable_classification` |
| snapshot-only inputs cannot be written | `test_field_profile.py::test_snapshot_only_inputs_cannot_be_selected_for_database_write` |
| contract limits are inherited unchanged | `test_snapshot_artifact.py::test_the_accepted_contract_limits_are_unchanged`, `…::test_the_contract_document_states_the_same_limits` |
| checksum before parse; bounded ingestion | `test_snapshot_artifact.py::test_one_changed_byte_is_a_different_snapshot`, `…::test_an_oversized_artifact_is_refused_without_being_parsed`, `…::test_excessive_nesting_is_refused_by_scanning_not_by_parsing`, `…::test_path_bearing_and_unsafe_names_are_refused_not_sanitised` |
| document and profile stay in step | `test_field_ownership_document.py::test_every_profile_field_appears_in_the_document` |

### 5.2 Identity, mappings and reconciliation

| Criterion | Evidence |
|---|---|
| every Actor accounted for | `test_snapshot_reconciliation.py::test_every_actor_is_mapped_a_create_candidate_or_explicitly_unresolved` |
| an unmapped Actor is a create candidate, never a name match | `test_snapshot_reconciliation.py::test_an_unmapped_actor_is_a_create_candidate_not_a_name_match` |
| duplicate display names are permitted | `test_snapshot_reconciliation.py::test_two_characters_may_share_a_display_name`, `…::test_two_actors_sharing_a_display_name_are_two_create_candidates` |
| ambiguous candidate lookup fails closed, naming every candidate | `test_snapshot_reconciliation.py::test_an_ambiguous_legacy_candidate_lookup_fails_closed_and_names_every_candidate` |
| a single claimant still blocks | `test_snapshot_reconciliation.py::test_a_single_claimant_still_blocks_because_a_name_is_not_an_identity` |
| legacy fields report deferred authority and their package | `test_snapshot_reconciliation.py::test_a_legacy_field_reports_deferred_authority_and_its_owning_package`, `…::test_the_deferred_warning_names_the_owning_package` |
| legacy fields are never reported as matching or differing | `test_snapshot_reconciliation.py::test_a_legacy_field_is_never_reported_as_matching_or_differing` |
| a deferred row carries presence, not the value | `test_snapshot_reconciliation.py::test_a_deferred_field_says_whether_foundry_holds_a_value_but_not_what` |
| rename under a stable ID keeps the character | `test_snapshot_reconciliation.py::test_a_renamed_actor_under_a_stable_id_stays_the_same_character` |
| an absent Actor warns and deletes nothing | `test_snapshot_reconciliation.py::test_an_absent_actor_warns_and_deletes_nothing` |
| preview persists nothing | `test_snapshot_reconciliation.py::test_a_preview_persists_no_character_or_mapping`, `test_snapshot_database.py::test_a_preview_against_postgresql_writes_nothing` |
| the binding covers every declared input | `test_snapshot_import_service.py::test_the_preview_binding_covers_every_declared_input`, `…::test_every_bound_input_is_reported_when_it_moves` |
| stale preview applies nothing | `test_snapshot_import_service.py::test_a_changed_snapshot_makes_the_preview_stale`, `…::test_a_changed_database_version_makes_the_preview_stale`, `…::test_a_changed_profile_version_makes_the_preview_stale`, `…::test_an_administrator_folder_change_between_preview_and_apply_is_stale` |
| the report is deterministic | `test_snapshot_reconciliation.py::test_the_report_is_deterministic` |

### 5.3 Authorization, provenance and audit

| Criterion | Evidence |
|---|---|
| one Council member suffices | `test_snapshot_import_service.py::test_one_council_member_is_sufficient` |
| ordinary and non-members denied | `test_snapshot_import_service.py::test_an_ordinary_member_is_denied`, `…::test_a_non_member_is_denied` |
| Platform Administrator alone cannot apply | `test_snapshot_import_service.py::test_a_platform_administrator_alone_cannot_apply_an_import` |
| authorization rechecked at apply | `test_snapshot_import_service.py::test_authorization_is_rechecked_at_apply_not_carried_from_the_preview`, `…::test_the_authorization_port_is_asked_again_for_the_apply` |
| zero partial commits at every write point | `test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state` (parametrised over snapshots, characters, mappings, import record, audit) |
| an audit-write failure rolls back the import | `test_snapshot_import_service.py::test_an_audit_write_failure_rolls_back_the_import` |
| one safe refused record, no partial claim | `test_snapshot_import_service.py::test_a_stale_preview_records_one_refused_attempt_and_no_success`, `…::test_a_refusal_audit_carries_no_traceback_or_artifact_content` |
| audit payload carries only allowlisted keys | `test_snapshot_import_service.py::test_the_audit_payload_contains_only_allowlisted_keys` |
| the summary carries no Actor values | `test_snapshot_reconciliation.py::test_the_import_summary_carries_counts_and_identifiers_but_no_actor_values` |
| retries and duplicates produce one effect | `test_snapshot_import_service.py::test_repeating_the_same_request_returns_the_original_result`, `…::test_reapplying_the_same_input_under_a_new_request_key_is_a_typed_duplicate` |
| a refusal does not block the corrected retry | `test_snapshot_import_service.py::test_a_refused_attempt_does_not_block_the_corrected_retry` |
| rejected scope is absent and non-importable | `test_rejected_scope_absent.py::test_a_rejected_module_cannot_be_imported`, `…::test_the_import_service_has_no_correction_dependency`, `…::test_the_profile_offers_no_field_that_a_snapshot_may_write` |
| the Sheet importer is dormant and reverted | `test_rejected_scope_absent.py::test_the_sheet_importer_is_the_accepted_committed_tool_and_is_dormant` |
| the bot's Sheet path is untouched | `test_sheet_bootstrap_boundary.py::test_the_legacy_sheets_connector_still_exposes_read_and_write`, `…::test_no_phase_2_module_imports_the_legacy_connector_except_the_fallback` |

### 5.4 PostgreSQL and operational evidence

| Criterion | Evidence |
|---|---|
| no generic state/balance/transaction table exists | `test_database_schema.py::test_no_generic_state_balance_or_transaction_table_exists`, `test_rejected_scope_absent.py::test_no_orm_metadata_defines_a_rejected_table` |
| unique world/Actor identity | `test_snapshot_database.py::test_a_world_actor_pair_can_only_be_mapped_once`, `…::test_a_character_has_one_mapping_per_world` |
| checksum uniqueness and format | `test_snapshot_database.py::test_two_snapshots_cannot_share_a_checksum`, `…::test_a_checksum_must_be_a_sha256_hex_digest` |
| database-enforced idempotency | `test_snapshot_database.py::test_a_repeated_request_key_is_refused_by_the_database`, `…::test_the_same_input_cannot_be_applied_twice`, `…::test_a_refused_attempt_does_not_claim_the_input_identity` |
| two concurrent applies produce one effect | `test_snapshot_database.py::test_two_concurrent_applies_produce_one_effect` |
| append-only enforced by the database, owner included | `test_snapshot_database.py::test_updating_an_append_only_table_is_rejected_by_the_database`, `…::test_deleting_from_an_append_only_table_is_rejected_by_the_database`, `…::test_the_trigger_applies_to_the_schema_owner_too` |
| restricted role denied UPDATE/DELETE/TRUNCATE | `test_runtime_grants_live.py::test_set_role_denies_update_on_every_append_only_table`, `…::test_set_role_denies_delete_on_every_append_only_table`, `…::test_set_role_denies_truncate_on_every_append_only_table` |
| restricted role can still do its job | `test_runtime_grants_live.py::test_set_role_permits_the_allowed_operations` |
| the role holds no privilege it should not | `test_runtime_grants_live.py::test_the_restricted_role_is_not_privileged`, `…::test_the_restricted_role_cannot_create_a_table` |
| grants template matches the live schema | `test_runtime_grants.py::test_every_table_is_granted_to_the_runtime_role`, `…::test_the_append_only_set_matches_the_schema_and_the_triggers` |
| upgrade / downgrade / upgrade | §6.2 |
| backup, restore, idempotent rerun | `test_snapshot_database.py::test_restore_matches_the_pre_drill_inventory_and_supports_idempotent_rerun`, `test_database_backup_restore.py::test_backup_and_restore_round_trip_preserves_data`, §6.5 |
| supervised real-export rehearsal | **PENDING — a maintainer action. Not performed.** See §8 |

## 6. Commands run and their exact results

All run on this host against the disposable `freedom_test` database over the
Unix-domain socket, on 2026-08-03.

### 6.1 Test suites

```text
$ TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest -q
1429 passed in 10.27s

$ ./venv/bin/python -m pytest -q          # without PostgreSQL, to show the skips
1296 passed, 133 skipped in 2.21s
```

**No skips remain in the PostgreSQL-backed run.** The single deliberate skip
reported by the superseded submission — the correction-path test that skipped
`character.downtime_progress` because its classification was unresolved — is
gone rather than reclassified. Its module was removed with the correction scope
it belonged to, and the field is now simply deferred to package 5.5 like its
neighbours (threshold T-11). The test is named in the superseded submission and
is deliberately *not* cited here, because it no longer exists.

### 6.2 Migration rehearsal

```text
$ APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic upgrade head
Running upgrade  -> 0001, Create Phase 1 identity and transaction foundation.
Running upgrade 0001 -> 0002, Create the Phase 2 snapshot, import and provenance schema.

$ ./venv/bin/alembic check
No new upgrade operations detected.

$ ./venv/bin/alembic downgrade 0001 && ./venv/bin/alembic upgrade head
$ ./venv/bin/alembic downgrade base   && ./venv/bin/alembic upgrade head
all four succeeded

$ psql -d freedom_test -tAc "select tablename from pg_tables where schemaname='public' order by 1"
alembic_version, audit_events, character_access, characters,
discord_guild_memberships, discord_membership_roles, discord_users,
external_actor_mappings, foundry_snapshots, idempotency_keys,
platform_initialization, sheet_row_mappings, snapshot_imports

$ psql -d freedom_test -tAc "select tgname from pg_trigger where not tgisinternal order by 1"
audit_events_append_only
foundry_snapshots_append_only
snapshot_imports_append_only
```

After `downgrade base` the schema held `alembic_version` alone. **No rejected
table appears at any point in the cycle.**

### 6.3 Runtime grants applied to the real restricted role

```text
$ sed 's/__APP_ROLE__/freedom_runtime_test/' infra/postgresql/runtime-grants.sql.tmpl \
    | psql -d freedom_test -v ON_ERROR_STOP=1
GRANT, GRANT, GRANT, REVOKE, REVOKE, REVOKE, REVOKE
```

Effective privileges, read back from `information_schema.table_privileges`:

| Grantee privileges | Tables |
|---|---|
| `SELECT, INSERT, UPDATE, DELETE` | `characters`, `character_access`, `discord_users`, `discord_guild_memberships`, `discord_membership_roles`, `external_actor_mappings`, `sheet_row_mappings`, `idempotency_keys` |
| `SELECT, INSERT` only | `audit_events`, `foundry_snapshots`, `snapshot_imports`, `platform_initialization` |

### 6.4 Restricted-role denial, exercised

Method: as `foundry`, `SET ROLE freedom_runtime_test`, then attempt each
operation. Every one of the twelve combinations was refused with
`permission denied for table <name>`, SQLSTATE **`42501`**
(`insufficient_privilege`), asserted per case by
`test_runtime_grants_live.py`:

| Table | `UPDATE` | `DELETE` | `TRUNCATE` |
|---|---|---|---|
| `audit_events` | denied | denied | denied |
| `foundry_snapshots` | denied | denied | denied |
| `snapshot_imports` | denied | denied | denied |
| `platform_initialization` | denied | denied | denied |

Allowed operations under the same role succeeded: `SELECT` on `characters` and
`audit_events`, and `INSERT` into `audit_events` — append-only is not read-only.
`CREATE TABLE` was denied with the same SQLSTATE.

The suite **applies the grants template itself** before assuming the role, so
this is evidence about the deployed artifact rather than about a hand-typed
equivalent. That also fixes a real defect found while running it: the schema
fixture migrates from empty on every run, dropping each table and its ACL, so
grants applied beforehand would not have survived to be tested.

### 6.5 Backup, restore and idempotent rerun

`test_snapshot_database.py::test_restore_matches_the_pre_drill_inventory_and_supports_idempotent_rerun`
and `test_database_backup_restore.py::test_backup_and_restore_round_trip_preserves_data`,
both against real PostgreSQL through
`infra/postgresql/backup-restore-drill.sh`:

1. apply a synthetic import — 1 character, 1 mapping, 1 snapshot, 1 import row;
2. record the full table/row inventory;
3. dump, checksum, **drop the schema**, restore;
4. compare the inventory — **identical**; and
5. re-apply the same immutable artifact under a new request key — returns a
   **typed duplicate**, and the inventory is unchanged.

Step 5 is the part a backup drill usually omits: a database that restores but
then duplicates every identity on the next import would pass an inventory check
and still be unusable.

### 6.6 Checks that could not be run

| Check | Why |
|---|---|
| formatter | none configured (`requirements-dev.txt` is `pytest` only) |
| linter | as above |
| type checker | as above |
| supervised real-export rehearsal | a maintainer action; not performed |

## 7. Security implications

- Removing the correction path removes the only Phase 2 route from an uploaded
  file to a character field. That is the largest single reduction in this
  remediation.
- Ingestion bounds are unchanged from the accepted contract and are now guarded
  by a test that names the contract, so relaxing one is a deliberate act.
- The deferred-authority row carries presence rather than the Foundry value, so
  Actor field data does not reach the reconciliation summary or the audit record
  built from it.
- Restricted-role denial is now exercised against a real role rather than
  reviewed as a template.
- Ambiguous identity fails closed, and every candidate is named so a human can
  resolve it deliberately.

## 8. Unmet criteria, stated plainly

1. **The maintainer-supervised real-export rehearsal has not been performed.**
   It is a maintainer action. No real export was read at any point.
2. **The Data Owner attestation does not exist**, because the rehearsal it
   attests to has not happened.
3. **The §9.4 operational windows are not set**: rehearsal window, observation
   period and preview/apply runtime budget.
4. **No formatter, linter or type checker was run**; none is configured in this
   repository (`requirements-dev.txt` is `pytest` only).
5. **Independent review has not occurred**, nor the separate security-focused
   pass. Both are required by plan §16.4 before the gate.

### 8.1 Two operator errors during R4, recorded

Neither affected the evidence above, and both are recorded because a submission
that hides its own mishaps is not evidence of anything.

- **The disposable database was dropped and could not be recreated.**
  `DROP DATABASE freedom_test` was issued as the first step of the
  replacement-migration procedure without first confirming that the `foundry`
  login could recreate it; it cannot (`rolcreatedb` is false). The maintainer
  recreated it. No data of value was lost — the database is disposable by
  design — but R4's drills were blocked until then.
- **The backup drill was run against the wrong database.** The drill takes its
  target as a positional argument and defaults to `freedom_dev`; it was invoked
  with an environment variable instead, so it drilled `freedom_dev`. That
  database was already empty — its pre-drill inventory artefact is one byte and
  the dump is 893 bytes, an empty-schema dump — so the dump/drop/restore cycle
  destroyed nothing. The drill was then re-run correctly against `freedom_test`.

Both are the same failure mode: a destructive database command issued without
first confirming its target and its reversibility.

## 9. What this submission does not claim

- It does not claim the Phase 2 gate.
- It does not claim the rehearsal was performed.
- It does not claim any drill in §6 has been run.
- It does not claim a formatter, linter or type checker was run.
- It does not authorize Phase 3.
