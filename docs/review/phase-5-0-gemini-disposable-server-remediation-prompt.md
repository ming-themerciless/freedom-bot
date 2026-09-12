# Prompt for Gemini — disposable test server remediation before P5.0 evidence

Work in `/opt/freedom-blades/platform` and on the explicitly disposable host
`oracle-test` only where this prompt permits it.

## Authority and outcome

Peter Duscha asked Codex to review and test Gemini's new disposable server.
Codex's 2026-09-05 review found that the host is reachable, grants the intended
administrative access, and uses persistent ext4, but it is not yet a faithful
repository test environment or an admissible Package 5.0 evidence target.

Remediate the disposable server setup and its documentation. Return a clean,
repeatable PostgreSQL 16 test lane whose full-suite results have the expected
coverage. Then prepare the exact target facts needed for Claude to regenerate
the Package 5.0 evidence execution plan. Stop there.

This prompt does **not** authorize execution of the Package 5.0 evidence
harness, C-1/C-3/C-4, creation of Package 5.0 evidence identities or journal
objects, migration `0014`, Package 5.0 product implementation, any production or
staging mutation, deployment, cutover, OD-62, Package 5.1+, or copying any real
credential or player data to the disposable host.

## Roles and separation

- **Gemini:** implements and verifies this disposable-server remediation.
- **Claude:** remains the Package 5.0 evidence-harness executor. Gemini must not
  execute that harness or claim its evidence.
- **Codex:** independently reviews the remediated server, target-specific plan,
  and later operational evidence.
- **Peter Duscha:** Operations Owner and Acceptance Authority; only Peter can
  confirm the named target as disposable and authorize the later evidence run.

## Required reading and worktree discipline

Before planning or changing anything, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. this prompt;
5. `docs/operations/disposable-test-server.md`;
6. `docs/operations/database-development.md`;
7. `docs/review/phase-5-0-evidence-harness-authorization-draft.md`;
8. `docs/review/phase-5-0-evidence-harness-execution-plan.md`;
9. `tests/conftest.py` and `tests/web/conftest.py`;
10. `tests/test_database_backup_restore.py`;
11. `tests/test_runtime_grants_live.py`; and
12. `tests/web/test_p3_2_runtime_grants_and_bounds.py`.

Check local and remote `git status` first. Preserve the complete local dirty
worktree. Do not reset, revert, stage, commit, push, or overwrite unrelated
changes. The remote repository is disposable test state, but record its initial
inventory before changing it and never infer that a file is safe to delete from
its absence in an rsync source.

## Review evidence to reproduce

Codex observed the following on `oracle-test`:

- SSH works as `ubuntu`; `sudo -n id` returns root without a prompt.
- Ubuntu 26.04, kernel `7.0.0-1009-oracle`, persistent ext4 root filesystem.
- one CPU, approximately 1 GiB RAM, no swap;
- system Python 3.14.4, while the dedicated test virtual environment correctly
  uses Python 3.12.14 and pytest 8.4.2;
- PostgreSQL 18.6 is the active default cluster;
- `freedom_test` and `freedom_dev` exist, owned through the `ubuntu` superuser;
- `freedom_runtime_test` does not exist;
- the synchronized repository is missing tracked `.env.example`;
- focused harness/scope/crafting tests: **481 passed**;
- bot suite: **3061 passed, 5 failed, 56 skipped**;
- web suite after recreating `freedom_test`: **2803 passed, 1 failed, 114
  skipped**; the accepted web baseline is exactly **80** skips;
- Foundry suite: **171 passed**; and
- local `git diff --check` reports a trailing blank line in `CLAUDE.md`.

The backup/restore drill failed after PostgreSQL 18 restored the schema because
its default `public` schema privilege state includes PostgreSQL-version-specific
`pg_database_owner` entries that differ from the PostgreSQL 16 baseline. The
drill correctly declared recovery required. Codex then recreated only the
disposable `freedom_test` database before continuing. Do not describe that run
as passing and do not reuse its partially restored database.

## Finding DS-R1 — Blocking: the authoritative lane is on the wrong PostgreSQL major

The controlled environment and current deployment baseline are PostgreSQL 16.
Package 5.0 operational evidence must be representative of that baseline. A
PostgreSQL 18-only result is forward-compatibility information, not substitute
evidence, and currently fails the backup/restore contract.

Create a dedicated PostgreSQL **16** cluster on `oracle-test` and make the
documented authoritative test command unambiguously reach it through a local
Unix-domain socket. It may coexist with PostgreSQL 18, but:

- PostgreSQL 16 must own the authoritative `freedom_test` lane;
- PostgreSQL 18 must use a different port/socket or be stopped during the
  authoritative run so there is no ambiguous default socket;
- record version, cluster name, port, socket directory, data directory and
  configuration directory;
- do not reuse `freedom_test` across PostgreSQL majors;
- do not weaken the repository's Unix-socket safety checks;
- do not edit backup/restore expectations merely to accept PostgreSQL 18; and
- do not upgrade or change production PostgreSQL.

If PostgreSQL 16 packages cannot be obtained from an approved Ubuntu/PGDG
source for this host, stop and report the exact packaging blocker. Do not
silently redefine PostgreSQL 18 as the package baseline and do not downgrade the
host operating system as an incidental fix.

PostgreSQL 18 may remain as a separately named optional compatibility lane.
Any future project support or production upgrade to PostgreSQL 18 is a separate
architecture and compatibility change, not part of this remediation.

## Finding DS-R2 — Blocking: restricted-role evidence is absent

Provision `freedom_runtime_test` **only on the PostgreSQL 16 test cluster** with
the contract already documented by `tests/test_runtime_grants_live.py`:

- `NOLOGIN`;
- not superuser;
- cannot create roles or databases;
- cannot replicate;
- cannot bypass RLS; and
- the PostgreSQL 16 test-owner login is a member so tests can exercise it with
  `SET ROLE`.

Do not grant application privileges by hand as a shortcut. The migrations and
grant templates under test establish and verify those privileges. Add a
read-only preflight that prints only role attributes and membership—never
credentials—and fails before pytest if the role contract is absent.

The final bot and web runs must not contain restricted-role skips. The web
suite must return to exactly the 80 documented permission-matrix skips.

## Finding DS-R3 — Important: synchronization omits a tracked contract file

The current command uses `--exclude '.env*'`, which also excludes the tracked,
non-secret `.env.example`. The remote tree therefore differs from the reviewed
tree and two filesystem-layout tests fail with `FileNotFoundError`.

Correct every documented sync command so that:

- `.env.example` is included;
- actual `.env`, `.env.*` secret variants, private keys, service-account files,
  caches and generated bytecode remain excluded;
- the include/exclude ordering is tested with `rsync --dry-run --itemize-changes`
  before the real synchronization;
- synchronization never follows or copies an external symlink;
- no production secret is read merely to decide whether to copy it;
- the remote tree is scanned by **name and metadata only** for forbidden secret
  files before tests; and
- the post-sync manifest proves every tracked file required by the test tree is
  present.

Do not use a broad `--delete-excluded`: excluded secret-shaped files require a
deliberate inventory and refusal, not silent deletion. If any real credential or
player-data file is found on the remote host, stop, report only its path and
metadata, and do not open, copy, print or delete it.

The remote test command must supply synthetic non-secret configuration for the
legacy connector import test. It must not copy the primary host's `.env` or use
a real Discord token, guild/channel ID, Sheet ID, or service-account key. Record
the synthetic variable names and bounded placeholder shapes, but do not invent
a service credential or make any Discord/Google request.

## Finding DS-R4 — Important: the P5.0 target is still unassigned

Do not edit the execution plan's `UNASSIGNED` placeholders as part of server
installation. Instead, produce a proposed target-facts handback containing:

- disposable host alias and stable host identity;
- exact PostgreSQL 16 cluster, socket and configuration directory;
- a proposed database named `fb_evidence_*`, never `freedom_test`;
- an absolute persistent ext4 evidence root at least three levels deep whose
  final component starts `fb-evidence-`;
- proof the root is outside `/run`, `/tmp`, `/dev/shm`, the repository,
  production paths and every `DisposableTarget.FORBIDDEN_ROOTS` entry;
- the before-state showing the proposed evidence database, identities, groups,
  target root and transient unit do not already exist;
- confirmation that no production credential or data is present; and
- an explicit reason the entire target is disposable.

Peter must confirm those facts and Codex must approve a regenerated exact plan
before Claude performs any mutation-bearing evidence step. Gemini must not
create `freedomcoord`, `freedomsheet`, `fbprobe`, `freedomjournal`, an
`fb_evidence_*` database, evidence HBA/ident rules, journal/probe paths or a
transient evidence unit during this remediation.

## Finding DS-R5 — Minor: documentation hygiene and authority

Remove the trailing blank line currently reported in `CLAUDE.md`, then make
`git diff --check` pass. Review the new server documentation and agent-entry
changes for these constraints:

- administrative access is scoped to the explicitly disposable host;
- no wording grants authority over production or bypasses a review gate;
- destructive examples name exact disposable objects and retain safety checks;
- the public IP and SSH alias are operational routing facts, not proof of
  disposability;
- no private key material or host-key contents are committed; and
- the documentation does not claim the full suites pass until they do.

Do not add more duplicated server instructions to agent entry points. Keep the
canonical operational procedure in `docs/operations/disposable-test-server.md`
and make entry points link to it concisely.

## Regression-first and recovery sequence

1. Capture local and remote status, host identity, cluster inventory, versions,
   mounts, roles and databases without reading secrets.
2. Reproduce the sync dry-run and `.env.example` omission before correcting it.
3. Preserve the PostgreSQL 18 failure as evidence; do not repeatedly run the
   destructive drill against a database already in recovery state.
4. Install/configure PostgreSQL 16 and provision only its test database and
   restricted test role.
5. Correct and dry-run synchronization, then sync the reviewed worktree without
   secrets.
6. Recreate only the PostgreSQL 16 `freedom_test` database immediately before
   verification.
7. Run focused environment and backup/restore checks first. If the drill fails,
   follow its exact recovery output, stop the full suites, and report the
   failure.
8. Run bot and web suites serially; they share `freedom_test`.
9. Run Foundry tests, compilation and `git diff --check`.
10. Capture the final remote inventory and prove no unintended evidence objects
    or residue were created.
11. Write the remediation handback and return to Codex. Do not proceed to the
    P5.0 harness.

## Required verification

Use the remote Python 3.12 environment and the PostgreSQL 16 Unix socket. Record
the exact resolved URL without credentials and prove `SHOW server_version`
reports major 16 before any destructive test.

Run serially:

```sh
# Exact PostgreSQL-16 socket URL is chosen and recorded during remediation.
export TEST_DATABASE_URL='<POSTGRESQL_16_UNIX_SOCKET_URL_FOR_freedom_test>'

/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q \
  tests/test_database_backup_restore.py \
  tests/test_runtime_grants_live.py \
  tests/web/test_p3_2_runtime_grants_and_bounds.py \
  tests/test_filesystem_layout.py

/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/test_*.py
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
/opt/freedom-blades/runtime/venv-web/bin/python -m compileall -q \
  tools/phase_5_0_evidence tests/phase_5_0_evidence
git diff --check
```

The two pytest suites must run one after the other. Passing evidence requires:

- no unexpected test failure;
- the web suite has exactly 80 skips;
- no restricted-role test skips because `freedom_runtime_test` is absent;
- `.env.example` exists and matches the synchronized source;
- PostgreSQL 16 is the server actually reached through the Unix socket;
- no network call to Discord, Google Sheets, Foundry or another external
  application; and
- no production or staging mutation.

Do not preserve a green result by weakening, deselecting or marking a failing
test. If the accepted totals differ only because the submitted tree gained
tests, explain the arithmetic; never carry forward Codex's totals as if they
were results from the remediated tree.

## Required handback

Create `docs/review/phase-5-0-gemini-disposable-server-remediation-handback.md`
containing:

- all five findings conceded before their corrections;
- every local documentation and remote infrastructure change;
- package sources and versions;
- PostgreSQL 16/18 cluster, socket, port and ownership inventory;
- exact restricted-role attributes and membership;
- safe synchronization dry-run and final manifest evidence;
- exact commands and results, including failures and recovery;
- suite totals, skips, warnings and durations;
- before/after database and filesystem state;
- confirmation that no secret, player data or production state was accessed or
  copied;
- the proposed P5.0 target facts, still explicitly **not executed**;
- residuals, including VM CPU/memory limits and any PostgreSQL 18
  incompatibility; and
- a request for Codex independent review that claims no P5.0 finding, assumption
  or readiness criterion closed.

Update `docs/review/Handover information` only after all remediation checks
pass. Its new current entry must say the disposable-server remediation is
submitted to Codex, the P5.0 harness remains unexecuted, its target remains
unapproved until Peter and Codex act, P5.0-R5 remains Blocking, and Package 5.0
remains `not ready`.

Stop after handback. Do not execute the evidence harness, close P5.0-R4/R5,
confirm A-5.0-4/A-5.0-5, rule OD-62, recommend package readiness, implement
Package 5.0, or begin Package 5.1.
