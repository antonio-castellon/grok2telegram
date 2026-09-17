from __future__ import annotations

from typing import Any

HELP = {
    "es": (
        "Gramática:\n"
        "/cmd <verbo> [texto]\n"
        "@bot <verbo> [texto]\n"
        "@bot <texto libre> → hablas con el GM de la mesa\n"
        "Sistema: help lang new-game rules limit cmd list status reset restart unjoin whoami grant revoke clear\n"
        "Detalle: /cmd help <verbo> | /cmd help extended"
    ),
    "en": (
        "Grammar:\n"
        "/cmd <verb> [text]\n"
        "@bot <verb> [text]\n"
        "@bot <free text> → talk to the table GM\n"
        "System: help lang new-game rules limit cmd list status reset restart unjoin whoami grant revoke clear\n"
        "Detail: /cmd help <verb> | /cmd help extended"
    ),
    "fr": (
        "Grammaire :\n"
        "/cmd <verbe> [texte]\n"
        "@bot <verbe> [texte]\n"
        "@bot <texte libre> → tu parles au GM de la table\n"
        "Système : help lang new-game rules limit cmd list status reset restart unjoin whoami grant revoke clear\n"
        "Détail : /cmd help <verbe> | /cmd help extended"
    ),
    "de": (
        "Grammatik:\n"
        "/cmd <verb> [text]\n"
        "@bot <verb> [text]\n"
        "@bot <freier Text> → du sprichst mit dem Tisch-GM\n"
        "System: help lang new-game rules limit cmd list status reset restart unjoin whoami grant revoke clear\n"
        "Detail: /cmd help <verb> | /cmd help extended"
    ),
}


# Short usage blurb per system verb (not too long).
VERB_HELP: dict[str, dict[str, str]] = {
    "ask": {
        "es": "Uso: @bot <texto>\nHabla al GM en lenguaje natural.",
        "en": "Usage: @bot <text>\nTalk to the GM in natural language.",
        "fr": "Usage : @bot <texte>\nParle au GM en langage naturel.",
        "de": "Nutzung: @bot <text>\nFrei mit dem GM sprechen.",
    },
    "help": {
        "es": "Uso: /cmd help [verbo|extended]\nLista, un comando, o catálogo completo.",
        "en": "Usage: /cmd help [verb|extended]\nOverview, one command, or full catalog.",
        "fr": "Usage : /cmd help [verbe|extended]\nVue d'ensemble, une commande, ou catalogue.",
        "de": "Nutzung: /cmd help [verb|extended]\nÜbersicht, ein Befehl, oder Katalog.",
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
    "clear": {
        "es": "Uso: /cmd clear all\nAdmin: borra mensajes recientes del chat (confirma con all).",
        "en": "Usage: /cmd clear all\nAdmin: deletes recent chat messages (confirm with all).",
        "fr": "Usage : /cmd clear all\nAdmin : efface les messages récents (confirmer avec all).",
        "de": "Nutzung: /cmd clear all\nAdmin: löscht aktuelle Chat-Nachrichten (mit all bestätigen).",
    },
    "restart": {
        "es": "Uso: /cmd restart\nAdmin: misma mesa, borra marcadores y reinicia la ronda.",
        "en": "Usage: /cmd restart\nAdmin: same table, clear scores and restart the round.",
        "fr": "Usage : /cmd restart\nAdmin : même table, scores à zéro, nouvelle manche.",
        "de": "Nutzung: /cmd restart\nAdmin: gleiche Runde, Punkte weg, Neustart.",
    },
    "unjoin": {
        "es": "Uso: /cmd unjoin [id]\nSales de la mesa; tu turno se salta.",
        "en": "Usage: /cmd unjoin [id]\nLeave the table; your turn is skipped.",
        "fr": "Usage : /cmd unjoin [id]\nQuitte la table ; ton tour est sauté.",
        "de": "Nutzung: /cmd unjoin [id]\nTisch verlassen; Zug wird übersprungen.",
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


# Ultra-short blurbs for the phone-width extended catalog (INNER≈24).
VERB_SHORT: dict[str, dict[str, str]] = {
    "ask": {"es": "hablar al GM", "en": "talk to the GM", "fr": "parler au GM", "de": "mit GM reden"},
    "help": {"es": "lista o detalla un cmd", "en": "list or explain a cmd", "fr": "liste ou explique", "de": "Liste oder Erklärung"},
    "lang": {"es": "idioma de la mesa", "en": "set table language", "fr": "langue de la table", "de": "Sprache setzen"},
    "new-game": {"es": "admin: nueva partida", "en": "admin: start a game", "fr": "admin: nouvelle partie", "de": "Admin: neues Spiel"},
    "rules": {"es": "ver/añadir reglas", "en": "show/add rules", "fr": "voir/ajouter règles", "de": "Regeln zeigen/add"},
    "limit": {"es": "ver/añadir límites", "en": "show/add limits", "fr": "voir/ajouter limites", "de": "Limits zeigen/add"},
    "cmd": {"es": "listar verbos", "en": "list verbs", "fr": "lister verbes", "de": "Verben listen"},
    "status": {"es": "estado de la mesa", "en": "table status", "fr": "état de la table", "de": "Tisch-Status"},
    "reset": {"es": "admin: cierra mesa", "en": "admin: close table", "fr": "admin: ferme table", "de": "Admin: Runde zu"},
    "restart": {"es": "admin: reinicia ronda", "en": "admin: restart round", "fr": "admin: relance", "de": "Admin: Neustart"},
    "unjoin": {"es": "salir; salta turno", "en": "leave; skip turn", "fr": "partir; saute tour", "de": "gehen; Zug skip"},
    "whoami": {"es": "tu id y admin", "en": "your id and admin", "fr": "ton id et admin", "de": "Id und Admin"},
    "grant": {"es": "admin: dar admin", "en": "admin: grant admin", "fr": "admin: donner admin", "de": "Admin: Recht geben"},
    "revoke": {"es": "admin: quitar admin", "en": "admin: revoke admin", "fr": "admin: retirer admin", "de": "Admin: Recht weg"},
    "clear": {"es": "admin: borrar msgs", "en": "admin: delete msgs", "fr": "admin: effacer msgs", "de": "Admin: Msgs löschen"},
}


def _one_line(blurb: str, limit: int = 22) -> str:
    """Collapse multi-line usage into a short phone-width line."""
    parts = [p.strip() for p in (blurb or "").splitlines() if p.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        line = parts[0]
    else:
        line = parts[1] if parts[0].lower().startswith(("uso:", "usage", "nutzung", "usage :")) else parts[-1]
    for prefix in ("Uso: ", "Usage: ", "Usage : ", "Nutzung: "):
        if line.startswith(prefix):
            line = line[len(prefix) :]
    line = " ".join(line.split())
    if len(line) > limit:
        line = line[: limit - 1].rstrip() + "…"
    return line


def _entry_block(verb: str, short: str) -> list[str]:
    """Command, dash ruler, explanation — readable inside WIDTH=28 cards."""
    verb = (verb or "").strip()
    short = (short or "").strip() or verb
    ruler = "-" * max(8, min(22, max(len(verb), 8)))
    return [verb, ruler, short]


def help_extended(game: dict[str, Any], lang: str) -> str:
    """All commands: verb / dashes / short explanation (system + game)."""
    lang = lang if lang in HELP else "es"
    blocks: list[list[str]] = []
    order = [
        "ask",
        "help",
        "lang",
        "new-game",
        "rules",
        "limit",
        "cmd",
        "status",
        "reset",
        "restart",
        "unjoin",
        "whoami",
        "grant",
        "revoke",
        "clear",
    ]
    for verb in order:
        pack = VERB_SHORT.get(verb) or {}
        short = pack.get(lang) or pack.get("en")
        if not short:
            long_pack = VERB_HELP.get(verb) or {}
            short = _one_line(long_pack.get(lang) or long_pack.get("en") or "", 22)
        blocks.append(_entry_block(verb, short or verb))
    for item in game.get("commands") or []:
        verb = str(item.get("verb") or "").strip()
        if not verb or verb in VERB_HELP:
            continue
        blurb = str(item.get("help") or "").strip() or verb
        blocks.append(_entry_block(verb, _one_line(blurb, 22)))
    lines: list[str] = []
    for i, block in enumerate(blocks):
        if i:
            lines.append("---")  # skin.DIV → horizontal rule inside the card
        lines.extend(block)
    return "\n".join(lines)


def help_text(game: dict[str, Any], lang: str, topic: str = "") -> str:
    """Overview, extended catalog, or a short usage blurb for one verb."""
    lang = lang if lang in HELP else "es"
    topic = (topic or "").strip().split()[0].lower() if topic else ""
    if not topic:
        return HELP[lang]
    if topic in {"extended", "all", "full", "extenso", "completo"}:
        return help_extended(game, lang)

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
        sys_ = "help lang new-game rules limit cmd status reset restart unjoin whoami grant revoke clear"
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
