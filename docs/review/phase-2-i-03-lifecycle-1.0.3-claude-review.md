# Independent Claude review — PreparedSnapshot lifecycle 1.0.3

Date: 2026-08-08
Reviewer: Claude, independent implementation reviewer
Reviewed state: `foundry-module/` at `75c7f47`, version 1.0.3
Baseline: `f632722`, version 1.0.2
Decision authority: Peter Duscha

## Recommendation

Do not accept 1.0.3 yet. Seven of the eight claimed resolutions hold as stated
and one holds only in part. The remediation is a genuine improvement on the
defective baseline: C-B-1, C-I-1, C-I-3, F-6, F-7 and F-8 are resolved, and
C-B-2 is closed on every path reachable from the user interface.

One Blocking finding is open. The status-first rule of claim 2 was applied to
two codes that are not server-supplied facts — `malformed_response`, which the
client generates when it *cannot read* the server's answer, and
`submission_refused`, the fallback for a code the new allowlist does not
recognise. On a 409 either of those now produces a definitive refusal and
discards the retry material for a key the server may already have spent. That
is C-B-1's consequence reached through a different door, and it is reachable
without any adversary.

On the explicit page-reload question I rule **not Blocking, conditional** — see
§ Residual decision. The conditions are documentation and rehearsal evidence,
not code, and they do not require storing snapshot bytes anywhere on the client.

This is a review only. I changed no implementation, test or configuration file.

## Verification of the claimed resolutions

| # | Claim | Verdict |
|---|---|---|
| 1 | `original_result_unavailable` pins and retries identical bytes/key | **Holds** |
| 2 | HTTP status evaluated before server-supplied code | **Holds in part** — see CL-B-1 |
| 3 | UI permits one dialog/workflow at a time | **Holds** for the UI; see CL-O-3 |
| 4 | Unknown codes bounded; success receipt validated before confirmation | **Holds**; allowlist contents are wrong — see CL-I-1 |
| 5 | Explicit discard into a non-submitting download; ordinary download preserves the pin | **Holds** |
| 6 | Standalone `discardPinned` during a live workflow refuses visibly | **Holds** |
| 7 | Credential non-retention test searches the actual credential value | **Holds** |
| 8 | Documentation says preparation creates the reusable cache | **Holds** |

Claim 1 is the important one and it is properly done. I reproduced the 409
`original_result_unavailable`, confirmed the entry pins, then retried against a
freshly constructed world and a later clock: the second request carried a
byte-identical payload, the same checksum and the same `Idempotency-Key`
(R-1). `request_key_conflict` remains definitive and clears (R-2).
`prepareSnapshot` returns the pinned entry before it reads the world
(`workflow.js:268-270`), which is what makes the guarantee hold across an
intervening world edit.

Claim 3 holds further than the diff alone shows. `openSubmissionDialog`
(`main.js:96-105`) holds `submissionDialogOpen` across `await
openSubmissionDialogOnce()`, and that function awaits `run(...)`
(`main.js:197-199`), which awaits the whole `executeWorkflow` prepare → dispatch
→ state-transition sequence. The flag therefore covers the entire critical
section, not just the dialog. The module registers no `api` object on
`game.modules.get(MODULE_ID)` and exports nothing from `main.js`, so the button
is the only entry point a world can reach. The reachable cross-payload overlap
is closed.

## Findings

### Blocking

#### CL-B-1 — an unidentifiable 409 discards a possibly-spent idempotency key

`classifyFailureDisposition` now branches on `error.status` first
(`workflow.js:168-182`). The comment states the principle correctly — "a
response status is a transport fact… server-supplied codes must never turn a
definitive 4xx refusal into a local or indeterminate failure" — but the branch
does not distinguish server-supplied codes from the client's own.

Two codes reaching that branch are not server facts:

- **`malformed_response`** (`transport.js:239-244`) is raised when
  `response.json()` throws. Its meaning is precisely *"I could not determine
  what the server said."* On a 409 it is now classified `DEFINITIVE_REFUSAL` and
  `executeWorkflow` clears the entry (`workflow.js:509`). Under 1.0.2 the code
  check ran first and this pinned.
- **`submission_refused`** is what `boundedRefusalCode` returns for any code the
  new allowlist does not recognise (`transport.js:89-93`), including an absent
  or wrongly-shaped `error.code`. It is a client-side stand-in for an unread
  value, not something the server said.

I reproduced both. A 409 with an unparseable body leaves the state `empty`
(R-8). So does a 409 whose body is valid JSON but not the service's error shape
— `{}`, `{"message":"conflict"}`, `{"error":{}}`, and `{"error":{"code":42}}`
all discard the entry (R-16). A non-JSON **2xx** still pins correctly (R-8b),
which confirms the defect is specific to the 4xx branch rather than to receipt
handling generally.

Why this is Blocking rather than Important. On this service a 409 is never
ambiguous about whether the key has a history: `_REFUSAL_STATUS`
(`adapters/http/wsgi.py:146-151`) maps exactly three codes to 409, and two of
them — `concurrent_submission` and `original_result_unavailable` — mean the key
is spent. Discarding the entry on a 409 the client could not identify therefore
destroys the only same-key retry material for a request that may already hold a
pending artifact, and the operator's next submission prepares fresh bytes with a
new `exportedAt`, a new checksum and a new key. That is the second pending
artifact the idempotency design exists to prevent — the same impact Codex
classified Blocking for C-B-1, and §16.4 classifies by impact rather than
frequency.

Nor is the trigger exotic. It needs only an intermediary that does not pass the
service's JSON error body through unchanged: an ingress with
`proxy_intercept_errors on`, a CDN or WAF error page, or an API gateway that
normalises upstream errors. In such a deployment *every* `concurrent_submission`
and `original_result_unavailable` would arrive unidentifiable, making the loss
systematic rather than incidental. The deployment topology is not yet
established, which is itself a reason not to rely on it.

Required direction. Keep status-first, but apply it only to codes the server
actually supplied. Two adjustments, both narrow:

1. A `malformed_response` is delivery-indeterminate at any status. The client
   did not read a refusal; it failed to read anything.
2. On 409, invert the default: `DEFINITIVE_REFUSAL` only for a positively
   identified `request_key_conflict`, and `RETRY_SAME_KEY` for anything else.
   Resending the same key when the server already holds its result is safe by
   the contract's own definition; discarding it when the server does hold a
   result is not. `invalid_request_key` is a 400 on this service, so this
   inversion costs nothing outside 409.

Regression coverage should include the four unidentifiable 409 shapes above and
the non-JSON 409, asserting the entry survives in each.

### Important

#### CL-I-1 — the refusal allowlist does not match the server contract

`SERVER_REFUSAL_CODES` (`transport.js:71-87`) is a hand-maintained copy of a
contract it was never checked against, and it is wrong in both directions.

Reachable on the submission path and **missing** from the allowlist, so
suppressed to `submission_refused`:

| Status | Code | Source |
|---|---|---|
| 403 | `out_of_scope` | `application/service_principals.py:88-91` |
| 411 | `length_required` | `adapters/http/wsgi.py:325` |
| 413 | `artifact_too_large` | `adapters/http/wsgi.py:342` |
| 415 | `unsupported_media_type` | `adapters/http/wsgi.py:305` |
| 400 | `missing_idempotency_key` | `adapters/http/wsgi.py:312` |
| 400 | `malformed_length` | `adapters/http/wsgi.py:334, :338` |
| 400 | `incomplete_body` | `adapters/http/wsgi.py:368` |

I confirmed all of these render as `submission_refused` (R-13). The first three
are named in this repository's own operator troubleshooting table
(`docs/operations/foundry-snapshot-submission.md:664-672`), so the guide now
instructs an operator to read a code the module has stopped showing them.
`artifact_too_large` and `out_of_scope` are the two most common recoverable
misconfigurations, and both are now indistinguishable from every other refusal.

**Spurious** entries — not emitted by this service on this path:
`authentication_unavailable` (preview route only,
`adapters/http/wsgi.py:414-421`); `unauthorized` (the real code is
`out_of_scope`); and `unsupported_deployment`, which is the *client's own*
`bundle.js:104` refusal. Admitting a client code into a server-code allowlist
lets a compromised endpoint present a refusal that reads as one of the module's
local safety checks. See the security review.

Required direction: derive the allowlist from `REFUSAL_CODES`
(`application/foundry/submission.py:110-130`) plus the boundary codes in
`wsgi.py`, remove the three that do not belong, and add a test that fails when
the two lists diverge. The service already has this pattern — the AST walk that
holds `ARTIFACT_REFUSAL_CODES` to the parser's actual codes.

#### CL-I-2 — the reload caution is shown after the window of risk opens

The reload warning lives in `buildDialogContent` and is appended only when
`hasPinnedRetry` is already true (`main.js:230-240`). The operator therefore
first reads "do not reload this page" when they *reopen* the dialog — which is
after the indeterminate delivery, and after the reload risk has been live for
however long they spent deciding what to do.

The notification they actually see at the moment the pin is created comes from
`notifyFailure` (`main.js:376-389`) rendering the transport message: "The
submission timed out. Nothing was confirmed. Submitting again with the same
export is safe: a retry cannot create a second snapshot"
(`transport.js:224-226`). Every word is true and none of it warns that the same
export ceases to exist if the page reloads. Given that the accepted design makes
operator discipline the control, the caution belongs on the indeterminate-failure
notification itself.

#### CL-I-3 — the documented recovery instruction points at a procedure that does not exist

The guide now tells the operator that after an accidental reload they must "stop
rather than submitting current state under a new key and ask the platform
operator to reconcile the earlier request"
(`docs/operations/foundry-snapshot-submission.md:1045-1047`). Nothing in the
guide says what that reconciliation is. `grep -i reconcil` over the document
returns this sentence and one unrelated Phase 3 preview step at line 819.

The route that might answer the question is disabled in this deployment: the
preview service is `None` until a Phase 3 authenticated boundary exists, and the
endpoint answers `503 authentication_unavailable`
(`adapters/http/wsgi.py:414-421`). `tools/snapshot_api.py` is a development
server, not a query tool. So the instruction currently resolves to an
undocumented manual database inspection.

This matters more than an ordinary documentation gap, because it is the entire
mitigation on which the page-reload boundary rests. Required direction: document
the concrete procedure — the query against `foundry_snapshots` by `world_id` and
`received_at`, what the operator concludes from a hit or a miss, and the rule
that no fresh submission happens until the question is answered. The table
carries everything needed (`adapters/database/tables.py:235-266`).

### Optional

- **CL-O-1** — `describeReceipt` (`workflow.js:537-549`) guards `receipt?.duplicate`
  and `receipt?.checksum` but reads `receipt.actor_count` bare, so it throws a
  `TypeError` on an absent receipt (R-12). Unreachable on the validated path;
  the inconsistency is the defect, not the behaviour. Either guard all three or
  none and document the precondition.
- **CL-O-2** — `artifact_code`, which the guide advertises as the actionable
  detail beside `artifact_rejected` (line 669) and which `wsgi.py:390-391`
  attaches, is never read by the module. It is a closed enumeration
  (`ARTIFACT_REFUSAL_CODES`) and is exactly the value that tells an operator what
  to fix. Worth allowlisting alongside CL-I-1.
- **CL-O-3** — `executeWorkflow` still has no concurrency contract:
  `startOperation()` unconditionally makes the caller the state authority
  (`workflow.js:85-93`), and the boolean returns of `setPinnedRetry` and
  `setConfirmed` are discarded at all four call sites. Two concurrent calls with
  different payloads still lose the older indeterminate delivery's pin silently
  (R-14). Codex classified this Blocking; I lower it to Optional because 1.0.3
  makes it unreachable from the UI and the module exposes no API. It should not
  stay latent: at minimum, treat a `false` return from `setPinnedRetry` as a
  condition worth surfacing rather than ignoring, since that return is the only
  signal that uncertain retry material was dropped.
- **CL-O-4** — the "CHECKSUM DISAGREEMENT" branch of `describeReceipt` is now
  dead. `isValidSuccessReceipt` requires `receipt.checksum === checksum`
  (`transport.js:99`) before the receipt is returned, so `agreed` is always true
  by the time it is rendered. The validation is the right place for the check;
  the unreachable message should go, or the operator will eventually be told to
  trust a warning that can no longer fire.
- **CL-O-5** — the corrected credential test asserts over `JSON.stringify(state)`,
  which serialises `prepared.bytes` as an index-keyed object. It would not
  detect a credential that reached the artifact bytes. Not a live risk — the
  credential never enters `buildBundle` — but a byte-level scan would make the
  assertion say what its name claims.

## Explicit residual decision — page reload

**Ruling: not Blocking for this supervised Phase 2 module, conditional on the
three items below. I do not recommend durable client storage.**

The constraint in the request is correct and I will not route around it. Every
durable client store available here is client-readable in Foundry's threat
model: a world-scope setting is readable by every user in the world, which is
the finding that forced the credential out of settings in the first place, and a
client-scope setting is `localStorage` — unencrypted on disk and readable by any
script in the page. The pinned payload is every exported Actor's full mechanics,
the same data the module refuses to put on the wire without TLS. Persisting it
to survive a reload would trade a rare reliability failure for a permanent
confidentiality exposure, and would contradict an accepted decision. That is the
wrong trade.

The stronger reason not to solve this on the client is that the client is not
where the invariant lives. What must hold is *no second pending artifact for an
unresolved request*. After a lost pin the operator does not need the original
bytes — they need to know whether a pending artifact already exists for this
world. That is a read, not a retry, and the server can answer it: every
submission carries a checksum-derived key, the request key digest is in
append-only history, and `foundry_snapshots.checksum` is `UNIQUE`
(`adapters/database/tables.py:242`), so identical bytes can never produce two
rows however many times they are sent.

Three things bound the exposure to something a supervised operator can carry:

1. The residual case is narrow — the operator must reload *during* an
   unconfirmed delivery, then prepare and submit fresh state despite an explicit
   instruction not to.
2. The duplicate that could result is a **pending** artifact. Nothing is applied
   until a Guild Council member reviews it, which the receipt text says
   plainly. §16.4's data-loss and atomicity heads are not engaged; the cost is
   reconciliation work in front of a human, not corrupted state.
3. The module makes no false claim. I searched the diff and the guide for any
   assertion that a retry guarantee survives a reload and found none; both the
   dialog and the guide now say the opposite, and the guide declines to
   represent it as durable recovery.

What makes this acceptable is therefore not the code, which is already right,
but whether the operational half exists. Today it does not — CL-I-3. The
conditions:

1. **Resolve CL-I-3.** Document the reconciliation procedure concretely enough
   that an operator can execute it without improvising: the query, the decision
   rule for a hit and for a miss, and the prohibition on submitting until the
   question is answered.
2. **Resolve CL-I-2.** Put the reload caution on the indeterminate-failure
   notification, where the operator meets the risk, not only on the next dialog.
3. **Rehearse it.** The supervised rehearsal must induce one reload after an
   indeterminate delivery and walk the documented reconciliation to a
   conclusion, with the evidence recorded. An operational control that has never
   been executed is not evidence, and this is the control the ruling rests on.

If the rehearsal shows the reconciliation cannot be performed with what this
deployment has, the boundary reverts to Blocking and the resolution is
server-side — an operator-facing pending-snapshot query, not client storage.

## Required checks

Run from `foundry-module/`:

```text
for file in scripts/*.js; do node --check "$file"; done   # 7 files, all pass
node --test tests/*.test.mjs                              # 132 pass, 0 fail
```

Both pass at `75c7f47`. The suite grew by 6 tests over the baseline's 126, and
the new coverage is real: the added `workflow.test.mjs` cases exercise both
spent-key 409 codes and the cross-payload race, and `claims.test.mjs` now
asserts the UI serialisation and the reload wording. No test covers an
unidentifiable 409 (CL-B-1) or the allowlist's agreement with the server
(CL-I-1), which is why both survived to this review.

## Evidence

- Read-only inspection of `75c7f47` against `f632722`, the two 2026-08-08 Codex
  lifecycle reviews, `.agents/AGENTS.md`, implementation plan §§16.3, 16.4 and
  17, and the operations guide.
- Cross-checked the client's refusal vocabulary and receipt schema against
  `application/foundry/submission.py`, `adapters/http/wsgi.py`,
  `application/service_principals.py` and `adapters/database/tables.py`.
- Temporary adversarial reproduction, 17 cases, all passing, written outside the
  repository and not committed: R-1/R-2 spent-key 409 transitions; R-3/R-4/R-5
  adversarial status/code pairs; R-6/R-7/R-13 hostile and suppressed code
  rendering; R-8/R-8b/R-16 unidentifiable-response classification; R-9/R-10
  discard-and-download and pin preservation; R-11 standalone discard refusal;
  R-12 receipt rendering; R-14 exported-API cross-payload race; R-15 receipt
  bounds against the server's 500-actor limit.
- The client's `actor_count` ceiling of 10,000 is well above the service's
  `BundleLimits.max_actors = 500` (`application/foundry/parser.py:72`), so it
  cannot reject a legitimate receipt.

No Foundry installation, live world, real export, credential, endpoint,
PostgreSQL service or browser rendering was used, and the excluded
`docs/screenshots/` files were not read. The Foundry module installation and the
supervised rehearsal remain outstanding gate evidence, unchanged by this review.

## Re-review focus

Re-review should establish that no 409 the client cannot positively identify
discards retry material; that the refusal allowlist is derived from the server's
vocabulary and held there by a test; that the reload caution reaches the
operator at the moment the pin is created; and that the reconciliation procedure
is documented and has been executed once under supervision.
