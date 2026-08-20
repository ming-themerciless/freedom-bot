# P3.3 sixth migration-rollback correction — security-focused re-review

Date: 2026-08-19

Scope: the security-sensitive parts of change-log `C-P3.3-I` only. This review
is distinct from the implementation re-review and considers the test-scoped
`pg_terminate_backend()` path, backend identity, connection ownership, orphan
accounting and production reachability.

## Result

No blocking or major security finding.

- `pg_terminate_backend()` appears only in
  `tests/web/test_migration_0013_rollback_boundary.py`; no production route,
  worker, migration, operator tool or infrastructure template can invoke it.
- The target is the test-owned holder backend and is matched on both `pid` and
  `backend_start`, captured directly from that holder before cleanup can block.
- Query values are bound parameters rather than interpolated SQL.
- The holder is detached from its pool before any cleanup helper thread starts,
  so a thread left inside rollback or close cannot return a still-used connection
  to the shared pool.
- A helper thread that outlives its bound is recorded and reported as cleanup
  failure. The passing path cannot silently accept it.
- Independent backend disposal is attempted only after client-side rollback or
  close fails to return; later cleanup and writer joining remain bounded.

## Verification

Run serially against the disposable database with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`:

```text
./venv-web/bin/python -m pytest -q \
  tests/web/test_migration_0013_rollback_boundary.py \
  tests/web/test_structural_guards.py \
  tests/test_rejected_scope_absent.py -rs
```

Result: **120 passed in 23.16s**.

## Recommendation and decision

Security recommendation: accept `C-P3.3-I`.

Peter/Acceptance Authority accepted `C-P3.3-I` on 2026-08-19. This accepts the
sixth correction and supersedes the defective fifth-correction ceiling claim; it
does not separately accept `C-P3.3-H`, close P3.G3 or authorize P3.4.
