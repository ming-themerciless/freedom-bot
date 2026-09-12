# Claude remediation prompt — R14 ownership baseline correction

Work in `/opt/freedom-blades/platform`.

Read completely `.agents/AGENTS.md`, `docs/implementation-plan.md` and
`docs/operations/disposable-test-server.md` before planning. Then read the
current handover, R13.2 handback, R14 independent review, applicable package
plan requirements and affected harness code/tests. Check git status and preserve
the dirty worktree. Do not stage, commit, reset or alter unrelated work.

## Bounded task

Fix **EH-R14-1**, the remaining Blocking ownership defect documented in
`phase-5-0-evidence-harness-r14-independent-review.md`.

`R-B-DB` accepts a connection failure as proof of database absence. With a
pre-existing database that refuses connections, the control connection to
`postgres` succeeds, the baseline grants ownership, `B6-03` fails to create the
existing database and `CL-08` drops it. The independent injected fake
reproduction confirms this path. Do not close EH-R13-1 yourself.

1. Add regression coverage before changing implementation. Seed a pre-existing
   database, make its connection probe return 2 while the control succeeds,
   and make creation return 3. Record the current erroneous deletion.
2. Require a successful, bounded, explicit existence observation before
   granting ownership. Distinguish absent, present and unknown. Unknown must
   stop before mutations and must never authorize deletion.
3. Audit every ownership baseline for the same error. In particular, generic
   `SET ROLE` failure and generic `stat` failure are not unique absence results.
   Add meaningful error-state tests as well as present/absent tests. Do not
   model every failed read as an absent object in the fake.
4. Use the existing approved grammar and bounded observation interfaces. If a
   trustworthy check cannot be expressed within them, explicitly block that
   baseline and document the exact design decision needed. Do not broaden the
   grammar, add a shell, or parse unrestricted host error text to force success.
5. Preserve attempt-aware cleanup and unknown-launch recovery for genuinely
   owned objects. Preserve pre-existing/unreached objects, recovery-capture
   retention, semantic observation contracts and honest persistence reporting.
6. Regenerate the manifest and rendered plan; verify source coverage, exact
   reproduction and changed vectors. A new digest identifies review input and
   grants no execution authority.

## Boundaries

This authorizes local synthetic scaffolding remediation only. Do not use SSH,
inspect oracle-test, run generated vectors or `--execute`, arm a real process
boundary/materializer, perform database operations or run the destructive
backup/restore drill. Keep `TEST_DATABASE_URL` unset. Do not infer permission
for these actions from general disposable-server administrative access.

Keep C-6/C-7 explicitly unresolved and all twelve unsupplied target facts
unconfirmed. Do not add immutable-flag operations, Band 7 ingestion, invent
observations or approve narrower execution scope. Those remain separate review
decisions. Do not require zero unresolved items as a cosmetic acceptance test.

Package 5.0 remains not ready, P5.0-R5 Blocking and OD-62 Open. No product
implementation, migration 0014, deployment, cutover or Package 5.1+ is authorized.

## Validation and handback

Run the structural no-execution suite first, the new failing regressions before
the fix, then focused and complete synthetic harness suites after the fix.
Use an available local interpreter only as an explicitly reported fallback;
the canonical oracle-test interpreter path is not proof of local availability.
Do not contact the target to satisfy an environment instruction. Report skipped
integration suites and the restriction; do not reuse earlier passing totals.

Run `git diff --check`. Report configured tooling honestly. Verify generated
manifest bytes and rendered plan against independent regeneration.

Provide a handback with the conceded defect, exact pre-fix evidence, changed
files, baseline-by-baseline proof obligations, post-fix tests, remaining design
decisions and operational restrictions. Return to Codex for independent review;
do not claim findings closed or execution approved.
