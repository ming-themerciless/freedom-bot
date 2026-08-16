# P3.1 OD-44 session-bounds construction remediation — Codex security-focused review

Date: 2026-08-15

Reviewed submission:
`phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md`

Related implementation review:
`phase-3-p3-1-od-44-session-bounds-construction-codex-review.md`

This is a defensive, security-focused source review of the local authorized
project. It is separately reported from the implementation review. It is not a
P3.G1 acceptance decision and does not claim use of Trusted Access, Codex
Security, an external scanner, or a professional penetration test.

## Recommendation

**Security-focused review does not recommend acceptance yet.** The Blocking
numeric-validation finding in the implementation review has a direct security
effect: it can disable the accepted per-account live-session limit. No separate
defect was found in the corrected idle-refresh SQL path.

## Blocking S1 — derived policy accepts a non-finite session-count maximum

N-66 bounds the number of simultaneously live credentials for one account.
`SessionSettings.__post_init__()` requires its numeric fields to be integers,
but the second, load-bearing validation boundary does not preserve that rule.

`SessionPolicy.derive()` reads values from subclasses of `SessionSettings`, then
passes them to `_validate_policy_values()`. That function applies only lower and
upper comparisons. A non-finite floating-point value can make both comparisons
false and is retained as `max_sessions_per_account`
(`application/web/sessions.py:130-165,212-255`). The policy's own
`__post_init__()` delegates to the same validator, so it adds no independent
type check (`application/web/sessions.py:117-128`).

The session-limit loop compares the integer number of live sessions with that
retained maximum. With the admitted non-finite value, the comparison never
enters the revocation loop (`application/web/sessions.py:492-508`). The result is
loss of the control that limits how many stolen or forgotten session credentials
can remain live for one account.

The local reproduction used only constructed settings and the comparison made
by the service. It did not access a route, credential, external system, or
non-test database. It confirmed that the invalid value survives derivation and
that a live-session count above the accepted maximum does not trigger the
enforcement comparison.

### Required security remediation

- Apply one shared whole-number validator to every integer session-policy field
  at both construction boundaries; explicitly reject booleans, floats and
  non-finite numeric values.
- Add a regression for a `SessionSettings` subclass whose derived value differs
  from the value observed by inherited construction validation.
- Add direct-policy cases for wrong numeric types, not only out-of-range integer
  values.
- Verify at the service boundary that creating the eleventh live session under
  a maximum of ten revokes the oldest session and records the audit event.

## Controls reviewed without a returned finding

- The touch duration is not accepted from a request or service caller. The SQL
  parameters are generated at repository construction from the derived policy.
- The persisted row's `auth_method` selects the idle duration, and the explicit
  classification table covers all current `AuthMethod` members.
- Unknown or unclassified methods fail closed rather than inheriting a default
  window.
- The conditional refresh requires a non-revoked row strictly inside both idle
  and absolute bounds.
- The refreshed idle expiry is clamped to the existing absolute expiry, which is
  not updated by touch.
- A zero-row repository result becomes the typed `SessionTouchRefused` at the
  service boundary.
- Repository and service construction no longer accept independent lifetime
  policy arguments.

These conclusions cover the reviewed service/repository boundary. The
submission correctly states that no P3.1 HTTP route calls `touch()` yet, so this
review does not claim end-to-end request-handler evidence.

## Verification boundary

The focused PostgreSQL-backed lifetime suite passed:

```text
54 passed in 1.66s
```

The new local validation reproduction also passed, and `git diff --check` was
clean. Passing tests do not close S1 because the current suite omits its input
class.

No production service, real credential, private account, player data, external
target, or non-test database was accessed. No network probing was performed.

## Gate effect

P3.G1 remains open. S1 must be remediated and independently re-reviewed before
this security-focused recommendation can change. Acceptance remains with the
maintainer.
