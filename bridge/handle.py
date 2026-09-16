from __future__ import annotations

from typing import Any

from bridge.admin import is_admin
from bridge.config import Config
from bridge.gm_mock import HELP, apply_mock
from bridge.parse import ADMIN_VERBS, SYSTEM_VERBS, Command
from bridge.store import append_inbox, append_log, save
from bridge.telegram_io import Telegram


def handle(
    cfg: Config,
    tg: Telegram,
    chat_id: int,
    user: dict[str, Any],
    cmd: Command,
    game: dict[str, Any],
) -> str:
    uid = int(user["id"])
    name = user.get("name") or str(uid)
    admin = is_admin(cfg, tg, chat_id, uid, game)
    game["chat_id"] = chat_id

    if cmd.verb == "whoami":
        return f"{name} id={uid} admin={'yes' if admin else 'no'}"

    if cmd.verb == "help":
        return HELP.get(game.get("lang") or "es", HELP["es"])

    if cmd.verb in ADMIN_VERBS and not admin:
        return "solo admin."

    if cmd.verb == "grant" and admin:
        raw = cmd.payload.strip().lstrip("@")
        if raw.isdigit():
            game.setdefault("admins", []).append(int(raw))
            save(cfg.data_dir, game)
            return f"grant {raw}"
        return "grant <id numérico>"

    if cmd.verb == "revoke" and admin:
        raw = cmd.payload.strip().lstrip("@")
        if raw.isdigit():
            game["admins"] = [a for a in game.get("admins") or [] if int(a) != int(raw)]
            save(cfg.data_dir, game)
            return f"revoke {raw}"
        return "revoke <id numérico>"

    if cmd.verb not in SYSTEM_VERBS:
        known = {c["verb"] for c in game.get("commands") or []}
        if cmd.verb not in known:
            return f"comando desconocido: {cmd.verb}. /cmd cmd list"

    append_log(game, f"{name}: /cmd {cmd.verb} {cmd.payload[:80]}")

    if cfg.gm_backend == "agent" and cmd.verb in {
        "new-game",
        "rules",
        "limit",
        "act",
        "join",
        "look",
        "guess",
        "hint",
        "next",
        "a",
        "b",
        "c",
        "d",
    }:
        append_inbox(
            cfg.data_dir,
            {
                "schema": "mesa.v1",
                "chat_id": chat_id,
                "user": {"id": uid, "name": name, "is_admin": admin},
                "lang": game.get("lang") or "es",
                "verb": cmd.verb,
                "payload": cmd.payload,
                "table": {
                    "phase": game.get("phase"),
                    "title": game.get("title"),
                    "brief": game.get("brief"),
                    "rules": game.get("rules"),
                    "limits": game.get("limits"),
                    "commands": game.get("commands"),
                    "blob": game.get("blob"),
                },
            },
        )
        save(cfg.data_dir, game)
        return ""

    say = apply_mock(game, cmd.verb, cmd.payload, game.get("lang") or "es")
    save(cfg.data_dir, game)
    return say
