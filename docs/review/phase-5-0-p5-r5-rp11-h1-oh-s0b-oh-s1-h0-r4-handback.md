# Handback — R4 isolated-checkout H-0: HARD STOP at retrieval

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R4-20261006-01`

Date: 2026-10-06

Executor: Claude Code (controller in `/opt/freedom-blades/platform`), one
forwarding-disabled SSH execution connection to `oracle-test`.

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-claude-prompt.md)
· Authority: [`project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-authority.md)

## Terminal state: `HARD STOP`

- **Failed step:** Execution step 3, anonymous retrieval. Command
  `c016-git-fetch` exited `128`.
- **Safe error (verbatim stderr, 40 bytes):** `fatal: unable to get password from user`
- **Meaning:** `https://github.com/ming-themerciless/freedom-bot.git` asked
  for HTTP authentication on a credential-free fetch. Git then called the
  configured no-op askpass (`/bin/false`), which returned nothing, so the fetch
  failed. Per the prompt, an authentication request is a HARD STOP. There was
  no retry, fallback, credential use, URL change or SSH transport. GitHub
  answers anonymous requests for a private repository and for a nonexistent one
  in the same way, so the run cannot tell those cases apart.
- **Not reached:** commit verification, detached checkout, `HEAD`/porcelain
  verification, governing-file verification from the pinned tree, retention
  of the R4 prompt/authority copies, and HF-03 through HF-20.

## Smallest follow-up needed

A maintainer must decide how the pinned commit becomes retrievable on
`oracle-test`. There are two options:

1. Confirm or make the canonical repository publicly readable at the fixed URL.
2. Under OH-D-1, separately authorize a read-only credential route with its
   own installation and handling authority.

Either option then needs a new work ID with fresh exclusive paths. The R4
paths below are consumed and retained. This run authorizes no retry.

## Controller command and program

- Program (controller transport, not repository source): SHA-256
  `b9b9f3315d1720735c1287e06671d294322fd3edc8cd6563ab9dfd05a88b9806`,
  40147 bytes. It embeds the R4 prompt and authority as base64 and no
  repository source or implementation file.
- The remote bootstrap verified the same digest and length before execution;
  otherwise it would have exited `72`/`73`. Commands `c001` and `c002`
  recomputed them remotely as
  `b9b9f3315d1720735c1287e06671d294322fd3edc8cd6563ab9dfd05a88b9806`, size
  40147, `ubuntu:ubuntu`, mode `600`, regular file.
- SSH start/end (controller UTC): `2026-10-06T01:10:16.182310414Z` /
  `2026-10-06T01:10:19.581722733Z`. SSH exit status `75`, which is the
  program's HARD STOP code. SSH stderr was exactly
  `HARD STOP at retrieval: anonymous fetch of pinned commit failed (exit 128; see c016-git-fetch.err)`.
  There was no authentication, host-key or transport error at the SSH layer.
- Exact controller command (one invocation; `PROGRAM` was a fresh scratchpad
  file):

```bash
ssh -T -o BatchMode=yes -o ClearAllForwardings=yes -o ForwardAgent=no -o ForwardX11=no -o PermitLocalCommand=no oracle-test "/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /bin/bash --noprofile --norc -c 'set -eu; if ! { test \"\$(/usr/bin/id -ru)\" = \"\$(/usr/bin/id -u ubuntu)\" && test \"\$(/usr/bin/id -u)\" = \"\$(/usr/bin/id -u ubuntu)\" && test \"\$(/usr/bin/id -run)\" = ubuntu && test \"\$(/usr/bin/id -un)\" = ubuntu && test \"\$(/usr/bin/uname -n)\" = Test; }; then /usr/bin/printf \"HARD STOP: remote identity mismatch\\n\" >&2; exit 70; fi; umask 077; evidence=/var/tmp/p5-r5-rp11-h0-20261006-01-evidence; checkout=/var/tmp/p5-r5-rp11-h0-20261006-01-checkout; for p in \"\$evidence\" \"\$checkout\"; do if /usr/bin/test -e \"\$p\" || /usr/bin/test -L \"\$p\"; then /usr/bin/printf \"HARD STOP: exclusive path exists\\n\" >&2; exit 71; fi; done; /usr/bin/mkdir -m 0700 -- \"\$evidence\"; /usr/bin/tee \"\$evidence/controller-h0-program.sh\" >/dev/null; /usr/bin/chmod 0600 \"\$evidence/controller-h0-program.sh\"; test \"\$(/usr/bin/sha256sum \"\$evidence/controller-h0-program.sh\" | /usr/bin/cut -d\" \" -f1)\" = b9b9f3315d1720735c1287e06671d294322fd3edc8cd6563ab9dfd05a88b9806 || { /usr/bin/printf \"HARD STOP: program digest mismatch\\n\" >&2; exit 72; }; test \"\$(/usr/bin/stat -c %s \"\$evidence/controller-h0-program.sh\")\" = 40147 || { /usr/bin/printf \"HARD STOP: program length mismatch\\n\" >&2; exit 73; }; exec /usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin /bin/bash --noprofile --norc \"\$evidence/controller-h0-program.sh\"'" < "PROGRAM"
```

## Fixed inputs (as used, unsubstituted)

- URL `https://github.com/ming-themerciless/freedom-bot.git`; pin
  `46d1c35a029ca8287779ae87d08a370ba0a0f2ef`
- Remote account/nodename `ubuntu` / `Test`
- Preserved fixed checkout `/opt/freedom-blades/platform`: on `oracle-test`
  it was neither inspected (not even `stat`) nor mutated
- Isolated checkout `/var/tmp/p5-r5-rp11-h0-20261006-01-checkout`
- Evidence directory `/var/tmp/p5-r5-rp11-h0-20261006-01-evidence`

## Facts established before the stop

| Item | Value | Evidence |
|---|---|---|
| real/effective UID | `1001` / `1001` | c003, c004 |
| real/effective user | `ubuntu` / `ubuntu` | c006, c005 |
| HF-01 nodename | `Test` | c007 |
| HF-02 `/etc/machine-id` SHA-256 | `e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d` | c008 |
| `/usr/bin/python3` resolution | symlink (`root:root`, `777`) → `/usr/bin/python3.14`, regular file `root:root` `755`, 7468968 bytes | c009–c011 |
| `/usr/bin/python3 -I -S` | `3.14.4 (main, Aug 20 2026, 10:41:58) [GCC 15.2.0]`; `isolated=1`, `no_site=1`; prefix `/usr`; suitable | c012 |
| exclusive paths before Git | evidence dir present (created by bootstrap; `ubuntu:ubuntu` `0700`, dev 2049, ino 1765916, no xattrs); checkout absent | c013 |
| Git | `git version 2.53.0` | c014 |
| isolated checkout init | `git init --quiet --template=` exit 0 | c015 |
| anonymous fetch | exit 128, `fatal: unable to get password from user` | c016 |

**Version difference, a fact and not an acceptance:** the available
interpreter is CPython 3.14.4 at `/usr/bin/python3.14`. The accepted design
cites `/usr/bin/python3.12` (TR-9, HF-07, HF-08, HF-10), and the R3 review
reported that path absent. This run did not re-observe `/usr/bin/python3.12`
because HF-08/HF-10 were not reached.

## HF-01 – HF-20

| HF | Status | Evidence |
|---|---|---|
| HF-01 | collected: `Test` | c007 |
| HF-02 | collected: `e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d` | c008 |
| HF-03 – HF-20 | **not collected**: HARD STOP at step 3 came first | — |

## Every remote command

Every command ran as `ubuntu` with the closed environment
`HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin`. The exact command text of
each command is reproduced verbatim in Appendix B.

| ID | Class | Start UTC | End UTC | Exit |
|---|---|---|---|---|
| bootstrap (fixed text above) | identity, path checks, `mkdir`, `tee`, `chmod`, digest/length | — | — | passed (no 70–73) |
| c001-program-sha256 | CTX | 2026-10-06T01:10:18.739957Z | 2026-10-06T01:10:18.745036Z | 0 |
| c002-program-stat | CTX | 2026-10-06T01:10:18.745699Z | 2026-10-06T01:10:18.750890Z | 0 |
| c003-id-ru | CTX | 2026-10-06T01:10:18.751473Z | 2026-10-06T01:10:18.756481Z | 0 |
| c004-id-u | CTX | 2026-10-06T01:10:18.758234Z | 2026-10-06T01:10:18.763246Z | 0 |
| c005-id-un | CTX | 2026-10-06T01:10:18.764964Z | 2026-10-06T01:10:18.770199Z | 0 |
| c006-id-run | CTX | 2026-10-06T01:10:18.771906Z | 2026-10-06T01:10:18.830248Z | 0 |
| c007-hf01-uname-n | HF-01 | 2026-10-06T01:10:18.831962Z | 2026-10-06T01:10:18.836941Z | 0 |
| c008-hf02-machine-id-sha256 | HF-02 | 2026-10-06T01:10:18.838705Z | 2026-10-06T01:10:18.843477Z | 0 |
| c009-py3-readlink | PY | 2026-10-06T01:10:18.844132Z | 2026-10-06T01:10:18.849207Z | 0 |
| c010-py3-stat | PY | 2026-10-06T01:10:18.849872Z | 2026-10-06T01:10:18.855119Z | 0 |
| c011-py3-stat-L | PY | 2026-10-06T01:10:18.855782Z | 2026-10-06T01:10:18.861027Z | 0 |
| c012-py3-version | PY | 2026-10-06T01:10:18.861732Z | 2026-10-06T01:10:18.929343Z | 0 |
| c013-paths-lstat-before-git | CTX | 2026-10-06T01:10:18.931428Z | 2026-10-06T01:10:18.951136Z | 0 |
| c014-git-version | GIT | 2026-10-06T01:10:18.953165Z | 2026-10-06T01:10:18.960006Z | 0 |
| c015-git-init | GIT | 2026-10-06T01:10:18.960880Z | 2026-10-06T01:10:18.970018Z | 0 |
| c016-git-fetch | GIT | 2026-10-06T01:10:18.970924Z | 2026-10-06T01:10:19.434250Z | **128** |
| c017-manifest-payload | CLOSE | 2026-10-06T01:10:19.435688Z | 2026-10-06T01:10:19.461166Z | 0 |
| c018-manifest-final | CLOSE | 2026-10-06T01:10:19.461885Z | 2026-10-06T01:10:19.480687Z | 0 |
| c019-inventory | CLOSE | 2026-10-06T01:10:19.481423Z | 2026-10-06T01:10:19.550118Z | 0 |

Before exiting, the program echoed every evidence file except the retained
program to SSH stdout. It used bash builtins only (`mapfile`/`printf`) and
executed no further command. That stdout (35146 bytes) is controller
transport only.

## Evidence closure

- `MANIFEST.payload`: SHA-256
  `eed233c04ab6f965496a2d5b00ebab15436fc699d58b92a3105ae366eed93002`,
  6256 bytes, 69 entries. It is reproduced in full in Appendix A.
- `MANIFEST.final`: SHA-256
  `76fa12bce526b3637c7bc08a0aab825db4a6696cba17fdc67a9775e03be6243e`,
  102 bytes. Its content is
  `MANIFEST.payload  sha256=eed233c04ab6f965496a2d5b00ebab15436fc699d58b92a3105ae366eed93002  bytes=6256`.
  The aggregate digest for this evidence directory is the `MANIFEST.final`
  digest.
- Owner/mode inventory (`INVENTORY.owner-mode`): every file present at c019
  was a fresh regular `ubuntu:ubuntu` mode-`0600` file with link count 1;
  `violations=0`. The evidence directory is `ubuntu:ubuntu` `0700`.
- Controller verification: the controller recomputed all 69 payload entries
  against the echoed bytes and the locally held program: 0 mismatches. It
  recomputed `MANIFEST.payload` and `MANIFEST.final` and got the digests and
  lengths above.
- Explicit exclusions (verbatim file `EXCLUSIONS`, Appendix A):
  - `MANIFEST.payload` and c017's `.cmd/.err/.meta` (self-reference);
  - `MANIFEST.final` and c018's records (later closing record);
  - `INVENTORY.owner-mode` and c019's records (later closing record);
  - c019's own `.meta`, which was written after it exited and so is not
    inventoried;
  - `COMMANDS.index`, which lists payload commands only.

  Nothing else is excluded.
- **Erratum to the retained `EXCLUSIONS` text:** that file says c019's `.err`
  and `.meta` are both missing from the inventory. In fact the recorder
  creates each `.err` (empty) before the command runs. So
  `c019-inventory.err` *is* inventoried, and only `c019-inventory.meta` is
  not. This handback corrects the statement and does not change the retained
  file.
- Retained file count: 81 in total.
  - 69 payload files, including `controller-h0-program.sh`;
  - `MANIFEST.payload`, `MANIFEST.final` and `INVENTORY.owner-mode`;
  - 9 closing records: `.cmd/.err/.meta` for each of c017, c018 and c019.

  The inventory lists 80 of them; the 81st is `c019-inventory.meta`.

## Repository, remote and controller changes

- **Repository:** only this handback file was written. No other repository
  file was changed. No commit or push.
- **Remote (`oracle-test`):** both exclusive paths were created and retained.
  - `/var/tmp/p5-r5-rp11-h0-20261006-01-evidence` holds closed evidence.
  - `/var/tmp/p5-r5-rp11-h0-20261006-01-checkout` was created by c015 as an
    empty, unborn Git repository with no objects and no HEAD commit. It was
    not inspected after the failed fetch. There was no other write, no
    cleanup and no removal.
- **Controller:** the following are scratchpad files only, outside the
  repository:
  - the program and its assembly inputs;
  - an SSH stdout/stderr capture;
  - local dry-run trees.

## Disclosures about controller-side activity

1. While computing expected digests during preparation, one controller shell
   command included a stray `git ls-remote https://github.com/ming-themerciless/freedom-bot.git`
   with its output discarded (`| head -0`). It contacted only GitHub over
   HTTPS from the controller, not `oracle-test`. It used no credential option,
   and its result was not observed.
2. Local validation used only scratchpad paths:
   - a syntax check;
   - a stub-`ssh` argument extraction;
   - a bootstrap simulation that, run unmodified, refused at the identity
     check with exit 70 and created nothing under `/var/tmp`;
   - a dry run of the recorder, manifest and inventory with harmless
     commands, which included an `lstat` of the controller's `/`;
   - a dry run of the retrieval and governing-file logic over `file://`
     against the local repository.

   One earlier dry-run variant also computed the controller's own
   `/etc/machine-id` SHA-256 into scratch. No raw machine-id was read into
   output, and no secret file was touched.
3. Pinned-tree expectations embedded in the program came from local `git show`
   of the pin:
   - `.agents/AGENTS.md`
     `ca907aa7fc2a7dd70e424fe40ec0ad4d42f625e972500190a358f57e70c9f39e`
   - `docs/implementation-plan.md`
     `07936a42ec645f2a997f5425ee68d7fd0fed92cfef8c088daf76b8831f24a1c9`
   - the accepted proposal
     `a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02`
   - the D3-R6 acceptance
     `afe1f2256259244f207c87a1244be5455ad18aebc6ac9a86db400fc105f729f5`
   - R4 prompt `451e1fa4a6b56900420b66f8463caa19e21a5d22f97aa37a32a3b2ebb665f8bf`
     (6019 bytes)
   - R4 authority `d45513de6090c83876685643137ad3b6d4b2545f0862e4f7bb4a96b8c2f3e845`
     (1794 bytes)

   These were not reached remotely.

## Prohibited-action confirmation

Each of the following was **not** done:

- a second SSH connection or retry;
- a nested Claude client;
- SCP, SFTP, rsync, or agent, X11 or port forwarding;
- interactive authentication, or reading or copying a credential, key,
  `known_hosts` or SSH config;
- `sudo` or any privilege;
- a package operation, installation, build or test;
- a service or database mutation;
- H-1/H-2, activation or a pass;
- rollback or cleanup;
- removal of either exclusive path;
- an environment dump;
- any read of `/tmp`, secrets, application data, PostgreSQL, earlier evidence
  or `/opt/freedom-blades/platform` on `oracle-test`;
- a commit or push.

## Checks not run

- Steps 4–6 were never reached after the HARD STOP. They are:
  - commit verification, detached checkout, `HEAD` and porcelain status;
  - governing-file verification;
  - retention of the R4 prompt/authority copies;
  - HF-03 through HF-20.
- No test suite was run, because the assignment does not authorize one.
- The isolated checkout was not re-inspected after the failure.

## Appendix A — verbatim retained closing and context files

Each block is the exact retained file content as echoed by the program. A trailing newline in a file appears as an empty last line inside its fence. The size and SHA-256 shown were computed by the controller over the echoed bytes, and they match `MANIFEST.payload` wherever the file is listed there.

### `RUN-CONTEXT` (1493 bytes, sha256 `4284deb0b915dad653ed9133ccea8a879404bd4234869f8c1028958e03563f89`)

````text
work_id=C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R4-20261006-01
program_start_utc=2026-10-06T01:10:18.739220Z
canonical_url=https://github.com/ming-themerciless/freedom-bot.git
pinned_commit=46d1c35a029ca8287779ae87d08a370ba0a0f2ef
remote_account=ubuntu
remote_nodename=Test
fixed_checkout_preserved_not_inspected=/opt/freedom-blades/platform
isolated_checkout=/var/tmp/p5-r5-rp11-h0-20261006-01-checkout
evidence_directory=/var/tmp/p5-r5-rp11-h0-20261006-01-evidence
durable_controller_handback=docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-handback.md
program_environment=HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin (set by the bootstrap; not read or dumped)
controller_command_shape=ssh -T -o BatchMode=yes -o ClearAllForwardings=yes -o ForwardAgent=no -o ForwardX11=no -o PermitLocalCommand=no oracle-test "<fixed bootstrap: real/effective ubuntu, uname -n Test, umask 077, both exclusive paths absent (test -e / test -L), mkdir -m 0700 evidence, tee stdin to controller-h0-program.sh, chmod 0600, require sha256 = SHA256 and stat %s = BYTES, exec env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin /bin/bash --noprofile --norc controller-h0-program.sh>" < PROGRAM
controller_program_digest_and_length=supplied to the bootstrap as literals; recomputed below by command c001/c002
r4_prompt_expected_sha256=451e1fa4a6b56900420b66f8463caa19e21a5d22f97aa37a32a3b2ebb665f8bf bytes=6019
r4_authority_expected_sha256=d45513de6090c83876685643137ad3b6d4b2545f0862e4f7bb4a96b8c2f3e845 bytes=1794

````

### `HARDSTOP` (125 bytes, sha256 `52ef140f2d5f985ad8fbe812264af0e072a3b6eeb84a573f49748225379d85b1`)

````text
step=retrieval
reason=anonymous fetch of pinned commit failed (exit 128; see c016-git-fetch.err)
last_command=c016-git-fetch

````

### `COMMANDS.index` (1784 bytes, sha256 `00d111fa7e948ce3d5f7f5f62951aa6dcde985a2a3ad43b468571fc230fe863a`)

````text
c001-program-sha256	CTX	2026-10-06T01:10:18.739957Z	2026-10-06T01:10:18.745036Z	exit=0	stdout=c001-program-sha256.out
c002-program-stat	CTX	2026-10-06T01:10:18.745699Z	2026-10-06T01:10:18.750890Z	exit=0	stdout=c002-program-stat.out
c003-id-ru	CTX	2026-10-06T01:10:18.751473Z	2026-10-06T01:10:18.756481Z	exit=0	stdout=c003-id-ru.out
c004-id-u	CTX	2026-10-06T01:10:18.758234Z	2026-10-06T01:10:18.763246Z	exit=0	stdout=c004-id-u.out
c005-id-un	CTX	2026-10-06T01:10:18.764964Z	2026-10-06T01:10:18.770199Z	exit=0	stdout=c005-id-un.out
c006-id-run	CTX	2026-10-06T01:10:18.771906Z	2026-10-06T01:10:18.830248Z	exit=0	stdout=c006-id-run.out
c007-hf01-uname-n	HF-01	2026-10-06T01:10:18.831962Z	2026-10-06T01:10:18.836941Z	exit=0	stdout=c007-hf01-uname-n.out
c008-hf02-machine-id-sha256	HF-02	2026-10-06T01:10:18.838705Z	2026-10-06T01:10:18.843477Z	exit=0	stdout=c008-hf02-machine-id-sha256.out
c009-py3-readlink	PY	2026-10-06T01:10:18.844132Z	2026-10-06T01:10:18.849207Z	exit=0	stdout=c009-py3-readlink.out
c010-py3-stat	PY	2026-10-06T01:10:18.849872Z	2026-10-06T01:10:18.855119Z	exit=0	stdout=c010-py3-stat.out
c011-py3-stat-L	PY	2026-10-06T01:10:18.855782Z	2026-10-06T01:10:18.861027Z	exit=0	stdout=c011-py3-stat-L.out
c012-py3-version	PY	2026-10-06T01:10:18.861732Z	2026-10-06T01:10:18.929343Z	exit=0	stdout=c012-py3-version.out
c013-paths-lstat-before-git	CTX	2026-10-06T01:10:18.931428Z	2026-10-06T01:10:18.951136Z	exit=0	stdout=c013-paths-lstat-before-git.out
c014-git-version	GIT	2026-10-06T01:10:18.953165Z	2026-10-06T01:10:18.960006Z	exit=0	stdout=c014-git-version.out
c015-git-init	GIT	2026-10-06T01:10:18.960880Z	2026-10-06T01:10:18.970018Z	exit=0	stdout=c015-git-init.out
c016-git-fetch	GIT	2026-10-06T01:10:18.970924Z	2026-10-06T01:10:19.434250Z	exit=128	stdout=c016-git-fetch.out

````

### `EXCLUSIONS` (1011 bytes, sha256 `c9a2a42c688c618e59f3ae2c00c94442e1122e8ee1c66bc11041667c0f66340f`)

````text
Manifest exclusions (R4 H-0, C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R4-20261006-01)
MANIFEST.payload covers every evidence file present when it is generated, except:
- MANIFEST.payload itself and the .cmd/.err/.meta records of the command that generates it (self-reference);
- MANIFEST.final and the .cmd/.err/.meta records of its command (closing record written after the payload manifest);
- INVENTORY.owner-mode and the .cmd/.err/.meta records of its command (closing record written after both manifests).
MANIFEST.final names only MANIFEST.payload's full SHA-256 and byte length.
INVENTORY.owner-mode lists every file present when it runs, including its own .cmd and its own still-open output;
its own .err and .meta are created after it exits and are therefore not inventoried.
COMMANDS.index lists the payload commands only; the three closing commands are recorded solely in their own .cmd/.meta/.err files.
No evidence file is excluded for any other reason. Retained program controller-h0-program.sh is payload.

````

### `MANIFEST.payload` (6256 bytes, sha256 `eed233c04ab6f965496a2d5b00ebab15436fc699d58b92a3105ae366eed93002`)

````text
00d111fa7e948ce3d5f7f5f62951aa6dcde985a2a3ad43b468571fc230fe863a  1784  COMMANDS.index
c9a2a42c688c618e59f3ae2c00c94442e1122e8ee1c66bc11041667c0f66340f  1011  EXCLUSIONS
52ef140f2d5f985ad8fbe812264af0e072a3b6eeb84a573f49748225379d85b1  125  HARDSTOP
4284deb0b915dad653ed9133ccea8a879404bd4234869f8c1028958e03563f89  1493  RUN-CONTEXT
63aa0263740977a3c7a30ce571c121b3f1df08645092d817414f7ae6f67a38d8  91  c001-program-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c001-program-sha256.err
cdf40d097055cc21e8efb20cd6022bcbc950e8f55e597f577eac7d1681a10a07  173  c001-program-sha256.meta
c505e7b5f0758d970750a974092d47a9de7fac6eaccbfbcfaeefefee9e849461  135  c001-program-sha256.out
41bea64015cc209b52ac4241744930890c1b70f264db8ee5dc7ba89cb441b81f  128  c002-program-stat.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c002-program-stat.err
e933d66b500db272982b187c7c7a7fa668c8cf96b3ddd154c75308d1c48e7b94  167  c002-program-stat.meta
9cd81e58d2f44b08dea727fa2ccabfdf23ec269cb3860c6a7cb8b28cf477fdc3  58  c002-program-stat.out
798b11d7f3717e79fa5a7dc6e520867551e8433fd518f8bbf7406c8d534bc665  16  c003-id-ru.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c003-id-ru.err
f015c4cccbddf3763921bae88072f49ebbcdb49d0cb313f7d45a7c94f2cbdc98  146  c003-id-ru.meta
d6a1a767319c3bf2a337b16e3a14916f63e432872e0f8df1cb73b32a8b338ae4  5  c003-id-ru.out
9bdceab1a7aa03b04c0718aa52f8c284e0474cdb262fe8affbfd674d99df9a5c  15  c004-id-u.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c004-id-u.err
fdcb2c3e4949cc9733ffbe19a8da5bf71ad89439371762a1693197576618052f  143  c004-id-u.meta
d6a1a767319c3bf2a337b16e3a14916f63e432872e0f8df1cb73b32a8b338ae4  5  c004-id-u.out
424807431da2c471d482cc7994ef1b2e77243e298e522cf424eeed9a52a890f5  16  c005-id-un.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c005-id-un.err
321fd3d9bde910d267190aa2cc163888089155550039802ad4b38f12268c18d8  146  c005-id-un.meta
da4d47d486c674b0e05b992713276b345aaa1858d3f147b4b185ad5215cfdc69  7  c005-id-un.out
bad37ef90e6ee7910f07a56394a6963176b7b476f31b29c6c733a403019096fa  17  c006-id-run.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c006-id-run.err
a5e874f13c6394fe52f6323f062bd41d615cf32f836fed177da61d34aef9c854  149  c006-id-run.meta
da4d47d486c674b0e05b992713276b345aaa1858d3f147b4b185ad5215cfdc69  7  c006-id-run.out
219a4d23f04743b974f422332709ba0c6464cf03b1d4c6b3b0cfdd92014a71d4  18  c007-hf01-uname-n.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c007-hf01-uname-n.err
5da5dc642a4a499ac549aa09fe604993585720c6008409b091800f08be0ad0fe  169  c007-hf01-uname-n.meta
c9d04c9565fc665c80681fb1d829938026871f66e14f501e08531df66938a789  5  c007-hf01-uname-n.out
897e893080611fb9038034bcd3f60291a066f557d868ffc2027f1b409b365807  35  c008-hf02-machine-id-sha256.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c008-hf02-machine-id-sha256.err
e2fd31c6ce4944dc1b045466c386597927be3bacf1f2f7bdc20096afb19e67ac  199  c008-hf02-machine-id-sha256.meta
0726bfdac8860577e63af5a4ec48c0f47027b912eabf1dcc115033d01aab82d2  82  c008-hf02-machine-id-sha256.out
5759c545d894116dcdde17f8c725da7b913b67120506500f7d6136b002ddd378  41  c009-py3-readlink.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c009-py3-readlink.err
0a6de82270399774cdfdbccd054dbd1dd61f23e44152173886194b7182a21d43  166  c009-py3-readlink.meta
65d0f645c13836692cffcd74d743a8b88f47bbfe824b29c6079c9d6968b8ff03  20  c009-py3-readlink.out
c88824fbad31deda456a739c9b421894bb681680d0b356f88da732b0f43ba55b  76  c010-py3-stat.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c010-py3-stat.err
1549f7786310d623b6e3a8aac0358143cc225b5f3bfcca50fb89e238921c3c58  154  c010-py3-stat.meta
d4688fe7bb3c8f0385d31b0dedd71b501b7a1bb75cf41fde90b3593fa9e9b3b5  66  c010-py3-stat.out
993267674a4ed4e76047bbe249d2cc68a292acebf443e2ea1f2b41806497b250  88  c011-py3-stat-L.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c011-py3-stat-L.err
0da325172846a3976dd453928871c26abfddfb9219ac61164305d3a5f149a2bb  160  c011-py3-stat-L.meta
018155c9f57ac932110e1df0de3f9a843834c2fb9430be9bc648efa63133c0df  78  c011-py3-stat-L.out
63175f7de94efd38edef1684eed925a5424e6e235a9076c87023f2c306cd677d  405  c012-py3-version.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c012-py3-version.err
901b8db8b2aeb1ecaefe293987fae78243d3e29b7ec4487b412338dfb15861b5  163  c012-py3-version.meta
6734d508cd94a6727a582960647cfccabfc83b5befc9f230aaaf2a408dba7d4c  237  c012-py3-version.out
bd8c35f29f01f202f821af1d1c977d4ee49126638f965487e98d6f6132777220  2295  c013-paths-lstat-before-git.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c013-paths-lstat-before-git.err
ab3d98c5a200f5970428076055958a571f95ea62c8c51c4a82a8e22dd5ee73a7  197  c013-paths-lstat-before-git.meta
2dcf73d33cf1b896d7b4a1c021bc3e14e1f4bbbf12e3b2eff898792adc386ff0  214  c013-paths-lstat-before-git.out
ebb972e24b60a02f9e947b51acbaf8b9e1a9006650f261b635a59c5a550c0823  280  c014-git-version.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c014-git-version.err
a6eeaae833a6beba60ea29bd2a868ac690e1eba196fba9a12d1e68c4b10b10a0  164  c014-git-version.meta
97452bcde974ef512f9552791fc4f6a3219a724877671fba270baca1a6075b74  19  c014-git-version.out
0ea38cb38b69467e8ba2b57949a3681a1b035183a80108d088b66a3a2f725886  752  c015-git-init.cmd
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c015-git-init.err
b74a9acbb2d1256fdf194724bc2b83aedbe1cf7ce9ae276805a2a5feaa24863c  155  c015-git-init.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c015-git-init.out
804fbb257b65ec78a776e591f424704d106e0de92f3b6dde646f6c821ff5d155  863  c016-git-fetch.cmd
df3408a8d5c3d94711c9bfa4361390576571cc8b42c28f477784ffaac922d128  40  c016-git-fetch.err
c3d34ac2e85e228618d7ecf4b34aa7f49e70dbb75b4184df4fcb955cf33eb8df  160  c016-git-fetch.meta
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0  c016-git-fetch.out
b9b9f3315d1720735c1287e06671d294322fd3edc8cd6563ab9dfd05a88b9806  40147  controller-h0-program.sh

````

### `MANIFEST.final` (102 bytes, sha256 `76fa12bce526b3637c7bc08a0aab825db4a6696cba17fdc67a9775e03be6243e`)

````text
MANIFEST.payload  sha256=eed233c04ab6f965496a2d5b00ebab15436fc699d58b92a3105ae366eed93002  bytes=6256

````

### `INVENTORY.owner-mode` (6960 bytes, sha256 `3438931882e1a7ca1426b90029a7d109fb0050ce81aa2af8bc58b198b23173f4`)

````text
DIR	/var/tmp/p5-r5-rp11-h0-20261006-01-evidence	uid=1001	gid=1001	mode=0700
COMMANDS.index	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
EXCLUSIONS	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
HARDSTOP	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
INVENTORY.owner-mode	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes	own-output-open
MANIFEST.final	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
MANIFEST.payload	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
RUN-CONTEXT	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
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
c017-manifest-payload.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c017-manifest-payload.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c017-manifest-payload.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c018-manifest-final.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c018-manifest-final.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c018-manifest-final.meta	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c019-inventory.cmd	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
c019-inventory.err	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
controller-h0-program.sh	reg	owner=ubuntu	group=ubuntu	mode=0600	nlink=1	fresh=yes	ok=yes
violations=0

````


## Appendix B — verbatim command records (`.cmd`, `.out`, `.err`, `.meta`) c001–c019

### `c001-program-sha256.cmd` (91 bytes, sha256 `63aa0263740977a3c7a30ce571c121b3f1df08645092d817414f7ae6f67a38d8`)

````text
/usr/bin/sha256sum -- /var/tmp/p5-r5-rp11-h0-20261006-01-evidence/controller-h0-program.sh

````

### `c001-program-sha256.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c001-program-sha256.meta` (173 bytes, sha256 `cdf40d097055cc21e8efb20cd6022bcbc950e8f55e597f577eac7d1681a10a07`)

````text
id=c001-program-sha256
hf=CTX
stdout=c001-program-sha256.out
stderr=c001-program-sha256.err
start_utc=2026-10-06T01:10:18.739957Z
end_utc=2026-10-06T01:10:18.745036Z
exit=0

````

### `c001-program-sha256.out` (135 bytes, sha256 `c505e7b5f0758d970750a974092d47a9de7fac6eaccbfbcfaeefefee9e849461`)

````text
b9b9f3315d1720735c1287e06671d294322fd3edc8cd6563ab9dfd05a88b9806  /var/tmp/p5-r5-rp11-h0-20261006-01-evidence/controller-h0-program.sh

````

### `c002-program-stat.cmd` (128 bytes, sha256 `41bea64015cc209b52ac4241744930890c1b70f264db8ee5dc7ba89cb441b81f`)

````text
/usr/bin/stat -c size=%s\ owner=%U:%G\ mode=%a\ type=%F -- /var/tmp/p5-r5-rp11-h0-20261006-01-evidence/controller-h0-program.sh

````

### `c002-program-stat.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c002-program-stat.meta` (167 bytes, sha256 `e933d66b500db272982b187c7c7a7fa668c8cf96b3ddd154c75308d1c48e7b94`)

````text
id=c002-program-stat
hf=CTX
stdout=c002-program-stat.out
stderr=c002-program-stat.err
start_utc=2026-10-06T01:10:18.745699Z
end_utc=2026-10-06T01:10:18.750890Z
exit=0

````

### `c002-program-stat.out` (58 bytes, sha256 `9cd81e58d2f44b08dea727fa2ccabfdf23ec269cb3860c6a7cb8b28cf477fdc3`)

````text
size=40147 owner=ubuntu:ubuntu mode=600 type=regular file

````

### `c003-id-ru.cmd` (16 bytes, sha256 `798b11d7f3717e79fa5a7dc6e520867551e8433fd518f8bbf7406c8d534bc665`)

````text
/usr/bin/id -ru

````

### `c003-id-ru.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c003-id-ru.meta` (146 bytes, sha256 `f015c4cccbddf3763921bae88072f49ebbcdb49d0cb313f7d45a7c94f2cbdc98`)

````text
id=c003-id-ru
hf=CTX
stdout=c003-id-ru.out
stderr=c003-id-ru.err
start_utc=2026-10-06T01:10:18.751473Z
end_utc=2026-10-06T01:10:18.756481Z
exit=0

````

### `c003-id-ru.out` (5 bytes, sha256 `d6a1a767319c3bf2a337b16e3a14916f63e432872e0f8df1cb73b32a8b338ae4`)

````text
1001

````

### `c004-id-u.cmd` (15 bytes, sha256 `9bdceab1a7aa03b04c0718aa52f8c284e0474cdb262fe8affbfd674d99df9a5c`)

````text
/usr/bin/id -u

````

### `c004-id-u.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c004-id-u.meta` (143 bytes, sha256 `fdcb2c3e4949cc9733ffbe19a8da5bf71ad89439371762a1693197576618052f`)

````text
id=c004-id-u
hf=CTX
stdout=c004-id-u.out
stderr=c004-id-u.err
start_utc=2026-10-06T01:10:18.758234Z
end_utc=2026-10-06T01:10:18.763246Z
exit=0

````

### `c004-id-u.out` (5 bytes, sha256 `d6a1a767319c3bf2a337b16e3a14916f63e432872e0f8df1cb73b32a8b338ae4`)

````text
1001

````

### `c005-id-un.cmd` (16 bytes, sha256 `424807431da2c471d482cc7994ef1b2e77243e298e522cf424eeed9a52a890f5`)

````text
/usr/bin/id -un

````

### `c005-id-un.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c005-id-un.meta` (146 bytes, sha256 `321fd3d9bde910d267190aa2cc163888089155550039802ad4b38f12268c18d8`)

````text
id=c005-id-un
hf=CTX
stdout=c005-id-un.out
stderr=c005-id-un.err
start_utc=2026-10-06T01:10:18.764964Z
end_utc=2026-10-06T01:10:18.770199Z
exit=0

````

### `c005-id-un.out` (7 bytes, sha256 `da4d47d486c674b0e05b992713276b345aaa1858d3f147b4b185ad5215cfdc69`)

````text
ubuntu

````

### `c006-id-run.cmd` (17 bytes, sha256 `bad37ef90e6ee7910f07a56394a6963176b7b476f31b29c6c733a403019096fa`)

````text
/usr/bin/id -run

````

### `c006-id-run.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c006-id-run.meta` (149 bytes, sha256 `a5e874f13c6394fe52f6323f062bd41d615cf32f836fed177da61d34aef9c854`)

````text
id=c006-id-run
hf=CTX
stdout=c006-id-run.out
stderr=c006-id-run.err
start_utc=2026-10-06T01:10:18.771906Z
end_utc=2026-10-06T01:10:18.830248Z
exit=0

````

### `c006-id-run.out` (7 bytes, sha256 `da4d47d486c674b0e05b992713276b345aaa1858d3f147b4b185ad5215cfdc69`)

````text
ubuntu

````

### `c007-hf01-uname-n.cmd` (18 bytes, sha256 `219a4d23f04743b974f422332709ba0c6464cf03b1d4c6b3b0cfdd92014a71d4`)

````text
/usr/bin/uname -n

````

### `c007-hf01-uname-n.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c007-hf01-uname-n.meta` (169 bytes, sha256 `5da5dc642a4a499ac549aa09fe604993585720c6008409b091800f08be0ad0fe`)

````text
id=c007-hf01-uname-n
hf=HF-01
stdout=c007-hf01-uname-n.out
stderr=c007-hf01-uname-n.err
start_utc=2026-10-06T01:10:18.831962Z
end_utc=2026-10-06T01:10:18.836941Z
exit=0

````

### `c007-hf01-uname-n.out` (5 bytes, sha256 `c9d04c9565fc665c80681fb1d829938026871f66e14f501e08531df66938a789`)

````text
Test

````

### `c008-hf02-machine-id-sha256.cmd` (35 bytes, sha256 `897e893080611fb9038034bcd3f60291a066f557d868ffc2027f1b409b365807`)

````text
/usr/bin/sha256sum /etc/machine-id

````

### `c008-hf02-machine-id-sha256.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c008-hf02-machine-id-sha256.meta` (199 bytes, sha256 `e2fd31c6ce4944dc1b045466c386597927be3bacf1f2f7bdc20096afb19e67ac`)

````text
id=c008-hf02-machine-id-sha256
hf=HF-02
stdout=c008-hf02-machine-id-sha256.out
stderr=c008-hf02-machine-id-sha256.err
start_utc=2026-10-06T01:10:18.838705Z
end_utc=2026-10-06T01:10:18.843477Z
exit=0

````

### `c008-hf02-machine-id-sha256.out` (82 bytes, sha256 `0726bfdac8860577e63af5a4ec48c0f47027b912eabf1dcc115033d01aab82d2`)

````text
e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d  /etc/machine-id

````

### `c009-py3-readlink.cmd` (41 bytes, sha256 `5759c545d894116dcdde17f8c725da7b913b67120506500f7d6136b002ddd378`)

````text
/usr/bin/readlink -f -- /usr/bin/python3

````

### `c009-py3-readlink.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c009-py3-readlink.meta` (166 bytes, sha256 `0a6de82270399774cdfdbccd054dbd1dd61f23e44152173886194b7182a21d43`)

````text
id=c009-py3-readlink
hf=PY
stdout=c009-py3-readlink.out
stderr=c009-py3-readlink.err
start_utc=2026-10-06T01:10:18.844132Z
end_utc=2026-10-06T01:10:18.849207Z
exit=0

````

### `c009-py3-readlink.out` (20 bytes, sha256 `65d0f645c13836692cffcd74d743a8b88f47bbfe824b29c6079c9d6968b8ff03`)

````text
/usr/bin/python3.14

````

### `c010-py3-stat.cmd` (76 bytes, sha256 `c88824fbad31deda456a739c9b421894bb681680d0b356f88da732b0f43ba55b`)

````text
/usr/bin/stat -c name=%n\ type=%F\ owner=%U:%G\ mode=%a -- /usr/bin/python3

````

### `c010-py3-stat.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c010-py3-stat.meta` (154 bytes, sha256 `1549f7786310d623b6e3a8aac0358143cc225b5f3bfcca50fb89e238921c3c58`)

````text
id=c010-py3-stat
hf=PY
stdout=c010-py3-stat.out
stderr=c010-py3-stat.err
start_utc=2026-10-06T01:10:18.849872Z
end_utc=2026-10-06T01:10:18.855119Z
exit=0

````

### `c010-py3-stat.out` (66 bytes, sha256 `d4688fe7bb3c8f0385d31b0dedd71b501b7a1bb75cf41fde90b3593fa9e9b3b5`)

````text
name=/usr/bin/python3 type=symbolic link owner=root:root mode=777

````

### `c011-py3-stat-L.cmd` (88 bytes, sha256 `993267674a4ed4e76047bbe249d2cc68a292acebf443e2ea1f2b41806497b250`)

````text
/usr/bin/stat -L -c name=%n\ type=%F\ owner=%U:%G\ mode=%a\ size=%s -- /usr/bin/python3

````

### `c011-py3-stat-L.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c011-py3-stat-L.meta` (160 bytes, sha256 `0da325172846a3976dd453928871c26abfddfb9219ac61164305d3a5f149a2bb`)

````text
id=c011-py3-stat-L
hf=PY
stdout=c011-py3-stat-L.out
stderr=c011-py3-stat-L.err
start_utc=2026-10-06T01:10:18.855782Z
end_utc=2026-10-06T01:10:18.861027Z
exit=0

````

### `c011-py3-stat-L.out` (78 bytes, sha256 `018155c9f57ac932110e1df0de3f9a843834c2fb9430be9bc648efa63133c0df`)

````text
name=/usr/bin/python3 type=regular file owner=root:root mode=755 size=7468968

````

### `c012-py3-version.cmd` (405 bytes, sha256 `63175f7de94efd38edef1684eed925a5424e6e235a9076c87023f2c306cd677d`)

````text
/usr/bin/python3 -I -S -c $'import sys\nprint("version=" + sys.version.replace("\\n", " "))\nprint("version_info=" + ".".join(str(x) for x in sys.version_info[:3]))\nprint("major=" + str(sys.version_info[0]))\nprint("isolated=" + str(sys.flags.isolated))\nprint("no_site=" + str(sys.flags.no_site))\nprint("executable=" + sys.executable)\nprint("prefix=" + sys.prefix)\nprint("path=" + repr(sys.path))\n'

````

### `c012-py3-version.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c012-py3-version.meta` (163 bytes, sha256 `901b8db8b2aeb1ecaefe293987fae78243d3e29b7ec4487b412338dfb15861b5`)

````text
id=c012-py3-version
hf=PY
stdout=c012-py3-version.out
stderr=c012-py3-version.err
start_utc=2026-10-06T01:10:18.861732Z
end_utc=2026-10-06T01:10:18.929343Z
exit=0

````

### `c012-py3-version.out` (237 bytes, sha256 `6734d508cd94a6727a582960647cfccabfc83b5befc9f230aaaf2a408dba7d4c`)

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

### `c013-paths-lstat-before-git.cmd` (2295 bytes, sha256 `bd8c35f29f01f202f821af1d1c977d4ee49126638f965487e98d6f6132777220`)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\ndef nm(f, i):\n    try:\n        return f(i)[0]\n    except KeyError:\n        return "?"\ndef kind(m):\n    if stat.S_ISDIR(m): return "dir"\n    if stat.S_ISREG(m): return "reg"\n    if stat.S_ISLNK(m): return "symlink"\n    if stat.S_ISCHR(m): return "chr"\n    if stat.S_ISBLK(m): return "blk"\n    if stat.S_ISFIFO(m): return "fifo"\n    if stat.S_ISSOCK(m): return "sock"\n    return "other"\ndef one(p):\n    try:\n        st = os.lstat(p)\n    except FileNotFoundError:\n        print(p + "\\tabsent")\n        return None\n    except OSError as e:\n        print(p + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n        return None\n    m = st.st_mode\n    try:\n        xs = ",".join(sorted(os.listxattr(p, follow_symlinks=False))) or "-"\n    except OSError as e:\n        xs = "error:" + type(e).__name__ + ":errno=" + str(e.errno)\n    row = [p, "present", kind(m), "uid=" + str(st.st_uid), "gid=" + str(st.st_gid),\n           "owner=" + nm(pwd.getpwuid, st.st_uid), "group=" + nm(grp.getgrgid, st.st_gid),\n           "mode=%04o" % stat.S_IMODE(m), "dev=" + str(st.st_dev), "ino=" + str(st.st_ino),\n           "nlink=" + str(st.st_nlink), "size=" + str(st.st_size), "xattr_names=" + xs]\n    if stat.S_ISLNK(m):\n        try:\n            row.append("link=" + os.readlink(p))\n        except OSError as e:\n            row.append("link=error:" + type(e).__name__)\n    print("\\t".join(row))\n    return st\nmode = sys.argv[1]\nif mode == "stat":\n    for p in sys.argv[2:]:\n        one(p)\nelif mode == "ls":\n    for d in sys.argv[2:]:\n        try:\n            names = sorted(os.listdir(d))\n        except FileNotFoundError:\n            print("DIR\\t" + d + "\\tabsent")\n            continue\n        except PermissionError:\n            print("DIR\\t" + d + "\\tunreadable")\n            continue\n        except OSError as e:\n            print("DIR\\t" + d + "\\terror\\t" + type(e).__name__ + "\\terrno=" + str(e.errno))\n            continue\n        print("DIR\\t" + d + "\\tentries=" + str(len(names)))\n        for n in names:\n            one(os.path.join(d, n))\nelse:\n    sys.exit(2)\n' stat /var/tmp/p5-r5-rp11-h0-20261006-01-evidence /var/tmp/p5-r5-rp11-h0-20261006-01-checkout

````

### `c013-paths-lstat-before-git.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c013-paths-lstat-before-git.meta` (197 bytes, sha256 `ab3d98c5a200f5970428076055958a571f95ea62c8c51c4a82a8e22dd5ee73a7`)

````text
id=c013-paths-lstat-before-git
hf=CTX
stdout=c013-paths-lstat-before-git.out
stderr=c013-paths-lstat-before-git.err
start_utc=2026-10-06T01:10:18.931428Z
end_utc=2026-10-06T01:10:18.951136Z
exit=0

````

### `c013-paths-lstat-before-git.out` (214 bytes, sha256 `2dcf73d33cf1b896d7b4a1c021bc3e14e1f4bbbf12e3b2eff898792adc386ff0`)

````text
/var/tmp/p5-r5-rp11-h0-20261006-01-evidence	present	dir	uid=1001	gid=1001	owner=ubuntu	group=ubuntu	mode=0700	dev=2049	ino=1765916	nlink=2	size=4096	xattr_names=-
/var/tmp/p5-r5-rp11-h0-20261006-01-checkout	absent

````

### `c014-git-version.cmd` (280 bytes, sha256 `ebb972e24b60a02f9e947b51acbaf8b9e1a9006650f261b635a59c5a550c0823`)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git --version

````

### `c014-git-version.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c014-git-version.meta` (164 bytes, sha256 `a6eeaae833a6beba60ea29bd2a868ac690e1eba196fba9a12d1e68c4b10b10a0`)

````text
id=c014-git-version
hf=GIT
stdout=c014-git-version.out
stderr=c014-git-version.err
start_utc=2026-10-06T01:10:18.953165Z
end_utc=2026-10-06T01:10:18.960006Z
exit=0

````

### `c014-git-version.out` (19 bytes, sha256 `97452bcde974ef512f9552791fc4f6a3219a724877671fba270baca1a6075b74`)

````text
git version 2.53.0

````

### `c015-git-init.cmd` (752 bytes, sha256 `0ea38cb38b69467e8ba2b57949a3681a1b035183a80108d088b66a3a2f725886`)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false -c init.defaultBranch=h0-unborn init --quiet --template= -- /var/tmp/p5-r5-rp11-h0-20261006-01-checkout

````

### `c015-git-init.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c015-git-init.meta` (155 bytes, sha256 `b74a9acbb2d1256fdf194724bc2b83aedbe1cf7ce9ae276805a2a5feaa24863c`)

````text
id=c015-git-init
hf=GIT
stdout=c015-git-init.out
stderr=c015-git-init.err
start_utc=2026-10-06T01:10:18.960880Z
end_utc=2026-10-06T01:10:18.970018Z
exit=0

````

### `c015-git-init.out` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c016-git-fetch.cmd` (863 bytes, sha256 `804fbb257b65ec78a776e591f424704d106e0de92f3b6dde646f6c821ff5d155`)

````text
/usr/bin/env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https GIT_NO_REPLACE_OBJECTS=1 /usr/bin/timeout 900 /usr/bin/git -C /var/tmp/p5-r5-rp11-h0-20261006-01-checkout -c credential.helper= -c credential.interactive=never -c core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always -c http.followRedirects=false -c fetch.writeCommitGraph=false -c advice.detachedHead=false fetch --no-tags --depth=1 --no-recurse-submodules -- https://github.com/ming-themerciless/freedom-bot.git 46d1c35a029ca8287779ae87d08a370ba0a0f2ef

````

### `c016-git-fetch.err` (40 bytes, sha256 `df3408a8d5c3d94711c9bfa4361390576571cc8b42c28f477784ffaac922d128`)

````text
fatal: unable to get password from user

````

### `c016-git-fetch.meta` (160 bytes, sha256 `c3d34ac2e85e228618d7ecf4b34aa7f49e70dbb75b4184df4fcb955cf33eb8df`)

````text
id=c016-git-fetch
hf=GIT
stdout=c016-git-fetch.out
stderr=c016-git-fetch.err
start_utc=2026-10-06T01:10:18.970924Z
end_utc=2026-10-06T01:10:19.434250Z
exit=128

````

### `c016-git-fetch.out` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c017-manifest-payload.cmd` (693 bytes, sha256 `241a36fd4f02329bfddcdc702ac1142982b17029a6a503b330f005e1bd940249`)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, hashlib\nd = sys.argv[1]\nexcl = sys.argv[2:]\nfor n in sorted(os.listdir(d)):\n    if any(n.startswith(x) for x in excl):\n        continue\n    p = os.path.join(d, n)\n    st = os.lstat(p)\n    if not stat.S_ISREG(st.st_mode):\n        print("NONREGULAR " + n)\n        sys.exit(3)\n    h = hashlib.sha256()\n    size = 0\n    with open(p, "rb") as f:\n        while True:\n            b = f.read(1048576)\n            if not b:\n                break\n            h.update(b)\n            size += len(b)\n    print(h.hexdigest() + "  " + str(size) + "  " + n)\n' /var/tmp/p5-r5-rp11-h0-20261006-01-evidence c017-manifest-payload. MANIFEST.

````

### `c017-manifest-payload.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c017-manifest-payload.meta` (172 bytes, sha256 `db27728e92ce37cc5b4ece9c2de1670ade9d39cd7e2d9f49ca33d0948e6195ba`)

````text
id=c017-manifest-payload
hf=CLOSE
stdout=MANIFEST.payload
stderr=c017-manifest-payload.err
start_utc=2026-10-06T01:10:19.435688Z
end_utc=2026-10-06T01:10:19.461166Z
exit=0

````

### `c018-manifest-final.cmd` (261 bytes, sha256 `818ba495a755760a2fedc3e566466f796727aed36dd801394d40312f396a912e`)

````text
/usr/bin/python3 -I -S -c $'import sys, hashlib\nwith open(sys.argv[1], "rb") as f:\n    b = f.read()\nprint("MANIFEST.payload  sha256=" + hashlib.sha256(b).hexdigest() + "  bytes=" + str(len(b)))\n' /var/tmp/p5-r5-rp11-h0-20261006-01-evidence/MANIFEST.payload

````

### `c018-manifest-final.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c018-manifest-final.meta` (166 bytes, sha256 `4656c1284536188e19fba5dc6c1885dc84ffd580ebe1b49e9fdd9209740b5f73`)

````text
id=c018-manifest-final
hf=CLOSE
stdout=MANIFEST.final
stderr=c018-manifest-final.err
start_utc=2026-10-06T01:10:19.461885Z
end_utc=2026-10-06T01:10:19.480687Z
exit=0

````

### `c019-inventory.cmd` (1347 bytes, sha256 `fa64641d50ec2d513f57b87082d846ef28a3445ad9c0256b6191493ccd091963`)

````text
/usr/bin/python3 -I -S -c $'import os, sys, stat, pwd, grp\nd, prog, own = sys.argv[1], sys.argv[2], sys.argv[3]\nuid = pwd.getpwnam("ubuntu").pw_uid\ngid = grp.getgrnam("ubuntu").gr_gid\nfloor = os.lstat(prog).st_mtime_ns\nbad = 0\nds = os.lstat(d)\nprint("DIR\\t" + d + "\\tuid=" + str(ds.st_uid) + "\\tgid=" + str(ds.st_gid) + "\\tmode=%04o" % stat.S_IMODE(ds.st_mode))\nfor n in sorted(os.listdir(d)):\n    p = os.path.join(d, n)\n    st = os.lstat(p)\n    ok = (stat.S_ISREG(st.st_mode) and st.st_uid == uid and st.st_gid == gid\n          and stat.S_IMODE(st.st_mode) == 0o600 and st.st_nlink == 1\n          and st.st_mtime_ns >= floor)\n    if not ok:\n        bad += 1\n    note = "own-output-open" if n == own else ""\n    print("\\t".join([n, "reg" if stat.S_ISREG(st.st_mode) else "NONREG",\n                     "owner=" + pwd.getpwuid(st.st_uid)[0], "group=" + grp.getgrgid(st.st_gid)[0],\n                     "mode=%04o" % stat.S_IMODE(st.st_mode), "nlink=" + str(st.st_nlink),\n                     "fresh=" + ("yes" if st.st_mtime_ns >= floor else "NO"),\n                     "ok=" + ("yes" if ok else "NO"), note]).rstrip("\\t"))\nprint("violations=" + str(bad))\nsys.exit(1 if bad else 0)\n' /var/tmp/p5-r5-rp11-h0-20261006-01-evidence /var/tmp/p5-r5-rp11-h0-20261006-01-evidence/controller-h0-program.sh INVENTORY.owner-mode

````

### `c019-inventory.err` (0 bytes, sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

````text

````

### `c019-inventory.meta` (162 bytes, sha256 `ad9d6816cdafef7b3a69e0c243b1513469197eae53889d48cf8a4c515285fa70`)

````text
id=c019-inventory
hf=CLOSE
stdout=INVENTORY.owner-mode
stderr=c019-inventory.err
start_utc=2026-10-06T01:10:19.481423Z
end_utc=2026-10-06T01:10:19.550118Z
exit=0

````


H-0 facts await independent Codex review; OH-S2 and every later slice remain unauthorized.
