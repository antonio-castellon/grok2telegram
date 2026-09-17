from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bridge.wake import wake_mesa


def _path(data_dir: Path, chat_id: int) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / f"chat_{chat_id}.json"


def empty(chat_id: int) -> dict[str, Any]:
    return {
        "chat_id": chat_id,
        "lang": "es",
        "phase": "lobby",
        "title": "",
        "brief": "",
        "rules": [],
        "limits": [],
        "commands": [],
        "admins": [],
        "players": {},
        "blob": {},
        "log": [],
    }


def load(data_dir: Path, chat_id: int) -> dict[str, Any]:
    p = _path(data_dir, chat_id)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return empty(chat_id)


def save(data_dir: Path, game: dict[str, Any]) -> None:
    game["updated_at"] = datetime.now(timezone.utc).isoformat()
    _path(data_dir, int(game["chat_id"])).write_text(
        json.dumps(game, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def append_log(game: dict[str, Any], entry: str, limit: int = 16) -> None:
    game.setdefault("log", []).append(entry)
    game["log"] = game["log"][-limit:]


def append_inbox(data_dir: Path, payload: dict[str, Any]) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "inbox.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    # Instant GM: ping Mesa webhook (no-op if MESA_WAKE_URL unset)
    wake_mesa()
