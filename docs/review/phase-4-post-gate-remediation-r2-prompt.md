# Claude prompt — Phase 4 post-gate remediation R2 · service-principal identifier boundary

You are Claude, the implementing agent and working Technical Lead for this
final bounded post-gate correction to Phase 4. Work in
`/opt/freedom-blades/platform`.

Before planning or changing anything, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. this prompt;
4. `docs/review/phase-4-post-gate-remediation-prompt.md`;
5. `docs/review/phase-4-post-gate-remediation-handback.md`;
6. `application/commands.py`;
7. `tests/test_p4_commands.py`; and
8. the Phase 4 acceptance record in `docs/review/phase-4-submission.md`.

Check `git status` before editing. Preserve all unrelated maintainer-owned and
agent-owned work. Do not reset, revert, reformat or rewrite unrelated files.

## Status and authority

Phase 4 remains approved. Codex independently re-reviewed remediation R1 and
found **P4-PG1** and **P4-PG2 materially remediated**. Preserve those fixes and
their tests exactly unless a strictly necessary adjustment is explained in the
handback.

Claude correctly reported one additional instance of the same defect class and
did not absorb it into R1. Codex classifies it as **P4-PG3 — Important** and
requests this final bounded correction before Phase 5 preparation continues.

This prompt authorizes only P4-PG3 remediation and its evidence. Package 5.0
remains `not ready`; this does not authorize Package 5.0 implementation,
migration `0014`, deployment, cutover, production or host changes, or Package
5.1+ work.

Do not edit `docs/review/Handover information`. It remains the active Package
5.0 handover and is resumed only after this correction passes independent
re-review.

## Finding to remediate

### P4-PG3 — Important: malformed service-principal identifier escapes or bypasses the typed boundary

`CommandCaller.__post_init__` currently ends with:

```python
if self.principal_id is not None and not self.principal_id.strip():
    raise InvalidEnvelopeError(
        "invalid_caller", "A service principal id may not be blank."
    )
```

This acts on `principal_id` before establishing that it is text:

- values such as `123`, `1.0` and `True` raise raw `AttributeError` rather than
  `InvalidEnvelopeError(code="invalid_caller")`; and
- a bytes value such as `b"principal"` has `.strip()` and is accepted even
  though it cannot be the string identity expected by
  `LedgerPrincipalPort.current_principal()`.

`CommandCaller` is the application boundary for this value. A service-principal
identifier must be a `str` before the existing nonblank rule is applied.
Malformed types must be refused through the existing `invalid_caller` typed
error. Do not coerce values with `str(...)`, decode bytes, normalize identifiers,
or change authorization or resolution behavior.

This correction validates only the envelope's identifier shape. It does not
grant authority. `LedgerCommandService` must continue resolving current
authority through `LedgerPrincipalPort` at execution.

## Required implementation sequence

1. Add regression tests that fail against the current R1-corrected production
   code before changing it. Record the exact failing command and output.
2. Apply the smallest correction in `application/commands.py`.
3. Run the focused Phase 4 command tests.
4. Run all prescribed suites serially against the corrected tree.
5. Review the diff for scope, secrets, player data and unsafe logging.
6. Return the correction to Codex for independent re-review. Do not declare
   P4-PG3 closed yourself.

## Mandatory regression coverage

Add table-driven synthetic tests proving at least:

- a representative valid nonblank string principal ID remains accepted;
- blank strings (`""`, whitespace, tab and newline) remain refused with
  `invalid_caller`;
- integers, booleans, floats, bytes, lists and tuples are refused with
  `InvalidEnvelopeError(code="invalid_caller")`, not raw `AttributeError` or
  another exception;
- a bytes value that previously passed because it had `.strip()` is refused;
- malformed values are not silently converted or decoded; and
- P4-PG1's Discord-ID and P4-PG2's aggregate-type regression tests remain
  passing unchanged.

Do not use a real service-principal identifier, credential or production value.
Tests must not contact Discord, Sheets, Foundry or a production database.

## Scope constraints

Expected production change: `application/commands.py` only.

Expected test change: `tests/test_p4_commands.py` only.

Expected documentation change: the R2 handback requested below only.

If another production or test file appears necessary, stop and explain the
need before widening scope.

Do not:

- alter the accepted P4-PG1/P4-PG2 behavior;
- change `validate_principal_id`, `LedgerPrincipal`, `LedgerPrincipalPort`,
  authorization ports, scopes or audit attribution;
- impose the configured-principal character vocabulary at the envelope
  boundary—the current port remains responsible for resolving whether an
  identifier exists and is authorized;
- alter the ledger domain or ledger service;
- change idempotency hashing, command envelopes beyond this validation, or
  receipt schemas;
- add a migration, dependency, framework, adapter, route or command;
- update Package 5.0 plans, findings, decisions, risks or readiness state;
- modify deployment, host accounts, groups, permissions, services, databases or
  credentials; or
- perform adjacent cleanup unrelated to P4-PG3.

If this correction exposes another material defect, stop and report it rather
than absorbing it.

## Verification contract

Use the repository-prescribed interpreters and exported test database URL. Run
the suites serially:

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

R1's submitted corrected-tree baseline was:

- focused command tests: **92 passed**;
- bot/application: **2960 passed**, zero skips reported;
- web: **2824 passed, 80 skipped**;
- Foundry: **171 passed**; and
- both `compileall` checks and `git diff --check`: clean.

Codex independently reproduced the **92 focused passes** and both `compileall`
checks. These figures are context only. Report only commands and results
actually produced against the R2 tree. Confirm that the web skip count remains
exactly 80 and include the `-rs` reasons. Do not run the Python suites in
parallel because they share one disposable database.

No formatter, linter or type checker is configured. Record each as `not
configured`; do not claim it passed and do not introduce tooling.

## Handback

Create
`docs/review/phase-4-post-gate-remediation-r2-handback.md` containing:

- confirmation that Phase 4 remains approved and this is a narrow post-gate
  correction;
- P4-PG3 conceded in concrete Python terms;
- the failing regression-test command and exact pre-fix failure output;
- files changed and why;
- the exact validation rule after correction;
- proof that P4-PG1 and P4-PG2 remain passing;
- focused and full verification commands with exact totals and skip reasons;
- checks not run and why;
- diff review for scope, secrets, real data and unsafe logging;
- confirmation that no Package 5, migration, deployment, host, database,
  credential, Discord, Sheets or Foundry mutation occurred;
- confirmation that `docs/review/Handover information` was not changed;
- every unexpected or residual finding; and
- a request for Codex independent re-review of P4-PG3.

Do not close P4-PG3, alter the Phase 4 acceptance decision, or claim this work
releases Package 5. Codex supplies the independent disposition. If P4-PG3 is
accepted with no further Blocking or Important Phase 4 finding, the post-gate
remediation is complete and work returns to the existing Package 5.0 readiness
and security-remediation sequence exactly where it stood.
