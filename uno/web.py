"""Browser table: stdlib HTTP, clickable cards, live S1 probs. No deps.
Run: python -m uno.web  ->  http://127.0.0.1:5000
"""
import json
import os
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import rlcard
from rlcard.games.uno.utils import ACTION_SPACE
from .player import s1_move, LAST

HERE = os.path.dirname(os.path.abspath(__file__))
S1 = "http://127.0.0.1:8090/v1/systemone"
wins = {"you": 0, "s1": 0}
last_probs, last_state = [], "booting"
lock = threading.Lock()


def new_game(seed=None):
    import random
    env = rlcard.make("uno")
    st, player = env.reset()
    return {"env": env, "st": st, "player": player,
            "seed": seed if seed is not None else random.randint(1, 9999),
            "turns": 0, "since_play": 0, "stalled": False, "mem": {}, "wild": None}


GAME = new_game(1)


def snap(msg=""):
    global last_probs
    st = GAME["st"]
    raw = st["raw_obs"]
    over = ""
    if GAME.get("stalled"):
        over = "Draw — 40 turns with no card played. New game?"
    elif GAME["env"].is_over():
        import numpy as _np
        w = int(_np.argmax(GAME["env"].get_payoffs()))
        wins["you" if w == 1 else "s1"] += 1
        over = "YOU win!" if w == 1 else "S1 wins."
    try:
        deck_n = len(GAME["env"].game.dealer.deck)
    except Exception:
        deck_n = -1
    from .player import fresh_target as _ft
    return {"top": _ft(raw["target"], GAME.get("wild")), "foe_n": raw["num_cards"][0],
            "hand": raw["hand"] if GAME["player"] == 1 else [],
            "legal": list(raw["legal_actions"]) if GAME["player"] == 1 else [],
            "last_probs": last_probs, "wins": wins, "over": over,
            "msg": msg, "turns": GAME["turns"], "deck": deck_n}


def s1_turn():
    global last_probs
    mv, dt = "?", 0.0
    for _ in range(500):
        st = GAME["st"]
        raw = st["raw_obs"]
        readable = list(raw["legal_actions"])
        t0 = __import__("time").time()
        mv = s1_move({**raw, "legal_actions": readable}, readable, None, GAME["mem"])
        dt = (__import__("time").time() - t0) * 1000
        last_probs = [(k, round(float(v), 3)) for k, v in LAST["probs"]]
        GAME["st"], GAME["player"] = GAME["env"].step(ACTION_SPACE[mv])
        if "wild" in mv:
            GAME["wild"] = mv
        GAME["turns"] += 1
        GAME["since_play"] = 0 if mv != "draw" else GAME["since_play"] + 1
        if GAME["since_play"] > 40:
            GAME["stalled"] = True
            break
        if GAME["env"].is_over() or GAME["player"] == 1:
            break
    return f"S1 played {mv} ({dt:.0f}ms)"


class H(BaseHTTPRequestHandler):
    def _send(self, obj, ctype="application/json"):
        if isinstance(obj, str):
            data, ctype = obj.encode(), "text/html"
        else:
            data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(open(os.path.join(HERE, "web_index.html")).read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global GAME, last_probs
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        with lock:
            if self.path == "/new":
                import random
                GAME = new_game(random.randint(1, 99999))
                # S1 opens if it starts
                msg = ""
                if GAME["player"] == 0:
                    msg = s1_turn()
                self._send({**snap(), "msg": msg})
            elif self.path == "/move":
                st = GAME["st"]
                raw = st["raw_obs"]
                readable = list(raw["legal_actions"])
                i = body.get("i", 0)
                mv = readable[max(0, min(i, len(readable) - 1))]
                GAME["st"], GAME["player"] = GAME["env"].step(
                    ACTION_SPACE[mv])
                if "wild" in mv:
                    GAME["wild"] = mv
                GAME["turns"] += 1
                GAME["since_play"] = 0 if mv != "draw" \
                    else GAME["since_play"] + 1
                if GAME["since_play"] > 40:
                    GAME["stalled"] = True
                msg = f"you played {mv}"
                if not GAME["env"].is_over() and GAME["player"] == 0:
                    msg += "; " + s1_turn()
                self._send({**snap(), "msg": msg})
            else:
                self.send_response(404)
                self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("UNO vs S1 at http://127.0.0.1:5000")
    ThreadingHTTPServer(("127.0.0.1", 5000), H).serve_forever()
