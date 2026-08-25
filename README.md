# Freedom Blades Platform

Freedom Blades web platform with Discord, PostgreSQL, Google Sheets migration,
and Foundry adapters. The Discord bot remains one supported adapter; it is no
longer the identity of the whole project.

## Quickstart

```bash
python3 -m venv /opt/freedom-blades/runtime/venv-bot
source /opt/freedom-blades/runtime/venv-bot/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env   # Werte ausfüllen (Token, IDs, Google)
```

Canonical repository location: `/opt/freedom-blades/platform`.
