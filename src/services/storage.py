import json
from pathlib import Path

STORAGE_FILE = Path("settings.json")


def save_setting(key: str, value: str) -> None:
    data = {}
    if STORAGE_FILE.exists():
        try:
            data = json.loads(STORAGE_FILE.read_text())
        except Exception:
            data = {}
    data[key] = value
    STORAGE_FILE.write_text(json.dumps(data, indent=2))


def get_setting(key: str, default: str | None = None) -> str | None:
    if not STORAGE_FILE.exists():
        return default
    try:
        data = json.loads(STORAGE_FILE.read_text())
        return data.get(key, default)
    except Exception:
        return default


def remove_setting(key: str) -> None:
    if STORAGE_FILE.exists():
        try:
            data = json.loads(STORAGE_FILE.read_text())
            if key in data:
                del data[key]
                STORAGE_FILE.write_text(json.dumps(data, indent=2))
        except Exception:
            pass


def get_currency_symbol() -> str:
    return get_setting("currency_symbol") or "kr"


def set_currency_symbol(symbol: str) -> None:
    save_setting("currency_symbol", symbol)
