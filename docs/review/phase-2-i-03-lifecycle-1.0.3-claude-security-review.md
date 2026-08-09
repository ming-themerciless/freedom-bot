# Claude security review — PreparedSnapshot lifecycle 1.0.3

Date: 2026-08-08
Reviewer: Claude, independent security reviewer
Reviewed state: `foundry-module/` at `75c7f47`, version 1.0.3
Related general review: `phase-2-i-03-lifecycle-1.0.3-claude-review.md`

## Recommendation

Security review does not recommend acceptance yet, on the strength of the
Blocking production-reliability finding in the general review (CL-B-1). The
untrusted-output finding Codex raised is **resolved**: the module no longer
renders any server-authored text, and both halves of the required control —
allowlisted codes and a validated success receipt — are in place. What remains
on the security side is that the allowlist's *membership* is wrong, which
weakens the control it implements rather than defeating it.

No credential-retention defect was found. The weak non-retention test is
corrected.

## Resolved — untrusted server response values no longer reach the operator as text

The 1.0.2 defect was that `receipt.error.code` crossed the HTTP boundary without
validation and was interpolated into a Foundry notification, giving a compromised
endpoint an unbounded text channel to a privileged operator.

Both paths are now closed.

**Refusals.** `boundedRefusalCode` (`transport.js:89-93`) admits a code only if
it is a string present in a fixed set, and substitutes `submission_refused`
otherwise. The message rendered alongside it is a repository-owned constant
(`transport.js:251-252`); the server's message is never read. I reproduced the
Codex phishing case — a sentence-length `error.code` instructing the operator to
send the world credential to an external address — and the operator sees only
`[submission_refused]` with repository text (R-7). Length, control characters,
Unicode and non-string types are all handled by the same membership test, since
nothing outside the set can pass.

**Successful receipts.** `isValidSuccessReceipt` (`transport.js:95-106`) is
checked before the receipt is returned and before any state is confirmed. It
requires an object, `checksum` equal to the locally computed value *and* matching
`/^[0-9a-f]{64}$/`, `actor_count` an integer in `[0, 10000]`, and `duplicate` a
boolean. A hostile `actor_count` carrying prose is refused (R-6), and — this is
the part that matters most — the refusal is a `malformed_response` at a 2xx
status, which classifies delivery-indeterminate and **pins** the entry rather
than discarding it. A compromised endpoint cannot use a malformed success
receipt to make the client throw away its retry material.

`notifyFailure` (`main.js:376-389`) renders `error.code` and `error.message`,
and after these changes both are repository-owned on every path. The checksum
equality check also means the operator can no longer be shown a checksum the
client did not compute.

## Important — the allowlist admits a client code and omits real server codes

The control is implemented; its contents are not derived from the contract it
claims to bound. The general review documents the full divergence as CL-I-1.
Two aspects are specifically security-relevant.

**A client-origin code is presented as a server refusal.**
`unsupported_deployment` is in `SERVER_REFUSAL_CODES` (`transport.js:86`) but is
not a server code at all — it is the module's own pre-flight refusal from
`bundle.js:104`, raised when the running Foundry or system version does not match
what the platform expects. A compromised or spoofed endpoint can return it and
have the operator read a refusal that appears to come from the module's local
safety checks rather than from the network. The purpose of the allowlist is that
every displayed code carries repository-owned meaning with correct attribution;
admitting a client-only code breaks the attribution half. `unauthorized` and
`authentication_unavailable` are likewise not emitted on the submission path
(the real 403 code is `out_of_scope`; `authentication_unavailable` belongs to the
disabled preview route), so both are additional codes an endpoint can assert but
the service will never send.

**Seven real codes are suppressed, including three the guide tells operators to
read.** `out_of_scope`, `length_required`, `artifact_too_large`,
`unsupported_media_type`, `missing_idempotency_key`, `malformed_length` and
`incomplete_body` all render as `submission_refused` (R-13). The first three
appear in the operator troubleshooting table at
`docs/operations/foundry-snapshot-submission.md:664-672`. The security cost is
diagnostic: an authorization refusal (`out_of_scope`, i.e. a credential without
`foundry:snapshot:submit`) is now indistinguishable from a routine validation
refusal, so a misissued or downgraded credential presents to the operator as an
ordinary failure. `unauthenticated` is allowlisted, so a revoked credential is
still legible; a wrongly-scoped one is not.

Required control: derive the allowlist from `REFUSAL_CODES`
(`application/foundry/submission.py:110-130`) together with the boundary codes in
`adapters/http/wsgi.py`, drop the three non-server entries, and add a test that
fails when client and server vocabularies diverge — the pattern the service
already uses to hold `ARTIFACT_REFUSAL_CODES` to the parser's actual codes.

## Note — allowlisting the two retry codes is a deliberate, bounded trust

`concurrent_submission` and `original_result_unavailable` must stay in the
allowlist, because CL-B-1's fix depends on them being recognised. That does give
a compromised endpoint a way to hold the client in a pinned state indefinitely by
returning either code on every attempt. I do not consider this a finding: the
module never retries automatically, so each cycle costs an explicit operator
action, the state is visible in the dialog, and the operator can always discard
explicitly. It is worth recording as an accepted property rather than an
oversight, since the general review's recommended fix widens it slightly by
defaulting unidentified 409s to retry-same-key. That widening trades an
endpoint-controlled nuisance for protection against losing a spent key, which is
the correct direction.

## Credential handling

Unchanged and correct. The credential remains a dialog-local parameter
(`main.js:311-333`), is sent only in the `Authorization` header
(`transport.js:204`), is never read from `game.settings`, and is cleared in the
`finally` blocks of both `run` and `openSubmissionDialogOnce`
(`main.js:200-204`, `:357-360`). `credentials: "omit"` and `redirect: "error"`
are still set, so no cookie authority is attached and a redirect cannot carry the
bearer token to another origin.

The non-retention test is corrected (F-8 resolved): it now builds an actual
credential value and asserts that value is absent from both the prepared
snapshot and the serialised state, rather than searching for the literal word
`secret` (`tests/workflow.test.mjs:1054-1099`). One residual weakness, recorded
as Optional CL-O-5 in the general review: the assertion runs over
`JSON.stringify`, which serialises `prepared.bytes` as an index-keyed object, so
it would not detect a credential that reached the artifact bytes. The credential
never enters `buildBundle`, so this is a strengthening rather than a fix.

## Reload boundary — security assessment

I concur with the general review's ruling and want the security reasoning on the
record separately, because the request asked specifically that browser storage
not be silently assumed safe.

It is not safe, and I do not recommend it. A world-scope Foundry setting is
readable by every user in the world — the finding that forced the credential out
of settings applies identically to the snapshot, which contains every exported
Actor's full mechanics. A client-scope setting is `localStorage`: unencrypted on
disk, readable by any script in the page, surviving logout, and outside the
platform's retention and deletion controls. Persisting the pinned payload to
survive a reload would make a durable plaintext copy of the most sensitive
artifact the module handles, on the operator's machine, to mitigate a rare
availability failure whose worst outcome is a duplicate *pending* record that a
human reviews before anything is applied. That trade is clearly wrong.

The privacy posture of 1.0.3 is the right one: memory-only, gone at page close,
with the recovery path routed through a server-side read the operator is told to
request. The security objection is only that the read has never been documented
or performed — CL-I-3 and rehearsal condition 3 in the general review.

## Evidence boundary

`node --test tests/*.test.mjs` — 132 passed, 0 failed. `node --check` — 7 module
scripts, all pass. Adversarial reproductions used synthetic values, an injected
`fetch` double, and no network, real credential or live endpoint; the temporary
file was written outside the repository and is not committed. No Foundry
installation, browser rendering or `docs/screenshots/` file was accessed.

Foundry escapes notification content, so nothing here was HTML or script
injection in either version. The 1.0.2 issue was social engineering against a
privileged operator through a trusted-looking channel, and closing the text
channel is what resolves it — which 1.0.3 does.
