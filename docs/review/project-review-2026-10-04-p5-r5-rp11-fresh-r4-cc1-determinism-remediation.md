# Independent review — R4 `cc1.v` determinism remediation

Date: 2026-10-04  
Reviewer: Codex  
Implementer: Claude  
Work ID: `C-P5.0-R5-RP11-FRESH-R5-R4-D1`

Reviewed handback:
[`phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-handback.md`](phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-handback.md).

## Disposition

No Blocking, Important or Optional implementation finding remains. Claude's
remediation is technically sound and `FRESH-R4-HS-1` is ready to close on
Peter Duscha's acceptance.

The correction removes the uncontrolled host-resource input at its source:
`build.sh` supplies `--param=ggc-min-expand=100` and
`--param=ggc-min-heapsize=131072` exactly once. IC-1 checks the driver and
`cc1` argument vectors for the canonical tokens, alternate/duplicate values
and response files. `cc1check.py` remains unchanged and exact byte equality is
still the only PASS route.

The new 5,305-byte fixture, SHA-256
`e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a`,
has a bounded, independently checked provenance relation: removing exactly the
three insertions of the two fixed arguments yields the former 5,120-byte B1
fixture and its exact SHA-256
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.
The four normative artifact hashes and committed listing are unchanged.

## Independent checks

- Recomputed the changed build, lock, fixture, IC-1, runner, runner-test and R5
  assignment identities; they match the handback and R5 pins.
- Verified all 19 R5 Appendix C runner/resource/test hashes with
  `sha256sum --check`.
- Recomputed the fixture's inverse transformation and compared its digest with
  the former fixture obtained independently from `HEAD`; both are
  `b77f92dc…905b`.
- Inspected the compiler vector, complete diagnostic-field audit, IC-1
  enforcement and regression tests. No normalization, ignored range,
  alternate accepted hash, caller exception or verdict override was added.
- Reproduced **4,159 passed, 16 explicitly skipped**, with two known local
  pytest configuration warnings. Twelve existing toolchain checks and four
  new real-root determinism checks skipped because this Codex session has no
  `RP11_LAUNCH_BUILD_ROOT`. A skip is not a pass.
- Python compilation, POSIX-shell syntax, all runner-block Bash syntax and
  `git diff --check` passed.

Claude's real-root evidence is stronger than the locally available Codex
environment: Claude reports 4,175 focused passes with two R-1-verified existing
roots, eight final gated builds across the accepted variants, unchanged
normative hashes, exact fixture equality and successful IC-1. Codex could not
repeat those 16 root-dependent cases because those scratch roots are no longer
available in this session. The proposed R5 run remains the independent
different-host confirmation; this limitation is not evidence of a defect.

No remote host was accessed during this review. No retained path was inspected,
changed or deleted, and no R-5 action was executed.

## R5 draft review

The proposed R5 assignment is 140,080 bytes with SHA-256
`4073360b0894c212e5b5507249c011d1d4197c09af2094e877829fcb9b00a1e1`.
Its proposed identifiers are internally consistent:

- work ID: `C-P5.0-R5-RP11-FRESH-R5-R5`;
- handback:
  `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md`;
- runner: 58,905 bytes, SHA-256
  `5626a9ecfa8486b058cfe9ab1c45f163671827d77a7f4adb34a1e8b9145a9142`.

The substantive R4 procedure, first-terminal-condition behavior, exact
comparison and Antigravity same-task waiting contract are preserved. R5 adds
the new contract identities and refuses the consumed R4 resources. The draft
is technically ready after the controlled implementation files are committed.

## Recommendations on Claude's listed decisions

1. **Close `FRESH-R4-HS-1` as remediated.** The source, contract, diagnostic
   fixture, manifests, runner and regression tests agree.
2. **Confirm the proposed R5 identifiers.** They are unique and consistently
   pinned; changing them adds work without reducing risk.
3. **Authorize one focused commit of the controlled remediation and runner
   files before activation.** S1.4 intentionally requires those paths to equal
   `HEAD`. The commit must be checked by exact path list and post-commit
   controlled-path cleanliness.
4. **Retain the R4 remote paths for now.** They are forbidden inputs, the R5
   preflight measures the 4 GiB floor with them present, and their retention
   preserves supplementary evidence. Cleanup is unnecessary before R5 unless
   that preflight fails; no cleanup authority should be granted now.
5. **Add a dated amendment note to the accepted D2 design before activation.**
   Sections 5.3.3 and 5.3.4 still transcribe the pre-remediation vector. The
   amendment should record the two fixed parameters and cite this accepted
   remediation without rewriting historical text. This is documentation
   reconciliation, not another implementation cycle.
6. **Leave S10 at its accepted 12-test contract.** R5 itself performs the fresh
   target-host build and exact `cc1.v` comparison. Adding the four
   resource-limit tests to the operational run would duplicate that proof and
   expand an otherwise unchanged execution procedure.
7. After items 1–5 and the focused commit are recorded, accept the exact R5
   assignment and activate Gemini for one invocation using its resolved
   `/goal` prompt. No activation exists until that record is written.

These decisions are a normal consequence of changing an accepted compiler
contract. They do not reveal another systematic technical issue.
