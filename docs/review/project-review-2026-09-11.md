# Independent technical review — reserved laboratory handback

Date: 2026-09-11. Reviewer: Codex. Disposition: **changes requested**.

Scope: the active C-P5.0-LAB-1 submission, its CRP correction, local evidence
producers, reservation decision API and proposed runner contract. This is not a
fresh audit of every previously accepted platform package. Existing working-tree
changes were preserved. No implementation was changed, no gate was closed and
no operational action or permission expansion was approved.

## Findings

### PR-20260911-1 — Blocking: the descriptor proposal does not bind all dependent effects

Location: `phase-5-0-reserved-laboratory-runner-contract.md:292–306`.

The proposal checks `fstat()` on held descriptors against their original device
and inode. Rename or pathname replacement leaves that descriptor pointing to the
original object, so that comparison still passes. `unlinkat(dirfd, component)`
also resolves the final component at the time of deletion: replacing that entry
inside an unchanged held directory still makes it remove the replacement.
`RENAME_NOREPLACE` protects the destination from overwrite; it does not bind the
source entry to an earlier observed inode. See the documented flag contract in
[rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html).

The proposed four verbs do not specify how pathname-based `install -d`, payload
installation and `chattr` become effects on the retained objects. Furthermore,
DIRFD is explicitly local to one case-program invocation, whereas the chain is
said to survive the whole run. The existing boundary launches separate processes
(`execution/boundary.py:841`); no descriptor-transfer or persistent-owner contract
is specified. Thus the claimed coverage of P1/P2/P4/X1/L3 is not established.

Required revision: name the descriptor owner and lifetime across process
boundaries, map each dependent effect to its actual object-resolution operation,
and specify exclusion/quiescence for final-entry changes where needed. Include
replacement after a successful check and before the actual effect, with separate
original/replacement identities. Retaining a descriptor can support a remedy;
the proposed comparison is not itself that remedy. EH-R16-1 remains open.

Documented semantics: [open(2)](https://man7.org/linux/man-pages/man2/open.2.html)
states that changing the path does not change the held reference;
[unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html) defines
directory-relative name removal. The failure scenarios above are the reviewer's
inference from those semantics and the submitted operation contract.

### PR-20260911-2 — Blocking: independent recovery depends on an unspecified copy

Location: `phase-5-0-reserved-laboratory-runner-contract.md:227–233`.

When R is unsafe, the contract disallows recovery from `R/before`, then relies on
an operator's out-of-band copy. No creation, verification, durable custody or
pre-mutation prerequisite for that copy appears in the operation inventory.
The cited `cleanup.RECOVERY_PROCEDURE` actually instructs recovery from the
captures under the disposable root (`tools/phase_5_0_evidence/cleanup.py:1278`).
It is not an independent recovery procedure.

After configuration mutation and loss of R's custody, the specified run can
therefore have no trustworthy restoration input. A correct held-buffer restore
does not solve restart after that buffer is lost.

Required revision: specify the independently retained bytes, their creation and
verification before mutation, durable location/custody, restart lookup and
recovery order. Refuse configuration mutation if that basis cannot be
established. Submit any additional writer/permission changes explicitly. Do not
describe an unprovided operator copy as an existing safeguard.

### PR-20260911-3 — Blocking: admission cannot distinguish a released host from a crashed reservation

Location: `tools/phase_5_0_evidence/reservation.py:397–405`.

`admit()` accepts `LockView(held_by=None)` with a complete inventory and no supplied
quarantine. It receives no preceding reservation state or verified release
record. After an executor dies and its process lock disappears, the same inputs
can occur while a server transaction or unresolved configuration state remains.
An inventory that classifies PostgreSQL as a required service does not prove
that the previous run's transactions settled.

The supplied missing-reservation test checks an *unreadable lock*. It does not
check a readable, free lock with a missing or unreleased reservation record.
The pure-function reproduction below returns `admitted=True` without any
predecessor release evidence. This is a defect in the proposed decision boundary,
not a claim that the currently unintegrated module already bypasses the CLI.

Required revision: make durable lifecycle state an explicit admission input,
distinguish verified first use from missing/unreadable history, and refuse
unreleased or uncertain predecessors even when the process lock is free.
Exercise the crash-between-effects-and-quarantine-publication case. The lock
adapter alone cannot supply the missing release rule.

### PR-20260911-4 — Important: release treats an omitted residue check as a successful check

Location: `tools/phase_5_0_evidence/reservation.py:458–459`.

`ReleaseEvidence.residue` defaults to `()`. With the other observations true,
omitting residue inspection yields `RELEASED`, unlike the explicit unknown state
provided for child processes, transactions and restoration. A caller that never
looked for residue is indistinguishable from one that observed none.

Additionally, exported `advance(RUNNING, RELEASED)` returns `RELEASED` without
any evidence, despite the transition-table comment saying release is possible
only through `release()`. These are public decision APIs, not enforced lifecycle
guards. Neither is currently integrated into operational execution.

Required revision: distinguish unobserved residue from observed-empty residue,
and make guarded transitions available only through the corresponding validated
decision. Add negative tests for omitted residue and evidence-free transitions.

### PR-20260911-5 — Important: the criterion split rests on the wrong creation order

Locations: `phase-5-0-reserved-laboratory-handback.md:132–145` and
`tools/phase_5_0_evidence/feasibility.py:521–529`.

The handback says absence after cleanup failure requires a generation previously
created by a real coordinator. The package contract says the opposite:
Algorithm C1 performs the probe **and its cleanup**; S-B stops the algorithm
there. C2 validates successful cleanup, and C5 creates the first persistent
generation artifact (`phase-5-0-package-plan.md:2909–2915`). JNL-47 explicitly
requires no generation or row for both cleanup-failure variants (line 4159).

The supposedly correct synthetic arrangement instead publishes journal, seal,
current, close and a row before injecting cleanup failure. Direct invocation
returns all four artifacts and `registry_row_present=True`. Its explanation that
the generation was legitimately created models a prohibited ordering.

Required revision: model C1 cleanup before C5 publication, and use an observed
attempt to reach a synthetic publication sink as the negative control. Preserve
later real-coordinator acceptance tests. A readiness/implementation evidence split
may still be appropriate, but Peter should not decide it on the incorrect claim
that the requirement demands creation followed by deletion. I do not recommend
accepting the submitted split as written. All three C-7 cases remain unresolved.

### PR-20260911-6 — Important: the proposed unprivileged lock cannot be created by its participants

Location: `phase-5-0-reserved-laboratory-runner-contract.md:308–315`.

The adapter is described as unprivileged, but it creates and unlinks a file in
`/run/freedom-blades`, specified as root-owned mode 0755. Ordinary test/sync
participants cannot create an entry there. Precreating a mode-0644 lock does not
fix the proposal: `O_CREAT|O_EXCL` fails while that entry exists, and ordinary
participants still cannot write the owner record or unlink it. The stated
fallback is refusal, so the proposed normal successful admission path is absent.

Required revision: specify who provisions the lock, the access required by each
participant, and whether it is a persistent flock inode or an exclusive-create
record. Specify crash recovery without automatic takeover. Prefer a single
persistent, provisioned lock inode with a separately protected lifecycle record
if that fits the approved identities; submit the exact provisioning/permission
delta instead of calling it zero privilege. This is a proposed correction, not
approval to provision it.

[open(2)](https://man7.org/linux/man-pages/man2/open.2.html) documents exclusive
creation and its EEXIST result;
[flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html) documents locks on
open file descriptions. The feasibility assessment applies those semantics to
the contract's stated ownership and modes; no host permissions were inspected.

## Disposition of the rest of the submission

The CRP correction answers PR-20260910-R2-1: both reads and writes use the same
equivalent-entry set and total. The focused 83-test skills suite passes,
including alias order, threshold and read-purity cases. No additional CRP defect
was found in this review. This is a technical recommendation for the correction,
not deployment authorization or a package gate decision.

LAB-1 is confirmed as an **Important** reporting defect: residue-only S-B has no
named recovery in `CleanupOutcome`. The labelled reproduction passes because it
asserts that the evidence record fails; it is not a passed safety invariant.
The ownership reproductions are likewise evidence of known defects.

The new producers are isolated local models, not operational evidence. Their
unresolved coverage and operational-ineligibility labels are appropriately
retained. Reservation enforcement and the privileged remedy remain unimplemented.
Passing tests do not cure the design/API findings above.

## Independent verification

Canonical testing remains on `oracle-test` with
`/opt/freedom-blades/runtime/venv-web/bin/python`. The active assignment forbids
remote execution. For this local exception I verified both fallback interpreters
as Python 3.12.3. `TEST_DATABASE_URL` was explicitly unset in every Python test
command, and the full bot suite completed before the web suite began.

Commands and results:

| Command (all Python test commands prefixed `env -u TEST_DATABASE_URL`) | Result |
|---|---|
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | 205 passed |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | 1490 passed |
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_skills.py` | 83 passed, 1 warning |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | 103 passed |
| `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | 3016 passed, 326 skipped, 1 warning |
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | 1610 passed, 1362 skipped |
| `node --test 'foundry-module/tests/'*.test.mjs` | 171 passed, zero failed/skipped |
| `git diff --check` | passed |

An initial combined focused invocation mistakenly used the web interpreter for
`tests/test_skills.py`; collection failed because that interpreter lacks
`discord`. Splitting the invocations as shown above fixed the environment choice;
no code or dependency was changed to make it pass.

Pure-function probes independently reproduced admission without a predecessor
release, evidence-free `advance()` to RELEASED, release with omitted residue
inspection, and publication before cleanup failure in the synthetic model.
No probe performed host effects. Minimal reproduction of the release issue:

```python
from tools.phase_5_0_evidence.reservation import (
    ReservationRequest, ReservationState, ReleaseEvidence, release,
)
r = ReservationRequest('new-run', 'reviewer', 'synthetic-host',
    'synthetic-target', '2026-09-11T09:00:00Z',
    '2026-09-11T10:00:00Z', 'operator')
e = ReleaseEvidence(reservation_id=r.reservation_id,
    target_identity=r.target_identity, lock_held_by=r.reservation_id,
    child_processes_ended=True, database_transactions_settled=True,
    configuration_restored=True)  # no residue observation supplied
assert release(request=r, current_state=ReservationState.RUNNING,
               evidence=e).state is ReservationState.RELEASED
```

Manifest generation was run twice using the non-executing CLI:
`env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m
tools.phase_5_0_evidence.execution.cli --manifest-out /tmp/project-review-20260911-manifest-a.json
--render /tmp/project-review-20260911-plan-a.md`, repeated with `-b` output names.
Both generated artifacts match each other and the supplied artifacts byte for
byte. All 34 source SHA-256 values independently match disk; three unresolved
steps remain. No manifest-covered source was changed by this review.

Review-input digest remains
`bbb3854fbdffae00696544465f1cd7bbdf22ad18583056490a6735444800e4fa`;
it is **not execution approval**.

No SSH, target inspection, synchronization, provisioning, database operation,
service change, credential access, generated-vector execution or armed real
boundary/materializer was performed. Database skips are unverified assertions;
the expected database-enabled web skip count is 80, so a local run with 1362
skips cannot establish PostgreSQL correctness. No new Python code was submitted;
compile/format/type checks are not claimed by this documentation-only review.

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**.
Return the bounded design/API corrections for technical review before privileged
mechanism implementation, target preflight or any separate execution decision.
