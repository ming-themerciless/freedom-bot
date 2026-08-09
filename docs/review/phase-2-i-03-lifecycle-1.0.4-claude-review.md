# Independent Claude review — PreparedSnapshot lifecycle 1.0.4

Date: 2026-08-08
Reviewer: Claude, independent implementation reviewer
Reviewed state: working tree at `75c7f47` plus the uncommitted 1.0.4 remediation
Baseline: `75c7f47`, version 1.0.3
Prior review: `phase-2-i-03-lifecycle-1.0.3-claude-review.md`
Decision authority: Peter Duscha

## Recommendation

**Accept the implementation.** Every claim in the handover holds on the
production path, and I found no regression. The 1.0.3 Blocking finding CL-B-1 is
closed, and closed at the right layer: `classifyFailureDisposition` now
distinguishes what the server said from what the client failed to read, and
`executeWorkflow` no longer lets an ordinary refusal on a retry destroy an
earlier unresolved delivery's bytes and key.

**No Blocking finding is open. One Important finding is open**, and it is about
test strength rather than behaviour: the reload-warning coverage cannot fail. I
removed the live `retryPinned` argument from the `notifyFailure` call site —
which silently reopens CL-I-2 — and all 138 Node tests still passed. The
handover asked exactly this question, so I am answering it directly: the
assertions are not adequate, and this one needs a behavioural seam.

**The Phase 2 gate remains open.** Code review can and does close the
implementation findings, but it cannot close the operational half. The
lost-pin reconciliation and the induced-response-loss walk are now *documented*
— which is what conditions 1 and 2 of the 1.0.3 residual ruling required — and
they remain *unperformed*, which is condition 3. See § Gate status.

This is a review only. I changed no implementation, test, documentation or
configuration file in the repository. Every reproduction was written to my
scratchpad; the two mutation experiments were run against copies there.

## Verification of the claimed resolutions

| # | Claim | Verdict |
|---|---|---|
| 1 | CL-B-2 — a failed retry preserves the exact pinned material | **Holds** |
| 2 | Only receipt, Discard, or identified `409 request_key_conflict` ends a pin | **Holds** |
| 3 | Empty-credential UI guard returns before `run`/`executeWorkflow` | **Holds** |
| 4 | CL-I-1 — cross-language refusal-vocabulary guard | **Holds**; two residual gaps, both Optional |
| 5 | CL-I-2 — reload caution in both `notifyFailure` branches | **Holds in code**; the test does not — see CL2-I-1 |
| 6 | CL-I-3 — lost-pin rehearsal and `psql` procedure | **Holds**; one substitution gap — see CL2-O-3 |
| 7 | Version identity — both manifests `1.0.4` | **Holds** |

### Claim 1 and 2 — CL-B-2, tested through `executeWorkflow`

The handover asked for the production path rather than
`classifyFailureDisposition` alone, so that is what I drove. For each case I
established a pin with a lost response, captured the pinned object's bytes,
checksum, `exportedAt` and the `Idempotency-Key` actually written to the outgoing
request, then retried **against a mutated world and a clock five months later**
and asserted object identity and byte identity afterwards.

Sixteen refusals preserve the pin (R-A1…A16): empty credential, whitespace-only
credential, empty endpoint, insecure endpoint, malformed endpoint, `401
unauthenticated`, `404 not_found`, `405 method_not_allowed`, `403 out_of_scope`,
`413 artifact_too_large`, `400 checksum_mismatch`, an unrecognised code
suppressed to `submission_refused`, a `400` whose body will not parse, a `200`
carrying an invalid receipt, an unsupported deployment tuple on the retry, and
loss of GM permission on the retry. In each, `state.pinnedPrepared` is
`strictEqual` to the original object and the *next* submission carries a
byte-identical body, the same `Idempotency-Key` and the same `X-Snapshot-SHA256`
(R-A1…A16 “next submission identity”). A later clock changes nothing, because
`prepareSnapshot` returns the pinned entry at `workflow.js:283-285` before it
reads the world.

The three permitted exits all work: a successful retry promotes the exact pinned
object to `confirmed-reusable` with the same object identity (R-B3); an
identified `409 request_key_conflict` clears (R-B1); explicit Discard clears
before current world state is read, proven by making the fresh preparation fail
afterwards and observing `empty` rather than a restored pin (R-B4).
Discard-and-download abandons the pin and downloads fresh bytes (R-B5), while an
ordinary download still hands the *pinned* object to `downloadPrepared` and
leaves the pin standing (R-B6).

The mechanism is sound rather than incidentally correct. `beganWithPinnedRetry`
is captured after `startOperation()` and before `prepareSnapshot`
(`workflow.js:463`), so it describes the state this operation inherited. The
preserve branch re-pins `prepared`, which for an inherited pin *is* the pinned
object, so there is no copy to drift. A failure inside `prepareSnapshot` cannot
reach the state machine at all — the inner `catch` wraps only the submit — and
an inherited pin makes `prepareSnapshot` unable to fail, since it returns before
validation.

**Operation-token races.** The handover asked whether this change lets an older
operation overwrite a newer authorized transition. It does not, in either
direction. `startOperation()` always makes the newest caller the authority, and
both new call paths are token-checked. I drove two interleavings with a gated
`fetch`: an older pinned operation failing `401` after a newer operation
succeeded leaves `confirmed-reusable` intact and `pinnedPrepared` null (R-E1);
an older unpinned operation failing `401` after a newer operation pinned cannot
clear that pin (R-E2). The pre-existing property that an older operation's
outcome is silently dropped is unchanged and is still CL-O-3, still unreachable
from the UI.

### Claim 3 — the empty-credential guard, against real `DialogV2` semantics

The handover asked me not to rely on the source-regex test, so I read the
deployed Foundry `14.365.0` client on this host
(`client/applications/api/dialog.mjs`, `client/applications/api/application.mjs`)
rather than reasoning from the module. The guard holds, and the mechanism is
worth recording because it is not obvious:

1. `_onSubmit` computes `const result = (await button?.callback?.(...)) ?? button?.action`
   (`dialog.mjs:273`). The coalescing operator is nullish, not falsy, so
   `submissionChoice`'s `false` survives instead of degrading to the action
   string `"submit"`. Had that line used `||`, the guard would fail open.
2. `DialogV2.wait` resolves the promise with whatever `submit` receives
   (`dialog.mjs:405-419`), so `choice === false`.
3. `main.js:181` returns on `!choice` before the `run(...)` call.

So Submit, Retry Pinned Submission and Discard Pinned & Prepare New all stop
before `executeWorkflow`, and the pin is untouched because nothing runs. There
is a second, independent control underneath: even if the guard were bypassed,
R-A1 and R-A2 show `executeWorkflow` preserves the pin on an empty or
whitespace-only credential.

`credentialInput.required` is real but narrower than the handover implies. A
click on a `[data-action]` button is dispatched by ApplicationV2's frame
listener (`application.mjs:1918-1951`) into `_onSubmit`, whose first statement is
`event.preventDefault()` — which cancels the button's activation behaviour, so
the browser never runs interactive constraint validation and `required` shows no
bubble on the click path. It *is* load-bearing on the Enter-key path, where the
form's own `submit` listener (`dialog.mjs:213`) is reached only after validation
passes. The two controls therefore cover the two input paths between them, which
is the right outcome — but `required` should not be described as the guard for
the button, because it is not.

### Claim 4 — the cross-language refusal-vocabulary guard

The guard is real and it bites. I re-implemented its extraction in my scratchpad
and ran it against mutated copies of the tree:

| Mutation | Expected | Result |
|---|---|---|
| M1 — add a literal `_error("too_many_requests", …)` to `_submit` | fail | **fails**: `missing from module: ['too_many_requests']` |
| M2 — invent a preview-only literal in `_preview_snapshot` | pass | **passes** — preview stays excluded |
| M3 — drop `artifact_too_large` from `transport.js` | fail | **fails** |
| M4 — add the refusal in a *new helper method* of the same class | fail | **passes** — see CL2-O-1 |

The allowlist itself is now correct against the contract. All seven codes CL-I-1
listed as suppressed are present, and the three spurious entries are gone. The
guide's troubleshooting table no longer names a code the module hides:
`out_of_scope`, `length_required` and `artifact_too_large` are all visible.

One wording correction to the handover, which changes nothing material: no
JavaScript test contained a third literal copy of the vocabulary at `75c7f47`
(I checked all three test files). What actually changed is that
`SERVER_REFUSAL_CODES` became an export and `transport.test.mjs` now iterates it
instead of hardcoding a list, so a third copy was avoided rather than removed.

### Claim 6 — the lost-pin procedure

Rehearsal A step 10 now requires a rehearsal-only proxy fault that forwards the
complete POST and drops only the downstream response, requires sanitized
upstream evidence that the POST arrived, states that stopping the service is not
a substitute because it can only exercise the miss branch, names the hit branch
as the intended outcome, and forbids a fresh submission during the check. That
is what CL-I-3 and residual condition 3 asked for. Step numbering is consistent
and nothing else in `docs/` references the old numbers.

The `psql` example is lexically sound. The previous defect — psql variable
interpolation inside `-c` — is gone: there are no `:name` sequences left. The
two remaining colon constructs are safe. Colons inside `'2026-08-08 19:00:00+00'`
are inside a quoted SQL literal, where `man psql` states plainly that
interpolation is not performed; and `::timestamptz` is the typecast token, which
psql's lexer does not treat as a variable, with `-X` guaranteeing no psqlrc has
defined one anyway. Every identifier resolves: `id`, `checksum`, `actor_count`,
`received_at`, `received_via`, `correlation_id` and `world_id` all exist on
`foundry_snapshots` (`adapters/database/tables.py:236-267`). The three decision
rules — hit, miss after one repeat, unresolved — are stated with the
no-fresh-submission prohibition attached to each. I did not execute the query;
that would require a database, which this review must not touch.

### Claim 7 — version identity

`module.json:5` and `package.json:3` both declare `1.0.4`, and they are the only
two manifests in the repository. Nothing install-facing still claims `1.0.3`;
the single remaining occurrence is a fixture value inside a test (CL2-O-5).
`main.js:319` reads the exporter version from `game.modules.get(MODULE_ID)`,
which Foundry populates from `module.json`, so newly prepared bundles and their
checksum-bearing history will carry `1.0.4`.

## Regression questions — answered

I checked each one explicitly. **No regression was found.**

- **Fresh submissions with no earlier pin keep the established policy.** Sixteen
  cases (R-C1…C16). Local refusals and definitive 4xx clear; `500`, `503`,
  network failure and every unidentified `409` shape pin; `409
  request_key_conflict` clears. A `400` with an unreadable body now pins rather
  than clears, which is CL-B-1's fix and is intended.
- **Ordinary reusable state is still cleared by a definitive refusal.** A
  confirmed-reusable entry followed by a `401` leaves `empty` (R-D1). The new
  preserve branch is gated on `beganWithPinnedRetry`, so it cannot protect
  ordinary cache state.
- **Explicit Discard still clears before current world state is read**,
  including discard-and-download (R-B4, R-B5).
- **`request_key_conflict` clears a pre-existing pin; `concurrent_submission`
  and `original_result_unavailable` preserve it** (R-B1, R-C6, R-C7).
- **A successful retry promotes the exact pinned material** — same object, same
  bytes, same checksum, and the entry becomes reusable under the pinned
  fingerprint (R-B3).
- **Credentials never enter prepared or cached state.** I scanned the prepared
  bytes decoded as UTF-8, the serialised state, and a serialisation that expands
  `Uint8Array` to text, for both the full credential and its secret half (R-F1).
  Absent from all three.
- **No server-controlled value bypasses the established bounds.** Every one of
  the eighteen allowlisted codes renders its code with the server's prose
  withheld (R-S2). Nine client-origin codes an endpoint might assert — including
  `unsupported_deployment`, `unauthorized` and `authentication_unavailable` —
  are now suppressed to `submission_refused` (R-S1). Five hostile receipts are
  refused at `2xx` and pin rather than discard (R-S3). The receipt line carries
  no server-authored text (R-S4).
- **No new notification claims that nothing was stored.** The two new strings —
  the reload caution and the `missing_credential` prose — are repository-owned
  and make no storage claim. `tests/test_storage_claim_vocabulary.py` scans every
  file under `foundry-module/scripts/` and passes.

## Findings

### Blocking

None.

### Important

#### CL2-I-1 — the reload-warning coverage cannot fail

The code is right: `run` computes `retryPinned` from the live post-failure state
(`main.js:354`) and `notifyFailure` appends the caution in both the typed-error
and the unexpected-error branch (`main.js:389-404`). The handover asked whether
the assertions would fail meaningfully if the argument stopped being passed. They
would not, and I proved it rather than inferring it.

I copied the module to my scratchpad and deleted the `retryPinned` argument from
the `notifyFailure` call site, leaving the parameter and both literals in place —
the smallest realistic regression, and one that silently restores exactly the
CL-I-2 defect, because the caution would then never appear at the moment the pin
is created. `node --test tests/*.test.mjs` reported **138 passed, 0 failed**.

Neither new assertion can detect it:

- `assert.match(main, /notifyFailure\([\s\S]*retryPinned/)` matches across the
  whole file, so the function's own declaration — `function notifyFailure(error,
  reassurance, retryPinned = false)` — satisfies it on its own. It is true of
  any file that both calls the function somewhere and names the parameter
  anywhere later.
- The occurrence count of the warning string stays at 2, because the two
  literals live inside `notifyFailure` and the mutation did not touch them.

The other new claims test is stronger: removing the guard's early return does
fail `/return false/`. So this is specifically about the `retryPinned` wiring.

This is Important, not Blocking: nothing is wrong today, and the finding is a
testing weakness under §16.4's "material maintainability, testing" head. But the
control it protects is the one the 1.0.3 residual reload ruling rests on, so it
should not be left dependent on nobody touching the call site.

Required direction: give it a behavioural seam. `notifyFailure` and the
`retryPinned` computation are the only things in `main.js` that need one, and
they need very little — export the message-building step as a pure function of
`(error, reassurance, retryPinned)` and assert that a pinned state produces the
caution and an unpinned state does not, in both branches. That converts a text
match into a test that fails when the behaviour changes. The alternative — a
`ui.notifications` double driven through `run` — needs more Foundry surface than
this module currently fakes, and I do not think it is worth it here.

### Optional

- **CL2-O-1 — the cross-language guard scans three method names.** The walk is
  restricted to `__call__`, `_route` and `_submit` of
  `SnapshotSubmissionApplication` (`tests/test_snapshot_submission.py:1008-1011`).
  A refusal added in a new helper method of the same class escapes it entirely
  (M4 above). That is a plausible refactor — the body-reading block in `_submit`
  is already long enough to invite extraction, and it emits three of the codes
  the guard exists to protect. Widening the walk to every method of the class
  except `_preview_snapshot` and `_preflight` would keep the preview exclusion
  the handover asked about while removing the name dependency.
- **CL2-O-2 — two boundary codes are hand-maintained inside the derived test.**
  `boundary_codes.update({"out_of_scope", "artifact_too_large"})`
  (`tests/test_snapshot_submission.py:1027`) reintroduces, in miniature, the
  hand-maintained list CL-I-1 was about. Both are currently correct:
  `out_of_scope` is the only `NotAuthorizedError` code reachable on this path
  (`application/service_principals.py:88-91`; the `authorization.py` codes belong
  to user authorization), and `artifact_too_large` is emitted both as a WSGI
  literal and by parser classification. If either is renamed server-side the test
  keeps passing while the module goes stale. `out_of_scope` could be derived from
  the `require_scope` refusal directly.
- **CL2-O-3 — the `psql` example needs four substitutions, not three.** The text
  says "Replace all three example values", meaning `world_id` and the two
  timestamps. The database name `freedom` is a fourth. It is not the name used
  anywhere else in this guide, which uses `freedom_test` (lines 322, 739) and
  `freedom_staging` (line 1028), and Rehearsal A runs against the disposable
  database. Run verbatim after the three documented replacements, the command
  fails to connect. Either name it as a fourth value to replace or write it as an
  obvious placeholder.
- **CL2-O-4 — the empty-credential notification closes the dialog it refers to.**
  `closeOnSubmit` defaults to `true` (`dialog.mjs:167-173`), so `_onSubmit` closes
  the dialog after `submit` resolves regardless of the callback's return value.
  The operator reads "Enter the submission credential before submitting" against
  a dialog that no longer exists and must reopen it. Nothing is lost — the pin
  lives in the module-level `snapshotState`, not the dialog, so reopening
  re-offers Retry Pinned Submission — but the sentence describes an action the
  operator cannot take. Either word it as "reopen the dialog and enter the
  submission credential", or set `form: { closeOnSubmit: false }` and manage
  closing explicitly, which is the larger change.
- **CL2-O-5 — a stale fixture version.** The new unidentifiable-409 test passes
  `exporterVersion: "1.0.3"` (`tests/workflow.test.mjs:383`) while the other new
  tests use `"1.0.4"`. Cosmetic; it is the only remaining `1.0.3` in the tree
  outside `docs/review/`.

### Carried forward from 1.0.3, unchanged and not claimed closed

CL-O-1 (`describeReceipt` reads `receipt.actor_count` bare at `workflow.js:582`
while guarding the other two), CL-O-2 (`artifact_code` still never read by the
module), CL-O-3 (the boolean returns of `setPinnedRetry` and `setConfirmed`
discarded at all call sites, now five), CL-O-4 (the unreachable "CHECKSUM
DISAGREEMENT" branch) and CL-O-5 (the credential test still asserts over
`JSON.stringify`). All remain Optional. On CL-O-5 I note that a byte-level scan
does pass — I ran one (R-F1) — so the weakness is in the assertion, not the
behaviour, exactly as recorded in 1.0.3.

## Gate status — what code review can and cannot close

Code review closes the implementation findings. CL-B-1 is resolved, CL-B-2 is
resolved, CL-I-1 is resolved with a guard that fails on divergence, CL-I-2 is
resolved in code with the testing caveat above, and CL-I-3 is resolved as
documentation.

It cannot close the Phase 2 gate, and nothing in this remediation claims it
does. The 1.0.3 residual ruling on page reload had three conditions. Conditions
1 and 2 are now met. Condition 3 — rehearse it — is met on paper and not in
fact: Rehearsal A is still marked **Not run**, and both Rehearsal A and
Rehearsal B are maintainer-supervised. The induced-response-loss walk in step 10
is the first execution of the control the reload ruling depends on, and an
operational control that has never been executed is not evidence. Plan §13.3
requires recovery documentation *exercised* against a disposable environment
whenever a phase introduces a new persistent mutation.

So my recommendation to Peter is: accept 1.0.4 as an implementation, treat
CL2-I-1 as a follow-up that should land before the module is considered
maintainable rather than before the rehearsal, and keep the Phase 2 gate open
until the supervised rehearsals — including step 10 and the lost-pin walk — have
been performed and their sanitized evidence recorded. If that rehearsal shows
the reconciliation cannot be performed with what this deployment has, the 1.0.3
ruling stands: the boundary reverts to Blocking and the resolution is
server-side, not client storage.

## Required checks

Run from the repository root. All four reproduce the implementation-side
results exactly.

```text
for file in foundry-module/scripts/*.js; do node --check "$file"; done
    → 7 files, all pass
node --test foundry-module/tests/*.test.mjs
    → 138 passed, 0 failed
./venv/bin/python -m pytest -q
    → 1747 passed, 208 skipped, 1 warning
      (the skips are the PostgreSQL suites; TEST_DATABASE_URL is unset)
git diff --check
    → clean
./venv/bin/python -m pytest -q tests/test_snapshot_submission.py
    → 57 passed
```

The Node suite grew by 6 over 1.0.3's 132, and the growth is real coverage: the
five unidentifiable-409 shapes, the seven-case retry-preservation table, the
identified-conflict clear, and the allowlist round-trip. Two of the six are
source-text claims tests, one of which is CL2-I-1.

## Evidence

- Read-only inspection of the working tree against `75c7f47`; `.agents/AGENTS.md`;
  implementation plan §§13.3, 16.3, 16.4; both 2026-08-08 Claude 1.0.3 lifecycle
  reviews; and the operations guide.
- Cross-checked the client's refusal vocabulary against
  `application/foundry/submission.py`, `adapters/http/wsgi.py`,
  `application/service_principals.py`, `application/authorization.py` and
  `adapters/database/tables.py`.
- Read the deployed Foundry `14.365.0` client source on this host for
  `DialogV2._onSubmit`, `_renderButtons`, `_renderHTML`, `DEFAULT_OPTIONS`,
  `DialogV2.wait` and `ApplicationV2`'s `[data-action]` click dispatch. Source
  only: no Foundry instance was started and no world was opened.
- 101 temporary adversarial reproductions, all passing, written outside the
  repository and not committed. R-A1…A16 pin preservation with byte and key
  identity across a later clock and a mutated world, each paired with a
  next-submission identity assertion; R-B1…B6 the three permitted pin exits plus
  download behaviour; R-C1…C16 fresh-submission policy; R-D1 reusable-state
  clearing; R-E1/E2 operation-token races in both directions; R-F1 byte-level
  credential absence; R-G1…G8 classification units; R-S1…S5 the adversarial
  endpoint cases in the security review.
- Six mutation experiments against scratchpad copies: M1–M4 on the cross-language
  guard, and two on `main.js` — dropping the `retryPinned` argument (survives the
  whole suite, CL2-I-1) and neutering the credential guard's early return
  (correctly detected).
- `man psql` on the installed PostgreSQL 16.14 client for the interpolation rule.

No Foundry installation was run, no live world, real export, credential,
endpoint or PostgreSQL service was contacted, no browser rendering was
performed, and no file under `docs/screenshots/` was read. I made no change to
any repository file other than writing this review and the accompanying security
review.

## Re-review focus

If a 1.0.5 follows, re-review should establish only that the reload caution has
a test which fails when the caution stops being produced, and — if the author
chooses to take them — that the guard's method-name dependency and the two
hand-maintained boundary codes are gone. Nothing else in this remediation needs
re-examination. The next substantive gate evidence is operational, not code:
Rehearsal A step 10 and the lost-pin walk, performed under supervision and
recorded.
