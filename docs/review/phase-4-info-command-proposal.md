# Phase 4 — proposal: exercise the shared query without rewiring `/info`

**Date:** 2026-08-28
**Raised by:** Peter Duscha, Product Owner
**Written by:** Claude, working Technical Lead for Phase 4
**For review by:** Codex, who co-authored the implementation plan
**Status: superseded by Peter Duscha's final OD-52 amendment on 2026-08-29.**
Neither alternative in this document is implemented: Phase 4 does not rewire
`/info` and does not build the adapter-only query compromise. Package 5.2
introduces the wallet query and production adapter with the character page as
their real consumer. WP-0 and WP-1 are unaffected.

This is deliberately a two-sided document. The Product Owner asked for Codex's
view precisely because Codex helped design the criterion this proposal would
amend, and may hold reasons for it that are not visible from the code. §4 and
§10 are written to make disagreement easy rather than polite.

---

## 1. The question

Implementation-plan §12 Phase 4 lists as a deliverable and acceptance criterion:

> first read-only bot command using the new application layer

The handover expands it as task 6: route one bounded money/resource query
through the shared application service, preserving command name, authorization,
privacy, response timing, error safety and visible result, with the Sheet
adapter as temporary backing.

`/info` is the only read-only command in `ext/commands/`; everything else
writes. So the criterion resolves to `/info`, and OD-52 ruled how: one query,
with only the money and resource block typed.

The Product Owner's question is the obvious one. **OD-53 retires the Freedom
bot. Why refine a command that is scheduled for deletion?**

---

## 2. The proposal

Split what is currently one work package (WP-5) into the part that carries the
engineering value and the part that does not, and do only the first.

**Keep — build the Sheet-backed read adapter and its contract tests.** A real
implementation of the money/resource query protocol, reading the real
`Characters` column layout through a fake Sheets *client*, exercised against the
real cases: the four denomination counters, an out-of-unit downtime value, an
unparseable cell, a missing row, an ambiguous name. This is where the query
protocol meets reality and where a wrong abstraction shows up.

**Drop — rewiring `/info` to call it.** `ext/commands/info.py` stays exactly as
it is until package 5.1 replaces it or §15.2 deletes it.

**Amend §12 Phase 4's criterion** under §0.2 from *"first read-only bot command
using the new application layer"* to something closer to *"the shared read query
implemented against the real Sheet-era data shapes, with adapter contract
tests"*, and record the reasoning.

Estimated effect on WP-5: from 0.5 / 1.0 / 2.0 implementer-days to roughly
0.5 / 0.75 / 1.5. **This is not primarily a saving.** A quarter-day is not worth
a baseline amendment; the argument has to stand on ownership and risk, or not
at all.

---

## 3. The case for

**3.1 Package 5.1 already owns `/info`.** The Phase 5 table names it
outright — *"5.1 Character profile and `/info`"* — and makes 5.1 accountable for
that command's typed schema, package-owned Sheet migration, reconciliation and
database-backed read path with linked-character authorization. Phase 4 rewiring
the same command puts two packages' hands on it. This project's register rules
treat single accountable ownership as load-bearing, and the plan states that a
register row may never have two write-authoritative targets. `/info` is not a
register row, so this is an analogy rather than a rule violation — but the
instinct behind the rule applies.

**3.2 It is work on something being deleted.** OD-53 retires the bot; §15.2
gates the deletion. Effort spent making `/info` internally tidy produces no
player-visible benefit at any point in its remaining life.

**3.3 The characterization tests do not depend on it.**
`tests/test_p4_characterization.py` pins `/info`'s byte-exact output, its defer
behaviour, its ephemerality, its refusals and the fact that it writes nothing.
Those 36 tests are a regression guard for **whoever** eventually changes the
command — 5.1 or §15.2 — and they hold whether or not Phase 4 touches it.

**3.4 The value is in the adapter, not the wiring.** What could be wrong with
the Phase 4 abstraction is the *query protocol's shape*: what it returns, how it
represents an invalid persisted value, whether the typed money survives contact
with four denomination counters. An adapter with contract tests probes all of
that. Rewiring the command probes the composition, which is a smaller and more
predictable question.

---

## 4. The case against — steelmanned

These are the arguments a reviewer should press, and at least two of them are
good.

**4.1 The gate is dependency direction, and only a real entry point demonstrates
it end to end.** Phase 4's gate is not "the domain is correct" — it is
*dependency direction and domain correctness*. Adapter contract tests prove the
adapter. They do not prove that a Discord entry point can be reduced to
parse → authorize → invoke → render with nothing leaking inward. Without one
caller doing exactly that, Phase 4 evidences its central claim by construction
rather than by demonstration. **This is the strongest argument against the
proposal.**

**4.2 It removes a rehearsal that 5.1 and 5.2 would otherwise inherit.** Some
package has to move a live command onto the platform for the first time. Doing
it once, on the simplest read-only command, in the phase whose entire purpose is
establishing the pattern, is cheaper than doing it first under mutation
pressure in 5.2. Deferring means the first command migration ever attempted is
also one that writes.

**4.3 `.agents/AGENTS.md` forbids abstractions without a real consumer.** A
fake-client contract test is a test, not a consumer. Under the strict reading,
the proposal leaves Phase 4's entire output — value objects, protocols, ledger,
idempotent executor — with no production caller at all.

**4.4 The saving is trivial and the amendment is not free.** A quarter of a day
against a §0.2 baseline amendment, a change-log entry and a decision record is a
poor trade if the criterion is otherwise sound.

**4.5 The 5.1 ownership argument may be weaker than it looks.** Phase 4's change
is a *layering* change with the Sheet still backing; 5.1's is a *migration*,
adding a database-backed read path and linked-character authorization. Those are
different work on the same file, and the plan may well have intended exactly
that sequence — Phase 4 does the layering, 5.1 does the migration on top of it.
If so, §3.1 describes the design working as designed rather than a conflict.

---

## 5. Where the proposal's original framing was wrong

Stated plainly, because it was argued to the Product Owner before it was
checked.

The case was first put partly on **regression risk to a live system**. That is
overstated. Phase 4 explicitly excludes deployment, service restarts and
production configuration changes: a rewired `/info` would sit in the repository
behind a separate deployment gate, not on the running bot. It would also sit
behind 36 characterization tests pinning its output byte for byte. The honest
cost of rewiring is **effort on something scheduled for deletion**, not risk to
players.

That correction removes one of the two original arguments. What remains is §3.1
and §3.2, and §4.5 contests §3.1. A reviewer who finds §4.1 persuasive should
reject this proposal, and the author would not regard that as a bad outcome.

---

## 6. What is not being proposed

- **Not** dropping the money/resource query, the protocol, or the adapter.
- **Not** dropping WP-3's ledger or WP-4's durable idempotency.
- **Not** changing OD-48, OD-49, OD-50, OD-51 or the domain work already
  delivered in WP-1.
- **Not** touching, disabling or degrading `/info` — under the corrected
  `.agents/AGENTS.md` rule the bot is untouchable until the platform is fully
  functional, and this proposal leaves it strictly more untouched than the
  current plan does.
- **Not** a Phase 5 authorization of any kind.

---

## 7. Cost of the amendment

Under §0.2 an acceptance-criterion change needs a change-log entry with
requester and reason, an impact assessment, a Product Owner recommendation, a
Technical Lead review and Acceptance Authority approval. It does **not** need a
new baseline version: no roadmap, phase order or release boundary moves. The
package plan's §11.1 traceability row and WP-5's estimate would be reissued.

If the proposal is rejected, nothing needs undoing — WP-5 proceeds as OD-52
already rules.

---

## 8. Separate and independent — sequencing 5.2 first

This is **not** part of the proposal and can be decided on its own. It is
recorded here because it follows from the same reasoning and is probably worth
more than the proposal is.

`/info` exists because checking the Sheet was inconvenient. The platform
replaces it — but **not yet**: the portal renders every money field as
`MigrationDeferred`, a view-model type with no value field, so a player looking
up their character today sees *"migration deferred (package 5.2)"* where their
coins should be (`tests/web/test_p3_4_member_views.py:703`).

**Package 5.2 is what changes that**, and it has an unusually clean path:

| Package | Predecessors | Open rule decisions blocking it |
|---|---|---|
| 5.1 Character profile and `/info` | Phase 3 gate, 5.0, OD-16/17 | none — OD-16/17 closed 2026-08-12 |
| **5.2 Wallet and `/xchange`** | **5.0 only** | **none** |
| 5.3 Lifestyle | 5.0, effective-dated history | OD-03, OD-04 |
| 5.5 Learning | 5.0 | OD-09, OD-28 |
| 5.7 Sales | 5.0, 5.6a | OD-39 |

5.2 is the only economy package with no unresolved rule decision in front of it,
and it is the one that puts money on the portal. Proposal: **after 5.0, schedule
5.2 first.** Open question for the reviewer: does making the portal *display* a
migrated wallet fall inside 5.2's read path, or does it need a separate portal
change with its own view-model contract amendment?

---

## 9. Decision requested

**Final disposition:** `/info` is not a platform feature, but the adapter-only
proposal is also rejected because it has no real production consumer. Package
5.2 owns the wallet query and adapter. Phase 5 order remains unchanged.

1. Amend §12 Phase 4's read-only-command criterion as in §2, or keep it as it
   stands and proceed with WP-5 under OD-52?
2. Independently: schedule 5.2 first among the Phase 5 packages after 5.0?

Neither decision blocks current work. WP-2, WP-3 and WP-4 are unaffected and
proceed either way.

---

## 10. Questions specifically for Codex

1. **Was the read-only-command criterion chosen for a reason not visible in the
   plan text?** It is the only Phase 4 criterion naming a concrete production
   artifact rather than a property, which suggests deliberate intent.
2. **Is §4.1 decisive?** Is there any evidence short of a real caller that would
   satisfy a dependency-direction gate — and if not, does that make the
   criterion unamendable in practice?
3. **Is §3.1 or §4.5 the better reading of the 5.1/Phase 4 boundary?** Did the
   plan intend Phase 4 to do the layering and 5.1 the migration on top?
4. **If the criterion stands, should OD-52's scope shrink further** — for
   example, `/info` calling the query while the *rendering* stays untouched in
   `helpers/renderers.py`, so 5.1 inherits an unmodified presentation layer?
5. **Does OD-53 change the answer at all**, or is a command's scheduled deletion
   simply irrelevant to whether the phase that precedes it has proved its own
   gate?
