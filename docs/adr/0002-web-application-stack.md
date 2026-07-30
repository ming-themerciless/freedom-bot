# ADR 0002 — Web application stack

Status: **Accepted** — approved by the maintainer 2026-07-30. That satisfies the
Phase 0 acceptance criterion *"maintainer approves architecture ADRs"* (plan §12).
The independent Codex review required by plan §16.4 approved Phase 0 on
2026-07-30, and the maintainer accepted the milestone. This ADR is the contract
Phase 1 will be reviewed against.

Date: 2026-07-29

## Context

Plan §5.2 recommends a baseline but requires the final choice to be recorded as
an ADR before framework scaffolding. Plan §12 Phase 3 then needs OAuth login,
role verification, sessions, CSRF and security headers.

Observed constraints:

- Deployment is Python 3.12.3 (`venv`, `Python 3.12.3`), systemd-managed on a
  single host (`infra/systemd/freedom-bot.service.tmpl`).
- The Discord bot is Pycord and must keep running as its own gateway process.
- **Caddy is already deployed** as the reverse proxy for three Foundry instances,
  terminating TLS with Cloudflare origin certificates
  (see [operations/topology.md](../operations/topology.md)).
- The product surface is forms, tables, approval queues, diffs and reports
  (plan §5.2) — not a real-time interactive application.
- There is no frontend build tooling in the repository and no maintainer
  identified as a frontend specialist.

## Decision

Adopt the plan §5.2 baseline, with Caddy fixed rather than optional.

| Concern | Choice |
|---|---|
| Language runtime | Python 3.12, matching deployment |
| HTTP framework | **FastAPI** |
| API boundary | Versioned under `/api/v1` |
| Server rendering | **Jinja2** templates |
| Client enhancement | **HTMX**, vendored — no npm, no bundler |
| Sessions | Server-side, opaque cookie — see [ADR 0004](0004-discord-oauth2-authentication.md) |
| Reverse proxy / TLS | **Caddy** (already deployed) |
| Process management | systemd, matching the existing bot unit |

**No SPA and no JavaScript build step.** Any dependency that requires npm to
produce a deployable artefact is out of scope until a measured interaction
requirement justifies it.

**HTMX is vendored as a static asset**, not loaded from a CDN. A CDN dependency
would put a third party in the trust path of an authenticated,
Council-authorization-bearing page.

### Process split

Two long-running Python processes, matching plan §5.3:

- `freedom-web` — FastAPI under uvicorn, bound to loopback, proxied by Caddy;
- `freedom-bot` — the existing Pycord gateway process, unchanged.

They share code (`application/`, `domain/`, `adapters/`) but not a process. The
bot must not import the web app, and the web app must not import Pycord.

`freedom-worker` is deliberately **not** created now. Plan §5.3: introduce a
durable worker only for a concrete need such as imports or large settlements.

## Consequences

**Positive.**

- FastAPI gives request validation and a typed boundary, which directly serves
  *"Never trust actor IDs, role claims, prices, balances, or calculated results
  supplied by the browser"* (`.agents/AGENTS.md`).
- Server-rendered templates mean authorization decisions happen where the data
  is, not in a client the user controls.
- No frontend toolchain means no npm supply chain and no build step in the
  deployment gate (plan §14.2).

**Negative.**

- FastAPI is API-first; cookie sessions, CSRF and server-rendered forms need
  explicit middleware rather than coming from the framework. Django would have
  supplied them.
- HTMX has a real learning curve for anyone expecting either a classic
  form-post application or a React one.
- Two processes sharing a database means the concurrency scenarios in plan §13.2
  ("concurrent trade/edit", "stale optimistic version") are genuinely reachable
  and must be tested, not assumed away.

**Security work this decision creates**, all required by plan §9.2 and none
supplied by FastAPI out of the box: CSRF tokens for cookie-authenticated
mutations, a Content Security Policy, `Secure`/`HttpOnly`/`SameSite` cookie
attributes, restrictive CORS, request size limits, rate limits on authentication
endpoints, and error pages that leak nothing. These belong in Phase 3, not a
later hardening phase (plan §9).

## Alternatives considered

**Django.** Genuinely competitive: it would supply sessions, CSRF, an admin
interface and an auth framework that map well onto the Council approval centre.
Rejected because the ORM and app conventions pull hard against the dependency
direction `.agents/AGENTS.md` mandates — Django models are simultaneously domain
objects and persistence records, which is exactly the coupling the migration is
trying to remove from `models/`. The plan also names FastAPI.

**Flask.** Lighter than Django, less structure than FastAPI, no typed request
validation. No advantage over FastAPI here.

**FastAPI + React/Vue SPA.** Rejected per plan §5.2: an entire build ecosystem
and a second authorization surface for a product dominated by forms and tables.

**nginx instead of Caddy.** Rejected: Caddy is already running and already
terminating TLS for this host's public traffic. Adding a second proxy would mean
two TLS configurations and two places to get security headers wrong.

## Open questions

- Production domain name for the web application ([OD-19](../discovery/open-decisions.md)).
- Whether the web app shares the host with the three Foundry instances or moves
  ([OD-20](../discovery/open-decisions.md)).
