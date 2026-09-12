# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R7

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Codex independently re-reviewed the R6 evidence-harness submission. **EH-R6-2
is Closed**: account and group records are counted rather than deduplicated,
the direct lookup must agree with the sole enumerated record, and the safe
failure vocabulary is preserved. No new Blocking or Important implementation
finding was identified.

**EH-R6-1 remains Blocking.** R6 correctly removed the unreviewed
`AS_CONFIGURED` pass-through and now fails closed, but no controlled source
states the exact permitted supplementary-group set for the `postgres`
operating-system account. Consequently the PostgreSQL evidence and its cleanup
cannot execute. Codex recommends R6 handback **Option A**: add one exact
`postgres` row to package-plan §2.12.2 and derive the execution contract from
that canonical row. This recommendation is not a maintainer ruling and does not
select the group set.

This prompt authorizes only the bounded, unprivileged R7 remediation described
below, and only **after** Peter Duscha records a ruling that states:

1. whether Option A is accepted; and
2. under Option A, the exact complete supplementary-group set permitted for
   `postgres` (including an explicit empty set if that is the ruling).

Do not infer `ssl-cert`, inspect a host to turn current state into policy, or
treat this prompt or Codex's recommendation as approval. If that ruling is not
present in the conversation or a controlled repository record, make no code or
document change and return one concise decision request for those two facts.

This prompt does **not** authorize `--execute`, an armed real
`SubprocessBoundary`, execution of a generated vector, SSH, host account/group
inspection, privileged or mutation-bearing commands, mutation of
`oracle-test`, Package 5.0 product implementation, migration `0014`, production
or staging mutation, deployment, cutover, OD-62's binding ruling, or Package
5.1+. Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.

## Required reading and worktree discipline

Before planning or editing, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/operations/disposable-test-server.md`;
4. `docs/review/Handover information`;
5. this prompt and the R6 remediation prompt;
6. the evidence-harness authorization and implementation prompts;
7. the current package plan §2.12.2, concrete plan, review manifest, and
   implementation handback;
8. `tools/phase_5_0_evidence/` in full; and
9. `tests/phase_5_0_evidence/` in full.

Check `git status` first. Preserve the complete dirty worktree. Do not reset,
revert, stage, commit, push, delete another contributor's files, or modify live
services. If a ruling conflicts with a controlled document, stop and cite the
exact passages instead of choosing between them.

## Review disposition to preserve

Codex ran these checks against R6:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m compileall -q \
  tools/phase_5_0_evidence tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli
git diff --check
```

Results: **550 passed**, `compileall` clean, a dry run of **64 steps, 39
mutations, 42 cleanup steps and 16 unresolved conflicts**, digest
`18bb5ccd1cc0845b2bbc397b0acb4943b6c1f2d02ad8b3f64590905f942a9fc6`,
`executable: False`, and a clean whitespace check. No real process boundary,
SSH connection, host lookup, database operation, or mutation ran.

These are review inputs, not execution authority. The R6 digest is superseded
by any covered-source edit and must never be passed to `--execute`.

## EH-R6-1 — required correction after the ruling

If and only if the maintainer accepts Option A and supplies the exact set:

1. Amend package-plan §2.12.2 through the repository's controlled
   change-governance mechanism so it contains exactly one `postgres` row with
   primary group `postgres` and the ruled complete supplementary-group set.
   Update the inverse group-to-members table consistently. Do not alter any
   other identity or widen Package 5.0 scope.
2. Add `postgres` once to `identity.CANONICAL_ACCOUNTS`, transcribing that row
   exactly and marking it as an existing host identity, not package-provisioned.
3. Replace the `UNDECIDED` `postgres` row in `IDENTITY_CONTRACT` with
   `_from_canonical("postgres")`. Remove `UNDECIDED` and
   `UNDECIDED_MEMBERSHIP` entirely if no row uses them; do not retain an unused
   escape hatch or introduce a second policy source.
4. Preserve unconditional exact set equality. A missing or unexpected group
   must refuse before the account database is read far enough to create a
   process, and no parent or host-configured group outside the canonical set may
   reach `extra_groups=`.
5. Preserve the fixed safe `LAUNCH_FAILURES` vocabulary and the existing R5
   guaranteed-cleanup behavior. Do not broaden exception output, identity
   fallback, permitted executables, target scope, or execution reachability.
6. Keep `PERMITTED_RUN_AS`, identity construction, generated steps, and tests
   derived from the single canonical source or guarded by import-time
   consistency checks that fail closed.

If the maintainer selects another option, stop before implementation and return
the exact impact against R6 handback §R6.4. Options B–D change either the
credential policy or the authority being tested and require a replacement
scoped instruction; this prompt does not silently authorize them.

## Required regressions

Update focused tests so they prove:

- the canonical source contains exactly one `postgres` row with the ruled
  primary and complete supplementary set;
- `IDENTITY_CONTRACT["postgres"]` is derived from that canonical row and uses
  `MembershipRule.EXACT`;
- the exact numeric GIDs reach `extra_groups=` in deterministic order;
- a missing required group and one unexpected group each refuse before the
  process starter is called;
- an empty ruled set, if selected, passes `extra_groups=[]` and still rejects
  every unexpected group;
- changing the parent process's groups cannot change the child credential;
- changing the canonical `postgres` policy changes the review-manifest digest;
- canonical/contract drift fails closed;
- identical and contradictory duplicate account/group records continue to
  refuse, preserving EH-R6-2; and
- no test reads the real account/group database or starts a real process.

Do not weaken structural no-execution tests to accommodate the change.

## Documentation and generated artifacts

Add a dated **R7 remediation section** at the top of
`docs/review/phase-5-0-evidence-harness-implementation-handback.md`, preserving
R6 and earlier history. It must:

- quote or precisely cite the maintainer ruling, its date, and the exact set;
- state that EH-R6-2 was closed by Codex and preserved;
- concede that EH-R6-1 remained Blocking before this remediation;
- list every changed file and why;
- trace the canonical row through credential construction and tests;
- map every requirement above to named code and tests;
- report only checks newly run against the final R7 tree;
- state that no real boundary, host lookup, SSH, privileged command, database
  operation, or mutation ran; and
- return R7 to Codex for independent pre-execution re-review, claiming no
  execution approval, readiness consequence, assumption confirmation, or gate
  closure.

Regenerate the concrete plan and review manifest because covered sources will
change. Generate each twice and compare bytes to prove determinism. Never
hand-edit either generated artifact or copy its digest into an execution
command. Update `docs/review/Handover information` to identify R7 as returned
to Codex, while preserving prior handovers below it.

Expected changed files are limited to:

- `docs/review/phase-5-0-package-plan.md` §2.12.2 and its directly required
  controlled decision/change record;
- `tools/phase_5_0_evidence/identity.py`;
- `tools/phase_5_0_evidence/execution/boundary.py`;
- `tools/phase_5_0_evidence/execution/executor.py` only if a comment or derived
  identity assertion must change;
- focused tests under `tests/phase_5_0_evidence/`;
- the generated concrete plan and review manifest;
- the implementation handback; and
- `docs/review/Handover information`.

Stop before changing any product application code, migration, schema,
deployment file, infrastructure script, roadmap, project status, RAID entry,
unrelated decision, or change-log content beyond the exact governance record
required to make the maintainer's ruling controlled.

## Verification and handback

Run serially against the final R7 tree:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
/opt/discord-bots/venv/bin/python -m compileall -q \
  tools/phase_5_0_evidence tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli
git diff --check
```

Report exact pass, fail, and skip counts. The CLI invocation must remain a dry
run and must report `executable: False` while any conflict remains. Do not pass
`--execute`, the confirmation token, or any reviewed digest. Inspect the final
diff for scope drift, secrets, raw host data, unsafe exception text, and any
path that could arm execution without the explicit prohibited branch.

Then stop and return the tree to Codex. No R7 result authorizes execution; a
separate independent pre-execution review and explicit maintainer authority are
still required.
