from __future__ import annotations

from typing import Any

HELP = {
    "es": "Gramática: /cmd <verbo> [texto]\nSistema: help lang new-game rules limit cmd list status reset whoami grant revoke",
    "en": "Grammar: /cmd <verb> [text]\nSystem: help lang new-game rules limit cmd list status reset whoami grant revoke",
    "fr": "Grammaire : /cmd <verbe> [texte]\nSystème : help lang new-game rules limit cmd list status reset whoami grant revoke",
    "de": "Grammatik: /cmd <verb> [text]\nSystem: help lang new-game rules limit cmd list status reset whoami grant revoke",
}


def _cmds_for_brief(brief: str) -> list[dict[str, str]]:
    b = brief.lower()
    if any(w in b for w in ("acertijo", "enigma", "riddle", "devinette")):
        verbs = [("join", "entrar"), ("guess", "respuesta"), ("hint", "pista"), ("next", "siguiente")]
    elif any(w in b for w in ("trivia", "pregunta", "opcion", "opción", "quiz")):
        verbs = [("join", "entrar"), ("a", "A"), ("b", "B"), ("c", "C"), ("d", "D"), ("next", "siguiente")]
    else:
        verbs = [("join", "entrar"), ("act", "actuar"), ("look", "mirar")]
    return [{"verb": v, "help": h} for v, h in verbs]


def apply_mock(game: dict[str, Any], verb: str, payload: str, lang: str) -> str:
    lang = lang if lang in HELP else "es"
    if verb == "help":
        return HELP[lang]
    if verb == "lang":
        code = payload.strip().lower()[:2]
        if code in HELP:
            game["lang"] = code
            return f"lang={code}"
        return "lang: es|fr|de|en"
    if verb == "new-game":
        brief = payload.strip() or "mesa abierta"
        game["phase"] = "playing"
        game["title"] = brief[:48]
        game["brief"] = brief
        game["commands"] = _cmds_for_brief(brief)
        game["rules"] = [brief] if brief else []
        game["blob"] = {}
        listing = ", ".join(c["verb"] for c in game["commands"])
        return f"Mesa: {game['title']}\n/cmd cmd list → {listing}"
    if verb == "rules":
        if payload:
            game.setdefault("rules", []).append(payload)
        return "rules: " + " | ".join(game.get("rules") or ["—"])
    if verb == "limit":
        if payload:
            game.setdefault("limits", []).append(payload)
        return "limits: " + " | ".join(game.get("limits") or ["—"])
    if verb == "cmd" and payload.split()[:1] == ["list"]:
        sys_ = "help lang new-game rules limit cmd status reset whoami grant revoke"
        game_ = " ".join(c["verb"] for c in game.get("commands") or [])
        return f"sistema: {sys_}\njuego: {game_ or '(nada: /cmd new-game …)'}"
    if verb == "status":
        return (
            f"{game.get('title') or '(sin título)'} · {game.get('phase')} · lang={game.get('lang')}\n"
            f"rules={game.get('rules')}\nlimits={game.get('limits')}"
        )
    if verb == "reset":
        keep_lang = game.get("lang") or "es"
        game.clear()
        game.update(
            {
                "lang": keep_lang,
                "phase": "lobby",
                "title": "",
                "brief": "",
                "rules": [],
                "limits": [],
                "commands": [],
                "admins": [],
                "players": {},
                "blob": {},
                "log": [],
            }
        )
        return "reset."
    if verb == "whoami":
        return ""
    known = {c["verb"] for c in game.get("commands") or []}
    if verb in known:
        return f"[{verb}] {payload or 'ok'} — mock."
    return f"comando desconocido: {verb}. /cmd cmd list"
