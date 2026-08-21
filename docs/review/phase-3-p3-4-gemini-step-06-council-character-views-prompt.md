# Prompt for Gemini — P3.4 Step 6: Council character-access pages

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY** · Step: 6 of 13

Peter accepted Step 5 and, in the same instruction, authorized and released
this bounded Step 6 prompt. Perform Step 6 only, report its checkpoint, and
stop. Step 7 and every later step remain unreleased.

This release does not authorize backend/contract changes, P3.G4 closure,
database provisioning, staging, deployment, secrets, live services, real data,
or production use.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master prompt and execution plan;
3. the Step 1 baseline and Steps 2–5 acceptance/review records;
4. the remediation release-policy clarification;
5. all Phase 3 contracts in prescribed order, especially R-22 through R-27,
   VM-07 through VM-09, object denial, CSRF/Origin, threat model and traceability;
6. production view-model types and R-22–R-27 handlers/services;
7. existing safe disposable-database fixtures and P3.2 authorization/CSRF/
   concurrency tests; and
8. the frozen Council prototype as reference only.

Record initial status/diff. Verify every starting hash and required absence.
Preserve unrelated dirty/untracked work and all stashes. Stop on mismatch,
overlap, missing VM fact, contract discrepancy, or required backend change.

## Objective

Implement only:

- `council_characters.html` — VM-07 / R-22;
- `character_links.html` — VM-08 / R-23 and mutation forms R-25–R-27; and
- `identity_search.html` — VM-09 / R-24 standalone HTMX fragment.

Render controls only from accepted server-produced pre-authorization facts.
The server remains authoritative. Every essential navigation and mutation must
work without JavaScript; HTMX may enhance R-24 but may not be required.

## Starting hashes

| File | Required SHA-256 |
|---|---|
| `adapters/web/templates/council_characters.html` | `cffc9bbb63773028deb4b0056c9a9d2c82a185c8f00a91530a623efd62c81661` |
| `adapters/web/templates/character_links.html` | `fbdbfe0c761304a77928b569568a8b79be3ef25ed4ae4a51fee6eb57c89cfa8b` |
| `adapters/web/templates/identity_search.html` | `fe5cb51fdfdcf5a829a7569766321ad6b8b555f8dbc3b520b94158a028c53f6e` |
| `adapters/web/templates/base.html` | `b836aba09cc60a2917a4b783e5b49021518e15ffed91d65fb5ecc8957d2926e5` |
| `adapters/web/templates/includes/header.html` | `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796` |
| `adapters/web/templates/includes/footer.html` | `2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3` |
| `adapters/web/static/css/freedom-blades.25d24d281e2b.css` | `25d24d281e2ba5645b1a96e09ff452be8d36fda49be106fcaea25698fd9b1b64` |
| `adapters/web/static/asset-integrity.sha256` | `eb83735f66910804dc74189655fde77aa9d5a6caf58fc5debec08edb71e637d7` |
| `tests/web/test_p3_4_member_views.py` | `d5efba524b44ce04f2389048aed311a8cf7636a3ede47de90b14611b030f814d` |
| `tests/web/test_p3_4_auth_and_system_views.py` | `4041972076634dcb41689eabfcd570da1046f08d0db29e636ce810e5870752df` |
| `tests/web/test_p3_4_shell_and_components.py` | `86124cc1e860aaf03828e9723654fde4a168a0702c8cf73bd5fbdb1d3131d8de` |
| `tests/web/test_p3_4_static_assets.py` | `61c612d254f4fbf409dd5368e424aafc074e92fbd966a68d4048a232ff5b83d0` |
| `tests/web/test_static_asset_surface.py` | `a6128f0a29995f10fce7ca7556ea1119b66ccd1acbd4363b55c1a06d2784322a` |

`tests/web/test_p3_4_council_character_views.py` must be absent. HTMX and emblem
must retain their accepted full digests. Stop on any mismatch.

## Exact write allowlist

Only these paths may change:

- the three objective templates;
- `base.html`, CSS filename only;
- removal/replacement of the one fingerprinted CSS file;
- `asset-integrity.sha256`, CSS entry only;
- `tests/web/test_p3_4_shell_and_components.py`, only the three transitioned
  template digests, CSS digest and exact Step 6 selector scope/use;
- `tests/web/test_p3_4_static_assets.py`, only exact CSS facts or an obsolete
  earlier-step selector boundary;
- `tests/web/test_static_asset_surface.py`, exact CSS filename only;
- `tests/web/test_p3_4_auth_and_system_views.py` and
  `tests/web/test_p3_4_member_views.py`, only the three transitioned template
  digests/count wording and exact CSS facts required to keep their immutable
  corpus/integrity checks green; and
- new `tests/web/test_p3_4_council_character_views.py`.

No include, header/footer, backend Python, route, view model, contract,
dependency, configuration, documentation, prompt, prototype, HTMX, emblem, or
other template/test change is permitted.

## R-22 / VM-07 Council character index

- Render `ready` and `empty`, bounded rows, stable ordinary `links_path`
  navigation, nullable level as `not recorded`, active state, active owner,
  active-link count and explicit unresolved-owner state.
- Render GET search/filter form for `/v1/council/characters` using only accepted
  `query` and `include_inactive`; search is never identity or authorization.
- Render opaque cursor navigation only from accepted cursor paths/tokens. Never
  invent offsets or decode/sign cursors client-side.
- No mutation form belongs on R-22.

## R-23 / VM-08 character links

- Render character summary, display-only `character_version`, active links
  (max 25), historical links (max 100), cursor navigation, and all accepted
  Council-visible `AccessFact` evidence, including subject display where
  present, grant/revoke/expiry facts, reason and correlation.
- Explain `LinkInvariants` before mutation: one-active-owner consequence,
  revoking the last owner may leave unresolved, and bounded existing-default
  character IDs. These facts explain; they do not enforce.
- Render R-25 grant as standard POST to
  `/v1/council/characters/{character_id}/links` with exactly successful named
  fields `{csrf_token, version, subject, access_kind, reason}`.
- R-25 `subject` is the selected/manual Discord snowflake; names are labels,
  never identity. `access_kind` is exactly owner/co_owner/delegate/viewer.
- Render each R-26 revoke POST to
  `/v1/council/characters/{character_id}/links/{access_id}/revoke` with exactly
  `{csrf_token, version, reason}`.
- Render each R-27 default POST to
  `/v1/council/characters/{character_id}/links/{access_id}/default` with exactly
  `{csrf_token, version, reason}`.
- Never submit account IDs, actor IDs, access IDs as body authority, correlation,
  timestamps, current/default state, grantor, invariant facts, or server-owned
  fields. Path identifiers remain in paths only.
- Use the VM's synchronizer CSRF token. Do not create cookie-readable or
  JavaScript-derived CSRF authority.

## R-24 / VM-09 identity-search fragment

- This is a meaningful standalone fragment with no document shell/landmarks.
- Render ready, empty and invalid states; escaped bounded `query_echo`; at most
  25 candidates; truncation; and the controlled `names_are_not_identity`
  notice.
- Candidate identity is the canonical `discord_subject` snowflake. Username and
  optional global name are evidence labels. Render observed time and both
  linked-state facts without inventing authority.
- R-24 is Council-only and answers `401` fragment response—not login redirect—
  when unauthenticated. Administrator alone, continuity callers and ordinary
  members remain refused by accepted backend authorization.
- If used as HTMX enhancement, use only accepted safe `hx-get`/target/swap
  attributes. No `hx-on:`, inline script, or JS-only selection. Manual snowflake
  entry and ordinary forms must remain usable without JavaScript.

## Shared security and CSS rules

- Preserve strict autoescape; zero `|safe`, inline event handler, `hx-on:`,
  inline executable script, remote origin/font, dynamic include or prototype
  production reference.
- Render only accepted VM fields and closed codes. Bound long content and keep
  tables usable through local overflow without hiding facts.
- Add only exact selectors actively used by the three Step 6 templates for
  Council filters/tables, invariant notices, access-history rows, forms and the
  identity candidate fragment. No Step 7+ identity-migration/role/admin,
  snapshot, job/polling, import/audit or dialog selectors.
- Preserve earlier selectors and integrity. Fingerprint/rename CSS, update base
  and manifest atomically, remove superseded CSS.

## Tests

Create `tests/web/test_p3_4_council_character_views.py` using strict direct
rendering, shared production validators, and database-backed HTTP evidence when
an already-configured disposable database exists. Prove at least:

1. VM-07 ready/empty/filter/cursor/nullable-level/unresolved-owner branches;
2. R-22 GET form exact fields and no mutation control;
3. VM-08 active/historical bounds, evidence, invariant and cursor branches;
4. exact R-25/R-26/R-27 action, method and successful named-field sets, with
   absence of every server-owned/foreign field;
5. no-JavaScript manual snowflake grant, revoke and default submissions;
6. VM-09 ready/empty/invalid/truncated/candidate/evidence-notice branches and
   standalone fragment semantics;
7. adversarial escaping and exact bounds;
8. Council/CA success, ordinary member and administrator-alone refusal,
   continuity refusal, R-24 unauthenticated `401`, direct-call protection,
   object substitution/non-enumeration, valid/invalid/missing CSRF, stale
   version, and accepted redirect outcomes through existing backend behavior;
9. database fixture cleanup after yield using a real connection, with shared
   structural positive/negative evidence;
10. exact digest protection for every non-Step-6 template and transitioned
    digest ownership across existing tests;
11. exact active CSS definition and exact active class-token use, prohibited/
    unused/comment/substring/value falsifications, fingerprint/manifest tamper
    failure, and unchanged HTMX/emblem; and
12. form-field, hidden-authority, unsafe-template, fragment-shell, authorization
    and selector mutations rejected through the same helpers used positively.

Structural/direct-render cases must run without PostgreSQL. Database cases may
skip only when `TEST_DATABASE_URL` is absent, must use safe disposable guards
and post-yield cleanup, and must report that a skip is not database evidence.
Do not provision or discover a database from `.env`.

## Verification

Run and report literally:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py
git diff --check
git status --short
```

Report exact hashes, allowlist compliance, evidence classes, pass/skip counts,
database execution/skips, and every check not run.

## Stop and handoff

Stop on any mismatch, overlap, required backend/contract change, unsafe database
configuration, authorization ambiguity, or need outside the allowlist. At
successful completion report:

`READY FOR INDEPENDENT STEP 6 REVIEW`

Then stop. Do not begin Step 7 or claim Step 6 acceptance.
