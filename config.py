# config.py
import os
import sys
import json
import re
from pathlib import Path
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

def _as_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

def _read_lavalink_from_yaml(paths: list[Path]) -> tuple[str, int, str] | None:
    """
    Best-effort Parser ohne PyYAML: liest host(default 127.0.0.1), port (server.port),
    password (lavalink.server.password) aus YAML-Dateien.
    """
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue

        # Port: erst explizit unter 'server:', sonst allgemeines 'port:'
        m_port = re.search(r"(?m)^\s*server:\s*\n(?:.*\n)*?\s*port:\s*(\d+)\s*$", text)
        if not m_port:
            m_port = re.search(r"(?m)^\s*port:\s*(\d+)\s*$", text)
        port = int(m_port.group(1)) if m_port else 2333

        # Passwort: unter lavalink.server.password
        m_pass = re.search(
            r"(?m)^\s*lavalink:\s*\n(?:.*\n)*?^\s*server:\s*\n(?:.*\n)*?^\s*password:\s*['\"]?(.+?)['\"]?\s*$",
            text
        )
        if not m_pass:
            # Fallback: erstes 'password:' irgendwo
            m_pass = re.search(r"(?m)^\s*password:\s*['\"]?(.+?)['\"]?\s*$", text)

        if m_pass:
            host = "127.0.0.1"  # Lavalink läuft typischerweise lokal
            return host, port, m_pass.group(1).strip()

    return None


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


# ==== Music / Lavalink ====
ENABLE_MUSIC: bool = _as_bool("ENABLE_MUSIC", default=False)

if ENABLE_MUSIC:
    # 1) ENV priorisieren
    _host = os.getenv("LAVALINK_HOST", "").strip()
    _port = os.getenv("LAVALINK_PORT", "").strip()
    _pass = os.getenv("LAVALINK_PASSWORD", "").strip()

    if _host and _port and _pass:
        try:
            LAVALINK_HOST: str = _host
            LAVALINK_PORT: int = int(_port)
            LAVALINK_PASSWORD: str = _pass
        except ValueError:
            sys.exit(f"LAVALINK_PORT must be integer, got { _port!r }")
    else:
        # 2) Fallback: aus YAML lesen
        candidates = [
            Path("/opt/lavalink/application.yml"),             # laufende Instanz
            Path("infra/lavalink/application.yml.tmpl"),       # Repo-Template
        ]
        parsed = _read_lavalink_from_yaml(candidates)
        if not parsed:
            sys.exit(
                "Music enabled but LAVALINK_* env not set and no usable YAML found.\n"
                "Set LAVALINK_HOST/LAVALINK_PORT/LAVALINK_PASSWORD or ensure /opt/lavalink/application.yml exists."
            )
        LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD = parsed
else:
    LAVALINK_HOST: str = ""
    LAVALINK_PORT: int = 0
    LAVALINK_PASSWORD: str = ""