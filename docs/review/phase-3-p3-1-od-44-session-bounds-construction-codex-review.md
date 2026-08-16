# P3.1 OD-44 session-bounds construction remediation — Codex independent review

Date: 2026-08-15

Role: Independent implementation reviewer under implementation-plan §0.3

Reviewed submission:
`phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md`

This is an implementation-review recommendation, not a security review and not
a P3.G1 acceptance decision. No Cyber or other external security-review service
was used.

## Recommendation

**Do not accept this remediation yet.** One Blocking construction finding is
open. The remediation closes the submitted 60-minute emergency-idle
counterexamples, but its replacement validator still admits a value outside the
numeric policy's type and makes N-66 unenforceable.

## Blocking F1 — `NaN` bypasses the derived policy validator and disables N-66

`SessionPolicy.derive()` deliberately accepts subclasses of `SessionSettings`
and reads each policy field once. That is sufficient only if the free-function
validator fully validates the value it reads. It does not.

`_validate_policy_values()` checks `value < 1` and `value > ceiling`, but does
not require `max_sessions_per_account` to be an integer. Both comparisons are
false for `float("nan")`, so the value is accepted
(`application/web/sessions.py:234-250`). `SessionPolicy.__post_init__()` calls
the same incomplete validator and therefore accepts it again
(`application/web/sessions.py:117-128`).

The value then reaches `_enforce_session_limit()`. For a NaN maximum,
`len(live) >= maximum` is always false, so no oldest session is revoked and the
accepted maximum of ten sessions is no longer enforced
(`application/web/sessions.py:492-508`).

This is reachable through the supported repository constructor without
`object.__new__`, mutation of a frozen object, a forged `SessionPolicy`, or a
private helper. A `SessionSettings` subclass can return the valid stored value
during its inherited `__post_init__`, then return NaN on the single read made by
`derive()`:

```python
reads = 0

class LyingSettings(SessionSettings):
    __slots__ = ()

    def __getattribute__(self, name):
        global reads
        if name == "max_sessions_per_account":
            reads += 1
            if reads > 1:
                return float("nan")
        return super().__getattribute__(name)

settings = LyingSettings(
    cookie_name="__Host-fb_session",
    cookie_secure=True,
    idle_minutes=60,
    absolute_hours=12,
    emergency_idle_minutes=15,
    emergency_absolute_minutes=60,
    max_sessions_per_account=10,
    login_transaction_cookie_name="__Host-fb_login_txn",
    oauth_transaction_minutes=10,
)
policy = SessionPolicy.derive(settings)

assert policy.max_sessions_per_account != policy.max_sessions_per_account
assert not (10 >= policy.max_sessions_per_account)
```

The reproduction produced:

```text
reads 2
policy max nan
11th session causes enforcement? False
```

The existing lying-settings regression covers only an out-of-ceiling integer
for `emergency_idle_minutes`, while the direct-policy cases cover 50, zero and
non-integral durations. They do not exercise non-integer or non-finite values
for `max_sessions_per_account`
(`tests/web/test_session_touch_lifetime.py:1025-1063`).

### Required remediation

Make `_validate_policy_values()` enforce the same whole-number rule as
`SessionSettings.__post_init__` for every integer policy field, explicitly
excluding `bool`. Do not rely only on ordering comparisons. Add regressions for
direct `SessionPolicy` construction and a lying `SessionSettings` subclass,
including NaN and representative non-integer values. The service-level test
should demonstrate that the eleventh live session still causes the oldest to be
revoked with the accepted maximum of ten.

The shared validation should ideally have one definition so the settings and
derived-policy gates cannot acquire different type semantics again.

## Confirmed parts of the remediation

The reviewed design does structurally remove `SessionIdlePolicy`, generates the
touch mapping by walking `AuthMethod`, derives the repository policy from
settings, and removes the independent policy/settings parameters from
`SessionService`. The focused PostgreSQL suite passed:

```text
54 passed in 1.66s
```

`git diff --check` also passed. These results do not close F1 because the suite
does not contain its counterexample.

No production service, credential, external account, or non-test database was
accessed. No files other than this review record were changed.

## Gate effect

P3.G1 remains open. After F1 is remediated, this construction package needs a
fresh implementation re-review. Acceptance remains with the maintainer.
