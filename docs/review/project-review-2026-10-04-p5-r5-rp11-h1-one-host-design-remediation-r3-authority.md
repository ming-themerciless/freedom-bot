# Authority — one-host H-1 design remediation R3

Date: 2026-10-04

Decision owner: Peter Duscha, Maintainer and Acceptance Authority

Recorded by: Codex

## Decision

Peter Duscha accepts Codex's D3-R2 re-review and authorizes Claude to perform
the narrow repository-only design remediation defined in:

[`phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r3-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r3-claude-prompt.md).

Claude must remediate exactly Blocking findings `OH-H1-D3-R2-1` and
`OH-H1-D3-R2-2`, preserve the accepted OH-D-1 through OH-D-9 dispositions and
the reviewed D3-R1/D3-R2 work that held, and return a revised inactive proposal
for independent Codex re-review. `OH-H1-D3-2` and `OH-H1-D3-R1-1` remain open.

## Boundary

This authority permits repository documentation and read-only inspection of
non-secret repository files only. It grants no SSH, Git/network retrieval,
credential creation or installation, `oracle-test` or production-host access,
retained R4/R5 evidence inspection, upstream research, implementation, build,
package, privilege, `systemctl`, Polkit, installation, service/database,
H-0/H-1/H-2, ACT/DEACT, activation, evidence pass, rollback, cleanup, commit
or push authority.

The current workspace host is the production server. It must not be used as a
source, controller, relay, destination, fallback or rollback target for the
later one-host workflow.

Claude must stop after writing the repository-only remediation return. Codex
then independently re-reviews it. No H-1 design is accepted by this authority.
