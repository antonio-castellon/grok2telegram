"""Ping Mesa's webhook so GM inbox drains without waiting for the 5m cron."""

from __future__ import annotations

import logging
import os
import re

import httpx

log = logging.getLogger("g2t.wake")

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.I,
)


def _normalize_url(url: str) -> list[str]:
    """Return URL candidates. Prefer api2.cursor.sh automations webhook."""
    url = url.strip().rstrip("/")
    out: list[str] = []
    m = _UUID_RE.search(url)
    if m:
        uid = m.group(0)
        out.append(f"https://api2.cursor.sh/automations/webhook/{uid}")
    if url not in out:
        out.append(url)
    # de-dupe preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def wake_mesa(url: str | None = None, key: str | None = None) -> bool:
    url = (url if url is not None else os.getenv("MESA_WAKE_URL") or "").strip()
    key = (key if key is not None else os.getenv("MESA_WAKE_KEY") or "").strip()
    if not url:
        log.debug("MESA_WAKE_URL unset — Mesa will drain on cron only")
        return False
    if key.startswith("whsec_"):
        log.warning(
            "MESA_WAKE_KEY looks like whsec_ (signing secret). "
            "Grok Bot needs a crsr_ sender key + Authorization: Bearer …"
        )
    body = {"source": "grok2telegram", "event": "inbox"}
    headers_base = {"Content-Type": "application/json"}
    if key:
        attempts = [
            {**headers_base, "Authorization": f"Bearer {key}"},
        ]
    else:
        attempts = [headers_base]

    last_status = None
    last_body = ""
    try:
        with httpx.Client(timeout=8.0) as client:
            for candidate in _normalize_url(url):
                for headers in attempts:
                    r = client.post(candidate, headers=headers, json=body)
                    last_status = r.status_code
                    last_body = (r.text or "")[:160]
                    if r.status_code < 400:
                        log.info("mesa wake ok (%s) via %s", r.status_code, candidate.split("/")[2])
                        return True
                    log.warning(
                        "mesa wake HTTP %s host=%s body=%s",
                        r.status_code,
                        candidate.split("/")[2],
                        last_body.replace("\n", " "),
                    )
        return False
    except Exception as exc:
        log.warning("mesa wake failed: %s", exc)
        return False
