# Phase 3 P3.5 Codex interim review — 2026-08-26

**Reviewer:** Codex  
**Request:** `phase-3-p3-5-codex-review-request-2026-08-26.md`  
**Baseline:** `0e3929a` plus the submitted working-tree changes  
**Disposition:** **Changes requested — one Blocking and two Important findings.**

This is the requested interim implementation and security review. It is not
EX-11, EX-12, an I-06 pass, an A-06 pass, or a Phase 3 gate disposition. The
submission correctly keeps the staging procedures listed in its §5.2 Not Run
and keeps TC-OPS-05 Failed pending deployment and re-observation.

## Findings

### B-1 — D-n moves S-15 on a false public-exposure premise (Blocking)

The proposed amendment says S-15 cannot be observed before the deployment gate
because its refusal requires `WEB_ENVIRONMENT=production`, while A-05 gates
public exposure. Those are not the same event. A production-marked candidate can
be started in an isolated pre-exposure exercise: with no public listener, or by
calling the startup/resource-check path against an explicitly guarded production-
shaped disposable database and configuration. S-02, S-05 and S-07 requiring the
accepted production identity make that exercise more controlled; they do not
make it public.

Moving the only observation of S-15 beyond A-05 therefore weakens a security
precondition rather than resolving a real circularity. It also leaves operational
contract §7 internally inconsistent: item 9 still requires S-01 through S-15 to
be demonstrated failing, while item 10 says S-15 cannot be observed before that
gate.

**Required:** retain a pre-exposure S-15 refusal observation in A-05. Define a
guarded exercise that cannot accept public traffic and cannot touch live
production data. A deployment-gate re-observation may remain as defense in
depth, but must not replace the pre-exposure evidence. Reconcile §7 items 9 and
10 explicitly rather than relying on the later item to narrow the earlier one by
implication.

### I-1 — N-7 redaction fails open if Uvicorn's access-record shape changes (Important)

The current filter redacts only a tuple with a string request target at index 2.
Every other shape is deliberately passed through unchanged, including a record
that may contain a query string. The tests enshrine that behavior. Consequently,
an Uvicorn upgrade or logging-configuration change can restore credential
disclosure while all shape-independent pass-through tests remain green.

For the pinned Uvicorn 0.32.1 implementation, the current path is sound: h11 and
httptools emit the same tuple shape; worker subprocesses reconfigure logging and
then import the application factory; mutation of `record.args` is compatible
with lazy and repeated formatting; and `?<redacted>` discloses no sensitive
value. The relevant test file passes 20/20. This finding is about maintaining the
security boundary when that external record contract changes.

**Required:** make an unrecognised `uvicorn.access` record fail closed with
respect to query data, or add a startup/runtime compatibility assertion that
prevents an unsupported Uvicorn/log-record contract from serving traffic. Add a
test showing the chosen fallback cannot emit a synthetic credential.

The submitted incident assessment is otherwise reasonable. The observed OAuth
codes were spent, short-lived, single-use and PKCE-bound; the verifier, session
cookie, client secret and durable recovery credentials were not observed; and
journal access was restricted. On the evidence recorded, credential rotation is
not indicated. TC-OPS-05 nevertheless remains Failed until the fix is deployed
and SP-12 is rerun.

### I-2 — The inventory contradicts itself about EX-3 (Important)

The SP-10 row first says EX-3 was executed and describes its real-database
result, then says: “The Alembic rollback rehearsal (EX-3) has never been run
either.” The request and the staging evidence both credit EX-3 and state that
TC-OPS-02's disposable half is evidenced. This contradiction makes the evidence
ledger non-authoritative at exactly the point where it assigns credit.

**Required:** correct the SP-10 row to distinguish EX-3's completed disposable
rehearsal from SP-10's unrun staging half, without changing the recorded Not Run
status of the staging exercise.

## Reviewed decisions and credits

- **D-l:** acceptable in scope. The exception is expressly limited to
  TC-PERF-01/02 and TC-OPS-03 and does not silently authorize real input for the
  other procedures. Execution remains blocked on the owed N-3 supervised
  transport and teardown procedure; that procedure must preserve the stated
  non-retention and no-payload-in-evidence controls.
- **D-m:** acceptable. One non-repeatable real apply reported as `n = 1`, plus
  two bounded-synthetic runs reported separately, is honest evidence and does
  not defeat the apply fence.
- **SP-04:** the credited observation is sufficient. Active web and worker units,
  the observed unit definitions and environment-file order, the loopback portal,
  and S-11's role refusal together substantiate the differing process roles.
- **TC-UI-01/02:** the one-browser observation satisfies the literal responsive
  and 200% reflow rows. It does not close the broader SP-23 accessibility work or
  R-23; the package records that distinction correctly.
- **N-8:** the five added citations resolve to behavioral tests. In particular,
  TC-AUTH-17's upgrade/downgrade objects and branched-chain refusal are exercised
  in the cited migration module even though its filename does not carry the
  contract ID.

## Verification

- `python -m pytest -q tests/web/test_n7_access_log_redaction.py` — **20 passed**.
- `git diff --check` — **passed** for tracked changes.
- Read-only source tracing covered Uvicorn 0.32.1 configuration/load ordering,
  subprocess logging setup, both HTTP protocol access log calls, the production
  configuration checks, S-15, and the cited migration tests.

No final gate pass is granted by this review. B-1 must be resolved before the
amended evidence package can be accepted; I-1 and I-2 must also be corrected or
explicitly dispositioned under the repository's review rules.
