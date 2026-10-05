# Authority — one-host H-1 design remediation R4

Date: 2026-10-04

Decision owner: Peter Duscha, Maintainer and Acceptance Authority

Recorded by: Codex

## Decision

Peter Duscha accepts Codex's D3-R3 re-review, closes
`OH-H1-D3-R2-2` as remediated and decides OH-D-10 as **Option A with
interruption route iii-a**.

The inactive H-1 design must grant the unprivileged operator only `start`.
The capture unit must consume that grant through the fixed root
`ExecStartPre=` step specified in D3-R3 and must obtain the PK not-authorized
post-check before `ExecStart=` may run. A failed consume step is a failed
start, not a pass. Manual interruption remains available only through the
executor's A-2-authorized root `systemctl stop` route.

Claude is authorized to perform the narrow repository-only R4 remediation
defined in [the R4 prompt](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r4-claude-prompt.md).

## Boundary

This authority permits repository documentation and read-only inspection of
non-secret repository files only. It grants no SSH, Git/network retrieval,
credential creation or installation, `oracle-test` or production-host access,
retained R4/R5 evidence inspection, upstream research, implementation, build,
package, privilege, `systemctl`, Polkit, installation, service/database,
H-0/H-1/H-2, ACT/DEACT, activation, evidence pass, rollback, cleanup, commit
or push authority.

The current workspace host is production and must not be used as a source,
controller, relay, destination, fallback or rollback target. Claude must stop
after revising the inactive proposal and writing its R4 handback. Codex then
independently re-reviews it. No H-1 design is accepted by this authority.

