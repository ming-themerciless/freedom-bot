# Authority — direct SSH-controlled OH-S0b/OH-S1 H-0

Date: 2026-10-05

Authority: Peter Duscha, Product Owner and Acceptance Authority

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R3-20261005-06`

Peter Duscha authorizes Claude Code in the production workspace to execute the
one-shot assignment in
[`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-claude-prompt.md).
Claude remains on the controller host and may make exactly one SSH execution
connection to `oracle-test`. It sends one self-contained, reviewed H-0 program
on standard input. That program performs all identity checks, repository
retrieval, observations and evidence writes locally on `oracle-test` as
`ubuntu`; only terminal output and the final handback return to the controller.

This decision supersedes R2 before execution. R2 is withdrawn unused; its work
ID and evidence path must not be used. For R3 H-0 only, this authority also
supersedes OH-D-2's local-client/no-scripted-controller condition and the
production-isolation table's controller/relay prohibition. The SSH transport
and controller remain outside the trusted execution path. This does not change
H-1, H-2, activation or Pass A topology.

The controller may use its already configured SSH authentication without
reading, printing, copying or forwarding credential material. Agent, X11,
port and other forwarding are disabled. No repository byte, environment,
credential or application data is transferred from the controller. The only
controller-supplied executable bytes are the exact R3 H-0 program, which the
remote bootstrap retains in the evidence directory before execution.

The remote program must first establish `ubuntu@Test`; otherwise it stops
before any remote write or network access. It then exclusively creates
`/var/tmp/p5-r5-rp11-h0-20261005-04-h0-evidence`, retains its exact bytes and
SHA-256 there, retrieves pinned commit
`46d1c35a029ca8287779ae87d08a370ba0a0f2ef` directly and anonymously from the
fixed canonical public HTTPS repository, and collects HF-01 through HF-20.

The assignment ends at its first `H-0 PASS` or `HARD STOP`. No second SSH
execution attempt, retry, repair, interactive authentication, credential
access or forwarding, `sudo`, package operation, build, test, service/database
mutation, H-1/H-2, activation, rollback, cleanup, commit or push is authorized.
OH-S2 and every later slice remain unauthorized pending independent Codex
review and a further recorded decision.

