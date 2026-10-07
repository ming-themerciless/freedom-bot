# Handback — OH-S3 R1 design remediation: `OH-S3 R1 DESIGN REMEDIATION READY FOR REVIEW`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R1-20261007-01`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-claude-prompt.md),
**9693 bytes, SHA-256
`8e4d2a95092b15aec184b7099716fd9f6f56d4a3695aa8e70bc58188bf2b8c00`**, recomputed
with `wc -c` and `sha256sum` before any edit and again at handback, and equal to
the pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r1-design-remediation-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-proposal.md).

## 1. Terminal state

**`OH-S3 R1 DESIGN REMEDIATION READY FOR REVIEW`.** No `HARD STOP` arose. The
prompt identity matched. Repository evidence was sufficient to specify a concrete
Route 3 (the accepted launcher chain already exists and is reused in method), so
the conditional Route 3 `HARD STOP` did not apply. Two things are not decided by
evidence and are returned as decisions: the Route 3 choice (DEC-1) and the
operational timeout values (DEC-3).

**Nothing is accepted by this return.** I have not claimed Codex's or Peter's
acceptance, have not proposed any successor for activation, and have created no
authority. Independent Codex review and Peter's later recorded decision are
mandatory.

## 2. Requirements covered

| Prompt requirement | Where |
|---|---|
| A.1 PO-20(f): last-reference rule, descriptor ownership, inheritance prevention, close points, failure behavior | proposal §4 (LD-1 … LD-9, PO-20 (f′)) |
| A.2 PO-21(c): no every-cause claim; independent recovery and backstop; the failure outside the guarantee | §5 (RL-0 … RL-5, IGR, IL, RO-1 … RO-3, PO-21 (c′)) |
| A.3 PO-21(s): a valid discriminator; attempts, inactive and failed states, `reset-failed`, reload and re-exec, same-microsecond observations | §6 (SD-1, BSP, handling table, PO-21 (s′), CX-4 void) |
| A.4 PO-11(d): finite, fail-closed `ACT`, consume, `DEACT`, backstop and verification; operational timeout separated from Polkit internals | §7 (PK/2, parameters and arithmetic, PO-11 (d′)) |
| A. revised state machines, terminal-cause tables, authority windows, recovery ownership, evidence records, invariants | §§5.5, 6.5, 8.1 … 8.6 |
| A. negative tests | §§4.10, 5.10, 6.10, 7.9, 8.7, 9.13 |
| A. exact amendments in the one-host design and the operational draft | Appendix A (30 rows), Appendix B (10 rows) |
| A. whether any accepted decision needs Peter to choose; recommendation and bounded alternatives | §12 (DEC-1 … DEC-6) |
| B.1 executable and runtime boundary for the entry, consume helper, holder, `ExecStopPost=` helper and backstop | §9.4 |
| B.2 every Role A–H occurrence and its Route 3 disposition | §9.6 |
| B.3 reproducible source, build, pinning, digest, ownership, installation, update, rollback and drift contracts, none performed | §9.7 |
| B.4 C11, D9 and I-7 preserved; every claim needing re-review | §9.8 |
| B.5 PO-12′ and PO-19 decided and narrowed to their consumers | §9.9 |
| B.6 byte-level PO-17 and OH-S4p boundary for the proposed launcher image | §9.10 |
| B.7 failure and recovery for missing, altered, wrongly owned or incompatible artifacts | §9.11 |
| B.8 comparison with a bounded alternative and the surface argument | §§9.2, 9.12 |
| MF-1 … MF-8 disposition, observing slice, privilege, path scope, evidence, drift trigger, dependent gate | §10 |
| successor order and review gates, none authorized by naming | §11 |
| two deliverables and four pointers, authority and prompt marked consumed | this file, the proposal, §4 below |

## 3. Result in brief

* **The four returned items are repairable without touching the safety kernel.**
  The grant boundary and the one-start-attempt contract rest on the claim, PID 1's
  inactive-entry record, the rule token and CP's journaled removal and *not
  authorized* check. None of those proofs cites the lock, the hold loop,
  `ExecStopPost=`, the backstop or a Polkit latency (proposal §2). Each repair
  tightens machinery around that kernel and fails closed to "no pass".
* **PO-20 (f):** a root-only lock object, one owner per open file description, no
  inheritance, explicit close points, a monotonic wait shorter than the stop
  timeout, and grant removal that never waits for the lock.
* **PO-21 (c):** a recovery ladder whose first rung, an inline release inside the
  dying holder, needs no spawn. A live rule without a live holder is shown inert.
  One residual (RO-1) stays outside the guarantee.
* **PO-21 (s):** inequality with a baseline separated from the monotonic clock, no
  strictness, explicit handling of every named event; **CX-4 is void** under the
  accepted R2 evidence for PO-21 (u) (retirement is DEC-6).
* **PO-11 (d):** no bound is claimed; an operational timeout family with
  `unconfirmed` failing closed everywhere; no unbounded poll.
* **Route 3 (RT3-A, recommended):** a static, environment-ignoring first image,
  `rp11-rootexec`, in front of the four unit-run roles and `attest`, built by the
  already accepted reproducible chain; the entry launcher changes by one literal.
  PO-12′ and PO-19 remain necessary, narrowed to root-owned *file* inputs. RT3-B
  (Python-free root path), RT3-Z (accept the residual) and four rejected routes
  are compared.
* **MF-1 … MF-8:** none eliminated; MF-1 and MF-2 narrowed; MF-4's consumer set
  moves; five unchanged. A staged successor order with gates is proposed
  (decisions, citation addendum, operational-draft incorporation, design-amendment
  application, Route 3 implementation, byte-level launcher review, independent
  rebuild, read-only MF collection, citation closure, H-1 readiness). **None is
  authorized.**

## 4. Files changed

**Created** (untracked):

* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-proposal.md`
* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-handback.md` (this file)

**Updated, current-state pointers only** (tracked; additive: heading and one
paragraph set to "returned for review", the authority and prompt relabelled
*Consumed*, proposal and handback links added):

* `docs/review/Handover information`
* `docs/project-management/status.md`
* `docs/implementation-plan.md`, §20 only
* `docs/operations/disposable-test-server.md`, the restriction banner only

**Pre-existing worktree changes.** Before my first edit `git status --short`
showed six modified tracked files (the four pointers above, plus
`docs/project-management/change-log.md` and
`docs/project-management/decision-register.md`) and two untracked files (this
assignment's prompt and authority). All were left by earlier work. The four
pointers already carried the uncommitted "OH-S3 R1 authorized" text, which I
edited in place and otherwise preserved. **I did not touch** `change-log.md`,
`decision-register.md`, the prompt or the authority.

**Not edited:** any accepted historical evidence, the operational draft, any
source, test, configuration, service file or migration, any archive snapshot or
archive index, the decision register and the change log.

## 5. Repository documents consulted

Read in full: `.agents/AGENTS.md`; the prompt; the authority; the R2 acceptance;
the R2 handback; the R3 acceptance; the R1-F1 residual-risk acceptance; the
H-0 and U-9 acceptance; `docs/review/Handover information`; the pointer sections
of `status.md`, `disposable-test-server.md` and `implementation-plan.md` §20.

Read by section: `docs/implementation-plan.md` (reading map, §§0, 14, 16, 17, 20);
the accepted R2 citation record `phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`
(§§R2-0 … R2-6 and §§0 … 16; the appendices only by heading); the one-host design
`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`
(header, §0-R6, §§4.1.1 … 4.1.5, 4.2.1 … 4.2.5-R6 in full, 4.4.1 … 4.4.3, 4.5,
4.7.1, 4.7.4, and a fixed search for every lock and interpreter occurrence); the
accepted R3 proposal `phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md`
(§§6, 13, 14, 15, 16) and DR1 `phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md`
(§§5.3 … 5.6) for Route 3's definition; the C11 proposal `phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`
and the D2 proposal `phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`
(headings, and D2 §§5.1, 5.5 … 5.8, 6.1 … 6.3, plus fixed searches for the
interpreter literal); the operational draft
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` (headings, §3, §4.1,
§4.5, §9.5.3 and fixed searches; **not edited**).

Tracked, non-secret launcher files: `infra/rp11-launch/launch.c` (lines 195 … 224),
`start.s`, `select.h`, `rp11-launch.ld`, `build.sh` (lines 1 … 80),
`toolchain.lock` and `expected.sha256` (line counts and structure),
`rp11-launch.x86_64.listing` lines 410 … 414; fixed searches of
`tools/phase_5_0_evidence/rp11_launch.py`, `infra/rp11-launch/verify/ctverify.py`,
`tests/test_rp11_launch_source.py` and
`docs/review/phase-5-0-evidence-harness-review-manifest.json` for the interpreter
literal.

## 6. Commands and checks run

Every command named exact files, or one named directory. None was recursive over
the repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command or tool (targets) | Result |
|---|---|---|
| 1 | `wc -c`, `sha256sum` on the prompt | `9693`; `8e4d2a95…8c00`: **equal** to the authority |
| 2 | `git status --short` | six modified tracked files, two untracked: all pre-existing (§4) |
| 3 | file reads of the documents in §5, by named path and line range | read as listed |
| 4 | `grep -n '^## \|^### '` on four named records (R2 record, design, R3 proposal, C11 and D2 proposals) | headings located |
| 5 | `grep -n` for `python3.12` and `python3.14` on the named design, C11, D2, `launch.c`, `rp11_launch.py`, `ctverify.py`, `tests/test_rp11_launch_source.py` and the manifest; two `sed -n` and `grep -n` reads of the listing | the Role A … E line numbers of proposal §9.6 |
| 6 | `wc -l`, `cat`, `sed -n` on the named `infra/rp11-launch/` files; `ls` of that directory | sizes, structure |
| 7 | `grep -n` and `sed -n` on the operational draft for activation and launcher terms | locations for Appendix B |
| 8 | `python3 -I` on a helper script that checks table row widths (§8) | see §8 |
| 9 | `Edit`/`Write` of the two deliverables and the four pointers | edits applied |
| 10 | the final checks of §8 | see §8 |

**Disclosed deviations from "named documents only".** Two reads went beyond a
single named document, both inside the one documentation directory `docs/review/`
and neither recursive: (a) `ls docs/review | grep -i …`, a directory listing
filtered by name, to find the acceptance records and the one-host files; and
(b) one fixed-string `grep -l "DR1" *.md` over that directory's `*.md` files, to
find the document that defines DR1 and "Route 3". No secret-bearing path is in that
directory and none was opened by name.

**Harness note.** One long `grep` output on the operational draft was saved by the
tool harness to its own session output store outside the repository. I did not read
that file back, and it contains only text of the draft.

**No guard refusal occurred.** `.claude/hooks/guard-secrets.py` and
`guard-git.py` refused nothing.

## 7. Checks not run, and why

* No SSH or other host connection, `oracle-test`, production, staging, Foundry or
  database access, and no retained-evidence access: forbidden.
* No application test, hook test (`python3 .claude/hooks/test_guards.py`),
  formatter, build, package tool, network check or remote-host check: forbidden,
  and this is a documentation slice. `run-suites` does not apply.
* No citation, observation or measurement of any host behaviour. Every new
  host-behaviour statement in the proposal is a **proposed** obligation (§13.2 of the
  proposal), and the line counts used in its surface argument are the only measured
  quantities.
* No re-verification of R2's source citations: re-retrieval is forbidden, and R2 is
  accepted.
* No byte-level inspection of any launcher image. PO-17 stays unevaluated.

## 8. Final checks

Run after every deliverable and pointer edit was written. All operated on the six
allowed files, listed explicitly.

| Check | Result |
|---|---|
| Prompt identity, re-checked at handback | `9693`; `8e4d2a95…8c00`: **equal** |
| Returned items and MF identifiers against the accepted R2 record | every item (PO-20 (f), PO-21 (c), PO-21 (s), PO-11 (d), PO-12, AS-8, PO-12′, PO-19, PO-17) and MF-1 … MF-8, X-1 and CL-21i is present in R2 at the locations of proposal Appendix C. The MF facts in proposal §10 equal R2 §14.3. PO-21 (u) appears in R2 as row (u) of its §8 table |
| Authority-language scan of the proposal | every occurrence of "authoriz…" is a statement that nothing is authorized, a name of a design object (for example *not authorized*, PK's result), or a reference to a future A-2 or separately authorized slice. None grants host, implementation, cleanup, activation, commit or push authority |
| Markdown table row widths, proposal | 0 mismatches |
| Trailing whitespace, six files | see the closing record below |
| Repository-relative links, six files | see the closing record below |
| `git diff --check`, four tracked pointers and two new deliverables | see the closing record below |
| Six-file diff review | the four pointers differ from their pre-start state only by the heading, one return paragraph, the relabelled authority and prompt links, and the added proposal and handback links. The two deliverables are new files. No host, implementation, successor, cleanup, credential, secret, commit or push authority is granted or implied |

## 9. Security implications

* **No new attack surface is created by this return.** It is documentation.
* **What the proposal changes, if accepted later:** the lock moves to a root-only
  object (no `ubuntu` process can hold it); a static first image closes the
  ambient environment and inherited descriptors of every root helper; and every
  wait has a monotonic deadline. Each change fails closed to "no pass".
* **What the proposal does not close**, stated by name in proposal §13.1: RO-1
  (an uncatchable holder end with PID 1 unable to spawn the stop-post and the
  backstop, leaving a pre-pass, inert grant); RO-2; RO-3; CX-5 (three root acts
  outside the authorized path set); HB-1 (H-1, RB-1 and RS-1 under `sudo`'s
  environment); and the `ubuntu`-owned `ACT` evidence directory, which I flagged.
  It is left unchanged for CL and CP and narrowed only for the inline release,
  which uses the identity the holder holds in memory.
* **Route 3 does not make PO-12′ or PO-19 true.** It removes the part R2 refuted
  (the ambient environment) and leaves the part never observed (the files), which
  stays MF-1, MF-2 and MF-4.
* **CX-4 is declared void on accepted R2 evidence, but not retired here.**
  Retirement is Peter's decision (DEC-6) and is bound to the cited systemd version.
* No secret, credential or player datum was read, and no secret-bearing path was
  opened or named.

## 10. Unresolved decisions for Peter

DEC-1 Route 3 (supersedes D-3's Route 1; RT3-A recommended; alternatives RT3-B and
RT3-Z). DEC-2 which PO-21 (c) residual to accept (RO-1 recommended; alternative
ALT-SENT). DEC-3 the operational timeout values (recommended `pk_op_ms` 30,000,
`pk_call_ms` 5,000, `lock_wait_ms` 5,000, S 120 s, R 60 s, `backstop_max` 20).
DEC-4 the lock location (K recommended). DEC-5 MF-3's observing slice (a separate
privileged read-only slice before H-1 recommended). DEC-6 CX-4's retirement. Each has
a recommendation and bounded alternatives in proposal §12. No other accepted
decision is changed: OH-D-1 … OH-D-10, OS-6, U-9's text, M-B, M-S and the R2
dispositions stand.

## 11. Proposed independent-review focus

The twelve questions of proposal §14, in particular: (1) whether the safety kernel
really cites none of the four refuted mechanisms; (2) the lock discipline and the
root-only object; (3) the inline release and the inertness lemma, and whether RO-1
is stated narrowly enough; (4) BSP's use of the monotonic clock and CX-4's
retirement; (5) HB-1; (6) the operational-timeout arithmetic and values; (7) whether
helper children's loader inputs need an MF-9; (8) the RX contract; (9) the PO-12′ and
PO-19 narrowing; (10) the completeness of the Role A … H inventory; (11) the
RT3-A versus RT3-B argument; (12) the successor order.

## 12. Confirmation and retained helper files

I confirm that **no** host connection, `oracle-test` or production access, Foundry
or database access, retained-evidence access, secret, credential or player-data
access, network research, package operation, implementation or configuration
edit, launcher retarget or rebuild, application or hook test, build, service or
database mutation, repository or host cleanup, workspace recreation, H-1/H-2,
activation, rollback, commit or push occurred.

Two small helper scripts, `tablecheck.py` and `links.py`, were written to this
session's scratchpad directory (outside the repository) and read only the named
files. They are not deliverables and were left in place. I took no cleanup action.

## 13. Closing record of the final repository checks

| Check | Result |
|---|---|
| Prompt identity, last run | `9693`; `8e4d2a95…8c00`: equal |
| Trailing whitespace, six files | 0 lines in each |
| Link check, six files: 37 distinct targets were listed first and seen to be project documentation only, then tested | 70 links checked, 0 broken |
| `git diff --check`, four tracked pointers | exit 0, no output |
| `git diff --check --no-index`, the two new deliverables | exit 1 (differences exist) and **no whitespace error reported**. An earlier run reported "new blank line at EOF" in the proposal. I removed that line and re-ran |
| Markdown table row widths, both deliverables | 0 mismatches |

OH-S3 R1 design remediation awaits independent Codex review; no host, implementation, cleanup, OH-S4p or later slice is authorized.
