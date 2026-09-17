from __future__ import annotations

from typing import Any

import httpx

from bridge.bbs import bbs_frame

API = "https://api.telegram.org"


class Telegram:
    def __init__(self, token: str, timeout: float = 50.0) -> None:
        self.token = token
        self.timeout = timeout
        self._base = f"{API}/bot{token}"

    def get_updates(self, offset: int | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"timeout": 30, "allowed_updates": ["message"]}
        if offset is not None:
            params["offset"] = offset
        with httpx.Client(timeout=self.timeout) as client:
            r = client.get(f"{self._base}/getUpdates", params=params)
            r.raise_for_status()
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data)
        return list(data.get("result") or [])

    def send_message(self, chat_id: int, text: str, title: str | None = None) -> int | None:
        if not text:
            return None
        html = bbs_frame(text, title=title)
        chunk = html[:3900]
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"{self._base}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": "HTML",
                },
            )
            r.raise_for_status()
            data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data)
        result = data.get("result") or {}
        mid = result.get("message_id")
        return int(mid) if mid is not None else None

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
