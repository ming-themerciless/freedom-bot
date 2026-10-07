# Handback — R5 isolated-checkout H-0: `H-0 PASS`

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-20261006-02`

Date: 2026-10-06

Executor: Claude Code (controller in `/opt/freedom-blades/platform`), one
forwarding-disabled SSH execution connection to `oracle-test`.

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-claude-prompt.md)
(SHA-256 `57d23c1ba683ce8c2be15fe101da959a9dc1334ff89a1b0c66f917f26cf42e8e`, 6942 bytes, equal to the authority's pin)
· Authority: [`project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-authority.md)
(SHA-256 `ddc0f9f1ca3c556f34a7844b6f6e969d8dc192ced37a7aef13a17bee75ffce66`, 2245 bytes)

## Terminal state: `H-0 PASS`

This is the executor's terminal state for fact collection. It is not an
acceptance of any fact. Every value below is an observation that waits for
independent review.

All three PASS conditions hold:

- **Pinned retrieval succeeded.** `c016-git-fetch` exited `0`. Its stderr
  shows `From https://github.com/ming-themerciless/freedom-platform` and
  `* branch 46d1c35a029ca8287779ae87d08a370ba0a0f2ef -> FETCH_HEAD`. There was
  no authentication request, redirect or credential use.
- **The isolated checkout is clean and detached.**
  - `cat-file -t` returned `commit` (c017).
  - `rev-parse --verify` of the pin returned the pin (c018).
  - The detached checkout succeeded (c020).
  - `rev-parse HEAD` = `46d1c35a029ca8287779ae87d08a370ba0a0f2ef` (c021).
  - `status --porcelain=v1 --untracked-files=all` printed nothing (c022).
  - `symbolic-ref -q HEAD` exited `1`, which means detached (c023).
  - `remote -v` printed nothing (c024).
  - The local config holds only four `core.*` keys: no remote and no
    credential (c025).
- **All of HF-01 through HF-20 were observed or recorded,** and both
  manifests and the owner/mode inventory closed with `violations=0`.
  The facts include every absence, unreadable result and version difference.
  HF-18 and HF-20's PO-21 (i) paths are recorded as `not specified`, because
  the accepted tree names no path for them.

## Controller command and program

- Program (controller transport, not repository source): SHA-256
  `ad4a2fc7308b43c1de95d8ab7c06bae8a3a7b10e7b9e065dadfbc8fa32745645`, 43068 bytes. It embeds the R5 prompt and authority as
  base64. It contains no repository source or implementation file.
- The remote bootstrap verified the same digest and length before execution;
  otherwise it would have exited `72`/`73`. Commands c001 and c002 recomputed
  them remotely: `ad4a2fc7308b43c1de95d8ab7c06bae8a3a7b10e7b9e065dadfbc8fa32745645  /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/controller-h0-program.sh` and `size=43068 owner=ubuntu:ubuntu mode=600 type=regular file`.
- SSH start/end (controller UTC): `2026-10-06T02:49:24.227015784Z` / `2026-10-06T02:49:42.139749298Z`. SSH exit
  status `0`. SSH stderr was empty (0 bytes). There was
  no authentication, host-key or transport error.
- SSH stdout (370403 bytes) is controller transport only. Before
  exiting, the program echoed every evidence file except the retained program,
  using bash builtins only (`mapfile`/`printf`) and no further command. The
  last line was `TERMINAL: H-0 PROGRAM COMPLETE (controller evaluates PASS)`.
- Exact controller command, run once. The redirected program file was a fresh
  scratchpad file whose digest and length are the values above:

```bash
ssh -T -o BatchMode=yes -o ClearAllForwardings=yes -o ForwardAgent=no -o ForwardX11=no -o PermitLocalCommand=no oracle-test "/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /bin/bash --noprofile --norc -c 'set -eu; if ! { test \"\$(/usr/bin/id -ru)\" = \"\$(/usr/bin/id -u ubuntu)\" && test \"\$(/usr/bin/id -u)\" = \"\$(/usr/bin/id -u ubuntu)\" && test \"\$(/usr/bin/id -run)\" = ubuntu && test \"\$(/usr/bin/id -un)\" = ubuntu && test \"\$(/usr/bin/uname -n)\" = Test; }; then /usr/bin/printf \"HARD STOP: remote identity mismatch\\n\" >&2; exit 70; fi; umask 077; evidence=/var/tmp/p5-r5-rp11-h0-20261006-02-evidence; checkout=/var/tmp/p5-r5-rp11-h0-20261006-02-checkout; for p in \"\$evidence\" \"\$checkout\"; do if /usr/bin/test -e \"\$p\" || /usr/bin/test -L \"\$p\"; then /usr/bin/printf \"HARD STOP: exclusive path exists\\n\" >&2; exit 71; fi; done; /usr/bin/mkdir -m 0700 -- \"\$evidence\"; /usr/bin/tee \"\$evidence/controller-h0-program.sh\" >/dev/null; /usr/bin/chmod 0600 \"\$evidence/controller-h0-program.sh\"; test \"\$(/usr/bin/sha256sum \"\$evidence/controller-h0-program.sh\" | /usr/bin/cut -d\" \" -f1)\" = ad4a2fc7308b43c1de95d8ab7c06bae8a3a7b10e7b9e065dadfbc8fa32745645 || { /usr/bin/printf \"HARD STOP: program digest mismatch\\n\" >&2; exit 72; }; test \"\$(/usr/bin/stat -c %s \"\$evidence/controller-h0-program.sh\")\" = 43068 || { /usr/bin/printf \"HARD STOP: program length mismatch\\n\" >&2; exit 73; }; exec /usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin /bin/bash --noprofile --norc \"\$evidence/controller-h0-program.sh\"'" < "/tmp/claude-1000/-opt-freedom-blades-platform/8c146a73-3994-4972-8bfd-4207c8e14a81/scratchpad/r5/xfer/h0-program.sh"
```

## Fixed inputs (as used, unsubstituted)

- URL `https://github.com/ming-themerciless/freedom-platform.git`; pin
  `46d1c35a029ca8287779ae87d08a370ba0a0f2ef`
- Remote account/nodename `ubuntu` / `Test`
- Preserved fixed checkout `/opt/freedom-blades/platform`: on `oracle-test`
  it was neither inspected (not even `stat`) nor mutated
- Isolated checkout `/var/tmp/p5-r5-rp11-h0-20261006-02-checkout`
- Evidence directory `/var/tmp/p5-r5-rp11-h0-20261006-02-evidence`
- Durable controller handback: this file

## Identity, interpreter, retrieval and governing files

| Item | Value | Evidence |
|---|---|---|
| real/effective UID | `1001` / `1001` | c003, c004 |
| real/effective user | `ubuntu` / `ubuntu` | c006, c005 |
| nodename | `Test` | c007 (HF-01) |
| `/etc/machine-id` SHA-256 | `e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d` | c008 (HF-02) |
| `/usr/bin/python3` resolution | symlink `root:root` `777` → `/usr/bin/python3.14`, a regular file `root:root` `755` of 7468968 bytes | c009–c011 |
| `/usr/bin/python3 -I -S` | `3.14.4 (main, Aug 20 2026, 10:41:58) [GCC 15.2.0]`; `isolated=1`, `no_site=1`; prefix `/usr`. Suitable for the bounded helpers | c012 |
| exclusive paths before Git | evidence dir present (created by the bootstrap; `ubuntu:ubuntu` `0700`, dev 2049, ino 1766009, no xattr names); checkout absent | c013 |
| Git | `git version 2.53.0` | c014 |
| init / fetch / verify / detach | all exit `0`; see the PASS conditions above | c015–c025 |
| commit | tree `56ccab51963de051d67426be8c560d69c8f3638c`, parent `236872647f3edd5fed5c7f14512518e13eeb8f07` | c019 |
| governing files in the pinned tree | `.agents/AGENTS.md`, `docs/implementation-plan.md`, the accepted proposal and the D3-R6 acceptance all equal their expected SHA-256 | c026 |
| D3-R6 acceptance decision text | present at line 12 | c027 |
| accepted proposal HF definitions | §4.4.1 table rows HF-01 … HF-18, §4.4.2b heading and the HF-20 bullet present | c028 |
| retained R5 prompt / authority copies | `R5-prompt.md` SHA-256 `57d23c1ba683ce8c2be15fe101da959a9dc1334ff89a1b0c66f917f26cf42e8e` (6942 bytes); `R5-authority.md` SHA-256 `ddc0f9f1ca3c556f34a7844b6f6e969d8dc192ced37a7aef13a17bee75ffce66` (2245 bytes); both equal to the controller's files | c029–c032 |

## HF-01 – HF-20

Command classes used: C-ID, C-PROC, C-STAT, C-DIG, C-VER, C-PKG and C-SDQ.
`readlink -f` (C-STAT resolution), `grep` (HF-19's "lines naming" and the
governing-file checks) and `base64 -d` (prompt/authority copies) are the
same helpers that R4 used. Appendix B gives every output verbatim.

| HF | Observation | Evidence |
|---|---|---|
| HF-01 | `Test` | c007 |
| HF-02 | `/etc/machine-id` SHA-256 `e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d` | c008 |
| HF-03 | `uid=1001(ubuntu) gid=1001(ubuntu)`; groups `ubuntu`(1001) `adm`(4) `cdrom`(24) `sudo`(27) `dip`(30) `lxd`(102) `freedomlab`(986). Home `/home/ubuntu`, shell `/bin/bash`. `adm` also lists `syslog` and `ocarun`. **Repository ownership is not observed**, because the prompt forbids inspecting the fixed checkout | c033–c042; HF-NOTES |
| HF-04 | `7.0.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug  1 04:26:38 UTC 2026 x86_64` | c043 |
| HF-05 | `/proc/1/comm` = `systemd`; `systemd 259 (259.5-0ubuntu3.4)` | c044, c045 |
| HF-06 | systemd `259.5-0ubuntu3.4`; polkit `127-2ubuntu1.1`; glibc `2.43-2ubuntu2.4`; CPython **3.14.4** (`/usr/bin/python3.14`). The cited CPython 3.12 is **absent** | c045, c050, c052, c012; HF-NOTES |
| HF-07 | Installed (`ii`): `systemd`, `systemd-sysv`, `libsystemd0`, `libsystemd-shared` `259.5-0ubuntu3.4`; `polkitd`, `libpolkit-gobject-1-0` `127-2ubuntu1.1`; `libc6`, `libc-bin` `2.43-2ubuntu2.4`; `coreutils` `9.5-1ubuntu2+0.0.0~ubuntu25` (source `coreutils-from (0.0.0~ubuntu25)`); `util-linux` `2.41.3-3ubuntu2.2`; `sudo` `1.9.17p2-1ubuntu3.1`; `dbus` `1.16.2-2ubuntu4`. **Not installed:** `python3.12`, `python3.12-minimal`, `libpython3.12-minimal`, `libpython3.12-stdlib`. Added by resolution: `python3-minimal` `3.14.3-0ubuntu2` owns `/usr/bin/python3`, and `python3.14-minimal` `3.14.4-1ubuntu0.2` owns `/usr/bin/python3.14`. `dpkg -S`: `systemd-executor` → `systemd`; `polkitd` and `pkcheck` → `polkitd`; the loader's real path → `libc6:amd64`. `/lib64/ld-linux-x86-64.so.2` reports only a `libc6` diversion. `dpkg --verify` printed nothing for any installed package (exit 0). `apt-cache policy` shows Installed = Candidate for every installed package; see the unexpected-facts list for the `python3.12` regex match | c046–c072, c073–c090, c091 |
| HF-08 | `/usr/bin/python3.12` **absent**: `stat` exit 1, `sha256sum` exit 1, invocation exit 127. `readlink -f` printed the path itself (exit 0), which is not evidence of presence. The available interpreter is `/usr/bin/python3.14` (`root:root` `755`, 7468968 bytes), SHA-256 `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd`, version as c012 | c092–c097, c009–c012 |
| HF-09 | `/lib64/ld-linux-x86-64.so.2` is a symlink → `../lib/x86_64-linux-gnu/ld-linux-x86-64.so.2`. Real path `/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2` (`root:root` `0755`, 250768 bytes), SHA-256 `75c84c6a1522e227864db7d8b40f66b5d6edefcff92538e15a964f1de7855390`. `/etc/ld.so.preload` **absent**. `/etc/ld.so.cache` `root:root` `0644`, SHA-256 `7b196d30bc25f05bc583fb218d63e83fbf5eaa390e3e8bcf9e784f6a91a205e9`. `/etc/ld.so.conf` SHA-256 `d4b198c463418b493208485def26a6f4c57279467b9dfa491b70433cedb602e8`. `/etc/ld.so.conf.d/` holds `fakeroot-x86_64-linux-gnu.conf`, `libc.conf` and `x86_64-linux-gnu.conf`, all `root:root` `0644`, with digests in c102. No xattr names | c062, c098–c102 |
| HF-10 | Not symlinks, `root:root` `755`: `systemctl`, `journalctl`, `dpkg-query`, `pkcheck`, `systemd-run`. **Symlinks** whose targets are `root:root` regular files: `sha256sum` (`755`), `stat` (`755`), `sleep` (`755`), `python3` (`755`), and `sudo` (`4755`, set-user-ID root). None is group- or world-writable. `/usr/bin/python3.12` is **absent**, so both `stat` calls exited 1. Link targets were not recorded by this `stat` format | c103, c104 |
| HF-11 | Every concrete §4.2.3 RP-11 path is **absent**, with one exception. `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules` is **unknown**: `lstat` raised `PermissionError errno=13`. Parents, all with no xattr names and dev 2049 except `/run`: `/` (ino 2), `/usr` (1709), `/usr/local` (65097), `/usr/local/libexec` (65117), `/etc` (44), `/etc/systemd` (419), `/etc/systemd/system` (430), `/etc/polkit-1` (1624) and `/var` (97830) are `root:root` `0755`; `/var/lib` is `0755` (97831). `/etc/polkit-1/rules.d` is **`root:polkitd` `0750`** (gid 983, ino 1625). `/run` is `root:root` `0755`, dev 29, ino 1. `/run/polkit-1` and `/run/polkit-1/rules.d` are **absent**. `/var/tmp` is `root:root` **`1777`** (ino 101403) | c105 |
| HF-12 | `/etc/polkit-1/rules.d`: `root:polkitd` `0750`; listing **unreadable**. `/usr/share/polkit-1/rules.d`: `root:root` `0755`, 9 entries, each with a SHA-256 (c108–c116). `10-systemd-logind-root-ignore-inhibitors.rules` is a symlink to its `.example`, with the same digest. `/run/polkit-1/rules.d` and `/usr/local/share/polkit-1/rules.d` are **absent**. No elevation was attempted | c106–c116 |
| HF-13 | `rp11-capture-pass-a.service`: `LoadState=not-found`, `FragmentPath=` and `DropInPaths=` empty. There are 12 unit paths, and every one of the 24 `rp11-capture-pass-a.service.d/` and `service.d/` drop-in directories is **absent** | c117–c119 |
| HF-14 | `binfmt_misc` is mounted at `/proc/sys/fs/binfmt_misc` (autofs `systemd-1`, plus `binfmt_misc` `rw,nosuid,nodev,noexec,relatime`). `status` = `enabled`. One entry, `python3.14`: `enabled`, interpreter `/usr/bin/python3.14`, flags empty, offset 0, magic `2b0e0d0a`. `register` was not read | c120–c123 |
| HF-15 | `/`, `/usr/local`, `/usr/local/libexec`, `/etc`, `/etc/systemd/system`, `/etc/polkit-1/rules.d`, `/var/lib` and `/var/tmp` all resolve to mount `/` on `/dev/sda1`, `ext4`, `rw,relatime,discard,errors=remount-ro,commit=30`. Capacity is 46167704 1K-blocks, about 17% used, with 5707520 inodes. `/run` is **`tmpfs`** `rw,nosuid,nodev,size=194716k,nr_inodes=819200,mode=755,inode64`. For `/run/polkit-1` (**absent**), `findmnt` exited 1 and `df` exited 1. The capture-root parent is not observed, because no fixed input names it | c124–c143, c120 |
| HF-16 | 52 `Default*` values (of 55 requested) plus `Version`, including `DefaultTimeoutStartUSec=1min 30s`, `DefaultTimeoutStopUSec=1min 30s`, `DefaultOOMPolicy=stop`, `DefaultTasksMax=1006`, `DefaultLimitNOFILE=524288` and `DefaultRestrictSUIDSGID=no`. `Version=259.5-0ubuntu3.4`. Requested but **not reported** by this manager: `DefaultCPUAccounting`, `DefaultBlockIOAccounting` and `DefaultSmackProcessLabel` | c144 |
| HF-17 | `apt-daily.timer` and `apt-daily-upgrade.timer` are `loaded active waiting enabled`. **`unattended-upgrades.service` is `loaded active running enabled`.** `list-timers` shows 19 timers, including `apt-daily` (next 03:38:07 UTC) and `apt-daily-upgrade` (next 06:12:05 UTC) | c145, c146 |
| HF-18 | **not specified.** The accepted tree names no interactive-client path. No search and no installation were performed | HF-NOTES |
| HF-19 | `/usr/lib/tmpfiles.d/tmp.conf` SHA-256 `a1dae3c409fab42c6e48d93ad36364cd6b35ac4705488f1e91b8593ef41ea931`. Its line 12 is **`q /var/tmp 1777 root root 30d`**. `systemd-tmp.conf` lines 13, 14 and 18 name `/var/tmp/systemd-private-*`. No `tmpfiles.d` line names `/run/polkit-1` or `/run/freedom-blades-rp11`. c149 lists every `*.conf` digest across the four directories | c147–c150 |
| HF-20 | `systemd-soft-reboot.service` `LoadState=loaded`; `soft-reboot.target` `LoadState=loaded`. The PO-21 (i) condition paths are **not specified** in the accepted tree, so none was observed | c151; HF-NOTES |

## Absent, unreadable and unexpected facts

1. **CPython 3.12 is absent.** These are absent: `/usr/bin/python3.12`; the
   packages `python3.12`, `python3.12-minimal`, `libpython3.12-minimal` and
   `libpython3.12-stdlib`; and any `dpkg -S` owner. The available
   interpreter is CPython 3.14.4 at `/usr/bin/python3.14`. TR-9, HF-07,
   HF-08, HF-10 and PO-19 cite `/usr/bin/python3.12`. This is a version
   difference to record, not something this run accepts.
2. **`/etc/polkit-1/rules.d` is `root:polkitd` `0750`** and unreadable to
   `ubuntu`. Its file names and digests are `unreadable`, and whether
   `50-freedom-blades-rp11.rules` exists there is unknown (`PermissionError
   errno=13`).
3. **`/run/polkit-1` and `/run/polkit-1/rules.d` are absent** at
   observation time. `/usr/local/share/polkit-1/rules.d` is also absent.
4. **`/var/tmp` is subject to 30-day ageing** (`q /var/tmp 1777 root root 30d`).
5. **`unattended-upgrades.service` is running and enabled**, and the
   `apt-daily*` timers are enabled, so HF-07 values can change after this
   observation.
6. **`sha256sum`, `stat`, `sleep` and `sudo` in `/usr/bin` are symbolic
   links.** `coreutils` is `9.5-1ubuntu2+0.0.0~ubuntu25` with source
   `coreutils-from`. This `stat` and `sha256sum` print errors in the form
   `(os error 2)`. Link targets were not recorded.
7. `dpkg -S /lib64/ld-linux-x86-64.so.2` reports only a `libc6` diversion
   (`… .usr-is-merged`). The loader's real path is owned by `libc6:amd64`.
8. `apt-cache policy` received the argument `python3.12`. It printed entries
   for `postgresql-plpython3-12` and `postgresql-plpython3-12-dbgsym`, both
   `Installed: (none)` from `apt.postgresql.org`, and nothing for
   `python3.12` or `libpython3.12-*`. This is apt's pattern matching and not
   an installed package.
9. `binfmt_misc` has a registered `python3.14` entry (magic `2b0e0d0a`).
10. HF-16: `DefaultCPUAccounting`, `DefaultBlockIOAccounting` and
    `DefaultSmackProcessLabel` were not reported by systemd 259.
11. HF-17: `list-timers --all --no-legend` prints every column, including
    last-run times. The full output is retained, although §4.4.1 uses only
    names and next-run fields.
12. `readlink -f /usr/bin/python3.12` printed the path itself and exited
    `0`, although the file is absent (c093). This is GNU-style resolution of
    a missing final component and not evidence of presence.
13. HF-03's repository-ownership element and HF-15's capture-root parent
    were not observed. The first is withheld by the prompt; the second has no
    fixed input. HF-18 and the PO-21 (i) paths of HF-20 are `not specified`.

## Every remote command

Every command ran as `ubuntu` with the closed environment
`HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin`. Git commands additionally ran
under `env -i` with prompting, askpass, credential helpers, system/global
config, submodules and maintenance disabled, and only HTTPS allowed. The fixed
bootstrap (above) ran first and passed (no exit 70–73).

The payload commands' IDs, classes, UTC start/end, exit status and stdout file
are the verbatim retained `COMMANDS.index` (21250 bytes; its final newline is
not shown):

````text
c001-program-sha256	CTX	2026-10-06T02:49:26.842489Z	2026-10-06T02:49:26.847438Z	exit=0	stdout=c001-program-sha256.out
c002-program-stat	CTX	2026-10-06T02:49:26.848079Z	2026-10-06T02:49:26.853206Z	exit=0	stdout=c002-program-stat.out
c003-id-ru	CTX	2026-10-06T02:49:26.853814Z	2026-10-06T02:49:26.858902Z	exit=0	stdout=c003-id-ru.out
c004-id-u	CTX	2026-10-06T02:49:26.860627Z	2026-10-06T02:49:26.865814Z	exit=0	stdout=c004-id-u.out
c005-id-un	CTX	2026-10-06T02:49:26.867486Z	2026-10-06T02:49:26.872565Z	exit=0	stdout=c005-id-un.out
c006-id-run	CTX	2026-10-06T02:49:26.927294Z	2026-10-06T02:49:26.932640Z	exit=0	stdout=c006-id-run.out
c007-hf01-uname-n	HF-01	2026-10-06T02:49:26.934344Z	2026-10-06T02:49:26.939209Z	exit=0	stdout=c007-hf01-uname-n.out
c008-hf02-machine-id-sha256	HF-02	2026-10-06T02:49:26.940899Z	2026-10-06T02:49:26.945915Z	exit=0	stdout=c008-hf02-machine-id-sha256.out
c009-py3-readlink	PY	2026-10-06T02:49:26.946589Z	2026-10-06T02:49:26.951954Z	exit=0	stdout=c009-py3-readlink.out
c010-py3-stat	PY	2026-10-06T02:49:26.952628Z	2026-10-06T02:49:26.957929Z	exit=0	stdout=c010-py3-stat.out
c011-py3-stat-L	PY	2026-10-06T02:49:26.958572Z	2026-10-06T02:49:26.963810Z	exit=0	stdout=c011-py3-stat-L.out
c012-py3-version	PY	2026-10-06T02:49:26.964469Z	2026-10-06T02:49:27.032068Z	exit=0	stdout=c012-py3-version.out
c013-paths-lstat-before-git	CTX	2026-10-06T02:49:27.034087Z	2026-10-06T02:49:27.053605Z	exit=0	stdout=c013-paths-lstat-before-git.out
c014-git-version	GIT	2026-10-06T02:49:27.055606Z	2026-10-06T02:49:27.062477Z	exit=0	stdout=c014-git-version.out
c015-git-init	GIT	2026-10-06T02:49:27.063318Z	2026-10-06T02:49:27.072286Z	exit=0	stdout=c015-git-init.out
c016-git-fetch	GIT	2026-10-06T02:49:27.073425Z	2026-10-06T02:49:31.839885Z	exit=0	stdout=c016-git-fetch.out
c017-git-cat-file-type	GIT	2026-10-06T02:49:31.840798Z	2026-10-06T02:49:31.848346Z	exit=0	stdout=c017-git-cat-file-type.out
c018-git-rev-parse-pin	GIT	2026-10-06T02:49:31.850658Z	2026-10-06T02:49:31.858456Z	exit=0	stdout=c018-git-rev-parse-pin.out
c019-git-commit-header	GIT	2026-10-06T02:49:31.860510Z	2026-10-06T02:49:31.867654Z	exit=0	stdout=c019-git-commit-header.out
c020-git-checkout-detach	GIT	2026-10-06T02:49:31.868478Z	2026-10-06T02:49:32.646041Z	exit=0	stdout=c020-git-checkout-detach.out
c021-git-rev-parse-head	GIT	2026-10-06T02:49:32.646926Z	2026-10-06T02:49:32.654087Z	exit=0	stdout=c021-git-rev-parse-head.out
c022-git-status-porcelain	GIT	2026-10-06T02:49:32.656153Z	2026-10-06T02:49:33.065970Z	exit=0	stdout=c022-git-status-porcelain.out
c023-git-symbolic-ref	GIT	2026-10-06T02:49:33.068239Z	2026-10-06T02:49:33.075512Z	exit=1	stdout=c023-git-symbolic-ref.out
c024-git-remote-list	GIT	2026-10-06T02:49:33.076712Z	2026-10-06T02:49:33.083772Z	exit=0	stdout=c024-git-remote-list.out
c025-git-local-config	GIT	2026-10-06T02:49:33.127884Z	2026-10-06T02:49:33.135097Z	exit=0	stdout=c025-git-local-config.out
c026-gov-sha256	GOV	2026-10-06T02:49:33.138315Z	2026-10-06T02:49:33.147789Z	exit=0	stdout=c026-gov-sha256.out
c027-gov-acceptance-decision	GOV	2026-10-06T02:49:33.149917Z	2026-10-06T02:49:33.152097Z	exit=0	stdout=c027-gov-acceptance-decision.out
c028-gov-proposal-hf-sections	GOV	2026-10-06T02:49:33.152798Z	2026-10-06T02:49:33.156588Z	exit=0	stdout=c028-gov-proposal-hf-sections.out
c029-r5-prompt-decode	GOV	2026-10-06T02:49:33.158279Z	2026-10-06T02:49:33.163456Z	exit=0	stdout=R5-prompt.md
c030-r5-authority-decode	GOV	2026-10-06T02:49:33.164159Z	2026-10-06T02:49:33.169451Z	exit=0	stdout=R5-authority.md
c031-r5-copies-sha256	GOV	2026-10-06T02:49:33.227578Z	2026-10-06T02:49:33.232975Z	exit=0	stdout=c031-r5-copies-sha256.out
c032-r5-copies-stat	GOV	2026-10-06T02:49:33.235016Z	2026-10-06T02:49:33.240429Z	exit=0	stdout=c032-r5-copies-stat.out
c033-hf03-id-ubuntu	HF-03	2026-10-06T02:49:33.242415Z	2026-10-06T02:49:33.248997Z	exit=0	stdout=c033-hf03-id-ubuntu.out
c034-hf03-id-Gn-ubuntu	HF-03	2026-10-06T02:49:33.249686Z	2026-10-06T02:49:33.255975Z	exit=0	stdout=c034-hf03-id-Gn-ubuntu.out
c035-hf03-getent-passwd	HF-03	2026-10-06T02:49:33.256704Z	2026-10-06T02:49:33.260492Z	exit=0	stdout=c035-hf03-getent-passwd.out
c036-hf03-getent-group-ubuntu	HF-03	2026-10-06T02:49:33.261162Z	2026-10-06T02:49:33.263306Z	exit=0	stdout=c036-hf03-getent-group-ubuntu.out
c037-hf03-getent-group-adm	HF-03	2026-10-06T02:49:33.263920Z	2026-10-06T02:49:33.265687Z	exit=0	stdout=c037-hf03-getent-group-adm.out
c038-hf03-getent-group-cdrom	HF-03	2026-10-06T02:49:33.266284Z	2026-10-06T02:49:33.268285Z	exit=0	stdout=c038-hf03-getent-group-cdrom.out
c039-hf03-getent-group-sudo	HF-03	2026-10-06T02:49:33.268994Z	2026-10-06T02:49:33.270831Z	exit=0	stdout=c039-hf03-getent-group-sudo.out
c040-hf03-getent-group-dip	HF-03	2026-10-06T02:49:33.271430Z	2026-10-06T02:49:33.273239Z	exit=0	stdout=c040-hf03-getent-group-dip.out
c041-hf03-getent-group-lxd	HF-03	2026-10-06T02:49:33.273836Z	2026-10-06T02:49:33.328641Z	exit=0	stdout=c041-hf03-getent-group-lxd.out
c042-hf03-getent-group-freedomlab	HF-03	2026-10-06T02:49:33.329294Z	2026-10-06T02:49:33.331285Z	exit=0	stdout=c042-hf03-getent-group-freedomlab.out
c043-hf04-uname-mrv	HF-04	2026-10-06T02:49:33.331929Z	2026-10-06T02:49:33.337048Z	exit=0	stdout=c043-hf04-uname-mrv.out
c044-hf05-proc1-comm	HF-05	2026-10-06T02:49:33.337739Z	2026-10-06T02:49:33.343217Z	exit=0	stdout=c044-hf05-proc1-comm.out
c045-hf05-hf06-systemctl-version	HF-05/HF-06	2026-10-06T02:49:33.343898Z	2026-10-06T02:49:33.348458Z	exit=0	stdout=c045-hf05-hf06-systemctl-version.out
c046-hf07-dpkg-query-systemd	HF-07	2026-10-06T02:49:33.349260Z	2026-10-06T02:49:33.363843Z	exit=0	stdout=c046-hf07-dpkg-query-systemd.out
c047-hf07-dpkg-query-systemd-sysv	HF-07	2026-10-06T02:49:33.364562Z	2026-10-06T02:49:33.431964Z	exit=0	stdout=c047-hf07-dpkg-query-systemd-sysv.out
c048-hf07-dpkg-query-libsystemd0	HF-07	2026-10-06T02:49:33.432709Z	2026-10-06T02:49:33.448397Z	exit=0	stdout=c048-hf07-dpkg-query-libsystemd0.out
c049-hf07-dpkg-query-libsystemd-shared	HF-07	2026-10-06T02:49:33.449157Z	2026-10-06T02:49:33.463330Z	exit=0	stdout=c049-hf07-dpkg-query-libsystemd-shared.out
c050-hf07-dpkg-query-polkitd	HF-07	2026-10-06T02:49:33.464057Z	2026-10-06T02:49:33.478092Z	exit=0	stdout=c050-hf07-dpkg-query-polkitd.out
c051-hf07-dpkg-query-libpolkit-gobject-1-0	HF-07	2026-10-06T02:49:33.478852Z	2026-10-06T02:49:33.541249Z	exit=0	stdout=c051-hf07-dpkg-query-libpolkit-gobject-1-0.out
c052-hf07-dpkg-query-libc6	HF-07	2026-10-06T02:49:33.541998Z	2026-10-06T02:49:33.556142Z	exit=0	stdout=c052-hf07-dpkg-query-libc6.out
c053-hf07-dpkg-query-libc-bin	HF-07	2026-10-06T02:49:33.556870Z	2026-10-06T02:49:33.570863Z	exit=0	stdout=c053-hf07-dpkg-query-libc-bin.out
c054-hf07-dpkg-query-python3.12	HF-07	2026-10-06T02:49:33.571672Z	2026-10-06T02:49:33.638880Z	exit=1	stdout=c054-hf07-dpkg-query-python3.12.out
c055-hf07-dpkg-query-python3.12-minimal	HF-07	2026-10-06T02:49:33.639624Z	2026-10-06T02:49:33.653934Z	exit=1	stdout=c055-hf07-dpkg-query-python3.12-minimal.out
c056-hf07-dpkg-query-libpython3.12-minimal	HF-07	2026-10-06T02:49:33.654856Z	2026-10-06T02:49:33.669241Z	exit=1	stdout=c056-hf07-dpkg-query-libpython3.12-minimal.out
c057-hf07-dpkg-query-libpython3.12-stdlib	HF-07	2026-10-06T02:49:33.669975Z	2026-10-06T02:49:33.736307Z	exit=1	stdout=c057-hf07-dpkg-query-libpython3.12-stdlib.out
c058-hf07-dpkg-query-coreutils	HF-07	2026-10-06T02:49:33.737022Z	2026-10-06T02:49:33.750861Z	exit=0	stdout=c058-hf07-dpkg-query-coreutils.out
c059-hf07-dpkg-query-util-linux	HF-07	2026-10-06T02:49:33.751641Z	2026-10-06T02:49:33.765435Z	exit=0	stdout=c059-hf07-dpkg-query-util-linux.out
c060-hf07-dpkg-query-sudo	HF-07	2026-10-06T02:49:33.766095Z	2026-10-06T02:49:33.832113Z	exit=0	stdout=c060-hf07-dpkg-query-sudo.out
c061-hf07-dpkg-query-dbus	HF-07	2026-10-06T02:49:33.832805Z	2026-10-06T02:49:33.846844Z	exit=0	stdout=c061-hf07-dpkg-query-dbus.out
c062-hf09-ld-readlink	HF-09	2026-10-06T02:49:33.847915Z	2026-10-06T02:49:33.853111Z	exit=0	stdout=c062-hf09-ld-readlink.out
c063-hf07-dpkg-S-_usr_bin_python3.12	HF-07	2026-10-06T02:49:33.855090Z	2026-10-06T02:49:34.563709Z	exit=1	stdout=c063-hf07-dpkg-S-_usr_bin_python3.12.out
c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2	HF-07	2026-10-06T02:49:34.564475Z	2026-10-06T02:49:34.841187Z	exit=0	stdout=c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.out
c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor	HF-07	2026-10-06T02:49:34.841976Z	2026-10-06T02:49:35.149674Z	exit=0	stdout=c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.out
c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd	HF-07	2026-10-06T02:49:35.150457Z	2026-10-06T02:49:35.360449Z	exit=0	stdout=c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.out
c067-hf07-dpkg-S-_usr_bin_pkcheck	HF-07	2026-10-06T02:49:35.361226Z	2026-10-06T02:49:35.635502Z	exit=0	stdout=c067-hf07-dpkg-S-_usr_bin_pkcheck.out
c068-hf07-dpkg-S-_usr_bin_python3	HF-07	2026-10-06T02:49:35.637691Z	2026-10-06T02:49:35.860325Z	exit=0	stdout=c068-hf07-dpkg-S-_usr_bin_python3.out
c069-hf07-dpkg-S-_usr_bin_python3.14	HF-07	2026-10-06T02:49:35.862512Z	2026-10-06T02:49:36.137526Z	exit=0	stdout=c069-hf07-dpkg-S-_usr_bin_python3.14.out
c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2	HF-07	2026-10-06T02:49:36.139709Z	2026-10-06T02:49:36.362785Z	exit=0	stdout=c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.out
c071-hf07-dpkg-query-python3-minimal	HF-07	2026-10-06T02:49:36.363665Z	2026-10-06T02:49:36.428813Z	exit=0	stdout=c071-hf07-dpkg-query-python3-minimal.out
c072-hf07-dpkg-query-python3.14-minimal	HF-07	2026-10-06T02:49:36.429570Z	2026-10-06T02:49:36.449006Z	exit=0	stdout=c072-hf07-dpkg-query-python3.14-minimal.out
c073-hf07-dpkg-verify-systemd	HF-07	2026-10-06T02:49:36.449818Z	2026-10-06T02:49:36.933022Z	exit=0	stdout=c073-hf07-dpkg-verify-systemd.out
c074-hf07-dpkg-verify-systemd-sysv	HF-07	2026-10-06T02:49:36.933785Z	2026-10-06T02:49:36.955014Z	exit=0	stdout=c074-hf07-dpkg-verify-systemd-sysv.out
c075-hf07-dpkg-verify-libsystemd0	HF-07	2026-10-06T02:49:36.955782Z	2026-10-06T02:49:36.975787Z	exit=0	stdout=c075-hf07-dpkg-verify-libsystemd0.out
c076-hf07-dpkg-verify-libsystemd-shared	HF-07	2026-10-06T02:49:36.976517Z	2026-10-06T02:49:37.061420Z	exit=0	stdout=c076-hf07-dpkg-verify-libsystemd-shared.out
c077-hf07-dpkg-verify-polkitd	HF-07	2026-10-06T02:49:37.062154Z	2026-10-06T02:49:37.143719Z	exit=0	stdout=c077-hf07-dpkg-verify-polkitd.out
c078-hf07-dpkg-verify-libpolkit-gobject-1-0	HF-07	2026-10-06T02:49:37.144718Z	2026-10-06T02:49:37.163646Z	exit=0	stdout=c078-hf07-dpkg-verify-libpolkit-gobject-1-0.out
c079-hf07-dpkg-verify-libc6	HF-07	2026-10-06T02:49:37.164366Z	2026-10-06T02:49:37.254201Z	exit=0	stdout=c079-hf07-dpkg-verify-libc6.out
c080-hf07-dpkg-verify-libc-bin	HF-07	2026-10-06T02:49:37.254923Z	2026-10-06T02:49:37.290015Z	exit=0	stdout=c080-hf07-dpkg-verify-libc-bin.out
c081-hf07-dpkg-verify-python3.12	HF-07	2026-10-06T02:49:37.290720Z	2026-10-06T02:49:37.344381Z	exit=1	stdout=c081-hf07-dpkg-verify-python3.12.out
c082-hf07-dpkg-verify-python3.12-minimal	HF-07	2026-10-06T02:49:37.345296Z	2026-10-06T02:49:37.360349Z	exit=1	stdout=c082-hf07-dpkg-verify-python3.12-minimal.out
c083-hf07-dpkg-verify-libpython3.12-minimal	HF-07	2026-10-06T02:49:37.361098Z	2026-10-06T02:49:37.374969Z	exit=1	stdout=c083-hf07-dpkg-verify-libpython3.12-minimal.out
c084-hf07-dpkg-verify-libpython3.12-stdlib	HF-07	2026-10-06T02:49:37.375678Z	2026-10-06T02:49:37.435848Z	exit=1	stdout=c084-hf07-dpkg-verify-libpython3.12-stdlib.out
c085-hf07-dpkg-verify-coreutils	HF-07	2026-10-06T02:49:37.436606Z	2026-10-06T02:49:37.453288Z	exit=0	stdout=c085-hf07-dpkg-verify-coreutils.out
c086-hf07-dpkg-verify-util-linux	HF-07	2026-10-06T02:49:37.453995Z	2026-10-06T02:49:37.634437Z	exit=0	stdout=c086-hf07-dpkg-verify-util-linux.out
c087-hf07-dpkg-verify-sudo	HF-07	2026-10-06T02:49:37.635212Z	2026-10-06T02:49:37.696615Z	exit=0	stdout=c087-hf07-dpkg-verify-sudo.out
c088-hf07-dpkg-verify-dbus	HF-07	2026-10-06T02:49:37.697310Z	2026-10-06T02:49:37.748334Z	exit=0	stdout=c088-hf07-dpkg-verify-dbus.out
c089-hf07-dpkg-verify-python3-minimal	HF-07	2026-10-06T02:49:37.749057Z	2026-10-06T02:49:37.773019Z	exit=0	stdout=c089-hf07-dpkg-verify-python3-minimal.out
c090-hf07-dpkg-verify-python3.14-minimal	HF-07	2026-10-06T02:49:37.773774Z	2026-10-06T02:49:37.855151Z	exit=0	stdout=c090-hf07-dpkg-verify-python3.14-minimal.out
c091-hf07-apt-cache-policy	HF-07	2026-10-06T02:49:37.856078Z	2026-10-06T02:49:39.955066Z	exit=0	stdout=c091-hf07-apt-cache-policy.out
c092-hf08-stat-python312	HF-08	2026-10-06T02:49:39.957829Z	2026-10-06T02:49:40.028132Z	exit=1	stdout=c092-hf08-stat-python312.out
c093-hf08-readlink-python312	HF-08	2026-10-06T02:49:40.028887Z	2026-10-06T02:49:40.034230Z	exit=0	stdout=c093-hf08-readlink-python312.out
c094-hf08-sha256-python312	HF-08	2026-10-06T02:49:40.035046Z	2026-10-06T02:49:40.039993Z	exit=1	stdout=c094-hf08-sha256-python312.out
c095-hf08-version-python312	HF-08	2026-10-06T02:49:40.040768Z	2026-10-06T02:49:40.041794Z	exit=127	stdout=c095-hf08-version-python312.out
c096-hf08-sha256-python3-real	HF-08	2026-10-06T02:49:40.042488Z	2026-10-06T02:49:40.327411Z	exit=0	stdout=c096-hf08-sha256-python3-real.out
c097-hf08-stat-python3-real	HF-08	2026-10-06T02:49:40.328485Z	2026-10-06T02:49:40.344067Z	exit=0	stdout=c097-hf08-stat-python3-real.out
c098-hf09-ld-stat	HF-09	2026-10-06T02:49:40.345067Z	2026-10-06T02:49:40.448760Z	exit=0	stdout=c098-hf09-ld-stat.out
c099-hf09-ld-sha256	HF-09	2026-10-06T02:49:40.449532Z	2026-10-06T02:49:40.457364Z	exit=0	stdout=c099-hf09-ld-sha256.out
c100-hf09-ld-preload-lstat	HF-09	2026-10-06T02:49:40.458218Z	2026-10-06T02:49:40.477449Z	exit=0	stdout=c100-hf09-ld-preload-lstat.out
c101-hf09-ld-conf-d-ls	HF-09	2026-10-06T02:49:40.480795Z	2026-10-06T02:49:40.548014Z	exit=0	stdout=c101-hf09-ld-conf-d-ls.out
c102-hf09-ld-conf-d-sha256	HF-09	2026-10-06T02:49:40.549488Z	2026-10-06T02:49:40.557502Z	exit=0	stdout=c102-hf09-ld-conf-d-sha256.out
c103-hf10-stat-lstat	HF-10	2026-10-06T02:49:40.558329Z	2026-10-06T02:49:40.564412Z	exit=1	stdout=c103-hf10-stat-lstat.out
c104-hf10-stat-follow	HF-10	2026-10-06T02:49:40.565150Z	2026-10-06T02:49:40.570824Z	exit=1	stdout=c104-hf10-stat-follow.out
c105-hf11-lstat-xattr	HF-11	2026-10-06T02:49:40.571950Z	2026-10-06T02:49:40.645625Z	exit=0	stdout=c105-hf11-lstat-xattr.out
c106-hf12-rules-dirs-stat	HF-12	2026-10-06T02:49:40.646631Z	2026-10-06T02:49:40.666886Z	exit=0	stdout=c106-hf12-rules-dirs-stat.out
c107-hf12-rules-dirs-ls	HF-12	2026-10-06T02:49:40.667776Z	2026-10-06T02:49:40.738243Z	exit=0	stdout=c107-hf12-rules-dirs-ls.out
c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules	HF-12	2026-10-06T02:49:40.739946Z	2026-10-06T02:49:40.745679Z	exit=0	stdout=c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.out
c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example	HF-12	2026-10-06T02:49:40.746446Z	2026-10-06T02:49:40.751420Z	exit=0	stdout=c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.out
c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules	HF-12	2026-10-06T02:49:40.752169Z	2026-10-06T02:49:40.758266Z	exit=0	stdout=c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.out
c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules	HF-12	2026-10-06T02:49:40.759001Z	2026-10-06T02:49:40.764683Z	exit=0	stdout=c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.out
c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules	HF-12	2026-10-06T02:49:40.765385Z	2026-10-06T02:49:40.770966Z	exit=0	stdout=c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.out
c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules	HF-12	2026-10-06T02:49:40.771675Z	2026-10-06T02:49:40.828209Z	exit=0	stdout=c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.out
c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules	HF-12	2026-10-06T02:49:40.828927Z	2026-10-06T02:49:40.834759Z	exit=0	stdout=c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.out
c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules	HF-12	2026-10-06T02:49:40.835502Z	2026-10-06T02:49:40.841217Z	exit=0	stdout=c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.out
c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules	HF-12	2026-10-06T02:49:40.841948Z	2026-10-06T02:49:40.847514Z	exit=0	stdout=c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.out
c117-hf13-systemctl-show-unit	HF-13	2026-10-06T02:49:40.848281Z	2026-10-06T02:49:40.863405Z	exit=0	stdout=c117-hf13-systemctl-show-unit.out
c118-hf13-unit-paths	HF-13	2026-10-06T02:49:40.864316Z	2026-10-06T02:49:40.934370Z	exit=0	stdout=c118-hf13-unit-paths.out
c119-hf13-dropin-dirs-ls	HF-13	2026-10-06T02:49:40.936381Z	2026-10-06T02:49:40.956394Z	exit=0	stdout=c119-hf13-dropin-dirs-ls.out
c120-hf14-hf15-proc-self-mountinfo	HF-14/HF-15	2026-10-06T02:49:40.957131Z	2026-10-06T02:49:40.963843Z	exit=0	stdout=c120-hf14-hf15-proc-self-mountinfo.out
c121-hf14-binfmt-ls	HF-14	2026-10-06T02:49:40.964709Z	2026-10-06T02:49:41.035082Z	exit=0	stdout=c121-hf14-binfmt-ls.out
c122-hf14-read-python3.14	HF-14	2026-10-06T02:49:41.036612Z	2026-10-06T02:49:41.041947Z	exit=0	stdout=c122-hf14-read-python3.14.out
c123-hf14-read-status	HF-14	2026-10-06T02:49:41.042663Z	2026-10-06T02:49:41.048122Z	exit=0	stdout=c123-hf14-read-status.out
c124-hf15-findmnt-_	HF-15	2026-10-06T02:49:41.048895Z	2026-10-06T02:49:41.058708Z	exit=0	stdout=c124-hf15-findmnt-_.out
c125-hf15-df-_	HF-15	2026-10-06T02:49:41.059385Z	2026-10-06T02:49:41.062856Z	exit=0	stdout=c125-hf15-df-_.out
c126-hf15-findmnt-_usr_local	HF-15	2026-10-06T02:49:41.063473Z	2026-10-06T02:49:41.066497Z	exit=0	stdout=c126-hf15-findmnt-_usr_local.out
c127-hf15-df-_usr_local	HF-15	2026-10-06T02:49:41.067122Z	2026-10-06T02:49:41.069199Z	exit=0	stdout=c127-hf15-df-_usr_local.out
c128-hf15-findmnt-_usr_local_libexec	HF-15	2026-10-06T02:49:41.069919Z	2026-10-06T02:49:41.072871Z	exit=0	stdout=c128-hf15-findmnt-_usr_local_libexec.out
c129-hf15-df-_usr_local_libexec	HF-15	2026-10-06T02:49:41.073508Z	2026-10-06T02:49:41.075445Z	exit=0	stdout=c129-hf15-df-_usr_local_libexec.out
c130-hf15-findmnt-_etc	HF-15	2026-10-06T02:49:41.076069Z	2026-10-06T02:49:41.128063Z	exit=0	stdout=c130-hf15-findmnt-_etc.out
c131-hf15-df-_etc	HF-15	2026-10-06T02:49:41.128764Z	2026-10-06T02:49:41.130837Z	exit=0	stdout=c131-hf15-df-_etc.out
c132-hf15-findmnt-_etc_systemd_system	HF-15	2026-10-06T02:49:41.131470Z	2026-10-06T02:49:41.134724Z	exit=0	stdout=c132-hf15-findmnt-_etc_systemd_system.out
c133-hf15-df-_etc_systemd_system	HF-15	2026-10-06T02:49:41.135446Z	2026-10-06T02:49:41.137780Z	exit=0	stdout=c133-hf15-df-_etc_systemd_system.out
c134-hf15-findmnt-_etc_polkit-1_rules.d	HF-15	2026-10-06T02:49:41.138443Z	2026-10-06T02:49:41.141662Z	exit=0	stdout=c134-hf15-findmnt-_etc_polkit-1_rules.d.out
c135-hf15-df-_etc_polkit-1_rules.d	HF-15	2026-10-06T02:49:41.142326Z	2026-10-06T02:49:41.145172Z	exit=0	stdout=c135-hf15-df-_etc_polkit-1_rules.d.out
c136-hf15-findmnt-_var_lib	HF-15	2026-10-06T02:49:41.145876Z	2026-10-06T02:49:41.149130Z	exit=0	stdout=c136-hf15-findmnt-_var_lib.out
c137-hf15-df-_var_lib	HF-15	2026-10-06T02:49:41.149806Z	2026-10-06T02:49:41.151870Z	exit=0	stdout=c137-hf15-df-_var_lib.out
c138-hf15-findmnt-_var_tmp	HF-15	2026-10-06T02:49:41.152487Z	2026-10-06T02:49:41.156253Z	exit=0	stdout=c138-hf15-findmnt-_var_tmp.out
c139-hf15-df-_var_tmp	HF-15	2026-10-06T02:49:41.156924Z	2026-10-06T02:49:41.158978Z	exit=0	stdout=c139-hf15-df-_var_tmp.out
c140-hf15-findmnt-_run	HF-15	2026-10-06T02:49:41.159615Z	2026-10-06T02:49:41.162619Z	exit=0	stdout=c140-hf15-findmnt-_run.out
c141-hf15-df-_run	HF-15	2026-10-06T02:49:41.163278Z	2026-10-06T02:49:41.165424Z	exit=0	stdout=c141-hf15-df-_run.out
c142-hf15-findmnt-_run_polkit-1	HF-15	2026-10-06T02:49:41.166075Z	2026-10-06T02:49:41.168960Z	exit=1	stdout=c142-hf15-findmnt-_run_polkit-1.out
c143-hf15-df-_run_polkit-1	HF-15	2026-10-06T02:49:41.169621Z	2026-10-06T02:49:41.229135Z	exit=1	stdout=c143-hf15-df-_run_polkit-1.out
c144-hf16-manager-defaults	HF-16	2026-10-06T02:49:41.230841Z	2026-10-06T02:49:41.238474Z	exit=0	stdout=c144-hf16-manager-defaults.out
c145-hf17-list-timers	HF-17	2026-10-06T02:49:41.239308Z	2026-10-06T02:49:41.330974Z	exit=0	stdout=c145-hf17-list-timers.out
c146-hf17-update-units-show	HF-17	2026-10-06T02:49:41.331808Z	2026-10-06T02:49:41.362645Z	exit=0	stdout=c146-hf17-update-units-show.out
c147-hf19-tmpfiles-dirs-ls	HF-19	2026-10-06T02:49:41.363632Z	2026-10-06T02:49:41.439920Z	exit=0	stdout=c147-hf19-tmpfiles-dirs-ls.out
c148-hf19-tmp-conf-sha256	HF-19	2026-10-06T02:49:41.442758Z	2026-10-06T02:49:41.449319Z	exit=0	stdout=c148-hf19-tmp-conf-sha256.out
c149-hf19-tmpfiles-sha256	HF-19	2026-10-06T02:49:41.450338Z	2026-10-06T02:49:41.473393Z	exit=0	stdout=c149-hf19-tmpfiles-sha256.out
c150-hf19-tmpfiles-lines	HF-19	2026-10-06T02:49:41.474399Z	2026-10-06T02:49:41.477699Z	exit=0	stdout=c150-hf19-tmpfiles-lines.out
c151-hf20-soft-reboot-loadstate	HF-20	2026-10-06T02:49:41.478456Z	2026-10-06T02:49:41.545351Z	exit=0	stdout=c151-hf20-soft-reboot-loadstate.out
````

The three closing commands are recorded only in their `.meta` files, which
are reproduced verbatim (each file's final newline is not shown):

````text
id=c152-manifest-payload
hf=CLOSE
stdout=MANIFEST.payload
stderr=c152-manifest-payload.err
start_utc=2026-10-06T02:49:41.550294Z
end_utc=2026-10-06T02:49:41.748927Z
exit=0
id=c153-manifest-final
hf=CLOSE
stdout=MANIFEST.final
stderr=c153-manifest-final.err
start_utc=2026-10-06T02:49:41.749758Z
end_utc=2026-10-06T02:49:41.768796Z
exit=0
id=c154-inventory
hf=CLOSE
stdout=INVENTORY.owner-mode
stderr=c154-inventory.err
start_utc=2026-10-06T02:49:41.769635Z
end_utc=2026-10-06T02:49:41.868620Z
exit=0
````

Non-zero exits, each of which records an absence and not a failure of the
run:

- c023 is `symbolic-ref` = 1, which is the required detached result.
- c054–c057, c063 and c081–c084 cover `python3.12*`, which is not installed.
- c092, c094 and c095 cover `/usr/bin/python3.12`, which is absent (c095
  exit 127).
- c103 and c104 are `stat` with `/usr/bin/python3.12` absent; every other
  operand printed.
- c142 and c143 cover `/run/polkit-1`, which is absent.

The exact text of every command (`.cmd`) and its stdout and stderr are
reproduced verbatim in Appendix B.

## Evidence closure

- `MANIFEST.payload`: SHA-256 `f116244f94ca3ea42e51b0d1c2ea3e0c99257cecfafc5b9c13bd7fb742724503`, 64132 bytes, 612
  entries. It is reproduced verbatim in Appendix A.
- `MANIFEST.final`: SHA-256 `b8da7875b2f87a44483d9c744426855360279cc5f332f120fcac20bafe397553`, 103 bytes. Its content is
  `MANIFEST.payload  sha256=f116244f94ca3ea42e51b0d1c2ea3e0c99257cecfafc5b9c13bd7fb742724503  bytes=64132`. The aggregate digest of this evidence directory is the
  `MANIFEST.final` digest.
- `INVENTORY.owner-mode`: SHA-256 `70117b92702aa4690a75d6c23f5a93f620dc5117dc943a61d1417469842bee78`, 61987 bytes.
  - It has 623 file rows, all `reg`, `owner=ubuntu`, `group=ubuntu`,
    `mode=0600`, `nlink=1`, `fresh=yes`, `ok=yes`, and ends `violations=0`.
  - The directory row is `ubuntu` (uid 1001, gid 1001), mode `0700`.
  - It is reproduced verbatim in Appendix A.
- Controller verification against the echoed bytes and the locally held
  program:
  - all 612 payload entries were recomputed with
    0 mismatches;
  - `MANIFEST.final` equals `MANIFEST.payload`'s recomputed digest and
    length;
  - every inventory row names an echoed file or the program.
- Retained evidence files: 624 in total.
  - 612 payload files, including `controller-h0-program.sh`;
  - `MANIFEST.payload`, `MANIFEST.final` and `INVENTORY.owner-mode`;
  - nine closing records: `.cmd`, `.err` and `.meta` for each of c152, c153
    and c154.
- **Closing-command file lifecycle.** The retained `EXCLUSIONS`, the
  inventory and this handback agree exactly on the following. Each command's
  `.cmd`, an empty `.err` and its stdout file are created *before* it starts.
  Its `.meta` is created only *after* it exits.
  - **c152** (`MANIFEST.payload`): while it runs, `c152-manifest-payload.cmd`,
    `.err` and the open `MANIFEST.payload` exist. It excludes them by the
    prefixes `c152-manifest-payload.` and `MANIFEST.`. `c152…meta` does not
    exist yet. No c153 or c154 file exists yet.
  - **c153** (`MANIFEST.final`): `.cmd`, `.err` and `MANIFEST.final` exist
    before it starts. `.meta` comes after it exits.
  - **c154** (`INVENTORY.owner-mode`): `.cmd`, `.err` and the open
    `INVENTORY.owner-mode` exist before and during the run, and all are
    inventoried. `c154-inventory.err` **is** inventoried (it is 0 bytes).
  - The **only** file absent from the inventory is `c154-inventory.meta`,
    created after c154 exited. The controller confirmed this as
    `not_in_inventory = [c154-inventory.meta]`.

  This corrects R4's retained wording; R4's file is not changed.
- Explicit exclusions: the verbatim retained `EXCLUSIONS` file is in
  Appendix A. Nothing else is excluded.

## Repository, remote and controller changes

- **Repository:** only this handback file was written. No other repository
  file was changed, and there was no commit or push. Per
  `.agents/AGENTS.md`, a handback is linked from `Handover information`. The
  R5 authority permits only this single write, so the link is left to the
  maintainer or controller.
- **Remote (`oracle-test`):** exactly two paths were created, and both are
  retained.
  - `/var/tmp/p5-r5-rp11-h0-20261006-02-evidence` holds closed evidence:
    624 files, `ubuntu:ubuntu` `0700`.
  - `/var/tmp/p5-r5-rp11-h0-20261006-02-checkout` is a clean checkout
    detached at the pin, with one shallow commit fetched and no remote.

  Nothing else was written, cleaned up or removed.
- **Controller:** scratchpad files only, outside the repository: the program,
  its template and inputs, the SSH stdout/stderr capture, the extracted
  evidence copy, a validation copy and its dry-run tree.

## Disclosures about controller-side activity

1. **No controller-side network preflight was issued.** There was no
   `git ls-remote`, `git fetch`, `curl` or HTTP/API request. The only
   network action was the single SSH execution connection.
2. **Offline local checks** read only the local repository:
   - `git cat-file -t` of the pin;
   - `git branch -r --contains` against local refs (it shows
     `origin/docs/platform-plan`);
   - `git show` of the pin's four governing files to compute expected
     digests;
   - `sha256sum` of the R5 prompt and authority.
3. **Program source.** The program was derived from R4's program template,
   read from an earlier session's local scratchpad, by changing:
   - the work ID, URL, paths, handback path and R5 prompt/authority
     digests;
   - the `EXCLUSIONS` text, which now names the closing commands and their
     file lifecycle exactly;
   - the "R4" labels in comments and `HF-NOTES`.

   The HF command set is unchanged from R4's reviewed template.
4. **Local validation** used scratchpad paths only:
   - a `bash -n` syntax check;
   - a stub-`ssh` extraction of the 13 SSH arguments.
   - An unmodified bootstrap simulation, which refused at the identity check
     with exit 70 (`id: 'ubuntu': no such user`) and created nothing under
     `/var/tmp`.
   - A full dry run of a **transformed copy**:
     - scratch evidence and checkout paths;
     - `file:///opt/freedom-blades/platform` retrieval with
       `GIT_ALLOW_PROTOCOL=file`;
     - identity checks adapted to the controller user;
     - every HF-labelled command replaced by a stub, so the controller's own
       machine-id, packages, units, mounts and polkit/tmpfiles directories
       were **not** read.

     The dry run executed `readlink -f /usr/bin/python3`, `stat` of
     `/usr/bin/python3` and the Python version literal on the controller. It
     reached `H-0 PROGRAM COMPLETE` with `violations=0`, and only
     `c146-inventory.meta` was missing from its inventory.
5. **Copies.** The R5 prompt and authority copies were embedded from the
   controller's repository files. Their digests equal the authority's pin and
   the retained copies.

## Prohibited-action confirmation

Each of the following was **not** done:

- a second SSH connection or retry;
- a nested Claude client;
- a controller-side network preflight;
- SCP, SFTP, rsync, or agent, X11 or port forwarding;
- interactive authentication, or reading or copying a credential, key,
  `known_hosts` or SSH config;
- `sudo` or any privilege;
- a package operation, installation, build or test (`apt-cache policy` read
  local lists only, with no `apt update`);
- a service or database mutation;
- H-1/H-2, activation or a pass;
- rollback or cleanup;
- removal of either exclusive path;
- an environment dump;
- any read of `/tmp`, secrets, application data, PostgreSQL, earlier
  checkout or evidence paths, or `/opt/freedom-blades/platform` on
  `oracle-test`;
- a commit or push.

## Checks not run

- No test suite, because the assignment does not authorize one.
- These HF elements were not observed:
  - HF-03 repository ownership (withheld by the prompt);
  - HF-15 capture-root parent (no fixed input);
  - HF-18 (not specified);
  - HF-20 PO-21 (i) condition paths (not specified);
  - the contents of `/etc/polkit-1/rules.d` (unreadable without privilege).
- Symlink targets of the HF-10 binaries other than `python3` were not
  recorded.
- No acceptance of any version difference. PO-19, PO-11 (f), PO-21 and the
  other citations are OH-S2 work and remain unauthorized.

## Appendix A — verbatim retained context and closing files

Each block is the exact retained file content as echoed by the program. A
trailing newline in a file appears as an empty last line inside its fence. A
0-byte file is shown only by its `(0 bytes)` label, with no fence. Sizes are byte counts computed by the
controller over the echoed bytes. SHA-256 values are in `MANIFEST.payload`,
and for the three closing outputs above. `R5-prompt.md` and `R5-authority.md`
are byte-identical to the repository files named at the top. Their base64
sources `R5-prompt.b64` (9378 bytes) and `R5-authority.b64`
(3036 bytes) are listed in `MANIFEST.payload` and not reproduced.

### `RUN-CONTEXT` (1498 bytes)

````text
work_id=C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-20261006-02
program_start_utc=2026-10-06T02:49:26.841798Z
canonical_url=https://github.com/ming-themerciless/freedom-platform.git
pinned_commit=46d1c35a029ca8287779ae87d08a370ba0a0f2ef
remote_account=ubuntu
remote_nodename=Test
fixed_checkout_preserved_not_inspected=/opt/freedom-blades/platform
isolated_checkout=/var/tmp/p5-r5-rp11-h0-20261006-02-checkout
evidence_directory=/var/tmp/p5-r5-rp11-h0-20261006-02-evidence
durable_controller_handback=docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-handback.md
program_environment=HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin (set by the bootstrap; not read or dumped)
controller_command_shape=ssh -T -o BatchMode=yes -o ClearAllForwardings=yes -o ForwardAgent=no -o ForwardX11=no -o PermitLocalCommand=no oracle-test "<fixed bootstrap: real/effective ubuntu, uname -n Test, umask 077, both exclusive paths absent (test -e / test -L), mkdir -m 0700 evidence, tee stdin to controller-h0-program.sh, chmod 0600, require sha256 = SHA256 and stat %s = BYTES, exec env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin /bin/bash --noprofile --norc controller-h0-program.sh>" < PROGRAM
controller_program_digest_and_length=supplied to the bootstrap as literals; recomputed below by command c001/c002
r5_prompt_expected_sha256=57d23c1ba683ce8c2be15fe101da959a9dc1334ff89a1b0c66f917f26cf42e8e bytes=6942
r5_authority_expected_sha256=ddc0f9f1ca3c556f34a7844b6f6e969d8dc192ced37a7aef13a17bee75ffce66 bytes=2245

````

### `RUN-END` (65 bytes)

````text
program_end_utc=2026-10-06T02:49:41.546125Z
payload_commands=151

````

### `HF-NOTES` (1642 bytes)

````text
HF observations recorded without a command, and design-input gaps (R5 H-0, C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-20261006-02)
HF-03: repository ownership of /opt/freedom-blades/platform is NOT observed. The R5 prompt forbids inspecting the preserved fixed checkout; its stat is withheld.
HF-06: derived from HF-05/HF-06 systemctl --version, HF-07 dpkg-query (polkitd, libc6) and HF-08 interpreter version commands; no separate command.
HF-08: the cited interpreter is /usr/bin/python3.12; R5 additionally records the available /usr/bin/python3 resolution (py3-* and hf08-*-python3-real commands). Version differences are facts, not acceptance.
HF-11: templated §4.2.3 paths (<record_id>, <activation_id>, <RUN>, temporary trees .rp11-<RUN>-<tag>.tmp) have no concrete name at H-0 and are not observed; their concrete parents are.
HF-15: the capture-root parent is not fixed (MI.capture_root_A remains a maintainer input; §4.1.5). Not observed; not invented.
HF-16: explicit -p list of Default* names plus Version; no name containing Environment is queried; names the installed manager does not report are simply absent from output.
HF-18: not specified. The accepted tree names no interactive-client path (OH-D-2 decided option (b) without naming one). Design-input gap; no search and no installation performed.
HF-19: digests and /var/tmp, /run/polkit-1, /run/freedom-blades-rp11 lines are recorded for every *.conf in /etc, /run, /usr/local/lib and /usr/lib tmpfiles.d.
HF-20: PO-21 (i) names no concrete condition path in the accepted tree (its citation is OH-S2 work). Recorded as not specified; only the two LoadState values are observed.

````

### `EXCLUSIONS` (2418 bytes)

````text
Manifest exclusions (R5 H-0, C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-20261006-02)
Every command record is written in this order: .cmd, then an empty .err, then the stdout file, all BEFORE the command starts;
the command then runs with stdout and stderr appended to those files; .meta is written only AFTER the command exits.
Closing commands, in order: c152-manifest-payload (writes MANIFEST.payload), c153-manifest-final (writes MANIFEST.final), c154-inventory (writes INVENTORY.owner-mode).
c152-manifest-payload: before it starts, c152-manifest-payload.cmd, c152-manifest-payload.err and an empty MANIFEST.payload exist; while it runs, the same three exist; c152-manifest-payload.meta is created after it exits.
MANIFEST.payload lists every regular file in the evidence directory while c152-manifest-payload runs, except names beginning with
'c152-manifest-payload.' (c152-manifest-payload.cmd and c152-manifest-payload.err, which exist; c152-manifest-payload.meta, which does not yet exist) or 'MANIFEST.' (MANIFEST.payload itself, open).
No c153-manifest-final.* or c154-inventory.* file, MANIFEST.final or INVENTORY.owner-mode exists yet while c152-manifest-payload runs, so none is listed.
c153-manifest-final: before it starts, c153-manifest-final.cmd, c153-manifest-final.err and an empty MANIFEST.final exist; c153-manifest-final.meta is created after it exits. It reads only MANIFEST.payload.
MANIFEST.final names only MANIFEST.payload's full SHA-256 and byte length.
c154-inventory: before it starts, c154-inventory.cmd, c154-inventory.err and an empty INVENTORY.owner-mode exist; while it runs, the same three exist; c154-inventory.meta is created after it exits.
INVENTORY.owner-mode lists every file present while c154-inventory runs: all payload files, MANIFEST.payload, c152-manifest-payload.cmd/.err/.meta,
MANIFEST.final, c153-manifest-final.cmd/.err/.meta, c154-inventory.cmd, c154-inventory.err (empty when created; it existed before c154-inventory started) and INVENTORY.owner-mode itself (still open, marked own-output-open).
The only evidence file absent from INVENTORY.owner-mode is c154-inventory.meta, because it does not exist until c154-inventory has exited.
COMMANDS.index lists the payload commands only; the three closing commands are recorded solely in their own .cmd/.err/.meta files.
No evidence file is excluded for any other reason. Retained program controller-h0-program.sh is payload.

````

### `MANIFEST.payload` (64132 bytes)

````text
3681b99783a13c6c255b5cd2d00e978de2c435d2585a672e7fbb6300b32cd835  21250  COMMANDS.index
a590e3a4798ec710a104cb938e141a38f7907ac5ec4ccfb389b29f95e824ce4b  2418  EXCLUSIONS
7ceed7036119672148dac463bd3db50211ff0b1c82d3cf948ecee31e142e802b  1642  HF-NOTES
5fe4e31e33956a61bb52d2a71f81df2ed86d2c47aa2c0c2972f50fdc75ea63df  3036  R5-authority.b64
ddc0f9f1ca3c556f34a7844b6f6e969d8dc192ced37a7aef13a17bee75ffce66  2245  R5-authority.md
86cfc21ae31c8cd5b4f63a819450ad681655f882eb0cec824ad101e453f9f472  9378  R5-prompt.b64
57d23c1ba683ce8c2be15fe101da959a9dc1334ff89a1b0c66f917f26cf42e8e  6942  R5-prompt.md
2b7bdefdcdd917d982d5f47046df5ec7ecc13056114dd66bf9c5009f647b0879  1498  RUN-CONTEXT
054dac55881cac30a1116017aac772f190a0cf12a38405fb850cb6a707e0e975  65  RUN-END
36ca130a7aa7e4e3bae57a6396afffa7e3a5d11bbbd2408dd196992ed7749b1c  91  c001-program-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c001-program-sha256.err
7cc1b6a845b6fd8ebaea2724a01b7511db4ce1ae2043fcc233dccfb7c59f026e  173  c001-program-sha256.meta
3a948dbbffed26cac39f0bec4b6b2b8ad858de105c9a332d128be98b6fde05ce  135  c001-program-sha256.out
fea4534ff15bc60f64d37bed2120bed4e76ac8443cac54745fa069d27a3a236c  128  c002-program-stat.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c002-program-stat.err
0e935ac316b53f3a8ca7dd4bace50f4dcd265134ca6ee59d4aec06f72953a394  167  c002-program-stat.meta
83bd88d05410faad527729443ccedc3410edfb8e4a570f75e69af34fa8179e2e  58  c002-program-stat.out
798b11d7f3717e79fa5a7dc6e520867551e8433fd518f8bbf7406c8d534bc665  16  c003-id-ru.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c003-id-ru.err
fe579afb830df3f0beef69f2aef288403cc04893fe1d5a44e3231af48e985a56  146  c003-id-ru.meta
d6a1a767319c3bf2a337b16e3a14916f63e432872e0f8df1cb73b32a8b338ae4  5  c003-id-ru.out
9bdceab1a7aa03b04c0718aa52f8c284e0474cdb262fe8affbfd674d99df9a5c  15  c004-id-u.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c004-id-u.err
00105fda4fa7e07683fc8670bfe51505f63d49a97332af95c5457affea379a3b  143  c004-id-u.meta
d6a1a767319c3bf2a337b16e3a14916f63e432872e0f8df1cb73b32a8b338ae4  5  c004-id-u.out
424807431da2c471d482cc7994ef1b2e77243e298e522cf424eeed9a52a890f5  16  c005-id-un.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c005-id-un.err
98d7d04e17c94182e7f7d96e7ffd862a7a5f4cb484f45fb9deb3a7631d77b0ae  146  c005-id-un.meta
da4d47d486c674b0e05b992713276b345aaa1858d3f147b4b185ad5215cfdc69  7  c005-id-un.out
bad37ef90e6ee7910f07a56394a6963176b7b476f31b29c6c733a403019096fa  17  c006-id-run.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c006-id-run.err
fcd32ea44e2c8fc84b7540aa14d5451a569083b59024c40f527a48c0b0f915bb  149  c006-id-run.meta
da4d47d486c674b0e05b992713276b345aaa1858d3f147b4b185ad5215cfdc69  7  c006-id-run.out
219a4d23f04743b974f422332709ba0c6464cf03b1d4c6b3b0cfdd92014a71d4  18  c007-hf01-uname-n.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c007-hf01-uname-n.err
355d959808772b1ea44e92348c1907a96bcea3b1dea8a4b1c2825395f6f7cd15  169  c007-hf01-uname-n.meta
c9d04c9565fc665c80681fb1d829938026871f66e14f501e08531df66938a789  5  c007-hf01-uname-n.out
897e893080611fb9038034bcd3f60291a066f557d868ffc2027f1b409b365807  35  c008-hf02-machine-id-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c008-hf02-machine-id-sha256.err
e8cd9936a67f7ceff044b66c3c4915578a8a61f2e0bb1327db610989e5b0ef91  199  c008-hf02-machine-id-sha256.meta
0726bfdac8860577e63af5a4ec48c0f47027b912eabf1dcc115033d01aab82d2  82  c008-hf02-machine-id-sha256.out
5759c545d894116dcdde17f8c725da7b913b67120506500f7d6136b002ddd378  41  c009-py3-readlink.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c009-py3-readlink.err
4cfda9fef61420e94b4685f3d185c5f86b36878039536c4408ad0b9285d6615d  166  c009-py3-readlink.meta
65d0f645c13836692cffcd74d743a8b88f47bbfe824b29c6079c9d6968b8ff03  20  c009-py3-readlink.out
c88824fbad31deda456a739c9b421894bb681680d0b356f88da732b0f43ba55b  76  c010-py3-stat.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c010-py3-stat.err
4187083d22d1f5ceed01330b15c675f81dff24961af3f2235c3e8802b8c5d35c  154  c010-py3-stat.meta
d4688fe7bb3c8f0385d31b0dedd71b501b7a1bb75cf41fde90b3593fa9e9b3b5  66  c010-py3-stat.out
993267674a4ed4e76047bbe249d2cc68a292acebf443e2ea1f2b41806497b250  88  c011-py3-stat-L.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c011-py3-stat-L.err
a249466367a373bd7f87faf727b86a86a9ee4dba046c48afcb31683f9f35121d  160  c011-py3-stat-L.meta
018155c9f57ac932110e1df0de3f9a843834c2fb9430be9bc648efa63133c0df  78  c011-py3-stat-L.out
63175f7de94efd38edef1684eed925a5424e6e235a9076c87023f2c306cd677d  405  c012-py3-version.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c012-py3-version.err
6fc3eb3fea4c52ba818d326bb475e409518e2a4be7dc6de8d653604da1f6c129  163  c012-py3-version.meta
6734d508cd94a6727a582960647cfccabfc83b5befc9f230aaaf2a408dba7d4c  237  c012-py3-version.out
466346cfa258ccd100da3a64a92a071c47ccecc0ef8c50774d56523f9683344d  2295  c013-paths-lstat-before-git.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c013-paths-lstat-before-git.err
314b434e1d8a1d93e0703c92a23b92a0d15f1de56ab330270ba987ed5e2d8391  197  c013-paths-lstat-before-git.meta
3fb5d26081113bb5487a846aa9077c6e817e8537d7e0599976ed8d56ed8ea096  214  c013-paths-lstat-before-git.out
ebb972e24b60a02f9e947b51acbaf8b9e1a9006650f261b635a59c5a550c0823  280  c014-git-version.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c014-git-version.err
dc7cdbb33f3088af40a48854117800eb6f8ce37932c11acf76ad09ccdbe74930  164  c014-git-version.meta
97452bcde974ef512f9552791fc4f6a3219a724877671fba270baca1a6075b74  19  c014-git-version.out
4d756608ea66a24813bb474996c576c4f08a383cb833f8a16ddb6866bfbfba5f  752  c015-git-init.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c015-git-init.err
34fda00f9089feafe05875f9ccbc7634108eee5b8361b7ab308f038e9854f6e9  155  c015-git-init.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c015-git-init.out
4bbc3bdb92d0bdd4e15980653fd73c54b024df67e34d9982bee4c782a3db60b3  868  c016-git-fetch.cmd
5145e438a61d20795168d2f8a23c3217ee6878ecf787b19446f3159803c08b78  135  c016-git-fetch.err
9b804e274ad53e9156656049e734dd9315882c9e12dccdf154d329d91ddf2fb8  158  c016-git-fetch.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c016-git-fetch.out
2d1f1628c34f70153270c1489feccbccc3e2c77cd36653f83f82f2f472bfefe4  748  c017-git-cat-file-type.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c017-git-cat-file-type.err
24ff2109e05c483896a42ec964f6eb55ecb236947128c014e9b8d245a6eb0cdd  182  c017-git-cat-file-type.meta
50836eee574ecff79dea3b4fd40673d7d000f7a5f177d8a6a3000b59c78383b8  7  c017-git-cat-file-type.out
c1d6b27ee4f87b322e60d9160a57d0f1acc98d74b3a842a55e83446eefa570a9  784  c018-git-rev-parse-pin.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c018-git-rev-parse-pin.err
7e27e5061d03959edcb7ff2575cedd37bc17fff829b4aab472f46f994c2ae5e3  182  c018-git-rev-parse-pin.meta
ea09ca6293ced37a62fcdad23a6b083d7cf9f89fa76a8923375fb277e23dab02  41  c018-git-rev-parse-pin.out
4268b16e2f67b600ecfb3b3d8d41dd6f1f0d8ca1d217da8efe5180339588c74f  748  c019-git-commit-header.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c019-git-commit-header.err
ca8153117e28650cb3b8e661a4ab0e34c281fe99e08d12aec5080294ff7031fe  182  c019-git-commit-header.meta
2fb88f4461e3de6e9982f899dcef602f87ac0c6f8e5138bb306aac920c6c1d3a  326  c019-git-commit-header.out
de64f2a450c2ad27537449159868d1599408b0ac1896f2a89c4e3d77cd650ec6  754  c020-git-checkout-detach.cmd
c42bfd58075a1e3759b6e6ab76518fc3dfccdc50e7afe081afa3be2540db6125  125  c020-git-checkout-detach.err
a90a1891f328e8578aab599bfd0f3ef9b3d3e59502bd4b38b0100a77ef1873d0  188  c020-git-checkout-detach.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c020-git-checkout-detach.out
12bb59c028e1ce28e2c17d899ff40cbe3cb1f7855636b1168fb1b2717c8be6ff  710  c021-git-rev-parse-head.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c021-git-rev-parse-head.err
02289216d0d0eddd7ca79ce0254811dbb16c8a9a25bc6a71ab427a0d597801c7  185  c021-git-rev-parse-head.meta
ea09ca6293ced37a62fcdad23a6b083d7cf9f89fa76a8923375fb277e23dab02  41  c021-git-rev-parse-head.out
73ead63603b009f72ab2fe5573fda42f9deefa17b3ea97cfbf74f0a0409d90d9  739  c022-git-status-porcelain.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c022-git-status-porcelain.err
0e88b6f600f6f171cc1f475813fb9f9c03ca3100d93dbf28c1ad4d38d93f3770  191  c022-git-status-porcelain.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c022-git-status-porcelain.out
17d15fb09036614a950b0032efa5a5c564fa16b108f8731e06acdbae913f9dd3  716  c023-git-symbolic-ref.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c023-git-symbolic-ref.err
6e642bd8942d1c539dabe6b770ca7ab43882360e93b24af59567123ff4cd9a25  179  c023-git-symbolic-ref.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c023-git-symbolic-ref.out
616fb38c30ad4b4f91881c1644b95c45233dbe237b5835fde45a2fc1e58c2261  705  c024-git-remote-list.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c024-git-remote-list.err
a0f4997b092c3e6b9e95f94370a47c7cc104ffbdb2080ea0a9beadb971834d7f  176  c024-git-remote-list.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c024-git-remote-list.out
28bf256e4cc113e030631e7cdab152ae5d587d1bc1424d0d660b1574ce46152f  717  c025-git-local-config.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c025-git-local-config.err
bfe2c83b977f72df245f112f38775dda67c94c197f6d5a72b8d2112caf803d6f  179  c025-git-local-config.meta
0ccbb3ab3a91a81952aaaab4d84e5cd90820a13adcd8407b417bd5a1ac15b37b  93  c025-git-local-config.out
c9745f38188c7ac6ab74a84e54ff7f30af0274f5695b22e558074644202ff369  427  c026-gov-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c026-gov-sha256.err
a7b93972e6cc1734fce062347427c4ad4718180191b0117a36bd792a1531484f  161  c026-gov-sha256.meta
9d5773b34ec48e67edae12266b6fb44a8a07e2aae3a472c881dc379cfbdbc639  669  c026-gov-sha256.out
139bd86d5f2c0f25701a8f6d1a68cb5e6af4b94a731a8cd1efe7b60e3ef525fe  219  c027-gov-acceptance-decision.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c027-gov-acceptance-decision.err
74e8b34ede578def85d308a42c8c502d0c40c1f47a222a8ac95700db76e61f0a  200  c027-gov-acceptance-decision.meta
c31da71bd1e8b91cd21cf0df7f31143ee2dd0f1baf6b606259e8d54dcf84bfd4  81  c027-gov-acceptance-decision.out
a57d7d91236350b11a8fdcd27777eed5b88bf0b533f086a46b92729657daec88  269  c028-gov-proposal-hf-sections.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c028-gov-proposal-hf-sections.err
230af4ffc71b35ab8072a048ca15f572571291c0202077404e8859961c84297a  203  c028-gov-proposal-hf-sections.meta
4df5b869549f0b2f296bb1198bf484977c54801325e5db9a9cca09ce6977f923  4068  c028-gov-proposal-hf-sections.out
6e74568612a21a6d42fde7dbbbc94ffcb7bb319196912d3643d62a0950cbc1ae  80  c029-r5-prompt-decode.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c029-r5-prompt-decode.err
5d25f7729277bf7b1fd3eadab97befb4fc3b3d6fbf85c12b3fd600761513aa21  166  c029-r5-prompt-decode.meta
6e090c68bda2bcfa38c031551d444f205a6b9fa3c8614ad453c390d4afa85660  83  c030-r5-authority-decode.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c030-r5-authority-decode.err
f606731c82d93dfbebaac2b21ba2b9b0e6b770fb40491630050ae578f6a2ca81  175  c030-r5-authority-decode.meta
3d2f31c0633935def0ca68b17be3fc11835f8c0b3210265061c5742f33cdd9f2  139  c031-r5-copies-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c031-r5-copies-sha256.err
27ece8a9e93864a9541570beec16e2addf81c3530d0b3846eface2d664572436  179  c031-r5-copies-sha256.meta
a2e5a4d029ba4c72f1806f579fe934636cbcdce1e46bcc0b8d5306c6c8170c9b  249  c031-r5-copies-sha256.out
c5390377ddd795d86ce2e4df1064c75e8d9d7c3636ac5be188cf5b6febd595c8  144  c032-r5-copies-stat.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c032-r5-copies-stat.err
208c49b758f1375a195f368cecaf269b57fe3ae6ffc7e5f9d994a0d85fb07e90  173  c032-r5-copies-stat.meta
c3dc23c20e7294a039f017eca0f1d6b5b3b80b731cb264b4fc3376205999da52  127  c032-r5-copies-stat.out
fbdebade4f63b689aa079bfe46923d6059619980ca0e46c9621eb7dd78c6b585  19  c033-hf03-id-ubuntu.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c033-hf03-id-ubuntu.err
d9eee2a465fd518e35f31586971f87958ede05800274b7b70fb21c3c23fbde1a  175  c033-hf03-id-ubuntu.meta
632bce81cb80922cc67f7dce007173410e77da74eaf1689b50a9393de188dc3c  113  c033-hf03-id-ubuntu.out
b82607568d6e8d291a14c91554868ad91eff75e309bbd3685b7b38225f0cd3ed  23  c034-hf03-id-Gn-ubuntu.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c034-hf03-id-Gn-ubuntu.err
4679b3ed9e9b74b02bc82de244a12d1631599cf9ed5c60d5cac2b84f6a39a89c  184  c034-hf03-id-Gn-ubuntu.meta
8f5042686f35f52d09b1c22cf7113e59f2e321bacf229e1c2e85c3e0b2e8111c  41  c034-hf03-id-Gn-ubuntu.out
9b3ab2f0530608057bfd2a688ef8928269ba09dee65bbcd1cbbb8c7dbad68de5  30  c035-hf03-getent-passwd.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c035-hf03-getent-passwd.err
fee68887b0b2e7ff18de707762b1b77aca9e18bfdf4e3c3b3c36fb0aedd3d811  187  c035-hf03-getent-passwd.meta
d7a2ea2ec497aed134330c6052bc1fd27a44ad552c914be48d0f118226726301  49  c035-hf03-getent-passwd.out
c273e3200feeacd4bd1c7941cab33f0b9897054f6386ab66eaae4e11c58905f2  29  c036-hf03-getent-group-ubuntu.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c036-hf03-getent-group-ubuntu.err
85e85a1e6108a081a6cb207bc0dbddc8e8b629dfb1fbb50fc3a5fbd151bcba0a  205  c036-hf03-getent-group-ubuntu.meta
81b84c3436d28202e99662d1be20bbca8d63e7049326351615ec3733ba4e865f  15  c036-hf03-getent-group-ubuntu.out
bb8e25426e676aa3a0086ba238ac0affa12fded6b91813c46d75f4f2c741c7b0  26  c037-hf03-getent-group-adm.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c037-hf03-getent-group-adm.err
dcdaad8e4b84a618f0742949ebdf456d97bb31d67e6cf3f254c9de9e5cf410f3  196  c037-hf03-getent-group-adm.meta
21a48ff78ef76a6e1dba4b02e169e06e452feb9218a098aaf2b265759b1207ac  29  c037-hf03-getent-group-adm.out
309ce9198d2830f4706b4945bf28274e8b1b0d446bb3728f59208491c812ae6c  28  c038-hf03-getent-group-cdrom.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c038-hf03-getent-group-cdrom.err
92c0f2802f9c43a36245ec2c9f33efb1952bd555d7fd53eb925087f2f55ed692  202  c038-hf03-getent-group-cdrom.meta
5627653bb12f4fc691fd1a59de3534276b1629931e82f96f0c2c2c8b0b519c7e  18  c038-hf03-getent-group-cdrom.out
a705ff28cbf3ee1ae6b18c37e99eb5cf08e3c66c0548ab5b118a080820a2f2e4  27  c039-hf03-getent-group-sudo.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c039-hf03-getent-group-sudo.err
0abfbf46867c8507d999d8ea17be0a04bc978465733f088b4d1b08d6a6903a06  199  c039-hf03-getent-group-sudo.meta
f051e8b0904a145137b9648e2ede1a70e1616f431c36c0a3f294ab0d63d2cea1  17  c039-hf03-getent-group-sudo.out
0a452f22d9c28b4153f15e808660e9fb3f1e50588e911f612b8bb2898612a4c9  26  c040-hf03-getent-group-dip.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c040-hf03-getent-group-dip.err
ab9e28e04059ab427e693bf18e76a687cd7a7eca9fecb4f1faf6684deae4f08c  196  c040-hf03-getent-group-dip.meta
1a7cfed1203e75cbbb3828da31bcda37d208909b340cf388922bc6d5571606f5  16  c040-hf03-getent-group-dip.out
e59c9a464489c762131b5e95e78a3b2429820e4d424881944e8dbc82ac69adb1  26  c041-hf03-getent-group-lxd.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c041-hf03-getent-group-lxd.err
6c13e72aa06187dd9bec03528dd11fb68d416bf03746d1167172c3c55238d261  196  c041-hf03-getent-group-lxd.meta
2ab135cbdd5a2153bffc84b3c5fb0d9f09c036ee7f2ac2bf1faeec1818be1588  17  c041-hf03-getent-group-lxd.out
1418ba2fcd1630fb478d209e8c05591533b132c216bc83cde3509a2236798377  33  c042-hf03-getent-group-freedomlab.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c042-hf03-getent-group-freedomlab.err
f5e0217afa1d4503e090770f55dc96c94a9adea52e7908f04aa6ca89393bfbf5  217  c042-hf03-getent-group-freedomlab.meta
1aced04baad56de851b39ec028a80343c23660523d910c1f327ccebce981e168  24  c042-hf03-getent-group-freedomlab.out
173c1ad2661f57bfc4ffab23aeeafc084e39281810f5910503cc3fc0d58e1c11  24  c043-hf04-uname-mrv.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c043-hf04-uname-mrv.err
c9e31424a07b9122f406c4cce9b886ac9dd4236b313943b93733d5784debc6b3  175  c043-hf04-uname-mrv.meta
d91b9923becd6aa169a3af515872f03da35652cf721af6c505030185d2b45b53  84  c043-hf04-uname-mrv.out
798f85c8a15af8f47020239befdef97588738f1d3d70d6e44a4c3bf856af7489  26  c044-hf05-proc1-comm.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c044-hf05-proc1-comm.err
c5cfafe2252ed4192e674da46d57d5504f825d9592bd089176c37dcc2acfb728  178  c044-hf05-proc1-comm.meta
12e6ff4feb1b552a431b41d3935d33f08f9d75ddb8a88f645f4cf231bc05e820  8  c044-hf05-proc1-comm.out
1e42320d2f29d6e669f1e8fd690c836a20b2ee0def34a8c8510da6cf3049b768  29  c045-hf05-hf06-systemctl-version.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c045-hf05-hf06-systemctl-version.err
4eb66aef898f27d00cac9a2acb29fbd6709a8ddd51f2a4b4ebdf07aa8d84267a  220  c045-hf05-hf06-systemctl-version.meta
b1ee098b5dc4fc35466eb97120463b37738af82ee5d71e1d22d7d0a9bab191ee  342  c045-hf05-hf06-systemctl-version.out
07285095bed4fa8a8f1f0405d335b82326deeb8f9d55b7e26d7d072180207e40  135  c046-hf07-dpkg-query-systemd.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c046-hf07-dpkg-query-systemd.err
1391fee32fe8a752043f8c21579390f03046d59aa27274d587260931e82212bb  202  c046-hf07-dpkg-query-systemd.meta
9eeab5ff70ea1c974c8274dd6553d5b76be352d89e96109b2dc250b9becc0f5f  36  c046-hf07-dpkg-query-systemd.out
ae9049a663deecfa9944b23d98c993f59a8985fb0f01f0e6e540183e180fddfd  140  c047-hf07-dpkg-query-systemd-sysv.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c047-hf07-dpkg-query-systemd-sysv.err
225cb2679de2b0888fd5dcc62a75159bbd7516648596cf5260d9afb81c6ffd90  217  c047-hf07-dpkg-query-systemd-sysv.meta
9b29e70272c846a48c4ce70533badafdaec8bc2aaea974b32d43158d8606f8a1  48  c047-hf07-dpkg-query-systemd-sysv.out
a2f2e3b933c38ef74a63c32e4f6d2f0238d8a32220c4625583fffc158a57dece  139  c048-hf07-dpkg-query-libsystemd0.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c048-hf07-dpkg-query-libsystemd0.err
a67db4388df32f022d303b2d4ea628523b7751486687ad6611d32a27f5287341  214  c048-hf07-dpkg-query-libsystemd0.meta
3fbbdcae1ba9257ed133a3b5a33099f838eeb562bd4e3006756f662fab0f2c4f  53  c048-hf07-dpkg-query-libsystemd0.out
4d6158ca6f244e340f6cdbe4c71b02f0d329eeabc8eb2b57d3d71bf7cfa79b68  145  c049-hf07-dpkg-query-libsystemd-shared.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c049-hf07-dpkg-query-libsystemd-shared.err
bd76a5c25e367d3442ec06bba3c561a40f8b893c7813366a248b5aa8397231f8  232  c049-hf07-dpkg-query-libsystemd-shared.meta
b008ef3ab004ec4445906d35d65d6f1ff87de90b97e042eba57b5bcf2f55e8c2  59  c049-hf07-dpkg-query-libsystemd-shared.out
76663fe19eb52878cf1a80952a96fdb48c242439d92d45a72cca70257601aee0  135  c050-hf07-dpkg-query-polkitd.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c050-hf07-dpkg-query-polkitd.err
332dba4a227c4acf69f9bdaa54f25f2ce24d9a81689a599a39a1fb4e79c4e894  202  c050-hf07-dpkg-query-polkitd.meta
6652f58f280f85180822f59846a9fb4ddfb1c7bf74f63c322e58762f1e0dcd48  45  c050-hf07-dpkg-query-polkitd.out
3398d97ed243a2d18c187b9d844c441c56b4610463c2f59e67163a2403519b7d  149  c051-hf07-dpkg-query-libpolkit-gobject-1-0.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c051-hf07-dpkg-query-libpolkit-gobject-1-0.err
d3a6c99a76bb0b820e8c9d3787aefde7d44327edcf8ff97231285f212c9680d1  244  c051-hf07-dpkg-query-libpolkit-gobject-1-0.meta
47d8c3b590562b900664d4adedcfbf7bf0cba0dceff46d8ada6e90f37d04424b  65  c051-hf07-dpkg-query-libpolkit-gobject-1-0.out
defe72223789b96830ac0641b85793995bb681538b693733394943ea4051d22c  133  c052-hf07-dpkg-query-libc6.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c052-hf07-dpkg-query-libc6.err
3d8bfa5191f255943214a1bb4dc837754ff31c45a812e62c7ab0f3ed1165f180  196  c052-hf07-dpkg-query-libc6.meta
9f00a36e2a0f675972c4faab9443f57ee363b584c959b55500a1da0ef9e12222  44  c052-hf07-dpkg-query-libc6.out
247c9dd9310a6d79ecb71f996feb7c7cff793e403944be8c823162d9f34d27cb  136  c053-hf07-dpkg-query-libc-bin.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c053-hf07-dpkg-query-libc-bin.err
ccbcf22f62432949be157e64ef21bba01b429385e64df4f870e1808feaf22796  205  c053-hf07-dpkg-query-libc-bin.meta
f0eaf250db76daedd2024d7ebcd24e6a5fab144024910e5c5529ac7790dcea77  41  c053-hf07-dpkg-query-libc-bin.out
124d90602533e4223f4e4f187bd5fe0d4dfc1fb2c3b249b12a6fc774ca7f67c0  138  c054-hf07-dpkg-query-python3.12.cmd
6fdadf2c9f32ce4deec3386aacd862be59581f64ae9c37984bc14041563ab808  50  c054-hf07-dpkg-query-python3.12.err
4961b6432b93a71462dd4196084035111ddb8756eb78bd12108ea1da2bcfb3d8  211  c054-hf07-dpkg-query-python3.12.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c054-hf07-dpkg-query-python3.12.out
28bedb780854c5adb44f56b5c348ad5485383a522d6c71eba0c0a62279405a33  146  c055-hf07-dpkg-query-python3.12-minimal.cmd
8f8aa53c2ad2a29fbac4f1fff4aa4baa382c2da90b83bee335c61fc3f83969a4  58  c055-hf07-dpkg-query-python3.12-minimal.err
5f00f364dc8e7bb6a460d4bf2b50e38bda71b37aa8efec24618138df929de6f2  235  c055-hf07-dpkg-query-python3.12-minimal.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c055-hf07-dpkg-query-python3.12-minimal.out
1d223a263dec0ed5c10ee51d2d3ea9c3aaf58118e8806c8c4d00586aaee6c027  149  c056-hf07-dpkg-query-libpython3.12-minimal.cmd
eae0d115bb15599115bb6779c0b07d8d753da5fc8e8b48ae2c1b87c812e79977  61  c056-hf07-dpkg-query-libpython3.12-minimal.err
90cba7b921fbfc0bd4f115cd73f96b706bdfd5c84461046f25ce0f611d5f3a14  244  c056-hf07-dpkg-query-libpython3.12-minimal.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c056-hf07-dpkg-query-libpython3.12-minimal.out
4ab690132e2d68053af168df2003e15afcb15868cc3a46ad849051adb3080acf  148  c057-hf07-dpkg-query-libpython3.12-stdlib.cmd
54cb98478ace7f79a50e576a7dd9788ffc7f79b14790457bd67077bf694fefc6  60  c057-hf07-dpkg-query-libpython3.12-stdlib.err
71cbd89ff0287132ea07db78085f802f5d228d1b976b812fdaaf6bafe435fc8e  241  c057-hf07-dpkg-query-libpython3.12-stdlib.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c057-hf07-dpkg-query-libpython3.12-stdlib.out
03a8dbf6b19aefe57814e9ee9f261dc96dcd9ab7e577b617568399df58d3f0c7  137  c058-hf07-dpkg-query-coreutils.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c058-hf07-dpkg-query-coreutils.err
c028a3c2d5246cf3d1dbc5be59eda61bf327e2a04463846030ecd75bc6c0337d  208  c058-hf07-dpkg-query-coreutils.meta
65de56954bed55c57ea8e37d2751e9c698d00cdcae005dc57d6b8f97cb3d3e28  78  c058-hf07-dpkg-query-coreutils.out
f646c6d37cf0e48139d24d55de16272a810df1878f87df815e3e6c719066bf26  138  c059-hf07-dpkg-query-util-linux.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c059-hf07-dpkg-query-util-linux.err
49e81064abc809ff8b1e0002eb5ae82b037a360fbac7cc2188059af15fa6fe81  211  c059-hf07-dpkg-query-util-linux.meta
18e3b23ff786def59c7ad3b526506a55f46573ce4cee379754521ad6e9289ec5  40  c059-hf07-dpkg-query-util-linux.out
3d14b7f6f864999273105a464473ab8a0abac24db22d93598f7b2db2d40f4865  132  c060-hf07-dpkg-query-sudo.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c060-hf07-dpkg-query-sudo.err
a6b924c3d43a7800a85875a89fdfc949e97fdf7a737e0f4bd78484716a639f73  193  c060-hf07-dpkg-query-sudo.meta
1a34d295b034911730314b4a58967b919fa839c7b8430bfdd4531fea12f62ec0  36  c060-hf07-dpkg-query-sudo.out
395ae3dd519e3bb14f8a879f31953c9aeae212bb6fbd2ca4d3b6433982899b80  132  c061-hf07-dpkg-query-dbus.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c061-hf07-dpkg-query-dbus.err
09c4dbfd0713a6b7e8c9d143383f0618bf9c0e0cbf2ba46bbe87efd86490eecc  193  c061-hf07-dpkg-query-dbus.meta
4ddecf2b06e9bbae53242ea0a80a816dac4c03ae136e929d8f64aa579d9795e4  32  c061-hf07-dpkg-query-dbus.out
3b50583fa76587faf62b30cb8de3825aab75e49f628aa3d7008e2f6bf872455e  52  c062-hf09-ld-readlink.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c062-hf09-ld-readlink.err
acc5a17c2800b4a6809ba91a6dfb7b1a25096e813bde6a188f1ce7db6b831ff2  181  c062-hf09-ld-readlink.meta
b0b6f9ea475eb5f7740d37ca1e1bbf59edd3058b85a65569cee70ebfa2e32219  47  c062-hf09-ld-readlink.out
8883085048677e04ff2f5fc7671993328a34a7feefbf34243b4a87eae570c3eb  37  c063-hf07-dpkg-S-_usr_bin_python3.12.cmd
9b31ff111e9b0d398072116bd0ebc14fd20f691b2888784c813190ae772c1ab3  63  c063-hf07-dpkg-S-_usr_bin_python3.12.err
7db3ebb6f47542283190db0b9cf6697c94e84d5c7d8d422b01630027f7a54198  226  c063-hf07-dpkg-S-_usr_bin_python3.12.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c063-hf07-dpkg-S-_usr_bin_python3.12.out
87b139a8032fa59e47342b3ca47c543c6088705881a322819221b8559eab868e  45  c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.err
09e15ce9a3f9fd122a6947ebee6ce3c61a8babb09e6396e6f603ad7b83e78bb5  250  c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.meta
899d6e7821a1d8af970202cb05e8fde5a2ddeafa8ab0648f3c7184f5cc74fded  118  c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.out
11e3b1d0255956c69e25be078bfc2c09943ad0bdc317cd49efbbc45dd283903c  51  c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.err
672508442bfa9698943f08251a49c410a7b7c176a64968fc33d890896fb8ccc6  268  c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.meta
a25b16fee34e96187d16cf128eb403a505693a3740e4b5985598a4037b745190  43  c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.out
6de0851160f14bfd37b4f28a16ec6970ba8c3731c7d0b1e16beaad0974d2441f  43  c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.err
6625793d4e6b8f56ee391c9b033445ee14e39ca0b45f9a11236bcd8d74329d29  244  c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.meta
a17d4d267c1b106c2c551ce2f24457fb25f4a67347c6293d9e4f70c2b7fa5cce  35  c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.out
9603a0c2e8bb0a542f93b8a8f87710d6beb8f3ee38acbec75a2455ce2ca30926  34  c067-hf07-dpkg-S-_usr_bin_pkcheck.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c067-hf07-dpkg-S-_usr_bin_pkcheck.err
f7ada7002f43a67b16957bd87ea25eb41cc8f6d9919e911b68765578f0f80794  217  c067-hf07-dpkg-S-_usr_bin_pkcheck.meta
550c0ce32fbce3275e14b23fb730cc0967b0001d03ffc39c0142084a63682116  26  c067-hf07-dpkg-S-_usr_bin_pkcheck.out
17b03df9f58555054c5caf86faa624365354f3b6fb26e1712b8928cfee6979d2  34  c068-hf07-dpkg-S-_usr_bin_python3.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c068-hf07-dpkg-S-_usr_bin_python3.err
7eb7d6c839a0e7f9f080b7d6109ace2ac27240a75d6b0f05656e981039f534db  217  c068-hf07-dpkg-S-_usr_bin_python3.meta
467489312dfbc07eaf9cf87e100c06537e65e2cbb18a623b7649f1874c634758  34  c068-hf07-dpkg-S-_usr_bin_python3.out
62c69f137961e3ba40223581e3ce4112ca191265c82ee320251ae8a21d6a5ec2  37  c069-hf07-dpkg-S-_usr_bin_python3.14.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c069-hf07-dpkg-S-_usr_bin_python3.14.err
b9f88c4b7656ec64947401450f822b42c2c89c7d8e2e73055f5bea29c9ecf370  226  c069-hf07-dpkg-S-_usr_bin_python3.14.meta
d6c7ce4153f26aaddc04e8a87ea459a87bbff834adf979f9e704a51d44395411  40  c069-hf07-dpkg-S-_usr_bin_python3.14.out
b4dc19384fb55d6ad08ddd6ede29dffa8d9c9e290f4ac0cc80a47de5bff4039b  64  c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.err
1b61d25abf92b63bcc3ed82c668b07665728121e74d6bc0c34e76e4799b4969d  307  c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.meta
c1d5853b459ef036a57e9faa8d0c14efe371964c1e2889fd9b012440920932a4  60  c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.out
b3b8fd1a3ca2d8e7636a290ea0c17fe18332fe5c1f4d35edf2d3d7463d1eaa30  143  c071-hf07-dpkg-query-python3-minimal.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c071-hf07-dpkg-query-python3-minimal.err
e2302291920c9e1dab69a4858da34b7de6c8748b7e44073aeb0bbd607a5b028f  226  c071-hf07-dpkg-query-python3-minimal.meta
b31f4eb61ac49b4de7c2aa08c4d7293e069d732e5d1bf9696723e8cd14a7f281  59  c071-hf07-dpkg-query-python3-minimal.out
c5eee51d9703a5d0e47ece635da64181df8c3e3d4e93cc2c355dcee357de7251  146  c072-hf07-dpkg-query-python3.14-minimal.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c072-hf07-dpkg-query-python3.14-minimal.err
c68b49bbe94bff8aaa7ffb2fa869aa315c806e03c4f824b0657cc1595fdabbab  235  c072-hf07-dpkg-query-python3.14-minimal.meta
48a9a80dfb86a500cdc683f74d9814612d3a89e764cf02ed71653998e3015b44  58  c072-hf07-dpkg-query-python3.14-minimal.out
8db9482c3fca41dcd7cb50c74c2c7f0cd5df28a068745c6e5f8cf347b9610046  31  c073-hf07-dpkg-verify-systemd.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c073-hf07-dpkg-verify-systemd.err
50a549e73c7d84c4cc50a90564bb2a5d1e9aceca9a81d64db72858fe2e720d9c  205  c073-hf07-dpkg-verify-systemd.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c073-hf07-dpkg-verify-systemd.out
f93f08f51afc89cafacc4de4093868b3f36f8c9f54deea0f8b112a79694719e0  36  c074-hf07-dpkg-verify-systemd-sysv.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c074-hf07-dpkg-verify-systemd-sysv.err
3993c5ae19d19749d1ffa529be54f8f1717b41300ee2db1204a177b506341d4e  220  c074-hf07-dpkg-verify-systemd-sysv.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c074-hf07-dpkg-verify-systemd-sysv.out
e38db896d6504973e6b2386b103d0b897a6bdfa1ceed54300e8489c116ff54c3  35  c075-hf07-dpkg-verify-libsystemd0.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c075-hf07-dpkg-verify-libsystemd0.err
ebf9caec97b4f5735d249feda1c50bf725ff2f38ef1b16822aa2422a2154d432  217  c075-hf07-dpkg-verify-libsystemd0.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c075-hf07-dpkg-verify-libsystemd0.out
fe22668dfefa73b9693b2241ca33ea2c0ccc2e6d6ec95534f8ce91ccd06d7d34  41  c076-hf07-dpkg-verify-libsystemd-shared.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c076-hf07-dpkg-verify-libsystemd-shared.err
9f06d34f97f27345cccb419e693850fbb15240b41d63f8a0a6069930d5fe6aef  235  c076-hf07-dpkg-verify-libsystemd-shared.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c076-hf07-dpkg-verify-libsystemd-shared.out
8b3568ca9f983e2727db743f1be67876532f359cc9a14544cad640d251cc5c47  31  c077-hf07-dpkg-verify-polkitd.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c077-hf07-dpkg-verify-polkitd.err
537b0d5e70563494cf6f59b6176cc2066c467dc77ff96e0da7315ca70be39a93  205  c077-hf07-dpkg-verify-polkitd.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c077-hf07-dpkg-verify-polkitd.out
f11e3281c98d8db9495f0a81bba0e82575b55e9f4d70fe0145fdade0ebfd4e5c  45  c078-hf07-dpkg-verify-libpolkit-gobject-1-0.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c078-hf07-dpkg-verify-libpolkit-gobject-1-0.err
7d6d126e1fd9be37869d75781132bcb2647772e29dfdb0cc9454cb983e0256c2  247  c078-hf07-dpkg-verify-libpolkit-gobject-1-0.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c078-hf07-dpkg-verify-libpolkit-gobject-1-0.out
53c00ece0a532ae44cc1f5d96dd278e80b6362c869331a01b4085b4cc69c6d3d  29  c079-hf07-dpkg-verify-libc6.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c079-hf07-dpkg-verify-libc6.err
d9e334c0ef07e208063346e748a5fc5c67aa6093d19e36264d629030fea57712  199  c079-hf07-dpkg-verify-libc6.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c079-hf07-dpkg-verify-libc6.out
00843745715874ed1b0ef1c4f1ead6a24f5129fec23d9964a9c60a2816262d2c  32  c080-hf07-dpkg-verify-libc-bin.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c080-hf07-dpkg-verify-libc-bin.err
3c1c34ab98c8f0e0a593397f96303d6b96fcf9ce6ac8a6f314596a998466d0d8  208  c080-hf07-dpkg-verify-libc-bin.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c080-hf07-dpkg-verify-libc-bin.out
133c572c3e249b61ac4615f6126a9e5903bba41025f22470af83e9d66e27d8cc  34  c081-hf07-dpkg-verify-python3.12.cmd
93cc694c0729bd84ea4db8d272da534b7f97d877d272c90f74d0278bbb63e209  44  c081-hf07-dpkg-verify-python3.12.err
6af5e0a81278f5230f4eeee70cb093b96fbbcac508fef703a4ca7ed018a6b502  214  c081-hf07-dpkg-verify-python3.12.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c081-hf07-dpkg-verify-python3.12.out
070da521de8576da300b91d0828026be16676368001fcbff0923631e0a18d6e2  42  c082-hf07-dpkg-verify-python3.12-minimal.cmd
8236da284518728339f1aa6fdb48a897726b3c98ba5291943770cdbed5a5f031  52  c082-hf07-dpkg-verify-python3.12-minimal.err
f5c2b3d63aa28f75bbcabecef2fb7418a1c50f6f106af64bd4c65eea2123e769  238  c082-hf07-dpkg-verify-python3.12-minimal.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c082-hf07-dpkg-verify-python3.12-minimal.out
3f92fd9d860e2e11ae2249f2d7038bd92b2d1ebfdc46c0a7b56d92bf848390ff  45  c083-hf07-dpkg-verify-libpython3.12-minimal.cmd
007a129ef89836fe6ee9f667dcf23df1ed276931bb125feefc7d430e738b99ac  55  c083-hf07-dpkg-verify-libpython3.12-minimal.err
9ee87d2119e11a8c34a9d8cae33e36b1b87a4e5422a991e85575ce1fdab38187  247  c083-hf07-dpkg-verify-libpython3.12-minimal.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c083-hf07-dpkg-verify-libpython3.12-minimal.out
99d1c399e0e9b1c2bca2b46d9da685b50f4b081ee0a50b44e7e9935d6a975c56  44  c084-hf07-dpkg-verify-libpython3.12-stdlib.cmd
34a0bd0aecdde512f91a57e9d7476176442e1f6deabc53ea66c1b4efcb3cdcdf  54  c084-hf07-dpkg-verify-libpython3.12-stdlib.err
862251b895cf54f311d6234df0654c5da4069a2504958f6df86b8e34c3177489  244  c084-hf07-dpkg-verify-libpython3.12-stdlib.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c084-hf07-dpkg-verify-libpython3.12-stdlib.out
16c75b0b2ca9bb68b5f54c1cddae5341700e19b44f384c0d25ae0c0f264db65a  33  c085-hf07-dpkg-verify-coreutils.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c085-hf07-dpkg-verify-coreutils.err
de935421ee184b9ae14b0e8bbb1dc4db5a4dfc9c23f3b5e4ab0bbbae8269940c  211  c085-hf07-dpkg-verify-coreutils.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c085-hf07-dpkg-verify-coreutils.out
3b3c5b2f44b5ab565b55ab6c3c17fdd92a0dbd80121020d26ff2fcdc2bbe2063  34  c086-hf07-dpkg-verify-util-linux.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c086-hf07-dpkg-verify-util-linux.err
6dd4510289b95144fa3efa3b631bfaa9e540344786ecc40512b229498bac80fc  214  c086-hf07-dpkg-verify-util-linux.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c086-hf07-dpkg-verify-util-linux.out
9c0333411fa56e5bcc39291c8550177d2f469342a726fb496c7af6ce88fa2e5a  28  c087-hf07-dpkg-verify-sudo.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c087-hf07-dpkg-verify-sudo.err
a60d43ae9859f730ed0025863726f3d9f848cac380adea392a667dc83d33751b  196  c087-hf07-dpkg-verify-sudo.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c087-hf07-dpkg-verify-sudo.out
16decac61733f4c878e18f45da6e3ac02a6de758c404a10c21d430b97360a9ee  28  c088-hf07-dpkg-verify-dbus.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c088-hf07-dpkg-verify-dbus.err
fcb30b52e5b6e2bc7df6f3a76c54c22d86e1b2dad162ece76e55afe2098f58e1  196  c088-hf07-dpkg-verify-dbus.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c088-hf07-dpkg-verify-dbus.out
47a9cdf5d32847204dd4ca10a161c801cf8c8fb159bdd086188f8d82f28a4094  39  c089-hf07-dpkg-verify-python3-minimal.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c089-hf07-dpkg-verify-python3-minimal.err
60b526583ebfa03a92605a6fbfb74072c1a10a7e2fdd9c9a3bbb478df5f70f49  229  c089-hf07-dpkg-verify-python3-minimal.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c089-hf07-dpkg-verify-python3-minimal.out
0a09aed8ca5ee58a9c9ff81b061d0ab428b3a7df5834bc5b53c07a04fc3f6049  42  c090-hf07-dpkg-verify-python3.14-minimal.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c090-hf07-dpkg-verify-python3.14-minimal.err
5e6ce1f9d81012183b2dbcdcdc77a2cd08c04a93886337259f504276d28f940e  238  c090-hf07-dpkg-verify-python3.14-minimal.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c090-hf07-dpkg-verify-python3.14-minimal.out
64f0b0ddd8925266573c4b1cea0c6de75ff36c2e4bac2d702d2b7bee590c43bf  261  c091-hf07-apt-cache-policy.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c091-hf07-apt-cache-policy.err
8bbb8972770dee6be19632ef158b8c49f247dd04e47937821f56bd0509d5d53e  196  c091-hf07-apt-cache-policy.meta
fb9e07c5928b4c5785013a6921b52280f43b6f972947cf916cb9bdfa359b053b  6396  c091-hf07-apt-cache-policy.out
76c88f057ce690fccb7812d5332e037c26a05c00b0a4f7937fb30fc8d9b65680  88  c092-hf08-stat-python312.cmd
22d68a8520944d7010eac56df0797105bef64a6beac55918c2974361765933e9  80  c092-hf08-stat-python312.err
b7ae919e201d8dcdd18115371ff7a439c17aad6a23f952c574b0b1b07ffad370  190  c092-hf08-stat-python312.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c092-hf08-stat-python312.out
ae5e28260ee6b8405c58e68d19a7c2903310711816ceb5c2d56477dd77c387c3  44  c093-hf08-readlink-python312.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c093-hf08-readlink-python312.err
287c665ed3487d5a05818203275cfe0f295fe34837ec8a0dbaaac7713572487a  202  c093-hf08-readlink-python312.meta
251ccfcd2e674f7179aece078f9d69c47f168905552bf747c2310c2a41b75fad  20  c093-hf08-readlink-python312.out
f8aba8efa46899fb2b63d2dbffc93680631e7736dc07d3115205e47a702a2c42  42  c094-hf08-sha256-python312.cmd
089df4b5426a92f244027bf5aaede99f50e9065f18ba12d00c5ee3b9be30f78b  58  c094-hf08-sha256-python312.err
1e563c93dd8e7e7ea043ef6f4de2f61d2d3c29973c36a4209e2722175842bfa8  196  c094-hf08-sha256-python312.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c094-hf08-sha256-python312.out
47e7a864663d8a6082c27965af3dbbb97e67a27cc701dd1d1e4a0995e6439668  408  c095-hf08-version-python312.cmd
74c5b9bdd1a754316f3a9efdfaaf132db8e374a5662da5738150278c53343a40  126  c095-hf08-version-python312.err
888280e575ec38ed037cba323553e4bed0a32eb6ffd630ba956e761982c57738  201  c095-hf08-version-python312.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c095-hf08-version-python312.out
b5d1b2947a9b600077e32f29bf6e96d9c95fe3ab55f50ef80ec8412a4977fa80  42  c096-hf08-sha256-python3-real.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c096-hf08-sha256-python3-real.err
f7697bae25185c13b5354b5c6f5b4d8789a167089ddad9d110aeb723cdc1839c  205  c096-hf08-sha256-python3-real.meta
f8f2038ffb9541b0ffd7e2cb459b583c422d0269b96f83d3f65f47ee79a8f6ca  86  c096-hf08-sha256-python3-real.out
3456f329b79bc2c1ac006299cacd1ed45cdb697d04b6594404c27cd2aaf7487f  88  c097-hf08-stat-python3-real.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c097-hf08-stat-python3-real.err
9984db38729956587edf3754c3f4d79c6ac62cfd172f709f9b837bcdc714bf8d  199  c097-hf08-stat-python3-real.meta
398e1d4413fa8394bfeefa68ae3087fa7e0469f3ba25f4be16bf6871e912b023  81  c097-hf08-stat-python3-real.out
513d163d3abce338f89c50e6653e8092e22acc1981f966389cf75aa78c20e59a  2352  c098-hf09-ld-stat.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c098-hf09-ld-stat.err
452399f4d0deb8eb930229028c4a82b9be5ee77c806012846c3ce681455ec9e4  169  c098-hf09-ld-stat.meta
bbaac0a6ec1095e5b8e1866eab24f72eec448aa640e5058d3ec7fc8fdbfac67f  734  c098-hf09-ld-stat.out
c121315f200e456702fce3f0c1234e9e4e6a2735e4f16d7d5bd10c31bce40a83  102  c099-hf09-ld-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c099-hf09-ld-sha256.err
d6e1e231fad7ad31183b04a6ef785910fd5c30ac1d38d36b509257fa22e68b79  175  c099-hf09-ld-sha256.meta
bac27691ba4f852acc50727694dc089a7262b64fd96dcb39eef8d328c4aa182d  278  c099-hf09-ld-sha256.out
e36914fe6781be729af80774bc70e4a94e049182247a22b7ea929d760f78c48a  2226  c100-hf09-ld-preload-lstat.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c100-hf09-ld-preload-lstat.err
81de6ff44ba9a41a3ffba8a4e1fec6759b00ad8bc2e9e74a8bc9fa2bae0280ef  196  c100-hf09-ld-preload-lstat.meta
0d5686c7a0ae5e0317779373ad5c8067b172ccf1f9b8f583ad66e80366fcf7e4  26  c100-hf09-ld-preload-lstat.out
fc50e1a1f71a3a959eb2a0782977c77beba4db8e71f5fbc9818e31395208c0ec  2223  c101-hf09-ld-conf-d-ls.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c101-hf09-ld-conf-d-ls.err
06170788ac0753dc5cc9f99326011dad32fdf64cd1c2ffebca9f3c4d4730e0fc  184  c101-hf09-ld-conf-d-ls.meta
abb7a75759f58f65d5804e1203456ae228574c8aa63964f64dae757d6d2812b6  460  c101-hf09-ld-conf-d-ls.out
4cbb4aafdb5642cf05e082a8926071849cfaa747af14a0bd52a71b78d1989695  139  c102-hf09-ld-conf-d-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c102-hf09-ld-conf-d-sha256.err
d7c6740d4ae22c727652116f09bd6dc447f223246acb5e83e05e5bdd201d5f6d  196  c102-hf09-ld-conf-d-sha256.meta
eaaf02f80d280d1b3a9531bdc59df0a04c1b8af07b7392b9c231467e096bf25a  315  c102-hf09-ld-conf-d-sha256.out
b5bc37d91ee799e333e5c9a728a8933856e26d7c7f7d820b1b65a0af963a12b3  281  c103-hf10-stat-lstat.cmd
22d68a8520944d7010eac56df0797105bef64a6beac55918c2974361765933e9  80  c103-hf10-stat-lstat.err
0a27ecf172ed76f7ccf365ec066f6eb2feaad55f479e43168933a11bca9ecbb4  178  c103-hf10-stat-lstat.meta
eac49f8b4f78e5ba42f15b86e5a86f1a1e0a46e90124b7135a2de1683a829a37  951  c103-hf10-stat-lstat.out
361732c859dca044f78ab3f32abac1ac00bcda6a0b88ec28246a853f03f443b9  284  c104-hf10-stat-follow.cmd
22d68a8520944d7010eac56df0797105bef64a6beac55918c2974361765933e9  80  c104-hf10-stat-follow.err
35001c3aeeb3962b59783e99153dbd896d7387d51d026fce9637ccb84f78fd56  181  c104-hf10-stat-follow.meta
116d4f95661e63d6b2707f225320fafc51df6c3f47513c6e0e2eb70659e8ea73  947  c104-hf10-stat-follow.out
7bc59bc4415832af1f1dbdc0017296262d35aa16a66d7a7dd29971d36d0173ca  3078  c105-hf11-lstat-xattr.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c105-hf11-lstat-xattr.err
92e65cb55f36c61c5874cc79ca9f29767616a7437394edb98702e450005bdba7  181  c105-hf11-lstat-xattr.meta
4ea1d2b9d65818a2a304190df1aeb103f7e4d8e7643ec5a1858182663b3e48fe  2409  c105-hf11-lstat-xattr.out
7e29a9013c6ebe03ce42713df40784a0b8f76cb4bbb0910c6ba9703f8e472838  2313  c106-hf12-rules-dirs-stat.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c106-hf12-rules-dirs-stat.err
558d83d7ceb03860c219df1cf6daeddea5255c4ef02678d02f10ee9af1f20a80  193  c106-hf12-rules-dirs-stat.meta
6569249ca528545227e67d6143afe6c1d9a8eb4155de0cc6aeac8f9b5b68b77f  338  c106-hf12-rules-dirs-stat.out
73457862073a47cd721d930a380ae3dc9fdce53637b6441cb31d56a7feab31f5  2311  c107-hf12-rules-dirs-ls.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c107-hf12-rules-dirs-ls.err
8f83c35601acf073da86558d7e415bcd3a175b5e8f641142512e244ceb7f437b  187  c107-hf12-rules-dirs-ls.meta
8f299eedf9f46a1bdeb3d887030a0913c7d376b7aa5c5f3234806c3d147370e5  1692  c107-hf12-rules-dirs-ls.out
9c27b8d03c8d8abc995aeacbac5a845c30fb0a17116e1f2cd71a059ff30f7871  97  c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.err
7c72c6f1df0da46a16c4ad9f864b0cbd39ae4b0b02b5aa4e96d37fac36bd6d29  391  c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.meta
38d2376902ac5399871b4f8001fc7dcf2f28e41bec7db09d2797c111e1b91332  141  c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.out
4d093a0d257463ce8adcbae730a1039dde6f9e6ccba3609403714a79f5b01cb2  105  c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.err
a3c9f0cc22a618a0f3b1176a0bae362512a04d3459080b9250a1abfff85f311b  415  c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.meta
a9904a1f2e5f9c5a877a5da800858ed3f5439a6d601d1d5d0176c0a92f657aa3  149  c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.out
f882bbe5f98131f24ab305f7d582ec5e138a9dd31211c48c70bb6d3f39514a80  72  c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.err
826b1ded6fad84b1eb199278b5b485ea58a8bca8a5267a692ddfba6705f774ff  316  c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.meta
0490f18e5d20d4f33cbcbc43770c46b1c07ee5ab409e92d7ed7224576012ea2b  116  c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.out
d4481d7275bba27b39995ce2360105edca08bd6700c9e40091cb45d365e17bcb  67  c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.err
a6039ad0e57af6ecf0da0ef9683a9396d04d115d3fa0079566c6c0822bc8c3e7  301  c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.meta
d6b595fd5301cc6a84df9675581c068f39849bcd7651597efa66014794811503  111  c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.out
862c69badb9a4eb2a10408b7de570470a1a061e6970782525befcd9c0de8a9c1  64  c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.err
12a692860c4cfe9ae14eded99ed5fe30637bc6184b64a6d42e1bc0f9a75a1d05  292  c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.meta
a93150f5bc22921600032e7c444d0d318b82f53fe129aeaf2ee76feb90ca43e2  108  c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.out
968901fbe533187832cb2d473ee0967786af3125bfeec7e49ee22d41820a5cc1  77  c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.err
8a010764b959032edb655cb338b7ef4ba995c396ac00dfa26bbc578d6fedd7d2  331  c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.meta
75aadd8268440e6f20b9722aa86fca8a223e236ab75f4e1f3e3e8c083dfe7e6b  121  c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.out
07b80d4063c4e1a29bae6b2ac58c3053255e7a2ed1c37ae4505a0001a6e26a4c  78  c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.err
1058e97ed68bdcc7dc939948e4bc36fa4de5b5eb639b46e9c61d928b35cbe443  334  c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.meta
aaf3f24362d018caabb6f3a39e325263ea880c4b9e4ba26dac4ff5bfb089f5e6  122  c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.out
e2db30f5e0b89c89c4f088c5d81afc1c8773c1dc2823e672ed9a34238a027a8c  83  c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.err
f49e0b53c3f2b54dba01eff5b610c2f2ff453b12c9232c509a20643f68472c91  349  c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.meta
b4315e9145351497d9657355cc77b0ce3681856f113e0b2c4c4b28febc7b7d77  127  c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.out
ff23e92f47f5e9a9b226f256cd355e5b9822ed1c6183a02e0d42535b4f50cb9b  73  c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.err
6880b664fd0a7a8e2aef7143d2335489fd22b747950fd7854e4ac64ce5c4fb64  319  c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.meta
f4acaa897a59ff13e4d0ccb8ecadf9afb0099eacac2c13fd634a2c4689cfc27c  117  c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.out
0c2c2144e502d6993845781ce3e084cbd08af0526a4c52db788e906790f7ea88  107  c117-hf13-systemctl-show-unit.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c117-hf13-systemctl-show-unit.err
cc826690ad8dbb231a0d58cc9e2e9223a5aea5b977231f2ca4ac70c1d8c572f7  205  c117-hf13-systemctl-show-unit.meta
b647af8c9506dd4600eb6e6ae15e79245260c7c9da982a2adfcb50eba17c6b34  47  c117-hf13-systemctl-show-unit.out
e32381ae75d7083416df865627545d160698cc9e281a20e9c68f49503a8c311b  36  c118-hf13-unit-paths.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c118-hf13-unit-paths.err
86a2655a21e5cf3319f50248f7c0367ac87875867e7bf81c073e5883340e1280  178  c118-hf13-unit-paths.meta
7249fdf6aa1ae313a410e04efbad0f952414ca74894a4861659e837cca30b2a0  311  c118-hf13-unit-paths.out
e9fb5f81c387a818b5a7fe2349f208f80998b07a13492e3070062cb80032230d  3307  c119-hf13-dropin-dirs-ls.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c119-hf13-dropin-dirs-ls.err
94d17588afd15254aea38220a15db0604c74929c3a8364a34d384c66a43bde2b  190  c119-hf13-dropin-dirs-ls.meta
fa18c0cecf9b2ab7fb836cccee23c9c12955336ab7536f888c28ede1229133fd  1366  c119-hf13-dropin-dirs-ls.out
5ea86b5990755fad6329306b20e84aeeca1afe7815fe021d7a4af8a38df0a0a9  34  c120-hf14-hf15-proc-self-mountinfo.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c120-hf14-hf15-proc-self-mountinfo.err
67823ab624db578078b0e85ed9c47fa75c0e87b087afdc52fb9a72277470144a  226  c120-hf14-hf15-proc-self-mountinfo.meta
83aa08d25473d2ce0a36694579f50a826d2760e6c03756ec520b6a574ddbaafa  4005  c120-hf14-hf15-proc-self-mountinfo.out
43af7bc9c2d9c4c1fc5239156ebe7f16ecfc9252684d899097218602c034369e  2230  c121-hf14-binfmt-ls.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c121-hf14-binfmt-ls.err
eb548d820c7dab0dc1150a4c46db51501c8fa7d09ddf954823937c2fe78f29a7  175  c121-hf14-binfmt-ls.meta
8bb8393dcef5139769fc4c347c861cf90f4338d2230d74ca6e7db587ebfb44a5  440  c121-hf14-binfmt-ls.out
54fa52dde5013b05c2da548cf15924f3669c764c671bc7a2f66bbaf08a6d23ba  52  c122-hf14-read-python3.14.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c122-hf14-read-python3.14.err
108345b437796e018a37a255aabc13eb74a8a8d9f73e09c908247776b80b19b7  193  c122-hf14-read-python3.14.meta
56f6d188d45e1df44c1c83affeb389d2cb6f504a9535d5fc0b0604d2fa2d5b60  72  c122-hf14-read-python3.14.out
c2777792aac0f1a6831a76971c9730307ca6088a0f1ffeeb58eaa5060bfda87f  48  c123-hf14-read-status.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c123-hf14-read-status.err
7b48cf8b22bb695404701945eb179d480cd7c1e7d8987998874bc1279529392a  181  c123-hf14-read-status.meta
e056a35db086947e2f5969d747f0a7517bff00c7ffff1f9e7b47b72bfac9d948  8  c123-hf14-read-status.out
4b394f2483d3b25db2612488d4f125c1395a5fcd225c625c63ea2b5b8f5bcc80  63  c124-hf15-findmnt-_.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c124-hf15-findmnt-_.err
8027b9238cabd2ebb4b661081a2b3a635dfa95284df0a842c6b118ee2cb3d9ee  175  c124-hf15-findmnt-_.meta
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  104  c124-hf15-findmnt-_.out
ce499cc27d08469beca3fa479fd67cb59b7d3ec4217c184e23bf3e805ed83b66  98  c125-hf15-df-_.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c125-hf15-df-_.err
7c5164ff9a0e19a61cca8a87ba041149f5a05abb3c41003ea7a0c39aa0b6d88c  160  c125-hf15-df-_.meta
793ec0ccb5220e41c277671f51b0699fc021c4d688d0bf14465636489943fc00  163  c125-hf15-df-_.out
5dbe9610d310c4056184ce5fe9125a4b62eb89923ce21e8456b09fac08624b14  72  c126-hf15-findmnt-_usr_local.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c126-hf15-findmnt-_usr_local.err
bf4330ecb88c707c556f72982e01ca93faa6f1ef29aa80a4226ab252a9b9825b  202  c126-hf15-findmnt-_usr_local.meta
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  104  c126-hf15-findmnt-_usr_local.out
be510b43c9a71f33095318848a09b3dfc787f0c263cd00a7f2bd08b2d55b8d77  107  c127-hf15-df-_usr_local.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c127-hf15-df-_usr_local.err
eb70b6e93f73d6d36012cb4b5e27d35efa9304df44fe0865c8cdbb11d5e02f13  187  c127-hf15-df-_usr_local.meta
e01edd2c42e313178aacbc36e468969cea0af04fc27a419d63d4e253678194b2  163  c127-hf15-df-_usr_local.out
47764d0369001535b5fed6b27197d16c730f9e36a2d937e36016b000a615ed91  80  c128-hf15-findmnt-_usr_local_libexec.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c128-hf15-findmnt-_usr_local_libexec.err
d0adfb93f1cc40d2901e36ae07034977538ca467a2261d336b8c94e982cdc85b  226  c128-hf15-findmnt-_usr_local_libexec.meta
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  104  c128-hf15-findmnt-_usr_local_libexec.out
054f539ec08e2a680015871999ae2f5feb8e4d2bcbef50bd23233f20f4612113  115  c129-hf15-df-_usr_local_libexec.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c129-hf15-df-_usr_local_libexec.err
204d8b80f9263c49909f624b34eba46c381ddbc83c33f0cefa1e942f4c1964f0  211  c129-hf15-df-_usr_local_libexec.meta
920f5ec5bd896246da860094b4d28cfa5588b9b60f92399b72e43cfbf4c800d2  163  c129-hf15-df-_usr_local_libexec.out
2d1f84a1012c0b89937781f7e24bfbcb68f453f97594450d8f145845be79cdaa  66  c130-hf15-findmnt-_etc.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c130-hf15-findmnt-_etc.err
8460daf28642aeedcff576856dd5d49d750664bc21fe3b55f895f9219c7d7000  184  c130-hf15-findmnt-_etc.meta
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  104  c130-hf15-findmnt-_etc.out
06bcd36a068007c46803dc5ed361cb243dd7f31a3fd2a130845a606ef123fe3b  101  c131-hf15-df-_etc.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c131-hf15-df-_etc.err
667e74bf29c3afcd347a8d9d64a1c0a4588ca6453507385bfbca32295a1f3295  169  c131-hf15-df-_etc.meta
94a503472218a2d83510b9b77a6ebbf555f14b2137cc904b9263d3b2b66e7e82  163  c131-hf15-df-_etc.out
29808a69d5003040d6a8816b936386d6ae4c325dc6be4c705894ace721021520  81  c132-hf15-findmnt-_etc_systemd_system.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c132-hf15-findmnt-_etc_systemd_system.err
aa4b3f42f07212c82cc251166f4db11f90faa290ff0137f0ad2c6f2d9f8862e0  229  c132-hf15-findmnt-_etc_systemd_system.meta
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  104  c132-hf15-findmnt-_etc_systemd_system.out
75050be5187f5afb8f8a88ca788a44ad23af9a64d251ae3f98f6f0dae636bba9  116  c133-hf15-df-_etc_systemd_system.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c133-hf15-df-_etc_systemd_system.err
1dd780f64ecd6f522f99c7868366cf96649e6f8889c02f0324730c0865442056  214  c133-hf15-df-_etc_systemd_system.meta
9b8320f68503f7ce24fb1677d111f9093561dbf327210352008eafe86826a0d9  163  c133-hf15-df-_etc_systemd_system.out
a66156d244be496928f455ba908fe489e9f3f37c933184584e295cc08e817db5  83  c134-hf15-findmnt-_etc_polkit-1_rules.d.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c134-hf15-findmnt-_etc_polkit-1_rules.d.err
683ecdf462be62b065153f7f2914bf91d9b1b1845648a6d761b37d7ab6ba66a9  235  c134-hf15-findmnt-_etc_polkit-1_rules.d.meta
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  104  c134-hf15-findmnt-_etc_polkit-1_rules.d.out
64395a3d144c6ea789f2a6c74731bab97734ccc320f8db217c3cf6f935dadbcf  118  c135-hf15-df-_etc_polkit-1_rules.d.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c135-hf15-df-_etc_polkit-1_rules.d.err
65e8ee6d25cdc953744cae8532841cbcbd5ea1303e60ec9ff81158523994961e  220  c135-hf15-df-_etc_polkit-1_rules.d.meta
8b02154f0e240857535882e436c3c93340b74301bcd9094045d415d768f2204c  163  c135-hf15-df-_etc_polkit-1_rules.d.out
5a9da6a82a9102a8f956fb91237824a7f77c289f98e89f03faf5a98ba2b9b248  70  c136-hf15-findmnt-_var_lib.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c136-hf15-findmnt-_var_lib.err
0fefccbc316208444fbbcd19528c4e7865a69c59761d0ddf5f41d62e98e4da6d  196  c136-hf15-findmnt-_var_lib.meta
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  104  c136-hf15-findmnt-_var_lib.out
d00d0964d29392ce0927b6ce4d0a2f7dc3efe2cb8e059dbaff92bdcea5318b1e  105  c137-hf15-df-_var_lib.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c137-hf15-df-_var_lib.err
dff719e8d1cf26efd291e7bbb71f750f9f9cc57b3865d88974908a7a982bce2b  181  c137-hf15-df-_var_lib.meta
52880d461f1a6828356d07af96b02ea1926067fbf6c624f2332be6dee7fa2992  163  c137-hf15-df-_var_lib.out
9137d08068ad24787b4db3af8657f9977080a287dd723a0d047878df0314c688  70  c138-hf15-findmnt-_var_tmp.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c138-hf15-findmnt-_var_tmp.err
fe0cc0c2e40f13a31de5c0be6608d45829d139fb05af5e07ca1e7187ff12f7e0  196  c138-hf15-findmnt-_var_tmp.meta
bc42e0aa5693cc86b8257ad1e649ce00e23161e9336bfb4805c53778d0ab9cb8  104  c138-hf15-findmnt-_var_tmp.out
86c35c6fb4f19af8707b6627729144f1e09a9069170d752c7ee8c241905aadff  105  c139-hf15-df-_var_tmp.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c139-hf15-df-_var_tmp.err
d704530d4d02f803b2378a54dce1188ecc4610a5d9003c05fd7ad8e833065d67  181  c139-hf15-df-_var_tmp.meta
fde7e40bfcb985d1fc2aa4950825f96f5d3d81ea5c0e7d9403ef62c5c3f1f6c9  163  c139-hf15-df-_var_tmp.out
f2d9b336d6fc37074d137000308361c8d8f8b6d048759da5f76c5c7dd6db3d60  66  c140-hf15-findmnt-_run.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c140-hf15-findmnt-_run.err
3cb26ef410e9a0b79f6339f5be15b22205310b4dbaf00cf7976ffae943c911b2  184  c140-hf15-findmnt-_run.meta
49d01c38f7df053ea3a7b85edb08ecf6a971b96259ac46102318bc996f7b6530  113  c140-hf15-findmnt-_run.out
281cba75cf20c0822547d1fdda19e4535a06f6f58174a984db80f224daaa27ea  101  c141-hf15-df-_run.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c141-hf15-df-_run.err
7c76b43b6abcbdc78dc327c4d19dfa6a20969e6ad8bb545d9edc6fbc9b7e69db  169  c141-hf15-df-_run.meta
5974161445d89655191869a6663b676b011ea6c266a5830d43d98dba29091f59  154  c141-hf15-df-_run.out
763a9d45129e98a1fa378bcc5234b658ec38df711375cc50691f6fda4ac355b5  75  c142-hf15-findmnt-_run_polkit-1.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c142-hf15-findmnt-_run_polkit-1.err
e8274abe089462b9c7deaffe62de8924213d4590e17ee24792c0c5c278968f56  211  c142-hf15-findmnt-_run_polkit-1.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c142-hf15-findmnt-_run_polkit-1.out
a90c257b1470bee4d24ac1fc6fe5585e53e2b99f4fa2a2ed25d92d10ffa8562c  110  c143-hf15-df-_run_polkit-1.cmd
785adbbacca26c9266e4abc628aa8f0de1277f6449db884c022b00b5a756ea43  45  c143-hf15-df-_run_polkit-1.err
bb7eaa7a4bded3b30847f7cce81665bb72e832de7e8833dd7623a5894b22352b  196  c143-hf15-df-_run_polkit-1.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c143-hf15-df-_run_polkit-1.out
564fc19efe12350dfe649a2b260d52a240e3c0dfe102a61c82ed8249a4ab1bb3  1392  c144-hf16-manager-defaults.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c144-hf16-manager-defaults.err
2324e3f1b8f29c83e3ff663fbb153dad81aac2e678f776efc0a047a066050f43  196  c144-hf16-manager-defaults.meta
df99b68b89f33da131a83765beea45b7ed742d621bbdd50ab6ccaed4467bc423  1468  c144-hf16-manager-defaults.out
5ca8dde8cacf139e3739ee61ba9595509d1924a3c3dcbafd93cfbf6ce54e0a6a  60  c145-hf17-list-timers.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c145-hf17-list-timers.err
16cdf22e3e3984d9935309f9b634c29668f375bdfbd9ad483a173749f032225b  181  c145-hf17-list-timers.meta
22a327412a92503bc67d4a87a292043122cbac4e13f2e7f3d857367232f9b5ab  2577  c145-hf17-list-timers.out
d12e754c62ef88cc84931f7ef5e79582a9185e59c2bdfcc4d5e8ac72e411d679  166  c146-hf17-update-units-show.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c146-hf17-update-units-show.err
9eb424443c79f97ce0ce71d52459cfd7465e8e50cb0c61e2398fd6422bd2040c  199  c146-hf17-update-units-show.meta
2d6570cace9dfcd7b54ff10b2d48d93588e577612182ef99ff854b420f6264c8  304  c146-hf17-update-units-show.out
7bc5a5a780fa0af7c56c09fcf2a4a49ea651df6bc2da6ee3d84f3e6f0c0ebabc  2283  c147-hf19-tmpfiles-dirs-ls.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c147-hf19-tmpfiles-dirs-ls.err
2e004f9eeb297e68a168a227b1046dcf287210e7634b671f8246be303047363c  196  c147-hf19-tmpfiles-dirs-ls.meta
1f3fe39459e5d31131a3f9dde94e68d2b82ce64899006b000d1839e5bd3a26d9  6648  c147-hf19-tmpfiles-dirs-ls.out
d5030817efc6e1a81d31f8d2eb7f3e96566a471a399dadb1b41afb54793adc8f  51  c148-hf19-tmp-conf-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c148-hf19-tmp-conf-sha256.err
d03ffa407f6cfa34a7793dcc0ee273f6318b47306c71e1d72539db92fcfd196e  193  c148-hf19-tmp-conf-sha256.meta
07cf49dca2ebbb8f4fc7faef749c5a0de8e5e601b3b81db8989d2cd886dec4fc  95  c148-hf19-tmp-conf-sha256.out
84a2f86de1026ede82fe2c40d60af2ac5759474d19a2fbfe351e1fc40d83a43c  1716  c149-hf19-tmpfiles-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c149-hf19-tmpfiles-sha256.err
fae121e0df9e2e650ddd3e9c297b0538cb969dfcb3264da4dd9b786f79465587  193  c149-hf19-tmpfiles-sha256.meta
215a027d2d08a3c8e420675c07b00c2dcc1703f43b164c4a2a99d232500cfc38  4730  c149-hf19-tmpfiles-sha256.out
9df51d52bd016e648310710e7bf85e0b0d82c8a4741b14f0e1787df1f389f32a  1770  c150-hf19-tmpfiles-lines.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c150-hf19-tmpfiles-lines.err
64ac47347ffc0a4c346e488c9a45e63b75fa31870822aa53abddd17884ecceef  190  c150-hf19-tmpfiles-lines.meta
369676001abb688ff0bf4bd9995b95616326cf50da96327388e85ea8e9f4d0b2  280  c150-hf19-tmpfiles-lines.out
95611ffec36fb9369fc4b12fb66163216092642e965c84531e7216c0a9e834c4  101  c151-hf20-soft-reboot-loadstate.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c151-hf20-soft-reboot-loadstate.err
d1e6d73f526795fdcde15ee10a43520b3b165d149d875da47693d26d4d5c1083  211  c151-hf20-soft-reboot-loadstate.meta
3faf7dd8dd12149a39ef4c2695a065dcc41953db57572e80fe2643aeae7d4299  88  c151-hf20-soft-reboot-loadstate.out
ad4a2fc7308b43c1de95d8ab7c06bae8a3a7b10e7b9e065dadfbc8fa32745645  43068  controller-h0-program.sh

````

### `MANIFEST.final` (103 bytes)

````text
MANIFEST.payload  sha256=f116244f94ca3ea42e51b0d1c2ea3e0c99257cecfafc5b9c13bd7fb742724503  bytes=64132

````

### `INVENTORY.owner-mode` (61987 bytes)

````text
DIR	/var/tmp/p5-r5-rp11-h0-20261006-02-evidence	uid=1001	gid=1001	mode=0700
COMMANDS.index	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
EXCLUSIONS	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
HF-NOTES	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
INVENTORY.owner-mode	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes	own-output-open
MANIFEST.final	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
MANIFEST.payload	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
R5-authority.b64	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
R5-authority.md	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
R5-prompt.b64	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
R5-prompt.md	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
RUN-CONTEXT	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
RUN-END	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c001-program-sha256.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c001-program-sha256.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c001-program-sha256.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c001-program-sha256.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c002-program-stat.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c002-program-stat.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c002-program-stat.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c002-program-stat.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c003-id-ru.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c003-id-ru.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c003-id-ru.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c003-id-ru.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c004-id-u.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c004-id-u.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c004-id-u.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c004-id-u.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c005-id-un.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c005-id-un.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c005-id-un.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c005-id-un.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c006-id-run.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c006-id-run.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c006-id-run.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c006-id-run.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c007-hf01-uname-n.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c007-hf01-uname-n.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c007-hf01-uname-n.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c007-hf01-uname-n.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c008-hf02-machine-id-sha256.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c008-hf02-machine-id-sha256.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c008-hf02-machine-id-sha256.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c008-hf02-machine-id-sha256.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c009-py3-readlink.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c009-py3-readlink.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c009-py3-readlink.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c009-py3-readlink.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c010-py3-stat.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c010-py3-stat.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c010-py3-stat.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c010-py3-stat.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c011-py3-stat-L.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c011-py3-stat-L.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c011-py3-stat-L.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c011-py3-stat-L.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c012-py3-version.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c012-py3-version.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c012-py3-version.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c012-py3-version.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c013-paths-lstat-before-git.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c013-paths-lstat-before-git.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c013-paths-lstat-before-git.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c013-paths-lstat-before-git.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c014-git-version.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c014-git-version.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c014-git-version.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c014-git-version.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c015-git-init.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c015-git-init.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c015-git-init.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c015-git-init.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c016-git-fetch.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c016-git-fetch.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c016-git-fetch.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c016-git-fetch.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c017-git-cat-file-type.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c017-git-cat-file-type.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c017-git-cat-file-type.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c017-git-cat-file-type.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c018-git-rev-parse-pin.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c018-git-rev-parse-pin.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c018-git-rev-parse-pin.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c018-git-rev-parse-pin.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c019-git-commit-header.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c019-git-commit-header.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c019-git-commit-header.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c019-git-commit-header.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c020-git-checkout-detach.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c020-git-checkout-detach.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c020-git-checkout-detach.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c020-git-checkout-detach.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c021-git-rev-parse-head.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c021-git-rev-parse-head.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c021-git-rev-parse-head.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c021-git-rev-parse-head.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c022-git-status-porcelain.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c022-git-status-porcelain.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c022-git-status-porcelain.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c022-git-status-porcelain.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c023-git-symbolic-ref.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c023-git-symbolic-ref.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c023-git-symbolic-ref.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c023-git-symbolic-ref.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c024-git-remote-list.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c024-git-remote-list.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c024-git-remote-list.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c024-git-remote-list.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c025-git-local-config.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c025-git-local-config.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c025-git-local-config.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c025-git-local-config.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c026-gov-sha256.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c026-gov-sha256.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c026-gov-sha256.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c026-gov-sha256.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c027-gov-acceptance-decision.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c027-gov-acceptance-decision.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c027-gov-acceptance-decision.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c027-gov-acceptance-decision.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c028-gov-proposal-hf-sections.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c028-gov-proposal-hf-sections.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c028-gov-proposal-hf-sections.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c028-gov-proposal-hf-sections.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c029-r5-prompt-decode.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c029-r5-prompt-decode.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c029-r5-prompt-decode.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c030-r5-authority-decode.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c030-r5-authority-decode.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c030-r5-authority-decode.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c031-r5-copies-sha256.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c031-r5-copies-sha256.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c031-r5-copies-sha256.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c031-r5-copies-sha256.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c032-r5-copies-stat.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c032-r5-copies-stat.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c032-r5-copies-stat.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c032-r5-copies-stat.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c033-hf03-id-ubuntu.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c033-hf03-id-ubuntu.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c033-hf03-id-ubuntu.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c033-hf03-id-ubuntu.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c034-hf03-id-Gn-ubuntu.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c034-hf03-id-Gn-ubuntu.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c034-hf03-id-Gn-ubuntu.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c034-hf03-id-Gn-ubuntu.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c035-hf03-getent-passwd.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c035-hf03-getent-passwd.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c035-hf03-getent-passwd.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c035-hf03-getent-passwd.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c036-hf03-getent-group-ubuntu.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c036-hf03-getent-group-ubuntu.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c036-hf03-getent-group-ubuntu.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c036-hf03-getent-group-ubuntu.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c037-hf03-getent-group-adm.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c037-hf03-getent-group-adm.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c037-hf03-getent-group-adm.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c037-hf03-getent-group-adm.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c038-hf03-getent-group-cdrom.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c038-hf03-getent-group-cdrom.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c038-hf03-getent-group-cdrom.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c038-hf03-getent-group-cdrom.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c039-hf03-getent-group-sudo.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c039-hf03-getent-group-sudo.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c039-hf03-getent-group-sudo.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c039-hf03-getent-group-sudo.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c040-hf03-getent-group-dip.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c040-hf03-getent-group-dip.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c040-hf03-getent-group-dip.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c040-hf03-getent-group-dip.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c041-hf03-getent-group-lxd.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c041-hf03-getent-group-lxd.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c041-hf03-getent-group-lxd.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c041-hf03-getent-group-lxd.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c042-hf03-getent-group-freedomlab.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c042-hf03-getent-group-freedomlab.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c042-hf03-getent-group-freedomlab.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c042-hf03-getent-group-freedomlab.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c043-hf04-uname-mrv.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c043-hf04-uname-mrv.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c043-hf04-uname-mrv.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c043-hf04-uname-mrv.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c044-hf05-proc1-comm.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c044-hf05-proc1-comm.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c044-hf05-proc1-comm.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c044-hf05-proc1-comm.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c045-hf05-hf06-systemctl-version.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c045-hf05-hf06-systemctl-version.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c045-hf05-hf06-systemctl-version.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c045-hf05-hf06-systemctl-version.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c046-hf07-dpkg-query-systemd.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c046-hf07-dpkg-query-systemd.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c046-hf07-dpkg-query-systemd.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c046-hf07-dpkg-query-systemd.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c047-hf07-dpkg-query-systemd-sysv.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c047-hf07-dpkg-query-systemd-sysv.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c047-hf07-dpkg-query-systemd-sysv.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c047-hf07-dpkg-query-systemd-sysv.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c048-hf07-dpkg-query-libsystemd0.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c048-hf07-dpkg-query-libsystemd0.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c048-hf07-dpkg-query-libsystemd0.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c048-hf07-dpkg-query-libsystemd0.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c049-hf07-dpkg-query-libsystemd-shared.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c049-hf07-dpkg-query-libsystemd-shared.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c049-hf07-dpkg-query-libsystemd-shared.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c049-hf07-dpkg-query-libsystemd-shared.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c050-hf07-dpkg-query-polkitd.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c050-hf07-dpkg-query-polkitd.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c050-hf07-dpkg-query-polkitd.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c050-hf07-dpkg-query-polkitd.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c051-hf07-dpkg-query-libpolkit-gobject-1-0.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c051-hf07-dpkg-query-libpolkit-gobject-1-0.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c051-hf07-dpkg-query-libpolkit-gobject-1-0.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c051-hf07-dpkg-query-libpolkit-gobject-1-0.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c052-hf07-dpkg-query-libc6.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c052-hf07-dpkg-query-libc6.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c052-hf07-dpkg-query-libc6.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c052-hf07-dpkg-query-libc6.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c053-hf07-dpkg-query-libc-bin.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c053-hf07-dpkg-query-libc-bin.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c053-hf07-dpkg-query-libc-bin.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c053-hf07-dpkg-query-libc-bin.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c054-hf07-dpkg-query-python3.12.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c054-hf07-dpkg-query-python3.12.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c054-hf07-dpkg-query-python3.12.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c054-hf07-dpkg-query-python3.12.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c055-hf07-dpkg-query-python3.12-minimal.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c055-hf07-dpkg-query-python3.12-minimal.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c055-hf07-dpkg-query-python3.12-minimal.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c055-hf07-dpkg-query-python3.12-minimal.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c056-hf07-dpkg-query-libpython3.12-minimal.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c056-hf07-dpkg-query-libpython3.12-minimal.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c056-hf07-dpkg-query-libpython3.12-minimal.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c056-hf07-dpkg-query-libpython3.12-minimal.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c057-hf07-dpkg-query-libpython3.12-stdlib.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c057-hf07-dpkg-query-libpython3.12-stdlib.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c057-hf07-dpkg-query-libpython3.12-stdlib.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c057-hf07-dpkg-query-libpython3.12-stdlib.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c058-hf07-dpkg-query-coreutils.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c058-hf07-dpkg-query-coreutils.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c058-hf07-dpkg-query-coreutils.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c058-hf07-dpkg-query-coreutils.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c059-hf07-dpkg-query-util-linux.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c059-hf07-dpkg-query-util-linux.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c059-hf07-dpkg-query-util-linux.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c059-hf07-dpkg-query-util-linux.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c060-hf07-dpkg-query-sudo.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c060-hf07-dpkg-query-sudo.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c060-hf07-dpkg-query-sudo.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c060-hf07-dpkg-query-sudo.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c061-hf07-dpkg-query-dbus.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c061-hf07-dpkg-query-dbus.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c061-hf07-dpkg-query-dbus.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c061-hf07-dpkg-query-dbus.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c062-hf09-ld-readlink.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c062-hf09-ld-readlink.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c062-hf09-ld-readlink.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c062-hf09-ld-readlink.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c063-hf07-dpkg-S-_usr_bin_python3.12.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c063-hf07-dpkg-S-_usr_bin_python3.12.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c063-hf07-dpkg-S-_usr_bin_python3.12.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c063-hf07-dpkg-S-_usr_bin_python3.12.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c067-hf07-dpkg-S-_usr_bin_pkcheck.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c067-hf07-dpkg-S-_usr_bin_pkcheck.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c067-hf07-dpkg-S-_usr_bin_pkcheck.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c067-hf07-dpkg-S-_usr_bin_pkcheck.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c068-hf07-dpkg-S-_usr_bin_python3.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c068-hf07-dpkg-S-_usr_bin_python3.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c068-hf07-dpkg-S-_usr_bin_python3.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c068-hf07-dpkg-S-_usr_bin_python3.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c069-hf07-dpkg-S-_usr_bin_python3.14.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c069-hf07-dpkg-S-_usr_bin_python3.14.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c069-hf07-dpkg-S-_usr_bin_python3.14.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c069-hf07-dpkg-S-_usr_bin_python3.14.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c071-hf07-dpkg-query-python3-minimal.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c071-hf07-dpkg-query-python3-minimal.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c071-hf07-dpkg-query-python3-minimal.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c071-hf07-dpkg-query-python3-minimal.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c072-hf07-dpkg-query-python3.14-minimal.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c072-hf07-dpkg-query-python3.14-minimal.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c072-hf07-dpkg-query-python3.14-minimal.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c072-hf07-dpkg-query-python3.14-minimal.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c073-hf07-dpkg-verify-systemd.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c073-hf07-dpkg-verify-systemd.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c073-hf07-dpkg-verify-systemd.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c073-hf07-dpkg-verify-systemd.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c074-hf07-dpkg-verify-systemd-sysv.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c074-hf07-dpkg-verify-systemd-sysv.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c074-hf07-dpkg-verify-systemd-sysv.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c074-hf07-dpkg-verify-systemd-sysv.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c075-hf07-dpkg-verify-libsystemd0.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c075-hf07-dpkg-verify-libsystemd0.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c075-hf07-dpkg-verify-libsystemd0.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c075-hf07-dpkg-verify-libsystemd0.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c076-hf07-dpkg-verify-libsystemd-shared.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c076-hf07-dpkg-verify-libsystemd-shared.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c076-hf07-dpkg-verify-libsystemd-shared.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c076-hf07-dpkg-verify-libsystemd-shared.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c077-hf07-dpkg-verify-polkitd.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c077-hf07-dpkg-verify-polkitd.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c077-hf07-dpkg-verify-polkitd.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c077-hf07-dpkg-verify-polkitd.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c078-hf07-dpkg-verify-libpolkit-gobject-1-0.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c078-hf07-dpkg-verify-libpolkit-gobject-1-0.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c078-hf07-dpkg-verify-libpolkit-gobject-1-0.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c078-hf07-dpkg-verify-libpolkit-gobject-1-0.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c079-hf07-dpkg-verify-libc6.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c079-hf07-dpkg-verify-libc6.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c079-hf07-dpkg-verify-libc6.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c079-hf07-dpkg-verify-libc6.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c080-hf07-dpkg-verify-libc-bin.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c080-hf07-dpkg-verify-libc-bin.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c080-hf07-dpkg-verify-libc-bin.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c080-hf07-dpkg-verify-libc-bin.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c081-hf07-dpkg-verify-python3.12.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c081-hf07-dpkg-verify-python3.12.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c081-hf07-dpkg-verify-python3.12.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c081-hf07-dpkg-verify-python3.12.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c082-hf07-dpkg-verify-python3.12-minimal.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c082-hf07-dpkg-verify-python3.12-minimal.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c082-hf07-dpkg-verify-python3.12-minimal.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c082-hf07-dpkg-verify-python3.12-minimal.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c083-hf07-dpkg-verify-libpython3.12-minimal.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c083-hf07-dpkg-verify-libpython3.12-minimal.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c083-hf07-dpkg-verify-libpython3.12-minimal.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c083-hf07-dpkg-verify-libpython3.12-minimal.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c084-hf07-dpkg-verify-libpython3.12-stdlib.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c084-hf07-dpkg-verify-libpython3.12-stdlib.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c084-hf07-dpkg-verify-libpython3.12-stdlib.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c084-hf07-dpkg-verify-libpython3.12-stdlib.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c085-hf07-dpkg-verify-coreutils.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c085-hf07-dpkg-verify-coreutils.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c085-hf07-dpkg-verify-coreutils.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c085-hf07-dpkg-verify-coreutils.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c086-hf07-dpkg-verify-util-linux.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c086-hf07-dpkg-verify-util-linux.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c086-hf07-dpkg-verify-util-linux.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c086-hf07-dpkg-verify-util-linux.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c087-hf07-dpkg-verify-sudo.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c087-hf07-dpkg-verify-sudo.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c087-hf07-dpkg-verify-sudo.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c087-hf07-dpkg-verify-sudo.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c088-hf07-dpkg-verify-dbus.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c088-hf07-dpkg-verify-dbus.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c088-hf07-dpkg-verify-dbus.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c088-hf07-dpkg-verify-dbus.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c089-hf07-dpkg-verify-python3-minimal.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c089-hf07-dpkg-verify-python3-minimal.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c089-hf07-dpkg-verify-python3-minimal.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c089-hf07-dpkg-verify-python3-minimal.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c090-hf07-dpkg-verify-python3.14-minimal.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c090-hf07-dpkg-verify-python3.14-minimal.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c090-hf07-dpkg-verify-python3.14-minimal.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c090-hf07-dpkg-verify-python3.14-minimal.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c091-hf07-apt-cache-policy.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c091-hf07-apt-cache-policy.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c091-hf07-apt-cache-policy.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c091-hf07-apt-cache-policy.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c092-hf08-stat-python312.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c092-hf08-stat-python312.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c092-hf08-stat-python312.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c092-hf08-stat-python312.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c093-hf08-readlink-python312.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c093-hf08-readlink-python312.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c093-hf08-readlink-python312.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c093-hf08-readlink-python312.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c094-hf08-sha256-python312.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c094-hf08-sha256-python312.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c094-hf08-sha256-python312.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c094-hf08-sha256-python312.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c095-hf08-version-python312.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c095-hf08-version-python312.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c095-hf08-version-python312.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c095-hf08-version-python312.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c096-hf08-sha256-python3-real.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c096-hf08-sha256-python3-real.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c096-hf08-sha256-python3-real.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c096-hf08-sha256-python3-real.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c097-hf08-stat-python3-real.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c097-hf08-stat-python3-real.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c097-hf08-stat-python3-real.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c097-hf08-stat-python3-real.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c098-hf09-ld-stat.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c098-hf09-ld-stat.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c098-hf09-ld-stat.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c098-hf09-ld-stat.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c099-hf09-ld-sha256.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c099-hf09-ld-sha256.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c099-hf09-ld-sha256.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c099-hf09-ld-sha256.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c100-hf09-ld-preload-lstat.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c100-hf09-ld-preload-lstat.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c100-hf09-ld-preload-lstat.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c100-hf09-ld-preload-lstat.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c101-hf09-ld-conf-d-ls.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c101-hf09-ld-conf-d-ls.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c101-hf09-ld-conf-d-ls.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c101-hf09-ld-conf-d-ls.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c102-hf09-ld-conf-d-sha256.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c102-hf09-ld-conf-d-sha256.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c102-hf09-ld-conf-d-sha256.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c102-hf09-ld-conf-d-sha256.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c103-hf10-stat-lstat.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c103-hf10-stat-lstat.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c103-hf10-stat-lstat.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c103-hf10-stat-lstat.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c104-hf10-stat-follow.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c104-hf10-stat-follow.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c104-hf10-stat-follow.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c104-hf10-stat-follow.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c105-hf11-lstat-xattr.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c105-hf11-lstat-xattr.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c105-hf11-lstat-xattr.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c105-hf11-lstat-xattr.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c106-hf12-rules-dirs-stat.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c106-hf12-rules-dirs-stat.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c106-hf12-rules-dirs-stat.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c106-hf12-rules-dirs-stat.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c107-hf12-rules-dirs-ls.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c107-hf12-rules-dirs-ls.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c107-hf12-rules-dirs-ls.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c107-hf12-rules-dirs-ls.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c117-hf13-systemctl-show-unit.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c117-hf13-systemctl-show-unit.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c117-hf13-systemctl-show-unit.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c117-hf13-systemctl-show-unit.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c118-hf13-unit-paths.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c118-hf13-unit-paths.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c118-hf13-unit-paths.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c118-hf13-unit-paths.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c119-hf13-dropin-dirs-ls.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c119-hf13-dropin-dirs-ls.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c119-hf13-dropin-dirs-ls.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c119-hf13-dropin-dirs-ls.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c120-hf14-hf15-proc-self-mountinfo.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c120-hf14-hf15-proc-self-mountinfo.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c120-hf14-hf15-proc-self-mountinfo.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c120-hf14-hf15-proc-self-mountinfo.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c121-hf14-binfmt-ls.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c121-hf14-binfmt-ls.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c121-hf14-binfmt-ls.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c121-hf14-binfmt-ls.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c122-hf14-read-python3.14.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c122-hf14-read-python3.14.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c122-hf14-read-python3.14.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c122-hf14-read-python3.14.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c123-hf14-read-status.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c123-hf14-read-status.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c123-hf14-read-status.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c123-hf14-read-status.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c124-hf15-findmnt-_.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c124-hf15-findmnt-_.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c124-hf15-findmnt-_.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c124-hf15-findmnt-_.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c125-hf15-df-_.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c125-hf15-df-_.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c125-hf15-df-_.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c125-hf15-df-_.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c126-hf15-findmnt-_usr_local.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c126-hf15-findmnt-_usr_local.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c126-hf15-findmnt-_usr_local.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c126-hf15-findmnt-_usr_local.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c127-hf15-df-_usr_local.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c127-hf15-df-_usr_local.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c127-hf15-df-_usr_local.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c127-hf15-df-_usr_local.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c128-hf15-findmnt-_usr_local_libexec.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c128-hf15-findmnt-_usr_local_libexec.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c128-hf15-findmnt-_usr_local_libexec.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c128-hf15-findmnt-_usr_local_libexec.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c129-hf15-df-_usr_local_libexec.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c129-hf15-df-_usr_local_libexec.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c129-hf15-df-_usr_local_libexec.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c129-hf15-df-_usr_local_libexec.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c130-hf15-findmnt-_etc.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c130-hf15-findmnt-_etc.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c130-hf15-findmnt-_etc.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c130-hf15-findmnt-_etc.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c131-hf15-df-_etc.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c131-hf15-df-_etc.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c131-hf15-df-_etc.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c131-hf15-df-_etc.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c132-hf15-findmnt-_etc_systemd_system.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c132-hf15-findmnt-_etc_systemd_system.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c132-hf15-findmnt-_etc_systemd_system.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c132-hf15-findmnt-_etc_systemd_system.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c133-hf15-df-_etc_systemd_system.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c133-hf15-df-_etc_systemd_system.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c133-hf15-df-_etc_systemd_system.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c133-hf15-df-_etc_systemd_system.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c134-hf15-findmnt-_etc_polkit-1_rules.d.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c134-hf15-findmnt-_etc_polkit-1_rules.d.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c134-hf15-findmnt-_etc_polkit-1_rules.d.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c134-hf15-findmnt-_etc_polkit-1_rules.d.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c135-hf15-df-_etc_polkit-1_rules.d.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c135-hf15-df-_etc_polkit-1_rules.d.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c135-hf15-df-_etc_polkit-1_rules.d.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c135-hf15-df-_etc_polkit-1_rules.d.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c136-hf15-findmnt-_var_lib.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c136-hf15-findmnt-_var_lib.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c136-hf15-findmnt-_var_lib.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c136-hf15-findmnt-_var_lib.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c137-hf15-df-_var_lib.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c137-hf15-df-_var_lib.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c137-hf15-df-_var_lib.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c137-hf15-df-_var_lib.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c138-hf15-findmnt-_var_tmp.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c138-hf15-findmnt-_var_tmp.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c138-hf15-findmnt-_var_tmp.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c138-hf15-findmnt-_var_tmp.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c139-hf15-df-_var_tmp.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c139-hf15-df-_var_tmp.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c139-hf15-df-_var_tmp.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c139-hf15-df-_var_tmp.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c140-hf15-findmnt-_run.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c140-hf15-findmnt-_run.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c140-hf15-findmnt-_run.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c140-hf15-findmnt-_run.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c141-hf15-df-_run.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c141-hf15-df-_run.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c141-hf15-df-_run.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c141-hf15-df-_run.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c142-hf15-findmnt-_run_polkit-1.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c142-hf15-findmnt-_run_polkit-1.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c142-hf15-findmnt-_run_polkit-1.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c142-hf15-findmnt-_run_polkit-1.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c143-hf15-df-_run_polkit-1.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c143-hf15-df-_run_polkit-1.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c143-hf15-df-_run_polkit-1.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c143-hf15-df-_run_polkit-1.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c144-hf16-manager-defaults.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c144-hf16-manager-defaults.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c144-hf16-manager-defaults.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c144-hf16-manager-defaults.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c145-hf17-list-timers.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c145-hf17-list-timers.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c145-hf17-list-timers.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c145-hf17-list-timers.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c146-hf17-update-units-show.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c146-hf17-update-units-show.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c146-hf17-update-units-show.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c146-hf17-update-units-show.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c147-hf19-tmpfiles-dirs-ls.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c147-hf19-tmpfiles-dirs-ls.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c147-hf19-tmpfiles-dirs-ls.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c147-hf19-tmpfiles-dirs-ls.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c148-hf19-tmp-conf-sha256.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c148-hf19-tmp-conf-sha256.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c148-hf19-tmp-conf-sha256.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c148-hf19-tmp-conf-sha256.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c149-hf19-tmpfiles-sha256.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c149-hf19-tmpfiles-sha256.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c149-hf19-tmpfiles-sha256.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c149-hf19-tmpfiles-sha256.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c150-hf19-tmpfiles-lines.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c150-hf19-tmpfiles-lines.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c150-hf19-tmpfiles-lines.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c150-hf19-tmpfiles-lines.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c151-hf20-soft-reboot-loadstate.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c151-hf20-soft-reboot-loadstate.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c151-hf20-soft-reboot-loadstate.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c151-hf20-soft-reboot-loadstate.out	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c152-manifest-payload.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c152-manifest-payload.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c152-manifest-payload.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c153-manifest-final.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c153-manifest-final.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c153-manifest-final.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c154-inventory.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c154-inventory.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
controller-h0-program.sh	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
violations=0

````


## Appendix B — verbatim command records (`.cmd`, stdout, `.err`) c001–c154

Each record gives the exact `.cmd` text, then stdout, then `.err`. Payload
`.meta` files hold the same fields as their `COMMANDS.index` line, plus the
stdout and stderr file names, and are not reproduced. The closing `.meta`
files are reproduced above. The stdout files of c029 and c030 are
`R5-prompt.md` and `R5-authority.md`, which are byte-identical to the repository files
named at the top and are not reproduced. The stdout files of c152–c154 are
the closing files in Appendix A.

### `c001-program-sha256`

`c001-program-sha256.cmd` (91 bytes)

````text
/usr/bin/sha256sum -- /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/controller-h0-program.sh

````

`c001-program-sha256.out` (135 bytes)

````text
ad4a2fc7308b43c1de95d8ab7c06bae8a3a7b10e7b9e065dadfbc8fa32745645  /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/controller-h0-program.sh

````

`c001-program-sha256.err` (0 bytes)

### `c002-program-stat`

`c002-program-stat.cmd` (128 bytes)

````text
/usr/bin/stat -c size=%s\ owner=%U:%G\ mode=%a\ type=%F -- /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/controller-h0-program.sh

````

`c002-program-stat.out` (58 bytes)

````text
size=43068 owner=ubuntu:ubuntu mode=600 type=regular file

````

`c002-program-stat.err` (0 bytes)

### `c003-id-ru`

`c003-id-ru.cmd` (16 bytes)

````text
/usr/bin/id -ru

````

`c003-id-ru.out` (5 bytes)

````text
1001

````

`c003-id-ru.err` (0 bytes)

### `c004-id-u`

`c004-id-u.cmd` (15 bytes)

````text
/usr/bin/id -u

````

`c004-id-u.out` (5 bytes)

````text
1001

````

`c004-id-u.err` (0 bytes)

### `c005-id-un`

`c005-id-un.cmd` (16 bytes)

````text
/usr/bin/id -un

````

`c005-id-un.out` (7 bytes)

````text
ubuntu

````

`c005-id-un.err` (0 bytes)

### `c006-id-run`

`c006-id-run.cmd` (17 bytes)

````text
/usr/bin/id -run

````

`c006-id-run.out` (7 bytes)

````text
ubuntu

````

`c006-id-run.err` (0 bytes)

### `c007-hf01-uname-n`

`c007-hf01-uname-n.cmd` (18 bytes)

````text
/usr/bin/uname -n

````

`c007-hf01-uname-n.out` (5 bytes)

````text
Test

````

`c007-hf01-uname-n.err` (0 bytes)

### `c008-hf02-machine-id-sha256`

`c008-hf02-machine-id-sha256.cmd` (35 bytes)

````text
/usr/bin/sha256sum /etc/machine-id

````

`c008-hf02-machine-id-sha256.out` (82 bytes)

````text
e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d  /etc/machine-id

````

`c008-hf02-machine-id-sha256.err` (0 bytes)

### `c009-py3-readlink`

`c009-py3-readlink.cmd` (41 bytes)

````text
/usr/bin/readlink -f -- /usr/bin/python3

````

`c009-py3-readlink.out` (20 bytes)

````text
/usr/bin/python3.14

````

`c009-py3-readlink.err` (0 bytes)

### `c010-py3-stat`

`c010-py3-stat.cmd` (76 bytes)

````text
/usr/bin/stat -c name=%n\ type=%F\ owner=%U:%G\ mode=%a -- /usr/bin/python3

````

`c010-py3-stat.out` (66 bytes)

````text
name=/usr/bin/python3 type=symbolic link owner=root:root mode=777

````

`c010-py3-stat.err` (0 bytes)

### `c011-py3-stat-L`

`c011-py3-stat-L.cmd` (88 bytes)

````text
/usr/bin/stat -L -c name=%n\ type=%F\ owner=%U:%G\ mode=%a\ size=%s -- /usr/bin/python3

````

`c011-py3-stat-L.out` (78 bytes)

````text
name=/usr/bin/python3 type=regular file owner=root:root mode=755 size=7468968

````

`c011-py3-stat-L.err` (0 bytes)

### `c012-py3-version`

`c012-py3-version.cmd` (405 bytes)

````text
/usr/bin/python3 -I -S -c $'import sys\nprint("version=" + sys.version.replace("\\n", " "))\nprint("version_info=" + ".".join(str(x) for x in sys.version_info[:3]))\nprint("major=" + str(sys.version_info[0]))\nprint("isolated=" + str(sys.flags.isolated))\nprint("no_site=" + str(sys.flags.no_site))\nprint("executable=" + sys.executable)\nprint("prefix=" + sys.prefix)\nprint("path=" + repr(sys.path))\n'

````

`c012-py3-version.out` (237 bytes)

````text
version=3.14.4 (main, Aug 20 2026, 10:41:58) [GCC 15.2.0]
version_info=3.14.4
major=3
isolated=1
no_site=1
executable=/usr/bin/python3
prefix=/usr
path=['/usr/lib/python314.zip', '/usr/lib/python3.14', '/usr/lib/python3.14/lib-dynload']

````

`c012-py3-version.err` (0 bytes)

### `c013-paths-lstat-before-git`

`c013-paths-lstat-before-git.cmd` (2295 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' stat /var/tmp/p5-r5-rp11-h0-20261006-02-evidence /var/tmp/p5-r5-rp11-h0-20261006-02-checkout

````

`c013-paths-lstat-before-git.out` (214 bytes)

````text
/var/tmp/p5-r5-rp11-h0-20261006-02-evidence	present	dir	uid=1001	gid=1001	owner=ubuntu	group=ubuntu	mode=0700	dev=2049	ino=1766009	nlink=2	size=4096	xattr_names=-
/var/tmp/p5-r5-rp11-h0-20261006-02-checkout	absent

````

`c013-paths-lstat-before-git.err` (0 bytes)

### `c014-git-version`

`c014-git-version.cmd` (280 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git --version

````

`c014-git-version.out` (19 bytes)

````text
git version 2.53.0

````

`c014-git-version.err` (0 bytes)

### `c015-git-init`

`c015-git-init.cmd` (752 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false -c init.defaultBranch=h0-unborn init --quiet --template= -- /var/tmp/p5-r5-rp11-h0-20261006-02-checkout

````

`c015-git-init.out` (0 bytes)

`c015-git-init.err` (0 bytes)

### `c016-git-fetch`

`c016-git-fetch.cmd` (868 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/timeout 900 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false fetch --no-tags --depth=1 --no-recurse-submodules -- https://github.com/ming-themerciless/freedom-platform.git 46d1c35a029ca8287779ae87d08a370ba0a0f2ef

````

`c016-git-fetch.out` (0 bytes)

`c016-git-fetch.err` (135 bytes)

````text
From https://github.com/ming-themerciless/freedom-platform
 * branch            46d1c35a029ca8287779ae87d08a370ba0a0f2ef -> FETCH_HEAD

````

### `c017-git-cat-file-type`

`c017-git-cat-file-type.cmd` (748 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false cat-file -t 46d1c35a029ca8287779ae87d08a370ba0a0f2ef

````

`c017-git-cat-file-type.out` (7 bytes)

````text
commit

````

`c017-git-cat-file-type.err` (0 bytes)

### `c018-git-rev-parse-pin`

`c018-git-rev-parse-pin.cmd` (784 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false rev-parse --verify --end-of-options 46d1c35a029ca8287779ae87d08a370ba0a0f2ef\^\{commit\}

````

`c018-git-rev-parse-pin.out` (41 bytes)

````text
46d1c35a029ca8287779ae87d08a370ba0a0f2ef

````

`c018-git-rev-parse-pin.err` (0 bytes)

### `c019-git-commit-header`

`c019-git-commit-header.cmd` (748 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false cat-file -p 46d1c35a029ca8287779ae87d08a370ba0a0f2ef

````

`c019-git-commit-header.out` (326 bytes)

````text
tree 56ccab51963de051d67426be8c560d69c8f3638c
parent 236872647f3edd5fed5c7f14512518e13eeb8f07
author Ming the Merciless <pduscha@gmail.com> 1791162361 +0000
committer Ming the Merciless <pduscha@gmail.com> 1791162361 +0000

docs: add project review, handover, topology, and remediation records for phase 5 H-1 one-host design

````

`c019-git-commit-header.err` (0 bytes)

### `c020-git-checkout-detach`

`c020-git-checkout-detach.cmd` (754 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false checkout --detach 46d1c35a029ca8287779ae87d08a370ba0a0f2ef

````

`c020-git-checkout-detach.out` (0 bytes)

`c020-git-checkout-detach.err` (125 bytes)

````text
HEAD is now at 46d1c35 docs: add project review, handover, topology, and remediation records for phase 5 H-1 one-host design

````

### `c021-git-rev-parse-head`

`c021-git-rev-parse-head.cmd` (710 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false rev-parse HEAD

````

`c021-git-rev-parse-head.out` (41 bytes)

````text
46d1c35a029ca8287779ae87d08a370ba0a0f2ef

````

`c021-git-rev-parse-head.err` (0 bytes)

### `c022-git-status-porcelain`

`c022-git-status-porcelain.cmd` (739 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false status --porcelain=v1 --untracked-files=all

````

`c022-git-status-porcelain.out` (0 bytes)

`c022-git-status-porcelain.err` (0 bytes)

### `c023-git-symbolic-ref`

`c023-git-symbolic-ref.cmd` (716 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false symbolic-ref -q HEAD

````

`c023-git-symbolic-ref.out` (0 bytes)

`c023-git-symbolic-ref.err` (0 bytes)

### `c024-git-remote-list`

`c024-git-remote-list.cmd` (705 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false remote -v

````

`c024-git-remote-list.out` (0 bytes)

`c024-git-remote-list.err` (0 bytes)

### `c025-git-local-config`

`c025-git-local-config.cmd` (717 bytes)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-02-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false config --local --list

````

`c025-git-local-config.out` (93 bytes)

````text
core.repositoryformatversion=0
core.filemode=true
core.bare=false
core.logallrefupdates=true

````

`c025-git-local-config.err` (0 bytes)

### `c026-gov-sha256`

`c026-gov-sha256.cmd` (427 bytes)

````text
/usr/bin/sha256sum -- /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/.agents/AGENTS.md /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/docs/implementation-plan.md /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md

````

`c026-gov-sha256.out` (669 bytes)

````text
ca907aa7fc2a7dd70e424fe40ec0ad4d42f625e972500190a358f57e70c9f39e  /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/.agents/AGENTS.md
07936a42ec645f2a997f5425ee68d7fd0fed92cfef8c088daf76b8831f24a1c9  /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/docs/implementation-plan.md
a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02  /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md
afe1f2256259244f207c87a1244be5455ad18aebc6ac9a86db400fc105f729f5  /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md

````

`c026-gov-sha256.err` (0 bytes)

### `c027-gov-acceptance-decision`

`c027-gov-acceptance-decision.cmd` (219 bytes)

````text
/usr/bin/grep -n -F Peter\ Duscha\ accepts\ that\ recommendation\ and\ the -- /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md

````

`c027-gov-acceptance-decision.out` (81 bytes)

````text
12:Important or Optional issue. Peter Duscha accepts that recommendation and the

````

`c027-gov-acceptance-decision.err` (0 bytes)

### `c028-gov-proposal-hf-sections`

`c028-gov-proposal-hf-sections.cmd` (269 bytes)

````text
/usr/bin/grep -n -E \^####\ 4\\.4\\.1\ \|\^####\ 4\\.4\\.2b\ \|\^\\\|\ HF-\(0\[1-9\]\|1\[0-9\]\)\ \|\^\\\*\ \\\*\\\*HF-20\ \\\(new\\\): -- /var/tmp/p5-r5-rp11-h0-20261006-02-checkout/docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md

````

`c028-gov-proposal-hf-sections.out` (4068 bytes)

````text
4427:#### 4.4.1 The read-only fact set (defined here; the executable H-0 assignment is OH-S1)
4431:| HF-01 | nodename | C-ID: `uname -n` |
4432:| HF-02 | `/etc/machine-id` SHA-256 only (MD-6) | C-DIG: `sha256sum /etc/machine-id` |
4433:| HF-03 | `ubuntu`: UID, primary GID, supplementary groups; home directory and shell path from the password database | C-ID: `id ubuntu`, `getent passwd ubuntu`, `getent group` for each listed group |
4434:| HF-04 | architecture, kernel release and version string | C-ID: `uname -m -r -v` |
4435:| HF-05 | PID 1 is systemd | C-PROC: read `/proc/1/comm`; `systemctl --version` |
4436:| HF-06 | systemd, polkit, glibc and CPython versions | C-VER/C-PKG |
4437:| HF-07 | package versions and provenance for `systemd`, `systemd-sysv`, `libsystemd0`, `libsystemd-shared` (if packaged separately), `polkitd`, `libpolkit-gobject-1-0`, `libc6`, `libc-bin`, `python3.12`, `python3.12-minimal`, `libpython3.12-minimal`, `libpython3.12-stdlib`, `coreutils`, `util-linux`, `sudo` and `dbus`. The final list is fixed by the H-0 assignment | C-PKG: `dpkg-query -W -f`; `dpkg -S` for `/usr/bin/python3.12`, the dynamic loader, `/usr/lib/systemd/systemd-executor` (if present), `/usr/lib/polkit-1/polkitd`; `dpkg --verify` for these packages; `apt-cache policy` (local lists only, **no** `apt update`) |
4438:| HF-08 | `/usr/bin/python3.12`: owner, mode, real path, SHA-256; version and `sys.flags` under `-I -S` | C-STAT, C-DIG; `/usr/bin/python3.12 -I -S -c` printing `sys.version`, `sys.flags.isolated`, `sys.flags.no_site`, `sys.prefix`, `sys.path` |
4439:| HF-09 | dynamic-loader inputs (U-9): the real path and SHA-256 of `/lib64/ld-linux-x86-64.so.2`; `/etc/ld.so.preload` present or absent (and, if present, owner, mode and digest only); the SHA-256, owner and mode of `/etc/ld.so.cache`; the names and digests of `/etc/ld.so.conf` and `/etc/ld.so.conf.d/*` | C-STAT, C-DIG |
4440:| HF-10 | required binaries present, root-owned and not group- or world-writable: `/usr/bin/systemctl`, `/usr/bin/python3.12`, `/usr/bin/sha256sum`, `/usr/bin/stat`, `/usr/bin/sudo`, `/usr/bin/journalctl`, `/usr/bin/dpkg-query` | C-STAT |
4441:| HF-11 | every §4.2.3 path and parent: present or absent, type, owner, group, mode, extended-attribute **names** | C-STAT (Python `os.lstat` and `os.listxattr`) |
4442:| HF-12 | polkit rules directories (`/etc/polkit-1/rules.d`, `/usr/share/polkit-1/rules.d`, `/run/polkit-1/rules.d`, `/usr/local/share/polkit-1/rules.d`): owner and mode; file names and SHA-256 where readable without privilege, otherwise `unreadable` | C-STAT, C-DIG |
4443:| HF-13 | unit and drop-in collisions: `systemctl show rp11-capture-pass-a.service -p LoadState -p FragmentPath -p DropInPaths`; `systemd-analyze unit-paths`; names under every `⟨unit-path⟩/rp11-capture-pass-a.service.d/` and `⟨unit-path⟩/service.d/` | C-SDQ, C-STAT |
4444:| HF-14 | `binfmt_misc`: `/proc/self/mountinfo` entry; `status`; every entry's file, read-only (§4.3.6 grammar) | C-PROC |
4445:| HF-15 | filesystem type, mount options and capacity of `/`, `/usr/local`, `/etc`, `/var/lib` and `/var/tmp`, and of the proposed capture-root parent if OH-D-3(a) *(D3-R1: OH-D-3 decided (a); always recorded)* | C-STAT: `findmnt --target`, `df --output` |
4446:| HF-16 | the manager `Default*` values, by the HF-07-version property list where already cited; otherwise deferred to H-1 | C-SDQ, explicit `-p` only |
4447:| HF-17 | automatic-update configuration that could change HF-07 (the `apt-daily*` and `unattended-upgrades` timers' presence and state) | C-SDQ: `systemctl list-timers --all --no-legend` (names and next-run fields only) |
4448:| HF-18 | the operator client's presence, if OH-D-2 asks for it *(D3-R1: OH-D-2 decided; the interactive client's presence is recorded as a fact and is never satisfied by installing one)* | C-STAT on the named path only |
4560:#### 4.4.2b PO-21, and the PO-11 and PO-20 extensions for supervised, boot-scoped activation *(D3-R2, new)*
4651:* **HF-20 (new):** the `LoadState` of `systemd-soft-reboot.service` and

````

`c028-gov-proposal-hf-sections.err` (0 bytes)

### `c029-r5-prompt-decode`

`c029-r5-prompt-decode.cmd` (80 bytes)

````text
/usr/bin/base64 -d -- /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-prompt.b64

````

stdout file `R5-prompt.md` (6942 bytes), reproduced or identified above

`c029-r5-prompt-decode.err` (0 bytes)

### `c030-r5-authority-decode`

`c030-r5-authority-decode.cmd` (83 bytes)

````text
/usr/bin/base64 -d -- /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-authority.b64

````

stdout file `R5-authority.md` (2245 bytes), reproduced or identified above

`c030-r5-authority-decode.err` (0 bytes)

### `c031-r5-copies-sha256`

`c031-r5-copies-sha256.cmd` (139 bytes)

````text
/usr/bin/sha256sum -- /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-prompt.md /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-authority.md

````

`c031-r5-copies-sha256.out` (249 bytes)

````text
57d23c1ba683ce8c2be15fe101da959a9dc1334ff89a1b0c66f917f26cf42e8e  /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-prompt.md
ddc0f9f1ca3c556f34a7844b6f6e969d8dc192ced37a7aef13a17bee75ffce66  /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-authority.md

````

`c031-r5-copies-sha256.err` (0 bytes)

### `c032-r5-copies-stat`

`c032-r5-copies-stat.cmd` (144 bytes)

````text
/usr/bin/stat -c %n\ %s -- /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-prompt.md /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-authority.md

````

`c032-r5-copies-stat.out` (127 bytes)

````text
/var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-prompt.md 6942
/var/tmp/p5-r5-rp11-h0-20261006-02-evidence/R5-authority.md 2245

````

`c032-r5-copies-stat.err` (0 bytes)

### `c033-hf03-id-ubuntu`

`c033-hf03-id-ubuntu.cmd` (19 bytes)

````text
/usr/bin/id ubuntu

````

`c033-hf03-id-ubuntu.out` (113 bytes)

````text
uid=1001(ubuntu) gid=1001(ubuntu) groups=1001(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),102(lxd),986(freedomlab)

````

`c033-hf03-id-ubuntu.err` (0 bytes)

### `c034-hf03-id-Gn-ubuntu`

`c034-hf03-id-Gn-ubuntu.cmd` (23 bytes)

````text
/usr/bin/id -Gn ubuntu

````

`c034-hf03-id-Gn-ubuntu.out` (41 bytes)

````text
ubuntu adm cdrom sudo dip lxd freedomlab

````

`c034-hf03-id-Gn-ubuntu.err` (0 bytes)

### `c035-hf03-getent-passwd`

`c035-hf03-getent-passwd.cmd` (30 bytes)

````text
/usr/bin/getent passwd ubuntu

````

`c035-hf03-getent-passwd.out` (49 bytes)

````text
ubuntu:x:1001:1001:Ubuntu:/home/ubuntu:/bin/bash

````

`c035-hf03-getent-passwd.err` (0 bytes)

### `c036-hf03-getent-group-ubuntu`

`c036-hf03-getent-group-ubuntu.cmd` (29 bytes)

````text
/usr/bin/getent group ubuntu

````

`c036-hf03-getent-group-ubuntu.out` (15 bytes)

````text
ubuntu:x:1001:

````

`c036-hf03-getent-group-ubuntu.err` (0 bytes)

### `c037-hf03-getent-group-adm`

`c037-hf03-getent-group-adm.cmd` (26 bytes)

````text
/usr/bin/getent group adm

````

`c037-hf03-getent-group-adm.out` (29 bytes)

````text
adm:x:4:syslog,ubuntu,ocarun

````

`c037-hf03-getent-group-adm.err` (0 bytes)

### `c038-hf03-getent-group-cdrom`

`c038-hf03-getent-group-cdrom.cmd` (28 bytes)

````text
/usr/bin/getent group cdrom

````

`c038-hf03-getent-group-cdrom.out` (18 bytes)

````text
cdrom:x:24:ubuntu

````

`c038-hf03-getent-group-cdrom.err` (0 bytes)

### `c039-hf03-getent-group-sudo`

`c039-hf03-getent-group-sudo.cmd` (27 bytes)

````text
/usr/bin/getent group sudo

````

`c039-hf03-getent-group-sudo.out` (17 bytes)

````text
sudo:x:27:ubuntu

````

`c039-hf03-getent-group-sudo.err` (0 bytes)

### `c040-hf03-getent-group-dip`

`c040-hf03-getent-group-dip.cmd` (26 bytes)

````text
/usr/bin/getent group dip

````

`c040-hf03-getent-group-dip.out` (16 bytes)

````text
dip:x:30:ubuntu

````

`c040-hf03-getent-group-dip.err` (0 bytes)

### `c041-hf03-getent-group-lxd`

`c041-hf03-getent-group-lxd.cmd` (26 bytes)

````text
/usr/bin/getent group lxd

````

`c041-hf03-getent-group-lxd.out` (17 bytes)

````text
lxd:x:102:ubuntu

````

`c041-hf03-getent-group-lxd.err` (0 bytes)

### `c042-hf03-getent-group-freedomlab`

`c042-hf03-getent-group-freedomlab.cmd` (33 bytes)

````text
/usr/bin/getent group freedomlab

````

`c042-hf03-getent-group-freedomlab.out` (24 bytes)

````text
freedomlab:x:986:ubuntu

````

`c042-hf03-getent-group-freedomlab.err` (0 bytes)

### `c043-hf04-uname-mrv`

`c043-hf04-uname-mrv.cmd` (24 bytes)

````text
/usr/bin/uname -m -r -v

````

`c043-hf04-uname-mrv.out` (84 bytes)

````text
7.0.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug  1 04:26:38 UTC 2026 x86_64

````

`c043-hf04-uname-mrv.err` (0 bytes)

### `c044-hf05-proc1-comm`

`c044-hf05-proc1-comm.cmd` (26 bytes)

````text
/usr/bin/cat /proc/1/comm

````

`c044-hf05-proc1-comm.out` (8 bytes)

````text
systemd

````

`c044-hf05-proc1-comm.err` (0 bytes)

### `c045-hf05-hf06-systemctl-version`

`c045-hf05-hf06-systemctl-version.cmd` (29 bytes)

````text
/usr/bin/systemctl --version

````

`c045-hf05-hf06-systemctl-version.out` (342 bytes)

````text
systemd 259 (259.5-0ubuntu3.4)
+PAM +AUDIT +SELINUX +APPARMOR +IMA +IPE +SMACK +SECCOMP +GCRYPT -GNUTLS +OPENSSL +ACL +BLKID +CURL +ELFUTILS +FIDO2 +IDN2 -IDN +KMOD +LIBCRYPTSETUP +LIBCRYPTSETUP_PLUGINS +LIBFDISK +PCRE2 +PWQUALITY +P11KIT +QRENCODE +TPM2 +BZIP2 +LZ4 +XZ +ZLIB +ZSTD +BPF_FRAMEWORK +BTF -XKBCOMMON -UTMP +SYSVINIT +LIBARCHIVE

````

`c045-hf05-hf06-systemctl-version.err` (0 bytes)

### `c046-hf07-dpkg-query-systemd`

`c046-hf07-dpkg-query-systemd.cmd` (135 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n systemd

````

`c046-hf07-dpkg-query-systemd.out` (36 bytes)

````text
systemd	259.5-0ubuntu3.4	amd64	ii 	

````

`c046-hf07-dpkg-query-systemd.err` (0 bytes)

### `c047-hf07-dpkg-query-systemd-sysv`

`c047-hf07-dpkg-query-systemd-sysv.cmd` (140 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n systemd-sysv

````

`c047-hf07-dpkg-query-systemd-sysv.out` (48 bytes)

````text
systemd-sysv	259.5-0ubuntu3.4	amd64	ii 	systemd

````

`c047-hf07-dpkg-query-systemd-sysv.err` (0 bytes)

### `c048-hf07-dpkg-query-libsystemd0`

`c048-hf07-dpkg-query-libsystemd0.cmd` (139 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libsystemd0

````

`c048-hf07-dpkg-query-libsystemd0.out` (53 bytes)

````text
libsystemd0:amd64	259.5-0ubuntu3.4	amd64	ii 	systemd

````

`c048-hf07-dpkg-query-libsystemd0.err` (0 bytes)

### `c049-hf07-dpkg-query-libsystemd-shared`

`c049-hf07-dpkg-query-libsystemd-shared.cmd` (145 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libsystemd-shared

````

`c049-hf07-dpkg-query-libsystemd-shared.out` (59 bytes)

````text
libsystemd-shared:amd64	259.5-0ubuntu3.4	amd64	ii 	systemd

````

`c049-hf07-dpkg-query-libsystemd-shared.err` (0 bytes)

### `c050-hf07-dpkg-query-polkitd`

`c050-hf07-dpkg-query-polkitd.cmd` (135 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n polkitd

````

`c050-hf07-dpkg-query-polkitd.out` (45 bytes)

````text
polkitd	127-2ubuntu1.1	amd64	ii 	policykit-1

````

`c050-hf07-dpkg-query-polkitd.err` (0 bytes)

### `c051-hf07-dpkg-query-libpolkit-gobject-1-0`

`c051-hf07-dpkg-query-libpolkit-gobject-1-0.cmd` (149 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libpolkit-gobject-1-0

````

`c051-hf07-dpkg-query-libpolkit-gobject-1-0.out` (65 bytes)

````text
libpolkit-gobject-1-0:amd64	127-2ubuntu1.1	amd64	ii 	policykit-1

````

`c051-hf07-dpkg-query-libpolkit-gobject-1-0.err` (0 bytes)

### `c052-hf07-dpkg-query-libc6`

`c052-hf07-dpkg-query-libc6.cmd` (133 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libc6

````

`c052-hf07-dpkg-query-libc6.out` (44 bytes)

````text
libc6:amd64	2.43-2ubuntu2.4	amd64	ii 	glibc

````

`c052-hf07-dpkg-query-libc6.err` (0 bytes)

### `c053-hf07-dpkg-query-libc-bin`

`c053-hf07-dpkg-query-libc-bin.cmd` (136 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libc-bin

````

`c053-hf07-dpkg-query-libc-bin.out` (41 bytes)

````text
libc-bin	2.43-2ubuntu2.4	amd64	ii 	glibc

````

`c053-hf07-dpkg-query-libc-bin.err` (0 bytes)

### `c054-hf07-dpkg-query-python3.12`

`c054-hf07-dpkg-query-python3.12.cmd` (138 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n python3.12

````

`c054-hf07-dpkg-query-python3.12.out` (0 bytes)

`c054-hf07-dpkg-query-python3.12.err` (50 bytes)

````text
dpkg-query: no packages found matching python3.12

````

### `c055-hf07-dpkg-query-python3.12-minimal`

`c055-hf07-dpkg-query-python3.12-minimal.cmd` (146 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n python3.12-minimal

````

`c055-hf07-dpkg-query-python3.12-minimal.out` (0 bytes)

`c055-hf07-dpkg-query-python3.12-minimal.err` (58 bytes)

````text
dpkg-query: no packages found matching python3.12-minimal

````

### `c056-hf07-dpkg-query-libpython3.12-minimal`

`c056-hf07-dpkg-query-libpython3.12-minimal.cmd` (149 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libpython3.12-minimal

````

`c056-hf07-dpkg-query-libpython3.12-minimal.out` (0 bytes)

`c056-hf07-dpkg-query-libpython3.12-minimal.err` (61 bytes)

````text
dpkg-query: no packages found matching libpython3.12-minimal

````

### `c057-hf07-dpkg-query-libpython3.12-stdlib`

`c057-hf07-dpkg-query-libpython3.12-stdlib.cmd` (148 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n libpython3.12-stdlib

````

`c057-hf07-dpkg-query-libpython3.12-stdlib.out` (0 bytes)

`c057-hf07-dpkg-query-libpython3.12-stdlib.err` (60 bytes)

````text
dpkg-query: no packages found matching libpython3.12-stdlib

````

### `c058-hf07-dpkg-query-coreutils`

`c058-hf07-dpkg-query-coreutils.cmd` (137 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n coreutils

````

`c058-hf07-dpkg-query-coreutils.out` (78 bytes)

````text
coreutils	9.5-1ubuntu2+0.0.0~ubuntu25	all	ii 	coreutils-from (0.0.0~ubuntu25)

````

`c058-hf07-dpkg-query-coreutils.err` (0 bytes)

### `c059-hf07-dpkg-query-util-linux`

`c059-hf07-dpkg-query-util-linux.cmd` (138 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n util-linux

````

`c059-hf07-dpkg-query-util-linux.out` (40 bytes)

````text
util-linux	2.41.3-3ubuntu2.2	amd64	ii 	

````

`c059-hf07-dpkg-query-util-linux.err` (0 bytes)

### `c060-hf07-dpkg-query-sudo`

`c060-hf07-dpkg-query-sudo.cmd` (132 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n sudo

````

`c060-hf07-dpkg-query-sudo.out` (36 bytes)

````text
sudo	1.9.17p2-1ubuntu3.1	amd64	ii 	

````

`c060-hf07-dpkg-query-sudo.err` (0 bytes)

### `c061-hf07-dpkg-query-dbus`

`c061-hf07-dpkg-query-dbus.cmd` (132 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n dbus

````

`c061-hf07-dpkg-query-dbus.out` (32 bytes)

````text
dbus	1.16.2-2ubuntu4	amd64	ii 	

````

`c061-hf07-dpkg-query-dbus.err` (0 bytes)

### `c062-hf09-ld-readlink`

`c062-hf09-ld-readlink.cmd` (52 bytes)

````text
/usr/bin/readlink -f -- /lib64/ld-linux-x86-64.so.2

````

`c062-hf09-ld-readlink.out` (47 bytes)

````text
/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2

````

`c062-hf09-ld-readlink.err` (0 bytes)

### `c063-hf07-dpkg-S-_usr_bin_python3.12`

`c063-hf07-dpkg-S-_usr_bin_python3.12.cmd` (37 bytes)

````text
/usr/bin/dpkg -S /usr/bin/python3.12

````

`c063-hf07-dpkg-S-_usr_bin_python3.12.out` (0 bytes)

`c063-hf07-dpkg-S-_usr_bin_python3.12.err` (63 bytes)

````text
dpkg-query: no path found matching pattern /usr/bin/python3.12

````

### `c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2`

`c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.cmd` (45 bytes)

````text
/usr/bin/dpkg -S /lib64/ld-linux-x86-64.so.2

````

`c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.out` (118 bytes)

````text
diversion by libc6 from: /lib64/ld-linux-x86-64.so.2
diversion by libc6 to: /lib64/ld-linux-x86-64.so.2.usr-is-merged

````

`c064-hf07-dpkg-S-_lib64_ld-linux-x86-64.so.2.err` (0 bytes)

### `c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor`

`c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.cmd` (51 bytes)

````text
/usr/bin/dpkg -S /usr/lib/systemd/systemd-executor

````

`c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.out` (43 bytes)

````text
systemd: /usr/lib/systemd/systemd-executor

````

`c065-hf07-dpkg-S-_usr_lib_systemd_systemd-executor.err` (0 bytes)

### `c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd`

`c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.cmd` (43 bytes)

````text
/usr/bin/dpkg -S /usr/lib/polkit-1/polkitd

````

`c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.out` (35 bytes)

````text
polkitd: /usr/lib/polkit-1/polkitd

````

`c066-hf07-dpkg-S-_usr_lib_polkit-1_polkitd.err` (0 bytes)

### `c067-hf07-dpkg-S-_usr_bin_pkcheck`

`c067-hf07-dpkg-S-_usr_bin_pkcheck.cmd` (34 bytes)

````text
/usr/bin/dpkg -S /usr/bin/pkcheck

````

`c067-hf07-dpkg-S-_usr_bin_pkcheck.out` (26 bytes)

````text
polkitd: /usr/bin/pkcheck

````

`c067-hf07-dpkg-S-_usr_bin_pkcheck.err` (0 bytes)

### `c068-hf07-dpkg-S-_usr_bin_python3`

`c068-hf07-dpkg-S-_usr_bin_python3.cmd` (34 bytes)

````text
/usr/bin/dpkg -S /usr/bin/python3

````

`c068-hf07-dpkg-S-_usr_bin_python3.out` (34 bytes)

````text
python3-minimal: /usr/bin/python3

````

`c068-hf07-dpkg-S-_usr_bin_python3.err` (0 bytes)

### `c069-hf07-dpkg-S-_usr_bin_python3.14`

`c069-hf07-dpkg-S-_usr_bin_python3.14.cmd` (37 bytes)

````text
/usr/bin/dpkg -S /usr/bin/python3.14

````

`c069-hf07-dpkg-S-_usr_bin_python3.14.out` (40 bytes)

````text
python3.14-minimal: /usr/bin/python3.14

````

`c069-hf07-dpkg-S-_usr_bin_python3.14.err` (0 bytes)

### `c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2`

`c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.cmd` (64 bytes)

````text
/usr/bin/dpkg -S /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2

````

`c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.out` (60 bytes)

````text
libc6:amd64: /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2

````

`c070-hf07-dpkg-S-_usr_lib_x86_64-linux-gnu_ld-linux-x86-64.so.2.err` (0 bytes)

### `c071-hf07-dpkg-query-python3-minimal`

`c071-hf07-dpkg-query-python3-minimal.cmd` (143 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n python3-minimal

````

`c071-hf07-dpkg-query-python3-minimal.out` (59 bytes)

````text
python3-minimal	3.14.3-0ubuntu2	amd64	ii 	python3-defaults

````

`c071-hf07-dpkg-query-python3-minimal.err` (0 bytes)

### `c072-hf07-dpkg-query-python3.14-minimal`

`c072-hf07-dpkg-query-python3.14-minimal.cmd` (146 bytes)

````text
/usr/bin/dpkg-query -W -f \$\{binary:Package\}\\t\$\{Version\}\\t\$\{Architecture\}\\t\$\{db:Status-Abbrev\}\\t\$\{Source\}\\n python3.14-minimal

````

`c072-hf07-dpkg-query-python3.14-minimal.out` (58 bytes)

````text
python3.14-minimal	3.14.4-1ubuntu0.2	amd64	ii 	python3.14

````

`c072-hf07-dpkg-query-python3.14-minimal.err` (0 bytes)

### `c073-hf07-dpkg-verify-systemd`

`c073-hf07-dpkg-verify-systemd.cmd` (31 bytes)

````text
/usr/bin/dpkg --verify systemd

````

`c073-hf07-dpkg-verify-systemd.out` (0 bytes)

`c073-hf07-dpkg-verify-systemd.err` (0 bytes)

### `c074-hf07-dpkg-verify-systemd-sysv`

`c074-hf07-dpkg-verify-systemd-sysv.cmd` (36 bytes)

````text
/usr/bin/dpkg --verify systemd-sysv

````

`c074-hf07-dpkg-verify-systemd-sysv.out` (0 bytes)

`c074-hf07-dpkg-verify-systemd-sysv.err` (0 bytes)

### `c075-hf07-dpkg-verify-libsystemd0`

`c075-hf07-dpkg-verify-libsystemd0.cmd` (35 bytes)

````text
/usr/bin/dpkg --verify libsystemd0

````

`c075-hf07-dpkg-verify-libsystemd0.out` (0 bytes)

`c075-hf07-dpkg-verify-libsystemd0.err` (0 bytes)

### `c076-hf07-dpkg-verify-libsystemd-shared`

`c076-hf07-dpkg-verify-libsystemd-shared.cmd` (41 bytes)

````text
/usr/bin/dpkg --verify libsystemd-shared

````

`c076-hf07-dpkg-verify-libsystemd-shared.out` (0 bytes)

`c076-hf07-dpkg-verify-libsystemd-shared.err` (0 bytes)

### `c077-hf07-dpkg-verify-polkitd`

`c077-hf07-dpkg-verify-polkitd.cmd` (31 bytes)

````text
/usr/bin/dpkg --verify polkitd

````

`c077-hf07-dpkg-verify-polkitd.out` (0 bytes)

`c077-hf07-dpkg-verify-polkitd.err` (0 bytes)

### `c078-hf07-dpkg-verify-libpolkit-gobject-1-0`

`c078-hf07-dpkg-verify-libpolkit-gobject-1-0.cmd` (45 bytes)

````text
/usr/bin/dpkg --verify libpolkit-gobject-1-0

````

`c078-hf07-dpkg-verify-libpolkit-gobject-1-0.out` (0 bytes)

`c078-hf07-dpkg-verify-libpolkit-gobject-1-0.err` (0 bytes)

### `c079-hf07-dpkg-verify-libc6`

`c079-hf07-dpkg-verify-libc6.cmd` (29 bytes)

````text
/usr/bin/dpkg --verify libc6

````

`c079-hf07-dpkg-verify-libc6.out` (0 bytes)

`c079-hf07-dpkg-verify-libc6.err` (0 bytes)

### `c080-hf07-dpkg-verify-libc-bin`

`c080-hf07-dpkg-verify-libc-bin.cmd` (32 bytes)

````text
/usr/bin/dpkg --verify libc-bin

````

`c080-hf07-dpkg-verify-libc-bin.out` (0 bytes)

`c080-hf07-dpkg-verify-libc-bin.err` (0 bytes)

### `c081-hf07-dpkg-verify-python3.12`

`c081-hf07-dpkg-verify-python3.12.cmd` (34 bytes)

````text
/usr/bin/dpkg --verify python3.12

````

`c081-hf07-dpkg-verify-python3.12.out` (0 bytes)

`c081-hf07-dpkg-verify-python3.12.err` (44 bytes)

````text
dpkg: package 'python3.12' is not installed

````

### `c082-hf07-dpkg-verify-python3.12-minimal`

`c082-hf07-dpkg-verify-python3.12-minimal.cmd` (42 bytes)

````text
/usr/bin/dpkg --verify python3.12-minimal

````

`c082-hf07-dpkg-verify-python3.12-minimal.out` (0 bytes)

`c082-hf07-dpkg-verify-python3.12-minimal.err` (52 bytes)

````text
dpkg: package 'python3.12-minimal' is not installed

````

### `c083-hf07-dpkg-verify-libpython3.12-minimal`

`c083-hf07-dpkg-verify-libpython3.12-minimal.cmd` (45 bytes)

````text
/usr/bin/dpkg --verify libpython3.12-minimal

````

`c083-hf07-dpkg-verify-libpython3.12-minimal.out` (0 bytes)

`c083-hf07-dpkg-verify-libpython3.12-minimal.err` (55 bytes)

````text
dpkg: package 'libpython3.12-minimal' is not installed

````

### `c084-hf07-dpkg-verify-libpython3.12-stdlib`

`c084-hf07-dpkg-verify-libpython3.12-stdlib.cmd` (44 bytes)

````text
/usr/bin/dpkg --verify libpython3.12-stdlib

````

`c084-hf07-dpkg-verify-libpython3.12-stdlib.out` (0 bytes)

`c084-hf07-dpkg-verify-libpython3.12-stdlib.err` (54 bytes)

````text
dpkg: package 'libpython3.12-stdlib' is not installed

````

### `c085-hf07-dpkg-verify-coreutils`

`c085-hf07-dpkg-verify-coreutils.cmd` (33 bytes)

````text
/usr/bin/dpkg --verify coreutils

````

`c085-hf07-dpkg-verify-coreutils.out` (0 bytes)

`c085-hf07-dpkg-verify-coreutils.err` (0 bytes)

### `c086-hf07-dpkg-verify-util-linux`

`c086-hf07-dpkg-verify-util-linux.cmd` (34 bytes)

````text
/usr/bin/dpkg --verify util-linux

````

`c086-hf07-dpkg-verify-util-linux.out` (0 bytes)

`c086-hf07-dpkg-verify-util-linux.err` (0 bytes)

### `c087-hf07-dpkg-verify-sudo`

`c087-hf07-dpkg-verify-sudo.cmd` (28 bytes)

````text
/usr/bin/dpkg --verify sudo

````

`c087-hf07-dpkg-verify-sudo.out` (0 bytes)

`c087-hf07-dpkg-verify-sudo.err` (0 bytes)

### `c088-hf07-dpkg-verify-dbus`

`c088-hf07-dpkg-verify-dbus.cmd` (28 bytes)

````text
/usr/bin/dpkg --verify dbus

````

`c088-hf07-dpkg-verify-dbus.out` (0 bytes)

`c088-hf07-dpkg-verify-dbus.err` (0 bytes)

### `c089-hf07-dpkg-verify-python3-minimal`

`c089-hf07-dpkg-verify-python3-minimal.cmd` (39 bytes)

````text
/usr/bin/dpkg --verify python3-minimal

````

`c089-hf07-dpkg-verify-python3-minimal.out` (0 bytes)

`c089-hf07-dpkg-verify-python3-minimal.err` (0 bytes)

### `c090-hf07-dpkg-verify-python3.14-minimal`

`c090-hf07-dpkg-verify-python3.14-minimal.cmd` (42 bytes)

````text
/usr/bin/dpkg --verify python3.14-minimal

````

`c090-hf07-dpkg-verify-python3.14-minimal.out` (0 bytes)

`c090-hf07-dpkg-verify-python3.14-minimal.err` (0 bytes)

### `c091-hf07-apt-cache-policy`

`c091-hf07-apt-cache-policy.cmd` (261 bytes)

````text
/usr/bin/apt-cache policy systemd systemd-sysv libsystemd0 libsystemd-shared polkitd libpolkit-gobject-1-0 libc6 libc-bin python3.12 python3.12-minimal libpython3.12-minimal libpython3.12-stdlib coreutils util-linux sudo dbus python3-minimal python3.14-minimal

````

`c091-hf07-apt-cache-policy.out` (6396 bytes)

````text
systemd:
  Installed: 259.5-0ubuntu3.4
  Candidate: 259.5-0ubuntu3.4
  Version table:
 *** 259.5-0ubuntu3.4 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     259.5-0ubuntu3 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
systemd-sysv:
  Installed: 259.5-0ubuntu3.4
  Candidate: 259.5-0ubuntu3.4
  Version table:
 *** 259.5-0ubuntu3.4 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     259.5-0ubuntu3 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
libsystemd0:
  Installed: 259.5-0ubuntu3.4
  Candidate: 259.5-0ubuntu3.4
  Version table:
 *** 259.5-0ubuntu3.4 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     259.5-0ubuntu3 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
libsystemd-shared:
  Installed: 259.5-0ubuntu3.4
  Candidate: 259.5-0ubuntu3.4
  Version table:
 *** 259.5-0ubuntu3.4 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     259.5-0ubuntu3 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
polkitd:
  Installed: 127-2ubuntu1.1
  Candidate: 127-2ubuntu1.1
  Version table:
 *** 127-2ubuntu1.1 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     127-2ubuntu1 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
libpolkit-gobject-1-0:
  Installed: 127-2ubuntu1.1
  Candidate: 127-2ubuntu1.1
  Version table:
 *** 127-2ubuntu1.1 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     127-2ubuntu1 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
libc6:
  Installed: 2.43-2ubuntu2.4
  Candidate: 2.43-2ubuntu2.4
  Version table:
 *** 2.43-2ubuntu2.4 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     2.43-2ubuntu2 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
libc-bin:
  Installed: 2.43-2ubuntu2.4
  Candidate: 2.43-2ubuntu2.4
  Version table:
 *** 2.43-2ubuntu2.4 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     2.43-2ubuntu2 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
postgresql-plpython3-12-dbgsym:
  Installed: (none)
  Candidate: 12.22-4.pgdg26.04+2
  Version table:
     12.22-4.pgdg26.04+2 500
        500 http://apt.postgresql.org/pub/repos/apt resolute-pgdg/main amd64 Packages
postgresql-plpython3-12:
  Installed: (none)
  Candidate: 12.22-4.pgdg26.04+2
  Version table:
     12.22-4.pgdg26.04+2 500
        500 http://apt.postgresql.org/pub/repos/apt resolute-pgdg/main amd64 Packages
coreutils:
  Installed: 9.5-1ubuntu2+0.0.0~ubuntu25
  Candidate: 9.5-1ubuntu2+0.0.0~ubuntu25
  Version table:
 *** 9.5-1ubuntu2+0.0.0~ubuntu25 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
        100 /var/lib/dpkg/status
util-linux:
  Installed: 2.41.3-3ubuntu2.2
  Candidate: 2.41.3-3ubuntu2.2
  Version table:
 *** 2.41.3-3ubuntu2.2 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     2.41.3-3ubuntu2 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
sudo:
  Installed: 1.9.17p2-1ubuntu3.1
  Candidate: 1.9.17p2-1ubuntu3.1
  Version table:
 *** 1.9.17p2-1ubuntu3.1 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute-updates/main amd64v3 Packages
        500 http://security.ubuntu.com/ubuntu resolute-security/main amd64v3 Packages
        100 /var/lib/dpkg/status
     1.9.17p2-1ubuntu3 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
dbus:
  Installed: 1.16.2-2ubuntu4
  Candidate: 1.16.2-2ubuntu4
  Version table:
 *** 1.16.2-2ubuntu4 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
        100 /var/lib/dpkg/status
python3-minimal:
  Installed: 3.14.3-0ubuntu2
  Candidate: 3.14.3-0ubuntu2
  Version table:
 *** 3.14.3-0ubuntu2 500
        500 http://eu-frankfurt-1-ad-3.clouds.archive.ubuntu.com/ubuntu resolute/main amd64v3 Packages
        100 /var/lib/dpkg/status
python3.14-minimal:
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

`c091-hf07-apt-cache-policy.err` (0 bytes)

### `c092-hf08-stat-python312`

`c092-hf08-stat-python312.cmd` (88 bytes)

````text
/usr/bin/stat -c name=%n\ type=%F\ owner=%U:%G\ mode=%a\ size=%s -- /usr/bin/python3.12

````

`c092-hf08-stat-python312.out` (0 bytes)

`c092-hf08-stat-python312.err` (80 bytes)

````text
stat: cannot stat '/usr/bin/python3.12': No such file or directory (os error 2)

````

### `c093-hf08-readlink-python312`

`c093-hf08-readlink-python312.cmd` (44 bytes)

````text
/usr/bin/readlink -f -- /usr/bin/python3.12

````

`c093-hf08-readlink-python312.out` (20 bytes)

````text
/usr/bin/python3.12

````

`c093-hf08-readlink-python312.err` (0 bytes)

### `c094-hf08-sha256-python312`

`c094-hf08-sha256-python312.cmd` (42 bytes)

````text
/usr/bin/sha256sum -- /usr/bin/python3.12

````

`c094-hf08-sha256-python312.out` (0 bytes)

`c094-hf08-sha256-python312.err` (58 bytes)

````text
sha256sum: /usr/bin/python3.12: No such file or directory

````

### `c095-hf08-version-python312`

`c095-hf08-version-python312.cmd` (408 bytes)

````text
/usr/bin/python3.12 -I -S -c $'import sys\nprint("version=" + sys.version.replace("\\n", " "))\nprint("version_info=" + ".".join(str(x) for x in sys.version_info[:3]))\nprint("major=" + str(sys.version_info[0]))\nprint("isolated=" + str(sys.flags.isolated))\nprint("no_site=" + str(sys.flags.no_site))\nprint("executable=" + sys.executable)\nprint("prefix=" + sys.prefix)\nprint("path=" + repr(sys.path))\n'

````

`c095-hf08-version-python312.out` (0 bytes)

`c095-hf08-version-python312.err` (126 bytes)

````text
/var/tmp/p5-r5-rp11-h0-20261006-02-evidence/controller-h0-program.sh: line 74: /usr/bin/python3.12: No such file or directory

````

### `c096-hf08-sha256-python3-real`

`c096-hf08-sha256-python3-real.cmd` (42 bytes)

````text
/usr/bin/sha256sum -- /usr/bin/python3.14

````

`c096-hf08-sha256-python3-real.out` (86 bytes)

````text
be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd  /usr/bin/python3.14

````

`c096-hf08-sha256-python3-real.err` (0 bytes)

### `c097-hf08-stat-python3-real`

`c097-hf08-stat-python3-real.cmd` (88 bytes)

````text
/usr/bin/stat -c name=%n\ type=%F\ owner=%U:%G\ mode=%a\ size=%s -- /usr/bin/python3.14

````

`c097-hf08-stat-python3-real.out` (81 bytes)

````text
name=/usr/bin/python3.14 type=regular file owner=root:root mode=755 size=7468968

````

`c097-hf08-stat-python3-real.err` (0 bytes)

### `c098-hf09-ld-stat`

`c098-hf09-ld-stat.cmd` (2352 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' stat /lib64/ld-linux-x86-64.so.2 /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /etc/ld.so.preload /etc/ld.so.cache /etc/ld.so.conf /etc/ld.so.conf.d

````

`c098-hf09-ld-stat.out` (734 bytes)

````text
/lib64/ld-linux-x86-64.so.2	present	symlink	uid=0	gid=0	owner=root	group=root	mode=0777	dev=2049	ino=5483	nlink=1	size=44	xattr_names=-	link=../lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2	present	reg	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=5456	nlink=1	size=250768	xattr_names=-
/etc/ld.so.preload	absent
/etc/ld.so.cache	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=14040	nlink=1	size=24791	xattr_names=-
/etc/ld.so.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=585	nlink=1	size=34	xattr_names=-
/etc/ld.so.conf.d	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=586	nlink=2	size=4096	xattr_names=-

````

`c098-hf09-ld-stat.err` (0 bytes)

### `c099-hf09-ld-sha256`

`c099-hf09-ld-sha256.cmd` (102 bytes)

````text
/usr/bin/sha256sum -- /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /etc/ld.so.cache /etc/ld.so.conf

````

`c099-hf09-ld-sha256.out` (278 bytes)

````text
75c84c6a1522e227864db7d8b40f66b5d6edefcff92538e15a964f1de7855390  /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7b196d30bc25f05bc583fb218d63e83fbf5eaa390e3e8bcf9e784f6a91a205e9  /etc/ld.so.cache
d4b198c463418b493208485def26a6f4c57279467b9dfa491b70433cedb602e8  /etc/ld.so.conf

````

`c099-hf09-ld-sha256.err` (0 bytes)

### `c100-hf09-ld-preload-lstat`

`c100-hf09-ld-preload-lstat.cmd` (2226 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' stat /etc/ld.so.preload

````

`c100-hf09-ld-preload-lstat.out` (26 bytes)

````text
/etc/ld.so.preload	absent

````

`c100-hf09-ld-preload-lstat.err` (0 bytes)

### `c101-hf09-ld-conf-d-ls`

`c101-hf09-ld-conf-d-ls.cmd` (2223 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' ls /etc/ld.so.conf.d

````

`c101-hf09-ld-conf-d-ls.out` (460 bytes)

````text
DIR	/etc/ld.so.conf.d	entries=3
/etc/ld.so.conf.d/fakeroot-x86_64-linux-gnu.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=59529	nlink=1	size=38	xattr_names=-
/etc/ld.so.conf.d/libc.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=587	nlink=1	size=44	xattr_names=-
/etc/ld.so.conf.d/x86_64-linux-gnu.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=588	nlink=1	size=78	xattr_names=-

````

`c101-hf09-ld-conf-d-ls.err` (0 bytes)

### `c102-hf09-ld-conf-d-sha256`

`c102-hf09-ld-conf-d-sha256.cmd` (139 bytes)

````text
/usr/bin/sha256sum -- /etc/ld.so.conf.d/fakeroot-x86_64-linux-gnu.conf /etc/ld.so.conf.d/libc.conf /etc/ld.so.conf.d/x86_64-linux-gnu.conf

````

`c102-hf09-ld-conf-d-sha256.out` (315 bytes)

````text
af7edc777dd224bade078ba540538444db69856533c02e18a7f9fbbdd23bd181  /etc/ld.so.conf.d/fakeroot-x86_64-linux-gnu.conf
90d4c7e43e7661cd116010eb9f50ad5817e43162df344bd1ad10898851b15d41  /etc/ld.so.conf.d/libc.conf
a1e651b43981e758869c3efef5822b60df6afc198a4c14b2552e3fb436819bfa  /etc/ld.so.conf.d/x86_64-linux-gnu.conf

````

`c102-hf09-ld-conf-d-sha256.err` (0 bytes)

### `c103-hf10-stat-lstat`

`c103-hf10-stat-lstat.cmd` (281 bytes)

````text
/usr/bin/stat -c name=%n\ type=%F\ owner=%U:%G\ uid=%u\ gid=%g\ mode=%a\ perms=%A -- /usr/bin/systemctl /usr/bin/python3.12 /usr/bin/sha256sum /usr/bin/stat /usr/bin/sudo /usr/bin/journalctl /usr/bin/dpkg-query /usr/bin/pkcheck /usr/bin/sleep /usr/bin/systemd-run /usr/bin/python3

````

`c103-hf10-stat-lstat.out` (951 bytes)

````text
name=/usr/bin/systemctl type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/sha256sum type=symbolic link owner=root:root uid=0 gid=0 mode=777 perms=lrwxrwxrwx
name=/usr/bin/stat type=symbolic link owner=root:root uid=0 gid=0 mode=777 perms=lrwxrwxrwx
name=/usr/bin/sudo type=symbolic link owner=root:root uid=0 gid=0 mode=777 perms=lrwxrwxrwx
name=/usr/bin/journalctl type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/dpkg-query type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/pkcheck type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/sleep type=symbolic link owner=root:root uid=0 gid=0 mode=777 perms=lrwxrwxrwx
name=/usr/bin/systemd-run type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/python3 type=symbolic link owner=root:root uid=0 gid=0 mode=777 perms=lrwxrwxrwx

````

`c103-hf10-stat-lstat.err` (80 bytes)

````text
stat: cannot stat '/usr/bin/python3.12': No such file or directory (os error 2)

````

### `c104-hf10-stat-follow`

`c104-hf10-stat-follow.cmd` (284 bytes)

````text
/usr/bin/stat -L -c name=%n\ type=%F\ owner=%U:%G\ uid=%u\ gid=%g\ mode=%a\ perms=%A -- /usr/bin/systemctl /usr/bin/python3.12 /usr/bin/sha256sum /usr/bin/stat /usr/bin/sudo /usr/bin/journalctl /usr/bin/dpkg-query /usr/bin/pkcheck /usr/bin/sleep /usr/bin/systemd-run /usr/bin/python3

````

`c104-hf10-stat-follow.out` (947 bytes)

````text
name=/usr/bin/systemctl type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/sha256sum type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/stat type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/sudo type=regular file owner=root:root uid=0 gid=0 mode=4755 perms=-rwsr-xr-x
name=/usr/bin/journalctl type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/dpkg-query type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/pkcheck type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/sleep type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/systemd-run type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x
name=/usr/bin/python3 type=regular file owner=root:root uid=0 gid=0 mode=755 perms=-rwxr-xr-x

````

`c104-hf10-stat-follow.err` (80 bytes)

````text
stat: cannot stat '/usr/bin/python3.12': No such file or directory (os error 2)

````

### `c105-hf11-lstat-xattr`

`c105-hf11-lstat-xattr.cmd` (3078 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' stat /usr/local/libexec/freedom-blades-rp11 /usr/local/libexec/freedom-blades-rp11/staged /usr/local/libexec/freedom-blades-rp11/rp11-launch /usr/local/libexec/freedom-blades-rp11/rp11_entry.py /usr/local/libexec/freedom-blades-rp11/rp11_h1.py /usr/local/libexec/freedom-blades-rp11/staged/50-freedom-blades-rp11.rules.staged /etc/systemd/system/rp11-capture-pass-a.service /etc/freedom-blades-rp11 /etc/freedom-blades-rp11/pass-a.json /etc/polkit-1/rules.d/50-freedom-blades-rp11.rules /var/lib/freedom-blades-rp11 /var/lib/freedom-blades-rp11/h1 /var/lib/freedom-blades-rp11/activation /run/freedom-blades-rp11 /run/freedom-blades-rp11/pass-a.json /run/polkit-1/rules.d/50-freedom-blades-rp11.rules / /usr /usr/local /usr/local/libexec /etc /etc/systemd /etc/systemd/system /etc/polkit-1 /etc/polkit-1/rules.d /var /var/lib /run /run/polkit-1 /run/polkit-1/rules.d /var/tmp

````

`c105-hf11-lstat-xattr.out` (2409 bytes)

````text
/usr/local/libexec/freedom-blades-rp11	absent
/usr/local/libexec/freedom-blades-rp11/staged	absent
/usr/local/libexec/freedom-blades-rp11/rp11-launch	absent
/usr/local/libexec/freedom-blades-rp11/rp11_entry.py	absent
/usr/local/libexec/freedom-blades-rp11/rp11_h1.py	absent
/usr/local/libexec/freedom-blades-rp11/staged/50-freedom-blades-rp11.rules.staged	absent
/etc/systemd/system/rp11-capture-pass-a.service	absent
/etc/freedom-blades-rp11	absent
/etc/freedom-blades-rp11/pass-a.json	absent
/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules	error	PermissionError	errno=13
/var/lib/freedom-blades-rp11	absent
/var/lib/freedom-blades-rp11/h1	absent
/var/lib/freedom-blades-rp11/activation	absent
/run/freedom-blades-rp11	absent
/run/freedom-blades-rp11/pass-a.json	absent
/run/polkit-1/rules.d/50-freedom-blades-rp11.rules	absent
/	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=2	nlink=19	size=4096	xattr_names=-
/usr	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=1709	nlink=12	size=4096	xattr_names=-
/usr/local	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=65097	nlink=11	size=4096	xattr_names=-
/usr/local/libexec	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=65117	nlink=2	size=4096	xattr_names=-
/etc	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=44	nlink=117	size=12288	xattr_names=-
/etc/systemd	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=419	nlink=7	size=4096	xattr_names=-
/etc/systemd/system	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=430	nlink=34	size=4096	xattr_names=-
/etc/polkit-1	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=1624	nlink=3	size=4096	xattr_names=-
/etc/polkit-1/rules.d	present	dir	uid=0	gid=983	owner=root	group=polkitd	mode=0750	dev=2049	ino=1625	nlink=2	size=4096	xattr_names=-
/var	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=97830	nlink=13	size=4096	xattr_names=-
/var/lib	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=97831	nlink=52	size=4096	xattr_names=-
/run	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=29	ino=1	nlink=40	size=1240	xattr_names=-
/run/polkit-1	absent
/run/polkit-1/rules.d	absent
/var/tmp	present	dir	uid=0	gid=0	owner=root	group=root	mode=1777	dev=2049	ino=101403	nlink=29	size=4096	xattr_names=-

````

`c105-hf11-lstat-xattr.err` (0 bytes)

### `c106-hf12-rules-dirs-stat`

`c106-hf12-rules-dirs-stat.cmd` (2313 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' stat /etc/polkit-1/rules.d /usr/share/polkit-1/rules.d /run/polkit-1/rules.d /usr/local/share/polkit-1/rules.d

````

`c106-hf12-rules-dirs-stat.out` (338 bytes)

````text
/etc/polkit-1/rules.d	present	dir	uid=0	gid=983	owner=root	group=polkitd	mode=0750	dev=2049	ino=1625	nlink=2	size=4096	xattr_names=-
/usr/share/polkit-1/rules.d	present	dir	uid=0	gid=0	owner=root	group=root	mode=0755	dev=2049	ino=48987	nlink=2	size=4096	xattr_names=-
/run/polkit-1/rules.d	absent
/usr/local/share/polkit-1/rules.d	absent

````

`c106-hf12-rules-dirs-stat.err` (0 bytes)

### `c107-hf12-rules-dirs-ls`

`c107-hf12-rules-dirs-ls.cmd` (2311 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' ls /etc/polkit-1/rules.d /usr/share/polkit-1/rules.d /run/polkit-1/rules.d /usr/local/share/polkit-1/rules.d

````

`c107-hf12-rules-dirs-ls.out` (1692 bytes)

````text
DIR	/etc/polkit-1/rules.d	unreadable
DIR	/usr/share/polkit-1/rules.d	entries=9
/usr/share/polkit-1/rules.d/10-systemd-logind-root-ignore-inhibitors.rules	present	symlink	uid=0	gid=0	owner=root	group=root	mode=0777	dev=2049	ino=48991	nlink=1	size=54	xattr_names=-	link=10-systemd-logind-root-ignore-inhibitors.rules.example
/usr/share/polkit-1/rules.d/10-systemd-logind-root-ignore-inhibitors.rules.example	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=48988	nlink=1	size=863	xattr_names=-
/usr/share/polkit-1/rules.d/49-ubuntu-admin.rules	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=22587	nlink=1	size=104	xattr_names=-
/usr/share/polkit-1/rules.d/50-default.rules	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=22588	nlink=1	size=325	xattr_names=-
/usr/share/polkit-1/rules.d/empower.rules	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=48989	nlink=1	size=260	xattr_names=-
/usr/share/polkit-1/rules.d/org.freedesktop.bolt.rules	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=48992	nlink=1	size=368	xattr_names=-
/usr/share/polkit-1/rules.d/org.freedesktop.fwupd.rules	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=48993	nlink=1	size=251	xattr_names=-
/usr/share/polkit-1/rules.d/org.freedesktop.packagekit.rules	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=36996	nlink=1	size=549	xattr_names=-
/usr/share/polkit-1/rules.d/systemd-networkd.rules	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=48990	nlink=1	size=527	xattr_names=-
DIR	/run/polkit-1/rules.d	absent
DIR	/usr/local/share/polkit-1/rules.d	absent

````

`c107-hf12-rules-dirs-ls.err` (0 bytes)

### `c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules`

`c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.cmd` (97 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/10-systemd-logind-root-ignore-inhibitors.rules

````

`c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.out` (141 bytes)

````text
0dcb4cdb6a4b43f23c4dc798e729ab605c3c0c470fe1c90f2db6351e4ae47418  /usr/share/polkit-1/rules.d/10-systemd-logind-root-ignore-inhibitors.rules

````

`c108-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.err` (0 bytes)

### `c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example`

`c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.cmd` (105 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/10-systemd-logind-root-ignore-inhibitors.rules.example

````

`c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.out` (149 bytes)

````text
0dcb4cdb6a4b43f23c4dc798e729ab605c3c0c470fe1c90f2db6351e4ae47418  /usr/share/polkit-1/rules.d/10-systemd-logind-root-ignore-inhibitors.rules.example

````

`c109-hf12-sha256-_usr_share_polkit-1_rules.d_10-systemd-logind-root-ignore-inhibitors.rules.example.err` (0 bytes)

### `c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules`

`c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.cmd` (72 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/49-ubuntu-admin.rules

````

`c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.out` (116 bytes)

````text
543995005caa05d096b9781b27a48e2369ef61e39a8a52234d2d271b6d0a9c1e  /usr/share/polkit-1/rules.d/49-ubuntu-admin.rules

````

`c110-hf12-sha256-_usr_share_polkit-1_rules.d_49-ubuntu-admin.rules.err` (0 bytes)

### `c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules`

`c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.cmd` (67 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/50-default.rules

````

`c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.out` (111 bytes)

````text
29f073ed9a8a6996b62f718e2bec962d5c84d311d23bb874830b4f9887eeabbf  /usr/share/polkit-1/rules.d/50-default.rules

````

`c111-hf12-sha256-_usr_share_polkit-1_rules.d_50-default.rules.err` (0 bytes)

### `c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules`

`c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.cmd` (64 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/empower.rules

````

`c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.out` (108 bytes)

````text
d9a62ab1ec477a4be1657769dfd194c75d1a07a4357e7717aa19ad5c07c3fc26  /usr/share/polkit-1/rules.d/empower.rules

````

`c112-hf12-sha256-_usr_share_polkit-1_rules.d_empower.rules.err` (0 bytes)

### `c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules`

`c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.cmd` (77 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/org.freedesktop.bolt.rules

````

`c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.out` (121 bytes)

````text
16da883b6ec384e0018b7e955efef1726e6470c2b4f72bfc23f9aadbec0709ca  /usr/share/polkit-1/rules.d/org.freedesktop.bolt.rules

````

`c113-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.bolt.rules.err` (0 bytes)

### `c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules`

`c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.cmd` (78 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/org.freedesktop.fwupd.rules

````

`c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.out` (122 bytes)

````text
f78e67e4e002dfd135d5bd8cb8d7b66c174d795316a1cd7bf0f3e021b85ee3a0  /usr/share/polkit-1/rules.d/org.freedesktop.fwupd.rules

````

`c114-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.fwupd.rules.err` (0 bytes)

### `c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules`

`c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.cmd` (83 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/org.freedesktop.packagekit.rules

````

`c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.out` (127 bytes)

````text
d22e59e890fd6726eaf02aded197fdc40da11bbc11fc2184d581e14e0a0437e6  /usr/share/polkit-1/rules.d/org.freedesktop.packagekit.rules

````

`c115-hf12-sha256-_usr_share_polkit-1_rules.d_org.freedesktop.packagekit.rules.err` (0 bytes)

### `c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules`

`c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.cmd` (73 bytes)

````text
/usr/bin/sha256sum -- /usr/share/polkit-1/rules.d/systemd-networkd.rules

````

`c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.out` (117 bytes)

````text
f199e386a9297858331b00df07ed0b0ee5fcf4bea67f6c0bccc8a92b7e310bbd  /usr/share/polkit-1/rules.d/systemd-networkd.rules

````

`c116-hf12-sha256-_usr_share_polkit-1_rules.d_systemd-networkd.rules.err` (0 bytes)

### `c117-hf13-systemctl-show-unit`

`c117-hf13-systemctl-show-unit.cmd` (107 bytes)

````text
/usr/bin/systemctl --no-pager show rp11-capture-pass-a.service -p LoadState -p FragmentPath -p DropInPaths

````

`c117-hf13-systemctl-show-unit.out` (47 bytes)

````text
LoadState=not-found
FragmentPath=
DropInPaths=

````

`c117-hf13-systemctl-show-unit.err` (0 bytes)

### `c118-hf13-unit-paths`

`c118-hf13-unit-paths.cmd` (36 bytes)

````text
/usr/bin/systemd-analyze unit-paths

````

`c118-hf13-unit-paths.out` (311 bytes)

````text
/etc/systemd/system.control
/run/systemd/system.control
/run/systemd/transient
/run/systemd/generator.early
/etc/systemd/system
/etc/systemd/system.attached
/run/systemd/system
/run/systemd/system.attached
/run/systemd/generator
/usr/local/lib/systemd/system
/usr/lib/systemd/system
/run/systemd/generator.late

````

`c118-hf13-unit-paths.err` (0 bytes)

### `c119-hf13-dropin-dirs-ls`

`c119-hf13-dropin-dirs-ls.cmd` (3307 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' ls /etc/systemd/system.control/rp11-capture-pass-a.service.d /etc/systemd/system.control/service.d /run/systemd/system.control/rp11-capture-pass-a.service.d /run/systemd/system.control/service.d /run/systemd/transient/rp11-capture-pass-a.service.d /run/systemd/transient/service.d /run/systemd/generator.early/rp11-capture-pass-a.service.d /run/systemd/generator.early/service.d /etc/systemd/system/rp11-capture-pass-a.service.d /etc/systemd/system/service.d /etc/systemd/system.attached/rp11-capture-pass-a.service.d /etc/systemd/system.attached/service.d /run/systemd/system/rp11-capture-pass-a.service.d /run/systemd/system/service.d /run/systemd/system.attached/rp11-capture-pass-a.service.d /run/systemd/system.attached/service.d /run/systemd/generator/rp11-capture-pass-a.service.d /run/systemd/generator/service.d /usr/local/lib/systemd/system/rp11-capture-pass-a.service.d /usr/local/lib/systemd/system/service.d /usr/lib/systemd/system/rp11-capture-pass-a.service.d /usr/lib/systemd/system/service.d /run/systemd/generator.late/rp11-capture-pass-a.service.d /run/systemd/generator.late/service.d

````

`c119-hf13-dropin-dirs-ls.out` (1366 bytes)

````text
DIR	/etc/systemd/system.control/rp11-capture-pass-a.service.d	absent
DIR	/etc/systemd/system.control/service.d	absent
DIR	/run/systemd/system.control/rp11-capture-pass-a.service.d	absent
DIR	/run/systemd/system.control/service.d	absent
DIR	/run/systemd/transient/rp11-capture-pass-a.service.d	absent
DIR	/run/systemd/transient/service.d	absent
DIR	/run/systemd/generator.early/rp11-capture-pass-a.service.d	absent
DIR	/run/systemd/generator.early/service.d	absent
DIR	/etc/systemd/system/rp11-capture-pass-a.service.d	absent
DIR	/etc/systemd/system/service.d	absent
DIR	/etc/systemd/system.attached/rp11-capture-pass-a.service.d	absent
DIR	/etc/systemd/system.attached/service.d	absent
DIR	/run/systemd/system/rp11-capture-pass-a.service.d	absent
DIR	/run/systemd/system/service.d	absent
DIR	/run/systemd/system.attached/rp11-capture-pass-a.service.d	absent
DIR	/run/systemd/system.attached/service.d	absent
DIR	/run/systemd/generator/rp11-capture-pass-a.service.d	absent
DIR	/run/systemd/generator/service.d	absent
DIR	/usr/local/lib/systemd/system/rp11-capture-pass-a.service.d	absent
DIR	/usr/local/lib/systemd/system/service.d	absent
DIR	/usr/lib/systemd/system/rp11-capture-pass-a.service.d	absent
DIR	/usr/lib/systemd/system/service.d	absent
DIR	/run/systemd/generator.late/rp11-capture-pass-a.service.d	absent
DIR	/run/systemd/generator.late/service.d	absent

````

`c119-hf13-dropin-dirs-ls.err` (0 bytes)

### `c120-hf14-hf15-proc-self-mountinfo`

`c120-hf14-hf15-proc-self-mountinfo.cmd` (34 bytes)

````text
/usr/bin/cat /proc/self/mountinfo

````

`c120-hf14-hf15-proc-self-mountinfo.out` (4005 bytes)

````text
34 48 0:29 / /run rw,nosuid,nodev shared:13 - tmpfs tmpfs rw,size=194716k,nr_inodes=819200,mode=755,inode64
48 1 8:1 / / rw,relatime shared:1 - ext4 /dev/sda1 rw,discard,errors=remount-ro,commit=30
41 48 0:7 / /dev rw,nosuid shared:2 - devtmpfs devtmpfs rw,size=409852k,nr_inodes=102463,mode=755,inode64
42 41 0:27 / /dev/shm rw,nosuid,nodev shared:3 - tmpfs tmpfs rw,inode64,usrquota
43 41 0:28 / /dev/pts rw,nosuid,noexec,relatime shared:4 - devpts devpts rw,gid=5,mode=600,ptmxmode=000
44 48 0:26 / /sys rw,nosuid,nodev,noexec,relatime shared:5 - sysfs sysfs rw
46 44 0:8 / /sys/kernel/security rw,nosuid,nodev,noexec,relatime shared:6 - securityfs securityfs rw
47 44 0:30 / /sys/fs/cgroup rw,nosuid,nodev,noexec,relatime shared:7 - cgroup2 cgroup2 rw,nsdelegate,memory_recursiveprot,memory_hugetlb_accounting
49 44 0:31 / /sys/fs/pstore rw,nosuid,nodev,noexec,relatime shared:8 - pstore none rw
50 44 0:32 / /sys/firmware/efi/efivars rw,nosuid,nodev,noexec,relatime shared:9 - efivarfs efivarfs rw
51 44 0:33 / /sys/fs/bpf rw,nosuid,nodev,noexec,relatime shared:10 - bpf bpf rw,mode=700
52 44 0:21 / /sys/kernel/config rw,nosuid,nodev,noexec,relatime shared:11 - configfs configfs rw
53 48 0:25 / /proc rw,nosuid,nodev,noexec,relatime shared:12 - proc proc rw
28 53 0:34 / /proc/sys/fs/binfmt_misc rw,relatime shared:14 - autofs systemd-1 rw,fd=35,pgrp=1,timeout=0,minproto=5,maxproto=5,direct,pipe_ino=6702
29 41 0:23 / /dev/mqueue rw,nosuid,nodev,noexec,relatime shared:15 - mqueue mqueue rw
30 41 0:35 / /dev/hugepages rw,nosuid,nodev,relatime shared:16 - hugetlbfs hugetlbfs rw,pagesize=2M
31 44 0:9 / /sys/kernel/debug rw,nosuid,nodev,noexec,relatime shared:17 - debugfs debugfs rw
32 48 0:36 / /tmp rw,nosuid,nodev shared:18 - tmpfs tmpfs rw,size=486792k,nr_inodes=1048576,inode64,usrquota
33 44 0:14 / /sys/kernel/tracing rw,nosuid,nodev,noexec,relatime shared:19 - tracefs tracefs rw
36 44 0:38 / /sys/fs/fuse/connections rw,nosuid,nodev,noexec,relatime shared:21 - fusectl fusectl rw
40 48 7:0 / /snap/core18/2999 ro,nodev,relatime shared:87 - squashfs /dev/loop0 ro,errors=continue,threads=single
55 48 7:1 / /snap/oracle-cloud-agent/129 ro,nodev,relatime shared:90 - squashfs /dev/loop1 ro,errors=continue,threads=single
61 48 8:13 / /boot rw,relatime shared:96 - ext4 /dev/sda13 rw
64 61 8:15 / /boot/efi rw,relatime shared:99 - vfat /dev/sda15 rw,fmask=0077,dmask=0077,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro
67 28 0:44 / /proc/sys/fs/binfmt_misc rw,nosuid,nodev,noexec,relatime shared:102 - binfmt_misc binfmt_misc rw
71 34 0:45 / /run/rpc_pipefs rw,relatime shared:106 - rpc_pipefs sunrpc rw
123 34 0:56 / /run/credentials/getty@tty1.service rw,nosuid,nodev,noexec,relatime,nosymfollow shared:327 - tmpfs none ro,size=1024k,nr_inodes=1024,mode=700,inode64,noswap
131 34 0:57 / /run/credentials/serial-getty@ttyS0.service rw,nosuid,nodev,noexec,relatime,nosymfollow shared:335 - tmpfs none ro,size=1024k,nr_inodes=1024,mode=700,inode64,noswap
165 48 7:3 / /snap/snapd/27738 ro,nodev,relatime shared:385 - squashfs /dev/loop3 ro,errors=continue,threads=single
84 48 7:4 / /snap/core18/3084 ro,nodev,relatime shared:387 - squashfs /dev/loop4 ro,errors=continue,threads=single
54 48 7:5 / /snap/snapd/28254 ro,nodev,relatime shared:22 - squashfs /dev/loop5 ro,errors=continue,threads=single
37 34 0:37 / /run/credentials/systemd-resolved.service rw,nosuid,nodev,noexec,relatime,nosymfollow shared:20 - tmpfs none ro,size=1024k,nr_inodes=1024,mode=700,inode64,noswap
107 34 0:41 / /run/credentials/systemd-journald.service rw,nosuid,nodev,noexec,relatime,nosymfollow shared:23 - tmpfs none ro,size=1024k,nr_inodes=1024,mode=700,inode64,noswap
39 34 0:53 / /run/credentials/systemd-networkd.service rw,nosuid,nodev,noexec,relatime,nosymfollow shared:392 - tmpfs none ro,size=1024k,nr_inodes=1024,mode=700,inode64,noswap
74 34 0:59 / /run/user/1001 rw,nosuid,nodev,relatime shared:446 - tmpfs tmpfs rw,size=97356k,nr_inodes=24339,mode=700,uid=1001,gid=1001,inode64

````

`c120-hf14-hf15-proc-self-mountinfo.err` (0 bytes)

### `c121-hf14-binfmt-ls`

`c121-hf14-binfmt-ls.cmd` (2230 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' ls /proc/sys/fs/binfmt_misc

````

`c121-hf14-binfmt-ls.out` (440 bytes)

````text
DIR	/proc/sys/fs/binfmt_misc	entries=3
/proc/sys/fs/binfmt_misc/python3.14	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=44	ino=586609	nlink=1	size=0	xattr_names=-
/proc/sys/fs/binfmt_misc/register	present	reg	uid=0	gid=0	owner=root	group=root	mode=0200	dev=44	ino=3	nlink=1	size=0	xattr_names=-
/proc/sys/fs/binfmt_misc/status	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=44	ino=2	nlink=1	size=0	xattr_names=-

````

`c121-hf14-binfmt-ls.err` (0 bytes)

### `c122-hf14-read-python3.14`

`c122-hf14-read-python3.14.cmd` (52 bytes)

````text
/usr/bin/cat -- /proc/sys/fs/binfmt_misc/python3.14

````

`c122-hf14-read-python3.14.out` (72 bytes)

````text
enabled
interpreter /usr/bin/python3.14
flags: 
offset 0
magic 2b0e0d0a

````

`c122-hf14-read-python3.14.err` (0 bytes)

### `c123-hf14-read-status`

`c123-hf14-read-status.cmd` (48 bytes)

````text
/usr/bin/cat -- /proc/sys/fs/binfmt_misc/status

````

`c123-hf14-read-status.out` (8 bytes)

````text
enabled

````

`c123-hf14-read-status.err` (0 bytes)

### `c124-hf15-findmnt-_`

`c124-hf15-findmnt-_.cmd` (63 bytes)

````text
/usr/bin/findmnt --target / -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c124-hf15-findmnt-_.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30

````

`c124-hf15-findmnt-_.err` (0 bytes)

### `c125-hf15-df-_`

`c125-hf15-df-_.cmd` (98 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /

````

`c125-hf15-df-_.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7560836 38590484  17% 5707520 253540 5453980 /

````

`c125-hf15-df-_.err` (0 bytes)

### `c126-hf15-findmnt-_usr_local`

`c126-hf15-findmnt-_usr_local.cmd` (72 bytes)

````text
/usr/bin/findmnt --target /usr/local -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c126-hf15-findmnt-_usr_local.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30

````

`c126-hf15-findmnt-_usr_local.err` (0 bytes)

### `c127-hf15-df-_usr_local`

`c127-hf15-df-_usr_local.cmd` (107 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /usr/local

````

`c127-hf15-df-_usr_local.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7560860 38590460  17% 5707520 253548 5453972 /

````

`c127-hf15-df-_usr_local.err` (0 bytes)

### `c128-hf15-findmnt-_usr_local_libexec`

`c128-hf15-findmnt-_usr_local_libexec.cmd` (80 bytes)

````text
/usr/bin/findmnt --target /usr/local/libexec -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c128-hf15-findmnt-_usr_local_libexec.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30

````

`c128-hf15-findmnt-_usr_local_libexec.err` (0 bytes)

### `c129-hf15-df-_usr_local_libexec`

`c129-hf15-df-_usr_local_libexec.cmd` (115 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /usr/local/libexec

````

`c129-hf15-df-_usr_local_libexec.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7560884 38590436  17% 5707520 253556 5453964 /

````

`c129-hf15-df-_usr_local_libexec.err` (0 bytes)

### `c130-hf15-findmnt-_etc`

`c130-hf15-findmnt-_etc.cmd` (66 bytes)

````text
/usr/bin/findmnt --target /etc -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c130-hf15-findmnt-_etc.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30

````

`c130-hf15-findmnt-_etc.err` (0 bytes)

### `c131-hf15-df-_etc`

`c131-hf15-df-_etc.cmd` (101 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /etc

````

`c131-hf15-df-_etc.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7560908 38590412  17% 5707520 253564 5453956 /

````

`c131-hf15-df-_etc.err` (0 bytes)

### `c132-hf15-findmnt-_etc_systemd_system`

`c132-hf15-findmnt-_etc_systemd_system.cmd` (81 bytes)

````text
/usr/bin/findmnt --target /etc/systemd/system -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c132-hf15-findmnt-_etc_systemd_system.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30

````

`c132-hf15-findmnt-_etc_systemd_system.err` (0 bytes)

### `c133-hf15-df-_etc_systemd_system`

`c133-hf15-df-_etc_systemd_system.cmd` (116 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /etc/systemd/system

````

`c133-hf15-df-_etc_systemd_system.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7560932 38590388  17% 5707520 253572 5453948 /

````

`c133-hf15-df-_etc_systemd_system.err` (0 bytes)

### `c134-hf15-findmnt-_etc_polkit-1_rules.d`

`c134-hf15-findmnt-_etc_polkit-1_rules.d.cmd` (83 bytes)

````text
/usr/bin/findmnt --target /etc/polkit-1/rules.d -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c134-hf15-findmnt-_etc_polkit-1_rules.d.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30

````

`c134-hf15-findmnt-_etc_polkit-1_rules.d.err` (0 bytes)

### `c135-hf15-df-_etc_polkit-1_rules.d`

`c135-hf15-df-_etc_polkit-1_rules.d.cmd` (118 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /etc/polkit-1/rules.d

````

`c135-hf15-df-_etc_polkit-1_rules.d.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7560956 38590364  17% 5707520 253580 5453940 /

````

`c135-hf15-df-_etc_polkit-1_rules.d.err` (0 bytes)

### `c136-hf15-findmnt-_var_lib`

`c136-hf15-findmnt-_var_lib.cmd` (70 bytes)

````text
/usr/bin/findmnt --target /var/lib -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c136-hf15-findmnt-_var_lib.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30

````

`c136-hf15-findmnt-_var_lib.err` (0 bytes)

### `c137-hf15-df-_var_lib`

`c137-hf15-df-_var_lib.cmd` (105 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /var/lib

````

`c137-hf15-df-_var_lib.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7560980 38590340  17% 5707520 253588 5453932 /

````

`c137-hf15-df-_var_lib.err` (0 bytes)

### `c138-hf15-findmnt-_var_tmp`

`c138-hf15-findmnt-_var_tmp.cmd` (70 bytes)

````text
/usr/bin/findmnt --target /var/tmp -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c138-hf15-findmnt-_var_tmp.out` (104 bytes)

````text
TARGET SOURCE    FSTYPE OPTIONS
/      /dev/sda1 ext4   rw,relatime,discard,errors=remount-ro,commit=30

````

`c138-hf15-findmnt-_var_tmp.err` (0 bytes)

### `c139-hf15-df-_var_tmp`

`c139-hf15-df-_var_tmp.cmd` (105 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /var/tmp

````

`c139-hf15-df-_var_tmp.out` (163 bytes)

````text
Filesystem     Type 1K-blocks    Used    Avail Use%  Inodes  IUsed   IFree Mounted on
/dev/sda1      ext4  46167704 7561004 38590316  17% 5707520 253596 5453924 /

````

`c139-hf15-df-_var_tmp.err` (0 bytes)

### `c140-hf15-findmnt-_run`

`c140-hf15-findmnt-_run.cmd` (66 bytes)

````text
/usr/bin/findmnt --target /run -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c140-hf15-findmnt-_run.out` (113 bytes)

````text
TARGET SOURCE FSTYPE OPTIONS
/run   tmpfs  tmpfs  rw,nosuid,nodev,size=194716k,nr_inodes=819200,mode=755,inode64

````

`c140-hf15-findmnt-_run.err` (0 bytes)

### `c141-hf15-df-_run`

`c141-hf15-df-_run.cmd` (101 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /run

````

`c141-hf15-df-_run.out` (154 bytes)

````text
Filesystem     Type  1K-blocks  Used  Avail Use% Inodes IUsed  IFree Mounted on
tmpfs          tmpfs    194716  1100 193616   1% 819200   911 818289 /run

````

`c141-hf15-df-_run.err` (0 bytes)

### `c142-hf15-findmnt-_run_polkit-1`

`c142-hf15-findmnt-_run_polkit-1.cmd` (75 bytes)

````text
/usr/bin/findmnt --target /run/polkit-1 -o TARGET\,SOURCE\,FSTYPE\,OPTIONS

````

`c142-hf15-findmnt-_run_polkit-1.out` (0 bytes)

`c142-hf15-findmnt-_run_polkit-1.err` (0 bytes)

### `c143-hf15-df-_run_polkit-1`

`c143-hf15-df-_run_polkit-1.cmd` (110 bytes)

````text
/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /run/polkit-1

````

`c143-hf15-df-_run_polkit-1.out` (0 bytes)

`c143-hf15-df-_run_polkit-1.err` (45 bytes)

````text
df: /run/polkit-1: No such file or directory

````

### `c144-hf16-manager-defaults`

`c144-hf16-manager-defaults.cmd` (1392 bytes)

````text
/usr/bin/systemctl --no-pager show -p Version -p DefaultStandardOutput -p DefaultStandardError -p DefaultTimerAccuracyUSec -p DefaultTimeoutStartUSec -p DefaultTimeoutStopUSec -p DefaultTimeoutAbortUSec -p DefaultDeviceTimeoutUSec -p DefaultRestartUSec -p DefaultStartLimitIntervalUSec -p DefaultStartLimitBurst -p DefaultCPUAccounting -p DefaultBlockIOAccounting -p DefaultIOAccounting -p DefaultIPAccounting -p DefaultMemoryAccounting -p DefaultTasksAccounting -p DefaultTasksMax -p DefaultLimitCPU -p DefaultLimitCPUSoft -p DefaultLimitFSIZE -p DefaultLimitFSIZESoft -p DefaultLimitDATA -p DefaultLimitDATASoft -p DefaultLimitSTACK -p DefaultLimitSTACKSoft -p DefaultLimitCORE -p DefaultLimitCORESoft -p DefaultLimitRSS -p DefaultLimitRSSSoft -p DefaultLimitNOFILE -p DefaultLimitNOFILESoft -p DefaultLimitAS -p DefaultLimitASSoft -p DefaultLimitNPROC -p DefaultLimitNPROCSoft -p DefaultLimitMEMLOCK -p DefaultLimitMEMLOCKSoft -p DefaultLimitLOCKS -p DefaultLimitLOCKSSoft -p DefaultLimitSIGPENDING -p DefaultLimitSIGPENDINGSoft -p DefaultLimitMSGQUEUE -p DefaultLimitMSGQUEUESoft -p DefaultLimitNICE -p DefaultLimitNICESoft -p DefaultLimitRTPRIO -p DefaultLimitRTPRIOSoft -p DefaultLimitRTTIME -p DefaultLimitRTTIMESoft -p DefaultOOMPolicy -p DefaultOOMScoreAdjust -p DefaultMemoryPressureWatch -p DefaultMemoryPressureThresholdUSec -p DefaultSmackProcessLabel -p DefaultRestrictSUIDSGID

````

`c144-hf16-manager-defaults.out` (1468 bytes)

````text
Version=259.5-0ubuntu3.4
DefaultStandardOutput=journal
DefaultStandardError=inherit
DefaultTimerAccuracyUSec=1min
DefaultTimeoutStartUSec=1min 30s
DefaultTimeoutStopUSec=1min 30s
DefaultTimeoutAbortUSec=1min 30s
DefaultDeviceTimeoutUSec=1min 30s
DefaultRestartUSec=100ms
DefaultStartLimitIntervalUSec=10s
DefaultStartLimitBurst=5
DefaultIOAccounting=no
DefaultIPAccounting=no
DefaultMemoryAccounting=yes
DefaultTasksAccounting=yes
DefaultLimitCPU=infinity
DefaultLimitCPUSoft=infinity
DefaultLimitFSIZE=infinity
DefaultLimitFSIZESoft=infinity
DefaultLimitDATA=infinity
DefaultLimitDATASoft=infinity
DefaultLimitSTACK=infinity
DefaultLimitSTACKSoft=8388608
DefaultLimitCORE=infinity
DefaultLimitCORESoft=0
DefaultLimitRSS=infinity
DefaultLimitRSSSoft=infinity
DefaultLimitNOFILE=524288
DefaultLimitNOFILESoft=1024
DefaultLimitAS=infinity
DefaultLimitASSoft=infinity
DefaultLimitNPROC=3354
DefaultLimitNPROCSoft=3354
DefaultLimitMEMLOCK=8388608
DefaultLimitMEMLOCKSoft=8388608
DefaultLimitLOCKS=infinity
DefaultLimitLOCKSSoft=infinity
DefaultLimitSIGPENDING=3354
DefaultLimitSIGPENDINGSoft=3354
DefaultLimitMSGQUEUE=819200
DefaultLimitMSGQUEUESoft=819200
DefaultLimitNICE=0
DefaultLimitNICESoft=0
DefaultLimitRTPRIO=0
DefaultLimitRTPRIOSoft=0
DefaultLimitRTTIME=infinity
DefaultLimitRTTIMESoft=infinity
DefaultTasksMax=1006
DefaultMemoryPressureThresholdUSec=200ms
DefaultMemoryPressureWatch=auto
DefaultOOMPolicy=stop
DefaultOOMScoreAdjust=0
DefaultRestrictSUIDSGID=no

````

`c144-hf16-manager-defaults.err` (0 bytes)

### `c145-hf17-list-timers`

`c145-hf17-list-timers.cmd` (60 bytes)

````text
/usr/bin/systemctl --no-pager list-timers --all --no-legend

````

`c145-hf17-list-timers.out` (2577 bytes)

````text
Tue 2026-10-06 02:50:00 UTC      18s Tue 2026-10-06 02:40:03 UTC         9min ago sysstat-collect.timer          sysstat-collect.service
Tue 2026-10-06 03:24:53 UTC    35min Tue 2026-10-06 02:01:25 UTC        48min ago fwupd-refresh.timer            fwupd-refresh.service
Tue 2026-10-06 03:38:07 UTC    48min Mon 2026-10-05 13:00:31 UTC          13h ago apt-daily.timer                apt-daily.service
Tue 2026-10-06 04:18:05 UTC 1h 28min Mon 2026-10-05 07:15:48 UTC          19h ago man-db.timer                   man-db.service
Tue 2026-10-06 06:12:05 UTC 3h 22min Mon 2026-10-05 06:35:31 UTC          20h ago apt-daily-upgrade.timer        apt-daily-upgrade.service
Tue 2026-10-06 09:40:20 UTC       6h Mon 2026-10-05 13:39:25 UTC          13h ago motd-news.timer                motd-news.service
Tue 2026-10-06 23:10:33 UTC      20h Mon 2026-10-05 23:10:33 UTC     3h 39min ago update-notifier-download.timer update-notifier-download.service
Tue 2026-10-06 23:21:18 UTC      20h Mon 2026-10-05 23:21:18 UTC     3h 28min ago systemd-tmpfiles-clean.timer   systemd-tmpfiles-clean.service
Wed 2026-10-07 00:00:00 UTC      21h Tue 2026-10-06 00:00:25 UTC     2h 49min ago dpkg-db-backup.timer           dpkg-db-backup.service
Wed 2026-10-07 00:00:00 UTC      21h Tue 2026-10-06 00:00:25 UTC     2h 49min ago sysstat-rotate.timer           sysstat-rotate.service
Wed 2026-10-07 00:07:00 UTC      21h Tue 2026-10-06 00:07:25 UTC     2h 42min ago sysstat-summary.timer          sysstat-summary.service
Wed 2026-10-07 00:24:20 UTC      21h Tue 2026-10-06 00:21:56 UTC     2h 27min ago logrotate.timer                logrotate.service
Wed 2026-10-07 08:24:59 UTC 1 day 5h Sun 2026-09-27 08:00:19 UTC 1 week 1 day ago update-notifier-motd.timer     update-notifier-motd.service
Sun 2026-10-11 03:10:18 UTC   5 days Sun 2026-10-04 03:10:25 UTC    1 day 23h ago e2scrub_all.timer              e2scrub_all.service
Sun 2026-10-11 03:10:50 UTC   5 days Sun 2026-10-04 03:10:31 UTC    1 day 23h ago xfs_scrub_all.timer            xfs_scrub_all.service
Mon 2026-10-12 00:45:55 UTC   5 days Mon 2026-10-05 01:09:57 UTC     1 day 1h ago fstrim.timer                   fstrim.service
-                                  - -                                          - apport-autoreport.timer        apport-autoreport.service
-                                  - -                                          - snapd.snap-repair.timer        snapd.snap-repair.service
-                                  - -                                          - ua-timer.timer                 ua-timer.service

````

`c145-hf17-list-timers.err` (0 bytes)

### `c146-hf17-update-units-show`

`c146-hf17-update-units-show.cmd` (166 bytes)

````text
/usr/bin/systemctl --no-pager show apt-daily.timer apt-daily-upgrade.timer unattended-upgrades.service -p Id -p LoadState -p ActiveState -p SubState -p UnitFileState

````

`c146-hf17-update-units-show.out` (304 bytes)

````text
Id=apt-daily.timer
LoadState=loaded
ActiveState=active
SubState=waiting
UnitFileState=enabled

Id=apt-daily-upgrade.timer
LoadState=loaded
ActiveState=active
SubState=waiting
UnitFileState=enabled

Id=unattended-upgrades.service
LoadState=loaded
ActiveState=active
SubState=running
UnitFileState=enabled

````

`c146-hf17-update-units-show.err` (0 bytes)

### `c147-hf19-tmpfiles-dirs-ls`

`c147-hf19-tmpfiles-dirs-ls.cmd` (2283 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' ls /etc/tmpfiles.d /run/tmpfiles.d /usr/local/lib/tmpfiles.d /usr/lib/tmpfiles.d

````

`c147-hf19-tmpfiles-dirs-ls.out` (6648 bytes)

````text
DIR	/etc/tmpfiles.d	entries=2
/etc/tmpfiles.d/freedom-blades-laboratory.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=1898	nlink=1	size=106	xattr_names=-
/etc/tmpfiles.d/screen-cleanup.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=177	nlink=1	size=119	xattr_names=-
DIR	/run/tmpfiles.d	entries=1
/run/tmpfiles.d/static-nodes.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=29	ino=60	nlink=1	size=507	xattr_names=-
DIR	/usr/local/lib/tmpfiles.d	absent
DIR	/usr/lib/tmpfiles.d	entries=43
/usr/lib/tmpfiles.d/00rsyslog.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=6525	nlink=1	size=465	xattr_names=-
/usr/lib/tmpfiles.d/20-systemd-osc-context.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8178	nlink=1	size=431	xattr_names=-
/usr/lib/tmpfiles.d/20-systemd-shell-extra.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8179	nlink=1	size=431	xattr_names=-
/usr/lib/tmpfiles.d/20-systemd-ssh-generator.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8180	nlink=1	size=458	xattr_names=-
/usr/lib/tmpfiles.d/20-systemd-stub.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8181	nlink=1	size=779	xattr_names=-
/usr/lib/tmpfiles.d/apport.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8202	nlink=1	size=80	xattr_names=-
/usr/lib/tmpfiles.d/credstore.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8182	nlink=1	size=474	xattr_names=-
/usr/lib/tmpfiles.d/cron-daemon-common.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8177	nlink=1	size=45	xattr_names=-
/usr/lib/tmpfiles.d/cryptsetup.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8205	nlink=1	size=35	xattr_names=-
/usr/lib/tmpfiles.d/dbus.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8196	nlink=1	size=365	xattr_names=-
/usr/lib/tmpfiles.d/debian.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8183	nlink=1	size=726	xattr_names=-
/usr/lib/tmpfiles.d/home.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8184	nlink=1	size=363	xattr_names=-
/usr/lib/tmpfiles.d/journal-nocow.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8185	nlink=1	size=1097	xattr_names=-
/usr/lib/tmpfiles.d/legacy.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8186	nlink=1	size=795	xattr_names=-
/usr/lib/tmpfiles.d/libselinux1.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8175	nlink=1	size=112	xattr_names=-
/usr/lib/tmpfiles.d/lvm2.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8208	nlink=1	size=61	xattr_names=-
/usr/lib/tmpfiles.d/man-db.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8200	nlink=1	size=85	xattr_names=-
/usr/lib/tmpfiles.d/multipath.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8207	nlink=1	size=34	xattr_names=-
/usr/lib/tmpfiles.d/openssh-client.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=58621	nlink=1	size=13	xattr_names=-
/usr/lib/tmpfiles.d/openssh-server.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=58606	nlink=1	size=17	xattr_names=-
/usr/lib/tmpfiles.d/passwd.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8176	nlink=1	size=239	xattr_names=-
/usr/lib/tmpfiles.d/polkit-tmpfiles.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=22545	nlink=1	size=268	xattr_names=-
/usr/lib/tmpfiles.d/postgresql-common.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=43175	nlink=1	size=172	xattr_names=-
/usr/lib/tmpfiles.d/provision.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8187	nlink=1	size=852	xattr_names=-
/usr/lib/tmpfiles.d/rpcbind.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=42416	nlink=1	size=78	xattr_names=-
/usr/lib/tmpfiles.d/screen-cleanup.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8199	nlink=1	size=29	xattr_names=-
/usr/lib/tmpfiles.d/snapd.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=35609	nlink=1	size=260	xattr_names=-
/usr/lib/tmpfiles.d/static-nodes-permissions.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8172	nlink=1	size=798	xattr_names=-
/usr/lib/tmpfiles.d/sudo.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=6714	nlink=1	size=27	xattr_names=-
/usr/lib/tmpfiles.d/systemd-network.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8188	nlink=1	size=598	xattr_names=-
/usr/lib/tmpfiles.d/systemd-nologin.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8189	nlink=1	size=538	xattr_names=-
/usr/lib/tmpfiles.d/systemd-pstore.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8190	nlink=1	size=1512	xattr_names=-
/usr/lib/tmpfiles.d/systemd-resolve.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8174	nlink=1	size=394	xattr_names=-
/usr/lib/tmpfiles.d/systemd-tmp.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8191	nlink=1	size=824	xattr_names=-
/usr/lib/tmpfiles.d/systemd.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8192	nlink=1	size=1740	xattr_names=-
/usr/lib/tmpfiles.d/tmp.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8193	nlink=1	size=450	xattr_names=-
/usr/lib/tmpfiles.d/tmux.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8206	nlink=1	size=14	xattr_names=-
/usr/lib/tmpfiles.d/tpm-udev.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8203	nlink=1	size=139	xattr_names=-
/usr/lib/tmpfiles.d/tpm2-tss-fapi.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8204	nlink=1	size=592	xattr_names=-
/usr/lib/tmpfiles.d/udisks2.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=58727	nlink=1	size=28	xattr_names=-
/usr/lib/tmpfiles.d/uuidd-tmpfiles.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=2108	nlink=1	size=136	xattr_names=-
/usr/lib/tmpfiles.d/var.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8194	nlink=1	size=467	xattr_names=-
/usr/lib/tmpfiles.d/x11.conf	present	reg	uid=0	gid=0	owner=root	group=root	mode=0644	dev=2049	ino=8195	nlink=1	size=618	xattr_names=-

````

`c147-hf19-tmpfiles-dirs-ls.err` (0 bytes)

### `c148-hf19-tmp-conf-sha256`

`c148-hf19-tmp-conf-sha256.cmd` (51 bytes)

````text
/usr/bin/sha256sum -- /usr/lib/tmpfiles.d/tmp.conf

````

`c148-hf19-tmp-conf-sha256.out` (95 bytes)

````text
a1dae3c409fab42c6e48d93ad36364cd6b35ac4705488f1e91b8593ef41ea931  /usr/lib/tmpfiles.d/tmp.conf

````

`c148-hf19-tmp-conf-sha256.err` (0 bytes)

### `c149-hf19-tmpfiles-sha256`

`c149-hf19-tmpfiles-sha256.cmd` (1716 bytes)

````text
/usr/bin/sha256sum -- /etc/tmpfiles.d/freedom-blades-laboratory.conf /etc/tmpfiles.d/screen-cleanup.conf /run/tmpfiles.d/static-nodes.conf /usr/lib/tmpfiles.d/00rsyslog.conf /usr/lib/tmpfiles.d/20-systemd-osc-context.conf /usr/lib/tmpfiles.d/20-systemd-shell-extra.conf /usr/lib/tmpfiles.d/20-systemd-ssh-generator.conf /usr/lib/tmpfiles.d/20-systemd-stub.conf /usr/lib/tmpfiles.d/apport.conf /usr/lib/tmpfiles.d/credstore.conf /usr/lib/tmpfiles.d/cron-daemon-common.conf /usr/lib/tmpfiles.d/cryptsetup.conf /usr/lib/tmpfiles.d/dbus.conf /usr/lib/tmpfiles.d/debian.conf /usr/lib/tmpfiles.d/home.conf /usr/lib/tmpfiles.d/journal-nocow.conf /usr/lib/tmpfiles.d/legacy.conf /usr/lib/tmpfiles.d/libselinux1.conf /usr/lib/tmpfiles.d/lvm2.conf /usr/lib/tmpfiles.d/man-db.conf /usr/lib/tmpfiles.d/multipath.conf /usr/lib/tmpfiles.d/openssh-client.conf /usr/lib/tmpfiles.d/openssh-server.conf /usr/lib/tmpfiles.d/passwd.conf /usr/lib/tmpfiles.d/polkit-tmpfiles.conf /usr/lib/tmpfiles.d/postgresql-common.conf /usr/lib/tmpfiles.d/provision.conf /usr/lib/tmpfiles.d/rpcbind.conf /usr/lib/tmpfiles.d/screen-cleanup.conf /usr/lib/tmpfiles.d/snapd.conf /usr/lib/tmpfiles.d/static-nodes-permissions.conf /usr/lib/tmpfiles.d/sudo.conf /usr/lib/tmpfiles.d/systemd-network.conf /usr/lib/tmpfiles.d/systemd-nologin.conf /usr/lib/tmpfiles.d/systemd-pstore.conf /usr/lib/tmpfiles.d/systemd-resolve.conf /usr/lib/tmpfiles.d/systemd-tmp.conf /usr/lib/tmpfiles.d/systemd.conf /usr/lib/tmpfiles.d/tmp.conf /usr/lib/tmpfiles.d/tmux.conf /usr/lib/tmpfiles.d/tpm-udev.conf /usr/lib/tmpfiles.d/tpm2-tss-fapi.conf /usr/lib/tmpfiles.d/udisks2.conf /usr/lib/tmpfiles.d/uuidd-tmpfiles.conf /usr/lib/tmpfiles.d/var.conf /usr/lib/tmpfiles.d/x11.conf

````

`c149-hf19-tmpfiles-sha256.out` (4730 bytes)

````text
042f193d50fb102afe789799a5e100b1e685ea3cdf0661ca8433038e76aebacf  /etc/tmpfiles.d/freedom-blades-laboratory.conf
b01ca3262f1ac0b97486dce16c9e932d684279ea98cd4a8bddd0c849cf4123da  /etc/tmpfiles.d/screen-cleanup.conf
045b40668255ddd32d1534a04026937f570dee6d7568c335697d0ef7eeefa542  /run/tmpfiles.d/static-nodes.conf
162fd61f2197334db713d1fea8bc36fc4fca78a4c13c4393451280742b7cc19f  /usr/lib/tmpfiles.d/00rsyslog.conf
8052bc32765fa96b831d414256e5d9c8369c185bc61d10fb4088d6871cba3ffb  /usr/lib/tmpfiles.d/20-systemd-osc-context.conf
2239913f1b4d343818aef1ba684219c46c3e291c89b1cf2dec1bb2f5e1ff29f6  /usr/lib/tmpfiles.d/20-systemd-shell-extra.conf
2e88fa5994e730a51a6a11d11ba4c394035cf1625dd1656bf88adec091236a0b  /usr/lib/tmpfiles.d/20-systemd-ssh-generator.conf
86f8ba2ce3c7a56aad8e8f4fae0998a4920b34ff3f62e5ce727b3b797a99c715  /usr/lib/tmpfiles.d/20-systemd-stub.conf
08d27fbf46bc836d374adf5c2623b43d053c3736aca35457a63d3f15290a708f  /usr/lib/tmpfiles.d/apport.conf
2bafed09323dcb75c9c59ffd863510c2d05b6939fbcda267a82198875d1b4ddb  /usr/lib/tmpfiles.d/credstore.conf
f71fe381e57ef0980cb256000c25e20fdd798cf0d5d0da712dbc8bd998c5cf72  /usr/lib/tmpfiles.d/cron-daemon-common.conf
d6bb4b689200c2348945700a6b0dad5df92bc2015860d15f36a25590814d77b0  /usr/lib/tmpfiles.d/cryptsetup.conf
d1b15f34a0590f6535dbff91727dd6bbf10752e8abb2cab73fa66a6184f9df1a  /usr/lib/tmpfiles.d/dbus.conf
7535c23784ea5b81b6d8d8841e1b4ee17ebaac094e38f23f003ecdef454efb8c  /usr/lib/tmpfiles.d/debian.conf
fcc7434662a40ed081eec2c608dd1a3ac8c909440359a7890c08175fb685ff68  /usr/lib/tmpfiles.d/home.conf
b0cfe7fb70a62747fd4002a8c5945f7b2a1784a7b482e65da6512987d0ba307d  /usr/lib/tmpfiles.d/journal-nocow.conf
c353525a3c1b4d88e0681bd3ce73806946dbf7f7bf54e2be6d620f450f78181a  /usr/lib/tmpfiles.d/legacy.conf
bb7c285a572a99cd0691bc27fb7754b0f696563dc0e954f039e6d9a5cef761f6  /usr/lib/tmpfiles.d/libselinux1.conf
670a21702d32d3a14a15494d8419aea5f2de9ca058ba9da46dd951492cf18411  /usr/lib/tmpfiles.d/lvm2.conf
e490f1f7e88b0e24491ddcb88c6e5780f71c37d06e11b9954f6d718a562d50df  /usr/lib/tmpfiles.d/man-db.conf
7fe3d6ba763cc9a45e8895b134b7759c27fb51509b9eea0c5f09b85d4391f38a  /usr/lib/tmpfiles.d/multipath.conf
b424e86e7fe590f50a5e7c2a83bb760335ee60ebb69beb2834d7cdf6ec36b1ae  /usr/lib/tmpfiles.d/openssh-client.conf
7c3984cb99bc2b6a74508fe3aa8177913865bd3491d0ad4e965b4068eb289a08  /usr/lib/tmpfiles.d/openssh-server.conf
1a3b927102b44454eb4c47e4fe659de2f5283f364ba27408329a54d4ad47e310  /usr/lib/tmpfiles.d/passwd.conf
50f4e9c849bee5120546109b288ff7a631004dd2a7bfb27062181aa684b517c2  /usr/lib/tmpfiles.d/polkit-tmpfiles.conf
f36602325dfaab59771198e50290e5d01d48e5757cacabc0aea2b92f360574d9  /usr/lib/tmpfiles.d/postgresql-common.conf
dbb85f57c2e24e703d2cc103b21634a4b53aa4d0f58dac59af74a3f12cddc73a  /usr/lib/tmpfiles.d/provision.conf
5640eda8a4437d18420fdb5f67cd96c39b2604545bd097fb5378388720ce52d8  /usr/lib/tmpfiles.d/rpcbind.conf
0250534a2cb7f9f81897e18b59deacbbb9d15d81c7551180ace35d95acbb4ee4  /usr/lib/tmpfiles.d/screen-cleanup.conf
0973f9f4204fbc4d87c719c6c26abf4816326b880f7cff06b20d8c2e4bbdede1  /usr/lib/tmpfiles.d/snapd.conf
ca4849c27428fd648f6377dd51a3ab0eb79de69fce1bdc910670012c0cf26f85  /usr/lib/tmpfiles.d/static-nodes-permissions.conf
eed7eb9d7ddaccb3ae13d3225de1302a96754938fea4dc305c43b64cbcb5d0bc  /usr/lib/tmpfiles.d/sudo.conf
4e60ef3d3cc3466ebab75561d70f6e58b7e22cc0a2b7e7e3dfbd083d24b988b6  /usr/lib/tmpfiles.d/systemd-network.conf
b97c3f92a569dd84957eb263f3438cc7d98ea2a4ffe5f5e9d090c04d14b725b9  /usr/lib/tmpfiles.d/systemd-nologin.conf
cdb3efb34ea12ef62140dc86ffbe90045729f3e8227698848e44bed4fdd5fe2f  /usr/lib/tmpfiles.d/systemd-pstore.conf
12e573ce01b47cde7cf7867a74d0ca04152fb083962a9ae5ba4989eb305a84ca  /usr/lib/tmpfiles.d/systemd-resolve.conf
224e8d4145ed4a049d7a0ffb7c7d20f5278c60f08eff6369f4e82f2397abc2bc  /usr/lib/tmpfiles.d/systemd-tmp.conf
17906b482927ed65b48239f6dc8b7e555a76a75dec76a67925e60764d3f93bbc  /usr/lib/tmpfiles.d/systemd.conf
a1dae3c409fab42c6e48d93ad36364cd6b35ac4705488f1e91b8593ef41ea931  /usr/lib/tmpfiles.d/tmp.conf
487851edcd733dd3113f3953f0bab604b32f140b127682970d2cc5c24aa61c03  /usr/lib/tmpfiles.d/tmux.conf
d35655572bb844cf6bd2d5330ca91fd298e90f76a90c675f2d935163a2690e49  /usr/lib/tmpfiles.d/tpm-udev.conf
ff0b4a047763274e93a1773d0a95c5078c9e0010e1df06461d7fa6dfee807c15  /usr/lib/tmpfiles.d/tpm2-tss-fapi.conf
27a7496ddf7e465995059a0410d47387b9e82ccd7aac9c3763f2ac6659ca9c21  /usr/lib/tmpfiles.d/udisks2.conf
9a96f64c463d613e2733f6fd91e9a515bdbf3ff690abe18356f4fa1a6366d67b  /usr/lib/tmpfiles.d/uuidd-tmpfiles.conf
87ee9655436403e91489d3f19ef01b70528539ac76b65435bedd7dc02db4df0e  /usr/lib/tmpfiles.d/var.conf
e541aecc6303f5a3d7027f85307380b0114fad977346c2106585c8cffaf7854e  /usr/lib/tmpfiles.d/x11.conf

````

`c149-hf19-tmpfiles-sha256.err` (0 bytes)

### `c150-hf19-tmpfiles-lines`

`c150-hf19-tmpfiles-lines.cmd` (1770 bytes)

````text
/usr/bin/grep -n -H -E /var/tmp\|/run/polkit-1\|/run/freedom-blades-rp11 -- /etc/tmpfiles.d/freedom-blades-laboratory.conf /etc/tmpfiles.d/screen-cleanup.conf /run/tmpfiles.d/static-nodes.conf /usr/lib/tmpfiles.d/00rsyslog.conf /usr/lib/tmpfiles.d/20-systemd-osc-context.conf /usr/lib/tmpfiles.d/20-systemd-shell-extra.conf /usr/lib/tmpfiles.d/20-systemd-ssh-generator.conf /usr/lib/tmpfiles.d/20-systemd-stub.conf /usr/lib/tmpfiles.d/apport.conf /usr/lib/tmpfiles.d/credstore.conf /usr/lib/tmpfiles.d/cron-daemon-common.conf /usr/lib/tmpfiles.d/cryptsetup.conf /usr/lib/tmpfiles.d/dbus.conf /usr/lib/tmpfiles.d/debian.conf /usr/lib/tmpfiles.d/home.conf /usr/lib/tmpfiles.d/journal-nocow.conf /usr/lib/tmpfiles.d/legacy.conf /usr/lib/tmpfiles.d/libselinux1.conf /usr/lib/tmpfiles.d/lvm2.conf /usr/lib/tmpfiles.d/man-db.conf /usr/lib/tmpfiles.d/multipath.conf /usr/lib/tmpfiles.d/openssh-client.conf /usr/lib/tmpfiles.d/openssh-server.conf /usr/lib/tmpfiles.d/passwd.conf /usr/lib/tmpfiles.d/polkit-tmpfiles.conf /usr/lib/tmpfiles.d/postgresql-common.conf /usr/lib/tmpfiles.d/provision.conf /usr/lib/tmpfiles.d/rpcbind.conf /usr/lib/tmpfiles.d/screen-cleanup.conf /usr/lib/tmpfiles.d/snapd.conf /usr/lib/tmpfiles.d/static-nodes-permissions.conf /usr/lib/tmpfiles.d/sudo.conf /usr/lib/tmpfiles.d/systemd-network.conf /usr/lib/tmpfiles.d/systemd-nologin.conf /usr/lib/tmpfiles.d/systemd-pstore.conf /usr/lib/tmpfiles.d/systemd-resolve.conf /usr/lib/tmpfiles.d/systemd-tmp.conf /usr/lib/tmpfiles.d/systemd.conf /usr/lib/tmpfiles.d/tmp.conf /usr/lib/tmpfiles.d/tmux.conf /usr/lib/tmpfiles.d/tpm-udev.conf /usr/lib/tmpfiles.d/tpm2-tss-fapi.conf /usr/lib/tmpfiles.d/udisks2.conf /usr/lib/tmpfiles.d/uuidd-tmpfiles.conf /usr/lib/tmpfiles.d/var.conf /usr/lib/tmpfiles.d/x11.conf

````

`c150-hf19-tmpfiles-lines.out` (280 bytes)

````text
/usr/lib/tmpfiles.d/systemd-tmp.conf:13:x /var/tmp/systemd-private-%b-*
/usr/lib/tmpfiles.d/systemd-tmp.conf:14:X /var/tmp/systemd-private-%b-*/tmp
/usr/lib/tmpfiles.d/systemd-tmp.conf:18:R! /var/tmp/systemd-private-*
/usr/lib/tmpfiles.d/tmp.conf:12:q /var/tmp 1777 root root 30d

````

`c150-hf19-tmpfiles-lines.err` (0 bytes)

### `c151-hf20-soft-reboot-loadstate`

`c151-hf20-soft-reboot-loadstate.cmd` (101 bytes)

````text
/usr/bin/systemctl --no-pager show systemd-soft-reboot.service soft-reboot.target -p Id -p LoadState

````

`c151-hf20-soft-reboot-loadstate.out` (88 bytes)

````text
Id=systemd-soft-reboot.service
LoadState=loaded

Id=soft-reboot.target
LoadState=loaded

````

`c151-hf20-soft-reboot-loadstate.err` (0 bytes)

### `c152-manifest-payload`

`c152-manifest-payload.cmd` (693 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, hashlib\nd = sys.argv[1]\nexcl = sys.argv[2:]\nfor n in sorted(os.listdir(d)):\n    if any(n.startswith(x) for x in excl):\n        continue\n    p = os.path.join(d, n)\n    st = os.lstat(p)\n    if not stat.S_ISREG(st.st_mode):\n        print("NONREGULAR " + n)\n        sys.exit(3)\n    h = hashlib.sha256()\n    size = 0\n    with open(p, "rb") as f:\n        while True:\n            b = f.read(1048576)\n            if not b:\n                break\n            h.update(b)\n            size += len(b)\n    print(h.hexdigest() + "  " + str(size) + "  " + n)\n' /var/tmp/p5-r5-rp11-h0-20261006-02-evidence c152-manifest-payload. MANIFEST.

````

stdout file `MANIFEST.payload` (64132 bytes), reproduced or identified above

`c152-manifest-payload.err` (0 bytes)

### `c153-manifest-final`

`c153-manifest-final.cmd` (261 bytes)

````text
/usr/bin/python3 -I -S -c $'import sys, hashlib\nwith open(sys.argv[1], "rb") as f:\n    b = f.read()\nprint("MANIFEST.payload  sha256=" + hashlib.sha256(b).hexdigest() + "  bytes=" + str(len(b)))\n' /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/MANIFEST.payload

````

stdout file `MANIFEST.final` (103 bytes), reproduced or identified above

`c153-manifest-final.err` (0 bytes)

### `c154-inventory`

`c154-inventory.cmd` (1347 bytes)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\nd, prog, own = sys.argv[1], sys.argv[2], sys.argv[3]\nuid = pwd.getpwnam("ubuntu").pw_uid\ngid = grp.getgrnam("ubuntu").gr_gid\nfloor = os.lstat(prog).st_mtime_ns\nbad = 0\nds = os.lstat(d)\nprint("DIR\\t" + d + "\\tuid=" + str(ds.st_uid) + "\\tgid=" + str(ds.st_gid) + "\\tmode=%04o" % stat.S_IMODE(ds.st_mode))\nfor n in sorted(os.listdir(d)):\n    p = os.path.join(d, n)\n    st = os.lstat(p)\n    ok = (stat.S_ISREG(st.st_mode) and st.st_uid == uid and st.st_gid == gid\n          and stat.S_IMODE(st.st_mode) == 0o600 and st.st_nlink == 1\n          and st.st_mtime_ns >= floor)\n    if not ok:\n        bad += 1\n    note = "own-output-open" if n == own else ""\n    print("\\t".join([n, "reg" if stat.S_ISREG(st.st_mode) else "NONREG",\n                     "owner=" + pwd.getpwuid(st.st_uid)[0], "group=" + grp.getgrgid(st.st_gid)[0],\n                     "mode=%04o" % stat.S_IMODE(st.st_mode), "nlink=" + str(st.st_nlink),\n                     "fresh=" + ("yes" if st.st_mtime_ns >= floor else "NO"),\n                     "ok=" + ("yes" if ok else "NO"), note]).rstrip("\\t"))\nprint("violations=" + str(bad))\nsys.exit(1 if bad else 0)\n' /var/tmp/p5-r5-rp11-h0-20261006-02-evidence /var/tmp/p5-r5-rp11-h0-20261006-02-evidence/controller-h0-program.sh INVENTORY.owner-mode

````

stdout file `INVENTORY.owner-mode` (61987 bytes), reproduced or identified above

`c154-inventory.err` (0 bytes)


H-0 facts await independent Codex review; OH-S2 and every later slice remain unauthorized.
