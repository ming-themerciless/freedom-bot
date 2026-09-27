# Claude handback — I3 verifier not implemented; exact decisions required — 2026-09-19

> **Decisions supplied 2026-09-19.** Peter accepted C-P5.0-LAB-I3-D1 after
> independent review: P2 is `root:root 0555`, relies on the filesystem-UID
> owner condition rather than `CAP_FOWNER`, actual capability masks must be
> observed without equating `CapBnd` and `CapEff`, and the armed verifier may
> create and identity-guardedly remove temporary canonical `R`/`R/bin`. This
> handback remains the historical analysis; its requests for decisions are
> resolved, while implementation remains pending.

Authorization: **C-P5.0-LAB-I3-R1**. Implementing Technical Lead: Claude.
Independent Technical and Security Reviewer: Codex. Prompt:
[`phase-5-0-reserved-laboratory-i3-verifier-claude-prompt.md`](phase-5-0-reserved-laboratory-i3-verifier-claude-prompt.md).

## 1. Result

**Stopped before implementation, under the prompt's own stop clause.** The
prompt says: *"If the existing contract cannot support a safe, complete verifier
without a product, security, authority or topology decision, stop and return
the exact decision needed instead of choosing it."* The existing contract cannot
support one. The third I3 dependency, P2's `CAP_FOWNER` path, is defined three
different ways by reviewed sources, and one of those definitions contradicts the
manual page. The verifier cannot "reproduce P2's reviewed ownership and `0555`
mode conditions" until someone decides what those conditions are. It also
cannot make the link "require and observe the reviewed `CAP_FOWNER` condition"
under P2's reviewed identity without a capability decision. Separately, creating
`R` outside the concrete plan would override maintainer decision B.

A verifier covering only T1, T6 and §2.3.3 would split I3, and the prompt
forbids that. So no source, test, probe or artifact was added. The only changes
are this handback and one entry at the top of `docs/review/Handover information`.

**No host action was taken.** There was no SSH session, synchronization,
inspection, `sudo`, identity or capability change, write under `/run`,
`/var/lib` or `/opt/freedom-blades`, V7 initialization, participant, harness,
database access, generated vector or `--execute`.

## 2. Decisions required

### Decision 1 — P2's reviewed owner (security and authority)

Three reviewed sources give three answers:

| Source | P2's owner | Consequence under `fs.protected_hardlinks=1` for a root executor |
|---|---|---|
| r6 §1.4.4 (line 553) and §3 (line 909): *"installed `0555` root-owned"* | `root` | The executor's filesystem UID is 0 (§7.2 step 2: every effect step is `run_as="root"`). So **the owner condition holds** and `CAP_FOWNER` is never needed. |
| r6 §6.2 (lines 1898–1901) and §7.2(6) (lines 2381–2385): *"`fchown`s its temporary away from the executor's filesystem UID"* | some non-root owner that **no reviewed document names** | The owner condition fails. The contract says `CAP_FOWNER` is then required, but Decision 3 shows that claim is incorrect. |
| Code: `case_runtime.CASE_PROGRAM_OWNER`/`GROUP` = `root`/`root` (lines 182–183), carried by the concrete plan's P2 step (`concrete_plan.py` lines 2068–2069) into `executor.install_case_program`'s `fchown` | `root:root` | Same as the first row: the owner condition holds and `CAP_FOWNER` is not needed. |

The prompt asks for a "changed-owner" case, which matches the second row. No
reviewed document names the owner it changes to, so implementing it would
choose one. Implementing the first or third row instead would drop the
`CAP_FOWNER` dependency that §7.2(6) and §9.3's I3 row keep open. That would
redefine I3.

**Needed:** one ruling on P2's owner and group, with a matching correction to
whichever of r6 §§1.4.4/3, r6 §§6.2/7.2(6) and `case_runtime` is wrong.

### Decision 2 — P2's reviewed mode (reconciliation)

| Source | Mode |
|---|---|
| r6 §1.4.2 P2 (line 494): `openat(…, 0500)`, then `fchmod 0555`; §1.4.4 and §3: `0555` | `0555` |
| `executor.install_case_program` default (line 2428) | `0o555`, but the plan overrides it |
| `case_runtime.CASE_PROGRAM_MODE = "0755"` (line 181), passed by the concrete plan's P2 step (`concrete_plan.py` line 2067) and asserted by `P-04` | **`0755`** |

The production P2 path installs `0755`, and the contract says `0555`. The
difference matters here. Under `0755` the owner can write the file, so the
"readable and writable" branch of `proc_sys_fs(5)` holds for a root owner even
without capabilities. Under `0555` it does not.

**Needed:** which mode is reviewed, and the correction of the other source.

### Decision 3 — which kernel condition authorizes P2's link (security)

r6 §6.2 and §7.2(6) say that after P2's `fchown` and `fchmod 0555`, *"neither
the owner condition nor the readable-and-writable condition holds"*, so
`CAP_FOWNER` is required. The installed manual page contradicts this **[D]**
(`proc_sys_fs(5)`, man-pages as installed on this workstation; kernel
6.8.0-139). Its third condition is that *"the caller has permission to read and
write the target file (either via the file's permissions mask **or because it
has suitable capabilities**)"*. `capabilities(7)` defines `CAP_DAC_OVERRIDE` as
*"Bypass file read, write, and execute permission checks."*

P2's reviewed identity is a full root executor. `P-01` requires its bounding set
to contain both `CAP_FOWNER` and `CAP_DAC_OVERRIDE`
(`phase-5-0-evidence-harness-execution-plan.md` line 220). For that identity,
the readable-and-writable condition therefore **holds through
`CAP_DAC_OVERRIDE`**, whatever the owner and whatever the `0555` mode. The link
succeeds without `CAP_FOWNER`. No test or target run under P2's reviewed
identity can show that the link "requires `CAP_FOWNER` rather than accidentally
succeeding through ownership or write permission". With that identity, write
permission always succeeds.

Codex's 2026-09-16 disposition
([review](project-review-2026-09-16-reserved-laboratory-d12-r1-acceptance-and-v6-preflight.md),
line 58) says *"the design may not rely on `CAP_FOWNER`; its protected-hardlink
owner/read-write conditions must hold for the actual publication object and
execution identity."* That also conflicts with the prompt's requirement to
exercise the `CAP_FOWNER` path.

Every way of isolating `CAP_FOWNER` needs a decision this pass cannot make:

* **(a)** Redefine P2's I3 dependency as "P2's `linkat` succeeds for the reviewed
  root identity on the reviewed owner and mode", through whichever condition
  holds. The r6 §6.2/§7.2(6) text would be corrected, and the prompt's
  `CAP_FOWNER`-specific test requirement would be withdrawn.
* **(b)** Specify a reduced-capability identity for P2, for example without
  `CAP_DAC_OVERRIDE` and `CAP_DAC_READ_SEARCH` but with `CAP_FOWNER`, and amend
  the executor to run P2 under it. That identity is a new security design. It
  is not P2's reviewed identity, and verifying under it would require the
  capability manipulation this pass forbids.
* **(c)** Keep P2 root-owned, which is Decision 1's first or third row, so the
  owner condition holds. The r6 `CAP_FOWNER` dependency would then be recorded
  as withdrawn rather than verified.

**Needed:** a choice among these or another option, recorded in r6 by the
maintainer after Codex's security review. The prompt's test row *"P2's
changed-owner, mode-`0555` case requires and observes the reviewed `CAP_FOWNER`
condition"* then needs rewording to match that choice.

### Decision 4 — who may create `R` for the verifier (topology and authority)

The prompt asks the verifier to obtain or create `R` and `R/bin` without
entering the harness. r6 §1.3.3 states that `R = /var/lib/fb-evidence-p5-0` is
*"created exclusively by the reviewed concrete plan's `mkroot` and **not** by
prerequisite provisioning (§7.3, decision B)"*. In code, `mkroot` is the case
program's bootstrap verb, launched by the plan (`concrete_plan.py` lines
1931–1945). A verifier that creates `R`, even exclusively and with guarded
removal afterwards, would be a second creator of the sole canonical root.
Decision B does not allow one. The two alternatives each need a ruling too:

* Performing P2's sequence in a directory other than `R/bin` moves P2 out of its
  contracted location. The prompt calls that narrowing.
* Leaving `R` behind after verification would break C1's precondition that `R`
  does not exist (§1.4.1: `EEXIST` is the refusal).

**Needed:** an amendment to decision B that authorizes the I3 verifier as a
second, temporary creator of `R` and `R/bin`. It should state `R`'s and
`R/bin`'s owner and mode for the verifier. r6 P1 uses `0700` through
`create_run_directories`, but the r16-3 ownership table states `R/bin` as
`0755 root:root`. It should also require identity-guarded removal of both
directories before the verifier reports success.

## 3. What is designable once the four decisions exist

These items need no maintainer decision. I propose them here for review and
have **not** adopted them. They are listed so the follow-up pass is bounded.

| Item | Proposal |
|---|---|
| Entry point | `tools/phase_5_0_evidence/execution/i3_verifier_cli.py`. It is non-effecting by default. An I3-specific arm, `--arm-i3-controlled-write`, is required, together with a second, independent in-code gate, so that removing one guard does not produce an effect. Unarmed, it opens nothing and reads no account database. |
| Checks and identities | T1 in V4 as root; §2.3.3 in a verifier-owned `<run-id>` directory under V5 as root; T6 in V9 as `ubuntu`; P2 in `R/bin` as decided by Decisions 1–4. Root checks and the `ubuntu` check run as two invocations. The verifier never changes identity itself. |
| Names | `.i3-verify-<nonce>.tmp` and `.i3-verify-<nonce>`, a leading dot plus a fixed prefix that no lifecycle, ledger, recovery or case-program grammar admits. The nonce comes from `os.urandom`, and the names are checked against those grammars before use. |
| Bytes | One fixed ASCII constant with its SHA-256 stated in code and asserted by a test. |
| Sequence | Reuses `DescriptorInventory` for the directory descriptors, bound synchronizable descriptor and barrier, and `PosixFilesystem.create_file`/`write`/`fsync`/`fstatat`. It does **not** reuse `PosixFilesystem.renameat(noreplace=True)`, because that call unlinks the temporary immediately and the two-names-present state is never observable. A separate `linkat` step without the paired unlink is a documented duplicate of a security-sensitive primitive. Codex should review it as such. |
| Observations | Both names are compared by `fstatat` for `(st_dev, st_ino)`, link count 2, and bytes plus digest read back through `O_RDONLY\|O_NOFOLLOW` before any removal. |
| Removal | An immediately preceding `(st_dev, st_ino)` comparison for each name, following `remove_publication_temporary`'s guard, then `unlinkat` of each name, then the containing-entry barrier. A mismatch or a foreign object is never removed. |
| Accounting and output | A closed state vocabulary for each boundary, a final bounded residue survey through D20, closed-vocabulary output with no path or OS message, and distinct nonzero exit codes. |

## 4. What this pass read

I read these in full: `.agents/AGENTS.md`; the implementation plan's reading
map, §§0, 13, 14, 16, 17, the Phase 5 package table in §12 and the current §20
pointer; the active `Handover information` entries back to C-P5.0-LAB-V6-P-R4;
the I3 operator prompt pointer and the I3 blocker handback; r6's preamble, §§0,
1.3–1.4.2, 5.10–5.11, 6, 7–7.3, 9.1, the rows 19–89 index of 9.2, 9.3 and 10;
`execution/descriptors.py`; and `DescriptorBoundEffects` and P2's call site in
`execution/executor.py`.

I also read the P2 constants in `case_runtime.py`, the P2 and `mkroot` steps in
`concrete_plan.py`, and every `CAP_FOWNER`/`CAP_DAC_OVERRIDE` reference in the
repository, including Codex's 2026-09-16 disposition.

**Reading gaps, disclosed:** I did not read the disposable-server runbook, the
V6/I12 operational handback and closure review, the status/RAID/decision/change
registers, `lifecycle_storage.py`'s publication path or `recovery_store.py`
line by line. The stop depends on r6, `case_runtime`, `concrete_plan`, the
execution plan's `P-01` and the installed manual pages. None of the unread
documents can reconcile three contradictory statements of one reviewed value
or change the manual page. The reviewer can weigh that.

## 5. Checks run and not run

* **Run:** none of the suites. There is no code change to verify.
* **Not run:** narrow tests, the `tests/phase_5_0_evidence` suite, the guard
  tests, `compileall` and `git diff --check` over code. The only changes are
  documentation. No review artifact was regenerated and no digest was computed
  for execution. The SHA-256 values in §6 are **review input only**.

## 6. Source identity

This section is review input only. It is not execution authority. `HEAD`
`2fb1d6fd88013752d53af76fc97b4db07fc31181` on `docs/platform-plan`. There were
54 uncommitted or untracked paths before this pass, and they are left as they
were. Working-tree SHA-256 at 2026-09-19T19:25:59Z:

| File | SHA-256 |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | `70f3f259736e92bf2a5915cc5d77b0c383eac1c9e35709e7be8c9ee3a907caf3` |
| `docs/review/phase-5-0-reserved-laboratory-i3-verifier-claude-prompt.md` | `3626c65f2f310c5cca48564d59191a2b39bd29221015a2f40f908dc7fc2cf160` |
| `tools/phase_5_0_evidence/case_runtime.py` | `15261b6cd98bdbf53ecd7f467d82230068c0193be49d524ea86581715bf9f66f` |
| `tools/phase_5_0_evidence/concrete_plan.py` | `d24ba5ca94b5a910197e23a87fbc69a9c090509d733c5d9a371abee282e5c483` |
| `tools/phase_5_0_evidence/execution/executor.py` | `a5b17330fb6bfe5c1903f8feb0aaf41203d68b1b2d781099ca646ecb97af48f5` |
| `tools/phase_5_0_evidence/execution/descriptors.py` | `625c29b46396056724cfee8687af5b2a21d643635d569f5d9a64883b185f1c00` |
| `tools/phase_5_0_evidence/plan.py` | `0c76f7d8206fb4b0114ea53587fe9a0c0c348932143c8aee3ec4766315a60fbb` |

## 7. Unchanged state and rollback

I3 is unconfirmed. V7 remains excluded, and V8 and V10 unperformed.
`plan.is_executable=False`. `reservation.REAL_EXECUTION_REFUSAL` remains
unconditional. LAB-SECRETS-1 is Open, Low. LAB-V6-P2 remains deferred. Package
5.0 is **not ready**. Claude closes no finding, confirms no I3 fact, approves no
digest and advances no gate.

**Proposed, not recorded:** a RAID item, LAB-I3-2 (Issue, owned by the
Technical Lead and the Security Reviewer), for the P2 owner/mode/capability
contradiction in Decisions 1–3.

**Rollback:** delete this file and the top entry of
`docs/review/Handover information`. Nothing else changed.

## 8. Reviewer focus

1. Is Decision 3's reading of `proc_sys_fs(5)` right, that a root process
   holding `CAP_DAC_OVERRIDE` satisfies the readable-and-writable condition on a
   `0555` file it does not own? If it is, r6 §6.2 and §7.2(6) contain an
   incorrect **[D]**-grounded claim, whatever else is decided.
2. Whether `0755` in `case_runtime` or `0555` in r6 is the reviewed P2 mode, and
   whether the difference is itself a finding against the implementation.
3. Whether Decision 4 is a real conflict with decision B, or whether decision B
   was meant only to exclude prerequisite provisioning from creating `R`.
4. Whether §3's proposal to add a separate `linkat` step, instead of reusing
   `renameat(noreplace=True)`, is an acceptable documented duplicate of the
   primitive.
