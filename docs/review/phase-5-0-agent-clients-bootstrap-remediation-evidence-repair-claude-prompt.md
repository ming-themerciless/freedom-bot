# Claude prompt — bootstrap-remediation retained-evidence repair

Status: **active assignment authorized by Peter Duscha on 2026-10-05**

Date: 2026-10-05

## Purpose

Audit the retained evidence from work ID
`C-P5.0-ORACLE-AGENT-CLIENT-BOOTSTRAP-R1-20261005-02` and produce a complete,
literal corrected handback. This assignment repairs the reporting record only.
It does not repeat, extend or retroactively alter the bootstrap remediation.

The prior handback cannot presently be accepted because it omitted exact command
texts, contains truncated or malformed identifiers and manifest values, appears
to give both deleted files the same inode despite reporting a link count of one,
and acknowledges that record 001 has no captured end time. Those facts must be
resolved from retained bytes where possible and reported as defects where they
are not recoverable. Never invent, estimate or reconstruct missing evidence.

## Activation and fixed inputs

Peter Duscha explicitly authorized this exact bounded assignment on 2026-10-05.
The authority is recorded in
[`project-review-2026-10-05-agent-client-bootstrap-evidence-repair-authority.md`](project-review-2026-10-05-agent-client-bootstrap-evidence-repair-authority.md).

- Work ID: `C-P5.0-ORACLE-AGENT-CLIENT-BOOTSTRAP-R1-20261005-03`
- SSH target: `oracle-test`
- expected remote account: `ubuntu`
- expected kernel nodename: `Test`
- original installation evidence:
  `/var/tmp/p5-agent-client-bootstrap-20261005-01-evidence`
- remediation evidence under audit:
  `/var/tmp/p5-agent-client-bootstrap-20261005-02-remediation-evidence`
- new repair evidence:
  `/var/tmp/p5-agent-client-bootstrap-20261005-03-handback-repair-evidence`
- installed prefix, for identification only:
  `/opt/freedom-blades/agent-tools`
- Gemini state path, for absence metadata only: `/home/ubuntu/.gemini`

Do not substitute any path, host, account or nodename.

## Authority and absolute boundaries

Claude may run on the current workspace host and control only `oracle-test`
over SSH for this assignment. On `oracle-test`, it may:

1. verify `id -un` and `uname -n`;
2. inspect without following links the three fixed evidence paths and the
   non-following metadata or absence of `/home/ubuntu/.gemini` and the two
   literal deleted paths learned from retained evidence; and
3. create and write only the new repair-evidence directory.

Everything else is forbidden:

- Do not run Claude Code or Gemini CLI on `oracle-test`, including `--version`.
- Do not inspect the installed prefix, `/usr/local/bin/claude`, or
  `/usr/local/bin/gemini`; their recorded observations are evidence inputs, not
  facts to refresh.
- Do not rerun any original bootstrap or remediation command.
- Do not create, modify, chmod, touch, rename or delete anything in either
  retained evidence directory.
- Do not create, modify or remove `/home/ubuntu/.gemini` or either former
  temporary path. Only non-following absence metadata is permitted.
- Do not access `/opt/freedom-blades/platform` on `oracle-test`.
- Do not authenticate a client or inspect credentials, tokens, keys, npm
  configuration, shell history, SSH material, environment dumps or provider
  account state.
- Do not use `sudo`, a package manager, Git, a repository command, a network
  retrieval, a service, a database, a build, a test suite, H-0, H-1/H-2,
  activation, rollback or cleanup.
- Do not modify the production workspace repository during execution. Return
  the handback in chat; a maintainer will decide whether to record it.
- Do not retry or repair a failed prerequisite. Preserve the new repair
  evidence and stop at the first `HARD STOP` condition.

This assignment does not activate H-0. The task-specific current handover
controls over any broader or inconsistent current-state wording.

## Evidence discipline

First verify identity. Then confirm with non-following metadata that the new
repair-evidence path is absent. Create it exactly once as `ubuntu:ubuntu` mode
`0700`, set `umask 077` before creating any evidence file, and require every
new evidence file to be a regular `ubuntu:ubuntu` file with mode `0600` and a
fresh exclusive name.

Record every command executed by this repair assignment with:

- a monotonically increasing record number;
- its exact command text;
- UTC start and end timestamps captured by the recording mechanism;
- raw stdout and stderr kept distinct; and
- exact exit status.

Do not place file contents in shell arguments, command substitutions or an
environment dump. Do not print retained payload indiscriminately. Read and
quote only the bounded records needed for the required audit, and redact
nothing silently. A suspected secret is a `HARD STOP`: record only the record
name and reason, never the suspected value.

Finish the new evidence without self-reference:

1. close every repair payload file;
2. inventory those files into `MANIFEST.payload`, recording safe relative name,
   SHA-256 and byte length;
3. record only `MANIFEST.payload`'s SHA-256 and byte length in
   `MANIFEST.final`; and
4. do not claim that `MANIFEST.final` hashes or includes itself.

## Phase A — retained-evidence integrity

1. Require both retained evidence paths to be real `ubuntu:ubuntu`
   directories, mode `0700`, and not links.
2. Inventory each retained directory without following links. Reject a link,
   special file, unsafe relative name or ownership mismatch. Reject a
   group/world-writable regular file except for remediation record files that
   are exactly mode `0664` inside the real mode-`0700` remediation directory.
   That reported condition is an evidence nonconformance to preserve and
   report, not a fact to conceal or repair; it does not prevent this bounded
   read-only audit. Do not call the original evidence fully
   permission-conforming.
3. Recompute the original `MANIFEST.sha256` digest and length and verify its
   complete inventory exactly as required by the original remediation prompt.
4. Recompute `MANIFEST.payload` and `MANIFEST.final` digests and lengths from
   the remediation evidence. Parse `MANIFEST.final` strictly and verify that it
   names the actual digest and length of `MANIFEST.payload` and nothing else.
5. Independently verify every safe entry named by each manifest. Record exact
   inclusion rules and independently computed byte totals. Never use the
   original self-referential `evidence_total_bytes` value as an integrity
   check.

A digest, length, inventory, ownership or parse mismatch is a `HARD STOP`.

## Phase B — literal record reconstruction

From the retained remediation evidence only:

1. identify the canonical record index and all records it names;
2. extract every original command's exact command text and exact exit status;
3. extract each captured UTC start and end time without normalization;
4. identify records written directly rather than produced by a command;
5. recover the complete new-evidence path and the full SHA-256 and byte length
   of both remediation manifests;
6. recover the exact original-evidence directory metadata, manifest facts,
   verified entry count and independently computed totals;
7. recover the complete paths, basenames, device/inode values, owners, groups,
   modes, link counts, byte lengths and SHA-256 digests of the two deleted
   Gemini files; and
8. recover the recorded client paths, complete target chains, target metadata,
   target digests and lengths, client/package versions, Node/npm facts, prefix
   counts and post-remediation comparison results.

Use literal values. Do not silently fix spelling, interpolate truncated text,
or merge fields based on how the prior chat rendering appeared.

### Mandatory discrepancy decisions

- If record 001 truly lacks an end timestamp, state `not captured` and identify
  the original evidence-rule violation. Filesystem timestamps, later record
  times and elapsed-time guesses are not substitutes.
- If both deleted files have the same inode while each has link count one on
  the same device, classify the retained evidence as internally contradictory
  and `HARD STOP`. If the apparent equality was only a damaged handback table,
  print the two distinct retained values and say so explicitly.
- If any exact command text is absent from retained evidence, name that command
  record and classify it as unrecoverable. Do not paraphrase it as exact.
- If any required handback field is absent, report it as absent. Absence is not
  permission to rerun a command.

## Phase C — bounded state confirmation

Using only non-following metadata operations:

1. verify that `/home/ubuntu/.gemini` is absent; and
2. verify that the two literal paths recovered from retained evidence are
   absent.

Do not inspect any other home entry. A present path is a `HARD STOP`; do not
remove or inspect its contents.

## Terminal outcomes

### `EVIDENCE REPAIR COMPLETE`

Use this outcome only when retained-manifest integrity passes, the apparent
inode contradiction is resolved from retained bytes, every recoverable field
has been transcribed literally, and the bounded paths remain absent.

This outcome means the repair audit completed. It does **not** erase the
original procedural nonconformances or by itself accept the earlier
`REMEDIATION PASS`.

Return, in this order:

1. identity, work ID and UTC audit interval;
2. retained-evidence integrity results and exact independent totals;
3. every exact original command, in execution order, with its original exit
   status and captured start/end times;
4. an explicit list of original commands or time fields that were never
   captured, including record 001's end time if absent;
5. all complete client, prefix, original-evidence, deletion and post-check
   facts required by the original terminal handback;
6. a side-by-side resolution of every truncated, malformed or contradictory
   field in the prior handback;
7. explicit confirmation that the Gemini directory and two literal paths
   remain absent;
8. every command run by this repair assignment and its exit status;
9. the new repair-evidence path and full SHA-256 and byte length of
   `MANIFEST.payload` and `MANIFEST.final`;
10. checks not run, deviations and every still-unrecoverable defect;
11. a disposition of the original handback as one of:
    - `substantive remediation facts verified; original evidence procedure was
      nonconforming`, or
    - `original remediation result not supportable from retained evidence`;
12. confirmation that no client, credential, installation, update, repository,
    service/database, H-0 or cleanup action occurred; and
13. the statement: `Evidence repair completed; H-0 remains unauthorized
    pending a separately recorded assignment.`

Do not use `REMEDIATION PASS` as this assignment's terminal label.

### `HARD STOP`

Use this outcome at the first integrity failure, identity/path mismatch,
present bounded path, suspected secret, unresolved inode/link-count
contradiction, unsafe retained entry, or boundary failure. Return the precise
failed step, exact safe error, all changes made, whether the new directory was
created, retained evidence details that remain trustworthy, and the smallest
maintainer decision needed. Do not retry, repair, rerun, delete or begin H-0.
