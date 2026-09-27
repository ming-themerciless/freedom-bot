# Claude handback — C-P5.0-R5-OP1-R1 operational-evidence prompt remediation — 2026-09-27

Author: Claude, under the assignment in `docs/review/Handover information`
(2026-09-27) and its controlling prompt,
[`phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md).
The controlling defect list is Codex's
[independent review](project-review-2026-09-27-p5-r5-operational-evidence-prompt.md).
Codex remains the Independent Reviewer and did not take part in this pass.

**Repository-only; documentation only.** No command was issued to
`oracle-test` or to any other host. No SSH, synchronization, inspection,
`sudo`, database access, provisioning, verifier, evidence band, controlled
write, reboot or `--execute` occurred. No source, test, hook, manifest,
generated evidence, migration, schema or configuration was changed. The
protected `/tmp` artifacts were not accessed. No secrets scan was run. No guard
or tool refused a call. Nothing was committed or pushed, and nothing was
restored from `HEAD`.

**Nothing here authorizes either pass, accepts the prompt, closes P5.0-R5,
binds OD-62 G-A, sets `plan.is_executable=True` or declares Package 5.0 ready.**

---

## 1. Outcome

The authorization draft was amended in place and is returned for Codex's
independent re-review. It remains visibly **draft and unauthorized**.

| Artifact | SHA-256 |
|---|---|
| Draft as reviewed by Codex on 2026-09-27 | `9bd4f5b54b3bf9fad9a1070dc88f62225e6d25b2d4deafbb59432cf11ad7785c` (verified before editing) |
| [Amended draft](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md), as returned | `7a73d3da474562eb098548cd44270c9d1f39adecb3ab073a6ed02409295ffe61` (890 → 1086 lines) |
| Drafting handback, **unchanged** | `e7db948d4f61938b02d6c8115fd0a1ffcccdbfc5d61115f34dcb0ede6ae24a1b` |
| Codex review, **unchanged** | `bc5d7954506ac8d04ad4425c23d06123c5ad633eb8e4dcd055f23791896171a2` |

**The central result: neither pass is executable as amended.** The remediation
did not make either pass executable. It made the blockers explicit:

* **Pass A** (now *synchronization plus read-only host preflight*) needs
  **RP-11**, a reviewed client-side capture mechanism that does not exist. It
  also needs the MD-5 independent acceptance record (A-6), `MI.pinned_commit`
  and `MI.capture_root`. Its corroborative target-fact steps (A1-C) need
  **RP-10**.
* **Pass B** needs RP-1 through RP-12, all unmet.

The drafting handback's proposal that Pass A was *"immediately admissible"*
(its §1, §10 item 1) and that RP-1 *"needs Pass A's observations"* (§1.1 item
2, §6) are superseded by the Codex review and this amendment. The drafting
handback is left as the durable record of the bytes Codex reviewed.

## 2. Exact changes, by review finding

### 2.1 OP1-R1 — E7 expectations were self-derived (Blocking)

* **RP-1 rewritten** (§4.4). The twelve facts must be **owner-stated
  expectations** that meet a new provenance rule and are independently
  verified. The amended text explicitly excludes values from Pass A, `grep`,
  `/proc`, `id`, `capsh`, `P-01`, `P-02`, `P-05` and `P-06`. It quotes the
  three governing passages: `capability.py`'s sentinel comment,
  `case_runtime.py`'s interpreter-fact comments, and concrete plan `P-06`'s
  refusal text. The claim that the facts *"come from Pass A's observations and
  from nothing else"* is removed.
* **New RP-10 — a typed, fail-closed blocker.** The governing sources require
  a statement by the Operations Owner (or a maintainer) and verification *"there"*
  by an independent reviewer. They supply **no method** for either of these:
  * a non-observational basis for the statement. For E7, every obvious basis
    is itself a host observation: `CAP_LAST_CAP`, the effect of the `sudo`
    policy, or the launcher's bounding set;
  * a way for the reviewer to verify on the host without that verification
    becoming the source.

  A later, separately assigned repository pass must propose a method. Codex
  must review it and the maintainer must accept it. If no sound method exists
  for a fact, the maintainer must rule on it explicitly. This draft invents
  no method and no value.
* **New §4.7 — the provenance and corroboration rule.** It has six
  requirements: stated, not learned; fixed by digest before corroboration;
  independently verified; corroboration one-way (a mismatch stops the band
  and never amends the statement); honest process identity; fail-closed. It
  also covers earlier recorded `oracle-test` observations, such as R8's
  `CapBnd` corroboration. The statement record must disclose any of these
  that its author saw. Whether that exposure disqualifies the basis is left
  for RP-10 to rule.
* **Pass A restructured.** A1-11, A1-12, A1-14 and A1-15 are now class
  **A1-C**, corroborative only. They run only after a digest-pinned
  `MI.target_fact_statement` exists (new A0-09). Otherwise they are
  `not_run (RP-10 unmet)`. Their outputs are renamed `OP.sudo_root_status.*` and
  `OP.sudo_capsh.*`. The text states that they observe a `sudo`-launched
  `grep` and a `sudo`-launched `capsh`, **not** the final interpreted E7
  process. The draft had also named `P-02` as E7's authoritative reading; it
  now names the concrete plan's `P-06` `identity` step.
* **Other places made consistent:**
  * the §3 MD-2 row: fresh observation now comes from `P-05`/`P-06` in Pass B,
    compared with the stated expectations;
  * the §4.6 rows;
  * B0 and B1: a B1 mismatch stops the pass and is never reconciled;
  * the Pass A closing paragraph: its observations are *never* RP-1 inputs;
  * matrix rows 52 and 63;
  * the new §14 handback section 6b.

### 2.2 OP1-R2 — `fsync` failure injection was deferred (Blocking)

* **Row 40 and A-5.0-5(k) reclassified** (§8) as **feasibility: remaining
  P5.0-R5 work**. The row's band is the new **B4b** and its blocker is
  **RP-12**. The production writer's own JNL-17 behaviour is still repeated as
  production-code evidence under MD-1. This restates MD-1 and makes no new
  deferral. The matrix intro records that the row's classification follows
  OP1-R2.
* **New RP-12 — a typed blocker.** It requires a bounded, reviewed `fsync`
  fault-injection producer and evidence contract. The contract must fix the
  following, at minimum:
  * the mechanism;
  * a scope confined to objects the producer creates under `R`;
  * the facsimile consumer and what it must record;
  * the pinned argv;
  * the reviewed cleanup and a read-only survey;
  * any package, module or device dependency. Such a dependency needs a
    separate maintainer decision and an amendment of §13.1.

  Package plan §4 names two candidate mechanisms, `dm-error` and an
  `LD_PRELOAD` interposer. The draft cites both and **chooses neither**.
* **New Band B4b** (§7.4b) holds typed placeholders only. The injection runs
  by `⟨MI.producer_argv.fsync_inject⟩`, the cleanup by `…fsync_cleanup` and
  the survey by `⟨RP-12.survey_argv⟩`. It states that only a new, explicit
  maintainer disposition naming the resulting residual may defer the work,
  and that **this draft makes none**.
* **Other places made consistent:**
  * AUTH-PRODUCERS and `MI.producer_argv.*`;
  * §10 item 8;
  * the §11.2 B4b stop row and §11.3;
  * §13.1 (two rows) and the new survey item B7-12;
  * the §14 handback section 6a;
  * §15, which now adds that success does not confirm A-5.0-5 component (k).

### 2.3 OP1-R3 — no executable evidence-capture method (Blocking)

* **The repository has no reviewed mechanism.** A search of `tools/`,
  `tests/` and `docs/` found `stdout_sha256`/`stderr_sha256` only in the draft
  and the Codex review. The harness's `capture.py` deliberately keeps no raw
  output. The client transcript is merged and may be truncated. The mechanism
  is therefore **new RP-11**, an unmet prerequisite that blocks A1 and every
  host command of B1 … B7. §4.2 now states that no authorization row is
  usable while RP-11 is unmet.
* **New §9.5 — the capture contract, as requirements C-1 … C-12:**

  | Item | Requirement |
  |---|---|
  | C-1 | exact command text and executed argv, including the shell-quoting case of §5 |
  | C-2 | separate, complete streams, with a declared maximum that stops rather than truncates |
  | C-3 | per-stream SHA-256 |
  | C-4 | client UTC bounds and exit status or signal |
  | C-5 | one durable record per act, with gap-free `capture_seq` and a capture index |
  | C-6 | location `⟨MI.capture_root⟩` on the repository host, outside the worktree and `/tmp`, absent before the pass, **nothing on `oracle-test`** |
  | C-7 | owner is the operator's account; `0700`/`0600`; immutable after writing |
  | C-8 | retained until post-execution review and a maintainer disposition; never committed |
  | C-9 | the redaction boundary: only digests and §12-safe excerpts are published; stop and notify on any unexpected secret |
  | C-10 | fail-closed: the act is `inconclusive`, the pass stops, nothing is re-issued, and an uncaptured host act is reported as such |
  | C-11 | the mechanism must not hide the §5 `rsync` from `guard-secrets.py`; a refusal is a stop |
  | C-12 | every handback row binds to its `capture_seq` and record digest |

* **Evidence fields reconciled.**
  * §9.3: `argv`, times, exit status and digests are taken **only** from the
    capture record. A missing field makes the act `inconclusive`, and the
    section states that neither pass is executable without RP-11.
  * §9.1: the capture records are the primary evidence. The transcript is
    demoted to a convenience that is "not evidence".
  * The §6.2 preamble, B2's expected-result paragraph, B6, §12 and §9.4 no
    longer rely on the transcript.
  * The §14 template's measured-facts table now carries `capture_seq`, the
    record digest and both stream digests, and states the capture root and
    index digest.
* **New maintainer input `MI.capture_root`**, a typed blocker. **New pin
  `PIN.capture_tool_sha256`**, unresolved. **New step A0-08**, the RP-11
  admission check. The §11.2 table gains an "every band" capture-failure row
  and an A0-08 stop.

### 2.4 Important corrections

1. **Pass A renamed** *synchronization plus read-only host preflight* in the
   header, §0, the §6 heading and the §6.2 heading.
   * §5, §6 and §13.1 state that `rsync --delete` is the **sole planned Pass A
     target mutation**, subject to AUTH-SYNC.
   * Incidental `sshd`/`sudo`/journald log entries are listed as side
     effects, not planned acts.
   * §5 adds that the synchronization is not executable until RP-11 states
     how it is captured without changing what the guard inspects.
2. **Placeholders kept as typed blockers.**
   * `MI.run_record_path` is now explicitly *"Unresolved: a typed blocker"*.
   * `MI.capture_root` and `MI.target_fact_statement` are added the same way.
   * No value was invented.
3. **MD-5 kept unmet.**
   * A-6 now requires a *durable, dated, independent acceptance record* that
     names the C-1 … C-4 corrections and the accepted `journal.py` digest. A
     maintainer statement, a green A0-06 or a matching A1-S2 is explicitly
     *not* that acceptance.
   * The same point is made in the §3 MD-5 row, at A0-06, at A1-S1, in the
     new A0-09, in §11.2 and in §15.
   * A1-S1 no longer claims to *"prove"* the bytes are *"reviewed"*. It now
     shows byte identity with the pinned tree only.
4. **Clean pin, digest and re-review.**
   * A-1 now requires acceptance of the exact amended bytes, a clean
     `⟨MI.pinned_commit⟩`, and the new manifest version and reviewed digest
     wherever a covered source changed. A review of `9bd4f5b5…` does not
     count.
   * §4.3 adds `⟨PIN.reviewed_digest_A⟩`, which equals `ac5ffb3c…` only if
     RP-11 touches no covered source. It records that the remediation did not
     re-derive the drafting-time pins.
   * The header and the closing reminder restate the requirement.
5. **Internal agreement.** The draft's §13.2 heading promised a *"Pass A
   subset"* survey that §6 never defined. A new read-only **A1-Z** step now
   defines it, repeating A1-19, A1-21 … A1-24 and, under AUTH-DBREAD,
   A1-29 … A1-33. §13.2 maps it to B7 rows, and §11.2 stops on an A1-Z
   difference.
   * The Pass B heading now reads RP-1 … RP-12.
   * B5 runs after B2–B4b.
   * The matrix intro states that RP-11 blocks every host-band row.

### 2.5 What was deliberately not changed

* MD-1 through MD-6, the §3 table apart from the MD-2 and MD-5 wording above,
  and the controlling-state paragraph.
* Band B6, which remains mandatory. The B6 changes add RP-11 capture only.
* The B5 rehearsals RR-11, RR-14 and RR-16, which remain mandatory.
* JNL-40(b)'s exclusion and `R-5.0-13`.
* RP-2 through RP-9, which are unchanged and not reduced.
* The feasibility/production-gate division, apart from row 40.

The review did not ask for row 39's split to change, so it stands as
drafted. RP-1 through RP-9 keep their numbers because the review and later
records cite them.

## 3. Unresolved prerequisites after this remediation

| Blocker | Kind | Blocks | What resolves it |
|---|---|---|---|
| RP-1 | source change (twelve facts) | B2 … B4 | a separate repository pass after RP-10, with a new manifest digest and re-review |
| **RP-10** | method plus maintainer ruling | RP-1, A1-C | a separately assigned pass proposing a provenance and verification method; Codex technical review; maintainer acceptance, or an explicit ruling where no sound method exists |
| **RP-11** | new mechanism | A1 and all host commands of B1 … B7 | a separately assigned implementation pass meeting §9.5 C-1 … C-12, including guard compatibility for §5, independently reviewed and pinned |
| **RP-12** | new producer and evidence contract | B4b; P5.0-R5 feasibility closure | a separately assigned pass choosing and bounding the mechanism, independently reviewed, and a maintainer decision if it needs a new package, module or device. The only alternative is a new explicit maintainer disposition naming the residual; this pass made none |
| RP-2 … RP-9 | as drafted | as drafted | as drafted |
| A-6 / MD-5 | independent acceptance record | every band beyond A0 | a dated independent acceptance of C-P5.0-R5-R1's C-1 … C-4 corrections |
| `MI.pinned_commit`, `MI.pinned_commit_B` | maintainer input | A0-02, B0 | a clean commit of the reviewed tree on a non-default branch |
| `MI.capture_root`, `MI.run_record_path`, `MI.target_fact_statement` | maintainer inputs; typed blockers | as §4.5 states | Codex-reviewed values; the last also needs RP-10 |
| the other §4.5 inputs | maintainer inputs | as drafted | as drafted |

Questions carried forward for Codex and the maintainer:

1. Is any RP-10 method technically sound for the ten E7 facts?
2. Should RP-11 be placed inside the covered harness sources? If so, it
   changes `PIN.reviewed_digest_A`.
3. Is the §4.7 rule, requirement 2 in particular, the right requirement?
4. The drafting-time proposals remain open: the 2 GiB floor, the 1 % B7
   tolerance, the 12 × 60 s reconnection bound, the timestamp format, and
   RP-2's facsimile-unit question.

## 4. Files read

* `CLAUDE.md`; `.agents/AGENTS.md` (complete).
* `docs/implementation-plan.md`: the reading map, §0, §16 and §20.
* `docs/review/Handover information` (current).
* `docs/operations/disposable-test-server.md`: the restriction banner, §§1–3.
* The remediation prompt and the Codex review, both in full.
* The authorization draft and its drafting handback, both in full. Their
  digests were verified against the review before editing.
* The MD-2 and MD-5 decision records.
* The accepted reconciliation handback: row 40, §3.9, §4 (A-5.0-5 components)
  and §5.
* The governing source passages:
  * `tools/phase_5_0_evidence/capability.py` (the `E7_TARGET_FACTS` block and
    its comment);
  * `case_runtime.py` (the interpreter target facts);
  * `concrete_plan.py` (the `P-05` and `P-06` refusal text, and C-S4-3);
  * `capture.py` (module docstring).
* `docs/review/phase-5-0-package-plan.md`, located passages only: the JNL-17
  table row, the §4 injection-candidates sentence, and the A-5.0-5 rows.
* Repository searches for existing stream-digest capture and `fsync`
  injection producers, read-only. Neither exists.

## 5. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | amended in place (§2) |
| `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | active assignment marked returned for Codex re-review, with pointers |
| `docs/project-management/status.md` | current status records the return |
| `docs/implementation-plan.md` | §20 current action points to the amended draft, this assignment, this handback and the required re-review |

Not changed: the drafting handback; the Codex review; the remediation prompt;
the disposable-server banner; the RAID, decision and change registers; any
source, test, hook, manifest, generated artifact, migration, schema or
configuration.

## 6. Validation performed

All checks were repository-local and documentation-only:

1. **Stale-claim search** of the amended draft for: *RP-1 input*, *Pass A's
   observations*, *from nothing else*, *can be admitted*, *immediately
   admissible*, *read-only preflight*, *RP-1 … RP-9*, *only in the client
   transcript*, *transcript (the primary*, *Flagged for Codex*,
   *production-gate. The mechanism*, *`P-02`/`identity`*, *proves the
   reviewed*, *the proof that*, and *admissible/executable once*.
   * Remaining hits are the new negations only, for example *"never an RP-1
     input"*.
   * One stale heading was fixed: §6.2's *"synchronization and read-only
     preflight"*.
   * One stale review-input item was fixed: §9.4's *"transcript excerpts"*.
2. **Relative links.** Every relative Markdown link in the changed files
   resolves (§6.1 below).
3. **`git diff --check`** limited to the five changed files (§6.1 below).
4. **Scoped diff inspection** and a pre-existing worktree survey (§7).

### 6.1 Results

Run after all edits to the five files:

* **Links.** A read-only Python script resolved every relative Markdown link
  (excluding URLs and in-page anchors) against each file's directory. Every
  file had 0 missing:

  | File | Relative links |
  |---|---|
  | the draft | 12 |
  | this handback | 3 |
  | `Handover information` | 6 |
  | `status.md` | 9 |
  | `implementation-plan.md` | 122 |

* **Tracked files.** `git diff --check` on the three tracked files printed no
  output and exited 0.
* **Untracked files.** `git diff --no-index --check /dev/null <file>` on the
  untracked draft and handback printed no output. Its exit status was 1,
  which `--no-index` also returns whenever the files differ, so it is not
  relied on. A direct search for trailing whitespace and tab characters in
  both files found 0 lines.
* **Scope.** These checks cover the handback bytes as they stood when the
  checks ran. This §6.1 edit added no link and no trailing whitespace.

## 7. Checks not run, and why

* Anything on `oracle-test`, including every command in the draft. This is
  prohibited, and the commands remain unexecuted by construction. Each
  expected output in the draft is a statement for review, not an observation.
* Test suites, the classifier tests named in A0-06, and the harness dry run.
  This was a documentation-only assignment, and the remediation prompt says
  not to run suites.
* Re-derivation of the §4.3 harness pins. They were not changed. §4.3 now
  says that this remediation did not re-derive them.
* A secrets scan (prohibited), and `python3 .claude/hooks/test_guards.py`
  (no guard was changed).
* Formatter, linter and type checker. No code was changed.

## 8. Git status relevant to this assignment

* Before this pass: 144 porcelain entries. The draft, the drafting handback,
  the Codex review and the remediation prompt were already untracked.
  `Handover information`, `status.md` and `implementation-plan.md` were
  already modified.
* After this pass: the same entries plus this new untracked handback.
* The three tracked files remain modified, with this pass's hunks added.
* No unrelated file was touched, and no pre-existing change was reverted or
  restored.
* Branch `docs/platform-plan`; `HEAD` `2fb1d6fd…` unchanged.

## 9. Security, data-authority and operational implications

* **Security.** The amendment only narrows the draft:
  * it adds three blockers and a capture contract that forbids target-side
    capture files;
  * it forbids hiding the `rsync` from the secrets guard;
  * it seals raw streams on the repository host and publishes only digests
    and safe excerpts.

  No new privileged path is proposed.
* **Data authority.** Unchanged. No production host, credential, Sheet or
  database is in scope. `freedom_test` and `freedom_dev` are never written.
* **Rollback and recovery.** New items cover RP-12's cleanup and the
  retention of capture records. The existing items are unchanged.
* **Reboot.** MD-3's B6 is unchanged apart from its capture requirement.

## 10. Proposed Codex re-review focus

1. RP-1, RP-10 and §4.7. Is the self-comparison fully removed, and does any
   remaining step still let an observation become an expectation?
2. Is A1-C safe to keep as a class of corroborative step, or should it be
   dropped?
3. Row 40 and RP-12. Is the reclassification complete, and is RP-12's minimum
   contract sufficient without choosing a mechanism?
4. §9.5 C-1 … C-12, in particular:
   * C-1's shell-quoting case;
   * C-6, the location outside the worktree;
   * C-9, the redaction boundary;
   * C-11, guard compatibility for §5.
5. MD-5 and A-6. Is the required independent-acceptance record correctly
   specified?
6. The consistency of the header, §4.2, §6, §8, §11, §13 and §14 with each
   other, including the new A1-Z.

Claude has stopped. The next action is Codex's independent technical,
security, operational and evidence re-review of the exact amended bytes. Only a
later explicit maintainer decision may accept and authorize any operational
pass.
