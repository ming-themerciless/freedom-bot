#!/usr/bin/env bash
#
# Publish the temporary test site through Caddy, safely.
# Authored 2026-08-23 by P3.5 (procedure SP-05).
#
#   sudo bash infra/staging/enable-test-site.sh
#
# This is the one action on this host with a blast radius onto the three live
# Foundry sites, so it is written to be undoable at every step:
#
#   1. it backs up /etc/caddy/Caddyfile with a timestamp before touching it;
#   2. it only ever *adds* an import line — no existing block is edited;
#   3. it validates the complete configuration before reloading; and
#   4. if validation fails it restores the backup and stops, having changed
#      nothing that Caddy is running.
#
# Undo at go-live: delete the import line, delete the site file, reload.

set -euo pipefail

REPO_ROOT="/opt/freedom-blades/platform"
SITE_SOURCE="${REPO_ROOT}/infra/caddy/freedom-blades-test.caddy"
SITE_TARGET="/etc/caddy/freedom-blades-test.caddy"
CADDYFILE="/etc/caddy/Caddyfile"
IMPORT_LINE="import ${SITE_TARGET}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="${CADDYFILE}.before-test-site-${STAMP}"

say()  { printf '  %s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
die()  { printf '\nREFUSED: %s\n' "$*" >&2; exit 1; }

step "Preflight"
[ "$(id -u)" -eq 0 ] || die "run this with sudo."
[ -f "$SITE_SOURCE" ] || die "$SITE_SOURCE is missing."
[ -f "$CADDYFILE" ] || die "$CADDYFILE is missing."
command -v caddy >/dev/null || die "caddy is not installed."
systemctl is-active --quiet caddy || die "caddy is not running; fix that first."
say "caddy is running and the configuration is present."

step "Backup"
cp -a "$CADDYFILE" "$BACKUP"
say "saved $BACKUP"

step "Install the site file"
install -o root -g root -m 0644 "$SITE_SOURCE" "$SITE_TARGET"
say "installed $SITE_TARGET"

step "Add the import"
if grep -qF "$IMPORT_LINE" "$CADDYFILE"; then
    say "(already imported) no change to $CADDYFILE"
else
    printf '\n# Temporary Freedom Blades test site (P3.5). Remove at go-live.\n%s\n' \
        "$IMPORT_LINE" >> "$CADDYFILE"
    say "appended the import line"
fi

step "Validate before reloading"
if ! caddy validate --config "$CADDYFILE" --adapter caddyfile 2>/tmp/caddy-validate.$$; then
    printf '\n  Validation FAILED. Restoring the previous configuration.\n'
    sed -n '$p;/Error/p' /tmp/caddy-validate.$$ | head -5
    cp -a "$BACKUP" "$CADDYFILE"
    rm -f "$SITE_TARGET" /tmp/caddy-validate.$$
    die "nothing was reloaded; Caddy is still serving what it was before."
fi
rm -f /tmp/caddy-validate.$$
say "the complete configuration is valid."

step "Reload"
systemctl reload caddy
say "reloaded."

step "Verify every site still answers"
failed=0
for host in foundry1.rpgworld.org foundry2.rpgworld.org foundry3.rpgworld.org \
            freedom-blades.rpgworld.org freedom-blades-test.rpgworld.org; do
    code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 -k \
            --resolve "${host}:443:127.0.0.1" "https://${host}/" || echo 000)"
    printf '  %-36s %s\n' "$host" "$code"
    case "$host:$code" in
        # 401 is the expected answer for the test site: the password gate is in
        # front of it until go-live.
        freedom-blades-test.rpgworld.org:401) ;;
        *:000|*:5??) failed=1 ;;
    esac
done
[ "$failed" -eq 0 ] || die "a site stopped answering. Restore with: cp -a '$BACKUP' '$CADDYFILE' && systemctl reload caddy"

step "Done"
cat <<SUMMARY

  https://freedom-blades-test.rpgworld.org/        the portal (password protected)
  https://freedom-blades-test.rpgworld.org/enrol   the passkey registration page

  Backup of the previous configuration: $BACKUP

SUMMARY
