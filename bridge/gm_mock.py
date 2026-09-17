from __future__ import annotations

from typing import Any

HELP = {
    "es": "Gramática: /cmd <verbo> [texto]\nSistema: help lang new-game rules limit cmd list status reset whoami grant revoke\nDetalle: /cmd help <verbo>",
    "en": "Grammar: /cmd <verb> [text]\nSystem: help lang new-game rules limit cmd list status reset whoami grant revoke\nDetail: /cmd help <verb>",
    "fr": "Grammaire : /cmd <verbe> [texte]\nSystème : help lang new-game rules limit cmd list status reset whoami grant revoke\nDétail : /cmd help <verbe>",
    "de": "Grammatik: /cmd <verb> [text]\nSystem: help lang new-game rules limit cmd list status reset whoami grant revoke\nDetail: /cmd help <verb>",
}

# Short usage blurb per system verb (not too long).
VERB_HELP: dict[str, dict[str, str]] = {
    "help": {
        "es": "Uso: /cmd help [verbo]\nLista general, o explica un comando.",
        "en": "Usage: /cmd help [verb]\nOverview, or explain one command.",
        "fr": "Usage : /cmd help [verbe]\nVue d'ensemble, ou explique une commande.",
        "de": "Nutzung: /cmd help [verb]\nÜbersicht oder einen Befehl erklären.",
    },
    "lang": {
        "es": "Uso: /cmd lang es|fr|de|en\nCambia el idioma de la mesa.",
        "en": "Usage: /cmd lang es|fr|de|en\nSets the table language.",
        "fr": "Usage : /cmd lang es|fr|de|en\nChange la langue de la table.",
        "de": "Nutzung: /cmd lang es|fr|de|en\nSprache der Runde setzen.",
    },
    "new-game": {
        "es": "Uso: /cmd new-game <idea>\nAdmin: abre una mesa e inventa verbos.",
        "en": "Usage: /cmd new-game <idea>\nAdmin: opens a table and invents verbs.",
        "fr": "Usage : /cmd new-game <idée>\nAdmin : ouvre une table et invente les verbes.",
        "de": "Nutzung: /cmd new-game <idee>\nAdmin: startet eine Runde und erfindet Verben.",
    },
    "rules": {
        "es": "Uso: /cmd rules [texto]\nMuestra reglas; con texto, añade una (admin).",
        "en": "Usage: /cmd rules [text]\nShows rules; with text, adds one (admin).",
        "fr": "Usage : /cmd rules [texte]\nAffiche les règles ; avec texte, en ajoute (admin).",
        "de": "Nutzung: /cmd rules [text]\nZeigt Regeln; mit Text fügt eine hinzu (Admin).",
    },
    "limit": {
        "es": "Uso: /cmd limit [texto]\nMuestra límites; con texto, añade uno (admin).",
        "en": "Usage: /cmd limit [text]\nShows limits; with text, adds one (admin).",
        "fr": "Usage : /cmd limit [texte]\nAffiche les limites ; avec texte, en ajoute (admin).",
        "de": "Nutzung: /cmd limit [text]\nZeigt Limits; mit Text fügt eines hinzu (Admin).",
    },
    "cmd": {
        "es": "Uso: /cmd cmd list\nLista verbos de sistema y de la partida.",
        "en": "Usage: /cmd cmd list\nLists system and game verbs.",
        "fr": "Usage : /cmd cmd list\nListe les verbes système et de jeu.",
        "de": "Nutzung: /cmd cmd list\nListet System- und Spielverben.",
    },
    "status": {
        "es": "Uso: /cmd status\nFase, título, idioma, reglas y límites.",
        "en": "Usage: /cmd status\nPhase, title, language, rules and limits.",
        "fr": "Usage : /cmd status\nPhase, titre, langue, règles et limites.",
        "de": "Nutzung: /cmd status\nPhase, Titel, Sprache, Regeln und Limits.",
    },
    "reset": {
        "es": "Uso: /cmd reset\nAdmin: cierra la mesa y vuelve al lobby.",
        "en": "Usage: /cmd reset\nAdmin: closes the table back to lobby.",
        "fr": "Usage : /cmd reset\nAdmin : ferme la table (retour lobby).",
        "de": "Nutzung: /cmd reset\nAdmin: schließt die Runde (zurück Lobby).",
    },
    "whoami": {
        "es": "Uso: /cmd whoami\nTu nombre, id de Telegram y si eres admin.",
        "en": "Usage: /cmd whoami\nYour name, Telegram id, and admin flag.",
        "fr": "Usage : /cmd whoami\nTon nom, id Telegram et statut admin.",
        "de": "Nutzung: /cmd whoami\nName, Telegram-Id und Admin-Flag.",
    },
    "grant": {
        "es": "Uso: /cmd grant <id>\nAdmin: da admin de mesa a ese usuario.",
        "en": "Usage: /cmd grant <id>\nAdmin: grants table-admin to that user.",
        "fr": "Usage : /cmd grant <id>\nAdmin : donne le rôle admin de table.",
        "de": "Nutzung: /cmd grant <id>\nAdmin: macht diesen User zum Tisch-Admin.",
    },
    "revoke": {
        "es": "Uso: /cmd revoke <id>\nAdmin: quita admin de mesa a ese usuario.",
        "en": "Usage: /cmd revoke <id>\nAdmin: removes table-admin from that user.",
        "fr": "Usage : /cmd revoke <id>\nAdmin : retire le rôle admin de table.",
        "de": "Nutzung: /cmd revoke <id>\nAdmin: entzieht dem User Tisch-Admin.",
    },
}

_UNKNOWN = {
    "es": "Comando desconocido: {verb}. /cmd cmd list",
    "en": "Unknown command: {verb}. /cmd cmd list",
    "fr": "Commande inconnue : {verb}. /cmd cmd list",
    "de": "Unbekannter Befehl: {verb}. /cmd cmd list",
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


def help_text(game: dict[str, Any], lang: str, topic: str = "") -> str:
    """Overview, or a short usage blurb for one verb."""
    lang = lang if lang in HELP else "es"
    topic = (topic or "").strip().split()[0].lower() if topic else ""
    if not topic:
        return HELP[lang]

    # System verb
    pack = VERB_HELP.get(topic)
    if pack:
        return pack.get(lang) or pack["en"]

    # Game verb from table commands
    for item in game.get("commands") or []:
        if str(item.get("verb") or "").lower() == topic:
            blurb = str(item.get("help") or "").strip()
            if blurb:
                return f"/cmd {topic}\n{blurb}"
            return f"/cmd {topic}"

    return (_UNKNOWN.get(lang) or _UNKNOWN["en"]).format(verb=topic)


def apply_mock(game: dict[str, Any], verb: str, payload: str, lang: str) -> str:
    lang = lang if lang in HELP else "es"
    if verb == "help":
        return help_text(game, lang, payload)
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
