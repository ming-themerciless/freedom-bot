# Handback — exact refusal-detail admission before normalization — 2026-09-18

**Authorization:** C-P5.0-LAB-V6-P-R3. Bounded, repository-local remediation of
the single Blocking finding Codex raised against C-P5.0-LAB-V6-P-R2. Claude
implemented; Claude closes no finding, approves no digest, applies no
provisioning and advances no gate.

**Status of the finding:** PR-20260918-LAB-V6P-R2-1 is remediated in the
repository and **returned for independent Codex technical and security
re-review**. It is not closed here.

This handback **supersedes**
[`phase-5-0-reserved-laboratory-v6-p-r2-provisioning-safe-output-handback.md`](phase-5-0-reserved-laboratory-v6-p-r2-provisioning-safe-output-handback.md)
as the current account of the entry point. That document's commands, figures and
results are left exactly as they were written; a superseding note has been added
at its head and nothing in it has been rewritten or removed. Its exact-membership
and whole-value claims about `_detail()` were false for the reason Codex gave,
and this document states what is true now.

---

## 1. The finding, reproduced before the fix

`tools/phase_5_0_evidence/execution/provisioning_cli.py::_detail()` collapsed
whitespace and then asked the applier's contract about the **collapsed** value:

```python
collapsed = " ".join(str(text).split())
if is_reviewed_refusal_detail(collapsed, item_ids):
    return _bounded(collapsed)
return WITHHELD_DETAIL
```

A value that was not a reviewed detail therefore became one on the way in. The
reproduction below was run before any edit, through the canonical interpreter,
with `TEST_DATABASE_URL` unset, on `DETAIL_BARRIER_FAILED` — the same constant
Codex used:

```
=== BEFORE FIX: bare detail ===
leading space          admitted=True
trailing space         admitted=True
doubled space          admitted=True
tab for space          admitted=True
newline for space      admitted=True
carriage return        admitted=True
=== BEFORE FIX: composed detail ===
leading space          admitted=True
trailing space         admitted=True
doubled space          admitted=True
tab                    admitted=True
newline                admitted=True
carriage return        admitted=True
```

`admitted=True` means the renderer emitted the reviewed fixed detail for input
that was not that detail. All twelve cases — six alteration classes across the
bare and the composed `classification: item_id — detail` forms — reproduced.
Codex's report is confirmed in full, including that the composed form carried
the same defect.

The positive regression
`test_every_reviewed_detail_survives_the_renderer_unchanged` masked this by
collapsing every provisioner detail before submitting it, so it asked the
renderer a question no refusal ever asks it.

## 2. The admission rule now in force

```python
if isinstance(text, str) and is_reviewed_refusal_detail(text, item_ids):
    return _bounded(text)
return WITHHELD_DETAIL
```

This is design 1 of the two the assignment offered — the expected small
correction. The rule, stated exactly:

* **The contract is asked about the value as supplied, character for
  character.** Nothing stands between the candidate and
  `is_reviewed_refusal_detail`: no trim, no split, no whitespace collapse, no
  case-folding, no Unicode normalization, no control-character removal and no
  truncation.
* **A bare or composed detail is emitted only when the complete supplied value
  is already one the provisioner's closed contract accepts.** A value one
  space, tab, newline or carriage return away from a reviewed detail is not
  that detail and is withheld **whole**, as the fixed `WITHHELD_DETAIL`
  sentence, with no fragment of the input surviving.
* **`_bounded()` remains, strictly after admission**, on a value the contract
  has already accepted. It is defence in depth and never participates in
  deciding that a candidate is safe.
* **A non-string is withheld rather than converted.** `str()` is itself a
  transformation and could render an arbitrary object's text. This also keeps
  the renderer total, which matters because `render_run` is called outside the
  handler that catches everything.

**The post-admission defence rewrites nothing that is admitted, so the
assignment's stop condition did not trigger.** This was checked rather than
assumed, across every bare detail the applier can produce (fixed constants, the
empty detail, and both discrepancy builders over the whole
`OBSERVATION_DISCREPANCIES` vocabulary including the empty and repeated lists)
and every composed value the real `apply()` path can record (each provisioning
classification × each supplied identifier × each bare detail): **0 values
altered by `_bounded()`**, widest composed value **466** characters against
`FIELD_WIDTH = 600`. `test_the_bound_alters_no_admitted_value` now asserts this
continuously, so a detail added later that the bound *would* rewrite fails the
suite instead of silently weakening the exact contract.

## 3. Regression mapping

`tests/phase_5_0_evidence/test_v6_provisioning_cli.py`, **86 → 114 tests**
(1 299 → 1 647 lines). New section **8a**, plus one correction in section 8.

| Assignment requirement | Test |
|---|---|
| every actual bare detail submitted and rendered unchanged | `test_every_bare_detail_the_applier_produces_is_submitted_and_rendered_unchanged` |
| every actual composed detail submitted and rendered unchanged | `test_every_composed_detail_the_apply_path_records_is_rendered_unchanged` |
| …and produced by the real `apply()` path, not composed by the suite | `test_a_real_refusal_from_apply_renders_its_detail_unchanged` |
| six alteration classes withheld — bare | `test_a_whitespace_altered_bare_detail_is_withheld_whole` (6 parametrizations) |
| six alteration classes withheld — composed | `test_a_whitespace_altered_composed_detail_is_withheld_whole` (6 parametrizations) |
| withheld **whole**, no fragment recoverable | `test_the_admitted_reviewed_detail_is_not_recoverable_from_a_withheld_one` |
| Unicode whitespace `str.split()` also collapsed (beyond the six named classes) | `test_unicode_whitespace_cannot_normalize_into_a_reviewed_detail` (7 parametrizations) |
| no pre-admission transformation can be reintroduced | `test_no_normalization_stands_between_a_candidate_and_the_contract` (structural) and `test_the_admission_is_asked_about_the_argument_itself` (behavioral) |
| bound alters no admitted value | `test_the_bound_alters_no_admitted_value` |
| the two finite discrepancy details admit exactly the builders' output | `test_the_finite_discrepancy_details_admit_only_what_the_builders_produce` |
| `str()` is a transformation too | `test_a_non_string_detail_is_withheld_rather_than_converted` |
| the masking regression corrected | `test_every_reviewed_detail_survives_the_renderer_unchanged` — now submits the applier's actual values with no pre-normalization, and builds the composed form with the real `ProvisioningRefused` type |

**The requirement was not satisfied by a source-text assertion.** Every row
above except the structural guard exercises the public renderer. The structural
guard is retained as the second line of evidence the assignment asks for: it
walks `_detail`'s body in the syntax tree and fails if any call other than
`isinstance`, `is_reviewed_refusal_detail` and `_bounded` appears, if a
subscript (a truncation) appears, or if the bound is reached before the
contract.

**The new regressions are not vacuous.** Temporarily restoring the defective
`_detail()` body and re-running the file produced **24 failed, 90 passed** —
every new assertion that should detect the finding does. Restoring the fix
returned **114 passed**. The three positive-half tests pass under both, which is
correct: they prove the admitted vocabulary is still reachable.

## 4. Preserved behavior

R1/R2 accepted behavior is intact and re-proved by the unchanged remainder of
the two suites (114 + 131 tests):

* no filesystem or account-database read and no mutation without `--apply`;
* `--apply` remains the only arm, including the single-point reversal guard;
* `SystemIdentityLookup`, the real `DirectoryProvisioner` and the no-argument
  production `directory_targets()` path retain their authority;
* V12, V4, V9, V5 remain the only items, in their reviewed order;
* complete applied, residue, refusal and not-attempted accounting remains;
* exit zero remains possible only for a complete four-item run;
* the R2 closed contracts for fixed details, finite discrepancy-list variation,
  composed `ItemRefusal` details, classifications, supplied item identifiers and
  paths, and recorded object identities are unchanged;
* hostile values, arbitrary alphanumeric prose, classification-only values,
  smuggled composed details, long values, Unicode/control input, paths,
  traceback text, OS messages and account-record-shaped text remain withheld or
  bounded as before; and
* no alternate input or environment arm, subprocess, `sudo`, repair, automatic
  rollback, lifecycle initialization, participant or evidence-harness execution
  path was added.

`_admitted()` and `_identity()` were **not** changed: both already decided
membership on the original value and applied the bound only afterwards.

The former Important finding **PR-20260918-LAB-V6P-R1-2** is preserved: all
Python evidence below uses `/opt/freedom-blades/runtime/venv-web/bin/python` and
the two pytest configuration warnings are reported. Neither historical
`/opt/discord-bots/` interpreter was used.

## 5. Canonical test evidence

Run locally, serially, with `TEST_DATABASE_URL` **unset**, using only
`/opt/freedom-blades/runtime/venv-web/bin/python`, against the tree being
submitted.

```bash
cd /opt/freedom-blades/platform
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning_cli.py
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning.py
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py tests/phase_5_0_evidence/test_concrete_plan.py
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/web/test_p3_4_static_assets.py
python3 .claude/hooks/test_guards.py
/opt/freedom-blades/runtime/venv-web/bin/python -m compileall -q tools/phase_5_0_evidence/execution/provisioning_cli.py tests/phase_5_0_evidence/test_v6_provisioning_cli.py
git diff --check
```

| Suite | Passed | Failed | Skipped | Warnings |
|---|---|---|---|---|
| `test_v6_provisioning_cli.py` (focused) | **114** | 0 | 0 | 2 |
| `test_v6_provisioning.py` (complete V6 applier) | **131** | 0 | 0 | 2 |
| `tests/phase_5_0_evidence` (full) | **2 492** | 0 | 0 | 2 |
| `test_no_execution.py` + `test_concrete_plan.py` | **320** | 0 | 0 | 2 |
| `tests/web/test_p3_4_static_assets.py` | 110 | **1** | 0 | 2 |

`.claude/hooks/test_guards.py`: 31 cases — 19 refused, 12 allowed — all passed.
`compileall`: exit 0. `git diff --check`: clean, exit 0.

**The two warnings are the canonical pytest configuration warnings** and they
remain: `PytestConfigWarning: Unknown config option: asyncio_default_fixture_loop_scope`
and `PytestConfigWarning: Unknown config option: asyncio_mode`. They are a
configuration fact of the repository, not a product of this change.

**The one failure is the known static-assets tree-shape failure, reported
honestly and not repaired or hidden.**
`test_the_discovery_enumerates_untracked_files_rather_than_directories` fails at
`tests/web/test_p3_4_static_assets.py:1196` on
`assert collapsed, "no untracked directory in this tree; this test proves nothing"`.
It requires an untracked **directory** to exist so that `git status --porcelain`
collapses it. Every untracked entry in this tree is an individual file. **This
remediation does not change that premise**: it created no new path at all, and
edited two files that were already untracked before this pass. It is outside
this authorization to repair and was left alone.

**No database evidence is claimed.** `TEST_DATABASE_URL` was unset for every
command above and no database was contacted. The zero skip counts are the
correct figures for these suites, which carry no database-marked tests; they are
not a claim that database-marked tests ran.

**No formatter, linter or type checker is configured** in this repository — no
`pyproject.toml`, `setup.cfg`, `.flake8`, `mypy.ini` or `.pylintrc`. That is an
**unconfigured check, not a pass**.

## 6. Review artifacts — regenerated through the non-executing route only

`execution/provisioning_cli.py` is a covered source, so the manifest and
concrete plan were regenerated. Generated twice into scratch, established
byte-for-byte identical, written into the repository, then verified by a third
generation:

```bash
python -m tools.phase_5_0_evidence.execution.cli --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
python -m tools.phase_5_0_evidence.execution.cli --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
                                                 --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`. The dry run
reported `executable : False`. Generations 1 and 2 were byte-identical to each
other and to the copies written into the repository, and a third generation
taken after the last edit reproduced both files exactly.

New digest:
`593a734954eb650a6f0080776f88023ecb806d31b3407d7a0e52acd2fc0d2db2`
(R2's, which it replaces:
`abd643732c23bda0179c1cc1cc97010c7e10594a16a5b8c10d82104c62e9b0bd`).

**This digest is review input only.** It is not an approval, it was not passed
to `--execute`, and `plan.is_executable` remains `False`.

**`MANIFEST_VERSION` stays at 14.** The covered set is unchanged — the same 45
files — and this pass changed the contents of exactly one of them,
`execution/provisioning_cli.py`. A changed covered file changes its digest and
nothing else; the manifest schema, the supplied-observation schema (3), the
run-record schema (3), `plan.PERMITTED_EXECUTABLES` (20), the verb table (20),
the eleven-item delta and `is_executable = False` are all unmoved.

**R1's and R2's disclosure stands and is repeated here, because it still
applies.** A diff of the manifest against `HEAD` folds in earlier uncommitted
work and does not describe this pass. Against `HEAD` it shows
`manifest_version` 12 → 14, two added rows and six changed digests; **only the
`execution/provisioning_cli.py` row digest and the overall digest are
attributable to this pass.** Everything else belongs to the uncommitted
C-P5.0-LAB-V6-R1, V6-P-R1 and V6-P-R2 work already present in the tree.

## 7. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/provisioning_cli.py` | `_detail()` admits the supplied value before any transformation; its docstring and two module-docstring bullets state the exact rule and cite the finding. 470 → 495 lines |
| `tests/phase_5_0_evidence/test_v6_provisioning_cli.py` | section 8a added; the masking regression in section 8 corrected; one stale comment in the control-character test updated. 86 → 114 tests, 1 299 → 1 647 lines |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated (see the disclosure above) |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated — the digest line only |
| `docs/review/phase-5-0-reserved-laboratory-v6-p-r2-...-handback.md` | superseding note added at the head; its commands and results untouched |
| `docs/review/phase-5-0-reserved-laboratory-v6-p-r3-exact-detail-admission-handback.md` | this document (new) |

No production module outside `execution/provisioning_cli.py` was touched. No
migration was added. `reservation.py` and `plan.py` were not modified. Every
unrelated, earlier-pass and reviewer-authored change in the working tree was
preserved; no project state, status, RAID, decision or change register was
updated, as the assignment directs.

## 8. Security implications

**The change closes an operator-surface disclosure path and opens none.**

* Before, an unreviewed value that normalized onto a reviewed detail was printed
  as that detail. The operator-facing meaning of the surface was therefore
  attacker-influenceable in a narrow way: text arriving at the renderer decided
  which reviewed sentence an operator read.
* After, the emitted text for any unreviewed value is the fixed
  `WITHHELD_DETAIL` constant, whatever whitespace it carries.
* **The admitted set did not grow.** It is unchanged and is still exactly what
  `provisioner.is_reviewed_refusal_detail` accepts. This pass makes the
  admission *narrower*, never wider.
* **The withheld set grew** by the whitespace-altered neighbourhood of every
  reviewed detail. Nothing previously withheld is now printed.
* Raw exception text, operating-system messages, tracebacks, account-database
  records, directory listings, environment values, paths and secrets remain
  absent from every output path.
* No authorization, arming, identity or filesystem behavior was touched. The
  entry point still applies nothing without `--apply` and still requires
  effective UID 0 inside the reviewed provisioner.

## 9. Repository rollback

This pass is repository-local and reverses cleanly:

```bash
cd /opt/freedom-blades/platform
git checkout -- docs/review/phase-5-0-evidence-harness-review-manifest.json \
                docs/review/phase-5-0-evidence-harness-concrete-plan.md \
                docs/review/phase-5-0-reserved-laboratory-v6-p-r2-provisioning-safe-output-handback.md
rm docs/review/phase-5-0-reserved-laboratory-v6-p-r3-exact-detail-admission-handback.md
```

`git checkout` restores the **committed** manifest and concrete plan, which are
older than R1 and R2. Restoring the R2 state instead means re-running the
regeneration route above after reverting `_detail()`. The two untracked files
this pass edited — `execution/provisioning_cli.py` and
`test_v6_provisioning_cli.py` — are not restorable by Git; reverting the
behavior means restoring the collapsing `_detail()` body quoted in §1, which
**reintroduces PR-20260918-LAB-V6P-R2-1** and is not recommended.

No host, service, database, account or file outside this repository was changed,
so there is nothing operational to roll back.

## 10. Restrictions honoured, and the stop point

**Nothing on `oracle-test` was touched, and nothing was synchronized to it.** No
SSH, no inspection of that host, no `sudo`, no account, group or membership
created or modified, no edit to `/etc`, no `systemd-tmpfiles`, and nothing
created, adopted, repaired or removed under real `/run`, `/var/lib` or
`/opt/freedom-blades`.

V7 was not initialized. I3, V8, V10 and I12 were not performed. No database was
accessed. No real boundary or materializer was invoked, no generated vector was
executed, no participant was invoked, and `--execute` was not used.
`plan.is_executable` remains **false** and
`reservation.REAL_EXECUTION_REFUSAL` remains unconditional. LAB-V6-P2 and the
web tree-shape guard were not repaired.

**Unchanged state:** LAB-V6-P1 remains Open. V6 remains
performed-but-not-closed. I3 unconfirmed. V7 excluded. V8, V10 and I12
unperformed. Package 5.0 remains **not ready**.

**Stop point.** This returns for **independent Codex technical and security
re-review** of PR-20260918-LAB-V6P-R2-1 before the provisioning entry point is
used on `oracle-test`. Claude closes no finding, approves no digest, applies no
provisioning and advances no gate.

### Proposed reviewer focus

1. That `_detail()` performs no transformation before
   `is_reviewed_refusal_detail`, and that `isinstance` narrowing is acceptable
   as the non-string guard rather than a transformation.
2. That the six named alteration classes plus the seven Unicode whitespace
   classes are the right closure, and whether a form Codex can construct
   escapes them.
3. That `test_the_bound_alters_no_admitted_value` is the correct mechanization
   of the assignment's stop condition.
4. That the composed-detail enumeration faithfully represents what `apply()`
   can record.

---

*Independent technical and security review required. This document approves
nothing.*
