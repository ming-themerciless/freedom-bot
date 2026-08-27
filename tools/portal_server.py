"""Operator entry point: build the portal for an ASGI server.

    ./venv-web/bin/python -m uvicorn tools.portal_server:application --factory

`create_app()` deliberately takes **exactly one** configuration authority — a
settings graph or a composition built from one — and refuses to be called with
neither, because a factory that silently read the environment would be a second
authority nothing could require to agree with the first. That refusal is correct,
and it means an ASGI server's `--factory` cannot call `create_app` directly: the
server calls it with no arguments.

This module is the missing half-line, and it lives in `tools/` because that is
where operator entry points live (`.agents/AGENTS.md`, repository map). It adds
no route, no view model, no dependency and no behaviour; it reads the environment
once, exactly as `tools.freedom_worker` does, and names which of the two
processes is reading so S-11 has its subject.

Authored 2026-08-23 by P3.5. It exists because the deployment step needed it, and
nothing before P3.5 ever started this process from a unit file.

## The access-log query-string redaction (N-7, 2026-08-26)

Added for a finding SP-12 produced on its first run against the deployed journal:
the OAuth authorization code and state were being written to the systemd journal
in clear text, failing TC-OPS-05's "no token data in monitoring output".

**The application was not the leak.** It logs exactly two kinds of line — startup
warnings that name variables and never values, and failure lines carrying a
correlation UUID and a path. The leak is `uvicorn.access`, whose default format
logs `get_path_with_query_string(scope)`; and R-04 `/auth/discord/callback` is the
one route that receives credentials **as query parameters**, because that is how
the provider redirects. Every successful login therefore wrote a code.

**Why the filter is installed here rather than in the unit.** `--no-access-log`
would fix the disclosure by destroying the operational visibility an operator
needs during an incident, which is the wrong trade. A `--log-config` file would
work but adds a deployment artifact to keep in step with the unit. This module is
already the process's one operator entry point, and `uvicorn.config.Config`
calls `configure_logging()` in `__init__` — **before** `load()` imports this
factory — so a filter added at import time is installed after `dictConfig` has
run and is not wiped by it. **No unit change, no new file, and the redaction
cannot be deployed without the code that needs it.**

**Why the whole query string goes, rather than an allowlist of safe keys.**
An allowlist is a control someone must maintain: the day a route gains a
parameter carrying a token, an allowlist that was not updated leaks it, and
nothing fails. Dropping the whole query string fails safe instead, and costs
little — the diagnostics that were being read out of query strings
(`?failure=…&correlation=…`) are already available from the application's own
correlation-ID logging and from the audit table, which is where a reviewer is
supposed to look for them anyway. The marker `?<redacted>` is kept so a reader
can tell "there was a query string" from "there was none"; that distinction is
occasionally what an operator needs and it discloses nothing.

**Two paths, and only one of them looks at the record's structure.** The pinned
uvicorn 0.32.1 access line is redacted precisely, at the one argument that
carries the request target. Everything else is rendered by the filter and
redacted as text, so its safety rests on the output rather than on a list of
argument types the filter claims to understand. `RedactAccessLogQueryString`
explains why the alternative — enumerating containers — cannot be made to work.
"""

from __future__ import annotations

import hashlib
import logging
import re
import secrets
import os
import traceback

from fastapi import FastAPI

from adapters.web.app import create_app
from application.web.config import ProcessRole, WebSettings

#: uvicorn logs `'%s - "%s %s HTTP/%s" %d'` with the request target — path plus
#: query string — as the third argument. Both the httptools and h11 protocol
#: implementations use the same logger and the same shape, so filtering the
#: logger covers both.
_ACCESS_LOGGER = "uvicorn.access"
#: The **exact** format string uvicorn 0.32.1 logs an access line with, in both
#: `httptools_impl` and `h11_impl`. The precise-redaction branch is taken **only**
#: for this contract, because recognising a record by its *shape* alone is not
#: enough: a future uvicorn that prepends a field would still present a tuple
#: with a string at index 2, and the filter would confidently redact the wrong
#: argument while the credential sailed past in the next one. That is not
#: hypothetical — it was caught by a test written for Codex finding I-1.
ACCESS_LOG_FORMAT = '%s - "%s %s HTTP/%s" %d'
_CLIENT_ARGUMENT = 0
_REQUEST_TARGET_ARGUMENT = 2
_ACCESS_LOG_ARITY = 5
REDACTED_QUERY = "?<redacted>"

#: Per-process, random, never persisted or logged (N-13).
#:
#: **Why the hash is keyed.** An *unkeyed* digest of an IPv4 address is not
#: pseudonymisation at all: the input space is 2^32, so a reader with the digest
#: recovers the address by exhausting it in seconds. A key the reader does not
#: have removes that, and generating it per process means a restart re-randomises
#: it and nothing on disk can be correlated with anything else.
#:
#: **What it costs:** correlation holds within one process lifetime and not
#: across a restart. That is the right trade for an access log — an incident is
#: investigated in the process it happened in — and it is the same pattern the
#: operational contract already accepts for rate-limit buckets, which are
#: recorded as a bucket hash rather than an address.
_CLIENT_PSEUDONYM_KEY = secrets.token_bytes(16)

#: Loose candidates, strictly validated. A pattern alone would mangle a
#: timestamp like `12:34:56`, which is why every candidate is handed to
#: `ipaddress` and replaced only if it really is an address.
_ADDRESS_CANDIDATE = re.compile(
    r"\b(?:\d{1,3}(?:\.\d{1,3}){3}|[0-9A-Fa-f:]{2,45})\b"
)


#: A value this filter has already pseudonymised. Recognised so that filtering a
#: record twice is a no-op — uvicorn's client field is `host:port` and can never
#: take this shape, so nothing real is mistaken for an already-redacted value.
_PSEUDONYM = re.compile(r"^client-[0-9a-f]{8}$")


def _pseudonymise_client(value: object) -> str:
    """A stable per-process pseudonym for one client address."""
    text = str(value)
    if _PSEUDONYM.match(text):
        return text
    digest = hashlib.blake2s(
        text.encode("utf-8", "replace"),
        key=_CLIENT_PSEUDONYM_KEY,
        digest_size=4,
    ).hexdigest()
    return f"client-{digest}"


def _scrub_addresses(text: str) -> str:
    """Replace every IP literal in `text` with a pseudonym.

    Used only on the fallback path and on attached tracebacks. Best-effort by
    construction — an address embedded inside a longer token is not isolated by
    the candidate pattern — which is why the pinned path below redacts the
    client argument exactly rather than relying on this.
    """
    import ipaddress

    def replace(match: re.Match[str]) -> str:
        candidate = match.group(0)
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            return candidate
        return _pseudonymise_client(candidate)

    return _ADDRESS_CANDIDATE.sub(replace, text)
#: What a record becomes when it cannot be rendered at all — mismatched
#: placeholders, or an argument whose `__str__` raises. It carries the
#: exception's type name and nothing else from the record, because the format
#: string, the arguments and the exception's own message are each capable of
#: being the thing that carried the credential.
UNRENDERABLE_RECORD = "<uvicorn.access record could not be rendered: {error}>"


def _redact(text: str) -> str:
    """Drop everything from the first `?` onward, leaving a marker.

    One rule, so the guarantee it underwrites is provable by reading it: **no
    character following the first `?` survives.** Everything the filter allows a
    handler to format is passed through this function, which is why the
    guarantee does not depend on knowing what kind of object carried the query
    string.
    """
    if "?" in text:
        text = text.partition("?")[0] + REDACTED_QUERY
    return _scrub_addresses(text)


class RedactAccessLogQueryString(logging.Filter):
    """Remove the query string from `uvicorn.access` records (N-7).

    Returns True always: this filter redacts, it never drops a line. Losing the
    access record entirely would trade one operational blindness for another.

    ## The accepted input contract, and what happens outside it

    **Rewritten 2026-08-26 after Codex re-review of finding I-1.** Two earlier
    versions were wrong in the same way, and the second one was wrong while
    claiming not to be. The first recognised uvicorn 0.32.1's five-tuple and
    passed every other shape through untouched. The second scrubbed tuples and
    mapping *values* and claimed that made unfamiliar records fail closed — but
    it inspected containers by type, so `record.args = ["/cb?code=…"]` walked
    straight through, and so did any object whose `__str__` renders a request
    target. **Enumerating containers cannot work**: the set of objects that can
    render a query string is not enumerable, and every enumeration is a claim
    that will silently become false.

    So there are exactly two paths, and the second one does not inspect
    structure at all:

    1. **The pinned contract** — `record.msg` is exactly `ACCESS_LOG_FORMAT` and
       the arguments are a five-tuple whose third element is a string. This is
       uvicorn 0.32.1's access line, in both `httptools_impl` and `h11_impl`.
       Only the request target is redacted, so the client, method, HTTP version
       and status code reach the log untouched and ordinary operational use of
       the access log is unaffected. The gate is the *format string*, not the
       shape: a future uvicorn prepending a field would still present a tuple
       with a string at index 2, and matching on shape alone would redact the
       wrong argument while the credential sailed past in the next one.

    2. **Everything else** — the record is *rendered first*, by this filter,
       and the rendered text is what gets redacted. `record.msg` becomes that
       redacted text and `record.args` becomes `None`. Whatever the arguments
       were — a list, a set, a nested mapping, a custom object, nothing at all —
       they have already become characters by the time the redaction runs, and
       `_redact` removes every character after the first `?`. The safety of this
       path therefore rests on one property of the *output*, not on a list of
       supported input types.

    A record that cannot be rendered at all — mismatched placeholders, an
    argument whose `__str__` raises — becomes `UNRENDERABLE_RECORD`, carrying
    the exception's *type name* and nothing else from the record. That closes
    the second failure mode of the fallback path: because `record.args` is left
    `None`, a malformed record can no longer raise inside a handler either. It
    could before.

    Any attached traceback or stack is rendered and redacted the same way, and
    `exc_info` is cleared once its text has been captured, so the guarantee
    covers everything a formatter appends rather than only the message. No
    uvicorn access record carries either, which is exactly why leaving them
    outside the guarantee would be an assumption rather than a control.

    Over-redacting an unfamiliar record on *this* logger costs an operator part
    of one access line; under-redacting it costs a credential. `uvicorn.access`
    logs nothing but access lines, which is what makes the second path safe to
    take here, and is why this filter is installed on no other logger.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not self._redact_pinned_access_line(record):
            self._render_and_redact(record)
        self._redact_attached_text(record)
        return True

    @staticmethod
    def _redact_pinned_access_line(record: logging.LogRecord) -> bool:
        """Redact the request target if this is uvicorn 0.32.1's access line.

        Recognition and redaction are one step so that the recognised tuple is
        never re-fetched, and the return value tells the caller whether the
        fail-closed path still has to run. Every condition is a term of the
        pinned contract: the format string, the arity, and a string at the index
        that contract puts the request target at.
        """
        arguments = record.args
        if (
            record.msg != ACCESS_LOG_FORMAT
            or not isinstance(arguments, tuple)
            or len(arguments) != _ACCESS_LOG_ARITY
        ):
            return False
        target = arguments[_REQUEST_TARGET_ARGUMENT]
        if not isinstance(target, str):
            return False
        redacted = list(arguments)
        # N-13: the client address, every time — not only when it parses as an
        # IP literal. `--proxy-headers` puts the true visitor address here, and
        # the operational contract §5 prohibits a plaintext address in any log
        # line, whatever its form.
        redacted[_CLIENT_ARGUMENT] = _pseudonymise_client(arguments[_CLIENT_ARGUMENT])
        if "?" in target:
            redacted[_REQUEST_TARGET_ARGUMENT] = _redact(target)
        record.args = tuple(redacted)
        return True

    @staticmethod
    def _render_and_redact(record: logging.LogRecord) -> None:
        """Collapse an unfamiliar record to already-rendered, already-redacted text."""
        try:
            rendered = record.getMessage()
        except Exception as error:  # noqa: BLE001 - a record we cannot render must still be safe
            # Nothing from the record survives: not the format string, not an
            # argument, not the exception's message, because any of them may be
            # what carries the credential. A type name is a Python identifier.
            rendered = UNRENDERABLE_RECORD.format(error=type(error).__name__)
        record.msg = _redact(rendered)
        record.args = None

    @staticmethod
    def _redact_attached_text(record: logging.LogRecord) -> None:
        """Redact an attached traceback or stack, which a formatter also emits."""
        if record.exc_text is None and record.exc_info is not None:
            try:
                record.exc_text = "".join(traceback.format_exception(*record.exc_info))
            except Exception as error:  # noqa: BLE001 - same reasoning as above
                record.exc_text = UNRENDERABLE_RECORD.format(error=type(error).__name__)
        record.exc_info = None
        if record.exc_text is not None:
            record.exc_text = _redact(record.exc_text)
        if record.stack_info is not None:
            record.stack_info = _redact(record.stack_info)


def install_access_log_redaction(logger: logging.Logger | None = None) -> None:
    """Install the N-7 redaction, at most once.

    Idempotent because `--workers` and any future re-import would otherwise stack
    identical filters, and because a test needs to be able to call it twice.
    """
    target = logger if logger is not None else logging.getLogger(_ACCESS_LOGGER)
    if any(isinstance(existing, RedactAccessLogQueryString) for existing in target.filters):
        return
    target.addFilter(RedactAccessLogQueryString())


def application() -> FastAPI:
    """The ASGI application, built from this process's environment.

    A `ConfigurationError` here is deliberately allowed to propagate: it names
    every problem it found, and a supervisor restarting a process that cannot be
    configured is the intended outcome, not a caught exception and a half-built
    portal.
    """
    install_access_log_redaction()
    return create_app(
        WebSettings.from_environment(os.environ, process=ProcessRole.WEB)
    )


__all__ = [
    "ACCESS_LOG_FORMAT",
    "REDACTED_QUERY",
    "RedactAccessLogQueryString",
    "UNRENDERABLE_RECORD",
    "application",
    "install_access_log_redaction",
]
