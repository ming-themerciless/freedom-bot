# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R13

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Codex independently reviewed the R12 evidence-harness implementation on
2026-09-07 and returned **changes requested** with one Blocking finding:

- **EH-R12-1 — E7 is excluded from the required semantic identity
  observation.** The R12 authority required every `E1 … E8` identity to call
  `prctl(PR_GET_SECUREBITS)` inside the final interpreted case-program process
  and to compare the complete twelve-value identity observation before any
  dependent operation could run or be interpreted. The submitted plan creates
  `CASE_IDENTITY` steps and contracts for E1–E6 and E8 only. It explicitly
  excludes E7, substitutes P-01/P-02, and has tests that require an E7 identity
  step to be rejected. P-01/P-02 do not execute the case program and do not
  semantically compare E7's complete required observation.

Remediate exactly this finding. Preserve R12's accepted P-05 semantic gate,
E1–E6/E8 identity contracts, bounded `PR_GET_SECUREBITS` call, Option-B vector
grammar, C-3 symlink boundary, C-5 late binding, C-1 root boundary and C-4
materializer. The required result is a fully specified, semantically fail-closed
dry-run plan with zero unresolved design conflicts and `executable: True` on
paper. That state is **not permission to execute it**.

This prompt does **not** authorize `--execute`, an armed process boundary or
materializer, execution of a generated vector, SSH, inspection or mutation of
`oracle-test`, privileged or mutation-bearing commands, database operations,
the destructive backup/restore drill, Package 5.0 product implementation,
migration `0014`, deployment, cutover, OD-62's binding ruling or Package 5.1+.
Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.

## Required reading and worktree discipline

Before editing, read completely `.agents/AGENTS.md`,
`docs/implementation-plan.md`, `docs/operations/disposable-test-server.md`,
`docs/review/Handover information`, this prompt, the R12 prompt and R12
handback, package-plan §2.12–§2.13, and every file under
`tools/phase_5_0_evidence/` and `tests/phase_5_0_evidence/`. Check `git status`
and preserve the full dirty worktree. Do not reset, revert, stage, commit, push
or alter unrelated files.

Treat the R12 generated plan and digest
`6f555c13f4b7f19eb440886cb08e3709057f3776af9d088da51880e82c87d733` as
superseded review input, never execution authority. Do not pass it or any new
digest to `--execute`.

## EH-R12-1 — make E7 a real semantic identity prerequisite

Add an explicit E7 `CapturePolicy.CASE_IDENTITY` command step using the exact
reviewed Option-B case-program vector and running as the harness's root identity.
It must execute the `identity` verb in the final interpreted process, after
`execve`, and therefore call the already bounded
`prctl(PR_GET_SECUREBITS)` implementation before any operation whose attribution
depends on E7.

Do not route E7 through a fictitious `capsh` construction: package-plan
§2.13.5c defines E7 as the harness's own root process with no credential drop.
Do not weaken or replace P-01/P-02; retain them as separate root/target
preflight evidence. The new E7 observation supplements them and satisfies the
R12 semantic contract they do not satisfy.

Give E7 the same closed twelve-key contract as the other identities:

- `verb == identity` and `result == returned`;
- effective UID and GID;
- the complete supplementary-group set;
- `CapInh`, `CapPrm`, `CapEff`, `CapBnd`, and `CapAmb`;
- `NoNewPrivs`; and
- the final securebits returned by `prctl(PR_GET_SECUREBITS)`.

Every expected E7 value must come from an independent reviewed source, never
from the observation being judged. E7's environment-dependent UID/GID/groups,
capability masks, `NoNewPrivs`, and securebits therefore need explicit reviewed
target-fact constants and a fail-closed confirmation gate analogous to the two
unconfirmed interpreter facts. Values previously observed on another host or
kernel are not facts about `oracle-test`. Do not copy the 2026-08-31 host values
from package-plan §2.13.5c into executable expectations unless the Operations
Owner separately states them for the current target and an independent reviewer
verifies them.

The checked-in facts may remain `UNCONFIRMED`. While any E7 fact is unconfirmed,
the executor must refuse before starting any command, just as it currently does
for the interpreter digest and resolved path. The dry-run plan may still be
structurally complete and `executable: True`; operational blocking is not an
unresolved design conflict. Do not inspect the host or learn an expected E7
value from P-01, P-02, the E7 observation, `/proc`, `id`, `capsh`, or any other
output produced by the run being judged.

Ensure ordering makes the E7 observation a prerequisite for every E7-attributed
dependent operation. A missing, duplicated, unreadable, malformed, unexpected,
or unequal E7 value must make the step unsatisfied, stop the run, and prevent
all such dependent operations from reaching the boundary or being interpreted.
Use the existing fixed safe refusal vocabulary; do not expose observed host
values in classifications.

Update comments and prose that currently say E7 is not a step or that P-01/P-02
alone classify it. Update `CONSTRUCTED_IDENTITIES` or replace that concept with
an accurately named closed set so tests and validators no longer encode the
defect. Do not describe E7 as capsh-constructed merely to make the old name fit.

## Required regression tests

Add tests proving all of the following:

- the generated plan contains exactly one E7 `CASE_IDENTITY` step as well as
  the seven existing identity steps;
- its vector is the exact direct Option-B `identity` vector, runs as root, uses
  no `capsh`, declares no late-bound account/group substitution, and remains
  inside the validated disposable target;
- the E7 contract contains exactly the same twelve keys required for E1–E6/E8;
- each expected E7 value comes from a reviewed target fact rather than the
  observation;
- every unconfirmed E7 fact causes a pre-execution refusal before the process
  boundary is called;
- a complete matching E7 observation satisfies the contract when tests inject
  fixed reviewed facts;
- one mismatch in each field category—UID, GID, groups, every capability mask,
  `NoNewPrivs`, and securebits—makes E7 inconclusive;
- missing, duplicated, unreadable, malformed and unexpected E7 observations
  are refused through the fixed safe classifications;
- an E7 mismatch prevents every E7-attributed dependent operation from reaching
  the process boundary or being interpreted; and
- the securebits value is supplied by the case program's real observation path,
  not inferred from a vector or copied from P-01/P-02.

Retain all R12 tests. Correct tests and handback statements that currently claim
“every E1 … E8” while exercising only seven executor contracts.

## Preserve the R12 security boundary

Do not broaden:

- the interpreter path or exact `-I -S` prefix;
- the closed case-program verbs, arities, modes or path grammar;
- `PERMITTED_EXECUTABLES`;
- the delegated `capsh` and `systemd-run` tail validation;
- the four late-bound names or substitution sites;
- the symlink target or cleanup primitive;
- target-root validation;
- the `ctypes` exception beyond the existing one file, one function and one
  literal `PR_GET_SECUREBITS` operation;
- materialization destinations or bytes;
- process/materializer arming rules; or
- the authority required to establish reviewed target facts and later execute
  the harness.

Do not supply real interpreter or E7 target facts, inspect `oracle-test`, or
convert any unconfirmed-fact refusal into a warning. If a complete E7 contract
cannot be constructed without a new maintainer decision, stop and return the
exact decision instead of inventing policy.

## Generated artifacts and verification

Regenerate the concrete plan and review manifest from covered sources. Generate
each twice and compare byte-for-byte; independently re-hash every covered
source. Never hand-edit generated artifacts. Bump manifest/harness versions if
their declared contracts require it. Report the new digest as review material
only.

Run serially with the documented interpreters and exported
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`:

1. complete `tests/phase_5_0_evidence` under the bot interpreter;
2. the same suite plus `tests/web/test_p3_4_static_assets.py` under the web
   interpreter;
3. the non-destructive backup/layout selection, with the same seven destructive
   database cases explicitly deselected as R12;
4. the complete bot suite with those same cases deselected;
5. the complete web suite, reporting the expected skip count;
6. Foundry's Node suite;
7. `compileall` for changed Python under both interpreters; and
8. `git diff --check`.

The dry run must remain inert and report zero unresolved design conflicts. Do
not run a destructive or privileged case to improve a test total.

## Required R13 handback and stop

Add a new R13 section to
`docs/review/phase-5-0-evidence-harness-implementation-handback.md` and update
`docs/review/Handover information` to point to it. State:

- the original E7 exclusion and why P-01/P-02 were insufficient;
- the new E7 step, exact vector, ordering and twelve-value contract;
- every reviewed E7 target fact and its current confirmed/unconfirmed state;
- how unconfirmed facts refuse before any process starts;
- the mismatch/refusal matrix and tests;
- every prior R12 boundary preserved;
- what changed in the generated artifacts and their new digest;
- exact verification results, skips and deselections;
- every privileged or destructive check not run;
- confirmation that no host inspection or mutation occurred; and
- every judgement call, residual or newly discovered dependency.

Then stop for Codex's independent R13 pre-execution review. Do not execute the
plan. Only a later explicit maintainer authorization may permit reading the
interpreter or E7 target facts or running the disposable-server evidence
harness. OD-62 remains open until the required operational evidence and
independent review exist.
