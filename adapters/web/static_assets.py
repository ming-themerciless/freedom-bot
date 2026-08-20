"""M-01: the one static asset surface, and the rules that keep it boring.

**Added 2026-08-19 by the accepted D-03 correction (`C-P3.4-A`, item D-03-1).**
N-26 is `default-src 'self'; … script-src 'self'; style-src 'self'; img-src
'self' data:`, so P3.4's production CSS, its vendored HTMX and its emblem must be
served from this origin — and until this module existed there was no accepted
surface to serve them from. A frontend package inventing one would have put a URL
surface, its authorization state, its host and kill-switch behaviour and its cache
policy inside a template change, which is exactly the drift D-03 exists to stop.

## What this surface is

Public, unauthenticated, `GET` and `HEAD` only, same-origin, read-only, and
served out of exactly one repository-owned directory
(`adapters/web/composition.py`'s `STATIC_ROOT`). It has no session, no CSRF token
and no capability. It is *deliberately* reachable while the operator kill switch
is engaged, because the maintenance, login and safe-error pages are the pages a
person sees during an incident and an unstyled one is a worse incident.

## The three rules that are this module's own

Everything else is Starlette's `StaticFiles`, which already refuses a method
other than `GET`/`HEAD` with `405`, already resolves `..` out of the request path
and then rejects any resolved path outside the root with `os.path.realpath` plus
`os.path.commonpath`, and — with `html=False`, which is the default and is
restated explicitly below — answers a directory request with `404` rather than a
listing, and answers a missing file with `404` rather than a filesystem path.

1. **A URL grammar, checked before the filesystem is touched.** Each path segment
   must match `SEGMENT`: an alphanumeric first character, then alphanumerics,
   dots, hyphens and underscores. That refuses every dotfile — including the
   `.gitkeep` that makes the root exist in Git — refuses an empty segment, and
   refuses the decoded forms of an encoded traversal without relying on the
   normalisation below it. Refusal is `404`, not `400`: a grammar violation and a
   missing file are the same fact to a caller, and answering differently would
   make the grammar itself enumerable.

2. **A fingerprint-aware `Cache-Control`.** A filename whose stem ends in a dot
   and sixteen lowercase hex characters — `styles.9f2a1c4b8e7d6f50.css` — names
   its own content, so a year of immutable public caching is safe and a
   deployment invalidates by changing the URL. Anything else gets
   `public, max-age=0, must-revalidate`: still cacheable, never *served* stale.
   The conservative branch is the default, so a P3.4 asset that forgets to
   fingerprint is slow rather than wrong.

3. **`public`, and never `no-store`.** Route contract §7.2 puts `no-store` on
   every authenticated response, and `SecurityHeaders` applies it whenever a
   session cookie is present. A static asset is identical for every caller and
   carries nothing about the session that happened to fetch it, so that rule is
   scoped away from this prefix in `middleware.py` rather than fought here — see
   `SecurityHeaders.__init__`.

## What this module deliberately does not do

It does not strip cookies. Nothing in the stack sets one on this path — the
session, login-transaction and CSRF cookies are set by named handlers, and this
mount reaches none of them — and a stripping step would be a control that hides
the arrival of a defect instead of failing on it. `TC-STATIC-06` asserts the
property against a real request instead.
"""
from __future__ import annotations

import re

from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

#: The mount's public prefix. One place, because the route contract, the kill
#: switch, the `Cache-Control` exemption and the structural inventory all have to
#: name the same string.
STATIC_URL_PREFIX = "/static"

#: One path segment of the accepted URL grammar (route contract §1.2). The first
#: character may not be a dot, which is what keeps every dotfile in the root
#: unreachable.
SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

#: A fingerprinted filename: `<stem>.<16 lowercase hex>.<ext>`. Sixteen hex
#: characters is 64 bits of a content digest — enough that a collision is not a
#: practical concern and short enough to read in a diff.
FINGERPRINTED = re.compile(r"^.+\.[0-9a-f]{16}\.[A-Za-z0-9]+$")

#: One year, immutable. Safe only because the URL changes when the bytes do.
IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"

#: Cacheable, but revalidated every time. The default, deliberately.
REVALIDATE_CACHE_CONTROL = "public, max-age=0, must-revalidate"


def cache_control_for(request_path: str) -> str:
    """The accepted policy for one asset path, as a pure function.

    Split out from the response so the policy can be asserted over a table of
    names without building an application, which is what `TC-STATIC-05` does.
    """
    filename = request_path.rsplit("/", 1)[-1]
    if FINGERPRINTED.match(filename):
        return IMMUTABLE_CACHE_CONTROL
    return REVALIDATE_CACHE_CONTROL


def path_is_within_grammar(request_path: str) -> bool:
    """Every segment matches `SEGMENT`, and there is at least one segment."""
    segments = [segment for segment in request_path.split("/") if segment != ""]
    if not segments:
        return False
    return all(SEGMENT.match(segment) for segment in segments)


class StaticAssets(StaticFiles):
    """`StaticFiles`, plus the grammar check and the cache policy above."""

    def __init__(self, *, directory) -> None:
        # `html=False`: a directory request is a `404`, never a listing and never
        # an implicit `index.html`. `check_dir=True`: a missing root refuses at
        # construction, so a mis-deployed application does not start and answer
        # `404` to every asset instead.
        super().__init__(directory=directory, html=False, check_dir=True)

    async def get_response(self, path: str, scope: Scope) -> Response:
        # The method check is Starlette's and runs first, so a `POST` to a path
        # the grammar would refuse still answers `405` rather than `404` — the
        # method is the more specific refusal and the path is not confirmed by
        # it, because `405` is what *every* path under this mount answers to a
        # mutation.
        if scope["method"] not in ("GET", "HEAD"):
            raise HTTPException(status_code=405)
        # `path` has already been normalised by `get_path`, so `..` is gone; this
        # is the grammar, not a second traversal check. It runs before
        # `lookup_path` touches the filesystem.
        if not path_is_within_grammar(path.replace("\\", "/")):
            raise HTTPException(status_code=404)
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = cache_control_for(path)
        return response


__all__ = [
    "FINGERPRINTED",
    "IMMUTABLE_CACHE_CONTROL",
    "REVALIDATE_CACHE_CONTROL",
    "SEGMENT",
    "STATIC_URL_PREFIX",
    "StaticAssets",
    "cache_control_for",
    "path_is_within_grammar",
]
