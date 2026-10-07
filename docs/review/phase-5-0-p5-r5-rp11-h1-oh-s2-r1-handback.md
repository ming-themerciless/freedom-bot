# Handback — OH-S2 R1 version-bound citation work: `OH-S2 CITATIONS READY FOR REVIEW`

Work ID: `C-P5.0-R5-RP11-H1-OH-S2-R1-20261006-07`

Date: 2026-10-06

Executor: Claude Code on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s2-r1-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s2-r1-claude-prompt.md),
9254 bytes, SHA-256
`97ba6c23aa19ee83cb5389eb2860d51806f3fad243afe9aacf76c8e3c7aca92f`
(recomputed before research or editing; equal to the authority's pin).
· Authority: [`project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r1-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r1-authority.md).
· Citation record: [`phase-5-0-p5-r5-rp11-h1-oh-s2-r1-citations.md`](phase-5-0-p5-r5-rp11-h1-oh-s2-r1-citations.md).

## 1. Terminal state

**`OH-S2 CITATIONS READY FOR REVIEW`.** PO-14 was evaluated first and is
established, so the remaining obligations were completed. Nothing is accepted
or authorized by this return. The record awaits independent Codex review and
Peter Duscha's decision. I have not accepted my own conclusions or proposed a
successor authority.

## 2. Requirements addressed and verdicts

| Requirement | Verdict | Record |
|---|---|---|
| PO-14 (first, load-bearing), with TR-7/LB-2S provenance | **established** | §3 |
| AD-7 | **established** | §3.4 |
| PO-15 (property lists; loaded-configuration reporting; `ExecStartPre` form) | **refuted** — limb (d), `NeedDaemonReload`; lists, `FragmentPath`, `DropInPaths`, `Exec*` form established | §4, Appendices A–C |
| PO-8, S-1 … S-10 | **established** (with precisions) | §5 |
| PO-11 (b) … (g) | **not established** — (b), (g) need `/etc/polkit-1/rules.d` (MF-3); (d), (f)(iii) no citable bound; (f)(ii) outside authorized sources | §6 |
| PO-20 (a) … (h), including (g), (h) | **refuted** — limb (f); (a), (d) await MF-5 | §7 |
| PO-21 (a) … (v), including D3-R4 and D3-R5 additions | **refuted** — limbs (c), (s) | §8 |
| CL-21i | **established, non-empty**; one disarm condition: `/run/nextroot` absent | §9 |
| PO-12, AS-8 (CPython 3.14.4, `-I -S`) | **refuted** — `PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__` honoured under `-I`; PO-12′ offered | §10 |
| PT-8 | **refuted** (no `os.renameat2`, no `os.RENAME_NOREPLACE`); `ctypes` retained | §10.5 |
| U-9 / PO-19 | **not established** — (b), (c) established; (a) binding and (d) need MF-1, MF-2 | §11 |
| D9-1 (AD-3, AD-4, AD-6, AD-8, AD-11, AD-12, unmounted case, grammar) | **refuted** — AD-8 as worded (established for the closed launcher inventory); unmounted case not established | §12 |
| PO-17 / OH-S4p boundary | premises established; **no image evaluated** | §12.9 |

## 3. Dispositions (reported, not decided)

1. **Activation design returns to design review**: PO-20 (f), PO-21 (c) and
   PO-21 (s) are refuted, and PO-11 (d) has no citable bound (the accepted
   design returns `ACT`/`DEACT` to review in that case).
2. **Route 1 returns to Route 3 design review**: PO-12 is refuted. A narrower,
   source-established PO-12′ is offered for the reviewer (record §10.4); it is
   not a substitute verdict.
3. PO-15 (d) and AD-8 are refuted as worded and returned for restatement.
4. PO-19 is not established; it does not itself trigger Route 3.
5. Fourteen contradictions with accepted texts are proposed for correction
   (record §15.3). No accepted or historical record was edited.

## 4. Files changed

Created:

- `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-citations.md` — the citation
  record.
- `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-handback.md` — this handback.

Updated (current-state pointers only; additive; pre-existing uncommitted
changes in each file preserved):

- `docs/review/Handover information` — heading set to "OH-S2 R1 returned for
  review"; one return paragraph; authority and prompt links relabelled
  *Consumed*; links to the record and handback added.
- `docs/project-management/status.md` — same, in its current-status section.
- `docs/implementation-plan.md` — §20 only: same.
- `docs/operations/disposable-test-server.md` — restriction banner only: OH-S2
  consumed, returned without host access, MF facts need separate authority;
  authority link relabelled *consumed*.

No implementation, test, configuration, migration, infrastructure, skill or
hook file was touched. No other repository file was changed by this run. The
working tree's many pre-existing modifications and untracked files (from
earlier slices; `git status` at start) were left as they were.

## 5. Sources consulted

All primary; full table with URLs, versions and SHA-256 in record §2.1 and
Appendix D. In brief:

- Ubuntu source packages from Launchpad: `systemd` `259.5-0ubuntu3.4`,
  `policykit-1` `127-2ubuntu1.1`, `glibc` `2.43-2ubuntu2.4`, `python3.14`
  `3.14.4-1ubuntu0.2`, `linux` `7.0.0-31.31`; and, to identify three host rule
  files by digest only, `bolt` `0.9.10-1`, `fwupd` `2.1.1-1ubuntu3.1`,
  `packagekit` `1.3.4-3ubuntu1.2`.
- Upstream reconciliation (byte-equality with each `orig`): systemd tag
  `v259.5` (GitHub), polkit tag `127` (GitHub), Python `3.14.4` (python.org),
  glibc `2.43` (GNU mirror `mirrors.kernel.org`), Linux `7.0`
  (`cdn.kernel.org` `sha256sums.asc`).
- Launchpad source pages and the Launchpad API `getPublishedSources` (metadata
  only).
- Accepted repository records: AGENTS.md; implementation plan reading map, §0,
  §14, §16, §17, §20; Handover; test-server banner; the one-host design
  (§§4.1.3, 4.2.5-R2 … R6 as needed, 4.3, 4.4, 4.7.4); C11 (§§2.3, 4.4.3, 14);
  D2 (§§2, 4.5, 5.4); cumulative R3 (§§6–7, 10, 13–14) and its acceptance; the
  composed H-0 review; the H-0 and U-9 acceptance; R5 and H-0G handbacks (as
  durable evidence only).

## 6. Commands and checks, with exact results

| Check | Command (summary) | Result |
|---|---|---|
| Prompt identity | `wc -c`, `sha256sum` on the prompt | `9254`; `97ba6c23…7aca92f` — **equal** to the authority |
| Starting state | `git status --short` | 11 modified, 49 untracked pre-existing paths (none created by this run at that time); preserved |
| Ubuntu `.dsc` integrity | `sha256sum` of each downloaded file vs the `.dsc` `Checksums-Sha256` | all **equal** (8 source packages) |
| Upstream equality | `sha256sum` of upstream release artifacts vs `orig` | systemd, polkit, CPython, glibc **equal**; Linux `orig` equals `linux-7.0.tar.gz` in kernel.org `sha256sums.asc` |
| Ubuntu patch application | GNU `patch -p1` over each `debian/patches/series` | systemd 40/40, polkit 2/2, CPython 45/45, glibc 103/103 **applied**; kernel delta hunks applied to every cited file |
| vtable extraction completeness | per-vtable raw macro count vs extracted entries | all 8 vtables **equal** (102, 71, 26, 69, 198, 3, 7, 111) |
| Patched vs upstream vtables | `diff` of names and flags | **identical** |
| Host cross-check | visible `Default*` names vs R5 c144 | 52 = 52, **identical** |
| polkit rule identification | `sha256sum` of source rule files (rendered where the build substitutes) vs R5 c108–c116 | all 9 host entries **identified** |
| Repository-relative link check | own script over the six changed or created files | 146 links checked, **0 broken** |
| Whitespace | `git diff --check` (tracked files); `grep -nP '[ \t]+$'` on the two new files | exit 0, no output; no trailing whitespace |

Download, extraction and patching took place only in the fresh directory
`/tmp/ohs2-r1-20261006` (created at 16:57Z; mode 0700). No downloaded code was
executed. My three helper scripts (vtable extraction, classification, table
rendering) and their intermediate TSV files are in the session scratchpad,
outside the repository.

### 6.1 Final checks

Run after every deliverable and pointer edit was written; results are in the table above and in §13.

## 7. Checks not run, and why

- No host connection, SSH, `oracle-test` access, retained-evidence access or
  host inspection: forbidden by the authority. Every host fact used comes from
  the accepted durable records. Missing host facts are listed as MF-1 … MF-8
  (record §14.3), not inferred.
- No application test suite, build, package operation or upstream build/test
  system: forbidden, and this is a documentation slice. `run-suites` therefore
  does not apply.
- No PGP verification of `.dsc` files or `sha256sums.asc`: no keyring
  operation was performed. Integrity rests on `.dsc` checksums and on equality
  with independently retrieved upstream release artifacts.
- GLib (`GFileMonitor` behaviour) and the x86-64 psABI document were not
  consulted: neither is among the authorized sources. The record says where
  that leaves a limb not established.
- `python3 .claude/hooks/test_guards.py`: not run; no guard was changed.

## 8. Disclosure

While locating Debian glibc's `slibdir` setting, one command ran
`grep -rln 'slibdir' .` and `grep -rn 'slibdir' --include=*.mk .` with the
**repository root** as the working directory, because I omitted the intended
`cd` into the temporary source tree. It printed only the repository's
top-level directory listing (from a preceding `ls`) and **no matches**. No file
contents were printed. The recursive search did read files in the working tree
to test for the literal `slibdir`, which can include secret-bearing files such
as `yt-cookies.txt` named in the listing; nothing from them was displayed or
retained. I then re-ran the search in the correct directory. I report this for
the reviewer; I do not believe it exposed any secret, and no maintainer action
seems required beyond noting it.

## 9. Security implications

- **LB-2S stands for this systemd version** (PO-14 established). The executor's
  input is PID 1's own environment, which also includes root-owned
  `ManagerEnvironment=` and can select the executor image via
  `SYSTEMD_EXECUTOR_PATH` (PR-14a, PR-14b). Both are root/boot state.
- **X-1 (record §15.4):** CP, the holder, its `ExecStopPost=` and the backstop
  are root `python3.14 -I -S` processes that start under the open manager
  block, not a literal environment. Their loader honours `LD_*`/tunables from
  that block, and CPython honours `PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__`
  and `MIMALLOC_*` despite `-I`. Those sources are root-controlled or need
  polkit `set-environment` authorization, but they are the same ambient state
  C11 treats as untrusted for the entry. This is a design question, raised for
  review.
- **PO-12 refutation:** under `-I`, a `PYTHONEXECUTABLE` value can select a
  `._pth` file that replaces `sys.path`. The entry's literal environment
  excludes it; other interpreter invocations do not.
- **Grant boundary:** PO-11 (d) has no citable reload bound, so PK's
  "not authorized within the bound" check has no cited bound to use.
- **Lock semantics:** `flock` survives in any process holding a duplicate of
  the open file description (PO-20 (f)).
- **Soft-reboot:** automatic conversion exists in 259.5 and is disarmed only
  by `/run/nextroot` being absent (CL-21i).
- **Kernel:** Ubuntu enables Live Update; unlinked shmem files (not named
  `/run` entries) can be carried across `kexec` by root.

No secret, credential or player data was read, printed or recorded (subject
to the disclosure in §8).

## 10. Configuration, deployment, migration, rollback

None. No migration was added and nothing was deployed. Rollback: delete the
two new files and revert the additive pointer edits in the four current-state
files; no other state exists. The temporary directory was deleted (§13).

## 11. Unresolved questions for Peter and the reviewer

1. Accept the dispositions in §3, and decide whether PO-12′ (record §10.4) is
   an acceptable basis for re-opening Route 1 or whether Route 3 review
   proceeds.
2. Decide how the activation design restates PO-20 (f), PO-21 (c) and PO-21
   (s), and how it treats PO-11 (d)'s missing bound (for example, a design that
   does not depend on a reload bound).
3. Decide X-1: whether root Python processes started by PID 1 may run under
   the open manager block, or must start from a literal environment.
4. Authorize, if wanted, a read-only slice to observe MF-1 … MF-6 (MF-3 needs
   privilege), and decide where MF-1's closure is fixed (after OH-S4's import
   trace).
5. Decide C-1 … C-14 (record §15.3), in particular the PO-17 type-E rule (full
   path, not basename) and the `UnsetEnvironment` classification.

## 12. Proposed reviewer focus

1. PO-14 premises P14-1 … P14-6 and the PR-14a/PR-14b refinements: is
   establishment sound and correctly bounded?
2. Whether each **refuted** verdict is a genuine refutation of the accepted
   wording (PO-15 (d), PO-20 (f), PO-21 (c), PO-21 (s), PO-12/AS-8, AD-8) rather
   than a precision; and whether any **established** verdict hides a needed
   qualification.
3. CL-21i completeness: the logind and systemctl conversion paths, and the
   items placed outside CL-21i by definition.
4. PO-12's `getpath.py` analysis (`PYTHONEXECUTABLE`, `._pth`, `pyvenv.cfg`)
   and the PO-12′ restatement.
5. The derived build-configuration facts (polkit directories, glibc trusted
   directories and `gconvdir`).
6. Appendix A/B accuracy; spot-check a sample against the vtables.
7. The §8 disclosure.

## 13. Final checks and temporary-directory disposition

- Link check: 146 repository-relative links in the six touched files, 0 broken.
- `git diff --check`: exit 0, no output. The two new (untracked) files have no trailing whitespace.
- Temporary directory `/tmp/ohs2-r1-20261006` (1.5 GB of downloaded source archives, extracted and patched trees) was **deleted** at 2026-10-06T17:55Z with `rm -rf` on the literal path; a following `ls -ld` reported `No such file or directory`. No downloaded archive or source tree is in the repository.
- The session scratchpad keeps only my own helper scripts and derived TSV/Markdown files; it is outside the repository.
