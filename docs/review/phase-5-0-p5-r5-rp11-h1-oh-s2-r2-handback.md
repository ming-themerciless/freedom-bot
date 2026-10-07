# Handback — OH-S2 R2 remediation of R1-F1 and R1-F2: `OH-S2 R2 REMEDIATION READY FOR REVIEW`

Work ID: `C-P5.0-R5-RP11-H1-OH-S2-R2-20261006-08`

Date: 2026-10-06

Executor: Claude Code on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s2-r2-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-remediation-claude-prompt.md),
**11759 bytes, SHA-256
`ca6dd02ff3400573413f77c3067366bd86259a599ba2107c963322f68bb0d05f`**,
recomputed with `wc -c` and `sha256sum` before any research or edit and equal
to the pin in the
[R2 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md).
· Cumulative record: [`phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md).

## 1. Terminal state

**`OH-S2 R2 REMEDIATION READY FOR REVIEW`.** No `HARD STOP` condition arose:
the prompt identity matched, and every authorized Polkit-rule source was
retrieved and validated. Nothing is accepted or authorized by this return.
**Neither R1 nor R2 is accepted because R2 is complete.** I have not accepted
my own work or proposed a successor slice.

## 2. Remediation summary

| Finding | Closing evidence and wording | Record |
|---|---|---|
| **R1-F1** — prohibited secret-file read, contradictory reporting | States plainly that R1's repository-root recursive `grep` **read** prohibited secret-bearing paths and that **R1 was nonconforming** for that reason; withdraws R1's no-secret-read wording for review purposes (R1 files unchanged); distinguishes the admitted read from R1's *reported* absence of printed or retained content, which R2 cannot verify; records that **Peter was notified through independent review**; makes **no** rotation or incident-response decision (Peter's); and documents bounded R2 commands | §R2-1.1 |
| **R1-F2** — `bolt`, `fwupd`, `packagekit` outside R1 authority | Marks R1's three-package evidence (§2.1 row, three §6.1 identifications, nine Appendix D rows, the Launchpad API query) **non-authoritative**; re-retrieves only `bolt` `0.9.10-1`, `fwupd` `2.1.1-1ubuntu3.1`, `packagekit` `1.3.4-3ubuntu1.2` under the R2 authority; validates every `Checksums-Sha256` entry; derives the three installed rule byte streams, **each equal to its durable R5 digest and size**; states the **non-retroactivity rule** | §R2-1.2, §R2-2, §R2-3, Appendix E |

Affected limbs: PO-11 (b)'s `/usr/share` sub-limb and, through (b), PO-11 (g).
**No verdict or disposition changes.** `/etc/polkit-1/rules.d` remains MF-3
and is not inferred from distribution packages. Every R1 requirement and limb
carries an explicit verdict in §R2-6.

R2 is a remediation of the two findings, not a repeat of R1's research. All
unaffected conclusions are carried from R1's durable citations as proposed
material; R2 checked their H-0 inputs' traceability against the durable R5 and
H-0G handbacks (§R2-4) and reports three internal contradictions found while
composing (§R2-5, IC-1 … IC-3). No R1 technical correction was dropped.

## 3. Files changed

Created:

- `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md` — cumulative R2
  record. Composed from a byte copy of the R1 record, then edited only at the
  *(R2)*-marked places: header, new §§R2-0 … R2-6, §0.2 item 5, §2.1, §2.3,
  §6.1, §6.4 (b) and (g), §13 PO-11 row, §14.1, §16 polkit row, Appendix D
  note and row markers, new Appendix E.
- `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-handback.md` — this handback.

Updated (current-state pointers only; additive):

- `docs/review/Handover information` — heading set to "OH-S2 R2 returned for
  review"; one return paragraph; R2 authority and prompt relabelled
  *Consumed*; record and handback links added.
- `docs/project-management/status.md` — the same, in its current-status section.
- `docs/implementation-plan.md` — §20 only: the same.
- `docs/operations/disposable-test-server.md` — restriction banner only: R2
  consumed, returned without host access; MF facts need separate authority.

**Pre-existing worktree changes.** At the start, `git status --short` showed
11 modified tracked files and 53 untracked paths, all from earlier slices. Four
of the modified files are the pointers above; their earlier uncommitted
changes were preserved and R2 only added to them. All other pre-existing
modified and untracked paths were left untouched. Not edited: the R1 record,
R1 handback, R1 prompt, R1 authority, R2 prompt, R2 authority, any accepted
historical record, and any implementation, test, configuration, migration,
skill or hook file.

## 4. Sources consulted

Network (the only network use; under the R2 authority): the three `.dsc` files
and the six files they name, from
`https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/…`, redirected to
`launchpadlibrarian.net`. URLs, times, sizes and SHA-256: record Appendix E.
Nothing else was retrieved: no systemd, Linux, glibc, CPython, polkit or
upstream comparison artifact, and no Launchpad API query.

Repository (read by exact path): `.agents/AGENTS.md` (complete);
`docs/implementation-plan.md` reading map, §§0, 14, 16, 17, 20; `docs/review/Handover information`;
the `disposable-test-server.md` banner; the R2 authority and prompt; the R1
authority, prompt, complete citation record and complete handback; the
one-host design §4.4 (H-0 fact set, PO-19, PO-20, PO-11 extensions, PO-21,
citation order) and its PO-11 references; cumulative R3 §§6.6–7.2, 13–14 and
its acceptance; the composed H-0 review; the H-0 and U-9 acceptance; and the
R5 and H-0G handbacks as durable evidence only (fixed-string searches and the
HF-12 output section of R5).

## 5. Commands and results

Every command named its targets exactly. None was recursive over the
repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command (exact targets) | Result |
|---|---|---|
| 1 | `wc -c`, `sha256sum` on the R2 prompt; `cat` of the R2 authority | `11759`; `ca6dd02f…d05f`: **equal** |
| 2 | `git status --short` (prompt-required) | 11 modified, 53 untracked, all pre-existing |
| 3 | `sed -n`, `grep -n` on named repository documents (plan, design, R3, R5, H-0G, R1 files, status) | read as listed in §4 |
| 4 | `mktemp -d /tmp/ohs2-r2-XXXXXXXX`; `chmod 0700` | `/tmp/ohs2-r2-jGOhonwm`, owner `foundry`, mode `700`, 19:10:45Z |
| 5 | `curl -fsSL --proto '=https' --max-time 60` for the three `.dsc` files into `…/dl` | HTTP 200; 2399, 3638, 2451 bytes |
| 6 | `sha256sum …/dl/*.dsc`; `sed -n` of each `Checksums-Sha256` list | each names exactly two files |
| 7 | `curl` (same flags, `--max-time 300`) for the six named files | HTTP 200; sizes as in Appendix E; finished 19:11:07Z |
| 8 | for each `.dsc` entry: `sha256sum` and `stat -c %s` vs the listed hash and size | **6/6 EQUAL** |
| 9 | `tar -tf` on each of the six archives, filtered by `grep -E` for policy, rules, packaging and meson files | members located |
| 10 | `tar -x` of named members only (`--no-same-owner --no-same-permissions`) into `…/src/{bolt,fwupd,pk}/{orig,deb}`; `find` on `…/src` only | 0 symlinks; only expected files |
| 11 | `cat` of each `debian/patches/series`; `grep -E '^(\+\+\+\|---) '` on each patch in those extracted directories | no patch touches any `.rules` file |
| 12 | `grep -n`, `sed -n`, `cat -n`, `cat -A` on the extracted rule, meson and packaging files | build steps as in record §R2-3 |
| 13 | `sed 's/@privileged_group@/sudo/g'`; `sed 's,wheel,sudo,'`; `cp` — on copies into `…/derived` | three derived files |
| 14 | `sha256sum`, `stat -c %s` of derived files vs R5 c113–c115 digests and HF-11 sizes | **3/3 EQUAL** (368, 251, 549 bytes) |
| 15 | `grep -cF` of 23 fixed strings in exactly the R5 and H-0G handbacks | all H-0 inputs found; no `RUNPATH`/`RPATH`/`readelf` |
| 16 | `cp` of the R1 record to the R2 path; `sha256sum` of the four R1 files | R1 digests recorded in the R2 header |
| 17 | `Edit` and a `python3 -I` text replacement (exact-count asserted) on the R2 record; heredoc append of Appendix E | edits applied |
| 18 | temporary-directory deletion (§8) | deleted 22:03:50Z |
| 19 | `python3 -I` exact-count replacements in the four pointer files | 4 files edited |
| 20 | final checks (§7) | see §7 |

## 6. Checks not run, and why

- No SSH or other host connection, `oracle-test`, production, staging, Foundry
  or database access, and no retained-evidence access: forbidden.
- No application test, hook test (`python3 .claude/hooks/test_guards.py`),
  formatter, build, package tool or upstream build system: forbidden, and this
  is a documentation slice. `run-suites` does not apply.
- No PGP verification of the `.dsc` files: no keyring operation was in scope.
  `.dsc` integrity rests on HTTPS retrieval from Launchpad; each named file's
  integrity rests on the `.dsc` checksum.
- No re-verification of R1's systemd, polkit, glibc, CPython or Linux line
  citations: re-retrieval of those sources is forbidden. They are carried as
  proposed material (record §R2-0).
- No investigation of R1-F1 beyond the R1 handback's own text: inspecting
  secret-bearing files, shell history, the R1 session scratchpad or logs is
  forbidden.

## 7. Final checks

Run after every deliverable and pointer edit was written. All operated on the
explicit allowlist of six files only.

| Check | Result |
|---|---|
| Prompt identity, re-checked at the end | `ca6dd02f…d05f`: equal |
| R1 record, handback, prompt and authority unchanged | SHA-256 equal to the start-of-composition digests in the record header |
| Derived Polkit rule bytes vs durable R5 digests (no retained-path access) | 3/3 equal (§5 row 14) |
| `.dsc` checksum sets | 6/6 entries equal (§5 row 8) |
| Repository-relative links | 170 links in the six files, 0 broken. Done in two steps: targets were first listed without touching the filesystem (62 distinct, all project documentation) and only then tested for existence |
| Trailing whitespace, six files | 0 lines |
| `git diff --check` on the four tracked pointer files | exit 0, no output |
| Required-term scan of the two new files | `R1-F1`, `R1-F2`, nonconformance, Peter-notified status, non-retroactivity and the three exact package versions all present in both |
| Diff review | the R2 record differs from R1 only at *(R2)*-marked places (28 R1 lines replaced, plus additions); the pointer edits only add a return paragraph and relabel links. No host, implementation, successor, cleanup, credential, secret, commit or push authority is granted or implied |

**Guard refusal, disclosed.** My first combined final-check command was
refused by `.claude/hooks/guard-secrets.py`. The refusal came from the command
text: my link checker contained a deny-list regular expression spelling
secret-bearing file names, and the guard matched on it. The guard stopped the
whole call, so nothing in it ran and no file was read. I did not rewrite the
pattern to get past the guard. Instead I removed the deny-list and used the
two-step method in the table above. No other guard refusal occurred.

## 8. Temporary-path disposition

`/tmp/ohs2-r2-jGOhonwm` was created by `mktemp -d` in this run. Before
deletion it was resolved with `realpath -e` and verified to match
`/tmp/ohs2-r2-?*`, to be a directory directly beneath `/tmp`, not `/tmp`
itself, not a symlink, and owned by the executing user. It held 11 MB
(downloads, extracted members, derived files). It was deleted with
`rm -rf -- /tmp/ohs2-r2-jGOhonwm` at 2026-10-06T22:03:50Z, after all citation
data was in the record; a following `ls -ld` reported `No such file or
directory`. No helper script or derived artifact was kept anywhere else: R2
wrote no file to any session scratchpad, and its only helper code ran inline
(`python3 -I` from stdin) on named repository files. No downloaded archive or
source tree is in the repository. No other path was cleaned.

## 9. Security implications

- **R1-F1 remains a security-compliance incident for Peter.** R2 did not read,
  test, hash, list or link-check any secret-bearing path, and connected to no
  host and no retained evidence path. It cannot say what R1's recursive search
  opened beyond R1's own disclosure. Whether credential rotation or other
  incident response is needed is Peter's decision; R2 does not decide it.
- R2's link check listed every target before any existence test; all 62
  distinct targets were project documentation (§7).
- The three re-cited rule files grant only `bolt`, `fwupd` and `packagekit`
  actions to active local `sudo` members. `ubuntu` is in `sudo` (HF-03), so
  those actions are available to an active local `ubuntu` session; none
  touches `org.freedesktop.systemd1`. This is unchanged from R1.
- All R1 security implications (R1 handback §9: LB-2S provenance, X-1,
  PO-12 refutation, PO-11 (d) bound, `flock`, soft-reboot, Live Update) are
  carried unchanged and remain for review.

## 10. Unresolved questions for Peter and the reviewer

1. R1-F1 incident response: whether any credential rotation or further action
   is required (Peter's decision; R2 makes none).
2. R1's helper scripts and derived TSV/Markdown files reportedly persist in
   R1's session scratchpad (R1 handback §6; record IC-3). R2 did not inspect
   them. Their retention or removal needs Peter's decision and its own
   authority.
3. All R1 questions stand unchanged (R1 handback §11): the dispositions, PO-12′,
   the activation-design restatements, X-1, MF-1 … MF-8 and C-1 … C-14.

## 11. Proposed independent-review focus

1. §R2-1: whether the R1-F1 wording is plain, makes no no-secret-read claim,
   and leaves rotation to Peter; whether the R2 command record (§5) is bounded.
2. §R2-1.2, §R2-2: whether every dependency on R1's three-package evidence is
   identified and replaced, and the non-retroactivity statement is sufficient.
3. §R2-3, Appendix E: the derivations (bolt `@privileged_group@`, fwupd
   `debian/rules:56`, packagekit unchanged) and the digest equalities.
4. §R2-6: completeness of the limb register against R1 §§3–12.
5. That the carried text matches R1 apart from the *(R2)* markings (for
   example, `diff` of the R1 and R2 records).

OH-S2 R2 remediation awaits independent Codex review; no host, implementation, cleanup, OH-S3/OH-S4p or later slice is authorized.
