# Phase 2 supervised Foundry rehearsal — 2026-08-09 (Rehearsal A)

Status: **COMPLETE** — Rehearsal A only. No gate decision is recorded and none
is implied.

Data Owner and supervising maintainer: Peter Duscha
Target database: `freedom_test` only
Foundry origin: `https://foundry1.rpgworld.org`
Foundry world ID: `the-guild`
Selected folder: the maintainer-selected non-live Actor folder, 35 Actors
Module ID and version: `freedom-blades-export` **1.0.5** (installed 2026-08-09;
the trialled 1.0.4 is a different build — CL3-I-2)
Field-profile version: `2026-08-03.1`
Endpoint delivery: temporary public Caddy route, reverted at teardown (see §F).

This record contains only operational outcomes, stable identifiers, counts and
checksums. It contains no credential, Actor name, mechanic, raw snapshot,
downloaded JSON, authorization header, database dump or browser-console output.

Supersedes nothing. The failed 2026-08-06 attempt remains recorded in
[`phase-2-supervised-rehearsal-2026-08-06.md`](phase-2-supervised-rehearsal-2026-08-06.md);
its history is retained deliberately (A-03).

## A. Preconditions and server-half smoke test

Performed by Claude before the maintainer session, with synthetic data only.

- [x] Module 1.0.5 installed to `foundry1` and `foundry3`, byte-identical to the
      repository tree, `module.json`, `scripts/`, `styles/` only, mode `0644`.
      The prior installs (1.0.1 on `foundry1`, 1.0.4 on `foundry3`) were backed
      up first. **Copying module files required no Foundry restart and caused no
      downtime**; the new build takes effect at the next world load.
- [x] All eight installed scripts pass `node --check`.
- [x] `freedom_test` at Alembic `0004`, all relevant tables empty.
- [x] Artifact root `/home/foundry/freedom-snapshots-rehearsal`, mode `0700`,
      accepted by the service's own startup checks.
- [x] Disposable credential issued per §5.2; the secret was written to a `0600`
      file, never printed, and configuration held only the digest.
- [x] Launcher loopback-only with the **controlled** deployment pin
      (`the-guild · 14.365 · dnd5e 5.3.3`). No `FREEDOM_SNAPSHOT_REHEARSAL_*`
      override was used at any point in this rehearsal.
- [x] §5.8 smoke test: `HTTP 201`, then `HTTP 200` with `duplicate: true` and
      the same snapshot ID; one `0600` artifact; zero characters and imports.
- [x] Origin policy at the server: allowed origin `204`, unlisted origin `403`.
- [x] Baseline restored before the maintainer session.

### A.1 Step 10 mechanics rehearsed server-side

Driven through a one-shot response-dropping proxy (rehearsal-only, loopback,
not part of the repository). Result: 1 snapshot, **1** audit event, 1
idempotency key, 0 characters, and the §9 query returning the original attempt's
event with `duplicate = false`.

This also discharges **CL3-O-3** — the §9 reconciliation query was *executed*
against PostgreSQL rather than string-matched — against synthetic data here, and
again against real data in §B step 10.

## B. Inactive-folder transport rehearsal

Maintainer-supervised, real export, real browser (Firefox).

- [x] Module enabled in `the-guild`; the four world settings confirmed.
- [x] GM dialog confirmed folder ID, full path, deployment tuple and Actor count
      before Submit.
- [x] Non-live folder selected, 35 Actors.
- [x] **Submission accepted.** Checksum `7a7d643e…ca510f`, snapshot
      `310e2a0c-b9f2-45bf-9809-03a2779bc6a2`, 9,839,520 bytes, exporter version
      recorded as `1.0.5`, principal `foundry-the-guild`, `21:01:23 UTC`.
- [x] Three-way checksum agreement: module receipt = `foundry_snapshots.checksum`
      = SHA-256 of the stored artifact bytes = SHA-256 of the downloaded
      fallback. The module reused the exact prepared snapshot for the download,
      as `workflow.js` documents.
- [x] Preview via `tools.bootstrap_manager` against `freedom_test`: **0 errors,
      36 warnings, 4.92 s**, inside the accepted 5-second threshold. Nothing was
      written. (The HTTP preview route remains disabled until the Phase 3
      authentication boundary exists.)
- [x] Foundry Actor, Item and Folder counts and the `Actors (shared)` compendium
      unchanged throughout.
- [x] `git status` showed no artifact, dump, log or Actor content.
- [x] **Step 10 passed.** A duplicate delivery of the pinned bytes committed
      upstream (`upstream=200`, the replay path) and its response was dropped;
      the page was then reloaded and the pin lost. The §9 reconciliation over the
      whole episode returned **exactly one row: the original attempt's event,
      `duplicate = false`, at 21:01:23**, joined by checksum to the snapshot row.
      The same-key retry wrote no audit event, exactly as the corrected
      procedure states.
- [x] No fresh submission was made during the reconciliation.

**This observation closes the CL3-B-1 window defect, and nothing wider.** Under
the superseded procedure the operator would have queried a window around the
*retry*, found nothing, recorded a miss, and been authorised to prepare a fresh
export — producing a second pending artifact for one real submission. The
whole-episode window is what this run exercised, and it worked.

> **Correction, 2026-08-10, on independent review finding B-1.** This paragraph
> previously read "This is the CL3-B-1 closure by observation." It was not, and
> the record should not have said so.
>
> **What this run did not exercise: the late-commit sequence.** The injected
> fault dropped the *response* of a request the service had already served —
> `upstream=200`, the replay path — so the acceptance event was committed before
> the reconciliation query ran. That is the hit branch, and observing it says
> nothing about the branch where the query runs while a transaction is still
> open and the commit lands afterwards. A client timeout does not establish that
> the server has stopped, and this run never tested a case where it mattered.
>
> That sequence is now covered by `tests/test_snapshot_recovery_settlement.py`
> and guarded by the settlement condition added to §9 step 1; the corrected §9
> step 10 records that inducing it against a live rehearsal is deliberately not
> attempted. Nothing observed on 2026-08-09 is withdrawn — the hit branch, the
> checksums, the single audit event and the silent same-key replay all stand.
> What is withdrawn is the claim that observing them closed the finding.

## C. Credential-confidentiality observation (§8.1)

- [x] Step 2 — settings under `freedom-blades-export.` matching
      `credential|secret|token`: **0**.
- [x] Step 3 — the secret searched across every value in the world state vended
      to an **ordinary player** in a separate session: **false**.
- [x] Step 4 — credential rotated. New principal id `foundry-the-guild-r2`; the
      old credential returned `401` afterwards; the old secret was shredded.

Deviations recorded rather than glossed:

- §8.1 specifies a disposable rehearsal world; this was performed in the live
  `the-guild`, because that is where 1.0.5 is installed. Both console snippets
  are read-only. Inspecting the real world's setting store is the stronger
  evidence.
- Step 3 necessarily placed the synthetic secret in a player browser's console
  history, which is why step 4 mandates rotation regardless of outcome.

The rotation produced additional evidence: a deliberately malformed request
under the new credential wrote **one** `snapshot_submission.refused` event and
nothing else — no snapshot row, no artifact, no accepted event. That is one of
the mandatory Phase 2 tests, observed against real PostgreSQL.

## D. Real-browser origin observation (§8.2)

Previously **never run**; `curl` does not enforce CORS, so no prior check had
exercised the supported browser workflow.

- [x] Positive: submission from the allowed origin accepted. Checksum
      `b05e2379…3799bb`, snapshot `bdbc7572-7b44-4850-90b0-d2113201eaea`,
      35 Actors, principal `foundry-the-guild-r2`, `21:41:42 UTC`. Preflight
      `204` with `Access-Control-Allow-Origin` naming the origin.
- [x] Negative: the service was restarted with the allowlist **emptied**; the
      same preflight returned `403`, the browser refused to send the `POST` at
      all, and the 9.8 MB body never left the client. Server state was
      byte-for-byte unchanged across the attempt.
- [x] Allowlist restored and re-verified at `204`.

Incidental result worth keeping: the two accepted submissions are 35 Actors and
**exactly 9,839,520 bytes each with different checksums**, because `exportedAt`
differs. Two exports of an unchanged folder are two identities, as the contract
requires.

## E. Findings

Recorded separately in
[`phase-2-rehearsal-a-findings-2026-08-09.md`](phase-2-rehearsal-a-findings-2026-08-09.md).
Four findings, none of which a synthetic fixture could have produced.

## F. Teardown

- [x] Launcher and fault proxy stopped; no listener remains on 8757 or 8758.
- [x] Credential shredded.
- [x] Both real artifacts shredded; artifact root empty.
- [x] `freedom_test` truncated and verified: snapshots, audit events,
      idempotency keys, imports, characters and mappings all `0`, schema at
      `0004`.
- [ ] Caddy reverted to `Caddyfile.pre-rehearsal-2026-08-09` — **maintainer
      action**, requires `sudo`.
- [ ] Downloaded fallback deleted from the maintainer's workstation —
      **maintainer action**.
- [x] No artifact, Actor name, mechanic, credential or console output entered
      Git.

### Public exposure during this rehearsal

A temporary Caddy route published `freedom-blades.rpgworld.org` to the public
internet for the duration, proxying to the rehearsal service. It was necessary
because the maintainer's browser could not reach the host over an SSH tunnel.
The route was credential-gated and submit-only: an unauthenticated request
receives `401`, and the submit scope applies nothing. **One unsolicited `GET /`
from the internet was observed within minutes of the route going up**, answered
`404`. This is the reason such a route should be short-lived and is recorded
here rather than left to memory.

## Gate boundary

**This rehearsal does not satisfy the Phase 2 gate.** It is Rehearsal A:
transport and integration evidence for a non-live folder. Rehearsal B — the
active-folder run that produces the signed Data Owner attestation — has not been
run, no attestation exists, and the field profile has no recorded maintainer
review.
