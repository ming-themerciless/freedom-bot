# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R5

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Peter Duscha authorized the bounded Package 5.0 pre-implementation evidence
harness. Codex's independent pre-execution review of the R4 executing-runner
submission returned two **Blocking** findings. Remediate only those findings and
the directly necessary tests and handback documentation.

This prompt authorizes **unprivileged code and test remediation only**. It does
not authorize `--execute`, construction of an armed `SubprocessBoundary` outside
tests, execution of any harness command through the real process boundary,
privileged or mutation-bearing execution on `oracle-test` or any other host,
Package 5.0 product implementation, migration `0014`, production or staging
mutation, deployment, cutover, OD-62's binding ruling, or Package 5.1+.

The approved disposable target facts remain unchanged, but their existence is
not execution authority. Stop after returning the corrected tree and evidence
to Codex for independent pre-execution re-review. Package 5.0 remains `not
ready`. Claim no finding, assumption, readiness item, operational check or gate
closed, passed or confirmed.

## Required reading and worktree discipline

Before planning or editing, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/operations/disposable-test-server.md`;
4. `docs/review/Handover information`;
5. this prompt;
6. `docs/review/phase-5-0-evidence-harness-authorization-draft.md`;
7. `docs/review/phase-5-0-evidence-harness-implementation-prompt.md`;
8. all earlier evidence-harness remediation prompts;
9. the current concrete plan, review manifest and implementation handback;
10. `tools/phase_5_0_evidence/` in full; and
11. `tests/phase_5_0_evidence/` in full.

Check `git status` first. Preserve the complete existing dirty worktree; it is
the submission under review. Do not reset, revert, stage, commit, push, delete
generated work belonging to another contributor, or modify live services. If
the controlling documents conflict, stop and identify the exact passages.

## Review evidence to reproduce first

Run the focused suites before editing and record their exact results:

```sh
/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/test_skills.py tests/test_filesystem_layout.py
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/web/test_p3_4_static_assets.py
git diff --check
```

Codex obtained **546 passed** from the first command, **59 passed** from the
second, and a clean whitespace check. These green results do not cover the two
real-boundary defects below. Do not weaken existing tests or treat fake-boundary
coverage as proof of operating-system credential behavior.

## EH-R5-1 — Blocking: the real process boundary constructs the wrong identity

### Defect

`SubprocessBoundary.run()` currently passes `user=run_as` and
`extra_groups=[]` for each non-root step, while omitting `group=`. Its comment
claims that `user=` selects the account's primary group, but Python's
`subprocess.Popen` treats user, group and supplementary groups as separate
credential controls. Omitting `group=` does not establish the reviewed target
primary GID. Supplying `extra_groups=[]` deliberately clears every
supplementary group, including memberships such as `freedomjournal` on which
the reviewed positive traversal and isolation cases depend.

The process can therefore execute under a UID/GID/group vector different from
the plan's declared E1-E8 identity. A positive control may fail, or a refusal
may occur, for the harness's credential-construction defect rather than for the
authority being tested. Such a result is not admissible evidence.

### Required correction

Implement one explicit, fail-closed credential-resolution contract for every
non-root `run_as` identity:

- resolve the account before process creation to a numeric UID, primary GID and
  exact supplementary-group list required by the reviewed plan;
- pass `user=`, `group=` and `extra_groups=` explicitly to `subprocess.run`;
- do not inherit the caller's primary or supplementary groups;
- do not erase a target account's required configured supplementary groups;
- distinguish the existing host identities from identities provisioned by the
  harness without inventing memberships or defaulting to root;
- require the resolved memberships to equal the plan's closed identity contract
  before starting the command; an absent account, group, required membership,
  unexpected membership, lookup inconsistency or malformed identity must refuse
  before `subprocess.run`;
- keep `root` explicit as well: either validate that the harness process is
  already effective UID/GID 0 with the intended root group vector before a root
  step, or construct and validate the exact reviewed root identity. Never let
  `run_as="root"` mean "whatever identity launched the CLI";
- keep lookup and credential construction inside the single reviewed process
  boundary or a small injected resolver owned by it; planning modules must not
  gain host reads; and
- return only a fixed safe `launch_failure` classification. Do not expose
  account databases, numeric IDs, group lists or operating-system exception
  text in serialized evidence.

Do not solve this with `sudo`, `su`, a shell, `setpriv`, `capsh`, a helper
executable, a mutable environment variable, or an unreviewed wrapper in the
argument vector. The reviewed vector must remain the vector passed to
`subprocess.run`.

Required regressions, using injected lookup functions and a mocked
`subprocess.run` only:

- a normal non-root account passes its numeric UID, primary GID and exact
  supplementary groups explicitly;
- a `freedomjournal` member retains that required supplementary group;
- a non-member receives no inherited supplementary group;
- changing the parent process's groups cannot change the child keyword set;
- omitted, unknown, duplicated, unexpected or inconsistent accounts/groups
  refuse before process creation;
- a required supplementary membership missing at execution time refuses;
- an unexpected supplementary membership, if the reviewed identity contract
  requires an exact set, refuses;
- a non-root launcher cannot execute a `run_as="root"` step as itself;
- the fixed safe failure classifications contain no raw lookup exception text;
  and
- no test starts a real process or reads the host account/group database.

The tests must assert the actual `subprocess.run` keyword arguments. A fake
`ProcessBoundary` test does not prove this correction.

## EH-R5-2 — Blocking: unexpected execution exceptions bypass cleanup

### Defect

`ExecutingRunner.execute()` calls the process boundary inside its step loop and
reaches `_clean_up()` only after the loop exits normally. There is no
`try/finally` or equivalent cleanup guard around mutation-bearing execution.
An unexpected `OSError`, capture/sanitizer exception, programming error,
`KeyboardInterrupt`, or other exception after any mutation has been reached can
therefore unwind past cleanup and leave accounts, groups, files, PostgreSQL
objects or configuration, or transient units behind.

This contradicts the executor's stated guarantee that cleanup runs whenever a
mutation was reached, including when execution raised. Because the harness
modifies authentication configuration and host identities, this is a
production-reliability and recovery blocker even on the disposable target.

### Required correction

Restructure execution so cleanup is guaranteed after the first attempted
mutation-bearing step, for normal completion, an unsatisfied result, timeout,
safe launch refusal, ordinary exception and operator interruption:

- establish cleanup responsibility before invoking a mutation-bearing command;
- invoke cleanup exactly once when any mutation may have occurred;
- preserve the original execution failure and separately retain the cleanup
  outcome; a cleanup exception must not erase the fact that execution failed,
  and an execution exception must not be reported as a successful run;
- translate unexpected boundary/capture exceptions to a fixed safe failure
  category without serializing raw exception text;
- if cleanup itself raises or cannot complete, return or raise a typed outcome
  that unambiguously represents S-B, names only bounded declared residue or
  effective-configuration risk, and never reports `artifact_admissible=True`;
- do not catch `BaseException` merely to suppress termination. If
  `KeyboardInterrupt` or `SystemExit` is re-raised, cleanup must finish first;
- cleanup must use the existing derived, bounded, non-recursive plan and remain
  subject to per-step validation, identity validation and timeouts;
- a mutation command whose launch outcome is uncertain must be treated as
  potentially reached; and
- no second invocation on the same runner may proceed after uncertain or failed
  cleanup.

Required injected-boundary regressions:

- exceptions before the first mutation do not run destructive cleanup;
- an exception immediately before invoking the first mutation-bearing boundary
  call follows the explicitly documented responsibility rule;
- exceptions from the first and each representative later mutation class run
  cleanup exactly once;
- exceptions from sanitization/capture handling follow the same cleanup path;
- `KeyboardInterrupt` and `SystemExit` run cleanup before propagation;
- an ordinary execution exception plus successful cleanup remains a failed,
  non-admissible run;
- execution failure plus cleanup failure preserves both facts and yields S-B;
- a cleanup-boundary exception cannot skip the remaining safe cleanup steps
  unless the existing dependency contract requires a stop, and it cannot claim
  S-C;
- no exception path writes an evidence artifact; and
- rerunning an executor after uncertain residue or effective configuration is
  refused.

Tests must exercise `ExecutingRunner` with boundaries that raise at controlled
call numbers. Do not add a broad `except Exception: pass`, convert interrupts
into success, or manufacture a clean S-C result when cleanup observations are
missing.

## Documentation and manifest consequences

Add a dated **R5 remediation section** at the top of
`docs/review/phase-5-0-evidence-harness-implementation-handback.md`. Preserve R4
and earlier history below it. The R5 section must:

- concede EH-R5-1 and EH-R5-2 before describing the corrections;
- identify the exact pre-fix commands and results above;
- list every changed file and why;
- document the final UID/GID/supplementary-group resolution contract;
- document exception, interruption and cleanup-failure semantics;
- map every requirement above to named code and tests;
- report only newly run results as current evidence and label older totals as
  superseded;
- confirm no real process boundary, privileged command or mutation-bearing
  command ran; and
- request Codex independent pre-execution re-review while claiming no finding
  closed and no readiness consequence.

Update comments/docstrings that currently make the false primary-group or
exception-cleanup claims. Update the concrete plan only if the correction
changes a fact it presents. Regenerate the review manifest and concrete plan if
their covered bytes or digest contract require it; never hand-edit a generated
digest. A new digest is a value for Codex to review, not permission to execute.

## Scope and safety

Expected changes are limited to:

- `tools/phase_5_0_evidence/execution/boundary.py`;
- `tools/phase_5_0_evidence/execution/executor.py`;
- directly necessary small supporting types in the same execution package;
- focused tests under `tests/phase_5_0_evidence/`;
- the generated concrete plan and review manifest when required;
- the implementation handback; and
- `docs/review/Handover information` when returning control to Codex.

Do not alter product application code, bot behavior, migrations, database
schemas, deployment files, infrastructure scripts, the roadmap, project status,
RAID, decision register or change log. If a file outside this list is necessary,
stop and explain why before widening scope.

Preserve these invariants:

- default invocation and every test execute no harness command;
- `SubprocessBoundary(armed=True)` remains reachable only through the explicit
  CLI `--execute` path and must not be constructed during this remediation;
- no privileged read, socket, HTTP request, database connection or external
  service access occurs;
- no arbitrary output, secret, credential, player data or raw exception enters
  evidence;
- argument vectors remain absolute, shell-free and covered by the review
  manifest;
- cleanup remains bounded, derived and non-recursive; and
- unresolved plan conflicts continue to make `ExecutingRunner` refuse before a
  process can start.

## Verification

Run serially against the final tree with the documented interpreters:

```sh
/opt/discord-bots/venv/bin/python -m pytest -q -rs \
  tests/phase_5_0_evidence
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
/opt/discord-bots/venv/bin/python -m compileall -q \
  tools/phase_5_0_evidence tests/phase_5_0_evidence
git diff --check
```

Run the bot and web full suites serially because they share the disposable test
database. The web suite must retain exactly 80 expected permission-matrix skips.
Report actual totals, skips and warnings from the final tree. Do not reuse prior
totals. Formatter, linter and type checker remain not configured; do not add
tooling or claim those checks passed.

Do not invoke the CLI with `--execute`, instantiate an armed real boundary, run
the generated vectors individually, SSH to run them, or perform a privileged
spot check. Mocked/injected boundary tests are the only execution-layer tests
authorized here.

If any focused or full suite fails, do not present the remediation as complete.
Continue correcting only within this prompt's scope or stop and identify the
scope conflict.

## Return to Codex

After verification, make `docs/review/Handover information` begin with a short
current handover stating that R5 is submitted for Codex independent
pre-execution re-review. It must state that no real process boundary, privileged
or mutation-bearing command ran; claim no finding closed; provide the new review
manifest digest if regenerated; and preserve all superseded history below it.

Then stop. Do not execute the harness, grant execution approval, close a
finding, recommend readiness, change the package state, or proceed to Package
5.0 implementation.
