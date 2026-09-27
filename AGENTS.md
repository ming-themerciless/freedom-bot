# Freedom Blades Platform — Agent Entry Point

Before planning, reviewing, or changing anything in this repository, read:

1. `.agents/AGENTS.md` **completely** — the canonical, always-applicable
   working agreement. It is short and must not be bypassed.
2. `docs/implementation-plan.md` — the approved roadmap, milestones, acceptance
   criteria and review gates. Read its **reading map** at the top, then §0, §16
   and §20, then the sections your task touches. It is cited by section number
   from roughly 126 other documents and is deliberately not split into
   per-phase files.
3. `docs/review/Handover information` — the **active assignment and its
   restrictions**. A task-specific restriction overrides the general
   environment and test-server instructions, and several are usually in force.
   This is a concise current-state entry point; consumed and superseded material
   is indexed under `docs/review/handover-archive/`.
4. `docs/operations/disposable-test-server.md` — the dedicated disposable Linux
   test environment (`oracle-test` / `138.2.182.39`) where agents have full
   administrative (root) access for isolated test runs and system drills. Check
   its restriction banner before running anything against it.

These documents apply to the entire repository. If they conflict or a requested
change would cross a review gate, stop and ask a maintainer.

Current delivery state is summarized in `docs/project-management/status.md`.
Historical status snapshots are indexed under
`docs/project-management/status-archive/`; archived text is evidence, not
current authority.

The repository location is `/opt/freedom-blades/platform`. For test execution,
follow the canonical agreement and disposable-server document above: the
documented Python environment is `/opt/freedom-blades/runtime/venv-web` on
`oracle-test`, rather than the historical `/opt/discord-bots/` paths.

## Tooling for agents that support it

Claude Code additionally loads `CLAUDE.md`, four procedural skills under
`.claude/skills/` (`run-suites`, `handoff-checklist`, `migration-staging`,
`rules-sourcing`) and two enforced `PreToolUse` guards under `.claude/hooks/`
that refuse secret-file access and Git history rewrites.

**None of that changes the rules.** The skills cite the two governing documents
rather than restating them, no always-applicable rule lives in a skill, and the
guards enforce a subset of what `.agents/AGENTS.md` already requires. An agent
without skill or hook support is held to exactly the same agreement and must
apply it by reading, which is what items 1 to 4 above are for.
