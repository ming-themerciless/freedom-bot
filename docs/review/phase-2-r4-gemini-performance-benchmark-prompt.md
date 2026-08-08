# Gemini handoff — Phase 2 R4 synthetic 500-Actor performance benchmark

Copy everything below this line into Gemini as one prompt.

---

You are the implementation agent responsible for one bounded Phase 2 R4 task:
produce reproducible performance evidence for previewing and applying an
**exactly 500-Actor, entirely synthetic** Foundry snapshot against the local
disposable PostgreSQL database.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-05

Maintainer and Operations Owner: Peter Duscha

## 1. Authority and outcome

You are authorized to:

- read the repository and its local instructions;
- create synthetic fixtures containing no real player or Actor data;
- use only the disposable PostgreSQL database `freedom_test` through the local
  Unix socket or loopback;
- add the smallest necessary reproducible benchmark harness and focused tests;
- run the benchmark, relevant tests and read-only environment inspection;
- clean up all benchmark data and temporary artifacts; and
- write a benchmark report and threshold recommendation.

You are **not** authorized to:

- access Foundry, Discord, Google Sheets, production PostgreSQL or any external
  service;
- read `/opt/discord-bots/foundry-actor-exports` or any real export;
- read or modify `.env`, credentials, tokens or player data;
- install a Foundry module;
- apply a real snapshot;
- commit, push or deploy;
- decide the Operations Owner's threshold;
- close a finding or gate; or
- start Phase 3.

The outcome is evidence and a recommendation. Peter accepts or rejects the
threshold afterward.

## 2. Mandatory repository context

Before planning or changing anything, read completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially Phase 2, §13.3 and §16.4
4. `docs/review/phase-2-v1.5-remediation-plan.md`, especially §9.4
5. `docs/operations/phase-2-maintainer-closeout.md`, especially §4.3
6. `docs/operations/foundry-snapshot-import.md`
7. `application/foundry/import_service.py`
8. `application/foundry/parser.py`
9. `application/foundry/reconciliation.py`
10. `tools/bootstrap_manager.py`
11. `tests/foundry_fixtures.py`
12. `tests/snapshot_harness.py`
13. relevant PostgreSQL integration tests in `tests/test_snapshot_database.py`

Check `git status` before working. The working tree contains extensive
uncommitted Phase 2 work belonging to the maintainer and previous agents.
Preserve it exactly. Do not reset, revert, clean, reformat or overwrite
unrelated work.

## 3. What must be measured

Measure the real application path for:

1. **Preview:** artifact validation and parsing, authorization, reconciliation
   and PostgreSQL reads needed to produce the 500-Actor preview.
2. **Apply:** the authorized application of that already-created preview,
   including real PostgreSQL transactions, character identities, external
   mappings, import provenance and audit effects.

Use `SnapshotImportService.preview` and `SnapshotImportService.apply`, or the
same public composition the production/operator path uses. Do not call private
helpers to bypass parsing, authorization, reconciliation, unit-of-work or audit
behavior.

Do not benchmark only the fake repositories. The evidence required by Phase 2
is PostgreSQL behavior.

Do not use `tools.bootstrap_manager --bootstrap` as a repeated timing loop. It
is a one-time supervised initialization path designed to close after success.
Build a disposable Council-authorized benchmark composition using the existing
public services and real PostgreSQL adapter, following the integration tests.

## 4. Synthetic dataset requirements

Generate exactly 500 Actors from code. Every value must be obviously synthetic.
Use stable IDs such as `synthetic-actor-0001`; use names such as
`Synthetic Actor 0001`. Do not copy any real name, ID, mechanic or export.

The artifact must:

- satisfy the real exporter/parser contract;
- use the supported observed deployment tuple and contract schema;
- select one synthetic Actor folder;
- have 500 unique stable Actor IDs;
- exercise the supported Actor structure realistically enough to parse and
  classify the normal field profile;
- remain below all byte, nesting and item-count limits; and
- be encoded using the real canonical fixture/artifact machinery rather than a
  hand-written JSON approximation.

Before timing, assert:

- the parser sees exactly 500 Actors;
- every Actor receives exactly one reconciliation disposition;
- the preview has no blocking error;
- a clean apply creates exactly 500 expected identity/mapping effects and the
  required import/audit records;
- no character game-state, balance or transaction rows are created; and
- a repeated apply is idempotent and creates no second effect.

If the accepted contract makes one of these expectations incorrect, stop and
explain the conflict rather than weakening the contract or silently changing
the expected count.

## 5. Reproducible benchmark harness

There is currently no dedicated 500-Actor benchmark command. Implement the
smallest maintainable harness that makes the evidence reproducible.

Preferred shape:

- a focused command under `tools/` or a clearly named non-pytest performance
  harness under `tests/`;
- explicit refusal unless `APP_ENVIRONMENT=test` and `DATABASE_URL` or
  `TEST_DATABASE_URL` resolves to the disposable `freedom_test` database;
- no implicit database creation, role creation, migration or privilege change;
- no network access;
- deterministic synthetic generation from a fixed seed or no randomness;
- separate preview and apply timers using `time.perf_counter_ns()`;
- machine-readable output such as JSON plus a concise human summary;
- no Actor-by-Actor output, SQL text, database URL or raw artifact bytes;
- cleanup in `finally`, including after a failed run; and
- an explicit post-cleanup verification that no benchmark rows remain.

If a repository change is unnecessary and a temporary `/tmp` runner is safer,
that is acceptable only if the final report includes the full reproducible
command and the generator is small enough to audit. Prefer a committed-style
repository harness when non-trivial composition or cleanup logic would
otherwise exist only in the report.

Add focused tests for any repository harness. At minimum test:

- refusal of a non-test environment or wrong database name;
- deterministic generation of exactly 500 unique Actors;
- output does not contain an Actor payload, credential or database URL;
- cleanup runs after success and injected failure; and
- timing phases are labelled correctly and not combined accidentally.

Do not optimize the application during this task unless a correctness defect or
an extreme performance failure makes measurement impossible. Report such a
finding first. Performance optimization is a separately reviewed change.

## 6. Database preparation and isolation

Use only:

```text
APP_ENVIRONMENT=test
postgresql+psycopg:///freedom_test
```

Before mutation, prove from parsed configuration—not substring matching alone—
that the target database is `freedom_test`, uses the local socket or loopback,
and passes the repository's `ConnectionPolicy`.

Confirm migrations are at head. Do not run migrations automatically unless the
database is already the approved disposable target and the repository procedure
explicitly requires it. Report any mismatch before proceeding.

Before each measured apply, establish a clean, equivalent starting state using
a transactionally safe method consistent with existing test fixtures. Do not
include database cleanup, schema creation, migration, fixture generation,
Python import time or process startup in preview/apply timings.

After every measured iteration, verify counts and clean the disposable rows.
At the end, verify every Phase 2 benchmark table is empty and the database
remains at Alembic head.

## 7. Measurement protocol

Use this minimum protocol unless a documented technical reason requires a
stronger one:

1. Record, without secrets:
   - current Git HEAD and whether the working tree is dirty;
   - Python version;
   - PostgreSQL server version;
   - CPU model and logical CPU count;
   - total memory;
   - whether PostgreSQL uses a Unix socket or loopback;
   - artifact byte size; and
   - exact Actor count.
2. Generate and validate the synthetic artifact once outside timed regions.
3. Run at least **two untimed warm-up iterations**.
4. Run at least **seven measured preview iterations** from equivalent database
   state.
5. Run at least **seven measured apply iterations**, each from a clean equivalent
   state with a fresh deterministic request key/checksum identity as required
   to measure a real apply rather than the duplicate fast path.
6. Time preview and apply separately with `time.perf_counter_ns()`.
7. Run the duplicate/idempotent path separately and label it informational; do
   not mix it into fresh-apply statistics.
8. For preview and fresh apply report every sample plus minimum, median, mean,
   p95 or nearest-rank p95, maximum and population standard deviation.
9. If any sample is an outlier, report it. Do not discard it without a
   predeclared mechanical rule and a second table containing all raw samples.
10. Repeat the complete measured set once if results vary by more than 25%
    between median and maximum, after checking for a test/setup defect.

Do not claim production capacity from this single-host synthetic test. It is a
Phase 2 guardrail for the named disposable environment.

## 8. Threshold recommendation method

Recommend separate wall-clock limits for preview and fresh apply.

The recommendation must:

- be a simple human-readable number in seconds;
- exceed the observed maximum by a documented safety margin;
- account for normal local-host variance without hiding pathological behavior;
- remain below any relevant request/operator timeout;
- explain whether it is a test/rehearsal acceptance threshold, an alert
  threshold or both; and
- state that Peter, as Operations Owner, must accept or replace it.

Use a defensible rule such as rounding up the larger of `3 × measured p95` or
`2 × measured maximum` to a practical boundary, then sanity-check it against
the existing 120-second module upload timeout and documented proxy limits. You
may recommend a different rule, but explain why. Do not manufacture a tiny
threshold merely because the local host is fast.

## 9. Required verification

Run narrow tests for the harness first. Then run the existing relevant snapshot
and database suites with the disposable database configured. Finally run the
full configured suite and static checks required by `.agents/AGENTS.md`.

At minimum report exact commands and results for:

```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q <new focused tests>

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q \
  tests/test_snapshot_import_service.py \
  tests/test_snapshot_database.py \
  tests/test_snapshot_reconciliation.py

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q -rs

./venv/bin/python -m compileall -q application adapters domain tools tests migrations

APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/alembic check

git diff --check
```

Also run the actual benchmark command at least once after its tests pass.

Do not report a test as passed unless you ran it. Report skips and warnings.
No formatter, linter or type checker should be invented if none is configured;
state that limitation accurately.

## 10. Stop conditions

Stop without working around the problem and report to Peter if:

- database safety validation cannot prove `freedom_test`;
- a migration is not at head or cleanup cannot restore the initial state;
- any real-looking data is discovered in the generated artifact or output;
- the 500-Actor artifact violates the accepted contract;
- preview or apply creates prohibited character game-state rows;
- apply is partial, non-idempotent or leaves benchmark rows after cleanup;
- authorization or audit must be bypassed to run the benchmark;
- a result requires changing authority, schema, retention, topology or an
  accepted architectural decision; or
- completing the task would require production access, a credential, external
  network access, privilege escalation, commit or push.

## 11. Deliverables

Produce:

1. the reproducible benchmark harness and its focused tests, if repository code
   was necessary;
2. `docs/review/phase-2-r4-500-actor-benchmark.md` containing:
   - scope and safety statement;
   - environment facts;
   - synthetic-data construction and proof of 500 Actors;
   - exact benchmark command;
   - raw samples and summary statistics;
   - correctness and cleanup evidence;
   - preview and apply threshold recommendations;
   - exact verification results;
   - changed files and working-tree preservation statement;
   - limitations and residual risks; and
   - the exact Operations Owner decision requested from Peter;
3. an update to `docs/operations/phase-2-maintainer-closeout.md` that replaces
   “pending Gemini benchmark” only with a link and the **recommended** values,
   clearly marked not accepted until Peter decides.

Do not update the controlled plan, change log, status, RAID register or gate
decision with accepted thresholds. Peter has not decided them yet.

End your response with exactly one of:

```text
Benchmark complete; Operations Owner threshold decision required.
```

or

```text
Benchmark blocked; no threshold recommendation is supportable.
```

Then give the report path, preview recommendation, apply recommendation, exact
test totals, cleanup result and any blocker in concise bullets.
