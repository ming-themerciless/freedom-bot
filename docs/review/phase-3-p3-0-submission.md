# Phase 3 P3.0 submission — contract and security design baseline

**Date:** 2026-08-13

**Package:** P3.0, the first package authorized by Peter Duscha's acceptance of
`docs/review/phase-3-delivery-plan.md` on 2026-08-13.

**Author:** Claude, operating as Working Technical Lead under Peter's designation.

**Status:** **Submitted for review. Nothing here is accepted.** P3.0 is
documentation and design. No route, dependency, migration, framework scaffold,
service, template or runtime module was added. Nothing was deployed or started.

**Requested next step:** Codex independent architecture review and a **distinct**
security-focused review, then Peter's P3.G0 decision.

> **Superseded in four respects, 2026-08-13.** This document is the dated record
> of what was submitted for the first review and is kept unedited apart from this
> note. Codex's review and Peter's remediation decision found four defects in it,
> which are corrected in the contracts and recorded in
> [`phase-3-p3-0-remediation-submission.md`](phase-3-p3-0-remediation-submission.md):
>
> 1. **§7 F-1 and §4 decision 6 are wrong in an important way.** Adding a
>    `NOT VALID` check is not sufficient: migration 0001's
>    `ck_audit_events_human_action_has_an_actor` still requires a Discord user id
>    for every human capability, so a Discord-independent break-glass audit insert
>    would have failed. The constraint is now **replaced**, not supplemented.
>    Related: this document and the contracts attributed the append-only trigger to
>    migration 0005; it is **migration 0002**.
> 2. **The break-glass boundary was incomplete.** A break-glass session could
>    create arbitrary role-capability mappings and thereby arrange Council
>    authority for a later ordinary login. N-67 and mapping provenance close it.
> 3. **N-43's job attempt semantics were unreachable**, leaving a job `running`
>    forever after its third lease expired. Redesigned.
> 4. **The PKCE verifier was described as hashed** in the route contract and
>    encrypted in the schema. It is encrypted; the route contract was wrong.
>
> Everything else in this document — the inventory, the boundaries confirmed in
> §9, the commands and outcomes in §8 — stands as recorded.

---

## 1. P3.G0 decision recorded by Peter

Peter Duscha reviewed the five proposals and the Codex findings on 2026-08-13.
The decision is:

| # | Decision |
|---|---|
| **D-1** | **Approved.** Introduce the separate `freedom-worker` process. |
| **D-2** | **Approved.** Treat Council apply as a durable job, subject to remediation of the retry-state machine before implementation. |
| **D-3** | **Conditionally approved.** Retain the narrower break-glass surface, but a break-glass session must not create a role-capability mapping that can confer Council, character or import authority after a later ordinary-provider login. Remediation must define and test a narrow administrator-continuity allowlist. |
| **D-4** | **Partly/provisionally approved.** N-30–N-42 and N-44–N-66 are accepted as proposed starting values, subject to their named staging measurements and gates. N-43 is withheld: its attempt semantics and job transitions must be corrected and re-reviewed. |
| **D-5** | **ADR 0010 conditionally approved.** Its provider-neutral account model and Discord-independent emergency-administration direction are accepted. Final acceptance and implementation authority require remediation of account-based audit attribution and the break-glass escalation path. |

This is a **remediation decision, not P3.G0 closure**. The blocking Codex findings
must be corrected and independently re-reviewed. P3.1 and Gemini production
integration remain unauthorized.

## 1.1 Original five proposals

Everything else in this package is an elaboration of the accepted plan. These five
are proposals that go beyond it and cannot be settled by an implementer.

| # | Decision | Why it is Peter's | Where |
|---|---|---|---|
| **D-1** | **Introduce a separate `freedom-worker` systemd service.** The measured 9.566-second preview is GIL-holding work (`json.loads` plus pure-Python NFC normalization), so running it inside `freedom-web` stalls every other request — including the status polls that exist to report the job and the health check monitoring relies on. The queue stays in PostgreSQL; this adds a **process**, not a technology | It adds a service to the accepted topology. Delivery plan §5 P3.3 explicitly asked P3.0 to show whether this is necessary | [Operational contract §3](../contracts/phase-3-operational-contract.md) |
| **D-2** | **The Council apply becomes a durable job too.** A real-folder apply has **never been measured** — Rehearsal B previewed and applied nothing, and the 500-Actor apply benchmark used Actors ~233× smaller (the RA-5 calibration error). An apply re-parses the same artifact, so its floor is the same ~9.6 s | It changes the shape of the confirmation route from the plan's implied synchronous apply | [Route contract §6.3](../contracts/phase-3-route-authorization-contract.md) |
| **D-3** | **Restrict break-glass sessions to identity/capability administration and audit reads (N-65)** — tighter than the accepted §7 boundary, which says only "Platform Administrator capability" | It narrows an accepted contract. Tightening is safe, but it is still a change to what Peter accepted | [Numeric register §3.4](../contracts/phase-3-numeric-policy-register.md); [ADR 0010 D9](../adr/0010-provider-neutral-identity-and-emergency-administration.md) |
| **D-4** | **Accept the P3.0-proposed numeric values N-30…N-66** — rate-limiter storage and algorithm (which §7 explicitly left to P3.0), break-glass limits, job bounds, pool and timeout bounds, WebAuthn parameters and session limits | §7 says a later change to a numeric policy follows change control; these are the new ones | [Numeric register §3](../contracts/phase-3-numeric-policy-register.md) |
| **D-5** | **Accept proposed ADR 0010**, the provider-neutral identity and emergency-administration decision that OD-43 requires before P3.1 | It is an architecture decision record; only Peter accepts one | [ADR 0010](../adr/0010-provider-neutral-identity-and-emergency-administration.md) |

If D-1 is declined, the honest consequence is that the portal stalls for roughly
ten seconds per preview and per apply, visibly, for every concurrent user.

## 2. Artifact inventory

### 2.1 Created

| Path | Lines | Contents |
|---|---:|---|
| `docs/contracts/README.md` | 49 | Package index and reading order |
| `docs/contracts/phase-3-numeric-policy-register.md` | 135 | Every numeric policy, defined once |
| `docs/contracts/phase-3-route-authorization-contract.md` | 672 | Deliverable 1 |
| `docs/contracts/phase-3-view-model-contract.md` | 768 | Deliverable 2 |
| `docs/contracts/phase-3-logical-schema.md` | 687 | Deliverable 3, schema half |
| `docs/contracts/phase-3-identity-migration-contract.md` | 317 | Deliverable 3, migration half |
| `docs/contracts/phase-3-state-machines.md` | 371 | Deliverable 4 |
| `docs/contracts/phase-3-threat-model.md` | 225 | Deliverable 5, threat half |
| `docs/contracts/phase-3-configuration-and-dependency-contract.md` | 288 | Deliverable 6, config/dependency half |
| `docs/contracts/phase-3-operational-contract.md` | 268 | Deliverable 6, operational half |
| `docs/contracts/phase-3-test-traceability.md` | 353 | Deliverable 7 |
| `docs/adr/0010-provider-neutral-identity-and-emergency-administration.md` | 298 | Deliverable 5, ADR half |
| `docs/review/phase-3-p3-0-submission.md` | — | This handoff |

### 2.2 Changed

| Path | Change | Why it genuinely changed state |
|---|---|---|
| `docs/adr/README.md` | Index row for 0010 (Proposed) plus an addition note | A new ADR exists |
| `docs/project-management/status.md` | Milestone row, critical path items 1–2, open conditions, next-update trigger | P3.0 moved from *authorized* to *submitted for review* |
| `docs/project-management/decision-register.md` | OD-43 row | The design OD-43 was waiting for now exists and is under review |
| `docs/project-management/raid-register.md` | Statuses of R-20, R-21, R-24, R-26, R-27; new risk R-28; new assumptions A-05, A-06 | Proposed Phase 3 risks now have named designs and tests; two new facts were discovered |
| `docs/project-management/change-log.md` | New section *Phase 3 P3.0 contract and security design submission*, decision **Not yet decided** | Plan §0.2 requires a dated entry for a material proposal |

### 2.3 Not touched

No file under `design-prototype/` (freeze manifest re-verified, 14/14 OK), no
source module, no test, no migration, no `requirements*.txt`, no `.env.example`,
no `alembic.ini`, no systemd unit, no Caddy configuration. `.env` was never read.

## 3. Deliverable-to-section map

| P3.0 prompt deliverable | Where it is satisfied |
|---|---|
| **1. Route and authorization contract** — every P3.1–P3.3 endpoint, method, auth state, capability, CSRF/origin, bounds, outcomes, session/cache/audit effects, kind, and proof that UI hiding is not authorization | `phase-3-route-authorization-contract.md` §§1–8. Route detail §4.1/§5.1/§6.1; matrices §4.2/§5.2/§6.2; outcomes §7.1; headers §7.2; session/cache/audit effects §7.3; CLI surface §8; UI-hiding proof §2.2 |
| — role matrices for the seven caller states | §3.1 and every matrix table |
| — login/callback/logout, health, My Characters, character detail, link administration, role-capability mapping, job lifecycle, import confirmation, audit search | R-01…R-10, R-20…R-37, R-40…R-49 |
| **2. Versioned view-model contracts** | `phase-3-view-model-contract.md`, version `vm-1`. Login/session/degraded VM-01…VM-04, VM-13; character summary/detail and portrait VM-05, VM-06, §3.4; link administration and identity resolution VM-08…VM-10; field profiles and `migration deferred` VM-11 and §2; job status/progress/result/stale VM-15; confirmation scope VM-14/VM-15/VM-17; audit VM-18; standard states VM-19…VM-21; escaping and safe display §3; Jinja/HTMX constraints §9 |
| **3. Logical schema and migration contract** | `phase-3-logical-schema.md` §§1–11 (ER diagram §2, per-table detail §§4–10, decision table §11, access patterns §11.1, runtime grants §11.2) and `phase-3-identity-migration-contract.md` §§1–10 (stages §3, rollback boundary §4, backup/rehearsal §5, verification period §6, Sheet-era evidence §7, control totals §7.4) |
| **4. State machines** | `phase-3-state-machines.md` SM-01 OAuth, SM-02 session, SM-03 break-glass, SM-04 identity linking, SM-05 jobs, SM-06 membership projection. Each has forbidden transitions and the six required failure modes |
| **5. ADR and threat model** | `docs/adr/0010-…md` (context, ten decisions, security consequences, adapter interface, migration strategy, rollback implications, five rejected alternatives) and `phase-3-threat-model.md` (assets §1, boundaries §2, attackers §3, 53 threats §4, residuals §5, verification map §6) |
| **6. Configuration, dependency and operational contracts** | `phase-3-configuration-and-dependency-contract.md` (dependency proposal §1 with rejected alternatives §1.4, typed configuration §2, fifteen startup refusals §2.3, environment separation §2.4) and `phase-3-operational-contract.md` (evidence discipline §1, topology §2, worker finding §3, perimeter and kill switch §4, monitoring §5, backup/recovery §6, gate inputs §7) |
| **7. Acceptance and test traceability** | `phase-3-test-traceability.md`, ~150 named cases across 17 groups, plus complete coverage tables for delivery plan §11 (§18) and implementation plan §12 Phase 3 (§19), and the explicit later-evidence list (§20) |

## 4. Decisions made inside P3.0's authority

These follow from the accepted plan and existing repository evidence. They are
recorded so a reviewer can disagree with any of them specifically.

| # | Decision | Basis |
|---|---|---|
| 1 | `/v1/*` is the browser boundary; `/api/v1/*` stays the machine boundary | The Foundry module's submission path is deployed and must not move (ADR 0009) |
| 2 | The Phase 2 `GET /api/v1/foundry/snapshots/{checksum}/preview` route is **retired** by P3.3 | It was built inert pending a Phase 3 authentication composition and has never served an authenticated request; the job routes supersede it |
| 3 | OAuth start is a `GET` navigation, so the accepted CSP stands **unweakened** | The N-26 validation §7 required; `form-action 'self'` is enforced across redirect chains, and a `GET` navigation is not a form submission |
| 4 | Object-scoped denials return `404`; capability-scoped denials return `403` | Prevents an existence oracle over character, job and access identifiers |
| 5 | A non-member receives **no session**; R-04 answers `403` with VM-02 | ADR 0004 requires rejection before session creation. Caller state `N` therefore arises only from mid-session revocation |
| 6 | Append-only history is **never rewritten**; historical attribution resolves through `external_identities` | Rewriting it would require suspending the migration-0005 trigger the Phase 2 gate accepted |
| 7 | External identities are **retired, never deleted**, and uniqueness covers retired rows | Keeps historical attribution readable and blocks subject-reuse takeover |
| 8 | The CSRF token is derived as `HMAC(key, session_id)` and stored nowhere | Session-bound and rotates with the session, with no second column to desynchronize |
| 9 | Rate limiting uses a PostgreSQL fixed-window counter | §7 ruled an in-process limiter insufficient; PostgreSQL is already required, transactional and backed up |
| 10 | Reconciliation warnings cross the boundary as closed-vocabulary **codes**, never artifact text | Extends the existing `ISSUE_CODES` discipline to the presentation boundary |
| 11 | No character image is served in Phase 3; portraits are initials plus metadata | Foundry image proxying is deferred (visual handoff §6) |
| 12 | Eleven production dependencies, four already present; no Redis, no broker, no auth/CSRF/session library | Delivery plan §5 P3.1's "deliberately bounded"; each security decision must remain reviewable |
| 13 | Cancellation is a timestamp, not a seventh job state | §8.2 names exactly six states |

## 5. Assumptions

| # | Assumption | If wrong |
|---|---|---|
| A-1 | The production database currently holds no or few `character_access` rows, so the identity migration is cheap now and monotonically more expensive later. **P3.0 did not inspect production data and must not.** The migration is designed for a non-empty database and computes its totals at run time | Nothing breaks; the migration simply does more work |
| A-2 | The Server Administrator's protected account and two WebAuthn credentials are established **before** public exposure (RAID A-05, startup check S-15) | The emergency route exists but cannot be used, so a Discord outage locks the administrator out |
| A-3 | PostgreSQL is an acceptable substrate for both the job queue and the rate limiter (RAID A-06) | A broker or Redis returns to the dependency proposal, which is a change request |
| A-4 | `py_webauthn` remains maintained and is acceptable to the Security Reviewer | The break-glass primary credential needs a different library or a different mechanism |
| A-5 | Discord's `guilds.members.read` continues to expose role IDs for the configured guild | Capability resolution needs another source; the adapter boundary contains the change |
| A-6 | One worker process and a job concurrency of 1 are sufficient for this community's volume | N-41/N-42 are raised after staging measurement |

## 6. Residual risks

Twelve are enumerated with owners in the threat model §5. The ones that most
affect the P3.G0 decision:

| # | Residual | Severity |
|---|---|---|
| RR-05 | **Worker peak memory is unmeasured.** N-47's 1 GiB is a guard, not a measurement | Medium |
| RR-06 | **Real-folder apply duration has never been measured** | Medium |
| RR-01 | Up to 5 minutes of stale privilege on reads after a role change — accepted in §7 | Medium |
| RR-07 | Escaping correctness ultimately rests on templates Gemini writes in P3.4 | Medium |
| RR-08 | Break-glass is a second authentication path and therefore a second surface | Medium |
| RR-10 | OD-25 (Foundry ports possibly reachable directly) is **still open** and shares this host. Phase 3 does not address it and P3.0 claims nothing about it | Medium |
| RR-11 | The bot remains unauthorized until Phase 5 (OD-17). Neither widened nor closed here | High |
| RR-12 | Assistive-technology evidence for the portal does not exist and is **not yet scheduled** | Medium |

## 7. Conflicts and findings

Reported rather than silently resolved, as the prompt requires.

| # | Finding | Disposition |
|---|---|---|
| **F-1** | **A naive identity migration is impossible.** Backfilling an account column on `audit_events` is an `UPDATE` on an append-only table whose trigger refuses it even for the schema owner. Dropping the trigger to run it would be the single most damaging thing this package could do | **Resolved by design, not by exception:** history is never rewritten, a `NOT VALID` check covers new writes without touching existing rows, and reads resolve through `external_identities`. No integrity control is suspended at any point |
| **F-2** | **The apply is as slow as the preview and has never been measured** | Recorded as D-2 and RAID R-28; apply becomes a durable job and P3.3 must measure it |
| **F-3** | **The accepted CSP would have broken the Discord redirect** had OAuth start been a form `POST` | Resolved without weakening N-26 (decision 3). The alternative — adding `https://discord.com` to `form-action` — is recorded as requiring documented security review if the chosen approach proves unworkable |
| **F-4** | **Four screens have no frozen prototype page:** identity migration, role-capability administration, account identities and audit search. The frozen baseline's `council-approval.html` is a **Phase 6** approval-centre concept, which delivery plan §4 excludes from Phase 3 | Recorded in the view-model contract §10. P3.4 extends the accepted visual language rather than adapting an accepted page, and Peter's P3.G4 acceptance covers new work in those four cases. **No change to the accepted visual baseline is requested** |
| **F-5** | **The RAID register has duplicate risk IDs.** `R-10`, `R-11` and `R-12` are each used twice — once for Phase 2 I-03 artifact/credential/exporter risks and once for requirements growth, legacy drift and mis-assigned migration | **Not fixed by P3.0.** Renumbering would rewrite identifiers cited in accepted Phase 2 records. It is a register-integrity defect for the Delivery Lead to resolve deliberately |
| **F-6** | `docs/operations/topology.md` §5 sketches configuration names (`PUBLIC_BASE_URL`, `SESSION_SECRET`, `DISCORD_OAUTH_REDIRECT_URI`, `COUNCIL_ROLE_ID`, `DM_ROLE_IDS`) that the P3.0 contract supersedes: the redirect path is now fixed by N-02, secrets are split by purpose, and role snowflakes are database mappings rather than configuration (OD-18) | Recorded in the configuration contract §2.5. Topology §5 is a proposal document, not an accepted contract, so **nothing accepted is superseded** |
| **F-7** | Delivery plan §7 sets no rate limit for break-glass endpoints, while §9.7 requires break-glass attempts to be rate limited | Closed by proposing N-32/N-33 (part of D-4) |
| **F-8** | The protected administrator **mapping** is inserted by migration, but the protected **account** cannot exist until the administrator first authenticates or a credential is enrolled | Recorded as assumption A-05 with startup check S-15 and a health-check report |

No conflict was found between the accepted plan, the ADRs, the open decisions and
the repository that required stopping work on a point.

## 8. Commands run, and their exact outcomes

Everything below was run from `/opt/discord-bots/freedom-bot` on 2026-08-13.

| Command | Outcome |
|---|---|
| `git status --short` (before editing) | Clean tree on branch `docs/platform-plan`; no unrelated work to preserve |
| `git diff --check` | **No output; exit status 0.** No whitespace or conflict-marker defects |
| `git status --short` (after) | 5 modified files, 2 untracked paths — exactly the inventory in §2 |
| `sha256sum --check docs/review/phase-3-visual-freeze-manifest.sha256` | **14 of 14 `OK`, zero failures.** The frozen visual baseline is untouched |
| `./venv/bin/python -m pytest -q` | **1968 passed, 253 skipped, 1 warning, 10.95 s.** No failures |
| Local Markdown link check over every created and changed file (ad-hoc Python, relative-link existence) | One broken link at the time of checking — `../review/phase-3-p3-0-submission.md`, this file, which did not yet exist. One false positive from a pre-existing percent-encoded path in `change-log.md`. No other broken link |
| Secret-shape scan over the new documents (`grep -E` for DSNs, tokens, PEM headers, `client_secret`, `password=`) | No match |

Notes on the test run, stated precisely:

- **All 253 skips are `TEST_DATABASE_URL is not configured`**, the disposable
  PostgreSQL condition the delivery plan §10 already records as *"must be
  re-confirmed before P3.1"*. P3.0 changed no code, so the skip set is unchanged
  by this package. **No database evidence is claimed.**
- The single warning is a pre-existing `audioop` deprecation from Pycord, unrelated
  to this package.
- The repository-local documentation check that exists — `tests/test_field_ownership_document.py`,
  which validates the field-ownership matrix against the profile and the
  controlled migration manifest — passed. `tests/test_rejected_scope_absent.py`,
  which asserts the rejected ADR 0008 scope stays absent, also passed.
- No tooling was installed to satisfy this package. The design-prototype tools
  (`check_css_tokens.py`, `calc_contrast.py`) were **not** re-run: this package
  changes no prototype file, and the freeze manifest already proves that.

## 9. Confirmation of boundaries

I confirm, and the diff in §2 is the evidence:

- **No runtime implementation.** No module, class, function or template was
  added or changed. No protected route exists.
- **No migration.** No file under `migrations/` was created or edited. Every
  schema statement in this package is a design in a Markdown document.
- **No dependency.** `requirements.txt` and `requirements-dev.txt` are unchanged;
  nothing was installed; no virtualenv was created.
- **No web framework scaffold.** FastAPI is proposed, not imported.
- **No service, no deployment, no start.** No systemd unit, no Caddy change,
  nothing started or stopped.
- **No Discord contact, no OAuth application registered, no production data
  accessed, no secret inspected.** `.env` was never read or printed.
- **No frozen prototype file altered**, verified by the manifest.
- **P3.1 has not started**, and Gemini has not been asked to begin production
  integration.
- **Nothing is marked accepted.** P3.G0 is open, P3.1 is unauthorized, Phase 3 is
  not implemented, and no claim is made that the production portal is secure.

## 10. Review request

**To Codex, as Independent Reviewer**, an architecture/integration pass over:

1. the closed route set and the seven-role matrices — particularly whether any
   route grants more than its row claims, and whether the `403`/`404` split leaks;
2. the identity migration's four stages, its six control totals, and specifically
   whether F-1's `NOT VALID` approach preserves the append-only guarantee;
3. the job state machine against delivery plan §8's nine invariants, especially
   the requeue-during-slow-attempt window in SM-05;
4. the D-1 worker conclusion — is the GIL argument correct, and is the evidence
   sufficient to justify a new service?
5. the view-model contract's boundedness and its fitness to be frozen for Gemini.

**To Codex, in a distinct security-focused pass**, over:

1. the threat model's completeness — what is missing from the 53 entries;
2. break-glass: whether N-12, N-65 and the `auth_method` short-circuit are
   genuinely redundant, and whether host-local-only issuance and enrollment hold;
3. the OAuth flow: state/PKCE binding, the `GET`-start login-CSRF argument, the
   return-target allowlist, and the CSP conclusion in F-3;
4. session, CSRF derivation, rotation and revocation;
5. whether any contract permits raw snapshot bytes, tokens, grants or another
   player's data to reach a response, a log or an audit payload.

**To Peter, as Acceptance Authority and accountable Security Reviewer:** the five
decisions in §1, after both reviews.

---

P3.0 submitted for Codex review and Peter's P3.G0 decision; P3.1 has not started.
