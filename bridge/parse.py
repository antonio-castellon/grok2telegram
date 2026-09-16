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
    }
)
ADMIN_VERBS = frozenset(
    {"lang", "new-game", "rules", "limit", "reset", "grant", "revoke"}
)


@dataclass(frozen=True)
class Command:
    verb: str
    payload: str


def parse_text(text: str | None) -> Command | None:
    if not text:
        return None
    line = text.strip()
    if line.startswith("/cmd"):
        rest = line[4:]
        if rest.startswith("@"):
            rest = rest.split(None, 1)[1] if " " in rest else ""
        else:
            rest = rest.lstrip()
    elif line.lower().startswith("cmd "):
        rest = line[4:]
    else:
        return None
    rest = rest.strip()
    if not rest:
        return Command(verb="help", payload="")
    parts = rest.split(None, 1)
    verb = parts[0].lower()
    payload = parts[1].strip() if len(parts) > 1 else ""
    if not VERB_RE.match(verb):
        return None
    return Command(verb=verb, payload=payload)
