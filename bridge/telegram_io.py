from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from bridge.bbs import bbs_frame
from bridge.buttons import build_inline_keyboard
from bridge.safety import scrub_outbound

API = "https://api.telegram.org"


class Telegram:
    def __init__(self, token: str, timeout: float = 50.0) -> None:
        self.token = token
        self.timeout = timeout
        self._base = f"{API}/bot{token}"

    def get_updates(self, offset: int | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "timeout": 30,
            "allowed_updates": ["message", "callback_query"],
        }
        if offset is not None:
            params["offset"] = offset
        with httpx.Client(timeout=self.timeout) as client:
            r = client.get(f"{self._base}/getUpdates", params=params)
            r.raise_for_status()
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data)
        return list(data.get("result") or [])

    def send_message(
        self,
        chat_id: int,
        text: str,
        title: str | None = None,
        buttons: list[dict[str, str]] | None = None,
        data_dir: Path | None = None,
    ) -> int | None:
        if not text:
            return None
        text = scrub_outbound(text)
        html = bbs_frame(text, title=title)
        chunk = html[:3900]
        body: dict[str, Any] = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
        }
        if buttons:
            body["reply_markup"] = build_inline_keyboard(
                buttons, chat_id=int(chat_id), data_dir=data_dir
            )
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{self._base}/sendMessage", json=body)
            r.raise_for_status()
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data)
        result = data.get("result") or {}
        mid = result.get("message_id")
        return int(mid) if mid is not None else None

    def answer_callback_query(
        self, callback_query_id: str, text: str | None = None
    ) -> None:
        body: dict[str, Any] = {"callback_query_id": callback_query_id}
        if text:
            body["text"] = text[:200]
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{self._base}/answerCallbackQuery", json=body)
            r.raise_for_status()
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description") or data)

    def edit_message_reply_markup(
        self,
        chat_id: int,
        message_id: int,
        reply_markup: dict[str, Any] | None = None,
    ) -> None:
        """Strip or replace inline keyboard. None / empty → remove markup."""
        body: dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": reply_markup if reply_markup is not None else {},
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{self._base}/editMessageReplyMarkup", json=body)
            data = r.json()
        if not data.get("ok"):
            # Message may already lack markup; ignore benign failures
            desc = str(data.get("description") or "")
            if "message is not modified" in desc.lower():
                return
            raise RuntimeError(data.get("description") or data)

    def delete_message(self, chat_id: int, message_id: int) -> None:
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"{self._base}/deleteMessage",
                json={"chat_id": chat_id, "message_id": message_id},
            )
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description") or data)

    def delete_messages(self, chat_id: int, message_ids: list[int]) -> None:
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"{self._base}/deleteMessages",
                json={"chat_id": chat_id, "message_ids": message_ids},
            )
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description") or data)

    def get_me(self) -> dict[str, Any]:
        with httpx.Client(timeout=30) as client:
            r = client.get(f"{self._base}/getMe")
            r.raise_for_status()
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data)
        return dict(data.get("result") or {})

    def get_chat_member(self, chat_id: int, user_id: int) -> dict[str, Any]:
        with httpx.Client(timeout=30) as client:
            r = client.get(
                f"{self._base}/getChatMember",
                params={"chat_id": chat_id, "user_id": user_id},
            )
            r.raise_for_status()
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description") or data)
        return dict(data.get("result") or {})

    def get_chat_administrators(self, chat_id: int) -> set[int]:
        with httpx.Client(timeout=30) as client:
            r = client.get(
                f"{self._base}/getChatAdministrators",
                params={"chat_id": chat_id},
            )
            r.raise_for_status()
            data = r.json()
        ids: set[int] = set()
        for row in data.get("result") or []:
            user = row.get("user") or {}
            if "id" in user:
                ids.add(int(user["id"]))
        return ids
