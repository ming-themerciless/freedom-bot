# Handback — LIT-FULL WP-1 boundary proposal: `WP-1 BOUNDARY PROPOSAL RETURNED`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-20261007-09`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-claude-prompt.md),
**5504 bytes, SHA-256 `60074759b6e0ae8f41b9cf3d5ddd0f477fa960cc4cd4d7fad5f21661b0a1011e`**,
recomputed with `wc -c` and `sha256sum` before any edit, and equal to the pin in the
[WP-1 authority](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-boundary-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-boundary-proposal.md),
53,995 bytes, SHA-256 `4c4535b8c1c7f207d6d82e039a9395b0bd97a6bfe5cc3cb33108e1fdd2b34775`.

## 1. Terminal state

**`WP-1 BOUNDARY PROPOSAL RETURNED`.** Both deliverables exist, the four current-state
pointers are updated, and they are mutually consistent (§5). No HARD STOP arose: the
required information was present and the authorities did not conflict.

**One point needs Codex's reading, and I stopped where the prompt told me to.** The
prompt says: *"If an LR exception is required, stop and report it rather than treating it
as approved."* My recommended answers to BQ-2 and BQ-3 **each require a BC-4 exception**
(proposal §8, EX-1 and EX-2). I read the instruction as: report the exception
prominently, treat it as unapproved, and still deliver the decision-ready proposal,
because the prompt also requires the recommendation and exact boundary sentences. I did
not stop short of delivering. If Codex reads the instruction as requiring a `HARD STOP`
instead, this handback is the report and the terminal text should be revisited.

**Nothing is accepted by this return.** I decided neither BQ-2 nor BQ-3, approved no
exception, authorized no successor, and opened no §0.2 change.

## 2. What the proposal concludes

| Item | Conclusion | Class |
|---|---|---|
| BQ-1 | recorded as R3-ROOT | commissioned direction |
| BQ-4 | recorded: no dynamic-child exception; constraints on WP-2 … WP-7 stated | commissioned direction |
| Procedures that need no exception | RT-1 … RT-4 (consume, holder, stop-post, backstop), because PID 1 starts a design image first | derived from accepted text |
| `sudo`-started paths | `attest`, the installer class, AP-2's `systemd-run`, and **the OS-6 `systemctl stop`** | the last is **not named in R8 §9.3 (E-4)** |
| BQ-2, beginning at `sudo` | LR-2 **cannot** be met; needs a start path that is not `sudo`, which no accepted record designs | new analysis |
| BQ-2, beginning at the first controlled image | LR-1 … LR-6 hold for everything the procedure does; the exception is confined to `sudo` and one `execve` | new analysis |
| Finding on BQ-2 | AP-2 and the OS-6 stop have **no controlled image today**, so "the first image the procedure controls" does not exist for them | observation |
| BQ-2 recommendation | **B2-F with B2-F-A**: begin at the first controlled image; add a static `start` and `stop` image; `sudo` the only excepted program. **Pending Peter** | new |
| BQ-3 recommendation | **B3-OUT**: installer class outside the set, as an exception with HB-1. **Pending Peter** | new |
| Exceptions required by the recommendation | EX-1 (`sudo`) and EX-2 (installer class), both under R8 §12.2 BC-4. **Reported, not approved** | — |
| Unresolved scope item | BC-2 (is R3-ROOT a narrowing of DR1 §5.3?) is **not decided by any accepted record** | flagged, not decided |

## 3. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-boundary-proposal.md` | **created** |
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-handback.md` | **created** (this file) |
| `docs/review/Handover information` | pointer: heading, current-state paragraph, WP-2 gate sentence, link rows |
| `docs/project-management/status.md` | pointer: same |
| `docs/implementation-plan.md` | **§20 only**: current-state paragraph and link rows |
| `docs/operations/disposable-test-server.md` | **restriction banner only**: heading, WP-1 sentence, link rows |

Nothing else was edited. The files that were already modified or untracked when the
session began (see the session's git status) were left as they were, other than the four
pointers above.

## 4. Checks performed

| Check | Result |
|---|---|
| Prompt identity: `wc -c` and `sha256sum` against the authority's pin | 5504 bytes and `60074759…a1011e`, **equal** |
| `.agents/AGENTS.md`, plan reading map, §0, §16, §20, Handover, banner, status, G-1 record, authority, R8 acceptance read | done; the R8 proposal and R2 record were read in the sections named in proposal §1.1 and not in full |
| Fixed-string search of the design for `sudo -n` | **24 lines, four distinct root literals**: the stub (`python3.12 -I -S`, used for installer and for `attest`), the AP-2 `systemd-run`, the OS-6 `systemctl stop` (seven occurrences), and `systemctl start` (Option C, not adopted) |
| Fixed-string search of R8 for `sudo -n` | the stub, `rp11-rootexec attest` (SSW text), and the AP-2 `systemd-run`; **no literal the design lacks**. `systemctl stop` appears in R8 only as DI-4 and as a mutating child, never as a `sudo` act |
| Fixed-string search of the design for `H-1R` | found in the `rp11_h1.py` subcommand list and in package-drift text; **R8 does not name it in the installer class** |
| Link targets of the proposal and the four pointers resolve | every target exists except this handback, created after the check, and rechecked below |
| Each pointer edit was made by exact-match replacement that asserted a single match | all matched once |
| Restrictions and archive links preserved | the "No host or retained-evidence access …" paragraph, the MF-1 … MF-8 statement and the retained R5 / H-0G sentence remain in the pointers; the archived pre-decision links remain |
| WP-2's inventory not performed | confirmed: only R8's DI map is used (proposal §4.1) |
| Anything run that is not a read or a repository-file write | **nothing** |

## 5. Mutual consistency of the deliverables and pointers

* Proposal ↔ handback: same terminal state, same exception statement, same open questions
  (proposal §12, Q-1 to Q-6; this handback adds Q-7 on the reading of the prompt).
* The four pointers each say that WP-1 returned, that its authority and prompt are
  consumed, that it awaits independent Codex review and Peter's recorded BQ-2 / BQ-3
  decisions, that WP-2 cannot be prompted before both, and that the exceptions are
  reported and unapproved. Each links the proposal, the handback, the consumed authority
  and the consumed prompt.
* No pointer states a decision on BQ-2 or BQ-3.

## 6. Unresolved questions

| ID | Question |
|---|---|
| Q-1 | Is treating the `ubuntu`-run entry as outside the set a narrowing of DR1 §5.3 (R8 BC-2)? |
| Q-2 | Is the list of `sudo`-started acts complete? SA-2 (the OS-6 stop) is not in R8 §9.3; `H-1R` is not in R8's installer class |
| Q-3 | Is B3-OUT an exception or only a set-membership determination? |
| Q-4 | Does the OH-D-6 consistency reasoning apply to inputs `ubuntu` itself sets on a `sudo`-started path? |
| Q-5 | Are the added `start` and `stop` roles an in-scope consequence of LR-4, or a design addition needing Peter's separate approval? |
| Q-6 | Should BQ-2a (where a `sudo`-started procedure begins) and BQ-2b (which acts are root procedures) be decided separately? |
| Q-7 | Does the prompt's "stop and report" mean what §1 above says it means? |

## 7. Statement on prohibited operations

**No prohibited operation occurred.** I used no SSH and made no connection to any host;
did not access retained evidence, secrets, credentials, player data, production, staging,
`oracle-test`, Foundry or a database; did no network research; ran no package operation,
installation, implementation, configuration edit, launcher work, build, test, formatter,
service or database operation, cleanup or workspace recreation; did no OH-S4 / OH-S4p or
later work, no H-1 / H-2, activation or rollback; and made no commit and no push. I edited
no application or infrastructure code, no accepted proposal, no acceptance record and no
historical snapshot. The commands I ran were reads (`sed`, `grep`, `wc`, `sha256sum`,
`ls`, `git status`, `git diff --stat`) and Python scripts that rewrote only the files in §3.

## 8. Proposed reviewer focus

1. Whether B2-S really fails LR-2 for every `sudo`-started path with the repository's
   mechanisms, and whether any accepted text already designs a `sudo`-free start (B2-N).
2. Whether SA-2 and H-1R belong in the sets as proposed (Q-2).
3. Whether the BC-4 reporting satisfies the prompt's "stop and report" (Q-7).
4. Whether the recommended sentences (proposal §7) say no more and no less than the
   analysis supports, and whether any [N] statement reads as accepted.
5. Whether BC-2 (Q-1) must be resolved before any WP-9 choice of LIT-FULL.
