# Prompt for Gemini — P3.4 Step 1: baseline and closed work map

Date: 2026-08-20 · Status: **RELEASED** · Step: 1 of 13

You are Gemini, the P3.4 production frontend implementer. Perform **only Step
1**, deliver its checkpoint, and stop. Do not begin static assets, CSS, shared
layout, templates or tests.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`;
3. `docs/review/phase-3-p3-4-gemini-execution-plan.md`;
4. `docs/review/phase-3-delivery-plan.md`, especially P3.4 and P3.G4;
5. `docs/review/phase-3-p3-4-authorisation-and-conditions.md`;
6. `docs/contracts/README.md` and every Phase 3 contract in its prescribed
   order;
7. `docs/review/phase-3-p3-4-gemini-readiness-report.md` §§A1–A10;
8. `docs/review/phase-3-visual-prototype-handoff.md` and the visual freeze
   manifest;
9. every file under `design-prototype/`, read-only;
10. all current production templates and their rendering handlers; and
11. the P3.4-relevant tests and structural guards.

Historical readiness-report §§1–12 are not implementation authority. Where an
accepted contract and current implementation disagree, record the exact
discrepancy and stop; do not choose a side.

## The only allowed write

Create:

`docs/review/phase-3-p3-4-gemini-baseline.md`

Do not modify any existing file. In particular, do not change anything under
`adapters/`, `application/`, `domain/`, `migrations/`, `tests/`,
`design-prototype/`, `infra/`, requirements/configuration files or controlled
project-management records. Do not commit, push, stash, deploy, contact a live
service, install a dependency, read `.env`/credentials/secrets, or access real
player/guild/Actor data.

## Work, in order

1. Record the literal output of `git status --short`. Treat every existing
   change as user work. Do not inspect or touch `stash@{0}`.
2. Verify the 14-file visual freeze with the existing manifest and record the
   literal command, exit code and result.
3. Record the complete current inventory of the 24 production templates and
   the static root. Record SHA-256 for each; use `absent` only for later files
   that do not yet exist.
4. Build a table mapping every production template to:
   - rendering route identifier(s) and handler;
   - accepted view-model identifier and type;
   - applicable `PageState` values and important nested states;
   - caller/capability class;
   - full-page or fragment role;
   - essential no-JavaScript flow;
   - prototype reference, or `none` where P3.4 must extend the visual language;
   - planned execution-plan step.
5. Inventory existing P3.4-relevant tests and identify the exact tests each
   later step must add or update. Do not create or edit a test.
6. Record the accepted M-01 `/static/` contract and list the anticipated Step 2
   assets without creating them or choosing final filenames prematurely.
7. Record every current dirty-tree path that overlaps a later P3.4 allowlist.
   Distinguish pre-existing user changes from files currently absent. Do not
   overwrite, revert or normalize anything.
8. Run only non-mutating baseline checks that do not require secrets, a live
   service, an external network call or a database. At minimum:
   - `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256`;
   - the existing non-database structural guards relevant to the route,
     view-model, template and static inventories, selecting them explicitly;
   - `git diff --check`.
9. List every ambiguity, missing fixture, unavailable browser/evidence class or
   apparent contract mismatch. Do not solve one in this step.

## Baseline document requirements

The new baseline document must contain:

- scope and evidence-class statement;
- dirty-tree baseline;
- visual-freeze result;
- file inventory with SHA-256;
- the complete template/route/view-model/state/flow/reference/step matrix;
- existing-test and planned-test map;
- later-step overlap analysis;
- static-asset contract facts and anticipated assets;
- literal commands, exit codes and results;
- checks not run and why;
- discrepancies, questions and residual risks; and
- a Step 1 checkpoint verdict: `READY FOR STEP 2` or `BLOCKED`, with reasons.

Do not claim browser, real-device, screen-reader, staging, PostgreSQL or
production evidence from source inspection.

## Stop conditions

Stop and mark the checkpoint `BLOCKED` if:

- an accepted contract and implementation disagree;
- a template cannot be mapped to its route and view model;
- the registered route/view-model/static surface is not closed as accepted;
- the visual freeze fails;
- an existing change overlaps later work and its ownership cannot be separated;
  or
- completing the baseline would require any write beyond the one allowed file.

After writing the baseline, run `git diff --check` and `git status --short`,
report the new file and its SHA-256, give the checkpoint verdict, and **stop**.
Do not begin Step 2 even if the verdict is ready.
