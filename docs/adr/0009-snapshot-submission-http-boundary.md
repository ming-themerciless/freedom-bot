# ADR 0009 — The snapshot submission HTTP boundary

Status: **Accepted** — approved by Peter Duscha, Acceptance Authority, on
2026-08-04. Proposed the same day by the implementing agent for the Phase 2 I-03
package.

**What this acceptance does and does not cover.** It accepts the *architectural
decision*: the submission endpoint is a stdlib WSGI application, and FastAPI is
not introduced by this package. It does **not** accept the Phase 2 I-03
implementation, which still requires the independent implementation review and
the separate security-focused review recorded in
[`../review/phase-2-i-03-submission.md`](../review/phase-2-i-03-submission.md)
§11. It authorizes no further HTTP surface: a second route is a new decision.

Date: 2026-08-04

Supersedes nothing. Narrows the scope of one decision in
[ADR 0002](0002-web-application-stack.md) for one endpoint, without changing it.

## Clarification, 2026-08-04 — the preflight is part of this route, not a second one

Independent review found (B-1, S-I-1) that the supported browser workflow could
not pass a CORS preflight, because the adapter answered `405` to `OPTIONS` and
emitted no permission. Remediating that adds `OPTIONS` handling and an
allowlisted-origin policy (`adapters/http/cors.py`) to
`POST /api/v1/foundry/snapshots`.

**This is not the "second route" the acceptance above reserves as a new
decision.** A CORS preflight is the same route's own contract: the browser is
required to send it before the POST this ADR already authorizes, and answering
it adds no resource, no capability and no caller. The route count is unchanged
at two, the preview route remains inert, and nothing here authorizes a third.

The stdlib WSGI decision is preserved and reinforced: the preflight is about
sixty lines of policy plus a bounded response, it has no dependency, and every
branch is covered in `tests/test_http_submission.py`, including one exercise
over a real socket. Recorded as a clarification under plan §0.2 rather than a
baseline change, because it alters no scope, authority, architecture or
production topology. It does add one required configuration variable,
`FREEDOM_SNAPSHOT_ALLOWED_ORIGINS`, which is documented in
`docs/operations/foundry-snapshot-submission.md` §5.4 and defaults to permitting
no browser origin at all.

## Context

The Foundry module must submit a snapshot to this application over HTTPS
(maintainer decision, Phase 2 I-03: "direct HTTPS submission is the primary
workflow… manual server file placement is not the supported user workflow").
That needs an HTTP surface.

[ADR 0002](0002-web-application-stack.md) records **FastAPI** as the HTTP
framework for the Freedom Blades web application, with Jinja2, vendored HTMX,
server-side sessions and Caddy in front. That decision stands and is not
reopened here.

But three things are true right now:

1. **The web stack is not scaffolded.** `fastapi`, `uvicorn`, `starlette`,
   `httpx` and `jinja2` are absent from `requirements.txt` and from the
   deployment virtualenv. There is no `web/` package, no `freedom-web` unit, no
   session store and no OAuth client.
2. **Phase 3 owns that scaffolding**, and its review gate is *authentication,
   authorization and web security* (plan §12). Standing FastAPI up now would be
   framework scaffolding ahead of the gate that reviews it.
3. **This endpoint needs almost none of what FastAPI provides.** It has one
   production route. It authenticates a bearer service credential rather than a
   browser session, so it uses no cookie, no CSRF token, no OAuth flow, no
   template and no static asset. Its body is one JSON document that must **not**
   be parsed into a model before hashing — the identity is the SHA-256 of the
   exact received bytes, so framework request-body validation is something to
   route around rather than a benefit.

`.agents/AGENTS.md` is explicit about the shape of the mistake available here:
*"Do not introduce a framework for a small utility"* and *"Do not choose a web
or frontend framework as a drive-by change."*

## Decision

**Implement the submission endpoint as a stdlib WSGI application**
(`adapters/http/wsgi.py`), and do not add FastAPI, uvicorn or any HTTP
dependency in this package.

WSGI is chosen specifically because it is not a competing framework decision:

- it is a **stdlib-supported interface** (PEP 3333, `wsgiref`), so the
  dependency count of this package is zero;
- it is **testable without a socket**, through `wsgiref.validate`, which proves
  the responses are well-formed WSGI rather than merely accepted by one client;
- it **mounts unchanged** inside the Phase 3 FastAPI application via
  `WSGIMiddleware`, or behind gunicorn, or behind any other WSGI server — so
  this is not a fork in the road that has to be undone;
- the small amount of transport code it requires — method, content type,
  bounded read, status, JSON body — is code this package wants to own anyway,
  because the size bound has to hold *before* the body is buffered and the
  checksum has to be taken over the exact bytes received.

`tools/snapshot_api.py` serves it with `wsgiref.simple_server` for the
maintainer-supervised rehearsal only. That is explicitly not the production
server: it is single-threaded, has no request timeout of its own, and binds
loopback only.

## Consequences

**Positive.**

- No dependency, no framework decision taken outside its gate, and no partial
  Phase 3 portal created as a side effect.
- The endpoint is fully implemented and fully testable today, so the Foundry
  module's workflow can be exercised end to end.
- The checksum is computed over exactly the bytes that arrived, because nothing
  deserialises the body first.

**Negative.**

- Request parsing is hand-written. It is about eighty lines, and every branch is
  covered in `tests/test_http_submission.py`, but it is eighty lines that
  FastAPI would have supplied.
- There is no generated OpenAPI document for this route. The wire contract is
  documented in `docs/operations/foundry-snapshot-submission.md` instead.
- **Production serving is not delivered by this package.** The WSGI application
  exists; the process that runs it in production does not. Phase 3 supplies
  `freedom-web`, and until then the endpoint runs only under the rehearsal
  server.

**Neutral, but worth stating.** If Phase 3 prefers to reimplement this route as
a native FastAPI endpoint rather than mount it, that is a small and reviewable
change: the application service beneath it takes bytes, a principal and a
request key, and knows nothing about HTTP at all.

## Alternatives considered

**Add FastAPI and uvicorn now.** Rejected. It commits the deployment to a
framework and an ASGI server before the phase whose gate reviews that choice,
adds four runtime dependencies for one route, and would produce a partial web
application that a later phase has to reconcile with the real one. ADR 0002 is
not weakened by this: it still names FastAPI for the web application, and this
endpoint is not the web application.

**A CLI-only workflow: the operator places a file and runs `bootstrap_manager`.**
Rejected by the maintainer decision for this package — that is exactly the SSH
and server-path workflow being replaced. The existing CLI remains, unchanged, as
a fallback and diagnostic path.

**A separate microservice.** Rejected. It would need its own deployment,
credentials and database access, and would duplicate the composition root for
one endpoint that shares every application service with the rest of the
platform.

**Have Foundry write to a shared directory.** Rejected. It requires filesystem
coupling between the Foundry account and the platform account, gives no
authentication, no idempotency and no receipt, and puts a caller-controlled
filename on the platform's filesystem — the traversal problem
`safe_artifact_name` exists to refuse.
