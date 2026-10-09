# LIT-FULL WP-2 assignment preparation — 2026-10-09

## Outcome

A proposed repository-only WP-2 assignment is prepared for independent review:

- [Proposed WP-2 prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-claude-prompt.md)
- proposed work ID:
  `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-20261009-13`
- exact size: 10,590 bytes, 201 lines
- SHA-256:
  `e1e05e48443cf0d2f79a9983e074a6aec192e3f6738db9359e3d777c2d2268bc`

The prompt is **not accepted, assigned, authorized or executable**. The agent
that prepared it has checked it for internal consistency but is not its
independent reviewer. A different reviewer must review the exact pinned bytes,
and Peter Duscha must later accept the exact prompt and name an executor before
WP-2 can start.

## Gate basis

The prerequisites recorded by accepted WP-1 are satisfied for canonical row
F-1:

- WP-1 is independently reviewed and accepted;
- PD-2a is B2-F;
- PD-2b puts `AP-2` and the OS-6 `stop` in the set;
- PD-3 is B3-OUT;
- EX-1 and EX-2 §0.2 control is closed under baseline v1.8;
- EX-3 is not selected; and
- neither B2-N nor a Python-free installer is a design prerequisite.

Those facts permit preparation of a WP-2 prompt. They do not authorize its
execution.

## Proposed scope

The prompt inventories exactly RT-1 through RT-5, SA-1 and SA-2 at system-call
intent: consume, hold, stop-post, backstop, `attest`, static `start` and static
`stop`. It excludes the unprivileged entry and the EX-2 installer class. It
requires complete coverage of R8 §7.3 rows 1 through 22 and 3a through 3g,
per-procedure and sub-role traceability, process-creation classification under
the no-dynamic-child boundary, DI-1 through DI-6 mapping inputs, reconciliation
tables and the dynamic-child hard stop.

It explicitly prohibits WP-3 interface design, WP-4 image design, WP-5 proof
planning, WP-6 equivalence decisions, WP-7 estimating, external research, host
facts, implementation and operational work.

## Independent-review request

The independent reviewer should verify at minimum:

1. the seven-procedure roster and the entry/installer exclusions match the
   accepted F-1 boundary;
2. EX-1, EX-2, HB-1, BC-4 and baseline v1.8 are stated without broadening them;
3. every WP-2 obligation in accepted R8 §9.5 and WP-1 R6 §§10 through 12 is
   present;
4. the required inventory reaches sends, identity validation, reap attempts,
   credential changes and every other operation rather than only DI rows;
5. the prompt does not pre-empt WP-3 through WP-7 or invent citations, host
   facts, interfaces, syscalls or images;
6. the no-dynamic-child stop rule is fail-closed and cannot silently become
   SCDC/BC-3;
7. return-time snapshot and pointer controls preserve history; and
8. the restrictions create no host, implementation, test, commit or push
   authority.

## Checks and limits

`wc -l -c`, `sha256sum`, targeted fixed-string review and `git diff --check`
were run against the proposed prompt. No application or hook suite was run
because the preparation changes documentation only and current restrictions
authorize no tests. No host, retained evidence, network, package, service,
database, implementation, commit or push action occurred.
