# Claude prompt — Phase 2 I-03 fourth remediation and gate-readiness package

Date: 2026-08-05
Repository: `/opt/discord-bots/freedom-bot`
Branch: `docs/platform-plan`
Current HEAD: `3abb5ba`
Baseline before the uncommitted Phase 2 package: `c8a3da9`

You are the implementing agent and working Technical Lead. Bring the current
uncommitted Phase 2 I-03 package to an honest, reviewable gate-ready state. Fix
the remaining Important evidence defect identified by Codex, audit the complete
Phase 2 gate package for any related overstatement, complete every safe
automated or disposable-environment check that is within scope, and produce a
self-contained final handoff for independent re-review and owner-controlled
evidence.

Do not commit or push. Do not install the Foundry module or touch a Foundry
world. Do not read Foundry world storage, LevelDB, compendium packs, or player
data. Do not issue, print, store, or request a real credential. Do not claim a
finding closed, approve your own work, or state that Phase 2 is finished. Peter
Duscha is the Acceptance Authority and records the gate decision only after the
required independent recommendations and supervised evidence.

## 1. Read and preserve before acting

Read completely, before editing:

1. `AGENTS.md` and `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`, especially §§0.2–0.5, 6.4–6.5, Phase 2,
   13.3, 14, and 16.4;
3. `docs/adr/0006-foundry-integration-boundary.md` and
   `docs/adr/0009-snapshot-submission-http-boundary.md`;
4. `docs/review/Handover information`;
5. `docs/review/phase-2-i-03-remediation-review-request.md`;
6. `docs/review/phase-2-i-03-remediation-submission.md`;
7. `docs/review/phase-2-i-03-third-remediation-codex-re-review.md`;
8. `docs/review/phase-2-i-03-third-remediation-codex-security-re-review.md`;
9. the package plan, operations documents, controlled management records,
   implementation, migrations, and tests implicated by those documents; and
10. the complete current `git status`, diff from `c8a3da9`, and the committed
    review-only change at `3abb5ba`.

The working tree contains intentional uncommitted implementation owned by this
package and two committed Codex review reports. Preserve all unrelated work.
Do not reset, rewrite, squash, amend, delete, or commit anything.

## 2. Required remediation: I-3R-1 evidence accuracy

Codex accepted the publication mechanism, I-1, I-2, root anchoring, S-B-1, and
S-I-1, but found one Important defect in the submitted evidence:

> The third-remediation request says “no temporary survives success or an
> ordinary failure” because `_discard` runs on each path. That is not what the
> implementation guarantees. `_discard` intentionally swallows `OSError`, and
> `test_a_failing_cleanup_leaves_the_published_artifact_alone` proves that a
> successful store may leave one private `.incoming-*` hard link behind.

Correct the record at its source and everywhere the same absolute claim or an
equivalent appears. At minimum audit:

- `docs/review/phase-2-i-03-remediation-review-request.md`;
- `docs/review/phase-2-i-03-remediation-submission.md`;
- `docs/review/phase-2-i-03-package-plan.md`;
- `docs/operations/foundry-snapshot-submission.md`;
- `.env.example`;
- `docs/project-management/change-log.md`;
- `docs/project-management/status.md`;
- `docs/project-management/raid-register.md`;
- module and application docstrings; and
- tests whose names, comments, or assertions describe cleanup guarantees.

State the actual contract consistently:

- publication never removes or overwrites the final checksum entry;
- cleanup can only name an internally generated `.incoming-*` entry;
- temporary cleanup is best effort;
- failure to remove a temporary does not invalidate or delete a correctly
  published artifact;
- a failed cleanup may leave a private, unservable hard link consuming storage;
- operator hygiene detects and handles such leftovers under the documented
  read-only orphan procedure; and
- no statement may promise zero surviving temporaries unless its preconditions
  explicitly exclude cleanup failure and a test proves those preconditions.

Do not change the accepted `os.link` publication design merely to make the old
sentence true. Codex accepted the `os.link` versus
`renameat2(RENAME_NOREPLACE)` trade and the test-only bounded ancestor walk.
Do not reopen either decision without discovering concrete contradictory
evidence.

Add or strengthen tests only where needed to make the documented contract
executable. Preserve the existing cleanup-failure test. If the operator hygiene
procedure claims a detection rule, prove it against synthetic files without
adding an application list/delete endpoint. Do not add automatic deletion of
unknown entries or broaden the service's filesystem authority.

## 3. Gate-readiness audit: distinguish work from evidence

The purpose of this turn is not merely to edit one sentence. Audit the complete
Phase 2 handoff against every Phase 2 acceptance criterion and §13.3 evidence
requirement. Produce one traceability table with exactly one current disposition
for each item:

- `automated — passed`, naming the test/check and exact latest result;
- `disposable rehearsal — passed`, naming the environment, command, result,
  cleanup, and retained evidence;
- `supervised — pending`, naming the accountable person, exact procedure,
  required observation, and why automation is not a substitute;
- `not applicable`, with the existing approved rationale; or
- `failed/blocked`, with the concrete failure and next action.

Never turn “not run” into “remediated by construction.” Construction and tests
may support a recommendation, but an acceptance criterion requiring observation
remains pending until observed. Do not use aggregate test counts as a substitute
for named traceability.

In particular, retain accurate dispositions for:

1. operations §8.1: credential absence from the state delivered to a live
   second Foundry client — supervised, not yet run;
2. operations §8.2: positive and negative CORS behavior in a real browser
   origin — supervised, not yet run;
3. the cross-account artifact-root experiment — not run unless Peter supplies
   an approved disposable second account and supervises it;
4. multi-process publication — currently residual evidence; do not silently
   relabel the deterministic two-store test as a process test;
5. operations rehearsals §§6 and 7 — run only if they are expressly disposable,
   synthetic, non-production, require no real Foundry access or credential, and
   the named environment is available; otherwise leave them pending with exact
   owner steps;
6. the supervised real immutable snapshot reconciliation and Data Owner
   attestation required by Phase 2 — pending unless Peter actually performs and
   records it; never use or commit real Actor data to simulate completion;
7. backup/restore/rerun, upgrade/downgrade/upgrade, and direct restricted-runtime
   role denial — run against the named disposable PostgreSQL environment if safe
   and authorized by the existing operations plan; report exact results and
   restore the disposable environment to its documented state; and
8. formatter, linter, and type checker — report `not configured` if still true;
   do not install tools solely to manufacture a check.

If an outstanding check requires Peter, do not stop after saying so. Prepare a
short, exact, copyable supervised run sheet containing prerequisites, commands
or UI actions, expected positive and negative observations, evidence to record,
redaction requirements, cleanup, and abort conditions. It must not contain a
real secret, origin, Actor name, raw snapshot, filesystem path exposing private
deployment details, or player data. Clearly mark placeholders.

## 4. Controlled records and final package

Update the controlled records so they agree with reality and with each other.
Do not rewrite history to make earlier attempts look correct. Mark superseded
claims as superseded and add a dated fourth-remediation entry. Preserve the
Codex reports verbatim.

The final package must state separately:

- implementation state;
- independent-review state;
- automated evidence;
- disposable operational evidence;
- supervised evidence still pending;
- Data, Security, and Operations Owner recommendations still required;
- Acceptance Authority decision still required; and
- whether Phase 2 is actually gate-ready, with no euphemism such as “complete
  except for” when mandatory evidence remains missing.

Create or amend a self-contained fourth-remediation submission and re-review
request. Map I-3R-1 to every changed file, named test, documentation correction,
operational effect, recovery behavior, and residual risk. Ask Codex for a narrow
independent implementation re-review of I-3R-1 and confirmation that the final
traceability/evidence claims are truthful. A new security re-review is not
required if no security-relevant code or contract changes; if you make such a
change, explicitly request one and explain why.

Do not ask Codex or Peter to infer readiness by searching the repository. The
handoff must be self-contained.

## 5. Verification

Run the narrow suites first, followed by the full configured suite. Report the
exact commands, counts, skips, warnings, and failures from this run—not copied
historical numbers:

```bash
(cd foundry-module && node --test "tests/*.test.mjs")

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
  tests/test_artifact_store.py tests/test_snapshot_submission.py \
  tests/test_storage_claim_vocabulary.py tests/test_submission_composition.py \
  tests/test_http_submission.py tests/test_snapshot_preview_service.py \
  tests/test_exporter_contract.py tests/test_submission_database.py

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q -rs

./venv/bin/python -m compileall -q application adapters domain tools tests migrations

APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/alembic check

git diff --check

for file in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do
  node --check "$file"
done
```

Also run any package-plan database rehearsal commands that are safe in the
named disposable environment. Do not contact production Discord, Sheets,
Foundry, PostgreSQL, or external services. Use synthetic fixtures only.

Review the complete diff from `c8a3da9` for secrets, raw artifacts, Actor/player
data, unsafe logs, generated files, unrelated changes, migration reversibility,
and false claims. Report what you inspected and any limitation. Do not say the
working tree is ready to commit merely because tests pass.

## 6. Stop conditions and required final response

Stop and ask Peter before any action that would:

- access or mutate live Foundry, Discord, Sheets, or production PostgreSQL;
- install the Foundry module;
- create or use a real credential;
- create a POSIX account or require privilege escalation;
- use a real Actor export;
- change data ownership, authorization, retention, topology, rollback policy,
  or an accepted architecture decision; or
- commit or push.

Your final response must lead with one of these exact conclusions:

1. `Gate-ready for independent re-review; mandatory supervised evidence remains
   pending.`
2. `Not gate-ready; the following implementation or disposable-evidence work
   remains.`

Then report changed files, migrations, exact verification, checks not run,
configuration/deployment effects, rollback/recovery, unresolved decisions, the
supervised run sheet, and the precise next reviewer request. Do not say “Phase 2
is finished,” “approved,” or “accepted.” Only Peter may record that conclusion
after all mandatory evidence and recommendations exist.
