# Claude prompt — OH-S0b public retrieval and OH-S1 H-0 fact collection

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0`

Date: 2026-10-05

## Assignment

Execute this assignment from an **interactive session on `oracle-test`**, with
the Claude process itself running locally as `ubuntu`. Proceed autonomously to
the first terminal state, `H-0 PASS` or `HARD STOP`, write the retained H-0
evidence and return the complete handback. Do not pause for ordinary
confirmation and do not continue after a terminal state.

Read completely before acting:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md` reading map, §0, §16 and §20;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md` restriction banner;
5. the accepted one-host proposal §4.1.1–§4.1.4, §4.2.3, §4.4.1,
   §4.4.2b and §4.7.4's latest OH-S1 row; and
6. the authority record for this assignment.

The repository content is not available as authority until retrieval and exact
commit verification below. The user may provide this prompt interactively;
that does not authorize transferring repository bytes from another host.

**Embedded authority capsule.** Peter Duscha authorizes this exact work ID on
2026-10-05 for the two ordered parts and boundaries stated here: anonymous
public retrieval of the fixed commit, then unprivileged H-0. This capsule is
the executable authority presented interactively. The repository authority
record is the durable management copy but is not required to exist in the
pinned predecessor commit. After retrieval is verified and the evidence
directory is created, record the exact received prompt bytes and their
SHA-256 before collecting any H-0 fact.

## Fixed inputs

- Canonical public URL:
  `https://github.com/ming-themerciless/freedom-bot.git`
- Pinned commit: `46d1c35a029ca8287779ae87d08a370ba0a0f2ef`
- Repository path: `/opt/freedom-blades/platform`
- Account: `ubuntu`
- Evidence-run identifier: `p5-r5-rp11-h0-20261005-01`
- Evidence directory:
  `/var/tmp/p5-r5-rp11-h0-20261005-01-h0-evidence`

Do not substitute any value.

## Absolute prohibitions

- no command may contact or execute on another host; no `ssh`, `scp`, `sftp`,
  `rsync`, host-path operand or scripted remote controller;
- no credential, authentication helper, SSH agent, token, key, `known_hosts`,
  SSH configuration, home-directory content or model-provider credential may
  be read, requested, created, installed or reused;
- no `sudo`, privilege change, package installation/update, `apt update`,
  build, test suite, service mutation, daemon reload, database access,
  `systemctl` mutation, H-1/H-2, `ACT`, `DEACT`, pass execution, rollback,
  cleanup, commit or push;
- no `git reset`, `git clean`, forced checkout, deletion, overwrite of local
  changes, submodule operation, hook execution or LFS operation;
- do not inspect, list, change or delete any retained
  `/var/tmp/p5-r5-fresh-*` path;
- no environment dump (`env`, `printenv`, `/proc/*/environ`), secret file,
  application data, PostgreSQL or production service; and
- during H-0, no write outside the exclusively created evidence directory.

Any needed action outside this list is a `HARD STOP`, not a reason to ask for
broader access.

## Phase A — local identity and safe retrieval

1. Without reading environment variables, establish that the process is
   running as `ubuntu` and that `uname -n` is exactly `oracle-test`. Otherwise
   `HARD STOP` before network or filesystem mutation.
2. Inspect only the repository path itself and its Git administrative state.
   It must be an existing Git checkout of the canonical repository with no
   tracked modification, staged change or untracked path. A dirty checkout,
   unexpected repository, unsafe ownership, active Git operation or worktree
   lock is a `HARD STOP`; do not repair it.
3. Disable interactive Git prompting for the retrieval invocation only. Fetch
   the pinned commit directly from the fixed HTTPS URL without a credential.
   Do not use the configured SSH remote. If the server requests
   authentication, access is denied, the commit is absent, or any helper or
   credential would be needed, `HARD STOP` without fallback.
4. Verify the fetched object is a commit with the exact 40-byte identifier.
   Switch the clean checkout to that exact commit in detached-HEAD mode,
   without force and without deleting anything. Verify `HEAD` equals the pin
   and `git status --porcelain=v1` is empty. Any mismatch is a `HARD STOP`.
5. From this verified tree, read the governing files listed under Assignment.
   Verify that the accepted proposal and D3-R6 acceptance record exist. The
   new OH-S0b/OH-S1 prompt and authority files need not exist in this
   predecessor commit because this exact prompt carries the embedded
   authority capsule. If the pinned tree does not contain the accepted design
   or contradicts this assignment, `HARD STOP`.

The fetch and detached checkout are the only Git mutations authorized.

## Phase B — H-0 evidence setup

1. Confirm the evidence directory does not exist by `lstat`. Create it once
   with mode `0700`. A pre-existing name of any type is a `HARD STOP`; do not
   inspect or remove it.
2. Record in the evidence directory: work ID, fixed inputs, start/end UTC,
   local nodename, machine-id SHA-256, exact commit, the received prompt bytes
   and SHA-256, the embedded authority capsule, every command in execution
   order, its exit status, and its raw stdout/stderr. Never record an
   environment or secret.
3. Each evidence file must be created without overwriting an existing name.
   Finish by recording a sorted inventory, SHA-256 and byte length for every
   evidence file, then the directory's retained aggregate manifest digest.

If evidence publication fails, `HARD STOP`. Preserve the directory; cleanup is
not authorized.

## Phase C — exact H-0 fact set

Collect HF-01 through HF-20 exactly as defined and cumulatively amended by the
accepted proposal. Use only the proposal's permitted C-ID, C-PROC, C-STAT,
C-DIG, C-VER, C-PKG and C-SDQ command classes.

Requirements that are easy to miss:

- HF-07 includes every package named in §4.4.1 plus the owner of
  `/usr/bin/pkcheck`; use local package lists only and never `apt update`.
- HF-10 includes `/usr/bin/pkcheck`, `/usr/bin/sleep` and
  `/usr/bin/systemd-run`.
- HF-11 includes every §4.2.3 path and parent, `/run`, `/run/polkit-1`,
  `/run/polkit-1/rules.d`, `/run/freedom-blades-rp11`,
  `/etc/freedom-blades-rp11` and `/var/tmp`, recording presence/absence, type,
  owner, group, mode, `(dev, ino)` and extended-attribute names.
- HF-12 never elevates to read a rules file; record `unreadable` where the
  unprivileged account cannot read it.
- HF-15 includes `/run` and every publication or temporary-tree filesystem,
  including the proposed capture-root parent only if already fixed. Do not
  invent a capture root.
- HF-16 uses explicit properties and includes
  `DefaultTimeoutStartUSec`; do not use `systemctl show-environment`.
- HF-18 records only whether the already named interactive client path exists;
  do not search broadly and do not install a client. If no path is named in
  the accepted tree, record `not specified` as a design input gap.
- HF-19 records the required configuration-file digests and only the lines
  naming `/var/tmp`, `/run/polkit-1` or `/run/freedom-blades-rp11`.
- HF-20 records the two specified unit `LoadState` values and only the named
  userspace-soft-reboot condition paths from PO-21(i).
- HF-14 reads only the named `binfmt_misc` procfs files under the proposal's
  grammar.

Do not turn a missing optional file, absent unit or unreadable unprivileged
file into an invented fact. Record the exact absence/unreadable result. If the
fact set cannot be completed safely within the permitted classes, preserve the
partial evidence and `HARD STOP`.

## Terminal states and handback

### `H-0 PASS`

Use only when retrieval and every required HF-01 through HF-20 observation
completed within authority and the retained evidence manifest is complete.
Return:

- exact commit and clean-status verification;
- evidence directory, its aggregate SHA-256 and byte length;
- a table HF-01 through HF-20 with evidence-file references and concise
  observed values;
- every absent, unreadable, unexpected or version-different fact, without
  interpreting it as acceptance of a proof obligation;
- commands run and exact exit statuses;
- confirmation that no prohibited action occurred;
- checks not run and why; and
- the statement: `H-0 facts await independent Codex review; OH-S2 and every
  later slice remain unauthorized.`

### `HARD STOP`

Stop immediately at the first prerequisite, retrieval, authority or evidence
failure. Preserve any evidence already written. Return the failed step, exact
error class, whether the repository or evidence directory changed, retained
paths and digests available, and the smallest decision needed. Do not retry,
repair, clean up, authenticate or continue to later phases.

No repository handback file, commit or push is authorized. Return the handback
in the Claude conversation and leave the authoritative H-0 evidence retained
on `oracle-test` for independent review.
