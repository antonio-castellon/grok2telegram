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


def test_mention_help_all():
    c = parse_text("@grok_maser_game_bot help all", bot_username="grok_maser_game_bot")
    assert c is not None
    assert c.verb == "help"
    assert c.payload == "all"


def test_mention_case_insensitive():
    c = parse_text("@Grok_Maser_Game_Bot status", bot_username="grok_maser_game_bot")
    assert c is not None
    assert c.verb == "status"


def test_mention_wrong_bot_ignored():
    assert parse_text("@other_bot help", bot_username="grok_maser_game_bot") is None


def test_mention_alone_is_help():
    c = parse_text("@grok_maser_game_bot", bot_username="grok_maser_game_bot")
    assert c is not None
    assert c.verb == "help"


def test_cmd_at_botname():
    c = parse_text("/cmd@grok_maser_game_bot whoami")
    assert c is not None
    assert c.verb == "whoami"


def test_mention_freeform_non_verb_token():
    c = parse_text("@grok_maser_game_bot ¿quién gana?", bot_username="grok_maser_game_bot")
    assert c is not None
    assert c.verb == "ask"
    assert "gana" in c.payload.lower()
    assert c.via_mention is True


def test_mention_english_words_parsed_as_verb_for_handle():
    # Tidy tokens parse as verbs; handle promotes unknowns to ask.
    c = parse_text("@grok_maser_game_bot what are the rules?", bot_username="grok_maser_game_bot")
    assert c is not None
    assert c.verb == "what"
    assert c.via_mention is True


def test_mention_known_verb_still_command():
    c = parse_text("@grok_maser_game_bot join", bot_username="grok_maser_game_bot")
    assert c is not None
    assert c.verb == "join"
    assert c.via_mention is True
