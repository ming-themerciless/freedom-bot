# Claude — LAB-1 raw read-back byte binding remediation

Date: 2026-09-13. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Review: [Codex R2 re-review](project-review-2026-09-12-lab1-rereview-r2.md).

## Assignment and boundary

Address **PR-20260912-LAB1-2** in one bounded local pass. Make the run-record
writer prove that the raw bytes returned by the destination are exactly the
bytes it serialized and wrote. Return one handback to Codex for independent
technical re-review. Do not close LAB-1 or the finding on the implementer's
authority.

This is a narrow read-back integrity correction. Do not redesign the run-record
schema, cleanup state machine, canonical recovery procedures, observation
importer, reservation lifecycle, runner contract or laboratory architecture.
Preserve the positive technical assessment of the exact per-cause recovery
validation and schema-version-3 transition. Prefer a focused change in
`tools/phase_5_0_evidence/execution/artifact.py` and its existing R13 regression
section.

The active assignment is local-only. No host, database, provisioning or real
execution work is authorized.

## Required context

Before changing anything, read `.agents/AGENTS.md` completely; the implementation
plan's reading map and §§0, 12 (Phase 5/5.0), 13, 16 and 20; the active handover;
and the disposable-server restriction banner. Then read:

- the R2 re-review named above and the handback it reviews;
- the preceding LAB-1 remediation prompt and re-review for history;
- runner contract r6 §8, including its dated follow-up;
- `execution/artifact.py`, its callers and the connected R13 tests; and
- the generated review-manifest contract.

Check Git status and preserve every unrelated and reviewer-authored change. Do
not overwrite or amend either Codex review record. Trace the exact raw value from
`json.dumps(...).encode("utf-8")`, through `destination.write_bytes()`, through
`destination.read_bytes()`, to the equality check, JSON parsing and
`validate_run_record()`.

## 1. Reproduce both defects first

Add failing-before regressions through the public `write_run_record()` path for
the two independent reproductions:

```text
read_back = b"\n" + serialized + b"\n"                    -> accepted
read_back = serialized with a duplicate schema_version=3  -> accepted
```

The duplicate member must carry the same value so that parsing produces the
same mapping and demonstrates why mapping equality plus canonical
re-serialization is insufficient. Show that both regressions fail against the
submitted tree and pass after correction without discarding or rewriting the
submitted tree to obtain the comparison.

## 2. Bind the raw bytes exactly

Retain the exact bytes returned by `destination.read_bytes()` and compare them
directly with `serialized`. Any byte difference must raise the existing fixed,
safe `NOT_THE_DOCUMENT_WRITTEN` refusal before the function can report a written
artifact.

The completed path must establish all three distinct claims:

1. the raw bytes read back equal the bytes serialized and written;
2. those bytes decode and parse as the expected document; and
3. the parsed document satisfies `validate_run_record()` including the exact
   per-cause canonical recovery contract.

Do not substitute a digest, normalized JSON, mapping equality, a newly
serialized mapping, file size, or decoded-text equality for raw byte equality.
Do not weaken the existing mapping/schema validation: raw equality proves what
came back, while validation proves what the document means. Preserve fixed and
bounded error messages; do not include a path, raw bytes, parsed hostile content
or operating-system text in a refusal.

This correction does not change the meaning of a valid schema-3 document, so do
not raise the run-record schema version merely for this writer implementation
fix. If inspection reveals a genuine document-contract change, stop and report
it rather than broadening the assignment.

## 3. Required regressions and negative control

Cover at least:

- leading or trailing whitespace added to the read-back bytes is refused;
- a duplicate top-level key with the same value is refused;
- a duplicate nested cleanup key with the same value is refused;
- the exact bytes written and returned are accepted through the public writer;
- malformed or partially flushed bytes continue to refuse;
- the existing substituted scalar/list matrix continues to refuse;
- the four accepted cleanup-cause combinations continue to pass; and
- schema version 2 continues to refuse rather than being reinterpreted.

Add a negative control proving that gutting or hardcoding the raw-byte comparison
makes at least the whitespace and duplicate-key regressions fail. The control
must exercise `write_run_record()`; testing a helper in isolation is not enough.

Prefer one named comparison whose inputs include the actual raw read-back bytes,
so weakening the binding is a visible edit. Avoid tests that merely reconstruct
the expected boolean beside the implementation.

## 4. Preserve accepted behavior and artifacts

Preserve:

- run-record schema version 3;
- observation schema version 3 and its separate cause/procedure fields;
- review-manifest version 10 unless its own declared contract genuinely changes;
- exact residue/configuration procedure validation and strict key sets;
- the operator-facing S-B message naming each applicable recovery;
- all R3/R4/R5 lifecycle fixes, reservation binding and terminal order;
- every unresolved C-7 case and target-fact refusal; and
- `is_executable=False`, EH-R16-1 Open, Package 5.0 not ready,
  package-level P5.0-R5 Blocking and OD-62 Open.

Because `artifact.py` is a covered source, regenerate the manifest and concrete
plan only through the non-executing CLI. Generate twice and prove byte identity,
independently recompute every covered hash, replace the installed generated
artifacts only with verified output, and report the new review-input digest.
Never pass any digest to `--execute`; never hand-edit generated artifacts.

Update the active handover, implementation-plan §20 action pointer and project
status only after implementation and evidence are complete. Preserve historical
entries and add dated corrections rather than silently rewriting them.

## 5. Restrictions and verification

No SSH, synchronization, host inspection, preflight, permission change,
provisioning, database operation, destructive drill, service change, credential
access, generated-vector execution, `--execute`, real boundary/materializer,
migration, deployment, cutover, commit, push, reset or history rewrite. Do not
restart the bot. Prior dependency installation on `oracle-test` broadens none of
these permissions.

Use available local interpreters only and keep `TEST_DATABASE_URL` unset. Run
the narrow run-record tests first, then the focused LAB-1 set, structural
no-execution suite and complete synthetic evidence harness. Run the other locally
available repository suites serially as required by `.agents/AGENTS.md`, and
report exact interpreters, results and skips. Every skip is unverified.
Distinguish unavailable tooling from a pass. Run scoped `compileall`, configured
formatter/linter/type checks if present, and `git diff --check`.

Demonstrate test sensitivity by reversing only the raw-byte repair in a scratch
copy or by an equivalent controlled negative-control run. Name any new tests that
remain green under reversal and explain why; do not summarize the reversal only
as an aggregate count.

## 6. Handback

Write one dated R2 remediation handback containing:

- PR-20260912-LAB1-2 disposition and traceability;
- failing-before and passing-after evidence for both reproductions;
- the exact raw-byte comparison and its ordering relative to parse/validation;
- confirmation that schema versions and accepted cause/content behavior remain;
- the regression matrix, negative control and reversal results;
- files changed, security/operational implications and rollback;
- commands, interpreters, exact results, skips and unavailable checks;
- generated-artifact integrity and the new review-only digest; and
- every remaining gate and the next Codex checkpoint.

Return to Codex for independent technical re-review. Do not claim LAB-1 closed,
Package 5.0 ready or execution authorized.
