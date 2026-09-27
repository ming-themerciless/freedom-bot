# P5.0-R5 MD-5 — Classifier correction prerequisite

**Date:** 2026-09-23  
**Decision:** accepted by Peter Duscha

Peter Duscha requires the journal-classifier contradictions identified in the
P5.0-R5 evidence reconciliation to be corrected and independently reviewed
before any evidence band is treated as executable.

The repository-only C-P5.0-R5-R1 remediation and its later independent review
may satisfy the correction prerequisite, but this decision does not itself
approve an executable plan, accept operational evidence, close P5.0-R5, or
grant implementation, host, database, reboot, deployment or production
authority. `plan.is_executable=False` remains controlling.

The next reconciliation decision is MD-6: either require JNL-40(b)'s second
host or `/etc/machine-id` rewrite, or accept `R-5.0-13` without that case.
Because MD-4 already explicitly accepted `R-5.0-13`, the consistent
recommendation is to accept it without making JNL-40(b) mandatory for P5.0-R5
closure, while retaining external-evidence controls and any later
production-gate requirements.
