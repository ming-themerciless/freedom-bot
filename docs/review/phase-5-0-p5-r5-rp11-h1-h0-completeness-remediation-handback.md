# Handback — R5 H-0 completeness and host-contract remediation (DR1)

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR1-20261006-03`

Date: 2026-10-06

Executor: Claude Code, in `/opt/freedom-blades/platform` (repository-local, read-only inspection plus the authorized documentation writes)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-remediation-claude-prompt.md), SHA-256 `b52085f8caccc88ec3b633c70e4d02d4874bfc9af06c90d8f48cc07e0268cedc`, 9780 bytes. These values were recomputed before any work and equal the authority's pin.

Authority: [`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-authority.md)

Deliverable: [`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md)

## 1. Terminal state: `REMEDIATION PROPOSAL READY FOR REVIEW`

The cumulative remediation proposal and this handback are written, and the three current-state pointers are updated. Nothing is accepted, bound or authorized.

R5's `H-0 PASS` remains not accepted, and HF-15 and HF-18 remain incomplete. No host, network or retained-evidence access occurred.

## 2. Requirements addressed

| Prompt item | Where in the proposal | Result |
|---|---|---|
| 1. HF-15 and `MI.capture_root_A` | §3, §7 | Fifteen accepted constraints (K-1 … K-15) are enumerated, including the §4.1.5 exclusions. Two implied consequences are stated: the parent must be pre-existing and `ubuntu`-writable, and it cannot be on `/run`. Every directory R5 observed (c124–c141, c105) was evaluated, and **none qualifies as the direct parent**. The recommended parent is `/var/lib/rp11-capture` (`ubuntu:ubuntu`, `0700`), on the `/var/lib` filesystem that R5 observed (c136, c137). The recommended template is `/var/lib/rp11-capture/⟨activation_id⟩-pass-a`. **Binding alone does not complete R5's HF-15**: a narrow observation is recommended (D-1c (a)), with an ancestor-rule alternative (D-1c (b)). The parent is created by a separate provisioning act, CPP (D-1b). Fixed input FI-1 and pre-execution `HARD STOP` FI-2 are added. Each item is presented as a Peter decision |
| 2. HF-18 | §4 | Traced through OH-D-2, IA-10, TR-0 … TR-3, C-3, C11 §4.4.6 and HF-18. Finding: no specific client executable is load-bearing for any security property. Options A, B and C are presented. Option A is recommended: withdraw HF-18 from H-0, and make the client path a fixed preflight input of each slice that runs a client, with a `HARD STOP` on absence. §4.4 explains why A does not weaken the hook grammar, the topology, the authorization boundary or the trusted path. HF-18 is retained as **incomplete** until Peter decides. No host path was guessed |
| 3. Python 3.12 versus 3.14 | §5 | 55 normative RP-11 occurrences were inventoried by semantic role (A–H), plus the launcher listing bytes. Three routes are compared on security, reproducibility, drift, operations and review, and three non-routes are rejected. Route 1 (exact `/usr/bin/python3.14`) is recommended. Its consequences are stated: launcher rebuild with new digests and I-7/D9 re-review (OH-S4p), OH-S2 re-citation, U-9 restatement, tests under 3.14, and drift gates (D-3b). The proposal states explicitly that a textual replacement discharges nothing |
| 4. Polkit and PO-21 (i) | §6 | R5's `unreadable` and unknown results are preserved. A gap in the accepted design is identified: P-0 and AP-0 are unprivileged but must establish absence inside a `0750 root:polkitd` directory. Proposed: privileged read-only P-0p at H-1 before M-0, an AM-0 root re-check, and `unreadable` never treated as absent. PO-21 (i): no accepted local source names the paths. HF-20 is split, and OH-S2 result CL-21i defines them. Fail-closed rule: AP-0 cannot pass without CL-21i |
| 5. Composition and successor | §8, §9 | Each fact has a disposition. The composition rule depends on re-observed anchors. The H-0G shape has entry and exit criteria and prohibitions, a fresh work ID and evidence path, and no R5 path access. The fallback is a full fresh H-0. No authority is created |
| Required proposal contents | §2, §10, §5.2, §8, §9, §11, §12 | traceability table, decision table, exact amendment texts, role-grouped inventory, disposition table, successor criteria, review questions, no-change statement |

## 3. Files changed

**Created by this assignment:**

| File | SHA-256 | Bytes |
|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md` | `403b2bc1acec24ceea4fb7e5ad327efde52f200f29fd09ac6e0d0ff357582d60` | 60344 |
| `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-handback.md` | this file (digest not self-reported) | — |

**Updated by this assignment.** These are pointer updates only, made on top of pre-existing uncommitted edits, which were preserved:

| File | Before | After | Change |
|---|---|---|---|
| `docs/review/Handover information` | `fa2e1a58da7f12c04b3e81f805ee4b8e90d801e17f93a43683d465c5992d7422` | `c042ec340d06bd2f8a54d6282e10adb707424fc1aff9b403b2a7de905faea4be` | heading changed to "remediation returned for review"; one terminal-state paragraph added; "Active remediation prompt" relabelled "Consumed"; proposal and handback links added |
| `docs/project-management/status.md` | `45d726d5e114dcd7cb185f19c1d81782dac5deeef12eecae72ffc57b27135f0a` | `5ff78cfaf0a4acefbe1c75901f8e11ae20860e75cc5959c80669069f4c331314` | the same three changes |
| `docs/implementation-plan.md` §20 | `903bee2b6439c231c0a9d2b2082178639e6b7c575945b8715e5875d45bd4428d` | `1bc4c6b0e20bb7707300dd6f972f4b43b9f8ecada9468950a46f7e3d5b752491` | the same three changes in §20 only |

No other file was changed. In particular, the following are unchanged:

- the accepted one-host design (`a752a4b8…7e615d02`);
- C11, D2, the operational draft and the manifest;
- all source, tests and infrastructure;
- the R5 handback and review;
- the change-log and decision register;
- `disposable-test-server.md`, whose banner still names the consumed R5 restriction. Updating it is outside this assignment's scope, so it is left to the controller.

There were no migrations, configuration or deployment changes, commits or pushes.

## 4. Pre-existing worktree changes, reported separately

These were present at start and preserved unchanged, except for the three pointer files above, which already had uncommitted edits before this assignment.

- **Modified:**
  - `.agents/AGENTS.md` (SHA-256 `28ce54ef…7c84ad2`, re-verified unchanged at the end);
  - `docs/implementation-plan-archive/README.md`;
  - `docs/implementation-plan.md`;
  - `docs/operations/disposable-test-server-archive/README.md`;
  - `docs/operations/disposable-test-server.md`;
  - `docs/project-management/change-log.md`;
  - `docs/project-management/decision-register.md`;
  - `docs/project-management/status-archive/README.md`;
  - `docs/project-management/status.md`;
  - `docs/review/Handover information`;
  - `docs/review/handover-archive/README.md`.
- **Untracked:** 30 files, the four `*-through-2026-10-04-d3-r6-acceptance.md` snapshots and the R1–R5 and agent-client prompts, authorities, handbacks and reviews listed in the start-of-session `git status`. Among them is this assignment's prompt and authority.

The `git status --porcelain` output at the end differs from the start only by the two new files.

## 5. Commands and checks run, with exact results

All commands were local and read-only, except the authorized writes.

| Check | Command (summary) | Result |
|---|---|---|
| prompt pin | `sha256sum`, `wc -c` on the prompt | `b52085f8…cedc`, 9780: **equal** to the authority |
| required reading | `Read`, `sed -n` of AGENTS.md (whole), plan reading map, §0, §16 and §20, Handover, banner, R5 review, R5 handback lines 1–518, the design sections listed in proposal §1 | done |
| retained-value verification | `sed`/`grep` of R5 handback Appendix B records c009–c012, c069, c071, c072, c096, c097 | confirmed that c012 invoked `/usr/bin/python3` (`executable=/usr/bin/python3`) and that the c096 digest, c097 stat and package versions are as cited |
| 3.12 search, whole tree | `git grep -c -i -E 'python3\.12\|python ?3\.12\|cpython ?3\.12\|libpython3\.12\|py3\.?12\|cp312' -- .` | 235 matches in 126 tracked files, classified by role in proposal §5.2. The RP-11-normative set is in Roles A–D. The remainder is Roles F–H, sampled per file and classified |
| inventory completeness | Python script: every matching line in the design, C11, D2, `launch.c`, `rp11_launch.py` and the manifest must be cited as `:line` in the proposal | first run: 55 matches, 1 missing (C11 `:514`), which was added. Re-run after all edits: **55 matches, 0 missing** |
| listing bytes | `grep -rn -i python3 infra/rp11-launch` | `launch.c:207`, `:221`; listing `:412` (`/usr/bin/python3` with `.12` continued on `:413`) |
| no blanket replacement | `git diff --stat` on `.agents tools infra tests` and the accepted design | only the pre-existing `.agents/AGENTS.md` diff appears, and its digest is unchanged. No `3.12` occurrence in any tracked file was edited |
| whitespace | `git diff --check` | exit 0, no output |
| whitespace, new file | `git diff --no-index --check /dev/null ⟨proposal⟩` | first run: 6 trailing-whitespace lines (Markdown hard breaks), which were fixed. Final run: exit 1 with no error lines, meaning the files differ and there are no whitespace errors |
| links | link-extraction loop over the proposal's relative links | final run over the proposal, this handback, `Handover information`, `status.md` (`../review/…`) and `implementation-plan.md` (`review/…`): **no missing target** |
| authority / remote language scan | `grep -n -i -E 'is (now )?authorized\|hereby\|we authorize\|accepted\.\|sudo \|ssh '` on the proposal | matches only (a) "not accepted"/"is authorized" inside negations in §0, §3.3 and §12, and (b) quoted design literals (`sudo -n …`) and the P-0p amendment text. No grant of authority |
| secrets / player data | review of the diff and of the files read | none read or written. The `/etc/machine-id` value appears only as R5's already-published SHA-256 inside cited records, and is not repeated in the proposal |
| scope | final `git status --porcelain` compared with the start snapshot | the only additions are the proposal and this handback, besides the three pointer edits |

## 6. Checks not run

- No application test suite, formatter, linter or type checker: the assignment changes documentation only and forbids them.
- No network, no `oracle-test` access, and no access to any `/var/tmp/p5-r5-rp11-*` path. Every host fact is cited from R5's durable handback, never re-observed.
- No upstream source was read (CPython, glibc, systemd, polkit). Every version-bound claim is deferred to OH-S2 under U-10. In particular, nothing is asserted about CPython 3.14's `os` API, `getpath` or PO-21 (i)'s actual conditions.
- No markdown renderer or link checker beyond the path-existence loop.

## 7. Security implications

- **Capture-root parent.** The parent is `ubuntu`-owned. This is consistent with OH-D-6 (an authority boundary, not a privilege boundary) and with the draft's C-7, but it is a deliberate choice, and review question 2 asks about it. Its creation needs one privileged act (CPP).
- **HF-18 Option A.** The client check moves later and closer to its use. No trust argument depended on it (§4.2), and installation and search stay forbidden.
- **Route 1.**
  - It changes a reviewed static binary, so I-7/D9 evidence and an independent rebuild must be redone before any installation.
  - The interpreter is auto-updatable (HF-17), so version- and digest-equality gates are proposed.
  - Route 2 is not recommended because it introduces an unsupported interpreter and a new trust root.
- **Design gap found.** H-1 P-0 and AP-0 cannot establish the absence of `50-freedom-blades-rp11.rules` without privilege. An implementation that mapped `EACCES` to absent would silently pass. The proposal makes `unreadable` explicitly never-absent and adds root checks (P-0p, AM-0).
- **PO-21 (i).** No grant can be linked until the CL-21i path list is accepted.

## 8. Remaining decisions

These are all Peter's, after Codex re-review (proposal §10):

| ID | Decision | Recommendation |
|---|---|---|
| D-1 | capture-root parent and template | `/var/lib/rp11-capture`; `/var/lib/rp11-capture/⟨activation_id⟩-pass-a` |
| D-1b | parent creation | a separate CPP act |
| D-1c | HF-15 completion | observe the parent in H-0G |
| D-2 | HF-18 | Option A |
| D-3 | interpreter | Route 1 |
| D-3b | drift control | equality gates |
| D-4 | Polkit gate | P-0p at H-1 plus AM-0 |
| D-5 | PO-21 (i) | HF-20 split and CL-21i |
| D-6 | successor | H-0G, or a full fresh H-0 on anchor failure |
| D-7 | fixed-checkout question | pre-existing and unresolved; it blocks HF-03's repository element |

## 9. Proposed reviewer focus

1. Whether the K-4/K-12 inference holds (a pre-existing, `ubuntu`-writable parent) and whether `/var/lib/rp11-capture` meets K-1 … K-15.
2. Whether the D-1c (b) ancestor rule is sound, or whether the observation is mandatory.
3. Whether Option A for HF-18 removes anything that C-3, E-1 … E-3, S-8 or the polkit/CP/A-2 boundary relied on.
4. Whether the Role A–D inventory is complete, especially the launcher image and every place that pins `04218ed2…`, and whether the Role F–H exclusions are correctly classified.
5. Whether P-0p is compatible with §4.2.4's "root … for the mutation steps only", and whether proposal §6.2 should become a separate finding against the accepted design.
6. The HF-20 split and the CL-21i "empty list" wording.
7. Whether the composition anchors in proposal §8 are sufficient.
8. That the pointer edits make no authority claim and that the `disposable-test-server.md` banner (still R5's) is handled by the controller.

Remediation awaits independent Codex review and Peter's recorded decisions; no H-0 successor, OH-S2 or later slice is authorized.
