# helpers/config.py
import os

def _env_int(name: str) -> int:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return int(v)

GUILD_ID = _env_int("GUILD_ID")