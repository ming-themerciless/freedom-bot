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
#      file, leaving the Discord values as refusable placeholders; and
#   5. installs the two systemd units, stopped.
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
step "systemd units"
# --------------------------------------------------------------------------
# `FORCE_UNITS=1 sudo -E bash …` reinstalls the unit files from the templates.
# Everything else in this script stays idempotent; only these are regenerated,
# and only when asked, because a hand-edited unit should not vanish silently.
install_unit() {
    local template="$1" target="$2" extra_env="$3"
    if [ -f "/etc/systemd/system/${target}" ] && [ "${FORCE_UNITS:-0}" != "1" ]; then
        skip "$target (FORCE_UNITS=1 to regenerate)"; return
    fi
    sed -e "s|__REPOSITORY_ROOT__|${REPO_ROOT}|g" \
        -e "s|__ENVIRONMENT_FILE__|${ENV_FILE}|g" \
        -e "s|__SERVICE_USER__|${SERVICE_USER}|g" \
        -e "s|__SERVICE_GROUP__|${SERVICE_GROUP}|g" \
        -e "s|__KILL_SWITCH_DIR__|${KILL_SWITCH_DIR}|g" \
        -e "s|__ARTIFACT_ROOT__|${ARTIFACT_ROOT}|g" \
        -e "s|__PORT__|${PORT}|g" \
        "$template" > "/etc/systemd/system/${target}"
    # An `if` rather than `[ … ] && …`: under `set -e` a false test at the head of
    # an && list makes the list itself fail, and this script must not exit
    # because a unit legitimately has no extra environment line.
    if [ -n "$extra_env" ]; then
        printf '\n[Service]\nEnvironment=%s\n' "$extra_env" \
            >> "/etc/systemd/system/${target}"
    fi
    chmod 644 "/etc/systemd/system/${target}"
    say "installed $target"
}
install_unit "$REPO_ROOT/infra/systemd/freedom-web.service.tmpl"    freedom-web.service    ""
# S-11 refuses each process the other's value, so the worker unit carries the
# single line that distinguishes them rather than a second environment file.
install_unit "$REPO_ROOT/infra/systemd/freedom-worker.service.tmpl" freedom-worker.service "WORKER_ENABLED=true"
systemctl daemon-reload
say "reloaded the systemd unit files. Neither service is enabled or started."

# --------------------------------------------------------------------------
step "Done"
# --------------------------------------------------------------------------
cat <<SUMMARY

  Created or confirmed:
    service account   ${SERVICE_USER}
    database          ${DB_NAME} (owner ${DB_OWNER}, runtime role ${DB_RUNTIME_ROLE})
    directories       ${KILL_SWITCH_DIR}, ${ARTIFACT_ROOT}
    environment file  ${ENV_FILE}
    units             freedom-web.service, freedom-worker.service (both stopped)

  Nothing is running and nothing is publicly reachable. Caddy was not touched.

  Next: the database schema and the restricted grants, which Claude can do
  without root. Then the Discord values, then the passkeys, then the switch-over.

SUMMARY
