# Claude prompt — bootstrap Claude Code and Gemini CLI on `oracle-test`

Work ID: `C-P5.0-ORACLE-AGENT-CLIENT-BOOTSTRAP-20261005-01`

Date: 2026-10-05

## Authority and purpose

Peter Duscha explicitly authorizes this one-time bootstrap assignment to install
both Claude Code and Gemini CLI on `oracle-test`, using `ubuntu`'s root access
where required. The purpose is only to make both interactive clients available
for a later, separately authorized H-0 run.

This is a narrow exception to the current no-install and no-production-host-
controller restrictions. For this bootstrap only, the Claude Code process may
run on the current workspace host and control `oracle-test` over SSH. The
workspace host must not supply repository bytes, package payloads, credentials,
configuration, or executable content to `oracle-test`; package bytes must be
retrieved by `oracle-test` directly from the official npm registry.

This authority does **not** authorize H-0, reuse of work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0`, repository retrieval or checkout, H-1/H-2,
RP-11 activation, tests, database or service operations, authentication to
either model provider, credential creation or transfer, or any later slice.

## Fixed target and installation contract

- Target host: `oracle-test`
- Target account: `ubuntu`
- Node.js requirement: existing Node.js 20 or later; do not replace or upgrade
  Node.js during this assignment
- Dedicated prefix: `/opt/freedom-blades/agent-tools`
- Required clients:
  - npm package `@anthropic-ai/claude-code`, stable/latest release
  - npm package `@google/gemini-cli`, stable/latest release
- Required command paths:
  - `/usr/local/bin/claude`
  - `/usr/local/bin/gemini`
- Evidence directory:
  `/var/tmp/p5-agent-client-bootstrap-20261005-01-evidence`

Do not substitute a different target, prefix, command path, package, release
channel, work ID, or evidence directory.

## Safety boundaries

1. Start with read-only checks. Verify the remote effective account is
   `ubuntu` and `uname -n` is exactly `oracle-test`. Otherwise `HARD STOP`.
2. Do not read or print environment dumps, SSH material, API keys, OAuth tokens,
   model-provider credentials, shell histories, or unrelated home-directory
   content. Do not run either client's interactive mode or login flow.
3. Do not inspect, fetch, modify, clean, or check out
   `/opt/freedom-blades/platform`. Do not transfer repository files from the
   workspace host.
4. Do not install or update OS packages. Do not run `apt`, `snap`, `curl | sh`,
   `npm update`, or an unpinned preview/nightly package release.
5. Do not use `sudo npm install`. Anthropic's official installation guidance
   warns against it. Use root only to create the dedicated prefix, establish
   safe ownership and modes, and create the two `/usr/local/bin` links after
   validating their targets. Run npm package resolution and installation as
   `ubuntu` into the dedicated prefix.
6. Do not overwrite or duplicate an existing client, command, symlink, prefix,
   or evidence path. If either client is already discoverable, or any fixed
   target already exists, stop before mutation and report its path, resolved
   target, version, ownership, mode, and package-manager provenance that can be
   established without reading credentials or unrelated home content. Do not
   repair, update, relocate, delete, or replace it.
7. Do not broaden permissions. The prefix must not be group- or world-writable
   when complete. No daemon, service, scheduled job, shell startup file, or
   global environment file may be added or changed.
8. No cleanup or retry after a terminal failure. Preserve any evidence and
   report every object created before the failure.

## Procedure

### A. Preconditions

From the current workspace host, connect only to `oracle-test`. On that host:

1. Record `id -un`, `id`, and `uname -n`.
2. Record `node --version`, `npm --version`, `command -v node`, and
   `command -v npm`. `node` must be version 20 or later.
3. Before any mutation, run `command -v claude` and `command -v gemini` as
   `ubuntu`. For each discovered command, record `--version`, non-following and
   resolved path metadata, and whether the owning package is visible through
   npm's system-global package inventory. Inspect only the discovered command
   and its package-manager metadata; do not search home directories. Discovery
   of either existing client is a `HARD STOP` for this installation assignment
   so the maintainer can decide whether it should be retained.
4. Use non-following path metadata checks to establish that the dedicated
   prefix, evidence directory, and both required command paths do not exist.
5. Record the npm registry configuration without displaying authentication
   material. If npm would use a registry other than the official public npm
   registry, or requires authentication, `HARD STOP`.

### B. Evidence setup

Create the evidence directory once with mode `0700`, owned by `ubuntu`. Record
the work ID, UTC start time, target identity, every remote command in execution
order, exit status, and raw stdout/stderr. Never record credentials or a full
environment.

### C. Resolve and install

1. As `ubuntu`, query the official npm registry for the exact versions behind
   the stable/latest tags of both required packages. Record the resolved exact
   versions and registry responses in evidence.
2. As root, create `/opt/freedom-blades/agent-tools` with ownership
   `ubuntu:ubuntu` and mode `0755`. Record its metadata.
3. As `ubuntu`, install both packages at the resolved exact versions into that
   prefix using npm's explicit `--prefix` and global-install options. Do not
   execute package-provided interactive clients during installation.
4. Validate that the resulting `claude` and `gemini` files resolve within the
   dedicated prefix, are ordinary safe executable files or symlinks whose
   complete target chains remain within that prefix, and are not group- or
   world-writable.
5. As root, create `/usr/local/bin/claude` and `/usr/local/bin/gemini` as
   symlinks to those validated commands. Do not overwrite anything.
6. Remove write permission for group and other throughout the installed prefix.
   Do not change ownership to root; future client self-update is outside this
   assignment and remains unauthorized.

### D. Verification

As `ubuntu`, without starting an interactive session or login flow:

1. Record `command -v claude` and `command -v gemini`; each must return its
   fixed `/usr/local/bin` path.
2. Record `claude --version` and `gemini --version`, including exit statuses.
3. Record non-following and resolved metadata for the command links, their
   complete target chains, the prefix, and installed package roots.
4. Record `npm list --global --depth=0 --prefix
   /opt/freedom-blades/agent-tools` and verify the two exact resolved versions.
5. Confirm no authentication was attempted and no client credential or client
   project configuration was created by this assignment. Do not inspect secret
   content to prove absence.

### E. Manifest

Finish the evidence directory with UTC end time, a sorted inventory, SHA-256
and byte length for every evidence file, and an aggregate manifest digest.

## Terminal states and handback

### `BOOTSTRAP PASS`

Use only when both clients are installed and every verification succeeds.
Return:

- exact package versions;
- fixed command paths and resolved targets;
- Node.js and npm versions;
- prefix ownership and modes;
- every command and exit status;
- evidence directory, aggregate SHA-256, and byte length;
- confirmation that authentication was not attempted and no credentials were
  transferred or created;
- confirmation that the repository and all services/databases were untouched;
- deviations, warnings, and checks not run; and
- the statement: `Client bootstrap is complete; H-0 remains unauthorized and
  requires a fresh work ID, evidence path, and assignment.`

### `HARD STOP`

Stop at the first identity, precondition, registry, permission, installation,
validation, or evidence failure. Do not retry, repair, overwrite, authenticate,
or clean up. Return the failed step, exact error, repository/evidence/install
objects changed, retained evidence digest if available, and the smallest
decision needed.

## Invocation

Give this entire prompt to Claude Code. Claude must proceed to exactly one
terminal state without beginning H-0 or any later work.
