# P5.0-R5 MD-3 supervised-reboot requirement — 2026-09-23

Peter Duscha decides that the supervised reboot durability case is **mandatory
for P5.0-R5 harness-facsimile feasibility closure**. It may not be recorded as
Not Run or replaced by an accepted residual at this gate.

The required evidence is target-specific and disposable: on `oracle-test`, a
harness-created disposable generation containing an unresolved dispatch must
survive a supervised reboot with its journal, append-only attribute, immutable
seal and chain intact and re-verifiable. The later implementation/release gate
still requires the production-code rehearsal, including the corresponding
dispatch/outcome behavior.

This resolves **MD-3** and changes the package-plan allowance that previously
permitted JNL-02b to end as a reported check not run. It does not authorize the
reboot or any other host action. A separately bounded operational prompt,
independent pre-execution review and explicit maintainer authorization remain
required. P5.0-R5 remains Blocking, OD-62 G-A remains conditional,
`plan.is_executable=False`, and Package 5.0 remains not ready.
