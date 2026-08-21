# P3.4 Step 3 independent review and acceptance

Date: 2026-08-20

Status: **ACCEPTED — STEP 3 CLOSED; STEP 4 RELEASED**

Implementer: Gemini

Independent reviewer: Codex

Acceptance authority: Peter Duscha

## Decision

Peter accepted P3.4 Step 3 on 2026-08-20 after Gemini completed the shared shell
and two bounded remediation passes and Codex completed independent re-review.
No Step 3 finding remains open.

This acceptance closed Step 3 only. Peter subsequently and separately released
the bounded Step 4 prompt on 2026-08-20. Neither decision closes P3.G4,
authorizes Step 5, staging or deployment, or authorizes secrets, live services,
or real data.

## Accepted deliverables

| File | Accepted SHA-256 |
|---|---|
| `adapters/web/templates/base.html` | `3048bd5bb561dfc5f26bfbf30353f7ddd474d804ebe65c2c5349a1b2f5566585` |
| `adapters/web/templates/includes/header.html` | `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796` |
| `adapters/web/templates/includes/footer.html` | `2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3` |
| `adapters/web/static/css/freedom-blades.e82fec19acd3.css` | `e82fec19acd3322066330a8a48a7d832446227fc9f805a0ffe54e6c7d9c12599` |
| `adapters/web/static/asset-integrity.sha256` | `08f6c81f09488749b6caefcc0da6c86efef03e220da8a2d2dc7334429a1f394b` |
| `tests/web/test_p3_4_shell_and_components.py` | `340e311602d8396bf38a7bf20b0d7206de87feec3e2ed96a7127406483657248` |

The accepted HTMX and emblem remained byte-identical to Step 2.

## Final independent evidence

| Check | Result |
|---|---|
| Visual freeze manifest | 14/14 passed |
| Static integrity manifest | 3/3 passed |
| Focused Step 3 suite | 37 passed |
| Supporting suite | 69 passed, 64 database-dependent skips because `TEST_DATABASE_URL` was absent |
| Combined suite | 106 passed, 64 database-dependent skips |
| Compilation | passed |
| `git diff --check` | passed |

The final re-review confirmed that ordinary inline handlers are rejected by the
same helper used for the complete production corpus, harmless probes pass, and
the copied manifest passes before temporary CSS mutation then fails because of
the changed temporary CSS bytes. All 23 Step 1 page/fragment digests were intact
at Step 3 closure.

## Next-step boundary

Peter explicitly released the separate bounded Step 4 prompt on 2026-08-20.
Gemini may execute Step 4 only and must stop at its checkpoint. Step 5 and all
later work remain unreleased.
