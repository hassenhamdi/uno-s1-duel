# UNO Tuner skill

Activates on: "duel match", "tune prompts", "win rate".

## Workflow
1. Baseline: 20-game race vs rand AND vs heur; record both scores.
2. Change exactly one prompt surface (one criterion sentence, one state line,
   one threshold); never touch legality/mapping for score.
3. Re-race identical seeds; keep iff combined win rate improves.
4. Log the delta in docs/RESULTS.md with the diff quoted.
