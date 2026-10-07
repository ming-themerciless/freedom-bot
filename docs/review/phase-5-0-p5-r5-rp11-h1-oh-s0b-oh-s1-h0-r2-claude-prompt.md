# Claude prompt — controller-launched public retrieval and H-0 fact collection

Status: **withdrawn unused and superseded by R3 on 2026-10-05**

Do not execute this prompt or use its work ID or evidence path.

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R2-20261005-05`

## Invocation

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r2-claude-prompt.md. Proceed autonomously through every authorized step in order until the defined terminal state (H-0 PASS or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

## Controller bootstrap

A Claude Code process in the production workspace may act only as the launch
controller. It may use the already configured SSH route to `oracle-test` to
start and interactively drive a Claude Code process there as `ubuntu`, transmit
this invocation and exact prompt/authority text, and receive terminal output
and the final handback.

For this bootstrap only, the R2 authority supersedes OH-D-2's prohibition on a
scripted remote controller and the production-isolation table's controller/
relay row. All other accepted-design restrictions remain in force. The login
transport remains outside the trusted execution path.

The controller must not transfer repository or implementation bytes, forward
an SSH agent or environment, read or copy any key, token or model-provider
credential, run any Phase A, B or C observation through SSH, write evidence,
or use the production workspace as a retrieval source, execution host,
destination, fallback or rollback target. If a remote Claude client cannot be
started using its already available installation and authentication, `HARD
STOP`; do not install, authenticate, copy credentials or fall back to remote
shell execution of the assignment.

After launch, the remote Claude process is the sole assignment executor. It
must run locally on `oracle-test` as `ubuntu`; all retrieval, repository
inspection and evidence operations below are local operations by that process.

## Assignment

Proceed autonomously to the first terminal state, `H-0 PASS` or `HARD STOP`,
write the retained H-0 evidence and return the complete handback. Do not pause
for ordinary confirmation and do not continue after a terminal state.

Read completely before acting:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md` reading map, §0, §16 and §20;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md` restriction banner;
5. the accepted one-host proposal §4.1.1–§4.1.4, §4.2.3, §4.4.1,
   §4.4.2b and §4.7.4's latest OH-S1 row; and
6. the authority record for this assignment.

The repository content is not available as authority until retrieval and exact
commit verification below. The controller-provided prompt and authority text
are the executable authority capsule; they do not authorize transferring any
repository byte from the controller.

## Fixed inputs

- Canonical public URL: `https://github.com/ming-themerciless/freedom-bot.git`
- Pinned commit: `46d1c35a029ca8287779ae87d08a370ba0a0f2ef`
- Repository path: `/opt/freedom-blades/platform`
- Account: `ubuntu`
- Expected kernel nodename: `Test`
- Evidence-run identifier: `p5-r5-rp11-h0-20261005-03`
- Evidence directory: `/var/tmp/p5-r5-rp11-h0-20261005-03-h0-evidence`

Do not substitute any value.

## Absolute prohibitions

- after controller bootstrap, no command may contact or execute on another
  host; no `ssh`, `scp`, `sftp`, `rsync`, host-path operand or remote controller;
- no repository or implementation byte may come from the controller;
- no credential, authentication helper, SSH agent, token, key, `known_hosts`,
  SSH configuration, home-directory content or model-provider credential may
  be read, requested, created, installed, forwarded or reused by the executor;
- no `sudo`, privilege change, package operation, build, test suite,
  service/database mutation, H-1/H-2, activation, rollback, cleanup, commit or
  push;
- no `git reset`, `git clean`, forced checkout, deletion, overwrite of local
  changes, submodule operation, hook execution or LFS operation;
- do not inspect, list, change or delete any retained `/var/tmp/p5-r5-fresh-*`
  path or any earlier H-0 evidence path;
- no environment dump, secret file, application data, PostgreSQL or production
  service; and
- during H-0, no write outside the exclusively created evidence directory.

Any needed action outside this list is a `HARD STOP`.

## Phase A — local identity and safe retrieval

1. Without reading environment variables, establish that this executor process
   is running as `ubuntu` and that `uname -n` is exactly `Test`. Otherwise
   `HARD STOP` before network or filesystem mutation.
2. Inspect only the repository path and its Git administrative state. It must
   be an existing checkout of the canonical repository with no tracked,
   staged or untracked change, unsafe ownership, active Git operation or
   worktree lock. Any failure is a `HARD STOP`; do not repair it.
3. Disable interactive Git prompting for this invocation only. Fetch the pin
   directly from the fixed HTTPS URL without a credential. Authentication,
   denial, absence or helper/credential need is a `HARD STOP` without fallback.
4. Verify the object is the exact commit. Switch the clean checkout to it in
   detached-HEAD mode without force or deletion. Require exact `HEAD` and an
   empty `git status --porcelain=v1`; otherwise `HARD STOP`.
5. From the verified tree, read the governing files listed above and require
   the accepted proposal and D3-R6 acceptance record. This current prompt and
   authority need not exist in the predecessor commit because their exact text
   arrived through the authorized controller bootstrap.

The fetch and detached checkout are the only Git mutations authorized.

## Phase B — H-0 evidence setup

1. Confirm the evidence directory does not exist by non-following metadata.
   Create it exactly once as `ubuntu:ubuntu` mode `0700`, set `umask 077`
   before creating any evidence file, and require each evidence file to be a
   fresh regular `ubuntu:ubuntu` file with mode `0600`. A pre-existing name of
   any type is a `HARD STOP`; do not inspect or remove it.
2. Record work ID, fixed inputs, start/end UTC, local nodename, machine-id
   SHA-256, exact commit, exact received R2 prompt and authority bytes and
   their SHA-256, the controller bootstrap provenance, and every executor
   command in order with exact text, UTC start and end timestamps, exit status,
   and distinct raw stdout/stderr. Never record an environment or secret.
3. Before manifest generation, close every payload record. Record the exact
   manifest-generation command like every other command. Build
   `MANIFEST.payload` over every closed payload file except its own command
   record and later closing records, with safe relative name, SHA-256 and byte
   length. Build `MANIFEST.final` naming only `MANIFEST.payload`'s full SHA-256
   and byte length; do not claim that it hashes itself. State which later
   command records are excluded and why.
4. Before terminal handback, inventory ownership and modes. A record missing
   command text, either timestamp or status, or any non-`0600` regular file is
   a `HARD STOP`; preserve the directory and report the defect without repair.

If evidence publication fails, `HARD STOP`. Preserve the directory; cleanup is
not authorized.

## Phase C — exact H-0 fact set

Collect HF-01 through HF-20 exactly as defined and cumulatively amended by the
accepted proposal. Use only its permitted C-ID, C-PROC, C-STAT, C-DIG, C-VER,
C-PKG and C-SDQ command classes.

- HF-07 includes every package named in §4.4.1 plus the owner of
  `/usr/bin/pkcheck`; use local package lists only and never `apt update`.
- HF-10 includes `/usr/bin/pkcheck`, `/usr/bin/sleep` and
  `/usr/bin/systemd-run`.
- HF-11 includes every §4.2.3 path and parent, `/run`, `/run/polkit-1`,
  `/run/polkit-1/rules.d`, `/run/freedom-blades-rp11`,
  `/etc/freedom-blades-rp11` and `/var/tmp`, recording presence/absence, type,
  owner, group, mode, `(dev, ino)` and extended-attribute names.
- HF-12 never elevates to read a rules file; record `unreadable` where needed.
- HF-14 reads only the named `binfmt_misc` procfs files under the proposal's
  grammar.
- HF-15 includes `/run` and every publication or temporary-tree filesystem,
  including the proposed capture-root parent only if already fixed. Do not
  invent a capture root.
- HF-16 uses explicit properties and includes `DefaultTimeoutStartUSec`; do
  not use `systemctl show-environment`.
- HF-18 records only whether the already named interactive client path exists;
  do not search broadly or install a client. If none is named, record `not
  specified` as a design input gap.
- HF-19 records the required configuration-file digests and only lines naming
  `/var/tmp`, `/run/polkit-1` or `/run/freedom-blades-rp11`.
- HF-20 records the two specified unit `LoadState` values and only the named
  userspace-soft-reboot condition paths from PO-21(i).

Record exact absence and unreadable results. If the fact set cannot be safely
completed within the permitted classes, preserve partial evidence and `HARD
STOP`.

## Terminal states and handback

Use `H-0 PASS` only when retrieval and every HF-01 through HF-20 observation
completed within authority and the retained evidence manifest is complete.
Return exact commit and clean status; evidence directory and aggregate digest
and length; both manifest digests and lengths; an HF-01–HF-20 table with
evidence references and concise values; every absent, unreadable, unexpected
or version-different fact; every executor command with status and timestamps;
manifest exclusions; prohibited-action confirmation; and checks not run.

At the first identity, prerequisite, retrieval, authority or evidence failure,
`HARD STOP` immediately. Preserve evidence already written and return the
failed step, exact safe error, repository/evidence changes, retained paths and
available full digests, plus the smallest decision needed. Do not retry,
repair, clean up, authenticate or continue.

In either state, additionally report how the controller launched the remote
Claude process, confirm that it transferred no repository/evidence bytes and
ran no H-0 command, and distinguish controller commands from executor commands.

End an `H-0 PASS` with: `H-0 facts await independent Codex review; OH-S2 and
every later slice remain unauthorized.`

No repository handback file, commit or push is authorized. Leave authoritative
H-0 evidence only on `oracle-test`.
