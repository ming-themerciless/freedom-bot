# Prompt for Gemini — disposable server remediation R2

Work in `/opt/freedom-blades/platform` and on the explicitly disposable host
`oracle-test` only where this prompt permits it.

## Authority and required outcome

Codex independently reviewed Gemini's first disposable-server remediation on
2026-09-05. The server is reachable and substantially improved, but two
Blocking and four Important findings remain. Correct those findings, rerun the
required checks from a pristine PostgreSQL 16 baseline, produce a truthful R2
handback, and return to Codex.

Peter Duscha's request for this remediation authorizes rebuilding the
**disposable** PostgreSQL 16 test cluster and its synthetic databases, roles and
test state. It does not authorize any production or staging change.

This prompt also authorizes one bounded repository maintenance fix to
`infra/postgresql/backup-restore-drill.sh` and its existing tests **only if** the
current drill first fails against an untouched, package-default PostgreSQL 16
cluster for the privilege-preservation reason identified below. Preserve the
drill's safety boundaries and recovery behavior.

This prompt does **not** authorize the Package 5.0 evidence harness, C-1/C-3/C-4,
creation of P5.0 evidence identities or journal objects, migration `0014`,
Package 5.0 product implementation, production/staging mutation, deployment,
cutover, OD-62, Package 5.1+, or any real credential or player data on the
disposable host.

## Roles and separation

- Gemini owns this R2 disposable-environment remediation.
- Claude remains the Package 5.0 evidence-harness executor.
- Codex independently reviews this remediation and any later exact execution
  plan and evidence.
- Peter remains Operations Owner and Acceptance Authority.

Gemini must not execute the P5.0 harness, close P5.0-R4/R5, confirm
A-5.0-4/A-5.0-5, approve its own target, or recommend Package 5.0 readiness.

## Required reading and worktree discipline

Before planning or changing anything, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. this prompt;
5. `docs/review/phase-5-0-gemini-disposable-server-remediation-prompt.md`;
6. `docs/review/phase-5-0-gemini-disposable-server-remediation-handback.md`;
7. `docs/operations/disposable-test-server.md`;
8. `docs/operations/database-development.md`;
9. `infra/postgresql/backup-restore-drill.sh`;
10. `tests/test_database_backup_restore.py`;
11. `tests/test_runtime_grants_live.py`;
12. `tests/web/test_p3_2_runtime_grants_and_bounds.py`;
13. `tools/phase_5_0_evidence/targets.py`; and
14. `docs/review/phase-5-0-evidence-harness-execution-plan.md`.

Check local and remote `git status` first. Preserve the complete local dirty
worktree. Do not reset, revert, stage, commit, push or overwrite unrelated work.
Record the remote cluster/database/role/filesystem inventory before rebuilding
anything. Stop if any database or file on `oracle-test` contains production or
player data; report only its path/name and metadata, never its contents.

## Independent-review evidence to reproduce

Codex confirmed:

- PostgreSQL 16.15 is active at port 5432 and `/var/run/postgresql`;
- PostgreSQL 18 is down at port 5433, but `systemctl is-enabled
  postgresql@18-main` reports **`enabled-runtime`**, not disabled;
- `freedom_runtime_test` has the expected restricted attributes and `ubuntu` is
  a member;
- `template1.public` is owned by `ubuntu` with a NULL ACL;
- a temporary database created from untouched `template0` has the actual
  PostgreSQL 16 default:
  `pg_database_owner|pg_database_owner=UC/pg_database_owner,=U/pg_database_owner`;
- the temporary inspection database was dropped immediately afterward;
- the exact focused files currently produce **123 passed, 0 skipped**, not the
  handback's **121 passed, 2 skipped**;
- `.agents/AGENTS.md` and `CLAUDE.md` still contain the old broken
  `--exclude '.env*'` recipe; `CLAUDE.md` still calls PostgreSQL 18 the test
  database server;
- the handback records kernel `6.8.0-1011-oracle`, while the host actually runs
  `7.0.0-1009-oracle`; and
- `/usr/local/bin/{psql,pg_dump,pg_restore,createdb,dropdb}` globally shadow the
  Debian/PGDG client selection with PostgreSQL 16 symlinks.

Do not dispute these observations by citing the R1 handback. Reproduce them
before remediation and concede each finding before presenting its correction.

## DS-R2-1 — Blocking: the green drill depends on a modified template

R1 changed `template1` with:

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

That does not restore “standard clean PostgreSQL 16 defaults.” It creates the
schema as the connected superuser, removes the `pg_database_owner` ownership
contract and changes the ACL inherited by every new database. The passing drill
therefore measured a customized template made to avoid the earlier failure.

### Required correction

Return PostgreSQL 16 to an independently recognizable package-default state.
The preferred method is to rebuild the disposable `16/main` cluster from
package defaults, after recording that it contains synthetic data only. Do not
repair `template1` by another ad hoc `DROP SCHEMA`/`CREATE SCHEMA` sequence.

After rebuild, before provisioning project roles or running migrations:

1. inspect `template0.public` and `template1.public` owner and ACL;
2. prove both carry the package-default PostgreSQL 16
   `pg_database_owner`/`PUBLIC` semantics;
3. create a temporary database from `template1`, prove it inherits those
   semantics, and drop it;
4. create fresh synthetic `freedom_test` and `freedom_dev` databases owned by
   `ubuntu`; and
5. provision `freedom_runtime_test` with the existing exact restricted-role
   contract and grant membership to `ubuntu`.

Then run the backup/restore regression first. If it fails because the drill
does not preserve or correctly compare the standard PostgreSQL 16 schema
ownership/ACL state, add a regression test that fails for that precise pristine
case before changing production code.

Any bounded drill correction must:

- preserve the full pre-drill privilege state that matters to application
  usability, including `pg_database_owner` and `PUBLIC` schema privileges;
- compare stable semantic principals and privileges, not transient OIDs;
- distinguish an absent grant from PostgreSQL's representation of a pseudo-role;
- retain the production-target refusal, Unix-socket verification, dump checksum,
  single-transaction restore, failure reporting and recovery instructions;
- never weaken a mismatch into a warning;
- work on standard PostgreSQL 16 without mutating `template0` or `template1`;
- avoid version-specific output normalization that would conceal a real loss;
  and
- add focused positive and negative tests proving both restoration and refusal.

Do not change the controlled PostgreSQL major or normalize templates merely to
make the test green. If correcting the drill requires a broader operational
contract change, stop and return the exact blocker rather than widening scope.

## DS-R2-2 — Blocking: mandatory agent instructions reproduce stale defects

The canonical `.agents/AGENTS.md` and discovery `CLAUDE.md` still contain the
old synchronization command that excludes `.env.example`; `CLAUDE.md` also
describes PostgreSQL 18 as authoritative. An agent following mandatory
instructions would undo the remediation.

Remove duplicated executable server recipes from `.agents/AGENTS.md` and
`CLAUDE.md`. Keep at most a concise statement that `oracle-test` is explicitly
disposable and a link to the canonical
`docs/operations/disposable-test-server.md`. The operational document must be
the single maintained source for versions, synchronization and test commands.

Keep root `AGENTS.md`'s required-reading link unless a narrower wording is
needed for consistency. Do not weaken the rule that repository and
implementation-plan review gates govern all work.

Add or extend a documentation regression that fails if mandatory entry points:

- contain an independent `rsync` recipe;
- identify PostgreSQL 18 as the authoritative lane;
- grant authority over any host other than `oracle-test`; or
- conflict with `docs/operations/disposable-test-server.md`.

## DS-R2-3 — Important: PostgreSQL 18 is not persistently disabled

R1 says PostgreSQL 18 is disabled, but systemd reports `enabled-runtime`.
Establish an unambiguous persistent policy:

- PostgreSQL 16 `16/main` is enabled and active on port 5432;
- PostgreSQL 18 `18/main` is inactive and cannot auto-start on boot;
- if PostgreSQL 18 remains installed, its cluster start policy and systemd state
  must both express manual/disabled operation and it remains on port 5433; and
- a reboot-free verification must show the persistent unit/cluster policy, not
  merely current inactivity.

If systemd's generated PostgreSQL units cannot truthfully report `disabled`,
document and test the Debian/PGDG cluster `start.conf` mechanism actually used.
Do not claim a state different from the command output.

## DS-R2-4 — Important: kernel baseline is misstated

Record the kernel actually running at verification time. Determine, using
read-only inspection, the kernel version used by the intended production host
for Package 5.0. Do not read secrets or unrelated configuration.

If production uses kernel 6.8.x while `oracle-test` runs kernel 7.0.x, do not
call the target representative without qualification. Choose one of:

1. boot the disposable VM into an available matching 6.8.x kernel; or
2. return the mismatch as an explicit blocker requiring Peter/Codex direction.

Do not silently amend Package 5.0's capability assumptions from kernel 6.8 to
7.0, and do not change or reboot production. A disposable-VM reboot is allowed
only if needed to select an already installed matching kernel; record before and
after kernel and service state.

## DS-R2-5 — Important: global client symlinks hide version selection

Remove the global `/usr/local/bin` PostgreSQL client symlinks created by R1,
after resolving and recording their exact targets. Use an explicit,
review-visible PostgreSQL 16 client selection instead:

- preferred: prepend `/usr/lib/postgresql/16/bin` to `PATH` only in the bounded
  test command or wrapper owned by this repository; or
- invoke the exact versioned binary paths directly.

Every destructive database command must prove both client major and connected
server major are 16 before mutation. Do not rely on ambient `PATH`, Debian
`pg_wrapper` inference or a globally shadowed executable. PostgreSQL 18
compatibility commands, if retained, must similarly name version 18 explicitly.

Update the operational document and tests accordingly. Do not install a generic
system-wide wrapper to conceal version selection.

## DS-R2-6 — Important: verification totals are not reproducible

R1 reported 121 passed and 2 skipped for the focused files. Codex reran those
files and obtained 123 passed with no skips. Establish a deterministic sequence:

1. rebuild/reset the test database from the standard template;
2. provision the restricted role;
3. run migrations/setup exactly as the fixtures require;
4. run the focused files once and record every skip reason with `-rs`;
5. reset again through the same procedure;
6. rerun the focused files and require the same pass/skip result; and
7. only then run the complete suites serially.

Do not reuse R1 totals. Explain any count change from the accepted local totals
by named collected tests or skip conditions. A state-dependent difference is a
finding, not harmless arithmetic.

The bot suite must use explicitly listed synthetic, non-secret environment
variables sufficient for `config.py` import, with dummy positive numeric IDs,
a dummy Sheet ID and a minimal JSON object. Do not create a credential-shaped
private key, copy `.env`, contact Discord/Google, or merely say “synthetic
configuration” without recording the variable names and bounded placeholder
forms.

## P5.0 target remains proposed, not approved

Preserve the absence of:

- `fb_evidence_*` databases;
- `freedomcoord`, `freedomsheet`, `fbprobe` and `freedomjournal` identities or
  groups;
- `/var/lib/fb-evidence-p50`;
- evidence HBA/ident entries; and
- `fb-evidence-*` transient units.

Do not replace `UNASSIGNED` in the execution plan. Update the proposed target
facts only with verified values. An IP address is routing information, not a
stable host identity; include a one-way digest of the disposable host's
machine-id or another approved non-secret stable identifier without recording
the raw value. Peter must still confirm disposability, and Claude must regenerate
the exact plan for Codex review before execution.

## Required verification sequence

Run all database suites serially against a freshly created standard PostgreSQL
16 `freedom_test`. Use explicit versioned client selection and the Unix socket.

At minimum:

```sh
export PATH='/usr/lib/postgresql/16/bin:<SYSTEM_PATH_WITHOUT_LOCAL_PG_SHADOWS>'
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'

/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs \
  tests/test_database_backup_restore.py \
  tests/test_runtime_grants_live.py \
  tests/web/test_p3_2_runtime_grants_and_bounds.py \
  tests/test_filesystem_layout.py

# Reset through the documented standard procedure and repeat the focused run.

/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/test_*.py
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
/opt/freedom-blades/runtime/venv-web/bin/python -m compileall -q \
  tools/phase_5_0_evidence tests/phase_5_0_evidence
git diff --check
```

Replace the placeholder system path with an explicitly recorded safe value; do
not execute the literal placeholder. Before each destructive run, record:

- resolved `psql`, `pg_dump`, `pg_restore`, `createdb` and `dropdb` paths and
  versions;
- connected server version, port, socket directory and database;
- `template1.public` and `freedom_test.public` owner/ACL;
- restricted-role attributes and membership; and
- absence of ambient `PGHOSTADDR`, `PGSERVICE`, `PGSERVICEFILE` and `PGOPTIONS`.

Passing evidence requires:

- package-default PostgreSQL 16 template semantics remain unchanged;
- both focused runs have identical totals and skip reasons;
- bot and web suites have no unexpected failure;
- web has exactly 80 documented permission-matrix skips;
- no restricted-role skip;
- Foundry has no failure;
- compilation and `git diff --check` pass;
- no external application call;
- no secret or player data; and
- no P5.0 evidence object or production/staging change.

## Required R2 handback

Append a clearly dated R2 section to
`docs/review/phase-5-0-gemini-disposable-server-remediation-handback.md`.
Preserve R1 as superseded history. The R2 section must:

- concede DS-R2-1 through DS-R2-6 before presenting corrections;
- list every local and remote change;
- give the pristine template owner/ACL before and after all tests;
- identify any backup/restore code correction and its regression-first failure;
- show persistent PostgreSQL 16/18 cluster policy;
- show removal of the global client symlinks and explicit client selection;
- state the actual kernel and production-kernel comparison;
- give both focused-run results and exact skip reasons;
- give fresh full-suite totals, skips, warnings and durations;
- list the synthetic environment variable names and placeholder forms without
  secret material;
- inventory cleanup and prove no P5.0 evidence object exists;
- retain `UNASSIGNED` and request Peter's target confirmation plus Codex review;
  and
- claim no P5.0 finding, assumption, operational check or readiness item closed.

Update `docs/review/Handover information` only after every required check passes.
If any check fails, make the handover state the remediation remains incomplete
and name the blocker; do not present a green summary.

Stop after returning the R2 handback to Codex. Do not execute the evidence
harness, close P5.0-R4/R5, confirm A-5.0-4/A-5.0-5, rule OD-62, authorize
Package 5.0, or begin Package 5.1.
