"""Compat wrapper: frame outbound say the grokgame way (skin.card + HTML <pre>)."""

from __future__ import annotations

from bridge.skin import as_html_pre, card


def bbs_frame(body: str, title: str | None = None) -> str:
    """Return HTML <pre>…</pre> ready for Telegram parse_mode=HTML."""
    text = (body or "").rstrip()
    if not text:
        return text
    stripped = text.strip()
    # Already HTML-pre
    if stripped.startswith("<pre>") and stripped.endswith("</pre>"):
        return stripped
    # Already a Unicode card from skin.card / agent
    if stripped.startswith("┌") or stripped.startswith("╔"):
        return as_html_pre(stripped)
    # Markdown fence leftovers — strip and reframe
    if stripped.startswith("```"):
        inner = stripped.strip("`")
        # drop optional language tag line
        parts = inner.split("\n", 1)
        if parts and parts[0].strip() in {"", "text", "ascii"}:
            inner = parts[1] if len(parts) > 1 else ""
        else:
            inner = inner
        stripped = inner.strip()
        if stripped.startswith("┌"):
            return as_html_pre(stripped)

    t = (title or "mesa").strip() or "mesa"
    lines = [ln.rstrip() for ln in stripped.splitlines()] or [""]
    return as_html_pre(card(t, lines))
