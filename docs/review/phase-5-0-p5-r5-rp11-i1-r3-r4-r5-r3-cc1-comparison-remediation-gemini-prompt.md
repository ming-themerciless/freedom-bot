# Gemini prompt — R-5 R3 `cc1.v` comparison remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-R3`

Date: 2026-10-01

Assignee: Gemini

Status: **authorized repository-only remediation; no host or R-5 rerun authority**

## 1. Context and objective

Gemini's R2 remediation correctly added the same-invocation R-1 manifest gate
before R-2/IC-1 and corrected the stopped R-5 handback. Independent Codex
review reproduced the repository results: 4,015 tests passed, 12
toolchain-dependent tests skipped because no accepted local root was named,
Python compilation succeeded, and `git diff --check` was clean.

R2 is not yet acceptable because the optional `cc1.v` comparison helper does
not implement the evidence contract it and the handback claim:

1. `cc1check.py` reports differing lines but not exact differing byte offsets
   or byte ranges. Its `byte_diff` label is never emitted.
2. An arbitrary caller-supplied regex and description can classify a changed
   line as explained and change the verdict to `PASS`. A pattern match is not
   evidence that a freshly recorded HA input caused the changed bytes.
3. The test named `test_cc1check_explained_difference_permits_pass` endorses
   that unsafe behavior by converting a textual label into a passing verdict.
4. The R2 handback therefore overstates both byte-level comparison and causal
   verification.

The accepted baseline `cc1.v` bytes remain unavailable. This task must make
the repository helper conservative and truthful; it must not invent a causal
explanation, recover evidence by assertion, or rerun R-5.

## 2. Required context

Before changing anything, read:

1. `.agents/AGENTS.md` completely;
2. the implementation-plan reading map, §0, §13, §16, §17 and §20;
3. `docs/review/Handover information`;
4. the accepted D2 design §§5.3.2–5.3.8 and §5.12.3;
5. LD-8 and the accepted I-7/I-7-R1 records;
6. the R-5 assignment, stopped R-5 handback, R2 prompt and R2 handback;
7. `infra/rp11-launch/verify/cc1check.py`,
   `infra/rp11-launch/buildroot/enter.py`, and the focused launcher tests; and
8. this prompt.

Inspect `git status` and preserve every unrelated change. The accepted
launcher source, image contract, toolchain lock, build-root manifest, expected
digests, committed listing, XD and T-L10/T-L11 contracts are immutable.

## 3. Required repository remediation

### 3.1 Make the comparison helper fail closed

Change `cc1check.py` so that it:

* reports the SHA-256 digest of each input;
* reports exact differing byte offsets or contiguous byte ranges, including
  the baseline and actual byte values at each reported difference;
* may additionally report useful line context, but must not describe a
  line-only diff as a byte-level diff;
* returns `PASS` only when the two byte streams are exactly identical; and
* returns `HARD_STOP` for every non-identical pair until a separately reviewed
  and accepted causal-evidence contract exists.

Remove the regex-based mechanism that converts a caller-provided label into an
explained difference or passing verdict. Do not replace it with another
free-form label, allowlist, callback, command-line flag or unauthenticated
metadata mechanism. A helper may record a proposed explanation as
non-authoritative context only if the verdict remains `HARD_STOP`, but the
simplest acceptable implementation is to omit explanations entirely.

Keep the CLI deterministic: identical inputs exit 0; different inputs exit 1;
missing or unreadable inputs produce a distinct usage/input failure and do not
produce `PASS`.

### 3.2 Replace the unsafe and misleading tests

Add or amend focused tests proving at minimum:

* identical byte streams produce equal digests, no differences, `PASS`, and
  CLI exit 0;
* a one-byte substitution reports its exact offset and both byte values and
  produces `HARD_STOP` / CLI exit 1;
* insertion and deletion, including at end of file, report exact ranges
  without losing or misaligning subsequent differences;
* non-UTF-8 bytes are compared and reported exactly rather than hidden by
  replacement decoding;
* no caller-provided regex, explanation string or other unauthenticated label
  can turn non-identical bytes into `PASS`; and
* missing input files fail without a passing verdict.

Correct the earlier “failing-before” orchestration test or its description so
it does not claim that the pre-remediation implementation was actually
executed when the test merely calls `prepare_checkout` directly. Retain a real
regression test through the `build` CLI path showing that manifest mismatch
prevents both checkout preparation and the build call. Preserve all valid R2
gate-ordering and fail-closed tests.

### 3.3 Correct the R2 handback

Amend the R2 handback to:

* withdraw the claims that the former helper performed byte-level analysis
  and verified causal explanations;
* describe the remediated helper's exact, conservative behavior;
* correct the failing-before description so it distinguishes an illustrative
  legacy-flow simulation from an executed historical failure, or replace it
  with the actual CLI regression evidence required above;
* retain the accurate R-1/R-2 orchestration implementation and verification;
* state that the accepted baseline bytes are still unavailable and therefore
  the `cc1.v` difference remains unresolved; and
* retain the stopped status and fresh-rerun requirement for R-5.

Do not alter either recorded `cc1.v` digest and do not assert that HA-1, HA-2
or HA-3 caused the difference.

## 4. Verification

Run repository-local checks only:

1. the focused gate and `cc1.v` tests;
2. `tests/test_rp11_launch_source.py`;
3. the complete `tests/phase_5_0_evidence` suite;
4. `tests/test_rp11_launch_toolchain.py` only if an already available accepted
   local root is explicitly named; otherwise report all skips as unverified;
5. Python compilation for every changed Python file;
6. `git diff --check`; and
7. generated-artifact checks only if a serialized contract actually changes.

Do not provision, download or reconstruct a build root during this stage. Do
not cite R2 or earlier figures as fresh R3 results.

## 5. Authority and restrictions

Gemini may edit only:

* `infra/rp11-launch/verify/cc1check.py`;
* `tests/test_rp11_launch_gate.py`, or one narrowly focused replacement test
  module if separation is clearer;
* the R2 remediation handback corrections required by §3.3; and
* one R3 remediation handback named in §6.

Do not change `enter.py` unless a focused test exposes a regression in the R2
gate. If that happens, stop and report it rather than expanding scope.

No SSH, rsync, `oracle-test` access, `sudo`, package operation, download,
provisioning, build-root creation, host inspection, service or database
action, launcher build/installation, H-1/H-2, PO-14 discharge, RP-11 wiring,
controlled write, reboot, evidence band, harness `--execute`, operational
path, protected-artifact access, secrets scan, commit or push is authorized.

Do not change launcher source, `toolchain.lock`, `build-root.manifest`,
`expected.sha256`, the committed listing, manifest version/digest, XD,
T-L10/T-L11, current governance documents or operational authorization
drafts. If remediation requires any forbidden change, stop and report the
conflict.

## 6. Required handback and stop gate

Write:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-handback.md`

Include:

* requirements implemented and files changed;
* before/after SHA-256 for every changed file;
* the exact byte-difference representation and boundary behavior;
* proof that no non-identical input can receive `PASS`;
* corrected R2 handback claims;
* fresh test commands, counts, skips and results;
* checks not run and why;
* unresolved baseline evidence and residual trust;
* security, configuration, deployment and rollback implications; and
* proposed independent-review focus.

Stop after writing the repository handback. Do not access `oracle-test`, seek
baseline bytes, reproduce the baseline, or rerun R-5. Codex independently
reviews R3; Peter alone may accept it and decide the separately scoped method
for obtaining comparable baseline evidence and authorizing a fresh R-5 run.
