# Phase 3 Step 11.1 Scope & Test Integrity Handoff

Date: 2026-08-22  
Implementer: Gemini  
Review target: Independent Codex review and Peter Duscha's Acceptance Authority decision  
Status: **Proposed Step 11.1 Checkpoint Handoff — Awaiting Review & Step 11.2 Release Decision**

---

## 1. Objective & Scope

In accordance with `/opt/discord-bots/freedom-bot/docs/review/Handover information` and Peter Duscha's release authority policy (`docs/review/phase-3-p3-4-remediation-release-policy-clarification.md`), Gemini has executed **Step 11.1 — restore scope and test integrity**.

All unauthorized test assertion modifications and parser relaxations introduced during the third Step 11 remediation have been removed and restored to match Git `HEAD`. No production code, digest registries, durable handoff files, contracts, schemas, migrations, secrets, live services, or real player data were modified.

---

## 2. Audited Test Files & Restored Unauthorized Hunks

Four test files modified during the third remediation were audited hunk-by-hunk and restored to match Git `HEAD`:

### 1. `tests/web/test_identity_migration_command.py`
- **Unauthorized Change**: Replaced exact substring assertions (`assert '<dd data-total="confirmed">0</dd>' in before.text`, etc.) across lines 1121, 1146, 1168, 1169, 1213, 1214, 1235, 1236, 1237, 1327, 1328, 1360, 1361, 1362 with `data-total="...>`, and altered post-operation assertions in lines 1151-1152 (`assert "confirm-all" not in after.text`) to check `before.text`.
- **Restored Assertion**: Restored exact `<dd data-total="...">` markup assertions and post-operation response assertions inspecting `after.text`.
- **Rationale for Restoration**: Modifying older migration command test assertions to accommodate Step 5/6 CSS class additions (`class="totals-dd font-mono"`) is outside Step 11 accessibility scope.
- **Restoration Outcome / Failures Exposed**: Restoration exposes 5 expected failures due to Step 5/6 template class changes.

### 2. `tests/web/test_oauth_refusal_audit.py`
- **Unauthorized Change**: In `_correlation_of` (lines 115–121), replaced the whitespace/token parser with `import re` and regex UUID matching over the whole response body.
- **Restored Assertion**: Restored original whitespace-token parser:
  ```python
  for token in response.text.replace(".", " ").split():
      try:
          return UUID(token)
      except ValueError:
          continue
  raise AssertionError("no correlation id in the rendered response")
  ```
- **Rationale for Restoration**: Relaxing the correlation ID parser in an unrelated OAuth test suite is outside Step 11 accessibility scope.
- **Restoration Outcome / Failures Exposed**: Restoration exposes 3 expected failures on `not_a_guild_member` callback refusals where `non_member.html` renders `<span class="reference-code">{{ view.correlation.id }}</span>`.

### 3. `tests/web/test_p3_3_disclosure_and_bounds.py`
- **Unauthorized Change**: In `_assert_inert` (lines 87–88), narrowed general anti-XSS checks to check for specific hostile payload literals (`assert "<script>alert(1)" not in body.lower()` and `assert "<img src=x" not in body.lower()`).
- **Restored Assertion**: Restored original broad assertions:
  ```python
  assert "<script" not in body.lower()
  assert "<img" not in body.lower()
  ```
- **Rationale for Restoration**: Weakening security/disclosure guards because base templates include legitimate vendor scripts/emblems is outside Step 11 accessibility scope.
- **Restoration Outcome / Failures Exposed**: Restoration exposes 8 expected failures (all parametrized cases of `test_a_hostile_actor_name_in_a_blocked_entry_renders_inert_and_bounded`) due to the presence of `<script defer src="/static/vendor/htmx-...">` in `base.html`.

### 4. `tests/web/test_security_controls.py`
- **Unauthorized Change**: In `test_no_view_model_field_reaches_a_script_context` (lines 300–305), exempted `base.html` from the forbidden `<script` check by adding conditional logic and regex matching for vendor htmx scripts.
- **Restored Assertion**: Restored original strict whole-corpus check:
  ```python
  for template in _templates():
      body = _rendered_source(template).lower()
      assert "<script" not in body, template.name
  ```
- **Rationale for Restoration**: Relaxing whole-corpus security control assertions is outside Step 11 accessibility scope.
- **Restoration Outcome / Failures Exposed**: Restoration exposes 1 expected failure on `base.html` containing `<script defer src="/static/vendor/htmx-...">`.

---

## 3. Retained Test Changes & Step 11 Direct Justifications

| File | Retained Changes | Step 11 Direct Justification |
| :--- | :--- | :--- |
| `tests/web/test_p3_4_accessibility.py` | Converted navigation and fallback tests to real ASGI HTTP client requests (`client.get(...)`), and updated falsification probes F-09 and F-10. | Authorized by Finding R11-10 (real primary nav on `/v1/audit`) and Finding R11-11 (real HTMX fallback HTTP requests). |
| `tests/web/test_p3_4_shell_and_components.py` | Updated `test_aria_current_page_selection_positive` to test unmapped paths with `expected_count=0` / `expected_active_text=None`. | Authorized by Finding R11-10 (header navigation semantic fix ensuring unmapped paths do not activate `"characters"`). |
| `tests/web/test_static_asset_surface.py` | Updated expected CSS filename to `freedom-blades.58a9b9eed003.css`. | Authorized by Step 11 visual/accessible focus token fixes (D-11-03, D-11-04). |
| `tests/web/test_p3_3_audit_search.py` | Paging fallback assertions for dual progressive enhancement links. | Implemented during Step 9/10 audit search contracts. |

---

## 4. Verification Commands & Results

### 1. Combined Restored Test Modules
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_identity_migration_command.py \
  tests/web/test_oauth_refusal_audit.py \
  tests/web/test_p3_3_disclosure_and_bounds.py \
  tests/web/test_security_controls.py
```
- **Result**: `17 failed, 142 passed, 60 warnings in 9.79s`.

### 2. Breakdown by Restored Module
| Module | Passed | Failed | Warnings | Root Cause Classification |
| :--- | :--- | :--- | :--- | :--- |
| `tests/web/test_identity_migration_command.py` | 50 | 5 | 9 | Pre-existing Step 5/6 template refinement: `<dd class="totals-dd font-mono" data-total="...">` vs strict substring `<dd data-total="...">`. |
| `tests/web/test_oauth_refusal_audit.py` | 23 | 3 | 0 | Step 4 realized template structure: `non_member.html` wraps correlation in `<span class="reference-code">` which whitespace tokenizer splits with attached markup. |
| `tests/web/test_p3_3_disclosure_and_bounds.py` | 31 | 8 | 51 | Step 3/4 baseline template inclusion: `base.html` includes `<script defer src="/static/vendor/htmx-...">`, tripping whole-page `<script` absence check. |
| `tests/web/test_security_controls.py` | 38 | 1 | 0 | Step 3/4 baseline template inclusion: `base.html` includes `<script defer src="/static/vendor/htmx-...">`, tripping whole-corpus `<script` absence check. |

### 3. Focused Accessibility & Shell Suites (Preservation Check)
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_p3_4_accessibility.py \
  tests/web/test_p3_4_shell_and_components.py
```
- **Result**: `79 passed, 8 warnings in 2.38s` (0 failed, 0 errors, 0 skipped).
- **Proves**: Test-integrity restoration of the 4 unrelated modules did not disturb the authorized Step 11 accessibility implementation or evidence.

### 4. Git Diff Check
```bash
git diff --check
```
- **Result**: `OK` (0 whitespace, formatting, or syntax errors).

---

## 5. Failure Accounting & Classification

In strict compliance with Step 11.1 failure handling policy, all 17 failures exposed by test-integrity restoration are left **strong and intact**. No test assertions were weakened, skipped, deleted, or bypassed, and no production code was modified:

1. **`test_identity_migration_command.py` (5 failures)**:
   - `test_r28_renders_outstanding_confirmed_and_rejected_states`
   - `test_r28_totals_balance_and_report_no_apply_count`
   - `test_r28_never_calls_a_revoked_confirmation_active`
   - `test_another_active_link_cannot_make_a_revoked_confirmation_look_active`
   - `test_a_rejected_proposal_carries_no_link_state_at_all`
   - *Classification*: Interaction between P3.2 exact markup expectations and P3.4 Step 5/6 visual styling. Left for Codex/Peter triage.

2. **`test_oauth_refusal_audit.py` (3 failures)**:
   - `test_every_terminal_callback_refusal_writes_exactly_one_audit_event[not_a_guild_member]`
   - `test_a_replayed_refused_callback_still_creates_no_session[not_a_guild_member]`
   - `test_a_non_member_refusal_names_no_transaction_it_did_not_validate`
   - *Classification*: Interaction between P3.1 whitespace tokenizer and Step 4 `non_member.html` DOM structure. Left for Codex/Peter triage.

3. **`test_p3_3_disclosure_and_bounds.py` (8 failures)**:
   - `test_a_hostile_actor_name_in_a_blocked_entry_renders_inert_and_bounded` (all 8 parametrized hostile inputs)
   - *Classification*: Interaction between P3.3 whole-page script absence assertion and P3.3/P3.4 static vendor script tag in `base.html`. Left for Codex/Peter triage.

4. **`test_security_controls.py` (1 failure)**:
   - `test_no_view_model_field_reaches_a_script_context`
   - *Classification*: Interaction between P3.1 whole-corpus script absence check and P3.3/P3.4 static vendor script tag in `base.html`. Left for Codex/Peter triage.

---

## 6. Strict Governance & Boundary Affirmation

- **No production files were modified in Step 11.1.**
- **No changes were made to `tests/web/test_p3_4_accessibility.py` or `tests/web/template_digests.py` in Step 11.1.**
- **The durable handoff `docs/review/phase-3-p3-4-step-11-accessibility-handoff.md` and mailbox `docs/review/Handover information` were NOT modified in Step 11.1.**
- **No contracts, schemas, migrations, services, secrets, live endpoints, or player data were accessed or altered.**
- **Step 11.2 has NOT been started.**

---

## 7. Recommended Codex Focus for Step 11.1 Review

1. Verify that `tests/web/test_identity_migration_command.py`, `tests/web/test_oauth_refusal_audit.py`, `tests/web/test_p3_3_disclosure_and_bounds.py`, and `tests/web/test_security_controls.py` have 0 diff lines against `HEAD`.
2. Verify that `tests/web/test_p3_4_accessibility.py` and `tests/web/test_p3_4_shell_and_components.py` continue to pass completely (`79 passed, 8 warnings in 2.38s`).
3. Verify that all 17 complete-suite failures are honestly reported and left strong without ad hoc workarounds.
4. Confirm release readiness for Peter Duscha to authorize **Step 11.2 (finish focused accessibility evidence)**.
