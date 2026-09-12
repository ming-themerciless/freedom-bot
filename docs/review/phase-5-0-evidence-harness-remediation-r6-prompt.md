# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R6

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Codex's independent pre-execution review of the R5 evidence-harness submission
found one remaining **Blocking** credential-policy defect and one **Important**
account-resolution defect. Remediate only those findings and the directly
necessary tests, generated review artifacts and handback documentation.

This prompt authorizes **unprivileged code and test remediation only**. It does
not authorize `--execute`, an armed real `SubprocessBoundary`, execution of any
generated vector, SSH or privileged inspection, mutation of `oracle-test`,
Package 5.0 product implementation, migration `0014`, production or staging
mutation, deployment, cutover, OD-62's binding ruling, or Package 5.1+.

Stop after returning R6 to Codex for independent pre-execution re-review.
Package 5.0 remains `not ready`; P5.0-R5 remains Blocking. Claim no finding,
assumption, readiness item, operational check or gate closed or confirmed.

## Required reading and worktree discipline

Before planning or editing, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/operations/disposable-test-server.md`;
4. `docs/review/Handover information`;
5. this prompt and the R5 remediation prompt;
6. the evidence-harness authorization and implementation prompts;
7. the current concrete plan, review manifest and implementation handback;
8. `tools/phase_5_0_evidence/` in full; and
9. `tests/phase_5_0_evidence/` in full.

Check `git status` first. Preserve the complete dirty worktree. Do not reset,
revert, stage, commit, push, delete another contributor's files or modify live
services. If controlling documents conflict, stop and cite the exact passages.

## Review evidence to reproduce first

Run and record these exact unprivileged checks before editing:

```sh
/opt/discord-bots/venv/bin/python -m pytest -q -rs \
  tests/phase_5_0_evidence tests/test_skills.py tests/test_filesystem_layout.py
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/web/test_p3_4_static_assets.py
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli
git diff --check
```

Codex obtained **599 passed / one dependency warning**, **59 passed**, a dry run
of **64 steps, 39 mutations, 42 cleanup steps and 16 unresolved steps across
C-2 through C-5**, and a clean whitespace check. The submitted digest was
`b709eb20cd58726897cffc5791bd9712ae05d9214961e9957e3bc0cbcde9a344`.
These green results do not close either finding below.

## EH-R6-1 — Blocking: `postgres` credentials are not review-bound

### Defect

R5 introduced `MembershipRule.AS_CONFIGURED` for `postgres`. It passes every
supplementary group currently configured on the host through to the child.
Those memberships are not fixed by the reviewed plan, are not covered by the
canonical §2.12.2 identity table and are not bound into the review-manifest
digest. A host membership change after Codex reviews the digest can therefore
change the credential vector that executes without changing any reviewed byte.

This is not the exact, reviewed, fail-closed identity contract EH-R5-1 required.
That no present evidence case intentionally depends on the groups does not make
an unreviewed authority part of an approved execution identity.

### Required correction

Replace `AS_CONFIGURED` with one explicit review-bound policy:

- add `postgres` to the single canonical identity source used by the evidence
  plan, with its exact primary group and exact permitted supplementary groups;
  or
- introduce a separate explicit reviewed identity record if the governing
  package design requires the PostgreSQL operating-system account to remain
  outside §2.12.2.

Whichever representation is consistent with the controlled design:

- the complete permitted supplementary-group set must be present in repository
  source covered by `ReviewManifest`;
- execution must require exact set equality: missing and unexpected groups both
  refuse before process creation;
- there must be no `AS_CONFIGURED`, pass-through, wildcard, subset-only or
  caller-inherited membership path;
- the manifest must change when the permitted `postgres` identity changes;
- `PERMITTED_RUN_AS`, the identity contract, membership evidence and execution
  credentials must derive from one source or be protected by cross-consistency
  validation that cannot drift;
- do not assume `ssl-cert` merely because it is common on Debian-derived hosts.
  Include it only if the already approved design states it; otherwise identify
  the design gap and stop for a maintainer ruling rather than inventing policy;
- do not read `oracle-test` or the local host to turn current state into policy;
  current state is evidence, not authority; and
- keep all refusals inside the existing fixed safe classification vocabulary.

If the controlled documents genuinely do not decide the exact `postgres`
supplementary set, do **not** select one. Return a precise decision request that
states the available options, security effect and affected artifacts. That is a
valid blocked handback; an inferred allowlist is not.

Required regressions:

- the canonical/reviewed source contains exactly one `postgres` row;
- the execution identity contract derives the `postgres` row from that source;
- the permitted exact set reaches `extra_groups=` as numeric GIDs;
- one missing required group refuses before the process starter is called;
- one unexpected group refuses before the process starter is called;
- the parent process's groups cannot affect the result;
- modifying the reviewed `postgres` group policy changes the review-manifest
  digest; and
- source/contract/evidence drift fails closed.

## EH-R6-2 — Important: identical duplicate account records pass validation

### Defect

`SystemIdentityLookup.account()` builds a set of `(uid, gid)` pairs for matching
account names and refuses only when that set has more than one element. Two or
more matching records with identical UID/GID collapse to one set member and are
accepted, despite the documented contract that a duplicated account record is
ambiguous and must refuse.

The same pattern should be checked for group records: duplicate records must
not become acceptable merely because their numeric values happen to match.

### Required correction

- count matching account records independently of their values and require
  exactly one;
- perform the equivalent exact-one check for named group records;
- ensure the directly returned `getpwnam`/`getgrnam` entry agrees with that sole
  enumerated record, including name and numeric identifiers;
- zero records map to the existing unknown classification;
- multiple records, whether numerically identical or contradictory, map to the
  existing inconsistent classification;
- preserve fixed safe output: no NSS record, UID, GID, group or exception text
  may reach `CommandResult`; and
- keep lookup injectable so tests read no real host account/group database.

Required regressions using mocked `pwd`, `grp` or an injected lower-level
enumerator only:

- exactly one account and group record succeeds;
- two identical account records refuse;
- two contradictory account records refuse;
- two identical group records refuse;
- two contradictory group records refuse;
- a direct-lookup record inconsistent with the sole enumerated record refuses;
- zero matching records refuse safely; and
- no test reads the actual host account/group database or starts a process.

Do not make the fake lookup alone responsible for this property. The tests must
exercise `SystemIdentityLookup`, because that is where R5's collapsing set is.

## Preserve the accepted R5 cleanup correction

EH-R5-2's guaranteed-cleanup structure was materially addressed. Do not rewrite
it as part of this remediation. All R5 cleanup regressions must remain green,
including exception, interruption, cleanup-failure, non-admissibility and
second-invocation refusal paths. Any necessary edit to `executor.py` must be
strictly limited to keeping its identity set derived from the corrected
review-bound source.

## Documentation and generated artifacts

Add a dated **R6 remediation section** at the top of
`docs/review/phase-5-0-evidence-harness-implementation-handback.md`, preserving
R5 and earlier history below it. The R6 section must:

- concede EH-R6-1 and EH-R6-2 before describing corrections;
- record the exact pre-fix checks and results above;
- list every changed file and why;
- state the final exact `postgres` identity source and membership policy;
- explain exact-one NSS account and group resolution;
- map every requirement to named code and tests;
- state that EH-R5-2 was preserved unchanged in substance;
- report only newly run results as current evidence;
- confirm no real process boundary, host account lookup, SSH, privileged or
  mutation-bearing command ran; and
- request Codex independent pre-execution re-review while claiming no finding
  closed and no readiness consequence.

Regenerate the concrete plan and review manifest when their covered inputs
change. Never hand-edit a generated digest. Confirm the regenerated artifacts
are deterministic by producing them twice and comparing bytes. The new digest
is a value for review, never execution authority.

## Scope and safety

Expected changes are limited to:

- `tools/phase_5_0_evidence/execution/boundary.py`;
- the canonical identity source directly required by EH-R6-1;
- `tools/phase_5_0_evidence/execution/executor.py` only if necessary to preserve
  derivation from that source;
- focused tests under `tests/phase_5_0_evidence/`;
- the generated concrete plan and review manifest;
- the implementation handback; and
- `docs/review/Handover information` when returning control to Codex.

Do not alter product application code, bot behavior, migrations, database
schemas, deployment files, infrastructure scripts, roadmap, project status,
RAID, decision register or change log. Stop before widening scope.

Preserve these invariants:

- every test and default CLI invocation starts no harness process;
- the real boundary remains unarmed by default and reachable only through the
  explicit `--execute` branch;
- no socket, HTTP request, database connection, SSH command or external service
  access occurs;
- no arbitrary output, secret, player data or raw exception enters evidence;
- argument vectors remain absolute, shell-free and manifest-covered;
- cleanup remains bounded, derived, non-recursive and guaranteed after a
  potentially reached mutation; and
- all unresolved plan conflicts continue to prevent execution.

## Verification

Run serially against the final tree:

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
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli
git diff --check
```

Run bot and web suites serially because they share the disposable test database.
The web suite must retain exactly 80 expected permission-matrix skips. Report
actual totals, skips and warnings from the final tree; do not reuse prior
figures. Formatter, linter and type checker remain not configured.

Do not invoke `--execute`, instantiate an armed real boundary, run vectors
individually, inspect NSS on a real host, or perform a privileged spot check.
All identity tests must use injected or mocked account/group data.

If the controlled design does not determine the exact `postgres` identity, or
if any focused/full suite fails, do not present R6 as complete. Return the
decision blocker or continue correcting only within this prompt's scope.

## Return to Codex

After verification, make `docs/review/Handover information` begin with a short
current handover stating that R6 is submitted for Codex independent
pre-execution re-review—or that it is blocked on the exact `postgres` policy.
State that no real process boundary, host lookup, SSH, privileged or
mutation-bearing command ran; claim no finding closed; provide the regenerated
digest if one exists; and preserve all superseded history below it.

Then stop. Do not execute the harness, grant execution approval, close a
finding, recommend readiness, change package state or proceed to Package 5.0
implementation.
