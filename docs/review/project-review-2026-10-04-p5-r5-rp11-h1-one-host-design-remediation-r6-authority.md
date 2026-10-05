# Authority — one-host H-1 design remediation R6

Date: 2026-10-04

Decision owner: Peter Duscha, Maintainer and Acceptance Authority

Recorded by: Codex

## Decision

Peter Duscha accepts Codex's recommendation and decides OS-6 as follows:

Route iii-a is available only after the capture unit is `active`, its
`InvocationID` equals the consume journal's `run-start.invocation_id`, and the
consume journal contains a durable `consumed` line. Route iii-a is not
available while the unit is `activating` or during `start-pre`. A hung consume
step is bounded by the finite, fail-closed start timeout.

This decision amends the D3-R4 route-iii-a timing condition. It does not change
the fixed interruption literal, its executor, its A-2 authority, or its
§9.5.3 classification for a running pass.

Peter authorizes Claude to perform the narrow repository-only design
remediation defined in:

[`phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r6-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r6-claude-prompt.md).

Claude must incorporate OS-6 as a decided condition, remediate exactly
Blocking issue `OH-H1-D3-R5-1`, preserve the reviewed D3-R5 mechanism that
held, and return the revised inactive proposal for independent Codex re-review.

`OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain
open. This authority does not close or accept any finding or design.

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
after revising the inactive proposal and writing its D3-R6 handback. Codex then
independently re-reviews it. No H-1 design is accepted by this authority.
