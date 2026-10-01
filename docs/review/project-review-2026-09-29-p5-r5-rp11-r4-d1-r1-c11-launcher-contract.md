# Codex independent re-review — C-11 launcher-contract remediation

Review ID: `C-P5.0-R5-RP11-I1-R3-R4-D1-R1-REV1`

Date: 2026-09-29

Reviewed returns:

* [`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
* [`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md)

Disposition: **one Blocking finding. R4-D1-2 is remediated in the design, but
R4-D1-1 remains open. Do not select LB-2 or approve the conditional O-2/D-1
direction from these bytes. Further documentation remediation and independent
re-review are required.** Peter Duscha remains the decision and acceptance
authority.

## Finding

### R4-D1-R1-1 — Blocking — LB-2 does not establish a closed pre-loader environment

The amendment correctly identifies PID 1 as the proposed boundary and correctly
states that an entry-process environment check is diagnostic only. But the
proposed unit does not actually construct the closed environment that the
design relies on.

Proposal §2.3 AS-6 says the unit receives the system manager's environment in
addition to the unit's `Environment=` entries and systemd-derived variables.
The proposed unit in §4.4.3 adds only `LC_ALL=C` and `PATH=/usr/bin`; it neither
clears nor exhaustively excludes manager-supplied names. Nevertheless §4.4.3
claims that no client-derived variable exists in the entry environment, §4.4.5
calls LB-2 prevention, and §7.9 treats any other name as a condition the Python
entry diagnoses. If the manager environment contains `LD_PRELOAD`,
`LD_AUDIT`, `GLIBC_TUNABLES`, or another native-loader input, it acts while
`/usr/bin/python3.12` is loaded, before §7.9 can run. The design has therefore
moved the original post-start-detection defect from the client environment to
the manager environment rather than demonstrating prevention of all unreviewed
loader state.

PO-8 does not close this design gap. Documentation, source review, or a host
drill can establish what the installed manager happens to pass, but cannot make
an open environment contract closed. Nor can the entry's exact-key check
provide prevention after the loader has acted.

**Required correction:** specify a mechanism that establishes the entry's
allowed environment before its dynamic loader runs, or narrow and justify the
trust boundary so every source of the manager environment is a reviewed,
root-controlled input bound by installation evidence. The correction must
state the exact systemd semantics relied upon, account for manager
`DefaultEnvironment`/runtime environment and systemd-generated variables, and
show how unexpected native-loader variables are prevented rather than merely
detected. Update AS-6, the LB-2 assessment, `rp11-entry-env/1`, PO-8, the unit
text/tests, manifest limits, rollout and conditional recommendation together.
If systemd cannot provide a closed allow-list before `execve`, LB-2 must not be
recommended without an earlier trusted launcher boundary.

## Re-review of the two controlling findings

* **R4-D1-1 remains open.** The timing model, rejection of post-start cleansing,
  explicit host-boundary decision and non-Claude analysis are materially
  improved. The recommended LB-2 realization, however, still does not prove
  that unreviewed loader state is absent before the enforcing process starts.
* **R4-D1-2 is remediated in the design.** Sections 5.4 and 6.6 now distinguish
  literals, templates, pre-bound and observed instantiations, and executed
  argv. D-2a makes every Pass A act literal; Pass B is truthfully excluded by
  M-11 because its runtime values and mid-session gate cannot meet the
  pre-start criterion. D-1 is conditional on those explicit maintainer
  choices and no longer equates template inspection with inspection of a
  runtime instantiation.

## Review conclusion

The return is not yet decision-ready because its sole conditional direction
depends on LB-2's unestablished pre-loader environment. No implementation,
hook, source, manifest, artifact, configuration or operational draft was
changed or tested by this review. Review activity was repository-local and
read-only except for this review record and concise current-state pointers.
No SSH, rsync, synchronization, network or host inspection, protected-artifact
access, secrets scan, operational path, commit or push occurred.

RP-11 remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.
