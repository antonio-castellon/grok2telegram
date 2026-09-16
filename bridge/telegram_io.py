from __future__ import annotations

from typing import Any

import httpx

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

    def send_message(self, chat_id: int, text: str) -> None:
        if not text:
            return
        chunk = text[:3900]
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"{self._base}/sendMessage",
                json={"chat_id": chat_id, "text": chunk},
            )
            r.raise_for_status()

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
