# Freedom Blades Platform — Claude Code Entry Point

Before planning or implementing any task in this repository, read:

1. `.agents/AGENTS.md` **completely** — the canonical engineering, product,
   safety and contributor rules. It is short, it has no scoped reading, and it
   must not be bypassed.
2. `docs/implementation-plan.md` — the milestone contract and acceptance
   criteria. Read its **reading map** at the top, then §0, §16 and §20, then the
   sections your task actually touches. It is cited by section number from
   roughly 126 other documents and is deliberately not split.
3. `docs/review/Handover information` — the **active task assignment and its
   restrictions**. A task-specific restriction overrides the general
   environment and server instructions, and several are usually in force.

Work only within the approved milestone or explicitly scoped task. Do not
continue past a review gate without the required maintainer and Codex review.
If the documents conflict or a rule, authority, privacy, migration, or
architecture decision is unresolved, stop and ask a maintainer.

## Skills — procedures, invoked when they apply

These live in `.claude/skills/`. Each one **cites** `.agents/AGENTS.md` and
`docs/implementation-plan.md` rather than restating them; where a skill and
either document disagree, the documents win and the disagreement is a defect to
report.

| Skill | Use it when |
|---|---|
| `run-suites` | running tests, verifying a change, or citing suite figures |
| `handoff-checklist` | finishing a slice, writing a handback, or preparing a gate |
| `migration-staging` | touching `migrations/`, the schema, an import or a cutover |
| `rules-sourcing` | changing game behavior, rule tables, rewards or facilities |

A skill applies only when it is invoked, so **no always-applicable rule lives in
one**. Safety rules, product invariants, gate discipline and the test-environment
traps stay in `.agents/AGENTS.md` and are in force whether or not a skill runs.

## Enforced guards — refusals, not reminders

`.claude/settings.json` registers two `PreToolUse` hooks in `.claude/hooks/`.
They turn two rules that were prose into mechanical refusals:

* **`guard-secrets.py`** refuses reads, copies, publications and edits of
  `.env` files, `yt-cookies.txt`, service-account and credential JSON, private
  keys, certificates and `.pgpass`. `.env.example` is exempt and must be kept
  current.
* **`guard-git.py`** refuses history rewrites on any branch — force push, hard
  reset, rebase, amend, filter-branch — and refuses commits and pushes on the
  default branch. Branch first, or let the maintainer publish.

Run `python3 .claude/hooks/test_guards.py` after changing either. It asserts
both directions: 19 calls that must be refused and 12 that must be allowed.

A refusal from a guard is a stop condition, not an obstacle to route around.

## Disposable Linux Test Server (`oracle-test` / `138.2.182.39`)

A dedicated, explicitly disposable Linux test server is available for isolated
test suites and destructive drills, away from production and staging. See
canonical
[`docs/operations/disposable-test-server.md`](docs/operations/disposable-test-server.md)
for environment profiles, synchronization recipes and test commands, and check
its restriction banner before running anything against it. The `run-suites`
skill carries the same procedure with the skip-count and serial-execution traps
that otherwise produce a green run proving nothing.
