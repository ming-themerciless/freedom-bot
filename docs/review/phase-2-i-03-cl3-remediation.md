# CL3 remediation record — R-1…R-4 trial findings

Date: 2026-08-09
Findings addressed: `CL3-B-1`, `CL3-I-1`, `CL3-I-2`, `CL3-O-1`, `CL3-O-2`
Source review: [`phase-2-i-03-r1-r4-claude-review.md`](phase-2-i-03-r1-r4-claude-review.md)
Decision authority: Peter Duscha

This record closes findings. It is not an I-03 acceptance, not a Phase 2 gate
decision, and not evidence that any rehearsal was performed.

## Who did what, and what that costs

Two parties acted, and the separation is not clean throughout:

| Finding | Implemented by | Independently reviewed |
|---|---|---|
| CL3-B-1 | Codex | **Yes** — Claude, verified against a re-run of every check below |
| CL3-I-1, CL3-I-2, CL3-O-1, CL3-O-2 | Claude | **No** — implemented by the reviewer who raised them, at the maintainer's explicit instruction on 2026-08-09 |

The second row is a deliberate, recorded departure from the §17 practice of
keeping implementation and review distinct. The maintainer directed it to stop
a review cycle that was no longer adding quality. It is stated here rather than
left for a later reader to discover: **the CL3-I and CL3-O changes carry no
independent review.** They are small, they are covered by tests named below, and
none of them touches the submission service, the artifact store, the audit path
or the database boundary — but a maintainer who wants them reviewed before the
gate should commission that as its own pass.

## CL3-B-1 — lost-pin reconciliation could report a false miss — **Reopened, then closed**

> **Correction, 2026-08-10.** This section recorded CL3-B-1 as closed on
> 2026-08-09. **It was not.** The independent gate review (finding B-1 in
> `docs/review/Handover information`) established that the window correction
> below fixes one false miss and leaves another: the operator was still told to
> wait for the client's "request/timeout" to finish, and a client timeout proves
> only that the browser stopped waiting, not that the server stopped processing.
> A query run before a still-open transaction commits misses twice and authorizes
> a fresh export anyway.
>
> The finding is remediated separately and later — see
> [`phase-2-b-1-settlement-remediation.md`](phase-2-b-1-settlement-remediation.md),
> which adds the settlement condition the §9 miss branch now requires. Read the
> section below as the record of the *window* correction only. Its final
> paragraph's verification claim stands for the three conditions the CL3 review
> named; it was never a verification that the recovery contract as a whole was
> sound, and it should not be read as one.

The defect: `idempotencyKeyFor(checksum)` is derived, so a module retry of
pinned bytes is always a *same-key* replay; the replay path returns before the
accepted-event write, so it records no audit event. The §9 procedure told the
operator to use "the smallest UTC window containing the failed attempt" — the
retry — find nothing, record a miss, and authorize a fresh export. That fresh
export mints a new checksum and becomes the second pending artifact the package
exists to prevent.

Remediated by Codex in the working tree:

- §9 now requires the window to span **the whole unresolved episode**, from the
  first submission of the pinned bytes to the last attempt before the reload,
  and states that a same-key retry replays its receipt without writing a new
  audit event;
- Rehearsal A step 10 now expects the reachable outcome — one hit with
  `duplicate = false`, the original attempt's event — instead of an outcome the
  module cannot produce;
- `tests/test_snapshot_submission.py` now asserts both halves of the premise:
  a same-key retry leaves exactly one audit event with `duplicate` false, and
  the same bytes under a different key produce a second event with `duplicate`
  true;
- `tests/test_snapshot_recovery_documentation.py` pins the whole-episode rule,
  the checksum join, the absence of a `foundry_snapshots.received_at` filter and
  the duplicate-safe miss rule.

Verified independently on 2026-08-09: the three conditions the review named as
closing the finding are all met, and every number in the handover reproduces
exactly (see Checks below).

## CL3-I-1 — the deployment override was fail-closed on shape, not on target — **Closed**

`deployment_from_environment` validated the four `FREEDOM_SNAPSHOT_REHEARSAL_*`
variables for completeness, length and charset, and nothing tied them to a
disposable database. A host with the tuple exported — a shell profile, a saved
command, a service `Environment=` line — and a production `DATABASE_URL` would
have accepted scratch-world snapshots into the real store, under the real
world's audit history.

The override is now refused outside `APP_ENVIRONMENT=test`
(`tools/snapshot_api.py`), which `DatabaseSettings.from_mapping` in turn binds
to the disposable `freedom_test` database. An unset `APP_ENVIRONMENT` is
refused: it defaults to `development` in the composition, so the override has to
be asked for deliberately. The refusal names the observed environment, bounded
and quoted so it cannot forge a line into the startup banner — the same
treatment the tuple members already had.

Not claimed: this binds the override to an *environment*, and through it to a
database name. It is not a proof of which cluster answers, and
`assert_disposable_target` is still not called from the launcher.

Covered by `tests/test_snapshot_api.py`: refusal in `production`, `staging`,
`development` and an empty value; refusal when the variable is absent; the
refusal's own output bounded; and — the property that must not regress — the
controlled `OBSERVED_DEPLOYMENT` pin returned unconditionally in every
environment when no override is present.

## CL3-I-2 — two behaviourally different builds both called themselves 1.0.4 — **Closed**

The build in this tree adds `notifications.js`, changes the operator-visible
failure text and surfaces `artifact_code`; the 1.0.4 installed on `foundry3`
for the 2026-08-09 trial did none of that. `main.js` feeds the manifest version
into the bundle as `exporter.version`, so it reaches
`foundry_snapshots.exporter_version` and checksum-bearing audit history: two
builds sharing the string makes that history unable to say which module
produced a row.

Both manifests are now `1.0.5`. `tests/test_exporter_contract.py` pins
`module.json` and `package.json` to one version and one id, so they cannot drift
apart again by hand. `docs/operations/phase-2-maintainer-closeout.md` §16
records that the trialled 1.0.4 is not this build and that nothing has been
installed as 1.0.5. The trial database was destroyed, so no stored row needs
correcting — luck, as the review said, not a control.

## CL3-O-1 — `build_application`'s docstring said the opposite — **Closed**

`adapters/http/composition.py` claimed `deployment` "is read from no
environment variable", which the rehearsal launcher had made false. The
docstring now separates the two seams: this function still reads nothing and
still defaults to the controlled pin, and the launcher's override is named
along with the `APP_ENVIRONMENT=test` restriction on it.

## CL3-O-2 — "three example values" — **Closed by Codex**

The §9 paragraph now reads "all four example values" and names them.

## CL3-O-3 — the reconciliation query is still string-matched — **Open**

`tests/test_snapshot_recovery_documentation.py` still asserts the query's text.
The join types and every `WHERE` literal were checked against the code by hand
in the source review, so it should run — but the previous defect in this same
block was an interpolation bug found by a human running it. Executing it once
against the disposable database, as part of whatever rehearsal replaces the
corrected step 10, remains the useful check. Tracked, not done.

Also still open and tracked: the fixture-guard test recommended by
[`phase-2-i-03-fixture-identity-correction.md`](phase-2-i-03-fixture-identity-correction.md).

## Checks

```text
./venv/bin/python -m pytest -q               → 1764 passed, 208 skipped, 0 failed
node --test foundry-module/tests/*.test.mjs  → 143 passed, 0 failed
node --check foundry-module/scripts/*.js     → 8 files, all pass
git diff --check                             → clean
```

The 208 skips are the database-backed tests; `TEST_DATABASE_URL` is not
configured in this session. That is the same posture as the previous reviews and
is stated rather than glossed. The count moved from 1,756 to 1,764: eight new
tests, all named above.

No rehearsal was run. No database, Foundry instance, endpoint, credential or
`docs/screenshots/` was read or modified.

## What this does not close

Unchanged by this record, and each one required before the Phase 2 gate:

- the maintainer-supervised real-export rehearsal — the 2026-08-06 attempt
  failed at the inactive-folder duplicate check, and Rehearsal A steps 6 and 7
  (preview, apply) remain unperformed because the preview route is disabled
  until the Phase 3 authentication boundary exists;
- Rehearsal B, the formal active-folder gate rehearsal;
- the signed Data Owner attestation, which does not exist in any form;
- recorded maintainer review of field profile `2026-08-03.1`;
- the remaining browser observations: credential revocation/cleanup and the
  negative removed-origin preflight;
- the independent gate recommendation and the Acceptance Authority's decision.

Phase 2 is not gate-ready, and this record does not make it so.
