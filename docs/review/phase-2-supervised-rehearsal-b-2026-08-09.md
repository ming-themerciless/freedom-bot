# Phase 2 supervised Foundry rehearsal B — 2026-08-09 (active folder)

Status: **COMPLETE** — evidence produced; no gate decision is recorded and none
is implied.

Data Owner and supervising maintainer: Peter Duscha
Target database: `freedom_test` only
World / folder: `the-guild` · `/actors/Characters (active)` — `smob5eya6XVBAuIb`
Module: `freedom-blades-export` **1.0.5**
Field profile: **`2026-08-09.1`**
Endpoint delivery: the temporary public Caddy route from Rehearsal A, still in
place; reverted at teardown.

The signed reconciliation report is
[`phase-2-data-owner-attestation-2026-08-09.md`](phase-2-data-owner-attestation-2026-08-09.md).
This file is the run record.

## Steps (plan §7 / operations §7)

1. [x] `Characters (active)` selected; folder ID, path, deployment tuple and
       Actor count confirmed in the dialog before Submit.
2. [x] Submitted. Checksum `c47723a4…424055`, 32 Actors, 16,287,185 bytes,
       snapshot `f6155f61-4c60-42af-a28e-a4bd092b6e17`, principal
       `foundry-the-guild-b`, 22:09:03 UTC. One
       `snapshot_submission.accepted` audit event, `duplicate = false`.
3. [x] Reconciliation **preview only**, via `tools.bootstrap_manager` in
       rehearsal mode: **0 errors, 0 warnings**; 32 Actors, 32 create-candidates,
       0 already-mapped, 0 blocked, 0 absent.
4. [x] Every stable external Actor ID accounted for — all 32 listed in the
       attestation §3, all distinct, all carrying the selected folder ID.
5. [x] **Zero unexplained identity discrepancies**, the §13.3 acceptance
       threshold.
6. [x] Nothing applied: `characters` 0, `external_actor_mappings` 0,
       `snapshot_imports` 0.
7. [x] Sanitized attestation stored under `docs/review/`; no artifact, Actor
       name, mechanic, raw report or unnecessary player data committed.

## Two closures validated against real data

Both were predicted before the run and could have failed:

- **RA-1 closed.** Zero `unknown_snapshot_path` warnings. Profile
  `2026-08-09.1` classified every path in a *second* real folder, including one
  it had never seen.
- **RA-2 closed.** No `non_canonical_encoding` warning, so `canonical_encoding`
  is true — the ECMAScript ordering adopted as change-log C-10 matches what the
  module actually emits. Rehearsal A's artifact was non-canonical under the old
  rule; this one is canonical under the new one, from the same unchanged module.

  > **Note added 2026-08-10, on independent review finding I-1.** C-10 stated
  > the array-index boundary as `2**53 - 1` instead of `2**32 - 2`, corrected as
  > change-log **C-12**. **This observation is not disproved**: the artifact
  > evidently held no key in the disputed range — canonical decimals of ten or
  > more digits — so the verifier and the exporter agreed on it either way. What
  > is corrected is the claim that C-10 was complete, not this run's result. The
  > module is unchanged by C-12, so "from the same unchanged module" also still
  > holds.

## One new finding

**RA-5 — the preview took 9.566 s against C-9's accepted 5-second threshold.**
The run was healthy; the threshold was calibrated against synthetic Actors 233×
smaller than real ones, contradicting the project's own discovery finding F-F5.
Throughput was 587 ms/MB versus the benchmark's 728 ms/MB. Recorded in
[`phase-2-rehearsal-a-findings-2026-08-09.md`](phase-2-rehearsal-a-findings-2026-08-09.md)
and referred to the Acceptance Authority. **It is not waived here.**

## Teardown

- [x] Launcher and fault proxy stopped; no listener on 8757 or 8758.
- [x] Credential shredded.
- [x] Artifact shredded per the D-c retention decision; artifact root empty.
- [x] `freedom_test` truncated and verified: snapshots, audit events,
      idempotency keys, imports, characters and mappings all `0`, schema at
      `0004`.
- [x] **Caddy reverted 2026-08-09 22:38 UTC.** Restored from
      `Caddyfile.phase2-active-backup-2026-08-06`, not from
      `Caddyfile.pre-rehearsal-2026-08-09` — that backup had been captured after
      the route was added, so the first revert attempt was a no-op and the route
      stayed live for about two hours after teardown. Verified: the live config
      is back to 440 bytes with no `freedom-blades` block; responses from that
      hostname no longer carry `via: 1.1 Caddy`, no CORS header and no body, so
      the request no longer reaches this host; `foundry1`, `2` and `3` all serve
      normally. A Cloudflare DNS record still resolves the name and answers an
      empty `200` from the edge — no origin behind it, worth deleting for
      hygiene.
- [x] Downloaded fallback deleted from the maintainer's workstation.

## Gate boundary

Rehearsal B and its attestation are **two items** of §13.3 evidence. The field
profile review and the RA-5 ruling were both recorded on 2026-08-10, and the
attestation was signed the same day. Outstanding for the Phase 2 gate: the
independent review closure of every blocking finding — which does not exist and
cannot be supplied by the party that implemented these changes — and the
Acceptance Authority's decision.
