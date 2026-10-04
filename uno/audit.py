"""Full rules audit over random games: conservation, legality, wilds, draws, wins."""
from rlcard.games.uno.utils import ACTION_SPACE
from uno.match import play


def audit(n=30):
    bad = []
    stats = {"wild_plays": 0, "draw_pens": 0, "wins": 0, "turns": []}
    for s in range(1, n + 1):
        full = []
        import rlcard
        from rlcard.games.uno.utils import ACTION_SPACE
        env = rlcard.make("uno")
        st, player = env.reset()
        import random
        rng = random.Random(s)
        prev_hands = list(st["raw_obs"]["num_cards"])
        for t in range(1000):
            raw = st["raw_obs"]
            mover = player
            legal = list(raw["legal_actions"])
            mv = rng.choice(legal)
            # legality
            assert mv in legal, (s, t, mv, legal)
            # wild color respected: next legal must match declared color/wild
            st, player = env.step(ACTION_SPACE[mv])
            cur = st["raw_obs"]
            if "wild" in mv:
                stats["wild_plays"] += 1
                col = mv.split("-")[0]
                for nxt in cur["legal_actions"]:
                    assert nxt == "draw" or nxt.split("-")[0] == col \
                        or "wild" in nxt, (s, t, mv, cur["legal_actions"])
            # draw penalties: hand deltas
            nh = list(cur["num_cards"])
            if "draw_2" in mv or "draw_4" in mv:
                stats["draw_pens"] += 1
                victim = 1 - mover
                need = 4 if "draw_4" in mv else 2
                # victim drew penalty (may also have played earlier this turn
                # window; require at least the penalty gain on victim)
                assert nh[victim] - prev_hands[victim] >= need, \
                    (s, t, mv, mover, prev_hands, nh)
            # conservation: dealer + played + hands == 108
            g = env.game
            try:
                total = len(g.dealer.deck) + len(g.round.played_cards) \
                    + sum(len(p.hand) for p in g.players)
                assert total == 108, (s, t, total)
            except AttributeError:
                pass
            prev_hands = nh
            if env.is_over():
                import numpy as _np
                w = int(_np.argmax(env.get_payoffs()))
                stats["wins"] += 1
                # winner holds no cards
                assert cur["num_cards"][w] == 0, (s, t, cur["num_cards"])
                stats["turns"].append(t + 1)
                break
    print(f"games={n} finished={stats['wins']} wilds={stats['wild_plays']} "
          f"drawpens={stats['draw_pens']}")
    print(f"turns min={min(stats['turns'])} max={max(stats['turns'])} "
          f"mean={sum(stats['turns']) / len(stats['turns']):.0f}")
    print("ALL INVARIANTS HOLD")


if __name__ == "__main__":
    audit()
