#!/usr/bin/env bash
#
# Development backup and restore drill.
#
# Plan §14.3 requires restore tests, not merely backup success messages. This
# script performs the full round trip against a *disposable* database: dump,
# checksum, destroy the schema, restore, and compare the table and row
# inventory before and after.
#
# It refuses production outright. It refuses staging *by default*, and accepts it
# only when the operator supplies two independent, non-default signals
# (FREEDOM_DRILL_ALLOW_STAGING and FREEDOM_DRILL_STAGING_CONFIRM naming the exact
# database). That path exists for one accepted procedure -- P3.5's SP-10,
# TC-OPS-02's staging half -- and is announced loudly when it is taken. Approved
# by Peter Duscha, Operations Owner, 2026-08-26 (decision D-q, change-log
# C-P3.5-V), as route A of docs/review/phase-3-p3-5-c8-staging-drill-guard-proposal.md.
#
# Recovering production means restoring a verified off-host backup under the
# procedure in docs/operations/database-development.md, never running a drill
# script.
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

# Computed once and reused by the connected-database gate below (0c). The
# previous shape repeated the list, and the copy that matters for safety is the
# second one -- the one that checks where the connection actually landed.
PERMITTED_DATABASES="freedom_dev freedom_test"

if [[ "${DATABASE}" == "freedom_staging" ]]; then
  # Two independent signals, neither a default, and the second one has to name
  # the database: a stray "export FREEDOM_DRILL_ALLOW_STAGING=1" in a shell
  # profile cannot by itself turn a mistyped argument into a staging drill.
  if [[ "${FREEDOM_DRILL_ALLOW_STAGING:-}" == "1" \
        && "${FREEDOM_DRILL_STAGING_CONFIRM:-}" == "freedom_staging" ]]; then
    PERMITTED_DATABASES="${PERMITTED_DATABASES} freedom_staging"
    echo "=====================================================================" >&2
    echo "STAGING DRILL. This DESTROYS AND RESTORES the freedom_staging schema." >&2
    echo "Authorized for SP-10 (TC-OPS-02 staging half) under SG-2 only." >&2
    echo "The dump taken in step 1 is the only thing standing between this run" >&2
    echo "and a lost staging database. Verify it before step 3." >&2
    echo "=====================================================================" >&2
  else
    echo "Refusing to drill against 'freedom_staging': it needs both" \
         "FREEDOM_DRILL_ALLOW_STAGING=1 and" \
         "FREEDOM_DRILL_STAGING_CONFIRM=freedom_staging." >&2
    exit 2
  fi
fi

if [[ " ${PERMITTED_DATABASES} " != *" ${DATABASE} "* ]]; then
  echo "Refusing to drill against '${DATABASE}': only ${PERMITTED_DATABASES}" \
       "may be drilled." >&2
  exit 2
fi

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

# The same list, not a second copy of it. This gate is the security-relevant one:
# it checks where libpq actually landed, after every redirection.
if [[ " ${PERMITTED_DATABASES} " != *" ${CONNECTED_DATABASE} "* ]]; then
  refuse_connection "'${CONNECTED_DATABASE}' is not a permitted drill target."
fi

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
GRANTS_BEFORE="${WORK_DIRECTORY}/grants-before.txt"
GRANTS_AFTER="${WORK_DIRECTORY}/grants-after.txt"

# The template that is the single source of truth for the runtime role's rights.
# Beside this script, so the drill cannot be separated from it.
GRANT_TEMPLATE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/runtime-grants.sql.tmpl"

SCHEMA_DROPPED=0

# `--no-owner --no-privileges` is the portable choice: it lets an archive restore
# into a cluster whose roles differ, without `--exit-on-error` aborting the whole
# restore on a GRANT naming a role that does not exist there. **It also discards
# every GRANT in the archive** — which is invisible on a disposable database where
# only the owner ever connects, and fatal on one with a restricted runtime role.
#
# Finding N-20 (2026-08-26): a staging restore returned every row and every
# trigger, reported success, and left the portal and worker crash-looping because
# the runtime role held no privileges. The flags stay — reverting them would trade
# a recoverable state for a restore that aborts mid-incident — and steps 5b and 6
# below restore the grant state deliberately and then **prove** it, rather than
# leaving it to a step an operator must remember.
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

# The privilege state the restore discards. Recorded before the destroy and
# compared after, so the drill can no longer be blind to what it throws away
# (finding N-20). Schema privileges are included deliberately: the staging
# failure left `public` with no ACL at all, and a table-only inventory would not
# have shown it.
grant_inventory() {
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 <<'SQL'
SELECT coalesce(string_agg(entry, E'\n' ORDER BY entry), '(no grants)') FROM (
  SELECT format('TABLE %s|%s|%s', table_name, grantee, privilege_type) AS entry
    FROM information_schema.table_privileges
   WHERE table_schema = 'public'
  UNION ALL
  SELECT format('SCHEMA public|%s|%s', pg_get_userbyid(a.grantee), a.privilege_type)
    FROM pg_namespace n, aclexplode(n.nspacl) a
   WHERE n.nspname = 'public'
) grants;
SQL
}

# The role whose privileges must survive: whoever held table grants before the
# destroy, other than the invoking user and PUBLIC. Derived rather than
# configured, so the drill needs no per-database mapping to keep in step.
detect_runtime_role() {
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 <<'SQL'
SELECT DISTINCT grantee
  FROM information_schema.table_privileges
 WHERE table_schema = 'public'
   AND grantee NOT IN (current_user, 'PUBLIC');
SQL
}

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

echo "3b. Recording the privilege inventory (N-20)"
grant_inventory >"${GRANTS_BEFORE}"
RUNTIME_ROLE="$(detect_runtime_role | tr -d '[:space:]')"
if [[ -z "${RUNTIME_ROLE}" ]]; then
  echo "    No runtime role holds table grants here; nothing to re-apply."
elif [[ "${RUNTIME_ROLE}" == *$'\n'* ]]; then
  echo "Refusing to drill: more than one non-owner role holds table grants," >&2
  echo "so which one the runtime template should name is ambiguous. Resolve" >&2
  echo "that before rehearsing a restore that has to put them back." >&2
  exit 2
else
  echo "    Runtime role: ${RUNTIME_ROLE}"
fi

echo "4. Destroying the schema to prove the restore, not the backup"
SCHEMA_DROPPED=1
psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 \
     -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;' >/dev/null

echo "5. Restoring from the backup"
"${RESTORE_COMMAND[@]}"

echo "5b. Re-applying the runtime grants the restore discarded (N-20)"
if [[ -n "${RUNTIME_ROLE}" ]]; then
  if [[ ! -r "${GRANT_TEMPLATE}" ]]; then
    echo "Restore verification FAILED: ${GRANT_TEMPLATE} is missing, so the" >&2
    echo "runtime role's privileges cannot be restored." >&2
    exit 1
  fi
  sed "s/__APP_ROLE__/${RUNTIME_ROLE}/g" "${GRANT_TEMPLATE}" \
    | psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 -f - >/dev/null
  echo "    Applied ${GRANT_TEMPLATE##*/} for ${RUNTIME_ROLE}"
else
  echo "    Skipped: no runtime role held grants before the destroy."
fi

echo "6. Comparing the inventory"
row_counts >"${AFTER}"
if ! diff -u "${BEFORE}" "${AFTER}"; then
  echo "Restore verification FAILED: the inventory differs." >&2
  exit 1
fi

echo "6b. Comparing the privilege inventory (N-20)"
grant_inventory >"${GRANTS_AFTER}"

# **Loss, not difference.** An exact comparison would fail on a database whose
# grants had drifted before the drill — step 5b re-applies the canonical
# template to every table, so the result can legitimately hold *more* entries
# than the starting state did. Failing there would punish the drill for having
# repaired something. What must never happen is a privilege that existed before
# and does not exist after, which is precisely the N-20 condition.
LOST_PRIVILEGES="$(comm -23 <(sort "${GRANTS_BEFORE}") <(sort "${GRANTS_AFTER}"))"
if [[ -n "${LOST_PRIVILEGES}" ]]; then
  echo "Restore verification FAILED: privileges present before the drill are" >&2
  echo "missing after it. The rows came back and the grants did not. An" >&2
  echo "application connecting as the runtime role would find the database" >&2
  echo "unusable — which is exactly what a row-count comparison cannot see" >&2
  echo "(N-20). Missing entries:" >&2
  echo "${LOST_PRIVILEGES}" >&2
  exit 1
fi

SCHEMA_DROPPED=0
echo "Restore verified for ${DATABASE}. Artefacts in ${WORK_DIRECTORY}"
