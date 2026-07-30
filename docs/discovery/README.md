# Phase 0 — Discovery and Architecture

Status: **All eight deliverables and all four acceptance criteria are met.** The
maintainer accepted ADRs 0001–0007 on **2026-07-30**. The independent Codex
re-review subsequently approved the architecture and data handling, and the
maintainer accepted Phase 0. The gate is closed and Phase 1 is authorized.

Both production-shape deliverables are now **verified** rather than inferred — the Sheet
inventory against the maintainer's description of all 38 columns plus the player tab, and
the Foundry mapping against two real Actor exports. That verification produced twelve
corrections and uncovered a **live data-loss defect in column W**, now fixed — see
[phase-0-handoff.md §4.6](phase-0-handoff.md#46-column-w-was-silently-destroying-crp-data-on-every-craft--fixed).

The two Actor exports were read for structure only. They were **never committed**, are
now held outside the repository, and `.gitignore` carries a narrow `fvtt-Actor-*.json`
rule to keep it that way.

**Nothing is committed.**

Scope note: Phase 0 is a discovery and design milestone. Production **behaviour** was
changed only twice, both explicitly scoped and maintainer-authorised: the five rule
corrections of 2026-07-29, and the column W data-loss fix of 2026-07-30. Since then the
only code changes have been additive or documentary — the fixture-validation tests, and
one comment in `models/skills.py` recording OD-34 as ruled. No web framework, database
schema, migration or integration was implemented — those belong to Phase 1 and later,
behind this gate.

## Deliverables

Plan §12 Phase 0 requires eight deliverables:

| Required deliverable | Document | Status |
|---|---|---|
| Sheet schema/formula inventory | [sheet-inventory.md](sheet-inventory.md) | **Verified 2026-07-30** — all 38 real headers, the player tab, no formulas but two active macros |
| Command/use-case inventory | [command-inventory.md](command-inventory.md) | Complete |
| Foundry field samples and mapping | [foundry-mapping.md](foundry-mapping.md) | **Verified 2026-07-30** against two real Actor exports; five corrections |
| Rule catalogue with PDF references | [../rules/rule-catalogue.md](../rules/rule-catalogue.md) | Complete |
| Field-ownership draft | [../rules/field-ownership.md](../rules/field-ownership.md) | Complete as a draft |
| Initial ADRs | [../adr/](../adr/README.md) | **All seven `Accepted` 2026-07-30** |
| Anonymized fixtures | [fixture-strategy.md](fixture-strategy.md), `tests/fixtures/` | **Complete 2026-07-30.** Both fixtures regenerated against the verified structure, a third added for the must-fail cases, and all three validated by `tests/test_fixtures.py` |
| Documented local/staging topology | [../operations/topology.md](../operations/topology.md) | Complete |

Plus, from the acceptance criteria and plan §16.3:

| Item | Document |
|---|---|
| Unresolved decisions, listed explicitly | [open-decisions.md](open-decisions.md) |
| Milestone handoff (maintainer-facing) | [phase-0-handoff.md](phase-0-handoff.md) |
| Review submission (reviewer-facing) | [../review/phase-0-submission.md](../review/phase-0-submission.md) |

## Reading order

For a maintainer reviewing this milestone:

1. **[phase-0-handoff.md](phase-0-handoff.md)** — what was done, what was found,
   what is needed. Start here.

   *Reviewers:* use [../review/phase-0-submission.md](../review/phase-0-submission.md)
   instead. It states the same work without nominating focus areas, so an
   independent review is not steered by the author's framing. The handoff's §10
   does nominate focus areas and is best read only after forming your own view.
2. **[open-decisions.md](open-decisions.md)** — 36 decisions, ordered by what they
   block. **Sixteen closed** across 2026-07-29/30. The substantive ones still open are
   **OD-15** (who owns character level), **OD-36** (the two live sheet macros at
   cutover), and the Phase 3 authorization parameters.
3. **[../rules/rule-catalogue.md](../rules/rule-catalogue.md)** — every rule in
   the PDF with page citations and implementation status, including the five
   mismatches corrected under the 2026-07-29 ruling.
4. **[command-inventory.md](command-inventory.md)** — §4 and §5 are the
   data-integrity and authorization findings.
5. **[../adr/](../adr/README.md)** — seven proposed architecture decisions, with a
   [per-ADR approval checklist](../adr/README.md#maintainer-approval-checklist-phase-0-gate).

## Provenance

Everything in these documents comes from one of:

- reading the repository's source, tests and configuration templates;
- reading `Freedom Blades - Homebrew Rules.pdf` (cited by section and page);
- reading Foundry **manifest** files (`world.json`, `system.json`) — configuration
  metadata, no player or character data;
- observing process, port and reverse-proxy configuration on this host.

- **maintainer statements of fact** about the sheet, the rules and the Foundry
  deployment, given on 2026-07-29 and 2026-07-30 and attributed where used;
- **two real Foundry Actor exports**, supplied by the maintainer on 2026-07-30 and
  read for **structural verification only** — field paths, presence/absence of
  derived values, key vocabularies, document size. No value from either export is
  reproduced in this repository, neither file was committed, and both are now held
  outside it.

Nothing came from the live Google Sheet, a Foundry world database, or any Discord
guild. No `.env`, credential or key material was read. No live service was
modified.

**On the Actor exports and the "no real player records" criterion.** The criterion
is *"no secrets or real player records are **committed**"* (plan §12), and that
holds: the fixtures are synthetic by construction and the exports are outside the
repository. But it would be wrong to read this section as saying no real character
data was ever *opened* — two real Actor documents were, deliberately and with the
maintainer supplying them, which is what turned §4 of
[foundry-mapping.md](foundry-mapping.md) from a proposal into verified fact. The
maintainer has confirmed the game data is fictional characters rather than personal
information; the one genuine exception in the whole discovery is `Characters` column
**C**, which holds real player names and stays out of fixtures.

Where a document states a proposal rather than an observation — chiefly
[foundry-mapping.md §4](foundry-mapping.md#4-field-mapping) — it says so in place.

**Two Phase 0 conclusions drawn from code alone turned out to be wrong**, and both
are corrected in place with the original reasoning retained: the three-Foundry-world
finding (one shared bind mount, not three copies) and the column W CRP format (which
was also destroying data). Where this documentation now rests on a maintainer
statement rather than on inference, it says which.
