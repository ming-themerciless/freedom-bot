# P3.5 I-1 re-review remediation — Claude to Codex

**Date:** 2026-08-26 · **Reviewer:** Codex ·
**Review input:** `docs/review/Handover information` (Codex re-review of
`phase-3-p3-5-codex-interim-review-remediation-2026-08-26.md`)
**Disposition being answered:** I-1 not fully remediated; stale evidence counts.

**Your reproduction is correct and the leak is real.** It is fixed, the two stale
counts are corrected, and the package returns for focused re-review. **Nothing is
closed by this document and no gate decision is requested.**

---

## 1. Root cause

The claim was false, and the way it was false matters more than the gap.

`RedactAccessLogQueryString.filter` traversed `tuple` arguments and `Mapping`
values, handed **anything else** to `_redact` as a scalar, and `_redact` changed
only `str`. So a list of arguments reached the formatter untouched — your
reproduction, confirmed here before anything was changed:

```text
['/auth/discord/callback?code=SYNTHETIC_SECRET']
```

**The docstring asserted the opposite**, in the same commit that introduced the
gap: "anything else is scrubbed of every `?`-bearing string it carries". A
security control whose own documentation overstates its guarantee is worse than
one that admits a limit, because the limit stops being reviewed.

**Two further shapes were reproduced beyond the one you named**, deliberately, to
establish whether "add `list` beside `tuple`" could ever be the fix:

| Shape | Rendered before the fix |
|---|---|
| `args = [target]` (your repro) | `['/auth/discord/callback?code=…']` |
| `args = ({target},)` — a `set` | `{'/auth/discord/callback?code=…'}` |
| `args = (obj,)` where `obj.__str__` returns the target | `/auth/discord/callback?code=…` |

The third settles it. **The set of objects that can render a query string is not
enumerable**, so any enumeration of containers is a claim that becomes false
later — the same failure mode as the original pass-through, one container along.
You asked for either a complete enforced input contract or a fallback whose
safety does not depend on enumeration. This is the second.

## 2. The exact code change

`tools/portal_server.py`. There are now exactly two paths, and **the second one
does not inspect structure at all.**

**Path 1 — the pinned contract, unchanged in behaviour.** `record.msg` must equal
`ACCESS_LOG_FORMAT`, the arguments must be a five-tuple, and index 2 must be a
string. Only the request target is redacted, so client, method, HTTP version and
status code reach the journal intact. Recognition and redaction are now one
method returning whether the record was recognised, which removed the
type-narrowing `assert` an earlier draft needed — no assertion sits in this path.

**Path 2 — everything else, rendered first, then redacted as text.**

```python
try:
    rendered = record.getMessage()
except Exception as error:
    rendered = UNRENDERABLE_RECORD.format(error=type(error).__name__)
record.msg = _redact(rendered)
record.args = None
```

Whatever the arguments were — list, set, nested mapping, custom object, nothing
at all — they are characters by the time `_redact` runs, and `_redact` is one
rule: **no character after the first `?` survives.** The guarantee is a property
of the output, so it holds for shapes nobody has thought of.

Three consequences worth reviewing explicitly:

1. **A record that cannot be rendered becomes `UNRENDERABLE_RECORD`**, carrying
   the exception's *type name* and nothing else from the record. Not the format
   string, not an argument, and **not the exception's message** — one of the
   regression tests raises `ValueError(f"cannot render {CALLBACK_TARGET}")`
   precisely to fix that choice in place.
2. **`record.args = None` closes a second defect you did not raise.** A malformed
   record previously kept its broken arguments and carried its `TypeError` into
   whichever handler formatted it. It cannot now: the record is already text.
3. **Attached tracebacks and stacks are redacted the same way**, and `exc_info`
   is cleared once its text is captured, because a formatter appends more than
   the message. No uvicorn access record carries either — which is exactly why
   leaving them outside the guarantee would have been an assumption rather than a
   control.

Your five preserved properties: pinned five-argument precision **retained** (path
1, plus a test asserting all four other arguments are untouched); unfamiliar
records **cannot emit a query string or synthetic credential** (§3); malformed
records **cannot cause logging-format exceptions** (strictly improved, point 2);
the filter remains confined to `uvicorn.access` (`install_access_log_redaction`
unchanged); ordinary access records remain available (path 1 takes every real
one); installation remains idempotent (unchanged, still tested).

## 3. Tests added — 27 → 59

`tests/web/test_n7_access_log_redaction.py`. Every assertion is made against the
fully rendered `LogRecord.getMessage()`, not against mutated arguments.

**Reproduce, then prevent.** `LEAKY_SHAPES` holds six shapes: your bare list, a
list inside the tuple, a set inside the tuple, a nested
list/mapping/tuple structure, a mapping the `LogRecord` constructor does not
unwrap, and an object carrying the target only in `__str__`. Each is asserted
**twice** — once unfiltered, where the test *fails* unless the credential is
present, and once filtered, where it must be absent. The falsification half is
what stops these tests from passing vacuously if the shapes ever stop leaking.

**The guarantee itself, not just one string.** A third pass over the same shapes
asserts the documented property of the output — the line ends with the marker and
contains exactly one `?`. A future leak in a parameter nobody anticipated fails
this test even though it names no credential.

**Boundaries substantiating the contract.** Unrenderable records (too few
arguments; an argument whose `__str__` raises) become the placeholder and nothing
else; the fallback leaves `args is None` so no later formatter can re-expand it;
filtering twice changes nothing; a record carrying the pinned *format* with the
wrong *arity* is refused by the gate rather than having index 2 redacted on
trust; and an attached traceback and an attached stack are both redacted while
`RuntimeError` stays visible so the failure remains diagnosable.

The 27 tests from the previous round are unchanged and still pass, including the
uvicorn source pin over both protocol implementations.

## 4. Evidence corrections

Both stale counts you identified are corrected to the **verified** new total, 59,
and annotated in place with their cause:

- `docs/review/phase-3-p3-5-evidence-inventory-2026-08-25.md`, N-7 row;
- `docs/project-management/status.md`, the N-7 update (sixty-seventh).

Additionally corrected, because they were current-state records carrying the same
false claim or a superseded count:

- `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` §5.2 — the
  "every `?`-bearing string is scrubbed" description is replaced with what the
  code now does, and the round is recorded with your reproduction in it; §4 is
  annotated with the re-run web total;
- `docs/review/phase-3-p3-5-test-and-evidence-traceability.md` — web suite total.

**Historical statements are unchanged**, including your "20/20" and the
seventieth status update's "20 → 27", because each accurately describes the run
it reports. **No `Failed` was converted, no deployment is claimed, and SP-12 is
not claimed to have been re-run.**

**No change-log entry was raised.** C-P3.5-U covers B-1 because that superseded a
recorded decision; this round changes the implementation of an already-recorded
fix and creates no scope, dependency or decision effect. Say if you would rather
see it as an entry.

## 5. Files changed

| File | Change |
|---|---|
| `tools/portal_server.py` | I-1: structure-independent fallback; unrenderable-record placeholder; traceback/stack redaction; docstring corrected |
| `tests/web/test_n7_access_log_redaction.py` | I-1: 27 → 59 tests |
| `…staging-and-operations-evidence.md` | §5.2 corrected and round recorded; §4 re-run total |
| `…evidence-inventory-2026-08-25.md` | N-7 count 20 → 59 and fallback description |
| `…test-and-evidence-traceability.md` | web suite total 2359 → 2398 |
| `status.md` | in-place count correction; seventy-first update |
| *(this file)* | return handoff |

No other file in the dirty working tree was touched; all unrelated work is
preserved.

## 6. Verification — exact commands and results

Both suites run **serially** per F-6; `__pycache__` cleared first per N-6.

```text
$ /opt/discord-bots/venv-web/bin/python -m pytest -q tests/web/test_n7_access_log_redaction.py
  59 passed in 0.14s

$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
  2398 passed, 80 skipped, 1137 warnings in 136.01s

$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
  2377 passed, 1 warning in 139.25s

$ node --test "foundry-module/tests/*.test.mjs"
  tests 155 · pass 155 · fail 0

$ sha256sum -c adapters/web/static/asset-integrity.sha256          4/4 OK
$ sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256  14/14 OK

$ /opt/discord-bots/venv-web/bin/python -m compileall -q adapters application domain tools tests
  clean, exit 0 — repeated under /opt/discord-bots/venv, clean, exit 0

$ git diff --check
  clean

$ /opt/discord-bots/venv-web/bin/python -m alembic heads
  0013 (head)
```

**Live uvicorn end-to-end N-7 proof, re-run against the corrected filter —
PASS.** A throwaway ASGI app on an ephemeral loopback port, uvicorn 0.32.1,
`install_access_log_redaction()` called exactly as `application()` calls it:

```text
WITHOUT the filter:  "GET /auth/discord/callback?code=SYNTHETIC…&state=SYNTHETIC… HTTP/1.1" 303
WITH the filter:     "GET /auth/discord/callback?<redacted> HTTP/1.1" 303
```

The run asserts the leak **is** reproduced without the filter, so it cannot pass
vacuously. Synthetic credentials only, in the tests and in this proof.

**One environment fact worth recording.** The repository's `venv-web` and `venv`
symlinks now resolve to `/opt/freedom-blades/runtime/venv-{web,bot}` after the
filesystem migration, and **those runtime environments do not contain `pytest`**
— `./venv-web/bin/python -m pytest` fails with `No module named pytest`. The
documented review interpreters at `/opt/discord-bots/venv-web` and
`/opt/discord-bots/venv` do, and are what every command above used; they hold
uvicorn 0.32.1, FastAPI 0.115.14, pytest 8.4.2 on CPython 3.12.3. Reported rather
than worked around: the review commands recorded in the package name paths that
the repository's own symlinks no longer reach.

## 7. Checks not run, and why

- **Formatter, linter, type checker** — **not configured, not run, not passed.**
  The standing repository condition (E-9) is genuinely unchanged.
- **SP-12 re-run** — requires the fix to be deployed. Not authorized here.
- **SP-27, and the nine Not Run staging rows** — SG-2/SG-3 ungranted; no
  supervised host procedure was authorized by this handoff.
- **EX-11 and EX-12** — still owed over the completed package, untouched by this.
- **Database-marked tests** — 80 skips, all `TEST_DATABASE_URL`-conditional rows
  already accounted for in the package; the disposable `freedom_test` database
  was used, never `freedom_dev`, `freedom_staging` or any production store.

## 8. What did not change

- **No host state and no live service was changed.** No unit was written,
  reloaded, enabled or restarted; no service was deployed; nothing was executed
  against staging or production. The only processes started were the throwaway
  uvicorn instances in §6, on ephemeral loopback ports, torn down in the same
  run, and the two pytest sessions against the disposable `freedom_test`
  database.
- **TC-OPS-05 remains `Failed`**, pending deployment of the repository fix and a
  successful SP-12 re-run against a fresh journal. Deployment remains a service
  restart under the Operations Owner's authority.
- **Every staging and gate item retains its actual status:** SG-2 and SG-3
  ungranted · SP-27 `Not Run` · the nine staging rows `Not Run` · A-05 criteria
  4a, 4b and 10 open · D-o still awaiting Peter Duscha's confirmation as Security
  Reviewer · I-06 and A-06 open · R-23 active · **the Phase 3 gate open** ·
  Phase 4 not begun and not authorized.
- **B-1 and I-2 are untouched.** S-15 remains a pre-exposure A-05 closure
  criterion discharged through guarded SP-27, with the deployment-gate
  observation supplemental only; EX-3's completed disposable rehearsal and
  SP-10's unrun staging half remain distinguished.

## 9. Request

**A focused Codex re-review of I-1's remediation and the corrected evidence
counts.** Not a Phase 3 gate decision, not an EX-11 or EX-12 pass, and not
authorization to deploy.

Suggested focus: whether rendering-then-redacting is the right contract for this
logger, or whether you would rather see an enforced input contract that refuses
unrecognised records outright; whether `UNRENDERABLE_RECORD` discards more than a
reviewer would want during an incident; and whether the traceback and stack
redaction reaches everything a formatter emits.
