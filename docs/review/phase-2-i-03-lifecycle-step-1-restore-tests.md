# Gemini Step 1 — restore removed lifecycle regressions

Work only on test restoration. Do not modify production code or controlled
status records in this step.

Read the global rules in
`docs/review/phase-2-i-03-lifecycle-remediation-step-plan.md`, then read:

- `foundry-module/tests/workflow.test.mjs`;
- `foundry-module/scripts/workflow.js` only for API context;
- the current Gemini walkthrough at
  `/home/foundry/.gemini/antigravity-ide/brain/334951f5-c84a-4eb3-b5f0-92105043951f/walkthrough.md`;
- the prior Codex review supplied by the maintainer.

Restore the eight regression cases removed when the suite fell from 110 to 106:

1. timeout/network failure followed by retry resends exact prepared identity,
   bytes, checksum, timestamp and idempotency key;
2. changed world while an unconfirmed retry is pinned, followed by explicit
   operator discard and fresh preparation;
3. meaningful Actor or embedded Item change invalidates reuse;
4. relevant Folder/export-scope change invalidates reuse;
5. switching selected folders does not reuse the prior folder snapshot;
6. download followed by submission reuses unchanged prepared bytes;
7. the cache remains strictly bounded to one entry through folder switches;
8. credentials never enter prepared or cached state and are not retained by the
   test harness after submission.

Use the last known versions of these tests where available in Gemini history or
the current conversation context. Otherwise reconstruct them from the behavior
described above. Prefer `executeWorkflow()` for retry/discard orchestration, but
do not change production code merely to make a test convenient.

Requirements:

- Assertions must verify behavior, not only test names or status strings.
- Use synthetic fixtures and fixed clocks.
- Do not weaken, delete, merge, skip or rename away an existing test.
- Do not add race-fix tests yet; those belong to Step 2.
- The expected total is the current 106 plus eight restored tests, unless a
  table-driven reconstruction produces a transparently explained equivalent
  count with all eight behaviors independently attributable.

Run:

```bash
(cd foundry-module && node --test tests/*.test.mjs)
for file in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do
  node --check "$file"
done
git diff --check
git status --short
```

Stop after the tests pass. The walkthrough must list each restored behavior,
the exact test name, fresh totals, and confirmation that no production or
controlled-status file changed. End with:

`Step 1 complete: removed regression coverage restored; production behavior unchanged; awaiting Codex review.`
