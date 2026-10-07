# Claude prompt — direct SSH-controlled public retrieval and H-0 collection

Status: **authorized by Peter Duscha on 2026-10-05**

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R3-20261005-06`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste the following
as an ordinary prompt. This is not a slash command:

```text
Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-claude-prompt.md. Remain on this controller host and perform the authorized H-0 through exactly one forwarding-disabled SSH execution connection to oracle-test. Proceed autonomously until H-0 PASS or HARD STOP, then return the complete handback. Do not launch a second Claude client and do not stop for ordinary confirmation.
```

## Operating model

You are the controller. Do not start Claude Code on `oracle-test`. Construct
one self-contained H-0 program locally, validate it without contacting another
host, and send it once on standard input to a non-interactive SSH command. The
remote bootstrap and program must perform every identity check, Git operation,
observation and evidence write on `oracle-test`. Do not execute individual H-0
commands through separate SSH calls.

The controller may read the governing repository documentation and create its
temporary program under a fresh `/tmp` directory. That file is controller
transport, not evidence. It must contain no repository source or implementation
file. Record its local SHA-256 and byte length before the SSH attempt.

Use exactly this command structure, replacing `PROGRAM`, `SHA256` and `BYTES`
with the fresh local program path and its literal lowercase digest and decimal
length. Do not add another SSH option or connection:

```bash
ssh -T -o BatchMode=yes -o ClearAllForwardings=yes -o ForwardAgent=no -o ForwardX11=no -o PermitLocalCommand=no oracle-test "/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /bin/bash --noprofile --norc -c 'set -eu; if ! { test \"\$(/usr/bin/id -ru)\" = \"\$(/usr/bin/id -u ubuntu)\" && test \"\$(/usr/bin/id -un)\" = ubuntu && test \"\$(/usr/bin/uname -n)\" = Test; }; then /usr/bin/printf \"HARD STOP: remote identity mismatch\\n\" >&2; exit 70; fi; umask 077; evidence=/var/tmp/p5-r5-rp11-h0-20261005-04-h0-evidence; if /usr/bin/test -e \"\$evidence\" || /usr/bin/test -L \"\$evidence\"; then /usr/bin/printf \"HARD STOP: evidence path exists\\n\" >&2; exit 71; fi; /usr/bin/mkdir -m 0700 -- \"\$evidence\"; /usr/bin/tee \"\$evidence/controller-h0-program.sh\" >/dev/null; /usr/bin/chmod 0600 \"\$evidence/controller-h0-program.sh\"; test \"\$(/usr/bin/sha256sum \"\$evidence/controller-h0-program.sh\" | /usr/bin/cut -d\" \" -f1)\" = SHA256; test \"\$(/usr/bin/stat -c %s \"\$evidence/controller-h0-program.sh\")\" = BYTES; exec /usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin /bin/bash --noprofile --norc \"\$evidence/controller-h0-program.sh\"'" < "PROGRAM"
```

The fixed remote bootstrap must use absolute system paths and a closed
`PATH=/usr/bin:/bin`, must not read a shell profile or environment dump, and
must do only the following before invoking the retained program:

1. require the effective and real account name to be `ubuntu` and
   `/usr/bin/uname -n` to be exactly `Test`;
2. otherwise print a safe `HARD STOP` and exit before any write or network use;
3. set `umask 077`, require the evidence path not to exist by non-following
   metadata, and create it once with mode `0700`;
4. retain stdin exactly as `controller-h0-program.sh` mode `0600`, record its
   full SHA-256 and byte length, and require them to equal the controller's
   precomputed values supplied as fixed literal arguments; and
5. invoke that retained file using `/bin/bash` with a closed environment
   containing only `HOME=/nonexistent`, `LC_ALL=C` and `PATH=/usr/bin:/bin`.

The connection uses existing SSH authentication only. Do not inspect or copy a
key, token, agent, SSH configuration, `known_hosts` or model-provider
credential. Do not enable agent, environment, X11, socket or port forwarding.
An authentication prompt, host-key prompt, transport failure or remote
bootstrap failure is `HARD STOP`; do not retry or change options.

## Required reading before constructing the program

Read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md` reading map, §0, §16 and §20;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md` restriction banner;
5. the accepted one-host proposal §4.1.1–§4.1.4, §4.2.3, §4.4.1,
   §4.4.2b and §4.7.4's latest OH-S1 row; and
6. the R3 authority record.

For this assignment only, R3 supersedes OH-D-2's local-client condition and
the production-isolation controller/relay row. Every other restriction remains
in force. The controller and SSH transport are outside the trusted execution
path.

## Fixed inputs

- Canonical public URL: `https://github.com/ming-themerciless/freedom-bot.git`
- Pinned commit: `46d1c35a029ca8287779ae87d08a370ba0a0f2ef`
- Remote repository: `/opt/freedom-blades/platform`
- Remote account and nodename: `ubuntu`, `Test`
- Evidence run: `p5-r5-rp11-h0-20261005-04`
- Evidence directory: `/var/tmp/p5-r5-rp11-h0-20261005-04-h0-evidence`

Do not substitute any value.

## Remote program requirements

The retained program is the sole remote executor. It must record every command
it runs with exact text, distinct stdout/stderr, UTC start/end timestamps and
exit status. It must also record the controller command shape, controller
program digest/length, work ID, fixed inputs, local nodename, machine-id
SHA-256, exact commit, and the exact received R3 prompt and authority text with
their SHA-256. Never record environment or credential content.

After the bootstrap has retained the program, execute these phases in order:

1. Inspect only the repository path and Git administrative state. Require an
   existing canonical checkout with no tracked, staged or untracked change,
   unsafe ownership, active operation or lock. Do not repair it.
2. With interactive Git prompting and credential helpers disabled for that
   invocation, fetch only the pinned commit directly from the fixed HTTPS URL.
   Authentication, denial, absence or credential/helper need is `HARD STOP`.
3. Verify the object is the exact commit, detach the clean checkout to it
   without force or deletion, and require exact `HEAD` plus empty porcelain
   status. These are the only authorized Git mutations.
4. Read the governing files from the verified tree and require the accepted
   proposal and D3-R6 acceptance record. The R3 prompt and authority may be
   controller-supplied because the pinned predecessor need not contain them.
5. Collect HF-01 through HF-20 exactly as cumulatively defined by §4.4.1 and
   §4.4.2b, using only C-ID, C-PROC, C-STAT, C-DIG, C-VER, C-PKG and C-SDQ.
   Preserve every absence, unreadable result and version difference.

The easy-to-miss amendments remain mandatory: HF-07 includes the owner of
`/usr/bin/pkcheck`; HF-10 includes `pkcheck`, `sleep` and `systemd-run`; HF-11
includes every §4.2.3 path and parent plus `/run`, the named Polkit/runtime
paths, `/etc/freedom-blades-rp11` and `/var/tmp`, with `(dev, ino)` and xattr
names; HF-12 never elevates; HF-14 reads only named `binfmt_misc` files; HF-15
includes `/run` and all publication/temporary-tree filesystems; HF-16 includes
`DefaultTimeoutStartUSec`; HF-18 records only the named client path or `not
specified`; HF-19 includes the named `/var/tmp` and runtime tmpfiles lines;
HF-20 records the two unit `LoadState` values and only PO-21(i)'s named paths.

Before handback, close every payload record; generate `MANIFEST.payload` over
all closed payload files except its own command record and later closing
records; generate `MANIFEST.final` naming only the payload manifest's full
SHA-256 and byte length; inventory owner/mode; and require every evidence file
to be a fresh regular `ubuntu:ubuntu` mode-`0600` file. Explain every manifest
exclusion. Evidence publication failure is `HARD STOP` without repair.

## Absolute prohibitions

No second SSH connection or retry; no nested Claude client; no SCP, SFTP,
rsync, repository/source transfer from the controller, forwarding, interactive
authentication, credential read/copy, `sudo`, package operation, build, test,
service/database mutation, H-1/H-2, activation, pass, rollback, cleanup,
commit or push. The remote program writes only its exclusive evidence
directory. It must not inspect retained evidence paths, `/tmp`, secrets,
application data, PostgreSQL, environment dumps or production services.

## Terminal handback

`H-0 PASS` requires successful retrieval, all HF-01–HF-20 observations and a
complete retained manifest. Return exact commit and status, evidence directory
and aggregate digest/length, both manifest digests/lengths, an HF-01–HF-20
table with evidence references, every absent/unreadable/unexpected fact, every
remote command and timing/status, manifest exclusions, the one controller SSH
command and program digest/length, prohibited-action confirmation, and checks
not run. End with: `H-0 facts await independent Codex review; OH-S2 and every
later slice remain unauthorized.`

At the first failure, return `HARD STOP` with the failed step, safe error,
repository/evidence changes, retained paths and available digests, and the
smallest decision needed. Do not retry, repair, authenticate or clean up.
