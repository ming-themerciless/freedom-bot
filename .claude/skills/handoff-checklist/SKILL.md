---
name: handoff-checklist
description: Verify and report a change before handing it to a maintainer or reviewer. Use when finishing a milestone or scoped slice, writing a handback or submission, preparing a review gate, or about to claim work is complete. Covers the verification order, the required report contents, and the claims that may not be made.
---

# Handing off a change

**This skill is a procedural aid, not a source of rules.** The authority is
`.agents/AGENTS.md` "Contributor and agent workflow / Before handing off" and
`docs/implementation-plan.md` §16.3 and §16.4. If this file disagrees with
either, they win.

## Verify, in this order

1. Run narrow relevant tests, then the full available suite. Use the
   `run-suites` skill; it carries the skip-count trap and the serial rule.
2. Run the configured formatter, linter and type checker. Distinguish
   **unavailable or unconfigured tooling from a pass** and say which it was.
3. Review the diff for secrets, generated files, unrelated changes, unsafe logs
   and migration reversibility.
4. Check `git status` and confirm unrelated user changes are preserved.
5. Run `git diff --check`.

## Report these, every time

From `.agents/AGENTS.md` and plan §16.3:

* requirements implemented, and requirements **proposed but not implemented**;
* files changed and migrations added;
* security implications;
* **exact commands run, the interpreter used, and the exact results**;
* **checks not run, and why**;
* configuration and deployment changes;
* rollback or recovery steps;
* unresolved questions and assumptions stated as assumptions; and
* proposed reviewer focus areas.

## Claims that may not be made

* **Never claim a check passed unless it was actually run.** A figure from a
  different tree or host is not evidence about this one.
* A passing test of an unfixed tree is a **defect reproduction**, not a passed
  safety invariant. Label it as such.
* Do not close a finding on the implementer's authority. Findings are closed by
  the reviewer or the Acceptance Authority, never by a passing suite.
* Do not treat a green suite as a gate approval, a risk acceptance, or an
  execution authorization.
* Separate **observations, assumptions, proof obligations, proposed decisions
  and unresolved dependencies**. Do not present one as another.

## Then stop

Work sits within one approved milestone or explicitly scoped slice. At the
review gates named in `docs/implementation-plan.md`, provide the complete handoff
and **wait**. Blocking findings involving security, data integrity,
authorization, rule correctness, migrations, atomicity or production reliability
must be fixed and re-reviewed before dependent work continues.

Stop and ask a maintainer when a decision changes architecture, data authority,
authorization, privacy, production behavior, or migration and rollback strategy.
