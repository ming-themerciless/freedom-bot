# Acceptance — R5 H-0 completeness remediation R3

Date: 2026-10-06

Decision owner: Peter Duscha, Product Owner and Acceptance Authority

Independent reviewer: Codex

## Decision

Codex independently re-reviewed Claude's cumulative R3 proposal and durable
handback and found no Blocking, Important or Optional issue. Peter Duscha
accepts that recommendation and the cumulative R3 proposal as the controlling
inactive design amendment.

R2 findings `R2-F1`, `R2-F2` and `R2-F3` are closed as remediated. In
particular, the accepted design now has:

- a closed, fail-safe `.git` structural contract with explicit rejection of
  redirecting, replacing, executing, importing and borrowed-state mechanisms;
- an authenticated symlink inventory and no-follow source-consumption contract
  under which every repository symlink is non-consumable; and
- a retained-evidence policy that treats digests as authentication and
  description, never as reproduction or cleanup eligibility.

Peter also accepts the explicitly stated Class T residual in SC-6: those tools
are not system-call confined, and their admission rests on T-1 through T-6 and
the accepted `ubuntu` ownership boundary. This is not authority to weaken any
per-slice check.

## Effect and limits

The R3 proposal supersedes R2 as the accepted cumulative design basis and
records decisions D-1 through D-7 and the disposable-Test lifecycle policy.
It does not itself execute H-0G, inspect or remove retained paths, recreate the
normal workspace, begin OH-S2, install anything, or activate H-1/H-2.

H-0G is the next operational slice and requires its own exact prompt,
authority, work ID and exclusive evidence path. Its executor may report only
`H-0G PASS` or a defined `HARD STOP`; composition with R5 is a later independent
reviewer act. Cleanup enumeration, cleanup, workspace recreation, OH-S2 and
all later slices remain separately gated.

## Review evidence

The independent review checked the R3 authority and prompt pins, the complete
R3 proposal and handback, the R2 findings, the active restrictions and the
relevant implementation-plan gates. The recorded prompt, authority and
proposal SHA-256 values were reproduced, and `git diff --check` passed. No
remote host, retained evidence or secret was accessed, and no application
test, build, cleanup or operational command was run.

## Next controlled step

Prepare and issue the narrow repository-free H-0G assignment specified by R3
§11. It must use one forwarding-disabled, non-interactive SSH execution
connection, a fresh exclusive evidence path, and the R3 anchor/exit contract.
After its terminal return, independent Codex review decides composition with
R5 before any cleanup lifecycle step or OH-S2 authority is considered.

