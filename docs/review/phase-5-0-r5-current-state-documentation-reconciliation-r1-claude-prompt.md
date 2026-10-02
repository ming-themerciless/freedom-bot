# Claude prompt — R-5 current-state documentation reconciliation R1

Work ID: `C-P5.0-R5-DOC-R1-R1`

Date: 2026-10-01

Assignee: Claude

Status: **authorized one-line documentation remediation**

## 1. Finding and objective

Codex's independent review found one Important documentation-accuracy defect:

`DOC-R1-1` — `docs/project-management/status.md` says the resumed R-5
handback “also misstates the pinned snapshot date.” That is no longer true of
the amended handback. The initial handback misstated the date, and Gemini's R2
remediation corrected it.

Correct that historical sentence without changing any decision, authority,
result or current-action disposition.

## 2. Required context

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation-plan reading map, §0, §16 and §20;
3. `docs/review/Handover information`;
4. the original documentation-reconciliation prompt and handback;
5. Gemini's R2 handback, especially its snapshot correction; and
6. this prompt.

Inspect `git status` and preserve every unrelated change.

## 3. Required change

Edit only `docs/project-management/status.md` so the affected paragraph says,
in substance:

* the initial returned handback misstated the pinned snapshot date; and
* Gemini's R2 remediation corrected that date, introduced the same-invocation
  R-1/R-2 manifest gate, and withdrew the erroneous R-5 PASS.

Use past tense for the corrected historical defect. Do not imply that the
current amended R-5 handback still contains the wrong date.

Do not otherwise rewrite, reorder or reformat the status document.

The existing
`status-through-2026-10-01-r5-r3-acceptance.md` snapshot must remain
byte-identical. It records the canonical state before Claude's original
reconciliation, not this still-unaccepted review correction. Do not create a
new snapshot or edit an archive index for this one-line pre-acceptance
remediation.

## 4. Concurrency and restrictions

Gemini's R4-R1 record remediation may still be active. Gemini exclusively owns
its R4 and R4-R1 handbacks. Claude must not open for editing, modify, delete,
rename, stage or format either Gemini handback or any Gemini prompt.

Claude may modify only:

* `docs/project-management/status.md`; and
* the remediation handback named in §5.

No other governance document, archive, index, source, test, fixture, launcher
artifact, lock, manifest or evidence file may change.

No SSH, synchronization, `oracle-test`, network access, download, package
operation, provisioning, build, service or database action, harness
`--execute`, secrets scan, commit or push is authorized.

## 5. Verification, handback and stop gate

Verify:

1. the status diff contains only the minimum historical wording correction;
2. the R2 handback states the snapshot was corrected to
   `20261001T000000Z`;
3. the existing status snapshot still has SHA-256
   `ee3ba027539239e6b25207e5eeec84e58d57190fad9d07bf2d51d85eea6724f7`;
4. all relative links in `status.md` resolve; and
5. `git diff --check` is clean for the authorized files.

Write:

`docs/review/phase-5-0-r5-current-state-documentation-reconciliation-r1-handback.md`

Include the exact before/after sentence and SHA-256 of `status.md`, verification
results, confirmation that the snapshot and Gemini-owned files were untouched,
and the unchanged project disposition.

Stop after the handback. Do not incorporate Gemini's R4 result, update the
current action, authorize an R-5 rerun or advance another package.
