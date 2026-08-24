#!/usr/bin/env bash
#
# Run one portal operator command with the service's own identity and settings.
# Authored 2026-08-23 by P3.5.
#
#   sudo bash infra/staging/portal-run.sh -m tools.webauthn_registration --operator "…" …
#   sudo bash infra/staging/portal-run.sh -m tools.webauthn_enrollment list --operator "…"
#   sudo bash infra/staging/portal-run.sh -m tools.portal_kill_switch status
#
# ## Why a wrapper rather than a command line
#
# Three things have to be true at once, and each is easy to get wrong on its own:
#
#   1. **the working directory must be the repository**, or `python -m tools.…`
#      cannot find the `tools` package at all;
#   2. **the settings must be the service's**, because these commands validate the
#      whole configuration graph — a command run with two hand-typed variables
#      gets a page of refusals about the forty it was not given; and
#   3. **the identity must be the service account**, because the database uses
#      peer authentication over the Unix socket: `freedomweb` is a PostgreSQL
#      role and `root` is not, so running these as root fails to connect.
#
# `systemd-run` is used rather than `sudo -u … env …` because it reads the
# environment file itself, with systemd's own parsing. Passing secrets through a
# shell expansion would put them in the process table and in the shell's history,
# and would mangle any value containing a shell metacharacter.

set -euo pipefail

REPO_ROOT="/opt/discord-bots/freedom-bot"
ENV_FILE="/etc/freedom-web/portal.env"
SERVICE_USER="freedomweb"
PYTHON="${REPO_ROOT}/venv-web/bin/python"

die() { printf '\nREFUSED: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run this with sudo — it has to drop to the service account."
[ -f "$ENV_FILE" ] || die "$ENV_FILE is missing; run setup-portal-host.sh first."
[ -x "$PYTHON" ] || die "the portal virtualenv is missing."
getent passwd "$SERVICE_USER" >/dev/null || die "the ${SERVICE_USER} account does not exist."
[ "$#" -gt 0 ] || die "give it a command, for example: -m tools.webauthn_enrollment list --operator \"…\""

# --pipe --wait so the command's own output and exit status are yours, not a
# unit's. --collect so a failed run leaves no residue in systemd's journal state.
exec systemd-run \
    --quiet --pipe --wait --collect \
    --uid="$SERVICE_USER" \
    --property=EnvironmentFile="$ENV_FILE" \
    --working-directory="$REPO_ROOT" \
    "$PYTHON" "$@"
