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
    # Telegram sometimes sticks punctuation: @bot, help  /  @bot: help
    return rest.lstrip(" 	:,-")


def parse_text(text: str | None, bot_username: str | None = None) -> Command | None:
    """Parse /cmd …, cmd …, or @bot_username … into a Command."""
    if not text:
        return None
    line = text.strip()
    rest: str | None = None

    if line.startswith("/cmd"):
        rest = line[4:]
        if rest.startswith("@"):
            # /cmd@BotName verb …
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

    rest = (rest or "").strip()
    if not rest:
        return Command(verb="help", payload="")
    parts = rest.split(None, 1)
    verb = parts[0].lower()
    # allow /help via mention typos: "@bot /help all" → strip leading slash on verb
    if verb.startswith("/"):
        verb = verb[1:]
    payload = parts[1].strip() if len(parts) > 1 else ""
    if not VERB_RE.match(verb):
        return None
    return Command(verb=verb, payload=payload)
