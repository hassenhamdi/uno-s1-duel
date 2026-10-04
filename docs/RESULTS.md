# UNO results (StartLux-0.8B-Q8_0, grounded prompts, Oct 2026)

| Opponent | Score | n | Notes |
|---|---|---|---|
| random | 7/10 then 15/20 | 30 | combined 22/30, p≈0.002 — genuinely above chance |
| heuristic (shed non-wild, save wilds, UNO defense) | 5/10 then 12/20 | 30 | combined 17/30, leans positive, n.s. |

Mean latency 35–85ms/move (server variance, not game variance).
Prompt recipe that got here: narrative turn state + per-option consequences
(colors held, foe threat tiers, wild-color advice, WINS-NOW hint).

## Tuning log (table-tuner agent, Oct 4 2026)

### Change 1: Explicit UNO defense (foe-at-1-card threat) — REJECTED
**Attempted diff:**
```diff
- threat = ("UNO! Opponent wins next turn unless disrupted."
+ threat = ("DANGER! Foe has ONE card left — wins next turn unless disrupted. MUST play skip/reverse/draw-2/wild-draw-4 OR they win."
```

**A/B race (seeds 1-20, heuristic opponent):**
- Baseline A: 12/20 vs heur
- Variant B: 11/20 vs heur (55%)
- Delta: -1 win (-5% rate)

**Verdict:** REJECTED. More explicit threat language + enumerated disruption moves DECREASED win rate. The original concise "UNO! Opponent wins next turn unless disrupted" performs better. Hypothesis: over-specification may have added noise or changed the decision context unfavorably. Reverted to baseline.
