# Handback — OH-S3 R2 remediation: `HARD STOP: concrete Route 3 not established`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R2-20261007-02`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-claude-prompt.md),
**13180 bytes, SHA-256
`c79b320e1afdf737699db19283b552fb66982bbd136c9c1d5b588fe1aa52b5a2`**, recomputed
with `wc -c` and `sha256sum` before any edit and again at handback, and equal to
the pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r2-remediation-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-proposal.md).

## 1. Terminal state

**`HARD STOP: concrete Route 3 not established`.** The prompt identity matched, so
the identity hard stop did not arise. The conditional hard stop that both the R1
prompt and the R2 prompt define **does** arise: repository evidence does not
suffice to define a Python-free, dynamic-loader-free root path without inventing
facts. The proposal names four gaps (proposal §9.3):

1. **Interface contract.** The root helpers delegate six functions to distribution
   binaries (unit-state reads, transient holder creation, backstop creation, timer
   disarm, the Polkit decision, the authorization subject). The accepted R2 record
   cites systemd and polkit **server-side** behaviour and `pkcheck`'s exit statuses.
   No accepted record cites a client-side contract by which a static image would do
   the same. A fixed-string count of SASL, marshalling, wire format, wire protocol,
   the private systemd socket and the system-bus socket over the R2 record, the
   one-host design, D2 and the R3 proposal returned one hit (TR-4's mention of the
   system-bus socket path).
2. **Proof method.** D2 and D9 proved the closed nine-call launcher, and R2
   refuted AD-8 as a general statement, establishing it only for that closed
   inventory. A root image needs a larger inventory with no cited blocking or
   `EINTR` behaviour.
3. **Boundary.** Procedures that `sudo` starts (`attest`, the installer class) pass
   through dynamic root processes before any image the procedure controls. That is
   a boundary statement for a maintainer (BQ-2, BQ-3), not evidence.
4. **Size and reading.** No accepted measure of the work exists, and the accepted
   wording (DR1 §5.3) is wider than the assignment's restatement (BQ-1).

This is **not** a finding that a literal Route 3 is impossible. The cumulative
document preserves the repaired activation design and returns the exact bounded
alternatives and the exact work that would make a literal Route 3 decision-ready.
**Nothing is accepted by this return.** I have not claimed Codex's or Peter's
acceptance, have not proposed any successor for activation, have made no scope
decision, and have created no authority.

## 2. Findings remediated

| Finding | Remediation | Proposal |
|---|---|---|
| **R2-F1**: RT3-A does not satisfy the authorized Route 3 boundary | R1 preserved unchanged; the statement that RT3-A did not meet the boundary; the accepted Route 3 meaning restored (the root procedures that touch the grant and activation mechanism do not run through CPython or a dynamic loader), with R3-ROOT and the wider DR1 wording both stated and neither decided; RT3-A kept only as `STATIC-SCRUB-WRAPPER` (SSW), a scope-change alternative that is not Route 3 and needs a §0.2 decision first; R1's DEC-1 withdrawn; BC-1 … BC-5 separate from the decisions; the Role A–H inventory, PO-12′, PO-19, MF-1 … MF-8, the OH-S4 / OH-S4p split, the rebuild chain, the PO-17 boundary, the surface comparison and the successor order re-evaluated per alternative; root-owned dynamic inputs stated to remain inputs | §0.1, §9, §10, §11, §12.2 |
| **R2-F2**: claimed cleanup bounds contain unbounded local work | the elapsed-time claims about CL and IGR withdrawn (and the same defect in the accepted design reported); deadline classes E, M, C, X; an inventory of every potentially blocking operation in ACT, CP, IGR, CL, the backstop and verification; terminators per procedure; sizing rules N1 … N4 as necessary conditions that are never recorded as bounds; signal discipline SG-1 … SG-8 (handlers installed before any state, flag-only, sliced waits, one IGR site with a latch, a second signal idempotent); GRR and CL-G, with the removal path tmpfs-only and before every `ext4` write; interruption maps for CL (L0 … L9), IGR, CP, the backstop and the holder; PO-11 (d′) retained with every operational timeout failing closed | §4, §5, §7, §8, Appendices A and B |

The proposal's Appendix D maps every numbered item of both findings to its closing
section.

## 3. Result in brief

* **The safety kernel is unchanged.** G1 … G5 never cited the lock, the hold loop,
  `ExecStopPost=`, the backstop, any polling bound or any elapsed time (proposal §2),
  so neither finding touches them. They are conditional on a helper-start contract
  RH-1 … RH-3 that the eventual Route 3 outcome must discharge; X-1 stays open for
  the root roles.
* **R1's bounds were unsupported and are withdrawn** (proposal §7.7, W-1 … W-11),
  including the accepted design's own sentence that CL-0 … CL-3 are "local operations
  bounded by S". The S grammar's 30 seconds is now the parameter ρ, named as an
  expectation.
* **A probable defect in the accepted backstop literal.** For a `Type=exec` service
  the start timeout would end at `execve`, so a started backstop firing would have
  no PID-1 bound and a hung one would block every later firing (the timer does not
  re-arm while its service is active [R2 §8 (j)]). The `Type=exec` start-completion
  behaviour is **proposed for citation**, not cited. The proposal adds a
  PID-1-enforced `RuntimeMaxSec=` (BS-RM) as DEC-2's correction.
* **Two design improvements are offered, not imposed:** one shared grant-release
  routine (GRR) used by the holder's inline release and by CL's first act, and a
  root-only `grant.id` so that those rungs do not read an `ubuntu`-owned `ext4`
  journal (DEC-3, with a bounded alternative).
* **Route 3:** six exact alternatives (LIT-FULL, LIT-DR1, WITHDRAW, SSW, SCDC,
  ACCEPT-X1), of which only the first three meet the accepted boundary and none of
  those is decision-ready except WITHDRAW; nine work packages (WP-1 … WP-9) that
  would make a literal Route 3 decision-ready; no recommendation among them.
* **Decisions are split:** six that Peter may make after a clean review (DEC-1 …
  DEC-6), and five boundary changes (BC-1 … BC-5) that need §0.2 change control and
  cannot be made by accepting the proposal.

## 4. Files changed

**Created** (untracked):

* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-proposal.md`
* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-handback.md` (this file)

**Updated, current-state pointers only** (tracked; the OH-S3 R2 paragraph changed
from "authorized and unexecuted" to "executed, hard stop", the authority and prompt
relabelled *Consumed*, proposal and handback links added):

* `docs/review/Handover information`
* `docs/project-management/status.md`
* `docs/implementation-plan.md`, §20 only
* `docs/operations/disposable-test-server.md`, the restriction banner only

**Pre-existing worktree changes.** Before my first edit `git status --short`
showed six modified tracked files (the four pointers above, plus
`docs/project-management/change-log.md` and `docs/project-management/decision-register.md`)
and six untracked files (the R1 prompt, handback, proposal and authority, and this
assignment's prompt and authority). All were left by earlier work. The four
pointers already carried the uncommitted "OH-S3 R2 authorized" text, which I edited
in place and otherwise preserved. **I did not touch** `change-log.md`,
`decision-register.md`, the R1 files, this assignment's prompt or its authority.

**Not edited:** R1 (proposal, handback, prompt, authority), any accepted historical
evidence, the operational draft, any source, test, configuration, service file or
migration, any archive snapshot or archive index, the decision register and the
change log. The SHA-256 of the R1 proposal, the R1 handback, the R1 prompt, the R1
authority, the accepted R2 record, the one-host design and the operational draft
were recorded before the first edit and compared again at the end (§8).

## 5. Repository documents consulted

**Read completely:** `.agents/AGENTS.md`; this assignment's prompt and authority;
the R1 prompt, the R1 authority, the complete R1 proposal and the complete R1
handback; the OH-S2 R2 acceptance; the OH-S2 R2 handback; the R3 H-0 completeness
acceptance; `docs/review/Handover information`; the pointer sections of
`status.md`, `disposable-test-server.md` (the restriction banner) and
`implementation-plan.md` §20.

**Read by section:** `docs/implementation-plan.md` (reading map; §0.1 … 0.5; §14.1
… 14.3; §16; §17; §20). The accepted R2 citation record
`phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`: §0.1 … 0.2, §6.3 … 6.4, §7, §8,
§10.4 … 10.5, §11.6, §12.9, §14.3 … 14.4, §15.4 … 15.5, §16, the section headings,
and fixed-string searches elsewhere. DR1
`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md` §5.3 … 5.5 and the
accepted R3 proposal `phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md`
§6.3 … 6.5. The one-host design
`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`: §4.1.3
(the trust table), D3-R2 (d) … (l) in full, D3-R5 (e) and (i), and fixed searches for
the interpreter literal, `systemctl`, `pkcheck` and `systemd-run`. The C11 proposal
`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md` and the D2 proposal
`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md` (the lines the
design and R1 cite, and D2's header). The operational draft
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` (headings, and fixed
searches for elapsed-time language, `PIN.interpreter` and the §9.5.3 and C-15
anchors; **not edited**). The Role A literals' lines in
`infra/rp11-launch/launch.c`, `tools/phase_5_0_evidence/rp11_launch.py` and
`docs/review/phase-5-0-evidence-harness-review-manifest.json`, by fixed search.

**Carried from R1 without re-reading the underlying source:** the Role A line
references in C11 and D2 and in the design at `:2481`, `:5242` and `:6979`, and the
launcher build description (§9.7, §9.11). The proposal says so (§1.1). The lines I
re-checked by fixed search agree with R1's.

## 6. Commands and checks run

Every command named exact files, or the documents of one named directory. None was
recursive over the repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command or tool (targets) | Result |
|---|---|---|
| 1 | `wc -c`, `sha256sum` on the prompt; `cat` of the authority | `13180`; `c79b320e…b5a2`: **equal** |
| 2 | `git status --short` | six modified tracked files, six untracked: all pre-existing (§4) |
| 3 | file reads of the documents in §5, by named path and line range | read as listed |
| 4 | `sha256sum` of seven named files (R1 proposal, handback, prompt, authority; R2 record; one-host design; operational draft), saved to a scratchpad file | recorded before the first edit |
| 5 | `grep -n`, `grep -c`, `sed -n` on named documents, for headings, the interpreter literal, `systemctl`, `pkcheck`, `systemd-run`, the D-Bus-related terms, elapsed-time language and `PIN.interpreter` | locations and counts as cited in the proposal |
| 6 | `python3 -I` on helper scripts that check Markdown table row widths, repository-relative links and section references | see §8 |
| 7 | assembly of the proposal: part files written to the session scratchpad, concatenated with `cat` into the deliverable (no copy of any repository file was made), then edited with exact-count `python3 -I` replacements | applied |
| 8 | exact-count `python3 -I` replacements in the four pointer files | applied. **One mistake, repaired:** my first replacement in `Handover information` found the wrong anchor and left a duplicated paragraph; I detected it from the printed output, removed exactly the duplicate and the superseded paragraph, and re-inspected the result and the diff hunks |
| 9 | the final checks of §8 | see §8 |

**Disclosed deviations from "named documents only".** Two reads went beyond a
single named document, both inside the one documentation directory `docs/review/`
and neither recursive, as R1 also disclosed: (a) `ls` of that directory filtered by
name with `grep -i`, to find the acceptance, one-host and OH-S3 files; and (b) one
fixed-string `grep -ln "Route 3"` over that directory's `*.md` glob, to find every
document that uses the term. No secret-bearing path is in that directory and none was
opened by name.

**Scratchpad files.** Helper scripts `tablecheck.py` and `links.py`, a baseline
digest file and the proposal's part files were written to this session's scratchpad
directory (outside the repository). They read only the named files, are not
deliverables, and were left in place. I took no cleanup action.

**No guard refusal occurred.** `.claude/hooks/guard-secrets.py` and `guard-git.py`
refused nothing, and no command text contained a secret-bearing file name pattern.

## 7. Checks not run, and why

* No SSH or other host connection, `oracle-test`, production, staging, Foundry or
  database access, and no retained-evidence access: forbidden.
* No application test, hook test (`python3 .claude/hooks/test_guards.py`),
  formatter, build, package tool, network check or remote-host check: forbidden, and
  this is a documentation slice. `run-suites` does not apply.
* No citation, observation or measurement of any host behaviour. Every new
  host-behaviour statement in the proposal is a **proposed** obligation (proposal
  §13.2), including the `Type=exec` start-completion behaviour behind BS-RM and the
  CPython 3.14.4 signal-handler timing behind SG-1 … SG-8.
* No re-verification of R2's source citations: re-retrieval is forbidden, and the
  record is accepted.
* No byte-level inspection of any launcher image. PO-17 stays unevaluated.
* No network research. No third-party artifact was selected.
* **No measurement of the size or effort of a Python-free root path.** That is WP-7.

## 8. Final checks

Run after every deliverable and pointer edit was written. All operated on the six
allowed files, listed explicitly.

| Check | Result |
|---|---|
| Prompt identity, re-checked at handback | `13180`; `c79b320e…b5a2`: **equal** |
| Unchanged inputs | SHA-256 of the R1 proposal, R1 handback, R1 prompt, R1 authority, the R2 record, the one-host design and the operational draft equal to the values recorded before the first edit (see the closing record below) |
| Required-term scan of the proposal | `R2-F1`, `R2-F2`, DR1's wording of Route 3, MF-1 … MF-8, PO-12′, PO-19, PO-17, OH-S4p, OH-S5, H-1 readiness, operational-draft incorporation, Route 3 implementation, read-only MF collection and byte-level review all present |
| Carried identifiers against R1, and against the accepted R2 record by exact named-file search | every carried identifier (PO-20 (f), PO-21 (c), (s), (u), PO-11 (d), PO-12, AS-8, PO-19, PO-17, X-1, CL-21i, MF-1 … MF-8, D9-1, AD-8, LD-1 … 9, RL-0 … 5, IGR, PK/2, BSP, SD-1, HB-1, INV-15, the NT families) occurs in the proposal. The identifiers that belong to the one-host design rather than to the R2 record (CQ, SB, OS, CX, AM, GP-R3, G-R1) occur in R1 and in the proposal and not in the R2 record, as expected. PO-21 (u) is row (u) of the R2 record's §8 table |
| No formula claims to bound a component described as unbounded | the only formulas with a time bound are N1 … N4 (necessary conditions, stated as such, with ρ named an expectation) and the E-class waits. Every occurrence of "within about", "by the S grammar", "bounded by S", "< S", "cannot be starved", "R + S" and "ten seconds" is a quotation of a withdrawn claim (§7.7) or the NT-DL-4 scan target |
| No SSW, SCDC or ACCEPT-X1 described as satisfying literal Route 3 | each is marked "no" in §9.4 and §9.13, and §9.4 states in terms that none is described as satisfying it |
| Markdown table row widths, both deliverables | see the closing record |
| Trailing whitespace, six files | see the closing record |
| Repository-relative links, six files | see the closing record |
| `git diff --check`, four tracked pointers and two new deliverables | see the closing record |
| Six-file diff review | the four pointers differ from their pre-start state only by the heading, one replaced paragraph, the relabelled authority and prompt links, and the added proposal and handback links; the diff hunks lie only in the pointer areas. The two deliverables are new files. The authority-language scan found no host, implementation, successor, cleanup, credential, secret, commit or push authority granted or implied: every occurrence of "authoriz…" states that nothing is authorized, names a design object (for example *not authorized*, PK's result), or refers to a future A-2 or separately authorized slice |

## 9. Security implications

* **No new attack surface is created by this return.** It is documentation.
* **What the proposal changes, if accepted later:** the lock moves to a root-only
  object with a root-only identity file; every wait has a deadline of a stated class
  and a fail-closed consequence; signal handlers only set a flag and are installed
  before any state exists; the inline release and CL's first act share one
  tmpfs-only removal routine. Each change fails closed to "no pass".
* **What it does not close, stated by name** (proposal §13.1): **X-1** for the root
  roles, until a Route 3 outcome exists; RO-1 (uncatchable holder end with PID 1
  unable to spawn the stop-post and the backstop); RO-2; RO-3; the new RO-4 (IGR not
  completed), RO-5 (an unbounded backstop firing, closed by BS-RM if accepted) and
  RO-6 (a persistent filesystem or kernel stall); CX-5; HB-1.
* **Elapsed-time honesty.** After this return no statement implies a time for a
  class-X operation, and the sizing rules are necessary conditions only. That is a
  correction of an overstatement, not a new weakness: the grant boundary never
  depended on those times.
* **Route 3 is not established.** Until it is, the accepted disposition stands:
  Route 1 returns to Route 3 design review, PO-12 and AS-8 are refuted, and PO-19
  stays not established.
* **No secret, credential or player datum was read**, and no secret-bearing path was
  opened or named.

## 10. Unresolved decisions

* **For Peter, only after a clean independent review** (proposal §12.1): DEC-1 which
  PO-21 (c) residual to accept (RO-1 recommended; ALT-SENT the alternative); DEC-2
  the operational parameters and BS-RM; DEC-3 the lock and identity objects (K with
  `grant.id` recommended); DEC-4 MF-3's observing slice; DEC-5 CX-4's retirement;
  DEC-6 the signal and removal discipline.
* **Route 3 direction** (G-1b, proposal §11): commission WP-1 … WP-7 (or WP-8), or
  open a §0.2 change request for a scope-change alternative, or WITHDRAW. **Not a DEC
  and not a consequence of accepting the proposal.**
* **Boundary changes needing §0.2** (proposal §12.2): BC-1 … BC-5.
* **Boundary questions** for the first work package: BQ-1 … BQ-4 (proposal §9.3).
* No other accepted decision is changed: OH-D-1 … OH-D-10, OS-6, U-9's text, M-B, M-S
  and the R2 dispositions stand.

## 11. Proposed independent-review focus

The fourteen questions of proposal §14.1, in particular: (1) whether the safety
kernel really cites no lock, timing or elapsed time, and whether G1 … G5 should be
stated as conditional on RH; (5) whether any statement still implies an elapsed time
for a class-X operation, whether the §7.3 inventory is complete, whether BS-RM's
reading of `Type=exec` is right, and whether the signal discipline and interruption
maps are complete; (6) whether R3-ROOT is the right working boundary; (7) whether the
hard stop is justified or repository evidence for a loader-free interface or a static
proof method was missed; (8) whether SSW is nowhere described as satisfying Route 3;
(10) the Role A–H inventory and the per-alternative PO-12′ and PO-19 narrowing;
(13) the successor order; and (14) whether any DEC smuggles in a scope change. The
claims that need independent **security** re-review are listed in proposal §14.2
(SR-1 … SR-11).

## 12. Confirmation

I confirm that **no** host connection, `oracle-test` or production access, Foundry
or database access, retained-evidence access, secret, credential or player-data
access, network research, package operation, implementation or configuration edit,
launcher retarget or rebuild, application or hook test, formatter, build, service or
database mutation, repository or host cleanup, workspace recreation, OH-S4/OH-S4p or
later slice, H-1/H-2, activation, rollback, commit or push occurred.

## 13. Closing record of the final repository checks

| Check | Result |
|---|---|
| Prompt identity, last run | `13180`; `c79b320e…b5a2`: equal |
| Unchanged inputs: R1 proposal, R1 handback, R1 prompt, R1 authority, the accepted R2 record, the one-host design, the operational draft | `sha256sum -c` against the digests taken before the first edit: **7 of 7 OK** |
| Trailing whitespace, six files | 0 lines in each |
| Link check, six files: the 68 distinct targets were listed first and seen to be project documentation only, then tested for existence | 99 links checked, **0 broken** |
| Markdown table row widths | proposal: 62 tables, 0 mismatches; handback: 4 tables, 0 mismatches |
| `git diff --check`, four tracked pointers | exit 0, no output |
| `git diff --check --no-index`, the two new deliverables | exit 1 (differences exist) and **no whitespace error reported** |
| Size of the proposal | 2,576 lines, 221,333 bytes |

HARD STOP: concrete Route 3 not established; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.
