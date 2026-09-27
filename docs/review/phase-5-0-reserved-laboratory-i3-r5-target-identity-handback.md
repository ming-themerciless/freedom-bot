# Claude implementation handback — C-P5.0-LAB-I3-R5, target identity Option A — 2026-09-20

Author: Claude (implementing agent, working Technical Lead for this pass).
Authorization: **C-P5.0-LAB-I3-R5**, one bounded repository-only pass.
Returned for **independent Codex technical and security review**.

**Nothing in this handback closes a review finding, approves a digest, confirms
I3, advances a gate or authorizes an operational retry.**

## 0. State, unchanged by this pass

I3 remains **unconfirmed and unperformed**. V7 remains **excluded**. V8 and V10
remain **unperformed**. `plan.is_executable` remains **`False`**. Package 5.0
remains **not ready**. LAB-SECRETS-1 stays Open, Low; LAB-V6-P2 stays deferred.

**No host action occurred.** No SSH, no synchronization, no inspection, no
deletion of `/tmp/fb-i3-root.out` or `/tmp/fb-i3-root.err`, no creation under
`/var/lib`, no capability change, no controlled write, no verifier invocation,
no V7, no participant wiring, no evidence-harness invocation, no generated-vector
execution, no database operation, no real boundary or materializer, and no
`--execute`. The restriction banner forbids all of it and it was obeyed. The two
`/tmp` evidence artifacts remain in place, untouched.

## 1. What was implemented

Option A exactly, as Peter decided for LAB-I3-TARGET-1 on 2026-09-20: the SSH
alias and the kernel nodename are two approved facts about two different layers,
and neither is substituted for the other.

### 1.1 The new canonical fact

`ApprovedTargetFacts` gains one field, `kernel_nodename`, value **`Test`**,
placed and ordered **immediately after `host`** — in the dataclass, in
`as_fields()` and therefore in the canonical identity material, the manifest and
the rendered plan. Ordering is fixed by the `as_fields()` tuple, not by a
mapping, exactly as every other fact already was.

`host` is untouched at `oracle-test`, on both `APPROVED_TARGET` and
`APPROVED_TARGET_FACTS`. No host was renamed, no alias changed, and `host` was
not redefined to mean a nodename.

The field carries its own provenance in the source: the other fifteen facts were
named or verified on 2026-09-05, and this one was approved on 2026-09-20 after
the R4 refusal. The class docstring states the distinction rather than leaving a
reader to infer it.

### 1.2 The admission change

`i3_verifier._admit` step 2 compares the observed `uname(2)` tuple with

```
(APPROVED_TARGET_FACTS.kernel_nodename,
 APPROVED_TARGET_FACTS.active_kernel,
 APPROVED_TARGET_FACTS.architecture)
```

in that order, replacing `.host` in the first position only. Kernel release and
architecture keep comparing their own separately approved facts, unchanged.

**Nothing else in admission moved.** The refusal code is still
`target-mismatch`, `target-unobservable` still covers a probe that raises, the
comparison is still a single tuple equality decided **before the first write**,
the ordering of the eleven admission steps is unchanged, and no refusal code,
exit status, output vocabulary, payload byte, nonce grammar, identity,
capability, directory topology, cleanup semantic or descriptor-custody rule
changed. No admission check was weakened: the change makes admission *stricter*
in the sense that matters — the value that previously would have passed
(`oracle-test`) is now refused, and the value the approved target actually
reports is the only one accepted.

### 1.3 Comments and documentation corrected

Three places implied the SSH alias was observable through `os.uname()`:

* `i3_verifier`'s module docstring ("The host is the approved target's host,
  kernel release and architecture") — now names the kernel nodename and states
  that the alias is not observable locally;
* `HostProbe.host()`'s docstring — now says the first element is the kernel
  nodename and what it is compared with;
* the inline comment at the comparison site — now records why the alias is
  deliberately not compared, and cites the R4 refusal and Peter's decision.

`approved_target`'s module docstring gained a paragraph stating the two-fact
model. The `HostProbe.host()` **method name** was deliberately *not* changed:
renaming it would touch the protocol, the production probe, the test double and
every call site for no behavioral gain, which is outside this pass's scope. Its
docstring now removes the ambiguity. **Flagged for the reviewer** as a judgement
call rather than an omission — see §7.

## 2. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/approved_target.py` | new `kernel_nodename` field, value, ordering and documentation |
| `tools/phase_5_0_evidence/execution/i3_verifier.py` | admission step 2 compares the nodename fact; three docstring/comment corrections |
| `tools/phase_5_0_evidence/review_manifest.py` | `MANIFEST_VERSION` 16 → 17 with its rationale |
| `tests/phase_5_0_evidence/test_approved_target.py` | fact-set assertion updated; two new tests |
| `tests/phase_5_0_evidence/test_i3_verifier.py` | probe default and target parametrization updated; two new tests |
| `tests/phase_5_0_evidence/test_concrete_plan.py` | manifest identity-fact assertions |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | manifest-version assertion 16 → 17 with rationale |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | §7.4.2 step 2 corrected; dated amendment header |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | **regenerated**, not hand-edited |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | **regenerated**, not hand-edited |
| `docs/review/Handover information` | new handback entry |
| `docs/operations/disposable-test-server.md` | new restriction banner |
| `docs/implementation-plan.md` | §20 action pointer |
| `docs/project-management/{status,raid-register,decision-register,change-log}.md` | registers |

No migration was added; this pass touches no schema, no database and no
persistent state.

## 3. Old and new identity relationships

| Value | Before | After |
|---|---|---|
| `APPROVED_TARGET.host` | `oracle-test` | **unchanged** `oracle-test` |
| `APPROVED_TARGET_FACTS.host` | `oracle-test` | **unchanged** `oracle-test` |
| `APPROVED_TARGET_FACTS.kernel_nodename` | *did not exist* | `Test` |
| approved facts | 15 | 16 |
| `TARGET_IDENTITY_DIGEST` | `ceb58ad1f9f0e07057ae9d292096a2f88910d5986a50507df8f7a7c14a149403` | `fc2a9c9b9d581cc79c7f9bff15712ce4d2e958123c0f8b9d1a6fc2bc2b1308ff` |
| `CONFIRMATION_TOKEN` | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#ceb58ad1f9f0e070` | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#fc2a9c9b9d581cc7` |
| `MANIFEST_VERSION` | 16 | **17** |
| review-input digest | `be9e110f9cc8828ba79aaeec7342fd23182dad54eb261852d68654bf8332762b` | `c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26` |

The token's **prefix is unchanged** — it names the operational alias, root and
database, which this decision kept — and only its digest suffix moves.

The "before" identity digest was recomputed from the current tree by removing the
nodename from the identity material, **not** by checking out or stashing the
prior tree; it reproduces the pre-change construction exactly.

**`be9e110f…` must not be carried forward.** It describes the
manifest-version-16 tree whose admission could not admit the approved target.
`c358ea8b…` is **review input only**: it is not approval, not authority for
`--execute`, and not an I3 confirmation. `plan.is_executable` is `False` and was
not touched.

### 3.1 Manifest version — why it moves

The rule is that the version moves when a digest approved under the old one
would cover a *different plan* rather than a differently rendered one. It moves
here, and the reasoning is recorded in `review_manifest.py` beside versions 2–16:

A version-16 digest covered a plan whose I3 admission compared a kernel nodename
with an SSH alias. That is not a cosmetic difference — it is a comparison **the
approved target cannot satisfy**, and it is exactly what refused the
C-P5.0-LAB-I3-R4 pass with `target-mismatch` before its first controlled write.
The reconciled plan admits a target the old one refused. Reinterpreting the old
digest as covering this one would silently re-approve a changed admission rule,
so it stops matching instead.

What does **not** move at 17: the covered source set (still the version-15
files — no file was added or removed), the supplied-observation schema (3), the
run-record schema (3), `plan.PERMITTED_EXECUTABLES` (20), the verb table (20),
the provisioning delta (eleven items), every mode ruled at versions 15 and 16,
and `is_executable` (`False`, C-7's three cases still unresolved).

## 4. Tests

Seven tests were added and two existing assertions updated. Every required
distinction from the prompt is covered by a named test.

| Required proof | Test |
|---|---|
| `("Test", "7.0.0-31-generic", "x86_64")` passes target identity | `test_i3_verifier.py::test_the_approved_nodename_passes_the_target_portion_of_admission` |
| `oracle-test` as nodename refuses `target-mismatch` | same test, second half; and `…::test_only_the_approved_target_is_admitted[ssh-alias-as-nodename]` |
| wrong nodename / release / architecture fail closed | `…::test_only_the_approved_target_is_admitted` — ids `other-nodename`, `nodename-case`, `nodename-empty`, `kernel`, `architecture`, `unobservable` |
| `host` stays `oracle-test`, nodename separately `Test` | `test_approved_target.py::test_the_ssh_alias_and_the_kernel_nodename_are_two_separate_facts` |
| nodename in digest, token and manifest identity facts | `test_approved_target.py::test_the_kernel_nodename_is_part_of_the_canonical_identity_material`; `test_concrete_plan.py` manifest assertions |
| admission is bound to the nodename fact, not the alias | `test_i3_verifier.py::test_admission_reads_the_nodename_fact_and_never_the_ssh_alias` |

Two points on their strength, since a weak version of each would pass anyway:

* The **alias case is asserted as a refusal**, not merely as "not the approved
  tuple". Before this pass `oracle-test` was the value that *passed*. It is now
  the first row of the parametrization, so the specific defect this decision
  resolves has a regression test of its own and cannot return silently.
* `test_admission_reads_the_nodename_fact_and_never_the_ssh_alias` moves each
  fact and observes what admission does. Moving `kernel_nodename` moves what is
  admitted; moving `host` changes nothing here. A verifier that had been left
  comparing `host` would pass the first assertion and fail the others — which a
  test that only compared the approved tuple against itself would not catch.

The first parametrized case's docstring records *why* `oracle-test` must refuse,
so a future reader does not "fix" it back.

`FakeProbe`'s default host moved from `("oracle-test", …)` to `("Test", …)`, so
every other I3 test continues to reach the checks it is about. This is a test
double aligning with the approved facts, not a relaxation: the target-identity
assertions are made explicitly by the tests above, against the module's values.

## 5. Verification — exact commands and results

All repository-local, with `TEST_DATABASE_URL` explicitly unset.

| Check | Command | Result |
|---|---|---|
| Focused | `python -m pytest -q tests/phase_5_0_evidence/test_i3_verifier.py tests/phase_5_0_evidence/test_approved_target.py` | **163 passed** |
| Full package suite | `python -m pytest -q -rs tests/phase_5_0_evidence` | **2649 passed, 0 skipped**, 2 warnings, 24.27s |
| Guards | `python3 .claude/hooks/test_guards.py` | **41/41** — 27 refused, 14 allowed |
| Byte-compile | `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| Whitespace | `git diff --check` | clean |

Interpreter: `/opt/freedom-blades/runtime/venv-web/bin/python` (3.12), run from
`/opt/freedom-blades/platform`.

**The 2649 figure is for this tree**, re-run after the final edit. It is not an
earlier figure carried forward: the previously reported figure for the
version-16 tree was 2642, and the difference is exactly the seven tests added
here. The **0 skipped** is stated because it is load-bearing — with
`TEST_DATABASE_URL` unset a database-marked test would skip while the run still
exited 0, and this package has none, so the count is a real zero rather than an
unexamined green.

### 5.1 Deterministic regeneration

```bash
python -m tools.phase_5_0_evidence.execution.cli \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

A dry run: it printed `executable: False`, planned 138 steps and started
nothing. Both artifacts were then generated a second time into a scratch
directory outside the repository and compared with `cmp`: **byte-for-byte
identical**. Neither was hand-edited.

| Artifact | SHA-256 |
|---|---|
| `…-concrete-plan.md` | `ce275fd3cf48ed26d0b2c0ed1193835c68d0390115bc0ec02066db3163b8d263` |
| `…-review-manifest.json` | `66855575a17ea08b96775e744fe35a3f344902a4311813524a07d6022d0c495c` |

The manifest carries `"manifest_version": 17`, the `kernel_nodename` fact, the
new `target_identity_digest` and the new `confirmation_token`; the rendered plan
carries the new `| kernel nodename | Test |` row in its §1 target table.

## 6. Checks not run, and what this evidence does not establish

* **Nothing was run on `oracle-test`.** No check of any kind was performed
  against the host, by design and by restriction.
* **The web and bot suites were not run.** This pass touches neither, and the
  restriction keeps `TEST_DATABASE_URL` unset, under which every database-marked
  test in the web suite would skip while still exiting 0. Those suites are
  unverified for this tree and **no figure is offered for them**.
* **No formatter, linter or type checker was run**, consistent with previous
  passes in this package; none is configured as a gate for it.
* **A local green suite does not confirm target-host behavior.** The tests
  compare injected observations against the approved facts. They prove the
  comparison is bound to the right fact and fails closed — they prove nothing
  about what `oracle-test`'s kernel will actually report at admission time.
* **I3 is not confirmed by anything here.** The verifier was not invoked
  operationally. Whether the reconciled admission admits the real target is
  established only by an authorized operational pass, which this is not and does
  not request.
* **The nodename value `Test` is not independently re-verified here.** It is
  taken from Peter's decision and the R4 observation. This pass did not and
  could not observe it.

## 7. Security implications

* **Fail-closed is preserved and the admission surface does not widen.** The
  comparison remains one tuple equality decided before the first write, with the
  same refusal code and exit status. The set of admissible hosts does not grow:
  it changes from one unsatisfiable value to one satisfiable value.
* **The approved-identity surface grows by one fact, deliberately.** More
  identity material in the digest means more ways for the token and manifest to
  stop matching, which is the direction that favors safety.
* **The refusal remains non-disclosing.** `target-mismatch` reveals neither the
  observed nor the approved value; no new value reaches any output path.
* **No secret was read, printed, transferred or modified.** The diff adds no
  `.env` path, credential, key, certificate or production identifier. Both
  guard hooks were exercised and refuse as before.
* **No new authority.** The new digest and token are review input. Execution
  still additionally requires `--execute` and a reviewer-supplied digest, and
  `is_executable` is `False`.
* **One residual judgement, disclosed:** `HostProbe.host()` keeps its name while
  returning a nodename first. The docstrings now say so explicitly. If the
  reviewer considers the name itself a defect, it is a contained rename and this
  pass did not make it unilaterally.

## 8. Diff review

Confined to the decided change: three source files, four test files, r6, the two
regenerated artifacts, the handover, the restriction banner, plan §20 and four
registers. No unrelated, earlier-pass or reviewer-authored change in the working
tree was reverted, reformatted or otherwise disturbed; the pre-existing stash
entry (`temp before rebase`) is untouched. No secret or credential path appears.
No file was added to or removed from the manifest's covered source set.

## 9. Configuration, deployment, rollback

None. No configuration, environment variable, `.env.example` entry, service
file, migration or deployment step changed. Rollback is `git checkout` of the
listed files; nothing outside the repository was altered, so there is no state
to recover. Reverting the source and regenerating the two artifacts restores the
version-16 tree and `be9e110f…` exactly.

## 10. Questions for the independent reviewer

1. **Semantics.** Is `kernel_nodename` the right name and the right position
   (immediately after `host`)? Should the facts instead carry an explicit note
   that no *other* consumer compares it, or is the field docstring sufficient?
2. **Fail-closed admission.** Is a single tuple equality still the right shape
   now that the first element comes from a different fact than the other two?
   Should nodename comparison be case-sensitive — it is, and
   `nodename-case` asserts that `test` refuses — or is that over-strict for a
   kernel value an administrator could re-case?
3. **Identity hashing.** Is including the nodename in `TARGET_IDENTITY_DIGEST`
   and therefore in `CONFIRMATION_TOKEN` correct, given the token is typed by an
   operator? The token's visible prefix is unchanged and only its digest suffix
   moved — is that the intended operator-facing outcome?
4. **Manifest and version reconciliation.** Does the move to 17 match the
   established rule, and is the recorded rationale complete? Is `target_facts`
   gaining a row, rather than the mapping gaining a key, still a field-set change
   in the sense versions 2–16 used?
5. **Artifact determinism.** Is the two-generation `cmp` comparison, into a
   directory outside the repository, adequate evidence that neither artifact was
   hand-edited? Both are wholly derived from source.
6. **Scope.** Is anything reconciled here that should have been left to a later
   pass — in particular the r6 amendment header and the register wording — and
   is anything left unreconciled that a reviewer would expect to move with this
   contract change?

## 11. What this handback does not do

It does not confirm I3, close a review finding, approve a digest, accept the
reconciliation, advance a gate, release the restriction or authorize an
operational retry. Those are Peter's decisions, taken on independent Codex
review, and the repository-only restriction stays in force until he issues a
fresh authorization.
