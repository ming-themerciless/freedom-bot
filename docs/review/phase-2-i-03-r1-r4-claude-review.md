# Claude re-review — R-1 through R-4 trial-finding remediation

Date: 2026-08-09
Reviewer: Claude, independent implementation reviewer
Request: `docs/review/Handover information`
Decision authority: Peter Duscha
Scope: the working-tree remediation of R-1…R-4, the fixture-identity scope
decision, and whether the trial changes the *accept* recommendation for the
1.0.4 code. Review only — nothing in the repository, the databases, Foundry,
the endpoints or `docs/screenshots/` was modified or read where prohibited.

## Verdict

| Finding | Requested | Verdict |
|---|---|---|
| R-1 reload-warning coverage | close | **Closed** — behaviourally tested, and the regression that defeated the old assertion now fails the suite |
| R-2 bounded artifact code | close | **Closed** — and the refusal vocabulary is now pinned to the real boundary, which is more than was asked |
| R-3 scratch deployment pin | close | **Closed as to the finding**, with one new Important follow-up (CL3-I-1) |
| R-4 duplicate-safe reconciliation | close | **Not closed — Blocking (CL3-B-1)**. The remediation fixes a duplicate shape the module cannot produce; the shape it *does* produce still yields a false miss |
| Fixture-identity scope decision | confirm | **Confirmed correct** |
| Trial changes the 1.0.4 accept? | opinion | **No** — I agree with the handover. But the module must not be installed anywhere as `1.0.4` again (CL3-I-2) |

New findings: **1 Blocking, 2 Important, 3 Optional.** Numbered `CL3-*`,
continuing `CL-*` (1.0.3) and `CL2-*` (1.0.4).

## Checks I ran

```text
node --check foundry-module/scripts/*.js   → 8 files, all pass
node --test foundry-module/tests/*.test.mjs → 143 passed, 0 failed
./venv/bin/python -m pytest -q              → 1756 passed, 208 skipped, 0 failed
git diff --check                            → clean
```

Every number in the handover reproduces exactly. Database-backed tests remain
skipped here (208) because `TEST_DATABASE_URL` is not configured in this
session; that is the same posture as the previous reviews and is stated rather
than glossed.

Mutation work and the behavioural probe below ran against **copies** in my
scratchpad and against the committed fakes. No repository file was edited.

---

## R-1 — reload-warning coverage — **Closed**

The control now has a real seam. `failureNotification`
(`foundry-module/scripts/notifications.js:16-28`) is pure, and
`foundry-module/tests/notifications.test.mjs` drives it over the typed, the
unexpected, the pinned and the unpinned outcomes and asserts the returned
operator text rather than the source.

I repeated the CL2-I-1 methodology rather than inferring the result. Copying the
module to my scratchpad and running four independent regressions:

| Mutation | Before (1.0.4) | Now |
|---|---|---|
| delete the `retryPinned` argument at the `notifyFailure` call site | 138 pass, 0 fail | **142 pass, 1 fail** |
| make `failureNotification` return `base` and drop the warning | not covered | **141 pass, 2 fail** |
| have `notifyFailure` pass `retryPinned: false` into the builder | not covered | **142 pass, 1 fail** |

The smallest realistic regression — the one that silently restores exactly the
CL-I-2 defect — is now caught. The wiring assertions
(`foundry-module/tests/claims.test.mjs:81-85`) are still source-text claims, but
they are no longer the *only* check, and the behaviour they guard is asserted
independently. That is the right split.

One note, not a finding: `run` computes `retryPinned` **after** the workflow's
catch handler has settled the pin (`foundry-module/scripts/main.js:355`), so the
message reports the post-failure state. That is what the trial observed at
16:19:11 and it is what the test fixes in place.

## R-2 — bounded artifact code — **Closed**

`artifact_rejected` now carries a separately bounded `artifact_code`
(`foundry-module/scripts/transport.js:145-148, 302-320`). Server prose is still
discarded; an unrecognised code is still dropped to nothing.

Two mutations, both caught:

| Mutation | Result |
|---|---|
| `boundedArtifactCode` returns the raw value unbounded | **142 pass, 1 fail** |
| the `[${artifactCode}]` fragment is removed again | **142 pass, 1 fail** |

Cross-language equality is enforced in both directions by
`tests/test_snapshot_submission.py:1047-1063` against
`submission.ARTIFACT_REFUSAL_CODES`, which
`test_the_declared_artifact_codes_are_exactly_the_parser_s` in turn pins to the
codes `artifact.py` and `parser.py` can actually raise. A new parser refusal
cannot become invisible, and an attacker-chosen string cannot become visible.

Beyond what was asked: `SERVER_REFUSAL_CODES` is now derived-and-checked against
the real WSGI submission boundary (`tests/test_snapshot_submission.py:999-1044`).
That is why `authentication_unavailable` and `unauthorized` disappeared —
nothing emits them — and why nine codes the boundary really does emit
(`incomplete_body`, `length_required`, `malformed_length`,
`missing_idempotency_key`, `out_of_scope`, `unsupported_media_type`,
`artifact_too_large`, …) are visible for the first time. Each is exercised end
to end in `foundry-module/tests/transport.test.mjs:162-176`. This closes a real
diagnostic gap the trial had not yet hit.

## R-3 — scratch deployment pin — **Closed, with one Important follow-up**

`deployment_from_environment` (`tools/snapshot_api.py:93-125`) is a genuine
all-or-nothing tuple: partial refuses with the missing variable names, blank
counts as missing, and the charset/length bound refuses a value that could forge
a line into the startup banner. `tests/test_snapshot_api.py` covers all five
behaviours including the newline-injection case. The default is still
`OBSERVED_DEPLOYMENT`, the banner prints the effective tuple, and the operations
guide documents the scope and the disposable-database requirement
(`docs/operations/foundry-snapshot-submission.md:326-341`). Nothing outside the
launcher reads the variables — I checked; `build_application` is called from one
non-test place, and it is this file.

The finding as written is answered. Two residuals:

### CL3-I-1 — the override is fail-closed on *shape*, not on *target* — Important

The four variables are validated for form, but nothing at runtime ties them to a
disposable database or a non-production `APP_ENVIRONMENT`. `build_application`
applies `ConnectionPolicy.SOCKET_OR_LOOPBACK`, which constrains *where* the
database is, not *which* database it is;
`adapters.database.safety.assert_disposable_target` exists and is used only by
`tests/conftest.py` and `tests/benchmark_snapshot_500.py`. So a host that has
the rehearsal tuple exported — in a shell profile, a saved command, a service
`Environment=` line — and the production `DATABASE_URL` will quietly accept
scratch-world snapshots into the real store, under the real world's audit
history.

This matters more than it would elsewhere, for two reasons. `tools/snapshot_api`
is currently the *only* process that serves this endpoint at all
(`docs/operations/topology.md:336-341`: "No production process runs this
endpoint yet"), and the trial published exactly this launcher to the public
internet through Cloudflare and Caddy. The deployment pin is the control that
made the 15:48 refusal happen; an environment variable that relaxes it should
not be satisfiable against a non-disposable target.

Recommendation: refuse the override unless the resolved database identity passes
`assert_disposable_target` (or, more cheaply, unless `APP_ENVIRONMENT` is not
`production`), and say so in the refusal. This is a small addition to
`deployment_from_environment`'s existing refusal path. It is the same
fail-closed reasoning the rest of this package already applies, extended from
the value's shape to its blast radius.

### CL3-O-1 — `build_application`'s docstring still says the opposite — Optional

`adapters/http/composition.py:87-94` still reads "`ancestors` is a test seam, in
the same sense `deployment` is … **It is read from no environment variable.**"
That sentence is the one R-3 quotes as the reason the shipped tooling looked
unable to reach a scratch world. It is now false for `deployment` in the shipped
launcher. Rewording it to name the launcher and the rehearsal variables costs
nothing and removes the exact trap that was fallen into once.

## R-4 — duplicate-safe lost-pin reconciliation — **Not closed. Blocking.**

The implementation change is correct as far as it goes. A duplicate that arrives
under a **new** idempotency key does write a fresh
`snapshot_submission.accepted` event at the current time, with
`entity_id` = the checksum and `payload.duplicate = true`, joining to the
original all-time `foundry_snapshots` row. I confirmed this by driving the real
service over the committed fakes:

```text
DUPLICATE / NEW KEY  -> events: [(accepted, duplicate=False, 5c213cf0…),
                                 (accepted, duplicate=True,  5c213cf0…)]
```

The problem is that **the Foundry module cannot produce that shape.**

### CL3-B-1 — the reachable duplicate writes no audit event at all — Blocking

`idempotencyKeyFor(checksum)` returns `` `foundry-module:${checksum}` ``
(`foundry-module/scripts/transport.js:217-219`) — "Derived, never random",
deliberately. The checksum is over the whole bundle, and the bundle contains
`exportedAt` (`foundry-module/scripts/bundle.js:198-212`). Therefore, from this
module:

- identical bytes **always** carry the identical idempotency key; and
- two separate preparations essentially never produce identical bytes, because
  `exportedAt` differs.

So a module resubmission of already-stored bytes is always a *same-key* replay,
never a new-key duplicate. And the same-key replay path returns at
`application/foundry/submission.py:583-586` — `idempotency.find(...)` is spent,
the unit of work is rolled back, `_replay` builds a receipt with
`duplicate=True` (`submission.py:792-805`) — **before** the accepted-event write
at `submission.py:662-689` is ever reached. No audit event is recorded. Same
probe, same service:

```text
SAME-KEY REPLAY -> audit events before: 1, after: 1, receipt.duplicate: True
```

Now run the §9 procedure over that. The GM gives "the smallest UTC window
containing the failed attempt" (`docs/operations/foundry-snapshot-submission.md:1088-1090`),
which is the retry. The query finds no event in that window. The operator reads
the second bullet — no row, query repeated once — records a **miss**, and
"Only then may the operator authorize the GM to prepare and submit a fresh
snapshot" (line 1125-1128). The fresh export mints a new `exportedAt`, a new
checksum and a new key, and becomes a genuine second pending row.

That is R-4, unchanged, along the only path the module can actually take. The
`received_at` filter was not the whole defect; it was the visible half of it.

Two concrete consequences to check against:

1. **The remediation's own rehearsal step cannot produce its stated outcome.**
   New step 10 (`docs/operations/foundry-snapshot-submission.md:825-838`)
   requires the module to "reuse the confirmed prepared bytes from step 4" and
   then states "The intended rehearsal outcome is one hit with `duplicate =
   true`: the attempt's new audit event resolves to the original snapshot row".
   Reusing step 4's bytes reuses step 4's key, so there *is* no new audit event.
   Run as written, this step will produce a **miss** and — if the operator
   follows the rule — an authorized fresh export. The rehearsal designed to
   prove the fix would demonstrate the defect, and would do so by creating the
   second pending artifact the design exists to prevent.
2. **§5.8 already documents the same shape.** Line 767-768: "Run the same
   command again: `HTTP 200` with `"duplicate":true`" — same
   `Idempotency-Key`, hence the replay path, hence no second event. The
   evidence that the reachable duplicate is the silent one is already in the
   guide.

**Why Blocking rather than Important**: identical to Codex's reasoning for R-4
itself — §16.4 production reliability, and the specific outcome is a second
pending artifact, which is the invariant this whole package exists to hold.

**What would close it.** The implementation is not wrong; the *anchor* is
incomplete. The cheapest correct fix is documentary and is one paragraph:

- Require the window to span the **whole unresolved episode** — from the first
  submission of the pinned bytes to the last attempt before the reload — not
  the last attempt alone. The event that proves arrival was written by the
  *first* attempt under that key; every later retry is a silent replay. State
  that explicitly, because the current text ("smallest", "do not broaden the
  time window merely to find a row") actively steers away from it.
- Correct step 10's expected outcome to match: the hit is the *original*
  attempt's event, `duplicate = false`, at the earlier timestamp — or, if the
  intent is genuinely to observe `duplicate = true`, the step must submit the
  same bytes under a different key, which the module will not do and `curl`
  must therefore do.
- Add the regression the doc test cannot express. There is currently **no**
  test asserting that a duplicate writes a second accepted event, nor that a
  replay writes none;
  `test_same_bytes_under_another_key_is_one_artifact_identity`
  (`tests/test_snapshot_submission.py:311-323`) checks receipts, snapshots and
  idempotency records but never `store.audit_events`. Two assertions there and
  in `test_a_retry_never_creates_a_second_snapshot_or_artifact` would pin both
  halves of the premise the §9 procedure now rests on.

A stronger option, if the maintainer would rather not depend on the GM
remembering the first attempt: record an audited replay event, or have the
procedure also consult `idempotency_keys` for the scope. Both are larger than
this package, and the window rule is sufficient if it is stated.

### CL3-O-2 — the §9 example still says "three" substitutions — Optional

Line 1111: "Replace all three example values". The command contains four:
`freedom` (the database), `'the-guild'`, and the two timestamps. This is
CL2-O-3, which the trial confirmed in practice (handover R-5), reproduced in the
paragraph the remediation rewrote. The rest of that paragraph is good — the
prohibition on restoring a `foundry_snapshots.received_at` filter is exactly
right and is enforced by
`tests/test_snapshot_recovery_documentation.py:31-32`.

### CL3-O-3 — the reconciliation query is still string-matched, never executed — Optional

`tests/test_snapshot_recovery_documentation.py` asserts the query's *text*. I
checked the parts a string match cannot: `audit_events.entity_id` is
`String(120)` and `foundry_snapshots.checksum` is `String(64)`
(`adapters/database/tables.py:205, 243`), so the join types agree; and every
literal in the `WHERE` clause matches the code —
`snapshot_submission.accepted` (`application/foundry/audit_policy.py:204`),
`foundry_snapshot` (`submission.py:77`), `foundry` (`application/audit.py:40`).
So it should run. But the previous defect in this same block was an
interpolation bug found by a human running it, not by a test, and the guarding
tests are still of the same kind. Executing it once against the disposable
database — as part of whatever rehearsal replaces the corrected step 10 —
would be worth more than another assertion about its text.

---

## CL3-I-2 — two behaviourally different builds both call themselves 1.0.4 — Important

`foundry-module/module.json` and `package.json` both read `1.0.4`, and the
working tree changes what the module *does*: it adds `notifications.js`, changes
the operator-visible failure text, and starts showing `artifact_code`. The 1.0.4
that was installed on `foundry3` and trialled did none of that — R-2 of the
handover records that build showing `[artifact_rejected]: ask an operator to
check the service log` and discarding the code.

That version string is not cosmetic. `main.js:326` feeds the manifest version
into the bundle as `exporter.version`, so it lands in `foundry_snapshots.
exporter_version` and in checksum-bearing audit history — the handover cites
`exporter_version = 1.0.4` as confirmation of the version-identity claim. Two
builds sharing it makes that history unable to answer which module produced a
row. Claim 7 of the 1.0.4 review ("version identity — both manifests 1.0.4 —
holds") does not survive this change.

Bump both manifests to `1.0.5` before this build is installed anywhere, and
record in the operational history that the trialled 1.0.4 is not this build. The
rehearsal database was destroyed, so nothing needs correcting retroactively — but
that is luck, not a control.

## Fixture-identity scope decision — **Confirmed correct**

I verified the correction rather than accepting it. Searching every `.py`,
`.js`, `.mjs`, `.json` and `.md` in the repository for `52ywI3ttEcgf9iBv`,
`smob5eya6XVBAuIb`, the shared tail `5eya6XVBAuIb` and the `smob` prefix: no
code, test, fixture or contract specimen contains any of them. The five
documents named in the correction are exactly the five that still do, and no
others.

The scope decision is right, on both halves:

- `docs/discovery/foundry-mapping.md:155` and
  `docs/adr/0006-foundry-integration-boundary.md:180` cite the identifier *as
  the evidence* for F-F1 — a manual export carries `"_id": null` and the real id
  survives only in the filename. Replacing it there would leave a finding whose
  reasoning no longer demonstrates anything. That is a citation, not a fixture,
  and the fixture-strategy rule it would be measured against does not reach it.
- The three historical review records are exactly what AGENTS.md's
  append-only/compensating-action rule protects. Editing them to look correct
  after the fact is the practice the rule forbids; the correction document is
  the compensating action, and it is specific enough to serve as one.

I also agree these are not secrets — AGENTS.md's Git-history rule concerns
credentials, and nothing here needs rotation — so no history rewrite.

The residual recommendation in the correction document (a test asserting no
fixture identifier appears among the identifiers `docs/discovery/` cites as
real) is worth doing and remains Optional. The attestation in
`fixtures.mjs` is prose again, and prose is what failed the first time.

## Does the trial change the *accept* for the 1.0.4 code?

No, and I agree with the handover's reasoning as far as it goes. Nothing in the
trial contradicts the 1.0.4 findings: CL-B-1 and CL-B-2 behaved in a real
browser against a real service exactly as the reproductions predicted, and the
one control the review could only verify by reading — the reload caution — was
seen firing at the moment the pin was created.

Two qualifications on "every trial finding is in the operational and
documentation layer, not in the remediated code":

- CL3-B-1 is not in the documentation layer. The miss rule is unsound because of
  a *code* property — a derived idempotency key plus an event written only on
  the store path. The fix I recommend happens to be documentary, but the finding
  is about how the service and the module behave together, and it was invisible
  to both of the layers reviewed separately.
- CL3-I-2 is a fact about this build, not about the trialled one.

## Recommendation

Do not record Phase 2 as closed on this package.

1. **CL3-B-1 must be resolved and re-reviewed** before the corrected Rehearsal A
   step 10 is run, and certainly before any procedure that can authorize a fresh
   export after a lost pin is used against a real world. It is small — a window
   rule, a corrected step, and two test assertions — but it is Blocking and it
   is currently guarded by nothing.
2. **CL3-I-1 and CL3-I-2** should land in the same change: they are a few lines
   each and both concern controls the trial has already shown are load-bearing.
3. **CL3-O-1, CL3-O-2, CL3-O-3** and the fixture-guard test are tracked
   follow-ups.
4. R-1 and R-2 are closed; R-3 is closed as a finding, with CL3-I-1 tracked
   against it.

The handover's own evidence boundary is accurate and should be preserved
verbatim in the milestone record: the trial does not satisfy the Phase 2 gate,
Rehearsal A steps 6 and 7 were not performed, Rehearsal B has not been run, and
no Data Owner attestation exists. That boundary, stated by the party who would
have benefited from blurring it, is the most reassuring thing in this package.
