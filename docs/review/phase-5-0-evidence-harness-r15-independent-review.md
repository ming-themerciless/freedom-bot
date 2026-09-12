# R15 independent review of R14 remediation — 2026-09-09

Disposition: **bounded remediation accepted; execution approval withheld**.
No new Blocking or Important implementation finding was identified in this
review of the R14 ownership correction. This is not a full-platform readiness
assessment or an operational safety certification.

## Finding disposition

**EH-R14-1 is addressed within the authorized remediation scope.** Database
and role ownership now require successful catalog observations with the control
present and the subject absent. A failed connection or query establishes no
ownership. The filesystem baseline no longer assigns ownership from generic
`stat` failure; its 29 path mutations are explicitly blocked under C-8.

This resolves the known unsafe ownership paths from EH-R13-1/EH-R14-1 by
correcting the database/role observations and refusing the unsupported
filesystem work. It does not establish a usable filesystem ownership mechanism
or authorize the previously declared cleanup vectors to run.

The catalog question passes from the reviewed command step through the process
boundary to the sanitizer and is included in the manifest. The observation
contract compares both answers before the executor grants ownership. Raw
catalog names are reduced to two yes/no observations rather than recorded.

## Independent verification

Reviewed manifest, identifying this tree only and **not an approved execution
digest**:

`79ed6ed615b3a2eeb74e5b07d51f76bac0e4b0d4451f636436cf1aec523e7324`

Independent in-memory regeneration exactly matched both the checked-in manifest
bytes and rendered concrete plan. The plan declares C-6, C-7 and C-8, with 29
mutations blocked by the filesystem ownership issue.

Used the generated plan with only its unresolved list cleared in memory and
synthetic reviewed target facts, injected FakeHost and fake materializer. Unlike
the suite's general runnable fixture, this check did not restore filesystem
ownership. Sanitized literal catalog listings were supplied to the executor:

| Injected observation | Result |
|---|---|
| Database catalog contains `postgres` and the evidence database, exit 0 | stops at R-B-DB; zero mutations and zero cleanup commands |
| Database catalog contains only `postgres`, exit 2 | stops at R-B-DB; zero mutations and zero cleanup commands |
| Role catalog contains `postgres` and the coordinator role, exit 0 | stops at R-B-ROLE; zero mutations and zero cleanup commands |
| Role catalog contains only `postgres`, exit 3 | stops at R-B-ROLE; zero mutations and zero cleanup commands |
| Satisfying fake baselines with unresolved list cleared | refuses B3-01 for lack of filesystem ownership |

These are synthetic executor checks, not database or target evidence.

Ran serially with `TEST_DATABASE_URL` explicitly unset:

```text
/opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence/test_no_execution.py
181 passed
/opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence
1255 passed
git diff --check
passed
```

This interpreter is an explicitly reported local fallback, not the canonical
oracle-test runtime. No SSH, target inspection, generated vector execution,
armed real boundary/materializer, database operation or destructive drill ran.
Full bot/web/database integration suites were not rerun for this bounded
review; prior handback totals are not claimed as independent verification.
Formatter, linter and type checker are not configured. No implementation file
was changed by this review.

## Remaining work

- **C-6:** required immutable-flag capability experiments remain unimplemented.
- **C-7:** Band 7 observation ingestion/classification remains incomplete.
- **C-8:** a trustworthy filesystem ownership mechanism or separately approved
  cleanup scope still requires a maintainer decision and independent review.
- The twelve required target facts remain unconfirmed.

The R14 handback's three C-8 options are proposals, not an approved or exhaustive
design. This review chooses none of them and does not approve reducing cleanup
obligations.

**Optional documentation correction:** `docs/review/Handover information:1`
still calls R13.2 current, cites its superseded digest and says all five findings
were remediated. Update the current pointer to the R14 handback and this review,
including C-8 and the continued execution restriction, while preserving history.
The dedicated R14 handback is accurate about its review status and supersedes
the earlier implementation account.

Package 5.0 remains **not ready**, P5.0-R5 **Blocking** and OD-62 **Open**.
Migration 0014, product implementation, deployment, cutover and Package 5.1+
remain unauthorized. Acceptance here closes the bounded remediation review,
not any of those gates.
