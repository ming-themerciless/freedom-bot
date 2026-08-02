# Local, Staging and Production Topology

Status: Phase 0 deliverable — **accepted 2026-07-30 after maintainer and
independent Codex review**

Plan §14.1 requires three environments: development (synthetic data), staging
(production-like, separate credentials and database) and production. Today only
production exists.

This document records the **observed** production topology and proposes the
development and staging ones. Nothing here was changed; no service was restarted
or reconfigured.

## 1. Observed production topology

Gathered from process/socket inspection, systemd unit templates, the Caddy
configuration and Foundry manifests. **Ports, hostnames and paths are recorded;
no credential was read.**

```text
                          Internet
                             │ 443
                             ▼
                     ┌───────────────┐
                     │     Caddy     │  TLS: Cloudflare origin certs
                     │   :80 :443    │  admin API on 127.0.0.1:2019
                     └───────┬───────┘
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   foundry1.rpgworld  foundry2.rpgworld  foundry3.rpgworld
     127.0.0.1:30001    127.0.0.1:30002    127.0.0.1:30003
   (node, user foundry — three separate Foundry VTT instances)

   ┌──────────────────────────────────────────────────────┐
   │ freedom-bot        systemd, user discordbot          │
   │   /opt/discord-bots/venv/bin/python main.py          │
   │   WorkingDirectory /opt/discord-bots/freedom-bot     │
   │   outbound only: Discord Gateway, Google Sheets API   │
   └──────────────────────────────────────────────────────┘
```

| Component | Bind | Public | User | Managed by |
|---|---|---|---|---|
| Caddy | `:80`, `:443` | yes | — | system |
| Caddy admin API | `127.0.0.1:2019` | no | — | system |
| Foundry ×3 | `*:30001-30003` | via Caddy | `foundry` | not systemd-templated in this repo |
| `freedom-bot` | none (outbound only) | no | `discordbot` | `infra/systemd/freedom-bot.service.tmpl` |
| PostgreSQL | — | — | — | **does not exist yet** |

### Findings

**F-1 — Foundry binds to all interfaces.** The three instances listen on `*`
(`0.0.0.0`), not loopback, while Caddy proxies them from `127.0.0.1`. Unless a
host firewall blocks 30001–30003, they are reachable directly, bypassing Caddy
and its TLS. Worth a maintainer check ([OD-25](../discovery/open-decisions.md)).

**F-2 — Three instances, but ONE shared world.** *Corrected 2026-07-30 after a
maintainer answer; the original Phase 0 reading was wrong.* The three instances do
**not** hold three copies of `the-guild`. `/home/foundry/shared/worlds` is
bind-mounted onto each instance's `foundrydata/Data/worlds`, so all three see the
same directory. Verified: all three paths to `the-guild` resolve to **inode
4388511 on device 64769** — one directory, three views. `/etc/fstab` declares the
binds explicitly.

There is therefore no stale-copy risk and no authoritative instance to choose:
**the world is the identity, and the instance is only a transport endpoint.**
[OD-12](../discovery/open-decisions.md) is resolved on that basis.

What *is* per-instance: the Foundry binary (`/home/foundry/foundryN/foundry/`),
the game system and the modules (`/home/foundry/dist/foundryN/{systems,modules}`
are bound in separately, one tree per instance). All three currently run core
**14.365** and `dnd5e` **5.3.3**, but they are independently upgradable, which is
why the connector still validates a **(core, system)** tuple per request even
though there is only one world.

See [foundry-mapping.md §3](../discovery/foundry-mapping.md#3-topology-one-shared-world-behind-three-instances).

**F-2a — LevelDB is single-writer, so only one instance can host the world at a
time.** Foundry opens the world's LevelDB stores when the world is launched, and
LevelDB takes an exclusive lock. On this local ext4 bind mount the lock is
effective, so the failure mode is *"the second instance refuses to launch
`the-guild`"* — not data corruption. Two consequences:

1. Whoever launches the world must know it is live elsewhere; the error is
   otherwise puzzling.
2. The connector's endpoint is *whichever instance currently hosts the world*, so
   configuration must be able to point at a different port without any change to
   world or actor identity. It must not assume port 30001.

**F-3 — The bot's systemd unit lacks standard hardening.** The `freedom-bot`
unit does not set `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem` or
`ProtectHome`, despite holding the Discord token and Google service-account key.
Adding them is a small, low-risk change proposed for Phase 1.

**F-4 — The unit's `User=discordbot` does not match the file owner.** The
repository is owned by `foundry:discordbot`. Group access is what makes this work;
worth confirming intentional.

**F-5 — No secrets management.** `.env` is a plain file read by `python-dotenv` at
import (`config.py:9`). The service account key lives in it as a single-line JSON
string. This is acceptable for one bot on one host; it does not scale to a web
app, a worker and a database URL. Phase 1 should move to systemd
`EnvironmentFile=` with `0600` permissions at minimum, or a credential store.

**F-6 — No shared venv isolation.** The bot runs from `/opt/discord-bots/venv`,
one directory above the repository and symlinked in as `venv`. A second Python
service sharing that venv would couple their dependency sets. `freedom-web` needs
its own.

## 2. Proposed development topology

Everything local, everything synthetic, nothing touching a live service.

```text
Developer workstation
├── PostgreSQL 16          localhost:5432   database freedom_dev
├── PostgreSQL 16 (test)   localhost:5432   database freedom_test  (recreated per run)
├── freedom-web            localhost:8000   uvicorn --reload
├── freedom-bot            optional, against a private test Discord guild
└── pytest                 fakes for Discord, Sheets and Foundry
```

**Rules for development**

1. **Never point a development environment at the production Sheet, the
   production Discord guild, or any live Foundry instance.** `.env.example` gains
   an explicit warning.
2. `freedom_test` is dropped and recreated by the test run, so migrations are
   exercised from empty on every run — plan §12 Phase 1's *"migrations apply to an
   empty database"*.
3. A developer who needs a Discord gateway uses a **private test guild** with its
   own bot application and its own snowflakes.
4. Data comes from `tests/fixtures/` (see
   [fixture-strategy.md](../discovery/fixture-strategy.md)).

**PostgreSQL for development** — either a local package install or a container.
The container form keeps the version pinned to production and is trivial to
reset:

```bash
docker run --rm -d --name freedom-pg \
  -e POSTGRES_PASSWORD=devonly \
  -e POSTGRES_DB=freedom_dev \
  -p 5432:5432 postgres:16
```

`devonly` is a development-only password on a loopback-bound container. It must
never appear in a staging or production configuration.

## 3. Proposed staging topology

Production-like, with its **own** credentials, database, Discord application and
Foundry world. Plan §14.1.

```text
staging.<domain>
      │ 443
      ▼
   Caddy (staging site block, or a separate host)
      │
      ├── freedom-web-staging   127.0.0.1:8001
      ├── freedom-bot-staging   → staging Discord guild, staging bot token
      └── PostgreSQL            freedom_staging, restricted role, loopback only
```

**Non-negotiable separations**

| Resource | Requirement |
|---|---|
| Database | Separate database **and** separate role. Not a schema in the production database |
| Discord | Separate bot application, separate guild, separate role IDs |
| Google | If Sheets is exercised at all, a **copy** of the sheet and a separate service account — never the production sheet |
| Foundry | A separate world, and preferably a fourth instance. **Never** the authoritative `the-guild` |
| Secrets | Independently generated. No value shared with production |
| Backups | Staging is never restored *into* production |

Staging exists to rehearse migrations and cutovers. A staging component that can
reach a production resource cannot do that safely, because a rehearsal mistake
becomes a production incident.

**Decision 2026-07-30:** staging shares this host ([OD-22](../discovery/open-decisions.md)).
The maintainer accepted the additional configuration risk to avoid the cost of a
second server. The separations above are therefore enforcement requirements, not
recommendations. Staging services use distinct Unix service names, environment
files and loopback ports; database ownership and login roles are distinct; a
staging service must not receive any production credential or endpoint.

## 4. Proposed production topology after Phase 3

```text
                          Internet
                             │ 443
                             ▼
                     ┌───────────────┐
                     │     Caddy     │  + security headers, rate limits
                     └───────┬───────┘
          ┌──────────────────┼──────────────┬──────────────┐
          ▼                  ▼              ▼              ▼
   foundry1..3        freedom-web    (future) worker   static assets
   :30001-30003      127.0.0.1:8000
                             │
                             ▼
                  ┌─────────────────────┐
                  │    PostgreSQL       │  127.0.0.1:5432, loopback only
                  │  restricted app role│  encrypted backups, tested restore
                  └─────────▲───────────┘
                            │
                     freedom-bot (systemd)
```

**Changes from today**

| # | Change | Source |
|---|---|---|
| 1 | PostgreSQL, loopback-bound, restricted application role | plan §9.3 |
| 2 | `freedom-web` unit, own venv, bound to `127.0.0.1:8000` | ADR 0002 |
| 3 | Caddy site block for the web app, with HSTS, CSP and security headers | plan §9.2 |
| 4 | Rate limits on authentication and sensitive endpoints | plan §9.2 |
| 5 | Encrypted, off-host, **restore-tested** backups | plan §14.3 |
| 6 | Systemd hardening on `freedom-bot` (F-3) | §1 |
| 7 | Secrets via `EnvironmentFile=` at `0600`, or a credential store (F-5) | plan §9.3 |
| 8 | Structured logging with correlation IDs, no tokens or player data | `.agents/AGENTS.md` |

**Deliberately not added:** `freedom-worker`. Plan §5.3 — introduce a durable
worker only for a concrete need such as imports, sync or large settlements.
Phase 2's importer is the first candidate, and even that can run as a one-shot
command initially.

## 5. Configuration contract changes

`.env.example` must stay current (`.agents/AGENTS.md`). Phases 1 and 3 add:

```bash
# ==== Environment ====
ENVIRONMENT=development          # development | staging | production

# ==== Database ====
DATABASE_URL=postgresql+psycopg://freedom_app:__PASSWORD__@127.0.0.1:5432/freedom_dev

# ==== Web ====
WEB_BIND_HOST=127.0.0.1
WEB_BIND_PORT=8000
PUBLIC_BASE_URL=https://__YOUR_DOMAIN__
SESSION_SECRET=__GENERATE_A_LONG_RANDOM_VALUE__

# ==== Discord OAuth2 ====
DISCORD_CLIENT_ID=__CLIENT_ID__
DISCORD_CLIENT_SECRET=__CLIENT_SECRET__
DISCORD_OAUTH_REDIRECT_URI=https://__YOUR_DOMAIN__/auth/callback
COUNCIL_ROLE_ID=__ROLE_SNOWFLAKE__
DM_ROLE_IDS=__COMMA_SEPARATED_ROLE_SNOWFLAKES__

# ==== Foundry ====
FOUNDRY_INSTANCE_ID=__WHICH_OF_THE_THREE__
FOUNDRY_WORLD_ID=the-guild
FOUNDRY_API_BASE_URL=https://__FOUNDRY_HOST__
FOUNDRY_SERVICE_TOKEN=__SCOPED_REVOCABLE_TOKEN__
FOUNDRY_SUPPORTED_CORE=__RANGE__
FOUNDRY_SUPPORTED_SYSTEM=__RANGE__
```

Two notes. `config.py` currently calls `sys.exit()` on a missing variable
(`config.py:16`), which is fine for a bot but wrong for a web process under a
supervisor — Phase 3 should raise a typed configuration error instead.

And `ENVIRONMENT` should be validated loudly: a production process started with
a development database URL is the failure this variable exists to prevent.

## 6. Deployment gate

Plan §14.2 lists ten steps. Two need naming now because they do not exist yet:

- **step 5, back up the production database** — nothing to back up until Phase 1,
  and the backup must be *restore-tested*, not merely reported successful
  (plan §14.3);
- **step 4, scan for secrets and unsafe logging** — no scanner is configured.

Until PostgreSQL exists, the only production state is the Google Sheet, and the
only rollback is Google's own version history. That is worth stating plainly:
**there is currently no tested recovery procedure for the live game data.**
Establishing one is part of Phase 1, not a later concern.

## 7. Open questions

| # | Question |
|---|---|
| [OD-12](../discovery/open-decisions.md) | Which Foundry instance is authoritative? |
| [OD-19](../discovery/open-decisions.md) | Production domain for the web application |
| [OD-20](../discovery/open-decisions.md) | Same host as Foundry, or separate? |
| [OD-21](../discovery/open-decisions.md) | PostgreSQL deployment and backup method |
| [OD-22](../discovery/open-decisions.md) | Staging on this host or its own? |
| [OD-25](../discovery/open-decisions.md) | Are ports 30001–30003 firewalled from the internet? |
