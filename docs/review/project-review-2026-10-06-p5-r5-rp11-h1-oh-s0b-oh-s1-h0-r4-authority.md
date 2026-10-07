# Authority — R4 isolated-checkout OH-S0b/OH-S1 H-0

Date: 2026-10-06

Authority: Peter Duscha, Product Owner and Acceptance Authority

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R4-20261006-01`

Peter Duscha directs the routine implementation details to be resolved without
further escalation and authorizes Claude Code in the production workspace to
execute the one-shot R4 assignment in
[`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-claude-prompt.md).

R4 preserves the dirty checkout at `/opt/freedom-blades/platform` without
inspection or mutation. Through exactly one forwarding-disabled,
non-interactive SSH execution connection, its retained remote program creates
an exclusive temporary checkout, anonymously retrieves only pinned commit
`46d1c35a029ca8287779ae87d08a370ba0a0f2ef` from the canonical public HTTPS
repository, and collects H-0 facts into a new exclusive evidence directory.

The program may use an available `/usr/bin/python3` only after recording its
resolved executable and version; it must not assume `/usr/bin/python3.12`.
Absence of a suitable Python 3 interpreter is a HARD STOP, not permission to
install anything.

The assignment ends at its first `H-0 PASS` or `HARD STOP`. It authorizes no
second SSH connection, retry, repair, credential access or forwarding, `sudo`,
package operation, installation, build, test, service/database mutation,
H-1/H-2, activation, rollback, cleanup, commit or push. The isolated checkout
and evidence directory are retained. Claude must preserve its exact terminal
handback in the dedicated repository file named by the prompt before returning
in chat. OH-S2 and every later slice remain unauthorized pending independent
Codex review and a further recorded decision.
