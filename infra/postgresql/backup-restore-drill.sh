#!/usr/bin/env bash
#
# Development backup and restore drill.
#
# Plan §14.3 requires restore tests, not merely backup success messages. This
# script performs the full round trip against a *disposable* database: dump,
# checksum, destroy the schema, restore, and compare the table and row
# inventory before and after.
#
# It refuses to run against staging or production. Recovering those means
# restoring a verified off-host backup under the procedure in
# docs/operations/database-development.md, never running a drill script.
#
# ---------------------------------------------------------------------------
# WHY THE CONNECTION IS VALIDATED AND NOT JUST THE NAME
# ---------------------------------------------------------------------------
# `--dbname=freedom_test` names a database, not a server. libpq fills in the
# host, port and even the database from PGHOST, PGHOSTADDR, PGPORT, PGDATABASE,
# and from a connection service file named by PGSERVICE/PGSERVICEFILE. An
# inherited value can therefore point `freedom_test` at another server, and step
# 4 below drops that server's `public` schema.
#
# A LOOPBACK ADDRESS IS NOT PROOF THAT THE SERVER IS ON THIS HOST. `ssh -L
# 5432:localhost:5432 elsewhere` binds 127.0.0.1:5432 here and delivers the
# session to PostgreSQL on another machine. That server sees the connection
# arrive from sshd over its own loopback interface, so inet_server_addr() and
# inet_client_addr() both report loopback -- exactly what a genuinely local TCP
# connection reports. A pooler or any other TCP proxy has the same shape.
#
# So this drill requires a PostgreSQL **Unix-domain socket**, which is a file on
# this host and which no TCP tunnel can present:
#   1. it refuses any inherited libpq configuration it cannot resolve;
#   2. it refuses PGHOSTADDR outright (an address is always TCP) and accepts
#      PGHOST only as an absolute socket directory -- 'localhost', '127.0.0.1'
#      and '::1' are refused;
#   3. it pins one explicit connection and exports it, so the dump, the
#      inventory, the drop and the restore all use the same validated target;
#      and
#   4. it asks the *server*, over that connection, which database it is and
#      requires both addresses to be null -- a Unix-domain socket -- before
#      anything is dumped or dropped.
#
# The residual, stated plainly: a deliberately forwarded *socket* path
# (`ssh -L /tmp/s:/remote/s`) would still answer with null addresses. That is a
# hand-built hostile configuration on the operator's own host, not the ordinary
# port-forward this gate exists to refuse, and no check inside this script can
# exclude it.
#
# ---------------------------------------------------------------------------
# THE IN-PLACE DRILL IS NOT FAILURE-ATOMIC
# ---------------------------------------------------------------------------
# Step 4 drops the schema of the same database step 5 restores into. Between
# those two steps the database is empty. If the restore fails, the disposable
# database is left empty or half-restored and needs recovery. The dump is kept,
# and the recovery command is printed on failure; see "Recovery" below and the
# ops document. A restore into a *separate* empty database would be atomic in
# this respect, and is not claimed here because it has not been tested.
#
# Usage: infra/postgresql/backup-restore-drill.sh [database] [work-directory]
#
# Exit codes:
#   0  the restore was verified
#   1  the drill ran and the restore did not match
#   2  the requested database is not disposable
#   3  the connection could not be proven safe; nothing was touched

set -euo pipefail

DATABASE="${1:-freedom_dev}"

# ---------------------------------------------------------------------------
# 0a. Only disposable databases, by name
# ---------------------------------------------------------------------------

case "${DATABASE}" in
  freedom_dev | freedom_test) ;;
  *)
    echo "Refusing to drill against '${DATABASE}': only freedom_dev and freedom_test" \
         "are disposable." >&2
    exit 2
    ;;
esac

refuse_connection() {
  echo "Refusing to drill against '${DATABASE}':" "$@" >&2
  echo "Nothing was dumped, dropped or restored." >&2
  exit 3
}

# ---------------------------------------------------------------------------
# 0b. Refuse inherited libpq configuration that cannot be resolved here
# ---------------------------------------------------------------------------
# A service file defines the target outside this repository, and PGOPTIONS can
# change how every command below behaves. Neither can be validated, so both are
# refused rather than ignored. PGDATABASE is refused because a drill that names
# its database on the command line must not also inherit one.

for variable in PGSERVICE PGSERVICEFILE PGOPTIONS PGDATABASE; do
  if [[ -n "${!variable:-}" ]]; then
    refuse_connection "${variable} is set, so the target is defined outside" \
                      "this script and cannot be verified. Unset it and re-run."
  fi
done

# ---------------------------------------------------------------------------
# 0c. The connection must be a local Unix-domain socket
# ---------------------------------------------------------------------------
# docs/operations/database-development.md: destructive workflows connect through
# the Unix-domain socket. The two accepted spellings are an absolute socket
# directory in PGHOST, and no PGHOST at all -- libpq's built-in default socket
# directory, which gate 0e then proves really was a socket.
#
# A TCP target is refused whatever its address. PGHOSTADDR is always an address,
# so it is refused outright; 'localhost', '127.0.0.1' and '::1' in PGHOST are
# refused for the same reason a forwarded port is indistinguishable from a local
# server.

if [[ -n "${PGHOSTADDR:-}" ]]; then
  refuse_connection "PGHOSTADDR='${PGHOSTADDR}' selects a TCP connection." \
                    "A TCP connection cannot be shown to reach a PostgreSQL" \
                    "server on this host: a forwarded port answers exactly as a" \
                    "local server does. Unset PGHOSTADDR and use the socket."
fi

if [[ -n "${PGHOST:-}" ]]; then
  case "${PGHOST}" in
    /*) ;;
    *) refuse_connection "PGHOST='${PGHOST}' is not an absolute Unix-domain" \
                         "socket directory. A TCP host -- including localhost," \
                         "127.0.0.1 and ::1 -- cannot be distinguished from an" \
                         "SSH local port forward or a proxy to another server," \
                         "so this drill requires the socket." ;;
  esac
fi

if [[ -n "${PGPORT:-}" ]]; then
  if [[ ! "${PGPORT}" =~ ^[0-9]+$ ]]; then
    refuse_connection "PGPORT='${PGPORT}' is not a port number."
  fi
fi

# ---------------------------------------------------------------------------
# 0d. Pin the validated connection for every command below
# ---------------------------------------------------------------------------
# Exporting the validated values (and nothing else) means the dump, the
# inventory, the drop and the restore cannot resolve differently from one
# another: they run in this environment, with PGHOST either the validated socket
# directory or absent, and every redirecting variable removed. PGPASSWORD, if
# the operator set one, is passed through untouched and is never printed or
# written to a file.

if [[ -n "${PGHOST:-}" ]]; then export PGHOST; else unset PGHOST; fi
if [[ -n "${PGPORT:-}" ]]; then export PGPORT; else unset PGPORT; fi
unset PGHOSTADDR PGSERVICE PGSERVICEFILE PGOPTIONS PGDATABASE

# ---------------------------------------------------------------------------
# 0e. Ask the server where this connection actually landed
# ---------------------------------------------------------------------------
# Everything above reasons about strings. This asks PostgreSQL itself, over the
# exact connection the destructive commands will use, and it is the last gate
# before step 4. It catches a remapped 'localhost' and an unset PGHOST whose
# built-in default turned out not to be a socket, and it is what makes the
# hostless form above safe to accept.

TARGET_REPORT="$(
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 -c "
    SELECT current_database()
        || '|' || (inet_server_addr() IS NULL AND inet_client_addr() IS NULL)::text
        || '|' || COALESCE(host(inet_server_addr()), '')
        || '|' || COALESCE(host(inet_client_addr()), '')"
)" || refuse_connection "the target could not be inspected; see the psql error above."

IFS='|' read -r CONNECTED_DATABASE UNIX_SOCKET SERVER_ADDRESS CLIENT_ADDRESS \
  <<<"${TARGET_REPORT}"

if [[ "${CONNECTED_DATABASE}" != "${DATABASE}" ]]; then
  refuse_connection "the connection landed in database '${CONNECTED_DATABASE}'."
fi

case "${CONNECTED_DATABASE}" in
  freedom_dev | freedom_test) ;;
  *) refuse_connection "'${CONNECTED_DATABASE}' is not a disposable database." ;;
esac

# A Unix-domain connection reports neither a server nor a client address. Any
# reported address means TCP, and a loopback one is NOT accepted: it is what a
# forwarded port to a remote server reports too.
# `boolean::text` renders "true"/"false", not psql's "t"/"f".

if [[ "${UNIX_SOCKET}" != "true" ]]; then
  refuse_connection "the connection is not a Unix-domain socket (server" \
                    "'${SERVER_ADDRESS}', client '${CLIENT_ADDRESS}')." \
                    "Loopback addresses are reported by a forwarded port to a" \
                    "remote server exactly as by a local one, so they cannot" \
                    "prove the server is on this host."
fi

echo "0. Target verified: database '${CONNECTED_DATABASE}', Unix-domain socket"

# ---------------------------------------------------------------------------
# The drill
# ---------------------------------------------------------------------------

WORK_DIRECTORY="${2:-$(mktemp -d)}"
mkdir -p "${WORK_DIRECTORY}"
chmod 700 "${WORK_DIRECTORY}"

DUMP="${WORK_DIRECTORY}/${DATABASE}.dump"
BEFORE="${WORK_DIRECTORY}/inventory-before.txt"
AFTER="${WORK_DIRECTORY}/inventory-after.txt"

SCHEMA_DROPPED=0

RESTORE_COMMAND=(pg_restore --dbname="${DATABASE}" --no-owner --no-privileges
                 --single-transaction --exit-on-error "${DUMP}")

on_exit() {
  local status=$?
  if (( status != 0 )) && (( SCHEMA_DROPPED == 1 )); then
    cat >&2 <<EOF

RECOVERY REQUIRED.

The schema of '${DATABASE}' was dropped and the restore did not complete, so the
database is empty or partially restored. This drill is not failure-atomic; that
is a documented property, not a surprise.

The dump is intact at:
  ${DUMP}
  ${DUMP}.sha256

Recover with either:
  1. sha256sum --check '${DUMP}.sha256' && \\
     ${RESTORE_COMMAND[*]}
  2. or re-run this drill, which dumps nothing useful from an empty database —
     so prefer (1) unless the database is disposable scratch state you are
     willing to lose, in which case:
       APP_ENVIRONMENT=<env> DATABASE_URL=<url> ./venv/bin/alembic upgrade head
EOF
  fi
  exit "${status}"
}
trap on_exit EXIT

row_counts() {
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 <<'SQL'
SELECT string_agg(entry, E'\n' ORDER BY entry) FROM (
  SELECT format('%s=%s', table_name,
                (xpath('/row/c/text()',
                       query_to_xml(format('SELECT count(*) AS c FROM public.%I', table_name),
                                    false, true, '')))[1]::text) AS entry
  FROM information_schema.tables
  WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
) inventory;
SQL
}

echo "1. Dumping ${DATABASE} in custom format"
pg_dump --format=custom --dbname="${DATABASE}" --file="${DUMP}"

echo "2. Recording the backup checksum"
sha256sum "${DUMP}" | tee "${DUMP}.sha256"

echo "3. Recording the table and row inventory"
row_counts >"${BEFORE}"
cat "${BEFORE}"

echo "4. Destroying the schema to prove the restore, not the backup"
SCHEMA_DROPPED=1
psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 \
     -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;' >/dev/null

echo "5. Restoring from the backup"
"${RESTORE_COMMAND[@]}"

echo "6. Comparing the inventory"
row_counts >"${AFTER}"
if ! diff -u "${BEFORE}" "${AFTER}"; then
  echo "Restore verification FAILED: the inventory differs." >&2
  exit 1
fi

SCHEMA_DROPPED=0
echo "Restore verified for ${DATABASE}. Artefacts in ${WORK_DIRECTORY}"
