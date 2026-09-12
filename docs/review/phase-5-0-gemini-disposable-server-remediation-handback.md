# Phase 5.0 Gemini Disposable Server Remediation Handback (Round 4)

- **Date:** 2026-09-05
- **Remediating Agent:** Gemini
- **Target Environment:** Dedicated Disposable Linux Test Server (`oracle-test` / `138.2.182.39`, Ubuntu 26.04 LTS x86_64)
- **Review Prompts:** `docs/review/phase-5-0-gemini-disposable-server-remediation-prompt.md` (and subsequent Codex reviews R2/R3/R4)
- **Current Status:** Round 4 documentation remediation accepted. Peter subsequently installed and booted `7.0.0-31-generic`, confirmed it as the future production kernel baseline, and named the exact disposable P5.0 target. The evidence harness remains unexecuted and Package 5.0 remains `not ready`; P5.0-R5 remains open pending executed evidence and independent review.

---

## 1. Authoritative Current-State Summary (Round 4, 2026-09-05)

This section provides the single authoritative, verified current state of the disposable test server (`oracle-test` / `138.2.182.39`) as of Round 4. Any descriptions in subsequent historical sections (Sections 4 and 5) that conflict with this section are superseded.

### 1.1 Host Infrastructure & Operating System
- **Host Alias:** `oracle-test`
- **IPv4 Address:** `138.2.182.39`
- **Operating System:** Ubuntu 26.04 LTS (x86_64)
- **Kernel:** `7.0.0-31-generic` (installed and booted by Peter Duscha after Round 4).
- **Kernel Baseline Status:** Peter confirmed Ubuntu 26.04 with the 7.x generic kernel as the future production baseline on 2026-09-05. Codex independently verified the active kernel and host prerequisites. The former Oracle-kernel divergence is resolved for target assignment.
- **Hardware Resources:** 1 vCPU, 951 MiB RAM, 0 MiB Swap (heavy test suites must be executed serially).
- **Filesystem Root:** `/dev/sda1` mounted on `/`, type `ext4`, 44 GiB total, ~40 GiB available. Outside `/run`, `/tmp`, `/dev/shm`.
- **Administrative Access:** SSH key access as `ubuntu`; passwordless `sudo` permitted exclusively on `oracle-test`. Zero authority or access over production or staging.

### 1.2 PostgreSQL 16 Authoritative Cluster
- **Cluster Identifier:** `16/main`
- **Package Version:** `postgresql-16` version `16.15-1.pgdg26.04+2` (from official PGDG repository `resolute-pgdg`)
- **Port:** `5432`
- **Socket Directory:** `/var/run/postgresql`
- **Data Directory:** `/var/lib/postgresql/16/main`
- **Configuration Directory:** `/etc/postgresql/16/main`
- **Service State:** `postgresql@16-main.service` active (running), enabled in systemd.
- **Connection String:** `postgresql+psycopg:///freedom_test` (or via Unix domain socket `/var/run/postgresql`).

### 1.3 PostgreSQL 18 Inactive & Disabled Cluster
- **Cluster Identifier:** `18/main`
- **Port:** `5433` (reconfigured to prevent port collision with port 5432)
- **Startup Configuration:** `/etc/postgresql/18/main/start.conf` explicitly set to `manual` (will not auto-start on boot or `systemctl start postgresql`).
- **Service State:** `postgresql@18-main.service` inactive (dead), disabled in systemd.
- **Cluster Status (`pg_lsclusters`):** `18/main down 5433 /var/lib/postgresql/18/main /var/log/postgresql/postgresql-18-main.log`.

### 1.4 Client Toolchain & PATH Discipline
- **Toolchain Location:** Native PGDG PostgreSQL 16 binaries located in `/usr/lib/postgresql/16/bin/`.
- **No Global Symlinks in `/usr/local/bin`:** Zero PostgreSQL client symlinks (`psql`, `pg_dump`, `pg_restore`, `createdb`, `dropdb`) exist in `/usr/local/bin`. Only `uv` is present in `/usr/local/bin`.
- **PATH Policy:** All scripts, services, interactive shells, and test commands must explicitly define `PATH="/usr/lib/postgresql/16/bin:/usr/bin:/bin"`.

### 1.5 Database Templates & Default Privileges
- **Template Public Schemas:** Pristine package defaults restored via fresh cluster initialization.
  - `template0.public`: Owner `pg_database_owner`, privileges `{pg_database_owner=UC/pg_database_owner,=U/pg_database_owner}`.
  - `template1.public`: Owner `pg_database_owner`, privileges `{pg_database_owner=UC/pg_database_owner,=U/pg_database_owner}`.
  - Fresh probe databases: Inherit pristine ownership `pg_database_owner` and privileges `{pg_database_owner=UC/pg_database_owner,=U/pg_database_owner}`.

### 1.6 Roles and Database Authorization
- **Superuser:** `ubuntu` (`SUPERUSER LOGIN`).
- **Restricted Test Role:** `freedom_runtime_test` provisioned exclusively on PostgreSQL 16 with exact restricted attributes:
  `NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`.
- **Role Membership:** `ubuntu` is a member of `freedom_runtime_test`, allowing clean execution of `SET ROLE freedom_runtime_test;` in live grant and boundary tests.
- **Databases:**
  - `freedom_test`: Authoritative primary test lane (owned by `ubuntu`, migrations applied, schema public owned by `pg_database_owner`, runtime grants applied).
  - `freedom_dev`: Development lane (owned by `ubuntu`).
  - `postgres`, `template0`, `template1`: System databases.

### 1.7 Package 5.0 Target Facts & Non-Execution Proof
- **Target Facts Status:** Assigned by Peter Duscha on 2026-09-05: `oracle-test`, `/var/lib/fb-evidence-p5-0`, PostgreSQL `16/main`, `/etc/postgresql/16/main`, `/var/run/postgresql`, and `fb_evidence_p5_0`.
- **Evidence Harness Execution:** Strictly unexecuted. `tools/phase_5_0_evidence/run_evidence_harness.py` was **not** run.
- **Evidence Objects Absence:**
  - Zero databases matching `fb_evidence_%`.
  - Zero database roles matching `freedomcoord`, `freedomsheet`, `fbprobe`, or `freedomjournal`.
  - Directory `/var/lib/fb-evidence*` does not exist.
  - Zero systemd units matching `fb-evidence*`.
- **Package 5.0 Status:** Package 5.0 remains `not ready` and finding `P5.0-R5` remains open pending the authorized evidence run and independent review.

### 1.8 Repository Worktree Synchronization & Hygiene
- **Worktree Synchronization:** Remote `/opt/freedom-blades/platform` intentionally mirrors the complete local dirty worktree (including authorized live-bot defect fix `models/skills.py` and `tests/test_skills.py`).
- **Safe Rsync Include/Exclude Contract:** `--include='.env.example'` strictly precedes `--exclude='.env*'`. Excludes all credential/key/cache patterns: `'*.pem'`, `'*.key'`, `'yt-cookies.txt'`, `'*service_account*.json'`, `'*credentials*.json'`, `'__pycache__/'`, `'*.py[cod]'`, `'.pytest_cache/'`.
- **Checksum Verification:** Local and remote `.env.example` SHA256 matches byte-for-byte:
  `67e2c7a91176b6d85eb56e87f8646b5a3eb64f514d7c67297e6be9596fa9e14e`.
- **Remote Secret Scan:** Metadata-only scan confirmed 0 files matching forbidden patterns.
- **Whitespace & Git Hygiene:** `git diff --check` passes with zero errors locally and remotely on `oracle-test`.

---

## 2. Round 3 Conceded Findings and Remediation (DS-R3-1 and DS-R3-2)

Gemini formally concedes both findings identified in the Round 3 review:

### Finding DS-R3-1 (Important) — Incomplete Recovery Procedure and Artifact Integrity
- **Concession:** The backup-restore drill script (`infra/postgresql/backup-restore-drill.sh`) and database operations documentation (`docs/operations/database-development.md`) omitted SHA256 checksum verification for `schema-grants.sql`, omitted applying `schema-grants.sql` in the manual recovery instructions, failed to mandate retention of `schema-grants.sql`, and did not explain the risks of omitting schema grants upon failure recovery.
- **Correction:**
  1. Updated `infra/postgresql/backup-restore-drill.sh`:
     - Step 3c now creates and validates `schema-grants.sql.sha256`: `sha256sum "${SCHEMA_GRANTS}" | tee "${SCHEMA_GRANTS}.sha256"`.
     - Updated `on_exit()` failure trap to output explicit recovery commands verifying checksums of **both** `${DUMP}.sha256` and `${SCHEMA_GRANTS}.sha256` with `sha256sum --check`.
     - Mandated applying `schema-grants.sql` via `psql -v ON_ERROR_STOP=1 -f "${SCHEMA_GRANTS}"`.
     - Explicitly documented the operational risk in the emitted failure instructions: omitting schema-grants restoration risks leaving the restored schema owned by the restoring superuser rather than `pg_database_owner` and missing package-default permissions.
  2. Updated `docs/operations/database-development.md`:
     - Explicitly mandates retaining both `${DUMP}` and `schema-grants.sql` (along with their `.sha256` checksum files).
     - Aligned recovery procedure with `backup-restore-drill.sh`: verify both checksums, execute `pg_restore` with `--no-owner --no-privileges --single-transaction --exit-on-error`, and apply `schema-grants.sql` with `psql -v ON_ERROR_STOP=1`.
     - Documented why `schema-grants.sql` is strictly required: standard `pg_restore` does not restore schema-level ownership or ACL, which would leave schema `public` owned by `postgres` rather than `pg_database_owner`.
  3. Added Regression Tests in `tests/test_database_backup_restore.py`:
     - Updated `test_the_drill_preserves_pristine_schema_ownership_and_privileges` to assert creation and integrity of `schema-grants.sql.sha256`.
     - Added `test_recovery_instructions_match_database_development_documentation` to assert exact alignment between `database-development.md` and `backup-restore-drill.sh`.
     - Added `test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure` which simulates drill failure after schema drop, checks `RECOVERY REQUIRED` emitted instructions, verifies both checksums, and executes manual recovery cleanly.

### Finding DS-R3-2 (Important) — Internally Contradictory Handback
- **Concession:** The previous handback document placed superseded Round 1 text at the top of the file, containing obsolete claims (e.g. symlinks in `/usr/local/bin`, kernel `6.8.0-1011-oracle`, old pass totals), contradicting the Round 2 section and creating confusion for reviewers.
- **Correction:**
  1. Restructured `phase-5-0-gemini-disposable-server-remediation-handback.md`. Section 1 now contains the authoritative Current-State Summary with all exact facts.
  2. Clearly demarcated all historical Round 1 and Round 2 sections (Sections 4 and 5) as **Historical / Superseded Context**, explicitly warning readers that specific implementation details from earlier rounds (such as `/usr/local/bin` symlinks or initial kernel readings) have been replaced by the Round 3/4 Current-State Summary.
  3. Documented exact test suite totals and determinism in Section 3.

---

## 3. Current Test Execution Evidence (Round 3 Baseline)

All suites executed serially on `oracle-test` against PostgreSQL 16 Unix domain socket `postgresql+psycopg:///freedom_test`:

### 3.1 Focused Test Suite & Backup/Restore Regressions (Two Deterministic Runs)
Command:
```bash
unset DATABASE_URL
export TEST_DATABASE_URL="postgresql+psycopg:///freedom_test"
/opt/freedom-blades/runtime/venv-web/bin/pytest -v -rs \
  tests/test_database_backup_restore.py \
  tests/test_runtime_grants_live.py \
  tests/web/test_p3_2_runtime_grants_and_bounds.py \
  tests/test_filesystem_layout.py
```
- **Run 1 Result:** **130 passed, 0 skipped, 14 warnings in 23.86s**
- **Run 2 Result:** **130 passed, 0 skipped, 14 warnings in 23.98s**
- **Determinism Proof:** Exactly 130 passed (128 baseline + 2 new DS-R3-1 regression tests), 0 skipped, 0 failed across consecutive runs.

### 3.2 Full Regression Suite Totals (Preserved from Serial Verification)
- **Bot Test Suite (`tests/test_*.py`):** **3125 passed, 0 skipped, 0 failed** in 677.00s (0:11:17).
- **Web Test Suite (`tests/web`):** **2840 passed, 80 skipped, 0 failed** in 546.28s (0:09:06).
  - Skips breakdown: Exactly 80 skips matching accepted matrix design (`test_p3_2_matrix.py`: 54; `test_p3_3_matrix.py`: 26).
- **Foundry Test Suite (`foundry-module/tests/`):** **171 passed, 0 failed, 0 skipped** in 3.68s.
- **Python Bytecode Compilation:** `compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` passes cleanly (0 syntax/compilation errors).
- **Whitespace and Git Hygiene:** `git diff --check` passes cleanly (exit code 0) locally and remotely on `oracle-test`.

---

## 4. Historical Context: Round 2 Remediation (2026-09-05) [SUPERSEDED]

*Note: This section records the historical state and findings from Remediation Round 2. Where any detail differs from Section 1 (such as test counts or intermediate drill implementations), Section 1 governs.*

### 4.1 Findings Conceded and Corrected (DS-R2-1 through DS-R2-6)

#### Finding DS-R2-1 (Critical) — Backup/Restore Drill Privileges Flawed & Host Template Privileges Polluted
- **Concession:** The backup-restore drill script (`infra/postgresql/backup-restore-drill.sh`) erroneously mapped integer grantee `0` to literal role name `'0'` (which does not exist) rather than standard `'PUBLIC'`, causing false-positive verification errors on clean clusters. In R1, rather than fixing the drill script bug, Gemini dropped and recreated the public schema in `template1`, which corrupted PostgreSQL 16 default privileges (changing schema ownership from `pg_database_owner` to `postgres` and stripping standard default UC/U ACLs). Furthermore, `pg_restore --clean` does not restore schema-level ownership or ACL, leaving the target database schema owned by `postgres` rather than `pg_database_owner` after a drill.
- **Correction:**
  1. Rebuilt PostgreSQL 16 cluster `16/main` from scratch using `pg_dropcluster 16 main --stop` and `pg_createcluster 16 main --start` to restore pristine package defaults on all templates.
  2. Verified `template0.public`, `template1.public`, and probe databases possess package-default ownership (`pg_database_owner`) and package-default privileges (`{pg_database_owner=UC/pg_database_owner,=U/pg_database_owner}`).
  3. Fixed `grant_inventory()` in `infra/postgresql/backup-restore-drill.sh` to correctly map grantee `0` to stable principal `'PUBLIC'`.
  4. Added `schema_grants_sql()` to `infra/postgresql/backup-restore-drill.sh` to snapshot pre-drill schema ownership and explicit ACL, re-applying them in Step 5b and documenting them in recovery instructions.
  5. Added positive (`test_the_drill_preserves_pristine_schema_ownership_and_privileges`) and negative (`test_the_drill_fails_when_schema_privileges_are_not_restored`) regression tests in `tests/test_database_backup_restore.py`.

#### Finding DS-R2-2 (Important) — Documentation Contradictions and Divergent Instructions
- **Concession:** `.agents/AGENTS.md` and `CLAUDE.md` duplicated rsync instructions and contained obsolete claims that PostgreSQL 18 was operational or coexisting, contradicting `docs/operations/disposable-test-server.md`.
- **Correction:**
  1. Removed duplicated rsync commands and PostgreSQL 18 claims from `.agents/AGENTS.md` and `CLAUDE.md`, establishing `docs/operations/disposable-test-server.md` as the single canonical source of truth for disposable host operations.
  2. Documented in `docs/operations/disposable-test-server.md` that PostgreSQL 18 is persistently disabled (`start.conf` = `manual`, systemd unit disabled), and that callers must use explicit `PATH='/usr/lib/postgresql/16/bin:/usr/bin:/bin'`.
  3. Added documentation regression tests in `tests/test_filesystem_layout.py` ensuring entry points reference `docs/operations/disposable-test-server.md`, do not contain independent rsync recipes, and do not claim PostgreSQL 18 is authoritative.

#### Finding DS-R2-3 (Important) — PostgreSQL 18 Not Persistently Disabled
- **Concession:** In R1, `postgresql@18-main` was stopped and disabled, but `/etc/postgresql/18/main/start.conf` remained set to `auto`. Upon reboot or `systemctl start postgresql`, PostgreSQL 18 would start automatically.
- **Correction:**
  1. Configured `/etc/postgresql/18/main/start.conf` to `manual`.
  2. Executed `systemctl daemon-reload`. Verified `systemctl is-enabled postgresql@18-main` reports `disabled`.
  3. Confirmed cluster status with `pg_lsclusters`: cluster 16 is `online` on port 5432, cluster 18 is `down` on port 5433.

#### Finding DS-R2-4 (Important) — Kernel Divergence Not Documented
- **Concession:** Gemini observed `uname -r` reporting `7.0.0-1009-oracle` on `oracle-test` while production / local environments run `6.8.0-138-generic`, but failed to analyze the divergence, check `/boot` for 6.8 kernels, or document it as a potential blocker.
- **Correction & Status:**
  - Inspected `/boot`: only Oracle Cloud kernel `7.0.0-1009-oracle` is installed. No 6.8 kernels exist on the VM.
  - Formally recorded this kernel divergence as an explicit operational risk/blocker in Section 1.1, requiring maintainer (Peter) / reviewer (Codex) direction before P5.0 execution.

#### Finding DS-R2-5 (Important) — Client Tool Symlinks Incomplete and Fragile
- **Concession:** Placing symlinks in `/usr/local/bin` is fragile, non-standard across environments, and risks version skew when tools or cron jobs run with different `PATH` environments.
- **Correction:**
  1. Removed all PostgreSQL client symlinks from `/usr/local/bin` (`psql`, `pg_dump`, `pg_restore`, `createdb`, `dropdb`). Only `uv` remains in `/usr/local/bin`.
  2. Documented the standard, robust pattern: all scripts, services, and shell commands must explicitly set `PATH="/usr/lib/postgresql/16/bin:/usr/bin:/bin"`.

#### Finding DS-R2-6 (Important) — Test Runs Incomplete and Failed to Report Skips
- **Concession:** R1 reported "121 passed, 2 skipped" without itemizing the skip reasons, and failed to run a clean re-execution proving determinism from a clean database state.
- **Correction:**
  1. Performed two consecutive, deterministic test runs of the focused test suite from a freshly rebuilt database state (`dropdb freedom_test`, `createdb freedom_test`, `alembic upgrade head`, runtime grants applied, `unset DATABASE_URL`, `TEST_DATABASE_URL` set).
  2. Run 1: 128 passed, 0 skipped, 14 warnings in 22.21s. Run 2: 128 passed, 0 skipped, 14 warnings in 23.46s (later expanded to 130 passed in R3).
  3. Executed full test suites serially: Bot suite (3125 passed, 0 failed), Web suite (2840 passed, 80 skipped, 0 failed), Foundry suite (171 passed, 0 failed), byte-compilation (0 errors), and git hygiene (0 errors).

---

## 5. Historical Context: Round 1 Remediation (2026-09-05) [SUPERSEDED]

*Note: This section records the initial Round 1 remediation claims. Multiple implementation decisions in this section (notably symlinks in `/usr/local/bin`, template public schema reset, and pass counts) were superseded by Round 2 and Round 3.*

### 5.1 Findings Conceded in Round 1 (DS-R1 through DS-R5)

#### Finding DS-R1 (Critical) — Unsupported PostgreSQL 18 and Missing Authoritative Test Cluster
- **Concession:** The disposable test server was provisioned with PostgreSQL 18 without an isolated, authoritative PostgreSQL 16 cluster. Production and package specifications explicitly target PostgreSQL 16. Furthermore, PostgreSQL 18's client toolchain generated dump parameters (`SET transaction_timeout = 0;`) that are rejected by PostgreSQL 16 during backup/restore drills.
- **Initial Action (Superseded):** Configured PGDG repository, installed `postgresql-16`, created cluster `16/main` on 5432, stopped `postgresql@18-main` on 5433, and initially symlinked binaries into `/usr/local/bin` (symlinks subsequently removed in Round 2).

#### Finding DS-R2 (Critical) — Missing Restricted Test Role `freedom_runtime_test`
- **Concession:** The restricted runtime role `freedom_runtime_test` was absent from the remote PostgreSQL cluster, causing live runtime grant tests and bounded permission checks to skip or fail.
- **Action:** Created `freedom_runtime_test` on PostgreSQL 16 with restricted attributes (`NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`), granted membership to `ubuntu`.

#### Finding DS-R3 (Important) — Unsafe and Incomplete Synchronization
- **Concession:** Previous `rsync` used `--exclude='.env*'` which omitted tracked `.env.example`.
- **Action:** Enforced `--include='.env.example'` before `--exclude='.env*'`. Validated checksum match and performed metadata scan.

#### Finding DS-R4 (Important) — P5.0 Target Still Unassigned
- **Concession:** Gemini previously filled in speculative evidence target values without human confirmation.
- **Action:** Maintained `UNASSIGNED` placeholders in `docs/review/phase-5-0-evidence-harness-execution-plan.md`. Did not execute harness or provision evidence objects.

#### Finding DS-R5 (Minor) — Documentation Hygiene and Authority Boundaries
- **Concession:** `CLAUDE.md` contained a trailing blank line failing `git diff --check`.
- **Action:** Fixed trailing blank line. Reasserted administrative boundaries.

---

## 6. Historical Submission (Round 3)

Round 3 remediation of findings **DS-R3-1** and **DS-R3-2** was accepted with two minor documentation findings remediated in Round 4 below.

- **Integrity Verified:** All drill failure recovery paths now verify checksums for both `${DUMP}` and `schema-grants.sql`, mandate executing both restore steps, document risks of omitted schema grants, and are backed by regression tests.
- **Handback Restructured:** Authoritative Current-State Summary is prominently placed in Section 1 with all exact facts. Historical rounds are explicitly marked as superseded.
- **Authority Boundaries Preserved:** Package 5.0 evidence harness remains unexecuted, target facts remain `UNASSIGNED`, no P5 roles/databases exist, host kernel remains untouched with divergence documented as a blocker/risk, and Package 5.0 remains `not ready` with `P5.0-R5` `Blocking`.

---

## 7. Round 4 Documentation Remediation (2026-09-05)

Gemini has completed the narrow documentation remediation requested in Codex's Round 3 review:

### 7.1 Finding DS-R4-1 (Minor) — Incorrect `pg_restore` Options in Handback
- **Correction:** The Round 3 handback erroneously reported that `docs/operations/database-development.md` uses `pg_restore --clean --if-exists`. That statement was false; the actual implemented command in `infra/postgresql/backup-restore-drill.sh` and documented in `docs/operations/database-development.md` is:
  ```bash
  pg_restore --dbname=freedom_dev --no-owner --no-privileges \
             --single-transaction --exit-on-error /var/tmp/drill/freedom_dev.dump
  ```
- **Action:** Corrected Section 2 (Finding DS-R3-1 summary) to accurately state the `--no-owner --no-privileges --single-transaction --exit-on-error` options. Verified that no other current-state text in this handback claims `--clean` or `--if-exists`. (Historical notes in Section 4.1 regarding past behavior remain explicitly labelled as historical context).

### 7.2 Finding DS-R4-2 (Minor) — "Authenticated" Overstates Adjacent Checksum Guarantees
- **Correction:** Adjacent `.sha256` files verify artifact integrity and detect corruption, but do not provide provenance authentication against an attacker capable of replacing both the artifact and its adjacent checksum file. Describing them as "authenticated" was an overstatement.
- **Action:** Replaced overstatements ("authenticated artifacts", "authenticate both checksums") with precise terminology ("checksummed artifacts", "verify both checksums", "integrity-checked artifacts") across:
  - `docs/operations/database-development.md` (line 340: `Restore from both checksummed artifacts:`)
  - `docs/review/phase-5-0-gemini-disposable-server-remediation-handback.md` (Sections 2 and 6)
  - `tests/test_database_backup_restore.py` (updated test name `test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure` and comments)
  - `docs/review/Handover information`
- **Boundary:** Preserved checksum generation and verification exactly as implemented. Did not introduce signing, keys, or new credentials.

### 7.3 Exact Files Changed
1. `docs/operations/database-development.md`: Replaced "authenticated artifacts" with "checksummed artifacts".
2. `tests/test_database_backup_restore.py`: Updated test name and comments from "authenticated" to checksum verification / integrity terminology.
3. `docs/review/phase-5-0-gemini-disposable-server-remediation-handback.md`: Corrected `pg_restore` options, replaced "authenticated" overstatements, added Section 7.
4. `docs/review/Handover information`: Updated header and summary for Round 4.

### 7.4 Validation and Invariant Confirmations
1. **Git Whitespace & Formatting Hygiene:** `git diff --check` passes cleanly (exit code 0).
2. **Focused Test Suite on `oracle-test`:** Executed twice consecutively against PostgreSQL 16:
   - Command:
     ```bash
     cd /opt/freedom-blades/platform
     unset DATABASE_URL
     PATH="/usr/lib/postgresql/16/bin:/usr/bin:/bin" \
     TEST_DATABASE_URL="postgresql+psycopg:///freedom_test" \
     /opt/freedom-blades/runtime/venv-web/bin/pytest -q -rs \
       tests/test_database_backup_restore.py \
       tests/test_runtime_grants_live.py \
       tests/web/test_p3_2_runtime_grants_and_bounds.py \
       tests/test_filesystem_layout.py
     ```
   - Run 1 Result: **130 passed, 14 warnings in 23.17s**.
   - Run 2 Result: **130 passed, 14 warnings in 23.21s** (100% deterministic).
3. **Read-Only Server Invariants (`oracle-test`):**
   - `uname -r` remains `7.0.0-1009-oracle`.
   - PostgreSQL `16/main` remains online on port 5432.
   - PostgreSQL `18/main` remains down on port 5433 with `/etc/postgresql/18/main/start.conf = manual`.
   - `/usr/local/bin` contains only `uv` (zero PostgreSQL client symlinks).
   - Zero P5.0 evidence databases, roles, directories, or systemd units exist.
4. **Metadata Secret Scan:** Confirmed 0 forbidden secret/credential files.
5. **Governance Confirmations:**
   - Server configuration was **not changed**.
   - Host kernel was **not altered**; kernel divergence remains documented as an unresolved operational blocker/risk.
   - Package 5.0 evidence harness was **not executed**.
   - Target facts remain strictly **`UNASSIGNED`**.
   - Package 5.0 remains **`not ready`** and finding **`P5.0-R5`** remains **`Blocking`**.

---

## 8. Post-Round-4 target assignment and generic-kernel verification

On 2026-09-05 Peter Duscha installed and booted kernel `7.0.0-31-generic`,
confirmed Ubuntu 26.04 with the generic 7.x kernel as the future production
baseline, and named the exact disposable target recorded in the evidence
execution plan. Codex independently verified the active kernel, ext4 append
attributes, required root capability bounding set and tools, PostgreSQL 16/18
states, pristine template ACL, restricted runtime role, absence of P5 evidence
objects and absence of secret-shaped files. The static harness suite passed
398 tests, and the recovery/privilege suite passed twice with 130 passed,
0 skipped and 14 warnings per run.

This resolves the former kernel-flavor and target-assignment blockers. It does
not execute the harness or close P5.0-R5. Concrete argument-vector generation,
independent review, privileged execution, cleanup and evidence review remain.
