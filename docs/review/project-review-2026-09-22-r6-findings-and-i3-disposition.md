# R6 findings and I3 disposition — 2026-09-22

Peter Duscha records the following decisions:

1. **PR-20260920-LAB-I3-R6-1 is Closed by maintainer disposition.** Continuing
   after the mandatory secrets-guard stop remains a historical procedural
   violation. Closure does not create retroactive compliance. R6 is retained
   but is inadmissible as gate evidence.
2. **PR-20260920-LAB-I3-R6-2 is Closed by maintainer disposition.** The `scp`
   write remains historically unauthorized. Closure does not retroactively
   authorize it. `/tmp/fb-i3-r6-filelist.txt` remains protected and preserved;
   no read, inspection, `stat`, deletion, modification, move, reuse or cleanup
   is authorized.
3. **R8 is accepted as valid replacement gate evidence and I3 is Closed.** R8
   ran unbroken, both verifier invocations returned `verified`, all four
   contexts verified, all tracked objects were removed, and both final surveys
   were clean. R6 remains in the record for accountability but supplies no gate
   evidence.

These decisions authorize no host action, digest use or `--execute`; do not
change `plan.is_executable=False`; do not make Package 5.0 ready; and do not
decide P5.0-R5 or OD-62.
