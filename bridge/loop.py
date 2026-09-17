from __future__ import annotations

import logging
import os
import time
from pathlib import Path

from bridge.config import load_config
from bridge.handle import handle
from bridge.parse import parse_text
from bridge.store import load
from bridge.telegram_io import Telegram

log = logging.getLogger("g2t")


def _offset_path(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "offset.txt"


def _read_offset(data_dir: Path) -> int | None:
    p = _offset_path(data_dir)
    if not p.exists():
        return None
    raw = p.read_text(encoding="utf-8").strip()
    return int(raw) if raw.isdigit() else None


def _write_offset(data_dir: Path, value: int) -> None:
    _offset_path(data_dir).write_text(str(value), encoding="utf-8")


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    if not cfg.telegram_bot_token:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN")
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    (cfg.data_dir / "pid").write_text(str(os.getpid()), encoding="utf-8")
    tg = Telegram(cfg.telegram_bot_token)
    log.info("g2t backend=%s", cfg.gm_backend)
    offset = _read_offset(cfg.data_dir)
    while True:
        try:
            updates = tg.get_updates(offset)
        except Exception as exc:
            log.warning("getUpdates: %s", exc)
            time.sleep(3)
            continue
        for upd in updates:
            offset = int(upd["update_id"]) + 1
            _write_offset(cfg.data_dir, offset)
            msg = upd.get("message") or {}
            chat = msg.get("chat") or {}
            chat_id = chat.get("id")
            if chat_id is None:
                continue
            if cfg.allowed_chat_ids and int(chat_id) not in cfg.allowed_chat_ids:
                continue
            cmd = parse_text(msg.get("text"))
            if not cmd:
                continue
            user = msg.get("from") or {}
            game = load(cfg.data_dir, int(chat_id))
            say = handle(
                cfg,
                tg,
                int(chat_id),
                {
                    "id": user.get("id"),
                    "name": user.get("first_name") or user.get("username") or "?",
                    "username": user.get("username") or "",
                },
                cmd,
                game,
            )
            if say:
                try:
                    raw_title = (game.get("title") or "").strip()
                    board_title = raw_title.split()[0][:20] if raw_title else None
                    tg.send_message(int(chat_id), say, title=board_title)
                except Exception as exc:
                    log.warning("sendMessage: %s", exc)
