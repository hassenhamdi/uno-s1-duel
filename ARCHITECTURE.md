# Architecture — uno-s1

RLCard `uno` (2-player, 61 actions, readable legal moves) + typed S1 choices.

```
RLCard state → player.describe (narrative: colors, threat, playable)
  → grounded options (consequences: wild-color advice, UNO alerts, WINS-NOW)
  → s1_move [S1 HTTP | heuristic fallback] → env.step → web.py table
```

S1 sees 1–4 options max. Heuristic mirrors doctrine (shed non-wild, save
wilds, disrupt at UNO). Human seat via terminal (`table.py`) or browser
(`web.py`, live prob bars). RESULTS.md holds 20-game win rates.
