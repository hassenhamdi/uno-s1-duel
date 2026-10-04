"""UNO player tests (no server needed)."""
from uno.player import heuristic, ground, describe


def raw():
    return {"hand": ["r-2", "b-skip", "wild"], "target": "b-2",
            "played_cards": ["b-2"], "legal_actions": ["r-2", "b-skip"],
            "num_cards": [3, 5], "num_players": 2, "current_player": 0}


def test_heuristic_sheds_nonwild():
    mv, c, _ = heuristic(raw(), ["r-2", "b-skip"])
    assert mv in ("r-2", "b-skip") and 0 <= c <= 1


def test_heuristic_draw_when_nothing():
    r = raw()
    mv, _, _ = heuristic(r, ["draw"])
    assert mv == "draw"


def test_ground_mentions_wild_value():
    g = ground("wild-r", raw())
    assert "color" in g and ("best" in g or "saved" in g)


def test_describe_counts():
    assert "3" in describe(raw()) and "b-2" in describe(raw())


def test_s1_offline_shape():
    import os
    os.environ.pop("S1_URL", None)
    import importlib
    import uno.player as p
    importlib.reload(p)
    log = []
    mv = p.s1_move(raw(), ["r-2", "b-skip"], log)
    assert mv in ("r-2", "b-skip") and len(log) == 1


def test_stall_guard_forces_play():
    import os
    os.environ.pop("S1_URL", None)
    import importlib
    import uno.player as p
    importlib.reload(p)
    raw = {"hand": ["r-2", "b-5"], "target": "b-2",
           "played_cards": ["b-2"], "legal_actions": ["draw", "b-5"],
           "num_cards": [2, 5], "num_players": 2, "current_player": 0}
    mem = {"consec_draws": 3, "prev_hand": ["r-2", "b-5"]}
    mv = p.s1_move(raw, ["draw", "b-5"], None, mem)
    assert mv == "b-5"


def test_mem_tracks_hands():
    import os
    os.environ.pop("S1_URL", None)
    import importlib
    import uno.player as p
    importlib.reload(p)
    mem = {}
    p.s1_move(raw(), ["r-2", "b-skip"], None, mem)
    assert mem["prev_hand"] == raw()["hand"]
    assert mem["consec_draws"] >= 0
