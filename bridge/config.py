from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    admin_telegram_ids: frozenset[int]
    gm_backend: str
    allowed_chat_ids: frozenset[int]
    data_dir: Path
    mesa_wake_url: str
    mesa_wake_key: str


def _parse_ids(raw: str) -> frozenset[int]:
    ids: set[int] = set()
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part:
            ids.add(int(part))
    return frozenset(ids)


def load_config(env_file: Path | None = None) -> Config:
    load_dotenv(env_file or ROOT / ".env")
    backend = (os.getenv("GM_BACKEND") or "mock").strip().lower()
    if backend not in {"mock", "agent"}:
        backend = "mock"
    data_dir = Path(os.getenv("DATA_DIR") or ROOT / "data")
    return Config(
        telegram_bot_token=(os.getenv("TELEGRAM_BOT_TOKEN") or "").strip(),
        admin_telegram_ids=_parse_ids(os.getenv("ADMIN_TELEGRAM_IDS") or ""),
        gm_backend=backend,
        allowed_chat_ids=_parse_ids(os.getenv("ALLOWED_CHAT_IDS") or ""),
        data_dir=data_dir,
        mesa_wake_url=(os.getenv("MESA_WAKE_URL") or "").strip(),
        mesa_wake_key=(os.getenv("MESA_WAKE_KEY") or "").strip(),
    )
