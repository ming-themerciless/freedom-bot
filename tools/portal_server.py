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

**Two paths, and the second one emits nothing that came from the record.** The
pinned uvicorn 0.32.1 access line is redacted precisely, at the arguments that
carry the request target and the client, because that contract says which
argument is which. Every other record is **withheld whole** (N-29, below).
`RedactAccessLogQueryString` sets out both paths and why the alternatives —
enumerating containers, then redacting rendered text — could not be made to work.

## The client pseudonym (N-13, 2026-08-26; corrected 2026-08-27)

The client address is replaced by a keyed per-process pseudonym rather than
logged, because operational contract §5 prohibits a plaintext address in any log
line and `--proxy-headers` puts the *visitor's* address in this field.

The correction: the digest was taken over uvicorn's client field verbatim, and
that field is `"%s:%d" % client` — address **and ephemeral port**. Every
connection from one visitor therefore got its own pseudonym, so the correlation
the pseudonym exists to provide did not exist. `_client_address` now extracts and
validates the address first, in every form uvicorn 0.32.1 and a proxy in front of
it can produce, and only the address is hashed. A client value that is not an
address in any recognised form still never reaches the log: it is hashed whole
under a distinct prefix that tells a reader it cannot be correlated.

## The unfamiliar record fails closed as a whole (N-29, 2026-08-28)

Codex EX-11/EX-12 re-review. The fallback path rendered an unfamiliar record and
redacted the **text**, and the address half of that redaction was a regex with a
`\b` boundary on each end. An address adjacent to a word character was therefore
never a candidate:

    input:  peer=203.0.113.7suffix
    output: peer=203.0.113.7suffix

Operational contract §5 prohibits a plaintext IP address in **every** metric, log
line and dashboard. A best-effort control cannot satisfy a requirement with no
exceptions, and no list of patterns can be shown complete against arbitrary
rendered objects: the finding is a property of the approach, not of that pattern.

So the fallback no longer redacts. **A record outside the pinned contract is
replaced entirely** by `WITHHELD_RECORD`, which names one reason drawn from a
closed set of literals in this file, and `args`, `exc_info`, `exc_text` and
`stack_info` are cleared so no formatter can append the original afterwards.
Nothing caller-controlled survives, because nothing caller-controlled is emitted.

Two things narrowed on the retained path at the same time, both for the same
reason — a branch that claims to know which argument is which has to check:

- every pinned field is validated against what uvicorn 0.32.1 can produce
  (`_HTTP_METHOD`, `_HTTP_VERSION`, `_REQUEST_PATH`, the status range, the
  client-field length), and a record carrying anything else is withheld rather
  than trusted field by field; and
- the retained **request path** is scrubbed of address literals by a rule that is
  closed over its input (`_scrub_addresses`), because an HTTP client chooses the
  path and `GET /x203.0.113.7y` would otherwise disclose an address through the
  branch the remediation keeps.

## The retained method is caller-controlled too (N-31, 2026-08-28)

Codex re-review of the correction above. The unfamiliar-record path and the
scrubbed request path were both accepted; the **method** was not, and for the
same reason as everything else in this file's history. An HTTP method is an
RFC 9110 token, `_HTTP_METHOD` repeats that syntax faithfully, and the token
alphabet includes digits and `.`. So this passes every term of the pinned
contract and formats the address in clear text:

    ("198.51.100.9:1", "203.0.113.7", "/healthz", "1.1", 200)
    -> client-9abe9d54 - "203.0.113.7 /healthz HTTP/1.1" 200

Syntactic validity is not confidentiality. The branch was checking the first and
being read as if it guaranteed the second.

**The record is withheld rather than the method scrubbed.** Scrubbing was the
other option and it was rejected: `X203.0.113.7Y` would become `X<pseudonym>Y`,
which keeps caller-chosen characters around a removed span in a field that has no
operational meaning left once it carries an address. Withholding is the same
fail-closed shape the unfamiliar path already has, and it costs nothing an
operator reads — no standard verb, WebDAV method or vendor extension can contain
a dotted quad, and `999.999.999.999`, `203.0.113` and `DEAD.BEEF` are all kept,
because the rule decides on content rather than guessing at shape.

**Why the detection is complete over its input.** The method's accepted alphabet
contains **no `:`**, and every textual IPv6 literal contains at least two, so no
IPv6 literal is expressible in a method at all. That leaves the IPv4 dotted quad,
and `_scrub_addresses` already enumerates every start position and every length
for those rather than trusting one greedy scan — the property N-29 established
and the 32-character bound makes exhaustive. So detection reuses that same
accepted rule instead of introducing a second one: a method carries address
material exactly when the rule would change it (`_carries_address_material`).

**What it does not claim.** The rule finds IP *literals*, which is what §5's
prohibition of plaintext addresses means and what N-29's accepted path already
covers. A method spelling an address in some other encoding — the decimal form
`ipaddress` also accepts, say — is not a plaintext address and is not detected;
the boundary is stated rather than quietly widened.

**What it costs an operator.** An unfamiliar record keeps only the reason it was
unfamiliar. `uvicorn.access` emits the pinned access line and nothing else, so in
practice nothing an operator reads day to day changes; a withheld line is itself
the signal that uvicorn's contract moved, and the reason says which term of it
stopped holding. Losing detail on an unrecognised access-log format is preferable
to disclosing a credential, an address or arbitrary exception text.
"""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import re
import secrets
import os

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
#:
#: **What "correlation" means here, precisely (corrected 2026-08-27).** One
#: *address* reaches one pseudonym for this process's lifetime. It did not, until
#: this correction: the digest was taken over uvicorn's whole client field, which
#: is `address:ephemeral-port`, so successive connections from one visitor were
#: pseudonymised differently and nothing could be correlated with anything. See
#: `_client_address`, which is where the port is now removed.
_CLIENT_PSEUDONYM_KEY = secrets.token_bytes(16)

#: Every character an IP literal can be spelled with, and nothing else: the hex
#: digits, the IPv6 separator and the IPv4 separator. A maximal run of these is
#: therefore a **superset** of any address in the text, which is the property the
#: N-29 correction rests on — see `_scrub_addresses`.
#:
#: **Replaced the `\b`-anchored candidate pattern on 2026-08-28 (N-29).** The
#: old pattern required a word boundary at both ends, so an address adjacent to a
#: word character was never a candidate at all: `peer=203.0.113.7suffix` came out
#: unchanged. A boundary condition is exactly the kind of best-effort clause an
#: absolute contract cannot be built on.
_ADDRESS_RUN = re.compile(r"[0-9A-Fa-f.:]{2,}")

#: The shape of an IPv4 literal, deliberately **unanchored**. Candidates are
#: enumerated per start position and per length rather than by a single scan,
#: because a greedy match can succeed on an invalid quad while a valid address
#: begins one character later — `999.999.999.203.0.113.7` and `203.0.113.789`
#: both hid a real address from the earlier single-pass reading.
_IPV4_LITERAL = re.compile(r"[0-9]{1,3}(?:\.[0-9]{1,3}){3}")
#: `255.255.255.255` is the longest IPv4 literal; `1.1.1.1` the shortest.
_IPV4_MAX_LENGTH = 15
_IPV4_MIN_LENGTH = 7

#: An IPv6 literal always contains at least two colons — that is what the `:`
#: separator means for a minimum of three fields, and a compressed `::` is two on
#: its own. A run carrying fewer cannot contain one, and a run carrying enough is
#: removed **whole** rather than searched, because searching an arbitrary run for
#: an embedded IPv6 literal is the enumeration problem N-29 rejects.
_IPV6_MINIMUM_COLONS = 2

#: What replaces a run that may carry an IPv6 literal but does not resolve to one
#: address. Over-redaction, deliberately: the alternative is deciding which
#: characters of an ambiguous run were the address.
REDACTED_ADDRESS = "<address-redacted>"


#: A value this filter has already pseudonymised, in either of its two forms.
#: Recognised so that filtering a record twice is a no-op — uvicorn's client
#: field is `host:port` or the empty string and can never take this shape, so
#: nothing real is mistaken for an already-redacted value.
_PSEUDONYM = re.compile(r"^client-(?:unknown-)?[0-9a-f]{8}$")

#: The port half of uvicorn's client field. `[0-9]` rather than `\d`, and
#: `fullmatch` rather than `str.isdigit()`, because both of those accept
#: non-ASCII digits: a "port" that `int()` reads differently from the socket
#: that produced it is not one this function should claim to understand, and
#: refusing it falls through to the fail-safe path rather than to a guess.
_PORT = re.compile(r"[0-9]{1,5}")
_MAX_PORT = 65535

#: The pseudonym for a client whose address was recognised. Correlates across
#: connections, because the address is what is hashed.
_CLIENT_PREFIX = "client-"
#: The pseudonym for a client value this module could not read as an address.
#: Still a keyed digest — an unrecognised value may *be* an address in a form
#: not covered here, so its characters must never reach the log — but a distinct
#: prefix, because it carries **no** correlation guarantee: it is a digest of
#: whatever arrived, ephemeral port and all. A reader who sees this prefix is
#: being told that this line cannot be correlated with any other.
_UNKNOWN_CLIENT_PREFIX = "client-unknown-"


def _digest(material: str) -> str:
    """The keyed 4-byte digest every pseudonym in this module is built from."""
    return hashlib.blake2s(
        material.encode("utf-8", "replace"),
        key=_CLIENT_PSEUDONYM_KEY,
        digest_size=4,
    ).hexdigest()


def _parse_address(text: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """One host — bracketed or bare — as an address, or `None` if it is not one."""
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    try:
        return ipaddress.ip_address(text)
    except ValueError:
        return None


def _client_address(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """The address in a client field, with any ephemeral port removed.

    **The port is the whole point (2026-08-27).** uvicorn builds this field as
    `"%s:%d" % client` (`uvicorn/protocols/utils.py::get_client_addr`, 0.32.1),
    so every connection from one visitor carries a *different* ephemeral port.
    Hashing the field as it arrives therefore produced a different pseudonym per
    connection, and the correlation property the pseudonym exists for did not
    hold at all. The port is dropped here, before anything is hashed.

    Recognised forms, all of which reduce to the same address:

    - `203.0.113.7:54321` — uvicorn's IPv4 form;
    - `2001:db8::1:54321` — uvicorn's IPv6 form, which is **not** bracketed
      because `"%s:%d"` does not bracket;
    - `[2001:db8::1]:54321` — the bracketed form a proxy or a future uvicorn
      may use;
    - `203.0.113.7`, `2001:db8::1`, `[2001:db8::1]` — a bare host, which is what
      `_scrub_addresses` and a `--uds` deployment can produce.

    **Why the port is split off before the whole value is tried as an address.**
    uvicorn's unbracketed IPv6 form is genuinely ambiguous: `::1:5432` is both
    `::1` port 5432 and a well-formed IPv6 address in its own right. On *this*
    field the first reading is the true one, and preferring it is what makes the
    IPv6 correlation property hold for the four-digit ports where the ambiguity
    exists at all. `_scrub_addresses`, whose input is free text rather than this
    field, resolves the same ambiguity the other way round and says why.
    """
    candidate = value.strip()
    if not candidate:
        return None
    host, separator, port = candidate.rpartition(":")
    if separator and _PORT.fullmatch(port) and int(port) <= _MAX_PORT:
        address = _parse_address(host)
        if address is not None:
            return address
    return _parse_address(candidate)


def _pseudonymise_address(
    address: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> str:
    """The pseudonym for one parsed address.

    Hashed from `str(address)`, which `ipaddress` guarantees is the canonical
    compressed form, so `::1` and `0:0:0:0:0:0:0:1` — and the same address read
    out of an access line and out of a traceback — reach one pseudonym. The
    domain prefix keeps this digest's input space disjoint from the fail-safe
    one below.
    """
    return f"{_CLIENT_PREFIX}{_digest(f'address:{address}')}"


def _pseudonymise_client(value: object) -> str:
    """A stable per-process pseudonym for one client address.

    Stable **per address**: two connections from one visitor pseudonymise
    identically for as long as this process lives, because the ephemeral port is
    removed before hashing (`_client_address`). A value this module cannot read
    as an address is hashed whole under `_UNKNOWN_CLIENT_PREFIX` — safe, since
    no character of it reaches the log, but explicitly not correlatable.
    """
    text = str(value)
    if _PSEUDONYM.match(text):
        return text
    address = _client_address(text)
    if address is None:
        return f"{_UNKNOWN_CLIENT_PREFIX}{_digest(f'unparsed:{text}')}"
    return _pseudonymise_address(address)


def _scrub_addresses(text: str) -> str:
    """Replace every IP literal in `text` with a pseudonym or a marker.

    **Rewritten 2026-08-28 for N-29, and no longer best-effort.** The previous
    version matched `\b`-anchored candidates, so an address adjacent to a word
    character was never isolated: `peer=203.0.113.7suffix` was returned exactly
    as it arrived. Operational contract §5 prohibits a plaintext address in
    *every* log line, and a control with a documented gap cannot satisfy a
    requirement with none.

    **The rule, and why it is closed over its input.** Every IP literal — IPv4,
    IPv6, compressed, IPv4-mapped — is spelled entirely from `_ADDRESS_CHARACTERS`
    (hex digits, `:` and `.`). So every literal in `text` lies inside exactly one
    *maximal run* of those characters, whatever surrounds the run. This function
    replaces the contents of every such run, in one of two ways:

    - a run with two or more colons **may** carry an IPv6 literal, and finding
      which substring of an arbitrary run is that literal is the enumeration
      problem N-29 rejects, so the **whole run** goes — resolved to a pseudonym
      when the run itself reads as one address, and to `REDACTED_ADDRESS`
      otherwise;
    - a run with fewer colons cannot carry an IPv6 literal, so only IPv4 remains,
      and `_scrub_ipv4_literals` enumerates every start position and length
      rather than trusting one greedy scan.

    Neither branch depends on what precedes or follows the run, which is the
    property the boundary-anchored version could not have.

    **Its one caller is the pinned path's request path** (N-29). The unfamiliar
    path no longer scrubs anything: it withholds the record whole, because no
    text rule can be trusted against arbitrary rendered objects. A request path
    is caller-controlled but *bounded* — validated against `_REQUEST_PATH` before
    it reaches here — so a rule closed over its input is a rule that holds.
    """
    return _ADDRESS_RUN.sub(_scrub_address_run, text)


def _scrub_address_run(match: re.Match[str]) -> str:
    """One maximal run of address characters, resolved or removed."""
    run = match.group(0)
    if run.count(":") < _IPV6_MINIMUM_COLONS:
        return _scrub_ipv4_literals(run)
    address = _parse_address(run)
    if address is None:
        address = _client_address(run)
    if address is None:
        return REDACTED_ADDRESS
    return _pseudonymise_address(address)


def _scrub_ipv4_literals(run: str) -> str:
    """Every IPv4 literal in `run`, replaced, wherever it starts and ends.

    **Enumerated rather than scanned (N-29).** A single greedy pass over
    `999.999.999.203.0.113.7` matches the invalid leading quad, rejects it, and
    resumes *after* it — leaving the real address behind. A single greedy pass
    over `203.0.113.789` matches an invalid four-digit final octet and leaves two
    valid addresses inside it. Both are the same defect: the first reading that
    fails is treated as the only reading.

    So each position is tried, longest form first, and a match is taken only when
    `ipaddress` accepts it. Replacing the leftmost-longest literal and continuing
    past it is what makes the pass complete: any other literal either lies inside
    the span just removed — and so no longer exists as contiguous text — or
    begins after it, where the scan continues.

    The cost is bounded by construction: at most nine lengths are tried per
    position, and the only caller passes a request path `_REQUEST_PATH` has
    already bounded.
    """
    scrubbed: list[str] = []
    index = 0
    while index < len(run):
        replacement, length = _ipv4_literal_at(run, index)
        if replacement is None:
            scrubbed.append(run[index])
            index += 1
            continue
        scrubbed.append(replacement)
        index += length
    return "".join(scrubbed)


def _ipv4_literal_at(run: str, index: int) -> tuple[str | None, int]:
    """The pseudonym for the longest IPv4 literal starting at `index`, if any."""
    for length in range(
        min(_IPV4_MAX_LENGTH, len(run) - index), _IPV4_MIN_LENGTH - 1, -1
    ):
        candidate = run[index : index + length]
        if not _IPV4_LITERAL.fullmatch(candidate):
            continue
        address = _parse_address(candidate)
        if address is not None:
            return _pseudonymise_address(address), length
    return None, 0


def _carries_address_material(text: str) -> bool:
    """Whether `text` contains an IP literal, decided by the rule that removes one.

    **Added 2026-08-28 for N-31.** Deliberately not a second rule. `_scrub_addresses`
    is the accepted, closed-over-its-input rule for finding address literals in a
    bounded string; asking whether it *would* change `text` asks the same question
    it already answers, so the detector cannot drift from the scrubber and there
    is only one rule for a reviewer to be convinced by.

    The equivalence "changed ⟺ carried a literal" holds because neither
    replacement can reproduce its input: a pseudonym and `REDACTED_ADDRESS` both
    contain characters `_ADDRESS_RUN` does not match, so a run that was replaced
    is always different from the run that was there.

    **Its one caller is the method**, whose alphabet contains no `:`. Every
    textual IPv6 literal contains at least two, so the IPv6 branch of the rule is
    unreachable from here and only the enumerated IPv4 branch runs — which is why
    the completeness argument for the method is the shorter of the two.
    """
    return _scrub_addresses(text) != text


#: The pinned record's bounds, one per field uvicorn 0.32.1 supplies.
#:
#: **Added 2026-08-28 for N-29.** The retained branch's justification is that it
#: knows which argument is which. "Knowing" has to mean something checkable, so
#: each field is checked against what uvicorn can actually produce, and a record
#: carrying anything else leaves the branch rather than being trusted field by
#: field. Method and request target are caller-controlled — an HTTP client
#: chooses both — so they are the two that matter.
#:
#: The method is an RFC 9110 token; uvicorn's own parsers reject anything else,
#: and this repeats the constraint rather than inheriting it.
_HTTP_METHOD = re.compile(r"[A-Za-z0-9!#$%&'*+.^_`|~-]{1,32}")
#: `scope["http_version"]` is `"1.0"`, `"1.1"` or `"2"` in the pinned release.
_HTTP_VERSION = re.compile(r"[0-9](?:\.[0-9])?")
#: The path half of the request target, after the query string is dropped.
#: uvicorn passes it through `urllib.parse.quote`, whose output is a subset of
#: printable ASCII; this bounds the length as well, because a formatter has no
#: bound of its own and an access log is not the place to discover one.
_REQUEST_PATH = re.compile(r"[!-~]{0,2048}")
#: uvicorn builds the client field as `"%s:%d"`, so 45 characters of IPv6 plus a
#: bracket pair, a colon and five digits is its ceiling. The value is hashed
#: whatever it is, so this bound buys tidiness rather than confidentiality.
_MAX_CLIENT_FIELD = 128
_MIN_STATUS = 100
_MAX_STATUS = 599

#: What an unfamiliar record becomes. Repository-owned text with exactly one
#: substitution, filled from the closed set of reasons below — never from the
#: record, its arguments, its exception or its stack.
WITHHELD_RECORD = "<uvicorn.access record withheld: {reason}>"

#: The reasons, which are the *only* thing a withheld line carries beyond the
#: marker. Each names a term of the pinned contract that did not hold. They are
#: literals in this repository: none is derived from a value, a type name, a
#: length or a count, so none of them is a channel for caller-controlled material.
WITHHELD_UNPINNED_FORMAT = "unpinned-format-string"
WITHHELD_UNPINNED_ARGUMENT_SHAPE = "unpinned-argument-shape"
WITHHELD_UNPINNED_ARGUMENT_TYPE = "unpinned-argument-type"
WITHHELD_UNPINNED_ARGUMENT_VALUE = "unpinned-argument-value"
WITHHELD_UNPINNED_REQUEST_TARGET = "unpinned-request-target"
WITHHELD_ATTACHED_DIAGNOSTIC = "attached-exception-or-stack"
#: N-31, 2026-08-28. The one reason that is not a term of *uvicorn's* contract:
#: the record is exactly what uvicorn 0.32.1 emits, and it is withheld because
#: operational contract §5 forbids what the caller put in the method. Like the
#: six above it names the term that failed and nothing about the value.
WITHHELD_ADDRESS_BEARING_METHOD = "address-bearing-method"

#: Every line this filter can substitute for a record. Recognised on the way in
#: so that filtering twice is a no-op even when the *first* pass withheld the
#: record: a second pass would otherwise reclassify the marker it just wrote as
#: an unpinned format string, and two applications would disagree.
WITHHELD_RECORDS = frozenset(
    WITHHELD_RECORD.format(reason=reason)
    for reason in (
        WITHHELD_UNPINNED_FORMAT,
        WITHHELD_UNPINNED_ARGUMENT_SHAPE,
        WITHHELD_UNPINNED_ARGUMENT_TYPE,
        WITHHELD_UNPINNED_ARGUMENT_VALUE,
        WITHHELD_UNPINNED_REQUEST_TARGET,
        WITHHELD_ATTACHED_DIAGNOSTIC,
        WITHHELD_ADDRESS_BEARING_METHOD,
    )
)


def _redact_query(path_and_query: str) -> tuple[str, bool]:
    """The request target split at the first `?`, with the query dropped.

    One rule, so the guarantee it underwrites is provable by reading it: **no
    character following the first `?` survives.** The boolean says whether there
    was a query string at all, which is the distinction `REDACTED_QUERY` exists
    to preserve.
    """
    path, separator, _ = path_and_query.partition("?")
    return path, bool(separator)


class RedactAccessLogQueryString(logging.Filter):
    """Bound what `uvicorn.access` may emit (N-7, N-13, N-29).

    Returns True always: this filter redacts, it never drops a line. Losing the
    access record entirely would trade one operational blindness for another.

    ## The accepted input contract, and what happens outside it

    **Rewritten 2026-08-28 after Codex re-review finding N-29.** Three earlier
    versions were wrong in the same way, each less obviously than the last. The
    first recognised uvicorn 0.32.1's five-tuple and passed every other shape
    through untouched. The second scrubbed tuples and mapping *values* and
    claimed that made unfamiliar records fail closed — but it inspected
    containers by type, so `record.args = ["/cb?code=…"]` walked straight
    through. The third rendered the unfamiliar record to text and redacted the
    text, which fixed the container problem and left a subtler one: the redaction
    was a **list of regex patterns**, and a pattern has edges. `_scrub_addresses`
    required a word boundary, so `peer=203.0.113.7suffix` survived intact,
    against a contract that prohibits a plaintext address in every log line.

    The lesson each version taught again is the same one: **no rule over
    arbitrary rendered text can be shown to be complete.** So the third version's
    successor does not have one. There are two paths, and the second emits
    nothing that came from the record:

    1. **The pinned contract** — `record.msg` is exactly `ACCESS_LOG_FORMAT`, the
       arguments are a five-tuple, each argument is of the type that contract
       gives it and within the bound this module states for it, and the record
       carries no exception and no stack. This is uvicorn 0.32.1's access line in
       both `httptools_impl` and `h11_impl`, **and its method carries no address
       literal** (N-31). The client becomes its keyed pseudonym (N-13), the query
       string is dropped (N-7), the request path is scrubbed of address literals
       by a rule closed over its input, and method, protocol and status reach the
       log unchanged. Ordinary operational use of the access log is unaffected —
       every real access line takes this path, because no verb, WebDAV method or
       vendor extension contains a dotted quad.

       The gate is the *format string*, not the shape: a future uvicorn
       prepending a field would still present a tuple with a string at index 2,
       and matching on shape alone would redact the wrong argument while the
       credential sailed past in the next one. That is not hypothetical — it was
       caught by a test written for Codex finding I-1.

       Nothing on this path renders caller-supplied data. Every retained field is
       already a `str` or an `int` by the time it is used, so no `__str__` runs,
       and "an argument whose rendering raises" is not a case this path has to
       survive — it is a case this path cannot reach.

    2. **Everything else is withheld whole**, including a record uvicorn really
       did emit whose method carries an address. The record is replaced by
       `WITHHELD_RECORD` naming one reason from a closed set of repository-owned
       literals, and `args`, `exc_info`, `exc_text` and `stack_info` are cleared
       so that no formatter can append the original afterwards. Nothing is
       rendered, so nothing rendered can escape a pattern; nothing partial is
       kept, so there is no fragment to argue about.

    **What that costs, stated plainly.** An unfamiliar record loses everything
    except the reason it was unfamiliar. On this logger the cost is close to
    nil — `uvicorn.access` emits the pinned line and nothing else, so a withheld
    record is itself the signal that something changed, and the reason names
    which term stopped holding. The alternative cost is a credential or an
    address, which is why the trade is not close. It is also why this filter is
    installed on `uvicorn.access` and on no other logger: the argument above is
    about *this* logger's content, and it does not transfer.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if self._already_withheld(record):
            return True
        reason = self._outside_the_pinned_contract(record)
        if reason is None:
            self._redact_pinned_access_line(record)
        else:
            self._withhold(record, reason)
        return True

    @staticmethod
    def _already_withheld(record: logging.LogRecord) -> bool:
        """A record this filter has already replaced is left exactly as it is.

        `--workers`, a re-import and a doubly-installed filter all apply this
        twice. Without this the second pass would classify the marker written by
        the first as an unpinned format string, so the reason recorded would
        depend on how many times the record was filtered.
        """
        return (
            isinstance(record.msg, str)
            and record.msg in WITHHELD_RECORDS
            and record.args is None
            and record.exc_info is None
            and record.exc_text is None
            and record.stack_info is None
        )

    @staticmethod
    def _outside_the_pinned_contract(record: logging.LogRecord) -> str | None:
        """The term that does not hold, or `None` if the record may be redacted.

        Every check but the last is a term of *uvicorn's* contract, and their
        order is the order a reader needs: what is attached, then the format
        string, then the shape of the arguments, then their types, then their
        values, then the request target.

        The last is the one term operational contract §5 adds (N-31): a record
        that is exactly what uvicorn emits can still carry an address the caller
        chose, and a syntax check is not a confidentiality check.
        """
        if (
            record.exc_info is not None
            or record.exc_text is not None
            or record.stack_info is not None
        ):
            # A uvicorn access record carries none of these. Redacting them as
            # text was the previous design; a traceback echoes its own raising
            # source line, so that was a text rule over arbitrary content again.
            return WITHHELD_ATTACHED_DIAGNOSTIC
        if not isinstance(record.msg, str) or record.msg != ACCESS_LOG_FORMAT:
            return WITHHELD_UNPINNED_FORMAT
        arguments = record.args
        if not isinstance(arguments, tuple) or len(arguments) != _ACCESS_LOG_ARITY:
            return WITHHELD_UNPINNED_ARGUMENT_SHAPE
        client, method, target, version, status = arguments
        if not all(isinstance(field, str) for field in (client, method, target, version)):
            return WITHHELD_UNPINNED_ARGUMENT_TYPE
        # `bool` is an `int`, and a status of `True` is not a status.
        if isinstance(status, bool) or not isinstance(status, int):
            return WITHHELD_UNPINNED_ARGUMENT_TYPE
        if (
            len(client) > _MAX_CLIENT_FIELD
            or not _HTTP_METHOD.fullmatch(method)
            or not _HTTP_VERSION.fullmatch(version)
            or not _MIN_STATUS <= status <= _MAX_STATUS
        ):
            return WITHHELD_UNPINNED_ARGUMENT_VALUE
        if not _REQUEST_PATH.fullmatch(_redact_query(target)[0]):
            return WITHHELD_UNPINNED_REQUEST_TARGET
        # N-31, and the only term below that is not uvicorn's. Everything above
        # asks whether this is the record uvicorn 0.32.1 emits; this asks whether
        # what the caller put in it may be logged. The method is an RFC 9110
        # token and the token alphabet includes digits and `.`, so a caller can
        # send `203.0.113.7` as a method and have it pass every check above.
        #
        # Withheld rather than scrubbed: scrubbing would keep the caller's
        # characters around the removed span, and a method carrying an address is
        # not a method whose remains are worth preserving. The request path is
        # scrubbed instead, because a path with an address removed is still a
        # route an operator can read.
        if _carries_address_material(method):
            return WITHHELD_ADDRESS_BEARING_METHOD
        return None

    @staticmethod
    def _redact_pinned_access_line(record: logging.LogRecord) -> None:
        """Redact the client and the request target of uvicorn's access line.

        Called only after `_outside_the_pinned_contract` returned `None`, so
        every field below is of the pinned type, within the pinned bound, and —
        for the method — free of address literals (N-31). The method is therefore
        retained here rather than redacted: the record would not have reached
        this branch if it were not safe to log.
        """
        client, method, target, version, status = record.args
        path, had_query = _redact_query(target)
        # N-13: the client address, every time — not only when it parses as an
        # IP literal. `--proxy-headers` puts the true visitor address here, and
        # the operational contract §5 prohibits a plaintext address in any log
        # line, whatever its form.
        #
        # N-29: and the *path* too. An HTTP client chooses the path, so
        # `GET /x203.0.113.7y` would otherwise put a plaintext address in the
        # access log through this branch — the same finding, on the branch the
        # remediation keeps.
        redacted_path = _scrub_addresses(path)
        if had_query:
            redacted_path += REDACTED_QUERY
        record.args = (
            _pseudonymise_client(client),
            method,
            redacted_path,
            version,
            status,
        )

    @staticmethod
    def _withhold(record: logging.LogRecord, reason: str) -> None:
        """Replace an unfamiliar record with repository-owned text.

        Everything a formatter can emit is cleared, not only the message:
        `args` so nothing is re-expanded, `exc_info` and `exc_text` so no
        traceback is appended, `stack_info` so no stack is. The record survives —
        this filter never drops a line — and what survives of it is the reason.
        """
        record.msg = WITHHELD_RECORD.format(reason=reason)
        record.args = None
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None


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
    "REDACTED_ADDRESS",
    "REDACTED_QUERY",
    "RedactAccessLogQueryString",
    "WITHHELD_ADDRESS_BEARING_METHOD",
    "WITHHELD_ATTACHED_DIAGNOSTIC",
    "WITHHELD_RECORD",
    "WITHHELD_RECORDS",
    "WITHHELD_UNPINNED_ARGUMENT_SHAPE",
    "WITHHELD_UNPINNED_ARGUMENT_TYPE",
    "WITHHELD_UNPINNED_ARGUMENT_VALUE",
    "WITHHELD_UNPINNED_FORMAT",
    "WITHHELD_UNPINNED_REQUEST_TARGET",
    "application",
    "install_access_log_redaction",
]
