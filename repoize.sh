#!/usr/bin/env bash
set -euo pipefail

ROOT="/opt/discord-bots/freedom-bot"
cd "$ROOT"

# --- .gitignore ---
cat > .gitignore <<'EOF'
# venv & Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/

# Env/Secrets
.env
*.env
.env.*
service_account.json
*.pem
*.key

# Logs & tmp
logs/
*.log
.DS_Store

# Node/lavalink cache (falls vorhanden)
node_modules/
EOF

# --- Beispiel-ENV (ohne Geheimnisse) ---
cat > .env.example <<'EOF'
# Discord
DISCORD_TOKEN=__PUT_TOKEN_HERE__
GUILD_ID=1052698198180892733
ROLL_CHANNEL_ID=
TRADE_CHANNEL_ID=
DT_CHANNEL_ID=
BASTION_CHANNEL_ID=

# Google Sheets
GUILD_SHEET_ID=
# SERVICE_ACCOUNT_JSON: komplettes JSON als eine Zeile (ohne Zeilenumbrüche)
SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",...}

# Music / Lavalink
ENABLE_MUSIC=1
LAVALINK_HOST=127.0.0.1
LAVALINK_PORT=2333
LAVALINK_PASSWORD=__PUT_LL_PASSWORD__
EOF

# --- Infra-Vorlagen ---
mkdir -p infra/systemd infra/lavalink

cat > infra/systemd/freedom-bot.service.tmpl <<'EOF'
[Unit]
Description=Discord Bot Service for the Freedom Bot
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/discord-bots/freedom-bot
ExecStart=/opt/discord-bots/venv/bin/python main.py
User=discordbot
Group=discordbot
Environment=PYTHONUNBUFFERED=1
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

cat > infra/systemd/lavalink.service.tmpl <<'EOF'
[Unit]
Description=Lavalink audio node (v4)
After=network.target

[Service]
User=lavalink
Group=lavalink
WorkingDirectory=/opt/lavalink
ExecStart=/usr/bin/java -Xms256m -Xmx1g -jar /opt/lavalink/Lavalink.jar
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF

cat > infra/lavalink/application.yml.tmpl <<'EOF'
server:
  port: 2333
  address: 0.0.0.0

lavalink:
  server:
    password: "__PUT_LL_PASSWORD__"
    sources:
      youtube: false

plugins:
  - dependency: "dev.lavalink.youtube:youtube-plugin:1.13.4"
    repository: "https://maven.lavalink.dev/releases"
    config:
      youtubeConfig:
        clients:
          - WEB
        oauth:
          enabled: true

logging:
  file:
    path: ./logs/

spring:
  cloud:
    config:
      enabled: false
EOF

# --- README minimal ---
cat > README.md <<'EOF'
# Freedom Bot (Discord)

Modularer Py-Cord-Bot mit Google Sheets und optionaler Music via Lavalink.

## Quickstart

```bash
python3 -m venv /opt/discord-bots/venv
source /opt/discord-bots/venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env   # Werte ausfüllen (Token, IDs, Google, Lavalink)