# Disposable Linux Test Server

This document defines the operational profile, access method, and execution instructions for the dedicated disposable Linux test environment.

**Current restriction, 2026-09-15 — preflight authorized but not yet released.**
Peter authorizes V6 as a read-only prerequisite survey, but the preflight
remains queued behind remediation and independent re-review of Blocking
PR-20260915-LAB-D12-1. It does not prove `linkat` viability or close I3. Until
that review accepts the remediation, SSH, synchronization and host inspection
remain out of scope. Provisioning, permission or group changes,
`systemd-tmpfiles`, database operations, generated-vector execution, real
participant invocation, real boundary/materializer use and `--execute` remain
unauthorized in every case. No item of the r6 §7 delta is provisioned, no
reservation is claimed and this host must remain untouched until the document
checkpoint closes. See
the active [handover](../review/Handover%20information) and
[Codex re-review](../review/project-review-2026-09-15-reserved-laboratory-one-shot-authority.md).

**Current state, 2026-09-14 — the mechanism is wired in the repository; this
host is still untouched.** The C-P5.0-LAB-I-R1 remediation is
[returned for independent re-review](../review/phase-5-0-reserved-laboratory-implementation-remediation-handback.md).
Reservation enforcement now has a repository-owned integration point for all
seven participants — `tools/phase_5_0_evidence/execution/participants.py` — and
the harness CLI's `--execute` branch assembles it. **Nothing here is enforced by
any of that**, for two separate reasons, and both matter:

* **the six non-harness participants are not wired to it.** The bot suite, the
  web suite, the Foundry tests, §3.2 synchronization, §3.5 dependency updates
  and §4 environment reset run exactly as they do today. Connecting them is a
  follow-up authorization, and RAID item **LAB-R6** records why it must not
  precede provisioning: an integration point refuses on an absent lock, so
  wiring it on an unprovisioned host would stop every suite; and
* **every r6 §7 item this host would need remains unapproved and
  unprovisioned** — the `freedomlab` group, `ubuntu`'s membership, the
  `systemd-tmpfiles` fragment, the laboratory and recovery directories, the
  ledger directory and the initialized `lifecycle.json`. The mechanism refuses
  on an absent lock or record rather than creating either.

**No reservation is claimed by this document.** Nothing was run, synchronized,
inspected or changed on this host, and V6, V8 and V10 remain unperformed.

**Current authorization boundary, 2026-09-14.** C-P5.0-LAB-I-R1 authorizes
repository changes and local tests with `TEST_DATABASE_URL` unset only. It does
**not** authorize SSH, synchronization, inspection, preflight, provisioning,
permission changes, database operations, generated-vector execution or execution
on this server, and it does not authorize invoking any of the seven integration
points against a real participant. Claude stops after its remediation handback
for independent Codex re-review.

**Prior state, 2026-09-13 — the mechanism exists; this host is untouched.**
The C-P5.0-LAB-I implementation is
[returned for independent review](../review/phase-5-0-reserved-laboratory-implementation-handback.md).
Reservation enforcement is now **implemented in the repository** and is still
**enforced by nothing here**: every one of the r6 §7 items this host would need
— the `freedomlab` group, `ubuntu`'s membership, the `systemd-tmpfiles`
fragment, the laboratory and recovery directories, the ledger directory and the
initialized `lifecycle.json` — remains **unapproved and unprovisioned**, and the
mechanism refuses on an absent lock or record rather than creating either. **No
reservation is claimed by this document.** Nothing was run, synchronized,
inspected or changed on this host, and V6, V8 and V10 remain unperformed.

**Current authorization boundary, 2026-09-13.** C-P5.0-LAB-I authorizes
repository implementation and local tests only. It does **not** authorize SSH,
synchronization, inspection, preflight, provisioning, permission changes,
database operations or execution on this server. Provisioning definitions may
be prepared in the repository for review but may not be applied. Claude must
stop after its implementation handback for independent Codex review.

**Prior review state, 2026-09-13.** The independent
[LAB-1 R3 re-review](../review/project-review-2026-09-13-lab1-rereview-r3.md)
accepts the local raw-byte remediation with no residual finding. This does not
authorize use of this host: reservation enforcement and the r6 provisioning
delta remain unimplemented, C-7 and EH-R16-1 remain unresolved, the twelve
target facts remain unconfirmed, and `is_executable` remains `False`. The next
action is maintainer direction on those blockers, followed only by separately
authorized implementation review, read-only preflight and execution decisions.

**Current laboratory direction and restriction, 2026-09-10.** C-P5.0-LAB-1
uses exclusive whole-host reservation, trusted administrators and scoped
adversarial cases; see the [direction and impact assessment](../review/phase-5-0-reserved-laboratory-direction.md).
During a reservation all other project work, including tests, synchronization
and dependency updates, must wait for verified release. A lock expiry or crashed
executor does not authorize takeover. Reservation enforcement is not implemented
or verified yet, and no reservation is claimed by this document.

**Maintainer design choice, 2026-09-12.** All seven participants are intended to
use the shared `ubuntu` identity; no separate identities are wanted. The
maintainer accepts the exact ten-item r6 §7 delta as the design basis. This is
not a provisioning or host-operation authorization. The choice records the
trusted-operator assumption and the disposable host's isolation rationale; it
does not make the shared UID a security boundary between participants or
confirm the target's actual entry-point identities. The current handover remains
local-only: no SSH, synchronization, preflight, permission changes, provisioning
or real execution. See the [decision and remediation note](../review/project-review-2026-09-12-lab1-disposition.md).

**Reservation contract, 2026-09-11.** The decision half is now written down:
`tools/phase_5_0_evidence/reservation.py` carries the six reservation states, the
owner/target/release record, fail-closed admission and the release and quarantine
conditions, and it enumerates the seven project entry points that must serialize
on one cooperative lock at `/run/freedom-blades/laboratory.lock` — the bot suite,
the web suite, the Foundry tests, the §3.2 synchronization, the §3.5 dependency
update, the §4 environment reset and the harness CLI. The rule for all seven is
*wait or refuse*, never proceed. **The adapter that actually takes the lock is
proposed and not built**, so no reservation is enforced by anything today and none
is claimed. The lock is advisory: it revokes no permission, and manual root access
to this host remains a trusted operational premise rather than something the lock
constrains. Holding it is not evidence the host is quiet, and releasing it is not
evidence a run ended.

**Errata, 2026-09-11.** Two statements in the paragraph above were corrected by
the [September 11 review](../review/project-review-2026-09-11.md) and the
remediation that answered it. First, the decision half now also requires
**explicit durable lifecycle evidence** to admit: a free process lock, a complete
service inventory, an elapsed deadline and an absent quarantine argument are each
refused as substitutes for a verified predecessor release, and release now
distinguishes an unobserved residue check from an observed empty one. Second, the
lock's proposed `O_CREAT|O_EXCL` adapter is **withdrawn** — ordinary participants
cannot create or unlink an entry in a root-owned directory. The replacement in
[runner contract r2](../review/phase-5-0-reserved-laboratory-runner-contract-r2.md)
§5 is a **provisioned persistent lock inode** plus a separately protected
lifecycle record, and it carries a **non-zero** provisioning and permission delta
(a `freedomlab` system group, a group membership, a `systemd-tmpfiles` fragment
and four provisioned paths). **None of that is approved or provisioned**, the
adapter is still not built, no reservation is enforced by anything today and none
is claimed by this document.

**Second erratum, 2026-09-11.** The
[September 11 re-review](../review/project-review-2026-09-11-r2.md) found four
further defects, and the paragraph above needs two corrections. First, the
decision half admitted a **contradictory** record: a release record beside a
`RUNNING` or `QUARANTINED` predecessor state was resolved in favour of reuse, and
an unrecognised disposition value fell through to admission with no refusal at
all. Both are repaired — `reservation.validate_lifecycle()` now validates the
record as a coherent whole before choosing an admitting branch, and it is the
**same** function all seven participants apply, so an ordinary participant has no
weaker rule than the executor. **`ADMITTED` is an active predecessor and refuses
reuse even when the process lock is free.** Second, the replacement design in
[runner contract r2](../review/phase-5-0-reserved-laboratory-runner-contract-r2.md)
§5 is **superseded by
[r3](../review/phase-5-0-reserved-laboratory-runner-contract-r3.md)**: r2 assigned
`O_PATH` to descriptors it then required `fsync` on, omitted the recovery
parent's durability barrier, overclaimed what a post-unlink check establishes,
and never initialized the verified-first-use record its own fresh-install path
needed. r3's provisioning and permission delta is **eight items** — the
`freedomlab` group, a group membership, a `systemd-tmpfiles` fragment, four
provisioned paths, the initial lifecycle record, and one preflight fact about the
directory barrier. **None of that is approved or provisioned**, the adapter is
still not built, no reservation is enforced by anything today and none is claimed
by this document.

**Third erratum, 2026-09-11.** The
[R3 re-review](../review/project-review-2026-09-11-r3.md) found three further
defects, and the paragraphs above need three corrections. First, the reservation
record's publication renames the record before synchronizing its containing
directory, so between those two points the record is **readable and not
durable**, and a process restart leaves a successor no way to learn that the
publication never completed. The replacement in
[runner contract r4](../review/phase-5-0-reserved-laboratory-runner-contract-r4.md)
§5.6 is that **every participant re-establishes that durability under the lock,
or refuses** — a barrier needing read permission and no write permission at all.
Second, r3's statement that a crashed test suite leaves no lifecycle record and
the next suite may proceed is **withdrawn**: all seven participants now publish
durable in-progress and completion state, an interrupted run of **any** of them
blocks every successor including the harness and the environment reset, and a
free lock or a clean wrapper exit is never evidence that a run's effects ended.
Third, a first-use or operator-recovery record carried no **approved target
identity**, so a history for this hostname admitted against a different approved
target; the binding, the first-use attester and basis, and the recovery's author
now travel from the stored bytes through a bounded versioned schema into the one
shared validator. r4's provisioning and permission delta is **ten items** — r3's
eight, plus a group-writable `runs` directory and a preflight confirmation of the
seven participants' identities. **None of that is approved or provisioned**, the
adapter is still not built, no reservation is enforced by anything today and none
is claimed by this document.

The active [Claude handover](../review/Handover%20information) permits local
remediation only. Do not run the SSH, synchronization, provisioning or test-server
commands below for that task. VM work is deferred; the general server profile
does not override the existing pre-execution review and task-specific gates.

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
