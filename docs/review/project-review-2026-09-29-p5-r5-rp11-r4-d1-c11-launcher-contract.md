# Codex independent review — C-11 and launcher-environment design

Review ID: `C-P5.0-R5-RP11-I1-R3-R4-D1-REV1`

Date: 2026-09-29

Reviewed returns:

* [`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
* [`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md)

Disposition: **two Blocking findings. Do not select O-2 or approve D-1 from
these returned bytes. Remediation and independent re-review are required.**
Peter Duscha remains the decision and acceptance authority.

## Findings

### R4-D1-1 — Blocking — the ambient dynamic-loader environment acts before the in-process gate

The proposed entry is started by the operator's ordinary shell with its ambient
environment. The proposal acknowledges that loader variables reach that
process, but treats a Python-level check for prohibited variable names as a
refusal that protects the boundary (proposal §6.9 R-4 and §7.7). That check is
too late. A dynamic loader processes variables such as `LD_PRELOAD` before the
Python interpreter starts and therefore before `rp11_cli`, manifest
verification, policy loading, admission, or the proposed refusal can execute.
Code selected by the ambient loader can bypass or alter every in-process check.

This invalidates the claims that the in-process gate "cannot be bypassed," that
hook absence has no effect on enforcement, and that O-2 is fail-closed for
non-Claude callers. `-E -s` controls Python environment and user-site handling;
it does not neutralize the native loader that has already started the process.

**Required correction:** specify a reviewed launch boundary that prevents
unreviewed loader state from reaching the trusted entry before that entry can
act. Bind that boundary into the exact client-inspected invocation, manifest,
trust analysis and tests. A post-start name check may remain diagnostic but
must not be presented as prevention. Reassess other pre-entry ambient inputs
and executable/interpreter substitution under the same timing rule.

### R4-D1-2 — Blocking — the client hook cannot inspect the final parameterized command before process start

O-2 claims that the client hooks resolve the pass and inspect every
semantically complete command before any process starts (proposal §1, §4.2 C-3
and §6.2). But A1-12 is not complete at that point. Its value is obtained only
from A1-11's admitted stdout in the running capture session, substituted later,
and only then evaluated and parsed (proposal §6.6). The pre-tool hook can inspect
at most a template, not the actual command text or argv that will execute.

The same mismatch appears in proposed amendment D-1: it says every A1 command
text is fixed byte-for-byte in the catalogue and inspected by the client hooks,
while §6.6 expressly creates a runtime-substituted text whose digest is known
only later. The in-process re-evaluation is useful, but it does not satisfy the
assignment's separate criterion that the client hook inspect the semantically
complete command before any process starts.

**Required correction:** either redesign parameterization so the complete
reviewed text is available and inspected before the entry starts, or state
plainly that this criterion cannot be met and seek a narrowly stated maintainer
amendment. D-1 must distinguish literal catalogue texts from any typed runtime
instantiation and accurately state which layer can inspect each form and when.
The option matrix and recommendation must then be reassessed.

## Review conclusion

The proposal is otherwise careful about the closed catalogue, exact argv
binding, environment key classification, authentication uncertainty, manifest
effects, test design and retained gate state. Those strengths do not cure the
two trust-boundary contradictions above. Because each affects the core reason
for choosing O-2, this return is not decision-ready.

No implementation, hook, source, manifest, artifact or operational draft was
changed or tested by this review. Review activity was repository-local and
read-only except for this review record and concise current-state pointers. No
SSH, rsync, synchronization, network or host inspection, protected-artifact
access, secret scan, operational path, commit or push occurred.

RP-11 remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.
