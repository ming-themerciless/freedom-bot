# Phase 3.4 Step 11.2 Focused Evidence and Stale-Test Reconciliation Handoff

Date: 2026-08-22  
Implementer: Gemini  
Review Target: Independent Codex Re-Review and Peter Duscha's Acceptance Authority Decision  
Status: **Step 11.2 Final Evidence Closure Complete — Awaiting Independent Re-Review & Decision**

---

## 1. Executive Summary & Authorization Boundary

Under Peter Duscha's explicit release authorization in [Handover information](../../docs/review/Handover%20information) and [phase-3-p3-4-remediation-release-policy-clarification.md](../../docs/review/phase-3-p3-4-remediation-release-policy-clarification.md), Gemini has resolved findings **R11.2-01** through **R11.2-05** strictly within test and documentation files.

**Governance Boundary**:
- This release does **not** accept final Step 11, close gate **P3.G4**, or release **Step 11.3**, **Step 12**, or **Step 13**.
- Step 11.3 remains **unreleased and verification-only**.
- No production templates, CSS, static assets, routes, application services, view models, authorization, sessions, CSRF implementation, database schemas, migrations, or player data were modified or touched.
- No live service contact was initiated, and no staging/deployment was authorized.

---

## 2. Remediation Findings & Exact Dispositions

### R11.2-01: Authenticated CSRF and Server-Owned Hidden-Field Evidence
- **Finding**: Previous handoff claimed session-backed CSRF token evidence across tested flows, but the flows tested were GET forms (audit search, council filter), navigation links (login), or deliberately sessionless / CSRF-exempt forms (emergency recovery).
- **Disposition**:
  - **Representative Authenticated POST Flow**: Added Flow 6 targeting `GET /v1/council/characters/{character_id}/links` using Council caller `callers["C"]` with a seeded character. This server-renders the R-25 character link grant POST form (`action="/v1/council/characters/{character_id}/links"`, `method="POST"`).
  - **Why Representative**: This flow exercises real ASGI execution, Council role authorization, dynamic URL parameter resolution against `app.routes`, optimistic concurrency versioning (`version="0"` server-owned hidden input), and session-backed CSRF token generation matching `csrf_token_for(settings, callers["C"])`.
  - **Route Matching & CSRF Verification**: Refactored `validate_rendered_no_js_fallback` to support parameterized route matching against `app.routes`, exact action/method matching, single hidden input named `csrf_token` with exact value equality against `csrf_token_for(settings, caller)`, and server-owned hidden field checking.
  - **Honest Flow Classifications**:
    - `GET /v1/audit`: Progressive HTMX search `GET` form (no CSRF).
    - `GET /v1/audit/results`: Dual-pagination `GET` link (no form).
    - `GET /v1/login`: Ordinary OAuth start and emergency recovery navigation links with no form.
    - `GET /v1/auth/emergency`: Emergency access `POST` recovery form — **deliberately sessionless and CSRF-exempt** under accepted contract (rate-limited, origin-checked, single-use token).
    - `GET /v1/council/characters`: Filter `GET` form (no CSRF).
    - `GET /v1/council/characters/{character_id}/links`: **Authenticated Council `POST` form with session-backed CSRF and server-owned `version` hidden input**.

---

### R11.2-02: TC-SEC-11 Production Validator & Shared Falsification
- **Finding**: `test_no_view_model_field_reaches_a_script_context_falsification` constructed synthetic HTML snippets and asserted BeautifulSoup visibility, rather than exercising the production validation helper.
- **Disposition**:
  - Extracted shared production validator `validate_script_contexts(template_sources: dict[str, str], allowed_script_src: str) -> None` in [tests/web/test_security_controls.py](../../tests/web/test_security_controls.py).
  - Shared falsification test `test_no_view_model_field_reaches_a_script_context_falsification` exercises `validate_script_contexts` with `pytest.raises(AssertionError)` across 8 controlled mutations.

---

### R11.2-03: Strict Canonical Correlation UUID Text Enforcement
- **Finding**: `_correlation_of` permitted leading/trailing whitespace and uppercase UUID spellings.
- **Disposition**:
  - Updated `_correlation_of` in [tests/web/test_oauth_refusal_audit.py](../../tests/web/test_oauth_refusal_audit.py) to locate exactly one `.reference-code` element, reject child elements/comments, and enforce `raw_text == str(UUID(raw_text))` directly.
  - Comprehensive acceptance/rejection matrix tested in `test_correlation_of_semantics_and_falsification`.

---

### R11.2-04: Fail Closed on Unrecognized Hidden Authority Fields
- **Finding**: `validate_rendered_no_js_fallback` verified required hidden fields but did not constrain additional hidden inputs. Injected client-controlled authority fields (`is_admin`, `role`, `character_id`) were ignored rather than failing closed.
- **Disposition**:
  - Refined `FormContract` in [tests/web/test_p3_4_accessibility.py](../../tests/web/test_p3_4_accessibility.py) with fail-closed allowed hidden fields semantics:
    - `allowed_hidden_fields: frozenset[str] | None = None`
    - In `validate_rendered_no_js_fallback`, `permitted_hidden_names` defaults to exact declared fields (`{"csrf_token"}` if `requires_csrf` + keys of `required_hidden_fields`) or explicit `allowed_hidden_fields`.
    - Every `<input type="hidden">` in the selected form is inspected: asserts non-empty `name` and asserts `name in permitted_hidden_names`, raising `AssertionError` on any unrecognized hidden input.
    - Forms with no hidden inputs permitted (e.g. CSRF-exempt emergency recovery or GET search forms) reject any hidden input.
    - Council grant form permits exactly `{"csrf_token", "version"}`.
  - **F-10 Falsification Expanded**:
    - Added demonstrably non-no-op mutation injecting `<input type="hidden" name="is_admin" value="true">` into real rendered `GET /v1/council/characters/{char_id}/links` response.
    - Verified `validate_rendered_no_js_fallback` fails with `match=r"unrecognized hidden input 'is_admin'"`.
    - Verified stripping only `hx-*` attributes passes cleanly under the exact hidden-field contract.
    - Confirmed all mutations in F-10 assert non-no-op changes before invoking the validator.

---

### R11.2-05: Correct Contradictory Durable Handoff History
- **Finding**: Durable handoff previously contained a contradictory statement in the R11-11 row claiming `GET /v1/login` provides a POST form with CSRF token and omitted documenting that emergency recovery is deliberately sessionless and CSRF-exempt.
- **Disposition**:
  - Corrected [docs/review/phase-3-p3-4-step-11-accessibility-handoff.md](../../docs/review/phase-3-p3-4-step-11-accessibility-handoff.md):
    - Replaced inaccurate R11-11 prose with honest descriptions: `GET /v1/login` documented as ordinary OAuth-start and emergency recovery links with no form; `GET /v1/auth/emergency` documented as deliberately sessionless, CSRF-exempt recovery POST form under accepted contract; `GET /v1/council/characters/{character_id}/links` documented as representative authenticated Council POST form with session-backed CSRF and exact server-owned `version` hidden field.
    - Updated F-10 description to explicitly document unrecognized extra hidden field rejection.
    - Verified no contradictory claims remain across the entire durable handoff.

---

## 3. Strict File Modifications Summary

All edits were confined to the authorized allowlist:

| File | Purpose of Modification |
| :--- | :--- |
| [tests/web/test_p3_4_accessibility.py](../../tests/web/test_p3_4_accessibility.py) | Fail-closed allowed hidden fields on `FormContract` / `validate_rendered_no_js_fallback`; injected unrecognized hidden input probe and non-no-op assertions in F-10 (R11.2-04). |
| [docs/review/phase-3-p3-4-step-11-accessibility-handoff.md](../../docs/review/phase-3-p3-4-step-11-accessibility-handoff.md) | Correct R11-11 description, login link-only classification, emergency CSRF-exempt classification, and F-10 table row (R11.2-05). |
| [tests/web/test_oauth_refusal_audit.py](../../tests/web/test_oauth_refusal_audit.py) | Canonical correlation UUID in `_correlation_of` and full rejection matrix (R11.2-03). |
| [tests/web/test_security_controls.py](../../tests/web/test_security_controls.py) | Extracted `validate_script_contexts` production validator and exercised across 8 falsifications (R11.2-02). |
| [docs/review/phase-3-p3-4-step-11-2-focused-evidence-handoff.md](../../docs/review/phase-3-p3-4-step-11-2-focused-evidence-handoff.md) | Document complete Step 11.2 remediation evidence closure. |
| External `walkthrough.md` | Artifact summary. |

---

## 4. Verification Results

### 1. Three Remediated Test Modules
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  venv-web/bin/python -m pytest -q -rs \
  tests/web/test_oauth_refusal_audit.py \
  tests/web/test_security_controls.py \
  tests/web/test_p3_4_accessibility.py
```
- `test_oauth_refusal_audit.py` + `test_security_controls.py`: **67 passed in 3.54s**
- `test_p3_4_accessibility.py`: **34 passed, 11 warnings in 2.49s**
- **Combined**: **101 passed, 11 warnings in 6.03s** (0 failed, 0 errors, 0 skipped).

### 2. Complete Step 11.2 Test Surface (8 suites)
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  venv-web/bin/python -m pytest -q -rs \
  tests/web/test_identity_migration_command.py \
  tests/web/test_oauth_refusal_audit.py \
  tests/web/test_p3_3_disclosure_and_bounds.py \
  tests/web/test_security_controls.py \
  tests/web/test_p3_4_accessibility.py \
  tests/web/test_p3_4_shell_and_components.py \
  tests/web/test_p3_3_audit_search.py \
  tests/web/test_p3_4_auth_and_system_views.py
```
- **Result**: **317 passed, 98 warnings in 15.96s** (0 failed, 0 errors, 0 skipped).

### 3. Static Asset & Repository Integrity Checks
```bash
sha256sum -c adapters/web/static/asset-integrity.sha256
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
venv-web/bin/python -m compileall -q application adapters domain tests
git diff --check
```
- `asset-integrity.sha256`: **All 3 files OK**
- `phase-3-visual-freeze-manifest.sha256`: **All 14 files OK**
- `compileall`: **0 syntax or bytecode errors**
- `git diff --check`: **Clean (0 whitespace/conflict errors)**

---

## 5. Work Deferred to Step 11.3 (Verification-Only)

- Complete 17-suite web regression run.
- Bot / Foundry test suites.
- Final gate checks and reconciliation across Phase 3 contracts.

---

## 6. Checkpoint Stop Notice

Gemini has completed all tasks required for **Step 11.2 Final Evidence Closure**.

In strict compliance with Peter Duscha's release authority policy:
- **Gate P3.G4 is NOT closed.**
- **Step 11.3 remains UNRELEASED and VERIFICATION-ONLY.**
- **Steps 12 and 13 are NOT started.**
- **No live services, staging environments, production databases, secrets, or real player data were accessed.**

Gemini **STOPS** at this checkpoint for independent Codex re-review and Peter Duscha's acceptance decision.
