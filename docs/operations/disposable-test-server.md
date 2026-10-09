# Disposable Linux Test Server

**Active restriction, 2026-10-09 — WP-3 assignment prepared; independent review pending; repository-only; no host authority.**

**Current state:** **WP-3 ASSIGNMENT PREPARED — INDEPENDENT REVIEW PENDING.**

WP-2 is independently reviewed and accepted. A bounded repository-only WP-3
assignment has now been prepared under proposed work ID
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-20261009-20`. The exact proposed prompt is
244 lines, 12,650 bytes and SHA-256
`e09605d27daa8d25174302079a43ebccac64f69169007bad78496a8907457576`.

The proposed assignment covers exactly Q3-1, Q3-2, Q3-3, Q3-4, Q3-5, Q3-6,
Q3-7, Q3-9 and Q3-11. It requires a loader-free interface contract for DI-1
through DI-6 and the SA-2 stop-unit call, reconciled to the accepted 41 logical
call sites and supported only by already-authorized, version-bound repository
citations. It authorizes no network or host research.

The prompt is not accepted, assigned, authorized or executable. A different
independent reviewer must review its exact pinned bytes, and Peter Duscha must
separately accept the exact prompt and name an executor before WP-3 can start.

**Preserved effective boundary:** baseline v1.8, F-1 B2-F, both lifecycle acts
in, B3-OUT, effective EX-1/EX-2 and no EX-3 remain unchanged. Q6-6 and Q6-7
remain unanswered. Concrete Route 3 remains unestablished, BC-2 remains a later
WP-9 question and LIT-FULL is not selected for implementation.

**Current action:** independent review of the exact proposed WP-3 prompt. No
executor is appointed. WP-4 through WP-7 remain separately gated.

The no-host restriction is unchanged: no host or retained-evidence access,
network research, cleanup, workspace recreation, implementation,
configuration/infrastructure edit, launcher work, build, test, formatter,
package or service/database operation, OH-S4/OH-S4p or later slice, H-1/H-2,
activation, rollback, commit or push is authorized. The R5 and H-0G retained
paths remain untouched pending separately gated LC-3 through LC-5 authority.

[Proposed WP-3 prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-claude-prompt.md)
· [WP-3 assignment preparation](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-assignment-preparation.md)
· [WP-2 acceptance](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-acceptance.md)
· [Accepted WP-2 inventory](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md)
· [Archived WP-2-accepted restriction](disposable-test-server-through-2026-10-09-lit-full-wp2-acceptance.md).
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
     --exclude='*service_account*.json' \
     --exclude='*credentials*.json' \
     --exclude='__pycache__/' \
     --exclude='*.py[cod]' \
     --exclude='.pytest_cache/' \
     /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
   ```
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
     --exclude='*service_account*.json' \
     --exclude='*credentials*.json' \
     --exclude='__pycache__/' \
     --exclude='*.py[cod]' \
     --exclude='.pytest_cache/' \
     /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
   ```
