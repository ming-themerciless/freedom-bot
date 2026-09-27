# P5.0-R5 MD-2 host-facts baseline decision — 2026-09-23

Peter Duscha decides that **`oracle-test` is the approved disposable target
whose host facts count for P5.0-R5 harness-facsimile feasibility evidence**.

Package-plan §8.1 observations made on the development host remain truthful
historical context for the design work that used them, but they do not satisfy
target-specific feasibility requirements. Every relevant environment fact must
be freshly observed on `oracle-test` during the separately authorized evidence
pass and bound to that pass's reviewed target identity and artifacts. A fact
that differs from the development-host record is reported as a target fact; it
is not normalized away or silently carried forward.

This resolves **MD-2**. It does not itself authorize SSH, synchronization,
inspection, provisioning, database access, controlled mutation, verifier or
evidence-band execution, reboot, protected-artifact access or `--execute`.
P5.0-R5 remains Blocking, OD-62 G-A remains conditional,
`plan.is_executable=False`, and Package 5.0 remains not ready.
