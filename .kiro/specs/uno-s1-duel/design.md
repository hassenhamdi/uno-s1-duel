# Design — uno-s1-duel (Lesson 1)

## Modules (`uno/`)
- `player.py` — `describe` (narrative state), `ground` (consequences),
  `turn_state`, `heuristic`, `s1_move` (+`LAST` probs for UI), `buzz n/a`.
- `match.py` — seeded RLCard runner, ACTION_SPACE id mapping, W/L table.
- `table.py` — terminal human seat (timed input, live conf+ms).
- `web.py` + `web_index.html` — browser table, clickable UNO-look cards,
  live S1 probability bars, running score.

## Decision flow
RLCard raw_obs → describe+ground → S1 choice (2-4 opts) → env.step(id).
Fallback path byte-identical shape. UI reads LAST probs (no extra calls).

## Tests (Lesson 4): heuristic determinism, legality always, prompt content
(properties over randomized hands), WINS-NOW annotation presence.
