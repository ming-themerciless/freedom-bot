# Gemini Step 2 — reproduce lifecycle races with failing tests

This is a test-only characterization step. Its intended result is a small set of
deterministic failing tests. Do not modify production code or status records.

Proceed only after Codex accepts Step 1. Read the global step plan, current
`workflow.js`, its tests, and the accepted Step 1 walkthrough.

Add production-path tests using deferred promises and concurrent
`executeWorkflow()` calls. Prewarm `PreparedSnapshotState` so concurrent calls
reuse the exact same cached prepared object and generation. Do not call
`setConfirmed`, `setPinnedRetry`, or `clear` directly to simulate a workflow
outcome.

Required interleavings:

1. Same cached payload: newer successful submission completes, then the older
   definitive refusal completes. Success must remain reusable; current code is
   expected to end `empty`.
2. Same cached payload: newer success completes, then the older retryable or
   indeterminate failure completes. The stale failure must not repin over the
   confirmed success.
3. Same cached payload: newer pinned failure completes, then an older success
   completes. Define and assert the intended latest-operation-wins behavior;
   the older success must not overwrite the newer pin.
4. Operator explicitly discards a pinned retry and begins fresh preparation
   while an older request is still in flight. The older completion must not
   restore, clear or repin discarded state.
5. The fresh preparation in case 4 fails locally before producing a new
   prepared snapshot. The discarded attempt must remain invalidated; an older
   completion must not resurrect it.
6. Different prepared payloads overlap. Retain the existing protection and
   prove it through `executeWorkflow()`, not direct state mutation.

Test requirements:

- Control completion order explicitly; do not depend on timers or scheduler
  luck.
- Assert strict prepared-object identity, state status, selected folder,
  checksum, generation/token, outbound body and `Idempotency-Key` where
  applicable.
- Add a timeout guard so a broken test fails instead of hanging.
- Do not encode the solution into test helpers.
- Keep the failures limited to the known concurrency defect. If another failure
  appears, document it and stop.

Run the focused tests and complete Node suite. Record the exact failing test
names and assertion differences. Do not make them pass in this step. Syntax and
`git diff --check` must still pass.

End with:

`Step 2 complete: concurrency defect reproduced by deterministic failing tests; production code unchanged; awaiting Codex review before implementation.`
