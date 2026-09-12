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
# **The recovery that is printed depends on how far the drill got** (finding
# PR-20260907-R2-2). A single "the schema was dropped" flag made the banner print
# the same full `pg_restore` for every failure after step 4, including failures
# that happen *after* the data restore has committed -- where repeating it fails
# on the objects that are already there instead of reaching the grant repair the
# operator actually needs. `DRILL_STAGE` therefore records the last step that
# **succeeded**, and each stage prints its own resume point:
#
#   intact                -> nothing was destroyed; no banner
#   destroy_attempted     -> the destroy ran and did not report success: whether
#                            the schema still holds its objects is NOT KNOWN, and
#                            neither is whether its transaction has ended; the
#                            banner says both
#   destroyed             -> the destroy reported success and the data restore had
#                            not started: EMPTY
#   restore_attempted     -> data restore ran and did not report success:
#                            committed or not is NOT KNOWN, and whether it has
#                            finished at all is NOT KNOWN; the banner says both
#   restored              -> data restore committed; grants not restored
#   schema_grants_applied -> schema grants applied; runtime grants not applied
#   grants_applied        -> everything applied; a verification did not pass
#   verified              -> the drill succeeded; no banner
#
# **`destroy_attempted` is separate from `destroyed`, and that is finding
# PR-20260908-R3-1.** `DRILL_STAGE="destroyed"` used to be assigned *before* the
# destructive command on the reasoning that a failure inside it leaves an unknown
# state. But the `destroyed` banner does not describe an unknown state: it asserts
# that the schema was dropped, that the database is EMPTY, and it prescribes a
# full restore. A command that never ran, that was refused, or whose result was
# lost establishes none of that. Codex modified the stub's DROP branch to emit a
# fixed error and exit 42 without changing its state file; the drill exited 42,
# never called `pg_restore`, and still printed `database is EMPTY` and
# `4. pg_restore ...`.
#
# Responsibility is therefore recorded before the command -- `destroy_attempted`
# means "this drill may have destroyed something" -- and the *known* state is
# recorded only after the command succeeds. The `destroy_attempted` banner asks
# the operator to establish the schema's actual state before choosing anything,
# and it prescribes no mutation at all until they have.
#
# **And what "the schema's actual state" can be established from is narrower than
# it looked** (PR-20260908-R3-1, continued). The first version of that step 0
# read `pg_class` and the base-table inventory, and treated `relations=0` as "the
# database held no objects". `pg_class` describes *relations*; a function lives
# in `pg_proc` and the row inventory does not see it either, so a schema holding
# only a function reported `schema_present=true|relations=0|base_tables=0` both
# before and after a destroy that removed it. Codex drove both scenarios --
# refused DROP with the function intact, and applied DROP with the client result
# lost -- through the stub boundary: the reports matched in both, and the banner
# said the schema was intact, that there had been nothing to lose, and that no
# restore was required. The state report now counts each schema-scoped catalog
# class separately, every conclusion drawn from it is written to hold for counts
# and for nothing wider, and the one state these counts genuinely cannot resolve
# -- every class zero now *and* zero in the baseline -- stops for an operator
# instead of being called empty.
#
# **And a report is an observation, not an outcome** (PR-20260908-R5-1, the same
# finding continued). Both uncertain stages read their reports and concluded from
# what those counted *now*: the destroy did not take effect and no restore is
# required, or the restore rolled back and may be run again. Neither first
# established that the transaction this drill started had ended. PostgreSQL 16
# documents both halves of why that is not safe: with
# `client_connection_check_interval=0`, the default, the server detects a lost
# connection at its next socket interaction rather than necessarily stopping the
# query when the client disappears; and a Read Committed SELECT sees what was
# committed before the query began, not another transaction's uncommitted work.
# So a DROP whose client died can still be running: `routines=1` and an empty
# inventory match their baselines, the operator is told no restore is required,
# and the transaction then commits and takes the function with it. The dependent
# restore decision has the mirror image -- zero counts are also what an
# uncommitted restore that is still running looks like, because
# `--single-transaction` publishes nothing until it commits, so "it rolled back,
# run it again" would start a second restore beside one still in flight.
#
# Both step 0s therefore ask **whether the transaction has ended** before they
# read anything, and every outcome below them is provisional until an operator
# has answered it. This drill does not answer it: there is no reliable evidence
# it could leave behind, because the process that would write it is the one whose
# death defines the failure, and pg_stat_activity shows every user that a session
# exists without necessarily showing them the fields that would identify its work
# or its open transaction (PostgreSQL 16, Viewing Statistics: existence and
# general properties are visible to all users, while many columns are null in
# rows about another role's session). So the honest thing, and the thing this
# correction does, is to stop -- name what an operator must establish, name what
# does not establish it, and refuse to classify the outcome until they have.
# **No banner terminates or cancels a backend**: that would convert an unknown
# outcome into a rollback somebody chose.
#
# Usage: infra/postgresql/backup-restore-drill.sh [database] [work-directory]
#
# Exit codes:
#   0  the restore was verified
#   1  the drill ran and the restore did not match
#   2  the drill refused. **Where it refused depends on which refusal it is**, and
#      saying otherwise was finding DS-R8-2: this list used to claim "before
#      touching anything" for all of them, which is only true of the first.
#        * gate 0a -- the requested database is not disposable. Refused before
#          the work directory is created, so nothing whatever was written.
#        * step 3b -- the runtime-role report could not be read: the query
#          failed, or its output was not the `ROLE <hex>` / `END <count>`
#          transport this script requires (finding PR-20260907-R2-1). An
#          unreadable report is never taken as "no runtime role". A record
#          carrying an encoded NUL byte is refused here too (finding
#          PR-20260908-R3-2): PostgreSQL cannot store a NUL in a role name and
#          the shell cannot carry one, so it is malformed transport, and it is
#          refused *before* it is decoded into a form that would drop it.
#        * step 3b -- more than one non-owner role holds table grants, or the
#          single such role is not a supported runtime role name (finding
#          PR-20260907-2: lower case only, no surrounding or embedded
#          whitespace, no reserved key word or special role spelling, no `pg_`
#          prefix, at most 63 bytes -- so that the unquoted SQL spelling is the
#          name PostgreSQL stores).
#        * step 3d -- the runtime grant template is missing or its placeholder
#          did not substitute. Moved here from step 5b by PR-20260907-1: after
#          the destroy this was not a refusal at all, it was a recovery whose
#          runtime grants could not be reconstructed.
#          All three decisions are made *after* step 1's dump, step 2's
#          checksum, the work directory and the read-only inventories of steps 3
#          and 3b, so **those artifacts may already exist on disk**. What has not
#          happened is the destructive part: no schema is dropped, nothing is
#          restored, the database is in exactly the state it was in, and **no
#          recovery is required**.
#   3  the connection could not be proven safe; nothing was touched and the work
#      directory is not created

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

# ---------------------------------------------------------------------------
# The three recovery artifacts, named here and written before the destroy
# ---------------------------------------------------------------------------
# Finding PR-20260907-1: `on_exit` printed `pg_restore --no-privileges` followed
# by `schema-grants.sql`, and that file carries schema ownership and the schema
# ACL and **nothing else**. An operator who followed the printed procedure
# exactly got every row back and an application role that could not read a
# single table -- N-20 again, reached this time by doing what the script said.
#
# So the runtime grants are rendered **into the work directory before step 4**,
# checksummed, and applied from that file by step 5b. One artifact, used by the
# normal path and by the recovery, which is what stops the two from disagreeing;
# and because the role is substituted before the destroy, recovery never needs
# an operator to work out which role the now-empty database used to grant.
RUNTIME_GRANTS="${WORK_DIRECTORY}/runtime-grants.sql"

# The privilege inventory query, written out rather than kept in a here-document,
# so the recovery procedure can name a file and re-run **the same check** step 6b
# runs. A recovery verified by a different query would be verified by something
# nobody compared with the drill.
GRANT_INVENTORY_SQL="${WORK_DIRECTORY}/grants-inventory.sql"
GRANTS_AFTER_RECOVERY="${WORK_DIRECTORY}/grants-after-recovery.txt"

# The same treatment for the **data** inventory (PR-20260907-R2-2 item 3). A
# recovery that restores the grants and never looks at the rows has verified half
# of what the drill verifies. Writing the query out means the recovery re-runs
# step 6's query rather than an operator's paraphrase of it, and -- at the
# `restore_attempted` stage -- it is also how the operator establishes whether
# the restore committed at all before deciding to run it again.
INVENTORY_QUERY_SQL="${WORK_DIRECTORY}/inventory-query.sql"
INVENTORY_AFTER_RECOVERY="${WORK_DIRECTORY}/inventory-after-recovery.txt"

# ---------------------------------------------------------------------------
# The schema-state report -- finding PR-20260908-R3-1
# ---------------------------------------------------------------------------
# The data inventory alone cannot answer "did the destroy happen?", and item 2 of
# the finding says so directly: a row-count match does not distinguish every
# schema state, **especially when the original database has no tables**, where an
# intact schema and a freshly recreated one produce the same empty inventory.
#
# So a second, structural report is written out and captured before the destroy:
# whether `public` exists at all, and how many objects of each schema-scoped
# catalog class it holds -- relations, base tables, routines, standalone types,
# extensions and the remaining schema-scoped catalogs. It is the same file the
# operator re-runs afterwards, so the comparison is against the drill's own query
# rather than a paraphrase of it.
#
# **The report counts named classes; it is not an object-identity inventory and
# it is not exhaustive** (PR-20260908-R3-1, continued). Counting relations alone
# was: a schema holding only a function reported `relations=0|base_tables=0`
# before *and* after a destroy that removed the function, and the matching
# reports were read as "intact, nothing lost, no restore required". The counts
# below cover far more, and every conclusion the banner draws from them is
# written to hold for counts over those classes and for nothing else. Where they
# cannot decide, the banner stops and says what an operator must establish, and
# points at the one identity inventory that exists -- `pg_restore --list` over
# the dump, which needs no database and changes nothing.
#
# **It also reports one moment, and that moment may not be after the transaction
# this drill started** (PR-20260908-R5-1). A report taken while the destroy or
# the restore is still open describes the state before it: under Read Committed
# it sees what was committed when its own query began, and the client's exit did
# not stop the backend. That is why both uncertain stages ask whether the
# transaction has ended *before* they read this report, and why every outcome
# they draw from it is provisional until an operator has answered that.
SCHEMA_STATE_SQL="${WORK_DIRECTORY}/schema-state.sql"
SCHEMA_STATE_BEFORE="${WORK_DIRECTORY}/schema-state-before.txt"
SCHEMA_STATE_AFTER_RECOVERY="${WORK_DIRECTORY}/schema-state-after-recovery.txt"

# The template that is the single source of truth for the runtime role's rights.
# Beside this script, so the drill cannot be separated from it.
GRANT_TEMPLATE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/runtime-grants.sql.tmpl"

# The last step that **succeeded**, not merely the last one that started. Every
# assignment below is placed *after* the command whose success it records, so a
# stage can never claim a command that did not finish. See the header comment for
# the seven values and what each one means.
DRILL_STAGE="intact"

# Set as soon as the row loop in step 3b has decided, so `on_exit` can read it
# under `set -u` whatever happens.
RUNTIME_ROLE=""

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
  if (( status == 0 )); then exit "${status}"; fi
  case "${DRILL_STAGE}" in
    # Nothing destructive has run, or everything succeeded. There is nothing to
    # recover, and printing a recovery banner for a step-3b refusal was the
    # inaccuracy DS-R8-2 corrected.
    intact|verified) exit "${status}" ;;
  esac

  # ------------------------------------------------------------------------
  # The runtime half of every step, or the sentence that says there is not one.
  # **Both are printed explicitly** (PR-20260907-1): a banner that simply omitted
  # the runtime step when no role held grants would be indistinguishable from one
  # that had forgotten it.
  # ------------------------------------------------------------------------
  local runtime_artifacts runtime_checksum runtime_apply runtime_rebuild
  if [[ -n "${RUNTIME_ROLE}" ]]; then
    runtime_artifacts="  ${RUNTIME_GRANTS}
  ${RUNTIME_GRANTS}.sha256"
    runtime_checksum="sha256sum --check '${RUNTIME_GRANTS}.sha256'"
    runtime_apply="psql --dbname=${DATABASE} -v ON_ERROR_STOP=1 -f '${RUNTIME_GRANTS}'"
    runtime_rebuild="     then re-apply '${SCHEMA_GRANTS}' and '${RUNTIME_GRANTS}', which a
     migration does not create."
  else
    runtime_artifacts="  (No runtime role held table grants before the destroy, so there is
   no runtime-grants.sql and none is to be applied. The schema grants above
   are still required.)"
    runtime_checksum="(no runtime-grants.sql: no runtime role held table grants)"
    runtime_apply="(no runtime grants to re-apply, for the same reason)"
    runtime_rebuild="     then re-apply '${SCHEMA_GRANTS}', which a migration does not create."
  fi

  # The two verifications, written once and used by every stage's procedure.
  local verify_privileges verify_inventory
  verify_privileges="Verify the restored privileges before declaring recovery complete:
       psql --dbname=${DATABASE} -tAX -v ON_ERROR_STOP=1 \\
            -f '${GRANT_INVENTORY_SQL}' >'${GRANTS_AFTER_RECOVERY}'
       comm -23 <(sort '${GRANTS_BEFORE}') <(sort '${GRANTS_AFTER_RECOVERY}')
     That is the same comparison step 6b makes. Recovery is complete only when
     it prints nothing. Every line it prints is a privilege that existed before
     this drill and does not exist now."
  verify_inventory="Verify the data inventory, which is the other half of what the drill
     verifies and is not implied by a restore command's exit status:
       psql --dbname=${DATABASE} -tAX -v ON_ERROR_STOP=1 \\
            -f '${INVENTORY_QUERY_SQL}' >'${INVENTORY_AFTER_RECOVERY}'
       diff -u '${BEFORE}' '${INVENTORY_AFTER_RECOVERY}'
     Recovery is complete only when that also prints nothing."

  # ------------------------------------------------------------------------
  # What is known about the data, and the resume point that follows from it --
  # finding PR-20260907-R2-2. Every stage below states the truth for its own
  # stage; none of them calls the database empty after a restore that committed,
  # and none of them repeats a data restore over objects that already exist.
  # ------------------------------------------------------------------------
  local data_state procedure not_recovery
  case "${DRILL_STAGE}" in
    destroy_attempted)
      data_state="The destroy command for '${DATABASE}' ran and did not report success, so WHAT THE
SCHEMA NOW HOLDS IS NOT KNOWN. This drill does not call the database empty here.
A command that was refused, that never ran, or whose result was lost proves
nothing about the schema, and the schema may be exactly as it was before this
drill started. IT MAY ALSO STILL BE CHANGING: a client that exited did not stop
the server, and the destroy's transaction may still be open. Step 0 below
establishes which state it is actually in, and nothing in this procedure changes
the database until it has."
      procedure="  0. Establish two things before choosing anything, in this order. Nothing in
     this step changes the database.
     0a. HAS THE DESTROY'S SERVER-SIDE TRANSACTION ENDED? The command above did
         not report success, and that is a statement about this drill's client,
         not about the server. UNTIL AN OPERATOR HAS ESTABLISHED THAT THE
         TRANSACTION HAS ENDED, EVERY OUTCOME IN 0b IS PROVISIONAL: none of them
         may be acted on, and that includes concluding that no restore is
         required, running a restore, and resuming at any step below. Those
         reports show what had been committed when they ran, so a transaction
         that is still open commits or aborts afterwards and changes the answer
         underneath them.
         WHAT DOES NOT ESTABLISH IT: this drill's client exiting or failing --
         with client_connection_check_interval=0, which is the default, the
         server does not necessarily stop a statement when its client
         disappears, so the destroy may still be running; elapsed time; running
         the reports twice and getting the same answer; the exit status this
         drill ended with.
         WHAT WOULD: that no backend is still running this drill's statement or
         holding its transaction open against '${DATABASE}'. pg_stat_activity is
         where a backend that is still there is visible -- its rows for this
         database, with pid, backend_start, xact_start, state and query. Read it
         deliberately. A pid is not an identity on its own, because pids are
         reused, so match backend_start with it. And PostgreSQL restricts
         columns here, not rows: the existence of a session and its general
         properties, such as its session user and database, are visible to all
         users, while in rows about a session belonging to a role you are not a
         member of many columns are null unless you are a superuser or hold
         pg_read_all_stats. So the row may be there while the fields that would
         tell you what that session is running, and whether it still holds a
         transaction open, are not. A NULL FIELD, OR BEING UNABLE TO ASSOCIATE
         A VISIBLE SESSION WITH THIS DRILL, IS NOT PROOF THAT THIS TRANSACTION
         HAS ENDED. A backend that has ended cannot come back, so that answer
         stays true once you have it; 'still running' does not, so re-read it
         rather than assuming it stayed that way.
         Do not terminate or cancel a backend to settle this. This procedure
         never does that: it would turn an unknown outcome into a rollback
         somebody chose, at the one moment nobody knows what the transaction was
         doing.
         IF COMPLETION CANNOT BE ESTABLISHED, THE OUTCOME IS UNRESOLVED. Stop
         here, change nothing, and resolve it with an operator.
     0b. WHAT THE SCHEMA HOLDS, read AFTER 0a has answered. Both reports are
         read-only and neither changes the database. If you ran them before 0a
         answered, run them again: a report taken while the transaction was
         still open describes the state before it, not the state it leaves.
       psql --dbname=${DATABASE} -tAX -v ON_ERROR_STOP=1 \\
            -f '${SCHEMA_STATE_SQL}' >'${SCHEMA_STATE_AFTER_RECOVERY}'
       diff -u '${SCHEMA_STATE_BEFORE}' '${SCHEMA_STATE_AFTER_RECOVERY}'
       psql --dbname=${DATABASE} -tAX -v ON_ERROR_STOP=1 \\
            -f '${INVENTORY_QUERY_SQL}' >'${INVENTORY_AFTER_RECOVERY}'
       diff -u '${BEFORE}' '${INVENTORY_AFTER_RECOVERY}'
     WHAT THESE REPORTS OBSERVE, AND WHAT THEY DO NOT. The state report counts
     how many objects 'public' holds in each of these classes: relations, base
     tables, routines, standalone types, extensions, and every remaining
     schema-scoped catalog together as other_objects. It does NOT say WHICH
     objects those are -- equal counts are not an object-identity inventory --
     and it is NOT an exhaustive enumeration of everything PostgreSQL can place
     in a schema. Read every outcome below as a statement about those counts and
     about nothing wider. They also observe only what had been committed when
     they ran, which is what 0a is for. The identity inventory that does exist
     is the archive:
       pg_restore --list '${DUMP}'
     names every object it holds, needs no database and changes nothing.
     * EITHER COMMAND FAILED: the state is still not known. A query that did not
       run is not evidence that the schema is empty. Resolve the client or
       server problem and repeat step 0. Do not restore, drop or truncate
       anything on the strength of a query that did not answer.
     * schema_present=false: the schema is ABSENT. Neither a restore nor a grant
       can run into a schema that does not exist, and recreating one is a
       deliberate change this procedure does not make for you. Stop here and
       resolve it with an operator.
     * SOME COUNT IS NON-ZERO AND THE WHOLE STATE REPORT MATCHES
       '${SCHEMA_STATE_BEFORE}', with the inventory matching '${BEFORE}' as
       well: THE DESTROY DID NOT TAKE EFFECT -- provided 0a established that its
       transaction has ended. If it did not, this is also exactly what an
       unfinished destroy looks like from another session, and the outcome is
       UNRESOLVED rather than a state you may act on.
       A dropped and recreated 'public' holds nothing at all, so objects that
       are still counted there were never dropped. Once 0a has answered, NO
       DATA RESTORE IS REQUIRED and none may be run -- it aborts on the objects
       that are already there. What this establishes is that the
       schema was not dropped and recreated; being counts, it does not certify
       the objects one by one, so if a specific object matters, read
       pg_restore --list '${DUMP}' against the catalog. Resolve whatever refused
       the destroy; running this drill again afterwards is an ordinary run, not
       a recovery.
     * EVERY COUNT IS ZERO AND '${SCHEMA_STATE_BEFORE}' RECORDED AT LEAST ONE
       OBJECT IN ANY CLASS: everything it counted is gone, so the schema was
       dropped and recreated -- again provided 0a established that its
       transaction has ended, without which this is a snapshot of a database
       something may still be changing. That is the 'destroyed' state. Continue
       at step 1.
     * EVERY COUNT IS ZERO AND '${SCHEMA_STATE_BEFORE}' RECORDED ZERO IN EVERY
       CLASS: THESE REPORTS CANNOT RESOLVE THIS STATE, and this procedure does
       not pretend otherwise. An intact schema and a dropped-and-recreated one
       produce exactly this pair of reports, and neither report establishes that
       the schema held nothing before the drill: they count the classes named
       above and no others, so an object of a kind they do not count may have
       been there and may now be gone. THIS IS NOT 'THERE WAS NOTHING TO LOSE'.
       Do not restore, drop or truncate on the strength of these counts. Stop
       here and resolve it with an operator, who can read
       pg_restore --list '${DUMP}' for what the database actually held before
       the destroy and inspect the catalogs directly for what it holds now. 0a
       does not rescue this one: even a transaction known to have ended leaves
       these two reports identical here.
     * ANYTHING ELSE -- counts that are neither all zero nor equal to
       '${SCHEMA_STATE_BEFORE}', or an inventory that differs from '${BEFORE}'
       without being empty: the schema is in an UNEXPECTED state. Neither
       restoring over it nor resetting it is safe, and this procedure does not
       choose between them. Stop here and resolve it with an operator.
  1. sha256sum --check '${DUMP}.sha256'
  2. sha256sum --check '${SCHEMA_GRANTS}.sha256'
  3. ${runtime_checksum}
  4. ${RESTORE_COMMAND[*]}
  5. psql --dbname=${DATABASE} -v ON_ERROR_STOP=1 -f '${SCHEMA_GRANTS}'
  6. ${runtime_apply}
  7. ${verify_privileges}
  8. ${verify_inventory}"
      ;;
    destroyed)
      data_state="The schema of '${DATABASE}' was dropped and the data restore had not started,
so the database is EMPTY. This drill is not failure-atomic; that is a documented
property, not a surprise."
      procedure="  1. sha256sum --check '${DUMP}.sha256'
  2. sha256sum --check '${SCHEMA_GRANTS}.sha256'
  3. ${runtime_checksum}
  4. ${RESTORE_COMMAND[*]}
  5. psql --dbname=${DATABASE} -v ON_ERROR_STOP=1 -f '${SCHEMA_GRANTS}'
  6. ${runtime_apply}
  7. ${verify_privileges}
  8. ${verify_inventory}"
      ;;
    restore_attempted)
      data_state="The schema of '${DATABASE}' was dropped and the data restore did not report
success, so WHETHER IT COMMITTED IS NOT KNOWN. --single-transaction
--exit-on-error rolls the whole restore back on an ordinary error, which leaves
the database empty; a process that was killed or crashed is not an ordinary
error, and this drill cannot tell the two apart from the outside. THE RESTORE
MAY ALSO STILL BE RUNNING: a client that exited did not stop the server. Step 0
below establishes which it was. This procedure assumes neither."
      procedure="  0. Establish two things before deciding whether to run the restore again, in
     this order. Nothing in this step changes the database.
     0a. HAS THE RESTORE'S SERVER-SIDE TRANSACTION ENDED? The command above did
         not report success, and that is a statement about this drill's client,
         not about the server. UNTIL AN OPERATOR HAS ESTABLISHED THAT THE
         TRANSACTION HAS ENDED, EVERY OUTCOME IN 0b IS PROVISIONAL: none of them
         may be acted on, and that includes running the restore again and
         skipping it. A restore that is still running has published nothing --
         --single-transaction keeps every object it has loaded invisible to
         other sessions until it commits -- so an unfinished restore looks
         exactly like a rolled-back one from another session. Reading that as a
         rollback and running the restore again starts a second restore beside
         one that is still in flight.
         WHAT DOES NOT ESTABLISH IT: this drill's client exiting or failing --
         with client_connection_check_interval=0, which is the default, the
         server does not necessarily stop a statement when its client
         disappears, so the restore may still be running; elapsed time; running
         the reports twice and getting the same answer; the exit status this
         drill ended with.
         WHAT WOULD: that no backend is still running this drill's restore or
         holding its transaction open against '${DATABASE}'. pg_stat_activity is
         where a backend that is still there is visible -- its rows for this
         database, with pid, backend_start, xact_start, state and query. Read it
         deliberately. A pid is not an identity on its own, because pids are
         reused, so match backend_start with it. And PostgreSQL restricts
         columns here, not rows: the existence of a session and its general
         properties, such as its session user and database, are visible to all
         users, while in rows about a session belonging to a role you are not a
         member of many columns are null unless you are a superuser or hold
         pg_read_all_stats. So the row may be there while the fields that would
         tell you what that session is running, and whether it still holds a
         transaction open, are not. A NULL FIELD, OR BEING UNABLE TO ASSOCIATE
         A VISIBLE SESSION WITH THIS DRILL, IS NOT PROOF THAT THIS TRANSACTION
         HAS ENDED. A backend that has ended cannot come back, so that answer
         stays true once you have it; 'still running' does not, so re-read it
         rather than assuming it stayed that way.
         Do not terminate or cancel a backend to settle this. This procedure
         never does that: it would turn an unknown outcome into a rollback
         somebody chose, at the one moment nobody knows what the transaction was
         doing.
         IF COMPLETION CANNOT BE ESTABLISHED, THE OUTCOME IS UNRESOLVED. Stop
         here, run no restore, and resolve it with an operator.
     0b. WHETHER WHAT THE ARCHIVE HOLDS IS IN THE SCHEMA, read AFTER 0a has
         answered. Both reports are read-only and neither changes the database.
         If you ran them before 0a answered, run them again: a report taken
         while the transaction was still open describes the state before it, not
         the state it leaves.
       psql --dbname=${DATABASE} -tAX -v ON_ERROR_STOP=1 \\
            -f '${SCHEMA_STATE_SQL}' >'${SCHEMA_STATE_AFTER_RECOVERY}'
       diff -u '${SCHEMA_STATE_BEFORE}' '${SCHEMA_STATE_AFTER_RECOVERY}'
       psql --dbname=${DATABASE} -tAX -v ON_ERROR_STOP=1 \\
            -f '${INVENTORY_QUERY_SQL}' >'${INVENTORY_AFTER_RECOVERY}'
       diff -u '${BEFORE}' '${INVENTORY_AFTER_RECOVERY}'
     THE ROW INVENTORY ALONE CANNOT ANSWER THIS (PR-20260908-R3-1, continued).
     It counts base tables, so on a database whose archive holds none -- one
     holding only functions, say -- a rolled-back restore and a committed one
     both leave it matching '${BEFORE}', and reading that as 'the restore
     committed' is the same unsupported inference, one stage later. The state
     report counts more classes and is still only counts: it does not say which
     objects they are and it does not enumerate every kind of schema object.
     The identity inventory is pg_restore --list '${DUMP}'.
     * EITHER COMMAND FAILED: whether the restore committed is still not known.
       Resolve the client or server problem and repeat step 0. Do not run the
       restore again on the strength of a query that did not answer.
     * '${SCHEMA_STATE_BEFORE}' RECORDS ZERO IN EVERY CLASS: these reports
       cannot tell a rolled-back restore from a committed one here, because both
       leave every count at zero. Stop and resolve it with an operator, reading
       pg_restore --list '${DUMP}' for what the archive holds and the catalogs
       for what is there now.
     * EVERY COUNT IS ZERO while '${SCHEMA_STATE_BEFORE}' recorded objects:
       none of what the archive holds is in the schema, so the transaction
       rolled back -- provided 0a established that its transaction has ended.
       If it did not, an unfinished restore produces this same pair of reports
       and the outcome is UNRESOLVED. Once 0a has answered, continue at step 1.
     * BOTH DIFFS PRINT NOTHING while '${SCHEMA_STATE_BEFORE}' recorded objects:
       everything these reports count is back in the numbers the archive holds,
       so the restore committed -- once 0a has established that its transaction
       has ended, without which no count here is a settled one. SKIP STEP 4 --
       running it again over the existing objects fails instead of repairing
       anything -- and continue at step 5.
     * ANYTHING ELSE: the restore is partial. Neither resuming nor repeating it
       is safe, and this procedure does not choose for you.
  1. sha256sum --check '${DUMP}.sha256'
  2. sha256sum --check '${SCHEMA_GRANTS}.sha256'
  3. ${runtime_checksum}
  4. ${RESTORE_COMMAND[*]}
  5. psql --dbname=${DATABASE} -v ON_ERROR_STOP=1 -f '${SCHEMA_GRANTS}'
  6. ${runtime_apply}
  7. ${verify_privileges}
  8. ${verify_inventory}"
      ;;
    restored)
      data_state="The data restore COMPLETED SUCCESSFULLY and the drill then stopped before the
grants were restored. The database is NOT empty. Do not restore over it: the
same restore run again fails on the objects that are already there, which is why
this banner resumes at the grants instead of repeating step 4."
      procedure="  1. sha256sum --check '${SCHEMA_GRANTS}.sha256'
  2. ${runtime_checksum}
  3. psql --dbname=${DATABASE} -v ON_ERROR_STOP=1 -f '${SCHEMA_GRANTS}'
  4. ${runtime_apply}
  5. ${verify_privileges}
  6. ${verify_inventory}"
      ;;
    schema_grants_applied)
      data_state="The data restore and the schema grants COMPLETED SUCCESSFULLY, and the drill
stopped before the runtime table grants were restored. The database is NOT empty
and must not be restored over. Its rows are present and the application role
holds no table grants, which is exactly the N-20 state."
      procedure="  1. ${runtime_checksum}
  2. ${runtime_apply}
  3. ${verify_privileges}
  4. ${verify_inventory}"
      ;;
    grants_applied)
      data_state="The data restore, the schema grants and the runtime grants ALL COMPLETED
SUCCESSFULLY, and the drill stopped in verification. The database is NOT empty
and must not be restored over. A check that did not pass is not a drill that
passed: a restore command's exit status is not a substitute for the comparison
below, and this banner does not treat it as one."
      procedure="  1. ${verify_privileges}
  2. If that printed lines, the grants did not take. Re-apply them and repeat
     step 1:
       psql --dbname=${DATABASE} -v ON_ERROR_STOP=1 -f '${SCHEMA_GRANTS}'
       ${runtime_apply}
  3. ${verify_inventory}
  4. If the data inventory still differs, the data restore itself is in
     question. Do NOT run step 4 of the full procedure over the objects that are
     there: it fails on them. Reaching a clean retry means deliberately resetting
     the schema, which destroys what a restore did put back; that is an operator
     decision and this procedure does not make it."
      ;;
  esac

  # The rebuild-from-migrations fallback is only a fallback where the data is
  # gone. Offering it after a committed restore would be offering to destroy it.
  case "${DRILL_STAGE}" in
    destroy_attempted)
      not_recovery="Re-running this drill is NOT a recovery step, and until step 0 has answered it is
not a step of any kind: it would dump the database in whatever state it is
actually in and then destroy that state. Rebuilding from migrations is not
offered here either -- it would replace a schema that may be completely intact.
If step 0 establishes that the schema was dropped and recreated -- which takes 0a
and not the reports alone -- **and** the dump
turns out to be unusable, then the 'destroyed' fallback applies: this database is
disposable scratch state and is rebuilt from migrations, which recreates the
schema, not the data the dump held:
       APP_ENVIRONMENT=<env> DATABASE_URL=<url> ./venv/bin/alembic upgrade head
${runtime_rebuild}" ;;
    destroyed)
      not_recovery="Re-running this drill is NOT a recovery step: it would dump the empty database
over nothing useful and destroy whatever a partial restore did put back. If the
dump itself is unusable, this database is disposable scratch state and is rebuilt
from migrations instead -- which recreates the schema, not the data the dump held:
       APP_ENVIRONMENT=<env> DATABASE_URL=<url> ./venv/bin/alembic upgrade head
${runtime_rebuild}" ;;
    restore_attempted)
      not_recovery="Re-running this drill is NOT a recovery step, and until step 0 has answered it
is not a step of any kind: it would dump the database in whatever state it is
actually in -- possibly over a restore that is still running -- and then destroy
that state. If step 0 establishes that the restore did not commit, which takes 0a
and not the reports alone, **and** the dump itself is unusable, this database is
disposable scratch state and is rebuilt from migrations instead -- which
recreates the schema, not the data the dump held:
       APP_ENVIRONMENT=<env> DATABASE_URL=<url> ./venv/bin/alembic upgrade head
${runtime_rebuild}" ;;
    *)
      not_recovery="Re-running this drill is NOT a recovery step: it would dump the database in the
state this failure left it in and destroy that state to prove a restore of it.
The data restore already committed here, so there is nothing a rebuild from
migrations would recover and it is not offered." ;;
  esac

  cat >&2 <<EOF

RECOVERY REQUIRED.

${data_state}

Every artifact this procedure needs was written before the destroy and is intact:
  ${DUMP}
  ${DUMP}.sha256
  ${SCHEMA_GRANTS}
  ${SCHEMA_GRANTS}.sha256
${runtime_artifacts}
  ${GRANT_INVENTORY_SQL}
  ${GRANTS_BEFORE}
  ${INVENTORY_QUERY_SQL}
  ${BEFORE}
  ${SCHEMA_STATE_SQL}
  ${SCHEMA_STATE_BEFORE}

All of them must be retained. The restore runs with --no-privileges and therefore
discards every GRANT in the archive: omitting schema-grants.sql can leave schema
ownership or the schema ACL different from the pre-drill state, and omitting
runtime-grants.sql leaves the application role holding no table grants at all --
every row present and the application unable to use its tables, which is finding
N-20.

Recovery procedure, in this order:

${procedure}

${not_recovery}
EOF
  exit "${status}"
}
trap on_exit EXIT

# The privilege state the restore discards. Recorded before the destroy and
# compared after, so the drill can no longer be blind to what it throws away
# (finding N-20). Schema privileges are included deliberately: the staging
# failure left `public` with no ACL at all, and a table-only inventory would not
# have shown it.
# Written to a file rather than kept in a here-document, so the recovery
# procedure printed by `on_exit` can name it and re-run **the same query** step
# 6b runs (PR-20260907-1). A recovery verified by a differently-worded check
# would be verified by something nobody compared with the drill.
cat >"${GRANT_INVENTORY_SQL}" <<'SQL'
SELECT coalesce(string_agg(entry, E'\n' ORDER BY entry), '(no grants)') FROM (
  SELECT format('TABLE %s|%s|%s', table_name, grantee, privilege_type) AS entry
    FROM information_schema.table_privileges
   WHERE table_schema = 'public'
  UNION ALL
  SELECT format('SCHEMA public|%s|%s',
                CASE WHEN a.grantee = 0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,
                a.privilege_type)
    FROM pg_namespace n, aclexplode(n.nspacl) a
   WHERE n.nspname = 'public'
) grants;
SQL

grant_inventory() {
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 -f "${GRANT_INVENTORY_SQL}"
}

# Capture the schema owner and explicit grants so they can be restored along
# with table runtime grants (DS-R2-1).
SCHEMA_GRANTS="${WORK_DIRECTORY}/schema-grants.sql"
schema_grants_sql() {
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 <<'SQL'
SELECT format('ALTER SCHEMA public OWNER TO %I;', pg_get_userbyid(nspowner))
  FROM pg_namespace WHERE nspname = 'public';
SELECT 'REVOKE ALL ON SCHEMA public FROM PUBLIC;'
  FROM pg_namespace WHERE nspname = 'public' AND nspacl IS NOT NULL;
SELECT format('GRANT %s ON SCHEMA public TO %s%s;',
              a.privilege_type,
              CASE WHEN a.grantee = 0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END,
              CASE WHEN a.is_grantable THEN ' WITH GRANT OPTION' ELSE '' END)
  FROM pg_namespace n, aclexplode(n.nspacl) a
 WHERE n.nspname = 'public';
SQL
}

# ---------------------------------------------------------------------------
# The runtime-role report, and why it is not a list of names -- PR-20260907-R2-1
# ---------------------------------------------------------------------------
# A PostgreSQL role name is a `name`, and a quoted one may contain **anything but
# NUL** -- including a newline. The previous shape read the catalog through
# `RUNTIME_ROLE_REPORT="$(detect_runtime_role)"` and then split it on newlines,
# and both halves of that lose information a role name may carry:
#
#   * `$( )` strips **trailing** newlines, so a catalog role `freedom_runtime\n`
#     arrived as `freedom_runtime` -- a different role, which the guard then
#     approved and the grant then named;
#   * a **leading** newline arrived as an empty first line and was skipped, so
#     `\nfreedom_runtime` also arrived as `freedom_runtime`; and
#   * a role named `\n` vanished entirely and was mistaken for a zero-row result,
#     so the drill restored no table grants and reported success.
#
# No further pattern applied to the split lines can recover a record boundary
# that has already been deleted, so the transport is changed rather than
# re-checked. The server emits one `ROLE <hex>` line per record -- the name's
# UTF-8 bytes, hex encoded, so a record is pure `[0-9a-f]` and can contain no
# separator at all -- followed by one `END <count>` terminator. Cardinality and
# identity therefore both survive the shell, and the *absence* of the terminator
# is detectable, which is what stops an unreadable report from being read as
# "no runtime role".
#
# The hex is decoded back to the exact catalog bytes below and the supported-role
# contract is applied to **those bytes**. Encoding is transport; it is not
# validation, and it widens nothing.
#
# **One byte cannot make that round trip, and it is refused rather than lost**
# (finding PR-20260908-R3-2). Bash strings cannot hold a NUL, so an encoded `00`
# disappeared during decoding and left a shorter, different name -- which is how
# `freedom_runtime_test\0` became the supported `freedom_runtime_test`. A `name`
# in PostgreSQL is NUL terminated and cannot contain one, so such a record is
# malformed transport, and `hex_record_contains_nul` refuses it before the decode.
detect_runtime_role() {
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 <<'SQL'
WITH roles AS (
  SELECT DISTINCT grantee::text AS role_name
    FROM information_schema.table_privileges
   WHERE table_schema = 'public'
     AND grantee NOT IN (current_user, 'PUBLIC')
)
SELECT line FROM (
  SELECT 0 AS ordinal,
         'ROLE ' || encode(convert_to(role_name, 'UTF8'), 'hex') AS line
    FROM roles
  UNION ALL
  SELECT 1, 'END ' || (SELECT count(*) FROM roles)::text
) report
ORDER BY ordinal, line;
SQL
}

# ---------------------------------------------------------------------------
# NUL is refused **before** decoding -- finding PR-20260908-R3-2
# ---------------------------------------------------------------------------
# `decode_hex_role` accumulates bytes in a Bash string, and a Bash string cannot
# hold a NUL. So a transported `00` did not arrive as a byte the supported-name
# guard could refuse: it simply **vanished**, and the record that remained was a
# different, shorter name. Codex supplied the report
#
#   ROLE 66726565646f6d5f72756e74696d655f7465737400
#   END 1
#
# -- `freedom_runtime_test` followed by NUL -- and the drill exited 0, reached
# both DROP and the restore, and rendered a grant naming `freedom_runtime_test`.
# The valid control exited 0 as it should; the newline-bearing control still
# refused with exit 2 before DROP.
#
# PostgreSQL cannot store a NUL in a role name, so this is not a claim about a
# legitimate catalog role. It is **malformed transport**, and R2 already requires
# malformed transport to refuse rather than be repaired into an identity. The
# check therefore lives with the other transport checks and refuses the report.
#
# **Whole byte pairs, not a substring search.** `grep 00` over the record would
# misclassify a pair boundary: `4004` is `@` followed by `\x04` and carries no
# NUL at all, while its text contains `00` spanning the two bytes. The scan below
# steps two characters at a time, over a record the caller has already proved to
# be even-length lower-case hex, so a pair boundary is exactly where it looks.
hex_record_contains_nul() {
  local hex="$1"
  while [[ -n "${hex}" ]]; do
    if [[ "${hex:0:2}" == "00" ]]; then
      return 0
    fi
    hex="${hex:2}"
  done
  return 1
}

#: The decoded bytes of the last `decode_hex_role` call. A function cannot return
#: them: command substitution would strip exactly the trailing newline this
#: correction exists to preserve.
DECODED_ROLE=""
decode_hex_role() {
  local hex="$1" piece
  DECODED_ROLE=""
  while [[ -n "${hex}" ]]; do
    printf -v piece '%b' "\\x${hex:0:2}"
    DECODED_ROLE+="${piece}"
    hex="${hex:2}"
  done
}

# The data inventory query, written to a file for the same reason the privilege
# query is (PR-20260907-R2-2): the recovery procedure names a file and re-runs
# **the same query** step 6 runs, rather than a paraphrase of it.
cat >"${INVENTORY_QUERY_SQL}" <<'SQL'
SELECT string_agg(entry, E'\n' ORDER BY entry) FROM (
  SELECT format('%s=%s', table_name,
                (xpath('/row/c/text()',
                       query_to_xml(format('SELECT count(*) AS c FROM public.%I', table_name),
                                    false, true, '')))[1]::text) AS entry
  FROM information_schema.tables
  WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
) inventory;
SQL

row_counts() {
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 -f "${INVENTORY_QUERY_SQL}"
}

# The structural half of the same idea (PR-20260908-R3-1). `to_regnamespace`
# returns NULL rather than raising when the schema is absent, so the report can
# distinguish "no `public` at all" from "a `public` holding nothing".
#
# **`pg_class` is not an inventory of a schema (finding PR-20260908-R3-1,
# continued).** It describes *relations* -- tables, views, materialized views,
# indexes, sequences, foreign tables, partitioned tables and composite types.
# A schema holding nothing but a function reports `relations=0` and
# `base_tables=0`, because a function lives in `pg_proc`; the table/row inventory
# does not see it either. R3's report therefore answered
# `schema_present=true|relations=0|base_tables=0` both before and after a destroy
# that removed the function, the two reports matched, and the banner concluded
# that the schema was intact, that nothing could have been lost and that no
# restore was required. All three were false.
#
# So the report counts each schema-scoped catalog separately:
#
#   relations      pg_class            tables, views, matviews, indexes,
#                                      sequences, foreign and partitioned tables
#   base_tables    information_schema  the subset the row inventory can count
#   routines       pg_proc             functions, procedures, aggregates
#   types          pg_type             standalone types: base, enum, domain,
#                                      range and composite, excluding the row
#                                      types and array types a relation or a
#                                      type already accounts for
#   extensions     pg_extension        extensions installed *into* this schema
#   other_objects  pg_collation, pg_conversion, pg_operator, pg_opclass,
#                  pg_opfamily, pg_ts_config, pg_ts_dict, pg_ts_parser,
#                  pg_ts_template, pg_statistic_ext
#
# **What it establishes, and what it does not.** It establishes how many objects
# of each of those classes `public` holds. It does **not** establish *which*
# objects they are -- equal counts are not an object-identity inventory -- and it
# is **not** an exhaustive enumeration of everything PostgreSQL can place in a
# schema. Every decision the recovery banner makes from it is written to be true
# of counts over those classes and of nothing more, and where the counts cannot
# decide, the banner says so and stops instead of choosing a mutation.
#
# The identity inventory that *does* exist is the dump: `pg_restore --list` names
# every object the archive holds, needs no database, and changes nothing. The
# banner names it wherever an operator has to resolve a state these counts cannot.
cat >"${SCHEMA_STATE_SQL}" <<'SQL'
SELECT 'schema_present=' ||
       (to_regnamespace('public') IS NOT NULL)::text
    || '|relations=' ||
       (SELECT count(*) FROM pg_class c
          JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'public')::text
    || '|base_tables=' ||
       (SELECT count(*) FROM information_schema.tables
         WHERE table_schema = 'public' AND table_type = 'BASE TABLE')::text
    || '|routines=' ||
       (SELECT count(*) FROM pg_proc p
          JOIN pg_namespace n ON n.oid = p.pronamespace
         WHERE n.nspname = 'public')::text
    || '|types=' ||
       (SELECT count(*) FROM pg_type t
          JOIN pg_namespace n ON n.oid = t.typnamespace
          LEFT JOIN pg_class c ON c.oid = t.typrelid
         WHERE n.nspname = 'public'
           AND (t.typrelid = 0 OR c.relkind = 'c')
           AND NOT EXISTS (SELECT 1 FROM pg_type e
                            WHERE e.oid = t.typelem AND e.typarray = t.oid))::text
    || '|extensions=' ||
       (SELECT count(*) FROM pg_extension x
          JOIN pg_namespace n ON n.oid = x.extnamespace
         WHERE n.nspname = 'public')::text
    || '|other_objects=' ||
       ( (SELECT count(*) FROM pg_collation o
            JOIN pg_namespace n ON n.oid = o.collnamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_conversion o
            JOIN pg_namespace n ON n.oid = o.connamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_operator o
            JOIN pg_namespace n ON n.oid = o.oprnamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_opclass o
            JOIN pg_namespace n ON n.oid = o.opcnamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_opfamily o
            JOIN pg_namespace n ON n.oid = o.opfnamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_ts_config o
            JOIN pg_namespace n ON n.oid = o.cfgnamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_ts_dict o
            JOIN pg_namespace n ON n.oid = o.dictnamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_ts_parser o
            JOIN pg_namespace n ON n.oid = o.prsnamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_ts_template o
            JOIN pg_namespace n ON n.oid = o.tmplnamespace WHERE n.nspname = 'public')
       + (SELECT count(*) FROM pg_statistic_ext o
            JOIN pg_namespace n ON n.oid = o.stxnamespace WHERE n.nspname = 'public')
       )::text;
SQL

schema_state() {
  psql --dbname="${DATABASE}" -tAX -v ON_ERROR_STOP=1 -f "${SCHEMA_STATE_SQL}"
}

echo "1. Dumping ${DATABASE} in custom format"
pg_dump --format=custom --dbname="${DATABASE}" --file="${DUMP}"

echo "2. Recording the backup checksum"
sha256sum "${DUMP}" | tee "${DUMP}.sha256"

echo "3. Recording the table and row inventory"
row_counts >"${BEFORE}"
cat "${BEFORE}"

echo "3a. Recording the schema state (PR-20260908-R3-1)"
# The baseline the `destroy_attempted` banner compares against. Without it the
# operator has a report of the current state and nothing to read it against.
# It is also what decides whether the counts can answer at all: a baseline that
# recorded objects makes "every count is zero now" mean they are gone, and a
# baseline that recorded zero in every class means these reports cannot separate
# an intact schema from a recreated one -- which the banner states as an
# unresolved state rather than as an empty database. What it never establishes,
# at either uncertain stage, is that the transaction whose outcome is in question
# has finished -- that is step 0a's question, and an operator's to answer
# (PR-20260908-R5-1).
schema_state >"${SCHEMA_STATE_BEFORE}"
cat "${SCHEMA_STATE_BEFORE}"

echo "3b. Recording the privilege inventory (N-20)"
grant_inventory >"${GRANTS_BEFORE}"
# ---------------------------------------------------------------------------
# How many runtime roles, decided before which one -- finding DS-R8-1
# ---------------------------------------------------------------------------
# The previous shape was `RUNTIME_ROLE="$(detect_runtime_role | tr -d
# '[:space:]')"` followed by a test for a newline in RUNTIME_ROLE. `tr` had
# already deleted every newline, so the ambiguity branch **could never run**:
# two grantees `app` and `report` arrived as the single identifier `appreport`,
# the drill accepted it, dropped the schema, and only then failed when the grant
# template named a role that does not exist -- after the destructive step, with
# the database empty.
#
# Cardinality is therefore answered by **counting records**, not by inspecting a
# string the record separator has been deleted from.
#
# **And the records themselves survive the shell** (finding PR-20260907-R2-1).
# `$( )` strips trailing newlines and a line reader treats newlines as record
# boundaries, so a role name that *contains* a newline was silently changed or
# lost before the guard below ever saw it. The report is now `ROLE <hex>` lines
# and one `END <count>` terminator, in which no record can contain a separator
# and a missing terminator is detectable.
refuse_runtime_report() {
  # **Fixed text, and no catalog content** (PR-20260907-R2-1 item 3). What the
  # report said is not repeated here: an unreadable report is exactly the case in
  # which its bytes cannot be trusted to be a role name, a UTF-8 string, or free
  # of terminal control sequences.
  echo "Refusing to drill: the runtime-role report could not be read." >&2
  echo "Reason: $1." >&2
  echo "This is NOT taken as 'no runtime role holds table grants'. A report" >&2
  echo "that cannot be read says nothing about how many roles there are, and" >&2
  echo "restoring no table grants on that basis is finding N-20 with an extra" >&2
  echo "step. Resolve the client or catalog problem and re-run." >&2
  echo "Nothing was dropped or restored; the schema is intact and no" >&2
  echo "recovery is required. The dump taken in step 1 and the inventories" >&2
  echo "are in ${WORK_DIRECTORY}." >&2
  exit 2
}

# A client failure is a refusal, not an empty result. `if !` rather than a plain
# assignment so the reason is stated instead of inherited from `set -e`.
RUNTIME_ROLE_REPORT=""
if ! RUNTIME_ROLE_REPORT="$(detect_runtime_role)"; then
  refuse_runtime_report "the query did not complete"
fi

RUNTIME_ROLE_ROWS=()
#: The same records in their transported form, for diagnostics that must not
#: print arbitrary catalog bytes.
RUNTIME_ROLE_HEX_ROWS=()
RUNTIME_ROLE_DECLARED_TOTAL=""
RUNTIME_ROLE_TERMINATED=0
while IFS= read -r report_line; do
  # An empty line is never a record in this encoding -- every record is
  # `ROLE ` plus hexadecimal, and every terminator is `END ` plus digits -- so
  # skipping one drops no information at all. This is what the old
  # `[[ -n "${role_row}" ]] || continue` could not say: there, an empty line was
  # indistinguishable from a role whose name began with a newline.
  [[ -n "${report_line}" ]] || continue
  if (( RUNTIME_ROLE_TERMINATED == 1 )); then
    refuse_runtime_report "a record followed the terminator"
  fi
  case "${report_line}" in
    "ROLE "*)
      role_hex="${report_line#ROLE }"
      # Even length, lower-case hex only. Nothing else can decode to bytes.
      if [[ ! "${role_hex}" =~ ^([0-9a-f][0-9a-f])*$ ]]; then
        refuse_runtime_report "a role record was not hex encoded"
      fi
      # PR-20260908-R3-2: refused **before** `decode_hex_role`, because the
      # representation it decodes into cannot hold a NUL and would drop it
      # silently. The pair scan runs here, after the line above has established
      # that the record really is whole byte pairs.
      if hex_record_contains_nul "${role_hex}"; then
        refuse_runtime_report "a role record carried a NUL byte"
      fi
      decode_hex_role "${role_hex}"
      RUNTIME_ROLE_ROWS+=("${DECODED_ROLE}")
      RUNTIME_ROLE_HEX_ROWS+=("${role_hex}")
      ;;
    "END "*)
      RUNTIME_ROLE_DECLARED_TOTAL="${report_line#END }"
      if [[ ! "${RUNTIME_ROLE_DECLARED_TOTAL}" =~ ^[0-9]+$ ]]; then
        refuse_runtime_report "the terminator carried no record count"
      fi
      RUNTIME_ROLE_TERMINATED=1
      ;;
    *)
      refuse_runtime_report "the report carried a line that is neither a record nor the terminator"
      ;;
  esac
done <<<"${RUNTIME_ROLE_REPORT}"

# A truncated or empty report is unreadable, not empty. This is the check that
# stops a `psql` that printed nothing -- or was cut off part way -- from being
# read as a zero-row result.
if (( RUNTIME_ROLE_TERMINATED != 1 )); then
  refuse_runtime_report "the report carried no terminator"
fi
# Compared as strings: the count came from `count(*)::text` and an array length
# is plain decimal, so neither can carry a leading zero, and a string comparison
# cannot be surprised by one being read as octal.
if [[ "${#RUNTIME_ROLE_ROWS[@]}" != "${RUNTIME_ROLE_DECLARED_TOTAL}" ]]; then
  refuse_runtime_report "the report carried fewer or more records than it declared"
fi

# ---------------------------------------------------------------------------
# The supported runtime-role contract -- finding PR-20260907-2
# ---------------------------------------------------------------------------
# A regular expression over the characters of a name does not prove that the
# name means itself in SQL. Two things also have to hold, and neither did:
#
#   * **the unquoted spelling PostgreSQL parses must be the catalog name.**
#     PostgreSQL down-cases an unquoted identifier, so a catalog role
#     `MixedCase` becomes `mixedcase` in `GRANT ... TO MixedCase` -- a different
#     role, or none. The previous check accepted upper case.
#   * **the name must not already mean something else.** `GRANT ... TO select`
#     is a syntax error, `TO user` and `TO current_user` name the session's own
#     role, and `TO public` grants to every role in the cluster. All of them
#     match `^[A-Za-z_][A-Za-z0-9_]*$`.
#
# And the name checked must be the name the catalog holds: the previous shape
# trimmed surrounding whitespace *before* validating, so ` padded_role ` was
# repaired into a different identifier and then approved.
#
# The contract below is therefore narrow and identity-preserving, which is what
# the two supported runtime roles in this repository -- `freedom_runtime` and
# `freedom_runtime_test` -- already satisfy. Anything else refuses here, before
# the destroy, where a refusal costs nothing.
is_reserved_role_spelling() {
  case "$1" in
    # PostgreSQL reserved key words: none of these can be an unquoted
    # identifier, so a GRANT naming one is a syntax error, not a grant.
    all|analyse|analyze|and|any|array|as|asc|asymmetric|both|case|cast|check|\
collate|column|constraint|create|default|deferrable|desc|distinct|do|else|end|\
except|false|fetch|for|foreign|from|grant|group|having|in|initially|intersect|\
into|lateral|leading|limit|localtime|localtimestamp|not|null|offset|on|only|or|\
order|placing|primary|references|returning|select|some|symmetric|table|then|to|\
trailing|true|union|unique|using|variadic|when|where|window|with) return 0 ;;
    # Spellings that resolve to a role other than the one they appear to name.
    current_catalog|current_date|current_role|current_schema|current_time|\
current_timestamp|current_user|session_user|user|public) return 0 ;;
    # Reserved by PostgreSQL for its predefined roles. Re-granting one of these
    # is never what a drill should do.
    pg_*) return 0 ;;
    *) return 1 ;;
  esac
}

if (( ${#RUNTIME_ROLE_ROWS[@]} > 1 )); then
  # Before DRILL_STAGE="destroy_attempted" and before step 4, so this is a refusal and
  # not a recovery -- but it is *not* before everything, and saying so was
  # finding DS-R8-2. Steps 1 to 3b have run: the dump, its checksum and the two
  # read-only inventories are on disk. Nothing destructive has run.
  echo "Refusing to drill: more than one non-owner role holds table grants," >&2
  echo "so which one the runtime template should name is ambiguous. Resolve" >&2
  echo "that before rehearsing a restore that has to put them back." >&2
  # Hex encoded, deliberately. A catalog role name is arbitrary bytes -- it may
  # carry newlines, control characters or terminal escapes -- so the diagnostic
  # prints the transported form rather than pasting catalog content into an
  # operator's terminal (PR-20260907-R2-1 item 3).
  echo "Roles found: ${#RUNTIME_ROLE_ROWS[@]}, hex encoded:" \
       "${RUNTIME_ROLE_HEX_ROWS[*]}" >&2
  echo "Nothing was dropped or restored; the schema is intact and no recovery" >&2
  echo "is required. The dump taken in step 1 and the inventories are in" >&2
  echo "${WORK_DIRECTORY}." >&2
  exit 2
elif (( ${#RUNTIME_ROLE_ROWS[@]} == 0 )); then
  echo "    No runtime role holds table grants here; nothing to re-apply."
else
  # **Exactly as the catalog holds it.** Nothing is trimmed and nothing is
  # normalized: the value checked below is the value PostgreSQL stores, which is
  # the whole of finding PR-20260907-2.
  RUNTIME_ROLE="${RUNTIME_ROLE_ROWS[0]}"

  # The name is interpolated into a `sed` replacement and into unquoted SQL, so
  # it is validated here -- before the schema is dropped -- rather than trusted.
  #
  # The first test is the identity-preserving one and it is written without a
  # character range because ranges in a bracket expression are collation
  # dependent: `${var,,}` is a plain ASCII case fold and does not vary with the
  # operator's locale. It is what refuses `MixedCase`.
  #
  # The expression after it states the accepted shape: lower-case letters, an
  # underscore, then lower-case letters, digits and underscores, up to the
  # 63-byte NAMEDATALEN limit. That is narrower than PostgreSQL allows (`$` is a
  # legal identifier character, and a quoted role may contain anything at all)
  # and deliberately so: both supported runtime roles in this repository --
  # freedom_runtime, freedom_runtime_test -- have this shape, and every excluded
  # character is one that is special to `sed`'s replacement text, to the shell,
  # or to SQL. Surrounding whitespace is excluded by the same expression, so a
  # catalog name that carries it is refused rather than repaired.
  #
  # The third test is the one a regular expression cannot make: whether the name
  # still means an identifier once SQL parses it.
  if [[ "${RUNTIME_ROLE}" != "${RUNTIME_ROLE,,}" ]] \
     || [[ ! "${RUNTIME_ROLE}" =~ ^[a-z_][a-z0-9_]{0,62}$ ]] \
     || is_reserved_role_spelling "${RUNTIME_ROLE}"; then
    echo "Refusing to drill: the role holding table grants is not a supported" >&2
    echo "runtime role name. This drill renders the name into a grant template" >&2
    echo "and into unquoted SQL, so it accepts only a name whose unquoted SQL" >&2
    echo "spelling is the name PostgreSQL stores and whose literal meaning in" >&2
    echo "SQL is an identifier: lower case, no surrounding or embedded" >&2
    echo "whitespace, no reserved key word, no special role spelling, no pg_" >&2
    echo "prefix, at most 63 bytes. Upper case is refused because PostgreSQL" >&2
    echo "down-cases an unquoted identifier, so the grant would name a" >&2
    echo "different role or none at all." >&2
    echo "Nothing was dropped or restored; the schema is intact and no" >&2
    echo "recovery is required. The dump taken in step 1 and the inventories" >&2
    echo "are in ${WORK_DIRECTORY}." >&2
    exit 2
  fi
  echo "    Runtime role: ${RUNTIME_ROLE}"
fi

echo "3c. Recording the schema grants (DS-R2-1, DS-R3-1)"
schema_grants_sql >"${SCHEMA_GRANTS}"
sha256sum "${SCHEMA_GRANTS}" | tee "${SCHEMA_GRANTS}.sha256"

# ---------------------------------------------------------------------------
# 3d. Render the runtime grants **before** the destroy -- finding PR-20260907-1
# ---------------------------------------------------------------------------
# Rendered here rather than piped through `sed` into `psql` in step 5b, for two
# reasons that are the finding:
#
#   * **it survives the failure.** If the restore fails, the file is on disk,
#     checksummed, and already carries the exact role the pre-drill database
#     granted -- so the recovery procedure names a file rather than asking an
#     operator to work out a role from an empty database.
#   * **the two paths cannot diverge.** Step 5b applies this same file, so the
#     grants an operator re-applies during recovery are byte-for-byte the grants
#     the drill would have applied itself.
#
# The template's readability is checked here too. It used to be checked in step
# 5b -- *after* the schema was dropped -- so a missing template turned a
# recoverable state into one whose runtime grants could not be reconstructed
# from anything the drill had kept.
if [[ -n "${RUNTIME_ROLE}" ]]; then
  if [[ ! -r "${GRANT_TEMPLATE}" ]]; then
    echo "Refusing to drill: the runtime grant template" >&2
    echo "${GRANT_TEMPLATE} is missing or unreadable, so the privileges" >&2
    echo "'${RUNTIME_ROLE}' holds could not be restored after the destroy." >&2
    echo "Nothing was dropped or restored; the schema is intact and no" >&2
    echo "recovery is required. The dump taken in step 1 and the inventories" >&2
    echo "are in ${WORK_DIRECTORY}." >&2
    exit 2
  fi
  sed "s/__APP_ROLE__/${RUNTIME_ROLE}/g" "${GRANT_TEMPLATE}" >"${RUNTIME_GRANTS}"
  if grep -q '__APP_ROLE__' "${RUNTIME_GRANTS}"; then
    # Belt and braces: an unsubstituted placeholder would be a SQL error after
    # the destroy, which is the one place this drill must not discover a problem.
    echo "Refusing to drill: the rendered runtime grants still contain" >&2
    echo "__APP_ROLE__, so the substitution did not take. Nothing was dropped" >&2
    echo "or restored; the schema is intact and no recovery is required." >&2
    exit 2
  fi
  sha256sum "${RUNTIME_GRANTS}" | tee "${RUNTIME_GRANTS}.sha256"
else
  echo "    No runtime grants to render; none will be applied or recovered."
fi

echo "4. Destroying the schema to prove the restore, not the backup"
# **Two assignments, and the distinction between them is finding
# PR-20260908-R3-1.** `destroy_attempted` is set *before* the command because
# from this point on this drill may have destroyed something and must say so
# whatever happens next -- that is responsibility, not knowledge. `destroyed` is
# set *after* the command succeeds, like every other stage assignment in this
# script, because it is a claim about what the database now holds: dropped,
# recreated and empty, restore not started.
#
# Neither of them is a claim that the *server* has finished with the statement
# (PR-20260908-R5-1). If this client dies here, the backend may still be running
# the destroy, and the `destroy_attempted` banner's step 0a says so rather than
# reading the catalog as though the question were closed.
#
# Assigning `destroyed` before the command made the drill claim that knowledge
# for a command that failed, was refused, or whose result was lost -- and the
# `destroyed` banner then asserted an EMPTY database and prescribed a full
# restore on that basis.
DRILL_STAGE="destroy_attempted"
psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 \
     -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;' >/dev/null
DRILL_STAGE="destroyed"

echo "5. Restoring from the backup"
# The one genuinely uncertain outcome, and it is recorded as such rather than
# guessed at. Between these two assignments the restore has started and has not
# reported success: `--single-transaction --exit-on-error` makes an ordinary
# failure roll back to empty, but a killed process is not an ordinary failure and
# this script cannot see the difference. Nor can it see whether the restore is
# still running: --single-transaction publishes nothing until it commits, so an
# unfinished restore and a rolled-back one look identical from another session
# (PR-20260908-R5-1). The banner for this stage says so, asks whether the
# transaction has ended before it reads anything, and tells the operator how to
# find out.
DRILL_STAGE="restore_attempted"
"${RESTORE_COMMAND[@]}"
DRILL_STAGE="restored"

echo "5b. Re-applying the runtime grants the restore discarded (N-20, DS-R2-1)"
psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 -f "${SCHEMA_GRANTS}" >/dev/null
DRILL_STAGE="schema_grants_applied"
if [[ -n "${RUNTIME_ROLE}" ]]; then
  # The file step 3d rendered, which is the same file the recovery procedure
  # names. Applying a second, separately produced rendering here is how the
  # normal path and the printed recovery came to say different things
  # (PR-20260907-1).
  psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 -f "${RUNTIME_GRANTS}" >/dev/null
  echo "    Applied ${RUNTIME_GRANTS##*/} for ${RUNTIME_ROLE}"
else
  echo "    Skipped: no runtime role held grants before the destroy."
fi
# Reached whether or not there were runtime grants to apply: in the zero-role
# case there is nothing left to restore, so the resume point is the verification.
DRILL_STAGE="grants_applied"

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

DRILL_STAGE="verified"
echo "Restore verified for ${DATABASE}. Artefacts in ${WORK_DIRECTORY}"
