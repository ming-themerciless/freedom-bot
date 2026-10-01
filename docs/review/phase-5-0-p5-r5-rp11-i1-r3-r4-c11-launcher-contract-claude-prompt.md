# Claude prompt — C-11 guard-preserving capture and pinned launcher-environment design

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D1`

Date: 2026-09-29

Assignee: Claude, design author

Independent reviewer: Codex

State: **assigned repository-only, documentation and read-only analysis only.**
Stop after the decision proposal and handback for independent Codex review.

## 1. Objective

Produce a decision-ready design that resolves the two remaining RP-11 blockers
without implementing or wiring either operational pass:

1. **C-11:** specify how §5's exact secret-excluding `rsync` is issued through
   RP-11 capture without hiding from, weakening, duplicating inconsistently or
   bypassing `guard-secrets.py` and `guard-git.py`; and
2. **Pinned launcher environment:** specify the exact environment supplied to
   every RP-11-launched `rsync` and `ssh`, with no inherited, inferred or
   unreviewed variable.

The proposal must be concrete enough for Peter Duscha to select an option and
for a later bounded implementation prompt to name exact files, interfaces,
tests and manifest effects.

## 2. Governing facts

The design must preserve all of these facts rather than silently choosing
around them:

* §5 fixes one plain `rsync` argv and forbids changing, reordering or wrapping
  it merely to obtain guard approval.
* The current secrets hook recognizes the exemption only when the inspected
  Bash command is exactly one plain `rsync` invocation. A wrapper command is
  intentionally not exempt.
* `StreamCaptureLauncher` starts one exact argv with `shell=False`, separate
  stdout/stderr capture, `stdin=/dev/null`, `cwd=/`, `close_fds=True`, and an
  explicit caller-supplied environment. It is unwired and unarmed by default.
* A design that invokes the guard only as an advisory subprocess, copies its
  rules by hand, or lets the capture path choose whether to consult it is not a
  solution: the guarded direct path and captured path could diverge.
* A guard refusal is a stop condition. The design must not recommend altering
  quoting, hiding operands, changing tool shape or retrying through another
  path after refusal.
* Secret values and files must not be read to prepare this proposal. In
  particular, do not inspect `.env`, private keys, agent sockets, credential
  files or host authentication state.
* RP-11 remains unwired and unmet. No proposal may claim that a design decision
  alone satisfies it or makes either pass executable.

## 3. Required C-11 analysis

Document the complete trust boundary from an operator/client tool request to
the exact argv that `StreamCaptureLauncher` would execute. Provide at least two
technically viable options and assess each against:

* one canonical policy implementation rather than independently drifting
  copies;
* whether the client `PreToolUse` hook inspects the semantically complete
  command before any process or capture-root mutation;
* whether the capture mechanism can execute any argv that the direct guarded
  path would refuse;
* fail-closed behavior for malformed payloads, unknown tools, policy-loading
  failure, hook absence, version/digest mismatch and guard refusal;
* TOCTOU and substitution risk between validation and execution;
* how exact argv identity is bound into the per-act RP-11 record;
* applicability to both `guard-secrets.py` and `guard-git.py` without granting
  an arbitrary wrapper exemption;
* compatibility with non-Claude agents, which remain bound by
  `.agents/AGENTS.md` even when they do not run Claude hooks;
* manifest coverage and which bytes must invalidate the reviewed digest; and
* testability without reading secrets, contacting a host or issuing a real
  synchronization.

Explicitly reject unsafe or non-solutions, including a blanket capture-wrapper
allowlist, shell-string reconstruction, a second unguarded launcher, trusting a
boolean such as `guard_passed=True`, and changing §5's command to evade the
existing hook.

Give one recommended option with a precise reason. If no option can meet every
governing constraint, say so and identify the minimum maintainer decision or
baseline amendment required; do not manufacture a solution.

## 4. Required launcher-environment contract

Propose a closed, typed environment contract separately for `rsync` and `ssh`.
For every variable considered—including `PATH`, `HOME`, `LANG`, `LC_ALL`,
`TERM`, `SHELL`, `SSH_AUTH_SOCK`, `RSYNC_RSH`, `SSH_CONFIG`, proxy variables and
any locale or authentication input—state exactly one disposition:

* fixed reviewed literal;
* typed maintainer input whose value is digest-bound and validated before X-1;
* deliberately absent; or
* prohibited.

The design must define:

* exact key sets, value grammar and maximum lengths;
* duplicate, empty, NUL, `=` and unexpected-key refusal;
* whether authentication can function with the proposed environment without
  reading a credential or inheriting ambient state;
* how an authorization binds any nonliteral value without recording secret
  content in the manifest, logs, records or handback;
* whether `HOME` is needed for SSH configuration or known-host lookup and, if
  so, which reviewed files are relied on without reading them in this pass;
* whether `SSH_AUTH_SOCK` is required, and how a dynamic socket can be
  authenticated and pinned without inspecting it now;
* how `rsync`'s child `ssh` receives the same reviewed contract;
* safe operator-facing refusal classifications; and
* exact tests for an empty inherited environment, missing required input,
  extra variables, mutated values, and direct-versus-captured equivalence.

Do not select an authentication mechanism merely because it is common. Where
the current repository does not establish the deployed mechanism, make that a
typed maintainer decision with options and consequences.

## 5. Required deliverables

Create:

1. `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`,
   containing the options, threat analysis, recommendation, environment matrix,
   proposed interfaces, test matrix, manifest impact, rollout/rollback and
   explicit maintainer decisions; and
2. `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md`,
   satisfying plan §16.3 and identifying the exact review questions for Codex.

Update only concise current-state pointers necessary to return the proposal for
review. Do not edit historical records.

## 6. Scope and prohibitions

This is **documentation-only**. Do not change Python, hooks, hook tests,
manifest source, generated artifacts, the operational-evidence draft, §5's
command, configuration, or any executable file. Do not implement a guard
bridge, environment builder, command entry point, wrapper, wiring or feature
flag. Do not increment the manifest.

No test execution is required except documentation/link/diff checks. Do not run
the hook against a real command or secret name as a probe; existing hook source
and committed synthetic tests may be read.

**No SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled write, reboot, verifier, evidence band,
harness `--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.**

## 7. Return and review gate

Claude stops after the proposal and handback. Codex independently reviews the
security boundary, feasibility, environment completeness, non-Claude behavior,
manifest implications and whether the recommendation actually preserves the
direct guard decision. Peter Duscha then chooses an option or requests
remediation. No implementation assignment exists until that decision is
recorded.

Throughout: RP-11 remains unwired and unmet; neither pass is executable or
authorized; `plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A
remains conditional; and Package 5.0 remains not ready.
