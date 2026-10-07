# Decision — `oracle-test` alias and `Test` kernel nodename

Date: 2026-10-05

Decision owner: Peter Duscha, Maintainer and Acceptance Authority

## Decision

`oracle-test` remains the operational SSH alias for the disposable test server.
The same machine's approved kernel nodename, as returned by `uname -n` and
`os.uname().nodename`, is `Test`.

Future assignments must keep these identifiers distinct:

- connection target / SSH alias: `oracle-test`;
- expected local kernel nodename: `Test`.

An identity check must not compare `uname -n` with the SSH alias. Where stronger
machine identity is required, it must bind the observed nodename `Test` to the
separately approved machine-id digest and other fixed host facts.

## Effect on completed assignments

This corrects the identity premise for future work. It does not rewrite either
executed prompt or retroactively change its terminal rules. The consumed H-0
work ID remains consumed, and H-0 still requires a fresh assignment and evidence
path. The bootstrap installation remains subject to the other findings from its
independent review.

