# Claude implementation prompt — resolve C-6, C-7 and C-8

Work in `/opt/freedom-blades/platform`.

## Authority recorded on 2026-09-09

The maintainer approved Codex's recommendations for C-6, C-7 and C-8, assigned
implementation to Claude, assigned subsequent independent review to Codex, and
authorized the separately described read-only target preflight.

This authorizes bounded design and local synthetic implementation of:

- narrowly scoped immutable-flag experiments for C-6;
- a separate, non-executing observation importer/classifier for C-7; and
- exclusive creation of the disposable root with recorded ownership and
  ownership-validated automatic cleanup for C-8.

These approvals supersede earlier prohibitions on those specific implementation
extensions. Do not return the same three high-level decisions to the maintainer.
Record the exact designs, interfaces and safety arguments for Codex review.
The earlier recommendation requested review of the exact C-8 creation mechanism
before implementation: prepare that concrete design for Codex first, continuing
independent C-6/C-7 work while it is reviewed. This is a technical review gate,
not a request to repeat the maintainer's authorization.

The read-only preflight is authorized for the later stage **after Codex reviews
the completed implementation**. Record that authorization in the handback;
do not request it again. This implementation assignment does not instruct Claude
to perform that later stage now. Codex will coordinate the preflight and review
its evidence after reviewing Claude's work.

The maintainer also assigned step 5 to Codex: review the final manifest and exact
disposable-host execution plan, determine whether the execution review gate is
satisfied, and coordinate operational evidence collection and cleanup
verification. Claude's handback must support that review. This assignment does
not authorize Claude to execute the harness or substitute its own approval.

Operational execution of the evidence harness remains a separate gate. No
`--execute`, real generated vectors, armed real process boundary/materializer,
target provisioning, database mutations, destructive drills, deployment or
cutover is authorized by this prompt. Package 5.0 stays not ready, P5.0-R5
Blocking and OD-62 Open. Product implementation, migration 0014 and Package
5.1+ remain outside scope.

## Required context and worktree discipline

Read completely `.agents/AGENTS.md`, `docs/implementation-plan.md` and
`docs/operations/disposable-test-server.md`. Then read the R15 independent
review, R14 handback, relevant package-plan sections 2.12–2.13, the generated
plan, and affected harness code and tests. Earlier prompts supply historical
constraints except where the maintainer's approval above explicitly changes them.

Check git status. Preserve unrelated changes. Do not reset, stage, commit or
push. Keep changes in the evidence harness, its tests and directly supporting
design/review documents. Update the current handover, preserving its history.
Do not rewrite roadmap or readiness gates to make the harness appear complete.

Starting review input, never execution approval:
`79ed6ed615b3a2eeb74e5b07d51f76bac0e4b0d4451f636436cf1aec523e7324`.
R15 accepted the bounded R14 remediation; it did not approve execution.

## C-6 — implement the missing experiments

Extend the closed case-program interface only as needed for the approved
immutable-flag operations on declared disposable artifacts. Specify permitted
verbs, arguments, paths, identities, flags, result schemas and refusal states.
Do not add general ioctl, arbitrary mask, shell or arbitrary-path interfaces.

Generate actual operation steps for:

1. E4 attempting to clear the root-owned archive's immutable flag;
2. E6 performing the corresponding positive-control operation; and
3. E5 clearing the flag, followed by a separately ordered O_WRONLY open whose
   interpretation requires the clear to have succeeded.

Preserve each identity's semantic prerequisite. Establish and observe the
initial artifact state separately for each experiment: a prior successful clear
must not make a subsequent case meaningless. State expected outcomes from the
approved package design, not from whatever the experiment returns. Unexpected
outcomes are findings, not reasons to alter expectations.

Include setup/reset/cleanup and failure paths in the exact plan. Preserve all
existing append-only experiments, identity contracts and bounded observations.

## C-7 — connect evidence to classification without execution capability

Design the importer as a separate non-executing component. Supplied records must
not select commands, executables, process identities, target paths, approval
tokens or reviewed expected values, or construct an executing boundary.

Use a strict, versioned and bounded schema. Bind records to their target, run,
manifest, case, identity and control as applicable. Refuse malformed, duplicate,
missing, unexpected, contradictory or mismatched records. Compare complete
required-case coverage before producing a complete evidence result.

Connect the existing provenance/journal/manifest classifiers to validated
observations for all required Band 7 cases, including omitted provenance,
failures at each required stage, cleanup failures and recovery-state distinctions.
Map each case to its actual producer and collection procedure. If an experiment
producer is still missing, report it as unresolved; an importer cannot supply
experimental evidence merely by accepting a correctly shaped record.

Keep synthetic fixtures visibly synthetic and ineligible for operational
acceptance. Define provenance and custody requirements for externally supplied
operational observations; target/run/digest fields alone do not authenticate
their origin. Never promote assertions into observations or learn expected
results from the evidence being judged.

Keep the diagnostic run record distinct from classified evidence. Persist and
validate the complete classified artifact before reporting that it was written.

## C-8 — establish filesystem ownership safely

Retain automatic cleanup. The maintainer did not select abandonment of the 29
filesystem reversals or parsing unrestricted operating-system error prose.

Submit the exact bounded creation mechanism, bootstrap location, approved root,
result vocabulary, ownership evidence and cleanup validation to Codex for the
technical design review noted above. Account for the bootstrap dependency: a
helper required to create the root cannot first be installed inside that root.

Ownership must derive from successful exclusive creation, not a preliminary
absence check followed by an overwriting creation. Refuse existing directories,
files and symlinks, ambiguous failures and unexpected parent resolution. Describe
how ownership is tied to the created object and revalidated before deletion;
replacement of a path must not inherit permission to delete its replacement.

Handle interruption and uncertain creation outcomes conservatively. If ownership
cannot be proved after a crash or failed response, report bounded residue and
recovery requirements without deleting an unowned object or claiming clean
success. Preserve configuration-backup retention until restoration, reload and
verification succeed.

Update mutation accounting and cleanup applicability to reflect exclusive
creation. Do not simply reattach ownership to R-B-ROOT or remove C-8's marker.
Retain the database/role catalog corrections and all pre-existing-object tests.

## Verification

Use local synthetic tests with TEST_DATABASE_URL unset. Report the interpreter
actually used as a local fallback where applicable; the canonical oracle-test
runtime path is not evidence of local test availability. Do not synchronize or
modify the target as part of this implementation stage.

Run structural no-execution checks first. Add regressions for the missing
behaviors before their implementation. Exercise error, interruption, ownership
replacement, invalid input, incomplete coverage and artifact-persistence paths,
as well as positive controls. Keep process/filesystem effects injected in these
tests; do not test the new privileged operations against this host.

Run focused tests, then the complete synthetic harness suite. Run other available
non-database suites serially where applicable. Report skipped integration tests
explicitly; do not reuse older results. Run git diff --check and configured
tooling, noting tools that are not configured.

Regenerate manifest and plan twice and compare bytes. Ensure all new trusted
code and new input contracts are covered by the manifest and structural tests.
Remove unresolved markers only when the corresponding implementation and proof
obligations are met. Passing tests and an executable-on-paper plan confer no
operational execution authority.

## Handback to Codex

Create `phase-5-0-evidence-harness-c6-c7-c8-handback.md` with designs and
decisions, changed files, required-case-to-producer mapping, pre/post-fix results,
failure/cleanup evidence, exact regenerated digest and remaining limitations.
Update `Handover information` to point to that submission and R15 history.

Include a proposed bounded read-only preflight command list for the twelve
target facts: interpreter SHA-256 and resolved path, plus E7 UID, GID,
supplementary groups, five capability masks, NoNewPrivs and securebits. Specify
the exact future launcher context; facts from a different SSH/sudo/process
context must not be substituted. Inspect only the approved oracle-test target,
never credentials or production systems. Leave facts unconfirmed until the
authorized later preflight supplies evidence and Codex verifies it.

Stop for Codex's independent implementation review. Codex owns that review and
the subsequent preflight coordination; Claude must not approve its own manifest,
close package gates or begin operational execution.
