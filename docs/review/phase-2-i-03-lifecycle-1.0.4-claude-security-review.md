# Claude security review — PreparedSnapshot lifecycle 1.0.4

Date: 2026-08-08
Reviewer: Claude, independent security reviewer
Reviewed state: working tree at `75c7f47` plus the uncommitted 1.0.4 remediation
Related general review: `phase-2-i-03-lifecycle-1.0.4-claude-review.md`
Prior security review: `phase-2-i-03-lifecycle-1.0.3-claude-security-review.md`

## Recommendation

**Security review recommends acceptance.** The one security-side finding
carried from 1.0.3 — that the refusal allowlist's membership was wrong in both
directions — is resolved, and resolved by derivation rather than by hand. The
credential posture is unchanged and remains correct, and the new empty-credential
guard slightly improves it. No new security finding is open.

Two properties below are accepted trade-offs rather than defects, and I record
them so they are decisions rather than oversights.

## Resolved — the allowlist now matches the server contract

`SERVER_REFUSAL_CODES` (`transport.js:71-91`) drops the three entries that were
not server codes on this path and adds the seven real ones that were being
suppressed. Both halves of the 1.0.3 finding are closed.

**Attribution is restored.** `unsupported_deployment` was the module's *own*
pre-flight refusal (`bundle.js:104`) sitting in a server-code allowlist, which
let a compromised or spoofed endpoint present a refusal that read as one of the
module's local safety checks. It is gone, along with `unauthorized` and
`authentication_unavailable`, neither of which this service emits on the
submission path. I drove nine client-origin codes through the production path
from a hostile endpoint — `unsupported_deployment`, `unauthorized`,
`authentication_unavailable`, `missing_credential`, `invalid_endpoint`,
`insecure_endpoint`, `timeout`, `network_failure` and `malformed_response` — and
every one is now suppressed to `submission_refused` (R-S1). An endpoint can no
longer borrow the client's voice.

**Diagnostic legibility is restored.** The seven suppressed codes are back, and
the security-relevant one is `out_of_scope`: a credential without
`foundry:snapshot:submit` again presents as an authorization refusal rather than
as an indistinguishable generic failure, so a misissued or downgraded credential
is legible to the operator. `artifact_too_large`, `length_required`,
`unsupported_media_type`, `missing_idempotency_key`, `malformed_length` and
`incomplete_body` are likewise visible, and the guide's troubleshooting table no
longer names a code the module hides.

**The control is now held in place by a test.** `REFUSAL_CODES` plus an AST walk
over the WSGI submission and routing paths is compared for exact set equality
against the vocabulary extracted from `transport.js`
(`tests/test_snapshot_submission.py:999-1046`). I mutation-tested it: adding a
literal `_error("too_many_requests", …)` to `_submit` fails the test as missing
from the module, dropping a code from `transport.js` fails it, and a preview-only
code stays correctly excluded. Two residual gaps — the walk names three methods,
and two codes are still hand-maintained inside the test — are recorded as
Optional CL2-O-1 and CL2-O-2 in the general review. Neither weakens the control
today; both are ways it could quietly stop covering the boundary later.

## Untrusted server output — still bounded, re-verified against the new surface

The 1.0.2 defect was an unbounded server-authored text channel to a privileged
operator. It stayed closed, and I re-verified it against the changed allowlist
rather than assuming the 1.0.3 result carries over.

Every one of the eighteen allowlisted codes renders its code with the server's
accompanying prose withheld; the message shown is the repository-owned constant
(R-S2). Five hostile success receipts — prose in `actor_count`, an
`actor_count` above the ceiling, a non-boolean `duplicate`, an injected extra
field, and a null receipt — are all refused by `isValidSuccessReceipt` before
any state is confirmed (R-S3). A valid receipt's rendered line carries no
server-authored text even when the response also contains hostile `message` and
`error` fields (R-S4).

One property of the 1.0.4 change is worth stating precisely, because it is a
widening: a hostile receipt at `2xx` and an unreadable response at *any* status
now classify delivery-indeterminate and **pin**. That is the safe direction —
a compromised endpoint cannot use a malformed answer to make the client throw
away retry material for a key the server may have spent — and it is the same
reasoning that closed CL-B-1.

The two new operator-facing strings introduced by this remediation are both
repository-owned: the reload caution in `notifyFailure` and the
`[missing_credential]` prose in `submissionChoice`. Neither interpolates a
server value, and neither makes a storage claim;
`tests/test_storage_claim_vocabulary.py` scans every file under
`foundry-module/scripts/` and passes.

## Credential handling

Unchanged and correct, and marginally improved.

The credential is still a dialog-local parameter, still sent only in the
`Authorization` header (`transport.js:208`), still never read from
`game.settings`, and still cleared in the `finally` blocks of both `run` and
`openSubmissionDialogOnce` (`main.js:363-367`, `:186-191`). `credentials:
"omit"` and `redirect: "error"` are still set, so no cookie authority is
attached and a redirect cannot carry the bearer token to another origin.

The new `submissionChoice` guard does not weaken this. It reads the field into
the same local it would have read it into, and on refusal it returns `false`
without constructing the choice object at all — so a blank attempt creates no
new reference. When it refuses, `main.js:181` returns before the `try`, so the
`choice.credential = ""` clearing step is not reached and is not needed: there
is no object and no credential.

I re-ran the credential non-retention check at byte level rather than over
`JSON.stringify`, which is the residual weakness recorded as CL-O-5. Scanning
the prepared bytes decoded as UTF-8, the serialised state, and a serialisation
that expands `Uint8Array` to text, for both the full credential and its secret
half: absent from all three (R-F1). The behaviour is right; only the committed
assertion is weaker than its name.

## Accepted properties, recorded deliberately

**A hostile endpoint can hold the client pinned indefinitely, and the 1.0.4
change widens that slightly.** 1.0.3's security review recorded this for
`concurrent_submission` and `original_result_unavailable`. The new default —
`RETRY_SAME_KEY` for any `409` that is not a positively identified
`request_key_conflict`, and `DELIVERY_INDETERMINATE` for any
`malformed_response` — means an endpoint can force the pinned state with a wider
range of answers. I still do not consider this a finding, and I verified the
escape rather than assuming it: the module never retries automatically, each
cycle costs an explicit operator action, the state is visible in the dialog, and
an explicit Discard always clears it. I drove three consecutive endpoint-forced
`409`s and then a Discard, which released the pin and produced a fresh
preparation (R-S5). The trade — an endpoint-controlled nuisance in exchange for
never discarding a possibly-spent idempotency key — is the correct direction, as
the 1.0.3 review anticipated.

**`credentialInput.required` is not the control on the button path.** The
general review documents the mechanism: ApplicationV2 dispatches the
`[data-action]` click into `DialogV2._onSubmit`, whose first statement is
`event.preventDefault()`, which cancels the button's activation behaviour and so
prevents the browser from ever running interactive constraint validation. The
attribute is load-bearing only on the Enter-key path, where the form's own
`submit` listener is reached after validation. The JavaScript guard covers the
click path and `required` covers the Enter path, so both input paths are
covered — but the security property belongs to the guard, and a future change
that removed the guard while keeping `required` would be a regression the
attribute does not prevent.

## Reload boundary — security assessment unchanged

I concur with the 1.0.3 ruling and with the general review's assessment that
conditions 1 and 2 are now met and condition 3 is not.

Nothing in 1.0.4 changes the storage posture, and that is the right outcome. The
pinned payload is still memory-only for one page load, still absent from any
Foundry setting, `localStorage`, flag or document. My objection to durable client
storage stands and is unaffected by this remediation: a world-scope setting is
readable by every user in the world, a client-scope setting is unencrypted
`localStorage` outside the platform's retention and deletion controls, and the
pinned payload is every exported Actor's full mechanics — the same data the
module refuses to put on the wire without TLS. Persisting it to survive a reload
would trade a rare availability failure for a permanent confidentiality
exposure.

The recovery path is now documented as a server-side read rather than a client
capability, which is the correct shape: the operator asks whether a pending
artifact exists for this world in a bounded time window, using a read-only query
against `foundry_snapshots` executed by someone permitted to read it, with the
GM sending only `world_id` and a UTC window and explicitly not Actor data or a
credential. The procedure's own instruction not to broaden the window merely to
find a row is a good detail: it keeps the read minimal and keeps a miss
honest.

The security objection that remains is the one from 1.0.3, reduced but not
eliminated: the read is now documented and has still never been performed. The
induced-response-loss walk in Rehearsal A step 10 is where that changes.

## Evidence boundary

`node --test foundry-module/tests/*.test.mjs` — 138 passed, 0 failed.
`node --check` — 7 module scripts, all pass. `./venv/bin/python -m pytest -q` —
1747 passed, 208 skipped (PostgreSQL suites; `TEST_DATABASE_URL` unset).
`git diff --check` — clean.

Adversarial reproductions used synthetic values, an injected `fetch` double and
no network, real credential or live endpoint; they were written to the
reviewer's scratchpad and are not committed. Mutation experiments ran against
scratchpad copies of the tree, never against repository files. The deployed
Foundry `14.365.0` client source on this host was read to establish `DialogV2`
callback and constraint-validation semantics; no Foundry instance was started,
no world was opened, no browser rendering was performed and no file under
`docs/screenshots/` was read. No database was contacted.

Foundry escapes notification content, so nothing here is HTML or script
injection. The threat model throughout has been social engineering against a
privileged operator through a trusted-looking channel, plus the destruction of
retry material by a party who should not control that decision. 1.0.3 closed the
first; 1.0.4 closes the second and repairs the attribution the first depended
on.
