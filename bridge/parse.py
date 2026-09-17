from __future__ import annotations

import re
from dataclasses import dataclass

VERB_RE = re.compile(r"^[a-z0-9-]{1,32}$")
SYSTEM_VERBS = frozenset(
    {
        "help",
        "lang",
        "new-game",
        "rules",
        "limit",
        "cmd",
        "status",
        "reset",
        "whoami",
        "grant",
        "revoke",
        "clear",
        "restart",
        "unjoin",
        "ask",  # free-form @bot chat → Agent
    }
)
ADMIN_VERBS = frozenset(
    {"lang", "new-game", "rules", "limit", "reset", "grant", "revoke", "clear", "restart"}
)
PURGE_SIGNAL = "__PURGE_ALL__"


@dataclass(frozen=True)
class Command:
    verb: str
    payload: str
    via_mention: bool = False


def _strip_bot_mention(line: str, bot_username: str | None) -> str | None:
    """If line starts with @bot_username, return the remainder; else None."""
    if not bot_username:
        return None
    name = bot_username.lstrip("@").strip()
    if not name:
        return None
    mention = f"@{name}".lower()
    lower = line.lower()
    if not lower.startswith(mention):
        return None
    rest = line[len(mention) :]
    return rest.lstrip(" \t:,-")


def parse_text(text: str | None, bot_username: str | None = None) -> Command | None:
    """Parse /cmd …, cmd …, or @bot … (command verb OR free-form ask)."""
    if not text:
        return None
    line = text.strip()
    rest: str | None = None
    via_mention = False

    if line.startswith("/cmd"):
        rest = line[4:]
        if rest.startswith("@"):
            rest = rest.split(None, 1)[1] if " " in rest else ""
        else:
            rest = rest.lstrip()
    elif line.lower().startswith("cmd "):
        rest = line[4:]
    else:
        mentioned = _strip_bot_mention(line, bot_username)
        if mentioned is None:
            return None
        rest = mentioned
        via_mention = True

    rest = (rest or "").strip()
    if not rest:
        return Command(verb="help", payload="", via_mention=via_mention)

    parts = rest.split(None, 1)
    first = parts[0].lower()
    if first.startswith("/"):
        first = first[1:]
    payload = parts[1].strip() if len(parts) > 1 else ""

    # @bot <free text>: if the first token is not a tidy verb, whole rest is ask.
    if via_mention and not VERB_RE.match(first):
        return Command(verb="ask", payload=rest, via_mention=True)

    if not VERB_RE.match(first):
        return None

    # @bot <maybe-verb> … — unknown verbs become free-form ask (handle decides
    # known game verbs later; we still parse as verb here, handle promotes).
    return Command(verb=first, payload=payload, via_mention=via_mention)
