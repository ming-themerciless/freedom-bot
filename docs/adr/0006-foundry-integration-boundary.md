# ADR 0006 — Foundry integration boundary

Status: **Accepted** — approved by the maintainer 2026-07-30. That satisfies the
Phase 0 acceptance criterion *"maintainer approves architecture ADRs"* (plan §12).
The independent Codex review required by plan §16.4 approved Phase 0 on
2026-07-30, and the maintainer accepted the milestone. This ADR is the contract
Phase 1 will be reviewed against.

Date: 2026-07-29

## Context

Plan §6.3 and §12 Phase 7 require a narrow, authenticated, versioned Foundry
integration. `.agents/AGENTS.md` forbids direct LevelDB reads or writes as the
production integration.

Phase 0 discovery ([foundry-mapping.md](../discovery/foundry-mapping.md)) confirmed
the deployment baseline from the manifests — world `the-guild`, title `The Guild`,
core `14.365`, system `dnd5e` `5.3.3` — and found one thing the plan did not
anticipate: **three Foundry instances run on this host**, on ports 30001–30003,
each exposing a world directory named `the-guild`. Phase 0 initially read that as
three separate worlds; the maintainer clarified on 2026-07-30 that
`/home/foundry/shared/worlds` is bind-mounted into all three, so it is **one world
with three front doors**. The decisions below reflect the corrected topology.

It also confirmed that all three world databases are held open by running
servers, which makes an offline snapshot read unsafe as well as unauthorized.

## Decision

### Foundry is an external client

It never receives a database credential, a database connection, or any secret
beyond its own scoped service-principal token. Data flows through a versioned
HTTPS API that this application exposes and the Foundry module consumes.

```text
Foundry module ──HTTPS──> /api/v1/foundry/* ──> application services ──> domain
     (client)              (this application)
```

The module is a client of the platform. The platform is never a client of
Foundry's internals.

### No LevelDB access in production, in either direction

Not for reads, not for writes, not "just for the import". The world stores are
live. An offline read-only snapshot is permitted **only** for
maintainer-authorized discovery (`.agents/AGENTS.md`) and never as a production
code path.

### The world is the identity; the instance is a transport endpoint

*Revised 2026-07-30 on a maintainer answer, which corrected the topology this
section originally assumed.* Phase 0 reported three instances each holding a
`the-guild` world and concluded that an authoritative instance had to be chosen.
That was wrong: `/home/foundry/shared/worlds` is bind-mounted into all three
instances, so there is **one** world seen three times (verified by inode; see
[foundry-mapping.md §3](../discovery/foundry-mapping.md#3-topology-one-shared-world-behind-three-instances)).

Therefore:

- `external_worlds` keys on **world ID**, not (instance, world ID). There is no
  stale parallel copy to guard against, and composing the instance into the
  identity would falsely split one world into three.
- The instance is **connection configuration** — a base URL. It must be
  repointable without any change to world or actor identity, because LevelDB's
  exclusive lock means only one instance can host the world at a time and it need
  not always be the same one.
- **One service principal**, not three, because there is one world.

[OD-12](../discovery/open-decisions.md) is closed by this correction rather than
by a choice.

### Version compatibility is a tuple, and mismatch fails safely

Compatibility is keyed on **(core version, system version)** together. The
manifests give `core 14.365` with the system declaring `compatibility.verified:
"14"` and `minimum: "13.347"` — neither value alone identifies a supported
deployment.

Every request carries both versions and the API schema version. An unsupported
combination **fails the sync with a clear diagnostic**. It does not degrade, does
not guess, and does not partially import. Plan §12 Phase 7: *"unsupported
versions fail safely."*

**Supported range, decided 2026-07-30 ([OD-14](../discovery/open-decisions.md)):**
exactly the deployed tuple — core `14.365`, `dnd5e` `5.3.3` — held in
configuration rather than hard-coded. This connector serves **one deployment and
is not distributed**, so no backwards compatibility is owed. A Foundry or system
upgrade deliberately stops the sync until the new tuple is validated and the
configured value updated; that visible checkpoint is the feature. The per-instance
upgrade path makes this concrete: one instance can be upgraded against the shared
world while the others are not, so the connector can meet an unexpected tuple even
though the world itself never changed.

### One-way, read-only first

Phase 7 delivers **snapshots into the platform only**. No write to Foundry, for
any field, before Phase 7's review gate closes and
[field-ownership.md](../rules/field-ownership.md) has no UNRESOLVED rows.

An imported value lands in `sync_snapshots` and generates `sync_differences`. It
does not update a live character record. Applying a difference is a Council
action through the approval centre (plan §12 Phase 6).

### Idempotency

A snapshot is keyed on **(world ID, actor `_id`, content hash)** — *revised
2026-07-30; the instance is deliberately not part of the key.* Including it would
mean the same unchanged actor, submitted through a different front door to the same
shared world, counted as a new snapshot. Idempotency must hold across instances,
because there is only one world behind them.
Re-submitting an identical snapshot is a no-op that returns the original result.
Plan §12 Phase 7: *"duplicate snapshots are idempotent."*

The Foundry actor `_id` is a **mapping key, not an identity**. It does not survive
a world rebuild, so `external_actor_mappings` also stores a human-verifiable
fingerprint — name plus class and level at mapping time — to support re-linking
after one.

### Credentials

**One service principal for the Foundry connector** — revised 2026-07-30 from
"one per instance", since there is one shared world rather than three. It is
scoped to snapshot submission only, revocable, and rotatable without redeploying
the application. No administrator credential and no database secret is ever
shipped in a Foundry module — the module runs on clients the platform does not
control.

### Mapping is Council-established, never inferred

A Foundry actor is linked to a platform character by an explicit, audited Council
action. Never by name matching. Names are mutable display values, and the Sheet's
name-based lookup already demonstrates the failure mode.

This makes Council character-link management (plan §12 Phase 3) a hard
prerequisite for Phase 7 — which the plan's phase ordering already reflects.

## Consequences

**Positive.**

- Foundry compromise or misconfiguration cannot corrupt platform state: the worst
  case is a rejected or quarantined snapshot.
- Version mismatches surface as diagnostics rather than as silently wrong
  imports.
- Keying identity on the world rather than the instance means the connector is
  unaffected by which instance happens to be hosting `the-guild`.

**Negative.**

- A Foundry module must be written, versioned and kept compatible across Foundry
  upgrades. That is real ongoing maintenance the project does not have today —
  though the single-deployment version policy above bounds it: the module is not
  distributed and owes no third party compatibility.
- Pinning to one (core, system) tuple means a Foundry upgrade **stops the sync
  until the pin is updated.** Deliberate, but it must be on the upgrade checklist
  or it will be discovered at the wrong moment.
- Read-only first means players see reconciliation differences they cannot fix
  from Foundry. That is intended — it is the Council's queue — but it needs
  explaining to the community.
- Bastion facility data in Foundry is **incompletely maintained** — not every player
  fills it in (maintainer, 2026-07-30). A Foundry snapshot is therefore evidence of
  what *is* recorded, never proof of what exists, and no rule check may treat an
  absent facility as an absent facility.

## Alternatives considered

**Offline LevelDB snapshot import.** Tempting: no module to write, no Foundry
API to learn. Rejected — forbidden by `.agents/AGENTS.md` for production, the
databases are open, and it would couple the platform to Foundry's internal
storage format across versions.

**Foundry REST API module from the ecosystem.** A general-purpose remote-access
module would grant far broader access than snapshot submission needs, and its
credential would be a standing key to the whole world. A purpose-built module
with one narrow capability is a much smaller thing to get wrong.

**Bidirectional sync from the start.** Rejected: `.agents/AGENTS.md` requires
field-level ownership rules and conflict resolution first, and
[field-ownership.md §10](../rules/field-ownership.md#10-unresolved-summary) still
has seven unresolved groups.

**Composing the instance into world identity.** This was the original decision,
made on the belief that three separate `the-guild` worlds existed. **Withdrawn
2026-07-30**: the world is bind-mounted and shared, so keying on
(instance, world ID) would split one world into three phantom identities and
generate spurious `sync_differences` between them. Recorded here rather than
deleted, because the reasoning was sound and only the premise was wrong — and
because it is a good illustration of why §7 of
[foundry-mapping.md](../discovery/foundry-mapping.md#7-what-a-maintainer-must-supply)
insists on maintainer-verified structure instead of agent inference.
