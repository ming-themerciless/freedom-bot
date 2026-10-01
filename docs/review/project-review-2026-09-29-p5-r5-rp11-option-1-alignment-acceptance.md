# RP-11 Option-1 alignment review acceptance — 2026-09-29

Decision ID: `C-P5.0-R5-RP11-I1-R3-D2-DOC1-R2`

Peter Duscha accepts Codex's independent review of the corrected Option-1
documentation alignment. The review found no Blocking, Important or Optional
finding and independently reproduced the full evidence package at both tested
descriptor limits: **3348 passed, 0 skipped** with the soft limit lowered to
1024, and **3348 passed, 0 skipped** at the default limit.

The accepted review confirms that:

* the corrected operational draft is SHA-256 `5c6046fc3dc0b9a931cc32076233b1ea9185dc14c5d0ea1abc193687dcca7de6`;
* the historical decision proposal is restored to SHA-256 `ac504ce188cb2eb477006eb3cbbdf0d66cd932568ecb5ed62a72151ba47f3e60`;
* manifest version 25 and review-input digest `f63cf3596a95701e3c24813f5362955dcdb5524e7b4fcaf749159db66f91cdb8` remain the review inputs; and
* the D2-DOC1-R1 erratum adequately preserves the historical record without
  rewriting the durable D2-DOC1 handback.

Peter accepts the reviewer's recommendation and closes these findings as
**superseded by the accepted I1-R3 retained-alias design**:

* `RP11-I1-2` (Blocking): the non-reproducing `O_TMPFILE`/`/proc/self/fd`
  publication route was removed;
* `RP11-I1-R2-1` (Blocking): the separate probe and its `stat`→`unlink` cleanup
  race were removed, and the RP-11 publication path performs no unlink, rename
  or alias cleanup; and
* `RP11-I1-R1-1` (Important): the removed standalone probe no longer has an
  evidence obligation; each pass's first real X-1 genesis publication is the
  fail-closed capability test.

This is acceptance of the documentation alignment, independent review and
finding dispositions only. It does **not** accept or wire the RP-11 mechanism,
approve an execution digest, satisfy RP-11, resolve C-11 or the pinned launcher
environment, authorize either operational pass, or change a package gate.
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

No SSH, synchronization, network or host inspection, `sudo`, database access,
provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, real capture root, protected-artifact access,
secrets scan, commit or push occurred.
