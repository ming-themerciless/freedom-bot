# Authority — OH-S0b public retrieval and OH-S1 H-0 fact collection

Date: 2026-10-05

Decision owner: Peter Duscha, Maintainer and Acceptance Authority

## Decision

Peter Duscha authorizes Claude to execute the bounded assignment in
[`phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-claude-prompt.md).

The authority has two ordered parts:

1. OH-S0b: from an interactive session running locally on `oracle-test` as
   `ubuntu`, retrieve commit `46d1c35a029ca8287779ae87d08a370ba0a0f2ef`
   directly and anonymously from the canonical GitHub repository using
   `https://github.com/ming-themerciless/freedom-bot.git`; and
2. only after exact commit verification, OH-S1: collect the accepted H-0
   read-only facts HF-01 through HF-20 and return their retained-evidence
   digest and a complete handback for Codex review.

Public, credential-free HTTPS is the only retrieval route authorized. An
authentication prompt, access denial, missing commit, wrong repository,
non-clean checkout, checkout conflict or inability to establish exact commit
identity is a HARD STOP. No credential may be read, requested, created,
installed or reused. No SSH Git URL, production-workspace transport, remote
controller, reset, clean, deletion, overwrite or fallback is authorized.

## Boundary

Claude runs locally on `oracle-test` as `ubuntu` through an interactive login
session. The production workspace host is never a source, controller, relay,
destination, fallback or rollback target.

The retrieval may update the existing clean Git checkout only through the
exact fetch and detached checkout described by the assignment. H-0 is
unprivileged and read-only except for its own exclusively created
`/var/tmp/...-h0-evidence` directory. No `sudo`, package operation,
installation, build, test suite, service mutation, database access, H-1/H-2,
activation, evidence pass, rollback, cleanup, commit or push is authorized.

The authority is consumed at the first terminal state: `H-0 PASS` or `HARD
STOP`. There is no retry or remediation authority.
