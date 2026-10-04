# UNO S1 Duel — what can a zero-shot 0.8B decision model actually do?

A research program in miniature: pit StartLux-Decision-0.8B-Q8_0 (a typed
decision model — no text generation, one forward pass per question) against
real games, and find exactly where it wins, ties, and fails.

**Main result:** UNO, 2-player, RLCard engine —
**22/30 vs random (p≈0.002), 17/30 vs a hand-coded tactician.**
A zero-shot 0.8B plays textbook UNO to a draw against written tactics,
at ~35–85ms per move, with a human seat at a browser table.

## Demo (81s)

<video src="docs/demo.mp4" width="720" controls></video>
*Public video URL for the entry form: attach the YouTube/X upload of this file.*

## The pattern that works

The 0.8B is a **judge of pre-computed verdicts**, not a reasoner:

1. **Narrate the state** — full sentences, never tensors or tags.
   (`"Snake head at (1,1). A snake body is south."` beat `"BODY-DIE"` 0.71 v 0.31.)
2. **Consequence options** — every choice states what happens if picked
   (`"go south into your own neck and die"`, `"sets your best color: red"`).
3. **Shortlist then judge** — cheap heuristic narrows to ≤5, S1 picks.
4. **Code owns rules** — legality, sleep vetoes, stall guards, memory.
   The model never tracks history; the harness does.

Violate any of these and it collapses to uniform noise (measured repeatedly).

## Full scorecard (all reproduced in-repo or linked)

| Game | S1 result | Lesson |
|---|---|---|
| UNO (this repo) | 22/30 rand, 17/30 heur; human table live | narrative + consequences generalize |
| Trivia buzzer | high-conf bucket 4/4; threshold 0.8 settled (n=16) | calibration is the game; margin trigger for recall |
| Battlesnake | survives 20–150 turns, wins FFA; loses food races | grounding 0.31→0.71; strategy gap remains |
| Blackjack | 40% doctrine agreement (full beats trimmed 38v29) | written rules transfer lossily |
| Minesweeper | 6/20 vs 12/20 random (McNemar 1v7, p≈0.07) | coin-flip gambles carry no signal — wrong stage |
| Crafter | dies ~150–250 steps, 0 achievements | sparse long-horizon needs exceed 0.8B |
| 2048 | parked | 100s of board-text calls/game OOM the loop — cost is a constraint |

Negative results kept deliberately: they delimit the envelope.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install rlcard pytest hypothesis requests
# S1 backend (local): llama-server + startlux gguf_server on :8090, then:
S1_URL=http://127.0.0.1:8090/v1/systemone PYTHONPATH=. .venv/bin/python -m uno.match --games 20 --p1 heur
PYTHONPATH=. .venv/bin/python -m uno.web   # human table http://127.0.0.1:5000
PYTHONPATH=. .venv/bin/python spectator.py  # S1-vs-heur broadcast http://127.0.0.1:5001
PYTHONPATH=. .venv/bin/pytest tests/ -q
```

Without `S1_URL`, everything runs on the built-in heuristic fallback
(same shapes, no server needed) — tests and races included.

## Layout

- `uno/player.py` — narrative state, grounded options, S1 + fallback, guards
- `uno/match.py` — seeded races, per-move JSONL, win tables
- `uno/audit.py` — 30-game rules audit (108 conservation, wilds, draws, wins)
- `uno/table.py`, `uno/web.py` — terminal + browser human seats, live prob bars
- `spectator.py`, `verbose_game.py` — broadcast + trace tooling
- `tests/` — unit + hypothesis property tests
- `docs/` — RESULTS, SUPPORTING-BUILDS, exam checklist

## Model & license note

Decisions via StartLux-Decision-0.8B-Q8_0 (CC BY-NC 4.0, research use).
Code here is the author's own. Built with Kiro + OpenCode tooling.
