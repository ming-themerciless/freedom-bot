# Handback — lifecycle validation and completion ordering (R4)

> **Dated correction, 2026-09-11 — E13.** This handback's claim that the R4-2
> repair bound participant completion to the started run is **narrowed, and one
> part of it is withdrawn**. The repair did bind the run id, the participant, the
> identity, the filename and the evidence's content and completeness to the stored
> start, and the R5 re-review confirmed those. **It did not bind the
> reservation.** The stored `participant_started` entry carried no reservation
> field, `check_participant_history()` checked only that the completion's
> reservation was non-empty, and `conclude_reservation()` accepted an independent
> caller-supplied `run_id`, so a release of reservation `A` published a valid
> RELEASED entry for `A` and a valid completion into an already-started harness run
> `B`. Any sentence below that reads as *"the binding is complete"* is wrong, and
> the row in §1 for R4-2 should be read as covering the run/participant/identity/
> filename/evidence bindings only.
>
> This is **PR-20260911-R5-1**, recorded in the
> [R5 re-review](project-review-2026-09-11-r5.md) and answered in the
> [R5 handback](project-review-remediation-2026-09-11-r5-handback.md) and
> [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md), which
> supersedes r5. The R5 re-review recommends closure of **R4-1's** specific defect
> and keeps **R4-2** and **R4-3** open; nothing here closes any of them. The
> verification figures below describe the tree that existed on 2026-09-11 before
> the R5 remediation and are not evidence for the current tree; the review-input
> digest `39cea2904f66606a66664f6835633a83a57780f4edc3570d6e8a3942edd196cd` is
> superseded by
> `2fa1d13b7b112f7fda837abcdd70f86ff6d85701602818d810af5fc2141ce5ca`, and neither
> may be passed to `--execute`.

Date: 2026-09-11. Author: Claude. Direction: C-P5.0-LAB-1, reserved disposable
laboratory. Review answered: [R4 re-review](project-review-2026-09-11-r4.md).

**Status: returned to Codex for technical re-review. Nothing is accepted, no
finding is closed on the implementer's authority, and no execution, provisioning,
preflight or host action is authorized.**

* Submitted design, **not accepted and not implemented**:
  [runner contract r5](phase-5-0-reserved-laboratory-runner-contract-r5.md),
  which supersedes [r4](phase-5-0-reserved-laboratory-runner-contract-r4.md).
  r4 now carries a dated supersession and a four-item erratum, and the
  [R3 handback](project-review-remediation-2026-09-11-r3-handback.md) carries
  dated errata **E9–E12**.
* All three R4 findings are answered in one bounded local pass. Two are
  **repaired in pure code**; the third is a **corrected protocol order**, modelled
  and unbuilt like the rest of the mechanism.

**No privileged mechanism, real filesystem writer, lock adapter, host runner or
operational integration was implemented, and nothing was provisioned.** The
proposed permission and provisioning delta is **unchanged at ten items**, and all
ten remain unapproved.

---

## 1. Disposition of the three findings

| Finding | Disposition | Where in r5 | Where in code | Regressions |
|---|---|---|---|---|
| **PR-20260911-R4-1**, Blocking — a stale terminal entry hides a newer active reservation | **repaired in pure code, and submitted as a contract correction.** Transitions are validated against the current reservation and its current state, over `reservation.TRANSITIONS`; the disposition is derived from that rather than from the last entry; the same check runs before an append and on read | §5.5 (rewritten), §5.9, §5.13, §5.14, §9.2 rows 41–44 | `lifecycle_storage.check_reservation_history`, `ReservationHistoryState`, `ENTRY_STATES`, `TERMINAL_STATES`, `derive_lifecycle_history`, `DurableRecordStore.publish` | `test_r4_remediation.py`, R4-1 section, 26 rows |
| **PR-20260911-R4-2**, Blocking — participant completion is not bound to the started run | **repaired in pure code, and submitted as a contract correction.** One participant-history validator used by both writers and the ledger survey; the completion profile is read from the stored start; evidence content and completeness are checked; an absent or unreadable ledger refuses | §5.8, §5.9, §5.11.1 (new), §5.13, §5.14, §9.2 rows 45–50 | `check_participant_history`, `ParticipantRunState`, `CompletionEvidence`, `RunLedger.complete` / `.recover` / `.survey`, `RunLedgerSurvey.invalid`, `read_and_admit` | `test_r4_remediation.py`, R4-2 section, 34 rows |
| **PR-20260911-R4-3**, Important — the successful trace assumes a future release | **corrected order, modelled and unbuilt.** The release decision, then the durable release publication, then the harness's completion, holding the lock throughout. The harness's two conditions are derived from steps 1 and 2; injecting either is refused | §5.6 (order block), §5.7 T10–T12, §5.12 (new), §9.2 row 51, §9.4 (dated erratum) | `TERMINAL_PUBLICATION_ORDER`, `ReleasePublication`, `TerminalPublication`, `conclude_reservation`, `ParticipantProfile.lifecycle_owned_conditions`, `CompletionObservation.injected_lifecycle_facts` | `test_r4_remediation.py`, R4-3 section, 14 rows, plus 2 full-lifecycle rows |

**No finding is closed here.** R4-1 and R4-2 are Blocking and stay open until
Codex says otherwise; R4-3 is Important and stays open with them.

---

## 2. The reproductions, failing before and passing after

Both reproductions were run against the submitted r4 tree **before any edit**,
through the same Laboratory fixture and public model APIs the review used, with
`PYTHONPATH=/opt/freedom-blades/platform` and
`env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python`.

### 2.1 R4-1, the stale terminal entry

```text
FIRST_USE → ADMITTED A → RELEASED A → ADMITTED B → RUNNING B → RELEASED A
```

| | Before | After |
|---|---|---|
| the stale append publishes | **True** | **False**, `INVALID_HISTORY`, stored bytes byte-identical |
| `admit(reservation_id="C")` | **True**, no refusal | **False**; B reported `running` |
| the analogous repeated operator recovery, appended | **True** | **False**, `INVALID_HISTORY` |
| `admit` after that repeated recovery | **True**, no refusal | **False** |

The same six entries planted **around the writer** — bytes a corrected writer can
no longer produce but an earlier revision could — parse successfully and still
refuse on read, deriving no disposition. That is the half a writer-only repair
would have left open.

### 2.2 R4-2, the cross-participant completion

```text
begin    web-1 as WEB_SUITE
complete web-1 as FOUNDRY_TESTS with only Foundry conditions observed
```

| | Before | After |
|---|---|---|
| `admit()` before the completion | False | False |
| the cross-participant completion publishes | **True** | **False**, `INVALID_HISTORY`, naming R4-2 |
| `admit()` after it | **True** | **False**; the web run is still `unsettled` |
| the web run's stored history | replaced | **unchanged** |
| every one of the seven successors after it | not checked | **all refuse** |
| `admit(ledger=None)` with the web run outstanding | **True** | **False**, naming §5.8 |
| a lone `participant_completed` file with no start | published, surveyed **settled** | refused at the writer; **planted around it, surveyed `invalid` and blocking** |

### 2.3 R4-3, the unreachable order

Before: the successful trace called `_observed(HARNESS_CLI)` at t3, which set
both of the harness's conditions to `True` while the reservation record said
`running`, and appended `RELEASED` at t4. After: the trace calls
`conclude_reservation`, which evaluates the release, publishes `RELEASED`, and
completes the harness run on the outcomes of those two operations.
`test_an_injected_lifecycle_fact_is_refused` asserts that the old observation is
now refused, and `test_a_completion_without_a_terminal_publication_refuses`
asserts that the harness cannot complete before it has published anything.

### 2.4 The regressions detect the original defects

Asserted rather than claimed. With the three r5 repairs **reversed in a scratch
copy of the package** — the membership checker and last-entry derivation
restored, the pre-publication semantic check removed, the survey classifying from
the last entry, the omitted ledger tolerated, and the harness's conditions made
injectable again — the new regression module was run against it:

| Tree | `tests/phase_5_0_evidence/test_r4_remediation.py` |
|---|---|
| r5, submitted | **76 passed** |
| r5 with the three repairs reversed | **49 failed, 27 passed** |

The 49 include all three named reproductions, both stored-byte reader cases, the
omitted-ledger refusal, every row of both audits that r4 accepted, and the whole
R4-3 section.

---

## 3. What is pure code, and what is a proposed unbuilt mechanism

**Pure code, in this tree, all of it planning-tier and synthetic:**

| Change | Module |
|---|---|
| the reservation history walked as a state machine over `reservation.TRANSITIONS`, carrying the current reservation, its current state and the recoveries appended so far | `tools/phase_5_0_evidence/lifecycle_storage.py` |
| the derivation reading that state rather than the last entry | same |
| the record store validating a proposed history **before any byte is written**, with the check chosen from the record's own entry kinds so no publication path can omit one | same |
| the participant-history validator, used by `complete`, `recover` and `survey` | same |
| the bounded completion-evidence codec, so content and completeness are checkable | same |
| the lifecycle-owned / external split on the participant profiles, and the derivation of the harness's two conditions | same |
| the terminal publication order as one operation | same |
| the absent ledger refusing in the connected admission path | same |

**Proposed, modelled and not built** — unchanged in kind from r4: the lock
adapter, the reservation-record writer, the ledger writer, the re-seal's real
`fsync`, every path in r5 §7, and every permission in it. `reservation.py` is
unchanged by this pass. `reservation.DECISIONS_DO_NOT_PERSIST` and
`ADAPTER_RESPONSIBILITIES` still say that an admitting decision is not a
reservation and that nothing here enforces anything.

**The models remain models.** `lifecycle_storage`'s whole filesystem is a
dictionary in `durability_model`, `MODEL_LIMITS` travels in every result, and the
module still makes **no observation of the model's durable-state map** —
`test_the_lifecycle_model_makes_no_oracle_observation` asserts that against the
module's syntax tree and still passes. The corrected order does not weaken it:
the harness's derived facts come from **its own call return values**, which a
real writer has, not from the oracle, which no participant has.

---

## 4. The achievable terminal-publication order

**Adopted order**, r5 §5.12: evaluate the release decision → publish the
reservation's `released` entry durably → publish the harness participant's
completion → release the lock.

**Why the harness may know the publication's outcome.** The executor writes the
release entry in this process while holding the lock, so whether its own `fsync`
on the containing directory returned success is the one durability fact a writer
legitimately has. A **successor** has no such fact, which is R3-1, and §5.6's
re-seal is unchanged and still required. The asymmetry is preserved, not softened.

**Why neither half authorizes reuse.** Before the release publication the record
says `running` and refuses. Between the two publications the record says
`released` **and the executor's own run is still `participant_started` in the
ledger**, and an unsettled run refuses every successor including the harness and
the environment reset. Only after both does a successor admit. This is asserted,
not argued: `test_a_restart_between_the_two_terminal_publications_is_blocked_by_the_ledger`
shows a `RELEASED` disposition with `may_proceed` false and
`runs.unsettled == ("RES-1-harness",)`.

**Intermediate states exercised**, each through a process restart, each asserting
no premature admission, preserved prior history and a bounded attributable
recovery:

| Interruption | What a restarted successor finds | Admits? | Recovery |
|---|---|---|---|
| before the release bytes were synchronized | record at `running`; a temporary in the laboratory directory; the run started | no | operator removes the reported temporary, quarantines, appends an attributed recovery, recovers the run |
| after the release bytes, before the rename | as above | no | as above |
| after the release rename, before its directory barrier | `released`, made durable by the successor's re-seal; the run still started | no | operator recovers the run |
| before the completion bytes were synchronized | `released`; a temporary in the runs directory | no | operator removes the temporary, recovers the run |
| after the completion bytes, before the rename | as above | no | as above |
| after the completion rename, before its directory barrier | `released` and the run **completed**, made durable by the successor's re-seal | **yes** | none needed |

The last row admits and that is the correction from R3-1 working rather than a
hole: both halves hold, and the successor established their durability itself.

**Power loss is kept a distinct scenario.** `test_a_power_loss_in_the_window_remains_a_distinct_scenario`
shows the visible release entry disappearing and the record returning to
`running`, which refuses. The restart and the power loss are never modelled by
calling the same operation.

**Stale release evidence from another reservation** refuses at step 1:
`release()` compares the evidence's reservation, target and lock holder with the
request's, neither terminal entry is published, and the reservation stays
`running`.

---

## 5. Interface, schema and permission impact

**Record schema: unchanged.** Same magic line, same `schema=1`, same ten entry
kinds, same field set per kind, same terminator. `SUPPORTED_SCHEMA_VERSIONS` is
still `{1}`. No entry gains or loses a field.

**One field's *content* is now a bounded encoding rather than free text.** A
`participant_completed` entry's `evidence` field is written and read as
`run=…|reservation=…|observed-by=…|condition=…|condition=…`. The field name, the
kind's field set and the parser are untouched; what changed is that the value has
a decoder and an arbitrary string is refused. r4 wrote a different free-text
value into the same field, so **a `participant_completed` entry written by r4
would now be refused as evidence that is not this protocol's evidence**. Nothing
is deployed, so no stored record exists to migrate; it is recorded because it is
a compatibility fact a reviewer should see stated rather than discover.

**Model interfaces that changed**, all planning-tier and all local to this tree:

| Symbol | Change |
|---|---|
| `DurableRecordStore.__init__` | gains `kinds`, defaulting to `RESERVATION_KINDS`. The store knows which record it holds, so the parse, the semantic check and the publication cannot be told three different things |
| `DurableRecordStore.append` | loses `permitted_kinds`; it uses the store's own |
| `RunLedger.complete` | gains `release_publication`; refuses an observation that supplies a lifecycle-owned condition |
| `RunLedgerSurvey` | gains `invalid`, which `settled` now also excludes |
| `read_and_admit` | `ledger=None` refuses instead of surveying nothing |
| `CompletionObservation.missing` | gains `derived` |
| `ParticipantProfile` | gains `lifecycle_owned_conditions` and `external_conditions()` |
| new | `ENTRY_STATES`, `TERMINAL_STATES`, `ReservationHistoryState`, `check_reservation_history`, `CompletionEvidence`, `ParticipantRunState`, `check_participant_history`, `HISTORY_SEMANTICS`, `ReleasePublication`, `TerminalPublication`, `conclude_reservation`, `TERMINAL_PUBLICATION_ORDER`, `HARNESS_RELEASE_DECIDED`, `HARNESS_RELEASE_PUBLISHED`, `EVIDENCE_SEPARATOR` |
| `PublicationRefusal` | gains `INVALID_HISTORY` |
| `check_history_semantics` | kept, now a thin wrapper over `check_reservation_history` |

**Permission and provisioning delta: unchanged, still ten items, still
unapproved.** All three corrections are pure validation and ordering over records
the protocol already stores. No new path, mode, group, identity, capability,
unit or descriptor is required. **No expansion is proposed**, and r5 §6.4 says so
explicitly rather than leaving it inferred, because expanding permissions to
repair pure validation is exactly what the prompt forbids.

**Test-side structure.** `tests/phase_5_0_evidence/lifecycle_fixtures.py` is new
and holds the Laboratory fixture, the observation helper and the byte-planting
helpers, shared by `test_r3_lifecycle.py` and the new
`test_r4_remediation.py` so the two exercise the same arrangement. The planting
helpers write through the model's own path and **around every writer-side
check**, which is what lets the reader be tested independently of the writer.

---

## 6. Commands, results and what was not run

Every command was run from `/opt/freedom-blades/platform` against the tree being
submitted, with `TEST_DATABASE_URL` unset. **The local interpreters are the
restricted-pass exception**; the canonical test environment remains
`/opt/freedom-blades/runtime/venv-web/bin/python` on `oracle-test`, and no SSH,
synchronization or host inspection was performed. Both local interpreters report
**Python 3.12.3**; `node` is **v24.20.0**.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
  217 passed
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_r2_proposal_models.py tests/phase_5_0_evidence/test_r3_lifecycle.py tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py
  326 passed
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_r4_remediation.py
  76 passed
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
  1801 passed, zero skips
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
  3018 passed, 326 skipped, 1 warning
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
  1610 passed, 1362 skipped
node --test 'foundry-module/tests/'*.test.mjs
  171 pass, 0 fail, 0 skipped
git diff --check
  passed
python -m compileall -q  (the five changed Python files)
  ok
```

Bot and web were run **serially**, in that order, because they share one
disposable database.

**Every skip is unverified, and the two figures are load-bearing.** The web
suite's **1362** skips are what a database-disabled run produces; the documented
database-enabled baseline is **80**. The bot suite's **326** skips are the same
cause — `TEST_DATABASE_URL is not configured for a disposable PostgreSQL
database` is the printed reason on both. **Nothing in the skipped set was
verified by this pass**, and the prompt keeps `TEST_DATABASE_URL` unset, so the
database-marked tests were not run at all.

**Checks not run, and why:**

| Check | Why |
|---|---|
| formatter, linter, type checker | **not configured and not installed.** There is no `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `.ruff.toml` or `mypy.ini` in the repository, and neither interpreter has `ruff`, `flake8`, `black`, `mypy`, `pylint` or `pyflakes`. **This is unavailable tooling, not a pass** |
| database-marked tests | `TEST_DATABASE_URL` is kept unset by the restriction |
| anything on `oracle-test` | no SSH, synchronization, host inspection, provisioning, dependency installation or environment reset is authorized |
| the read-only target preflight | it follows implementation review and is not performed or expanded here |
| any real execution | `--execute`, an armed boundary or materializer, and generated-vector execution are all refused |

**No historical count is carried forward.** The R4 independent baseline of 217
structural and 1723 harness tests was about a tree that no longer exists; this
tree's harness total is 1801 because 76 new regressions and two new order cases
were added.

### 6.1 Manifest integrity and the review-input digest

Covered source changed — `lifecycle_storage.py` is in `COVERED_SOURCES` — so the
manifest and the concrete plan were regenerated through the non-executing CLI.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m tools.phase_5_0_evidence.execution.cli --manifest-out <temporary> --render <temporary>
```

* Generated **twice to temporary paths**; both generations byte-identical.
* All **36** covered-source SHA-256 hashes recomputed independently with
  `hashlib`, against `COVERED_SOURCES` read through the AST: **exact set
  equality, no mismatch**.
* The installed artifacts were **replaced with the generated output**, not
  hand-edited, and a **third** generation was compared against the installed
  files byte-for-byte: identical.
* Coverage and schema are **unchanged**: still 36 sources, same manifest schema.
  Only `lifecycle_storage.py`'s hash moved, because only it changed.

**New review-input digest:**

```text
39cea2904f66606a66664f6835633a83a57780f4edc3570d6e8a3942edd196cd
```

It **supersedes** `45b3c6c0313e5cb8b48e116aea7716b47f1a2d231f12719975d63166d3458201`
for this tree. **It is review input only. It must never be passed to
`--execute`.** The dry run still reports `executable: False` and the same twelve
unconfirmed target facts.

---

## 7. Preserved, and not reopened

| Preserved | State |
|---|---|
| the target/attribution repair (R3-3) | positively reviewed; unchanged, and its tests still pass |
| the successor directory barrier under the file-before-rename writer contract | unchanged; §5.6 is untouched apart from the terminal tail of its order block |
| process restart kept distinct from power loss | unchanged, and exercised again in the new window cases |
| accounting for all seven participants | unchanged, and now also exercised as seven success and seven recovery controls |
| the R2 state-shape repair, usable descriptors, recovery-parent barrier, corrected post-unlink evidence | unchanged |
| C1 → C2 → C5 and the withdrawn JNL-47 criterion split | unchanged; **no criterion decision is requested** |
| the valid, provisioned, observed-empty ledger control | **explicitly preserved and given its own test**, so the new refusal is for accounting that was unavailable and not for accounting that was empty |
| the CRP fix, the synthetic skills fixture, the sanitized crafting report, the production alias fix | untouched. **The bot was not restarted** |
| LAB-1 | **Important and unrepaired**, reproduction unchanged |
| EH-R16-1 | **Open**, privileged remedy **unbuilt**, real-execution refusal retained |
| the three C-7 cases | **unresolved** |
| producer-review claims and coverage controls | unchanged |
| `is_executable` | **False** |
| the twelve target facts | **unconfirmed** |

**No new architecture and no new isolation design is proposed**, as the review
asked. Every correction is validation and ordering inside the existing modules.

---

## 8. Remaining proof obligations and unapproved decisions

**Proof obligations, none discharged.** r5 §9.3's implementation checks I1–I10
are unchanged and unperformed. I9 is the one this pass touches without
discharging: a completion condition nobody can observe is a run that never
settles, and the six ordinary participants' conditions remain injected,
attributable claims that the model **does not** verify. The harness's two are now
derived rather than injected, which removes them from the injected set and adds
nothing to the confirmed set: they are model facts about model operations.

**Decisions awaiting a maintainer, after Codex's review and not before:**

1. r5 §7's ten-item provisioning and permission delta — unchanged by this pass,
   still entirely unapproved;
2. V10's identity question, which is both a preflight fact and a decision; and
3. LAB-1's classification.

**Nothing in this handback requests privileged-implementation approval**, and
none is sought before the checkpoint.

---

## 9. Next owner and checkpoint

**Next: Codex technical re-review** of the three corrections, of r5 §§5.5, 5.8,
5.9, 5.11.1, 5.12 and 5.13, and of the regressions in
`tests/phase_5_0_evidence/test_r4_remediation.py`.

Suggested reviewer focus:

* whether the state machine in §5.5 is the right reading of the accepted
  transition rules, and whether any legal history it refuses should be legal;
* whether the stated duplicate-delivery policy — explicit refusal rather than
  idempotence — is the right choice for an append-only record;
* whether §5.11.1's P1–P8 are complete, and whether the bounded evidence encoding
  is the right way to make content checkable;
* whether §5.12's argument holds: that the still-started ledger entry is
  sufficient to block reuse in the window between the two publications; and
* whether the derived/injected split in §0 is drawn in the right place.

**Package 5.0 remains not ready. P5.0-R5 remains Blocking. OD-62 remains Open.
EH-R16-1 remains Open. Passing tests accept no risk and advance no operational
gate.**
