# Gemini Step 5 — reconcile evidence and prepare final handoff

Proceed only after Codex accepts Steps 3 and 4. This is primarily documentation
and verification. Do not make further production behavior changes; if a check
finds one is needed, stop and return to a new scoped implementation step.

Reconcile, without rewriting history:

- `docs/project-management/status.md`;
- `docs/review/phase-2-supervised-rehearsal-2026-08-06.md`;
- `docs/operations/phase-2-maintainer-closeout.md`;
- `docs/operations/foundry-snapshot-submission.md`;
- module comments affected by final semantics; and
- the existing Gemini walkthrough.

State the sequence accurately: initial `undefined_value` refusal; 1.0.1
projection correction; successful transport exposing advancing-clock duplicate
submissions; incomplete first 1.0.2 lifecycle implementation; Codex discovery
of same-payload overlapping races and removed tests; restored coverage;
operation-token correction; classification hardening; independent review state.

Do not mark any supervised checkbox complete. Version 1.0.2 remains uninstalled
and unrehearsed. The negative-origin observation, incomplete cleanup evidence,
inactive-folder preview, active-folder preview, Data Owner attestation, owner
recommendations, final independent gate review and Acceptance Authority decision
remain pending unless an existing signed record proves otherwise.

Run fresh verification:

```bash
(cd foundry-module && node --test tests/*.test.mjs)
for file in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do
  node --check "$file"
done
./venv/bin/python -m pytest -q tests/test_exporter_contract.py \
  tests/test_snapshot_parser.py tests/test_snapshot_roll_inputs.py
./venv/bin/python -m pytest -m "not db" -q -rs
./venv/bin/python -m compileall -q application adapters domain tools tests migrations
git diff --check
git status --short
```

Do not run database-backed tests merely to increase totals when no database
contract changed. Inspect untracked files explicitly because ordinary
`git diff` omits them. Scan the complete package for secrets, raw artifacts,
real Actor/player data, unsafe logs, contradictory retry instructions, removed
coverage and false completion claims.

The final walkthrough must contain changed files, final state and operation
tables, exact fresh results, checks not run, security review, residual risks,
untracked-file limitation, rollback (do not install; revert only this bounded
change if rejected), and the next action.

End with:

`Implementation and evidence ready for final independent review; version 1.0.2 remains uninstalled and unrehearsed; Phase 2 gate remains open.`
