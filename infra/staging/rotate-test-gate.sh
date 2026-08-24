#!/usr/bin/env bash
#
# Generate and install the temporary test site's Basic Auth gate.
# (C35-01, R35-08, R35-13, R35-14)
#
#   sudo bash infra/staging/rotate-test-gate.sh
#
# Rotation is MANDATORY: the previous verifier was committed to a repository
# artifact and read during review, and the first two versions of this script
# could not run at all, so the gate has never actually been rotated.
#
# The password is printed **once**, only after the gate it describes is serving,
# and is written nowhere else — not to argv, a file, a log or a backup.
#
# ## This is a transaction, because a half-done rotation is worse than none
#
# Three states, and every exit path knows which one it is in:
#
#   none       nothing of ours is on disk
#   candidate  the new fragment is installed but NOT yet active
#   committed  Caddy has validated and reloaded it; it is the live gate
#
# Rollback restores the exact pre-run state from `none` and `candidate`, and is a
# no-op once `committed`. It runs on ordinary failure, on `EXIT`, and on `INT` and
# `TERM` — the last two being the case review caught: a signal after the atomic
# `mv` previously left an unvalidated verifier on disk whose password had never
# been shown, and a later unrelated reload would have activated an unknown gate.
#
# The rollback copy is transaction-owned and always removed. It is deliberately
# **not** the retained recovery generation: a failed attempt must not leave
# credential material behind merely because it ran (R35-14).
#
# ## Two earlier defects, kept written down
#
# `tr -dc … | head -c 20` exits 141 under `pipefail` — `head` closes the pipe and
# `tr` dies of SIGPIPE. Generation now reads one finite block so every stage sees
# EOF, and the substring is taken in the shell.
#
# `caddy hash-password --plaintext "$PW"` puts the plaintext in argv. It is fed on
# stdin instead, newline-terminated: verified by running it, the terminator is
# required (without it Caddy fails `Error: EOF`) and is stripped rather than
# hashed.

set -euo pipefail

FRAGMENT="${FREEDOM_GATE_FRAGMENT:-/etc/caddy/freedom-blades-test.gate}"
CADDYFILE="${FREEDOM_GATE_CADDYFILE:-/etc/caddy/Caddyfile}"
USERNAME="${FREEDOM_GATE_USERNAME:-peter}"
PASSWORD_LENGTH=20

GATE_DIR="$(dirname -- "$FRAGMENT")"
GATE_NAME="$(basename -- "$FRAGMENT")"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

STATE="none"          # none | candidate | committed
ROLLBACK_COPY=""      # transaction-owned; never a retained generation
CANDIDATE=""          # staged file before it is moved into place
HAD_FRAGMENT="no"
ROLLED_BACK="no"
PASSWORD=""
VERIFIER=""

die() { printf '\nREFUSED: %s\n' "$*" >&2; exit 1; }

# Idempotent: nested failure inside rollback must not re-enter it.
rollback() {
    [ "$ROLLED_BACK" = "yes" ] && return 0
    ROLLED_BACK="yes"

    [ -n "$CANDIDATE" ] && [ -e "$CANDIDATE" ] && rm -f -- "$CANDIDATE"

    if [ "$STATE" = "candidate" ]; then
        if [ "$HAD_FRAGMENT" = "yes" ] && [ -n "$ROLLBACK_COPY" ] && [ -e "$ROLLBACK_COPY" ]; then
            # Atomic: the restore is a rename within the gate's own directory.
            local restoring="${FRAGMENT}.restoring.$$"
            cp -a -- "$ROLLBACK_COPY" "$restoring"
            mv -f -- "$restoring" "$FRAGMENT"
        else
            rm -f -- "$FRAGMENT"
        fi
        STATE="none"
    fi

    [ -n "$ROLLBACK_COPY" ] && [ -e "$ROLLBACK_COPY" ] && rm -f -- "$ROLLBACK_COPY"
    PASSWORD=""; VERIFIER=""
    return 0
}

# `$?` is captured first so rollback cannot mask the failure that triggered it.
on_exit() { local status=$?; rollback; exit "$status"; }
on_signal() { local status=$1; rollback; exit "$status"; }

trap on_exit EXIT
trap 'on_signal 130' INT
trap 'on_signal 143' TERM

# --------------------------------------------------------------------------
# Preflight
# --------------------------------------------------------------------------
[ "$(id -u)" -eq 0 ] || die "run this with sudo."
command -v caddy >/dev/null || die "caddy is not installed."
command -v systemctl >/dev/null || die "systemctl is not available."
[ -f "$CADDYFILE" ] || die "$CADDYFILE does not exist."
[ -d "$GATE_DIR" ] || die "$GATE_DIR does not exist."

CADDY_GROUP="$(systemctl show caddy -p Group --value 2>/dev/null || true)"
[ -n "$CADDY_GROUP" ] || CADDY_GROUP="caddy"
getent group "$CADDY_GROUP" >/dev/null || die "the '${CADDY_GROUP}' group does not exist."

# --------------------------------------------------------------------------
# Generate — finite reads only
# --------------------------------------------------------------------------
POOL="$(head -c 512 /dev/urandom | base64 | LC_ALL=C tr -dc 'A-Za-z0-9')"
[ "${#POOL}" -ge "$PASSWORD_LENGTH" ] || die "could not gather ${PASSWORD_LENGTH} characters of entropy."
PASSWORD="${POOL:0:$PASSWORD_LENGTH}"
POOL=""

VERIFIER="$(printf '%s\n' "$PASSWORD" | caddy hash-password | tail -1)"
case "$VERIFIER" in
    \$2*\$*) ;;
    *) die "the hashing command did not return a verifier." ;;
esac

# --------------------------------------------------------------------------
# Install the candidate
# --------------------------------------------------------------------------
CANDIDATE="${GATE_DIR}/.${GATE_NAME}.candidate.$$"
( umask 077; printf 'basic_auth {\n\t%s %s\n}\n' "$USERNAME" "$VERIFIER" > "$CANDIDATE" )
VERIFIER=""
chown root:"$CADDY_GROUP" "$CANDIDATE"
chmod 640 "$CANDIDATE"

if [ -f "$FRAGMENT" ]; then
    HAD_FRAGMENT="yes"
    ROLLBACK_COPY="${GATE_DIR}/.${GATE_NAME}.rollback.$$"
    cp -a -- "$FRAGMENT" "$ROLLBACK_COPY"
fi

mv -f -- "$CANDIDATE" "$FRAGMENT"
CANDIDATE=""
STATE="candidate"

# --------------------------------------------------------------------------
# Validate, then reload. Rollback owns every failure from here.
# --------------------------------------------------------------------------
caddy validate --config "$CADDYFILE" --adapter caddyfile >/dev/null 2>&1 \
    || die "the configuration did not validate. The previous gate is back in place, nothing was reloaded, and the new password was discarded unused."

systemctl reload caddy >/dev/null 2>&1 \
    || die "the reload failed. The previous gate has been restored on disk and the new password was discarded unused. Caddy is still running its previously loaded configuration, so the OLD password remains active. Investigate with: systemctl status caddy"

# --------------------------------------------------------------------------
# Committed. Rollback is now a no-op, and the statement below is true.
# --------------------------------------------------------------------------
STATE="committed"

# **Displayed before any further work** (R35-19). Everything after the reload is
# housekeeping, and every step of it can fail: a rename, an enumeration, a sort, a
# removal. Under `set -e` a failure there would have exited the script with the new
# gate *already serving* and its plaintext never shown — locking the operator out
# of a door only they were supposed to hold the key to. Nothing fallible may stand
# between a confirmed reload and this message.
cat <<SUMMARY

  The test site's password has been replaced and is active.

    username: ${USERNAME}
    password: ${PASSWORD}

  Written nowhere else. Copy it now; this is the only time it is shown.
  Anyone who held the previous password no longer has access.

SUMMARY
PASSWORD=""

# --------------------------------------------------------------------------
# Housekeeping. Best effort by design: the password is already shown, the gate is
# already serving, and a tidy-up failure must not look like a rotation failure.
# --------------------------------------------------------------------------
# `set -e` is suspended for this block and restored immediately after. Each step
# reports for itself, and none of them can change which password is active.
housekeeping_faults=""
note_fault() { housekeeping_faults="${housekeeping_faults:+${housekeeping_faults}, }$1"; }
set +e

# Each step is a controlled operation with its own status, never a pipeline whose
# failure source cannot be told apart (R35-28). The warnings name the *class* of
# operation and the gate directory — never a verifier, never a password.

if [ "$HAD_FRAGMENT" = "yes" ] && [ -n "$ROLLBACK_COPY" ] && [ -e "$ROLLBACK_COPY" ]; then
    mv -f -- "$ROLLBACK_COPY" "${GATE_DIR}/${GATE_NAME}.replaced-${STAMP}"
    [ $? -eq 0 ] || note_fault "retaining the previous gate as a recovery generation"
fi
if [ -n "$ROLLBACK_COPY" ] && [ -e "$ROLLBACK_COPY" ]; then
    rm -f -- "$ROLLBACK_COPY"
    [ $? -eq 0 ] || note_fault "removing the transaction's rollback copy"
fi
ROLLBACK_COPY=""

# Enumeration and selection are separated so a failure in either is attributable.
generations="$(find "$GATE_DIR" -maxdepth 1 -type f -name "${GATE_NAME}.replaced-*" 2>/dev/null)"
if [ $? -ne 0 ]; then
    note_fault "enumerating retained generations"
else
    stale_generations="$(printf '%s\n' "$generations" | sort -r | tail -n +2)"
    if [ $? -ne 0 ]; then
        note_fault "selecting which retained generations to prune"
    else
        while IFS= read -r stale; do
            [ -n "$stale" ] || continue
            rm -f -- "$stale"
            [ $? -eq 0 ] || note_fault "removing a superseded generation"
        done <<STALE
$stale_generations
STALE
    fi
fi

set -e

if [ -n "$housekeeping_faults" ]; then
    # A warning, not a rotation failure, and explicitly not a reason to doubt the
    # password above. Names the operation class only — no verifier, no password,
    # and the password is never printed a second time.
    printf '  WARNING: post-commit housekeeping did not complete: %s.\n' "$housekeeping_faults" >&2
    printf '  The password shown above IS active and correct. This is tidy-up only.\n' >&2
    printf '  Superseded verifier generations may remain in %s; remove them when convenient.\n\n' "$GATE_DIR" >&2
fi
