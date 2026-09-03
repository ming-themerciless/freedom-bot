# Package 5.0 read-only operational-evidence preflight

Date: 2026-09-02

Performed by: Codex, Security Reviewer and Independent Reviewer

Outcome: **Read-only discovery complete; privileged evidence still required**

## Authority and scope

This preflight used only non-elevated, non-mutating commands. It did not invoke
`sudo`, read credential contents, create an account/group/file/database object,
change PostgreSQL or systemd configuration, alter a filesystem attribute,
contact Google/Discord/Foundry, or mutate any service or external state.

## Results

| Surface | Command class | Result | Disposition |
|---|---|---|---|
| Session identity | `id`, `umask`, `capsh --print` | `foundry` uid/gid 1000; supplementary `nogroup`; umask `0002`; permitted/effective/ambient/bounding capability sets empty; `no-new-privs=1` | This session cannot construct the privileged E1-E8 evidence identities. A separately authorized privileged disposable harness is required |
| C-1 sudoers discovery | `ls -ld`, non-elevated directory listing | `/etc/sudoers.d` is `0750`; listing returned `Permission denied` | Expected denial confirmed; C-1 remains incomplete pending an explicitly authorized privileged read |
| PostgreSQL identity | read-only SQL | Connected to `freedom_test` as `foundry`; PostgreSQL 16.15 | Disposable database is reachable; this does not confirm the Package 5.0 roles/schema |
| HBA/identity-map discovery | `SHOW` and direct file reads | `SHOW hba_file` denied because `foundry` lacks `pg_read_all_settings`; `/etc/postgresql/16/main/pg_hba.conf` and `pg_ident.conf` are `0640` and unreadable | Pre-change content inspection remains pending privileged read-only authorization |
| Required tools | `command -v`, version output | `/usr/bin/chattr`, `/usr/bin/lsattr`, `/usr/sbin/capsh`; systemd 255 | Tool presence confirmed; behavior and required privileges are not confirmed |
| Filesystems | `findmnt` | Repository path is ext4 and writable through the workspace view; `/var/lib` resolves to ext4 but is read-only in this session | No append-only conclusion is possible; C-3 needs a privileged disposable target with representative mount behavior |
| Proposed identities | `getent` | `freedomcoord`, `freedomsheet`, `fbprobe` and `freedomjournal` absent | Expected pre-implementation state; C-4 cannot yet run |
| Existing identities | `getent`, `id` | `discordbot`, `freedomweb`, `foundry` exist; `freedomweb` is supplementary member of `discordbot` | Confirms the pre-existing shared-group concern; no membership changed |
| Proposed paths | `ls -ld` | Journal hierarchy, coordinator path and bare object store absent; `/etc/freedom-blades` exists but contents were not read | Expected pre-implementation state; no provenance/journal claim can be made |
| Service hardening | read-only `systemctl show` | Bot: all four approved hardening properties off; web and worker: `NoNewPrivileges=yes`, `PrivateTmp=yes`, `ProtectSystem=strict`, `ProtectHome=yes` | Confirms OD-65's bot-hardening work remains implementation/deployment work; no unit was changed or restarted |
| Repository path | `stat`, `namei`, group lookup | Workspace path is setgid and group-writable in this environment; `freedomweb` shares the `discordbot` group | Confirms the condition OD-65 B defers; approved deployment must not read executable inputs from this worktree |

## Findings

1. **C-1 remains incomplete**, now with a fresh non-elevated denial.
2. **Pre-change HBA/identity-map inspection remains incomplete** for the same
   access-control reason.
3. **A-5.0-4 and A-5.0-5 remain unconfirmed.** The current session cannot run
   their evidence because it has no capabilities and a read-only `/var/lib`
   view.
4. The operational runbook contains an assumption-label defect: its P5.0-R5
   resolution path describes A-5.0-3 and A-5.0-4 differently from the canonical
   RAID register. The RAID definitions govern and the runbook must be corrected
   before execution.
5. The runbook also exposes a gate circularity: it requires implementation-only
   evidence to close a finding that blocks implementation. The separate bounded
   evidence-harness authorization draft is the proposed change-controlled
   resolution.

No Package 5.0 finding or assumption closes on this preflight.
