from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from bridge.config import load_config
from bridge.handle import handle
from bridge.parse import PURGE_SIGNAL, parse_text
from bridge.purge import bot_can_delete, purge_upto
from bridge.store import load
from bridge.telegram_io import Telegram
from bridge.inbox_flush import flush_pending

log = logging.getLogger("g2t")


def _offset_path(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "offset.txt"


def _seen_path(data_dir: Path, chat_id: int) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / f"seen_{chat_id}.json"


def _read_offset(data_dir: Path) -> int | None:
    p = _offset_path(data_dir)
    if not p.exists():
        return None
    raw = p.read_text(encoding="utf-8").strip()
    return int(raw) if raw.isdigit() else None


def _write_offset(data_dir: Path, value: int) -> None:
    _offset_path(data_dir).write_text(str(value), encoding="utf-8")


def _load_seen(data_dir: Path, chat_id: int) -> set[int]:
    p = _seen_path(data_dir, chat_id)
    if not p.exists():
        return set()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {int(x) for x in data if isinstance(x, (int, str)) and str(x).lstrip("-").isdigit()}
    except Exception:
        return set()


def _save_seen(data_dir: Path, chat_id: int, ids: set[int]) -> None:
    # Keep a bounded set of recent ids
    kept = sorted(ids)[-800:]
    _seen_path(data_dir, chat_id).write_text(
        json.dumps(kept, ensure_ascii=False),
        encoding="utf-8",
    )


def _remember(data_dir: Path, chat_id: int, message_id: int | None) -> None:
    if message_id is None:
        return
    ids = _load_seen(data_dir, chat_id)
    ids.add(int(message_id))
    _save_seen(data_dir, chat_id, ids)


def _purge_messages(lang: str) -> dict[str, str]:
    return {
        "work": {
            "es": "Borrando todos los mensajes.",
            "en": "Deleting every message.",
            "fr": "Suppression de tous les messages.",
            "de": "Lösche alle Nachrichten.",
        }.get(lang, "Deleting every message."),
        "denied": {
            "es": "El bot debe ser admin con permiso Borrar mensajes.",
            "en": "The bot must be admin with Delete messages permission.",
            "fr": "Le bot doit être admin avec le droit Supprimer des messages.",
            "de": "Bot muss Admin mit Recht Nachrichten löschen sein.",
        }.get(lang, "The bot must be admin with Delete messages permission."),
        "none": {
            "es": "Nada que borrar.",
            "en": "Nothing to delete.",
            "fr": "Rien à supprimer.",
            "de": "Nichts zu löschen.",
        }.get(lang, "Nothing to delete."),
        "ok": {
            "es": "Listo. Borrados ~{n} (omitidos {fail}).",
            "en": "Done. Deleted ~{n} (skipped {fail}).",
            "fr": "Fait. Supprimés ~{n} (ignorés {fail}).",
            "de": "Fertig. Gelöscht ~{n} (übersprungen {fail}).",
        }.get(lang, "Done. Deleted ~{n} (skipped {fail})."),
    }


def _execute_purge(
    tg: Telegram,
    data_dir: Path,
    chat_id: int,
    upto_message_id: int,
    lang: str,
    board_title: str | None,
) -> None:
    msgs = _purge_messages(lang)
    if not bot_can_delete(tg, chat_id):
        tg.send_message(chat_id, msgs["denied"], title=board_title or "clear")
        return
    progress_id = None
    try:
        progress_id = tg.send_message(chat_id, msgs["work"], title=board_title or "clear")
        _remember(data_dir, chat_id, progress_id)
    except Exception:
        log.debug("could not post purge progress", exc_info=True)
    extra = _load_seen(data_dir, chat_id)
    stats = purge_upto(tg, chat_id, int(upto_message_id), extra_ids=extra)
    if progress_id is not None:
        try:
            tg.delete_message(chat_id, progress_id)
        except Exception:
            pass
    if stats.denied:
        say = msgs["denied"]
    elif stats.deleted <= 0:
        say = msgs["none"]
    else:
        say = msgs["ok"].format(n=stats.deleted, fail=stats.failed)
    mid = tg.send_message(chat_id, say, title=board_title or "clear")
    _remember(data_dir, chat_id, mid)
    # After purge, reset seen to just the summary message
    if mid is not None:
        _save_seen(data_dir, chat_id, {mid})


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config()
    if not cfg.telegram_bot_token:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN")
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    (cfg.data_dir / "pid").write_text(str(os.getpid()), encoding="utf-8")
    tg = Telegram(cfg.telegram_bot_token)
    bot_username = ""
    try:
        me = tg.get_me()
        bot_username = str(me.get("username") or "").strip()
    except Exception as exc:
        log.warning("getMe: %s", exc)
    log.info("g2t backend=%s bot=@%s", cfg.gm_backend, bot_username or "?")
    try:
        stats = flush_pending(cfg, tg)
        log.info("boot flush %s", stats)
    except Exception as exc:
        log.warning("boot flush: %s", exc)
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
            message_id = msg.get("message_id")
            if message_id is not None:
                _remember(cfg.data_dir, int(chat_id), int(message_id))
            cmd = parse_text(msg.get("text"), bot_username=bot_username or None)
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
            raw_title = (game.get("title") or "").strip()
            board_title = raw_title.split()[0][:20] if raw_title else None
            if say == PURGE_SIGNAL:
                try:
                    _execute_purge(
                        tg,
                        cfg.data_dir,
                        int(chat_id),
                        int(message_id or 0),
                        game.get("lang") or "es",
                        board_title,
                    )
                except Exception as exc:
                    log.warning("purge: %s", exc)
                continue
            if say:
                try:
                    mid = tg.send_message(int(chat_id), say, title=board_title)
                    _remember(cfg.data_dir, int(chat_id), mid)
                except Exception as exc:
                    log.warning("sendMessage: %s", exc)
