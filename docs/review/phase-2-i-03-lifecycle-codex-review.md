# Independent Codex review — Foundry module PreparedSnapshot lifecycle

Date: 2026-08-08
Reviewer: Codex, independent reviewer
Reviewed state: `foundry-module/` at `f632722` on `docs/platform-plan`
Decision authority: Peter Duscha

## Recommendation

Do not accept the lifecycle remediation yet. I independently reproduced F-1 through F-5. F-1 and F-5 are Blocking under implementation plan §16.4 because each can lose the only reusable bytes/key for an indeterminate or already-recorded request and allow a later submission to create a second pending artifact. F-2 through F-4 are Important. The missing Foundry installation and supervised rehearsal remain separate acceptance-evidence gaps.

This is a review only. I changed no module or server implementation.

## Findings

### Blocking

#### C-B-1 — `original_result_unavailable` discards a spent idempotency key (confirms F-1)

`classifyFailureDisposition` treats the 409 as a definitive 4xx refusal (`workflow.js:180-188`); `executeWorkflow` consequently clears the prepared entry (`workflow.js:483-498`). The next preparation includes a new `exportedAt` (`workflow.js:285-297`), changing the checksum-derived key. My isolated reproduction observed an empty state after the 409 and unequal first and second `Idempotency-Key` values.

The server's `original_result_unavailable` means the key has already been spent but its stored receipt cannot be returned. Losing the original key defeats the documented no-second-artifact guarantee. Blocking is the correct severity despite the branch being uncommon: impact, not frequency, controls the §16.4 classification.

Required direction: classify `original_result_unavailable`, like `concurrent_submission`, as retry-same-key; do not reclassify every 409 because `request_key_conflict` requires a new key.

#### C-B-2 — overlapping submissions and page reload can lose an indeterminate delivery (confirms and upgrades F-5)

Every click starts another dialog (`main.js:69-80`) and every workflow makes itself the current state authority (`workflow.js:85-92`). With different payloads, a newer operation can complete and the older operation's later `setPinnedRetry` fails its token check (`workflow.js:120-130`, `:483-495`). The return value is ignored. My reproduction completed the newer payload successfully, failed the older request after dispatch, and observed no pin for the older bytes/key.

This is Blocking, not Important: after an indeterminate delivery the application has discarded the only same-key retry material and can create a duplicate pending artifact. Guarding only the button is insufficient unless every callable workflow entry also has an explicit concurrency contract or safely retains all uncertain deliveries.

The module-level state is also memory-only (`main.js:63`). Reloading the page after an indeterminate delivery loses the pin and has the same duplicate-artifact consequence. Either provide appropriately protected durable recovery or narrow the operator guarantee and provide a server-side recovery workflow that prevents a fresh key from duplicating the unresolved submission. The current operations text overstates page-lifetime state.

### Important

#### C-I-1 — response code precedes HTTP status in failure policy (confirms F-2)

At `workflow.js:166-179`, unvalidated response codes are checked before `status` at `:180`. I reproduced `400 + timeout -> delivery_indeterminate` and `400 + missing_credential -> local_refusal`. This contradicts the documented status-first table and the remediation's one-code-override claim.

Evaluate response status first for post-dispatch server responses, with an explicit bounded exception set for the two same-key 409 outcomes. Locally generated pre-dispatch errors have no status and can then use their local codes.

#### C-I-2 — unbounded response fields reach operator notifications (confirms F-3)

`transport.js:209-218` copies `receipt.error.code` without validation and `main.js:347-355` renders it. I reproduced a sentence-length phishing instruction as the displayed code. On success, `describeReceipt` interpolates unvalidated `actor_count` (`workflow.js:525-535`); I reproduced the same content there.

This is Important rather than Blocking on the reviewed threat model. A compromised submission endpoint already receives the bearer credential used for that request, but untrusted response text remains a social-engineering and UI-integrity surface and can solicit other credentials or actions. Allowlist stable error codes with a bounded fallback; validate successful receipt shape and render actor count only as a bounded non-negative integer. See the separate security review.

#### C-I-3 — a pin makes fallback download folder-blind (confirms F-4)

`prepareSnapshot` returns the pin before reading `folderId` (`workflow.js:249-264`). My reproduction pinned the active folder, requested a fallback download for the inactive folder, and received the active-folder artifact. The notification later identifies the actual folder, but the dialog warning discusses submitting only (`main.js:204-210`) and the only discard action immediately submits (`main.js:103-127`).

Preserve the pin invariant, but add a non-submitting explicit discard-and-download path with a clear confirmation naming the discarded uncertain delivery and selected folder. Silently scoping pins by folder would make it too easy to abandon an unresolved request.

### Optional / test and contract cleanup

- F-6 confirmed: standalone `discardPinned` can silently fail while a workflow is active because `startStandaloneOperation()` returns `null`. Classify Optional while unreachable from the UI, but make the exported API report refusal rather than pretend discard succeeded.
- F-7 confirmed: preparation sets `confirmed-reusable` (`workflow.js:310-312`), while the operations guide says successful submission does so. Classify Important documentation/state-contract mismatch; rename the state or correct the guide and tests.
- F-8 confirmed: the state credential assertion checks the literal word `secret`, not the actual credential. Classify Important test weakness because credential non-retention is a security claim, although code inspection did not find retention.
- F-9 and F-10 confirmed as Optional latent state-machine asymmetries. The pinned early return skips standalone finish, and standalone tokens are not entered in `_activeOperations`.
- F-11 confirmed as Optional. A synchronous `fetch` refusal is conservatively treated as post-dispatch. Safety is preserved, but the diagnostic can be inaccurate.

## Items cleared

I agree with the handoff that remediation claims 1, 2, 5 and 6 hold for the tested production paths. Operation-token checks prevent stale completions from overwriting newer state, and the download path preserves an existing pin. No credential was found in prepared or cached state.

Those properties do not resolve C-B-2: rejecting a stale state mutation is safe only when the stale completion does not carry a distinct indeterminate delivery that must remain retryable.

## Evidence

- `node --check scripts/*.js` — passed for all seven module scripts.
- `node --test foundry-module/tests/*.test.mjs` from repository root — 126 passed, 0 failed.
- Temporary isolated reproduction — 8 assertions passed, covering F-1 through F-5; the temporary file was removed and is not part of the repository.
- Read-only inspection of commit `f632722`, the server error semantics, operations guide, and implementation plan §§6.4, 6.5, Phase 2, and 16.4.

No Foundry installation, live world, credential, endpoint, PostgreSQL service, or supervised rehearsal was used. Those are not needed to reproduce these defects and remain outstanding gate evidence.

## Re-review focus

The remediation should add regression coverage for both spent-key 409 codes, adversarial code/status combinations, bounded refusal and success receipt fields, discard-and-download, cross-payload older-indeterminate/newer-completion races, and page reload/recovery semantics. Re-review must establish that every possibly dispatched request retains or can recover its exact bytes and key until the server outcome is definitive.
