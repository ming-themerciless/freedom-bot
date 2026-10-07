# Handback — narrow H-0G gap collection R1: `H-0G PASS`

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0G-R1-20261006-06`

Date: 2026-10-06

Executor: Claude Code on the production workspace controller
(`/opt/freedom-blades/platform`), one forwarding-disabled, non-interactive SSH
execution connection to `oracle-test`.

Prompt: [`phase-5-0-p5-r5-rp11-h1-h0g-r1-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-h0g-r1-claude-prompt.md),
SHA-256 `58ebc8cb07a82d4f2c75df5dc35feb99eaf04802cc9abd1a98ffdb1104caca31`,
7881 bytes. Both values were recomputed before any connection and equal the
authority's pin.
· Authority: [`project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-authority.md),
SHA-256 `05b8bb314515f92c9e0d92c7f60865c9e4ebfe371b15cbbf23d44de476a69954`,
2172 bytes.

## Terminal state: `H-0G PASS`

This is the executor's terminal state for the H-0G fact collection. It is an
observation record only. It is **not** a composed `H-0 PASS`. Composition with
R5 is reserved to independent Codex review.

Every PASS condition of the prompt and R3 §11.5 held:

- every required observation ran (c001–c026), and every command exited `0`
  with empty stderr;
- G-15a: `lstat` and no-follow `listxattr` of `/var/lib/rp11-capture` both
  raised `ENOENT` (errno 2);
- G-15b: `/var/lib` is a non-symlink directory equal to A-9;
- G-15c: `findmnt` exited `0` with exactly one data row equal to A-10;
- G-15d: `df` exited `0` with exactly one data row. Its `source`, `fstype` and
  `target` equal R5 c137;
- anchors A-1 through A-10 are all exactly equal.

The program's own terminal line was `H0G-TERMINAL: H-0G PASS`. Its retained
`TERMINAL-STATE` reads `H-0G PASS`, closed at `2026-10-06T15:11:56.434701Z`.

## Connection

**Exactly one** SSH connection was made. No network preflight, retry or second
connection took place.

- Exact controller command, run once:

```bash
ssh -T -o BatchMode=yes -o ClearAllForwardings=yes -o ForwardAgent=no -o ForwardX11=no -o PermitLocalCommand=no oracle-test 'env -i HOME=/home/ubuntu USER=ubuntu LOGNAME=ubuntu PATH=/usr/bin:/bin LC_ALL=C /bin/bash -s' < /tmp/claude-1000/-opt-freedom-blades-platform/a7ac9498-07b4-4c52-a00e-d2c7281887fc/scratchpad/h0g/run/h0g-program.sh
```

- Program sent on standard input: SHA-256
  `f35b455eb55c68c86a3da202d30c9378c83b8259a164e6c0de76b7e300242607`,
  14112 bytes. It is reproduced verbatim in Appendix A.
- SSH start and end times (controller UTC): `2026-10-06T15:11:50.220741364Z`
  and `2026-10-06T15:11:56.547645744Z`.
- SSH exit status `0`. SSH stderr was empty (0 bytes), with no
  authentication, host-key or transport message.
- SSH stdout was 65889 bytes, SHA-256
  `4ee61cd18a71cc9329f024b852642643ef003c02bcdb7f384cbd2fecdc80bd40`. It is
  controller transport only. At closure the program echoed every evidence file
  between `----- BEGIN <name> (<n> bytes) -----` and `----- END <name> -----`
  markers, using bash builtins only, then printed the terminal line.

## Program structure and the retained program

The remote command is the prompt's fixed `bash -s`. The program therefore has
two parts.

1. **Part 1** (1276 bytes) is a single `{ … }` group. Bash parses it completely
   before running it. It runs these steps in order, and each failure stops with
   its own exit code:
   - set `umask 077`;
   - check that `id -u` is numeric and non-zero (exit 70);
   - check that `uname -n` is `Test` (exit 70);
   - check freshness of the evidence path with `test -e` and `test -L` only
     (exit 71, `HARD STOP: evidence path not fresh`);
   - create only the evidence directory, with `mkdir -m 0700` (exit 72);
   - write the rest of standard input to `received-program.part2` (exit 73);
   - check that part 2 begins with `# H0G-PART2-BEGIN` and ends with
     `# H0G-PART2-END`, using builtins (otherwise
     `HARD STOP: program delivery incomplete`, closed and hashed, exit 74);
   - `exec` part 2 under `bash --noprofile --norc`.
2. **Part 2** (12836 bytes) carries out everything else. It does not use
   `set -e`. Every command's exit status is checked explicitly. An `EXIT` trap
   and a `HUP`/`INT`/`TERM` trap close and hash the evidence on every terminal
   path.

**Disclosure — how the exact received program is retained.** Part 2's bytes
are the bytes part 1 actually read from standard input. Part 1 cannot capture
its own text, because bash had already consumed it. Part 2 therefore embeds
part 1 verbatim as a quoted here-document and writes it to
`received-program.part1`. `received-program.sh` is the concatenation of part 1
and part 2.

Its remote SHA-256, recomputed in c001, is
`f35b455eb55c68c86a3da202d30c9378c83b8259a164e6c0de76b7e300242607`
(14112 bytes). That equals the controller's digest of the file it sent. The
echoed copy is also byte-identical to the sent file. The retained part 1 is
therefore an exact reproduction that has been authenticated against the
transmitted program. It is not a capture of the bytes bash read.

## Fixed inputs (checked before connection, as used)

| Input | Value | Source checked |
|---|---|---|
| Evidence path | `/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence` | prompt, authority |
| Capture-root parent | `/var/lib/rp11-capture` | prompt, R3 §9 FI-1 |
| Interpreter | `/usr/bin/python3.14` | prompt, R3 §9 FI-1 |
| A-1 … A-10 | as tabulated below | prompt, R3 §10.2, R5 handback c007, c008, c043, c046, c050, c052, c072, c096, c105, c136, c137 (all values matched) |

No fixed input was missing or malformed.

## A-1 through A-10 comparison

| # | Anchor | Expected (R5) | Observed (H-0G) | Command | Equal |
|---|---|---|---|---|---|
| A-1 | nodename | `Test` | `Test` | c004 `uname -n` | yes |
| A-2 | `/etc/machine-id` SHA-256 | `e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d` | `e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d` | c005 | yes |
| A-3 | kernel release | `7.0.0-31-generic` | `7.0.0-31-generic` | c006 `uname -r` | yes |
| A-4 | `systemd` | `259.5-0ubuntu3.4` | `259.5-0ubuntu3.4` (`ii`) | c007 | yes |
| A-5 | `polkitd` | `127-2ubuntu1.1` | `127-2ubuntu1.1` (`ii`) | c008 | yes |
| A-6 | `libc6` | `2.43-2ubuntu2.4` | `2.43-2ubuntu2.4` (`ii`) | c009 | yes |
| A-7 | `python3.14-minimal` | `3.14.4-1ubuntu0.2` | `3.14.4-1ubuntu0.2` (`ii`) | c010 | yes |
| A-8 | `/usr/bin/python3.14` SHA-256 | `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` | `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` | c011 | yes |
| A-9 | `/var/lib` | dir, `root:root`, `0755`, `(2049, 97831)`, no xattr | dir (not symlink), uid 0/gid 0 `root:root`, `0755`, `(2049, 97831)`, `names=-` | c024 | yes |
| A-10 | `/var/lib` mount row | `/`, `/dev/sda1`, `ext4`, `rw,relatime,discard,errors=remount-ro,commit=30` | `/`, `/dev/sda1`, `ext4`, `rw,relatime,discard,errors=remount-ro,commit=30` | c025 | yes |

The program compared full values exactly, not by prefix:

- A-2 and A-8: the whole `sha256sum` output line;
- A-4 to A-7: the version field, plus status `ii `;
- A-9: all seven fields, and empty xattr names;
- A-10: all four columns of the single data row.

**Byte-identity cross-check against R5** (computed after the run from the
retained manifests; the program did not use it). These pairs have identical
SHA-256 for both `.cmd` and `.out`:

- c004 = R5 c007;
- c005 = R5 c008;
- c007 = R5 c046;
- c008 = R5 c050;
- c009 = R5 c052;
- c010 = R5 c072;
- c011 = R5 c096;
- c025 = R5 c136;
- c026 `.cmd` = R5 c137 `.cmd`.

## G-15a through G-15d

| ID | Command | Result | Outcome |
|---|---|---|---|
| G-15a | c023: Python helper under `/usr/bin/python3.14 -I -S`, `os.lstat('/var/lib/rp11-capture')` then, as a separate call, `os.listxattr('/var/lib/rp11-capture', follow_symlinks=False)` | `lstat … error errno=2 ENOENT`; `listxattr … error errno=2 ENOENT` | **PASS**: `parent=/var/lib/rp11-capture absent (lstat ENOENT; listxattr ENOENT)` |
| G-15b | c024: same helper on `/var/lib` only | `type=dir uid=0 gid=0 owner=root group=root mode=0755 dev=2049 ino=97831 nlink=52`; `names=-` | **PASS**: equal to A-9 (`nlink` recorded, not an anchor) |
| G-15c | c025: `/usr/bin/findmnt --target /var/lib -o TARGET,SOURCE,FSTYPE,OPTIONS` | exit 0; one data row `/ /dev/sda1 ext4 rw,relatime,discard,errors=remount-ro,commit=30` | **PASS**: equal to A-10 |
| G-15d | c026: `/usr/bin/df --output=source,fstype,size,used,avail,pcent,itotal,iused,iavail,target -- /var/lib` | exit 0; one data row `/dev/sda1 ext4 46167704 7570952 38580368 17% 5707520 253747 5453773 /` | **PASS**: source/fstype/target equal to R5 c137 |

The G-15d capacity values are recorded but are not anchors. Compared with R5
c137, used went from 7560980 to 7570952 1K-blocks, available from 38590340 to
38580368, used inodes from 253588 to 253747 and free inodes from 5453932 to
5453773. Size, total inodes and `17%` are unchanged.

No `findmnt`, `df` or following `stat` named `/var/lib/rp11-capture`.
`/var/lib` was not listed, and no other candidate path was inspected.

## Route 1 package and interpreter facts (HF-07, HF-08)

| Cmd | Command | Result |
|---|---|---|
| c012 | `dpkg-query -W -f '${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Abbrev}\t${Source}\n' python3.14` | `python3.14	3.14.4-1ubuntu0.2	amd64	ii 	` (empty Source field) |
| c013 | same, `libpython3.14-minimal` | `libpython3.14-minimal:amd64	3.14.4-1ubuntu0.2	amd64	ii 	python3.14` |
| c014 | same, `libpython3.14-stdlib` | `libpython3.14-stdlib:amd64	3.14.4-1ubuntu0.2	amd64	ii 	python3.14` |
| c015–c017 | `dpkg --verify` each of the three | exit 0, no output for all three |
| c018–c020 | `apt-cache policy` each (local lists; no `apt update`) | Installed = Candidate = `3.14.4-1ubuntu0.2` for all three; version table also lists `3.14.4-1` from `resolute/main` (verbatim in Appendix C) |
| c021 | `stat -c 'name=%n type=%F owner=%U:%G uid=%u gid=%g mode=%a size=%s dev=%d ino=%i nlink=%h' -- /usr/bin/python3.14` (no `-L`, no-follow) | `type=regular file owner=root:root uid=0 gid=0 mode=755 size=7468968 dev=2049 ino=8254 nlink=1` |
| c022 | `/usr/bin/python3.14 -I -S -c <fixed literal>` | `version=3.14.4 (main, Aug 20 2026, 10:41:58) [GCC 15.2.0]`, `isolated=1`, `no_site=1`, `executable=/usr/bin/python3.14`, `prefix=/usr`, `path=['/usr/lib/python314.zip', '/usr/lib/python3.14', '/usr/lib/python3.14/lib-dynload']` |

Every Python invocation used the exact path `/usr/bin/python3.14 -I -S`, never
`/usr/bin/python3`. The helper also sets `sys.dont_write_bytecode = True`.

## Every remote command and exact result

The ledger is reproduced verbatim in Appendix B. Each command's exact `.cmd`,
stdout and stderr are reproduced verbatim in Appendix C. All 26 commands exited
`0`, and all 26 `.err` files are empty.

| Cmd | Class | Purpose | Exit | Result |
|---|---|---|---|---|
| (part 1) | C-ID | `id -u`, `uname -n`, `test -e`/`test -L`, `mkdir -m 0700`, `cat` of stdin | — | uid `1001` (non-root), nodename `Test`, path absent (`test -e` false, `test -L` false), directory created (recorded in `PRE-EVIDENCE`) |
| c001 | C-DIG | SHA-256 of the retained program parts | 0 | part1 `ac14fa25…a8df`, part2 `2af48c49…a8eb`, whole `f35b455e…2607` |
| c002 | C-ID | `id -u` | 0 | `1001`, equal to part 1 |
| c003 | C-ID | `id -un` | 0 | `ubuntu` |
| c004–c011 | — | A-1 … A-8 | 0 | all equal (table above) |
| c012–c022 | C-PKG/C-STAT/C-VER | HF-07, HF-08 | 0 | table above |
| c023–c026 | C-STAT | G-15a … G-15d | 0 | table above |

Per-command start and end times are in the ledger. The run on the host lasted
from `2026-10-06T15:11:53.755666Z` (part 2 start) to
`2026-10-06T15:11:56.434701Z` (close).

**Fail-closed checks added beyond the prompt's literal list.** None of them was
triggered. The program stops with a precise `HARD STOP` if:

- `id -un` is not `ubuntu`, or c002 differs from part 1's `id -u`;
- an anchor package's status is not `ii `;
- `/usr/bin/python3.14` is not a regular file under no-follow `stat`;
- the c022 output lacks `isolated=1`, `no_site=1` and
  `executable=/usr/bin/python3.14`;
- any required command exits non-zero, including `dpkg --verify`;
- a helper output does not have its expected shape.

These checks implement the prompt's "any other unexpected condition" clause.

## Evidence closure, manifest and hashes

The evidence directory is `/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence`,
mode `0700`, created by part 1. It contains 88 files, each `ubuntu:ubuntu`
`0600` with `nlink=1` (Appendix B `INVENTORY`):

- **Program:** `received-program.part1`, `received-program.part2`,
  `received-program.sh`.
- **Pre-evidence record:** `PRE-EVIDENCE`.
- **Command/result ledger:** `LEDGER`.
- **Bounded fact file:** `FACTS`.
- **Command records:** 26 `.cmd`, 26 `.out` and 26 `.err` files.
- **Closing files:** `TERMINAL-STATE`, `INVENTORY`, `MANIFEST.payload`,
  `MANIFEST.final`.

| Closing file | SHA-256 | Bytes |
|---|---|---|
| `MANIFEST.payload` (86 entries: every file except the two manifests) | `cc0c3f29221c035241efdad71852776258c69e68e530c145925d3f4a74f1da3d` | 8427 |
| `MANIFEST.final` (SHA-256 of `MANIFEST.payload`) | `02e6d7be2eb4922a69ba865618659ae54f51438bf3300ea97ef488661e9b2b10` | 83 |
| `INVENTORY` | `4c777f3d86f067f92169cc7c7c2593286909dda98509fccabc97c6dbffd88890` | — |
| `TERMINAL-STATE` | `27c0af86624e119984e4fc4c3f3e52c07fe6a582900400039b7d13cb69c320f9` | 104 |
| `received-program.sh` | `f35b455eb55c68c86a3da202d30c9378c83b8259a164e6c0de76b7e300242607` | 14112 |

**Controller-side verification, without revisiting the host.** The controller
parsed the echoed stdout into its 88 blocks. Each block's length equals its
declared byte count. All 86 `MANIFEST.payload` entries match the SHA-256 of
the corresponding echoed bytes (0 mismatches), and `MANIFEST.final` matches
`MANIFEST.payload`. These digests authenticate and describe the retained
bytes. They do not reproduce them (R3 §12.7).

**Retention disposition (R3 §12.6).** The evidence path is to be retained as
evidence until the independent Codex review of H-0G and its composition with
R5. Whether that review or any later review or recovery needs the path's host
bytes, rather than this durable record, is for that review to state (RD-2,
RD-5). Until then the dependency is open. This handback does not make the path
cleanup-eligible.

## Disclosures about controller-side activity

- Before the connection, the controller ran local dry runs of the same
  template, with test parameters, on the production workspace controller
  itself. The parameters were the local nodename and user, local anchors,
  `/usr/bin/python3.12`, `python3.12*` packages and evidence paths under the
  session scratchpad. The dry runs exercised these paths:
  - PASS, both piped and file-redirected;
  - evidence path not fresh;
  - nodename mismatch, with no directory created;
  - composition anchor changed;
  - capture-root parent present (a scratch directory);
  - parent unobservable (`errno 13`, using a mode-`000` scratch directory);
  - truncated program delivery.

  Those runs ran only the same read-only commands on the controller host:
  `id`, `uname`, `sha256sum`, `dpkg-query`, `dpkg --verify`, `apt-cache
  policy`, `stat`, `python3.12 -I -S`, `lstat`/`listxattr` of the local
  `/var/lib/rp11-capture` and `/var/lib`, `findmnt` and `df`. They wrote only
  inside the scratchpad. The production program differs from the tested
  template only in its fixed-input substitutions, and that was confirmed by
  `diff`.
- The controller also read local values (`uname`, `dpkg-query`, `stat`,
  `findmnt`) to build the test parameters. No `oracle-test` access other than
  the single connection occurred.

## Files changed

Repository files created or changed by this assignment:

- `docs/review/phase-5-0-p5-r5-rp11-h1-h0g-r1-handback.md`: this handback
  (new);
- `docs/review/Handover information`: authority and prompt marked consumed,
  pointer to this handback;
- `docs/project-management/status.md`: current-state pointer;
- `docs/implementation-plan.md`: §20 only;
- `docs/operations/disposable-test-server.md`: the restriction banner only.

The 55 pre-existing working-tree changes and untracked files were preserved.
Nothing was staged, committed or pushed.

## Checks run and not run

Run:

- prompt byte count and SHA-256 against the authority pin (equal);
- recomputation of the authority SHA-256;
- R5 anchor cross-check (all ten matched the prompt);
- `bash -n` of the program;
- the local dry runs listed above;
- the single H-0G connection;
- controller verification of the echoed evidence against both manifests;
- repository-relative link check of the five changed files: 115 links, 0
  broken;
- `git diff --check` on the tracked changes: exit 0, no output;
- `git diff --no-index --check /dev/null` on this untracked handback: it
  reports trailing whitespace on 4 lines. All 4 are inside verbatim retained
  evidence (`FACTS` and the c007/c012 `dpkg-query` output with an empty
  `${Source}` field). They are kept byte-exact deliberately.

Not run, because they are outside the assignment or prohibited:

- application test suites, builds, linters and type checkers;
- any second connection or retry;
- any evidence revisit;
- any composition with R5.

## Prohibited-action confirmation

Every prohibition held:

- **One connection.** Exactly one SSH connection, with forwarding disabled
  (`ClearAllForwardings`, `ForwardAgent=no`, `ForwardX11=no`), `BatchMode`,
  and no local command. There was no preflight and no retry.
- **Unprivileged.** No `sudo` or other privilege path; all commands ran as
  uid 1001 `ubuntu`.
- **One write.** The only remote write was the creation of, and writes inside,
  the fresh exclusive evidence path.
- **No listing.** `/var/tmp` was not listed, and neither was `/var/lib`.
- **No forbidden paths.** There was no access to any retained R1–R5 or
  agent-client evidence path. There was no access of any kind to
  `/opt/freedom-blades/platform` on `oracle-test`, and no repository
  retrieval or inspection.
- **No sensitive data.** No credentials, secrets, player data,
  `/etc/polkit-1/rules.d`, CL-21i path or agent-client path was accessed, and
  there was no client search.
- **No package operations.** Nothing was installed, removed or updated, and
  there was no `apt update` (only local `apt-cache policy` reads).
- **No other operations.** There was:
  - no build, test, service or database access;
  - no cleanup or workspace recreation;
  - no OH-S2, H-1 or H-2, and no activation;
  - no commit or push.
- **No composition claim.** The executor does not claim a composed `H-0 PASS`.

## Unresolved questions and reviewer focus

1. Confirm that the part-1 retention method is acceptable as "exact received
   program" retention. Part 1 is reproduced from an embedded literal and
   authenticated by the whole-program digest.
2. Confirm that the added fail-closed checks are within the prompt's "any
   other unexpected condition" clause.
3. Decide composition with R5, using these inputs:
   - R5 `MANIFEST.payload`:
     `f116244f94ca3ea42e51b0d1c2ea3e0c99257cecfafc5b9c13bd7fb742724503`;
   - H-0G `MANIFEST.payload`:
     `cc0c3f29221c035241efdad71852776258c69e68e530c145925d3f4a74f1da3d`;
   - the two observation times: R5 `2026-10-06T02:49Z`, H-0G
     `2026-10-06T15:11Z`.

   Also state the host-byte dependency for both evidence paths (RD-2).

## Appendix A — verbatim program sent and retained (`received-program.sh`)

Part 1 is the leading `{ … }` group (1276 bytes); part 2 begins at `# H0G-PART2-BEGIN`.

`received-program.sh` (14112 bytes)

````text
{
set -u
umask 077
E='/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence'
u=$(/usr/bin/id -u) || { printf 'HARD STOP: remote identity unobservable\n' >&2; exit 70; }
case $u in ''|*[!0-9]*) printf 'HARD STOP: remote identity unobservable\n' >&2; exit 70;; esac
if [ "$u" = 0 ]; then printf 'HARD STOP: remote identity is root\n' >&2; exit 70; fi
n=$(/usr/bin/uname -n) || { printf 'HARD STOP: nodename unobservable\n' >&2; exit 70; }
if [ "$n" != 'Test' ]; then printf 'HARD STOP: nodename mismatch\n' >&2; exit 70; fi
if test -e "$E" || test -L "$E"; then printf 'HARD STOP: evidence path not fresh\n' >&2; exit 71; fi
/usr/bin/mkdir -m 0700 -- "$E" || { printf 'HARD STOP: evidence directory not created\n' >&2; exit 72; }
/usr/bin/cat > "$E/received-program.part2" || { printf 'HARD STOP: program delivery failed\n' >&2; exit 73; }
IFS= read -r -d '' p2 < "$E/received-program.part2"
case $p2 in '# H0G-PART2-BEGIN'$'\n'*$'\n''# H0G-PART2-END'$'\n') ;; *)
  printf 'HARD STOP: program delivery incomplete\n' > "$E/TERMINAL-STATE"
  ( cd -- "$E" && /usr/bin/sha256sum -- received-program.part2 TERMINAL-STATE > MANIFEST.payload )
  printf 'HARD STOP: program delivery incomplete\n' >&2; exit 74;;
esac
exec /bin/bash --noprofile --norc "$E/received-program.part2" "$u" "$n"
}
# H0G-PART2-BEGIN
main() {
set -u
umask 077
export TZ=UTC
cd / || exit 80
WORK_ID='C-P5.0-R5-RP11-H1-OH-S0B-S1-H0G-R1-20261006-06'
E='/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence'
PY='/usr/bin/python3.14'
PARENT='/var/lib/rp11-capture'
ANC='/var/lib'
PRE_UID=$1
PRE_NODE=$2
FILES=()
TERMINAL=''
FINISHED=0
OUT=''
RC=0

stamp() { local _now=$EPOCHREALTIME; printf -v "$1" '%(%Y-%m-%dT%H:%M:%S)T.%sZ' "${_now%.*}" "${_now#*.}"; }
track() { local f; for f in "${FILES[@]}"; do [ "$f" = "$1" ] && return 0; done; FILES+=("$1"); }
wnew() { track "$1"; printf '%s' "$2" > "$E/$1"; }
append() { track "$1"; printf '%s' "$2" >> "$E/$1"; }
fact() { append FACTS "$1"$'\n'; }
slurp() { OUT=''; IFS= read -r -d '' OUT < "$E/$1"; return 0; }

run() {
  local id=$1 cls=$2 s e q; shift 2
  printf -v q '%q ' "$@"
  wnew "$id.cmd" "${q% }"$'\n'
  track "$id.out"; track "$id.err"
  stamp s
  "$@" > "$E/$id.out" 2> "$E/$id.err" < /dev/null
  RC=$?
  stamp e
  append LEDGER "$id"$'\t'"$cls"$'\t'"$s"$'\t'"$e"$'\t'"exit=$RC"$'\n'
  slurp "$id.out"
}

finish() {
  [ "$FINISHED" = 1 ] && return 0
  set +u
  local closed f c
  stamp closed
  wnew TERMINAL-STATE "$TERMINAL"$'\n'"work_id=$WORK_ID"$'\n'"closed_utc=$closed"$'\n'
  ( cd -- "$E" && /usr/bin/stat -c $'%n\t%F\t%U:%G\t%a\t%s\t%h' -- "${FILES[@]}" > INVENTORY 2>&1 )
  track INVENTORY
  ( cd -- "$E" && /usr/bin/sha256sum -- "${FILES[@]}" > MANIFEST.payload 2>&1 )
  ( cd -- "$E" && /usr/bin/sha256sum -- MANIFEST.payload > MANIFEST.final 2>&1 )
  for f in "${FILES[@]}" MANIFEST.payload MANIFEST.final; do
    c=''; IFS= read -r -d '' c < "$E/$f"
    printf -- '----- BEGIN %s (%d bytes) -----\n%s\n----- END %s -----\n' "$f" "${#c}" "$c" "$f"
  done
  printf 'H0G-TERMINAL: %s\n' "$TERMINAL"
  FINISHED=1
}

stop() { TERMINAL="HARD STOP: $1"; finish; exit 10; }
trap 'stop "unexpected signal"' HUP INT TERM
trap 'set +u; [ "$FINISHED" = 1 ] || { [ -n "$TERMINAL" ] || TERMINAL="HARD STOP: unexpected program termination"; finish; }' EXIT

# Retain the exact received program: part 1 is reproduced from this literal,
# part 2 was written by part 1 from standard input.
P1=''
IFS= read -r -d '' P1 <<'H0G_PART1_EOF'
{
set -u
umask 077
E='/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence'
u=$(/usr/bin/id -u) || { printf 'HARD STOP: remote identity unobservable\n' >&2; exit 70; }
case $u in ''|*[!0-9]*) printf 'HARD STOP: remote identity unobservable\n' >&2; exit 70;; esac
if [ "$u" = 0 ]; then printf 'HARD STOP: remote identity is root\n' >&2; exit 70; fi
n=$(/usr/bin/uname -n) || { printf 'HARD STOP: nodename unobservable\n' >&2; exit 70; }
if [ "$n" != 'Test' ]; then printf 'HARD STOP: nodename mismatch\n' >&2; exit 70; fi
if test -e "$E" || test -L "$E"; then printf 'HARD STOP: evidence path not fresh\n' >&2; exit 71; fi
/usr/bin/mkdir -m 0700 -- "$E" || { printf 'HARD STOP: evidence directory not created\n' >&2; exit 72; }
/usr/bin/cat > "$E/received-program.part2" || { printf 'HARD STOP: program delivery failed\n' >&2; exit 73; }
IFS= read -r -d '' p2 < "$E/received-program.part2"
case $p2 in '# H0G-PART2-BEGIN'$'\n'*$'\n''# H0G-PART2-END'$'\n') ;; *)
  printf 'HARD STOP: program delivery incomplete\n' > "$E/TERMINAL-STATE"
  ( cd -- "$E" && /usr/bin/sha256sum -- received-program.part2 TERMINAL-STATE > MANIFEST.payload )
  printf 'HARD STOP: program delivery incomplete\n' >&2; exit 74;;
esac
exec /bin/bash --noprofile --norc "$E/received-program.part2" "$u" "$n"
}
H0G_PART1_EOF
wnew received-program.part1 "$P1"
track received-program.part2
slurp received-program.part2
wnew received-program.sh "$P1$OUT"
stamp T0
wnew PRE-EVIDENCE "work_id=$WORK_ID"$'\n'"stage1_id_u=$PRE_UID"$'\n'"stage1_uname_n=$PRE_NODE"$'\n'"stage1_freshness=test -e false; test -L false"$'\n'"stage1_mkdir=$E mode 0700"$'\n'"stage2_start_utc=$T0"$'\n'
wnew LEDGER ''
wnew FACTS ''

run c001-program-sha256 C-DIG /usr/bin/sha256sum -- "$E/received-program.part1" "$E/received-program.part2" "$E/received-program.sh"
[ "$RC" = 0 ] || stop "unexpected condition: c001 exit $RC"

run c002-id-u C-ID /usr/bin/id -u
[ "$RC" = 0 ] && [ "$OUT" = "$PRE_UID"$'\n' ] && [ "$PRE_UID" != 0 ] || stop "unexpected condition: c002 identity"
run c003-id-un C-ID /usr/bin/id -un
[ "$RC" = 0 ] && [ "$OUT" = 'ubuntu'$'\n' ] || stop "unexpected condition: c003 identity"
fact "identity uid=$PRE_UID user=${OUT%$'\n'}"

# A-1 .. A-8
run c004-a1-uname-n C-ID /usr/bin/uname -n
[ "$RC" = 0 ] || stop "unexpected condition: c004 exit $RC"
fact "A-1 observed=${OUT%$'\n'} expected=Test"
[ "$OUT" = 'Test'$'\n' ] || stop "composition anchor changed"

run c005-a2-machine-id-sha256 C-DIG /usr/bin/sha256sum /etc/machine-id
[ "$RC" = 0 ] || stop "unexpected condition: c005 exit $RC"
fact "A-2 observed=${OUT%%  *} expected=e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d"
[ "$OUT" = 'e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d  /etc/machine-id'$'\n' ] || stop "composition anchor changed"

run c006-a3-uname-r C-ID /usr/bin/uname -r
[ "$RC" = 0 ] || stop "unexpected condition: c006 exit $RC"
fact "A-3 observed=${OUT%$'\n'} expected=7.0.0-31-generic"
[ "$OUT" = '7.0.0-31-generic'$'\n' ] || stop "composition anchor changed"

DQF='${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Abbrev}\t${Source}\n'
anchor_pkg() {
  local id=$1 a=$2 pkg=$3 want=$4 x f
  run "$id" C-PKG /usr/bin/dpkg-query -W -f "$DQF" "$pkg"
  [ "$RC" = 0 ] || stop "unexpected condition: $id exit $RC"
  x=${OUT%$'\n'}
  IFS=$'\t' read -r -a f <<< "$x"
  fact "$a package=$pkg observed_version=${f[1]-} observed_status=${f[3]-} expected=$want status_expected=ii"
  [ "$OUT" != "$x" ] && [[ $x != *$'\n'* ]] && [ "${f[1]-}" = "$want" ] && [ "${f[3]-}" = 'ii ' ] || stop "composition anchor changed"
}
anchor_pkg c007-a4-dpkg-query-systemd A-4 systemd '259.5-0ubuntu3.4'
anchor_pkg c008-a5-dpkg-query-polkitd A-5 polkitd '127-2ubuntu1.1'
anchor_pkg c009-a6-dpkg-query-libc6 A-6 libc6 '2.43-2ubuntu2.4'
anchor_pkg c010-a7-dpkg-query-python3.14-minimal A-7 'python3.14-minimal' '3.14.4-1ubuntu0.2'

run c011-a8-python-sha256 C-DIG /usr/bin/sha256sum -- "$PY"
[ "$RC" = 0 ] || stop "unexpected condition: c011 exit $RC"
fact "A-8 observed=${OUT%%  *} expected=be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd"
[ "$OUT" = 'be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd  '"$PY"$'\n' ] || stop "composition anchor changed"

# Route 1 package facts
n=12
for p in 'python3.14' 'libpython3.14-minimal' 'libpython3.14-stdlib'; do
  printf -v id 'c%03d-hf07-dpkg-query-%s' "$n" "$p"; n=$((n+1))
  run "$id" C-PKG /usr/bin/dpkg-query -W -f "$DQF" "$p"
  [ "$RC" = 0 ] || stop "unexpected condition: $id exit $RC"
  fact "HF-07 dpkg-query $p: ${OUT%$'\n'}"
done
for p in 'python3.14' 'libpython3.14-minimal' 'libpython3.14-stdlib'; do
  printf -v id 'c%03d-hf07-dpkg-verify-%s' "$n" "$p"; n=$((n+1))
  run "$id" C-PKG /usr/bin/dpkg --verify "$p"
  [ "$RC" = 0 ] || stop "unexpected condition: $id exit $RC"
  fact "HF-07 dpkg --verify $p: exit=0 stdout_bytes=${#OUT}"
done
for p in 'python3.14' 'libpython3.14-minimal' 'libpython3.14-stdlib'; do
  printf -v id 'c%03d-hf07-apt-cache-policy-%s' "$n" "$p"; n=$((n+1))
  run "$id" C-PKG /usr/bin/apt-cache policy "$p"
  [ "$RC" = 0 ] || stop "unexpected condition: $id exit $RC"
  fact "HF-07 apt-cache policy $p: exit=0 stdout_bytes=${#OUT}"
done

# HF-08 exact-path interpreter
run c021-hf08-stat-python C-STAT /usr/bin/stat -c 'name=%n type=%F owner=%U:%G uid=%u gid=%g mode=%a size=%s dev=%d ino=%i nlink=%h' -- "$PY"
[ "$RC" = 0 ] || stop "unexpected condition: c021 exit $RC"
fact "HF-08 stat ${OUT%$'\n'}"
[[ $OUT == "name=$PY type=regular file "* ]] || stop "unexpected condition: $PY not a regular file"

run c022-hf08-python-version C-VER "$PY" -I -S -c 'import sys
print("version=" + sys.version.replace("\n", " "))
print("isolated=" + str(sys.flags.isolated))
print("no_site=" + str(sys.flags.no_site))
print("executable=" + sys.executable)
print("prefix=" + sys.prefix)
print("path=" + repr(sys.path))
'
[ "$RC" = 0 ] || stop "unexpected condition: c022 exit $RC"
fact "HF-08 python ${OUT//$'\n'/ | }"
[[ $OUT == *$'\n'isolated=1$'\n'no_site=1$'\n'executable="$PY"$'\n'* ]] || stop "unexpected condition: c022 interpreter flags or executable"

HELPER='import errno, grp, os, pwd, stat, sys
sys.dont_write_bytecode = True
def ename(n):
    return errno.errorcode.get(n, "?")
def kind(m):
    for t, f in (("dir", stat.S_ISDIR), ("reg", stat.S_ISREG), ("symlink", stat.S_ISLNK), ("chr", stat.S_ISCHR), ("blk", stat.S_ISBLK), ("fifo", stat.S_ISFIFO), ("sock", stat.S_ISSOCK)):
        if f(m):
            return t
    return "other"
def nm(f, i):
    try:
        return f(i)[0]
    except KeyError:
        return "?"
p = sys.argv[1]
try:
    st = os.lstat(p)
except OSError as e:
    print("lstat\t" + p + "\terror\terrno=" + str(e.errno) + "\t" + ename(e.errno))
else:
    m = st.st_mode
    print("\t".join(["lstat", p, "ok", "type=" + kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid), "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid), "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino), "nlink=" + str(st.st_nlink)]))
try:
    xs = os.listxattr(p, follow_symlinks=False)
except OSError as e:
    print("listxattr\t" + p + "\terror\terrno=" + str(e.errno) + "\t" + ename(e.errno))
else:
    print("listxattr\t" + p + "\tok\tnames=" + (",".join(sorted(xs)) or "-"))
'

# G-15a capture-root parent: lstat and no-follow listxattr only
run c023-g15a-parent-lstat-listxattr C-STAT "$PY" -I -S -c "$HELPER" "$PARENT"
[ "$RC" = 0 ] || stop "unexpected condition: c023 exit $RC"
mapfile -t L < "$E/c023-g15a-parent-lstat-listxattr.out"
fact "G-15a ${L[0]-} | ${L[1]-}"
[ "${#L[@]}" = 2 ] || stop "unexpected condition: c023 output shape"
IFS=$'\t' read -r -a L0 <<< "${L[0]}"
IFS=$'\t' read -r -a L1 <<< "${L[1]}"
[ "${L0[0]-}" = lstat ] && [ "${L1[0]-}" = listxattr ] || stop "unexpected condition: c023 output shape"
if [ "${L0[2]-}" = ok ] || [ "${L1[2]-}" = ok ]; then stop "capture-root parent present before CPP"; fi
if [ "${L0[3]-}" != errno=2 ]; then x=${L0[3]-errno=?}; stop "capture-root parent unobservable (errno ${x#errno=})"; fi
if [ "${L1[3]-}" != errno=2 ]; then x=${L1[3]-errno=?}; stop "capture-root parent unobservable (errno ${x#errno=})"; fi
fact "G-15a result=parent=$PARENT absent (lstat ENOENT; listxattr ENOENT)"

# G-15b existing ancestor
run c024-g15b-ancestor-lstat-listxattr C-STAT "$PY" -I -S -c "$HELPER" "$ANC"
[ "$RC" = 0 ] || stop "unexpected condition: c024 exit $RC"
mapfile -t L < "$E/c024-g15b-ancestor-lstat-listxattr.out"
fact "G-15b ${L[0]-} | ${L[1]-}"
[ "${#L[@]}" = 2 ] || stop "unexpected condition: c024 output shape"
IFS=$'\t' read -r -a L0 <<< "${L[0]}"
IFS=$'\t' read -r -a L1 <<< "${L[1]}"
[ "${L0[0]-}" = lstat ] && [ "${L1[0]-}" = listxattr ] || stop "unexpected condition: c024 output shape"
if [ "${L0[2]-}" != ok ]; then
  [ "${L0[3]-}" = errno=2 ] && stop "capture-root ancestor invalid"
  x=${L0[3]-errno=?}; stop "unexpected condition: capture-root ancestor unobservable (errno ${x#errno=})"
fi
[ "${L0[3]-}" = type=dir ] || stop "capture-root ancestor invalid"
[ "${L1[2]-}" = ok ] || stop "unexpected condition: ancestor listxattr ${L1[3]-}"
[ "${L0[*]:4:7}" = 'uid=0 gid=0 owner=root group=root mode=0755 dev=2049 ino=97831' ] && [ "${L1[3]-}" = names=- ] || stop "composition anchor changed"
fact "A-9 equal=yes"

# G-15c ancestor mount row
run c025-g15c-findmnt-ancestor C-STAT /usr/bin/findmnt --target "$ANC" -o TARGET,SOURCE,FSTYPE,OPTIONS
[ "$RC" = 0 ] || stop "ancestor filesystem facts unavailable"
mapfile -t L < "$E/c025-g15c-findmnt-ancestor.out"
fact "G-15c rows=$(( ${#L[@]} - 1 )) row=${L[1]-}"
[ "${#L[@]}" = 2 ] || stop "composition anchor changed"
read -r -a R <<< "${L[1]}"
[ "${#R[@]}" = 4 ] && [ "${R[0]}" = '/' ] && [ "${R[1]}" = '/dev/sda1' ] && [ "${R[2]}" = 'ext4' ] && [ "${R[3]}" = 'rw,relatime,discard,errors=remount-ro,commit=30' ] || stop "composition anchor changed"
fact "A-10 equal=yes"

# G-15d ancestor filesystem and capacity
run c026-g15d-df-ancestor C-STAT /usr/bin/df --output=source,fstype,size,used,avail,pcent,itotal,iused,iavail,target -- "$ANC"
[ "$RC" = 0 ] || stop "ancestor filesystem facts unavailable"
mapfile -t L < "$E/c026-g15d-df-ancestor.out"
fact "G-15d rows=$(( ${#L[@]} - 1 )) row=${L[1]-}"
[ "${#L[@]}" = 2 ] || stop "composition anchor changed"
read -r -a R <<< "${L[1]}"
[ "${#R[@]}" = 10 ] && [ "${R[0]}" = '/dev/sda1' ] && [ "${R[1]}" = 'ext4' ] && [ "${R[9]}" = '/' ] || stop "composition anchor changed"
fact "G-15d comparison columns equal=yes capacity size=${R[2]} used=${R[3]} avail=${R[4]} pcent=${R[5]} itotal=${R[6]} iused=${R[7]} iavail=${R[8]}"

TERMINAL='H-0G PASS'
finish
exit 0
}
main "$@"
exit $?
# H0G-PART2-END
````

## Appendix B — verbatim retained context and closing files

### `PRE-EVIDENCE`

`PRE-EVIDENCE` (255 bytes)

````text
work_id=C-P5.0-R5-RP11-H1-OH-S0B-S1-H0G-R1-20261006-06
stage1_id_u=1001
stage1_uname_n=Test
stage1_freshness=test -e false; test -L false
stage1_mkdir=/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence mode 0700
stage2_start_utc=2026-10-06T15:11:53.755666Z
````

### `LEDGER`

`LEDGER` (2569 bytes)

````text
c001-program-sha256	C-DIG	2026-10-06T15:11:53.756440Z	2026-10-06T15:11:53.832324Z	exit=0
c002-id-u	C-ID	2026-10-06T15:11:53.833335Z	2026-10-06T15:11:53.840355Z	exit=0
c003-id-un	C-ID	2026-10-06T15:11:53.841363Z	2026-10-06T15:11:53.848182Z	exit=0
c004-a1-uname-n	C-ID	2026-10-06T15:11:53.849440Z	2026-10-06T15:11:53.931012Z	exit=0
c005-a2-machine-id-sha256	C-DIG	2026-10-06T15:11:53.932404Z	2026-10-06T15:11:53.938711Z	exit=0
c006-a3-uname-r	C-ID	2026-10-06T15:11:53.940171Z	2026-10-06T15:11:53.946617Z	exit=0
c007-a4-dpkg-query-systemd	C-PKG	2026-10-06T15:11:53.948253Z	2026-10-06T15:11:54.041248Z	exit=0
c008-a5-dpkg-query-polkitd	C-PKG	2026-10-06T15:11:54.043192Z	2026-10-06T15:11:54.137590Z	exit=0
c009-a6-dpkg-query-libc6	C-PKG	2026-10-06T15:11:54.139650Z	2026-10-06T15:11:54.233816Z	exit=0
c010-a7-dpkg-query-python3.14-minimal	C-PKG	2026-10-06T15:11:54.235974Z	2026-10-06T15:11:54.330127Z	exit=0
c011-a8-python-sha256	C-DIG	2026-10-06T15:11:54.332298Z	2026-10-06T15:11:54.539799Z	exit=0
c012-hf07-dpkg-query-python3.14	C-PKG	2026-10-06T15:11:54.541977Z	2026-10-06T15:11:54.636581Z	exit=0
c013-hf07-dpkg-query-libpython3.14-minimal	C-PKG	2026-10-06T15:11:54.638887Z	2026-10-06T15:11:54.734259Z	exit=0
c014-hf07-dpkg-query-libpython3.14-stdlib	C-PKG	2026-10-06T15:11:54.736673Z	2026-10-06T15:11:54.831256Z	exit=0
c015-hf07-dpkg-verify-python3.14	C-PKG	2026-10-06T15:11:54.833717Z	2026-10-06T15:11:54.955774Z	exit=0
c016-hf07-dpkg-verify-libpython3.14-minimal	C-PKG	2026-10-06T15:11:55.028449Z	2026-10-06T15:11:55.585262Z	exit=0
c017-hf07-dpkg-verify-libpython3.14-stdlib	C-PKG	2026-10-06T15:11:55.587452Z	2026-10-06T15:11:55.929350Z	exit=0
c018-hf07-apt-cache-policy-python3.14	C-PKG	2026-10-06T15:11:55.932306Z	2026-10-06T15:11:55.976184Z	exit=0
c019-hf07-apt-cache-policy-libpython3.14-minimal	C-PKG	2026-10-06T15:11:55.979192Z	2026-10-06T15:11:56.139814Z	exit=0
c020-hf07-apt-cache-policy-libpython3.14-stdlib	C-PKG	2026-10-06T15:11:56.142240Z	2026-10-06T15:11:56.242787Z	exit=0
c021-hf08-stat-python	C-STAT	2026-10-06T15:11:56.245247Z	2026-10-06T15:11:56.256284Z	exit=0
c022-hf08-python-version	C-VER	2026-10-06T15:11:56.259799Z	2026-10-06T15:11:56.279335Z	exit=0
c023-g15a-parent-lstat-listxattr	C-STAT	2026-10-06T15:11:56.283402Z	2026-10-06T15:11:56.349183Z	exit=0
c024-g15b-ancestor-lstat-listxattr	C-STAT	2026-10-06T15:11:56.354326Z	2026-10-06T15:11:56.376235Z	exit=0
c025-g15c-findmnt-ancestor	C-STAT	2026-10-06T15:11:56.379408Z	2026-10-06T15:11:56.386834Z	exit=0
c026-g15d-df-ancestor	C-STAT	2026-10-06T15:11:56.429139Z	2026-10-06T15:11:56.433583Z	exit=0
````

### `FACTS`

`FACTS` (2613 bytes)

````text
identity uid=1001 user=ubuntu
A-1 observed=Test expected=Test
A-2 observed=e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d expected=e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d
A-3 observed=7.0.0-31-generic expected=7.0.0-31-generic
A-4 package=systemd observed_version=259.5-0ubuntu3.4 observed_status=ii  expected=259.5-0ubuntu3.4 status_expected=ii
A-5 package=polkitd observed_version=127-2ubuntu1.1 observed_status=ii  expected=127-2ubuntu1.1 status_expected=ii
A-6 package=libc6 observed_version=2.43-2ubuntu2.4 observed_status=ii  expected=2.43-2ubuntu2.4 status_expected=ii
A-7 package=python3.14-minimal observed_version=3.14.4-1ubuntu0.2 observed_status=ii  expected=3.14.4-1ubuntu0.2 status_expected=ii
A-8 observed=be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd expected=be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd
HF-07 dpkg-query python3.14: python3.14	3.14.4-1ubuntu0.2	amd64	ii 	
HF-07 dpkg-query libpython3.14-minimal: libpython3.14-minimal:amd64	3.14.4-1ubuntu0.2	amd64	ii 	python3.14
HF-07 dpkg-query libpython3.14-stdlib: libpython3.14-stdlib:amd64	3.14.4-1ubuntu0.2	amd64	ii 	python3.14
HF-07 dpkg --verify python3.14: exit=0 stdout_bytes=0
HF-07 dpkg --verify libpython3.14-minimal: exit=0 stdout_bytes=0
HF-07 dpkg --verify libpython3.14-stdlib: exit=0 stdout_bytes=0
HF-07 apt-cache policy python3.14: exit=0 stdout_bytes=469
HF-07 apt-cache policy libpython3.14-minimal: exit=0 stdout_bytes=480
HF-07 apt-cache policy libpython3.14-stdlib: exit=0 stdout_bytes=479
HF-08 stat name=/usr/bin/python3.14 type=regular file owner=root:root uid=0 gid=0 mode=755 size=7468968 dev=2049 ino=8254 nlink=1
HF-08 python version=3.14.4 (main, Aug 20 2026, 10:41:58) [GCC 15.2.0] | isolated=1 | no_site=1 | executable=/usr/bin/python3.14 | prefix=/usr | path=['/usr/lib/python314.zip', '/usr/lib/python3.14', '/usr/lib/python3.14/lib-dynload'] | 
G-15a lstat	/var/lib/rp11-capture	error	errno=2	ENOENT | listxattr	/var/lib/rp11-capture	error	errno=2	ENOENT
G-15a result=parent=/var/lib/rp11-capture absent (lstat ENOENT; listxattr ENOENT)
G-15b lstat	/var/lib	ok	type=dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=97831	nlink=52 | listxattr	/var/lib	ok	names=-
A-9 equal=yes
G-15c rows=1 row=/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30
A-10 equal=yes
G-15d rows=1 row=/dev/sda1      ext4  46167704 7570952 38580368  17% 5707520 253747 5453773 /
G-15d comparison columns equal=yes capacity size=46167704 used=7570952 avail=38580368 pcent=17% itotal=5707520 iused=253747 iavail=5453773
````

### `TERMINAL-STATE`

`TERMINAL-STATE` (104 bytes)

````text
H-0G PASS
work_id=C-P5.0-R5-RP11-H1-OH-S0B-S1-H0G-R1-20261006-06
closed_utc=2026-10-06T15:11:56.434701Z
````

### `INVENTORY`

`INVENTORY` (5982 bytes)

````text
received-program.part1	regular file	ubuntu:ubuntu	600	1276	1
received-program.part2	regular file	ubuntu:ubuntu	600	12836	1
received-program.sh	regular file	ubuntu:ubuntu	600	14112	1
PRE-EVIDENCE	regular file	ubuntu:ubuntu	600	255	1
LEDGER	regular file	ubuntu:ubuntu	600	2569	1
FACTS	regular file	ubuntu:ubuntu	600	2613	1
c001-program-sha256.cmd	regular file	ubuntu:ubuntu	600	235	1
c001-program-sha256.out	regular file	ubuntu:ubuntu	600	411	1
c001-program-sha256.err	regular empty file	ubuntu:ubuntu	600	0	1
c002-id-u.cmd	regular file	ubuntu:ubuntu	600	15	1
c002-id-u.out	regular file	ubuntu:ubuntu	600	5	1
c002-id-u.err	regular empty file	ubuntu:ubuntu	600	0	1
c003-id-un.cmd	regular file	ubuntu:ubuntu	600	16	1
c003-id-un.out	regular file	ubuntu:ubuntu	600	7	1
c003-id-un.err	regular empty file	ubuntu:ubuntu	600	0	1
c004-a1-uname-n.cmd	regular file	ubuntu:ubuntu	600	18	1
c004-a1-uname-n.out	regular file	ubuntu:ubuntu	600	5	1
c004-a1-uname-n.err	regular empty file	ubuntu:ubuntu	600	0	1
c005-a2-machine-id-sha256.cmd	regular file	ubuntu:ubuntu	600	35	1
c005-a2-machine-id-sha256.out	regular file	ubuntu:ubuntu	600	82	1
c005-a2-machine-id-sha256.err	regular empty file	ubuntu:ubuntu	600	0	1
c006-a3-uname-r.cmd	regular file	ubuntu:ubuntu	600	18	1
c006-a3-uname-r.out	regular file	ubuntu:ubuntu	600	17	1
c006-a3-uname-r.err	regular empty file	ubuntu:ubuntu	600	0	1
c007-a4-dpkg-query-systemd.cmd	regular file	ubuntu:ubuntu	600	135	1
c007-a4-dpkg-query-systemd.out	regular file	ubuntu:ubuntu	600	36	1
c007-a4-dpkg-query-systemd.err	regular empty file	ubuntu:ubuntu	600	0	1
c008-a5-dpkg-query-polkitd.cmd	regular file	ubuntu:ubuntu	600	135	1
c008-a5-dpkg-query-polkitd.out	regular file	ubuntu:ubuntu	600	45	1
c008-a5-dpkg-query-polkitd.err	regular empty file	ubuntu:ubuntu	600	0	1
c009-a6-dpkg-query-libc6.cmd	regular file	ubuntu:ubuntu	600	133	1
c009-a6-dpkg-query-libc6.out	regular file	ubuntu:ubuntu	600	44	1
c009-a6-dpkg-query-libc6.err	regular empty file	ubuntu:ubuntu	600	0	1
c010-a7-dpkg-query-python3.14-minimal.cmd	regular file	ubuntu:ubuntu	600	146	1
c010-a7-dpkg-query-python3.14-minimal.out	regular file	ubuntu:ubuntu	600	58	1
c010-a7-dpkg-query-python3.14-minimal.err	regular empty file	ubuntu:ubuntu	600	0	1
c011-a8-python-sha256.cmd	regular file	ubuntu:ubuntu	600	42	1
c011-a8-python-sha256.out	regular file	ubuntu:ubuntu	600	86	1
c011-a8-python-sha256.err	regular empty file	ubuntu:ubuntu	600	0	1
c012-hf07-dpkg-query-python3.14.cmd	regular file	ubuntu:ubuntu	600	138	1
c012-hf07-dpkg-query-python3.14.out	regular file	ubuntu:ubuntu	600	40	1
c012-hf07-dpkg-query-python3.14.err	regular empty file	ubuntu:ubuntu	600	0	1
c013-hf07-dpkg-query-libpython3.14-minimal.cmd	regular file	ubuntu:ubuntu	600	149	1
c013-hf07-dpkg-query-libpython3.14-minimal.out	regular file	ubuntu:ubuntu	600	67	1
c013-hf07-dpkg-query-libpython3.14-minimal.err	regular empty file	ubuntu:ubuntu	600	0	1
c014-hf07-dpkg-query-libpython3.14-stdlib.cmd	regular file	ubuntu:ubuntu	600	148	1
c014-hf07-dpkg-query-libpython3.14-stdlib.out	regular file	ubuntu:ubuntu	600	66	1
c014-hf07-dpkg-query-libpython3.14-stdlib.err	regular empty file	ubuntu:ubuntu	600	0	1
c015-hf07-dpkg-verify-python3.14.cmd	regular file	ubuntu:ubuntu	600	34	1
c015-hf07-dpkg-verify-python3.14.out	regular empty file	ubuntu:ubuntu	600	0	1
c015-hf07-dpkg-verify-python3.14.err	regular empty file	ubuntu:ubuntu	600	0	1
c016-hf07-dpkg-verify-libpython3.14-minimal.cmd	regular file	ubuntu:ubuntu	600	45	1
c016-hf07-dpkg-verify-libpython3.14-minimal.out	regular empty file	ubuntu:ubuntu	600	0	1
c016-hf07-dpkg-verify-libpython3.14-minimal.err	regular empty file	ubuntu:ubuntu	600	0	1
c017-hf07-dpkg-verify-libpython3.14-stdlib.cmd	regular file	ubuntu:ubuntu	600	44	1
c017-hf07-dpkg-verify-libpython3.14-stdlib.out	regular empty file	ubuntu:ubuntu	600	0	1
c017-hf07-dpkg-verify-libpython3.14-stdlib.err	regular empty file	ubuntu:ubuntu	600	0	1
c018-hf07-apt-cache-policy-python3.14.cmd	regular file	ubuntu:ubuntu	600	37	1
c018-hf07-apt-cache-policy-python3.14.out	regular file	ubuntu:ubuntu	600	469	1
c018-hf07-apt-cache-policy-python3.14.err	regular empty file	ubuntu:ubuntu	600	0	1
c019-hf07-apt-cache-policy-libpython3.14-minimal.cmd	regular file	ubuntu:ubuntu	600	48	1
c019-hf07-apt-cache-policy-libpython3.14-minimal.out	regular file	ubuntu:ubuntu	600	480	1
c019-hf07-apt-cache-policy-libpython3.14-minimal.err	regular empty file	ubuntu:ubuntu	600	0	1
c020-hf07-apt-cache-policy-libpython3.14-stdlib.cmd	regular file	ubuntu:ubuntu	600	47	1
c020-hf07-apt-cache-policy-libpython3.14-stdlib.out	regular file	ubuntu:ubuntu	600	479	1
c020-hf07-apt-cache-policy-libpython3.14-stdlib.err	regular empty file	ubuntu:ubuntu	600	0	1
c021-hf08-stat-python.cmd	regular file	ubuntu:ubuntu	600	130	1
c021-hf08-stat-python.out	regular file	ubuntu:ubuntu	600	119	1
c021-hf08-stat-python.err	regular empty file	ubuntu:ubuntu	600	0	1
c022-hf08-python-version.cmd	regular file	ubuntu:ubuntu	600	291	1
c022-hf08-python-version.out	regular file	ubuntu:ubuntu	600	212	1
c022-hf08-python-version.err	regular empty file	ubuntu:ubuntu	600	0	1
c023-g15a-parent-lstat-listxattr.cmd	regular file	ubuntu:ubuntu	600	1278	1
c023-g15a-parent-lstat-listxattr.out	regular file	ubuntu:ubuntu	600	102	1
c023-g15a-parent-lstat-listxattr.err	regular empty file	ubuntu:ubuntu	600	0	1
c024-g15b-ancestor-lstat-listxattr.cmd	regular file	ubuntu:ubuntu	600	1265	1
c024-g15b-ancestor-lstat-listxattr.out	regular file	ubuntu:ubuntu	600	129	1
c024-g15b-ancestor-lstat-listxattr.err	regular empty file	ubuntu:ubuntu	600	0	1
c025-g15c-findmnt-ancestor.cmd	regular file	ubuntu:ubuntu	600	70	1
c025-g15c-findmnt-ancestor.out	regular file	ubuntu:ubuntu	600	104	1
c025-g15c-findmnt-ancestor.err	regular empty file	ubuntu:ubuntu	600	0	1
c026-g15d-df-ancestor.cmd	regular file	ubuntu:ubuntu	600	105	1
c026-g15d-df-ancestor.out	regular file	ubuntu:ubuntu	600	163	1
c026-g15d-df-ancestor.err	regular empty file	ubuntu:ubuntu	600	0	1
TERMINAL-STATE	regular file	ubuntu:ubuntu	600	104	1
````

### `MANIFEST.payload`

`MANIFEST.payload` (8427 bytes)

````text
ac14fa252e8cec1b00995d6c14ab3f88e362c5349b39a868eb92016e18d7a8df  received-program.part1
2af48c496af04140b66a26044d21e95de205bc6eb84c8ee7c893720d6bdaf8eb  received-program.part2
f35b455eb55c68c86a3da202d30c9378c83b8259a164e6c0de76b7e300242607  received-program.sh
66f99959a0e8db2421d81056dadfa6932099816a764d9a89c5d71619b2604dff  PRE-EVIDENCE
395cfa36e349fcee67db4fa38a80a2d54a5b2377b7bcb54fe79b85ffa7166d1d  LEDGER
9b0629c8d4467009f9d3bf336aad134ce05b233a2fd8ef3f327e2ca78580cd48  FACTS
be85b6cae714cca5754a5185f34698a4b5edd6ea0c40bcf24d7464f715cd15b5  c001-program-sha256.cmd
0a594253f5563fbbc6cc2a815d59030fa2d414a85fc47ab24bc2436ce412743c  c001-program-sha256.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c001-program-sha256.err
9bdceab1a7aa03b04c0718aa52f8c284e0474cdb262fe8affbfd674d99df9a5c  c002-id-u.cmd
d6a1a767319c3bf2a337b16e3a14916f63e432872e0f8df1cb73b32a8b338ae4  c002-id-u.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c002-id-u.err
424807431da2c471d482cc7994ef1b2e77243e298e522cf424eeed9a52a890f5  c003-id-un.cmd
da4d47d486c674b0e05b992713276b345aaa1858d3f147b4b185ad5215cfdc69  c003-id-un.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c003-id-un.err
219a4d23f04743b974f422332709ba0c6464cf03b1d4c6b3b0cfdd92014a71d4  c004-a1-uname-n.cmd
c9d04c9565fc665c80681fb1d829938026871f66e14f501e08531df66938a789  c004-a1-uname-n.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c004-a1-uname-n.err
897e893080611fb9038034bcd3f60291a066f557d868ffc2027f1b409b365807  c005-a2-machine-id-sha256.cmd
0726bfdac8860577e63af5a4ec48c0f47027b912eabf1dcc115033d01aab82d2  c005-a2-machine-id-sha256.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c005-a2-machine-id-sha256.err
c998867695bf35aeb350b6e813be572f0eded9606b580d32518fd6c090575d6a  c006-a3-uname-r.cmd
a935f668606af0c33e08bbf9a9be501309bbbf21c847239e922bc3d1b4473681  c006-a3-uname-r.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c006-a3-uname-r.err
07285095bed4fa8a8f1f0405d335b82326deeb8f9d55b7e26d7d072180207e40  c007-a4-dpkg-query-systemd.cmd
9eeab5ff70ea1c974c8274dd6553d5b76be352d89e96109b2dc250b9becc0f5f  c007-a4-dpkg-query-systemd.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c007-a4-dpkg-query-systemd.err
76663fe19eb52878cf1a80952a96fdb48c242439d92d45a72cca70257601aee0  c008-a5-dpkg-query-polkitd.cmd
6652f58f280f85180822f59846a9fb4ddfb1c7bf74f63c322e58762f1e0dcd48  c008-a5-dpkg-query-polkitd.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c008-a5-dpkg-query-polkitd.err
defe72223789b96830ac0641b85793995bb681538b693733394943ea4051d22c  c009-a6-dpkg-query-libc6.cmd
9f00a36e2a0f675972c4faab9443f57ee363b584c959b55500a1da0ef9e12222  c009-a6-dpkg-query-libc6.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c009-a6-dpkg-query-libc6.err
c5eee51d9703a5d0e47ece635da64181df8c3e3d4e93cc2c355dcee357de7251  c010-a7-dpkg-query-python3.14-minimal.cmd
48a9a80dfb86a500cdc683f74d9814612d3a89e764cf02ed71653998e3015b44  c010-a7-dpkg-query-python3.14-minimal.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c010-a7-dpkg-query-python3.14-minimal.err
b5d1b2947a9b600077e32f29bf6e96d9c95fe3ab55f50ef80ec8412a4977fa80  c011-a8-python-sha256.cmd
f8f2038ffb9541b0ffd7e2cb459b583c422d0269b96f83d3f65f47ee79a8f6ca  c011-a8-python-sha256.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c011-a8-python-sha256.err
1c7993132511d16eaf4319eff9bfe3c7d3de3655683aff8933f13a8b6c693df6  c012-hf07-dpkg-query-python3.14.cmd
7938a2ddc7b27faa8f8ce30d7895b8e0bcd36d99cd2014bec7d3ef62730700e4  c012-hf07-dpkg-query-python3.14.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c012-hf07-dpkg-query-python3.14.err
200e29d95419a464f45b7c5f2831f6f67eb4841c389bcb72602f722a889fe573  c013-hf07-dpkg-query-libpython3.14-minimal.cmd
0dee137d2b4bbae71b217ca73df664eeab79be674d94250668cfdc87e8ddd387  c013-hf07-dpkg-query-libpython3.14-minimal.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c013-hf07-dpkg-query-libpython3.14-minimal.err
adeaf34bb1950751131d849b179781ba1163d2d9540bc94f1f0ca6b378d7806a  c014-hf07-dpkg-query-libpython3.14-stdlib.cmd
487315d8ed0204fdc1ce9c59adeacc264c438ba9e2146b18479d34ebd33fdb26  c014-hf07-dpkg-query-libpython3.14-stdlib.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c014-hf07-dpkg-query-libpython3.14-stdlib.err
8297c3573d8d79aebdb2415593546f3e5b6e4a98b290ffeece80b4030131c3e9  c015-hf07-dpkg-verify-python3.14.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c015-hf07-dpkg-verify-python3.14.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c015-hf07-dpkg-verify-python3.14.err
aaacd72fe699f06c44568e9622a1efa127695b703d72788fb14720a412c22ef2  c016-hf07-dpkg-verify-libpython3.14-minimal.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c016-hf07-dpkg-verify-libpython3.14-minimal.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c016-hf07-dpkg-verify-libpython3.14-minimal.err
3012dcabe91f456935c84053e4e354c445133bcf94251855e070bdfdf3929434  c017-hf07-dpkg-verify-libpython3.14-stdlib.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c017-hf07-dpkg-verify-libpython3.14-stdlib.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c017-hf07-dpkg-verify-libpython3.14-stdlib.err
c191ea357ee650a5dbca3baf669fbe0cc68a923517a770329371083331016ef0  c018-hf07-apt-cache-policy-python3.14.cmd
68e88ba9243be0d9377c8fd47b1ff93de3905683ee5cc73522f2184d2d900bb9  c018-hf07-apt-cache-policy-python3.14.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c018-hf07-apt-cache-policy-python3.14.err
56191a747aaf4dabca7d2ef295396ab80fd0868d4ce301f8a72b32a7119b5053  c019-hf07-apt-cache-policy-libpython3.14-minimal.cmd
03f795dec290fcbb508e80118ae605d3154b907e06d713a0dad411c9c0536e85  c019-hf07-apt-cache-policy-libpython3.14-minimal.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c019-hf07-apt-cache-policy-libpython3.14-minimal.err
9d70ff3a3bfbd9ad06836ac44455a8c0f1c51bc143cbe674c30579204ebf16a1  c020-hf07-apt-cache-policy-libpython3.14-stdlib.cmd
c137453069e3de7a88790fedb6bd5dbdb9253fd41125aa132e3b9f0228314ab2  c020-hf07-apt-cache-policy-libpython3.14-stdlib.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c020-hf07-apt-cache-policy-libpython3.14-stdlib.err
55fd4fd7a822896730ae9ec0392f286da792596af1827b4a948c37937348daa8  c021-hf08-stat-python.cmd
402fa1d44bb982cd9536a90b8042224519502d9193d8ae2545b090c09bf7a1dc  c021-hf08-stat-python.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c021-hf08-stat-python.err
310228b57f5a02f14fb169f39bbdc9e46eb1a3cbca494b40f78e84f1dcb1a8bc  c022-hf08-python-version.cmd
43b21b0e916641f4efc9c1307c8a20f4905f22e4a75ac4d01f93d1d3565cb2ad  c022-hf08-python-version.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c022-hf08-python-version.err
973b7afcbe3fed8fa9b7652b87ff677219c3613eda90efc9899545e2356cdd95  c023-g15a-parent-lstat-listxattr.cmd
6ed52ed72b62b45bb67d202d122f7d948b1ba55a249e203444b26c66f76e6c9e  c023-g15a-parent-lstat-listxattr.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c023-g15a-parent-lstat-listxattr.err
5bc6f56b4985f3746372328ecc53a98680d85b2ed526f05ade07c5045283a1d2  c024-g15b-ancestor-lstat-listxattr.cmd
80ede5fd235c1a2f82b670a670f6816c7865a211396a76079cdbbbf00007cfe4  c024-g15b-ancestor-lstat-listxattr.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c024-g15b-ancestor-lstat-listxattr.err
5a9da6a82a9102a8f956fb91237824a7f77c289f98e89f03faf5a98ba2b9b248  c025-g15c-findmnt-ancestor.cmd
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  c025-g15c-findmnt-ancestor.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c025-g15c-findmnt-ancestor.err
d00d0964d29392ce0927b6ce4d0a2f7dc3efe2cb8e059dbaff92bdcea5318b1e  c026-g15d-df-ancestor.cmd
d5c7831971115c479787a8a52387a2e0fac1b9880cac82c4031f49c8a7dfe33c  c026-g15d-df-ancestor.out
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  c026-g15d-df-ancestor.err
27c0af86624e119984e4fc4c3f3e52c07fe6a582900400039b7d13cb69c320f9  TERMINAL-STATE
4c777f3d86f067f92169cc7c7c2593286909dda98509fccabc97c6dbffd88890  INVENTORY
````

### `MANIFEST.final`

`MANIFEST.final` (83 bytes)

````text
cc0c3f29221c035241efdad71852776258c69e68e530c145925d3f4a74f1da3d  MANIFEST.payload
````

## Appendix C — verbatim command records (`.cmd`, stdout, `.err`) c001–c026

### `c001-program-sha256`

`c001-program-sha256.cmd` (235 bytes)

````text
/usr/bin/sha256sum -- /var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence/received-program.part1 /var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence/received-program.part2 /var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence/received-program.sh
````

`c001-program-sha256.out` (411 bytes)

````text
ac14fa252e8cec1b00995d6c14ab3f88e362c5349b39a868eb92016e18d7a8df  /var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence/received-program.part1
2af48c496af04140b66a26044d21e95de205bc6eb84c8ee7c893720d6bdaf8eb  /var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence/received-program.part2
f35b455eb55c68c86a3da202d30c9378c83b8259a164e6c0de76b7e300242607  /var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence/received-program.sh
````

`c001-program-sha256.err` (0 bytes)

### `c002-id-u`

`c002-id-u.cmd` (15 bytes)

````text
/usr/bin/id -u
````

`c002-id-u.out` (5 bytes)

````text
1001
````

`c002-id-u.err` (0 bytes)

### `c003-id-un`

`c003-id-un.cmd` (16 bytes)

````text
/usr/bin/id -un
````

`c003-id-un.out` (7 bytes)

````text
ubuntu
````

`c003-id-un.err` (0 bytes)

### `c004-a1-uname-n`

`c004-a1-uname-n.cmd` (18 bytes)

````text
/usr/bin/uname -n
````

`c004-a1-uname-n.out` (5 bytes)

````text
Test
````

`c004-a1-uname-n.err` (0 bytes)

### `c005-a2-machine-id-sha256`

`c005-a2-machine-id-sha256.cmd` (35 bytes)

````text
/usr/bin/sha256sum /etc/machine-id
````

`c005-a2-machine-id-sha256.out` (82 bytes)

````text
e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d  /etc/machine-id
````

`c005-a2-machine-id-sha256.err` (0 bytes)

### `c006-a3-uname-r`

`c006-a3-uname-r.cmd` (18 bytes)

````text
/usr/bin/uname -r
````

`c006-a3-uname-r.out` (17 bytes)

````text
7.0.0-31-generic
````

`c006-a3-uname-r.err` (0 bytes)

### `c007-a4-dpkg-query-systemd`

`c007-a4-dpkg-query-systemd.cmd` (135 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n systemd
````

`c007-a4-dpkg-query-systemd.out` (36 bytes)

````text
systemd	259.5-0ubuntu3.4	amd64	ii 	
````

`c007-a4-dpkg-query-systemd.err` (0 bytes)

### `c008-a5-dpkg-query-polkitd`

`c008-a5-dpkg-query-polkitd.cmd` (135 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n polkitd
````

`c008-a5-dpkg-query-polkitd.out` (45 bytes)

````text
polkitd	127-2ubuntu1.1	amd64	ii 	policykit-1
````

`c008-a5-dpkg-query-polkitd.err` (0 bytes)

### `c009-a6-dpkg-query-libc6`

`c009-a6-dpkg-query-libc6.cmd` (133 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libc6
````

`c009-a6-dpkg-query-libc6.out` (44 bytes)

````text
libc6:amd64	2.43-2ubuntu2.4	amd64	ii 	glibc
````

`c009-a6-dpkg-query-libc6.err` (0 bytes)

### `c010-a7-dpkg-query-python3.14-minimal`

`c010-a7-dpkg-query-python3.14-minimal.cmd` (146 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n python3.14-minimal
````

`c010-a7-dpkg-query-python3.14-minimal.out` (58 bytes)

````text
python3.14-minimal	3.14.4-1ubuntu0.2	amd64	ii 	python3.14
````

`c010-a7-dpkg-query-python3.14-minimal.err` (0 bytes)

### `c011-a8-python-sha256`

`c011-a8-python-sha256.cmd` (42 bytes)

````text
/usr/bin/sha256sum -- /usr/bin/python3.14
````

`c011-a8-python-sha256.out` (86 bytes)

````text
be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd  /usr/bin/python3.14
````

`c011-a8-python-sha256.err` (0 bytes)

### `c012-hf07-dpkg-query-python3.14`

`c012-hf07-dpkg-query-python3.14.cmd` (138 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n python3.14
````

`c012-hf07-dpkg-query-python3.14.out` (40 bytes)

````text
python3.14	3.14.4-1ubuntu0.2	amd64	ii 	
````

`c012-hf07-dpkg-query-python3.14.err` (0 bytes)

### `c013-hf07-dpkg-query-libpython3.14-minimal`

`c013-hf07-dpkg-query-libpython3.14-minimal.cmd` (149 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libpython3.14-minimal
````

`c013-hf07-dpkg-query-libpython3.14-minimal.out` (67 bytes)

````text
libpython3.14-minimal:amd64	3.14.4-1ubuntu0.2	amd64	ii 	python3.14
````

`c013-hf07-dpkg-query-libpython3.14-minimal.err` (0 bytes)

### `c014-hf07-dpkg-query-libpython3.14-stdlib`

`c014-hf07-dpkg-query-libpython3.14-stdlib.cmd` (148 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libpython3.14-stdlib
````

`c014-hf07-dpkg-query-libpython3.14-stdlib.out` (66 bytes)

````text
libpython3.14-stdlib:amd64	3.14.4-1ubuntu0.2	amd64	ii 	python3.14
````

`c014-hf07-dpkg-query-libpython3.14-stdlib.err` (0 bytes)

### `c015-hf07-dpkg-verify-python3.14`

`c015-hf07-dpkg-verify-python3.14.cmd` (34 bytes)

````text
/usr/bin/dpkg --verify python3.14
````

`c015-hf07-dpkg-verify-python3.14.out` (0 bytes)

`c015-hf07-dpkg-verify-python3.14.err` (0 bytes)

### `c016-hf07-dpkg-verify-libpython3.14-minimal`

`c016-hf07-dpkg-verify-libpython3.14-minimal.cmd` (45 bytes)

````text
/usr/bin/dpkg --verify libpython3.14-minimal
````

`c016-hf07-dpkg-verify-libpython3.14-minimal.out` (0 bytes)

`c016-hf07-dpkg-verify-libpython3.14-minimal.err` (0 bytes)

### `c017-hf07-dpkg-verify-libpython3.14-stdlib`

`c017-hf07-dpkg-verify-libpython3.14-stdlib.cmd` (44 bytes)

````text
/usr/bin/dpkg --verify libpython3.14-stdlib
````

`c017-hf07-dpkg-verify-libpython3.14-stdlib.out` (0 bytes)

`c017-hf07-dpkg-verify-libpython3.14-stdlib.err` (0 bytes)

### `c018-hf07-apt-cache-policy-python3.14`

`c018-hf07-apt-cache-policy-python3.14.cmd` (37 bytes)

````text
/usr/bin/apt-cache policy python3.14
````

`c018-hf07-apt-cache-policy-python3.14.out` (469 bytes)

````text
python3.14:
  Installed: 3.14.4-1ubuntu0.2
  Candidate: 3.14.4-1ubuntu0.2
  Version table:
 *** 3.14.4-1ubuntu0.2 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     3.14.4-1 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
````

`c018-hf07-apt-cache-policy-python3.14.err` (0 bytes)

### `c019-hf07-apt-cache-policy-libpython3.14-minimal`

`c019-hf07-apt-cache-policy-libpython3.14-minimal.cmd` (48 bytes)

````text
/usr/bin/apt-cache policy libpython3.14-minimal
````

`c019-hf07-apt-cache-policy-libpython3.14-minimal.out` (480 bytes)

````text
libpython3.14-minimal:
  Installed: 3.14.4-1ubuntu0.2
  Candidate: 3.14.4-1ubuntu0.2
  Version table:
 *** 3.14.4-1ubuntu0.2 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     3.14.4-1 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
````

`c019-hf07-apt-cache-policy-libpython3.14-minimal.err` (0 bytes)

### `c020-hf07-apt-cache-policy-libpython3.14-stdlib`

`c020-hf07-apt-cache-policy-libpython3.14-stdlib.cmd` (47 bytes)

````text
/usr/bin/apt-cache policy libpython3.14-stdlib
````

`c020-hf07-apt-cache-policy-libpython3.14-stdlib.out` (479 bytes)

````text
libpython3.14-stdlib:
  Installed: 3.14.4-1ubuntu0.2
  Candidate: 3.14.4-1ubuntu0.2
  Version table:
 *** 3.14.4-1ubuntu0.2 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     3.14.4-1 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
````

`c020-hf07-apt-cache-policy-libpython3.14-stdlib.err` (0 bytes)

### `c021-hf08-stat-python`

`c021-hf08-stat-python.cmd` (130 bytes)

````text
/usr/bin/stat -c name=%n\ type=%F\ owner=%U:%G\ uid=%u\ gid=%g\ mode=%a\ size=%s\ dev=%d\ ino=%i\ nlink=%h -- /usr/bin/python3.14
````

`c021-hf08-stat-python.out` (119 bytes)

````text
name=/usr/bin/python3.14 type=regular file owner=root:root uid=0 gid=0 mode=755 size=7468968 dev=2049 ino=8254 nlink=1
````

`c021-hf08-stat-python.err` (0 bytes)

### `c022-hf08-python-version`

`c022-hf08-python-version.cmd` (291 bytes)

````text
/usr/bin/python3.14 -I -S -c $'import sys\nprint("version=" + sys.version.replace("\\n", " "))\nprint("isolated=" + str(sys.flags.isolated))\nprint("no_site=" + str(sys.flags.no_site))\nprint("executable=" + sys.executable)\nprint("prefix=" + sys.prefix)\nprint("path=" + repr(sys.path))\n'
````

`c022-hf08-python-version.out` (212 bytes)

````text
version=3.14.4 (main, Aug 20 2026, 10:41:58) [GCC 15.2.0]
isolated=1
no_site=1
executable=/usr/bin/python3.14
prefix=/usr
path=['/usr/lib/python314.zip', '/usr/lib/python3.14', '/usr/lib/python3.14/lib-dynload']
````

`c022-hf08-python-version.err` (0 bytes)

### `c023-g15a-parent-lstat-listxattr`

`c023-g15a-parent-lstat-listxattr.cmd` (1278 bytes)

````text
/usr/bin/python3.14 -I -S -c $'import errno, grp, os, pwd, stat, sys\nsys.dont_write_bytecode = True\ndef ename(n):\n    return errno.errorcode.get(n, "?")\ndef kind(m):\n    for t, f in (("dir", stat.S_ISDIR), ("reg", stat.S_ISREG), ("symlink", stat.S_ISLNK), ("chr", stat.S_ISCHR), ("blk", stat.S_ISBLK), ("fifo", stat.S_ISFIFO), ("sock", stat.S_ISSOCK)):\n        if f(m):\n            return t\n    return "other"\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\np = sys.argv[1]\ntry:\n    st = os.lstat(p)\nexcept OSError as e:\n    print("lstat\\t" + p + "\\terror\\terrno=" + str(e.errno) + "\\t" + ename(e.errno))\nelse:\n    m = st.st_mode\n    print("\\t".join(["lstat", p, "ok", "type=" + kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid), "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid), "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino), "nlink=" + str(st.st_nlink)]))\ntry:\n    xs = os.listxattr(p, follow_symlinks=False)\nexcept OSError as e:\n    print("listxattr\\t" + p + "\\terror\\terrno=" + str(e.errno) + "\\t" + ename(e.errno))\nelse:\n    print("listxattr\\t" + p + "\\tok\\tnames=" + (",".join(sorted(xs)) or "-"))\n' /var/lib/rp11-capture
````

`c023-g15a-parent-lstat-listxattr.out` (102 bytes)

````text
lstat	/var/lib/rp11-capture	error	errno=2	ENOENT
listxattr	/var/lib/rp11-capture	error	errno=2	ENOENT
````

`c023-g15a-parent-lstat-listxattr.err` (0 bytes)

### `c024-g15b-ancestor-lstat-listxattr`

`c024-g15b-ancestor-lstat-listxattr.cmd` (1265 bytes)

````text
/usr/bin/python3.14 -I -S -c $'import errno, grp, os, pwd, stat, sys\nsys.dont_write_bytecode = True\ndef ename(n):\n    return errno.errorcode.get(n, "?")\ndef kind(m):\n    for t, f in (("dir", stat.S_ISDIR), ("reg", stat.S_ISREG), ("symlink", stat.S_ISLNK), ("chr", stat.S_ISCHR), ("blk", stat.S_ISBLK), ("fifo", stat.S_ISFIFO), ("sock", stat.S_ISSOCK)):\n        if f(m):\n            return t\n    return "other"\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\np = sys.argv[1]\ntry:\n    st = os.lstat(p)\nexcept OSError as e:\n    print("lstat\\t" + p + "\\terror\\terrno=" + str(e.errno) + "\\t" + ename(e.errno))\nelse:\n    m = st.st_mode\n    print("\\t".join(["lstat", p, "ok", "type=" + kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid), "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid), "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino), "nlink=" + str(st.st_nlink)]))\ntry:\n    xs = os.listxattr(p, follow_symlinks=False)\nexcept OSError as e:\n    print("listxattr\\t" + p + "\\terror\\terrno=" + str(e.errno) + "\\t" + ename(e.errno))\nelse:\n    print("listxattr\\t" + p + "\\tok\\tnames=" + (",".join(sorted(xs)) or "-"))\n' /var/lib
````

`c024-g15b-ancestor-lstat-listxattr.out` (129 bytes)

````text
lstat	/var/lib	ok	type=dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=97831	nlink=52
listxattr	/var/lib	ok	names=-
````

`c024-g15b-ancestor-lstat-listxattr.err` (0 bytes)

### `c025-g15c-findmnt-ancestor`

`c025-g15c-findmnt-ancestor.cmd` (70 bytes)

````text
/usr/bin/findmnt --target /var/lib -o TARGET\,SOURCE\,FSTYPE\,OPTIONS
````

`c025-g15c-findmnt-ancestor.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30
````

`c025-g15c-findmnt-ancestor.err` (0 bytes)

### `c026-g15d-df-ancestor`

`c026-g15d-df-ancestor.cmd` (105 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /var/lib
````

`c026-g15d-df-ancestor.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7570952 38580368  17% 5707520 253747 5453773 /
````

`c026-g15d-df-ancestor.err` (0 bytes)

H-0G awaits independent Codex review and composition; no cleanup, workspace recreation, OH-S2 or later slice is authorized.
