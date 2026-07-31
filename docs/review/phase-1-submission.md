# Phase 1 — Review Submission

Status: **ACCEPTED by the maintainer on 2026-07-31. Phase 1 is complete and the
plan §17 decision log is satisfied.** The three Codex Phase 1 blocking findings are resolved
(§12), the Codex Phase 1 **re-review** blocking finding — Alembic's target guard
could approve a remote PostgreSQL server — is resolved (§15), the Codex
Phase 1 **second re-review** blocking finding — the loopback address check could
not distinguish a local server from an SSH port forward — is resolved (§16), and
the Codex Phase 1 **third re-review** blocking finding — an inherited
`PGHOSTADDR` turned the documented socket URL into a TCP connection while static
validation still called it a socket — is resolved (§17). The
plan §17 decision log is now satisfied: **all 15 decisions are closed** (§13).

This is a **narrow Codex re-review request** covering §12, §13, §15, §16 and
§17. It is not a claim that Phase 1 is approved.

> **§16 supersedes part of §12 and §15.** Both of those sections say the live
> address check catches a port-forward or a pooler. **That claim was false**; it
> is corrected in §16 and in the code and operations documentation. The earlier
> sections are left as written — this is the review history, not a redraft of it
> — and every statement they make about that check should be read through §16.
>
> **§17 supersedes part of §15 and §16.** §15 says *"`?hostaddr=` is resolved as
> the host"* and §16's acceptance table implies a socket URL is a socket. Both
> were wrong whenever `PGHOSTADDR` was inherited from the environment: `host`
> and `hostaddr` are separate libpq parameters and `hostaddr` decides where the
> connection goes. Those sections are likewise left as written; read every
> statement they make about `hostaddr` through §17.

Date: 2026-07-31 (revised after the Codex Phase 1 third re-review; §1–§15 date from 2026-07-30, §16 from 2026-07-30/31)

Nothing is committed or pushed. Phase 2 has not been started.

---

## 0. What this document is

The plan §16.3 milestone handoff for Phase 1. It reports what exists, what was
found and fixed during review, what was verified and how, and what a reviewer
should attack first.

Phase 1 work already existed as uncommitted changes when this session began. It
was preserved and reviewed, not rewritten. The corrections in §4 are edits to
that work.

---

## 1. Requirements implemented

Plan §12 Phase 1 deliverables:

| Deliverable | Where | State |
|---|---|---|
| PostgreSQL development setup | `docs/operations/database-development.md`, `adapters/database/config.py`, `.env.example` | Done |
| Migration framework | `alembic.ini`, `migrations/` | Done |
| Identity, character, access, external mapping, audit, idempotency tables | `adapters/database/tables.py`, `migrations/versions/0001_database_foundation.py` | Done |
| Repository interfaces and database adapters | `application/repositories.py`, `adapters/database/repositories.py` | Done, deliberately narrow |
| Transaction boundary conventions | `adapters/database/unit_of_work.py`, ADR 0003 | Done |
| Database integration-test setup | `tests/conftest.py`, `pytest.ini` | Done |
| Backup/restore development procedure | `infra/postgresql/backup-restore-drill.sh`, ops doc | Done and exercised |

Plan §12 Phase 1 acceptance criteria:

| Criterion | Evidence |
|---|---|
| Migrations apply to an empty database | `test_migrations_apply_to_empty_postgresql_and_downgrade`; also run by hand after `DROP SCHEMA public CASCADE` (§5) |
| Downgrade/recovery strategy is documented | Ops doc, *Downgrade and recovery strategy* — including that `downgrade()` is **not** the production rollback |
| Constraints reject invalid data | 40 PostgreSQL schema and constraint tests in `tests/test_database_postgresql.py` |
| Repository contract tests pass | 12 tests in `tests/test_database_repositories.py`, now against migrated PostgreSQL |
| Current bot remains unchanged in production behaviour | §7 |

### Deliberately not built

`service_principals`, `sessions`, `external_worlds`, `sync_*`, and every game-state
table in plan §7.3–7.5. None has a Phase 1 use case, domain model or test, and
plan §7.3 says not to create every future table in the first migration. The
repository interfaces cover only `Character` and `DiscordUser` for the same
reason.

---

## 2. Files changed

### Added (untracked)

```
alembic.ini
migrations/env.py
migrations/script.py.mako
migrations/README.md
migrations/versions/0001_database_foundation.py
adapters/__init__.py
adapters/database/__init__.py
adapters/database/config.py
adapters/database/metadata.py
adapters/database/tables.py
adapters/database/mappers.py
adapters/database/repositories.py
adapters/database/unit_of_work.py
application/errors.py
application/repositories.py
domain/__init__.py
domain/identity.py
infra/postgresql/runtime-grants.sql.tmpl
infra/postgresql/backup-restore-drill.sh      ← added during this review
docs/operations/database-development.md
docs/review/phase-1-submission.md             ← this document
tests/conftest.py                             ← added during this review
tests/test_runtime_grants.py                  ← added during this review
tests/test_database_backup_restore.py         ← added during this review
tests/test_database_config.py
tests/test_database_postgresql.py
tests/test_database_repositories.py
tests/test_database_schema.py
tests/test_identity_domain.py
tests/test_migration_safety.py                ← added during the re-review (§15)
adapters/database/safety.py                   ← added during the re-review (§12)
tests/test_database_safety.py                 ← added during the re-review (§12)
```

### Modified (tracked)

```
.env.example      APP_ENVIRONMENT, DATABASE_URL, TEST_DATABASE_URL placeholders
pytest.ini        `database` marker
requirements.txt  SQLAlchemy>=2.0.36,<2.1 · alembic>=1.14,<2 · psycopg[binary]>=3.2.3,<4
```

`docs/discovery/*`, `docs/operations/topology.md` and `docs/rules/field-ownership.md`
also carry uncommitted modifications. Those are **Phase 0 edits that predate this
session** and were left untouched.

No file under `ext/`, `models/`, `helpers/`, `connectors/`, `main.py`, `config.py`
or `music.py` was modified. `.env` was not read or modified.

---

## 3. Migrations added

One: **`0001_database_foundation`**, the only head.

Nine tables: `discord_users`, `discord_guild_memberships`,
`discord_membership_roles`, `characters`, `character_access`,
`external_actor_mappings`, `sheet_row_mappings`, `audit_events`,
`idempotency_keys`.

Conforming to ADR 0003:

- application-generated UUID primary keys, never derived from external data
  (`domain.identity.Character.create` calls `uuid4()`; nothing computes an ID
  from a sheet row, name or Foundry `_id`);
- Discord snowflakes as `BIGINT` everywhere, asserted against
  `information_schema` rather than only against the mapped metadata;
- every timestamp `TIMESTAMPTZ`, asserted by a query that finds *any*
  non-`timestamptz` timestamp column in the schema;
- enumerations as `TEXT` + `CHECK`, no PostgreSQL `ENUM` types;
- `characters.version INTEGER NOT NULL DEFAULT 0` for optimistic concurrency;
- every foreign key declares `ON DELETE` explicitly, asserted both in metadata
  and in `pg_constraint` (`confdeltype <> 'a'`).

**`0001` was edited in place rather than superseded by a `0002`.** It has been
applied to no durable database — `freedom_dev` is empty and was verified empty —
so the ADR 0003 rule *"an applied migration is never edited"* is not engaged.
Once this gate passes and the migration is applied anywhere, that stops being
true.

---

## 4. Findings

Classified per plan §16.4. Everything Blocking and Important below was **fixed
in this session**, each with a regression test.

### Blocking

**B-1 — `character_access` uniqueness erased revocation history.**
The table carried `UNIQUE (character_id, discord_user_id)` across *all* rows.
Because it also carries `active`, `revoked_at`, `reason` and
`audit_correlation_id`, a revoke-then-re-grant — an ordinary Council workflow
under plan §4.2 — could not insert a second row. The only way to re-grant was to
`UPDATE` the revoked row back to active, overwriting `revoked_at` and the
revocation's reason: exactly the erasure `.agents/AGENTS.md` forbids
(*"Corrections use explicit compensating actions rather than erased history"*).
It also made a `viewer` → `owner` promotion an in-place mutation of the record
that is supposed to evidence the original grant.

*Fix:* the table-wide unique constraint is replaced by a partial unique index
`uq_character_access_one_active_link (character_id, discord_user_id) WHERE active`.
At most one *active* link per user and character; revoked rows accumulate as
history.
*Tests:* `test_revoked_grant_is_kept_as_history_and_access_can_be_regranted`,
`test_duplicate_active_link_is_rejected`,
`test_character_access_uniqueness_does_not_erase_revocation_history`.

**B-2 — the test suite was an unguarded destructive command.**
`tests/test_database_postgresql.py` ran `alembic downgrade base` — which drops
every table — against whatever `TEST_DATABASE_URL` named. The only check was
that the URL started with `postgresql`. Pointing it at the production or staging
URL, by a stale shell export or a copied CI variable, would have destroyed that
database on `pytest`.

*Fix:* `tests/conftest.py` validates the target before any fixture runs and
**fails the run** (never skips) unless the URL is PostgreSQL, is the
`freedom_test` database, is loopback-only, and differs from `DATABASE_URL`.
*Verified by hand* against `freedom_production`, a remote host, and a URL equal
to `DATABASE_URL` — all three refused (§5).

### Important

**I-1 — repository contract tests did not touch the schema they claim to test.**
They ran against `sqlite+pysqlite:///:memory:` with tables created from metadata
via `Table.create()`. ADR 0003 is explicit that *"repository and migration tests
run against real PostgreSQL"*, and SQLite exercises neither the migration output
nor PostgreSQL type and constraint behaviour. The acceptance criterion
*"repository contract tests pass"* was being met against a store production never
uses.
*Fix:* they run against the migrated PostgreSQL database, inside a rolled-back
transaction. Four tests were added covering transaction atomicity, partial-state
rollback, and 64-bit snowflake precision.

**I-2 — the PostgreSQL tests were order-dependent and left rows behind.**
Test 2 and 3 relied on test 1 having re-migrated the database; running
`test_postgresql_rejects_invalid_level_and_duplicate_mapping` alone failed with
a unique violation on rows a previous run had left behind.
*Fix:* session-scoped `migrated_database`, per-test `db_connection` that always
rolls back, and `committed_database` that truncates for the few tests that must
really commit. Verified: single test in isolation passes, the file passes twice
in a row, and the database holds zero rows afterwards.

**I-3 — `updated_at` never advanced.**
`characters.updated_at` and `discord_users.updated_at` had a `server_default` but
no update behaviour, and `SqlAlchemyCharacterRepository.save()` did not set them,
so both columns permanently held their insert value while the row changed
underneath.
*Fix:* `onupdate=func.now()` on both columns. This is SQLAlchemy-side, so the DDL
and therefore `alembic check` are unaffected. `now()` is the *transaction*
timestamp, consistent with `created_at`. Raw SQL that bypasses the mapped table
also bypasses this.
*Test:* `test_saving_a_character_advances_updated_at`, confirmed to fail when the
`onupdate` is removed.

**I-4 — `audit_events.actor_discord_user_id` had no foreign key.**
ADR 0003 requires foreign keys to be *"always declared, with explicit ON DELETE
behaviour"*. Without one, audit rows could attribute an action to a snowflake
that is not a known user, and a user carrying audit history could be deleted,
silently orphaning the attribution.
*Fix:* `FOREIGN KEY … ON DELETE RESTRICT`, still nullable for import, scheduled
and system actions (reason recorded in the column comment). Deleting a user with
audit history is now refused, which forces any future erasure requirement through
an explicit, designed anonymisation path rather than a cascade.
*Tests:* `test_audit_actor_must_be_a_known_discord_user`,
`test_deleting_a_user_with_audit_history_is_refused`.

**I-5 — the configuration safety boundary had no consumer and rejected the
documented URL form.**
`DatabaseSettings` — the class that enforces "development must be `freedom_dev`,
production must be `freedom_production`, loopback only" — was imported by nothing
but its own unit test. Migrations read `os.environ["DATABASE_URL"]` raw. Separately,
its host check rejected `postgresql+psycopg:///freedom_test`, the local
Unix-socket form the ops document itself prescribes, because `make_url` reports
no host.
*Fix:* a missing host or a socket-directory path counts as loopback; and
`migrations/env.py` now validates every Alembic invocation through
`DatabaseSettings`, keyed on `APP_ENVIRONMENT`, **defaulting to `development`**.
A bare `alembic upgrade head` can therefore only reach `freedom_dev`; reaching
staging or production is a deliberate act. Verified: pointing a default-environment
migration at `freedom_test` is refused (§5).

**I-6 — grant timestamps were unordered.**
`revoked_at` before `granted_at`, or `expires_at` before `granted_at`, were
accepted.
*Fix:* `CHECK (revoked_at IS NULL OR revoked_at >= granted_at)` and
`CHECK (expires_at IS NULL OR expires_at > granted_at)`, with tests.

**I-7 — nothing asserted the *physical* column types.**
`tests/test_database_schema.py` inspected the SQLAlchemy metadata only, so a
type that mapped differently in PostgreSQL would not have been caught.
*Fix:* `information_schema`/`pg_constraint` assertions for `bigint`, `uuid`,
`timestamptz` (schema-wide, not a fixed column list), timezone-aware round trip,
and explicit `ON DELETE` on every foreign key.

**I-8 — the backup/restore procedure was prose only.**
Plan §14.3 asks for *"restore tests, not merely backup success messages"*.
*Fix:* `infra/postgresql/backup-restore-drill.sh` dumps with `pg_dump -Fc`,
records a SHA-256, destroys the schema, restores with `pg_restore`, and diffs the
table/row inventory. It refuses any database but `freedom_dev`/`freedom_test`.
Driven by `tests/test_database_backup_restore.py`, including the refusal path.

**I-9 — the runtime grants template was unverified.**
Append-only audit depends entirely on that file being correct and complete; a
table added later would silently receive no grant, or the wrong one.
*Fix:* `tests/test_runtime_grants.py` asserts every table in the metadata appears
exactly once with the right grant, that `audit_events` receives only
`SELECT, INSERT`, that no `CREATE`/`ALL`/`SUPERUSER` is granted, and that no
credential is embedded. It parses statements with `--` comments stripped, so
prose cannot mask a grant. This checks the *template*; see §6 for what remains
unverified.

### Ruled during review

**R-1 — character ownership and Council reach (was O-1).**
Recorded as [OD-37](../discovery/open-decisions.md). Maintainer ruling,
2026-07-30: *"A character has exactly one owner. However, the Guild Council
members can access and modify all characters. Modifications should be logged."*

Implemented in Phase 1:

- `uq_character_access_one_active_owner` — a partial unique index on
  `character_id WHERE active AND access_kind = 'owner'`. `co_owner`, `delegate`
  and `viewer` stay unlimited. Because it covers active rows only, an ownership
  handover is revoke-then-grant and the outgoing owner's row keeps its
  `revoked_at` and reason.
- **The "at least one" half is not, and cannot be, a table constraint.**
  PostgreSQL cannot require a row in another table without a deferred trigger,
  and the Phase 2 importer must create a character before Council has resolved
  ownership — the same reason `characters.level` is nullable. So the database
  enforces *at most* one owner, and *at least* one is an application invariant.
  **Phase 2's reconciliation report must list every character with no active
  owner.** This is the one part of the ruling the schema does not hold, and it is
  stated here rather than quietly downgraded.
- **Council reach is role-derived.** Council members get no access rows;
  their capability comes from the configured role snowflake in
  `discord_membership_roles` (OD-18 supplies it). `guild_council` is therefore
  deliberately *not* an `access_kind`, and a test asserts it is rejected. Any
  Phase 3 query answering "may this user modify this character?" from
  `character_access` alone is wrong.
- **`audit_events.actor_capability`** (`NOT NULL`, `CHECK` over the plan §4.1
  roles) records the authority a modification was made under, so a Council
  override is distinguishable from an owner editing their own character. Plan
  §4.3 already required *"the acting Discord user and current authorization
  context"*; the ruling is what makes the second half concrete. A companion check
  requires an acting user unless the capability is `service_principal` or
  `system`.
- Enforcing the reach itself is Phase 3 authorization work. Phase 1 provides the
  role snapshot table it will read and the audit column it must write.

*Tests:* `test_a_character_has_at_most_one_active_owner`,
`test_one_owner_does_not_limit_co_owners_delegates_or_viewers`,
`test_ownership_can_be_transferred_after_the_previous_owner_is_revoked`,
`test_guild_council_is_not_an_access_kind`,
`test_audit_records_the_capability_a_modification_was_made_under`,
`test_an_unknown_actor_capability_is_rejected`,
`test_a_human_capability_requires_an_acting_user`,
`test_automated_actions_may_have_no_acting_user`, plus three metadata assertions.

**R-2 — the downgrade named indexes it did not always own.**
Found while applying R-1: `downgrade()` dropped `character_access` and
`audit_events` indexes by name before dropping their tables. Against a database
whose index set differed — exactly what happens when a migration is revised
before release — `DROP INDEX` failed and left the schema stamped at `0001`.
`DROP TABLE` removes a table's own indexes, so the explicit calls were redundant
as well as fragile; they are gone. Verified by a full base → head → base → head
cycle.

### Optional — reported, not changed
- **O-2 — `characters.display_name` has no uniqueness rule.**
  `docs/discovery/sheet-inventory.md:636` records it as "to be decided". Left open.
- **O-3 — `external_actor_mappings.last_instance` has no consumer** and no
  grounding in the ADRs. `docs/discovery/foundry-mapping.md` §3 is explicit that
  the Foundry instance is connection configuration and not identity, which
  suggests this belongs to `sync_runs` in Phase 7 rather than to the mapping row.
  `relink_fingerprint`, by contrast, *is* grounded (foundry-mapping.md §4.1) and
  correctly `NOT NULL`.
- **O-4 — `discord_membership_roles` replaces plan §7.1's
  `discord_role_snapshots`.** Deliberate; documented in the ops doc.
- **O-5 — `SqlAlchemyCharacterRepository.save()` reports a missing row as
  `ConcurrencyConflictError`.** Both are `rowcount != 1`. Harmless now, worth
  splitting when the first real use case exists in Phase 4.
- **O-6 — `character_access.character_id` cascades on character deletion** while
  `discord_user_id` restricts. The asymmetry is defensible — a character is
  platform-owned, a Discord user is an external identity — but it means an
  administrative character deletion silently removes its access history. Flagged
  for the reviewer rather than changed, because it is a data-authority decision.
- **O-7 — `idempotency_keys.expires_at` has no index or reaping job.** Not needed
  until Phase 4 writes to it.

---

## 5. Commands run, and their exact results

All run from `/opt/discord-bots/freedom-bot` using the repository's own
`./venv` (Python 3.12.3, SQLAlchemy 2.0.51, Alembic 1.18.5, psycopg 3.3.4)
against the disposable local database `freedom_test` (PostgreSQL 16.14).

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest -q` | **295 passed**, 1 warning (pre-existing `audioop` deprecation from Pycord) |
| 2 | `TEST_DATABASE_URL=… ./venv/bin/python -m pytest -m database -q` | **54 passed**, 241 deselected |
| 3 | `./venv/bin/python -m pytest -q` (no `TEST_DATABASE_URL`) | **242 passed, 53 skipped** — the suite stays green without PostgreSQL |
| 4 | `APP_ENVIRONMENT=test DATABASE_URL=… ./venv/bin/alembic downgrade base` | `Running downgrade 0001 -> ` |
| 5 | `APP_ENVIRONMENT=test DATABASE_URL=… ./venv/bin/alembic upgrade head` | `Running upgrade  -> 0001` |
| 6 | `APP_ENVIRONMENT=test DATABASE_URL=… ./venv/bin/alembic check` | `No new upgrade operations detected.` |
| 7 | `./venv/bin/alembic heads` | `0001 (head)` — single head |
| 8 | `./venv/bin/python -m compileall -q adapters application domain migrations tests infra models helpers connectors config.py main.py` | exit 0 |
| 9 | `git diff --check HEAD` | exit 0; no trailing whitespace in untracked files either (`grep -rlP '[ \t]+$'` empty) |
| 10 | `bash -n infra/postgresql/backup-restore-drill.sh` | exit 0 |
| 11 | `./infra/postgresql/backup-restore-drill.sh freedom_test <dir>` | `Restore verified for freedom_test`; inventory diff empty |

### Empty-database proof

`DROP SCHEMA public CASCADE; CREATE SCHEMA public;` reduced `freedom_test` to
**0 tables**, then `alembic upgrade head` → `alembic check` (clean) →
`alembic downgrade base` (only `alembic_version` left) → `alembic upgrade head`.
So the migration applies to a genuinely empty database, not merely to one where
a previous downgrade ran.

### Destructive-guard proof (run by hand)

| `TEST_DATABASE_URL` | Outcome |
|---|---|
| `postgresql+psycopg:///freedom_production` | `Failed: Refusing to run destructive database tests: test must use database 'freedom_test', not 'freedom_production'.` |
| `postgresql+psycopg://app:x@db.example/freedom_test` | `Failed: … test PostgreSQL must be loopback-only on this shared host.` |
| equal to `DATABASE_URL` | `Failed: TEST_DATABASE_URL must not be the runtime DATABASE_URL: these tests drop every table.` |
| unset | 53 skipped, run continues |

And for migrations: `DATABASE_URL=…/freedom_test` with no `APP_ENVIRONMENT` →
`ValueError: development must use database 'freedom_dev', not 'freedom_test'.`

### Regression tests confirmed to actually fail without their fix

- `test_saving_a_character_advances_updated_at` — fails with `AssertionError`
  when `onupdate=func.now()` is removed (verified by temporary edit, reverted).
- `test_revoked_grant_is_kept_as_history_and_access_can_be_regranted` — the old
  table-wide unique constraint rejects the second insert by construction.

### Secret and data scans

`grep -rniE "password=|secret|token|BEGIN PRIVATE KEY|postgres://user:pass@"` over
every added and modified file returns only `__PLACEHOLDER__` forms in
`.env.example`, prose in `docs/operations/topology.md`, and the synthetic Phase 0
CSV fixture. No credential, no real player data, no production identifier is
introduced. `.env` was never read.

---

## 6. Checks **not** run, and why

| Check | Why not |
|---|---|
| Formatter, linter, type checker | **None is configured or installed.** No `pyproject.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `tox.ini` exists; `requirements-dev.txt` pins only `pytest`. `ruff`, `black`, `flake8`, `mypy`, `pyright` and `isort` are all absent from `./venv`. Adding one is a repository-wide decision that would reformat Phase 0 and bot code, so it is proposed in §9 rather than done inside Phase 1. |
| Live grant rehearsal of `runtime-grants.sql.tmpl` | The database role available here (`foundry`) has `rolsuper=f, rolcreatedb=f, rolcreaterole=f`. Creating the restricted role and proving that `UPDATE audit_events` raises `InsufficientPrivilege` is impossible on this host. **Only the template is verified, not its effect.** This is the single largest gap in the append-only claim and is a deployment-time verification step (§8). |
| Restore into a *separate* empty database | No `CREATEDB`. The drill restores into the same disposable database after dropping its schema, which proves the dump and the restore but not a cross-database recovery. |
| Any production, staging, Discord, Sheets, Foundry or live-PostgreSQL interaction | Forbidden by `.agents/AGENTS.md` and by the task. `freedom_dev` was read (confirmed empty) but never written. |
| Bot runtime smoke test | Would require a live Discord token. Instead: no bot file was modified (§7), and every bot module still imports cleanly. |
| Performance/index tuning | No query workload exists yet. Deferred. |

---

## 7. Existing bot production behaviour

Unchanged, and verified rather than assumed:

- `git diff --stat` over `main.py`, `config.py`, `ext/`, `models/`, `helpers/`,
  `connectors/`, `music.py`: **no changes**. The only tracked runtime change is
  three added lines in `requirements.txt`.
- `grep` for `adapters`, `from domain`, `application.repositories`,
  `DATABASE_URL`, `sqlalchemy`, `alembic` across all bot code: **no matches**.
  The Phase 1 code is not reachable from the running bot.
- `config.py` neither reads nor requires `DATABASE_URL` or `APP_ENVIRONMENT`, so
  the bot starts with an unchanged `.env`.
- `config`, `models.actor`, `models.money`, `models.resource`,
  `helpers.craft_calculator` and `application.actor_locks` all import cleanly.
- The 242 non-database tests pass identically with and without PostgreSQL
  configured.

---

## 8. Configuration and deployment changes

**Configuration.** Three new variables, all optional for the bot and documented
in `.env.example`:

- `APP_ENVIRONMENT` — `development` (default) | `test` | `staging` | `production`.
  Selects which database name is permitted.
- `DATABASE_URL` — must name the database matching `APP_ENVIRONMENT` and be
  loopback or local-socket.
- `TEST_DATABASE_URL` — must be `freedom_test` and must differ from `DATABASE_URL`.

**Dependencies.** `SQLAlchemy>=2.0.36,<2.1`, `alembic>=1.14.0,<2`,
`psycopg[binary]>=3.2.3,<4`. Already installed in `./venv`. The bot does not
import them, so a bot restart is not required by Phase 1.

**Deployment, when this gate passes** (nothing below has been done):

1. Create the databases and roles in the ops doc's table. The runtime role must
   not own the schema.
2. `pg_dump -Fc` the target first if it is not empty; checksum it off-host.
3. `APP_ENVIRONMENT=<env> DATABASE_URL=<migration-role URL> alembic upgrade head`,
   run as the **migration** role, as a deployment step, never by the application.
4. Apply `infra/postgresql/runtime-grants.sql.tmpl` as the schema owner with
   `__APP_ROLE__` substituted through the deployment's secret-safe templating.
5. **Verify the append-only grant for real** — connect as the runtime role and
   confirm `UPDATE audit_events …` and `DELETE FROM audit_events …` both fail
   with `InsufficientPrivilege`. This is the check §6 could not run here, and it
   should not be treated as done until someone has seen it fail.
6. `alembic check` against the deployed database.
7. No bot or service restart is required.

---

## 9. Unresolved questions for the maintainer

1. ~~May a character have more than one active `owner`?~~ **Ruled 2026-07-30 —
   see R-1 and OD-37.** One residual question follows from it: **when Phase 2
   finds a character with no active owner, is that an import error that blocks
   the run, or a reconciliation exception for Council to resolve?** The schema
   permits the state, so someone must decide what happens next.
2. **Must `characters.display_name` be unique** — globally, among active
   characters, or not at all? Left open per sheet-inventory.md:636.
3. **What does an expired grant mean operationally?** `expires_at` is stored, and
   ordering is now constrained, but nothing marks an expired row inactive. Is
   expiry evaluated at read time, or swept by a job that writes `revoked_at`?
   This affects whether `WHERE active` is a sufficient authorization predicate in
   Phase 3.
4. **Should deleting a character really delete its access history?** (O-6)
5. **Should a formatter/linter/type checker be adopted, and which?**
   `.agents/AGENTS.md` says to run the configured ones; none is configured. This
   is a repository-wide change and needs a decision plus its own scoped commit.
6. **Is `external_actor_mappings.last_instance` wanted at all?** (O-3) Removing
   it is free now and a migration later.
7. Plan §17 lists **fifteen** decisions *"required before Phase 1 completion"*.
   They have now been audited one by one against `open-decisions.md` and the
   ADRs: **4 are closed, 1 is partly closed, and 10 are unresolved.** The full
   matrix is **§13**, and it is why this submission reports Phase 1 as blocked
   rather than complete. *(An earlier revision of this document said "fourteen"
   and did not audit them; both are corrected.)*

---

## 10. Recommended reviewer focus

In descending order of what would hurt most if wrong:

1. **`character_access` and the two paths to a character** —
   `adapters/database/tables.py:80-150` and the ops doc's *authorization model*
   section. The B-1 fix makes rows a history, so "current access" is
   `WHERE active`; the R-1 ruling then puts Council reach entirely *outside*
   this table. Both readings have to survive into Phase 3, and the second is the
   easy one to get wrong: an authorization query written against
   `character_access` alone would silently deny Council.
2. **The append-only audit claim** — `infra/postgresql/runtime-grants.sql.tmpl`
   plus §6 and §8 step 5. The schema does not enforce append-only; a grant does,
   and that grant has never been rehearsed. This matters more after R-1: *"modifications
   should be logged"* is only as strong as the guarantee that the log cannot be
   rewritten. Decide whether the template plus a deployment-time check is
   sufficient assurance, or whether a rule/trigger should back it up.
3. **`actor_capability` as a vocabulary** — is `guild_member`,
   `character_owner`, `dm`, `guild_council`, `platform_administrator`,
   `service_principal`, `system` the right set, and is `NOT NULL` the right
   strictness? It is taken from plan §4.1, but it is new in this session and
   every future audit write must supply it.
4. **The `ON DELETE` matrix** — `CASCADE` from `characters` to access and
   mappings, `RESTRICT` to `discord_users` from access and audit. This is a
   data-authority decision encoded in DDL (O-6).
5. **The environment guard** — `adapters/database/config.py` and
   `migrations/env.py`. It is the only thing standing between a mistyped
   `DATABASE_URL` and a production migration. Is defaulting `APP_ENVIRONMENT` to
   `development` the right failure mode, or should it be mandatory?
6. **Transaction boundaries** — `adapters/database/unit_of_work.py` and
   `test_a_repository_write_is_not_visible_before_the_use_case_commits`. Phase 5's
   "trade/crafting cannot partially apply" rests entirely on this shape.
7. **Migration reversibility** — `migrations/versions/0001_database_foundation.py`
   against `adapters/database/tables.py`. `alembic check` is clean, but it does
   not compare `server_default` drift; a manual read of the two side by side is
   worth the ten minutes.
8. **Whether editing `0001` in place was acceptable** (§3). If the reviewer
   disagrees, the alternative is a `0002` carrying the B-1/I-4/I-6 changes.

---

## 11. Repository state

Branch `docs/platform-plan`, nothing committed, nothing pushed, no remote
touched. `git status` shows 7 modified tracked files (2 of them Phase 0 edits
that predate this session, plus `.env.example`, `pytest.ini`, `requirements.txt`
and 2 more Phase 0 docs) and 16 untracked paths.

`.env`, credentials, production services, live PostgreSQL, Discord, Google
Sheets and Foundry were not touched. The only database written to was
`freedom_test`, which is disposable and was left migrated and empty of rows.

---

## 12. Codex Phase 1 review — findings and resolutions

Three blocking findings were raised. All three are resolved; the third is
resolved as an **audit that reports Phase 1 blocked**, which is the outcome the
finding asked for when decisions are missing.

### C-1 — Destructive test-database identity guard · **Resolved**

**The finding.** `tests/conftest.py` compared `TEST_DATABASE_URL` and
`DATABASE_URL` as raw strings. `postgresql:///freedom_test` and
`postgresql+psycopg:///freedom_test` are the same database but different
strings, so the guard passed and the suite then ran `alembic downgrade base`.

**The resolution.** A new module, `adapters/database/safety.py`, replaces string
comparison with two layers, because neither is sufficient alone:

1. **Static** — `resolve_connection_identity()` normalises a URL *and the ambient
   libpq environment* (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGSERVICE`, …) into a
   `ConnectionIdentity`: driver stripped, host/port/socket resolved to their
   defaults, database extracted. `assert_disposable_target()` compares
   identities, not text, and additionally requires the target to be the expected
   disposable database on a local connection.
2. **Runtime** — `verify_connected_target()` asks the *server*
   `current_database()` and whether the connection is local, on the connection
   the destructive command will use, **before** the first `downgrade`. This
   catches what no string parsing can: a remapped `localhost`, a port-forward or
   a pooler.

`run_alembic()` also strips `PGSERVICE`, `PGSERVICEFILE` and `PGOPTIONS` from the
child environment, so the subprocess cannot resolve to a target the parent did
not validate.

A non-disposable target **fails** the run rather than skipping it. A skip would
let a misconfigured suite look green while the guard was the only thing standing
between it and a destroyed database.

**Passwords.** `redact()` strips credentials from every identity rendered into an
error, and two tests assert no refusal message and no identity description can
contain a password.

**Regression tests** — `tests/test_database_safety.py`, 22 test functions
expanding to **46 cases** under parametrisation, all connection-free so they run
in the non-database suite where a broken guard is caught before it can act.
Covering each case the finding named:

| Required case | Tests |
|---|---|
| Identical URLs | `test_identical_urls_are_refused` |
| Equivalent but textually different URLs | `test_equivalent_but_textually_different_urls_are_refused` (parametrised over driver, host, port and socket spellings) |
| Different expected database | `test_a_database_that_is_not_the_disposable_one_is_refused` |
| Allowed local disposable configuration | `test_the_documented_local_disposable_configuration_is_allowed` (7 spellings), `test_a_local_disposable_target_is_allowed_beside_a_different_runtime_database` |
| Remote or otherwise unsafe targets | `test_a_remote_target_is_refused`, `test_a_hostless_url_redirected_by_libpq_is_refused`, `test_a_target_defined_by_a_service_file_is_refused`, `test_a_connection_that_left_this_host_is_refused` |
| No credential disclosure | `test_no_refusal_message_contains_a_password`, `test_the_identity_description_carries_no_credentials`, `test_an_unparsable_url_is_refused_without_echoing_it` |

### C-2 — Backup/restore drill connection guard · **Resolved**

**The finding.** `infra/postgresql/backup-restore-drill.sh` validated only the
database *name*. libpq can point `freedom_test` at another server, and step 4
drops that server's `public` schema.

**The resolution.** Five gates before anything destructive runs:

| Gate | What it does | Exit |
|---|---|---|
| 0a | The requested name is `freedom_dev` or `freedom_test` | 2 |
| 0b | Refuses `PGSERVICE`, `PGSERVICEFILE`, `PGOPTIONS`, `PGDATABASE` — each defines the target outside this script and cannot be verified here | 3 |
| 0c | `PGHOST` must be a loopback name or an absolute socket directory; `PGHOSTADDR` must be a loopback address; `PGPORT` must be numeric | 3 |
| 0d | Exports the validated values and unsets the rest, **pinning one connection** so the dump, inventory, drop and restore cannot resolve differently from one another | — |
| 0e | Asks the server `current_database()` and whether the connection is local, over that pinned connection | 3 |

Every destructive command runs under the connection validated at 0d/0e. On any
refusal nothing is dumped, dropped or restored, and the work directory is not
even created — which the tests assert.

**Credentials.** `PGPASSWORD` is passed through untouched, never printed and never
written to a file. The checksum file records only the dump's hash.

**Not failure-atomic — documented, with the recovery action.** Step 4 drops the
schema that step 5 restores into, so between them the database is empty. This is
now stated in the script header *and* in
`docs/operations/database-development.md`. On failure an `EXIT` trap prints
`RECOVERY REQUIRED` naming the intact dump, its checksum file, and the exact
`sha256sum --check && pg_restore …` command to recover. A separate-database
restore would be atomic in this respect and is **not claimed**, because it has
not been tested.

**Automated refusal tests** — `tests/test_database_backup_restore.py`, 9 refusal
tests added this session (the file previously had only the non-disposable-name
case; the rest had been exercised by hand but never automated):

- `test_the_drill_refuses_non_disposable_databases`
- `test_the_drill_refuses_a_connection_it_cannot_prove_local` — hostile `PGHOST`,
  hostile `PGHOSTADDR`, malformed `PGPORT`
- `test_the_drill_refuses_libpq_configuration_it_cannot_verify` — `PGSERVICE`,
  `PGSERVICEFILE`, `PGOPTIONS`, `PGDATABASE`
- `test_a_refusal_does_not_echo_the_password`

Each asserts the exit code, the refusal message, and that the work directory is
still empty. `run_drill()` clears the inherited libpq variables before applying
the hostile one, so a test asserts on the value it set rather than on whatever
the developer happened to export.

**A real bug this found.** Gate 0e compared its locality flag against `"t"`, but
`boolean::text` in PostgreSQL renders `true`, not psql's `t`. Every Unix-socket
connection — the documented local configuration — was therefore misread as
non-local and **refused**. It failed *closed*, so it was never a safety hole, but
it made the drill unrunnable on a correctly configured host. Fixed at
`infra/postgresql/backup-restore-drill.sh:159`. Confirmed to be a real
regression test: restoring `"t"` fails
`test_backup_and_restore_round_trip_preserves_data`, and restoring `"true"`
passes it.

### C-3 — Phase 1 decision-log gate · **Resolved as: Phase 1 is blocked**

Every plan §17 item was audited against `docs/discovery/open-decisions.md` and
the ADRs. The matrix is **§13**. No ruling was invented, and the plan was not
amended to defer anything.

**Result at the time of that audit: 4 closed, 1 partly closed, 10 unresolved.**
Maintainer rulings on 2026-07-31 supersede that count; the current matrix in §13
records all 15 decisions closed. The §17 gate is satisfied.

---

## 13. Plan §17 decision matrix

Plan §17: *"Maintainers must decide and record"* the following before Phase 1
completion. Audited 2026-07-30 against `docs/discovery/open-decisions.md`, the
seven ADRs, and `docs/rules/field-ownership.md`.

Legend: **Closed** — a recorded maintainer decision exists. **Partial** — some of
the item is ruled and some is not. **Unresolved** — no maintainer decision exists.

| # | §17 decision | State | Recorded decision / where it is open |
|---|---|---|---|
| 1 | Discord guild and Council role IDs, through configuration | **Closed** | [OD-18](../discovery/open-decisions.md): guild `1052698198180892733`; Council role `1052702392728178688` |
| 2 | Which Discord roles grant DM capabilities | **Closed** | [OD-18](../discovery/open-decisions.md): Dungeon Master role `1124406915783475241`; the Sheet flag remains evidence only |
| 3 | Ordinary-user website mutation policy | **Closed** | [OD-31](../discovery/open-decisions.md): read-only initially; website mutations require Guild Council |
| 4 | Character co-ownership / delegation policy | **Closed** | [OD-37](../discovery/open-decisions.md#od-37--character-ownership-and-council-reach--closed-2026-07-30), 2026-07-30: *"A character has exactly one owner… Guild Council members can access and modify all characters. Modifications should be logged."* Implemented in Phase 1 as `uq_character_access_one_active_owner`, Council reach as role-derived rather than an access row, and `audit_events.actor_capability`. See R-1 |
| 5 | Field ownership for currency, inventory, languages, proficiencies | **Closed** | Currency is database-owned after migration; [OD-13](../discovery/open-decisions.md) and the approved field-ownership matrix classify notable inventory, languages, and weapon proficiencies/masteries as Council-approved shared. A Council member imports Foundry differences as proposals; application requires Council approval |
| 6 | Initial source of truth during Sheet migration | **Closed** | Maintainer decision 2026-07-31: Sheets remain authoritative until an explicitly approved per-feature cutover; PostgreSQL imports and reconciles first; no indefinite dual writes |
| 7 | Mission approval rules | **Closed** | [OD-32](../discovery/open-decisions.md): DM prepares/submits; Guild Council approves/applies |
| 8 | May an approver approve their own draft | **Closed** | [OD-32](../discovery/open-decisions.md): yes for Council members, with explicit, searchable audit evidence reviewable by other Council members |
| 9 | Thresholds requiring a second approver, if any | **Closed** | [OD-32](../discovery/open-decisions.md): none in the initial release |
| 10 | Event / announcement channel mappings | **Closed** | [OD-33](../discovery/open-decisions.md): announcements `1054441748874657852`; missions `1052700525444997130`; Scheduled Events are guild-level and have no channel |
| 11 | Production domain and reverse proxy | **Closed** | [OD-19](../discovery/open-decisions.md) and [OD-20](../discovery/open-decisions.md): co-located on this host at `freedom-blades.rpgworld.org` behind Caddy |
| 12 | PostgreSQL deployment / backup method | **Closed**, with a residual | [OD-21](../discovery/open-decisions.md#od-21--postgresql-deployment-and-backup-method--closed-2026-07-30), 2026-07-30: PostgreSQL 16 from the Ubuntu package, host systemd service, loopback-bound, separate migration owner role, restricted application roles. **Residual, explicitly deferred by the decision itself:** backup target, retention and off-host copy *"must be settled before production data is stored"* — not before Phase 1 |
| 13 | Staging strategy | **Closed** | [OD-22](../discovery/open-decisions.md#od-22--staging-on-this-host-or-its-own--closed-2026-07-30), 2026-07-30: staging shares this host, mitigated by separate database and login role, separate service accounts and environment files, distinct loopback ports, a staging-only Discord application/guild, a non-production Foundry world, no shared credentials, and never a production backup |
| 14 | Retention policy for attendance and reports | **Closed** | [OD-23](../discovery/open-decisions.md): raw attendance 90 days after settlement; confirmed roster/reports retained; audit/settlement history retained indefinitely in normal operation; OAuth tokens/sessions only while operationally necessary |
| 15 | Supported Foundry / D&D5e version range | **Closed** | [OD-14](../discovery/open-decisions.md#od-14--supported-foundry-and-dnd5e-version-range--blocking-phase-7--closed), 2026-07-30: pin to exactly the deployed tuple — core `14.365`, `dnd5e` `5.3.3` — held in configuration, fail closed on mismatch, no backwards compatibility owed. Carried forward: updating the pin belongs on the Foundry upgrade checklist |

**Totals after maintainer rulings on 2026-07-31: 15 closed, 0 partial, 0 unresolved.**

### What this means for the gate

Plan §17 is unambiguous that these are required *before Phase 1 completion*.
Every required decision is recorded, so the plan §17 gate is satisfied and
Phase 1 is ready for maintainer signoff.

Two observations for the maintainer, offered as observations and not as a
proposed amendment:

1. **The unresolved items cluster in Phases 3, 6 and 8, not Phase 1.** Items 1,
   2, 3, 10, 11 and 14 are authorization, channel and retention parameters that
   nothing in the Phase 1 schema consumes; items 7–9 are mission-approval rules
   first needed in Phase 6. The Phase 1 engineering work does not depend on any
   of them.
2. **Item 6 is the exception, and item 5 is the one with teeth.** The Sheet
   source of truth (6) governs Phase 2, which is the next milestone; and the
   field-ownership matrix (5) already blocks write-enablement by its own terms.

If the gate should be narrowed to the items Phase 1 and Phase 2 actually depend
on, **that is a change to the plan and needs maintainer approval.** The plan has
not been edited, and this document reports the gate as it is written.

---

## 14. Verification for this re-review

Run 2026-07-30, in `/opt/discord-bots/freedom-bot`, against the disposable
`freedom_test` database only.

| Check | Command | Result |
|---|---|---|
| Non-database suite | `./venv/bin/python -m pytest -q` | **296 passed, 53 skipped** — the database tests skip cleanly with no `TEST_DATABASE_URL` |
| Full suite incl. database | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q` | **349 passed** |
| Backup/restore file alone | `… pytest tests/test_database_backup_restore.py -v` | **10 passed** — 9 refusal paths plus the round trip |
| Shell syntax | `bash -n infra/postgresql/backup-restore-drill.sh` | Clean |
| Migration round trip | `alembic downgrade base` → `upgrade head` → `downgrade base` → `upgrade head` | Each ran `0001` in the stated direction with no error |
| Migration drift | `alembic check` | `No new upgrade operations detected.` |
| Current revision | `alembic current` | `0001 (head)` |
| Whitespace | `git diff --check` | Clean |
| C-2 regression is real | Reverted `"true"` → `"t"`, re-ran the file | **1 failed, 9 passed**; restored, **10 passed** |

The destructive drill was run **only after** the strengthened validation passed,
and only against `freedom_test`, as the finding required.

### Checks not run

- **No formatter, linter or type checker.** None is configured, and the review
  explicitly said not to add one as a drive-by change. Still open as §9 item 5.
- **No separate-database restore.** Not tested, therefore not claimed (C-2).
- **Nothing against `freedom_dev`, staging or production**, and no Discord,
  Sheets or Foundry contact. `.env` was not read.
- **The append-only audit grant is still unrehearsed** — unchanged from the
  original submission, and still reviewer-focus item 2.

### Files changed in this re-review round

| File | Change |
|---|---|
| `adapters/database/safety.py` | New — the C-1 identity and runtime guard |
| `tests/conftest.py` | Uses the guard; strips unsafe libpq variables from the Alembic child |
| `tests/test_database_safety.py` | New — 22 connection-free guard tests (46 parametrised cases) |
| `infra/postgresql/backup-restore-drill.sh` | Gates 0b–0e, pinned connection, recovery trap; the `"true"` locality fix |
| `tests/test_database_backup_restore.py` | 9 refusal tests, sanitised `run_drill()` environment, credential-leak assertions |
| `docs/operations/database-development.md` | The drill is not failure-atomic, and the exact recovery action |
| `docs/review/phase-1-submission.md` | This §12–§14, the §9 item 7 correction, and the status header |

### Confirmation

**Phase 2 has not been started.** No Sheet import, no importer, no reconciliation
code, and no Phase 2 table exists. Nothing is committed or pushed. `.env`,
credentials, production services, Discord, Google Sheets and Foundry were not
touched. The only database written to was `freedom_test`.

Phase 1 is **not** approved, and this document does not claim it is. It is
submitted for a narrow Codex re-review of C-1, C-2 and C-3, with Phase 1 itself
ready for maintainer signoff with every §17 decision closed in §13.

---

## 15. Codex Phase 1 re-review — the multi-host target finding

One blocking finding was raised against the §12 C-1 work. It is resolved.

### C-4 — Alembic's target guard could approve a remote PostgreSQL server · **Resolved**

#### The finding

Two defects, one boundary.

1. **`adapters/database/safety.py` inspected only the first value of a repeated
   `host` query parameter.** For

   ```text
   postgresql+psycopg://app@/freedom_production?host=127.0.0.1&host=db.example.org
   ```

   SQLAlchemy parses `host` as the tuple `('127.0.0.1', 'db.example.org')`.
   `_first()` returned `'127.0.0.1'`, `resolve_connection_identity()` normalised
   that to the local token, and `identity.is_local` was `True` — while psycopg's
   multi-host failover could connect to `db.example.org`.

2. **`migrations/env.py` validated only the URL.** It never called the existing
   `verify_connected_target()` against the live Alembic connection, so a
   DNS-remapped `localhost`, a port-forward, a pooler, or a failover target that
   chose its second host could carry migrations past the intended loopback-only
   boundary regardless of what the URL said.

Reproduced before the fix: the URL above resolved to
`ConnectionIdentity(host='local')` and passed `DatabaseSettings` for
`APP_ENVIRONMENT=production`.

#### Two more instances of the same defect, found while fixing it

Both verified against psycopg 3.3.4 on this host, not reasoned about:

- **`postgresql+psycopg://127.0.0.1/freedom_test?host=/var/run/postgresql`
  connects to the *query parameter's* host, not the URL authority's.** The old
  resolver preferred `parsed.host`, so
  `postgresql+psycopg://127.0.0.1/freedom_test?host=db.example.org` would have
  been classified local while connecting to `db.example.org`. This is the
  reported bypass again, without needing a repeated parameter.
- **`postgresql+psycopg:///freedom_test?dbname=postgres` connects to
  `postgres`.** The old resolver read `parsed.database` first and reported
  `freedom_test`, so the *database* half of the boundary had the same hole as
  the host half. Confirmed by connecting: `current_database()` returned
  `postgres`.
- **`?service=` in the URL query is honoured by libpq** exactly as `PGSERVICE`
  is (confirmed: `definition of service "…" not found`), so it could define the
  target outside this repository. `?hostaddr=` is likewise honoured and is the
  address libpq actually dials.

#### The policy, and why rejection

**Multi-host targets are rejected outright, not validated host by host.**

`docs/operations/database-development.md` documents one loopback-only PostgreSQL
cluster per environment, and no failover requirement is approved anywhere in the
plan, the ADRs or `open-decisions.md`. Validating every host would make the
guard weaker in the sense that matters: it would accept a URL whose meaning is
"connect to one of these", when the whole purpose of the guard is to name *the*
database about to be created, migrated or dropped.

**Multiple *local* hosts are rejected too.** The rule is about how many targets a
URL names, not about which of them happen to be safe. `?host=127.0.0.1&host=localhost`
is refused. If a failover target is ever needed, that is a maintainer decision
and an ADR, not a relaxation of this guard.

#### The safety behaviour now enforced

`resolve_connection_identity()` — the single function every caller
(`DatabaseSettings`, `assert_disposable_target`, `migrations/env.py`,
`tests/conftest.py`) goes through — now refuses:

| Spelling | Example | Refusal |
|---|---|---|
| Repeated query parameter | `?host=a&host=b` | `host` is set 2 times … failover list |
| Comma-separated query value | `?host=a,b` | is the list … failover list |
| Comma-separated URL authority | `//a,b/freedom_dev` | is the list … failover list |
| Comma-separated environment | `PGHOST=a,b`, `PGHOSTADDR=…` | is the list … failover list |
| Repeated/comma `port` | `?port=5432&port=5433`, `PGPORT=5432,5433` | same, for `port` |
| Repeated `dbname` | `?dbname=x&dbname=y` | same, for `database` |
| One component named twice, differing | `//127.0.0.1/db?host=b`, `///x?dbname=y`, `//h:5432/db?port=5433` | names more than one *component* … not decidable |
| Target defined outside the repository | `?service=freedom` | cannot be verified |

`?hostaddr=` is resolved as the host (it is what libpq dials), so a remote
`hostaddr` beside a loopback `host` is refused. A component named twice with the
*same* value is not ambiguous and is allowed.

Everything the guard already refused it still refuses: non-PostgreSQL backends,
the wrong database name for the environment, non-loopback hosts, `PGSERVICE`/
`PGSERVICEFILE`, a URL naming no database, and a test URL equal to the runtime
URL by resolved identity.

**Live verification in online Alembic migrations.** `migrations/env.py` now calls

```python
verify_connected_target(connection, expected_database=settings.identity.database)
```

on the established connection, **before** `context.run_migrations()`, and
therefore before any DDL. It checks *both* halves the finding asked for:

- `current_database()` equals the database `APP_ENVIRONMENT` requires
  (`freedom_dev`/`freedom_test`/`freedom_staging`/`freedom_production`); and
- the connection is genuinely local — `inet_server_addr()` and
  `inet_client_addr()` both null (Unix-domain socket), or both loopback.

Either mismatch raises `UnsafeDatabaseTargetError` and no migration runs.

**A real bug this fix introduced, and caught.** The verification query implicitly
begins a transaction on the connection. Left open, Alembic's own
`begin_transaction()` nested inside it and committed only the inner marker, so
the DDL was discarded when the connection closed — migrations reported success
and changed nothing. Caught by the existing
`test_migrations_apply_to_empty_postgresql_and_downgrade`. Fixed with an explicit
`connection.rollback()` after the check, and now covered directly by
`test_online_migrations_run_against_a_verified_local_target`, which downgrades to
base, asserts the tables are gone, upgrades to head, and asserts they are back.
Confirmed to fail when the `rollback()` is removed.

#### Offline (`--sql`) Alembic — considered explicitly

Offline mode never opens a connection, so it **cannot** perform the live check.
It is not silently trusted and it is not disabled:

- **The static half still applies in full.** `database_settings()` runs before
  anything is emitted, so a multi-host, remote, `?service=`, or wrong-environment
  `DATABASE_URL` produces **no script at all**. Tested.
- **The limitation travels with the script.** A comment block is prepended to the
  generated SQL stating that Alembic did not connect, that nothing in the script
  proves which server it will be applied to, and giving the
  `SELECT current_database(), inet_server_addr(), inet_client_addr();` the
  operator must run instead. Tested, including that the script is still complete
  and still valid SQL.
- **It is proven not to connect**: the test generates a full script with
  `DATABASE_URL` pointing at `127.0.0.1:1`, where nothing listens.
- Documented in `docs/operations/database-development.md`,
  *Offline (`--sql`) migrations cannot be verified*, which states that offline
  mode is for review and change-controlled hand-off, not routine deployment, and
  that the operator carries the target check.

**This remains a real, accepted residual risk**, and it is the one part of the
boundary a machine does not close: an offline script is text, and text can be
applied anywhere by anyone. Rejecting offline mode outright was considered; it is
not done because generating a reviewable script is a legitimate change-control
need and offline mode itself touches nothing. A reviewer who disagrees should say
so — refusing `--sql` is a two-line change in `run_migrations_offline()`.

#### Regression tests

All connection-free tests run in the non-database suite, where a broken guard is
caught before it can act.

| Required case | Test |
|---|---|
| Repeated host, local then remote | `test_a_repeated_host_parameter_is_refused[local then remote]`; the finding's exact URL as `test_the_reported_finding_url_is_refused` and in `test_a_multi_target_migration_url_is_refused` |
| Repeated host, remote then local | `test_a_repeated_host_parameter_is_refused[remote then local]` |
| Multiple local hosts (rejection policy) | `test_a_repeated_host_parameter_is_refused[two local hosts]`, `…[socket then remote]`, `…[three hosts]`, `test_a_comma_separated_host_list_is_refused[…127.0.0.1,localhost]` |
| Comma-separated / psycopg multi-host forms | `test_a_comma_separated_host_list_is_refused` (6 spellings: query, URL authority, `hostaddr`), `test_a_multi_host_libpq_environment_is_refused` (`PGHOST`, `PGHOSTADDR`) |
| Multi-valued port and database | `test_a_repeated_port_or_database_is_refused` (4 cases) |
| One component named twice | `test_a_url_that_names_one_component_twice_is_refused` (7 cases), `test_a_single_host_repeated_with_the_same_value_is_not_ambiguous` |
| Alembic refuses a live connection on the wrong database | `test_online_migrations_refuse_a_connection_that_landed_in_another_database` — drives `command.downgrade(…, "base")` through the real `env.py` and asserts every table survives |
| Alembic refuses a non-loopback live connection | `test_online_migrations_refuse_a_connection_that_is_not_local` — same, and asserts every table survives |
| Valid local Unix-socket connection | `test_a_unix_socket_connection_to_the_expected_database_is_accepted`, `test_the_documented_local_disposable_configuration_is_allowed` (7 URL spellings), `test_the_live_check_accepts_this_hosts_real_connection` (real server) |
| Valid loopback connection | `test_a_loopback_connection_to_the_expected_database_is_accepted` (IPv4 and IPv6), `test_a_local_hostaddr_is_allowed`, `test_a_single_host_and_port_parameter_pair_is_still_allowed` |
| Passwords never in errors or output | `test_no_refusal_message_contains_a_password` (8 URLs, now including every multi-target refusal path), `test_a_refused_migration_url_does_not_echo_the_password`, `test_a_refused_migration_does_not_echo_the_password` (asserts stdout and stderr too), `test_the_identity_description_carries_no_credentials`, `test_an_unparsable_url_is_refused_without_echoing_it` |
| Offline mode | `test_offline_migrations_never_connect_and_say_so`, `test_offline_migrations_refuse_a_target_they_cannot_verify` (6 cases) |

**The tests were confirmed to be real regressions.** With the multi-value and
ambiguity checks disabled in `safety.py` (temporary edit, reverted): **42 failed,
67 passed**. With them restored: **113 passed**. With `connection.rollback()`
removed from `env.py`: `test_online_migrations_run_against_a_verified_local_target`
**fails**; restored, **13 passed**.

### Files changed in this round

| File | Change |
|---|---|
| `adapters/database/safety.py` | `_first()` replaced by `_sole_value()`, `_reject_value_list()` and `_one_target_component()`; `?service=` refused; `?hostaddr=` resolved as the host; `verify_connected_target()` messages generalised (it now guards migrations too, not only drops) |
| `migrations/env.py` | `database_url()` → `database_settings()`; live `verify_connected_target()` before `run_migrations()` online, with the transaction fix; offline warning banner and its rationale |
| `tests/test_database_safety.py` | +12 test functions (33 further parametrised cases) for multi-host, multi-valued and ambiguous targets, `hostaddr`, `?service=`, and 5 more password cases |
| `tests/test_database_config.py` | +3 test functions (9 cases) covering the same on the Alembic path through `DatabaseSettings` |
| `tests/test_migration_safety.py` | **New** — 13 tests driving the real `env.py` through Alembic's command API: 4 online (2 refusals asserting the schema survives, 1 commit/positive control, 1 real-server locality check), 9 offline |
| `docs/operations/database-development.md` | *One target, or none*, *The URL is checked, and then the connection is checked*, *Offline (`--sql`) migrations cannot be verified* |
| `docs/review/phase-1-submission.md` | This §15 and the status header |

### Verification for this round

Run 2026-07-30 in `/opt/discord-bots/freedom-bot` with the repository's own
`./venv` (Python 3.12.3, SQLAlchemy 2.0.51, Alembic 1.18.5, psycopg 3.3.4),
against the disposable local `freedom_test` (PostgreSQL 16.14) and nothing else.

| # | Command | Result |
|---|---|---|
| 1 | `pytest tests/test_database_safety.py tests/test_database_config.py tests/test_migration_safety.py -q` | **109 passed, 4 skipped** (the 4 online-Alembic tests skip without `TEST_DATABASE_URL`) |
| 2 | `pytest -q` (no `TEST_DATABASE_URL`) — complete non-database suite | **346 passed, 57 skipped**, 1 pre-existing `audioop` warning from Pycord |
| 3 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test pytest -q` — complete suite | **403 passed**, same 1 warning |
| 4 | `TEST_DATABASE_URL=… pytest -m database -q` | **66 passed**, 337 deselected |
| 5 | `APP_ENVIRONMENT=test DATABASE_URL=… alembic check` | `No new upgrade operations detected.` |
| 6 | `… alembic downgrade base` → `alembic upgrade head` | `Running downgrade 0001 -> `, then `Running upgrade  -> 0001` |
| 7 | `… alembic current` / `alembic heads` | `0001 (head)`, single head |
| 8 | `… alembic upgrade head --sql` | Complete script, warning banner first, valid SQL comments |
| 9 | `python -m compileall -q adapters application domain migrations tests infra models helpers connectors config.py main.py` | exit 0 |
| 10 | `grep -rlP '[ \t]+$'` over the changed files | no matches |
| 11 | `grep -rniE "password=\|secret\|BEGIN PRIVATE KEY"` over the changed files | only `hide_password=True` in `redact()` and the synthetic `app:secret@db.example.org` fixture URL |

Refusals reproduced by hand, with a password in the URL, and neither echoed it:

| Command | Outcome |
|---|---|
| `APP_ENVIRONMENT=production DATABASE_URL='…app:hunter2@/freedom_production?host=127.0.0.1&host=db.example.org' alembic upgrade head` | `UnsafeDatabaseTargetError: DATABASE_URL's host= parameter is set 2 times ('127.0.0.1', 'db.example.org')…` — the finding, refused |
| The same URL as `TEST_DATABASE_URL`, `pytest tests/test_database_repositories.py` | `Failed: Refusing to run destructive database tests: TEST_DATABASE_URL's host= parameter is set 2 times…` |
| `DATABASE_URL='…?host=127.0.0.1&host=db.example.org' alembic upgrade head --sql` | Refused; no script emitted |

### Checks not run in this round

| Check | Why not |
|---|---|
| Formatter, linter, type checker | Still none configured or installed; unchanged from §6 and §14. Open as §9 item 5 |
| A live wrong-database or remote connection | Deliberately impossible here, and it would mean connecting somewhere unsafe to prove a guard against connecting somewhere unsafe. The online tests substitute the query the live check sends, so the real `env.py` receives a wrong-database and a non-loopback answer from a real connection and refuses both. What is *not* proven end-to-end is PostgreSQL's own `inet_server_addr()` behaviour on a genuinely remote server |
| `backup-restore-drill.sh` by hand | Unchanged this round; its 10 tests pass inside run 3. Its own gates already reject a comma-separated `PGHOST`/`PGHOSTADDR` (neither matches `/*` nor a loopback literal) and a non-numeric `PGPORT`, so the multi-host form fails closed there too — verified by reading the gates, not by a new test |
| Anything against `freedom_dev`, staging, production, Discord, Sheets or Foundry | Forbidden. The only database connected to this round was `freedom_test`. `.env` was not read |

### Remaining Phase 1 blockers

1. **The plan §17 decision log — all 15 closed.** See the current §13; the gate
   is satisfied by the maintainer rulings recorded on 2026-07-31.
2. **The append-only audit grant is still unrehearsed** (§6, §8 step 5, reviewer
   focus 2). No role on this host can create the restricted role, so the template
   is verified and its effect is not.
3. **Offline `--sql` migrations cannot verify their target** (above). Mitigated by
   static validation, an in-script warning and documentation; not eliminated.
4. **No formatter, linter or type checker is configured** (§9 item 5).

Nothing is committed or pushed. **Phase 2 has not been started** — no importer,
no reconciliation code, no Phase 2 table. Phase 1 remains **not approved**.

---

## 16. Codex Phase 1 second re-review — the loopback-target finding

One blocking finding was raised against the §12 and §15 work. It is resolved.

### C-5 — A loopback target could be a remote server, and the guard said local · **Resolved**

#### The finding

`adapters/database/safety.py::verify_connected_target()` treated a connection as
local when `current_database()` was the expected name **and**
`inet_server_addr()`/`inet_client_addr()` were both loopback, or both null. The
first of those two answers proves nothing:

```bash
ssh -L 5432:localhost:5432 elsewhere        # then connect to 127.0.0.1:5432 here
```

The session terminates at PostgreSQL on `elsewhere`, arriving from sshd over
*that* host's loopback interface. The server therefore reports loopback for both
addresses, and `current_database()` answers with whatever database name the URL
asked for. A connection pooler or any other TCP proxy has the same shape. The
guard would have accepted it — and then run `alembic upgrade`, `alembic downgrade
base`, or the drill's `DROP SCHEMA public CASCADE` against a database on another
machine.

**The comments and documentation claiming the live address check catches SSH port
forwarding were false.** They were introduced in the §15 round (and echoed in
§12) and appeared in `safety.py`, `migrations/env.py`, `tests/conftest.py`,
`backup-restore-drill.sh`, `docs/operations/database-development.md` and this
document. Every one of them is corrected; none of the prior review history is
deleted.

#### The correction: the documented topology closes the boundary

`docs/operations/database-development.md` describes one loopback-only PostgreSQL
cluster per environment on this host, reached through the local Unix-domain
socket. That is what makes a real boundary available: **a Unix socket is a file
on this machine.** A TCP tunnel cannot present one, and a server reached through
one reports null addresses at both ends. So the three destructive or
schema-changing workflows now require it, statically *and* live:

| Workflow | Static | Live, on the same connection |
|---|---|---|
| Online Alembic migrations (`migrations/env.py`) | `DatabaseSettings.from_mapping(..., policy=UNIX_SOCKET_ONLY)` | `verify_connected_unix_socket_target()` before `run_migrations()` |
| Destructive test fixtures (`tests/conftest.py`) | `assert_disposable_target(..., policy=UNIX_SOCKET_ONLY)` | same, before the first `alembic downgrade base` |
| Backup/restore drill | gates 0b–0d: no `PGHOSTADDR`, `PGHOST` only an absolute socket directory or unset | gate 0e: `inet_server_addr()` and `inet_client_addr()` must both be null |

`postgresql+psycopg://user@127.0.0.1/freedom_test` is refused by all three, as
are `localhost`, `::1`, `?host=127.0.0.1`, `?hostaddr=127.0.0.1`, and a loopback
`PGHOST`/`PGHOSTADDR` supplied to an otherwise hostless URL.

**The API says what it proves.** `ConnectionPolicy` is an explicit parameter with
two values, so no function is left promising proof it cannot provide:

- `UNIX_SOCKET_ONLY` — the connection is a socket file on this host. **The
  default**, so a caller has to ask for anything weaker by name.
- `SOCKET_OR_LOOPBACK` — the target is not a named remote host, and *nothing
  more*. It is correct for an ordinary future runtime connection, which creates
  and drops nothing; it is never what a destructive caller asks for.

The live check was renamed from `verify_connected_target` to
`verify_connected_unix_socket_target` for the same reason: it no longer accepts a
loopback answer, and the name now states the one thing it verifies. No
loopback-accepting live variant was kept, because after this change nothing
consumes one (`.agents/AGENTS.md`: no abstractions without a real consumer).

**Everything the guards already refused, they still refuse.** Expected
environment and database names; remote, ambiguous, multi-host, repeated and
`?service=`/`PGSERVICE` targets; resolution of `PGHOST`, `PGHOSTADDR`, `PGPORT`
and `PGDATABASE` into the identity; the test-versus-runtime identity comparison;
credential-safe errors; and the live `current_database()` check on the connection
that does the work. Socket and loopback still collapse to one `ConnectionIdentity`
for *equality*, so a destructive URL cannot hide from the runtime comparison by
choosing the other spelling — `locality` is carried alongside and excluded from
comparison (`field(compare=False)`).

**Alembic still owns its transaction.** The verification query implicitly opens
one on the migration's connection, so `env.py` still ends it with
`connection.rollback()` before `context.begin_transaction()`. Verified by hand
this round: empty → head → `alembic check` → base → head, with the tables
actually present after each upgrade (§16 verification, rows 5–7).

#### What this does **not** prove — stated, not hidden

Requiring a socket closes the port-forward and TCP-proxy paths. It is not an
absolute proof of locality: a deliberately forwarded *socket*
(`ssh -L /tmp/s:/remote/s`) would still answer with null addresses. That is a
hand-built hostile configuration on the operator's own host rather than the
ordinary `ssh -L 5432:…` accident these guards exist to refuse, and no in-process
check can exclude it. It is written into `safety.py`, the drill header and the
operations document rather than left for the next reviewer to find.

Ordinary runtime database connections are outside this correction. None exists
yet; when one does, it may use `SOCKET_OR_LOOPBACK` unless it invokes the
destructive-target guard.

#### Regression tests

All are new or rewritten this round. Every one was confirmed to **fail** before
the correction: with the pre-correction behaviour restored by temporary edit
(weak policy default, loopback accepted live, drill gates accepting loopback),
the four files reported **47 failed, 114 passed**; restored, **161 passed**.

| # | Required case | Test |
|---|---|---|
| 1 | Alembic refuses a statically loopback TCP URL | `test_alembic_refuses_a_tcp_loopback_url` (3 cases: `upgrade`, `downgrade`, `--sql`) driving the real `env.py`; `test_a_tcp_loopback_migration_target_is_refused` (8 cases) on the `DatabaseSettings` path; `test_alembic_refuses_a_loopback_host_inherited_from_libpq` |
| 2 | Destructive pytest setup refuses the same TCP form | `test_a_tcp_loopback_target_is_refused_for_destructive_operations` (6 spellings, including `postgresql+psycopg://user@127.0.0.1/freedom_test`), `test_a_loopback_target_inherited_from_libpq_is_refused` |
| 3 | Expected database + loopback addresses is refused, not accepted | `test_a_loopback_connection_to_the_expected_database_is_refused` (IPv4, IPv6); `test_online_migrations_refuse_a_live_loopback_connection`, which drives `command.downgrade(…, "base")` through the real `env.py` and asserts every table survives |
| 4 | A Unix-socket connection to the expected database is accepted | `test_a_unix_socket_connection_to_the_expected_database_is_accepted`; `test_the_live_check_accepts_this_hosts_real_connection` (real server, asserts both addresses null) |
| 5 | The wrong database is still refused | `test_a_connection_that_landed_in_another_database_is_refused`, `test_the_database_is_checked_even_on_a_unix_socket_connection`, `test_online_migrations_refuse_a_connection_that_landed_in_another_database` |
| 6 | Multi-host, ambiguous, libpq-environment and password tests still pass | The whole §15 set is unchanged and green: `test_a_repeated_host_parameter_is_refused`, `test_a_comma_separated_host_list_is_refused`, `test_a_multi_host_libpq_environment_is_refused`, `test_a_url_that_names_one_component_twice_is_refused`, `test_a_hostless_url_redirected_by_libpq_is_refused`, `test_no_refusal_message_contains_a_password`, … |
| 7 | The drill refuses `PGHOST=127.0.0.1`, `localhost`, `::1` | `test_the_drill_refuses_a_loopback_tcp_target` (5 cases, including loopback `PGHOSTADDR`), each asserting exit `3` and that the work directory was never created |
| 8 | The drill accepts its documented Unix-socket configuration | `test_the_drill_accepts_an_explicit_unix_socket_directory` (explicit `PGHOST=/var/run/postgresql`), `test_backup_and_restore_round_trip_preserves_data` (hostless default), both asserting a verified restore |
| 9 | Refusal messages never expose passwords | `test_a_refusal_does_not_echo_the_password` (3 environments, drill stdout and stderr), `test_no_refusal_message_contains_a_password`, `test_a_refused_migration_url_does_not_echo_the_password`, `test_a_refused_migration_does_not_echo_the_password` |
| 10 | Migrations apply, downgrade and commit through the socket | `test_online_migrations_run_against_a_verified_local_target` (base → head, asserting the tables really appear, which is what catches the transaction-nesting failure mode), plus the by-hand round trip below |

Two further tests pin the boundary from the other side, so the strict policy
cannot be quietly widened: `test_the_weaker_policy_still_accepts_loopback_and_says_no_more_than_that`
and `test_the_strict_socket_policy_is_the_default`.

### Files changed in this round

| File | Change |
|---|---|
| `adapters/database/safety.py` | `TargetLocality` and `ConnectionPolicy`; `ConnectionIdentity.locality` (excluded from equality) and `is_unix_socket`; `require_target_policy()`; `assert_disposable_target(policy=…)`; `verify_connected_target` → `verify_connected_unix_socket_target`, which now refuses a loopback answer; module docstring corrected, with the residual stated |
| `adapters/database/config.py` | `DatabaseSettings.from_mapping(policy=…)`, defaulting to `UNIX_SOCKET_ONLY` |
| `migrations/env.py` | Passes `UNIX_SOCKET_ONLY`; calls the renamed live check; corrected comments; offline warning now states that both addresses must be NULL and that loopback is not sufficient |
| `tests/conftest.py` | Passes `UNIX_SOCKET_ONLY`; uses the renamed live check; module docstring corrected with the port-forward explanation |
| `infra/postgresql/backup-restore-drill.sh` | Gate 0c requires the socket (`PGHOSTADDR` refused outright, `PGHOST` only an absolute directory); gate 0d unsets `PGHOSTADDR` when pinning; gate 0e requires both addresses null; header corrected |
| `tests/test_database_safety.py` | Socket-only accepted set, new TCP-loopback refusal set, weak-policy boundary, live-check loopback refusal, identity-equality test |
| `tests/test_database_config.py` | TCP-loopback refusal on the Alembic path, default-policy test, weak-policy tests |
| `tests/test_migration_safety.py` | `test_alembic_refuses_a_tcp_loopback_url`, inherited-`PGHOST` refusal, live loopback refusal, offline banner assertions |
| `tests/test_database_backup_restore.py` | Loopback refusal set, explicit-socket acceptance, password cases extended |
| `docs/operations/database-development.md` | *Destructive and schema-changing work uses the Unix-domain socket*; corrected *The URL is checked, and then the connection is checked*, the offline section, the drill section, and the example URLs |
| `.env.example` | `DATABASE_URL`/`TEST_DATABASE_URL` placeholders are the socket form, with the reason |
| `docs/review/phase-1-submission.md` | This §16 and the status header |

### Verification for this round

Run 2026-07-30/31 in `/opt/discord-bots/freedom-bot` with the repository's own
`./venv` (Python 3.12.3, SQLAlchemy 2.0.51, Alembic 1.18.5, psycopg 3.3.4),
against the disposable local `freedom_test` (PostgreSQL 16) over the Unix-domain
socket and nothing else.

| # | Command | Result |
|---|---|---|
| 1 | `pytest tests/test_database_safety.py tests/test_database_config.py tests/test_migration_safety.py tests/test_database_backup_restore.py -q` (with `TEST_DATABASE_URL`) | **161 passed** |
| 2 | `pytest -q` (no `TEST_DATABASE_URL`) — complete non-database suite | **382 passed, 59 skipped**, 1 pre-existing `audioop` warning from Pycord |
| 3 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test pytest -q` — complete suite | **441 passed**, same 1 warning |
| 4 | `TEST_DATABASE_URL=… pytest -m database -q` | **75 passed**, 366 deselected |
| 5 | `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` → 0 tables → `alembic upgrade head` | `Running upgrade  -> 0001`; **10 tables present**, so the DDL committed |
| 6 | `alembic check` | `No new upgrade operations detected.` |
| 7 | `alembic downgrade base` → `upgrade head` → `current` / `heads` | only `alembic_version` left, then 10 tables again; `0001 (head)`, single head |
| 8 | `bash -n infra/postgresql/backup-restore-drill.sh` | Clean |
| 9 | Drill by hand, `PGHOST=127.0.0.1`, `PGHOST=localhost`, `PGHOST=::1`, `PGHOSTADDR=127.0.0.1` | Exit `3` each, `Nothing was dumped, dropped or restored.`, and the work directory does not exist afterwards |
| 10 | Drill by hand, hostless default and `PGHOST=/var/run/postgresql` | `0. Target verified: database 'freedom_test', Unix-domain socket` → `Restore verified for freedom_test` |
| 11 | `pytest tests/test_database_repositories.py` with `TEST_DATABASE_URL=postgresql+psycopg://user:hunter2@127.0.0.1/freedom_test` | `Failed: Refusing to run destructive database tests: … must connect through the PostgreSQL Unix-domain socket …`; `hunter2` appears **0 times** in the output |
| 12 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg://user:hunter2@127.0.0.1/freedom_test' alembic upgrade head` | `UnsafeDatabaseTargetError: … must connect through the PostgreSQL Unix-domain socket …`; no connection attempted, no password echoed |
| 13 | The same with `DATABASE_URL='postgresql+psycopg:///freedom_test'` and `PGHOST=127.0.0.1` | Refused identically — the socket URL is only a socket while the environment leaves it alone |
| 14 | `python -m compileall -q adapters application domain migrations tests infra models helpers connectors config.py main.py` | exit 0 |
| 15 | `git diff --check` | exit 0; `grep -rlP '[ \t]+$'` over the changed files: no matches |
| 16 | Pre-correction behaviour restored by temporary edit, four files re-run | **47 failed, 114 passed**; edits reverted, **161 passed** |

`freedom_test` was left migrated to `0001` and holding zero rows.

### Checks not run in this round

| Check | Why not |
|---|---|
| Formatter, linter, type checker | Still none configured or installed; unchanged from §6, §14 and §15. Open as §9 item 5 |
| A genuinely tunnelled or remote connection | Not attempted: proving a guard against connecting somewhere unsafe by connecting somewhere unsafe is not available here, and there is nowhere authorised to connect to. The live layer is exercised by substituting the query so the real `env.py` receives a loopback and a remote answer from a real connection and refuses both; the static layer is exercised directly. What is **not** proven end-to-end is PostgreSQL's own `inet_*` behaviour through an actual SSH forward |
| Restore into a separate empty database | Still no `CREATEDB` on this host; unchanged from §6, and still not claimed |
| Live rehearsal of the append-only runtime grant | Unchanged from §6 and §14 — still the largest gap in the append-only claim, still a deployment-time step (§8 step 5) |
| Anything against `freedom_dev`, staging, production, Discord, Sheets or Foundry | Forbidden. The only database connected to this round was `freedom_test`, over the Unix-domain socket. `.env` was not read |

### Operational consequence for the maintainer

**`DATABASE_URL` and `TEST_DATABASE_URL` must now name the Unix-domain socket for
migrations and for the database tests.** Change
`postgresql+psycopg://role@127.0.0.1:5432/freedom_x` to
`postgresql+psycopg://role@/freedom_x` (or add `?host=/var/run/postgresql`).
`.env.example` and the operations document carry the new form. A loopback URL now
fails closed with an explicit message rather than running. Nothing else about
deployment changes, and the running bot is unaffected — it reads neither
variable.

### Remaining Phase 1 blockers

Unchanged by this round:

1. **The plan §17 decision log — all 15 closed.** See the current §13; the gate
   is satisfied by the maintainer rulings recorded on 2026-07-31.
2. **The append-only audit grant is still unrehearsed** (§6, §8 step 5).
3. **Offline `--sql` migrations cannot verify their target** (§15). The in-script
   warning now also tells the operator that loopback addresses are not a
   sufficient answer.
4. **No formatter, linter or type checker is configured** (§9 item 5).

Nothing is committed or pushed. **Phase 2 has not been started** — no importer,
no reconciliation code, no Phase 2 table. Phase 1 remains **not approved**.

---

## 17. Codex Phase 1 third re-review — the inherited `PGHOSTADDR` finding

> **Not to be confused with plan §17**, the decision log audited in §13 of this
> document. As elsewhere here, a bare `§N` means a section of *this* document and
> `plan §N` means `docs/implementation-plan.md`.

One blocking finding was raised against the §15 and §16 work. It is resolved.

Date: 2026-07-31. Nothing is committed or pushed. Phase 2 has not been started.

### C-6 — A socket URL with an inherited `PGHOSTADDR` is a TCP connection · **Resolved**

#### The finding

`resolve_connection_identity()` in `adapters/database/safety.py` consulted the
ambient `PGHOSTADDR` **only when the URL supplied no host of any kind**. libpq
does not work that way: `host` and `hostaddr` are two separate connection
parameters, each with its own environment default, and `hostaddr` is the address
the connection is *made to* — when it is set, `host` is kept only as a name for
authentication. So

```bash
PGHOSTADDR=127.0.0.1
DATABASE_URL='postgresql+psycopg:///freedom_test?host=/var/run/postgresql'
```

passed static validation as a Unix-domain socket while psycopg dialled TCP. Codex
reproduced it: `DatabaseSettings` described a local socket and Alembic attempted
a TCP connection.

The online live check does not close this. It runs on an *established*
connection, and establishing the connection is what offers the credentials. An
inherited **remote** `PGHOSTADDR` would therefore have handed the migration
role's password to an unauthorised server before anything on this host could
object. Static validation has to refuse before an engine exists.

#### Reproduced here first, on both halves

| Check | Result before the correction |
|---|---|
| `resolve_connection_identity(url, environ={'PGHOSTADDR': '127.0.0.1'})` | `locality=UNIX_SOCKET`, `is_unix_socket=True` |
| Same with `PGHOSTADDR=203.0.113.9` | `locality=UNIX_SOCKET` — a **remote** address classified as the local socket |
| `assert_disposable_target(...)` | **Accepted** |
| `DatabaseSettings.from_mapping(..., environment='test')` | **Accepted** |
| `psycopg.connect(host='/var/run/postgresql', dbname='freedom_test')` with `PGHOSTADDR=127.0.0.1` | `connection to server at "127.0.0.1", port 5432 failed` — libpq really does dial TCP, confirmed rather than assumed |

#### Root cause

One line of modelling: the resolver folded `hostaddr`, the `host=` parameter and
the URL authority into a **single** "host" component through
`_one_target_component`, then fell back to `PGHOSTADDR or PGHOST` only if that
component was empty. Two consequences followed from the same mistake:

1. an explicit `host` in the URL suppressed `PGHOSTADDR` entirely, when libpq
   would have applied it; and
2. because a loopback address and a socket directory both normalise to the
   `local` host token, the substitution was invisible to identity comparison —
   only `locality` differed, and `locality` was taken from the wrong component.

#### The correction

`host` and `hostaddr` are now resolved **independently**, each from the URL
first and then from its own environment default, and combined afterwards by
`_dialled_target()`:

| `hostaddr` | `host` | Resolved target |
|---|---|---|
| unset | unset | the default Unix-domain socket |
| unset | absolute directory | that socket directory |
| unset | name or address | TCP to that host |
| set | **absolute socket directory** | **refused** |
| set | anything else, or unset | TCP to `hostaddr`; `host` is authentication only |

Two deliberate choices in that table:

- **Socket directory plus any host address is refused at resolution**, under
  *every* policy, rather than reclassified as TCP. Precedence alone would let a
  loopback `hostaddr` satisfy `SOCKET_OR_LOOPBACK` while the operator's URL says
  socket. A configuration whose two halves name different transports names no
  single provable target, so it fails closed for every caller. This is what
  makes "reject a socket URL combined with inherited `PGHOSTADDR`, whether
  loopback or remote" unconditional rather than policy-dependent.
- **An address is always TCP.** A `hostaddr` is classified by
  `_address_locality`, which never returns `UNIX_SOCKET`, and normalised by
  `_normalise_address`, which — unlike `_normalise_host` — does not treat a
  leading `/` as the local socket. A `hostaddr` shaped like a path is a
  misconfiguration libpq rejects; it must not borrow the local token on its way
  there.

**Behaviour deliberately changed, and reported rather than buried.** Two cases
that were previously refused as *ambiguous* are now refused as *remote*:
`//127.0.0.1/freedom_test?hostaddr=203.0.113.9` and
`?hostaddr=10.0.0.5&host=localhost`. Both still fail closed; what changed is the
reason, and the reason is now the true one — libpq dials the address, so the
address is what the policy is applied to. The two parametrised cases moved out
of `test_a_url_that_names_one_component_twice_is_refused` and into
`test_a_host_address_outranks_a_named_host`. No case that was refused before is
accepted now.

**Everything else is preserved.** Repeated and comma-separated `host`,
`hostaddr`, `port` and `dbname`; multi-host URL authorities; `PGHOST`/
`PGHOSTADDR` lists in the environment; one component named twice with different
values; `PGSERVICE`/`PGSERVICEFILE`/`?service=`; the `UNIX_SOCKET_ONLY` default;
the test-versus-runtime identity comparison; the live
`verify_connected_unix_socket_target` check; and the socket/loopback identity
collapse that stops a destructive URL hiding from that comparison. The full
§12–§16 test set is unchanged and green apart from the two relocated cases.

#### Where the refusal happens, per workflow

| Workflow | Refuses before | Evidence |
|---|---|---|
| Online Alembic | `engine_from_config` is called | `test_online_alembic_refuses_an_inherited_host_address_before_connecting` substitutes `sqlalchemy.engine_from_config` with a function that fails the test if reached — 12 cases |
| Offline Alembic (`--sql`) | anything is printed | `test_offline_alembic_emits_no_script_for_an_inherited_host_address` — no DDL, no `alembic_version`, **not even the warning banner** — 4 cases |
| Destructive pytest fixtures | any fixture runs | `test_the_destructive_pytest_guard_refuses_an_inherited_host_address` calls the real `tests/conftest.py::resolve_test_database_url` — 4 cases |
| `DatabaseSettings` | it returns | `test_a_socket_migration_url_with_an_inherited_host_address_is_refused` — 16 cases across all four environments |
| Backup/restore drill | the work directory is created | `test_the_drill_refuses_a_host_address_beside_a_socket_directory` — 12 cases |

#### The backup/restore drill: verified, not assumed

The finding asked for confirmation rather than an assumption. Gate 0c refuses
`PGHOSTADDR` outright at `infra/postgresql/backup-restore-drill.sh:118`, and it
does so **before** the `PGHOST` check at line 125, so naming the socket
directory in `PGHOST` cannot rescue an inherited address. That ordering is now
under test (12 cases: four addresses × no `PGHOST` / `/var/run/postgresql` /
`/run/postgresql`), each asserting exit `3`, that the refusal names
`PGHOSTADDR`, and that the work directory was never created. Confirmed by hand
as well (verification rows 9–10 below). **The drill needed no change.**

#### Files changed in this round

| File | Change |
|---|---|
| `adapters/database/safety.py` | `host` and `hostaddr` resolved as separate components; `_dialled_target()`, `_normalise_address()`, `_address_locality()` added; `hostaddr` removed from `_one_target_component`'s candidates; module docstring records the defect and the libpq precedence |
| `adapters/database/config.py` | `from_mapping` docstring states that `PGHOSTADDR` applies even to a URL that names a host |
| `tests/conftest.py` | Module docstring: the socket URL is a socket only while `PGHOSTADDR` is unset, and why the live check cannot substitute for the static one |
| `tests/test_database_safety.py` | +8 test functions (56 further cases) for the precedence model, the socket/address contradiction under both policies, socket-like URL authorities, a path-shaped `hostaddr`, the conftest guard, and a password case; 2 cases relocated |
| `tests/test_database_config.py` | +4 test functions (20 cases) on the Alembic `DatabaseSettings` path |
| `tests/test_migration_safety.py` | +3 test functions (17 cases): online with engine creation forbidden, offline with no emission, and a password case |
| `tests/test_database_backup_restore.py` | +1 test function (12 cases) pinning gate 0c's ordering |
| `docs/operations/database-development.md` | New *`PGHOSTADDR` overrides the socket URL — operators must unset it* section with the precedence table and the operator instruction; corrected the `?hostaddr=` paragraph; added why the live check cannot replace the static one; the empty-database and drill sections now name the variable |
| `.env.example` | "Keep `PGHOSTADDR` unset", with the reason |
| `docs/review/phase-1-submission.md` | This §17 and the status header |

`infra/postgresql/backup-restore-drill.sh`, `migrations/env.py`, the migration
`0001`, the schema and every bot file are **unchanged** this round.

#### Regression tests added

All are connection-free except the drill set, so they run in the non-database
suite where a broken guard is caught before it can act.

| # | Required case | Test |
|---|---|---|
| 1 | Explicit `?host=/var/run/postgresql` + loopback `PGHOSTADDR` | `test_a_socket_target_combined_with_an_inherited_host_address_is_refused` (`127.0.0.1`, `::1`) |
| 2 | The same + remote `PGHOSTADDR` | the same test (`203.0.113.9`, `10.0.0.5`), and `test_the_socket_and_address_refusal_carries_no_credentials` |
| 3 | Socket-host URL-authority form + inherited `PGHOSTADDR` | `test_a_socket_like_url_authority_with_an_inherited_address_is_refused` (percent-encoded authority, with and without `PGHOSTADDR`); the hostless authority and `PGHOST=/var/run/postgresql` are covered by case 1's third URL and its `socket-pghost-plus-loopback` environment |
| 4 | `DatabaseSettings` | `test_a_socket_migration_url_with_an_inherited_host_address_is_refused` (4 environments × 4 addresses), `test_a_hostless_migration_url_with_an_inherited_host_address_is_refused`, `test_the_socket_and_address_contradiction_is_refused_under_every_policy` |
| 5 | `assert_disposable_target` | cases 1–2 run through it; `test_the_socket_and_address_contradiction_is_refused_under_every_policy`; `test_a_socket_host_beside_a_url_host_address_is_refused` |
| 6 | Online Alembic, no engine or connection attempt | `test_online_alembic_refuses_an_inherited_host_address_before_connecting` — `sqlalchemy.engine_from_config` replaced by a function that fails the test if called |
| 7 | Offline Alembic, no SQL emitted | `test_offline_alembic_emits_no_script_for_an_inherited_host_address` |
| 8 | Password-bearing variants, password absent from all output | `test_the_socket_and_address_refusal_carries_no_credentials`, `test_a_refused_socket_and_address_url_does_not_echo_the_password`, `test_a_refused_host_address_migration_does_not_echo_the_password` (message, stdout **and** stderr) |
| 9 | The precedence model itself | `test_a_host_address_outranks_a_named_host` (4 cases), `test_a_url_host_address_overrides_the_inherited_one`, `test_a_host_address_that_is_not_an_address_does_not_borrow_the_local_token` |
| 10 | The destructive pytest path | `test_the_destructive_pytest_guard_refuses_an_inherited_host_address` |
| 11 | The drill | `test_the_drill_refuses_a_host_address_beside_a_socket_directory` |

**Confirmed to be real regressions.** With the pre-correction resolution restored
by temporary edit (the single folded host component plus the
`PGHOSTADDR or PGHOST` fallback), the four files reported **48 failed, 196
passed**; restored, **244 passed**. The `engine_from_config` substitution was
separately proven to bite: with a valid socket URL it raises
`AssertionError: engine created`, so test 6 above is a real proof of "no engine",
not a vacuous one.

### Verification for this round

Run 2026-07-31 in `/opt/discord-bots/freedom-bot` with the repository's own
`./venv` (Python 3.12.3, SQLAlchemy 2.0.51, Alembic 1.18.5, psycopg 3.3.4),
against the disposable local `freedom_test` (PostgreSQL 16) over the Unix-domain
socket and nothing else.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test pytest tests/test_database_safety.py tests/test_database_config.py tests/test_migration_safety.py` | **214 passed** |
| 2 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test pytest -q` — complete suite | **524 passed**, 1 pre-existing `audioop` warning from Pycord |
| 3 | `pytest -q` (no `TEST_DATABASE_URL`) — complete non-database suite | **465 passed, 59 skipped**, same 1 warning |
| 4 | `python -m compileall -q adapters application domain migrations tests models helpers connectors config.py main.py` | exit 0 |
| 5 | `git diff --check` | exit 0; `grep -rlP '[ \t]+$'` over every changed file: no matches |
| 6 | Pre-correction resolution restored by temporary edit, four safety files re-run | **48 failed, 196 passed**; edit reverted, **244 passed** |
| 7 | `PGHOSTADDR=127.0.0.1 APP_ENVIRONMENT=test DATABASE_URL='…migration_role:hunter2@/freedom_test?host=/var/run/postgresql' alembic upgrade head` | `UnsafeDatabaseTargetError: DATABASE_URL names the Unix-domain socket directory '/var/run/postgresql', and PGHOSTADDR names the host address '127.0.0.1'…`; **no connection attempted**; `hunter2`, `migration_role` and any raw URL appear **0 times** |
| 8 | The same with `PGHOSTADDR=203.0.113.9`, and with `--sql` | Refused identically; the `--sql` run emitted **0 bytes** on stdout — no DDL, no banner; `hunter2` 0 times |
| 9 | `PGHOSTADDR=127.0.0.1 TEST_DATABASE_URL='…test_role:hunter2@/freedom_test?host=/var/run/postgresql' pytest tests/test_database_repositories.py` | `Refusing to run destructive database tests: …`; 12 errors, no fixture ran; `hunter2` 0 times |
| 10 | Drill by hand, `PGHOST=/var/run/postgresql PGHOSTADDR=127.0.0.1` and `PGHOSTADDR=203.0.113.9`, with `PGPASSWORD` set | Exit `3` each, `Nothing was dumped, dropped or restored.`, the work directory does not exist afterwards, password never echoed |
| 11 | Positive control: `alembic downgrade base` → `upgrade head` → `check` → `heads`, clean environment | `0001` in each direction, `No new upgrade operations detected.`, `0001 (head)`, **10 tables present** — the DDL still commits |
| 12 | Positive control: `DATABASE_URL='postgresql+psycopg:///freedom_test?host=/var/run/postgresql' alembic check` | `No new upgrade operations detected.` — the explicit socket spelling still works when `PGHOSTADDR` is unset |

`freedom_test` was left migrated to `0001` and holding zero rows.

### Checks not run in this round

| Check | Why not |
|---|---|
| Formatter, linter, type checker | Still none configured or installed; unchanged from §6, §14, §15 and §16. Open as §9 item 5 |
| A connection to a genuinely remote `PGHOSTADDR` | Deliberately not attempted: it would mean offering credentials to a server this project is not authorised to contact, which is the exact harm the guard exists to prevent. What *was* done is the local half — `psycopg.connect(host='/var/run/postgresql')` with `PGHOSTADDR=127.0.0.1` was shown to dial TCP — which establishes the precedence the finding turns on. The remote case follows from the same libpq rule and is not separately demonstrated |
| A genuinely tunnelled connection | Unchanged from §16, and unchanged in kind: PostgreSQL's own `inet_*` behaviour through a real SSH forward is still not proven end-to-end |
| Restore into a separate empty database | Still no `CREATEDB` on this host; unchanged from §6, still not claimed |
| Live rehearsal of the append-only runtime grant | Unchanged from §6 and §14 — still the largest gap in the append-only claim, still a deployment-time step (§8 step 5) |
| Anything against `freedom_dev`, staging, production, Discord, Sheets or Foundry | Forbidden. The only database connected to this round was `freedom_test`, over the Unix-domain socket. `.env` was not read |

### Residual limitations

1. **Static validation models libpq; it does not execute it.** The precedence
   above is taken from libpq's documented behaviour and confirmed for the local
   case against psycopg 3.3.4 on this host. A future libpq that changed the
   `host`/`hostaddr` relationship would need this model revisited. The failure
   direction is the safe one — the guards refuse more than libpq's rules
   strictly require — but that is a property to keep checking, not a proof.
2. **Only `PGHOSTADDR` is modelled as a second address source.** `PGSERVICE`,
   `PGSERVICEFILE` and `?service=` are refused outright rather than resolved,
   and `PGOPTIONS` is stripped from the Alembic child and refused by the drill.
   A libpq variable nobody here has enumerated could in principle redirect a
   connection; the mitigation is that the *live* check still asks the server
   where it landed.
3. **Offline `--sql` still cannot verify its target** (§15, §16). Unchanged.
   The static half now also refuses the `PGHOSTADDR` case, so an offline script
   is never generated for it, but a generated script remains text that can be
   applied anywhere.
4. **The forwarded-socket residual** (§16) is unchanged and unclosable in
   process.
5. **Ordinary runtime connections remain out of scope.** None exists yet. When
   one does, `SOCKET_OR_LOOPBACK` is available to it — and the socket/address
   contradiction is refused for it too, because that refusal happens during
   resolution rather than in a policy.

### Remaining Phase 1 blockers

Unchanged by this round:

1. **The plan §17 decision log — all 15 closed.** See the current §13; the gate
   is satisfied by the maintainer rulings recorded on 2026-07-31.
2. **The append-only audit grant is still unrehearsed** (§6, §8 step 5).
3. **Offline `--sql` migrations cannot verify their target** (§15, §16).
4. **No formatter, linter or type checker is configured** (§9 item 5).

### Confirmation

**Phase 2 has not been started** — no importer, no reconciliation code, no
Phase 2 table, and no work of any kind beyond this correction. **Nothing is
committed or pushed**; no remote was contacted. `.env`, credentials, production
services, `freedom_dev`, staging, Discord, Google Sheets and Foundry were not
touched. The only database connected to was `freedom_test`, over the
Unix-domain socket. Phase 1 remains **not approved**.
