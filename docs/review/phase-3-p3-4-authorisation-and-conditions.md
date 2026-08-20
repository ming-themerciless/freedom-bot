# P3.4 authorization and operating conditions

Date: 2026-08-19

Peter/Acceptance Authority accepted the recommended post-P3.G3 sequence after
closing P3.G3 and authorizing P3.4 in change-log `C-P3.3-K`.

## Decisions

1. **P3.4 development may begin** within the scope and review gates of the
   approved implementation plan.
2. **Deployment and public exposure remain unauthorized.** P3.4 authorization is
   development authorization only.
3. **I-06 will be addressed through isolated staging**, not by presenting local
   simulations as staging evidence. The staging environment must use separate
   infrastructure, database, Discord application/guild and credentials, with
   synthetic or explicitly authorized data.
4. **A-05 remains a prerequisite for exposure.** Establish the protected
   administrator account and enroll two independent real WebAuthn credentials,
   with login and recovery verified, before public staging or production access.
5. **D-03 remains a later integration gate.** Approve a frozen backend
   route/view-model contract before Gemini production integration; frontend
   assumptions may not silently add fields, authority or mutation behavior.

## Required order

```text
P3.4 development
    ↓
isolated staging and I-06 evidence
    ↓
A-05 administrator/WebAuthn readiness
    ↓
D-03 contract approval before Gemini production integration
    ↓
separate deployment/exposure decision
```

No production deployment, live-service contact, real-player-data use or public
exposure is authorized by this record.

## D-03 correction decision — 2026-08-19

Peter/Acceptance Authority accepted change-log `C-P3.4-A` as written and
authorized the bounded backend-contract correction package:

1. application-served `/static/` with `GET`/`HEAD`, no authentication,
   trusted-host enforcement, kill-switch availability, fingerprint-aware cache
   headers and structural inventory of mounts;
2. the implemented eight-field `ConfirmScope` definition;
3. the implemented `CharacterFilters(query, include_inactive)` definition;
4. accurate recording of VM-13's additive `csrf_token`;
5. R-36 recorded as `200` HTML with VM-13 denied, not `303`; and
6. a dedicated typed `DeniedView` containing only `state` and closed-vocabulary
   `reason`, preserving byte-identical object-denial and absent-object `404`
   responses.

This acceptance authorizes Claude/backend to implement those corrections. It
does **not** close D-03 or release Gemini. The corrected package must first pass
an independent Codex implementation review and a distinct security-focused
review, then return to Peter for contract acceptance and explicit release of the
Gemini implementation prompt. P3.G4, I-06 and A-05 remain open, and no staging
exposure, deployment, production use, live-service contact or real-player-data
use is authorized.

## D-03 contract acceptance and Gemini release — 2026-08-20

The corrected package passed the independent Codex implementation review and a
distinct security-focused review with no blocking findings. Peter/Acceptance
Authority accepted the corrected D-03 backend route/view-model contract and
explicitly released
`docs/review/phase-3-p3-4-gemini-implementation-prompt.md`.

D-03 is closed and Gemini may begin the bounded P3.4 production frontend
integration. P3.G4, I-06 and A-05 remain open. This decision does not authorize
staging exposure, deployment, production use, live-service contact or
real-player-data use. Evidence and the exact review limitation are recorded in
`docs/review/phase-3-d-03-codex-reviews-and-acceptance.md`; change-log entry
`C-P3.4-C` records the decision.

The earlier required-order diagram records the conditions as they stood on
2026-08-19. This dated acceptance satisfies D-03 earlier than that forecast and
supersedes its placement in the diagram; it does not waive or reorder the
remaining evidence and exposure gates in the approved delivery plan.
