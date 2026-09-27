# P5.0-R5 MD-4 — Residual-risk dispositions

**Date:** 2026-09-23  
**Decision:** accepted by Peter Duscha  
**Scope:** `R-5.0-10` through `R-5.0-16`

Peter Duscha explicitly accepts all seven residual risks on the terms stated in
the Phase 5.0 package plan. They remain active, tracked residual risks rather
than closed defects.

| Risk | Disposition | Required control or evidence |
|---|---|---|
| `R-5.0-10` | Accepted integrity boundary; retain in RAID. | Process termination, empty-cgroup proof, host inspection, Google-access revocation, unit hardening and deployed-artifact digest evidence remain mandatory. |
| `R-5.0-11` | Accepted fail-closed availability cost; retain in RAID. | Refusal behaviour and operational recovery must be rehearsed and evidenced. |
| `R-5.0-12` | Accepted combined-authority integrity boundary; enter in RAID. | External logs and backups remain the independent detection and recovery controls. |
| `R-5.0-13` | Accepted root-plus-authority integrity boundary; enter in RAID. | External evidence remains required; assurance enhancement `A-5.0-2` is not adopted. |
| `R-5.0-14` | Accepted fail-closed availability cost; enter in RAID. | Explicit cleanup/recovery must be rehearsed; automatic cleanup remains prohibited. |
| `R-5.0-15` | Accepted operator-trust integrity boundary; enter in RAID. | Separation and external evidence remain required; assurance enhancement `A-5.0-3` is not adopted. |
| `R-5.0-16` | Accepted fail-closed availability cost; enter in RAID. | Approval, install, deployment and rotation recovery paths must be rehearsed and evidenced. |

The recovery rehearsals for `R-5.0-11`, `R-5.0-14` and `R-5.0-16` are
mandatory feasibility evidence and must be repeated against actual production
journal code at the later implementation/release gate.

This decision does not waive MD-1, MD-2 or MD-3, does not close `P5.0-R5`, and
grants no implementation, deployment, host-access, reboot or production
authority.
