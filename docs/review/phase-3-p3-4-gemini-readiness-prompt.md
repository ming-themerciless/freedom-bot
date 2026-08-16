# Prompt for Gemini — read-only P3.4 frontend integration readiness analysis

Gemini, prepare a durable readiness analysis for the future Phase 3 package P3.4
(production frontend integration). This is planning and contract analysis only.
P3.G1 remains open, P3.2 and P3.3 have not been implemented, and the P3.G2/P3.G3
view-model freeze gates have not closed. You are **not authorized to begin P3.4
implementation**.

Your output should make later P3.4 work faster and safer without changing any
runtime behavior, accepted contract, frozen prototype asset or gate state.

## Sole permitted deliverable

Create or replace only:

`docs/review/phase-3-p3-4-gemini-readiness-report.md`

Do not edit any other file. In particular, do not edit `design-prototype/`,
`application/`, `adapters/`, `web/`, tests, migrations, contracts, ADRs, project
management records, configuration, dependency files or existing review records.
Do not commit.

If the report path already contains work you did not create during this task,
stop and report the collision rather than overwriting it.

## Read completely before analysing

1. `AGENTS.md`, `.agents/AGENTS.md`, and `docs/implementation-plan.md`;
2. `docs/review/phase-3-delivery-plan.md`, especially §§3–5, P3.2–P3.5,
   P3.G2–P3.G4, the traceability table and risk section;
3. `docs/contracts/README.md`, then every Phase 3 contract in its specified
   order, paying particular attention to:
   - `phase-3-route-authorization-contract.md`;
   - `phase-3-view-model-contract.md`;
   - `phase-3-numeric-policy-register.md`;
   - `phase-3-state-machines.md`;
   - `phase-3-threat-model.md`; and
   - `phase-3-test-traceability.md`;
4. `docs/adr/0010-provider-neutral-identity-and-emergency-administration.md`;
5. `docs/review/phase-3-visual-prototype-handoff.md` and
   `docs/review/phase-3-visual-freeze-manifest.sha256`;
6. all files under `design-prototype/`, read-only;
7. current `docs/project-management/status.md`, `decision-register.md`,
   `raid-register.md` and the current Phase 3 change-log entries; and
8. existing production/minimal templates and static assets, if present, for
   inventory only. Their presence is not permission to modify or complete them.

Treat accepted contracts as authoritative and current implementations as
provisional until their owning gates close. Where they disagree, record the
discrepancy; do not choose a new contract or quietly treat current code as the
source of truth.

## Hard boundaries

- Do not implement Jinja templates, partials, CSS, JavaScript or HTMX.
- Do not copy, move, import or serve files from `design-prototype/`.
- Do not alter the 14-file visual freeze or regenerate its manifest.
- Do not add routes, view-model fields, application queries, authorization,
  persistence, dependencies, configuration or tests.
- Do not propose frontend enforcement as a substitute for server authorization.
- Do not invent fields, actions, links, controls or status values absent from
  the accepted route/view-model contracts.
- Do not expose a control merely because the backend would later refuse it.
  Pre-authorized view models and route-level authorization both remain required.
- Do not add `hx-on:`, inline event handlers, inline executable script,
  `unsafe-inline`, a SPA, JSON browser APIs, npm, a bundler, CDN resources,
  remote fonts, analytics or trackers.
- Do not read `.env`, credentials, production data, real Discord/Foundry/Sheet
  records or external services. Use no network access. Include no real player
  names, identifiers, portraits or payloads in the report.
- Do not mark P3.G1, P3.G2, P3.G3, P3.G4 or Phase 3 ready, accepted or closed.

This task is intentionally useful even if backend details change before the
freeze gates: distinguish facts already fixed by accepted contracts from items
that must be revalidated against the eventual P3.G2/P3.G3 accepted implementation.

## Required analysis

### 1. Contract-to-screen coverage matrix

Produce one complete matrix covering VM-01 through VM-21. For each view model,
record:

- owning backend package and gate;
- route or response status that supplies it;
- intended full page and any partial/full-page pairing;
- closest frozen prototype page/component, or `none`;
- reusable accepted visual patterns;
- required normal, empty, loading, invalid, denied, stale, terminal-success and
  system-error states that are applicable;
- required actions and the exact accepted authority that permits their presence;
- progressive-enhancement/no-JavaScript behavior;
- user-controlled text and escaping concerns;
- numeric bounds or pagination limits relevant to layout;
- P3.4 tests required by the traceability contract; and
- readiness classification: `contract-fixed`, `revalidate at P3.G2`,
  `revalidate at P3.G3`, or `new visual work for P3.G4`.

Do not collapse several view models into an unexplained “covered” row. Shared
patterns may be referenced, but every VM identifier must have an explicit
disposition.

### 2. Route and interaction inventory

Map every P3.1–P3.3 HTML route that P3.4 must render to its method, capability,
object scope, full-page/fragment behavior, CSRF requirement, expected success
and refusal statuses, view model and prototype pattern. Explicitly identify:

- fragments that must also work as full pages;
- mutations whose controls must not appear without pre-authorized view-model
  data;
- polling behavior, including `poll_after_seconds` and terminal job states;
- forms requiring optimistic versions, reasons or confirmation scope;
- object-substitution and enumeration-oracle risks; and
- the OD-45 direct-HTTP tests for R-33, R-34 and R-38 that belong to P3.G2 and
  must already be accepted before P3.4 consumes those routes.

Do not redesign authentication, authorization, CSRF or error semantics.

### 3. Frozen-design adaptation plan

Inventory the accepted design tokens, layout primitives, components and state
patterns that can later be reimplemented in production-owned templates/static
assets. State what may be adapted conceptually and what must not be imported or
served.

For each production screen, identify the closest prototype source and the
minimum adaptation needed. Treat these four accepted contract gaps explicitly:

- VM-10 identity migration;
- VM-12 role-capability administration;
- VM-13 account identities; and
- VM-18 audit search.

For those four screens, give semantic page outlines and reusable component/state
recommendations only—no production HTML/CSS/JS and no new design system. Record
that Peter's visual acceptance at P3.G4 is required for this new visual work.
Do not repurpose the Phase 6 approval-centre concept into a Phase 3 workflow.

### 4. Accessibility and responsive acceptance plan

Build a testable checklist for:

- semantic landmarks, headings, labels, descriptions and error association;
- keyboard order, visible focus, skip links and focus placement after navigation,
  validation failure and HTMX replacement;
- status/error announcements without excessive live-region noise;
- modal/dialog behavior only where already required by accepted interaction
  contracts;
- tables at narrow widths without hiding authoritative facts;
- 320, 768 and 1280 CSS-pixel layouts;
- 200% zoom/reflow, text spacing, reduced motion and contrast;
- no-JavaScript completion of every essential flow;
- loading, stale, denied and system-error behavior; and
- browser, source-derived, automated accessibility, real-device and supervised
  evidence classes, without claiming any has run.

Tie each item to the accepted delivery plan, view-model contract or traceability
identifier where one exists. Separate checks Gemini can automate during P3.4
from checks that require Codex review or Peter's real-device/visual acceptance.

### 5. Security-preserving template checklist

Produce a concise implementation checklist covering Jinja autoescape, the ban on
unsafe `|safe`, static HTMX attributes, the `hx-on:` prohibition, synchronizer
CSRF handling, CSP compatibility, safe URLs/return paths, image handling,
bounded iteration, safe closed-code-to-copy lookup, no authoritative client-side
calculation and no secret/raw payload rendering.

For each control, identify the future source test or response/browser test that
should prove it. Make clear that templates cannot grant authority and that
hidden controls do not replace direct-HTTP denial tests.

### 6. Proposed P3.4 file and test plan

Propose—but do not create—a minimal future production file tree for base layout,
pages, partials, reusable components, static CSS, vendored HTMX and frontend
tests. Assign each proposed file a clear responsibility and list the view models
it consumes. Avoid generic dumping grounds, duplicated page logic and a second
frontend application architecture.

Include a recommended implementation order constrained by P3.G2/P3.G3:

- work that cannot begin until P3.G2;
- work that cannot begin until P3.G3;
- work that may overlap late P3.3 only after its contracts are accepted and
  non-conflicting; and
- final P3.G4 integration/accessibility evidence.

Do not estimate calendar dates. You may identify relative complexity and likely
risk concentration.

### 7. Readiness gaps and questions

List only concrete gaps that would prevent faithful P3.4 implementation. Each
entry must include:

- exact source artifact and section/identifier;
- observed ambiguity, absence or conflict;
- consequence if unresolved;
- accountable owner (`Claude/backend`, `Gemini/frontend`, `Codex/review`, or
  `Peter/decision`);
- gate by which it must be resolved; and
- safest default action, normally “stop and return to the contract owner.”

Do not manufacture questions already answered by the contracts. Distinguish:

- a true contract defect;
- backend implementation not yet available because its package has not run;
- new visual work already anticipated for P3.G4; and
- optional polish that does not block implementation.

End this section with a go/no-go checklist that can be rerun after P3.G2 and
P3.G3. Its present result must be **NO-GO for P3.4 implementation because the
predecessor gates remain open**, regardless of how complete the planning report
is.

## Evidence and self-check

Before writing, record `git status --short` so you can distinguish pre-existing
changes. Verify the frozen prototype before and after analysis:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
```

After creating the sole permitted report, run:

```bash
git diff --check -- docs/review/phase-3-p3-4-gemini-readiness-report.md
git status --short
```

In the report, state:

- exact commands and results;
- whether all 14 freeze-manifest entries passed before and after;
- the sole file you created;
- that no implementation, contract, prototype or gate record was changed;
- all evidence classes deliberately not run; and
- any collision or repository inconsistency encountered.

Do not run production services, migrations, database tests, browsers, package
installation or network commands for this planning task.

## Required report structure

Use these headings in
`docs/review/phase-3-p3-4-gemini-readiness-report.md`:

1. `Scope, authority and current no-go state`
2. `Sources read and precedence`
3. `VM-01–VM-21 contract-to-screen matrix`
4. `P3.1–P3.3 route and interaction inventory`
5. `Frozen-design adaptation map`
6. `Four new-screen semantic outlines`
7. `Accessibility and responsive acceptance plan`
8. `Security-preserving template checklist`
9. `Proposed P3.4 file, test and implementation plan`
10. `Readiness gaps, owners and gate deadlines`
11. `Post-P3.G2/P3.G3 go/no-go checklist`
12. `Commands, freeze verification and diff account`

Prefer precise tables where they make coverage auditable. Use requirement,
route, view-model, test and gate identifiers instead of vague prose. Do not copy
large passages from contracts; cite their file and section.

End with this exact line:

`P3.4 readiness analysis complete; P3.4 implementation remains NO-GO until P3.G2 and P3.G3 close, and no production or frozen-prototype file was changed.`
