---
name: run-suites
description: Run the Freedom Blades test suites correctly and report the result honestly. Use whenever asked to run tests, verify a change, confirm something works, or cite suite figures. Carries the two facts that otherwise produce a green run proving nothing - the TEST_DATABASE_URL export and the skip-count check - plus the serial-execution rule and the canonical interpreter path.
---

# Running the suites

**This skill is a procedural aid, not a source of rules.** The authority is
`.agents/AGENTS.md` "Testing / Running the suites" and
`docs/operations/disposable-test-server.md`. If this file and either of those
disagree, they win and the disagreement is a defect to report, not a choice to
make.

## Before anything: check for a task-specific restriction

`.agents/AGENTS.md` states that the environment instructions **do not override a
task-specific restriction** on SSH, host inspection, database operations or
destructive tests. Package 5.0 evidence work has carried such restrictions
continuously.

1. Read the active handover, `docs/review/Handover information`.
2. Read the restriction banner at the top of
   `docs/operations/disposable-test-server.md`.
3. If either forbids SSH, synchronization or host operations, **do not run the
   remote commands below.** Run only what the restriction permits, and report
   every check not run and why.

## The two facts that make a false green possible

Both are load-bearing. State them in any evidence that cites a figure.

* **The repository and the test environment are different hosts.** Work in
  `/opt/freedom-blades/platform`. The documented interpreter is
  `/opt/freedom-blades/runtime/venv-web/bin/python` **on `oracle-test`**. The
  historical `/opt/discord-bots/` environments are not the default. An
  interpreter path existing on one host says nothing about another.
* **`TEST_DATABASE_URL` must be exported.** Without it every database-marked
  test skips, the web suite finishes in about twelve seconds reporting roughly
  **1362 skipped**, and **it still exits 0**. With it, the correct web skip count
  is **80**. Check the skip count before believing a pass, and use `-rs` so each
  reason prints. The **skip** count is the check; the pass count moves as tests
  are added and is not a target to match.

## Order of execution

Narrow first, then broad. Run the bot and web suites **serially**: they share one
disposable database (finding F-6), so a parallel run is a different verification,
not a faster one.

1. Structural or focused tests for what changed.
2. The changed area's full module.
3. The complete available suites.

## The canonical run, on `oracle-test`

Synchronize first with the secret-excluding procedure in
`docs/operations/disposable-test-server.md` §3.2. Do not use
`--delete-excluded`, and keep `--include='.env.example'` before `--exclude='.env*'`.

```bash
cd /opt/freedom-blades/platform
export PATH='/usr/lib/postgresql/16/bin:/usr/bin:/bin'
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/test_*.py
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
```

## Restricted local pass

When a task forbids SSH, a handover may name fallback interpreters for a local
run. They are an exception for that task only and **must be verified before
use**. Keep `TEST_DATABASE_URL` unset, keep the suites serial, and record that
every database skip is an unverified assertion rather than PostgreSQL evidence.

## Reporting

* Re-run the full set against the tree you are actually submitting. A figure
  carried from an earlier tree describes a state that no longer exists.
* Report the exact command, the interpreter, the counts, and the skip reasons.
* Report every check that could not be run, and why.
* **Do not claim a check passed unless it was actually run.** A passing defect
  reproduction is evidence the defect is open, not a passed invariant.
