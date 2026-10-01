# Claude prompt — remediate the C-11 launcher-contract design

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D1-R1`

Date: 2026-09-29

Assignee: Claude, remediation author

Independent reviewer: Codex

State: **assigned repository-only, documentation and read-only analysis only.**
Stop after the amended proposal and remediation handback for independent Codex
re-review.

## 1. Objective

Remediate exactly the two Blocking findings in Codex review
`C-P5.0-R5-RP11-I1-R3-R4-D1-REV1` so the C-11 and pinned
launcher-environment proposal is internally truthful and decision-ready:

1. `R4-D1-1`: unreviewed native-loader state can act before the proposed
   Python entry or its refusal code; and
2. `R4-D1-2`: the client hook cannot inspect A1-12's final runtime-substituted
   command before the capture entry starts.

Do not implement either correction. Amend the existing proposal in place,
create the remediation handback named in §5, update concise current-state
pointers, and stop for independent review.

## 2. Controlling inputs

Read completely before editing:

* `.agents/AGENTS.md`;
* the implementation-plan reading map, §0, §16 and §20;
* `docs/review/Handover information`;
* the original R4-D1 assignment;
* the existing R4-D1 proposal and handback; and
* [Codex's controlling review](project-review-2026-09-29-p5-r5-rp11-r4-d1-c11-launcher-contract.md).

The original assignment's governing facts, environment-contract requirements,
unsafe non-solutions, restrictions and gates remain in force except where this
prompt expressly requires a correction. The review findings control over the
returned proposal.

## 3. Required correction for R4-D1-1

Replace the post-start loader-variable argument with a complete, timed trust
boundary from the already-running client through creation of the trusted entry
process. The corrected proposal must:

* distinguish inputs that affect the client or shell before the proposed
  boundary from inputs supplied to each newly executed image;
* identify the earliest component whose behaviour the design trusts and state
  how its executable bytes, invocation and environment are bound;
* account for the fact that a dynamic loader consumes variables such as
  `LD_PRELOAD`, `LD_LIBRARY_PATH`, audit/debug/profile variables and
  platform-equivalent loader inputs before application code can inspect or
  reject them;
* prevent unreviewed loader state from reaching any process whose in-process
  checks are relied upon for enforcement, rather than detecting it after it
  has already acted;
* reassess interpreter lookup, executable substitution, current directory,
  module lookup, shell startup behaviour, Python startup inputs and inherited
  file descriptors under the same timing rule;
* show the exact client-inspected invocation for each viable option and explain
  why no command reshaping grants a blanket wrapper exemption or hides §5's
  reviewed text from the canonical guard policy;
* state precisely what protection remains for non-Claude agents when client
  hooks are absent; and
* bind every new trusted component, literal, configuration byte and contract
  field into the proposed manifest and test plan.

Provide at least two technically viable launch-boundary options if two exist.
For each, analyze native-loader timing, bypass, TOCTOU, portability, non-Claude
behaviour and repository-only testability. Reject options that merely run
`unset`, inspect environment names, or start a cleansing utility after an
untrusted loader has already acted and then claim that this prevents pre-entry
execution.

If no design can satisfy the existing constraint through the client's ordinary
execution path, say so. Identify the minimum typed maintainer decision or
baseline amendment required; do not conceal the gap as a residual risk.

## 4. Required correction for R4-D1-2

Reconcile the hook-timing claim with every parameterized act, especially
A1-12. The corrected proposal must:

* enumerate every literal and parameterized catalogue entry and identify when
  its final command text and argv first become knowable;
* state separately what the client hook inspects before the entry starts, what
  the in-process canonical policy inspects before X-1, and what it inspects
  immediately before each launch;
* ensure no option is called compliant with pre-start inspection of every
  semantically complete command when a runtime value does not yet exist;
* compare viable remedies, including moving the typed value to a separately
  inspected invocation, changing invocation/session granularity, eliminating
  runtime textual substitution in favour of a reviewed typed operation, or a
  narrowly stated amendment to the pre-start-inspection requirement;
* analyze each remedy against the retained-root/session lifecycle, exact stream
  capture, stop transition, command-text/argv record contract, canonical guard
  decision, and the prohibition on caller-supplied arbitrary argv;
* rewrite D-1 so it distinguishes fixed literal text, reviewed templates,
  typed runtime instantiation and executed argv, and states truthfully which
  layer inspects each representation and when; and
* revise the option matrix, recommendation, threat analysis, record fields,
  interfaces, tests, manifest effects, rollout and maintainer decisions to
  match the selected correction.

Do not assume that inspecting a template is equivalent to inspecting its final
instantiation. If satisfying the original client-hook criterion is impossible,
make the minimum amendment an explicit maintainer choice and show the security
property that replaces it.

## 5. Deliverables

1. Amend in place:
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`.
   Preserve its provenance and add a dated remediation note identifying
   `R4-D1-1` and `R4-D1-2`; do not rewrite the original handback.
2. Create:
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md`.
   It must satisfy implementation-plan §16.3, map each finding to exact amended
   sections, disclose every unresolved proof obligation and maintainer
   decision, and give Codex focused re-review questions.
3. Update only concise current-state pointers needed to return the remediation
   for review. Do not edit historical or archived records.

The amended proposal must give one recommendation only if it actually satisfies
its stated constraints. Otherwise return a decision-ready impossibility result
and the minimum maintainer choices. Neither form may claim a finding closed;
only independent review and Peter Duscha's later decision can do that.

## 6. Scope and prohibitions

This remains **documentation-only**. Do not change Python, hooks, hook tests,
manifest source, generated artifacts, the operational-evidence draft, §5's
command, configuration or any executable file. Do not implement a launcher,
guard bridge, catalogue, environment builder, parser, entry point, wrapper,
session transport, wiring or feature flag. Do not increment the manifest.

No test execution is required except documentation, link and diff checks. Do
not run a loader experiment, the hooks against a real command or secret name,
an interpreter-entry probe, `ssh`, `rsync`, or any operational component.
Repository source and committed synthetic tests may be read.

**No SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled write, reboot, verifier, evidence band,
harness `--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.**

Preserve unrelated worktree changes. A guard or tool refusal is a stop
condition and must not be routed around.

## 7. Return gate

Claude stops after the amended proposal, remediation handback and concise
pointer updates. Codex independently re-reviews both Blocking findings, the
corrected trust boundary, parameterized-act timing, non-Claude behaviour,
environment completeness and manifest implications. Peter Duscha then decides
whether to accept a design direction or request further remediation.

No implementation assignment exists until that decision is recorded. RP-11
remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.
