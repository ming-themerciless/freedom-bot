# Independent technical re-review — September 11 remediation

Date: 2026-09-11. Reviewer: Codex. Disposition: **changes requested**.

Scope: the active handback, runner contract r2, reservation decision API and
synthetic C0/C1/C2/C5 ordering model. This is a bounded Phase 5.0 review, not a
fresh audit of every accepted product package. Existing changes are preserved;
no mechanism, test, generated artifact or operational configuration was edited.

## PR-20260911-R2-1 — Blocking: contradictory predecessor state still admits

Location: `tools/phase_5_0_evidence/reservation.py:641`.

The RELEASED disposition validates the release record's reservation, host and
target, but never checks `history.predecessor_state`. A complete, readable
history with `predecessor_state=RUNNING` or `QUARANTINED`, disposition RELEASED,
and a matching release record returns `admitted=True`. A contradictory record
must not be resolved in favor of reuse. This matters when a lifecycle reader
combines stale release metadata with a later state or encounters inconsistent
stored data. The first-use branch already rejects analogous contradictions.

An independent pure-function reproduction used a synthetic host and target,
an empty complete inventory and `LockView()`. For the same matching ReleaseRecord,
varying only predecessor_state produced:

```text
running -> True ()
quarantined -> True ()
released -> True ()
```

Required correction: validate the consistency of disposition, predecessor state,
identity and attached evidence before selecting an admitting branch. Reject
contradictory histories and retain the valid released control. Cover RUNNING,
ADMITTED, RECOVERING, QUARANTINED and missing state paired with RELEASED, and
audit the first-use/operator-recovered branches for incompatible evidence.
This is a defect in the decision API, not a demonstrated operational bypass:
the adapter remains unbuilt and real execution remains gated.

## PR-20260911-R2-2 — Blocking: the durability sequence uses invalid descriptors

Locations: runner contract r2 §1.3, P2 at line 188, M1 at line 224, and
§2.4 at line 423.

The directory chain is opened with `O_PATH`, including `bin_fd`; M1 explicitly
defines `pgconf_fd` as O_PATH. P2 subsequently requires `fsync(bin_fd)` and
restore requires `fsync(pgconf_fd)`. These are not usable fsync descriptors.
The proposed normal installation fails at its directory durability barrier;
restoration reaches the same failure after replacing a destination.
The limited operations permitted on O_PATH descriptors are documented in
[open(2)](https://man7.org/linux/man-pages/man2/open.2.html).

There is also an omitted durability edge in §2.3: a newly created recovery
`<run-id>` directory must itself be durably linked in the recovery parent before
M1. Syncing captures and the run directory does not establish persistence of
that parent entry. After power loss, restart discovery by listing the recovery
parent is therefore not guaranteed to find the advertised recovery basis.
[fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html) explains the
separate containing-directory synchronization requirement. The crash consequence
is an inference from that requirement and the specified sequence, not a target
experiment performed in this review.

Required correction: specify usable directory descriptors and their custody,
including how an O_RDONLY directory descriptor is bound to the intended object
if separate from the O_PATH reference. Enumerate every publication barrier,
including the recovery parent after run-directory creation. No configuration
mutation may begin before all recovery barriers succeed. Add a successful
sequence model and failures at each barrier; eventual implementation evidence
must exercise the actual descriptor modes and restart discoverability.

## PR-20260911-R2-3 — Important: the post-unlink check overclaims detection

Location: runner contract r2 §1.4.5 steps 2–3 and §9 row 3.

After the pre-check succeeds for original A, a writer can rename A away, place B
at its name, and let `unlinkat` remove B. The proposed post-check then sees
ENOENT, exactly as it would after correctly removing A. It neither detects that
B was deleted nor learns B's identity, contrary to the matrix's promise to
detect the event and report both identities. The final-name semantics are in
[unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html); this
counterexample is a design inference.

The trusted-administrator premise and genuinely established experimental
quiescence can exclude this event from an admitted run. They do not make the
post-check detect it when injected. Required correction: distinguish an absence
check from object-identity evidence, and make row 3 reflect the actual result.
Keep quiescence as the prevention prerequisite, refuse when unobserved, and
include the A-renamed/B-deleted/ENOENT counterexample in the proposed model.
Do not claim that the repair requires excluding trusted administrators by DAC.

## PR-20260911-R2-4 — Important: the storage protocol omits first use and ADMITTED

Location: runner contract r2 §5.6–§5.7, especially lines 641–643 and 656–659.

The normal path refuses RUNNING, RECOVERING and QUARANTINED, then lets an
ordinary participant run. It omits ADMITTED, despite the decision API explicitly
classifying that state as an active predecessor. A crash after ADMITTED is
persisted but before RUNNING leaves a free lock and exactly that omitted state.
No release has been verified, so proceeding contradicts the lifecycle contract.

Conversely, the record being absent always refuses, but §7's provisioning list
creates only its directory and never initializes a verified-first-use record.
The documented fresh-install path therefore cannot reach its successful control.

Required correction: admit through an explicit allowlist of validated lifecycle
outcomes shared by all seven participants, including refusal of ADMITTED and
unknown/malformed states. Specify initial record creation, identity binding,
durability and authorization as part of provisioning. Test fresh provisioned
first use, absent record, and a crash between ADMITTED and RUNNING. These are
design corrections; they authorize no provisioning.

## Disposition of the submitted remediation

The C1-cleanup → C2 → publication ordering correction is technically recommended
for the bounded feasibility model. Inspection of `run_sequence()` confirms
cleanup failure returns before publication, while the intentionally unordered
control publishes first. Withdrawal of the proposed JNL-47 criterion split is
correct. This establishes no product producer or operational coverage.

The explicit residue observation and evidence-required transition changes address
the specific omitted-evidence cases of PR-20260911-4 at the pure-model level.
The predecessor-history repair of PR-20260911-3 remains incomplete under R2-1.
The independent recovery store and persistent lock are useful design corrections,
but PR-20260911-1/-2/-6 cannot receive an overall implementation recommendation
until the findings above are answered. EH-R16-1 stays open. LAB-1 remains
Important and unimplemented; keeping separate residue and configuration recovery
procedures is a reasonable direction, subject to the corrected recovery design.

Preferred next action: one bounded local correction of the decision validation
and runner design, with named synthetic regressions, followed by Codex re-review.
The designated implementer owns remediation; Peter retains permission and gate
authority. No new architecture selection or criterion waiver is needed for
these corrections. The proposed provisioning delta remains unapproved.

## Independent verification and limits

Commands run from `/opt/freedom-blades/platform`:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python --version
  Python 3.12.3
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
  205 passed in 1.08s
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
  1546 passed in 8.79s; no skips
git diff --check
  passed
```

The additional reproduction above imported only the pure reservation model and
used synthetic values; no host or database effects were invoked. Primary Linux
manuals were read online for descriptor, unlink and durability semantics.

The local interpreter is the restricted-pass exception, not the canonical
`/opt/freedom-blades/runtime/venv-web/bin/python` on oracle-test.
TEST_DATABASE_URL was unset. Bot/web suites share a database and must run
serially when authorized; neither was rerun for this scoped review. No earlier
suite figures are adopted as new evidence. Database tests, remote suites,
Foundry tests, host checks, privileged syscall experiments and target preflight
were not run. No formatter, linter or type-checker result is claimed.
No covered implementation source or generated artifact was changed, and manifest
hashes were not independently reverified in this pass.

Package 5.0 remains not ready, P5.0-R5 Blocking, OD-62 Open. Three C-7 cases and
twelve target facts remain unresolved/unconfirmed; no execution digest is
approved. This review closes no package gate and authorizes no implementation
of the privileged mechanism, provisioning, host action, migration or deployment.
