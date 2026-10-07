# Claude prompt — R4 isolated-checkout public retrieval and H-0

Status: **authorized by Peter Duscha on 2026-10-06**

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R4-20261006-01`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-claude-prompt.md. Proceed autonomously through the single authorized SSH run until H-0 PASS or HARD STOP. Preserve the complete terminal handback in the required repository file before returning it in chat. Do not ask the maintainer to choose routine implementation details.
```

## Required reading

Read completely `.agents/AGENTS.md`; the implementation-plan reading map,
§0, §16 and §20; `docs/review/Handover information`; the restriction banner in
`docs/operations/disposable-test-server.md`; the accepted one-host proposal
§4.1.1–§4.1.4, §4.2.3, §4.4.1, §4.4.2b and §4.7.4's latest OH-S1 row; the R3
prompt and independent HARD STOP review; and the R4 authority.

## Fixed inputs

- Canonical public URL: `https://github.com/ming-themerciless/freedom-bot.git`
- Pinned commit: `46d1c35a029ca8287779ae87d08a370ba0a0f2ef`
- Remote account and nodename: `ubuntu`, `Test`
- Existing checkout, preserved and not inspected: `/opt/freedom-blades/platform`
- Exclusive isolated checkout: `/var/tmp/p5-r5-rp11-h0-20261006-01-checkout`
- Exclusive evidence directory: `/var/tmp/p5-r5-rp11-h0-20261006-01-evidence`
- Durable controller handback:
  `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-handback.md`

Do not substitute these values.

## Operating model and boundaries

Remain on the controller. Construct and locally validate one self-contained
program, record its digest and length, and send it once on standard input to
exactly one non-interactive SSH command using the same forwarding-disabled,
closed-environment structure required by R3. Do not launch another Claude
client or execute separate remote commands. Authentication, host-key or
transport failure is a HARD STOP without retry.

The remote bootstrap must first establish real/effective `ubuntu@Test` before
any write or network use. It then sets `umask 077`, requires both exclusive
remote paths to be absent using non-following metadata checks, creates only the
evidence directory, retains the exact program as mode `0600`, verifies its
controller-supplied SHA-256 and length, and invokes it with a closed environment
containing only `HOME=/nonexistent`, `LC_ALL=C` and `PATH=/usr/bin:/bin`.

The retained program may write only the two exclusive `/var/tmp` paths. It
must not inspect or mutate `/opt/freedom-blades/platform`, any earlier evidence,
`/tmp`, secrets, application data, PostgreSQL or production services.

## Execution

1. Record the controller command shape, program digest/length, work ID, fixed
   inputs, remote identity, nodename and machine-id SHA-256.
2. Record `/usr/bin/python3` resolution and version. Use it only with `-I -S`
   for bounded evidence helpers. If it is absent or unsuitable, HARD STOP.
3. With prompting, credential helpers, submodules and maintenance disabled,
   initialize the absent isolated-checkout path and fetch only the pinned
   commit directly and anonymously from the fixed HTTPS URL. Authentication,
   denial, missing pin or credential/helper need is a HARD STOP.
4. Verify the object is the exact commit, detach the isolated checkout to it,
   and require exact `HEAD` plus empty porcelain status. Do not configure a
   persistent credential helper or add an SSH remote.
5. Read the governing files from the verified isolated tree and require the
   accepted proposal and D3-R6 acceptance. Retain and verify exact copies of
   the controller-supplied R4 prompt and authority in the evidence directory.
6. Collect HF-01 through HF-20 exactly as cumulatively defined by proposal
   §4.4.1 and §4.4.2b, using only C-ID, C-PROC, C-STAT, C-DIG, C-VER, C-PKG and
   C-SDQ. Preserve every absence, unreadable result and version difference.
   Apply every amendment enumerated in the R3 prompt, including HF-07, HF-10,
   HF-11, HF-12, HF-14 through HF-16, and HF-18 through HF-20.
7. Record every remote command with exact text, separate stdout/stderr, UTC
   start/end times and exit status. Never record environment or credential
   content.
8. Close the evidence exactly as R3 required: payload manifest, final manifest,
   ownership/mode inventory and explicit exclusions. Every evidence file must
   be a fresh regular `ubuntu:ubuntu` mode-`0600` file. Publication failure is
   a HARD STOP without repair.

## Prohibitions

No second SSH connection or retry; no nested Claude; no SCP, SFTP, rsync,
forwarding, interactive authentication, credential read/copy, `sudo`, package
operation, installation, build, test, service/database mutation, H-1/H-2,
activation, pass, rollback, cleanup, commit or push. Do not remove either
exclusive remote path after creation.

## Terminal handback

At either terminal state, first write the complete, unabridged handback to the
fixed durable controller-handback path using repository editing tools. This
single documentation write is authorized; do not update another repository
file. Then return the same handback in chat.

`H-0 PASS` requires successful pinned retrieval, a clean detached isolated
checkout, all HF-01–HF-20 observations and complete manifests. Report exact
commit/status, paths and digests/lengths; the full HF table with evidence
references; all absent/unreadable/unexpected facts; every command and
timing/status; manifest exclusions; controller command and program
digest/length; prohibited-action confirmation; and checks not run.

At the first failure, report `HARD STOP` with the failed step, safe error,
repository/evidence changes, retained paths and available digests, and the
smallest follow-up needed. Do not retry, repair or clean up.

End exactly: `H-0 facts await independent Codex review; OH-S2 and every later slice remain unauthorized.`
