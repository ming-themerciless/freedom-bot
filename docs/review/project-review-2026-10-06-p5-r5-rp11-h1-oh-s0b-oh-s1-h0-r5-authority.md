# Authority — R5 isolated-checkout OH-S0b/OH-S1 H-0

Date: 2026-10-06

Authority: Peter Duscha, Product Owner and Acceptance Authority

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-20261006-02`

Authorized prompt:
[`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-claude-prompt.md),
SHA-256 `57d23c1ba683ce8c2be15fe101da959a9dc1334ff89a1b0c66f917f26cf42e8e`,
6942 bytes.

Peter Duscha authorizes Claude Code in the production workspace to execute the
exact R5 prompt revision identified above. R5 preserves the dirty fixed checkout
without inspection or mutation and uses only these fresh exclusive paths:

- checkout: `/var/tmp/p5-r5-rp11-h0-20261006-02-checkout`
- evidence: `/var/tmp/p5-r5-rp11-h0-20261006-02-evidence`

Through exactly one forwarding-disabled, non-interactive SSH execution
connection, its retained remote program may anonymously retrieve only pinned
commit `46d1c35a029ca8287779ae87d08a370ba0a0f2ef` from
`https://github.com/ming-themerciless/freedom-platform.git` and collect H-0
facts HF-01 through HF-20. The controller may perform offline preparation only;
no controller-side network preflight is authorized.

The program may use the available `/usr/bin/python3` only after recording its
resolved executable and version and only with `-I -S` for bounded evidence
helpers. It must not assume `/usr/bin/python3.12`. Absence of a suitable Python
3 interpreter is a HARD STOP, not permission to install anything.

The assignment ends at its first `H-0 PASS` or `HARD STOP`. It authorizes no
second SSH connection, retry, repair, controller-side network preflight,
credential access or forwarding, `sudo`, package operation, installation,
build, test, service/database mutation, H-1/H-2, activation, rollback, cleanup,
commit or push. Every earlier checkout and evidence path remains untouched.

Claude must preserve its complete, unabridged terminal handback in
`docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-handback.md` before
returning the same complete handback in chat. This is the single repository
write authorized by this assignment. OH-S2 and every later slice remain
unauthorized pending independent Codex review and a further recorded decision.
