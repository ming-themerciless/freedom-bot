# R16 independent review — C-6/C-7/C-8, 2026-09-09

Disposition: **changes requested; execution approval withheld**.

Reviewed Claude's C-6/C-7/C-8 handback and the current harness tree. This is
the bounded independent implementation and C-8 technical design review, not a
full-platform audit. No implementation code was changed.

Review-input digest, **not execution approval**:
`765b299bf680b06bce4edd34ed236dea13dff466c39e6d457d7da190b5772acd`.

## Findings

### EH-R16-1 — Blocking: root identity is checked after dependent cleanup

Location: `tools/phase_5_0_evidence/cleanup.py:910` and
`tools/phase_5_0_evidence/execution/executor.py:1315`.

The only ownership revalidation precedes the final root `rmdir`. All earlier
cleanup operations retain ownership inferred from the original root creation.
If the root is renamed and another directory occupies its path before cleanup,
the executor first restores PostgreSQL configuration from that replacement's
`before/` files and clears flags/removes paths within the replacement. Only
afterward does it notice that the root inode differs. Preventing the final
`rmdir` does not protect the replacement's contents or the configuration files.

Independent injected-boundary reproduction: provide satisfying observations
through the run, then return device/inode `999/999` from cleanup revalidation.
The executor issues **30 cleanup commands referencing the root before that
check**, starting with both configuration restores, and skips only the root
removal on the mismatch. No real host operation was performed.

Required correction: validate the ownership of the hierarchy before consuming
recovery inputs or mutating descendants, and make those operations depend on
that validation. Account explicitly for replacement during creation, execution
and cleanup, including descendant replacement and remaining race windows. Test
a replacement containing sentinel files and substitute recovery inputs; no
unowned content may be removed or installed as configuration. Preserve residue
and recovery reporting when ownership cannot be established. The current C-8
design is not accepted.

### EH-R16-2 — Blocking: observed provenance refusal is replaced by an inference

Location: `tools/phase_5_0_evidence/observations.py:843`;
`tools/phase_5_0_evidence/provenance.py:136`.

The importer validates `fields.refusal_code` but does not pass it to the
classifier. `classify_missing_provenance` constructs an observed `refused J-26`
solely from APR/PVR absence. Absence is the experimental input; it does not
establish the program's actual refusal.

Independent reproduction: take the complete synthetic payload and change only
the provenance record's refusal code from `J-26` to `DEP-04`. Import succeeds
and emits `JNL-51-g-refusal` with status **passed** and observed value
**refused J-26**. The artifact therefore contradicts its supplied evidence.

Required correction: carry the observed result into classification and compare
it with the fixed expected `J-26`. Preserve mismatches as failed evidence rather
than synthesizing the expected response. Add a regression for a different valid
refusal code and represent unexpected admission/no refusal explicitly.

### EH-R16-3 — Important: complete coverage omits the capability cases

Location: `tools/phase_5_0_evidence/observations.py:711` and `:367`.

The coverage loop skips every required case absent from `BAND_7_SCHEMA`.
Consequently, the three required JNL-49/JNL-50 capability cases never enter
`missing`. Eight Band-7 input records yield `complete=True`, `missing=()`,
without a run record or any capability observation. This was independently
reproduced. The presence of producing steps in a plan does not prove those
steps ran or that their controls succeeded.

Required correction: distinguish Band-7 import completeness from complete
required-case evidence. A complete harness result must join validated execution
observations and external observations under the same target/run/manifest,
including the capability controls. Until that join exists, report only partial
coverage and do not expose overall completeness or eligibility based on Band 7
alone. Test absent, failed and mismatched execution evidence.

### EH-R16-4 — Important: missing producers are reclassified as resolved

Location: `tools/phase_5_0_evidence/concrete_plan.py:3945` and
`tools/phase_5_0_evidence/observations.py:211`.

Band 7 now declares external producers by descriptions of future coordinator
tooling, removing all unresolved entries. The handback expressly says their
existence is not established. There is no concrete reviewed producer artifact
or runnable collection procedure in this submission for these cases. Naming
`init-generation` and a future table does not resolve the evidence dependency
that blocked pre-implementation readiness.

The approved implementation prompt specifically requires a still-missing
experiment producer to remain unresolved. An external-input route is useful,
but cannot discharge that requirement by changing the coverage category.

Required correction: retain the missing-producer dependency as unresolved until
an actual bounded producer and its collection procedure are available and
reviewed. Do not implement gated Package 5.0 product tooling merely to satisfy
this finding. If a separate evidence-only producer is needed, identify its
scope and applicable authorization before implementation.

## Accepted progress and verification

C-6 now contains the three requested operation steps, separate immutable-flag
observations, initial-state controls, E4/E6 comparison and E5 clear/open ordering,
plus reset and cleanup declarations. No additional Blocking or Important C-6
implementation finding was identified in this pass. This is not a claim that
the kernel experiments passed; none was executed.

The separate importer has no executing boundary in its import graph. Exclusive
root creation improves the pre-existing-object refusal, but does not resolve
EH-R16-1. C-7 and C-8 remain unaccepted as complete remedies.

Independent verification, serially, with `TEST_DATABASE_URL` explicitly unset:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence/test_no_execution.py
193 passed
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence
1335 passed
git diff --check
passed
```

The interpreter is an explicitly reported **local fallback**. The repository
is `/opt/freedom-blades/platform`; the canonical test interpreter is on
`oracle-test` at `/opt/freedom-blades/runtime/venv-web/bin/python`. No PostgreSQL
assertion ran: `TEST_DATABASE_URL` was unset, and these were synthetic harness
tests. Full bot/web/Foundry suites were not rerun for this bounded review, and
Claude's totals are not claimed as independent verification. Formatter, linter
and type checker are not configured.

Independent in-memory regeneration matched both submitted manifest bytes and
the rendered concrete plan exactly. Additional reproductions used the suite's
synthetic target facts, fake boundary and fake materializer only. They never
armed a real boundary, invoked a generated vector or modified a target.

## Gate and next step

Return the findings for bounded remediation and independent re-review. The
requested prior C-8 design checkpoint was not performed before implementation;
reviewing the combined submission now does not retroactively satisfy it.

The maintainer's read-only preflight authorization remains recorded and need
not be requested again. It was not exercised in this review; the implementation
has blocking findings and no executable manifest is approved. No SSH, target
synchronization, host inspection/mutation, database operation or destructive
drill was performed. The twelve target facts remain unconfirmed.

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, and OD-62 **Open**.
Migration 0014, product implementation, deployment, cutover and Package 5.1+
remain unauthorized.
