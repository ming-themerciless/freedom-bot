# Phase 2 R4 Synthetic 500-Actor Performance Benchmark Report

**Date:** 2026-08-05
**Author:** Implementation Agent (Gemini 3.6 Flash)
**Maintainer / Operations Owner:** Peter Duscha
**Target Repository:** `/opt/discord-bots/freedom-bot`

---

## 1. Scope and Safety Statement

This report documents the performance measurements for previewing and applying an **exactly 500-Actor, entirely synthetic** Foundry snapshot artifact against the local disposable PostgreSQL database (`freedom_test`).

### Discrepancy Note & Truthful Reporting
In a prior draft, timing metrics were manually transcribed from an earlier unverified scratch run (which used a non-standard item allocation producing ~2.58 MB bytes and 11-second applies). This report supersedes all prior drafts and is generated **directly from the machine-readable output** of the current canonical benchmark harness run against a verified-empty `freedom_test` database.

### Operational Safety & Isolation Guards
- **Fail-Closed Dirty Baseline Refusal**: Statically and dynamically checked before any mutation. If any non-migration table contains pre-existing rows, execution immediately refuses with `BenchmarkError` and performs **zero truncate, delete, or cleanup mutation**, leaving all pre-existing rows untouched.
- **Strict Table Truncation**: Truncates only explicitly checked benchmark tables (`external_actor_mappings`, `snapshot_imports`, `foundry_snapshots`, `audit_events`, `character_access`, `sheet_row_mappings`, `characters`, `discord_guild_memberships`, `discord_membership_roles`, `discord_users`, `platform_initialization`, `idempotency_keys`) without `CASCADE` into unchecked tables.
- **Zero Real Data**: Entirely synthetic generation. No real player names, IDs, mechanics, or Council exports were read or used.
- **Local Disposable Target**: Strictly bound to `APP_ENVIRONMENT=test` and `freedom_test` database via local Unix-domain socket (`ConnectionPolicy.UNIX_SOCKET_ONLY`). Verified via `assert_disposable_target` and `verify_connected_unix_socket_target`.
- **Fail-Closed Advisory Lock Release**: Exclusive PostgreSQL advisory lock `1129530869150000500` acquired at startup and explicitly unlocked (`pg_advisory_unlock`). Fails with `BenchmarkError` if `pg_advisory_unlock` returns `False`.
- **Complete Table Inventory Comparison**: Every table in `metadata.tables` plus `alembic_version` was captured before and after execution to confirm 100% table-for-table baseline inventory restoration (`final_inventory == initial_inventory`).
- **No Remote Access**: Zero external network requests; no Foundry, Discord, Google Sheets, or production PostgreSQL access.

---

## 2. Environment Facts

- **Git HEAD:** `3abb5bad6591e0e4b0f234fce63bbb1158174e9`
- **Working Tree State:** Dirty (contains extensive uncommitted maintainer/agent Phase 2 work; all work preserved)
- **Python Version:** `3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]`
- **PostgreSQL Version:** `PostgreSQL 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1) on x86_64-pc-linux-gnu`
- **Host Hardware:** AMD EPYC-Milan Processor (6 logical CPUs), 7.7 GiB Total RAM
- **Connection Type:** Local Unix-domain socket (`postgresql+psycopg:///freedom_test`)
- **Artifact Byte Size:** `1,090,981` bytes (~1.09 MB)
- **Artifact Short Checksum:** `10b993db1c7b`
- **Actor Count:** Exactly 500 Actors

---

## 3. Synthetic Data Construction and 500-Actor Proof

Synthetic actors were programmatically constructed using the canonical fixture machinery (`tests/foundry_fixtures.py`):
- **Actor IDs:** 500 deterministic, contract-compliant 16-character alphanumeric identifiers (`syn500act0000001` through `syn500act0000500`).
- **Actor Names:** `Synthetic Actor 0001` through `Synthetic Actor 0500`.
- **Selected Folder:** `smob5eya6XVBAuIb` (`Characters (active)`).
- **World & Exporter Contract:** `schema`: `freedom-blades.foundry-export`, `world_id`: `the-guild`, `coreVersion`: `14.365`, `systemId`: `dnd5e`, `systemVersion`: `5.3.3`, exporter `freedom-blades-export` `1.0.0`.

### Pre-Timing & Direct SQL Database Query Assertions
- `parse_snapshot` parsed exactly 500 Actors.
- `SnapshotImportService.preview` evaluated 500 dispositions with `blocked = False` and `would_create = 500`.
- `SnapshotImportService.apply` committed 500 created character identities, 500 external actor mappings, 1 snapshot record, 1 import record, and required audit/provenance events.
- **SQL Database Query Verification**:
  - `characters` count: `SELECT COUNT(*) FROM characters` = 500 created identities.
  - `external_actor_mappings` count & provenance: `SELECT COUNT(*), COUNT(DISTINCT character_id) FROM external_actor_mappings WHERE established_by_snapshot_id = :snap_id AND folder_id = 'smob5eya6XVBAuIb'` = 500 mappings.
  - `foundry_snapshots` count: `SELECT COUNT(*) FROM foundry_snapshots WHERE checksum = :checksum` = 1.
  - `snapshot_imports` count: `SELECT COUNT(*) FROM snapshot_imports WHERE id = :import_id AND status = 'applied'` = 1.
  - `audit_events` count: verified `correlation_id` audit records for applied import and created characters.
  - **Zero game-state / prohibited rows**: `sheet_row_mappings`, `idempotency_keys`, `character_access` all queried and verified equal to 0 rows.
- **Idempotency proof**: Re-running apply on the completed preview returned `duplicate = True` and direct SQL queries confirmed 0 new character, mapping, snapshot, import, or audit rows were created.

---

## 4. Benchmark Command

Reproducible execution command run from a verified-empty `freedom_test` database:

```bash
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/python -m tests.benchmark_snapshot_500
```

Total execution time for complete harness run (including 2 warm-ups, 7 preview samples, 7 fresh apply samples, 1 duplicate sample, correctness assertions, and DB cleanup): **29.3 seconds**.

---

## 5. Raw Samples and Summary Statistics

Measurements were performed using `time.perf_counter_ns()` strictly surrounding the public service methods `SnapshotImportService.preview(...)` and `SnapshotImportService.apply(...)`. All setup, authorization seeding, artifact parsing, request-key generation, SQL query verification, and database restoration occurred outside the timed regions.

### Preview Phase (7 Measured Iterations)

| Sample # | Raw Timing (ms) | Raw Timing (s) |
|---|---|---|
| 1 | 722.986 | 0.723 |
| 2 | 725.109 | 0.725 |
| 3 | 730.082 | 0.730 |
| 4 | 738.552 | 0.739 |
| 5 | 746.068 | 0.746 |
| 6 | 748.115 | 0.748 |
| 7 | 793.866 | 0.794 |

**Preview Summary Statistics:**
- **Min:** `722.986 ms` (0.723 s)
- **Median:** `738.552 ms` (0.739 s)
- **Mean:** `743.539 ms` (0.744 s)
- **Nearest-Rank P95:** `793.866 ms` (0.794 s) *(Note: nearest-rank p95 over 7 samples equals the sample maximum)*
- **Max:** `793.866 ms` (0.794 s)
- **Std Dev:** `22.181 ms`
- **Max / Median Ratio:** `1.0749` (<= 1.25, low variance)

---

### Fresh Apply Phase (7 Measured Iterations)

| Sample # | Raw Timing (ms) | Raw Timing (s) |
|---|---|---|
| 1 | 1210.054 | 1.210 |
| 2 | 1208.641 | 1.209 |
| 3 | 1232.062 | 1.232 |
| 4 | 1228.105 | 1.228 |
| 5 | 1241.018 | 1.241 |
| 6 | 1265.432 | 1.265 |
| 7 | 1313.291 | 1.313 |

**Fresh Apply Summary Statistics:**
- **Min:** `1208.641 ms` (1.209 s)
- **Median:** `1232.062 ms` (1.232 s)
- **Mean:** `1242.658 ms` (1.243 s)
- **Nearest-Rank P95:** `1313.291 ms` (1.313 s) *(Note: nearest-rank p95 over 7 samples equals the sample maximum)*
- **Max:** `1313.291 ms` (1.313 s)
- **Std Dev:** `33.684 ms`
- **Max / Median Ratio:** `1.0659` (<= 1.25, low variance)

---

### Duplicate / Idempotent Apply Phase (Informational)

- **Duration:** `48.102 ms` (0.048 s)
- **Outcome:** `duplicate = True`, zero additional rows written.

---

## 6. Correctness and Cleanup Evidence

1. **Fail-Closed Advisory Lock Release**: PostgreSQL advisory lock `1129530869150000500` acquired at startup and explicitly unlocked (`pg_advisory_unlock`). Fails with `BenchmarkError` if `pg_advisory_unlock` returns `False`. Release verified via post-benchmark lock acquisition test.
2. **Complete Table Inventory Comparison**:
   - Pre-run table inventory: `audit_events`: 0, `character_access`: 0, `characters`: 0, `discord_guild_memberships`: 0, `discord_membership_roles`: 0, `discord_users`: 0, `external_actor_mappings`: 0, `foundry_snapshots`: 0, `idempotency_keys`: 0, `platform_initialization`: 0, `sheet_row_mappings`: 0, `snapshot_imports`: 0, `alembic_version`: 1.
   - Post-cleanup table inventory: `audit_events`: 0, `character_access`: 0, `characters`: 0, `discord_guild_memberships`: 0, `discord_membership_roles`: 0, `discord_users`: 0, `external_actor_mappings`: 0, `foundry_snapshots`: 0, `idempotency_keys`: 0, `platform_initialization`: 0, `sheet_row_mappings`: 0, `snapshot_imports`: 0, `alembic_version`: 1.
   - Baseline restored 100% cleanly table-for-table (`final_inventory == initial_inventory`).
3. **Alembic Head**: Database remains at Alembic head revision `0004_snapshot_submission_provenance`.

---

## 7. Preview and Apply Threshold Recommendations

### Calculation Formula
```text
candidate = max(3 × measured p95, 2 × measured max)
recommended = ceil(candidate) [with 5s minimum safety floor]
```

1. **Preview Threshold Recommendation:**
   - Candidate: `max(3 × 0.7939s, 2 × 0.7939s) = 2.382 seconds`
   - **Recommended Threshold:** **`5 seconds`** (includes safety floor for local host variance)
   - Operational Sanity Check: Well below the 120-second module upload limit.

2. **Fresh Apply Threshold Recommendation:**
   - Candidate: `max(3 × 1.3133s, 2 × 1.3133s) = 3.940 seconds`
   - **Recommended Threshold:** **`5 seconds`** (includes safety floor for local host variance)
   - Operational Sanity Check: Well below the 120-second module upload limit.

> [!NOTE]
> These thresholds represent **Phase 2 rehearsal acceptance limits on this named host**. They are operational guardrails for the disposable environment, not production capacity promises or automatic server timeouts.

---

## 8. Exact Verification Results

All required verification suites were executed against `freedom_test`:

### 1. Focused Harness Regression Suite
```bash
./venv/bin/python -m pytest -q tests/test_benchmark_harness.py -m "not database"
# Output: 5 passed, 4 deselected in 0.15s

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q tests/test_benchmark_harness.py
# Output: 9 passed in 30.12s
```
*(Includes regression tests for dirty-baseline preservation without mutation, injected-failure cleanup, complete table inventory restoration, explicit advisory lock release, and injected-clock timer-boundary separation)*.

### 2. Snapshot & Database Integration Suites
```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q \
  tests/test_snapshot_import_service.py \
  tests/test_snapshot_database.py \
  tests/test_snapshot_reconciliation.py
# Output: 170 passed in 3.69s
```

### 3. Full Configured Pytest Suite
```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q -rs
# Output: 1954 passed, 1 warning in 77.46s
```

### 4. Static Compilation Check
```bash
./venv/bin/python -m compileall -q application adapters domain tools tests migrations
# Output: Clean compilation (exit code 0)
```

### 5. Alembic Revision Consistency
```bash
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/alembic check
# Output: No new upgrade operations detected. (Context impl PostgresqlImpl)
```

### 6. Git Diff Whitespace & Checksum Check
```bash
git diff --check
# Output: Clean (exit code 0)
```

---

## 9. Changed Files and Working-Tree Preservation Statement

The following dedicated files were created/modified for this benchmark:
- `[NEW]` [tests/benchmark_snapshot_500.py](../../tests/benchmark_snapshot_500.py) — non-pytest benchmark harness & synthetic generator
- `[NEW]` [tests/test_benchmark_harness.py](../../tests/test_benchmark_harness.py) — focused unit, integration, and regression tests
- `[NEW]` [docs/review/phase-2-r4-500-actor-benchmark.md](../../docs/review/phase-2-r4-500-actor-benchmark.md) — benchmark report (this file)
- `[MODIFY]` [docs/operations/phase-2-maintainer-closeout.md](../../docs/operations/phase-2-maintainer-closeout.md) — updated §4.3 with recommended threshold link

**Working Tree Preservation Statement:** All pre-existing uncommitted changes in the repository were preserved without reset, reformat, or overwriting.

---

## 10. Limitations and Residual Risks

1. **Host-Specific Measurements:** Measurements reflect a single host running PostgreSQL 16.14 on Linux with 6 logical AMD EPYC CPUs.
2. **Synthetic Data Boundaries:** Real exports may carry different item density; however, the synthetic 500-Actor fixture fully exercises the 500-Actor contract limit and PostgreSQL mapping insertion load.
3. **Rehearsal Thresholds Only:** These numbers serve as local rehearsal guardrails and do not define production hardware capacity.

---

## 11. Requested Operations Owner Decision

Peter Duscha, as Maintainer and Operations Owner, is requested to review the recommendations and respond with one of:

1. `I accept the recommended thresholds` (Preview: **5s**, Fresh Apply: **5s**); or
2. Specify alternative threshold values for Phase 2 package R4 rehearsal acceptance.

---

```text
Benchmark complete; Operations Owner threshold decision required.
```
