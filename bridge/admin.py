from __future__ import annotations

from typing import Any

from bridge.config import Config
from bridge.telegram_io import Telegram


def is_admin(
    cfg: Config,
    tg: Telegram,
    chat_id: int,
    user_id: int,
    game: dict[str, Any],
) -> bool:
    if user_id in cfg.admin_telegram_ids:
        return True
    extra = game.get("admins") or []
    if user_id in extra or str(user_id) in {str(x) for x in extra}:
        return True
    try:
        if user_id in tg.get_chat_administrators(chat_id):
            return True
    except Exception:
        pass
    return False
