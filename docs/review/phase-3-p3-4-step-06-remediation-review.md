# P3.4 Step 6 remediation 01 independent re-review

Date: 2026-08-20

Status: **REMEDIATION 02 REQUIRED AND RELEASED**

Implementer: Gemini · Independent reviewer: Codex · Acceptance authority: Peter Duscha

## Result

Remediation 01 substantially corrected the original Step 6 findings. Complete
active/historical evidence, bounded invariant UUIDs, removal of broken HTMX,
URL-encoded cursor/filter navigation, consistent VM-09 query echo, and exact
selector/token validation are present and covered by passing structural tests.

Step 6 is not yet accepted because three bounded findings remain.

## Remaining findings

1. **R2-1 — Database test is not executable.** Calls at the mutation and CSRF
   stages pass the SQLAlchemy engine to `character_version`, while the accepted
   helper requires a bound connection and calls `connection.execute()`.
2. **R2-2 — Required HTTP/security evidence remains incomplete.** The test
   omits CA success for R-23/R-24; administrator-alone and continuity refusal
   for R-24; byte-identical object-denial evidence; missing/invalid CSRF and
   stale/no-partial-write cases across R-25/R-26/R-27; and fresh-connection
   verification after cleanup that created rows are absent.
3. **R2-3 — Owner invariant copy invents replacement behavior.** The template
   says an owner grant “establishes or replaces” the primary owner. The accepted
   service refuses a different existing owner with `409`; Council must revoke
   the current owner before granting another.

## Verification

- Visual and asset integrity manifests: passed.
- Focused suite: 32 passed, 1 database skip.
- Non-database combined suite: 220 passed, 64 skipped, 3 deselected.
- Combined suite: 220 passed, 67 skipped.
- Compilation and `git diff --check`: passed.
- PostgreSQL evidence: not run because `TEST_DATABASE_URL` is absent.

## Governance

Peter's instruction to update documentation and write the remediation prompt
is the single authorization and release for remediation 02. No repeat approval
is required. Execute only
`phase-3-p3-4-gemini-step-06-remediation-02-prompt.md` and stop for independent
review. Step 7 remains unreleased.
