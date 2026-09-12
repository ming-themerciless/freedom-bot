# Project review remediation R3, 2026-09-08 — implementation handback

Date: 2026-09-08

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: `docs/review/project-review-remediation-2026-09-08-r3-claude-prompt.md`.
That prompt authorizes a **bounded correction of the backup/restore drill, its
recovery documentation, and the production-file scope guard**, and nothing else.
It is not Package 5.0 product implementation and it is not complete R13
pre-execution approval.

Outcome: **PR-20260908-R3-1, PR-20260908-R3-2 and PR-20260908-R3-3 are
remediated.** The R1/R2 corrections, the live-bot skills fix and the current R13
evidence harness are preserved; no evidence-harness production source changed.
Package 5.0 remains `not ready`; P5.0-R5 remains Blocking. No assumption,
decision, residual risk or gate closes through this work, and no earlier finding
ID is touched or closed.

**The undiagnosed pristine-schema drill failure reported in the 2026-09-07
handback (§6, case 5) remains unresolved.** It was not re-run here, and nothing
below is offered as its diagnosis or resolution.

---

## 1. PR-20260908-R3-1 — Blocking: a failed DROP was reported as a known empty database

### The finding, conceded

`DRILL_STAGE="destroyed"` was assigned *before* the destructive command, with the
script's own comment calling it "the deliberate exception" because a failure
inside `DROP SCHEMA` leaves an unknown state.

The reasoning was sound and the conclusion was not. **The `destroyed` banner does
not describe an unknown state.** It asserts that the schema was dropped, that the
database is `EMPTY`, and it directs a full `pg_restore`. A command that was
refused, that never ran, or whose result was lost establishes none of that — and
the schema may be exactly as it was.

Worse, the test suite made the defect *mandatory*:
`test_each_stage_is_recorded_only_after_its_command_succeeded` asserted
`destroyed < drop`, so a correction would have failed the regression written to
protect the previous one.

### Pre-fix evidence, reproduced before anything was corrected

Codex's reproduction exactly: the existing stub helper, with only the stub's DROP
branch changed to emit a fixed error and exit 42 **without changing its state
file**. Nothing else about the boundary was altered, and no database was
contacted.

```
exit: 42
pg_restore called: False
--- stub invocation log (abbreviated) ---
  psql        -c SELECT current_database() …           (gate 0e)
  pg_dump     --format=custom --dbname=freedom_test …
  psql        -f …/inventory-query.sql
  psql        -f …/grants-inventory.sql
  psql        (runtime-role report)
  psql        (schema grants)
  psql        -c DROP SCHEMA public CASCADE; CREATE SCHEMA public;   <- exit 42
--- emitted recovery banner ---
RECOVERY REQUIRED.

The schema of 'freedom_test' was dropped and the data restore had not started,
so the database is EMPTY. …

Recovery procedure, in this order:
  1. sha256sum --check '…/freedom_test.dump.sha256'
  2. sha256sum --check '…/schema-grants.sql.sha256'
  3. sha256sum --check '…/runtime-grants.sql.sha256'
  4. pg_restore --dbname=freedom_test --no-owner --no-privileges --single-transaction …
  …
```

The drill exited 42, never called `pg_restore`, and still claimed
`the database is EMPTY` and prescribed `4. pg_restore …`. **This was a stub
reproduction, not a PostgreSQL execution.**

### The correction — responsibility before the command, knowledge after it (item 1)

Two stages replace one:

| Assignment | Placed | What it claims |
|---|---|---|
| `DRILL_STAGE="destroy_attempted"` | **before** `DROP SCHEMA` | *responsibility*: from here on this drill may have destroyed something and must say so whatever happens. It claims **no** knowledge about the schema. |
| `DRILL_STAGE="destroyed"` | **after** the command succeeds | *knowledge*: the schema is dropped, recreated and empty; the data restore has not started. |

Moving the assignment after the command **without** an attempted state was
explicitly insufficient and was not done: a lost client result would then have
left `DRILL_STAGE="intact"`, which prints no banner at all and would have treated
a lost result as proof that nothing happened. `destroy_attempted` is exactly that
missing state.

There is now **no exception** to the rule that a stage records a success.
`test_each_stage_is_recorded_only_after_its_command_succeeded` was rewritten:
the assertion `destroyed < drop` — the one that made the defect mandatory — is
replaced by `attempted_destroy < drop < destroyed`, and the docstring says why.

### Safe state inspection before any recovery choice (item 2)

The `destroy_attempted` banner prescribes **no change to the database at all**
until a read-only step 0 has established the state. Two reports are compared
against baselines written before the destroy:

* `inventory-query.sql` against `inventory-before.txt` — the table/row inventory
  the drill itself compares in step 6; and
* **`schema-state.sql` against `schema-state-before.txt` — new for this finding.**
  A row-count match alone does not distinguish every schema state, so a
  structural report is captured too:

  ```sql
  SELECT 'schema_present=' || (to_regnamespace('public') IS NOT NULL)::text
      || '|relations='    || (relations of any kind in public)::text
      || '|base_tables='  || (base tables in public)::text;
  ```

  `to_regnamespace` returns NULL rather than raising when the schema is absent,
  so "no `public` at all" is distinguishable from "a `public` holding nothing";
  and the relation count covers views, sequences and indexes, so a schema still
  holding objects cannot report itself empty merely because there were no base
  tables.

The four states the finding names, and the fifth non-answer, each have a stated
outcome in the banner and in the operations guide:

| Reported state | Banner's answer |
|---|---|
| either command failed | **the state is still not known.** "A query that did not run is not evidence that the schema is empty." Repeat step 0; restore, drop and truncate nothing. |
| both diffs print nothing | **the schema is intact.** The destroy did not take effect, nothing was lost, **no recovery is required**, and the restore must *not* be run over it. |
| `schema_present=true`, `relations=0`, baseline recorded relations | **dropped and recreated, empty** — the `destroyed` state. Continue at step 1. |
| `schema_present=false` | **absent.** No restore or grant can run into a schema that does not exist, and recreating one is a deliberate change *this procedure does not make*. Stop; resolve with an operator. |
| anything else | **unexpected.** Neither restoring over it nor resetting it is safe, and the procedure **does not choose between them**. Stop; resolve with an operator. |

**The case a row count cannot decide at all is stated rather than left implicit.**
If the baseline itself records `relations=0` — the original database had no
objects — an intact schema and a recreated one produce the same empty inventory
and *cannot* be told apart by these reports. Both documents say so, and both say
what follows: nothing was lost either way, no data restore is required, and the
operator goes to the grant re-application and the two verifications.

### No mutation on a false premise, and no destructive reset (item 3)

No full restore is prescribed over known existing objects: at
`destroy_attempted` the restore is step 4, reachable only through the step-0
outcome that establishes an empty recreated schema, and the "intact" outcome says
`Do not restore over it`. No `DROP`, `--clean`, `TRUNCATE` or other destructive
reset was added —
`test_no_recovery_path_prescribes_an_unrequested_destructive_reset` now runs over
**five** stages including this one. Two outcomes end in "stop and resolve it with
an operator" rather than in a mutation.

The re-run/rebuild fallback is stage-specific too. At `destroy_attempted` neither
is offered while the state is unknown: re-running the drill "would dump the
database in whatever state it is actually in and then destroy that state", and
rebuilding from migrations "would replace a schema that may be completely
intact". The rebuild is named only as what applies *after* step 0 establishes
that the schema really was dropped **and** the dump turns out to be unusable.

### What was preserved (item 4)

`restored`, `schema_grants_applied` and `grants_applied` are unchanged, and their
banners still contain no `pg_restore` at all — a confirmed restore is never
repeated during grant recovery. Both final verifications (privileges, then the
data inventory) still terminate every emitted procedure. The pre-destruction
checksummed artifacts, the exact validated runtime role rendered before the
destroy, and the explicit zero-runtime-role statements are untouched;
`test_the_zero_runtime_role_branch_is_stated_at_every_stage_it_reaches` now
covers `destroy_attempted` as well.

### Stub boundary and regressions (item 5)

The stub `psql` gained two independent parameters, and their independence is the
point: `destroy_exit` says whether the command reports success, `destroy_applied`
says whether the schema was really dropped, and **the drill cannot see the
second**. Both failing outcomes are therefore produced behind one identical exit
status.

| Test | Cases | What it establishes |
|---|---:|---|
| `test_a_failed_destroy_is_never_described_as_a_known_empty_database` | 2 | the finding: no `EMPTY` claim, for a refused DROP *and* for a lost result |
| `test_a_failed_destroy_prescribes_no_mutation_before_the_state_is_known` | 2 | an ordering over the emitted procedure: both read-only reports precede the restore, which precedes both grant applications |
| `test_the_failed_destroy_banner_accounts_for_every_schema_state` | 2 | all four states, the failed-query non-answer, and the relations=0 ambiguity |
| `test_the_failed_destroy_banner_names_the_two_state_artifacts` | 2 | both are on disk, named by absolute path, and the baseline records the real pre-destruction state |
| `test_the_printed_state_report_distinguishes_the_two_failed_destroys` | 1 | **step 0 demonstrated**: the printed command is run through the same boundary for both scenarios and returns `relations=1` versus `relations=0` |
| `test_a_successful_destroy_still_reports_a_known_empty_database` | 1 | **positive control**: a destroy that reports success is not turned into an uncertainty |
| `test_the_schema_state_baseline_is_recorded_before_the_destroy` | 1 | step 3a runs on the normal path, and the log shows it issued before the drop |
| `test_the_failed_destroy_offers_neither_a_rerun_nor_a_rebuild` | 1 | the fallback text, and why each is withheld |
| `test_each_stage_is_recorded_only_after_its_command_succeeded` | 1 | **rewritten**: the mandatory-defect assertion is gone |
| four existing stage parametrizations | +4 | `destroy_attempted` added to `STAGE_INJECTIONS`, so the no-repeat, no-destructive-reset, both-verifications and zero-role assertions all cover it |

Every assertion is over the **emitted sequence and its state claims** — indices
into the procedure text and the sentences themselves — not over the presence of a
banner or of a filename.

### Documentation (item 6)

`docs/operations/database-development.md` carries the new stage row, a paragraph
stating the `destroy_attempted`/`destroyed` distinction and the finding, a step-0
section with the five-row outcome table, the relations=0 ambiguity, the two new
artifacts in the artifact table with what each carries and why the recovery fails
without it, and the qualification that the full procedure at `destroy_attempted`
runs **only** after step 0 establishes an empty recreated schema. A stale
reference to the withdrawn `SCHEMA_DROPPED=1` flag was corrected to
`DRILL_STAGE="destroy_attempted"` in the DS-R8-2 paragraph.
`test_recovery_instructions_match_database_development_documentation` was
extended to hold both documents to all of it.

**No new database-semantic regression was written for this finding and none was
executed.** The stage table, the banner and the guide are what changed; the
existing PostgreSQL cases that exercise the destroy remain deselected.

### Post-fix, the same reproduction

```
DROP refused, schema intact (Codex's reproduction)  exit=42  pg_restore called=False
DROP applied, client result lost                    exit=42  pg_restore called=False

RECOVERY REQUIRED.

The destroy command for 'freedom_test' ran and did not report success, so WHAT THE
SCHEMA NOW HOLDS IS NOT KNOWN. This drill does not call the database empty here.
A command that was refused, that never ran, or whose result was lost proves
nothing about the schema, and the schema may be exactly as it was before this
drill started. Step 0 below establishes which state it is actually in, and
nothing in this procedure changes the database until it has.
…
Recovery procedure, in this order:

  0. Establish the state of the schema before choosing anything. Both reports
     are read-only and neither changes the database:
       psql … -f '…/schema-state.sql'    >'…/schema-state-after-recovery.txt'
       diff -u '…/schema-state-before.txt' '…/schema-state-after-recovery.txt'
       psql … -f '…/inventory-query.sql' >'…/inventory-after-recovery.txt'
       diff -u '…/inventory-before.txt'  '…/inventory-after-recovery.txt'
     * EITHER COMMAND FAILED: … A query that did not run is not evidence that
       the schema is empty. …
     * BOTH DIFFS PRINT NOTHING: THE SCHEMA IS INTACT. … NO RECOVERY IS REQUIRED.
       Do not restore over it …
     * schema_present=true with relations=0 … That is the 'destroyed' state.
       Continue at step 1.
     * schema_present=false: the schema is ABSENT. … Stop here and resolve it
       with an operator.
     * ANYTHING ELSE … this procedure does not choose between them. Stop here …
  1. sha256sum --check '…/freedom_test.dump.sha256'
  …
```

Both failing outcomes emit the same banner, because the drill genuinely cannot
tell them apart; the printed step 0 is what does, and it was run through the same
boundary to show it (`relations=1` versus `relations=0`).

### Acceptance

No failed or uncertain destructive command is described as proven empty, and no
recovery path recommends a mutation on that premise.

---

## 2. PR-20260908-R3-2 — Important: hex decoding dropped NUL bytes

### The finding, conceded

`decode_hex_role()` accumulates bytes with `printf -v piece '%b'` into a Bash
string, and **a Bash string cannot hold a NUL**. So a transported `00` did not
arrive as a byte the supported-name guard could refuse. It vanished, and the
shorter name that remained reached the guard already looking supported.

### Pre-fix evidence, reproduced before anything was corrected

Codex's report supplied verbatim through `report_override`, with two controls:

```
case                                           exit   DROP  restore  grant rendered
NUL-bearing 'freedom_runtime_test\x00'            0   True     True  freedom_runtime_test
valid control 'freedom_runtime_test'              0   True     True  freedom_runtime_test
newline control 'freedom_runtime_test\n'          2  False    False  absent
```

Exactly the reported behaviour: exit 0, both `DROP SCHEMA` and `pg_restore` in
the stub log, and a grant naming a role the catalog does not hold. The
newline-bearing control still refused before `DROP`, so R2's correction was
intact and this was a distinct loss.

### The correction — refused before the decode (items 1 and 3)

A PostgreSQL `name` is NUL terminated and cannot contain one, so such a record is
**malformed transport**, not a role identity — and R2 already requires malformed
transport to refuse without identity repair. The check therefore joins the other
transport checks and refuses the *report*:

```sh
hex_record_contains_nul() {
  local hex="$1"
  while [[ -n "${hex}" ]]; do
    if [[ "${hex:0:2}" == "00" ]]; then return 0; fi
    hex="${hex:2}"
  done
  return 1
}
```

Called in the `ROLE` branch **after** the even-length lower-case hex check
(which is what makes a pair boundary well defined) and **before**
`decode_hex_role`, because a NUL inspected after the decode would be inspected in
a representation that no longer contains it — a check that exists and can never
fire, which is the DS-R8-1 shape.

**Whole byte pairs, not a substring search.** `4004` is `@` followed by `\x04`
and carries no NUL, while its *text* contains `00` spanning the two bytes. The
scan steps two characters at a time, so a boundary-crossing pair is not
misclassified.

It refuses through the existing `refuse_runtime_report` path: **exit 2, before
`DROP` and before the restore, with no runtime grants rendered**, and with fixed
diagnostics — `the runtime-role report could not be read` / `Reason: a role
record carried a NUL byte` — carrying no bytes from the report.

### The contract was not widened (item 2)

Nothing else changed. Exact identity, cardinality, the terminator rule and the
supported-role contract are untouched; `test_the_supported_role_contract_itself_
is_unchanged` still asserts the lower-case fold, `^[a-z_][a-z0-9_]{0,62}$`,
`is_reserved_role_spelling`, the special-role spellings and the `pg_` prefix at
the source. No name is trimmed, coerced or normalized, and no supported spelling
was added.

### Regressions added (item 4)

| Test | Cases | What it establishes |
|---|---:|---|
| `test_a_nul_bearing_record_refuses_before_any_destruction` | 8 | leading, trailing, embedded, repeated (adjacent, both ends, throughout), NUL-only and NUL-only-repeated — each exit 2, no `DROP`, no `pg_restore`, no rendered grant, no `runtime-grants.sql`, **no recovery banner** |
| `test_a_nul_bearing_record_is_not_repaired_into_a_supported_one` | 3 | the specific harm: the supported name the decode used to produce appears nowhere, including in the diagnostics |
| `test_a_nul_bearing_record_is_never_read_as_zero_roles` | 2 | `ROLE 00` decoded to the empty string, which is what a zero-row result also looks like; the empty path is not taken |
| `test_a_valid_record_beside_a_nul_bearing_one_still_refuses` | 2 | valid-then-NUL and NUL-then-valid: the whole report refuses and the valid name is not adopted |
| `test_a_boundary_crossing_zero_pair_is_not_mistaken_for_a_nul` | 3 | **the detector control**: `4004`, `700a` and a longer `…3001` refuse at the *role guard* with `is not a supported runtime role name`, and explicitly **not** with the NUL reason |
| `test_the_supported_names_are_unaffected_by_the_nul_check` | 2 | **positive control**: `freedom_runtime` and `freedom_runtime_test` still decode, reach step 5b and render their grants |
| `test_zero_roles_are_unaffected_by_the_nul_check` | 1 | `END 0` is still an answer, not a refusal |
| `test_the_nul_check_runs_before_the_decode_that_would_lose_it` | 1 | at the source: the ordering, the pair-stepping shape, and that it precedes `DRILL_STAGE="destroy_attempted"` |

The pre-existing newline/multiple-role refusals, the thirteen malformed-report
cases, the client-failure case and both zero-role positive controls all still
pass unchanged.

### Transport evidence and database-semantic evidence, kept apart (item 5)

Every case above is a **stub reproduction**. The report is computed in Python by
`encoded_role_report` / `report_override`, so these establish that the shell
refuses the record losslessly and before destruction, and establish **nothing**
about SQL semantics. **No PostgreSQL regression was added for this finding**, and
the reason is stated in the test module: a role name containing a NUL is not
something PostgreSQL can be asked to create, so a test purporting to do so would
be asserting a fiction.

### Post-fix, the same reproduction

```
case                                           exit   DROP  restore  grant rendered
NUL-bearing 'freedom_runtime_test\x00'            2  False    False  absent
valid control 'freedom_runtime_test'              0   True     True  freedom_runtime_test
newline control 'freedom_runtime_test\n'          2  False    False  absent
```

### Acceptance

An impossible NUL-bearing report cannot become an accepted role through lossy
decoding, and every previously supported input retains its behaviour.

---

## 3. PR-20260908-R3-3 — Important: human-readable Git parsing hid a watched file

### The finding, conceded

`status_paths()` treated every ` -> ` substring as a rename separator whatever the
status said, and stripped `"` characters from the ends of the result. Both are
guesses about a filename, and ` -> ` and `"` are legal in one.

### Pre-fix evidence, reproduced before anything was corrected

Codex's reproduction, using the guard's own functions against a temporary
synthetic Git repository:

```
raw git status --short --untracked-files=all:
    '?? "tools/extra -> outside.py"'
    '?? tools/extra.py'
working_tree_paths(repo) -> ['outside.py', 'tools/extra.py']
  scope_violation('outside.py')     -> None
  scope_violation('tools/extra.py') -> 'Unpermitted tools modification detected in working tree: tools/extra.py'
```

`['outside.py']` and `None`, exactly as reported, with the normal control
correctly rejected. The classification was sound; it was being handed a filename
that had been rewritten before it ever saw it — N-27's and N-30's failure class in
a third shape.

### The correction — machine-readable records (item 1)

Discovery now runs

```
git status --porcelain=v1 -z --untracked-files=all
```

read as **bytes** and decoded with `surrogateescape`, so a path that is not valid
UTF-8 round-trips instead of raising or being replaced. `parse_status_records`
reads documented fields:

* records are NUL delimited, and paths are emitted verbatim with no quoting or
  display escaping whatever bytes they contain;
* a record is `XY`, one space, then the path — sliced, never tokenized;
* a rename or copy is the documented **two-record** form: the entry `XY <new>`
  followed by a bare `<old>`, consumed together, and only when the status field
  actually carries `R` or `C`.

Nothing is split on an arrow, a newline or whitespace, and no quote character is
stripped. `--untracked-files=all` is retained unchanged from R2.

### Both rename endpoints, and copies handled explicitly (item 2)

`record_paths` is deliberately asymmetric, and the asymmetry is the reason each
is handled by name rather than by one rule:

* **a rename removes its origin.** Moving a watched production source out of a
  watched prefix deletes it, and reading only the destination would classify that
  as a change to the unwatched destination — the removal concealed by the move.
  Both endpoints reach the guard.
* **a copy leaves its origin exactly as it was.** Reporting it would assert a
  change to a file that did not change, which is the opposite error. Only the
  destination is reported; the origin record is still *consumed* as the second
  half of one entry rather than read as a status record of its own, which is what
  keeps the rest of the payload in sync.

Malformed or truncated records raise `MalformedStatusRecord` rather than being
skipped: a change that cannot be classified must not read as a change that is
permitted.

### What was preserved (item 3)

`scope_violation` is unchanged. The five production allowlists, the template
allowlist, `WATCHED_PRODUCTION_PREFIXES`, `UNPOLICED_WITHIN_WATCHED`,
`NON_PRODUCTION_DIRECTORIES` and the R2 reconciliation of the 28 evidence-harness
sources are all untouched. Nothing was broadened, no prefix was added, and no
unusual name was exempted — the parsing failure was fixed as a parsing failure.

### Regressions added (items 4 and 5)

| Test | Cases | What it establishes |
|---|---:|---|
| `test_the_record_parser_reads_each_status_form` | 15 | modified, staged-modified, added, untracked, both deletion forms, a path with a space — plus the seven the old parser could not read: a literal ` -> `, a quote, a backslash, a tab, a **newline**, non-ASCII and a leading space |
| `test_a_rename_record_reports_both_endpoints` | 4 | `R `, `RM`, ` R`, `RD`: both endpoints, so a move out of a watched prefix cannot conceal the removal |
| `test_a_copy_record_reports_only_its_destination` | 2 | the origin record is consumed, not reported — asserted against a fixture, because git reports a copy only under `status.renames=copies` and its detection would otherwise be nondeterministic |
| `test_the_parser_reads_a_rename_beside_ordinary_records` | 1 | the two-record form does not desynchronize the rest of the payload |
| `test_a_malformed_status_record_is_refused_rather_than_dropped` | 9 | truncation mid-payload and at the end, records too short, a wrong separator column, a rename or copy with no origin record, and one with an empty origin — all raise, none is skipped. Fixtures, for the same nondeterminism reason |
| `test_an_empty_payload_is_a_clean_tree_and_not_an_error` | 1 | the positive control for the terminator rule |
| `test_the_discovery_uses_the_machine_readable_form` | 1 | at the source: `STATUS_COMMAND` is the porcelain form, and `status_paths`, the arrow split and the quote strip are **gone**, not merely unused |
| `test_an_undeclared_file_with_a_hostile_name_is_still_rejected` | 13 | **discovery through classification** in a synthetic repository, for each hostile name: arrow, two arrows, spaces (leading and trailing), both quote characters, backslash, tab, newline, non-ASCII, CJK and emoji |
| `test_the_normal_control_beside_the_hostile_name_is_rejected_too` | 1 | Codex's reproduction with both files: two paths, two violations, and `outside.py` produced by neither |
| `test_a_tracked_modification_and_a_tracked_deletion_are_discovered` | 1 | the ordinary tracked forms, end to end against a committed synthetic repository |
| `test_a_rename_is_classified_at_both_endpoints` | 4 | real `git mv` renames out of, into and within watched areas, plus a declared file moved out — the emitted `R` record is asserted, then the classification of both endpoints |
| `test_a_nested_untracked_file_with_a_hostile_name_is_discovered` | 1 | both corrections at once: the collapse *and* the name, in the shape a new probe inside the evidence harness would take |

The R2 regressions are retained and updated to read the machine-readable form:
`test_the_discovery_enumerates_untracked_files_rather_than_directories`,
`test_the_discovery_finds_a_file_inside_an_untracked_directory`,
`test_the_reviewed_file_set_passes_and_one_more_file_does_not` (**item 5** — the
exact declared file set passes and one extra module in the same package fails),
`test_every_evidence_harness_source_in_the_tree_is_declared` and
`test_no_production_allowlist_entry_is_a_directory`.

**No synthetic unauthorized file was written into this worktree.** Every
synthetic test builds a separate repository under `tmp_path`, and the one that
needs tracked forms commits there with an identity supplied on the command line
rather than from any global configuration.

### Acceptance

Discovery and classification cannot change the scope of a file by
misinterpreting its name or by omitting a rename endpoint.

---

## 4. What was preserved

* **The R13 evidence harness.** No production source under
  `tools/phase_5_0_evidence/` was modified. All 28 covered-source digests were
  re-hashed from this tree against
  `docs/review/phase-5-0-evidence-harness-review-manifest.json` with **0
  mismatches**, so the generated artifacts were left untouched (§7).
* **The R1 and R2 corrections.** PR-20260907-1's pre-destruction artifacts,
  checksums and single rendered grant file; PR-20260907-2's identity-preserving
  role contract; PR-20260907-R2-1's `ROLE`/`END` transport, strict reader and
  fixed diagnostics; PR-20260907-R2-2's stage machine, per-stage resume points
  and both verifications; PR-20260907-R2-3's `--untracked-files=all` discovery,
  withdrawn directory entries and file-by-file declarations. All still asserted
  by their own regressions, all still passing.
* **The live-bot skills fix** (`models/skills.py`, `tests/test_skills.py`) and
  every other pre-existing modification and untracked file. Nothing was reset,
  reverted, staged, committed, pushed or reformatted; the working tree holds the
  same 86 entries it held at the start plus this handback.
* **The drill's connection gates** 0a–0e, the staging double signal, the
  production refusal and the DS-R8-2 accuracy corrections — unchanged.
* **Every execution restriction.** No SSH, no target-host inspection or mutation,
  no database operation, no destructive drill, no `--execute`, no armed real
  process boundary or materializer, no execution of a generated vector, no
  deployment, no migration `0014`, no cutover, no OD-62 ruling, no Package 5.1+
  work. **No stub test falls through to a real PostgreSQL client**: every stub run
  puts `psql`, `pg_dump` and `pg_restore` on `PATH` ahead of anything else and the
  drill's own gate 0e is answered by the stub, and `TEST_DATABASE_URL` was never
  exported in this session.
* **Every unconfirmed interpreter and `E7` target fact remains unconfirmed.**

## 5. Files changed

| File | Change |
|---|---|
| `infra/postgresql/backup-restore-drill.sh` | R3-1: `DRILL_STAGE="destroy_attempted"` before the destroy and `"destroyed"` after it; the `schema-state.sql` query, its step-3a baseline capture and the two new artifact paths; a `destroy_attempted` case in `on_exit` with its step 0, four state outcomes and its own non-recovery text; header stage list and exit-code contract updated. R3-2: `hex_record_contains_nul`, called before `decode_hex_role`, with the transport comment and exit-code contract updated |
| `docs/operations/database-development.md` | R3-1: the `destroy_attempted` stage row, the responsibility/knowledge paragraph, the step-0 section and its five-outcome table, the relations=0 ambiguity, the two new artifacts, the qualified full procedure and fallback, and the stale `SCHEMA_DROPPED=1` reference corrected. R3-2: the NUL refusal and why a substring search would be the wrong check |
| `tests/test_database_backup_restore.py` | `destroy_exit`/`destroy_applied` on the stub boundary and the schema-state answer; `destroy_attempted` added to `STAGE_INJECTIONS` and `STAGES_THAT_MAY_PRINT_A_RESTORE`; **38 new stub cases** across R3-1 and R3-2; `test_each_stage_is_recorded_only_after_its_command_succeeded` rewritten; the documentation-agreement test extended; three source-ordering anchors re-pointed at `destroy_attempted` |
| `tests/web/test_p3_4_static_assets.py` | R3-3: `status_paths` removed and replaced by `STATUS_COMMAND`, `parse_status_records`, `record_paths` and `MalformedStatusRecord`; `working_tree_paths` reads bytes from the porcelain `-z` form; `_commit_everything`; **46 new cases**; three R2 tests updated to the machine-readable form |
| `docs/review/project-review-remediation-2026-09-08-r3-handback.md` | this file |
| `docs/review/Handover information` | dated pointer to this handback, prior submissions retained |

No file under `tools/`, `application/`, `domain/`, `adapters/`, `models/`,
`ext/`, `migrations/`, `connectors/`, `helpers/` or `foundry-module/` was
modified.

## 6. Verification

### The environment, and what it is not

`.agents/AGENTS.md` documents the test environment as `oracle-test`, with
`/opt/freedom-blades/runtime/venv-web/bin/python` as the interpreter for both
suites. **It was not used and could not be**: this prompt retains the no-SSH
restriction, so `oracle-test` was not contacted at all.

Interpreter availability was **probed directly on this host**, not inferred from
any earlier handback:

| Interpreter | Version | `import pytest` |
|---|---|---|
| `/usr/bin/python3` | 3.12.3 | `ModuleNotFoundError` — matches Codex's finding |
| `/opt/freedom-blades/runtime/venv-web/bin/python` | 3.12.3 | `ModuleNotFoundError`. This is the **runtime** environment; installing into it is forbidden and was not done |
| `/opt/discord-bots/venv/bin/python` | 3.12.3 | pytest 8.4.2 |
| `/opt/discord-bots/venv-web/bin/python` | 3.12.3 | pytest 8.4.2 |

The last two are what was actually run. They are **not** presented as the
documented environment and no figure from a historical handback was carried
forward; each was verified by invoking it in this session. `shellcheck` is not
installed on this host.

### Results, run serially against the final tree

`pgrep` confirmed no other pytest process before starting, and `TEST_DATABASE_URL`
was **unset for every run**.

| # | Command | Result |
|---|---|---|
| 1 | `bash -n infra/postgresql/backup-restore-drill.sh` | clean |
| 2 | `venv … pytest -q -rs <11 deselections> tests/test_database_backup_restore.py tests/test_filesystem_layout.py` | **185 passed, 11 deselected** |
| 3 | `venv-web … pytest -q -rs tests/web/test_p3_4_static_assets.py` | **111 passed** |
| 4 | `venv … pytest -q tests/phase_5_0_evidence` | **1143 passed** |
| 5 | `venv-web … pytest -q tests/phase_5_0_evidence` | **1143 passed** |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `venv … -m compileall -q` over the two changed test modules and `tools/phase_5_0_evidence` | clean |
| 8 | `venv-web … -m compileall -q` over the same paths | clean |
| 9 | `git diff --check` | clean |
| 10 | manifest re-hash of all covered sources | **28 sources, 0 mismatches** |

**Baselines, measured rather than quoted.** The pre-fix files were run against
the same tree to establish what the deltas are:

| Selection | Before | After | New cases |
|---|---:|---:|---:|
| `tests/test_database_backup_restore.py` + `tests/test_filesystem_layout.py`, 11 deselected | 147 | **185** | **38** (22 for R3-2, 12 for R3-1, 4 from extending existing stage parametrizations) |
| `tests/web/test_p3_4_static_assets.py` | 65 | **111** | **46** |

The evidence suite is **unchanged at 1143** on both interpreters — no
evidence-harness source or test was touched. The 147 baseline reproduces the R2
handback's figure for the same selection exactly, which is the cross-check that
the baseline is the R2 tree and not something else.

**`tests/test_filesystem_layout.py` was inspected before being run**, not
launched hopefully: it contains no `database` marker, no database fixture, no
`TEST_DATABASE_URL` reference and no PostgreSQL client invocation. Its 5 cases
account for the difference between run 2's 185 and the drill module's own 180.

### Pre-fix failure record

Recorded before the corrections, in two forms for each finding.

1. **Behavioural reproductions** using the shipped helpers, in §1, §2 and §3.
   Each is Codex's own reproduction, re-run here: the failed-DROP banner claiming
   `EMPTY` and prescribing `pg_restore`; the NUL report reaching `DROP` and
   `pg_restore` with a grant for the wrong role; and
   `working_tree_paths → ['outside.py']` with `scope_violation → None`.
2. **The new regressions run against the pre-fix code.**

   * The drill regressions against a byte-exact copy of the pre-R3 script:
     **31 failed, 149 passed** (the 11 database cases error out in that ad-hoc
     run, having no fixtures, and are not counted as evidence either way). The
     failures are the 22 R3-2 cases, the 12 R3-1 cases, the four extended stage
     parametrizations, `test_each_stage_is_recorded_only_after_its_command_
     succeeded`, `test_recovery_instructions_match_database_development_
     documentation`, and three source-ordering tests whose anchor moved.
   * The scope-guard regressions against the pre-fix discovery restored verbatim:
     **15 failed, 96 passed** — the nine hostile names the old parser rewrote, the
     two-file control, the four rename cases and the nested hostile name. The
     four hostile names the old parser happened to survive (plain space, leading
     and trailing space, single quote) passed pre-fix, and are reported as
     passing rather than counted as evidence.

The pre-fix files are byte-exact copies taken before the first edit, not
reconstructions.

### Deselected: eleven cases, by name

All in `tests/test_database_backup_restore.py`, unchanged from the R2 set:

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

**This correction adds no twelfth**: no new PostgreSQL regression was written for
any of the three findings. **None of the eleven is claimed to pass against this
tree.** Cases 4, 6 and 7 assert literal fragments of the drill script or its
banner; those literals were re-checked against the corrected script so an
authorized run exercises the current code rather than failing stale. **Case 5's
previously undiagnosed failure remains undiagnosed**: it was not re-run, and no
stub result here is offered as its explanation.

### Whole modules excluded, by name

Both are `pytest.mark.database` modules that invoke the real drill against a real
database, and both were identified by reading them rather than by running them:

* `tests/test_snapshot_database.py` — runs `backup-restore-drill.sh` against the
  disposable database as part of a snapshot round trip.
* `tests/web/test_identity_migration_backup_restore.py` — automates the same
  round trip, including `test_the_drill_script_still_refuses_a_non_disposable_target`.

### Checks not run, and why

| Not run | Reason |
|---|---|
| The eleven deselected cases | destructive drill / cluster-role creation; the prompt forbids them here |
| The two database-marked modules above | same |
| The complete bot suite and the complete web suite | the prompt requires focused checks against inspected fixtures and forbids launching a broad suite intending to stop before database access. The four modules those suites share with this correction were run individually and are named above |
| Anything on `oracle-test` | the no-SSH restriction; the documented environment is unreachable under this authority |
| Either suite **under the documented `oracle-test` interpreter** | same; runs 2–5 are this host's local interpreters and are labelled as such |
| Re-running the pristine-schema drill to diagnose the outstanding failure | it is a destructive drill; the prompt forbids it and says so explicitly |
| The evidence harness itself | no `--execute`, no armed boundary or materializer, no generated vector; unchanged from R13 |
| Any privileged or mutation-bearing command from the plan | all 43 mutations and 46 cleanup steps remain reviewed argument vectors |
| A configured formatter, linter or type checker | **none is configured in this repository**: there is no `pyproject.toml`, `ruff.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `.pre-commit-config.yaml`, and `pytest.ini` is the only tool configuration present. `shellcheck` is not installed on this host. `compileall`, `bash -n` and `git diff --check` are what is available and were run |

## 7. Generated artifacts

**No evidence-harness production source changed in this revision**, so the
prompt's first branch applies: the manifest was verified and the generated
artifacts were left untouched. Nothing was regenerated and nothing was
hand-edited.

| Fact | Value |
|---|---|
| Covered sources re-hashed from this tree | **28** |
| Digest mismatches against the manifest | **0** |
| Manifest version / schema | **5** / `phase-5-0-evidence-review-manifest`, unchanged |
| Harness version | **0.6.0-pre-execution**, unchanged |
| Target identity digest recorded in the manifest | `ceb58ad1f9f0e07057ae9d292096a2f88910d5986a50507df8f7a7c14a149403`, unchanged |
| Review-manifest digest recorded in the concrete plan | `d91e996977d91bbd6229fa0311df46ff13494611cb6cdd8a4234a077ded9e402`, unchanged |
| Superseded R13 digest, never to be passed to `--execute` | `057c84a96225bfb8e1b02f4502619015b06b8dbc050342423ade25be4f3b7ae5` |

**No digest was passed to `--execute`**, and the digest above remains **review
material only, not execution authority**: the executor still refuses this plan on
twelve unsupplied reviewed target facts whatever digest it is given.

## 8. Status, and what this does not claim

* **PR-20260908-R3-1: remediated.** Destruction *attempted* and destruction
  *confirmed* are separate states; a failed or uncertain destroy is never called
  a proven empty database; its recovery begins with read-only inspection covering
  an intact schema, an empty recreated one, an absent one and an unexpected one,
  and says explicitly where an operator must resolve uncertainty rather than
  mutate; no unconditional `DROP`, `--clean` or `TRUNCATE` was introduced; the
  post-restore resume points, both verifications and the zero-role behaviour are
  preserved.
* **PR-20260908-R3-2: remediated.** A NUL-bearing record is refused as malformed
  transport before it is decoded into a representation that cannot hold it, by a
  whole-byte-pair scan that does not misclassify a boundary-crossing `00`; exit 2
  before `DROP`, with fixed safe diagnostics and no grants rendered; the
  supported-role contract is unchanged.
* **PR-20260908-R3-3: remediated.** Discovery reads NUL-delimited porcelain
  records with `--untracked-files=all`, parses the documented rename/copy form,
  reports both rename endpoints and refuses malformed records; the allowlists,
  scopes and watched prefixes are unchanged; the human-readable parsing path is
  removed rather than left unused.
* **Package 5.0 remains `not ready`. P5.0-R5 remains Blocking.** No finding,
  assumption, decision, residual risk or gate is closed, and no roadmap, RAID,
  decision or gate record was altered. **R13 has not received complete
  independent pre-execution approval**, and nothing here implies one.
* This submission does not claim the eleven deselected cases pass, does not claim
  any figure from the documented `oracle-test` environment, does not confirm any
  reviewed target fact, and does not resolve the outstanding pristine-schema
  drill failure.

## 9. Request

Please re-review these three corrections, and in particular:

1. **the `destroy_attempted` contract** — whether recording responsibility before
   the command and knowledge only after it is the right split; whether the four
   state outcomes and the failed-query non-answer are complete; and whether
   stopping at "resolve it with an operator" for the absent and unexpected states
   is the right refusal rather than a gap;
2. **the schema-state report** — whether `to_regnamespace` plus a relation count
   and a base-table count is sufficient to separate the states the banner claims
   to separate, and whether the stated relations=0 ambiguity is handled honestly;
3. **the NUL classification** — whether refusing the *report* as malformed
   transport is the right treatment rather than refusing the *role*, and whether
   the byte-pair scan is the right shape;
4. **the rename/copy asymmetry** — whether reporting both endpoints of a rename
   and only the destination of a copy is correct, or whether a copy origin should
   also reach the guard; and
5. **the verification boundary** — whether running four inspected modules instead
   of the two full suites is the right reading of "do not launch a broad suite and
   hope to stop before database access", or whether an authorized full run should
   be requested before this correction is accepted.

Nothing here is offered as operational execution, and this submission stops
before it.
