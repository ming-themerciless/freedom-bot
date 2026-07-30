# ADR 0001 — Develop the platform in the existing repository

Status: **Accepted** — approved by the maintainer 2026-07-30. That satisfies the
Phase 0 acceptance criterion *"maintainer approves architecture ADRs"* (plan §12).
The independent Codex review required by plan §16.4 approved Phase 0 on
2026-07-30, and the maintainer accepted the milestone. This ADR is the contract
Phase 1 will be reviewed against.

Date: 2026-07-29

Supersedes: none

## Context

The Freedom Blades platform is an evolution of a live Discord bot backed by
Google Sheets. Implementation plan §2.1 already states the decision; this ADR
records the reasoning so it can be reviewed rather than assumed.

The alternative that teams usually reach for — a clean sibling repository that
eventually replaces the old one — is specifically what the plan forbids, and the
current codebase shows why the constraint matters. Rules logic is not isolated:
`Resource.sale()` performs a rule calculation, mutates state and formats a
Discord message in one method (`models/resource.py:147`); `Actor.load_from_sheet`
couples domain objects to an A1 range (`models/actor.py:75`). A parallel rewrite
would have to re-derive every rule from the same PDF while the original kept
running and drifting.

## Decision

Develop the platform inside this repository.

1. The Discord bot remains a supported adapter and is not deleted.
2. The layout evolves toward plan §2.2 incrementally. A module moves **only**
   when its feature is being migrated and is protected by characterization tests.
3. No mass file move is performed to obtain the target layout.
4. A repository rename is deferred until the database-backed web application runs
   reliably, and is an administrative change.

## Consequences

**Positive.**

- Rules extracted from a live module are validated against that module's own
  characterization tests, not re-derived from scratch.
- The existing 43-test suite keeps running throughout.
- Feature flags can cut a single command over at a time (plan §12 Phase 5) with a
  Sheets rollback path in the same process.

**Negative.**

- The repository holds two architectural generations at once — `models/` with
  Sheet-coupled classes alongside `domain/` and `application/` — for the whole of
  Phases 4–5. Contributors must know which is authoritative for a given feature.
- `application/actor_locks.py` already exists under the target layout while the
  domain does not, so the layout is inconsistent from the start.

**Mitigation.** Every migrated command's entry in
[command-inventory.md §6](../discovery/command-inventory.md#6-proposed-application-services)
records which layer owns it. A module is not "migrated" until the old path is
deleted or flag-guarded.

## Alternatives considered

**New repository, later replacement.** Rejected: forbidden by plan §2.1, and it
would require maintaining two implementations of the same rules against a live
community for months.

**Extract a shared rules library first.** Rejected for now: it adds a packaging
and versioning boundary before there is a second consumer. `.agents/AGENTS.md` —
*"Do not add abstractions without a real consumer"*. Revisit if the Foundry
module ever needs to execute rules client-side, which the current design avoids.
