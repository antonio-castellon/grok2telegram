"""Wipe Telegram messages in a chat (sync httpx version of grokgame purge).

Bots cannot list history. We delete a recent id window (newest first) plus
any ids the process has seen. The bot must be a group admin with
Delete messages.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bridge.telegram_io import Telegram

log = logging.getLogger("g2t.purge")

BATCH = 100
WINDOW = 500

PURGE_CONFIRM = frozenset({"all", "todo", "todos", "tous", "alle", "everything"})


@dataclass
class PurgeStats:
    deleted: int = 0
    failed: int = 0
    denied: bool = False


def ids_for_purge(upto: int, extra: Iterable[int] = ()) -> list[int]:
    if upto < 1:
        return []
    lo = max(1, upto - WINDOW + 1)
    found = set(range(lo, upto + 1))
    found.update(i for i in extra if isinstance(i, int) and 1 <= i <= upto)
    return sorted(found, reverse=True)


def purge_upto(
    tg: "Telegram",
    chat_id: int,
    upto: int,
    extra_ids: Iterable[int] = (),
) -> PurgeStats:
    stats = PurgeStats()
    ids = ids_for_purge(upto, extra_ids)
    log.info("purge chat=%s upto=%s count=%s", chat_id, upto, len(ids))
    i = 0
    while i < len(ids) and not stats.denied:
        batch = ids[i : i + BATCH]
        i += BATCH
        _delete_ids(tg, chat_id, batch, stats)
    log.info(
        "purge done chat=%s deleted=%s failed=%s denied=%s",
        chat_id,
        stats.deleted,
        stats.failed,
        stats.denied,
    )
    return stats


def _delete_ids(tg: "Telegram", chat_id: int, ids: list[int], stats: PurgeStats) -> None:
    if not ids or stats.denied:
        return
    if len(ids) == 1:
        mid = ids[0]
        try:
            tg.delete_message(chat_id, mid)
            stats.deleted += 1
        except Exception as exc:
            _on_error(exc, stats, tg, chat_id, ids)
        return
    try:
        tg.delete_messages(chat_id, ids)
        stats.deleted += len(ids)
        return
    except Exception as exc:
        _on_error(exc, stats, tg, chat_id, ids)


def _on_error(
    exc: Exception,
    stats: PurgeStats,
    tg: "Telegram",
    chat_id: int,
    ids: list[int],
) -> None:
    wait = _retry_after(exc)
    if wait is not None:
        time.sleep(wait)
        _delete_ids(tg, chat_id, ids, stats)
        return
    if _is_denied(exc):
        stats.denied = True
        log.warning("purge denied chat=%s: %s", chat_id, exc)
        return
    if len(ids) == 1:
        stats.failed += 1
        return
    mid = len(ids) // 2
    _delete_ids(tg, chat_id, ids[:mid], stats)
    _delete_ids(tg, chat_id, ids[mid:], stats)


def _retry_after(exc: Exception) -> float | None:
    text = str(exc).lower()
    if "retry after" in text or "too many requests" in text:
        # TelegramError often embeds retry_after in the message
        import re

        m = re.search(r"retry after (\d+)", text)
        if m:
            return float(m.group(1)) + 0.2
        return 1.2
    return None


def _is_denied(exc: Exception) -> bool:
    text = str(exc).lower()
    return (
        "not enough rights" in text
        or "need administrator" in text
        or "chat_admin_required" in text
        or "forbidden" in text
    )


def bot_can_delete(tg: "Telegram", chat_id: int) -> bool:
    try:
        me = tg.get_me()
        member = tg.get_chat_member(chat_id, int(me["id"]))
    except Exception:
        log.debug("get_chat_member failed chat=%s", chat_id, exc_info=True)
        return True
    status = str(member.get("status") or "")
    if status == "creator":
        return True
    if status != "administrator":
        return False
    flag = member.get("can_delete_messages")
    return flag is not False
