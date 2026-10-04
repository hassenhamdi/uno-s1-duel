"""Seed-matched UNO: S1 vs random/heuristic. Win rate + ms/move."""
import argparse
import random
import time
import rlcard
from .player import s1_move, heuristic


def play(seed, p0="s1", p1="rand", max_steps=500, full_log=None):
    env = rlcard.make("uno")
    env.seed(seed) if hasattr(env, "seed") else None
    st, player = env.reset()
    rng = random.Random(seed)
    log, ms, n = [], [], 0
    mem = {}
    last_wild = None
    kinds = {0: p0, 1: p1}
    for _ in range(max_steps):
        raw = st["raw_obs"]
        from rlcard.games.uno.utils import ACTION_SPACE
        readable = list(raw["legal_actions"])
        name_to_id = {a: ACTION_SPACE[a] for a in readable}
        kind = kinds[player]
        t0 = time.time()
        via = kind
        if kind == "s1":
            mv = s1_move({**raw, "legal_actions": readable}, readable, log, mem)
            via = log[-1].get("via", "s1") if log else "s1"
        elif kind == "heur":
            mv, _, _ = heuristic({**raw, "legal_actions": readable}, readable)
        else:
            mv = rng.choice(readable)
        ms.append((time.time() - t0) * 1000)
        n += 1
        if "wild" in mv:
            last_wild = mv
        if full_log is not None:
            from .player import fresh_target
            full_log.append({"seed": seed, "turn": n, "player": player,
                             "hands": list(raw["num_cards"]),
                             "target": fresh_target(raw["target"], last_wild),
                             "legal": readable,
                             "move": mv, "via": via})
        st, player = env.step(name_to_id[mv])
        if env.is_over():
            break
    w = env.get_payoffs() if hasattr(env, "get_payoffs") else None
    import numpy as _np
    winner = int(_np.argmax(w)) if w is not None else None
    return {"seed": seed, "winner": winner,
            "payoffs": [float(x) for x in w] if w is not None else None,
            "ms": round(sum(ms) / max(1, len(ms)), 1),
            "moves": n, "log": log}


def decode(env, ids):
    g = env.game
    if hasattr(g, "actions"):
        acts = g.actions
        out = []
        for i in ids:
            a = acts[i]
            out.append(str(a) if not hasattr(a, "get_string") else a.get_string())
        return out
    raise RuntimeError("no action decode")


def action_id(env, name):
    g = env.game
    for i, a in enumerate(g.actions):
        s = str(a) if not hasattr(a, "get_string") else a.get_string()
        if s == name:
            return i
    raise KeyError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=10)
    ap.add_argument("--p1", default="rand", choices=["rand", "heur"])
    a = ap.parse_args()
    res = [play(s, "s1", a.p1) for s in range(1, a.games + 1)]
    sw = sum(1 for r in res if r["winner"] == 0)
    print(f"S1 wins {sw}/{len(res)} vs {a.p1}")
    for r in res:
        print(f"  seed {r['seed']}: winner=P{r['winner']} moves={r['moves']} ms={r['ms']}")
    ms = [r["ms"] for r in res]
    print(f"mean ms/move: {sum(ms) / len(ms):.1f}")


if __name__ == "__main__":
    main()
