"""The **execution tier** of the Package 5.0 evidence harness.

Everything in `tools/phase_5_0_evidence/*.py` plans and classifies and cannot
execute: no module there imports `subprocess`, a shell, a socket, an HTTP client
or a database driver, and it opens no file at all.
`tests/phase_5_0_evidence/test_no_execution.py` asserts that by reading the
source of every one of them.

This subpackage is the one place that changes, and it is a subpackage rather than
four more modules beside the planner precisely so the boundary is a directory a
reviewer can see rather than a convention they have to check. The same suite
enumerates **both** tiers — `test_no_execution.py` partitions
`tools/phase_5_0_evidence/**/*.py` into the planning tier and this one and fails
on a file in neither — so putting an executing module here is a declaration, not
an escape from the scan.

## What this tier may do, and the guards on each

| Module | May | Guarded by |
|---|---|---|
| `boundary` | start a process | `shell=False` always; argv from a validated `CommandStep`; a fixed environment; a bounded timeout; raw output never leaves the module |
| `materializer` | write the two reviewed configuration files | a closed two-file table, four independent destination checks, `O_TRUNC` without `O_CREAT`, `O_NOFOLLOW` |
| `case_program` | perform one reviewed syscall inside the disposable root, and make one native `prctl(PR_GET_SECUREBITS)` call | a closed verb table, every path strictly inside the root, the isolation flags checked from `sys.flags`, no import outside a fixed standard-library set, and — for the one `ctypes` use this repository permits anywhere — the already-loaded C runtime, the literal `prctl` symbol, fixed `argtypes`/`restype`, the literal operation with zero remaining arguments, an errno read on `-1` and a range check before the value can be emitted |
| `executor` | drive a reviewed plan | the approved target, the reviewer's digest, the confirmation token, per-step revalidation, and cleanup after the first reached mutation |
| `cli` | read source files and write artifacts | reads only `review_manifest.COVERED_SOURCES`; a default invocation is a dry run |

## What no module here may do

Compose a shell string, call `os.system`, `eval`, `exec` or a shell binary,
resolve an executable through `PATH`, run a command the plan did not generate,
run at all without `--execute`, the exact confirmation token and a matching
reviewed digest, or serialize raw output. Each of those is a test.

**`ctypes`, dynamic import, `getattr` symbol lookup and an arbitrary native call
remain forbidden in every module of both tiers but one.** `case_program` may make
the single `prctl(PR_GET_SECUREBITS)` call §2.13.5c's assertion contract
requires, in one function, with the literal library, symbol, operation and
argument shape asserted mechanically against its syntax tree. No other module may
import `ctypes` at all, and there is no reusable arbitrary-FFI helper for one to
call.

## Status

**Nothing here has been executed.** The first privileged execution remains
prohibited until Codex approves the submitted concrete plan and this executor,
and until a maintainer authorizes the run. The submitted plan no longer carries
an unresolved conflict — R11 resolved the last of them — and that changes nothing
about the prohibition: the executor still refuses without the exact confirmation
token and the reviewer's digest, and it additionally refuses while either of the
two interpreter reviewed target facts — the expected SHA-256 and the expected
resolved path — is unsupplied.
"""
from __future__ import annotations

__all__: list[str] = []
