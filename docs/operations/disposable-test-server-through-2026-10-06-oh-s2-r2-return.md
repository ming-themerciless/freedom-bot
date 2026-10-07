# Disposable Linux Test Server

**Active restriction, 2026-10-06 — OH-S2 R2 returned for review; no host authority.**
OH-S2 R1 (`C-P5.0-R5-RP11-H1-OH-S2-R1-20261006-07`) is consumed. It returned at
`OH-S2 CITATIONS READY FOR REVIEW` without any host connection and awaits
independent Codex review. Its record lists host facts still to be observed
(MF-1 … MF-8); none may be collected without a separate authority.
[Citation record](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-citations.md)
· [Handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-handback.md).
Work ID `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0G-R1-20261006-06` used its single
connection and returned `H-0G PASS`. Independent Codex review accepted it and
composed R5 plus H-0G as `H-0 PASS`. No SSH connection to `oracle-test` is
currently authorized. Its evidence path
`/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence` is retained and, like the
normal workspace and every earlier retained evidence path, must not be
accessed, reused or cleaned. No retry, privilege, package operation,
installation, build, test, service/database mutation, cleanup, workspace
recreation, OH-S2, H-1/H-2, activation, rollback, commit or push is
authorized.
The [consumed OH-S2 authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r1-authority.md)
permitted repository documentation and read-only authoritative-source
research only; it granted no host access or operational action.
Independent Codex review did not accept R1 and recorded two Blocking process
findings. Peter has authorized repository-only OH-S2 R2 remediation work ID
`C-P5.0-R5-RP11-H1-OH-S2-R2-20261006-08`; its network authority is limited to
three exact public Ubuntu source packages and grants no connection to this
server. R2 is consumed: it returned at `OH-S2 R2 REMEDIATION READY FOR
REVIEW` without any host connection or retained-evidence access and awaits
independent Codex re-review. The MF-1 … MF-8 host facts still need a separate
authority. [Consumed R2 authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md)
· [Consumed R2 prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-remediation-claude-prompt.md)
· [R2 citation record](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md)
· [R2 handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-handback.md).
[Authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-authority.md)
· [Consumed prompt](../review/phase-5-0-p5-r5-rp11-h1-h0g-r1-claude-prompt.md)
· [Handback](../review/phase-5-0-p5-r5-rp11-h1-h0g-r1-handback.md).
· [Independent review and composed H-0](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-composed-h0-pass.md).

The predecessor restriction is preserved in
[`disposable-test-server-through-2026-10-04-d3-r6-acceptance.md`](disposable-test-server-through-2026-10-04-d3-r6-acceptance.md);
earlier snapshots are indexed under
[`disposable-test-server-archive/`](disposable-test-server-archive/README.md).

Agents that support skills should use the `run-suites` skill, which carries
this document's synchronization and execution procedure together with the
skip-count and serial-execution traps from `.agents/AGENTS.md`. The skill
checks the restriction banner above first and cites both documents rather
than replacing either.

The server exists so that **Codex, Claude Code, Antigravity, and maintainers have full administrative (root) access** to execute end-to-end tests, destructive PostgreSQL migration drills, dependency builds, and system-level experiments in complete isolation from the production/staging host.

---

## 1. Machine Profile

| Property | Value |
|---|---|
| **Public IPv4** | `138.2.182.39` |
| **SSH Host Alias** | `oracle-test` (and direct IP `138.2.182.39`) |
| **Kernel Nodename** | `Test` (`uname -n`); distinct from the SSH alias |
| **User** | `ubuntu` |
| **Privilege Level** | Full passwordless `sudo` (`sudo ALL=(ALL) NOPASSWD:ALL`) |
| **SSH Authentication** | Key-based via `~/.ssh/id_ed25519` from this host |
| **Operating System** | Ubuntu 26.04 LTS (x86_64) |
| **Kernel** | `7.0.0-31-generic` (future production 7.x generic-kernel baseline) |
| **Node.js** | v22 LTS (`/usr/bin/node`, npm 10) |
| **Python Virtualenv** | `/opt/freedom-blades/runtime/venv-web` (Python 3.12.14) |
| **Python Manager** | `uv` (`/usr/local/bin/uv`) |
| **Database Server** | PostgreSQL 16 (active systemd service `postgresql@16-main`, port 5432, Unix socket `/var/run/postgresql`); PostgreSQL 18 disabled via `/etc/postgresql/18/main/start.conf` (`manual`, port 5433) |
| **PostgreSQL Roles** | `ubuntu` (superuser, local peer auth), `freedom_runtime_test` (restricted role: `NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`, granted to `ubuntu`) |
| **Databases** | `freedom_test` (test lane), `freedom_dev` (development lane) |
| **Client Utilities** | `/usr/lib/postgresql/16/bin` explicitly prepended to `PATH` in test invocations (no global `/usr/local/bin` client symlinks) |
| **Repository Path** | `/opt/freedom-blades/platform` (owned by `ubuntu:ubuntu`) |

---

## 2. Access Configuration

The host configuration is established in `~/.ssh/config` on the primary development/staging server:

```ssh-config
Host oracle-test 138.2.182.39
    HostName 138.2.182.39
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking accept-new
```

Any agent running in this workspace can reach the remote environment without prompts or interactive passwords.

---

## 3. Agent Usage Instructions (Codex & Claude Code)

### 3.1 Running Administrative (Root) Commands

The `ubuntu` user has unrestricted, passwordless `sudo` rights. To run any administrative or system-level command:

```bash
ssh oracle-test "sudo <command>"
```

Examples:
- Restarting or inspecting PostgreSQL: `ssh oracle-test "sudo systemctl status postgresql"`
- Installing system packages: `ssh oracle-test "sudo apt-get install -y <package>"`
- Managing files or services: `ssh oracle-test "sudo systemctl restart <service>"`

### 3.2 Synchronizing Code to the Disposable Server

Before executing tests or scripts on the disposable server, sync the latest workspace state. Note that `--include='.env.example'` must precede `--exclude='.env*'` to ensure tracked example configuration is transferred while secrets remain excluded. Do not use broad `--delete-excluded`:

```bash
rsync -avz --delete \
  --include='.env.example' \
  --exclude='.env*' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='yt-cookies.txt' \
  --exclude='*service_account*.json' \
  --exclude='*credentials*.json' \
  --exclude='__pycache__/' \
  --exclude='*.py[cod]' \
  --exclude='.pytest_cache/' \
  /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
```

**Secrets guard (LAB-V6-P3 remediation r1, accepted 2026-09-19).** The repository secrets guard admits this command only in the documented shape: one plain `rsync` invocation whose exclusion values are **single-quoted**. It still refuses double-quoted or unquoted exclusion values, `--exclude-from`, a secret named as a source or destination, and any command that chains, substitutes, redirects or comments. Do not rewrite the command to get past a refusal; a refusal is a stop condition. [Independent review](../review/project-review-2026-09-19-lab-v6-p3-secrets-guard-remediation.md).

### 3.3 Running Test Suites Against PostgreSQL

The test database `freedom_test` is created on the authoritative PostgreSQL 16 cluster and owned by `ubuntu`. Run pytest directly using the remote Python 3.12 virtual environment with explicit PostgreSQL 16 `PATH`:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && \
  PATH='/usr/lib/postgresql/16/bin:/usr/bin:/bin' \
  TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/freedom-blades/runtime/venv-web/bin/pytest -q -rs tests/web"
```

To run a single test module:
```bash
ssh oracle-test "cd /opt/freedom-blades/platform && \
  PATH='/usr/lib/postgresql/16/bin:/usr/bin:/bin' \
  TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/freedom-blades/runtime/venv-web/bin/pytest -q tests/web/test_structural_guards.py"
```

### 3.4 Running Frontend / Node.js Tests

Node.js v22 LTS is installed and supports the Node built-in test runner:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && node --test 'foundry-module/tests/'*.test.mjs"
```

### 3.5 Updating Python Dependencies

To add or update dependencies inside the remote virtualenv using `uv`:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && \
  uv pip install --python /opt/freedom-blades/runtime/venv-web -r requirements-dev.txt -r requirements-web-dev.txt"
```

---

## 4. Resetting the Disposable Environment

If a test corrupted the database or filesystem:

1. **Re-create the PostgreSQL 16 test database:**
   ```bash
   ssh oracle-test "dropdb -U ubuntu --if-exists freedom_test && createdb -U ubuntu freedom_test"
   ```
2. **Re-sync the repository tree safely:**
   ```bash
   rsync -avz --delete \
     --include='.env.example' \
     --exclude='.env*' \
     --exclude='*.pem' \
     --exclude='*.key' \
     --exclude='yt-cookies.txt' \
     --exclude='*service_account*.json' \
     --exclude='*credentials*.json' \
     --exclude='__pycache__/' \
     --exclude='*.py[cod]' \
     --exclude='.pytest_cache/' \
     /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
   ```
