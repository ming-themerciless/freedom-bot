# Phase 2 remediation 2 — Codex security-focused re-review

Date: 2026-08-03

Scope: authorization, artifact handling, audit content, and runtime grants in
the uncommitted remediation working tree. This report is separate from the
independent implementation re-review and is a recommendation, not approval.

## Result

The authorization, artifact boundary, database-error translation, and runtime
grant remediations are sound. One audit data-minimization issue should be
remediated before the supervised rehearsal.

### S-1 — a printable request key is still an arbitrary permanent audit channel (Blocking)

`request_key` accepts any nonblank printable text up to 255 characters and is
copied verbatim into the `snapshot_import.applied` audit payload. Those checks
prevent control-character and size abuse, but do not prevent a caller from
placing a player name, email address, access token, or other unnecessary data
into append-only audit history. The fact that the persistence table already
needs the idempotency key does not make a second audit copy exposure-free:
audit records are deliberately searchable and rendered to Council and Platform
Administrators, and permanent audit content is governed by the narrower safe
content rule in plan §6.5.

Record a one-way digest or a deliberately redacted/suffix form in the audit
payload, while retaining the verbatim key only where required for the database
uniqueness lookup. Alternatively, constrain request keys at their trusted outer
boundary to a closed opaque identifier format and prove that arbitrary user
text cannot reach this service. Preserve correlation ID and operation digest
for traceability.

Classification: **Blocking** — permanent audit data minimization/security.

## Area conclusions

- **Authorization:** Pass. Apply re-resolves current Council authority before
  every idempotency lookup. An unauthorized caller cannot retrieve a receipt;
  Platform Administrator alone remains insufficient; bootstrap remains a
  separate one-time authority path.
- **Artifact handling:** Pass. The change does not relax checksum-first parsing,
  supported-format enforcement, size/count/depth limits, path/archive refusal,
  or the prohibition on live Foundry storage. The operation digest does not
  contain raw artifact data.
- **Audit content:** Remediate S-1. Per-action required/optional allowlists are
  enforced at write time; action and issue vocabularies are closed; Actor
  display names and free-text refusal details no longer enter audit payloads.
  Folder path/exporter are necessary bounded operational provenance, and
  removing `display_name` is the right ruling.
- **Database error boundary:** Pass. SQL, parameters, conflicting Actor values,
  connection details, driver classes, and cause chains are suppressed. Exposing
  only SQLSTATE classification is acceptable.
- **Runtime grants:** Pass. Hostile `PUBLIC` grants are explicitly normalized;
  tests verify effective PostgreSQL privileges under the restricted role and
  retain intended operations. The broad `PUBLIC` revoke is appropriate for the
  stated deployment, with explicit grants required for future service roles.

## Recommendation

Remediate S-1 and re-review it together with the implementation review's B-1R
receipt finding before conducting the supervised real-export rehearsal. The
Acceptance Authority, not this report, decides the Phase 2 gate.
