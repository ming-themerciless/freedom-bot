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

The second section, from `LEAKY_SHAPES` onward, was added for Codex's re-review
of finding I-1, which reproduced a credential leak through a *list* of arguments.
Those tests follow the same falsify-then-prevent order: each shape is first shown
to leak unfiltered, then shown not to leak through the filter, and every
assertion is made against the fully rendered `LogRecord.getMessage()` rather than
against mutated arguments.

The last section, from `N29_V4` onward, was added for Codex's EX-11/EX-12
re-review finding **N-29**, which reproduced a plaintext address surviving the
fallback because it was adjacent to a word character. That finding changed the
contract rather than the pattern: an unfamiliar record is now withheld whole. A
number of tests above it were rewritten on 2026-08-28 for the same reason, and
each says in its own docstring what it used to assert and why that is no longer
the property to hold. None was deleted.

The two unfamiliar-client tests were rewritten again on 2026-08-28 for finding
**N-32**, which is a defect in *this file* rather than in the module it tests:
they forbade any three-character fragment of the source from occurring inside an
eight-hex-character keyed pseudonym, and a keyed digest may contain such a
fragment by chance — so a run could fail on a pseudonym that disclosed nothing.
They now assert *complete* values, and the section at the end of this file
reproduces the collision deterministically and mutation-tests the replacement.
"""

from __future__ import annotations

import hashlib
import logging
import re
import sys
from typing import NamedTuple

import pytest

from tools.portal_server import (
    ACCESS_LOG_FORMAT,
    REDACTED_QUERY,
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
def test_nothing_of_an_unfamiliar_record_survives_at_all(msg: str, args: object) -> None:
    """The guarantee itself, restated 2026-08-28 when N-29 strengthened it.

    Until N-29 this asserted the *text* guarantee the fallback then had: no
    character after the first `?` survived. That guarantee was real and it was
    not enough — it said nothing about an address, which does not follow a `?`.
    The fallback no longer redacts text at all, so the property to assert is the
    stronger one: the record is replaced by a marker this repository owns, and
    no character of the original reaches the line.
    """
    record = _shaped_record(msg, args)
    RedactAccessLogQueryString().filter(record)
    rendered = record.getMessage()
    assert rendered in portal_server.WITHHELD_RECORDS
    assert "?" not in rendered


@pytest.mark.parametrize("msg, args, expected_error", UNRENDERABLE_SHAPES)
def test_a_record_that_cannot_be_rendered_is_withheld_like_any_other(
    msg: str, args: object, expected_error: str
) -> None:
    """Nothing from the record survives — not even the exception's type name.

    Until N-29 this path reported the exception type, on the reasoning that a
    type name is a Python identifier and therefore safe. It is safe, and it is
    also **unreachable now**: the filter no longer renders an unfamiliar record,
    so no exception is raised for it to name. `expected_error` is kept as the
    parameter's label — it records which failure each shape used to produce.
    """
    record = _shaped_record(msg, args)
    assert RedactAccessLogQueryString().filter(record) is True
    assert record.getMessage() in portal_server.WITHHELD_RECORDS
    assert expected_error not in record.getMessage()
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
    # `"%s %s"` is not uvicorn's format string, so the first term of the pinned
    # contract is the one that fails — before the arity is ever looked at.
    assert logging.Formatter().format(record) == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_UNPINNED_FORMAT
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
    assert record.args is None, "the record must have been withheld, not redacted"
    rendered = record.getMessage()
    assert SYNTHETIC_CODE not in rendered
    assert "127.0.0.1" not in rendered
    assert rendered == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_UNPINNED_ARGUMENT_SHAPE
    )


def test_an_attached_traceback_puts_the_record_outside_the_pinned_contract() -> None:
    """A formatter appends more than the message, so the guarantee must too.

    No uvicorn access record carries an exception. Leaving `exc_info` outside the
    guarantee would therefore rest on that continuing to be true, which is the
    class of assumption finding I-1 was about.

    **Strengthened 2026-08-28 (N-29).** The traceback used to be rendered and
    scrubbed, and the exception *type* kept so the failure stayed diagnosable. A
    traceback echoes its own raising source line, so scrubbing one is a text rule
    over arbitrary content — which is what N-29 rejects. An attached exception
    now withholds the record whole, and the reason is the diagnostic.
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
        msg=ACCESS_LOG_FORMAT,
        args=("127.0.0.1:52341", "GET", "/healthz", "1.1", 200),
        exc_info=exc_info,
    )
    RedactAccessLogQueryString().filter(record)
    formatted = logging.Formatter().format(record)
    assert SYNTHETIC_CODE not in formatted
    assert SYNTHETIC_STATE not in formatted
    assert "Traceback" not in formatted
    assert "127.0.0.1" not in formatted
    assert formatted == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_ATTACHED_DIAGNOSTIC
    ), "the reason is what stays diagnosable"


def test_an_attached_stack_puts_the_record_outside_the_pinned_contract() -> None:
    record = _access_record("/healthz")
    record.stack_info = "Stack (most recent call last):\n  request " + CALLBACK_TARGET
    RedactAccessLogQueryString().filter(record)
    formatted = logging.Formatter().format(record)
    assert SYNTHETIC_CODE not in formatted
    assert record.stack_info is None
    assert formatted == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_ATTACHED_DIAGNOSTIC
    )

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


def test_a_timestamp_in_an_unfamiliar_record_goes_with_everything_else() -> None:
    """The case that used to justify validating candidates instead of matching.

    Until N-29 this asserted that `12:34:56` *survived* the fallback, because a
    colon pattern alone would have corrupted every timestamp the fallback
    touched. There is no fallback text any more, so the timestamp goes with the
    rest of the record — which is the trade N-29 makes explicit: an unfamiliar
    record keeps nothing, including the parts that were harmless.
    """
    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, "%s", ("started at 12:34:56 today",), None,
    )

    RedactAccessLogQueryString().filter(record)

    assert "12:34:56" not in record.getMessage()
    assert record.getMessage() in portal_server.WITHHELD_RECORDS


def test_pseudonymising_an_already_pseudonymised_client_is_a_no_op() -> None:
    """Filtering twice must not hash the hash, or correlation breaks."""
    record = _client_record()

    filtered = RedactAccessLogQueryString()
    filtered.filter(record)
    once = record.getMessage()
    filtered.filter(record)

    assert record.getMessage() == once


# ---------------------------------------------------------------------------
# N-13 correction — the ephemeral port (added 2026-08-27)
#
# Codex EX-11 finding: `_pseudonymise_client()` hashed uvicorn's *whole* client
# field, and that field is built as `"%s:%d" % client`
# (`uvicorn/protocols/utils.py::get_client_addr`, 0.32.1) — the address **and**
# the ephemeral port. Successive connections from one visitor therefore received
# different pseudonyms inside one process, so the correlation property the
# pseudonym exists to provide, and which the comments claimed, did not hold at
# all. The confidentiality property always held; the usefulness never did.
#
# The first test below reproduces the defect against the pre-correction
# algorithm, restated locally, so the tests that follow cannot pass vacuously:
# if `_pseudonymise_client` were reverted to hashing the field verbatim, every
# correlation assertion below fails.
# ---------------------------------------------------------------------------

#: One visitor, four connections, as uvicorn renders them. Ephemeral ports from
#: the Linux default range (`net.ipv4.ip_local_port_range`, 32768–60999) plus one
#: four-digit port, which is the case where uvicorn's unbracketed IPv6 form is
#: genuinely ambiguous with a bare IPv6 address.
VISITOR_V4 = "203.0.113.7"
VISITOR_V4_CONNECTIONS = [f"{VISITOR_V4}:{port}" for port in (54321, 33012, 60998, 5432)]
VISITOR_V6 = "2001:db8::1"
#: uvicorn does **not** bracket: `"%s:%d"` on an IPv6 host yields `2001:db8::1:5432`.
VISITOR_V6_CONNECTIONS = [f"{VISITOR_V6}:{port}" for port in (54321, 33012, 60998, 5432)]
#: The bracketed form, which a proxy or a future uvicorn may present instead.
VISITOR_V6_BRACKETED = [f"[{VISITOR_V6}]:{port}" for port in (54321, 33012, 5432)]


def _pre_correction_pseudonym(value: str) -> str:
    """The algorithm as it stood before 2026-08-27: the whole field, hashed.

    Restated here rather than imported, because the point of a falsification is
    that it holds even after the defect is gone from the module.
    """
    from tools.portal_server import _CLIENT_PSEUDONYM_KEY

    digest = hashlib.blake2s(
        value.encode("utf-8", "replace"), key=_CLIENT_PSEUDONYM_KEY, digest_size=4
    ).hexdigest()
    return f"client-{digest}"


def test_falsification_uvicorn_really_does_put_the_port_in_the_client_field() -> None:
    """The premise of the finding, read out of the pinned dependency itself.

    Not a paraphrase of uvicorn's behaviour: if a future uvicorn stops composing
    the field this way, this test says so rather than leaving the correction
    resting on a comment.
    """
    import inspect

    from uvicorn.protocols.utils import get_client_addr

    assert '"%s:%d" % client' in inspect.getsource(get_client_addr)
    assert get_client_addr({"client": (VISITOR_V4, 54321)}) == f"{VISITOR_V4}:54321"
    assert get_client_addr({"client": (VISITOR_V6, 54321)}) == f"{VISITOR_V6}:54321"
    assert get_client_addr({"client": None}) == ""


def test_falsification_the_pre_correction_algorithm_broke_correlation() -> None:
    """The defect, reproduced: one visitor, four pseudonyms.

    Without this, the four tests below would be asserting a property no
    implementation had ever failed.
    """
    pseudonyms = {_pre_correction_pseudonym(c) for c in VISITOR_V4_CONNECTIONS}

    assert len(pseudonyms) == len(VISITOR_V4_CONNECTIONS), (
        "the pre-correction algorithm must be shown to produce a distinct "
        "pseudonym per connection, or the correction proves nothing"
    )


def test_one_ipv4_visitor_reaches_one_pseudonym_whatever_the_port() -> None:
    pseudonyms = {_pseudonymise_client(c) for c in VISITOR_V4_CONNECTIONS}

    assert len(pseudonyms) == 1, pseudonyms


def test_one_ipv6_visitor_reaches_one_pseudonym_whatever_the_port() -> None:
    """Including uvicorn's unbracketed form, which is the one it actually emits."""
    pseudonyms = {_pseudonymise_client(c) for c in VISITOR_V6_CONNECTIONS}

    assert len(pseudonyms) == 1, pseudonyms


def test_the_bracketed_and_unbracketed_ipv6_forms_agree() -> None:
    """A proxy's bracketing must not split one visitor into two."""
    assert {_pseudonymise_client(c) for c in VISITOR_V6_BRACKETED} == {
        _pseudonymise_client(c) for c in VISITOR_V6_CONNECTIONS
    }


def test_a_bare_address_agrees_with_the_same_address_carrying_a_port() -> None:
    """So a literal scrubbed out of a traceback matches the access line's client."""
    assert _pseudonymise_client(VISITOR_V4) == _pseudonymise_client(
        VISITOR_V4_CONNECTIONS[0]
    )
    assert _pseudonymise_client(VISITOR_V6) == _pseudonymise_client(
        VISITOR_V6_CONNECTIONS[0]
    )


def test_two_spellings_of_one_ipv6_address_reach_one_pseudonym() -> None:
    """`ipaddress` canonicalises, so the pseudonym is of the address, not the text."""
    assert _pseudonymise_client("0:0:0:0:0:0:0:1:54321") == _pseudonymise_client("::1")


@pytest.mark.parametrize(
    "left, right, why",
    [
        ("203.0.113.7:54321", "203.0.113.8:54321", "adjacent IPv4 addresses"),
        ("203.0.113.7:54321", "198.51.100.9:54321", "unrelated IPv4 addresses"),
        ("2001:db8::1:54321", "2001:db8::2:54321", "adjacent IPv6 addresses"),
        ("203.0.113.7:54321", "2001:db8::1:54321", "across address families"),
    ],
)
def test_different_visitors_still_reach_different_pseudonyms(
    left: str, right: str, why: str
) -> None:
    """Dropping the port must not have collapsed distinct visitors together."""
    assert _pseudonymise_client(left) != _pseudonymise_client(right), why


def test_no_plaintext_address_or_port_survives_formatting() -> None:
    """Confidentiality, asserted on the fully formatted line rather than the args."""
    for connection in VISITOR_V4_CONNECTIONS + VISITOR_V6_CONNECTIONS:
        record = _client_record(connection)
        RedactAccessLogQueryString().filter(record)
        formatted = logging.Formatter().format(record)

        address, _, port = connection.rpartition(":")
        assert address not in formatted, connection
        assert port not in formatted, connection
        assert re.search(r"client-[0-9a-f]{8}", formatted), connection


# ---------------------------------------------------------------------------
# N-32 — the unfamiliar-client assertions were probabilistic (2026-08-28)
#
# Codex evidence rerun. The two tests below used to split the source client value
# on `.`, `:` and `/` and require every fragment of three characters or more to
# be absent from the eight hexadecimal characters of the keyed pseudonym. A
# digest is free to contain any short hex string, and `_CLIENT_PSEUDONYM_KEY` is
# generated per process, so the assertion depended on the key:
#
#     source:     203.0.113.999:54321
#     pseudonym:  client-unknown-59990025
#     collision:  999
#     result:     2 failed, 451 passed
#
# That was not a disclosure. Neither the complete client field nor a dotted
# address literal survived; the test had mistaken coincidental equality for
# source preservation.
#
# The replacement asserts *complete* values instead of arbitrary fragments, and
# every value it asserts the absence of carries a character the pseudonym's own
# alphabet does not contain — so absence follows from the contract rather than
# from the key. The deterministic reproduction, and the mutation that proves the
# corrected assertions still catch a real pass-through, are in this file's N-32
# section at the end.
# ---------------------------------------------------------------------------


class _UnfamiliarClient(NamedTuple):
    """One client value this module cannot read, and what must not survive it."""

    #: The client field as uvicorn would present it.
    value: str
    #: The complete representations that must be absent from the pseudonym and
    #: from the formatted line: the whole field, and the punctuation-bearing host
    #: or credential inside it. Never a fragment — see the section comment, and
    #: `test_n32_no_forbidden_value_can_occur_inside_a_pseudonym`, which checks
    #: that each one is a value a pseudonym is incapable of containing.
    forbidden: tuple[str, ...]
    #: Why this value reaches the fail-safe path at all.
    why: str


UNFAMILIAR_CLIENT_CASES = [
    _UnfamiliarClient(
        "",
        (),
        "uvicorn's own no-client case: `get_client_addr` returns \"\" for a "
        "Unix socket or a lost peer",
    ),
    _UnfamiliarClient(
        "/run/freedom-portal.sock",
        ("/run/freedom-portal.sock",),
        "a Unix socket path, which is not an address at all",
    ),
    _UnfamiliarClient(
        "203.0.113.7:99999",
        ("203.0.113.7:99999", "203.0.113.7"),
        "a port outside the range: not a client field this module can read, so "
        "it must fail safe rather than guess which half is the address",
    ),
    _UnfamiliarClient(
        "203.0.113.7:not-a-port",
        ("203.0.113.7:not-a-port", "203.0.113.7"),
        "a port that is not numeric, for the same reason",
    ),
    _UnfamiliarClient(
        "203.0.113.999:54321",
        ("203.0.113.999:54321", "203.0.113.999"),
        "N-32's own case: no octet may exceed 255, so the host half is not an "
        "address either",
    ),
    _UnfamiliarClient(
        "host.example.invalid:54321",
        ("host.example.invalid:54321", "host.example.invalid"),
        "a hostname, which `--proxy-headers` can put here if a proxy sends one",
    ),
    _UnfamiliarClient(
        f"{SYNTHETIC_CODE}:54321",
        (f"{SYNTHETIC_CODE}:54321", SYNTHETIC_CODE),
        "a credential-shaped value, standing in for anything unexpected: its "
        "characters must not reach the log either",
    ),
]

#: Readable parametrisation ids, so a failure names the client field rather than
#: an index.
UNFAMILIAR_CLIENT_IDS = [
    case.value or "<no-client>" for case in UNFAMILIAR_CLIENT_CASES
]

#: The values alone, for the tests that need only a client field.
UNFAMILIAR_CLIENTS = [case.value for case in UNFAMILIAR_CLIENT_CASES]


def _assert_no_forbidden_value_survives(case: _UnfamiliarClient, text: str) -> None:
    """The N-32 confidentiality rule, held in one place.

    Shared by the two tests below and by the mutation test in this file's N-32
    section, so what the mutation is shown to fail is the assertion the suite
    really runs rather than a restatement of it that could drift from it.
    """
    for forbidden in case.forbidden:
        assert forbidden not in text, (case.why, forbidden)


def _assert_the_pseudonym_is_safe(case: _UnfamiliarClient, pseudonym: str) -> None:
    """Bounded form, then confidentiality."""
    assert re.fullmatch(r"client-unknown-[0-9a-f]{8}", pseudonym), pseudonym
    _assert_no_forbidden_value_survives(case, pseudonym)


def _assert_the_access_line_is_safe(case: _UnfamiliarClient, formatted: str) -> None:
    """Confidentiality, then the fields an operator is owed."""
    _assert_no_forbidden_value_survives(case, formatted)
    assert re.match(r"client-unknown-[0-9a-f]{8} - ", formatted), formatted
    assert '"GET /v1/characters HTTP/1.1" 200' in formatted


@pytest.mark.parametrize("case", UNFAMILIAR_CLIENT_CASES, ids=UNFAMILIAR_CLIENT_IDS)
def test_an_unfamiliar_client_value_fails_safe_without_leaking_its_contents(
    case: _UnfamiliarClient,
) -> None:
    """Fail-safe, and *labelled*: the prefix says the line is not correlatable.

    **Rewritten 2026-08-28 (N-32).** This used to assert that no fragment of the
    source of three characters or more occurred anywhere in the pseudonym, which
    a keyed digest can violate by chance and did. What it asserts now is the
    bounded form, and the absence of the complete client field and of the
    complete host or credential inside it — the values whose survival would
    actually be a disclosure.
    """
    _assert_the_pseudonym_is_safe(case, _pseudonymise_client(case.value))


@pytest.mark.parametrize("case", UNFAMILIAR_CLIENT_CASES, ids=UNFAMILIAR_CLIENT_IDS)
def test_an_unfamiliar_client_value_does_not_reach_the_formatted_line(
    case: _UnfamiliarClient,
) -> None:
    """The same confidentiality property, on the fully formatted line.

    **Rewritten 2026-08-28 (N-32)**, for the reason given above and in the
    section comment. The line is also asserted to still *be* an access line: the
    pseudonym in the client position, and method, path, protocol and status
    intact, so a correction that emptied the record could not pass this.
    """
    record = _client_record(case.value)

    RedactAccessLogQueryString().filter(record)

    _assert_the_access_line_is_safe(case, logging.Formatter().format(record))


def test_a_pseudonym_of_either_form_is_left_alone_when_filtered_again() -> None:
    """`--workers`, a re-import, or two filters must not hash the hash."""
    for client in VISITOR_V4_CONNECTIONS[:1] + UNFAMILIAR_CLIENTS[:1]:
        once = _pseudonymise_client(client)
        assert _pseudonymise_client(once) == once
        assert _pseudonymise_client(_pseudonymise_client(once)) == once


def test_the_pinned_line_still_carries_its_three_guarantees_together() -> None:
    """N-7, N-13 and N-29 asserted against one record rather than one each.

    **Rewritten 2026-08-28.** Until N-29 this record carried an attached
    exception and a stack as well, and asserted that the route and the exception
    type stayed diagnosable through them. Both of those now put the record
    outside the pinned contract, so they are asserted in their own tests and this
    one keeps what the pinned path is *for*: one access line whose client is a
    pseudonym, whose query string is gone, and whose path discloses no address.

    Every address below comes from a *name*, never from a literal in this
    function, because a literal written here would appear in an assertion failure
    as test source and be indistinguishable from a leak.
    """
    peer_v4 = VISITOR_V4_CONNECTIONS[0]
    port = peer_v4.rpartition(":")[2]

    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, ACCESS_LOG_FORMAT,
        (peer_v4, "GET", f"/probe/{VISITOR_V6}/callback{CALLBACK_TARGET}", "1.1", 303),
        None,
    )

    RedactAccessLogQueryString().filter(record)
    formatted = logging.Formatter().format(record)

    assert SYNTHETIC_CODE not in formatted
    assert SYNTHETIC_STATE not in formatted
    assert "code=" not in formatted and "state=" not in formatted
    assert VISITOR_V4 not in formatted
    assert VISITOR_V6 not in formatted
    assert port not in formatted
    assert "/probe/" in formatted, "the route stays diagnosable"
    assert REDACTED_QUERY in formatted
    assert formatted.count("?") == 1, "only the redaction marker's own '?' remains"
    assert formatted.endswith('HTTP/1.1" 303'), "the rest of the access line is kept"


def test_a_scrubbed_path_address_and_the_client_field_agree_on_one_visitor() -> None:
    """One address, two positions in the same contract, one pseudonym.

    **Rewritten 2026-08-28.** This used to compare the pinned path against the
    fallback scrubber; the fallback no longer scrubs, so the comparison that
    still means something is between the client field and an address appearing in
    the request path — the two places on the retained branch where one visitor's
    address can arrive, and the two that have to agree for correlation to work.
    """
    record = _client_record(VISITOR_V4_CONNECTIONS[0], f"/probe/{VISITOR_V4}")

    RedactAccessLogQueryString().filter(record)

    pseudonyms = set(re.findall(r"client-[0-9a-f]{8}", record.getMessage()))
    assert len(pseudonyms) == 1, pseudonyms
    assert VISITOR_V4 not in record.getMessage()


# ---------------------------------------------------------------------------
# N-29 — the unfamiliar-record path must fail closed as a whole (2026-08-28)
#
# Codex EX-11/EX-12 re-review. `_scrub_addresses()` was documented as
# best-effort, and its candidate pattern is anchored on `\b`, so an address
# adjacent to a word character was never isolated at all:
#
#     input:  peer=203.0.113.7suffix
#     output: peer=203.0.113.7suffix
#
# Operational contract §5 prohibits a plaintext IP address in **every** metric,
# log line and dashboard. A best-effort control cannot satisfy an absolute
# requirement, and a list of regex patterns cannot prove safe handling of
# arbitrary rendered objects: whatever the pattern is, some rendering escapes it.
#
# The remediation is not a better pattern. It is a narrower contract:
#
#   * the pinned uvicorn 0.32.1 access line keeps its precise path, with every
#     retained field bounded and validated, and the request path scrubbed by a
#     rule that is closed over its input rather than best-effort; and
#   * **every other record is withheld whole** — replaced by repository-owned
#     text naming only a category, with `args`, `exc_info`, `exc_text` and
#     `stack_info` cleared so no formatter can append the original afterwards.
#
# The tests below are written against that contract. Each falsification
# reproduces the disclosure first, so a regression cannot pass them vacuously.
# ---------------------------------------------------------------------------

from tools import portal_server  # noqa: E402 - the section's subject, read late

#: One synthetic documentation-range address (RFC 5737) and one synthetic IPv6
#: documentation address (RFC 3849), each embedded in a token so the adjacency
#: N-29 was raised for is what is actually asserted.
N29_V4 = "203.0.113.7"
N29_V6 = "2001:db8::1"

#: Every adjacency the finding names, plus the two the correction added while
#: proving the rule closed. `id` names what is adjacent, because that is what a
#: failure has to tell a reader.
N29_ADJACENT_V4 = [
    pytest.param(f"peer={N29_V4}suffix", id="ipv4-followed-by-letters"),
    pytest.param(f"prefix{N29_V4}", id="ipv4-preceded-by-letters"),
    pytest.param(f"{N29_V4}8", id="ipv4-followed-by-a-digit"),
    pytest.param(f"9{N29_V4}", id="ipv4-preceded-by-a-digit"),
    pytest.param(f"{N29_V4}89", id="ipv4-followed-by-two-digits"),
    pytest.param(f"peer_{N29_V4}_port", id="ipv4-between-underscores"),
    pytest.param(f"<{N29_V4}>", id="ipv4-in-punctuation"),
    pytest.param(f"host={N29_V4}:54321;", id="ipv4-with-a-port"),
    pytest.param(f"999.999.999.{N29_V4}", id="ipv4-after-an-invalid-quad"),
    pytest.param(f"{N29_V4},{N29_V4}", id="two-ipv4-addresses"),
]

N29_ADJACENT_V6 = [
    pytest.param(f"peer={N29_V6}suffix", id="ipv6-followed-by-letters"),
    pytest.param(f"prefix{N29_V6}", id="ipv6-preceded-by-letters"),
    pytest.param(f"[{N29_V6}]", id="ipv6-bracketed"),
    pytest.param(f"[{N29_V6}]:54321", id="ipv6-bracketed-with-a-port"),
    pytest.param(f"{N29_V6}:54321", id="ipv6-unbracketed-with-a-port"),
    pytest.param("fe80::1%eth0", id="ipv6-with-a-zone-identifier"),
    pytest.param(f"::ffff:{N29_V4}", id="ipv4-mapped-ipv6"),
    pytest.param("0:0:0:0:0:0:0:1", id="ipv6-uncompressed"),
]


class _N29StrCarriesAddress:
    """An object that discloses an address only when something renders it."""

    def __str__(self) -> str:
        return f"peer={N29_V4}suffix target={CALLBACK_TARGET}"


class _N29StrRaises:
    """An argument whose rendering raises, with the disclosure in the message."""

    def __str__(self) -> str:
        raise ValueError(f"cannot render {N29_V4} {CALLBACK_TARGET}")


#: Unfamiliar records that disclose an address, a credential, or both. Every
#: container the earlier remediation enumerated is here, plus the two shapes
#: that show enumeration can never be completed: an object that discloses only
#: through `__str__`, and one whose `__str__` raises with the secret inside the
#: exception.
N29_UNFAMILIAR = [
    pytest.param("%s", (f"peer={N29_V4}suffix",), id="tuple-scalar"),
    pytest.param("%s", [f"peer={N29_V4}suffix"], id="bare-list"),
    pytest.param("%s", ([f"peer={N29_V4}suffix"],), id="list-in-tuple"),
    pytest.param("%s", ({f"peer={N29_V4}suffix"},), id="set-in-tuple"),
    pytest.param(
        "%s",
        ([{"peer": (f"{N29_V4}suffix", f"{N29_V6}tail")}],),
        id="nested-list-mapping-tuple",
    ),
    pytest.param(
        "%(peer)s",
        {"peer": f"{N29_V4}suffix", "target": CALLBACK_TARGET},
        id="mapping-arguments",
    ),
    pytest.param("%s", (_N29StrCarriesAddress(),), id="object-str-discloses"),
    pytest.param(f"peer={N29_V4}suffix {CALLBACK_TARGET}", None, id="preformatted-msg"),
    pytest.param(
        ACCESS_LOG_FORMAT,
        (f"{N29_V4}:1", "GET", CALLBACK_TARGET, "1.1", 200, "extra"),
        id="pinned-format-wrong-arity",
    ),
    pytest.param("%s %s", (CALLBACK_TARGET,), id="too-few-arguments"),
    pytest.param("%s", (_N29StrRaises(),), id="rendering-raises"),
]

#: Fragments that must never appear in a formatted line, whatever produced it.
N29_FORBIDDEN_FRAGMENTS = (
    N29_V4,
    "203.0.113",
    N29_V6,
    "2001:db8",
    "fe80::1",
    SYNTHETIC_CODE,
    SYNTHETIC_STATE,
    "code=",
    "state=",
    "suffix",
    "peer=",
    "/auth/discord/callback",
    "cannot render",
    "ValueError",
    "TypeError",
)


def _n29_record(msg: object, args: object) -> logging.LogRecord:
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=None,
    )


def _n29_format(record: logging.LogRecord) -> str:
    """The **fully formatted** line, which is what actually reaches a journal.

    Asserting on `record.msg` alone would miss the two places the earlier
    versions leaked from: arguments a handler re-expands, and the traceback a
    formatter appends after the message.
    """
    return logging.Formatter().format(record)


@pytest.mark.parametrize("text", N29_ADJACENT_V4 + N29_ADJACENT_V6)
def test_n29_falsification_adjacent_addresses_survive_without_the_filter(
    text: str,
) -> None:
    """Reproduce first: unfiltered, every adjacency below reaches the line."""
    rendered = _n29_format(_n29_record("%s", (text,)))

    assert text in rendered, "this input must disclose, or the next test proves nothing"


@pytest.mark.parametrize("text", N29_ADJACENT_V4 + N29_ADJACENT_V6)
def test_n29_no_adjacent_address_survives_an_unfamiliar_record(text: str) -> None:
    """N-29 itself: `peer=203.0.113.7suffix` must not reach the journal.

    The record is unfamiliar, so nothing of it survives — which is a stronger
    statement than "the address was found and replaced", and it is the only one
    that can be made about arbitrary rendered input.
    """
    record = _n29_record("%s", (text,))

    assert RedactAccessLogQueryString().filter(record) is True

    formatted = _n29_format(record)
    assert N29_V4 not in formatted
    assert N29_V6 not in formatted
    assert "fe80::1" not in formatted
    assert text not in formatted


@pytest.mark.parametrize("msg, args", N29_UNFAMILIAR)
def test_n29_falsification_every_unfamiliar_shape_really_does_disclose(
    msg: object, args: object
) -> None:
    """Each shape below discloses something when nothing filters it.

    A shape that cannot be rendered discloses through the *formatter* instead,
    so the falsification accepts either: the disclosure in the line, or the
    exception a handler raises carrying it.
    """
    record = _n29_record(msg, args)
    try:
        rendered = _n29_format(record)
    except Exception as error:  # noqa: BLE001 - both hazards being proved
        # A shape that cannot be formatted discloses through the exception
        # instead, if the secret was in the raising code's own message; and if
        # it discloses nothing it is still the *other* hazard this path removes,
        # because before the correction that exception moved out of the filter
        # and into whichever handler formatted the record.
        rendered = f"{type(error).__name__}: {error}"
        if not any(f in rendered for f in (N29_V4, N29_V6, SYNTHETIC_CODE)):
            return

    assert any(fragment in rendered for fragment in (N29_V4, N29_V6, SYNTHETIC_CODE)), (
        f"shape {msg!r} must disclose unfiltered, or it proves nothing"
    )


@pytest.mark.parametrize("msg, args", N29_UNFAMILIAR)
def test_n29_no_fragment_of_an_unfamiliar_record_survives(
    msg: object, args: object
) -> None:
    """The contract in one assertion: nothing caller-controlled reaches the line.

    Not "the address is gone" and not "the credential is gone" — *no fragment*.
    That is the property a list of regex patterns cannot establish and a whole
    replacement can.
    """
    record = _n29_record(msg, args)

    assert RedactAccessLogQueryString().filter(record) is True

    formatted = _n29_format(record)
    for fragment in N29_FORBIDDEN_FRAGMENTS:
        assert fragment not in formatted, f"{fragment!r} survived {msg!r}"


@pytest.mark.parametrize("msg, args", N29_UNFAMILIAR)
def test_n29_an_unfamiliar_record_is_replaced_by_repository_owned_text(
    msg: object, args: object
) -> None:
    """What is left is a bounded marker this repository owns, and nothing else."""
    record = _n29_record(msg, args)

    RedactAccessLogQueryString().filter(record)

    assert record.msg in portal_server.WITHHELD_RECORDS, record.msg
    assert _n29_format(record) == record.msg


@pytest.mark.parametrize("msg, args", N29_UNFAMILIAR)
def test_n29_an_unfamiliar_record_keeps_nothing_a_formatter_could_reapply(
    msg: object, args: object
) -> None:
    """Requirement 3: `args`, `exc_info`, `exc_text` and `stack_info` are cleared."""
    record = _n29_record(msg, args)

    RedactAccessLogQueryString().filter(record)

    assert record.args is None
    assert record.exc_info is None
    assert record.exc_text is None
    assert record.stack_info is None


@pytest.mark.parametrize("msg, args", N29_UNFAMILIAR)
def test_n29_withholding_is_idempotent(msg: object, args: object) -> None:
    """`--workers`, a re-import or two filters must not change the marker."""
    record = _n29_record(msg, args)
    filter_ = RedactAccessLogQueryString()

    filter_.filter(record)
    once = _n29_format(record)
    filter_.filter(record)
    filter_.filter(record)

    assert _n29_format(record) == once


def test_n29_a_record_with_an_attached_exception_is_withheld_whole() -> None:
    """An attached exception puts a record outside the pinned contract.

    A uvicorn access record never carries one, which is exactly why the filter
    must not assume it. Previously the traceback was rendered and scrubbed; a
    traceback echoes the raising source line, so scrubbing it was the
    best-effort text path N-29 rejects. The category is the diagnostic now.
    """
    try:
        raise RuntimeError(f"failed for {N29_V4} {CALLBACK_TARGET}")
    except RuntimeError:
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=ACCESS_LOG_FORMAT,
        args=(f"{N29_V4}:54321", "GET", "/healthz", "1.1", 200),
        exc_info=exc_info,
    )

    RedactAccessLogQueryString().filter(record)

    formatted = _n29_format(record)
    assert record.msg == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_ATTACHED_DIAGNOSTIC
    )
    for fragment in N29_FORBIDDEN_FRAGMENTS:
        assert fragment not in formatted, fragment
    assert "Traceback" not in formatted


def test_n29_a_pre_rendered_exc_text_is_withheld_whole() -> None:
    """`exc_text` may already be a string by the time a filter runs."""
    record = _n29_record(ACCESS_LOG_FORMAT, (f"{N29_V4}:1", "GET", "/healthz", "1.1", 200))
    record.exc_text = f"Traceback (most recent call last):\n  peer {N29_V4}suffix"

    RedactAccessLogQueryString().filter(record)

    formatted = _n29_format(record)
    assert record.exc_text is None
    assert N29_V4 not in formatted
    assert "Traceback" not in formatted


def test_n29_attached_stack_text_is_withheld_whole() -> None:
    record = _n29_record(ACCESS_LOG_FORMAT, (f"{N29_V4}:1", "GET", "/healthz", "1.1", 200))
    record.stack_info = f"Stack:\n  from {N29_V6}tail to {CALLBACK_TARGET}"

    RedactAccessLogQueryString().filter(record)

    formatted = _n29_format(record)
    assert record.stack_info is None
    assert N29_V6 not in formatted
    assert SYNTHETIC_CODE not in formatted


# --- The pinned path: what it keeps, and the bound on each field ------------


def test_n29_only_the_pinned_format_keeps_method_path_protocol_and_status() -> None:
    """The other half of the contract: ordinary access lines are not degraded."""
    record = _client_record(f"{N29_V4}:54321", "/v1/characters")

    RedactAccessLogQueryString().filter(record)

    client, method, target, version, status = record.args
    assert (method, target, version, status) == ("GET", "/v1/characters", "1.1", 200)
    assert re.fullmatch(r"client-[0-9a-f]{8}", client)
    assert N29_V4 not in _n29_format(record)


def test_n29_the_pinned_path_still_redacts_the_query_string() -> None:
    record = _client_record(f"{N29_V4}:54321", CALLBACK_TARGET)

    RedactAccessLogQueryString().filter(record)

    formatted = _n29_format(record)
    assert f"/auth/discord/callback{REDACTED_QUERY}" in formatted
    assert SYNTHETIC_CODE not in formatted
    assert SYNTHETIC_STATE not in formatted


@pytest.mark.parametrize("text", N29_ADJACENT_V4 + N29_ADJACENT_V6)
def test_n29_an_address_in_the_request_path_does_not_survive_either(text: str) -> None:
    """The request path is caller-controlled, so §5 binds it too.

    `GET /x203.0.113.7y` would otherwise put a plaintext address in the access
    log through the *pinned* path — the same finding on the branch the handoff
    keeps. The path scrub is closed over its input rather than best-effort:
    every maximal run of address characters is either resolved to a pseudonym
    or removed.
    """
    record = _client_record("198.51.100.9:1", f"/probe/{text}")

    RedactAccessLogQueryString().filter(record)

    formatted = _n29_format(record)
    assert N29_V4 not in formatted, text
    assert N29_V6 not in formatted, text
    assert "fe80::1" not in formatted, text


@pytest.mark.parametrize(
    "target",
    [
        "/",
        "/healthz",
        "/my-characters",
        "/characters/0f3c1b2e-4a5d-4c6e-9a1b-2d3e4f5a6b7c",
        "/static/css/portal.4a3f2b1c9d8e.css",
        "/council/imports",
    ],
)
def test_n29_the_path_scrub_leaves_ordinary_portal_paths_intact(target: str) -> None:
    """Over-redaction is affordable only if it does not reach ordinary routes."""
    record = _client_record("198.51.100.9:1", target)

    RedactAccessLogQueryString().filter(record)

    assert record.args[2] == target


@pytest.mark.parametrize(
    "client, method, target, version, status, why",
    [
        (b"198.51.100.9:1", "GET", "/healthz", "1.1", 200, "client is not a string"),
        ("198.51.100.9:1", b"GET", "/healthz", "1.1", 200, "method is not a string"),
        ("198.51.100.9:1", "GET", b"/healthz", "1.1", 200, "target is not a string"),
        ("198.51.100.9:1", "GET", "/healthz", 1.1, 200, "version is not a string"),
        ("198.51.100.9:1", "GET", "/healthz", "1.1", "200", "status is not an int"),
        ("198.51.100.9:1", "GET", "/healthz", "1.1", True, "status is a bool"),
        ("198.51.100.9:1", "GET /x", "/healthz", "1.1", 200, "method is not a token"),
        ("198.51.100.9:1", "GET", "/healthz", "HTTP/1.1", 200, "version is not a number"),
        ("198.51.100.9:1", "GET", "/healthz", "1.1", 99, "status is below the range"),
        ("198.51.100.9:1", "GET", "/healthz", "1.1", 600, "status is above the range"),
        ("198.51.100.9:1", "GET", "/heal thz", "1.1", 200, "the path carries a space"),
        ("198.51.100.9:1", "GET", "/heal\nthz", "1.1", 200, "the path carries a newline"),
        ("198.51.100.9:1", "GET", "/" + "a" * 4096, "1.1", 200, "the path is unbounded"),
        ("x" * 512, "GET", "/healthz", "1.1", 200, "the client field is unbounded"),
    ],
)
def test_n29_a_field_outside_the_pinned_bounds_withholds_the_record(
    client: object, method: object, target: object, version: object, status: object, why: str
) -> None:
    """Each retained field is bounded, and a value outside its bound fails closed.

    The pinned branch's whole justification is that it knows what each argument
    is. A value it does not recognise is not a value it knows, so the record
    leaves the branch rather than being trusted field by field.
    """
    record = _n29_record(ACCESS_LOG_FORMAT, (client, method, target, version, status))

    RedactAccessLogQueryString().filter(record)

    assert record.msg in portal_server.WITHHELD_RECORDS, why
    assert record.args is None, why


def test_n29_the_pinned_path_invokes_no_caller_supplied_rendering() -> None:
    """Nothing on the retained branch calls `__str__` on caller-supplied data.

    An object is not a string, so it cannot be a pinned argument; the record is
    withheld before anything renders it. That is what removes "an argument whose
    `__str__` raises" from the retained path entirely, rather than catching it.
    """
    record = _n29_record(
        ACCESS_LOG_FORMAT, (_N29StrRaises(), "GET", "/healthz", "1.1", 200)
    )

    RedactAccessLogQueryString().filter(record)

    assert record.msg in portal_server.WITHHELD_RECORDS
    assert "cannot render" not in _n29_format(record)


# --- N-13's correlation, re-asserted across the correction ------------------


def test_n29_ipv4_correlation_is_unchanged_by_the_correction() -> None:
    """Same address, different ports, one pseudonym — N-13's property, intact."""
    pseudonyms = set()
    for port in (54321, 33012, 60998, 5432):
        record = _client_record(f"{N29_V4}:{port}", "/healthz")
        RedactAccessLogQueryString().filter(record)
        pseudonyms.add(record.args[0])

    assert len(pseudonyms) == 1, pseudonyms
    assert re.fullmatch(r"client-[0-9a-f]{8}", pseudonyms.pop())


def test_n29_ipv6_correlation_is_unchanged_by_the_correction() -> None:
    pseudonyms = set()
    for client in (
        f"{N29_V6}:54321",
        f"{N29_V6}:33012",
        f"[{N29_V6}]:54321",
        N29_V6,
    ):
        record = _client_record(client, "/healthz")
        RedactAccessLogQueryString().filter(record)
        pseudonyms.add(record.args[0])

    assert len(pseudonyms) == 1, pseudonyms


def test_n29_distinct_visitors_still_reach_distinct_pseudonyms() -> None:
    first, second = _client_record(f"{N29_V4}:1"), _client_record("198.51.100.9:1")

    RedactAccessLogQueryString().filter(first)
    RedactAccessLogQueryString().filter(second)

    assert first.args[0] != second.args[0]


def test_n29_the_pseudonym_is_idempotent_through_the_filter() -> None:
    record = _client_record(f"{N29_V4}:54321")
    filter_ = RedactAccessLogQueryString()

    filter_.filter(record)
    once = record.args[0]
    filter_.filter(record)
    filter_.filter(record)

    assert record.args[0] == once


def test_n29_the_filter_is_installed_on_the_access_logger_and_nowhere_else() -> None:
    """Requirement 5: this filter is not broadened to another logger."""
    access = logging.getLogger("uvicorn.access")
    access.filters = [f for f in access.filters if not isinstance(f, RedactAccessLogQueryString)]

    install_access_log_redaction()
    install_access_log_redaction()

    installed = [f for f in access.filters if isinstance(f, RedactAccessLogQueryString)]
    assert len(installed) == 1
    for other in (logging.getLogger(), logging.getLogger("uvicorn"), logging.getLogger("uvicorn.error")):
        assert not any(isinstance(f, RedactAccessLogQueryString) for f in other.filters), other.name


def test_n29_the_installed_filter_withholds_through_a_real_handler(caplog) -> None:
    """End to end: a real logger, a real handler, and the marker on the wire."""
    logger = logging.getLogger("test.n29.handler")
    logger.filters.clear()
    install_access_log_redaction(logger)

    with caplog.at_level(logging.INFO, logger="test.n29.handler"):
        logger.info("%s", [f"peer={N29_V4}suffix {CALLBACK_TARGET}"])

    text = caplog.text
    assert N29_V4 not in text
    assert SYNTHETIC_CODE not in text
    assert portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_UNPINNED_FORMAT
    ) in text


# ---------------------------------------------------------------------------
# N-31 — the retained method is caller-controlled too (2026-08-28)
#
# Codex EX-11/EX-12 *remediation* re-review of C-P3.5-AD. N-29's unfamiliar-record
# half was accepted and the retained request path was accepted, but the retained
# **method** was still returned unchanged. An HTTP method is an RFC 9110 token,
# `_HTTP_METHOD` repeats that syntax faithfully, and the token alphabet includes
# digits and `.`. So this passes every term of the pinned contract:
#
#     ("198.51.100.9:1", "203.0.113.7", "/healthz", "1.1", 200)
#     -> client-08c95168 - "203.0.113.7 /healthz HTTP/1.1" 200
#
# and puts a plaintext address in the access log through the branch the handoff
# keeps. Syntactic validity is not confidentiality: they are different
# properties, and the filter was checking the first while claiming the second.
#
# **The correction withholds the record rather than scrubbing the method.** The
# handoff offers both and prefers this one where scrubbing would leave ambiguous
# partial preservation, which is exactly what it would leave here: `X203.0.113.7Y`
# would become `X<pseudonym>Y`, a caller-controlled fragment kept around a removed
# span, in a field that has no operational meaning left once it carries an
# address. A method is not a method any more at that point.
#
# **Why the detection is complete over its input, which is the claim this section
# has to support.** The method's accepted alphabet contains no `:`, and every
# textual IPv6 literal contains at least two, so no IPv6 literal is expressible
# in a method at all — asserted below rather than asserted about. That leaves the
# IPv4 dotted quad, and `_scrub_addresses` already enumerates every start
# position and every length for those rather than trusting one greedy scan.
# Detection therefore reuses that same accepted rule: a method carries address
# material exactly when the rule would change it. The equivalence is checked
# below against an independent brute-force reference over the token alphabet.
#
# Each test falsifies first: the disclosure is reproduced against an unfiltered
# record, so none of them can pass vacuously.
# ---------------------------------------------------------------------------

import ipaddress  # noqa: E402 - the section's own helpers, read late
import random  # noqa: E402

#: The exact tuple the reviewer reproduced with, kept verbatim so this file
#: contains the finding rather than a paraphrase of it.
N31_REVIEWER_TUPLE = ("198.51.100.9:1", N29_V4, "/healthz", "1.1", 200)

#: Methods that are syntactically valid RFC 9110 tokens *and* carry an address.
#: Each `id` names the concealment, because that is what a failure has to say.
N31_ADDRESS_BEARING_METHODS = [
    pytest.param(N29_V4, id="method-is-exactly-the-address"),
    pytest.param(f"X{N29_V4}Y", id="letters-on-both-sides"),
    pytest.param(f"{N29_V4}Y", id="letters-after"),
    pytest.param(f"X{N29_V4}", id="letters-before"),
    pytest.param(f"{N29_V4}8", id="digit-after"),
    pytest.param(f"9{N29_V4}", id="digit-before"),
    pytest.param(f"{N29_V4}89", id="two-digits-after"),
    pytest.param(f"GET{N29_V4}", id="looks-like-a-verb-then-an-address"),
    pytest.param(f"{N29_V4}-{N29_V4}", id="two-address-spans-hyphenated"),
    pytest.param(f"{N29_V4}.{N29_V4}", id="two-address-spans-dotted"),
    pytest.param(f"{N29_V4}!{N29_V4}", id="two-address-spans-punctuated"),
    pytest.param(f"999.999.999.{N29_V4}", id="address-after-an-invalid-quad"),
    pytest.param(f"{N29_V4}89.9", id="address-inside-a-longer-dotted-run"),
    pytest.param(f"A.{N29_V4}", id="hex-letter-and-dot-prefix"),
    pytest.param(f"DEAD.BEEF.{N29_V4}", id="hex-words-then-an-address"),
    pytest.param(f"~{N29_V4}~", id="tilde-delimited"),
    pytest.param(f"_{N29_V4}_", id="underscore-delimited"),
    pytest.param("198.51.100.9", id="a-different-documentation-address"),
    pytest.param("127.0.0.1", id="loopback"),
    pytest.param("1.1.1.1", id="the-shortest-ipv4-literal"),
    pytest.param("255.255.255.255", id="the-longest-ipv4-literal"),
]

#: Methods an operator actually needs to keep reading. Standard verbs, WebDAV and
#: extension methods, and near-misses that look numeric without being addresses.
N31_OPERATIONAL_METHODS = [
    pytest.param("GET", id="get"),
    pytest.param("HEAD", id="head"),
    pytest.param("POST", id="post"),
    pytest.param("PUT", id="put"),
    pytest.param("PATCH", id="patch"),
    pytest.param("DELETE", id="delete"),
    pytest.param("OPTIONS", id="options"),
    pytest.param("TRACE", id="trace"),
    pytest.param("CONNECT", id="connect"),
    pytest.param("PROPFIND", id="propfind"),
    pytest.param("MKCALENDAR", id="mkcalendar"),
    pytest.param("VERSION-CONTROL", id="version-control-extension"),
    pytest.param("M-SEARCH", id="m-search-extension"),
    pytest.param("X-FREEDOM-BLADES", id="vendor-extension"),
    pytest.param("REPORT.V2", id="extension-with-a-dot"),
    pytest.param("QUERY", id="the-2024-query-method"),
    pytest.param("DEAD.BEEF", id="hex-words-that-are-not-an-address"),
    pytest.param("1.2.3", id="three-quads-are-not-an-address"),
    pytest.param("203.0.113", id="a-truncated-address"),
    pytest.param("999.999.999.999", id="four-invalid-quads"),
    pytest.param("A" * 32, id="the-longest-accepted-token"),
]


def _n31_record(
    client: str = "198.51.100.9:1",
    method: str = "GET",
    target: str = "/healthz",
    version: str = "1.1",
    status: int = 200,
) -> logging.LogRecord:
    """One pinned uvicorn record, with the method as the parameter under test."""
    return logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, ACCESS_LOG_FORMAT,
        (client, method, target, version, status), None,
    )


def _n31_reference_carries_ipv4(text: str) -> bool:
    """An independent brute force: does any substring parse as an IPv4 literal?

    Deliberately *not* the implementation's algorithm. Every substring of every
    length is offered to `ipaddress.IPv4Address`, with the dotted-quad shape
    required explicitly so the integer and octal spellings `ipaddress` also
    accepts are not counted — those are not what `_scrub_addresses` claims to
    find, and a reference that disagreed about the claim would test nothing.
    """
    for start in range(len(text)):
        for end in range(start + 1, len(text) + 1):
            candidate = text[start:end]
            if not re.fullmatch(r"[0-9]{1,3}(?:\.[0-9]{1,3}){3}", candidate):
                continue
            try:
                ipaddress.IPv4Address(candidate)
            except ValueError:
                continue
            return True
    return False


# --- Falsification: the disclosure is real, and it is real in this file ------


@pytest.mark.parametrize("method", N31_ADDRESS_BEARING_METHODS)
def test_n31_falsification_the_method_really_does_disclose_unfiltered(
    method: str,
) -> None:
    """Without the filter every one of these formats the address in clear text."""
    record = _n31_record(method=method)

    assert N29_V4 in _n29_format(record) or "198.51.100.9" in _n29_format(record)


def test_n31_falsification_the_reviewers_exact_tuple_is_the_one_asserted() -> None:
    """The reproduction in evidence §5S, formatted, before anything filters it.

    Pinned as a tuple rather than described, so the regression below is against
    the reviewer's case and not against an approximation of it.
    """
    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, ACCESS_LOG_FORMAT,
        N31_REVIEWER_TUPLE, None,
    )

    formatted = _n29_format(record)

    assert formatted == '198.51.100.9:1 - "203.0.113.7 /healthz HTTP/1.1" 200'


# --- The regression itself, on the fully formatted line ---------------------


@pytest.mark.parametrize("method", N31_ADDRESS_BEARING_METHODS)
def test_n31_no_address_bearing_method_reaches_the_formatted_line(
    method: str,
) -> None:
    """N-31. The **formatted** line, which is what reaches a journal.

    Asserting on `record.args` would miss a formatter that re-expands them, so
    the whole rendered line is searched for every fragment of the address.
    """
    record = _n31_record(method=method)

    RedactAccessLogQueryString().filter(record)

    formatted = _n29_format(record)
    assert N29_V4 not in formatted, method
    assert "203.0.113" not in formatted, method
    assert "198.51.100.9" not in formatted, method
    assert "127.0.0.1" not in formatted, method
    assert "255.255.255.255" not in formatted, method
    assert "1.1.1.1" not in formatted, method


@pytest.mark.parametrize("method", N31_ADDRESS_BEARING_METHODS)
def test_n31_an_address_bearing_method_withholds_the_whole_record(
    method: str,
) -> None:
    """Withheld, not scrubbed: no caller-controlled fragment of it survives.

    The alternative the handoff allows — scrubbing the method — would leave
    `X<pseudonym>Y`, keeping caller-chosen characters around the removed span in
    a field that no longer means anything. This asserts the choice actually made.
    """
    record = _n31_record(method=method)

    RedactAccessLogQueryString().filter(record)

    assert record.msg == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_ADDRESS_BEARING_METHOD
    ), method
    assert record.args is None, method
    assert record.exc_info is None and record.exc_text is None
    assert record.stack_info is None


def test_n31_the_reviewers_exact_tuple_is_withheld() -> None:
    """Evidence §5S's reproduction, end to end through the filter."""
    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, ACCESS_LOG_FORMAT,
        N31_REVIEWER_TUPLE, None,
    )

    RedactAccessLogQueryString().filter(record)

    assert _n29_format(record) == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_ADDRESS_BEARING_METHOD
    )


def test_n31_the_new_reason_is_repository_owned_and_in_the_closed_set() -> None:
    """The reason must carry nothing from the record, like the other six.

    It names a term of the contract — not the method, not its length, not a
    count of the spans found — because a reason derived from a value is a
    channel for the value.
    """
    assert portal_server.WITHHELD_ADDRESS_BEARING_METHOD == "address-bearing-method"
    assert (
        portal_server.WITHHELD_RECORD.format(
            reason=portal_server.WITHHELD_ADDRESS_BEARING_METHOD
        )
        in portal_server.WITHHELD_RECORDS
    )
    assert len(portal_server.WITHHELD_RECORDS) == 7


# --- The operational half: ordinary methods are not degraded ----------------


@pytest.mark.parametrize("method", N31_OPERATIONAL_METHODS)
def test_n31_an_ordinary_or_extension_method_still_reaches_the_log(
    method: str,
) -> None:
    """Over-refusal is affordable only if it does not reach real traffic.

    Standard verbs, WebDAV, vendor extensions and dotted extension methods all
    stay exactly as uvicorn supplied them. `999.999.999.999` and `203.0.113` are
    here deliberately: neither is an address, and a rule that refused them would
    be guessing at shape rather than deciding on content.
    """
    record = _n31_record(method=method)

    RedactAccessLogQueryString().filter(record)

    assert record.args is not None, method
    assert record.args[1] == method
    assert f'"{method} /healthz HTTP/1.1" 200' in _n29_format(record)


# --- Completeness over the accepted input, which is the required argument ---


def test_n31_no_ipv6_literal_is_expressible_in_the_method_alphabet() -> None:
    """Half the completeness argument, asserted rather than asserted about.

    Every textual IPv6 literal contains at least two `:` — that is what the
    separator means for a minimum of three fields, and `::` is two on its own.
    `_HTTP_METHOD` accepts no `:` at all, so no IPv6 literal can be spelled in a
    method, and only the IPv4 dotted quad remains to be found.
    """
    assert portal_server._HTTP_METHOD.fullmatch(":") is None
    assert portal_server._HTTP_METHOD.fullmatch("2001:db8::1") is None
    assert portal_server._HTTP_METHOD.fullmatch("::ffff:203.0.113.7") is None
    for form in (N29_V6, "fe80::1", "::1", "0:0:0:0:0:0:0:1", f"::ffff:{N29_V4}"):
        assert ":" in form, form
        assert portal_server._HTTP_METHOD.fullmatch(form) is None, form


def test_n31_the_method_bound_is_still_thirty_two_characters() -> None:
    """The other term the completeness argument rests on (requirement 6)."""
    assert portal_server._HTTP_METHOD.fullmatch("A" * 32) is not None
    assert portal_server._HTTP_METHOD.fullmatch("A" * 33) is None


def test_n31_detection_agrees_with_a_brute_force_reference_over_the_alphabet() -> None:
    """The completeness claim, checked rather than argued.

    2,000 pseudo-random token-valid methods — a third of them seeded with a real
    address at a random offset — are classified by the filter and by
    `_n31_reference_carries_ipv4`, which enumerates *every* substring. A single
    disagreement in either direction fails: a method the reference calls
    address-bearing that the filter keeps is a disclosure, and one the filter
    withholds that the reference calls clean is over-refusal.

    Seeded, so a failure is reproducible and the suite does not change what it
    asserts between runs.
    """
    alphabet = "ABCXYZabcxyz0123456789.-_~!"
    addresses = ("203.0.113.7", "198.51.100.9", "127.0.0.1", "255.255.255.255")
    #: Near misses, seeded as often as the real addresses so the check runs in
    #: **both** directions. Without them a detector that matched the dotted-quad
    #: shape without validating the octets — over-refusing `999.999.999.999` —
    #: would agree with the reference on every case this test generated.
    near_misses = ("999.999.999.999", "256.1.1.1", "1.2.3", "203.0.113", "1.1.1.1.1")
    rng = random.Random(20260828)
    disagreements: list[tuple[str, bool, bool]] = []

    for index in range(2000):
        length = rng.randint(1, 32)
        method = "".join(rng.choice(alphabet) for _ in range(length))
        if index % 3 == 0:
            address = rng.choice(addresses)
            cut = rng.randint(0, max(0, 32 - len(address)))
            method = (method[:cut] + address + method[cut:])[:32]
        elif index % 3 == 1:
            near = rng.choice(near_misses)
            cut = rng.randint(0, max(0, 32 - len(near)))
            method = (method[:cut] + near + method[cut:])[:32]
        if portal_server._HTTP_METHOD.fullmatch(method) is None:
            continue

        record = _n31_record(method=method)
        RedactAccessLogQueryString().filter(record)
        withheld = record.args is None
        expected = _n31_reference_carries_ipv4(method)
        if withheld != expected:
            disagreements.append((method, withheld, expected))

    assert not disagreements, disagreements[:10]


def test_n31_every_offset_of_an_address_in_a_bounded_method_is_found() -> None:
    """Exhaustive over position, since the bound makes that possible.

    `203.0.113.7` is 11 characters and the method bound is 32, so every start
    offset it can occupy is enumerable. A rule that scanned once and gave up
    after the first failed reading — the defect `_scrub_ipv4_literals` was
    written to avoid — fails here at the offsets it skipped past.
    """
    filler = "9"
    for offset in range(0, 32 - len(N29_V4) + 1):
        method = filler * offset + N29_V4
        method += filler * (32 - len(method))
        assert portal_server._HTTP_METHOD.fullmatch(method) is not None, method

        record = _n31_record(method=method)
        RedactAccessLogQueryString().filter(record)

        assert record.args is None, f"offset {offset}: {method}"
        assert N29_V4 not in _n29_format(record), f"offset {offset}: {method}"


# --- Requirements 1, 2, 3, 6, 7 and 8, re-asserted across the correction -----


def test_n31_query_removal_and_client_correlation_hold_in_one_record() -> None:
    """Requirements 1, 2 and 3 together, on a record that exercises all three.

    A single access line with an ordinary method, a credential-bearing query
    string and a real client address: the query goes and leaves only its marker,
    the client becomes the keyed pseudonym, and the same visitor on a different
    ephemeral port reaches the same pseudonym.
    """
    first = _n31_record(f"{N29_V4}:54321", "GET", CALLBACK_TARGET)
    second = _n31_record(f"{N29_V4}:33012", "GET", CALLBACK_TARGET)

    RedactAccessLogQueryString().filter(first)
    RedactAccessLogQueryString().filter(second)

    formatted = _n29_format(first)
    assert f"/auth/discord/callback{REDACTED_QUERY}" in formatted
    assert SYNTHETIC_CODE not in formatted
    assert SYNTHETIC_STATE not in formatted
    assert "code=" not in formatted and "state=" not in formatted
    assert N29_V4 not in formatted
    assert re.search(r"client-[0-9a-f]{8}", formatted)
    assert first.args[0] == second.args[0], "one visitor, one pseudonym"


def test_n31_ipv6_client_correlation_is_unchanged_by_the_method_handling() -> None:
    """Requirement 3 for IPv6, which the method rule cannot reach at all."""
    pseudonyms = {
        _filtered_client(client)
        for client in (f"{N29_V6}:54321", f"[{N29_V6}]:33012", N29_V6)
    }

    assert len(pseudonyms) == 1, pseudonyms


def _filtered_client(client: str) -> str:
    record = _n31_record(client, "GET", "/healthz")
    RedactAccessLogQueryString().filter(record)
    return record.args[0]


@pytest.mark.parametrize("text", N29_ADJACENT_V4 + N29_ADJACENT_V6)
def test_n31_request_path_address_handling_is_intact(text: str) -> None:
    """Requirement 6. N-29's path scrub is not weakened by the method rule."""
    record = _n31_record("198.51.100.9:1", "GET", f"/probe/{text}")

    RedactAccessLogQueryString().filter(record)

    formatted = _n29_format(record)
    assert N29_V4 not in formatted, text
    assert N29_V6 not in formatted, text
    assert "fe80::1" not in formatted, text


@pytest.mark.parametrize(
    "client, method, target, version, status, why",
    [
        (b"198.51.100.9:1", "GET", "/healthz", "1.1", 200, "client is not a string"),
        ("198.51.100.9:1", b"GET", "/healthz", "1.1", 200, "method is not a string"),
        ("198.51.100.9:1", "GET", b"/healthz", "1.1", 200, "target is not a string"),
        ("198.51.100.9:1", "GET", "/healthz", 1.1, 200, "version is not a string"),
        ("198.51.100.9:1", "GET", "/healthz", "1.1", "200", "status is not an int"),
        ("198.51.100.9:1", "GET", "/healthz", "1.1", True, "status is a bool"),
        ("198.51.100.9:1", "GET /x", "/healthz", "1.1", 200, "method is not a token"),
        ("198.51.100.9:1", "A" * 33, "/healthz", "1.1", 200, "the method is unbounded"),
        ("198.51.100.9:1", "", "/healthz", "1.1", 200, "the method is empty"),
        ("198.51.100.9:1", "GET", "/healthz", "HTTP/1.1", 200, "version is not a number"),
        ("198.51.100.9:1", "GET", "/healthz", "1.1", 99, "status is below the range"),
        ("198.51.100.9:1", "GET", "/healthz", "1.1", 600, "status is above the range"),
        ("198.51.100.9:1", "GET", "/heal thz", "1.1", 200, "the path carries a space"),
        ("198.51.100.9:1", "GET", "/" + "a" * 4096, "1.1", 200, "the path is unbounded"),
        ("x" * 512, "GET", "/healthz", "1.1", 200, "the client field is unbounded"),
    ],
)
def test_n31_every_pinned_field_bound_still_withholds_the_record(
    client: object, method: object, target: object, version: object, status: object, why: str
) -> None:
    """Requirement 6. The bounds N-29 added are not relaxed by the method rule."""
    record = _n29_record(ACCESS_LOG_FORMAT, (client, method, target, version, status))

    RedactAccessLogQueryString().filter(record)

    assert record.msg in portal_server.WITHHELD_RECORDS, why
    assert record.args is None, why


@pytest.mark.parametrize("method", N31_ADDRESS_BEARING_METHODS)
def test_n31_withholding_an_address_bearing_method_is_idempotent(
    method: str,
) -> None:
    """Requirement 7. Two passes agree, including on the reason recorded.

    Without the already-withheld guard the second pass would reclassify the
    marker the first wrote as an unpinned format string, so the reason would
    depend on how many times the record was filtered.
    """
    record = _n31_record(method=method)
    filter_ = RedactAccessLogQueryString()

    filter_.filter(record)
    once = (record.msg, record.args)
    filter_.filter(record)
    filter_.filter(record)

    assert (record.msg, record.args) == once, method
    assert record.msg == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_ADDRESS_BEARING_METHOD
    )


@pytest.mark.parametrize("method", N31_OPERATIONAL_METHODS)
def test_n31_filtering_an_ordinary_record_twice_is_still_a_no_op(
    method: str,
) -> None:
    """Requirement 7 on the retained branch, where the pseudonym must not rehash."""
    record = _n31_record(f"{N29_V4}:54321", method, CALLBACK_TARGET)
    filter_ = RedactAccessLogQueryString()

    filter_.filter(record)
    once = record.args
    filter_.filter(record)

    assert record.args == once, method


def test_n31_the_filter_is_still_installed_only_on_the_access_logger() -> None:
    """Requirement 8. The method rule does not broaden the installation."""
    access = logging.getLogger("uvicorn.access")
    access.filters = [
        f for f in access.filters if not isinstance(f, RedactAccessLogQueryString)
    ]

    install_access_log_redaction()
    install_access_log_redaction()

    installed = [
        f for f in access.filters if isinstance(f, RedactAccessLogQueryString)
    ]
    assert len(installed) == 1
    for other in (
        logging.getLogger(),
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.error"),
        logging.getLogger("uvicorn.asgi"),
    ):
        assert not any(
            isinstance(f, RedactAccessLogQueryString) for f in other.filters
        ), other.name


def test_n31_an_address_bearing_method_is_withheld_through_a_real_handler(
    caplog,
) -> None:
    """End to end: a real logger, a real handler, and nothing of it on the wire."""
    logger = logging.getLogger("test.n31.handler")
    logger.filters.clear()
    install_access_log_redaction(logger)

    with caplog.at_level(logging.INFO, logger="test.n31.handler"):
        logger.info(ACCESS_LOG_FORMAT, *N31_REVIEWER_TUPLE)

    text = caplog.text
    assert N29_V4 not in text
    assert "203.0.113" not in text
    assert portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_ADDRESS_BEARING_METHOD
    ) in text


# --- Requirement 4: the unfamiliar-record tests are unchanged ----------------


def test_n31_the_unfamiliar_record_contract_is_untouched() -> None:
    """Requirement 4, asserted here as well as left standing above.

    The N-29 section's whole-withholding tests are unmodified by this
    remediation — no assertion in them was relaxed, and none was deleted. This
    restates the property they hold so a future edit to the method rule that
    weakened the fallback would fail in this section too, not only in that one.
    """
    for msg, args, reason in (
        ("%s", ([f"peer={N29_V4}suffix"],), portal_server.WITHHELD_UNPINNED_FORMAT),
        (
            ACCESS_LOG_FORMAT,
            (f"{N29_V4}:1", "GET", CALLBACK_TARGET, "1.1", 200, "extra"),
            portal_server.WITHHELD_UNPINNED_ARGUMENT_SHAPE,
        ),
        (
            ACCESS_LOG_FORMAT,
            (f"{N29_V4}:1", b"GET", "/healthz", "1.1", 200),
            portal_server.WITHHELD_UNPINNED_ARGUMENT_TYPE,
        ),
        (
            ACCESS_LOG_FORMAT,
            (f"{N29_V4}:1", "GET", "/healthz", "1.1", 600),
            portal_server.WITHHELD_UNPINNED_ARGUMENT_VALUE,
        ),
        (
            ACCESS_LOG_FORMAT,
            (f"{N29_V4}:1", "GET", "/heal thz", "1.1", 200),
            portal_server.WITHHELD_UNPINNED_REQUEST_TARGET,
        ),
    ):
        record = _n29_record(msg, args)

        RedactAccessLogQueryString().filter(record)

        formatted = _n29_format(record)
        assert record.msg == portal_server.WITHHELD_RECORD.format(reason=reason), msg
        assert record.args is None
        for fragment in N29_FORBIDDEN_FRAGMENTS:
            assert fragment not in formatted, (msg, fragment)


def test_n31_an_attached_diagnostic_still_outranks_the_method_rule() -> None:
    """Order matters: what is *attached* is decided before anything is inspected.

    A record carrying both an exception and an address-bearing method is withheld
    for the attachment, because that check comes first and because the reason a
    reader needs is the one that says a traceback was present.
    """
    try:
        raise ValueError(f"cannot render {N29_V4} {CALLBACK_TARGET}")
    except ValueError:
        record = logging.LogRecord(
            "uvicorn.access", logging.INFO, "", 0, ACCESS_LOG_FORMAT,
            ("198.51.100.9:1", N29_V4, "/healthz", "1.1", 200), sys.exc_info(),
        )

    RedactAccessLogQueryString().filter(record)

    formatted = _n29_format(record)
    assert record.msg == portal_server.WITHHELD_RECORD.format(
        reason=portal_server.WITHHELD_ATTACHED_DIAGNOSTIC
    )
    assert N29_V4 not in formatted
    assert "cannot render" not in formatted


# ---------------------------------------------------------------------------
# N-32 — the deterministic reproduction and the mutation (2026-08-28)
#
# The correction above is only worth what its falsification is worth, and the
# defect it corrects is one that appears once every few hundred process starts.
# A regression that waits for an unlucky key is not a regression test, so the
# collision is *made* here rather than waited for: `_digest` is monkeypatched at
# its boundary to return the eight characters the independent rerun observed,
# and everything else — the parsing, the prefix choice, the filter, the
# formatter — runs as it ships.
#
# The three tests that matter are, in order: the old rule fails on this
# pseudonym; the corrected rule passes on it; and a mutation that hands back the
# raw client or the raw address fails the corrected rule. Without the third, the
# correction could have been an assertion that no longer asserts anything.
#
# Nothing here changes production code. `_digest` is restored by `monkeypatch`
# at the end of each test, and no injection seam was added to
# `tools/portal_server.py` for any of it.
# ---------------------------------------------------------------------------

#: The rerun's exact case, from evidence §5U: this source, under the key that
#: process happened to draw, rendered as this pseudonym, whose `999` is the
#: source's `999` by coincidence and not by preservation.
N32_SOURCE = "203.0.113.999:54321"
N32_DIGEST = "59990025"
N32_PSEUDONYM = f"client-unknown-{N32_DIGEST}"

#: The one case in `UNFAMILIAR_CLIENT_CASES` the rerun failed on.
N32_CASE = next(
    case for case in UNFAMILIAR_CLIENT_CASES if case.value == N32_SOURCE
)


def _n32_pin_the_digest(monkeypatch, digest: str = N32_DIGEST) -> None:
    """Fix the digest boundary so the pseudonym no longer depends on the key.

    The narrowest seam that reproduces the finding: `_pseudonymise_client` and
    `_pseudonymise_address` both reach `_digest` as a module global, so pinning
    it leaves every other decision — reading the port, failing to parse the
    host, choosing `client-unknown-` — to the shipped code.
    """
    monkeypatch.setattr(portal_server, "_digest", lambda material: digest)


def _n32_the_old_fragment_rule(source: str, text: str) -> None:
    """The assertion as it stood before this correction, restated locally.

    Restated rather than imported, because the point of a falsification is that
    it still holds after the defect is gone from the file.
    """
    for fragment in re.split(r"[.:/]", source):
        if len(fragment) >= 3:
            assert fragment not in text, source


def test_n32_falsification_the_old_fragment_rule_fails_on_a_safe_pseudonym(
    monkeypatch,
) -> None:
    """The defect, made deterministic: a safe pseudonym that the old rule rejects.

    This is the whole finding in one assertion. The pseudonym below discloses
    nothing — the next test says so — and the rule that used to guard it fails
    anyway, because `59990025` contains `999` and the source contains `999`.
    """
    _n32_pin_the_digest(monkeypatch)

    pseudonym = portal_server._pseudonymise_client(N32_SOURCE)

    assert pseudonym == N32_PSEUDONYM, pseudonym
    with pytest.raises(AssertionError):
        _n32_the_old_fragment_rule(N32_SOURCE, pseudonym)


def test_n32_falsification_the_old_rule_fails_on_the_formatted_line_too(
    monkeypatch,
) -> None:
    """The second failing test of the rerun, reproduced the same way."""
    _n32_pin_the_digest(monkeypatch)
    record = _client_record(N32_SOURCE)

    RedactAccessLogQueryString().filter(record)
    formatted = logging.Formatter().format(record)

    assert formatted.startswith(N32_PSEUDONYM), formatted
    with pytest.raises(AssertionError):
        _n32_the_old_fragment_rule(N32_SOURCE, formatted)


def test_n32_the_corrected_rule_passes_on_that_same_pseudonym(monkeypatch) -> None:
    """And nothing of the source survives it: not the field, not the host.

    The two assertions the suite runs, against the exact value that failed the
    old ones. A digest that had preserved the source would fail these.
    """
    _n32_pin_the_digest(monkeypatch)
    record = _client_record(N32_SOURCE)

    RedactAccessLogQueryString().filter(record)

    _assert_the_pseudonym_is_safe(
        N32_CASE, portal_server._pseudonymise_client(N32_SOURCE)
    )
    _assert_the_access_line_is_safe(N32_CASE, logging.Formatter().format(record))


@pytest.mark.parametrize(
    "mutation, what",
    [
        (lambda value: str(value), "the raw client field"),
        (lambda value: str(value).rpartition(":")[0], "the raw host address"),
        (
            lambda value: f"client-unknown-{str(value).rpartition(':')[0]}",
            "the raw host address wearing the pseudonym's prefix",
        ),
    ],
)
def test_n32_a_raw_pass_through_still_fails_the_corrected_rule(
    monkeypatch, mutation, what: str
) -> None:
    """The mutation test: a real disclosure must still be caught.

    Each mutation replaces `_pseudonymise_client` with something that hands back
    what the pseudonym exists to hide. The third is the interesting one — it
    keeps the prefix, so a corrected rule that had checked only the *label* would
    pass it. The corrected rule checks the complete values as well, and fails.
    """
    monkeypatch.setattr(portal_server, "_pseudonymise_client", mutation)
    record = _client_record(N32_SOURCE)

    RedactAccessLogQueryString().filter(record)
    formatted = logging.Formatter().format(record)

    with pytest.raises(AssertionError):
        _assert_the_pseudonym_is_safe(N32_CASE, mutation(N32_SOURCE))
    with pytest.raises(AssertionError):
        _assert_the_access_line_is_safe(N32_CASE, formatted)


@pytest.mark.parametrize("case", UNFAMILIAR_CLIENT_CASES, ids=UNFAMILIAR_CLIENT_IDS)
def test_n32_no_forbidden_value_can_occur_inside_a_pseudonym(
    case: _UnfamiliarClient,
) -> None:
    """Why the corrected assertions are deterministic where the old ones were not.

    A pseudonym is `client-unknown-` followed by eight hexadecimal characters, so
    the set of characters one can contain is fixed and small. Every value the
    table forbids carries at least one character outside that set, which makes
    its absence a fact about the alphabet rather than a fact about the key. The
    old rule forbade fragments drawn from `[0-9]` alone, every one of which is
    inside the set — which is exactly how `999` got in.
    """
    alphabet = set("client-unknown-") | set("0123456789abcdef")

    for forbidden in case.forbidden:
        assert forbidden, case.why
        assert set(forbidden) - alphabet, (
            f"{forbidden!r} is spelled entirely from the pseudonym's own "
            f"alphabet, so asserting its absence would be probabilistic — N-32"
        )


@pytest.mark.parametrize("case", UNFAMILIAR_CLIENT_CASES, ids=UNFAMILIAR_CLIENT_IDS)
def test_n32_every_forbidden_value_really_is_present_in_its_source(
    case: _UnfamiliarClient,
) -> None:
    """The table must forbid what the source actually spells.

    A `forbidden` entry that is not in its own `value` would be a test asserting
    the absence of something that was never there.
    """
    for forbidden in case.forbidden:
        assert forbidden in case.value, case.why


@pytest.mark.parametrize("case", UNFAMILIAR_CLIENT_CASES, ids=UNFAMILIAR_CLIENT_IDS)
def test_n32_every_complete_ipv4_literal_in_the_source_is_absent(
    case: _UnfamiliarClient,
) -> None:
    """Property 3, taken from the source by brute force rather than by hand.

    The hand-written table above is the readable contract; this is the mechanical
    one, so a value added to the table later cannot silently skip the address
    check. Every substring of every length is offered to `ipaddress.IPv4Address`
    with the dotted-quad shape required explicitly — the same independent
    reference the N-31 tests use, and for the same reason.
    """
    record = _client_record(case.value)

    RedactAccessLogQueryString().filter(record)
    formatted = logging.Formatter().format(record)

    literals = set()
    for start in range(len(case.value)):
        for end in range(start + 1, len(case.value) + 1):
            candidate = case.value[start:end]
            if not re.fullmatch(r"[0-9]{1,3}(?:\.[0-9]{1,3}){3}", candidate):
                continue
            try:
                ipaddress.IPv4Address(candidate)
            except ValueError:
                continue
            literals.add(candidate)

    for literal in literals:
        assert literal not in formatted, (case.value, literal)
        assert literal not in _pseudonymise_client(case.value), case.value
