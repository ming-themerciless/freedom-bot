# Independent review — LAB-V6-P3 secrets-guard remediation r1 — 2026-09-19

## Disposition

Accepted with no Blocking or Important finding. Peter Duscha accepted the
independent review on 2026-09-19, recorded his in-session instruction as the
authorization for the remediation, and closed LAB-V6-P3.

The remediation admits only a single-quoted `rsync --exclude` value that starts
a word outside quotes in one plain `rsync` invocation. Substitution, chaining,
redirection, comments, alternate filter-file options, quote-shifting constructs
and secret source or destination operands remain visible to the guard and are
refused.

## Evidence reproduced

- `python3 .claude/hooks/test_guards.py`: 41 cases passed; 27 required refusal
  and 14 required allowance.
- `python3 -m py_compile .claude/hooks/guard-secrets.py
  .claude/hooks/test_guards.py`: exit 0.
- Both complete `rsync` command blocks were extracted from
  `docs/operations/disposable-test-server.md` and submitted to the guard as
  JSON without execution: both exited 0.
- Scoped `git diff --check`: exit 0.

The committed allow cases abbreviate the full runbook commands rather than
pinning both verbatim. That is a non-blocking test-maintainability observation;
the complete commands were independently verified in this review.

## Residual limitation

The name-based guard's pre-existing inability to recognize aliases such as
`.en?` or a broad directory copy containing a secret was not introduced by
this remediation. Peter subsequently recorded it separately as
**LAB-SECRETS-1, Open, Low**; it does not reopen LAB-V6-P3, invalidate R4 or
block Package 5.0.

## Unchanged boundaries

This acceptance authorizes no `oracle-test` action and decides neither V6
closure nor acceptance of the earlier `--exclude-from` synchronization
deviation. V7, I3, V8, V10, database access, participant execution,
generated-vector execution, the evidence harness and `--execute` remain
unauthorized. `plan.is_executable` remains false, LAB-V6-P2 remains deferred,
and Package 5.0 remains not ready.
