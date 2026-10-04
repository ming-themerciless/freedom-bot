# Claude task — R4 `cc1.v` determinism audit and remediation

Work ID: `C-P5.0-R5-RP11-FRESH-R5-R4-D1`  
Assignee: Claude  
Scope: repository-only analysis, implementation, tests and handback  
No `oracle-test` access, cleanup or R-5 execution

## Governing finding and decision

Read completely:

1. [`project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop.md`](project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop.md);
2. [`project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop-acceptance-and-remediation-authority.md`](project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop-acceptance-and-remediation-authority.md);
3. the immutable R4 handback and its controlling assignment; and
4. the accepted static-launcher design, build-root, IC-1, baseline-fixture and
   exact-comparison records they cite.

Remediate Important finding `FRESH-R4-HS-1`. R4 reproduced every normative
artifact but stopped because the diagnostic `cc1.v` contained GCC GGC values
selected from host resource state:

```text
baseline: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
actual:   --param ggc-min-expand=94  --param ggc-min-heapsize=2169
```

## Required outcome

Audit the complete `cc1.v` byte contract, not only the observed line. Identify
every field whose bytes can depend on the outer host, runtime resources,
filesystem location, locale, environment, driver state or other input not
already pinned by the build-root and IC-1 contracts.

Implement the smallest fail-closed correction that removes uncontrolled inputs
at their source. The preferred design is to make the two GGC parameters
explicit, fixed, reviewed compiler inputs. You must verify the precise GCC
semantics and command spelling from repository-controlled or pinned-toolchain
evidence before implementing it. Do not assume that merely adding arguments
leaves `cc1.v` unchanged: account for every resulting diagnostic-byte change.

The completed remediation must:

- preserve the four normative launcher artifacts and their frozen semantics;
- preserve exact byte equality as the `cc1check.py` PASS rule;
- contain no regex, ignored range, normalization, alternate accepted hash,
  caller-supplied exception or causal-label override;
- ensure each fixed parameter is supplied exactly once and cannot be
  caller-overridden later in the compiler vector;
- update every genuinely affected source, IC-1 expectation, fixture, manifest,
  generated artifact, runner resource, pin, assignment contract and test;
- add regression tests for absence, duplication, changed values, reordering or
  later override of the fixed inputs, plus mutation of every new contract;
- document the complete dynamic-field audit and distinguish normative outputs
  from diagnostic provenance; and
- leave the closed R4 handback and independent review unchanged.

If a correct new baseline fixture or frozen output cannot be derived and
verified using already available, authorized local resources, do not fabricate
or reconstruct it from prose. Return a precise blocker and a minimal proposed
bounded acquisition or reference-reproduction step for later maintainer
decision. Do not access the network or any remote host to remove that blocker.

## Boundaries

You may change repository source, tests, generated review artifacts and draft
successor-assignment material only as required by this remediation. You may run
local, non-operational tests and use already present repository-host tools and
non-secret caches. You may not:

- access `oracle-test` or any production/staging system;
- inspect, modify or delete retained R4 paths;
- provision or download a new toolchain or package;
- run R-5, the evidence harness with `--execute`, or any operational check;
- install packages, use privilege, alter services/databases/configuration, or
  read secrets;
- activate Gemini, grant host authority, commit or push; or
- close `FRESH-R4-HS-1`, accept R-5, wire RP-11 or advance Package 5.0.

Do not silently weaken an accepted contract. If full determinism would require
a material change to the accepted evidence boundary, stop with a decision-ready
analysis rather than selecting that change yourself.

## Verification and handback

Run focused source, manifest, runner and toolchain tests available locally;
syntax/compile checks; deterministic regeneration checks for every generated
artifact touched; and `git diff --check`. Report unavailable checks and all
skips accurately. Audit the final diff for unrelated changes and stale pins.

Write the handback to:

`docs/review/phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-handback.md`

The handback must include:

- the dynamic-field audit and evidence for each disposition;
- exact changed paths, identities and contract/digest changes;
- proof that normative artifacts are preserved or an explicit blocker;
- all commands, results, failures, skips and unavailable checks;
- any proposed successor assignment and unresolved maintainer decisions; and
- an explicit statement that no remote access, cleanup or R-5 execution
  occurred.

Stop after the handback. Codex independently reviews the result before any
successor assignment can be activated.
