# Phase 3 P3.1 submission — authentication and security foundation

**Prepared:** 2026-08-14 · **Package:** P3.1 · **Owner:** Claude (Working
Technical Lead) · **Status:** **Submitted for review. Not accepted. P3.G1 is
open.**

**Authority:** `docs/review/phase-3-p3-1-claude-prompt.md`, under the acceptance
Peter Duscha recorded when he closed P3.G0 on 2026-08-13.

**Review requested:** Codex independent implementation review, and a
**separately reported** security-focused pass. Both are required before P3.2.

---

## 0. Corrections recorded 2026-08-14 after Codex's independent review

Codex reviewed this submission and returned three blocking findings and one
important finding. **The claims below are superseded.** Nothing in this document
has been deleted: the original text stands as the record of what was submitted,
and each superseded claim is annotated in place with the correction that applies
to it. The complete remediation is
[`phase-3-p3-1-remediation-submission.md`](phase-3-p3-1-remediation-submission.md).

| # | Superseded claim | Where | Correction |
|---|---|---|---|
| **C1** | "TC-BG-05a…05e — **Implemented, passing**" | §10 | **Overstated.** The direct-HTTP portions of TC-BG-05b, 05c and 05e are **unrun**: they require R-33, R-34 and R-38, which belong to P3.2 and are intentionally absent. §10.1 said so for 05b alone and the §10 table contradicted it. Portions are now reported separately in the remediation submission §6. A governance decision is requested in [`phase-3-p3-1-tc-bg-05-http-evidence-decision.md`](phase-3-p3-1-tc-bg-05-http-evidence-decision.md) |
| **C2** | "**No historical row is read, updated or deleted.**" | §6.3, §14.1 | **False as stated.** Migration 0006 **reads** `discord_users` for the backfill and **updates** `character_access` with account attribution. The narrower append-only claim is correct and is restated precisely in the remediation submission §7 |
| **C3** | "TC-AUTH-08, TC-AUTH-11 — **Implemented, passing**" | §10 | **Overstated for TC-AUTH-11.** Five terminal OAuth callback refusals wrote no audit event at all. Remediated; see remediation submission §4 |
| **C4** | "no database transaction is held open across a call to Discord" (review request item 2) | §14 | **Accurate, and in unresolved tension with SM-01's prescribed mechanism.** See [`phase-3-p3-1-sm-01-completion-binding-decision.md`](phase-3-p3-1-sm-01-completion-binding-decision.md). Finding 1 is **not** remediated and awaits a maintainer decision |

**P3.G1 is not ready and is not closed.**

---

## 1. The environment prerequisite, confirmed before anything ran

The prompt made P3.1 conditional on a guarded disposable PostgreSQL database.
That was established first, through the repository's **existing** safety
mechanism rather than a new one:

| Check | Result |
|---|---|
| Cluster | PostgreSQL 16.14, `pg_lsclusters` reports `16/main` online |
| Static guard | `assert_disposable_target('postgresql+psycopg:///freedom_test', expected_database='freedom_test', runtime_url=$DATABASE_URL, policy=UNIX_SOCKET_ONLY)` — accepted |
| Live guard | `verify_connected_unix_socket_target` — `current_database() = 'freedom_test'`, `inet_server_addr()` and `inet_client_addr()` **both null** |
| Baseline run | `tests/test_database_postgresql.py` — **40 passed** before any P3.1 change |

Both addresses null is a Unix-domain socket, which a TCP tunnel cannot present.
No credential is recorded here or anywhere in this package. `freedom_production`
does not exist on this host.

---

## 2. Scope delivered

### 2.1 Dependencies and the separate virtualenv

- `requirements-web.txt` — twelve packages. The eleven the configuration contract
  proposed, plus `python-multipart`, which Starlette requires before it will read
  **any** form body (R-05 and R-09 are form routes). Recorded as an addition
  rather than slipped in.
- `requirements-web-dev.txt`, `requirements-web.lock` (the resolved set, 46
  packages).
- `/opt/discord-bots/venv-web`, symlinked as `./venv-web` and gitignored. **The
  bot's virtualenv is not touched** beyond one test-only package
  (`pytest-asyncio`), added to `requirements-dev.txt` so `pytest.ini`'s asyncio
  options are recognised by whichever interpreter runs the suite.

Every rejection in the contract's §1.4 holds: no Redis, no broker, no
`fastapi-users`/`authlib`/`starlette-session`/`fastapi-csrf-protect`, no
`slowapi`, no `pydantic-settings`, no JWT library, no `passlib`, no npm.

### 2.2 Typed configuration and the fifteen startup refusals

`application/web/config.py` builds a frozen dataclass tree through
`WebSettings.from_environment`. It **raises** a typed `ConfigurationError`
listing every problem, names variables and never prints a value. S-01…S-11 are
decided from the environment; S-12, S-14 and S-15 need a resource and live in
`application/web/startup.py`.

Bounds are **ceilings, not defaults**: `WEB_SESSION_IDLE_MINUTES=30` is accepted
and `=90` is refused. Configuration may tighten an accepted policy and never
loosen it.

### 2.3 Migrations

| Revision | Stage | Content |
|---|---|---|
| `0006` | A | `platform_accounts`, `external_identities`, `oauth_token_grants`, `sessions`, `oauth_transactions`, `webauthn_credentials`, `webauthn_challenges`, `recovery_grants`, `auth_rate_limits`, `role_capability_mappings`, `role_capability_mapping_events`; nullable account columns on `character_access` and the three append-only tables; the **`audit_events` constraint swap**; the backfill; control totals T1–T8; the protected bootstrap mapping |
| `0007` | B | `NOT NULL` on the account columns; the account-keyed partial unique indexes **alongside** the Discord-keyed ones |
| `0008` | C | The trigger that maintains `character_access.discord_user_id` as a read-only shadow and refuses a row whose account has no active Discord identity |

Stage D is **not** in this package.

### 2.4 Application and adapter layer

`application/web/`: `config`, `crypto`, `errors`, `view_models`, `capabilities`,
`sessions`, `oauth`, `breakglass`, `role_mappings`, `rate_limit`, `csrf`,
`providers`, `startup`.

`adapters/web/`: `composition`, `repositories`, `discord_provider`,
`middleware`, `app`, and six minimal contract templates.

`tools/`: `web_operator`, `emergency_recovery` (C-01/C-02),
`webauthn_enrollment` (C-03), `portal_kill_switch` (C-06), `session_revoke`
(C-07).

Ten routes, exactly the route contract's §4 set: R-01 to R-10.

### 2.5 Documentation

`docs/operations/web-portal.md` — virtualenv, configuration, key rotation, the
three migration stages and what a downgrade costs, runtime grants, emergency
enrolment and recovery, the kill switch, health, and how to run both suites.
`.env.example` gains a `WEB_*`/`WORKER_*` block with placeholders only; **no
existing line changed**.

---

## 3. Explicitly deferred

| Deferred | Owner | Why it is not here |
|---|---|---|
| R-20…R-38 (member reads, Council links, identity migration UI, role-capability administration, account identities, ratification) | P3.2 | Behind P3.G1. `test_a_route_owned_by_a_later_package_is_absent_from_this_build` asserts their absence |
| R-40…R-49 (import, durable jobs, audit views) | P3.3 | Same |
| The `freedom-worker` process, the job table, the reaper | P3.3 | N-40. P3.1 validates `WORKER_*` bounds and refuses `WORKER_ENABLED=true` in the web process (S-11); it claims no job |
| Migration stage D | A later decision | The point after which rollback becomes recovery, gated on the verification period in the migration contract §6 |
| VM-05…VM-15, VM-17, VM-18 | P3.2/P3.3 | Named in `DEFERRED_VIEW_MODELS` with their owning package, rather than stubbed. A stub is a contract the frontend could start depending on before its authorization exists |
| Gemini production integration, deployment, Caddy, OAuth registration, production database access, Foundry or Sheet mutation | — | Not authorized |

**`design-prototype/` is untouched.** Its 14-entry freeze manifest verifies:
`sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` → 14 OK. No
production module imports or serves it.

---

## 4. Files and migrations changed

### 4.1 New (production)

```
application/web/{__init__,config,crypto,errors,view_models,capabilities,
                 sessions,oauth,breakglass,role_mappings,rate_limit,csrf,
                 providers,startup}.py
adapters/web/{__init__,composition,repositories,discord_provider,middleware,app}.py
adapters/web/templates/{base,login,emergency,non_member,degraded,error}.html
tools/{web_operator,emergency_recovery,webauthn_enrollment,
       portal_kill_switch,session_revoke}.py
migrations/versions/000{6,7,8}_platform_identity_stage_{a,b,c}.py
requirements-web.txt, requirements-web-dev.txt, requirements-web.lock
docs/operations/web-portal.md
```

≈10,000 lines of production code and migrations.

### 4.2 New (tests)

```
tests/web/{conftest,webauthn_double}.py
tests/web/test_{oauth_flow,sessions,break_glass_login,break_glass_escalation,
                security_controls,structural_guards,identity_boundary,
                identity_migration,audit_attribution,rate_limits_and_outage,
                operator_commands}.py
tests/web_fixtures.py
```

≈5,500 lines; 197 tests.

### 4.3 Modified, and why

| File | Change |
|---|---|
| `application/audit.py` | The `UNATTENDED_CAPABILITIES` guard now accepts an account id. **Moved in the same revision as the constraint**, per schema §6.1.1 |
| `adapters/database/tables.py` | The eleven new tables; the account columns on `character_access`, `audit_events`, `snapshot_imports`, `foundry_snapshots`; the swapped audit check; the new indexes; `role_capability_mapping_events` added to `APPEND_ONLY_TABLES` |
| `adapters/database/repositories.py` | The audit writer persists `actor_platform_account_id` |
| `infra/postgresql/runtime-grants.sql.tmpl` | The eleven new tables, in the three bands of schema §11.2 |
| `.env.example` | A new `WEB_*`/`WORKER_*` block. No existing line changed |
| `.gitignore` | `venv-web` |
| `pytest.ini` | `asyncio_mode = auto` and the loop-scope default |
| `requirements-dev.txt` | `pytest-asyncio` |
| `tests/conftest.py` | Bootstrap snowflakes for migration 0006; `link_platform_account`/`account_for` helpers; the `pytest_ignore_collect` hook |
| `tests/test_database_postgresql.py` | `insert_user` also links an account; `grant_access` resolves accounts from identities |
| `tests/test_database_schema.py` | The Phase 3 table set; the swapped audit constraint asserted in both directions |
| `tests/test_runtime_grants.py` | The no-`DELETE` band; the append-only set; trigger migrations 0002 **and** 0006 |
| `tests/test_snapshot_database.py` | Raw import fixtures name a Council actor, because the new attribution check requires one |
| `tests/benchmark_snapshot_500.py`, `tests/test_benchmark_harness.py` | "Clean" now means "as the migration left it" — the protected mapping is a migration-seeded row, not dirt |
| `tests/test_rejected_scope_absent.py` | The import-graph walk skips portal modules under the bot interpreter, bounded to web-only missing packages |
| `docs/project-management/{status,raid-register,change-log}.md` | Facts actually changed by P3.1 |

---

## 5. Dependency and configuration changes

New runtime dependencies: `fastapi`, `uvicorn[standard]`, `jinja2`,
`itsdangerous`, `httpx`, `webauthn`, `cryptography`, `python-multipart`. New
test dependency: `pytest-asyncio`, `beautifulsoup4`.

New configuration: 46 `WEB_*` variables and 8 `WORKER_*` variables, all
documented in `.env.example` with placeholders. Four secret keys are required
and must differ from one another.

**No secret value appears anywhere in this package.** `.env` was neither read
nor modified. A scan of every new module for credential-shaped literals and
long base64 strings returns nothing, and
`test_a_configuration_error_names_variables_and_never_values` puts a
recognisable marker in every variable and asserts it is absent from the rendered
error.

---

## 6. Security, privacy, migration, rollback and operational effects

### 6.1 Security

- **The `audit_events` attribution rule is replaced, not relaxed.** Its subject
  widened from *a Discord user* to *an identified person*. An unattributed human
  action is still refused, by the database and by `application/audit.py`. This is
  what makes an emergency login **recordable**, and therefore possible, during a
  Discord outage — the availability half of OD-43.
- **N-67 is enforced by three independent controls**: the application service
  (before any row is read or written), the check constraint
  `created_under_scope = 'full' OR capability = 'platform_administrator'` (which
  depends on what is being written, not on who is writing it), and the route
  surface. TC-BG-05d exercises the second with the application bypassed entirely.
- **Provenance travels with the mapping.** Administrator authority held only
  through emergency-provenance mappings is itself continuity-scoped, through an
  ordinary Discord login as well.
- The PKCE verifier is encrypted and AAD-bound to its transaction row, recovered
  **once**, and erased in the same statement that reads it. The `state` is
  hashed. Neither is logged, and neither appears in any audit payload.
- Sessions are opaque; the row holds a SHA-256, never the cookie value. Rotation
  is insert + revoke.
- Provider tokens are AES-256-GCM encrypted, AAD-bound to the identity, and
  **deleted** on logout, on operator revocation and with the account's sessions.

### 6.2 Privacy

Client addresses and user-agent strings are stored only as HMACs under a
configured key. Rate-limit buckets carry a keyed digest, never an address. The
scopes are exactly `identify guilds.members.read`; a wider one is a startup
refusal. `external_identities` has **no** name, username or email column, and a
test asserts that structurally.

### 6.3 Data migration

`upgrade → downgrade → upgrade` was executed against real PostgreSQL for the
full range and for each stage individually. Control totals T1–T8 run inside
stage A's own transaction and abort it on disagreement.

> **Superseded 2026-08-14 by correction C2 (§0).** The sentence below is false
> as written: migration 0006 reads `discord_users` and updates
> `character_access`. The append-only half of the claim is correct and is
> restated precisely in the remediation submission §7.

**No historical row is read, updated or deleted.** `ADD COLUMN` without a
default, `ADD CONSTRAINT … NOT VALID` and `DROP CONSTRAINT` are catalogue
operations; row triggers do not fire for DDL, so the migration-0002 append-only
trigger is neither dropped, disabled nor evaded — it is never reached.
`test_history_is_byte_identical_across_the_swap_including_its_row_versions`
compares `xmin`, which is PostgreSQL's own record of which transaction last wrote
each row: unchanged `xmin` proves no row **was written**, not merely that the
rows look the same.

### 6.4 Rollback

| Position | Reversal | Cost |
|---|---|---|
| After 0006 | `alembic downgrade 0005` | The legacy constraint returns `NOT VALID`. **Dropping `actor_platform_account_id` discards the attribution of every audit event written by a break-glass session after the upgrade** — the events survive, their actor becomes unresolvable |
| After 0007 | `alembic downgrade 0006` | None |
| After 0008 | `alembic downgrade 0007` | None; the shadow column is current because the trigger kept it current |

The consequence in the first row is stated in the revision docstring, in
`docs/operations/web-portal.md` §3.3 and here, because an operator will meet it
in one of the three.

### 6.5 Operational

A second systemd-managed process will be required at deployment; **none is
created**. The kill switch, session revocation, credential enrolment and
recovery-grant issuance are host-local commands, and no HTTP route performs any
of them.

---

## 7. Accepted invariants, mapped to implementation and evidence

| Invariant | Implementation | Evidence |
|---|---|---|
| Legacy Discord-only audit constraint replaced in the accepted order, with `application/audit.py` in the same revision | `0006._swap_audit_attribution_constraint`; `UNATTENDED_CAPABILITIES` | `test_before_the_swap_a_discord_independent_human_event_is_refused`, `test_account_attributed_inserts_succeed_in_both_forms`, `test_an_unattributed_human_action_is_rejected_by_the_database`, `…_by_the_python_guard`, `test_machine_capabilities_remain_valid_with_no_attribution_at_all` |
| The three append-only tables treated on their own evidence | `audit_events` swapped; `snapshot_imports` strengthened `NOT VALID`; `foundry_snapshots` column + FK only | `test_the_constraint_inventory_of_all_three_tables_is_exactly_as_documented`, `test_foundry_snapshots_gained_a_column_and_no_constraint` |
| Append-only history never rewritten; the 0002 trigger never suspended | Catalogue-only DDL | `test_history_is_byte_identical_across_the_swap_including_its_row_versions`, `test_append_only_denial_still_holds_after_the_swap` |
| A break-glass or emergency-derived session cannot acquire **or arrange** Council, character or import authority | `resolve_capabilities` short-circuit + `_administrator_scope` + `RoleMappingService` + the check constraint | `test_the_whole_escalation_sequence_is_refused` (the **multi-login sequence**, not each request in isolation), `test_a_continuity_scoped_create_is_refused_and_recorded`, `test_the_constraint_refuses_the_same_thing_with_the_application_bypassed`, `test_administrator_scope_resolution_is_parametrized_exactly_as_documented` |
| Continuity-scoped authority becomes full only through R-38 by a full-scope administrator on an ordinary-provider session | `require_full_administrator_scope`; the one-way trigger | `test_ratification_by_a_full_scope_administrator_restores_full_scope`, `test_ratification_is_one_way_and_happens_once` |
| Protected mapping immutability | `reject_protected_mapping_change`, `reject_second_protected_mapping` | `test_the_protected_bootstrap_mapping_cannot_be_changed_by_anyone`, `test_a_second_protected_mapping_and_a_second_protected_account_are_refused` |
| PKCE state hashed; verifier encrypted, AAD-bound, recovered once, erased in the same statement; neither logged | `OAuthTransactionRepository.consume`; `Envelope` + `transaction_aad` | `test_the_stored_pkce_verifier_is_ciphertext_and_never_its_hash`, `test_a_verifier_moved_to_another_transaction_row_refuses_to_decrypt`, `test_consumption_erases_the_verifier_in_the_same_statement`, `test_two_concurrent_callbacks_yield_exactly_one_exchange` |
| No P3.3 reconciliation worker or job system in this package | Absent | `test_the_registered_route_set_equals_the_contract_exactly`, `test_a_route_owned_by_a_later_package_is_absent_from_this_build` |

---

## 8. Contract deviations, declared

Three, each the narrowest change that made an accepted contract implementable.
None weakens a control; each is carried into P3.G1 as RAID assumption **A-07**.

### 8.1 `role_capability_mappings.created_by_account_id` is nullable

Schema §8 says `Null: no` **and** that migration inserts the protected row. Those
cannot both hold: the accounts table is created empty in the same revision, so
there is no account for the protected row to name.

Implemented as nullable with
`CHECK (created_by_account_id IS NOT NULL OR protected)` — so exactly one row may
omit it, and that row is trigger-immutable anyway.
`test_the_protected_bootstrap_mapping_is_inserted_by_the_migration` asserts the
null is present and confined.

### 8.2 `WEB_SECRET_KEY_CLIENT_DIGEST` is added

The configuration contract's §2.2 names three secrets; S-08 says "the four
secret keys". The accepted **schema** specifies `sessions.client_ip_hash` as a
*salted* hash and `auth_rate_limits.bucket` as hashing the address. An unkeyed
SHA-256 over an IPv4 address is reversible by exhaustive search in seconds, so
without a key the "hash" would be the address with extra steps. The fourth key
is this one plus the active encryption key, which makes S-08's count exact.

### 8.3 `webauthn_challenges` is added

SM-03 requires "a challenge row with an N-04 lifetime"; schema §9 lists no table
for it. Added, storing the challenge in the clear — it is a public nonce that
must be handed to the browser and compared byte-for-byte, and a hash could not be
presented as `expected_challenge`.

### 8.4 Two smaller notes

- **Stage A adds the `character_access` foreign keys** beside the columns, rather
  than deferring them to stage B as the contract's stage table sketches. The
  reversal boundary is unchanged and a nullable column with its FK cannot hold an
  unresolvable account id even briefly.
- **`python-multipart`** is a twelfth dependency, required by Starlette before it
  will parse any form body.

---

## 9. Every command, and its exact result

Run 2026-08-14 on this host. `$DB` is
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`.

| # | Command | Result |
|---|---|---|
| 1 | `psql --dbname=freedom_test -c 'SELECT current_database(), inet_server_addr(), inet_client_addr()'` | `freedom_test`, both addresses **null** |
| 2 | `$DB ./venv/bin/python -m pytest tests/test_database_postgresql.py -q` (baseline, before any change) | **40 passed** |
| 3 | `APP_ENVIRONMENT=test DATABASE_URL=… WEB_DISCORD_GUILD_ID=… WEB_BOOTSTRAP_ADMIN_ROLE_ID=… ./venv/bin/alembic downgrade base` then `upgrade head` then `downgrade base` then `upgrade head` | Head `0008` both times; no error |
| 4 | `./venv/bin/alembic check` | **No new upgrade operations detected** |
| 5 | `./venv/bin/alembic upgrade head --sql` | Script generated: 53 DDL statements; revision 0006's offline notice present (1 occurrence) |
| 6 | `$DB ./venv/bin/python -m pytest -q` | **2251 passed, 0 failed, 0 skipped**, 1 warning, 124.70s |
| 7 | `$DB ./venv-web/bin/python -m pytest -q tests/web` | **197 passed, 0 failed, 0 skipped**, 5 warnings, 19.70s |
| 8 | `./venv/bin/python -m pytest -q` (no `TEST_DATABASE_URL`) | **1998 passed, 253 skipped** — the skips are the database suites, refusing rather than passing without a guarded database |
| 9 | `./venv-web/bin/python -m pytest -q tests/web` (no `TEST_DATABASE_URL`) | **47 passed, 150 skipped** — the 47 are the structural and configuration tests, which need no database |
| 10 | `$DB ./venv/bin/python -m pytest -q tests/test_runtime_grants.py tests/test_runtime_grants_live.py` | **56 passed** — grants proven under `SET ROLE freedom_runtime_test` against real PostgreSQL |
| 11 | `./venv-web/bin/python -m compileall -q application adapters domain tools migrations tests` | exit 0 |
| 12 | `./venv/bin/python -m compileall -q …` | exit 0 |
| 13 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 14 | Relative-link check over `docs/**/*.md` | 403 links checked; 8 broken, **all pre-existing Phase 2 documents** (`Handover%20information`, four `file:///` URLs in `phase-2-r4-500-actor-benchmark.md`). No link in any P3.0 or P3.1 document is broken |
| 15 | Secret-shape scan of every new module | No credential-shaped literal, no long base64 literal |
| 16 | `git status --porcelain .env` | Empty — `.env` was neither read nor modified |

The warnings in 6 and 7 are: one `audioop` deprecation from `py-cord` on Python
3.12 (pre-existing), and five `httpx` deprecations for per-request cookies in the
portal tests.

### 9.1 Formatter, linter and type checker

**None is configured or installed**, re-verified for this package exactly as
Phase 2 recorded it: no `pyproject.toml`, `setup.cfg`, `.flake8`, `ruff.toml` or
`mypy.ini` exists, and `black`, `ruff`, `flake8`, `mypy`, `pyright`, `isort` and
`pylint` are all absent from both virtualenvs. `compileall` was run in both as
the nearest available check (rows 11 and 12).

This remains an open maintainer decision, unchanged by P3.1. No such dependency
was introduced, because choosing and configuring one is a repository-wide change
rather than part of this package.

### 9.2 Evidence deliberately **not** claimed

| Class | Checks | Why |
|---|---|---|
| `staging` | TC-LIM-02, TC-SEC-07's browser half, TC-OPS-01…05, TC-PERF-01…03 | **Staging does not exist.** Recorded as issue I-06 |
| `real-device` | TC-UI-08 | Peter's own hardware |
| `assistive-technology` | TC-UI-09 | Not planned or scheduled; inherited as `not tested` |
| `browser` | TC-UI-01…07 | P3.4's package |
| Live Discord | Every provider interaction | The tests use a scripted double. **No production Discord application or guild was contacted** |

No staging, browser, live Discord, real-device or assistive-technology evidence
is claimed anywhere in this document.

---

## 10. P3.1-owned traceability, test by test

| Test case | Status | Named test(s) |
|---|---|---|
| TC-AUTH-01…06 | **Implemented, passing** | `test_oauth_flow.py` |
| TC-AUTH-07, TC-AUTH-12 | **Implemented, passing** | `test_the_stored_pkce_verifier_is_ciphertext_and_never_its_hash`, `test_a_verifier_moved_to_another_transaction_row_refuses_to_decrypt`, `test_consumption_erases_the_verifier_in_the_same_statement`, `test_two_concurrent_callbacks_yield_exactly_one_exchange` |
| TC-AUTH-08, TC-AUTH-11 | **Implemented, passing** — *superseded by correction C3 (§0); TC-AUTH-11 was overstated* | `test_a_non_member_callback_creates_no_session_and_answers_403`, `test_a_member_login_creates_one_session_and_one_audit_event` |
| TC-AUTH-09, TC-AUTH-10 | **Implemented, passing** | `test_rate_limits_and_outage.py` |
| TC-SESS-01…10 | **Implemented, passing** | `test_sessions.py`; TC-SESS-06 in `test_rate_limits_and_outage.py` |
| TC-BG-01…04, 06…15 | **Implemented, passing** | `test_break_glass_login.py`, `test_operator_commands.py`, `test_security_controls.py` (TC-BG-10) |
| TC-BG-05a…05e | **Implemented, passing** — *superseded by correction C1 (§0); the direct-HTTP portions of 05b/05c/05e are unrun* | `test_break_glass_escalation.py` |
| TC-ID-01…07 | **Implemented, passing** | `test_identity_boundary.py` |
| TC-MIG-01…06, 14…16 | **Implemented, passing** | `test_identity_migration.py`, `test_audit_attribution.py` |
| TC-CAP-01, 03…06, 08, 10, 11 | **Implemented, passing** | `test_break_glass_escalation.py`, `test_rate_limits_and_outage.py` |
| TC-AUD-09…14 | **Implemented, passing** | `test_audit_attribution.py` |
| TC-SEC-01…06, 08…13 | **Implemented, passing** | `test_security_controls.py` |
| TC-SEC-07 | **Partly implemented** | Automated half passing; the staging browser half is unrun |
| TC-LIM-01, 03 | **Implemented, passing** | `test_security_controls.py` |
| TC-LIM-02 | **Unrun** | Requires the deployed proxy configuration |
| TC-OUT-01…04 | **Implemented, passing** | `test_rate_limits_and_outage.py` |
| TC-STRUCT-01, 04, 05, 06 | **Implemented, passing** | `test_structural_guards.py` |
| TC-VM-01, 02 | **Implemented, passing** | `test_structural_guards.py` |

### 10.1 Partials, named rather than counted as complete

- **TC-STRUCT-02** (implemented view-model set *equals* the documented set) is
  implemented as a **subset** check plus an exhaustive ownership check: every
  implemented model is documented, and every documented model is either
  implemented or named in `DEFERRED_VIEW_MODELS` with its owning package. Full
  equality is reachable only once P3.2 and P3.3 implement theirs.
- **TC-CAP-02 and TC-CAP-09** are `[MATRIX]` tests over the whole route
  inventory. P3.1 registers the ten authentication routes, none of which is
  capability-gated, so the matrix has no protected cell to exercise yet. The
  capability facts they rest on — administrator does not imply Council, `AC`
  resolves exactly as `BG` — are asserted at the service level in
  `test_break_glass_escalation.py`. The HTTP matrix belongs to P3.2.
- **TC-BG-05b** (direct HTTP to R-33/R-34/R-38) cannot be issued: those routes
  are P3.2's. The same parametrisation is exercised against the service and
  against the check constraint (TC-BG-05a, 05c, 05d).
- **TC-ID-07** asserts the *fact* an unlink refusal will rest on — the active
  identity count, with retired identities excluded. R-37 is P3.2's route.
- **TC-STRUCT-03**, **TC-OBJ-\***, **TC-ACC-\***, **TC-JOB-\***,
  **TC-AUD-01…08** are P3.2/P3.3-owned and are not claimed here.

---

## 11. Assumptions

1. The bot's virtualenv is a live production environment, so the portal's
   dependencies were **not** installed into it. The consequence is two test
   commands rather than one, both reported above.
2. The synthetic guild snowflake `900000000000000001` and role
   `900000000000000002` are used by `tests/conftest.py` for migration 0006.
   They are far outside Discord's issued range, and `WebSettings` refuses the
   real production guild outside production regardless (S-07).
3. `worker_heartbeat` and `expired_leases` are reported `ok` by `/healthz` with
   nothing behind them, because the worker is P3.3's. The names are in VM-16's
   accepted vocabulary so P3.3 can make them real without a contract change.
4. The WebAuthn registration ceremony happens in a browser; C-03 takes its
   result. No browser was involved in this package, and the assertion tests use
   a software authenticator that signs real ES256 assertions verified by
   `py_webauthn` as written.

---

## 12. Residual risks

| # | Residual | Recorded |
|---|---|---|
| 1 | **A-05 is still unvalidated.** No WebAuthn credential has been enrolled on any host, so the emergency route exists and cannot be used. Until it holds, a Discord outage locks the administrator out | RAID A-05 |
| 2 | RR-13's persistence gain is real and delivered: a break-glass session can leave a continuity-scoped administrator mapping behind it. That is what the recovery case requires; it reaches no Council, character or import authority | ADR 0010 |
| 3 | RR-03's 2× fixed-window burst at the boundary | N-30 |
| 4 | RR-02: a link prefetcher can replace a pending login transaction. The failure is a recoverable "please sign in again" | Route contract §6.4 |
| 5 | The stage-C shadow trigger is proven against synthetic rows only. No production `character_access` row exists to migrate — the migration contract §2 records that the production database holds none | Migration contract §2 |
| 6 | Peak memory and latency under real audit volume are unmeasured; the historical-attribution resolution join is bounded by page size but has never been run against real volume | P3.5 |
| 7 | No formatter, linter or type checker exists, so this package's ~15,500 new lines carry no static analysis beyond `compileall` | §9.1; open maintainer decision |

---

## 13. Clean-worktree and diff account

`git status --porcelain` at submission. The working tree contains **both** P3.0's
documentation changes and P3.1's implementation, because P3.0 was accepted but
never committed. They are separated here so a reviewer can tell them apart.

### 13.1 Pre-existing P3.0 documentation changes — **not P3.1's**

```
 M docs/adr/README.md
 M docs/discovery/open-decisions.md
 M docs/project-management/decision-register.md
?? docs/adr/0010-provider-neutral-identity-and-emergency-administration.md
?? docs/contracts/                     (11 files)
?? docs/review/phase-3-p3-0-remediation-claude-prompt.md
?? docs/review/phase-3-p3-0-remediation-submission.md
?? docs/review/phase-3-p3-0-submission.md
?? docs/review/phase-3-p3-1-claude-prompt.md   (the prompt this package executes)
```

P3.1 changed none of these. `docs/project-management/{status,raid-register,change-log}.md`
were modified by P3.0 **and** by P3.1; the P3.1 additions are the 2026-08-14
status date, the P3.G1 row, A-02's re-confirmation, A-05's mechanism note, A-07,
I-06 and change-log entry **C-P3.1**.

### 13.2 P3.1's own changes

Everything in §4. Twenty-two modified files and the new trees
`application/web/`, `adapters/web/`, `tests/web/`,
`migrations/versions/000{6,7,8}_*`, the five `tools/` modules, the three
`requirements-web*` files and `docs/operations/web-portal.md`.

### 13.3 Not committed

Nothing was committed and no branch was created; the working tree is
`docs/platform-plan` as it was found. `.env`, `yt-cookies.txt` and every
credential file are untouched. `venv-web` is a gitignored symlink to
`/opt/discord-bots/venv-web`.

---

## 14. Review request

**Codex independent implementation review** is requested over:

1. migration 0006's statement ordering, the control totals, and the claim that
   no historical row is read or written — *the claim was false; see correction
   C2 (§0)*;
2. the sync/async seam — that no database transaction is held open across a call
   to Discord, and that no database work runs on the event loop;
3. the two-transaction pattern for refusal records (`run_mapping_change`,
   `record_authentication_failure`) and whether any refusal path still writes its
   record inside the transaction it rolls back;
4. the three declared deviations in §8; and
5. the partials in §10.1 — whether any of them should block P3.G1 rather than
   wait for its owning package.

**A separately reported security-focused pass** is requested over:

1. the N-67 escalation sequence and all three of its controls, including whether
   a fourth path exists that `test_the_whole_escalation_sequence_is_refused` does
   not walk;
2. the PKCE verifier's storage, AAD binding, single recovery and erasure;
3. session rotation, expiry clamping and revocation, and the CSRF derivation;
4. the break-glass surface: what a compromised emergency session can *arrange*,
   not only what it can do; and
5. the rate limiter's placement outside the work transaction, and whether that
   creates a counting path an attacker can exploit in the other direction.

---

P3.1 submitted for Codex independent and distinct security re-review; P3.G1 remains open and P3.2 has not started.
