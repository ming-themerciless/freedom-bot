# Claude prompt — implement the chosen I3 target-identity model — 2026-09-20

Authorization: **C-P5.0-LAB-I3-R5**. Peter Duscha assigns Claude one bounded,
repository-only implementation pass for the accepted target-identity decision.
Codex remains the Independent Technical and Security Reviewer and must review
the completed reconciliation before any operational retry may be authorized.

## Governing decision

Implement Option A exactly:

- keep `host="oracle-test"` as the operational SSH alias used by the runbook,
  planner and operator-facing records;
- add a separately named approved kernel-nodename fact with the exact value
  `Test`; and
- compare `os.uname().nodename` with that nodename fact during I3 admission,
  while continuing to compare the observed kernel release and architecture
  with their separately approved facts.

Do not rename the host, change the alias, or redefine `host` to mean nodename.

## Required reading

Before changing anything, read completely and obey:

1. `.agents/AGENTS.md`;
2. the implementation-plan reading map and §§0, 12 (Package 5.0), 13, 14, 16,
   17 and 20;
3. `docs/review/Handover information` and the current restriction in
   `docs/operations/disposable-test-server.md`;
4. the maintainer target-identity decision;
5. the R4 operational handback and E1 evidence-precision correction;
6. runner contract r6, especially target identity and I3 admission;
7. `approved_target.py`, `review_manifest.py`, `concrete_plan.py`,
   `execution/i3_verifier.py`, `execution/i3_verifier_cli.py` and all tests for
   approved target facts, identity, manifests, confirmation and I3 admission;
8. the current status, RAID, decision and change registers.

Inspect Git status and preserve every unrelated, earlier-pass and
reviewer-authored change. Never read, print, transfer or modify a secret file.

## Required implementation

1. Extend the canonical approved-target facts with one explicitly named
   nodename field whose value is `Test`. Keep ordering deterministic and include
   the field in the canonical identity material.
2. Change I3 admission so the probe tuple is compared, in order, with approved
   nodename, active kernel and architecture. Do not weaken any other admission
   check or safe-output rule.
3. Update comments and documentation that imply the SSH alias is observed
   through `os.uname()`.
4. Add focused regression coverage proving at least that:
   - `("Test", "7.0.0-31-generic", "x86_64")` passes the target-identity
     portion of admission;
   - substituting `oracle-test` for nodename refuses with `target-mismatch`;
   - a wrong nodename, release or architecture still fails closed;
   - operational `host` remains `oracle-test` and nodename is separately `Test`;
   - nodename participates in the target-identity digest, confirmation token
     and manifest identity facts.
5. Reconcile runner contract r6 and every generated/review artifact whose
   source contract changes. Use deterministic generation; do not hand-edit
   generated output. Apply the established manifest-version rule and report
   whether and why the version changes.
6. Record the new full target-identity digest, confirmation token and
   review-input digest as review input only, never approval or authority.
7. Update the handover and controlled registers to say implementation is
   complete and awaiting independent review. Do not claim I3 confirmed, close
   a review finding, or authorize an operational retry.

## Verification

Run repository-local checks only, with `TEST_DATABASE_URL` explicitly unset:

- focused approved-target, manifest and I3-verifier tests;
- the complete `tests/phase_5_0_evidence` suite;
- `.claude/hooks/test_guards.py`;
- Python compilation for changed Python modules;
- deterministic artifact regeneration and byte-for-byte comparison; and
- `git diff --check`.

Report exact commands, pass/fail/skip counts and checks not run. Do not reuse an
earlier suite figure as evidence for the changed tree.

## Prohibited actions

This pass is repository-only. Do **not** use SSH or access `oracle-test`; do not
synchronize, inspect or mutate the host; do not delete or inspect the two
`/tmp` capture files; do not invoke the I3 verifier operationally; and do not
perform a controlled write, initialize V7, wire a participant, invoke the
evidence harness, execute a generated vector, access a database, use a real
boundary/materializer or pass `--execute`.

Stop and return without working around any guard refusal, unexpected generated
change, ambiguous contract, secret exposure, unrelated-tree conflict or scope
expansion.

## Handback

Return one implementation handback for independent Codex review containing the
exact changes; old and new identity/digest relationships; tests and generation
evidence; security implications; checks not run; confirmation that no host
action occurred; and reviewer questions about semantics, fail-closed admission,
identity hashing, manifest/version reconciliation and artifact determinism.

Nothing in the handback closes review, approves a digest, advances a gate or
authorizes an operational retry.
