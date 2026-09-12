# Claude remediation prompt — project review R3, 2026-09-08

Work in `/opt/freedom-blades/platform`.

## Scope and authority

Remediate the three findings below from Codex's project review. This is a
bounded correction of the backup/restore drill, its recovery documentation,
and the production-file scope guard. Preserve the R1/R2 corrections, the
live-bot skills fix, and the current R13 evidence harness.

These new finding IDs identify this review; they do not replace or close earlier
findings. Package 5.0 remains `not ready`; P5.0-R5 remains Blocking. This prompt
does not authorize product implementation or constitute complete R13
pre-execution approval.

The existing execution restrictions remain binding: no SSH, target-host
inspection or mutation, database operation, destructive drill, `--execute`,
armed real process boundary or materializer, execution of a generated vector,
deployment, migration `0014`, cutover, OD-62 ruling or Package 5.1+ work.
Local synthetic tests using recording boundaries, stub PostgreSQL clients and
temporary Git repositories are permitted. Every PostgreSQL client invoked by
a stub test must remain stubbed; never fall through to a real client.

## Required reading and worktree discipline

Before planning or editing, read completely:

- `.agents/AGENTS.md`, `docs/implementation-plan.md`, and
  `docs/operations/disposable-test-server.md`;
- the current section of `docs/review/Handover information`;
- `docs/review/project-review-remediation-2026-09-07-r2-claude-prompt.md`
  and its R2 handback;
- `docs/review/project-review-remediation-2026-09-07-handback.md`, including
  its execution deviations and undiagnosed pristine-schema drill failure;
- `infra/postgresql/backup-restore-drill.sh`,
  `infra/postgresql/runtime-grants.sql.tmpl`, the recovery section of
  `docs/operations/database-development.md`, and
  `tests/test_database_backup_restore.py`;
- `tests/web/test_p3_4_static_assets.py`, including discovery, parsing,
  allowlists and scope regressions.

Check `git status --short --untracked-files=all`. Preserve unrelated changes
and untracked files. Do not reset, revert, stage, commit, push, reformat unrelated
files or overwrite earlier prompts/handbacks. Expected implementation changes
are confined to the drill, its tests, recovery documentation and scope-guard
test module. Report any necessary expansion before proceeding with it.

## PR-20260908-R3-1 — Blocking: a failed DROP is reported as a known empty database

At review time, `DRILL_STAGE="destroyed"` is assigned before:

```sh
psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 \
     -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;' >/dev/null
```

The `destroyed` banner then asserts that the schema was dropped and the database
is empty, and directs a full restore. Failure to execute the command, refusal of
DROP, or an uncertain client outcome does not establish that assertion.

Codex reproduced this using the existing stub helper, modifying only the stub's
DROP branch to emit a fixed error and exit 42 without changing its state file.
The real drill exited 42, never called `pg_restore`, but its recovery banner
claimed `database is EMPTY` and prescribed `4. pg_restore ...`. This was a stub
reproduction, not a PostgreSQL execution.

Required correction:

1. Distinguish destruction attempted/outcome unknown from destruction confirmed.
   Record responsibility before starting the command, but advance to a known
   destroyed state only after success. Moving the assignment after the command
   without an attempted state is insufficient: a lost client result must not be
   treated as proof that nothing happened.
2. For an uncertain destruction outcome, require safe state inspection before
   choosing recovery. Account for an intact schema, an empty recreated schema,
   an absent schema and an unexpected state. A row-count match alone does not
   distinguish every schema state, especially when the original database has
   no tables. Query failure is unknown, never evidence of emptiness.
3. Do not prescribe a full restore over known existing objects or introduce an
   unconditional DROP, `--clean`, TRUNCATE or other destructive reset. State
   when an operator must resolve uncertainty instead of choosing a mutation.
4. Preserve the current post-restore resume points, both final verifications,
   checksummed pre-destruction artifacts, exact runtime role and explicit
   zero-role behavior. A confirmed restore must not be repeated during grant
   recovery.
5. Extend the stub boundary to model DROP refusal with state intact and an
   uncertain outcome, alongside successful destruction. Assert emitted recovery
   order and state claims, not merely that a banner exists. Replace the current
   test assertion that makes pre-command `destroyed` assignment mandatory.
6. Update the operational recovery table and instructions to match. Any new
   database-semantic regression may be written for a later authorized run but
   must not be executed here.

Acceptance: no failed or uncertain destructive command is described as proven
empty, and recovery never recommends a mutation based on that false premise.

## PR-20260908-R3-2 — Important: hex decoding drops NUL bytes and accepts malformed transport

`decode_hex_role()` uses `printf -v piece '%b'` and accumulates bytes in Bash
strings. Bash cannot retain NUL bytes, so a transported `00` vanishes before
the supported-name guard runs.

Codex supplied this exact report through `report_override`:

```text
ROLE 66726565646f6d5f72756e74696d655f7465737400
END 1
```

It encodes `freedom_runtime_test` followed by NUL. The drill exited 0 and reached
both DROP and restore in the stub log. The valid role control also exited 0;
the newline-bearing role control correctly refused with exit 2 before DROP.

PostgreSQL cannot store a NUL-bearing role name. This is a malformed-transport
defect, not a claim that a legitimate catalog role contains NUL. R2 explicitly
requires unreadable/malformed transport to refuse without identity repair.

Required correction:

1. Reject NUL-containing encoded records before decoding into a representation
   that cannot preserve them. Inspect complete byte pairs; a raw substring
   search for `00` can misclassify a sequence crossing a byte boundary.
2. Keep exact identity, cardinality, terminator and supported-role validation.
   Do not trim, coerce, normalize or broaden supported SQL role names.
3. Refuse with exit 2 before DROP/restore and without rendering runtime grants.
   Use fixed safe diagnostics containing no arbitrary report bytes.
4. Add regressions for leading, trailing, embedded, repeated and NUL-only
   encodings, and a valid record alongside a malformed record. Include a
   byte-boundary control for the detector and preserve valid zero-role,
   `freedom_runtime` and `freedom_runtime_test` cases, newline/multiple-role
   refusals, malformed report handling and client failure handling.
5. Keep the evidence distinction explicit: stub tests establish transport and
   pre-destruction behavior; they do not establish SQL semantics. Do not add a
   PostgreSQL test purporting to create a NUL-bearing role.

Acceptance: an impossible NUL-bearing report cannot become an accepted role
through lossy decoding, while previously supported inputs retain their behavior.

## PR-20260908-R3-3 — Important: human-readable Git parsing hides watched files

`status_paths()` treats every ` -> ` substring as a rename separator, regardless
of the status. Such a substring is legal in an ordinary filename.

Codex created a temporary synthetic Git repository containing the untracked file
`tools/extra -> outside.py`. Calling the actual `working_tree_paths()` produced
`['outside.py']`; `scope_violation()` returned `None`. The normal control
`tools/extra.py` was correctly rejected as an unpermitted tools modification.

Required correction:

1. Use explicit machine-readable porcelain output with NUL-delimited records
   and `--untracked-files=all`. Parse status fields and the documented rename/
   copy record format; do not split filenames on arrows, newlines or whitespace,
   strip quote characters, or treat display escaping as a filename.
2. Preserve the actual paths for modified, added, deleted, untracked, renamed
   and copied entries. For renames, inspect both endpoints so moving a watched
   production source outside a watched prefix cannot conceal its removal.
   Handle copy records explicitly as well. Refuse malformed/truncated status
   records rather than silently dropping them.
3. Preserve the exact file allowlists, separate maintenance/package scopes,
   watched prefixes and current submitted-file coverage. Do not solve parsing
   failures by broadening an allowlist or ignoring unusual names.
4. Add end-to-end discovery/classification regressions in temporary synthetic
   Git repositories for literal ` -> `, spaces, quotes, tabs, newlines and
   non-ASCII filenames; normal tracked edits/deletions; actual renames into,
   within and out of watched areas; and nested untracked files. Exercise copy
   and malformed record parsing with fixtures where Git detection would be
   nondeterministic. Do not add synthetic unauthorized files to this worktree.
5. Prove that the actual reviewed file set still passes and an undeclared file
   in the same package fails. Update parser consumers and existing tests so no
   old human-readable parsing path remains in production-scope discovery.

Acceptance: discovery/classification cannot change the scope of a file by
misinterpreting its name or omitting a rename endpoint.

## Verification constraints

Add regression tests first and record actual pre-fix failures. Run permitted
focused checks serially against the final tree. Inspect fixtures before choosing
tests: do not launch a broad suite and hope to stop before database access.

The repository is `/opt/freedom-blades/platform`; the documented Python test
environment is on `oracle-test` at
`/opt/freedom-blades/runtime/venv-web/bin/python`. The no-SSH restriction prevents
using that environment under this prompt. Codex found no pytest in local
`/usr/bin/python3`. Do not infer availability from historical handbacks, copy
historical `/opt/discord-bots/` paths as the default, or install into production
runtimes. If a permitted local test environment is unavailable, finish the
correction and available static/synthetic checks and report that dependency.

Permitted checks include stub-only drill tests, temporary-Git scope tests,
affected filesystem/static tests after confirming they do not touch a database,
synthetic evidence-harness tests using recording boundaries, Foundry Node tests,
shell syntax, Python compilation and diff whitespace checks. Report configured
lint/format/type tools that are absent or unavailable; do not introduce tools to
claim a pass.

Exclude every database-touching test, including the eleven cases identified in
the R2 handback and any newly added integration case. List exclusions by name.
The undiagnosed pristine-schema drill failure remains unresolved operational
evidence; do not rerun it or claim stub success diagnoses it. Full bot/web
database suites and disposable-server drills need a later authorized run.

Codex's review evidence was limited to eleven stub scenarios, a temporary-Git
filename reproduction, 28 matching source hashes, 171 passing Foundry tests,
shell syntax and diff whitespace checks. Full Python/PostgreSQL suites were
not run. None of these figures is evidence for your changed tree.

No evidence-harness production source needs changing. Verify every manifest
source hash; if covered sources remain unchanged, leave generated artifacts
untouched. If a covered-source change becomes necessary, explain the scope
dependency first, use the existing inert generator, compare two generations
byte-for-byte and independently re-hash sources. Never hand-edit generated
artifacts or pass a digest to `--execute`. Leave all unconfirmed interpreter and
E7 target facts unconfirmed.

## Handback

Create `docs/review/project-review-remediation-2026-09-08-r3-handback.md` with:

- each finding, changed files, correction and remaining limitations;
- actual pre-fix failures and final-tree verification commands/results;
- destruction-attempt/completion states and exact recovery instructions;
- strict transport handling and pre-destruction refusal evidence;
- machine-readable Git parsing and discovery-through-classification evidence;
- passed, skipped, deselected and not-run checks, interpreters and reasons;
- manifest hash verification or justified regeneration evidence;
- confirmation that unrelated changes and execution restrictions were preserved.

Prepend a concise dated pointer to the handback in
`docs/review/Handover information`, retaining prior submissions as history.
Do not alter roadmap, RAID, decision or gate records, close findings, accept
risks or claim complete R13 approval. Return to Codex for independent re-review
and stop before operational execution.
