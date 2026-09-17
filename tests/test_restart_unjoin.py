from bridge.handle import restart_table, unjoin_player
from bridge.parse import parse_text, ADMIN_VERBS, SYSTEM_VERBS


def test_verbs_registered():
    assert "restart" in SYSTEM_VERBS
    assert "unjoin" in SYSTEM_VERBS
    assert "restart" in ADMIN_VERBS
    assert parse_text("/cmd restart").verb == "restart"
    assert parse_text("/cmd unjoin").verb == "unjoin"


def test_restart_clears_runtime_keeps_rules():
    game = {
        "lang": "en",
        "title": "21",
        "brief": "cards",
        "commands": [{"verb": "join", "help": "sit"}],
        "players": {"1": {"id": 1, "name": "A", "score": 21}},
        "blob": {"hands": {}, "awaiting": "keep"},
        "phase": "playing",
    }
    say = restart_table(game)
    assert "Restart" in say
    assert game["players"]["1"] == {"id": 1, "name": "A"}
    assert "hands" not in game["blob"]
    assert game["blob"]["awaiting"] == "keep"
    assert game["title"] == "21"


def test_unjoin_skips_turn():
    game = {
        "lang": "es",
        "players": {"1": {"id": 1, "name": "A"}, "2": {"id": 2, "name": "B"}},
        "blob": {"turn_order": ["1", "2"], "turn_i": 0},
    }
    say = unjoin_player(game, 1, "A", "")
    assert "sale" in say
    assert "1" not in game["players"]
    assert game["blob"]["turn_order"] == ["2"]
