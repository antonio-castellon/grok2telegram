from bridge.parse import parse_text


def test_cmd_new_game():
    c = parse_text("/cmd new-game misterio en un faro")
    assert c is not None
    assert c.verb == "new-game"
    assert "faro" in c.payload


def test_cmd_list():
    c = parse_text("/cmd cmd list")
    assert c is not None
    assert c.verb == "cmd"
    assert c.payload == "list"


def test_lang():
    c = parse_text("/cmd lang de")
    assert c is not None
    assert c.verb == "lang"
    assert c.payload == "de"


def test_ignore_smalltalk():
    assert parse_text("buenos días") is None


def test_alias():
    c = parse_text("cmd join")
    assert c is not None
    assert c.verb == "join"
