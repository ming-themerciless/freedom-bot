# Project review remediation R6, 2026-09-08 — implementation handback

Date: 2026-09-08

Implementer: Claude, Package 5.0 implementer and working Technical Lead

Reviewer requested: Codex, Security Reviewer and Independent Reviewer

Authority: `docs/review/project-review-remediation-2026-09-08-r6-claude-prompt.md`.
That prompt authorizes **the session-visibility wording correction, updates to
the existing tests that require the inaccurate wording, and a concise handback**,
and nothing else. It is not Package 5.0 product implementation and it is not
complete R13 pre-execution approval.

Outcome: **the Optional session-visibility finding from Codex's independent
review of the R5 handback is corrected** in the drill's two uncertain-stage
banners, the operations guide, the drill tests and — as a dated erratum — in the
R5 handback itself. No finding is closed, and nothing here reopens
PR-20260908-R3-1 or affects Codex's recommendation to close it.

---

## 1. The corrected distinction

**What R5 implied.** The two uncertain-stage banners, the guide, and their test
comments and assertions said that a role which is neither a superuser nor a
member of `pg_read_all_stats` *"is restricted in what it sees of another role's
session, so **a session whose row you cannot see is not a session that has
ended**"*. Read plainly, that says permissions can hide the whole session row.

**What PostgreSQL 16 documents**
([Viewing Statistics](https://www.postgresql.org/docs/16/monitoring-stats.html#MONITORING-STATS-VIEWS),
the primary reference, read before this correction): the **existence** of a
session and its general properties, such as its session user and database, are
**visible to all users**. In rows about other sessions many columns are null. A
user sees the full information for sessions belonging to a role they are a member
of, and superusers and roles with the privileges of `pg_read_all_stats` see the
full information for all sessions.

**So the distinction is between a row and its fields, not between a visible
session and a hidden one.** The corrected text, in the same words in both
documents:

> PostgreSQL restricts columns here, not rows: the existence of a session and its
> general properties, such as its session user and database, are visible to all
> users, while in rows about a session belonging to a role you are not a member of
> many columns are null unless you are a superuser or hold `pg_read_all_stats`. So
> the row may be there while the fields that would tell you what that session is
> running, and whether it still holds a transaction open, are not. **A null field,
> or being unable to associate a visible session with this drill, is not proof
> that this transaction has ended.**

Two things follow, and both are now stated rather than implied:

* an operator may see a session and still be unable to attribute it to this
  drill or to establish that its transaction has ended; and
* neither a null field nor an inability to make that association is completion
  evidence.

**No claim that permissions hide entire session rows survives in either
document**, and a regression asserts that in three forms.

**Nothing about the target is inferred from the reference.** Whether the
disposable server runs with the default `client_connection_check_interval`, and
what `pg_stat_activity` shows to the role an operator would recover as, both
remain unconfirmed. The procedure is written to be safe without knowing either.

## 2. What did not change

* **The conservative operator stop.** Both stages still ask 0a — *has the
  server-side transaction ended?* — before reading anything, every 0b outcome is
  still provisional until an operator has answered, and an unestablished
  completion is still **UNRESOLVED**: stop, change nothing, resolve with an
  operator. No completion mechanism was implemented and no recovery behaviour
  changed.
* **Completion before observation.** 0a is still emitted and read before 0b, and
  0b still instructs an operator who read the reports early to run them again.
* **No backend is terminated or cancelled**, and neither document names
  `pg_terminate_backend` or `pg_cancel_backend`. The correction adds no
  suggestion that checking completion requires ending a backend; the corrected
  paragraph is followed, unchanged, by the prohibition against doing so.
* **The all-zero-baseline refusal, the absent/unexpected stops,
  query-failure-as-unknown, "equal counts are not an identity inventory",
  R4's six catalog classes and their explicit limits, fresh reports after
  completion, pid-reuse caution, confirmed post-restore resume points,
  checksummed artifacts, exact runtime-role handling, explicit zero-role
  behaviour, both final verifications, R3-2's pre-decode NUL refusal and R3-3's
  machine-readable Git path discovery** — all unchanged in substance. The
  pending-transaction scenarios and their completed controls are unchanged; no
  new simulation of PostgreSQL permissions and no completion checker was added.
* **The R13 evidence harness**, unchanged: no production source under
  `tools/phase_5_0_evidence/` was touched and no generated artifact regenerated.

## 3. Files changed

| File | Change |
|---|---|
| `infra/postgresql/backup-restore-drill.sh` | the visibility paragraph inside step 0a's `WHAT WOULD` text, at **both** uncertain stages (identical wording); the header comment's one-line version of the same claim, with the primary reference named |
| `docs/operations/database-development.md` | the `How that observation fails` row of **both** step-0a tables, with the primary reference linked; the R5 narrative paragraph that carried the same claim |
| `tests/test_database_backup_restore.py` | `test_the_completion_gate_says_what_would_establish_completion` — docstring and assertions rewritten to the corrected distinction, plus a negative assertion that the row-hiding claim is gone; `test_recovery_instructions_match_database_development_documentation` — the visibility block rewritten, the primary reference asserted in the guide, and the withdrawn claim asserted absent from both documents in three forms |
| `docs/review/project-review-remediation-2026-09-08-r5-handback.md` | a dated **Erratum — 2026-09-08, issued with remediation R6** section, prepended before §1; the original submission is preserved below it unaltered |
| `docs/review/project-review-remediation-2026-09-08-r6-handback.md` | this file |
| `docs/review/Handover information` | dated pointer to this handback, prior entries retained |

No other file was modified. No test case was added or removed: the selection
count is unchanged at 204, which is the expected shape of a wording correction.

### The erratum, and exactly what it supersedes

R5 handback §2 gave three reasons for choosing a stop over a
`(pid, backend_start)` completion mechanism. The erratum supersedes:

1. **§2, reason 2**, headed *"Absence of a row is not absence of a backend"*,
   and its supporting sentence about what a non-privileged role sees of another
   role's session. Permissions do not remove the row. What is true, and what the
   reason should have said, is that the columns identifying *which* session it is
   and whether it holds a transaction open may be null.
2. **§2, "The completion/observation distinction, as it is now written"** — the
   second of its two named limits, *"a session whose row you cannot see is not a
   session that has ended"*.

It also corrects, by reference, §5's description of the completion-gate test as
naming "the visibility limit" and §10's request item 3.

**The stop remains an allowed design choice.** §2's reasons 1 and 3 are
untouched — the evidence would be written by the process whose death defines the
failure, and automating the answer invites automating the remedy — and the
corrected reason 2 still tells against relying on a `pg_stat_activity` check for
every recovering role, because the fields such a check would read may be null.
The erratum states that this overstated reason does not by itself reopen the
choice, and it closes nothing.

## 4. Verification

### Interpreter

The documented interpreter is on `oracle-test` at
`/opt/freedom-blades/runtime/venv-web/bin/python`; **the no-SSH restriction
prevents using it, and `oracle-test` was not contacted.** Both interpreters used
here were probed directly in this session and are **local fallbacks on this
host**, not the documented environment:

| Interpreter | Version | pytest |
|---|---|---|
| `/opt/discord-bots/venv/bin/python` | 3.12.3 | 8.4.2 |
| `/opt/discord-bots/venv-web/bin/python` | 3.12.3 | 8.4.2 |

Nothing was installed into any runtime. `TEST_DATABASE_URL` was **unset for
every run** (each invocation used `env -u TEST_DATABASE_URL`), and the runs were
serial.

### Pre-fix regression, measured

Byte-exact pre-R6 copies of the drill and the guide were reconstructed by
reversing each replacement, swapped in, and the two affected tests run against
them; both files were then restored and verified by `sha256sum -c` against
digests taken before the swap:

**2 failed** —
`test_the_completion_gate_says_what_would_establish_completion` and
`test_recovery_instructions_match_database_development_documentation`.
The first failed on `"PostgreSQL restricts"` absent from the banner; the second
on `"restricts columns" in said_by_guide.lower()`.

### Results, final tree

| # | Command | Interpreter | Result |
|---|---|---|---|
| 1 | `bash -n infra/postgresql/backup-restore-drill.sh` | bash | clean |
| 2 | `pytest -q -rs <11 deselections> tests/test_database_backup_restore.py tests/test_filesystem_layout.py` | `/opt/discord-bots/venv` | **204 passed, 11 deselected** |
| 3 | `pytest -q -rs tests/web/test_p3_4_static_assets.py` | `/opt/discord-bots/venv-web` | **111 passed** |
| 4 | `pytest -q tests/phase_5_0_evidence` | `/opt/discord-bots/venv` | **1143 passed** |
| 5 | `python -m compileall -q` over the changed test module and `tools/phase_5_0_evidence` | `/opt/discord-bots/venv` | clean |
| 6 | `git diff --check` | git | clean |
| 7 | manifest re-hash of every covered source | `/opt/discord-bots/venv` | **28 sources, 0 mismatches** |

Codex measured R5 at **204 passed, 11 deselected** for the same selection, with
shell-syntax, whitespace and 28-hash manifest checks passing. Run 2 above is this
tree's own figure and matches, as a wording correction with no added case should.

`tests/test_filesystem_layout.py` and `tests/web/test_p3_4_static_assets.py` were
inspected before being run: no `database` marker, no database fixture, no
`TEST_DATABASE_URL` reference and no PostgreSQL client invocation in either.

### Generated artifacts

No evidence-harness production source changed, so the manifest was verified and
the generated artifacts were left untouched — nothing regenerated, nothing
hand-edited. Manifest version/schema **5** / `phase-5-0-evidence-review-manifest`
and harness version **0.6.0-pre-execution** are unchanged. **No digest was passed
to `--execute`.**

### Deselected: eleven cases, by name

All in `tests/test_database_backup_restore.py`, unchanged from the R2–R5 set, and
**none is claimed to pass against this tree**:

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

No newly database-touching case was introduced, so there is no twelfth
deselection. `tests/test_snapshot_database.py` and
`tests/web/test_identity_migration_backup_restore.py` remain excluded as whole
modules: both are `pytest.mark.database` modules that invoke the real drill.

### Checks not run, and why

| Not run | Reason |
|---|---|
| The eleven deselected cases and the two excluded modules | destructive drill / real database; forbidden here |
| Any PostgreSQL execution, including of `schema-state.sql`, and any observation of `pg_stat_activity` or backend behaviour | no database operation is permitted. The corrected wording rests on the cited PostgreSQL 16 documentation, not on an observation of any server |
| The complete bot and web suites | broad suites are not to be launched hoping to stop before database access; the affected modules were inspected and run individually |
| Anything on `oracle-test`, including either suite under the documented interpreter | the no-SSH restriction |
| Re-running the pristine-schema drill | it is a destructive drill; **its failure remains unresolved and undiagnosed** |
| The evidence-harness executor | no `--execute`, no armed boundary or materializer, no generated vector; unchanged from R13 |
| A configured formatter, linter or type checker | **none is configured in this repository** — no `pyproject.toml`, `ruff.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `.pre-commit-config.yaml`; `pytest.ini` is the only tool configuration present. `shellcheck` is not installed on this host. `compileall`, `bash -n` and `git diff --check` are what is available and were run |

### Preservation of unrelated work

`git status --short --untracked-files=all` was checked at the start and again at
the end. Nothing was reset, reverted, staged, committed, pushed or reformatted;
no roadmap, RAID, decision or gate record was altered; no earlier prompt or
handback was overwritten, and the R5 handback's original submission is intact
below its erratum. The only files touched are the six in §3.

## 5. Limitations

* **Everything here is documentary.** No SQL was executed, no backend was
  contacted, and no PostgreSQL behaviour was reproduced. The corrected
  distinction is taken from the cited PostgreSQL 16 documentation.
* **No target configuration is established**, and none is inferred from the
  reference.
* **The extended `schema-state.sql` has still never run against a PostgreSQL
  server** and still needs authorized validation before operational acceptance.
* **The pristine-schema drill failure remains unresolved**; nothing here is
  offered as its diagnosis.

## 6. Status

* The Optional session-visibility finding is corrected in the drill, the guide,
  the tests and the R5 handback erratum. **No finding, decision, assumption,
  residual risk or package gate is closed by this handback.**
* PR-20260908-R3-1 is not reopened, and this correction is **not** a new
  prerequisite for Codex's recommendation to close it.
* **Package 5.0 remains `not ready`. P5.0-R5 remains Blocking.** Complete R13
  pre-execution approval remains outstanding. PostgreSQL validation of
  `schema-state.sql` and the unresolved pristine-schema failure remain
  outstanding.
* **Every execution restriction held.** No SSH, target-host inspection or
  mutation, database operation, destructive drill, real backend cancellation or
  termination, `--execute`, armed real process boundary or materializer,
  generated-vector execution, deployment, migration `0014`, cutover, OD-62 ruling
  or Package 5.1+ work. No stub test falls through to a real PostgreSQL client.

Returned for independent review. This submission stops before any operational
execution.
