# Phase 2 gate — independent re-review of C-19, 2026-08-11

Reviewer: Codex, as Independent Reviewer
Requested by: Peter Duscha, Acceptance Authority
Implementer of everything reviewed: Claude
Repository state reviewed: branch `docs/platform-plan`, the **uncommitted
fifth-remediation working tree** on top of commit `3ff8c5a`

Preserved from [`Handover information`](Handover%20information), which is the
working exchange channel and not a record. Both findings below are remediated by
change-log **C-20** and the sixth remediation in
[`phase-2-b-1-settlement-remediation.md`](phase-2-b-1-settlement-remediation.md);
that remediation **carries no independent review** and returns with the package.

---


**Recommendation: keep B-1 and the Phase 2 gate Blocking.** The fourth-remediation
mechanism is materially stronger and the shared proxy test now establishes its
claimed control, but the fifth-remediation working tree introduces two operational
gaps in the procedure that is supposed to establish and recover from settlement.

### Finding 1 — Blocking: S-I.3d still cannot establish its stated negative

At `docs/operations/foundry-snapshot-submission.md:1456-1475`, S-I.3d claims to
establish that no supervisor outside systemd owns either process. Its commands do
not establish that condition. In particular, `ls -la /etc/cron.d/` lists names but
does not read the jobs, `/etc/crontab` and the other users' crontabs are not read,
and container listings do not inspect restart policies or entrypoints. The same
class of gap remains for unlisted supervisors/start mechanisms. Nevertheless the
procedure says a readable, non-positive result establishes S-I.3 and permits a
miss to authorize a fresh export.

This is the same kind of overclaim the remediation correctly identifies for timer
names at lines 1432-1435: a name or listing does not say what the invoked job does.
A scheduled or supervised restart after the checks but before the outcome is
recorded can restore the old route and allow an accepted request to commit after a
miss is declared. The new documentation test only asserts that command strings and
the prose claim exist; it does not make the commands sufficient.

Required correction: replace the attempted open-ended proof with a bounded,
host-specific inventory whose complete sources and contents are actually read and
recorded, or make an inability to enumerate every configured start mechanism an
explicit Unsettled result. At minimum, read system cron configuration and job
contents, inspect relevant users and container restart/command configuration, and
tie the checklist to the maintained production topology rather than a process-name
grep.

### Finding 2 — Blocking: the unresolved recovery branch assumes the host is down

The definition of **Unsettled** expressly includes cases where the endpoint is
still serving, Caddy is still running, or either was restarted
(`docs/operations/foundry-snapshot-submission.md:1640-1649`). The shared unresolved
branch then states that "the host is down now" and instructs the maintainer to
amend the Caddyfile, restart the endpoint, and `start` Caddy
(`docs/operations/foundry-snapshot-submission.md:1836-1854`). For those reachable
Unsettled states, `systemctl start caddy` is a no-op on the already-running service,
so the edited configuration need not be loaded; restarting an already-running
foreground endpoint may also fail or create competing listeners. The following
`410` check will detect some failures, but the runbook provides no safe transition
to the intended state and may disrupt or leave the original submission route live.

The same defect is reachable after the hit branch: lines 1828-1834 can reclassify
a post-restart result as Ambiguous and send it to the unresolved branch after both
services have already been brought up. Again, the branch begins from a false
precondition.

Required correction: give the unresolved branch explicit entry procedures for
services-down and services-running states. For a running state, validate the
amended configuration and deliberately reload/restart Caddy (with the documented
rollback and availability checks), while handling the foreground endpoint's actual
state idempotently. Do not say every branch "restarts" unless the branch first
establishes that each process is stopped.

### Verification performed

```text
/opt/discord-bots/venv/bin/pytest -q         -> passed (PostgreSQL tests skipped without TEST_DATABASE_URL)
(cd foundry-module && npm test)              -> 155 passed, 0 failed
git diff --check                             -> clean
```

The Python output was successful; the exact pass/skip totals were not recoverable
from the captured truncated console output, so this review does not repeat the
handoff's prior totals as newly verified. No disposable PostgreSQL URL was
configured, so database-backed enforcement was not rerun. No production service,
database, Caddy configuration, Foundry instance, or external network endpoint was
changed or exercised in this review.
