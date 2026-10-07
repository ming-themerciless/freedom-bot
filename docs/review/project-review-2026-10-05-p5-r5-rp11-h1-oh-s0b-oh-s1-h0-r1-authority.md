# Authority — corrected OH-S0b public retrieval and OH-S1 H-0

Date: 2026-10-05

Authority: Peter Duscha, Product Owner and Acceptance Authority

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R1-20261005-04`

Peter Duscha authorizes Claude Code to execute the exact one-shot assignment in
[`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r1-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r1-claude-prompt.md).

Claude must run locally and interactively on `oracle-test` as `ubuntu`. The
kernel nodename check is against `Test`; `oracle-test` is the SSH alias and is
not the expected `uname -n` value. Claude may retrieve only pinned commit
`46d1c35a029ca8287779ae87d08a370ba0a0f2ef` directly and anonymously from the
fixed canonical public HTTPS repository, then collect the accepted
unprivileged, read-only H-0 facts HF-01 through HF-20 into the exclusive
evidence directory named by the prompt.

The assignment terminates at its first `H-0 PASS` or `HARD STOP`. It is
one-shot: no retry, repair, authentication, credential use, privilege, package
operation, build, test, service/database mutation, H-1/H-2, activation,
rollback, cleanup, commit or push is authorized. OH-S2 and every later slice
remain unauthorized pending independent Codex review and a further recorded
decision.

