# EXAM SUBMISSION checklist (UNO as main demo)

First GitHub commit must be ≥ Sept 21, 2026 — committing now qualifies.

| Lesson | Evidence in this repo |
|---|---|
| 1 Spec-driven | `.kiro/specs/uno-s1-duel/{requirements,design,tasks}.md` (EARS) |
| 2 Steering | `.kiro/steering/{product,tech,structure}.md` |
| 3 Hooks | `.kiro/hooks/{lint-on-save,test-on-save}.json` (PostFileSave) |
| 4 PBT | `tests/test_uno_property.py` (hypothesis, 100 examples) + pytest log |
| 5 Powers | `.kiro/powers.json` + `powers/uno-tuner/` via "duel match" |
| 6 MCP | `.kiro/mcp.json` (fetch + filesystem) |
| 7 Agents | `.kiro/agents/{table-tuner,game-logic}.json` |
| Bonus 1 | SKIPPED (paid only; optional) |
| Bonus 2 | `powers/uno-tuner/{plugin.json,skills/,mcp.json}` |
| Real functionality | RLCard UNO vs rand/heur/human + browser table w/ live probs |
| Program depth | `docs/SUPPORTING-BUILDS.md` (7 builds, lessons absorbed) |

Steps: new public repo → push → screenshots (pytest, browser table, race table)
→ entry form before deadline.
