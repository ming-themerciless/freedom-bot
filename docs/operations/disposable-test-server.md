# Disposable Linux Test Server

**Restriction during I-7 implementation, 2026-10-01 — no action on this
server is authorized.** Peter Duscha authorized repository implementation and
repository-host evidence only. The I-7 prompt does not authorize SSH,
synchronization, inspection, dependency installation, build, test, verifier,
provisioning, controlled write or any other command on `oracle-test`.
[Assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md).

Historical restriction banners are preserved in [`disposable-test-server-through-2026-10-01-d2-r2-acceptance.md`](disposable-test-server-through-2026-10-01-d2-r2-acceptance.md) and indexed under [`disposable-test-server-archive/`](disposable-test-server-archive/README.md).

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
