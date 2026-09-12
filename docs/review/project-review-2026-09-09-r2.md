# Independent review — project remediation, 2026-09-09, second pass

Reviewer: Codex. Disposition: **changes requested for the C-8 design; recommend
closure of Finding 3's working-tree sanitation. Execution approval withheld.**

Scope: the current project-review handback, revised C-8 design, new synthetic
reproductions, sanitized crafting fixture/report, and their integration with the
current harness. This is not an exhaustive platform audit or a package gate.
The required repository agreement, roadmap and disposable-server instructions
were read earlier in this conversation and remain applicable.

## Prior findings

- **EH-R16-1 remains open**, with its existing identity. The mechanism is
  deliberately unimplemented pending design acceptance. The new reproduction
  suite confirms the late cleanup check; passing it does not demonstrate a fix.
- **Finding 2 remains open.** The revised design correctly withdraws the claim
  that `mkdirat` followed by `openat` detects child replacement and supplies the
  previously missing permission inventory. It is not technically accepted for
  the reasons below.
- **Finding 3: recommend closure for the current working tree.** The fixture is
  independently synthetic and still checks alias resolution and the unrelated
  tool fallback. The report no longer identifies the character or transcribes
  the original cells. A scoped search of docs, tests and models found no remaining
  original identifier or copied row combination. Production alias code is
  preserved. This disposition makes no claim about remote copies or Git history.

## PR-20260909-R2-1 — Blocking: proposed guards omit execution-time effects

Location: `phase-5-0-evidence-harness-c8-ownership-design-r16-2.md:337–354`
and its P7 implementation table.

P2 defines and generates guards exclusively for cleanup steps. Its implementation
table adds no root identity comparison before ordinary command steps during
execution. The lifecycle trace itself lists provisioning, flag changes, capture
and experiments that resolve paths under the root after initial identity
acquisition. The existing executor's `_revalidate()` checks the vector and its
capture policy; its mutation ownership check consults recorded baseline ownership,
not a fresh comparison with `created_identity`.

For example, replace the root after B3-01 and before the next `install -d`.
The subsequent provisioning commands act on the replacement. A later cleanup
guard can detect that replacement, but cannot undo those unauthorized effects.
This does not depend on a replacement racing an immediately preceding guard:
there is no proposed execution guard there at all.

Required revision: cover each execution-time read/mutation dependent on root or
descendant ownership, including recovery capture and installed-program use.
Specify exactly how each effect is gated and how uncertain ownership stops it.
Add an injected replacement immediately after creation and before provisioning,
plus a replacement before a later experiment; assert that dependent effects are
not issued. Retain independently safe recovery. Do not narrow the earlier
whole-lifecycle requirement to cleanup without an explicit scope decision.

## PR-20260909-R2-2 — Blocking: P3 does not bind installed bytes to verified bytes

Location: `phase-5-0-evidence-harness-c8-ownership-design-r16-2.md:360–391`.

P3 hashes the capture in one process and then runs `install` against its pathname
in another. Replace the capture after the digest passes but before `install`
opens it: the check succeeds and the substitute bytes are installed. Root identity
can remain unchanged throughout. This directly contradicts the `[proved]` label
and the unconditional claim that content comparison removes the restoration
effect from dependence on custody. R-C8-3 acknowledges the window; that honest
acknowledgment does not establish the stronger protection claimed above it.

The initial capture also lacks an exact contract tying the recorded live-file
digest to the bytes copied and requiring recoverability before configuration
mutation begins. A separate later read of the live pathname is not that contract.

Required revision: specify how the exact bytes validated are the bytes used for
restoration, with a trustworthy baseline established before modification. Assess
a bounded capture/verification/write operation using a verified byte buffer or
protected staged content, including destination safety, interruption and recovery.
An open source descriptor alone does not prevent in-place modification of that
source. These are design alternatives to evaluate, not authorization to add a
writer or widen a privileged interface.

If a remaining race is proposed for acceptance, state its precise consequence
and prerequisite honestly and remove the contradictory proof claim. Do not
recommend accepting arbitrary substituted configuration merely because the
current two-process interface reopens the path. Include tests for substitution
after a successful digest check and for capture/digest disagreement before the
first configuration mutation.

## PR-20260909-R2-3 — Important: residual recommendations rest on false equivalence

Location: `phase-5-0-evidence-harness-c8-ownership-design-r16-2.md:287–321`.

The design rejects descriptor-based alternatives partly on the claim that their
benefit is already obtained by comparing the root identity, and recommends
acceptance because no mechanism is available. These conclusions do not follow
from the lack of a descriptor-only unlink operation.

A held directory descriptor continues referring to that directory after rename;
a successful pathname identity check does not stabilize the next lookup. These
are different protections. Moreover, a root descriptor followed by
`journal/000001.seal` still resolves the `journal` component: the example does not
make every intermediate component immune to substitution. The documented
descriptor semantics support this distinction. See
[Linux open(2)](https://man7.org/linux/man-pages/man2/open.2.html) and
[Linux unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html).

Required revision: distinguish whole-root replacement, deeper directory
replacement, final-entry replacement and in-place content mutation. Compare
the actual protections and costs of descriptor chains and exclusion of concurrent
writers, including quiescence of experimental processes. A protected namespace
is a trust-boundary design requiring evidence; it is not the same as inventing
a missing syscall. Do not assert that all designs on Linux must retain the
current exposure. Conversely, do not claim that descriptors alone solve every
race or that an unrestricted root adversary can be excluded by DAC.

No residual or interface expansion is accepted in this review. The maintainer
should receive a technically accurate comparison before being asked to choose.

## Evidence limitations and minor corrections

The new descendant-replacement test runs an unchanged `FakeHost` and checks that
the configured paths are removed. It is structural evidence that no descendant
identity is consulted, not an injected substitution of an object. Keep that
distinction explicit; the implementation regression must actually model the
replacement and assert which object or bytes an effect would consume.

The handback asserts that the sanitized material is already committed. The review
document is untracked here; `git log --all -- <report>` and the corresponding
`git log --all -S` search for the former test name returned no matching commits.
That does not prove absence from every remote or unreachable object, but it does
not support the handback's positive assertion either. Correct it to the observed
scope or cite the actual commits. No history rewrite was performed or requested.

## Independent verification

All Python commands ran locally with `TEST_DATABASE_URL` explicitly unset under
the active task restriction. The fallback interpreters were
`/opt/discord-bots/venv-web/bin/python` for harness/web and
`/opt/discord-bots/venv/bin/python` for the bot. The canonical environment remains
`/opt/freedom-blades/runtime/venv-web` on `oracle-test`; it was not contacted.
Bot and web suites ran serially.

| Command selection | Result |
|---|---|
| `pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | 193 passed |
| `pytest -q -rs tests/phase_5_0_evidence` | 1388 passed |
| `pytest -q -rs tests/test_*.py` | 2990 passed, 326 skipped, one dependency deprecation warning |
| `pytest -q -rs tests/web` | 1610 passed, 1362 skipped |
| `node --test "foundry-module/tests/"*.test.mjs` | 171 passed, zero failed/skipped |
| non-executing CLI manifest/plan generation | artifacts match supplied files byte-for-byte |
| independent SHA-256 check of manifest sources | 32 sources, zero mismatches |
| `git diff --check` | passed |

Manifest digest remains
`ec1e3e70b5d24aca911df9e4dcd394361ebffdb04b9587434cb74386756f2839`,
**review input only**. The generated plan retains three unresolved C-7 cases,
twelve unconfirmed facts and `is_executable=False`.

Database skips are unverified assertions, not integration evidence. No SSH,
target preflight, operational execution, database operation, privileged vector,
service change or production mutation was performed. No formatter, linter or
type-checker result is claimed. No implementation source was changed by this
review; only this review artifact was added.

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**.
The next step is a corrected technical design, not execution or product work.
