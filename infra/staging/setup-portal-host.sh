#!/usr/bin/env bash
#
# One-command host preparation for the Freedom Blades portal test environment.
# Authored 2026-08-23 by P3.5 (procedures SP-01, SP-02, SP-04).
#
#   sudo bash infra/staging/setup-portal-host.sh
#
# ## What it does
#
#   1. creates the service account the portal and worker run as;
#   2. creates the restricted PostgreSQL login role and the test database;
#   3. creates the kill-switch and artifact directories;
#   4. generates the portal's own secret keys and writes a locked environment
#      file, leaving the Discord values as refusable placeholders;
#   5. writes the worker's one-line environment file, which is the only place
#      systemd will let `WORKER_ENABLED=true` override the shared file (F5); and
#   6. installs the two systemd units, stopped, and verifies with systemd that
#      the worker reads those two files in the order that makes the override win.
#
# ## What it deliberately does NOT do
#
#   * it never touches Caddy. Switching the public address to the portal is a
#     separate, later step with its own script, because it is the one action on
#     this host with a blast radius onto the three live Foundry sites;
#   * it never starts a service. The portal refuses to start while the Discord
#     values are placeholders (`__` is a refused token), which is the intended
#     ordering: configuration first, then the operator fills in Discord;
#   * it never drops, truncates or overwrites an existing database, role or
#     environment file. Re-running it is safe: every step checks first; and
#   * it never prints a secret. The keys it generates go straight into a file
#     readable by root and the service account, and appear in no output, no log
#     line and no document.
#
# ## Guards
#
# It refuses to run against the development or disposable-test databases, and it
# refuses to run anywhere but as root on this host.

set -euo pipefail

# --------------------------------------------------------------------------
# Settings (D-c and D-d of the P3.5 plan)
# --------------------------------------------------------------------------
REPO_ROOT="/opt/discord-bots/freedom-bot"
SERVICE_USER="freedomweb"
SERVICE_GROUP="freedomweb"
DB_NAME="freedom_staging"
DB_OWNER="foundry"          # existing schema owner; distinct from the runtime role
DB_RUNTIME_ROLE="freedomweb" # matches SERVICE_USER so PostgreSQL peer auth needs no password
PORT="8001"
ENV_DIR="/etc/freedom-web"
ENV_FILE="${ENV_DIR}/portal.env"
# The worker's one-line file, listed **after** the shared one on the worker unit.
# It is the only place systemd will let `WORKER_ENABLED=true` win over the shared
# file's required `false` — see the Worker environment file step below (F5).
WORKER_ENV_FILE="${ENV_DIR}/worker.env"
KILL_SWITCH_DIR="/srv/freedom/web"
ARTIFACT_ROOT="/srv/freedom/snapshots"
# The TEST address, and it must not be the production one: S-02 refuses a
# non-production process that claims the accepted production origin (N-01),
# because a staging process on the production origin would receive production
# cookies and OAuth callbacks. One label under rpgworld.org, so the existing
# wildcard certificate covers it. Production uses freedom-blades.rpgworld.org
# with WEB_ENVIRONMENT=production.
PUBLIC_HOST="freedom-blades-test.rpgworld.org"
PUBLIC_ORIGIN="https://${PUBLIC_HOST}"
PROTECTED_DATABASES="postgres template0 template1 freedom_dev freedom_test"

say()  { printf '  %s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
skip() { printf '  (already present) %s\n' "$*"; }
die()  { printf '\nREFUSED: %s\n' "$*" >&2; exit 1; }

# --------------------------------------------------------------------------
step "Preflight"
# --------------------------------------------------------------------------
[ "$(id -u)" -eq 0 ] || die "run this with sudo."
[ -d "$REPO_ROOT" ] || die "$REPO_ROOT does not exist."
[ -x "$REPO_ROOT/venv-web/bin/python" ] || die "the portal virtualenv is missing."
command -v psql >/dev/null || die "psql is not installed."
systemctl is-active --quiet postgresql@16-main || die "PostgreSQL is not running."

for protected in $PROTECTED_DATABASES; do
    [ "$DB_NAME" = "$protected" ] && die "$DB_NAME is a protected database."
done
# The existing-worker-file validation (C3) lives in a sourceable library because a
# check nobody can execute is a check nobody can falsify; tests/test_worker_env_file.py
# runs this exact function.
WORKER_ENV_LIBRARY="${REPO_ROOT}/infra/staging/lib/worker-env-file.sh"
[ -r "$WORKER_ENV_LIBRARY" ] || die "$WORKER_ENV_LIBRARY is missing; the worker environment file could not be validated."
# shellcheck source=lib/worker-env-file.sh
. "$WORKER_ENV_LIBRARY"

say "root, repository, virtualenv and PostgreSQL all present."
say "target database: ${DB_NAME} (not a protected name)."

# --------------------------------------------------------------------------
step "Service account"
# --------------------------------------------------------------------------
if getent group "$SERVICE_GROUP" >/dev/null; then skip "group $SERVICE_GROUP"
else groupadd --system "$SERVICE_GROUP"; say "created group $SERVICE_GROUP"; fi

if getent passwd "$SERVICE_USER" >/dev/null; then skip "user $SERVICE_USER"
else
    useradd --system --gid "$SERVICE_GROUP" --no-create-home \
            --home-dir /nonexistent --shell /usr/sbin/nologin "$SERVICE_USER"
    say "created system user $SERVICE_USER (no home, no shell, no login)"
fi
# Read access to the repository, which is group-owned by discordbot.
if getent group discordbot >/dev/null; then
    usermod -a -G discordbot "$SERVICE_USER"
    say "added $SERVICE_USER to the discordbot group for repository read access."
else
    die "the discordbot group does not exist, so ${SERVICE_USER} would have no way to read ${REPO_ROOT}."
fi

# --------------------------------------------------------------------------
step "Directories"
# --------------------------------------------------------------------------
# The two directories are NOT the same shape, and getting that wrong costs a
# startup. The kill switch is written by the operator and only read by the
# service, so root owns it. The artifact store is written by the service, and
# `FilesystemArtifactStore` refuses a root it does not own (`root_not_owned`) or
# one carrying any group or other permission bit (`root_permissive`) — so it must
# be owned by the service account at mode 0700, checked at every startup.
if [ -d "$KILL_SWITCH_DIR" ]; then skip "$KILL_SWITCH_DIR"; else mkdir -p "$KILL_SWITCH_DIR"; say "created $KILL_SWITCH_DIR"; fi
chown root:"$SERVICE_GROUP" "$KILL_SWITCH_DIR"
chmod 750 "$KILL_SWITCH_DIR"
say "kill switch $KILL_SWITCH_DIR — root writes, ${SERVICE_USER} reads (0750)"

if [ -d "$ARTIFACT_ROOT" ]; then skip "$ARTIFACT_ROOT"; else mkdir -p "$ARTIFACT_ROOT"; say "created $ARTIFACT_ROOT"; fi
chown "$SERVICE_USER":"$SERVICE_GROUP" "$ARTIFACT_ROOT"
chmod 700 "$ARTIFACT_ROOT"
say "artifact store $ARTIFACT_ROOT — owned by ${SERVICE_USER}, 0700, as the store demands"

# --------------------------------------------------------------------------
step "PostgreSQL role and database"
# --------------------------------------------------------------------------
# The runtime role has the same name as the service account, so the service
# connects over the Unix socket under peer authentication and there is no
# database password anywhere — not in the environment file, not in a URL, not in
# a backup of either.
if sudo -u postgres psql -tAc "select 1 from pg_roles where rolname='${DB_RUNTIME_ROLE}'" | grep -q 1
then skip "role $DB_RUNTIME_ROLE"
else
    sudo -u postgres psql -qc "create role ${DB_RUNTIME_ROLE} login nosuperuser nocreatedb nocreaterole noinherit;"
    say "created restricted login role $DB_RUNTIME_ROLE (no superuser, no create rights)"
fi

if sudo -u postgres psql -tAc "select 1 from pg_database where datname='${DB_NAME}'" | grep -q 1
then skip "database $DB_NAME"
else
    sudo -u postgres createdb --owner="$DB_OWNER" "$DB_NAME"
    say "created database $DB_NAME owned by $DB_OWNER"
fi

# --------------------------------------------------------------------------
step "Environment file"
# --------------------------------------------------------------------------
if [ -f "$ENV_FILE" ]; then
    skip "$ENV_FILE — left exactly as it is, including its keys"
else
    mkdir -p "$ENV_DIR"; chmod 750 "$ENV_DIR"
    umask 077
    key() { openssl rand -base64 32; }
    cat > "$ENV_FILE" <<ENVEOF
# Freedom Blades portal — test environment. Generated $(date -u +%Y-%m-%dT%H:%M:%SZ).
#
# THIS FILE CONTAINS SECRETS. It is readable by root and ${SERVICE_GROUP} only.
# Never copy it, never paste its contents anywhere, never include it in a backup
# that leaves this host unencrypted.
#
# The four WEB_DISCORD_* values below are deliberately placeholders. The portal
# refuses to start while any value contains "__", so it cannot accidentally run
# half-configured. Replace them once the test Discord application exists.

WEB_ENVIRONMENT=staging
WEB_BIND_HOST=127.0.0.1
WEB_BIND_PORT=${PORT}
WEB_PUBLIC_ORIGIN=${PUBLIC_ORIGIN}
WEB_ALLOWED_HOSTS=${PUBLIC_HOST}
WEB_KILL_SWITCH_FILE=${KILL_SWITCH_DIR}/kill-switch

# Peer authentication over the Unix socket: no user, no password, no host.
WEB_DATABASE_URL=postgresql+psycopg:///${DB_NAME}
WEB_DATABASE_POOL_SIZE=5
WEB_DATABASE_MAX_OVERFLOW=5
WEB_DATABASE_TIMEOUT_SECONDS=5
WEB_DATABASE_STATEMENT_TIMEOUT_MS=10000

WEB_PROVIDER_REGISTRY=discord
WEB_DISCORD_CLIENT_ID=__FILL_IN_FROM_DISCORD_DEVELOPER_PORTAL__
WEB_DISCORD_CLIENT_SECRET=__FILL_IN_FROM_DISCORD_DEVELOPER_PORTAL__
WEB_DISCORD_GUILD_ID=__FILL_IN_TEST_SERVER_ID__
WEB_BOOTSTRAP_ADMIN_ROLE_ID=__FILL_IN_PLATFORM_ADMINISTRATOR_ROLE_ID__
WEB_DISCORD_REDIRECT_URI=${PUBLIC_ORIGIN}/auth/discord/callback
WEB_DISCORD_SCOPES=identify,guilds.members.read
WEB_DISCORD_API_TIMEOUT_SECONDS=5

WEB_COOKIE_SECURE=true
WEB_SESSION_IDLE_MINUTES=60
WEB_SESSION_ABSOLUTE_HOURS=12
WEB_EMERGENCY_SESSION_IDLE_MINUTES=15
WEB_EMERGENCY_SESSION_ABSOLUTE_MINUTES=60
WEB_MAX_SESSIONS_PER_ACCOUNT=10
WEB_OAUTH_TRANSACTION_MINUTES=10

WEB_WEBAUTHN_RP_ID=${PUBLIC_HOST}
WEB_WEBAUTHN_RP_NAME=Freedom Blades
WEB_WEBAUTHN_ALLOWED_ORIGINS=${PUBLIC_ORIGIN}
WEB_WEBAUTHN_USER_VERIFICATION=required
WEB_RECOVERY_GRANT_MINUTES=10

WEB_SECRET_KEY_CSRF=$(key)
WEB_SECRET_KEY_CURSOR=$(key)
WEB_SECRET_KEY_CLIENT_DIGEST=$(key)
WEB_TOKEN_ENCRYPTION_KEYS=1:$(key)
WEB_TOKEN_ENCRYPTION_ACTIVE_VERSION=1

WEB_MEMBERSHIP_CACHE_SECONDS=300
WEB_MEMBERSHIP_GRACE_SECONDS=900
WEB_RATE_LIMIT_WINDOW_MINUTES=10
WEB_RATE_LIMIT_OAUTH_STARTS=10
WEB_RATE_LIMIT_OAUTH_CALLBACKS=20
WEB_RATE_LIMIT_WEBAUTHN_PER_IP=5
WEB_RATE_LIMIT_WEBAUTHN_PER_ACCOUNT=10
WEB_RATE_LIMIT_WEBAUTHN_ACCOUNT_WINDOW_MINUTES=60
WEB_RATE_LIMIT_RECOVERY_PER_IP=3
WEB_RATE_LIMIT_RECOVERY_PER_GRANT=5
WEB_RATE_LIMIT_CLEANUP_MINUTES=60

WEB_MAX_REQUEST_BYTES=1048576
WEB_TRUSTED_PROXY_HOPS=1
WEB_AUDIT_PAGE_SIZE_DEFAULT=50
WEB_AUDIT_PAGE_SIZE_MAX=100
WEB_POLL_MIN_SECONDS=2

WORKER_ENABLED=false
WORKER_ARTIFACT_ROOT=${ARTIFACT_ROOT}
WORKER_CONCURRENCY=1
WORKER_LEASE_SECONDS=60
WORKER_HEARTBEAT_SECONDS=20
WORKER_MAX_ATTEMPTS=3
WORKER_ATTEMPT_TIMEOUT_SECONDS=300
WORKER_QUEUE_MAX_DEPTH=5
ENVEOF
    chown root:"$SERVICE_GROUP" "$ENV_FILE"
    chmod 640 "$ENV_FILE"
    say "wrote $ENV_FILE (root:${SERVICE_GROUP}, 0640) with freshly generated keys"
    say "no key was printed, and none is recoverable from this script's output."
fi

# --------------------------------------------------------------------------
step "Worker environment file"
# --------------------------------------------------------------------------
# **F5, and the reason this file exists at all.** `freedom-web` and
# `freedom-worker` run the same code from the same virtualenv and differ by
# `WORKER_ENABLED` alone, and S-11 refuses each process the other's value. The
# shared file above must therefore say `false`, because it is also the portal's.
#
# The obvious way to flip it for the worker — `Environment=WORKER_ENABLED=true`
# on the unit — **cannot work**. `systemd.exec(5)`: "Settings from these files
# override settings made with Environment=". The shared file is read second and
# wins, so the worker refuses itself with S-11 on every start while its unit
# reads as though it were configured correctly. That is exactly what happened on
# this host between 2026-08-23 and 2026-08-25.
#
# What does work is a second *file*, listed after the shared one on the worker
# unit, because later files override earlier ones. It holds that single line and
# nothing secret; the unit's `__WORKER_ENVIRONMENT_FILE__` placeholder is
# substituted with this path below.
if [ -e "$WORKER_ENV_FILE" ] || [ -L "$WORKER_ENV_FILE" ]; then
    # Confirmed rather than overwritten, in keeping with this script's promise
    # about the shared file — and confirmed **completely**, not just for the value
    # of WORKER_ENABLED (C3, 2026-08-25). This file is read after the shared one,
    # so anything in it overrides the portal's configuration; the only file this
    # script will adopt is one that is exactly what it would have written itself.
    # `worker_env_file_problem` is in a sourceable library because a check nobody
    # can execute is a check nobody can falsify — see tests/test_worker_env_file.py.
    problem="$(worker_env_file_problem "$WORKER_ENV_FILE" root "$SERVICE_GROUP" 640)" \
        && skip "$WORKER_ENV_FILE — left exactly as it is (verified: one line, root:${SERVICE_GROUP}, 0640)" \
        || die "$WORKER_ENV_FILE ${problem}
This script will not overwrite it. Inspect it, then either correct it to a single
line reading WORKER_ENABLED=true owned root:${SERVICE_GROUP} at mode 0640, or
remove it and re-run — this script will write it correctly."
else
    mkdir -p "$ENV_DIR"; chmod 750 "$ENV_DIR"
    printf 'WORKER_ENABLED=true\n' > "$WORKER_ENV_FILE"
    chown root:"$SERVICE_GROUP" "$WORKER_ENV_FILE"
    chmod 640 "$WORKER_ENV_FILE"
    say "wrote $WORKER_ENV_FILE (root:${SERVICE_GROUP}, 0640) — one line, no secret"
fi

# --------------------------------------------------------------------------
step "systemd units"
# --------------------------------------------------------------------------
# `FORCE_UNITS=1 sudo -E bash …` reinstalls the unit files from the templates.
# Everything else in this script stays idempotent; only these are regenerated,
# and only when asked, because a hand-edited unit should not vanish silently.
install_unit() {
    local template="$1" target="$2"
    local installed="/etc/systemd/system/${target}"
    if [ -f "$installed" ] && [ "${FORCE_UNITS:-0}" != "1" ]; then
        skip "$target (FORCE_UNITS=1 to regenerate)"; return
    fi
    # Rendered beside the target and only moved into place once it has been
    # checked: a unit carrying an unsubstituted placeholder is a unit that fails
    # at start, and installing one and then refusing would leave the host worse
    # than not running this script at all.
    local staged="${installed}.staged.$$"
    sed -e "s|__REPOSITORY_ROOT__|${REPO_ROOT}|g" \
        -e "s|__ENVIRONMENT_FILE__|${ENV_FILE}|g" \
        -e "s|__WORKER_ENVIRONMENT_FILE__|${WORKER_ENV_FILE}|g" \
        -e "s|__SERVICE_USER__|${SERVICE_USER}|g" \
        -e "s|__SERVICE_GROUP__|${SERVICE_GROUP}|g" \
        -e "s|__KILL_SWITCH_DIR__|${KILL_SWITCH_DIR}|g" \
        -e "s|__ARTIFACT_ROOT__|${ARTIFACT_ROOT}|g" \
        -e "s|__PORT__|${PORT}|g" \
        "$template" > "$staged"
    # Directives only. The templates explain themselves in `#` comments, and one
    # of those comments names `__PLACEHOLDER__` as a word — a check that could not
    # tell an explanation from a setting would be a check someone deletes.
    local unresolved
    unresolved="$(grep -v '^[[:space:]]*[#;]' "$staged" | grep -oE '__[A-Z0-9_]+__' | sort -u | tr '\n' ' ' || true)"
    if [ -n "${unresolved% }" ]; then
        rm -f "$staged"
        die "$target would have been installed with unsubstituted placeholder(s): ${unresolved}\
Add the substitution to install_unit() above; the template and this installer are one contract."
    fi
    mv "$staged" "$installed"
    chown root:root "$installed"
    chmod 644 "$installed"
    say "installed $target"
}
install_unit "$REPO_ROOT/infra/systemd/freedom-web.service.tmpl"    freedom-web.service
# The worker unit lists ${WORKER_ENV_FILE} *after* the shared file, which is the
# only arrangement systemd lets win (F5, see the step above). No `Environment=`
# override is appended here, and none may be: it would be read first and then
# overwritten by the shared file's `WORKER_ENABLED=false`.
install_unit "$REPO_ROOT/infra/systemd/freedom-worker.service.tmpl" freedom-worker.service
systemctl daemon-reload
say "reloaded the systemd unit files. Neither service is enabled or started."

# The effective configuration, asked of systemd rather than inferred from the
# file this script just wrote. `systemctl show` reports the parsed list in load
# order, so it answers the one question the unit text cannot: which file is read
# last, and therefore which `WORKER_ENABLED` the worker will actually see.
worker_files="$(systemctl show -p EnvironmentFiles --value freedom-worker.service | sed 's/ (ignore_errors=[a-z]*)//')"
shared_position="$(printf '%s\n' "$worker_files" | grep -nxF "$ENV_FILE" | cut -d: -f1 || true)"
worker_position="$(printf '%s\n' "$worker_files" | grep -nxF "$WORKER_ENV_FILE" | cut -d: -f1 || true)"
if [ -z "$shared_position" ] || [ -z "$worker_position" ] || [ "$worker_position" -le "$shared_position" ]; then
    die "freedom-worker.service does not read ${WORKER_ENV_FILE} after ${ENV_FILE}. \
systemd reports: ${worker_files:-<none>}. The worker would refuse itself with S-11 on every start."
fi
say "verified: freedom-worker reads ${ENV_FILE} then ${WORKER_ENV_FILE} — the later file wins."

# --------------------------------------------------------------------------
step "Done"
# --------------------------------------------------------------------------
cat <<SUMMARY

  Created or confirmed:
    service account   ${SERVICE_USER}
    database          ${DB_NAME} (owner ${DB_OWNER}, runtime role ${DB_RUNTIME_ROLE})
    directories       ${KILL_SWITCH_DIR}, ${ARTIFACT_ROOT}
    environment file  ${ENV_FILE}
    worker override   ${WORKER_ENV_FILE} (WORKER_ENABLED=true, read last)
    units             freedom-web.service, freedom-worker.service (both stopped)

  Nothing is running and nothing is publicly reachable. Caddy was not touched.

  Next: the database schema and the restricted grants, which Claude can do
  without root. Then the Discord values, then the passkeys, then the switch-over.

SUMMARY
