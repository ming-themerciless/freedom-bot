# Claude independent re-review request — PreparedSnapshot lifecycle 1.0.3

Prepared: 2026-08-08

## Role

Act as the independent implementation and security reviewer. Do not implement
or approve the package. Verify or refute the fixes, classify findings under
implementation plan §16.4, and give Peter Duscha an acceptance recommendation.

Read `.agents/AGENTS.md`, `docs/implementation-plan.md`, the two 2026-08-08
Codex lifecycle reviews, and the remediation commit before reviewing.

## Baseline and scope

- Reviewed defective module baseline: `f632722`, version 1.0.2.
- Remediation: version 1.0.3 in the commit immediately following the review and
  governance checkpoint `306063e`.
- Primary files: `foundry-module/scripts/{workflow,transport,main}.js`, their
  tests, and `docs/operations/foundry-snapshot-submission.md`.
- Phase 2 server checkpoint `6db51e7` is context, not a request to re-review the
  complete server package.
- Do not access Foundry, real exports, credentials, production services, or the
  excluded `docs/screenshots/` files.

## Claimed resolutions to verify

1. `409 original_result_unavailable` now pins and retries the exact same bytes,
   checksum and idempotency key; `request_key_conflict` remains definitive.
2. HTTP status is evaluated before server-supplied code, with only
   `concurrent_submission` and `original_result_unavailable` overriding a 4xx
   into same-key retry.
3. The UI permits only one dialog/workflow at a time, preventing the reachable
   cross-payload overlap that discarded an older indeterminate delivery.
4. Unknown response codes are replaced by `submission_refused`; successful
   receipt checksum, Actor count and duplicate flag are validated before state
   is confirmed. Invalid success receipts are delivery-indeterminate and pin.
5. A pin can be explicitly discarded into a non-submitting download of the
   selected folder. Ordinary download still preserves the pin.
6. Standalone `discardPinned:true` during a live workflow now refuses visibly.
7. The credential non-retention test searches for the actual credential value.
8. Documentation correctly says preparation creates the reusable cache.

## Explicit residual decision — page reload

Version 1.0.3 does not persist raw snapshot bytes or keys in a Foundry setting,
browser storage or other client-readable durable store. The UI and operations
guide now state that the pin lasts only for the current page load and instruct
the operator not to reload; after an accidental reload they must stop and ask
the platform operator to reconcile rather than submit under a new key.

Please decide explicitly whether that fail-operational boundary is acceptable
for this supervised Phase 2 module or whether the lack of durable client retry
material remains Blocking. If it remains Blocking, identify a resolution that
does not violate the accepted rule against storing sensitive snapshot bytes or
reusable credentials in client-readable Foundry configuration. Do not silently
assume browser storage is safe.

## Required checks

Run from `foundry-module/`:

```text
for file in scripts/*.js; do node --check "$file"; done
node --test tests/*.test.mjs
```

Also reproduce adversarial status/code pairs, the spent-key 409 transition,
hostile error code and Actor-count rendering attempts, selected-folder
discard-and-download, and the UI overlap guard. Review the diff for any claim
that a retry guarantee survives page reload.

Write the result to:

- `docs/review/phase-2-i-03-lifecycle-1.0.3-claude-review.md`
- `docs/review/phase-2-i-03-lifecycle-1.0.3-claude-security-review.md`

Do not modify implementation files.
