# Independent review — R5 H-0 evidence incomplete

Date: 2026-10-06

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-20261006-02`

Reviewer: Codex, independent of the Claude executor

## Disposition

Do not accept the reported `H-0 PASS`. R5 is consumed. The anonymous pinned
retrieval, isolated checkout and facts actually collected are credible, but
H-0 is incomplete against the accepted fact set. OH-S2 and every later slice
remain unauthorized.

The durable handback supports successful retrieval of pinned commit
`46d1c35a029ca8287779ae87d08a370ba0a0f2ef`, a clean detached checkout and a
closed retained evidence set. Local review reproduced the reported byte lengths
and SHA-256 values for `MANIFEST.payload`, `MANIFEST.final` and
`INVENTORY.owner-mode`; the manifest has 612 entries, and the inventory has
623 file rows followed by `violations=0`. The locally retained R5 prompt and
authority also match their pinned lengths and digests.

No remote path was revisited. This review made no network connection and did
not inspect, repair, retry or clean up any retained remote path.

## Findings

1. **Blocking — HF-15 is incomplete.** Accepted proposal §4.4.1 says the
   proposed capture-root parent's filesystem type, mount options and capacity
   are always recorded after OH-D-3 was decided. R5 supplied no capture-root
   path and the handback records this element as not observed. Recording that
   the required input was not specified is accurate reporting, but it is not
   the required host observation and cannot satisfy `H-0 PASS`.
2. **Blocking — HF-18 is incomplete.** Accepted proposal §4.4.1 says that,
   after OH-D-2 was decided, the interactive client's presence is recorded by
   `C-STAT` on its named path. R5 supplied no client path and reports HF-18 as
   `not specified`; no `C-STAT` observation exists. This is a design-input gap,
   not evidence that the required fact was observed.
3. **Important — the accepted design does not match the observed interpreter.**
   TR-9, HF-07, HF-08, HF-10 and PO-19 name `/usr/bin/python3.12`, but R5
   credibly records that Python 3.12 and its packages are absent and that the
   host provides `/usr/bin/python3.14` / CPython 3.14.4. A later design review
   must explicitly resolve and re-review that version-bound contract; the H-0
   run does not accept the substitution.
4. **Important — the active Polkit directory remains partly unknown.**
   `/etc/polkit-1/rules.d` is correctly recorded as unreadable to `ubuntu`, so
   the presence of `50-freedom-blades-rp11.rules` is unknown. This satisfies
   HF-12's allowed `unreadable` result, but later staging must not infer the
   rule is absent without separately authorized evidence.

The reported absence of concrete PO-21(i) condition paths is also retained as
a design-input gap. It is not treated as an additional executor defect here,
but OH-S2 cannot be released merely by accepting the two collected unit
`LoadState` values.

## Successor condition

Do not retry R5 or reuse, inspect, repair or clean up its retained paths. Peter
must first name the capture-root parent and interactive-client path, decide how
the Python 3.12/3.14 mismatch is to be handled, and determine whether any
additional PO-21(i) path input is required. Any gap-collection successor needs
a fresh work ID, fresh exclusive evidence path and separate authority. It may
collect only the missing or newly defined facts if the new authority explicitly
defines that narrower scope and how it composes with the accepted R5 evidence.

[R5 handback](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-handback.md) ·
[R5 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-authority.md) ·
[Accepted design](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md)
