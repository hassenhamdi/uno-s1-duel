"""Lesson 4: properties over randomized UNO states (no server needed)."""
from hypothesis import given, settings, strategies as st
from uno.player import heuristic, s1_move, describe, ground, turn_state

COLORS = ["r", "g", "b", "y"]
FACES = ["0", "1", "5", "9", "skip", "reverse", "draw_2"]
cards = st.builds(lambda c, f: f"{c}-{f}",
                  st.sampled_from(COLORS), st.sampled_from(FACES))
wilds = st.sampled_from(["r-wild", "g-wild_draw_4", "draw"])


@st.composite
def raw_state(draw):
    hand = draw(st.lists(st.one_of(cards, wilds), min_size=1, max_size=10,
                         unique=True))
    legal = draw(st.lists(st.sampled_from(hand + ["draw"]), min_size=1,
                          max_size=4, unique=True))
    return {"hand": hand, "target": draw(st.one_of(cards)),
            "played_cards": [], "legal_actions": legal,
            "num_cards": [len(hand), draw(st.integers(1, 10))],
            "num_players": 2, "current_player": 0}


@given(raw_state())
@settings(max_examples=100)
def test_prop_heuristic_deterministic(raw):
    a = heuristic(raw, raw["legal_actions"])
    b = heuristic(raw, raw["legal_actions"])
    assert a == b and a[0] in raw["legal_actions"]


@given(raw_state())
@settings(max_examples=100)
def test_prop_s1_offline_legal(raw):
    import os
    os.environ.pop("S1_URL", None)
    import importlib
    import uno.player as p
    importlib.reload(p)
    assert p.s1_move(raw, raw["legal_actions"]) in raw["legal_actions"]


@given(raw_state())
@settings(max_examples=100)
def test_prop_state_names_everything(raw):
    s = describe(raw)
    assert str(len(raw["hand"])) in s and raw["target"] in s
    t = turn_state(raw)
    assert ("with ONE card" in t) == (len(raw["hand"]) == 1)


@given(raw_state())
@settings(max_examples=100)
def test_prop_wild_names_color(raw):
    for a in raw["legal_actions"]:
        g = ground(a, raw)
        if "wild" in a.lower() and raw["hand"]:
            assert "color" in g
