# C-P5.0-LAB-V6-D-R1 — r6 contract topology correction handback — 2026-09-17

One bounded repository-local **documentation** correction of Codex Blocking
finding **PR-20260917-LAB-V6D-R1-1**, raised in the
[independent topology-disposition review](project-review-2026-09-17-reserved-laboratory-v6-topology-disposition.md).
Only `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` and the
project-management records changed. **No source file changed, no artifact was
regenerated, no host was touched, and nothing here closes the finding** — the
reviewer closes it, not this pass.

## The finding, and what was corrected

The disposition amended §7's item table and the D1 row but left the withdrawn
`/opt` topology standing in two operative rows, which is the control failure the
pass's own Blocking PR-20260917-LAB-V6D-2 named: a dated banner is not a
correction of a normative row.

1. **§1.3.3, the descriptor inventory preamble.** It opened with
   `R = /opt/freedom-blades/evidence/<run>` six lines above its own amended D1
   row. It now states **`R = /var/lib/fb-evidence-p5-0`** — the approved
   target's `root_path`, created exclusively by the reviewed concrete plan's
   `mkroot` and not by prerequisite provisioning, its final component the one
   `targets.validate_mutation_root` admits — and says that the `"<run>"` name in
   C1's `mkdirat` and §1.4.1's by-name `fstatat` is `R`'s own final component.
2. **§7's live V6 row.** It directed the survey to observe
   `/opt/freedom-blades/evidence` and reported the preflight **unperformed**. It
   now names only the canonical locations (`R`, and the filesystem V12, V4, V9
   and V5 would be created on), states explicitly that the withdrawn `/opt`
   path is not observed, and records V6 as **performed 2026-09-16 and not
   closed**, with what the survey found, what it could not confirm, and the fact
   that the post-provision repetition is unperformed and separately authorized.

## The further old-topology statements found and corrected

The finding also required a search of the operative contract. Five more were
found; all are in the same file.

* **§1.3.3's D1 row.** It still described `evidence_pathfd` as *"the evidence
  root … `/var/lib/fb-evidence-p5-0`"*. That cannot be right under the accepted
  disposition: §7.3 decision B, §10 and `provisioning.EVIDENCE_ROOT` make
  `/var/lib/fb-evidence-p5-0` **`R` itself** (D2/D3), while `plan.py` and
  `executor.py` both define the pair as *"the disposable root **and its
  parent**"* — `ROOT_ROLE` and `EVIDENCE_ROLE`. D1's object is therefore `R`'s
  parent, which under the canonical topology is `/var/lib`: root-owned, not
  group- or other-writable, administrator-only **[A]**, and not a provisioning
  item (§7.3 leaves V12's own parent outside the delta). The row now says that.
  **This is the one judgement call in the pass and it is flagged for the
  reviewer** — the review accepted the D1 row as amended, and this pass changes
  it because the withdrawn *"provisioned evidence root"* between `/var/lib` and
  `R` is exactly the object the maintainer withdrew.
* **§7's submission paragraph** said *"both preflight observations remain
  unperformed."* V8 does; V6 was performed on 2026-09-16.
* **§7's D1-remediation paragraph** ended *"V6 remains an unperformed preflight
  observation …"* — same defect, same correction, with the reason it did not
  close.
* **§9.3's I12** still required *"that the `evidence` entry is reachable only by
  root"* and expected the check *"to fail on the entry until a maintainer
  rules."* The maintainer ruled on 2026-09-17 (decision A) and withdrew the
  location. The clause is withdrawn; I12 is now the post-provision repetition
  of the read-only survey, which is why V6 stays performed-but-not-closed.
* **§7.3's decision-B row** closed by declaring every remaining §1.3.3 and
  §1.4.1 `/opt` passage *"historical and superseded by the amendment at the head
  of this document."* That sentence is the banner-cure the review rejected. It
  now records that the rows were corrected in place and names where the `/opt`
  form legitimately survives.

Two smaller ones: **§2.2's** location sentence now marks
`/opt/freedom-blades/evidence` as withdrawn where it excludes it, and
**§1.4.1's** dated paragraph no longer points at §1.3.3's D1 row as retained
`/opt` history, because it no longer is any.

A dated **C-P5.0-LAB-V6-D-R1** block is added at the head of r6, and every
changed passage is marked *amended 2026-09-17, C-P5.0-LAB-V6-D-R1*.

## Considered and deliberately left

* **The head banners and the §7/§7.2/§7.3/§9.2 historical passages.** Each is
  dated, attributed and labelled as history or as a struck row. §7.2 stays
  *(historical)* with its step-6 `CAP_FOWNER` dependency intact.
* **§9.2 row 84**, which cites `/opt/freedom-blades`'s observed `1001:1001 0755`
  shape as the parent-refusal case the applier must not widen around. That is a
  true observation used as a test rationale, not a topology definition.
* **Peter's dated 2026-09-15 disposition paragraph** in §7, which says the
  preflight *"remains authorized and queued."* It is a quoted, dated maintainer
  decision; restating its status is the surrounding text's job, and that text is
  corrected above.
* **Everything approved.** `R`, V12's `root:root 0755`, the released subset
  `V1, V2, V3, V12, V4, V9, V5` and its order, V7's exclusion, `EVIDENCE_ROLE`'s
  deferred registration and `approved = False` on every item are untouched.

## Evidence

**Restricted local pass**, per the active restriction: repository changes and
local tests only, **`TEST_DATABASE_URL` unset**, suites serial, no SSH and no
host contact. Interpreters were verified on this host before use:
`/opt/freedom-blades/runtime/venv-web/bin/python` (3.12.3) for the evidence
suite and the artifact regeneration, `/opt/discord-bots/venv/bin/python` and
`/opt/discord-bots/venv-web/bin/python` (both 3.12.3) for the bot and web
suites, and `node` v24.20.0 for the Foundry module.

| Check | Command | Result |
|---|---|---|
| focused V6 provisioning module | `python -m pytest -q -rs tests/phase_5_0_evidence/test_v6_provisioning.py` | **131 passed**, 2 warnings |
| complete evidence suite | `python -m pytest -q -rs tests/phase_5_0_evidence` | **2,374 passed**, zero failed, **zero skipped**, 2 warnings |
| bot suite | `python -m pytest -q -rs tests/test_*.py` | **3,026 passed, 326 skipped** |
| web suite | `python -m pytest -q -rs tests/web` | **1,609 passed, 1 failed, 1,362 skipped** |
| Foundry module | `node --test "foundry-module/tests/"*.test.mjs` | **171 passed**, 0 failed |
| structural guards | `python3 .claude/hooks/test_guards.py` | **31/31** — 19 refused, 12 allowed |
| scoped compile | `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | passed |
| whitespace | `git diff --check` | passed |

The two warnings are the existing unknown pytest options `asyncio_mode` and
`asyncio_default_fixture_loop_scope`.

**The web failure is the same pre-existing one, on its own premise.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
asserts *"no untracked directory in this tree; this test proves nothing"*, and
this pass added no untracked directory. It is unrelated to this change.

**Every skip is an unverified assertion, not PostgreSQL evidence.** With
`TEST_DATABASE_URL` unset the web suite's 1,362 skips are the documented false
green; the correct figure under the canonical `oracle-test` run is 80, and that
run is not authorized here.

**Artifacts are unchanged and were re-verified, not regenerated into the
tree.** A non-executing CLI generation to a scratch path is byte-identical to
both installed artifacts; all **44** covered hashes were independently
recomputed with **zero mismatches**; `manifest_version` stays **13**; and the
review-input digest recomputes to

`6b3ec46f82fa55983d52765cedf32e6d61723059ebe816269c112716dd478973`

— **unchanged**, because no covered source changed. It is **review input only,
it is not approved while the finding is open, and it must not be passed to
`--execute`.**

**No formatter, linter or type checker is configured** in this repository. That
is unconfigured tooling, not a passed check.

## Files changed

* `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` — the eight
  corrections above and the dated head block.
* `docs/review/phase-5-0-reserved-laboratory-v6-d-r1-contract-correction-handback.md`
  — this file.
* `docs/project-management/status.md`, `change-log.md`, `raid-register.md`, and
  `docs/review/Handover information` — the pass recorded.

No migration, no configuration change, no deployment change, and no
secret-bearing file was read or written. **Rollback is `git checkout` of these
documents**; nothing was applied anywhere. The working tree still carries the
preceding uncommitted passes, so a reviewer separating this pass should read the
passages marked *C-P5.0-LAB-V6-D-R1* rather than the whole file diff.

## Checks not run, and why

* The canonical `oracle-test` run with `TEST_DATABASE_URL` exported, and every
  database-marked test behind it — **no SSH, synchronization or host access is
  authorized**.
* Every host observation: the V6 re-survey, I12, controlled write verification,
  provisioning, `--execute`. None is authorized and none was performed.
* The bot, web and Foundry suites were re-run here against the submitted tree
  even though this pass changes no code, so the figures describe this tree.

## Unresolved, and reviewer focus

1. **The D1 object change is the item to check first.** Does the reviewer agree
   that `evidence_pathfd` holds `R`'s parent `/var/lib` under the canonical
   topology, on `plan.ROOT_ROLE`/`EVIDENCE_ROLE`'s *"the disposable root and its
   parent"*? If the intended reading is instead that `R` sits one level below an
   evidence directory, then `provisioning.EVIDENCE_ROOT`, §7.3 decision B, §10
   and the concrete plan's `mkroot` all disagree with it, and the disagreement
   is a maintainer question rather than an implementer's choice.
2. Whether any further passage should be corrected rather than left as dated
   history — the four listed under *Considered and deliberately left*.
3. **V6 remains performed-but-not-closed**, I3 unconfirmed, V7 excluded, V8 and
   V10 unperformed, `plan.is_executable` **False**,
   `reservation.REAL_EXECUTION_REFUSAL` unconditional, and Package 5.0 **not
   ready**.

## Restrictions observed and next action

No SSH, synchronization, host inspection, `sudo`, user or group creation,
`/etc` edit, `/run`, `/var/lib` or `/opt/freedom-blades` creation,
`systemd-tmpfiles`, link, controlled write verification, provisioning, database
operation, generated-vector execution, real participant, real
boundary/materializer or `--execute` was performed or is authorized.

**Next action: independent Codex technical and security re-review of
PR-20260917-LAB-V6D-R1-1.** No gate advances and no digest is approved.
