# Claude remediation prompt — Package 5.0 evidence harness pre-execution R8 and backup-drill ambiguity guard

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Codex independently reviewed the current R7 working tree and found two material
defects:

1. **EH-R8-1 — Blocking:** the new `postgres` group inverse conflates an
   account's primary group with the explicit member list returned in the fourth
   field of `getent group`. This can make `JNL-52-GROUP-postgres` fail on a host
   whose approved credential is configured correctly.
2. **DS-R8-1 — Important:** the database backup/restore drill removes all
   whitespace from the runtime-role query result before testing for a newline,
   so its multiple-role ambiguity guard is unreachable.

Remediate only these findings and their directly necessary tests, controlled
documentation, generated review artifacts and handback records. Treat them as
two independently authorized maintenance slices: EH-R8-1 is evidence-harness
pre-execution remediation; DS-R8-1 is a backup-drill correctness repair. Do not
use either slice to widen the other.

This prompt does **not** authorize `--execute`, an armed real
`SubprocessBoundary`, execution of a generated vector, SSH, host account/group
inspection, privileged or mutation-bearing commands, mutation of
`oracle-test`, execution of the destructive backup drill, Package 5.0 product
implementation, migration `0014`, production or staging mutation, deployment,
cutover, OD-62's binding ruling, or Package 5.1+. Package 5.0 remains `not
ready`; P5.0-R5 remains Blocking.

## Required reading and worktree discipline

Before planning or editing, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/operations/disposable-test-server.md`;
4. `docs/review/Handover information`;
5. this prompt, the R7 prompt and the current R7 implementation handback;
6. the evidence-harness authorization and implementation prompts;
7. package-plan §2.12.2, the generated concrete plan and review manifest;
8. `tools/phase_5_0_evidence/` and `tests/phase_5_0_evidence/` in full; and
9. `infra/postgresql/backup-restore-drill.sh`, its operations documentation and
   `tests/test_database_backup_restore.py` in full.

Run `git status` first and preserve the complete dirty worktree. Do not reset,
revert, stage, commit, push, delete another contributor's files or modify live
services. If a requested correction conflicts with a controlled ruling, stop
and cite the exact passages rather than choosing silently.

## Review evidence to preserve

Codex ran the following against R7 without executing the harness or the
backup/restore drill:

```sh
/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/test_skills.py tests/test_filesystem_layout.py
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
git diff --check
```

Results: **623 passed** in the focused selection; bot **3135 passed** with one
pre-existing `audioop` deprecation warning; web **2840 passed / 80 expected
skips**; and a clean whitespace check. Green tests do not close either finding.

The R7 digest `15e131bfdce8fa8366aa97f19e233c249de4f1855492edac9a6fa4d758dcf176`
is superseded by any covered-source edit and must never be passed to
`--execute`.

## EH-R8-1 — Blocking: the group inverse models primary membership incorrectly

### Defect

The controlled identity row correctly states:

- account: `postgres`;
- primary group: `postgres`; and
- complete supplementary-group set: exactly `ssl-cert`.

R7 then added `CanonicalGroup("postgres", {"postgres"})` and made the import
guard require inverse rows for `account.supplementary | {account.primary_group}`.
But `ObservedGroup.members` is expressly the fourth field of `getent group`.
That field represents explicit group-list membership; an account's primary
membership comes from its passwd record and normally does not appear there.
The account-side `id` evidence already checks the primary group independently.

The implementation therefore turns the ruled fact *"primary group is
postgres"* into a different, unruled fact *"the postgres group explicitly lists
postgres as a member"*. A correctly configured host may fail
`JNL-52-GROUP-postgres`, so the positive PostgreSQL evidence remains blocked.

### Required correction

1. Preserve the maintainer's R7 ruling exactly: primary group `postgres`,
   supplementary set exactly `ssl-cert`. Do not seek or infer a new membership
   ruling.
2. Define the semantics of the inverse group table precisely. If it models the
   `getent group` fourth field, it must contain explicit members only and must
   not manufacture primary membership.
3. Remove the false requirement that the `postgres` primary-group row list the
   `postgres` account explicitly. Either represent the `postgres` group with
   the correct explicit-member set required by the controlled design, or omit
   that inverse row if primary groups are intentionally outside the inverse;
   choose the smallest representation consistent with the existing table's
   stated semantics.
4. Change the import-time consistency guard so it verifies the ruled
   supplementary membership in both directions without unioning the primary
   group into the explicit-member relation. Continue to verify the primary
   group through the account row and account-identity classifier.
5. Keep `ssl-cert -> postgres` exact if that is the explicit membership implied
   by the ruled supplementary set. A missing or unexpected supplementary group
   must still refuse before process creation.
6. Audit the other canonical rows for this same representation error. Do not
   silently change their policy. If pre-existing rows also conflate primary and
   explicit membership, report them with exact impact and stop before widening
   the remediation unless correcting them is mechanically required to make the
   single table internally truthful.
7. Preserve `MembershipRule.EXACT`, the fixed safe `LAUNCH_FAILURES`
   vocabulary, review-manifest binding, R5 guaranteed cleanup, and R6 exact-one
   NSS lookup behavior.

### Required regressions

Add or update focused tests proving:

- the account row still has primary group `postgres` and supplementary set
  exactly `ssl-cert`;
- the group inverse does not treat primary membership as an explicit
  `getent group` member;
- `ssl-cert` explicitly lists `postgres` exactly once;
- an observed `postgres` group with no explicit members is not rejected merely
  because `postgres` has that primary group, if that row remains classified;
- the account-side classifier still rejects a primary group other than
  `postgres`;
- the import-time guard fails when `ssl-cert` omits `postgres` or when the
  account supplementary set and inverse disagree;
- a missing or unexpected observed supplementary group still refuses before a
  process is started;
- the corrected policy remains covered by the review-manifest digest; and
- no test reads the real host account/group database or starts a process.

Do not weaken a test merely to accept both the old and corrected
representations.

## DS-R8-1 — Important: the multiple-runtime-role guard is unreachable

### Defect

`detect_runtime_role` may return multiple newline-separated grantees. The
script currently assigns its result through `tr -d '[:space:]'` and only then
tests `RUNTIME_ROLE` for a newline. Because the newline has already been
deleted, that ambiguity branch can never run. Two roles become one concatenated
identifier and the drill may proceed into its destructive restore cycle before
grant reapplication fails.

### Required correction

1. Preserve record boundaries while determining whether the query returned
   zero, one or more than one non-owner runtime role.
2. Refuse with exit status 2 **before `SCHEMA_DROPPED=1` and before the schema is
   dropped** when more than one distinct row is returned.
3. Only after establishing exactly one row, extract and validate the role name.
   Do not strip internal characters or concatenate records.
4. Keep zero rows as the documented no-runtime-role path.
5. Keep the query non-interactive and do not interpolate an unvalidated role
   into `sed` or SQL. Use PostgreSQL-safe identifier handling or a narrowly
   justified validation rule consistent with supported runtime-role names.
6. Preserve the schema-owner/ACL artifact and checksum remediation already in
   the dirty tree; do not revert or redesign it.
7. Do not run the destructive drill under this prompt. Exercise behavior using
   a non-destructive fake/stubbed script boundary or another focused test that
   proves the refusal occurs before the destructive command.

### Required regressions

Tests must prove:

- zero detected roles follows the existing empty path;
- one role is retained exactly and reaches the existing grant-reapplication
  path;
- two distinct roles refuse with exit status 2;
- the multiple-role refusal occurs before `DROP SCHEMA`;
- whitespace removal cannot concatenate two records into an accepted role;
- a malformed or unsupported role name refuses before destructive work or SQL
  interpolation; and
- the existing schema ownership, ACL, checksum and recovery-instruction tests
  remain unchanged in substance and green.

## Documentation, generated artifacts and handback

Add a dated **R8 remediation section** at the top of
`docs/review/phase-5-0-evidence-harness-implementation-handback.md`, preserving
R7 and earlier history. Clearly separate EH-R8-1 from DS-R8-1. It must:

- concede both findings before describing their corrections;
- explain primary versus explicit/supplementary membership;
- state the final inverse-table semantics and list every affected canonical row;
- explain how runtime-role cardinality is preserved and where refusal occurs;
- list every changed file and why;
- map every requirement above to named code and tests;
- report only checks actually run against the final R8 tree;
- state that no real boundary, generated vector, host lookup, SSH, privileged
  command, database operation or destructive drill ran; and
- return R8 to Codex for independent re-review, claiming no finding, readiness
  item, assumption, operational check or gate closed.

Regenerate the evidence-harness concrete plan and review manifest if any covered
source changes. Generate each twice and compare bytes. Never hand-edit a
generated artifact or pass its digest to `--execute`. Update
`docs/review/Handover information` so R8 is the current handover while preserving
all previous handovers below it.

Expected changes are limited to:

- package-plan §2.12.2 only where necessary to correct inverse-table semantics;
- `tools/phase_5_0_evidence/identity.py`;
- focused tests under `tests/phase_5_0_evidence/`;
- `infra/postgresql/backup-restore-drill.sh`;
- `tests/test_database_backup_restore.py`;
- directly corresponding operations documentation if its contract changes;
- regenerated concrete-plan and review-manifest artifacts when required;
- the implementation handback; and
- `docs/review/Handover information`.

Do not alter product application code, bot behavior, migrations, database
schema, deployment files, roadmap, project status, RAID, unrelated decisions or
the accepted `postgres` supplementary-group ruling. Stop before scope widens.

## Verification and stop point

Run serially against the final tree:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m pytest -q -rs \
  tests/test_database_backup_restore.py tests/test_filesystem_layout.py
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

Do not run the backup/restore drill itself merely because its test module
contains integration tests. If the focused test command would execute the real
destructive drill against a database, select or add the non-destructive tests
needed for DS-R8-1 and report the integration cases as **not run by authority**.
Do not skip tests silently.

Report exact pass, fail and skip counts. The CLI must remain a dry run and must
report `executable: False` while conflicts remain. Do not pass `--execute`, a
confirmation token or a reviewed digest. Then stop and return the tree to Codex.
No R8 result authorizes harness execution, privileged evidence gathering or a
Package 5.0 gate movement.
