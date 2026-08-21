# P3.4 Step 9 final independent review

Date: 2026-08-21  
Reviewer: Codex, independent reviewer  
Scope: P3.4 Step 9 job-status and confirmation integration, including the R-37,
R-42 and R-46 remediation findings  
Recommendation: **accept Step 9**  
Acceptance authority: Peter Duscha  
Decision: **ACCEPTED — STEP 9 CLOSED**

## Acceptance Authority decision

Peter Duscha accepted P3.4 Step 9 on 2026-08-21 after the final independent
review found the R-37, R-42 and R-46 remediation findings closed and the complete
PostgreSQL-backed Step 9 gate passed with 711 tests and no failures.

This decision closes Step 9 only. It does not close P3.G4, release or accept
Step 10, authorize deployment or public exposure, permit live-service contact,
or authorize production/real-player data. The preserved Step 10 template stash
remains held until Step 10 is explicitly released.

## Outcome

Step 9 is accepted. The three findings raised during independent review are
closed:

1. R-37's concrete transaction and audit-repository orchestration resides at
   the web adapter boundary rather than in the application layer.
2. R-42 accepts exactly one server-minted, fixed-width URL-safe preview nonce
   without normalization and preserves authorization and CSRF precedence.
3. R-46 accepts exactly one nonce equal to the canonical preview-job UUID from
   its route path, so direct callers cannot choose alternate request identities.

The older P3.3 test edits are compatibility corrections to test input. They
replace hand-built nonce strings with the canonical shapes now enforced by the
production boundaries. They change no P3.3 route, capability, persistence,
state-machine, audit or product behavior and require no separate product-policy
decision.

## Step 10 isolation

The in-progress Step 10 versions of these templates were preserved in the named
Git stash `Preserve in-progress P3.4 Step 10 templates before Step 9 gate`:

- `adapters/web/templates/audit_results.html`;
- `adapters/web/templates/audit_search.html`; and
- `adapters/web/templates/import_result.html`.

The Step 9 verification tree contains the accepted corpus:

| Template | SHA-256 |
|---|---|
| `audit_results.html` | `11ee0efcba8892970dee0870b5612d0fbf9c5091d5cf954ddf77e4af4f98291e` |
| `audit_search.html` | `c54db1a4cc1779a52921269641330f79d295a843086eb198916a2f07c6e61c15` |
| `import_result.html` | `152b84f766211b886ddd67ca1ce03c53cb37ceefc9ea5678cd22f7f2b7f3fff6` |

No Step 10 digest was approved or substituted by this review. Restore the
preserved Step 10 work only when that step is released for implementation or
review.

## Verification evidence

The complete accepted P3.4 surface through Step 9 was run against the disposable
local PostgreSQL database with:

```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_p3_4_static_assets.py \
  tests/web/test_static_asset_surface.py \
  tests/web/test_p3_4_shell_and_components.py \
  tests/web/test_p3_4_auth_and_system_views.py \
  tests/web/test_p3_4_member_views.py \
  tests/web/test_p3_4_council_character_views.py \
  tests/web/test_p3_4_identity_and_role_views.py \
  tests/web/test_p3_4_snapshot_views.py \
  tests/web/test_p3_4_job_status_views.py \
  tests/web/test_account_identity_refusal_audit.py \
  tests/web/test_p3_3_jobs.py \
  tests/web/test_p3_3_matrix.py \
  tests/web/test_p3_3_success_cells.py \
  tests/web/test_structural_guards.py
```

Result: **711 passed, 26 skipped, 0 failed** in 28.39 seconds.

The 26 skips are the existing `test_p3_3_matrix.py` permitted cells whose
success behavior is asserted by the per-route success tests. No PostgreSQL
evidence was skipped.

Additional checks:

- `python -m compileall -q application adapters domain`: passed;
- `git diff --check`: passed;
- formatter: not configured;
- linter: not configured;
- type checker: not configured.

The run emitted HTTPX deprecation warnings about per-request cookies. They do
not affect Step 9 correctness but should be handled in later test-maintenance
work before the relevant HTTPX API is removed.

## Security and integrity conclusions

- ordinary, non-member, administrator-only and continuity callers cannot reach
  Council job operations;
- CSRF and authorization precede nonce validation;
- malformed and unreachable identifiers remain non-enumerating;
- malformed, duplicate, alternate and oversized nonce submissions enqueue no
  job and write no success audit effect;
- duplicate and concurrent confirmations converge on one live apply and one
  durable effect under PostgreSQL constraints;
- refusal-audit and successful mutation transaction boundaries remain durable;
- no schema, migration, capability, route, Foundry, Sheet or game-state scope
  changed; and
- no live service, production database, secret, real snapshot or player data
  was used.

## Recommendation and accepted disposition

Codex recommended acceptance, and Peter accepted P3.4 Step 9 on 2026-08-21.

Retain the Step 10 stash until Step 10 is explicitly released.
Do not apply it back merely to close Step 9; Step 9 is now verified independently
against its accepted corpus.
