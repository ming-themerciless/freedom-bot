# Claude prompt — remediate the LB-2 system-manager environment boundary

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D1-R2`

Date: 2026-09-29

Assignee: Claude, remediation author

Independent reviewer: Codex

State: **assigned repository-only, documentation and read-only analysis only.**
Stop after the amended proposal and remediation handback for independent Codex
re-review.

## 1. Objective

Remediate exactly the remaining Blocking finding in Codex review
`C-P5.0-R5-RP11-I1-R3-R4-D1-R1-REV1`:

* `R4-D1-R1-1`: the recommended LB-2 systemd unit adds `PATH` and `LC_ALL`
  but does not establish a closed environment before the dynamic loader starts
  `/usr/bin/python3.12`. Manager-level environment can therefore carry loader
  inputs into the enforcing process before its diagnostic check runs.

Do not implement a correction. Amend the existing proposal in place, create
the remediation handback named in §5, update concise current-state pointers,
and stop for independent review.

`R4-D1-2` is remediated at the design level. Preserve its literal/template,
knowability, D-2 and M-11 analysis unless a change required by this assignment
has an explicitly traced consequence for it. Do not reopen or broaden it.

## 2. Controlling inputs

Read completely before editing:

* `.agents/AGENTS.md`;
* the implementation-plan reading map, §0, §16 and §20;
* `docs/review/Handover information`;
* the original R4-D1 assignment;
* the R4-D1 proposal and both Claude handbacks;
* the R4-D1 Codex review;
* the R4-D1-R1 remediation assignment; and
* [Codex's controlling remediation re-review](project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md).

The earlier assignments' governing facts, environment-contract requirements,
unsafe non-solutions, restrictions and gates remain in force except where this
prompt expressly requires correction. The latest Codex finding controls over
the returned proposal.

## 3. Required correction

Replace LB-2's open manager-environment assumption with a complete account of
the state that exists **before the entry interpreter's loader runs**. The
corrected proposal must:

* state the exact systemd system-manager semantics relied upon for
  `Environment=`, `DefaultEnvironment=`, manager runtime environment,
  `PassEnvironment=`, `UnsetEnvironment=`, `User=`, PAM if applicable, and
  systemd-generated variables;
* distinguish environment sources configured in unit bytes from sources held
  by PID 1, injected through manager configuration or runtime APIs, derived by
  systemd, or added only after `execve`;
* enumerate every source that may reach the entry's `execve`, identify which
  source wins on collision, and identify when filtering occurs relative to
  that `execve`;
* state whether the proposed unit can construct a true allow-list before
  `execve`, rather than add or remove a finite set of names from an otherwise
  open manager environment;
* account at minimum for `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, loader
  debug/profile variables, `GLIBC_TUNABLES`, `MALLOC_*`, and platform-equivalent
  native-loader inputs without pretending that a deny-list is a closed set;
* treat the Python `rp11-entry-env/1` check only as diagnostic. It may verify
  the result, but it must never be credited with preventing a variable that the
  loader has already consumed;
* identify the earliest trusted component that establishes the entry
  environment, how its relevant bytes and configuration are bound, and what
  root-controlled state remains outside the manifest;
* state precisely whether ambient manager state is inside the chosen T-A
  threat scope. Do not silently redefine T-A merely to preserve LB-2;
* reassess the exact LB-2 unit, pass configuration, installation record,
  drop-in and manager-state checks, admission checks, rollback, and later host
  drill under that model; and
* preserve the distinction between a repository-testable configuration-text
  property, an installation-time check, a host proof obligation, and a
  prevention mechanism.

Update every dependent statement together: AS-6; §4.2 and §4.3 timing; LB-2
§4.4.3; the §4.4.5 comparison; non-Claude behaviour; the fail-closed matrix;
residual risks; `rp11-entry-env/1`; the interfaces; unit and boundary tests;
manifest coverage and limits; rollout/rollback; M-9/M-10/M-12 if affected;
PO-8 and any new proof obligations; the conditional recommendation; and the
proposal's limitation and state language.

## 4. Required outcome discipline

Use one of these outcomes, whichever the analysis supports:

1. **Corrected LB-2.** Specify a technically credible mechanism that creates
   the stated closed entry environment before `execve`. Give its exact unit or
   trusted-launcher contract and bind all new trusted inputs into the proposed
   evidence, tests and installation record.
2. **Narrowed trust boundary.** If LB-2 relies on PID 1 environment or other
   root-controlled state rather than excluding it, state that trust explicitly
   and show how every relevant source is reviewed and bound before the pass.
   Do not call an unreviewed ambient source prevention.
3. **LB-2 rejected.** If systemd cannot establish the required allow-list under
   the retained threat model, withdraw LB-2 as the conditional direction.
   Reassess LB-1 and LB-3 under the same pre-loader rule. If neither is ready,
   return a decision-ready impossibility result or the minimum new design
   decision; do not select a merely cleaner open environment.

Do not assume that a clean observation in one host drill proves a closed
contract. Do not propose an entry-process `unset`, environment-name check,
re-exec, or cleansing utility as prevention. Do not treat root ownership alone
as review of mutable manager runtime state. Do not claim that a finite
loader-variable deny-list covers future or platform-specific loader inputs.

The proposal may give one recommendation only if it satisfies its stated
threat model and pre-loader timing rule. Otherwise it must say that no
recommendation is ready and identify the minimum maintainer decision or design
work required.

## 5. Deliverables

1. Amend in place:
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`.
   Preserve its provenance and earlier remediation record. Add a dated R2 note
   identifying `R4-D1-R1-1` and every claim withdrawn or narrowed by this work.
2. Create:
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md`.
   It must satisfy implementation-plan §16.3, map the finding to exact amended
   sections, disclose all unresolved assumptions, proof obligations and
   maintainer decisions, and give Codex focused re-review questions.
3. Update only concise current-state pointers needed to return the remediation
   for review. Do not edit historical or archived records.

Neither deliverable may claim the finding closed. Only independent Codex
re-review and Peter Duscha's later decision can do that.

## 6. Scope and prohibitions

This remains **documentation-only**. Do not change Python, hooks, hook tests,
manifest source, generated artifacts, the operational-evidence draft, §5's
command, systemd or polkit files, configuration, or any executable file. Do not
implement a launcher, unit, guard bridge, catalogue, environment builder,
parser, entry point, wrapper, session transport, wiring or feature flag. Do
not increment the manifest.

No test execution is required except documentation, link and diff checks. Do
not run a loader experiment, interpreter-entry probe, hook against a real
command or secret name, `systemctl`, `systemd-run`, `loginctl`, `busctl`,
`sudo`, `ssh`, `rsync`, or any operational component. Repository source and
committed synthetic tests may be read.

**No SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled write, reboot, verifier, evidence band,
harness `--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.**

Preserve unrelated worktree changes. A guard or tool refusal is a stop
condition and must not be routed around.

## 7. Return gate

Claude stops after the amended proposal, R2 handback and concise pointer
updates. Codex independently re-reviews whether the selected boundary prevents
unreviewed loader state before the entry starts, the exact system-manager
environment semantics, threat-scope consistency, non-Claude behaviour,
manifest limits and the honesty of any conditional recommendation. Peter
Duscha then decides whether to accept a design direction or request further
remediation.

No implementation assignment exists until that decision is recorded. RP-11
remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.
