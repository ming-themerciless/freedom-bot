import os, json
from dotenv import load_dotenv

load_dotenv()

# --- Discord ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

ROLL_CHANNEL_ID    = int(os.getenv("ROLL_CHANNEL_ID", "0"))
TRADE_CHANNEL_ID   = int(os.getenv("TRADE_CHANNEL_ID", "0"))
DT_CHANNEL_ID      = int(os.getenv("DT_CHANNEL_ID", "0"))
BASTION_CHANNEL_ID = int(os.getenv("BASTION_CHANNEL_ID", "0"))

# --- Google Sheets ---
GUILD_SHEET_ID = os.getenv("GUILD_SHEET_ID", "")
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON", "")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN missing")
if not GUILD_SHEET_ID:
    raise ValueError("GUILD_SHEET_ID missing")
if not SERVICE_ACCOUNT_JSON:
    raise ValueError("SERVICE_ACCOUNT_JSON missing")

try:
    SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)
except Exception as e:
    raise ValueError("SERVICE_ACCOUNT_JSON must be valid JSON") from e
