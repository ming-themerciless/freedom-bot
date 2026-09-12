# Project review remediation R2, 2026-09-07 — implementation handback

Date: 2026-09-08

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: `docs/review/project-review-remediation-2026-09-07-r2-claude-prompt.md`.
That prompt authorizes a **bounded correction of the backup/restore drill, its
recovery documentation, and the production-file scope guard**, and nothing else.
It is not Package 5.0 product implementation and it is not complete R13
pre-execution approval.

Outcome: **PR-20260907-R2-1, PR-20260907-R2-2 and PR-20260907-R2-3 are
remediated.** The previous remediation and the current R13 evidence harness are
preserved; no evidence-harness production source changed. Package 5.0 remains
`not ready`; P5.0-R5 remains Blocking. No assumption, decision, residual risk or
gate closes through this work, and the earlier finding IDs are untouched.

**The undiagnosed pristine-schema drill failure reported in the previous
handback (§6, case 5) remains unresolved.** It was not re-run here, and nothing
below is offered as its resolution.

---

## 1. PR-20260907-R2-1 — Blocking: newline-bearing role identities were still changed

### The finding, conceded

PR-20260907-2 stopped the guard from *repairing* a name. It did not stop the
**transport** from doing so, and the transport is upstream of the guard:

* `RUNTIME_ROLE_REPORT="$(detect_runtime_role)"` strips **trailing** newlines;
* the line reader below it treats a newline as a record boundary; and
* it skipped empty lines, so a **leading** newline was discarded too.

A quoted PostgreSQL role name may contain anything but NUL, newlines included.
So the guard validated a different string from the one the catalog holds, and in
one case validated nothing at all.

### Pre-fix evidence, reproduced before anything was corrected

The pre-R2 script was reconstructed byte-exactly (see §7) and driven through the
stub boundary in its **own** transport — one plain record per line, as
`psql -tA` emitted it then. `\n` denotes an actual newline inside one role name.
No database was contacted.

```
catalog role(s)                                exit   DROP  runtime grant
"freedom_runtime_test"                            0   True  GRANT USAGE ON SCHEMA public TO freedom_runtime_test;
"MixedCase"                                       2  False  absent
"freedom_runtime_test\n"                          0   True  GRANT USAGE ON SCHEMA public TO freedom_runtime_test;
"\nfreedom_runtime_test"                          0   True  GRANT USAGE ON SCHEMA public TO freedom_runtime_test;
"\n"                                              0   True  absent
"freedom\nruntime"                                2  False  absent
"a\n\nb"                                          2  False  absent
"freedom_runtime" + "freedom_runtime_test\n"      2  False  absent
"freedom_runtime" + "\n"                          0   True  GRANT USAGE ON SCHEMA public TO freedom_runtime;
zero rows                                         0   True  absent
```

The first five rows are Codex's table exactly. The last two are this handback's
addition and the second of them is the worse one: **two catalog roles arrived as
one record**, so the multiple-role refusal — the guard DS-R8-1 was added to make
reachable — did not fire, and the drill destroyed and restored while granting to
one of two roles. `freedom\nruntime` also refuses for the wrong reason: it is one
role read as two.

These are stub reproductions. They establish that the destructive step was
reached with a corrupted identity; they establish nothing about the rendered SQL.

### The correction — an unambiguous transport, decoded strictly

Option 2 of the prompt's item 1 was taken: **transport the names in an
encoding that cannot contain a separator, and decode strictly.** No second
regular expression was applied after a lossy split, and no validation moved into
SQL.

The query now emits, in this order:

```text
ROLE <the role name's UTF-8 bytes, hex encoded>   one line per record
END <the number of records>                       exactly one, last
```

so that

1. **a record cannot contain a separator.** It is `[0-9a-f]` and nothing else, so
   neither command substitution nor a line reader can change or split it;
2. **cardinality is stated by the server**, not inferred from how many lines
   survived. The declared count is compared with the number of records decoded,
   and a mismatch refuses; and
3. **absence is detectable.** A report with no terminator is unreadable, which is
   what stops a truncated or empty result from being read as "no runtime role".

`decode_hex_role()` decodes back to the exact catalog bytes through
`printf -v … '%b'`, deliberately not through command substitution — that would
strip exactly the trailing newline this correction exists to preserve. The
decoded bytes are what the **unchanged** supported-role contract is applied to.

### The contract was not widened (item 2)

Nothing in the supported-role contract changed. `test_the_supported_role_
contract_itself_is_unchanged` asserts, at the source, that the lower-case fold,
`^[a-z_][a-z0-9_]{0,62}$`, `is_reserved_role_spelling`, the special-role
spellings and the `pg_` prefix are all still there. A quoted name still refuses —
it is simply refused for what it actually is rather than after being repaired
into something else. The multiple-role refusal, the zero-row path and the two
supported lowercase names are unchanged in substance.

### Unreadable transport and client failure are refusals (item 3)

`refuse_runtime_report()` exits `2` with **fixed text carrying no catalog
content**, and says explicitly that this is *not* taken as "no runtime role":

| Condition | Reason printed |
|---|---|
| the query did not exit 0 | `the query did not complete` |
| no `END` line | `the report carried no terminator` |
| `END` without a count | `the terminator carried no record count` |
| declared count ≠ records decoded | `the report carried fewer or more records than it declared` |
| a record after the terminator | `a record followed the terminator` |
| a record that is not even-length lower-case hex | `a role record was not hex encoded` |
| any other non-empty line | `the report carried a line that is neither a record nor the terminator` |

The multiple-role diagnostic also stopped printing raw names: it prints the count
and the hex forms, because a catalog name is arbitrary bytes and may carry
terminal escapes.

### Post-fix, the same reproduction

```
catalog role(s)                                exit   DROP  runtime grant
"freedom_runtime_test"                            0   True  GRANT USAGE ON SCHEMA public TO freedom_runtime_test;
"MixedCase"                                       2  False  absent
"freedom_runtime_test\n"                          2  False  absent
"\nfreedom_runtime_test"                          2  False  absent
"\n"                                              2  False  absent
"freedom\nruntime"                                2  False  absent
"a\n\nb"                                          2  False  absent
"freedom_runtime" + "freedom_runtime_test\n"      2  False  absent
"freedom_runtime" + "\n"                          2  False  absent
zero rows                                         0   True  absent
```

Both positive controls are preserved: the supported name reaches step 5b and
renders its grant, and zero rows still takes the documented empty path. `DROP` is
read from the stub invocation log, so it is a fact about what was issued.

### Regressions added (item 4)

| Test | Cases | What it establishes |
|---|---:|---|
| `test_a_newline_bearing_role_refuses_before_any_destruction` | 8 | leading, trailing, embedded, newline-only, multiple breaks, `\r`, and newline beside whitespace — each exit 2, no `DROP`, no `pg_restore`, no rendered grant, **no recovery banner** |
| `test_a_newline_bearing_role_is_not_repaired_into_a_supported_one` | 2 | the specific harm: the supported name the transport used to produce is emitted nowhere |
| `test_a_newline_only_role_is_a_record_not_a_zero_row_result` | 1 | the empty path is not taken |
| `test_a_valid_role_beside_a_newline_bearing_one_is_still_two_records` | 3 | cardinality survives, including the pair the reader used to collapse |
| `test_the_supported_names_still_pass_through_the_new_transport` | 2 | **positive control**: a decoder that refused everything would pass every negative above |
| `test_zero_records_are_still_the_documented_empty_path` | 1 | `END 0` is an answer, not a failure |
| `test_an_unreadable_role_report_refuses_and_is_never_read_as_zero_roles` | 13 | every malformed transport in the table above, including the **pre-fix wire format itself** |
| `test_an_unreadable_role_report_does_not_echo_its_contents` | 1 | no `hunter2`, no escape byte, in stdout or stderr |
| `test_a_failing_role_query_refuses_rather_than_inferring_zero_roles` | 1 | a client failure is a stated refusal |
| `test_the_role_transport_no_longer_splits_on_a_character_a_name_may_contain` | 1 | the defective construct is gone, at the source |
| `test_the_supported_role_contract_itself_is_unchanged` | 1 | nothing was widened |
| `test_the_role_report_query_can_be_read_out_of_the_script` | 1 | the helper the PostgreSQL regression uses really extracts the script's query |

The existing invalid-name cases, the `MixedCase`/whitespace/keyword/`pg_` table,
the multiple-role refusal and the zero-role positive control are all retained.

### Transport evidence and database-semantic evidence, kept apart (item 5)

The stub emits the report **computed in Python** by `encoded_role_report()`. That
is deliberate and it is stated in the helper's own docstring: driving the drill
with it proves that the shell decodes records losslessly, counts them correctly
and classifies the decoded bytes. It proves **nothing** about whether the SQL
encodes the catalog correctly, because no SQL runs.

The database-semantic half is
`test_a_newline_bearing_role_refuses_against_postgresql`, added and **not
executed**. It creates a `NOLOGIN` probe role whose quoted name contains a
newline, asserts PostgreSQL stored it that way, runs **the drill's own query read
out of the script** and asserts the emitted lines are exactly
`["ROLE <hex-of-the-name-including-the-newline>", "END 1"]`, then asserts the
drill refuses before any destruction. Against the pre-fix script it fails at the
last step. It creates and drops a cluster role, so it is deselected here; see §6.

### Acceptance

No unsupported name became a supported name and none vanished as a record; every
tested unsupported input refuses before destruction, with no recovery banner.

---

## 2. PR-20260907-R2-2 — Blocking: recovery restarted an already completed restore

### The finding, conceded

`on_exit()` read one flag, `SCHEMA_DROPPED`, set at step 4 and cleared only on
success. It therefore printed the same full `pg_restore --single-transaction
--exit-on-error` for every failure after the destroy — including the failures
that happen *after* the data restore has committed, where repeating it aborts on
the objects already there instead of reaching the grant repair the operator
needs. The banner also called the database "empty or partially restored" in every
one of those cases, and the recovery tests injected failure only before the
restore committed.

### Pre-fix evidence, reproduced

Codex's reproduction, re-run against the reconstructed pre-fix script: the stub
`psql` fails with exit 42 only while applying `runtime-grants.sql`.

```
exit: 42
--- stub invocation log ---
  pg_dump     --format=custom --dbname=freedom_test --file=…/freedom_test.dump
  psql        -c DROP SCHEMA public CASCADE; CREATE SCHEMA public;
  pg_restore  --dbname=freedom_test --no-owner --no-privileges --single-transaction --exit-on-error …
  psql        -f …/schema-grants.sql
  psql        -f …/runtime-grants.sql          <- fails, exit 42
--- emitted recovery procedure ---
  1. sha256sum --check '…/freedom_test.dump.sha256'
  2. sha256sum --check '…/schema-grants.sql.sha256'
  3. sha256sum --check '…/runtime-grants.sql.sha256'
  4. pg_restore --dbname=freedom_test --no-owner --no-privileges --single-transaction --exit-on-error …
  5. psql … -f '…/schema-grants.sql'
  6. psql … -f '…/runtime-grants.sql'
     Restores the table grants 'freedom_runtime_test' held before the destroy. …
     out from the now-empty database.
  …
Re-running this drill is NOT a recovery step: it would dump the empty database …
```

A successful restore, then a grant failure — and the emitted procedure still
began its mutation steps with the same full restore, over a database it called
empty.

### The correction — a stage, advanced only by success (item 1)

`SCHEMA_DROPPED` is replaced by `DRILL_STAGE`, which records the last step that
**succeeded**. Every assignment is placed *after* the command whose success it
records, with one deliberate exception stated in the script and asserted by
`test_each_stage_is_recorded_only_after_its_command_succeeded`: `destroyed` is set
*before* `DROP SCHEMA`, because a failure inside the destroy leaves the schema in
an unknown state and `destroyed` is the honest reading of that.

### The stages, and the exact emitted recovery path for each

| Stage | Reached when | What is known about the data | Emitted procedure |
|---|---|---|---|
| `intact` | before step 4 | untouched | **no banner** |
| `destroyed` | `DROP SCHEMA` ran, restore not started | **empty** | 3 checksums → restore → schema grants → runtime grants → verify privileges → verify inventory |
| `restore_attempted` | restore ran, did not report success | **not known** | **step 0** establishes which, then the same eight steps, with an explicit "SKIP STEP 4" branch |
| `restored` | restore exited 0 | committed | 2 checksums → schema grants → runtime grants → verify privileges → verify inventory |
| `schema_grants_applied` | schema grants exited 0 | committed, runtime role holds nothing (the N-20 state) | runtime checksum → runtime grants → verify privileges → verify inventory |
| `grants_applied` | runtime grants exited 0, or no runtime role | committed and granted; a verification failed | verify privileges → re-apply both grant files *only if* that showed loss → verify inventory → an explicit statement about what a still-differing inventory means |
| `verified` | step 6b passed | correct | **no banner** |

The post-fix emission for Codex's own case, at `schema_grants_applied`:

```
Recovery procedure, in this order:

  1. sha256sum --check '…/runtime-grants.sql.sha256'
  2. psql --dbname=freedom_test -v ON_ERROR_STOP=1 -f '…/runtime-grants.sql'
  3. Verify the restored privileges before declaring recovery complete:
       psql … -f '…/grants-inventory.sql' >'…/grants-after-recovery.txt'
       comm -23 <(sort '…/grants-before.txt') <(sort '…/grants-after-recovery.txt')
  4. Verify the data inventory, which is the other half of what the drill
     verifies and is not implied by a restore command's exit status:
       psql … -f '…/inventory-query.sql' >'…/inventory-after-recovery.txt'
       diff -u '…/inventory-before.txt' '…/inventory-after-recovery.txt'
     Recovery is complete only when that also prints nothing.

Re-running this drill is NOT a recovery step: it would dump the database in the
state this failure left it in and destroy that state to prove a restore of it.
The data restore already committed here, so there is nothing a rebuild from
migrations would recover and it is not offered.
```

### Uncertainty is described, not resolved by assumption

`restore_attempted` is the one genuinely uncertain outcome and it is reported as
uncertain. The banner states that `--single-transaction --exit-on-error` rolls
the whole restore back on an ordinary error — which leaves the database empty —
but that a killed or crashed process is not an ordinary error and the script
cannot tell the two apart from the outside. Its **step 0** is the query that
settles it, with three named outcomes: empty (continue at step 1), unchanged
inventory (skip the restore, continue at the grants), anything in between
(partial; neither resuming nor repeating is safe, and the procedure does not
choose).

### No destructive reset was added (item 2)

`test_no_recovery_path_prescribes_an_unrequested_destructive_reset` asserts, over
all four reachable failure stages, that no emitted banner contains `DROP SCHEMA`,
`DROP DATABASE`, `--clean`, `-c ` or `TRUNCATE`. Where a clean retry would be
needed — a data inventory that still differs after a committed restore — the
banner says what that means and says explicitly that resetting the schema
destroys what the restore put back, that it is an operator decision, and that the
procedure does not make it.

### Artifacts, verification and the zero-role case (items 3 and 4)

The pre-destruction dump, schema-grants and runtime-grants artifacts and their
checksums are unchanged, as is the validated role identity being substituted
before the destroy. Two artifacts are added so the **data** half can be verified
and so `restore_attempted`'s step 0 has a query to run:

* `inventory-query.sql` — the same table/row query steps 3 and 6 run, written out
  for the same reason `grants-inventory.sql` already was; and
* `inventory-after-recovery.txt` — where the recovery writes its comparison.

`row_counts()` now runs that file, so the recovery re-runs *the same query* the
drill runs rather than a paraphrase of it. Every stage's procedure ends in both
verifications, asserted as an ordering by
`test_every_emitted_recovery_procedure_ends_in_both_verifications`. A verification
failure cannot become a success: `grants_applied` is a failure stage and prints a
banner, and its text says that a restore command's exit status is not a
substitute for the comparison.

The zero-runtime-role case is printed explicitly at every stage that can reach
it, and the drill writes no `runtime-grants.sql`. `schema_grants_applied` is
unreachable without a runtime role — there is no runtime-grant step to fail — and
`test_the_zero_runtime_role_path_skips_the_runtime_grant_stage_entirely` asserts
that rather than leaving it an unexplained gap.

### Documentation (item 5)

`docs/operations/database-development.md` carries the stage table, the resume
point for each stage, step 0 and its three outcomes, both verification commands,
the two new artifacts, the statement that the `pg_restore` line is not run again
at any stage where the data committed, and the statement about what a
still-differing inventory means. The runtime-role section additionally documents
the new transport and the unreadable-report refusal.
`test_recovery_instructions_match_database_development_documentation` was extended
to hold both documents to all of it.

### Regressions added (item 6)

The stub boundary is now **stateful**: it records that `DROP SCHEMA` has been
issued, so an observation taken after the destroy can differ from the same
observation before it. Failure is injected by artifact, so each stage is reached
exactly.

| Test | What it establishes |
|---|---|
| `test_a_restore_that_did_not_report_success_is_described_as_uncertain` | the uncertain wording, step 0 before the restore, and the "SKIP STEP 4" branch |
| `test_a_schema_grant_failure_after_a_committed_restore_does_not_restore_again` | stage `restored`: the log shows a successful `pg_restore`, and the procedure contains none |
| `test_a_runtime_grant_failure_resumes_at_the_runtime_grants` | **Codex's reproduction**: stage `schema_grants_applied`, no restore and no schema-grant re-application in the procedure |
| `test_a_verification_failure_is_not_answered_by_repeating_the_restore` (2) | both of the drill's own verifications, at stage `grants_applied` |
| `test_no_recovery_path_repeats_a_data_restore_it_knows_committed` (4) | the acceptance condition over every stage |
| `test_no_recovery_path_prescribes_an_unrequested_destructive_reset` (4) | no destructive reset anywhere in any banner |
| `test_every_emitted_recovery_procedure_ends_in_both_verifications` (4) | privileges then inventory, as an ordering |
| `test_the_zero_runtime_role_branch_is_stated_at_every_stage_it_reaches` (3) | the zero-role branch, at each reachable resume point |
| `test_the_zero_runtime_role_path_skips_the_runtime_grant_stage_entirely` | why the fourth stage is absent above |
| `test_a_refusal_before_the_destroy_still_prints_no_banner_at_all` | the `intact` stage stays silent — DS-R8-2 is not reintroduced |
| `test_a_successful_drill_prints_no_banner` | the `verified` stage |
| `test_each_stage_is_recorded_only_after_its_command_succeeded` | the ordering of every stage assignment, at the source |

Every assertion is over the **emitted sequence** — indices into the procedure
text — not over the presence of a filename.

### The PostgreSQL regression, written and **not executed** (item 7)

`test_the_post_restore_recovery_path_restores_grants_without_restoring_again`
copies the drill with its runtime-grant application replaced by a failing
command, so the data restore commits and the run stops at
`schema_grants_applied`. It asserts the stage sentence, that
`runtime_privilege_count` is `0` — the state the operator is actually in — and
that the emitted procedure contains no `pg_restore`. It then follows the printed
procedure exactly and asserts preserved rows, the restored privilege count, that
the runtime role can `SELECT` its tables and `INSERT` but not `UPDATE` an
append-only one, and that **both** printed verifications print nothing. Against
the pre-fix banner it fails at the first mutation step, because that banner began
with the restore and it aborts on the objects already there. Deselected; see §6.

### Acceptance

The documented recovery path resumes from each tested stage without a redundant
data restore and without an unrequested destructive reset. The remaining
uncertainty — `restore_attempted` — is stated in the banner rather than assumed
away, and the unexecuted database checks are named in §6.

---

## 3. PR-20260907-R2-3 — Important: collapsed untracked directories bypassed the guard

### The finding, conceded

`git status --short` collapses a *wholly untracked* directory to one
trailing-slash entry. The allowlists declared those entries, so the guard
accepted `tools/phase_5_0_evidence/` and never inspected a single file inside it.
This is N-27's and N-30's failure class again: a guard that cannot see a file
cannot report that it is not seeing it — it passes, which reads like the file
being declared.

### Pre-fix evidence

The guard module was loaded, its evidence-harness allowlist restored to its
pre-fix contents (the two collapsed entries present, the six files they hid
absent), and its own `status_paths()` / `scope_violation()` run over both status
forms:

```
git status --short: 0 violation(s)
git status --short --untracked-files=all: 6 violation(s)
    tools/phase_5_0_evidence/binding.py
    tools/phase_5_0_evidence/case_runtime.py
    tools/phase_5_0_evidence/execution/case_program.py
    tools/phase_5_0_evidence/execution/materializer.py
    tools/phase_5_0_evidence/expectations.py
    tools/phase_5_0_evidence/materialization.py
```

Exactly the six the finding names.

### The correction (items 1–3)

1. **Discovery enumerates files.** `working_tree_paths(root)` runs
   `git status --short --untracked-files=all` and is extracted as a function, so
   the discovery itself can be exercised against a synthetic repository rather
   than only against whatever this worktree happens to hold. Tracked
   modifications and renames are covered exactly as before — `status_paths()` is
   unchanged, and its seven parsing cases still pass.
2. **The escape hatch is removed, not left unused.** Three directory entries are
   withdrawn: `tools/phase_5_0_evidence/`,
   `tools/phase_5_0_evidence/execution/` and `adapters/ledger/`.
   `test_no_production_allowlist_entry_is_a_directory` asserts that no entry in
   any of the five production allowlists ends in `/`, so the hatch cannot return
   quietly if the discovery is ever changed back.
3. **The six are declared individually, with their scope rationale.** Each is a
   **covered source in `docs/review/phase-5-0-evidence-harness-review-manifest.json`**,
   which pins its SHA-256 and is the artifact under review, and each is described
   in the R13 implementation handback:

   | File | Revision and role |
   |---|---|
   | `binding.py` | R11 conflict C-5: the four disposable names, their declared substitution sites, and the rule that nothing else in a reviewed vector may change |
   | `case_runtime.py` | R11 conflict C-2, Option B: the named-interpreter vector and the closed grammar for what may follow it |
   | `expectations.py` | R12/R13: the typed, closed semantic expectation contracts |
   | `materialization.py` | R11 conflict C-4: the closed table of every byte sequence the harness may put on disk |
   | `execution/case_program.py` | C-2's payload: the single-file reviewed case program |
   | `execution/materializer.py` | C-4's writing half |

   All 28 manifest-covered sources were re-hashed from this tree against the
   manifest with **no mismatch** (§7), so the declaration reconciles against the
   submission rather than against an assertion. **This prompt is not treated as
   authority for new production modules**: nothing was added, and the six were
   already in the submitted, reviewed set.
4. **The separate allowlists and watched prefixes are unchanged.** `tools/` is
   still watched in full; nothing was added to `UNPOLICED_WITHIN_WATCHED`; the
   five allowlists remain disjoint. The pre-existing narrowness tests still pass,
   including the seven synthetic `tools/` paths that must be refused.

### Regressions added (items 4 and 5)

| Test | What it establishes |
|---|---|
| `test_the_discovery_enumerates_untracked_files_rather_than_directories` | over **this** tree: the discovery hands the guard no directory, and the default form really does still collapse one — so the switch is not a no-op here |
| `test_every_evidence_harness_source_in_the_tree_is_declared` | the reconciliation in both directions: no module present but undeclared, no entry declared but absent |
| `test_the_discovery_finds_a_file_inside_an_untracked_directory` | **item 4**: a synthetic temporary Git repository with a nested untracked directory and one undeclared source file. It asserts the default form collapses it to `tools/`, that the real discovery path yields the file, and that `scope_violation` then rejects exactly it |
| `test_the_reviewed_file_set_passes_and_one_more_file_does_not` | **item 5**: a synthetic repository holding the exact declared file set, all untracked, produces **no** violation; adding one more module inside the same package produces exactly one, named |
| `test_no_production_allowlist_entry_is_a_directory` | the hatch is gone from all five lists |

No synthetic unauthorized file was written into this worktree: both synthetic
tests build a **separate** repository under `tmp_path`.

### Acceptance

The guard's result no longer depends on git collapsing an untracked directory,
and the exact submitted source files are accounted for — 28 declared, 28 present,
28 manifest digests verified.

---

## 4. What was preserved

* **The R13 evidence harness.** No production source under
  `tools/phase_5_0_evidence/` was modified in this revision. All 28 covered-source
  digests match the manifest, so the generated artifacts were left untouched and
  the R13 digest carried forward from the previous remediation stands.
* **The previous remediation.** PR-20260907-1's pre-destruction artifacts,
  checksums, single rendered grant file, N-20 privilege comparison and
  zero-role statements; PR-20260907-2's identity-preserving contract, its
  keyword/special-role/`pg_` list and its refusal placement; PR-20260907-3's
  strict capture policies — all unchanged. `capture.py` was **not** touched.
* **The drill's connection gates.** 0a through 0e, the staging double signal, the
  production refusal and the DS-R8-2 accuracy corrections, unchanged.
* **Every execution restriction.** No `--execute`, no armed process boundary or
  materializer, no generated vector, no SSH, no target-host inspection or
  mutation, no database operation, no destructive drill, no deployment, no
  migration `0014`, no cutover, no OD-62 ruling, no Package 5.1+ work. No stub
  test falls through to a real PostgreSQL client: every stub run replaces `psql`,
  `pg_dump` and `pg_restore` on `PATH` and the drill's own gate 0e is answered by
  the stub.
* **Every unconfirmed interpreter and `E7` target fact is still unconfirmed.**
* **Unrelated worktree changes.** The live-bot skills fix
  (`models/skills.py`, `tests/test_skills.py`), the updated agent instructions,
  the prior handbacks and every other pre-existing modification and untracked
  file are as they were. Nothing was reset, reverted, staged, committed, pushed
  or reformatted.

## 5. Files changed

| File | Change |
|---|---|
| `infra/postgresql/backup-restore-drill.sh` | R2-1: the `ROLE`/`END` transport query, `decode_hex_role`, the strict report reader, `refuse_runtime_report`, hex-encoded multiple-role diagnostics. R2-2: `DRILL_STAGE` replacing `SCHEMA_DROPPED`, the stage assignments, `inventory-query.sql`/`inventory-after-recovery.txt`, `row_counts` reading the file, and `on_exit` rewritten as five stage-specific procedures. Header exit-code and failure-atomicity comments updated for both |
| `docs/operations/database-development.md` | the transport and the unreadable-report refusal in the runtime-role section; the recovery section rewritten around the stage table, step 0, per-stage resume points, both verifications and the two new artifacts |
| `tests/test_database_backup_restore.py` | the stateful stub with five injection points and the encoded report; `encoded_role_report`, `_role_report_sql`, `_procedure`, `STAGE_INJECTIONS`; **59 new stub cases** across R2-1 and R2-2; two new PostgreSQL regressions (deselected); six existing tests updated for the changed diagnostics, source anchors and stub substitutions |
| `tests/web/test_p3_4_static_assets.py` | R2-3: `working_tree_paths` with `--untracked-files=all`; the three directory entries withdrawn; the six modules declared with rationale; five new tests including two synthetic-repository regressions |
| `docs/review/project-review-remediation-2026-09-07-r2-handback.md` | this file |
| `docs/review/Handover information` | dated pointer to this handback |

No file under `tools/`, `application/`, `domain/`, `adapters/`, `models/`,
`ext/`, `migrations/` or `foundry-module/` was modified.

## 6. Verification

### The environment, and what it is not

`.agents/AGENTS.md` documents the test environment as `oracle-test`, with
`/opt/freedom-blades/runtime/venv-web/bin/python` as the interpreter for both
suites. **That environment was not used and could not be**: this prompt retains
the no-SSH restriction, so `oracle-test` was not contacted at all. On this host
`/opt/freedom-blades/runtime/venv-web` exists and is the **runtime** environment —
`import pytest` fails with `ModuleNotFoundError` — and installing pytest into it
would be installing into a production runtime, which the prompt forbids.

The permitted local environments used are `/opt/discord-bots/venv` and
`/opt/discord-bots/venv-web`, both CPython 3.12.3 with pytest 8.4.2. **Every
figure below is from this host, not from `oracle-test`.**
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` was exported for every
run. No historical `/opt/discord-bots/` path was copied from an old handback as
*the documented* environment; it is named here as what was actually run.

### Results, run serially against the final tree

| # | Command | Result |
|---|---|---|
| 1 | `venv … pytest -q tests/phase_5_0_evidence` | **1143 passed** |
| 2 | `venv-web … pytest -q tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py` | **1208 passed** |
| 3 | `venv … pytest -q -rs tests/test_database_backup_restore.py tests/test_filesystem_layout.py` with the eleven deselected | **147 passed, 11 deselected** |
| 4 | `venv … pytest -q -rs tests/test_*.py` with the same eleven deselected | **3244 passed, 11 deselected**, 1 warning (`audioop` deprecation, pre-existing) |
| 5 | `venv-web … pytest -q -rs tests/web` | **2846 passed, 80 skipped** — the documented figure |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `venv … -m compileall -q` over the two changed test modules and `tools/phase_5_0_evidence` | clean |
| 7 | `venv-web … -m compileall -q` over the same paths | clean |
| 7 | `bash -n infra/postgresql/backup-restore-drill.sh` | clean |
| 8 | `git diff --check` | clean |

**The two suites were run one at a time, with nothing else running**, and `pgrep`
was used to confirm that before each. The previous handback reported a concurrent
run as a deviation; it did not recur.

The evidence suite is **unchanged at 1143** — no evidence-harness source or test
was touched. Run 2 went 1202 → **1208**: the five new scope-guard tests and one
net new parametrization. The backup/layout selection went 88/9 → **147/11** and
the bot suite 3185 → **3244**: 59 new stub cases, and the two new PostgreSQL
regressions joining the deselected set. The web suite went 2840 → **2846**, the
same six.

**The web suite's 80 skips are the documented figure**, and `-rs` printed the
reason for each: 54 in `tests/web/test_p3_2_matrix.py:155` and 26 in
`tests/web/test_p3_3_matrix.py:198`, both *"permitted cells are asserted by the
per-route success cases"*. **No skip is an environment gate.**

### Pre-fix failure record

Recorded before the corrections, in three forms.

1. **The R2-1 reproduction table** in §1, against the reconstructed pre-fix
   script in its own transport. Five rows are Codex's; two more are additional.
2. **The R2-2 reproduction** in §2, the runtime-grant failure after a committed
   restore, showing the emitted procedure beginning at the full restore.
3. **The whole regression module against the pre-fix script and the pre-fix
   operations guide: 94 failed, 48 passed, 11 deselected.** This figure needs one
   statement to be read correctly, and it is not a caveat added afterwards: the
   run uses the **corrected stub**, which speaks the new transport, so its
   failures include existing tests that fail because the pre-fix script cannot
   read a report in that shape. The behavioural pre-fix evidence is (1) and (2),
   which use the pre-fix wire format and are therefore comparable.
4. **The R2-3 comparison** in §3: 0 violations under the default status form,
   6 under `--untracked-files=all`, with the pre-fix allowlist in place.

The pre-fix script and guide were reconstructed by reversing this session's edits
and **self-checked by round trip**: re-applying the same edits to the
reconstruction reproduces the current file byte for byte. The fixed files were
restored afterwards and `cmp`-verified byte-identical against snapshots taken
before the swap.

### Deselected: eleven cases, by name

The nine from the previous submission, plus the two this correction adds. All are
in `tests/test_database_backup_restore.py`:

1. `test_the_drill_accepts_an_explicit_unix_socket_directory`
2. `test_backup_and_restore_round_trip_preserves_data`
3. `test_the_drill_leaves_the_runtime_roles_privileges_intact`
4. `test_the_drill_fails_when_the_privilege_state_is_not_restored`
5. `test_the_drill_preserves_pristine_schema_ownership_and_privileges`
6. `test_the_drill_fails_when_schema_privileges_are_not_restored`
7. `test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure`
8. `test_the_documented_recovery_procedure_restores_runtime_table_grants`
9. `test_a_role_whose_sql_identity_differs_refuses_against_postgresql`
10. `test_a_newline_bearing_role_refuses_against_postgresql` *(new)*
11. `test_the_post_restore_recovery_path_restores_grants_without_restoring_again` *(new)*

**None of the eleven is claimed to pass against this tree.** Cases 4, 6 and 7
assert literal fragments of the drill script or its banner; those literals were
checked against the corrected script so an authorized run exercises the current
code rather than failing stale, and cases 10 and 11 have never run. **Case 5's
previously undiagnosed failure remains undiagnosed**: it was not re-run, and no
stub result here is offered as its explanation.

### Checks not run, and why

| Not run | Reason |
|---|---|
| The eleven deselected cases above | destructive drill / cluster-role creation; the prompt forbids them here |
| Anything on `oracle-test` | the no-SSH restriction; the documented environment is unreachable under this authority |
| The bot and web suites **under the documented `oracle-test` interpreter** | same; runs 4 and 5 are this host's local interpreters and are labelled as such |
| Re-running the pristine-schema drill to diagnose the outstanding failure | it is a destructive drill; the prompt forbids it and says so explicitly |
| The evidence harness itself | no `--execute`, no armed boundary or materializer, no generated vector; unchanged from R13 |
| Any privileged or mutation-bearing command from the plan | all 43 mutations and 46 cleanup steps remain reviewed argument vectors |
| A configured formatter, linter or type checker | **none is configured in this repository**: there is no `pyproject.toml`, `ruff.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `.pre-commit-config.yaml`, and `pytest.ini` is the only tool configuration present. `shellcheck` is not installed on this host. `compileall`, `bash -n` and `git diff --check` are what is available and were run |

## 7. Generated artifacts

**No evidence-harness production source changed in this revision**, so the prompt's
first branch applies: the manifest was verified and the generated artifacts were
left untouched.

| Fact | Value |
|---|---|
| Covered sources re-hashed from this tree | **28** |
| Digest mismatches against `source_digests` | **0** |
| Manifest schema version | **5**, unchanged |
| Harness version | **0.6.0-pre-execution**, unchanged |
| Review-manifest digest recorded in the concrete plan | `d91e996977d91bbd6229fa0311df46ff13494611cb6cdd8a4234a077ded9e402`, unchanged |
| Superseded R13 digest, never to be passed to `--execute` | `057c84a96225bfb8e1b02f4502619015b06b8dbc050342423ade25be4f3b7ae5` |

The digest is a function of the plan the covered sources produce plus the
serialized manifest body; with all 28 digests verified unchanged, it does not
move. Neither artifact was regenerated and neither was hand-edited. **No digest
was passed to `--execute`**, and the digest above remains **review material only,
not execution authority**: the executor still refuses this plan on twelve
unsupplied reviewed target facts whatever digest it is given.

## 8. Status, and what this does not claim

* **PR-20260907-R2-1: remediated.** Record cardinality and exact identity survive
  the transport; the supported-role contract is unchanged and applied to the
  catalog bytes; unreadable transport and client failure refuse with fixed text
  and are never read as zero roles.
* **PR-20260907-R2-2: remediated.** Completion state advances only on success;
  each stage emits its own resume point; no path repeats a committed data
  restore or prescribes an unrequested destructive reset; both verifications are
  required before recovery is complete; the one uncertain outcome is described as
  uncertain.
* **PR-20260907-R2-3: remediated.** Discovery enumerates individual untracked
  files, the collapsed-directory entries are withdrawn from all five production
  allowlists, and the six previously hidden files are declared and reconciled
  against the review manifest.
* **Package 5.0 remains `not ready`. P5.0-R5 remains Blocking.** No finding,
  assumption, decision, residual risk or gate is closed. No roadmap, RAID,
  decision or gate record was altered. **R13 has not received complete
  independent pre-execution approval**, and nothing here implies one.
* This submission does not claim the eleven deselected cases pass, does not claim
  any figure from the documented `oracle-test` environment, does not confirm any
  reviewed target fact, and does not resolve the outstanding pristine-schema
  drill failure.

## 9. Request

Please re-review these three corrections, and in particular:

1. **the transport contract** — whether `ROLE <hex>` / `END <count>` with strict
   decoding is the right shape, whether refusing an unreadable report with exit
   `2` is the right classification, and whether the hex-only multiple-role
   diagnostic loses anything an operator needs;
2. **the stage boundaries** — whether `destroyed` being set *before* the destroy
   is the right exception, whether `restore_attempted`'s step 0 is the right way
   to handle an uncertain restore, and whether `grants_applied` should offer more
   than a repair and a statement;
3. **the scope-guard reconciliation** — whether the six files' rationale is
   adequate, and whether withdrawing `adapters/ledger/` alongside them is in
   scope or should be raised separately;
4. **the pre-fix figure in §6 item 3** and whether its stated limitation is
   acceptable evidence; and
5. **the two new PostgreSQL regressions**, as the authorized run's specification.

The outstanding operational items are unchanged: the twelve reviewed target
facts, the eleven deselected database cases, the undiagnosed pristine-schema
drill failure, and whatever remains of the R13 pre-execution review.
