"""TC-AUTH-11 over **every** terminal exit of R-04, not only the two that raised.

The gap this file closes: five of R-04's terminal refusals returned a redirect
and wrote no audit event, and the suite did not notice because the provider-outage
test asserted the redirect and the absence of a session — both of which are true
of a refusal that records nothing at all.

Each branch below asserts the same seven things, which is why they are one
parametrization rather than eleven near-copies:

1. the safe response, and the correlation id the caller is shown;
2. no session row;
3. no OAuth token grant;
4. **exactly one** refusal audit event *for that correlation id*;
5. no success audit event;
6. no secret and no attacker-controlled raw value in the audit payload, the
   rendered response, the `Location` header or the log; and
7. a second, identical callback still creates no session.

Point 4 is scoped to the correlation id deliberately. "Exactly one refusal event
in the table" would be a weaker claim that the rate-limit branch could not make at
all — it spends its budget by issuing twenty callbacks first, each of which
correctly records its own refusal. The contract's unit is the *attempt*.

Cookies are sent as an explicit `Cookie` header rather than through `httpx`'s
per-request `cookies=`, which is deprecated and would add a warning per test.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable
from uuid import UUID

import pytest
from bs4 import BeautifulSoup
from sqlalchemy import select, text

from adapters.database.tables import (
    audit_events,
    oauth_token_grants,
    platform_accounts,
    sessions,
)
from application.web.refusals import (
    LOGIN_REFUSED_ACTION,
    LoginRefusalReason,
    UNBOUND_ENTITY_ID,
    UNBOUND_ENTITY_TYPE,
)
from tests.web.no_js_helpers import validate_exact_canonical_correlation_uuid
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database

TRANSACTION_COOKIE = "__Host-fb_login_txn"

#: The authorization code and the state the tests present. Both are secrets in
#: the sense that matters here: neither may appear in an audit payload, a
#: response or a log line.
CODE = "the-authorization-code-x7f3"

#: A transaction cookie that is not a UUID, shaped so that echoing it would be
#: unmistakable in any output.
MALFORMED_COOKIE = "not-a-uuid-<script>alert(1)</script>"


def _cookie_header(value: str) -> dict[str, str]:
    return {"Cookie": f"{TRANSACTION_COOKIE}={value}"}


#: The test client is not the platform. `httpx` logs the request line of every
#: call it makes, which contains the query string the *test* constructed — so it
#: reports the authorization code the test just sent, from inside the test
#: process, before any application code runs. Including it in the leak assertion
#: would assert something about `httpx`'s logging, not about the portal's.
_HARNESS_LOGGERS = ("httpx", "httpcore", "asyncio")


def _application_log(caplog) -> str:
    """Everything the *application* logged, and nothing the harness did."""
    return "\n".join(
        record.getMessage()
        for record in caplog.records
        if not record.name.startswith(_HARNESS_LOGGERS)
    )


async def _start(client) -> str:
    """Begin a flow and return the transaction cookie it set.

    The client's cookie jar is **emptied** afterwards. `httpx.AsyncClient` keeps
    cookies across requests like a browser, so a branch that means "no transaction
    cookie" would otherwise send the one the start route just set and complete a
    perfectly successful login. Clearing the jar makes every branch below send
    exactly the cookie it names in its `Cookie` header, and nothing else.
    """
    response = await client.get("/v1/auth/discord/start")
    assert response.status_code == 303
    for cookie in response.headers.get_list("set-cookie"):
        if cookie.startswith(f"{TRANSACTION_COOKIE}="):
            client.cookies.clear()
            return cookie.split("=", 1)[1].split(";", 1)[0]
    raise AssertionError("the start route set no login-transaction cookie")


def _correlation_of(response) -> UUID:
    """The correlation id the caller was actually shown, from wherever it is."""
    if response.status_code == 303:
        location = response.headers["location"]
        _, _, query = location.partition("?")
        for pair in query.split("&"):
            key, _, value = pair.partition("=")
            if key == "correlation":
                try:
                    parsed = UUID(value)
                except ValueError as exc:
                    raise AssertionError(f"correlation query parameter {value!r} is not a valid UUID") from exc
                if str(parsed) != value:
                    raise AssertionError(f"correlation query parameter {value!r} is not in exact canonical UUID format")
                return parsed
        raise AssertionError(f"no correlation id in {location!r}")

    # For rendered refusal pages (e.g. 403, 409, 503), delegate to shared strict validator
    return validate_exact_canonical_correlation_uuid(response)


# ---------------------------------------------------------------------------
# The branches
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Branch:
    """One terminal exit of R-04, and what the contract says it owes."""

    name: str
    #: Arranges the fault and issues the callback. Returns the response.
    issue: Callable
    reason: str
    #: The caller-visible failure code, deliberately coarser than the reason.
    failure_code: str | None
    entity_type: str
    status: int = 303

    def __str__(self) -> str:  # pragma: no cover - identifies the parametrization
        return self.name


async def _issue_rate_limited(client, provider):
    # N-18's callback budget is twenty per source address per ten minutes. The
    # twenty spending requests are themselves refusals and record their own
    # events; the assertions below are scoped to the twenty-first attempt.
    for _ in range(20):
        await client.get("/auth/discord/callback")
    transaction = await _start(client)
    state = provider.authorization_calls[-1][0]
    return await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": CODE},
        headers=_cookie_header(transaction),
    )


async def _issue_missing_cookie(client, provider):
    await _start(client)
    state = provider.authorization_calls[-1][0]
    return await client.get(
        "/auth/discord/callback", params={"state": state, "code": CODE}
    )


async def _issue_missing_state(client, provider):
    transaction = await _start(client)
    return await client.get(
        "/auth/discord/callback",
        params={"code": CODE},
        headers=_cookie_header(transaction),
    )


async def _issue_missing_code(client, provider):
    transaction = await _start(client)
    state = provider.authorization_calls[-1][0]
    return await client.get(
        "/auth/discord/callback",
        params={"state": state},
        headers=_cookie_header(transaction),
    )


async def _issue_malformed_cookie(client, provider):
    await _start(client)
    state = provider.authorization_calls[-1][0]
    return await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": CODE},
        headers=_cookie_header(MALFORMED_COOKIE),
    )


async def _issue_state_mismatch(client, provider):
    transaction = await _start(client)
    return await client.get(
        "/auth/discord/callback",
        params={"state": "not-the-minted-state", "code": CODE},
        headers=_cookie_header(transaction),
    )


def _provider_fault(**flags):
    async def issue(client, provider):
        transaction = await _start(client)
        state = provider.authorization_calls[-1][0]
        for flag, value in flags.items():
            setattr(provider, flag, value)
        return await client.get(
            "/auth/discord/callback",
            params={"state": state, "code": CODE},
            headers=_cookie_header(transaction),
        )

    return issue


BRANCHES = (
    Branch(
        name="callback_rate_limited",
        issue=_issue_rate_limited,
        reason=LoginRefusalReason.RATE_LIMITED.value,
        failure_code="rate_limited",
        entity_type=UNBOUND_ENTITY_TYPE,
    ),
    Branch(
        name="missing_transaction_cookie",
        issue=_issue_missing_cookie,
        reason=LoginRefusalReason.CALLBACK_PARAMETERS_MISSING.value,
        failure_code="transaction_unknown",
        entity_type=UNBOUND_ENTITY_TYPE,
    ),
    Branch(
        name="missing_state",
        issue=_issue_missing_state,
        reason=LoginRefusalReason.CALLBACK_PARAMETERS_MISSING.value,
        failure_code="transaction_unknown",
        entity_type=UNBOUND_ENTITY_TYPE,
    ),
    Branch(
        name="missing_authorization_code",
        issue=_issue_missing_code,
        reason=LoginRefusalReason.CALLBACK_PARAMETERS_MISSING.value,
        failure_code="transaction_unknown",
        entity_type=UNBOUND_ENTITY_TYPE,
    ),
    Branch(
        name="malformed_transaction_cookie",
        issue=_issue_malformed_cookie,
        reason=LoginRefusalReason.TRANSACTION_COOKIE_MALFORMED.value,
        failure_code="transaction_unknown",
        entity_type=UNBOUND_ENTITY_TYPE,
    ),
    Branch(
        name="transaction_not_live_or_state_mismatch",
        issue=_issue_state_mismatch,
        reason=LoginRefusalReason.TRANSACTION_NOT_LIVE_OR_STATE_MISMATCH.value,
        failure_code="transaction_unknown",
        entity_type="oauth_transaction",
    ),
    Branch(
        name="provider_unavailable_at_exchange",
        issue=_provider_fault(unavailable_at_exchange=True),
        reason=LoginRefusalReason.PROVIDER_UNAVAILABLE.value,
        failure_code="provider_error",
        entity_type="oauth_transaction",
    ),
    Branch(
        name="provider_unavailable_at_verification",
        issue=_provider_fault(unavailable_at_verify=True),
        reason=LoginRefusalReason.PROVIDER_UNAVAILABLE.value,
        failure_code="provider_error",
        entity_type="oauth_transaction",
    ),
    Branch(
        name="provider_refused_at_exchange",
        issue=_provider_fault(refuse_exchange=True),
        reason=LoginRefusalReason.PROVIDER_REFUSED.value,
        failure_code="provider_error",
        entity_type="oauth_transaction",
    ),
    Branch(
        name="provider_refused_at_verification",
        issue=_provider_fault(refuse_verify=True),
        reason=LoginRefusalReason.PROVIDER_REFUSED.value,
        failure_code="provider_error",
        entity_type="oauth_transaction",
    ),
    Branch(
        name="not_a_guild_member",
        issue=_provider_fault(is_member=False),
        reason=LoginRefusalReason.NOT_A_GUILD_MEMBER.value,
        failure_code=None,
        entity_type="external_identity",
        status=403,
    ),
)


# ---------------------------------------------------------------------------
# The parametrized contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("branch", BRANCHES, ids=[b.name for b in BRANCHES])
async def test_every_terminal_callback_refusal_writes_exactly_one_audit_event(
    branch, client, provider, migrated_database, caplog
):
    """TC-AUTH-11, branch by branch. One event, one correlation id, no secret."""
    caplog.set_level(logging.DEBUG)
    response = await branch.issue(client, provider)

    # 1. The safe response, and the correlation id the caller can quote.
    assert response.status_code == branch.status
    if branch.failure_code is not None:
        assert f"failure={branch.failure_code}" in response.headers["location"]
    correlation_id = _correlation_of(response)

    with migrated_database.connect() as connection:
        rows = (
            connection.execute(
                select(audit_events).where(
                    audit_events.c.correlation_id == correlation_id
                )
            )
            .mappings()
            .all()
        )
        session_count = connection.execute(
            select(text("count(*)")).select_from(sessions)
        ).scalar_one()
        grant_count = connection.execute(
            select(text("count(*)")).select_from(oauth_token_grants)
        ).scalar_one()
        successes = connection.execute(
            select(text("count(*)"))
            .select_from(audit_events)
            .where(audit_events.c.action == "auth.login.succeeded")
        ).scalar_one()

    # 2 and 3. Nothing was granted.
    assert session_count == 0, "a refused callback must create no session"
    assert grant_count == 0, "a refused callback must store no provider token"

    # 4. Exactly one refusal event, for this attempt.
    assert len(rows) == 1, f"expected one audit event, found {[r['action'] for r in rows]}"
    event = rows[0]
    assert event["action"] == LOGIN_REFUSED_ACTION
    assert event["entity_type"] == branch.entity_type
    assert event["payload"]["reason"] == branch.reason
    assert event["source"] == "web"

    # 5. And no success event anywhere.
    assert successes == 0

    # 6. No secret, and no attacker-controlled raw value, in anything the
    #    platform wrote or rendered.
    state = provider.authorization_calls[-1][0] if provider.authorization_calls else ""
    forbidden = [
        CODE,
        MALFORMED_COOKIE,
        "synthetic-access-token",
        "synthetic-refresh-token",
    ]
    if state:
        forbidden.append(state)
    haystacks = {
        "audit payload": str(dict(event["payload"])),
        "audit entity id": str(event["entity_id"]),
        "response body": response.text,
        "location header": response.headers.get("location", ""),
        "application log": _application_log(caplog),
    }
    for label, haystack in haystacks.items():
        for secret in forbidden:
            assert secret not in haystack, f"{secret!r} leaked into the {label}"

    if branch.entity_type == UNBOUND_ENTITY_TYPE:
        assert event["entity_id"] == UNBOUND_ENTITY_ID


@pytest.mark.parametrize("branch", BRANCHES, ids=[b.name for b in BRANCHES])
async def test_a_replayed_refused_callback_still_creates_no_session(
    branch, client, provider, migrated_database
):
    """7. The second attempt is refused too, and leaves the same absences.

    Separated from the assertions above so a replay that *did* create a session
    fails a test whose name says what happened, rather than making a
    seven-assertion test fail on its last line.
    """
    first = await branch.issue(client, provider)
    first_correlation = _correlation_of(first)

    second = await branch.issue(client, provider)
    second_correlation = _correlation_of(second)

    assert second.status_code == branch.status
    assert second_correlation != first_correlation, (
        "each attempt gets its own correlation id"
    )
    with migrated_database.connect() as connection:
        assert (
            connection.execute(
                select(text("count(*)")).select_from(sessions)
            ).scalar_one()
            == 0
        )
        assert (
            connection.execute(
                select(text("count(*)")).select_from(oauth_token_grants)
            ).scalar_one()
            == 0
        )
        for correlation in (first_correlation, second_correlation):
            assert (
                connection.execute(
                    select(text("count(*)"))
                    .select_from(audit_events)
                    .where(audit_events.c.correlation_id == correlation)
                ).scalar_one()
                == 1
            ), "each attempt records exactly one event, and never a second"


# ---------------------------------------------------------------------------
# The properties the parametrization cannot state
# ---------------------------------------------------------------------------


async def test_the_successful_path_writes_no_refusal_event(
    client, provider, migrated_database
):
    """The other half of "exactly one": a login records a success and nothing else."""
    transaction = await _start(client)
    state = provider.authorization_calls[-1][0]

    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": CODE},
        headers=_cookie_header(transaction),
    )
    assert response.status_code == 303

    with migrated_database.connect() as connection:
        actions = (
            connection.execute(
                select(audit_events.c.action).where(
                    audit_events.c.action.like("auth.login.%")
                )
            )
            .scalars()
            .all()
        )
    assert actions == ["auth.login.succeeded"]


async def test_a_non_member_refusal_names_no_transaction_it_did_not_validate(
    client, provider, migrated_database
):
    """The entity-naming rule, at the one branch that names something else.

    A refusal names an OAuth transaction only where a validated identifier
    exists. The non-member branch has a verified external identity instead, and
    names that — which is the more useful fact and is equally non-secret.
    """
    provider.is_member = False
    transaction = await _start(client)
    state = provider.authorization_calls[-1][0]

    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": CODE},
        headers=_cookie_header(transaction),
    )
    correlation_id = _correlation_of(response)

    with migrated_database.connect() as connection:
        event = (
            connection.execute(
                select(audit_events).where(
                    audit_events.c.correlation_id == correlation_id
                )
            )
            .mappings()
            .one()
        )
        accounts = connection.execute(
            select(text("count(*)")).select_from(platform_accounts)
        ).scalar_one()

    assert event["entity_type"] == "external_identity"
    assert event["entity_id"] == f"discord:{provider.subject}"
    assert accounts == 0, "a non-member leaves no account behind"


async def test_the_recorder_writes_once_even_if_a_branch_records_twice(
    composition, migrated_database
):
    """The "at most one" property, asserted on the object rather than through a route.

    A future editor adding a branch that both raises and records must not be able
    to produce two rows. The recorder enforces that itself, so the property is
    tested where it lives.
    """
    from uuid import uuid4

    from application.web.refusals import OAuthRefusalRecorder

    correlation_id = uuid4()
    recorder = OAuthRefusalRecorder(
        migrated_database, correlation_id=correlation_id
    )
    recorder.record(LoginRefusalReason.PROVIDER_UNAVAILABLE)
    assert recorder.recorded
    recorder.record(LoginRefusalReason.PROVIDER_REFUSED)
    recorder.record(LoginRefusalReason.RATE_LIMITED, transaction_id=uuid4())

    with migrated_database.connect() as connection:
        rows = (
            connection.execute(
                select(audit_events).where(
                    audit_events.c.correlation_id == correlation_id
                )
            )
            .mappings()
            .all()
        )
    assert len(rows) == 1
    assert rows[0]["payload"]["reason"] == "provider_unavailable"


async def test_a_refusal_that_cannot_be_recorded_does_not_become_a_login(
    app, provider, migrated_database, monkeypatch
):
    """The audit-failure rule, in the refusal direction.

    If the refusal record cannot be written the caller gets VM-20 and a
    correlation id — **not** a session. The failure direction matters: an audit
    write that fails must never be the difference between a refusal and a login.

    It builds its own client because `raise_app_exceptions=False` is needed to
    observe the safe error response rather than the exception Starlette re-raises
    into the test.
    """
    import httpx

    from application.web import refusals

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(
        transport=transport, base_url=PUBLIC_ORIGIN, follow_redirects=False
    ) as client:
        transaction = await _start(client)
        state = provider.authorization_calls[-1][0]
        provider.unavailable_at_exchange = True

        def explode(self, event):
            raise RuntimeError("the audit write failed")

        monkeypatch.setattr(refusals.OAuthRefusalRecorder, "_write", explode)

        response = await client.get(
            "/auth/discord/callback",
            params={"state": state, "code": CODE},
            headers=_cookie_header(transaction),
        )

    assert response.status_code == 500
    for leak in ("the audit write failed", "RuntimeError", "Traceback", CODE):
        assert leak not in response.text, leak
    with migrated_database.connect() as connection:
        assert (
            connection.execute(
                select(text("count(*)")).select_from(sessions)
            ).scalar_one()
            == 0
        )


def test_correlation_of_semantics_and_falsification() -> None:
    """Falsification: _correlation_of strictly enforces exact canonical UUID text across redirects and refusal DOM."""
    from unittest.mock import MagicMock

    # 1. 303 Redirect extraction
    r_redirect = MagicMock(status_code=303, headers={"location": "/v1/login?failure=auth_failed&correlation=11111111-1111-1111-1111-111111111111"})
    assert _correlation_of(r_redirect) == UUID("11111111-1111-1111-1111-111111111111")

    # Missing correlation query param on 303 fails
    r_no_corr = MagicMock(status_code=303, headers={"location": "/v1/login?failure=auth_failed"})
    with pytest.raises(AssertionError, match="no correlation id in"):
        _correlation_of(r_no_corr)

    # Uppercase / non-canonical UUID in query param fails
    r_upper_query = MagicMock(status_code=303, headers={"location": "/v1/login?correlation=11111111-1111-1111-1111-11111111111A"})
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        _correlation_of(r_upper_query)

    # 2. Rendered refusal page extraction (canonical lowercase hyphenated UUID)
    r_html = MagicMock(
        status_code=403,
        text='<p>Reference <span class="reference-code">22222222-2222-2222-2222-222222222222</span>.</p>',
    )
    assert _correlation_of(r_html) == UUID("22222222-2222-2222-2222-222222222222")

    # Missing .reference-code fails
    r_missing = MagicMock(status_code=403, text='<p>Reference 22222222-2222-2222-2222-222222222222.</p>')
    with pytest.raises(AssertionError, match="no correlation reference element"):
        _correlation_of(r_missing)

    # Duplicate .reference-code fails
    r_duplicate = MagicMock(
        status_code=403,
        text='<span class="reference-code">22222222-2222-2222-2222-222222222222</span><span class="reference-code">33333333-3333-3333-3333-333333333333</span>',
    )
    with pytest.raises(AssertionError, match="expected exactly one correlation reference element"):
        _correlation_of(r_duplicate)

    # Leading whitespace fails
    r_leading_space = MagicMock(status_code=403, text='<span class="reference-code"> 22222222-2222-2222-2222-222222222222</span>')
    with pytest.raises(AssertionError):
        _correlation_of(r_leading_space)

    # Trailing whitespace fails
    r_trailing_space = MagicMock(status_code=403, text='<span class="reference-code">22222222-2222-2222-2222-222222222222 </span>')
    with pytest.raises(AssertionError):
        _correlation_of(r_trailing_space)

    # Uppercase UUID fails
    r_uppercase = MagicMock(status_code=403, text='<span class="reference-code">22222222-2222-2222-2222-22222222222A</span>')
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        _correlation_of(r_uppercase)

    # Unhyphenated UUID fails
    r_unhyphenated = MagicMock(status_code=403, text='<span class="reference-code">22222222222222222222222222222222</span>')
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        _correlation_of(r_unhyphenated)

    # Braced UUID fails
    r_braces = MagicMock(status_code=403, text='<span class="reference-code">{22222222-2222-2222-2222-222222222222}</span>')
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        _correlation_of(r_braces)

    # URN format fails
    r_urn = MagicMock(status_code=403, text='<span class="reference-code">urn:uuid:22222222-2222-2222-2222-222222222222</span>')
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        _correlation_of(r_urn)

    # Child markup / tags inside element fails
    r_child_tag = MagicMock(status_code=403, text='<span class="reference-code"><b>22222222-2222-2222-2222-222222222222</b></span>')
    with pytest.raises(AssertionError, match="child markup, comments, or mixed content"):
        _correlation_of(r_child_tag)

    # Comments inside element fails
    r_comment = MagicMock(status_code=403, text='<span class="reference-code">22222222-2222-2222-2222-222222222222<!-- comment --></span>')
    with pytest.raises(AssertionError, match="child markup, comments, or mixed content"):
        _correlation_of(r_comment)

    # Extra prose fails
    r_prose = MagicMock(status_code=403, text='<span class="reference-code">Ref: 22222222-2222-2222-2222-222222222222</span>')
    with pytest.raises(AssertionError, match="not a valid UUID"):
        _correlation_of(r_prose)

    # Malformed non-UUID text fails
    r_malformed = MagicMock(status_code=403, text='<span class="reference-code">not-a-uuid</span>')
    with pytest.raises(AssertionError, match="not a valid UUID"):
        _correlation_of(r_malformed)
