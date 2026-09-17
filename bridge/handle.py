from __future__ import annotations

from typing import Any

from bridge.admin import is_admin
from bridge.config import Config
from bridge.gm_mock import HELP, apply_mock, help_text
from bridge.parse import ADMIN_VERBS, SYSTEM_VERBS, Command, PURGE_SIGNAL
from bridge.store import append_inbox, append_log, save
from bridge.telegram_io import Telegram
from bridge import safety

LOCAL_VERBS = frozenset({"help", "whoami", "grant", "revoke", "lang", "status", "reset", "cmd", "clear", "restart", "unjoin", "rules", "limit"})

def _strip_player_runtime(players: dict) -> dict:
    """Keep seat identity; drop hands/scores/results."""
    out: dict[str, Any] = {}
    for key, val in (players or {}).items():
        if not isinstance(val, dict):
            out[str(key)] = {"id": key, "name": str(val)}
            continue
        out[str(key)] = {
            "id": val.get("id", key),
            "name": val.get("name") or str(val.get("id") or key),
        }
    return out


def _runtime_blob_keys() -> frozenset[str]:
    return frozenset(
        {
            "hands",
            "hand",
            "scores",
            "score",
            "deck",
            "discard",
            "turn",
            "turn_order",
            "current",
            "round",
            "results",
            "winner",
            "bust",
            "stood",
            "plantados",
            "active",
        }
    )


def restart_table(game: dict[str, Any]) -> str:
    """Replay same game: wipe player results and runtime blob, keep rules/commands."""
    lang = game.get("lang") or "es"
    if not (game.get("title") or game.get("commands") or game.get("brief")):
        msg = {
            "es": "No hay partida que reiniciar. /cmd new-game …",
            "en": "No game to restart. /cmd new-game …",
            "fr": "Pas de partie à relancer. /cmd new-game …",
            "de": "Kein Spiel zum Neustart. /cmd new-game …",
        }
        return msg.get(lang, msg["en"])
    game["players"] = _strip_player_runtime(game.get("players") or {})
    blob = dict(game.get("blob") or {})
    drop = _runtime_blob_keys()
    game["blob"] = {k: v for k, v in blob.items() if k not in drop}
    # seated players stay; round restarts
    if game.get("commands"):
        game["phase"] = "playing"
    else:
        game["phase"] = "lobby"
    game["blob"]["turn_order"] = [
        str(p.get("id") or pid) for pid, p in game["players"].items()
    ]
    game["blob"]["turn_i"] = 0
    msg = {
        "es": "Reinicio. Misma mesa, marcadores a cero. /cmd join si faltáis.",
        "en": "Restart. Same table, scores cleared. /cmd join if seats are empty.",
        "fr": "Relance. Même table, scores à zéro. /cmd join si besoin.",
        "de": "Neustart. Gleiche Runde, Punkte weg. /cmd join falls nötig.",
    }
    return msg.get(lang, msg["en"])


def unjoin_player(game: dict[str, Any], uid: int, name: str, target_raw: str) -> str:
    lang = game.get("lang") or "es"
    players = game.setdefault("players", {})
    target = target_raw.strip().lstrip("@")
    if target.isdigit():
        tid = str(int(target))
    else:
        tid = str(uid)
    if tid not in players and str(uid) not in players:
        # try match by name
        hit = None
        for k, v in players.items():
            if isinstance(v, dict) and (v.get("name") or "").lower() == target.lower():
                hit = k
                break
        if hit is None and tid not in players:
            msg = {
                "es": f"{name}: no estabas en la mesa.",
                "en": f"{name}: you were not seated.",
                "fr": f"{name}: pas à la table.",
                "de": f"{name}: nicht am Tisch.",
            }
            return msg.get(lang, msg["en"])
        if hit is not None:
            tid = hit
    if tid in players:
        left = players.pop(tid)
        left_name = left.get("name") if isinstance(left, dict) else name
    else:
        left_name = name
    blob = game.setdefault("blob", {})
    order = [str(x) for x in (blob.get("turn_order") or []) if str(x) != tid]
    blob["turn_order"] = order
    if order:
        blob["turn_i"] = int(blob.get("turn_i") or 0) % len(order)
    else:
        blob["turn_i"] = 0
    msg = {
        "es": f"{left_name} sale. Su turno se salta.",
        "en": f"{left_name} leaves. Their turn is skipped.",
        "fr": f"{left_name} part. Son tour est sauté.",
        "de": f"{left_name} geht. Zug wird übersprungen.",
    }
    return msg.get(lang, msg["en"])



def handle(
    cfg: Config,
    tg: Telegram,
    chat_id: int,
    user: dict[str, Any],
    cmd: Command,
    game: dict[str, Any],
) -> str:
    uid = int(user["id"])
    name = user.get("name") or str(uid)
    admin = is_admin(cfg, tg, chat_id, uid, game)
    game["chat_id"] = chat_id

    if cmd.verb == "whoami":
        return f"{name} id={uid} admin={'yes' if admin else 'no'}"

    if cmd.verb == "help":
        return help_text(game, game.get("lang") or "es", cmd.payload)

    if cmd.verb == "clear":
        from bridge.purge import PURGE_CONFIRM

        lang = game.get("lang") or "es"
        if not admin:
            return "solo admin."
        if cmd.payload.strip().lower() not in PURGE_CONFIRM:
            need = {
                "es": "Borra TODOS los mensajes de cualquiera. Confirma: /cmd clear all",
                "en": "Deletes EVERY message from anyone. Confirm: /cmd clear all",
                "fr": "Efface TOUS les messages. Confirme : /cmd clear all",
                "de": "Löscht ALLE Nachrichten. Bestätigen: /cmd clear all",
            }
            return need.get(lang, need["en"])
        return PURGE_SIGNAL


    if cmd.verb == "unjoin":
        say = unjoin_player(game, uid, name, cmd.payload)
        save(cfg.data_dir, game)
        return say

    if cmd.verb == "restart":
        if not admin:
            return "solo admin."
        say = restart_table(game)
        save(cfg.data_dir, game)
        return say

    if cmd.verb in ADMIN_VERBS and not admin:
        return "solo admin."

    if cmd.verb == "grant" and admin:
        raw = cmd.payload.strip().lstrip("@")
        if raw.isdigit():
            game.setdefault("admins", []).append(int(raw))
            save(cfg.data_dir, game)
            return f"grant {raw}"
        return "grant <id numérico>"

    if cmd.verb == "revoke" and admin:
        raw = cmd.payload.strip().lstrip("@")
        if raw.isdigit():
            game["admins"] = [a for a in game.get("admins") or [] if int(a) != int(raw)]
            save(cfg.data_dir, game)
            return f"revoke {raw}"
        return "revoke <id numérico>"

    if cmd.verb not in SYSTEM_VERBS:
        known = {c["verb"] for c in game.get("commands") or []}
        if cmd.verb not in known:
            # @bot free chat: treat unknown first word as natural language to the GM
            if getattr(cmd, "via_mention", False):
                full = f"{cmd.verb} {cmd.payload}".strip()
                cmd = Command(verb="ask", payload=full, via_mention=True)
            else:
                return f"comando desconocido: {cmd.verb}. /cmd cmd list"

    if cmd.verb == "ask":
        append_log(game, f"{name}: @bot {cmd.payload[:120]}")
        blocked = safety.block_reason_for_payload("ask", cmd.payload)
        if blocked:
            return safety.refusal(blocked, game.get("lang") or "en")
        append_inbox(
            cfg.data_dir,
            {
                "schema": "mesa.v1",
                "chat_id": chat_id,
                "user": {"id": uid, "name": name, "is_admin": admin},
                "lang": game.get("lang") or "es",
                "verb": "ask",
                "payload": cmd.payload,
                "table": {
                    "phase": game.get("phase"),
                    "title": game.get("title"),
                    "brief": game.get("brief"),
                    "rules": game.get("rules"),
                    "limits": game.get("limits"),
                    "commands": game.get("commands"),
                    "blob": game.get("blob"),
                },
            },
        )
        save(cfg.data_dir, game)
        lang = game.get("lang") or "es"
        ack = {
            "es": "Te leo. Un momento…",
            "en": "Reading you. One moment…",
            "fr": "Je te lis. Un instant…",
            "de": "Ich lese mit. Einen Moment…",
        }
        return ack.get(lang, ack["en"])

    append_log(game, f"{name}: /cmd {cmd.verb} {cmd.payload[:80]}")

    needs_brain = cfg.gm_backend == "agent" and cmd.verb not in LOCAL_VERBS
    if needs_brain:
        blocked = safety.block_reason_for_payload(cmd.verb, cmd.payload)
        if blocked:
            return safety.refusal(blocked, game.get("lang") or "en")
        append_inbox(
            cfg.data_dir,
            {
                "schema": "mesa.v1",
                "chat_id": chat_id,
                "user": {"id": uid, "name": name, "is_admin": admin},
                "lang": game.get("lang") or "es",
                "verb": cmd.verb,
                "payload": cmd.payload,
                "table": {
                    "phase": game.get("phase"),
                    "title": game.get("title"),
                    "brief": game.get("brief"),
                    "rules": game.get("rules"),
                    "limits": game.get("limits"),
                    "commands": game.get("commands"),
                    "blob": game.get("blob"),
                },
            },
        )
        save(cfg.data_dir, game)
        # Never leave the group in silence while the Agent drains the inbox.
        lang = game.get("lang") or "es"
        ack = {
            "es": f"Recibido: /cmd {cmd.verb}. Preparo respuesta…",
            "en": f"Got it: /cmd {cmd.verb}. Working on it…",
            "fr": f"Reçu : /cmd {cmd.verb}. Je prépare la réponse…",
            "de": f"OK: /cmd {cmd.verb}. Antwort kommt…",
        }
        return ack.get(lang, ack["en"])

    say = apply_mock(game, cmd.verb, cmd.payload, game.get("lang") or "es")
    save(cfg.data_dir, game)
    return say
