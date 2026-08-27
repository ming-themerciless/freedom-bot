"""N-7: the OAuth authorization code must never reach the access log.

Raised by SP-12 on 2026-08-26, from the deployed systemd journal: uvicorn's
default access logger writes `get_path_with_query_string(scope)`, and R-04
`/auth/discord/callback` receives the authorization code and state **as query
parameters** because that is how the provider redirects. Every successful login
wrote a credential to the journal, failing TC-OPS-05.

These tests are written against the **real uvicorn record shape**, not a guess at
it: `'%s - "%s %s HTTP/%s" %d'` with the request target third
(`uvicorn/protocols/http/httptools_impl.py`, and identically in `h11_impl.py`).
The first test below **falsifies** the fix by asserting the leak is reproduced
when the filter is absent, so a filter that silently stopped matching could not
pass this file.

The second half of the file, from `LEAKY_SHAPES` onward, was added for Codex's
re-review of finding I-1, which reproduced a credential leak through a *list* of
arguments. Those tests follow the same falsify-then-prevent order: each shape is
first shown to leak unfiltered, then shown not to leak through the filter, and
every assertion is made against the fully rendered `LogRecord.getMessage()`
rather than against mutated arguments.
"""

from __future__ import annotations

import hashlib
import logging
import re
import sys

import pytest

from tools.portal_server import (
    ACCESS_LOG_FORMAT,
    REDACTED_QUERY,
    UNRENDERABLE_RECORD,
    RedactAccessLogQueryString,
    install_access_log_redaction,
    _pseudonymise_client,
)

#: The literal shape uvicorn emits. Not a paraphrase — and asserted below to be
#: the same constant the filter gates its precise branch on, so the test and the
#: implementation cannot drift apart silently.
ACCESS_FORMAT = '%s - "%s %s HTTP/%s" %d'
#: The request target's position in that format.
_TARGET = 2

#: A synthetic authorization code and state. Structurally like Discord's and
#: deliberately unmistakable, so a test failure names what leaked.
SYNTHETIC_CODE = "SYNTHETICcode0123456789abcdefAB"
SYNTHETIC_STATE = "SYNTHETICstate-0123456789_abcdefABCDEF"
CALLBACK_TARGET = f"/auth/discord/callback?code={SYNTHETIC_CODE}&state={SYNTHETIC_STATE}"


def test_the_test_and_the_filter_agree_on_the_access_format() -> None:
    """The two constants must be the same string, or these tests prove nothing."""
    assert ACCESS_FORMAT == ACCESS_LOG_FORMAT


def _access_record(target: str) -> logging.LogRecord:
    """One `uvicorn.access` record, with uvicorn's own argument tuple."""
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=ACCESS_FORMAT,
        args=("127.0.0.1:52341", "GET", target, "1.1", 303),
        exc_info=None,
    )


def test_falsification_the_leak_is_real_without_the_filter() -> None:
    """Falsification: unfiltered, the code and state DO reach the formatted line.

    If this ever stops failing to redact, the other tests below would be proving
    nothing, because there would be no leak left for them to prevent.
    """
    record = _access_record(CALLBACK_TARGET)
    assert SYNTHETIC_CODE in record.getMessage()
    assert SYNTHETIC_STATE in record.getMessage()


def test_the_authorization_code_and_state_never_reach_the_formatted_line() -> None:
    record = _access_record(CALLBACK_TARGET)
    assert RedactAccessLogQueryString().filter(record) is True
    rendered = record.getMessage()
    assert SYNTHETIC_CODE not in rendered
    assert SYNTHETIC_STATE not in rendered
    assert "code=" not in rendered
    assert "state=" not in rendered


def test_the_path_survives_so_the_access_log_stays_useful() -> None:
    """Redaction, not deletion: the route is still identifiable."""
    record = _access_record(CALLBACK_TARGET)
    RedactAccessLogQueryString().filter(record)
    rendered = record.getMessage()
    assert "/auth/discord/callback" in rendered
    assert REDACTED_QUERY in rendered
    assert '"GET ' in rendered and "HTTP/1.1" in rendered
    assert rendered.endswith("303")


def test_a_request_without_a_query_string_keeps_its_target_exactly() -> None:
    """No query string, nothing to redact in the target.

    **Amended 2026-08-26 for N-13.** This asserted that the whole record was
    left untouched, which stopped being true when the client address began being
    pseudonymised. The property that mattered — the request target survives a
    record with no query string — is asserted here directly instead of by
    comparing the whole argument tuple.
    """
    record = _access_record("/healthz")

    RedactAccessLogQueryString().filter(record)

    assert record.args[_TARGET] == "/healthz"
    assert record.args[1:] == ("GET", "/healthz", "1.1", 303)
    assert "127.0.0.1" not in record.getMessage()
    assert record.getMessage().endswith('- "GET /healthz HTTP/1.1" 303')


@pytest.mark.parametrize(
    "target",
    [
        "/v1/auth/emergency?failure=invalid&correlation=00000000-0000-4000-8000-000000000000",
        "/v1/auth/emergency?failure=rate_limited",
        "/v1/council/jobs/00000000-0000-4000-8000-000000000000/status?cursor=abc",
        "/?",
        "/v1/login?",
    ],
)
def test_every_query_string_goes_not_only_the_oauth_one(target: str) -> None:
    """Fail-safe by construction: no allowlist of 'harmless' parameters exists.

    An allowlist is a control somebody has to maintain, and the day a route gains
    a parameter carrying a token, an allowlist nobody updated leaks it silently.
    """
    record = _access_record(target)
    RedactAccessLogQueryString().filter(record)
    rendered = record.getMessage()
    assert "?" not in rendered.split(REDACTED_QUERY)[0]
    assert rendered.count("?") == 1, "only the redaction marker's own '?' remains"
    assert target.split("?")[0] in rendered


@pytest.mark.parametrize(
    "args",
    [
        None,
        (),
        ("only-one",),
        ("a", "b"),
        ("a", "b", 12345, "1.1", 200),
        # Two keys deliberately: CPython's LogRecord unwraps a *single*-key
        # mapping via `args[0]`, which is a quirk of the constructor rather than
        # anything this filter sees.
        {"mapping": "style", "second": "key"},
    ],
)
def test_an_unrecognised_record_shape_does_not_crash_the_filter(args: object) -> None:
    """Whatever arrives, the record survives and the filter returns True."""
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="%s",
        args=args,
        exc_info=None,
    )
    assert RedactAccessLogQueryString().filter(record) is True


@pytest.mark.parametrize(
    "msg, args",
    [
        # The known shape, but with the target somewhere unexpected.
        ("%s %s", ("GET", CALLBACK_TARGET)),
        ("%s", (CALLBACK_TARGET,)),
        # Extra leading fields, as a future uvicorn might add.
        ("%s %s %s %s %s %s", ("x", "y", "GET", CALLBACK_TARGET, "1.1", 200)),
        # Mapping-style arguments.
        ("%(target)s", {"target": CALLBACK_TARGET, "other": "value"}),
        # Pre-formatted message with no arguments at all: no argument redaction
        # could ever reach this one.
        (f'127.0.0.1 - "GET {CALLBACK_TARGET} HTTP/1.1" 303', None),
    ],
)
def test_an_unrecognised_record_fails_closed_and_cannot_emit_a_credential(
    msg: str, args: object
) -> None:
    """I-1: the fallback must not leak, whatever shape the record arrives in.

    Codex interim finding I-1: the first version passed every unrecognised shape
    through untouched, and its tests enshrined that. A uvicorn upgrade or a
    logging-configuration change could then restore credential disclosure with
    the whole suite still green. Over-redacting an unfamiliar record on this
    logger costs part of one access line; under-redacting costs a credential.
    """
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=None,
    )
    assert RedactAccessLogQueryString().filter(record) is True
    rendered = record.getMessage()
    assert SYNTHETIC_CODE not in rendered, f"credential leaked through shape {msg!r}"
    assert SYNTHETIC_STATE not in rendered
    assert "code=" not in rendered
    assert "?" not in rendered.replace(REDACTED_QUERY, "")


def test_the_pinned_uvicorn_access_contract_still_holds() -> None:
    """I-1's other half: notice when the external contract moves.

    The precise-redaction branch is written against uvicorn's access-log call —
    `'%s - "%s %s HTTP/%s" %d'` with the request target third. If a future
    uvicorn changes that, the fail-closed branch above still protects the
    credential, but this test is what says *why* the behaviour changed, in CI,
    instead of leaving somebody to discover it in a journal.
    """
    inspect = pytest.importorskip("inspect")
    impls = []
    for module_name in (
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.http.h11_impl",
    ):
        module = pytest.importorskip(module_name)
        impls.append(inspect.getsource(module))

    assert impls, "neither uvicorn HTTP protocol implementation could be read"
    for source in impls:
        assert ACCESS_FORMAT in source, (
            "uvicorn's access-log format has changed; re-verify which argument "
            "carries the request target before trusting the precise branch"
        )
        # The request target is produced by this helper, third in the call.
        assert "get_path_with_query_string(self.scope)" in source


def test_the_filter_never_drops_a_record() -> None:
    """Losing the access line would trade one operational blindness for another."""
    for target in ("/healthz", CALLBACK_TARGET, "/v1/login?failure=invalid"):
        assert RedactAccessLogQueryString().filter(_access_record(target)) is True


def test_installation_is_idempotent() -> None:
    logger = logging.getLogger("test.n7.idempotent")
    logger.filters.clear()
    install_access_log_redaction(logger)
    install_access_log_redaction(logger)
    install_access_log_redaction(logger)
    installed = [f for f in logger.filters if isinstance(f, RedactAccessLogQueryString)]
    assert len(installed) == 1


def test_installation_targets_the_uvicorn_access_logger_by_default() -> None:
    access = logging.getLogger("uvicorn.access")
    access.filters = [f for f in access.filters if not isinstance(f, RedactAccessLogQueryString)]
    install_access_log_redaction()
    assert any(isinstance(f, RedactAccessLogQueryString) for f in access.filters)


def test_the_installed_filter_redacts_through_a_real_handler(caplog) -> None:
    """End to end through the logging machinery, not just a direct filter call."""
    logger = logging.getLogger("test.n7.endtoend")
    logger.filters.clear()
    logger.setLevel(logging.INFO)
    install_access_log_redaction(logger)
    with caplog.at_level(logging.INFO, logger="test.n7.endtoend"):
        logger.info(
            ACCESS_FORMAT, "127.0.0.1:52341", "GET", CALLBACK_TARGET, "1.1", 303
        )
    assert caplog.records, "the record must survive: this filter redacts, it never drops"
    rendered = caplog.records[0].getMessage()
    assert SYNTHETIC_CODE not in rendered
    assert "/auth/discord/callback" in rendered


def test_the_operator_entry_point_installs_the_redaction(monkeypatch) -> None:
    """The closing link: available is not the same as installed.

    Every test above proves the filter works once something adds it. This one
    proves `application()` — the factory the unit file names, and the only way
    this process is started — actually adds it. Without this, the redaction could
    be removed from the entry point and the rest of the file would stay green.
    """
    import tools.portal_server as portal_server

    installed: list[bool] = []

    monkeypatch.setattr(
        portal_server,
        "install_access_log_redaction",
        lambda *a, **k: installed.append(True),
    )
    monkeypatch.setattr(
        portal_server.WebSettings, "from_environment", classmethod(lambda cls, *a, **k: object())
    )
    monkeypatch.setattr(portal_server, "create_app", lambda settings: "app")

    assert portal_server.application() == "app"
    assert installed == [True], "application() must install the N-7 redaction"


# ---------------------------------------------------------------------------
# Codex re-review of I-1, 2026-08-26: the fallback was still enumerating types.
#
# The first remediation scrubbed tuples and mapping values and claimed that made
# every unrecognised record fail closed. Codex reproduced the leak with a list:
# `record.args = ["/auth/discord/callback?code=…"]` is neither a tuple nor a
# mapping, so it reached `_redact` as a scalar, `_redact` changed only strings,
# and the credential rendered intact. The shapes below deliberately go past that
# one container: a set, a nested structure, and an object that carries the target
# only in its `__str__` — which is the case that shows enumeration can never be
# completed, because the set of objects that can render a query string is not a
# set anyone can list.
#
# The filter no longer inspects structure on that path. It renders the record and
# redacts the text, so these tests assert against the fully rendered
# `LogRecord.getMessage()` rather than against mutated arguments.
# ---------------------------------------------------------------------------


class _TargetInRepr:
    """An object that carries the request target only when it is rendered."""

    def __str__(self) -> str:
        return CALLBACK_TARGET


class _RenderingExplodes:
    """An argument whose rendering raises — with the credential in the message."""

    def __str__(self) -> str:
        raise ValueError(f"cannot render {CALLBACK_TARGET}")


#: Shapes that render the credential when nothing filters them. Each one is a
#: `(msg, args)` pair; the ids name the container the old fallback missed.
LEAKY_SHAPES = [
    pytest.param("%s", [CALLBACK_TARGET], id="codex-repro-bare-list"),
    pytest.param("%s", ([CALLBACK_TARGET],), id="list-inside-the-tuple"),
    pytest.param("%s", ({CALLBACK_TARGET},), id="set-inside-the-tuple"),
    pytest.param("%s", ([{"a": (CALLBACK_TARGET,)}],), id="nested-list-mapping-tuple"),
    pytest.param("%s %s", ("x", {"k": CALLBACK_TARGET}), id="mapping-not-unwrapped"),
    pytest.param("%s", (_TargetInRepr(),), id="object-rendering-the-target"),
]

#: Shapes that cannot be rendered at all. A broken record must still be safe.
UNRENDERABLE_SHAPES = [
    pytest.param("%s %s", (CALLBACK_TARGET,), "TypeError", id="too-few-arguments"),
    pytest.param("%s", (_RenderingExplodes(),), "ValueError", id="argument-raises"),
]


def _shaped_record(msg: str, args: object) -> logging.LogRecord:
    """One `uvicorn.access` record with a deliberately unfamiliar payload."""
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=None,
    )


@pytest.mark.parametrize("msg, args", LEAKY_SHAPES)
def test_falsification_these_container_shapes_really_do_leak_unfiltered(
    msg: str, args: object
) -> None:
    """Reproduce first: unfiltered, every shape below renders the credential.

    Without this, the prevention tests underneath could pass against shapes that
    never carried a credential in the first place.
    """
    rendered = _shaped_record(msg, args).getMessage()
    assert SYNTHETIC_CODE in rendered, "this shape must leak, or it proves nothing"


@pytest.mark.parametrize("msg, args", LEAKY_SHAPES)
def test_no_argument_shape_can_render_a_credential_through_the_filter(
    msg: str, args: object
) -> None:
    """Prevent: the same shapes, filtered, and asserted on the rendered line."""
    record = _shaped_record(msg, args)
    assert RedactAccessLogQueryString().filter(record) is True
    rendered = record.getMessage()
    assert SYNTHETIC_CODE not in rendered, f"credential leaked through {msg!r} {args!r}"
    assert SYNTHETIC_STATE not in rendered
    assert "code=" not in rendered


@pytest.mark.parametrize("msg, args", LEAKY_SHAPES)
def test_nothing_survives_after_the_first_question_mark(msg: str, args: object) -> None:
    """The documented guarantee itself, not merely the absence of one credential.

    The fallback redacts *rendered text*, so what it promises is a property of
    the output: no character after the first `?` survives. Asserting that, rather
    than asserting that one synthetic string is missing, is what makes the test
    independent of which parameter a future leak arrives in.
    """
    record = _shaped_record(msg, args)
    RedactAccessLogQueryString().filter(record)
    rendered = record.getMessage()
    assert rendered.endswith(REDACTED_QUERY)
    assert rendered.count("?") == 1, "only the redaction marker's own '?' remains"


@pytest.mark.parametrize("msg, args, expected_error", UNRENDERABLE_SHAPES)
def test_a_record_that_cannot_be_rendered_becomes_a_safe_placeholder(
    msg: str, args: object, expected_error: str
) -> None:
    """Nothing from the record survives — not even the exception's own message.

    `_RenderingExplodes` puts the credential in the `ValueError` it raises, which
    is why only the exception's *type name* is reported.
    """
    record = _shaped_record(msg, args)
    assert RedactAccessLogQueryString().filter(record) is True
    assert record.getMessage() == UNRENDERABLE_RECORD.format(error=expected_error)
    assert SYNTHETIC_CODE not in record.getMessage()


def test_an_unrenderable_record_can_no_longer_break_a_formatter() -> None:
    """The fallback's other half: a malformed record used to raise at emit time.

    Before this change the filter left the broken arguments in place, so the
    `TypeError` simply moved to whichever handler formatted the record. Clearing
    `record.args` means the record is already text by the time a handler sees it.
    """
    record = _shaped_record("%s %s", (CALLBACK_TARGET,))
    with pytest.raises(TypeError):
        record.getMessage()

    RedactAccessLogQueryString().filter(record)
    assert logging.Formatter().format(record) == UNRENDERABLE_RECORD.format(
        error="TypeError"
    )


def test_the_fallback_leaves_no_arguments_for_a_later_formatter_to_reapply() -> None:
    """Redacted text with `args = None` cannot be re-expanded back into a leak."""
    record = _shaped_record("%s", [CALLBACK_TARGET])
    RedactAccessLogQueryString().filter(record)
    assert record.args is None
    assert record.getMessage() == record.getMessage()


@pytest.mark.parametrize("msg, args", LEAKY_SHAPES)
def test_filtering_twice_changes_nothing(msg: str, args: object) -> None:
    """`--workers` and re-imports make double application worth pinning down."""
    record = _shaped_record(msg, args)
    filter_ = RedactAccessLogQueryString()
    filter_.filter(record)
    once = record.getMessage()
    filter_.filter(record)
    assert record.getMessage() == once


def test_the_pinned_line_redacts_the_client_and_the_query_and_nothing_else() -> None:
    """Path 1's exact scope: two fields changed, three untouched.

    This is the boundary that makes the aggressive fallback affordable — every
    ordinary access record takes this path, so nothing an operator reads day to
    day is degraded beyond these two fields.

    **Amended 2026-08-26 for N-13**, which added the client field. Method, HTTP
    version and status are asserted unchanged, so a future over-broad redaction
    fails here.
    """
    record = _access_record(CALLBACK_TARGET)

    RedactAccessLogQueryString().filter(record)

    client, method, target, version, status = record.args
    assert re.fullmatch(r"client-[0-9a-f]{8}", client)
    assert "127.0.0.1" not in client
    assert (method, target, version, status) == (
        "GET",
        f"/auth/discord/callback{REDACTED_QUERY}",
        "1.1",
        303,
    )


def test_the_pinned_format_with_the_wrong_arity_is_not_trusted() -> None:
    """The format string alone is not the contract: the arity is part of it.

    A record carrying uvicorn's format string but six arguments is not the pinned
    contract, so index 2 must not be redacted on the assumption that the rest of
    the tuple is what it looks like. Six arguments cannot render against a
    five-placeholder format at all, so this record takes the fallback's
    unrenderable path — which is the point: the gate refused it, and refusing it
    disclosed nothing. Before this change the same record would have carried its
    `TypeError` into whichever handler formatted it.
    """
    record = _shaped_record(
        ACCESS_FORMAT, ("127.0.0.1", "extra", "GET", CALLBACK_TARGET, "1.1", 303)
    )
    RedactAccessLogQueryString().filter(record)
    assert record.args is None, "the fallback must have run, not the precise branch"
    rendered = record.getMessage()
    assert SYNTHETIC_CODE not in rendered
    assert rendered == UNRENDERABLE_RECORD.format(error="TypeError")


def test_an_attached_traceback_is_redacted_as_well() -> None:
    """A formatter appends more than the message, so the guarantee must too.

    No uvicorn access record carries an exception. Leaving `exc_info` outside the
    guarantee would therefore rest on that continuing to be true, which is the
    class of assumption finding I-1 was about.
    """
    try:
        raise RuntimeError(f"failed for {CALLBACK_TARGET}")
    except RuntimeError:
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=ACCESS_FORMAT,
        args=("127.0.0.1:52341", "GET", "/healthz", "1.1", 200),
        exc_info=exc_info,
    )
    RedactAccessLogQueryString().filter(record)
    formatted = logging.Formatter().format(record)
    assert SYNTHETIC_CODE not in formatted
    assert SYNTHETIC_STATE not in formatted
    assert "RuntimeError" in formatted, "the failure itself must stay diagnosable"


def test_an_attached_stack_is_redacted_as_well() -> None:
    record = _access_record("/healthz")
    record.stack_info = f'Stack (most recent call last):\n  request {CALLBACK_TARGET}'
    RedactAccessLogQueryString().filter(record)
    formatted = logging.Formatter().format(record)
    assert SYNTHETIC_CODE not in formatted
    assert formatted.endswith(REDACTED_QUERY)

# ---------------------------------------------------------------------------
# N-13 — the client address (added 2026-08-26)
#
# SP-12's first post-deployment run showed the N-7 token disclosure fixed and a
# second class still present: the deployed access line carried a plaintext
# client address, which the operational contract §5 prohibits in every metric,
# log line and dashboard. `--proxy-headers` means the address logged is the
# true visitor's, not the proxy's.
#
# Every case below is falsified first: the leak is reproduced without the
# filter, then shown prevented with it.
# ---------------------------------------------------------------------------

SYNTHETIC_ADDRESS = "203.0.113.7:54321"
SYNTHETIC_V6 = "2001:db8::1"


def _client_record(client: str = SYNTHETIC_ADDRESS, target: str = "/v1/characters"):
    return logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, ACCESS_LOG_FORMAT,
        (client, "GET", target, "1.1", 200), None,
    )


def test_without_the_filter_the_client_address_is_logged_in_plaintext() -> None:
    """The leak, reproduced. Without this the next test could pass vacuously."""
    record = _client_record()

    assert "203.0.113.7" in record.getMessage()


def test_the_pinned_access_line_carries_no_plaintext_client_address() -> None:
    record = _client_record()

    RedactAccessLogQueryString().filter(record)

    rendered = record.getMessage()
    assert "203.0.113.7" not in rendered
    assert "54321" not in rendered
    assert re.search(r"client-[0-9a-f]{8}", rendered)
    # The rest of the line still reaches the journal: an operator keeps method,
    # path, protocol and status.
    assert '"GET /v1/characters HTTP/1.1" 200' in rendered


def test_the_same_client_gets_the_same_pseudonym_within_one_process() -> None:
    """Correlation is the point of keeping anything at all here."""
    first, second = _client_record(), _client_record()

    RedactAccessLogQueryString().filter(first)
    RedactAccessLogQueryString().filter(second)

    assert first.getMessage() == second.getMessage()


def test_different_clients_get_different_pseudonyms() -> None:
    first = _client_record("203.0.113.7:1")
    second = _client_record("198.51.100.9:1")

    RedactAccessLogQueryString().filter(first)
    RedactAccessLogQueryString().filter(second)

    assert first.getMessage() != second.getMessage()


def test_the_pseudonym_is_keyed_and_not_a_bare_digest() -> None:
    """The property that makes it pseudonymisation rather than theatre.

    An unkeyed digest of an IPv4 address is reversible by exhausting 2^32
    candidates. If the key were ever dropped, this comparison fails.
    """
    address = "203.0.113.7:54321"
    unkeyed = hashlib.blake2s(address.encode(), digest_size=4).hexdigest()

    assert _pseudonymise_client(address) != f"client-{unkeyed}"


def test_an_unrecognised_record_carrying_an_address_is_scrubbed() -> None:
    leaking = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, "%s",
        ([f"{SYNTHETIC_ADDRESS} /auth/discord/callback?code=SYNTHETIC"],), None,
    )
    assert "203.0.113.7" in leaking.getMessage()

    RedactAccessLogQueryString().filter(leaking)

    rendered = leaking.getMessage()
    assert "203.0.113.7" not in rendered
    assert "SYNTHETIC" not in rendered


def test_an_ipv6_literal_is_scrubbed_on_the_fallback_path() -> None:
    leaking = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, "%s", ([SYNTHETIC_V6],), None,
    )
    assert SYNTHETIC_V6 in leaking.getMessage()

    RedactAccessLogQueryString().filter(leaking)

    assert SYNTHETIC_V6 not in leaking.getMessage()


def test_a_timestamp_is_not_mistaken_for_an_address() -> None:
    """Why candidates are validated rather than matched.

    A colon-separated pattern alone would rewrite `12:34:56` and quietly corrupt
    every traceback timestamp the fallback path touches.
    """
    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, "%s", ("started at 12:34:56 today",), None,
    )

    RedactAccessLogQueryString().filter(record)

    assert "12:34:56" in record.getMessage()


def test_pseudonymising_an_already_pseudonymised_client_is_a_no_op() -> None:
    """Filtering twice must not hash the hash, or correlation breaks."""
    record = _client_record()

    filtered = RedactAccessLogQueryString()
    filtered.filter(record)
    once = record.getMessage()
    filtered.filter(record)

    assert record.getMessage() == once
