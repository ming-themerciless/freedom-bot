# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R9

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Peter Duscha accepted Codex's recommendation on 2026-09-06, recorded in
package-plan §2.12.2 and change-log **C-P5.0-AF**. Apply this exact
representational correction to the group inverse:

- `freedomcoord`: no explicit members;
- `freedomsheet`: no explicit members;
- `discordbot`: `freedomweb` only; and
- `fbprobe`: no explicit members.

Peter Duscha also accepted Codex's follow-up recommendation on 2026-09-06 that
the missing inverse row for the already-recorded `foundry -> users`
supplementary membership is:

- `users`: `foundry` only.

These are the explicit members represented by the fourth field of
`getent group`. Do not change any account's primary group or complete
supplementary-group set. Remediate **EH-R8-2** and the directly related
documentation finding **DS-R8-2** only.

This prompt does **not** authorize `--execute`, an armed real process boundary,
execution of a generated vector, SSH, host inspection or mutation, privileged
or mutation-bearing commands, execution of the destructive backup/restore
drill, Package 5.0 product implementation, migration `0014`, deployment,
cutover, OD-62's binding ruling, or Package 5.1+. Package 5.0 remains `not
ready`; P5.0-R5 remains Blocking.

## Required reading and worktree discipline

Before editing, read completely `.agents/AGENTS.md`,
`docs/implementation-plan.md`, `docs/operations/disposable-test-server.md`,
`docs/review/Handover information`, this prompt, the R8 prompt and handback,
package-plan §2.12.2, `tools/phase_5_0_evidence/`,
`tests/phase_5_0_evidence/`, `infra/postgresql/backup-restore-drill.sh`, and its
operations/tests documentation. Check `git status` and preserve the complete
dirty worktree. Do not reset, revert, stage, commit, push or alter unrelated
files.

## EH-R8-2 — required implementation

1. Update `CANONICAL_GROUPS` to carry exactly the four corrected
   explicit-member sets and the `users = {foundry}` inverse row ruled above.
2. Remove `PRE_EXISTING_PRIMARY_IN_INVERSE` and all tests or current-state prose
   that treat those false rows as an accepted hold. Preserve the historical R8
   handback account of what R8 submitted.
3. Generalize the consistency validation so every supplementary membership
   stated by `CANONICAL_ACCOUNTS` appears in the inverse and every explicit
   inverse member is stated as supplementary by that account. Primary groups
   must not participate in this relation.
4. Ensure every canonical supplementary membership is represented in the
   inverse. The previously missing `foundry -> users` relation is decided by
   this prompt: add `CanonicalGroup("users", {"foundry"}, ...)` exactly. Do not
   infer any additional member from the host or from accounts outside the
   controlled Package 5.0 identity table.
5. Preserve the accepted `postgres` row, `MembershipRule.EXACT`, fixed safe
   launch classifications, exact-one NSS lookup, manifest binding and guaranteed
   cleanup behavior.

Required tests must prove all canonical account/inverse relations agree in both
directions; the four corrected sets and `users = {foundry}` are exact; primary membership is never treated
as explicit membership; unexpected or missing supplementary membership refuses
before process creation; drift fails at import/validation; and no test reads the
host account database or starts a real process.

## DS-R8-2 — documentation correction

The runtime-role decision occurs after `pg_dump`, checksum creation, work
directory creation and read-only inventories, but before `SCHEMA_DROPPED=1`,
`DROP SCHEMA` and restore. Correct the exit-code comments, operations guide,
tests and current handback language accordingly:

- do not say exit 2 occurs “before touching anything” for this branch;
- do not say “nothing is dumped”;
- state precisely that a dump and diagnostic artifacts may already exist, but
  no schema is dropped or restored, the database state remains intact and no
  recovery is required; and
- preserve the actual DS-R8-1 cardinality and role-name validation code unless
  a focused regression exposes a defect.

Do not run the destructive drill. Test this wording and ordering statically or
through the existing stubbed-client boundary.

## Generated artifacts, verification and handback

Add a dated R9 section at the top of the implementation handback, preserve all
earlier history, and update `docs/review/Handover information` to return R9 to
Codex. Concede both findings, identify every changed file, map requirements to
named tests, report only checks actually run, and claim no finding or gate
closed.

Regenerate the concrete plan and review manifest if covered sources change;
generate each twice and compare bytes. Never hand-edit a generated artifact or
pass its digest to `--execute`.

Run serially:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m pytest -q -rs \
  tests/test_database_backup_restore.py tests/test_filesystem_layout.py \
  <the seven destructive drill node IDs explicitly deselected>
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py \
  <the same seven destructive drill node IDs explicitly deselected>
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
/opt/discord-bots/venv/bin/python -m compileall -q \
  tools/phase_5_0_evidence tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli
git diff --check
```

Replace the placeholders with the exact seven node IDs already listed in R8
handback §R8.8; do not pass angle-bracket placeholders to the shell. Report the
seven as deselected by authority, not passed or silently skipped. The CLI must
remain a dry run and `executable: False` while conflicts remain.

Then stop and return the tree to Codex for independent pre-execution re-review.
