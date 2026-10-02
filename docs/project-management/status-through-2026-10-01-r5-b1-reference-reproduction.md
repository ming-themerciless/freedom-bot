# Superseded current action block — 2026-10-01

This is the verbatim current-action block from [`status.md`](status.md) while the
B1 reference reproduction assignment was active, preserved before the
B1-R3 baseline-contract verification remediation was made current.

---

**Current action.** Peter selected Option 1 and assigned Gemini a controlled
reference reproduction on this repository host, whose observed kernel, CPU and
bubblewrap facts match Claude's recorded reference. Gemini must re-observe them,
provision a wholly fresh pinned root in `/tmp`, use the accepted one-invocation
manifest gate, and retain `cc1.v` only if its SHA-256 is exactly
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`
([decision](../review/project-review-2026-10-01-p5-r5-rp11-r4-r1-acceptance-and-reference-reproduction-decision.md),
[prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-gemini-prompt.md)).
Any host-fact or digest mismatch stops. No `oracle-test` access or R-5 rerun is
authorized.

R-5 remains stopped, Blocking and unaccepted. RP-11 remains unwired and unmet;
`plan.is_executable=False`; and Package 5.0 remains not ready.
