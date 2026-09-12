# Claude — bounded remediation for the reserved disposable laboratory

Date: 2026-09-10. Authorized direction: C-P5.0-LAB-1.

## Objective and required reads

Make concrete progress toward Package 5.0 evidence using the existing disposable
host with exclusive reservation, trusted administrators and scoped adversarial
cases. Do not build or further expand the proposed VM architecture.

Read `.agents/AGENTS.md`, `docs/implementation-plan.md` and
`docs/operations/disposable-test-server.md` completely. Then read:

* `docs/review/phase-5-0-reserved-laboratory-direction.md` — current direction and repercussions;
* `docs/review/project-review-2026-09-10-r2.md` — new CRP defect and continuing harness defect;
* the September 2 evidence-harness authorization, R16 independent review,
  September 10 C-8 review and VM independent review;
* package-plan §§2.12–2.13, C-8 revision 3, current source, tests, concrete and
  execution plans, review manifest and observation/coverage contracts;
* current status, decisions and RAID entries for C-P5.0-LAB-1.

Preserve unrelated changes. No stage, commit, push or history rewrite. This
prompt supersedes the next-action instruction to expand/revise the VM proposal.
It does not supersede production acceptance requirements or approve residuals.

## 1. Resolve the evidence dependency first

Before substantial mechanism work, trace each of the three named C-7 cases to
its exact requirement, current missing producer, minimum synthetic experiment,
observable result, positive/negative control and later production regression.
Use actual source references, not inferred names of future commands.

Produce a compact feasibility-versus-product-evidence table. Implement minimum
local evidence-only producers where the September 2 authorization suffices.
Use deterministic injection and actual observed synthetic effects; do not feed
expected answers directly into the classifier. Include missing/corrupt output,
injected failure, duplicate input and cleanup-failure cases. Keep these modules
isolated from production startup, database migrations and runtime imports.

If an essential case cannot be meaningful without gated product code, stop that
dependent work and submit the exact readiness/implementation criterion split for
Peter, with a recommendation. Continue the independent CRP and admission work.
Do not mark the case covered, clear C-7 or change `is_executable` merely because
a proposed producer or a synthetic input schema exists. No criterion split is
pre-approved by this prompt.

## 2. Implement bounded local admission and evidence handling

Implement and test the reservation state/owner/target contract and fail-closed
admission/reporting with injected effects. Specify one cooperative host lock and
how every project test/sync entry point participates; manual root access remains
a trusted operational premise, not a permission that the lock revokes.

Cover a second executor, missing/expired reservation, mismatched target/release,
unknown writer, orphaned child, delayed database transaction, interrupted recovery
and successful release. Lock release or timeout cannot make quarantine reusable.
Do not introduce a VM manager, distributed scheduler or general privileged shell.

Produce the exact operation-by-operation contract for the smaller privileged
runner: subjects and writable parents, test identities, source custody, verified
capture, restore destination, quiescence and refusal/uncertainty handling. The
whole-host reservation excludes unrelated cooperative work; it does not repair
substitution by experimental writers. Preserve independent configuration recovery
when the disposable root is unsafe. Do not reintroduce staged-source substitution
or assume a held root descriptor protects every descendant/final entry.

Local admission/reporting and bounded producers are authorized here. Any newly
required privileged writer, verb, syscall surface or permission expansion must
be presented as an exact implementation/permission diff for Codex review before
that mechanism is implemented, under the existing design checkpoint. Reuse
accepted mechanisms where sufficient; do not request another broad architecture
round or silently adopt the rejected C-8/VM mechanisms.

Retain a real-execution refusal while the ownership remedy remains unaccepted.
Keep injected defect reproductions useful and labelled as such; do not weaken
them to make an unimplemented safety property appear to pass. Do not clear the
operational-ineligibility control as a shortcut to testing admission.

## 3. Separate CRP regression fix

Fix PR-20260910-R2-1 in `models/skills.py` and focused tests. First reproduce
the reported cell `60 (Herbalist), 50 (Herbalism)`: reads currently report 60
while adding one reports 111. Make reads and writes consistently aggregate
equivalent entries, with no persistence or mutation on read. Cover both orders,
Herbalist/Herbalism, Forger/Forgery and Thief/Thieves, Master-learning threshold
and read-before-plus-one equality. Preserve untagged, unreadable and mastered CRP
semantics and the existing alias fix. Use synthetic fixtures only. Keep this
small maintenance fix reviewable independently of harness work; no bot restart.

## Verification, authority and handback

No SSH, synchronization, target inspection, provisioning, database operation,
service mutation, generated-vector execution, `--execute` or armed real boundary
during this local pass. The later authorized Codex preflight remains after
implementation review. Do not inspect credentials or production data. Do not
populate the twelve unconfirmed target facts.

Use local synthetic tests with injected effects. Verify the existing fallback
interpreters before use; they are exceptions for this restricted task, not the
canonical oracle-test environment. Keep `TEST_DATABASE_URL` unset. Run structural
checks, changed focused tests, then the harness, bot and web suites (bot/web
serially) and Foundry tests. Run configured lint/type/format checks, scoped
compileall and `git diff --check`; report unavailable tooling and every skip.

If manifest-covered code changes, regenerate using only the non-executing path
twice, compare bytes and independently verify covered hashes. Changed artifacts
remain review input; no digest is approved for execution. Do not hand-edit the
manifest to hide a source change or record an unperformed producer review.

Return `docs/review/phase-5-0-reserved-laboratory-handback.md` with:

* implemented code versus proposed privileged changes;
* separate CRP disposition and regressions;
* three explicit C-7 dispositions and any precise criterion decision required;
* reservation/quarantine enforcement, operational premises and residual limits;
* exact permission delta and ownership/recovery tests;
* final-tree commands/results/skips, manifest integrity and unrun host checks;
* next runnable step, owner and evidence it will establish.

Update current pointers concisely and preserve review history. Return one
consolidated handback to Codex. Package 5.0 remains not ready, P5.0-R5 Blocking,
OD-62 Open; EH-R16-1 and the relevant project findings remain open pending review.
Product implementation, migration 0014, deployment, cutover and Package 5.1+
remain unauthorized. Do not close your own findings or accept risks for Peter.
