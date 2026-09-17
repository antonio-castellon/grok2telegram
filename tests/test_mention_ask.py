from bridge.parse import Command
from bridge.handle import handle
from bridge.config import Config
from pathlib import Path


class _TG:
    def get_chat_administrators(self, chat_id):
        return {83216105}


def test_unknown_mention_becomes_ask_ack(tmp_path):
    cfg = Config(
        telegram_bot_token="x",
        admin_telegram_ids=frozenset({83216105}),
        gm_backend="agent",
        allowed_chat_ids=frozenset(),
        data_dir=tmp_path,
    )
    game = {
        "chat_id": -1,
        "lang": "en",
        "phase": "playing",
        "title": "21",
        "brief": "",
        "rules": [],
        "limits": [],
        "commands": [{"verb": "join", "help": "sit"}],
        "admins": [],
        "players": {},
        "blob": {},
        "log": [],
    }
    cmd = Command(verb="what", payload="are the rules?", via_mention=True)
    say = handle(cfg, _TG(), -1, {"id": 83216105, "name": "Antonio"}, cmd, game)
    assert "moment" in say.lower() or "Reading" in say
    inbox = (tmp_path / "inbox.jsonl").read_text()
    assert '"verb": "ask"' in inbox
    assert "what are the rules?" in inbox


def test_known_game_verb_mention_not_ask(tmp_path):
    cfg = Config(
        telegram_bot_token="x",
        admin_telegram_ids=frozenset({83216105}),
        gm_backend="agent",
        allowed_chat_ids=frozenset(),
        data_dir=tmp_path,
    )
    game = {
        "chat_id": -1,
        "lang": "en",
        "phase": "playing",
        "title": "21",
        "commands": [{"verb": "join", "help": "sit"}],
        "rules": [],
        "limits": [],
        "admins": [],
        "players": {},
        "blob": {},
        "log": [],
        "brief": "",
    }
    cmd = Command(verb="join", payload="", via_mention=True)
    say = handle(cfg, _TG(), -1, {"id": 1, "name": "Bob"}, cmd, game)
    # join needs brain → ack, inbox verb join not ask
    assert "Working" in say or "Got it" in say or "moment" in say.lower()
    inbox = (tmp_path / "inbox.jsonl").read_text()
    assert '"verb": "join"' in inbox
