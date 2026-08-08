# Phase 2 remediation 3 — Codex security-focused re-review

Date: 2026-08-03

Scope: the S-1 audit-content remediation in the uncommitted working tree. This
report is separate from the independent implementation re-review and is a
recommendation, not approval.

## Result

**S-1 is resolved. I found no new blocking or important security finding in
this remediation.** The remaining unkeyed-digest limitation is explicit and is
not an authorization weakness.

## S-1 disposition

The raw request key no longer reaches append-only audit payloads, refusal
messages, or refused-row keys. It remains verbatim only in
`snapshot_imports.request_key`, where exact lookup is required for idempotency.
The applied audit event carries a domain-separated, versioned SHA-256 digest;
the old `request_key` payload property is undeclared, so the enforced payload
policy refuses any attempted reintroduction.

The implementation also removes the key from the `request_key_conflict`
message and constructs refused-row identities from the digest plus correlation
ID. Source inspection found no import-path logger receiving the raw key. These
changes close the arbitrary second-copy channel identified by S-1 while
retaining correlation ID and operation digest for event and operation
traceability.

## Residual risk

The digest is unkeyed. A reader who already suspects a short or predictable
request key can hash the guess and confirm it. This is a real pseudonymisation
limit, but not a remaining S-1 blocker:

- the prior finding explicitly permitted a one-way digest;
- the digest replaces an unnecessary verbatim copy rather than claiming to
  make the key secret;
- it is never accepted as an idempotency key or authorization credential; and
- the service still requires current Council authority before returning an
  idempotency result.

Phase 3 should supply opaque, high-entropy interaction identifiers at the outer
boundary. If future audit readers are broader than import-history readers, or
request keys remain human-chosen, the Data/Security Owner should reassess
whether cross-event request-key grouping is necessary or should be removed.

Pre-existing audit rows are not rewritten, consistently with append-only
history. The submission states only disposable `freedom_test` currently holds
such rows; production handling remains an Operations/Data Owner decision.

## Verification performed

The full PostgreSQL-backed suite passed with 1,566 tests and no skips. It
includes audit-policy rejection of the raw key, digest determinism and domain
separation, safe conflict/refusal content, transactional audit failure, live
concurrency, and hostile-`PUBLIC` restricted-role tests. Compilation, Alembic
schema-drift, and diff-whitespace checks also passed. The only warning was the
pre-existing `audioop` deprecation warning.

## Recommendation

Proceed to the remaining owner-controlled Phase 2 operational evidence. Phase
2 remains open until the supervised real-export rehearsal, Data Owner and
Operations evidence, and Acceptance Authority decision are recorded.
