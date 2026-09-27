# Maintainer acceptance — R8-R4 review and R8 finding dispositions — 2026-09-22

Peter Duscha accepts Codex's independent R8-R4 review and records the following
decisions.

1. **C-P5.0-LAB-I3-R8-R4 is accepted.**
2. **LAB-I3-R8-R3-ROLLBACK-1 is Closed, remediated.** No rollback of R8-R3 is
   wanted. The corrected documentation stands; no reverse patch is to be
   constructed and no file is to be restored from `HEAD`.
3. **LAB-I3-R8-R3-WORDING-1 is Closed, remediated.** The corrected distinction
   between reference and access is accepted.
4. **LAB-I3-R8-R2-GUARD-1 is Closed as a documented and accepted procedural
   violation.** The guard refusal remains part of the historical record; the
   later altered scan did not cure it. No repeat secrets scan is required, no
   guard or rule change is authorized, and the violation does not invalidate
   the underlying R8 operational evidence. This is acceptance of the recorded
   disposition, not retroactive compliance.
5. **LAB-I3-R8-R2-COUNT-1 is Closed, remediated.** The accepted statement is
   960 candidate descriptions, two reproducing `f4120970…`, representing 612
   distinct calculations, one reproducing that value.
6. **LAB-I3-R8-AGGREGATE-1 is Closed, remediated with a retained limitation.**
   No byte of the measured 50-file set differs between the records and both
   values are reproducible under documented alternative calculations. The
   historical R6 calculation and historical cause of the divergence remain
   unknown and must not be inferred. That limitation is accepted as
   non-blocking for the R8 operational evidence.

These decisions do not close **LAB-I3-R8-R2-ROLLBACK-1**, which is assigned to
Claude under C-P5.0-LAB-I3-R8-R5 and remains Open, Important pending remediation
and independent Codex re-review. They do not close either R6 Blocking finding,
close I3, approve a digest, authorize `--execute`, change
`plan.is_executable=False`, advance Package 5.0, initialize V7, perform V8 or
V10, or authorize any action on `oracle-test`.

