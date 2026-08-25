#!/usr/bin/env bash
#
# The one validation `setup-portal-host.sh` applies to an existing worker
# environment file, in a file that can be sourced and therefore tested.
#
# ## Why this is stricter than "does it say true"
#
# Codex finding C3, 2026-08-25. The first version of this check read the last
# `WORKER_ENABLED=` assignment and accepted the file if it said `true`. That is
# the wrong shape of check for this particular file, and the reason is the same
# systemd precedence rule that caused F5 in the other direction: the worker unit
# reads this file **after** the shared portal file, so **every** assignment in it
# overrides the portal's. A file like
#
#     WEB_DATABASE_URL=unexpected-database
#     WORKER_ARTIFACT_ROOT=/unexpected/path
#     WORKER_ENABLED=true
#
# passed the old check while silently redirecting the worker's database and
# artifact store. The file's whole purpose is to state one variable in the only
# place systemd will let it win, so anything else in it is either a mistake or an
# override nobody reviewed — and this script must not adopt it by saying nothing.
#
# The mode and ownership are checked for the same reason the artifact store's are
# (`root_permissive`, `root_not_owned`): a file the service account can write is a
# file the service account can use to reconfigure itself, and a symlink is a file
# whose content is decided somewhere else entirely.
#
# ## Contract
#
#   worker_env_file_problem <path> <expected_owner> <expected_group> <expected_mode>
#
# Prints one sentence describing the first problem found and returns 1, or prints
# nothing and returns 0 when the file conforms exactly. It reads; it never writes,
# never repairs and never deletes. The expected owner, group and mode are
# parameters rather than constants so the caller states its own contract — and so
# the check can be exercised by a test that is not root.

#: The complete permitted content, final newline included. The policy is explicit
#: rather than incidental: exactly one assignment, terminated by one newline.
WORKER_ENV_FILE_CONTENT='WORKER_ENABLED=true
'

worker_env_file_problem() {
    local path="$1" expected_owner="$2" expected_group="$3" expected_mode="$4"

    # `-L` before `-f`, because `-f` follows the link and would answer for the
    # target: the question here is what this path *is*, not what it points at.
    if [ -L "$path" ]; then
        printf 'is a symbolic link. This file is read by systemd as root; its content must not be decided by whatever the link resolves to today.\n'
        return 1
    fi
    if [ ! -e "$path" ]; then
        printf 'does not exist.\n'
        return 1
    fi
    if [ ! -f "$path" ]; then
        printf 'is not a regular file.\n'
        return 1
    fi

    local observed
    observed="$(stat -c '%U %G %a' "$path" 2>/dev/null)" || {
        printf 'could not be inspected with stat.\n'
        return 1
    }
    local expected="${expected_owner} ${expected_group} ${expected_mode}"
    if [ "$observed" != "$expected" ]; then
        printf 'is owned/permissioned %s, and must be %s. A file the service account can write is a file the service account can use to reconfigure itself.\n' \
            "$observed" "$expected"
        return 1
    fi

    # Byte-exact, trailing newlines included. A command substitution alone would
    # strip them and quietly accept a file with none, or with three.
    local content
    content="$(cat "$path"; printf x)" || {
        printf 'could not be read.\n'
        return 1
    }
    content="${content%x}"
    if [ "$content" != "$WORKER_ENV_FILE_CONTENT" ]; then
        printf 'does not contain exactly one line reading WORKER_ENABLED=true. The worker unit reads this file after the shared portal file, so every assignment in it overrides the portal configuration — an extra variable here is an unreviewed override, and a WORKER_ENABLED that is not true is F5 reinstated.\n'
        return 1
    fi
    return 0
}
