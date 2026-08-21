# P3.4 master-prompt correction — review, acceptance, and re-release

Date: 2026-08-20

Correction owner: Claude, backend contract owner

Independent reviewer: Codex

Acceptance and release authority: Peter Duscha

## Corrected record

Peter accepts and re-releases the corrected P3.4 master prompt:

`docs/review/phase-3-p3-4-gemini-implementation-prompt.md`

| State | SHA-256 |
|---|---|
| Before correction | `0a396c8f5c29c2528f41ad93510eb0b3a0f4dcf86da9a5df528471209242f8ad` |
| Accepted and re-released | `cfe0517b45abc7d4dda4427c453af71348f8e147558373e581250dd851735fbb` |

The correction changed only two stale master-prompt descriptions:

1. **D-03-6 denial carrier.** Master-prompt §4 now identifies VM-22
   `DeniedView`, containing only `state` and closed-vocabulary `reason`, as the
   generic denial carrier. VM-02 remains confined to `non_member.html` and its
   intentional membership-recovery context. The byte-identical absent-object
   and unreachable-object `404` requirement remains unchanged.
2. **D-03-5 R-36 response.** Master-prompt §5.5 now records R-36 as `200`
   HTML rendering VM-13 in its `denied` state with
   `additional_provider = "no_additional_provider"`. It distinguishes that
   authenticated response from caller-matrix `U: ✗ 303`, which remains the
   unauthenticated navigation redirect to login.

## Independent review

Codex reviewed the complete two-hunk diff and found no blocking or important
finding. The review verified that:

- the corrected wording matches D-03-5, D-03-6, route contract §§2.3 and 5.1,
  the R-36 response row, and view models VM-02, VM-13 and VM-22;
- no scope, behavior, route, response, caller permission, CSRF/Origin rule,
  field, state, invariant, authority or historical acceptance changed; and
- `git diff --check` passed.

The focused D-03 and structural selection returned 48 passed and 45 skipped,
exit 0. The skips required an unconfigured disposable PostgreSQL database and
were not represented as database-backed evidence. No browser, migration,
staging, external network, live service, secret or real-data check was run.

Codex recommended acceptance. Codex did not release Gemini.

## Acceptance Authority decision

Peter/Acceptance Authority accepted the prompt-record correction and explicitly
re-released the corrected master prompt on 2026-08-20.

This is a documentation correction only. It changes no backend or contract
behavior and does not close P3.G4, I-06 or A-05. It does not authorize staging,
deployment, production use, external/live-service contact or real-player data.

The prior Step 1 blocker is resolved. Step 1 may be recorded `READY FOR STEP 2`
if its recheck finds no other discrepancy. This decision does **not** release
Step 2: a separate bounded Step 2 prompt must be reviewed and explicitly
released by Peter or his designated coordinator.

## Step 2 prompt release

After the Step 1 closure recheck found no other discrepancy and the separate
bounded prompt was prepared for review, Peter/Acceptance Authority explicitly
released
`docs/review/phase-3-p3-4-gemini-step-02-static-assets-prompt.md` on 2026-08-20.

Gemini may execute Step 2 only and must stop at its checkpoint. This release
does not authorize Step 3, close P3.G4, or authorize staging, deployment,
production use, external/live-service contact or real-player data.

## Step 2 remediation authority clarification

Codex's first Step 2 review returned four findings and a bounded remediation
prompt was provided to Gemini as a continuation of the already released Step 2.
The remediation prompt initially carried `HELD FOR REVIEW — NOT RELEASED` even
though Peter's Step 2 authorization remained active and the coordinator had
provided the remediation for execution. Peter clarified on 2026-08-20 that this
was a documentation error, not an unauthorized Gemini action.

The remediation therefore falls within the existing Step 2 release. No
retroactive widening of scope is claimed: the prompt was limited to the four
review findings and Gemini stopped at the Step 2 checkpoint. Step 3 remains
unreleased.
