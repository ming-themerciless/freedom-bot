# Fresh static-launcher R-5 PASS acceptance

Date: 2026-10-04  
Decision owner: Peter Duscha, Maintainer and Acceptance Authority  
Recorded by: Codex

## Decision

Peter Duscha accepts Codex's independent review and Gemini's complete R5 PASS
for work ID `C-P5.0-R5-RP11-FRESH-R5-R5`.

The static-launcher independent-rebuild procedure **R-5 is accepted**, and
**D9-3 is Complete**. The accepted evidence includes:

- a wholly fresh, separately provisioned pinned build root;
- same-invocation R-1 manifest equality immediately before R-2;
- passing IC-1/build-environment evidence;
- qualifying HA-1 and HA-2 variation;
- byte-identical image, map, listing and `launch.s` normative artifacts;
- byte-identical `cc1.v` diagnostic provenance after the accepted
  determinism remediation; and
- 12 corroborating tests with zero failures, errors or skips.

- [Gemini handback](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md)
- [Independent review](project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass.md)
- [Accepted assignment](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md)

## Scope of acceptance

This closes only the static-launcher reproducibility/build-environment
component R-5 / D9-3. It does **not** close the separately named package RAID
item `P5.0-R5`, which remains Blocking. It also does not discharge PO-9 as a
whole, PO-14, D9-4 or H-1; wire RP-11; make `plan.is_executable` true; approve
an evidence-harness execution digest; or make Package 5.0 ready.

Gemini's authority is consumed. No host, cleanup, H-1, installation, wiring,
operational, service/database, commit or push authority is created. The
retained R4 and R5 paths remain untouched. Cleanup, H-1 preparation and H-1
execution each require their applicable separate decision and review gate.

## Next controlled step

The next static-launcher step is preparation of a decision-ready H-1
installed-host evidence assignment for D9-4 and its prerequisites. Preparation
is not execution and is not authorized by this acceptance record.
