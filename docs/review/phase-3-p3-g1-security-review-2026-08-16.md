# P3.G1 distinct security-focused review

Date: 2026-08-16

Reviewer: Codex, acting as independent security-review assistant

Outcome: **changes requested; P3.G1 remains open.**

This is the separately reported security-focused pass required by the Phase 3 delivery plan. It is distinct from the clean implementation re-review of the composition-lifecycle remediation. It does not accept P3.G1, close RAID I-09/I-10, authorize P3.2, or replace the maintainer's gate decision.

## Findings

### [Blocking] N-32's per-account WebAuthn assertion budget has no production consumer

N-32 requires both a per-source-IP WebAuthn assertion budget and a per-platform-account budget. `RateLimiter.check_account()` implements the latter using `webauthn_assertions_per_account` and `webauthn_account_window_minutes` (`application/web/rate_limit.py:89-107`), but no production call site invokes it. The only calls found in the repository are direct consumer tests in `tests/web/test_settings_construction_validation.py`.

Both R-07 and R-08 consume only `_consume_rate_limit(..., LimitedAction.WEBAUTHN_ASSERTION, client_ip=...)` (`adapters/web/app.py:909-954`). `BreakGlassService.complete_assertion()` resolves the credential and therefore the protected platform account, but does not consume an account bucket (`application/web/breakglass.py:171-256`). Consequently, attempts distributed across source addresses are bounded only per address; the accepted ten-attempt, sixty-minute account budget is inoperative.

The green TC-LIM-06 test proves that `check_account()` counts correctly when called directly. It does not prove that a WebAuthn request reaches it, and the production caller search proves that none does.

Remediation must consume the account budget after the credential has been safely resolved but before signature verification/session creation, in a transaction whose increment survives a refused assertion. Unknown credentials must remain indistinguishable to the caller, and the design must avoid creating an account-existence oracle. Add direct-HTTP and real-PostgreSQL evidence that attempts for one credential/account across multiple source addresses share one budget and that a refusal still spends it.

### [Blocking] N-33's per-grant recovery-attempt counter rolls back on every refused matched grant

`BreakGlassService.redeem_recovery_grant()` increments `recovery_grants.attempt_count`, reads it, and then raises `AuthenticationFailure` when the cap is exceeded or when the grant cannot be consumed (`application/web/breakglass.py:280-326`). R-09 runs that whole service call inside `_in_transaction()` and records an authentication failure only after the exception has rolled the transaction back (`adapters/web/app.py:973-1007`). The increment therefore does not survive the refused attempt it is meant to count.

This affects attempts that match a real but expired, invalidated, or already-consumed grant. Such an attempt updates the row, subsequently fails `consume()`, and rolls the update back. Repeating it from multiple source addresses bypasses the per-grant cap; only the separate per-IP counter advances.

The existing `test_the_per_grant_attempt_cap_refuses_the_sixth_attempt` does not exercise this path (`tests/web/test_break_glass_login.py:511-539`). It sends `"wrong-" + token`, which matches no grant row, and explicitly asserts that the stored attempt count remains zero after all five refused transactions. It never presents a token that matches an expired, invalidated, or consumed grant, never observes a committed increment, and never reaches a sixth matched attempt. Its name and opening sentence therefore overstate what it proves.

Move the per-grant attempt accounting to an independently committed boundary, or otherwise make the failed authentication transaction preserve only the bounded counter without preserving any failed session/audit work. Add direct-HTTP and real-PostgreSQL evidence using a matched non-live grant from multiple source addresses: attempts one through the configured limit must durably advance the same grant counter, the next must return the coarse rate-limited outcome, and no session may be created. Correct the existing test's name/claim or replace it with evidence for the actual control.

## Areas reviewed without an additional finding

- N-67's continuity-scope create/revoke allowlist, provenance propagation, ratification boundary, protected mapping triggers, direct-database constraint, and sequence tests.
- PKCE verifier encryption, row/provider/version AAD binding, conditional single-use consumption, verifier erasure, concurrent callback behavior, and coarse failure handling.
- Session creation, rotation, absolute/idle expiry clamping, touch refusal, revocation, one-successor constraints, CSRF derivation from the session ID, constant-time verification, and session rotation changing the CSRF token.
- Break-glass capability resolution and the restriction that emergency-derived administrator provenance survives an ordinary login until full-scope ratification.
- Canonical settings authority, provider/engine derivation and immutability, captured request authority, failed-startup cleanup, and one-way single-claim composition lifecycle.
- Migrations 0006-0009, including attribution, append-only mapping events, provenance constraints/triggers, session/OAuth completion binding, linear rotation objects, and upgrade/downgrade safety evidence.
- Authentication refusal audit separation and the IP rate-limit increment's independent transaction.

No further blocking, important, or minor security finding was identified in those reviewed areas.

## Verification performed

- `rg` production-caller searches for `check_account`, `webauthn_assertions_per_account`, `recovery_attempts_per_grant`, `note_attempt`, and `attempts_for`.
- `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest -q -rs tests/web/test_break_glass_escalation.py tests/web/test_break_glass_login.py tests/web/test_oauth_flow.py tests/web/test_oauth_completion_binding.py tests/web/test_oauth_refusal_audit.py tests/web/test_rate_limits_and_outage.py tests/web/test_security_controls.py tests/web/test_sessions.py tests/web/test_session_rotation_integrity.py tests/web/test_session_rotation_lifetime.py tests/web/test_session_touch_lifetime.py tests/web/test_canonical_settings_graph.py tests/web/test_request_authority_and_lifecycle.py tests/test_database_schema.py tests/test_migration_safety.py tests/test_oauth_completion_binding_migration.py`
  - **414 passed**, 20 dependency deprecation warnings, 0 skipped.
- `git diff --check`
  - clean before this report was written.

The passing suite does not negate the findings: the missing per-account production call is tested only by invoking the otherwise-unused method directly, while the recovery-grant case asserts rollback-compatible zero for a token that matches no row.

No production code was changed by this review.

---

## Remediation pointer (appended 2026-08-16 by the working Technical Lead)

The two findings above are **unchanged**; nothing in this section edits, softens
or answers the review on its own behalf. It records only where the response
lives.

Both blocking findings were accepted without qualification and remediated the
same day in
`docs/review/phase-3-p3-g1-security-review-remediation-submission-2026-08-16.md`:

1. **N-32's per-account budget** is consumed by R-08, in its own committed
   transaction, after the presented credential has been resolved and before any
   verification. A credential that resolves to no account spends an equivalent
   keyed per-credential budget, so the limit does not become an account-existence
   oracle. Evidence: **TC-BG-16**, direct HTTP against real PostgreSQL, eleven
   attempts from eleven source addresses sharing one bucket, all of them
   refusals.
2. **N-33's per-grant counter** is spent by R-09 through
   `BreakGlassService.note_recovery_attempt()`, which **returns** its refusal
   instead of raising it, so the increment commits and survives the refusal it
   counts. `note_attempt()` is now one `UPDATE … RETURNING` statement. Evidence:
   **TC-BG-17**, direct HTTP against real PostgreSQL, five durable increments
   against a **matched** invalidated grant from five source addresses and a sixth
   attempt refused with no session created.
3. `test_the_per_grant_attempt_cap_refuses_the_sixth_attempt` is renamed
   `test_a_token_matching_no_grant_counts_against_no_grant_record` and re-scoped
   to the property it actually proved, as the review required.

**This does not accept P3.G1, close RAID I-09/I-10 or authorize P3.2.** The
outcome recorded above — *changes requested* — stands until an independent
security re-review of that remediation and the maintainer's gate decision.
