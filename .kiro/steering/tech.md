# Tech steering (Lesson 2)

Python 3.10+, venv, RLCard, pytest + hypothesis. S1 optional via S1_URL;
heuristic fallback mandatory and shape-identical. Deterministic heuristic path
(argmax, no RNG in decisions). UI (`web.py`) makes zero extra model calls —
reads LAST probs. Enforce: s1_move returns only legal moves (guard by
membership, fallback to heuristic).
