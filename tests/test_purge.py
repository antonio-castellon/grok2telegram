from bridge.purge import PURGE_CONFIRM, ids_for_purge


def test_ids_for_purge_window():
    ids = ids_for_purge(1000)
    assert ids[0] == 1000
    assert ids[-1] == 501
    assert len(ids) == 500


def test_ids_for_purge_extra():
    ids = ids_for_purge(10, extra=[3, 999])
    assert 3 in ids
    assert 999 not in ids


def test_purge_confirm():
    assert "all" in PURGE_CONFIRM
    assert "todo" in PURGE_CONFIRM
