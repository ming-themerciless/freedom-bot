# Gemini prompt — R-5 R4-R1 baseline-recovery record remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-R4-R1`

Date: 2026-10-01

Assignee: Gemini

Status: **authorized documentation-only correction; no renewed recovery search**

## 1. Objective

Correct two accuracy defects in Gemini's R4 baseline-recovery handback without
changing its substantive Branch B result:

1. The handback says the repository worktree was “inspected completely” and
   that no file anywhere in it contains the target raw artifact. The recorded
   operations searched selected names (`*cc1*`, `*.v`, `build-out`, and related
   launcher/test paths). Those operations support the narrower statement that
   no candidate was found by the recorded bounded filename/path searches; they
   do not prove that no differently named file in the worktree could contain
   the bytes.
2. The candidate table's byte-length cell for Gemini's stopped-run `cc1.v`
   says “Recorded in stopped run.” No numeric byte length was retained in the
   cited record. The cell must say `Unknown — artifact not retained and no byte
   length recorded`, or equivalent truthful wording.

Branch B remains correct: the historical baseline artifact was not recovered,
no fixture was created, and R-5 remains stopped.

## 2. Required context

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation-plan reading map, §0, §13, §16, §17 and §20;
3. the current `docs/review/Handover information`;
4. the R4 prompt and R4 handback;
5. the R3 acceptance decision; and
6. this prompt.

Inspect `git status` and preserve all unrelated work. Claude's concurrent
documentation assignment is complete; its files remain outside this task and
must not be modified.

## 3. Required corrections

Edit only the R4 handback:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-handback.md`

Make these precise changes:

* replace every claim of complete or exhaustive repository inspection with a
  statement bounded to the exact searches recorded in §2;
* replace “No file anywhere in the repository worktree contains raw bytes with
  SHA-256 …” with a statement that no candidate path was identified by those
  recorded searches;
* state explicitly that differently named content was not exhaustively hashed
  and that R4 did not authorize an expanded content scan;
* correct the stopped-run candidate's byte length to unknown/not recorded;
* retain the exact commands already run, without inventing additional checks;
* retain Branch B, the no-fixture result, all restrictions and the stop gate;
  and
* add a short R4-R1 correction note naming these two changes.

Do not repeat the search, run new discovery commands, hash additional
candidates, access an external artifact, or alter any technical conclusion.

## 4. Authority and restrictions

Gemini may modify only the R4 handback named in §3 and create the R4-R1
handback named in §5.

Do not modify Claude's documentation-reconciliation handback or any canonical
handover, status, implementation-plan, operations, archive, change-log or
decision-register file. Do not modify the R3 acceptance, R4 prompt, launcher
files, tests, fixtures, locks, manifests, listings or other evidence.

No filesystem search beyond opening the two authorized handback paths, SSH,
rsync, `oracle-test`, network access, download, `sudo`, package action,
provisioning, build-root creation, compiler or launcher build, baseline
reproduction, R-5 rerun, service or database action, harness `--execute`,
secrets scan, commit or push is authorized.

## 5. Required handback and stop gate

Write:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-r1-baseline-recovery-record-remediation-handback.md`

Include:

* the exact statements corrected;
* before/after SHA-256 for the amended R4 handback;
* confirmation that no search or recovery operation was repeated;
* confirmation that no fixture or other existing file was changed;
* `git diff --check` for the two authorized files; and
* the unchanged Branch B disposition and residual blocker.

Stop after the handback. Do not begin another recovery method or act on
Claude's completed work.
