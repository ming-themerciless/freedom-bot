# Gemini Step 3 — implement the minimal per-operation race fix

Proceed only after Codex accepts the failing tests from Step 2. Modify only the
smallest production and test surface required to make those tests pass.

The current defect is that `prepared.generation` identifies a cached payload,
not an individual workflow attempt. Concurrent attempts reusing that payload
therefore share a generation and can overwrite one another's state.

Required semantics:

- Give each `executeWorkflow()` invocation a distinct monotonic operation token
  before any asynchronous preparation or dispatch can allow an older outcome to
  race back in.
- Prepared payload identity remains separate. Reusing content must still reuse
  the exact object, bytes, checksum, `exportedAt`, fingerprint and idempotency
  key.
- Only the currently authoritative operation may confirm, pin, clear or discard
  lifecycle state.
- Explicit discard immediately invalidates every older operation, even if fresh
  preparation subsequently fails.
- Latest-operation-wins must be documented precisely. Do not use wall-clock
  time or promise completion order as authority.
- State remains bounded to one prepared payload plus constant-size counters or
  tokens. Store no credential, error, receipt or history.
- Counter wraparound must not silently make an ancient operation current. Use a
  safe integer guard or an opaque identity token with bounded retention.
- Keep state mutation encapsulated; tests must not need `_entry` access.

Do not serialize by disabling the UI unless Codex and the maintainer explicitly
approve that product change. Do not clone/re-encode cached payloads, remove
`exportedAt`, randomize keys, or expand storage beyond one entry.

Make every Step 1 test and every Step 2 race test pass. Replace the old direct
mutator race test with production-path coverage if it has become redundant; do
not reduce behavioral coverage.

Run:

```bash
(cd foundry-module && node --test tests/*.test.mjs)
for file in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do
  node --check "$file"
done
git diff --check
git status --short
```

The walkthrough must include a compact state/operation transition table and
map every Step 2 failure to the passing assertion. Do not update controlled
project status yet. End with:

`Step 3 implementation complete locally; race tests and restored regressions pass; awaiting Codex implementation review.`
