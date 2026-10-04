# Independent review — fresh R-5 successor R4 `cc1.v` HARD STOP

Date: 2026-10-04  
Reviewer: Codex  
Executor: Gemini  
Work ID: `C-P5.0-R5-RP11-FRESH-R5-R4`

Reviewed handback:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r4-handback.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r4-handback.md)  
SHA-256: `0302ee9dc76b1f1fb239058d97fb7c3516d5a422c1b3f78ba82b8dbff98ffdda`  
Length: 64,273 bytes

Controlling assignment SHA-256:
`7d472c0a2ca2b0a7efc0f42bd58c0d85bacbdef0911f1bbe9f6858a957b7e8cc`.
Runner SHA-256:
`4ef88bd6059af6624bea9c4155ab895076e6076d031efd6c0fe60f13a63be015`.

## Disposition

Gemini reached a valid, correctly closed **HARD STOP at S9**. The run is not
an R-5 PASS and must not be resumed or reclassified. Gemini's one-run authority
is consumed.

The evidence through S8 is useful and internally consistent: the wholly fresh
root was provisioned, HA-1 and HA-2 qualified, the same-invocation R-1/R-2
manifest gate passed, and all four normative outputs plus the committed listing
were byte-identical. S9 then correctly failed because the diagnostic `cc1.v`
was not byte-identical to its accepted fixture. S10 and S11 were correctly not
run, and the S12 closing record is present.

R-5 remains Blocking and unaccepted; D9-3 is not complete; RP-11 remains
unwired and unmet; `plan.is_executable=False`; PO-9 and PO-14 remain open; and
Package 5.0 remains not ready.

## Finding

### `FRESH-R4-HS-1` — Important — the exact `cc1.v` contract includes host-resource-selected GCC garbage-collector heuristics

The complete byte comparison reports exactly three edit ranges, all on one
diagnostic line:

```text
baseline: GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
actual:   GGC heuristics: --param ggc-min-expand=94 --param ggc-min-heapsize=2169
```

There is no other reported difference. The actual file is 5,119 bytes with
SHA-256 `cdc0fe118866d838a9b399d35975e7627e22b3f43e8ab2bfcdf9ed5ff19045f9`;
the baseline is 5,120 bytes with SHA-256
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.
These values are GCC's runtime-selected GGC parameters, so the diagnostic
stream incorporates host resource state that the build-root manifest does not
pin. This is consistent with the assignment's disclosed U-1 risk and with the
fact that every normative output remained byte-identical despite qualifying
kernel and CPU variation.

This explains the observed difference, but it does not make the run pass. R4
expressly retained byte equality as the only route through S9 and prohibited a
GGC-only exception. The immutable handback therefore remains a HARD STOP.

## Evidence checks

- The runner, assignment and handback identities match their accepted digests.
- The independence attestation precedes Step 1.
- The 50 reproduced S1.3 Git-status lines agree with the recorded line count
  and digest according to the runner's closed record.
- Local and synchronized-checkout controlled-file checks passed.
- The signed package resolution, 62-package cache accounting and root
  provisioning passed.
- The same-invocation manifest gate and regenerated-manifest comparison passed.
- `rp11-launch`, its map, `launch.s` and the x86-64 listing all match their
  frozen digests; the independent output check passed.
- S9 preserves the verifier's nonzero result and reports exact offsets, lengths
  and bytes without a causal override.
- S10 and S11 are consistently recorded as not run after the first terminal
  condition.
- `S12.end` and `RUN.end` are both `2026-10-03T23:49:28Z`; the closing record
  is the final content of the handback.

No remote host was accessed during this review. Retained paths
`oracle-test:/var/tmp/p5-r5-fresh-20261003T234834Z-4fc93046-*` were not read,
changed or deleted. No cleanup, retry, remediation or new run is authorized by
this review.

## Recommendation

Peter Duscha should accept the valid consumed HARD STOP and retain
`FRESH-R4-HS-1` against this immutable run. I recommend a repository-only
Claude remediation that makes the two GGC parameters explicit, reviewed build
inputs with fixed values, instead of weakening `cc1check.py` or adding a
pattern-based exception. That approach removes the host-resource input at its
source and keeps byte equality as the simple fail-closed rule.

The remediation should update the compile vector and all affected manifest,
fixture, runner, assignment and regression-test contracts; prove locally that
the parameters are present exactly once and cannot be caller-overridden; and
return for independent review. It must not access `oracle-test`, alter the
closed handback, clean retained paths, execute R-5 or authorize another Gemini
run. A fresh run should be considered only after remediation review and a new
maintainer acceptance/activation decision.
