# Phase 2 / I-02 — Foundry snapshot milestone submission

Status: **Superseded for implementation acceptance by controlled baseline v1.1.
Phase 2 is NOT closed.** This remains the evidence record of the submitted
implementation; ADR 0008 was subsequently rejected and its state/bootstrap/
correction scope must be removed before resubmission.

Prepared by the implementing agent. Independent Codex review is required by plan
§16.4 (*import/reconciliation*), and the Acceptance Authority records the gate
decision. This document does not claim the gate.

Starting point: commit `1695122` (the accepted Sheet identity slice; I-01
closed), with `9432ded` adding only the prompt. The worktree was clean when this
work began and nothing that existed after `1695122` has been discarded.

Plan: [phase-2-package-plan.md](phase-2-package-plan.md).
Predecessor record: [phase-2-submission.md](phase-2-submission.md) — the I-01
record, superseded for the milestone conclusion.

---

## 1. What this delivers

| Package | Delivered |
|---|---|
| 2.1 | ADR 0006 amended; versioned deterministic export contract; bounded safe ingestion with checksum-before-parse; parser/validation; the exhaustive versioned field profile |
| 2.2 | Preview that persists nothing; explicit stable mappings; deterministic reconciliation; snapshot-only roll inputs with provenance; Foundry-out-of-date warnings; no implicit deletion; atomic apply; idempotency; stale-preview refusal |
| 2.3 | Standard/protected/compensating corrections; one-Council authorization rechecked at apply; one-transaction state + audit; append-only triggers and runtime grants; migration `0002` |
| 2.4 | The Sheet boundary decided, narrowed and fenced; the legacy connector proven untouched |
| 2.5 | One-time supervised bootstrap; PostgreSQL concurrency/immutability evidence; operations, rollback and retention documentation; this submission |

## 2. The three headline decisions, and where each is enforced

**The artifact.** ADR 0006's rejection of offline snapshot import and its
`"_id": null` premise are superseded *explicitly*, in place, with every surviving
decision carried forward verbatim (no LevelDB, no Manager-initiated live access,
world-not-instance identity, exact version tuple, platform-owned stable IDs, no
write-back). The replacement is a Council-produced **export bundle** built
through supported Foundry document APIs —
[`docs/rules/foundry-export-contract.md`](../rules/foundry-export-contract.md).
A hand-saved per-Actor export, whose real id survives only in its filename, is
**refused** rather than name-matched.

**The folder set.** The bundle carries a **bounded set of 1–8 folders** and the
Manager selects one. The alternative — one folder chosen inside the Foundry
macro — was rejected because plan §12 Phase 3 requires a Platform Administrator
to select the folder *from the artifact*, and a macro-side choice cannot be
authorized or audited. Reasoning: contract §2.5.

**The state store.** Phase 2 must correct every database-managed field; those
fields have no Phase 4/5 tables yet, and plan §7.3 forbids building them all
now. The implementation uses a **profile-driven store** and records that as a
decision requiring maintainer acceptance:
[ADR 0008](../adr/0008-profile-driven-character-state.md), status **Proposed**.
It is listed in §8 as an unmet criterion.

## 3. Files changed

### Added — domain

| File | Purpose |
|---|---|
| `domain/foundry.py` | snapshot identity value objects; an identity is never a name |
| `domain/snapshot_values.py` | normalisation and comparison; `different` and `unable to compare` are distinct answers |
| `domain/field_profile.py` | the profile types, invariants, path matching and fail-closed enumeration |
| `domain/foundry_profile.py` | the profile itself, version `2026-08-02.1` |

### Added — application

| File | Purpose |
|---|---|
| `application/authorization.py` | current effective privilege, resolved at apply |
| `application/character_state.py` | one read model over the three storages |
| `application/corrections.py` | standard, protected and compensating corrections |
| `application/snapshots.py` | the immutable records an import writes |
| `application/bootstrap.py` | the one-time gate and its closing |
| `application/foundry/artifact.py` | bounded safe ingestion; checksum before parsing |
| `application/foundry/parser.py` | contract, deployment, folder-graph and identity validation |
| `application/foundry/extraction.py` | profile-classified value extraction; refuses rather than defaults |
| `application/foundry/reconciliation.py` | the deterministic report |
| `application/foundry/import_service.py` | preview, binding, apply |
| `application/foundry/roll_inputs.py` | snapshot-only projections with provenance |

### Added — adapters, migrations, tools, tests

`migrations/versions/0002_foundry_snapshot_and_character_state.py`,
`tools/bootstrap_manager.py`, and 13 test modules plus
`tests/foundry_fixtures.py` and `tests/snapshot_harness.py`.

### Modified

| File | Change |
|---|---|
| `adapters/database/tables.py` | six Phase 2 tables; provenance columns on `external_actor_mappings` |
| `adapters/database/repositories.py` | seven repositories for the new tables |
| `adapters/database/unit_of_work.py` | all repositories share one session, so an import is one transaction |
| `application/repositories.py` | the new repository protocols |
| `infra/postgresql/runtime-grants.sql.tmpl` | grants for the new tables; `UPDATE`/`DELETE`/`TRUNCATE` revoked on all five append-only ones |
| `tools/import_sheet_characters.py` | profile scope check, supervisor requirement, one-time gate, exit code 6 |
| `docs/adr/0006-…` | the amendment |
| `docs/rules/field-ownership.md` | rewritten against the 2026-08-02 rulings |
| `docs/operations/sheet-import.md` | the narrowed role and the closed gate |
| `tests/fakes.py`, `tests/test_database_schema.py`, `tests/test_database_postgresql.py`, `tests/test_runtime_grants.py` | extended for the new schema |

Nothing else was touched. `connectors/`, `ext/`, `models/`, `helpers/`,
`main.py` and `config.py` are byte-for-byte unchanged.

## 4. The Sheet work: retained, removed, repurposed

The prompt requires this list explicitly.

| Part | Disposition | Why |
|---|---|---|
| `connectors/sheets.py` | **untouched** | The live bot still requires it. Not read, not edited, not imported by any platform module. |
| `application/sheet_import.py` (identity service, mapped-name refusal) | **retained unchanged** | I-01's fail-closed identity policy. Not reopened and not weakened; the refusal logic and `domain/names.py` are as accepted. |
| `adapters/sheets/character_import.py` (parser) | **retained unchanged** | Reads exactly the four Sheet-era fields the profile classifies. |
| `adapters/sheets/read_only.py` (narrow credential) | **retained** | Still the right posture for a read-only bootstrap; the read-only service account remains a deployment step. |
| `tools/import_sheet_characters.py` | **repurposed and fenced** | No longer *the* character importer. Now a one-time Sheet-era bootstrap: startup check that every field it writes is profile-classified Sheet-era; `--apply` requires `--supervisor`; `--apply` closes permanently once `platform_initialization` exists (exit 6). |
| Character *creation* from the Sheet | **superseded** | Characters are created by the snapshot import, from stable Foundry Actor ids. The Sheet path survives only for rows that already map. |
| Read-only credential configuration, CLI and docs | **retained** | The analysis says they still have a role: the narrow bootstrap still reads the Sheet. Nothing was removed on the strength of "it exists", and nothing was kept on that strength either. |

**Nothing was deleted.** The prompt permits removing obsolete Sheet-import
configuration, CLI and docs "if they have no role after this analysis" — after
the analysis, they do have one. That is stated rather than assumed, and it is a
point a reviewer may reasonably disagree with.

**Manual bootstrap is the default.** `tests/test_sheet_bootstrap_boundary.py`
shows a Council correction reaching the same stored values and the same audit
semantics as the importer would, so "default to manual entry" is a real option.

## 5. §13.3 traceability

Every Phase 2 acceptance criterion and mandatory scenario, mapped to a named
test or to an identified supervised operational check.

### 5.1 Acceptance criteria (plan §12 Phase 2)

| Criterion | Evidence |
|---|---|
| every §6.5 invariant implemented below the UI | the application package has no web/Discord import; `test_sheet_bootstrap_boundary.py::test_the_domain_layer_imports_no_infrastructure` |
| the field profile is exhaustive, versioned, contains no unclassified supported field | `test_field_profile.py::test_the_fixture_actor_has_no_unclassified_path`, `…::test_a_new_supported_schema_field_fails_closed`, `…::test_a_new_item_document_type_fails_closed` |
| no Phase 2 process requires network or live Foundry access | `test_snapshot_import_service.py::test_the_service_needs_no_network_or_live_foundry`; no client, URL or socket exists in `application/foundry/` |
| checksum, authority, world, versions, exporter schema and folder validated before proposing changes | `test_snapshot_artifact.py` (13 refusal tests), `test_snapshot_parser.py` (67 tests), `test_snapshot_import_service.py::test_a_wrong_deployment_is_refused_with_no_transaction_opened` |
| altered bytes cannot inherit another snapshot's identity, preview or audit | `test_snapshot_artifact.py::test_one_changed_byte_is_a_different_snapshot`, `…::test_verify_refuses_bytes_that_no_longer_hash_to_the_recorded_checksum`, `test_snapshot_import_service.py::test_a_tampered_artifact_cannot_inherit_another_snapshot_identity`, `test_snapshot_database.py::test_a_tampered_artifact_is_a_different_snapshot_in_the_database` |
| all Actors map or are explicitly unresolved | `test_snapshot_reconciliation.py::test_an_unmapped_actor_is_a_create_candidate_not_a_name_match`, `…::test_an_unmapped_actor_whose_name_is_taken_blocks_the_run` |
| duplicate external IDs, malformed fields, unsupported versions, missing Actors, ambiguous mappings reported | `test_snapshot_parser.py::test_a_duplicate_actor_id_is_ambiguous_and_refused`, `…::test_a_duplicate_folder_id_is_ambiguous_and_refused`, `test_snapshot_reconciliation.py::test_a_dangling_mapping_blocks_rather_than_creating_a_character`, `test_snapshot_extraction.py::test_two_race_items_are_ambiguous_and_never_resolved_by_choosing_one` |
| repeated imports do not create duplicates | `test_snapshot_import_service.py::test_reapplying_the_same_input_under_a_new_request_key_is_a_typed_duplicate`, `test_snapshot_database.py::test_reapplying_the_same_checksum_is_a_no_op_against_postgresql` |
| import failure cannot partially commit | `test_snapshot_import_service.py::test_an_audit_write_failure_rolls_back_the_import`, `…::test_a_record_write_failure_leaves_no_partial_state` |
| stale or concurrent previews apply nothing | `test_snapshot_import_service.py` (5 staleness tests), `test_snapshot_database.py::test_two_concurrent_applies_produce_one_effect` |
| preview and dry-run persist nothing | `test_snapshot_reconciliation.py::test_a_preview_persists_no_character_or_mapping`, `test_snapshot_database.py::test_a_preview_against_postgresql_writes_nothing` |
| database-owned disagreements warn and do not overwrite | `test_snapshot_reconciliation.py::test_a_database_owned_mismatch_warns_that_foundry_is_out_of_date`, `…::test_a_matching_field_produces_no_warning_while_a_differing_one_does` |
| a Council correction copies only selected, allowlisted values, after a before/after preview, atomically and append-only audited | `test_snapshot_import_service.py::test_a_selected_correction_is_applied_atomically_with_the_import`, `…::test_an_unselected_field_is_left_alone`, `test_snapshot_database.py::test_a_selected_correction_commits_with_the_import` |
| snapshot-only fields readable without a second managed representation | `test_snapshot_roll_inputs.py::test_a_projection_exposes_no_way_to_write_a_snapshot_only_field`, `test_field_profile.py::test_snapshot_only_roll_inputs_cannot_be_selected_for_database_overwrite` |
| calculations identify snapshot and profile versions and refuse missing inputs | `test_snapshot_roll_inputs.py::test_a_roll_input_carries_the_snapshot_and_profile_it_came_from`, `…::test_a_missing_required_input_refuses_rather_than_defaulting` |
| an Actor absent from a later snapshot stays intact and mapped | `test_snapshot_reconciliation.py::test_an_absent_actor_warns_and_deletes_nothing` |
| every applied character and mapping traceable to checksum and actor | `test_snapshot_import_service.py::test_every_applied_character_and_mapping_traces_to_the_snapshot_and_actor`, `test_snapshot_database.py::test_the_stored_mapping_traces_to_the_snapshot_and_the_folder` |
| any Sheet bootstrap reads only classified fields, never writes Sheets, is not used after bootstrap | `test_sheet_bootstrap_boundary.py` (14 tests) |
| the runtime role cannot update, delete or truncate audit and history | **partial — see §8.** `test_runtime_grants.py` (grants template); `test_snapshot_database.py::test_updating_an_append_only_table_is_rejected_by_the_database` and `…::test_deleting_from_an_append_only_table_is_rejected_by_the_database` (real triggers, real PostgreSQL) |
| rollback/recovery and retention documented | [`docs/operations/foundry-snapshot-import.md`](../operations/foundry-snapshot-import.md) §6–§8 |
| supervised rehearsal with the real snapshot | **PENDING — a maintainer action. Not performed.** |
| real data is not copied into tests | `tests/foundry_fixtures.py` is synthetic by construction; no artifact is committed |

### 5.2 Mandatory Phase 2 tests

| Scenario | Named test |
|---|---|
| valid synthetic preview/apply, and the bootstrap without separate approval | `test_snapshot_import_service.py::test_a_clean_import_creates_a_character_a_mapping_and_a_record`; `test_snapshot_database.py::test_a_supervised_bootstrap_needs_no_council_member` |
| checksum mismatch after any byte changes | `test_snapshot_artifact.py::test_one_changed_byte_is_a_different_snapshot` |
| oversized, nested, unknown-shape, path-bearing input refused before a transaction | `test_snapshot_artifact.py::test_an_oversized_artifact_is_refused_without_being_parsed`, `…::test_excessive_nesting_is_refused_by_scanning_not_by_parsing`, `…::test_path_bearing_and_unsafe_names_are_refused_not_sanitised`, `test_snapshot_parser.py::test_an_unknown_top_level_key_is_refused_not_ignored` |
| ordinary member denied, one Council member accepted, revoked authorization refused | `test_snapshot_import_service.py::test_an_ordinary_member_is_denied`, `…::test_one_council_member_is_sufficient`, `…::test_authorization_is_rechecked_at_apply_not_carried_from_the_preview` |
| wrong world, unsupported version, wrong folder, unsupported schema | `test_snapshot_parser.py::test_the_wrong_world_is_refused_and_names_both_values`, `…::test_the_version_tuple_is_validated_as_a_tuple`, `…::test_an_unsupported_exporter_schema_version_fails_closed`, `test_snapshot_import_service.py::test_an_administrator_folder_change_between_preview_and_apply_is_stale` |
| malformed Actor, duplicate external ID, duplicate display name, missing/ambiguous mapping | `test_snapshot_parser.py::test_a_duplicate_actor_id_is_ambiguous_and_refused`, `…::test_two_actors_may_share_a_display_name_under_distinct_ids`, `test_snapshot_reconciliation.py::test_two_actors_sharing_a_display_name_are_two_create_candidates`, `…::test_a_dangling_mapping_blocks_rather_than_creating_a_character` |
| Actor renamed under the same external ID; Actor absent from a later snapshot | `test_snapshot_reconciliation.py::test_a_renamed_actor_under_a_stable_id_stays_the_same_character`, `…::test_an_absent_actor_warns_and_deletes_nothing` |
| repeated preview and repeated apply of the same checksum | `test_snapshot_reconciliation.py::test_the_report_is_deterministic`, `test_snapshot_import_service.py::test_repeating_the_same_request_returns_the_original_result` |
| stale preview after database, profile, folder or snapshot change, each committing nothing | `test_snapshot_import_service.py::test_a_changed_database_version_makes_the_preview_stale`, `…::test_a_changed_profile_version_makes_the_preview_stale`, `…::test_an_administrator_folder_change_between_preview_and_apply_is_stale`, `…::test_a_changed_snapshot_makes_the_preview_stale` |
| two concurrent applies cannot duplicate anything | `test_snapshot_database.py::test_two_concurrent_applies_produce_one_effect` (two threads, two engines, real PostgreSQL) |
| absent Actor warns without deletion, deactivation or unmapping | `test_snapshot_reconciliation.py::test_an_absent_actor_warns_and_deletes_nothing` |
| database-owned mismatch warns; a match does not | `test_snapshot_reconciliation.py::test_a_matching_field_produces_no_warning_while_a_differing_one_does` |
| selection defaults unselected, refuses unknown/snapshot-only fields, applies atomically with before/after, reason, actor, checksum | `test_snapshot_reconciliation.py::test_every_eligible_field_is_offered_unselected`, `…::test_a_snapshot_only_field_cannot_be_selected`, `test_snapshot_import_service.py::test_a_selected_correction_is_applied_atomically_with_the_import` |
| one Council member executes standard, protected and compensating corrections; protected needs no second actor | `test_corrections.py::test_one_council_member_can_apply_a_standard_correction`, `…::test_one_council_member_can_apply_a_protected_correction`, `…::test_one_council_member_can_apply_a_compensating_correction` — each parametrised over **every** field of that mode |
| correction tests cover every database-managed field | `test_corrections.py::test_every_database_managed_field_has_a_correction_path`, parametrised off the profile |
| Council can read/search audit; update and delete denied | `test_snapshot_database.py::test_updating_an_append_only_table_is_rejected_by_the_database`, `…::test_deleting_from_an_append_only_table_is_rejected_by_the_database`; the repository protocol exposes no update or delete |
| snapshot-only skill/stat inputs available with provenance | `test_snapshot_roll_inputs.py` (19 tests) |
| a missing/malformed/unsupported required value produces a typed refusal | `test_snapshot_roll_inputs.py::test_a_missing_required_input_refuses_rather_than_defaulting`, `test_snapshot_extraction.py` (12 refusal tests) |
| every path and field has exactly one classification; an unknown new path fails closed | `test_field_profile.py` (161 tests, parametrised off the profile) |
| bootstrap requires flag and supervisor, refuses a non-empty target, cannot run again | `test_snapshot_database.py::test_the_bootstrap_disables_itself_after_its_first_success`, `…::test_the_bootstrap_refuses_a_dataset_that_is_not_empty`, `test_bootstrap_cli.py::test_bootstrap_requires_a_named_supervisor` |
| Sheet bootstrap refuses non-allowlisted fields; manual bootstrap reaches the same state | `test_sheet_bootstrap_boundary.py::test_a_widened_importer_refuses_to_start`, `…::test_manual_entry_reaches_the_same_state_as_the_sheet_bootstrap` |
| parser, constraint and injected mid-import failure each leave everything unchanged and write no success audit | `test_snapshot_import_service.py::test_a_record_write_failure_leaves_no_partial_state`, `…::test_a_stale_preview_records_one_refused_attempt_and_no_success` |
| injected audit-write failure rolls back the import/correction | `test_snapshot_import_service.py::test_an_audit_write_failure_rolls_back_the_import`, `test_corrections.py::test_an_audit_write_failure_rolls_the_correction_back` |
| runtime-role `UPDATE`/`DELETE`/`TRUNCATE` on audit and history rejected by PostgreSQL | **partial — §8.** Trigger evidence is real (`test_snapshot_database.py`); grant evidence is template review only |
| constraints prevent two records claiming one world/Actor identity | `test_snapshot_database.py::test_a_world_actor_pair_can_only_be_mapped_once`, `…::test_a_character_has_one_mapping_per_world` |

### 5.3 §13.3 evidence classes

| Required | Provided |
|---|---|
| unit and application tests for parsing, field policy, authorization, reconciliation, typed failures | yes — 12 modules |
| repository/contract tests proving the same behaviour for fakes and PostgreSQL | partial: the fakes reproduce the uniqueness and optimistic-concurrency rules the adapter enforces, and both are exercised; a shared contract-test harness is **not** built (see §8) |
| PostgreSQL integration for migrations, uniqueness, FKs, optimistic concurrency, idempotency, rollback, audit immutability | yes — `test_snapshot_database.py` (35 tests) |
| web security tests | **not applicable** — Phase 3 owns the web surface, and none was built |
| deterministic synthetic fixtures covering the supported schema | yes — `tests/foundry_fixtures.py` |
| narrow suite then the full suite, with exact commands and results | §6 |
| formatter, linter, type checker, migration consistency, `compileall` | §6, including what is **not** configured |
| diff review for secrets, raw snapshots, unsafe logs, production data | §7 |
| recovery documentation exercised against a disposable environment | migrations up/down exercised (§6); the **backup restore drill** was not re-run for this milestone (§8) |

## 6. Commands run, and their exact results

All run in this session, on this host, against the disposable `freedom_test`
database over the Unix-domain socket.

```text
$ ./venv/bin/python -m pytest tests/test_foundry_identity.py \
    tests/test_snapshot_values.py tests/test_field_profile.py \
    tests/test_snapshot_artifact.py tests/test_snapshot_parser.py \
    tests/test_snapshot_extraction.py tests/test_field_ownership_document.py -q
429 passed in 0.32s

$ ./venv/bin/python -m pytest tests/test_snapshot_reconciliation.py \
    tests/test_snapshot_import_service.py tests/test_snapshot_roll_inputs.py -q
79 passed in 0.25s

$ TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest \
    tests/test_corrections.py tests/test_snapshot_database.py \
    tests/test_runtime_grants.py -q
186 passed, 1 skipped in 1.95s

$ ./venv/bin/python -m pytest tests/test_sheet_bootstrap_boundary.py \
    tests/test_bootstrap_cli.py tests/test_import_cli.py \
    tests/test_sheet_import_service.py -q
103 passed in 0.48s

$ TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest -q
1499 passed, 1 skipped in 7.43s

$ ./venv/bin/python -m pytest -q          # without PostgreSQL, to show the skips
1374 passed, 126 skipped in 1.65s

$ APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
    ./venv/bin/alembic check
No new upgrade operations detected.

$ ./venv/bin/alembic downgrade base && ./venv/bin/alembic upgrade head
$ ./venv/bin/alembic downgrade 0001    && ./venv/bin/alembic upgrade head
all four succeeded

$ psql -d freedom_test -tAc "select tgname from pg_trigger where not tgisinternal"
audit_events_append_only
character_transactions_append_only
foundry_snapshots_append_only
snapshot_imports_append_only

$ ./venv/bin/python -m compileall -q . -x 'venv|__pycache__|\.git'
compileall OK

$ git diff --check
no whitespace errors
```

The one skip is deliberate and named:
`test_corrections.py::test_every_database_managed_field_has_a_correction_path`
skips `character.downtime_progress`, whose classification is **unresolved** and
whose apply is disabled by design.

### Checks that could not be run

| Check | Why |
|---|---|
| formatter | none configured in this repository (`requirements-dev.txt` is `pytest` only). None installed for the purpose. |
| linter | as above. Unused imports were removed using a standard-library AST scan written for this session; that is weaker than a configured linter and is reported as such. |
| type checker | as above. New code is fully annotated, but no checker was run. |
| runtime-role grant denial against a live role | this host's PostgreSQL login lacks `CREATEROLE`, so the restricted role cannot be created and its grants cannot be exercised. See §8. |
| backup/restore drill | not re-run for this milestone; the Phase 1 drill script is unchanged. |

## 7. Diff review

- **Secrets**: none. The diff was scanned for private-key headers, service-account
  fields, client secrets and token prefixes; nothing matched.
- **Raw snapshots or player data**: none. Every fixture is synthetic by
  construction and no artifact is committed; `.gitignore` still excludes
  `fvtt-Actor-*.json`.
- **Unsafe logging**: refusals carry a fixed category and, where useful, an
  offset or a limit. Nothing renders artifact bytes, a DSN, a credential or a
  traceback. `SnapshotArtifact.__repr__` deliberately omits content, and
  `test_snapshot_artifact.py::test_repr_never_renders_artifact_content` holds it
  to that.
- **Generated files**: none.
- **Unrelated changes**: none. `connectors/`, `ext/`, `models/`, `helpers/`,
  `main.py` and `config.py` are unchanged, which is asserted by
  `test_sheet_bootstrap_boundary.py` and confirmed by `git status`.

**Nothing has been committed or pushed.** The working tree holds the change.

## 8. Unmet criteria, stated plainly

Phase 2 is **not** closed. These are outstanding:

1. **The maintainer-supervised real-snapshot rehearsal has not been performed.**
   It is a maintainer action and a separate gate check. No real import was run;
   no real artifact was read.
2. **ADR 0008 is `Proposed`.** The profile-driven state store is a
   schema-identity decision and needs the Acceptance Authority's ruling. The
   alternatives and the costs are in the ADR.
3. **`character.downtime_progress` is UNRESOLVED.** Apply is disabled for it
   pending a maintainer ruling on whether Sheet column V is corrected as text or
   as projects. Every other database-managed field is correctable and tested.
4. **Runtime-role grant denial is not exercised against a live role.** This host
   cannot create one. What *is* proven against real PostgreSQL is stronger in one
   respect and weaker in another: database triggers refuse `UPDATE` and `DELETE`
   on all four append-only tables **even for the schema owner**, which no grant
   would do; but `TRUNCATE` denial rests on the reviewed grants template alone.
   A staging environment with `CREATEROLE` would close this.
5. **No shared repository contract-test harness.** The fakes and the PostgreSQL
   adapter are each tested, and they implement the same rules, but there is no
   single suite run against both. §13.3 asks for one.
6. **The backup/restore drill was not re-run** for the new tables.
7. **Magic-item comparison will usually answer `unable to compare`** until the
   Phase 5.6a catalogue exists, because few items carry a stable identity today.
   That is the honest answer and it is visible in the report, but it means the
   inventory comparison is not yet load-bearing.
8. **Phase 3 was not begun.** No routes, templates, sessions or authentication.

## 9. Security implications

- Authorization is resolved **at apply**, from the port, not carried from the
  preview. Revocation between the two refuses the action.
- Platform Administrator does **not** imply Council authority; it cannot apply
  an import or a correction.
- The bootstrap is not an authorization bypass: it runs once, against an empty
  dataset, and its own success closes it.
- The artifact never reaches a log, a report, an audit payload or a `__repr__`.
  `foundry_snapshots.artifact_location` holds a reference, never bytes.
- Ingestion refuses archives, executables, path-bearing names, oversized and
  deeply nested input **before** parsing, and the parser refuses any Actor key
  outside the contract — so a bundle carrying `ownership` or `_stats`, which
  would contain Foundry user ids, is rejected rather than stored.
- Audit and history are append-only in the database itself, not only in the
  application.

## 10. Proposed reviewer focus

1. **The staleness binding** (`import_service.PreviewBinding`). Two defects were
   found here by the tests during implementation and fixed: a smuggled selection
   list bypassed the check, and an administrator folder change was
   unverifiable. Both now have tests. Please look for a third.
2. **`_apply_within_transaction`'s ordering** — idempotency check, reconcile,
   binding compare, block check, snapshot record, creates, corrections, import
   record, audit, commit. Is any check reachable after a write it should have
   prevented?
3. **The refusal path.** It writes in a *second* transaction after the rollback.
   Is there any state it could claim that did not happen?
4. **The profile's fail-closed enumeration** (`iter_actor_paths` plus
   `unknown_paths`). Is there a document shape whose new field would *not*
   produce an unclassified path?
5. **ADR 0008.** The load-bearing question of this milestone.
6. **`_compare_item_sets`'s precedence** — a known disagreement outranks an
   unidentifiable remainder. Is that the right way round?

## 11. What this submission does not claim

- It does not claim the Phase 2 gate.
- It does not claim the rehearsal was performed.
- It does not claim a formatter, linter or type checker was run.
- It does not claim runtime-role grants were exercised.
- It does not authorize Phase 3.
