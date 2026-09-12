# Independent technical re-review — runner contract r3

Date: 2026-09-11. Reviewer: Codex. Disposition: **changes requested**.

Scope: the active R2 remediation handback, runner contract r3, reservation
validation, lifecycle storage model and its synthetic tests. This is the current
Package 5.0 checkpoint, not a fresh audit of every product component. No code,
tests, generated artifacts or operational configuration were changed.

## PR-20260911-R3-1 — Blocking: failed initialization leaves an admissible-looking record

Locations: [contract r3 §5.7–5.8](phase-5-0-reserved-laboratory-runner-contract-r3.md),
`tools/phase_5_0_evidence/lifecycle_storage.py:445`, and
`tests/phase_5_0_evidence/test_r2_proposal_models.py:984,1040`.

Initialization renames the first-use record before synchronizing its directory.
If that barrier fails, the function returns NOT_DURABLE but the final record is
already readable. A process restart without a machine crash retains this visible
record. Retrying returns ALREADY_INITIALIZED, whose recovery says to read it.
The participant protocol admits a readable, coherent first-use record and has no
specified way to establish that the failed publication was subsequently made
durable. The initializer's in-memory outcome is unavailable to that reader.

Independent synthetic reproduction, using the existing Store fixture and
`_initialize(store, fail_at="record-entry")`, returned:

```text
failed initialization: False not_durable
visible record: True
durable record: False
retry: already_initialized
```

This violates the proposal's requirement that initialization not admit anyone
until both barriers succeed. The interruption test immediately calls the model's
power-loss `crash()`, hiding the process-only restart case. The claimed
end-to-end successful test constructs `environment_reset_history(HOST)` instead
of reading the initialized bytes; it cannot detect this storage/admission gap.
This is a design/model defect, not a demonstrated operational bypass in an
implemented adapter.

Required correction: specify publication, reader coordination and restart
recovery as one protocol. A successor must either establish the required
durability under the lock or refuse pending an attributable operator recovery;
file existence alone cannot discharge this obligation. Model a reader of the
actual stored record, failed directory sync followed by process-only restart,
retry, concurrent participant arrival, and the successful durable control.
Do not replace these with a newly constructed successful history.

The distinction between file data and containing-entry durability is documented
by [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html). The admission
consequence above is an inference from the proposed reader and publication rules.

## PR-20260911-R3-2 — Blocking: ordinary participant crashes bypass lifecycle protection

Location: [contract r3 §5.2 and §5.5](phase-5-0-reserved-laboratory-runner-contract-r3.md),
especially the paragraph beginning “Conversely a test suite that crashes”.

Participants 1–6 never publish lifecycle state. The contract explicitly permits
the next suite to proceed after one crashes because its lock has disappeared.
These participants include database suites, synchronization, dependency updates
and environment reset. For example, a synchronization wrapper can die after
updating only part of the tree, or a database test can die while a server-side
operation remains unsettled. The previous RELEASED or FIRST_USE record remains
unchanged. The next ordinary participant takes the free lock, validates that
stale record and proceeds; its protocol requires neither termination evidence
nor a consistency check for the interrupted operation.

Calling the interrupted operation a test rather than a reservation does not
establish that its effects ended. This reintroduces the predecessor gap the
durable record was introduced to close, now across the six other entry points.
The current survey tests only common input validation, not participant lifecycle
execution. Kernel lock release is associated with closing the open file
descriptions, not completion of external effects:
[flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html).

Required correction: provide durable in-progress/completion accounting for every
participant that can leave relevant effects, with recovery suited to that
operation. Alternatively prove an explicit containment and completion contract
for each exempt participant; “not a reservation” is insufficient. Keep permission
changes proposed for review. Inject wrapper death with a surviving effect and
partial synchronization, require every successor to refuse, and include clean
completion and verified recovery controls. No real crash drill is requested here.

## PR-20260911-R3-3 — Important: first-use and recovery histories lose target binding

Locations: `tools/phase_5_0_evidence/reservation.py:391,938`,
`tools/phase_5_0_evidence/lifecycle_storage.py:457`, and contract r3 §5.8.

The initializer writes a target identity, but LifecycleHistory has no target
field. Validation compares target identity only for RELEASED through its
ReleaseRecord; FIRST_USE and OPERATOR_RECOVERED cannot carry the corresponding
binding. A history for the same hostname therefore admits against a different
target identity. The first-use evidence's author and basis likewise never travel
through the demonstrated storage-to-decision path.

Independent synthetic check: the same
`environment_reset_history("synthetic-host")`, supplied to `survey()` with
`target_identity="target-A"` and then `"target-B"`, admitted all seven
participants both times. This is not evidence of a live-host bypass; it shows
the proposed binding requirement is absent from the model's admission boundary.

Required correction: preserve and validate host/target binding for every admitting
disposition, and parse the stored evidence into the shared validator. Require
wrong-target, absent-target and missing-attestation refusals, alongside a matching
record control. The BINDING_MISMATCH enum currently has no enforcing branch in
initialization; either implement the bounded model obligation or label it as
unmodelled. Correct the end-to-end evidence claims accordingly.

## Disposition of the previous findings

| Finding | Technical recommendation |
|---|---|
| R2-1, contradictory lifecycle state | Recommend closure of this specific decision-code defect: the shared shape validator rejects incompatible states and malformed enum values, with regressions. This does not establish complete storage validation. |
| R2-2, O_PATH fsync and missing recovery-parent barrier | The named design corrections are satisfactory: usable O_RDONLY directory references and the recovery-parent barrier are specified. No implementation or target durability proof exists; R3-1 is a separate publication/restart gap. |
| R2-3, post-unlink detection claim | Recommend closure of the specific claim defect. The corrected text and counterexample distinguish name absence from removed-object identity. Quiescence and administrator trust remain prerequisites. |
| R2-4, shared allowlist and first use | ADMITTED refusal and the common allowlist are corrected. First-use storage remains incomplete under R3-1 and R3-3; do not close the whole finding. |

EH-R16-1 remains Open; its privileged remedy is not implemented. LAB-1 remains
Important and unrepaired. The C1 → C2 → C5 correction and withdrawal of the
JNL-47 criterion split are preserved. Technical recommendations close no package
gate and accept no provisioning or residual risk on Peter's behalf.

## Independent verification and limits

Commands run from `/opt/freedom-blades/platform`:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python --version
  Python 3.12.3
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
  217 passed in 1.15s
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
  1657 passed in 8.94s; zero skips
git diff --check
  passed
```

Additional pure synthetic checks used `runpy.run_path` on
`test_r2_proposal_models.py`, its Store and initialization helper, and survey
over the two synthetic target identities described above. No armed boundary,
filesystem durability experiment or database effect was used. Linux open(2),
fsync(2) and flock(2) primary documentation was consulted.

The local interpreter is the restricted-pass exception. The canonical interpreter
remains `/opt/freedom-blades/runtime/venv-web/bin/python` on oracle-test.
TEST_DATABASE_URL was unset. Bot and web suites must run serially because they
share a database; neither was rerun for this bounded review. No previous counts
are adopted as new evidence. Database suites, Foundry tests, host inspection,
SSH, synchronization, provisioning, privileged drills and target preflight were
not run. No formatter, linter or type-checker result is claimed.

No manifest-covered source changed. The 36 hashes and generated artifacts were
not independently reverified in this review. The supplied digest
`55af840fbb28f0ea8ae447e732644c5b2f81dace83f6ccd499f24ebc8864cff2`
remains review input only, never execution approval.

Next action: bounded local lifecycle design/model remediation, then Codex
technical re-review before privileged implementation or maintainer permission
decisions. Package 5.0 remains not ready, P5.0-R5 Blocking, OD-62 Open; the three
C-7 cases and twelve target facts remain unresolved/unconfirmed. No host action,
migration, deployment, cutover or Package 5.1+ work is authorized by this review.
