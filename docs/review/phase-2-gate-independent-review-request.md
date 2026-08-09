# Independent review request — the complete Phase 2 gate package

Prepared: 2026-08-10
Requested by: Peter Duscha, Acceptance Authority
Implementer of the work under review: Claude
Reviewer: Codex, as Independent Reviewer
Repository state: branch `docs/platform-plan`, through commit `9dfe676` plus the
records added with this request

## What is being asked

Recommend whether the Phase 2 data-integrity, identity and migration-safety gate
may close. This is the review the plan requires as §13.3 operational evidence —
"independent review closure of every blocking security, identity, atomicity,
migration and recovery finding" — not a courtesy pass over a finished thing.

**Nothing in this package has been independently reviewed.** That is the reason
for the request and the first thing to weigh.

## Why independence matters unusually much here

On 2026-08-09 Claude acted as both reviewer and implementer, on the maintainer's
explicit instruction, to end a review cycle that had stopped producing value.
Concretely, Claude:

- raised findings CL3-B-1, CL3-I-1, CL3-I-2, CL3-O-1…O-3 **and then implemented
  the fixes for I-1, I-2 and O-1**;
- raised RA-1, RA-2, RA-3, RA-4, RA-5 during the rehearsals **and implemented or
  drafted the disposition of RA-1, RA-2 and RA-5**;
- chose the field classifications, the canonical ordering rule, the throughput
  unit and the 1,200 ms/MB limit — every one a judgement nobody has checked.

The maintainer authorised this and it is recorded in each affected document.
It is still a departure from §17, and the correct remedy is this review rather
than a note.

## Scope

Everything from commit `e1749db` onward, plus the standing Phase 2 package.

| Area | Where |
|---|---|
| CL3 remediation | `phase-2-i-03-cl3-remediation.md`, commit `e1749db` |
| Rehearsal A + findings | `phase-2-supervised-rehearsal-2026-08-09.md`, `phase-2-rehearsal-a-findings-2026-08-09.md`, commit `e2f0a4d` |
| RA-1 / RA-2 closures | commit `281dbec` — `domain/foundry_profile.py`, `application/foundry/parser.py`, `docs/rules/*` |
| Rehearsal B + attestation + RA-5 | commit `e54e5c0` — `phase-2-supervised-rehearsal-b-2026-08-09.md`, `phase-2-data-owner-attestation-2026-08-09.md` |
| Change-log C-10, C-11 | `docs/project-management/change-log.md` |
| Profile review, owner recommendations | `phase-2-field-profile-maintainer-review-2026-08-10.md`, `phase-2-owner-recommendations-2026-08-10.md` |

## Specific questions, in priority order

1. **Is CL3-B-1 genuinely closed?** The §9 window rule now spans the whole
   unresolved episode, and Rehearsal A step 10 observed the hit branch against
   real data. Does any reachable sequence still produce a false miss and
   authorise a second export?
2. **Is the RA-1 classification right?** Ten paths became `SNAPSHOT_ONLY` with
   no owning package, on the argument that favourites and sourcebook provenance
   will never be platform state. Should any of them instead be
   `legacy_authority_deferred` with a named package?
3. **Is C-10's canonical order correct and complete?** Integer-index keys
   ascending, then string keys by code point. Check the array-index definition
   against ECMAScript, and check `canonical_bytes` against the module's
   `canonical.js` for any case where the two still disagree.
4. **Is C-11's throughput criterion sound?** 1,200 ms/MB from the slowest
   sample, replacing wall-clock seconds. Is the limit defensible, and does
   measuring the slowest sample rather than the median hold under a noisy host?
5. **Is the attestation adequate §13.3 evidence?** Note the honest weakness
   recorded in its §2: every Actor is a create-candidate because the database was
   empty, so no identity conflict *could* arise. Does that satisfy "accounting
   for every Actor" as the plan intends, or does the gate need a reconciliation
   against a populated database?
6. **Is the field-profile review adequate?** Its own record states it was a
   blanket acceptance, resting on two rehearsals returning zero unclassified
   paths rather than a field-by-field session.
7. **Is anything claimed that was not done?** This package's history includes
   two prior evidence-accuracy findings (I-1, I-3R-1) where a document asserted
   more than the code delivered. Please look for a third.

## Known open items, declared rather than found

- **RA-3** — a `401` on a large upload surfaces as `network_failure`. Bounded to
  the `wsgiref` rehearsal launcher; referred to Phase 3, not fixed.
- **RA-4** — a step 10 fault injector must fault the `POST`, never the
  preflight. Procedure note; the operations guide does not yet say so.
- **CL3-O-1's sibling in the module** — `foundry-module/scripts/canonical.js:15`
  still describes the pre-C-10 key-order rule in a comment. Deliberately not
  edited, to avoid changing the bytes of an installed, rehearsed 1.0.5 build for
  a comment.
- **Caddy** — the temporary public route needs removing from the live config;
  the first revert restored a backup that already contained it.
- The **fixture-guard test** recommended by
  `phase-2-i-03-fixture-identity-correction.md` remains untracked work.

## Evidence boundary

- Rehearsals A and B ran against real Actor data in the live `the-guild` world,
  writing only to the disposable `freedom_test`. No character, mapping or import
  row was ever created. Both artifacts and both credentials were shredded.
- The 208 skipped tests are database-backed and skip without
  `TEST_DATABASE_URL`; that is the same posture as every prior review.
- Storage guarantees remain proven against same-process substitution, not a
  cross-account or multi-process experiment. Neither is a gate requirement.
- **Rehearsal A satisfies no gate criterion.** Rehearsal B and its attestation
  are two items of §13.3 evidence, not the gate.

## Verification

```text
./venv/bin/python -m pytest -q               → 1784 passed, 208 skipped
node --test foundry-module/tests/*.test.mjs  → 143 passed
node --check foundry-module/scripts/*.js     → 8 files
git diff --check                             → clean
```

## What a clean review would release

The Acceptance Authority's gate decision, and nothing else. Phase 3 additionally
requires an accepted §12.1 visual direction, a named security reviewer distinct
from the implementer, and OD-16 and OD-17 closed — none of which this package
touches.
