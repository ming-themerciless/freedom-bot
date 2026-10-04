# Preparation handback — fresh R-5 successor assignment (R3, `/var/tmp`)

Work ID: `C-P5.0-R5-RP11-FRESH-A2`

Date: 2026-10-03

Drafting assignee: Claude

Controlling prompt:
[`phase-5-0-p5-r5-rp11-fresh-r5-new-run-assignment-preparation-claude-prompt.md`](phase-5-0-p5-r5-rp11-fresh-r5-new-run-assignment-preparation-claude-prompt.md)
(SHA-256 `64a1c7e5dce442d1001961932b1c7c72a945a8a9cb74f489eb380907bc219334`)

Proposed assignment:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md)

| Property | Value |
|---|---|
| SHA-256 | `9959d93da7fafb194f942657a3851e83652dc8e1b9ec332b0fa5abd7abb72909` |
| Byte length | 109644 |

Status: **Proposal returned for independent Codex review. It is not accepted,
not activated and not executable.** Claude implemented I-7/I-7-R1 and remains
ineligible to execute R-5, to be its assignee, to select one, or to review or
accept the assignment. No R-5 command was executed and `oracle-test` was not
accessed. Claude has stopped.

R-5 remains Blocking and unaccepted; `FRESH-R5-HS-1` remains open against the
closed predecessor handback; RP-11 remains unwired and unmet;
`plan.is_executable=False`; PO-9 and PO-14 remain open; Package 5.0 remains
not ready.

---

## 1. Inputs read

The canonical instructions were read first: `.agents/AGENTS.md` completely;
`docs/implementation-plan.md` reading map, §0, §16 and §20; `docs/review/Handover
information`; and the `docs/operations/disposable-test-server.md` restriction
banner. Then, completely:

| Input | SHA-256 |
|---|---|
| accepted predecessor, as activated: [`…-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md) | `dab0a5c23086a1cda4054b441565aa8ec0e207ff1c4ddad6e0bcc4bc8a089bd5` |
| its reviewed proposal: [`…-rebuild-reviewed-proposal.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-reviewed-proposal.md) | `f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94` (equals the accepted digest) |
| Gemini's closed HARD STOP handback: [`…-rebuild-handback.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-handback.md) | `797c431dd4147d96062de4b7a1978316973c6690c0c84f3b7f5154664ffd1c3f` (equals the digest Codex reviewed; not edited) |
| Codex's independent HARD STOP review: [`project-review-2026-10-03-…-hard-stop.md`](project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop.md) | `7cbf37f187966e18c0d1f9c7bad2a370e0168790de894e2e9ad28dc61d292b40` |
| Peter's acceptance and cleanup authority: [`project-review-2026-10-03-…-acceptance-and-cleanup-authority.md`](project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop-acceptance-and-cleanup-authority.md) | `62eebcfa278dc0988c6bf084c87cf2276933dfad5410892457726511868a503c` |
| cleanup result: [`phase-5-0-p5-r5-rp11-fresh-r5-cleanup-result.md`](phase-5-0-p5-r5-rp11-fresh-r5-cleanup-result.md) | `41b93f0ae38807710bb4333de03e6714ea6ec2ad3298dbaa6f201338adb51492` |

The activated predecessor differs from the reviewed proposal only in its
acceptance and activation metadata (title, work-ID and assignee lines, status,
§0, §5 handback row, §7.1 and the §12 U-7 row), as the activation record
states. R3 is derived from the activated text, and its pending-acceptance
wording follows the reviewed proposal's.

To check that the run's outer-host paths are only bind sources and never
embedded in a compared output, `infra/rp11-launch/buildroot/enter.py` was read
completely, and `provision.py`, `cc1check.py`, `ic1check.py`, `build.sh`,
`tests/test_rp11_launch_toolchain.py` and `tests/rp11_launch_support.py` were
searched for any `tempfile`, `TMPDIR`, `/tmp` or `/var/tmp` use (§4).

No disposable artifact of the stopped run was read or reused. Those paths have
been deleted, and this work used only repository records.

## 2. How R3 was produced

R3 was generated from the activated predecessor by a script of exact
replacements. Each replacement asserts its expected occurrence count, so the
script stops if the source text is not exactly as expected. The outer-host
substitution `/tmp/<RUN>-` → `/var/tmp/<RUN>-` is **pattern-specific, not a
global `/tmp` substitution**. It touches only the 89 run-resource references,
which all have the form `/tmp/<RUN>-…`. It runs before any new text is
inserted. Every other `/tmp` or `/var/tmp` reference was classified and either
kept or rewritten by hand (§4).

## 3. Amendments made (prompt items 1–7)

| # | Prompt requirement | R3 implementation |
|---|---|---|
| 1 | all outer-host run resources under `/var/tmp/<RUN>-*`; build root's own `/tmp`/`/var/tmp` keep their meaning | §5 table and location paragraph; all of steps 4a, 4b (destination only), 4d, 5, 6/7, 8, 9, 10 (`--basetemp`, `--junitxml`, `RP11_LAUNCH_BUILD_ROOT`) and 11. A new §5 paragraph defines the build root's own `/tmp` and `/var/tmp` (`/var/tmp/<RUN>-root/tmp`, `/var/tmp/<RUN>-root/var/tmp`). Statuses 12 and 13 and S7.4 are unchanged in meaning |
| 2 | prefix check in `oracle-test:/var/tmp`; record `df`, fs type, mount options, available bytes, inodes before creation; missing/link/non-directory or < 4 GiB is a HARD STOP; floor is not an allowance | S2.18 (`df -P /tmp`) is replaced by **S2.18a** (`lstat`: missing, link, non-directory or `realpath` ≠ `/var/tmp` → **15**), **S2.18b** `df -P -T /var/tmp`, **S2.18c** `df -P -i /var/tmp`, and **S2.18d** (`/proc/self/mountinfo` mount point, fstype, source, mount and superblock options; `statvfs` bytes and inodes; `f_bavail × f_frsize` < 4,294,967,296 → **16**). S2.25 now lists `/var/tmp`. New statuses 15 and 16 are in the §6.0 table. §5 states that the floor is a preflight stop condition, not an allowance. All of this runs in step 2, before step 4a creates anything |
| 3 | consistent `/var/tmp` naming in creation, sync, build, evidence, accounting, retention and cleanup-state statements | §4.4, §5, §7 summary, §7.2, §8.3, §10 items 4, 8 and 13, and §10.1 intro and item 3 |
| 4 | `FRESH-R5-HS-1`, prospectively | S1.3 is now a single Python invocation that runs `git status --short --untracked-files=all` once. It writes git's complete stdout byte for byte, then `git_status_lines=<N>` and `git_status_sha256=<digest>` of those same bytes, and exits with git's status. S1.4, which prints and gates the derived repository state, runs after it. The step-1 Pass text, §6 step 12b and §10 item 3 require every S1.3 line to be reproduced verbatim. The reviewer recomputes the count and digest from the handback, and a mismatch is missing evidence (§8.3). The closed predecessor handback was not edited |
| 5 | new run identifier and handback path; no resume or reuse | `<RUN>` must differ from `p5-r5-fresh-20261002T184800Z-7e9b2d41` (§5). The stopped run's resources are added to the §2 item 4 Gemini clause and the §5 forbidden list. The proposed work ID is `C-P5.0-R5-RP11-FRESH-R5-R3`, pending acceptance. The handback is `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md` (§5 table, §10, §12 U-7) |
| 6 | no remediation, retry, cleanup, package change, privilege, service/database, secrets, commit or push; complete handback and closing record at any terminal state | Preserved unchanged (§6 step 12, §7.2, §8). §7.2 adds that the 2026-10-03 inspection and cleanup authority was exhausted, is not inherited, and that the executor deletes or frees nothing |
| 7 | resolved invocation in assignment and handback | new §13 of the assignment, and §8 below |

Other changes, all consequential to the items above:

* title, header, status and §0 restated as an unaccepted proposal, with
  links to the HARD STOP records;
* §0.1, which tabulates the amendments;
* §1, which states that the run is not a resume or retry;
* §3.2, which records the A2 re-verification;
* §4.4, which does not assume the stopped-run or cleanup capacity figures;
* §7.1, which now describes the current no-access banner instead of an
  active one;
* §12, with U-7 pending again and new rows U-10, U-11 and U-12.

**Not changed:** the 28 pinned digests and lengths (§3.2, Appendices A and B
are byte-identical); the reference environment and HA rules (§3.4, §4.1–§4.3);
every comparison, gate value and status meaning other than 10 (`/tmp` →
`/var/tmp`); block structure, order, single invocation and timestamp contract
(§6.0); and §8 verdict precedence and PASS conditions.

## 4. Mechanical audit of the location change

Script audit over the final bytes; every check passed (0 failures).

| Check | Result |
|---|---|
| outer-host `/tmp/<RUN>` references remaining | only the §0.1 row that describes the change ("instead of `/tmp/<RUN>-*`") |
| predecessor `/tmp/<RUN>-` references / R3 `/var/tmp/<RUN>-` references | 89 / 94 (the 89 moved plus 5 new prose references) |
| doubled prefix `/var/var` | none |
| bare `/tmp` references in R3 | each one classified, none unclassified. **Historical or forbidden:** `/tmp/r5-*`, `/tmp/p5-b1-repro-*`, `/tmp/pytest-of-*`, `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-*`. **Build-root internal:** statuses 12 and 13, S7.4's `-root/tmp` and `-root/var/tmp` arguments, §5's build-root paragraph, §10 item 8, U-10. **Repository host:** §5, §7. **Context or prohibition:** §4.4, §5 location paragraph and forbidden list, §7.2 |
| `bash` fences | 18 in both. Only the step-1 and step-2 blocks differ beyond the path move; the other 16 fences are byte-identical after `/tmp/<RUN>-` → `/var/tmp/<RUN>-` |
| outer-host `/tmp` inside any block | none. The only `/tmp` left in a block is the build root's own `/var/tmp/<RUN>-root/tmp` and `…/var/tmp` (S7.4) |
| step 4b `rsync` | identical except `oracle-test:/tmp/` → `oracle-test:/var/tmp/` in the destination. `.claude/hooks/guard-secrets.py` exits 0 (admits) for the exact R3 command with a sample `<RUN>` |
| syntax | `bash -n` passes for all 16 `R5BLOCK` blocks after the §6.0 substitutions (sample `<RUN>`, appendices, S1.6 program, `<HANDBACK>`) |
| S1.3 program, run read-only on the repository host | exit 0. Its body is byte-equal to a direct `git status --short --untracked-files=all` (35 lines at the time). `git_status_lines` and `git_status_sha256` match a recomputation from those bytes. It precedes S1.4 |
| S2.18a program, run locally | local `/var/tmp` → 0. Missing path, symlink, regular file and a path through a linked parent → 15 each |
| S2.18d program, run locally | local `/var/tmp` (ext4) → 0. With the floor raised to 10¹⁸ → 16. On `/dev/shm` it selects the `/dev/shm` tmpfs mount, so the longest-prefix mount selection works. The floor is `4*1024**3` of `f_bavail*f_frsize` |
| ordering | S2.18a–S2.18d run before S2.25, both in step 2, before step 4a's `mkdir` |
| `/goal` invocation | present verbatim in assignment §13 |
| links, whitespace | all relative links resolve; the only exception is this handback, which was written after the audit. No trailing whitespace; single final newline |
| pinned inputs | all 28 files match their §3.2 SHA-256 and length; `infra/rp11-launch/` is exactly 22 files in 5 directories; the lock has 62 `package=` lines, snapshot `20261001T000000Z` and manifest digest `f08ba9de…e76f`. `git status` of `infra`, `tests`, `tools` and `pytest.ini` shows no change. HEAD is `9cad3ded6479fb7b423b35c1d815fbfc7e48aaaa` |

The executed sources use no `tempfile`, `TMPDIR` or outer-host `/tmp`. pytest
temporary paths come from `tmp_path_factory` under `--basetemp`. The only other
`/tmp` and `/var/tmp` mentions are inside the sandbox: `provision.py`'s
in-root `tmp` and `var/tmp`, `ic1check.py`'s in-root rule, and the test's
`--tmpfs /tmp` bwrap argument. `enter.py` uses the outer root, checkout and
work paths only as `bwrap` bind sources or outer file paths. They are never
written into the regenerated manifest, the four normative outputs or `cc1.v`,
which are produced inside the sandbox at `/`, `/rp11/co` and its `build-out`.

## 5. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md` | new (the proposal) |
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3-handback.md` | new (this handback) |

No other file was created or modified. The predecessor assignment, its reviewed
proposal, the closed Gemini handback, the review, authority and cleanup records,
and every governance or current-state document (Handover, status, plan §20,
test-server banner) are untouched. Recording any of them is for the maintainer
or a separately assigned agent. No migration, configuration, dependency, code
or test change. No commit or push.

## 6. Checks not run

* Any R-5 block or command, including the S1.8 in-memory review-manifest
  build. Only the pinned digests, tree, lock facts and controlled-path status
  were re-verified, by independent read-only scripts.
* Any `oracle-test` access or observation. `/var/tmp` capacity, filesystem,
  mount options and quota on `oracle-test` are therefore not known to this
  work beyond Codex's cleanup record. S2.18a–S2.18d observe them at run time.
* Repository test suites. This is a documentation-only change and the prompt
  forbids host execution. `python3 .claude/hooks/test_guards.py` was not run
  because neither guard changed; the secrets guard itself was exercised on
  the new `rsync` text.
* `git diff --check`, which does not cover untracked files. The audit's own
  trailing-whitespace and final-newline checks were run instead.

## 7. Unresolved issues and proposed reviewer focus

1. **S1.3 completeness rule (design choice).** R3 makes a handback whose
   reproduced S1.3 lines disagree with `git_status_lines` or
   `git_status_sha256` **missing evidence**, and therefore a HARD STOP of
   record (§10 item 3). This is stricter than a record-accuracy finding: a
   transcription error alone would void an otherwise clean run. Codex and
   Peter should confirm that this strength is intended, or downgrade it to a
   reviewable finding.
2. **S1.3 as a Python wrapper.** The prompt asks for "the complete actual
   stdout" of the git command. R3 runs git once inside a `python3 -I -B`
   wrapper, which writes git's bytes unmodified, so the count and digest come
   from the same reading. A bare `git status` followed by a second digest
   invocation would read the tree twice. Confirm that the wrapper satisfies
   the requirement.
3. **"Derived" repository-state result.** S1.4 is unchanged. It is a
   separate `git status --porcelain --untracked-files=all` over the controlled
   paths, which runs after S1.3. It is not computed from S1.3's bytes,
   because that would change an accepted gate.
4. **U-12, per-user quota.** The stopped run's `Errno 122` is "Disk quota
   exceeded". The cleanup result attributes it to tmpfs capacity, and `/tmp`
   carried `usrquota`. On `/var/tmp`, per-user quota headroom cannot be
   observed without privilege, and `quota` is not installed. S2.18d records
   the mount and superblock options so that quota options are visible. It
   does not gate on them, because the prompt names only the three HARD STOP
   conditions. A write failure remains a HARD STOP.
5. **AppArmor (observation, unchanged).** The stopped run recorded
   `apparmor_restrict_unprivileged_userns=1`. It stopped before step 5's
   `enter.py ldconfig`, so the first unprivileged bubblewrap entry on this
   host is still unexercised. R3 keeps the accepted rule: the value is
   recorded, and a restriction that prevents bubblewrap is a HARD STOP at
   step 5. This is unrelated to the location change and is noted only so it
   is not mistaken for a new risk.
6. **Retention on `/var/tmp`.** Unlike the tmpfs `/tmp`, `/var/tmp`
   survives reboot, but host housekeeping may age entries. §10.1 already makes
   the handback the evidence of record, so R3 adds no retention promise.
7. **Identifiers.** The work ID `C-P5.0-R5-RP11-FRESH-R5-R3` is proposed,
   and Peter confirms or replaces it. The handback path is fixed by the
   prompt.

No rule, authority, privacy, migration or architecture conflict was found that
required stopping.

## 8. Resolved Gemini invocation

For the activator to copy without interpretation once Codex has reviewed and
Peter has accepted and activated the assignment. It is inert until then:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

## 9. Deployment, configuration and rollback

None. The change is two new documentation files and nothing else. To roll back,
delete them. The proposal becomes active only through Codex's independent
review and Peter Duscha's recorded acceptance and activation. Claude has
stopped.
