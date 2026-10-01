# Handback — review and correction of the RP-11 Option-1 documentation alignment

Work ID: `C-P5.0-R5-RP11-I1-R3-D2-DOC1-R1`

Date: 2026-09-28

Reviewed return:
[`phase-5-0-p5-r5-rp11-i1-r3-d2-option-1-documentation-alignment-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-d2-option-1-documentation-alignment-handback.md)
(`C-P5.0-R5-RP11-I1-R3-D2-DOC1`, Codex; SHA-256
`223dffc63c4d604e77725d53152cc37c3952647336d15a8907c869c25c3e88c8`, unchanged
by this pass)

State: **returned repository-only for independent Codex review. Claude has
stopped.** Nothing is accepted and no finding is closed by this pass.

**Assignment basis.** Peter Duscha asked Claude, in session, to review the
D2-DOC1 return, since Codex had implemented it. He then instructed Claude to
fix the findings and decided the one open question (§4). No handover record
assigned this pass. The maintainer should confirm that the in-session
instruction is the assignment of record.

**Reviewer independence.** Codex implemented D2-DOC1, and Claude reviewed it.
Claude has now implemented this correction, so Codex, or another reviewer who
is not Claude, must review it. Claude also wrote the original decision proposal
and earlier amendments of the draft. Findings 1 and 2 concern edits to those
texts.

## 1. Review outcome

No Blocking finding. The Option-1 behavior is unchanged, and the D2-DOC1
evidence reproduced:

* **Hashes.** All seven hashes in the D2-DOC1 handback matched the tree. Both
  archives were byte-identical to R2's recorded "after" values.
* **Source.** The source delta from R2 is documentation-only. It was checked
  against a preserved R2-era copy of the tree:
  * `retention_check.py` differs in two docstring lines (`482e1a5a…` →
    `208bec5a…`);
  * `test_rp11_retention.py` differs in docstrings only;
  * `test_r16_remediation.py` differs in its version pin, 24 → 25, and a
    comment;
  * `review_manifest.py` differs in `MANIFEST_VERSION` and its history
    comment.
* **Draft.** The draft's prior bytes were rebuilt exactly (`4f68e4c7…`
  verified) from D2-DOC1's recorded edits. Its D2-DOC1 delta is exactly six
  edits: the banner, the draft reminder, RP-11 row (e), B0-RA, X-4 and B0-RA's
  unresolved clause. The Option-1 text in X-4 and B0-RA matches the decision
  record.
* **Tests and artifacts.** The whole package gave 3348 passed, 0 skipped at
  both limits. The dry run was byte-identical at `f63cf359…`.

Findings:

| # | Severity | Finding | Disposition in this pass |
|---|---|---|---|
| 1 | Important | The historical decision proposal was rewritten in place (`ac504ce1…` → `9511d1a7…`): its banner, State line, §1, §6, §8 and §9. The D2-DOC1 handback said historical records were not rewritten. The rewrite left §9 saying RP11-I1-R3-2/-3 "remain Open", which contradicts the decision record | **Restored** byte-for-byte to `ac504ce1…`. The erratum is §2 |
| 2 | Important | The draft banner extended the **R1** attribution paragraph so that it recorded the later D2 decision. D2-DOC1 had no attribution of its own. It also said Codex "accepted" R2, although under plan §0.3 a reviewer does not accept | **Corrected** (§3) |
| 3 | Important | The concise current-state files omitted three findings that were never closed: `RP11-I1-2` (Blocking), `RP11-I1-R2-1` (Blocking) and `RP11-I1-R1-1` (Important). They were last stated Open in the I1-R3 review, line 98 | **Restored** as Open, with Peter's directed proposed disposition (§4) |
| 4 | Important | The D2-DOC1 handback lacked §16.3 contents: a files-changed list, security implications, checks not run and reviewer focus. Its 774-test focused selection named no modules | **Erratum** (§2). This handback supplies those contents for its own pass |
| 5 | Optional | Draft §4.3 said "Two later repository passes" changed covered sources and omitted versions 24 and 25 | **Corrected** |
| 6 | Optional | B0-RA's "Unresolved" clause listed "the accepted Option-1 unadmitted-pair rule applies" among its reasons | **Corrected**: the phrase is removed; the rule is stated earlier in the same row |
| 7 | Optional | Cosmetic issues in two test files: an over-long docstring line in `test_rp11_retention.py`, a docstring broken mid-sentence at line 868, and a missing `#` separator in `test_r16_remediation.py` | **Fixed**, on Peter Duscha's explicit permission after a first attempt was refused by the tool-permission classifier and not routed around. Docstring and comment text only |

## 2. Erratum to the D2-DOC1 handback — dated 2026-09-28

The D2-DOC1 handback (`223dffc6…`) is durable history. It is not edited.
This erratum corrects it:

| D2-DOC1 location | Original claim | Correction |
|---|---|---|
| "Archives" | "Historical prompts, handbacks and reviews were not rewritten or deleted." | **Incorrect for one record.** D2-DOC1 rewrote the decision proposal in place, `ac504ce1…` → `9511d1a7…`. This pass restores `ac504ce1…` exactly. The proposal stays pre-decision input, and the [decision record](project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md) supersedes its pending-decision statements. That record is the authority for the decision, the closure of RP11-I1-R3-1 and the closures of RP11-I1-R3-2/-3 |
| "Outcome" | "`RP11-I1-R3-1` is Closed … `RP11-I1-R3-2` and `RP11-I1-R3-3` are Closed as remediated" | **Incomplete.** `RP11-I1-2`, `RP11-I1-R2-1` and `RP11-I1-R1-1` remain Open (§4) |
| whole handback | no files-changed list | D2-DOC1 changed these files:<br>• `retention_check.py`, `review_manifest.py`, `test_rp11_retention.py` and `test_r16_remediation.py`<br>• both generated artifacts<br>• the operational draft and the decision proposal<br>• the decision register, change log and `open-decisions.md`<br>• Handover information, `status.md`, plan §20 and the test-server banner<br>• both archive indexes<br>It also added the two snapshots and its handback |
| "Verification" | "774 passed" focused selection | The modules were not named, so that figure is not independently reproducible. The whole-package figure reproduced |
| "Exact review inputs", operational draft | `48bef661…` | Superseded as review input by `5c6046fc…` (§3) |

## 3. Files changed, with SHA-256

"Before" values were recorded before any edit. The one exception is
`change-log.md`, whose "before" value was reconstructed by removing this
pass's single inserted row.

| File | Change | Before → after |
|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md` | restored to the original R1 bytes by exactly reversing D2-DOC1's recorded edits | `9511d1a7…` → `ac504ce188cb2eb477006eb3cbbdf0d66cd932568ecb5ed62a72151ba47f3e60` |
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | R1 paragraph restored to its R1 wording; new attribution of D2, D2-DOC1 and this pass; §4.3 stale list now covers four passes (v22–v25); B0-RA unresolved clause | `48bef661…` → `5c6046fc3dc0b9a931cc32076233b1ea9185dc14c5d0ea1abc193687dcca7de6` |
| `docs/review/Handover information` | current state, restored findings, next review | `07fb5107…` → `264e1d826c2ed05cb7a940b4bb6389aef7bfd7f4290f59a9e2e999d11bab1304` |
| `docs/project-management/status.md` | current status | `92852a4c…` → `6e50b0b2e7dad848aedc2c851d579563f6cfad8182277ac3e3a7e118db3332cf` |
| `docs/implementation-plan.md` | new §20 current action; previous action relabelled *Superseded*, text otherwise unchanged | `18e011dc…` → `c30469bdad3f21bfc2f55592e641cf043d0b4eb7a61634beeed5967924dd04a4` |
| `docs/operations/disposable-test-server.md` | new first restriction banner; previous banner relabelled *Restriction unchanged* | `36e3c7d0…` → `504614a5b262d6bdae83ef377170bab5070acc0a4d01fe7c69e015fe6412edcd` |
| `docs/project-management/change-log.md` | one row | `381590fd…` (reconstructed) → `a5a4c8fe144e6ad0cf6e6bd81e7e4dfc2d41b09b9ae08e0c815f981803885ff5` |
| `docs/review/handover-archive/README.md` | one snapshot row | `d2c69f06…` → `ebc687c1c2763001cb86413530f5510b24f58a3bfb4c07a45963fdbe61627aef` |
| `docs/project-management/status-archive/README.md` | one snapshot row | `50aaeef3…` → `133db609860129c5c916953000e0b1eec04b351f9e2d226f6f11f642bd829582` |
| `docs/review/Handover-information-through-2026-09-28-d2-doc1.md` | new verbatim snapshot | `07fb51074ac48c157270315eefaed89802ebefda04a6e231da91617423da8f4d` |
| `docs/project-management/status-through-2026-09-28-d2-doc1.md` | new verbatim snapshot | `92852a4c6a936a4aff978c87bf5b26e0b44f410c0d876682776cd8e424218db0` |
| `tests/phase_5_0_evidence/test_rp11_retention.py` | finding 7: module docstring rewrapped; test docstring joined (docstrings only) | `d3e158d7…` → `da2f31e6dd3e61862fbd64794b007fa50c54f266ba95f0675b4b8359debfc65e` |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | finding 7: one `#` separator line | `b6112391…` → `6097c8551261ea64c5153ec363c9a0ad30e5864ada3f091658faa154980ddb8f` |
| this handback | new | not self-hashed |

**Unchanged, recomputed after the final edit:**

* review manifest JSON `3632270a…`;
* concrete plan `f177db4d…`;
* `retention_check.py` `208bec5a…` and `review_manifest.py` `709ea407…`;
* the D2-DOC1 handback `223dffc6…`;
* the decision record, decision register and `open-decisions.md`.

Tests are not covered sources. **No covered source changed**, so manifest version 25 and review-input digest
`f63cf3596a95701e3c24813f5362955dcdb5524e7b4fcaf749159db66f91cdb8` stand.

## 4. Maintainer direction — the three restored findings

Peter Duscha chose to keep all three findings **Open**, record a proposed
disposition, and have the reviewer confirm it before he closes them. The
evidence for the proposal:

| Finding | Subject | Proposed disposition and basis |
|---|---|---|
| `RP11-I1-2`, Blocking | The focused evidence was not reproducible in the review context: the `O_TMPFILE`/procfs publication route failed there | **Superseded.** The accepted I1-R3 design removed the procfs route. Codex's R2 review reproduced the whole package, including the RP-11 suites, at 3348 passed, 0 skipped, in its own context at both descriptor limits |
| `RP11-I1-R2-1`, Blocking | The probe cleanup's `stat`→`unlink` race could remove an unchecked replacement | **Superseded.** I1-R3 removed the probe and every automatic unlink, rename and cleanup (draft §9.5.1). The reviewer should confirm that no unlink call site remains on the RP-11 path |
| `RP11-I1-R1-1`, Important | The diagnostic prototype did not exercise the §9.5.4 probe | **Superseded.** The separate probe no longer exists. Each pass's X-1 genesis publication is its fail-closed capability test (draft §9.5.4) |

This is a proposal only. It closes nothing and changes no gate.

## 5. Commands and results

All commands ran on the repository host. Pytest ran serially, one fresh
process per run, with this prefix:
`env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p no:cacheprovider`.

| Run | Result |
|---|---|
| `tests/phase_5_0_evidence`, `ulimit -Sn 1024` in a subshell (confirmed 1024) | **3348 passed, 0 skipped** |
| `tests/phase_5_0_evidence`, default limit | **3348 passed, 0 skipped** |
| Harness dry run with `--manifest-out` and `--render` to scratchpad paths | `DRY RUN — nothing was executed.`; digest `f63cf359…`; `executable : False`; both artifacts `cmp`-identical to the checked-in files |
| `git diff --check` (repository-wide) | clean |

Both pytest runs and the dry-run comparison were repeated after all edits,
including finding 7's test edits, with the same results. The same figures appeared
during the review, before any edit. Every pytest run printed only the two known
`Unknown config option` warnings (`asyncio_default_fixture_loop_scope`,
`asyncio_mode`).

**How prior bytes were recovered.** D2-DOC1's edit records were read from the
local Codex session log for 2026-09-28. Only the patch and substitution text
for the proposal and the draft was read. No credential file was read. Reversing
those edits reproduced `ac504ce1…` and `4f68e4c7…` exactly. That verification
is what establishes the restoration and the draft delta.

## 6. Checks not run, and why

* **Not run: the bot and web suites, `oracle-test`, SSH, sync and database.**
  All are prohibited by the active restrictions. No behavior changed.
* **Not run: a secrets scan.** It is prohibited.
* **Not run: formatter, linter and type checker.** None is configured.
* **Not run: the 774 focused selection.** Its module list was never recorded.
  The whole package supersedes it.

## 7. Security, configuration, deployment and rollback

* **Security, configuration and deployment.** None. The changes are
  documentation only: no source behavior, secret, configuration or deployment
  change.
* **Rollback.** Revert the listed files to their "before" hashes. The proposal
  can be returned to `9511d1a7…`, though that would reintroduce finding 1.

## 8. Reviewer focus

1. Confirm the restored proposal equals the R1 handback's recorded
   `ac504ce1…`, and that the §2 erratum is an adequate substitute for the
   in-place edits.
2. Review the draft's new attribution paragraph, §4.3 and B0-RA against
   `4f68e4c7…` and `48bef661…`. The draft is now `5c6046fc…`.
3. Confirm or reject each proposed supersession in §4.
4. Confirm that no RP-11 unlink or cleanup call site remains
   (`RP11-I1-R2-1`).
5. Confirm finding 7's test edits touch docstring and comment text only.

## 9. Return state

* RP-11 remains unwired, unaccepted and unmet.
* C-11 and the pinned launcher environment remain unresolved, and neither pass
  is executable or authorized.
* P5.0-R5 remains Blocking, and OD-62 G-A remains conditional.
* `plan.is_executable=False`, and Package 5.0 remains not ready.
* No SSH, synchronization, network or host inspection, `sudo`, database access,
  provisioning, controlled write, reboot, verifier, evidence band, harness
  `--execute`, real participant, real capture root, protected-artifact access,
  secrets scan, commit or push occurred.
