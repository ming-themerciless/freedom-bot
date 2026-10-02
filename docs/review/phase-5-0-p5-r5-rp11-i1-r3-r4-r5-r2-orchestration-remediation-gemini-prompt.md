# Gemini prompt — R-5 R2 orchestration and evidence remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-R2`

Date: 2026-10-01

Assignee: Gemini

Status: **authorized repository-only remediation; no host rerun authority**

## 1. Context and objective

Gemini's resumed R-5 run reproduced the four accepted outputs across real
HA-1, HA-2 and HA-3 variation, but Codex cannot recommend acceptance because
two LD-8 stop conditions remain and one handback statement is wrong:

1. R-1 and R-2 were invoked as separate CLI commands. Contrary to its module
   documentation, `enter.py build` does not regenerate and compare the build-
   root manifest before starting R-2. The accepted D-2 interpretation requires
   the R-1 manifest vectors and R-2 to be consecutive entries made by one
   `enter.py build` invocation over the same root, with nothing intervening.
2. `cc1.v` changed from Claude's accepted digest
   `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`
   to Gemini's
   `cdc0fe118866d838a9b399d35975e7627e22b3f43e8ab2bfcdf9ed5ff19045f9`.
   The handback attributes this to kernel/CPU variation without an exact diff
   or causal derivation. LD-8 makes every unexplained intermediate difference
   a hard stop.
3. The handback says acquisition used snapshot `20260801T000000Z`; the accepted
   lock and provisioning code use `20261001T000000Z`.

This assignment remedies the repository orchestration and the returned record.
It does **not** rerun or accept R-5. Gemini must stop after the repository
handback so Codex can review the changed evidence mechanism before Peter
decides whether to authorize a fresh R-5 rerun.

## 2. Required context

Before changing anything, read:

1. `.agents/AGENTS.md` completely;
2. the implementation-plan reading map, §0, §13, §16, §17 and §20;
3. `docs/review/Handover information`;
4. the accepted D2 design §§5.3.2–5.3.8 and §5.12.3;
5. the active R-5 assignment and both Gemini handback versions in Git/worktree
   history available to this task;
6. the stopped-handback review and bubblewrap authority;
7. `infra/rp11-launch/buildroot/enter.py`, `provision.py`, their tests and the
   toolchain-dependent suite; and
8. this prompt.

Inspect `git status` and preserve every unrelated change. The accepted launcher
source, image contract, toolchain lock, build-root manifest, expected digests,
listing, XD and T-L10/T-L11 contracts are immutable in this remediation.

## 3. Required repository remediation

### 3.1 Make one build invocation enforce R-1 immediately before R-2

Change `enter.py` so the `build` and `ic1` CLI paths, in one Python process and
one invocation:

1. regenerate the manifest using the root's pinned `find` and `sha256sum`;
2. compare those exact bytes with the committed
   `infra/rp11-launch/build-root.manifest`;
3. fail closed before preparing or starting the build if they differ; and
4. only on equality, immediately prepare the checkout and start the accepted
   R-2 vector over the same root, with no externally callable or interactive
   step between the comparison and build entry.

The manifest output and equality verdict must be available to the caller's
record without weakening the build's stdout/stderr contract. Use a typed or
explicit result rather than an undocumented global. Do not silently make the
standalone `manifest` command sufficient evidence for this condition.

Keep the accepted interpretation precise: this is one host-side `enter.py`
invocation making consecutive bwrap entries over the same root; it is not a
claim that `find`, `sha256sum` and the shell run in one bwrap process.

### 3.2 Add regression and negative tests

Tests must demonstrate at minimum:

* a build invocation regenerates and compares the manifest before any checkout
  preparation or build process starts;
* exact equality permits the build;
* one-byte manifest drift refuses before R-2;
* a manifest-generation failure refuses before R-2;
* ordering is enforced, not inferred from independent fixture setup;
* both `build` and `ic1` use the same gate;
* existing R-1, R-2, R-4, IC-1 and toolchain tests remain meaningful; and
* the CLI reports enough evidence for the later R-5 handback to show that the
  gate ran in that same invocation.

Add a failing-before demonstration against the current implementation for the
missing gate. Do not weaken an assertion merely to preserve an old test.

### 3.3 Correct the R-5 record without claiming a pass

Amend
`phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-handback.md` to:

* change the acquisition snapshot to `20261001T000000Z` and explain that
  `provision.py` reads `archive_snapshot` from the accepted lock;
* withdraw the current overall PASS because the same-invocation condition was
  not met and `cc1.v` remains unexplained;
* retain the useful observed HA facts and matching four output digests as
  historical stopped-run evidence, clearly not the final R-5 record;
* retain the accurate repository-sync and package-install disclosures; and
* state that a completely fresh rerun is required after this remediation is
  independently reviewed and accepted.

Do not invent an explanation for `cc1.v`, and do not replace either digest.

### 3.4 Prepare the later `cc1.v` investigation contract

Add tests or a small repository-only comparison helper, only if genuinely
needed, that can compare two retained `cc1.v` byte streams and report:

* both SHA-256 values;
* the exact differing lines/bytes;
* whether each difference is explained by a freshly recorded HA input or by
  another named input; and
* a hard-stop verdict for every unexplained difference.

Do not assert that kernel or CPU variation explains the difference merely
because both varied. The later rerun must retain its `cc1.v`. If the accepted
baseline bytes cannot be recovered or independently reproduced under the
accepted baseline environment, say so explicitly and propose a decision-ready
way to obtain a comparable baseline. A digest alone cannot produce a byte diff.

## 4. Verification

Run repository-local checks only:

1. focused new failing-before and passing orchestration tests;
2. `tests/test_rp11_launch_source.py`;
3. the complete `tests/phase_5_0_evidence` suite;
4. `tests/test_rp11_launch_toolchain.py` only if an already available local
   accepted root is named; otherwise report every skip as unverified;
5. Python compilation for changed Python files;
6. `git diff --check`; and
7. generated-artifact checks only if a serialized contract actually changes.

Do not provision or download a new root for this repository-only stage. Do not
cite carried-over figures as fresh results.

## 5. Authority and restrictions

Gemini may edit only:

* `infra/rp11-launch/buildroot/enter.py`;
* focused launcher support/tests required for the gate;
* the R-5 handback corrections in §3.3;
* a narrowly necessary `cc1.v` comparison helper/test under existing launcher
  test/tool directories; and
* one remediation handback named in §6.

No SSH, rsync, `oracle-test` access, `sudo`, package operation, download,
provisioning, build-root creation, host inspection, service or database action,
launcher build/installation, H-1/H-2, PO-14, RP-11 wiring, controlled write,
reboot, evidence band, harness `--execute`, operational path, protected-
artifact access, secrets scan, commit or push is authorized.

Do not change launcher source, `toolchain.lock`, `build-root.manifest`,
`expected.sha256`, the committed listing, manifest version/digest, XD, T-L10,
T-L11, operational authorization drafts or platform behavior. If the required
gate cannot be implemented without one of those changes, stop and report the
conflict.

## 6. Required handback and stop gate

Write
`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md`
with:

* requirements implemented and files changed;
* before/after SHA-256 for every changed file;
* the exact gate call path and ordering proof;
* failing-before evidence and complete test results;
* the corrected status of the earlier R-5 handback;
* the `cc1.v` comparison capability, available baseline bytes, and unresolved
  evidence needs;
* checks not run and why;
* security, configuration, deployment and rollback implications; and
* proposed reviewer focus.

Stop after the repository handback. Do not rerun R-5. Codex independently
reviews this remediation; Peter alone accepts it and may then authorize a new
fresh-root R-5 run.
