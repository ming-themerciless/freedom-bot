# P3.G1 independent implementation and security re-review

**Date:** 2026-08-16  
**Reviewer:** Codex, Independent Reviewer and distinct security-focused review
resource  
**Decision authority:** Peter Duscha, Acceptance Authority and accountable
Security Reviewer

## Outcome

**No remaining blocking or important implementation or security finding was
identified. P3.1 and stop gate P3.G1 are recommended for acceptance.**

Peter Duscha accepted that recommendation on 2026-08-16. P3.G1 is closed and
P3.2 is authorized to begin. P3.3 is not authorized by this decision: it remains
behind P3.G2 and the P3.2 read-path, identity, object-authorization and Council
administration review.

This review covers the complete current P3.G1 package, not only the final
break-glass remediation. It reconciles the original P3.1 submission, OD-44
completion/provider/session remediations, exact numeric-policy and canonical
settings-graph remediations, provider/engine/request authority, application
lifecycle and startup cleanup, test-clock evidence, and the distinct security
review of N-32/N-33 with its remediation.

## Recommendation by control area

- **OAuth and provider binding:** accept. Completion is durably bound to the
  claimed OAuth transaction and its recorded provider; provider I/O remains
  outside database transactions; session rotation cannot cross account,
  authentication method or OAuth binding.
- **Sessions:** accept. Rotation and touch cannot revive an expired or revoked
  row, extend the absolute lifetime, or apply an ordinary idle window to a
  break-glass session. Registered bounds have one exact-integer runtime
  definition and one canonical settings source.
- **Break glass and authorization:** accept. WebAuthn and recovery-grant sessions
  resolve only Platform Administrator capability and cannot imply Council or
  character authority. The N-67 escalation sequence remains refused.
- **Configuration and composition authority:** accept. One canonical settings
  graph supplies the provider, engine, middleware, request authority,
  repositories and services. Process-lifetime authorities are derived once,
  write-once and not re-resolved through mutable `app.state`.
- **Lifecycle and startup:** accept. One composition is claimed by one ASGI
  lifespan. Normal shutdown, refused startup and covered partial construction
  release owned resources without disposing lent test resources or replacing
  the original startup refusal.
- **Authentication throttles:** accept. R-08 reaches N-32's per-account budget
  after credential resolution and before verification, in a transaction that
  commits independently of the assertion. An unresolved credential spends the
  same configured limit and window in a keyed per-credential bucket. R-09 spends
  N-33's per-grant attempt in its own committed transaction, and the repository
  increment is one atomic `UPDATE ... RETURNING` statement.
- **Schema and migration evidence:** accept for P3.G1. Migrations 0006–0009,
  OD-44's durable binding, provider binding and rotation integrity have the
  required PostgreSQL constraint, concurrency, rollback and mutation evidence.

## Evidence independently run

All database-backed commands used the guarded disposable PostgreSQL database
`freedom_test` over its local Unix-domain socket.

| Check | Result |
|---|---|
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/python -m pytest -q -rs tests/web` | **712 passed**, 20 dependency deprecation warnings, 0 skipped |
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q -rs` | **2260 passed**, 1 dependency deprecation warning, 0 skipped |
| `./venv-web/bin/python -m compileall -q adapters/web application/web tests/web tests/web_fixtures.py` | passed |
| `git diff --check` | clean |

The warnings are the already-recorded `httpx` per-request-cookie and Discord
`audioop` deprecations. No formatter, linter or type checker is configured.
Historical falsification mutations were inspected through their restored code
and recorded results; this review did not repeat every mutation run.

## Evidence wording correction

TC-BG-16 proves identical **externally meaningful outcomes** for enrolled and
invented credential IDs: the same sequence of status codes and coarse error
codes, with rate limiting beginning at the same attempt and using the same
configured window. It does not prove literally byte-identical response bodies:
correlation identifiers intentionally differ between requests. It also does not
compare literal `Retry-After` values, which can differ with request timing. The
traceability and remediation records are corrected accordingly without changing
the implementation or the security conclusion.

## Conditions deliberately carried forward

### I-06 — staging/browser/device evidence remains open

P3.G1 acceptance is based on automated, direct-HTTP and real-PostgreSQL evidence.
No staging environment currently exists, so TC-LIM-02, the browser half of
TC-SEC-07, TC-OPS-01 through TC-OPS-05 and TC-PERF-01 through TC-PERF-03 remain
unrun. I-06 therefore stays **open**.

This is not a blocker for beginning P3.2. It is a blocker for claiming the final
Phase 3 production-readiness evidence and for exposing the portal in staging or
production until the owning gate's documented checks have run successfully.

### A-05 — real WebAuthn enrolment remains open

The enrollment mechanism, minimum-two invariant and startup refusal are accepted
as P3.1 implementation. No deployment host has yet been proved to hold the two
real enrolled credentials required for the protected administrator. A-05 stays
**open** until the Operations Owner validates that prerequisite.

This is not a blocker for beginning P3.2. It is a blocker for public staging or
production exposure: without it, the normal break-glass route cannot satisfy its
operational purpose during a Discord outage.

## Gate decision

Peter Duscha accepted P3.1 and closed P3.G1 on 2026-08-16. RAID I-07, I-09 and
I-10 are closed by this re-review and decision. I-06 and A-05 remain open under
the conditions above. P3.2 may begin; later package gates and the final Phase 3
gate remain mandatory.
