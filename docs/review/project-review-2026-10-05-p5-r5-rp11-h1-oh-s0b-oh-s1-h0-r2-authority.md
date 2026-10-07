# Superseded authority — controller-launched OH-S0b public retrieval and OH-S1 H-0

Status: **withdrawn unused and superseded by R3 on 2026-10-05**. Do not execute
this authority or use its work ID or evidence path.

Date: 2026-10-05

Authority: Peter Duscha, Product Owner and Acceptance Authority

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R2-20261005-05`

Peter Duscha authorizes Claude Code running in the production workspace to act
only as a narrow launch controller for the assignment in
[`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r2-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r2-claude-prompt.md).
It may use the already configured SSH route to `oracle-test` to start and
interactively drive a Claude Code process that runs locally there as `ubuntu`.

For this R2 controller bootstrap only, this decision supersedes OH-D-2's “no
scripted remote controller” condition and the production-isolation table's
controller/relay prohibition. It does not amend the trusted execution path:
the SSH/login transport remains outside it, and no controller-supplied byte is
accepted as repository or H-0 evidence. It does not change H-1, H-2, activation
or pass topology; those retain the accepted one-host rules.

The controller may transmit only terminal control, the assignment invocation
and the exact prompt/authority text needed to start the remote process. It may
receive terminal output and the final handback. It must not transfer repository
or implementation bytes, forward an agent or environment, read or copy a key,
token or model-provider credential, run H-0 commands through SSH, create or
modify evidence itself, or use the production workspace as a retrieval source,
execution host, destination, fallback or rollback target.

The remote Claude process must establish locally that it is `ubuntu` and that
the kernel nodename is `Test`. Only that process may retrieve pinned commit
`46d1c35a029ca8287779ae87d08a370ba0a0f2ef` directly and anonymously from the
fixed canonical public HTTPS repository and collect HF-01 through HF-20 into
`/var/tmp/p5-r5-rp11-h0-20261005-03-h0-evidence`.

This is a one-shot replacement for the consumed R1 authority. It ends at the
first `H-0 PASS` or `HARD STOP`. It authorizes no retry, repository transfer
from the controller, credential access or forwarding, `sudo`, package
operation, build, test, service/database mutation, H-1/H-2, activation,
rollback, cleanup, commit or push. OH-S2 and every later slice remain
unauthorized pending independent Codex review and a further recorded decision.
