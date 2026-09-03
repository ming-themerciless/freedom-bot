# Claude prompt — Phase 4 post-gate constructor-validation remediation

You are Claude, the implementing agent and working Technical Lead for this
bounded post-gate correction to Phase 4. Work in
`/opt/freedom-blades/platform`.

Before planning or changing anything, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. this prompt;
4. `application/commands.py`;
5. the relevant Phase 4 tests, especially `tests/test_p4_commands.py`; and
6. the Phase 4 acceptance record in `docs/review/phase-4-submission.md`.

Check `git status` before editing. The working tree contains substantial
maintainer-owned and agent-owned uncommitted work. Preserve every unrelated
change. Do not reset, revert, reformat or rewrite unrelated files.

## Status and authority

Phase 4 was approved on 2026-08-29. These are two post-gate defects found by
Codex during a later repository review. This prompt authorizes only their narrow
remediation and the evidence needed to review it. It does not reopen the Phase
4 architecture or its accepted ledger, authorization, idempotency, concurrency,
audit or correlation decisions.

Package 5.0 remains `not ready`. This correction does not authorize Package 5.0
implementation, migration `0014`, deployment, cutover, production or host
changes, or any Package 5.1+ work. After this correction is independently
re-reviewed and accepted, work resumes from the existing Package 5.0 handover
and its unchanged readiness conditions.

Do not edit `docs/review/Handover information`: it is the active Package 5.0
handover and is not superseded by this prompt.

## Findings to remediate

### P4-PG1 — Important: malformed Discord identity is accepted or escapes the typed boundary

`CommandCaller.__post_init__` currently checks:

```python
if self.discord_user_id is not None and self.discord_user_id <= 0:
```

This has two incorrect outcomes:

- `True` is accepted as Discord user ID `1`, because Python's `bool` is an
  `int` subclass; and
- a malformed value such as `"123"` raises a raw `TypeError` from `<=`, rather
  than the documented `InvalidEnvelopeError(code="invalid_caller")`.

The constructor is the application boundary for this value. It must accept an
actual positive integer Discord snowflake and refuse booleans and every other
type with the existing typed error vocabulary. Do not silently coerce strings,
floats, decimals or other values to integers. Do not add a production Discord
ID or change identity resolution or authorization.

### P4-PG2 — Important: malformed expected-version aggregate type escapes the typed boundary

`ExpectedVersion.__post_init__` currently calls
`self.aggregate_type.strip()` before proving that `aggregate_type` is a string.
For example, `aggregate_type=1` raises `AttributeError`, rather than the
documented
`InvalidEnvelopeError(code="invalid_expected_version")`.

The constructor must first establish that `aggregate_type` is a string, then
apply its existing nonblank rule. Refuse malformed types through the existing
typed error vocabulary. Do not coerce them with `str(...)`, and do not change
the accepted aggregate name or expected-version semantics.

## Required implementation sequence

1. Add regression tests that fail on the current tree before changing
   production code. Demonstrate and record that failure in the handback.
2. Apply the smallest production correction in `application/commands.py`.
3. Run the focused regression/Phase 4 tests.
4. Run the full prescribed suites serially against the corrected tree.
5. Review the diff for unrelated changes, secrets, real player data and unsafe
   logging.
6. Return the correction to Codex for independent re-review. Do not declare
   either finding closed yourself.

## Mandatory regression coverage

Add table-driven coverage proving at least:

- a representative positive integer Discord snowflake remains accepted;
- `0` and negative integers remain refused with `invalid_caller`;
- `True` and `False` are refused with `invalid_caller`;
- representative non-integer Discord-ID inputs, including a numeric string and
  a float, are refused with `invalid_caller`, not `TypeError`;
- a nonblank string `aggregate_type` remains accepted;
- blank string aggregate types remain refused with
  `invalid_expected_version`; and
- representative non-string aggregate types, including an integer and a
  boolean, are refused with `invalid_expected_version`, not `AttributeError`.

Use synthetic values only. Tests must not contact Discord, Sheets, Foundry or a
production database.

## Scope constraints

Expected production change: `application/commands.py` only.

Expected test change: `tests/test_p4_commands.py` only, unless an existing test
organization makes one additional Phase 4 test file strictly necessary. If any
other production or test file must change, stop and explain why before widening
scope.

Do not:

- alter the ledger domain or ledger service;
- change authorization ports, service-principal scopes or audit attribution;
- change idempotency hashing or receipt schemas;
- add a migration, dependency, framework, adapter, route or command;
- update Package 5.0 design, findings, decisions, risks or readiness state;
- modify deployment, host accounts, groups, permissions, services, databases or
  credentials; or
- clean up adjacent validation code that is not required by P4-PG1 or P4-PG2.

If the narrow fix exposes a materially broader boundary defect, stop and report
it rather than absorbing it into this correction.

## Verification contract

Use the repository-prescribed interpreters and exported database URL. Run the
suites serially:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'

/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/test_p4_commands.py

/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs

/opt/discord-bots/venv/bin/python -m compileall -q \
  application/commands.py tests/test_p4_commands.py
/opt/discord-bots/venv-web/bin/python -m compileall -q \
  application/commands.py tests/test_p4_commands.py

git diff --check
```

The established pre-remediation full-suite baseline observed by Codex on
2026-08-31 was:

- bot/application: **2929 passed**, zero skips reported;
- web: **2824 passed, 80 skipped**;
- Foundry: **171 passed**; and
- `git diff --check`: clean.

Do not copy these figures into the handback as new evidence. Report only results
actually produced against the corrected tree. For the web suite, verify that the
skip count remains exactly 80 and include the `-rs` reason summary. Run no suites
in parallel because the Python suites share one disposable database.

No formatter, linter or type checker is presently configured. Record each as
`not configured`; do not describe it as passed and do not introduce tooling in
this correction.

## Handback

Create
`docs/review/phase-4-post-gate-remediation-handback.md` containing:

- an explicit statement that Phase 4 remains approved and that this is a narrow
  post-gate correction;
- the two defects conceded in concrete Python terms;
- the failing regression-test command and exact pre-fix failure output;
- files changed and why each was necessary;
- the exact validation rules after the correction;
- focused and full verification commands with exact pass/skip/fail totals;
- checks not run and why;
- confirmation that no Package 5, migration, deployment, host, database,
  credential, Discord, Sheets or Foundry mutation occurred;
- confirmation that `docs/review/Handover information` was not changed;
- any residual or unexpected finding; and
- a request for Codex independent re-review of P4-PG1 and P4-PG2.

Do not update the Phase 4 acceptance decision, close either finding, or claim
that the correction releases Package 5. Codex supplies the independent
disposition; the maintainer decides any governance consequence. If both
findings are accepted, continuation returns to the existing Package 5.0
readiness and security-remediation sequence exactly where it stood.
