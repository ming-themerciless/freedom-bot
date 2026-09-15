# Maintainer direction and LAB-1 local remediation — 2026-09-12

## Decisions

Peter made the three pending choices for runner contract r6:

1. **Identity:** use the existing shared `ubuntu` identity for all seven
   participants; do not create separate identities. This resolves the desired
   identity choice in V10, not its target observation. Whether each of the seven
   entry points actually runs as `ubuntu` is still unconfirmed.
2. **r6 §7:** accept the exact ten-item permission/provisioning delta as the
   proposed design for this disposable lab. This records the design choice; it
   does not apply, provision or authorize any of the ten changes.
3. **LAB-1:** retain the Important classification and accept the bounded fix
   proposed in r6 §8. The straightforward repair is to report residue recovery
   independently from configuration recovery, retain both procedures when
   both failure conditions exist, and serialize the residue procedure in the
   run record.

The rationale for the shared identity and lab design is that the server is
disposable and isolated from the other server and Peter's home system. Separate
accounts would provide clearer per-participant attribution and reduce accidental
cross-participant changes, but they add setup and do not materially improve the
stated cross-server containment boundary. With the shared identity, participant
file permissions are accident guards, not barriers between the seven
participants; the lab continues to assume trusted operators. This is an explicit
tradeoff, not a claim that shared UIDs provide isolation.

## Local implementation

The LAB-1 correction is implemented in the workspace:

- `CleanupOutcome` carries `residue_recovery_procedure` separately from the
  existing configuration-capture `recovery_procedure`.
- `classify_cleanup()` attaches the residue procedure only when residue remains;
  configuration recovery remains conditional on retained captures.
- The feasibility experiment and classifier use the procedures carried by the
  actual outcome.
- The run-record schema is version 2 and encodes residue recovery steps
  separately.
- Existing configuration recovery still truthfully names the captures under
  `R/before` and its step 2 now instructs the operator not to rely on them if
  the disposable root or their integrity is in question. That is an instruction
  in the procedure text, **not a mechanical refusal**, and a test now pins the
  clause so it cannot be dropped or re-worded into a claim of enforcement. The
  separate durable external recovery-store idea in r6 §8.2 is **not implemented
  or provisioned** and is not described as available.

## Independent review of that implementation, and what it changed

Claude reviewed the implementation above rather than accepting it, and three
findings were repaired in the same workspace. The first two were demonstrated by
reversing each repair in a scratch copy and observing which tests failed.

**1. The accepted clause was not the clause implemented.** r6 §8.1 requires the
evidence clause to be satisfied when the run names *the procedure that applies to
the state it reached*. The submitted repair passed a single boolean over both
procedures to `journal.classify_cleanup_failure_state`, so an S-B run that left
residue and named only the **configuration** recovery satisfied *"the named
operator recovery is reported"*. That is the reporting gap LAB-1 named, moved
from the outcome into the record that judges it. The classifier now takes the two
causes and the two procedures separately and requires every **present** cause to
name its own procedure; an absent cause requires nothing and never excuses a
present one. The failed record now says which procedure was missing.

**2. The negative control constrained nothing.** The submitted control called the
classifier directly with `recovery_procedure_named=False`, bypassing the
derivation under repair. With that derivation hardcoded to `True` the complete
harness stayed green, as did gutting the run-record encoder to emit an empty
residue procedure. Three controls replace it: one substitutes an outcome naming
neither procedure and requires a failed record, one names only the configuration
procedure with residue present, and one retains a capture without naming the
configuration procedure. Two run-record tests now encode the populated five-step
procedure, read it back off disk and require the validator to accept it and to
refuse it reordered — the state the schema went to version 2 for, which no test
previously exercised.

**3. The review-input artifacts were stale.** All three edited modules are in
`COVERED_SOURCES`, so the review-input digest changed and neither derived
artifact was regenerated. Both have been regenerated through the non-executing
CLI, twice, byte-identical.

**4. The operator never read the procedure.** §2.13.2b asks an S-B run to
*report* the named recovery, and the reader of that report is an operator looking
at a non-zero exit rather than at `CleanupOutcome`'s fields. The S-B message said
only that the host *"requires operator recovery"*. It now names the procedure
each present cause calls for — the residue procedure step by step, the
configuration procedure beside it when a capture was retained, and a sentence
saying neither answers for the other. A clean run names none, which is the
control. Two smaller points from the same review are also closed: `RecoveryStep`
is imported from `journal`, which defines it, rather than through `cleanup`; and
the orphaned `feasibility.LAB_1` constant was removed.

**Contract changes this entails, and they need review.** The supplied-observation
schema is **version 3**: `JNL-47-RECOVERY-STATE` replaces
`recovery_procedure_named` with `residue_recovery_named`,
`configuration_capture_retained` and `configuration_recovery_named`. A version-2
payload is refused rather than reinterpreted. The review manifest is
**version 10** for the same reason. The now-orphaned `feasibility.LAB_1`
constant, which no disposition referenced after the repair, was removed.

## Verification

Run locally with `TEST_DATABASE_URL` unset. The documented interpreter
`/opt/freedom-blades/runtime/venv-web/bin/python` has no `pytest`, so these
non-operational suites were run with the available local interpreters
(Python 3.12.3, pytest 8.4.2; node v24.20.0). **This is not the required
disposable-host test environment and no host or integration evidence is
claimed.**

| Suite | Result |
|---|---|
| Focused: feasibility, plan/cleanup, r13 remediation | 195 passed |
| Complete `tests/phase_5_0_evidence` | 1,871 passed, zero skips |
| Bot `tests/test_*.py` | 3,018 passed, 326 skipped |
| Web `tests/web` | 1,609 passed, 1 failed, 1,362 skipped |
| Foundry `foundry-module/tests` | 171 passed |

**Every skip is unverified.** With `TEST_DATABASE_URL` unset the web suite's
correct skip count is 80, not 1,362, so the web figure is evidence about a
configuration that skipped its database-marked tests.

The one web failure,
`test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`,
is **unrelated to this change and predates it**: it was reproduced on a clean
detached worktree at commit `7b8c483` with no untracked files present. The test
asserts that the working tree contains an untracked directory and fails when it
does not, so its result depends on incidental working-tree state rather than on
the behavior it names. It is reported here, not fixed here.

No formatter, linter or type checker is configured or installed — **unavailable,
not a pass**. `git diff --check` passed and a scoped `compileall` succeeded.

**New review-input digest, review input only — do not pass it to `--execute`:**
`af3181ed276f61a89a51b25afcbfb91f7a4c938b21a5bf83c1ff53f8b3764821`. It replaces
`2fa1d13b7b112f7fda837abcdd70f86ff6d85701602818d810af5fc2141ce5ca`, which
described the pre-repair tree and is now evidence about a state that no longer
exists.

| Regenerated artifact | SHA-256 |
|---|---|
| `phase-5-0-evidence-harness-review-manifest.json` | `bc0f8d0b39d50ce0d1887fa455ccd0c5bafaaf619c7a41196f4b78061d62d6c8` |
| `phase-5-0-evidence-harness-concrete-plan.md` | `922d7db9345a1989eee925b504e8c9904e8ca45301b07470523cf3e0f9c467fa` |

Independent technical review is still required. The implementer does not close
their own Important finding. Codex implemented the first LAB-1 pass, which
inverted the normal division of work; this record restores it. Claude reviewed
and remediated that pass, and **Codex re-reviews** — no session closes a finding
on work it produced, and the review below was not independent of the corrections
it describes.

## Authority and remaining gates

The current handover remains local-only. This decision record authorizes no SSH,
synchronization, host inspection, preflight, permission change, provisioning,
database operation or real execution. In particular:

- V10's identity **choice** is resolved; V10's actual-identity **preflight fact**
  is unconfirmed.
- V6 and V8 remain unperformed.
- No item in the ten-item delta has been provisioned.
- C-7 remains unresolved, EH-R16-1 remains Open, `is_executable` remains False,
  Package 5.0 remains not ready, package-level P5.0-R5 remains Blocking, and
  OD-62 remains Open.

Next: independent technical review of the LAB-1 local repair, including the
supplied-observation and manifest version changes it entails. Any later target
preflight, provisioning or operational action needs an updated handover that
explicitly permits it and must satisfy its own review and execution gates.

---

## Dated correction, 2026-09-12 — the run-record schema is version 3

The statements above are preserved as the record of that pass. Two of them are
corrected here rather than rewritten, because the Codex re-review that followed
found what they described was not what the run record enforced.

**"The run-record schema is version 2 and encodes residue recovery steps
separately"** was accurate about *encoding* and not about *reading*. The
[re-review](project-review-2026-09-12-lab1-rereview.md) recorded
**PR-20260912-LAB1-1**: `validate_run_record()` checked each residue-recovery
entry for three keys, a consecutive order and non-empty strings, and never
compared the value with `journal.RECOVERY_PROCEDURE`, with the procedure
serialized from the outcome, or with the residue that requires it. A schema-2
S-B record carrying one arbitrary ordered instruction was accepted.

**"Two run-record tests now encode the populated five-step procedure, read it
back off disk and require the validator to accept it and to refuse it
reordered"** is likewise accurate as written and was not enough: reordering is a
useful negative case and does not cover substitution.

The correction is
[the LAB-1 run-record binding remediation](project-review-remediation-2026-09-12-lab1-handback.md).
The **run-record schema is now version 3**: residue present requires the exact
canonical five-step procedure and residue absent requires none, retained recovery
inputs require the exact `cleanup.RECOVERY_PROCEDURE` and no retained inputs
require none, the two causes are independent, and the document read back is
compared whole with the document that was written. A version-2 record is refused
by name rather than reinterpreted.

The **supplied-observation schema remains version 3** and the **review manifest
remains version 10**: the manifest does not declare the run-record document
contract, so only `artifact.py`'s pinned hash moved. The review-input digest is
now `3b50e8f7adb309549aa1e69a61e9ddce1ce5bf11429eecc002f427b773df98a3`,
replacing `af3181ed276f61a89a51b25afcbfb91f7a4c938b21a5bf83c1ff53f8b3764821`. It
is review input only and must not be passed to `--execute`.

Nothing else in this note changes. LAB-1 remains Important and **not closed**;
the authority and remaining-gates section above stands unamended.
