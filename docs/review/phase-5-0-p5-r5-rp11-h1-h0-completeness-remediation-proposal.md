# Proposal — R5 H-0 completeness and host-contract remediation (DR1)

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR1-20261006-03`

Date: 2026-10-06

Author: Claude (repository-only documentation remediation)

Independent reviewer: Codex

Decision owner: Peter Duscha

Prompt:
[`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-remediation-claude-prompt.md)
(SHA-256 `b52085f8caccc88ec3b633c70e4d02d4874bfc9af06c90d8f48cc07e0268cedc`,
9780 bytes, equal to the authority's pin)

Authority:
[`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-authority.md)
(SHA-256 `4fea647613d398627ed49d91a68458ae64664a082f132abe06647ae0baee9a5e`)

Handback:
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-handback.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-handback.md)

**State: proposal only, inactive, unreviewed and unaccepted.** Nothing in this
file changes the accepted one-host design, any accepted baseline, decision,
authority, gate or finding. It accepts no capture-root binding, removes no
H-0 fact, selects no interpreter route, composes nothing into an `H-0 PASS`
and authorizes no successor. Every amendment below is **proposed text** for
Codex's independent review and Peter Duscha's recorded decisions. Labels
*(DR1)* mark proposed amendments to the accepted design; the accepted design
file itself is not edited by this assignment.

---

## 0. Outcome and recommendations

R5 (`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-20261006-02`) collected credible facts
but not a complete H-0: two accepted facts depended on maintainer inputs that
no assignment supplied, the design names an interpreter the host does not
have, and two further items (the Polkit collision and PO-21 (i)) cannot be
settled by an unprivileged H-0 at all. This proposal resolves each gap by
making the missing input an explicit decision and by moving each fact to the
earliest gate that can actually establish it.

| # | Gap | Recommendation (for Peter's decision) |
|---|---|---|
| 1 | HF-15 has no capture-root parent | Bind `MI.capture_root_A` to the template `/var/lib/rp11-capture/⟨activation_id⟩-pass-a` under the dedicated parent `/var/lib/rp11-capture` (`ubuntu:ubuntu`, `0700`), created by a separately authorized one-time provisioning act. Observe the parent in the narrow successor (§9), because R5 never observed it |
| 2 | HF-18 has no client path | Option **A**: remove HF-18 from H-0, and require each slice that runs an agent client on `oracle-test` to name and `C-STAT` its exact client path as a fixed preflight input. HF-18 stays **incomplete** until Peter decides |
| 3 | `/usr/bin/python3.12` absent; CPython 3.14.4 present | Route **1**: retarget the design to the exact `/usr/bin/python3.14`, rebuild and re-review the launcher, and return PO-12, PO-19 and every version-bound claim to OH-S2. A textual `3.12 → 3.14` substitution discharges nothing |
| 4 | `/etc/polkit-1/rules.d` unreadable; PO-21 (i) paths unnamed | Add a **privileged read-only** absence check at H-1, before any mutation (P-0p), repeat it as root at AM-0, and treat `unreadable` as never-absent. Split HF-20: its path-presence element moves to AP-0/AM-0 with a path list that only an accepted OH-S2 PO-21 (i) citation can supply |
| 5 | R5 composition | Preserve R5 as is. A **narrow gap collection (H-0G)** under a fresh work ID observes only what R5 lacks and re-observes the composition anchors. A full fresh H-0 is the fallback if any anchor differs |

The H-0 contract is also amended (§7) so that a maintainer-supplied input
missing from an assignment is a **pre-execution `HARD STOP`**, never a fact
recorded as `not specified` at `H-0 PASS`.

**No accepted baseline, authority or gate changes until Peter decides and
Codex re-reviews the resulting amendment.**

---

## 1. Sources examined

All reads were local and read-only. Digests are of the working-tree files at
the time of this assignment.

| Source | SHA-256 | Read |
|---|---|---|
| `.agents/AGENTS.md` | `28ce54ef69b94e21eb82e298aef5bef5fded36bb34dde202eea438acc7c84ad2` | completely |
| `docs/implementation-plan.md` | `903bee2b6439c231c0a9d2b2082178639e6b7c575945b8715e5875d45bd4428d` (before this assignment's pointer update) | reading map, §0, §16, §20 |
| `docs/review/Handover information` | `fa2e1a58da7f12c04b3e81f805ee4b8e90d801e17f93a43683d465c5992d7422` (before this assignment's pointer update) | completely |
| `docs/operations/disposable-test-server.md` | `6c6ea256b1121e3905232afe684e153f52574d478bb4301f36f7966b67ba47a1` | restriction banner and §1 profile |
| R5 independent review `project-review-2026-10-06-…-h0-r5-incomplete.md` | `eb5506b228604a6621c91b652a7a2ffec5e8364be0dfb10195ea69c65e2f49ea` | completely |
| R5 handback `phase-5-0-…-h0-r5-handback.md` | `5bbc72a56cf43de8de149c27703fec5c7d80115113567de8778f83896fa652af` | through **Checks not run**; Appendix B records c009–c012, c069, c071, c072, c096 and c097 only, to verify the interpreter values cited here |
| accepted one-host design `phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | `a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02` (525019 bytes; unmodified in the worktree) | header; §1–§3.4; §4.1.1–§4.1.5; §4.2.3; §4.2.5-R1 (a)–(c); §4.2.5-R2 (b), (d), (l); §4.2.5-R4 (b); §4.3.5; §4.4.1–§4.4.3 including §4.4.2b; §4.7.4 with D3-R1 … D3-R6 successor rows; targeted searches |
| R5 authority and prompt | `ddc0f9f1ca3c556f34a7844b6f6e969d8dc192ced37a7aef13a17bee75ffce66`; `57d23c1ba683ce8c2be15fe101da959a9dc1334ff89a1b0c66f917f26cf42e8e` | scope history only |
| C11 `phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md` | `f6405cd94a826e7883b80589c1edcd2be1e5b56b4481987d7cacdea96312f70b` | C-3, §4.4.6, PO-12, AS-8, M-5 and every 3.12 line |
| D2 `phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md` | `4859ab4efd307d8dda27518335a9c9bc3a36b99c55c83dfcee02e7b141366174` | every 3.12 line |
| operational draft `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | `5c6046fc3dc0b9a931cc32076233b1ea9185dc14c5d0ea1abc193687dcca7de6` | `MI.capture_root_A/B`, C-6 … C-9, `PIN.interpreter` |
| prerequisite decisions `project-review-2026-10-04-p5-r5-rp11-h1-prerequisite-decisions.md` | `17a32ab45e33d36424579ec6ec963ff38f5d9ad7be368813f541473baf57b9cc` | U-9 |
| `infra/rp11-launch/launch.c` | `6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe` | the `execve` literal |
| `tools/phase_5_0_evidence/rp11_launch.py` | `0d4ece459dbffac790e3a1f7d61e0c83efe270825e0d874cded48e759f626a08` | `EXECVE_PATH`, `EXECVE_ARGV` |
| `phase-5-0-evidence-harness-review-manifest.json` (v31) | `b9f03a4791448c029b9a1eccc50416818893294357fa9f6182f85610ed14817a` | the `rp11_launch` section |

No remote path, retained evidence directory, secret, credential, SSH
configuration or application or player data was read.

---

## 2. Finding-to-change traceability

| Finding / gap | Source | Proposed change | Section | Decision |
|---|---|---|---|---|
| HF-15 capture-root parent not observed | R5 review finding 1 (Blocking) | fixed parent and template; provisioning act; HF-15 (DR1) wording; fixed-input rule FI-1 | §3, §7 | D-1, D-1b, D-1c |
| HF-18 client path not observed | R5 review finding 2 (Blocking) | remove HF-18 from H-0 (Option A) and move client verification to the slice that uses the client; or keep it with a Peter-named path | §4, §7 | D-2 |
| `/usr/bin/python3.12` absent; CPython 3.14.4 present | R5 review finding 3 (Important); R5 HF-06 … HF-10 | Route 1 retarget, grouped by semantic role; OH-S2 re-citation; drift gates | §5 | D-3, D-3b |
| `/etc/polkit-1/rules.d` unreadable; `50-freedom-blades-rp11.rules` unknown | R5 review finding 4 (Important); R5 HF-11, HF-12 | P-0p privileged absence check; AM-0 root re-check; AP-0 records `unreadable` and defers | §6.1 – §6.3 | D-4 |
| PO-21 (i) condition paths not named | R5 review, closing paragraph; R5 HF-20 | HF-20 split; OH-S2 result CL-21i; AP-0/AM-0 check; fail-closed rule | §6.4 | D-5 |
| *(found here)* H-1 P-0 and AP-0 are specified as unprivileged, yet must establish absence inside a `0750 root:polkitd` directory | accepted design §4.2.4 P-0, §4.2.5-R2 (d) AP-0; R5 HF-11/HF-12 | same as the row above | §6.2 | D-4 |
| *(found here)* the static launcher image embeds `/usr/bin/python3.12` | `launch.c:207,221`; listing `0x40067f`; image `04218ed2…2668572` | the launcher is in Route 1's scope: rebuild, new digests, I-7/D9 re-review | §5.2, §5.5 | D-3 |
| HF-03 repository-ownership element not observed | R5 HF-03; R3 review | **not resolved here**: depends on Peter's pending fixed-checkout decision | §8, §11 | D-7 (existing) |
| R5 composition | R5 review, successor condition | fact-by-fact disposition; H-0G | §8, §9 | D-6 |
| H-0 contract allowed `not specified` at PASS | R5 handback terminal state | FI-1 … FI-5 | §7 | D-6 |

---

## 3. HF-15 and `MI.capture_root_A`

### 3.1 Every accepted constraint on `MI.capture_root_A`

| # | Constraint | Source |
|---|---|---|
| K-1 | a maintainer input, reviewed by Codex | operational draft `MI.capture_root_A`; design §4.1.5 |
| K-2 | absolute; on `oracle-test` | design §4.1.5; OH-D-3 decision |
| K-3 | pass-specific; distinct from `MI.capture_root_B`, neither inside the other | OH-D-3 decision; draft C-6, `MI.capture_root_B` |
| K-4 | does not exist before its pass; created **exclusively** by the entry at X-1 (TR-11), which runs as `ubuntu` with `NoNewPrivileges=yes`, `UMask=0077` and no `sudo` | draft A0-08, C-6; design TR-11, §4.2.5-R4 (b) unit text |
| K-5 | outside the Git worktree `/opt/freedom-blades/platform` | draft C-6; design §4.1.5 |
| K-6 | outside `/tmp` and `/var/tmp` | draft C-6; design §4.1.5 |
| K-7 | outside `/var/lib/fb-evidence-p5-0` and `/var/lib/freedom-blades` | design §4.1.5 |
| K-8 | neither contains nor lies under any §4.2.3 path, nor under `/var/lib/freedom-blades-rp11` | design §4.1.5 |
| K-9 | on a filesystem whose type and mount options H-0 records (HF-15) and RP-11's review accepts: directory and file synchronization semantics and same-directory hard links (PO-20) | design §4.1.5; draft `MI.capture_root_A` |
| K-10 | owned by the operator account (`ubuntu`); directory `0700`, files `0600` | draft C-7; U-3 binding |
| K-11 | its creation is made durable by a directory barrier on the directory that contains it | draft C-6 |
| K-12 | a common parent, if any, already exists and is not created, cleaned up or otherwise written by the mechanism or operator beyond each root's own entry, and holds no capture file | draft C-6 |
| K-13 | retained unmodified after the pass; never removed, renamed or reused | draft C-8 |
| K-14 | `pass-a.json` names exactly one capture root, and AP-0 requires it absent | design §4.2.5-R1 (a), §4.2.5-R2 (d) |
| K-15 | the holder and CP read the capture root's presence as root (HL, CQ-4, `pass-ended` predicates) | design §4.2.5-R2 (g), §4.2.5-R5 |

Two consequences follow, and neither is stated in the accepted text.

* **K-4 with K-12 requires a pre-existing parent writable by `ubuntu`.** The
  entry is unprivileged and may not create the parent (K-12), so the parent
  exists before the pass and grants `ubuntu` write and search permission.
* **K-13 excludes `/run`.** A `tmpfs` does not survive a kernel boot (PO-20 (g)),
  so retained evidence cannot live there.

### 3.2 Candidate parents, including every directory R5 observed

R5 recorded filesystem facts (HF-15) for `/`, `/usr/local`,
`/usr/local/libexec`, `/etc`, `/etc/systemd/system`, `/etc/polkit-1/rules.d`,
`/var/lib`, `/var/tmp` and `/run` (c124–c141), and owner/mode facts (HF-11,
c105) for the §4.2.3 parents.

| Candidate parent | R5 facts | Verdict |
|---|---|---|
| `/var/tmp` | ext4 `/`, `1777`, 30-day ageing (c138, c139, c105, c150) | **excluded** by K-6; ageing contradicts K-13 |
| `/run` | `tmpfs` (c140, c141) | **excluded** by K-13 |
| `/`, `/usr/local`, `/usr/local/libexec`, `/etc`, `/etc/systemd/system`, `/var/lib` | ext4 `/` (c124–c133, c136, c137); `root:root` `0755` (c105) | **not usable as the direct parent**: `ubuntu` cannot create an entry in a `root:root` `0755` directory, so X-1 would fail (K-4). `/usr/local/libexec` and `/etc/systemd/system` also hold §4.2.3 paths |
| `/etc/polkit-1/rules.d` | `root:polkitd` `0750` | **excluded**: polkit rules directory; not writable by `ubuntu` |
| `/home/ubuntu/…` | password-database entry only (c035); no filesystem fact | **rejected**: H-0 forbids home-directory content; the directory co-locates the operator's credentials and any agent client's state with evidence; not observed by R5 |
| `/srv/…`, `/opt/…` (outside the worktree) | none | **rejected**: no R5 fact; `/opt/freedom-blades` holds the worktree and the test runtime |
| **a new directory `/var/lib/rp11-capture`** | its containing filesystem is `/var/lib`'s: ext4 on `/dev/sda1`, `rw,relatime,discard,errors=remount-ro,commit=30`, 46167704 1K-blocks about 17 % used, 5707520 inodes (c136, c137); `/var/lib` is `root:root` `0755`, dev 2049, ino 97831, no xattr names (c105) | **recommended**, subject to §3.4 provisioning |

**No directory whose facts R5 collected satisfies every constraint as the
direct parent.** The recommendation therefore prefers the closest compatible
choice: a new dedicated directory on the one filesystem (`/` ext4) that R5
observed for every candidate and that PO-20 must already cite for `/var/lib`
and `/var/tmp` (HF-15 D3-R1 amendment). It introduces no new filesystem type.

The name avoids textual prefixes of the excluded subtrees.
`/var/lib/freedom-blades-capture`, for example, is not under
`/var/lib/freedom-blades` as a path, but a naive string-prefix check would
misclassify it.

### 3.3 Recommended binding (decision D-1)

* **Parent:** `/var/lib/rp11-capture`, a directory, `ubuntu:ubuntu`, mode
  `0700`, no POSIX ACL extended attribute, on the filesystem that holds
  `/var/lib`, and not a mount point.
* **Template:**
  `MI.capture_root_A` = `/var/lib/rp11-capture/⟨activation_id⟩-pass-a`,
  with `⟨activation_id⟩` exactly the A-2 value of §4.2.5-R1 (a). The full
  grammar is
  `^/var/lib/rp11-capture/rp11-act-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}-pass-a$`.
* `pass-a.json` carries the full path, and A-2 pins it. The pairing with the
  activation identifier makes each root pass-specific and fresh by
  construction (K-3, K-4), and lets an auditor relate a root to its
  activation records without parsing the root.
* A future `MI.capture_root_B` would use `-pass-b` under a different
  activation. Pass B is outside M-11 and this proposal; the template only
  guarantees that the two cannot collide (K-3).

Each constraint holds as follows: K-2, K-5 … K-8 by the literal; K-9 by
`/var/lib`'s filesystem and the PO-20 citation; K-4 and K-10 by the parent's
owner and mode; K-11 because `ubuntu` can open the parent `O_RDONLY` and
`fsync` it; K-12 and K-13 by §3.4; K-14 and K-15 unchanged.

**This binding is a recommendation for Peter's decision. It is not
accepted.**

### 3.4 Creating the parent (decision D-1b)

Creating `/var/lib/rp11-capture` needs root, which H-0, the entry and an
unprivileged executor do not have.

| Option | Description | Assessment |
|---|---|---|
| **(i) recommended** | **CPP, capture-parent provisioning**: a one-time act under its own authority, after H-1 PASS and before the first A-2. Its preflight requires E-1 and that the parent path does not exist (`lstat` → `ENOENT`). It then runs an exclusive `mkdir` (never `-p`), `chown ubuntu:ubuntu`, `chmod 0700` and an `fsync` of `/var/lib`, and records `lstat`, `listxattr` names, `findmnt --target` and `df --output` of the parent. CPP never removes anything | keeps H-1's root-only trees, the H-1 record, RS-A and RB-1 unchanged; one small privileged act with a single postcondition |
| (ii) | H-1 creates the parent as an extra directory outside trees **L** and **V** | H-1 would then own an `ubuntu`-owned, non-RB-1 directory; this changes §4.2.3, the H-1 record schema, RS-A and RB-1's scope |
| (iii) | `ACT` creates the parent if absent | mixes a persistent evidence directory into a boot-scoped activation whose cleanup (CL) must never touch it |

**Retention.** Neither CL, RB-1 nor any cleanup slice may remove, rename or
write inside the parent. Its later removal needs Peter's explicit decision
after every root under it has been dispositioned (K-13).

### 3.5 Does the binding make R5's HF-15 evidence complete?

**Not by itself.** HF-15 as accepted records the filesystem type, mount
options and capacity *of the proposed capture-root parent*. R5 never observed
`/var/lib/rp11-capture`: it did not `lstat` it and did not run `findmnt` or
`df` on it. The binding therefore leaves a gap, which closes in one of two
ways (decision D-1c).

* **(a) Recommended: a narrow successor observation.** H-0G (§9) observes
  `lstat /var/lib/rp11-capture` (expected `ENOENT`), `findmnt --target` and
  `df --output` on that path (which resolve to its nearest existing ancestor),
  and the `/var/lib` composition anchors. That is three or four commands, in
  a collection that Route 1 needs anyway (§5).
* **(b) Alternative: accept R5 under an ancestor rule.** If Peter and Codex
  accept the HF-15 (DR1) wording in §3.6, which records the nearest existing
  ancestor whenever the parent does not exist yet, then R5's c136 and c137
  (`/var/lib` → `/` ext4) are that ancestor's facts. HF-15 would be complete
  for H-0 purposes **only** together with CPP's fail-closed preflight and
  postcondition. Without those, an unobserved mount point at the parent path
  could invalidate the inference.

### 3.6 Proposed amendments

**§4.1.5 (DR1), appended:**

> *(DR1)* `⟨MI.capture_root_A⟩` is
> `/var/lib/rp11-capture/⟨activation_id⟩-pass-a`, with `⟨activation_id⟩`
> exactly as A-2 fixes it (§4.2.5-R1 (a)). Its parent `/var/lib/rp11-capture`
> is a pre-existing directory, `ubuntu:ubuntu`, mode `0700`, without a POSIX
> ACL extended attribute, not a mount point, and on the filesystem holding
> `/var/lib`. Only the provisioning act CPP creates it, under its own
> authority. No RP-11 slice, CL, RB-1 or cleanup removes, renames or writes
> inside it, except that X-1 creates exactly one capture root per pass in it.
> No `tmpfiles.d` line names the parent. A string-prefix comparison is never
> used for the exclusions above. Each is tested on path components.

**HF-15 (DR1), replacing the D3-R1 annotation:**

> HF-15 also records, for the capture-root parent named by the assignment's
> fixed input (§7, FI-1): its `lstat` result. If the parent exists, it records
> its type, owner, group, mode, `(dev, ino)` and extended-attribute names,
> plus `findmnt --target` and `df --output` on the parent. If it does not
> exist, it records `ENOENT` and the same two commands on the parent path,
> naming the mount they resolve to. A capture-root parent absent from the
> assignment is a pre-execution `HARD STOP`. It is never recorded as `not
> specified`.

**AP-0 (DR1), additional conditions:** the parent satisfies §4.1.5 (DR1) as
re-observed unprivileged by `ubuntu` (`lstat`, `listxattr` names, and its
`/proc/self/mountinfo` mount equal to `/var/lib`'s); the capture root is
absent; and no `tmpfiles.d` line names the parent.

**OH-S3 note.** The operational draft's `MI.capture_root_A` and C-6/C-7 rows
still say "on the repository host" and "no file is created on `oracle-test`".
The one-host restatement already belongs to OH-S3 (§4.7.4). This proposal
adds the parent and template to OH-S3's inputs and edits no draft text.

---

## 4. HF-18 and the interactive client

### 4.1 Trace

| Element | Accepted text | What it needs from a client executable |
|---|---|---|
| OH-D-2 (decided) | operator and executor processes run locally on `oracle-test` as `ubuntu`, reached through an interactive login session; no scripted remote controller; no model-provider credential without separate authority | a **topology** rule for where processes run, not a named executable |
| IA-10 | the client hook and the entry read the same root-owned `pass-a.json`. That holds only if the client runs on `oracle-test` | co-location, satisfied by OH-D-2 |
| TR-0 | the login session, outside the trusted path; nothing it carries reaches TR-4 (S-8) | none |
| TR-1 | the client (T0), as `ubuntu`, *Trusted?* **no** | none |
| TR-2 | client hooks (T1, **Claude only**), *defense in depth only* | present only when the client is Claude Code with this repository's `.claude/settings.json` |
| TR-3 | the client shell (T2) runs the one literal `systemctl … start --wait rp11-capture-pass-a.service`; *Trusted?* **no** | none |
| C11 C-3 | hooks under *E_c*: **"defense in depth, not enforcement"** | none |
| C11 §4.4.6 | the in-entry guarantee "is identical for Claude and non-Claude operators" | none |
| HF-18 | "the operator client's presence, if OH-D-2 asks for it … recorded as a fact and never satisfied by installing one … `C-STAT` on the named path only" | a named path that **no accepted text names** |

### 4.2 Finding

**A specific interactive-client executable is not load-bearing for any
accepted security property.**

* **Hook grammar.** C-3 is a text-level defense in depth whose rules are
  fixed in the repository and tested there (E-2, T-B1/T-B2 and the OH-S4
  literal-grammar tests). Its absence is the accepted non-Claude case of
  C11 §4.4.6, not a defect.
* **Local-only topology.** It is enforced by E-1 (identity preflight), E-2
  (no `ssh`, `scp`, `sftp`, `rsync` or `host:path` in any resource) and E-3,
  and by OH-D-2's decision text. None of them depends on the client's path.
* **Authorization boundary.** The only authorization decision is polkit's at
  TR-5, under the start-only rule, CP's consume (TR-6a) and A-2. The
  requester's identity reaches it only as kernel peer credentials (TR-4).
* **Trusted-path argument.** LB-2S begins at TR-6. S-8 and PO-14 make
  everything from TR-0 to TR-4 irrelevant to the entry's state.

HF-18 is **operationally** relevant to exactly one question: can a slice that
intends to run an agent client on `oracle-test` (rebuild, H-1, `ACT`, the pass
operator) do so without installing one? That is a readiness precondition of
**that** slice, at **its** time, and not a host fact that any proof obligation
or citation consumes. An H-0 observation of it would also go stale before the
slice that relies on it.

### 4.3 Alternatives (decision D-2)

| Option | Amendment | Effect on R5 | Trade-off |
|---|---|---|---|
| **A, recommended** | Remove HF-18 from §4.4.1. Each later assignment that runs an agent client on `oracle-test` names its exact client executable path as a fixed input. Its preflight `C-STAT`s that path after E-1 and before any other act, and records owner, mode and real path. Absent or unexpected → `HARD STOP`, never an installation. A slice whose operator is a human shell user names no client, and C-3's absence is recorded as the C11 §4.4.6 case | HF-18 needs no observation. R5's `not specified` is superseded and not converted into a pass | the fact is checked when it matters, under the authority that relies on it |
| B | Keep HF-18. Peter names one exact path per role, and H-0G `C-STAT`s it | H-0G gains one command per named path | records presence long before use; requires Peter to fix the client choice now |
| C | Keep HF-18 and declare every role human-operated through the login shell, with no agent client | HF-18 recorded as `n/a — no client by decision` | forgoes C-3's defense in depth for every role; conflicts with any later wish to run Claude on `oracle-test` |

No host path is guessed or inferred here. In particular, nothing is inferred
from the controller's own installation of Claude Code, because OH-D-2 is about
`oracle-test` and the controller is a different host.

### 4.4 Why Option A does not weaken the design

1. **Hook grammar.** C-3's rules and OH-S4's grammar tests are repository
   properties and do not change. Option A states explicitly when C-3 is
   present (an agent client named and verified at preflight), instead of
   leaving it implied by an H-0 row.
2. **Local-only topology.** E-1 … E-3 and OH-D-2 are unchanged. Option A adds
   a check (the named client is local and present). It removes none.
3. **Authorization boundary.** It is unchanged: polkit, CP and A-2 never
   depended on the client's identity.
4. **Trusted-path argument.** It is unchanged: TR-0 … TR-4 remain untrusted,
   and S-8 is the reason.

### 4.5 Proposed amendment (if Option A is chosen)

**§4.4.1 HF-18 (DR1):**

> *(DR1)* HF-18 is withdrawn from H-0. Every assignment that runs an agent
> client on `oracle-test` names that client's exact executable path as a fixed
> input. After E-1 and before any other act, its preflight records `lstat`, the
> real path, owner, group and mode of that path. An absent path, a path
> missing from the assignment, or an unexpected type or owner is a `HARD
> STOP` before any act. It is never remedied by installing, updating or
> searching for a client. An assignment that names no agent client records
> that C-3 is absent (C11 §4.4.6).

Until Peter decides, **HF-18 remains incomplete** and R5's `not specified`
stays a design-input gap.

---

## 5. CPython 3.12 versus 3.14

### 5.1 Observed facts used (R5 only; not accepted here)

| Fact | R5 evidence |
|---|---|
| `/usr/bin/python3.12` absent: `stat` exit 1, `sha256sum` exit 1, invocation exit 127; `readlink -f` printing the path is not presence | c092–c095 |
| `python3.12`, `python3.12-minimal`, `libpython3.12-minimal`, `libpython3.12-stdlib` not installed; no `dpkg -S` owner of `/usr/bin/python3.12` | c054–c057, c063, c081–c084 |
| `apt-cache policy` printed **nothing** for `python3.12` or `libpython3.12-*` from the configured lists (only two unrelated `postgresql-plpython3-12*` entries matched the pattern) | c091; R5 unexpected fact 8 |
| `/usr/bin/python3` is a `root:root` `777` symlink resolving to `/usr/bin/python3.14` | c009, c010 |
| `/usr/bin/python3.14`: regular file, `root:root`, `755`, 7468968 bytes, SHA-256 `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` | c096, c097 |
| `/usr/bin/python3.14` owned by `python3.14-minimal` `3.14.4-1ubuntu0.2` (source `python3.14`); `/usr/bin/python3` owned by `python3-minimal` `3.14.3-0ubuntu2` (source `python3-defaults`); `dpkg --verify` silent for both | c068, c069, c071, c072, c089, c090 |
| `/usr/bin/python3 -I -S -c …`: `3.14.4 (main, Aug 20 2026, 10:41:58) [GCC 15.2.0]`, `isolated=1`, `no_site=1`, `executable=/usr/bin/python3`, `prefix=/usr`, `path=['/usr/lib/python314.zip', '/usr/lib/python3.14', '/usr/lib/python3.14/lib-dynload']` | c012 |
| `unattended-upgrades.service` active and enabled; `apt-daily*` timers enabled | c145, c146 |

**c012 invoked the symlink `/usr/bin/python3`, not `/usr/bin/python3.14`.**
Its `sys.executable` is the symlink path. An exact-path invocation of
`/usr/bin/python3.14` was never observed. The packages `python3.14`,
`libpython3.14-minimal` and `libpython3.14-stdlib` were never queried.

### 5.2 Inventory of affected references, by semantic role

Method: `git grep -n -i -E 'python3\.12|python ?3\.12|cpython ?3\.12|libpython3\.12|py3\.?12|cp312'`
over all tracked files, plus the launcher listing's split byte string. The
handback (§3) gives the exact commands and counts. Each match was classified
by what the literal *does*. Roles A–D are normative for the RP-11 installed
or privileged contract and change under Routes 1 and 2. Roles E–H do not.

**Role A — executed literals: the program a process `execve`s, in an
installed, compiled or privileged artifact.**

| Location | Text | Route 1 replacement |
|---|---|---|
| `infra/rp11-launch/launch.c:207`, `:221` | `argv_out[0] = "/usr/bin/python3.12"`; `rp11_syscall3(RP11_SYS_EXECVE, (long)"/usr/bin/python3.12", …)` | `/usr/bin/python3.14` in both; then a rebuild (new image, listing, map and `launch.s` digests, `expected.sha256`) |
| `infra/rp11-launch/rp11-launch.x86_64.listing:412–413` | `.rodata` bytes `/usr/bin/python3` `.12` at `0x40067f` | regenerated by the rebuild, never hand-edited |
| launcher image `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | the compiled literal | superseded by a new reviewed digest. Every pin of `04218ed2…` (`rp11_launch.py`, `expected.sha256`, `tools/r5_runner/blocks/s08.sh`, design §4.2.4 P-0 and §4.5.2, IA-8) moves to the new value only through review |
| `tools/phase_5_0_evidence/rp11_launch.py:47`, `:49` | `EXECVE_PATH`, `EXECVE_ARGV[0]` | `/usr/bin/python3.14` |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json:2732`, `:2744`, `:2824`, `:2841` | `rp11_launch` contract `execve_argv`, `execve_path`, `execve.argv`, `execve.path` | `/usr/bin/python3.14`, in a new manifest version, with the new image digests |
| design §4.2.5-R4 (b) unit (`:2857`); also quoted at `:228`, `:2481`, `:2509`, `:5242` | `ExecStartPre=+/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume` | `ExecStartPre=+/usr/bin/python3.14 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume`. T-B1 admits exactly this line |
| design §4.2.4 (`:1257`) | `sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' …` | `sudo -n /usr/bin/python3.14 -I -S -c '⟨verified-exec stub⟩' …` |
| design §4.2.5-R2 (e), (f), (i) (`:1996`, `:1997`, `:2016`, `:2147`) | holder `ExecStopPost=`, holder command, backstop command, attest command | each `/usr/bin/python3.12` → `/usr/bin/python3.14`; the (e)/(f) grammar tests apply unchanged |
| design §4.2.5-R4 (h) (`:3124`) | `ExecStartPre` normalization `path` and `argv[0]` | `/usr/bin/python3.14` |
| C11 §4.4.3.4 item 5 (`:688`, `:903`–`:904`); D2 OD-1 (`:436`), §5.8 (`:1256`, `:1258`, `:1567`, `:1568`) | the `rp11-launch/1` `execve` contract | `/usr/bin/python3.14`, as a dated amendment to each accepted text, not a rewrite |

**Role B — trust-path and proof-obligation statements naming the interpreter.**

| Location | Text | Route 1 treatment |
|---|---|---|
| design TR-9 (`:945`) | `/usr/bin/python3.12 -I -S` (dynamic); PO-12, PO-19 | `/usr/bin/python3.14 -I -S`; PO-12 and PO-19 **re-cited** for 3.14 (§5.6) |
| design §4.4.2 PO-19 (a) (`:4497`) | "when `/usr/bin/python3.12` is started with exactly …" | `/usr/bin/python3.14`; the whole of PO-19 is re-cited for the HF-07 `libc6` *and* the new executable's `DT_RUNPATH`/`DT_RPATH` |
| C11 PO-12 (`:2426`), AS-8 (`:456`) | "CPython 3.12 `-I -S <script>` reads no `PYTHON*` variable …" | "CPython 3.14, at the HF-07-recorded `python3.14-minimal` version, …"; **re-cited** from that version's documentation and `getpath` source |
| C11 M-5 (`:2404`); design §4.7.1 M-5 (`:5154`) | "the entry interpreter `/usr/bin/python3.12`" | `/usr/bin/python3.14` |
| C11 C-5 (`:514`), T5 (`:576`), interpreter lookup row (`:598`), (`:619`), (`:809`), (`:941`), (`:1748`); C11 (`:62`), (`:281`) | descriptive trust-path text | `/usr/bin/python3.14` in a dated C11 amendment note. Withdrawn LB-2 (R1) and LB-3 rows (`:226`, `:798`, `:1019`, `:2529`, `:2533`) stay **as history**, unchanged |
| U-9 decision (prerequisite decisions `:24`) | "trusted loader inputs relevant to `/usr/bin/python3.12`" | a Peter-recorded restatement naming `/usr/bin/python3.14`. U-9 is a decision and is not edited silently |

**Role C — H-0 fact definitions and command classes.**

| Location | Route 1 replacement |
|---|---|
| HF-06 (`:4436`) | unchanged wording ("CPython version"); the observed value becomes 3.14.4 |
| HF-07 (`:4437`) | packages `python3.14`, `python3.14-minimal`, `libpython3.14-minimal`, `libpython3.14-stdlib` replace the four `3.12` names; `dpkg -S /usr/bin/python3.14` replaces `dpkg -S /usr/bin/python3.12` |
| HF-08 (`:4438`) | `/usr/bin/python3.14`: owner, mode, real path, SHA-256; `/usr/bin/python3.14 -I -S -c` printing `sys.version`, `sys.flags.isolated`, `sys.flags.no_site`, `sys.executable`, `sys.prefix`, `sys.path` |
| HF-10 (`:4440`) | `/usr/bin/python3.14` replaces `/usr/bin/python3.12` |
| C-VER (`:4472`) | `/usr/bin/python3.14 -I -S -c` with a fixed literal |

**Role D — standard-library capability claims that RP-11 code running under
the system interpreter relies on.**

| Location | Claim | Treatment |
|---|---|---|
| design §4.2.4-R1 PT-8 (`:1437`) | "glibc's `renameat2` … through standard-library `ctypes` (Python 3.12 has no wrapper)" | becomes an **OH-S2 citation item** for 3.14: does `os` expose `renameat2`/`RENAME_NOREPLACE`? The `ctypes` mechanism stays until the citation is accepted. No claim about 3.14 is made here |
| the bootstrap, the capture mechanism (`capture_contract.py`, `execution/capture_mechanism.py`, `execution/capture_store.py`) and the future `rp11_h1.py` | no version literal, but they run under TR-9's interpreter | OH-S4 must run their tests under the target interpreter version (§5.5, reproducibility) |

**Role E — verification and test artifacts derived from Role A.**
`tests/test_rp11_launch_source.py` (`:129`, `:134`, `:336`) and
`infra/rp11-launch/verify/ctverify.py` (`:796`) read the constants or the
manifest contract and need no literal edit, but their expected values change
with Role A. D2's test methods (`:1525`, `:2207`) and the I-7 handback's
decoded `execve` record (`:224`) are D9 evidence for the **old** image. They
remain history and are superseded by re-run evidence for the new image.

**Role F — development, test and Pass A act runtimes (not the installed
contract; unaffected).**

* `venv-web` CPython 3.12.14 (`disposable-test-server.md:44`, `:108`; operational
  draft `PIN.interpreter` `:342`; `tools/phase_5_0_evidence/case_runtime.py:111`).
  This interpreter runs the test suites and the Pass A acts A1-S1 and A1-13.
  It is uv-managed under `ubuntu`'s home (`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-handback.md`,
  lines 589 and 665), so it cannot be the root-owned M-5 entry interpreter. It is not a
  route (§5.4). It is unaffected, and H-0 does not observe it.
* Local controller CPython 3.12.3 records: the I-7 handbacks (`:178`, `:345`,
  `:356`), the IC1 handback (`:244`, `:274`, `:362`), `change-log.md:4521`,
  `:4631`, and reviews of 2026-09-28.
* Production deployment Python 3.12 (`docs/adr/0002-web-application-stack.md:19`,
  `:36`; `.agents/AGENTS.md` coding standards); `phase-5-0-package-plan.md`
  (`:1508`, `:5647`, `:5648`); `decision-register.md:58`; `change-log.md:128`
  (C-P5.0-AH).
* Evidence-harness and laboratory statements (`execution/descriptors.py:74`,
  `:157`, `:253`; `execution/case_program.py:839`;
  `tests/phase_5_0_evidence/test_no_execution.py:326`;
  `decision-register.md:1498`; `phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md:24`,
  `:33`; `phase-5-0-p5-r5-rp11-capture-mechanism-implementation-handback.md:35`,
  `:342`). These describe the harness runtime. If any of them is later relied
  on for code that runs under TR-9's interpreter, it joins Role D.
* The synthetic lab constant `REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"`
  in ten test files, and `test_executor.py:400`, `:405`,
  `test_expectations.py:270`, `:822`. These are test fixtures for the reserved
  laboratory runner contract (r2–r6) and are unrelated to RP-11.

**Role G — current-state records describing the mismatch.**
`implementation-plan.md:2566`, `status.md:17`, `Handover information` and
`change-log.md:8`. These are descriptive and are updated only as pointers.

**Role H — historical or consumed evidence; never edited.** The R3–R5 prompts,
authorities, handbacks and reviews; the design's §0-R4 summary (`:228`) and
§16 check row 8 (`:6979`), as revision history; the preparation handback
(`:185`, `:188`, `:283`); the 2026-09-29 C11 review (`:35`); and the
`*-through-*` snapshots.

**No blanket replacement is proposed.** Role A and C texts get exact
replacements. Role B texts get replacements **plus** re-citation. Role D texts
become citation or test items. Roles E–H are unchanged.

### 5.3 Routes compared (decision D-3)

| | Route 1: exact `/usr/bin/python3.14` | Route 2: separately authorized Python 3.12 | Route 3: abandon the Python-dependent route |
|---|---|---|---|
| **What changes** | Role A–D text; the launcher source and image; manifest; tests; U-9 restated | nothing in the design. A root-owned `/usr/bin/python3.12` must be installed under separate authority | the entry bootstrap, capture mechanism, CP, holder, backstop and CL must be re-implemented without Python, or RP-11's one-host design is withdrawn |
| **Availability (R5)** | present, packaged, `dpkg --verify` clean | **no candidate** in the configured apt lists (c091). It needs a new package source, a source build or a standalone build | — |
| **Security** | distribution-packaged, root-owned, verifiable through `dpkg`; the host's default `python3` target. No new trust root | a new trust root: a third-party archive, or an unpackaged build without `dpkg` provenance, so the HF-07 C-PKG model no longer covers it. The ubuntu-owned uv 3.12.14 fails M-5 | depends on the replacement. Likely a larger trusted computing base, written new |
| **Reproducibility** | the repository tests run under venv-web 3.12, so RP-11 code that runs under 3.14 must also be tested under 3.14 (a 3.14 test interpreter needs its own authority, or the gap is stated) | the test and target versions match | — |
| **Package drift** | `unattended-upgrades` is active (HF-17). A `python3.14*` update changes the version and digest that PO-12 and PO-19 bind. It is caught by the version-equality gates (§5.7) | an out-of-archive 3.12 receives no Ubuntu 26.04 security updates. Drift is lower and maintenance risk higher | — |
| **Operational** | no host change | a privileged installation and its rollback; an ongoing maintenance owner | a long redesign |
| **Review** | largest documentary churn: launcher rebuild and I-7/D9 re-review (D9-1 … D9-4, including an independent R-5 rebuild for D9-3), manifest v32, C11/D2/D3 dated amendments, OH-S4 tests, OH-S2 re-citation | the smallest design churn, keeping image `04218ed2…2668572`. But it adds installation review, provenance review and a citation of an unsupported build | a new design cycle |

### 5.4 Non-routes, rejected

* **Unversioned `/usr/bin/python3`.** It is prohibited by this assignment, and
  rightly: `python3-defaults` can re-point it in a routine upgrade, silently
  changing the version that every citation binds.
* **A `/usr/bin/python3.12` symlink or copy to 3.14.** It would make every
  3.12 citation describe a 3.14 process. That is a textual mask, worse than
  the mismatch it hides.
* **`venv-web`'s uv-managed 3.12.14.** It is `ubuntu`-owned under a home
  directory, so it fails M-5 (root-owned, not group- or world-writable), and
  it has no `dpkg` provenance.

### 5.5 Recommendation: Route 1, and its consequences

Route 1 keeps the interpreter inside the distribution's maintained,
`dpkg`-verifiable set and introduces no new trust root. Route 2's only
advantage, an unchanged launcher image, is outweighed by an unsupported
interpreter on a host whose other packages auto-update. Route 3 is warranted
only if OH-S2 **refutes** PO-12 or PO-19 for 3.14.

Route 1 requires, each under its own authority:

1. **OH-S2 (amended).** Re-cite PO-12 and AS-8 for CPython 3.14 at the
   accepted `python3.14-minimal` version, and PO-19 for the accepted `libc6`
   **and** `/usr/bin/python3.14`'s dynamic section. Add the PT-8 `renameat2`
   question. Re-run PO-17 (§4.3.6) against the new launcher image. A refuted
   PO-12 or PO-19 sends the design to Route 3 review.
2. **OH-S4p (new): interpreter retarget, repository only.** Apply Role A and C
   replacements to `launch.c`, `rp11_launch.py`, the manifest (a new version),
   tests and design texts. Rebuild the launcher deterministically. Record the
   new image, listing, map and `launch.s` digests. Re-run D9-1, D9-2 and D9-4
   evidence, then an independent rebuild for D9-3 (OH-S5 on `oracle-test`
   inherits the new digest).
3. **Tests under the target version.** OH-S4's RP-11 code tests (bootstrap,
   capture mechanism, `rp11_h1.py`) run under CPython 3.14 as well as the
   suite interpreter. Without a 3.14 test interpreter, the handback reports
   that gap.
4. **U-9 restated** by Peter for `/usr/bin/python3.14`.
5. **H-0G** observes the 3.14 facts R5 lacks (§9).

**Changing `3.12` to `3.14` textually discharges nothing.** PO-12, PO-19,
AS-8, the PT-8 capability claim, PO-17 against the new image, and D9-1 … D9-4
are all version- or image-bound. Each returns to OH-S2 citation or I-7-style
evidence, and then to independent review. Until then, Route 1's Role A text is
an unexecuted proposal.

### 5.6 Version-bound obligations that return to review

| Obligation | Bound to | Returns to |
|---|---|---|
| PO-12 / AS-8 | CPython version and `getpath` | OH-S2 |
| PO-19 (a)–(d) | `libc6` version and the interpreter's dynamic section | OH-S2 |
| PT-8 capability | CPython 3.14 `os` API | OH-S2 |
| PO-17 | launcher image bytes and HF-14 entries (R5 recorded a `python3.14` `binfmt_misc` entry, magic `2b0e0d0a`, interpreter `/usr/bin/python3.14`) | OH-S4p / H-1 P-0 |
| D9-1 … D9-4 | launcher image | OH-S4p, OH-S5 |
| §4.3.3 baseline `ExecStartPre` | unit text | PO-15 in OH-S2 |
| HF-07, HF-08, HF-10 values | observed host | H-0G |

### 5.7 Drift control (decision D-3b)

* **Minimum, recommended.** H-1 P-0 already requires re-observed HF-04 …
  HF-10 versions equal to H-0's. DR1 extends this: H-2 and AP-0 also require
  the `python3.14-minimal` version and the `/usr/bin/python3.14` SHA-256 to
  equal the values the accepted PO-12/PO-19 citations name. Any difference is
  INVALID RUN, followed by re-citation. It is never accepted at run time.
* **Optional, a host change under separate authority.** Hold the
  `python3.14*` and `libc6` packages, or disable `unattended-upgrades`, on
  `oracle-test` for the RP-11 window. This proposal does not recommend it as
  a substitute for the gates.

---

## 6. The Polkit unknown and PO-21 (i)

### 6.1 Preserved fact

R5's result stands exactly as recorded: `/etc/polkit-1/rules.d` is
`root:polkitd` `0750` (gid 983, ino 1625), and its listing is **unreadable**
to `ubuntu`. Whether `50-freedom-blades-rp11.rules` exists there is
**unknown** (`PermissionError errno=13`, c105–c107). HF-12 allows this
result. No part of this proposal infers absence.

### 6.2 A gap in the accepted design

Two accepted steps must establish that basename's absence, and both are
specified as **unprivileged**:

* H-1 **P-0** ("preflight, read-only, unprivileged … every §4.2.3 path
  **absent**"), whose D3 table still lists
  `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules`; and
* `ACT` **AP-0** ("executor, unprivileged … the rule basename absent from
  every PO-11 (f) directory").

`ubuntu` is not in group `polkitd` (HF-03), so neither step can obtain
`ENOENT` for that path. A fail-closed implementation always refuses. An
implementation that maps `EACCES` to absent would silently pass.
**AM-0** re-checks "AP-0's … absence conditions" **as root**, which is the
first accepted point that can establish the fact.

### 6.3 Earliest gate and amendment (decision D-4)

**Recommended:** the earliest gate is H-1, under its existing root authority
and before its first mutation. H-1 is the first slice that both holds root
and could make the collision matter.

> **P-0p (DR1), H-1, privileged and read-only, after P-0 and before M-0.**
> Through the H-1 tool's verified-exec stub under `sudo -n`, `lstat` exactly
> `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules`, and for every other
> rules directory that the accepted PO-11 (f)(i) citation lists,
> `⟨dir⟩/50-freedom-blades-rp11.rules`. Each result must be `ENOENT`. Any
> other result, including `EACCES` or a present object of any type, is
> **INVALID RUN** with nothing mutated, and it returns to Peter. The object
> is never removed, renamed or read beyond `lstat`. P-0's unprivileged form
> records `/etc/polkit-1/rules.d` as `unreadable` and defers the basename to
> P-0p. It never reports it as absent.

> **AP-0 (DR1).** For a rules directory that `ubuntu` cannot read, AP-0
> records `unreadable` and does not pass that condition by itself. **AM-0
> (DR1)** performs the same `lstat` set as root and requires `ENOENT` for each
> before AK-1. Otherwise the holder exits non-zero, before any activation file
> exists, and CL follows (stop-post).

**Alternative:** a separately authorized, narrow, privileged read-only
observation before H-1, run once to de-risk the decision early. It does not
replace P-0p or AM-0, because the fact can change before H-1.

HF-12 and HF-11 are **not** extended with privilege. H-0 stays unprivileged.

### 6.4 PO-21 (i) condition paths (decision D-5)

**Trace.** PO-21 (i) asks whether systemd `259.5-0ubuntu3.4` can restart
userspace while keeping the kernel, and if so, **every** condition under which
a requested reboot becomes such a restart automatically. AP-0 and AM-0
require each condition to be absent (DF-1, §4.2.5-R2 (l)). HF-20 asks H-0 to
record "the presence of every path that PO-21 (i) names".

**No accepted local source enumerates those paths.** The accepted design
names none, and R5 correctly recorded `not specified`. Only PO-21 (i)'s
citation, which is OH-S2 work under U-10, can name them. A pre-OH-S2 H-0
therefore cannot observe them. The HF-20 row asks H-0 for a list that only a
later slice produces.

**Proposed amendment:**

> **HF-20 (DR1)** is split. **HF-20a**, the `LoadState` of
> `systemd-soft-reboot.service` and `soft-reboot.target`, remains an H-0 fact.
> **HF-20b**, the presence of each PO-21 (i) condition path, leaves H-0.
>
> **CL-21i**, a required OH-S2 result: PO-21 (i)'s accepted citation states
> a closed list of condition paths and any non-path conditions for the
> HF-07 systemd version. For each it gives the exact absolute path, the
> predicate (present, absent, or a named content property), whether `ubuntu`
> can observe it unprivileged, and how it is disarmed. If the version cannot
> soft-reboot automatically, the citation says so and CL-21i is the empty
> list, which is then an accepted result and not an omission.
>
> **AP-0 (DR1)** evaluates every CL-21i condition that `ubuntu` can observe,
> and **AM-0 (DR1)** evaluates every condition as root. A condition that is
> present, armed or unobservable is INVALID RUN. A CL-21i entry that cannot be
> disarmed returns the design to review (DF-1).
>
> **Fail-closed.** Until CL-21i is accepted, no record may report HF-20b, or
> any PO-21 (i) host check, as observed or successful, and AP-0 cannot pass,
> so no grant can be linked.

An optional pre-H-1 host observation of CL-21i is possible as a later narrow
collection. It is not needed for H-0 and is not proposed here.

---

## 7. Future H-0 contract amendments

Proposed as §4.4.1 (DR1), applying to every future H-0 or H-0G assignment:

* **FI-1 Fixed inputs.** Every fact whose definition depends on a
  maintainer-supplied value is listed with that value as a fixed input of the
  assignment. Today that means the capture-root parent (HF-15), any client
  path (HF-18, if Option B), and the repository root's identity (HF-03, once
  Peter decides the fixed-checkout question).
* **FI-2 Pre-execution `HARD STOP`.** The executor checks every FI-1 input
  before any connection, command or write. A missing, empty or malformed
  input is `HARD STOP: missing fixed input ⟨name⟩`. It produces a handback
  and nothing else.
* **FI-3 No `not specified` at PASS.** `H-0 PASS` requires every listed fact
  to be observed, or to carry an outcome that its definition permits
  (`absent`, `unreadable`, a recorded non-zero exit). `not specified` is not
  such an outcome.
* **FI-4 No fact whose input comes from a later slice.** A fact whose path or
  value comes from a later citation (such as HF-20b) is not an H-0 fact.
* **FI-5 No inference.** No fact is inferred from controller-side state, from
  another host or from an earlier run's retained paths.

---

## 8. R5 fact disposition and evidence composition

R5's handback, its retained evidence digests (`MANIFEST.payload`
`f116244f94ca3ea42e51b0d1c2ea3e0c99257cecfafc5b9c13bd7fb742724503`; `MANIFEST.final`
`b8da7875b2f87a44483d9c744426855360279cc5f332f120fcac20bafe397553`;
`INVENTORY.owner-mode`
`70117b92702aa4690a75d6c23f5a93f620dc5117dc943a61d1417469842bee78`) and its
independent review are preserved unchanged. "Accepted from R5" below means
*proposed for acceptance as observed at R5's time*, subject to Codex and
Peter.

| Fact | Disposition | Note |
|---|---|---|
| retrieval, clean detached checkout, governing-file digests | **accepted from R5** | accepted by the independent review |
| HF-01, HF-02 | **accepted from R5** | E-1 re-checks them in every executing slice; H-0G re-observes them as composition anchors |
| HF-03 (account, groups, home, shell) | **accepted from R5** | — |
| HF-03 (repository ownership) | **incomplete** | withheld by R5's prompt; depends on Peter's pending fixed-checkout decision (R3 review). Not resolved by this proposal |
| HF-04, HF-05 | **accepted from R5** | re-observed in H-0G as anchors |
| HF-06 | **accepted from R5** as observed (CPython 3.14.4) | **invalidates** the design's 3.12 premise (§5) |
| HF-07, systemd, polkit, glibc, coreutils, util-linux, sudo, dbus rows | **accepted from R5** | the HF-07 versions in H-0G must equal R5's, or composition fails |
| HF-07, `python3.12*` rows | **accepted from R5** as `not installed` | **invalidated** as a contract under Route 1; replaced by `python3.14*` rows |
| HF-07, `python3.14`, `libpython3.14-minimal`, `libpython3.14-stdlib` | **requires a fresh observation** | never queried |
| HF-07, `python3.14-minimal`, `python3-minimal`, `dpkg -S` of both paths | **accepted from R5** | anchors for H-0G |
| HF-08, `/usr/bin/python3.12` | **accepted from R5** as absent | invalidated as a contract under Route 1 |
| HF-08, `/usr/bin/python3.14` owner, mode, size, SHA-256 | **accepted from R5** (c096, c097) | anchor: H-0G re-observes the SHA-256 |
| HF-08, exact-path `/usr/bin/python3.14 -I -S -c` output | **requires a fresh observation** | c012 used the symlink |
| HF-09 | **accepted from R5** | PO-19 re-citation uses it |
| HF-10 | **accepted from R5** (python3.14 through c097; the others through c103/c104) | link targets of `sha256sum`, `stat`, `sleep` and `sudo` not recorded (Optional) |
| HF-11 | **accepted from R5** | except `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules`: **unknown**, established at P-0p/AM-0 (§6.3), never in H-0 |
| HF-12 | **accepted from R5**, including `unreadable` | — |
| HF-13, HF-14, HF-16, HF-17, HF-19 | **accepted from R5** | HF-17 motivates §5.7 |
| HF-15 (listed paths, `/run`) | **accepted from R5** | — |
| HF-15 (capture-root parent) | **incomplete** | **requires a fresh observation** of `/var/lib/rp11-capture` (D-1c (a)), or acceptance of the ancestor rule (D-1c (b)) |
| HF-18 | **incomplete** | removed under D-2 Option A; a fresh observation under Option B |
| HF-20a | **accepted from R5** | — |
| HF-20b | **incomplete**; **invalidated as an H-0 fact** under D-5 | moves to CL-21i, AP-0 and AM-0 |

**Composition rule (proposed).** The composed H-0 record is R5's record plus
H-0G's record, joined by a composition statement that cites both evidence
digests. It is valid only if H-0G re-observes these anchors equal to R5's
values: HF-01, HF-02, the HF-04 kernel release, the HF-07 versions of
`systemd`, `polkitd`, `libc6` and `python3.14-minimal`, and the
`/usr/bin/python3.14` SHA-256. Any difference means the two observations do
not describe one host state. The successor then ends `HARD STOP: composition
anchor changed`, and a full fresh H-0 is required. The composed record
carries **two** observation times, and every later version-equality gate
uses H-0G's values.

---

## 9. Successor shape: H-0G, narrow gap collection (decision D-6)

**Recommended** over a full fresh H-0, because every other R5 fact is accepted
and anchored. A full fresh H-0 is the fallback on anchor failure or at
Peter's preference.

**This section proposes a shape. It creates no authority and marks nothing
authorized.**

**Entry criteria (all required before any connection):**

1. Peter's recorded decisions on D-1, D-1b, D-1c, D-2, D-3, D-5 and D-6, and
   Codex's re-review of the resulting amendment.
2. A **fresh work ID** and a fresh exclusive evidence path, of the form
   `/var/tmp/⟨RUN0⟩-h0g-evidence`, that differs from every earlier R1–R5 path.
   The program checks that exact path for absence by `test -e`/`test -L` only.
   It never lists `/var/tmp`.
3. Fixed inputs (FI-1): the capture-root parent `/var/lib/rp11-capture`; under
   Route 1, the interpreter path `/usr/bin/python3.14` and the four `python3.14*`
   package names; under D-2 Option B, each named client path; and the R5 anchor
   values of §8, copied from the R5 handback.
4. A separately authorized execution topology. Its form (for example R5's
   single forwarding-disabled connection) is Peter's to authorize. It is not
   presumed here.

**Command set (read-only, unprivileged, classes C-ID, C-PROC, C-STAT, C-DIG,
C-VER, C-PKG only):**

* anchors: `uname -n`; `sha256sum /etc/machine-id`; `uname -r`;
  `dpkg-query -W -f` for `systemd`, `polkitd`, `libc6`, `python3.14-minimal`;
  `sha256sum /usr/bin/python3.14`;
* HF-07 (Route 1): `dpkg-query -W -f`, `dpkg --verify` and `apt-cache policy`
  (local lists only) for `python3.14`, `libpython3.14-minimal`,
  `libpython3.14-stdlib`;
* HF-08 (Route 1): `stat` of `/usr/bin/python3.14`; `/usr/bin/python3.14 -I
  -S -c` with the fixed literal printing `sys.version`, `sys.flags.isolated`,
  `sys.flags.no_site`, `sys.executable`, `sys.prefix`, `sys.path`;
* HF-15 (DR1): Python `os.lstat` and `os.listxattr` of `/var/lib/rp11-capture`
  (expected `ENOENT`); `findmnt --target /var/lib/rp11-capture`;
  `df --output … /var/lib/rp11-capture`;
* HF-18 (Option B only): `C-STAT` of each named client path.

**Exit criteria.** `H-0G PASS` requires every command observed, an outcome
its definition permits, and every anchor equal. Otherwise the terminal state
is `HARD STOP`. Composition (§8) is a reviewer act after Codex's review. The
executor never claims a composed `H-0 PASS`.

**Prohibitions.** These are §4.4.1's list, plus: no access to R1–R5 retained
paths (`/var/tmp/p5-r5-rp11-*`) or to `/opt/freedom-blades/platform` on
`oracle-test`; no retrieval or checkout unless separately authorized (H-0G
needs no repository bytes on the host); no privilege; no `/etc/polkit-1/rules.d`
access beyond R5's recorded `unreadable`; no CL-21i path checks; no search for
a client; no installation, package operation, cleanup, retry, H-1/H-2,
activation, commit or push.

**Successor-slice rows (§4.7.4, DR1).** These replace or add to the D3-R6
rows of the same name. Every slice still needs its own authority.

| Order | Slice | Scope | Gate |
|---|---|---|---|
| OH-S0 | as D3-R6, plus D-1 … D-6 of this proposal | decision | Codex re-review of DR1, then Peter |
| OH-S1 | **H-0 composed** = R5 + H-0G (§8), under FI-1 … FI-5 | read-only, unprivileged | Codex review of H-0G and the composition |
| OH-S2 | as D3-R6, plus PO-12/AS-8 and PO-19 for 3.14, the PT-8 capability, and **CL-21i** | documentation, U-10 | Codex, then Peter; refuted PO-12/PO-19 → Route 3 review |
| **OH-S4p (new)** | interpreter retarget (§5.5 item 2), only under Route 1 | repository only | Codex review per slice, with a security-focused review |
| OH-S5 | as before, with the new image digest | as before | as before |
| OH-S8 | H-1 with **P-0p** | as before | as before |
| **CPP (new)** | capture-parent provisioning (§3.4) after H-1 PASS, before the first A-2 | privileged, one directory | Codex review; Peter acceptance |
| OH-S9 | as D3-R6, with AP-0/AM-0 (DR1) | outside this amendment | — |

---

## 10. Decision table

| ID | Decision | Recommendation | Owner | Effect if accepted |
|---|---|---|---|---|
| D-1 | capture-root parent and template | `/var/lib/rp11-capture` (`ubuntu:ubuntu` `0700`); `/var/lib/rp11-capture/⟨activation_id⟩-pass-a` | Peter, after Codex | §4.1.5 (DR1); OH-S3 input; AP-0 (DR1) |
| D-1b | who creates the parent | (i) CPP, a separate one-time privileged act | Peter | new CPP slice; H-1, RB-1 and CL unchanged |
| D-1c | how HF-15 becomes complete | (a) observe the parent in H-0G | Peter, after Codex | H-0G includes HF-15 (DR1) |
| D-2 | HF-18 | Option A, removed from H-0 and verified per slice | Peter, after Codex | §4.4.1 HF-18 (DR1); HF-18 needs no H-0 observation |
| D-3 | interpreter route | Route 1, exact `/usr/bin/python3.14` | Peter, after Codex | Role A–D amendments; OH-S4p; OH-S2 re-citation; U-9 restated |
| D-3b | drift control | version- and digest-equality gates at H-2/AP-0; host-side hold not recommended as a substitute | Peter | AP-0/H-2 (DR1) |
| D-4 | Polkit collision gate | P-0p at H-1, plus the AM-0 root re-check | Peter, after Codex | H-1 P-0p; AP-0/AM-0 (DR1) |
| D-5 | PO-21 (i) | split HF-20; CL-21i from OH-S2; AP-0/AM-0 checks | Peter, after Codex | HF-20 (DR1); OH-S2 scope |
| D-6 | successor | H-0G composing with R5; full H-0 on anchor failure | Peter | a future authority with a fresh work ID |
| D-7 | HF-03 repository ownership / fixed checkout | **existing open decision** (R3 review). Not decided here | Peter | blocks HF-03's repository element and IA-12 |

---

## 11. Unresolved decisions and independent-review questions

Every decision in §10 is unresolved. For Codex:

1. **K-4/K-12 inference.** Is it correct that the accepted constraints require
   a pre-existing, `ubuntu`-writable parent, and that no R5-observed directory
   qualifies as the direct parent?
2. **Parent choice.** Is an `ubuntu`-owned `0700` directory directly under
   `/var/lib` acceptable under OH-D-6's authority-boundary statement and the
   draft's C-7, or should the parent be root-owned with a narrower grant?
3. **D-1c.** Is the ancestor rule (D-1c (b)) sound enough to complete HF-15
   from R5 alone, or is the H-0G observation required?
4. **HF-18 removal.** Does Option A remove any property that C-3, E-1 … E-3,
   S-8 or the polkit/CP/A-2 boundary relied on? Is the per-slice preflight
   wording strict enough to forbid installation and search?
5. **Route 1 completeness.** Is the Role A–D inventory complete? In
   particular, are any version-bound claims missing from §5.6, and should
   OH-S4p be split into launcher and non-launcher slices?
6. **Route 2 dismissal.** Is "no candidate in the configured lists" (c091) a
   sufficient factual basis, given that R5 read only local lists?
7. **Test-version gap.** Must OH-S4 test RP-11 code under CPython 3.14 before
   OH-S5, or may a stated gap proceed?
8. **P-0p.** Is adding a privileged read-only step to H-1 before M-0 compatible
   with §4.2.4's "root … for the mutation steps only"? If not, which wording
   change is acceptable?
9. **HF-20 split.** Is moving HF-20b out of H-0 consistent with the D3-R2
   acceptance, and is CL-21i's "empty list is an accepted result" wording
   safe?
10. **Composition anchors.** Are the anchors in §8 sufficient, or should every
    HF-07 version be re-observed in H-0G?
11. **Defect found here.** Does §6.2 (unprivileged P-0/AP-0 against a `0750`
    directory) warrant a separate finding against the accepted design?

---

## 12. No change to the accepted baseline, authority or gates

This proposal changes no accepted baseline, design text, decision, authority,
gate, finding or disposition. R5 remains consumed, and its `H-0 PASS` remains
not accepted. HF-15 and HF-18 remain incomplete. The interpreter mismatch,
the Polkit unknown and PO-21 (i) remain open. No H-0 successor, gap
collection, provisioning act, OH-S2, OH-S4p or later slice is authorized.
Any effect described above takes effect only after Peter decides and Codex
re-reviews the resulting amendment.
