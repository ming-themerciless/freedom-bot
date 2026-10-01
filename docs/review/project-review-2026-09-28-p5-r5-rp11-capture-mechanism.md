# Codex review — P5.0-R5 RP-11 capture mechanism — 2026-09-28

Reviewer: Codex, independent of the Claude implementation

Reviewed handback:
`phase-5-0-p5-r5-rp11-capture-mechanism-implementation-handback.md`.
Controlling contract: the R5-amended
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` at SHA-256
`5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3`.

## Result — changes requested

RP-11 is **not accepted or satisfied**. Two Blocking findings remain. The
implementation is still unwired, neither operational pass is executable or
authorized, P5.0-R5 remains Blocking, OD-62 G-A remains conditional,
`plan.is_executable=False`, and Package 5.0 remains not ready.

### RP11-I1-1 — Blocking — publication does not implement the accepted contract

The accepted RP-11 contract requires each record and immutable index state to
be completed under a **temporary name**, file-synchronized, and published by an
atomic **rename** that replaces nothing. The assignment required that contract
to be implemented exactly and required the implementer to stop on a
contradiction rather than choose a weaker or different reading.

The returned implementation deliberately uses an unnamed `O_TMPFILE` inode and
publishes it through `/proc/self/fd/N` with `linkat`; there is no temporary name
and no rename. This may be a viable replacement design, but it is a material
change to P-5/P-7, not an implementation of the exact accepted bytes. The
maintainer's in-session direction is recorded in the handback as a deviation;
it did not amend the controlled draft through §0.2 change control or receive
independent review before implementation.

Remediation requires one of:

1. implement the exact accepted temporary-name/non-replacing-rename contract;
   or
2. amend the operational draft to specify the unnamed-inode/link publication
   contract, including its platform prerequisites and failure semantics, then
   obtain independent review and maintainer acceptance of those exact bytes
   before the implementation can satisfy RP-11.

The same re-review must cover the amended shared `os.link` primitive because it
changes a previously reviewed I3 contract and serves two callers with different
follow semantics.

### RP11-I1-2 — Blocking — focused evidence is not reproducible on this repository host

The exact focused command reported by the handback was rerun locally with
`TEST_DATABASE_URL` explicitly unset and the cache provider disabled. Result:
**991 passed, 179 failed, 0 skipped**. The two expected pytest configuration
warnings were present.

The ordinary success paths fail before a durable genesis state. The production
publication route creates the unnamed file successfully, but
`link_unnamed_descriptor()` fails with `FileNotFoundError` (`errno 2`) while
linking `/proc/self/fd/N`; `CaptureRootStore` reduces that to
`X-1:genesis:publish: publication-failed`, and every dependent session is
`no-genesis`. A direct local probe of the same repository function reproduced
the `ENOENT` result.

Failing closed is correct, but it does not prove a usable capture mechanism on
the repository host. It also contradicts the handback's reported 1170-pass
local evidence and its statement that the route was confirmed locally. The
handback does not identify an environment distinction that reconciles the two
results.

Remediation must make the accepted publication mechanism work on the actual
repository-host filesystem/runtime selected for the passes, add an explicit
pre-admission capability check where platform support is conditional, and
rerun the required focused suites on the exact reviewed tree. The handback must
record the host/filesystem/runtime facts needed to explain and reproduce the
result without using a real capture root or creating operational authority.

## Reviewed decisions and remaining integration questions

* A behavioural terminal seal is consistent with the draft's operator-level
  read-only rule only if the amended contract states that meaning explicitly;
  it is not an operating-system write-protection control and must not be
  described as one.
* C-11 synchronization routing remains unresolved. A mechanism that cannot
  carry the exact guarded synchronization command cannot make either pass
  executable.
* The launcher's exact environment remains unresolved and must be pinned before
  wiring. It must not be inferred at execution time.
* The fixed `rp11-capture-binding` block must be incorporated into the
  controlling draft's §14 and `MI.pass_a_handback` contract before B0-RA can
  consume an operational handback.
* The capture-tool digest scope must be decided and pinned in the amended
  draft. The current digest includes complete shared modules, which is safe but
  broad.

These are not waived by the two implementation findings. RP-11 cannot be
accepted until the contract, implementation, focused evidence and operational
binding agree.

## Checks performed and limits

Commands/checks:

* read the governing agreement, implementation-plan sections required by its
  reading map, active handover, disposable-server restriction banner,
  assignment, accepted R5 contract/review, handback, implementation and tests;
* inspected task-relevant Git status and preserved the existing modified files;
* reran the handback's exact focused/local pytest selection with
  `TEST_DATABASE_URL` unset: **991 passed, 179 failed, 0 skipped**;
* reproduced the publication failure through the repository's
  `link_unnamed_descriptor` function: `FileNotFoundError`, errno 2; and
* performed no SSH, synchronization, network or host inspection, database
  access, `sudo`, provisioning, controlled write, reboot, verifier, evidence
  band, harness `--execute`, real participant invocation, protected-artifact
  access or secrets scan.

The full bot/web suites, `oracle-test`, crash/power-loss testing and any real
capture root were excluded by the active assignment. This review creates no
host or operational authority.
