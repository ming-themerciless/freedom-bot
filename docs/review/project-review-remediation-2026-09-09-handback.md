# Project-review remediation handback — 2026-09-09

Returned to Codex for independent review. **Nothing here is closed on the
implementer's authority.** Passing tests authorize no operational execution and
close no package gate.

**The submission is deliberately partial, and the partition is the point.**
Finding 3 is implemented. Finding 2 is a **corrected design artifact submitted
for technical acceptance**, plus labelled synthetic reproductions of the defect
Finding 1 names. **Finding 1's mechanism is not implemented**, because the
prompt and the C-8 checkpoint both require the design to be accepted first, and
because combining implementation with the submission is exactly what R16 said
does not satisfy the checkpoint.

| Finding | Severity | Disposition |
|---|---|---|
| 1 — ownership validation occurs after dependent cleanup (**EH-R16-1**, same identity, not a new id) | Blocking | **Open.** Mechanism not implemented; awaiting acceptance of the Finding 2 design. Reproduced under injected boundaries, labelled as a defect reproduction |
| 2 — reject and revise the submitted C-8 ownership design | Blocking | **Conceded in full.** The rejected design's two false claims are named in the new artifact's §1. A corrected design is submitted for technical acceptance |
| 3 — replace live-derived fixture data and sanitize its report | Important | **Implemented.** Fixture rebuilt synthetically, report sanitized, scope inspected and recorded |

Review-input manifest digest, unchanged and **not execution approval**:
`ec1e3e70b5d24aca911df9e4dcd394361ebffdb04b9587434cb74386756f2839`.

---

## 1. Finding 1 — EH-R16-1, still open

**No source file changed for it.** `tools/phase_5_0_evidence/cleanup.py`,
`execution/executor.py` and `execution/case_program.py` are byte-identical to the
tree R16 reviewed. The single `REVALIDATE` step is still generated immediately
before the root `rmdir`, and the configuration restores, flag changes and
descendant removals still precede it.

The finding retains its identity. It is not re-raised, not renumbered, and not
partially closed.

**What is delivered against it now** is the reproduction the review asked to be
possible, in `tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py`. It
asserts the **presence of specific commands in the fake boundary's call log**,
not an eventual S-B label:

* with the root replaced before cleanup, both `install` restores are issued
  against sources under the replaced root, and both precede the only ownership
  comparison the plan generates;
* the count of cleanup commands referencing the root before that comparison is
  **30** — the same number R16 reported independently — and the assertion is
  written as a floor so a later plan change does not turn the reproduction into
  an arithmetic failure;
* an unreadable identity fails the guard closed, and still protects only the
  final `rmdir`;
* a replaced **descendant** is removed while the root's identity matches,
  because nothing compares a descendant identity;
* structurally: exactly one `REVALIDATE` exists, exactly one step carries
  `requires_revalidated`, neither `RESTORE` does, and both restores precede the
  guard.

Two controls sit beside them so the reproductions cannot pass against a cleanup
that never runs: ordinary cleanup still reaches S-C with both restores issued,
and the independently safe reversals — accounts, groups, role, database — still
run when the guard fails, which is a property the corrected design must keep.

Every case in that module is labelled in its own docstring and in the module
docstring: **a green run is evidence the defect is open**, and the assertions
will have to be inverted when the mechanism lands.

---

## 2. Finding 2 — the corrected design

**Artifact:**
[`phase-5-0-evidence-harness-c8-ownership-design-r16-2.md`](phase-5-0-evidence-harness-c8-ownership-design-r16-2.md).
**Status: submitted, not accepted, not implemented.** It supersedes
`phase-5-0-evidence-harness-c8-ownership-design-r16.md`, which is rejected.

### 2.1 The two false claims, conceded

* **`mkdirat` followed by `openat` does not detect child replacement.** The
  rejected pseudocode held the parent descriptor and then resolved the child by
  name; that fixes which directory the lookup happens in and says nothing about
  whether the entry is the one `mkdirat` created. There was no comparison and no
  second reading in it, so no branch could have reached the exit `66` the text
  claimed. Conceded without qualification.
* **The root-permission argument does not hold.** Read against the generated
  plan: `…/probe` and `…/probe-ro` are `0770 root:freedomsheet`, so any member of
  a group this run creates may replace entries in them — and the plan itself does
  so, as `freedomsheet`, in eight steps. `CAP_DAC_OVERRIDE` is granted
  **ambiently** to `fbprobe` in `B5-E4`, `B5-E6` and `B5-C6-01` … `B5-C6-04`, so
  an identity that can write anywhere under the root, `before/` and `bin/`
  included, is inside the plan rather than outside the threat model.

### 2.2 What the corrected design says

It answers the seven numbered requirements in order. In summary:

* **§3 lifecycle trace** — every operation, what it acts on, and every later
  pathname resolution. It shows that between the identity read and the single
  guard the harness holds **no descriptor at all**: every step is a separate
  process and identity is re-derived by name.
* **§4 what establishes that the created object is the opened object** — on Linux,
  **nothing does**. `mkdir`/`mkdirat` return no descriptor, `O_TMPFILE` creates
  regular files only, `linkat` refuses directories. Creation and identity
  acquisition cannot be made atomic for a directory. The design therefore states
  a **trust boundary** instead of claiming detection, and makes it checkable:
  **P1** adds five parent-directory reviewed target facts, shipped `UNCONFIRMED`
  with the executor refusing, compared against five new observation keys on the
  existing `mkroot` verb. Obtaining the values is the read-only preflight, which
  is Codex's.
* **§5 inventory** — the directory and mode table taken from the generated plan
  now, the seven subjects a non-root identity can replace, the two subjects whose
  replacement matters most (`before/pg_hba.conf`, `before/pg_ident.conf`), and the
  guards' own trust chain, including that the bootstrap program comes from a
  worktree recorded as group-writable under `H-1` / `D5.0-12` / `OD-65`.
* **§6 guard-to-effect window** — stated as **not closable**. Linux has no
  `funlinkat`; every removal names a final path component. Two alternatives —
  `/proc/self/fd` prefixing and a descriptor-addressed `remove` verb — are
  described, costed and **not proposed**.
* **§7 the mechanism**, each item labelled proved / boundary / residual. The
  substantive addition beyond the rejected design is **P3**: configuration
  restoration compares the capture's **content** against a digest recorded at
  capture time, so a substituted capture is refused whatever replaced it and by
  whatever route. That removes the highest-consequence effect from the identity
  argument altogether. It needs one new read-only `digest` verb, which is
  identified as a widening and routed for decision rather than assumed.
* **§8 regression matrix**, split into `[reproduction]` (in the tree now) and
  `[proposed]` (unwritable until the mechanism exists), mapped to the review's
  nine bullets.
* **§9** lists the six items needing a maintainer decision, with who decides each.

### 2.3 Proposed expansions and residuals, routed rather than assumed

| Id | What | Kind |
|---|---|---|
| P1 | five parent-directory target facts; five extra `mkroot` observation keys | observation widening; obtaining the values is the preflight |
| P3 | a new read-only `digest <path>` verb | **privileged-interface widening — maintainer decision** |
| R-C8-1 | the create-to-identify interval, not closable on Linux | residual needing acceptance |
| R-C8-2 | the guard-to-effect interval, not closable on Linux | residual needing acceptance |
| R-C8-3 | the digest-to-install interval for a restore | residual needing acceptance |
| R-C8-4 | `rm` on the seven replaceable probe subjects: accept with the inventory rendered, or refuse and always report residue | residual needing acceptance; the design recommends accepting and says why |

**No expansion was implemented.** No verb, argument kind, arity, privilege,
identity or executable changed in this submission.

---

## 3. Finding 3 — sanitation

### 3.1 The fixture

`tests/test_skills.py` — the test is rebuilt and renamed
`test_artisan_crafting_skill_matches_its_tool_alias`. It constructs two cells
here: one artisan tier with its tool, and a second tool with no crafting skill
behind it. The tier differs from the one in the original report, and the extra
entries that came from the copied row are gone.

It remains a real regression. Evaluated against a reconstructed pre-fix
`_clean_tool_name` — the alias branch removed, nothing else changed — the aliased
tool resolves to `journeyman` and the assertion fails; with the shipped fix it
resolves to the artisan tier. The second assertion pins the fallback that the
defect produced, so the test now fails in both directions rather than one.

`test_clean_tool_name_artisan_aliases` is unchanged: it uses generic tool
vocabulary only and is the alias-level regression the prompt asks to keep. The
unrelated-tool tests are untouched.

### 3.2 The report

`docs/review/live-bot-herbalist-crafting-defect-fix-review.md` — the character
identifier is removed from all three places it appeared, the two transcribed
sheet cells are removed, and the claims of reproducing an exact live row and of
evaluating against that character's data are replaced with generic descriptions.
A dated sanitation note records that the removal happened and what class of
material it covered, **without repeating the material**. The renamed test is
described in its new form, with a note that it previously carried copied values.
The defect analysis, the fix description and the scope declaration are otherwise
unchanged.

### 3.3 Scope inspected

Searched the working tree for the character identifier, for the transcribed cell
combination, and for the phrases claiming an exact reproduction. After the
changes above, **no occurrence of any of them remains**.

Four other places mention the artisan and tool names and were **deliberately left
alone**, because they are the generic domain vocabulary the prompt says to
preserve — a tier and an ordinary tool name, with no character identifier and no
transcribed row:

* `tests/web/test_p3_4_static_assets.py`, the allowlist comment;
* `docs/project-management/change-log.md`, entry `C-BOT-01`;
* `docs/review/phase-5-0-evidence-harness-implementation-handback.md`, the
  superseded R3 scope-guard discussion; and
* `models/skills.py`, the alias table itself.

`tests/fixtures/sheet_characters_sample.csv` was inspected: it is explicitly
labelled a synthetic fixture, its rows are `Test …` placeholders, and it contains
no herbalist entry. Nothing there was changed.

**No live data was fetched and no credential was read to perform or validate any
of this.** Git history was not rewritten. The material is in commits before this
session; if further handling of already-committed data is wanted, that is a
maintainer disposition and the scope is: one review document and one test
function, both named above.

### 3.4 Production behaviour

`models/skills.py` is untouched. The alias fix stands, no game policy changed, and
no service was restarted or contacted.

---

## 4. Preserved safeguards

Re-asserted in this tree rather than assumed:

* observed refusal/admission stays distinct from the expected `J-26` — the R16-2
  regressions pass unchanged;
* Band-7 coverage stays separate from passing outcomes and from overall
  completeness, and `eligible_for_operational_acceptance` is `False`
  unconditionally;
* Band-7 producers stay explicitly unresolved, the shipped plan is
  `is_executable=False`, and a supplied record still cannot close a missing
  producer;
* the C-6 immutable-flag experiments, the executor's six gates, the
  pre-existing-object protections and the configuration-recovery safeguards are
  unchanged;
* no Package 5.0 product tooling or table was built.

---

## 5. Changed files

| File | Finding | Change |
|---|---|---|
| `docs/review/phase-5-0-evidence-harness-c8-ownership-design-r16-2.md` | 2 | **new** — the corrected design, for acceptance |
| `tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | 1, 2 | **new**, 13 cases — labelled defect reproductions, inventory assertions and two controls |
| `tests/test_skills.py` | 3 | the live-derived fixture replaced and the test renamed |
| `docs/review/live-bot-herbalist-crafting-defect-fix-review.md` | 3 | sanitized, with a dated note |
| `tests/phase_5_0_evidence/harness_fixtures.py` | — | `runnable_plan()`'s docstring corrected: it described C-7 as resolved, which EH-R16-4 reversed |
| `docs/review/project-review-remediation-2026-09-09-handback.md` | — | **new** — this document |
| `docs/review/Handover information`, `docs/project-management/status.md` | — | pointer updated |

**No file under `tools/` changed.** No generated artifact was hand-edited.

---

## 6. Manifest applicability

**Regeneration is not applicable to this pass.** No file in `COVERED_SOURCES`
changed: every change is under `tests/` or `docs/`, neither of which the manifest
covers. Confirmed rather than asserted — the plan was regenerated through its
non-executing path and compared against the committed artifacts:

```text
python -m tools.phase_5_0_evidence.execution.cli --manifest-out … --render …
committed artifacts match the fresh generation, byte for byte
review manifest digest: ec1e3e70b5d24aca911df9e4dcd394361ebffdb04b9587434cb74386756f2839
```

The digest is unchanged from the previous submission, **no new manifest version
was invented**, and the 32 covered sources were independently re-hashed outside
the harness with **0 mismatches**.

---

## 7. Verification — commands, interpreters, results

Serially, `TEST_DATABASE_URL` **explicitly unset** throughout, in the order the
prompt sets out.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
193 passed

env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_skills.py
60 passed, 1 warning

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py
13 passed

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_r16_remediation.py
39 passed

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
1388 passed

env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
2990 passed, 326 skipped, 1 warning

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
1610 passed, 1362 skipped

node --test "foundry-module/tests/"*.test.mjs
tests 171, pass 171, fail 0

python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence
python -m compileall -q models/skills.py tests/test_skills.py
clean

git diff --check
clean
```

The harness suite moved from **1375** to **1388**: the 13 reproduction cases.
The skills suite is **60**, unchanged in count — the sanitized test replaced the
old one rather than being added beside it.

**No configured suite fails, and no assertion was weakened to obtain a pass.**
The reproductions assert the current tree's behaviour deliberately and say so in
their own docstrings.

### 7.1 Interpreters, identified accurately

Both fallbacks were verified present before use, and neither is the canonical
default:

| Path | Present | Used for |
|---|---|---|
| `/opt/discord-bots/venv-web/bin/python` | yes — 3.12.3, pytest 8.4.2 | harness and web suites |
| `/opt/discord-bots/venv/bin/python` | yes — pytest and `discord` importable | bot and skills suites |
| `/opt/freedom-blades/runtime/venv-web/bin/python` | **exists as a path on this host and has no pytest** | **not used** |

The canonical test environment remains `/opt/freedom-blades/runtime/venv-web` on
`oracle-test`. Its path existing here establishes nothing about that host, and
`oracle-test` was not contacted.

### 7.2 Skips, and what they are not

Every database-marked assertion skipped: `TEST_DATABASE_URL` was unset for every
command. The bot suite skipped **326** and the web suite **1362**; the documented
figure for a real database run is 80 web skips. **These skips are unverified
assertions, not successful integration evidence**, and nothing in this submission
establishes any PostgreSQL behaviour.

### 7.3 Tooling not configured or unavailable

No formatter, linter or type checker is configured in this repository: there is no
`pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `.pylintrc`, `mypy.ini`,
`ruff.toml` or pre-commit configuration. `black`, `ruff`, `flake8`, `mypy`,
`pylint` and `shellcheck` are none of them installed on this host. That is stated
rather than reported as a pass. `pytest.ini` is the one configured tool, and
`compileall` and `git diff --check` are what was available to run.

### 7.4 Checks not run, by restriction

No SSH; no synchronization, inspection or mutation of `oracle-test`; no database
operation; no destructive drill; no generated-vector execution; no `--execute`;
no armed real boundary or materializer; no provisioning; no service change; no
credential access. Every effect in every test is injected. The read-only target
preflight was **not** performed — it remains authorized and assigned to Codex —
and the twelve reviewed target facts remain `UNCONFIRMED`.

---

## 8. Remaining risks, decisions and gaps

* **EH-R16-1 is open.** The mechanism is unimplemented and the defect is live in
  the tree.
* **Six decisions are pending**, listed in §9 of the design artifact: P1's parent
  target facts, P3's new `digest` verb, and residuals R-C8-1 … R-C8-4. Two of
  them (R-C8-1, R-C8-2) are limitations of Linux rather than of this design, and
  are offered for acceptance rather than for repair.
* **Band 7's three producers remain unresolved** under conflict C-7, and
  `is_executable` is `False`. A separate evidence-only producer would need its own
  scope and authority, described in §4 of the R16 remediation handback.
* **The twelve reviewed target facts remain unconfirmed**, and P1 would add five
  more of the same kind.
* **Already-committed sanitized material** is in Git history and was not
  rewritten; §3.3 states the scope for maintainer disposition.

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**. Migration
0014, product implementation, deployment, cutover and Package 5.1+ remain
unauthorized.

Returning the corrected C-8 design and the independent sanitation work for Codex
review **before** the mechanism is implemented. After an accepted implementation,
this returns again for independent implementation review.

---

## Erratum — 2026-09-09, after project review R2

**The text above is preserved unchanged.** This section records five statements
in it that project review R2 found to be wrong or unsupported, and what the
correct statement is. It does not rewrite the original, and it does not close
any finding. Full reasoning is in
[`phase-5-0-evidence-harness-c8-ownership-design-r16-3.md`](phase-5-0-evidence-harness-c8-ownership-design-r16-3.md).

**E-1. §2.2, sixth bullet — "§6 guard-to-effect window — stated as not
closable. Linux has no `funlinkat`."** The `funlinkat` fact is correct and
narrow: every removal names a final path component, so *final-entry*
substitution between a check and a pathname-addressed removal is not closable by
a check. The generalisation to the whole window is wrong. Whole-root and
deeper-directory substitution **are** reducible by a held descriptor chain,
because `rename(2)` leaves open descriptors for the renamed object unaffected,
which a pathname identity comparison cannot reproduce. See r16-3 §1.3(a),
§9.2 and §9.3.

**E-2. §2.2, sixth bullet — the two rejected alternatives.** The stated ground
for rejecting `/proc/self/fd` prefixing and a descriptor-addressed `remove` verb
included the claim that their benefit "is already obtained by comparing the
root's identity". That is a false equivalence and is withdrawn. A held object
reference and a compared observation are different protections. The alternatives
remain **not proposed**, on cost and authorization grounds rather than on that
one. See r16-3 §1.3(b) and §9.3.

**E-3. §2.2, seventh bullet — "P3 … removes the highest-consequence effect from
the identity argument altogether."** Withdrawn. P3 hashed a capture in one
process and then ran `install` against its pathname in another; a capture
replaced after the digest passed is installed despite the passing check, and the
root's identity can remain unchanged throughout. The `[proved]` label the design
carried above that claim was not earned. r16-3 §5 replaces P3 with a contract
that binds the bytes written to the bytes checked.

**E-4. §2.3 and design §9 — the recommendation to accept R-C8-4.** It rested on
there being no mechanism for the seven replaceable probe subjects. There is one:
the only non-root actor that can substitute them is an account this run itself
creates, and its concurrency is excludable and checkable. r16-3 §9.5 sets out
how, and R-C8-4′ conditions the removals on that check rather than accepting
them blanket.

**E-5. §3.3 — "The material is in commits before this session."** Not
established, and withdrawn. Read-only inspection of this repository found the
sanitized report **untracked**, unknown to `git ls-files`, with no commits from
`git log --all` on its path and none from the corresponding `git log --all -S`
search for the former test name; the two source changes are modified and
uncommitted. Within that scope the material is not committed here. That is not
proof of absence from any remote or unreachable object, and nothing observed
supports a claim of historical exposure either. No remote was contacted and no
history was rewritten. See r16-3 §12.

**Unchanged by this erratum:** EH-R16-1 remains open with its existing identity;
Finding 3's working-tree sanitation stands, with the synthetic skills fixture,
the sanitized crafting report and the production alias fix preserved; and the
review-input manifest digest is unchanged and is not execution approval.
