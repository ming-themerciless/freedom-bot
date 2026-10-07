# Independent review — R4 H-0 retrieval HARD STOP

Date: 2026-10-06

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R4-20261006-01`

Reviewer: Codex, independent of the Claude executor

## Disposition

Accept the substantive `HARD STOP`. R4 is consumed. H-0 did not pass, and
OH-S2 and every later slice remain unauthorized.

The retained evidence shows that the one authorized SSH execution reached
anonymous Git retrieval, disabled prompting and credential helpers, and
stopped when Git exited 128 with `fatal: unable to get password from user`.
No commit verification, checkout, governing-file verification or HF-03 through
HF-20 collection followed.

Local review of the durable handback reproduced all 80 embedded evidence-block
sizes and SHA-256 values. All 68 embedded payload entries match
`MANIFEST.payload`; the remaining payload entry is the separately retained
40,147-byte program. `MANIFEST.payload` and `MANIFEST.final` reproduce their
reported digests and lengths.

## Findings

1. **Important — authority discipline.** Preparation accidentally issued a
   controller-side anonymous `git ls-remote` outside the retained one-shot
   remote program. It used no credential and its output was discarded, so it
   does not invalidate the remote failure evidence, but it was outside scope.
2. **Important — terminal reporting.** The prompt required the complete
   handback verbatim in chat. The executor returned a summary. The durable file
   is complete, so this is a reporting nonconformance, not an evidence blocker.
3. **Optional — retained exclusions wording.** `EXCLUSIONS` says both c019
   `.err` and `.meta` were absent from the inventory. The inventory proves the
   `.err` was present and only `.meta` was absent. The handback records the
   erratum accurately without rewriting retained evidence.

## Successor condition

Do not retry R4 or reuse its paths. Any successor requires a new work ID, fresh
exclusive paths and separate authority. It must name the canonical repository
URL current at authorization time.

[R4 handback](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-handback.md) ·
[R4 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-authority.md)
