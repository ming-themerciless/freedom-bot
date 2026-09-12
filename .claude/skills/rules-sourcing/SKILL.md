---
name: rules-sourcing
description: Identify and cite the authoritative rule before changing Freedom Blades game behavior. Use when touching calculations, rule tables, advancement, rewards, crafting, trade, lifestyle, downtime, bastions or facilities, or when a rule looks ambiguous or sources disagree. Covers the precedence order, citation duty and the no-silent-choice rule.
---

# Sourcing a game rule

**This skill is a procedural aid, not a source of rules.** The authority is
`.agents/AGENTS.md` "Rules sources" and the Bastion and facility sections of
`docs/implementation-plan.md`. If this file disagrees with either, they win.

## Precedence, highest first

1. Explicit Freedom Blades rulings supplied by maintainers.
2. `Freedom Blades - Homebrew Rules.pdf`.
3. Official D&D 2024 / 5.5 rules.
4. Existing behavior, **only** where those sources are silent.

## When sources conflict or are ambiguous

**Do not silently choose.** Preserve current production behavior where that is
safe, document the ambiguity, and ask a maintainer. A rule conflict is a stop
condition, not a judgement call.

## Citation duty

* Tie rule-table comments and tests to a rule name and a PDF page or section
  wherever possible.
* **Do not reproduce copyrighted sourcebooks in this repository.** Cite; do not
  transcribe.
* Each implemented facility must cite its rule source and version, validate
  prerequisites, preview effects, and carry boundary and failure tests.

## Where rule code belongs

Rules are domain policy, not Discord UI code. Calculations, validation, state
transitions and rule tables must be reusable by the Freedom bot, the web app,
tests and Foundry. Keep them out of the adapters.

* Prefer data-driven definitions for declarative facts.
* **Do not introduce an unrestricted expression or scripting language** for
  facility effects. Complex or exceptional behavior belongs in tested domain
  policy objects.
* Use table-driven tests for rule matrices and boundary values.

## Product invariants that override any rule reading

* No advancement, mission settlement, reward or Council-controlled Foundry
  proposal is official until an authorized Guild Council user approves it.
* **There is no automatic advancement.**
* Attendance from Discord voice state is evidence only. It never grants rewards
  or advancement.
* AI may draft or extract proposals. It must never calculate authoritatively or
  apply game state without deterministic validation and required human approval.
