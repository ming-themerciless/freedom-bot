# R14 independent pre-execution review — 2026-09-09

Disposition: **changes requested**. This reviews the current R13.2 evidence
harness handback, not a fresh approval of the entire platform. No execution
authority or package readiness is granted.

Reviewed manifest (identification only, **not approval**):
`8875b165b32f5a0929770380571c15ae4a102cd80f4ebb8979a17c7698690cb4`.
The tree has 30 covered sources, 127 command steps, 46 cleanup steps and six
unresolved required cases. Generated manifest bytes and rendered plan match the
checked-in artifacts exactly.

## EH-R14-1 — Blocking: connection failure still grants destructive ownership

`tools/phase_5_0_evidence/concrete_plan.py:1157` makes `R-B-DB` accept psql
exit 2 and establish ownership of `fb_evidence_p5_0`. The successful connection
to `postgres` in `R-B-PG` does not establish that another database is absent.
An existing evidence database with connections disabled can fail this probe
while the control connection succeeds.

PostgreSQL documents exit 2 as a connection failure, not an absence assertion;
`pg_database.datallowconn = false` prevents connections to an existing database.
See [psql exit status](https://www.postgresql.org/docs/18/app-psql.html)
and [pg_database](https://www.postgresql.org/docs/18/catalog-pg-database.html).

The later `CREATE DATABASE` (`concrete_plan.py:2989`) fails because the database
exists. It has no pre-existing-object status classification. The executor has
already recorded the attempted mutation and trusts the incorrect baseline, so
cleanup issues `DROP DATABASE IF EXISTS fb_evidence_p5_0` from `postgres`.
The run can therefore delete the very database whose existence it failed to
observe. EH-R13-1 is **not closed**.

### Independently reproduced with fakes only

Used the submitted `test_r13_remediation` helpers and real generated plan,
with their standard synthetic reviewed facts and unresolved items removed only
in the in-memory test plan. No real boundary or database was used.

1. Seed `FakeHost.objects` with `database:fb_evidence_p5_0`.
2. Override `R-B-DB` with `CommandResult(exit_status=2, timed_out=False)`.
3. Override the database creation step with exit 3, representing failed
   creation of an already existing database.
4. Run the injected executor and inspect cleanup and the fake object set.

Actual output:

```text
creation B6-03 stopped_at B6-03
baseline_satisfied True
database_survives False
drop_requested CL-08: DROP DATABASE IF EXISTS fb_evidence_p5_0
```

The existing fake normally equates connection failure with absence, so its
pre-existing-object tests do not cover this state.

Use a successful, bounded catalog observation to prove absence, independently
of whether the candidate database permits connections. Connection or query
errors must establish no ownership and stop before mutations. Audit the same
assumption in `R-B-ROLE` (generic statement failure) and `R-B-ROOT` (generic
stat failure); neither generic failure code uniquely identifies absence.
If the reviewed grammar cannot express a trustworthy observation, declare an
unresolved blocker rather than relaxing the grammar or accepting failure as
absence. Preserve unknown-launch cleanup for objects genuinely proved absent.

## Other R13 findings

- EH-R13-2: the new cleanup dependencies retain recovery captures and their
  parents when applicable restoration/reload/verification fails; no additional
  defect identified in that correction during this pass.
- EH-R13-3: observation-bearing steps now require semantic contracts; the
  previously reported empty-capability and unexpected-membership cases are
  covered. This does not repair the exit-status-only ownership issue above.
- EH-R13-4: missing capability operations and Band 7 coverage are now explicit
  unresolved items; the submitted plan refuses execution. This corrects the
  false completeness claim, but does not deliver the missing experiments.
- EH-R13-5: CLI persistence reporting now distinguishes eligibility and an
  actually written run record. The run record is explicitly not the completed
  classified evidence artifact; that remains dependent on missing coverage.

## Verification and limits

Commands run locally with `TEST_DATABASE_URL` explicitly unset:

```text
/opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence/test_no_execution.py
181 passed
/opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence
1211 passed
git diff --check
passed
```

The interpreter is an explicitly labeled local fallback, not the documented
oracle-test runtime. The two in-memory checks confirmed exact manifest and
render equality. The independent reproduction above passed through injected
fakes only and is not operational evidence.

No SSH, target inspection, generated vector execution, armed real boundary,
database operation or backup/restore drill was performed. Full database/bot/web
integration suites were not run under the current pre-execution restriction;
their earlier totals are not evidence for this review. Formatter, linter and
type checker are not configured. Production files were not changed.

Package 5.0 remains **not ready**, P5.0-R5 Blocking and OD-62 Open. C-6/C-7
and the twelve unconfirmed target facts remain unresolved. Migration 0014,
deployment, cutover and Package 5.1+ remain unauthorized.
