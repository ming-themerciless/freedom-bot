# Claude prompt — execute narrow H-0G gap collection R1

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0G-R1-20261006-06`

Date: 2026-10-06

Executor: Claude Code on the production workspace controller

Target: `oracle-test` (kernel nodename `Test`), executing locally as `ubuntu`

Exclusive evidence path:
`/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence`

## Objective and terminal boundary

Execute the repository-free H-0G fact collection specified by accepted R3
§11 through exactly one forwarding-disabled, non-interactive SSH execution
connection. Preserve the exact program and complete output in the exclusive
evidence directory. End at the first `H-0G PASS` or defined `HARD STOP`, write
the complete durable handback named below, update the four current-state
pointers, return the handback verbatim in chat, and stop for independent Codex
review.

The executor must not claim a composed `H-0 PASS`. Composition with R5 is an
independent reviewer act.

Handback:
`docs/review/phase-5-0-p5-r5-rp11-h1-h0g-r1-handback.md`

## Required reading before any connection

Read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md` reading map, §0, §14, §16 and §20;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
5. the R3 acceptance, proposal §9 through §12, and this authority;
6. the R5 handback, solely as repository-held evidence for the fixed anchors.

Inspect `git status` and preserve every pre-existing change. Verify this
prompt's byte count and SHA-256 against the authority before doing anything
else. A mismatch is a local `HARD STOP: prompt identity mismatch`; make no
connection.

## Fixed inputs

- Evidence path:
  `/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence`
- Capture-root parent literal: `/var/lib/rp11-capture`
- Exact Python path: `/usr/bin/python3.14`
- A-1 nodename: `Test`
- A-2 `/etc/machine-id` SHA-256:
  `e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d`
- A-3 kernel: `7.0.0-31-generic`
- A-4 systemd: `259.5-0ubuntu3.4`
- A-5 polkitd: `127-2ubuntu1.1`
- A-6 libc6: `2.43-2ubuntu2.4`
- A-7 python3.14-minimal: `3.14.4-1ubuntu0.2`
- A-8 `/usr/bin/python3.14` SHA-256:
  `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd`
- A-9 `/var/lib`: non-symlink directory, `root:root`, mode `0755`,
  `(st_dev, st_ino)=(2049, 97831)`, no xattr names
- A-10 `/var/lib` mount row: target `/`, source `/dev/sda1`, fstype `ext4`,
  options `rw,relatime,discard,errors=remount-ro,commit=30`
- R5 `df` comparison columns: source `/dev/sda1`, fstype `ext4`, target `/`.
  Capacity values are recorded but are not anchors.

Any missing or malformed fixed input is a local
`HARD STOP: missing fixed input <name>` before connection.

## Connection and program constraints

Use exactly one connection equivalent to:

```text
ssh -T -o BatchMode=yes -o ClearAllForwardings=yes \
  -o ForwardAgent=no -o ForwardX11=no -o PermitLocalCommand=no \
  oracle-test 'env -i HOME=/home/ubuntu USER=ubuntu LOGNAME=ubuntu \
  PATH=/usr/bin:/bin LC_ALL=C /bin/bash -s'
```

Send one self-contained program on standard input. Do not make a controller
network preflight or a second connection. The program must set `umask 077`,
verify `id -u` is non-root and `uname -n` is `Test`, then check freshness of
the exact evidence path using only `test -e` and `test -L`. Do not list
`/var/tmp`. Present path means `HARD STOP: evidence path not fresh`.

After freshness succeeds, create only that evidence directory. Retain the
exact received program, a command/result ledger, stdout/stderr captures,
bounded fact files, a SHA-256 manifest and a terminal-state file. Close and
hash evidence on every terminal path. Do not write anywhere else.

## Required observations

Run only the unprivileged, read-only commands/classes accepted in R3 §11:

1. Re-observe A-1 through A-8 using `uname`, `sha256sum`, `dpkg-query`, and
   the exact paths stated above.
2. For `python3.14`, `libpython3.14-minimal` and
   `libpython3.14-stdlib`, record `dpkg-query -W -f`, `dpkg --verify`, and
   local `apt-cache policy`. Do not run `apt update` or any package operation.
3. Record no-follow `stat` facts for `/usr/bin/python3.14`, then run
   `/usr/bin/python3.14 -I -S -c` with a fixed literal that prints
   `sys.version`, `sys.flags.isolated`, `sys.flags.no_site`,
   `sys.executable`, `sys.prefix` and `sys.path`. Every bounded Python helper
   must use this exact interpreter with `-I -S`, never `/usr/bin/python3`.
4. G-15a: with Python, call `os.lstat('/var/lib/rp11-capture')` and
   `os.listxattr('/var/lib/rp11-capture', follow_symlinks=False)` separately.
   Both must return `ENOENT` for PASS.
5. G-15b: with Python, `lstat` and no-follow `listxattr` only `/var/lib`.
   Record type, UID/GID and resolved owner/group names, mode, `(st_dev,
   st_ino)` and xattr names. It must equal A-9.
6. G-15c: run exactly `/usr/bin/findmnt --target /var/lib -o
   TARGET,SOURCE,FSTYPE,OPTIONS`; require one data row equal to A-10.
7. G-15d: run exactly `/usr/bin/df --output=source,fstype,size,used,avail,pcent,itotal,iused,iavail,target
   -- /var/lib`; require source, fstype and target equal to the R5 comparison
   columns and record all capacity columns.

Never use `findmnt`, `df` or following `stat` on
`/var/lib/rp11-capture`. Never list `/var/lib` or inspect any other candidate.

## Terminal contract

`H-0G PASS` requires every required observation and exact equality of A-1
through A-10. Otherwise stop without repair:

- parent present: record only its `lstat` facts and xattr names, then
  `HARD STOP: capture-root parent present before CPP`;
- parent error other than `ENOENT`:
  `HARD STOP: capture-root parent unobservable (errno N)`;
- invalid `/var/lib`: `HARD STOP: capture-root ancestor invalid`;
- failed `findmnt` or `df`:
  `HARD STOP: ancestor filesystem facts unavailable`;
- any anchor difference:
  `HARD STOP: composition anchor changed`;
- any other unexpected condition: a precise fail-closed `HARD STOP` recorded
  before further observation.

No retry is authorized.

## Absolute prohibitions

Do not access any retained R1-R5 or agent-client evidence path. Do not access
`/opt/freedom-blades/platform` on `oracle-test` in any way, including `stat`.
Do not retrieve or inspect a repository. Do not access credentials, secrets,
player data, SSH-agent forwarding, `/etc/polkit-1/rules.d`, CL-21i paths or any
agent-client path. Do not search for a client. Do not use `sudo` or another
privilege path. Do not install, remove or update packages. Do not build, test,
run services, access a database, clean up, recreate the workspace, execute
OH-S2/H-1/H-2, activate anything, commit or push.

## Durable handback and pointer updates

After the connection ends, create the dedicated handback from the captured
terminal output and evidence summary without revisiting the host. It must
include the work ID, prompt/authority identity, exact terminal state, the
single connection count, every command and exact result, A-1 through A-10
comparison, G-15a through G-15d results, evidence manifest and hashes, files
changed, checks run/not run, and confirmation that every prohibition held.

Update only:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner only in `docs/operations/disposable-test-server.md`.

Mark this authority and prompt consumed and point to the handback. Do not
claim composition or authorize cleanup, workspace recreation, OH-S2 or later
work. Run repository-relative link checks and `git diff --check`, return the
complete handback verbatim in chat, and stop for independent Codex review.

End the handback exactly:

`H-0G awaits independent Codex review and composition; no cleanup, workspace recreation, OH-S2 or later slice is authorized.`
