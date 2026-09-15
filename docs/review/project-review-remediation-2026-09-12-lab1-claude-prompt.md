# Claude — LAB-1 run-record binding remediation

Date: 2026-09-12. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Review: [project-review-2026-09-12-lab1-rereview.md](project-review-2026-09-12-lab1-rereview.md).

## Assignment and boundary

Address **PR-20260912-LAB1-1** in one bounded local pass. Preserve the accepted
separation between residue recovery and configuration recovery, but make the
schema-2 run-record writer/read-back path prove the exact procedure the outcome
produced and its correspondence to the cleanup state. Return one handback to
Codex for independent technical re-review. Do not close LAB-1 on the
implementer's authority.

This is a run-record integrity correction, not permission to redesign the
cleanup state machine, observation importer, reservation lifecycle or
laboratory architecture. Prefer the existing `execution/artifact.py`, cleanup
types and focused regression modules.

The maintainer separately authorized installation of the repository-declared
pytest packages on `oracle-test`; pytest 8.4.2 is now present in
`/opt/freedom-blades/runtime/venv-web`. That completed operation does **not**
authorize Claude to SSH, synchronize, inspect the host, run tests there,
provision anything or execute the harness. The active remediation remains
local-only.

## Required context

Before changing anything, read `.agents/AGENTS.md` completely; the
implementation plan's reading map and §§0, 12 (Phase 5/5.0), 13, 16 and 20;
the active handover; and the disposable-server restriction banner. Then read:

- the LAB-1 disposition and Codex re-review named above;
- runner contract r6 §8, including the dated follow-up;
- `cleanup.py`, `journal.py`, `feasibility.py`, `observations.py`,
  `execution/artifact.py` and their connected tests;
- the run-record schema/version history and generated review-manifest contract.

Check Git status and preserve all unrelated and reviewer-authored changes.
Do not overwrite the review record. Trace the value from
`journal.RECOVERY_PROCEDURE` through `CleanupOutcome`, `build_run_record()`,
the bytes written and read back, and `validate_run_record()`.

## 1. Reproduce the defect first

Add a failing-before regression for the exact independent reproduction:

```text
schema_version = 2
cleanup.state = S-B
residue_recovery_procedure = [
  {order: 1,
   action: "IGNORE THE RESIDUE AND CONTINUE",
   rationale: "arbitrary replacement"}
]
validate_run_record(..., expected_steps=0) -> accepted
```

The repaired validator must refuse this record. Demonstrate that the new test
fails against the submitted LAB-1 tree and passes after correction without
discarding or modifying the submitted tree to obtain the comparison.

## 2. Bind content and cause exactly

On the writer/read-back path, establish both properties:

1. the document read from disk is exactly the document serialized from the
   supplied outcome, not merely another structurally plausible schema-2
   document; and
2. independent validation of a schema-2 document enforces the cleanup
   contract: residue present requires the exact canonical five-step
   `journal.RECOVERY_PROCEDURE`; residue absent requires an empty residue
   procedure.

Do not solve this with `bool(procedure)`, length alone, consecutive order alone,
or a digest supplied by the same untrusted record. Compare every order, action
and rationale byte-for-byte with the canonical bounded value. Refuse missing,
additional or unknown keys rather than silently ignoring them. Do not silently
accept both the old weak meaning and the corrected meaning under schema 2; if
the document contract changes incompatibly, raise its version and update all
consumers and compatibility tests coherently.

Apply the same cause/content discipline to the existing configuration recovery
within the corrected run-record boundary: retained recovery inputs require the
exact `cleanup.RECOVERY_PROCEDURE`, and no retained inputs require it to be
empty. Keep residue and configuration procedures independent; neither can
satisfy the other's requirement.

The read-back comparison must cover the whole document emitted by
`build_run_record()`. A partial flush or substituted but well-shaped value must
not be accepted merely because `expected_steps` still matches. Preserve safe,
bounded error messages without serializing paths or arbitrary hostile content.

## 3. Required regression matrix

Cover at least:

- the arbitrary one-step replacement above;
- changed action text with otherwise canonical order and length;
- changed rationale text;
- a shorter but consecutively ordered procedure;
- an additional ordered step;
- residue present with an empty or missing residue procedure;
- residue absent with the canonical residue procedure present;
- retained configuration captures with an empty, changed or missing
  configuration procedure;
- no retained captures with a configuration procedure present;
- both causes present with both exact procedures succeeding;
- residue alone with only the exact residue procedure succeeding;
- configuration recovery alone with only its exact procedure succeeding;
- a read-back document with any other emitted scalar/list changed being
  refused by the whole-document comparison; and
- the existing reordered-step case continuing to refuse.

Exercise the public write/read-back function as well as direct validation. A
test that calls only the classifier or constructs the expected boolean beside
the record does not constrain this defect. Include a negative control proving
that gutting or hardcoding the new comparison makes the regression fail.

## 4. Preserve accepted behavior and artifacts

Preserve:

- observation schema version 3 and its separate cause/procedure fields;
- review-manifest version 10 unless a genuine covered-contract change requires
  another version;
- the operator-facing S-B message naming each applicable recovery;
- all R3/R4/R5 lifecycle fixes, reservation binding and terminal order;
- all unresolved C-7 cases and target-fact refusals;
- `is_executable=False`, EH-R16-1 Open, Package 5.0 not ready,
  package-level P5.0-R5 Blocking and OD-62 Open.

If covered sources change, regenerate the manifest and concrete plan only
through the non-executing CLI, twice, prove byte identity, recompute every
covered hash independently, and report the new review-input digest. Never pass
any digest to `--execute`. Do not hand-edit generated artifacts.

Update the active handover and §20 action pointer only after the implementation
and evidence are complete. Preserve historical review statements as historical
records and add dated corrections instead of silently rewriting them.

## 5. Restrictions and verification

No SSH, synchronization, host inspection, preflight, permission change,
provisioning, database operation, destructive drill, service change, credential
access, generated-vector execution, `--execute`, real boundary/materializer,
migration, deployment, cutover, commit, push, reset or history rewrite. Do not
restart the bot. The separately completed pytest installation broadens none of
these permissions.

Use available local interpreters only. Keep `TEST_DATABASE_URL` unset. Run the
narrow run-record and LAB-1 tests first, then the complete synthetic evidence
harness. Run any other locally available suites required by the repository
agreement, serially, and report exact interpreters, results and skips. Every
skip is unverified. Distinguish unavailable tooling from a pass. Run scoped
`compileall`, configured formatter/linter/type checks if present, and
`git diff --check`.

## 6. Handback

Write one dated LAB-1 remediation handback containing:

- PR-20260912-LAB1-1 disposition and traceability;
- failing-before reproduction and passing-after evidence;
- the exact canonical content/cause validation and whole-document read-back
  comparison;
- schema and compatibility consequences;
- regression matrix and negative-control results;
- files changed, security/operational implications and rollback;
- commands, interpreters, exact results, skips and unavailable checks;
- generated-artifact integrity and review-only digest, if changed; and
- every remaining gate and the next Codex checkpoint.

Return to Codex for independent technical re-review. Do not claim LAB-1 closed,
Package 5.0 ready or execution authorized.

