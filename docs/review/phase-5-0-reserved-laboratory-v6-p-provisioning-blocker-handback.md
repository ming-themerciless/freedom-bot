# Handback — C-P5.0-LAB-V6-P stopped before mutation: no reviewed operator invocation — 2026-09-17

Authorization: **C-P5.0-LAB-V6-P**. Claude was assigned as implementing
operator for one bounded operational pass on `oracle-test`: apply V1, V2, V3,
V12, V4, V9 and V5 in that order, then perform only the read-only I12/V6
verification.

## Disposition — stopped at the mandatory pre-application gate

**Nothing was applied. No item of the released prerequisite subset was created,
changed, adopted or repaired, and the host is exactly as it was.**

The pass stopped on the application rule the assignment itself states:

> If the repository has no already reviewed operator invocation that can drive
> the directory provisioner exactly as approved, stop before mutation and
> report that gap. Do not add source, invent an entry point or execute an
> improvised generated vector in this operational pass.

That condition holds. It is the blocker this handback returns, and it is
reported for independent Codex technical and security review and maintainer
direction. **Claude closes no finding, approves no digest and advances no
gate.**

---

## 1. Source identity and secret exclusions

**No synchronization to `oracle-test` was performed**, and the reason is in §7.
The identity below is the local repository tree that was read and inspected.

| | |
|---|---|
| Repository | `/opt/freedom-blades/platform` |
| Branch | `docs/platform-plan` |
| `git rev-parse HEAD` | `2fb1d6fd88013752d53af76fc97b4db07fc31181` |
| Working tree | the reviewed submitted tree, uncommitted, as the accepted R1 review read it |
| `git diff --check` | passed |

Exact bytes of the sources this pass depends on:

| Path | SHA-256 |
|---|---|
| `tools/phase_5_0_evidence/provisioning.py` | `93de013129c4654cae6ff0b7a00e0df1ce52c9df15541e022cf3b3c4746d4354` |
| `tools/phase_5_0_evidence/execution/provisioner.py` | `b6bef14eefaf197fc174d77ef3b06afb79ff9e6895a2650d7bddc297cfe258c5` |
| `tests/phase_5_0_evidence/test_v6_provisioning.py` | `b582b1e8135a8dd47eb1f756e1b898b70aa383cd58487819197844a019510b3e` |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | `5a866a0d9b3e34afc7898e8eb74f1e943efe67fd3d784844c0385ad5ef59e5ce` |

**Secret exclusions.** No environment file, `yt-cookies.txt`, service-account or
credential JSON, private key, certificate or `.pgpass` was read, printed,
copied or transferred. Because no `rsync` ran, the runbook §3.2 exclusion set
was not exercised; it remains the procedure for the pass that does synchronize.

**Corroboration that this tree is the reviewed one.** Restricted local pass,
`TEST_DATABASE_URL` explicitly unset, interpreter
`/opt/freedom-blades/runtime/venv-web/bin/python` (3.12.3, pytest 9.1.1) **on
the repository host, not on `oracle-test`**:

```
python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning.py
131 passed, 2 warnings in 0.63s          # zero skipped
python3 .claude/hooks/test_guards.py
31 cases: 19 must be refused, 12 must be allowed — all passed
```

131 passed with zero skips and the two pre-existing unknown-pytest-option
warnings is exactly the figure the accepted independent R1 review recorded.
The two warnings are `asyncio_default_fixture_loop_scope` and `asyncio_mode`
and are unrelated to this work.

---

## 2. Pre-application observations

Every observation below is **read-only**: `getent`, `id`, `stat`, `ls`,
`findmnt`, `grep` and `cat` of `/proc`. No `sudo` mutation, no write, no
`mkdir`, no link, no lock.

### 2.1 The seven released items

| Item | Object | Observed |
|---|---|---|
| V1 | group `freedomlab` | **Absent.** `getent group freedomlab` exits 2 with no record; `grep -c '^freedomlab:' /etc/group` is `0` |
| V2 | `ubuntu` in `freedomlab` | **Absent**, necessarily — V1 does not exist |
| V3 | `/etc/tmpfiles.d/freedom-blades-laboratory.conf` | **Absent.** `/etc/tmpfiles.d/` holds only `screen-cleanup.conf` (`root:root 0644`) |
| V3 | `/run/freedom-blades` | **Absent.** No `freedom-*` entry exists under `/run` |
| V3 | `/run/freedom-blades/laboratory.lock` | **Absent** |
| V12 | `/var/lib/freedom-blades` | **Absent** |
| V4 | `/var/lib/freedom-blades/laboratory` | **Absent** |
| V9 | `/var/lib/freedom-blades/laboratory/runs` | **Absent** |
| V5 | `/var/lib/freedom-blades/recovery` | **Absent** |

**No item is partially present, and none exists in a non-compliant form.** The
delta is therefore the whole subset; no item would have been verified rather
than created.

### 2.2 The parents

| Parent | Observed | Meets the rule |
|---|---|---|
| `/var/lib` | real directory, **not** a symbolic link; `uid=0(root) gid=0(root) mode=0755`, `nlink=51`, `st_dev=2049`, `st_ino=97831` | **Yes.** Owned by the applying identity (`root`), and `mode & 0o022 == 0` — no group- or other-write bit |
| `/var/lib` mount | `/` on `/dev/sda1`, `ext4`, `rw,relatime,discard,errors=remount-ro,commit=30` | the root filesystem the durability and hard-link arguments were made about |
| `/etc/tmpfiles.d` | `root:root 0755` | root-only entry |
| `/run` | tmpfs, as designed; V3's objects are boot-time artifacts | consistent with V3's persistence field |

### 2.3 The other mandatory checks

| Check | Result |
|---|---|
| synchronized repository bytes are the reviewed submitted tree | **Not established on the target.** See §7 — no synchronization was performed, and the host's copy is stale (§2.4) |
| `freedomlab` does not exist, or resolves to exactly one record | **Satisfied** — it does not exist. Zero records, so no ambiguity |
| `ubuntu` still has the five supplementary groups V6 observed | **Satisfied.** `id ubuntu` → `uid=1001(ubuntu) gid=1001(ubuntu) groups=1001(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),102(lxd)`. The five are `adm`, `cdrom`, `sudo`, `dip`, `lxd`, unchanged since V6 |
| neither `lifecycle.json` nor `lifecycle.json.tmp` exists | **Satisfied.** Both absent — necessarily, since V4 does not exist |
| no run entry or recovery object exists under a target | **Satisfied.** No target exists, so nothing is inside one. Neither an idempotent application nor a guarded reversal would refuse on residue |
| `/var/lib` is a real directory owned by the applying identity, not group- or other-writable | **Satisfied** — §2.2 |
| V11 `/opt/freedom-blades/evidence` neither created nor used | **Satisfied.** `/opt/freedom-blades/evidence` is absent. `/opt/freedom-blades` is `1001:1001 0755` and was **not** modified; no ownership change was made or attempted, and nothing was provisioned under `/opt` |

### 2.4 Two further observations, recorded because they matter to the next pass

**The host's repository copy is stale and does not contain the applier.**
`/opt/freedom-blades/platform` on `oracle-test` is dated 5 September and
`tools/phase_5_0_evidence/execution/provisioner.py` is **not present there**.
Any pass that does drive a repository-owned invocation must synchronize first
under runbook §3.2.

**Canonical `R` is absent.** `/var/lib/fb-evidence-p5-0` does not exist. It is
created by the reviewed concrete plan, not by prerequisite provisioning, and
this pass neither created nor touched it.

### 2.5 Ambient facts, recorded as context and **not** as I12/V6 rows

These were read while inspecting, and they are stated here only so the record
is complete. **They are not the I12/V6 verification**, which was not performed
(§6):

* `/proc/sys/fs/protected_hardlinks` = `1`;
* the observing process was `ubuntu`: `Uid: 1001`, `Gid: 1001`,
  `Groups: 4 24 27 30 102 1001`;
* `CapInh`, `CapPrm`, `CapEff`, `CapAmb` all zero, `CapBnd 000001ffffffffff`,
  `NoNewPrivs: 0`.

No conclusion is drawn from any of them. In particular **I3 remains
unconfirmed**: no link was created, and a policy value is not a successful
`linkat`.

---

## 3. The blocker — no reviewed operator invocation exists

### 3.1 What the assignment requires

V12, V4, V9 and V5 must be applied **through the reviewed directory provisioner
and its production `directory_targets()` values, armed explicitly and running
as root**, and explicitly not through `mkdir -p`, `install -d`, a second
applier or an unreviewed helper.

Driving it exactly as approved requires all four of:

1. `provisioner.directory_targets()` with its default production layout;
2. a `DirectoryProvisioner` constructed with a real `OwnershipLookup` over the
   host's account database;
3. `armed=True`, which is one explicit act and is `False` by default; and
4. a process whose effective UID is already `root`, which
   `_require_provisioning_identity` demands before anything is created.

### 3.2 What the repository actually has

**No entry point performs steps 2–4.** Every reference to the applier outside
its own module is a test:

* `tools/phase_5_0_evidence/execution/provisioner.py` defines
  `DirectoryProvisioner`, `directory_targets()` and `released_operator_steps()`
  and **has no `main` and no `if __name__ == "__main__"` block**;
* `tools/phase_5_0_evidence/execution/cli.py` — the harness CLI — **does not
  import `provisioner` at all**. Its options are `--manifest`, `--manifest-out`,
  `--render`, `--execute`, `--confirm-target`, `--reviewed-digest`, `--run-id`
  and the reservation/quiescence arguments. There is no provisioning
  subcommand, and its `--execute` branch is the reviewed plan's execution,
  which this pass forbids;
* `tools/phase_5_0_evidence/execution/evidence_cli.py` classifies observations
  and takes `--observations`, `--run-id`, `--synthetic` and `--artifact-out`.
  It touches no provisioning item;
* a scan of `tools/`, `infra/`, `application/`, `adapters/` and `main.py` for
  `DirectoryProvisioner` or `directory_targets` returns **only
  `provisioner.py` itself**;
* the sole construction of an **armed** provisioner anywhere is
  `tests/phase_5_0_evidence/test_v6_provisioning.py:177`, and it takes
  `FakeAccounts` — an injected lookup that resolves the declared owner to the
  test process's own ids — over a `tmp_path` layout. That is deliberate and is
  what lets the suite drive the real mechanism without creating one object
  under `/run` or `/var/lib`. **It is not an operator invocation**, it does not
  use the production `directory_targets()` defaults, and running the suite as
  root to make it touch the real paths would be an improvised vector, not the
  reviewed route.

### 3.3 Why this is a stop and not something to route around

The mechanism is reviewed and accepted; **the way an operator reaches it is
not, because it does not exist.** Closing the gap means writing new source — a
CLI subcommand or an operator script that constructs the lookup, arms the
provisioner, calls `apply(directory_targets())` and renders the
`ProvisioningRun`. This authorization forbids exactly that: *do not add source,
invent an entry point or execute an improvised generated vector in this
operational pass.* Adding one would also put unreviewed code on the applying
path of a root-run mutation, and it would need its own independent technical
and security review before it applied anything — which is the review this
handback returns for.

The three operator items are not affected by the gap: V1's `groupadd --system
freedomlab`, V2's `usermod --append --groups freedomlab ubuntu` and V3's
fragment are out-of-band operator steps that the repository never performs.
**They were not applied either**, because the assignment fixes the order
V1 → V2 → V3 → V12 → V4 → V9 → V5 and applying the first three would leave a
host with a group, a membership and a `/run` lock inode whose reason to exist —
the four directories, the record and the ledger — could not follow in the same
pass. Splitting a released ordered subset is a maintainer's decision, not an
implementer's.

---

## 4. Commands and invocations run, in order

Every one is read-only. No repository-owned invocation was run against the
target, because none exists (§3).

**On `oracle-test`, over SSH as `ubuntu`, no `sudo` mutation:**

1. `echo CONNECTED; hostname; id; uname -sr`
2. `getent group freedomlab` · `grep -c '^freedomlab:' /etc/group`
3. `id ubuntu` · `getent group | awk` for `ubuntu`'s memberships
4. `ls -l /etc/tmpfiles.d/freedom-blades-laboratory.conf` · `ls -la /etc/tmpfiles.d/`
5. `stat` on `/run/freedom-blades` and `/run/freedom-blades/laboratory.lock`
6. `stat` and `findmnt --target` on `/var/lib`
7. `stat` on `/var/lib/freedom-blades`, `…/laboratory`, `…/laboratory/runs`, `…/recovery`
8. `stat` on `…/laboratory/lifecycle.json` and `…/laboratory/lifecycle.json.tmp`
9. `stat` on `/opt/freedom-blades` and `/opt/freedom-blades/evidence`
10. `stat` on `/var/lib/fb-evidence-p5-0`
11. `ls -ld /var/lib` · `cat /proc/sys/fs/protected_hardlinks` · `grep` of `/proc/self/status`
12. `ls -ld /opt/freedom-blades/platform` and one `ls` of the applier's path there
13. `ls -la /run | grep -i freedom`

**Locally, in the repository:**

14. `git rev-parse HEAD`, `git status --porcelain`, `git diff --stat`, `git diff --check`
15. `sha256sum` of the four sources in §1
16. an AST/text scan of `tools/`, `infra/`, `application/`, `adapters/`, `main.py` for `DirectoryProvisioner` and `directory_targets`
17. `python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning.py`, `TEST_DATABASE_URL` unset
18. `python3 .claude/hooks/test_guards.py`

---

## 5. Before-and-after facts, and the `ProvisioningRun`

**Before and after are the same, for every one of the seven items.** The
"before" facts are §2.1 and §2.2 — every item absent, `/var/lib`
`uid=0 gid=0 mode=0755 dev=2049 ino=97831`. No numeric uid, gid or mode changed
anywhere on the host, because nothing was applied.

**There is no directory `ProvisioningRun` to report.** `apply()` was never
called, so there is no `applied` collection, no created-versus-already-provisioned
outcome, and no recorded `(st_dev, st_ino)` identity. Reporting an empty run
would imply the applier ran and found nothing to do; it did not run.

| | |
|---|---|
| Items applied | **none** |
| Items verified as already compliant | **none** |
| Items refused by the applier | **none** — it was never invoked |
| Items not attempted | **all seven**: V1, V2, V3, V12, V4, V9, V5 |
| Residue | **none.** No object was created, so there is no `CREATED_IDENTITY_UNKNOWN` residue and nothing for an operator to account for |

---

## 6. The I12/V6 verification was not performed

`provisioning.VERIFICATION_PROCEDURE` is defined as the post-provision
repetition of the read-only survey, and the assignment scopes it to *after all
seven items apply or verify cleanly*. They did not, so **the procedure was not
run and I12 is unperformed.** Every row and why it was not run:

| Row | Not run because |
|---|---|
| the execution identity | the procedure was not entered. `/proc/self/status` was read as ambient context (§2.5) and is **not** offered as this row |
| the capability state | same — read as context, not as a procedure row |
| the hard-link policy | same. `protected_hardlinks=1` is context; **it creates no link and I3 stays unconfirmed** |
| mount point and filesystem type per provisioned directory | there are no provisioned directories. `/var/lib`'s mount was read as the parent check, not as this row |
| exact type, owner, group, numeric mode, link count and contents through `verify()` | `verify()` was never called; its four targets do not exist |
| each item's parent ownership and write bits | only `/var/lib` was read, as a pre-application precondition. V4's, V9's and V5's parents do not exist |
| the unique `freedomlab` record, `ubuntu` membership and every group-owned gid | the group does not exist and no group-owned object exists |
| absence of `lifecycle.json` and `lifecycle.json.tmp` | **both are confirmed absent** (§2.1) — but as a pre-application observation, not as a verification row, because the row's meaning is *the release stopped where it says it stops* and the release did not start |

**Explicit confirmation, on its own:** both `lifecycle.json` and
`lifecycle.json.tmp` are absent under `/var/lib/freedom-blades/laboratory`,
which is itself absent. V7 is untouched and remains excluded.

---

## 7. Checks not run, and why

| Check | Why not |
|---|---|
| synchronization to `oracle-test` under runbook §3.2 | authorized, but **deliberately not performed**. The pass stops before mutation and no repository-owned invocation will run on the target, so synchronizing would write the repository tree to the host for no purpose in this pass. It is the first step of the pass that does apply |
| the complete I12/V6 verification | §6 — the items are not applied |
| V6's closure | it remains **performed 2026-09-16 and not closed**. This pass observed the same absences and closes nothing |
| I3 controlled write / any `linkat` probe | not authorized, and not performed |
| V7 / lifecycle-record initialization | not authorized, and not performed |
| V8, V10 | not authorized, unperformed |
| the full bot, web and Foundry suites | not run in this pass. It changes no source: the only repository edits are this handback and the register updates §9 lists. The focused module and the guards were run (§1). **Every database-marked test would skip with `TEST_DATABASE_URL` unset**, so no PostgreSQL claim is made here |
| formatter, linter, type checker | not run; no source file changed |

---

## 8. Rollback for what this pass created

**Nothing was created, so there is nothing to roll back.** No reversal is
proposed and none is executed.

Recorded for the pass that does apply, and **not executed here**, the reviewed
reversal is each item's own `rollback` field, in the exact reverse of the
application order:

1. V5 — non-recursive `rmdir` of `/var/lib/freedom-blades/recovery`, on the
   recorded `(st_dev, st_ino)` guard, only while empty;
2. V9 — non-recursive `rmdir` of `…/laboratory/runs`, **before** V4's, only
   while it holds no run file;
3. V4 — non-recursive `rmdir` of `…/laboratory`, after V9 and after V7's record
   are gone;
4. V12 — non-recursive `rmdir` of `/var/lib/freedom-blades`, only while empty
   and only after the recorded identity matches;
5. V3 — remove the fragment **first**, then the two `/run` entries; the reverse
   order re-creates them at the next boot, and the removal refuses while any
   participant holds the lock;
6. V2 — `gpasswd --delete ubuntu freedomlab`, which touches no other group; and
7. V1 — `groupdel freedomlab`, only after V2 and after every group-owned object
   is removed or re-owned.

V7 has no rollback by contract, not by omission. It is excluded and absent.

---

## 9. Repository changes in this pass

Documentation only. No source file, test, artifact or digest changed.

* **added** this handback;
* **updated** `docs/review/Handover information`, `docs/project-management/status.md`,
  `docs/project-management/raid-register.md`,
  `docs/project-management/decision-register.md`,
  `docs/project-management/change-log.md` and
  `docs/operations/disposable-test-server.md` to record the observed facts.

Every unrelated and reviewer-authored change in the working tree was preserved;
`git status` was inspected before and after.

---

## 10. One defect found in the tooling, reported and not repaired

`.claude/hooks/guard-secrets.py` refused a `cat > <file> <<'EOF'` heredoc that
wrote **this document**, because the document's prose names an environment file
beside the verb `cat`. The guard's own docstring states the intended rule —
*"Writing about it is allowed; `cat`ting it is not"* — so the implementation is
narrower than its stated contract: the verb list matches `cat` in a
write-redirect as well as in a read. No secret was read, printed or copied, and
the document was written through the file tool, which the guard gates on path.

**The guard was not modified, disabled or bypassed**, and
`python3 .claude/hooks/test_guards.py` still passes 31/31. This is reported as
a defect for a maintainer to dispose of, not repaired here: changing a guard is
outside this authorization.

---

## 11. What was not used

**Explicitly**: V7 was not initialized; I3 was not tested and no `linkat` or
any other write probe was performed; V8 and V10 were not performed; no
participant was wired or invoked; no database was accessed or mutated; no
generated vector was executed; the evidence harness was not run; no real
boundary or materializer was used; no object under `/opt/freedom-blades/evidence`
was created or used; and `--execute` was not passed to anything.

`plan.is_executable` remains `False` and
`reservation.REAL_EXECUTION_REFUSAL` remains unconditional. The host has V7
absent and remains fail-closed for all seven participants — here because it is
unprovisioned entirely.

---

## 12. Next action

**Independent Codex technical and security review of this blocker**, then
maintainer direction on how the directory items are to be reached. The decision
is Peter's, and the two readings this pass can see are:

* **authorize a bounded implementation pass** that adds the missing reviewed
  operator invocation — a provisioning entry point that renders the
  `ProvisioningRun` — returning it for independent review before it applies
  anything; or
* **rule that an existing route is the approved one**, in which case this pass
  did not find it and the ruling names it.

Claude takes neither. V6 remains performed-but-not-closed; I3 unconfirmed; V7
excluded; V8, V10 and I12 unperformed; `plan.is_executable` False; C-7,
EH-R16-1, LAB-R6, LAB-X1, P5.0-R5 and OD-62 Open; Package 5.0 **not ready**.
