# Claude implementation prompt — Phase 2 mapped-name normalization closure

Session context: 2026-08-02. Work in `/opt/discord-bots/freedom-bot` on the
current dirty working tree. Preserve all unrelated maintainer and agent changes.
Do not commit, push, stash, reset, check out, restore, delete, or reformat
unrelated work.

## Objective

Close the final blocking review defect in the existing Phase 2 Sheet identity
bootstrap slice: mapped-name comparison and collision lookup currently use
inconsistent Unicode normalization semantics.

Implement the narrow correction, add regression evidence, update the applicable
documentation and prepare a review handoff. Do not begin or claim completion of
the broader Foundry snapshot milestone, Phase 3, or another Phase 2 package.

## Required context before planning or editing

Read these files completely, in this order:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §§0, 6.4–6.5, 12 Phase 2,
   13.3, 16 and 20
4. `docs/project-management/README.md`
5. `docs/project-management/status.md`
6. `docs/project-management/raid-register.md`
7. `docs/project-management/decision-register.md`
8. `docs/project-management/change-log.md`
9. `docs/review/phase-2-submission.md`, especially §§0.3, 2.13, 7.0, 11,
   12 and 13
10. `docs/operations/sheet-import.md`
11. `application/sheet_import.py`
12. `application/repositories.py`
13. `adapters/database/repositories.py`
14. `adapters/sheets/character_import.py`
15. `tests/fakes.py`
16. `tests/test_sheet_import_service.py`
17. `tests/test_sheet_import_database.py`
18. `tests/test_import_cli.py`

Inspect `git status --short` before editing. Do not read `.env`, credential
files, ignored credential-shaped files, real Foundry artifacts, or real player
data. Do not contact Discord, Google Sheets, Foundry, or a production/staging
database.

## Blocking defect to reproduce first

The importer decides whether a mapped name changed semantically with Python
`casefold()` in `application/sheet_import.py`. It also skips collision lookup
when the two folded names match. The fake and PostgreSQL character repositories
use `lower()` for `find_by_display_name()`.

`casefold()` is broader than capitalization. For example, `Straße` and
`STRASSE` fold to the same value, but `lower()` does not make them equal. The
current service can therefore:

1. hold one character named `Test Straße` and another named `Test STRASSE`;
2. import mapped `Test Straße` as `Test STRASSE`;
3. classify it as a permitted capitalization update;
4. skip collision lookup; and
5. commit two characters with the exact display name `Test STRASSE`, with no
   blocking issue.

Codex reproduced the current result as:

```text
applied= True
issues= []
names= ['Test STRASSE', 'Test STRASSE']
```

Add a focused regression test that proves this failure against the uncorrected
implementation before changing production code. Record the exact failing test
and result in the handoff; do not leave the code deliberately broken after the
proof.

## Accepted policy — do not reopen it

The product decision is already made and baseline v1.0 is accepted by Peter
Duscha:

- an exact mapped display-name match is identity-neutral;
- a change of capitalization alone may update automatically when it does not
  collide with another character;
- every other mapped display-name change is a semantic identity change and must
  be refused (`mapped_name_change`, or the existing more specific refusal when
  applicable);
- every spelling change, including capitalization-only, must be checked for a
  different character already claiming the permitted comparison identity;
- unmapped creation must use the same comparison policy and must not mint a
  second character through Unicode-normalization disagreement;
- identity comes only from the stable stored mapping, never from name
  similarity;
- one blocked row blocks and rolls back the complete run, including characters,
  mappings, versions and audit events;
- dry run and apply must make the same decision; and
- no mapping is silently re-keyed.

For this importer, “capitalization-only” must not mean arbitrary Unicode
`casefold()` equivalence. `Test Straße -> Test STRASSE` is a semantic change and
must be refused. A conventional change such as `Test Smith A -> TEST SMITH A`
remains eligible to apply after collision checking.

## Implementation requirements

1. Define one small, explicit display-name comparison policy in an inward,
   infrastructure-free location appropriate to the current architecture. Avoid
   scattered direct calls to `lower()` and `casefold()` for identity decisions.
2. Give the policy intention-revealing operations for at least:
   - exact equality;
   - capitalization-only equivalence; and
   - the canonical collision key/equivalence used by this bootstrap.
3. Use the same policy in the Sheet parser, import application service, fake
   repository and PostgreSQL repository wherever they decide name equivalence.
4. Perform collision lookup for every non-exact mapped spelling change, even
   when it is capitalization-only.
5. Ensure the PostgreSQL adapter actually honors the repository protocol for
   the complete supported comparison domain. Do not claim that SQL `lower()` is
   equivalent if it is not. The live bootstrap population is deliberately
   small, so a clear bounded Python-side comparison is acceptable if that is
   safer than database/locale-specific behavior. If choosing that approach,
   document the cost and the threshold that would trigger a normalized/indexed
   schema design later.
6. Preserve all existing issue codes, outcome shapes, transaction boundaries,
   idempotency behavior, audit vocabulary and CLI exit behavior except where
   the new blocking case necessarily adds an issue.
7. Do not add a migration or dependency unless it is genuinely necessary. If
   either becomes necessary, stop and request maintainer approval because that
   expands this correction materially.
8. Keep the change confined to this defect. Do not implement a rename/re-key
   command or Foundry reconciliation flow.

## Mandatory acceptance criteria

Automated tests must demonstrate all of the following:

1. Exact same name remains unchanged and idempotent.
2. `Test Smith A -> TEST SMITH A` applies as an update when no other character
   claims that comparison identity.
3. A capitalization-only mapped change colliding with another character is
   refused as `name_collision` and commits nothing.
4. `Test Straße -> Test STRASSE` is a semantic mapped-name change and is refused
   as `mapped_name_change` when no more specific refusal applies.
5. The concrete two-character reproduction above is refused and leaves both
   original identities, mappings, versions and audit rows unchanged.
6. An unmapped `Test STRASSE` is refused when `Test Straße` already exists under
   the importer's canonical collision policy; no second character or mapping is
   created.
7. Parser, fake repository, service and PostgreSQL repository agree on a
   table-driven set including ordinary case changes, German sharp-s expansion,
   and at least one exact non-ASCII name.
8. Dry-run and apply reach identical decisions for the new refusal cases.
9. A mixed run containing a valid non-identity update plus one normalization
   refusal rolls back characters, mappings, versions and audit effects
   atomically.
10. Existing fresh-name swap and three-row-cycle regressions remain green.

At least the concrete collision reproduction, capitalization-only collision,
unmapped collision and repository-policy agreement must execute against real
PostgreSQL as well as application fakes where applicable. A mocked repository
call does not prove PostgreSQL behavior.

## Documentation and project records

Update, as applicable:

- `docs/operations/sheet-import.md` with the exact comparison rule and examples;
- `docs/review/phase-2-submission.md` as the next revision, preserving earlier
  review history rather than rewriting it;
- `docs/project-management/status.md` after verification, marking I-01 closed
  only if the implementation is complete and independently reviewable;
- `docs/project-management/raid-register.md` with the resulting I-01/R-01
  status; and
- `docs/project-management/change-log.md` only if the accepted baseline itself
  changes. This correction is expected to implement existing policy, not amend
  it.

Do not overwrite this prompt during implementation. Put the final implementation
handoff in `docs/review/phase-2-submission.md` and summarize the exact section in
your response to Peter.

## Verification

Use the repository virtual environment. Run narrow checks first, then the full
available suite:

```bash
./venv/bin/pytest tests/test_sheet_import_service.py -q
./venv/bin/pytest tests/test_sheet_import_database.py -q
./venv/bin/pytest tests/test_import_cli.py -q
./venv/bin/pytest -q
./venv/bin/python -m compileall -q main.py config.py application adapters domain ext models tools
git diff --check
```

Also run the full suite with the guarded disposable PostgreSQL database using
the established repository procedure if `freedom_test` is available and passes
the two-layer test guard. Never substitute production or staging. Run:

```bash
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' ./venv/bin/alembic check
```

Do not claim PostgreSQL acceptance if `TEST_DATABASE_URL` was absent and the
tests skipped. Report exact pass/skip counts, warning text, commands not run and
why. No formatter, linter or type checker should be installed merely for this
task; report accurately whether any is configured.

## Handoff and stopping condition

Before handing back:

1. inspect the complete diff for unrelated changes, secrets, real data, unsafe
   logs and documentation contradictions;
2. report every file changed and why;
3. provide the regression proof that failed before the fix;
4. provide exact narrow, full and PostgreSQL verification results;
5. state database/migration/configuration/deployment effects (expected: none);
6. state rollback/recovery implications;
7. identify remaining limitations without claiming the broader Phase 2 gate is
   closed; and
8. request independent Codex re-review of this blocking defect.

Stop after this normalization correction and its handoff. Do not continue into
the Foundry snapshot importer, Phase 3, or any other package without a new
instruction and the applicable gate.
