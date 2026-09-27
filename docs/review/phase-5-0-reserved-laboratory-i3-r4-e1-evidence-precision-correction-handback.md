# Claude correction handback — C-P5.0-LAB-I3-R4-E1, evidence precision — 2026-09-20

Authorization: **C-P5.0-LAB-I3-R4-E1**. Peter Duscha authorizes one bounded
**repository-documentation-only** correction to the evidence wording of the
C-P5.0-LAB-I3-R4 handback and the documents that restate it.

**This correction changes no result.** The C-P5.0-LAB-I3-R4 outcome stands as
Peter accepted it: the root invocation of the armed I3 verifier refused
admission with `target-mismatch` at exit `4`, **I3 remains unconfirmed and
unperformed**, and the `ubuntu` invocation was not run. No host action, no
`oracle-test` inspection, no deletion of the two `/tmp` capture files and no
I3 retry is authorized or was performed. No source, test, generated artifact,
review manifest or digest was touched.

---

## 1. What was wrong

The R4 handback and its downstream restatements asserted, in several places,
that "nothing was written on the host", that "the host is exactly as it was",
that "nothing was created" and that "the host was not mutated".

Those claims are broader than the evidence. They are true of the **verifier**
and false as statements about the **host**, because the same authorized pass
had two disclosed effects on the target:

1. the authorized §3.2 `rsync --delete` synchronization, which updated the
   remote **repository worktree** at `/opt/freedom-blades/platform`; and
2. the operator's stdout/stderr redirection, which created
   `/tmp/fb-i3-root.out` and `/tmp/fb-i3-root.err`.

Both were disclosed elsewhere in the same handback (§3 and §8), so this is an
imprecision in the summary claims, not a concealment. But a reviewer reading
only the banner would have been told something the body contradicts, and the
two `/tmp` files could have been mistaken for residue the verifier's cleanup
contract failed to remove. That is exactly the misreading the correction
removes.

A second error: §6 stated the invocation used "no wrapper". The reviewed
verifier **argv** was indeed unwrapped and unmodified, but it was carried to
the target inside an ordinary shell-level evidence-capture wrapper. The two
levels were collapsed into one claim.

## 2. What the corrected wording says

The governing phrase is now **"no verifier-controlled mutation occurred"**,
used in place of every broad claim, and never used to imply the two disclosed
effects away. Specifically, and everywhere:

- the I3 verifier **performed no controlled write and created no verifier
  object** — it refused in admission, before the first `openat`, `mkdirat` and
  `linkat`, before any context was entered;
- **synchronization updated the remote repository worktree** on `oracle-test`,
  as the authorization permits;
- **the operator's output redirection created the two `/tmp` files**; they are
  **evidence artifacts outside canonical `R` and outside the four publication
  directories, not verifier residue**; and
- no reviewed object — canonical `R`, the four publication directories, V1,
  V2, V3, V12, V4, V9, V5 or V7 — was created, removed or altered by anything
  in the pass.

## 3. The exact executed command

The R4 handback recorded the reviewed verifier argv but not the shell command
that carried it. The complete command has been **recovered verbatim from this
operator's own execution transcript** — it was not reconstructed, inferred or
guessed — and is now recorded in the corrected handback §6:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && date -u +'START %Y-%m-%dT%H:%M:%SZ' && sudo /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.i3_verifier_cli --arm-i3-controlled-write --identity root > /tmp/fb-i3-root.out 2>/tmp/fb-i3-root.err; echo \"EXIT=\$?\"; date -u +'END %Y-%m-%dT%H:%M:%SZ'; echo '=== STDOUT ==='; cat /tmp/fb-i3-root.out; echo '=== STDERR ==='; cat /tmp/fb-i3-root.err"
```

One line, 434 characters, reproduced with its SSH quoting, redirection and
exit-status capture exactly as issued. The escaped `\"EXIT=\$?\"` defers `$?`
to the remote shell, so the reported status is the verifier's own. Its
captured transcript output was `START 2026-09-20T13:14:44Z`, `EXIT=4`,
`END 2026-09-20T13:14:45Z`, followed by the stdout and stderr already quoted
in the handback.

Because the exact command was recovered, the fallback limitation the
authorization provided for does not apply and is not claimed. The recovery
read only this operator's local execution transcript; it involved no access to
`oracle-test`.

### 3.1 A discrepancy flagged, not rewritten

While recovering the command from the same transcript, one figure in the
accepted R4 §3 was found not to reproduce. The handback states "52 paths
transferred"; the recorded `rsync` output lists **54 entries — 45 files and 9
directories**. The three byte figures (`sent 372,553`, `received 33,273`,
`total size is 73,348,693`) reproduce exactly, as does the file list, which
contains no secret-type file.

This authorization covers wording, not the accepted R4 figures, and the count
bears on no result. The figure is therefore **left as accepted** and the
discrepancy is flagged inline in §3 and here for the reviewer to dispose of.
Nothing was reconstructed or substituted.

### 3.2 The two levels

The distinction the corrected §6 now draws:

| Level | What it is | Status |
|---|---|---|
| Verifier argv | `sudo …/python -m …i3_verifier_cli --arm-i3-controlled-write --identity root` | Exactly the reviewed, authorized invocation: no added flags, no ad hoc script, no re-implementation, no substituted probe |
| Shell wrapper | `ssh`, `cd`, `date -u`, `>`/`2>` redirection, `EXIT=$?`, `cat` | Ordinary operator evidence capture. Adds nothing to the verifier's behaviour; created the two `/tmp` files |

## 4. Files changed

All changes are repository documentation. No source, test, generated artifact,
manifest or digest was touched.

| File | Change |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-i3-r4-e1-evidence-precision-correction-handback.md` | **New.** This handback |
| `docs/review/phase-5-0-reserved-laboratory-i3-r4-controlled-write-blocker-handback.md` | Prominent erratum block at the top; corrected result banner; §3 synchronization-effect disclosure; §6 two-level distinction and the verbatim command; §8 residue wording and the not-residue statement for the two `/tmp` files; §12 rollback wording |
| `docs/review/Handover information` | Correction pointer and banner at the top; the R4 banner's broad claim replaced |
| `docs/operations/disposable-test-server.md` | Current restriction banner reworded; restriction itself unchanged |
| `docs/implementation-plan.md` | §20 current action reworded |
| `docs/project-management/status.md` | Current status reworded |
| `docs/project-management/raid-register.md` | LAB-I3-TARGET-1 impact wording; the item stays Open, Blocking |
| `docs/project-management/decision-register.md` | Open target-identity decision wording; the decision stays open and unchosen |
| `docs/project-management/change-log.md` | New append-only entry **C-P5.0-LAB-I3-R4-E1**; the R4 and R4-H1 entries are left as written |

`git diff --check` is clean. The earlier-pass and reviewer-authored
working-tree changes were preserved untouched.

## 5. Checks not run, and why

| Check | Why not |
|---|---|
| Any `oracle-test` access — SSH, synchronization, inspection | Explicitly excluded by this authorization |
| Deletion of `/tmp/fb-i3-root.out` and `/tmp/fb-i3-root.err` | Explicitly excluded; the files remain in place for independent inspection |
| Any I3 retry or verifier invocation | Explicitly excluded; I3 remains unperformed and the R4 authority is consumed |
| Test suites, formatter, linter, type checker | No source, test or artifact changed; this is a documentation-only correction, and no suite figure is cited or claimed |
| Artifact or digest regeneration | Explicitly excluded; the accepted review-input digest `be9e110f…` is untouched |

## 6. Resulting state

Unchanged by this correction, and restated for the record:

- **I3 is unconfirmed and was not performed.** No controlled write occurred
  and the four publication contexts were not exercised;
- Peter accepted the R4 fail-closed result; this correction concerns evidence
  precision only and does not revisit that acceptance;
- C-P5.0-LAB-I3-R4 remains **consumed**; no retry is authorized;
- the target-identity decision (RAID LAB-I3-TARGET-1, decision register)
  remains **open and unchosen**, with the three options recorded in the R4
  handback §10;
- V7 remains excluded and absent; `plan.is_executable = False`; V8 and V10
  remain unperformed; Package 5.0 remains **not ready**;
- LAB-SECRETS-1 remains Open, Low; LAB-V6-P2 remains deferred; and
- the review-input digest remains `be9e110f…`, which is not an approval and is
  not authority for `--execute`.

## 7. Reviewer focus areas

1. whether "no verifier-controlled mutation occurred" is the right governing
   phrase, and whether it is used consistently across all seven reconciled
   documents without implicitly excluding the two disclosed effects;
2. whether treating the two `/tmp` files as operator evidence artifacts rather
   than verifier residue is correct — they lie outside canonical `R` and the
   four publication directories, and were created by the wrapper's
   redirection, not by the verifier;
3. whether the §3.2 argv/wrapper distinction is drawn correctly, and whether
   the recorded command is accepted as the verbatim executed command given
   that it comes from the operator's execution transcript;
4. whether the append-only change-log correction entry is the right form, the
   historical R4 and R4-H1 entries having been left unrewritten; and
5. **the §3.1 discrepancy** — the accepted R4 §3 "52 paths" figure against the
   recorded 54 entries (45 files, 9 directories) — which is flagged and left
   as accepted rather than rewritten, and needs a reviewer disposition.

**Unresolved question:** none introduced. The §10 target-identity decision
remains the single open decision, and this correction does not touch it.

Returned for independent Codex review. **Nothing in this handback closes a
finding, accepts a risk, approves a digest, advances a gate or authorizes a
host action.**
