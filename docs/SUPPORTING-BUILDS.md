# Supporting builds as lessons

The UNO demo stands on a program of S1-vs-game experiments. Each taught one
load-bearing lesson now baked into `uno/player.py`:

| Build | Lesson absorbed |
|---|---|
| `mines-s1-duel` | Order bias is real: shuffle options, log position index; state-seed the shuffle for reproducible races. Coin-flip gambles carry no signal — don't stage S1 where nothing discriminates. |
| `battlesnake-s1` | Narrative scene grounding (0.31→0.71): describe the world in sentences, never abstract tags. Verified by stark-prompt A/B. |
| `blackjack-s1` | Written doctrine transfers lossily (38/95 full beats 29/95 trimmed); over-double/over-stand bias. Judge-of-verdicts, not applier-of-rules. |
| `trivia-s1-buzzer` | Confidence buzzer (0.8 versus, margin for recall); verify-mode tie 3/10 — hints route knowledge, don't create it. Calibration buckets as evidence. |
| `crafter-s1-decision` | Full Kiro exam exemplar + prompt-input doctrine + code-side guards; S1-0.8B live stack docs; range-gated `do`-spam fix; upstream nondeterminism hunt. |
| `game2048-s1` | Parked: hundreds of board-text calls/game OOMs the loop. Cost-per-game is a design constraint. |
| `strategy-decision-model` | TS reference: utility→minimax→MCTS pipeline, PBT with fast-check. |

Stack notes (all verified): StartLux-0.8B-Q8_0 local (llama-server + gguf_server,
0.1–0.3s/decision warm); CPU backend after Vulkan anon-creep finding
(`~/s1/serve.sh`, 2.5GB cap); RAM discipline between batches.
