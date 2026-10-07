# Acceptance — composed H-0 and U-9 restatement

Date: 2026-10-06

Decision owner: Peter Duscha, Product Owner and Acceptance Authority

## Decisions

Peter Duscha accepts Codex's independent H-0G R1 review and its composition
of R5 plus H-0G as **`H-0 PASS`**.

Peter also accepts the following Route 1 restatement:

> **U-9 — glibc/loader evidence.** Add an explicit numbered,
> version-specific glibc/dynamic-loader proof obligation covering the trusted
> loader inputs relevant to `/usr/bin/python3.14`. The proof must bind to the
> H-0-recorded `libc6` version and the executable's `DT_RUNPATH`/`DT_RPATH`.
> Any version or executable-digest drift requires re-citation before H-1 may
> proceed.

Python 3.14 is the deployed RP-11 entry-interpreter target. Testing under
another supported Python version may provide useful portability or regression
evidence, but does not replace the exact-version production trust proof,
target-version tests or drift gates.

## Effect and limits

The two prerequisites named by accepted R3 §14 for completing OH-S2 are now
satisfied: the H-0G composition is accepted and U-9 is restated for the exact
Python 3.14 path.

This decision does not itself perform citation work, modify implementation,
build a launcher, inspect a host, authorize cleanup, or begin H-1/H-2. Each
later slice retains its own review gate.

[Composed H-0 review](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-composed-h0-pass.md) ·
[Accepted R3 contract](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md) ·
[Original U-9 decision](project-review-2026-10-04-p5-r5-rp11-h1-prerequisite-decisions.md)
