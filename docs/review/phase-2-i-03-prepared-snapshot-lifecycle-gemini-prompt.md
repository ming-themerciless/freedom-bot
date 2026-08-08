# Gemini prompt — Phase 2 I-03 prepared-snapshot lifecycle remediation

Status: **superseded on 2026-08-07** by the bounded five-step sequence in
`phase-2-i-03-lifecycle-remediation-step-plan.md`. Do not give this broad prompt
to an implementing agent. It is retained only as historical context.

Use this prompt from `/opt/discord-bots/freedom-bot`.

---

Act as the implementing engineer for one bounded Phase 2 I-03 remediation. Fix
the incomplete prepared-snapshot lifecycle in the unreleased Foundry module
version `1.0.2`, add transition-level regression evidence, reconcile affected
documentation, and produce a self-contained walkthrough for independent Codex
review.

Do not commit or push. Do not install or restart Foundry, start a rehearsal
endpoint, access Foundry world storage, read a real export, use a credential, or
touch production services or data. Use synthetic fixtures only. Do not claim
that I-03 or Phase 2 is complete, accepted, gate-ready, or approved.

## 1. Read and preserve before editing

Read completely before changing anything:

1. `AGENTS.md` and `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`, especially §§6.4–6.5 and Phase 2 acceptance,
   mandatory tests, operational evidence and review gate;
3. `docs/adr/0009-snapshot-submission-http-boundary.md`;
4. `docs/operations/foundry-snapshot-submission.md`, especially its failure
   taxonomy, retry instructions and rehearsals;
5. `docs/operations/phase-2-maintainer-closeout.md`;
6. `docs/project-management/status.md`;
7. `docs/review/phase-2-supervised-rehearsal-2026-08-06.md`;
8. the prior undefined-value remediation prompts and review records relevant to
   module `1.0.1`;
9. every file under `foundry-module/scripts/` and
   `foundry-module/tests/`; and
10. the complete `git status`, the diff from `3abb5ba`, and all untracked files
    in the package.

The working tree is intentionally large and dirty. Preserve every unrelated
change. Do not reset, checkout, clean, delete, rewrite, reformat broadly, amend,
stage, commit or push. The complete `foundry-module/` is currently untracked;
do not mistake that for permission to replace it wholesale.

## 2. Rehearsal defect and accepted direction

The 2026-08-06 supervised rehearsal proved that rebuilding unchanged exportable
content with a new `exportedAt` produces a new checksum and idempotency key. Six
pending snapshots were created before the disposable endpoint was stopped and
cleaned up. Version `1.0.2` introduces a bounded one-entry
`PreparedSnapshotState` and correctly reuses exact bytes while unchanged
content is confirmed-reusable. It also pins exact bytes after browser timeout or
network failure.

Independent review found the lifecycle incomplete:

- `main.js` pins only `timeout` and `network_failure`;
- every other failure clears state;
- the operations contract requires retrying the **same key** for at least
  `concurrent_submission`, `storage_unavailable`, `database_unavailable`, and
  `internal_error`;
- `malformed_response` is delivery-indeterminate because the request reached a
  server but the client cannot establish whether it committed; and
- an unknown failure after dispatch must not silently become a fresh checksum
  unless the implementation can prove that the request was not accepted.

The safe rule is: when delivery may have occurred or the server/operator
contract requires retrying the same key, retain and pin the exact prepared
object, bytes, checksum, `exportedAt`, content fingerprint and idempotency key.
Clear it only for a definitive pre-dispatch/local refusal or a definitive
non-retryable response. Never infer certainty solely from prose in a UI error.

## 3. Required design

Implement an explicit, testable failure disposition at the transport/workflow
boundary. Do not leave a growing ad-hoc list embedded in Foundry UI code.

The design must:

1. Distinguish at least:
   - no request dispatched / definitive local refusal;
   - definitive non-retryable server refusal;
   - retry same prepared submission; and
   - delivery indeterminate, which also retries the same prepared submission.
2. Derive disposition from facts known where the error is created: request
   stage, HTTP status and bounded repository-owned error code. Do not trust an
   arbitrary server message, leak response content, or echo credentials.
3. Pin exact prepared state for network failure, timeout, malformed response,
   the documented same-key server categories, HTTP 5xx unless a stronger
   repository contract proves otherwise, and conservative unknown
   post-dispatch failures.
4. Clear state for local endpoint/credential validation failures and documented
   definitive contract/authentication/authorization refusals where no same-key
   retry is prescribed. Treat `request_key_conflict` deliberately and document
   why retrying identical bytes can or cannot resolve it.
5. Keep the state strictly bounded to one prepared snapshot. Store no
   credential, response body, Actor data beyond the already prepared artifact,
   exception object or unbounded history.
6. Prevent an older overlapping submission completion from overwriting or
   clearing newer prepared state. Use a small compare-and-set/generation design
   or serialize active workflows; prove the chosen behavior with deterministic
   tests. A stale success or failure must not replace a newer entry.
7. Preserve explicit operator control for an unconfirmed pinned retry: retry
   exact bytes or deliberately discard and prepare current world state.
8. Preserve unchanged-content reuse, meaningful-content invalidation, folder
   switching, credential isolation, canonical bytes, checksum derivation and
   all previously accepted security behavior.

Do not solve this by removing `exportedAt`, weakening checksum identity, using a
random idempotency key, persisting credentials, storing multiple snapshots, or
silently preparing fresh bytes after an uncertain attempt.

If current operations prose claims a server category definitely recorded
nothing while also requiring the same key, retain the safer same-key behavior
and correct the prose to distinguish database receipt from possible artifact or
delivery state. Do not weaken an existing durability warning without evidence.

## 4. Required regression tests

Add tests at the level that owns the transition, not tests that manually call
`setUnconfirmedRetryPinned` and thereby bypass production orchestration.
Refactor a small dependency-injected coordinator out of `main.js` if necessary
to make real transitions testable without importing Foundry globals.

At minimum prove:

- advancing-clock unchanged successful submission reuses strict object identity,
  bytes, checksum and key;
- timeout and network failure pin exact prepared identity;
- malformed response pins exact prepared identity;
- each documented same-key server failure pins exact prepared identity;
- an unknown post-dispatch failure fails conservatively and pins;
- local invalid endpoint, insecure endpoint and missing credential do not leave
  a false unconfirmed-delivery claim;
- definitive 400/401/403/411/413 refusals clear according to the documented
  policy;
- `request_key_conflict` has an explicit tested disposition;
- explicit discard after a pinned retry prepares current changed world state;
- retry without discard ignores later world changes and resends exact bytes;
- a stale older failure cannot overwrite a newer prepared snapshot;
- a stale older success cannot clear or replace newer pinned state;
- state remains bounded to one entry through folder switches and races; and
- no credential enters prepared state, cached state, error metadata, fixtures,
  messages or logs.

Assert both state and outbound request headers/body. Avoid tests that merely
reimplement the production classification table in test code without driving
the real transition.

## 5. Documentation and controlled records

Update only records affected by this defect. Preserve the rehearsal as a failed
historical attempt; do not turn pending boxes into passes.

At minimum reconcile:

- `docs/review/phase-2-supervised-rehearsal-2026-08-06.md` with the final local
  remediation state and verification, while stating that `1.0.2` has not been
  installed or rehearsed;
- `docs/project-management/status.md` with the implementation/review state and
  exact remaining critical path;
- `docs/operations/foundry-snapshot-submission.md` failure and retry guidance;
- module comments and operator dialog wording; and
- the Gemini walkthrough identified by the current task, updating it in place
  if one exists rather than creating competing walkthroughs.

Do not erase the earlier `undefined_value` failure. Present the sequence
honestly: initial undefined-value refusal, 1.0.1 projection remediation, later
successful transport exposing duplicate submissions, then the 1.0.2 lifecycle
remediation and this correction. Do not claim a real-data preview, negative
origin observation, Data Owner attestation or gate decision occurred.

## 6. Verification

Run narrow tests first and then all safe configured checks. Report commands and
fresh exact counts; do not copy totals from an earlier walkthrough.

```bash
(cd foundry-module && node --test tests/*.test.mjs)

for file in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do
  node --check "$file"
done

./venv/bin/python -m pytest -q \
  tests/test_exporter_contract.py tests/test_snapshot_parser.py \
  tests/test_snapshot_roll_inputs.py

./venv/bin/python -m pytest -m "not db" -q -rs

./venv/bin/python -m compileall -q application adapters domain tools tests migrations

git diff --check
git status --short
```

Run database-backed checks only if they are necessary for a changed Python or
database contract and the existing instructions authorize the disposable
`freedom_test` database. Prove the target and clean inventory before use and
restore it exactly afterward. This JavaScript lifecycle correction should not
require database mutation merely to inflate evidence.

Review the entire resulting diff for credentials, authorization headers, raw
exports, Actor/player data, stable real-world identifiers beyond already
approved sanitized evidence, unsafe exception text, generated artifacts,
unrelated edits and false completion claims. Because untracked files are absent
from ordinary `git diff`, inspect them explicitly and report that limitation.

## 7. Stop conditions and handoff

Stop and ask the maintainer before accessing Foundry or a real export, using or
creating a credential, starting an endpoint, changing data authority,
authorization, retention, topology, accepted architecture or rollback policy,
or committing/pushing.

Create a self-contained remediation walkthrough that contains:

- root cause and exact failure-policy correction;
- the lifecycle states and transition table;
- overlap/race behavior and bounded-state proof;
- every changed file;
- exact test commands and fresh results;
- documentation/status corrections;
- security and privacy review;
- unchanged wire format and version decision, or a justified version bump if
  packaging rules require it;
- checks not run and why;
- confirmation that no real export, credential or Foundry data was accessed;
- residual risks; and
- the precise next action: independent Codex implementation and security review
  before installation or supervised rehearsal rerun.

End with: `Implementation ready for independent review; not installed or
rehearsed; Phase 2 gate remains open.` Do not commit, push, install, rehearse or
approve your own work.

---
