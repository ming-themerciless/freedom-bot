# Claude prompt — agent-client bootstrap remediation and acceptance audit

Work ID: `C-P5.0-ORACLE-AGENT-CLIENT-BOOTSTRAP-R1-20261005-02`

Date: 2026-10-05

## Authority and outcome

Peter Duscha authorizes Claude Code to perform this bounded remediation and
acceptance audit on the disposable test server reached through the SSH alias
`oracle-test`. The machine's approved kernel nodename is `Test`; the alias and
nodename are intentionally different.

Claude may run on the current workspace host and control only `oracle-test`
over SSH for this assignment. It may inspect the prior bootstrap installation
and retained evidence, remove only the verified empty Gemini temporary state
defined below, and write only the new evidence directory. It must not reinstall,
update, authenticate, run H-0, or begin any later work.

The required outcome is exactly one terminal state: `REMEDIATION PASS` or
`HARD STOP`.

## Fixed inputs

- SSH target: `oracle-test`
- remote account: `ubuntu`
- expected `uname -n`: `Test`
- installed prefix: `/opt/freedom-blades/agent-tools`
- Claude command: `/usr/local/bin/claude`
- Gemini command: `/usr/local/bin/gemini`
- expected Claude package/version: `@anthropic-ai/claude-code@2.1.285`
- expected Gemini package/version: `@google/gemini-cli@0.62.0`
- original evidence:
  `/var/tmp/p5-agent-client-bootstrap-20261005-01-evidence`
- new evidence:
  `/var/tmp/p5-agent-client-bootstrap-20261005-02-remediation-evidence`
- Gemini state directory: `/home/ubuntu/.gemini`
- permitted Gemini temporary-name grammar: `projects.json.*.tmp`
- permitted Gemini temporary-file content: exactly 20 bytes of valid UTF-8 JSON
  whose root object has the sole key `projects` and whose value is an empty
  object

Do not substitute any input.

## Absolute boundaries

1. Do not inspect or modify `/opt/freedom-blades/platform` on `oracle-test`.
2. Do not install, reinstall, update, downgrade, migrate, or self-update either
   client, Node.js, npm, or any package. Do not use `npm install`, `npm update`,
   `claude update`, or an interactive client command.
3. Do not authenticate or inspect, create, transfer, print, or delete any
   credential, token, key, npm configuration, shell history, SSH material, or
   model-provider account state.
4. Do not run H-0, H-1/H-2, tests, builds, services, databases, activation,
   package-manager mutation, OS-package commands, or repository commands.
5. Do not alter the original evidence directory. It is read-only input.
6. Apart from the new evidence directory, the only deletion authorized is the
   exact verified Gemini cleanup in Phase C. No wildcard deletion command,
   recursive deletion, unrelated home inspection, or general cleanup is
   authorized.
7. Do not retry or repair a failed prerequisite. Preserve new evidence and
   stop at the first `HARD STOP` condition.

## Evidence rules

Confirm the new evidence path does not exist using non-following metadata, then
create it once as `ubuntu:ubuntu` mode `0700`. Record every command in execution
order, its exact exit status, and raw stdout/stderr. Record UTC start/end times,
work ID, fixed inputs, identity, and every decision. Never record an environment
dump or secret.

Each evidence file must be created without overwriting an existing name. The
final manifest must avoid self-reference: first inventory and hash all closed
evidence payload files into `MANIFEST.payload`, then record that file's SHA-256
and byte length in `MANIFEST.final`. `MANIFEST.final` must not claim to include
or hash itself. Report both files' SHA-256 and byte lengths.

## Phase A — identity and unchanged installation audit

1. Verify remotely that `id -un` is `ubuntu` and `uname -n` is exactly `Test`.
   Otherwise `HARD STOP` before mutation.
2. Confirm the new evidence path does not exist, then create it as specified.
3. Record Node.js and npm versions and paths. They must remain Node.js 22.x at
   `/usr/bin/node` and npm 10.x at `/usr/bin/npm`.
4. Without launching an interactive session, record `command -v`, non-following
   metadata, full resolved target chain, SHA-256, and byte length for both fixed
   client commands. Record `claude --version`. Do **not** execute Gemini: its
   prior `--version` invocation is the known source of the state being
   remediated. Establish Gemini's version from the installed npm package
   metadata and the original retained evidence instead. Every symlink target
   must remain inside the installed prefix; no chain member may be group- or
   world-writable.
5. Record prefix ownership/modes and verify every entry is owned by `ubuntu`
   and none is group- or world-writable.
6. Run the read-only npm global inventory against the explicit prefix and
   require exactly the expected package versions for the two clients. Do not
   query the network.

Any mismatch is a `HARD STOP`; do not reinstall or repair it.

## Phase B — original evidence audit

1. Verify the original evidence path is a real directory owned by `ubuntu`,
   mode `0700`, and not a symlink.
2. Inventory it without following links. Any symlink, non-regular payload,
   group/world writable entry, or unexpected ownership is a `HARD STOP`.
3. Verify `MANIFEST.sha256` itself against the handback value
   `6e8d84c80d36f03743667747a017794e28f7fbc4eae4fcc3d601eb2a511a6828`
   and byte length `7620`.
4. Parse its recorded inventory, reject duplicate or unsafe pathnames, and
   independently verify every recorded payload SHA-256 and byte length against
   the retained files. Do not trust or use the acknowledged self-referential
   `evidence_total_bytes` value as an integrity check.
5. Compute and record an independent total of the closed payload files named by
   `MANIFEST.sha256`, clearly defining which files are included. This is a new
   audit observation and must not modify the original evidence.

Any missing file, digest/length mismatch, unsafe name, or unverifiable manifest
is a `HARD STOP`.

## Phase C — exact Gemini temporary-state remediation

1. Inspect only `/home/ubuntu/.gemini` itself and its direct children without
   following links. Require:
   - the directory is a real `ubuntu:ubuntu` directory with mode `0700`;
   - it contains exactly two direct children;
   - both are regular `ubuntu:ubuntu` files, not links;
   - both names match `projects.json.*.tmp`;
   - both are mode `0600` or stricter; and
   - each file is exactly 20 bytes and parses as the fixed permitted JSON value,
     with no duplicate key, trailing non-whitespace content, or other value.
2. Record each exact basename, metadata, byte length and SHA-256 in the new
   evidence. Do not print file contents in the handback.
3. If and only if every condition above holds, delete the two files by their
   individually validated literal absolute paths. Do not use a glob in the
   deletion command.
4. Remove `/home/ubuntu/.gemini` using non-recursive `rmdir`, which must succeed
   only because the directory is empty.
5. Verify with non-following metadata that the directory and the two literal
   paths are absent.

If any condition differs, `HARD STOP` without deleting anything. If a deletion
or `rmdir` fails, `HARD STOP` without retry or broader cleanup.

## Phase D — post-remediation verification

Repeat the client path, target-chain, package-version and permissions checks
from Phase A, but do **not** execute either client again: their versions were
already captured before cleanup, and `gemini --version` is the known source of
the state being remediated. Verify that `/home/ubuntu/.gemini` remains absent.

Confirm from the command record that no authentication, credential operation,
installation, update, repository access, service/database operation, H-0, or
unapproved cleanup occurred.

## Terminal handback

### `REMEDIATION PASS`

Use only if every audit passed, the exact temporary files and empty directory
were removed once, they remained absent, and the new manifest is complete.
Return:

- observed account, SSH alias and kernel nodename;
- both exact client versions, paths, target chains and package versions;
- original evidence verification result and independently computed payload
  total;
- the two removed basenames, metadata, lengths and digests;
- confirmation that `/home/ubuntu/.gemini` remains absent;
- every exact command and exit status;
- new evidence path plus `MANIFEST.payload` and `MANIFEST.final` digests and
  lengths;
- checks not run and deviations;
- confirmation that no authentication, credential, installation, update,
  repository, service/database, or H-0 action occurred; and
- the statement: `Bootstrap remediation passed; client authentication and H-0
  remain unauthorized pending separate assignments.`

### `HARD STOP`

Return the first failed step, exact error, all changes made, whether either
temporary file or directory was removed, retained evidence details, and the
smallest decision needed. Do not retry, reinstall, authenticate, repair, or
clean up.
