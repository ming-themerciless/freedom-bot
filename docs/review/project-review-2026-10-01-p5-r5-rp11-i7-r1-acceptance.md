# I-7-R1 IC-1 environment-remediation acceptance — 2026-10-01

Decision ID: `C-P5.0-R5-RP11-I1-R3-R4-I7-R1-A1`

Peter Duscha accepts Claude's narrow I-7-R1 remediation on Codex's independent
recommendation. Codex found no Blocking, Important or Optional finding in the
returned exact-environment change. Finding `I7-R1-1` is **Closed as
remediated**, and D-2 is accepted as implemented.

[Independent re-review](project-review-2026-10-01-p5-r5-rp11-i7-r1-ic1-environment-remediation.md).

IC-1 now defines the ordered ten successful `execve` calls and compares each
complete environment as an exact name/value mapping for its controlled
checkout. Missing, changed, extra, duplicate and malformed entries fail. The
four compiler-driver additions are specified from `build.sh` and pinned-driver
inputs rather than learned from the trace. Both `/rp11/co` and
`/rp11/alt/checkout` are covered. The accepted derivation includes R1-D-1:
GCC's `prune_options` drops the earlier `-fno-pic` when the later `-fno-pie`
cancels it through the driver's `Negative()` cycle.

Codex independently ran 368 focused IC-1 tests and the combined launcher
source/evidence suite (4,004 passed), Python compilation and `git diff
--check`. The toolchain-dependent suite reported 12 explicit skips because no
`RP11_LAUNCH_BUILD_ROOT` was named in the review session; those skips were not
treated as passes. Claude's handback records the fresh pinned-root R-1, R-2,
both IC-1 variants and T-L11/T-L10 evidence. The accepted manifest is version
28 with aggregate digest
`02d660c3bb8cd030a36ae1ece70da0de1756ca3052f3de74c89a15279a5c5abb`.

This acceptance closes only the I-7-R1 return gate. It does **not** authorize
R-5, SSH, `oracle-test`, synchronization, provisioning, installation, H-1/H-2,
PO-14 discharge, RP-11 wiring, a controlled write, an evidence band, harness
`--execute`, or an operational pass. R-5 still requires a separate maintainer
assignment to an independent party and must actually vary and record at least
one of HA-1 … HA-3; every unexplained difference is a hard stop.

PO-9 and PO-14 remain open; RP-11 remains unwired and unmet; neither pass is
executable or authorized; `plan.is_executable=False`; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not ready.

No host access, execution, repository commit or push occurred in recording
this decision.
