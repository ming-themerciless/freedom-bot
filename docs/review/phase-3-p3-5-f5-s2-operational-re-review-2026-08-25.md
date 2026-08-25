# F5/S-2 operational re-review after filesystem cutover

**Date:** 2026-08-25

**Reviewer:** Codex, Independent Reviewer

**Repository:** `/opt/freedom-blades/platform`

**Deployed commit:** `6ec7ebd46d90337f09d9eb26e1b6543e324d1bd2`

This review covers the operational item left open by the C1/C2 and C3/C4
re-reviews: execute the supported staging installer, confirm the effective worker
environment-file order, and observe the worker process active. It does not approve
the C2 health-contract change, close A-05, authorize public exposure or Phase 4,
or make an Acceptance Authority decision.

## Outcome

**No blocking or important finding. Codex recommends closing F5/S-2.**

The product-owned filesystem cutover executed the supported installer with
`FORCE_UNITS=1`, regenerated the active units, and recorded direct verification in
`docs/project-management/status.md` update 59. The resulting worker unit is active
and has the required effective configuration:

```text
freedom-worker.service: active
WorkingDirectory=/opt/freedom-blades/platform
ExecStart=/opt/freedom-blades/runtime/venv-web/bin/python -m tools.freedom_worker
EnvironmentFiles=/etc/freedom-blades/portal.env (ignore_errors=no)
EnvironmentFiles=/etc/freedom-blades/worker.env (ignore_errors=no)
```

The worker-specific file is therefore read after the shared portal file, so its
strictly validated `WORKER_ENABLED=true` assignment wins. This is direct process
and effective-unit evidence; `/healthz.worker_heartbeat` was not used as worker
liveness evidence.

The unprivileged review account could not read the protected worker environment
file or the complete system journal. Those are appropriate access controls, not
failed product checks. The executed cutover record supplies the privileged
installer and service verification; this review independently observed the active
process and effective systemd properties.

## Verification

```text
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/test_deployment_artifacts.py tests/test_worker_env_file.py
    34 passed in 0.17s

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  /opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/web/test_break_glass_health_reporting.py \
  tests/web/test_provider_health_probe.py
    26 passed in 1.58s

systemd-analyze verify /etc/systemd/system/freedom-worker.service
    passed (no output)

systemctl is-active freedom-worker.service
    active

systemctl show -p EnvironmentFiles -p WorkingDirectory -p ExecStart \
  freedom-worker.service
    required paths and ordering observed

git diff --check
    clean before this review record
```

The fresh production runtime at `venv-web` intentionally has no pytest installed.
The focused tests therefore used the preserved development/review environment
under the filesystem-migration rollback hold. No dependency was installed and no
service or production data was mutated during this review.

## Remaining authority-owned work

- The C2 `break_glass_credentials` health-contract addition remains proposed.
  Codex's earlier security recommendation to approve it is unchanged; the
  Acceptance Authority must record the decision.
- A-05 criterion 4 remains open until that decision and the required deployed
  observation/production-refusal evidence are recorded.
- A-05 criterion 10 remains the Security Reviewer's confirmation.
- The Phase 3 gate, public exposure and Phase 4 remain unauthorized.
