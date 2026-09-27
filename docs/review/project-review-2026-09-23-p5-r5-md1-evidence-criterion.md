# P5.0-R5 MD-1 evidence-criterion decision — 2026-09-23

Peter Duscha decides that **P5.0-R5 may close on independently reviewed
harness-facsimile feasibility evidence from the approved disposable target**.
Evidence from the actual production journal code remains mandatory at the later
implementation/release gate.

The two evidence classes must remain explicit and must not be substituted for
one another:

- feasibility evidence establishes that the reviewed mechanisms can be built
  and exercised safely on the approved disposable target;
- production-code evidence establishes that the implemented writer, journal
  administration tool, coordinator and migration enforce the accepted
  contract, and is required before implementation/release acceptance.

This resolves **MD-1**, the readiness-versus-implementation criterion split
identified by the P5.0-R5 evidence reconciliation. It breaks the circular
dependency in which production implementation waited on OD-62 while OD-62
waited on P5.0-R5. It does not close P5.0-R5, make OD-62 G-A binding, approve a
digest, authorize implementation or migration `0014`, confirm A-5.0-5, resolve
C-S4-3 or C-7, or authorize any host, database, verifier, evidence-band,
reboot or `--execute` action.
