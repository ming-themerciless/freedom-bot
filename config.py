# config.py
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()


# -------- helpers --------
def _req(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        sys.exit(f"Missing required env var: {name}")
    return v

def _req_int(name: str) -> int:
    s = _req(name)
    try:
        v = int(s)
    except ValueError:
        sys.exit(f"Env var {name} must be an integer, got {s!r}")
    if v <= 0:
        sys.exit(f"Env var {name} must be a positive integer, got {v}")
    return v

# ==== Discord ====
DISCORD_TOKEN: str = _req("DISCORD_TOKEN")
GUILD_ID: int = _req_int("GUILD_ID")

ROLL_CHANNEL_ID: int    = _req_int("ROLL_CHANNEL_ID")
TRADE_CHANNEL_ID: int   = _req_int("TRADE_CHANNEL_ID")
DT_CHANNEL_ID: int      = _req_int("DT_CHANNEL_ID")
BASTION_CHANNEL_ID: int = _req_int("BASTION_CHANNEL_ID")

# Für Slash-Command-Registrierung
GUILD_IDS = [GUILD_ID]


# ==== Google Sheets ====
GUILD_SHEET_ID: str = _req("GUILD_SHEET_ID")
SERVICE_ACCOUNT_JSON: str = _req("SERVICE_ACCOUNT_JSON")

try:
    SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)
except Exception:
    sys.exit("SERVICE_ACCOUNT_JSON must be valid JSON (single-line, escaped).")
