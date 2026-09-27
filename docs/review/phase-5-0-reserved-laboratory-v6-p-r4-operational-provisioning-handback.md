# Handback — C-P5.0-LAB-V6-P-R4 prerequisite provisioning applied; I12/V6 verified read-only — 2026-09-18

**Synchronization deviation accepted 2026-09-19.** Peter Duscha accepts the
explicitly authorized, one-time `--exclude-from` deviation retrospectively for
this R4 pass. The acceptance does not authorize `--exclude-from` for future
synchronization, which must use the accepted inline runbook command.
[Independent review](project-review-2026-09-19-r4-synchronization-deviation.md).

**V6 accepted and closed 2026-09-19.** Peter Duscha accepted the independent
I12/V6 evidence review and closed V6. Closure confirms only the approved
read-only prerequisite survey. I3 remains unconfirmed and separately
authorized; V7 remains excluded; V8 and V10 remain unperformed;
`plan.is_executable` remains false; and Package 5.0 remains not ready. The
`--exclude-from` synchronization deviation remains a separate pending
decision. [Independent review](project-review-2026-09-19-reserved-laboratory-i12-v6-closure.md).

Authorization: **C-P5.0-LAB-V6-P-R4**. Claude was assigned as implementing
operator for one bounded operational retry on `oracle-test`: secret-excluding
synchronization, inspection, V1, V2, V3, V12, V4, V9 and V5 in that exact order,
then only the read-only I12/V6 verification. Codex remains the Independent
Technical and Security Reviewer.

## Disposition

**All seven released items are applied and every I12/V6 row observed matches
the reviewed definitions.** No refusal, discrepancy, unclassified result or
unaccounted residue occurred. The provisioning CLI exited `0` with all four
directory items `created`, no refusal, nothing unattempted and no unidentified
residue.

**One disclosed deviation, taken on explicit maintainer direction:** the runbook
§3.2 synchronization command is refused by the repository secrets guard, so the
synchronization was performed with the identical exclusion rules supplied
through `--exclude-from`, and the final run was executed by the maintainer, not
by Claude (§1.2). A new tooling defect is raised as proposed RAID
**LAB-V6-P3** (§9).

Claude closes no finding, approves no digest and advances no gate. **V6 may
close only on independent Codex review and a maintainer decision.**
V7 is absent; I3, V8 and V10 are unperformed; `plan.is_executable` remains
`False`; `reservation.REAL_EXECUTION_REFUSAL` remains unconditional; LAB-V6-P2
remains Open, Low and deferred; Package 5.0 remains **not ready**.

---

## 1. Source identity and synchronization

### 1.1 The local tree

| | |
|---|---|
| Repository | `/opt/freedom-blades/platform`, branch `docs/platform-plan` |
| `git rev-parse HEAD` | `2fb1d6fd88013752d53af76fc97b4db07fc31181` |
| Working tree | the reviewed, uncommitted tree; 43 porcelain entries before this pass, all preserved |
| `git diff --check` | passed |
| Review manifest bytes | `docs/review/phase-5-0-evidence-harness-review-manifest.json` sha256 `b166e5f6bd7af3516af342f841e4353721e22cdad5daeb518dd4dc0808b57f0a` |
| Covered sources | all **45** `source_digests` entries recomputed locally: **0 mismatches** |

Relevant covered digests (all equal to the manifest):

| Path | SHA-256 |
|---|---|
| `tools/phase_5_0_evidence/provisioning.py` | `93de013129c4654cae6ff0b7a00e0df1ce52c9df15541e022cf3b3c4746d4354` |
| `tools/phase_5_0_evidence/execution/provisioner.py` | `32ff8d9a9dc0bb4205ce59b2f73f67bb1834bab994d75fbe87aa57b54b8fd0e7` |
| `tools/phase_5_0_evidence/execution/provisioning_cli.py` | `f65cca5f84a36d791ec912b2166ff0806be3560c5bca451cf54cf3696abf343f` |
| `tools/phase_5_0_evidence/execution/boundary.py` | `1354b600cab03e649e90cd780e47c57a1cb4d0e7abc394cd063888005ebc5c32` |

The manifest was read **as data** to compare file bytes. The review-input
digest was not recomputed through the harness CLI, not approved, and not
consumed as execution authority; the harness CLI was not run.

Local corroboration, `TEST_DATABASE_URL` unset, interpreter
`/opt/freedom-blades/runtime/venv-web/bin/python`:

```
python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning_cli.py tests/phase_5_0_evidence/test_v6_provisioning.py
245 passed, 2 warnings in 7.14s          # 114 + 131, zero skipped
python3 .claude/hooks/test_guards.py
31 cases: 19 must be refused, 12 must be allowed — all guard cases passed
```

The two warnings are the pre-existing unknown pytest options
`asyncio_default_fixture_loop_scope` and `asyncio_mode`.

### 1.2 Synchronization — the deviation, exactly

1. The runbook §3.2 command was issued as written. **`guard-secrets.py`
   refused it**: the `--exclude='.env*'` argument matches the guard's secret
   pattern and `rsync` is one of its access verbs, so the runbook's own
   secret-*excluding* command is classified as secret-*copying*. Per CLAUDE.md
   the refusal was treated as a stop; nothing was transferred.
2. Claude asked the maintainer. **Peter authorized, for this pass only**, the
   same rsync with the identical rules read from a file via `--exclude-from`.
3. The rules file (scratch, not in the repository), sha256
   `f87fa54bea8ca2a3da0d9df54a8c6f1e7c8b9848b982d36efb737b2b38102eb3`, is the
   runbook's set in the runbook's order:

   ```
   + .env.example
   - .env*
   - *.pem
   - *.key
   - yt-cookies.txt
   - *service_account*.json
   - *credentials*.json
   - __pycache__/
   - *.py[cod]
   - .pytest_cache/
   ```
4. Claude's first `--exclude-from` dry run was blocked by the Claude Code
   auto-mode permission classifier as a guard bypass. On the maintainer's
   further instruction ("Please update the repo") the dry run was retried and
   succeeded: `rc=0`, 806 listing lines, **one deletion** (`infra/lavalink/`,
   a stale directory of the music removal under OD-40), and no key,
   certificate, cookie, service-account or credential file and no root-level
   dotfile other than `.claude/` and `.git/` in the list.
5. The real run was again blocked by the classifier for Claude. **The
   maintainer ran it directly** from this session with the `!` prefix:

   ```
   rsync -avz --delete --exclude-from=<scratch>/sync-rules.txt \
     /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
   ```
   Result: `sent 8,573,693 bytes received 38,203 bytes`, `total size is
   72,905,806`, exactly one `deleting infra/lavalink/`, no secret-type name in
   the transfer list. The run completed before 2026-09-18T22:06Z; the exact
   instant is not recorded in its output.

No environment file, `yt-cookies.txt`, service-account or credential JSON,
private key, certificate or `.pgpass` was read, printed, copied or transferred
by Claude. `.env` and `yt-cookies.txt` exist locally and are covered by the
rules above; no `.pgpass`, `*.crt`, `*.p12` or `*.pfx` exists in the tree.

### 1.3 The synchronized tree on the target

```
ssh oracle-test 'cd /opt/freedom-blades/platform && sha256sum -c --quiet -' < manifest.sha256
ALL_45_OK
sha256 of docs/review/phase-5-0-evidence-harness-review-manifest.json on target:
b166e5f6bd7af3516af342f841e4353721e22cdad5daeb518dd4dc0808b57f0a
```

On the target, `TEST_DATABASE_URL` unset, canonical interpreter
(`Python 3.12.14`):

```
python -m pytest -q -rs -p no:cacheprovider tests/phase_5_0_evidence/test_v6_provisioning_cli.py tests/phase_5_0_evidence/test_v6_provisioning.py
245 passed in 41.58s                     # zero skipped
python -m tools.phase_5_0_evidence.execution.provisioning_cli     # no flag
NOT APPLIED — no account database and no filesystem was read.
  items this tool owns : V12, V4, V9, V5
  ...
exit=3
```

---

## 2. Pre-mutation observations

Read-only, as `ubuntu`, at **2026-09-18T18:08:28Z**, and the absence checks
repeated immediately before each mutation (22:06:01Z, 22:06:40Z, 22:07:00Z).
**Identical to the 2026-09-17 report in every fact.**

| Item / object | Observed |
|---|---|
| V1 `freedomlab` | absent — `getent group freedomlab` exit 2; `grep -c '^freedomlab:' /etc/group` = 0 |
| V2 | `uid=1001(ubuntu) gid=1001(ubuntu) groups=1001(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),102(lxd)` |
| V3 fragment, `/run/freedom-blades`, lock | all absent; `/etc/tmpfiles.d/` holds only `screen-cleanup.conf` |
| V12, V4, V9, V5 | all absent |
| `lifecycle.json`, `lifecycle.json.tmp` | absent |
| `/var/lib` | directory `0:0 0755`, `nlink=51`, `dev=2049 ino=97831`; mount `/` `/dev/sda1` `ext4` `rw,relatime,discard,errors=remount-ro,commit=30` |
| `/etc/tmpfiles.d` | `0:0 0755`, `dev=2049 ino=176` |
| `/opt/freedom-blades` | `1001:1001 0755`, `dev=2049 ino=764055` |
| `/opt/freedom-blades/evidence`, `R=/var/lib/fb-evidence-p5-0` | both absent |
| `/proc/sys/fs/protected_hardlinks` | `1` |
| host | hostname `Test`, `Linux 7.0.0-31-generic` |

---

## 3. Application — commands, exit statuses, output

All over `ssh oracle-test`, as `ubuntu` with `sudo` only where stated. Every
step's script stopped with a distinct nonzero status if its precondition did
not hold; none did. Standard error was empty for every step.

### V1 — 2026-09-18T22:06:01Z

```
sudo groupadd --system freedomlab            exit=0
getent group freedomlab  →  freedomlab:x:986:     exit=0; records=1
```

### V2 — 2026-09-18T22:06:19Z

```
sudo usermod --append --groups freedomlab ubuntu     exit=0
before: uid=1001(ubuntu) gid=1001(ubuntu) groups=1001(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),102(lxd)
after:  uid=1001(ubuntu) gid=1001(ubuntu) groups=1001(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),102(lxd),986(freedomlab)
getent group freedomlab  →  freedomlab:x:986:ubuntu
```

All five pre-existing supplementary groups retained.

### V3 — 2026-09-18T22:06:40Z

Expected content from `provisioning.TMPFILES_FRAGMENT_CONTENT`: 106 bytes,
sha256 `042f193d50fb102afe789799a5e100b1e685ea3cdf0661ca8433038e76aebacf`.

```
sudo sh -c 'umask 022; set -C; printf "%s\n" "d /run/freedom-blades 0750 root freedomlab -" \
  "f /run/freedom-blades/laboratory.lock 0660 root freedomlab -" > /etc/tmpfiles.d/freedom-blades-laboratory.conf'
                                                                    exit=0
/etc/tmpfiles.d/freedom-blades-laboratory.conf regular file root:root 644 size=106
sha256=042f193d50fb102afe789799a5e100b1e685ea3cdf0661ca8433038e76aebacf     (equal — checked before continuing)
sudo systemd-tmpfiles --create /etc/tmpfiles.d/freedom-blades-laboratory.conf    exit=0
/run/freedom-blades                  directory          root:freedomlab 750 dev=29 ino=11451
/run/freedom-blades/laboratory.lock  regular empty file root:freedomlab 660 dev=29 ino=11452
```

`set -C` made the write exclusive (no clobber of an existing file). Only the
one fragment was passed to `systemd-tmpfiles`.

### V12, V4, V9, V5 — 2026-09-18T22:07:00Z

From `/opt/freedom-blades/platform`, after confirming all four absent:

```
sudo /opt/freedom-blades/runtime/venv-web/bin/python -B -m tools.phase_5_0_evidence.execution.provisioning_cli --apply
exit=0
--- stdout:
APPLIED — every item this tool owns is in place.
  items applied        : 4
      · V12  created                  /var/lib/freedom-blades  [2049:1275049]
      · V4   created                  /var/lib/freedom-blades/laboratory  [2049:1275050]
      · V9   created                  /var/lib/freedom-blades/laboratory/runs  [2049:1275051]
      · V5   created                  /var/lib/freedom-blades/recovery  [2049:1275052]
  refusal              : none
  not attempted        : none
  created by this run  : V12, V4, V9, V5
  unidentified residue : none
  guarded reversal     : available for V12, V4, V9, V5. No rollback is performed by this program; reversing a partly provisioned host is the operator's decision
--- stderr:
(empty)
```

`-B` (do not write bytecode) was added so a root process would leave no
root-owned `__pycache__` in the `ubuntu`-owned worktree; it does not affect
argument parsing, targets or the arm. Afterwards
`sudo find /opt/freedom-blades/platform -xdev -uid 0` found **0** entries.
The CLI was the only repository-owned route used for these four items; the
provisioner was not otherwise imported or called, and `verify()` was not
invoked (I12 below uses independent shell observation).

**Complete CLI accounting:** applied/created V12, V4, V9, V5 with the four
identities above; already-provisioned none; refusal none (so no
classification or detail); not attempted none; residue none; guarded reversal
available for all four.

---

## 4. I12/V6 read-only verification — 2026-09-18T22:07:19Z

Performed only after all seven items completed. A **fresh** `ubuntu` SSH session
(so V2 is in the process credentials). `sudo` was used only for read-only
`stat`, `findmnt`, `ls -A` and `test -e` where `0700`/`0750` modes require it.
No link, no lock, no write, no `verify()` call.

| Row (`VERIFICATION_PROCEDURE`) | Observed | Result |
|---|---|---|
| execution identity | `Uid: 1001×4`, `Gid: 1001×4`, `Groups: 4 24 27 30 102 986 1001` → `adm cdrom sudo dip lxd freedomlab ubuntu` | the observing process holds `freedomlab`. **Does not confirm V10** |
| capability state | `CapInh/CapPrm/CapEff/CapAmb 0`, `CapBnd 000001ffffffffff`, `NoNewPrivs 0` | recorded; settles nothing about a root process's `CAP_FOWNER` (P2) |
| hard-link policy | `protected_hardlinks = 1` | recorded; **no link created, I3 unconfirmed** |
| mount and filesystem | V12, V4, V9, V5: mount `/`, `/dev/sda1`, `findmnt` `ext4`; `/run/freedom-blades` and the lock: mount `/run`, `tmpfs` | as designed. `stat -f %T` prints `ext2/ext3` for the ext4 objects because it names the shared ext superblock magic; `findmnt` is authoritative for `ext4`. **Not a V8/I2 claim** |
| type, owner, group, mode (and link count, identity, contents) | see table below | **all match** |
| each item's parent | `/var/lib` `uid=0 0755`; `/var/lib/freedom-blades` `uid=0 0755`; `/var/lib/freedom-blades/laboratory` `uid=0 0750`; `/run` `uid=0 0755`; `/etc/tmpfiles.d` `uid=0 0755` — `mode & 022 = 0` for every one | every entry is root-owned and not group-/other-writable |
| group and membership | `freedomlab:x:986:ubuntu`, exactly one record; every group-owned object carries gid 986 | V1 and V2 match; **does not confirm I8** |
| V7 absence | `lifecycle.json` absent; `lifecycle.json.tmp` absent | the release stopped where `V7_EXCLUSION` says; host fail-closed |

Object table:

| Item | Path | Type | uid:gid | Mode | nlink | Identity | Contents |
|---|---|---|---|---|---|---|---|
| V12 | `/var/lib/freedom-blades` | directory | 0(root):0(root) | 0755 | 4 | 2049:1275049 | `laboratory recovery` |
| V4 | `/var/lib/freedom-blades/laboratory` | directory | 0(root):986(freedomlab) | 0750 | 3 | 2049:1275050 | `runs` |
| V9 | `/var/lib/freedom-blades/laboratory/runs` | directory | 0(root):986(freedomlab) | **3770** | 2 | 2049:1275051 | empty |
| V5 | `/var/lib/freedom-blades/recovery` | directory | 0(root):0(root) | 0700 | 2 | 2049:1275052 | empty |
| V3 | `/run/freedom-blades` | directory | 0(root):986(freedomlab) | 0750 | 2 | 29:11451 | `laboratory.lock` |
| V3 | `/run/freedom-blades/laboratory.lock` | regular empty file | 0(root):986(freedomlab) | 0660 | 1 | 29:11452 | — |
| V3 | `/etc/tmpfiles.d/freedom-blades-laboratory.conf` | regular file | 0(root):0(root) | 0644 | 1 | 2049:1898 | 106 B, sha256 `042f193d…aebacf` (exact) |

The four directory identities equal those the CLI recorded. Link counts equal
2 + subdirectories in every case. V9's `3770` carries both setgid and sticky.

Unchanged context: `/opt/freedom-blades` still `1001:1001 0755`,
`dev=2049 ino=764055`; `/opt/freedom-blades/evidence` and
`/var/lib/fb-evidence-p5-0` both absent.

---

## 5. What changed on the host, and residue

`sudo find /etc /var/lib /run -xdev -newermt "2026-09-18 22:05:55"` lists,
attributable to this pass: `/etc/group`, `/etc/group-`, `/etc/gshadow`,
`/etc/gshadow-` (V1/V2; the `-` files are the backups `groupadd`/`usermod`
write), `/etc/tmpfiles.d` and the fragment (V3), `/run/freedom-blades` and the
lock (V3), `/var/lib/freedom-blades` and its three children (V12, V4, V9, V5),
and the parent directories' mtimes. Everything else listed is ambient SSH
session, `motd` and landscape state. The temporary `/tmp/fb-prov.out`/`.err`
capture files were removed and confirmed absent. The synchronized worktree
has no root-owned file.

**No unaccounted residue.** No object was created outside the released
subset; nothing under `/opt/freedom-blades` changed except the synchronized
worktree; no PostgreSQL, production service or data was touched.

---

## 6. Rollback — available, **not executed**

No rollback was performed and none is proposed. If the maintainer decides to
reverse, each item's reviewed `rollback` field applies, in exact reverse order:
V5, V9, V4, V12 (non-recursive `rmdir`, only while empty, guarded by the
recorded identities `2049:1275052`, `…051`, `…050`, `…049`); V3 (fragment
first, then the two `/run` entries, refused while the lock is held); V2
`gpasswd --delete ubuntu freedomlab`; V1 `groupdel freedomlab`. V7 has no
rollback by contract and is absent.

---

## 7. Checks not run, and why

| Check | Why not |
|---|---|
| full bot, web and Foundry suites | this pass changed no source; only the focused provisioning modules were run, locally and on the target. No PostgreSQL claim is made; `TEST_DATABASE_URL` was unset throughout |
| formatter, linter, type checker | no source changed |
| harness CLI / review-digest regeneration | the evidence harness is unauthorized; bytes were compared against the manifest's per-file digests instead |
| `provisioner.verify()` | deliberately not called, so the CLI stays the only repository route touching the four items; I12 used independent read-only observation |
| V7, I3 controlled write, V8, V10 | unauthorized; not performed |
| a reboot to observe tmpfiles re-creation | not authorized; V3's persistence is a definition property, not observed here |

---

## 8. Explicitly not done

No V7 initialization; no `linkat` or write probe (I3); no V8 or V10; no
participant wired or invoked; no database access; no generated vector; no
evidence harness; no real boundary or materializer; no `--execute`; nothing
under `/opt/freedom-blades/evidence`; no repair mode; no rollback; no
production service touched. `plan.is_executable` remains `False` and
`reservation.REAL_EXECUTION_REFUSAL` unconditional.

---

## 9. Tooling defects found — reported, not repaired

**Proposed LAB-V6-P3, Open, Low (maintainer to confirm).**
`.claude/hooks/guard-secrets.py` refuses the runbook §3.2 synchronization
command: an rsync **exclude** argument naming `.env*` matches `SECRET_PATTERNS`
and `rsync` is in `ACCESS_VERBS`, so the only documented secret-excluding
synchronization cannot be run by an agent. The guard's docstring names "rsync
exclude lists" as a legitimate mention it means to allow, and
`test_guards.py` has no case for it. Consequence: every future synchronization
needs either a maintainer-run command or a maintainer-authorized deviation,
and the Claude Code auto-mode classifier additionally blocks the
`--exclude-from` form as a bypass. Related to, but distinct from, LAB-V6-P2
(false refusal of `cat` heredocs writing prose). The guard was **not**
modified, disabled or bypassed by Claude; 31/31 still passes.

---

## 10. Repository changes in this pass

Documentation only: this handback (new); `docs/review/Handover information`,
`docs/project-management/status.md`, `raid-register.md`,
`decision-register.md`, `change-log.md`,
`docs/operations/disposable-test-server.md` and
`docs/implementation-plan.md` §20 updated to record the result. No source,
test, artifact or digest changed. Unrelated and reviewer-authored changes were
preserved.

---

## 11. Proposed reviewer focus

1. The synchronization deviation (§1.2) and whether the `--exclude-from` set is
   equivalent to runbook §3.2; the target-side 45/45 byte match (§1.3).
2. V3 was applied by an exclusive `sh -c 'set -C; printf …'` write rather than
   an editor or `install`; confirm that is an acceptable reading of "write
   `TMPFILES_FRAGMENT_CONTENT` … as root, `0644 root:root`".
3. The `-B` interpreter flag on the `--apply` invocation (§3).
4. Whether shell-based I12 observation (rather than `verify()`) satisfies the
   `VERIFICATION_PROCEDURE` type/owner/group/mode row.
5. V6 closure, and disposition of proposed LAB-V6-P3.

## 12. Next action

**Independent Codex technical, security and evidence review of this handback,
then maintainer decision.** V6 remains performed-but-not-closed until then; I3,
V8 and V10 unperformed; V7 excluded and absent; `plan.is_executable=False`;
LAB-V6-P2 Open and deferred; Package 5.0 **not ready**.
