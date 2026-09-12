# Project review remediation R4, 2026-09-08 — implementation handback

Date: 2026-09-08

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: `docs/review/project-review-remediation-2026-09-08-r4-claude-prompt.md`.
That prompt authorizes a **bounded drill/recovery-documentation correction and
its synthetic tests**, and nothing else. It is not Package 5.0 product
implementation and it is not complete R13 pre-execution approval.

Outcome: **the remaining Blocking PR-20260908-R3-1 recovery finding is
corrected.** It is a continuation of that finding, not a new finding ID, and no
earlier finding ID is touched or closed. R3-2's pre-decode NUL rejection, R3-3's
machine-readable Git path discovery, the earlier R1/R2 corrections, the live-bot
skills fix and the current R13 evidence harness are all preserved; no
evidence-harness production source changed. Package 5.0 remains `not ready`;
P5.0-R5 remains Blocking.

**The undiagnosed pristine-schema drill failure reported in the 2026-09-07
handback (§6, case 5) remains unresolved.** It was not re-run here, and nothing
below is offered as its diagnosis or resolution.

---

## 1. The remaining finding, conceded

The `destroy_attempted` / `destroyed` split introduced by R3 is sound and is
kept. **The report that split depends on was not sufficient for what its banner
then claimed.**

`schema-state.sql` checked whether `public` exists and counted `pg_class`
relations and `information_schema` base tables. `pg_class` describes *relations*
— tables, views, materialized views, indexes, sequences, foreign and partitioned
tables. **A schema whose only object is a function reports
`schema_present=true|relations=0|base_tables=0`**: the function is described by
`pg_proc`, and the table/row inventory does not observe it either.

So for such a database:

* if the DROP was refused, before and after reports match and the schema is
  intact;
* if the DROP committed and recreated `public` while the client result was lost,
  before and after reports **also** match — and the function is gone.

R3's banner read matching diffs as *the schema is intact, nothing was lost, no
recovery is required*, and its zero-baseline special case went further: *the
database held no objects before the drill … Nothing was lost either way …
no data restore is required: skip to step 5*. Both are false for that database.
The procedure then skipped the restore that would have recovered the function.

The same unsupported inference sat one stage later, in `restore_attempted`,
where step 0 read the **row inventory alone**: "empty output ⇒ rolled back",
"no differences ⇒ committed". On an archive holding no base tables those are the
*same* output, so a rolled-back restore was read as a commit and the operator
was told to skip the restore. That dependent branch is corrected in the same
scope (§4).

### Pre-fix reproduction, run before anything was corrected

Codex's reproduction re-run here against a byte-exact copy of the submitted R3
script (`sha256 41e0b481…`), through the shipped stub helper, modelling a schema
holding one function and no relations. No database was contacted.

```
state-report fields the R3 query emits: ('relations', 'base_tables')

scenario                         | exit | pg_restore | state before                             | state after                              | reports match | inventory match | claims nothing to lose | claims no restore needed
DROP refused, function intact    |  42  |   False    | schema_present=true|relations=0|base_tables=0 | schema_present=true|relations=0|base_tables=0 |     True      |      True       |          True          |          True
DROP applied, client result lost |  42  |   False    | schema_present=true|relations=0|base_tables=0 | schema_present=true|relations=0|base_tables=0 |     True      |      True       |          True          |          True
```

The emitted R3 banner for the *lost-result* case, verbatim in the relevant part:

```
     * BOTH DIFFS PRINT NOTHING: THE SCHEMA IS INTACT. The destroy did not take
       effect, nothing was lost, and NO RECOVERY IS REQUIRED. …
     * If '…/schema-state-before.txt' itself records relations=0, then the database
       held no objects before the drill and these two reports CANNOT tell an
       intact schema from a recreated one … Nothing was lost either way, because
       there was nothing to lose, and no data restore is required: skip to step 5 …
```

This reproduces Codex's table exactly. **It is synthetic evidence, not a
PostgreSQL execution.**

## 2. The chosen evidence contract

The correction does not add a generic schema-recovery engine. It makes the
report observe more, states exactly what it observes, and keys every decision on
what those observations actually support.

**What the report observes.** `schema-state.sql` now emits one line with
`schema_present` and six counts, each from its own schema-scoped catalog:

| Field | Catalog | Covers |
|---|---|---|
| `relations` | `pg_class` | tables, views, matviews, indexes, sequences, foreign and partitioned tables |
| `base_tables` | `information_schema.tables` | the subset the row inventory can count (a subset of `relations`) |
| `routines` | `pg_proc` | functions, procedures, aggregates |
| `types` | `pg_type` | standalone base, enum, domain, range and composite types, excluding relation row types and array types |
| `extensions` | `pg_extension` | extensions installed *into* `public` |
| `other_objects` | `pg_collation`, `pg_conversion`, `pg_operator`, `pg_opclass`, `pg_opfamily`, `pg_ts_config`, `pg_ts_dict`, `pg_ts_parser`, `pg_ts_template`, `pg_statistic_ext` | the remaining schema-scoped catalogs, summed |

**What it cannot establish, stated in the banner, in the script and in the
guide:**

* it does **not** say *which* objects those are — equal counts are not an
  object-identity inventory; and
* it is **not** an exhaustive enumeration of everything PostgreSQL can place in
  a schema.

Adding a `routines` count alone was explicitly rejected as another unqualified
claim: `types` is its own field precisely so a standalone type is not silently
classified as absent, and `other_objects` carries the rest — but the report
still says it is not exhaustive rather than implying it is.

**The identity inventory that does exist** is the archive: `pg_restore --list`
over the dump names every object it holds, needs no database and changes
nothing. Every outcome that an operator has to resolve now names it.

## 3. The corrected decision, and why each branch is supported

`destroy_attempted` step 0 is still read-only, still runs both reports, and
still changes nothing before it has answered. The outcomes are now:

| Observation | Decision | What supports it |
|---|---|---|
| either report failed | **not known**; repeat step 0, change nothing | unchanged from R3 — a query that did not run is not evidence of emptiness |
| `schema_present=false` | **absent**; stop, resolve with an operator | unchanged from R3 |
| some count non-zero **and** the whole state report matches the baseline, with the inventory matching | **the destroy did not take effect**; no data restore, and none may be run | a dropped-and-recreated `public` holds nothing at all, so objects still counted there were never dropped. Stated as counts: it establishes that the schema was not dropped and recreated, and does not certify objects one by one |
| every count zero **and** the baseline recorded at least one object in any class | **dropped and recreated** — the `destroyed` state; continue at step 1 | everything the baseline counted is gone |
| every count zero **and** the baseline recorded zero in every class | **UNRESOLVED**; stop, resolve with an operator | both an intact and a recreated schema produce this pair, *and* neither report establishes that the schema held nothing, because both count named classes and no others |
| anything else | **unexpected**; stop, resolve with an operator | unchanged in intent from R3, re-expressed over the counts |

**Every inference that `relations=0` means no objects existed, or that nothing
could have been lost, is removed.** The matching-diffs branch no longer exists as
"both diffs print nothing ⇒ intact": matching reports now decide nothing on
their own, because the R3 defect is exactly two matching reports over a schema
that lost an object. What decides is whether any counted object is *present*.
The zero-baseline special case no longer says "nothing was lost either way …
no data restore is required" and no longer sends the operator on to the grants;
it says **"THIS IS NOT 'THERE WAS NOTHING TO LOSE'"** and stops. That is the
conservative stop the prompt permits, and it is not a new recovery engine.

`test_no_recovery_path_prescribes_an_unrequested_destructive_reset` still runs
over all five banner stages: no `DROP`, `DROP DATABASE`, `--clean`, `-c ` or
`TRUNCATE` was added, and no branch prescribes restoration over known existing
objects — three of the six outcomes end in "stop and resolve it with an
operator" rather than in a mutation.

## 4. The dependent branch corrected in the same scope (item 5)

`restore_attempted` step 0 read the row inventory alone and drew the same kind
of conclusion from it. It now runs the state report first, and its outcomes are:

| Observation | Decision |
|---|---|
| either report failed | not known; repeat step 0 |
| the baseline records zero in every class | **cannot be resolved by these reports** — both a rollback and a commit leave every count at zero; stop, resolve with an operator, reading `pg_restore --list` |
| every count zero, baseline recorded objects | the transaction **rolled back**; continue at step 1 |
| both diffs print nothing, baseline recorded objects | the restore **committed**; SKIP STEP 4, continue at step 5 |
| anything else | **partial**; neither resuming nor repeating is safe |

The banner states the reason in place: the row inventory counts base tables, so
on an archive that holds none a rolled-back restore and a committed one produce
the same output.

## 5. What was preserved

* **Responsibility before DROP, confirmed destruction only after success.**
  `DRILL_STAGE="destroy_attempted"` is still assigned before the command and
  `"destroyed"` only after it succeeds;
  `test_each_stage_is_recorded_only_after_its_command_succeeded` still asserts
  `attempted_destroy < drop < destroyed` at the source.
* **The absent/unexpected stop and query-failure-as-unknown behaviour**, both
  unchanged in substance.
* **The confirmed post-restore resume points.** `restored`,
  `schema_grants_applied` and `grants_applied` are untouched and their banners
  still contain no `pg_restore` at all; a confirmed restore is never repeated.
* **Checksummed recovery artifacts**, the exact validated runtime role rendered
  before the destroy, the explicit zero-runtime-role statements at every stage
  that reaches them, and **both final verifications** terminating every emitted
  procedure.
* **R3-2 and R3-3.** `hex_record_contains_nul` and its byte-pair scan, and the
  `--porcelain=v1 -z` discovery with both rename endpoints, are unmodified and
  still asserted by their own regressions (all passing, §7).
* **The live-bot skills fix** (`models/skills.py`, `tests/test_skills.py`) and
  every other pre-existing modification and untracked file. Nothing was reset,
  reverted, staged, committed, pushed or reformatted; the working tree holds the
  same **88** entries it held at the start, plus this handback.
* **Every execution restriction.** No SSH, no target-host inspection or
  mutation, no database operation, no destructive drill, no `--execute`, no
  armed real process boundary or materializer, no execution of a generated
  vector, no deployment, no migration `0014`, no cutover, no OD-62 ruling, no
  Package 5.1+ work. **No stub test falls through to a real PostgreSQL client**:
  every stub run puts `psql`, `pg_dump` and `pg_restore` on `PATH` ahead of
  anything else, the drill's gate 0e is answered by the stub, and
  `TEST_DATABASE_URL` was never exported in this session.
* **Every unconfirmed interpreter and `E7` target fact remains unconfirmed.**

## 6. Files changed

| File | Change |
|---|---|
| `infra/postgresql/backup-restore-drill.sh` | `schema-state.sql` extended from two counts to six, each from its own catalog, with the "what it observes / what it does not" contract beside the query; the `destroy_attempted` step-0 outcomes rewritten (matching-diffs branch and zero-baseline special case both replaced); the `restore_attempted` step-0 outcomes rewritten to read the state report first; header comment, the schema-state declaration comment and the step-3a comment updated |
| `docs/operations/database-development.md` | the same evidence contract and both step-0 outcome tables; the `restore_attempted` stage row; the "what step 0 can establish is narrower" paragraph and its statement of the withdrawn claim; the artifact table's `schema-state.sql` / `schema-state-before.txt` rows |
| `tests/test_database_backup_restore.py` | the stub's state and inventory answers made parameters **projected through the drill's own query**; `schema_state_report`, `_counted_objects`, `SCHEMA_STATE_FIELDS` and four modelled catalogs; **7 new cases**; `test_the_failed_destroy_banner_accounts_for_every_schema_state` rewritten; the documentation-agreement test extended to both new contracts and to the withdrawn claims; three literal report assertions re-pointed at the projected constants |
| `docs/review/project-review-remediation-2026-09-08-r4-handback.md` | this file |
| `docs/review/Handover information` | dated pointer to this handback, prior submissions retained |

No file under `tools/`, `application/`, `domain/`, `adapters/`, `models/`,
`ext/`, `migrations/`, `connectors/`, `helpers/`, `foundry-module/` or
`tests/web/` was modified.

### The stub change that matters most

The R3 stub answered the state query with a literal the test chose. That would
have hidden this defect: a test could have "modelled a function" by handing the
stub a report that mentions one, whatever the drill's query actually asks. **The
stub now projects a modelled catalog through the drill's own `schema-state.sql`,
read out of the script.** A report can only observe the classes its query names,
so under the R3 query a function-only schema projects to
`relations=0|base_tables=0` and the two scenarios collapse into one — which is
what makes the new tests fail against the R3 tree rather than pass vacuously.

## 7. Verification

### The environment, and what it is not

`.agents/AGENTS.md` documents the test environment as `oracle-test`, with
`/opt/freedom-blades/runtime/venv-web/bin/python` as the interpreter. **It was
not used and could not be**: this prompt retains the no-SSH restriction, so
`oracle-test` was not contacted at all.

Interpreter availability was **probed directly on this host in this session**,
not inferred from an earlier handback:

| Interpreter | Version | `import pytest` |
|---|---|---|
| `/usr/bin/python3` | 3.12.3 | not installed |
| `/opt/freedom-blades/runtime/venv-web/bin/python` | 3.12.3 | not installed. This is the **runtime** environment; installing into it is forbidden and was not done |
| `/opt/discord-bots/venv/bin/python` | 3.12.3 | pytest 8.4.2 |
| `/opt/discord-bots/venv-web/bin/python` | 3.12.3 | pytest 8.4.2 |

The last two are what was actually run. They are **local fallbacks, not the
documented environment**, and the historical `/opt/discord-bots/` path is
evidence of these runs and not a default. `shellcheck` is not installed on this
host.

### Results, run serially against the final tree

`pgrep` confirmed no other pytest process before starting, and
`TEST_DATABASE_URL` was **unset for every run**.

| # | Command | Result |
|---|---|---|
| 1 | `bash -n infra/postgresql/backup-restore-drill.sh` | clean |
| 2 | `venv … pytest -q -rs <11 deselections> tests/test_database_backup_restore.py tests/test_filesystem_layout.py` | **192 passed, 11 deselected** |
| 3 | `venv-web … pytest -q -rs tests/web/test_p3_4_static_assets.py` | **111 passed** |
| 4 | `venv … pytest -q tests/phase_5_0_evidence` | **1143 passed** |
| 5 | `venv-web … pytest -q tests/phase_5_0_evidence` | **1143 passed** |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `venv … -m compileall -q` over the changed test module, the scope-guard module and `tools/phase_5_0_evidence` | clean |
| 8 | `venv-web … -m compileall -q` over the same paths | clean |
| 9 | `git diff --check` | clean |
| 10 | manifest re-hash of all covered sources | **28 sources, 0 mismatches** |

**Baseline, measured rather than quoted.** The R3 tree — its script, its guide
and its test module, all byte-exact copies taken before the first edit — was run
against the same selection and returned **185 passed, 11 deselected**, which
reproduces the R3 handback's figure for that selection exactly and is the
cross-check that the baseline is the R3 tree. The final tree returns **192**, so
this correction adds **7 cases**. Runs 3–6 are unchanged from R3, as expected:
nothing outside the drill, its guide and its tests was touched.

`tests/test_filesystem_layout.py` was inspected before being run: no `database`
marker, no database fixture, no `TEST_DATABASE_URL` reference and no PostgreSQL
client invocation. Its 5 cases account for the difference between run 2's 192
and the drill module's own 187.

### Pre-fix failure record

Recorded before the corrections, in two forms.

1. **The behavioural reproduction** in §1: two scenarios, identical exit status,
   identical matching reports, and a banner claiming there was nothing to lose
   and no restore was needed in both.
2. **The new regressions run against byte-exact copies of the R3 script and
   guide, with the final test module: 10 failed, 177 passed, 11 deselected.**

   * `test_a_function_only_schema_is_never_called_empty_of_objects` (2 cases)
   * `test_the_printed_step_zero_separates_a_lost_function_from_a_refused_drop`
   * `test_a_standalone_type_is_not_silently_classified_as_absent`
   * `test_a_baseline_that_counts_nothing_is_left_explicitly_unresolved`
   * `test_the_state_report_counts_every_schema_scoped_catalog_it_claims_to`
   * `test_the_uncertain_restore_is_not_settled_by_an_empty_row_inventory`
   * `test_the_failed_destroy_banner_accounts_for_every_schema_state` (2 cases,
     rewritten)
   * `test_recovery_instructions_match_database_development_documentation`
     (extended)

   The two demonstration tests fail on their central assertion — that the two
   scenarios' reports differ — which under R3 they do not, because the query
   observes neither the function nor the type.

### The scenarios and the decisions they now emit

Post-fix, the same reproduction:

```
state-report fields the drill's query emits: ('relations', 'base_tables', 'routines', 'types', 'extensions', 'other_objects')

scenario                         | exit | pg_restore | state before                                                       | state after                                                        | reports match | claims nothing to lose | claims no restore needed
DROP refused, function intact    |  42  |   False    | …|relations=0|base_tables=0|routines=1|types=0|extensions=0|other_objects=0 | …|relations=0|base_tables=0|routines=1|types=0|extensions=0|other_objects=0 |     True      |         False          |          False
DROP applied, client result lost |  42  |   False    | …|relations=0|base_tables=0|routines=1|types=0|extensions=0|other_objects=0 | …|relations=0|base_tables=0|routines=0|types=0|extensions=0|other_objects=0 |     False     |         False          |          False
```

The drill emits the same banner for both, because it still genuinely cannot tell
them apart. The printed step 0 now can, and the emitted rules select:

* **function intact** — some count non-zero and the report matches the baseline
  ⇒ *the destroy did not take effect*; no restore, and none may be run;
* **function lost** — every count zero against a baseline that recorded an
  object ⇒ *dropped and recreated*; continue at step 1, which restores the
  function from the archive. Under R3 this scenario was told no restore was
  required.
* **baseline records zero in every class** — a third scenario, asserted
  separately ⇒ *these reports cannot resolve this state*; stop for an operator,
  with `pg_restore --list` named as the identity inventory.

### Other object kinds considered

`pg_proc` (functions, procedures, aggregates) and standalone `pg_type` entries
(base, enum, domain, range, composite) are counted in their own fields, and each
has a test. `pg_extension`, `pg_collation`, `pg_conversion`, `pg_operator`,
`pg_opclass`, `pg_opfamily`, the four `pg_ts_*` catalogs and `pg_statistic_ext`
are counted, the last ten summed into `other_objects`. Triggers, constraints,
rules, policies and indexes belong to relations and are covered through them;
casts and foreign-data servers are not schema-scoped.

**What remains unresolved and is stated as such.** The report is still counts
over named catalogs. It cannot name the objects, and a future PostgreSQL version
may place something in a schema that none of these catalogs enumerates. That is
why the all-zero-on-both-sides state stops for an operator rather than being
called empty, and why the "destroy did not take effect" outcome says it
establishes that the schema was not dropped and recreated rather than certifying
objects one by one.

### Evidence limitations — synthetic versus PostgreSQL

* Every case above is a **stub reproduction**. The reports are computed in
  Python and projected through the drill's query text; no SQL is executed.
* They establish **which recovery decision the drill emits for a given pair of
  reports**, and the ordering and content of the emitted procedure.
* They establish **nothing about whether the new SQL counts a real catalog
  correctly**, and nothing about whether PostgreSQL returns what the modelled
  catalogs assume. **The extended `schema-state.sql` has not been executed
  against any PostgreSQL server.** Its column names were checked against the
  PostgreSQL 16 catalog documentation, and that is the whole of the evidence for
  it. A first authorized run should execute it before the drill is relied on.
* **No new database-semantic regression was written and none was executed**, so
  there is no twelfth deselected case.

### Deselected: eleven cases, by name

All in `tests/test_database_backup_restore.py`, unchanged from the R2/R3 set:

1. `test_the_drill_accepts_an_explicit_unix_socket_directory`
2. `test_backup_and_restore_round_trip_preserves_data`
3. `test_the_drill_leaves_the_runtime_roles_privileges_intact`
4. `test_the_drill_fails_when_the_privilege_state_is_not_restored`
5. `test_the_drill_preserves_pristine_schema_ownership_and_privileges`
6. `test_the_drill_fails_when_schema_privileges_are_not_restored`
7. `test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure`
8. `test_the_documented_recovery_procedure_restores_runtime_table_grants`
9. `test_a_role_whose_sql_identity_differs_refuses_against_postgresql`
10. `test_a_newline_bearing_role_refuses_against_postgresql`
11. `test_the_post_restore_recovery_path_restores_grants_without_restoring_again`

**None of the eleven is claimed to pass against this tree.** Each one's
source-replacement anchors and asserted banner literals were re-checked against
the corrected script so that an authorized run exercises the current code rather
than failing stale. **Case 5's previously undiagnosed failure remains
undiagnosed**: it was not re-run, and no stub result here is offered as its
explanation.

### Whole modules excluded, by name

Both are `pytest.mark.database` modules that invoke the real drill against a
real database, and both were identified by reading them:

* `tests/test_snapshot_database.py`
* `tests/web/test_identity_migration_backup_restore.py`

### Checks not run, and why

| Not run | Reason |
|---|---|
| The eleven deselected cases | destructive drill / cluster-role creation; the prompt forbids them here |
| The two database-marked modules above | same |
| The extended `schema-state.sql` against PostgreSQL | no database operation is permitted; it is stated as unexecuted rather than implied to work |
| The complete bot suite and the complete web suite | the prompt forbids launching a broad suite intending to stop before database access. The affected modules were inspected and run individually and are named above |
| Anything on `oracle-test` | the no-SSH restriction; the documented environment is unreachable under this authority |
| Either suite **under the documented `oracle-test` interpreter** | same; runs 2–5 are this host's local interpreters and are labelled as such |
| Re-running the pristine-schema drill to diagnose the outstanding failure | it is a destructive drill; the prompt forbids it |
| The evidence harness executor | no `--execute`, no armed boundary or materializer, no generated vector; unchanged from R13 |
| A configured formatter, linter or type checker | **none is configured in this repository**: there is no `pyproject.toml`, `ruff.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `.pre-commit-config.yaml`, and `pytest.ini` is the only tool configuration present. `shellcheck` is not installed on this host. `compileall`, `bash -n` and `git diff --check` are what is available and were run |

## 8. Generated artifacts

**No evidence-harness production source changed in this revision**, so the
manifest was verified and the generated artifacts were left untouched. Nothing
was regenerated and nothing was hand-edited.

| Fact | Value |
|---|---|
| Covered sources re-hashed from this tree | **28** |
| Digest mismatches against the manifest | **0** |
| Manifest version / schema | **5** / `phase-5-0-evidence-review-manifest`, unchanged |
| Harness version | **0.6.0-pre-execution**, unchanged |
| Superseded R13 digest, never to be passed to `--execute` | `057c84a96225bfb8e1b02f4502619015b06b8dbc050342423ade25be4f3b7ae5` |

**No digest was passed to `--execute`.**

## 9. Status, and what this does not claim

* **The remaining PR-20260908-R3-1 recovery finding is corrected.** After an
  uncertain DROP, a schema holding non-relation objects cannot be declared
  intact, empty of all objects, or safely recovered merely because relation and
  row-count reports match; a lost object cannot be dismissed as "nothing to
  lose"; and the genuinely unresolved state stops for an operator without an
  automatic recovery mutation.
* **The dependent `restore_attempted` branch** carried the same inference over
  the row inventory alone and is corrected within the same bounded scope.
* **Package 5.0 remains `not ready`. P5.0-R5 remains Blocking.** No finding,
  assumption, decision, residual risk or gate is closed, and no roadmap, RAID,
  decision or gate record was altered. **R13 has not received complete
  independent pre-execution approval**, and nothing here implies one.
* This submission does not claim the eleven deselected cases pass, does not
  claim any figure from the documented `oracle-test` environment, does not
  confirm any reviewed target fact, and does not resolve the outstanding
  pristine-schema drill failure.

## 10. Request

Please re-review, and in particular:

1. **the evidence contract** — whether six named catalog classes plus an
   explicit "these are counts, and they are not exhaustive" is the right
   boundary, or whether a class has been left out that matters;
2. **the "destroy did not take effect" branch** — whether "some counted object
   is present and the report matches the baseline" is a sound basis for
   declaring that no restore is required, or whether it too should stop;
3. **the unresolved stop** — whether stopping on an all-zero baseline is the
   right refusal rather than a gap, given it withdraws R3's grant-only path;
4. **the `restore_attempted` correction** — whether treating it as a dependent
   instruction inside this bounded scope was right, and whether its outcome
   table is complete; and
5. **the unexecuted SQL** — the extended `schema-state.sql` has never run
   against PostgreSQL, and whether that should be executed under authorization
   before this correction is accepted.

Nothing here is offered as operational execution, and this submission stops
before it.
