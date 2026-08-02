"""A read-only Sheets values reader for the import tools.

The importer only ever reads. The live bot's connector authenticates with a
credential scoped to `.../auth/spreadsheets` — full read *and write* — because
the bot needs it, so an import run today carries the authority to overwrite
every character in the Sheet it is only reading.

This module is the code half of narrowing that. It defines the port the import
tools depend on, and selects a credential scoped to
`.../auth/spreadsheets.readonly` when the deployment provides one. The live
bot's `connectors.sheets` is untouched and keeps its existing credential.

The other half is an operations step this repository cannot take: a second
Google service account, granted Viewer on the Sheet, with its JSON placed in
`SHEET_READONLY_SERVICE_ACCOUNT_JSON`. Until that exists the tools fall back to
the shared read/write credential and say so, because refusing to run would stop
the import for a reason the operator cannot fix from here. See
`docs/operations/sheet-import.md`.
"""
from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from adapters.safe_logging import log_expected_failure

logger = logging.getLogger(__name__)

#: The narrowest Google scope that can serve `spreadsheets.values.get`.
READ_ONLY_SCOPES = ("https://www.googleapis.com/auth/spreadsheets.readonly",)

#: Service-account JSON for the read-only principal. Optional; absent means the
#: shared read/write credential is used instead.
READ_ONLY_CREDENTIAL_VARIABLE = "SHEET_READONLY_SERVICE_ACCOUNT_JSON"

#: Which spreadsheet the read-only principal opens. Shared with the bot, since
#: it identifies the document rather than granting anything.
SHEET_ID_VARIABLE = "GUILD_SHEET_ID"

FALLBACK_NOTE = (
    f"{READ_ONLY_CREDENTIAL_VARIABLE} is not set, so this run uses the shared "
    "read/write Sheets credential. It still only reads, but it holds more "
    "authority than it needs; see docs/operations/sheet-import.md."
)

READ_ONLY_NOTE = "Using the read-only Sheets credential."

#: Operator-facing text for a credential that parses but cannot be used.
#:
#: Deliberately fixed, and deliberately without the underlying exception. Google's
#: own messages quote the offending value back — a malformed `private_key` field
#: produces `InvalidValue("<the value> could not be converted to unicode")` — so
#: rendering the cause is a path by which private-key material, a service-account
#: address or a Google response body reaches a terminal, a shell history or a CI
#: log. Neither the message nor a traceback is retained at any logging level;
#: `adapters.safe_logging` records the failure category and the exception's class
#: name and discards the rest.
CREDENTIAL_UNUSABLE_MESSAGE = (
    f"{READ_ONLY_CREDENTIAL_VARIABLE} is valid JSON but is not a usable "
    "service-account credential. Check that it is the complete, unedited key "
    "file for the read-only service account, minified onto one line. The reason "
    "is deliberately not reported anywhere, because it can quote credential "
    "material."
)

CREDENTIAL_NOT_AN_OBJECT_MESSAGE = (
    f"{READ_ONLY_CREDENTIAL_VARIABLE} must be a JSON object holding the "
    "service-account key fields."
)

#: One message for either half of the dependency. `google-auth` and
#: `google-api-python-client` are separate distributions, so an environment can
#: hold one without the other; the operator's action is the same for both, and
#: naming which half is missing would be the only difference.
GOOGLE_LIBRARIES_MISSING_MESSAGE = (
    f"{READ_ONLY_CREDENTIAL_VARIABLE} is set, but the Google API libraries are "
    "not installed in this environment. Install the project requirements, or "
    "unset the variable to fall back to the shared credential."
)


class SheetValuesReader(Protocol):
    """Read one A1 range. The only Sheets capability the importer needs."""

    def __call__(
        self, a1_range: str, value_render_option: str = "UNFORMATTED_VALUE"
    ) -> list[list[Any]]: ...


class SheetCredentialError(ValueError):
    """The configured read-only credential could not be used."""


@dataclass(frozen=True, slots=True)
class ReaderSelection:
    """Which credential a run reads with, and whether it is the narrow one."""

    read_values: SheetValuesReader
    read_only_credential: bool
    note: str


def build_values_reader(
    environ: Mapping[str, str],
    *,
    read_only_factory: Any = None,
    shared_factory: Any = None,
) -> ReaderSelection:
    """Select the narrowest Sheets reader this deployment can provide.

    The two factories are injected so the selection can be tested without a
    Google client or any credential at all.
    """
    read_only_factory = read_only_factory or _build_read_only_reader
    shared_factory = shared_factory or _shared_reader

    raw = (environ.get(READ_ONLY_CREDENTIAL_VARIABLE) or "").strip()
    if not raw:
        return ReaderSelection(
            read_values=shared_factory(),
            read_only_credential=False,
            note=FALLBACK_NOTE,
        )

    sheet_id = (environ.get(SHEET_ID_VARIABLE) or "").strip()
    if not sheet_id:
        raise SheetCredentialError(
            f"{READ_ONLY_CREDENTIAL_VARIABLE} is set but {SHEET_ID_VARIABLE} is "
            "not, so there is no spreadsheet to open."
        )
    return ReaderSelection(
        read_values=read_only_factory(raw, sheet_id),
        read_only_credential=True,
        note=READ_ONLY_NOTE,
    )


def _shared_reader() -> SheetValuesReader:
    """The bot's existing connector, imported only when it is actually used.

    Deferred so that `--help`, configuration errors and the whole test suite do
    not require Google credentials to be present.
    """
    from connectors.sheets import get_values

    return get_values


def _read_only_credentials(credential_json: str) -> Any:
    """Build a `spreadsheets.readonly` credential from configured JSON.

    Every way the configured value can be wrong is a misconfiguration the
    operator can fix, so each becomes `SheetCredentialError` and the import CLI
    reports it as such. Only the shapes Google's own construction raises are
    translated; an error from anywhere else still propagates, because a bug in
    this repository must not be reported to an operator as bad configuration.

    The *successful* path is exercised only in production: constructing a
    credential requires a real service-account key, which `.agents/AGENTS.md`
    forbids in tests. The failure paths below need no key and no network, and
    are covered.
    """
    try:
        from google.auth.exceptions import GoogleAuthError
        from google.oauth2 import service_account
    except ImportError as error:
        log_expected_failure(logger, "google_auth_library_missing", error)
        raise SheetCredentialError(GOOGLE_LIBRARIES_MISSING_MESSAGE) from error

    try:
        info = json.loads(credential_json)
    except ValueError as error:
        # No cause is rendered here either: a JSON error quotes the document.
        raise SheetCredentialError(
            f"{READ_ONLY_CREDENTIAL_VARIABLE} must be valid single-line JSON."
        ) from error

    if not isinstance(info, Mapping):
        raise SheetCredentialError(CREDENTIAL_NOT_AN_OBJECT_MESSAGE)

    try:
        return service_account.Credentials.from_service_account_info(
            dict(info), scopes=list(READ_ONLY_SCOPES)
        )
    except (GoogleAuthError, ValueError, TypeError) as error:
        # `MalformedError` and `InvalidValue` are ValueError subclasses; a
        # corrupt PEM body surfaces as `binascii.Error`, also a ValueError; and
        # a field of an unexpected JSON type can reach the crypto layer as a
        # TypeError. All three are "the configured JSON is wrong", not a defect.
        #
        # The exception carries fragments of the credential document, so only
        # the category and its class name are kept. `raise ... from error` keeps
        # the cause on the exception itself, where a debugger can see it and a
        # log cannot: the CLI never renders it either.
        log_expected_failure(logger, "read_only_credential_refused", error)
        raise SheetCredentialError(CREDENTIAL_UNUSABLE_MESSAGE) from error


def _build_read_only_reader(credential_json: str, sheet_id: str) -> SheetValuesReader:
    """A values reader authenticated with a `spreadsheets.readonly` credential."""
    credentials = _read_only_credentials(credential_json)

    # `google-auth` and `google-api-python-client` are separate distributions, so
    # the credential above can succeed in an environment where the discovery
    # client is absent — a partial install, or a requirements file applied only
    # in part. Without this the operator would get an `ImportError` traceback
    # instead of the documented dependency refusal and its exit code. Only the
    # import is guarded: catching more would put this repository's own import
    # failures behind a "check your configuration" message.
    try:
        from googleapiclient.discovery import build
    except ImportError as error:
        log_expected_failure(logger, "google_client_library_missing", error)
        raise SheetCredentialError(GOOGLE_LIBRARIES_MISSING_MESSAGE) from error

    service = build(  # pragma: no cover - needs a credential
        "sheets", "v4", credentials=credentials, cache_discovery=False
    )

    def read_values(  # pragma: no cover - needs a credential
        a1_range: str, value_render_option: str = "UNFORMATTED_VALUE"
    ) -> list[list[Any]]:
        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=sheet_id,
                range=a1_range,
                valueRenderOption=value_render_option,
            )
            .execute()
        )
        return result.get("values", [])

    return read_values
