# Freedom Blades filesystem-layout migration

Status: executed and verified · Date: 2026-08-25 · Owner: Operations Owner

This controlled maintenance change replaces the legacy `/opt/discord-bots`,
`/srv/freedom`, and `/etc/freedom-web` product paths. It does not rename systemd
services, databases, roles, Linux accounts, DNS names, or the Git remote.

## Target layout

```text
/opt/freedom-blades/
├── platform/                  Git repository
├── runtime/
│   ├── venv-bot/
│   └── venv-web/
├── reference/actor-exports/  offline Foundry reference; outside Git
└── workspace/{review,tmp}/   disposable engineering work

/srv/freedom-blades/{snapshots,web}/
/etc/freedom-blades/{portal.env,worker.env}
```

Persistent artifacts remain under `/srv`; secrets remain under `/etc`. Account
state such as `.ssh`, `.cache`, `.claude`, `.codex`, and `.agents` is not product
content and must not be moved into the product tree.

## Preconditions

1. Identify the preparation commit and require a clean tree.
2. Run focused path/deployment checks and the full available suites.
3. Record current unit files, Caddy configuration, service states, and target
   directory absence. Refuse rather than merge any unexpected target.
4. Confirm PostgreSQL is healthy and no import/apply job is running.
5. Obtain the Operations Owner's maintenance authorization.

## Prepare before downtime

Create fresh virtual environments. Do not move the old ones: their entry-point
shebangs embed their old absolute paths.

```bash
install -d -o foundry -g nogroup -m 2775 /opt/freedom-blades
install -d -o foundry -g nogroup -m 2775 /opt/freedom-blades/runtime
install -d -o foundry -g foundry -m 0755 /opt/freedom-blades/reference
install -d -o foundry -g foundry -m 0700 /opt/freedom-blades/workspace

python3 -m venv /opt/freedom-blades/runtime/venv-bot
python3 -m venv /opt/freedom-blades/runtime/venv-web
/opt/freedom-blades/runtime/venv-bot/bin/pip install -U pip
/opt/freedom-blades/runtime/venv-bot/bin/pip install \
  -r /opt/discord-bots/freedom-bot/requirements.txt
/opt/freedom-blades/runtime/venv-web/bin/pip install -U pip
/opt/freedom-blades/runtime/venv-web/bin/pip install \
  -r /opt/discord-bots/freedom-bot/requirements-web.txt
```

Verify imports and focused tests through both new interpreters before downtime.

## Cutover

Record which services are active, then stop only the Freedom Blades processes:

```bash
systemctl is-active freedom-bot freedom-web freedom-worker
systemctl stop freedom-bot freedom-web freedom-worker
```

Each target below must be absent. These are same-host renames; do not replace them
with copy-and-delete or merge directory trees.

```bash
mv /opt/discord-bots/freedom-bot /opt/freedom-blades/platform
mv /opt/discord-bots/foundry-actor-exports \
   /opt/freedom-blades/reference/actor-exports
mv /srv/freedom /srv/freedom-blades
mv /etc/freedom-web /etc/freedom-blades

ln -sfnT /opt/freedom-blades/runtime/venv-bot \
         /opt/freedom-blades/platform/venv
ln -sfnT /opt/freedom-blades/runtime/venv-web \
         /opt/freedom-blades/platform/venv-web
```

The repository-local links retain established development commands while the
actual environments live under `runtime/`.

The moved environment file is deliberately preserved byte-for-byte by the host
setup script. Update only its legacy service-data path prefix, without printing
the file or changing credential values, then restore its required metadata:

```bash
sed -i 's|/srv/freedom/|/srv/freedom-blades/|g' \
  /etc/freedom-blades/portal.env
chown root:freedomweb /etc/freedom-blades/portal.env
chmod 0640 /etc/freedom-blades/portal.env
```

Regenerate active configuration from the moved repository:

```bash
FORCE_UNITS=1 bash \
  /opt/freedom-blades/platform/infra/staging/setup-portal-host.sh
install -o root -g root -m 0644 \
  /opt/freedom-blades/platform/infra/systemd/freedom-bot.service.tmpl \
  /etc/systemd/system/freedom-bot.service
systemctl daemon-reload
bash /opt/freedom-blades/platform/infra/staging/enable-test-site.sh
```

## Verification

```bash
systemd-analyze verify /etc/systemd/system/freedom-{bot,web,worker}.service
systemctl start freedom-bot freedom-web freedom-worker
systemctl is-active freedom-bot freedom-web freedom-worker
systemctl show -p WorkingDirectory -p ExecStart \
  freedom-bot freedom-web freedom-worker
systemctl show -p EnvironmentFiles freedom-worker
journalctl -u freedom-bot -u freedom-web -u freedom-worker -n 100 --no-pager
curl --fail --silent http://127.0.0.1:8001/v1/auth/emergency >/dev/null
curl --silent --output /tmp/freedom-health.json --write-out '%{http_code}\n' \
  http://127.0.0.1:8001/healthz
sha256sum -c \
  /opt/freedom-blades/platform/adapters/web/static/asset-integrity.sha256
```

Success requires no active unit or Caddy directive naming `/opt/discord-bots`,
both portal processes using `runtime/venv-web`, the bot using `runtime/venv-bot`,
configuration under `/etc/freedom-blades`, service data under
`/srv/freedom-blades`, all three expected services active, and no S-11 refusal.
`worker_heartbeat` is not worker-process liveness evidence.

## Rollback

Stop the three services; restore the backed-up units and Caddy files; remove only
the two repository-local virtual-environment symlinks; move the four renamed
trees back to their exact legacy locations, refusing if any destination exists;
reload systemd and Caddy; then start only the services active before cutover and
repeat the service, journal, endpoint, and integrity checks.

The fresh target virtual environments contain no secrets or authoritative data
and may remain stopped for diagnosis.

## Cleanup after observation

Only after the Operations Owner records a successful cutover and releases the
rollback hold:

- remove obsolete virtual environments and disposable review trees under
  `/opt/discord-bots`;
- remove `/opt/discord-bots` only after it contains no product/runtime content;
- update backup and monitoring inventories; and
- record deployed commit, service start times, and final directory inventory.
