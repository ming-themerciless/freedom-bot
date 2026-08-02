"""Diagnostic logging for expected failures that cannot leak what they carry.

An expected operational failure — a refused credential, an unreachable Sheet, a
database that is down — is reported to the operator as a fixed string and a
documented exit code. It is tempting to attach the exception to a `logger.debug`
call so that the detail is *available* to whoever turns debug logging on. That
is not safe, and the reason is the same one the fixed strings exist for:

- Google's credential errors quote the offending field value back, so a
  malformed `private_key` renders part of the key material into the message;
- SQLAlchemy's `DatabaseError.__str__` renders the failing **SQL statement**,
  its bound parameters and the driver's message, which for a connection failure
  contains the host, port, user and database name;
- a traceback renders local variables' repr in some handlers, every frame's file
  path, and the chained `__cause__` of all of the above.

Debug logging is still logging. It is written to a terminal, a journald unit, a
CI job log or a log collector, all of which outlive the run and none of which is
a place for credential material, a DSN or player data. `logging.lastResort`
being set to WARNING only means the message is invisible *by default*; any
operator who adds `--log-level=DEBUG`, or any library that calls
`logging.basicConfig(level=DEBUG)`, turns it into a written record.

So this module logs exactly two things: the fixed failure category chosen by the
caller, and the exception's class name. A class name is an identifier in
installed source code rather than data derived from a credential, a database or
a player, which makes it the one piece of an exception that is safe to keep. It
is also the piece that actually helps: it distinguishes a `MalformedError` from
an `InvalidValue` from a `binascii.Error` without quoting any of them.

The exception object itself is never interpolated, never serialized, and never
passed as `exc_info`. Anything more than the category and the class name belongs
in a debugger against synthetic input, not in a log.

This applies to *expected* failures only. A programming defect must still
propagate: mislabelling one as a configuration error sends an operator to check
their environment for a bug in this repository.
"""
from __future__ import annotations

import logging

#: The whole record. No exception message, no arguments, no traceback.
_TEMPLATE = "expected failure category=%s exception_type=%s"


def log_expected_failure(
    logger: logging.Logger,
    category: str,
    error: BaseException,
    *,
    level: int = logging.DEBUG,
) -> None:
    """Record that an expected failure of `category` occurred, and nothing else.

    `category` must be a fixed string chosen at the call site, never derived
    from the exception or from any input. Only `type(error).__name__` is taken
    from the exception.
    """
    logger.log(level, _TEMPLATE, category, type(error).__name__)
