# Gemini handoff — Phase 3 visual design prototype

Copy everything below this line into Gemini as one prompt.

---

You are the frontend design agent for the Freedom Blades Platform. Build the
static, inert visual prototype required by implementation-plan §12.1.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-12

Maintainer and Product Owner: Peter Duscha

Frontend owner: Gemini

Backend owner: Claude

Independent and security-focused reviewer: Codex

## 1. Outcome and authority

Create an original, accessible Freedom Blades interface design under
`design-prototype/`. This task establishes the visual language and static page
contracts only. It is not Phase 3 production integration and it closes no gate.

You may:

- read the repository instructions and controlled design/architecture records;
- create or edit files only under `design-prototype/` and the single prototype
  handoff/report you create under `docs/review/`;
- use synthetic names, IDs, portraits, values and reconciliation records;
- use local semantic HTML, plain CSS and small removable prototype-only
  JavaScript; and
- inspect `docs/Freedom Blades Token.png` as the requested visual reference.

You may not:

- add FastAPI routes, Jinja production templates, authentication, sessions,
  authorization, CSRF, repositories, application services, migrations, API
  calls, production configuration or persistence;
- place prototype code in `web/` or import it from production code;
- introduce React, Vue, another SPA framework, npm, a bundler or a build step;
- use a CDN, remote font, tracker, analytics or runtime network dependency;
- contact Discord, Foundry, Google Sheets, PostgreSQL or any external service;
- read `.env`, credentials, real exports or player data;
- commit, push, deploy, or claim approval; or
- begin production frontend integration before Claude's route and view-model
  contracts have been accepted.

## 2. Mandatory context

Before planning or editing, read completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §§4, 5, 6.2, 9, 12.1, Phase 3,
   §13.3 and §16.4
4. `docs/adr/0002-web-application-stack.md`
5. `docs/adr/0004-discord-oauth2-authentication.md`
6. `docs/rules/field-ownership.md`
7. `docs/project-management/status.md`
8. the closed OD-16 and OD-17 rulings in `docs/discovery/open-decisions.md`
9. `docs/review/phase-3-visual-prototype-implementation-plan.md`

The controlled implementation plan expands this handoff into ordered work and
acceptance evidence. Follow both; if they appear to conflict, stop and report the
conflict rather than silently choosing or weakening a requirement.

Check `git status` and preserve every existing change. Do not reset, clean,
revert or reformat unrelated work.

## 3. Brand reference and required asset

Peter has supplied a clean 1024×1024 PNG at
`docs/Freedom Blades Token.png` and confirmed on 2026-08-12 that the earlier
picture issue is remedied. Use this PNG as the visual sign of the Freedom Blades
and build the interface around its winged-sword emblem, circular seal, cool blue,
steel-grey, black and white palette.

- Use the PNG itself; do not trace, redraw, distort or generate a near-copy.
- Preserve its aspect ratio and provide useful alternative text where it conveys
  identity. Decorative repetitions use empty alternative text.
- Keep it crisp at common device-pixel ratios and avoid enlarging it beyond its
  useful source resolution.
- Do not bury the emblem in visual noise. It is the identity anchor, not a page
  texture or watermark.
- Record it in the asset inventory as a maintainer-supplied project asset, with
  the maintainer's 2026-08-12 confirmation in the handoff.

## 4. Design direction

Build a distinctive guild-command interface around these ideas without turning
it into fantasy-game cliché:

- the circular seal is the identity anchor in the header/login composition;
- blue wings suggest navigation, motion and openness; steel suggests dependable
  administrative controls; white space keeps dense records readable;
- use restrained heraldic geometry, fine steel borders and clear information
  hierarchy rather than parchment textures, faux-medieval fonts, excessive
  gradients or ornamental clutter;
- choose a local/system font stack that remains highly readable in long tables;
- separate player-facing calm from Council-facing operational density while
  keeping one coherent component system; and
- never use copyrighted D&D publication art or visual elements that imply an
  official Wizards of the Coast product.

Create documented design tokens for colours, typography, spacing, radii,
borders, elevation, focus rings, motion and breakpoints. Test all text and
essential controls against WCAG 2.2 AA contrast. Do not rely on colour alone.

This is not an exercise in merely satisfying a page checklist. Peter's acceptance
requires all three qualities together:

1. **functional clarity** — users can understand what the eventual working
   interface does, what is read-only, what is pending and what requires Council;
2. **usability** — navigation, hierarchy, responsive behaviour, states and dense
   operational information work for real tasks; and
3. **visual quality** — the result is cohesive, deliberate and attractive enough
   to serve as the production visual direction, not a wireframe wearing colours.

A beautiful page that obscures state fails. An accessible and understandable
page that looks unfinished also fails. Explain the design rationale and revise
weak compositions rather than declaring the first complete layout done.

## 5. Required static pages

Create independently openable static pages for:

1. **Login** — Freedom Blades identity, plain explanation of Discord sign-in,
   privacy-conscious copy and non-functional sign-in control.
2. **My Characters** — multiple linked characters, empty state, unavailable
   state and clear distinction between identity and mutable display name.
3. **Character detail** — read-only profile, provenance, snapshot freshness and
   financial facts. Follow OD-16: an ordinary member sees only linked
   characters; Council access is visibly elevated. Do not imply that hiding UI
   is the security control.
4. **Reconciliation** — checksum, world/folder/profile version, progress,
   mappings, create candidates, explicit unresolved records, warnings and
   `migration deferred` fields. Reflect the measured 9.57-second real preview:
   show an asynchronous queued/running/completed model, never a synchronous
   request that appears frozen.
5. **Council approval queue and diff** — a forward-looking component prototype
   for later phases, clearly marked inert. Show before/after, provenance,
   warnings, stale state and explicit confirmation without suggesting that
   Phase 3 can mutate character game state.
6. **Component catalogue** — navigation, cards, tables, forms, badges, alerts,
   tabs, pagination, dialog examples, progress, skeleton/loading, empty,
   validation, denied, stale and system-error states.

All people, characters, IDs, values and portraits must be obviously synthetic.
Do not copy repository fixtures if there is any chance they derive from real
data.

## 6. Interaction and responsive requirements

- Semantic HTML and logical heading order.
- Full keyboard reachability and visible `:focus-visible` treatment.
- A skip link and landmarks.
- Usable layouts at 320 px, 768 px and wide desktop widths.
- Dense tables gain a deliberate narrow-screen treatment; do not merely force
  the whole page to horizontal-scroll.
- Minimum practical touch targets and no hover-only information.
- Reduced-motion support; animation must be optional and nonessential.
- Dialog examples must demonstrate focus intent and accessible labelling even
  though they are inert.
- Status, errors and warnings require text/icon distinctions in addition to
  colour.
- Preserve zoom and text resizing; do not disable browser scaling.

Optional JavaScript must be local, dependency-free, tiny and removable. The
prototype must remain understandable without it.

## 7. Architecture handoff

The accepted production stack is FastAPI, Jinja2 and vendored HTMX with no npm
or bundler. Design semantic fragments that Gemini can later translate into
Jinja templates and modest HTMX partials, but do not write production code now.

Provide `design-prototype/README.md` containing:

- how to open every page locally with no server and no network;
- the design-token and component inventory;
- responsive and accessibility notes;
- asset provenance, identifying the token as the maintainer-supplied project
  identity asset confirmed on 2026-08-12;
- a page/component mapping to likely future Jinja layouts, templates and HTMX
  partials without dictating backend route names or payloads;
- every normal, empty, loading, validation, denied, stale and error state; and
- a clear list of assumptions Claude must settle in the route/view-model
  contracts before production integration.

Also create one concise review handoff under
`docs/review/phase-3-visual-prototype-handoff.md` listing files, decisions,
accessibility checks, widths inspected, asset status, limitations and exact
commands run.

## 8. Verification

At minimum:

- open or render every page locally and verify it requires no network;
- inspect at 320 px, 768 px and a desktop width;
- keyboard-walk every primary navigation and representative control;
- verify visible focus and reduced-motion behaviour;
- calculate or inspect WCAG 2.2 AA contrast for every text/control token and
  record the ratios or tool output;
- check for remote URLs, production imports, forms with real effects, secrets,
  real data and unlicensed copied assets;
- run `git diff --check`; and
- report checks that could not be run rather than claiming them.

Do not commit. Return the prototype for Codex review and Peter's visual
acceptance. Production integration begins only after that acceptance and after
Claude's backend contracts are stable.
