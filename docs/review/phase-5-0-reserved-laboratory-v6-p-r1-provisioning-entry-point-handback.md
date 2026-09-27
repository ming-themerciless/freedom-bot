# Handback — C-P5.0-LAB-V6-P-R1: the reviewed directory provisioner now has an operator entry point — 2026-09-18

> **Reviewed 2026-09-18 and returned not accepted.** Codex raised Blocking
> **PR-20260918-LAB-V6P-R1-1** (refusal details admitted by character shape
> rather than by an exact reviewed vocabulary) and Important
> **PR-20260918-LAB-V6P-R1-2** (this evidence was taken through the historical
> `/opt/discord-bots/` interpreters rather than the documented
> `/opt/freedom-blades/runtime/venv-web/bin/python`).
>
> **§5 "Test evidence" below is superseded.** Its commands and figures are left
> exactly as they were recorded — they are the history of what was run, not a
> claim about the canonical environment — and they are **not** evidence for the
> current tree. The canonical-interpreter reruns, the actual warning counts and
> the remediation itself are in
> [the R2 handback](phase-5-0-reserved-laboratory-v6-p-r2-provisioning-safe-output-handback.md).
> The safe-output contract described in §4 of this document was replaced there.

Claude implemented the bounded repository change Peter authorized as
**C-P5.0-LAB-V6-P-R1** and returns it for **independent Codex technical and
security review**. Claude is the implementing Technical Lead; Codex is the
Independent Technical and Security Reviewer and must accept this before it is
used on `oracle-test`.

## Disposition

**Nothing was applied, anywhere.** No SSH, no synchronization, no inspection of
`oracle-test`, no `sudo`, no group or membership, no edit under `/etc`, no
`systemd-tmpfiles`, and nothing created, adopted, repaired or removed under real
`/run`, `/var/lib` or `/opt/freedom-blades`. No V7 initialization, no I3, V8,
V10 or I12, no participant, no database, no generated vector, no real boundary
or materializer, and no `--execute`. `plan.is_executable` is still `False` and
`reservation.REAL_EXECUTION_REFUSAL` is still unconditional.

**The blocker is closed in the repository and only in the repository.** The gap
the C-P5.0-LAB-V6-P pass stopped on — RAID **LAB-V6-P1**, *no already reviewed
operator invocation can drive the directory provisioner as approved* — now has
one: `tools/phase_5_0_evidence/execution/provisioning_cli.py`. Whether it may be
run is Peter's separate release after Codex accepts it. **LAB-V6-P1 stays Open**
until that review; Claude closes no finding, approves no digest, applies no
provisioning and advances no gate.

**LAB-V6-P2 was not repaired**, as the assignment directs. The `guard-secrets.py`
over-refusal reported by the previous pass is untouched, and the guard still
passes 31/31.

---

## 1. The exact interface

One module, one program, one flag.

```
python -m tools.phase_5_0_evidence.execution.provisioning_cli            # reads nothing
python -m tools.phase_5_0_evidence.execution.provisioning_cli --apply    # arms the applier
```

`build_parser()` defines exactly one option beside argparse's own `-h/--help`:
`--apply`, `action="store_true"`, default `False`. There is **no** alternate
path, layout, owner, group, mode, target, host, identity, repair, rollback,
dry-run-with-effects or digest option, and no environment variable is read.
`test_the_application_flag_is_the_only_option_and_is_off_by_default` and
`test_the_entry_point_offers_no_second_input_and_no_second_authority` assert
that against the parser and against the module's syntax tree.

Public names: `main`, `build_parser`, `render_not_applied`, `render_run`, the
four exit codes, `FIELD_WIDTH`, `NO_IDENTITY`, `UNRECOGNIZED_CLASSIFICATION`,
`SAFE_DETAIL_PUNCTUATION`, `WITHHELD_DETAIL`.

## 2. The call graph

**Without `--apply`** — the whole path, and nothing is elided:

```
main(argv) → build_parser().parse_args(argv) → args.apply is False
           → sys.stdout.write(render_not_applied())      # APPLIED_DIRECTORY_ITEMS only
           → return NOT_APPLIED_EXIT_CODE (3)
```

No lookup is constructed, no provisioner is assembled and no target is built, so
**no account-database read, no filesystem read and no mutation occurs on this
path**. `render_not_applied()` names the four fixed identifiers from
`provisioning.APPLIED_DIRECTORY_ITEMS` — a constant of the reviewed release, not
a host read — and states that nothing was applied.

**With `--apply`**, four statements and no fifth:

```
main(["--apply"])
  → directory_targets()                                  # no arguments: production V12, V4, V9, V5
  → SystemIdentityLookup()                               # execution.boundary; construction reads nothing
  → DirectoryProvisioner(lookup=…, armed=args.apply)     # the arm IS the flag
  → DirectoryProvisioner.apply(targets)   → ProvisioningRun
  → sys.stdout.write(render_run(run, completed))
  → return COMPLETED_EXIT_CODE | REFUSED_EXIT_CODE
```

The reviewed provisioner is **reused, not reimplemented**: no path, owner, group,
mode or order is written down in the entry point, and
`test_the_entry_point_writes_down_no_reviewed_value_of_its_own` asserts that no
item's subject, mode, owner or group literal appears in the module.

**The import graph is the authority argument.** Absolute imports are exactly
`__future__`, `argparse`, `sys`, `typing`. Relative imports are exactly
`..provisioning` (for `APPLIED_DIRECTORY_ITEMS`), `.boundary` (for
`SystemIdentityLookup` **and nothing else**) and `.provisioner`. It imports no
`cli`, `executor`, `materializer`, `case_program`, `artifact`, `descriptors`,
`participants`, `host_lock`, `lifecycle_record`, `run_ledger` or
`recovery_store` — so there is no call path from this program to an execution, a
lifecycle initialization, a participant or a second applier.
`test_the_entry_point_imports_only_what_its_four_statements_need` asserts the
whole set in both directions.

**The process must already be effective UID 0.** The entry point does not
elevate, does not `sudo`, starts no process, composes no shell string and reads
no environment value. The reviewed provisioner's
`_require_provisioning_identity` refuses before the first `mkdirat` when the
process is not the identity the item declares.

**V1, V2 and V3 are not implemented, executed or wrapped.** This entry point
owns V12, V4, V9 and V5. The later operational pass retains the approved
whole-subset order V1, V2, V3, V12, V4, V9, V5. V7 remains excluded and the
provisioner refuses it by name. There is no repair mode and **no automatic
rollback**: reversing a partly provisioned host stays the operator's decision on
each item's reviewed `rollback` field.

## 3. The arm, and why a single-point reversal does not defeat it

Two independent points, deliberately.

1. **The early return.** `main` returns before anything is constructed when the
   flag is absent. `test_the_production_route_is_unreachable_before_the_flag_is_checked`
   asserts that every call to `DirectoryProvisioner`, `SystemIdentityLookup` and
   `directory_targets` occurs after that branch.
2. **The arm is the flag, not a constant.** `armed=args.apply` is written as the
   parsed attribute; `test_the_arm_is_the_flag_itself_and_never_a_constant`
   reads the construction out of the syntax tree and refuses an `ast.Constant`
   there.

`test_removing_the_flag_check_still_creates_nothing` is the negative control the
assignment asks for, and it is a real reversal rather than an assertion that one
is absent: it **deletes the flag check from the module's syntax tree, compiles
the result and runs it**. The mutated program reaches the construction, builds an
**unarmed** provisioner, refuses `provisioner-not-armed` on V12, attempts V4, V9
and V5 not at all, creates nothing under the model host and exits non-zero.

## 4. The output and exit contract

Output goes to standard output as the complete account of the run; a refused or
unclassified run additionally puts **one fixed line** on standard error, so a run
whose output was redirected still says so.

`render_run` emits, for every run:

* `items applied` and one line per `AppliedItem`: its item identifier, its
  outcome — `created`, `already-provisioned` or `created-identity-unknown` — the
  reviewed target path, and the recorded `(st_dev, st_ino)` identity or the fixed
  `none recorded`;
* the refusal's item, classification and detail, or `refusal : none`;
* `not attempted`, naming every item the run never reached;
* `created by this run` and `unidentified residue`, which is the residue account;
  and
* whether a guarded reversal is available, with the fixed statement that **this
  program performs none**.

| Status | Meaning |
|---|---|
| `0` | every one of the four items was created or verified already compliant |
| `3` | `--apply` was not given. No account database and no filesystem was read |
| `4` | the run refused or was incomplete |
| `6` | a condition this program does not classify; nothing about it is printed |

Zero is returned only when `run.complete`, the applied count equals the target
count, there is no unidentified residue, and every outcome is `CREATED` or
`ALREADY_PROVISIONED`. It never means *"the command ran"*. None of the non-zero
codes is `1`, so *"the host is not provisioned as reviewed"* is never the same as
*"something went wrong in this program"*.

### What may reach an operator, as a mechanism rather than a promise

* **Every field is collapsed to one line, stripped of non-printable characters
  and truncated at `FIELD_WIDTH = 600`.** A multi-line value cannot become a
  multi-line field and nothing can address a terminal rather than being read by
  it. `test_a_control_character_never_reaches_the_operators_terminal`.
* **A classification is checked against `provisioner.PROVISIONER_REFUSALS`**,
  imported rather than restated; anything else renders as
  `unrecognized-classification` and says nothing more.
* **A detail is shown only when it has the shape a reviewed detail has, and is
  otherwise withheld whole.** The shape is decided on the untruncated value,
  before the bound, so a long unsafe detail cannot be admitted because its
  giveaway fell off the end.
* **The catch-all prints nothing about what it caught.** An exception outside
  the reviewed vocabulary yields exit `6` and a fixed notice; its text, type and
  traceback are never emitted.

`SAFE_DETAIL_PUNCTUATION` is **derived from the applier's own details, not
chosen**. `test_every_reviewed_detail_survives_the_renderer_unchanged` reads
every detail out of `execution/provisioner.py`'s syntax tree — including the one
`ast.JoinedStr` that interpolates the closed observation vocabulary — and asserts
each one, and the `classification: item_id — detail` form `apply()` builds,
passes through **unchanged**. That is the half that keeps the rule honest: a
renderer that withheld everything would satisfy *no unsafe text is emitted* and
tell an operator nothing.

**A defect found and fixed during this pass, recorded because it is the kind a
reviewer should look for.** The first version of the shape rule used a character
set derived from the applier's *literal* details only. A manual run over a model
host showed the `object-wrong-type` refusal being withheld: one reviewed detail
is an f-string ending `All disagreements: {list(observation.discrepancies)}`,
whose brackets the set did not admit, and whose composed length exceeded the
original 400-character bound. Both were corrected, the derivation now reads
f-strings, and the two regressions are asserted
(`test_every_reviewed_detail_survives_the_renderer_unchanged`,
`test_no_reviewed_detail_is_truncated_by_the_bound`).

## 5. Test evidence

`tests/phase_5_0_evidence/test_v6_provisioning_cli.py`, **60 tests, all passing**.
Every mutating test drives the **real** `DirectoryProvisioner` over `tmp_path`
with an injected account lookup that resolves the reviewed owner and group to the
test process's own ids. **No test runs as root and no test touches a provisioned
path.** Two replacements and no third: the layout the reviewed factory is called
with, and the account database.

| Required proof | Test |
|---|---|
| import and no-argument invocation cause no account lookup, filesystem write or provisioner application | `test_without_the_flag_nothing_is_constructed_read_or_written` (doubles that raise on contact), `test_the_inert_rendering_claims_no_run`, `test_nothing_is_constructed_when_the_module_is_imported` |
| the explicit flag is required and is the only arm | `test_the_application_flag_is_the_only_option_and_is_off_by_default`, `test_the_arm_is_the_flag_itself_and_never_a_constant`, `test_the_production_route_is_unreachable_before_the_flag_is_checked` |
| the production route constructs `SystemIdentityLookup`, calls the real `directory_targets()` default and preserves V12, V4, V9, V5 order | `test_the_reviewed_factory_is_called_with_no_alternate_layout`, `test_the_production_route_applies_exactly_what_the_factory_built` (compares the handed targets with `directory_targets()` itself, creating nothing) |
| success renders every applied item, outcome and object identity and exits zero | `test_a_successful_application_renders_every_item_and_exits_zero` |
| already-compliant distinguished from created | `test_an_already_compliant_host_is_not_reported_as_a_creation` |
| every reviewed refusal classification renders without a raw exception, traceback, operating-system message or unbounded text, and exits non-zero | `test_every_reviewed_refusal_renders_safely_and_completely` (parametrized over all 30 members of `PROVISIONER_REFUSALS`), `test_an_injected_operating_system_failure_never_reaches_the_operator`, `test_a_detail_outside_the_reviewed_shape_is_withheld_whole`, `test_an_unclassified_condition_says_nothing_about_itself` |
| partial application reports the refusing item, residue/applied account and every not-attempted item, with no automatic rollback | `test_a_partial_application_reports_residue_and_what_was_never_tried`, `test_an_unidentified_residue_is_reported_and_blocks_a_guarded_reversal` |
| non-root application refuses before any directory creation | `test_an_application_by_the_wrong_identity_refuses_before_any_creation` |
| no alternate path/layout/owner/group/mode input, environment arm, subprocess, `sudo`, V1–V3 operation, lifecycle initialization, evidence-harness execution or rollback option | `test_the_entry_point_imports_only_what_its_four_statements_need`, `test_the_entry_point_offers_no_second_input_and_no_second_authority`, `test_the_entry_point_writes_down_no_reviewed_value_of_its_own`, `test_the_exit_codes_distinguish_the_four_outcomes` |
| a single-point reversal that removes or bypasses the explicit arm is caught | `test_removing_the_flag_check_still_creates_nothing` |

### Commands run, in order, and their exact results

Interpreters, **verified on this host before use**:
`/opt/discord-bots/venv-web/bin/python` and `/opt/discord-bots/venv/bin/python`,
both Python 3.12.3 with pytest 8.4.2; `node` for the Foundry module.
`/opt/freedom-blades/runtime/venv-web/bin/python` (3.12.3) is present here with
pytest 9.1.1 and was **not** used, so the figures below are all from one pytest
version.

All suites were run **locally and serially with `TEST_DATABASE_URL` unset**, as
the assignment directs.

```bash
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning_cli.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python     -m pytest -q -rs tests/test_*.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
python3 .claude/hooks/test_guards.py
/opt/discord-bots/venv-web/bin/python -m compileall -q <the five changed Python files>
git diff --check
```

| Run | Result |
|---|---|
| new operator tests | **60 passed**, 0 failed, 0 skipped, 0 warnings |
| `test_v6_provisioning.py` | **131 passed**, 0 failed, 0 skipped, 0 warnings |
| `tests/phase_5_0_evidence` | **2 438 passed**, 0 failed, **0 skipped**, 0 warnings (baseline before this pass: 2 374) |
| bot suite `tests/test_*.py` | **3 027 passed, 326 skipped, 1 warning** |
| web suite `tests/web` | **1 609 passed, 1 362 skipped, 1 failed**, 0 warnings |
| Foundry module | **171 passed, 0 failed** |
| `.claude/hooks/test_guards.py` | **31/31** — 19 refused, 12 allowed |
| `compileall` | succeeded on all five changed Python files |
| `git diff --check` | clean |

**The 64 new tests in the evidence suite** are the 60 operator tests plus four
parametrized structural guards that now cover the new module.

**The one web failure is pre-existing and not caused by this change**, and that
was demonstrated rather than asserted:
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
requires at least one *collapsed untracked directory* in `git status
--porcelain=v1`. This tree has **zero**, because every untracked path in it is a
file inside an already-tracked directory. The two new files were temporarily
moved out of the tree, the count was re-measured as **0** and the test **still
failed**, after which both files were restored. The test's own message —
*"no untracked directory in this tree; this test proves nothing"* — is accurate;
it is a tree-shape dependency in the guard, not a finding about this change, and
it is **reported and not repaired**, being outside this authorization.

**The 326 bot and 1 362 web skips are `TEST_DATABASE_URL`-marked database tests.**
The assignment requires that variable unset, so **every database-marked
assertion in this pass is unverified and none of it is PostgreSQL evidence.** The
correct web skip count with the variable exported is 80; that run was not
performed and is not claimed. The single bot warning is
`DeprecationWarning: 'audioop' is deprecated`, raised by `discord/player.py`
inside the virtual environment; it is unrelated to this change.

**No formatter, linter or type checker is configured in this repository** —
there is no `pyproject.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `.pylintrc`.
That is an unconfigured check, **not a pass**.

### Review artifacts — regenerated through the non-executing route only

```bash
# twice into a scratch directory, then into the repository
python -m tools.phase_5_0_evidence.execution.cli --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
python -m tools.phase_5_0_evidence.execution.cli --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
                                                 --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`. The dry run
reported `executable : False`. Generations 1 and 2 were **byte-identical** to
each other and to the copies written into the repository; a third generation
after the last source edit reproduced both files exactly.

New digest: `2be8dae8b81256af01e5e1f9ac702ef256401ae62624c27a9396badefbb23101`
(previous in the tree: `5df172565b3b27fe769a87a56f9638e33f25c33c779178d62f0e35a15125d957`).
**This digest is review input only.** It is not an approval, it was not passed to
`--execute`, and `plan.is_executable` remains `False`.

**Two disclosures about that regeneration, because it carries more than this
pass's changes.** The committed manifest was **stale**: it was at
`manifest_version` 12 and did not cover `execution/provisioner.py` at all, so the
C-P5.0-LAB-V6-R1 pass that added the applier did not regenerate it. Regenerating
now necessarily folds in that pass's uncommitted work.

* **Attributable to this pass:** `manifest_version` 13 → 14, the new
  `execution/provisioning_cli.py` row, and the changed digest of
  `review_manifest.py`.
* **Attributable to the earlier, uncommitted C-P5.0-LAB-V6-R1 work, not to this
  pass:** `manifest_version` 12 → 13, the new `execution/provisioner.py` row, and
  the changed digests of `execution/descriptors.py`,
  `execution/lifecycle_record.py`, `execution/run_ledger.py`,
  `lifecycle_storage.py` and `provisioning.py`.

`MANIFEST_VERSION` moves to **14** for one reason and it is a change in what a
digest covers: the covered set grows by one file. The
supplied-observation schema stays at 3, the run-record schema at 3,
`plan.PERMITTED_EXECUTABLES` at 20, the verb table at 20, the delta at eleven
items, and `is_executable` stays `False` with C-7's three cases unresolved.

## 6. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/provisioning_cli.py` | **new.** The operator entry point. 398 lines, of which 107 are its docstring |
| `tests/phase_5_0_evidence/test_v6_provisioning_cli.py` | **new.** 60 operator-surface tests, 985 lines |
| `tools/phase_5_0_evidence/review_manifest.py` | `provisioning_cli.py` added to `COVERED_SOURCES`; `MANIFEST_VERSION` 13 → 14 with its dated rationale |
| `tests/phase_5_0_evidence/test_no_execution.py` | the new module declared in `EXECUTION_TIER_NAMES`, with the rationale each row carries |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | the manifest-version assertion follows to 14, with its dated comment |
| `tests/web/test_p3_4_static_assets.py` | the new module declared in `PERMITTED_PHASE_5_0_EVIDENCE_HARNESS` |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated (see the disclosures above) |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated — the digest line only |
| `docs/review/phase-5-0-reserved-laboratory-v6-p-r1-provisioning-entry-point-handback.md` | **new.** This document |

The three declarations are not incidental: the repository refuses an undeclared
module in three independent places, and each refusal was reached and answered
rather than routed around —
`test_no_execution.py::test_the_execution_tier_is_exactly_the_declared_modules`,
`test_concrete_plan.py::test_the_covered_sources_are_exactly_the_package` and
`test_p3_4_static_assets.py::test_every_evidence_harness_source_in_the_tree_is_declared`.

**Unrelated and reviewer-authored changes were preserved.** `git status` was
inspected first. The 16 files modified and the 16 untracked files belonging to
earlier passes are untouched except for the four test/manifest declarations
listed above and the two regenerated artifacts. No production module outside
`tools/phase_5_0_evidence/` was changed, no migration was added, no
configuration or deployment artifact was touched, and `.env.example` needs no
change: this program reads no environment value.

## 7. Security implications

* **It creates an armed path to a root-run mutation that did not exist before.**
  That is the point of the change and it is the thing to review hardest. The
  mitigations are the two-point arm, the closed-vocabulary rendering, the
  absence of any second input, and the fact that the mechanism being reached is
  already reviewed and is reused rather than reimplemented.
* **It adds no privilege and no way to obtain one.** No `sudo`, no `setuid`, no
  process, no shell, no environment read, no credential. The process must
  already be effective UID 0 and the reviewed provisioner refuses otherwise.
* **The operator surface cannot leak.** No raw exception, traceback,
  operating-system message, account-database record, directory listing,
  environment value or secret can reach it, and the unclassified path prints
  nothing about what it caught.
* **It cannot reach the executing runner.** Its import graph contains no
  `executor`, `materializer` or `cli`, so a provisioning invocation has no call
  path to an execution.
* **No secret is read, printed or committed.** The diff was reviewed for
  secrets, credentials, real paths outside the reviewed set, generated files and
  unsafe logging.
* **Rollback remains manual and guarded**, as reviewed. Nothing here performs a
  reversal, and an unidentified residue still refuses the whole guarded
  reversal.

## 8. Repository rollback

This pass is repository-local and reverses cleanly with no host or data effect.

1. `rm tools/phase_5_0_evidence/execution/provisioning_cli.py`
2. `rm tests/phase_5_0_evidence/test_v6_provisioning_cli.py`
3. `rm docs/review/phase-5-0-reserved-laboratory-v6-p-r1-provisioning-entry-point-handback.md`
4. `git checkout -- tools/phase_5_0_evidence/review_manifest.py tests/phase_5_0_evidence/test_no_execution.py tests/phase_5_0_evidence/test_r16_remediation.py tests/web/test_p3_4_static_assets.py docs/review/phase-5-0-evidence-harness-review-manifest.json docs/review/phase-5-0-evidence-harness-concrete-plan.md`

**Step 4 would also discard the earlier uncommitted work in those same files**,
which is why it is written as a whole-pass reversal and not as advice to run
casually. The four test/manifest files and the two artifacts each carry both
passes' changes. To reverse only this pass, remove the two new files, delete the
`provisioning_cli.py` row from `COVERED_SOURCES`, restore `MANIFEST_VERSION` to
13 and its assertion in `test_r16_remediation.py`, delete the
`provisioning_cli` rows from `EXECUTION_TIER_NAMES` and
`PERMITTED_PHASE_5_0_EVIDENCE_HARNESS`, and regenerate the two artifacts through
the same non-executing route.

Nothing was applied to any host, so **there is no operational rollback to
perform**.

## 9. Checks not run, and why

| Check | Why not |
|---|---|
| anything on `oracle-test` — SSH, synchronization, inspection, provisioning, verification | forbidden by the authorization and by the current banner in `docs/operations/disposable-test-server.md`. This is repository-local authority only |
| `--apply` against the production paths | not authorized, and this host is not the disposable target. The armed path was exercised **only** over temporary directories with an injected lookup |
| PostgreSQL-backed tests | `TEST_DATABASE_URL` is required to be unset and database access is forbidden. 326 bot and 1 362 web skips are unverified and are **not** PostgreSQL evidence |
| the web suite's correct 80-skip configuration | same reason. Not run, not claimed |
| formatter, linter, type checker | none is configured in this repository. Unconfigured, **not** passed |
| I3, I12, V6 closure, V8, V10 | unperformed and separately authorized; none is touched by this pass |
| LAB-V6-P2 (`guard-secrets.py` over-refusal) | explicitly out of scope for this pass. Reported by the previous handback and not repaired |

## 10. Assumptions and unresolved questions, stated as such

1. **`MANIFEST_VERSION` was moved to 14.** Precedent from versions 12 and 13 is
   that growing `COVERED_SOURCES` by one file moves the version. If Codex reads
   an entry point as an ordinary covered-source change rather than a set growth,
   the correct value is 13 and the assertion in `test_r16_remediation.py` follows
   it. This is a judgement, not a rule found in the documents.
2. **The regenerated artifacts carry the earlier pass's uncommitted changes.**
   §5 lists exactly which rows belong to which pass. Whether the stale
   version-12 manifest should have been regenerated by the C-P5.0-LAB-V6-R1 pass
   is a question for the reviewer, not something this pass could decide.
3. **Exit code `3` for a no-flag invocation** follows the assignment's rule that
   zero is returned only when all four items completed or were verified already
   compliant. A reviewer may prefer `0` for a purely informational invocation;
   the assignment's wording is why it is not.
4. **The detail shape rule is fail-closed.** A future reviewed detail written
   with a character outside `SAFE_DETAIL_PUNCTUATION` is withheld rather than
   shown — but the suite fails first, by design, so the choice reaches a person.
5. **The `--apply` path has never been executed against a real provisioned
   path**, by anyone. Every green figure above is evidence about the mechanism
   over temporary directories, and **none of it is evidence about `oracle-test`**.

## 11. Proposed reviewer focus areas

1. **The arm and its negative control.** Whether the two points are genuinely
   independent, and whether the syntax-tree mutation control is a fair test of
   the reversal it models.
2. **The rendering's safety argument**, especially the derived
   `SAFE_DETAIL_PUNCTUATION` set, the decision to check shape before applying the
   bound, and whether withholding a detail whole is the right failure direction.
3. **The catch-all `except Exception`.** It is there so that an unanticipated
   condition cannot put its text in front of an operator, and it costs the
   diagnosis. Whether that trade is right on a root-run path is a judgement a
   reviewer should make.
4. **The exit-code contract**, in particular `3` and `6`.
5. **The manifest version decision** and the disclosure in §5 about what the
   regeneration carries.
6. **The import graph**, as the authority argument — whether importing
   `.boundary` for `SystemIdentityLookup` is acceptable given that module also
   defines the process starter, or whether the identity lookup should live
   somewhere narrower.

---

## Status after this pass

Unchanged, and stated so nothing is read as advanced by a green suite.
**LAB-V6-P1 Open** pending Codex's review of this implementation; **LAB-V6-P2
deferred**; V6 **performed-but-not-closed**; **I3 unconfirmed**; V7 **excluded**;
V8, V10 and I12 **unperformed**; `plan.is_executable` **False**;
`reservation.REAL_EXECUTION_REFUSAL` **unconditional**; C-7, EH-R16-1, LAB-R6,
LAB-X1, P5.0-R5 and OD-62 **Open**; **Package 5.0 not ready**.

**Next action: independent Codex technical and security review of this
implementation.** A later operational retry requires Peter's separate release
after Codex accepts it. Claude closes no finding, approves no digest, applies no
provisioning and advances no gate, and stops here.
