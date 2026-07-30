# Architecture Decision Records

Material architecture choices are recorded here as short ADRs, per
`.agents/AGENTS.md` ("Do not choose a web or frontend framework as a drive-by
change") and implementation plan §20.

## Status values

| Status | Meaning |
|---|---|
| **Proposed** | Written, not yet accepted. Does **not** authorize implementation |
| **Accepted** | Maintainer-approved. Implementation may proceed |
| **Superseded by NNNN** | Replaced; kept for history |
| **Rejected** | Considered and declined; kept for history |

An ADR is accepted by a maintainer changing its `Status` line. One of Phase 0's four
acceptance criteria is *"maintainer approves architecture ADRs"* (plan §12).

> **All seven ADRs were accepted by the maintainer on 2026-07-30, satisfying that
> criterion.** The independent Codex review named in plan §16.4 approved Phase 0
> on 2026-07-30, and the maintainer accepted the milestone. Phase 1 is cleared to
> start. The ADRs are the contract Phase 1 will be reviewed against.
> Changing an accepted ADR means superseding it with a new one, not editing it in place.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-develop-platform-in-existing-repository.md) | Develop the platform in the existing repository | **Accepted** |
| [0002](0002-web-application-stack.md) | Web application stack | **Accepted** |
| [0003](0003-postgresql-and-alembic.md) | PostgreSQL as the authoritative store, Alembic for migrations | **Accepted** |
| [0004](0004-discord-oauth2-authentication.md) | Discord OAuth2 authentication and server-side sessions | **Accepted** |
| [0005](0005-identifier-and-quantity-representation.md) | Identifier, money and quantity representation | **Accepted** |
| [0006](0006-foundry-integration-boundary.md) | Foundry integration boundary | **Accepted** |
| [0007](0007-field-ownership-and-conflict-policy.md) | Field ownership and conflict policy | **Accepted** |

## Maintainer approval checklist (Phase 0 gate)

Phase 0's acceptance criterion is *"maintainer approves architecture ADRs"* (plan §12).
**It is met: all seven were accepted on 2026-07-30.** The table is retained as the
record of what was decided, what was hard to reverse, and what was still open at the
time of acceptance.

| ADR | Decides | Reversibility once Phase 1 starts | Unresolved choice inside it | Recommendation |
|---|---|---|---|---|
| **0001** Repository | Evolve in place; bot stays a supported adapter; no mass file move | Easy | None | **Accept.** It records what plan §2.1 already mandates |
| **0002** Web stack | FastAPI + Jinja2 + vendored HTMX, no npm; Caddy; two processes (`freedom-web`, `freedom-bot`) | Hard after scaffolding | Django was genuinely competitive — it would supply sessions/CSRF/admin that FastAPI makes you build. Rejected for dependency-direction reasons | **Accept.** But note it creates the Phase 3 security work list itself (CSRF, CSP, cookie flags, CORS, rate limits) |
| **0003** PostgreSQL + Alembic | PostgreSQL authoritative; SQLAlchemy 2.x with explicit mapping; Alembic; schema conventions; **IDs assigned at row creation, idempotency from mapping constraints**; one-use-case-one-transaction; restricted DB role | **Very hard** — the conventions are what every migration is reviewed against | **None left.** [OD-35](../discovery/open-decisions.md) was ruled on 2026-07-30 and the ADR is amended | **Accept.** Re-read §"Identifier assignment and import idempotency" — it is new |
| **0004** OAuth2 + sessions | Discord OAuth2 + PKCE, scopes `identify` + `guilds.members.read`, server-side sessions, capabilities from role **IDs**, `character_access` separate from role, fail-closed on Discord outage | Moderate | Retention periods ([OD-23](../discovery/open-decisions.md)), role snowflakes ([OD-18](../discovery/open-decisions.md)), break-glass admin ([OD-24](../discovery/open-decisions.md)) — all parameters, not architecture | **Accept.** The three open questions can be answered during Phase 3 without reopening the ADR |
| **0005** IDs, money, quantities | Integer copper; **thousandth-day** downtime (revised 2026-07-30, was eighth-day); tenth-point CRP; artisan codes not free text; entity equality by UUID; rounding stated per calculation | **Very hard** — a unit change means rewriting applied migrations | **None left.** [OD-08](../discovery/open-decisions.md) is ruled — crafting days round to one decimal, so eighth-days is withdrawn — and its residual closed the same day: the fixed `0.25` / `0.125` master-tier constants are charged **exactly**, confirming thousandths. OD-35, which it inherited, is also ruled | **Accepted** after that amendment |
| **0006** Foundry boundary | External client only; no LevelDB in production; **the world is the identity and the instance is a transport endpoint**; (core, system) tuple pinned to the deployed versions, fail closed; read-only snapshots first; one service principal; Council-established mapping | Moderate | **None left.** OD-12 and OD-14 were both closed on 2026-07-30 and this ADR was revised accordingly | **Accept.** Re-read §"The world is the identity" and §"Idempotency" first — both changed materially on 2026-07-30 |
| **0007** Field ownership policy | One recorded owner per field; unlisted ⇒ database-owned and never overwritten; ownership is versioned data, not code; no silent last-write-wins; no import writes a live record; ownership changes are Council decisions | Moderate | The matrix itself still has 7 UNRESOLVED groups ([field-ownership.md §10](../rules/field-ownership.md#10-unresolved-summary)) — but the *policy* stands independently | **Accept the policy.** The matrix rows stay open until write-enablement |

Two ADRs are hard to reverse and deserve the most attention: **0003** (schema
conventions) and **0005** (smallest units). Both had an unresolved choice inside them,
and both were settled *before* acceptance: OD-35 for 0003, and OD-08 for 0005 —
including the master-tier rounding residual, which closed the same day and confirmed
thousandth-days. Neither carries an open internal choice now.

**Revision history, 2026-07-30.** Three ADRs were amended on maintainer answers before
acceptance, each recorded in place with the withdrawn reasoning kept rather than
deleted:

- **0003** — the identifier contradiction resolved: IDs are assigned at row creation,
  and import idempotency comes from mapping-table constraints.
- **0005** — eighth-days withdrawn in favour of **thousandth-days**, then confirmed by
  the maintainer's follow-up (*"make the number exact, round after three digits"*),
  which makes the unit and the rounding rule agree exactly.
- **0006** — one shared Foundry world rather than three; snapshot idempotency re-keyed
  off the instance; one service principal rather than three.

**All seven accepted 2026-07-30.** No residual questions remain inside any of them.

## Format

Context → Decision → Consequences → Alternatives considered. Keep them short;
the reasoning matters more than the prose.
