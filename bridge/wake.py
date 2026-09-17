"""Ping Mesa's webhook so GM inbox drains without waiting for the 5m cron."""

from __future__ import annotations

import logging
import os

import httpx

log = logging.getLogger("g2t.wake")


def wake_mesa(url: str | None = None, key: str | None = None) -> bool:
    url = (url if url is not None else os.getenv("MESA_WAKE_URL") or "").strip()
    key = (key if key is not None else os.getenv("MESA_WAKE_KEY") or "").strip()
    if not url:
        log.debug("MESA_WAKE_URL unset — Mesa will drain on cron only")
        return False
    body = {"source": "grok2telegram", "event": "inbox"}
    attempts: list[dict[str, str]] = [{"Content-Type": "application/json"}]
    if key:
        attempts = [
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            {"Content-Type": "application/json", "Authorization": key},
            {"Content-Type": "application/json", "X-Webhook-Key": key},
        ]
    last_status = None
    try:
        with httpx.Client(timeout=8.0) as client:
            for headers in attempts:
                r = client.post(url, headers=headers, json=body)
                last_status = r.status_code
                if r.status_code < 400:
                    log.info("mesa wake ok (%s)", r.status_code)
                    return True
                log.warning("mesa wake HTTP %s (%s)", r.status_code, ",".join(headers.keys()))
        return False
    except Exception as exc:
        log.warning("mesa wake failed: %s", exc)
        return False
