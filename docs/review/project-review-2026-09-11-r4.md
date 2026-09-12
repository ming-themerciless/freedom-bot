# Independent technical re-review — runner contract r4

Date: 2026-09-11. Reviewer: Codex. Disposition: **changes requested**.

Scope: the R3 remediation handback, runner contract r4, the connected lifecycle
model, shared validator and synthetic tests. This is the active Package 5.0
checkpoint, not a fresh audit of all product packages. No implementation, test,
generated artifact or operational configuration was changed during this review.

The submission makes concrete progress: stored records now reach the shared
validator with target and attribution intact; process restart is distinguished
from power loss; and all seven participants have persistent run accounting.
The remaining failures concern the interpretation and ordering of those records.

## PR-20260911-R4-1 — Blocking: a stale terminal entry hides a newer active reservation

Location: `tools/phase_5_0_evidence/lifecycle_storage.py:1526`
(`check_history_semantics`), especially the RUNNING/RELEASED/QUARANTINED/RECOVERING
branch at line 1553; contract r4 §5.5.

The checker remembers whether an ID was ever admitted but does not require a
transition to belong to the currently active reservation or reject transitions
of an already finished reservation. `finished` is checked only for a new
ADMITTED entry. Consequently this stored history is accepted:

```text
FIRST_USE
ADMITTED A
RELEASED A
ADMITTED B
RUNNING B
RELEASED A       # stale completion from A
```

Independent reproduction appended those entries through the existing Laboratory
fixture and called `admit(reservation_id="C")`. Result:

```text
stale release A while B running: True ()
```

`derive_lifecycle_history()` takes the last entry, reports A released, and loses
the unresolved B. A stale duplicate publication or a syntactically valid corrupt
history can therefore authorize reuse. Repeating an old operator-recovery entry
has the same missing-current-predecessor concern. The separate run ledger does
not make an invalid reservation history valid; the reservation layer promises
its own fail-closed validation, including crashes around admission publication.
This is reproduced in pure code, not against an operational adapter.

Required correction: validate transitions against the current reservation and
its current state, using the accepted transition rules. Permit operator recovery
only for the applicable quarantined predecessor; terminal identities must not
reappear as stale transitions. Validate the proposed append before publication
as well as validating all stored history on read. Test stale releases/recoveries
after a newer ADMITTED/RUNNING entry, transitions after terminal states, duplicate
terminal entries and valid sequential reservations. The result must preserve B's
refusal rather than deriving admission from A's final entry.

## PR-20260911-R4-2 — Blocking: participant completion is not bound to the started run

Locations: `lifecycle_storage.py:2081` (`RunLedger.complete`), `:2130`
(`recover`), `:2189` (`survey`) and `:2275` (`read_and_admit`); contract r4
§§5.5, 5.8 and 5.11.

`complete()` selects completion conditions from the caller-supplied participant,
then appends to the caller-supplied run filename. It never compares that
participant with the stored start entry. The parser validates field names,
sequence and host/target, but the ledger has no semantic check binding run ID,
participant and identity across entries or to the filename. `survey()` declares
a file settled solely from its last entry kind.

Independent reproduction used ordinary model APIs:

```text
begin(run_id="web-1", participant=WEB_SUITE)
admit() -> False
complete(run_id="web-1", participant=FOUNDRY_TESTS,
         observation=all Foundry completion conditions observed)
  -> published=True
admit() -> True
```

Foundry completion does not observe the web suite's database backends or fixture
cleanup. An unfinished web run becomes reusable on another participant's evidence.
The reader would also accept a syntactically valid file containing only a
PARTICIPANT_COMPLETED entry; no corresponding start is required by that parser.
The recovery path needs the same binding checks.

There is a second missing-accounting path in this boundary: `ledger=None` skips
both resealing and survey. With an outstanding web run, the independent call
`admit(ledger=None)` returned **True**. Contract §5.8 requires the ledger for
every participant, so absence must not mean an empty, settled ledger. Unit tests
that intentionally omit this layer should use a separately labelled unit path.

Required correction: one participant-history validator must require a start,
valid terminal progression, stable run/participant/identity binding, filename
binding and the appropriate completion/recovery evidence. Use it both before
append and when surveying existing bytes. Derive the required completion profile
from the validated start, not the completion caller. Reject absent/unreadable
ledger evidence in the connected admission path. Cover wrong participant, wrong
run/filename, terminal-without-start, malformed or empty terminal evidence,
terminal reuse, missing ledger and the valid matching controls for all seven.

## PR-20260911-R4-3 — Important: the successful trace assumes a future release

Locations: contract r4 §5.6 sequence, §5.7 T11/T12 and §5.11 harness row;
`lifecycle_storage.py:1897`; and
`tests/phase_5_0_evidence/test_r3_lifecycle.py:1202`.

The harness completion profile requires both `release()` returning RELEASED
and the release entry having reached durable storage. The declared sequence
publishes participant completion at T11 and RELEASED at T12. The successful
test follows that order but supplies `_observed(HARNESS_CLI)` at t3, which sets
both requirements True while the reservation record still says RUNNING. It only
appends RELEASED at t4. Thus the stated successful path cannot obtain its own
required observation in that order, and its green test masks the contradiction.

Required correction: choose and specify an achievable ordering between the
release decision, reservation release publication and participant completion.
For example, evaluate whether publishing the verified reservation release before
participant completion is safe because the still-started participant ledger
continues to block successors. Make that argument explicit rather than merely
swapping calls. Derive lifecycle-owned observations from the preceding modeled
operations; inject external observations only for facts outside this model.
Test crashes and barrier failures between the two terminal publications, proving
no premature reuse and a successful recovery path. Correct the handback's claim
that the current successful trace establishes the complete sequence.

## Disposition and next action

| Previous finding | Recommendation on this submission |
|---|---|
| R3-1, publication/restart gap | The specific successor directory-barrier correction is technically supported under the specified file-before-rename writer order and cooperative lock custody. The tests exercise visible-but-unsynchronized publication and barrier refusal. This is design/model evidence only. |
| R3-2, ordinary participant crashes | Durable accounting for all seven is the right correction and removes the explicit crashed-suite exemption. Keep the finding open pending R4-2 and the executable ordering in R4-3. |
| R3-3, target and attribution binding | Recommend closure of the specific missing-target/attribution defect: stored bytes and direct validator tests now carry and require those fields. This is not blanket acceptance of history validation; R4-1/R4-2 address that separately. |

The prior R2 state-shape repair, usable directory descriptors, recovery-parent
barrier, post-unlink evidence correction, C1 → C2 → C5 ordering and withdrawn
JNL-47 split remain positively reviewed within their bounded scope. EH-R16-1
remains Open and its privileged remedy remains unbuilt. LAB-1 remains Important
and unrepaired. No maintainer provisioning or identity decision is accepted here.

Next: one bounded local correction to reservation transitions, participant-history
binding and terminal-publication order, with adversarial stored-history regressions.
Retain the current architectural direction; these findings do not require a new
isolation architecture. Return for Codex technical re-review before implementing
the privileged mechanism or requesting approval of its permission delta.

## Independent evidence and limits

From `/opt/freedom-blades/platform`:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python --version
  Python 3.12.3
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
  217 passed in 1.19s
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
  1723 passed in 8.59s; zero skips
git diff --check
  passed
```

The three reproduction outputs above came from a local Python heredoc using
`runpy.run_path('tests/phase_5_0_evidence/test_r3_lifecycle.py')`, its Laboratory
fixture and injected observations. No live effects or real boundary ran.

Independently recomputed all **36** source hashes with hashlib, checked exact set
equality with COVERED_SOURCES read through AST, and generated the manifest and
concrete plan twice to temporary paths through:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m tools.phase_5_0_evidence.execution.cli --manifest-out <temporary>.json --render <temporary>.md
```

Both generations and the supplied artifacts matched byte-for-byte. No generated
artifact or covered source changed. Digest
`45b3c6c0313e5cb8b48e116aea7716b47f1a2d231f12719975d63166d3458201`
is review input only and was not supplied to `--execute`.

Primary [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html) documents
the separate containing-directory barrier, supporting the bounded R3-1 correction.
[flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html) documents lock
release on descriptor closure; this is not evidence of effect completion.
Neither reference establishes target filesystem behavior or implemented custody.

The local interpreter is the restricted-pass exception; the canonical environment
is `/opt/freedom-blades/runtime/venv-web/bin/python` on oracle-test.
TEST_DATABASE_URL was unset. Bot/web suites share a database and must run serially
when authorized; neither was rerun for this scoped review. No earlier suite counts
are adopted as new evidence. Database, Foundry, host, privileged filesystem,
provisioning and target-preflight checks were not run. No formatter/linter/type
check result is claimed. Synthetic lock observations do not prove acquisition or
holding a real lock; the adapter remains unbuilt.

Package 5.0 remains not ready, P5.0-R5 Blocking, OD-62 Open, EH-R16-1 Open.
Three C-7 cases remain unresolved, twelve target facts unconfirmed and execution
ineligible. This review authorizes no host action, permission expansion, migration,
deployment, cutover or Package 5.1+ work and closes no package gate.
