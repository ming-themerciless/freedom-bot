# Proposal and handback — one-host `oracle-test` amendment to the RP-11 static-launcher H-1 design

> **Accepted inactive design basis, 2026-10-04.** Peter Duscha accepted
> Codex's clean D3-R6 re-review and closed `OH-H1-D3-R5-1`,
> `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` as
> remediated. Historical revision sections below retain their original
> open/unaccepted wording as evidence. CX-4 is accepted as the documented
> outside-A-2 residual. This acceptance grants no implementation, host or
> execution authority. See the [acceptance record](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md).

Work ID: `C-P5.0-R5-RP11-H1-D3`  
Date: 2026-10-04  
Author: Claude, design author  
Independent reviewer: Codex  
Decision owner: Peter Duscha

Assignment:
[`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-claude-prompt.md)
(SHA-256 `22ea1f38e25c590f7079836d74b83e14346521dda2b1a0cd65af45e31e54d086`, 8,875 bytes)  
Authority:
[`project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-authority.md)
(SHA-256 `9ab372ff7f3106b79d72921261e3723be10573465ae5306c680d35f51015e24a`)  
Topology correction:
[`project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-topology-correction.md`](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-topology-correction.md)
(SHA-256 `c9889058b47285892ac6831b5bcfaab4d89a4e7302d7a721520b748d452f5a23`)

State: **proposal only, inactive, unreviewed and unaccepted.** It changes no
source, test, manifest, unit, rule, configuration or current-state record. It
authorizes no host access, build, installation, activation, H-0, H-1, H-2,
evidence pass, cleanup, commit or push. Everything below marked *proposed* is a
proposal for Codex's review and Peter Duscha's decision. It is not an accepted
design.

**Revision D3-R1 (2026-10-04).** Work ID `C-P5.0-R5-RP11-H1-D3-R1`, under
[`phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-claude-prompt.md)
(SHA-256 `7e2aaf6b706d221a3c3a3742620848752362a9a29c8ce7abd19d37342c9188ec`,
9,302 bytes) and
[`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-authority.md)
(SHA-256 `957632e1d2aa2cf0ce309b82b4a8ab7a5f8300108e8054f79a62906b1c837c7a`).
It remediates Blocking findings `OH-H1-D3-1` and `OH-H1-D3-2` of
[Codex's independent review](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md)
and incorporates Peter Duscha's
[OH-D-1 … OH-D-9 decisions](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md).
The D3 file as Codex reviewed it had SHA-256
`df50f62a92e58d08d1a206464a8dc282e5e44d0949784b3e19d7c44bffc1814e`
(91,310 bytes). Every D3-R1 change is marked *(D3-R1)* where it occurs.
Replaced D3 text is kept beside its replacement under the label **Original D3
text, superseded by D3-R1**, and §12 lists every replaced or amended paragraph.
The revised proposal is **still inactive, unreviewed and unaccepted**.

**Revision D3-R2 (2026-10-04).** Work ID `C-P5.0-R5-RP11-H1-D3-R2`, under
[`phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r2-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r2-claude-prompt.md)
(SHA-256 `748102eadbe2d5e1f8ee939b25e05aa5d11eff8cf30e7b8c284a05ab7f2e478b`,
7,058 bytes) and
[`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2-authority.md)
(SHA-256 `9328bbb20e45db625045e6fb786ddb4505bf247477b1548daeff92d47c335527`).
It remediates only Blocking finding `OH-H1-D3-R1-1` of
[Codex's independent re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation.md).
The D3-R1 file as Codex re-reviewed it had SHA-256
`edf4893240673c6a51e5649101f00a8f81077007ee87b9e25f8bbbfa611351b1`
(190,074 bytes). Every D3-R2 change is marked *(D3-R2)*. Superseded D3-R1
text is kept in place and labelled, and §13.5 lists every changed paragraph.
The proposal is **still inactive, unreviewed and unaccepted**.

**Revision D3-R3 (2026-10-04).** Work ID `C-P5.0-R5-RP11-H1-D3-R3`, under
[`phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r3-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r3-claude-prompt.md)
(SHA-256 `57a450626631b33b7bcbcebbf4cdefdc3193ea7bfd52a44d666b006f91c1076c`,
8,093 bytes) and
[`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3-authority.md)
(SHA-256 `3678a98d74280d5438d27d183b4ab589e9bf478ecfc8b5764f1b7d4a3832ab91`).
It addresses Blocking findings `OH-H1-D3-R2-1` and `OH-H1-D3-R2-2` of
[Codex's independent R2 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2.md).
At the start of D3-R3 this file had SHA-256
`9268a534992d9344f46b8cf3a59670c6c3f907ea01ce1541381d2df1a0f260b9`
(268,582 bytes). Every D3-R3 change is marked *(D3-R3)*. Superseded D3-R2
text is kept in place and labelled, and §14.5 lists every changed paragraph.
The return is **BLOCKED REMEDIATION** (§0-R3). The proposal is **still
inactive, unreviewed and unaccepted**.

**Revision D3-R4 (2026-10-04).** Work ID `C-P5.0-R5-RP11-H1-D3-R4`, under
[`phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r4-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r4-claude-prompt.md)
(SHA-256 `3578da8341862b7c2c07c27fbd48cb9fb988b9fd4fc331d934e1cd8d0f604b29`,
1,870 bytes) and
[`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4-authority.md)
(SHA-256 `0be8f2dfc0f716e5c606b309c119bd759cc16b61f1d96692f812efa74c2e2fe1`).
It adopts Peter Duscha's OH-D-10 decision, Option A with interruption route
(iii-a), after
[Codex's independent R3 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3.md).
At the start of D3-R4 this file had SHA-256
`efac90b61785a8dcf4c699024f5852a00715e535c6c182b6ddc900983496ca5a`
(330,599 bytes). Every D3-R4 change is marked *(D3-R4)*. D3-R3 text is kept
in place as history and labelled where D3-R4 supersedes it, and §15.5 lists
every changed paragraph. The return is **DESIGN REMEDIATION READY FOR
RE-REVIEW** (§0-R4). The proposal is **still inactive, unreviewed and
unaccepted**.

**Revision D3-R5 (2026-10-04).** Work ID `C-P5.0-R5-RP11-H1-D3-R5`, under
[`phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r5-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r5-claude-prompt.md)
(SHA-256 `2a01b7481b15285dcd392486b8625168b405d12fe3ca0df9ac9fbcb51aa476b0`,
3,483 bytes) and
[`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5-authority.md)
(SHA-256 `68d739263226f32c07c35ac580be496671680c399f721943685c9d183b66c5dc`).
It remediates only Blocking finding `OH-H1-D3-R4-1` of
[Codex's independent D3-R4 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4.md).
The D3-R4 file as Codex re-reviewed it had SHA-256
`019d5c3b8843f2a812dd0357621a2478296926d63805698f2e23475717c1fffe`
(398,749 bytes). Every D3-R5 change is marked *(D3-R5)*. D3-R4 text is kept in
place as history and labelled where D3-R5 supersedes it, and §16.5 lists every
changed paragraph. The return is **DESIGN REMEDIATION READY FOR RE-REVIEW**
(§0-R5). The proposal is **still inactive, unreviewed and unaccepted**.

**Revision D3-R6 (2026-10-04).** Work ID `C-P5.0-R5-RP11-H1-D3-R6`, under
[`phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r6-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r6-claude-prompt.md)
(SHA-256 `48345a17dbbf64f2bc951443f5f9e76c723dc1ede191f46121b4810db0d0d14f`,
2,330 bytes) and
[`project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-authority.md)
(SHA-256 `c320ab3e14852784cd1e53f020078cf279318ed06f80125dfc4db36e0e62e1a5`).
It incorporates Peter Duscha's OS-6 decision and remediates only Blocking issue
`OH-H1-D3-R5-1` of
[Codex's independent D3-R5 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5.md).
At the start of D3-R6 this file had SHA-256
`0c2bacfc7e2b8eda072d20deacf244a947c6327e9e3c81111fdd60c2c3255743`
(470,827 bytes). Every D3-R6 change is marked *(D3-R6)*. D3-R5 text is kept in
place as history and labelled where D3-R6 supersedes it, and §17.5 lists every
changed paragraph. The return is **DESIGN REMEDIATION READY FOR RE-REVIEW**
(§0-R6). The proposal is **still inactive, unreviewed and unaccepted**.

---

## 0. Outcome and recommendation

### 0-R6. D3-R6 outcome *(D3-R6, 2026-10-04)*

**DESIGN REMEDIATION READY FOR RE-REVIEW.**

`OH-H1-D3-R5-1` is addressed in design by §4.2.5-R6. It is **not** declared
closed. `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2`
also remain open. Only Codex may recommend closure, and Peter Duscha retains
acceptance authority.

* **The finding is accepted.** D3-R5 narrowed the decided route (iii-a) and
  called that a refinement. It should have returned BLOCKED REMEDIATION
  (§4.2.5-R6 (a)).
* **OS-6 is now Peter's decided amendment** to route (iii-a)
  ([R6 authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-authority.md)).
  The route is available only while the capture unit is `active`, its
  `InvocationID` equals the consume journal's `run-start.invocation_id`, and
  the journal has a durable `consumed` line. It is unavailable while the unit
  is `activating`, including `start-pre`. A hung consume step ends at the
  finite, fail-closed start timeout (§4.2.5-R6 (b)). The literal, the executor,
  A-2's authority and the §9.5.3 classification are unchanged.
* **Every route (iii-a) `stop` lands after the claim** (Lemma R6,
  §4.2.5-R6 (c)), even if the executor's read and the `stop` are not atomic.
* **Contract OSA is stated over the authorized path set 𝒜** (§4.2.5-R6 (d),
  (e)), and it holds over 𝒜 **without exception**. Its authority boundary is
  the decided boundary of route (iii-a).
* **CX-4 stays, honestly, outside 𝒜.** It needs a root `stop` that is not
  route (iii-a), or an orderly transition that A-2 forbids, during the first
  attempt's `start-pre`, plus PO-21 (u), τ₀ = `0` and an unload. It is an SL-1
  kind residual, not an authorized-path exception. Even then no grant exists
  during or after a pass (§4.2.5-R6 (f)). One D3-R5 claim, that OS-4 covers an
  orderly transition, is corrected there.
* **Preserved:** the D3-R5 SB-1, SB-2 and SB-3 mechanism, the CQ order, the
  shared lock and OS-5, the start timeout, and every proposed proof
  obligation. None is added, removed or re-worded.

**Recommendation.** Codex re-reviews §4.2.5-R6 and the D3-R6 notes, using
§17.9. No host step is released by this revision.

### 0-R5. D3-R5 outcome *(D3-R5, 2026-10-04)*

*(D3-R6 note.)* §0-R5 is history. OS-6 is no longer a D3-R5 refinement but
Peter's decided amendment to route (iii-a), and CX-4 is not an exception to
contract OSA within the authority boundary but a residual outside it. §0-R6
and §4.2.5-R6 govern.

**DESIGN REMEDIATION READY FOR RE-REVIEW.**

`OH-H1-D3-R4-1` is addressed in design by §4.2.5-R5. It is **not** declared
closed. `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` also remain open.
Only Codex may recommend closure, and Peter Duscha retains acceptance
authority.

* **The defect is confirmed.** D3-R4's CP created its one-shot name only at
  CP-4, so failures at CP-0, CP-1 and CP-2, and any death before CP-4, left no
  barrier (§4.2.5-R5 (a)).
* **The contract is now one start attempt per activation, on every path**
  (contract OSA, §4.2.5-R5 (b)). Three barriers enforce it. **SB-1:** CP's first
  act under the activation lock is the exclusive creation of the claim. **SB-2:**
  PID 1's own record of the capture unit's last entry into `inactive` or
  `failed` (τ), which the holder baselines at AM-0 and re-checks at
  `hold-start`, and which CP requires unchanged. SB-2 covers attempts that fail
  before CP runs a single instruction. **SB-3:** CP succeeds only through its own
  verified removal of the once-linked rule.
* **Identified versus unidentified.** A start that cannot identify an
  activation creates nothing, so an ST-1 root probe is never an activation
  marker. Once CP holds the activation lock, it claims the attempt before any
  check, then removes the grant, then validates ((e) CQ-0 … CQ-7).
* **CP, CL, HL and the backstop agree.** HL now decides its end under the
  same lock (OS-5), CL records the attempt's class, and no repeated start can
  race cleanup into `ExecStart=` ((g)).
* **Preserved:** the decided OH-D-10 (A) with route (iii-a), the unit and rule
  bytes, the root `ExecStartPre=` consume before `ExecStart=`, GP-R3, ST-1.ur,
  M-B, automatic cleanup and the separately authorized RB-1.
* **New proof obligations, not host facts:** PO-21 (s) … (v) and PO-20 (h)
  ((j)). AP-0 is INVALID RUN, and no grant is linked, unless each is accepted.
* **One new residual,** CX-4: a root `stop` issued against A-2's terms during
  the first attempt's `start-pre` can, in one narrow combination, defeat SB-1
  and SB-2. Even then no grant exists during or after a pass ((k)).

**Recommendation.** Codex re-reviews §4.2.5-R5 and the D3-R5 notes, using
§16.9. No host step is released by this revision.

### 0-R4. D3-R4 outcome *(D3-R4, 2026-10-04)*

*(D3-R5 note.)* §0-R4 is history. Its statements that CP is one-shot (first
bullet) are corrected by §0-R5 and §4.2.5-R5, which governs.

**DESIGN REMEDIATION READY FOR RE-REVIEW.**

`OH-H1-D3-R2-1` is addressed in design by §4.2.5-R4. It is **not** declared
closed. `OH-H1-D3-R1-1` and `OH-H1-D3-2` also remain open. Only Codex may
recommend closure, and Peter Duscha retains acceptance authority.

* **The grant is `start` only and is consumed before the pass.** The rule
  grants `ubuntu` the verb `start` and nothing else (§4.2.5-R4 (b)). The
  capture unit gains exactly one line, the fixed root step
  `ExecStartPre=+/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume`,
  with no operand and nothing from the requester. That step, CP, removes the
  rule and obtains PK *not authorized* before PID 1 may execute `ExecStart=`
  ((c)). A CP failure leaves `ExecStart=` unexecuted. It is a failed start,
  not a pass ((d)). CP is one-shot and serialized with cleanup on the same lock
  ((c) CP-1, CP-3).
* **OH-D-7 holds literally.** §4.2.5-R4 (i) proves that no grant exists at any
  instant from the `execve` of `ExecStart=` onward, for every terminal cause.
  "After the pass" keeps its plain meaning.
* **Interruption is route (iii-a) only.** The executor, under A-2, issues the
  root literal `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service`.
  The operator has no `stop` route ((e)).
* **Polling is lifetime and recovery machinery only.** HL and the backstop
  establish no grant boundary ((f)).
* **Preserved:** GP-R3, ST-1.ur, M-B (`/run`, cleared at every kernel boot),
  M-S and the automatic cleanup CL, attestation, the separately authorized
  RB-1, OH-D-1 … OH-D-9, and the D3-R1 publication and recovery contract.
* **Proof obligations, not host facts:** PO-21 (n) … (r), PO-11 (g) and the
  matching H-0 facts are fail-closed gates. AP-0 is INVALID RUN, and no grant
  is linked, unless each is accepted ((j)).
* **Eight refinements** (AR-1 … AR-8) close points that §4.2.5-R3 (d) left
  under-specified, such as the lock order and the start timeout. Each fails
  closed ((a)). Three residuals, CX-1 … CX-3, are stated exactly ((k)). None
  of them leaves a grant during or after a pass.

**Recommendation.** Codex re-reviews §4.2.5-R4 and the D3-R4 reconciliations,
using §15.9. If Codex agrees, Codex recommends the disposition of
`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2`, and Peter decides whether to
accept the H-1 and activation design. No host step is released by this
revision.

### 0-R3. D3-R3 outcome *(D3-R3, 2026-10-04)*

*(D3-R4 note.)* §0-R3 is history. Peter decided OH-D-10 as Option A with
interruption route (iii-a), and §0-R4 governs. Its statement that the design
"does not establish 'no live grant after the pass'" is superseded by
§4.2.5-R4 (i).

**BLOCKED REMEDIATION.**

Neither finding is declared closed. `OH-H1-D3-2` and `OH-H1-D3-R1-1` also
remain open. Only Codex may recommend closure, and Peter Duscha retains
acceptance authority.

* **`OH-H1-D3-R2-2` is addressed mechanically** by §4.2.5-R3 (e), grant-priority
  cleanup GP-R3. When evidence cannot be written, CL still removes, in order,
  an A1-intact rule, then an A1-intact `pass-a.json`, then tree **P**'s top and
  any tree **R** directory that `ACT` created. Each removal is preceded by a
  descriptor re-verification of identity and digest. Nothing is claimed
  without a durable record. The host then holds the new state **ST-1.ur**
  (cleared, unrecorded), and every later RP-11 step refuses until a later
  trigger records it. No attributable activation object is left solely
  because a write-ahead line could not be written.
* **`OH-H1-D3-R2-1` cannot be met within the accepted texts.** §4.2.5-R3 (b)
  shows why. C11's rule grants `stop` as well as `start`, so that the operator
  can interrupt a hung pass, and the grant is therefore live for the whole
  pass. The pass can end at any instant (`SIGKILL`, a crash, an OOM kill), and
  every removal of a rule takes effect only after polkitd reloads its rules
  (PO-11 (d)). So **any** design that keeps a grant live while the pass runs
  has a non-zero interval after the pass in which the grant is still live.
  Triggering cleanup by an event instead of by polling shortens that interval
  but cannot make it zero. The only way to close it is for the grant to be
  disabled, and verified disabled, **before** the pass's image runs. That
  needs two changes to reviewed C11 text: a root pre-start step in the
  LB-2S unit, which C11's T-B1 excludes, and a rule that grants `start` only,
  which removes the operator's Polkit route to interrupt a pass. Both are
  outside a design author's authority.
* **The exact maintainer decision** is **OH-D-10** (§4.2.5-R3 (c)). Option A,
  recommended: the grant is consumed at the start, so no grant exists during
  or after any pass, and the route for interrupting a hung pass is chosen
  explicitly. Options B and C are stated with their costs.
* **What D3-R3 withdraws.** D3-R2's latency bound and its proof step that "HL
  ends at the pass's terminal state" are withdrawn as claims about the grant
  boundary (§4.2.5-R2 (g), (n) 3). Until OH-D-10 is decided and a successor
  remediation adopts it, **this design does not establish "no live grant after
  the pass"**, and no text in it relies on polling for that boundary.
* **Preserved.** OH-D-1 … OH-D-9; the D3-R1 publication and recovery contract
  (PF, PT, the journal, RS-1, G-R1, P-1 and P-2); the separately authorized
  RB-1; D3-R2's boot-cleared `/run` placement (M-B) and PID-1 supervision
  (M-S); and every proof obligation already defined.

**Recommendation.** Codex re-reviews §4.2.5-R3, with emphasis on the
impossibility argument of (b) and on GP-R3 in (e), using §14.9. If Codex
agrees, Peter decides OH-D-10. The smallest safe successor is then one narrow
repository-only remediation, R4, that adopts the chosen option into
§4.2.5-R2 and C11's unit and rule text. For Option A, §4.2.5-R3 (d) already
specifies it at the required mechanical level. No host step is released by
this revision.

### 0-R2. D3-R2 outcome *(D3-R2, 2026-10-04)*

*(D3-R3 note.)* §0-R2 is history. Codex found its "no grant after the pass"
claim Blocking (`OH-H1-D3-R2-1`) and its GP incomplete (`OH-H1-D3-R2-2`).
§0-R3 governs.

**DESIGN REMEDIATION READY FOR RE-REVIEW.**

Blocking finding `OH-H1-D3-R1-1` is addressed mechanically by §4.2.5-R2. It
is **not** declared closed. `OH-H1-D3-2` also remains open. Only Codex may
recommend closure after independent re-review, and Peter Duscha retains
acceptance authority.

* **Boot scope (M-B).** The active rule and `pass-a.json` move from `/etc` to
  the `/run` tmpfs. Neither can exist in any boot after the one in which
  `ACT` created it, whatever happens to any process. Power loss, a hard reset,
  a panic and every kernel reboot are therefore covered by host semantics,
  not by a procedure (PO-20 (g), PO-21 (g)).
* **Supervision (M-S).** `ACT`, the wait for the pass's terminal state and
  cleanup run in a transient system service supervised by PID 1, created
  under A-2. Its `ExecStopPost=` runs cleanup CL, grant first, whenever its
  main process ends, for any cause. A transient backstop timer re-runs CL
  every R seconds until a terminal record exists. Session loss does not
  affect either unit (PO-21).
* **Residual RR-2 is withdrawn**, together with every statement that cleanup
  after a death or a reboot waits for the next actor. After an unclean
  kernel boot, only the **record** waits: an attestation that disables
  nothing, because the boot has already removed the files. Every later RP-11
  step refuses until that record exists.
* **Preserved.** OH-D-1 … OH-D-9, the D3-R1 publication and recovery contract
  (PF, PT, the journal, RS-1, G-R1 and the proofs P-1 and P-2), the separately
  authorized RB-1 and the immutable records. New proof obligations PO-11 (f),
  PO-20 (g) and PO-21 are fail-closed: without them no grant is ever linked.

**Recommendation.** Codex re-reviews §4.2.5-R2, §4.4.2b and §13, using §13.9.
The remediation needs no new maintainer choice. If Codex accepts it, the
D3-R1 next decisions stand (§5), and PO-21, PO-11 (f) and PO-20 (g) join them.
No host step is released by this revision.

### 0-R1. D3-R1 outcome *(D3-R1, 2026-10-04)*

*(D3-R2 note.)* §0-R1 stands, except for its activation-cleanup statements.
Those are superseded by §0-R2 for death, session loss, power loss and reboot.

**DESIGN REMEDIATION READY FOR RE-REVIEW.**

Both Blocking findings are addressed mechanically. Neither is declared closed:
only Codex may recommend closure after independent re-review, and Peter Duscha
retains acceptance authority.

* **`OH-H1-D3-1`.** §4.2.4 is replaced by a write-ahead,
  identity-before-name publication protocol (§4.2.4-R1). The root tool durably
  journals each object's `(st_dev, st_ino)`, digest, size, owner and mode
  **before** any name that recovery may remove can exist. Files are created as
  unnamed `O_TMPFILE` inodes and linked under their final name only after that.
  New directories are assembled under a run-unique temporary name and moved to
  their final name by one `renameat2(RENAME_NOREPLACE)`, again only after their
  identity is durable. Recovery (§4.6.2-R1) removes only an object whose current
  identity **and** digest equal a durable journal record. Losing or corrupting
  journal lines can therefore only reduce what recovery removes. It can never
  cause an unrelated object to be removed. §4.6.2-R1 proves that a later H-1 is
  not blocked by anything this protocol can attribute, and that it refuses to
  remove anything it cannot.
* **`OH-H1-D3-2`.** §4.2.5 is replaced by a complete `ACT`/`DEACT` contract
  (§4.2.5-R1). It defines the activation identifier and its one-pass, one-boot
  binding; evidence paths; a closed activation-record schema; the exact
  bindings to A-2, the H-1 and H-2 records, the boot ID, `pass-a.json`, the
  staged rule and the active rule; publication by the same protocol; every
  partial state; and the automatic activation cleanup that OH-D-7 and OH-D-8
  pre-authorize. Cleanup removes the live rule **first** and then
  `pass-a.json`, and claims that the grant is removed only after a journaled
  removal, a path check and a privileged `pkcheck` decision. That decision must
  differ from the one recorded at activation. Every terminal path ends in
  verified ST-1, or in a HARD STOP that names each residual object and the
  grant's exact state.
* **Accepted decisions.** OH-D-1 … OH-D-9 are recorded as decided in §3 and
  applied throughout. H-1 installation rollback (RB-1) remains separately
  authorized and is never automatic. Activation cleanup is automatic.

**Recommendation.** Codex re-reviews §4.2.4-R1, §4.2.5-R1, §4.6.1-R1 and
§4.6.2-R1 against the two findings and the focus list in §12.9. If the design
is accepted, the next decisions are the §4.7.1 wordings and the acceptance of
PO-19, PO-20 and the PO-11 extensions (§5). No host step is released by this
revision.

### 0-D3. Original D3 outcome (2026-10-04, retained; superseded by §0-R1)

**BLOCKED DESIGN.**

The H-1 installation part of the amendment can be fully specified, and it is
specified in §4.2 to §4.6. That covers the staged and activation states, the
paths and modes, the publication algorithm, the H-1 record, the H-0 fact set,
the local launcher rebuild and the failure and rollback rules. It needs no
decision beyond those already taken (U-2, U-4 … U-10), with one exception,
OH-D-7.

The amendment as a whole cannot be finished yet. Making `oracle-test` both the
installation host and the **evidence host** breaks several properties of the
Pass A evidence contract. Those properties held only because the controller
and the target were different machines. Restoring or replacing each one is a
new evidence, authorization, credential or rollback semantic. The assignment
forbids me to choose those (assignment, "Required outcome"). There are nine
decisions, OH-D-1 … OH-D-9, set out in §3. Each has its options, a non-binding
recommendation and the smallest safe successor that resolves it. The five
that most constrain the work are:

1. **The capture root moves onto the observed host.** RP-11 requires *"a
   fixed, pass-specific capture root on the repository host … with no file
   created on `oracle-test`"*. On one host that cannot hold (OH-D-3).
2. **Pass A's one mutation, the §5 `rsync`, has no meaning inside a one-host
   pass.** Removing it from the pass changes Pass A's evidence and
   authorization rows, and with them RP-11's synchronization-capture
   requirement (OH-D-4).
3. **Five Pass A acts use `sudo`.** These are A1-14, A1-15 and A1-31 … A1-33.
   Locally they would run under the unit's `NoNewPrivileges=yes`, which makes
   `sudo` fail (OH-D-5).
4. **The documented route for repository bytes onto `oracle-test` starts on
   the repository host.** The repository's records treat that host as the
   production server (§3, OH-D-1), and the assignment requires that the
   production server is **never a source**.
5. **`ubuntu` has passwordless `sudo` for every command.** U-8's separation
   between installation and activation can therefore be an authority boundary
   only, not a privilege boundary, on this account (OH-D-6).

**Recommendation.** Peter should take the decisions in the order of §4.7.4.
OH-D-1 and OH-D-2 come first, because H-0 needs them and nothing else. The
H-1 sections of this proposal (§4.2 to §4.6) can be reviewed now, independently
of the Pass A blockers. Because the unit text in §4.2.6 keeps
`NoNewPrivileges=yes` under OH-D-5's recommended option, the H-1 file bytes do
not depend on how the Pass A blockers are resolved. Codex can therefore review
H-1 in parallel with Peter's evidence-semantics decisions.

*(D3-R1 note.)* The paragraphs of §0-D3 are history. Peter Duscha decided
OH-D-1 … OH-D-9 on 2026-10-04 (§3). Codex found that, contrary to §0-D3, the H-1
portion was **not** fully specified (`OH-H1-D3-1`, `OH-H1-D3-2`). The
rsync route of item 4 is prohibited by OH-D-1.

---

## 1. Requirements and governing sections examined

| Source | SHA-256 | Read |
|---|---|---|
| `.agents/AGENTS.md` | — | completely |
| `docs/implementation-plan.md` | — | reading map, §0, §16, §20 |
| `docs/review/Handover information` | — | completely; active restriction: repository-only, no SSH, host, build, install, H-0/H-1/H-2 or pass authority |
| assignment and authority (above) | as above | completely |
| topology correction (above) | `c9889058…52f5a23` | completely; U-1 and U-3 superseded |
| `project-review-2026-10-04-p5-r5-rp11-h1-prerequisite-decisions.md` | `17a32ab4…57b9cc` | completely; U-2 and U-4 … U-10 effective |
| `project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation.md` | `49dfea85…6e741d` | completely |
| `phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md` | `5c118cc7…0dbc59` | completely; §§2–6 and the P-1 … P-10 matrix |
| `project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md` (D1-R2) | `10daa599…c3b40` | completely: M-14 design, M-9 = LB-2S **conditional**, M-10 |
| `project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md` (D2-R2) | `133191c5…87c678` | completely: LD-7 … LD-9 |
| C11 proposal `phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md` | `f6405cd9…12f70b` (equal to the value D2 cites) | header, §0-R2, §1, §2.2, §2.3, §4.1 … §4.4.7 (all of §4.4.3), §5.1 … §5.4, §6.5, §6.6, §6.8, §6.9, §7.1 … §7.4, §7.9, §8, §9, §11 … §15 |
| D2 proposal `phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md` | `4859ab4e…366174` | header, §0 … §3, §5.3.5, §5.3.6, §5.4, §5.11, §5.13, §6.1 … §6.3; §5.14 and §5.15 by section title and premise references only |
| I-7 review `project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md` | `dd5a0833…c7d755d` | the XD-11 / D9-2 passages (decoder `48594e41…c04e3e`, stream `eb9c584a…500b1a`, 332/332) |
| I-7-R1 acceptance `project-review-2026-10-01-p5-r5-rp11-i7-r1-acceptance.md` | `bc14d8f9…7a2928` | identity only; it is cited for D9-2's unchanged evidence |
| R5 acceptance and R5 handback | handback `6e94b7cb…1afb2c` | acceptance completely; handback lines 202, 532 and S11 by search only (recorded `oracle-test` facts, used as context) |
| R5 assignment `phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md` | — | §5 and steps 4 … 7 (freshness, synchronization, provisioning, R-1/R-2), for the local-rebuild design |
| operational draft `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | `5c6046fc…dcca7de6` | §0 … §4.2, the RP-11 row of §4.4, the `MI.capture_root_*` rows, §5, §6 complete |
| `docs/operations/disposable-test-server.md` | `7339dea5…509737` | completely, including the active banner |
| `phase-5-0-evidence-harness-review-manifest.json` | `b9f03a47…ed14817a` (v31) | the `rp11_launch` section: `installed: false`, `wired: false` |
| `infra/rp11-launch/` | `expected.sha256` file `6e87a542…a83625` | inventory; `expected.sha256` |
| `tools/phase_5_0_evidence/capture_contract.py` | — | `canonical_bytes` only (serialization convention reused in §4.3) |

**Naming collisions kept distinct.**

* Static-launcher **H-1** (installation) and **H-2** (pre-pass check) are not
  any RAID item or finding with those names.
* Static-launcher **R-5** (accepted; D9-3 Complete) is not package RAID item
  **`P5.0-R5`**, which remains Blocking.
* The handback's prerequisite rows **P-1 … P-10** are written here as
  "handback P-n". They are not D2 §6.1's PO-9 premises P-1 … P-7, which are
  written "D2 premise P-n".
* C11's systemd semantics **S-1 … S-10** are not D2's launcher steps S-3 … S-9,
  and neither is this proposal's successor sequence, which is named
  **OH-S0 … OH-S9**.
* C11 decisions **D-1** and **D-2** are not the I-7 discrepancies with the
  same names.
* This proposal's new identifiers are **OH-D-n** (decisions), **IA-n**
  (invalidated assumptions), **ST-n** (installation states), **HF-n** (H-0
  facts), **PB-n** (Pass B items), **TR-n** (trace steps) and **PO-19**. A
  repository search found none of them in use.

---

## 2. Assumptions invalidated by the one-host topology

Each row is an assumption whose truth depended on the controller (the
"repository host") and the target (`oracle-test`) being different machines.
Under **Disposition**, *removed* means the topology deletes the need for it,
*restated* means it carries over with a new subject, and *decision* names the
OH-D item that must resolve it.

| # | Assumption in the accepted or proposed text | Where | What changes on one host | Disposition |
|---|---|---|---|---|
| IA-1 | The capture root is on the repository host, and no file is created on `oracle-test` | draft RP-11 row; `MI.capture_root_A/B`; §6.2 | The entry runs on `oracle-test`, so its capture root must be there. Evidence about a host is recorded on that host, on its filesystem, under its clock, and is subject to its failures | **decided OH-D-3** *(D3-R1)*: a pass-specific capture root on `oracle-test`, on a filesystem accepted after H-0 and review; the loss of observer and clock independence is explicit evidence semantics |
| IA-2 | Pass A's only target mutation is the §5 `rsync` from the repository host, issued inside the pass and captured by RP-11 (A1-00, AUTH-SYNC). C-11 exists mainly so that this `rsync` is captured without changing what `guard-secrets.py` inspects | draft §5, §6.2; C11 §5.1, §5.3 | On one host the source and destination of that command coincide. Any synchronization needs a second host, which the assignment forbids during the pass | **decided OH-D-4** *(D3-R1)*: Pass A contains no synchronization act; retrieval happens before the pass, outside the trusted path (§4.1.4) |
| IA-3 | Every A1 act is `ssh oracle-test "…"`. A **remote** shell interprets the quoted text, so local `NoNewPrivileges` does not affect remote `sudo`, and local `argv` is just `ssh` plus one string | draft §6.2; C11 §6.6 (`program` ∈ {`rsync`, `ssh`}), §9 `PROGRAM_PATHS` | Acts run locally as children of the entry, with no shell (G-3). Texts with `cd … &&` (A1-S1, A1-S2) need re-expression. `sudo` acts fail under the unit's `NoNewPrivileges=yes` (C11 §4.4.3.4; S-9) | **decided OH-D-5** *(D3-R1)*: `NoNewPrivileges=yes` stays; A1-14, A1-15 and A1-31 … A1-33 are `not_run (one-host: no privilege in RP-11)`; catalogue re-expression (OH-S3) |
| IA-4 | SSH authentication, host-key trust and client configuration matter: M-1, M-3, M-4, PO-1 … PO-3, R-3, `SSH_AUTH_SOCK`, C11 §7.4 … §7.6 | C11 §7, §13, §14 | No `ssh` or `rsync` runs in the pass | **removed** (§4.7.2) |
| IA-5 | The client's clock is independent of the target's. *"UTC timestamps in the handback are taken from the client"*, and A1-10 records whether the **host** clock is synchronized | draft A1-10; C11 §7.2 `TZ` row (record times come from the entry's clock) | Client, entry and target share one clock. A1-10 now records whether the recording clock is itself synchronized | **decided OH-D-3** *(D3-R1)*: the loss of clock independence is accepted as explicit evidence semantics |
| IA-6 | The capture session survives anything that happens to the target. That matters for Pass B's supervised reboot (B6) and its destructive bands | draft §7; C11 F-2, F-4, M-11 | A per-pass entry on `oracle-test` dies with a reboot. Destructive bands share a filesystem with the capture root | **out of M-11 scope**; recorded as PB-1 … PB-4 (§3.10) |
| IA-7 | The operator account on the H-1 host is unprivileged apart from its polkit grant, so root ownership of the five files protects them from the operator | C11 §4.4.3.4, §4.4.2 TOCTOU row; D2 §5.11 | `ubuntu` has `NOPASSWD: ALL` (`disposable-test-server.md` §1). The R5 handback (line 532) also records membership of `sudo`, `adm` and `lxd`, which is context and not an H-0 observation. Root ownership still stops unprivileged writes, but not the account itself | **decided OH-D-6** *(D3-R1)*: an authority boundary, not a privilege boundary; no record may call ST-1 privilege-inert |
| IA-8 | The canonical repository, and therefore every expected digest, sits on the controller. The executor compares target bytes against values read on the trusted side | R5 steps 1, 4b … 4d; draft A0 | Expected values (commit, manifest digest, `04218ed2…2668572`, assignment SHA-256) reach `oracle-test` by the same transport as the bytes they authenticate. Against T-A (accidental drift or corruption) the comparison still works. Against transport tampering it does not, but that is T-B, which M-10 places out of scope | **restated**: stated residual RR-1 (§9). *(D3-R1)* Under OH-D-1 the bytes arrive by direct Git retrieval from the canonical remote and are verified locally against the accepted commit and pinned file digests before use |
| IA-9 | The H-1 host's architecture and kernel are unknown (D2 OD-5, OD-6, AD-1, AD-2) | D2 §2 | The H-1 host is the documented `x86_64` server, kernel `7.0.0-31-generic`. That is documentation, not observation, and H-0 re-observes it. PO-18's ≥ 5.9 condition is expected to hold. D9-1 cites the 7.0 series | **restated**: H-0 HF-04, PO-18 |
| IA-10 | The client hook (C-3) and the entry read the same root-owned `pass-a.json` on the repository host | C11 §4.2 C-3, §9 hook rules | Still one host, now `oracle-test`. This holds **only if the operator's client also runs there**. A client elsewhere would have to wrap the invocation in `ssh`, and the hook's exact grammar would then refuse it as a near match (`rp11-capture-`) | **decided OH-D-2** *(D3-R1)*: operator and executor processes run locally on `oracle-test` as `ubuntu`, reached through an interactive login session; no scripted remote controller |
| IA-11 | The pass's handback is written where the canonical repository lives | draft §14; R5 §5 table | The handback and the H-0/H-1 records are produced on `oracle-test` and must return to the canonical repository and to Codex | **decided OH-D-9** *(D3-R1)*: the retained file on `oracle-test` is authoritative; its SHA-256 and byte length bind every returned copy |
| IA-12 | `oracle-test:/opt/freedom-blades/platform` is *"a synchronized tree of unrecorded provenance, which must not be read, used or modified"* (R5 §5) | R5 §5 | It becomes the RP-11 repository root that the bootstrap reads and verifies. Its provenance does not matter **inside** the trusted path, because the bootstrap verifies every covered source against the root-owned pinned digest (C11 C-6). It does matter for A0-02 and for the rebuild's controlled checkout | **restated**: §4.1.4, §4.5 |
| IA-13 | The PO-16 drill *"may run only on a host where a manager-wide change is permitted"*, implicitly not the repository host | C11 §4.4.3.7 | `oracle-test` is disposable, so the drill is now possible on the same host as the installation. It then mutates the manager of the host holding the H-1 state | **restated**: PO-16 ordering rule (§4.6.4) |
| IA-14 | H-1 is root work by an executor with the exact required privilege (U-2), separate from the operator | prerequisite decisions U-2 | The executor obtains root through `ubuntu`'s own `sudo`. The installer, the activator and the operator are one account | **decided OH-D-6** *(D3-R1)* (authority boundary) |
| IA-15 | Retained R4/R5 evidence lives on a host other than the H-1 host | handback §2.2; R5 §5 | Retained paths `/var/tmp/p5-r5-fresh-20261003T234834Z-4fc93046-*` and `/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-*` share the host and the `/var/tmp` filesystem with the rebuild, the staging and H-1 | **restated**: exclusion rules (§4.5.3) |

Assumptions that did **not** depend on separate hosts are unchanged:

* S-8: `systemctl start` carries no requester state;
* PO-9, PO-14 and LB-2S's environment argument;
* `rp11-entry-env/1`;
* the bootstrap's covered-source verification; and
* M-10's T-A/T-B scope.

LB-2S's own guarantee is independent of how the operator's session reaches the
host. That is what lets the transport stay outside the trusted path (§4.1.3).

---

## 3. Blocking analysis — maintainer decisions still required

Each item states the contradiction, the options, a **non-binding**
recommendation and the smallest safe successor. None is decided here.

*(D3-R1.)* **All nine items are now decided.** Peter Duscha accepted OH-D-1 …
OH-D-9 on 2026-10-04
([decision record](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md),
SHA-256 `8edb27db385622bac2f4995d7eedbf9fcec6052fb2d3cc29b9139da5b7afa15c`).
The D3 analysis below is kept as the history of each choice. Each item ends
with a **Decided** line that quotes the accepted disposition, and that line
governs. Where the decision differs from the D3 recommendation, the line says
so. The heading's "still required" is D3 wording and no longer applies.

### 3.1 OH-D-1 — the source and transport of repository bytes onto `oracle-test`

**Contradiction.** The assignment requires that the production server is
never a *source*. The only documented route for repository bytes onto
`oracle-test` is `rsync … /opt/freedom-blades/platform/ oracle-test:…` from
the host holding the working repository (`disposable-test-server.md` §3.2,
used by R5 step 4b). The records treat that host as the production server:

* C11 §12 and D2 OD-5 place H-1 on "the repository host";
* the superseded U-1 then named the production server as the H-1 launcher
  host; and
* `disposable-test-server.md` describes the SSH configuration as living on
  "the primary development/staging server".

This proposal inspected no host and does not assert the identity. It only
records that **no repository document establishes that the repository host is
not the production server.** The rebuild (U-4) needs a verified controlled
checkout on `oracle-test`, and so does every later pass.

**Options.**

* (a) A named non-production host as the sole synchronization source, with
  Peter's attestation of its role.
* (b) `git` retrieval on `oracle-test` from the canonical remote at a pinned
  commit. That needs a read credential on `oracle-test`, which is a credential
  decision.
* (c) Peter transfers a `git bundle` or archive himself, and the receiving
  steps verify it.
* (d) Peter attests that the repository host is not the production server, in
  which case the documented `rsync` remains admissible as a **pre-pass**
  step.

**Recommendation.** (d) if true; otherwise (c). Under every option the bytes
are authenticated **on `oracle-test`** against reviewed digests (§4.1.4,
§4.5.2), so the transport stays outside the trusted path.

**Successor.** One line in the OH-S0 decision record.

**Decided 2026-10-04 (D3-R1).** *"The current workspace host is the
Freedom-Blades production server and is prohibited as a source, controller,
relay, destination, fallback or rollback target. `oracle-test` retrieves the
pinned commit directly from the canonical Git remote. Public read access is
used if available. If authentication is required, a narrowly scoped read-only
repository credential may be used only after its own explicit installation and
handling authority. Received bytes are verified locally against the accepted
commit and pinned file digests before use."* This is option (b), not the D3
recommendation. Options (a), (c) and (d) are **not selected**. Option (d)'s
premise is false, so the documented `rsync` from the workspace host is
prohibited for this workflow. The decision does not itself authorize network
access or a credential on `oracle-test`.

### 3.2 OH-D-2 — where the operator's and executors' client processes run, and how they reach `oracle-test`

**Contradiction.** One-host execution requires the client process that issues
`/usr/bin/systemctl …`, together with its hook and its catalogue and
`pass-a.json` reads, to run **on `oracle-test` as `ubuntu`** (IA-10). The
H-0, rebuild and H-1 executors likewise run their commands there. The
repository does not record whether an agent client (Claude Code,
Antigravity/Gemini) is present on `oracle-test`. Installing one, together with
its model-provider credential, would be a host change and a new credential on
the target. Running the client elsewhere and driving `oracle-test` through a
scripted `ssh oracle-test bash -s` (the R5 runner pattern) would be the
separate controller that the topology correction removes.

**Options.**

* (a) An agent client installed on `oracle-test` and run as `ubuntu`, with its
  credential held there. That needs separate installation authority and
  Peter's acceptance of that credential on a disposable host.
* (b) An interactive login session, console or SSH, in which the client runs
  **on `oracle-test`**. The login transport carries no client state into the
  entry (S-8), so it is outside the trusted path.
* (c) Remote scripted control: **rejected** by the topology correction.

**Recommendation.** Peter states which of (a) or (b) applies to each role
(H-0, rebuild, H-1 executor, pass operator). H-0 records the client's presence
as a fact, not as a precondition the executor may satisfy by installing
something.

**Successor.** OH-S0, before H-0.

**Decided 2026-10-04 (D3-R1).** *"Operator and executor processes run locally
on `oracle-test` as `ubuntu`, reached through an interactive login session. No
scripted remote controller is used. No model-provider credential is installed
on `oracle-test` without separate authority."* This is option (b) for every
role. Option (c) stays rejected.

### 3.3 OH-D-3 — capture root on the observed host, and a shared clock

**Contradiction.** RP-11 and `MI.capture_root_A` place the root on the
repository host, with *"no file created on `oracle-test`"*. One-host execution
places it on `oracle-test`. The evidence then lives on the host it describes:

* a full disk, a filesystem fault or an fsync anomaly affects the evidence and
  the subject together; and
* timestamps come from the subject's clock (IA-5).

Under M-10, T-B forgery was already out of scope, so this is not a new
integrity loss against an adversary. It is a loss of observer independence
against T-A, and that is an evidence-semantics change.

**Options.**

* (a) Accept the capture root on `oracle-test`. The constraints are proposed
  in §4.1.5:
  * an absolute path outside `/opt/freedom-blades/platform`, `/tmp`,
    `/var/tmp/p5-r5-fresh-*`, `/var/lib/fb-evidence-p5-0` and the RP-11
    installation paths;
  * a filesystem accepted under RP-11's review; and
  * A1-10 restated as self-observation.
* (b) Keep an independent observer. That needs a second host, which the
  topology correction rules out for this workflow.

**Recommendation.** (a), with A1-Z's sentence *"Pass A created nothing on the
target except the synchronized worktree"* replaced by one that accounts for
the capture root and the activation files.

**Successor.** OH-S0 decision, then the OH-S3 draft amendment.

**Decided 2026-10-04 (D3-R1).** *"Accept a pass-specific capture root on
`oracle-test`, on a filesystem accepted after H-0 and review. The loss of
observer and clock independence is explicit evidence semantics, not silently
preserved from the two-host design."* This is option (a), as recommended.

### 3.4 OH-D-4 — Pass A synchronization leaves the pass

**Contradiction.** A1-00 cannot run inside a one-host pass (IA-2). Without
it, AUTH-SYNC has nothing to grant, RP-11's requirement to capture the §5
synchronization has no subject, and Pass A becomes read-only.

**Options.**

* (a) The synchronization becomes a **pre-pass** step outside RP-11 and
  outside the trusted path, and its result is verified inside the pass. A1-S1
  and A1-S2 already do this. They are re-expressed locally, and the
  bootstrap's manifest check covers the covered sources.
* (b) Keep a captured synchronization in the pass. That needs a source host
  during the pass, which the assignment forbids.

**Recommendation.** (a). C-11's guard-preservation requirement then applies to
each local Pass A act, and the pre-pass `rsync` is inspected by the client
hook on the ordinary path wherever it runs, as today.

**Successor.** OH-S0, then OH-S3.

**Decided 2026-10-04 (D3-R1).** *"Pass A contains no synchronization act.
Retrieval/synchronization occurs before the pass and outside the trusted
execution path; the trusted path verifies the resulting bytes."* This is option
(a). Under OH-D-1 the pre-pass step is direct Git retrieval on `oracle-test`,
not the `rsync` that the recommendation's last sentence mentions.

### 3.5 OH-D-5 — `sudo` acts under `NoNewPrivileges=yes`

**Contradiction.** A1-14 and A1-15 (A1-C, corroborative) and A1-31 … A1-33
(AUTH-DBREAD, optional) invoke `sudo`. As children of the entry they inherit
`NoNewPrivileges`, so `sudo` cannot elevate and the act fails. Removing
`NoNewPrivileges` would let any descendant of the entry become root through
`ubuntu`'s `NOPASSWD` rule. `sudo` would then also merge its PAM environment
into those children (AS-12), breaking `rp11-launcher-env/1` for them.

**Options.**

* (a) Keep `NoNewPrivileges=yes`. Record A1-14, A1-15 and A1-31 … A1-33 as
  `not_run (one-host: no privilege in RP-11)`. Pass A loses the corroborative
  `sudo` observations and the optional database baseline.
* (b) Re-express A1-31 and A1-32 without `sudo`, using `ubuntu`'s own
  PostgreSQL peer role. The documentation records that role as superuser,
  which changes the role used and the privilege exercised. A1-33 stays
  impossible, because `pg_hba.conf` is not readable by `ubuntu` on the
  documented layout. That is not verified.
* (c) A second, separately reviewed root unit for read-only root
  observations. That is new architecture.
* (d) Drop `NoNewPrivileges`: **not recommended**.

**Recommendation.** (a). The unit bytes in §4.2.6 assume (a) or (b).

**Successor.** OH-S0, then OH-S3.

**Decided 2026-10-04 (D3-R1).** *"Keep `NoNewPrivileges=yes`. A1-14, A1-15
and A1-31 through A1-33 are recorded `not_run (one-host: no privilege in
RP-11)`. Do not weaken the unit to run them."* This is option (a). Option (b) is
not selected.

### 3.6 OH-D-6 — `ubuntu`'s unrestricted `sudo` versus U-8 and root ownership

**Contradiction.** U-8 requires that H-1 leaves no usable polkit start grant
before pass authorization. §4.2 meets that **technically** for the polkit
path, and adds a second technical absence: there is no pass configuration, so
the bootstrap refuses before X-1. But `ubuntu` can `sudo systemctl start` the
loaded unit, or `sudo` install anything. Separating staging from activation is
therefore an authority control on this account. It is not a privilege
control. The same holds for root ownership of the installed files (IA-7) and
for U-2's "exact required privilege" (IA-14).

**Options.**

* (a) Accept this, with the property stated exactly as above.
* (b) Narrow `ubuntu`'s `sudo` (and `lxd`) before activation. That is a host
  configuration change, which affects every other disposable-server workflow.
* (c) A dedicated operator account. That contradicts U-3 and is excluded.

**Recommendation.** (a). Write the property into the H-1 and pass
authorizations verbatim, so that no record ever calls ST-1 privilege-inert.

**Successor.** OH-S0.

**Decided 2026-10-04 (D3-R1).** *"Accept that staging and activation
separation is an authority boundary, not a privilege boundary, because
`ubuntu` has unrestricted sudo on the disposable host. Every later record must
state that limit and must not call ST-1 privilege-inert."* This is option (a).
The H-1 record, the activation record (§4.2.5-R1) and A-2 carry the fixed
`authority_limit` sentence of §4.2.5-R1.

### 3.7 OH-D-7 — authority for activation and deactivation

**Gap.** U-8 requires *"an explicit reviewed amendment"* separating
installation from activation. §4.2.2 specifies:

* ST-1, staged and inert, reached by H-1;
* ST-2, activated, reached by a separate step `ACT`;
* the return from ST-2 to ST-1, a step `DEACT`; and
* the order H-2 → A-2 → `ACT` → start.

Two questions remain:

* who authorizes `ACT`. The proposal is the pass authorization A-2 itself, so
  that no grant exists before it; and
* whether `DEACT` runs **automatically** at the pass's terminal state, under
  the same authority, or only under separate authority.

**Recommendation.**

* `ACT` is authorized only inside A-2, for one pass and one boot.
* `DEACT` runs automatically under A-2 immediately after the pass's terminal
  state, removing the rule first. Leaving the grant standing after the pass
  would recreate U-8's concern.

**Successor.** OH-S0.

**Decided 2026-10-04 (D3-R1).** *"A-2 authorizes `ACT` for exactly one pass and
one boot. `DEACT` is mandatory and automatically authorized at every terminal
state. No live Polkit grant may exist before A-2 or remain after the pass."*
This is the recommendation. §4.2.5-R1 makes it mechanical.

### 3.8 OH-D-8 — automatic or separately authorized rollback

**Gap.** The handback (§2.7) and the preparation review left open whether
rollback is automatic. §4.6 specifies a digest-guarded rollback for every
state.

**Recommendation.**

* **No automatic rollback of H-1.** A HARD STOP leaves the state as found,
  records it and reports it. Rollback RB-1 then runs only under a separate,
  explicitly authorized step, using the pre-reviewed procedure.
* **One exception, for activation.** If `ACT` or the pass ends with the polkit
  rule in place, the same authority removes **only the rule**, digest-guarded,
  at once. This is D2 §5.13's "emergency disable", and without it U-8 would
  be violated.

This matches the evidence-preservation practice of R4/R5 (stop, record, never
repair).

**Successor.** OH-S0.

**Decided 2026-10-04 (D3-R1).** *"H-1 installation rollback is not automatic
and requires separate authority so failure evidence remains intact. Activation
cleanup is automatic and pre-authorized by A-2: on ACT failure or pass
termination it removes both the live Polkit rule and `pass-a.json` under a
crash-consistent, digest- and identity-guarded procedure, while retaining an
immutable activation/failure record."* This **differs** from the D3
recommendation's exception, which removed only the rule and left `pass-a.json`
to a separate authority. That narrowing is withdrawn. §4.2.5-R1 and §4.6.2-R1
implement the decision.

### 3.9 OH-D-9 — the return path for handbacks and records

**Gap.** H-0, the rebuild, H-1 and pass handbacks are written on
`oracle-test`. Codex reviews, and the canonical repository records, elsewhere.

**Options.**

* (a) The executor commits nothing, and Peter transfers the handback files.
* (b) The handback is returned through the client transcript as text, with its
  SHA-256, and the retained file stays on `oracle-test`.
* (c) Through OH-D-1's channel in reverse, which is not available if that
  channel is (b) or (c) there.

**Recommendation.** The retained file on `oracle-test` is authoritative. Its
SHA-256 appears in the executor's final message, and the reviewer verifies any
copy against that digest. Under M-10 this is adequate.

**Successor.** OH-S0.

**Decided 2026-10-04 (D3-R1).** *"The retained record on `oracle-test` is
authoritative. The executor reports its exact SHA-256 and byte length, and
every transferred copy is verified against them. No repository-write
credential is implied."* This is the recommendation, with the byte length
added. It applies to handbacks, the H-1 record, the activation records and
the run journals (§4.6.2-R1).

### 3.10 Pass B items (recorded; not decided; outside M-11's Pass A scope)

| # | Item | Why it is not resolved here |
|---|---|---|
| PB-1 | B6's supervised reboot ends a per-pass entry on the same host (F-2). A capture root cannot be reopened (OB-8) | Pass B already needs its own design pass (C11 M-11, F-4). One-host makes the reboot boundary a hard constraint on that design |
| PB-2 | B2's provisioning and `pg_hba.conf` replacement, B4b's `fsync` failure injection and B5's recovery rehearsals all run on the host whose filesystem holds the capture root, and whose `fsync` the §9.5.1 barriers rely on | the same |
| PB-3 | B7's clean-state survey must account for the RP-11 installation (ST-1 files) and both capture roots as target-side changes (§13.1) | the same |
| PB-4 | B0-RA's retention check reads Pass A's root on the same host after the operator account (with `sudo`) has existed alongside it | T-B, out of scope; to be restated in the Pass B design |

---

## 4. The proposed amendment (inactive)

### 4.1 One-host topology and trust boundaries

#### 4.1.1 Roles

| Role | Host | Account |
|---|---|---|
| *(D3-R1)* pre-pass repository retrieval (OH-D-1, OH-D-4) | `oracle-test`, directly from the canonical Git remote | `ubuntu`, no `sudo`; under its own separate authority, and a read-only credential only under separate installation and handling authority |
| H-0 read-only fact collection | `oracle-test` | `ubuntu`, no `sudo` |
| launcher rebuild and staging (U-4) | `oracle-test` | `ubuntu` unprivileged for the build. Root only where the accepted R5 procedure required it (§4.5) |
| H-1 installation (ST-0 → ST-1) | `oracle-test` | executor per U-2. Root through `ubuntu`'s `sudo -n` for the mutation steps only (§4.2.4) |
| H-2 pre-pass check | `oracle-test` | `ubuntu`, no `sudo` (every query is unprivileged; §4.3.4) |
| `ACT` / `DEACT` (ST-1 ↔ ST-2) | `oracle-test` | executor under A-2; root through `sudo -n`. *(D3-R1)* `DEACT` is automatically authorized at every terminal state (OH-D-7), so any actor working under A-2 (the executor, the pass operator or Peter) runs it in an interactive session on `oracle-test` (§4.2.5-R1). *(D3-R2: that sentence is withdrawn. `ACT`, the hold loop and CL run in a PID-1-supervised transient unit created by AP-2. CL is triggered automatically by that unit's end and by a backstop timer, never by an actor reaching the host (§4.2.5-R2). An interactive actor only issues AP-2 and, when no automatic trigger remains, the attestation of §4.2.5-R2 (i), which disables nothing.)* |
| pass operator request | `oracle-test` | `ubuntu`, no `sudo`; the polkit rule is the only grant |
| capture entry | `oracle-test` | `ubuntu` (`User=ubuntu`), `NoNewPrivileges=yes` |
| retained-evidence holder | `oracle-test` | as created; never touched by this workflow |

**U-3 binding.** `⟨MI.operator_account⟩` := `ubuntu` everywhere C11 uses it:
the unit's `User=` and the rule's `subject.user`. H-0 re-observes the
account's UID, primary GID, supplementary groups and the repository's
ownership. The values recorded historically in the R5 handback (line 532) are
`uid=1001`, `gid=1001`, groups `adm`, `cdrom`, `sudo`, `dip`, `lxd` and
`freedomlab`. They are context only and never expected values. Any later
difference from H-0 is a stop that returns to Peter. It is never a licence to
substitute another account (topology correction; prerequisite decisions,
"Consequences").

#### 4.1.2 Production isolation, stated mechanically

The Freedom-Blades production server, including its production Foundry
service, has exactly the following role in every step of this workflow:

| Role | Production server |
|---|---|
| inspected (any read, query, listing or login) | **never** |
| source of bytes, including repository bytes (OH-D-1) | **never** |
| destination of bytes | **never** |
| controller, runner or relay | **never** |
| fallback when `oracle-test` fails | **never** |
| rollback target | **never** |

It is enforced by these mechanisms, each proposed for the named slice:

* **E-1 (every executing assignment).** The first preflight compares the
  local `uname -n` and `sha256sum /etc/machine-id` with the H-0-recorded
  values (HF-01, HF-02), and stops before any other action on a mismatch. A
  mismatch is INVALID RUN and is never re-targeted.
* **E-2 (OH-S4, a repository test).** Every catalogue, block and command
  resource of H-0, the rebuild, H-1, `ACT`, `DEACT`, H-2 and Pass A contains
  no `ssh`, `scp`, `sftp` or `rsync` token. It also contains no `host:path`
  operand: no token matches `^[^/\s]+:` other than literal `--` options. The
  test reads the files and fails on any match.
* **E-3 (every assignment).** A fixed sentence: *"No step contacts, reads from,
  writes to, or falls back to any host other than the local host
  `oracle-test`."*

**A failure is never retried on, redirected to or rolled back on another host
(§4.6.)**

#### 4.1.3 Complete trace from the operator request to the evidence entry (ST-2 only)

*Process* gives the image and account. *Inputs* lists files, descriptors,
environment and credentials. *Privilege* names any transition. *Trusted?*
uses C11 §4.3's stage names.

| # | Process | Inputs | Privilege | Trusted? |
|---|---|---|---|---|
| TR-0 | the operator's interactive login session reaching `oracle-test` (OH-D-2, decided) | login transport, terminal | none | **no.** Outside the trusted path. Nothing it carries reaches TR-4 onward (S-8) |
| TR-1 | the operator's client (T0), as `ubuntu`, running on `oracle-test` | *E_c*; the client's own credential only if separately authorized (OH-D-2, decided) | none | no (T0) |
| TR-2 | the client hooks (T1, Claude only) | *E_c*; the catalogue file in `/opt/freedom-blades/platform` (ubuntu-owned); `/etc/freedom-blades-rp11/pass-a.json` (root-owned; present only in ST-2) | none | defense in depth only |
| TR-3 | the client shell (T2) running `/usr/bin/systemctl --no-ask-password start --wait rp11-capture-pass-a.service` | *E_c*. No operand, digest or path | none | no |
| TR-4 | `/usr/bin/systemctl` (T3, dynamic, *E_c*) | the system-bus socket (`/run/dbus/system_bus_socket`). It sends `StartUnit(name, mode)`, and the bus attaches the kernel's peer credentials (the UID of `ubuntu`). **No environment, descriptor, working directory, limit or confinement** (S-8, PO-8(b)) | none. `--no-ask-password`: no authentication agent | no |
| TR-5 | `polkitd` (root-trusted, R-8) | action `org.freedesktop.systemd1.manage-units`, `unit`, `verb`, subject. The rule `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules` (ST-2 only) returns `YES` for `start`/`stop` of this unit for `ubuntu`. **In ST-1 the rule is absent, and no other rule may grant this action to `ubuntu` without authentication (PO-11(b))** | **the only authorization decision** | R-8 |
| TR-6 | PID 1 (root) | the **loaded** unit configuration: fragment, drop-ins (required empty), manager `Default*=` (R-10, bound at H-1/H-2) | root | R-8, R-10 |
| TR-7 | `systemd-executor` (systemd ≥ 255; AS-13) or a forked PID 1 | PID 1's own environment (PO-14); the execution context PID 1 passes it over a descriptor | root → `ubuntu` via `User=`; `NoNewPrivileges=yes` set; `UMask=0077`; `WorkingDirectory=/`; stdin `/dev/null`; stdout and stderr to journal stream sockets. It assembles the unit's **open** block (S-1) | R-8; **PO-14 load-bearing** |
| TR-8 | `/usr/local/libexec/freedom-blades-rp11/rp11-launch` (static, `ubuntu`, NNP) | the open block, of which **only** `INVOCATION_ID` is read (PO-9; D9-1 … D9-4); descriptors 0–2 checked, ≥ 3 closed; signals reset; `umask 077`; `chdir("/")` | none (NNP) | the earliest component that fixes the entry's environment |
| TR-9 | `/usr/bin/python3.12 -I -S` (dynamic) | the literal `rp11-entry-env/1`; `/etc/ld.so.preload` (required absent: PO-19 and HF-12), `/etc/ld.so.cache`, the libraries it names, and the interpreter prefix | none | R-8; **PO-12, PO-19** |
| TR-10 | the bootstrap `/usr/local/libexec/freedom-blades-rp11/rp11_entry.py` | `pass-a.json`; every covered source under `/opt/freedom-blades/platform`, read once and verified against the pinned digest; the hook files, read once and verified. Diagnostic: environment contract, `INVOCATION_ID`, parent PID 1, unit, launcher and **H-1-record** digests, **boot ID** (§4.3.5) | none | T6 |
| TR-11 | the entry (X-1) | creates `⟨MI.capture_root_A⟩` on `oracle-test` exclusively (OH-D-3). **First mutation** | none | T6 |
| TR-12 | each act's program (local, absolute path) | the closed map `{LC_ALL=C, PATH=/usr/bin}` (§4.7.2, `rp11-launcher-env/1` amended); `cwd=/`; `stdin=/dev/null`; no shell | none. NNP inherited; no `sudo` (OH-D-5) | T7 |

*(D3-R2)* In TR-2 and TR-10 the pass configuration is
`/run/freedom-blades-rp11/pass-a.json`. In TR-5 the rule is
`/run/polkit-1/rules.d/50-freedom-blades-rp11.rules`, present in ST-1.a2 … ST-3
only (§4.2.5-R2 (b)). In ST-1 that basename is absent from every rules
directory.

*(D3-R4)* In TR-5 the rule returns `YES` for `start` only (§4.2.5-R4 (b)).
`stop` by `ubuntu` is not authorized (PO-11 (g)). Between TR-6 and TR-7, PID 1
first runs **TR-6a**, the unit's `ExecStartPre=+` step CP: the installed tool
`rp11_h1.py consume`, as root, with PID 1's environment and no operand. CP
removes the rule and obtains PK *not authorized*. Only if CP exits `0` does
PID 1 continue to TR-7 for `ExecStart=` (§4.2.5-R4 (c), PO-21 (n), (o)). CP is
a separate process. It receives nothing from TR-1 … TR-4, and it is not an
ancestor of TR-8, so LB-2S's two prevention claims about the entry are
unchanged.

*(D3-R5)* TR-6a's order is §4.2.5-R5 (e): CP identifies the activation, takes
its lock, creates the claim, removes the rule, validates, and requires PK *not
authorized*. A start that cannot identify an activation creates nothing. The
one-start-attempt property rests on the claim and on PID 1's start history
(§4.2.5-R5 (f)).

**Credentials in the path:**

* the client's own credential, at TR-1, only if its installation on
  `oracle-test` is separately authorized (OH-D-2, decided);
* the kernel peer credentials, at TR-4; and
* nothing else.

The entry reads no key, agent socket, token or password. *(D3-R1)* OH-D-5
selected option (a), so PostgreSQL peer authentication does not occur in the
path.

**Descriptors crossing a boundary:** the bus socket (TR-4/5), PID 1's
serialization descriptor to the executor (TR-7), and the journal stream
sockets on descriptors 1 and 2 (TR-7 onward). Nothing crosses from the client.

**Environment sources reaching an image:**

| Image | Environment it receives |
|---|---|
| TR-1 … TR-4 | *E_c* |
| TR-7 | PID 1's own environment |
| TR-8 | the open unit block, ignored except `INVOCATION_ID` |
| TR-9 onward | the literal |
| TR-12 | the closed map |

#### 4.1.4 Pre-pass synchronization, outside the trusted execution path

*(D3-R1: amended for the decided OH-D-1 and OH-D-4.)* Under OH-D-4, repository
bytes reach `/opt/freedom-blades/platform` on `oracle-test` **before** any
H-0, rebuild, H-1, H-2 or pass step starts. Under OH-D-1 they arrive by
**direct retrieval of the pinned commit from the canonical Git remote, run on
`oracle-test`**. Public read access is used if it is available. A read-only
credential is used only under its own separate authority. The workspace host
is never a source, controller or relay. The retrieval needs its own separate
authority. Its resource names only the canonical remote and the pinned commit.
Nothing in that transport is trusted:

1. The **pass** verifies them inside the trusted path. The bootstrap reads
   every covered source once and requires the manifest digest to equal the
   value in the root-owned `pass-a.json` (C11 C-6). A0-02's
   `git rev-parse HEAD` and empty `git status --porcelain=v1` run locally.
2. The **rebuild** verifies its own controlled checkout file by file against
   digests pinned in its assignment (§4.5.2). That is R5 step 4d's pattern,
   with the transport replaced.
3. **H-1** verifies every byte it installs, by SHA-256 over the in-memory
   bytes it writes (§4.2.4).
4. No synchronization runs while ST-2 holds or a pass is running. A
   synchronization during ST-1 changes no installed file.

#### 4.1.5 Proposed capture-root constraints (OH-D-3 decided; *D3-R1* heading amended)

`⟨MI.capture_root_A⟩` stays a maintainer input. In addition to RP-11's
existing conditions, it must:

* be absolute and on `oracle-test`;
* lie outside `/opt/freedom-blades/platform` (a pre-pass `rsync --delete`
  would remove it), `/tmp`, `/var/tmp`, `/var/lib/fb-evidence-p5-0` (A1-19
  requires `R` absent) and `/var/lib/freedom-blades` (lab V-items);
* not contain or lie under any §4.2.3 path, or under
  `/var/lib/freedom-blades-rp11`; and
* lie on a filesystem whose type and mount options H-0 records (HF-15) and
  RP-11's review accepts.

### 4.2 Installation, activation and standing authority (U-8)

#### 4.2.1 Explicit amendment of the five-file H-1 model

C11 §4.4.3.6, §4.4.3.7 and §12 (row H-1), and D2 §5.13 ("roll back an
installation"), define H-1 as root installation of five files with one
`daemon-reload`. The files are the unit, the polkit rule, `rp11-launch`, the
bootstrap and `pass-a.json`. **This proposal replaces that with two steps:**

* **H-1 (installation → ST-1)** places three files into service locations:
  * `rp11-launch`;
  * the bootstrap; and
  * the unit, which is **loaded**, so that the U-7 baseline can be recorded.

  It also **stages** the polkit rule outside every polkit rules directory,
  creates the empty `/etc/freedom-blades-rp11/`, writes the H-1 record and runs
  exactly one `daemon-reload`. It places **no rule** and **no pass
  configuration**.
* **`ACT` (activation → ST-2)**, under A-2 only (OH-D-7), places
  `pass-a.json` and copies the staged rule into
  `/etc/polkit-1/rules.d/`. It needs no `daemon-reload`, because no unit file
  changes. It writes an activation record.

**Why the unit is loaded at H-1, not at `ACT`.** U-7 requires H-1 to record
the complete effective unit-property baseline together with `FragmentPath`,
`DropInPaths` and `NeedDaemonReload=no`. Those exist only for a loaded unit.
Loading without the rule meets U-8 literally: there is no usable polkit start
grant. It also adds a technical refusal: with no `pass-a.json`, a root-started
unit reaches the bootstrap, which refuses (`entry-pass-config-unavailable`)
before X-1. No capture root is created and no act runs. OH-D-6 states the
limit of that property.

*(D3-R1.)* The two-step model is unchanged. Its mechanics are replaced:
H-1's publication by §4.2.4-R1, and `ACT`/`DEACT` by §4.2.5-R1. Under
OH-D-8, failed or ended activations are cleaned up automatically, and both
activation files are removed. *Erratum:* §0-D3 and §3.5 refer to "the unit
text in §4.2.6". No §4.2.6 exists. The unit bytes are C11 §4.4.3.4's unit with
`User=ubuntu` (§4.7.2), and they keep `NoNewPrivileges=yes` under OH-D-5.

*(D3-R2.)* `ACT` now places `pass-a.json` and the rule on the `/run` tmpfs, not
under `/etc`, and runs inside a PID-1-supervised transient unit (§4.2.5-R2).
H-1 therefore no longer creates `/etc/freedom-blades-rp11/`. It installs the
H-1 tool's pinned bytes as a member of tree **L**, so that activation runs
root-owned code bound by the H-1 record. Neither change creates a grant.

*(D3-R4.)* Under OH-D-10 (A), H-1's unit bytes gain the one
`ExecStartPre=+…rp11_h1.py consume` line, and the staged rule grants `start`
only (§4.2.5-R4 (b)). Both are H-1 bytes, bound by the H-1 record and compared
by H-2. A root start in ST-1 now reaches CP first, which finds no
`pass-a.json` and refuses (CP-0). The bootstrap's refusal stays behind it.

#### 4.2.2 States

> **Original D3 table, superseded by the D3-R1 table below.**

| State | Files present (beyond ST-0) | Usable polkit start grant? | Evidence pass possible? | Who changes it |
|---|---|---|---|---|
| **ST-0** absent | none of §4.2.3 | no | no | — |
| **ST-0.x** partial H-1 | any prefix of the §4.2.4 order, plus temporary names | no (no rule) | no (no pass configuration) | H-1 run, only by HARD STOP |
| **ST-1** staged and inert | launcher, bootstrap, unit (loaded, inactive), staged rule, empty `/etc/freedom-blades-rp11/`, H-1 record, H-1 directories | **no** | **no**: polkit refuses `ubuntu`; a root start refuses at the bootstrap. Not privilege-inert for `ubuntu` (OH-D-6) | H-1 (in); RB-1 (out) |
| **ST-1.x** partial `ACT` | ST-1 plus some of {`pass-a.json`, rule} | only if the rule is placed (it goes **last**; §4.2.5) | only once both exist | `ACT` HARD STOP; then the OH-D-8 rule removal *(withdrawn by D3-R1: cleanup removes the rule and `pass-a.json`)* |
| **ST-2** activated | ST-1 plus `pass-a.json`, the active rule and the activation record | yes, for `start`/`stop` of this unit by `ubuntu` | yes, for one pass, under A-2 | `ACT` (in); `DEACT` (out) |
| **ST-3** running | ST-2 plus the running unit and the capture root | — | in progress | the pass; `systemctl stop` is a §9.5.3 interruption |

No state is reached by `systemctl enable`. The unit has no `[Install]`
section. `start` and `stop` are issued only by the pass operator in ST-2, and
never by H-0, the rebuild, H-1, H-2, `ACT`, `DEACT` or any rollback.

**States after D3-R1** *(D3-R1; this table governs where it differs from the
D3 table above, which is retained as the original D3 text)*:

| State | Final paths present (beyond ST-0) | Usable polkit start grant? | Evidence pass possible? | Entered by | Left by |
|---|---|---|---|---|---|
| **ST-0** absent | no §4.2.3 path, except a record store admitted by **RS-A** (§4.2.3). Run-unique temporary leftovers classed **S0** may exist (§4.6.2-R1) | no | no | — | H-1 |
| **ST-0.k** partial H-1, k = 0 … 6 | the prefix of H-1's commit order given in §4.6.1-R1, plus this run's temporary trees. **Suffix `+X`** when an object classed A0 or A1-damaged sits at, or inside, a final path | no (no rule) | no (no pass configuration) | an H-1 HARD STOP | RB-1 only, under **separate** authority (OH-D-8) |
| **ST-1** staged and inert | launcher, bootstrap, unit (loaded; `ActiveState` `inactive`, or `failed` after an earlier pass), staged rule, empty `/etc/freedom-blades-rp11/`, the record store with the H-1 record | **no** | **no**: polkit refuses `ubuntu`; a root start refuses at the bootstrap. Not privilege-inert for `ubuntu` (OH-D-6) | H-1 PASS; `DEACT` or ACT cleanup with verified ST-1 | A-2's `ACT`; RB-1 (separate authority) |
| **ST-1.a1** partial `ACT` | ST-1 plus `pass-a.json` | no | no: polkit refuses `ubuntu` | an `ACT` stop after `pass-a.json` is linked and before the rule is linked | automatic cleanup (§4.2.5-R1) |
| **ST-1.a2** partial `ACT`, grant live | ST-1 plus `pass-a.json` and the active rule; post-check or activation record incomplete | **yes, live** | technically possible, but **not authorized**: A-2 permits a start only after `ACT` PASS (§4.2.5-R1 (d)), and cleanup removes the grant first | an `ACT` stop after the rule is linked | automatic cleanup; **the rule is removed first** |
| **ST-1.d1** partial cleanup | ST-1 plus `pass-a.json`, rule removed | no | no | a cleanup stop after the rule removal | the next `DEACT` attempt |
| **ST-2** activated | ST-1 plus `pass-a.json`, the active rule and the record `⟨activation_id⟩.act.json` with outcome `activated` | yes, for `start`/`stop` of this unit by `ubuntu` | yes, one pass, this boot, under A-2 | `ACT` PASS | pass start (ST-3); `DEACT` at any terminal state |
| **ST-3** running | ST-2 plus the running unit and the capture root | — | in progress; a second start in the same activation fails at X-1, because the capture root is created exclusively (TR-11) | operator `start` | the pass's terminal state, then `DEACT` |
| **ST-1+R** residual | any ST-1.x after cleanup reached a HARD STOP, with each residual classified (§4.2.5-R1, AC-9) | as recorded: `removed-verified`, or a precise non-removal class | no further pass may be authorized while it holds | a cleanup HARD STOP | Peter's separate decision; the A-2 authority is consumed |

Each transition is made by exactly one procedure, as listed in "Entered by" and
"Left by". An `ACT` failure never leaves `pass-a.json` for a later authority.

*(D3-R2.)* The activation rows of this table (ST-1.a1, ST-1.a2, ST-1.d1, ST-2,
ST-3 and ST-1+R) are superseded by §4.2.5-R2 (j), which moves both activation
files to `/run` and adds ST-1.a0 and ST-1.bc. In particular, ST-1.d1's "Left
by: the next `DEACT` attempt" is **withdrawn**. An unfinished attempt is
retried by the backstop, or its objects are cleared by the next kernel boot.
In the ST-1 row, "empty `/etc/freedom-blades-rp11/`" is withdrawn with tree
**E**. The other H-1 rows are unchanged.

*(D3-R4.)* In both tables, the ST-2 cell "yes, for `start`/`stop` of this unit
by `ubuntu`" becomes "yes, for `start` only", and ST-3 holds **no** grant. The
D3 sentence "`start` and `stop` are issued only by the pass operator in ST-2"
is superseded. The operator issues only `start`, and only the executor issues
`stop`, by route (iii-a). §4.2.5-R4 (g) gives the governing ST-2, ST-2.c,
ST-2.f and ST-3 rows.

#### 4.2.3 Exact paths, owners, groups and modes

Every file below is root-owned. Every one must have:

* **no** set-user-ID, set-group-ID or sticky bit;
* **no** `security.capability` extended attribute; and
* **no** `system.posix_acl_access` or `system.posix_acl_default` extended
  attribute.

The last rule is stricter than "no write-granting ACL entry" and needs no ACL
parsing. Checks use extended-attribute **names** only, through Python
`os.listxattr` with `follow_symlinks=False`. No value is read, and no `getfacl`
or `getcap` is needed.

| Role | Path | Owner:group | Mode | State |
|---|---|---|---|---|
| launcher directory | `/usr/local/libexec/freedom-blades-rp11/` | `root:root` | `0755` | created by H-1 if absent (§4.2.4) |
| staging directory | `/usr/local/libexec/freedom-blades-rp11/staged/` | `root:root` | `0755` | H-1 |
| `rp11-launch` | `/usr/local/libexec/freedom-blades-rp11/rp11-launch` | `root:root` | `0755` | ST-1 |
| bootstrap (M-12) | `/usr/local/libexec/freedom-blades-rp11/rp11_entry.py` | `root:root` | `0644` (read by the interpreter as `ubuntu`; never executed directly) | ST-1 |
| staged rule | `/usr/local/libexec/freedom-blades-rp11/staged/50-freedom-blades-rp11.rules.staged` | `root:root` | `0444` | ST-1 |
| unit | `/etc/systemd/system/rp11-capture-pass-a.service` | `root:root` | `0644` | ST-1 |
| pass-configuration directory | `/etc/freedom-blades-rp11/` | `root:root` | `0755` | created at H-1, empty in ST-1 |
| pass configuration | `/etc/freedom-blades-rp11/pass-a.json` | `root:root` | `0644` | ST-2 only |
| active rule | `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules` | `root:root` | `0644` | ST-2 only |
| record directories | `/var/lib/freedom-blades-rp11/`, `…/h1/`, `…/activation/` | `root:root` | `0755` | H-1 |
| H-1 record | `/var/lib/freedom-blades-rp11/h1/⟨record_id⟩.json` | `root:root` | `0444` | ST-1 onward, **retained** |
| activation record | `/var/lib/freedom-blades-rp11/activation/⟨activation_id⟩.json` | `root:root` | `0444` | written by `ACT`, **retained** |

*(D3-R1)* Rows amended or added (the D3 rows above are the original text):

| Role | Path | Owner:group | Mode | State |
|---|---|---|---|---|
| launcher directory | `/usr/local/libexec/freedom-blades-rp11/` | `root:root` | `0755` | created by H-1, as tree **L** (§4.2.4-R1). It must be absent at P-0 |
| activation record (`ACT`) | `/var/lib/freedom-blades-rp11/activation/⟨activation_id⟩.act.json` | `root:root` | `0444` | written once by `ACT` at its terminal state; **retained** |
| activation record (`DEACT` attempt k) | `/var/lib/freedom-blades-rp11/activation/⟨activation_id⟩.deact-⟨k⟩.json` | `root:root` | `0444` | written by each `DEACT` attempt, including `ACT`'s in-process cleanup as k = 1; **retained** |
| H-1 temporary tree | `⟨parent⟩/.rp11-⟨RUN⟩-⟨tag⟩.tmp/`, with `tag` ∈ {`L`, `V`, `E`} and `⟨parent⟩` the pre-existing parent of that tree's top | `root:root` | `0700` until sealed, then the final mode | exists only while H-1 assembles a tree; renamed to the final name. Never exists in ST-1 |
| H-1 run evidence and journal | `/var/tmp/⟨RUN⟩-h1-evidence/` (`ubuntu:ubuntu`, `0700`) with `journal` (`root:root`, `0644`) | as stated | as stated | created at P-1 and M-0; **retained** (§4.5.3) |
| `ACT` run evidence and journal | `/var/tmp/⟨activation_id⟩-act-evidence/` (`ubuntu:ubuntu`, `0700`) with `journal` (`root:root`, `0644`) | as stated | as stated | **retained** |
| `DEACT` attempt evidence and journal | `/var/tmp/⟨activation_id⟩-deact-⟨k⟩-evidence/` (`ubuntu:ubuntu`, `0700`) with `journal` (`root:root`, `0644`) | as stated | as stated | **retained** |
| RB-1 run evidence and journal | `/var/tmp/⟨RUN⟩-rb1-⟨n⟩-evidence/` (`ubuntu:ubuntu`, `0700`) with `journal` (`root:root`, `0644`) | as stated | as stated | **retained** |

The `ACT` and `DEACT` records replace the single D3 activation record, because
cleanup must leave its own immutable record after the activation files are
gone. `⟨k⟩` is a decimal integer from 1 to 99 with no leading zero.

*(D3-R2.)* The rows for the pass-configuration directory, the pass
configuration and the active rule (in both tables), and the `DEACT` evidence
row, are superseded by §4.2.5-R2 (b):

* both activation files, and the directory holding `pass-a.json`, move to
  `/run`;
* tree **E** is withdrawn;
* tree **L** gains the installed tool `rp11_h1.py` (`0644`); and
* CL attempt directories are created by root (`root:root`, `0755`).

The parent list gains `/run` and `/run/polkit-1`.

**RS-A, record-store admission** *(D3-R1)*. Records are never deleted, so after
RB-1 the record store `/var/lib/freedom-blades-rp11/` (with `h1/` and
`activation/`) may remain. A later H-1 admits it at P-0 only if all of the
following hold:

* each of the three directories is a directory, `root:root`, mode `0755`, with
  no POSIX ACL extended attribute;
* they contain nothing except regular files `root:root`, mode `0444`, link
  count 1, whose names match the record grammars above; and
* every such file's SHA-256 is listed in the new H-1 assignment's pinned
  **retained-record inventory**, which is compiled from accepted handbacks.

Anything else is INVALID RUN. If the store is admitted, H-1 does not create
tree **V**. RS-A is a precondition on retained evidence. It is not an exception
to pre-existing-path refusal: every other §4.2.3 path must still be absent.

**Parent requirements.** Every existing parent up to `/` of every path above
must be:

* a directory (not a symbolic link), owned by `root`;
* without group or other write permission; and
* without a POSIX ACL extended attribute.

The parents are `/`, `/usr`, `/usr/local`, `/usr/local/libexec`, `/etc`,
`/etc/systemd`, `/etc/systemd/system`, `/etc/polkit-1`,
`/etc/polkit-1/rules.d`, `/var` and `/var/lib`.

`/etc/polkit-1/rules.d` is the exception. Its owner, group and mode are taken
**exactly as H-0 records them** (HF-11). Distributions differ here, and
polkitd must be able to read it. H-1 and `ACT` never create or change it.

H-1 may create only the directories named in the table, and `/usr/local/libexec`
**only if** H-0 recorded it absent. Each is created by an exclusive `mkdir`,
never `-p`, then `fchown root:root` and `fchmod`, then `fsync` of the parent.
The H-1 record lists every directory it created (`created_by_run: true`).

*(D3-R1: the previous paragraph's creation method is replaced.)* Directories are
created only inside a temporary tree. Each tree is moved to its final name by
one `renameat2(RENAME_NOREPLACE)` after its identity is durable
(§4.2.4-R1, protocol PT). If H-0 recorded `/usr/local/libexec` absent, it is the
top of tree **L**, and its parent is `/usr/local`. `created_by_run: true` is
kept, and each directory entry in the record also gains `dev` and `ino`.

**Search-path exclusion of the staged rule.** PO-11(c) must show that the
staging directory is in no polkit rules search directory for the installed
polkit version. PO-15 must show that it is in no systemd unit search
directory. The `.staged` suffix is an additional guard: polkit loads only
`*.rules`.

#### 4.2.4 The H-1 publication algorithm and order

> **Original D3 text, superseded by D3-R1.** The publication algorithm, the
> run journal and the order table below are replaced by §4.2.4-R1, because
> step 5 named the final path before the journal recorded it
> (`OH-H1-D3-1`). The tool, the verified-exec stub and its stated limit, and the
> `⟨RUN⟩` grammar are **retained** by §4.2.4-R1. The rest of this subsection
> is history and does not govern.

H-1's mutating work is done by one reviewed, standard-library-only Python
tool, proposed as `tools/phase_5_0_evidence/execution/rp11_h1.py` (OH-S4). It
runs as root through:

```text
sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' ⟨subcommand⟩ ⟨arguments⟩
```

The stub reads the tool file **once**, requires its SHA-256 to equal the value
pinned in the H-1 assignment, and executes **those** bytes. There is no window
between the check and the use.

*Stated limit.* The tool runs under `sudo`'s environment, which is not closed
(AS-12). That is acceptable only because H-1 is not the capture entry. Its
results are re-read unprivileged by H-2, and diagnostically by the entry. It
is a review focus (§10).

**Publication of one file, F → path P, with expected digest D:**

1. Read the source bytes B **once** into memory, and require `sha256(B) == D`.
2. Require `lstat(P)` to fail with `ENOENT`. Anything else stops: INVALID RUN
   before the mutation point, HARD STOP after it.
3. Create the temporary name `T = dir(P)/.⟨basename(P)⟩.⟨RUN⟩.tmp` with
   `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC` and mode `0600`. Before
   creating it, append the line `intend T` to the run journal (below).
4. Write B in full, `fsync`, `fchown(0,0)`, `fchmod(mode)`, `fsync`. Record
   `(st_dev, st_ino)` in the journal.
5. `link(T, P)`. `EEXIST` is a HARD STOP, and P is **not** recorded as
   created. Success appends `created P dev ino sha256` to the journal.
6. `fsync(dir(P))`, then `unlink(T)`, then `fsync(dir(P))`.
7. Re-open P with `O_NOFOLLOW`, re-read it, and require digest D, owner,
   mode, no forbidden extended attributes, and `(dev, ino)` equal to step 4.

`link` gives the final name its complete content atomically, and fails rather
than replacing a file. That is the same no-replace property as the capture
mechanism's exclusive final link. Temporary names are derived from the run
identifier, so rollback can find them.

**Run journal.** `/var/tmp/⟨RUN⟩-h1-evidence/journal`, a directory owned by
`ubuntu` with mode `0700`, created first in the run, plus the run's evidence
files. Lines are appended and `fsync`ed **before** and **after** each
mutation. The journal is evidence, not an installed file.

**`⟨RUN⟩` grammar.** `rp11-h1-⟨UTC YYYYMMDDTHHMMSSZ⟩-⟨8 lowercase hex⟩`.
Before anything is created, the tool requires that no entry of `/var/tmp`
begins with `⟨RUN⟩`.

**H-1 order (ST-0 → ST-1):**

| Step | Action | Mutation? |
|---|---|---|
| P-0 | preflight, read-only, unprivileged: E-1 identity; repository commit and controlled-path digests; authority and assignment digests; accepted H-0 and citation records, with re-observed versions equal to H-0 (HF-04 … HF-10); PO-18; every §4.2.3 path **absent**; every parent as §4.2.3 and as H-0 recorded; the launcher source digest equal to `04218ed2…2668572` (§4.5.2); PO-17 against the **source** image bytes; `systemctl show rp11-capture-pass-a.service -p LoadState` = `not-found`; no drop-in directory for the unit in any search directory (HF-13) | no. Any failure is **INVALID RUN** |
| P-1 | create the run evidence directory and journal | ubuntu-owned run evidence only. Before the **mutation point** |
| **M-0** | **mutation point.** The first `sudo -n` invocation | — |
| M-1 | create the H-1 directories (§4.2.3) | yes |
| M-2 | publish `rp11-launch` (`0755`) | yes |
| M-3 | publish the bootstrap (`0644`) | yes |
| M-4 | publish the staged rule (`0444`) | yes |
| M-5 | publish the unit (`0644`). **Last of the files**, so a unit never names an absent `ExecStart=` image | yes |
| M-6 | exactly one `systemctl daemon-reload` | yes |
| V-1 | post-check, unprivileged: every published file per step 7; every parent; PO-17 against the **installed** image's bytes; the U-7 queries (§4.3.3) with `LoadState=loaded`, `ActiveState=inactive`, `FragmentPath=/etc/systemd/system/rp11-capture-pass-a.service`, `DropInPaths=` (empty), `NeedDaemonReload=no`; `pass-a.json` and the active rule **absent** | no |
| M-7 | publish the H-1 record (`0444`), built by the tool from V-1's observations only | yes |
| V-2 | re-read the record and require its SHA-256 to equal the value the tool reports | no |

There is no `start`, `stop`, `enable`, `restart`, `edit`, `set-property`,
`set-environment` or `show-environment` in any step.

#### 4.2.4-R1 Crash-consistent H-1 publication, recovery binding and order *(D3-R1)*

This subsection replaces §4.2.4's "Publication of one file", "Run journal" and
"H-1 order" paragraphs. It keeps §4.2.4's tool
(`tools/phase_5_0_evidence/execution/rp11_h1.py`), the verified-exec stub, the
stated `sudo` environment limit and the `⟨RUN⟩` grammar. Everything here is
**proposed** and inactive.

##### (a) Invariants

* **W, write-ahead.** No namespace or content mutation starts until the
  `fsync` of the journal line announcing it has returned success.
* **I, identity before name.** An object that recovery may remove is given a
  name only after a durable journal line records its identity: `(st_dev,
  st_ino)`, type, owner, group and mode, plus size and SHA-256 for a file.
  Files have no temporary name at all. A directory's run-unique temporary name
  can exist for one short window, W-T, before its identity line. That name is
  never final, recovery never removes it, and it cannot block a later run (S0,
  §4.6.2-R1).
* **N, no replace.** Every name-creating call fails if the name exists:
  `linkat` (it never replaces), `renameat2` with `RENAME_NOREPLACE`, and
  `mkdirat`. Plain `rename`, `O_TRUNC`, `mkdir -p` and symlink-following on a
  target name are never used.
* **D, durability order.** A file's bytes and metadata are made durable by
  `fsync` on that file. A directory entry is durable only after its
  **containing** directory is synchronized. Every directory `fsync` uses a
  separately opened `O_RDONLY|O_DIRECTORY|O_NOFOLLOW` descriptor, never an
  `O_PATH` one. `tools/phase_5_0_evidence/durability_model.py` records both
  rules and the defect they prevent.
* **R, relative resolution.** At M-0 each pre-existing parent is opened once
  with `O_RDONLY|O_DIRECTORY|O_NOFOLLOW`. `fstat` must show the
  `(dev, ino)`, owner and mode that H-0 recorded. Every later operation in that
  parent uses the descriptor through `*at` calls with
  `AT_SYMLINK_NOFOLLOW`. No path is re-resolved from `/`.
* **S, single attempt.** Each object has one publication attempt per run.
  Nothing is retried.

##### (b) The run journal, format `rp11-journal/1`

* **Location and creation.** At P-1 `ubuntu` creates
  `/var/tmp/⟨RUN⟩-h1-evidence/` with an exclusive `mkdir`, mode `0700`, and
  then `fsync`s `/var/tmp`. At M-0 the root tool opens that directory,
  requires owner `ubuntu` and mode `0700`, and takes
  `flock(LOCK_EX|LOCK_NB)` on it for its whole lifetime. If the lock fails it
  stops before any mutation. It then creates `journal` with
  `openat(…, O_WRONLY|O_CREAT|O_EXCL|O_APPEND|O_NOFOLLOW|O_CLOEXEC, 0644)` and
  `fsync`s the file and the directory.
* **Lines.** Each line is `canonical_bytes(entry)` (§4.3.1): one canonical
  JSON object followed by LF. Every entry has `seq` (1, 2, … with no gap),
  `prev` (the SHA-256 of the previous line's exact bytes, or 64 `0` characters
  for `seq` 1), `run` (`⟨RUN⟩`), `op`, and the closed fields of that `op`.
  Values are strings, integers, booleans, lists and objects only.
* **Append.** A line is appended with one `write` of the whole line, followed
  by `fsync`. A short write, or an error from `write` or `fsync`, stops the tool
  at once. Nothing further is mutated, `fsync` is never retried, and the
  outcome is HARD STOP.
* **Parsing (RS-1, RB-1, `DEACT`).** The bytes are split at LF. A final
  segment without LF is a **torn tail**: it is ignored and reported. Every
  complete line must be canonical (re-serializing it gives the same bytes),
  must have a contiguous `seq`, a correct `prev`, the expected `run`, a known
  `op` and exactly its closed fields. Any violation makes the journal
  **invalid**.
* **Monotone safety.** The journal is used only to **permit** removal of an
  object whose present identity and digest equal a recorded line. A lost, torn
  or invalid line can therefore only shrink what recovery may remove. An
  invalid or missing journal classifies every object A0, so nothing is
  removed. Only a forged line could cause a wrong removal. Forgery is T-B,
  which M-10 places out of scope.
* **Binding.** The handback reports the journal's SHA-256 and byte length
  (OH-D-9). RB-1 uses the retained file, or a copy whose digest and length
  equal the reported ones.

H-1's closed `op` set is: `run-start`, `tree-intent`, `dir-identity`,
`file-intent`, `file-identity`, `file-linked`, `tree-sealed`, `tree-linked`,
`reload-intent`, `reload-done`, `v1-pass` and `run-end`.

##### (c) Protocol PF: publish one file into an open directory descriptor

Inputs: a directory descriptor `pd`, a name `n`, bytes `B` read once with
`sha256(B) = D`, size `z` and mode `m`.

| Step | Action | Invariant |
|---|---|---|
| PF-1 | `fstatat(pd, n, AT_SYMLINK_NOFOLLOW)` must fail with `ENOENT`. Anything else is HARD STOP `preexisting-path`, and the object found is classed **A0** | N |
| PF-2 | append `file-intent {dir, name, sha256: D, size: z, uid: 0, gid: 0, mode: m, grant}`, where `grant` is `true` only for the active rule (§4.2.5-R1); `fsync` | W |
| PF-3 | `fd = openat(pd, ".", O_TMPFILE\|O_WRONLY\|O_CLOEXEC, 0600)`. This is an **unnamed** inode. `O_EXCL` is **not** used, because it would forbid the later link | I |
| PF-4 | `fstat(fd)`: regular file, uid 0, `st_nlink = 0`, size 0. Append `file-identity {dir, name, dev, ino}`; `fsync` | I, W |
| PF-5 | write `B` in full; `fsync(fd)`; `fchown(fd, 0, 0)`; `fchmod(fd, m)`; `fsync(fd)`. `fstat` must show the same `(dev, ino)`, size `z`, mode `m`, uid and gid 0 | D |
| PF-6 | link the inode as `n`: `os.link("/proc/self/fd/⟨fd⟩", n, dst_dir_fd=pd, follow_symlinks=True)`. That is `linkat(…, AT_SYMLINK_FOLLOW)`, the form `open(2)` documents for `O_TMPFILE`. On `EEXIST` the outcome is HARD STOP: the object now at `n` appeared after PF-1 and is **A0**, and the unnamed inode is freed when `fd` closes | N |
| PF-7 | `fsync(pd)`, which makes the name durable | D |
| PF-8 | append `file-linked {dir, name}`; `fsync`. This is the **commit** | W |
| PF-9 | close `fd`. Re-open with `openat(pd, n, O_RDONLY\|O_NOFOLLOW)` and require: the recorded `(dev, ino)`; a regular file; uid and gid 0; mode `m`; `st_nlink = 1`; size `z`; no forbidden extended-attribute name (`os.listxattr` on the descriptor); and a re-read SHA-256 equal to `D` | verification |

**Why every final name is attributable.** Before PF-6 the object has no name.
After PF-6, `n` names an inode whose identity line was made durable at PF-4.
No instant exists at which `n` names this run's object without a durable
identity line. A crash, kill or power loss before PF-6 leaves only an unnamed
inode, which the kernel frees on its last close or which the filesystem's
orphan processing frees at the next mount. A crash between PF-6 and PF-7 can
leave `n` either present, with the recorded identity, or absent after a power
loss. Both cases are attributable. These are host semantics, so they become
proof obligation **PO-20** (§4.4.2a).

##### (d) Protocol PT: build a directory tree, then publish it with one rename

Inputs: a pre-existing parent descriptor `pp`, a final top name `t`, the
temporary name `x = .rp11-⟨RUN⟩-⟨tag⟩.tmp`, and the member list (relative
directories with modes; files with their PF inputs).

| Step | Action |
|---|---|
| PT-1 | `fstatat(pp, t)` and `fstatat(pp, x)` must both fail with `ENOENT`. Otherwise HARD STOP, and whatever was found is classed A0 |
| PT-2 | append `tree-intent {parent, top: t, temp: x, tag, members}`. Each member lists its relative path, kind, final mode and, for a file, SHA-256 and size. `fsync` |
| PT-3 | `mkdirat(pp, x, 0700)`. Open it with `O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW`; `fstat` must show a directory, uid 0, mode `0700` and `st_nlink = 2`, and the listing must be empty. Append `dir-identity {rel: ".", dev, ino}`; `fsync`. **Window W-T** runs from `mkdirat` to this `fsync` |
| PT-4 | for each member directory, in pre-order: `mkdirat(parent, name, 0700)`, open and verify as in PT-3, append `dir-identity {rel, dev, ino}`, `fsync`. Window W-T applies to the child, which lies **inside** the unsealed temporary tree |
| PT-5 | for each member file: protocol PF, with `pd` the descriptor of its directory |
| PT-6 | bottom-up for each directory: `fchown(0, 0)`, `fchmod(final mode)`, `fsync`; finally `fsync(pp)` |
| PT-7 | **seal.** List every directory of the tree. Its entries must be exactly the members, and each member's `fstatat` identity must equal its identity line. Append `tree-sealed {temp: x, inventory_sha256}`, where the inventory is the canonical list `[rel, kind, dev, ino, mode, sha256 or "absent"]`; `fsync`. On any mismatch the outcome is HARD STOP, and the tree stays under `x` |
| PT-8 | `renameat2(pp, x, pp, t, RENAME_NOREPLACE)`, through glibc's `renameat2` called with standard-library `ctypes` (Python 3.12 has no wrapper). `EEXIST` gives HARD STOP: the object at `t` is A0 and the tree stays under `x`. `EINVAL` gives HARD STOP and refutes PO-20 for this host; the tree stays under `x` |
| PT-9 | `fsync(pp)`; append `tree-linked {parent, top: t}`; `fsync`. This is the **commit** |
| PT-10 | verify: `openat(pp, t, O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW)` shows the top's recorded `(dev, ino)`, and every member is re-verified (files as in PF-9) |

The final name `t` appears only after the top's identity and every member's
identity are durable, and only after the seal has shown that the tree holds
nothing else. `rename` is atomic, so after any stop the tree is found under
exactly one of `x` and `t`, with its recorded identity. Window W-T can leave
only a directory under a temporary name, and that name is never final. The top's
temporary name lives in a pre-existing system directory and contains this run's
`⟨RUN⟩`, which a later run's P-0 never checks and cannot reuse. A child left by
W-T lies inside an unsealed tree, which is never renamed.

##### (e) H-1 trees, order and partial states

| Tree | Pre-existing parent | Top `t` | Members (mode) |
|---|---|---|---|
| **L** | `/usr/local/libexec`; or `/usr/local` if H-0 recorded `/usr/local/libexec` absent, in which case `t` is `libexec` and `freedom-blades-rp11/` (`0755`) is a member | `freedom-blades-rp11` (`0755`) | `staged/` (`0755`); `rp11-launch` (`0755`, `04218ed2…2668572`); `rp11_entry.py` (`0644`); `staged/50-freedom-blades-rp11.rules.staged` (`0444`) |
| **V** | `/var/lib` | `freedom-blades-rp11` (`0755`) | `h1/` (`0755`); `activation/` (`0755`). Not built when RS-A admits an existing store (§4.2.3) |
| **E** | `/etc` | `freedom-blades-rp11` (`0755`) | none |

The unit is published by PF into `/etc/systemd/system`, and the H-1 record by
PF into `/var/lib/freedom-blades-rp11/h1/`.

| Step | Action | Mutation? | State once its commit is durable |
|---|---|---|---|
| P-0 | §4.2.4's preflight, plus: every §4.2.3 path absent except a store admitted by RS-A; no `.rp11-⟨RUN⟩-*` name in the three tree parents; no `/var/tmp` entry beginning with `⟨RUN⟩`; each parent's `(dev, ino)`, owner and mode as H-0 recorded; and the accepted PO-20 citation's kernel series and filesystem types equal to the observed ones (HF-04, HF-15) | no. Any failure is **INVALID RUN** | ST-0 |
| P-1 | create the run evidence directory (b), as `ubuntu` | evidence only | ST-0 |
| **M-0** | **mutation point.** The first `sudo -n`. The root tool takes the lock, creates the journal and appends `run-start {tool_sha256, assignment_sha256, authority_sha256, h0_record_sha256, source digests}` | journal only | **ST-0.0** |
| M-1 | tree **L** (PT) | yes | **ST-0.1** |
| M-2 | tree **V** (PT), unless RS-A admitted a store | yes | **ST-0.2** |
| M-3 | tree **E** (PT) | yes | **ST-0.3** |
| M-4 | the unit (PF). It is the last service file, so a unit never names an absent `ExecStart=` image | yes | **ST-0.4** |
| M-5 | append `reload-intent`, `fsync`, run `systemctl daemon-reload`, append `reload-done {exit}`, `fsync`. A non-zero exit is HARD STOP | yes (manager state) | **ST-0.5** |
| V-1 | the unprivileged post-check of §4.2.4, with each file checked as in PF-9, each tree as in PT-10 and `ActiveState=inactive`. On success the root tool appends `v1-pass {journal_prefix_sha256, journal_prefix_length}`, covering the journal up to the line before `v1-pass` | no | ST-0.5 |
| M-6 | the H-1 record (PF) into `h1/`. Its `context.journal_sha256` and `context.journal_length` are the `v1-pass` prefix values | yes | **ST-0.6** |
| V-2 | re-read the record and require the SHA-256 the tool reports. Append `run-end {outcome: "PASS", h1_record_sha256}` | no | **ST-1** |

Each step starts only after the previous step's commit line is durable. After
any stop, the final paths this run created are therefore **exactly a prefix**
of M-1 … M-6. ST-0.k names that prefix. Only A0 objects, which this run never
created, can lie outside it. In ST-0.6, V-2 has not passed, so the state is
not ST-1 even though every file exists. There is still no `start`, `stop`,
`enable`, `restart`, `edit`, `set-property`, `set-environment` or
`show-environment` in any step.

Recovery, terminal states and RB-1 are in §4.6.1-R1 and §4.6.2-R1.

*(D3-R2.)* Tree **L** gains the member `rp11_h1.py` (`0644`, the tool's pinned
SHA-256). **Step M-3 (tree E) is withdrawn**, because `ACT` creates the
pass-configuration directory on `/run` (§4.2.5-R2 (b)). The labels M-4 … M-6
and ST-0.4 … ST-0.6 keep their meanings, except that ST-0.4 … ST-0.6 contain
L, V and the unit, with no E. ST-0.3 no longer exists: a stop after M-2's
commit is ST-0.2 until M-4 commits. V-1 additionally requires the
§4.2.5-R2 (b) activation paths and `/etc/freedom-blades-rp11` to be absent.

#### 4.2.5 `ACT` and `DEACT` order (proposed; authority per OH-D-7)

> **Original D3 text, superseded by D3-R1.** This subsection is replaced in
> full by §4.2.5-R1 (`OH-H1-D3-2`). It is history and does not govern.

`ACT`, under A-2, for one pass and one boot:

1. Preflight, read-only: ST-1 exactly as the H-1 record states. That is the
   H-2 equality (§4.3.4), the current boot ID equal to A-2's, and both
   activation paths absent.
2. Publish `pass-a.json` (`0644`). Its SHA-256 must equal the value A-2 pins.
   Its bytes carry `h1_record_sha256` and `boot_id` (§4.3.5).
3. Publish the active rule, last. Its bytes must equal the staged rule's
   recorded digest.
4. Post-check:
   * both files as published;
   * `NeedDaemonReload=no` still holds, and the unit baseline is unchanged
     (the H-2b re-check); and
   * PO-11's rule-reload behaviour, which says when polkitd sees a new
     rules file, is satisfied as cited. Under the citation the activation
     waits on no unbounded condition; if the citation cannot bound it, `ACT`
     is redesigned rather than polled.
5. Publish the activation record.

`DEACT` is digest-guarded:

1. Remove the active rule.
2. Remove `pass-a.json`.
3. Verify ST-1.

No `daemon-reload` is needed in either direction.

#### 4.2.5-R1 The `ACT`/`DEACT` contract and automatic activation cleanup *(D3-R1)*

> **D3-R1 text, superseded in part by D3-R2 (§4.2.5-R2).** Superseded: in
> (a), the "One boot" bullet from "Any reboot" onward; in (b), the active-rule
> path; in (c), the two activation paths; in (d), the target paths and the
> actor of AM-0 … AM-3 (the PID-1-supervised holder replaces the in-session
> tool) and `ACT`'s in-process cleanup; in (e),
> items 1, 3 and 4 of "When it runs" and the definitions of CL-0, CL-5, CL-6
> and CL-7; in (g), the schema `/1` and its paths; and in (h), rows AC-10 and
> AC-11 and the paragraph "Residual RR-2". Everything else in this subsection
> stays in force. *(D3-R2)* markers below show each withdrawn statement.

This subsection replaces §4.2.5. It implements OH-D-6, OH-D-7 and OH-D-8 as
decided. It is **proposed** and inactive. `ACT` and `DEACT` are subcommands of
the same tool as H-1 (`rp11_h1.py act` and `rp11_h1.py deact`). They use the
same verified-exec stub, the same journal format (§4.2.4-R1 (b)) and the same
protocol PF. Neither creates a directory or a temporary name, so W-T never
occurs in activation.

##### (a) Activation identifier and the one-pass, one-boot binding

* **Grammar.** `⟨activation_id⟩` matches
  `^rp11-act-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}$`. The timestamp is the UTC
  preparation time of A-2, and the suffix is 8 random lowercase hexadecimal
  digits. **A-2 fixes the value.** `ACT` never chooses it.
* **One pass.** A-2 authorizes exactly one `ACT` with that identifier. The
  identifier is **consumed** when AP-1 creates
  `/var/tmp/⟨activation_id⟩-act-evidence/`. AP-0 refuses if any `/var/tmp`
  entry begins with `⟨activation_id⟩`, or if any
  `activation/⟨activation_id⟩.*` record exists. Within ST-2 a second pass
  cannot run, because X-1 creates the capture root exclusively (TR-11) and
  `pass-a.json` names one capture root.
* **One boot.** A-2 pins the `boot_id` that H-2 observed. AP-0 requires
  `/proc/sys/kernel/random/boot_id` to equal it. `pass-a.json` carries it, and
  the bootstrap refuses with `entry-activation-stale` on a mismatch. That
  refusal is diagnostic and is not credited as prevention. Any reboot in
  ST-1.a1, ST-1.a2, ST-2 or ST-3 **terminates** the activation, and `DEACT`
  is then due (AC-10). *(D3-R2: from "Any reboot" onward this is withdrawn.
  The activation files live on `/run`, so no kernel boot can carry them into
  the next boot, and nothing is due from an actor. §4.2.5-R2 (a) and (k).)*

##### (b) What A-2 pins

A-2 is the pass authorization (§4.3.4). For `ACT` it must state:

* `activation_id`;
* `h1_record_id` and `h1_record_sha256`;
* `h2_record_sha256` and the `boot_id` H-2 observed;
* the complete `pass-a.json` document (§4.3.5) and its SHA-256;
* `staged_rule_sha256`, equal to the H-1 record's
  `baseline.files[staged rule].sha256`, together with that file's
  `(dev, ino)`;
* the active rule path `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules`;
* the PO-11(d) bound, in milliseconds;
* the fixed `authority_limit` sentence: *"Staging and activation separation on
  `oracle-test` is an authority boundary, not a privilege boundary: `ubuntu`
  has unrestricted sudo. ST-1 is not privilege-inert."* (OH-D-6); and
* the sentence: *"`DEACT`, including `ACT`'s in-process cleanup, is mandatory
  and automatically authorized under this authority at every terminal state.
  H-1 installation rollback (RB-1) is not authorized by it."* (OH-D-7,
  OH-D-8).

`ACT` receives A-2's SHA-256 as an argument. It reads A-2's file from the
verified repository tree, and requires its digest to be equal.

##### (c) Activation files and how `ACT` derives their bytes

| File | Bytes | Mode | Bound by |
|---|---|---|---|
| `/etc/freedom-blades-rp11/pass-a.json` | `canonical_bytes(doc)`, with `doc` exactly as A-2 quotes it. `ACT` recomputes the bytes, and their SHA-256 must equal A-2's pin | `0644` | A-2; the activation records |
| `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules` | the staged rule's bytes, read once through a descriptor whose `fstat` `(dev, ino)` equals the H-1 record. Their SHA-256 must equal `staged_rule_sha256`. Published as a **new** inode by PF; the staged file is never linked or moved | `0644` | the H-1 record; A-2; the activation records |

The `ACT` evidence directory is
`/var/tmp/⟨activation_id⟩-act-evidence/` (`ubuntu:ubuntu`, `0700`). Its
journal is created and locked exactly as H-1's is (§4.2.4-R1 (b)).

##### (d) `ACT` order

| Step | Action | On failure | State once committed |
|---|---|---|---|
| AP-0 | read-only, unprivileged preflight: E-1; A-2's digest; the H-1 and H-2 records' digests; the current `boot_id` equal to A-2's; **ST-1 exactly**, meaning the recomputed `baseline` equals the H-1 record's `baseline_sha256` (the H-2 code); `/etc/freedom-blades-rp11/` with the H-1-recorded `(dev, ino)` and empty; both activation paths absent; the identifier unused (a); unit `ActiveState` `inactive` or `failed`; `pass-a.json` bytes and staged-rule digest and identity as in (c); the PO-11(d) and PO-11(e) citations accepted for the installed polkit version | **INVALID RUN**: nothing is mutated and ST-1 is unchanged. If the failure is an object present at an activation path, that object is classed A0 and the privileged check PK (f) is run and recorded | ST-1 |
| AP-1 | create the `ACT` evidence directory; `fsync` `/var/tmp`. This consumes the identifier | INVALID RUN | ST-1 |
| **AM-0** | **mutation point.** The root tool locks, creates the journal and appends `run-start {a2_sha256, h1_record_sha256, h2_record_sha256, boot_id, pass_config_sha256, staged_rule_sha256}` | HARD STOP; cleanup CL runs (e) | ST-1 |
| AM-1 | PF publishes `pass-a.json` into `/etc/freedom-blades-rp11/` | HARD STOP; CL | **ST-1.a1** |
| AM-2 | PF publishes the active rule into `/etc/polkit-1/rules.d/`, with `grant: true` in its `file-intent`. **The grant is live from PF-6's link**, before the commit | HARD STOP; CL | **ST-1.a2** |
| AV-1 | post-check: both files as in PF-9; **H-2b**, meaning the recomputed `baseline` still equals the H-1 record's `baseline_sha256`; PK must return *authorized* within the PO-11(d) bound. This is the positive control that makes cleanup's later negative result meaningful | HARD STOP; CL | ST-1.a2 |
| AM-3 | PF publishes `⟨activation_id⟩.act.json` with `outcome: "activated"` into `activation/`, then re-reads it. **The commit of this record is `ACT` PASS** | HARD STOP; CL | **ST-2** |
| — | append `run-end {outcome: "activated", act_record_sha256}` | — | ST-2 |

If `ACT` is killed after AM-3's link but before `run-end`, the record is still
A1-intact at its path and `ACT` still counts as PASS. The executor reads the
record to learn this. A-2 permits the operator's `start` only after `ACT` PASS
is established in this way.

##### (e) Automatic activation cleanup, procedure CL

**When it runs.** All of these are pre-authorized by A-2 under OH-D-7 and
OH-D-8. None needs a new authority, and none is an H-1 rollback.

1. any `ACT` failure at or after AM-0: `ACT` runs CL **in-process** as `DEACT`
   attempt k = 1 before it exits;
2. every pass terminal state (PASS, INVALID RUN, HARD STOP or a §9.5.3
   interruption): `DEACT`;
3. death of the `ACT` process, loss of the executor's session, or a host
   reboot in ST-1.a1 … ST-3: `DEACT` is the **first** RP-11 action of any actor
   working under A-2 once the host can be reached; and
4. an earlier attempt that ended without `st1-verified` and without a residual
   HARD STOP, for example because it was killed: the next attempt.

*(D3-R2.)* Items 1, 3 and 4 are **withdrawn**. Under §4.2.5-R2: item 1 becomes
the holder's end, which runs CL through `ExecStopPost=`; item 3 becomes the
same trigger for every process death (session loss has no effect), and the
kernel boot itself for power loss and reboot; and item 4 becomes the backstop
BS, which retries every R seconds. No item waits for an actor to reach the
host. Item 2 stands, with HL detecting the pass's terminal state.

| Step | Action |
|---|---|
| CL-0 | **attempt k.** Create `/var/tmp/⟨activation_id⟩-deact-⟨k⟩-evidence/` exclusively, as `ubuntu`, mode `0700`. `k` is 1 plus the number of existing `deact` evidence directories for this identifier. On `EEXIST` the attempt stops with `concurrent-deact` and acts on nothing. The root tool takes `flock(LOCK_EX\|LOCK_NB)` on the **`ACT`** evidence directory. If that fails, the attempt stops with `act-or-deact-in-progress` and acts on nothing. Within `ACT`'s in-process cleanup the lock is already held. The tool creates this attempt's journal and appends `run-start` |
| CL-1 | read the `ACT` journal, every earlier attempt's journal, the A-2 pins and the H-1 record. If the `ACT` journal is missing or invalid, every object at an activation path is A0 for removal purposes |
| CL-2 | record the unit's `ActiveState`. CL never issues `start`, `stop` or `kill`. If the unit is `active`, `activating`, `deactivating` or `reloading`, CL continues with the grant removal, and its outcome cannot be better than HARD STOP `unit-still-active` |
| CL-3 | **the grant first.** Classify the object at the active rule path against the `ACT` journal's `file-identity` line for the rule. The expected values are the staged digest, mode `0644`, uid and gid 0, and link count 1. **A1-intact:** remove it with G-R1 (§4.6.2-R1), write-ahead in this attempt's journal: `remove-intent {path, dev, ino, sha256}`, `fsync`, `unlinkat`, `fsync(/etc/polkit-1/rules.d)`, then `removed {path}` and `fsync`. **Absent:** class `never-linked` if no identity line exists; `removed-earlier` if an earlier attempt journaled `removed`; otherwise `absent-before-removal`. **A1-damaged or A0:** not removed |
| CL-4 | **grant post-check.** The path must give `ENOENT`, and PK must return *not authorized* within the PO-11(d) bound. The rule's grant class is then one of: `removed-verified`; `removed-unconfirmed` (removed, but PK still authorized after the bound, or PK errored); `never-linked`; `removed-earlier`; `absent-before-removal`; `present-damaged-unremoved`; `present-foreign-unremoved`. The record states PK's result for every class |
| CL-5 | `pass-a.json`: the same classification and G-R1 removal against its own identity line, with A-2's digest. It is **always attempted**, even when CL-3 could not remove the rule, because without a pass configuration the bootstrap refuses any start (`entry-pass-config-unavailable`). Classes: `removed`, `never-linked`, `removed-earlier`, `absent-before-removal`, `present-damaged-unremoved`, `present-foreign-unremoved` |
| CL-6 | **verify ST-1:** both activation paths absent; `/etc/freedom-blades-rp11/` with the H-1-recorded `(dev, ino)` and empty; the recomputed `baseline` equal to the H-1 record's `baseline_sha256`; PK *not authorized*; `ActiveState` `inactive` or `failed` |
| CL-7 | **records.** Inside `ACT`'s in-process cleanup, PF first publishes `⟨activation_id⟩.act.json` with `outcome: "failed"`. Then PF publishes `⟨activation_id⟩.deact-⟨k⟩.json`. Both are re-read, and `run-end` is appended |

**Outcome.** `st1-verified` if, and only if, all of the following hold:

* the rule's class is `removed-verified`, `never-linked`, `removed-earlier`, or
  `absent-before-removal` with PK *not authorized*;
* `pass-a.json`'s class is `removed`, `never-linked`, `removed-earlier` or
  `absent-before-removal`;
* CL-6 holds; and
* the unit is not active.

Every other combination is **HARD STOP** with a residual list (AC-9).

**Grant removal is claimed only with evidence.** `removed-verified` needs all
three of: a durable `removed` line written after the `unlinkat` and the
directory `fsync`; `ENOENT` at the path; and a *not authorized* PK result from
the same procedure that returned *authorized* at AV-1. Without all three, the
record says `removed-unconfirmed` or a non-removal class. It never says
`removed-verified`.

**If the record cannot be published** (for example `ENOSPC`), the attempt
ends HARD STOP `record-unpublished`. Its removals remain durable in its
journal, and the next attempt re-verifies and writes its own record. The
handback reports every journal's SHA-256 and length (OH-D-9).

##### (f) PK: the privileged grant-decision check

The root tool forks a **subject** process. The child sets the supplementary
groups, GID and UID that the H-1 record holds for `ubuntu`, then executes
`/usr/bin/sleep 60`. The tool runs:

```text
/usr/bin/pkcheck --action-id org.freedesktop.systemd1.manage-units
  --process ⟨pid⟩,⟨start-time⟩,⟨uid⟩
  --detail unit rp11-capture-pass-a.service --detail verb start
```

as **root**, without `--allow-user-interaction`, and then kills and reaps the
subject. The rule tests the `unit` and `verb` details. The design runs PK as
root so that it does not depend on whether the installed polkit honours
details from an unprivileged caller. If it did not, an unprivileged check would
report "not authorized" with the rule live, and would prove nothing.

PO-11(e) must cite how exit statuses map to decisions. The expected mapping is:

* 0 means authorized;
* 1, or 2 (authorization only with authentication), means not authorized; and
* any other status is an error, which counts as unconfirmed.

PK re-checks on a fixed schedule whose total length is the PO-11(d) bound.
There is no unbounded wait. PK does not start, stop or change anything.

##### (g) Activation records, schema `rp11-activation-record/1`

* **Serialization:** `canonical_bytes` (§4.3.1): ASCII, no floats, no `null`,
  and the string `"absent"` for absent facts. A schema test rejects any extra
  key and any value outside its grammar.
* **Destination:** `/var/lib/freedom-blades-rp11/activation/`, named
  `⟨activation_id⟩.act.json` (written once, by `ACT`, at its terminal state)
  and `⟨activation_id⟩.deact-⟨k⟩.json` (written by each attempt). Both are
  `root:root`, `0444` and published by PF. **Records are never deleted**,
  whether by CL, RB-1 or any other procedure.
* **Digest and length:** the SHA-256 and byte length of the file's exact
  bytes, including the final LF. They are reported in the handback (OH-D-9).

| Key | Content |
|---|---|
| `schema` | `"rp11-activation-record/1"` |
| `kind` | `"act"` or `"deact"` |
| `activation_id`, `attempt` | the identifier; `0` for `act`, `k` for `deact` |
| `authority` | `{a2_path, a2_sha256}` |
| `authority_limit` | the fixed OH-D-6 sentence of (b) |
| `h1_record` | `{record_id, sha256}` |
| `h2_record_sha256` | from A-2 |
| `boot` | `{pinned, observed_at_start, observed_at_end}` |
| `pass_config` | `{path, sha256_pinned, size, identity: {dev, ino} or "absent", class}` |
| `staged_rule` | `{path, sha256, dev, ino}` from the H-1 record, re-observed |
| `active_rule` | `{path, sha256_expected, identity: {dev, ino} or "absent", class}` |
| `grant_check` | `{procedure: "pk-root/1", bound_ms, authorized_at_act: exit status or "absent", after_cleanup: exit status or "absent"}` |
| `unit` | `{active_state_at_start, active_state_at_end}` |
| `st1` | `{verified: true or false, baseline_sha256_observed}` |
| `journals` | a list of `{path, sha256, length}` for the `ACT` journal and every attempt journal read. The writing attempt's own journal appears as its prefix up to the line before the record's `file-intent` |
| `act_record_sha256` | for `deact` only: the `act` record's digest, or `"absent"` if `ACT` died before writing it |
| `outcome` | `act`: `"activated"` or `"failed"`; `deact`: `"st1-verified"` or `"hard-stop"` |
| `failure` | `{step, class}`, or `"absent"` |
| `residual` | a list of `{path, class, type, uid, gid, mode, size, dev, ino, nlink, xattr_names, sha256 or "unreadable"}`. Empty when there is no residual. **No content**, and no environment content anywhere in the record |
| `time` | `{start_utc, end_utc, grant_linked_utc or "absent", grant_removed_utc or "absent"}` |

##### (h) Partial states and terminal paths

| # | Where `ACT` or the pass stopped | State found | Grant | What CL does | Terminal result |
|---|---|---|---|---|---|
| AC-1 | AP-0 or AP-1 | ST-1 | none from this activation. A pre-existing object at the rule path is A0, and PK reports its effect | nothing | `ACT` INVALID RUN. If AP-0 found an object at an activation path, that object is reported A0 and escalated |
| AC-2 | AM-0, or AM-1 before PF-6 returns | ST-1 (an unnamed inode at most, freed) | none | nothing to remove; CL-6 | `ACT` HARD STOP; `st1-verified` |
| AC-3 | AM-1's PF-6 returns `EEXIST` | ST-1 plus a foreign object at `pass-a.json` | none (the rule was never linked) | `pass-a.json` A0, kept; rule `never-linked`; PK *not authorized* | HARD STOP `foreign-pass-config`; residual escalated |
| AC-4 | after AM-1's link, before AM-2's PF-6 returns | ST-1.a1 | none | removes `pass-a.json` | `ACT` HARD STOP; `st1-verified` |
| AC-5 | AM-2's PF-6 returns `EEXIST` | ST-1.a1 plus a foreign object at the rule path | unknown; PK reports it | rule A0, kept; **`pass-a.json` removed** | HARD STOP `foreign-rule`; grant class `present-foreign-unremoved` with PK's result; escalated at once |
| AC-6 | after AM-2's link: crash, PF-9 or AV-1 failure, H-2b mismatch, or PK positive control not met within the bound | ST-1.a2 | **live** | **removes the rule first**, PK must be *not authorized*, then removes `pass-a.json` | `ACT` HARD STOP; `st1-verified` when all classes verify |
| AC-7 | AM-3 fails before the record's PF-6 returns | ST-1.a2 | live | as AC-6; the `act` record says `failed` (or `record-unpublished` if it cannot be written) | `ACT` HARD STOP; `st1-verified` or `record-unpublished` |
| AC-8 | after AM-3's link: ST-2, then a pass terminal state | ST-2, or ST-2 plus a capture root | live | `DEACT` k = 1: rule first, then `pass-a.json` | `st1-verified` or AC-9 |
| AC-9 | either path holds an A0 or A1-damaged object, PK still reports *authorized* after the bound, or the unit is still active | **ST-1+R** | as classed: never claimed removed without (e)'s three conditions | removes everything it can attribute; keeps the rest | **HARD STOP** with the exact residual and grant class; the A-2 authority is consumed; no pass may be authorized until Peter decides separately |
| AC-10 | reboot in ST-1.a1 … ST-3 | as found after boot. The rule file, if present, is **live** again once polkitd starts | as found | first `DEACT` attempt, recording the new `boot_id` and the interval since boot | `st1-verified` or AC-9 |
| AC-11 | a `DEACT` attempt killed | ST-1.a2, ST-1.d1 or ST-1 | as found | next attempt k + 1 | idempotent |
| AC-12 | `DEACT` repeated after `st1-verified` | ST-1 | none | nothing to remove; both classes `removed-earlier`; CL-6 | `st1-verified`, with a new record |

*(D3-R2.)* Rows **AC-10** and **AC-11** are withdrawn. They are replaced by the
event matrix of §4.2.5-R2 (k): a reboot clears the activation files from
`/run` (M-B) after an orderly transition has run CL, and a killed attempt is
retried by the backstop. AC-12 stands for the `stop-post` and `attest`
triggers. The backstop instead ends without a record once a `st1-verified`
record exists (BS-2).

**Idempotence.** An attempt removes only an object that is present **and**
A1-intact against the `ACT` journal's identity. After removal the object is
absent, and later attempts class it `removed-earlier`. Repeating `DEACT`
therefore never removes anything else, and it never fails because an earlier
attempt succeeded. Two concurrent attempts cannot both act: the
`ACT`-directory lock, together with exclusive creation of the attempt
directory, admits one at a time.

**Every terminal path reaches verified ST-1 or a precise HARD STOP.** By the
table, each row ends in `st1-verified` (CL-6 holds) or in AC-9's HARD STOP.
AC-9's record names each residual object and the grant's class. Whenever the
rule's identity is proven (A1-intact), CL-3 removes it **before** anything
else, so the grant is disabled. It is reported `removed-verified` only with
(e)'s three pieces of evidence. No path leaves `pass-a.json` to a later
authority. If its identity is proven, CL-5 removes it. If not, it is A0 or
A1-damaged residual, and the HARD STOP escalates it under AC-9 at once.

*(D3-R2.)* **The next paragraph, residual RR-2, is withdrawn.** It is kept only
as the D3-R1 text that Codex re-reviewed. §4.2.5-R2 (a), (k) and (l) replace it.

**Residual RR-2: a reboot leaves a live rule until `DEACT` runs.** An
unplanned reboot in ST-1.a2, ST-2 or ST-3 ends every process. The rule file
persists in `/etc/polkit-1/rules.d`, and polkitd loads it again at boot. The
grant is therefore usable until an actor runs `DEACT`. That is AC-10's first
act, and its record states the interval. During the interval:

* the bootstrap refuses any start with `entry-activation-stale`. This is
  diagnostic and not credited as prevention; and
* the exposure is no larger than `ubuntu`'s own unrestricted `sudo` (OH-D-6).

No procedure in this design can act while no process runs. Removing the
residual mechanically would need the active rule in a boot-cleared directory.
`/run/polkit-1/rules.d` is one candidate, if the installed polkit loads and
watches it. That would be a design change, needing its own citation, and it is
**not** adopted here. It is review focus §12.9 (3).

#### 4.2.5-R2 Supervised, boot-scoped activation and automatic cleanup *(D3-R2)*

> **D3-R2 text, superseded in part by D3-R3 (§4.2.5-R3).** Superseded: in
> (g), the paragraph "Latency bound" and every reading of HL as the mechanism
> that ends the grant after the pass; in (h), the GP paragraph from "3. It
> stops" to its end (replaced by GP-R3, §4.2.5-R3 (e)); in (j), the ST-1.d1
> row's "Left by" cell and a new state ST-1.ur; in (k), the EP cell of row
> ST-3, the row "HL detecting an end" and the conclusion "Each cell ends in
> …" as a statement about the post-pass grant; and in (n), item 3 as a proof
> and item 5's "GP never claims a removal" as the whole of GP. **Not
> superseded:** M-B, M-S, (b) … (f), (i), (l) and (o), and (m) apart from the
> enumerations that §4.2.5-R3 (h) extends. *(D3-R3)* markers below show each
> statement.
>
> **Also amended by D3-R4 (§4.2.5-R4 (g)):** (b) gains the consume-evidence
> row; (c) gains the interruption literal, the consume sentence and the
> start-timeout pin; in (d), AP-0, AM-0's lock, AV-1 and the last paragraph;
> in (g), the `pass-failed-early` row and the sentence on L; in (h), CL-1 and
> CL-3; in (j), the ST-2 and ST-3 rows, with ST-2.c and ST-2.f added; in (k),
> the ST-3 row, with an ST-2.c row added; in (m), the `consume` key; and in
> (n), item 3, which is replaced by §4.2.5-R4 (i). *(D3-R4)* markers below show
> each place.
>
> **Also amended by D3-R5 (§4.2.5-R5):** (b)'s consume-evidence row is created
> by CQ-2, under the lock, before any validation; (c) gains OS-8; in (d), AM-0
> and `hold-start` gain the start-history baseline (OS-1, OS-7); in (g), HL
> decides its end under the lock (OS-5) and its reasons are amended; in (j) and
> (k), the ST-2.c and ST-2.f rows; and in (m), the `consume` key, the `unit` key
> and the `run-start`/`hold-start` fields.
>
> **Also amended by D3-R6 (§4.2.5-R6):** in (c), A-2's pinned consume sentence
> gains the decided route (iii-a) condition (OS-6). Nothing else in this
> subsection changes.

This subsection remediates Blocking finding `OH-H1-D3-R1-1`. It is
**proposed** and inactive. It replaces the parts of §4.2.5-R1 listed in the
label at the head of that subsection, and it keeps everything else in
§4.2.5-R1: the identifier grammar, A-2's pins (extended in (b) below), the PF
and PT protocols, the journal format, PK, the attribution classes, G-R1 and the
record discipline.

##### (a) The defect and the two mechanisms that remove it

D3-R1 left the rule in a persistent directory and ran cleanup only inside
processes that a session loss, a process death or a reboot could end. After
such an event, cleanup waited for a later actor (§4.2.5-R1 (e) item 3, AC-10,
RR-2). D3-R2 removes that dependence with two mechanisms. Neither needs a
human action to disable the grant.

* **M-B, boot scope.** Both activation files live only on the `/run` tmpfs:
  the active rule at `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules` and
  the pass configuration at `/run/freedom-blades-rp11/pass-a.json`. A kernel
  boot starts with an empty `/run`, so neither file can exist in any boot
  after the one in which `ACT` created it. This holds after a power loss, a
  hard reset, a kernel panic or any reboot, whether or not any RP-11 process
  ran. It is a mechanical property of the host (PO-20 (g), PO-21 (g), HF-15),
  not a procedure.
* **M-S, supervision.** Within the boot, `ACT`, the wait for the pass's
  terminal state and cleanup run in a **transient system service supervised
  by PID 1**, not in any login session. The service's `ExecStopPost=` runs
  cleanup CL whenever its main process ends, for any cause. A second
  transient unit, the **backstop**, re-runs CL on a fixed period if the first
  invocation did not reach a terminal record. Session loss therefore does not
  touch the activation (PO-21 (a)). The death of `ACT`, of the holder or of the
  pass process ends the holder, and its end triggers CL (PO-21 (c)). The death
  of CL itself is retried by the backstop (PO-21 (j)).

No unit is installed or enabled for activation, and no unit is created before
A-2. Both transient units exist only in the manager's memory and in `/run`, and
neither survives a kernel boot (PO-21 (g)). Neither grants anything: each only
runs the root tool's `hold`, `deact` or `backstop` subcommand.

**Why not only one of them.** M-B alone would leave a live grant for the rest
of the boot after a session loss or a process death. M-S alone would leave the
rule in a persistent directory after a power loss, which no process survives.
Together they cover every event in (h). An automatically invoked startup
cleanup unit was considered and **not** selected. It would need a unit enabled
at every boot, ordered before `polkit.service`, as a standing root action in
ST-1. It would also prove its ordering only by a further systemd citation, and
it would do at boot what M-B gets from the absence of state. A rule that
expires itself (a time test inside the rule text) was also **not** selected. It
would change C11's reviewed rule bytes for every activation, depend on the
wall clock, and still need M-B for the boot boundary.

##### (b) Paths, owners and modes

| Object | Path | Owner:group | Mode | Created by | Removed by |
|---|---|---|---|---|---|
| pass-configuration directory (tree **P** top) | `/run/freedom-blades-rp11/` | `root:root` | `0755` | `ACT` (PT, AM-1) | CL (CL-5b), or the next kernel boot |
| pass configuration (tree **P** member) | `/run/freedom-blades-rp11/pass-a.json` | `root:root` | `0644` | `ACT` (PT, AM-1) | CL (CL-5), or the next kernel boot |
| rules directory | `/run/polkit-1/rules.d/` | `root:root` | `0755`, unless PO-11 (f) cites another mode | the distribution, if PO-11 (f) and HF-12 show it at boot. Otherwise `ACT` (tree **R**, AM-1R), only if PO-11 (f)(ii) holds | if `ACT` created it: CL (CL-5b), or the next kernel boot. A pre-existing one is **never** removed |
| active rule | `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules` | `root:root` | `0644` | `ACT` (PF, AM-2) | CL (CL-3), or the next kernel boot |
| holder unit | `⟨activation_id⟩.service` (transient) | PID 1 | — | AP-2 | PID 1, when it ends; a kernel boot |
| backstop units | `⟨activation_id⟩-backstop.timer` and `⟨activation_id⟩-backstop.service` (transient) | PID 1 | — | the holder at AK-1 | BS-2 or BS-3 (their own disarm); a kernel boot |
| installed tool | `/usr/local/libexec/freedom-blades-rp11/rp11_h1.py` (tree **L** member) | `root:root` | `0644` | H-1 (PT, M-1) | RB-1 only |
| `ACT` evidence and journal | `/var/tmp/⟨activation_id⟩-act-evidence/` (`ubuntu:ubuntu`, `0700`), `journal` (`root:root`, `0644`) | as stated | as stated | AP-1 (directory); AM-0 (journal) | **retained** |
| CL attempt evidence and journal | `/var/tmp/⟨activation_id⟩-deact-⟨k⟩-evidence/` (`root:root`, `0755`), `journal` (`root:root`, `0644`) | as stated | as stated | CL-0, as root | **retained** |
| activation records | `/var/lib/freedom-blades-rp11/activation/⟨activation_id⟩.act.json` and `….deact-⟨k⟩.json` | `root:root` | `0444` | PF (AM-3, CL-7) | **never** |

The D3-R1 activation paths `/etc/freedom-blades-rp11/pass-a.json` and
`/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules` are **withdrawn**. H-1 no
longer builds tree **E** (`/etc/freedom-blades-rp11/`). AP-0 requires
`/etc/freedom-blades-rp11` to be absent, and requires the basename
`50-freedom-blades-rp11.rules` to be absent from **every** rules directory that
PO-11 (f) lists for the installed polkit. A same-named file anywhere could
shadow or be shadowed by the active rule.

The CL attempt directory is now created by root, because CL runs in a
PID-1-supervised unit and not as `ubuntu`. It is `0755` so that `ubuntu` can
read the `0644` journal. The installed tool is the H-1 tool's exact bytes
(pinned SHA-256), placed in tree **L** so that the code a transient unit runs is
root-owned, bound by the H-1 record and compared by H-2. The ubuntu-owned
repository copy is not used for activation.

**Parents.** `/run`, `/run/polkit-1` and `/run/polkit-1/rules.d` (when present)
must be directories, not symbolic links, owned by root, without group or other
write permission and without a POSIX ACL extended attribute. `/run` must be a
`tmpfs` mount (HF-15, re-observed at AP-0 and AM-0 from `/proc/self/mountinfo`).
If `/run` is not a `tmpfs`, M-B does not hold, and `ACT` is INVALID RUN.

*(D3-R4.)* The table gains one row, the consume evidence and journal
`/var/tmp/⟨activation_id⟩-consume-evidence/` (`root:root`, `0755`; journal
`0644`), created by CP-4 and **retained** (§4.2.5-R4 (g)).

##### (c) What A-2 pins in addition to §4.2.5-R1 (b)

* the installed tool's SHA-256, equal to the H-1 record's
  `baseline.files[rp11_h1.py].sha256`;
* the **lease parameters**, as decimal integers:

  | Name | Meaning | Grammar |
  |---|---|---|
  | `start_window_s` (W) | time from `ACT` PASS within which the operator's start must be observed | 60 … 3,600 |
  | `lease_s` (L) | the holder's `RuntimeMaxSec=`: the longest the activation may last | W < L ≤ 86,400 |
  | `poll_ms` (Δ) | the hold loop's observation period | 250 … 5,000 |
  | `stop_timeout_s` (S) | the holder's `TimeoutStopSec=`, which bounds CL in `ExecStopPost=` | ⌈PO-11(d) bound / 1,000⌉ + 30 … 600 |
  | `backstop_period_s` (R) | the backstop timer's period | 30 … 600 |

* the two fixed command literals of (e) and (f), with each `⟨…⟩` filled, and
  their SHA-256 values;
* the sentence: *"While this activation is unterminated, no reboot,
  userspace-only restart (soft-reboot), kexec, suspend or hibernation is
  issued, and no transient unit of this activation is stopped, killed or
  changed, except by the RP-11 procedures named here."* It is an authority
  statement. Mechanically M-B covers every kernel boot, and DF-1 in (i)
  states what remains; and
* the sentence of §4.2.5-R1 (b) on `DEACT`, extended: *"`DEACT`, in every
  trigger (`stop-post`, `backstop` and `attest`), is mandatory and
  automatically authorized under this authority."*

*(D3-R4.)* A-2 also pins the route (iii-a) interruption literal and its
SHA-256, the consume sentence, and the unit's recorded start timeout, which
must be finite and at least ⌈PO-11 (d) bound / 1,000⌉ + 30 seconds
(§4.2.5-R4 (g)).

*(D3-R6.)* The pinned consume sentence also states the decided route (iii-a)
condition: the capture unit `active`, its `InvocationID` equal to the consume
journal's `run-start.invocation_id`, and a `consumed` line; never while
`activating`. The full sentence is §4.2.5-R6 (g), "A-2".

##### (d) `ACT` and hold order

`ACT` is now split between the executor's session, which only prepares and
requests, and the holder, which mutates. Rows marked *(D3-R1)* keep their
D3-R1 definition, except for the target paths of (b).

| Step | Where | Action | On failure | State once committed |
|---|---|---|---|---|
| AP-0 *(D3-R1, amended)* | executor, unprivileged | §4.2.5-R1 AP-0, plus: `/run` is `tmpfs`; the (b) parent conditions; tree **P**'s top, the rule path and `/etc/freedom-blades-rp11` absent; the rule basename absent from every PO-11 (f) directory; `/run/polkit-1/rules.d` present, or absent with PO-11 (f)(ii) accepted; `systemctl show -p LoadState` is `not-found` for `⟨activation_id⟩.service`, `⟨activation_id⟩-backstop.timer` and `⟨activation_id⟩-backstop.service`; the capture root named in `pass-a.json` absent; every PO-21 (i) condition for a userspace-only restart absent; **no unterminated activation** of this H-1 record (each has a `deact` record with outcome `st1-verified`, or ST-1+R has been decided by Peter); the PO-11 (d) … (f), PO-20 (g) and PO-21 citations accepted for the observed versions; the installed tool's digest as pinned | **INVALID RUN**; nothing mutated | ST-1 |
| AP-1 *(D3-R1)* | executor | create the `ACT` evidence directory; this consumes the identifier | INVALID RUN | ST-1 |
| **AP-2** | executor, privileged | issue the holder literal of (e) once. Its only effect is the transient holder unit. The executor then waits, without input, for the `act` record or the holder's end, reading only records, journals and `systemctl show -p ActiveState,Result ⟨activation_id⟩.service` | if `⟨activation_id⟩.service` is not loaded afterwards: **INVALID RUN**, nothing mutated. If it is loaded, the holder governs from here, whether or not the executor's session survives | ST-1 |
| AM-0 *(D3-R1, amended)* | holder | re-check, as root, AP-0's `boot_id`, `/run` and absence conditions; lock the `ACT` evidence directory and **keep the lock until the holder exits**; create the journal; append `run-start {a2_sha256, h1_record_sha256, h2_record_sha256, boot_id, pass_config_sha256, staged_rule_sha256, tool_sha256, holder_invocation_id, lease}` | exit non-zero, then CL (stop-post) | ST-1 |
| **AK-1** | holder | append `backstop-intent`; run the backstop literal of (f); require `⟨activation_id⟩-backstop.timer` to be `active`; append `backstop-armed {timer, period_s}`. **No activation file exists before this commit** | exit non-zero, then CL (stop-post) | **ST-1.a0** |
| AM-1 *(amended)* | holder | PT builds tree **P** (`/run/freedom-blades-rp11/` with member `pass-a.json`) in `/run` | exit non-zero, then CL | **ST-1.a1** |
| AM-1R *(only if `/run/polkit-1/rules.d` was absent)* | holder | PT builds tree **R**: its top is the first absent component of `/run/polkit-1/rules.d`, with no file member | exit non-zero, then CL | ST-1.a1 |
| AM-2 *(D3-R1, amended)* | holder | PF publishes the active rule into `/run/polkit-1/rules.d/` with `grant: true`; **the grant is live from PF-6** | exit non-zero, then CL | **ST-1.a2** |
| AV-1 *(D3-R1)* | holder | both files as in PF-9; H-2b; PK *authorized* within the PO-11 (d) bound | exit non-zero, then CL | ST-1.a2 |
| AM-3 *(D3-R1)* | holder | PF publishes `⟨activation_id⟩.act.json` with `outcome: "activated"`; its commit is **`ACT` PASS** | exit non-zero, then CL | **ST-2** |
| HL | holder | the hold loop of (g) until a terminal condition; append `hold-end {reason}`; exit `0` | — | ST-2 or ST-3, then CL |

`ACT` never runs CL in-process any more. Every end of the holder, including a
failed `ACT`, leads to CL through `ExecStopPost=`. The D3-R1 rule that a linked
`activated` record counts as `ACT` PASS (§4.2.5-R1 (d), last paragraph) is
kept. A-2 permits the operator's `start` only while that record exists **and**
the holder's `ActiveState` is `active`.

*(D3-R4.)* AP-0, AM-0, AV-1 and the preceding paragraph are amended by
§4.2.5-R4 (g). The holder releases the lock once `hold-start` is durable. AV-1
adds the PK negative control for verb `stop`. The `start` additionally needs
`hold-start` in the `ACT` journal.

##### (e) The holder literal (AP-2)

```text
sudo -n /usr/bin/systemd-run --system --no-ask-password --quiet
  --unit=⟨activation_id⟩ --service-type=exec
  --property=Restart=no --property=OOMScoreAdjust=-1000
  --property=RuntimeMaxSec=⟨L⟩ --property=TimeoutStopSec=⟨S⟩
  "--property=ExecStopPost=/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py deact ⟨activation_id⟩ ⟨a2_sha256⟩ stop-post"
  /usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py hold ⟨activation_id⟩ ⟨a2_sha256⟩
```

It is one command line; the breaks are for layout. It contains no
`--setenv`, `-E`, `--scope`, `--user`, `--pty`, `--wait`, `--collect` or other
`--property=` key. Apart from the shell quotes around the `ExecStopPost=`
argument, no argument contains `%`, `$`, `\` or a quotation mark, so systemd's specifier and variable expansion cannot change it
(PO-21 (b)). The holder runs with PID 1's environment, not `sudo`'s (PO-21
(b)), which narrows §4.2.4's stated `sudo` environment limit for `ACT`. A unit
name that is already loaded makes the call fail (PO-21 (m)), and AP-0 has
already required that it is not.

##### (f) The backstop literal (AK-1) and the backstop procedure BS

```text
/usr/bin/systemd-run --system --no-ask-password --quiet
  --unit=⟨activation_id⟩-backstop --on-active=⟨R⟩ --on-unit-active=⟨R⟩
  --timer-property=AccuracySec=1s --service-type=exec
  --property=Restart=no --property=OOMScoreAdjust=-1000 --property=TimeoutStartSec=⟨S⟩
  /usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py backstop ⟨activation_id⟩ ⟨a2_sha256⟩
```

The holder issues it as a child process, as root, under the same grammar rules
as (e). Each firing runs **BS**, which reads before it writes:

| Step | Condition | Action |
|---|---|---|
| BS-1 | the holder's `ActiveState` is `activating`, `active`, `deactivating` or `reloading` | exit `0`. No record, no mutation. The holder, or its `ExecStopPost=`, still owns the activation |
| BS-2 | a `deact` record of this activation with outcome `st1-verified` exists, is `root:root` `0444` and parses | `systemctl stop ⟨activation_id⟩-backstop.timer` (disarm), then exit `0`. No record |
| BS-3 | the latest `deact` record is `hard-stop`, its residual contains no A1-intact object, and its grant class is not `removed-unconfirmed` or `grant-unremovable` | disarm, then exit `0`. Nothing further can be removed without Peter (ST-1+R) |
| BS-4 | otherwise | run CL with trigger `backstop`. If `k` would exceed 99, disarm and exit non-zero without a record; the journals stand |

BS never starts, stops or kills the holder or the capture unit. The disarm is
the only `systemctl` verb that BS issues, and it names only this activation's
own timer.

##### (g) The hold loop HL and the terminal predicate

At AM-0 the holder records the capture unit's `ActiveState` `a₀` and
`InvocationID` `i₀` (possibly empty), and the capture root `c` that
`pass-a.json` names. AP-0 required `c` to be absent. Every Δ milliseconds after
`ACT` PASS, HL observes:

* whether `c` exists, by `lstat` only. HL never lists, opens or changes `c`
  (§4.6.2's "never touched" list stands); and
* `systemctl show -p ActiveState -p InvocationID rp11-capture-pass-a.service`.

| Reason | Condition | Meaning |
|---|---|---|
| `pass-ended` | `c` exists, and `ActiveState` is `inactive` or `failed` | the pass reached X-1 and its process has ended |
| `pass-failed-early` | `ActiveState` is `failed` and `InvocationID` is non-empty and differs from `i₀` | the pass started and failed before X-1. Premise **P-E**: every exit of `rp11-launch` or the bootstrap before X-1 has a non-zero status (C11 §6.5; OH-S4 test) |
| `start-window-expired` | W seconds have passed since `ACT` PASS, `c` is absent, `InvocationID` is `i₀` or empty, and no observation since `ACT` PASS showed `activating`, `active`, `deactivating` or `reloading` | no pass started |
| `observation-failed` | an observation errors or does not parse | fail closed: the activation ends |

The first matching reason ends HL. The holder appends `hold-end {reason,
observation}` and exits `0`; `observation-failed` exits non-zero. A pass that is
still running at L is ended by systemd's `RuntimeMaxSec=` (PO-21 (d)). CL then
removes the grant while the unit is active, and its outcome cannot be better
than HARD STOP `unit-still-active` (§4.2.5-R1 CL-2). HL never relies on the
`InvocationID` of an `inactive` unit, which may have been unloaded (PO-21 (k)).
A pass that succeeds always leaves `c`.

**Latency bound.** After the pass's terminal state the rule is unlinked within
Δ plus the time for CL-0 … CL-3, which are local operations bounded by S. If
that CL invocation dies before CL-3, the backstop unlinks it within R plus the
same time. A kernel boot removes it unconditionally.

*(D3-R3.)* **The "Latency bound" paragraph is withdrawn as a statement about
OH-D-7.** It describes a normal interval after the pass in which the grant is
live, which is Blocking finding `OH-H1-D3-R2-1`. HL stays only as the
activation's lifetime control: it ends the activation at W, at an observation
failure and after the pass, so that CL removes `pass-a.json` and writes the
records. **HL establishes no grant boundary.** §4.2.5-R3 (b) shows that no
cleanup that begins after the pass can establish one, and (c) states the
decision that can.

*(D3-R4.)* OH-D-10 is decided, and the boundary is established before the
pass by CP (§4.2.5-R4 (c), (i)). HL stays lifetime and recovery machinery only
(§4.2.5-R4 (f)). Its `pass-failed-early` row is split by the new reason
`start-failed-before-exec`. The sentence above on a pass still running at L is
corrected: `RuntimeMaxSec=` ends the holder, and so the activation, not the
capture unit (§4.2.5-R4 (g)).

##### (h) Cleanup CL, as amended by D3-R2

CL keeps §4.2.5-R1 (e)'s steps, classes and outcome rule, with these changes.

| Step | D3-R2 definition |
|---|---|
| CL-0 | **Trigger** `t` ∈ {`stop-post`, `backstop`, `attest`}. `stop-post` is run only by systemd as the holder's `ExecStopPost=`; `backstop` only by BS-4; `attest` only under (i). For `stop-post` and `backstop` the tool records its parent PID and `INVOCATION_ID` as provenance (diagnostic only). Root takes `flock(LOCK_EX)` on the `ACT` evidence directory, retrying `LOCK_NB` every second for at most S seconds, else it stops with `lock-timeout` and acts on nothing. It then creates the attempt directory exclusively as root (`0755`), `k` being 1 plus the number of existing attempt directories (`EEXIST`: `concurrent-deact`, nothing acted on), creates the journal and appends `run-start {trigger, boot_id, holder_state}`. If the directory or the journal cannot be created, CL enters **grant-priority mode GP** (below) instead of stopping |
| CL-1 | as D3-R1, plus **boot scoping**: an identity line for an object under `/run` is valid only in the boot recorded by the `ACT` journal's `run-start`. In any other boot every object found under `/run` is **A0** |
| CL-2 | as D3-R1 |
| CL-3 | **the grant first**, as D3-R1, at the `/run` rule path. New classes: **`cleared-by-boot`**, when the current `boot_id` differs from the `ACT` journal's, `/run` is `tmpfs`, an identity line for the rule exists and the path gives `ENOENT`; and **`grant-unremovable`**, when the rule is A1-intact but `unlinkat` fails. Under GP an A1-intact rule is re-verified and removed **without** this attempt's write-ahead line (below) |
| CL-4 | as D3-R1. PK must return *not authorized* within the PO-11 (d) bound |
| CL-5 | `pass-a.json` at `/run/freedom-blades-rp11/pass-a.json`, as D3-R1, with the class `cleared-by-boot` added. Always attempted, even when CL-3 could not remove the rule |
| **CL-5b** | directories: tree **P**'s top, then any directory of tree **R**, each removed by G-R1 only if it is A1-intact against the `ACT` journal and empty. Run-unique temporary names left by window W-T under `/run` are **S0**, reported and kept; the next kernel boot clears them. A pre-existing `/run/polkit-1/rules.d` is never removed |
| CL-6 | verify ST-1 at the D3-R2 paths: the rule, `pass-a.json` and tree **P**'s top absent; `/run/polkit-1/rules.d` present with its AP-0 identity if it pre-existed, absent if `ACT` created it; `/etc/freedom-blades-rp11` and the rule basename still absent everywhere they were at AP-0; the recomputed `baseline` equal to the H-1 record's `baseline_sha256`; PK *not authorized*; the capture unit not active |
| CL-7 | records, as D3-R1, with one change. If no `act` record exists, this attempt first publishes `⟨activation_id⟩.act.json` with `outcome: "failed"`. A later attempt never writes a second `act` record. Then it publishes `⟨activation_id⟩.deact-⟨k⟩.json` |

**Outcome.** `st1-verified` if and only if D3-R1's outcome rule holds with the
class `cleared-by-boot` admitted beside `removed-verified`, `never-linked`,
`removed-earlier` and `absent-before-removal` for the rule, and beside
`removed`, `never-linked`, `removed-earlier` and `absent-before-removal` for
`pass-a.json`. Every other combination is HARD STOP (ST-1+R).

**GP, grant-priority mode.** Disabling the grant never waits for evidence
input/output. If CL-0 cannot create its evidence, or a later journal append
fails before CL-3 completes, CL still performs CL-1 (read only) and CL-3:

1. It removes the rule if, and only if, it is A1-intact against the `ACT`
   journal and passes G-R1's descriptor re-verification.
2. It then attempts CL-4.
3. It stops. The outcome is HARD STOP `evidence-unwritable`, and no claim of
   removal is made.

The next trigger classifies the absent rule as `absent-before-removal` and
must then obtain PK *not authorized* before it may record `st1-verified`. GP
changes nothing about attribution. P-1 rests on the A1-intact check and the
descriptor re-verification, and a missing removal line can only make a later
attempt claim less. GP applies to the rule only. `pass-a.json` and the
directories are removed only with this attempt's write-ahead lines.

*(D3-R3.)* **Item 3 and the last two sentences are withdrawn** (Blocking
finding `OH-H1-D3-R2-2`). GP no longer stops after the grant. It continues as
GP-R3 (§4.2.5-R3 (e)): it removes an A1-intact `pass-a.json`, then tree **P**'s
top and any tree **R** directory that `ACT` created, each re-verified through a
descriptor immediately before removal. It then ends in ST-1.ur, a cleared but
unrecorded state, without claiming any removal.

*(D3-R4.)* CL-1 also reads CP's consume journal, and CL-3 classes a rule that
CP removed as `removed-earlier`, or `absent-before-removal` when no durable
`removed` line exists (§4.2.5-R4 (g)). CL and CP take the same lock. CL never
runs CP, and CP never removes `pass-a.json`. GP-R3 is unchanged.

##### (i) Attestation when no automatic trigger remains

After an unclean kernel boot, M-B has already removed both activation files
(state **ST-1.bc**). Nothing needs to be disabled. What is missing is the
**record** of that outcome, because no process survived to write it. The same
holds in two same-boot cases in which no activation file can exist: the
holder's CL dies before AK-1 armed the backstop, when no file had yet been
created (AK-1 precedes AM-1); and BS-4 reaches `k` = 99.

* **Gate.** H-2, AP-0, H-1R and RB-1 each refuse to start while any activation
  of the H-1 record has no `deact` record with a terminal outcome. The refusal
  is fail-closed: no later RP-11 step can act on an unattested state.
* **Attest.** Any actor working under that activation's A-2 runs, in an
  interactive session on `oracle-test`:

  ```text
  sudo -n /usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py deact ⟨activation_id⟩ ⟨a2_sha256⟩ attest
  ```

  It requires that neither `⟨activation_id⟩.service` nor either backstop
  unit is `activating`, `active`, `deactivating` or `reloading`. A unit that
  is `not-found`, `inactive` or `failed` does not block it. Then it runs CL
  with trigger `attest`. In a later boot it can find nothing A1 under `/run`
  (CL-1), so it removes nothing attributable. In the same boot it is CL with
  its ordinary classes. It records the classes `cleared-by-boot` and
  `st1-verified` only if CL-4 and CL-6 hold.
* **Why this is not the deferral of D3-R1.** Attestation disables nothing,
  because the grant ceased to exist when the kernel booted. The record it
  writes is evidence of what the boot did, and it claims nothing without its
  own post-check. Until it exists, every later RP-11 step refuses. Under D3-R1
  the **grant** waited for the later actor. Under D3-R2 only the **record**
  does.

*(D3-R3.)* ST-1.ur (§4.2.5-R3 (f)) is a further state in which only the record
is missing. The gate above already covers it, because no terminal `deact`
record exists. Normally BS-4 records it within R once evidence can be
written. Attestation is needed only if the boot ends first, or if no backstop
remains.

##### (j) States

The D3-R1 states table (§4.2.2) is amended for the activation rows only. The
H-1 rows are unchanged, apart from tree **E**'s withdrawal (§4.2.4-R1 (e)).

| State | Activation objects present | Grant? | Entered by | Left by |
|---|---|---|---|---|
| **ST-1** | none under `/run`; no unterminated activation | no | H-1 PASS; CL `st1-verified` | AP-2 under a new A-2; RB-1 (separate) |
| **ST-1.a0** | holder `active`, backstop armed, no file | no | AK-1 | AM-1, or the holder's end, then CL |
| **ST-1.a1** | tree **P** (and tree **R**, if built) | no | AM-1 | AM-2, or the holder's end, then CL |
| **ST-1.a2** | plus the rule; `act` record absent | **yes, live** | AM-2 | AM-3, or the holder's end, then CL with **the rule first** |
| **ST-2** | plus the `act` record `activated`; holder in HL | yes | AM-3 | the operator's start (ST-3), or HL's end, then CL |
| **ST-3** | plus the running unit and the capture root | yes | the operator's start | HL's end, then CL |
| **ST-1.d1** | rule removed, `pass-a.json` (or tree **P**'s top) remains | no | a CL attempt that ended after CL-3 | the same attempt continuing; else BS-4 within R; else the next kernel boot |
| **ST-1.bc** | none: cleared by a kernel boot; no terminal record yet | no | an unclean kernel boot in ST-1.a0 … ST-3 or during CL | attestation (i). Every later RP-11 step refuses until then |
| **ST-1+R** | as recorded. An A1-intact rule appears only as `grant-unremovable`, and BS-4 keeps retrying it | as recorded | a CL HARD STOP | Peter's separate decision; the A-2 authority is consumed |

*(D3-R3.)* ST-1.d1's "Left by" also includes the GP-R3 continuation of the
same attempt, which removes `pass-a.json` and the directories without a
write-ahead line. The state **ST-1.ur** is added (§4.2.5-R3 (f)). The rows ST-2
and ST-3 still show a live grant during the pass. That is the subject of
OH-D-10 (§4.2.5-R3 (c)).

*(D3-R4.)* The ST-2 and ST-3 rows above are superseded by §4.2.5-R4 (g). In
ST-2 the grant is `start` only. ST-2.c (CP running) and ST-2.f (failed start,
no pass) are added. In ST-3 there is **no** grant.

##### (k) Every death, session-loss, power-loss and reboot boundary

Events:

* **ES**, loss of the executor's or operator's interactive session;
* **EH**, death of the holder's main process for any cause, including `ACT`'s
  own failure, `SIGKILL`, a crash and `RuntimeMaxSec=` expiry;
* **EP**, the end or death of the pass process;
* **EC**, death of a CL invocation;
* **EO**, an orderly transition: `systemctl reboot`, `poweroff`, `halt` or
  `kexec`, all of which stop units first (PO-21 (h)); and
* **EU**, an unclean kernel boot: power loss, hard reset, panic, watchdog or a
  forced reboot that skips unit stop.

A userspace-only restart is treated separately in (l).

Codes:

* **SP**: the holder ends, and `ExecStopPost=` runs CL (PO-21 (c)).
* **BS**: the backstop runs CL within R.
* **BC**: the kernel boot clears `/run` (M-B), then attestation (i) records
  `cleared-by-boot`.
* **—**: no effect; the activation continues.
* **INV**: `ACT` INVALID RUN. No activation file exists, and ST-1 is
  unchanged.

| State when the event occurs | ES | EH | EP | EC | EO | EU |
|---|---|---|---|---|---|---|
| AP-0, AP-1 (no holder) | INV | n/a | n/a | n/a | INV | INV |
| AP-2 in flight | — if the holder was created, otherwise INV | as the next row | n/a | n/a | as the next row, or INV | BC, or INV |
| AM-0, before AK-1 (no backstop yet, no file) | — | SP: nothing to remove; `act` record `failed` | n/a | no file ever existed: ST-1, recorded by attestation (i) | SP | BC: nothing was created |
| ST-1.a0 | — | SP | n/a | BS | SP | BC |
| ST-1.a1 | — | SP: removes `pass-a.json` and tree **P**; rule `never-linked` | n/a | BS | SP | BC |
| ST-1.a2 | — | SP: **rule first**, PK, then `pass-a.json` | n/a | BS | SP | BC |
| ST-2, before the start | — (HL ends at W) | SP | n/a | BS | SP | BC |
| ST-3 | — (the pass continues as a system service) | SP: rule removed while the unit is active, so HARD STOP `unit-still-active` | HL ends within Δ, then SP | BS | SP: the transition stops the pass and the holder | BC; the pass is interrupted (§9.5.3) and its capture root is retained |
| HL detecting an end (≤ Δ) | — | SP | — | BS | SP | BC |
| CL before CL-3 is durable | — | n/a | n/a | BS | the transition's stop of CL, then BC | BC |
| CL after CL-3, before CL-5 | — | n/a | n/a | BS removes `pass-a.json` | BC | BC |
| CL after CL-5, before CL-7 | — | n/a | n/a | BS writes the records | BC records by attestation | BC records by attestation |

Each cell ends in `st1-verified`, in an AC-9 HARD STOP (ST-1+R), or in ST-1.bc
followed by attestation. **In no cell does disabling the grant wait for a
human action.** No cell leaves `pass-a.json` for a later authority. The only
human-run step, attestation, follows EU and disables nothing.

*(D3-R3.)* The matrix still holds for **human action**: no cell waits for a
person. It does **not** show that no grant remains after the pass. In row
ST-3, the EP cell leaves the rule live after the pass process has ended, for Δ
plus the CL time. If that CL then dies (column EC), the backstop leaves it live
for up to R more. In every cell, the rule also stays loaded in polkitd until
the PO-11 (d) reload that follows the `unlinkat`. That is `OH-H1-D3-R2-1`. The
row "HL detecting an end" is
withdrawn as a grant-boundary row. §4.2.5-R3 (g) adds the evidence-failure
rows.

*(D3-R4.)* The ST-3 row is replaced, and a row for ST-2.c is added
(§4.2.5-R4 (g)). With them, no cell in which a pass exists has a grant. In the
replaced ST-3 row, the EP cell's interval is now one with no grant. It
governs only the removal of `pass-a.json` and the records.

##### (l) What remains, stated exactly

* **DF-1, a double fault in a userspace-only restart.** PO-21 (i) must state
  whether the installed systemd can restart userspace while keeping the kernel,
  and so the `boot_id` and `/run`. One example is `systemctl soft-reboot`.
  Such a restart stops units first, so SP still runs CL. If that CL dies
  before CL-3 (for the rule) or before CL-5 (for `pass-a.json`) **and** the
  restart then completes, the backstop is gone, the `boot_id` is unchanged and
  M-B does not apply. The object then persists until attestation. This needs
  two things together: a CL failure, and an explicit root command that A-2
  prohibits. No single event in (k) reaches it. AP-0 refuses if any automatic
  path to such a restart that PO-21 (i) identifies is armed. If PO-21 (i)
  finds a path that cannot be disarmed, the design returns to review.
* **SL-1, deliberate root acts outside A-2.** Root can kill the holder and the
  backstop, stop timers, write a rule anywhere, or force a transition that
  skips unit stop. Under OH-D-6 and M-10 these are acts against the authority
  boundary, not T-A events. That limit is already stated for G-R1 and for
  ST-1's privilege status. D3-R2 does not change it.
* **GU, `grant-unremovable`.** An A1-intact rule whose `unlinkat` fails is
  recorded with the `errno`. BS-4 retries it every R. A kernel boot removes it.
  No T-A cause is identified for a root `unlinkat` failure on `tmpfs` in a
  root-only directory, but the class is kept so that the record never claims
  a removal that did not happen.

**Residual RR-2 is withdrawn.** No statement in this design lets the grant
wait for a later actor after a session loss, a process death, a power loss or
a reboot.

##### (m) Immutable evidence, and what survives a kernel boot

| Evidence | Location | Survives a kernel boot? | Returned under OH-D-9 by |
|---|---|---|---|
| `act` record | `/var/lib/freedom-blades-rp11/activation/` | yes | the pass handback, or the attestation handback |
| `deact-⟨k⟩` records | the same | yes | the same |
| the `ACT` journal (`run-start`, `backstop-armed`, the publication lines, `hold-end`) | `/var/tmp/⟨activation_id⟩-act-evidence/journal` | yes. HF-19 ageing is covered by the reported digest and length | the same |
| CL attempt journals | `/var/tmp/⟨activation_id⟩-deact-⟨k⟩-evidence/journal` | yes | the same |
| the activation files and the transient units | `/run`, manager memory | **no, by design (M-B)** | not evidence. Their identities and digests are in the journals and records |

Every returned copy is bound by the SHA-256 and byte length that the retaining
executor reports. The `deact` record's `journals` list gives the digest and
length of every journal that the attempt read (§4.2.5-R1 (g)). No record is
ever deleted.

**Schema `rp11-activation-record/2`.** It is `rp11-activation-record/1`
(§4.2.5-R1 (g)) with these changes. `/1` was never implemented and is
superseded.

* `pass_config.path` and `active_rule.path` take the (b) paths.
* New keys:
  * `trigger`: `"act"`, `"stop-post"`, `"backstop"` or `"attest"`;
  * `holder`: `{unit, invocation_id, active_state_at_start, result, hold_end_reason}`,
    each value or `"absent"`;
  * `lease`: the five (c) values; and
  * `evidence_mode`: `"journaled"` or `"grant-priority"`.
* `boot` becomes `{pinned, act_boot, observed_at_start, observed_at_end,
  run_fstype}`.
* The class enumerations gain `cleared-by-boot`, and the grant enumeration
  also gains `grant-unremovable`.
* The outcome `hard-stop` gains the failure classes `lock-timeout`,
  `evidence-unwritable` and `observation-failed`.

**The `ACT` journal's closed `op` set** is `run-start`, `backstop-intent`,
`backstop-armed`, `tree-intent`, `dir-identity`, `file-intent`,
`file-identity`, `file-linked`, `tree-sealed`, `tree-linked`, `grant-check`,
`hold-start`, `pass-observed`, `hold-end` and `run-end`. `pass-observed` is
appended only when an observation differs from the previous one, not at every
poll. **A CL attempt journal's closed `op` set** is `run-start`,
`remove-intent`, `removed`, `remove-failed`, `grant-check`, `classified`,
`file-intent`, `file-identity`, `file-linked` and `run-end`.

*(D3-R4.)* `deact` records gain the key `consume`, and `hold_end_reason`
admits `start-failed-before-exec`. The consume journal is retained evidence
with its own closed `op` set (§4.2.5-R4 (c), (g)). Like the other journals, it
survives a kernel boot and is returned under OH-D-9 with its digest and length.

##### (n) Proof that the one-pass, one-boot boundary is enforced

1. **No grant before A-2.** H-1 places no rule, and the staged rule is outside
   every rules directory (PO-11 (c)). AP-0 requires A-2's digest before AP-2,
   and only the holder that AP-2 creates links a rule (AM-2).
2. **No grant in a later boot.** The rule exists only on `/run`. A kernel boot
   starts with an empty `/run` (PO-20 (g), PO-21 (g)), and polkitd keeps no
   rule across its own restart (PO-11 (f)(iv)). AM-0 re-checks that the
   `boot_id` equals A-2's before AM-2 links anything.
3. **No grant after the pass in the same boot.** HL ends at the pass's
   terminal state ((g)). The holder's end runs CL with the rule first
   (PO-21 (c)). The death of that CL is retried by BS every R
   (PO-21 (j)). A pass that outlives L is cut off by `RuntimeMaxSec=`
   (PO-21 (d)).
4. **One pass.** One identifier, one holder (PO-21 (m)), one capture root
   created exclusively (TR-11), and HL ends the activation at the first
   observed terminal state.
5. **Removal is claimed only with evidence.** `removed-verified` keeps D3-R1's
   three conditions. `cleared-by-boot` needs a changed `boot_id`, `tmpfs`
   observed, `ENOENT` and PK *not authorized*. GP never claims a removal.

*(D3-R3.)* **Item 3 is withdrawn as a proof.** HL observes the end of the pass
only after it has happened, and CL starts only after that. The rule therefore
stays live for a normal interval after the pass (`OH-H1-D3-R2-1`). §4.2.5-R3 (b)
shows that an event trigger cannot remove the interval either, so the item is
**open** pending OH-D-10, not replaced. Items 1, 2 and 4 stand. Item 5 stands,
and GP-R3 also claims no removal (§4.2.5-R3 (e)).

*(D3-R4.)* Item 3 is **replaced** by §4.2.5-R4 (i): the grant is consumed and
verified absent before `ExecStart=`, so none exists during or after any pass.
That proof does not rely on HL, on `ExecStopPost=` or on the backstop.

Each step that rests on host behaviour names its proof obligation. If an
obligation is not accepted for the observed versions, AP-0 is INVALID RUN and
no grant is ever linked. That is the fail-closed rule.

##### (o) Activation cleanup and RB-1 stay distinct

CL, BS and attestation act only on the activation objects of (b), and on
records and journals that they write themselves. They never remove an H-1
object, never run `daemon-reload` and never invoke RB-1. RB-1 (§4.6.2-R1) is
still separately authorized and never automatic. It never touches `/run`. Its
precondition gains two conditions: no transient unit of any activation of this
H-1 record is loaded, and every such activation has a terminal `deact` record
(including `cleared-by-boot`). RB-1 now also removes the installed tool, as a
member of tree **L**, and has no tree **E** to remove.

#### 4.2.5-R3 Pass-terminal coupling, blocked on OH-D-10, and complete grant-priority cleanup *(D3-R3)*

> **D3-R3 text, kept as history; amended by D3-R4 (§4.2.5-R4).** OH-D-10 is
> decided: Option A with interruption route (iii-a). (a)'s "Not adopted"
> bullet, (c)'s open question, (d)'s "not adopted" status and the first
> bullet of (j) are superseded. (d) is adopted as §4.2.5-R4 states, without
> route (iii-b) and with refinements AR-1 … AR-8. Where (d) and §4.2.5-R4
> differ, §4.2.5-R4 governs. (b)'s impossibility argument stands as the
> reason for the decision. (e) … (i), GP-R3 and ST-1.ur, stand unchanged.

This subsection responds to Blocking findings `OH-H1-D3-R2-1` and
`OH-H1-D3-R2-2`. It is **proposed** and inactive. It keeps every part of
§4.2.5-R2 that the label at the head of that subsection does not supersede.

##### (a) What D3-R3 adopts and what it does not

* **Adopted** (`OH-H1-D3-R2-2`): GP-R3 (e), the state ST-1.ur (f), the
  evidence-failure rows (g), the record amendments (h) and the proof
  amendments (i).
* **Not adopted** (`OH-H1-D3-R2-1`): the pass-terminal coupling. (b) shows that
  the accepted texts cannot provide it. (c) states the maintainer decision
  OH-D-10. (d) specifies the recommended option at the mechanical level, so
  that a successor can adopt it, but **this revision does not adopt it**.
* **Unchanged:** OH-D-1 … OH-D-9; PF, PT, the journal format, RS-1, G-R1, P-1,
  P-2 and RB-1; M-B (`/run`), M-S (the holder, `ExecStopPost=` and the
  backstop); AP-0 … AM-3; PK; the attribution classes; attestation; and every
  proof obligation already defined.

##### (b) Why `OH-H1-D3-R2-1` cannot be met within the accepted texts

The accepted boundary is OH-D-7's *"No live Polkit grant may … remain after
the pass."* Three facts bear on it.

* **GB-1, the grant is live during the pass.** C11's rule grants `start` **and**
  `stop` to `ubuntu` for the capture unit. `stop` exists *"so that the operator
  can interrupt a hung pass"* (C11 §4.4.3.4), and this proposal keeps the rule
  text (§4.7.2). In ST-3 the grant is therefore live at every instant.
* **GB-2, the pass can end at any instant without cooperating.** `SIGKILL`, a
  crash, a kernel OOM kill or a `systemctl stop` ends the entry, and the
  operational draft makes termination of the mechanism the end of the pass
  (C-15). No code of the pass runs at that instant. The bootstrap's own X-3
  finalization exists only on the orderly path.
* **GB-3, disabling takes time after its trigger.** A grant stops being usable
  only after a root process unlinks the rule **and** polkitd reloads its rules,
  which PO-11 (d) bounds but which takes longer than zero. `ExecStopPost=` and
  every other systemd trigger start after the main process ends (PO-21 (c)).

**Argument.** Take a pass that ends at an instant `t_e` in ST-3. By GB-1 the
grant is live at `t_e`. By GB-2, `t_e` can be any instant, and nothing can act
before it. By GB-3, any disabling that the end itself triggers takes effect at
some `t_e + δ` with `δ > 0`. The grant is therefore live in `[t_e, t_e + δ)`,
after the pass. Any trigger has the same result: D3-R2's polling, an
`ExecStopPost=` on the capture unit, `OnSuccess=`/`OnFailure=`,
`PropagatesStopTo=`, or a D-Bus subscription. Triggering by event instead of by
polling shortens `δ`, but it cannot remove the reload or make `δ` zero.

**Consequence.** A zero interval needs all three of the following:

* **Z-1.** No grant is live at any instant at which the pass can end. So there
  is no `stop` grant, and the `start` grant is disabled before the pass's
  image runs.
* **Z-2.** That disabling is a root act that PID 1 orders **between** the
  Polkit decision on the `start` and the `execve` of `ExecStart=`. It must end
  with PK *not authorized* before `ExecStart=` runs.
* **Z-3.** If the disabling fails, `ExecStart=` never runs.

Z-2 needs a root step inside the capture unit's own start, because:

* drop-ins are excluded (`DropInPaths` empty, U-7, HF-13);
* `set-property` is excluded (§4.2.4); and
* a separate unit is ordered into this unit's start only through this unit's
  own dependency lines.

C11's T-B1 requires the LB-2S unit text to have **no** `ExecStartPre=`, and
LB-2S is Peter's conditional M-9 selection (D1-R2). Z-1 removes the
operator's Polkit route for interrupting a hung pass, which is the stated
reason for `stop`. Both are changes to reviewed C11 text and to an
authorization route. Under `.agents/AGENTS.md` ("Stop for maintainer direction
when a decision changes … authorization") and the R3 prompt, the design author
may not make them. The remaining alternative is to measure "after the pass"
at the capture unit's terminal transition instead of at the pass's end. That
reinterprets OH-D-7, which the R2 re-review and the R3 prompt both forbid.

**What the current design therefore establishes.** Under §4.2.5-R2 the capture
unit **is** reported terminal (`inactive` or `failed`) before the grant is
disabled. HL sees the end within Δ, and CL then unlinks the rule and waits for
the reload. **No text of this proposal now claims that no live grant remains
after the pass.** §4.2.5-R2 (g)'s latency paragraph and (n) 3 are withdrawn as
grant-boundary claims, and the boundary stays open until OH-D-10 is decided
and adopted.

##### (c) OH-D-10, the maintainer decision required

**Question.** OH-D-7 requires that no live Polkit grant remains after the
pass. C11's rule keeps a `stop` grant live during the pass, and the LB-2S unit
admits no pre-start step. Which change to C11's reviewed rule and unit text,
and which interruption route, does Peter accept so that OH-D-7 holds
literally?

| Option | What changes | Effect on OH-D-7 | Cost | Recommendation |
|---|---|---|---|---|
| **A, start-consumed grant** | (i) the rule grants `start` only; (ii) the LB-2S unit gains exactly one line, `ExecStartPre=+/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume`, and T-B1 admits exactly that line; (iii) a hung pass is interrupted by **one** of: (iii-a) the executor under A-2, with the literal `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service`, as a §9.5.3 interruption; or (iii-b) no manual interruption, with one further unit line `RuntimeMaxSec=` bounding the pass; and (iv) a start whose consume step fails is not a pass, because no image of the pass runs | **met literally.** The grant is disabled and PK-verified before `ExecStart=`, so no grant exists during or after any pass (d) | changes LB-2S's unit text and C11's rule, and moves interruption from the operator's grant to root (iii-a) or removes it (iii-b). Adds PO-21 (n) … (r) | **recommended**, with (iii-a). (iii-a) keeps a manual interruption and needs no further unit line. Under OH-D-6 it does not widen `ubuntu`'s privilege |
| **B, unit-terminal reading** | the capture unit gains `ExecStopPost=+…rp11_h1.py deact … stop-post` and `TimeoutStopSec=infinity`. Peter decides that "after the pass" is measured when the unit leaves `deactivating` | met only under the new reading. The grant stays live between the entry's end and the end of `stop-post`, and a `start` authorized in that interval can be queued and run after `stop-post` (an uncited systemd behaviour that a PO-21 item would have to settle) | reinterprets an accepted decision; changes the unit text; leaves a usable grant after the entry has ended | **not recommended** |
| **C, no Polkit grant** | the rule is never activated. The executor starts the pass as root under A-2 (`sudo -n /usr/bin/systemctl start --wait rp11-capture-pass-a.service`) | met trivially: no grant ever exists | reopens C11's issue model: the operator's own reviewed `systemctl start` (§4.7.1 D-1 "Issue"), the client-hook path TR-2 and S-8's requester. It is a C-11 decision, not an activation one | **not recommended** for this remediation |

Under every option, M-B, M-S, CL, GP-R3, attestation and RB-1 stay as they
are. **Smallest safe successor:** Peter decides OH-D-10, and one narrow
repository-only remediation, R4, adopts the chosen option into §4.2.5-R2, the
§4.7.2 dispositions and PO-21 for independent Codex re-review. No host step,
H-0 or implementation precedes that.

##### (d) Option A, specified for decision (not adopted)

The following is the mechanical content that R4 would adopt under OH-D-10 (A)
with (iii-a). It answers each point of the R3 prompt. **Nothing in (d) is in
force.**

*(D3-R4.)* (d) is adopted by §4.2.5-R4, which governs where the two differ.
The differences are: CP's lock is taken once, non-blocking, before any check
(AR-1), so the steps are renumbered: (d)'s CP-0 checks move under the lock
into R4's CP-2, R4's CP-0 only reads the identifier, and (d)'s CP-1 … CP-6
become R4's CP-1 and CP-3 … CP-7; CP also checks that the
activation is still live (AR-3); the timeout row for (iii-b) is dropped; and
the start timeout is checked at AP-0 (AR-4).

**Unit and rule deltas.** The unit is C11 §4.4.3.4's text with `User=ubuntu`,
plus exactly one line placed after `ExecStart=`:

```ini
ExecStartPre=+/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume
```

The rule is C11's text with the clause `|| action.lookup("verb") == "stop"`
removed. `ExecStart=`, `User=`, `NoNewPrivileges=yes`, the absence of every
environment and PAM directive, and `rp11-launch` are unchanged. The `consume`
step takes no operand. It reads the activation identifier from the root-owned
`pass-a.json`, so the unit bytes are fixed at H-1 and are the same for every
activation.

**Procedure CP (consume).** CP runs as root, with PID 1's environment, as the
capture unit's `ExecStartPre=+`, inside that unit's start job, after Polkit has
authorized the `start` and before PID 1 executes `ExecStart=` (PO-21 (o), (p)).

| Step | Action | On failure |
|---|---|---|
| CP-0 | open `/run/freedom-blades-rp11/pass-a.json` through a descriptor (`O_NOFOLLOW`); it must be A1-intact against the identity line in `/var/tmp/⟨activation_id⟩-act-evidence/journal`, where `⟨activation_id⟩` is the document's field. The `act` record must be `activated`. The `boot_id` must equal the `ACT` journal's | exit non-zero |
| CP-1 | take the `ACT`-directory lock as CL-0 does, retrying for at most S seconds. Under Option A the holder **releases** that lock when it appends `hold-start`; D3-R2's AM-0 kept it until exit | exit non-zero |
| CP-2 | **one-shot:** if `/var/tmp/⟨activation_id⟩-consume-evidence` exists, exit non-zero. A second start of this activation, by `ubuntu` or by root, never runs the pass | exit non-zero |
| CP-3 | create that directory exclusively (root, `0755`), its journal, and `run-start {invocation_id, boot_id}`. If it cannot, run CP-4 and CP-5 **without** journal lines (grant priority), and exit non-zero | grant priority, then exit non-zero |
| CP-4 | the rule: A1-intact against the `ACT` journal, removed by G-R1 (descriptor re-verification, `remove-intent`, `unlinkat`, directory `fsync`, `removed`) | exit non-zero |
| CP-5 | PK must return *not authorized* within the PO-11 (d) bound. Append `grant-check`, then `consumed {pk_status}`, then `fsync` | exit non-zero |
| CP-6 | exit `0`. Only now does PID 1 execute `ExecStart=` | — |

**Each terminal cause, with Option A in force.**

| Cause | When the grant was disabled | Grant at the pass's terminal instant |
|---|---|---|
| normal exit (X-3 reached) | CP-5, before `ExecStart=` | none |
| early failure (`rp11-launch` or bootstrap refusal before X-1) | CP-5, before `ExecStart=` | none |
| signal death, crash or OOM kill of the entry | CP-5, before `ExecStart=` | none |
| timeout (the pass bound `RuntimeMaxSec=` under (iii-b)) | CP-5 | none |
| operator interruption, (iii-a) root `stop` under A-2 | CP-5 | none. The interruption needs no grant |
| CP fails, is killed or times out (`TimeoutStartSec=`) | not, or not verifiably | **no pass ran.** `ExecStart=` never executed (PO-21 (o)). The grant is a pre-pass grant of the activation, and CL removes it when the activation ends: at W, on the holder's end, or by the backstop (§4.2.5-R2) |

**Unit relationship and ordering.** PID 1 owns the capture unit's terminal
transition. CP runs inside that unit's start job (`activating`, sub-state
`start-pre`). The holder `⟨activation_id⟩.service` and the backstop units stay
separate transient units, with **no** `Requires=`, `BindsTo=`, `After=` or
`PropagatesStopTo=` between them and the capture unit. Neither can start the
capture unit. The only ordering relied on is PID 1's own ordering within one
unit: every `ExecStartPre=` exits successfully before `ExecStart=` (PO-21 (o)),
and the Polkit decision is made before the job is enqueued (PO-21 (p)).

**Can the capture unit be reported terminal before the grant is disabled?**
For a pass, no. `ExecStart=` is not executed until CP-5 has recorded *not
authorized*, so the unit cannot reach a terminal state of a pass while the
grant is live. For a failed start, the unit reports `failed` with the grant
possibly live, but under (iv) no pass has run.

**Owners.** CP is not a cleanup owner. It is part of the start, runs at most
once per activation (CP-2), and removes only the rule. CL stays the **single**
cleanup owner for `pass-a.json`, the directories and the records, through its
three triggers `stop-post`, `backstop` and `attest`. CP and every CL trigger
serialize on the same `ACT`-directory lock, so no two of them act at the same
time. After a successful CP, CL classes the rule `removed-earlier` from CP's
`removed` line. HL and the backstop stay recovery mechanisms. **Neither is
relied on for the grant boundary.**

**The terminal transition and its evidence.** The pass is terminal when the
capture unit's main process ends, for any cause. The proof that the grant was
already absent at that instant is:

* CP's durable `removed`, `grant-check` (*not authorized*) and `consumed`
  lines, written before CP exits `0`;
* PID 1's ordering of `ExecStart=` after that exit (PO-21 (o)); and
* the `INVOCATION_ID` that CP records and that the entry records in its
  genesis state, which ties both to the same start.

The `deact` record would gain a key `consume`, holding
`{journal: {path, sha256, length}, invocation_id, pk_status}` or `"absent"`.

**PO-21 additions under Option A** (for the HF-07 systemd version; each with
its H-0 fact):

* (n) an `ExecStartPre=` line prefixed `+` runs as root with full privileges,
  unaffected by `User=` and `NoNewPrivileges=`, with PID 1's environment and
  nothing from the requester (HF-05, HF-07);
* (o) `ExecStart=` is executed only after every `ExecStartPre=` has exited
  successfully. A non-zero exit, a signal or a `TimeoutStartSec=` expiry of an
  `ExecStartPre=` leaves `ExecStart=` unexecuted and the unit `failed`;
* (p) Polkit authorizes `StartUnit` once, before the job is enqueued. Removing
  the rule afterwards does not cancel that job, and no other Polkit decision is
  consulted for the job's `ExecStartPre=` or `ExecStart=`;
* (q) `systemctl start --wait` needs no Polkit action after `StartUnit` itself;
  and
* (r) the `TimeoutStartSec=` that applies (the manager's default unless the
  unit sets one) is recorded in the H-1 `baseline` (HF-16, §4.3.3).

PO-11 would gain **(g)**: with the rule granting `start` only, a `stop` request
by `ubuntu` is not authorized without authentication (HF-12).

**What Option A would not change.** LB-2S's two prevention claims (no
client-derived process state reaches the entry; the entry's environment is
the literal) are about `ExecStart=`'s process, and CP is a separate process
that PID 1 creates before it (PO-14 is unaffected). U-7's `baseline` simply
gains the `ExecStartPre` property. A root start in ST-1 runs CP, which finds no
`pass-a.json` and exits non-zero, so the pass image never runs. That is a
stronger refusal than the bootstrap's.

##### (e) GP-R3, complete grant-priority cleanup (adopted; `OH-H1-D3-R2-2`)

GP-R3 replaces D3-R2's GP item 3 and its last two sentences. Its principle is
that **a failure to write evidence reduces what the attempt can claim. It never
causes an attributable activation object to be kept.**

**Entry.** An attempt enters GP-R3 when, after CL-0's lock is held:

* E-a: the attempt directory or its journal cannot be created (CL-0);
* E-b: a journal append or `fsync` fails before the rule's removal is
  durable; or
* E-c: a journal append or `fsync` fails after that, at any point up to CL-6.

A record that cannot be published at CL-7 is not GP-R3. Its removals are
already journaled, and it stays D3-R1's `record-unpublished`.

The lock does not depend on writable evidence: it is `flock` on a directory
opened `O_RDONLY` (PO-20 (f)). If the `ACT` evidence directory cannot even be
opened, its journal cannot be read either. Every object is then A0, and nothing
is removed.

| Step | Action | On failure |
|---|---|---|
| GP-1 | CL-1 read-only: parse the `ACT` journal and every earlier attempt journal; apply boot scoping. A missing or invalid `ACT` journal makes every object A0 | nothing is removed; HARD STOP |
| GP-2 | **the rule.** If it is A1-intact, re-verify it through a descriptor **immediately before** removal: `openat(…, O_RDONLY\|O_NOFOLLOW)`, `fstat` for type, `(dev, ino)`, uid and gid 0, mode `0644` and `st_nlink = 1`, a full re-hash equal to the staged digest, and no forbidden extended-attribute name. Then `unlinkat`. A write-ahead line is written only if the journal still accepts it | `unlinkat` error: class `grant-unremovable`, with the `errno`. Re-verification mismatch: the object is A1-damaged or A0 now, and it is kept. `ENOENT` at `unlinkat` (a concurrent removal): absent. In every case GP-3 follows |
| GP-3 | **grant post-check** (CL-4): `ENOENT` at the path, and PK within the PO-11 (d) bound. The result is held in memory | — |
| GP-4 | **`pass-a.json`**, always attempted after GP-3, as CL-5 is. If A1-intact against its identity line and A-2's digest, re-verify through a descriptor immediately before removal (type, `(dev, ino)`, owner, mode `0644`, `st_nlink = 1`, size, full re-hash), then `unlinkat` | `unlinkat` error: class `unremovable`, with the `errno`. Mismatch: kept. `ENOENT`: absent |
| GP-5 | **directories** (CL-5b): first tree **P**'s top, then, bottom-up, each directory of tree **R** that `ACT` created. Each must be A1-intact (type, `(dev, ino)`, uid and gid 0, mode) and, through an `O_DIRECTORY\|O_NOFOLLOW` descriptor, empty, immediately before `unlinkat(…, AT_REMOVEDIR)`. A pre-existing `/run/polkit-1/rules.d` and every S0 name are never removed | `ENOTEMPTY`, a mismatch or another error: kept, with its class |
| GP-6 | CL-6, read-only | — |
| GP-7 | one fixed diagnostic line on standard error, which goes to the system journal: `rp11-cl grant-priority ⟨activation_id⟩ rule=⟨class⟩ pk=⟨status⟩ pass_config=⟨class⟩ dirs=⟨class,…⟩`. It is **diagnostic only** and never evidence, because the journal may share the failed storage. Then exit non-zero | — |

**Repeated and concurrent attempts.** Every trigger takes the same
`ACT`-directory lock first, so `stop-post`, `backstop` and `attest` attempts run
one at a time, under GP-R3 or not. The kernel releases the lock when a process
dies (PO-20 (f)), so a killed GP-R3 attempt never blocks the next one. A
repeated GP-R3 attempt finds the objects it removed absent and acts on nothing.
GP-R3 consumes no attempt number `k`, so BS-4's limit of 99 does not stop the
backstop while the evidence stays unwritable. Each later firing runs GP-1 …
GP-7 again. They are read-only once nothing attributable is left.

**What can and cannot be claimed without a durable removal record.**

* A GP-R3 attempt writes **no record**, so it claims nothing durable. Its
  outcome is HARD STOP `evidence-unwritable`, reported only by the diagnostic
  line and the unit's exit status.
* A later journaled attempt (BS-4 or `attest`) finds each object that GP-R3
  removed **absent**. Its identity line is in the `ACT` journal, and no
  durable `removed` line exists. It classes the object `absent-before-removal`
  (D3-R1). For the rule, that class counts towards `st1-verified` only with
  that attempt's own PK *not authorized* and CL-6. The record never says
  `removed`, `removed-verified` or `removed-earlier` for such an object, and it
  never names who removed it or when.
* In a later boot the class is `cleared-by-boot`. That class asserts only its
  four conditions: a different `boot_id`, `tmpfs`, an identity line and
  `ENOENT`. It does **not** assert that the object still existed when the boot
  happened.

**Removed without a record, or foreign or damaged?** A later attempt never
needs to delete anything to tell these apart:

* **removed without a record:** nothing is at the path. The class is
  `absent-before-removal` (or `cleared-by-boot`), and there is nothing to act on;
* **still A1-intact:** GP-R3 could not remove it. The later attempt removes it
  under G-R1, with its own write-ahead lines;
* **A1-damaged:** type and `(dev, ino)` match, another attribute differs. Kept
  and escalated; and
* **A0:** no identity match. This includes any object that appeared at the
  path after GP-R3's removal. Kept and escalated.

If a later foreign object reuses a freed `tmpfs` inode number, it is still
removed only if it also matches the recorded type, owner, mode, size, link
count **and** SHA-256. It is then byte-identical to what `ACT` published there,
which is P-1's item 3.

**Result.** If GP-2 … GP-5 remove, or find absent, every A1 object and no
residual exists, the host is in **ST-1.ur**: cleared, with the grant post-check
held only in memory and no terminal record. Otherwise the residual stays for
the next journaled attempt, which records it as ST-1+R. In both cases the
attempt's own outcome is HARD STOP `evidence-unwritable`, without a record.

**ST-1 and ST-1+R mapping.**

| GP-R3 found | Host state | Recorded later as |
|---|---|---|
| every activation object removed or absent; PK *not authorized* | **ST-1.ur** | **ST-1** (`st1-verified`), when the first later journaled attempt obtains its own PK *not authorized* and CL-6. In a later boot, attestation records `cleared-by-boot` |
| every object removed or absent; PK still *authorized* or erroring | ST-1.ur, grant `removed-unconfirmed` | ST-1 if that later attempt's PK is *not authorized*. Otherwise ST-1+R (`removed-unconfirmed`), and BS-4 retries |
| the rule `grant-unremovable` | a residual with the grant live; no record yet | ST-1+R (`grant-unremovable`). BS-4 retries every R, and a kernel boot removes it |
| `pass-a.json` or a directory `unremovable`, damaged or foreign | residual | ST-1+R with that residual; A0 and A1-damaged objects are escalated |

Until that later record exists, **every later RP-11 step refuses**: H-2, AP-0,
H-1R and RB-1 each require a terminal `deact` record (§4.2.5-R2 (i)).

**Why this does not weaken D3-R1.** D3-R1's write-ahead invariant W and its
"stop at once" journal rule govern **publication** (H-1 and `ACT`). GP-R3
publishes nothing. For a removal, safety comes from G-R1's identity check
against the `ACT` journal and its descriptor re-verification, and P-1 rests on
those alone. The removing attempt's own `remove-intent` and `removed` lines are
evidence of the removal, not the guard on it. GP-R3 is limited to CL's
activation objects. RB-1 and every H-1 object keep strict write-ahead removal.

##### (f) States (amends §4.2.5-R2 (j))

| State | Activation objects present | Grant? | Entered by | Left by |
|---|---|---|---|---|
| **ST-1.d1** *(amended)* | rule removed; `pass-a.json` or tree **P**'s top remains | no | an attempt that stopped after CL-3 or GP-2 | the same attempt continuing (CL-5, or GP-4 under GP-R3); else BS-4 within R; else the next kernel boot |
| **ST-1.ur** *(new)* | none attributable; no terminal `deact` record | no rule at the path. PK's result is as GP-3 observed it, normally *not authorized*, possibly `removed-unconfirmed`. That observation is not durable | a GP-R3 attempt that removed or found absent every A1 object | the first later journaled attempt (BS-4 within R, or `attest`), which records `st1-verified` or ST-1+R. Every later RP-11 step refuses until then |

##### (g) Evidence-failure rows (added to §4.2.5-R2 (k))

| Event during CL | Result |
|---|---|
| attempt directory or journal cannot be created (E-a) | GP-R3. The rule first (GP-2, GP-3), then `pass-a.json` (GP-4), then the directories (GP-5). ST-1.ur, or a residual |
| journal append or `fsync` fails before the rule's removal is durable (E-b) | GP-R3 from GP-2 |
| journal append or `fsync` fails after the rule's removal (E-c) | GP-R3 from the next step not yet done. The journaled lines stand as evidence |
| record publication fails at CL-7 | `record-unpublished` (D3-R1). The removals are durable, and the next attempt records |
| `unlinkat` fails | `grant-unremovable` or `unremovable`. BS-4 retries, and a kernel boot clears `/run` |
| descriptor re-verification fails | the object is kept and classed A1-damaged or A0 |
| a second trigger fires during an attempt | it waits on the lock for at most S seconds, then `lock-timeout`. It acts on nothing |
| a GP-R3 attempt dies (EC) | the lock is released. BS-4 runs GP-R3 or CL again within R |
| an unclean kernel boot during GP-R3 (EU) | M-B clears `/run`, and attestation records `cleared-by-boot` |

##### (h) Record and journal amendments (to `rp11-activation-record/2`)

* `pass_config.class` gains `unremovable`.
* A new key, `directories`, lists `{path, class, identity: {dev, ino} or
  "absent"}` for tree **P**'s top and every tree **R** directory. The classes
  are `removed`, `never-created`, `removed-earlier`, `absent-before-removal`,
  `cleared-by-boot`, `pre-existing-kept`, `present-nonempty-unremoved`,
  `present-damaged-unremoved`, `present-foreign-unremoved` and `unremovable`.
  `st1-verified` admits only the first six.
* `evidence_mode`: a record is published only by a journaled attempt, so its
  value is always `"journaled"`. D3-R2's value `"grant-priority"` is
  withdrawn.
* `evidence-unwritable` stays a failure class of the **attempt**. It appears
  only in GP-7's diagnostic line, never in a record.
* The closed `op` sets of §4.2.5-R2 (m) are unchanged.

##### (i) Proof amendments

1. **No unrelated object is removed by GP-R3.** Each removal requires
   A1-intact against the `ACT` journal **and** a descriptor re-verification
   immediately before it. That is P-1's items 2 … 5, which do not use the
   removing attempt's own journal. The stated limit of G-R1 (only root can
   swap a name in a root-only directory, which is T-B) is unchanged.
2. **No attributable activation object is kept because evidence failed.** E-a,
   E-b and E-c each lead into GP-2 … GP-5, not to a stop. An A1-intact object
   is kept only when its `unlinkat` fails or its re-verification fails, never
   because a line could not be written.
3. **Success is never claimed without durable evidence.** GP-R3 writes no
   record. `st1-verified` is recorded only by a journaled attempt, with its own
   PK *not authorized* and CL-6. Objects that GP-R3 removed are recorded only
   as `absent-before-removal` or `cleared-by-boot`.
4. **The order holds.** The rule (GP-2) and its post-check (GP-3) come before
   `pass-a.json` (GP-4), and that comes before the directories (GP-5), exactly
   as in CL.
5. **§4.2.5-R2 (n) 3 stays open.** It is the subject of OH-D-10.

##### (j) What remains, stated exactly

* **`OH-H1-D3-R2-1`** is open and blocked on OH-D-10. Until R4 adopts a
  decided option, the grant stays live after the pass for the interval of (b).
  *(D3-R4: superseded. R4 adopts Option A, and §4.2.5-R4 (i) removes that
  interval. The finding stays open until Codex re-reviews it.)*
* **Unwritable evidence for the rest of the boot.** ST-1.ur then persists
  unrecorded. Nothing attributable is left, and every later RP-11 step refuses.
  After the next kernel boot, attestation records `cleared-by-boot`.
* **`grant-unremovable` together with unwritable evidence.** The rule then
  stays live, as GU in §4.2.5-R2 (l). BS-4 retries every R, and the kernel boot
  removes it. No T-A cause of a root `unlinkat` failure on `tmpfs` is known.

#### 4.2.5-R4 Start-consumed grant, adopted under OH-D-10 (A) with interruption route (iii-a) *(D3-R4)*

> **D3-R4 text, kept as history; amended by D3-R5 (§4.2.5-R5).** Superseded:
> in (b), the sentences that "CP-3" refuses a pre-existing name and that
> "CP-2" refuses a planted `deact` name (now CQ-2 and CQ-4); the whole of (c)'s
> step order (replaced by CQ-0 … CQ-7) and its `run-start` fields; in (d), the
> last row; in (e), "When" (`activating` is withdrawn, OS-6) and "What
> follows"; in (f), the `start-failed-before-exec` and `pass-failed-early`
> conditions; in (g), the (j) ST-2.c and ST-2.f rows, the (k) ST-2.c row, and
> the (m) `consume` key; in (i), item 7; and in (k), CX-1 and CX-2. **Not
> superseded:** (a), the unit and rule of (b), (h), (i) items 1 … 6, (j) and
> CX-3. *(D3-R5)* markers below show each place.
>
> **Also amended by D3-R6 (§4.2.5-R6), on Peter Duscha's OS-6 decision.** In
> (d), the route (iii-a) row and the words "including by a route (iii-a)
> `stop` during `start-pre`" of the last row; in (e), "When" (the decided
> condition replaces `activating` or `active`) and the last sentence of "What
> it is"; in (g), A-2's pinned consume sentence and, in (j), the words "or a
> `stop` during `start-pre`" of the ST-2.f row. *(D3-R6)* markers below show
> each place.

This subsection adopts Peter Duscha's OH-D-10 decision
([R4 authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4-authority.md)):
**Option A with interruption route (iii-a)**. It addresses Blocking finding
`OH-H1-D3-R2-1` in design. It does **not** declare that finding closed, and
`OH-H1-D3-R1-1` and `OH-H1-D3-2` also stay open. It is **proposed** and
inactive. Where it differs from §4.2.5-R3 (d), this subsection governs.

##### (a) What D3-R4 adopts, refines and leaves unchanged

* **Decided** (quoted from the R4 authority): *"The inactive H-1 design must
  grant the unprivileged operator only `start`. The capture unit must consume
  that grant through the fixed root `ExecStartPre=` step specified in D3-R3
  and must obtain the PK not-authorized post-check before `ExecStart=` may
  run. A failed consume step is a failed start, not a pass. Manual
  interruption remains available only through the executor's A-2-authorized
  root `systemctl stop` route."*
* **Adopted from §4.2.5-R3 (d):** the unit and rule deltas, procedure CP, the
  terminal-cause table without its (iii-b) row, the unit relationship and
  ordering, the owners paragraph, the terminal evidence, the `consume` key,
  PO-21 (n) … (r) and PO-11 (g).
* **Not adopted:** route (iii-b). The capture unit gains no `RuntimeMaxSec=`
  line. Options B and C are not adopted.
* **Refinements.** Adopting (d) exposed eight points that it left
  under-specified. Each refinement below closes one of them. None widens
  authority, and each one fails closed.

  | # | Point in §4.2.5-R3 (d) | D3-R4 refinement | Where |
  |---|---|---|---|
  | AR-1 | CP-0 validated `pass-a.json` **before** CP-1 took the lock, so cleanup could change the object between the check and the act. CP-1 retried for up to S seconds, which could exceed the start timeout | CP takes the `ACT`-directory lock **once, non-blocking**, before any validation, and validates everything under the lock. Under D3-R4 no step holds that lock during ST-2 (AR-2), so contention means cleanup has begun, and the start fails | (c) CP-1 |
  | AR-2 | the holder "releases the lock at `hold-start`", but §4.2.5-R2 (d) AM-0 still kept it until exit | AM-0 is amended. The holder releases the lock immediately after appending `hold-start`. A-2 permits the start only after `hold-start` | (g) |
  | AR-3 | CP did not check that the activation was still live | CP requires `hold-start` and no `hold-end` in the `ACT` journal, no `deact` evidence directory or record for the activation, and the capture root absent | (c) CP-2 |
  | AR-4 | the unit's start timeout was only recorded (PO-21 (r)) | AP-0 requires the recorded start timeout to be finite and at least the PO-11 (d) bound plus 30 seconds. Otherwise `ACT` is INVALID RUN | (g); §4.3.3 |
  | AR-5 | a `+` command's handling of `UMask=` and the other execution settings was not stated | CP sets every mode explicitly by `fchmod` and relies on no inherited execution setting except journal output. PO-21 (n) states which settings still apply | (c); (j) |
  | AR-6 | the `INVOCATION_ID` tie between CP and the entry assumed both see the same value | PO-21 (n) also states that the `ExecStartPre=` process receives the same `INVOCATION_ID` as the `ExecStart=` process of the same start | (j) |
  | AR-7 | PO-11 (g) had no corroboration at activation | AV-1 adds a negative control: PK with verb `stop` must return *not authorized* while the rule is live. It corroborates PO-11 (g) on the host. It does not replace the citation | (g) |
  | AR-8 | HL classed a failed consume as `pass-failed-early`, which named a pass that never ran | HL's reason is `start-failed-before-exec` when the consume journal has no `consumed` line | (f) |

* **Unchanged:** OH-D-1 … OH-D-9; PF, PT, the journal format, RS-1, G-R1, P-1,
  P-2 and RB-1, which stays separately authorized and never automatic; M-B
  (the `/run` placement, cleared by every kernel boot); M-S (the holder,
  `ExecStopPost=` and the backstop); CL and its automatic triggers; GP-R3 and
  ST-1.ur (§4.2.5-R3 (e) … (i)); attestation; PK; the attribution classes; and
  every earlier proof obligation.

##### (b) The unit and the rule, in full

**The unit** is C11 §4.4.3.4's text with `User=ubuntu` (§4.7.2) and exactly
one added line, placed after `ExecStart=` as §4.2.5-R3 (d) specified:

```ini
[Unit]
Description=Freedom Blades RP-11 capture entry, Pass A (reviewed bytes; installed only under authorization)

[Service]
Type=exec
User=ubuntu
ExecStart=/usr/local/libexec/freedom-blades-rp11/rp11-launch --pass A
ExecStartPre=+/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume
WorkingDirectory=/
UMask=0077
StandardInput=null
StandardOutput=journal
StandardError=journal
NoNewPrivileges=yes
```

PID 1 runs `ExecStartPre=` before `ExecStart=` whatever the lines' order in
the file. That order is PO-21 (o), and it does not depend on where the line
is placed. The added line contains no `%`, `$`, `\` or quotation mark, so
systemd's specifier and variable expansion cannot change it (the PO-21 (b)
grammar). Its argument vector is fixed. Its program and script are
root-owned files of tree **L**, bound by the H-1 record. The unit still has
no `Environment=`, `EnvironmentFile=`, `PassEnvironment=`,
`UnsetEnvironment=`, `PAMName=`, `ExecStartPost=`, `ExecStop=`,
`ExecStopPost=`, `ExecCondition=`, `RuntimeMaxSec=`, `TimeoutStartSec=`,
credential import, `[Install]` section or template instance.

**T-B1, amended.** The unit-text test admits exactly the key set above and
exactly this one `ExecStartPre=` value, byte for byte. Any other
`ExecStartPre=` value, a second `ExecStartPre=` line or any directive listed
as absent fails. The docstring still states that this is a property of the
text, not of the loaded configuration (S-5). §4.3.3 checks the loaded
configuration.

**The rule** is C11's text with `subject.user == "ubuntu"` and with the verb
test narrowed to `start`:

```js
polkit.addRule(function (action, subject) {
  if (action.id == "org.freedesktop.systemd1.manage-units" &&
      action.lookup("unit") == "rp11-capture-pass-a.service" &&
      action.lookup("verb") == "start" &&
      subject.user == "ubuntu") {
    return polkit.Result.YES;
  }
});
```

**T-B2, amended.** The rule-text test requires one action identifier, one
unit, the verb `start` only, and one subject user.

C11's reason for `stop` ("so that the operator can interrupt a hung pass") is
withdrawn. Interruption is route (iii-a), in (e).

**No requester-controlled input decides the grant boundary.**

* **Operand and environment.** `StartUnit` carries only the unit name and the
  job mode (S-8). CP's argument vector is the literal above. Its environment
  is PID 1's (PO-21 (n)). Nothing from `ubuntu`'s client reaches CP.
* **Files CP reads.** These are `pass-a.json` on `/run` (root-owned), the
  `act` record (`root:root`, `0444`), the H-1 record and the `ACT` journal.
  The `ACT` journal is `root:root` `0644`, but its directory is
  `ubuntu`-owned (§4.2.5-R2 (b)), so `ubuntu` can replace the journal or the
  directory. A replaced journal can only make CP refuse, or make CP remove
  the real rule. CP removes nothing except the one object at the fixed rule
  path, and only after a descriptor re-verification against the staged
  digest. That digest comes from the root-owned H-1 record, not from the
  journal. Whatever the journal says, `ExecStart=` runs only after CP-6 has
  obtained PK *not authorized* as root.
* **`/var/tmp`.** It is world-writable with the sticky bit set. A
  pre-existing `⟨activation_id⟩-consume-evidence` name, whether a directory, a
  file or a symbolic link, makes CP-3 refuse. A planted
  `⟨activation_id⟩-deact-*` name makes CP-2 refuse. CP creates its directory with
  `mkdirat`, which never follows a final symbolic link, and its journal with
  `O_CREAT|O_EXCL|O_NOFOLLOW` relative to that directory's descriptor. The
  worst outcome is a refused start, with no pass. Under OH-D-6 that is no
  more than `ubuntu` can already do.

##### (c) Procedure CP (consume), as adopted

CP runs as root, as the capture unit's `ExecStartPre=+`, inside that unit's
start job. It runs after Polkit has authorized the `start` and before PID 1
executes `ExecStart=` (PO-21 (o), (p)). CP is part of the start. It is not a
cleanup owner, and it removes only the rule. Every exit other than CP-7's is
non-zero, and `ExecStart=` is then never executed (PO-21 (o)).

| Step | Action | On failure |
|---|---|---|
| CP-0 | open `/run/freedom-blades-rp11/pass-a.json` through a descriptor (`O_RDONLY\|O_NOFOLLOW`) and parse **only** `activation_id`, which must match the §4.2.5-R1 (a) grammar. Nothing is decided yet | exit non-zero (`consume-no-activation`). This is the ST-1 case: a root start finds no `pass-a.json`, and the image of the pass never runs |
| CP-1 | open `/var/tmp/⟨activation_id⟩-act-evidence/` with `O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW` and take `flock(LOCK_EX\|LOCK_NB)` **once**. *(AR-1)* | `EWOULDBLOCK`: exit non-zero (`consume-busy`). Cleanup, or another CP, holds the lock. Nothing is touched |
| CP-2 | **under the lock**, verify all of the following. `pass-a.json` is still at its path with the descriptor's `(dev, ino)`, A1-intact against its identity line in the `ACT` journal and equal to `run-start.pass_config_sha256`. The current `boot_id` equals the `ACT` journal's. `⟨activation_id⟩.act.json` exists, is `root:root` `0444` and has `outcome: "activated"`. The `ACT` journal has `hold-start` and no `hold-end`. No `⟨activation_id⟩-deact-*` evidence directory and no `deact` record exists. The capture root that `pass-a.json` names is absent (`lstat`). *(AR-3)* The `ACT` journal is parsed under the existing rules, and a torn tail, which the holder's unlocked appends can leave, is ignored | exit non-zero (`consume-precondition`). Nothing is touched |
| CP-3 | **one-shot:** if `/var/tmp/⟨activation_id⟩-consume-evidence` exists, as any type, exit. A second start of this activation, by `ubuntu` or by root, never runs the pass | exit non-zero (`consume-repeated`). Nothing is touched |
| CP-4 | create `/var/tmp/⟨activation_id⟩-consume-evidence/` with `mkdirat`, then `fchown` `root:root` and `fchmod` `0755`. Create `journal` in it (`O_CREAT\|O_EXCL\|O_NOFOLLOW`, then `fchmod` `0644`) and append `run-start {invocation_id, boot_id, act_journal: {sha256, length}}`, then `fsync` the journal and the directory. `invocation_id` is the `INVOCATION_ID` of CP's environment (PO-21 (n)). *(AR-5)* | **grant priority:** if the directory or the journal cannot be created, or a line cannot be made durable, run CP-5 and CP-6 **without** journal lines, then exit non-zero (`consume-evidence-unwritable`). No pass runs |
| CP-5 | **the rule.** Classify the object at `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules` against the `ACT` journal's identity line. It must be A1-intact, with the digest equal to the H-1 record's staged-rule digest (`baseline.files[staged rule].sha256`, which A-2 pins as `staged_rule_sha256`). Remove it by G-R1: a descriptor re-verification immediately before removal (type, `(dev, ino)`, uid and gid 0, mode `0644`, `st_nlink = 1`, a full re-hash and no forbidden extended-attribute name); then `remove-intent {path, dev, ino, sha256}`, `fsync`, `unlinkat`, `fsync` of the rules directory, `removed {path}` and `fsync` | absent, A1-damaged, A0 or a re-verification mismatch: `consume-failed {step, class}`, then exit non-zero. `unlinkat` error: `remove-failed {errno}`, then exit non-zero. In each case the object is left as it is, for CL |
| CP-6 | **post-check.** `ENOENT` at the path, then PK (§4.2.5-R1 (f), verb `start`). PK must return *not authorized* within the PO-11 (d) bound. Append `grant-check {status}`, then `consumed {pk_status}`, then `fsync` | PK *authorized* or an error after the bound: `consume-failed {step: "CP-6", class: "removed-unconfirmed"}`, then exit non-zero |
| CP-7 | append `run-end`, `fsync`, release the lock and exit `0`. Only now does PID 1 execute `ExecStart=` | — |

The lock is released by the kernel at every exit, including a kill
(PO-20 (f)). The stable codes in parentheses go to standard error, and so to
the system journal, as one fixed line without values. They are diagnostic
only. The durable evidence is the consume journal.

**The consume journal's closed `op` set** is `run-start`, `remove-intent`,
`removed`, `remove-failed`, `grant-check`, `consumed`, `consume-failed` and
`run-end`. Its format is the journal format of §4.2.4-R1 (b). CP writes no
record file. Its journal is retained evidence, listed with its digest and
length in every later `deact` record ((g)).

*(D3-R5.)* This step order is **superseded** (`OH-H1-D3-R4-1`). CP-3 tested a
name that only CP-4 created, so CP-0, CP-1 and CP-2 could fail with no barrier.
§4.2.5-R5 (e) gives the governing order CQ-0 … CQ-7 and maps each CP-n to it.

##### (d) Each terminal cause

| Cause | When the grant was disabled | Grant at the pass's terminal instant |
|---|---|---|
| normal exit (X-3 reached) | CP-5 and CP-6, before `ExecStart=` | none |
| early failure (`rp11-launch` or bootstrap refusal before X-1) | CP-5 and CP-6, before `ExecStart=` | none |
| signal death, crash or kernel OOM kill of the entry | CP-5 and CP-6, before `ExecStart=` | none |
| the activation's lease L ends while the pass runs (the holder's `RuntimeMaxSec=`) | CP-5 and CP-6. CL then removes `pass-a.json` while the unit is active, and its outcome is HARD STOP `unit-still-active` (§4.2.5-R2 (g)) | none. The pass is not ended by the holder's lease |
| interruption by route (iii-a), the executor's root `stop` under A-2 | CP-5 and CP-6 | none. The interruption needs no grant |
| an orderly reboot or shutdown while the pass runs (PO-21 (h)) | CP-5 and CP-6 | none |
| an unclean kernel boot while the pass runs | CP-5 and CP-6, and M-B clears `/run` | none |
| CP fails, refuses, is killed (including by a route (iii-a) `stop` during `start-pre`) or exceeds the start timeout | not, or not verifiably | **no pass ran.** `ExecStart=` never executed (PO-21 (o)). Any live rule is a pre-pass grant of the activation. HL ends the activation (AR-8), and CL removes the rule first. A second start finds CP-3's directory and refuses (CX-2) |

*(D3-R5.)* The last row's final sentence is **withdrawn**: it was false for
failures before CP-4. §4.2.5-R5 (j) replaces the row. Every later start is
refused by the claim (SB-1) or by PID 1's start history (SB-2), with CX-4 as the
only exception.

*(D3-R6.)* A route (iii-a) `stop` during `start-pre` is no longer possible:
OS-6, decided, makes the route available only on a running pass with a
durable `consumed` line. A `stop` during `start-pre` is a root act outside
A-2. §4.2.5-R6 (g) restates the route (iii-a) row and the last row, and
"CX-4 as the only exception" now reads "without exception within the
authorized path set 𝒜; CX-4 is outside 𝒜".

##### (e) Interruption route (iii-a)

* **Literal.** `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service`.
  It is one fixed command line, with no other operand or option.
* **Who.** Only the executor (U-2), working under this activation's A-2, in an
  interactive session on `oracle-test` as `ubuntu` (OH-D-2), elevating through
  `sudo -n`. The operator has no `stop` route: the rule grants `start` only,
  and PO-11 (g) and AV-1's negative control show that `ubuntu`'s
  unauthenticated `stop` is refused.
* **When.** Only while the capture unit's `ActiveState` is `activating` or
  `active` for this activation's start, and only to end a pass that is hung or
  must stop under the operational draft's §9.5.3. The executor reads
  `systemctl show -p ActiveState,InvocationID rp11-capture-pass-a.service`
  first. The literal is never issued to start, restart or reset the unit, and
  never against any other unit.
* **What it is.** It terminates the capture mechanism, which is a §9.5.3
  interruption. No X-3 finalization attempt follows, and the capture root is
  retained, read-only. If the `stop` lands during `start-pre`, it ends CP and
  no pass runs ((d), last row).
* **What follows.** HL observes the unit's end within Δ (`pass-ended` if the
  capture root exists, otherwise `pass-failed-early` or
  `start-failed-before-exec`). The holder ends, and CL removes `pass-a.json` and
  writes the records. No grant is involved at any point.
* **Privilege.** Under OH-D-6 `ubuntu` already has unrestricted `sudo`, so the
  route adds no privilege. It moves the interruption from a Polkit grant to an
  act under A-2's authority. A-2 pins the literal and its SHA-256 ((g)).

*(D3-R6.)* "When" is **replaced** by Peter Duscha's OS-6 decision: the route
is available only while the unit is `active`, its `InvocationID` equals the
consume journal's `run-start.invocation_id`, and the journal has a durable
`consumed` line. It is unavailable while the unit is `activating`, including
`start-pre`, and a hung consume step ends at the start timeout. The last
sentence of "What it is" no longer describes route (iii-a). The governing
text is §4.2.5-R6 (b). The literal, the executor, A-2's authority and the
§9.5.3 classification are unchanged.

##### (f) Polling and HL: lifetime and recovery only

HL and the backstop establish **no** grant boundary. Under D3-R4 the grant has
been consumed before `ExecStart=`, so nothing that HL observes, or fails to
observe, bears on whether a grant exists during or after the pass. HL stays the
activation's lifetime control. It ends the activation at W, at an observation
failure, after a failed start and after the pass, so that CL removes
`pass-a.json` and writes the records. The backstop stays the retry for a
CL that died.

**HL reason added** *(AR-8)*. The `pass-failed-early` row of §4.2.5-R2 (g) is
split by one read-only check of the consume journal:

| Reason | Condition | Meaning |
|---|---|---|
| `start-failed-before-exec` | `ActiveState` is `failed`, `InvocationID` is non-empty and differs from `i₀`, the capture root is absent, and `/var/tmp/⟨activation_id⟩-consume-evidence/journal` is absent or has no `consumed` line | the start failed in CP or before it. No image of the pass ran |
| `pass-failed-early` | as §4.2.5-R2 (g), and the consume journal has a `consumed` line | the pass started after CP and failed before X-1 (premise P-E) |

HL never treats either as a reason to remove anything itself. CL does that.

##### (g) Amendments to §4.2.5-R2

* **(b) Paths.** One row is added:

  | Object | Path | Owner:group | Mode | Created by | Removed by |
  |---|---|---|---|---|---|
  | consume evidence and journal | `/var/tmp/⟨activation_id⟩-consume-evidence/`, `journal` | `root:root` | `0755`; journal `0644` | CP-4, as root | **retained** |

* **(c) What A-2 pins.** In addition:
  * the interruption literal of (e) and its SHA-256;
  * the sentence: *"The capture unit's consume step is part of its start. It
    is mandatory and automatically authorized under this authority. The only
    interruption route is the executor's root literal pinned here, used only
    under the operational draft's §9.5.3."*; and
  * the unit's recorded start timeout, from the H-1 `baseline`, which must be
    finite and at least ⌈PO-11 (d) bound / 1,000⌉ + 30 seconds *(AR-4)*.
* **(d) `ACT` and hold order.**
  * **AP-0** additionally requires: PO-21 (n) … (r) and PO-11 (g) accepted for
    the observed versions; the start-timeout condition above; and the
    loaded unit's `ExecStartPre` equal to the (b) value under §4.3.3's
    normalization.
  * **AM-0** *(AR-2)*: "keep the lock until the holder exits" is replaced by
    "keep the lock until `hold-start` is durable, then release it".
  * **AV-1** *(AR-7)*: after PK returns *authorized* for verb `start`, PK runs
    once more with `--detail verb stop`. It must return *not authorized*.
    Otherwise `ACT` exits non-zero, and CL runs with the rule first.
  * **HL** appends `hold-start` immediately after AM-3, then releases the
    lock.
  * **(g), correction.** The sentence *"A pass that is still running at L is
    ended by systemd's `RuntimeMaxSec=` (PO-21 (d))"* is corrected.
    `RuntimeMaxSec=` is a property of the holder unit. At L it ends the holder
    and so the activation. It does not end the capture unit, and the pass
    continues without a grant ((d); CX-1, CX-3).
  * The last paragraph of (d) is amended. A-2 permits the operator's `start`
    only while the `act` record exists, the holder's `ActiveState` is
    `active` **and** the `ACT` journal shows `hold-start`.
* **(h) Cleanup CL.**
  * **CL-1** reads `/var/tmp/⟨activation_id⟩-consume-evidence/journal`, if it
    exists, as an earlier attempt's journal for classification. Boot scoping
    applies to it as to every other journal.
  * **CL-3.** If CP's journal has a durable `removed` line for the rule's
    identity, the rule's class is `removed-earlier`. A `remove-intent`
    without `removed`, or a CP grant-priority removal that left no line, gives
    `absent-before-removal`. Each class still needs CL-4's own PK *not
    authorized* for `st1-verified`, as before.
  * CL never runs CP, and CP never removes `pass-a.json`, a directory or a
    record. Both take the same lock, so they never act at the same time.
* **(j) States.** These rows replace the ST-2 and ST-3 rows and add two rows.

  | State | Activation objects present | Grant? | Entered by | Left by |
  |---|---|---|---|---|
  | **ST-2** | tree **P**, the rule and the `act` record `activated`; holder in HL, lock released | **yes, `start` only**, for `ubuntu` | AM-3, then `hold-start` | the operator's `start` (ST-2.c), or HL's end, then CL |
  | **ST-2.c** *(new)* | as ST-2; the capture unit `activating` in `start-pre`, CP running | yes until CP-5's `unlinkat` and the polkitd reload; CP-6 confirms *not authorized* | the `start` that Polkit authorized | CP-7 (ST-3), or a CP failure (ST-2.f) |
  | **ST-2.f** *(new)* | as ST-2, or with the rule already removed by CP; the unit `failed`; no capture root | possibly, as a **pre-pass** grant; no pass has run or can run (CP-3) | a CP failure or a `stop` during `start-pre` | HL's `start-failed-before-exec`, then CL, the rule first |
  | **ST-3** | tree **P**, the `act` record, the consume journal with `consumed`, the running unit and the capture root | **no** | CP-7, then PID 1's `ExecStart=` | the pass's terminal state; HL observes it; CL removes `pass-a.json` and writes the records |

* **(k) Boundaries.** The ST-3 row is replaced, and one row is added:

  | State when the event occurs | ES | EH | EP | EC | EO | EU |
  |---|---|---|---|---|---|---|
  | ST-2.c (CP running) | — | SP waits on the lock for at most S, then CL with the rule first. If CP finished first, the pass may run, and CL ends `unit-still-active` (CX-1) | n/a | BS | the transition stops the start job and CP; no pass | BC |
  | ST-3 | — | SP: the rule is `removed-earlier`; `pass-a.json` is removed while the unit is active, so HARD STOP `unit-still-active`. **No grant** | HL ends within Δ, then SP for `pass-a.json` and the records. **No grant at any instant** | BS | SP: the transition stops the pass and the holder. No grant | BC; the pass is interrupted (§9.5.3), and its capture root is retained |

  With these rows, every cell in which a pass exists has no grant. The other
  rows stand.
* **(m) Records.** `rp11-activation-record/2` gains the key `consume` on
  `deact` records: `{journal: {path, sha256, length}, invocation_id,
  pk_status}`, or `"absent"` if no consume journal exists. The `holder`
  object's `hold_end_reason` admits `start-failed-before-exec`. The `ACT`
  journal's closed `op` set is unchanged, and the consume journal's is in (c).
* **(n) Proof.** Item 3 is **replaced** by (i) below.

*(D3-R6.)* In (c), A-2's pinned consume sentence is replaced by the sentence
of §4.2.5-R6 (g), "A-2", which adds the decided route (iii-a) condition. In
(j), the ST-2.f row's "or a `stop` during `start-pre`" names an act outside
A-2. Route (iii-a) is never issued in ST-2.c (§4.2.5-R6 (g), "States").

##### (h) Baseline amendment (§4.3.3)

* `ExecStartPre` moves from the "each required empty" list to the compared
  list. It must hold exactly one entry, normalized as `ExecStart` is: path
  `/usr/bin/python3.12`; `argv` `["/usr/bin/python3.12", "-I", "-S",
  "/usr/local/libexec/freedom-blades-rp11/rp11_h1.py", "consume"]`; and the
  privileged (`+`) flag as the only flag. The flag appears in the form the
  cited version prints it, including through an `ExecStartPreEx` property if
  that version documents one (PO-15). `ExecStartPost`, `ExecCondition`,
  `ExecStop`, `ExecStopPost` and `ExecReload` stay required empty.
* The unit's start timeout (`TimeoutStartUSec`, or the name the cited version
  uses) is already a compared timeout property. Under PO-21 (r) its value is
  also the one that AP-0 and A-2 check *(AR-4)*.
* H-2, AP-0 and CL-6 compare these as part of `baseline_sha256`, unchanged.

##### (i) Proof: no live grant during or after the pass

The pass is the execution of the `ExecStart=` image of one start of the
capture unit, with its descendants, from that `execve` to the end of the main
process. The operational draft makes the end of the mechanism the end of the pass (C-15). The proof covers every instant from that `execve` onward.

1. **`ExecStart=` follows CP's success.** PID 1 executes `ExecStart=` only
   after every `ExecStartPre=` has exited `0` (PO-21 (o)). CP exits `0` only at
   CP-7.
2. **CP-7 follows a verified removal.** CP reaches CP-7 only after CP-5
   removed the A1-intact rule from `/run/polkit-1/rules.d` with a durable
   `removed` line, and after CP-6 obtained `ENOENT` and PK *not authorized*
   for verb `start` within the PO-11 (d) bound. PK's subject is an `ubuntu`
   process, and the rule tests only `subject.user`, so the decision holds for
   every `ubuntu` process.
3. **No `stop` grant ever exists.** The rule grants `start` only (T-B2;
   PO-11 (g); AV-1's negative control). No other rule grants the action to
   `ubuntu` without authentication (PO-11 (b)). The rule's basename is absent
   from every other rules directory (AP-0).
4. **No grant reappears.** Only AM-2 links the rule, once per activation,
   before AM-3 (§4.2.5-R2 (n) 1). `ACT` never repeats (one identifier, one
   holder, PO-21 (m)). CL, BS and attestation only remove. A kernel boot
   clears `/run` (M-B). Root acts outside A-2 are SL-1, outside the threat
   model.
5. **The running job needs no further decision.** Polkit authorized the
   `StartUnit` before the job was enqueued. Removing the rule does not cancel
   the job, and no further decision is made for `ExecStartPre=` or
   `ExecStart=` (PO-21 (p)). `systemctl start --wait` needs no further action
   (PO-21 (q)).
6. **So the grant is absent at every instant of the pass and after it**, for
   every terminal cause in (d). No step after CP-6 depends on how the pass
   ends.
7. **A failed start is not a pass.** If CP does not reach CP-7, `ExecStart=`
   never runs (PO-21 (o)). A live rule is then a pre-pass grant. CP-3 prevents
   any later start of this activation from running the pass. HL ends the
   activation, and CL removes the rule first (§4.2.5-R2 (h)).

*(D3-R5.)* Item 7 is **replaced** by §4.2.5-R5 (j). Its claim that "CP-3
prevents any later start" did not hold for failures before CP-4.

Items 1, 2, 4 and 5 of §4.2.5-R2 (n) stand. Item 3 is replaced by this
proof. OH-D-7's *"No live Polkit grant may … remain after the pass"* is met
literally, with "after the pass" read as written and not at the unit's
terminal transition.

##### (j) Proof obligations and fail-closed gates

Each item below is a **proposed proof obligation**, version-bound and paired
with the H-0 fact that fixes its version or state. None is an observed host
fact. **AP-0 is INVALID RUN unless every item is accepted for the observed
versions, and no grant is then linked.** A refuted item returns the
activation design to review. It is never worked around at run time.

| Item | Obligation (for the HF-07 versions) | H-0 fact |
|---|---|---|
| PO-21 (n) | an `ExecStartPre=` line prefixed `+` runs as root with full privileges, unaffected by `User=` and `NoNewPrivileges=`. It runs with PID 1's environment and nothing from the requester. It receives the same `INVOCATION_ID` as the `ExecStart=` process of the same start *(AR-6)*. The citation lists which unit execution settings (`UMask=`, `WorkingDirectory=`, `Standard*=`, limits) still apply to it *(AR-5)* | HF-05, HF-07 (`systemd`) |
| PO-21 (o) | `ExecStart=` is executed only after every `ExecStartPre=` has exited `0`. A non-zero exit, a signal, or expiry of the start timeout during an `ExecStartPre=` leaves `ExecStart=` unexecuted and the unit `failed`. *(D3-R4 additions:)* so does a `stop` request that arrives during `start-pre`; and the order does not depend on the lines' order in the unit file | HF-07 (`systemd`) |
| PO-21 (p) | Polkit authorizes `StartUnit` once, before the job is enqueued. Removing the rule afterwards does not cancel the job. No other Polkit decision is made for the job's `ExecStartPre=` or `ExecStart=` | HF-07 (`systemd`, `polkitd`) |
| PO-21 (q) | `systemctl start --wait` needs no Polkit action after `StartUnit` | HF-07 (`systemd`) |
| PO-21 (r) | the start timeout that applies (the manager's default, because the unit sets none) is recorded in the H-1 `baseline` (HF-16, §4.3.3) | HF-16 (`DefaultTimeoutStartUSec`); HF-07 |
| PO-11 (g) | with the rule granting `start` only, a `stop` request by `ubuntu` is not authorized without authentication | HF-07 (`polkitd`), HF-12 |

PO-21 (n) … (r) join the PO-21 citation step, and PO-11 (g) joins step 4
(§4.4.3). PO-15 must also cover `ExecStartPre`'s printed form and its flag
(h). H-1's P-0 needs only that PO-15 coverage, because in ST-1 a start
reaches CP-0 and refuses, and without CP the bootstrap still refuses.

##### (k) What remains, stated exactly

* **CX-1, a holder end racing with a start.** HL can end the activation, for
  example at W, after CP-2 checked for `hold-end`. The pass then runs after the
  holder has ended. It runs **without a grant**. CL, waiting on the lock,
  removes `pass-a.json` while the unit is active and ends HARD STOP
  `unit-still-active` (ST-1+R). This is the same outcome as a pass that
  outlives L. It is a lifetime defect, not a grant defect.
* **CX-2, a failed start leaves a pre-pass grant until the activation ends.**
  It lasts for HL's Δ plus CL's time, or up to R more if that CL dies. No pass
  has run, and none can run in this activation (CP-3). OH-D-7's "after the
  pass" does not apply to it. It is the same interval as ST-1.a2 and ST-2
  before any start.
  *(D3-R5: "none can run in this activation (CP-3)" is withdrawn as proved
  here. §4.2.5-R5 (f) proves it, and (k) narrows CX-1 and CX-2.)*
* **CX-3, interruption needs the executor.** If the executor is not
  available, a hung pass continues **without a grant** until it ends, or until
  a separately authorized root act ends it. The holder's lease L ends the
  activation, not the pass (CX-1).
* **SL-1** (§4.2.5-R2 (l)) is unchanged: root can link a rule anywhere, which
  is an act against the authority boundary.
* **`OH-H1-D3-R2-1`** is addressed in design by (i). It stays open until Codex
  re-reviews it and Peter decides. `OH-H1-D3-R1-1` and `OH-H1-D3-2` also stay
  open.

#### 4.2.5-R5 One start attempt per activation, on every path *(D3-R5)*

This subsection remediates Blocking finding `OH-H1-D3-R4-1` of
[Codex's D3-R4 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4.md).
It is **proposed** and inactive. It refines OH-D-10 (A) with route (iii-a). It
does not change the decision, the unit text, the rule text or any authority.
Where it differs from §4.2.5-R4, this subsection governs. It declares no
finding closed.

> **D3-R5 text, kept as history; amended by D3-R6 (§4.2.5-R6).** Codex's
> D3-R5 re-review found that OS-6 changed the decided route (iii-a)
> (`OH-H1-D3-R5-1`), and Peter Duscha then decided OS-6. Superseded: the
> statement above that this subsection "does not change the decision" as far
> as OS-6 is concerned; (a)'s OS-6 row, as a D3-R5 change; in (b), "Its only
> exception is CX-4" and SB-2's "except CX-4"; in (f), the third case's
> reliance on OS-6 as a D3-R5 rule and its EO sentence; the whole of (h); in
> (i), the definition of event S; in (j), the "with CX-4 as the only
> exception" wordings and the A-2 pin; and in (k), CX-3's and CX-4's
> wording. **Not superseded:** the SB-1, SB-2 and SB-3 mechanism, (c), (d),
> (e), (g), the rest of (f), (i) and (j), and the proof obligations.
> *(D3-R6)* markers below show each place.

##### (a) The defect, and what D3-R5 changes and keeps

**The defect.** In D3-R4, CP-3 tests the consume-evidence name, but only CP-4
creates it. A start that fails at CP-0 (`consume-no-activation`), CP-1
(`consume-busy`) or CP-2 (`consume-precondition`) therefore leaves no barrier.
So does a start that dies before CP-4: a kill, a start-timeout expiry, an
interpreter that cannot start, or a route (iii-a) `stop` during `start-pre`. A
later start of the same activation then finds no name at CP-3, and if the
earlier cause was transient it can reach `ExecStart=`. The D3-R4 terminal
table, proof item 7 and CX-2 claim the opposite.

**Why one barrier object cannot be enough.** Some failures happen before any
CP instruction runs. PID 1 can fail to create the `ExecStartPre=` process, the
interpreter can fail to start, or the process can be killed first. No barrier
that CP writes can exist after such a failure. A complete contract therefore
needs a fact that PID 1 itself changes at the end of **every** start attempt,
whether or not CP ran. D3-R5 uses PID 1's own record of the capture unit's
last entry into `inactive` or `failed`, under new proof obligations.

**Changed by D3-R5:**

| # | Change | Where |
|---|---|---|
| OS-1 | **Start-history baseline.** The holder records the capture unit's `InactiveEnterTimestampMonotonic` (τ₀) at AM-0, before any activation file exists. At `hold-start` it requires that no start attempt has begun or ended since. CP requires τ₀ unchanged | (c); (e) CQ-4 |
| OS-2 | **The claim is CP's first act under the lock.** It is created before any validation, so any identified attempt consumes the activation's only attempt. Its publication, identity, blocking point and durability point are fixed | (d); (e) CQ-2 |
| OS-3 | **The grant is removed next**, before any remaining precondition. CP can succeed only through its own verified removal of the once-linked rule | (e) CQ-3 |
| OS-4 | **CP checks that the holder is alive** (`active`, with the `ACT` journal's holder `InvocationID`). This answers §15.9 item 4 | (e) CQ-4 |
| OS-5 | **HL decides its end under the activation lock**, so no start can race HL's end into `ExecStart=` | (g) |
| OS-6 | **Route (iii-a) is issued only while the unit is `active`** with this activation's consumed `InvocationID`, never during `activating`. The start timeout bounds a hung CP | (h) |
| OS-7 | **A start before `hold-start` ends the activation** (`start-before-hold`), fail-closed | (c) |
| OS-8 | **AP-0 requires that `/var/tmp` ageing cannot remove the claim** within the activation's lease | (d) |

**Unchanged:** the rule grants `start` only. The fixed root `ExecStartPre=`
removes the grant and PK-verifies it before `ExecStart=`. A failed consume is
a failed start, not a pass. Route (iii-a) is the executor's A-2-authorized
root `stop`. Polling establishes no grant boundary. GP-R3, ST-1.ur, `/run`
boot clearing (M-B), supervision (M-S), automatic cleanup CL, the backstop,
attestation and the separately authorized RB-1 are unchanged. So are OH-D-1 …
OH-D-10, PF, PT, the journal format, RS-1, G-R1, P-1, P-2, PK, the attribution
classes and AR-1 … AR-8, except where (e) re-orders AR-1's and AR-3's checks.
PO-21 (n) … (r), PO-11 (g) and the new items of (j) are proposed proof
obligations, not host facts.

##### (b) The contract: one start attempt per activation

**Definitions.**

* A **start attempt** is one start job of `rp11-capture-pass-a.service` that
  PID 1 runs: the unit leaves `inactive` or `failed`, and PID 1 tries to run
  `ExecStartPre=`. A start request that PID 1 merges into a queued or running
  start job is part of that attempt, not a new one. Two attempts of the unit
  never overlap (PO-21 (t)).
* An attempt **ends** when the unit next enters `inactive` or `failed`, for any
  cause.
* An activation's **first attempt** A₁ is the first attempt that PID 1 begins
  after the holder's AM-0 observation (OS-1).
* An attempt is **identified** once its CP holds the activation lock on the
  `ACT` evidence directory that `pass-a.json` names (CQ-1). Every other attempt
  is **unidentified**: CP never ran, died before CQ-1, or failed CQ-0 or CQ-1.
* The **pre-barrier class** is every attempt that ends without a claim having
  been created by it. It holds every unidentified attempt, and every identified
  attempt whose `mkdirat` at CQ-2 failed other than with `EEXIST`, or which
  died before that `mkdirat` returned.

**Contract OSA.** For an activation X:

1. no attempt other than A₁ executes `ExecStart=` while any object of X
   exists;
2. A₁ executes it only if its CP exits `0`, at CQ-7;
3. this holds whether A₁ failed identified or unidentified, and whether a
   later attempt is requested by `ubuntu` under the grant or by root; and
4. no failed attempt is ever recorded or claimed as a pass.

The proof is (f). Its only exception is CX-4 ((k)), which needs a root `stop`
issued against A-2's terms.

*(D3-R6.)* Contract OSA is restated over the authorized path set 𝒜 in
§4.2.5-R6 (d) and (e), and it holds there **without exception**. CX-4 is not
an exception to it. CX-4 needs an act outside 𝒜 (§4.2.5-R6 (f)). The same
applies to SB-2's "except CX-4" in the table below.

**Three independent barriers**, each sufficient for the cases it covers:

| Barrier | Fact | Who makes it | Covers |
|---|---|---|---|
| **SB-1, the claim** | `/var/tmp/⟨activation_id⟩-consume-evidence` exists | CP, CQ-2, under the lock | every later attempt after an identified attempt that reached CQ-2's `mkdirat` |
| **SB-2, start history** | the capture unit's τ differs from τ₀ | PID 1, at the end of every attempt | every later attempt after **any** attempt, including the pre-barrier class (PO-21 (s), (t), (u)), except CX-4 |
| **SB-3, the rule token** | CP succeeds only if it removed, itself, the A1-intact rule that AM-2 linked once | CP, CQ-3 | at most one CP can ever succeed per activation |

##### (c) OS-1 and OS-7: the start-history baseline, on the holder's side

* **AM-0** *(amended)*. Before AK-1, so before any activation file exists, the
  holder reads, as root, `systemctl show -p ActiveState -p InvocationID -p
  InactiveEnterTimestampMonotonic -p Job rp11-capture-pass-a.service`. It
  requires `ActiveState` `inactive` or `failed` and `Job` empty. Otherwise it
  exits non-zero (`capture-busy-at-act`), and CL runs. It appends the values
  to `run-start` as the new field `capture: {active_state, invocation_id,
  inactive_enter_us}`. These are a₀, i₀ and τ₀ of §4.2.5-R2 (g), now durable.
* **`hold-start`** *(amended)*. After AM-3, still holding the lock taken at
  AM-0, the holder reads the same four properties again. It requires
  `ActiveState` `inactive` or `failed`, `Job` empty, and
  `InactiveEnterTimestampMonotonic` equal to τ₀. Only then does it append
  `hold-start {capture: {active_state, inactive_enter_us}}`, `fsync`, and
  release the lock (AR-2).
* **OS-7.** If that check fails, a start attempt has begun or ended since
  AM-0. The holder appends `hold-end {reason: "start-before-hold"}` instead of
  `hold-start`, exits non-zero, and CL runs (rule first). The activation never
  reaches ST-2. A-2 permits the operator's `start` only after `hold-start`, so
  this case is outside A-2's procedure. It is fail-closed.
* **Not an activation marker.** τ is PID 1's state, not a file. An ST-1 root
  probe, such as H-1's P-0 start, changes τ before any activation exists. The
  next AM-0 takes its τ₀ after that, so the probe neither marks nor blocks a
  later activation.

##### (d) OS-2: the attempt claim (barrier SB-1)

| Property | Value |
|---|---|
| Path | `/var/tmp/⟨activation_id⟩-consume-evidence/`, where `⟨activation_id⟩` is the value parsed at CQ-0 from root-owned `pass-a.json`. The name is never taken from the requester |
| Type, owner, mode | directory, `root:root`. Created with mode `0700`, then `fchmod` to `0755` once its journal exists. The journal is `root:root` `0644` |
| Created by | CP only, as root, at CQ-2, while holding the activation lock |
| Publication | `vfd = open("/var/tmp", O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW)`; `fstat(vfd)` must show a directory, `root:root`, mode `1777`. Then `mkdirat(vfd, name, 0700)`. `mkdirat` never follows a final symbolic link and fails `EEXIST` for an existing name of any type (PO-20 (h)) |
| **Blocking point** | the return `0` of `mkdirat`. From then on, every later `mkdirat` of that name on this host fails `EEXIST`. This is the barrier for every later attempt in this boot. The activation cannot outlive the boot (M-B), so blocking needs nothing more durable |
| Identity | `cfd = openat(vfd, name, O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW)`; `fstat(cfd)` must show a directory, uid 0, gid 0, mode `0700` and `st_nlink = 2`. `(dev, ino)` is journaled in `run-start` |
| Journal | `openat(cfd, "journal", O_WRONLY\|O_CREAT\|O_EXCL\|O_APPEND\|O_NOFOLLOW\|O_CLOEXEC, 0600)`, then `fchmod` `0644`; `fchmod(cfd, 0755)`; then `run-start` |
| **Durability point** | after `run-start`: `fsync` of the journal, then `fsync(cfd)`, then `fsync(vfd)`. On return of `fsync(vfd)`, the claim and its first line survive a crash (PO-20 (d)). That matters only for evidence: a kernel boot ends the activation in any case |
| Removal | **never.** CL, BS, attestation, RB-1 and every other procedure keep it. It is retained evidence, like the `ACT` and CL journals |
| Ageing | **OS-8.** AP-0 requires that no HF-19 `tmpfiles.d` line can age a `/var/tmp` entry younger than L + 2R seconds, so the claim lives at least as long as the activation. Otherwise `ACT` is INVALID RUN |
| Requester interference | `/var/tmp` is sticky, so `ubuntu` cannot remove or rename root's claim (PO-20 (h)). `ubuntu` can pre-create the name. CQ-2 then fails `EEXIST`, and the start is refused with no pass. Under OH-D-6 that is no more than `ubuntu` can already do |

**The consume journal's closed `op` set** is unchanged from §4.2.5-R4 (c):
`run-start`, `remove-intent`, `removed`, `remove-failed`, `grant-check`,
`consumed`, `consume-failed` and `run-end`. Its fields are amended:

* `run-start {invocation_id, boot_id, claim: {dev, ino}, act_journal: {sha256,
  length}}`;
* `consume-failed {step, class}`, with `step` one of `CQ-3`, `CQ-4` or `CQ-5`,
  and `class` the stable code of the failed check; and
* `consumed {pk_status, inactive_enter_us}`, the τ that CQ-4 observed.

CP never writes a record file. CL lists the journal's digest and length in
every later `deact` record ((j)).

##### (e) Procedure CP, D3-R5 order (steps CQ-0 … CQ-7)

The steps are labelled **CQ-n** so that they cannot be confused with the
superseded D3-R4 labels CP-0 … CP-7. Those labels keep their D3-R4 meaning
where they occur in D3-R4 text. CP runs as the capture unit's `ExecStartPre=+`,
as root, with PID 1's environment, after Polkit has authorized the `start` and
before PID 1 may execute `ExecStart=` (PO-21 (n) … (p)). Every exit other than
CQ-7's is non-zero, so `ExecStart=` is then never executed (PO-21 (o)). The
stable codes go to standard error as one fixed line without values. They are
diagnostic only.

| Step | Action | On failure |
|---|---|---|
| CQ-0 | **identify, without the lock and without any mutation.** `pfd = open("/run/freedom-blades-rp11", O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW)`; `openat(pfd, "pass-a.json", O_RDONLY\|O_NOFOLLOW\|O_NONBLOCK)`; `fstat` must show a regular file, uid and gid 0, mode `0644`, `st_nlink = 1` and size at most 65,536 bytes. Read it, and parse **only** `activation_id` against the §4.2.5-R1 (a) grammar | `consume-unidentified`, then exit. **Nothing is created.** Unidentified attempt |
| CQ-1 | **identify the activation lock.** `afd = open("/var/tmp/⟨activation_id⟩-act-evidence", O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW)`, then **one** `flock(afd, LOCK_EX\|LOCK_NB)` (AR-1) | open error: `consume-unidentified`. `EWOULDBLOCK`: `consume-busy`. Either way, exit with nothing created. Unidentified attempt |
| **CQ-2** | **the claim, first act under the lock (OS-2).** Exactly as (d): `mkdirat`, which is the blocking point; then identity, journal and `run-start`; then the durability point. No validation precedes it | `EEXIST`: `consume-repeated`. Exit at once. The existing claim and its journal are not opened, and nothing else is touched. Any other `mkdirat` error: **no claim** (pre-barrier). Run CQ-3 in grant-priority form without lines, then exit `consume-claim-failed`. A failure after `mkdirat` returned (identity, journal, `fchmod`, `run-start`, any `fsync`): **the claim exists.** Run CQ-3 in grant-priority form, appending lines only while the journal still accepts them, then exit `consume-evidence-unwritable` |
| CQ-3 | **the grant (OS-3), before any remaining precondition.** Read and parse the `ACT` journal (torn tail ignored, §4.2.4-R1 (b)), and require the current `boot_id` to equal its `run-start` (boot scoping). Classify the object at `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules` against the journal's identity line and the H-1 record's staged-rule digest. If A1-intact, remove it by G-R1: descriptor re-verification immediately before removal (type, `(dev, ino)`, uid and gid 0, mode `0644`, `st_nlink = 1`, full re-hash, no forbidden extended-attribute name); `remove-intent`, `fsync`, `unlinkat`, `fsync` of the rules directory, `removed`, `fsync` | absent, A1-damaged, A0, an unparsable `ACT` journal, another boot, or a re-verification mismatch: `consume-failed {step: "CQ-3", class}`, exit. `unlinkat` error: `remove-failed {errno}`, exit. The object is left for CL. **SB-3: CP never succeeds unless this step journaled `removed` for the A1-intact rule** |
| CQ-4 | **the activation is live and this is its first attempt.** All of the following, read under the lock. `pass-a.json` is still at its path with `pfd`'s `(dev, ino)`, A1-intact against its identity line, and equal to `run-start.pass_config_sha256`. `⟨activation_id⟩.act.json` exists, is `root:root` `0444`, and has `outcome: "activated"`. The `ACT` journal has `hold-start` and no `hold-end`. No `⟨activation_id⟩-deact-*` evidence directory and no `deact` record exists. The capture root that `pass-a.json` names is absent (`lstat`). **OS-4:** `systemctl show -p ActiveState -p InvocationID ⟨activation_id⟩.service` gives `active`, with the `ACT` journal's `holder_invocation_id`. **OS-1:** `systemctl show -p ActiveState -p InvocationID -p InactiveEnterTimestampMonotonic rp11-capture-pass-a.service` gives `activating`, an `InvocationID` equal to CP's own `INVOCATION_ID`, and `InactiveEnterTimestampMonotonic` equal to `hold-start`'s τ₀ (PO-21 (s), (v)) | any check false, or any read or `systemctl show` error: `consume-failed {step: "CQ-4", class}`, exit (`consume-precondition`) |
| CQ-5 | **post-check.** `ENOENT` at the rule path; then PK for verb `start` (§4.2.5-R1 (f)) must return *not authorized* within the PO-11 (d) bound. Append `grant-check {status}`, `fsync` | `consume-failed {step: "CQ-5", class: "removed-unconfirmed"}`, exit |
| CQ-6 | append `consumed {pk_status, inactive_enter_us}`, `fsync` | a failed append or `fsync`: exit `consume-evidence-unwritable`. **No `consumed` line means no pass** |
| CQ-7 | append `run-end`, `fsync`, release the lock, exit `0`. Only now may PID 1 execute `ExecStart=` | a failed append or `fsync`: exit non-zero. `consumed` is durable, but `ExecStart=` does not run |

**Grant-priority form of CQ-3.** CQ-3's classification and G-R1 removal do
not depend on the claim journal. The identity comes from the `ACT` journal,
and the digest from the H-1 record. Without a writable claim journal, CQ-3
removes an A1-intact rule after the same descriptor re-verification, writes
no line it cannot make durable, and then runs CQ-5's PK check with the result
held in memory. It never continues to CQ-4. The attempt always fails. This is
GP-R3's principle, applied to CP: a failure to write evidence reduces what is
claimed, and it never keeps a live grant that could be removed.

**What each step can and cannot leave**, in brief: CQ-0 and CQ-1 leave nothing.
CQ-2 leaves the claim, or with `EEXIST` nothing new. From CQ-3 on, the rule is
gone or is left exactly as it was. CQ-4 … CQ-7 leave only journal lines.
**No step before CQ-7 can let `ExecStart=` run.**

**The map from D3-R4 to D3-R5.**

| D3-R4 step | D3-R5 step | Change |
|---|---|---|
| CP-0 (parse `activation_id`) | CQ-0 | adds the descriptor checks; failure is now `consume-unidentified` and is covered by SB-2 |
| CP-1 (lock, non-blocking) | CQ-1 | unchanged; failure is covered by SB-2 |
| CP-2 (preconditions) | CQ-4 | moved **after** the claim and the grant removal; adds OS-1 and OS-4 |
| CP-3 (test the name) | CQ-2 (`EEXIST`) | the test **is** the exclusive creation; there is no separate test |
| CP-4 (create the name) | CQ-2 | moved **before** every validation |
| CP-5 (remove the rule) | CQ-3 | moved before the preconditions |
| CP-6 (post-check, `consumed`) | CQ-5, CQ-6 | split |
| CP-7 (`run-end`, exit `0`) | CQ-7 | unchanged |

##### (f) Proof of contract OSA

**Lemma 1 (attempts are serial).** By PO-21 (t), a later attempt A_k begins
only after the previous attempt has ended, that is, after the unit entered
`inactive` or `failed`. A start request during an attempt joins it and runs
no second CP.

**Lemma 2 (every ended attempt changes τ, or leaves a loaded `failed` unit).**
By PO-21 (s), every entry into `inactive` or `failed` sets the unit's
`InactiveEnterTimestampMonotonic` to a value later than every earlier one in
the boot. By PO-21 (k), a `failed` unit stays loaded, so the value persists.
By PO-21 (u), an attempt ends `failed` when CP exits non-zero, is killed by a
signal that no stop job sent, exceeds the start timeout, or cannot be
executed. Only a stop job during `start-pre` may end it `inactive`, in which
case the unit may be unloaded and its τ read back as `0` (PO-21 (k), (s)).

**Lemma 3 (τ₀ is a valid baseline).** τ₀ is read at AM-0 and re-checked at
`hold-start` under the lock (OS-1). If any attempt had begun or ended between
them, `hold-start` would not be written (OS-7), and every CQ-4 would refuse it.

**Proof of 1 and 3.** Let A_k, with k ≥ 2, be any later attempt of X. By
Lemma 1, A₁ has ended. Three cases cover every way A₁ can have ended without
running the pass, and the first case also covers a pass that did run.

* **A₁ reached CQ-2's `mkdirat`** (identified, claim made). A_k's CQ-2 gets
  `EEXIST` and exits before any check. SB-1 alone suffices.
* **A₁ is in the pre-barrier class, and ended `failed`.** By Lemma 2, A_k's
  CQ-4 reads τ ≠ τ₀ and refuses. If A_k's CP fails earlier, it refuses
  earlier. SB-2 suffices, with no CP line of A₁ needed. This covers a CP that
  never ran, CQ-0 and CQ-1 failures, a busy lock, a kill, a timeout and a
  failed `mkdirat`.
* **A₁ is in the pre-barrier class, and ended `inactive`.** That needs a stop
  job during A₁'s `start-pre` before its `mkdirat`. By OS-6, A-2 permits route
  (iii-a) only while the unit is `active`. A_k's CQ-4 still refuses if τ
  remains above τ₀ (no unload), or if τ₀ ≠ 0 (an unload reads back `0`). The
  only remaining combination (a root `stop` against A-2's terms during
  `start-pre`, before the claim, with τ₀ = 0 and the unit unloaded before A_k)
  is residual **CX-4** ((k)). If PO-21 (u) shows that such a stop ends
  `failed`, CX-4 is void. An orderly transition (EO) is covered without SB-2:
  it stops the holder too, CL removes the rule and `pass-a.json`, and until
  then OS-4 refuses any attempt.

  *(D3-R6: the third case no longer rests on OS-6 as a D3-R5 rule. Under the
  decided OS-6 no act within 𝒜 produces it (§4.2.5-R6 (d), (e)). The EO
  sentence is corrected: the design fixes no order between the holder's and
  the capture unit's stop, so OS-4 does not cover EO. EO is outside 𝒜 and is
  CX-4's source (b) (§4.2.5-R6 (f)).)*

Whatever A_k's requester, it runs the same CP (PO-21 (n)). So the result holds
for a start by `ubuntu` and by root alike.

**Proof of 2.** `ExecStart=` runs only after CP exits `0` (PO-21 (o)), and CP
exits `0` only at CQ-7. CQ-7 follows CQ-2 (its own claim), CQ-3 (its own
journaled removal of the A1-intact rule), CQ-4 (OS-1: A₁ is the first attempt;
OS-4: the holder is alive) and CQ-5 (PK *not authorized*).

**SB-3 bounds success independently.** AM-2 links the rule once per activation
and nothing re-links it (§4.2.5-R4 (i) item 4). A removal can therefore be
journaled `removed` by at most one actor. A CP that finds the rule absent fails
at CQ-3. So at most one CP per activation can reach CQ-7, whatever happens to
SB-1 and SB-2.

**Proof of 4.** A pass is claimed only from a consume journal with `consumed`
and a capture root (HL `pass-ended` or `pass-failed-early`; the `deact`
record's `consume.outcome` of (g)). A failed attempt writes no `consumed` line,
because CQ-6 follows every check, and it never runs `ExecStart=`. It is
recorded as `start-failed-before-exec`.

**Pre-barrier failures cannot become a valid start in the same activation.**
This is the case analysis above, read for a pre-barrier A₁: SB-2 refuses every
later attempt, with CX-4 as the only exception. The pre-barrier class is
therefore not narrowed by assumption. It is covered by a fact that PID 1
changes at the end of the failed attempt itself, so it does not depend on any
CP instruction having run.

##### (g) OS-5: CP, CL, HL and the backstop agree

**One lock.** The `ACT` evidence directory's `flock` (PO-20 (f)) is held:

* by the holder from AM-0 until `hold-start` is durable (AR-2, OS-1);
* by CP from CQ-1 until it exits;
* by HL **only while it decides to end** (OS-5, below);
* by each CL attempt from CL-0 until it exits, including GP-R3, the backstop's
  BS-4 and `attest`.

BS-1 … BS-3 only read. The kernel releases the lock at every process exit,
including a kill.

**OS-5, HL ends under the lock.** HL still observes every Δ without the lock.
When an observation satisfies a terminal reason, HL tries
`flock(LOCK_EX|LOCK_NB)` once:

* on `EWOULDBLOCK`, a CP holds the lock. HL does not end, and it observes again
  after Δ;
* with the lock, HL observes again, this time also reading the claim and its
  journal. If a terminal reason still holds, it appends `hold-end {reason,
  observation}`, `fsync`s it, and exits **while holding the lock**. Otherwise it
  releases the lock and continues.

A CP that gets the lock after the holder's exit finds `hold-end`, or a holder
that is not `active`, and refuses at CQ-4. It has still made its claim and
removed the rule. A CP that held the lock first has either failed, or
completed CQ-7, in which case a pass is running and HL's next decision under
the lock sees the claim and `consumed`. **So no attempt can pass CQ-4 after HL
has decided to end.** CX-1 is narrowed to the holder's own death or lease
expiry ((k)).

**HL's terminal reasons, amended** (they replace §4.2.5-R2 (g) and §4.2.5-R4 (f)
where they differ):

| Reason | Condition (read under the lock before HL acts on it) | Meaning |
|---|---|---|
| `pass-ended` | the capture root exists, and `ActiveState` is `inactive` or `failed` | the pass ran and its process has ended |
| `pass-failed-early` | the consume journal has `consumed`, the capture root is absent, `ActiveState` is `inactive` or `failed`, **and** `ExecStart=` is shown to have been forked in this attempt: HL observed `active` with the consumed `InvocationID`, or `ExecMainStartTimestampMonotonic` is non-zero (PO-21 (v)) | the pass started after CP and failed before X-1 (premise P-E) |
| `start-failed-before-exec` | the capture root is absent, `pass-failed-early` does not hold, `ActiveState` is `inactive` or `failed`, and **any** of the following: τ ∉ {τ₀, `0`}; `InvocationID` is non-empty and differs from i₀; the claim exists | an attempt ended without evidence that `ExecStart=` was forked. This label errs only towards "no pass" |
| `capture-unloaded` | the capture root and the claim absent, `ActiveState` `inactive`, τ = `0` ≠ τ₀, and `InvocationID` empty or i₀ | the unit was unloaded. An attempt may or may not have ended `inactive`. SB-2 already refuses every later attempt, so the activation is ended, fail-closed |
| `start-window-expired` | W seconds since `ACT` PASS, the capture root and the claim absent, τ = τ₀, `ActiveState` `inactive` or `failed`, `Job` empty | no attempt has begun |
| `observation-failed` | an observation errors or does not parse | fail closed. Like every reason, it is acted on only under the lock. A CP holding the lock ends within the start timeout |

`start-failed-before-exec` no longer depends only on `InvocationID`. SB-2's τ
also detects an attempt that ended `inactive` without unloading, and the
claim detects any identified attempt.

**CL's classification of the attempt.** CL-1 reads the claim and its journal,
and CL-2 records the capture unit's τ. The `deact` record's `consume` key
((i)) states one of:

| `consume.attempt` | Condition | Meaning |
|---|---|---|
| `none` | no claim, τ = τ₀, and the holder's `hold-end` reason is not `start-before-hold` or `start-failed-before-exec` | no attempt in this activation |
| `unidentified` | no claim, and τ ∉ {τ₀, `0`}, or `hold-end` is `start-failed-before-exec` or `start-before-hold` | a pre-barrier attempt; no pass |
| `indeterminate` | no claim, τ = `0` ≠ τ₀, and none of the above | the unit was unloaded. Whether an attempt ended `inactive` cannot be told. No pass is claimed |
| `claimed` | the claim exists | an identified attempt. `consume.outcome` is `consumed`, `failed` (with `{step, class}`), `incomplete` (no `consumed` and no `consume-failed`: CP was killed), or `unjournaled` (no valid journal) |

CL-3's rule classes from the claim journal are §4.2.5-R4 (g)'s:
`removed-earlier` with a durable `removed` line, otherwise
`absent-before-removal`, each needing CL-4's own PK *not authorized* for
`st1-verified`. CL never creates, opens for writing or removes the claim. CP
never removes `pass-a.json`, a directory or a record.

**The backstop** is unchanged. BS-1 does nothing while the holder is
`activating`, `active`, `deactivating` or `reloading`. Every BS-4 attempt runs
CL under the lock, so it can never interleave with CP.

**No interval in which a repeated start can race cleanup into `ExecStart=`.**
A repeated start is an attempt A_k with k ≥ 2. (f) refuses it whatever
cleanup is doing, because SB-1 and SB-2 depend only on A₁'s past, not on CL's
progress. A first attempt that coincides with cleanup also cannot pass:

* CL holds the lock: CQ-1 gets `consume-busy`, and SB-2 then also blocks every
  later attempt;
* CL has started: a `deact` evidence directory exists, or the holder is not
  `active` (CL runs only after the holder ends, or under `attest` with the
  holder not active), so CQ-4 refuses;
* CL in GP-R3 left no `deact` directory: the holder is still not `active`
  (OS-4), and GP-R3 has removed the rule, so CQ-3 fails (SB-3); and
* CL has removed `pass-a.json`: CQ-0 is unidentified.

##### (h) OS-6: route (iii-a), when it may be issued

§4.2.5-R4 (e)'s "When" is amended. The executor issues the literal only while
`systemctl show -p ActiveState,InvocationID rp11-capture-pass-a.service` gives
`active`, with an `InvocationID` equal to the consume journal's `run-start`
`invocation_id`, and only when that journal has `consumed`. That is a running
pass of this activation. It is never issued while the unit is `activating`. A
CP that hangs is ended by the unit's finite start timeout (AR-4), which ends
the attempt `failed` (PO-21 (u)) and so engages SB-2. Nothing else about the
route changes: the literal, the executor, A-2's pin and the §9.5.3
classification are as §4.2.5-R4 (e) states. "What follows" uses the HL reasons
of (g).

*(D3-R6.)* (h) is **superseded** by §4.2.5-R6 (b). Its condition is the one
Peter Duscha decided, but it is now the decision's, not a D3-R5 refinement,
and §4.2.5-R6 (b) adds the exclusions, how the executor establishes the
condition, why durability needs no further check, and Lemma R6.

##### (i) Every boundary around the barrier

Events: **K**, a kill of CP for any cause, including the kernel OOM killer;
**T**, the start timeout; **S**, a stop job (route (iii-a) used against OS-6,
or root outside A-2); **C**, contention, meaning another lock holder;
**M**, malformed or missing input; **L**, cleanup running or finished; **EO**
and **EU** as §4.2.5-R2 (k). "SB-2" means that later attempts are refused by
the start history, and "SB-1" by the claim. In every row, `ExecStart=` has not
run.

*(D3-R6.)* Event **S** is a stop job during `start-pre`. Route (iii-a) is never
one under the decided OS-6, so S is always outside the authorized path set 𝒜
(§4.2.5-R6 (d), (g)). The S column describes what happens if such an act
occurs. In the table, "SB-2, or CX-4" reads "SB-2, or, outside 𝒜, CX-4".

| Point | K or T | S | C | M | L | EO | EU |
|---|---|---|---|---|---|---|---|
| before CP's first instruction (fork, `exec`, interpreter start) | unit `failed`; no claim; rule live; SB-2; HL `start-failed-before-exec`; CL rule first | ends `inactive` or `failed` (PO-21 (u)); SB-2, or CX-4 | n/a | n/a | n/a | holder stopped too, then CL; boot | M-B; attestation |
| CQ-0 | as above | as above | n/a | `consume-unidentified`: nothing created; SB-2 | `pass-a.json` removed by CL: unidentified; activation already ending | as above | as above |
| CQ-1 | as above | as above | `consume-busy`: nothing created; SB-2. The holder before `hold-start`: OS-7 ends the activation. HL deciding: HL sees `activating` under the lock and does not end; this attempt fails, SB-2 refuses every later one, and HL then ends `start-failed-before-exec`. CL: the activation is already ending | `ACT` directory missing or unopenable: unidentified; SB-2 | CL holds the lock: busy | as above | as above |
| CQ-2, before `mkdirat` returns | as above (pre-barrier) | as above | n/a (lock held) | `/var/tmp` wrong type or mode: `consume-claim-failed` in grant-priority form; SB-2 | n/a: CL waits on the lock | as above | as above |
| CQ-2, `mkdirat` error | — | — | — | `EEXIST`: `consume-repeated`, nothing touched; SB-1. Other error: no claim; CQ-3 grant priority removes the rule; exit; SB-2 | n/a | — | — |
| CQ-2, after the blocking point, before the durability point | claim exists, perhaps without journal or `run-start`; SB-1 and SB-2; CL classes `claimed`/`unjournaled` | claim exists; SB-1 | n/a | journal or identity failure: grant priority, `consume-evidence-unwritable`; SB-1 | n/a | SB-1; holder stopped, CL | claim may be lost with the crash; the boot ends the activation (M-B) |
| after the durability point, before CQ-3's `remove-intent` | claim journaled; rule live; SB-1, SB-2; HL ends; CL removes the rule first | SB-1 | n/a | an invalid `ACT` journal or another boot: rule A0, kept; `consume-failed {CQ-3}`; CL escalates | n/a | as left | claim survives; attestation |
| CQ-3, `remove-intent` written, before `unlinkat` | rule live; CL classes it and removes it (A1-intact) | SB-1 | n/a | re-verification mismatch: kept, `consume-failed`; CL escalates | n/a | as left | as left |
| CQ-3, after `unlinkat`, before `removed` | rule absent; CL classes `absent-before-removal`, PK required | SB-1 | n/a | — | n/a | as left | as left |
| CQ-3 done (`removed` durable) | rule absent; CL `removed-earlier` | SB-1 | n/a | `unlinkat` error: `remove-failed`, rule live, `grant-unremovable` for CL | n/a | as left | as left |
| CQ-4 | as above | SB-1 | n/a | any check false or any read error: `consume-failed {CQ-4}`; rule already removed | a `deact` directory, `hold-end` or a dead holder: refused | as left | as left |
| CQ-5 | as above | SB-1 | n/a | PK still *authorized* after the bound: `consume-failed {CQ-5, removed-unconfirmed}`; CL re-checks PK | n/a | as left | as left |
| after `consumed`, before CQ-7's exit | `consumed` durable but CP killed: unit `failed`, no `ExecStart=`. `pass-failed-early` does not hold, because `ExecStart=` was never forked; HL ends `start-failed-before-exec`, and the record says `consume.outcome` `consumed` with no pass | SB-1 | n/a | `run-end` unwritable: exit non-zero, no `ExecStart=` | n/a | as left | as left |
| CQ-7 exit `0` | — | — | — | — | the pass runs with no grant (§4.2.5-R4 (i)) | — | — |

**A `consumed` line alone is therefore not a pass.** HL's `pass-failed-early`
needs positive evidence that `ExecStart=` was forked ((g)). Without it, the
attempt is recorded `start-failed-before-exec`, so a label can understate a
pass that was stopped within Δ and then unloaded, but it never claims one that
did not run. The `deact` record carries the `consumed` line, the unit's
`Result` and both observations, so a reviewer sees the basis.

**Every row ends** with the rule removed by CP or by CL, with every later
attempt refused (SB-1 or SB-2), and with CL reaching `st1-verified`, AC-9's
HARD STOP or ST-1.ur, exactly as before. No row creates an activation marker
from an unidentified attempt, and no row waits for a human to disable the
grant.

##### (j) Amendments elsewhere, and the new proof obligations

* **§4.2.5-R4 (d), last row.** It becomes: *CP fails, refuses, is killed or
  exceeds the start timeout, or the attempt fails before CP runs:* no pass ran.
  The rule is already removed if CQ-3 completed; otherwise it is a pre-pass
  grant that HL's end and CL remove, rule first. **Every later start of this
  activation is refused** by SB-1 or SB-2 ((f)), with CX-4 as the only exception.
* **§4.2.5-R4 (g) (j), ST-2.c and ST-2.f.** ST-2.c: the grant is live until
  CQ-3's `unlinkat` and the polkitd reload, and CQ-5 confirms *not authorized*.
  Its sub-phases are unidentified (CQ-0, CQ-1), claimed (CQ-2) and consumed
  (CQ-6). ST-2.f: entered by **any** ended attempt without `ExecStart=`. The
  claim is present if the attempt was identified, and absent otherwise. The
  rule is absent if CQ-3 completed, and possibly live otherwise. "No pass has
  run or can run" now rests on (f), not on CP-3. It is left by HL's
  `start-failed-before-exec` under the lock, then CL.
* **§4.2.5-R4 (g) (k), the ST-2.c row.** EH: SP waits up to S for the lock. If
  CP has passed CQ-4 already, the pass may run without a grant, and CL ends
  `unit-still-active` (CX-1). Otherwise CQ-4 refuses, and CL removes the rule
  first. EO: the transition stops the start job and the holder. No pass runs.
  A row **ST-2.f** is added: ES —; EH SP, rule first; EP n/a; EC BS; EO SP;
  EU BC. A repeated start in ST-2.f is refused by SB-1 or SB-2.
* **§4.2.5-R4 (i), item 7** is replaced: *"A failed start is not a pass, and
  no later start of the activation runs one. If CP does not reach CQ-7,
  `ExecStart=` never runs (PO-21 (o)). By (f), every later attempt of the
  activation is refused by the claim (SB-1) or by PID 1's start history (SB-2),
  whether the failed attempt was identified or not, with CX-4 as the only
  exception, and at most one CP can ever succeed (SB-3). A rule that is still
  live is a pre-pass grant. HL ends the activation under the lock, and CL
  removes the rule first."*
* **§4.2.5-R4 (k), CX-2** is amended. A pre-pass grant now remains after a
  failed attempt only if that attempt did not complete CQ-3: an unidentified
  attempt, a CQ-3 failure, or a kill before `unlinkat`. It lasts for HL's Δ
  plus CL's time, or up to R more if that CL dies. "None can run in this
  activation" now rests on (f).
* **Records.** `rp11-activation-record/2`'s `consume` key becomes `{attempt,
  claim: {path, dev, ino} or "absent", journal: {path, sha256, length} or
  "absent", invocation_id or "absent", outcome, failure: {step, class} or
  "absent", pk_status or "absent"}`, with `attempt` and `outcome` as (g)
  defines them. The `unit` key gains `{inactive_enter_us_baseline,
  inactive_enter_us_at_start}`. `hold_end_reason` admits `start-before-hold` and `capture-unloaded`.
  The failure classes admit `capture-busy-at-act`.
* **Journals.** The `ACT` journal's closed `op` set is unchanged. Its
  `run-start` gains `capture`, and `hold-start` gains `capture` ((c)). `hold-end`
  is written under the lock (OS-5). The consume journal's fields are as (d).
* **A-2 pins.** The route (iii-a) precondition of (h). The rest is unchanged.
* **AP-0** additionally requires: PO-21 (s) … (v) and PO-20 (h) accepted for
  the observed versions; OS-8's ageing condition; and `/var/tmp` a directory,
  `root:root`, mode `1777` (HF-11).

**New proof obligations.** Each is proposed, version-bound and paired with
the H-0 fact that fixes its version. None is an observed host fact. **AP-0 is
INVALID RUN unless each is accepted, and no grant is then linked.** A refuted
item returns the activation design to review.

| Item | Obligation | H-0 fact |
|---|---|---|
| PO-21 (s) | `InactiveEnterTimestampMonotonic` is set, at every transition of a unit into `inactive` or `failed`, to the manager's monotonic time of that transition, which is later than every earlier value in the boot. It is unchanged while the unit is `activating`, by any property read, and by a start job before the unit leaves `inactive` or `failed`. It survives `daemon-reload` and `daemon-reexec` while the unit stays loaded. A unit that has been unloaded and loaded again reports `0` until it next enters one of those states. `systemctl show -p` prints it as decimal microseconds | HF-07 (`systemd`) |
| PO-21 (t) | two start attempts of one unit never overlap. A start request while a start job is queued or running joins it and runs no second `ExecStartPre=`. A start of an `active` unit runs no `ExecStartPre=`. A start while the unit is `deactivating` runs only after it has entered `inactive` or `failed` | HF-07 |
| PO-21 (u) | the state in which a start attempt ends for each cause. An `ExecStartPre=` that exits non-zero, is killed by a signal that no stop job sent, exceeds the start timeout, or cannot be forked or executed ends the attempt `failed`. The citation states whether a stop job during `start-pre` ends it `inactive` or `failed` | HF-07 |
| PO-21 (v) | `systemctl show -p …`, run by an `ExecStartPre=+` process during its own unit's start job, returns without waiting for that job. It reports `activating`, the job's `InvocationID`, and τ as it was before this attempt. A query of another unit (the holder) behaves as PO-21 (l). `ExecMainStartTimestampMonotonic` is reset at the start of each attempt, and is non-zero after the attempt's end only if `ExecStart=` was forked in it | HF-07 |
| PO-20 (h) | in a root-owned directory with mode `1777` on the HF-15 filesystem of `/var/tmp`, an entry owned by root can be unlinked or renamed only by a process with `CAP_FOWNER` (root). `mkdirat` fails `EEXIST` for an existing name of any type, including a dangling symbolic link, and never follows it | HF-04 (kernel), HF-15 (`/var/tmp`'s filesystem) |

**H-0 additions:** HF-11 adds `/var/tmp` (type, owner, mode including the
sticky bit, `(dev, ino)`). HF-19 already records `/var/tmp` ageing. No other
fact is added. PO-21 (s) … (v) are fixed by the HF-07 systemd version.

*(D3-R6.)* In the bullets above, each "with CX-4 as the only exception" reads
"without exception within the authorized path set 𝒜 of §4.2.5-R6 (d); CX-4
requires an act outside 𝒜". The A-2 pin is the full sentence of §4.2.5-R6 (g),
"A-2". The proof obligations are unchanged.

##### (k) What remains, stated exactly

* **CX-1, narrowed.** A start can no longer race HL's own decision to end
  (OS-5). It can still coincide with the holder's **death** or its lease L
  expiring after CQ-4 has seen the holder `active`. The pass then runs without
  a grant. CL removes `pass-a.json` while the unit is active and ends HARD STOP
  `unit-still-active`. This is a lifetime defect, not a grant defect, and not
  a repeated start.
* **CX-2, narrowed** as (j) states. It is the pre-pass grant after a failed
  attempt that did not complete CQ-3. No pass can run in that interval.
* **CX-3** is unchanged. Interruption needs the executor, and now only while
  the pass is `active` (OS-6).
* **CX-4 (new), a stop during `start-pre` against A-2's terms.** It needs all
  of the following together: a root `stop` job while the first attempt is in
  `start-pre`, before its claim's `mkdirat` returns, or at any time before
  `hold-start` (OS-6 forbids it, and it is not route (iii-a)); PO-21 (u)
  showing that such a stop ends the attempt `inactive`; a τ₀ of `0` at AM-0; and the unit being unloaded before the next
  attempt. Then SB-1 and SB-2 are both absent. The rule is still live, so a
  later `ubuntu` start could run the pass, **with no grant** during or after
  it (CQ-3 runs first). It is a root act outside A-2, of the SL-1 kind. If
  PO-21 (u) shows that the stop ends `failed`, CX-4 is void. Closing it in
  every case would need a further unit or rule line, for example a start
  limit or a once-only rule, which changes OH-D-10 (A). That is **not**
  proposed.

  *(D3-R6: CX-4 is re-stated in §4.2.5-R6 (f) as a residual outside the
  authorized path set 𝒜, of the SL-1 kind, with the forbidden orderly
  transition as a second source. "OS-6 forbids it" now rests on Peter's
  decision. CX-3: interruption needs the executor, and is available only under
  §4.2.5-R6 (b).)*
* **Liveness, not safety.** OS-1 and OS-7 fail closed. The unloading of an
  `inactive` capture unit whose τ₀ was non-zero, between AM-0 and the first
  attempt (HL `capture-unloaded`), an early or root start, or a start that meets
  HL's decision under the lock each end the activation without a pass. Another
  pass then needs a new A-2.
* **SL-1** (§4.2.5-R2 (l)) is unchanged.
* **`OH-H1-D3-R4-1`** is addressed in design by (b) … (i). It is **not**
  declared closed. `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` stay
  open.

*(D3-R6.)* §4.2.5-R5 is kept as history. §4.2.5-R6 records OS-6 as Peter
Duscha's decided amendment to route (iii-a), and it scopes contract OSA to the
authority boundary. Where the two differ, §4.2.5-R6 governs.

#### 4.2.5-R6 OS-6 decided: route (iii-a) only on a consumed, running pass, and contract OSA within the authority boundary *(D3-R6)*

This subsection incorporates Peter Duscha's OS-6 decision
([R6 authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-authority.md))
and remediates Blocking issue `OH-H1-D3-R5-1` of
[Codex's D3-R5 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5.md).
It is **proposed** and inactive. It declares no finding closed. Where it
differs from §4.2.5-R4 or §4.2.5-R5, this subsection governs.

##### (a) The finding, the decision and what D3-R6 changes

**The finding.** D3-R5 proved its one-start-attempt property only by
narrowing route (iii-a) from D3-R4's `activating` or `active` to `active`
after a durable `consumed` line (OS-6). It presented that narrowing as a
refinement. Codex found that it changed a decided route, that only Peter
could make that change, and that, without it, CX-4 was an exception inside
the authorized route. The D3-R5 return should therefore have been **BLOCKED
REMEDIATION**. D3-R6 accepts the finding as stated.

**The decision** (quoted from the R6 authority): *"Route iii-a is available
only after the capture unit is `active`, its `InvocationID` equals the consume
journal's `run-start.invocation_id`, and the consume journal contains a durable
`consumed` line. Route iii-a is not available while the unit is `activating` or
during `start-pre`. A hung consume step is bounded by the finite, fail-closed
start timeout."* The authority adds: *"This decision amends the D3-R4
route-iii-a timing condition. It does not change the fixed interruption
literal, its executor, its A-2 authority, or its §9.5.3 classification for a
running pass."*

**What D3-R6 changes.** OS-6 is no longer a D3-R5 refinement. It is a
**decided amendment** to the route (iii-a) that OH-D-10 (A) adopted, and its
source is the R6 authority, not this proposal. D3-R6 makes the rest of the
design follow from it:

| # | Change | Where |
|---|---|---|
| RX-1 | Route (iii-a)'s governing text, with the decided condition as three conjuncts and its exclusions | (b) |
| RX-2 | A lemma: every route (iii-a) `stop` lands after SB-1's blocking point, even when the executor's read and the `stop` are not atomic | (c) |
| RX-3 | Contract OSA is stated over the **authorized path set** 𝒜. It holds over 𝒜 **without exception**. CX-4 is outside 𝒜 | (d), (e) |
| RX-4 | CX-4 is re-stated as a residual of the SL-1 kind, outside OSA's scope, with a second source, a prohibited orderly transition, that D3-R5 had treated as covered | (f) |
| RX-5 | Reconciliation of D-1, A-2, the terminal-cause and boundary tables, ST-2.c and ST-2.f, the HL reasons, records, traceability, successors, tests and drills | (g) |

**Unchanged, and preserved from D3-R5:** SB-1, SB-2 and SB-3; the claim's
publication, blocking and durability points (§4.2.5-R5 (d)); the CQ-0 … CQ-7
order and the grant-priority form of CQ-3 ((e)); the one shared lock and OS-5
((g)); OS-1, OS-2, OS-3, OS-4, OS-5, OS-7 and OS-8; the finite, fail-closed
start timeout (AR-4); PO-21 (n) … (v), PO-20 (h) and PO-11 (g), each still a
proposed proof obligation; the fixed interruption literal, its executor, its
A-2 authority and its §9.5.3 classification; the unit and rule bytes; GP-R3,
ST-1.ur, M-B, M-S, CL, the backstop, attestation and the separately authorized
RB-1. One D3-R5 sentence, on the orderly transition (EO) in §4.2.5-R5 (f), is
corrected in (f) below, because it relied on an order that the design does not
fix.

##### (b) Route (iii-a), as amended by OS-6 (governing text)

This replaces §4.2.5-R4 (e) "When" and "What it is", and §4.2.5-R5 (h). The
other parts of §4.2.5-R4 (e) stand.

* **Literal.** Unchanged: the one fixed command line of §4.2.5-R4 (e), pinned
  by A-2 with its SHA-256.
* **Who.** Unchanged: only the executor (U-2), under this activation's A-2, in
  an interactive session on `oracle-test` as `ubuntu` (OH-D-2), elevating
  through `sudo -n`. The operator has no `stop` route.
* **When (OS-6, decided).** The route is **available** only while all three
  of the following hold:
  1. **OC-1.** The capture unit's `ActiveState` is `active`.
  2. **OC-2.** Its `InvocationID` equals the `invocation_id` of the
     `run-start` line of `/var/tmp/⟨activation_id⟩-consume-evidence/journal`.
  3. **OC-3.** That journal contains a `consumed` line.

  The route is **unavailable** in every other state. In particular it is
  unavailable while the unit is `activating`, in every sub-state, including
  `start-pre` (CP running) and `start` (CP finished, `ExecStart=` not yet
  executed). It is also unavailable while the unit is `deactivating`,
  `inactive` or `failed`, while the `InvocationID` is empty or different, and
  while the journal is absent, unreadable or has no `consumed` line.
* **How the executor establishes it.** Immediately before issuing the
  literal, the executor runs, without `sudo`,
  `systemctl show -p ActiveState,InvocationID rp11-capture-pass-a.service` and
  reads the consume journal (`root:root` `0644`, in a `0755` directory, so
  readable by `ubuntu`). Both are reads. Neither needs a new privilege, and
  neither is a new command literal of A-2.
* **Why "durable" needs no further check.** A `consumed` line that the
  executor can read, together with OC-1 and OC-2, is durable by construction.
  CQ-6 writes and `fsync`s `consumed` before CQ-7 exits `0`. PID 1 executes
  `ExecStart=` only after that exit (PO-21 (o)). The unit reaches `active` only
  after `ExecStart=`'s `execve` (`Type=exec`). And the `ExecStart=` process
  carries CP's `INVOCATION_ID` (PO-21 (n), AR-6). So OC-1 and OC-2 can hold
  together only after CQ-6's `fsync` returned.
* **A hung consume step.** The executor does not interrupt it. It is ended by
  the unit's start timeout, which A-2 pins and AP-0 requires to be finite and
  at least ⌈PO-11 (d) bound / 1,000⌉ + 30 seconds (AR-4). If the recorded
  timeout is infinite or shorter, `ACT` is INVALID RUN and no grant is linked.
  Expiry ends the attempt `failed` (PO-21 (u)), which changes τ and so engages
  SB-2 (§4.2.5-R5 (f), Lemma 2).
* **What it is.** Unchanged: it terminates the capture mechanism of a running
  pass, which is a §9.5.3 interruption. No X-3 finalization attempt follows,
  and the capture root is retained, read-only. Because the route is never
  available during `start-pre`, a route (iii-a) `stop` never ends CP. The
  sentence of §4.2.5-R4 (e) "If the `stop` lands during `start-pre`, it ends CP
  and no pass runs" no longer describes route (iii-a). A `stop` during
  `start-pre` is not route (iii-a). It is a root act outside A-2 ((d), (f)).
* **What follows.** HL observes the unit's end within Δ and decides under the
  lock with the reasons of §4.2.5-R5 (g), unchanged: `pass-ended` if the
  capture root exists, otherwise `pass-failed-early` when `ExecStart=` is shown
  to have been forked, otherwise `start-failed-before-exec`. CL then removes
  `pass-a.json` and writes the records. No grant is involved at any point.
* **If the condition cannot be established for a running pass.** For example,
  the consume journal cannot be read. The route is then unavailable. The pass
  continues **without a grant** (§4.2.5-R4 (i)) until it ends, or until a
  separately authorized root act ends it. That is CX-3's interval. It is a
  liveness limit, not a grant defect.
* **Privilege.** Unchanged. Under OH-D-6 `ubuntu` already has unrestricted
  `sudo`, so the route adds no privilege. A-2 pins the literal, its SHA-256
  and, from D3-R6, the condition ((g), A-2).

##### (c) Lemma R6: every route (iii-a) `stop` lands after the claim

**Lemma R6.** If the executor observed OC-1, OC-2 and OC-3 for activation X,
then SB-1's blocking point for X has already been passed, and it stays passed
for the rest of the activation.

*Proof.* The consume journal is created inside the claim directory, by
`openat(cfd, "journal", …)` after `mkdirat` returned `0` (§4.2.5-R5 (d)). So a
readable journal, with or without `consumed`, implies the claim exists. The
claim is never removed by any procedure of this design (§4.2.5-R5 (d),
"Removal"). `ubuntu` cannot remove or rename it (sticky `/var/tmp`,
PO-20 (h)), and OS-8 prevents ageing within the activation. A kernel boot ends
the activation (M-B). So once true, "the claim exists" stays true for X.

**Consequence: the read and the `stop` need not be atomic.** Between the
executor's read and its `stop`, the pass may end and a later attempt A_k may
begin. The `stop` may then land on A_k, even during A_k's `start-pre`. A_k
still finds the claim at CQ-2 (`EEXIST`, `consume-repeated`) and exits with
nothing touched. Every attempt after it is refused in the same way, whatever
state the `stop` leaves. So **no route (iii-a) `stop` can produce an attempt
that ends in the pre-barrier class**, which is the only class in which SB-1 is
absent (§4.2.5-R5 (b)).

##### (d) The authorized path set 𝒜

Contract OSA is a statement about everything that A-2 permits, and about every
event that this design treats as possible without anyone acting against the
authority. 𝒜 is exactly that set:

| Part of 𝒜 | Members |
|---|---|
| **acts A-2 permits** | `ACT` and its holder (AM-0 … AM-3, `hold-start`, HL); the operator's `start` of the capture unit, only after `hold-start` and while the holder is `active`; CP, as the unit's fixed root pre-start step; route (iii-a) under (b); CL in every trigger (`stop-post`, `backstop`, `attest`), GP-R3 and the backstop; reads, such as `systemctl show`, PK and journal reads |
| **events in scope** | K, a kill of CP for any cause, including the kernel OOM killer; T, the start timeout; failure to fork or execute the pre-start step; C, lock contention; M, malformed or missing input; L, cleanup running or finished; ES, a lost session; EH, the holder's death or lease expiry; EP, the end or death of the pass; EC, a CL's death; EU, an unclean kernel boot |
| **requests the mechanism refuses** | a `stop` or other non-`start` verb requested by `ubuntu` without authentication, which Polkit refuses (PO-11 (g); AV-1's negative control) |

**Outside 𝒜** are root acts that A-2 does not permit, of the SL-1 kind
(§4.2.5-R2 (l)). For this contract the relevant ones are:

* **a `stop` job on the capture unit that is not route (iii-a)**, in
  particular a root `stop` while the unit is `activating`. After OS-6 this is
  not a narrowing of an authorized route. The decided route simply does not
  include it;
* **an orderly transition (EO)** — `reboot`, `poweroff`, `halt`, `kexec` or a
  userspace-only restart — while the activation is unterminated. A-2's pinned
  sentence forbids it (§4.2.5-R2 (c)). If the hosting platform triggers one
  regardless, for example through an ACPI power event, it is outside the
  authority in the same way;
* root's other acts already listed under SL-1: killing the holder or the
  backstop, writing a rule, removing evidence, or forcing a transition that
  skips unit stop.

A root **kill** of CP or of the pre-start process, with no stop job, is not
special. It ends the attempt `failed` (PO-21 (u)), so SB-2 refuses every later
attempt. OSA holds for it even though it is outside 𝒜.

**Where a stop job on the capture unit can come from.** A stop job during
`start-pre` is the only way an attempt can end `inactive` (§4.2.5-R5 (f),
Lemma 2), so the contract needs every source of one:

1. **An explicit `stop` request.** From `ubuntu` without authentication, it is
   refused (PO-11 (g)). From root, it is route (iii-a) only under (b), and by
   Lemma R6 that lands after the claim. Any other root `stop` is outside 𝒜.
2. **A stop propagated by a dependency.** The reviewed unit has no
   `Requires=`, `BindsTo=`, `PartOf=` or `Conflicts=` line. The holder and the
   backstop have no `Requires=`, `BindsTo=`, `After=` or `PropagatesStopTo=`
   relation to it (§4.2.5-R3 (d), "Unit relationship and ordering"). The loaded
   dependency properties, including reverse ones, are part of the compared
   property list of §4.3.3 (a), because neither V nor E excludes them, so any
   such relation present at H-1 is in the reviewed baseline, and one added
   later is a root act that H-2 and AP-0 detect. The only implicit relation is
   the default `Conflicts=shutdown.target`, which acts only in an orderly
   transition (item 3).
3. **An orderly transition (EO).** It is outside 𝒜, as above.

So, **within 𝒜, no stop job reaches the capture unit during `start-pre`
before the claim**. §17.9 asks Codex to confirm item 2's reading of the
reviewed baseline.

##### (e) Contract OSA, as scoped by D3-R6

**Contract OSA (D3-R6).** For an activation X, and for every sequence of acts
and events drawn from 𝒜:

1. no attempt other than A₁ executes `ExecStart=` while any object of X
   exists;
2. A₁ executes it only if its CP exits `0`, at CQ-7;
3. this holds whether A₁ failed identified or unidentified, and whether a
   later attempt is requested by `ubuntu` under the grant or by root; and
4. no failed attempt is ever recorded or claimed as a pass.

**OSA has no exception within 𝒜.** CX-4 is not an exception to it. CX-4 needs
an act outside 𝒜 ((f)). Item 3 keeps D3-R5's stronger wording: a later
**start** by root, which is itself outside A-2, is still refused, because it
runs the same CP (PO-21 (n)) and meets the same barriers.

**Proof.** §4.2.5-R5 (f) stands, with its third case re-read:

* **A₁ reached CQ-2's `mkdirat`.** SB-1 alone suffices. Unchanged.
* **A₁ is in the pre-barrier class and ended `failed`.** SB-2 suffices
  (Lemma 2). Unchanged. It covers a CP that never ran, CQ-0 and CQ-1 failures,
  a busy lock, a kill, a failed `mkdirat` and a **hung CP ended by the start
  timeout**, which is now the only way a stuck consume step ends within 𝒜.
* **A₁ is in the pre-barrier class and ended `inactive`.** That needs a stop
  job during A₁'s `start-pre` before its `mkdirat` returned (Lemma 2). By (d),
  no member of 𝒜 produces one: an unauthenticated `ubuntu` `stop` is refused,
  route (iii-a) lands only after the claim (Lemma R6), and no dependency
  propagates one. **So within 𝒜 this case does not occur.** D3-R5's
  sub-analysis of it (τ above τ₀, τ₀ ≠ 0, the unload) stays correct, and it
  now describes how far SB-2 still reaches outside 𝒜 ((f)).

Proofs 2, 4 and SB-3's independent bound are §4.2.5-R5 (f), unchanged.

**Why this follows from the decision, and is not assumed.** D3-R5 obtained the
same case split by applying OS-6 as its own refinement. D3-R6 obtains it from
the R6 authority, which makes route (iii-a)'s condition OC-1 ∧ OC-2 ∧ OC-3 and
excludes `activating` and `start-pre`. The authority boundary of OSA is
therefore the decided boundary of route (iii-a), and nothing in D3-R6 narrows
an authorized act further.

##### (f) What remains outside 𝒜, stated exactly

**CX-4 (re-stated by D3-R6): a stop job during the first attempt's
`start-pre`, from an act outside 𝒜.** It is a residual of the SL-1 kind. It
is **not** an authorized-path exception, and it is **not** made acceptable by
being outside 𝒜: it is stated so that Peter's eventual acceptance of the
design covers it knowingly.

* **Sources.** (a) A root `stop` that is not route (iii-a), issued while the
  first attempt is in `start-pre` before its claim's `mkdirat` returned, or at
  any time before `hold-start`. (b) An orderly transition (EO) that A-2
  forbids, in the same window.
* **Further conditions, all needed.** PO-21 (u) shows that a stop job during
  `start-pre` ends the attempt `inactive`. τ₀ was `0` at AM-0. The unit is
  unloaded before the next attempt. If any of these fails, SB-2 refuses every
  later attempt, as §4.2.5-R5 (f) shows.
* **Consequence.** SB-1 and SB-2 are then both absent, and the rule may still
  be live. A later start can run the pass. **No grant exists during or after
  that pass**, because its CP removes and PK-verifies the rule at CQ-3 and
  CQ-5 before `ExecStart=` (§4.2.5-R4 (i)). SB-3 still allows at most one CP to
  succeed. For source (b), the transition then ends in a kernel boot, which
  clears `/run` and so ends the activation (M-B). DF-1 (§4.2.5-R2 (l)) states
  the userspace-only restart, which A-2 also forbids.
* **Voidable, not voided.** If the PO-21 (u) citation shows that a stop job
  during `start-pre` ends the attempt `failed`, CX-4 is void. PO-21 (u) stays a
  proposed, version-bound obligation, and D3-R6 does not assume its answer.
* **Not closed in every case.** Closing CX-4 without PO-21 (u) would need a
  further unit or rule line, such as a start limit or a once-only rule, which
  changes OH-D-10 (A). That is **not** proposed.

**Correction to §4.2.5-R5 (f), the EO sentence.** D3-R5 said an orderly
transition "is covered without SB-2: it stops the holder too, CL removes the
rule and `pass-a.json`, and until then OS-4 refuses any attempt". That relied
on the holder being stopped before, or with, the capture unit. The design
fixes no such order. The holder and the capture unit have no ordering relation
((d) item 2), and a holder whose stop job is still queued is `active`, so
OS-4 would not refuse. D3-R6 therefore does not claim EO is covered by OS-4.
It places EO outside 𝒜, as A-2's pinned sentence already does, and names it as
CX-4's source (b). Whether systemd refuses a new start while a shutdown
transaction is queued is uncited, and the design does not rely on it. This is
the only change to a D3-R5 claim, and it widens no authority.

**CX-1, CX-2 and CX-3.** CX-1 and CX-2 stand as §4.2.5-R5 (k) narrowed them.
CX-3 stands, with route (iii-a) available only under (b). A pass whose
condition cannot be established is in CX-3's interval.

**SL-1, DF-1 and GU** (§4.2.5-R2 (l)) are unchanged.

##### (g) Reconciliation

Each item below states the governing D3-R6 reading. The earlier text is kept,
with a *(D3-R6)* note at each place.

* **D-1 (§4.7.1).** OS-6 is decided, so the Interruption sentence states the
  condition itself, not a reading of §4.2.5-R5 (h). The proposed D-1 wording
  is in §4.7.1's D3-R6 note. The D3-R5 one-attempt sentence is qualified to
  the authority boundary, so that the decision text does not claim more than
  OSA proves.
* **A-2 (§4.2.5-R2 (c), §4.2.5-R4 (g)).** The pinned consume sentence is
  replaced by: *"The capture unit's consume step is part of its start. It is
  mandatory and automatically authorized under this authority. The only
  interruption route is the executor's root literal pinned here, used only
  under the operational draft's §9.5.3, and only while the capture unit is
  `active`, its `InvocationID` equals the `run-start.invocation_id` of this
  activation's consume journal, and that journal contains a `consumed` line.
  The literal is not issued while the unit is `activating`, including during
  `start-pre`. A consume step that does not finish is ended only by the unit's
  start timeout pinned here."* The literal, its SHA-256, the executor and the
  start-timeout pin are unchanged.
* **Terminal causes (§4.2.5-R4 (d)).** Two rows are restated:

  | Cause | When the grant was disabled | Grant at the pass's terminal instant |
  |---|---|---|
  | interruption by route (iii-a), the executor's root `stop` under A-2, only under (b): the unit `active` with this activation's consumed invocation | CQ-3 and CQ-5, before `ExecStart=` | none. The interruption needs no grant. Later attempts are refused by SB-1 (Lemma R6) |
  | CP fails, refuses, is killed, or exceeds the start timeout (the only end of a hung CP within 𝒜), or the attempt fails before CP runs | not, or not verifiably | **no pass ran.** `ExecStart=` never executed (PO-21 (o)). A live rule is a pre-pass grant that HL's end and CL remove, rule first. Within 𝒜, every later start is refused by SB-1 or SB-2 (contract OSA, (e)). A stop job during `start-pre` is outside 𝒜 (CX-4) |

  The other rows stand.
* **Boundary table (§4.2.5-R5 (i)).** Event **S** is re-defined as *a stop
  job during `start-pre`*. Route (iii-a) is never one (OS-6), so S is always
  outside 𝒜: a root `stop` or a forbidden orderly transition. The S column's
  entries stand as descriptions of what happens if it occurs. "SB-2, or CX-4"
  in the first rows now reads "SB-2, or, outside 𝒜, CX-4". Every other column
  is within 𝒜, and in every one of its cells later attempts are refused by SB-1
  or SB-2 with no exception.
* **States (§4.2.5-R4 (g) (j), as amended by §4.2.5-R5 (j)).** ST-2.c: no
  route (iii-a) `stop` can occur in it. Its exits are CQ-7 (to ST-3), a CP
  failure, the start timeout, a kill, or, outside 𝒜, a stop job. ST-2.f is
  entered by "a CP failure, a start-timeout expiry or any ended attempt
  without `ExecStart=`". The words "or a `stop` during `start-pre`" in the
  D3-R4 row name an act outside 𝒜. ST-3: route (iii-a) is available in it
  only while OC-1 … OC-3 hold.
* **Proof item 7 (§4.2.5-R4 (i), as replaced by §4.2.5-R5 (j)).** "with CX-4
  as the only exception" reads: *"for every sequence within the authorized
  path set 𝒜 of §4.2.5-R6 (d), without exception. CX-4 requires an act
  outside 𝒜."*
* **HL reasons and CL classes (§4.2.5-R5 (g)).** Unchanged. After a route
  (iii-a) `stop` the claim always exists (Lemma R6), so CL classes the attempt
  `claimed`, never `unidentified` or `indeterminate`. The `capture-unloaded`
  reason and the `indeterminate` class can arise within 𝒜 only from an unload
  with no attempt, and otherwise only from an act outside 𝒜.
* **Records.** No schema change. A `deact` record already carries the
  consume journal, the unit's `Result` and both observations. The executor's
  pre-`stop` observation is operational-draft evidence (OH-S3), not a record
  field.
* **Proof obligations.** None is added, removed or re-worded. PO-21 (u) is
  still the obligation whose answer would void CX-4. It cannot be assumed
  before the citation gate (OH-S2).
* **Traceability, successors, tests and drills.** §4.7.3 and §4.7.4 carry
  D3-R6 tables. OH-S4 gains an evaluator test for OC-1 … OC-3 and splits
  test (21) into authorized and out-of-scope sequences. OH-S8b drills route
  (iii-a) only on a running pass, drills the start timeout on a hung test
  pre-start step, and keeps the root `stop` during `start-pre` only as a
  labelled observation of PO-21 (u) under its own authority, never as route
  (iii-a).

**`OH-H1-D3-R5-1`** is addressed in design by (a) … (g). It is **not** declared
closed. `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2`
stay open. Only Codex may recommend closure, and Peter Duscha retains
acceptance authority.

### 4.3 H-1 record and H-2 comparison (U-7)

#### 4.3.1 Identifier, serialization, destination and digest

* **Schema identifier:** `rp11-h1-record/1`.
* **Record identifier:** the H-1 `⟨RUN⟩` (§4.2.4).
* **Serialization:** exactly the repository's existing canonical JSON
  convention, `capture_contract.canonical_bytes`:

  ```text
  json.dumps(doc, sort_keys=True, separators=(",", ":"),
             ensure_ascii=True, allow_nan=False) + "\n"
  ```

  encoded as ASCII. The standard-library-only tool re-implements it, and a
  repository test asserts byte equality with `canonical_bytes` for a corpus of
  records.
* **Value types:** strings, integers, booleans, lists and objects only. There
  are no floats and no `null`. Absent facts use the explicit string
  `"absent"`.
* **Destination:** `/var/lib/freedom-blades-rp11/h1/⟨record_id⟩.json`,
  `root:root`, `0444`.
* **Digest:** `h1_record_sha256` is the SHA-256 of the file's exact bytes,
  including the final LF.
* **Return:** the H-1 handback quotes the record bytes verbatim, its digest
  and its length (OH-D-9).

#### 4.3.2 Schema (top level)

| Key | Content | In `baseline`? |
|---|---|---|
| `schema` | `"rp11-h1-record/1"` | — |
| `record_id` | `⟨RUN⟩` | no |
| `context` | `start_utc`, `end_utc`, `boot_id`, `assignment_path`, `assignment_sha256`, `authority_record_sha256`, `h0_record_sha256`, `journal_sha256` | no |
| `baseline` | the object H-2 compares (§4.3.4) | — |
| `baseline_sha256` | SHA-256 of `canonical_bytes(baseline)` | — |
| *(D3-R1)* `authority_limit` | the fixed OH-D-6 sentence of §4.2.5-R1 (b). It is a constant literal, so it is not a free-form string in the sense of the rule below | no |

*(D3-R1)* `context` also holds `journal_length`. `journal_sha256` and
`journal_length` cover the journal prefix ending with the line before
`v1-pass` (§4.2.4-R1 (e)), because the journal continues after the record is
written. The complete journal's digest and length are reported in the
handback.

`baseline` contains:

| Key | Content |
|---|---|
| `host` | `nodename`, `machine_id_sha256`, `architecture` (`x86_64`), `kernel_release` |
| `operator` | `user` = `ubuntu`, `uid`, `gid`, `groups`, a list of `[name, gid]` sorted by gid; `repository_root` = `/opt/freedom-blades/platform` with its `owner`, `group` and `mode` |
| `repository` | `commit`, `manifest_version`, `reviewed_digest`, `expected_sha256_file_sha256` (`6e87a542…a83625` today), `manifest_json_sha256` |
| `packages` | a sorted list of `[package, version, architecture]` for the fixed set of HF-07 |
| `citations` | for each of `D9-1`, `PO-8`, `PO-11`, `PO-12`, `PO-14`, `PO-15` and `PO-19`: `{record_path, record_sha256, cited_version}`, with `cited_version` equal to the package or kernel version above |
| `launcher` | the D2 §5.11 facts: `path`, `sha256` (= `expected_sha256` = the pass configuration's `launcher_sha256` at `ACT`), `size`, `owner`, `group`, `mode`, `setid` (false), `file_capability` (false), `posix_acl` (false), `dev`, `ino`, `parents`, `toolchain_lock_sha256`, `build_root_manifest_sha256`, `builds` (R-2 first party, R-5, and the §4.5 installation-source rebuild, each with `kernel_release`, `cpu_model` and `entry_mechanism`), `ha_variation` (from the accepted R5 record), `ic1_record_sha256`, `t_l10`, `t_l11` and `t_l12` verdicts, `xd_source_sha256` (`84598d06…038c97`), `xd_spelling_sha256` (`d2040648…ba67b66`), `agreed_stream_sha256` (`e1354c29…bf8e0`), `interpreter_version`, `d9_2` = `{review_path, review_sha256 (dd5a0833…c7d755d), decoder_sha256 (48594e41…c04e3e), stream_sha256 (eb9c584a…500b1a), agreement "332/332"}`, `installation_source_record_sha256` (§4.5) |
| `files` | for the bootstrap, the unit and the staged rule: `role`, `path`, `sha256`, `size`, `owner`, `group`, `mode`, `dev`, `ino`, `setid`, `file_capability`, `posix_acl` |
| `directories` | every §4.2.3 directory and every parent to `/`: `path`, `owner`, `group`, `mode`, `posix_acl`, `created_by_run`; *(D3-R1)* plus `dev` and `ino`, which `ACT` (AP-0, CL-6) and RB-1 use as identities |
| `absent` | `["/etc/freedom-blades-rp11/pass-a.json", "/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules"]` |
| `unit` | §4.3.3 (a) |
| `manager` | §4.3.3 (b) |
| `po17` | §4.3.6 |
| `po18` | `machine` (`x86_64`), `release`, `release_at_least_5_9` (true), compared numerically on the dotted prefix |

There is **no environment content.** No key may hold:

* a `NAME=VALUE` pair;
* a manager or process environment;
* a credential; or
* a free-form string other than paths, versions and digests.

A schema test rejects any extra key and any value that does not match its
declared grammar.

*(D3-R2.)* `absent` lists `/run/freedom-blades-rp11/pass-a.json`,
`/run/polkit-1/rules.d/50-freedom-blades-rp11.rules` and
`/etc/freedom-blades-rp11`, and the rule basename in every other rules
directory that PO-11 (f) lists. `files` gains the installed tool
(`rp11_h1.py`). `citations` gains PO-20 and PO-21.

#### 4.3.3 The complete effective property baseline

**(a) Unit.** The tool queries `systemctl show rp11-capture-pass-a.service`
with an **explicit** `--property=` list, never `--all`.

The list is **every property the installed systemd version documents for a
service unit**, taken from the PO-15 citation and committed as version-bound
data. The proposed file is
`infra/systemd/rp11-unit-properties.⟨systemd version⟩.txt`. Two sets are
removed from it:

* **V (volatile), not compared:**
  * every name ending in `Timestamp` or `TimestampMonotonic`;
  * `InvocationID`, `MainPID`, `ControlPID`, `ExecMainPID`, `ExecMainCode`,
    `ExecMainStatus`, `NRestarts`, `StatusText`, `StatusErrno`, `Result`;
  * the run-time accounting counters (`CPUUsageNSec`, `Memory*` current and
    peak values, `Tasks*` current values, `IP*Bytes`/`Packets`,
    `IO*Bytes`/`Operations`);
  * `ControlGroup` and `ControlGroupId`;
  * the `Effective*` run-time sets; and
  * *(D3-R1)* `ActiveState` and `SubState`. They are checked separately:
    V-1 requires `inactive`; H-2, AP-0 and CL-6 accept `inactive` or
    `failed` (a failed earlier pass leaves `failed`, and no step issues
    `reset-failed`) and record the value.

  The exact list is finalized from the same citation and committed beside the
  property list.
* **E (environment-bearing), never queried:** `Environment`,
  `SetCredential`, `SetCredentialEncrypted`, `LogExtraFields` and
  `StandardInputData`. Their emptiness is **derived, not read**: the fragment
  digest equals the reviewed bytes, which set none of them; `DropInPaths` is
  empty; and `NeedDaemonReload=no`. Run-time properties appear as drop-ins in
  `DropInPaths`, which PO-15 must show.

The following are **queried and compared**:

* `ExecStart` (normalized below);
* `User`, `Group`, `SupplementaryGroups`, `DynamicUser`, `NoNewPrivileges`,
  `PAMName` (required empty), `PassEnvironment` and `UnsetEnvironment`
  (names only, required empty), `EnvironmentFiles` (required empty);
* `WorkingDirectory`, `RootDirectory`, `UMask`, `StandardInput`,
  `StandardOutput`, `StandardError`;
* every `Limit*`;
* every sandboxing and confinement property (`Protect*`, `Private*`,
  `Restrict*`, `SystemCall*`, `CapabilityBoundingSet`,
  `AmbientCapabilities`, `SecureBits`, `ReadWritePaths`, `ReadOnlyPaths`,
  `InaccessiblePaths`, `BindPaths`, `BindReadOnlyPaths`,
  `TemporaryFileSystem`, `MountFlags`, `Personality`,
  `MemoryDenyWriteExecute`, `LockPersonality`); and
* the scheduling, OOM, slice, delegation, timeout, restart and kill
  properties, plus `ExecStartPre`, `ExecStartPost`, `ExecCondition`,
  `ExecStop`, `ExecStopPost` and `ExecReload` (each required empty).

**`ExecStart` normalization.** `systemctl show` prints `ExecStart` with
run-time fields (`start_time`, `stop_time`, `pid`, `code`, `status`). The tool
parses the printed structure and records only `path`, `argv[]` and the
flag fields (`ignore_errors` and its successors in the cited version). A parse
failure is a stop. This keeps H-2 stable after a previous pass has run.

*(D3-R4.)* `ExecStartPre` moves from the "each required empty" list to the
compared list. It must hold exactly the one CP entry, normalized as
`ExecStart` is, with the privileged (`+`) flag as its only flag. The unit's
start timeout is also the value that AP-0 checks. §4.2.5-R4 (h) gives the
exact values.

**(b) Manager.** The tool queries `systemctl show` (the manager object) with an
explicit list taken from the same citation:

* every `Default*` property;
* `Version`, `Features`, `Architecture`, `UnitPath`, `ConfirmSpawn` and
  `ServiceWatchdogs`.

**No name containing `Environment` is ever queried.** The manager's global
environment is neither inspected nor recorded (C11 §4.4.3.5).

**Value encoding.** Each value is the exact bytes after the first `=`,
decoded as strict UTF-8. Any decoding failure is a stop. A property the
installed manager does not report is a stop, because the version-bound list
and the installed version then disagree.

#### 4.3.4 H-2 comparison and A-2 binding

* **H-2** (`rp11-h2-record/1`, the same serialization) runs **unprivileged**.
  It recomputes `baseline` by the same code. It stops on any byte difference
  between `canonical_bytes(baseline_H2)` and `canonical_bytes(baseline_H1)`,
  that is, on `baseline_sha256` inequality. On a stop it reports the first
  differing key path. It also records the current `boot_id`.
* **A-2** (the pass authorization) names `h1_record_id`, `h1_record_sha256`,
  the H-2 record's SHA-256, the `boot_id` H-2 observed, and `pass-a.json`'s
  SHA-256.
* **Order (proposed; OH-D-7):** H-2 → A-2 → `ACT` → H-2b (the unit and
  manager `baseline` re-checked after `ACT`, compared with H-2) → the
  operator's `start`.
* *(D3-R1, amended order, OH-D-7 decided):* H-2 → A-2 → `ACT` (its AV-1
  includes H-2b, §4.2.5-R1 (d)) → `ACT` PASS established by the `act` record →
  the operator's `start` → the pass's terminal state → `DEACT` → verified ST-1.
  A failure anywhere from AM-0 on runs the automatic cleanup CL. A-2 also pins
  everything listed in §4.2.5-R1 (b). H-2 stays immediately before A-2, and
  AP-0 repeats its `baseline` equality immediately before the first activation
  mutation, so C11's "H-2 immediately before each pass" is preserved.
* *(D3-R2, amended order):* H-2 → A-2 → AP-0, AP-1 → AP-2 (the holder) → AM-0
  → AK-1 (the backstop, before any activation file) → AM-1 … AV-1 (with H-2b) →
  AM-3 (`ACT` PASS) → the operator's `start` → the pass's terminal state → HL
  detects it within Δ → the holder's end → CL (`stop-post`), the rule first →
  verified ST-1 → the backstop disarms (BS-2). A death at any point triggers CL
  through `ExecStopPost=`, with the backstop as retry. An unclean kernel boot
  clears both files, and attestation records it (§4.2.5-R2 (i)). A failure
  from AM-0 on never waits for an actor.
* *(D3-R3)* In the D3-R2 order, the steps "the pass's terminal state → HL
  detects it within Δ → the holder's end → CL (`stop-post`), the rule first"
  leave the grant live after the pass (`OH-H1-D3-R2-1`). They remain the
  order in which `pass-a.json` and the records are cleaned up, but they **do
  not establish OH-D-7's post-pass boundary**. Under OH-D-10 (A), not adopted,
  the order would be: … → AM-3 (`ACT` PASS) → the operator's `start` (Polkit
  decides) → CP, the grant consumed and PK *not authorized* → `ExecStart=` →
  the pass → its terminal state, with no grant → the holder's end → CL for
  `pass-a.json` and the records (§4.2.5-R3 (d)).
* *(D3-R4, adopted order; supersedes the two bullets above where they
  differ):* H-2 → A-2 → AP-0, AP-1 → AP-2 (the holder) → AM-0 → AK-1 → AM-1 …
  AV-1 (with H-2b and the PK `stop` negative control) → AM-3 (`ACT` PASS) →
  `hold-start`, then the lock is released → the operator's `start` (Polkit
  decides once) → CP: the lock, the checks, the rule removed, PK *not
  authorized* → `ExecStart=` → the pass → its terminal state, with no grant →
  HL observes it → the holder's end → CL (`stop-post`) for `pass-a.json`, the
  directories and the records → verified ST-1 → the backstop disarms. A hung
  pass is ended only by route (iii-a). A failure of CP ends the start with no
  pass, and HL's `start-failed-before-exec` leads to the same CL
  (§4.2.5-R4).

* *(D3-R5)* In the adopted order, AM-0 also records τ₀, and `hold-start` first
  re-checks it (OS-1, OS-7). CP's part becomes: the lock → the claim → the rule
  removed → the checks, including OS-1 and OS-4 → PK *not authorized* →
  `consumed` (§4.2.5-R5 (e)). HL ends only under the lock (OS-5).

* *(D3-R6)* "A hung pass is ended only by route (iii-a)" is read with the
  decided OS-6: only while the unit is `active` with this activation's
  consumed invocation (§4.2.5-R6 (b)). A hung CP is ended by the start
  timeout, never by route (iii-a).

#### 4.3.5 Pass-configuration and bootstrap additions (for slice I-6)

`pass-a.json` gains these fields:

* `h1_record_sha256`;
* `activation_id`; and
* `boot_id`, the boot ID A-2 pins.

*(D3-R1)* A-2 quotes the complete document, and `ACT` publishes exactly
`canonical_bytes(doc)` (§4.2.5-R1 (c)). It never edits a field.

*(D3-R2)* The document is published at `/run/freedom-blades-rp11/pass-a.json`
(§4.2.5-R2 (b)), and the bootstrap and the client hook read it there (§4.7.2).
The launcher image is unaffected. Its only compiled path is the bootstrap's
(`tools/phase_5_0_evidence/rp11_launch.py`, `EXECVE_ARGV`).

The bootstrap gains two **diagnostic** refusals before X-1, in the style of
C11 §6.5:

| Refusal | Condition |
|---|---|
| `entry-h1-record-mismatch` | the record at its fixed path has a different digest |
| `entry-activation-stale` | `/proc/sys/kernel/random/boot_id` ≠ `boot_id` |

Neither is credited as prevention.

#### 4.3.6 PO-17 — mechanical `binfmt_misc` matching algorithm

Input: the bytes `I` of the image, read once. At P-0 these are the source
bytes; at V-1 and H-2 they are the installed file.

1. Read `/proc/self/mountinfo`. If no entry has mount point
   `/proc/sys/fs/binfmt_misc` and filesystem type `binfmt_misc`, record
   `mounted: false`. **PO-17 holds**, subject to D9-1's citation that an
   unmounted `binfmt_misc` in the initial namespace has no effective
   registration for the cited kernel series. If D9-1 cannot cite that, treat
   unmounted as a stop.
2. Otherwise read `status`, which must be exactly `enabled\n` or
   `disabled\n`; anything else is a stop. Record it.
3. List the directory. Exclude exactly `register` and `status`. Sort the
   remaining names bytewise. Read each entry file. Its grammar, from the cited
   kernel's `fs/binfmt_misc.c`, is:
   * first line `enabled` or `disabled`;
   * `interpreter ⟨path⟩`;
   * `flags: ⟨letters⟩`; then
   * either `offset ⟨n⟩`, `magic ⟨hex⟩` and optionally `mask ⟨hex⟩`
     (type **M**), or `extension .⟨ext⟩` (type **E**).

   Any line outside that grammar is a stop.
4. An entry **matches** if, and only if, the global status is `enabled`, the
   entry is `enabled`, and one of the following holds:
   * **Type M.** Let `k = len(magic)`. If `offset + k > len(I)`, the entry
     **matches**. This is fail-closed: the kernel's buffer beyond the file's
     end is not image bytes. Otherwise it matches if
     `(I[offset+i] & mask[i]) == (magic[i] & mask[i])` for every `i < k`,
     with `mask[i] = 0xFF` when no mask is given.
   * **Type E.** The installed basename contains a `.` and the suffix after
     the last `.` equals `⟨ext⟩`. `rp11-launch` contains no `.`, so this is
     never true for the current path. The rule is stated so that a rename
     cannot silently bypass it.
5. **PO-17 holds** if, and only if, no entry matches.

The record lists, for every entry:

* `name`, `enabled`, `type`, `offset`, `magic_hex`, `mask_hex` (or
  `"absent"`), `extension` (or `"absent"`), `interpreter`, `flags` and
  `matches`;

and, for the whole check:

* `mounted`, `status`, `image_sha256` and `holds`.

The interpreter path is a configuration path, not environment content. No
entry is ever written, enabled or disabled.

### 4.4 H-0 host facts and citation order

#### 4.4.1 The read-only fact set (defined here; the executable H-0 assignment is OH-S1)

| # | Fact | Command class |
|---|---|---|
| HF-01 | nodename | C-ID: `uname -n` |
| HF-02 | `/etc/machine-id` SHA-256 only (MD-6) | C-DIG: `sha256sum /etc/machine-id` |
| HF-03 | `ubuntu`: UID, primary GID, supplementary groups; home directory and shell path from the password database | C-ID: `id ubuntu`, `getent passwd ubuntu`, `getent group` for each listed group |
| HF-04 | architecture, kernel release and version string | C-ID: `uname -m -r -v` |
| HF-05 | PID 1 is systemd | C-PROC: read `/proc/1/comm`; `systemctl --version` |
| HF-06 | systemd, polkit, glibc and CPython versions | C-VER/C-PKG |
| HF-07 | package versions and provenance for `systemd`, `systemd-sysv`, `libsystemd0`, `libsystemd-shared` (if packaged separately), `polkitd`, `libpolkit-gobject-1-0`, `libc6`, `libc-bin`, `python3.12`, `python3.12-minimal`, `libpython3.12-minimal`, `libpython3.12-stdlib`, `coreutils`, `util-linux`, `sudo` and `dbus`. The final list is fixed by the H-0 assignment | C-PKG: `dpkg-query -W -f`; `dpkg -S` for `/usr/bin/python3.12`, the dynamic loader, `/usr/lib/systemd/systemd-executor` (if present), `/usr/lib/polkit-1/polkitd`; `dpkg --verify` for these packages; `apt-cache policy` (local lists only, **no** `apt update`) |
| HF-08 | `/usr/bin/python3.12`: owner, mode, real path, SHA-256; version and `sys.flags` under `-I -S` | C-STAT, C-DIG; `/usr/bin/python3.12 -I -S -c` printing `sys.version`, `sys.flags.isolated`, `sys.flags.no_site`, `sys.prefix`, `sys.path` |
| HF-09 | dynamic-loader inputs (U-9): the real path and SHA-256 of `/lib64/ld-linux-x86-64.so.2`; `/etc/ld.so.preload` present or absent (and, if present, owner, mode and digest only); the SHA-256, owner and mode of `/etc/ld.so.cache`; the names and digests of `/etc/ld.so.conf` and `/etc/ld.so.conf.d/*` | C-STAT, C-DIG |
| HF-10 | required binaries present, root-owned and not group- or world-writable: `/usr/bin/systemctl`, `/usr/bin/python3.12`, `/usr/bin/sha256sum`, `/usr/bin/stat`, `/usr/bin/sudo`, `/usr/bin/journalctl`, `/usr/bin/dpkg-query` | C-STAT |
| HF-11 | every §4.2.3 path and parent: present or absent, type, owner, group, mode, extended-attribute **names** | C-STAT (Python `os.lstat` and `os.listxattr`) |
| HF-12 | polkit rules directories (`/etc/polkit-1/rules.d`, `/usr/share/polkit-1/rules.d`, `/run/polkit-1/rules.d`, `/usr/local/share/polkit-1/rules.d`): owner and mode; file names and SHA-256 where readable without privilege, otherwise `unreadable` | C-STAT, C-DIG |
| HF-13 | unit and drop-in collisions: `systemctl show rp11-capture-pass-a.service -p LoadState -p FragmentPath -p DropInPaths`; `systemd-analyze unit-paths`; names under every `⟨unit-path⟩/rp11-capture-pass-a.service.d/` and `⟨unit-path⟩/service.d/` | C-SDQ, C-STAT |
| HF-14 | `binfmt_misc`: `/proc/self/mountinfo` entry; `status`; every entry's file, read-only (§4.3.6 grammar) | C-PROC |
| HF-15 | filesystem type, mount options and capacity of `/`, `/usr/local`, `/etc`, `/var/lib` and `/var/tmp`, and of the proposed capture-root parent if OH-D-3(a) *(D3-R1: OH-D-3 decided (a); always recorded)* | C-STAT: `findmnt --target`, `df --output` |
| HF-16 | the manager `Default*` values, by the HF-07-version property list where already cited; otherwise deferred to H-1 | C-SDQ, explicit `-p` only |
| HF-17 | automatic-update configuration that could change HF-07 (the `apt-daily*` and `unattended-upgrades` timers' presence and state) | C-SDQ: `systemctl list-timers --all --no-legend` (names and next-run fields only) |
| HF-18 | the operator client's presence, if OH-D-2 asks for it *(D3-R1: OH-D-2 decided; the interactive client's presence is recorded as a fact and is never satisfied by installing one)* | C-STAT on the named path only |
| *(D3-R1)* HF-19 | `systemd-tmpfiles` ageing that applies to `/var/tmp`, where the H-1, `ACT`, `DEACT` and RB-1 journals live: the SHA-256 of `/usr/lib/tmpfiles.d/tmp.conf` and of every `/etc/tmpfiles.d/*.conf`, and their lines naming `/var/tmp` | C-STAT, C-DIG; reading named configuration files |

*(D3-R1)* Amendments to the rows above:

* **HF-07** adds the package that owns `/usr/bin/pkcheck` (`dpkg -S`).
* **HF-10** adds `/usr/bin/pkcheck` and `/usr/bin/sleep`.
* **HF-15** adds the filesystem type and mount options of every directory that
  receives a publication or a temporary tree: `/usr/local/libexec` (or
  `/usr/local`), `/etc`, `/etc/systemd/system`, `/etc/polkit-1/rules.d` and
  `/var/lib`. PO-20 (§4.4.2a) is cited for exactly these types.
* **HF-11** records `(dev, ino)` for every parent. §4.2.4-R1's invariant R
  compares them.

*(D3-R2)* Further amendments to HF-10, HF-11, HF-15 and HF-19, and the new
HF-20, are in §4.4.2b.

**Permitted command classes:**

* **C-ID:** `uname`, `id`, `getent`;
* **C-PROC:** reads of named `/proc` files only;
* **C-STAT:** `stat`, `findmnt`, `df`, and Python `os.lstat`, `os.listxattr`
  and `os.listdir` on named paths;
* **C-DIG:** `sha256sum` of named root-owned system files;
* **C-VER:** `--version` of `systemctl`, and `/usr/bin/python3.12 -I -S -c`
  with a fixed literal;
* **C-PKG:** `dpkg-query`, `dpkg -S`, `dpkg --verify`, `apt-cache policy`;
* **C-SDQ:** `systemctl show` with explicit `-p` lists, `systemctl --version`,
  `systemd-analyze unit-paths`, `systemctl list-timers`.

**Prohibited in H-0:**

* `sudo` or any privilege;
* any write except the H-0 run's own evidence directory
  (`/var/tmp/⟨RUN0⟩-h0-evidence`, `0700`);
* `systemctl` verbs other than `show`, `--version` and `list-timers`, and in
  particular `show-environment`;
* `env`, `printenv`, `/proc/*/environ`;
* any secret, key, credential, `known_hosts`, SSH configuration, `sudoers`,
  home-directory content, application data, database or `psql`;
* `/opt/freedom-blades/platform` contents (its own `stat` is HF-03/HF-11);
* the retained `/var/tmp/p5-r5-fresh-*` paths, including any listing of them;
* network access, including `apt update`;
* `/tmp`.

#### 4.4.2 PO-19 — glibc and dynamic-loader proof obligation (U-9)

**PO-19 (new).** For the glibc version that HF-07 records:

* (a) when `/usr/bin/python3.12` is started with exactly
  `{INVOCATION_ID, LC_ALL=C, PATH=/usr/bin}` and is not set-ID, the dynamic
  loader takes its library search inputs only from:
  * the executable's `DT_RUNPATH`/`DT_RPATH`, if any;
  * `/etc/ld.so.cache`;
  * the built-in trusted directories, and their `glibc-hwcaps`
    subdirectories (AB-4); and
  * `/etc/ld.so.preload`, if present;
* (b) none of `INVOCATION_ID`, `LC_ALL` or `PATH` is a loader or tunable input
  (the `LD_*` and `GLIBC_TUNABLES` namespaces);
* (c) `LC_ALL=C` selects glibc's built-in C locale without opening a locale
  archive, and if `gconv` modules may still be opened, they are named; and
* (d) every file in (a) and (c) is root-owned on the host, as HF-09
  records.

**Discharged by** a citation of that glibc version's `elf/rtld.c`,
`elf/dl-load.c`, `elf/dl-cache.c`, the tunables sources and the locale
loading path, read-only under U-10. HF-09 supplies the facts for (d).

**Required by H-1 and H-2:** the citation is accepted and its version equals
the installed `libc6`. Otherwise H-1 is INVALID RUN.

#### 4.4.2a PO-20 — filesystem and system-call semantics of the publication protocol *(D3-R1, new)*

**PO-20.** For the HF-04 kernel series, the HF-15 filesystem types and the
HF-07 `libc6` version:

* (a) `open` with `O_TMPFILE` creates an unnamed regular file in the named
  directory, and without `O_EXCL` it may be linked by
  `linkat(AT_FDCWD, "/proc/self/fd/N", dirfd, name, AT_SYMLINK_FOLLOW)`. If the
  process ends, the host crashes or power is lost before the link, the inode
  is freed and no name remains.
* (b) `linkat` fails with `EEXIST` and never replaces an existing name.
* (c) `renameat2` with `RENAME_NOREPLACE` is supported for directories, is
  atomic, fails with `EEXIST` rather than replacing, and keeps the inode
  number. glibc exports `renameat2`.
* (d) `fsync` on a regular file makes its data and metadata durable, and
  `fsync` on an `O_RDONLY` directory descriptor makes that directory's entries
  durable, including those created by `linkat`, `renameat2`, `mkdirat` and
  `unlinkat`.
* (e) `st_ino` is stable for a live inode, and no two live objects on one
  device share it.
* (f) `flock` on an `O_RDONLY` directory descriptor gives an exclusive advisory
  lock that is released when the process ends.

**Discharged by** a citation of the kernel's `fs/namei.c`, `fs/open.c` and the
named filesystems' sources and documentation, and of glibc's `renameat2`
wrapper, read-only under U-10. **Required by H-1, `ACT`, `DEACT` and RB-1:**
the accepted citation's kernel series and filesystem types equal the observed
ones. Otherwise the run is INVALID RUN at P-0 or AP-0. A refutation returns the
protocol to design review. It is never worked around at run time.

**PO-11 extensions** *(D3-R1)*, in addition to (b) and (c):

* (d) after a rules file is created by `linkat` in, or removed by `unlinkat`
  from, `/etc/polkit-1/rules.d`, polkitd reloads its rules within a cited
  bound. That bound becomes A-2's PO-11(d) value. If no bound can be cited,
  `ACT` and `DEACT` return to design review rather than polling without a
  bound; and
* (e) `pkcheck`'s exit statuses and their mapping to decisions, and whether
  `--detail` from an unprivileged caller reaches the rules. PK runs as root in
  either case (§4.2.5-R1 (f)).

#### 4.4.2b PO-21, and the PO-11 and PO-20 extensions for supervised, boot-scoped activation *(D3-R2, new)*

Every host behaviour that §4.2.5-R2 relies on is listed here, version-bound and
paired with the H-0 fact that fixes its version or state. **Fail-closed rule:**
`ACT` (AP-0) is INVALID RUN unless every item below is accepted for the
observed versions. A refuted item returns the activation design to review. It
is never worked around at run time, and no fallback to a persistent rule
location exists.

**PO-11 (f)**, for the HF-07 polkit version:

* (i) `/run/polkit-1/rules.d` is in polkitd's rules search path. The citation
  gives the complete list of rules directories and the precedence between
  equal basenames in different directories;
* (ii) whether polkitd loads a rules file within the PO-11 (d) bound when
  `/run/polkit-1/rules.d`, or `/run/polkit-1`, was created after polkitd
  started. If this cannot be cited, AP-0 requires the directory to exist, and
  `ACT` never builds tree **R**;
* (iii) PO-11 (d)'s bound applies to a `linkat` into, and an `unlinkat` from,
  `/run/polkit-1/rules.d`; and
* (iv) polkitd holds no rule across its own restart or a kernel boot other than
  what it reads from the rules directories when it starts.

**PO-20 (g)**, for the HF-04 kernel and the HF-15 type of `/run`: PO-20 (a) …
(f) hold on `tmpfs`, including `O_TMPFILE`, `linkat` with `AT_SYMLINK_FOLLOW`
and `renameat2` with `RENAME_NOREPLACE`; `st_ino` is unique among live `tmpfs`
objects; and a `tmpfs` mount's contents do not survive a kernel boot, including
`kexec`. `fsync` on `tmpfs` may be a no-op. No claim depends on it, because no
`tmpfs` object outlives its kernel. The identities are made durable in the
journal on `/var/tmp`, which PO-20 (d) covers.

**PO-21 (new)**, for the HF-07 systemd version:

* (a) a unit created by `systemd-run --system` without `--scope` is a system
  service, supervised by PID 1 in its own control group. It is not ended by
  the end of a login session, by logind's `KillUserProcesses=` or by a hang-up
  of the invoking terminal;
* (b) the service's environment is PID 1's, plus nothing from the caller
  unless `--setenv`, `-E` or an `Environment=` property is given (none is).
  The argument grammar of §4.2.5-R2 (e) and (f) leaves the command lines
  unchanged by specifier (`%`) and variable (`$`) expansion;
* (c) `ExecStopPost=` runs, as the unit's user (root), after the main process
  ends for **every** cause: exit `0`, a non-zero exit, any signal including
  `SIGKILL`, a kernel OOM kill, `RuntimeMaxSec=` expiry, `systemctl stop`, a
  failure to execute `ExecStart=`, and a stop issued by an orderly shutdown,
  reboot, `kexec` or userspace-only restart;
* (d) `RuntimeMaxSec=` ends the main process after the bound. The citation
  states whether time spent suspended counts;
* (e) how `TimeoutStopSec=` bounds the `ExecStopPost=` phase, and what happens
  when it expires;
* (f) `OOMScoreAdjust=-1000` excludes the unit's processes from the kernel's
  OOM selection;
* (g) transient units and their unit files exist only in the manager's memory
  and under `/run`. They do not survive a kernel boot. They do survive
  `daemon-reload` and `daemon-reexec`;
* (h) a transient service's default dependencies order its stop, including
  `ExecStopPost=`, before `shutdown.target` and before the unmounting of local
  filesystems. `/var/tmp` and `/var/lib` therefore stay writable while CL
  runs during an orderly transition;
* (i) whether the installed version can restart userspace while keeping the
  kernel (for example `systemctl soft-reboot`). If it can, the citation states
  whether `/run` and transient units survive, whether units are stopped first,
  and **every** condition under which a requested reboot becomes such a
  restart automatically. AP-0 and AM-0 require each such condition to be
  absent (DF-1);
* (j) `--on-active=` and `--on-unit-active=` timers fire at the stated period,
  with `AccuracySec=1s`. The citation states what happens when the period
  elapses while the service is still running, and that `systemctl stop` on
  the timer prevents later firings;
* (k) a unit that fails stays loaded with `ActiveState=failed` and its last
  `InvocationID` until `reset-failed` or its next start. Each start assigns a
  new `InvocationID`. An `inactive` unit may be unloaded, so HL never relies
  on an `inactive` unit's `InvocationID`;
* (l) `systemctl show` with explicit `-p` does not start, stop or change a
  unit; and
* (m) `systemd-run --unit=⟨name⟩` fails, and creates nothing, when a unit of
  that name is already loaded.

**Corresponding H-0 facts** (amendments to §4.4.1; read-only, unprivileged):

* **HF-10** adds `/usr/bin/systemd-run`.
* **HF-11** adds `/run`, `/run/polkit-1`, `/run/polkit-1/rules.d`,
  `/run/freedom-blades-rp11` and `/etc/freedom-blades-rp11`, each present or
  absent, with type, owner, group, mode, `(dev, ino)` and extended-attribute
  names.
* **HF-12** is unchanged. It already lists `/run/polkit-1/rules.d`. Its
  observation fixes whether that directory exists at boot on this host.
* **HF-15** adds `/run`: its filesystem type, which must be `tmpfs` for M-B,
  and its mount options.
* **HF-19** adds every `tmpfiles.d` line that names `/run/polkit-1` or
  `/run/freedom-blades-rp11`.
* **HF-20 (new):** the `LoadState` of `systemd-soft-reboot.service` and
  `soft-reboot.target`, and the presence of every path that PO-21 (i) names as
  a condition for an automatic userspace-only restart. The command class is
  C-SDQ with explicit `-p`, and C-STAT.

PO-21 joins the §4.4.3 citation order as a further step that may run in
parallel once PO-14 is accepted. PO-11 (f) belongs to step 4 and PO-20 (g) to
the PO-20 step.

*(D3-R3.)* GP-R3 (§4.2.5-R3 (e)) relies on no host behaviour beyond PO-20 (f)
and (g), PO-11 (d) and PO-21 (c) and (j), which are already listed. Two
amendments to this list are **conditional on OH-D-10 (A)** and are **not**
obligations of the current design: PO-21 (n) … (r) and PO-11 (g)
(§4.2.5-R3 (d)). R4 would add them, with their H-0 facts, only if Peter
selects Option A.

*(D3-R4.)* Peter selected Option A. **PO-21 (n) … (r) and PO-11 (g) are now
proof obligations of this design**, stated with their H-0 facts in
§4.2.5-R4 (j). They are proposed obligations, not observed host facts. The
fail-closed rule above applies to them: AP-0 is INVALID RUN, and no grant is
linked, unless each is accepted for the observed versions. PO-21 (n) adds the
`INVOCATION_ID` and execution-setting statements (AR-5, AR-6). PO-21 (o) adds
a `stop` during `start-pre` and independence from line order. **HF-16**
must include `DefaultTimeoutStartUSec`, which the `Default*` set already
covers, and H-1's `baseline` records the unit's own start timeout. PO-15 also
covers `ExecStartPre`'s printed form and its flag (§4.2.5-R4 (h)).

*(D3-R5.)* **PO-21 (s) … (v) and PO-20 (h)** are added as proof obligations of
this design (§4.2.5-R5 (j)). PO-21 (s) … (v) fix the start-history barrier SB-2
and the attempt model. PO-20 (h) fixes the claim's protection in `/var/tmp`.
**HF-11** adds `/var/tmp`. The fail-closed rule above applies: AP-0 is INVALID
RUN, and no grant is linked, unless each is accepted for the observed versions.

#### 4.4.3 Citation order after H-0 (OH-S2, under U-10)

1. **PO-14** with AD-7. If it is refuted for the installed systemd, LB-2S is
   withdrawn for that version, the sequence stops, and nothing below is
   started.
2. **PO-15**, which produces the version-bound property lists of §4.3.3.
3. **PO-8** (S-1 … S-10).
4. **PO-11**, with:
   * (b) no distribution rule grants `manage-units` to `ubuntu` without
     authentication, given HF-12; and
   * (c) the staging path is in no rules search directory.
5. **PO-12**.
6. **PO-19**.
7. **D9-1** for the HF-04 kernel series (AD-3, AD-4, AD-6, AD-8, AD-11,
   AD-12; the §4.3.6 unmounted case; the `binfmt_misc` entry grammar).

Steps 2 … 7 may run in parallel once step 1 is accepted.

*(D3-R1)* **PO-20** (§4.4.2a) joins as a further step that may also run in
parallel once step 1 is accepted. PO-11 (d) and (e) are part of step 4.

*(D3-R2)* **PO-21** (§4.4.2b) joins as a further parallel step after step 1.
PO-11 (f) is part of step 4, and PO-20 (g) is part of the PO-20 step.

*(D3-R4)* PO-21 (n) … (r) are part of the PO-21 step, and PO-11 (g) is part
of step 4. Any refuted item among PO-21 (n) … (r) and PO-11 (g) returns the
activation design to review, and no grant may be linked.

*(D3-R5)* PO-21 (s) … (v) are part of the PO-21 step, and PO-20 (h) is part of
the PO-20 step. A refuted item returns the activation design to review, and no
grant may be linked.

### 4.5 Launcher source and local build (U-4 on `oracle-test`)

#### 4.5.1 Source

The installation source is the output of **one separately authorized pinned
rebuild on `oracle-test`** (OH-S5). Retained R4/R5 output is evidence only
and is **never** read, copied, compared against or used as an installation
source.

#### 4.5.2 Procedure and verification

The rebuild reuses the accepted R5 machinery unchanged in substance:

* `provision.py`, `enter.py build` and `build.sh`;
* the same-invocation R-1 gate; and
* R-2 as the unprivileged build user.

It uses a fresh run identifier of the form
`p5-rp11-h1src-⟨UTC⟩-⟨8 hex⟩`, under `/var/tmp/⟨BRUN⟩-{checkout,index,cache,root,work,evidence}`.

Its controlled checkout reaches `oracle-test` by OH-D-1's transport. It is
verified **on `oracle-test`** file by file against an Appendix-A-style list of
digests pinned in the rebuild assignment, before provisioning. That is R5
step 4d's pattern.

*(D3-R1)* Under OH-D-1, as decided, that transport is direct retrieval of the
pinned commit from the canonical Git remote, run on `oracle-test` under its own
separate authority. It is never a copy from the workspace (production) host.
The retrieved commit identity is checked as well as the per-file digests.

The rebuild **passes** only if:

* (a) R-1's regenerated tree manifest is byte-equal to the committed
  `build-root.manifest`; and
* (b) the image, map, listing and `launch.s` digests equal
  `infra/rp11-launch/expected.sha256`.

Its record states equality of the image digest with four independent
bindings:

| Binding | Value |
|---|---|
| `expected.sha256`, row `rp11-launch` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` |
| manifest v31 `rp11_launch.expected_sha256` (manifest file `b9f03a47…ed14817a`) | the same |
| the accepted R5 record's S11 image digest (handback `6e94b7cb…1afb2c`) | the same |
| Codex's I-7 XD-11 image | the same |

The rebuild is **not** an R-5, and it reopens neither D9-3 nor D9-2. Its role
is to produce installation bytes. Its record is
`installation_source_record_sha256` in the H-1 record.

#### 4.5.3 Distinct paths and separate cleanup authority

| Class | Paths | Owner | Who may write | Who may delete |
|---|---|---|---|---|
| build and staging (source) | `/var/tmp/p5-rp11-h1src-*-*` | `ubuntu` | the rebuild run only | **separate cleanup authority**, after H-1 is accepted. Until then they are retained as installation-source evidence |
| installed | §4.2.3 | `root` | H-1, `ACT`, `DEACT`, RB-1 only | RB-1 / `DEACT` only (§4.6) |
| *(D3-R1)* installed, amended row | §4.2.3, except the record store | `root` | H-1 (trees L, V, E, the unit, the H-1 record); `ACT` (the two activation files and the `act` record); `DEACT` (its records) | **H-1 objects:** RB-1 only, under separate authority (OH-D-8), never automatically. **Activation files:** CL, automatically under A-2 (OH-D-7, OH-D-8). **Records:** nobody |
| *(D3-R1)* activation and rollback run evidence | `/var/tmp/⟨activation_id⟩-act-evidence`, `/var/tmp/⟨activation_id⟩-deact-⟨k⟩-evidence`, `/var/tmp/⟨RUN⟩-rb1-⟨n⟩-evidence` | `ubuntu` (journals `root`) | its run only | separate cleanup authority, and only after the records that cite them are accepted |
| retained R4/R5 evidence | `/var/tmp/p5-r5-fresh-20261003T234834Z-4fc93046-*`, `/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-*` | as recorded | nobody | only Peter's separate cleanup decision |
| H-0, H-1 and H-2 run evidence | `/var/tmp/⟨RUN⟩-h0-evidence`, `-h1-evidence`, `-h2-evidence` | `ubuntu` | its run only | separate cleanup authority |

*(D3-R2)* The activation objects now live under `/run` (§4.2.5-R2 (b)). Only CL
removes them, automatically under A-2, or a kernel boot clears them. CL attempt
directories are root-owned, and the installed tool `rp11_h1.py` is an H-1
object, removable by RB-1 only. The transient holder and backstop units are
created and ended under A-2 and leave nothing persistent.

H-1 reads the rebuild's image **once**, from the path its accepted rebuild
record names. It verifies the in-memory bytes and publishes **those bytes**
(§4.2.4). The source path cannot be substituted between the check and the
write. Every run's freshness check refuses an identifier that collides with
the `p5-r5-fresh-` prefixes.

### 4.6 Failure, rollback and terminal states

#### 4.6.1 H-1 terminal states

> **Original D3 text, superseded by D3-R1 §4.6.1-R1.**

| State | Boundary | Host |
|---|---|---|
| **PASS** | P-0 … V-2 all succeed; ST-1 exactly; the record re-read with matching digest; no path outside §4.2.3 and the run evidence directory was created | ST-1 |
| **INVALID RUN** | any failure in P-0 or P-1, before M-0 | unchanged, apart from the run's own evidence directory |
| **HARD STOP** | any failure at or after M-0, including a failed post-check or a record mismatch | some ST-0.x or ST-1. Reported exactly from the journal; **no automatic remediation** (OH-D-8) |

#### 4.6.2 Rollback procedures (digest-guarded)

> **Original D3 text, superseded by D3-R1 §4.6.2-R1.** Guard G depended on a
> `created` line written after the link (`OH-H1-D3-1`). The ST-1.x row left
> `pass-a.json` for a separate authority, which is contrary to the decided
> OH-D-8 (`OH-H1-D3-2`). The list "Never touched by any procedure" is
> **retained** by §4.6.2-R1.

**Guard G.** A path is removed only if all of the following hold:

* its journal line `created P dev ino sha256` exists for this run;
* `lstat` shows a regular file, owned by root, with that `(dev, ino)`; and
* the re-read SHA-256 equals the recorded value.

A temporary name `T` is removed only if its `intend T` line exists and it is a
regular root- or `ubuntu`-owned file with the recorded `(dev, ino)`, when one
was recorded.

A directory is removed with `rmdir` only if it is recorded
`created_by_run: true` and is empty.

Anything failing G is **left in place and reported**. That is what prevents
removing an unrelated file that appeared at the path.

| From | Procedure | `daemon-reload`? |
|---|---|---|
| ST-0.x (H-1 HARD STOP) | **RB-1** under separate authority (OH-D-8): in reverse journal order, remove the H-1 record, unit, staged rule, bootstrap, launcher and temporaries under G; `rmdir` the created directories | **only if** the unit's final name was recorded as created and has now been removed |
| ST-1 | **RB-1** under separate authority. The H-1 record is **retained**: it is evidence, and RB-1 never deletes a record. Its directory is then not empty and stays | yes, once, after the unit is removed |
| ST-1.x (`ACT` HARD STOP) | automatic under A-2, if OH-D-8 accepts: remove **only** the active rule under G. Then stop. `pass-a.json` removal is separate authority *(withdrawn by D3-R1: contrary to the decided OH-D-8; see §4.2.5-R1 (e))* | no |
| ST-2 | **`DEACT`** (§4.2.5) → ST-1 | no |
| ST-3 | not a rollback: `systemctl stop` is the §9.5.3 interruption, then `DEACT` | no |

**Never touched by any procedure:**

* any capture root;
* any database;
* `/opt/freedom-blades/platform`;
* the retained R4/R5 paths;
* the build/staging paths (separate cleanup); and
* any host other than `oracle-test`.

#### 4.6.1-R1 H-1 terminal states and the ST mapping *(D3-R1)*

| Terminal state | Boundary | Host state | Who acts next |
|---|---|---|---|
| **PASS** | P-0 … V-2 succeed and `run-end PASS` is durable | **ST-1** exactly, with the record re-read at its reported digest | A-2 preparation, which is separate |
| **INVALID RUN** | any failure in P-0 or P-1 | **ST-0**, apart from the run's own evidence directory | Peter |
| **HARD STOP** | any failure, kill or host loss at or after M-0, including a failed V-1 or V-2 | **ST-0.k** for k = 0 … 6 (§4.2.4-R1 (e)), with the suffix `+X` when RS-1 finds an A0 or A1-damaged object at or under a final path. Never ST-1, because ST-1 requires V-2 to pass | nobody automatically. RB-1 needs **separate** authority (OH-D-8) |

**How a HARD STOP is classified.** The read-only scan **RS-1** (§4.6.2-R1)
determines k and the classification of every object. If the executor's
session survives the stop, it runs RS-1 under the H-1 authority and writes the
HARD STOP handback. That handback reports the journal's SHA-256 and length, and
RS-1's complete output. If the session does not survive, the H-1 run ends
without a handback. RS-1 is then run only under a later authority: either the
read-only first step of a separately authorized RB-1, or a separate read-only
scan authority, as Peter chooses. An H-1 HARD STOP never triggers removal.

| ST-0.k | Final paths this run created, from §4.2.4-R1 (e)'s commit order |
|---|---|
| ST-0.0 | none. At most this run's temporary trees and S0 leftovers exist |
| ST-0.1 | tree L |
| ST-0.2 | L and V (V is absent from this run's objects when RS-A admitted an earlier store) |
| ST-0.3 | L, V and E |
| ST-0.4 | L, V, E and the unit; `daemon-reload` not confirmed |
| ST-0.5 | as ST-0.4, with `reload-done` exit 0; V-1 not passed |
| ST-0.6 | as ST-0.5, with the H-1 record linked; V-2 not passed |

*(D3-R2)* ST-0.3 is withdrawn with tree **E**. ST-0.4 … ST-0.6 contain L, V and
the unit (§4.2.4-R1 (e), D3-R2 note).

#### 4.6.2-R1 Recovery: RS-1, attribution, RB-1 and escalation *(D3-R1)*

**RS-1, the read-only recovery scan.** The `scan` subcommand of the same tool
runs as root through the verified-exec stub. Root is needed to list the `0700`
temporary trees. It makes no mutating call. A repository test (OH-S4) asserts
that its code path contains no write-mode `open`, namespace call or `fsync`.
RS-1:

1. reads and parses the journal (§4.2.4-R1 (b));
2. for every identity line, finds the object by its final name and, for a
   tree, by its temporary name as well. It uses `fstatat` with
   `AT_SYMLINK_NOFOLLOW`, descriptor opens with `O_NOFOLLOW`, and reads and
   hashes regular files;
3. lists every final directory of this run, every temporary tree and each
   `file-intent`'s directory; and
4. classifies every object it finds.

**Attribution classes** (closed):

| Class | Definition | Removable? |
|---|---|---|
| **A1-intact** | The journal is valid and holds an identity line for this object. Its current type and `(dev, ino)` equal that line. It is uid and gid 0 with the recorded mode (or `0700` for an unsealed temporary directory). A file also has the recorded size and SHA-256 and `st_nlink = 1` | yes, by RB-1 (H-1 objects) or by CL (activation files), under G-R1 |
| **A1-damaged** | type and `(dev, ino)` match an identity line, but some other recorded attribute differs | **no**: kept and escalated |
| **A0** | no matching identity line; or **every** object when the journal is invalid or missing; or any object that was found at a target name by PF-1, PT-1, PF-6 `EEXIST` or PT-8 `EEXIST` | **no**: kept and escalated |
| **S0** | the A0 objects at, or inside, a run-unique temporary name `.rp11-⟨RUN⟩-*`. Window W-T is the only way this run can create one | **no**: kept and reported. Never blocking (proof P-2) |
| **absent** | nothing at a name for which an identity line exists | — |

**G-R1, the removal guard.** An object is removed only if all of the following
hold:

* it is A1-intact;
* it is **re-verified immediately before removal** through a descriptor. For a
  file: `openat(…, O_RDONLY|O_NOFOLLOW)`, `fstat` and a full re-hash. For a
  directory: `O_DIRECTORY` and a listing that must be empty;
* the removal is journaled write-ahead in the removing run's **own** journal:
  `remove-intent {path, dev, ino, sha256}`, `fsync`, then `unlinkat` (with
  `AT_REMOVEDIR` for a directory), `fsync` of the parent, `removed {path}` and
  `fsync`; and
* each directory is removed only once it is empty.

*Stated limit.* Between the descriptor re-verification and `unlinkat`, only
root can swap the name, because every directory involved is root-owned and not
group- or world-writable. Under OH-D-6 that is the T-B case, which M-10 places
out of scope. It is not a T-A case.

**Boundary table for H-1** (each row is a stop at that boundary):

| Protocol boundary | Durable journal | What can be at the name | RS-1 class | RB-1 action |
|---|---|---|---|---|
| before PF-2 or PT-2 is durable | no intent | nothing, unless a foreign object appeared | absent, or A0 | none, or keep and escalate |
| PF-2 … PF-6, not yet returned | intent, perhaps identity | an unnamed inode only, freed. The name is absent unless foreign | absent, or A0 | none, or keep |
| PF-6 returned, before PF-7 | identity | this run's inode, or nothing if a power loss lost the entry | A1-intact, or absent | remove, or none |
| PF-7 … PF-9 and later | identity and `file-linked` | this run's inode | A1-intact (A1-damaged if altered) | remove (or keep and escalate) |
| PF-6 `EEXIST` | identity | a foreign object | A0 | keep, escalate |
| PT-3 or PT-4 within window W-T | intent (and the parent's identity, for PT-4) | a directory whose identity is unrecorded, at `x` or inside the tree | S0 | keep, report; it never blocks |
| PT-3 … PT-7 after the identity lines | directory and file identities | the temporary tree with A1 members | A1-intact | remove members bottom-up, then the temporary top if it is empty |
| PT-8, before or after the rename, before PT-9 | `tree-sealed` | the tree at exactly one of `x` and `t` | A1-intact wherever found | remove |
| PT-9 and later | `tree-linked` | the tree at `t` | A1-intact | remove |
| PT-8 `EEXIST` | `tree-sealed` | a foreign object at `t`; the tree at `x` | A0 at `t`; A1-intact at `x` | keep `t` and escalate; remove the tree at `x` |
| M-5 | `reload-intent`, perhaps `reload-done` | manager state only | — | one `daemon-reload` after removing the unit, whenever the journal has the unit's `file-identity` line |

**RB-1, H-1 installation rollback.** RB-1 is **separately authorized** (OH-D-8).
H-1, `ACT`, `DEACT` and CL never perform, request or trigger it. It is never
automatic.

1. **Precondition.** Both activation paths are absent. Every activation that
   names this H-1 record has a `deact` record with `st1-verified`. The unit's
   `ActiveState` is `inactive` or `failed`. Otherwise RB-1 is INVALID RUN, and
   CL's residual handling governs first.
2. **Run.** RB-1 has its own run identifier
   `⟨RUN⟩-rb1-⟨n⟩`, evidence directory and journal, under the same rules as
   §4.2.4-R1 (b). It runs RS-1 first. Its input is the H-1 journal: the
   retained file, or a copy whose SHA-256 and length equal the H-1 handback's
   (OH-D-9). It also reads every earlier RB-1 journal for the same `⟨RUN⟩`.
   An object such a journal shows as `removed` and that is now absent is
   classed `removed-earlier`, so a repeated or interrupted RB-1 is
   idempotent.
3. **Order** (reverse commit order):
   * the unit;
   * one `daemon-reload` if the journal has the unit's `file-identity` line;
   * tree E;
   * tree V, only if this run created it and it holds no record (ST-0.0 …
     ST-0.5);
   * tree L, members bottom-up and then its directories; and
   * this run's A1 temporary trees.

   Records are **never** removed.
4. **Terminal states.** PASS: ST-0, apart from retained records, run
   evidence and S0. HARD STOP: any A0 or A1-damaged object remains at or under
   a final path, or a removal or post-check fails. The handback lists the
   residual. INVALID RUN: the precondition fails.

*(D3-R2)* RB-1's precondition (item 1) gains two conditions: no transient unit
of any activation of this H-1 record is loaded in an active state, and every
such activation has a terminal `deact` record (`cleared-by-boot` included).
Item 3 no longer has a tree **E**, and tree **L** includes the installed tool.
RB-1 never touches `/run`, and it never runs CL, BS or attestation
(§4.2.5-R2 (o)).

**Escalation of what cannot be attributed.** For every A0, A1-damaged and S0
object, the H-1 or RB-1 handback lists: its path, class, type, uid, gid, mode,
size, `(dev, ino)` and link count; its extended-attribute **names**; and, for
a readable regular file, its SHA-256. It never lists content. Such objects are
**kept**. Only Peter's separate decision, made after investigation, may
dispose of one. No procedure in this design removes, moves or adopts one.

**Proof P-1: no unrelated object is ever removed.**

1. Every final path and every temporary name was shown absent at P-0, and again
   immediately before its own mutation (PF-1 and PT-1).
2. An object that existed before the run is still the same live object. Two
   live objects never share `(dev, ino)` on one device (PO-20 (e)), so it
   cannot match an identity line recorded from a descriptor this run created.
3. An object that appeared later can pass G-R1 only by matching this run's
   recorded type, `(dev, ino)`, owner, mode, size, link count **and** SHA-256,
   at a name where this run published that object. It is then byte-identical to
   what this run published there, so removing it removes no unrelated content.
4. An object found at a target name by PF-1, PT-1 or an `EEXIST` is A0 by
   definition.
5. A missing or invalid journal makes everything A0.

**Proof P-2: a later H-1 is never blocked by an object this protocol can
attribute.** Let *F* be §4.2.3's final paths other than the RS-A record store.

1. By invariant I and the prefix property, every object this run placed at or
   under a path in *F* has a durable identity line. It is therefore A1-intact
   or A1-damaged, never A0.
2. RB-1 removes every A1-intact object, and every directory of this run that
   becomes empty.
3. RB-1 ends PASS only if no A1-damaged or A0 object remains at or under *F*.
   So after RB-1 PASS every path in *F* is absent.
4. What can remain is:
   * the record store with retained records, which a later P-0 admits under
     RS-A once the records are in the pinned inventory;
   * S0 objects, which exist only at, or inside, `.rp11-⟨RUN⟩-*` names in
     pre-existing system directories. A later run never checks those names
     and cannot reuse them, because its own `⟨RUN⟩` differs and is checked
     absent; and
   * run evidence under `/var/tmp`.

   None is a path that a later P-0 requires to be absent.
5. A later H-1 therefore stays blocked only by an A0 or A1-damaged object at
   or under *F*. Those are exactly the objects this design refuses to
   attribute or remove, and it escalates them.

**Activation files.** `pass-a.json` and the active rule are never RB-1 objects.
They are removed only by CL (§4.2.5-R1), automatically under A-2, with the same
classes and the same G-R1.

| From | Procedure | Authority | `daemon-reload`? |
|---|---|---|---|
| ST-0.k (H-1 HARD STOP) | RS-1, then RB-1 | **separate** (OH-D-8) | as in the boundary table |
| ST-1 | RB-1; records retained | **separate** (OH-D-8) | yes, once, after the unit |
| ST-1.a1, ST-1.a2, ST-1.d1 | CL (§4.2.5-R1 (e)) | automatic under A-2 (OH-D-7, OH-D-8) | no |
| ST-2, ST-3 | `DEACT` (CL) at the pass's terminal state; a hung pass is first interrupted under §9.5.3 by the operator | automatic under A-2 | no |
| ST-1+R | none automatically; Peter decides | separate | — |

*(D3-R2)* The rows for ST-1.a1, ST-1.a2, ST-1.d1, ST-2 and ST-3 now read as
follows, and ST-1.a0 is the same. CL is triggered by the holder's end
(`stop-post`) and retried by the backstop, both automatically under A-2. No
interactive actor is needed. ST-1.bc needs no removal: the kernel boot has
cleared it, and attestation (§4.2.5-R2 (i)) records it under the same
automatic A-2 authority. ST-1+R is unchanged, except that BS-4 keeps retrying
a `grant-unremovable` rule.

*(D3-R3)* CL's grant-priority mode GP-R3 also removes `pass-a.json` and the
activation directories when evidence cannot be written (§4.2.5-R3 (e)). It
leaves ST-1.ur, which the next journaled CL trigger records, automatically
under A-2. RB-1's precondition already refuses ST-1.ur, because no terminal
`deact` record exists.

*(D3-R4)* In the ST-2, ST-3 row, "a hung pass is first interrupted under
§9.5.3 by the operator" is superseded. Only the executor interrupts, by the
route (iii-a) root literal under A-2 (§4.2.5-R4 (e)). The same applies to the
original D3 table's ST-3 row. CP is part of the start, not a rollback, and it
removes only the rule. RB-1 is unchanged, separately authorized and never
automatic. Its precondition also covers ST-2.f, because no terminal `deact`
record exists until CL has run.

*(D3-R5)* Route (iii-a) is issued only while the capture unit is `active` with
this activation's consumed `InvocationID` (§4.2.5-R5 (h), OS-6). CP's claim is
retained evidence. RB-1 never removes it, and RB-1 is unchanged.

*(D3-R6)* The route (iii-a) condition is now Peter Duscha's decided OS-6, and
its governing text is §4.2.5-R6 (b). It is never issued while the capture unit
is `activating`. A hung CP ends at the start timeout. RB-1 is unchanged,
separately authorized and never automatic.

The list of things never touched by any procedure (§4.6.2) is retained
unchanged. It now also covers every record in the record store.

#### 4.6.3 Drift between H-1 and a pass

| Event | Detected by | Result |
|---|---|---|
| reboot | `boot_id` (H-2 context, `pass-a.json`'s `boot_id`, `entry-activation-stale`) | ST-1 survives, because the files are persistent and the unit is reloaded at boot. An activation does not survive: `ACT` is valid for one boot, and a reboot during ST-2 requires `DEACT` before any further step. A generator-written drop-in or a changed default appears in H-2's `baseline`. *(D3-R1)* A reboot in ST-1.a1 … ST-3 is AC-10: `DEACT` is the first RP-11 action after the reboot, and it is automatically authorized. Residual RR-2 states that the rule is live until then. *(D3-R2: the two preceding sentences are withdrawn. An orderly reboot first runs CL through the holder's `ExecStopPost=`. Any kernel boot clears both activation files from `/run` (M-B), and attestation records the outcome (§4.2.5-R2 (i), (k)). A userspace-only restart is DF-1 (§4.2.5-R2 (l)).)* A reboot during H-1 is an H-1 HARD STOP classified by RS-1 (§4.6.1-R1). A reboot during RB-1 is an RB-1 HARD STOP, and its journal lets a later RB-1 run continue safely |
| package-version drift (`unattended-upgrades` or manual) | H-2 `packages` | stop. The citations are version-bound: re-cite for the new version, then write a new H-1 record by an **H-1R** re-record step (read-only plus record write, no file change) under separate authority. Whether to hold packages is Peter's operational choice, not proposed here. *(D3-R1)* H-1R publishes its record by PF into `h1/`, with its own run journal |
| systemd update | `packages`, the unit and manager `baseline`, `NeedDaemonReload` | stop. Re-cite PO-8, PO-14 and PO-15 (and the property lists). If PO-14 is refuted, LB-2S is withdrawn for that version and RB-1 is requested |
| kernel update (only effective after reboot) | `host.kernel_release` | stop. Re-establish PO-18, PO-17 and D9-1 for the new series, then H-1R. No rebuild (D2 §5.13) |
| glibc or CPython update | `packages`; HF-08/HF-09 digests in the H-2 recomputation | stop. Re-cite PO-12 and PO-19, then H-1R |
| `ubuntu` UID, GID or groups changed, or repository ownership changed | `operator` | stop and return to Peter (U-3). Never substitute an account |
| an installed file changed or replaced | `files`/`launcher` digests and `(dev, ino)` | stop. The cause is reported. Reinstalling needs RB-1 then H-1 |

#### 4.6.4 PO-16 and D9-5 ordering on one host

Both are separately authorized. Because `oracle-test` now holds the
installation:

* **PO-16's drill** may run only in ST-1 or ST-2 with a **test** pass
  configuration, never with a real capture root. It must restore the manager
  environment it changed, under its own authority. An H-2 after it must equal
  H-1.
* **D9-5** runs only on a separate copy of the image under its own run paths.
  It never runs on the installed file.

*(D3-R4)* A start of the capture unit in ST-2 runs CP, which consumes that
activation's grant once (CP-3). A PO-16 drill that starts the unit therefore
needs its own test activation, and it cannot reuse a real one.

*(D3-R5)* "Once (CP-3)" now rests on §4.2.5-R5 (f): any start attempt of an
activation, failed or not, uses that activation's only attempt.

### 4.7 Decisions, paragraph disposition, traceability and successors

#### 4.7.1 Proposed wording for the remaining C11 decisions (U-6; not a blanket acceptance)

M-9 = LB-2S (conditional), M-14 and M-10 are decided (D1-R2) and are not
re-proposed. The texts below are **proposed decision wording**. Each becomes
effective only through Peter's individual decision after Codex's review.
Brackets name the OH-D on which a clause depends.

*(D3-R1.)* Every bracketed OH-D item was decided on 2026-10-04, as each
clause assumes (§3). The clauses stand as written. They remain **proposed
wording**, which needs Peter's individual decision after Codex's review.

* **M-11 (scope).**
  > The C-11 decision, and this one-host amendment, apply to **Pass A only**.
  > Pass B, including PB-1 … PB-4, requires its own design pass.
* **M-12 (bootstrap location).**
  > The bootstrap is installed root-owned at
  > `/usr/local/libexec/freedom-blades-rp11/rp11_entry.py`, mode `0644`, by
  > H-1. Its SHA-256 is bound by the H-1 record and by `pass-a.json`'s
  > `bootstrap_sha256`.
* **D-2 (A1-12).**
  > **D-2a.** A1-12 is the reviewed literal
  > `sha256sum /opt/freedom-blades/runtime/venv-web/bin/python`, executed
  > locally by the entry. It depends on PO-7 (`sha256sum` follows the link),
  > cited for the HF-07 `coreutils` version.
* **D-1 (draft amendment; replaces C11 §5.3's quoted block for one host).**
  > **Pass A command texts.** Every Pass A act is a reviewed literal command
  > text, fixed byte for byte in the draft and in the pinned act catalogue.
  > The entry executes it on `oracle-test` as the reviewed no-shell parse of
  > that text, with `argv[0]` mapped to its pinned absolute path. No Pass A
  > text is completed from a value the pass produces. **Pass A contains no
  > synchronization act** [OH-D-4]. The repository tree is placed before the
  > pass, outside RP-11, and is verified inside the pass by the bootstrap's
  > manifest check and by A1-S. **No Pass A act invokes `sudo`** [OH-D-5].
  >
  > **Issue.** The operator issues the acts only through the one reviewed
  > invocation `/usr/bin/systemctl --no-ask-password start --wait
  > rp11-capture-pass-a.service`, from a client process running on
  > `oracle-test` as `ubuntu` [OH-D-2], and only in state ST-2 under the
  > pass's authorization [OH-D-7]. That invocation takes no operand. The
  > entry's image and argv are fixed by root-installed bytes. Its environment
  > is the literal that the root-installed static first image writes, and
  > nothing from the client or the service manager's environment. Its other
  > process state comes from the reviewed, root-configured service manager,
  > not from the client.
  >
  > **Inspection, execution and record.** As C11 §5.3, unchanged.
* **MD-C11.**
  > **O-2**, carried by LB-2S, for Pass A, subject to PO-9, PO-14 and the
  > installation and activation states of the one-host amendment.
* **M-1, M-3, M-4 and M-8.**
  > **Withdrawn as not applicable**: no `ssh` or `rsync` runs in Pass A.
* **M-2.**
  > `LC_ALL=C`.
* **M-5 (amended).**
  > Every Pass A act's program is named by an absolute path under `/usr/bin`
  > (or the venv interpreter for A1-S1 and A1-13), pinned in
  > `PROGRAM_PATHS`. Each is checked by `lstat`: root-owned, not group- or
  > world-writable. `/usr/bin/python3.12` is checked the same way. Binary
  > digests are not pinned.
* **M-6.**
  > Per-pass invocation for Pass A, with catalogue-encoded conditions and stop
  > predicates.
* **M-7.**
  > The hook files and `.claude/settings.json` are covered sources.
* **M-13.**
  > No change to the hooks' shebangs in this amendment. It remains an optional,
  > separate decision.

*(D3-R4.)* **D-1, "Issue" paragraph, amended** for OH-D-10 (A, iii-a). This is
proposed wording, like the rest of §4.7.1. Two sentences are added after
"…not from the client.":

> The rule grants the operator `start` only. The capture unit's fixed root
> pre-start step consumes that grant, and verifies it disabled, before the
> entry's image runs. A start whose pre-start step fails is not a pass.
> **Interruption.** The operator has no `stop` route. A pass is interrupted
> only by the executor, under the pass's authorization, with the one reviewed
> literal `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service`, as a
> §9.5.3 interruption.

*(D3-R5.)* One further sentence is proposed after "…is not a pass.":

> An activation admits one start attempt. After any attempt has ended, no
> later start of that activation can run the pass.

In the **Interruption** sentence, "a pass is interrupted only by the executor"
is read with §4.2.5-R5 (h): only while the pass is running.

*(D3-R6.)* OS-6 is decided, so the reading note above is replaced by wording.
In the **Interruption** sentence, after "…as a §9.5.3 interruption", add:

> …, and only while the capture unit is `active`, its invocation equals the one
> its consume step recorded, and that step's `consumed` record is durable. The
> literal is never issued while the unit is `activating`, including during its
> pre-start step. A pre-start step that does not finish is ended by the unit's
> finite start timeout.

The D3-R5 one-attempt sentence is replaced by:

> An activation admits one start attempt. While every act on the host stays
> within the pass's authorization, no later start of that activation can run
> the pass after any attempt has ended.

#### 4.7.2 Disposition of earlier C11 and D2 text

| Text | Disposition |
|---|---|
| C11 §4.4.3.1 … §4.4.3.5 (S-1 … S-10, E-1 … E-11, the LB-2S unit and launcher contract, the allow-list answer) | **retained.** Only the subject host changes; `⟨MI.operator_account⟩` := `ubuntu` |
| C11 §4.4.3.4, the polkit rule text | **retained**, with `subject.user == "ubuntu"`. Its installed location is **added**: `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules`, in ST-2 only |
| C11 §4.4.3.6, "provisioning" row | **replaced** by §4.2.1 and §4.2.2 (H-1 three placed plus one staged; `ACT` two) |
| C11 §4.4.3.7, installation record | **replaced** by §4.3 (`rp11-h1-record/1`). The H-2 paragraph is **amended**: H-2 compares `baseline_sha256` (§4.3.4). Rollback is **replaced** by §4.6.2 *(D3-R1: by §4.6.2-R1)*. PO-16 drill **amended** by §4.6.4 |
| C11 §5.3, D-1 block | **replaced for one host** by §4.7.1's D-1 text. The inspection, execution and record clauses are retained |
| C11 §6.5, fail-closed matrix | **retained**, plus the two diagnostic rows of §4.3.5 |
| C11 §6.6, `program` ∈ {`rsync`, `ssh`}; §9 `PROGRAM_PATHS` | **replaced**: local absolute programs (M-5 amended). `A1-00`'s §5 drift test is **withdrawn** |
| C11 §7.1 … §7.6, `rp11-launcher-env/1` | **amended**: one key set `{LC_ALL, PATH}`, the same literals and grammars. The `SSH_AUTH_SOCK` row, agent mode, §7.4 … §7.6 and the `RSYNC_*`/`SSH_*` rationale are **withdrawn**. Their names stay **P** (prohibited) in the matrix, so their presence is still refused |
| C11 §7.9, `rp11-entry-env/1` | **retained** unchanged |
| C11 §12, slices I-1 … I-7 | **retained**. Row H-1 is **replaced** by §4.2. **New** rows: `ACT`, `DEACT`, H-1R (§4.6.3). *(D3-R1: also RS-1 and RB-1, §4.6.2-R1)* |
| C11 §13, M-1, M-3, M-4, M-8 | **withdrawn** (not applicable) |
| C11 §14, PO-1 … PO-3 | **withdrawn**. PO-11 is **extended** with (b) and (c). **New** PO-19. PO-8, PO-9, PO-12, PO-14 … PO-16 are **retained**. *(D3-R1: PO-11 is further extended with (d) and (e); **new** PO-20, §4.4.2a)* |
| C11 §6.9, R-3 | **withdrawn**. R-7 and R-10 are **retained**, with OH-D-6 added as a stated property |
| D2 §2.1 OD-5, OD-6; §2.2 AD-1, AD-2 | **amended**: the H-1 host is `oracle-test`. PO-18 and H-0 (HF-04) discharge AD-1 and AD-2 |
| D2 §5.11, H-1 record launcher facts | **retained in substance**, carried as `baseline.launcher` (§4.3.2). The "first 128 bytes" wording for PO-17 is **replaced** by §4.3.6's bounds rule |
| D2 §5.13, "roll back an installation" and "emergency disable" | **replaced** by §4.6.2. Emergency disable is **narrowed** to removing the active rule (ST-2 → ST-1.x). *(D3-R1: replaced by §4.6.2-R1 (RB-1, separately authorized) and §4.2.5-R1 (CL). Emergency disable becomes the automatic activation cleanup: the rule first, then `pass-a.json`, ending in verified ST-1 or AC-9. The D3 narrowing is withdrawn under OH-D-8)* |
| D2 §5.14, §5.15, §6.1 … §6.3 | **retained** unchanged |

*(D3-R2)* Further dispositions:

| Text | Disposition |
|---|---|
| C11 §4.4.3.4, the rule's installed location (as added above) | **amended**: `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules`, in ST-1.a2 … ST-3 only. The rule **text** is unchanged |
| C11 §4.4.3.4 and §9 (the bootstrap row, and the hook rule that compares `catalogue_sha256`): the pass-configuration path `/etc/freedom-blades-rp11/pass-a.json` | **amended** to `/run/freedom-blades-rp11/pass-a.json`. The root-ownership and "not group- or world-writable" checks are unchanged. No implemented file holds the old path. The launcher image names only the bootstrap path |
| D2 §5.13, "emergency disable" (as replaced by D3-R1) | **amended**: the automatic activation cleanup is triggered by the holder's end and by the backstop, and a kernel boot clears both files (§4.2.5-R2) |

*(D3-R3)* No further disposition is made. Two are **proposed for OH-D-10 (A)
only, and are not made**: C11 §4.4.3.4's rule text, narrowed to the verb
`start`; and C11 §4.4.3.4's unit text and T-B1, amended to admit exactly the
one `ExecStartPre=+…rp11_h1.py consume` line (§4.2.5-R3 (c), (d)). Until Peter
decides, C11's rule and unit text stand as §4.7.2 retains them.

*(D3-R4)* Peter decided OH-D-10 (A, iii-a). The two dispositions above are
**proposed as made**, and four more follow from them. Each takes effect only
with Peter's acceptance of the design after Codex's re-review.

| Text | Disposition |
|---|---|
| C11 §4.4.3.4, the unit text | **amended**: exactly one line added, `ExecStartPre=+/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume`. The full text is §4.2.5-R4 (b). `ExecStart=`, `User=ubuntu`, `NoNewPrivileges=yes` and every absence except `ExecStartPre=` are unchanged |
| C11 §4.4.3.4, the rule text | **amended**: the verb test is `action.lookup("verb") == "start"`. The full text is §4.2.5-R4 (b). The sentence "`stop` is allowed so that the operator can interrupt a hung pass" is **withdrawn** |
| C11 §4.4.3.4, "**Those absences are properties of the text** (T-B1)", and the T-B1 and T-B2 rows of C11 §10.3 | **amended**: T-B1 admits exactly the one `ExecStartPre=` value. T-B2 requires the verb `start` only (§4.2.5-R4 (b)) |
| C11 §14, PO-11 row: "…and that `stop` produces a §9.5.3 interruption" | **amended**: interruption is route (iii-a), a root `stop` that needs no Polkit decision. PO-11 gains (g): `ubuntu`'s `stop` is not authorized |
| C11 §5.3, D-1 "Issue" (as replaced for one host by §4.7.1) | **amended** by the D3-R4 sentences in §4.7.1 |
| C11 §6.5, fail-closed matrix | **amended**: one row is added. A CP failure ends the start with the unit `failed` and **no entry process**, and the pass does not begin. CP's stable codes are journal lines, not RP-11 records |

#### 4.7.3 Traceability

| Requirement | Where this proposal addresses it | Status |
|---|---|---|
| U-1 (superseded → `oracle-test`) | §4.1.1, §4.1.2, IA-1 … IA-15 | designed; OH-D-1 … OH-D-4 open *(superseded: decided, see the D3-R1 amendments)* |
| U-2 (Gemini executor) | §4.1.1, §4.2.4; OH-D-2, OH-D-6 | designed; placement open *(superseded: decided)* |
| U-3 (superseded → `ubuntu`) | §4.1.1, HF-03, §4.6.3 | designed |
| U-4 (pinned local rebuild) | §4.5 | designed; OH-D-1 open *(superseded: decided)* |
| U-5 (D9-2 Complete) | `baseline.launcher.d9_2` (§4.3.2) | carried |
| U-6 (individual decision wording) | §4.7.1 | proposed |
| U-7 (complete baseline) | §4.2.1, §4.3.3, §4.3.4 | designed; property lists version-bound (OH-S2) |
| U-8 (no standing grant) | §4.2.1, §4.2.2, §4.2.5 | designed; OH-D-6, OH-D-7 open *(superseded: decided; see the D3-R1 amendments)* |
| U-9 (glibc/loader) | PO-19 (§4.4.2), HF-09 | designed |
| U-10 (citation access) | §4.4.3 | ordered |
| handback P-1 (decisions) | §3, OH-S0 | open |
| handback P-2 (D9-2) | decided (U-5) | closed by decision |
| handback P-3 (C11 decisions) | §4.7.1 | proposed |
| handback P-4 (installation and record design) | §4.2, §4.3, §4.6 | **this proposal** |
| handback P-5 (repository implementation) | OH-S4 | pending |
| handback P-6 (host facts) | §4.4.1, OH-S1 | defined |
| handback P-7 (citations) | §4.4.3, OH-S2 | ordered |
| handback P-8 (installable bytes) | §4.5, OH-S5 | designed |
| handback P-9 (focused commit) | OH-S6 | pending |
| handback P-10 (H-1 assignment) | OH-S7 | pending |
| D9-1 | §4.4.3 step 7 | ordered |
| D9-2 | U-5; `baseline.launcher.d9_2` | Complete |
| D9-3 | §4.5.2 (not reopened) | Complete |
| D9-4 | §4.2.4 V-1, §4.3.2 `launcher`, §4.3.6, H-2 | designed |
| PO-8 | §4.4.3 step 3; TR-4 | ordered |
| PO-11 | §4.4.3 step 4 (b, c); TR-5; §4.2.5 | extended |
| PO-12 | §4.4.3 step 5; TR-9 | ordered |
| PO-14 | §4.4.3 step 1 (first); TR-7 | ordered; load-bearing |
| PO-15 | §4.4.3 step 2; §4.3.3 | ordered; produces the property lists |
| PO-17 | §4.3.6; P-0, V-1, H-2 | designed |
| PO-18 | `baseline.po18`; HF-04 | designed |

**Traceability amendments** *(D3-R1)*. The rows below replace the rows of
the same name above, which are kept as the original D3 text. New rows are
marked **new**. Rows not listed are unchanged.

| Requirement | Where this proposal addresses it | Status |
|---|---|---|
| U-1 (superseded → `oracle-test`) | §4.1.1, §4.1.2, IA-1 … IA-15 | designed; OH-D-1 … OH-D-4 **decided** |
| U-2 (Gemini executor) | §4.1.1, §4.2.4-R1; OH-D-2, OH-D-6 | designed; placement **decided** (local, interactive, as `ubuntu`) |
| U-4 (pinned local rebuild) | §4.5 | designed; OH-D-1 **decided** (direct Git retrieval on `oracle-test`, separately authorized) |
| U-8 (no standing grant) | §4.2.1, §4.2.2 (D3-R1 table), §4.2.5-R1 | designed: one-pass, one-boot `ACT`; automatic CL; grant removed first and claimed only with evidence; residual RR-2 stated. OH-D-6, OH-D-7 and OH-D-8 **decided** |
| handback P-1 (decisions) | §3 | OH-D-1 … OH-D-9 **decided**; §4.7.1 wording still open |
| handback P-4 (installation and record design) | §4.2.4-R1, §4.2.5-R1, §4.3, §4.6.1-R1, §4.6.2-R1 | **this proposal**, as remediated |
| PO-11 | §4.4.3 step 4 (b, c); §4.4.2a (d, e); TR-5; §4.2.5-R1 (f) | extended |
| **new** `OH-H1-D3-1` | §4.2.4-R1 (invariants W, I, N, D, R, S; PF; PT; journal), §4.6.1-R1, §4.6.2-R1 (RS-1, classes, G-R1, boundary table, RB-1, P-1, P-2) | remediated in design; **open** until Codex re-reviews |
| **new** `OH-H1-D3-2` | §4.2.5-R1 (a) … (h), §4.2.2 (D3-R1 table), §4.3.4 | remediated in design; **open** until Codex re-reviews |
| **new** OH-D-1 | §3.1, §4.1.1, §4.1.2, §4.1.4, §4.5.2, §9 | applied |
| **new** OH-D-2 | §3.2, IA-10, §4.1.1, TR-0, TR-1 | applied |
| **new** OH-D-3 | §3.3, IA-1, IA-5, §4.1.5 | applied |
| **new** OH-D-4 | §3.4, IA-2, §4.1.4, §4.7.1 D-1 | applied |
| **new** OH-D-5 | §3.5, IA-3, TR-12, §4.7.1 D-1 | applied |
| **new** OH-D-6 | §3.6, IA-7, IA-14, the `authority_limit` sentence (§4.2.5-R1 (b), §4.3.2, the activation records) | applied |
| **new** OH-D-7 | §3.7, §4.2.5-R1 (a), (b) and (e), §4.3.4 | applied |
| **new** OH-D-8 | §3.8, §4.2.5-R1 (e), §4.6.1-R1, §4.6.2-R1 (RB-1 separate; CL automatic) | applied |
| **new** OH-D-9 | §3.9, §4.2.4-R1 (b), §4.2.5-R1 (g), §4.6.2-R1 | applied |
| **new** PO-20 | §4.4.2a; P-0, AP-0 | defined; to be cited (OH-S2) |
| **new** RR-2 | §4.2.5-R1 (h) | stated residual; review focus §12.9 (3) |

**Traceability amendments** *(D3-R2)*. These rows replace the rows of the same
name above.

| Requirement | Where this proposal addresses it | Status |
|---|---|---|
| U-8 (no standing grant) | §4.2.1, §4.2.5-R1, §4.2.5-R2 (a) … (o) | designed: one-pass, one-boot `ACT` under a PID-1-supervised holder; the rule and `pass-a.json` on `/run`; CL on the holder's end and by the backstop, grant first, claimed only with evidence. OH-D-6, OH-D-7 and OH-D-8 **decided** |
| PO-11 | §4.4.3 step 4 (b, c); §4.4.2a (d, e); §4.4.2b (f); TR-5; §4.2.5-R1 (f) | extended |
| `OH-H1-D3-2` | §4.2.5-R1 (a) … (h) as amended, §4.2.5-R2 | remediated in design; **open** until Codex re-reviews |
| RR-2 | §4.2.5-R1 (h) | **withdrawn** by D3-R2 |
| **new** `OH-H1-D3-R1-1` | §4.2.5-R2 (a) … (o); §4.4.2b; §4.2.2 and §4.6.2-R1 D3-R2 notes; §4.3.4 D3-R2 order; §4.6.3 | remediated in design; **open** until Codex re-reviews |
| **new** PO-21 | §4.4.2b; AP-0, AM-0 | defined; to be cited (OH-S2) |
| **new** PO-20 (g) | §4.4.2b; AP-0 | defined; to be cited (OH-S2) |
| **new** DF-1, SL-1, GU | §4.2.5-R2 (l) | stated precisely; none defers disabling the grant after a single event |

**Traceability amendments** *(D3-R3)*. These rows replace or add to the D3-R2
rows of the same name.

| Requirement | Where this proposal addresses it | Status |
|---|---|---|
| U-8 and OH-D-7 (no live grant after the pass) | §4.2.5-R3 (b) … (d) | **not established.** Blocked on OH-D-10. D3-R2's latency claim and (n) 3 are withdrawn |
| `OH-H1-D3-2` | §4.2.5-R1 … R3 | **open**; depends on `OH-H1-D3-R2-1` |
| `OH-H1-D3-R1-1` | §4.2.5-R2; §4.2.5-R3 | **open**. Its human-action part stands as D3-R2 designed it. Its post-pass part is `OH-H1-D3-R2-1` |
| **new** `OH-H1-D3-R2-1` | §4.2.5-R3 (b), (c), (d); notes in §4.2.5-R2 (g), (k), (n) and §4.3.4 | **BLOCKED REMEDIATION**: needs OH-D-10, then R4 |
| **new** `OH-H1-D3-R2-2` | §4.2.5-R3 (e) … (i); notes in §4.2.5-R2 (h), (i), (j) and §4.6.2-R1 | remediated in design; **open** until Codex re-reviews |
| **new** OH-D-10 | §4.2.5-R3 (c) | maintainer decision required |
| **new** ST-1.ur | §4.2.5-R3 (f) | designed |
| PO-21 (n) … (r), PO-11 (g) | §4.2.5-R3 (d); §4.4.2b note | conditional on OH-D-10 (A); **not** obligations of the current design |

**Traceability amendments** *(D3-R4)*. These rows replace or add to the D3-R3
rows of the same name.

| Requirement | Where this proposal addresses it | Status |
|---|---|---|
| U-8 and OH-D-7 (no live grant after the pass) | §4.2.5-R4 (b) … (d), (i) | **designed**: the grant is `start` only and is consumed and PK-verified before `ExecStart=`. No grant exists during or after any pass. Open until Codex re-reviews |
| `OH-H1-D3-R2-1` | §4.2.5-R4; notes in §4.2.5-R2 (g), (j), (k), (n), §4.2.5-R3 and §4.3.4 | addressed in design; **open** until Codex re-reviews |
| `OH-H1-D3-R2-2` | §4.2.5-R3 (e) … (i) | **closed as remediated** by Peter on 2026-10-04 (R4 authority). GP-R3 is unchanged by D3-R4 |
| `OH-H1-D3-R1-1` | §4.2.5-R2; §4.2.5-R3; §4.2.5-R4 | **open**. Its post-pass part is addressed by §4.2.5-R4 (i) |
| `OH-H1-D3-2` | §4.2.5-R1 … R4 | **open** |
| OH-D-10 | §4.2.5-R3 (c); §4.2.5-R4 (a) | **decided**: Option A with route (iii-a) |
| **new** CP (consume step) | §4.2.5-R4 (b), (c); §4.1.3 TR-6a | designed; one-shot; serialized with CL |
| **new** route (iii-a) | §4.2.5-R4 (e); §4.7.1 D-1 | designed; pinned by A-2 |
| **new** ST-2.c, ST-2.f | §4.2.5-R4 (g) | designed |
| **new** AR-1 … AR-8; CX-1 … CX-3 | §4.2.5-R4 (a), (k) | refinements and residuals stated |
| PO-21 (n) … (r), PO-11 (g) | §4.2.5-R4 (j); §4.4.2b, §4.4.3 notes | **obligations of this design**; fail-closed at AP-0; to be cited (OH-S2) |

**Traceability amendments** *(D3-R5)*. These rows replace or add to the D3-R4
rows of the same name.

| Requirement | Where this proposal addresses it | Status |
|---|---|---|
| **new** `OH-H1-D3-R4-1` | §4.2.5-R5 (a) … (k); notes in §4.2.5-R2, §4.2.5-R4 (head label, (c), (d), (i), (k)), §4.1.3, §4.3.4, §4.6.2-R1, §4.6.4 and §4.7.1 | addressed in design; **open** until Codex re-reviews |
| one start attempt per activation (contract OSA) | §4.2.5-R5 (b), (f) | designed: SB-1, SB-2 and SB-3; CX-4 stated |
| CP consumption under the cleanup lock, before any remaining fallible precondition | §4.2.5-R5 (d), (e) CQ-1, CQ-2 | designed |
| CP, CL, HL and backstop agreement | §4.2.5-R5 (g) | designed (OS-5) |
| `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1`, `OH-H1-D3-2` | §4.2.5-R4; §4.2.5-R5 | **open**. D3-R5 changes no part of §4.2.5-R4 (i) items 1 … 6 |
| CP (consume step) | §4.2.5-R5 (e) | **re-ordered**: CQ-0 … CQ-7 supersede CP-0 … CP-7 |
| **new** OS-1 … OS-8; CX-4; CX-1 and CX-2 narrowed | §4.2.5-R5 (a), (k) | refinements and residuals stated |
| **new** PO-21 (s) … (v), PO-20 (h) | §4.2.5-R5 (j); §4.4.2b, §4.4.3 notes | **obligations of this design**; fail-closed at AP-0; to be cited (OH-S2) |

**Traceability amendments** *(D3-R6)*. These rows replace or add to the D3-R5
rows of the same name.

| Requirement | Where this proposal addresses it | Status |
|---|---|---|
| **new** `OH-H1-D3-R5-1` | §4.2.5-R6 (a) … (g); notes in §0-R5, §4.2.5-R2, §4.2.5-R4 (head label, (d), (e), (g)), §4.2.5-R5 (head label, (b), (f), (h), (i), (j), (k)), §4.3.4, §4.6.2-R1 and §4.7.1 | addressed in design; **open** until Codex re-reviews |
| OS-6, route (iii-a) timing | §4.2.5-R6 (a), (b); R6 authority | **decided** by Peter Duscha on 2026-10-04, as an amendment to route (iii-a); D3-R6 incorporates it |
| route (iii-a) | §4.2.5-R4 (e) as amended by §4.2.5-R6 (b); §4.7.1 D-1 (D3-R6 note); A-2 pin (§4.2.5-R6 (g)) | designed: available only under OC-1 … OC-3; literal, executor, A-2 authority and §9.5.3 classification unchanged |
| one start attempt per activation (contract OSA) | §4.2.5-R6 (c), (d), (e); §4.2.5-R5 (b), (f) | designed over the authorized path set 𝒜, **without exception**; Lemma R6 |
| CX-4 | §4.2.5-R6 (f) | residual **outside 𝒜**, SL-1 kind, two sources; voidable by PO-21 (u); not closed in every case |
| EO in `start-pre` (D3-R5's OS-4 claim) | §4.2.5-R6 (f) | **corrected**: outside 𝒜, CX-4 source (b) |
| `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1`, `OH-H1-D3-2` | §4.2.5-R4; §4.2.5-R5; §4.2.5-R6 | **open**. D3-R6 changes no part of §4.2.5-R4 (i) items 1 … 6 or of the SB-1 … SB-3 mechanism |
| PO-21 (n) … (v), PO-20 (h), PO-11 (g) | §4.2.5-R4 (j); §4.2.5-R5 (j) | unchanged; **obligations of this design**; fail-closed at AP-0; to be cited (OH-S2) |

#### 4.7.4 Bounded successor slices and review gates (proposals only)

| Order | Slice | Assignee | Scope | Gate |
|---|---|---|---|---|
| OH-S0 | decision record for OH-D-1 … OH-D-9 (OH-D-1 and OH-D-2 first) and the §4.7.1 wording *(superseded by the D3-R1 row below)* | Peter, recorded by Codex | decision | maintainer decision |
| OH-S1 | **H-0** read-only facts (§4.4.1) on `oracle-test` | the executor named under OH-D-2 | read-only, no `sudo`, prohibited list of §4.4.1 | Codex review |
| OH-S2 | citations, **PO-14 first**, then PO-15, PO-8, PO-11, PO-12, PO-19, D9-1, plus the version-bound property lists | Claude (repository documentation and read-only upstream source under U-10) | documentation | Codex review, then Peter. **A refuted PO-14 ends the sequence** |
| OH-S3 | operational-draft amendment for one-host Pass A: D-1/D-2 application; OH-D-3 … OH-D-5 outcomes; the local catalogue texts (no shell; A1-S1's working directory; `sudo` rows); `MI.capture_root_A` constraints; A1-Z restatement | Claude | documentation | Codex re-review of the draft (A-1) |
| OH-S4 | repository implementation, split as Peter prefers: C11 I-1 … I-6 under §4.7.1; `rp11_h1.py` (preflight, install, record, verify, rollback, `ACT`, `DEACT`, H-1R), the H-2 tool, the PO-17 matcher, the schema tests, E-2's absence test. Version-bound data lands **after** OH-S2 | Claude | repository only, unwired, nothing installed | Codex review per slice, with a security-focused review (§0.3) |
| OH-S5 | launcher rebuild and staging on `oracle-test` (§4.5) | executor per U-2/OH-D-2 | build as `ubuntu`; R5 procedure | Codex review |
| OH-S6 | focused commit of every reviewed input, then transport per OH-D-1 *(superseded by the D3-R1 row below)* | Peter | commit | controlled-path identity |
| OH-S7 | H-1 assignment preparation (digest-pinned, with `/goal` invocation) | Claude | documentation | Codex review, Peter acceptance and activation |
| OH-S8 | **H-1** execution (ST-0 → ST-1) | Gemini (U-2) | §4.2.4 only | Codex review of the handback; Peter acceptance |
| OH-S9 | H-2, then A-2, `ACT`, Pass A and `DEACT`: **outside this amendment** and each separately authorized | — | — | — |

OH-S3 and OH-S4's version-independent parts may run in parallel with OH-S1
and OH-S2. OH-S5 needs OH-S1 (capacity and the `bubblewrap` facts) and
OH-D-1.

**Successor amendments** *(D3-R1)*. The rows below replace the rows of the
same name above, which are kept as the original D3 text. Rows not listed are
unchanged. Every slice still needs its own authority, and none is requested
here.

| Order | Slice | Assignee | Scope | Gate |
|---|---|---|---|---|
| OH-S0 | **done in part**: OH-D-1 … OH-D-9 decided on 2026-10-04. Still to decide: acceptance of this design after Codex's re-review; the §4.7.1 wordings; PO-19, PO-20 and PO-11 (b) … (e) | Peter, recorded by Codex | decision | Codex re-review, then maintainer decision |
| **OH-S0b (new)** | authority for direct Git retrieval of the pinned commit on `oracle-test` from the canonical remote. If authentication is needed, a separate authority for a read-only credential's installation and handling (OH-D-1) | Peter | decision | maintainer decision; no retrieval before it |
| OH-S1 | **H-0** as §4.4.1, plus HF-19 and the D3-R1 amendments to HF-07, HF-10, HF-11 and HF-15. The executor runs locally on `oracle-test` as `ubuntu` in an interactive session (OH-D-2) | the executor named under OH-D-2 | read-only, no `sudo` | Codex review |
| OH-S2 | citations as before, plus PO-20 and PO-11 (d) and (e) | Claude, under U-10 | documentation | Codex review, then Peter. A refuted PO-14 ends the sequence. A refuted PO-20 or PO-11(d) returns the protocol to design review |
| OH-S4 | as before. `rp11_h1.py` gains `scan` (RS-1), `rb1`, `act` and `deact`. Tests add: a crash-injection test that stops at **every** PF, PT, `ACT` and CL boundary on a synthetic filesystem in the style of `durability_model.py`, and asserts the RS-1 class and that no A0 or S0 object is ever removed; journal-parser tests (torn tail, broken chain, non-canonical line, unknown `op`); a test that RS-1's code path makes no mutating call; activation-record and journal schema tests; and P-2's "later P-0 passes after RB-1 PASS" property | Claude | repository only, unwired, nothing installed | Codex review per slice, with a security-focused review |
| OH-S6 | focused commit of every reviewed input. Peter makes it available on the canonical remote. Retrieval follows only under OH-S0b | Peter | commit | controlled-path identity; retrieved commit and file digests verified on `oracle-test` |
| OH-S9 | H-2, then A-2 (pinning §4.2.5-R1 (b)), `ACT`, Pass A and `DEACT`. `ACT` and `DEACT` are now designed. Each step is separately authorized, except that CL and `DEACT` are automatic under A-2 | — | outside this amendment | — |
| **OH-S10 (new; only if needed)** | RB-1, or a read-only RS-1 scan after host loss, under its own assignment and authority | executor | §4.6.2-R1 | Codex review; Peter acceptance |

**Successor amendments** *(D3-R2)*. These rows replace or add to the D3-R1 rows
of the same name. Every slice still needs its own authority, and none is
requested here.

| Order | Slice | Assignee | Scope | Gate |
|---|---|---|---|---|
| OH-S1 | **H-0** as amended by D3-R1, plus the §4.4.2b amendments to HF-10, HF-11, HF-15 and HF-19, and HF-20 | the executor named under OH-D-2 | read-only, no `sudo` | Codex review |
| OH-S2 | citations as amended by D3-R1, plus **PO-21**, **PO-11 (f)** and **PO-20 (g)** | Claude, under U-10 | documentation | Codex review, then Peter. A refuted PO-21, PO-11 (f) or PO-20 (g) returns the activation design to review, and no grant may be linked |
| OH-S4 | as amended by D3-R1. `rp11_h1.py` gains `hold`, `backstop` and the `deact` triggers `stop-post`, `backstop` and `attest`; tree **L** gains the tool; tree **E** is removed. Tests add: (1) crash injection at every AM-0, AK-1, AM-1, AM-1R, AM-2, AV-1, AM-3, HL, CL-0 … CL-7 and BS boundary, on a synthetic filesystem with a fake manager, asserting each §4.2.5-R2 (k) cell; (2) HL's terminal predicate over synthetic `ActiveState`, `InvocationID` and capture-root sequences, including an unloaded `inactive` unit and a start that races W; (3) the BS decision table; (4) GP, by failing every journal and record write before CL-3 and asserting that an A1-intact rule is still removed and that no removal is claimed; (5) boot scoping (any `/run` object in another boot is A0); (6) attestation's preconditions and the `cleared-by-boot` conditions; (7) the holder and backstop literals against the (e) and (f) grammar (no `%`, `$`, `\` or forbidden option), extending E-2; (8) premise P-E (every pre-X-1 exit of `rp11-launch` and the bootstrap is non-zero); and (9) schema tests for `rp11-activation-record/2` and both closed `op` sets | Claude | repository only, unwired, nothing installed | Codex review per slice, with a security-focused review |
| **OH-S8b (new)** | **activation fault drill** on `oracle-test`, after H-1 PASS and before the first real A-2. It uses a test A-2, a test `pass-a.json` and a test capture root, never a real one, and injects in turn: executor and operator session loss; `SIGKILL` of the holder in ST-1.a0, ST-1.a1, ST-1.a2, ST-2 and ST-3; `SIGKILL` of CL before and after CL-3; an orderly reboot in ST-2; and an unclean reset in ST-2 (destructive, explicitly authorized). Each case records the PK result and the `deact` records. Like PO-16, a drill corroborates one host at one time and does not prove the contract | executor per U-2/OH-D-2 | host, root, destructive; its own authority | Codex review; Peter acceptance before any real A-2 |
| OH-S9 | as D3-R1, with `ACT` started by AP-2 and cleanup automatic through the holder, the backstop and the kernel boot | — | outside this amendment | — |

**Successor amendments** *(D3-R3)*. These rows replace or add to the D3-R2
rows of the same name. Every slice still needs its own authority, and none is
requested here.

| Order | Slice | Assignee | Scope | Gate |
|---|---|---|---|---|
| OH-S0 | as D3-R1, plus **OH-D-10** (§4.2.5-R3 (c)), which comes **first**. Nothing that depends on the activation design may be accepted before it | Peter, recorded by Codex | decision | Codex re-review of D3-R3, then maintainer decision |
| **OH-S0c (new)** | **R4**, a repository-only design remediation that adopts the decided OH-D-10 option into §4.2.5-R2, §4.7.2 and §4.4.2b (for Option A, §4.2.5-R3 (d) as written) | Claude | documentation | Codex re-review; Peter's acceptance of the H-1/activation design |
| OH-S4 | as D3-R2, with test (4) **replaced** by: (4) GP-R3, by failing in turn the attempt directory, the journal's creation, every append and every `fsync` before and after each removal, and the record. Each case asserts that an A1-intact rule, `pass-a.json` and tree **P**/**R** directories are still removed, in that order and each after a descriptor re-verification; that no record is written and no removal is claimed; that the next journaled attempt records `absent-before-removal` and never `removed`; and that a substituted, damaged or foreign object is kept. Added: (10) concurrency of `stop-post`, `backstop` and `attest` triggers under GP-R3 on one lock; (11) the ST-1.ur gate (H-2, AP-0, H-1R and RB-1 refuse); and, **only if R4 adopts Option A**, (12) CP's order, one-shot rule and grant-priority path, and that no fake-manager path executes `ExecStart=` unless CP exited `0` | Claude | repository only, unwired, nothing installed | Codex review per slice, with a security-focused review |
| OH-S8b | as D3-R2, plus: evidence made unwritable (a read-only or full evidence filesystem) in ST-2 and ST-3, asserting ST-1.ur and the later record; and, **only if R4 adopts Option A**, `SIGKILL` of CP before and after its removal, and a `start` repeated after CP | executor per U-2/OH-D-2 | host, root, destructive; its own authority | Codex review; Peter acceptance before any real A-2 |

**Successor amendments** *(D3-R4)*. These rows replace or add to the D3-R3
rows of the same name. Every slice still needs its own authority, and none is
requested here.

| Order | Slice | Assignee | Scope | Gate |
|---|---|---|---|---|
| OH-S0 | OH-D-10 **decided** (Option A, route (iii-a)). Still to decide: acceptance of this design after Codex's re-review of D3-R4; the §4.7.1 wordings, including D-1 as amended by D3-R4; the §4.7.2 D3-R4 dispositions; and acceptance of PO-21 (n) … (r) and PO-11 (g) with the other obligations | Peter, recorded by Codex | decision | Codex re-review of D3-R4, then maintainer decision |
| OH-S0c | **done in design** by this revision (R4). Codex re-review is pending | Claude | documentation | Codex re-review; Peter's acceptance of the H-1/activation design |
| OH-S1 | **H-0** as amended by D3-R2. HF-16 explicitly includes `DefaultTimeoutStartUSec`. No other fact is added: PO-21 (n) … (r) and PO-11 (g) are fixed by the HF-05, HF-07, HF-12 and HF-16 facts already listed | the executor named under OH-D-2 | read-only, no `sudo` | Codex review |
| OH-S2 | citations as amended by D3-R2, plus **PO-21 (n) … (r)** and **PO-11 (g)**, and PO-15's coverage of `ExecStartPre`'s printed form and flag | Claude, under U-10 | documentation | Codex review, then Peter. A refuted item returns the activation design to review, and no grant may be linked |
| OH-S3 | as before, plus the operational draft's one-host interruption text: route (iii-a) as the only interruption, and "a failed consume step is not a pass" | Claude | documentation | Codex re-review of the draft (A-1) |
| OH-S4 | as D3-R3, with test (12) now **unconditional**: CP's order (lock first, then the checks), one-shot rule, `consume-busy` on a held lock, grant-priority path, and that no fake-manager path executes `ExecStart=` unless CP exited `0`. Added: (13) T-B1 and T-B2 as amended (§4.2.5-R4 (b)); (14) the `ExecStartPre` normalization of §4.3.3 over synthetic `systemctl show` output, including a missing or extra `+` flag; (15) HL's `start-failed-before-exec` predicate; (16) CL-3's classes from a consume journal (`removed-earlier`, `absent-before-removal`); (17) AV-1's negative control and AP-0's start-timeout check; (18) the interruption literal against a grammar test in the style of E-2; and (19) schema tests for the `consume` key and the consume journal's closed `op` set | Claude | repository only, unwired, nothing installed | Codex review per slice, with a security-focused review |
| OH-S8b | as D3-R3, with the Option A items now **unconditional**: `SIGKILL` of CP before and after its removal; a `start` repeated after CP; `ubuntu`'s `stop` refused; route (iii-a) during `start-pre` and during the pass; and a holder end racing with a start (CX-1). Each case records PK for `start` and `stop`, the consume journal and the `deact` records | executor per U-2/OH-D-2 | host, root, destructive; its own authority | Codex review; Peter acceptance before any real A-2 |

**Successor amendments** *(D3-R5)*. These rows replace or add to the D3-R4
rows of the same name. Every slice still needs its own authority, and none is
requested here.

| Order | Slice | Assignee | Scope | Gate |
|---|---|---|---|---|
| OH-S0 | as D3-R4, plus acceptance of PO-21 (s) … (v) and PO-20 (h), and of the D3-R5 sentence in §4.7.1 | Peter, recorded by Codex | decision | Codex re-review of D3-R5, then maintainer decision |
| OH-S0c | **R5 done in design** by this revision. Codex re-review is pending | Claude | documentation | Codex re-review; Peter's acceptance of the H-1/activation design |
| OH-S1 | as D3-R4. HF-11 adds `/var/tmp` (type, owner, mode with the sticky bit, `(dev, ino)`). HF-19 already records its ageing | the executor named under OH-D-2 | read-only, no `sudo` | Codex review |
| OH-S2 | as D3-R4, plus **PO-21 (s) … (v)** and **PO-20 (h)** | Claude, under U-10 | documentation | Codex review, then Peter. A refuted item returns the activation design to review, and no grant may be linked |
| OH-S3 | as D3-R4, plus: route (iii-a) only while the pass is `active` (OS-6); and one start attempt per activation | Claude | documentation | Codex re-review of the draft (A-1) |
| OH-S4 | as D3-R4, with test (12) **replaced** by: (12) CP's order CQ-0 … CQ-7 on a synthetic filesystem with a fake manager, asserting that CQ-0 and CQ-1 failures create nothing, that the claim precedes every validation, and that no fake-manager path executes `ExecStart=` unless CP exited `0`. Added: (20) crash injection at **every** CQ boundary of §4.2.5-R5 (i), including between `mkdirat` and each `fsync`, followed by a second attempt that must be refused; (21) contract OSA over generated attempt sequences, with a fake manager implementing PO-21 (s) … (u): every ended attempt (failed, killed, timed out, never executed, or stopped during `start-pre`, ended `inactive` with and without unloading) followed by k further attempts, by `ubuntu` and by root, asserting that only A₁ can run `ExecStart=` and that the only exception produced is CX-4's exact combination; (22) OS-1 and OS-7 at AM-0 and `hold-start`; (23) OS-5: HL's decision under the lock racing a CP at each CQ step; (24) CL's `consume.attempt` and `consume.outcome` classification ((g)); (25) the HL reasons of §4.2.5-R5 (g), including a `consumed` line with no forked `ExecStart=`; (26) OS-8's ageing check and the `/var/tmp` mode check; and (27) schema tests for the amended `consume`, `unit`, `run-start`, `hold-start` and consume-journal fields | Claude | repository only, unwired, nothing installed | Codex review per slice, with a security-focused review |
| OH-S8b | as D3-R4, with "`SIGKILL` of CP before and after its removal" and "a `start` repeated after CP" **replaced** by: for each of (1) a CP that never runs (an unexecutable test interpreter path in a **test** unit only), (2) `SIGKILL` of CP before CQ-2, (3) a held lock at CQ-1, (4) a `/var/tmp` claim name pre-created, (5) `SIGKILL` between CQ-2's `mkdirat` and its `fsync`, (6) `SIGKILL` after CQ-3, (7) a CQ-4 precondition false and (8) a start before `hold-start`, a **repeated `start` by `ubuntu` and then by root**, each of which must be refused without `ExecStart=`. The τ, `InvocationID`, claim, consume journal, PK for `start` and `stop`, and `deact` records are recorded for each. The route (iii-a) drill during `start-pre` is withdrawn (OS-6); a drill of a root `stop` during `start-pre` is run only to observe PO-21 (u)'s end state, under its own authority | executor per U-2/OH-D-2 | host, root, destructive; its own authority | Codex review; Peter acceptance before any real A-2 |

**Successor amendments** *(D3-R6)*. These rows replace or add to the D3-R5
rows of the same name. Every slice still needs its own authority, and none is
requested here.

| Order | Slice | Assignee | Scope | Gate |
|---|---|---|---|---|
| OH-S0 | OS-6 **decided** (R6 authority). Still to decide: acceptance of this design after Codex's re-review of D3-R6, including the CX-4 statement of §4.2.5-R6 (f); the §4.7.1 wordings, including D-1 as amended by D3-R6; and acceptance of PO-21 (n) … (v), PO-20 (h) and PO-11 (g) with the other obligations | Peter, recorded by Codex | decision | Codex re-review of D3-R6, then maintainer decision |
| OH-S0c | **R6 done in design** by this revision. Codex re-review is pending | Claude | documentation | Codex re-review; Peter's acceptance of the H-1/activation design |
| OH-S3 | as D3-R5, with the route (iii-a) text **replaced** by: the executor's pre-`stop` check of OC-1 … OC-3 (§4.2.5-R6 (b)), recorded as operational evidence; the route never issued while the unit is `activating`; a hung consume step left to the start timeout; and what happens if the condition cannot be established (CX-3) | Claude | documentation | Codex re-review of the draft (A-1) |
| OH-S4 | as D3-R5, with test (21) **split**: (21a) sequences drawn only from 𝒜 (no stop job during `start-pre`; route (iii-a) only under OC-1 … OC-3, including a `stop` that lands on a later attempt after a stale read), asserting that only A₁ can run `ExecStart=`, **with no exception**; and (21b) out-of-scope sequences that inject a non-route stop job or an orderly transition during `start-pre`, asserting that the only defeat produced is CX-4's exact combination and that no grant exists during or after any pass. Added: (28) a pure evaluator of OC-1 … OC-3 over synthetic `systemctl show` output and consume journals, returning *available* only for `active` with a matching `InvocationID` and a `consumed` line, and *unavailable* for every `activating` sub-state, `deactivating`, `inactive`, `failed`, an empty or different `InvocationID`, and an absent, unreadable, torn or `consumed`-less journal; and (29) a fake-manager start timeout during CP, ending `failed` with τ changed, followed by a refused later attempt | Claude | repository only, unwired, nothing installed | Codex review per slice, with a security-focused review |
| OH-S8b | as D3-R5, plus: route (iii-a) drilled **only** on a running pass whose OC-1 … OC-3 hold, followed by a repeated `start` by `ubuntu` and by root, each refused by SB-1; a hung pre-start step in a **test** unit only, ended by the start timeout, recording `failed`, τ and a refused repeat. The root `stop` during `start-pre` stays only as a labelled observation of PO-21 (u) under its own authority. It is an act outside 𝒜, **never** route (iii-a) | executor per U-2/OH-D-2 | host, root, destructive; its own authority | Codex review; Peter acceptance before any real A-2 |

---

## 5. Decisions preserved, superseded and still required

* **Preserved:**
  * D9-2 Complete (U-5); D9-3 Complete;
  * M-9 = LB-2S conditional; M-14; M-10 (T-A in scope, R-10, T-B out of
    scope);
  * LD-7 … LD-9;
  * U-2 and U-4 … U-10, as interpreted for one host;
  * `rp11-entry-env/1`; `rp11-launch/1`; the expected image
    `04218ed2…2668572`;
  * MD-1 … MD-6.
* **Superseded:** U-1 and U-3, by Peter's topology correction. This proposal
  supersedes nothing itself. It proposes the §4.7.2 dispositions for
  decision.
* **Still required** *(original D3 list; superseded by the D3-R1 list
  below)*:
  * OH-D-1 … OH-D-9 (§3);
  * the individual §4.7.1 decisions (M-11, M-12, D-2, D-1, MD-C11; the
    withdrawal of M-1, M-3, M-4, M-8; M-2, M-5 (amended), M-6, M-7, M-13);
  * acceptance of PO-19 and of the PO-11 extensions;
  * every later authority in OH-S1 … OH-S9.

*(D3-R1)* **Decisions after D3-R1:**

* **Decided on 2026-10-04:** OH-D-1 … OH-D-9, as quoted in §3. They are no
  longer required.
* **Still required:**
  * Peter's acceptance of this design after Codex's re-review, and Codex's
    recommendation on closing `OH-H1-D3-1` and `OH-H1-D3-2`;
  * the individual §4.7.1 decisions (unchanged list);
  * acceptance of PO-19, PO-20 and PO-11 (b) … (e);
  * whether residual RR-2 is acceptable as stated, or whether the
    boot-cleared rule location of §12.9 (3) should be designed; and
  * every later authority: OH-S0b, OH-S1 … OH-S9, OH-S10, and A-2 for each
    pass.
* **Not a decision required here:** whether RB-1 or activation cleanup is
  automatic. OH-D-8 decided that, and §4.2.5-R1 and §4.6.2-R1 apply it.

*(D3-R2)* **Decisions after D3-R2:**

* The D3-R1 bullet *"whether residual RR-2 is acceptable as stated, or whether
  the boot-cleared rule location of §12.9 (3) should be designed"* is
  **withdrawn**. Codex judged RR-2 Blocking (`OH-H1-D3-R1-1`), and D3-R2 adopts
  the boot-cleared location together with supervision (§4.2.5-R2).
* **Still required**, in addition to the D3-R1 list:
  * Codex's re-review and recommendation on `OH-H1-D3-R1-1` and
    `OH-H1-D3-2`, and Peter's acceptance of this design;
  * acceptance of PO-21, PO-11 (f) and PO-20 (g);
  * OH-S8b's authority, before the first real A-2; and
  * for each pass, A-2's lease values (§4.2.5-R2 (c)).
* **No new maintainer choice** is needed for the remediation itself. The
  mechanism is a design choice within the authorized remediation, and its
  host dependencies are fail-closed proof obligations, not choices.

*(D3-R3)* **Decisions after D3-R3:**

* D3-R2's bullet *"No new maintainer choice is needed for the remediation
  itself"* is **withdrawn** for `OH-H1-D3-R2-1`.
* **Required first: OH-D-10** (§4.2.5-R3 (c)). It decides how OH-D-7's
  post-pass boundary is met: Option A (recommended, with interruption route
  (iii-a)), B or C. It changes reviewed C11 text, so only Peter can make it,
  after Codex's re-review of (b).
* **Then:** R4 (OH-S0c), Codex's re-review of it, and only then Codex's
  recommendation on `OH-H1-D3-R2-1`, `OH-H1-D3-R2-2`, `OH-H1-D3-R1-1` and
  `OH-H1-D3-2`, and Peter's acceptance of the activation design.
* **Unchanged:** the rest of the D3-R1 and D3-R2 lists.
* **Not a decision required here:** GP-R3. It implements OH-D-8's automatic
  removal of `pass-a.json` within the existing attribution rules.

*(D3-R4)* **Decisions after D3-R4:**

* **Decided on 2026-10-04:** OH-D-10, Option A with interruption route (iii-a),
  and the closure of `OH-H1-D3-R2-2` as remediated (R4 authority). They are no
  longer required.
* **Still required:**
  * Codex's re-review of D3-R4, and Codex's recommendation on
    `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2`;
  * Peter's acceptance of the H-1 and activation design;
  * the §4.7.1 wordings, including D-1 as amended by D3-R4, and the §4.7.2
    D3-R4 dispositions of C11's unit text, rule text, T-B1, T-B2, PO-11 and
    §6.5;
  * acceptance of PO-21 (n) … (r) and PO-11 (g), with the earlier
    obligations;
  * for each pass, A-2's pins, which now include the route (iii-a) literal and
    the start-timeout check; and
  * every later authority: OH-S0b, OH-S1 … OH-S10 and OH-S8b.
* **No new maintainer choice** is needed for D3-R4 itself. AR-1 … AR-8 are
  design refinements within the decided option, and each fails closed. If
  Codex or Peter judges any of them to be a choice, it is put back to Peter.
* **Unchanged:** the rest of the D3-R1, D3-R2 and D3-R3 lists.

*(D3-R5)* **Decisions after D3-R5:**

* **Still required:** Codex's re-review of D3-R5, and its recommendation on
  `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2`; Peter's
  acceptance of the H-1 and activation design; the §4.7.1 wordings, including
  the D3-R5 sentence; acceptance of PO-21 (s) … (v) and PO-20 (h), with the
  earlier obligations; and every later authority.
* **No new maintainer choice** is needed for D3-R5 itself. OS-1 … OS-8 refine
  OH-D-10 (A) within its decided unit and rule bytes, and each fails closed.
  OS-6 narrows **when** the decided route (iii-a) is used, and not who may use
  it or how. If Codex or Peter judges OS-6, or any other OS item, to be a
  choice, it is put back to Peter. Closing CX-4 in every case would change
  OH-D-10 (A) (a further unit or rule line). That is **not** proposed.
* **Unchanged:** the rest of the D3-R1 … D3-R4 lists.

*(D3-R6)* **Decisions after D3-R6:**

* **Decided on 2026-10-04:** OS-6, by Peter Duscha (R6 authority). It amends
  route (iii-a)'s timing condition. It does not change the literal, the
  executor, A-2's authority or the §9.5.3 classification.
* **Superseded:** the D3-R5 statement above that "no new maintainer choice is
  needed" as far as OS-6 is concerned. Codex found that OS-6 was a choice, and
  Peter has now made it.
* **Still required:** Codex's re-review of D3-R6, and its recommendation on
  `OH-H1-D3-R5-1`, `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and
  `OH-H1-D3-2`; Peter's acceptance of the H-1 and activation design,
  including the CX-4 statement; the §4.7.1 wordings, including the D3-R6 D-1
  additions; acceptance of the proof obligations; and every later authority.
* **No further maintainer choice** is needed for D3-R6 itself. It follows the
  decided OS-6, and its one correction, the EO sentence, only withdraws a
  claim. Closing CX-4 in every case would still change OH-D-10 (A), and that
  is **not** proposed. If Codex judges that accepting CX-4 outside 𝒜 needs a
  separate decision, it is put to Peter.

## 6. Files created or changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | **created** (this file) |
| *(D3-R1)* the same file | **revised in place** by D3-R1. See §12.6 |
| *(D3-R2)* the same file | **revised in place** by D3-R2. See §13.6 |
| *(D3-R3)* the same file | **revised in place** by D3-R3. See §14.6 |
| *(D3-R4)* the same file | **revised in place** by D3-R4. See §15.6 |
| *(D3-R5)* the same file | **revised in place** by D3-R5. See §16.6 |
| *(D3-R6)* the same file | **revised in place** by D3-R6. See §17.6 |

No other file was created, changed or deleted. Pre-existing uncommitted
maintainer and Codex changes (ten modified and sixteen untracked paths at
start) were preserved untouched. Current status, Handover and §20 were **not**
updated (assignment, final paragraph).

## 7. Commands and checks run (repository-local, read-only)

| Command or check | Result |
|---|---|
| `git status --short`, `git rev-parse HEAD` | HEAD `236872647f3edd5fed5c7f14512518e13eeb8f07`; ten modified and sixteen untracked documentation paths, all pre-existing |
| `wc -l` / `wc -c` and `sha256sum` of the governing inputs | as §1. The prompt is 8,875 bytes, SHA-256 `22ea1f38…54d086` |
| `cat`, `sed -n` and `grep -n` over AGENTS.md, the plan, Handover, the decision records, C11, D2, the operational draft, the R5 assignment and handback, and the test-server document | as §1 |
| `ls -la infra/rp11-launch …`; `cat infra/rp11-launch/expected.sha256` | inventory as the handback states; image row `04218ed2…2668572` |
| `python3` (standard-library `json`, `hashlib`) reading the manifest's `rp11_launch` section | manifest v31, `installed: false`, `wired: false`; XD digests as §4.3.2 |
| `grep -rln 'PO-19\|PO-20'` and a search for `OH-D` in `docs/` | no prior use |
| `ls` of the output path before writing | absent |
| `git diff --no-index --check /dev/null ⟨this file⟩` | run after writing. Reports only the deliberate two-space Markdown line breaks in the header lines, the same style as the preparation handback |

## 8. Checks not run, and why

* **No host fact was observed**, on any host. No `uname`, package query,
  `systemctl`, `/proc`, `binfmt_misc`, `id` or `stat` outside the repository
  tree was run. Every host-dependent statement is a requirement, a documented
  value or a recorded historical value, never an observation. The authority
  excludes host inspection.
* **No SSH, `rsync`, build, installation, `sudo`, polkit, service, database,
  capture-root, retained-path, cleanup, commit or push action** was taken.
* **No upstream source was read.** PO-8, PO-11, PO-12, PO-14, PO-15, PO-19 and
  D9-1 remain uncited (U-10 needs H-0's versions first).
* **No test suite, formatter, linter or type checker** was run. No code
  changed, and the documented remote suite path is outside this authority. No
  suite figure is claimed.

## 9. Security, production-isolation, operational and rollback implications

* **This return:** one new documentation file. It has no effect on any host.
  Reverting it means deleting the file.
* **Security.** The one-host design keeps LB-2S's two prevention claims
  unchanged:
  * no client-derived process state reaches the entry; and
  * the entry's environment is the literal, given PO-9 and PO-14.

  It **loses** observer independence (OH-D-3), and it makes U-8 an authority
  boundary rather than a privilege boundary for `ubuntu` (OH-D-6). **RR-1**
  (IA-8): expected digests travel with the bytes they authenticate. That
  protects against T-A, not T-B, consistently with M-10.
* **Production isolation.** §4.1.2 makes it a stop condition (E-1), a
  repository test (E-2) and an assignment sentence (E-3). OH-D-1 must remove
  the one documented route by which production could be a source.
  *(D3-R1: OH-D-1 has removed it. Retrieval is direct from the canonical Git
  remote on `oracle-test`, §4.1.4.)*
* **Operational.**
  * H-1 adds a loaded but ungranted unit and root-owned files to the
    disposable server, and they persist across reboot.
  * `unattended-upgrades`, if enabled (HF-17), can invalidate the baseline at
    any time. That fails closed, at the cost of a re-citation and H-1R.
  * `/var/tmp` is shared with the retained evidence. HF-15 records its
    capacity.
* **Rollback.** Every state has a digest-guarded procedure (§4.6.2). Only a
  removed unit needs `daemon-reload`. Records are never deleted. Whether any
  rollback is automatic is OH-D-8.
  *(D3-R1: OH-D-8 is decided. RB-1 is separately authorized and identity- and
  digest-guarded (§4.6.2-R1). Activation cleanup is automatic (§4.2.5-R1).
  §12.8 restates the implications.)*
* *(D3-R2)* §13.8 states the implications of the supervised, boot-scoped
  activation.
* *(D3-R3)* §14.8 states the implications of GP-R3 and of the open OH-D-10.
* *(D3-R4)* §15.8 states the implications of the start-consumed grant and of
  route (iii-a).
* *(D3-R5)* §16.8 states the implications of the one-start-attempt barriers.
* *(D3-R6)* §17.8 states the implications of the decided OS-6 and of the
  scoped contract OSA.

## 10. Proposed independent-review focus

1. Whether **IA-1 … IA-15** are complete. In particular, whether any other
   property of the two-host design silently depended on host separation.
   IA-5 (the clock) and IA-12 (repository provenance) are the subtle cases.
2. **§4.2.1's choice to load the unit at H-1 without the rule.** It meets U-7
   and U-8 literally. Is the literal reading what U-8 intended, given OH-D-6?
3. **Running `rp11_h1.py` as root under `sudo`'s open environment**
   (§4.2.4). It is not the capture entry, but it writes the H-1 record.
4. **The `link`-then-`unlink` publication and guard G**, especially crash
   windows between `link` and the journal line. *(D3-R1: Codex found this to
   be Blocking `OH-H1-D3-1`. Replaced by §4.2.4-R1. The new focus list is
   §12.9.)*
5. **§4.3.3's "explicit version-bound list, never `--all`" rule.** It avoids
   reading any environment, but completeness then rests on the PO-15
   citation. Is deriving the emptiness of the E set from
   F/D/N plus the fragment digest sound for the installed version?
6. **The PO-17 fail-closed bounds rule** and the unmounted-namespace case.
7. **The order H-2 → A-2 → `ACT` → H-2b → start**, and whether it preserves
   C11's "H-2 immediately before each pass".
8. **OH-D-5 option (a)**: whether losing A1-14, A1-15 and A1-31 … A1-33 is
   acceptable for MD-2's purposes.

## 11. Statement of authority used

I used only the repository-documentation and read-only repository-inspection
authority of `C-P5.0-R5-RP11-H1-D3`. **No host, implementation or execution
authority was used.** No SSH, `rsync`, `oracle-test` or production-host
access, upstream research, build, installation, privilege, `systemctl`,
polkit, service or database action, capture-root, evidence-pass, cleanup,
commit or push occurred. Nothing in this document is an accepted design or an
executable assignment.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9 (as a whole), PO-14, PO-17,
PO-18 and H-1 remain open. RP-11 remains unwired and unmet. Package RAID item
`P5.0-R5` remains Blocking. `plan.is_executable=False`. Package 5.0 remains
not ready.

Claude stops here, pending Codex's independent review and Peter Duscha's
decisions.

---

## 12. D3-R1 remediation and handback *(D3-R1, 2026-10-04)*

Work ID `C-P5.0-R5-RP11-H1-D3-R1`. Author: Claude. Independent reviewer:
Codex. Decision owner: Peter Duscha.

### 12.1 Outcome and recommendation

**DESIGN REMEDIATION READY FOR RE-REVIEW** (§0-R1). Both Blocking findings are
addressed mechanically, and the revised proposal is internally consistent by
the checks in §12.7. **Neither finding is declared closed.** Only Codex may
recommend closure after independent re-review, and Peter Duscha retains
acceptance authority. The proposal remains **inactive and unaccepted**. No
H-0, implementation or host step is begun or requested.

**Recommendation.** Codex re-reviews §4.2.4-R1, §4.2.5-R1, §4.6.1-R1 and
§4.6.2-R1, using the focus list in §12.9. Residual RR-2 (§4.2.5-R1 (h)) needs
an explicit judgement: either it is acceptable as stated, or the boot-cleared
rule location becomes a further bounded design item. *(D3-R2: Codex judged
RR-2 Blocking as `OH-H1-D3-R1-1`. RR-2 is withdrawn. See §4.2.5-R2 and §13.)*
No maintainer decision is missing for the remediation itself. OH-D-7 and OH-D-8 supplied what Codex
said the remediation depended on.

### 12.2 Requirements and governing sections examined

| Source | SHA-256 (bytes) | Read |
|---|---|---|
| `.agents/AGENTS.md` | — | completely |
| `docs/implementation-plan.md` | — | reading map, §0, §16 and §20 |
| `docs/review/Handover information` | `293dce2d…6008c` (25,743) | active block completely; superseded blocks scanned |
| remediation prompt | `7e2aaf6b…9188ec` (9,302) | completely |
| remediation authority | `957632e1…1c837c7a` (1,404) | completely |
| OH-D decision record | `8edb27db…b7afa15c` (4,637) | completely |
| Codex's independent review | `aa10ebe3…afdd9e` (6,973) | completely |
| this proposal as reviewed (D3) | `df50f62a…1814e` (91,310) | completely |
| original D3 prompt and authority | `22ea1f38…54d086`; `9ab372ff…15e24a` | completely |
| prerequisite decisions (U-1 … U-10) | `17a32ab4…57b9cc` (4,702) | completely |
| C11 proposal | as §1 | §4.4.3.4 … §4.4.3.7 and §12 again, for the rule text, H-1, rollback and emergency disable |
| D2 proposal | as §1 | §5.11 and §5.13 again |
| `docs/operations/disposable-test-server.md` | `19f358e7…183ca8` (7,668) | completely, including the active restriction banner |
| `tools/phase_5_0_evidence/durability_model.py` | `b2c69ad7…a86a40b` | module docstring and limits: the `O_PATH` `fsync` defect, the containing-directory durability rule, and `RENAME_NOREPLACE` as an unconfirmed target fact. These are reused in invariant D and PO-20 |
| `tools/phase_5_0_evidence/capture_contract.py` | — | `canonical_bytes` (journal lines and records) |

The D1-R2, D2-R2, I-7, I-7-R1 and H-1-preparation records were relied on as §1
cites them, and were not re-read in full. D3-R1 changes none of the facts §1
takes from them.

### 12.3 Disposition of the two Blocking findings

**`OH-H1-D3-1` — addressed in design; open pending re-review.** Each demand of
the remediation prompt and where it is met:

| Prompt requirement | Where |
|---|---|
| durable intent before every file and directory mutation | invariant W; PF-2; PT-2 |
| identity, digest, owner, mode and intended final path bound by the intent | `file-intent` and `tree-intent` fields; `file-identity` and `dir-identity` lines (PF-4, PT-3, PT-4) |
| file-data, journal and parent-directory `fsync` order | invariant D; PF-4 … PF-8; PT-3 … PT-9; journal "Append" |
| namespace operation and no-replace semantics | invariant N; PF-6 (`linkat`); PT-8 (`renameat2` `RENAME_NOREPLACE`); PO-20 (b), (c) |
| durable completion and commit record | `file-linked`, `tree-linked`, `reload-done`, `v1-pass`, `run-end` |
| recovery at every boundary, immediately before and after the final name appears | §4.6.2-R1 boundary table, rows "PF-2 … PF-6, not yet returned" and "PF-6 returned, before PF-7", and the PT rows |
| proof that a path belongs to this run without removing an unrelated one | class A1-intact; G-R1; proof P-1 |
| classification, retention and escalation of unverifiable paths | classes A1-damaged, A0 and S0; "Escalation of what cannot be attributed" |
| exact ST-0.x and ST-1 terminal mapping | §4.6.1-R1 (ST-0.0 … ST-0.6, suffix `+X`) |
| which recovery actions belong to the separately authorized RB-1 | §4.6.2-R1 RB-1; RS-1 placement in §4.6.1-R1 |
| a later H-1 not permanently blocked by attributable paths, while unattributable ones are never removed | proof P-2; RS-A (§4.2.3) |
| none of: weakened refusal, deletion of uncertain paths, crash window as residual risk, automatic H-1 rollback | PF-1, PT-1 and RS-A keep refusal; G-R1 removes only A1-intact objects; the window is **closed** for every final name (invariant I), and W-T can create only non-final, non-blocking S0 names; RB-1 separate |

**`OH-H1-D3-2` — addressed in design; open pending re-review.**

| Prompt requirement | Where |
|---|---|
| identifier grammar; one-pass and one-boot binding | §4.2.5-R1 (a) |
| evidence paths, owners, groups and modes | §4.2.5-R1 (c); §4.2.3 D3-R1 rows |
| closed record schema, serialization, destination, SHA-256 and length | §4.2.5-R1 (g) |
| binding to A-2, the H-1 and H-2 records, boot ID, `pass-a.json`, staged rule and active rule | §4.2.5-R1 (b), (c), (d) AP-0 and (g) |
| fail-closed handling of pre-existing targets and temporary paths | AP-0; PF-1; PF-6 `EEXIST`; no temporary names (`O_TMPFILE`); AC-1, AC-3, AC-5 |
| crash-consistent publication using item 1's protocol | AM-1 … AM-3 use PF; the journal of §4.2.4-R1 (b) |
| partial states before, between and after the three publications | §4.2.5-R1 (h) AC-1 … AC-7; §4.2.2 D3-R1 table |
| automatic cleanup at `ACT` failure and every pass terminal state | §4.2.5-R1 (e), "When it runs" 1 … 4 |
| the live grant disabled first | CL-3 before CL-5; `ACT` runs CL before writing its record |
| a path that cannot be attributed or removed | CL-3 and CL-5 classes; AC-3, AC-5, AC-9 |
| retained immutable success, failure and cleanup evidence | `act` and `deact-⟨k⟩` records (never deleted); retained journals |
| ST-1 verified after cleanup | CL-6 |
| reboot, process death, repeated or incomplete `DEACT` | AC-10, AC-11, AC-12; idempotence; locks; RR-2. *(D3-R2: AC-10, AC-11 and RR-2 are withdrawn and replaced by §4.2.5-R2 (k) and (l))* |
| activation cleanup distinguished from RB-1 | §4.2.5-R1 (e) ("none is an H-1 rollback"); §4.6.2-R1 RB-1 and its final table |
| `pass-a.json` never left for a later authority after an `ACT` failure | CL-5, always attempted; AC-4, AC-6, AC-7. An unattributable `pass-a.json` is escalated at once as AC-9 residual |
| removal of the live rule never claimed without evidence | "Grant removal is claimed only with evidence": journal, `ENOENT` and PK after the AV-1 positive control |

### 12.4 The corrected contracts, in brief

* **Publication (§4.2.4-R1).** Each file is an unnamed `O_TMPFILE` inode,
  journaled, filled and synchronized, then linked under its final name. A
  directory set is built as a temporary tree, sealed against its journaled
  inventory, and renamed into place without replacement. No final name ever
  refers to this run's object before its identity line is durable.
* **Recovery (§4.6.1-R1, §4.6.2-R1).** RS-1 is a read-only classification.
  RB-1 is separately authorized, write-ahead and journaled, removes only
  A1-intact objects under G-R1, and never removes records.
* **Activation (§4.2.5-R1).** `ACT` publishes `pass-a.json`, then the rule,
  checks that the grant is live with PK, and commits by writing the `act`
  record. CL removes the rule first, then `pass-a.json`. It runs in-process on
  `ACT` failure and as `DEACT` at every terminal state, after any death or
  reboot, and again until it reaches `st1-verified` or a precise AC-9
  HARD STOP. *(D3-R2: "after any death or reboot" is superseded. CL runs from
  the holder's `ExecStopPost=` and from the backstop, and a kernel boot clears
  both files (§4.2.5-R2).)*

### 12.5 Affected sections and change ledger

"Retained" means that the D3 text stays in place, labelled **Original D3 text,
superseded by D3-R1**. "Annotated" means that a *(D3-R1)* note was appended to
the D3 text, which itself is unchanged. "Cell amended" means that the D3 cell
text was replaced in place, and the original wording is quoted here.

| Section | D3-R1 change |
|---|---|
| header | paragraph **added** ("Revision D3-R1") |
| §0 | §0-R1 **added**. The D3 outcome is retitled §0-D3 and **retained**, with a note added |
| §2 | Disposition cells **amended** for IA-1, IA-2, IA-3, IA-5, IA-7, IA-10, IA-11 and IA-14. Each D3 cell read "**decision OH-D-n**" (IA-2: "**decision OH-D-4**; pre-pass synchronization outside the trusted path (§4.1.4)"; IA-3: "**decision OH-D-5**; catalogue re-expression (OH-S3)"; IA-5: "**decision OH-D-3** (part of the evidence-semantics change)"; IA-14: "**decision OH-D-6** (authority boundary)"). IA-8 **annotated** |
| §3 | paragraph **added** after the introduction; a **Decided** line **added** to each of §3.1 … §3.9. The analysis is unchanged |
| §4.1.1 | retrieval row **added**. `ACT`/`DEACT` row **cell amended** (D3: "executor under A-2; root through `sudo -n`") |
| §4.1.3 | TR-0 and TR-1 **cells amended** (D3: "the operator's session reaching `oracle-test` (OH-D-2)"; "*E_c*; the client's own credential (OH-D-2)"). Credential bullet **amended** (D3: "the client's own credential, at TR-1, under OH-D-2;"). The PostgreSQL sentence is **replaced** (D3: "PostgreSQL peer authentication applies only if OH-D-5(b) is chosen.") |
| §4.1.4 | introductory paragraph **replaced** (D3: "Under OH-D-4(a), repository bytes reach `/opt/freedom-blades/platform` on `oracle-test` by OH-D-1's transport **before** any H-0, rebuild, H-1, H-2 or pass step starts. Nothing in that transport is trusted:"). Items 1 … 4 unchanged |
| §4.1.5 | heading **amended** (D3: "(only if OH-D-3(a) is decided)") |
| §4.2.1 | paragraph **added**, with the §4.2.6 erratum |
| §4.2.2 | D3 table **retained** and labelled, its ST-1.x cell **annotated**; D3-R1 states table **added** |
| §4.2.3 | D3-R1 path rows and RS-A **added**. D3 creation paragraph **retained**; replacement paragraph **added** |
| §4.2.4 | **retained** and labelled. **§4.2.4-R1 added** |
| §4.2.5 | **retained** and labelled. **§4.2.5-R1 added** |
| §4.3.2 | `authority_limit` row and `context` paragraph **added**. `directories` **cell amended** (`dev` and `ino` appended) |
| §4.3.3 | V-set bullet **amended** ("`ControlGroup` and `ControlGroupId`; and" became "…; ") and the `ActiveState`/`SubState` bullet **added** |
| §4.3.4 | D3-R1 order bullet **added**. The D3 bullet is retained |
| §4.3.5 | paragraph **added** |
| §4.4.1 | HF-19 and the HF-07, HF-10, HF-11 and HF-15 amendments **added**. HF-15 and HF-18 **annotated** |
| §4.4.2a | **added** (PO-20; PO-11 (d), (e)) |
| §4.4.3 | paragraph **added** |
| §4.5.2, §4.5.3 | paragraph **added**; two rows **added** |
| §4.6.1, §4.6.2 | **retained** and labelled. The ST-1.x row of §4.6.2 is **annotated** "withdrawn". **§4.6.1-R1 and §4.6.2-R1 added** |
| §4.6.3 | reboot and package-drift cells **annotated** |
| §4.7.1 | paragraph **added** |
| §4.7.2 | rows for C11 §4.4.3.7, C11 §12, C11 §14 and D2 §5.13 **annotated** |
| §4.7.3 | four D3 status cells **annotated**; amendments table **added** |
| §4.7.4 | OH-S0 and OH-S6 **annotated**; amendments table **added** (OH-S0, OH-S0b, OH-S1, OH-S2, OH-S4, OH-S6, OH-S9, OH-S10) |
| §5 | D3 list **annotated**; D3-R1 list **added** |
| §6, §9, §10 | row or note **added** |
| §12 | **added** (this section) |

The successor slices, gates and decisions still required are in §4.7.4's and
§5's D3-R1 additions.

### 12.6 Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | revised in place, as §12.5 lists |

No other repository file was created, changed or deleted. The pre-existing
uncommitted changes (31 status entries at start, 21 of them untracked, all
documentation) were preserved untouched. Current status, Handover, §20, the
decision register and the active restriction were **not** updated. A scratch
copy of the D3 file, used for the diff checks, lives outside the repository.

### 12.7 Commands and checks run, and checks not run

**Run** (repository-local and read-only, apart from editing this file and a
scratch copy outside the repository):

| Command or check | Exact result |
|---|---|
| `git status --short`; `git rev-parse HEAD` (start and end) | HEAD `236872647f3edd5fed5c7f14512518e13eeb8f07`; 31 entries, 21 untracked, at start and at end. The set is unchanged, and this file was already untracked |
| `sha256sum` and `wc -c` of the inputs in §12.2, and of this file before editing | as §12.2; D3 file `df50f62a…1814e`, 91,310 bytes |
| `cat`, `sed -n`, `grep -n` over AGENTS.md, the plan (§0, §16, §20 and the reading map), Handover, the decision, authority, review and prompt records, C11 §4.4.3.4 … §4.4.3.7 and §12, D2 §5.11 and §5.13, and the test-server document | read as §12.2 |
| `grep -rn 'PO-20\|OH-R1\|RS-A\|RS-1'` over `docs/` before writing | `PO-20` appeared only in this file's own §7 search note. The other three identifiers were unused |
| **(1) OH-D dispositions:** `grep -n 'OH-D-[0-9]'`, filtered for "open", "undecided", "still required", "if OH-D", "accepts" and "must remove" | Counted over §0 … §11 (excluding this §12): 132 lines mention an OH-D item. Nine match the filter. Eight are original D3 text with an appended *(D3-R1 … decided)* or *(superseded …)* note. The ninth is the D3-R1 row for handback P-1, which says "**decided**; §4.7.1 wording still open". Every other occurrence is a §3 analysis paragraph followed by its **Decided** line, history in §0-D3, or a statement of the decided disposition |
| **(2) production as a source:** `grep -n -i 'production\|workspace host\|repository host'` | no text proposes the production or workspace host as a source, controller, relay, destination, fallback or rollback target. §3.1's options (a), (c) and (d) are marked **not selected**, and the premise of (d) false |
| **(3) `pass-a.json` after an `ACT` failure:** `grep -n 'pass-a.json'`, filtered for "separate authority", "later authority" and "left for" | Counted over §0 … §11: 3 matches. The only text leaving it to a separate authority is §4.6.2's D3 ST-1.x row. It is labelled superseded and annotated "withdrawn by D3-R1". The other two matches, §4.2.2's D3-R1 table note and §4.6.2's superseded-text label, state the opposite |
| **(4) every activation terminal path:** manual check of §4.2.5-R1 (h) AC-1 … AC-12 against (e)'s outcome rule | each row ends in `st1-verified` with CL-6, or in AC-9's HARD STOP, which records the grant class and removes a proven rule first. AC-1 is an INVALID RUN with no activation object; an object it finds is escalated |
| **(5) H-1 rollback never automatic:** `grep -n 'RB-1'`, filtered for "automatic" | Counted over §0 … §11: all 5 matches state that RB-1 is separate, not automatic, or contrast it with automatic CL. None makes RB-1 automatic |
| **(6) no host command, assignment or implementation added:** `diff` of the D3 copy against this file, with added lines filtered for `/goal`, `ssh `, `rsync `, code fences, `sudo -n /` and `git fetch\|clone` | one added code fence: PK's `pkcheck` design literal in §4.2.5-R1 (f). It is a proposed specification, like D3's `sudo -n` stub, not an assignment or authority. Of the other two matches, one is the §0-D3 note saying the `rsync` route is prohibited, and the other is unchanged D3 text inside the amended IA-3 line. No `/goal`, no assignment and no source, test or manifest change |
| **Markdown structure:** a scratch Python check for balanced fences, consistent table pipe counts and trailing whitespace; then a check for unescaped `\|` inside table code spans | fences balanced; 0 inconsistent tables. Five table code spans with a bare `\|` were found in the new D3-R1 tables and escaped. The D3 copy had none |
| `git diff --no-index --check /dev/null ⟨this file⟩` (untracked file) | exit 3. It reports only the 6 deliberate two-space line breaks in header lines 3 … 14. The D3 copy reports the same 6 |
| `git diff --check` (tracked files) | exit 0 |
| `diff` of the D3 copy against this file, for removed or changed D3 lines | 40 D3 lines changed. Each is an entry in §12.5 (a cell amended or annotated, or a paragraph replaced). No D3 paragraph was deleted without being kept or quoted |

**Not run, and why:**

* **No host check** of any kind on any host, so the PO-20 and PO-11 (d) and
  (e) semantics remain uncited and unobserved. The authority excludes host
  access and upstream research.
* **No test suite, formatter, linter or type checker.** No code changed, and
  the prompt prohibits suite runs. No suite figure is claimed.
* **No Markdown linter.** None is configured in the repository. The scratch
  structural check above is the substitute.
* **No re-read in full** of D1-R2, D2-R2, I-7, I-7-R1 or the H-1-preparation
  handback, which are relied on as §1 cites them (§12.2).

### 12.8 Security, production-isolation, operational and rollback implications

* **This return** changes one documentation file. It has no effect on any
  host. It is reverted by restoring the D3 bytes, whose SHA-256 is in the
  header.
* **Security.** The design never removes an object it cannot attribute by
  identity **and** digest (P-1). A grant whose identity is proven is removed
  first and verified by a privileged decision check. The root tools still run
  under `sudo`'s environment (§4.2.4's stated limit). G-R1's
  re-verification-to-`unlinkat` interval, and the journal's integrity against
  forgery, are T-B under OH-D-6 and M-10. That is stated, not hidden.
  **RR-2:** after an unplanned reboot the rule is live until `DEACT` runs.
  The bootstrap refuses (diagnostic only), and the exposure does not exceed
  `ubuntu`'s `sudo`. *(D3-R2: withdrawn. See §13.8.)*
* **Production isolation.** Unchanged and strengthened. OH-D-1 removes the
  workspace host as a source, controller, relay, destination, fallback and
  rollback target. Retrieval is direct from the canonical remote on
  `oracle-test`, under separate authority. No D3-R1 procedure names any other
  host. E-1 to E-3 continue to apply to `ACT`, `DEACT`, RS-1 and RB-1.
* **Operational.**
  * PO-20's semantics must hold for the observed kernel and filesystems.
    Otherwise P-0 or AP-0 is INVALID RUN.
  * `O_TMPFILE` and `renameat2` support are host prerequisites.
  * Journals live in `/var/tmp`, so `systemd-tmpfiles` ageing (HF-19) could
    remove one before RB-1. The handback's digest and length (OH-D-9) allow a
    verified copy to substitute.
  * Records accumulate in the record store and are never deleted. A later H-1
    needs RS-A's pinned inventory.
  * Window W-T can leave S0 directories under pre-existing system
    directories. They are reported and kept, and only Peter's separate
    decision may dispose of them.
* **Rollback.** H-1 rollback (RB-1) is never automatic. It needs separate
  authority (OH-D-8), is idempotent and journaled, and never deletes records.
  Activation cleanup (CL) is automatic under A-2 and removes the rule, then
  `pass-a.json`. A residual that cannot be attributed is escalated and never
  forced.

### 12.9 Proposed independent-review focus

1. **Invariant I and window W-T.** Does P-2 hold, with S0 directories
   confined to run-unique names in pre-existing parents and a child left by
   W-T kept inside an unsealed tree? Is the seal (PT-7) sufficient to keep
   anything unjournaled out of a final tree?
2. **PO-20.** Linking an `O_TMPFILE` inode through `/proc/self/fd` with
   `AT_SYMLINK_FOLLOW`, and calling glibc `renameat2` through `ctypes` as root
   under `sudo`'s environment. Is the PO-20 list complete for the claims made,
   and is "refuted means redesign" the right response?
3. *(D3-R2: answered by Codex as Blocking `OH-H1-D3-R1-1` and superseded by
   §13.9.)* **RR-2.** Is a rule that stays live after an unplanned reboot, until the
   first `DEACT`, acceptable under OH-D-7's "no live Polkit grant may … remain
   after the pass"? Or should a successor design put the active rule in a
   boot-cleared directory such as `/run/polkit-1/rules.d`? That would need a
   PO-11 citation that the installed polkit loads and watches that directory,
   and a decision on who creates it.
4. **PK.** Running `pkcheck` as root against a dropped-privilege subject, with
   AV-1's positive control. Is a later "not authorized" result adequate
   evidence that the grant is disabled, given PO-11 (d) and (e)?
5. **G-R1's stated limit.** Is the root-only interval between
   re-verification and `unlinkat` correctly assigned to T-B?
6. **RS-A.** Is admitting a retained record store, bound to a pinned
   inventory of record digests, consistent with "do not weaken pre-existing-path
   refusal"?
7. **CL-2.** CL removes the grant even while the unit is active. That prevents
   the operator's `stop` from then succeeding. Should DEACT instead wait for
   the §9.5.3 interruption, and for how long?
8. **AC-7 and the PASS commit.** Treating a linked `activated` record as
   `ACT` PASS even if `run-end` is missing.
9. §10's D3 items 1 … 3 and 5 … 8 remain open for review. Item 4 is superseded
   by this remediation.

### 12.10 Statement of authority used

I used only the repository-documentation and read-only repository-inspection
authority of `C-P5.0-R5-RP11-H1-D3-R1`. **No host, network, credential,
implementation or execution authority was used.** No SSH, `rsync`, Git or
network retrieval, `oracle-test` or production-host access, credential
creation or installation, upstream research, build, installation, privilege,
`sudo`, `systemctl`, Polkit, `pkcheck`, service or database action,
H-0, H-1, H-2, `ACT`, `DEACT`, RB-1, evidence pass, cleanup, commit or push
occurred. No retained R4/R5 path was inspected. No test suite was run. Nothing
here is an accepted design, an executable assignment, or authority for any
step.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18, PO-19,
PO-20 and H-1 remain open. RP-11 remains unwired and unmet. Package RAID item
`P5.0-R5` remains Blocking. `plan.is_executable=False`. Package 5.0 remains
not ready.

Claude stops here, pending Codex's independent re-review.

---

## 13. D3-R2 remediation and handback *(D3-R2, 2026-10-04)*

Work ID `C-P5.0-R5-RP11-H1-D3-R2`. Author: Claude. Independent reviewer:
Codex. Decision owner: Peter Duscha.

### 13.1 Outcome and recommendation

**DESIGN REMEDIATION READY FOR RE-REVIEW** (§0-R2). `OH-H1-D3-R1-1` is
addressed mechanically by §4.2.5-R2 and §4.4.2b, and the revised proposal is
internally consistent by the checks in §13.7. **`OH-H1-D3-R1-1` and
`OH-H1-D3-2` are not declared closed.** Only Codex may recommend closure, and
Peter Duscha retains acceptance authority. The proposal remains **inactive and
unaccepted**. No H-0, implementation or host step is begun or requested.

**Recommendation.** Codex re-reviews §4.2.5-R2 (with its supersession label in
§4.2.5-R1) and §4.4.2b against the finding, using §13.9. No maintainer decision
is missing for the remediation itself. The mechanism is a design choice within
the authorized remediation. Its host dependencies are fail-closed proof
obligations, PO-21, PO-11 (f) and PO-20 (g), and they need acceptance like
PO-19 and PO-20.

### 13.2 Requirements and governing sections examined

| Source | SHA-256 (bytes) | Read |
|---|---|---|
| `.agents/AGENTS.md` | `ca907aa7…70c9f39e` (35,077) | completely |
| `docs/implementation-plan.md` | `822d40b6…9017fe83` (148,273) | reading map, §0, §16 and §20 |
| `docs/review/Handover information` | `4449cfe9…6c786e700` (27,613) | completely; the active R2 block governs |
| R2 prompt | `748102ea…f2e478b` (7,058) | completely |
| R2 authority | `9328bbb2…c527` (1,651) | completely |
| Codex's D3-R1 re-review | `10fd2396…a927bb443` (5,222) | completely |
| OH-D decision record | `8edb27db…b7afa15c` (4,637) | completely |
| Codex's D3 review | `aa10ebe3…afdd9e` (6,973) | completely |
| this proposal as re-reviewed (D3-R1) | `edf48932…611351b1` (190,074) | completely |
| D3-R1 authority and prompt | `957632e1…1c837c7a` (1,404); `7e2aaf6b…9188ec` (9,302) | completely |
| D1-R2 decision | `10daa599…de9c3b40` (1,970) | completely |
| D2-R2 acceptance | `133191c5…3787c678` (2,050) | completely |
| I-7 review | `dd5a0833…c7d755d` (7,175) | completely |
| I-7-R1 acceptance | `bc14d8f9…7a2928` (2,385) | completely |
| C11 proposal | `f6405cd9…12f70b` (209,120) | §4.4.3.4 … §4.4.3.7 (unit, rule text, pass configuration, rollback), §12, and every line naming `pass-a.json` or `rules.d` (§4.4.3.4, §9) |
| D2 proposal | `4859ab4e…366174` (201,284) | §5.13 (rollback and emergency disable) |
| `docs/operations/disposable-test-server.md` | `e92f7e6e…a3eda578b1eb3` (7,679) | completely, including the active R2 restriction banner |
| `tools/phase_5_0_evidence/rp11_launch.py` | `0d4ece45…f626a08` (16,942) | the `EXECVE_*` constants only: the launcher image names the bootstrap path and no pass-configuration path |

### 13.3 Disposition of `OH-H1-D3-R1-1`

**Addressed in design; open pending re-review.** The prompt's six conditions:

| Condition | Where it is met |
|---|---|
| 1. A-2 authorizes `ACT` for exactly one pass and one boot | §4.2.5-R2 (n) 2 and 4: one identifier, one holder (PO-21 (m)), one capture root; the files exist only on `/run` in the boot AM-0 checked against A-2's `boot_id` |
| 2. no live grant before A-2 or after the pass | (n) 1 and 3: no rule before AP-2. HL ends at the pass's terminal state, and the holder's end runs CL with the rule first; the latency bound is in (g). *(D3-R3: the "after the pass" part is withdrawn. It is `OH-H1-D3-R2-1`, blocked on OH-D-10, §4.2.5-R3 (b), (c).)* |
| 3. process death, session loss, power loss and reboot need no later human action to disable the grant | (k): every cell; M-S for deaths and sessions (PO-21 (a), (c), (j)), M-B for kernel boots (PO-20 (g), PO-21 (g)) |
| 4. grant disabled first, then `pass-a.json` removed | CL-3 before CL-4 and CL-5, unchanged from D3-R1. GP makes CL-3 independent of evidence input/output. A kernel boot removes both together, so no instant has the grant live after `pass-a.json` has gone |
| 5. cleanup automatic under A-2 and distinct from RB-1 | (c)'s DEACT sentence covers the `stop-post`, `backstop` and `attest` triggers; (o): CL, BS and attestation never touch H-1 objects, and RB-1 stays separate and never automatic |
| 6. no claimed success without durable evidence and a post-check | (n) 5; `cleared-by-boot`'s four conditions; GP never claims a removal; attestation records only with CL-4 and CL-6 |

The prompt's required specification items:

| Item | Where |
|---|---|
| paths, owners, groups, modes, identities, digests | (b); (c) (pinned tool and literal digests); the H-1 record's `files` (§4.3.2 note) |
| publication and removal order; durability boundaries | (d); PT and PF unchanged; (h) CL-0 … CL-7 and CL-5b; PO-20 (g) on `tmpfs` versus the durable journal |
| installed or staged without a standing grant | (a) last paragraph; (b): only the tool is installed, in tree **L**; the units are transient and created under A-2 |
| binding to A-2, activation ID, pass ID, H-1/H-2 records and boot ID | (c); AM-0's `run-start`; the unit name is the activation ID; `rp11-activation-record/2` |
| every boundary before and after the grant appears | (d) "On failure" column; (k) |
| death, session loss, power loss and reboot at every state | (k) |
| repeated, interrupted and concurrent cleanup | CL-0 lock and exclusive attempt directory; BS-1 … BS-4; attestation precondition; AC-12 note |
| foreign, damaged or unverifiable objects | D3-R1 classes and escalation unchanged; CL-1 boot scoping (A0 in another boot); CL-5b S0 under `/run` |
| ST-1 and ST-1+R terminal mapping | (j); (h) Outcome |
| immutable evidence, what survives a reboot, OH-D-9 binding | (m) |
| version-bound PO-11/PO-20 facts and H-0 observations | §4.4.2b: PO-11 (f), PO-20 (g), PO-21; HF-10, HF-11, HF-12, HF-15, HF-19, HF-20 |
| implementation and crash-injection tests | §4.7.4 D3-R2 OH-S4 tests (1) … (9); OH-S8b drill |
| rollback and recovery without automatic RB-1 | (o); §4.6.2-R1 D3-R2 note |

**Withdrawn D3-R1 statements** (each is kept in place, labelled *(D3-R2)*):

* §4.1.1, the `ACT`/`DEACT` row's "runs it in an interactive session";
* §4.2.2, ST-1.d1's "the next `DEACT` attempt";
* §4.2.5-R1 (a), "is then due (AC-10)";
* §4.2.5-R1 (e), "When it runs" items 1, 3 and 4;
* §4.2.5-R1 (h), AC-10, AC-11 and residual RR-2;
* §4.6.3, the reboot cell's AC-10 and RR-2 sentences;
* §4.7.3, row RR-2;
* §5, the RR-2 bullet; and
* in §12, the 12.1 judgement request, the 12.3 reboot row, the 12.4
  "after any death or reboot", the 12.8 RR-2 bullet and the 12.9 item 3.

### 13.4 The corrected automatic cleanup contract, in brief

* **Where the grant lives.** The rule and `pass-a.json` are created only on the
  `/run` tmpfs. No kernel boot can carry them forward (M-B).
* **Who holds it.** `ACT` and the wait for the pass run in a transient system
  service, `⟨activation_id⟩.service`, which AP-2 creates under A-2. PID 1
  supervises it, outside every login session. Its environment is PID 1's, and
  its code is the root-owned tool installed by H-1.
* **When it ends.** HL ends it within Δ of the pass's terminal state, at W if
  no pass starts, on any observation error, at L (`RuntimeMaxSec=`), or on any
  death.
* **What then runs.** `ExecStopPost=` runs CL every time: the rule first, PK,
  then `pass-a.json` and the activation directories, the ST-1 check and the
  records. A backstop timer, armed before any file exists, re-runs CL every R
  seconds until a terminal record exists, then disarms itself. GP removes an
  attributable rule even when no evidence can be written.
  *(D3-R3: "within Δ of the pass's terminal state" does not bound the grant
  after the pass. That is `OH-H1-D3-R2-1`, §4.2.5-R3 (b). GP is completed by
  GP-R3, which also removes `pass-a.json` and the directories,
  §4.2.5-R3 (e).)*
* **After an unclean boot.** Nothing is left to disable. Attestation, which
  disables nothing, writes the record, and every later RP-11 step refuses
  until it exists.
* **What remains.** DF-1 (a CL failure combined with a root-issued
  userspace-only restart that A-2 prohibits), SL-1 (deliberate root acts, as
  OH-D-6 and M-10 already state) and GU (an `unlinkat` failure, retried and
  bounded by the boot). None of them defers disabling the grant after a single
  death, session-loss, power-loss or reboot event.

### 13.5 Affected sections and change ledger

"Annotated" means that a *(D3-R2)* note was appended and the earlier text is
unchanged. "Cell amended" means that a note was appended inside an existing
table cell.

| Section | D3-R2 change |
|---|---|
| header | "Revision D3-R2" paragraph **added** |
| §0 | §0-R2 **added** before §0-R1. §0-R1 gains a one-line D3-R2 note |
| §4.1.1 | `ACT`/`DEACT` row **cell amended** |
| §4.1.3 | path note **added** after the TR table (TR-2, TR-5, TR-10) |
| §4.2.1 | paragraph **added** |
| §4.2.2 | note **added** after the D3-R1 table: activation rows superseded, ST-1.d1's "Left by" withdrawn, and ST-1's empty `/etc` directory withdrawn |
| §4.2.3 | note **added**: activation rows superseded; tree **E** withdrawn; tool in tree **L**; parents |
| §4.2.4-R1 (e) | note **added**: tool member; M-3 and ST-0.3 withdrawn; V-1's absence list |
| §4.2.5-R1 | supersession label **added** at the head; notes **added** to (a), after (e)'s "When it runs" list, after (h)'s table, and before RR-2 |
| §4.2.5-R2 | **added** ((a) … (o)) |
| §4.3.2 | note **added** (`absent`, `files`, `citations`) |
| §4.3.4 | D3-R2 order bullet **added** |
| §4.3.5 | paragraph **added** (path; launcher unaffected) |
| §4.4.1 | pointer **added** |
| §4.4.2b | **added** (PO-11 (f), PO-20 (g), PO-21; HF amendments; HF-20) |
| §4.4.3 | paragraph **added** |
| §4.5.3 | paragraph **added** |
| §4.6.1-R1 | note **added** (ST-0.3) |
| §4.6.2-R1 | notes **added** (RB-1 precondition and order; the activation rows of the final table) |
| §4.6.3 | reboot **cell amended** |
| §4.7.2 | D3-R2 disposition table **added** (C11 rule location, the pass-configuration path in C11 §4.4.3.4 and §9, D2 §5.13) |
| §4.7.3 | D3-R2 traceability table **added** |
| §4.7.4 | D3-R2 successor table **added** (OH-S1, OH-S2, OH-S4, OH-S8b, OH-S9) |
| §5 | D3-R2 decision list **added** |
| §6, §9 | row and bullet **added** |
| §12.1, §12.3, §12.4, §12.8, §12.9 | RR-2 and deferral statements **annotated** (one line in §12.1 was re-wrapped) |
| §13 | **added** (this section) |

### 13.6 Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | revised in place, as §13.5 lists |

No other repository file was created, changed or deleted. The pre-existing
uncommitted changes (34 status entries at start, 24 of them untracked, all
documentation) were preserved untouched. Current status, Handover, §20, the
decision register and the active restriction were **not** updated. Scratch
copies (the D3-R1 bytes, drafts and a Markdown checker) live outside the
repository, in the session scratchpad.

### 13.7 Commands and checks run, and checks not run

**Run** (repository-local and read-only, apart from editing this file and
writing scratch files outside the repository):

| Command or check | Exact result |
|---|---|
| `git status --short`; `git rev-parse HEAD` (start and end) | HEAD `236872647f3edd5fed5c7f14512518e13eeb8f07`; 34 entries, 24 untracked, at start and at end. This file was already untracked |
| `sha256sum`, `wc -c` of the inputs in §13.2 and of this file before editing | as §13.2; D3-R1 file `edf48932…611351b1`, 190,074 bytes, equal to the copy used for the diff checks |
| `cat`, `sed -n`, `grep -n` over the §13.2 inputs | read as §13.2 |
| `grep` of `infra/rp11-launch/{launch.c,start.s,select.h}` and `rp11_launch.py` for `pass-a`, `/etc/`, `/run/` | no pass-configuration path in the launcher sources. `EXECVE_ARGV` names only `/usr/local/libexec/freedom-blades-rp11/rp11_entry.py`, so moving `pass-a.json` changes no frozen digest |
| identifier collision search: `grep -cw` for each new identifier over the D3-R1 copy, C11 and D2 | none in use, except `AB-1` (a D2 build assumption) and `GP` (D2's `#GP` exception mnemonic). `AB-1` was renamed `AK-1` before submission. `GP` is unambiguous in context and kept. `grep -rln` for `PO-21`, `DF-1`, `ST-1.bc`, `OH-S8b` and `rp11-activation-record/2` over `docs/` outside this file: no match |
| **(1) no grant left pending human action:** `grep -n -i` for "first RP-11 action", "once the host can be reached", "until an actor", "is then due", "next `DEACT` attempt", "until `DEACT` runs", "live until", "first `DEACT`", "waits for", "wait for a later" and "later actor" | 17 matching lines before §13. **9** are D3-R1 statements, and each is labelled withdrawn by an adjacent *(D3-R2)* note or by the §4.2.5-R1 head label: §4.2.2 ST-1.d1, §4.2.5-R1 (a), (e) item 3, AC-10, RR-2 (2 lines), §4.6.3, §12.8 and §12.9 (3). **8** are D3-R2 text that states the opposite or quotes a withdrawn phrase: §0-R2, the §4.2.2 note, the §4.2.5-R1 (e) note, §4.2.5-R2 (a), (h) GP, (i) and (l), and the §4.3.4 order |
| **(2) every boundary:** manual check of the §4.2.5-R2 (k) matrix against (h)'s outcome rule and (j) | 12 state rows × 6 events, every cell filled. Each ends in SP, BS or BC, which lead to `st1-verified` or an AC-9 ST-1+R HARD STOP, or in INV with no activation object. No cell has an attributable live grant waiting for a person. The two "attestation" cells are evidence-only states in which no file can exist |
| **(3) `pass-a.json` automatic:** `grep -n 'pass-a.json'`, filtered for "separate authority", "later authority", "left for" and "for a later" | 6 matches before §13. The only text leaving it to another authority is §4.6.2's D3 ST-1.x row, already labelled "withdrawn by D3-R1". The others state the opposite, or are the D3-R1 §12 check rows |
| **(4) RB-1 never automatic:** `grep -n 'RB-1'`, filtered for "automatic" | 8 matches before §13. Every one states that RB-1 is separate, not automatic, or contrasts it with automatic CL, or is the D3-R1 §12 check row. §4.2.5-R2 (o) adds that CL, BS and attestation never invoke RB-1 |
| **(5) OH-D-1 … OH-D-9 and the D3-R1 publication protocol not weakened:** `diff` of the D3-R1 copy against this file, removed lines | 9 D3-R1 lines changed, all by appending a note or re-wrapping: the §4.1.1 row, §4.2.5-R1 (a)'s last line, the §4.6.3 reboot cell, two §12.1 lines re-wrapped around the note, the §12.3 row, the end lines of §12.4 and §12.8, and §12.9 item 3's first line. Two of them contain an OH-D reference (the §4.1.1 row and the §12.1 line), and their D3-R1 wording is intact. No §3 **Decided** line, no PF, PT, journal, RS-1 or G-R1 line, and no P-1 or P-2 line changed |
| **(6) no host command, assignment or implementation added:** added lines filtered for `/goal`, `ssh `, `rsync `, code fences, `sudo -n` and `git fetch\|clone` | three fenced design literals: the holder (§4.2.5-R2 (e)), the backstop ((f)) and attestation ((i)). They are specification, like D3's `sudo -n` stub and D3-R1's `pkcheck` literal, and they are not assignments or authorities. The only other match is the amended §4.1.1 row, whose `sudo -n` is D3 text. No `/goal`, no `ssh`, `rsync` or `git` retrieval, and no source, test or manifest change |
| **Markdown structure:** a scratch Python check for balanced fences, consistent table pipe counts, unescaped pipes in table code spans and trailing whitespace | fences balanced; 65 tables (59 before §13), 0 inconsistent; 0 unescaped pipes in code spans. Trailing whitespace only on the 6 deliberate header line breaks (lines 3 … 14), the same as the D3-R1 copy |
| `git diff --no-index --check ⟨D3-R1 copy⟩ ⟨this file⟩` | no whitespace error reported. Exit 1 only because the files differ |
| `git diff --no-index --check /dev/null ⟨this file⟩` | reports only the same 6 header line breaks as D3-R1 |
| `git diff --check` (tracked files) | exit 0 |

The (1) to (6) and Markdown results were re-run after §13 was written, and
§13.7 reports the final figures. §13's own lines add only quotations of the
searched phrases, inside this table.

**Not run, and why:**

* **No host check** of any kind on any host. PO-21, PO-11 (f) and PO-20 (g)
  remain uncited and unobserved, and polkit's `/run/polkit-1/rules.d` support
  in particular is not assumed. The authority excludes host access and
  upstream research. Each obligation is fail-closed at AP-0.
* **No test suite, formatter, linter or type checker.** No code changed, and
  the prompt prohibits suite runs. No suite figure is claimed.
* **No Markdown linter.** None is configured in the repository. The scratch
  structural check above is the substitute.

### 13.8 Security, production-isolation, operational and rollback implications

* **This return** changes one documentation file and affects no host. It is
  reverted by restoring the D3-R1 bytes, whose SHA-256 is in the header.
* **Security.**
  * The grant's lifetime is now bounded mechanically by the kernel boot and
    procedurally by a PID-1-supervised holder with a retrying backstop.
    Neither bound depends on a login session or on a person.
  * The activation code runs with PID 1's environment rather than `sudo`'s,
    which narrows §4.2.4's stated limit for `ACT` and CL. The executor's
    `sudo` environment reaches only the `systemd-run` client (PO-21 (b)).
  * GP puts disabling the grant ahead of evidence. It never claims a removal
    and never weakens attribution.
  * DF-1, SL-1 and GU are stated exactly in §4.2.5-R2 (l). OH-D-6's limit is
    unchanged: ST-1 is not privilege-inert, and nothing here makes it so.
  * **Residual RR-2 is withdrawn.**
* **Production isolation.** Unchanged. Every D3-R2 procedure runs on
  `oracle-test` only, and E-1 to E-3 apply to AP-2, the holder, BS and
  attestation. The production workspace host is never a source, controller,
  relay, destination, fallback or rollback target (OH-D-1).
* **Operational.**
  * Two transient units exist per activation, and none outlives the boot.
  * The backstop runs every R seconds until it disarms. It is read-only while
    the holder lives (BS-1).
  * The pass now has a hard lease L and a start window W, both pinned in A-2.
  * The host must provide `tmpfs` `/run`, polkit `/run/polkit-1/rules.d`
    support and the PO-21 systemd semantics. Otherwise no activation is
    possible, and the design returns to review.
  * One more root-owned file is installed (the tool in tree **L**), and
    `/etc/freedom-blades-rp11/` is no longer created.
  * OH-S8b adds a destructive drill before the first real A-2.
* **Rollback.** RB-1 is still separately authorized and never automatic
  (OH-D-8). It now also removes the installed tool, has no tree **E**, never
  touches `/run`, and requires every activation to be terminated with a
  record. Activation cleanup (CL, BS and the kernel boot) is automatic under
  A-2. Records are never deleted.

### 13.9 Proposed independent-review focus

1. **M-B's premise.** Is placing the rule in `/run/polkit-1/rules.d`, and
   `pass-a.json` in `/run/freedom-blades-rp11/`, sound? Is PO-11 (f) complete,
   in particular on precedence between equal basenames, on late-created
   directories ((ii)) and on polkitd holding no rule across a restart ((iv))?
2. **PO-21 (c) and (j).** Is `ExecStopPost=` plus a periodic backstop a
   sufficient automatic trigger set? Is the "armed before any file" ordering
   (AK-1 before AM-1) the right place to close the window?
3. **HL's terminal predicate** ((g)) and premise P-E. Does relying on the
   capture root's existence, and on a failed unit's `InvocationID`, avoid every
   unit-unloading ambiguity (PO-21 (k))? Is the bounded latency Δ an
   acceptable reading of "no grant after the pass"? *(D3-R3: Codex answered
   no, `OH-H1-D3-R2-1`.)*
4. **DF-1.** Is a double fault that needs a root-issued userspace-only restart,
   which A-2 prohibits, correctly placed outside the single-event guarantee?
   Should AP-0's disarm requirement for automatic soft-reboot paths be
   strengthened?
5. **Attestation.** After an unclean boot only the **record** waits for an
   actor, and every later step refuses until it exists. Is that consistent
   with OH-D-8's "retaining an immutable activation/failure record", or should
   a boot-time attesting unit be designed? (§4.2.5-R2 (a) explains why one was
   not chosen.)
6. **GP.** Is removing an A1-intact rule without this attempt's own
   write-ahead line consistent with the D3-R1 publication and recovery
   contract, given that P-1 rests on the A1-intact check and the descriptor
   re-verification? *(D3-R3: GP-R3 extends the same reasoning to
   `pass-a.json` and the directories, §4.2.5-R3 (e), (i).)*
7. **The `pass-a.json` relocation.** It amends C11's proposed path (§4.7.2) and
   withdraws tree **E**. Does any other accepted record bind
   `/etc/freedom-blades-rp11/`?
8. **The installed tool.** Activation code moves from the ubuntu-owned
   repository copy, checked by the stub, to a root-owned copy installed by
   H-1. Is that the right binding, and is H-2's comparison of it sufficient?
9. §12.9's items 1, 2 and 4 … 8, and §10's D3 items, remain open as stated
   there. §12.9 item 3 is superseded by this list.

### 13.10 Statement of authority used

I used only the repository-documentation and read-only repository-inspection
authority of `C-P5.0-R5-RP11-H1-D3-R2`. **No host, network, credential,
implementation or execution authority was used.** No SSH, `rsync`, Git or
network retrieval, `oracle-test` or production-host access, credential
creation or installation, upstream research, build, installation, privilege,
`sudo`, `systemctl`, `systemd-run`, Polkit, `pkcheck`, service or database
action, H-0, H-1, H-2, `ACT`, `DEACT`, RB-1, attestation, drill, evidence
pass, cleanup, commit or push occurred. No retained R4/R5 path was inspected.
No test suite was run. Nothing here is an accepted design, an executable
assignment, or authority for any step.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18, PO-19,
PO-20, PO-21 and H-1 remain open. RP-11 remains unwired and unmet. Package
RAID item `P5.0-R5` remains Blocking. `plan.is_executable=False`. Package 5.0
remains not ready.

Claude stops here, pending Codex's independent re-review.

---

## 14. D3-R3 remediation and handback *(D3-R3, 2026-10-04)*

Work ID `C-P5.0-R5-RP11-H1-D3-R3`. Author: Claude. Independent reviewer:
Codex. Decision owner: Peter Duscha.

### 14.1 Outcome and recommendation

**BLOCKED REMEDIATION** (§0-R3).

* **`OH-H1-D3-R2-2`** is addressed mechanically by GP-R3 (§4.2.5-R3 (e) … (i)).
  When evidence cannot be written, CL removes the attributable rule, then
  `pass-a.json`, then the activation directories, each after a descriptor
  re-verification, and claims nothing without a durable record.
* **`OH-H1-D3-R2-1`** cannot be remediated within the accepted texts. While
  C11's `stop` grant is live during the pass, and while disabling needs a
  root act and a polkitd reload after its trigger, the grant is live for a
  non-zero interval after any pass that ends abruptly (§4.2.5-R3 (b)). Only a
  grant disabled before `ExecStart=` closes that interval. That requires
  changing C11's reviewed unit text (T-B1) and rule verbs, and the route for
  interrupting a pass. Those are maintainer decisions.
* **The exact missing decision is OH-D-10** (§4.2.5-R3 (c)). Option A,
  start-consumed grant, with interruption route (iii-a), is recommended and
  specified in (d) but not adopted.
* **Not declared closed:** `OH-H1-D3-R2-1`, `OH-H1-D3-R2-2`, `OH-H1-D3-R1-1`
  and `OH-H1-D3-2`. Only Codex may recommend closure, and Peter Duscha retains
  acceptance authority. The proposal stays **inactive and unaccepted**.

**Recommendation.**

1. Codex re-reviews §4.2.5-R3, using §14.9, and in particular confirms or
   refutes the impossibility argument of (b).
2. If it holds, Peter decides OH-D-10.
3. The smallest safe successor is R4 (OH-S0c): a narrow repository-only
   remediation that adopts the decided option. For Option A it adopts
   §4.2.5-R3 (d) and the conditional PO-21 (n) … (r) and PO-11 (g), and then
   returns for Codex re-review.

No host step, H-0 or implementation precedes R4.

### 14.2 Requirements and governing sections examined

| Source | SHA-256 (bytes) | Read |
|---|---|---|
| `.agents/AGENTS.md` | `ca907aa7…70c9f39e` (35,077) | completely |
| `docs/implementation-plan.md` | `f005c976…5c987465` (150,067) | reading map, §0, §16 and §20 (the R3 current action) |
| `docs/review/Handover information` | `fb414307…4fc1bcc4` (29,577) | completely; the active R3 block governs |
| R3 prompt | `57a45062…91c1076c` (8,093) | completely |
| R3 authority | `3678a98d…3832ab91` (1,590) | completely |
| Codex's D3-R2 re-review | `a98d94c0…ef65730a` (5,705) | completely |
| Codex's D3-R1 re-review | `10fd2396…927bb443` (5,222) | completely |
| OH-D decision record | `8edb27db…b7afa15c` (4,637) | completely |
| D3-R2 authority and prompt | `9328bbb2…7c335527` (1,651); `748102ea…7f2e478b` (7,058) | completely |
| this proposal at the start of D3-R3 | `9268a534…a0f260b9` (268,582) | completely: header, §0 … §13, with §4.2.5-R1, §4.2.5-R2, §4.4.2b, §4.6.2-R1 and §13 in detail |
| C11 proposal | `f6405cd9…6312f70b` (209,120) | §4.4.3.4 … §4.4.3.7 (unit text, T-B1 absences, rule text and the reason for `stop`, H-1/H-2/rollback); the T-B1 row of its test table |
| D1-R2 decision | `10daa599…de9c3b40` (1,970) | completely (M-9 = LB-2S, conditional) |
| operational draft | `5c6046fc…dcca7de6` (174,711) | C-10, C-15, X-3 and §9.5.3's heading and interruption rules, by search, for when a pass ends |
| `docs/operations/disposable-test-server.md` | `63f03d12…e808ddef` (7,692) | the active R3 restriction banner, §1 and §3 opening |

### 14.3 Disposition of both findings

**`OH-H1-D3-R2-1`: BLOCKED REMEDIATION; open.** The prompt's points:

| Prompt point | Where answered |
|---|---|
| replace polling as the mechanism claimed to establish the post-pass boundary | §4.2.5-R2 (g) latency paragraph and (n) 3 **withdrawn** as grant-boundary claims; HL kept only as the activation's lifetime control; §4.2.5-R3 (b) "What the current design therefore establishes" |
| a coupling in which the terminal transition triggers or includes grant-first cleanup | §4.2.5-R3 (b): no trigger at or after the end can give a zero interval. (d): under OH-D-10 (A) the start includes the disabling, which is stronger than "the end includes it" |
| normal exit, early failure, signal death, timeout, operator interruption | (d), table "Each terminal cause" (Option A); (b), GB-2 (current design) |
| exact unit relationship and ordering; who owns the terminal transition | (d), "Unit relationship and ordering" |
| cleanup cannot execute, is killed or times out | (d): CP failure means `ExecStart=` never runs (PO-21 (o)); (e) and (g) for CL |
| may the capture unit be reported terminal before the grant is disabled? | current design: **yes**, which is the defect ((b)). Option A: no, for any pass ((d)) |
| holder, `ExecStopPost=`, backstop and observation without two concurrent owners | (d), "Owners": CP is part of the start and one-shot; CL is the single cleanup owner; all serialize on one lock |
| the exact terminal state and the evidence that the grant is already absent | (d), "The terminal transition and its evidence" |
| version-bound PO-21 facts and H-0 observations | (d), PO-21 (n) … (r) and PO-11 (g), conditional on Option A; §4.4.2b note |
| do not solve it by a faster poll, a bounded exposure or a redefinition | none is used. Option B, the redefinition, is put to Peter and not recommended |
| if the absolute boundary cannot be met: the smallest exact decision | OH-D-10, §4.2.5-R3 (c) |

**`OH-H1-D3-R2-2`: addressed in design; open pending re-review.**

| Prompt point | Where answered |
|---|---|
| attempt directory or journal cannot be created | GP-R3 entry E-a; (g) row 1 |
| journal write or `fsync` failure before and after grant removal | E-b, E-c; (g) rows 2 and 3 |
| identity and digest re-verification immediately before each removal | GP-2, GP-4, GP-5 |
| an unlink or directory-removal failure | GP-2, GP-4, GP-5 "On failure"; classes `grant-unremovable`, `unremovable`, `present-nonempty-unremoved`; (g) row 5 |
| repeated and concurrent `stop-post` and backstop attempts | (e), "Repeated and concurrent attempts"; (g) rows 7 and 8 |
| what can and cannot be claimed without a durable record | (e), "What can and cannot be claimed …"; (h) |
| ST-1 and ST-1+R when cleanup succeeds but evidence cannot be persisted | (e), "Result" and the mapping table; (f) ST-1.ur |
| distinguishing "removed without a record" from foreign or damaged objects | (e), "Removed without a record, or foreign or damaged?" |
| an unverifiable or foreign object stays retained and escalated | GP-1, GP-2, GP-4, GP-5; (e) last list; P-1 unchanged |

### 14.4 The corrected contracts, in brief

**Pass-terminal coupling (not adopted; OH-D-10).** *(D3-R4: adopted under
OH-D-10 (A, iii-a) by §4.2.5-R4. This paragraph is history.)*

* Under the current design, the grant is live during the pass and is removed
  after it ends. A non-zero post-pass interval is therefore unavoidable, and
  the proposal no longer claims otherwise.
* Under Option A:
  * the rule grants `start` only;
  * the capture unit's single added `ExecStartPre=+…consume` step removes the
    rule, waits for PK *not authorized*, and records it, all before PID 1 runs
    `ExecStart=`;
  * a failure of that step means no pass runs;
  * every pass, whatever ends it, therefore ends with no grant; and
  * a hung pass is interrupted by root under A-2.

**Evidence-unwritable cleanup (adopted; GP-R3).**

* When CL cannot write evidence, it still removes, in order, the A1-intact rule
  (with the post-check), `pass-a.json` and the activation directories, each
  after a descriptor re-verification.
* It writes no record and claims nothing. It leaves ST-1.ur, and the next
  journaled trigger records that as `st1-verified` (with
  `absent-before-removal`) or as ST-1+R.
* Every later RP-11 step refuses until that record exists.
* A foreign or damaged object is never removed.

### 14.5 Affected sections and change ledger

"Annotated" means that a *(D3-R3)* note was appended and the earlier text is
unchanged. "Cell amended" means that a note was appended inside an existing
table cell.

| Section | D3-R3 change |
|---|---|
| header | "Revision D3-R3" paragraph **added** |
| §0 | §0-R3 **added** before §0-R2. §0-R2 gains a one-paragraph D3-R3 note |
| §4.2.5-R2 | supersession label **added** at the head; (g) latency paragraph, (h) GP, (i) attestation, (j) states, (k) matrix conclusion and (n) proof **annotated** |
| §4.2.5-R3 | **added** ((a) … (j)) |
| §4.3.4 | D3-R3 order bullet **added** |
| §4.4.2b | paragraph **added** (GP-R3's obligations; conditional PO-21 (n) … (r) and PO-11 (g)) |
| §4.6.2-R1 | note **added** after the D3-R2 note (GP-R3, ST-1.ur, RB-1 precondition) |
| §4.7.2 | paragraph **added** (conditional C11 dispositions, not made) |
| §4.7.3 | D3-R3 traceability table **added** |
| §4.7.4 | D3-R3 successor table **added** (OH-S0, OH-S0c, OH-S4, OH-S8b) |
| §5 | D3-R3 decision list **added** |
| §6, §9 | row and bullet **added** |
| §13.3 | condition-2 row **cell amended** |
| §13.4, §13.9 | "What then runs" bullet, and items 3 and 6, **annotated** |
| §14 | **added** (this section) |

### 14.6 Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | revised in place, as §14.5 lists |

No other repository file was created, changed or deleted. The pre-existing
uncommitted changes (37 status entries at start, 27 of them untracked, all
documentation) were preserved untouched. Current status, Handover, §20, the
decision register and the active restriction were **not** updated. A copy of
the D3-R2 bytes and the scratch checks live outside the repository, in the
session scratchpad.

### 14.7 Commands and checks run, and checks not run

**Run** (repository-local and read-only, apart from editing this file and
writing scratch files outside the repository):

| Command or check | Exact result |
|---|---|
| `git status --short`; `git rev-parse HEAD` (start and end) | HEAD `236872647f3edd5fed5c7f14512518e13eeb8f07`; 37 entries, 27 untracked, at start and at end. This file was already untracked |
| `sha256sum`, `wc -c` of the §14.2 inputs and of this file before editing | as §14.2. The D3-R2 file is `9268a534…a0f260b9`, 268,582 bytes, equal to the scratch copy used for the diff checks |
| `cat`, `sed -n`, `grep -n` over the §14.2 inputs | read as §14.2 |
| identifier collision search: `grep -rlE` over `docs/` outside this file, and `grep -cE` over the D3-R2 copy, for `OH-D-10`, `GP-R3`, `ST-1.ur`, `OH-S0c`, `CP-n`, `GB-n` and `Z-n` | no prior use of any of them. A first draft used `F-1 … F-3` for the facts of §4.2.5-R3 (b). The same search found C11's `F-2` and `F-4`, which this file cites in IA-6 and PB-1, so they were renamed `GB-1 … GB-3` before submission |
| **(1) no text relies on polling for the post-pass boundary:** `grep -n -i` before §14 for "within Δ", "latency", "HL ends at the pass", "no grant after the pass", "no live grant after", "grant after the pass" and "remain after the pass" | 20 lines. **7** are D3-R2 statements, each labelled withdrawn by the §4.2.5-R2 head label and an adjacent *(D3-R3)* note or cell amendment: (g) "Latency bound", the (k) ST-3 EP cell, (n) 3, the §4.3.4 D3-R2 order, the §13.3 row, the §13.4 bullet and §13.9 item 3. **1** is the OH-D-7 quotation in §3.7. **12** are D3-R3 text that states the withdrawal or the open boundary |
| **(2) no path reports the pass terminal while an attributable grant is live** | **not met by the current design, and stated as such** (§4.2.5-R3 (b), "What the current design therefore establishes"). Under OH-D-10 (A), not adopted, every pass path is met by construction ((d), "Each terminal cause"). No text claims that the current design meets it |
| **(3) evidence failure never leaves an A1-intact `pass-a.json` or directory:** `grep -n -i` before §14 for "GP applies to the rule only", "removed only with this attempt", "evidence-unwritable" | the only text that kept `pass-a.json` under evidence failure is D3-R2 (h)'s item 3 and its last two sentences, labelled withdrawn by the head label and the (h) note. Every other match is a failure-class name or GP-R3 text. GP-R3's E-a, E-b and E-c each continue into GP-4 and GP-5 |
| **(4) success never claimed without durable evidence:** lines added before §14 containing `st1-verified` or `removed-verified` | 5 lines with `st1-verified`. Each makes it conditional on a later journaled attempt with its own PK and CL-6, or restricts its classes. 1 line with `removed-verified`, which says a record **never** uses it for an object that GP-R3 removed |
| **(5) `/run` boot clearing, process-death cleanup and RB-1 preserved; OH-D-1 … OH-D-9 and D3-R1 not weakened:** `diff` of the D3-R2 copy against this file, removed lines; added lines naming RB-1 | **3** D3-R2 lines changed, all by an appended note: the §13.3 condition-2 cell, and the last lines of §13.9 items 3 and 6. No §3 **Decided** line, no PF, PT, journal, RS-1, G-R1, P-1, P-2, M-B, M-S, AP-0 … AM-3, BS or attestation line changed. No added line makes RB-1 automatic. The added lines naming RB-1 state that it is preserved or stays separately authorized, that it keeps strict write-ahead removal, that its precondition refuses ST-1.ur, or list it among things not done or tested |
| **(6) no host command, assignment or implementation added:** added lines filtered for `/goal`, `ssh `, `rsync `, code fences, `sudo -n` and `git fetch\|clone` | apart from this row's own quotation of the filter, one `ini` fence holding the unit line that Option A **would** add (§4.2.5-R3 (d)), and two option-table cells quoting design literals (Option A's `ExecStartPre=+…` and (iii-a) `systemctl stop`, Option C's `systemctl start`). They are options put to Peter, like D3-R2's holder literal, and they are not assignments or authorities. No `/goal`, no `ssh`, `rsync` or `git` retrieval, and no source, test, unit, rule or manifest file change |
| **Markdown structure:** a scratch Python check for balanced fences, consistent table pipe counts, unescaped pipes in table code spans and trailing whitespace | fences balanced (10 fence lines); 80 tables (74 before §14), 0 inconsistent; 0 unescaped pipes in code spans. Trailing whitespace only on the 6 deliberate header line breaks (lines 3 … 14), as in D3-R2 |
| `git diff --no-index --check ⟨D3-R2 copy⟩ ⟨this file⟩` | no whitespace error reported. Exit 1 only because the files differ |
| `git diff --no-index --check /dev/null ⟨this file⟩` | reports only the same 6 header line breaks as D3-R2 |
| `git diff --check` (tracked files) | exit 0 |

The (1) to (6) and Markdown results were re-run after §14 was written, and
§14.7 reports the final figures. §14's own lines add only quotations of the
searched phrases, inside this table and §14.3.

**Not run, and why:**

* **No host check** of any kind on any host. PO-21, PO-11 (f) and (g) and
  PO-20 (g) remain uncited and unobserved. In particular, the systemd facts
  that (b) relies on (`ExecStopPost=` after the main process ends) and that
  Option A would rely on (PO-21 (n) … (r)) are stated as obligations, not
  observed. The authority excludes host access and upstream research.
* **No test suite, formatter, linter or type checker.** No code changed, and
  the prompt prohibits suite runs. No suite figure is claimed.
* **No Markdown linter.** None is configured in the repository. The scratch
  structural check above is the substitute.

### 14.8 Security, production-isolation, operational and rollback implications

* **This return** changes one documentation file and affects no host. It is
  reverted by restoring the D3-R2 bytes, whose SHA-256 is in the header.
* **Security.**
  * **The post-pass grant boundary is open.** The design no longer claims
    OH-D-7's "no live grant after the pass". Until OH-D-10 and R4, no
    activation design is acceptable, and no A-2 may be prepared.
  * Option A would remove every grant from the duration of the pass, and the
    operator's `stop` route with it. Under OH-D-6 the root interruption route
    (iii-a) adds no privilege that `ubuntu` lacks, but it moves the
    interruption from a Polkit grant to an act under A-2's authority. A root
    `ExecStartPre=+` step would run fixed, root-owned code at every start of
    the capture unit, including a start by `ubuntu` under the grant. It takes
    no operand and nothing from the requester (PO-21 (n)), and it is a review
    focus.
  * GP-R3 never removes an unattributed object, never claims a removal and
    leaves P-1 unchanged. It removes `pass-a.json` sooner when evidence fails,
    which narrows what a stray start could use.
* **Production isolation.** Unchanged. Every procedure runs on `oracle-test`
  only, and E-1 to E-3 apply to GP-R3 and, if adopted, CP. The production
  workspace host is never a source, controller, relay, destination, fallback
  or rollback target (OH-D-1).
* **Operational.**
  * While evidence is unwritable, the backstop fires every R seconds, read-only
    once nothing is left. Later RP-11 steps refuse until a record exists.
  * Option A would add one unit line and change the rule. Both are H-1 bytes,
    so a later H-1 (and RB-1 of any earlier one) would be needed if they
    changed after an installation. None exists today.
* **Rollback.** RB-1 is still separately authorized and never automatic
  (OH-D-8). Its precondition refuses ST-1.ur. Activation cleanup (CL with
  GP-R3, the backstop and the kernel boot) is automatic under A-2. Records are
  never deleted.

### 14.9 Proposed independent-review focus

1. **The impossibility argument** (§4.2.5-R3 (b)). Are GB-1 … GB-3 right? Is
   there a mechanism, within C11's reviewed unit and rule text and OH-D-7's
   literal reading, that disables a grant live during the pass before the
   pass's terminal instant, for every cause? If there is, OH-D-10 is
   unnecessary.
2. **OH-D-10's options** ((c)). Are A, B and C the complete smallest set? Is
   (iv), "a failed consume step is not a pass", consistent with RP-11's
   definition of a pass and with A-2's "one pass"?
3. **Option A's mechanics** ((d)). The one-shot rule CP-2; the lock released at
   `hold-start`; CP's grant-priority path; PO-21 (n) … (r); and whether a root
   `ExecStartPre=+` is compatible with LB-2S's prevention claims and PO-14.
4. **GP-R3** ((e)). Is removal without the attempt's own write-ahead lines
   consistent with D3-R1, given that P-1 rests only on the `ACT` journal's
   identity lines and the descriptor re-verification? Is `absent-before-removal`
   the right class for an object that GP-R3 removed?
5. **ST-1.ur** ((f)). Is "cleared, unrecorded, and every later step refuses"
   consistent with OH-D-8's "retaining an immutable activation/failure
   record"?
6. **The `cleared-by-boot` clarification** ((e)): the class asserts only its
   four conditions.
7. §13.9's items 1, 2, 4, 5, 7 and 8, §12.9's open items and §10's D3 items
   remain as stated there.

### 14.10 Statement of authority used

I used only the repository-documentation and read-only repository-inspection
authority of `C-P5.0-R5-RP11-H1-D3-R3`. **No host, network, credential,
implementation or execution authority was used.** No SSH, `rsync`, Git or
network retrieval, `oracle-test` or production-host access, credential
creation or installation, upstream research, build, installation, privilege,
`sudo`, `systemctl`, `systemd-run`, Polkit, `pkcheck`, service or database
action, H-0, H-1, H-2, `ACT`, `DEACT`, CP, RB-1, attestation, drill, evidence
pass, cleanup, commit or push occurred. No retained R4/R5 path was inspected.
No test suite was run. Nothing here is an accepted design, an executable
assignment, or authority for any step. OH-D-10 is put to Peter, not decided.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18, PO-19,
PO-20, PO-21 and H-1 remain open. RP-11 remains unwired and unmet. Package
RAID item `P5.0-R5` remains Blocking. `plan.is_executable=False`. Package 5.0
remains not ready.

Claude stops here, pending Codex's independent re-review and Peter Duscha's
decision on OH-D-10.

---

## 15. D3-R4 remediation and handback *(D3-R4, 2026-10-04)*

Work ID `C-P5.0-R5-RP11-H1-D3-R4`. Author: Claude. Independent reviewer:
Codex. Decision owner: Peter Duscha.

### 15.1 Outcome and recommendation

**DESIGN REMEDIATION READY FOR RE-REVIEW** (§0-R4).

* **OH-D-10 (A, iii-a) is adopted** by §4.2.5-R4. The rule grants `start`
  only. The capture unit's one added, fixed root step CP consumes the grant
  and obtains PK *not authorized* before PID 1 may execute `ExecStart=`. A CP
  failure is a failed start, not a pass. CP is one-shot and serialized with
  cleanup. Manual interruption is the executor's root literal under A-2.
* **`OH-H1-D3-R2-1` is addressed in design.** §4.2.5-R4 (i) proves that no
  grant exists at any instant of any pass or after it, for every terminal
  cause, with OH-D-7 read literally. HL and the backstop are lifetime and
  recovery machinery only.
* **Not declared closed:** `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2`.
  Only Codex may recommend closure, and Peter Duscha retains acceptance
  authority. `OH-H1-D3-R2-2` was closed by Peter in the R4 authority. D3-R4
  does not change GP-R3. The proposal stays **inactive and unaccepted**.

**Recommendation.** Codex re-reviews §4.2.5-R4 and the D3-R4 notes, using
§15.9. If Codex finds no Blocking defect, Codex recommends the disposition of
the three open findings, and Peter decides on the design, the §4.7.1 wordings
and the §4.7.2 D3-R4 dispositions. No host step, H-0 or implementation
precedes that.

### 15.2 Requirements and governing sections examined

| Source | SHA-256 (bytes) | Read |
|---|---|---|
| `.agents/AGENTS.md` | `ca907aa7…70c9f39e` (35,077) | completely |
| `docs/implementation-plan.md` | `a6a8c49c…11dcff8` (150,913) | reading map, §0 (to §0.3), §16 and §20 (the R4 current action) |
| `docs/review/Handover information` | `ebaf9d95…5c9427b0` (30,575) | the active R4 block completely; the superseded blocks by heading |
| R4 prompt | `3578da83…0f604b29` (1,870) | completely |
| R4 authority | `0be8f2df…c2e2fe1` (1,713) | completely |
| Codex's D3-R3 re-review | `4a0b20b3…7ebadf` (3,000) | completely |
| OH-D decision record | `8edb27db…b7afa15c` (4,637) | OH-D-6, OH-D-7 and OH-D-8 rows |
| this proposal at the start of D3-R4 | `efac90b6…6ca5a` (330,599) | completely by heading; header, §0, §4.1.3, §4.2.1 … §4.2.3, §4.2.5-R1 … R3, §4.3.3, §4.3.4, §4.4.1 … §4.4.3, §4.6, §4.7, §5 … §11 and §14 in full |
| C11 proposal | `f6405cd9…96312f70b` (209,120) | §4.4.3.4 (unit text, T-B1 absences, rule text and the reason for `stop`); the T-B1, T-B2 rows (§10.3), the PO-11 row (§14) and the §6.5 heading, by search |
| operational draft (`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`) | (174,711) | §9.5.3 and C-10, C-15, by search |
| `docs/operations/disposable-test-server.md` | `04cf010c…8da348` (7,739) | the active R4 restriction banner |

Every digest was taken by `sha256sum` and is abbreviated here only for width.
The plan's full SHA-256 is
`a6a8c49c6382e0078a39fbbf6f5b834ec055d5a4c0d200b38a0db711cc1dcff8`. The
prompt's and the authority's are in the header.

### 15.3 Disposition of the prompt's points

| Prompt point | Where answered |
|---|---|
| preserve D3-R3 as history; add a D3-R4 section and handback | the D3-R3 text is unchanged except one appended note (§15.7 check 8); labels in §0-R3, §4.2.5-R3 and §14.4; §4.2.5-R4 and this §15 |
| the Polkit rule grants `start` only | §4.2.5-R4 (b), T-B2; §4.7.2 D3-R4 table; §4.1.3 D3-R4 note |
| the capture unit has the fixed `ExecStartPre=+… rp11_h1.py consume` step, with no requester-controlled operand or environment | §4.2.5-R4 (b): the full unit text, T-B1, and "No requester-controlled input decides the grant boundary"; §4.3.3 note; PO-21 (n) |
| consume removes and PK-verifies the grant before `ExecStart=` can run | §4.2.5-R4 (c) CP-5, CP-6, CP-7; (i) items 1 and 2; PO-21 (o), (p) |
| a consume failure prevents `ExecStart=` and is not a pass | §4.2.5-R4 (c) (every non-CP-7 exit); (d) last row; (i) item 7; ST-2.f; HL's `start-failed-before-exec` (f) |
| the consume step is one-shot and serialized with cleanup | CP-3 (one-shot); CP-1 (one non-blocking lock attempt, AR-1); CP-2 (no `deact` evidence, AR-3); AM-0's lock released at `hold-start` (AR-2); (g) CL-1, CL-3 |
| manual interruption is the executor's A-2-authorized root `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service` | §4.2.5-R4 (e); A-2 pin (g); §4.7.1 D-1 amended; §4.6.2-R1 D3-R4 note |
| polling is lifetime and recovery machinery only and establishes no grant boundary | §4.2.5-R4 (f); notes in §4.2.5-R2 (g) and (n); (i) uses neither HL nor the backstop |
| GP-R3, ST-1.ur, `/run` boot clearing, automatic cleanup and separately authorized RB-1 remain intact | §4.2.5-R4 (a) "Unchanged"; §4.6.2-R1 D3-R4 note; §15.7 checks 8 and 9 |
| PO-21 (n) … (r), PO-11 (g), H-0 facts and fail-closed gates remain explicit proposed proof obligations, not assumed host facts | §4.2.5-R4 (j); §4.4.2b and §4.4.3 D3-R4 notes; §4.7.3 D3-R4 row; OH-S1 and OH-S2 D3-R4 rows |
| reconcile every affected table, proof obligation, traceability row and successor slice | §15.5 ledger |
| do not declare `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` or `OH-H1-D3-2` closed | §0-R4, §4.7.3 D3-R4 rows, §15.1 |

### 15.4 The adopted contract, in brief

* **Before a pass:** ST-2 holds a `start`-only grant for `ubuntu`. The
  operator's `start` is authorized once by Polkit. PID 1 then runs CP as root.
  CP takes the activation lock without waiting, checks that the activation is
  live and unconsumed, records its start, removes the rule by G-R1, and
  requires PK *not authorized*. Only then does it exit `0`.
* **During and after a pass:** no grant exists. Nothing re-links the rule. A
  hung pass is ended only by the executor's root `stop` under A-2.
* **On any CP failure:** `ExecStart=` never runs, and no pass happens. Any rule
  left is a pre-pass grant, which HL and CL remove when the activation ends.
  No later start of this activation can run the pass.
* **Cleanup** is CL as before, rule first, with GP-R3 when evidence fails. It
  now reads CP's journal. RB-1 stays separate.

### 15.5 Affected sections and change ledger

"Annotated" means that a *(D3-R4)* note was appended and the earlier text is
unchanged.

| Section | D3-R4 change |
|---|---|
| header | "Revision D3-R4" paragraph **added** |
| §0 | §0-R4 **added** before §0-R3; §0-R3 gains a D3-R4 note |
| §4.1.3 | **annotated** (TR-5 `start` only; TR-6a, CP) |
| §4.2.1 | **annotated** (H-1 unit and staged-rule bytes) |
| §4.2.2 | **annotated** (ST-2 and ST-3 grant cells; who issues `stop`) |
| §4.2.5-R2 | supersession label **extended**; (b), (c), (d), (g), (h), (j), (k), (m) and (n) **annotated** |
| §4.2.5-R3 | history label **added** at the head; (d) and (j) **annotated** |
| §4.2.5-R4 | **added** ((a) … (k)) |
| §4.3.3 | **annotated** (`ExecStartPre` compared; start timeout) |
| §4.3.4 | D3-R4 order bullet **added** |
| §4.4.2b, §4.4.3 | **annotated** (PO-21 (n) … (r), PO-11 (g) adopted as obligations) |
| §4.6.2-R1 | **annotated** (interruption route; CP not a rollback; RB-1 unchanged) |
| §4.6.4 | **annotated** (a PO-16 drill needs its own activation) |
| §4.7.1 | D-1 "Issue" amendment **added** |
| §4.7.2 | D3-R4 disposition table **added** |
| §4.7.3 | D3-R4 traceability table **added** |
| §4.7.4 | D3-R4 successor table **added** (OH-S0, OH-S0c, OH-S1, OH-S2, OH-S3, OH-S4, OH-S8b) |
| §5 | D3-R4 decision list **added** |
| §6, §9 | row and bullet **added** |
| §14.4 | one line **annotated** (the only changed D3-R3 line) |
| §15 | **added** (this section) |

### 15.6 Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | revised in place, as §15.5 lists |

No other repository file was created, changed or deleted. The pre-existing
uncommitted changes (40 status entries at start, 30 of them untracked, all
documentation) were preserved untouched. Current status, Handover, §20, the
decision register and the active restriction were **not** updated. A copy of
the D3-R3 bytes, the draft of §4.2.5-R4 and the scratch checks live outside
the repository, in the session scratchpad.

### 15.7 Commands and checks run, and checks not run

**Run** (repository-local and read-only, apart from editing this file and
writing scratch files outside the repository):

| # | Command or check | Exact result |
|---|---|---|
| 1 | `git status --short`; `git rev-parse HEAD` (start and end) | HEAD `236872647f3edd5fed5c7f14512518e13eeb8f07`; 40 entries, 30 untracked, at start and at end. This file was already untracked |
| 2 | `sha256sum`, `wc -c` of the §15.2 inputs and of this file before editing | as §15.2. The D3-R3 file is `efac90b6…6ca5a`, 330,599 bytes, equal to the scratch copy used for the diff checks |
| 3 | `cat`, `sed -n`, `grep -n` over the §15.2 inputs | read as §15.2 |
| 4 | identifier collision search: `grep -rlE` over `docs/` for `AR-n`, `CX-n`, `ST-2.c`, `ST-2.f`, `TR-6a`, `CP-7`, `consume-busy`, `consume-repeated`, `start-failed-before-exec`, `consume-failed` | none used elsewhere. A first draft used `RF-n` and `RC-n`, which other review documents use, and the HL reason `start-failed`, which an RP-11 I-1 handback uses. They were renamed `AR-n`, `CX-n` and `start-failed-before-exec` before writing |
| 5 | **the rule grants `start` only:** `grep` of added lines for `lookup("verb")` | 2 lines: the rule text (`== "start"`) and the §4.7.2 disposition quoting it. No added text grants `stop`. The earlier `start`/`stop` cells (§4.1.3 TR-5, §4.2.2 ST-2) carry D3-R4 notes |
| 6 | **one `consume` literal:** every `ExecStartPre=+` string in the whole file, extracted by `grep -o` up to the closing code-span mark and counted | 5 full occurrences, byte-identical. All other occurrences are elided references (`ExecStartPre=+`, `ExecStartPre=+…`, `…consume` or `…rp11_h1.py consume`), including §15's own |
| 7 | **one interruption literal:** `grep -o 'sudo -n /usr/bin/systemctl stop…'`, counted | before §15, 4 occurrences; in the whole file, 6. All are byte-identical: `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service`. The only other match is this row's elided search pattern |
| 8 | **D3-R3 preserved:** `diff` of the D3-R3 copy against this file | **1** removed line, `**Pass-terminal coupling (not adopted; OH-D-10).**` (§14.4), re-added with an appended history note. 682 lines added before §15. No GP-R3, ST-1.ur, M-B, M-S, CL, BS, attestation, PF, PT, journal, RS-1, G-R1, P-1, P-2 or RB-1 line changed |
| 9 | **RB-1 not made automatic:** added lines naming RB-1 | 3 lines. Each states that RB-1 is unchanged, separately authorized and never automatic |
| 10 | **polling establishes no boundary:** added lines matching "within Δ", "latency", "grant boundary", "no live grant" or "grant after the pass" | 8 lines. Two state that HL and the backstop establish no grant boundary. Two use "within Δ" for HL's lifetime role: the route (iii-a) bullet, which ends "No grant is involved at any point", and the (k) ST-3 cell, which says "No grant at any instant". The others are the (b) heading on requester inputs, the (i) heading, the traceability row and the §0-R3 note. None uses polling for the grant boundary |
| 11 | **obligations, not facts:** added lines matching "obligation" or "host fact" | each PO-21 (n) … (r) and PO-11 (g) statement is framed as a proposed, fail-closed obligation. None states an observed host value |
| 12 | **closure claims:** added lines matching "closed" | 1 line: `OH-H1-D3-R2-2` closed by Peter in the R4 authority. No added line declares the other three findings closed |
| 13 | **no host command, assignment or implementation added:** added lines filtered for `/goal`, `ssh `, `rsync `, `git fetch\|clone`, code fences and `sudo -n` | two fenced blocks, the unit (`ini`) and the rule (`js`), as design text, and three quotations of the route (iii-a) literal, which A-2 would pin. No `/goal`, no `ssh`, `rsync` or `git` retrieval, and no source, test, unit, rule or manifest file change. `infra/systemd/` holds no RP-11 unit, and `infra/polkit/` does not exist |
| 14 | Markdown structure (scratch Python: fences, table pipe counts outside fences, unescaped pipes inside code spans in tables, trailing whitespace) | 18 fence lines (14 before), balanced; 92 tables before §15 and 97 with it, 0 inconsistent rows; 0 unescaped pipes in code spans; trailing whitespace only on the 6 deliberate header line breaks (lines 3 … 14), as before |
| 15 | `git diff --no-index --check ⟨D3-R3 copy⟩ ⟨this file⟩` | no whitespace error reported. Exit 1 only because the files differ |
| 16 | `git diff --check` (tracked files) | exit 0 |

Checks 4 to 16 were first run before this §15 was written. Checks 5 to 16
were re-run on the final file, and the table gives those figures. For checks
5 and 8 … 13, "added lines" means lines added before §15. §15's own lines add
only quotations of the searched phrases.

**Not run, and why:**

* **No host check** of any kind on any host. PO-21 (n) … (r), PO-11 (g) and
  every earlier obligation remain uncited and unobserved. The authority
  excludes host access and upstream research.
* **No test suite, formatter, linter or type checker.** No code changed, and
  the prompt prohibits suite runs. No suite figure is claimed.
* **No Markdown linter.** None is configured in the repository. Check 14 is
  the substitute.

### 15.8 Security, production-isolation, operational and rollback implications

* **This return** changes one documentation file and affects no host. It is
  reverted by restoring the D3-R3 bytes, whose SHA-256 is in the header.
* **Security.**
  * **No grant exists during or after any pass** (§4.2.5-R4 (i)). The
    operator loses the Polkit `stop` route.
  * **CP is root code at every start of the capture unit**, including a start
    by `ubuntu` under the grant. It is the installed tool's fixed bytes, bound
    by the H-1 record and compared by H-2. It takes no operand, and it receives
    PID 1's environment and nothing from the requester. Requester-writable
    inputs can only make it refuse (§4.2.5-R4 (b)). It is a separate process,
    not an ancestor of the entry, so LB-2S's two prevention claims and PO-14
    are unaffected.
  * **Route (iii-a)** adds no privilege under OH-D-6. It moves interruption
    from a grant to an act under A-2.
* **Production isolation.** Unchanged. CP, CL and route (iii-a) run on
  `oracle-test` only. E-1 to E-3 apply. The production workspace host is never
  a source, controller, relay, destination, fallback or rollback target
  (OH-D-1).
* **Operational.**
  * Each activation permits exactly one start attempt that reaches CP-4.
    A failed start ends the activation, and another pass needs a new A-2
    (CX-2).
  * A hung pass needs the executor (CX-3). The operator cannot stop it.
  * The unit and rule bytes change before any installation. No installation
    exists, so no H-1R or RB-1 follows from this.
* **Rollback.** RB-1 is still separately authorized and never automatic
  (OH-D-8). CP is part of the start, not a rollback. Activation cleanup (CL
  with GP-R3, the backstop and the kernel boot) is automatic under A-2. Records
  and journals, including the consume journal, are never deleted.

### 15.9 Proposed independent-review focus

1. **The proof** (§4.2.5-R4 (i)). Does it cover every instant from the
   `execve` of `ExecStart=` onward, for every cause in (d)? Is "the pass"
   defined correctly for OH-D-7?
2. **CP's order and lock** ((c), AR-1 … AR-3). Is one non-blocking attempt,
   taken before any check, correct, given that no step holds the lock in ST-2?
   Is the `hold-start` release safe for the holder's later unlocked `ACT`
   journal appends?
3. **Requester-writable inputs** ((b)). The `ACT` journal sits in an
   `ubuntu`-owned directory, and `/var/tmp` is shared. Is "can only make CP
   refuse, or remove the real rule" right?
4. **CX-1** ((k)). Is a pass that runs after the holder has ended, without a
   grant and ending in `unit-still-active`, acceptable? Or should CP also
   check the holder's `ActiveState`, which adds a `systemctl show` call from
   inside a start job and a further PO-21 item?
5. **The start timeout** (AR-4, PO-21 (r)). Is a manager-default timeout,
   checked at AP-0, enough without a unit `TimeoutStartSec=` line, which the
   decision does not admit?
6. **PO-21 (n) … (r) and PO-11 (g)** ((j)). Are they complete, including
   AR-5's execution-setting statement and AR-6's `INVOCATION_ID` statement?
7. **Route (iii-a)** ((e)). Is the precondition (`activating` or `active`) and
   the §9.5.3 classification right, including a `stop` during `start-pre`?
8. **AR-1 … AR-8 as design refinements.** Is any of them a maintainer choice
   rather than a refinement within OH-D-10 (A)?
9. §14.9 items 4 … 6, §13.9's items 1, 2, 4, 5, 7 and 8, §12.9's open items
   and §10's D3 items remain as stated there.

### 15.10 Statement of authority used

I used only the repository-documentation and read-only repository-inspection
authority of `C-P5.0-R5-RP11-H1-D3-R4`. **No host, network, credential,
implementation or execution authority was used.** No SSH, `rsync`, Git or
network retrieval, `oracle-test` or production-host access, credential
creation or installation, upstream research, build, installation, privilege,
`sudo`, `systemctl`, `systemd-run`, Polkit, `pkcheck`, service or database
action, H-0, H-1, H-2, `ACT`, `DEACT`, CP, RB-1, attestation, drill, evidence
pass, cleanup, commit or push occurred. No retained R4/R5 path was inspected.
No test suite was run. Nothing here is an accepted design, an executable
assignment, or authority for any step.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18, PO-19,
PO-20, PO-21 and H-1 remain open. RP-11 remains unwired and unmet. Package
RAID item `P5.0-R5` remains Blocking. `plan.is_executable=False`. Package 5.0
remains not ready.

Claude stops here, pending Codex's independent re-review.

## 16. D3-R5 remediation and handback *(D3-R5, 2026-10-04)*

Work ID `C-P5.0-R5-RP11-H1-D3-R5`. Author: Claude. Independent reviewer:
Codex. Decision owner: Peter Duscha.

### 16.1 Outcome and recommendation

**DESIGN REMEDIATION READY FOR RE-REVIEW** (§0-R5).

* **`OH-H1-D3-R4-1` is addressed in design** by §4.2.5-R5. The defect is
  confirmed as Codex stated it. D3-R4's CP created its one-shot name at CP-4,
  so CP-0, CP-1 and CP-2 failures, and any death before CP-4, left no barrier.
* **The one-start-attempt property is now proved for every path**, as contract
  OSA (§4.2.5-R5 (b), (f)). SB-1, the claim, is CP's first act under the
  activation lock. SB-2, PID 1's start history, covers every attempt that ends
  before the claim, including attempts in which no CP instruction ran. SB-3,
  the rule token, limits success to one CP per activation. One narrow
  exception is stated as CX-4. It needs a root `stop` issued against A-2's
  terms, and it never leaves a grant during or after a pass.
* **No maintainer decision is required.** OH-D-10 (A) is refined, not changed:
  the unit and rule bytes, the consume line, route (iii-a)'s literal and its
  executor are unchanged. OS-6 narrows when route (iii-a) is used, and §16.9
  item 6 asks Codex whether that is a choice for Peter.
* **Not declared closed:** `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1`
  and `OH-H1-D3-2`. Only Codex may recommend closure, and Peter Duscha retains
  acceptance authority. The proposal stays **inactive and unaccepted**.

**Recommendation.** Codex re-reviews §4.2.5-R5 and the D3-R5 notes, using
§16.9. No host step, H-0 or implementation precedes the review and Peter's
decision.

### 16.2 Requirements and governing sections examined

| Source | SHA-256 (bytes) | Read |
|---|---|---|
| `.agents/AGENTS.md` | `ca907aa7…70c9f39e` (35,077) | completely |
| `docs/implementation-plan.md` | `34e3ca47…bed2acc9` (152,552) | reading map, §0 (to §0.5), §16 and §20 (the R5 current action and the superseded R4 blocks) |
| `docs/review/Handover information` | `66cf097d…d00b8b11` (32,440) | completely |
| R5 prompt | `2a01b748…1aa476b0` (3,483) | completely |
| R5 authority | `68d73926…3b66c5dc` (1,633) | completely |
| Codex's D3-R4 re-review | `cfe599da…56f56b50` (4,072) | completely |
| this proposal at the start of D3-R5 | `019d5c3b…17c1fffe` (398,749) | completely by heading. In full: the header, §0-R4, §4.2.4-R1 (b), §4.2.5-R1 … R4, §4.4.2a, §4.4.2b, the §4.7.4 tables and §15. In part: §4.4.3's revision notes, §4.7.3's D3-R2 … D3-R4 tables, §5's D3-R4 list, and the D3-R4 notes in §4.1.3, §4.2.2, §4.3.4, §4.6.2-R1, §4.6.4, §4.7.1, §6 and §9 |
| `docs/operations/disposable-test-server.md` | `3dc338a4…699e1673` (7,713) | the active R5 restriction banner |

Every digest was taken by `sha256sum`, and is abbreviated here only for width.
The prompt's, the authority's and the D3-R4 file's full digests are in the
header. The plan's full SHA-256 is
`34e3ca476e0fa6607dfe099af183879e320cbbe4bcf851d35469a6a0bed2acc9`.

### 16.3 Disposition of the prompt's points

| Prompt point | Where answered |
|---|---|
| preserve D3-R4 as history; add a D3-R5 section and handback | D3-R4 text is unchanged (§16.7 check 6); labels at the head of §4.2.5-R4 and in §0-R4, with notes at R4 (c), (d), (i) and (k); §4.2.5-R5 and this §16 |
| distinguish a start with no valid active activation from an identified consume attempt, without making an ST-1 root probe an activation marker | §4.2.5-R5 (b) definitions; (e) CQ-0 and CQ-1 create nothing; (c) "Not an activation marker" |
| once CP has identified the activation, durably and atomically consume its single attempt before any remaining fallible precondition, holding the cleanup lock | (e) CQ-1 (the lock), CQ-2 (the claim, first act under the lock), then CQ-3 and CQ-4; (d) |
| the publication protocol, ownership, mode, identity, durability point and closed journal operations of the barrier | (d), including the separate **blocking point** (`mkdirat`) and **durability point** (`fsync` of `/var/tmp`) |
| every crash, kill, timeout, contention, malformed or missing input and cleanup race, before, during and after that point | (i), the boundary table, with every row ending without `ExecStart=` |
| prove that a pre-barrier failure cannot later become a valid start in the same activation | (f): SB-2, PID 1's start history, refuses every later attempt after any ended attempt, with CX-4 as the only exception. The pre-barrier class is defined in (b) and is not narrowed by assumption |
| CP, CL, HL and the backstop agree; no interval in which a repeated start can race cleanup into `ExecStart=` | (g): one lock and its four holders; OS-5 (HL ends under the lock); HL's reasons; CL's `consume.attempt` classes; the four race cases |
| consume failure is fail-closed: no `ExecStart=`, no pass claimed, no later start of the activation runs the pass | (e) "every exit other than CQ-7's"; (f) proofs of 1 … 4; (i) |
| reconcile CP-0 … CP-7, the terminal-cause table, ST-2.c and ST-2.f, the boundary table, proof item 7, CX-2, records and journals, traceability, implementation tests and OH-S8b drills | (e) map from CP-n to CQ-n; (j) for the R4 (d) row, ST-2.c, ST-2.f, the (k) rows, item 7, CX-2, records and journals; §4.7.3 and §4.7.4 D3-R5 tables (OH-S4 tests (12) and (20) … (27); OH-S8b) |
| state any new residual honestly; BLOCKED REMEDIATION if a maintainer choice or a change to OH-D-10 is needed | (k) CX-4, narrowed CX-1 and CX-2, and the liveness note; §5 D3-R5: no choice is needed, and closing CX-4 in every case would change OH-D-10 (A), which is not proposed |
| preserve the unaffected D3-R4 properties | (a) "Unchanged"; §16.7 checks 7 … 12 |
| do not declare `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` or `OH-H1-D3-2` closed | §0-R5, §4.2.5-R5 (k), §4.7.3 D3-R5 rows, §16.1 |

### 16.4 The contract, in brief

* **Before an attempt:** at AM-0, before any activation file exists, the
  holder records the capture unit's τ₀. At `hold-start` it requires that no
  attempt has begun or ended since. Otherwise the activation ends
  (`start-before-hold`).
* **CP:** it identifies the activation without the lock and creates nothing
  if it cannot. It then takes the lock once, without waiting. Its first act
  under the lock is the exclusive `mkdirat` of the claim. It then removes the
  rule, checks that the activation is live and that this is its first attempt
  (τ = τ₀, holder `active`), and requires PK *not authorized*. Only then does
  it write `consumed` and exit `0`.
* **After any failed attempt:** the claim (SB-1) or PID 1's start history
  (SB-2) refuses every later attempt, by `ubuntu` or by root. At most one CP can
  ever succeed (SB-3). HL ends the activation under the lock, and CL removes
  anything left, rule first.
* **Unchanged:** no grant exists during or after any pass (§4.2.5-R4 (i) items
  1 … 6). Interruption is route (iii-a), now only while the pass is `active`.

### 16.5 Affected sections and change ledger

"Annotated" means that a *(D3-R5)* note was appended and the earlier text is
unchanged.

| Section | D3-R5 change |
|---|---|
| header | "Revision D3-R5" paragraph **added** |
| §0 | §0-R5 **added** before §0-R4; §0-R4 gains a D3-R5 note |
| §4.1.3 | **annotated** (TR-6a order) |
| §4.2.5-R2 | supersession label **extended** |
| §4.2.5-R4 | history label **added** at the head; (c), (d), (i) and (k) **annotated** |
| §4.2.5-R5 | **added** ((a) … (k)) |
| §4.3.4 | D3-R5 order bullet **added** |
| §4.4.2b, §4.4.3 | **annotated** (PO-21 (s) … (v), PO-20 (h), HF-11) |
| §4.6.2-R1 | **annotated** (route (iii-a) only while `active`; the claim is never removed) |
| §4.6.4 | **annotated** |
| §4.7.1 | D3-R5 sentence for D-1 **added** |
| §4.7.3 | D3-R5 traceability table **added** |
| §4.7.4 | D3-R5 successor table **added** (OH-S0, OH-S0c, OH-S1, OH-S2, OH-S3, OH-S4, OH-S8b) |
| §5 | D3-R5 decision list **added** |
| §6, §9 | row and bullet **added** |
| §16 | **added** (this section) |

### 16.6 Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | revised in place, as §16.5 lists |

No other repository file was created, changed or deleted. The pre-existing
uncommitted changes (43 status entries at start, 33 of them untracked, all
documentation) were preserved untouched. Current status, Handover, §20, the
decision register and the active restriction were **not** updated. A copy of
the D3-R4 bytes, the draft of §4.2.5-R5 and the scratch checks live outside the
repository, in the session scratchpad.

### 16.7 Commands and checks run, and checks not run

**Run** (repository-local and read-only, apart from editing this file and
writing scratch files outside the repository):

| # | Command or check | Exact result |
|---|---|---|
| 1 | `git status --short`; `git rev-parse HEAD` (start and end) | HEAD `236872647f3edd5fed5c7f14512518e13eeb8f07`; 43 entries, 33 untracked, at start and at end. This file was already untracked |
| 2 | `sha256sum`, `wc -c` of the §16.2 inputs and of this file before editing | as §16.2. The D3-R4 file is `019d5c3b…17c1fffe`, 398,749 bytes, equal to the scratch copy used for the diff checks |
| 3 | `cat`, `sed -n`, `grep -n` over the §16.2 inputs | read as §16.2 |
| 4 | identifier collision search: `grep -rlE` over `docs/` outside this file for `CQ-n`, `OS-n`, `SB-n`, `CX-4`, `OSA`, `consume-unidentified`, `consume-claim-failed`, `start-before-hold`, `capture-busy-at-act`, `capture-unloaded`, `PO-21 (s)` … `(v)` and `PO-20 (h)` | none used elsewhere. A first draft named the barriers `B-1` … `B-3`, which other review documents use. They were renamed `SB-1` … `SB-3` before this handback |
| 5 | the barrier precedes every validation: CQ-2 is the first step after CQ-1 that touches anything, and no CQ step before CQ-2 creates or removes an object | holds by the (e) table; restated in (e) "What each step can and cannot leave" |
| 6 | **D3-R4 preserved:** `diff` of the D3-R4 copy against this file | **0** removed lines. 671 lines added before §16, in 22 hunks, plus the blank line that precedes §16 |
| 7 | **the rule still grants `start` only:** added lines containing `lookup("verb")` | 0. The rule text is unchanged |
| 8 | **one `consume` literal:** full occurrences of `ExecStartPre=+/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume` | 5 in the D3-R4 copy and 5 before §16, byte-identical; none added. The whole file has 6, the sixth being this row's own quotation |
| 9 | **one interruption literal:** full occurrences of `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service` | 6 in the D3-R4 copy and 6 before §16; none added. The whole file has 7, the seventh being this row's own quotation. OS-6 changes only when the literal is issued |
| 10 | **RB-1 not made automatic:** added lines naming RB-1 | 4 lines. Each states that RB-1 is unchanged and separately authorized, or that it never removes the claim |
| 11 | **closure claims:** added lines matching "closed" | none declares a finding closed. The matches are "not declared closed", "remain open", "closed `op` set" and "fail-closed" |
| 12 | **no host command, assignment or implementation added:** added lines filtered for `/goal`, `ssh `, `rsync `, `git fetch\|clone`, code fences and `sudo -n` | none. No source, test, unit, rule or manifest file changed |
| 13 | Markdown structure (scratch Python: fences, table cell counts outside fences, unescaped pipes inside code spans in tables, trailing whitespace), run on the D3-R4 copy and on this file | 14 column-0 fence lines in both, balanced; 92 tables before, 103 before §16 and 108 with it. One row is flagged in both files: the pre-existing D3-R2 OH-S4 row, unchanged, whose backslash code span this checker miscounts. 0 unescaped pipes in code spans; trailing whitespace only on the 6 deliberate header line breaks (lines 3 … 14), as before |
| 14 | `git diff --no-index --check ⟨D3-R4 copy⟩ ⟨this file⟩` | no whitespace error reported. Exit 1 only because the files differ |
| 15 | `git diff --check` (tracked files) | exit 0 |

Checks 4 … 15 were first run before this §16 was written, and checks 6 … 15
were re-run on the final file. For checks 7 and 10 … 12, "added lines" means
lines added before §16. §16's own lines add only quotations of the searched
phrases.

**Not run, and why:**

* **No host check** of any kind on any host. PO-21 (s) … (v), PO-20 (h) and
  every earlier obligation remain uncited and unobserved. The authority
  excludes host access and upstream research. The systemd behaviour that
  §4.2.5-R5 relies on (attempt serialization, `InactiveEnterTimestampMonotonic`,
  end states, queries from `ExecStartPre=`) is stated only as proposed
  obligations, from the design author's understanding, not from a citation.
* **No test suite, formatter, linter or type checker.** No code changed, and
  the prompt prohibits suite runs. No suite figure is claimed.
* **No Markdown linter.** None is configured in the repository. Check 13 is the
  substitute.

### 16.8 Security, production-isolation, operational and rollback implications

* **This return** changes one documentation file and affects no host. It is
  reverted by restoring the D3-R4 bytes, whose SHA-256 is in the header.
* **Security.**
  * The grant boundary of §4.2.5-R4 (i) is unchanged: no grant exists during or
    after any pass.
  * **CP now removes the rule earlier**, before its precondition checks. A
    failed identified attempt therefore usually leaves no pre-pass grant
    (CX-2 narrowed).
  * **CP now calls `systemctl show`** twice, read-only, as root (OS-1, OS-4).
    It issues no other `systemctl` verb. PO-21 (v) must show that the call
    cannot wait on CP's own start job.
  * **The claim sits in `/var/tmp`.** `ubuntu` can pre-create its name, which
    only refuses the start. It cannot remove or rename root's claim
    (PO-20 (h)).
  * **CX-4** needs a root act against A-2's terms. It cannot leave a grant
    during or after a pass.
* **Production isolation.** Unchanged. Everything runs on `oracle-test` only,
  E-1 to E-3 apply, and the production workspace host is never a source,
  controller, relay, destination, fallback or rollback target (OH-D-1).
* **Operational.**
  * An activation admits **one** start attempt. Any failed attempt, an early
    start before `hold-start`, or a start that meets HL's end ends the
    activation without a pass. Another pass needs a new A-2.
  * The executor's route (iii-a) is used only on a running pass (OS-6). A hung
    CP ends at the unit's start timeout.
  * One more `/var/tmp` evidence directory per activation is retained, and
    AP-0 checks that ageing cannot remove it within the lease (OS-8).
* **Rollback.** RB-1 is still separately authorized and never automatic
  (OH-D-8). CP is part of the start, not a rollback. Records, journals and the
  claim are never deleted.

### 16.9 Proposed independent-review focus

1. **Contract OSA and its proof** (§4.2.5-R5 (b), (f)). Is "the first attempt
   after AM-0" the right unit? Do Lemmas 1 … 3 cover every way an attempt can
   end, including a CP that never ran?
2. **SB-2 rests on systemd behaviour** (PO-21 (s) … (v)). Is
   `InactiveEnterTimestampMonotonic` the right fact? Are the obligations
   complete, including unloading of `inactive` units and `daemon-reexec`? Would
   a refuted item leave any path that is not fail-closed at AP-0?
3. **The claim** ((d)). Are the separate blocking and durability points right,
   given that the activation cannot outlive the boot? Is OS-8's ageing
   condition needed and sufficient?
4. **CQ order** ((e)). Is removing the rule before the precondition checks
   (OS-3) safe in every state in which CP can hold the lock, including a dead
   holder before `hold-start`?
5. **OS-5 and the races** ((g)). Is HL's decision under the lock free of
   deadlock and starvation, given CP's single non-blocking attempt? Is CX-1,
   narrowed to the holder's death or lease expiry, acceptable?
6. **OS-6** ((h)). Is limiting route (iii-a) to an `active` unit a refinement,
   or a maintainer choice about the decided route? If it is a choice, Peter
   decides it, and without it CX-4 also covers a route (iii-a) `stop` during
   `start-pre`.
7. **CX-4** ((k)). Is the residual stated exactly? Is classing it as a root
   act outside A-2 (SL-1 kind) acceptable, or should Peter be asked to close
   it through a change to OH-D-10 (A)?
8. **HL labels** ((g), (i)). Is it acceptable that `start-failed-before-exec`
   and `indeterminate` can understate a pass, but never overstate one?
9. §15.9 items 1, 3, 5, 6 and 8 remain as stated there. Item 4 is answered by
   OS-4, and item 2's lock is re-examined by item 5 above.

### 16.10 Statement of authority used

I used only the repository-documentation and read-only repository-inspection
authority of `C-P5.0-R5-RP11-H1-D3-R5`. **No host, network, credential,
implementation or execution authority was used.** No SSH, `rsync`, Git or
network retrieval, `oracle-test` or production-host access, credential
creation or installation, upstream research, build, installation, privilege,
`sudo`, `systemctl`, `systemd-run`, Polkit, `pkcheck`, service or database
action, H-0, H-1, H-2, `ACT`, `DEACT`, CP, RB-1, attestation, drill, evidence
pass, cleanup, commit or push occurred. No retained R4/R5 path was inspected.
No test suite was run. Nothing here is an accepted design, an executable
assignment, or authority for any step.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18, PO-19,
PO-20, PO-21 and H-1 remain open. RP-11 remains unwired and unmet. Package
RAID item `P5.0-R5` remains Blocking. `plan.is_executable=False`. Package 5.0
remains not ready.

Claude stops here, pending Codex's independent re-review.

## 17. D3-R6 remediation and handback *(D3-R6, 2026-10-04)*

Work ID `C-P5.0-R5-RP11-H1-D3-R6`. Author: Claude. Independent reviewer:
Codex. Decision owner: Peter Duscha.

### 17.1 Outcome and recommendation

**DESIGN REMEDIATION READY FOR RE-REVIEW** (§0-R6).

* **`OH-H1-D3-R5-1` is addressed in design** by §4.2.5-R6. The finding is
  accepted as Codex stated it. D3-R5 narrowed the decided route (iii-a),
  called that a refinement, and so should have returned BLOCKED REMEDIATION.
* **OS-6 is incorporated as Peter Duscha's decided amendment** to route
  (iii-a), with its three conditions OC-1 … OC-3 and its exclusions
  (§4.2.5-R6 (b)). The fixed literal, its executor, its A-2 authority and its
  §9.5.3 classification are unchanged.
* **Contract OSA's authority boundary follows from the decision.** OSA is
  stated over the authorized path set 𝒜 (§4.2.5-R6 (d), (e)) and holds there
  without exception. Lemma R6 shows that every route (iii-a) `stop` lands
  after the claim, so the decided route cannot produce the pre-barrier
  `inactive` case.
* **CX-4 stays, honestly, outside 𝒜** (§4.2.5-R6 (f)). It is an SL-1 kind
  residual, not an authorized-path exception. It is stated so that Peter's
  eventual acceptance covers it knowingly. It is not closed in every case, and
  closing it would change OH-D-10 (A), which is not proposed.
* **One narrowly explained correction.** D3-R5 claimed OS-4 covers an orderly
  transition during `start-pre`. The design fixes no order between the
  holder's and the capture unit's stop, so the claim is withdrawn and EO is
  named as CX-4's second source, outside 𝒜 as A-2's pinned sentence already
  places it.
* **Preserved:** the D3-R5 SB-1, SB-2 and SB-3 mechanism, the CQ-0 … CQ-7
  order, the shared lock and OS-5, the finite, fail-closed start timeout, and
  every proposed proof obligation, none added, removed or re-worded.
* **Not declared closed:** `OH-H1-D3-R5-1`, `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`,
  `OH-H1-D3-R1-1` and `OH-H1-D3-2`. Only Codex may recommend closure, and
  Peter Duscha retains acceptance authority. The proposal stays **inactive and
  unaccepted**.

**Recommendation.** Codex re-reviews §4.2.5-R6 and the D3-R6 notes, using
§17.9. No host step, H-0 or implementation precedes the review and Peter's
decision.

### 17.2 Requirements and governing sections examined

| Source | SHA-256 (bytes) | Read |
|---|---|---|
| `.agents/AGENTS.md` | `ca907aa7…70c9f39e` (35,077) | completely |
| `docs/implementation-plan.md` | `83a02bd6…88e0e4e8` (154,444) | reading map, §0 (to §0.5), §16 and §20 (the R6 current action and the superseded R5 and R4 blocks) |
| `docs/review/Handover information` | `fcedfcce…0d14bb5` (34,587) | the active R6 block and the superseded D3-R5, R5 and D3-R4 blocks |
| R6 prompt | `48345a17…0d0d14f` (2,330) | completely |
| R6 authority | `c320ab3e…62e1a5` (2,211) | completely |
| Codex's D3-R5 re-review | `b01b5a0d…894cb19` (4,074) | completely |
| this proposal at the start of D3-R6 | `0c2bacfc…3255743` (470,827) | completely by heading. In full: the header, §0-R5, §4.2.5-R4, §4.2.5-R5 and §16. In part: §4.2.5-R2 (c), (k) and (l), §4.2.5-R3 (d)'s unit relationship, §4.3.3 (a), §4.3.4, §4.6.2-R1, §4.6.4, §4.7.1 D-1, §4.7.3 and §4.7.4 D3-R4 and D3-R5 tables, §5, §6 and §9 |
| `docs/operations/disposable-test-server.md` | `dd3678c5…5c947` (7,742) | the active R6 restriction banner |

Every digest was taken by `sha256sum` and is abbreviated here only for width.
The prompt's, the authority's and the starting file's full digests are in the
header.

### 17.3 Disposition of the prompt's points

| Prompt point | Where answered |
|---|---|
| preserve D3-R5 as history; add a D3-R6 section and handback | D3-R5 text is unchanged (§17.7 check 5); labels at the heads of §4.2.5-R4 and §4.2.5-R5 and in §0-R5; §4.2.5-R6 and this §17 |
| incorporate the exact decided condition | §4.2.5-R6 (a) quotes it; (b) states OC-1 … OC-3, the exclusions (`activating`, every sub-state, `start-pre`) and the start timeout for a hung consume step |
| literal, executor, A-2 authority and §9.5.3 classification unchanged | §4.2.5-R6 (b) "Literal", "Who", "What it is"; §17.7 checks 6 and 7 |
| record OS-6 as a decided amendment, not merely a refinement | §4.2.5-R6 (a); §0-R6; §5 D3-R6 list; §4.7.3 D3-R6 row |
| make contract OSA's authority boundary and CX-4 classification follow explicitly | §4.2.5-R6 (c) Lemma R6, (d) the set 𝒜 and the sources of a stop job, (e) OSA over 𝒜 and why it follows from the decision, (f) CX-4 outside 𝒜 |
| reconcile D-1, A-2, terminal-cause and boundary tables, traceability, successors, tests and OH-S8b drills | §4.2.5-R6 (g); §4.7.1 D3-R6 note (D-1); §4.2.5-R2 (c) and §4.2.5-R4 (g) notes (A-2); §4.7.3 and §4.7.4 D3-R6 tables (OH-S0, OH-S0c, OH-S3, OH-S4 tests (21a), (21b), (28), (29), OH-S8b) |
| preserve the root-outside-A-2 residual honestly | §4.2.5-R6 (f): sources, conditions, consequence, voidable but not voided, not closed in every case |
| preserve the SB-1/SB-2/SB-3 mechanism, CQ order, lock protocol, start timeout and proof obligations unless a concrete inconsistency requires a narrow correction | §4.2.5-R6 (a) "Unchanged"; the only correction is the EO sentence, (f) |
| state whether `OH-H1-D3-R5-1` is addressed, declaring nothing closed | §0-R6, §4.2.5-R6 (g), §4.7.3 D3-R6 rows, §17.1 |

### 17.4 The contract, in brief

* **Route (iii-a):** only while the unit is `active`, its `InvocationID`
  equals the consume journal's `run-start.invocation_id`, and the journal has
  `consumed`. Never while `activating`. A hung CP ends at the start timeout,
  `failed`, which engages SB-2.
* **Lemma R6:** the condition implies the claim exists, and the claim is never
  removed, so every route (iii-a) `stop`, even after a stale read, lands after
  SB-1's blocking point.
* **OSA within 𝒜:** no stop job reaches the capture unit during `start-pre`
  before the claim, so only the SB-1 and `failed`/SB-2 cases occur, and OSA
  holds without exception.
* **Outside 𝒜:** CX-4 (a non-route root `stop` or a forbidden orderly
  transition, with PO-21 (u), τ₀ = `0` and an unload) can defeat SB-1 and
  SB-2. No grant exists during or after any pass even then.

### 17.5 Affected sections and change ledger

"Annotated" means that a *(D3-R6)* note was appended and the earlier text is
unchanged.

| Section | D3-R6 change |
|---|---|
| header | "Revision D3-R6" paragraph **added** |
| §0 | §0-R6 **added** before §0-R5; §0-R5 gains a D3-R6 note |
| §4.2.5-R2 | supersession label **extended**; (c) **annotated** (A-2 pin) |
| §4.2.5-R4 | history label **extended**; (d), (e) and (g) **annotated** |
| §4.2.5-R5 | history label **added**; (b), (f), (h), (i), (j) and (k) **annotated**; closing pointer to §4.2.5-R6 |
| §4.2.5-R6 | **added** ((a) … (g)) |
| §4.3.4 | **annotated** (a hung pass, a hung CP) |
| §4.6.2-R1 | **annotated** |
| §4.7.1 | D3-R6 D-1 wording **added** |
| §4.7.3 | D3-R6 traceability table **added** |
| §4.7.4 | D3-R6 successor table **added** (OH-S0, OH-S0c, OH-S3, OH-S4, OH-S8b) |
| §5 | D3-R6 decision list **added** |
| §6, §9 | row and bullet **added** |
| §17 | **added** (this section) |

### 17.6 Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | revised in place, as §17.5 lists |

No other repository file was created, changed or deleted. The pre-existing
uncommitted changes (46 status entries at start, 36 of them untracked, all
documentation) were preserved untouched. Current status, Handover, §20, the
decision register and the active restriction were **not** updated. A copy of
the D3-R5 bytes and the scratch checks live outside the repository, in the
session scratchpad.

### 17.7 Commands and checks run, and checks not run

**Run** (repository-local and read-only, apart from editing this file and
writing scratch files outside the repository):

| # | Command or check | Exact result |
|---|---|---|
| 1 | `git status --short`; `git rev-parse HEAD` | HEAD `236872647f3edd5fed5c7f14512518e13eeb8f07`; 46 entries, 36 untracked, at start. This file was already untracked |
| 2 | `sha256sum`, `wc -c` of the §17.2 inputs and of this file before editing | as §17.2. The scratch copy equals the starting file, `0c2bacfc…3255743`, 470,827 bytes |
| 3 | `cat`, `sed -n`, `grep -n` over the §17.2 inputs | read as §17.2 |
| 4 | identifier collision search over `docs/` and the D3-R5 copy for the new labels | a first draft used `IA-1` … `IA-3`, which this file already uses for assumptions, and `R6-1` … `R6-5`, which 29 other documents use. They were renamed `OC-1` … `OC-3` and `RX-1` … `RX-5` in the added lines only. The D3-R5 counts of `IA-1`, `IA-2` and `IA-3` are unchanged (6, 4, 4). `Lemma R6` and `𝒜` are used nowhere else |
| 5 | **D3-R5 preserved:** `diff` of the D3-R5 copy against this file, before §17 | **0** removed lines; 575 lines added in 25 hunks |
| 6 | **one `consume` literal:** full occurrences of the `ExecStartPre=` line | 6 in the D3-R5 copy and 6 before §17; none added |
| 7 | **one interruption literal:** full occurrences of the route (iii-a) command line | 7 in the D3-R5 copy and 7 before §17; none added. D3-R6 refers to the literal and does not repeat it |
| 8 | **the rule still grants `start` only:** added lines containing `lookup("verb")` | 0 |
| 9 | **RB-1 not made automatic:** added lines naming RB-1 | 2. Each states that RB-1 is unchanged, separately authorized and never automatic |
| 10 | **closure claims:** added lines matching "closed" | none declares a finding closed. The matches are "not declared closed", "declares no finding closed", "not closed in every case" and "fail-closed" |
| 11 | **no host command, assignment or implementation added:** added lines filtered for `/goal`, `ssh `, `rsync `, `git fetch\|clone`, code fences and `sudo -n` | one match, the existing prose "elevating through `sudo -n`" restated under "Who". No command, assignment or code block added |
| 12 | Markdown structure (scratch Python: column-0 fences, table cell counts outside fences with code spans masked, trailing whitespace), on the D3-R5 copy and this file before §17 | 14 fence lines in both, balanced; 113 tables before, 118 after; no table row with an inconsistent cell count; trailing whitespace only on the 6 deliberate header line breaks, as before |
| 13 | `git diff --no-index --check ⟨D3-R5 copy⟩ ⟨this file⟩` | no whitespace error reported. Exit 1 only because the files differ |
| 14 | `git diff --check` (tracked files) | exit 0 |

**Not run, and why:**

* **No host check** of any kind on any host. PO-21 (u), on which CX-4's
  voiding depends, and every other obligation remain uncited and unobserved.
  The authority excludes host access and upstream research. Whether systemd
  refuses a new start while a shutdown transaction is queued is uncited, and
  the design does not rely on it.
* **No test suite, formatter, linter or type checker.** No code changed, and
  the prompt prohibits suite runs. No suite figure is claimed.
* **No Markdown linter.** None is configured. Check 12 is the substitute.

### 17.8 Security, production-isolation, operational and rollback implications

* **This return** changes one documentation file and affects no host. It is
  reverted by restoring the D3-R5 bytes, whose SHA-256 is in the header.
* **Security.** The grant boundary of §4.2.5-R4 (i) is unchanged: no grant
  exists during or after any pass, including in CX-4. Route (iii-a) is
  narrower than D3-R4's, by Peter's decision, and adds no privilege. The
  executor's precondition check is two unprivileged reads.
* **Authority boundary.** OSA is now claimed only over 𝒜, and the claim has
  no exception there. CX-4 and the orderly-transition case are stated as
  outside 𝒜, not hidden in it.
* **Production isolation.** Unchanged. Everything runs on `oracle-test` only,
  and the production workspace host is never a source, controller, relay,
  destination, fallback or rollback target (OH-D-1).
* **Operational.** The executor may interrupt only a running pass whose
  consume step is durable. A hung CP waits for the start timeout, up to the
  pinned value. A pass whose condition cannot be established runs without a
  grant until it ends (CX-3).
* **Rollback.** RB-1 is still separately authorized and never automatic
  (OH-D-8). Records, journals and the claim are never deleted.

### 17.9 Proposed independent-review focus

1. **OS-6 as written** (§4.2.5-R6 (b)). Do OC-1 … OC-3 and the exclusions
   match the R6 authority exactly? Is the "durable by construction" argument
   sound?
2. **Lemma R6** ((c)). Does it hold for a stale read, a `stop` landing on a
   later attempt's `start-pre`, and an unloaded unit?
3. **The set 𝒜** ((d)). Is the boundary right? Is the enumeration of
   stop-job sources complete, in particular item 2's reading that §4.3.3 (a)
   compares the loaded dependency properties, including reverse ones?
4. **OSA without exception within 𝒜** ((e)). Does the proof now follow from
   the decision rather than from an assumption?
5. **CX-4 and the EO correction** ((f)). Is CX-4 stated exactly and honestly
   as outside 𝒜? Is the EO correction right, and is placing EO outside 𝒜,
   including a platform-triggered transition, acceptable, or a matter for
   Peter?
6. **Reconciliation** ((g), §4.7.1, §4.7.3, §4.7.4). Is any place still
   treating D3-R4's `activating`/`active` timing as current, or OS-6 as
   undecided?
7. §16.9 items 1 … 5 and 8 remain as stated there. Items 6 and 7 are
   answered by the decision and by items 3 and 5 above.

### 17.10 Statement of authority used

I used only the repository-documentation and read-only repository-inspection
authority of `C-P5.0-R5-RP11-H1-D3-R6`. **No host, network, credential,
implementation or execution authority was used.** No SSH, `rsync`, Git or
network retrieval, `oracle-test` or production-host access, credential
creation or installation, upstream research, build, installation, privilege,
`sudo`, `systemctl`, `systemd-run`, Polkit, `pkcheck`, service or database
action, H-0, H-1, H-2, `ACT`, `DEACT`, CP, RB-1, attestation, drill, evidence
pass, cleanup, commit or push occurred. No retained R4/R5 path was inspected.
No test suite was run. Nothing here is an accepted design, an executable
assignment, or authority for any step.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18, PO-19,
PO-20, PO-21 and H-1 remain open. RP-11 remains unwired and unmet. Package
RAID item `P5.0-R5` remains Blocking. `plan.is_executable=False`. Package 5.0
remains not ready.

Claude stops here, pending Codex's independent re-review.
