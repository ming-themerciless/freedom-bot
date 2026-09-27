# Handback — C-P5.0-LAB-V6-P-R2: the operator surface is closed by exact admission — 2026-09-18

> **SUPERSEDED, 2026-09-18, by
> [`phase-5-0-reserved-laboratory-v6-p-r3-exact-detail-admission-handback.md`](phase-5-0-reserved-laboratory-v6-p-r3-exact-detail-admission-handback.md).**
>
> Codex returned this pass **not accepted** with one Blocking finding,
> **PR-20260918-LAB-V6P-R2-1**: `_detail()` collapsed whitespace *before* asking
> the applier's contract, so a value that was not a reviewed detail could become
> one on the way in. **The exact-membership and whole-value claims this document
> makes about `_detail()` were therefore false**, and its section on the detail
> rule should be read as the state of the tree on the day it was written, not as
> a description of the current renderer.
>
> Nothing below has been rewritten, corrected or removed: its commands, figures
> and results stand as the record of what that pass ran and found. The R3
> handback carries the current admission rule, the before-fix reproduction, the
> regression mapping and the superseding digest.


Authorization **C-P5.0-LAB-V6-P-R2**. Claude, implementing Technical Lead. This
is the bounded repository-local remediation of Codex's two findings against
C-P5.0-LAB-V6-P-R1. It is returned **for independent Codex technical and
security re-review** and closes nothing.

## Disposition

| Finding | Class | State after this pass |
|---|---|---|
| **PR-20260918-LAB-V6P-R1-1** — refusal details admitted by character shape | Blocking | **Remediated.** The character rule is gone. A detail is printed only when the applier's own contract says the complete value is one it produces |
| **PR-20260918-LAB-V6P-R1-2** — evidence taken through the historical interpreters | Important | **Remediated.** Every figure below is from `/opt/freedom-blades/runtime/venv-web/bin/python`, and the two pytest configuration warnings it raises are reported rather than absorbed. R1's figures are marked superseded and are not rewritten |

Nothing else moved. LAB-V6-P1 remains **Open** pending this re-review; LAB-V6-P2
is untouched; V6 remains performed-but-not-closed; I3 unconfirmed; V7 excluded;
V8, V10 and I12 unperformed; `plan.is_executable` remains `False`;
`reservation.REAL_EXECUTION_REFUSAL` remains unconditional; Package 5.0 remains
**not ready**. **No action was taken on `oracle-test`**: no SSH, no
synchronization, no inspection, no `sudo`, no group or membership, no edit under
`/etc`, no `systemd-tmpfiles`, and nothing created, adopted, repaired or removed
under real `/run`, `/var/lib` or `/opt/freedom-blades`. No database was
accessed, no participant invoked, no generated vector executed and `--execute`
was not used.

---

## 1. The Blocking finding, and why the old rule could not be patched

`_detail()` admitted a value when every character in it was an ASCII
alphanumeric or a member of a small punctuation set. Codex is right that this is
not a boundary: `hunter2`, `DiscordToken ABCDEFG1234567890` and
`AWS SECRET ACCESS KEY abc def` are written entirely in those characters, and
each was rendered unchanged. The old hostile-detail tests passed because every
case in them carried a giveaway character — `=`, `/`, a bracketed `Errno`,
traceback punctuation — so they exercised the rule's easy half and never its
claim.

**The register a secret is written in is the register ordinary prose is written
in**, so no rule that inspects characters can separate them. The admission is
therefore no longer made on characters at all. It is made on **identity with a
value the provisioner produces**.

### The contract, and where it lives

It is owned by `execution/provisioner.py` — the module that raises the details —
and consumed by the renderer, as the assignment directs.

* **Every fixed detail is now a named module constant.** Thirty raise sites that
  carried inline prose now name `DETAIL_BARRIER_FAILED`,
  `DETAIL_PARENT_REPLACED`, `DETAIL_ROLLBACK_NOT_EMPTY` and the rest. The move
  was performed mechanically over the syntax tree and each literal was asserted
  equal to its original before and after; the applier's 131 focused tests pass
  unchanged, which is the behavioural half of that claim.
* **`REVIEWED_DETAILS`** is the frozen set of those thirty, plus `""` because a
  refusal may legitimately carry no detail.
* **The two details that vary are built, not interpolated.** One ends in the
  list of findings an observation made, the other in the list a post-creation
  read-back made; both lists are drawn from `OBSERVATION_DISCREPANCIES`, which
  is already closed. `unexplained_object_detail()` and
  `verification_failed_detail()` own those two, so the varying part is a list of
  closed findings and can be nothing else.
* **`is_reviewed_detail(text)`** answers *is this, in whole, a detail I
  produce?*. Membership in `REVIEWED_DETAILS`, or — for the two varying ones —
  the prefix followed by a list whose every member is a closed finding **and
  which reproduces the input exactly when rendered back**. That reconstruction
  is the authority; the parsing in front of it only proposes a candidate.
* **`is_reviewed_refusal_detail(text, item_ids)`** answers the same question for
  the composed `classification: item_id — detail` form that
  `ProvisioningRun.refusal.detail` carries. It is admitted by **rebuilding it**
  from a closed classification, an item identifier the caller states it handed
  over, and a detail that is itself reviewed. A real classification in front of
  arbitrary text admits nothing.

None of this is keyword detection, entropy, a secret-name blacklist, a character
class or a test-only case. The renderer asks the applier, and the applier
answers about values it can produce.

### What the renderer does with it

`_detail()` collapses whitespace, asks the contract about the **whole** value,
and either prints it or replaces it with one fixed sentence. The admission is
decided before `FIELD_WIDTH` is applied, so a long value is judged on all of
itself rather than on its first six hundred characters.

**The bound and the control-character stripping are now defence in depth over
values already established as safe, and never the thing that established them.**

### The rest of the operator surface, closed the same way

This is a deliberate extension beyond the literal text of the finding, offered
for Codex's judgement. The R1 module docstring already claimed that every
fragment of its output came from "the reviewed item identifiers, the reviewed
target paths this program itself handed to the applier, the provisioner's fixed
refusal classifications and its fixed refusal details". Classifications were
enforced; identifiers and paths were only bounded. They are now enforced too:

| Field | Admitted by |
|---|---|
| item identifier | identity with an item this program handed to the applier; otherwise `unrecognized-item` |
| path | identity with a target path this program handed to the applier; otherwise withheld |
| classification | membership of `PROVISIONER_REFUSALS` (unchanged from R1) |
| detail | `is_reviewed_refusal_detail` (new) |
| object identity | parsing `st_dev` and `st_ino` as integers and **rendering them back**; a value is shown only when that reproduces it character for character |
| outcome | the `Outcome` enum, by type |

`render_run()` therefore takes the targets the program built, which is the only
statement of those values anywhere in this module — it still writes down no
path, owner, group or mode of its own, and
`test_the_entry_point_writes_down_no_reviewed_value_of_its_own` still holds.

If Codex considers the identifier/path/identity half out of scope for R2, it can
be reverted independently: it is confined to `_admitted()`, `_identity()` and
the `targets` parameter of `render_run()`.

---

## 2. Regression mapping

`tests/phase_5_0_evidence/test_v6_provisioning_cli.py`, **60 → 86 tests**.

| Required proof | Test |
|---|---|
| every detail the real provisioner can produce and the operator contract approves is rendered as intended | `test_every_reviewed_detail_survives_the_renderer_unchanged` (reads the applier's syntax tree, resolves each constant, checks bare and composed forms) |
| arbitrary alphanumeric and space-separated values are withheld whole | `test_an_arbitrary_alphanumeric_value_is_withheld_whole` — nine cases including `hunter2`, a token-shaped value, a database-password-shaped value, a key-shaped value and `freedomlab 1001 1001` |
| adding a new provisioner detail does not make it printable until explicitly admitted | `test_a_new_provisioner_detail_is_not_printable_until_it_is_admitted` — plausible new prose is withheld, is still withheld when raised through the real `ProvisioningRefused`, and prints only once it is in `REVIEWED_DETAILS`. `test_the_admitted_vocabulary_is_exactly_what_the_applier_raises` asserts set equality between the raise sites and the contract, so a detail added without admission fails the suite |
| classification membership alone cannot make a detail printable | `test_classification_membership_alone_cannot_make_a_detail_printable` — all 30 classifications and all 9 observation findings are withheld as details |
| composed `ItemRefusal` details cannot bypass exact admission | `test_a_composed_detail_cannot_carry_an_unadmitted_detail` — arbitrary text behind a real classification, an invented classification, an item never handed over, and a missing separator |
| the finite discrepancy variation cannot bypass exact admission | `test_the_finite_discrepancy_variation_is_admitted_and_nothing_else_is` — empty, single, whole and repeated lists admitted; a smuggled element or a rewritten fixed half withheld |
| long input, Unicode/control characters, paths, traceback text, OS messages and account-record-shaped text remain bounded or withheld | `test_a_detail_outside_the_reviewed_vocabulary_is_withheld_whole` (8 cases incl. 10 000 characters, Unicode, a directory listing), `test_a_control_character_never_reaches_the_operators_terminal`, `test_no_reviewed_detail_is_truncated_by_the_bound` |
| identifiers and paths outside what was supplied are not printed | `test_an_identifier_or_path_this_program_did_not_supply_is_not_printed` |
| object identity carries nothing but two integers | `test_an_object_identity_is_admitted_only_by_being_rebuilt` — 9 cases |
| success, already-provisioned, every reviewed refusal classification, partial application, unidentified residue and the inert default path retain R1 behavior | the R1 tests, unchanged in intent: `test_a_successful_application_renders_every_item_and_exits_zero`, `test_an_already_compliant_host_is_not_reported_as_a_creation`, `test_every_reviewed_refusal_renders_safely_and_completely` (all 30 classifications), `test_a_partial_application_reports_residue_and_what_was_never_tried`, `test_an_unidentified_residue_is_reported_and_blocks_a_guarded_reversal`, `test_without_the_flag_nothing_is_constructed_read_or_written`, `test_the_inert_rendering_claims_no_run` |
| the structural guards still prove no second authority or route to execution | `test_the_entry_point_imports_only_what_its_four_statements_need`, `test_the_entry_point_offers_no_second_input_and_no_second_authority`, `test_the_entry_point_writes_down_no_reviewed_value_of_its_own`, `test_removing_the_flag_check_still_creates_nothing`, `test_the_exit_codes_distinguish_the_four_outcomes` |

Two R1 tests were adapted rather than removed: the AST scan now resolves a
constant name as well as a literal, and `render_run` is called with the targets
it renders against. No assertion was weakened.

**No test runs as root and no test touches a provisioned path.** Every mutating
test drives the real `DirectoryProvisioner` over `tmp_path` with an injected
account lookup resolving to this process's own ids.

---

## 3. Test evidence — canonical interpreter only

**This supersedes §5 of the R1 handback**, whose figures came from
`/opt/discord-bots/venv-web/bin/python` and `/opt/discord-bots/venv/bin/python`
(pytest 8.4.2). Those commands and results are left in place, marked superseded,
and are not rewritten.

Interpreter: **`/opt/freedom-blades/runtime/venv-web/bin/python`**, Python
3.12.3, **pytest 9.1.1** — the environment `.agents/AGENTS.md` names. Run
**locally and serially with `TEST_DATABASE_URL` unset**.

```bash
env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning_cli.py
env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning.py
env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py tests/phase_5_0_evidence/test_concrete_plan.py
env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/web/test_p3_4_static_assets.py
python3 .claude/hooks/test_guards.py
/opt/freedom-blades/runtime/venv-web/bin/python -m compileall -q <the three changed Python files>
git diff --check
```

| Run | Passed | Failed | Skipped | Warnings |
|---|---|---|---|---|
| operator CLI tests | **86** | 0 | 0 | 2 |
| `test_v6_provisioning.py` (the applier) | **131** | 0 | 0 | 2 |
| `tests/phase_5_0_evidence` | **2 464** | 0 | **0** | 2 |
| `test_no_execution.py` + `test_concrete_plan.py` | **320** | 0 | 0 | 2 |
| `tests/web/test_p3_4_static_assets.py` | 110 | **1** | 0 | 2 |
| `.claude/hooks/test_guards.py` | **31/31** — 19 refused, 12 allowed | — | — | — |
| `compileall` | succeeded on all three changed files | — | — | — |
| `git diff --check` | clean | — | — | — |

**The two warnings are the canonical-interpreter pytest configuration warnings
Codex observed**, and they are present on every run above:

```
PytestConfigWarning: Unknown config option: asyncio_default_fixture_loop_scope
PytestConfigWarning: Unknown config option: asyncio_mode
```

They are raised by pytest 9.1.1 reading two `pytest-asyncio` options that this
interpreter's plugin set does not register. **They are an environment/plugin
mismatch, not a finding about this change, and they are reported rather than
suppressed.** R1's "0 warnings" figures described pytest 8.4.2 under the
historical interpreters and are superseded.

**The 2 464 figure replaces R1's 2 438**, and the arithmetic is this pass's 26
new operator tests: R1 reported 2 438 with 60 tests in
`test_v6_provisioning_cli.py`, this pass takes that file to 86, and
2 438 + 26 = 2 464. **That is an accounting of the difference, not a measurement
of the old tree under the new interpreter**, which was not run and is not
claimed.

**The one web failure is the pre-existing tree-shape guard R1 already reported
and did not repair**, and this pass does not repair it either:
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
requires at least one *collapsed untracked directory* in `git status
--porcelain=v1`, and this tree has none. Nothing in this remediation changes its
premise, and the restriction excludes repairing it.

**No database evidence is claimed.** `TEST_DATABASE_URL` was unset for every
command, so every database-marked assertion in this pass is unverified. The
correct web skip count with the variable exported is 80; that run was not
performed and is not claimed.

**No formatter, linter or type checker is configured in this repository** —
there is no `pyproject.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `.pylintrc`.
That is an unconfigured check, **not a pass**.

### Checks not run, and why

* **The full bot suite (`tests/test_*.py`) and the full web suite
  (`tests/web`)** could not be run through the canonical interpreter on this
  development host: it has no `discord` module (7 collection errors) and no
  `bs4` (8 collection errors). Per `.agents/AGENTS.md`, that is an environment
  problem rather than a broken suite, and interpreter availability on one host
  does not establish it on another. **Falling back to `/opt/discord-bots/` is
  what the Important finding objected to, so it was not done.** These two suites
  are not in this assignment's required list; `test_p3_4_static_assets`, which
  is, runs under the canonical interpreter and is reported above. This gap is
  offered to the maintainer as an observation: the documented canonical
  interpreter is not presently able to collect either full suite on this host.
* **Everything on `oracle-test`** — SSH, synchronization, inspection,
  provisioning, `systemd-tmpfiles`, group and membership changes, controlled
  write verification, I3, V7, V8, V10, I12, a real boundary or materializer, a
  participant, a generated vector and `--execute`. All are excluded by the
  restriction and none was attempted.
* **The Foundry module's `node --test` suite** was not re-run; no JavaScript
  changed in this pass.

---

## 4. Review artifacts — regenerated through the non-executing route only

Two covered sources changed, so the manifest and the concrete plan were
regenerated. **Only the existing non-executing route was used**, twice into a
scratch directory and then into the repository:

```bash
python -m tools.phase_5_0_evidence.execution.cli --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
python -m tools.phase_5_0_evidence.execution.cli --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
                                                 --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`. The dry run
reported `executable : False`. Generations 1 and 2 were **byte-identical** to
each other and to the copies written into the repository, and a third
generation taken after the last edit reproduced both files exactly again.

New digest:
`abd643732c23bda0179c1cc1cc97010c7e10594a16a5b8c10d82104c62e9b0bd`
(R1's, which it replaces:
`2be8dae8b81256af01e5e1f9ac702ef256401ae62624c27a9396badefbb23101`).

**This digest is review input only.** It is not an approval, it was not passed
to `--execute`, and `plan.is_executable` remains `False`.

**`MANIFEST_VERSION` stays at 14.** The covered set is unchanged from R1 — the
same 45 files — and this pass changed the contents of two of them. A changed
covered file changes its digest and nothing else; the manifest schema, the
supplied-observation schema (3), the run-record schema (3),
`plan.PERMITTED_EXECUTABLES` (20), the verb table (20), the eleven-item delta
and `is_executable = False` are all unmoved. R1's disclosure stands: a diff of
this file against `HEAD` still folds in the earlier uncommitted
C-P5.0-LAB-V6-R1 work, because the committed copy is at `manifest_version` 12.

---

## 5. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/provisioner.py` | 30 inline refusal details extracted to named constants; 2 interpolated details moved into `unexplained_object_detail()` / `verification_failed_detail()`; new `REVIEWED_DETAILS`, `is_reviewed_detail()`, `is_reviewed_refusal_detail()`; `Collection` imported; `__all__` extended. **No change to any refusal's classification, timing, ordering, partial-state accounting or reversal behavior** — 1 895 → 2 128 lines |
| `tools/phase_5_0_evidence/execution/provisioning_cli.py` | `SAFE_DETAIL_PUNCTUATION` and the character-shape loop removed; `_detail()` now asks the applier's contract; new `_admitted()`, `_identity()`, `UNRECOGNIZED_ITEM`, `WITHHELD_PATH`, `WITHHELD_IDENTITY`; `render_run()` takes the handed targets; docstring section rewritten — 398 → 470 lines |
| `tests/phase_5_0_evidence/test_v6_provisioning_cli.py` | section 8 replaced and section 9 added; 60 → 86 tests, 985 → 1 299 lines |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated, non-executing route, review input only |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated, same route |
| `docs/review/phase-5-0-reserved-laboratory-v6-p-r1-provisioning-entry-point-handback.md` | superseded-evidence banner added at the top. **Its commands and figures are left intact** |
| `docs/review/phase-5-0-reserved-laboratory-v6-p-r2-provisioning-safe-output-handback.md` | this document |

`git status` was inspected first and every unrelated, earlier-pass and
reviewer-authored change is preserved. No register was edited: the status, RAID,
decision and change registers record the maintainer's authorizations and gate
decisions, and this pass closes nothing and decides nothing.

---

## 6. Security implications

* The Blocking finding's exact examples are now withheld: `hunter2`,
  `DiscordToken ABCDEFG1234567890` and `AWS SECRET ACCESS KEY abc def` each
  render as the fixed withholding sentence, verified directly and in the suite.
* The guarantee the assignment names — *no secret or environment value may reach
  operator output* — is now a property of an admission set rather than of a
  character class. A value reaches an operator only if the provisioner could
  have produced it.
* **The guarantee does not depend on this module staying correct about what is
  dangerous.** It depends on the applier's list of what it says, which is the
  thing a reviewer can read in one place.
* No secret file was read, written or referenced. No `.env`, credential JSON,
  key, certificate or cookie file was touched; the secrets guard refused
  nothing because nothing approached it.
* The entry point gained no authority: no new option, no environment read, no
  subprocess, no `sudo`, no alternate layout, no repair mode, no automatic
  rollback, no lifecycle initialization and no route to the executing runner.
  Its import graph is unchanged apart from three names taken from the applier it
  already imports.

## 7. Repository rollback

Everything in this pass is repository-local and reversible by file:

```bash
git checkout -- docs/review/phase-5-0-evidence-harness-review-manifest.json \
                docs/review/phase-5-0-evidence-harness-concrete-plan.md
```

restores the committed review artifacts (to `manifest_version` 12, the stale
state R1 documented). `execution/provisioner.py`,
`execution/provisioning_cli.py` and `test_v6_provisioning_cli.py` are untracked
and belong to the R1/V6 work; reverting **this pass** within them means removing
the safe-detail contract section from the applier, restoring the character rule
in the renderer and restoring sections 8–9 of the suite — which reinstates the
Blocking finding and is offered only for completeness. Deleting the two new
handback files and the R1 banner reverses the documentation.

**There is nothing to roll back outside this repository.** No host was touched.

## 8. Assumptions and unresolved questions

1. **The composed form's item identifiers.** `is_reviewed_refusal_detail` takes
   the identifiers the caller handed over. On the production route those are
   exactly V12, V4, V9 and V5; on the pre-target refusal path — a refusal raised
   while `directory_targets()` is building — no target exists yet, so the four
   released identifiers are used. Stated rather than assumed silently.
2. **`REVIEWED_DETAILS` duplicates nothing but must be maintained.** A detail
   added to the applier is inert until it is admitted. That is the assignment's
   requirement, and
   `test_the_admitted_vocabulary_is_exactly_what_the_applier_raises` makes
   forgetting it a test failure rather than a silent withholding. Codex should
   confirm it considers a failing test the right failure mode here.
3. **The identifier/path/identity extension** is described in §1 and can be
   reverted independently if Codex judges it outside R2's scope.
4. **The canonical interpreter cannot collect the full bot or web suites on this
   development host.** Reported above; it needs a maintainer decision, not an
   implementer's workaround.

## 9. Proposed reviewer focus areas

1. `is_reviewed_detail` / `is_reviewed_refusal_detail` — in particular whether
   the reconstruction on the last line of `_is_discrepancy_detail` really is the
   authority, and whether the composed-form rebuild can be satisfied by anything
   the applier would not produce.
2. The mechanical constant extraction: that all thirty values are byte-identical
   to the ones R1's applier raised, and that no refusal changed classification,
   ordering or partial-state accounting.
3. Whether `REVIEWED_DETAILS` set-equality with the raise sites is the right
   guard, or whether admission should be narrower still.
4. The identifier/path/identity extension — scope as much as correctness.
5. That the inert path, the single arm, the reversal guard and the
   no-second-authority guards are all unchanged in force.

## Status after this pass

LAB-V6-P1 **Open**; LAB-V6-P2 untouched; V6 performed-but-not-closed; I3
unconfirmed; V7 excluded; V8, V10, I12 unperformed; `plan.is_executable`
**False**; `reservation.REAL_EXECUTION_REFUSAL` unconditional; Package 5.0 **not
ready**; P5.0-R5 Blocking; OD-62 Open.

Claude closes no finding, approves no digest, applies no provisioning and
advances no gate. **Stopped for independent Codex technical and security
re-review.** A later operational retry requires Peter's separate release after
Codex accepts this remediation.
