# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R12

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Codex independently reviewed the R11 evidence-harness implementation on
2026-09-07 and returned **changes requested** with two Blocking findings:

- **EH-R11-1 — P-05 observations are not enforced.** The case program emits
  runtime observations and the capture boundary sanitizes them, but
  `ExecutingRunner` declares the step satisfied from exit status alone. It does
  not compare the observed interpreter path/version/SHA-256, isolation flags,
  third-party visibility or installed case-program digest with reviewed
  expectations.
- **EH-R11-2 — securebits are asserted from intent rather than observed.** The
  case program omits `prctl(PR_GET_SECUREBITS)` and relies on the presence of
  `capsh --secbits=`. Package-plan §2.13.5c and JNL-49/JNL-50 require every E1…E8
  identity's final securebits to be observed before its operation.

Remediate exactly these findings while preserving R11's accepted Option-B
vector grammar, C-3 symlink boundary, C-5 late binding, C-1 root boundary and
C-4 materializer. The required result is a fully specified, semantically
fail-closed dry-run plan with zero unresolved items and `executable: True` on
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
`docs/review/Handover information`, this prompt, the R11 prompt and R11
handback, package-plan §2.12–§2.13, and every file under
`tools/phase_5_0_evidence/` and `tests/phase_5_0_evidence/`. Check `git status`
and preserve the full dirty worktree. Do not reset, revert, stage, commit, push
or alter unrelated files.

Treat the R11 generated plan and digest
`dfa61a575315803c6bb2f9ee39ec3bf4e2fcd7f25e895b5fdacb1acf58b454e0` as
superseded review input, never execution authority. Do not pass it or any new
digest to `--execute`.

## EH-R11-1 — make P-05 a semantic prerequisite

Add a typed, closed expectation contract for `CapturePolicy.CASE_RUNTIME` and
enforce it inside the executor before P-05 can be marked satisfied. Exit status
0 is necessary but not sufficient.

P-05 must require exactly one readable value for every expected key and compare
at least:

- `verb == runtime` and `result == returned`;
- `interpreter == case_runtime.INTERPRETER_PATH`;
- `interpreter_real` equals a separately reviewed expected resolved path, or is
  validated by another explicitly documented reviewed rule that cannot learn
  its own expectation from this observation;
- `python_version == case_runtime.INTERPRETER_PYTHON_VERSION`;
- `interpreter_sha256 == case_runtime.EXPECTED_INTERPRETER_SHA256`;
- `isolated == yes` and `no_site == yes`;
- `third_party_importable == no`;
- `case_program == case_runtime.case_program_path(target)`; and
- `case_program_sha256` equals the review manifest's covered-source digest for
  `CASE_PROGRAM_SOURCE`, which is also the byte-for-byte installation digest.

Missing, duplicate, malformed, unreadable, unexpected or unequal values must
make P-05 unsatisfied with a fixed safe classification. They must stop the run
before any dependent case and must never be reported as a pass or merely stored
for later interpretation. Do not include observed paths, digests, identifiers
or exception text in the failure classification.

Do not special-case this only in rendering or handback prose. The enforcement
must operate on the `CommandResult` that the executor actually receives,
immediately after capture sanitation and before `StepOutcome.satisfied`,
`state.satisfied_steps` or any dependent execution decision is produced.

Keep expectations separate from observations. The expected interpreter digest
remains an externally supplied reviewed target fact; do not learn it from P-05.
The expected case-program digest must come from the source bytes already used to
construct the reviewed manifest, not from P-05's output or the installed file.
If the executor cannot bind that manifest-derived expectation without creating
a circular self-approval, stop and return the exact dependency.

Add regression tests proving a P-05 result with exit 0 is rejected for each of:

- no observations;
- one missing key;
- a duplicate key or unreadable value;
- wrong interpreter path or resolved path;
- wrong Python version;
- wrong interpreter digest;
- `isolated=no`, `no_site=no`, or `third_party_importable=yes`;
- wrong case-program path; and
- wrong case-program digest.

Also prove the exact complete observation set passes when all expected values
match, and that no dependent case reaches the boundary after any mismatch.

## EH-R11-2 — observe final securebits inside E1…E8

Restore the package-plan requirement literally: each E1…E8 identity observation
must call `prctl(PR_GET_SECUREBITS)` inside the final interpreted case-program
process, after `capsh` has applied the credential/capability construction and
after `execve`, and before the operation whose attribution depends on that
identity. Capture `securebits` as a bounded numeric/hex observation and compare
it with the exact value declared for that E identity.

Python 3.12 does not expose `prctl` in `os`. The smallest permitted mechanism is
a tightly scoped `ctypes` call **inside `execution/case_program.py` only**:

- load the current process's already-required C runtime with `ctypes.CDLL(None,
  use_errno=True)`;
- bind only the literal `prctl` symbol;
- declare fixed `argtypes` and `restype`;
- call only literal operation `PR_GET_SECUREBITS` with zero arguments;
- accept no library name, symbol, operation or raw arguments from the vector;
- on `-1`, obtain the errno and report it through a fixed safe failure path;
- range-check the returned value before emitting it; and
- expose no reusable arbitrary-FFI helper.

This is a narrow exception to the execution-tier `ctypes` prohibition, justified
solely by the already-approved `PR_GET_SECUREBITS` evidence contract. Update the
structural guard so it permits `ctypes` only in this one file and mechanically
asserts the literal library, symbol, operation and argument shape. `ctypes`,
dynamic import, `getattr`, arbitrary symbol lookup and arbitrary native calls
must remain forbidden everywhere else. If this exact mechanism cannot be
bounded mechanically, stop and return the choice instead of weakening the
guard globally.

Extend `CapturePolicy.CASE_IDENTITY` to require a shaped `securebits` value.
More importantly, add typed semantic expectations for every E1…E8 identity:
effective UID, GID, complete supplementary-group set, `CapInh`, `CapPrm`,
`CapEff`, `CapBnd`, `CapAmb`, `NoNewPrivs` and securebits. Compare the captured
observation against the identity's reviewed expected values before the identity
step can satisfy its case or authorize interpretation of a dependent operation.
Exit 0 and the presence of a `capsh --secbits=` argument are not evidence of the
final state.

Tests must cover:

- the literal successful `PR_GET_SECUREBITS` result for `0x0` and `0x4` through
  an injected or monkeypatched fixed native boundary—never by changing this
  process's securebits;
- `prctl` returning `-1`, malformed, negative or out-of-range output;
- missing and malformed `securebits` capture;
- every E1…E8 expected securebits value;
- one mismatch for each identity field category, including UID/GID, groups,
  each capability mask, `NoNewPrivs` and securebits;
- a mismatch making the case `inconclusive` and preventing its dependent
  operation from being interpreted or run; and
- structural tests proving no other module can import `ctypes` or perform a
  native call.

Do not mutate the current test process's credentials, capabilities or
securebits. No test may require root.

## Preserve the R11 security boundary

Do not broaden:

- the interpreter path or exact `-I -S` prefix;
- the closed case-program verbs, arities, modes or path grammar;
- `PERMITTED_EXECUTABLES`;
- the delegated `capsh` and `systemd-run` tail validation;
- the four late-bound names or substitution sites;
- the symlink target or cleanup primitive;
- target-root validation;
- materialization destinations or bytes;
- process/materializer arming rules; or
- the authority required to establish the interpreter digest and later execute
  the harness.

Do not supply the real interpreter digest, inspect `oracle-test`, or convert the
executor's current digest refusal into a warning. The shipped plan may remain
structurally executable but operationally blocked on the unconfirmed reviewed
target fact.

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
   database cases explicitly deselected as R11;
4. the complete bot suite with those same cases deselected;
5. the complete web suite, reporting the expected skip count;
6. Foundry's Node suite;
7. `compileall` for changed Python under both interpreters; and
8. `git diff --check`.

The dry run must remain inert and report zero unresolved conflicts. Do not run a
destructive or privileged case to improve a test total.

## Required R12 handback and stop

Add a new R12 section to
`docs/review/phase-5-0-evidence-harness-implementation-handback.md` and update
`docs/review/Handover information` to point to it. State:

- how P-05 expectations are constructed independently and enforced before
  satisfaction;
- the complete mismatch/refusal matrix and tests;
- how final securebits are read and semantically compared for E1…E8;
- the exact scope of the `ctypes` exception and its mechanical guard;
- what changed in the generated artifacts and their new digest;
- exact verification results, skips and deselections;
- every privileged or destructive check not run;
- confirmation that no host inspection or mutation occurred; and
- every judgement call, residual or newly discovered dependency.

Then stop for Codex's independent R12 pre-execution review. Do not execute the
plan. Only a later explicit maintainer authorization may permit reading the
interpreter digest or running the disposable-server evidence harness. OD-62
remains open until the required operational evidence and independent review
exist.
