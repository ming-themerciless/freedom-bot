# Handback — reservation-to-harness binding (R5)

Date: 2026-09-11. Author: Claude. Direction: C-P5.0-LAB-1, reserved disposable
laboratory. Review answered: [R5 re-review](project-review-2026-09-11-r5.md).

**Status: returned to Codex for technical re-review. Nothing is accepted, no
finding is closed on the implementer's authority, and no execution, provisioning,
preflight or host action is authorized.**

* Submitted design, **not accepted and not implemented**:
  [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md),
  which supersedes [r5](phase-5-0-reserved-laboratory-runner-contract-r5.md).
  r5 now carries a dated supersession and a three-item erratum, and the
  [R4 handback](project-review-remediation-2026-09-11-r4-handback.md) carries a
  dated correction, **E13**.
* The one Blocking finding is answered in one bounded local pass, **repaired in
  pure code**: one stored field, its grammar, and the comparisons that make it
  load-bearing on the writer and the reader path.

**No privileged mechanism, real filesystem writer, lock adapter, host runner,
preflight or operational integration was implemented, and nothing was
provisioned.** The proposed permission and provisioning delta is **unchanged at
ten items**, and all ten remain unapproved.

---

## 1. Disposition and traceability of PR-20260911-R5-1

| Finding | Disposition |
|---|---|
| **PR-20260911-R5-1**, Blocking — a release can settle another reservation's harness run | **repaired in pure code, and submitted as a contract correction.** The harness's `participant_started` entry durably names the reservation the run owns; terminal publication requires exact equality among the stored start, the reservation request, the release publication, the completion evidence and the reservation the terminal result reports; the same validator runs before an append and on read; and the conclusion checks the binding before the release decision, so a mismatch publishes nothing |

**Where it is, in the contract and in the code.**

| Layer | Where |
|---|---|
| Contract | r6 §5.1 (the finding), §5.5 (the field, its shape, its grammar, the refused filename convention, the r5 compatibility consequence), §5.7 (T6, the new T10a, T12), §5.8 (the new admission condition), §5.11 row 7, §5.11.1 (P7 rewritten, P9 new, the five compared values), §5.12 (step 0, the intermediate state and its recovery), §5.13 (the layer that owns the comparison), §5.14, §6.1, §6.4, §7, §9.2 rows 53–69, §9.3 I11, §9.5 (dated erratum), §10 |
| Schema | `RECORD_SCHEMA_VERSION` 1 → **2**; `SUPPORTED_SCHEMA_VERSIONS` = `{2}`; `KIND_FIELDS[PARTICIPANT_STARTED]` gains `reservation` |
| Reader | `reservation_field_problems()` (new), `check_participant_history()` rules 7 and the start-shape check, `ParticipantRunState.reservation_id` (new) |
| Writer | `RunLedger.begin(reservation_id=…)`, `RunLedger.read_run()` → `StoredRun` (new), `RunLedger._reservation_binding_problems()` (new), `RunLedger.complete()` reading the stored start first, `conclude_reservation()` step 0 |
| Narrative | `RESERVATION_BINDING` (new, seven statements), `TERMINAL_PUBLICATION_ORDER` step 0 |
| Regressions | `tests/phase_5_0_evidence/test_r5_remediation.py`, **58 rows**; `tests/phase_5_0_evidence/lifecycle_fixtures.py` gains `DEFAULT_RESERVATION`, `Laboratory.begin_harness()` and the profile-shaped default in `run_entry()` |

**No finding is closed here.** R5-1 is Blocking and stays open until Codex says
otherwise. **R4-1 carries the R5 re-review's positive technical recommendation and
is not closed on my authority; R4-2 and R4-3 remain open with R5-1.**

---

## 2. The reproduction, failing before and passing after

**The reviewer's exact case, through the existing `Laboratory` fixture and the
public model APIs.** Reproduced first, against the submitted r5 tree:

```text
initialize                                        -> True
ADMITTED A                                        -> published
begin B-harness as HARNESS_CLI                    -> published
RUNNING A                                         -> published
conclude_reservation(reservation=A, run_id=B-harness)

{'concluded': True, 'release': True, 'completion': True}
survey: completed ('B-harness',)  unsettled ()  settled True
```

**After the repair, the same sequence:**

```text
conclude_reservation(reservation=A, run_id=B-harness)

{'concluded': False, 'release': None, 'completion': None}
refusals[0]: run 'B-harness' was started for reservation 'B' and this
             conclusion is of 'A'. **PR-20260911-R5-1**: a release settles the
             harness run that the stored start says belongs to the same
             reservation, and nothing else. …
survey: completed ()  unsettled ('B-harness',)  settled False
B's stored bytes unchanged: True
successor admits: False
```

**What happens to A's already-published RELEASED entry: it is never published.**
The binding is **step 0** of the terminal publication order, before the release
decision, so the release-before-completion order is not entered at all. The
reservation record's bytes are byte-identical afterwards, the reservation stays
`RUNNING`, and `RUNNING` refuses every successor on its own. This intermediate
state is not hidden — **it is not created**, and that is the reason for the
placement. Checking the binding at the completion instead would publish a durable
RELEASED entry into an append-only record on the strength of an unchecked claim,
and then refuse, leaving a reservation that reads terminal beside a run that can
never be settled by it.

**The bounded attributable recovery, demonstrated rather than described.** The run
the caller wrongly named belongs to its own reservation. An operator publishes an
attributed `participant_recovered` entry for it; the reservation whose conclusion
was refused is then concluded against **its own** harness run; both publications
succeed, the survey reports one completed and one recovered, and the successor
admits from stored bytes after a process restart. Nothing is rewritten, no
identity is reused, and the quarantine path is untouched.
`test_the_bounded_attributable_recovery_of_the_refused_conclusion`.

**Planted stored bytes, because a safe writer excuses no reader.** Eight
syntactically valid run files that mismatch — a harness start with no reservation,
with whitespace, with a padded identity; a completion naming a different
reservation from its start; a completion naming none over a bound start; a web
start, a web completion and a reset start each claiming a reservation — are each
classified `invalid` by the survey and refuse **all seven** successors through the
connected admission path. Two more are refused at the parse: an r5 file
(`schema=1`, no reservation field) as `unsupported_schema`, and a schema-2 file
omitting the field as `malformed`. Neither is read as a start whose reservation is
empty.

**Failing-before, measured on a scratch copy and not on the submitted tree.** The
submitted tree was neither modified nor discarded: the scratch copy symlinks every
top-level entry of the repository and replaces `tools/` with a real copy, in which
the repair is reversed — schema back to 1, the reservation field removed from the
start, the presence check restored in place of the equality, the writer's
stored-start read removed, and step 0 removed.

```text
cd <scratch>
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/phase_5_0_evidence/test_r5_remediation.py
  36 failed, 22 passed in 0.10s
```

**36 of 58 fail**, the reviewer's reproduction among them. The 22 that pass are
named rather than glossed: **six** are the grammar rows for a pure helper that has
no r5 counterpart, **one** states the binding contract text that the reversal
leaves in place, and the remaining **fifteen** are the preserved controls that must
hold under both revisions — the six participants' completions, the matching
positive control, the injected-lifecycle-fact refusal, the stale-evidence refusal,
the identity-reuse refusal, the R4-2 profile refusal, and the release-published/
completion-refused window. They are in the file to show the repair broke nothing.

---

## 3. The durable binding, and its reader and writer enforcement

**One durable fact.** The harness's `participant_started` entry carries
`reservation`, published before the run's first effect and never rewritten. It is
a field of the record's bounded schema.

**One representation, required in both directions.** A participant whose
completion conditions are lifecycle-owned — today only `HARNESS_CLI` — carries a
reservation identity. The six whose conditions are external carry the field
**exactly empty**. Neither is optional. Missing, empty, whitespace-only, padded or
changed refuses for the harness; any non-empty value refuses for the six. There is
**no generic metadata bag**, and the parser accepts **one** meaning: a record
written under r5's meanings declares `schema=1` and is refused by name.

**The bounded grammar.** The value equals its own stripped form, contains no line
break, and contains no `|` — the completion evidence's field separator. An
identity that cannot survive the codec that transports it refuses where it is
written rather than where the comparison would silently fail.

**The five values that must agree exactly.**

| # | Value | Source |
|---|---|---|
| 1 | the reservation in the **stored start** | the durable record. **The only binding; the other four are claims** |
| 2 | `ReservationRequest.reservation_id` | the caller; compared at step 0 |
| 3 | `ReleasePublication.reservation_id` | the executor's own publication; compared before any evidence is built |
| 4 | `CompletionEvidence.reservation_id` | **written from value 1**, so a caller cannot choose it; compared with value 1 again on every read |
| 5 | the reservation the `TerminalPublication` reports | the conclusion's own account |

Two would not have been enough, and that is why r5's check looked satisfied: its
completion copied the reservation off the publication, so the comparison compared
a value with itself.

**Enforced on both paths, by the same function.** `HISTORY_SEMANTICS` maps the run
file's entry kinds to `check_participant_history`, and `DurableRecordStore` looks
its own check up there. So the check that validates a proposed append is
**literally** the check that validates stored bytes.
`test_the_validator_is_the_same_function_on_both_sides` asserts the two problem
lists are equal for the same mismatching pair. An invalid publication is refused
**before any byte is written**, so the stored run bytes are unchanged.

**The writer reads the stored start before deriving anything.** `RunLedger.read_run()`
parses and validates the run's own bytes; `complete()` takes the completion
profile, the required conditions and the reservation written into the evidence from
that stored entry. A caller's `participant`, `run_id`, reservation and release
publication are **checked claims**: the participant must equal the stored one, and
the release publication must name the reservation the stored start owns. R4-2's
rule that the required completion profile comes from the stored participant is
preserved and is now applied one step earlier.

**No identity is inferred from a run name.** No prefix, suffix or other convention
over a filename is read, checked or relied on, and **no filename convention is
adopted by r6**. A run named `RES-9-harness` and started for `RES-1` belongs to
`RES-1`: concluding `RES-1` against it succeeds and concluding `RES-9` refuses.
`test_the_binding_is_not_inferred_from_the_run_name` fails the moment an
implementation starts reading a reservation out of a filename. r6 §5.5 states why a
convention would be a second place the binding could disagree with itself, and what
a later revision would have to do to add one as an additional invariant.

**`conclude_reservation()` can no longer settle an unrelated run because both
calls succeeded.** Step 0 requires the named run to be a readable, valid,
in-progress **harness** run whose stored start owns exactly the reservation in the
request. A run started by another participant refuses, an already completed or
recovered run refuses, an absent or invalid run refuses, and each refusal writes
nothing.

---

## 4. Schema, interface, compatibility and permission impact

| Change | Kind |
|---|---|
| `RECORD_SCHEMA_VERSION` 1 → 2, `SUPPORTED_SCHEMA_VERSIONS` = `{2}` | **breaking for stored records.** An r5 record refuses as `unsupported_schema` |
| `KIND_FIELDS[PARTICIPANT_STARTED]` gains `reservation` | **breaking for stored records and for entry construction.** A schema-2 start omitting it is `malformed`; a `RecordEntry` omitting it raises `PlanRefused` |
| `RunLedger.begin(..., reservation_id: str = "")` | **additive keyword.** The default is the six participants' correct value; a harness start that omits it refuses as `invalid_history` rather than publishing |
| `RunLedger.read_run(run_id) -> StoredRun` | **new public reader**, used by `complete()` and available to a caller that wants the stored facts |
| `StoredRun`, `reservation_field_problems`, `RESERVATION_BINDING` | **new exports** |
| `ParticipantRunState.reservation_id` | **new field**, empty on a refused state |
| `RunLedger.complete()` refusals | **changed reason strings**, and `unreadable_predecessor` / `invalid_history` reached earlier than before for an absent run and a mismatched participant claim |
| `TERMINAL_PUBLICATION_ORDER` | **one element longer**; the former step 1 is now the second element |

**The compatibility consequence for r5 participant-start records, stated
explicitly.** They are refused, not migrated. There is no dual-meaning parser and
no reader-side migration: reading an r5 start as one whose reservation is empty
would read an r5 harness run as one whose binding happens to satisfy whichever
branch the reader reached, which is R5-1 with extra steps. Both refusals block
every successor, so a laboratory holding r5 run files is re-initialized, or its
outstanding runs are recovered by an attributed operator entry, before r6's
protocol runs. This is a design statement about a mechanism that **does not
exist**: no such laboratory has been provisioned.

**Permission and provisioning delta: unchanged at ten items, all unapproved.**
R5-1's repair is one additional line in a file the harness already writes, one
comparison over bytes it already reads, and one check moved ahead of a decision it
already took. No new path, mode, group, identity, capability, unit or descriptor is
required. r6 §6.4 and §7 say so explicitly rather than leaving it inferred.

**Existing tests adapted to the new interface, and none weakened.** Thirteen
harness `begin` call sites in `test_r3_lifecycle.py` and `test_r4_remediation.py`
now pass the reservation, through the fixture's new `begin_harness()` helper or a
`reservation_id=` argument; the two parametrized seven-participant controls take
the profile-appropriate value through `_owned_reservation()`; one planted
unknown-participant entry gains `reservation=""`; one schema tamper targets
`schema=2`; and one assertion about `SUPPORTED_SCHEMA_VERSIONS` was updated. **No
assertion was removed, relaxed or deleted**, and the R4 module still holds all 76
of its rows.

---

## 5. Preserved, and not reopened

| Preserved | State |
|---|---|
| R4-1's reservation transition state machine | **unchanged**, positively recommended by the R5 re-review, **not closed here** |
| R4-2's cross-participant refusal, filename binding, evidence content check, required ledger | **unchanged**, and the profile is now read from the stored start one step earlier. Its exact reproduction still refuses with its own `PR-20260911-R4-2` reason |
| R4-3's release-before-completion order and derived lifecycle facts | **unchanged**; step 0 precedes it and changes nothing inside it |
| the evidence codec's own boundary | unchanged; its decode-refusal rows still pass |
| the successor re-seal, and process restart kept distinct from power loss | unchanged, and exercised again in the new sequential trace |
| the release-published/completion-refused window and its recovery | unchanged, and given its own R5 row on a correctly bound run |
| the valid, provisioned, observed-empty ledger control | unchanged |
| identity reuse and stale release evidence refusals | unchanged |
| R3-3's target/attribution binding, the R2 state-shape repair, usable descriptors, the recovery-parent barrier, the corrected post-unlink claim | unchanged |
| C1 → C2 → C5 and the withdrawn JNL-47 criterion split | unchanged; **no criterion decision is requested** |
| the three C-7 cases | **unresolved** |
| target-fact refusals, producer-review controls, `is_executable` | **twelve facts unconfirmed, controls unchanged, `is_executable` False** |
| the CRP fix, the synthetic skills fixture, the sanitized crafting report, the production alias fix | untouched. **The bot was not restarted** |
| LAB-1 | **Important and unrepaired**, reproduction unchanged |
| EH-R16-1 | **Open**, privileged remedy **unbuilt**, real-execution refusal retained |

**No new architecture, isolation mechanism, scheduler or lifecycle-store redesign
is proposed**, as the prompt required. The repair is one field and a set of
comparisons inside the existing modules.

---

## 6. Verification

**Restricted-pass interpreters.** The canonical test environment remains
`/opt/freedom-blades/runtime/venv-web/bin/python` on `oracle-test`. The restriction
forbids SSH, synchronization and host inspection, so the historical local paths
were used as the prompt's restricted-pass exception. Both were verified present
before use: `/opt/discord-bots/venv-web/bin/python` and
`/opt/discord-bots/venv/bin/python` are **Python 3.12.3**, `node` is **v24.20.0**,
and `TEST_DATABASE_URL` was **unset** throughout (`env -u`). Bot and web were run
**serially**, in that order, because they share one disposable database.

| Command | Result |
|---|---|
| `pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **217 passed** |
| `pytest -q -rs tests/phase_5_0_evidence/test_r4_remediation.py` | **76 passed** |
| `pytest -q -rs tests/phase_5_0_evidence/test_r5_remediation.py` | **58 passed** |
| `pytest -q -rs tests/phase_5_0_evidence` | **1859 passed**, zero skips |
| `pytest -q -rs tests/test_*.py` (bot, `venv`) | **3018 passed, 326 skipped** |
| `pytest -q -rs tests/web` (web, `venv-web`) | **1610 passed, 1362 skipped** |
| `node --test 'foundry-module/tests/'*.test.mjs` | **171 passed**, 0 fail, 0 skipped |
| `git diff --check` | passed |
| `compileall` on the four changed Python files | ok |

Structural plus R4 regressions total **293**, matching the R5 independent
baseline; the complete synthetic harness is **1859** because 58 new rows were
added to 1801. **The R5 review's historical counts are comparisons, not evidence
for this tree**, and every figure above was produced against the tree being
submitted, after the generated artifacts were replaced.

**Every skip is unverified, and the two figures are load-bearing.** The web
suite's **1362** skips are what a database-disabled run produces; the documented
database-enabled baseline is **80**. The bot suite's **326** skips have the same
cause — `TEST_DATABASE_URL is not configured for a disposable PostgreSQL
database` is the printed reason on both. **Nothing in the skipped set was verified
by this pass.**

**Checks not run, and why:**

| Check | Why |
|---|---|
| formatter, linter, type checker | **not configured and not installed.** There is no `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `.ruff.toml` or `mypy.ini`, and neither interpreter has `ruff`, `flake8`, `black`, `mypy`, `pylint` or `pyflakes`. **This is unavailable tooling, not a pass** |
| database-marked tests | `TEST_DATABASE_URL` kept unset by the restriction |
| anything on `oracle-test` | no SSH, synchronization, host inspection, provisioning, dependency installation, service change or environment reset is authorized |
| the read-only target preflight | it follows implementation review and is neither performed nor expanded here |
| any real execution | `--execute`, an armed boundary or materializer, and generated-vector execution are all refused |

### 6.1 Manifest integrity and the review-input digest

Covered source changed — `lifecycle_storage.py` is in `COVERED_SOURCES` — so the
manifest and the concrete plan were regenerated through the **non-executing** CLI.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python \
  -m tools.phase_5_0_evidence.execution.cli --manifest-out <temporary> --render <temporary>
```

* Generated **twice to temporary paths**; both generations byte-identical.
* All **36** covered-source SHA-256 hashes recomputed independently with
  `hashlib`, against `COVERED_SOURCES` read through the AST: **exact set
  equality, no mismatch**.
* The installed artifacts were **replaced with the generated output**, never
  hand-edited, and a **third** generation was compared with the installed files
  byte-for-byte: identical.
* Coverage and schema are **unchanged**: still 36 sources, same manifest schema
  `phase-5-0-evidence-review-manifest`. Only `lifecycle_storage.py`'s hash moved,
  because only it changed among the covered set.

**New review-input digest:**

```text
2fa1d13b7b112f7fda837abcdd70f86ff6d85701602818d810af5fc2141ce5ca
```

It **supersedes** `39cea2904f66606a66664f6835633a83a57780f4edc3570d6e8a3942edd196cd`
for this tree. **It is review input only. It must never be passed to
`--execute`.** The dry run still reports `executable: False` and the same twelve
unconfirmed target facts.

---

## 7. Remaining proof obligations and unapproved decisions

**Proof obligations, none discharged.** r6 §9.3's I1–I10 are unchanged and
unperformed. **I11 is new and is this pass's own addition to the list:** the
stored binding's value depends on a reservation identity never being minted twice
over the laboratory's lifetime on the target. The model refuses a readmitted
identity inside one history it can read; nothing establishes that an operator or a
future tool cannot mint the same identity against a re-initialized record. I9 is
unchanged — the six participants' completion conditions remain injected,
attributable claims the model does not verify.

**Decisions awaiting a maintainer, after Codex's review and not before:**

1. r6 §7's ten-item provisioning and permission delta — unchanged by this pass,
   still entirely unapproved;
2. V10's identity question, which is both a preflight fact and a decision; and
3. LAB-1's classification.

**Nothing in this handback requests privileged-implementation approval**, and none
is sought before the checkpoint.

---

## 8. Next owner and checkpoint

**Next: Codex technical re-review** of the binding, of r6 §§5.5, 5.7, 5.8, 5.11.1,
5.12, 5.13 and 9.2 rows 53–69, and of the regressions in
`tests/phase_5_0_evidence/test_r5_remediation.py`.

Suggested reviewer focus:

* whether **step 0's placement** is right — the binding checked before the release
  decision, so no RELEASED entry is published on a claim that fails — or whether
  the reviewer would rather see the intermediate state created and recovered;
* whether the **five compared values** are the complete set, and whether value 4's
  derivation from value 1 makes its own comparison redundant or load-bearing;
* whether **refusing r5 records by schema version** is the right compatibility
  answer for a mechanism that does not yet exist, against the alternative of a
  versioned reader;
* whether **P9's one-representation rule** — the field required empty for the six
  rather than absent — is the right of the two shapes the prompt allowed; and
* whether **I11** is the right statement of the uniqueness assumption the binding
  rests on.

**Package 5.0 remains not ready. P5.0-R5 remains Blocking. OD-62 remains Open.
EH-R16-1 remains Open. Passing tests accept no risk and advance no operational
gate.**
