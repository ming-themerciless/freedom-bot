# Claude handback — canonical `R` `0700` and P2 temporary `0500` reconciled — 2026-09-20

**C-P5.0-LAB-I3-R3 is implemented in the repository and returned for fresh
independent Codex technical and security review. No host action was taken.**

This pass implements the two rulings in
[`project-review-2026-09-20-reserved-laboratory-i3-r2-acceptance-and-discrepancy-ruling.md`](project-review-2026-09-20-reserved-laboratory-i3-r2-acceptance-and-discrepancy-ruling.md)
and nothing else. It closes no finding, confirms no target fact and approves no
digest.

## What the two rulings required, and what changed

### Ruling 1 — canonical `R` is created `root:root 0700`

`R`'s mode has one definition: the mode the reviewed case program's `mkroot`
verb gives `mkdir(2)` and re-applies with `fchmod(2)` on the descriptor of the
directory it just created.

| Where | Before | After |
|---|---|---|
| `execution/case_program.py` `ROOT_DIRECTORY_MODE` | `0o755` | **`0o700`** |
| `concrete_plan.py` `_create_disposable_root` docstring | `0755` | **`0700`**, with the ruling's reason |
| `concrete_plan.py` `B3-02` compared expectation | `_stat_mode("0755")` → `755` | **`_stat_mode("0700")` → `700`** |
| `concrete_plan.py` `B3-02` `expected_result` | `mode 755` | **`mode 700`** |

`R/bin` is a **separate item and deliberately unchanged at `0755`**, as are
V12's `/var/lib/freedom-blades` `0755` and every other provisioning mode. The
verifier's `CANONICAL_ROOT_MODE` was already `0o700` and needed no change; it is
now asserted equal to `case_program.ROOT_DIRECTORY_MODE` so the two cannot drift.

### Ruling 2 — P2 alone creates its temporary `0500`

The reviewed exclusive-file creation abstraction gained the minimum explicit
input, and its default did not move.

| Where | Change |
|---|---|
| `descriptors.PosixFilesystem.create_file` | new **keyword-only** `mode: int = EXCLUSIVE_CREATION_MODE`; the value is passed to the existing `os.open`, and nothing else in the call changed |
| `descriptors.EXCLUSIVE_CREATION_MODE` | **unchanged at `0o600`**; its comment now says it is the default and that P2's `0500` is passed at P2's call |
| `case_runtime.CASE_PROGRAM_TEMPORARY_MODE` | **new**, `"0500"`, stated beside `CASE_PROGRAM_MODE` so the creation mode and the published mode have one source each |
| `executor.install_case_program` | new `creation_mode` parameter defaulting to `CASE_PROGRAM_TEMPORARY_MODE`, passed to `create_file`. **This is P2's real case-program installation path.** |
| `i3_verifier._ContextPlan` | new `creation_mode` field; P2's context sets it to `0500`, T1, §2.3.3 and T6 set it to `EXCLUSIVE_CREATION_MODE` |
| `durability_model` model filesystem | same keyword-only parameter, so the model and the real filesystem stay substitutable. The model does not enforce permission bits and does not begin to |

**The creation mode never becomes the published mode.** In both P2 paths the
already-open writable descriptor remains the authority: the payload is written
to it, synchronized on it, and `fchown`ed and `fchmod`ed on it. The reviewed
order was preserved exactly in each path and neither was re-sequenced —
`O_CREAT|O_EXCL`, `O_NOFOLLOW`, descriptor-relative creation, complete
descriptor write, data barrier, descriptor ownership/mode application, exclusive
`linkat`, temporary unlink, containing-directory barrier.

### Every caller of the abstraction, traced before the signature changed

| Caller | Context | Creation mode |
|---|---|---|
| `lifecycle_storage.py:1849` | T1, the first-use record | default `0600` |
| `execution/recovery_store.py:854` | §2.3.3, the capture publication | default `0600` |
| `execution/executor.py:2400` `create_object` | reviewed file creation | default `0600` |
| `execution/materializer.py:483` | restoration temporary | default `0600` |
| `durability_model.py` ×4 | model callers | default `0600` |
| `execution/i3_verifier.py:1575` | the four verifier contexts | `plan.creation_mode` — `0600`, except P2 |
| **`execution/executor.py:2458`** | **P2, the real installation** | **`0500`** |

No caller had to give up its `0600` behavior, so the stop condition in the
assignment was not reached.

## Contract, artifacts and manifest

* **r6** gains the C-P5.0-LAB-I3-R3 decision banner; §7.4.3's table gains a
  **creation-mode column** beside the pre-`linkat` mode, with the paragraph
  stating that only P2 distinguishes the two and that a `0500` on a *published*
  name is a mismatch; §7.4.4 step 1 names the per-context creation mode; §9.2
  gains rows **106** and **107**. §1.4.1's C1 row (`0700`) and §6.2's P2 row
  (`0500`) already carried the ruled values and were not edited — the
  discrepancy was always the implementation disagreeing with them.
* **`review_manifest.MANIFEST_VERSION` moves 15 → 16**, with the reason recorded
  in the same form as earlier versions. The covered file set does not change.
* The two generated artifacts were regenerated through the repository-owned
  deterministic path. **No generated value was hand-edited.**

## Evidence

All commands were run in `/opt/freedom-blades/platform` with
`TEST_DATABASE_URL` **unset**, using
`/opt/freedom-blades/runtime/venv-web/bin/python` (Python 3.12.3, pytest 9.1.1),
which was verified present on this host before use.

### Tests

```bash
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
```

**2642 passed, 0 failed, 0 skipped**, run serially — 2637 before this pass plus
**5 new tests**. The focused selections were run first and also pass:
`test_i3_verifier.py -k "0700 or 0500 or 0600 or before_linkat"` → 4 passed;
`test_lab_implementation.py -k "0500 or payload"` → 5 passed.

The five new regression tests prove the four required distinctions:

| Test | Distinction |
|---|---|
| `test_i3_verifier.py::test_mkroot_creates_canonical_r_as_0700_not_0755` | `mkroot` uses `0700`; `B3-02` compares `700`; `R/bin` still `0755` |
| `test_i3_verifier.py::test_p2_alone_creates_its_temporary_0500` | P2's temporary is `0500`, and **exactly one** exclusive file creation in the root invocation is |
| `test_i3_verifier.py::test_t1_capture_and_t6_keep_the_shared_0600_default` | root invocation creations are exactly `0500, 0600, 0600`; the `ubuntu` invocation's is `0600`; the parameter default is `0600` |
| `test_i3_verifier.py::test_p2_is_root_root_0555_on_the_descriptor_before_linkat` | `fchown` then `fchmod 0555` precede P2's `linkat`; every mode observed **at a link** is a final mode and never `0500` |
| `test_lab_implementation.py::test_p2_creates_its_temporary_0500_and_publishes_0555` | the same on P2's **real** installation path: one `0500` creation, a `0555` published file |

Each observes the real `os.open`, `os.fchmod`, `os.fchown` and `os.link` calls
rather than re-reading a constant, so a change that moved a mode without moving
the syscall would fail them.

### Other checks

| Check | Command | Result |
|---|---|---|
| Guards | `python3 .claude/hooks/test_guards.py` | **41/41** — 27 refused, 14 allowed |
| Byte-compile | `compileall tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| Whitespace | `git diff --check` | clean |

### Deterministic regeneration

```bash
/opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.cli \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

A dry run: it printed the plan, `executable: False`, and started nothing. It was
then generated a second time into a scratch directory and compared byte for
byte: **identical**.

| Artifact | SHA-256 |
|---|---|
| `…-concrete-plan.md` | `122f0b9a4eddebfa5a998a376adbc51da3ec9d7fb066a1c8c3709b00b2d31720` |
| `…-review-manifest.json` | `65ef078d99273c52f64cd707021e9479d43c80bfcc58f419070c3e08f8f25239` |

Resulting **review-input digest**:
`be9e110f9cc8828ba79aaeec7342fd23182dad54eb261852d68654bf8332762b`.

**This digest is neither approval nor authority for `--execute`.** It is review
input only. `plan.is_executable` remains `False` and was not touched.

### Required searches

* **No operative source creates canonical `R` as `0755`.** `ROOT_DIRECTORY_MODE`
  is `0o700` at its one definition and its two uses; the only remaining `0755`
  strings in the package are `R/bin`, V12's `/var/lib/freedom-blades`, the
  observed `1001:1001 0755` parent in the withdrawn-V11 reasoning, and dated
  comments recording what the value used to be.
* **No P2 temporary uses `0600`.** Both P2 paths pass
  `CASE_PROGRAM_TEMPORARY_MODE`.
* **The other three publication contexts still use `0600`.** They pass no mode
  and take the unchanged default, asserted directly by the new tests.

### Scoped diff review

The diff is confined to the two rulings: nine source files, two test files, r6,
the two regenerated artifacts and the registers. No secret, credential or `.env`
path is read, added or printed; no new output vocabulary, exit status, payload
byte, nonce grammar, identity, capability, directory topology, cleanup semantic
or descriptor-custody rule changed. `plan.is_executable=False` is unchanged and
asserted by `test_the_standing_gates_are_unchanged`.

## Checks not run, and what this evidence does not establish

* **Nothing was run on `oracle-test`.** No SSH, synchronization, inspection,
  creation under `/var/lib`, capability change, controlled write or verifier
  invocation. The restriction banner forbids all of it and it was obeyed.
* **The web and bot suites were not run.** This pass touches neither, and the
  restriction keeps `TEST_DATABASE_URL` unset, under which every
  database-marked test would skip while still exiting 0. Those suites are
  therefore unverified for this tree, and no figure is offered for them.
* **A local green suite does not confirm target-host behavior.** Every
  publication in these tests succeeded on whichever kernel and filesystem ran
  them. It says nothing about `oracle-test`'s filesystems or its hard-link
  policy.
* **I3 is not confirmed by anything here.** The verifier was not invoked
  operationally.

## Two observations for the reviewer, changed by nothing in this pass

1. **The committed artifacts at `HEAD` were stale before this pass.** `HEAD`'s
   `…-review-manifest.json` carries `manifest_version` **12** and a `P-04`
   expectation of `0755`, predating even the C-P5.0-LAB-I3-R2 `0555` ruling.
   The R2 regeneration existed only as an uncommitted working-tree change, which
   this pass's regeneration has now replaced. Both artifacts are wholly derived
   from source through the deterministic path above, so nothing is lost; the
   point is only that a reviewer diffing against `HEAD` will see two rulings'
   worth of change, not one.
2. **`docs/project-management/change-log.md` had a malformed table.** The
   `C-P5.0-LAB-I3-R2-A` row sat *above* the header separator, so the table did
   not render. Adding this pass's row required the separator to be in the right
   place, so it was moved; no existing row's text was altered. Flagged because
   it is a correction this pass did not set out to make.

## State — unchanged by this pass

I3 remains **unconfirmed**. V7 remains **excluded**. V8 and V10 remain
**unperformed**. `plan.is_executable=False`. `reservation.REAL_EXECUTION_REFUSAL`
remains unconditional. Package 5.0 remains **not ready**.

No gate is closed and no finding is closed on the implementer's authority. This
returns for fresh independent Codex technical and security review.

## Proposed reviewer focus

1. That `create_file`'s new parameter is the **minimum** input the ruling needs,
   that keyword-only is right, and that no caller's `0600` behavior moved.
2. That `0500` is reachable from P2's two paths and from nowhere else.
3. That the reviewed publication order is byte-for-byte the prior order in both
   P2 paths, with only the creation mode added.
4. That r6 §7.4.3's new column and §9.2's rows 106–107 describe what the code
   does, and that §1.4.1 C1 and §6.2's P2 row remain the normative statements.
5. That the manifest-version 16 rationale is complete and the regeneration is
   reproducible from this tree.
