# UNO S1 Duel — zero-shot 0.8B vs noise, tacticians, and humans

Kiro University final-exam build. RLCard UNO driven by typed S1 decisions
with narrative state + consequence options; heuristic fallback; browser table
with live probability bars; human seat.

## Quickstart
```bash
python3 -m venv .venv && .venv/bin/pip install rlcard pytest hypothesis requests
S1_URL=http://127.0.0.1:8090/v1/systemone PYTHONPATH=. .venv/bin/python -m uno.match --games 20 --p1 heur
PYTHONPATH=. .venv/bin/python -m uno.web   # http://127.0.0.1:5000
PYTHONPATH=. .venv/bin/pytest tests/ -q
```

## Results (StartLux-0.8B-Q8_0, committed in docs/RESULTS.md)
- vs random: 22/30 (p≈0.002) · vs heuristic: 17/30 (even) · ~35–85ms/move

## Exam map
L1 `.kiro/specs/uno-s1/` · L2 steering · L3 hooks · L4 hypothesis properties
L5 powers.json · L6 mcp.json · L7 agents · Bonus2 `powers/uno-tuner/`
(Bonus1 skipped: paid only) · Supporting builds: `docs/SUPPORTING-BUILDS.md`
