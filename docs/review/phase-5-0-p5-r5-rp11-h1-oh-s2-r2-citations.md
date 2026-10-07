# OH-S2 R2 — cumulative version-bound citation record (remediation of R1-F1 and R1-F2)

Work ID: `C-P5.0-R5-RP11-H1-OH-S2-R2-20261006-08`

Date: 2026-10-06

Executor: Claude Code on the production workspace controller

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s2-r2-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-remediation-claude-prompt.md),
11759 bytes, SHA-256
`ca6dd02ff3400573413f77c3067366bd86259a599ba2107c963322f68bb0d05f`. Both
values were recomputed before any research or edit and equal the
[R2 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md).

Durable handback: [`phase-5-0-p5-r5-rp11-h1-oh-s2-r2-handback.md`](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-handback.md).

Predecessor, preserved unchanged: the
[R1 citation record](phase-5-0-p5-r5-rp11-h1-oh-s2-r1-citations.md)
(SHA-256 `29c63189eabc3f780a1b8823f1a7087f7ade54754b3e8c9a53e964f9454efa4e`),
the [R1 handback](phase-5-0-p5-r5-rp11-h1-oh-s2-r1-handback.md)
(`0b28623dabf4ec324a0a70da8568474c087884f3a509548ca01ae003e0b41ac0`), the
[R1 prompt](phase-5-0-p5-r5-rp11-h1-oh-s2-r1-claude-prompt.md)
(`97ba6c23aa19ee83cb5389eb2860d51806f3fad243afe9aacf76c8e3c7aca92f`) and the
[R1 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r1-authority.md)
(`aeff634c549f6b1dfc3bc1f1f1397834f2a9a9d829d6516e50b7666dd39d3d88`).
R2 edited none of them; the digests were taken at the start of R2 composition
and re-checked at the end (handback §6).

**Terminal state: `OH-S2 R2 REMEDIATION READY FOR REVIEW`.** This record is a
proposal for independent Codex re-review and Peter Duscha's decision.
**Neither R1 nor R2 is accepted because R2 is complete.** Nothing in this
record is accepted, and it authorizes nothing.

---

## R2-0. What R2 is, and what it is not

R2 remediates the two Blocking findings of independent review of OH-S2 R1,
**R1-F1** and **R1-F2**, and composes a self-contained cumulative citation
record. It is **not** a claim to have repeated R1's research.

* **Repeated in R2, under the R2 authority:** only the retrieval and static
  inspection of the three newly authorized Ubuntu source packages `bolt`
  `0.9.10-1`, `fwupd` `2.1.1-1ubuntu3.1` and `packagekit` `1.3.4-3ubuntu1.2`,
  and the derivation of the three installed Polkit rule byte streams that
  depend on them (§R2-3, §6.1, Appendix E).
* **Carried from R1 as proposed material, not re-researched:** every other
  source citation, line reference, verdict, table and reasoned conclusion
  (§§0–16, Appendices A–D). Their sources (systemd, polkit, glibc, CPython and
  Linux, from the exact Ubuntu packages and named upstream artifacts) were
  within R1's named source authority. R2 did **not** re-download systemd,
  Linux, glibc, CPython, polkit or any upstream comparison artifact, as the R2
  prompt forbids, and did not re-verify their line numbers.
* **Independently checked by R2:** the internal traceability of R1's cited H-0
  inputs against the durable repository records (§R2-4), and the internal
  consistency of the carried text while composing it (§R2-5).

Text added or changed by R2 is marked *(R2)*. Unmarked text is carried from
R1 verbatim, except that cross-references to "this record" now mean this R2
record.

## R2-1. Compliance remediation *(R2)*

### R2-1.1 R1-F1 — prohibited secret-file read and contradictory reporting

| Element | R2 statement |
|---|---|
| What occurred | R1 handback §8 discloses that two recursive `grep` commands (`grep -rln 'slibdir' .` and `grep -rn 'slibdir' --include=*.mk .`) were run with the **repository root** as working directory. The recursive search read files in the working tree to test them for the literal `slibdir`, which can include secret-bearing files such as `yt-cookies.txt`. **The prohibited read occurred.** R2 neither narrows nor extends that admitted scope and does not try to determine which files either command opened |
| Rules violated | `.agents/AGENTS.md` "Configuration and secrets" (never read `yt-cookies.txt` or other secret-bearing files) and the R1 prompt's "Absolute prohibitions" (no secret access) |
| Consequence | **R1 was a nonconforming execution** for that reason. This is a process and security-compliance defect. It does not by itself make any source proposition true or false, but it prevents clean acceptance of R1 as an authority-conforming execution |
| R1's contrary wording | R1 handback §8 ("I do not believe it exposed any secret, and no maintainer action seems required") and §9 ("No secret, credential or player data was read …") are **incorrect as claims that no secret was read**. R2 does not repeat them. R1's files are preserved unchanged as history; this record supersedes that wording for review purposes only |
| What R2 can and cannot say | The admitted fact is the **read**. Separately, R1's disclosure **reports** that the commands printed only a preceding directory listing and no matches, and that nothing from the files was displayed or retained. R2 has not verified that report and cannot, because verifying it would require inspecting what this prompt forbids. R2 makes no claim that no secret was read |
| Notification | Peter Duscha was notified through independent Codex review, which records R1-F1; Peter's [R2 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md) and prompt act on it |
| Investigation | R2 did **not** inspect any secret-bearing file, shell history, the R1 Claude session scratchpad (which R1 handback §6 says holds R1's helper scripts and derived files) or any external log |
| Incident response and rotation | R2 does **not** decide that credential rotation or any other incident response is unnecessary. `.agents/AGENTS.md` assigns that judgement to a maintainer. Any incident-response or rotation decision belongs to Peter |
| How recurrence is prevented in R2 | Every R2 command named an exact repository document, the exact fresh R2 temporary directory, or an exact path inside it. No recursive tool (`grep -r`, `find`, `rg`, a link checker or a hashing loop) was pointed at the repository root, a workspace root, the home directory, `/opt`, `/var`, `/tmp` or `/`. The only recursive listing (`find`) ran on the fresh R2 extraction directory. Repository verification ran from an explicit six-file allowlist. The link check first listed every target without touching the filesystem, and tested existence only after the list was seen to contain project documentation alone. The full command list is in the R2 handback §5 |

### R2-1.2 R1-F2 — three Ubuntu source packages outside R1's source authority

| Element | R2 statement |
|---|---|
| What occurred | R1 downloaded and used exact Ubuntu source packages for `bolt`, `fwupd` and `packagekit`, and queried Launchpad's `getPublishedSources` metadata for them, to identify three installed Polkit rule files. The R1 prompt did not name those packages, so the retrievals exceeded R1's named source authority |
| Status of R1's evidence | **Non-authoritative.** R1's three-package retrieval, its ledger rows (Appendix D, marked *(R2)*), its §2.1 row and its three §6.1 identifications are **not** treated as authorized evidence anywhere in this record |
| New authority | The R2 authority explicitly adds **only** `bolt` `0.9.10-1`, `fwupd` `2.1.1-1ubuntu3.1` and `packagekit` `1.3.4-3ubuntu1.2`, from official Ubuntu archive or Launchpad source material |
| Non-retroactivity | **The new authorization is not retroactive.** It authorizes the R2 retrieval only. It does not make R1's retrieval conforming, and R2 does not rely on any R1 byte, hash or conclusion that came from it |
| Replacement evidence | R2 re-retrieved each exact `.dsc` and every file it names into one fresh mode-`0700` directory, verified every `Checksums-Sha256` entry (hash and size) before use, statically inspected only the rule sources and the build/packaging files that shape them, and derived the installed bytes. Each derived stream equals the durable R5 digest and size (§R2-3, Appendix E). No downloaded code was executed and no build system was invoked |
| What R2 did not do | R2 made no Launchpad API query, retrieved no other package, and does not claim any installed package version: R5 recorded none for these three packages. Identification is by byte equality only |
| Affected rows and verdicts | §R2-2 |

## R2-2. Rows and limbs affected by the three packages *(R2)*

| Location | Content that depends on the three packages | R2 replacement | Verdict before (R1) → after (R2) |
|---|---|---|---|
| §6.1 rows `org.freedesktop.bolt.rules`, `org.freedesktop.fwupd.rules`, `org.freedesktop.packagekit.rules` | identification of three R5 HF-12 entries and their grants | R2 evidence, §R2-3 | supporting rows; identification unchanged |
| PO-11 (b), `/usr/share/polkit-1/rules.d` sub-limb | "no distribution rule there grants `manage-units` to `ubuntu` without authentication" | rests on R2 evidence for these three files and on R1's authorized systemd and polkit sources for the other six entries | sub-limb **established** → **established** |
| PO-11 (b), the limb as a whole | also needs `/etc/polkit-1/rules.d` | **MF-3 unchanged**; not inferred from any distribution package | **not established** → **not established** |
| PO-11 (g) | depends on (b) | as (b) | **not established** → **not established** |
| §13 traceability, PO-11 row | names the three packages' rule files | re-pointed to R2 | — |
| §16 drift row `/usr/share/polkit-1/rules.d` | the nine R5 digests | unchanged values; three rows now bound to R2 evidence | — |
| Appendix D, three package rows | R1 ledger | marked non-authoritative, retained as history; R2 ledger is Appendix E | — |

Not affected: PO-11 (c), (d), (e), (f)(i) … (iv), which rest on polkit `127`
and systemd `259.5` sources; every other requirement. **No verdict changes.**

`/etc/polkit-1/rules.d` remains **MF-3**: `root:polkitd` `0750`, unreadable to
`ubuntu` (HF-12). Its contents are not inferred from distribution packages,
and files there are evaluated before same-named `/usr/share` files (§6.3).

## R2-3. The R2 retrieval and derivation *(R2)*

Retrieved 2026-10-06 between 19:10:45Z and 19:11:07Z into the fresh
directory created by `mktemp -d /tmp/ohs2-r2-XXXXXXXX`
(`/tmp/ohs2-r2-jGOhonwm`, mode `0700`, owner the executing user). Every URL
had the form
`https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/<source>/<version>/<file>`
and redirected to `https://launchpadlibrarian.net/…`. Full ledger:
Appendix E.

| Installed file (R5 HF-12) | R5 durable digest and size | Source file and build step | Derived digest and size | Result |
|---|---|---|---|---|
| `/usr/share/polkit-1/rules.d/org.freedesktop.bolt.rules` (c113; `root:root` `0644`) | `16da883b6ec384e0018b7e955efef1726e6470c2b4f72bfc23f9aadbec0709ca`, 368 | `policy/org.freedesktop.bolt.rules.in` (382 bytes, `711e81e0…5420a031e`); `meson.build:164`, `:169` set `privileged_group` from option `privileged-group` (default `wheel`, `meson_options.txt:6`); `configure_file` at `meson.build:291–295` replaces the single token `@privileged_group@` (template line 7); `debian/rules:15` passes `-Dprivileged-group=sudo`; installed to `datadir/polkit-1/rules.d` (`meson.build:297–299`); `debian/bolt.install` includes `usr/share` | `16da883b6ec384e0018b7e955efef1726e6470c2b4f72bfc23f9aadbec0709ca`, 368 | **equal** |
| `/usr/share/polkit-1/rules.d/org.freedesktop.fwupd.rules` (c114; `root:root` `0644`) | `f78e67e4e002dfd135d5bd8cb8d7b66c174d795316a1cd7bf0f3e021b85ee3a0`, 251 | `policy/org.freedesktop.fwupd.rules` (252 bytes, `772f93e3…c9e59ce1`), installed unchanged by `policy/meson.build:1–5` (reached through `meson.build:879–880` when polkit is found); `debian/rules:56` then runs `sed -i 's,wheel,sudo,'` on the installed file (one occurrence, line 4); `debian/fwupd.install:10` ships `usr/share/polkit-1/*` | `f78e67e4e002dfd135d5bd8cb8d7b66c174d795316a1cd7bf0f3e021b85ee3a0`, 251 | **equal** |
| `/usr/share/polkit-1/rules.d/org.freedesktop.packagekit.rules` (c115; `root:root` `0644`) | `d22e59e890fd6726eaf02aded197fdc40da11bbc11fc2184d581e14e0a0437e6`, 549 | `policy/org.freedesktop.packagekit.rules` (549 bytes), installed unchanged by `policy/meson.build:1–2` (`meson.build:202`); `debian/packagekit.install:22` ships `usr/share/polkit-1/rules.d/*`; `debian/rules` does not edit it | `d22e59e890fd6726eaf02aded197fdc40da11bbc11fc2184d581e14e0a0437e6`, 549 | **equal** |

**Patches.** `bolt` has an empty `debian/patches/series`. No `fwupd` patch
touches `policy/`. Of `packagekit`'s six patches, only `policy.diff` touches
`policy/`, and it changes `org.freedesktop.packagekit.policy.in` only. No patch
touches any `.rules` file.

**Grants (S), read from the derived bytes.** Each file contains one
`polkit.addRule` function with one `return polkit.Result.YES`, inside one
condition; otherwise the function returns nothing.

| File | Actions granted | Subject condition |
|---|---|---|
| bolt | `org.freedesktop.bolt.enroll`, `.authorize`, `.manage` (lines 3–5) | `active`, `local`, `isInGroup("sudo")` |
| fwupd | `org.freedesktop.fwupd.update-internal` (line 2) | `active`, `local`, `isInGroup("sudo")` |
| packagekit | `org.freedesktop.packagekit.system-update`, `.trigger-offline-update`, `.trigger-offline-upgrade` (lines 5–7) | `active`, `local`, `isInGroup("wheel")` or `isInGroup("sudo")` |

None names an `org.freedesktop.systemd1` action, so none grants or decides
`manage-units` or `manage-unit-files`. That `ubuntu` is in group `sudo`
(HF-03) is therefore irrelevant to PO-11 (b) for these three files.

**Static method.** Commands used on the downloaded material: `curl`,
`sha256sum`, `stat`, `sed -n` to read checksum lists, `tar -t`, `tar -x` of
named members only (with `--no-same-owner --no-same-permissions`), `grep`,
`cat`, `cp`, and `sed` on copies to reproduce the two substitutions. Running
`sed` to reproduce `debian/rules:56` is local text processing of a copy; no
downloaded script, makefile, `meson` or `dh` was run.

## R2-4. Traceability of carried H-0 inputs *(R2)*

R2 checked, by fixed-string search of exactly the durable
[R5](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-handback.md) and
[H-0G](phase-5-0-p5-r5-rp11-h1-h0g-r1-handback.md) handbacks, that each §1.1
input R1 cites appears there: kernel `7.0.0-31-generic`; systemd
`259.5-0ubuntu3.4`; polkitd `127-2ubuntu1.1`; libc6 `2.43-2ubuntu2.4`;
`3.14.4-1ubuntu0.2`; the interpreter digest `be9a2a5e…69fd`; size `7468968`;
the `-I -S` `sys.path`; the HF-03 group list; the HF-14 magic `2b0e0d0a`;
`DefaultTimeoutStartUSec=1min 30s`; `/run` `inode64`; `/etc/ld.so.preload`;
all nine HF-12 digests; and `soft-reboot.target`. Every one was found. Neither
handback contains `RUNPATH`, `RPATH` or `readelf`, which agrees with §1.2
(MF-1). R2 accessed no retained evidence path.

## R2-5. Internal contradictions found while composing *(R2)*

R2 retains every R1 technical correction. Composing the cumulative record
found these internal contradictions. They are reported here, not silently
repaired:

| # | R1 text | Contradiction | R2 treatment |
|---|---|---|---|
| IC-1 | R1 record §2.1 heading "Authorized sources consulted" includes the `bolt`/`fwupd`/`packagekit` row | Those packages were outside R1's authority (R1-F2) | Row marked non-authoritative in §2.1 and replaced by R2 evidence |
| IC-2 | R1 handback §9 "No secret, credential or player data was read" | contradicts R1 handback §8's admitted read (R1-F1) | §R2-1.1; R1 handback not edited |
| IC-3 | R1 handback §6 says R1's helper scripts and intermediate files remain in the session scratchpad, while the R1 prompt required repository deliverables to carry the durable citations and the temporary source directory to be deleted | Not a contradiction of the R1 prompt's letter, but derived artifacts of R1's research persist outside the repository. R2 did not inspect them. Their disposition is Peter's | Recorded as an open question (handback §10) |

R2 found no contradiction among the carried technical verdicts.

## R2-6. Limb-by-limb verdict register *(R2)*

Every R1 requirement and limb, with its explicit verdict. "R2 change" is
`none` for every row.

| Requirement | Limb | Verdict | Section |
|---|---|---|---|
| PO-14 | P14-1 … P14-6 | established (each) | §3.1 |
| PO-14 | conclusion | **established** | §3.1 |
| AD-7 | four premises | established (each) | §3.4 |
| AD-7 | conclusion | **established** | §3.4 |
| PO-15 | (a) lists | established | §4.3 |
| PO-15 | (b) `FragmentPath` | established (as of last load or reload) | §4.3 |
| PO-15 | (c) `DropInPaths` | established | §4.3 |
| PO-15 | (d) `NeedDaemonReload` | **refuted** | §4.3 |
| PO-15 | (e) `Exec*` printed form and flag | established | §4.4 |
| PO-15 | (f) staging directory outside unit paths | established | §4.3 |
| PO-15 | requirement | **refuted** | §4.3 |
| PO-8 | S-1 … S-10 | established (each) | §5 |
| PO-8 | (a), (b), (c) and requirement | **established** | §5 |
| PO-11 | (b) | **not established** (MF-3); `/usr/share` sub-limb established on R2 evidence | §6.4, §R2-2 |
| PO-11 | (c) | established | §6.4 |
| PO-11 | (d) | **not established** (no citable bound) | §6.4 |
| PO-11 | (e) | established | §6.4 |
| PO-11 | (f)(i) | established | §6.4 |
| PO-11 | (f)(ii) | not established | §6.4 |
| PO-11 | (f)(iii) | not established | §6.4 |
| PO-11 | (f)(iv) | established | §6.4 |
| PO-11 | (g) | **not established** (depends on (b)) | §6.4 |
| PO-11 | requirement | **not established** | §6.4 |
| PO-20 | (a) | not established (MF-5) | §7 |
| PO-20 | (b), (c), (e), (g), (h) | established (each; (g) for named objects) | §7 |
| PO-20 | (d) | not established (MF-5) | §7 |
| PO-20 | (f) | **refuted** | §7 |
| PO-20 | requirement | **refuted** | §7 |
| PO-21 | (a), (b), (d) … (r), (t) … (v) | established (each; (l) with the recorded precision) | §8 |
| PO-21 | (c) | **refuted** | §8 |
| PO-21 | (s) | **refuted** | §8 |
| PO-21 | requirement | **refuted** | §8 |
| CL-21i | closed list CL-21i-1 … CL-21i-5; single disarm `/run/nextroot` absent | **established** (non-empty) | §9 |
| PO-12 | reads no `PYTHON*` variable | **refuted** | §10.4 |
| PO-12 | `sys.path[0]` not prepended | established | §10.4 |
| PO-12 | no `site` import | established | §10.4 |
| PO-12 | only files under the root-owned prefix | **refuted** | §10.4 |
| PO-12 | requirement | **refuted** | §10.4 |
| AS-8 | requirement | **refuted** | §10.4 |
| PO-12′ | offered restatement, not a requirement or verdict substitute | source-established; binding needs MF-4 | §10.4 |
| PT-8 | `os.renameat2`; `os.RENAME_NOREPLACE` | **refuted** (neither exists); `ctypes` retained | §10.5 |
| PO-19 | (a) | **not established** (source part established; binding needs MF-1) | §11.2 |
| PO-19 | (b) | established | §11.3 |
| PO-19 | (c) | established | §11.4 |
| PO-19 | (d) | **not established** (MF-2) | §11.5 |
| PO-19 | requirement | **not established** | §11.6 |
| D9-1 | AD-3, AD-4, AD-6, AD-11, AD-12 | established (each) | §12 |
| D9-1 | AD-8 | **refuted** as a general statement; established for the closed D2 inventory | §12 |
| D9-1 | unmounted case | not established | §12 |
| D9-1 | entry grammar | established | §12 |
| D9-1 | requirement | **refuted** | §12 |
| PO-17 boundary | premises 1–5 and 7 | established | §12.9 |
| PO-17 boundary | premise 6 (unmounted) | not established | §12.9 |
| PO-17 | against a launcher image | **not established — not evaluated** (OH-S4p supplies the image) | §12.9 |

---

## 0. Outcome

### 0.1 Verdict summary

Each requirement receives exactly one verdict. Where a requirement has several
limbs, each limb has its own verdict and the requirement takes the weakest:
**refuted** if any limb is refuted, otherwise **not established** if any limb is
not established, otherwise **established**.

| Requirement | Verdict | Decisive limb(s) | Section |
|---|---|---|---|
| **PO-14** (with TR-7/LB-2S provenance) | **established** | all six premises | §3 |
| **AD-7** | **established** | — | §3.4 |
| PO-15 | **refuted** | (d) `NeedDaemonReload` reflects only strictly newer mtimes and drop-in set changes | §4 |
| PO-8 (S-1 … S-10) | **established** | — (precisions recorded) | §5 |
| PO-11 (b) … (g) | **not established** | (b) and (g): `/etc/polkit-1/rules.d` content; (d), (f)(iii): no citable bound; (f)(ii): GLib behaviour outside the authorized sources | §6 |
| PO-20 (a) … (h) | **refuted** | (f) `flock` release is tied to the last reference of the open file description, not to process end; (a), (d): crash/durability limbs await MF-5 | §7 |
| PO-21 (a) … (v) | **refuted** | (c) `ExecStopPost=` is skipped if PID 1 cannot spawn it; (s) wording and strictness | §8 |
| **CL-21i** | **established** (non-empty closed list) | — | §9 |
| PO-12 | **refuted** | `PYTHONEXECUTABLE` and `__PYVENV_LAUNCHER__` are read and acted on under `-I` | §10 |
| AS-8 | **refuted** | as PO-12 | §10 |
| PT-8 (`os.renameat2`, `os.RENAME_NOREPLACE`) | **refuted** (neither exists) — `ctypes` retained | — | §10.5 |
| PO-19 (U-9) | **not established** | (a) executable-specific binding and (d) ownership need MF-1, MF-2; (b), (c) established | §11 |
| D9-1 | **refuted** | AD-8 as a general statement (established for the closed launcher inventory); unmounted case not established | §12 |

### 0.2 Terminal dispositions (reported, not decided)

The prompt fixes these consequences. They are reported without qualification.

1. **The activation design returns to design review.** Refuted items: PO-20
   (f), PO-21 (c) and PO-21 (s). Independently, PO-11 (d) has no citable bound,
   and the accepted design states that `ACT` and `DEACT` then return to design
   review rather than polling without a bound (design §4.4.2a).
2. **Route 1 returns to Route 3 design review.** PO-12 is refuted for CPython
   3.14.4 (§10). A source-established restatement, **PO-12′**, is offered in
   §10.4 for the reviewer. It is not a substitute verdict.
3. PO-15 (d) and AD-8 are refuted as worded. Neither is on the prompt's list of
   automatic returns. Each is returned to design review for restatement
   (§15.3).
4. PO-19 is **not established**, not refuted. It does not by itself trigger
   Route 3. It cannot be accepted until MF-1 and MF-2 are observed and the
   citation is bound to them (§11.6).
5. *(R2)* R2 changes **no** verdict and **no** disposition above. Its
   re-retrieval re-establishes, under authority, only the three `/usr/share`
   rule identifications that support PO-11 (b) and (g) (§R2-2). These
   dispositions remain reported for review, not decided.

### 0.3 What this record does not do

It does not claim PO-17 for any launcher image (§12.9), inspect any host, edit
any implementation, accept any H-0 fact anew, or amend any accepted record.
Corrections to accepted texts are proposed in §15 for the reviewer.

---

## 1. Fixed inputs and how they are used

### 1.1 Accepted H-0 inputs

These come from the composed `H-0 PASS`
([review](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-composed-h0-pass.md),
[acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-acceptance-and-u9.md)),
read only from the durable [R5](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-handback.md)
and [H-0G](phase-5-0-p5-r5-rp11-h1-h0g-r1-handback.md) handbacks.

| Input | Value | Anchor / evidence |
|---|---|---|
| kernel | `7.0.0-31-generic` `#31-Ubuntu`, `x86_64` | A-3; R5 c043 |
| systemd | `259.5-0ubuntu3.4` | A-4; R5 c045, c046 |
| polkitd | `127-2ubuntu1.1` | A-5; R5 c050 |
| libc6 | `2.43-2ubuntu2.4` | A-6; R5 c052 |
| python3.14-minimal | `3.14.4-1ubuntu0.2` | A-7; R5 c072 |
| interpreter | `/usr/bin/python3.14`, regular file, `root:root` `0755`, 7468968 bytes | H-0G c021 |
| interpreter SHA-256 | `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` | A-8 |
| `-I -S` runtime | `3.14.4`, `isolated=1`, `no_site=1`, `executable=/usr/bin/python3.14`, `prefix=/usr`, `sys.path=['/usr/lib/python314.zip', '/usr/lib/python3.14', '/usr/lib/python3.14/lib-dynload']` | H-0G c022 |
| loader inputs (HF-09) | `/lib64/ld-linux-x86-64.so.2` → `/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2` (`root:root` `0755`); `/etc/ld.so.preload` absent; `/etc/ld.so.cache` `root:root` `0644`; `/etc/ld.so.conf` and three `/etc/ld.so.conf.d/*.conf`, all `root:root` `0644` | R5 c098–c102 |
| polkit rules dirs (HF-12) | `/etc/polkit-1/rules.d` `root:polkitd` `0750`, **unreadable**; `/usr/share/polkit-1/rules.d` nine entries with digests; `/run/polkit-1/rules.d` and `/usr/local/share/polkit-1/rules.d` absent | R5 c106–c116 |
| `ubuntu` groups (HF-03) | `ubuntu adm cdrom sudo dip lxd freedomlab` | R5 c033–c042 |
| unit paths (HF-13) | 12 paths, from `/etc/systemd/system.control` to `/run/systemd/generator.late` | R5 c118 |
| `binfmt_misc` (HF-14) | mounted; `status` `enabled`; one entry `python3.14`, `enabled`, interpreter `/usr/bin/python3.14`, flags empty, offset 0, magic `2b0e0d0a` | R5 c120–c123 |
| filesystems (HF-15) | `/`, `/var/lib`, `/var/tmp` … on `/dev/sda1` `ext4` `rw,relatime,discard,errors=remount-ro,commit=30`; `/run` `tmpfs` `…,inode64` | R5 c124–c143; A-10 |
| manager defaults (HF-16) | 52 `Default*` values, including `DefaultTimeoutStartUSec=1min 30s` | R5 c144 |
| soft-reboot units (HF-20a) | `systemd-soft-reboot.service`, `soft-reboot.target` `LoadState=loaded` | R5 c151 |

### 1.2 The dynamic-section fact is not established

Neither R5 nor H-0G recorded any dynamic-section fact for
`/usr/bin/python3.14`. A search of both durable handbacks for `RUNPATH`,
`RPATH`, `readelf` and "dynamic section" returns nothing. As the prompt
requires, **`DT_RUNPATH`/`DT_RPATH` is marked unestablished** and is not
inferred from any other binary. Its observation is MF-1 (§14.3), assigned to a
later gated read-only slice. The same applies to `DT_NEEDED`, `DT_FLAGS_1` and
`PT_INTERP`, which the PO-19 binding also needs.

No other fixed input was missing or contradictory.

---

## 2. Sources and method

### 2.1 Authorized sources consulted

All retrievals were on 2026-10-06 between 16:57Z and 17:50Z. Launchpad
`+sourcefiles` URLs have the form
`https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/<src>/<version>/<file>`.
The complete download ledger with sizes is Appendix D.
*(R2)* These are R1's retrievals, carried as R1's durable citations. The R2
retrieval (2026-10-06, 19:10:45Z–19:11:07Z) covers only the three packages in
the *(R2)* row below; its ledger is Appendix E.

| Component | Exact source | Files (SHA-256) | Upstream reconciliation |
|---|---|---|---|
| systemd | Ubuntu source `systemd` `259.5-0ubuntu3.4` (page `https://launchpad.net/ubuntu/+source/systemd/259.5-0ubuntu3.4`) | `.dsc` `c4c764e0…218f8177`; `orig.tar.gz` `80ed55a8…48be0f76`; `debian.tar.xz` `34048bc4…0c74aaa9` | `orig` is byte-identical to upstream `https://github.com/systemd/systemd/archive/refs/tags/v259.5.tar.gz` (same SHA-256). 40 Ubuntu patches |
| polkit | Ubuntu source `policykit-1` `127-2ubuntu1.1` (binary `polkitd`) | `.dsc` `838df29d…488c00f6`; `orig.tar.gz` `9b7bc16f…f6d8b988`; `debian.tar.xz` `2f8f11ca…333da73d` | `orig` byte-identical to `https://github.com/polkit-org/polkit/archive/refs/tags/127.tar.gz`. 2 Ubuntu patches, both in `src/polkitagent/polkitagenthelperprivate.c` |
| glibc | Ubuntu source `glibc` `2.43-2ubuntu2.4` | `.dsc` `da10d551…8e482ed3`; `orig.tar.xz` `d9c86c6b…d5fa3831`; `debian.tar.xz` `28103a7c…8533e306` | `orig` byte-identical to `https://mirrors.kernel.org/gnu/glibc/glibc-2.43.tar.xz` (`ftp.gnu.org` unreachable; `sourceware.org/pub/glibc/releases/` returned 404). 103 Ubuntu/Debian patches |
| CPython | Ubuntu source `python3.14` `3.14.4-1ubuntu0.2` | `.dsc` `00771af0…4911e165`; `orig.tar.xz` `d923c513…d7faaef8`; `debian.tar.xz` `c23cc6a2…cff31fbe` | `orig` byte-identical to `https://www.python.org/ftp/python/3.14.4/Python-3.14.4.tar.xz`. 45 Ubuntu/Debian patches |
| Linux | Ubuntu source `linux` `7.0.0-31.31` (matches HF-04 `7.0.0-31-generic #31-Ubuntu`) | `.dsc` `70114682…8fba9c71`; `orig.tar.gz` `c6343795…3f149536`; `diff.gz` `7d1ee5c5…4b33cd6a` | `orig` equals `linux-7.0.tar.gz` in `https://cdn.kernel.org/pub/linux/kernel/v7.x/sha256sums.asc` (file SHA-256 `bf9dc5d2…34e4828e`). The Ubuntu delta raises the tree to upstream stable `7.0.14` (`SUBLEVEL = 14`) plus Ubuntu changes |
| ~~polkit rules from other packages~~ *(R2: non-authoritative R1 row, retained as history)* | R1 retrieved `bolt` `0.9.10-1`, `fwupd` `2.1.1-1ubuntu3.1`, `packagekit` `1.3.4-3ubuntu1.2` and Launchpad `getPublishedSources` metadata **outside R1's source authority (R1-F2)** | Appendix D (R1 rows, non-authoritative) | **not used as evidence in this record** |
| *(R2)* polkit rules from other packages | Ubuntu source `bolt` `0.9.10-1`, `fwupd` `2.1.1-1ubuntu3.1`, `packagekit` `1.3.4-3ubuntu1.2`, re-retrieved under the R2 authority | Appendix E | used **only** to derive and identify three host rule files by digest equality (§R2-3, §6.1); no installed version was recorded by R5 or is claimed |

Not used: search snippets, blogs, Q&A sites, AI summaries, other
distributions, or any unversioned `main` branch. The x86-64 psABI document was
not consulted; AD-6 rests on kernel source (§12.3).

### 2.2 Ubuntu reconciliation

For systemd, polkit, glibc and CPython, the complete `debian/patches/series`
was applied with GNU `patch` to a copy of the upstream tree. Every patch
applied without fuzz failure (systemd 40, polkit 2, CPython 45, glibc 103).
**All line numbers below refer to these patched ("Ubuntu") trees.** For the
kernel, the Ubuntu `diff.gz` hunks for every cited file were applied the same
way. Patch-by-patch relevance is recorded in §15.2.

### 2.3 Method limits

* No downloaded code was executed. Processing was static reading, `tar`,
  `patch`, `sha256sum`, `grep`, and three standard-library Python scripts I
  wrote (vtable extraction, classification, table rendering) that read source
  text only.
* PGP signatures on `.dsc` files and on `sha256sums.asc` were **not** verified.
  Integrity rests on the `.dsc` checksums and on byte equality with the
  independently retrieved upstream release artifacts.
* Build-configuration facts (for example glibc's built-in directories) are
  derived from the packaging and build files. They are labelled *derived*, and
  corroborated by H-0 facts where possible. No package was built.
* *(R2)* R2 did not repeat these steps for systemd, polkit, glibc, CPython or
  Linux; it carries their results. For `bolt`, `fwupd` and `packagekit`, R2
  extracted only named members and reproduced two text substitutions on
  copies (§R2-3). The `.dsc` files themselves were not PGP-verified; their
  integrity rests on HTTPS retrieval from Launchpad.

### 2.4 Fact classes used in this record

| Tag | Meaning |
|---|---|
| **S** | source fact: read from the cited Ubuntu tree |
| **H** | durable H-0 fact: from the accepted R5/H-0G records |
| **M** | mechanical fact still missing: not observed by any accepted record (§14.3) |
| **R** | reasoned conclusion: drawn from S and H facts; the reasoning is stated |

---

## 3. PO-14 and AD-7 — first, load-bearing

**Obligation (C11 §14, design TR-7, LB-2S).** On systemd `259.5-0ubuntu3.4`,
the image that calls `execve` on `ExecStart=` is not loaded under the unit's
assembled block. Under systemd ≥ 255, `systemd-executor` is started with PID
1's own environment (AS-13). TR-7 states its inputs as "PID 1's own
environment; the execution context PID 1 passes it over a descriptor".

### 3.1 Premises, sources and conclusions

| # | Premise | Source (systemd-259.5, Ubuntu tree) | Class | Verdict |
|---|---|---|---|---|
| P14-1 | Every command of a unit (`ExecStart=`, `ExecStartPre=`, …) is started by `exec_spawn()`, which requires a pinned executor (`assert(unit->manager->executor_fd >= 0)`) and has no forked-PID-1 alternative in this version | `src/core/execute.c:470–487` | S | **established** |
| P14-2 | The executor process is created by `posix_spawn_wrapper(FORMAT_PROC_FD_PATH(executor_fd), {executor_path, "--deserialize", fd, "--log-level", …, "--log-target", …}, environ, cgtarget, &pidref)`. The environment argument is PID 1's own `environ` | `src/core/execute.c:586–593`; `posix_spawn_wrapper` passes `envp` unchanged to `pidfd_spawn`/`posix_spawn`, `src/basic/process-util.c:2189`, `:2209`, `:2222` | S | **established** |
| P14-3 | The unit's execution context, command and parameters are serialized to a file whose descriptor alone is passed (`exec_serialize_invocation`); the executor deserializes it, and the assembled block is built inside the executor and given **only** to the command's `execve` | `src/core/execute.c:536–556`; `src/core/executor.c:235–256`; assembly `src/core/exec-invoke.c:5664–5716`; `UnsetEnvironment=` last, `:6394–6401`; `fexecve_or_execve(…, accum_env)`, `:6475` | S | **established** |
| P14-4 | PID 1's own `environ` is: the kernel-supplied initial environment as adjusted by PID 1 (`TERM` set, `COLORTERM`/`NO_COLOR` imported from the kernel command line when `TERM=` is given there, `HOME=/` removed, `COLUMNS`/`LINES` set or removed for the console), plus `ManagerEnvironment=` from `system.conf` and `system.conf.d`, applied at start-up and at every reload. It is not changed by `DefaultEnvironment=`, `systemd.setenv=`, environment generators or the D-Bus `SetEnvironment`/`UnsetEnvironment` methods, which all act on the manager's separate `transient_environment`/`client_environment` | `src/core/main.c:1550–1597` (`fixup_environment`), `:216–237`, `:2726–2736` (`setenv_manager_environment`), `:2820–2845`, `:2207` (reload); `man/systemd-system.conf.xml:669–679`; `src/core/manager.c:658–706` (system manager starts children from a clean block), `:4187–4229`; `src/core/dbus-manager.c:1922`, `:1957`, `:1999`; `src/core/main.c:405–413`, `:861–880` | S | **established** |
| P14-5 | The executor binary is pinned at manager start by `pin_callout_binary(SYSTEMD_EXECUTOR_BINARY_PATH)`. A `SYSTEMD_EXECUTOR_PATH` variable in PID 1's own environment (read with `secure_getenv`) overrides the path | `src/core/manager.c:1033–1037`; `src/basic/build-path.c:196–217`, `:249–288`; `meson.build:275` | S | **established** |
| P14-6 | No Ubuntu patch modifies `execute.c`, `exec-invoke.c`, `executor.c`, `execute-serialize.c`, `process-util.c`, `build-path.c` or `main.c`. The only `src/core/manager.c` hunk adds `XDG_SESSION_EXTRA_DEVICE_ACCESS` to the *user* manager's unset list | `debian/patches/series`; `lp2077538/login-Add-XDG_SESSION_EXTRA_DEVICE_ACCESS-variable-for-ad.patch`; patched `manager.c:700` | S | **established** |

**Conclusion (R).** For this version, the image that calls `execve` on
`ExecStart=` is `systemd-executor`. It is started with PID 1's own process
environment and receives the unit's context over a descriptor. The assembled
block exists only inside the executor and is passed only to the command's
`execve`. **PO-14 is established.** LB-2S is not withdrawn for this version.

### 3.2 Provenance refinements (recorded; not refutations)

These are precise source facts about TR-7's input. Neither makes the executor
load under the unit's block, and both are root or boot state, the trust class
LB-2S assigns to PID 1 (R-8).

* **PR-14a.** C11 §4.4.3.2 row E-9 describes PID 1's own environment as set
  "at boot by the kernel and the initrd". In 259.5 it also receives
  `ManagerEnvironment=` from root-owned `system.conf`/`system.conf.d`, applied
  at start-up and on each `daemon-reload`. The E-9 "who can change it" cell is
  therefore incomplete. It should read "kernel, initrd and root-owned manager
  configuration (`ManagerEnvironment=`)".
* **PR-14b.** The executor *image* PID 1 uses is selectable by
  `SYSTEMD_EXECUTOR_PATH` in that same environment. Whatever image is pinned is
  started under PID 1's environment, not the unit's block.

`/proc/1/environ` is root-readable only, so neither fact is observable by
`ubuntu`. No PO-14 conclusion depends on observing it.

### 3.3 Requester and execution-context limbs of TR-7

TR-7's other entries (root → `ubuntu` through `User=`, `NoNewPrivileges=yes`,
`UMask=0077`, `WorkingDirectory=/`, `/dev/null` input, journal stream outputs)
are applied inside the executor before `execve`: `exec-invoke.c:5409–5428`
(standard I/O), `:5718` (umask), `:6183` (working directory), `:6136–6145`
(`enforce_user`), `:6249–6253` (`PR_SET_NO_NEW_PRIVS`). None comes from the
requester (§5, S-8). They are not prevention claims in LB-2S and are recorded
for completeness.

### 3.4 AD-7 — `INVOCATION_ID` format

| Premise | Source | Verdict |
|---|---|---|
| Each start acquires a fresh random 128-bit ID | `src/core/unit.c:5472–5487` (`sd_id128_randomize`); called from `service_start`, `src/core/service.c:3026` | **established** |
| The string form is `sd_id128_to_string`: 16 bytes, each as two characters from `"0123456789abcdef"` | `src/libsystemd/sd-id128/sd-id128.c:21–29`; `src/basic/hexdecoct.c:35–39`; `src/core/unit.c:3399` | **established** |
| The executor re-derives the string from the parsed 128-bit value | `src/core/execute-serialize.c:1516–1524` | **established** |
| The block entry is `INVOCATION_ID=<that string>` | `src/core/exec-invoke.c:2167–2169` | **established** |

**AD-7 is established**: `INVOCATION_ID` is exactly 32 lowercase hexadecimal
digits, matching `rp11-launch/1`'s `[0-9a-f]{32}`.

---

## 4. PO-15 — loaded-configuration reporting and the version-bound property lists

### 4.1 How `systemctl show` reports properties (S)

| Fact | Source | Verdict |
|---|---|---|
| `systemctl show <unit>` issues one `GetAll` with interface `""`, so it returns every interface on the unit object | `src/systemctl/systemctl-show.c:2330–2338`; `src/shared/bus-map-properties.c:235–238` | established |
| `GetAll` omits properties flagged `SD_BUS_VTABLE_HIDDEN` or `SD_BUS_VTABLE_PROPERTY_EXPLICIT` | `src/libsystemd/sd-bus/bus-objects.c:767–783` | established |
| A `-p` name the manager does not return is skipped with a debug message. The exit status is still 0 | `src/systemctl/systemctl-show.c:2375–2381` | established |
| `-p` prints a requested property even when empty | `src/systemctl/systemctl.c:599–602` | established |
| A service object exposes `org.freedesktop.systemd1.Unit` (`bus_unit_vtable`) and `org.freedesktop.systemd1.Service` (`bus_service_vtable`, `bus_unit_cgroup_vtable`, `bus_cgroup_vtable`, `bus_exec_vtable`, `bus_unit_exec_vtable`, `bus_kill_vtable`) | `src/core/dbus.c:436–442`, `:487–497` | established |
| `systemctl show` with no unit returns the manager object (`bus_manager_vtable`) | `src/core/dbus.c:546–550` | established |

**Consequence (R).** The design's rule "a property the installed manager does
not report is a stop" (§4.3.3) must be enforced by the H-1/H-2 tool itself.
`systemctl` does not fail.

### 4.2 Complete property lists (version-bound)

Extracted mechanically from the vtables of the Ubuntu tree. The extractor
expands `BUS_PROPERTY_DUAL_TIMESTAMP`, `BUS_EXEC_STATUS_VTABLE` and the
`BUS_EXEC_*COMMAND*_VTABLE` macros, records flags, and was checked against a
raw count of entries per vtable (all eight vtables equal). No vtable contains a
preprocessor conditional. The patched and upstream extractions have identical
names and flags. R5's HF-16 observation is reproduced exactly: the 52 visible
`Default*` names equal R5 c144's 52 reported names, and the three R5 did not
receive (`DefaultCPUAccounting`, `DefaultBlockIOAccounting`,
`DefaultSmackProcessLabel`) are respectively `HIDDEN`, `HIDDEN` and absent.

* **Unit (service) list:** 464 visible properties. **Appendix A.**
* **Manager list:** 126 visible properties. **Appendix B.**
* 27 service names are hidden and never printed, including the deprecated
  service-level duplicates of `StartLimit*`, `FailureAction` and
  `RebootArgument` (Appendix C.1).

### 4.3 Verdicts on PO-15's limbs

| Limb | Statement | Verdict | Basis |
|---|---|---|---|
| (a) | the complete version-bound unit and manager lists | **established** | §4.2, Appendices A–B |
| (b) | `FragmentPath` reflects unit-path precedence | **established** as of the last load or reload: the name map takes the first (highest-priority) search directory that holds the name, `src/shared/unit-file.c` `unit_file_build_name_map` (lines 366–550, comment at 530–533). A fragment created later in a higher-priority directory is not reflected until a reload | S |
| (c) | `DropInPaths` includes top-level type drop-ins and run-time drop-ins | **established**, and more: every search directory is scanned for `<unit>.d`, for each **dash-prefix** form (`rp11-capture-pass-.service.d`, `rp11-capture-.service.d`, `rp11-.service.d`) and for `service.d`, and the run-time directories `/etc/systemd/system.control`, `/run/systemd/system.control` and `/run/systemd/transient` are in the search path (R5 c118) | `src/shared/dropin.c:166–238`, `:240–295` |
| (d) | `NeedDaemonReload` reflects unapplied changes | **refuted** as an unconditional statement. It is `yes` only if (i) the manager's unit-file state was marked outdated by a D-Bus unit-file operation, (ii) the fragment or source path is inaccessible or has an mtime **strictly newer** than at load, or (iii) the drop-in set changed or a drop-in is strictly newer. A fragment rewritten with an mtime not newer than the recorded one, or a new fragment in a higher-priority directory, leaves it `no` | `src/core/unit.c:3823–3846`, `:3848–3879`; `src/core/dbus-manager.c:2338` |
| (e) | `ExecStartPre`'s printed form and its flag | **established**: see §4.4 | S |
| (f) | the staging directory is in no unit search directory | **established**: `/usr/local/libexec/freedom-blades-rp11/staged/` is not among R5 c118's 12 paths | H + S |

**PO-15 is refuted** (limb (d)). Consequence (R): §4.3.3's derivation that the
E-set is empty ("the fragment digest equals the reviewed bytes … and
`NeedDaemonReload=no`") additionally rests on the root-trust assumption that
no root actor replaced the fragment while keeping a non-newer mtime. That is
within R-10's trusted-root model, but the citation cannot assert it. Returned
for restatement (§15.3).

### 4.4 `Exec*` printed form (PO-15 (e))

`systemctl show` prints each `Exec*` property, for every element, as:

```text
<Name>={ path=<path> ; argv[]=<argv joined by single spaces> ; ignore_errors=<yes|no> ; start_time=[<ts>] ; stop_time=[<ts>] ; pid=<pid> ; code=<code> ; status=<int>[/<SIG>] }
<Name>Ex={ path=<path> ; argv[]=<argv joined by single spaces> ; flags=<space-separated flags> ; start_time=[<ts>] ; stop_time=[<ts>] ; pid=<pid> ; code=<code> ; status=<int>[/<SIG>] }
```

Source: `src/systemctl/systemctl-show.c:1515–1567`. Flag names, in bit order:
`ignore-failure`, `privileged`, `no-setuid`, `no-env-expand`, `via-shell`
(`src/shared/exec-util.c:482–488`, `src/shared/exec-util.h:47–53`).

* **The `+` prefix is invisible in `ExecStartPre`.** The non-`Ex` form carries
  only `ignore_errors`. The `+` prefix appears only in **`ExecStartPreEx`**, as
  `flags=privileged` (`src/core/dbus-execute.c:1517–1545`, `:1644–1648`). The
  §4.2.5-R4 (h) normalization must therefore read `ExecStartPreEx` for the
  flag. The expected normalized value is `path=/usr/bin/python3.14`,
  `argv[]=/usr/bin/python3.14 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume`,
  `flags=privileged`. The same applies to `ExecStart`/`ExecStartEx` (`flags=`
  empty).
* `argv[]` is joined with single spaces and is ambiguous if an argument
  contains a space. No literal in the design does.

### 4.5 Environment-bearing and volatile sets (contradictions for review)

* **`UnsetEnvironment` can carry values.** Its entries are names or exact
  `NAME=VALUE` assignments (`src/basic/env-util.c:234–258`). §4.3.3 lists it
  as "names only, required empty". Querying it can print an assignment. The
  reviewer should either move it to E or require the tool to record emptiness
  only.
* **Two further directives shape the block:** `ExecSearchPath=` (sets `PATH`,
  `exec-invoke.c:5690–5704`) and `SetLoginEnvironment=` (`USER`, `LOGNAME`,
  `HOME`, `SHELL`, `exec-invoke.c:2125–2165`). Both are ordinary compared
  properties in Appendix A.
* **The design's V rule does not cover every run-time-varying property of
  259.5.** 109 visible properties are not `PROPERTY_CONST` and not in V or E.
  Appendix C.2 lists them in three groups: 30 run-time state values (for
  example `Job`, `Refs`, `ConditionResult`, `Conditions`, `FreezerState`,
  `OOMKills`, `UID`, `GID`, `UnitFileState`, `NeedDaemonReload`), 16 `Exec*`
  arrays (normalized under §4.4), and 63 run-time-settable configuration
  properties (`set-property --runtime`), which should stay compared. The split
  is a reasoned proposal (R), not a source classification.

---

## 5. PO-8 — semantics S-1 … S-10

Sources: systemd-259.5 Ubuntu tree. Each verdict is for 259.5 only.

| # | Claim (C11 §4.4.3.1) | Verdict | Source and precision |
|---|---|---|---|
| S-1 | Assembly order (a) manager global → (b) manager-defined → (c) `PassEnvironment=` → (d) `Environment=` → (e) `EnvironmentFile=` → (f) PAM; later wins | **established** | `exec-invoke.c:5706–5716`: `strv_env_merge(params->environment, our_env, joined_exec_search_path, pass_env, context->environment, params->files_env)`; then `TERM` for TTY units (`:5720`, `:4939–5000`); then PAM (`:5775`, `:1405–1425`); then `UnsetEnvironment=` (`:6394–6401`). (a) is `transient_environment` (default `PATH`, locale from `/etc/locale.conf`/`locale.*=`, `DefaultEnvironment=`, `systemd.setenv=`, environment-generator output) merged with `client_environment` (`SetEnvironment`), `manager.c:4231–4242`, `:658–706`; `main.c:861–880`. Service-level variables (`MAINPID`, `SERVICE_RESULT`, `MONITOR_*`, `TRIGGER_*`, …) are merged into (a) before (b), `service.c:1792–1915`. **Additions to the stated order:** `ExecSearchPath=` `PATH` between (b) and (c); `TERM` (TTY units only) after (e) |
| S-2 | PID 1's own environment is not passed except names in `PassEnvironment=` | **established** | system manager starts from a clean block, `manager.c:658–676`; `PassEnvironment=` reads the executor's own environment (= PID 1's, §3), `exec-invoke.c:2278–2304` |
| S-3 | Manager-defined variables vary by version | **established**; the closed 259.5 set is: `exec-invoke.c` `build_environment` (`:2039–2276`): `LISTEN_PID`, `LISTEN_PIDFDID`, `LISTEN_FDS`, `LISTEN_FDNAMES`, `WATCHDOG_PID`, `WATCHDOG_USEC`, `SYSTEMD_NSS_DYNAMIC_BYPASS`, `USER`, `LOGNAME`, `HOME`, `SHELL`, `INVOCATION_ID`, `JOURNAL_STREAM`, `LOG_NAMESPACE`, `RUNTIME_DIRECTORY`, `STATE_DIRECTORY`, `CACHE_DIRECTORY`, `LOGS_DIRECTORY`, `CONFIGURATION_DIRECTORY`, `CREDENTIALS_DIRECTORY`, `SYSTEMD_EXEC_PID`, `MEMORY_PRESSURE_WATCH`, `MEMORY_PRESSURE_WRITE`, `NOTIFY_SOCKET`, `TMPDIR`; `service_spawn` (`service.c:1797–1915`): `FDSTORE`, `MAINPID`, `MAINPIDFDID`, `MANAGERPID`/`MANAGERPIDFDID` (user manager only), `PIDFILE`, `REMOTE_ADDR`, `REMOTE_PORT`, `SO_COOKIE`, `[MONITOR_]SERVICE_RESULT`, `[MONITOR_]EXIT_CODE`, `[MONITOR_]EXIT_STATUS`, `MONITOR_INVOCATION_ID`, `MONITOR_UNIT`, `DEBUG_INVOCATION`; activation details `TRIGGER_UNIT`, `TRIGGER_PATH`, `TRIGGER_TIMER_REALTIME_USEC`, `TRIGGER_TIMER_MONOTONIC_USEC` (`unit.c:6952`, `path.c:962`, `timer.c:971–975`); `TERM`/`COLORTERM`/`NO_COLOR` (TTY units only, `exec-invoke.c:4939–5000`) |
| S-4 | No allow-list directive; `UnsetEnvironment=` takes names or exact `NAME=VALUE`, no pattern, applied last | **established** | directives that shape the block: `Environment`, `EnvironmentFile`, `PassEnvironment`, `UnsetEnvironment`, `ExecSearchPath`, `SetLoginEnvironment`, `PAMName` (`src/core/load-fragment-gperf.gperf.in:22`, `:35–38`, `:124`, `:174`); matching `env-util.c:234–258`; applied last `exec-invoke.c:6394–6401`. None discards (a) as a class |
| S-5 | The loaded configuration is not one file | **established**, with the dash-prefix drop-ins of §4.3 (c) added |
| S-6 | Filtering happens in the process that `execve`s, immediately before | **established** | §3 P14-3 |
| S-7 | Run-time mutation | **established**: `SetEnvironment`/`UnsetEnvironment`/`UnsetAndSetEnvironment` change `client_environment` under polkit action `org.freedesktop.systemd1.set-environment` (defaults `auth_admin`/`auth_admin`/`auth_admin_keep`, `src/core/org.freedesktop.systemd1.policy.in:53–61`); `daemon-reload` re-parses `system.conf` (`main.c:2207`), rebuilds the transient environment (`main.c:2209`, `:861–880`) and re-runs environment generators and generators (`manager.c:3634–3635`). `client_environment` survives reload and re-exec (serialized, `manager-serialize.c:134–135`) but not soft-reboot (`switching_root`) |
| S-8 | `systemctl start` carries no requester environment, descriptor, working directory, limit or confinement | **established**: `StartUnit` with signature `ss` (name, mode), `src/systemctl/systemctl-start-unit.c:141`; the method reads only the mode, `src/core/dbus-unit.c:379–440`; `--no-ask-password` clears the interactive-authorization header, `src/systemctl/systemctl-util.c:68`. The sender's bus credentials are used only for the polkit check (§6) |
| S-9 | `User=` is not a secure-mode transition; `NoNewPrivileges=` filters no environment | **established**: credentials are switched in the executor before `execve` (`exec-invoke.c:6136–6145`), so the command starts with real = effective IDs and is not set-ID; `PR_SET_NO_NEW_PRIVS` is a single `prctl` (`:6249–6253`). Kernel side: AT_SECURE arises only from an ID change or capability gain at exec (`security/commoncap.c` `cap_bprm_creds_from_file`), which neither causes |
| S-10 | No `PAMName=` → no PAM | **established**: PAM runs only `if (needs_setuid && context->pam_name && username)`, `exec-invoke.c:5770–5779` |

PO-8 (a), (b), (c) follow from S-1 … S-10, S-8 and S-7 respectively. **PO-8 is
established.**

---

## 6. PO-11 (b) … (g) — polkit 127 and systemd's action

### 6.1 Distribution rules on the host, identified by digest (S + H)

All nine entries R5 recorded under `/usr/share/polkit-1/rules.d` were
identified byte-for-byte:

| Host file (R5 digest) | Identified as | Grant |
|---|---|---|
| `10-systemd-logind-root-ignore-inhibitors.rules` (symlink) and `.example` (`0dcb4cdb…`) | systemd `src/login/10-systemd-logind-root-ignore-inhibitors.rules.example` | `login1.*-ignore-inhibit` for `root` only |
| `49-ubuntu-admin.rules` (`54399500…`) | `policykit-1/debian/49-ubuntu-admin.rules` | `addAdminRule`: admin identities `sudo`, `admin`; grants nothing |
| `50-default.rules` (`29f073ed…`) | polkit `src/polkitbackend/50-default.rules.in` rendered with `@PRIVILEGED_GROUP@`=`sudo` (`meson.build:323–328`, `os_type=debian`) | `addAdminRule` only |
| `empower.rules` (`d9a62ab1…`) | systemd `src/run/empower.rules` | **`YES` for every action** if `subject.isInGroup("empower")` |
| `org.freedesktop.bolt.rules` (`16da883b…`) | *(R2 evidence, §R2-3)* bolt `0.9.10-1` `policy/org.freedesktop.bolt.rules.in` with `@privileged_group@`=`sudo` (`debian/rules:15`) | `bolt.*`, active local `sudo` subjects |
| `org.freedesktop.fwupd.rules` (`f78e67e4…`) | *(R2 evidence, §R2-3)* fwupd `2.1.1-1ubuntu3.1` `policy/org.freedesktop.fwupd.rules` after `debian/rules:56` (`wheel`→`sudo`) | `fwupd.update-internal` |
| `org.freedesktop.packagekit.rules` (`d22e59e8…`) | *(R2 evidence, §R2-3)* packagekit `1.3.4-3ubuntu1.2` `policy/org.freedesktop.packagekit.rules`, unchanged | three `packagekit.*` update actions |

*(R2)* The three rows above rest on the R2 retrieval only; R1's identification
of them is non-authoritative (R1-F2). The other rows are carried from R1's
authorized systemd `259.5` and polkit `127` sources.
| `systemd-networkd.rules` (`f199e386…`) | systemd `src/network/systemd-networkd.rules` | `hostname1`/`timedate1` actions for `systemd-network` |

None grants `org.freedesktop.systemd1.manage-units` or
`org.freedesktop.systemd1.manage-unit-files` (which **implies**
`manage-units`, `org.freedesktop.systemd1.policy.in:42–51`) to `ubuntu`,
except `empower.rules` if `ubuntu` were in group `empower`. HF-03 records that
it is not. Membership is evaluated through NSS at each decision, so adding
`ubuntu` to `empower` is a root act of the SL-1 kind.

### 6.2 systemd's action and defaults (S)

* `StartUnit`/`StopUnit` call `bus_verify_manage_units_async_full(u, verb, …)`
  with details `unit` = unit ID and `verb` = `start`/`stop`
  (`src/core/dbus-unit.c:379–440`;
  `src/core/dbus-util.c:162–208`). The job is queued only after a positive
  decision (`bus_unit_queue_job` follows the check).
* Shipped defaults for `manage-units`: `allow_any=auth_admin`,
  `allow_inactive=auth_admin`, `allow_active=auth_admin_keep`
  (`org.freedesktop.systemd1.policy.in:32–40`).

### 6.3 polkitd 127 rule loading and reload (S)

| Fact | Source (polkit-127, Ubuntu tree) |
|---|---|
| Rules directories, in this order: `PACKAGE_SYSCONF_DIR "/polkit-1/rules.d"`, `"/run/polkit-1/rules.d"`, `"/usr/local/share/polkit-1/rules.d"`, and `PACKAGE_DATA_DIR "/polkit-1/rules.d"` when that is not `/usr/local/share` | `src/polkitbackend/polkitbackendduktapeauthority.c:254–264` |
| `PACKAGE_SYSCONF_DIR` = `/etc`, `PACKAGE_DATA_DIR` = `/usr/share` for this build (derived: `src/polkitbackend/meson.build:30–31` with Debian's debhelper meson prefix `/usr` and sysconfdir `/etc`; corroborated by HF-12, whose package rules sit in `/usr/share/polkit-1/rules.d`) | derived + H |
| polkitd has no option to change the list (`--no-debug` only) | `src/polkitbackend/polkitd.c:46–49` |
| Each load reads every directory **non-recursively** and takes names ending `.rules` | `polkitbackendduktapeauthority.c:101–163` |
| Files are sorted by **basename**, ties by full path. Files with equal basenames are **all** executed; none shadows another. `/etc` < `/run` < `/usr/local/share` < `/usr/share` in the tie order | `src/polkitbackend/polkitbackendcommon.c:456–480` |
| Each directory has a `GFileMonitor` set up once at construction | `polkitbackendduktapeauthority.c:194–230`, `:266–267` |
| Reload is synchronous in the monitor callback, for `CREATED`, `DELETED` or `CHANGES_DONE_HINT` on a name ending `.rules` not starting with `.` or `#`. There is no polkit-side timer, coalescing or bound (the source's own TODO notes this) | `polkitbackendcommon.c:326–357` |
| Reload drops all rules and re-reads all directories | `polkitbackendduktapeauthority.c:166–191` |
| Only uid 0 or an action owner may pass details to `CheckAuthorization` or check another identity's subject | `src/polkitbackend/polkitbackendinteractiveauthority.c:1045–1085` |
| A root **subject** is always authorized unless `ALWAYS_CHECK` | `polkitbackendinteractiveauthority.c:1234–1238` |

### 6.4 Verdicts

| Limb | Verdict | Basis |
|---|---|---|
| (b) no distribution rule grants `manage-units` to `ubuntu` without authentication, given HF-12 | **not established** | `/usr/share`: established (§6.1, given HF-03). `/run/polkit-1/rules.d` and `/usr/local/share/polkit-1/rules.d`: absent at H-0. **`/etc/polkit-1/rules.d`: unreadable to `ubuntu` (HF-12); its contents are MF-3.** All files there are evaluated before same-named `/usr/share` files. *(R2)* The `/usr/share` sub-limb's `bolt`/`fwupd`/`packagekit` entries now rest on R2 evidence (§R2-3); the verdict is unchanged, and MF-3 is not inferred from any distribution package |
| (c) the staging path is in no rules search directory | **established** | the four directories of §6.3; non-recursive; `.staged` does not end in `.rules` |
| (d) reload within a cited bound after `linkat`/`unlinkat` in `/etc/polkit-1/rules.d` | **not established** | reload is triggered only by a GIO monitor event; delivery latency belongs to GLib/inotify, which are outside the authorized sources, and polkit's own source contains no bound. Design §4.4.2a: "If no bound can be cited, `ACT` and `DEACT` return to design review" |
| (e) `pkcheck` exit statuses; `--detail` from an unprivileged caller | **established**: 0 authorized; 1 not authorized; 2 challenge (authentication required, and `-u` not given or no agent); 3 dismissed; 126 usage error; 127 error checking. An unprivileged caller passing `--detail` gets a `NOT_AUTHORIZED` *error*, so status 127, not "not authorized" | `src/programs/pkcheck.c:362–366`, `:546–556`, `:586–645`; interactive authority `:1045–1085` |
| (f)(i) `/run/polkit-1/rules.d` is in the search path; complete list; precedence between equal basenames | **established** | §6.3 |
| (f)(ii) rules loaded within the bound if `/run/polkit-1[/rules.d]` was created after polkitd started | **not established** | the monitor is created once; behaviour on a then-missing path is GLib's. Design fallback applies: AP-0 requires the directory to exist and `ACT` never builds tree R. Note: any later reload (from any monitored directory) re-reads all four directories |
| (f)(iii) (d)'s bound applies to `/run` | **not established** | same mechanism as (d) |
| (f)(iv) no rule held across polkitd restart or boot except what is read at start | **established** | rules live only in the Duktape heap built by `load_scripts` at construction and reload; temporary authorizations are in-memory |
| (g) with the rule granting `start` only, `ubuntu`'s `stop` is not authorized without authentication | **not established** | source limb established: verb `stop` reaches the rules; the RP-11 rule returns nothing for it; the defaults are `auth_admin*`, so the result is a challenge, refused without interaction. The limb depends on (b)'s `/etc/polkit-1/rules.d` (MF-3). *(R2)* For the three re-cited `/usr/share` files, no rule names a systemd action, so none returns a result for `stop` (§R2-3); verdict unchanged |

**PO-11 is not established.** Under the design, (d) returns `ACT`/`DEACT` to
design review (§0.2).

---

## 7. PO-20 (a) … (h) — kernel 7.0 (Ubuntu 7.0.0-31), ext4, tmpfs, glibc

Kernel sources: upstream 7.0 with every cited file patched by the Ubuntu
delta. Relevant Ubuntu changes are listed in §15.2.

| Limb | Verdict | Source and reasoning |
|---|---|---|
| (a) `O_TMPFILE` creates an unnamed file; without `O_EXCL` it can be linked by `linkat(AT_FDCWD, "/proc/self/fd/N", dirfd, name, AT_SYMLINK_FOLLOW)`; if the process ends, the host crashes or power fails before the link, the inode is freed and no name remains | **not established** | Established limbs: `vfs_tmpfile` sets `I_LINKABLE` unless `O_EXCL` (`fs/namei.c:4706–4745`); `filename_linkat` accepts `AT_SYMLINK_FOLLOW` and follows the `/proc/self/fd/N` link to the open file's path (`fs/namei.c:5786–5830`; `fs/proc/fd.c:174–190`, Ubuntu-refactored, same semantics); `vfs_link` refuses `i_nlink == 0` only without `I_LINKABLE` (`fs/namei.c:5753`); process end: last `fput` of an `nlink=0` inode frees it. **Ubuntu sets `protected_hardlinks` and `protected_symlinks` to 1 by default** (`fs/namei.c:1199–1200`): `may_linkat` then requires the caller to own the inode or hold `CAP_FOWNER` (`:1312–1370`). Root publishers and the file's creator pass. Crash/power-loss limb: ext4 places an `O_TMPFILE` inode on the orphan list (`fs/ext4/namei.c:2875–2900`), cleared at recovery, which is crash-safe only with a journal. **Whether `/dev/sda1` has a journal is MF-5** |
| (b) `linkat` fails `EEXIST` and never replaces | **established** | `filename_create` → `-EEXIST` for an existing name (`fs/namei.c:4898–4935`) |
| (c) `renameat2(RENAME_NOREPLACE)` works for directories, is atomic, fails `EEXIST`, keeps the inode; glibc exports `renameat2` | **established** | `do_renameat2` flag checks and `-EEXIST` (`fs/namei.c:6085–6125`), `vfs_rename` (`:5912ff`); ext4 `ext4_rename2` and tmpfs `shmem_rename2` accept `RENAME_NOREPLACE` (`fs/ext4/namei.c:4182–4195`; `mm/shmem.c:4048–4060`); a rename moves the dentry, keeping the inode. glibc: `renameat2` exported at `GLIBC_2.28` (`stdio-common/Versions:60–62`); the Linux wrapper passes flags to the system call and returns `EINVAL` on `ENOSYS`, with no non-atomic emulation (`sysdeps/unix/sysv/linux/renameat2.c`); `RENAME_NOREPLACE` = 1 (`libio/stdio.h:174`) |
| (d) `fsync` on a file makes data and metadata durable; `fsync` on an `O_RDONLY` directory descriptor makes its entries durable | **not established** | ext4 files and directories both use `ext4_sync_file` (`fs/ext4/file.c:970`, `fs/ext4/dir.c:691`), which commits the transaction covering the inode's last change (`fs/ext4/fsync.c:109–175`). That guarantee holds for journaled ext4. **MF-5** |
| (e) `st_ino` is stable for a live inode and unique among live objects on a device | **established** | ext4 inode numbers index the inode table; tmpfs mounted `inode64` (HF-15) allocates 64-bit numbers from `sbinfo->next_ino` (`mm/shmem.c:344–406`). Without `inode64`, tmpfs emulates 32-bit wrap (`:365–375`) |
| (f) `flock` on an `O_RDONLY` directory descriptor gives an exclusive advisory lock released when the process ends | **refuted** | The lock is available on any descriptor with `FMODE_READ` or `FMODE_WRITE`, directories included (`fs/locks.c:2198–2230`). It is released when the **last reference to the open file description** is dropped (`__fput` → `locks_remove_file`, `fs/file_table.c:498`; `fs/locks.c:2767`). A forked process, or any holder of a duplicate, keeps it after the locking process ends. Correct form: "released when the last descriptor referring to that open file description is closed, which process exit does when no other process holds one" |
| (g) (a)…(f) on `tmpfs`; `st_ino` unique; contents do not survive a kernel boot, including `kexec`; `fsync` may be a no-op | **established** for named objects | `shmem_tmpfile`, `shmem_rename2` (`mm/shmem.c:5263–5264`), `noop_fsync` (`:5233`). **Precision:** Ubuntu's amd64 config enables `CONFIG_LIVEUPDATE`, `CONFIG_LIVEUPDATE_MEMFD` and `CONFIG_KEXEC_HANDOVER(_ENABLE_DEFAULT)` (`debian.master/config/annotations`). Live Update can carry **unlinked** shmem files (`i_nlink == 0`) across `kexec` on root's request (`mm/memfd_luo.c:530–536`). Named entries in `/run`, such as a linked rule file, cannot be carried |
| (h) in a root-owned `1777` directory, a root-owned entry can be unlinked or renamed only with `CAP_FOWNER`; `mkdirat` fails `EEXIST` for any existing name, including a dangling symlink, and never follows it | **established** | `__check_sticky` (`fs/namei.c:3622–3632`); `filename_create` looks up the last component without following (`:4898–4935`) |

**PO-20 is refuted** (limb (f)); (a) and (d) await MF-5.

---

## 8. PO-21 (a) … (v) — systemd 259.5

"PID 1's environment" in PO-21 (b) and (n) is read in the sense the design uses
for the holder and CP: the block PID 1 assembles for a unit, as opposed to
`sudo`'s. It is **not** TR-7's "PID 1's own environment" (§3). See X-1 (§15.4)
for the consequence.

| Limb | Verdict | Source and precision |
|---|---|---|
| (a) `systemd-run --system` without `--scope` makes a PID-1-supervised service, not ended by session end, `KillUserProcesses=` or terminal hang-up | **established** | `systemd-run` sends `StartTransientUnit` for a `.service` (`src/run/run.c`, service path); logind's session end stops only `session-<id>.scope` (`src/login/logind-session.c:777–780`, `:950ff`); Ubuntu builds `-Ddefault-kill-user-processes=false` (`debian/rules:77`); the service's standard I/O are not a terminal unless `--pty`/`-t` |
| (b) environment = the manager's block plus nothing from the caller unless `--setenv`/`-E`/`Environment=`; argument grammar unaffected by `%`/`$` | **established** | `systemd-run` sends `Environment=` only from `--setenv`/`-E` (`run.c:1574–1590`) or `TERM`/`COLORTERM`/`NO_COLOR` when it allocates or passes a TTY (`:1503–1572`), neither of which the literals use (default `ARG_STDIO_NONE`, `run.c:101`). `--expand-environment` defaults to `yes` (`:79`), so `$` would expand at exec time; the literals contain none |
| (c) `ExecStopPost=` runs after the main process ends for every cause listed | **refuted** | For each listed cause the state machine enters `STOP_POST` and spawns `ExecStopPost=` (`service.c:2224–2250`, `:4441–4460`, `:4580–4600`). But if spawning it fails, the unit goes to `FINAL_SIGTERM` with result `resources` and `ExecStopPost=` never runs (`service.c:2236–2246`). (Condition- and start-pre spawn failures go straight to dead, `service.c:2621`, `:2657`; the holder has neither.) PID 1 failure and power loss are outside any unit guarantee |
| (d) `RuntimeMaxSec=` ends the main process after the bound; does suspended time count? | **established**: not counted | deadline = `ActiveEnterTimestampMonotonic` + `RuntimeMaxSec` (`service.c:678–691`) on `CLOCK_MONOTONIC` (`src/core/unit.c:6697–6730`, `unit_arm_timer`); kernel `CLOCK_MONOTONIC` "stops during suspend" (`Documentation/core-api/timekeeping.rst:16–19`). On expiry: `service_enter_stop(…, timeout)` → `SIGTERM` → after `TimeoutStopSec` `SIGKILL` → stop-post (`service.c:4520–4523`) |
| (e) how `TimeoutStopSec=` bounds stop-post, and expiry | **established** | stop-post is spawned with `timeout_stop_usec` (`service.c:2240`); on expiry the default `TimeoutStopFailureMode=terminate` sends `SIGTERM` to what remains, including `ExecStopPost=` (`FINAL_SIGTERM`), then after another `TimeoutStopSec` `SIGKILL` (`FINAL_SIGKILL`), ending `failed` with result `timeout` (`service.c:4602–4640`; defaults `kill.c:13–16`, `service.h:84`) |
| (f) `OOMScoreAdjust=-1000` excludes the unit's processes from kernel OOM selection | **established** | written in the executor (`exec-invoke.c:5440–5445`); `oom_badness` returns `LONG_MIN` for `OOM_SCORE_ADJ_MIN` (`mm/oom_kill.c:219–225`). User-space `systemd-oomd` is a separate mechanism and not covered |
| (g) transient units exist only in memory and under `/run`; do not survive a kernel boot; survive `daemon-reload` and `daemon-reexec` | **established** | transient files in `/run/systemd/transient` (removed when the unit is freed, `unit.c:669–700`); reload/re-exec serialize and keep the directory (`rm_rf` only without serialization, `manager.c:2040`); `/run` is tmpfs (HF-15; §7 (g)). See (i) for soft-reboot |
| (h) default dependencies order the stop, including `ExecStopPost=`, before `shutdown.target` and before local filesystems are unmounted | **established** | `Requires=`/`After=sysinit.target`, `After=basic.target`, `Before=`/`Conflicts=shutdown.target` (`service.c:760–797`); `basic.target` `RequiresMountsFor=/var /var/tmp` (`units/basic.target:15–22`); `sysinit.target` `After=local-fs.target` (`units/sysinit.target:15`). Stop order is the reverse of start order; `/` itself is never unmounted while units run |
| (i) soft-reboot capability, survival of `/run` and transient units, units stopped first, and every automatic condition | **established** | 259.5 can soft-reboot (`units/soft-reboot.target`, `units/systemd-soft-reboot.service`). `/run` stays mounted and populated (`man/systemd-soft-reboot.service.xml`; `main.c:2035` keeps `/run` across the root switch). Units with default dependencies are stopped first; remaining processes get `SIGTERM` then `SIGKILL` except `SurviveFinalKillSignal=` cgroups (`main.c:1922–1933`). **Transient units:** stopped like others; files of freed units are removed; **units still loaded (for example a `failed` holder) are serialized and the new manager does not wipe `/run/systemd/transient`** because it starts with a serialization (`manager-serialize.c:134–186`; `manager.c:2039–2040`). `set-environment` state is dropped. Automatic conditions: CL-21i, §9 |
| (j) `--on-active=`/`--on-unit-active=` timers with `AccuracySec=1s`; overlap; `systemctl stop` on the timer | **established** | `OnUnitActiveSec` base = `max(last activation of the service, last trigger)` (`timer.c:483–487`); events armed on `CLOCK_MONOTONIC` with the accuracy window (`:540–552`). While the service is active, the timer is `RUNNING` and not re-armed; it re-arms when the service enters `inactive`/`failed`, firing at once if the period has already elapsed (`timer.c:619–660`, `:795–830`). `systemctl stop` on the timer enters `dead` and disables the event sources (`timer.c:710–717`) |
| (k) a failed unit stays loaded with `failed` and its last `InvocationID` until `reset-failed` or next start; each start assigns a new ID; an `inactive` unit may be unloaded | **established** | default `CollectMode=inactive` collects `inactive` only (`unit.h:41`; `unit.c:418–486`); the ID changes only in `unit_acquire_invocation_id` at each start (`unit.c:5472–5487`), a fresh random value |
| (l) `systemctl show -p` does not start, stop or change a unit | **established** for start, stop, jobs, settings and active state. **Precision:** it loads an unloaded unit into memory (`manager.c:3335–3373`), which (s) already anticipates |
| (m) `systemd-run --unit=<name>` fails and creates nothing if that unit is loaded | **established** | `StartTransientUnit` refuses a unit that has a fragment or source path, a job, or is merged: `Unit %s was already loaded or has a fragment file.` (`dbus-manager.c:1054–1056`; `unit.c:5248–5266`). Drop-ins, including dash-prefix ones, do apply to transient units (comment at `unit.c:5251–5257`) |
| (n) `ExecStartPre=+` runs as root, unaffected by `User=`/`NoNewPrivileges=`, with PID 1's block and nothing from the requester; same `INVOCATION_ID` as `ExecStart=`; which settings still apply | **established** | `+` sets `FULLY_PRIVILEGED`, so `needs_sandboxing=false` and `needs_setuid=false` (`exec-invoke.c:5342`, `:5734`): no set*id, no `PR_SET_NO_NEW_PRIVS` (inside the sandboxing block `:6189–6390`), **no `Limit*=`** (`:5757–5768`), no seccomp or namespaces. **Still applied:** `UMask=` (`:5718`), `WorkingDirectory=` (`:6183`), `Standard*=` (`:5409–5428`), the environment block including `USER=ubuntu`, `HOME`, `LOGNAME`, `SHELL` from `User=` (user lookup `:5270–5300` is unconditional). One `InvocationID` per start (`service.c:3026`) is used for all commands of that start |
| (o) `ExecStart=` only after every `ExecStartPre=` exits 0; failure, signal, timeout or a `stop` during start-pre leave it unexecuted; independent of line order | **established** | `START_PRE` advances only on `SERVICE_SUCCESS` and runs the next pre-command only on success (`service.c:4322–4330`, `:4348–4353`); timeout (`:4489–4517`); `stop` in `START_PRE` → `STOP_SIGTERM` (`service.c:3133–3144`); commands are kept in per-type lists, so line order does not matter |
| (p) polkit authorizes `StartUnit` once before enqueueing; removing the rule does not cancel the job; no further polkit decision | **established** | §6.2; job execution contains no polkit call |
| (q) `systemctl start --wait` needs no polkit action after `StartUnit` | **established** | `--wait` uses signal matches and `GetAll` (`src/shared/bus-wait-for-units.c:131`, `:264–349`; `systemctl-start-unit.c:383–430`); `Subscribe` checks SELinux only (`dbus-manager.c:1394–1420`) |
| (r) the applicable start timeout is the manager default | **established** | `service_init` sets `timeout_start_usec = defaults.timeout_start_usec` (`service.c:172`); only `oneshot` without an explicit value gets infinity (`:879–881`); the unit is `Type=exec`. HF-16: `1min 30s` |
| (s) `InactiveEnterTimestampMonotonic` semantics | **refuted** | It is set only on a transition from a **non-inactive** state into `inactive`/`failed`, while not reloading (`unit.c:2741–2753`). A `failed`→`inactive` transition (`reset-failed`) does **not** set it, contrary to "at every transition … into inactive or failed". The value is `now(CLOCK_MONOTONIC)` in µs: **non-decreasing is established; strictly later than every earlier value is not established by any source invariant** (it rests on at least 1 µs elapsing between two such transitions). Established limbs: unchanged while activating, by reads and by a queued start; serialized across reload/re-exec (`unit-serialize.c:95`, `:249`); `0` for a freshly loaded unit; printed as decimal µs (not a `…Timestamp` name, no `USec`, `bus-print-properties.c:19–25`, `:108–126`) |
| (t) two attempts never overlap; joined, active and deactivating cases | **established** | start+start merge (`job.c:408–416`); active → `-EALREADY` (job done, no start-pre); `deactivating` → `-EAGAIN` (job waits) (`unit.c:1922–1950`); `service_start` asserts an inactive/failed state (`service.c:3009–3024`) |
| (u) end state per cause; a stop during start-pre | **established** | non-zero exit, signal not from a stop, timeout, or fork/exec failure → `failed` (`service.c:4116–4130`, `:2621`). **A stop during start-pre ends `failed`** (result `signal`) when the stop's `SIGTERM`/`SIGKILL` terminates CP, because command processes treat signals as unclean (`exit-status.c:139–153`; `service.c:4318–4320`); it ends `inactive` only if CP exits 0 before the signal lands, and `failed` if CP exits non-zero |
| (v) `systemctl show -p` from an `ExecStartPre=+` process during its own start | **established** | PID 1 serves D-Bus from its event loop while the control process runs; state `START_PRE` maps to `activating`; the `InvocationID` was acquired before start-pre (`service.c:3026`); τ unchanged (only set on entering inactive/failed); `ExecMain*` status reset at each start (`service.c:3054–3055`) and set only when the main process is spawned (`execute.c:616`) |

**PO-21 is refuted** (limbs (c) and (s)).

---

## 9. CL-21i — automatic soft-reboot conditions for systemd 259.5

**Result: non-empty.** 259.5 can turn a requested reboot into a soft-reboot
automatically. The Ubuntu patches do not touch the functions below (the
`logind-dbus.c` hunks are confined to `manager_create_session*`).

Mechanism (S):

* `systemctl reboot` (also invoked as `reboot` and `shutdown -r`) without
  `--force` and without `--when=` calls logind's `RebootWithFlags`. It sets
  `SD_LOGIND_SOFT_REBOOT_IF_NEXTROOT_SET_UP` when
  `SYSTEMCTL_SKIP_AUTO_SOFT_REBOOT` is not true **and**
  `path_is_mount_point("/run/nextroot") > 0`
  (`src/systemctl/systemctl-logind.c:94–105`; dispatch
  `systemctl-start-special.c:197–219`).
* logind turns the request into a soft-reboot if that flag is set **and**
  `path_is_os_tree("/run/nextroot") > 0`, that is, `/run/nextroot` exists and
  `etc/os-release` or `usr/lib/os-release` resolves inside it
  (`src/login/logind-dbus.c:2349–2382`; `src/basic/os-util.h:27–30`;
  `os-util.c:93–118`, `:167–186`, `:211–231`).
* Any D-Bus client may pass the flag (bit 3) directly; logind then applies
  only the OS-tree test, not the mount-point test.

| # | Path or condition | Predicate that arms it | Observable by `ubuntu` unprivileged? | How it is disarmed |
|---|---|---|---|---|
| CL-21i-1 | `/run/nextroot` | is a mount point (client-side test in `systemctl`) | **yes**: `/run` is `root:root` `0755` (HF-11); `lstat`/`/proc/self/mountinfo` | `/run/nextroot` **absent** (`lstat` `ENOENT`) |
| CL-21i-2 | `/run/nextroot/etc/os-release`, `/run/nextroot/usr/lib/os-release` (resolved within `/run/nextroot`, `CHASE_AT_RESOLVE_IN_ROOT`) | either resolves (logind-side test) | **yes** if `/run/nextroot` is traversable; otherwise unobservable (fail closed) | `/run/nextroot` absent: `access_nofollow("/run/nextroot")` fails first, so the tree test returns 0 |
| CL-21i-3 | non-path: `SYSTEMCTL_SKIP_AUTO_SOFT_REBOOT` in the environment of the `systemctl` that requests the reboot | unset or not a true boolean | **no** (another actor's environment) | not disarmable for other actors; covered by CL-21i-1 |
| CL-21i-4 | non-path: `SYSTEMD_OS_RELEASE` in systemd-logind's environment (`secure_getenv`) redirects CL-21i-2's file inside `/run/nextroot` | set | **no** | covered by `/run/nextroot` absent |
| CL-21i-5 | non-path: a direct `RebootWithFlags` call with `SD_LOGIND_SOFT_REBOOT_IF_NEXTROOT_SET_UP` | any authorized caller | **no** | covered by `/run/nextroot` absent |

**Single disarm condition (R):** `/run/nextroot` absent, as observed by
`lstat` returning `ENOENT`. It disarms every entry, is observable by `ubuntu`,
and is decided at AP-0 (unprivileged) and AM-0 (root) as R3 §7.2 specifies.
Creating `/run/nextroot` is a root act.

**Outside CL-21i by definition, listed for DF-1 review** (they do not convert
a reboot request): an explicit `systemctl soft-reboot`; a logind key or idle
action configured as `soft-reboot` in `logind.conf(.d)`; a unit
`FailureAction=`/`SuccessAction=`/`StartLimitAction=`/`JobTimeoutAction=` of
`soft-reboot`/`soft-reboot-force` (`src/core/emergency-action.c:24–25`,
`:141–150`). `soft-reboot.target` itself has `JobTimeoutAction=soft-reboot-force`.
Scheduled reboots (`--when=`, `ScheduleShutdown`) and `--force` do not apply
the nextroot test. `systemctl reboot` also converts automatically to **kexec**
when a kexec kernel is loaded (`SYSTEMCTL_SKIP_AUTO_KEXEC`,
`systemctl-logind.c:94–97`); kexec is a kernel boot, covered by PO-21 (c)/(h)
and PO-20 (g).

---

## 10. CPython 3.14.4 — PO-12, AS-8, PT-8

Sources: `Python-3.14.4` with the 45 Ubuntu/Debian patches. Only
`Lib/site.py` (`distutils-install-layout.diff`), `Modules/main.c`
(`min-pyrepl.diff`) and `Lib/_sitebuiltins.py` among start-up files are
patched; `Modules/getpath.py`, `Modules/getpath.c`, `Python/initconfig.c`,
`Python/preconfig.c` and `Python/pylifecycle.c` are not.

### 10.1 What `-I -S` does (S)

| Fact | Source |
|---|---|
| `-I` sets `isolated=1`, then `use_environment=0` in pre-configuration | `Python/preconfig.c:205–206`, `:242–251` |
| `isolated` forces `safe_path=1`, `use_environment=0`, `user_site_directory=0` | `Python/initconfig.c:3498–3502` |
| `-S` sets `site_import=0`; `site` is imported only if `site_import` | `Python/initconfig.c:2986–2987`; `Python/pylifecycle.c:1310` |
| With `safe_path`, `sys.path[0]` is not computed from the script or the working directory (unless the "script" is a zip or directory importer) | `Modules/main.c:646–659` |
| `PYTHON*` variables read through `_Py_GetEnv` honour `use_environment` | `Python/preconfig.c:530–540` |

### 10.2 Inputs the claims do **not** exclude (S)

| Input | When | Source |
|---|---|---|
| **`PYTHONEXECUTABLE`** | always read with `getenv` on POSIX; if set, it becomes `sys.executable`, sets `executable_dir`, moves the `pyvenv.cfg` search to it and its parent, and selects `<value>._pth`, whose contents **replace `sys.path`**. `use_environment` is not tested | `Modules/getpath.c:704–716`, `:937–940`; `Modules/getpath.py:303–324`, `:342–415`, `:457–490` |
| **`__PYVENV_LAUNCHER__`** | as `PYTHONEXECUTABLE`, then unset | same |
| `PATH` | only if `argv[0]` contains no `/` | `getpath.py:283–293`. The design always passes an absolute `argv[0]` |
| `LC_ALL`, and `LC_CTYPE`/`LANG` through `setlocale(LC_CTYPE, "")` | pre-initialization | `Python/pylifecycle.c:193–220`, `:291–310`; `Python/preconfig.c:600–720` |
| `mimalloc_<option>`/`MIMALLOC_<OPTION>` | at process load, by bundled mimalloc's GCC constructor, independent of `-I`. mimalloc is compiled in by default (`configure.ac:5023–5032`; Ubuntu does not disable it) | `Objects/mimalloc/init.c:499–523`, `:680–683`; `Objects/mimalloc/options.c:97–110`, `:505–515`; `Objects/mimalloc/prim/unix/prim.c:709–725` |
| `/proc/sys/vm/overcommit_memory` | mimalloc start-up | `Objects/mimalloc/prim/unix/prim.c:106` |
| files near the executable | `/usr/bin/python3.14._pth`, `/usr/pyvenv.cfg`, `/usr/bin/pyvenv.cfg`, `/usr/bin/pybuilddir.txt`, `/usr/bin/Modules/Setup.local`; prefix landmarks under `/usr/lib/python3.14` | `getpath.py:178–187`, `:342–415`, `:457–520` |

### 10.3 Locale behaviour under `LC_ALL=C` (S)

With a non-empty `LC_ALL`, `_Py_LegacyLocaleDetected(0)` returns 0, so C-locale
coercion is off (`pylifecycle.c:193–205`; `preconfig.c:701–713`). UTF-8 Mode
turns on because `LC_CTYPE` is `C` (`preconfig.c:651–663`), using CPython's own
codec. `_Py_CoerceLegacyLocale` (`pylifecycle.c:291–390`) never runs. CPython
calls `iconv_open` only under `HAVE_NON_UNICODE_WCHAR_T_REPRESENTATION`
(`Python/fileutils.c:33`, `:949–1044`), which `configure.ac:6318–6330` defines
on Oracle Solaris only.

### 10.4 Verdicts

* **PO-12** — "CPython 3.14 `-I -S <script>` reads no `PYTHON*` variable, adds
  neither the working directory nor the script directory to `sys.path`,
  imports no `site`, and locates only files under its root-owned prefix":
  **refuted.** It reads `PYTHONEXECUTABLE` and `__PYVENV_LAUNCHER__` and acts
  on them under `-I`, and through them it can read a `._pth` or `pyvenv.cfg`
  outside the prefix. The `sys.path[0]` and `site` limbs are established.
* **AS-8** (same claim, interpreter path form): **refuted** on the same
  ground.
* **PO-12′, offered for review (not a verdict substitute).** For
  `/usr/bin/python3.14` (`python3.14-minimal` `3.14.4-1ubuntu0.2`, SHA-256
  `be9a2a5e…69fd`) started with absolute `argv[0]` `/usr/bin/python3.14`,
  `-I -S`, a regular-file script and an environment containing neither
  `PYTHONEXECUTABLE` nor `__PYVENV_LAUNCHER__`: no `PYTHON*` variable is read;
  `sys.path[0]` is not prepended; `site` is not imported; the files consulted
  for path calculation are `/usr/bin/python3.14._pth`, `/usr/pyvenv.cfg`,
  `/usr/bin/pyvenv.cfg`, `/usr/bin/pybuilddir.txt`,
  `/usr/bin/Modules/Setup.local` and the landmarks under `/usr/lib/python3.14`;
  and the remaining environment inputs are `LC_ALL`, `LC_CTYPE`/`LANG` and
  `mimalloc_*`/`MIMALLOC_*`. The design's literal `rp11-entry-env/1`
  (`{INVOCATION_ID, LC_ALL=C, PATH=/usr/bin}`) satisfies the environment
  precondition for the **entry** (TR-9). PO-12′ is source-established; binding
  it needs MF-4 (absence and ownership of those files). H-0G's `sys.path` and
  `prefix` are consistent with no `._pth` being honoured, but do not establish
  `pyvenv.cfg` absence.

### 10.5 PT-8

Neither `os.renameat2` nor `os.RENAME_NOREPLACE` exists in 3.14.4: no
occurrence in `Modules/posixmodule.c`, `Modules/clinic/posixmodule.c.h`,
`Lib/os.py` or `Doc/library/os.rst` (which documents only
`rename(src, dst, *, src_dir_fd=None, dst_dir_fd=None)` at line 2750). The
prompt's hypothesis is **refuted**; **the reviewed `ctypes` mechanism is
retained**. Its foundations are §7 (c) (glibc `renameat2`, `RENAME_NOREPLACE`
= 1). Loading `_ctypes` adds its own shared-library closure (for example
`libffi`), which belongs to MF-1.

---

## 11. U-9 / PO-19 — glibc 2.43-2ubuntu2.4 for `/usr/bin/python3.14`

### 11.1 Accepted U-9 wording (verbatim)

> **U-9 — glibc/loader evidence.** Add an explicit numbered,
> version-specific glibc/dynamic-loader proof obligation covering the trusted
> loader inputs relevant to `/usr/bin/python3.14`. The proof must bind to the
> H-0-recorded `libc6` version and the executable's `DT_RUNPATH`/`DT_RPATH`.
> Any version or executable-digest drift requires re-citation before H-1 may
> proceed.

Source: [H-0 and U-9 acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-acceptance-and-u9.md).

### 11.2 PO-19 (a) — loader search inputs (S, derived where marked)

For a non-set-ID start (`__libc_enable_secure` = 0), glibc 2.43 as patched:

1. **Preload:** `/etc/ld.so.preload`, read only if `access(R_OK)` succeeds
   (`elf/rtld.c:1838–1911`); and `LD_PRELOAD` (environment).
2. **For each `DT_NEEDED` name without `/`** (`elf/dl-load.c:1988–2130`): the
   loading object's and the executable's `DT_RPATH`, only if the loading object
   has no `DT_RUNPATH`; `LD_LIBRARY_PATH` (environment); the loading object's
   `DT_RUNPATH`; `/etc/ld.so.cache` (`LD_SO_CACHE` = `SYSCONFDIR
   "/ld.so.cache"`, `sysdeps/generic/dl-cache.h:37–39`; `elf/dl-cache.c:389–394`),
   unless `DF_1_NODEFLIB` excludes default-path results; then the built-in
   directories, unless `DF_1_NODEFLIB`. A name containing `/` is opened
   directly.
3. **Built-in trusted directories (derived):** `default-rpath` =
   `$(slibdir):$(libdir)` plus Debian's `extra_libdir` = `/lib:/usr/lib`
   (`Makeconfig:157–158`, `:660–670`; Debian patch `any/local-ld-multiarch.diff`),
   with `slibdir=/lib/x86_64-linux-gnu`, `libdir=/usr/lib/x86_64-linux-gnu`
   (`debian/rules:75`, `:87–89`), rendered by `elf/gen-trusted-dirs.awk`
   (`elf/Makefile:1576–1585`). Result: `/lib/x86_64-linux-gnu/`,
   `/usr/lib/x86_64-linux-gnu/`, `/lib/`, `/usr/lib/`.
4. **`glibc-hwcaps`:** subdirectories `glibc-hwcaps/x86-64-v4`, `x86-64-v3`,
   `x86-64-v2` (`sysdeps/x86_64/dl-hwcaps-subdirs.c:24`; `elf/dl-hwcaps.h:27–28`),
   selected by CPU (AB-4).
5. Ubuntu/Debian patches touching the loader add no input:
   `ubuntu/local-disable-ld_audit.diff` (secure mode only),
   `any/unsubmitted-ldso-machine-mismatch.diff` (skips foreign-machine ELF),
   `arm/unsubmitted-ldso-multilib.diff` (`#ifdef __arm__`), and
   `git-updates.diff`'s `dl-tunables.c` hunk (`strlen` refactor).

The **source** part of (a) is established. Its **binding** to
`/usr/bin/python3.14` needs that executable's `DT_RUNPATH`, `DT_RPATH`,
`DT_NEEDED`, `DT_FLAGS_1` and `PT_INTERP`, and the same for every object in its
closure, including any `lib-dynload` extension the entry or CP imports
(**MF-1**). **(a): not established.**

### 11.3 PO-19 (b) — `INVOCATION_ID`, `LC_ALL`, `PATH` are not loader or tunable inputs

* `ld.so` examines only environment entries beginning `LD_`
  (`elf/dl-environ.c:22–44`), dispatching on these suffixes: `WARN`, `DEBUG`,
  `AUDIT`, `VERBOSE`, `PRELOAD`, `PROFILE`, `BIND_NOW`, `BIND_NOT`,
  `SHOW_AUXV`, `ORIGIN_PATH`, `LIBRARY_PATH`, `DEBUG_OUTPUT`, `DYNAMIC_WEAK`,
  `PROFILE_OUTPUT`, `TRACE_LOADED_OBJECTS` (`elf/rtld.c:2582–2740`, `:2742–2750`).
* Tunables read only `GLIBC_TUNABLES` and the aliases `MALLOC_CHECK_`,
  `MALLOC_TOP_PAD_`, `MALLOC_PERTURB_`, `MALLOC_MMAP_THRESHOLD_`,
  `MALLOC_TRIM_THRESHOLD_`, `MALLOC_MMAP_MAX_`, `MALLOC_ARENA_MAX`,
  `MALLOC_ARENA_TEST` (`elf/dl-tunables.list:32–65`) and
  `LD_PREFER_MAP_32BIT_EXEC` (`sysdeps/x86_64/64/dl-tunables.list:25`), in
  `__tunables_init` (`elf/dl-tunables.c:293–335`, called from
  `sysdeps/unix/sysv/linux/dl-sysdep.c:110`).

None of `INVOCATION_ID`, `LC_ALL` or `PATH` is among them. `PATH` is used only
by later `exec*p` calls, `LC_ALL` only by `setlocale` (c). **(b): established.**

### 11.4 PO-19 (c) — `LC_ALL=C`, locale archive and `gconv`

* `_nl_find_locale` reads `LC_ALL` first; for `"C"` or `"POSIX"` it returns the
  built-in `_nl_C[category]` before any archive or `LOCPATH` lookup
  (`locale/findlocale.c:101–160`).
* The C locale's `LC_CTYPE` presets its conversion functions to the built-in
  set (`locale/C-ctype.c:544`), so `get_gconv_fcts` never calls
  `__wcsmbs_load_conv` for it (`wcsmbs/wcsmbsload.h:67–73`;
  `wcsmbs/wcsmbsload.c:151–206`).
* `gconv` modules are loaded only through `iconv_open` and the functions built
  on it. Their directory is the compiled `gconvdir` = `$(libdir)/gconv` =
  `/usr/lib/x86_64-linux-gnu/gconv` (derived, `Makeconfig:221–222`) plus
  `GCONV_PATH` (`iconv/gconv_cache.c:56`; `iconv/gconv_conf.c:360–390`).
  CPython does not call `iconv_open` on Linux (§10.3).

**Named `gconv` modules: none.** **(c): established.**

### 11.5 PO-19 (d) — root ownership

HF-09 shows `/etc/ld.so.cache`, `/etc/ld.so.conf`, `/etc/ld.so.conf.d/*` and the
loader's real path root-owned, and `/etc/ld.so.preload` absent. It does not
record the trusted directories, their `glibc-hwcaps` subdirectories, or the
libraries the executable's closure resolves to (**MF-2**). **(d): not
established.**

### 11.6 Binding, drift and re-citation gate

**PO-19 is not established.** Once MF-1 and MF-2 are observed by a separately
authorized slice and reviewed, the citation can be bound to this exact tuple:

| Bound input | Value | Re-citation trigger |
|---|---|---|
| `libc6` | `2.43-2ubuntu2.4` | any version change |
| `python3.14-minimal` | `3.14.4-1ubuntu0.2` | any version change |
| `/usr/bin/python3.14` SHA-256 | `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` | any digest change |
| `DT_RUNPATH`/`DT_RPATH` (and `DT_NEEDED`, `DT_FLAGS_1`, `PT_INTERP`) | **unestablished** (MF-1) | any difference from the reviewed observation |

Under R3 §6.7 and U-9, H-1 P-0, H-2 and AP-0 must find all four equal to the
accepted values; any drift is INVALID RUN followed by re-citation, never
accepted at run time. The same tuple governs PO-12′.

---

## 12. D9-1 — Linux 7.0 (Ubuntu 7.0.0-31) and the PO-17 boundary

The Ubuntu delta touches none of `fs/binfmt_misc.c`, `fs/binfmt_elf.c`,
`fs/exec.c`, `arch/x86/entry/*`, `arch/x86/kernel/traps.c`,
`arch/x86/kernel/signal.c`, `arch/x86/kernel/process_64.c` or
`include/uapi/linux/binfmts.h`.

| Item | Verdict | Source |
|---|---|---|
| **AD-3** — `ET_EXEC` without `PT_INTERP`: segments mapped, argv/envp/auxv copied without interpreting environment strings, start at `e_entry`, no user instruction before | **established** | `load_elf_binary` opens an interpreter only for `PT_INTERP` (`fs/binfmt_elf.c:883–910`); without one, `elf_entry = e_entry` (`:1279–1285`; `ET_EXEC` has `load_bias` 0, `:1067–1074`); strings are copied by `copy_strings` and laid out by `create_elf_tables` (`:165–330`); `START_THREAD(elf_ex, regs, elf_entry, bprm->p)` (`:1380`) |
| **AD-4** — `binfmt_misc` is tried before the ELF handler | **established** | `insert_binfmt` → `list_add` at the head (`fs/exec.c:91–97`; `include/linux/binfmts.h:112–120`; `fs/binfmt_misc.c:1030–1035`); ELF uses `register_binfmt` → tail (`fs/binfmt_elf.c:2133`); handlers are tried in list order (`fs/exec.c:1659`) |
| **AD-6** — at `_start`, `%rsp` is 16-byte aligned and points at `argc`, then argv, NULL, envp, NULL, auxv | **established** (kernel source) | `STACK_ROUND` aligns down to 16 (`fs/binfmt_elf.c:149–152`, `:304`); `argc` written first (`:327`), then the vectors; `start_thread_common` sets `ip`/`sp` (`arch/x86/kernel/process_64.c:530–550`) |
| **AD-8** — with no handler, no system call returns `EINTR` | **refuted** as a general statement; **established** for the closed D2 inventory | Counter-example: `ep_poll` returns `-EINTR` directly when a signal is pending (`fs/eventpoll.c:2001–2002`), and only `-ERESTART*` codes are rewound when no handler runs (`arch/x86/kernel/signal.c:333–365`); a stop/continue therefore surfaces `EINTR`. For `fcntl(F_GETFD)`, `close_range`, `rt_sigaction`, `rt_sigprocmask`, `umask`, `chdir`, `execve`, `write(2)` and `exit_group`: none sleeps interruptibly except `write` on the journal stream socket, which returns `-ERESTARTSYS` (restarted) or a short count, because systemd sets no send timeout on it (`include/net/sock.h:2722–2725`; `net/unix/af_unix.c:2259`; systemd `exec-invoke.c` `connect_logger_as`); `execve`'s killable waits fail only with a fatal signal pending, which ends the process |
| **AD-11** — a synchronous fault with no handler terminates without running user code; ignored or blocked signals are forced to default | **established** | `#UD` → `do_error_trap(…, SIGILL)` (`arch/x86/kernel/traps.c:393–397`, `:480ff`); `#GP` → `force_sig(SIGSEGV)` (`:904–913`); `#PF` → `force_sig_fault(SIGSEGV)` (`arch/x86/mm/fault.c:777–830`); `force_sig_info_to_task` resets an ignored or blocked signal to `SIG_DFL` and unblocks it (`kernel/signal.c:1294–1327`); the default action dumps core and calls `do_group_exit` (`:3008–3035`) during exit-to-user processing (`kernel/entry/common.c:63–64`) before any return to user mode. The Ubuntu `kernel/signal.c` hunk is in `zap_other_threads` (`:1343`) |
| **AD-12** — `syscall` returns to the next instruction; with no handler, `-ERESTART*` re-executes the same `syscall` | **established** | `arch_do_signal_or_restart`: for `-ERESTARTNOHAND`/`-ERESTARTSYS`/`-ERESTARTNOINTR`, `ax = orig_ax; ip -= 2`; for `-ERESTART_RESTARTBLOCK`, `ax = restart_syscall`, `ip -= 2` (same instruction, different number); handlers only on delivery (`arch/x86/kernel/signal.c:333–365`, restart cases `:347–355`; `handle_signal` `:255–280` converts to `EINTR` only when a handler runs); entry/return `arch/x86/entry/entry_64.S` (`%rcx`/`%r11`) |
| unmounted `binfmt_misc` in the initial namespace has no effective registration | **not established** | Entries belong to the per-user-namespace instance (`fs/binfmt_misc.c:182–198`) and are removed only when the superblock shuts down (`bm_evict_inode`, `:660–676`). A mount of the same instance in **another mount namespace** keeps the superblock alive, so absence from `/proc/self/mountinfo` does not prove no registration. The design's own branch applies: treat unmounted as a stop (§4.3.6 step 1) |
| entry-file grammar | **established** | `entry_status` with `VERBOSE_STATUS = 1` (`fs/binfmt_misc.c:41`, `:578–617`): `enabled`/`disabled`; `interpreter <path>`; `flags: <P|O|C|F…>`; then `offset <n>`, `magic <hex>` and optional `mask <hex>`, or `extension .<ext>`. `status` reads `enabled\n` or `disabled\n` (`:856–857`) |

**D9-1 is refuted** (AD-8 as worded). AD-8 is not one of D2 §4.5's LB-2S
withdrawal triggers (those are AD-3, AD-4, AD-11, AD-12 and PO-14, each
established here). Returned for restatement (§15.3).

### 12.9 PO-17 / OH-S4p boundary

**OH-S2 establishes these source-bound PO-17 premises** for kernel
7.0.0-31:

1. Matching order: enabled `binfmt_misc` entries are tried before the ELF
   handler (AD-4).
2. Global gate: `misc->enabled` (`fs/binfmt_misc.c:211`), per-entry `Enabled`
   bit (`:101–103`).
3. Magic entries compare `size` bytes of `bprm->buf` at `offset`, with an
   optional mask (`:112–124`). `bprm->buf` is the first `BINPRM_BUF_SIZE` =
   256 bytes, zero-filled before the read (`fs/exec.c:1594–1603`;
   `include/uapi/linux/binfmts.h:19`). Registration requires `offset + size ≤
   256` (`fs/binfmt_misc.c:467–468`). The design's fail-closed rule for an
   image shorter than `offset + k` is stricter than the kernel and stays valid.
4. **Extension entries compare the text after the last `.` in
   `bprm->interp`, the full path string**, not the basename
   (`fs/binfmt_misc.c:94–110`). `bprm->interp` is the path passed to `execve`
   (`fs/exec.c:1405–1440`). Ubuntu's systemd is built without `fexecve`
   (`meson_options.txt:541–542`; `debian/rules` does not set it), so the
   executor calls `execve(<resolved executable path>)`
   (`src/shared/exec-util.c:513–545`). **This contradicts §4.3.6 step 4
   type E**, which tests the basename (§15.3).
5. Entry grammar as above.
6. The unmounted case is not citable (above); unmounted ⇒ stop.
7. System services run in the initial user namespace unless
   `PrivateUsers=`, so the initial instance applies (`load_binfmt_misc`).

**OH-S4p and the later gated slices must supply:** the new launcher image's
bytes and SHA-256 (at least its first 256 bytes for matching); its exact
installed path string, checked for any `.` over the whole path; the HF-14
entries re-observed at H-1 P-0, V-1 and H-2; and the mechanical evaluation of
every entry against that image under rules 2–4. R5's `python3.14` entry
(`offset 0`, magic `2b0e0d0a`, no mask) is an H-0 fact; whether it matches the
new image is a byte-level check that OH-S2 does not make. **PO-17 has not been
evaluated against any launcher image.**

---

## 13. Traceability

| Obligation | Primary sources (Ubuntu trees) | H-0 inputs bound | Verdict |
|---|---|---|---|
| PO-14 | systemd `execute.c`, `executor.c`, `exec-invoke.c`, `process-util.c`, `build-path.c`, `main.c`, `manager.c`, `dbus-manager.c`, `systemd-system.conf.xml` | A-4 (`259.5-0ubuntu3.4`); HF-05 | established |
| AD-7 | `unit.c`, `sd-id128.c`, `hexdecoct.c`, `execute-serialize.c`, `exec-invoke.c` | A-4 | established |
| PO-15 | `dbus-*.c` vtables, `bus-objects.c`, `systemctl-show.c`, `bus-print-properties.c`, `dropin.c`, `unit-file.c`, `unit.c`, `exec-util.c`, `dbus-execute.c` | A-4; HF-13 (c118); HF-16 (c144) | refuted (d) |
| PO-8 S-1…S-10 | `exec-invoke.c`, `service.c`, `manager.c`, `main.c`, `env-util.c`, `load-fragment-gperf.gperf.in`, policy file, `systemctl-start-unit.c`, `systemctl-util.c`; kernel `commoncap.c` | A-4 | established |
| PO-11 (b)…(g) | polkit `polkitbackendduktapeauthority.c`, `polkitbackendcommon.c`, `polkitbackendinteractiveauthority.c`, `pkcheck.c`, `50-default.rules.in`, `debian/49-ubuntu-admin.rules`; systemd `dbus-util.c`, `dbus-unit.c`, policy file, rule files; *(R2)* bolt `0.9.10-1`, fwupd `2.1.1-1ubuntu3.1`, packagekit `1.3.4-3ubuntu1.2` rule sources and build/packaging files, re-retrieved under the R2 authority (§R2-3, Appendix E) | A-5 (`127-2ubuntu1.1`); HF-03; HF-12 (c106–c116) | not established |
| PO-20 (a)…(h) | kernel `fs/namei.c`, `fs/ext4/{namei,fsync,file,dir}.c`, `mm/shmem.c`, `fs/locks.c`, `fs/file_table.c`, `fs/proc/fd.c`, `mm/memfd_luo.c`, Ubuntu config annotations; glibc `renameat2.c`, `stdio-common/Versions` | A-3; A-6; HF-11; HF-15 (A-10, `/run` `inode64`) | refuted (f) |
| PO-21 (a)…(v) | systemd `service.c`, `unit.c`, `timer.c`, `job.c`, `run.c`, `dbus-manager.c`, `manager.c`, `main.c`, `manager-serialize.c`, `unit-serialize.c`, `logind-session.c`, units; kernel `oom_kill.c`, timekeeping doc | A-4; HF-16; HF-20a | refuted (c), (s) |
| CL-21i | systemd `systemctl-logind.c`, `systemctl-start-special.c`, `logind-dbus.c`, `os-util.[ch]`, `emergency-action.c`, soft-reboot units and manual | A-4; HF-11 (`/run`); HF-20a | established (non-empty) |
| PO-12, AS-8 | CPython `getpath.py`, `getpath.c`, `initconfig.c`, `preconfig.c`, `pylifecycle.c`, `main.c`, mimalloc sources, `configure.ac` | A-7; A-8; H-0G c021, c022 | refuted |
| PT-8 | CPython `posixmodule.c`, clinic header, `os.py`, `os.rst`; glibc `renameat2` | A-7; A-6 | refuted (ctypes retained) |
| PO-19 (U-9) | glibc `rtld.c`, `dl-environ.c`, `dl-load.c`, `dl-cache.[ch]`, `dl-hwcaps*`, `dl-tunables.{c,list}`, `findlocale.c`, `C-ctype.c`, `wcsmbsload.[ch]`, `gconv_*.c`, `Makeconfig`, `elf/Makefile`, `debian/rules`, Debian/Ubuntu patches | A-6; A-7; A-8; HF-09 (c098–c102); **MF-1, MF-2** | not established |
| D9-1 | kernel `fs/binfmt_elf.c`, `fs/binfmt_misc.c`, `fs/exec.c`, `include/{linux,uapi/linux}/binfmts.h`, `arch/x86/kernel/{process_64,signal,traps}.c`, `arch/x86/mm/fault.c`, `kernel/signal.c`, `kernel/entry/common.c`, `fs/eventpoll.c`, `net/unix/af_unix.c`, `include/net/sock.h` | A-3; HF-04; HF-14 | refuted (AD-8) |
| PO-17 boundary | as D9-1, plus systemd `exec-util.c`, `meson_options.txt` | HF-14 | premises only; not evaluated (§12.9) |

---

## 14. Fact separation

### 14.1 Source facts (S)

Every row above tagged with a file and line is a source fact of the stated
Ubuntu tree. Derived build-configuration facts are those marked *derived*
(polkit directories, glibc built-in directories and `gconvdir`).
*(R2)* Also derived: the three installed rule byte streams of §R2-3, each
reproduced from its source by the stated build or packaging step and equal to
its R5 digest.

### 14.2 Durable H-0 facts used (H)

Only the inputs in §1.1, read from the accepted durable records. No retained
evidence path or host was accessed.

### 14.3 Mechanical facts still missing (M)

| ID | Fact | Needed by | Proposed observing slice (each needs its own authority) |
|---|---|---|---|
| MF-1 | `/usr/bin/python3.14` `DT_RUNPATH`, `DT_RPATH`, `DT_NEEDED`, `DT_FLAGS_1`, `PT_INTERP`; the same for each object in its closure, including every `lib-dynload` extension the entry, CP and the H-1 tool import (for example `_ctypes` → `libffi`) | PO-19 (a), U-9 binding | a read-only H-0 supplement or H-1 P-0, after OH-S4 fixes the import closure |
| MF-2 | type, owner, mode of `/lib`, `/lib/x86_64-linux-gnu`, `/usr/lib`, `/usr/lib/x86_64-linux-gnu`, their `glibc-hwcaps/x86-64-v{2,3,4}`, and each library MF-1 resolves to | PO-19 (d) | same as MF-1 |
| MF-3 | privileged read-only inventory of `/etc/polkit-1/rules.d` (names, types, owners, modes, SHA-256) | PO-11 (b), (g) | H-1 P-0p (extend beyond the RP-11 basename) or a separate privileged read-only slice |
| MF-4 | absence (or root ownership) of `/usr/bin/python3.14._pth`, `/usr/pyvenv.cfg`, `/usr/bin/pyvenv.cfg`, `/usr/bin/pybuilddir.txt`, `/usr/bin/Modules/Setup.local`; ownership of `/usr/lib/python3.14` | PO-12′ | read-only H-0 supplement or H-1 P-0 |
| MF-5 | whether the ext4 filesystem on `/dev/sda1` has a journal (`has_journal`) and its data mode | PO-20 (a) crash limb, (d) | read-only, unprivileged where possible |
| MF-6 | run-time `fs.protected_hardlinks`/`fs.protected_symlinks` | PO-20 (a), only for a non-owner publisher | read-only |
| MF-7 | `/run/nextroot` absent | CL-21i | AP-0 and AM-0 (already specified by R3 §7.2 as HF-20b's replacement) |
| MF-8 | the dash-prefix drop-in directories (`rp11-.service.d`, `rp11-capture-.service.d`, `rp11-capture-pass-.service.d`) in all 12 unit paths | HF-13 completeness | covered mechanically at H-1 by `DropInPaths` empty; recorded so HF-13 is not read as complete |

### 14.4 Reasoned conclusions (R)

The conclusions in §3.1, §4.3, §6.4's "design fallback" notes, §9's single
disarm condition, §10.4's PO-12′ and §12.9's boundary are reasoned from the
cited S and H facts. Each states its reasoning where it appears.

---

## 15. Contradictions, patch uncertainty and items returned to design review

### 15.1 Patch uncertainty

None is unresolved for the cited functions. Every relevant Ubuntu patch was
read (§3.1 P14-6, §6.3, §10, §11.2 (5), §12). The kernel delta also carries
upstream 7.0.1 … 7.0.14 stable changes; every cited kernel file was read in its
patched form.

### 15.2 Relevant Ubuntu changes found

| Package | Change | Effect on this record |
|---|---|---|
| systemd | `lp2077538` adds `XDG_SESSION_EXTRA_DEVICE_ACCESS` to the user manager's unset list | none for PO-14 |
| glibc | `local-disable-ld_audit`, `unsubmitted-ldso-machine-mismatch`, arm multilib, `git-updates` tunables refactor | no new loader input (§11.2) |
| CPython | `distutils-install-layout` (`site.py`), `min-pyrepl` (`main.c`), `min-pyrepl-sitebuiltins` | not on the `-I -S` script path |
| polkit | two `polkitagenthelperprivate.c` CVE fixes | none |
| kernel | `protected_hardlinks`/`protected_symlinks` default 1 (`fs/namei.c:1199–1200`) | PO-20 (a) precision |
| kernel | `proc_fd_link` refactor (`fs/proc/fd.c`) | semantics unchanged |
| kernel config | `CONFIG_LIVEUPDATE(_MEMFD)`, `CONFIG_KEXEC_HANDOVER(_ENABLE_DEFAULT)` = y on amd64 | PO-20 (g) precision |

### 15.3 Contradictions with accepted texts (proposed corrections; nothing edited)

| # | Accepted text | Source finding | Proposed treatment |
|---|---|---|---|
| C-1 | C11 §4.4.3.2 E-9: PID 1's environment set by kernel and initrd | also `ManagerEnvironment=` and `SYSTEMD_EXECUTOR_PATH` selection (PR-14a, PR-14b) | dated C11 amendment note |
| C-2 | design §4.3.3: `NeedDaemonReload=no` with the fragment digest proves the E-set empty | PO-15 (d) refuted | restate as an R-10 trust assumption, or check E-set emptiness without recording values |
| C-3 | §4.3.3: `UnsetEnvironment` "names only" | may hold `NAME=VALUE` | move to E, or record emptiness only |
| C-4 | §4.3.3 V list | 109 run-time-varying visible names outside V/E (Appendix C.2) | reviewer classifies; this record proposes a split |
| C-5 | §4.2.5-R4 (h): flag "in the form the cited version prints it" | `+` visible only in `ExecStartPreEx` as `flags=privileged` | normalize from `ExecStartPreEx` |
| C-6 | §4.3.6 step 4 type E: basename | kernel matches over the full `bprm->interp` path | test the full path |
| C-7 | §4.3.6 step 1: unmounted ⇒ holds if D9-1 cites it | not citable | apply the design's "unmounted is a stop" branch |
| C-8 | D2 AD-8 (general) | refuted; holds for the closed inventory | restate AD-8 over the inventory |
| C-9 | PO-20 (f) "released when the process ends" | release at last reference to the open file description | restate; implementations must not share the lock descriptor with longer-lived processes |
| C-10 | PO-21 (c) "for every cause" | skipped if PID 1 cannot spawn it | restate; decide whether the backstop retry closes it |
| C-11 | PO-21 (s) "at every transition into inactive or failed"; "later than every earlier value" | not on `failed`→`inactive`; strictness not a source invariant | restate; decide whether SB-2 needs strictness |
| C-12 | PO-12/AS-8 | `PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__` retained under `-I` | Route 3 review per the prompt; PO-12′ offered |
| C-13 | HF-13 drop-in collision set | omits dash-prefix directories | note on HF-13 (MF-8) |
| C-14 | PO-11 (e) design expectation that an unprivileged `--detail` check "would report not authorized" | it reports an error (127) | wording only; PK runs as root anyway |

### 15.4 Cross-cutting finding for review

* **X-1 — root Python processes run under the open manager block.** CP
  (`ExecStartPre=+`), the holder, its `ExecStopPost=` and the backstop are
  `/usr/bin/python3.14 -I -S` processes started by PID 1 with the unit block
  (S-1 (a) … (f)), not with a literal environment. Their dynamic loader
  consumes `LD_*` and the tunables from that block (§11.3), and CPython consumes
  `PYTHONEXECUTABLE`/`__PYVENV_LAUNCHER__` and `MIMALLOC_*` from it (§10.2).
  Manager-global sources (E-3 … E-7) are root-controlled or need polkit
  `set-environment` authorization (§5 S-7). C11 classes this ambient manager
  state as T-A for the entry. PO-19 and PO-12′ as framed cover only the
  entry's literal environment. Whether the activation design accepts this
  under OH-D-6/R-10 or needs these processes to start from a literal
  environment is a design decision, not a citation.

### 15.5 Items returned to design review

1. Activation design: PO-20 (f), PO-21 (c), PO-21 (s); PO-11 (d) (no bound).
2. Route 1 → Route 3: PO-12 (and AS-8).
3. Restatements: PO-15 (d), AD-8, PO-17 type E, and C-1 … C-14.

---

## 16. Drift and re-citation gates

| Bound version or digest | Value | Applies to |
|---|---|---|
| kernel | `7.0.0-31-generic` (Ubuntu `7.0.0-31.31`, upstream stable `7.0.14`) | D9-1, PO-20, PO-21 (d), (f) |
| systemd | `259.5-0ubuntu3.4` | PO-14, AD-7, PO-15, PO-8, PO-21, CL-21i, PO-11 (systemd parts) |
| polkitd | `127-2ubuntu1.1` | PO-11 |
| libc6 | `2.43-2ubuntu2.4` | PO-19, PO-20 (c) |
| python3.14-minimal | `3.14.4-1ubuntu0.2` | PO-12′, AS-8, PT-8 |
| `/usr/bin/python3.14` | SHA-256 `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` | PO-19, PO-12′ |
| dynamic section | **unestablished** (MF-1) | PO-19 |
| `/usr/share/polkit-1/rules.d` | the nine digests of R5 c108–c116 (*(R2)* c113–c115 bound to the R2 derivation, §R2-3) | PO-11 (b), (g) |

Any change to a row makes the dependent citation stale. H-1 P-0, H-2 and AP-0
must compare the observed values with these before relying on any verdict.
`unattended-upgrades` is active on the host (HF-17), so drift is expected
unless separately controlled; a package hold is not authorized (R3 §6.7).

---

## Appendix A — systemd 259.5 service-unit properties (visible to `systemctl show`)

Columns: *vtable flags* as declared (`none` = run-time-varying without change
signal); *Source* in the Ubuntu tree; *§4.3.3 class* is the mechanical
application of the design's rules (V volatile, E environment-bearing, Q
queried); *Run-time varying* is `yes` when the entry is not `PROPERTY_CONST`.
Interfaces: `Unit` = `org.freedesktop.systemd1.Unit`, `Service` =
`org.freedesktop.systemd1.Service`.

| # | Property | Interface | vtable flags | Source (Ubuntu tree) | §4.3.3 class | Run-time varying |
|---:|---|---|---|---|---|---|
| 1 | `AccessSELinuxContext` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:936` | Q | no |
| 2 | `ActivationDetails` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:995` | Q | yes |
| 3 | `ActiveEnterTimestamp` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:948` | V | yes |
| 4 | `ActiveEnterTimestampMonotonic` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:948` | V | yes |
| 5 | `ActiveExitTimestamp` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:949` | V | yes |
| 6 | `ActiveExitTimestampMonotonic` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:949` | V | yes |
| 7 | `ActiveState` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:938` | V | yes |
| 8 | `After` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:919` | Q | no |
| 9 | `AllowIsolate` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:962` | Q | no |
| 10 | `AllowedCPUs` | Service | none | `src/core/dbus-cgroup.c:384` | Q | yes |
| 11 | `AllowedMemoryNodes` | Service | none | `src/core/dbus-cgroup.c:386` | Q | yes |
| 12 | `AmbientCapabilities` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1313` | Q | no |
| 13 | `AppArmorProfile` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1355` | Q | no |
| 14 | `AssertResult` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:976` | Q | yes |
| 15 | `AssertTimestamp` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:978` | V | yes |
| 16 | `AssertTimestampMonotonic` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:978` | V | yes |
| 17 | `Asserts` | Unit | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-unit.c:980` | Q | yes |
| 18 | `BPFDelegateAttachments` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1408` | Q | no |
| 19 | `BPFDelegateCommands` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1405` | Q | no |
| 20 | `BPFDelegateMaps` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1406` | Q | no |
| 21 | `BPFDelegatePrograms` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1407` | Q | no |
| 22 | `BPFProgram` | Service | none | `src/core/dbus-cgroup.c:428` | Q | yes |
| 23 | `Before` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:918` | Q | no |
| 24 | `BindLogSockets` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1398` | Q | no |
| 25 | `BindPaths` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1394` | Q | no |
| 26 | `BindReadOnlyPaths` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1395` | Q | no |
| 27 | `BindsTo` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:907` | Q | no |
| 28 | `BoundBy` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:913` | Q | no |
| 29 | `BusName` | Service | PROPERTY_CONST | `src/core/dbus-service.c:354` | Q | no |
| 30 | `CPUAffinity` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1280` | Q | no |
| 31 | `CPUAffinityFromNUMA` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1281` | Q | no |
| 32 | `CPUQuotaPerSecUSec` | Service | none | `src/core/dbus-cgroup.c:382` | Q | yes |
| 33 | `CPUQuotaPeriodUSec` | Service | none | `src/core/dbus-cgroup.c:383` | Q | yes |
| 34 | `CPUSchedulingPolicy` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1278` | Q | no |
| 35 | `CPUSchedulingPriority` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1279` | Q | no |
| 36 | `CPUSchedulingResetOnFork` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1285` | Q | no |
| 37 | `CPUUsageNSec` | Service | none | `src/core/dbus-unit.c:1747` | V | yes |
| 38 | `CPUWeight` | Service | none | `src/core/dbus-cgroup.c:380` | Q | yes |
| 39 | `CacheDirectory` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1379` | Q | no |
| 40 | `CacheDirectoryAccounting` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1377` | Q | no |
| 41 | `CacheDirectoryMode` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1376` | Q | no |
| 42 | `CacheDirectoryQuota` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1378` | Q | no |
| 43 | `CacheDirectoryQuotaUsage` | Service | none | `src/core/dbus-execute.c:1475` | Q | yes |
| 44 | `CacheDirectorySymlink` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1375` | Q | no |
| 45 | `CanClean` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:955` | Q | no |
| 46 | `CanFreeze` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:956` | Q | no |
| 47 | `CanIsolate` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:954` | Q | no |
| 48 | `CanLiveMount` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:957` | Q | no |
| 49 | `CanReload` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:953` | Q | no |
| 50 | `CanStart` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:951` | Q | no |
| 51 | `CanStop` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:952` | Q | no |
| 52 | `CapabilityBoundingSet` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1312` | Q | no |
| 53 | `CleanResult` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:364` | Q | yes |
| 54 | `CollectMode` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:993` | Q | no |
| 55 | `ConditionResult` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:975` | Q | yes |
| 56 | `ConditionTimestamp` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:977` | V | yes |
| 57 | `ConditionTimestampMonotonic` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:977` | V | yes |
| 58 | `Conditions` | Unit | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-unit.c:979` | Q | yes |
| 59 | `ConfigurationDirectory` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1386` | Q | no |
| 60 | `ConfigurationDirectoryMode` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1385` | Q | no |
| 61 | `ConflictedBy` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:917` | Q | no |
| 62 | `Conflicts` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:916` | Q | no |
| 63 | `ConsistsOf` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:915` | Q | no |
| 64 | `ControlGroup` | Service | none | `src/core/dbus-unit.c:1737` | V | yes |
| 65 | `ControlGroupId` | Service | none | `src/core/dbus-unit.c:1738` | V | yes |
| 66 | `ControlPID` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:353` | V | yes |
| 67 | `CoredumpFilter` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1274` | Q | no |
| 68 | `CoredumpReceive` | Service | none | `src/core/dbus-cgroup.c:435` | Q | yes |
| 69 | `DebugInvocation` | Unit | none | `src/core/dbus-unit.c:996` | Q | yes |
| 70 | `DefaultDependencies` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:963` | Q | no |
| 71 | `DefaultMemoryLow` | Service | none | `src/core/dbus-cgroup.c:398` | Q | yes |
| 72 | `DefaultMemoryMin` | Service | none | `src/core/dbus-cgroup.c:400` | Q | yes |
| 73 | `DefaultStartupMemoryLow` | Service | none | `src/core/dbus-cgroup.c:399` | Q | yes |
| 74 | `Delegate` | Service | none | `src/core/dbus-cgroup.c:377` | Q | yes |
| 75 | `DelegateControllers` | Service | none | `src/core/dbus-cgroup.c:378` | Q | yes |
| 76 | `DelegateNamespaces` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1392` | Q | no |
| 77 | `DelegateSubgroup` | Service | none | `src/core/dbus-cgroup.c:379` | Q | yes |
| 78 | `Description` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:935` | Q | no |
| 79 | `DeviceAllow` | Service | none | `src/core/dbus-cgroup.c:414` | Q | yes |
| 80 | `DevicePolicy` | Service | none | `src/core/dbus-cgroup.c:413` | Q | yes |
| 81 | `DisableControllers` | Service | none | `src/core/dbus-cgroup.c:422` | Q | yes |
| 82 | `Documentation` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:934` | Q | no |
| 83 | `DropInPaths` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:943` | Q | no |
| 84 | `DynamicUser` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1316` | Q | no |
| 85 | `EffectiveCPUs` | Service | none | `src/core/dbus-unit.c:1748` | V | yes |
| 86 | `EffectiveMemoryHigh` | Service | none | `src/core/dbus-unit.c:1746` | V | yes |
| 87 | `EffectiveMemoryMax` | Service | none | `src/core/dbus-unit.c:1745` | V | yes |
| 88 | `EffectiveMemoryNodes` | Service | none | `src/core/dbus-unit.c:1749` | V | yes |
| 89 | `EffectiveTasksMax` | Service | none | `src/core/dbus-unit.c:1751` | V | yes |
| 90 | `Environment` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1223` | E | no |
| 91 | `EnvironmentFiles` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1224` | Q | no |
| 92 | `ExecCondition` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:377` | Q | yes |
| 93 | `ExecConditionEx` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:378` | Q | yes |
| 94 | `ExecMainCode` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 95 | `ExecMainExitTimestamp` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 96 | `ExecMainExitTimestampMonotonic` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 97 | `ExecMainHandoffTimestamp` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 98 | `ExecMainHandoffTimestampMonotonic` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 99 | `ExecMainPID` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 100 | `ExecMainStartTimestamp` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 101 | `ExecMainStartTimestampMonotonic` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 102 | `ExecMainStatus` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:376` | V | yes |
| 103 | `ExecPaths` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1330` | Q | no |
| 104 | `ExecReload` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:385` | Q | yes |
| 105 | `ExecReloadEx` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:386` | Q | yes |
| 106 | `ExecReloadPost` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:387` | Q | yes |
| 107 | `ExecReloadPostEx` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:388` | Q | yes |
| 108 | `ExecSearchPath` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1332` | Q | no |
| 109 | `ExecStart` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:381` | Q | yes |
| 110 | `ExecStartEx` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:382` | Q | yes |
| 111 | `ExecStartPost` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:383` | Q | yes |
| 112 | `ExecStartPostEx` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:384` | Q | yes |
| 113 | `ExecStartPre` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:379` | Q | yes |
| 114 | `ExecStartPreEx` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:380` | Q | yes |
| 115 | `ExecStop` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:389` | Q | yes |
| 116 | `ExecStopEx` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:390` | Q | yes |
| 117 | `ExecStopPost` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:391` | Q | yes |
| 118 | `ExecStopPostEx` | Service | PROPERTY_EMITS_INVALIDATION | `src/core/dbus-service.c:392` | Q | yes |
| 119 | `ExitType` | Service | PROPERTY_CONST | `src/core/dbus-service.c:327` | Q | no |
| 120 | `ExtensionDirectories` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1270` | Q | no |
| 121 | `ExtensionImagePolicy` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1415` | Q | no |
| 122 | `ExtensionImages` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1271` | Q | no |
| 123 | `ExtraFileDescriptorNames` | Service | PROPERTY_CONST | `src/core/dbus-service.c:373` | Q | no |
| 124 | `FailureAction` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:987` | Q | no |
| 125 | `FailureActionExitStatus` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:988` | Q | no |
| 126 | `FileDescriptorStoreMax` | Service | PROPERTY_CONST | `src/core/dbus-service.c:355` | Q | no |
| 127 | `FileDescriptorStorePreserve` | Service | none | `src/core/dbus-service.c:357` | Q | yes |
| 128 | `FinalKillSignal` | Service | PROPERTY_CONST | `src/core/dbus-kill.c:32` | Q | no |
| 129 | `Following` | Unit | none | `src/core/dbus-unit.c:903` | Q | yes |
| 130 | `FragmentPath` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:941` | Q | no |
| 131 | `FreezerState` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:939` | Q | yes |
| 132 | `GID` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:369` | Q | yes |
| 133 | `Group` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1315` | Q | no |
| 134 | `GuessMainPID` | Service | PROPERTY_CONST | `src/core/dbus-service.c:348` | Q | no |
| 135 | `IOAccounting` | Service | none | `src/core/dbus-cgroup.c:388` | Q | yes |
| 136 | `IODeviceLatencyTargetUSec` | Service | none | `src/core/dbus-cgroup.c:396` | Q | yes |
| 137 | `IODeviceWeight` | Service | none | `src/core/dbus-cgroup.c:391` | Q | yes |
| 138 | `IOReadBandwidthMax` | Service | none | `src/core/dbus-cgroup.c:392` | Q | yes |
| 139 | `IOReadBytes` | Service | none | `src/core/dbus-unit.c:1756` | V | yes |
| 140 | `IOReadIOPSMax` | Service | none | `src/core/dbus-cgroup.c:394` | Q | yes |
| 141 | `IOReadOperations` | Service | none | `src/core/dbus-unit.c:1757` | V | yes |
| 142 | `IOSchedulingClass` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1276` | Q | no |
| 143 | `IOSchedulingPriority` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1277` | Q | no |
| 144 | `IOWeight` | Service | none | `src/core/dbus-cgroup.c:389` | Q | yes |
| 145 | `IOWriteBandwidthMax` | Service | none | `src/core/dbus-cgroup.c:393` | Q | yes |
| 146 | `IOWriteBytes` | Service | none | `src/core/dbus-unit.c:1758` | V | yes |
| 147 | `IOWriteIOPSMax` | Service | none | `src/core/dbus-cgroup.c:395` | Q | yes |
| 148 | `IOWriteOperations` | Service | none | `src/core/dbus-unit.c:1759` | V | yes |
| 149 | `IPAccounting` | Service | none | `src/core/dbus-cgroup.c:417` | Q | yes |
| 150 | `IPAddressAllow` | Service | none | `src/core/dbus-cgroup.c:418` | Q | yes |
| 151 | `IPAddressDeny` | Service | none | `src/core/dbus-cgroup.c:419` | Q | yes |
| 152 | `IPCNamespacePath` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1412` | Q | no |
| 153 | `IPEgressBytes` | Service | none | `src/core/dbus-unit.c:1754` | V | yes |
| 154 | `IPEgressFilterPath` | Service | none | `src/core/dbus-cgroup.c:421` | Q | yes |
| 155 | `IPEgressPackets` | Service | none | `src/core/dbus-unit.c:1755` | V | yes |
| 156 | `IPIngressBytes` | Service | none | `src/core/dbus-unit.c:1752` | V | yes |
| 157 | `IPIngressFilterPath` | Service | none | `src/core/dbus-cgroup.c:420` | Q | yes |
| 158 | `IPIngressPackets` | Service | none | `src/core/dbus-unit.c:1753` | V | yes |
| 159 | `Id` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:901` | Q | no |
| 160 | `IgnoreOnIsolate` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:968` | Q | no |
| 161 | `IgnoreSIGPIPE` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1357` | Q | no |
| 162 | `ImportCredential` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1323` | Q | no |
| 163 | `ImportCredentialEx` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1324` | Q | no |
| 164 | `InaccessiblePaths` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1329` | Q | no |
| 165 | `InactiveEnterTimestamp` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:950` | V | yes |
| 166 | `InactiveEnterTimestampMonotonic` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:950` | V | yes |
| 167 | `InactiveExitTimestamp` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:947` | V | yes |
| 168 | `InactiveExitTimestampMonotonic` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:947` | V | yes |
| 169 | `InvocationID` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:992` | V | yes |
| 170 | `Job` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:958` | Q | yes |
| 171 | `JobRunningTimeoutUSec` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:972` | Q | no |
| 172 | `JobTimeoutAction` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:973` | Q | no |
| 173 | `JobTimeoutRebootArgument` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:974` | Q | no |
| 174 | `JobTimeoutUSec` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:971` | Q | no |
| 175 | `JoinsNamespaceOf` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:930` | Q | no |
| 176 | `KeyringMode` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1399` | Q | no |
| 177 | `KillMode` | Service | PROPERTY_CONST | `src/core/dbus-kill.c:29` | Q | no |
| 178 | `KillSignal` | Service | PROPERTY_CONST | `src/core/dbus-kill.c:30` | Q | no |
| 179 | `LimitAS` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1242` | Q | no |
| 180 | `LimitASSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1243` | Q | no |
| 181 | `LimitCORE` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1236` | Q | no |
| 182 | `LimitCORESoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1237` | Q | no |
| 183 | `LimitCPU` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1228` | Q | no |
| 184 | `LimitCPUSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1229` | Q | no |
| 185 | `LimitDATA` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1232` | Q | no |
| 186 | `LimitDATASoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1233` | Q | no |
| 187 | `LimitFSIZE` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1230` | Q | no |
| 188 | `LimitFSIZESoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1231` | Q | no |
| 189 | `LimitLOCKS` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1248` | Q | no |
| 190 | `LimitLOCKSSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1249` | Q | no |
| 191 | `LimitMEMLOCK` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1246` | Q | no |
| 192 | `LimitMEMLOCKSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1247` | Q | no |
| 193 | `LimitMSGQUEUE` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1252` | Q | no |
| 194 | `LimitMSGQUEUESoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1253` | Q | no |
| 195 | `LimitNICE` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1254` | Q | no |
| 196 | `LimitNICESoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1255` | Q | no |
| 197 | `LimitNOFILE` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1240` | Q | no |
| 198 | `LimitNOFILESoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1241` | Q | no |
| 199 | `LimitNPROC` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1244` | Q | no |
| 200 | `LimitNPROCSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1245` | Q | no |
| 201 | `LimitRSS` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1238` | Q | no |
| 202 | `LimitRSSSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1239` | Q | no |
| 203 | `LimitRTPRIO` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1256` | Q | no |
| 204 | `LimitRTPRIOSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1257` | Q | no |
| 205 | `LimitRTTIME` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1258` | Q | no |
| 206 | `LimitRTTIMESoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1259` | Q | no |
| 207 | `LimitSIGPENDING` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1250` | Q | no |
| 208 | `LimitSIGPENDINGSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1251` | Q | no |
| 209 | `LimitSTACK` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1234` | Q | no |
| 210 | `LimitSTACKSoft` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1235` | Q | no |
| 211 | `LiveMountResult` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:365` | Q | yes |
| 212 | `LoadCredential` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1321` | Q | no |
| 213 | `LoadCredentialEncrypted` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1322` | Q | no |
| 214 | `LoadError` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:981` | Q | no |
| 215 | `LoadState` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:937` | Q | no |
| 216 | `LockPersonality` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1364` | Q | no |
| 217 | `LogExtraFields` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1308` | E | no |
| 218 | `LogFilterPatterns` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1309` | Q | no |
| 219 | `LogLevelMax` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1305` | Q | no |
| 220 | `LogNamespace` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1310` | Q | no |
| 221 | `LogRateLimitBurst` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1307` | Q | no |
| 222 | `LogRateLimitIntervalUSec` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1306` | Q | no |
| 223 | `LogsDirectory` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1384` | Q | no |
| 224 | `LogsDirectoryAccounting` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1382` | Q | no |
| 225 | `LogsDirectoryMode` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1381` | Q | no |
| 226 | `LogsDirectoryQuota` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1383` | Q | no |
| 227 | `LogsDirectoryQuotaUsage` | Service | none | `src/core/dbus-execute.c:1476` | Q | yes |
| 228 | `LogsDirectorySymlink` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1380` | Q | no |
| 229 | `MainPID` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:352` | V | yes |
| 230 | `ManagedOOMKills` | Service | none | `src/core/dbus-unit.c:1761` | Q | yes |
| 231 | `ManagedOOMMemoryPressure` | Service | none | `src/core/dbus-cgroup.c:424` | Q | yes |
| 232 | `ManagedOOMMemoryPressureDurationUSec` | Service | none | `src/core/dbus-cgroup.c:426` | Q | yes |
| 233 | `ManagedOOMMemoryPressureLimit` | Service | none | `src/core/dbus-cgroup.c:425` | Q | yes |
| 234 | `ManagedOOMPreference` | Service | none | `src/core/dbus-cgroup.c:427` | Q | yes |
| 235 | `ManagedOOMSwap` | Service | none | `src/core/dbus-cgroup.c:423` | Q | yes |
| 236 | `Markers` | Unit | none | `src/core/dbus-unit.c:970` | Q | yes |
| 237 | `MemoryAccounting` | Service | none | `src/core/dbus-cgroup.c:397` | Q | yes |
| 238 | `MemoryAvailable` | Service | none | `src/core/dbus-unit.c:1744` | Q | yes |
| 239 | `MemoryCurrent` | Service | none | `src/core/dbus-unit.c:1739` | V | yes |
| 240 | `MemoryDenyWriteExecute` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1388` | Q | no |
| 241 | `MemoryHigh` | Service | none | `src/core/dbus-cgroup.c:404` | Q | yes |
| 242 | `MemoryKSM` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1409` | Q | no |
| 243 | `MemoryLow` | Service | none | `src/core/dbus-cgroup.c:402` | Q | yes |
| 244 | `MemoryMax` | Service | none | `src/core/dbus-cgroup.c:406` | Q | yes |
| 245 | `MemoryMin` | Service | none | `src/core/dbus-cgroup.c:401` | Q | yes |
| 246 | `MemoryPeak` | Service | none | `src/core/dbus-unit.c:1740` | V | yes |
| 247 | `MemoryPressureThresholdUSec` | Service | none | `src/core/dbus-cgroup.c:433` | Q | yes |
| 248 | `MemoryPressureWatch` | Service | none | `src/core/dbus-cgroup.c:432` | Q | yes |
| 249 | `MemorySwapCurrent` | Service | none | `src/core/dbus-unit.c:1741` | V | yes |
| 250 | `MemorySwapMax` | Service | none | `src/core/dbus-cgroup.c:408` | Q | yes |
| 251 | `MemorySwapPeak` | Service | none | `src/core/dbus-unit.c:1742` | V | yes |
| 252 | `MemoryZSwapCurrent` | Service | none | `src/core/dbus-unit.c:1743` | V | yes |
| 253 | `MemoryZSwapMax` | Service | none | `src/core/dbus-cgroup.c:410` | Q | yes |
| 254 | `MemoryZSwapWriteback` | Service | none | `src/core/dbus-cgroup.c:412` | Q | yes |
| 255 | `MountAPIVFS` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1397` | Q | no |
| 256 | `MountFlags` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1333` | Q | no |
| 257 | `MountImagePolicy` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1414` | Q | no |
| 258 | `MountImages` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1272` | Q | no |
| 259 | `NFTSet` | Service | none | `src/core/dbus-cgroup.c:434` | Q | yes |
| 260 | `NFileDescriptorStore` | Service | none | `src/core/dbus-service.c:356` | Q | yes |
| 261 | `NRestarts` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:370` | V | yes |
| 262 | `NUMAMask` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1283` | Q | no |
| 263 | `NUMAPolicy` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1282` | Q | no |
| 264 | `Names` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:902` | Q | no |
| 265 | `NeedDaemonReload` | Unit | none | `src/core/dbus-unit.c:969` | Q | yes |
| 266 | `NetworkNamespacePath` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1411` | Q | no |
| 267 | `Nice` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1275` | Q | no |
| 268 | `NoExecPaths` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1331` | Q | no |
| 269 | `NoNewPrivileges` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1358` | Q | no |
| 270 | `NonBlocking` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1286` | Q | no |
| 271 | `NotifyAccess` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:331` | Q | yes |
| 272 | `OOMKills` | Service | none | `src/core/dbus-unit.c:1760` | Q | yes |
| 273 | `OOMPolicy` | Service | PROPERTY_CONST | `src/core/dbus-service.c:371` | Q | no |
| 274 | `OOMScoreAdjust` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1273` | Q | no |
| 275 | `OnFailure` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:922` | Q | no |
| 276 | `OnFailureJobMode` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:967` | Q | no |
| 277 | `OnFailureOf` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:923` | Q | no |
| 278 | `OnSuccess` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:920` | Q | no |
| 279 | `OnSuccessJobMode` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:966` | Q | no |
| 280 | `OnSuccessOf` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:921` | Q | no |
| 281 | `OpenFile` | Service | PROPERTY_CONST | `src/core/dbus-service.c:372` | Q | no |
| 282 | `PAMName` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1326` | Q | no |
| 283 | `PIDFile` | Service | PROPERTY_CONST | `src/core/dbus-service.c:330` | Q | no |
| 284 | `PartOf` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:908` | Q | no |
| 285 | `PassEnvironment` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1225` | Q | no |
| 286 | `Perpetual` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:983` | Q | no |
| 287 | `Personality` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1363` | Q | no |
| 288 | `PrivateBPF` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1404` | Q | no |
| 289 | `PrivateDevices` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1336` | Q | no |
| 290 | `PrivateIPC` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1347` | Q | no |
| 291 | `PrivateMounts` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1346` | Q | no |
| 292 | `PrivateNetwork` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1343` | Q | no |
| 293 | `PrivatePIDs` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1348` | Q | no |
| 294 | `PrivateTmp` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1334` | Q | no |
| 295 | `PrivateTmpEx` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1335` | Q | no |
| 296 | `PrivateUsers` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1344` | Q | no |
| 297 | `PrivateUsersEx` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1345` | Q | no |
| 298 | `ProcSubset` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1401` | Q | no |
| 299 | `PropagatesReloadTo` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:926` | Q | no |
| 300 | `PropagatesStopTo` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:928` | Q | no |
| 301 | `ProtectClock` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1337` | Q | no |
| 302 | `ProtectControlGroups` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1341` | Q | no |
| 303 | `ProtectControlGroupsEx` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1342` | Q | no |
| 304 | `ProtectHome` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1349` | Q | no |
| 305 | `ProtectHostname` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1402` | Q | no |
| 306 | `ProtectHostnameEx` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1403` | Q | no |
| 307 | `ProtectKernelLogs` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1340` | Q | no |
| 308 | `ProtectKernelModules` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1339` | Q | no |
| 309 | `ProtectKernelTunables` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1338` | Q | no |
| 310 | `ProtectProc` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1400` | Q | no |
| 311 | `ProtectSystem` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1350` | Q | no |
| 312 | `ReadOnlyPaths` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1328` | Q | no |
| 313 | `ReadWritePaths` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1327` | Q | no |
| 314 | `RebootArgument` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:991` | Q | no |
| 315 | `Refs` | Unit | none | `src/core/dbus-unit.c:994` | Q | yes |
| 316 | `RefuseManualStart` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:960` | Q | no |
| 317 | `RefuseManualStop` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:961` | Q | no |
| 318 | `ReloadPropagatedFrom` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:927` | Q | no |
| 319 | `ReloadResult` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:363` | Q | yes |
| 320 | `ReloadSignal` | Service | PROPERTY_CONST | `src/core/dbus-service.c:374` | Q | no |
| 321 | `RemainAfterExit` | Service | PROPERTY_CONST | `src/core/dbus-service.c:347` | Q | no |
| 322 | `RemoveIPC` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1318` | Q | no |
| 323 | `RequiredBy` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:910` | Q | no |
| 324 | `Requires` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:904` | Q | no |
| 325 | `RequiresMountsFor` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:932` | Q | no |
| 326 | `Requisite` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:905` | Q | no |
| 327 | `RequisiteOf` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:911` | Q | no |
| 328 | `Restart` | Service | PROPERTY_CONST | `src/core/dbus-service.c:328` | Q | no |
| 329 | `RestartForceExitStatus` | Service | PROPERTY_CONST | `src/core/dbus-service.c:350` | Q | no |
| 330 | `RestartKillSignal` | Service | PROPERTY_CONST | `src/core/dbus-kill.c:31` | Q | no |
| 331 | `RestartMaxDelayUSec` | Service | PROPERTY_CONST | `src/core/dbus-service.c:334` | Q | no |
| 332 | `RestartMode` | Service | PROPERTY_CONST | `src/core/dbus-service.c:329` | Q | no |
| 333 | `RestartPreventExitStatus` | Service | PROPERTY_CONST | `src/core/dbus-service.c:349` | Q | no |
| 334 | `RestartSteps` | Service | PROPERTY_CONST | `src/core/dbus-service.c:333` | Q | no |
| 335 | `RestartUSec` | Service | PROPERTY_CONST | `src/core/dbus-service.c:332` | Q | no |
| 336 | `RestartUSecNext` | Service | none | `src/core/dbus-service.c:335` | Q | yes |
| 337 | `RestrictAddressFamilies` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1365` | Q | no |
| 338 | `RestrictFileSystems` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1393` | Q | no |
| 339 | `RestrictNamespaces` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1391` | Q | no |
| 340 | `RestrictNetworkInterfaces` | Service | none | `src/core/dbus-cgroup.c:431` | Q | yes |
| 341 | `RestrictRealtime` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1389` | Q | no |
| 342 | `RestrictSUIDSGID` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1390` | Q | no |
| 343 | `Result` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:362` | V | yes |
| 344 | `RootDirectory` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1261` | Q | no |
| 345 | `RootDirectoryStartOnly` | Service | PROPERTY_CONST | `src/core/dbus-service.c:346` | Q | no |
| 346 | `RootEphemeral` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1269` | Q | no |
| 347 | `RootHash` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1264` | Q | no |
| 348 | `RootHashPath` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1265` | Q | no |
| 349 | `RootHashSignature` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1266` | Q | no |
| 350 | `RootHashSignaturePath` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1267` | Q | no |
| 351 | `RootImage` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1262` | Q | no |
| 352 | `RootImageOptions` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1263` | Q | no |
| 353 | `RootImagePolicy` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1413` | Q | no |
| 354 | `RootVerity` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1268` | Q | no |
| 355 | `RuntimeDirectory` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1369` | Q | no |
| 356 | `RuntimeDirectoryMode` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1368` | Q | no |
| 357 | `RuntimeDirectoryPreserve` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1367` | Q | no |
| 358 | `RuntimeDirectorySymlink` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1366` | Q | no |
| 359 | `RuntimeMaxUSec` | Service | PROPERTY_CONST | `src/core/dbus-service.c:341` | Q | no |
| 360 | `RuntimeRandomizedExtraUSec` | Service | PROPERTY_CONST | `src/core/dbus-service.c:342` | Q | no |
| 361 | `SELinuxContext` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1354` | Q | no |
| 362 | `SameProcessGroup` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1351` | Q | no |
| 363 | `SecureBits` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1311` | Q | no |
| 364 | `SendSIGHUP` | Service | PROPERTY_CONST | `src/core/dbus-kill.c:34` | Q | no |
| 365 | `SendSIGKILL` | Service | PROPERTY_CONST | `src/core/dbus-kill.c:33` | Q | no |
| 366 | `SetCredential` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1319` | E | no |
| 367 | `SetCredentialEncrypted` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1320` | E | no |
| 368 | `SetLoginEnvironment` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1317` | Q | no |
| 369 | `Slice` | Service | none | `src/core/dbus-unit.c:1736` | Q | yes |
| 370 | `SliceOf` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:931` | Q | no |
| 371 | `SmackProcessLabel` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1356` | Q | no |
| 372 | `SocketBindAllow` | Service | none | `src/core/dbus-cgroup.c:429` | Q | yes |
| 373 | `SocketBindDeny` | Service | none | `src/core/dbus-cgroup.c:430` | Q | yes |
| 374 | `SourcePath` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:942` | Q | no |
| 375 | `StandardError` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1292` | Q | no |
| 376 | `StandardErrorFileDescriptorName` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1293` | Q | no |
| 377 | `StandardInput` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1287` | Q | no |
| 378 | `StandardInputData` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1289` | E | no |
| 379 | `StandardInputFileDescriptorName` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1288` | Q | no |
| 380 | `StandardOutput` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1290` | Q | no |
| 381 | `StandardOutputFileDescriptorName` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1291` | Q | no |
| 382 | `StartLimitAction` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:986` | Q | no |
| 383 | `StartLimitBurst` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:985` | Q | no |
| 384 | `StartLimitIntervalUSec` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:984` | Q | no |
| 385 | `StartupAllowedCPUs` | Service | none | `src/core/dbus-cgroup.c:385` | Q | yes |
| 386 | `StartupAllowedMemoryNodes` | Service | none | `src/core/dbus-cgroup.c:387` | Q | yes |
| 387 | `StartupCPUWeight` | Service | none | `src/core/dbus-cgroup.c:381` | Q | yes |
| 388 | `StartupIOWeight` | Service | none | `src/core/dbus-cgroup.c:390` | Q | yes |
| 389 | `StartupMemoryHigh` | Service | none | `src/core/dbus-cgroup.c:405` | Q | yes |
| 390 | `StartupMemoryLow` | Service | none | `src/core/dbus-cgroup.c:403` | Q | yes |
| 391 | `StartupMemoryMax` | Service | none | `src/core/dbus-cgroup.c:407` | Q | yes |
| 392 | `StartupMemorySwapMax` | Service | none | `src/core/dbus-cgroup.c:409` | Q | yes |
| 393 | `StartupMemoryZSwapMax` | Service | none | `src/core/dbus-cgroup.c:411` | Q | yes |
| 394 | `StateChangeTimestamp` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:946` | V | yes |
| 395 | `StateChangeTimestampMonotonic` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:946` | V | yes |
| 396 | `StateDirectory` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1374` | Q | no |
| 397 | `StateDirectoryAccounting` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1372` | Q | no |
| 398 | `StateDirectoryMode` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1371` | Q | no |
| 399 | `StateDirectoryQuota` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1373` | Q | no |
| 400 | `StateDirectoryQuotaUsage` | Service | none | `src/core/dbus-execute.c:1474` | Q | yes |
| 401 | `StateDirectorySymlink` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1370` | Q | no |
| 402 | `StatusBusError` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:360` | Q | yes |
| 403 | `StatusErrno` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:359` | V | yes |
| 404 | `StatusText` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:358` | V | yes |
| 405 | `StatusVarlinkError` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:361` | Q | yes |
| 406 | `StopPropagatedFrom` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:929` | Q | no |
| 407 | `StopWhenUnneeded` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:959` | Q | no |
| 408 | `SubState` | Unit | PROPERTY_EMITS_CHANGE | `src/core/dbus-unit.c:940` | V | yes |
| 409 | `SuccessAction` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:989` | Q | no |
| 410 | `SuccessActionExitStatus` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:990` | Q | no |
| 411 | `SuccessExitStatus` | Service | PROPERTY_CONST | `src/core/dbus-service.c:351` | Q | no |
| 412 | `SupplementaryGroups` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1325` | Q | no |
| 413 | `SurviveFinalKillSignal` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:964` | Q | no |
| 414 | `SyslogFacility` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1304` | Q | no |
| 415 | `SyslogIdentifier` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1301` | Q | no |
| 416 | `SyslogLevel` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1303` | Q | no |
| 417 | `SyslogLevelPrefix` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1302` | Q | no |
| 418 | `SyslogPriority` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1300` | Q | no |
| 419 | `SystemCallArchitectures` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1360` | Q | no |
| 420 | `SystemCallErrorNumber` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1361` | Q | no |
| 421 | `SystemCallFilter` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1359` | Q | no |
| 422 | `SystemCallLog` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1362` | Q | no |
| 423 | `TTYColumns` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1299` | Q | no |
| 424 | `TTYPath` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1294` | Q | no |
| 425 | `TTYReset` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1295` | Q | no |
| 426 | `TTYRows` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1298` | Q | no |
| 427 | `TTYVHangup` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1296` | Q | no |
| 428 | `TTYVTDisallocate` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1297` | Q | no |
| 429 | `TasksAccounting` | Service | none | `src/core/dbus-cgroup.c:415` | Q | yes |
| 430 | `TasksCurrent` | Service | none | `src/core/dbus-unit.c:1750` | V | yes |
| 431 | `TasksMax` | Service | none | `src/core/dbus-cgroup.c:416` | Q | yes |
| 432 | `TemporaryFileSystem` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1396` | Q | no |
| 433 | `TimeoutAbortUSec` | Service | none | `src/core/dbus-service.c:338` | Q | yes |
| 434 | `TimeoutCleanUSec` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1387` | Q | no |
| 435 | `TimeoutStartFailureMode` | Service | PROPERTY_CONST | `src/core/dbus-service.c:339` | Q | no |
| 436 | `TimeoutStartUSec` | Service | PROPERTY_CONST | `src/core/dbus-service.c:336` | Q | no |
| 437 | `TimeoutStopFailureMode` | Service | PROPERTY_CONST | `src/core/dbus-service.c:340` | Q | no |
| 438 | `TimeoutStopUSec` | Service | PROPERTY_CONST | `src/core/dbus-service.c:337` | Q | no |
| 439 | `TimerSlackNSec` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1284` | Q | no |
| 440 | `Transient` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:982` | Q | no |
| 441 | `TriggeredBy` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:925` | Q | no |
| 442 | `Triggers` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:924` | Q | no |
| 443 | `Type` | Service | PROPERTY_CONST | `src/core/dbus-service.c:326` | Q | no |
| 444 | `UID` | Service | PROPERTY_EMITS_CHANGE | `src/core/dbus-service.c:368` | Q | yes |
| 445 | `UMask` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1227` | Q | no |
| 446 | `USBFunctionDescriptors` | Service | PROPERTY_CONST | `src/core/dbus-service.c:366` | Q | no |
| 447 | `USBFunctionStrings` | Service | PROPERTY_CONST | `src/core/dbus-service.c:367` | Q | no |
| 448 | `UnitFilePreset` | Unit | none | `src/core/dbus-unit.c:945` | Q | yes |
| 449 | `UnitFileState` | Unit | none | `src/core/dbus-unit.c:944` | Q | yes |
| 450 | `UnsetEnvironment` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1226` | Q | no |
| 451 | `UpheldBy` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:914` | Q | no |
| 452 | `Upholds` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:909` | Q | no |
| 453 | `User` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1314` | Q | no |
| 454 | `UserNamespacePath` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1410` | Q | no |
| 455 | `UtmpIdentifier` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1352` | Q | no |
| 456 | `UtmpMode` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1353` | Q | no |
| 457 | `WantedBy` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:912` | Q | no |
| 458 | `Wants` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:906` | Q | no |
| 459 | `WantsMountsFor` | Unit | PROPERTY_CONST | `src/core/dbus-unit.c:933` | Q | no |
| 460 | `WatchdogSignal` | Service | PROPERTY_CONST | `src/core/dbus-kill.c:35` | Q | no |
| 461 | `WatchdogTimestamp` | Service | none | `src/core/dbus-service.c:344` | V | yes |
| 462 | `WatchdogTimestampMonotonic` | Service | none | `src/core/dbus-service.c:344` | V | yes |
| 463 | `WatchdogUSec` | Service | none | `src/core/dbus-service.c:343` | Q | yes |
| 464 | `WorkingDirectory` | Service | PROPERTY_CONST | `src/core/dbus-execute.c:1260` | Q | no |

## Appendix B — systemd 259.5 manager properties (visible to `systemctl show`)

`§4.3.3 (b) query set`: `yes` for every `Default*` name and for `Version`, `Features`, `Architecture`, `UnitPath`, `ConfirmSpawn`, `ServiceWatchdogs`; `never` for any name containing `Environment`. The 52 `Default*` rows equal R5 c144 exactly.

| # | Property | vtable flags | Source (Ubuntu tree) | §4.3.3 (b) query set | Note |
|---:|---|---|---|---|---|
| 1 | `Architecture` | PROPERTY_CONST | `src/core/dbus-manager.c:2905` | yes |  |
| 2 | `ConfidentialVirtualization` | PROPERTY_CONST | `src/core/dbus-manager.c:2904` | no |  |
| 3 | `ConfirmSpawn` | PROPERTY_CONST | `src/core/dbus-manager.c:2937` | yes |  |
| 4 | `ControlGroup` | none | `src/core/dbus-manager.c:2953` | no |  |
| 5 | `CtrlAltDelBurstAction` | PROPERTY_CONST | `src/core/dbus-manager.c:3010` | no |  |
| 6 | `DefaultDeviceTimeoutUSec` | PROPERTY_CONST | `src/core/dbus-manager.c:2960` | yes |  |
| 7 | `DefaultIOAccounting` | PROPERTY_CONST | `src/core/dbus-manager.c:2967` | yes |  |
| 8 | `DefaultIPAccounting` | PROPERTY_CONST | `src/core/dbus-manager.c:2968` | yes |  |
| 9 | `DefaultLimitAS` | PROPERTY_CONST | `src/core/dbus-manager.c:2985` | yes |  |
| 10 | `DefaultLimitASSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2986` | yes |  |
| 11 | `DefaultLimitCORE` | PROPERTY_CONST | `src/core/dbus-manager.c:2979` | yes |  |
| 12 | `DefaultLimitCORESoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2980` | yes |  |
| 13 | `DefaultLimitCPU` | PROPERTY_CONST | `src/core/dbus-manager.c:2971` | yes |  |
| 14 | `DefaultLimitCPUSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2972` | yes |  |
| 15 | `DefaultLimitDATA` | PROPERTY_CONST | `src/core/dbus-manager.c:2975` | yes |  |
| 16 | `DefaultLimitDATASoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2976` | yes |  |
| 17 | `DefaultLimitFSIZE` | PROPERTY_CONST | `src/core/dbus-manager.c:2973` | yes |  |
| 18 | `DefaultLimitFSIZESoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2974` | yes |  |
| 19 | `DefaultLimitLOCKS` | PROPERTY_CONST | `src/core/dbus-manager.c:2991` | yes |  |
| 20 | `DefaultLimitLOCKSSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2992` | yes |  |
| 21 | `DefaultLimitMEMLOCK` | PROPERTY_CONST | `src/core/dbus-manager.c:2989` | yes |  |
| 22 | `DefaultLimitMEMLOCKSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2990` | yes |  |
| 23 | `DefaultLimitMSGQUEUE` | PROPERTY_CONST | `src/core/dbus-manager.c:2995` | yes |  |
| 24 | `DefaultLimitMSGQUEUESoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2996` | yes |  |
| 25 | `DefaultLimitNICE` | PROPERTY_CONST | `src/core/dbus-manager.c:2997` | yes |  |
| 26 | `DefaultLimitNICESoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2998` | yes |  |
| 27 | `DefaultLimitNOFILE` | PROPERTY_CONST | `src/core/dbus-manager.c:2983` | yes |  |
| 28 | `DefaultLimitNOFILESoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2984` | yes |  |
| 29 | `DefaultLimitNPROC` | PROPERTY_CONST | `src/core/dbus-manager.c:2987` | yes |  |
| 30 | `DefaultLimitNPROCSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2988` | yes |  |
| 31 | `DefaultLimitRSS` | PROPERTY_CONST | `src/core/dbus-manager.c:2981` | yes |  |
| 32 | `DefaultLimitRSSSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2982` | yes |  |
| 33 | `DefaultLimitRTPRIO` | PROPERTY_CONST | `src/core/dbus-manager.c:2999` | yes |  |
| 34 | `DefaultLimitRTPRIOSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:3000` | yes |  |
| 35 | `DefaultLimitRTTIME` | PROPERTY_CONST | `src/core/dbus-manager.c:3001` | yes |  |
| 36 | `DefaultLimitRTTIMESoft` | PROPERTY_CONST | `src/core/dbus-manager.c:3002` | yes |  |
| 37 | `DefaultLimitSIGPENDING` | PROPERTY_CONST | `src/core/dbus-manager.c:2993` | yes |  |
| 38 | `DefaultLimitSIGPENDINGSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2994` | yes |  |
| 39 | `DefaultLimitSTACK` | PROPERTY_CONST | `src/core/dbus-manager.c:2977` | yes |  |
| 40 | `DefaultLimitSTACKSoft` | PROPERTY_CONST | `src/core/dbus-manager.c:2978` | yes |  |
| 41 | `DefaultMemoryAccounting` | PROPERTY_CONST | `src/core/dbus-manager.c:2969` | yes |  |
| 42 | `DefaultMemoryPressureThresholdUSec` | none | `src/core/dbus-manager.c:3004` | yes |  |
| 43 | `DefaultMemoryPressureWatch` | none | `src/core/dbus-manager.c:3005` | yes |  |
| 44 | `DefaultOOMPolicy` | PROPERTY_CONST | `src/core/dbus-manager.c:3007` | yes |  |
| 45 | `DefaultOOMScoreAdjust` | PROPERTY_CONST | `src/core/dbus-manager.c:3008` | yes |  |
| 46 | `DefaultRestartUSec` | PROPERTY_CONST | `src/core/dbus-manager.c:2961` | yes |  |
| 47 | `DefaultRestrictSUIDSGID` | PROPERTY_CONST | `src/core/dbus-manager.c:3009` | yes |  |
| 48 | `DefaultStandardError` | PROPERTY_CONST | `src/core/dbus-manager.c:2941` | yes |  |
| 49 | `DefaultStandardOutput` | PROPERTY_CONST | `src/core/dbus-manager.c:2940` | yes |  |
| 50 | `DefaultStartLimitBurst` | PROPERTY_CONST | `src/core/dbus-manager.c:2966` | yes |  |
| 51 | `DefaultStartLimitIntervalUSec` | PROPERTY_CONST | `src/core/dbus-manager.c:2962` | yes |  |
| 52 | `DefaultTasksAccounting` | PROPERTY_CONST | `src/core/dbus-manager.c:2970` | yes |  |
| 53 | `DefaultTasksMax` | none | `src/core/dbus-manager.c:3003` | yes |  |
| 54 | `DefaultTimeoutAbortUSec` | none | `src/core/dbus-manager.c:2959` | yes |  |
| 55 | `DefaultTimeoutStartUSec` | PROPERTY_CONST | `src/core/dbus-manager.c:2957` | yes |  |
| 56 | `DefaultTimeoutStopUSec` | PROPERTY_CONST | `src/core/dbus-manager.c:2958` | yes |  |
| 57 | `DefaultTimerAccuracyUSec` | PROPERTY_CONST | `src/core/dbus-manager.c:2956` | yes |  |
| 58 | `Environment` | none | `src/core/dbus-manager.c:2936` | never | name contains `Environment`: never queried (C11 §4.4.3.5) |
| 59 | `ExitCode` | none | `src/core/dbus-manager.c:2955` | no |  |
| 60 | `Features` | PROPERTY_CONST | `src/core/dbus-manager.c:2902` | yes |  |
| 61 | `FinishTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2912` | no |  |
| 62 | `FinishTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2912` | no |  |
| 63 | `FirmwareTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2907` | no |  |
| 64 | `FirmwareTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2907` | no |  |
| 65 | `GeneratorsFinishTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2917` | no |  |
| 66 | `GeneratorsFinishTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2917` | no |  |
| 67 | `GeneratorsStartTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2916` | no |  |
| 68 | `GeneratorsStartTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2916` | no |  |
| 69 | `InitRDGeneratorsFinishTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2924` | no |  |
| 70 | `InitRDGeneratorsFinishTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2924` | no |  |
| 71 | `InitRDGeneratorsStartTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2923` | no |  |
| 72 | `InitRDGeneratorsStartTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2923` | no |  |
| 73 | `InitRDSecurityFinishTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2922` | no |  |
| 74 | `InitRDSecurityFinishTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2922` | no |  |
| 75 | `InitRDSecurityStartTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2921` | no |  |
| 76 | `InitRDSecurityStartTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2921` | no |  |
| 77 | `InitRDTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2910` | no |  |
| 78 | `InitRDTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2910` | no |  |
| 79 | `InitRDUnitsLoadFinishTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2926` | no |  |
| 80 | `InitRDUnitsLoadFinishTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2926` | no |  |
| 81 | `InitRDUnitsLoadStartTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2925` | no |  |
| 82 | `InitRDUnitsLoadStartTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2925` | no |  |
| 83 | `KExecWatchdogUSec` | none | `src/core/dbus-manager.c:2951` | no | writable |
| 84 | `KernelTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2909` | no |  |
| 85 | `KernelTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2909` | no |  |
| 86 | `LoaderTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2908` | no |  |
| 87 | `LoaderTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2908` | no |  |
| 88 | `LogLevel` | none | `src/core/dbus-manager.c:2927` | no | writable |
| 89 | `LogTarget` | none | `src/core/dbus-manager.c:2928` | no | writable |
| 90 | `NFailedJobs` | none | `src/core/dbus-manager.c:2933` | no |  |
| 91 | `NFailedUnits` | PROPERTY_EMITS_CHANGE | `src/core/dbus-manager.c:2930` | no |  |
| 92 | `NInstalledJobs` | none | `src/core/dbus-manager.c:2932` | no |  |
| 93 | `NJobs` | none | `src/core/dbus-manager.c:2931` | no |  |
| 94 | `NNames` | none | `src/core/dbus-manager.c:2929` | no |  |
| 95 | `Progress` | none | `src/core/dbus-manager.c:2935` | no |  |
| 96 | `RebootWatchdogUSec` | none | `src/core/dbus-manager.c:2948` | no | writable |
| 97 | `RuntimeWatchdogPreGovernor` | none | `src/core/dbus-manager.c:2947` | no | writable |
| 98 | `RuntimeWatchdogPreUSec` | none | `src/core/dbus-manager.c:2946` | no | writable |
| 99 | `RuntimeWatchdogUSec` | none | `src/core/dbus-manager.c:2945` | no | writable |
| 100 | `SecurityFinishTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2915` | no |  |
| 101 | `SecurityFinishTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2915` | no |  |
| 102 | `SecurityStartTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2914` | no |  |
| 103 | `SecurityStartTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2914` | no |  |
| 104 | `ServiceWatchdogs` | none | `src/core/dbus-manager.c:2952` | yes | writable |
| 105 | `ShowStatus` | none | `src/core/dbus-manager.c:2938` | no |  |
| 106 | `ShutdownStartTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2913` | no |  |
| 107 | `ShutdownStartTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2913` | no |  |
| 108 | `SoftRebootsCount` | PROPERTY_CONST | `src/core/dbus-manager.c:3011` | no |  |
| 109 | `SystemState` | none | `src/core/dbus-manager.c:2954` | no |  |
| 110 | `Tainted` | PROPERTY_CONST | `src/core/dbus-manager.c:2906` | no |  |
| 111 | `TimerSlackNSec` | PROPERTY_CONST | `src/core/dbus-manager.c:3006` | no |  |
| 112 | `TransactionsWithOrderingCycle` | none | `src/core/dbus-manager.c:2934` | no |  |
| 113 | `UnitPath` | PROPERTY_CONST | `src/core/dbus-manager.c:2939` | yes |  |
| 114 | `UnitsLoadFinishTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2919` | no |  |
| 115 | `UnitsLoadFinishTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2919` | no |  |
| 116 | `UnitsLoadStartTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2918` | no |  |
| 117 | `UnitsLoadStartTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2918` | no |  |
| 118 | `UnitsLoadTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2920` | no |  |
| 119 | `UnitsLoadTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2920` | no |  |
| 120 | `UserspaceTimestamp` | PROPERTY_CONST | `src/core/dbus-manager.c:2911` | no |  |
| 121 | `UserspaceTimestampMonotonic` | PROPERTY_CONST | `src/core/dbus-manager.c:2911` | no |  |
| 122 | `Version` | PROPERTY_CONST | `src/core/dbus-manager.c:2901` | yes |  |
| 123 | `Virtualization` | PROPERTY_CONST | `src/core/dbus-manager.c:2903` | no |  |
| 124 | `WatchdogDevice` | PROPERTY_CONST | `src/core/dbus-manager.c:2942` | no |  |
| 125 | `WatchdogLastPingTimestamp` | none | `src/core/dbus-manager.c:2943` | no |  |
| 126 | `WatchdogLastPingTimestampMonotonic` | none | `src/core/dbus-manager.c:2944` | no |  |

## Appendix C — hidden properties and the V-set gap

### C.1 Hidden (never printed by `systemctl show`)

Service object (27): `OnSuccesJobMode` (HIDDEN,PROPERTY_CONST, `src/core/dbus-unit.c:965`), `RequiresOverridable` (HIDDEN, `src/core/dbus-unit.c:1090`), `RequisiteOverridable` (HIDDEN, `src/core/dbus-unit.c:1091`), `RequiredByOverridable` (HIDDEN, `src/core/dbus-unit.c:1092`), `RequisiteOfOverridable` (HIDDEN, `src/core/dbus-unit.c:1093`), `StartLimitInterval` (HIDDEN,PROPERTY_CONST, `src/core/dbus-unit.c:1095`), `StartLimitIntervalSec` (HIDDEN,PROPERTY_CONST, `src/core/dbus-unit.c:1096`), `PermissionsStartOnly` (HIDDEN,PROPERTY_CONST, `src/core/dbus-service.c:345`), `StartLimitInterval` (HIDDEN,PROPERTY_CONST, `src/core/dbus-service.c:413`), `StartLimitBurst` (HIDDEN,PROPERTY_CONST, `src/core/dbus-service.c:414`), `StartLimitAction` (HIDDEN,PROPERTY_CONST, `src/core/dbus-service.c:415`), `FailureAction` (HIDDEN,PROPERTY_CONST, `src/core/dbus-service.c:416`), `RebootArgument` (HIDDEN,PROPERTY_CONST, `src/core/dbus-service.c:417`), `MemoryLimit` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:438`), `CPUShares` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:439`), `StartupCPUShares` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:440`), `BlockIOAccounting` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:441`), `BlockIOWeight` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:442`), `StartupBlockIOWeight` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:443`), `BlockIODeviceWeight` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:444`), `BlockIOReadBandwidth` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:445`), `BlockIOWriteBandwidth` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:446`), `CPUAccounting` (DEPRECATED,HIDDEN, `src/core/dbus-cgroup.c:448`), `Capabilities` (HIDDEN,PROPERTY_CONST, `src/core/dbus-execute.c:1418`), `ReadWriteDirectories` (HIDDEN,PROPERTY_CONST, `src/core/dbus-execute.c:1419`), `ReadOnlyDirectories` (HIDDEN,PROPERTY_CONST, `src/core/dbus-execute.c:1420`), `InaccessibleDirectories` (HIDDEN,PROPERTY_CONST, `src/core/dbus-execute.c:1421`), `IOScheduling` (HIDDEN,PROPERTY_CONST, `src/core/dbus-execute.c:1422`).

Manager (5): `ShutdownWatchdogUSec` (HIDDEN, `src/core/dbus-manager.c:2950`), `DefaultStartLimitIntervalSec` (HIDDEN,PROPERTY_CONST, `src/core/dbus-manager.c:2964`), `DefaultStartLimitInterval` (HIDDEN,PROPERTY_CONST, `src/core/dbus-manager.c:2965`), `DefaultBlockIOAccounting` (DEPRECATED,HIDDEN,PROPERTY_CONST, `src/core/dbus-manager.c:3014`), `DefaultCPUAccounting` (DEPRECATED,HIDDEN,PROPERTY_CONST, `src/core/dbus-manager.c:3016`).

### C.2 Run-time-varying visible service properties outside the design V and E sets (109)

Source basis: the vtable entry is not `PROPERTY_CONST`. The three-way split is a reasoned proposal (R) for the reviewer.

* **Run-time state values (30)** — proposed for V or for separate checks: `ActivationDetails`, `AssertResult`, `Asserts`, `CacheDirectoryQuotaUsage`, `CleanResult`, `ConditionResult`, `Conditions`, `DebugInvocation`, `Following`, `FreezerState`, `GID`, `Job`, `LiveMountResult`, `LogsDirectoryQuotaUsage`, `ManagedOOMKills`, `Markers`, `MemoryAvailable`, `NFileDescriptorStore`, `NeedDaemonReload`, `OOMKills`, `Refs`, `ReloadResult`, `RestartUSecNext`, `StateDirectoryQuotaUsage`, `StatusBusError`, `StatusVarlinkError`, `UID`, `UnitFilePreset`, `UnitFileState`, `WatchdogUSec`.
* **`Exec*` arrays (16)** — compared after the §4.4 normalization: `ExecCondition`, `ExecConditionEx`, `ExecReload`, `ExecReloadEx`, `ExecReloadPost`, `ExecReloadPostEx`, `ExecStart`, `ExecStartEx`, `ExecStartPost`, `ExecStartPostEx`, `ExecStartPre`, `ExecStartPreEx`, `ExecStop`, `ExecStopEx`, `ExecStopPost`, `ExecStopPostEx`.
* **Run-time-settable configuration (63)** — proposed to stay compared, because `set-property --runtime` can change them without a reload: `AllowedCPUs`, `AllowedMemoryNodes`, `BPFProgram`, `CPUQuotaPerSecUSec`, `CPUQuotaPeriodUSec`, `CPUWeight`, `CoredumpReceive`, `DefaultMemoryLow`, `DefaultMemoryMin`, `DefaultStartupMemoryLow`, `Delegate`, `DelegateControllers`, `DelegateSubgroup`, `DeviceAllow`, `DevicePolicy`, `DisableControllers`, `FileDescriptorStorePreserve`, `IOAccounting`, `IODeviceLatencyTargetUSec`, `IODeviceWeight`, `IOReadBandwidthMax`, `IOReadIOPSMax`, `IOWeight`, `IOWriteBandwidthMax`, `IOWriteIOPSMax`, `IPAccounting`, `IPAddressAllow`, `IPAddressDeny`, `IPEgressFilterPath`, `IPIngressFilterPath`, `ManagedOOMMemoryPressure`, `ManagedOOMMemoryPressureDurationUSec`, `ManagedOOMMemoryPressureLimit`, `ManagedOOMPreference`, `ManagedOOMSwap`, `MemoryAccounting`, `MemoryHigh`, `MemoryLow`, `MemoryMax`, `MemoryMin`, `MemoryPressureThresholdUSec`, `MemoryPressureWatch`, `MemorySwapMax`, `MemoryZSwapMax`, `MemoryZSwapWriteback`, `NFTSet`, `NotifyAccess`, `RestrictNetworkInterfaces`, `Slice`, `SocketBindAllow`, `SocketBindDeny`, `StartupAllowedCPUs`, `StartupAllowedMemoryNodes`, `StartupCPUWeight`, `StartupIOWeight`, `StartupMemoryHigh`, `StartupMemoryLow`, `StartupMemoryMax`, `StartupMemorySwapMax`, `StartupMemoryZSwapMax`, `TasksAccounting`, `TasksMax`, `TimeoutAbortUSec`.

## Appendix D — download ledger

*(R2)* This is R1's ledger, carried as history. Its nine `bolt`, `fwupd` and `packagekit` rows and the Launchpad `getPublishedSources` query in the last paragraph record R1's out-of-authority retrieval (R1-F2). They are non-authoritative and no conclusion in this record rests on them; the R2 authority is not retroactive. The authorized R2 retrieval is Appendix E.

All files were downloaded on 2026-10-06 into the temporary directory `/tmp/ohs2-r1-20261006/dl`, which was deleted at the end of the run (handback §6). Launchpad files came from `https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/<source>/<version>/<file>`. Each `.dsc` checksum list matched its files.

| SHA-256 | Bytes | File |
|---|---:|---|
| `c4c764e0b98b7840619f16f42fb8229a344bc2946bd1a74612280d5e218f8177` | 8779 | `systemd_259.5-0ubuntu3.4.dsc` |
| `80ed55a8a69c4bd1fb12a36659303372b37baf9ee224ef4f032db4b748be0f76` | 17336729 | `systemd_259.5.orig.tar.gz` |
| `34048bc4b67dce61835a5a959d903f912d68bb09a93ba654e6ae33410c74aaa9` | 267032 | `systemd_259.5-0ubuntu3.4.debian.tar.xz` |
| `838df29d92dd84c99173e5610cadcec33c66965760bdc8023573045c488c00f6` | 3201 | `policykit-1_127-2ubuntu1.1.dsc` |
| `9b7bc16f086479dcc626c575976568ba4a85d34297a750d8ab3d2e57f6d8b988` | 472872 | `policykit-1_127.orig.tar.gz` |
| `2f8f11ca818b9726dd8ed9f8979e0a0211edb7b9ee1949b6fb5df697333da73d` | 31456 | `policykit-1_127-2ubuntu1.1.debian.tar.xz` |
| `da10d551ca51076bf7bf663de38369d04e267386b8211c283c2814e68e482ed3` | 9078 | `glibc_2.43-2ubuntu2.4.dsc` |
| `d9c86c6b5dbddb43a3e08270c5844fc5177d19442cf5b8df4be7c07cd5fa3831` | 20297012 | `glibc_2.43.orig.tar.xz` |
| `28103a7cf808c29901c6053d89a4e8299880abfbb850c0d97a09c8df8533e306` | 530764 | `glibc_2.43-2ubuntu2.4.debian.tar.xz` |
| `00771af0fbfa9e80f9269df87d346ebec91d7eddad597a674eaec0844911e165` | 4226 | `python3.14_3.14.4-1ubuntu0.2.dsc` |
| `d923c51303e38e249136fc1bdf3568d56ecb03214efdef48516176d3d7faaef8` | 23855332 | `python3.14_3.14.4.orig.tar.xz` |
| `c23cc6a28530e50e6d2c99bc7aa05122d00fd2f6d7d619184a95cb1dcff31fbe` | 240104 | `python3.14_3.14.4-1ubuntu0.2.debian.tar.xz` |
| `70114682332062c01b806c202dfeeb7408db898bbb57f55b518bcb0f8fba9c71` | 7746 | `linux_7.0.0-31.31.dsc` |
| `c6343795c8c7e4feff55f5b309365c8e0eaf49cd6abcb412e32315313f149536` | 254937830 | `linux_7.0.0.orig.tar.gz` |
| `7d1ee5c5a554dc037f9d1ce643b644edff63c01718a4fa1d5c735e064b33cd6a` | 2399688 | `linux_7.0.0-31.31.diff.gz` |
| `75046d4c15ba654c2999e50135de37be32819d8868bf79a7087c579b04e7fb52` | 2399 | `bolt_0.9.10-1.dsc` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `050f9cdebbda55e078df3037fd6d467069c5e10e264b02bc6c625ae38386ec1f` | 257367 | `bolt_0.9.10.orig.tar.gz` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `5d090c653b541a19d50f8edf6e8bb398879485006972175cfb8c8d9d1193da28` | 4464 | `bolt_0.9.10-1.debian.tar.xz` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `0e4f798f4e9313aec5126b0d524ec471d4c621d1f6c2a2283a6897b18d3be141` | 3638 | `fwupd_2.1.1-1ubuntu3.1.dsc` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `1bb6e7bef9a5e2ed4ba847a6e38b7d6ee87ad7255c8c4f090aef34b611b5626b` | 7209099 | `fwupd_2.1.1.orig.tar.gz` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `342f256f97dd20f6b99abcad3ecc4786ab22622716e8b39f5b6202be15094292` | 36436 | `fwupd_2.1.1-1ubuntu3.1.debian.tar.xz` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `5f7e5590b65887b6ad1cd29fa8791b547f25b651ec90103a82134bf2337bfce9` | 2451 | `packagekit_1.3.4-3ubuntu1.2.dsc` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `5d79d97a66fd9a50fcc82419ab530fe7b2102aa3afb1dec53df5d29efba2e687` | 2963704 | `packagekit_1.3.4.orig.tar.xz` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `87866162101f3828dc395623e1e04c42c596373e06bce826d9756e07cdda5df2` | 29732 | `packagekit_1.3.4-3ubuntu1.2.debian.tar.xz` *(R2: R1 retrieval outside R1's authority, R1-F2; non-authoritative)* |
| `bf9dc5d223b56bd2493a5dcd5ffd1bd31976f9d118ee26470d7f5ffc34e4828e` | 13881 | `kernel-sha256sums.asc` |

Upstream comparison artifacts (hashed, then deleted; their SHA-256 equals the matching `orig` above): `https://github.com/systemd/systemd/archive/refs/tags/v259.5.tar.gz`, `https://github.com/polkit-org/polkit/archive/refs/tags/127.tar.gz`, `https://www.python.org/ftp/python/3.14.4/Python-3.14.4.tar.xz`, `https://mirrors.kernel.org/gnu/glibc/glibc-2.43.tar.xz`. The kernel `orig` was compared with the `linux-7.0.tar.gz` line of `https://cdn.kernel.org/pub/linux/kernel/v7.x/sha256sums.asc` rather than downloaded twice. Other metadata fetched (not used as evidence of content): the Launchpad source pages for each version and `https://api.launchpad.net/devel/ubuntu/+archive/primary?ws.op=getPublishedSources&…&distro_series=…/resolute` for `bolt`, `fwupd`, `packagekit`.

## Appendix E — R2 download ledger *(R2)*

Authority: [R2 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md),
which adds exactly these three Ubuntu source packages. Retrieved on
2026-10-06 between 19:10:45Z and 19:11:07Z with `curl -fsSL --proto '=https'`
into `/tmp/ohs2-r2-jGOhonwm/dl` (created by `mktemp -d`, mode `0700`). Each
request URL was
`https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/<source>/<version>/<file>`;
the effective URL after redirection is listed. Every file named by a `.dsc`
was checked against that `.dsc`'s `Checksums-Sha256` entry, hash and size,
before use: **all six equal**. Each `.dsc` names exactly two files. The
directory was deleted after this record was written (R2 handback §8).

| SHA-256 | Bytes | File | Effective URL | `.dsc` check |
|---|---:|---|---|---|
| `75046d4c15ba654c2999e50135de37be32819d8868bf79a7087c579b04e7fb52` | 2399 | `bolt_0.9.10-1.dsc` | `https://launchpadlibrarian.net/815520686/bolt_0.9.10-1.dsc` | — |
| `050f9cdebbda55e078df3037fd6d467069c5e10e264b02bc6c625ae38386ec1f` | 257367 | `bolt_0.9.10.orig.tar.gz` | `https://launchpadlibrarian.net/815520687/bolt_0.9.10.orig.tar.gz` | equal |
| `5d090c653b541a19d50f8edf6e8bb398879485006972175cfb8c8d9d1193da28` | 4464 | `bolt_0.9.10-1.debian.tar.xz` | `https://launchpadlibrarian.net/815520688/bolt_0.9.10-1.debian.tar.xz` | equal |
| `0e4f798f4e9313aec5126b0d524ec471d4c621d1f6c2a2283a6897b18d3be141` | 3638 | `fwupd_2.1.1-1ubuntu3.1.dsc` | `https://launchpadlibrarian.net/866019113/fwupd_2.1.1-1ubuntu3.1.dsc` | — |
| `1bb6e7bef9a5e2ed4ba847a6e38b7d6ee87ad7255c8c4f090aef34b611b5626b` | 7209099 | `fwupd_2.1.1.orig.tar.gz` | `https://launchpadlibrarian.net/866019111/fwupd_2.1.1.orig.tar.gz` | equal |
| `342f256f97dd20f6b99abcad3ecc4786ab22622716e8b39f5b6202be15094292` | 36436 | `fwupd_2.1.1-1ubuntu3.1.debian.tar.xz` | `https://launchpadlibrarian.net/866019112/fwupd_2.1.1-1ubuntu3.1.debian.tar.xz` | equal |
| `5f7e5590b65887b6ad1cd29fa8791b547f25b651ec90103a82134bf2337bfce9` | 2451 | `packagekit_1.3.4-3ubuntu1.2.dsc` | `https://launchpadlibrarian.net/869859579/packagekit_1.3.4-3ubuntu1.2.dsc` | — |
| `5d79d97a66fd9a50fcc82419ab530fe7b2102aa3afb1dec53df5d29efba2e687` | 2963704 | `packagekit_1.3.4.orig.tar.xz` | `https://launchpadlibrarian.net/869859576/packagekit_1.3.4.orig.tar.xz` | equal |
| `87866162101f3828dc395623e1e04c42c596373e06bce826d9756e07cdda5df2` | 29732 | `packagekit_1.3.4-3ubuntu1.2.debian.tar.xz` | `https://launchpadlibrarian.net/869859578/packagekit_1.3.4-3ubuntu1.2.debian.tar.xz` | equal |

Files statically inspected (paths inside each archive):

* `bolt-0.9.10-c0d4cb2f4399e86417907a37c0d8ef3bb9fb406f/`: `policy/org.freedesktop.bolt.rules.in`, `meson.build`, `meson_options.txt`; `debian/`: `rules`, `bolt.install`, `patches/series` (empty).
* `fwupd-2.1.1/`: `policy/org.freedesktop.fwupd.rules`, `policy/meson.build`, `meson.build` (polkit and `subdir('policy')` lines), `meson_options.txt` (polkit option); `debian/`: `rules`, `fwupd.install`, `patches/series` and the `---`/`+++` headers of each listed patch.
* `PackageKit-1.3.4/`: `policy/org.freedesktop.packagekit.rules`, `policy/meson.build`, `meson.build` (polkit and `subdir('policy')` lines); `debian/`: `rules`, `packagekit.install`, `patches/series` and the `---`/`+++` headers of each listed patch.

Derived byte streams (§R2-3): `org.freedesktop.bolt.rules`
`16da883b6ec384e0018b7e955efef1726e6470c2b4f72bfc23f9aadbec0709ca` (368);
`org.freedesktop.fwupd.rules`
`f78e67e4e002dfd135d5bd8cb8d7b66c174d795316a1cd7bf0f3e021b85ee3a0` (251);
`org.freedesktop.packagekit.rules`
`d22e59e890fd6726eaf02aded197fdc40da11bbc11fc2184d581e14e0a0437e6` (549). Each
equals the durable R5 c113, c114 and c115 digest and the R5 HF-11/HF-12 size.

*Consistency note, not evidence:* the nine R2 file digests equal the nine
digests in R1's Appendix D. R2's conclusions do not depend on that equality.
