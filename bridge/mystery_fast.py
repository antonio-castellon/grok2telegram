"""Instant Misterio A/B/C/D when Mesa pre-baked next scenes into blob.branches.

Keeps the bridge thin: no narration inventing here. Mesa must write
blob["branches"] = {"a": {"say": "...", "scene": "...", "patch": {...}}, ...}
when it posts a choice turn. Missing branch → fall through to inbox/wake.
Also answers inventario / pistas / estado / repetir from blob without waking Mesa.
"""

from __future__ import annotations

from typing import Any


_FACT_VERBS = frozenset({"inventario", "pistas", "estado", "repetir"})
_CHOICE_VERBS = frozenset({"a", "b", "c", "d"})


def is_mystery(game: dict[str, Any]) -> bool:
    blob = game.get("blob") or {}
    mode = (blob.get("mode") or "").lower()
    title = (game.get("title") or "").lower()
    return mode in {"mystery_cyoa", "misterio", "mystery"} or "misterio" in title


def try_fast(game: dict[str, Any], verb: str, payload: str = "") -> str | None:
    """Return a say string if handled locally; else None."""
    if not is_mystery(game):
        return None
    v = (verb or "").lower().strip()
    blob = game.setdefault("blob", {})

    if v in _FACT_VERBS:
        return _fact(game, v)

    # /cmd a  or ask payload "a"
    choice = v if v in _CHOICE_VERBS else None
    if v == "ask":
        low = (payload or "").strip().lower()
        if low in _CHOICE_VERBS:
            choice = low
        elif low in _FACT_VERBS:
            return _fact(game, low)

    if choice is None:
        return None

    branches = blob.get("branches") or {}
    branch = branches.get(choice) or branches.get(choice.upper())
    if not isinstance(branch, dict) or not (branch.get("say") or "").strip():
        return None  # Mesa has not pre-baked this choice yet

    say = str(branch["say"]).strip()
    if branch.get("scene"):
        blob["scene"] = branch["scene"]
    patch = branch.get("patch")
    if isinstance(patch, dict):
        for k, val in patch.items():
            if k == "clues_add" and isinstance(val, list):
                clues = blob.setdefault("clues", [])
                for c in val:
                    if c not in clues:
                        clues.append(c)
            elif k == "inventory_add" and isinstance(val, list):
                inv = blob.setdefault("inventory", [])
                for obj in val:
                    if obj not in inv and len(inv) < 6:
                        inv.append(obj)
            elif k == "tension_delta":
                blob["tension"] = max(0, min(10, int(blob.get("tension") or 0) + int(val)))
            elif k not in {"say", "branches"}:
                blob[k] = val
    blob["turn"] = int(blob.get("turn") or 0) + 1
    # consume this menu; next turn Mesa (or a deeper branch tree) must refill
    next_branches = branch.get("branches")
    if isinstance(next_branches, dict) and next_branches:
        blob["branches"] = next_branches
    else:
        blob["branches"] = {}
    blob["last_say"] = say
    blob["last_options"] = {
        k.upper(): (bv.get("label") if isinstance(bv, dict) else None)
        for k, bv in (blob.get("branches") or {}).items()
    }
    return say


def _fact(game: dict[str, Any], verb: str) -> str:
    blob = game.get("blob") or {}
    lang = game.get("lang") or "es"
    if verb == "inventario":
        inv = blob.get("inventory") or []
        if not inv:
            return "Inventario vacío." if lang.startswith("es") else "Inventory empty."
        return "Inventario: " + ", ".join(inv)
    if verb == "pistas":
        clues = blob.get("clues") or []
        if not clues:
            return "Sin pistas aún." if lang.startswith("es") else "No clues yet."
        return "Pistas:\n- " + "\n- ".join(clues)
    if verb == "estado":
        return (
            f"Escena: {blob.get('scene') or '?'}\n"
            f"Tensión: {blob.get('tension', 0)}/10\n"
            f"Turno: {blob.get('turn', 0)}\n"
            f"Inventario: {', '.join(blob.get('inventory') or []) or '—'}"
        )
    if verb == "repetir":
        last = (blob.get("last_say") or "").strip()
        if last:
            return last
        return "Nada que repetir aún." if lang.startswith("es") else "Nothing to repeat yet."
    return ""
