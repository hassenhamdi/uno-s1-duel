"""Human-vs-S1 UNO table. You play seat 1, S1 plays seat 0. First to shed wins."""
import argparse
import select
import sys
import time
import rlcard
from rlcard.games.uno.utils import ACTION_SPACE
from .player import s1_move


def timed_input(prompt, timeout=30):
    print(prompt, end="", flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if not ready:
        return None
    return sys.stdin.readline().strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args()
    env = rlcard.make("uno")
    st, player = env.reset()
    TABLE_MEM = {}
    log = []
    while not env.is_over():
        raw = st["raw_obs"]
        readable = list(raw["legal_actions"])
        if player == 1:
            print(f"\nTop: {raw['target']} | foe holds {raw['num_cards'][0]} | "
                  f"your hand ({len(raw['hand'])}):")
            for i, c in enumerate(readable, 1):
                print(f"  {i}. {c}")
            ans = timed_input(f"play 1-{len(readable)} ({a.timeout}s): ",
                              a.timeout)
            if ans is None or not ans.isdigit() \
                    or not (1 <= int(ans) <= len(readable)):
                print("  too slow/invalid → first legal played")
                mv = readable[0]
            else:
                mv = readable[int(ans) - 1]
            print(f"  you play {mv}")
        else:
            t0 = time.time()
            mv = s1_move({**raw, "legal_actions": readable}, readable, log, TABLE_MEM)
            dt = (time.time() - t0) * 1000
            print(f"\nTop: {raw['target']} | S1 plays {mv} "
                  f"({[e for e in log[-1:]][0]['conf']}, {dt:.0f}ms)")
        st, player = env.step(ACTION_SPACE[mv])
    import numpy as _np
    w = int(_np.argmax(env.get_payoffs()))
    print(f"\n== {'YOU win!' if w == 1 else 'S1 wins.'} "
          f"(payoffs {list(env.get_payoffs())}) ==")


if __name__ == "__main__":
    main()
