# Project review remediation R5, 2026-09-08 — implementation handback

Date: 2026-09-08

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: `docs/review/project-review-remediation-2026-09-08-r5-claude-prompt.md`.
That prompt authorizes a **bounded correction to the drill's recovery
instructions, their supporting logic if necessary, the operations guide and
synthetic tests**, and nothing else. It is not Package 5.0 product
implementation and it is not complete R13 pre-execution approval.

Outcome: **the remaining Blocking PR-20260908-R3-1 recovery finding is
corrected at both uncertain stages.** It continues that finding; no finding ID
is replaced, reopened or closed. Package 5.0 remains `not ready`; P5.0-R5
remains Blocking.

**The undiagnosed pristine-schema drill failure reported in the 2026-09-07
handback (§6, case 5) remains unresolved.** It was not re-run here, and nothing
below is offered as its diagnosis.

---

## Erratum — 2026-09-08, issued with remediation R6

**This submission is preserved below as history. Two of its statements about
PostgreSQL session visibility were wrong, and this erratum supersedes them.**
It was raised as an Optional finding in Codex's independent review of this
handback and corrected under
`docs/review/project-review-remediation-2026-09-08-r6-claude-prompt.md`; the
corrected wording is in
`docs/review/project-review-remediation-2026-09-08-r6-handback.md`.

**What PostgreSQL 16 actually documents**
([Viewing Statistics](https://www.postgresql.org/docs/16/monitoring-stats.html#MONITORING-STATS-VIEWS)):
the **existence** of a session and its general properties, such as its session
user and database, are **visible to all users**. In rows about *other* sessions
many columns are null. A user sees the full information for sessions belonging
to a role they are a member of, and superusers and roles with the privileges of
`pg_read_all_stats` see the full information for every session. **PostgreSQL
restricts columns here, not rows.**

**The assertions this erratum supersedes**, precisely:

1. **§2, reason 2 of the three reasons the completion mechanism was rejected**,
   headed *"Absence of a row is not absence of a backend."* Its supporting
   sentence — *"A role that is neither a superuser nor a member of
   `pg_read_all_stats` is restricted in what it sees of another role's session,
   so 'I see no such session' and 'no such session exists' are different
   statements, and the drill cannot establish which one the recovering operator
   is making"* — **overstates the restriction**. Permissions do not remove the
   session row, so a role that sees no session row for the database is not being
   denied the row's existence.

   **What is true, and is what the reason should have said:** the columns that
   would identify *which* session it is and *whether it still holds a
   transaction open* are among those that come back null for another role's
   session. So an operator can see that a session exists and still be unable to
   attribute it to this drill or to establish that its transaction has ended. A
   null field, or an inability to associate a visible session with this drill,
   is not proof of completion.

2. **§2, "The completion/observation distinction, as it is now written"**, the
   second of the two named limits: *"a session whose row you cannot see is not a
   session that has ended"*. Replaced by the corrected limit above — a visible
   session row is not the same thing as the fields needed to identify its work
   or establish transaction completion.

**Dependent claims, corrected by reference.** §5's row for
`test_the_completion_gate_says_what_would_establish_completion` describes the
gate as naming *"the visibility limit"*: that is now the corrected limit, and
the test asserts the corrected wording. §10's request item 3 remains a live
question, read with the corrected distinction: what the drill cannot confirm is
the recovering role's **field-level** visibility for a session it can see, not
whether the row is visible at all.

**What this erratum does not change.**

* **The conservative stop stands.** It remains an allowed design choice, and
  §2's reasons 1 and 3 are untouched: the evidence would be written by the
  process whose death defines the failure, and automating the answer invites
  automating the remedy. The corrected reason 2 still tells against relying on
  a `pg_stat_activity` mechanism for every recovering role, because the fields
  such a check would read may be null.
* **Nothing here implies that establishing completion requires terminating or
  cancelling a backend.** No banner, guide section or test does that, and none
  may.
* **No finding, decision, assumption, residual risk or gate is closed**, and no
  package state moves. Package 5.0 remains `not ready`; P5.0-R5 remains
  Blocking.

---

## 1. The remaining finding, conceded

R4's step 0 reads two reports and classifies the outcome from what they count
**at the moment they run**. Neither stage first establishes that the transaction
this drill started has ended.

PostgreSQL 16 documents both halves of why that does not hold:

* with
  [`client_connection_check_interval=0`](https://www.postgresql.org/docs/16/runtime-config-connection.html#GUC-CLIENT-CONNECTION-CHECK-INTERVAL),
  the default, the server detects a lost connection at its next socket
  interaction rather than necessarily stopping the query when the client
  disappears; and
* under [Read Committed](https://www.postgresql.org/docs/16/transaction-iso.html)
  a `SELECT` sees what was committed before the query began, not another
  transaction's uncommitted work.

So the failure sequence R4 permits is exactly the one the prompt states:

1. `public` holds one function and no base tables.
2. The DROP reaches the server; the client dies without reporting success. The
   server transaction is still running.
3. Both recovery reports see the old committed state — `routines=1`, empty row
   inventory — and both match their baselines.
4. R4's banner selects **THE DESTROY DID NOT TAKE EFFECT … NO DATA RESTORE IS
   REQUIRED**.
5. The original transaction commits. The function is gone, and the procedure
   directed the operator past the restore that would have recovered it.

**The dependent `restore_attempted` decision has the mirror omission.** Zero
counts are also what an uncommitted restore that is **still running** looks like
from another session: `--single-transaction` publishes nothing until it commits.
R4 reads that as "the transaction rolled back, continue at step 1", which starts
a second restore beside one still in flight.

## 2. The correction, and why it is a stop rather than a mechanism

The prompt allowed either an explicit unresolved outcome pending operator
confirmation, or a bounded, reviewable completion mechanism. **This correction
takes the stop**, and the mechanism was considered and rejected on evidence
rather than on preference.

**The mechanism that was considered.** The destroying session could record its
own `pg_backend_pid()` together with its `backend_start`, and step 0 could then
ask `pg_stat_activity` whether that exact `(pid, backend_start)` session is
still present — the pairing being what survives pid reuse. A session that is
gone cannot commit anything later, so its state would be final and the reports
decisive.

**Why it was not built.**

1. **The evidence is written by the process whose death defines the failure.**
   The identity line would leave the drill through the same client whose
   disappearance is the failure mode, through a block-buffered stream. It is
   most likely to be missing in precisely the case it exists for, and a
   mechanism that silently degrades to "no evidence" is a mechanism that has to
   stop anyway.
2. **Absence of a row is not absence of a backend.** A role that is neither a
   superuser nor a member of `pg_read_all_stats` is restricted in what it sees
   of another role's session, so "I see no such session" and "no such session
   exists" are different statements, and the drill cannot establish which one
   the recovering operator is making.
3. **Automating the answer would be the first step toward automating the
   remedy.** The prompt forbids backend termination and cancellation, and a
   completion check that returns "still running" invites one.

So the procedure does the honest thing instead: it asks the question, names what
would answer it, names what does **not** answer it, and refuses to classify the
outcome until an operator has answered. That is a conservative operator stop, not
a new recovery engine, and it takes no operational authority the drill did not
already have.

### The completion/observation distinction, as it is now written

**An observation** is what the state report and the row inventory return: counts
over named schema-scoped catalog classes, describing what had been committed when
each query began. R4's boundary on those counts is preserved verbatim — they do
not say *which* objects are there, and they are not exhaustive.

**Completion evidence** is separate and this drill does not produce it. It is
the operator's finding that no backend is still running this drill's statement or
holding its transaction open against the database, established from
`pg_stat_activity` and read with its two limits in mind: a pid is not an identity
on its own, and a session whose row you cannot see is not a session that has
ended. Only one direction of that answer is stable — a backend that has ended
cannot come back, while "still running" can become "gone" a moment later.

**Neither is the other.** Client exit, the drill's exit status, elapsed time and
two reports that agree are all named in the banner and the guide as *not*
completion evidence.

### Every unresolved outcome, after the correction

At `destroy_attempted`:

| Observation | Decision |
|---|---|
| **completion not established, whatever the reports say** | **UNRESOLVED**; stop, change nothing, resolve with an operator |
| either report failed | not known; repeat step 0b, change nothing |
| `schema_present=false` | absent; stop, resolve with an operator |
| some count non-zero, whole report matches the baseline, inventory matches | the destroy did not take effect — **provided 0a answered**; otherwise this is also what an unfinished destroy looks like, and it is unresolved |
| every count zero, baseline recorded an object | dropped and recreated — **provided 0a answered**; continue at step 1 |
| every count zero, baseline recorded zero in every class | unresolved; stop. **0a does not rescue this one**: even a transaction known to have ended leaves these two reports identical |
| anything else | unexpected; stop, resolve with an operator |

At `restore_attempted`:

| Observation | Decision |
|---|---|
| **completion not established, whatever the reports say** | **UNRESOLVED**; stop, run no restore, resolve with an operator |
| either report failed | not known; repeat step 0b |
| baseline records zero in every class | cannot be resolved by these reports; stop |
| every count zero, baseline recorded objects | rolled back — **provided 0a answered**; otherwise an unfinished restore produces the same pair and it is unresolved |
| both diffs print nothing, baseline recorded objects | committed — **once 0a has answered**, without which no count here is settled; SKIP STEP 4, continue at step 5 |
| anything else | partial; neither resuming nor repeating is safe |

**The dependent fallback text was audited too.** `destroy_attempted`'s
rebuild-from-migrations fallback now says the schema-was-dropped finding "takes
0a and not the reports alone". `restore_attempted` previously shared the
`destroyed` fallback, which asserted "it would dump the empty database" — an
emptiness claim the stage does not establish, and one that would have read as a
resolution behind step 0's stop. It now has its own text: re-running is not a
step of any kind until step 0 has answered, the database is described as being
in whatever state it is actually in, "possibly over a restore that is still
running", and the rebuild applies only once step 0 has established that the
restore did not commit.

**No banner and no guide text terminates or cancels a backend**, and both say so
in place. `pg_terminate_backend` and `pg_cancel_backend` appear in neither file,
which is asserted by regression.

## 3. Files changed

| File | Change |
|---|---|
| `infra/postgresql/backup-restore-drill.sh` | `destroy_attempted` and `restore_attempted` step 0 each split into **0a** (has the server-side transaction ended?) and **0b** (the reports, read after 0a); every outcome that concludes or directs an action conditioned on 0a; the `destroy_attempted` and `restore_attempted` `data_state` paragraphs; the `restore_attempted` fallback split out of the shared `destroyed` branch; header comment, schema-state section comment, step 3a, step 4 and step 5 comments |
| `docs/operations/database-development.md` | the R5 narrative with both primary references; the stage table's two uncertain rows; a **Step 0a** section at each of the two stages, with its does-not-establish / would-establish / how-the-observation-fails / what-not-to-do / unresolved table; both step-0 outcome tables conditioned on 0a; the full-procedure and dump-unusable paragraphs; the `schema-state-before.txt` artifact row |
| `tests/test_database_backup_restore.py` | transaction completion modelled as its own stub axis (`destroy_completed`, `restore_completed`, `restore_applied`, `schema_state_restored`, a `.restored` report state); `resolve_pending_transaction` and `read_state_report` helpers; **12 new cases**; `test_the_failed_destroy_banner_accounts_for_every_schema_state`, `test_a_failed_destroy_prescribes_no_mutation_before_the_state_is_known` and the documentation-agreement test extended |
| `docs/review/project-review-remediation-2026-09-08-r5-handback.md` | this file |
| `docs/review/Handover information` | dated pointer to this handback, prior submissions retained |

No file under `tools/`, `application/`, `domain/`, `adapters/`, `models/`,
`ext/`, `migrations/`, `connectors/`, `helpers/`, `foundry-module/` or
`tests/web/` was modified. Verified by modification time across the working
tree: the only files touched in this session are the three above plus this
handback and the handover pointer.

### The boundary change that makes the regressions real

The stub already modelled *whether* the DROP applied, independently of the exit
status. It could not model **whether the statement had finished**, so no test
could distinguish "the reports are final" from "the reports are a snapshot of a
database something is still changing".

Completion is now a third independent axis. `destroy_completed=False` /
`restore_completed=False` mean the statement reached the server and its
transaction has **not** ended: no catalog change is visible to any other session,
and the outstanding transaction is recorded in a marker **no report reads**.
`resolve_pending_transaction(scenario, stage, "commit"|"rollback")` ends it at a
point the test chooses. The ordering "observe, *then* the transaction ends" is
therefore a property of the test — **an explicit state transition, with no sleep
and no timing dependence**.

## 4. Pre-fix regression failures, recorded before the correction

Two forms, both measured rather than asserted.

**a. The behavioural reproduction**, run against the submitted R4 tree. In
`test_a_pending_destroy_transaction_is_not_settled_by_the_current_reports` the
first three stages pass against R4 — that *is* the defect:

* the drill exits 42 having reached the destroy and never called `pg_restore`;
* the baseline is `…|relations=0|base_tables=0|routines=1|types=0|extensions=0|other_objects=0`
  and the row inventory is empty;
* the state report, run through the same stub boundary exactly as the banner
  tells the operator to run it, **equals the baseline and counts an object** —
  R4's "the destroy did not take effect, no data restore is required" premise;
* `resolve_pending_transaction(..., "commit")` then ends the transaction, and the
  same report returns `…|routines=0|…`.

The test then fails on its fourth stage, which is the decision contract:

```
>       assert "HAS THE DESTROY'S SERVER-SIDE TRANSACTION ENDED?" in procedure
E       assert "HAS THE DESTROY'S SERVER-SIDE TRANSACTION ENDED?" in
        "Recovery procedure, in this order: 0. Establish the state of the schema
         before choosing anything. Both reports are re…"
```

The restore case is the same shape:

```
>       assert "HAS THE RESTORE'S SERVER-SIDE TRANSACTION ENDED?" in procedure
E       assert "HAS THE RESTORE'S SERVER-SIDE TRANSACTION ENDED?" in
        "Recovery procedure, in this order: 0. Establish whether the data restore
         committed, before deciding to run it. Both r…"
```

**b. The full selection**, final test module against **byte-exact copies of the
R4 script and guide** (`sha256 1e91c1ea…` and `e594d898…`, taken before the first
edit and restored afterwards, verified):

**10 failed, 189 passed, 11 deselected.**

* `test_a_pending_destroy_transaction_is_not_settled_by_the_current_reports`
* `test_a_pending_restore_transaction_is_not_called_a_rollback`
* `test_the_completion_gate_says_what_would_establish_completion`
* `test_no_recovery_instruction_ends_a_backend_to_settle_the_question`
  (`destroy_attempted`, `restore_attempted` — the two stages that must state the
  prohibition; the other three stages pass, having no open-transaction question)
* `test_the_failed_destroy_banner_accounts_for_every_schema_state` (2 cases,
  extended)
* `test_a_failed_destroy_prescribes_no_mutation_before_the_state_is_known`
  (2 cases, extended)
* `test_recovery_instructions_match_database_development_documentation`
  (extended to the guide's half of the same contract)

## 5. The cases, and their completed controls

| Case | Modelled | What it shows |
|---|---|---|
| `test_a_pending_destroy_transaction_is_not_settled_by_the_current_reports` | function-only schema; DROP applied; transaction **pending**; commit **after** the observation | the reports match the baseline while the destroy is still running, then change; the procedure may not conclude from them until 0a has answered |
| `test_a_completed_destroy_transaction_still_reaches_a_decisive_outcome[completed-refused-or-rolled-back]` | DROP not applied; transaction **ended** | `routines=1`, stable on re-read; "the destroy did not take effect" is still available |
| `test_a_completed_destroy_transaction_still_reaches_a_decisive_outcome[completed-committed]` | DROP applied; transaction **ended** | every count zero against a baseline that recorded an object; "dropped and recreated, continue at step 1" is still available |
| `test_a_pending_restore_transaction_is_not_called_a_rollback` | restore applied; transaction **pending**; commit **after** the observation | zero counts while the restore is still running — R4's rollback premise — then the objects appear |
| `test_a_completed_restore_transaction_still_resolves_to_one_outcome[completed-committed]` | restore applied; transaction **ended** | both diffs print nothing; SKIP STEP 4 is still available |
| `test_a_completed_restore_transaction_still_resolves_to_one_outcome[completed-rolled-back]` | restore not applied; transaction **ended** | every count zero; the restore is still available |
| `test_the_completion_gate_says_what_would_establish_completion` | pending destroy | the gate names `pg_stat_activity`, pid reuse, the visibility limit, the stable direction, and that 0b is read **after** 0a |
| `test_no_recovery_instruction_ends_a_backend_to_settle_the_question` | all five banner stages | no stage names a termination or cancellation, and the two uncertain stages state the prohibition |

In every completed control the boundary leaves **no pending marker**, and the
report is asserted to be identical on a second read — the property that makes it
a control rather than another snapshot.

## 6. What was preserved

* **R4's evidence contract in full**: six named catalog classes, the explicit
  "these are counts, they are not an identity inventory, they are not
  exhaustive" statement, `pg_restore --list` as the identity inventory, and the
  all-zero-baseline refusal — which is still a stop and is still not "there was
  nothing to lose".
* **Responsibility before DROP, confirmed destruction only after success.**
  `DRILL_STAGE="destroy_attempted"` is still assigned before the command,
  `"destroyed"` only after it succeeds, and
  `test_each_stage_is_recorded_only_after_its_command_succeeded` still asserts
  the source ordering.
* **The absent/unexpected stops and query-failure-as-unknown behaviour**,
  unchanged in substance.
* **Confirmed post-restore resume points.** `restored`,
  `schema_grants_applied` and `grants_applied` are untouched and still contain no
  `pg_restore`; a confirmed restore is never repeated.
* **Checksummed recovery artifacts**, the exact validated runtime role rendered
  before the destroy, the explicit zero-runtime-role statements, and **both
  final verifications** terminating every emitted procedure.
* **No destructive reset anywhere.** `test_no_recovery_path_prescribes_an_
  unrequested_destructive_reset` still runs over all five stages: no `DROP`,
  `DROP DATABASE`, `--clean`, `-c ` or `TRUNCATE`, and no branch prescribes
  restoration over known existing objects.
* **R3-2's pre-decode NUL refusal** and **R3-3's machine-readable Git path
  discovery**, unmodified and still asserted by their own regressions.
* **The live-bot skills fix** (`models/skills.py`, `tests/test_skills.py`) and
  every other pre-existing modification and untracked file: nothing was reset,
  reverted, staged, committed, pushed or reformatted. The working tree holds the
  same **90** entries it held at the start of this session, and this handback
  will be the 91st.
* **The R13 evidence harness**, unchanged: no production source under
  `tools/phase_5_0_evidence/` was touched and no generated artifact regenerated.
* **Every execution restriction.** No SSH, no target-host inspection or
  mutation, no database operation, no destructive drill, no `--execute`, no armed
  real process boundary or materializer, no execution of a generated vector, no
  deployment, no migration `0014`, no cutover, no OD-62 ruling, no Package 5.1+
  work. **No stub test falls through to a real PostgreSQL client**: every stub
  run puts `psql`, `pg_dump` and `pg_restore` on `PATH` ahead of anything else,
  and `TEST_DATABASE_URL` was never exported in this session. **No backend was
  terminated or cancelled, and none was contacted.**
* **Every unconfirmed interpreter and `E7` target fact remains unconfirmed.**

## 7. Verification

### The environment, and what it is not

`.agents/AGENTS.md` documents the test environment as `oracle-test`, interpreter
`/opt/freedom-blades/runtime/venv-web/bin/python`. **It was not used and could
not be**: the no-SSH restriction stands and `oracle-test` was not contacted.

Interpreter availability was **probed directly on this host in this session**:

| Interpreter | Version | `import pytest` |
|---|---|---|
| `/usr/bin/python3` | 3.12.3 | not installed |
| `/opt/freedom-blades/runtime/venv-web/bin/python` | 3.12.3 | not installed. This is the **runtime** environment; installing into it is forbidden and was not done |
| `/opt/discord-bots/venv/bin/python` | 3.12.3 | pytest 8.4.2 |
| `/opt/discord-bots/venv-web/bin/python` | 3.12.3 | pytest 8.4.2 |

The last two were used. They are **local fallbacks on this host, not the
documented environment**. `shellcheck` is not installed here.

### Results, run serially against the final tree

`TEST_DATABASE_URL` was **unset for every run**.

| # | Command | Interpreter | Result |
|---|---|---|---|
| 1 | `bash -n infra/postgresql/backup-restore-drill.sh` | bash | clean |
| 2 | `pytest -q -rs <11 deselections> tests/test_database_backup_restore.py tests/test_filesystem_layout.py` | `/opt/discord-bots/venv` | **204 passed, 11 deselected** |
| 3 | `pytest -q -rs tests/web/test_p3_4_static_assets.py` | `/opt/discord-bots/venv-web` | **111 passed** |
| 4 | `pytest -q tests/phase_5_0_evidence` | `/opt/discord-bots/venv` | **1143 passed** |
| 5 | `pytest -q tests/phase_5_0_evidence` | `/opt/discord-bots/venv-web` | **1143 passed** |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | node | **171 pass, 0 fail** |
| 7 | `python -m compileall -q` over the changed test module and `tools/phase_5_0_evidence` | both venvs | clean |
| 8 | `git diff --check` | git | clean |
| 9 | manifest re-hash of every covered source | `/opt/discord-bots/venv` | **28 sources, 0 mismatches** |

Run 2 is **204** against R4's **192** for the same selection: this correction
adds **12** cases. Runs 3–6 are unchanged from R4, as expected — nothing outside
the drill, its guide and its tests was touched.

`tests/test_filesystem_layout.py` and `tests/web/test_p3_4_static_assets.py`
were inspected before being run: no `database` marker, no database fixture, no
`TEST_DATABASE_URL` reference and no PostgreSQL client invocation in either.

The eleven deselected cases' **source-replacement anchors were re-checked
against the corrected script** — `"${RESTORE_COMMAND[@]}"`, the schema-grants
`psql` line, the runtime-grants `psql` line and the `GRANT_TEMPLATE` assignment
are all present and unchanged — so an authorized run exercises the current code
rather than failing stale.

### Evidence limitations — synthetic versus PostgreSQL

* Every case above is a **stub reproduction**. Reports are computed in Python and
  projected through the drill's own `schema-state.sql`; **no SQL is executed**.
* The completion axis is a **modelled** transaction lifetime: a marker written
  when the statement is issued and removed by an explicit call. It establishes
  which recovery decision the drill emits for a given pair of reports **and a
  given completion state**, and the ordering of the emitted procedure.
* It is **not a PostgreSQL timing reproduction**. No backend was started, none
  was left running, and nothing here observes `client_connection_check_interval`,
  Read Committed visibility or `pg_stat_activity` behaviour on any server. **The
  backend-timing concern is an inference from the primary PostgreSQL 16
  documentation cited in §1**, and it is presented as exactly that in the script,
  the guide and here.
* **No target configuration is established.** Whether the disposable server runs
  with the default `client_connection_check_interval`, and what
  `pg_stat_activity` shows to the role an operator would recover as, are both
  unconfirmed. The procedure is written to be safe without knowing either.
* **The extended `schema-state.sql` has still never run against a PostgreSQL
  server**, and this correction does not change that. Its column names were
  checked against the PostgreSQL 16 catalog documentation and that remains the
  whole of the evidence for it. **Synthetic evidence does not supply the
  authorized PostgreSQL validation it needs before operational acceptance.**
* **No database-semantic or timing test was written or executed here**, so there
  is no twelfth deselected case. Such a test belongs to a later authorized run.

### Deselected: eleven cases, by name

All in `tests/test_database_backup_restore.py`, unchanged from the R2/R3/R4 set:

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

**None of the eleven is claimed to pass against this tree. Case 5's previously
undiagnosed failure remains undiagnosed**: it was not re-run, and no stub result
here is offered as its explanation.

### Whole modules excluded, by name

Both are `pytest.mark.database` modules that invoke the real drill against a real
database:

* `tests/test_snapshot_database.py`
* `tests/web/test_identity_migration_backup_restore.py`

### Checks not run, and why

| Not run | Reason |
|---|---|
| The eleven deselected cases | destructive drill / cluster-role creation; forbidden here |
| The two database-marked modules above | same |
| Any PostgreSQL execution of `schema-state.sql`, or any observation of backend behaviour | no database operation is permitted; stated as unexecuted rather than implied to work |
| The complete bot suite and the complete web suite | the prompt forbids launching a broad suite intending to stop before database access. The affected modules were inspected and run individually and are named above |
| Anything on `oracle-test` | the no-SSH restriction; the documented environment is unreachable under this authority |
| Either suite **under the documented `oracle-test` interpreter** | same; runs 2–5 are this host's local fallbacks and are labelled as such |
| Re-running the pristine-schema drill | it is a destructive drill |
| The evidence-harness executor | no `--execute`, no armed boundary or materializer, no generated vector; unchanged from R13 |
| A configured formatter, linter or type checker | **none is configured in this repository**: no `pyproject.toml`, `ruff.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `.pre-commit-config.yaml`; `pytest.ini` is the only tool configuration present. `shellcheck` is not installed on this host. `compileall`, `bash -n` and `git diff --check` are what is available and were run |

## 8. Generated artifacts

**No evidence-harness production source changed**, so the manifest was verified
and the generated artifacts were left untouched. Nothing was regenerated and
nothing was hand-edited.

| Fact | Value |
|---|---|
| Covered sources re-hashed from this tree | **28** |
| Digest mismatches against the manifest | **0** |
| Manifest version / schema | **5** / `phase-5-0-evidence-review-manifest`, unchanged |
| Harness version | **0.6.0-pre-execution**, unchanged |
| Superseded R13 digest, never to be passed to `--execute` | `057c84a96225bfb8e1b02f4502619015b06b8dbc050342423ade25be4f3b7ae5` |

**No digest was passed to `--execute`.**

## 9. Status, and what this does not claim

* **The remaining PR-20260908-R3-1 recovery finding is corrected.** While the
  original transaction may still finish, neither uncertain stage classifies its
  final outcome from current counts alone, and neither directs an operator to
  skip or repeat recovery on that basis. The conservative stop is explicit in
  every dependent instruction, including both fallbacks.
* **Package 5.0 remains `not ready`. P5.0-R5 remains Blocking.** No finding,
  assumption, decision, residual risk or gate is closed, and no roadmap, RAID,
  decision or gate record was altered. **R13 has not received complete
  independent pre-execution approval**, and nothing here implies one.
* This submission does not claim the eleven deselected cases pass, does not
  claim any figure from the documented `oracle-test` environment, does not
  confirm any reviewed target fact, does not establish any PostgreSQL timing or
  visibility behaviour, and does not resolve the outstanding pristine-schema
  drill failure.

## 10. Request

Please re-review, and in particular:

1. **the choice of a stop over a mechanism** — §2 gives three reasons the
   `(pid, backend_start)` completion check was rejected. If any of them is wrong
   on this target, the mechanism becomes available and this correction becomes
   the conservative half of it;
2. **the gate's placement** — 0a before 0b, with 0b re-run afterwards, rather
   than a completion caveat attached to each outcome;
3. **what the gate asks an operator to establish** — whether naming
   `pg_stat_activity` with its two limits is useful guidance or an invitation to
   over-read it, given the drill cannot confirm the recovering role's visibility;
4. **the `restore_attempted` fallback split** — whether separating it from the
   `destroyed` branch was in scope, and whether its text now says only what the
   stage establishes; and
5. **the unexecuted SQL and the unconfirmed target configuration**, both of
   which still need an authorized run before this procedure is relied on.

Nothing here is offered as operational execution, and this submission stops
before it.
