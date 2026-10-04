# Requirements — uno-s1-duel (Lesson 1, EARS)

## 1. Typed decisions
- WHEN it is S1's turn with >1 legal move THEN THE SYSTEM SHALL choose via one
  S1 `choice` request with grounded per-option consequences.
- WHEN the S1 server is unreachable or 1 move is legal THEN THE SYSTEM SHALL
  use the heuristic fallback with identical return shape (never throw).

## 2. Prompt-input knowledge
- WHEN building state THEN THE SYSTEM SHALL narrate hand, colors held,
  top card, foe threat tier, playable list (no raw tensor input).
- WHEN listing options THEN EACH SHALL state its consequence (wild-color
  advice, UNO disruption alert, WINS-NOW when it empties the hand).

## 3. Playability + evidence
- WHEN a game ends THEN payoffs SHALL decide the winner; W/L SHALL be logged.
- WHEN a human sits down (terminal or browser) THEN THEY SHALL get a timed
  seat with S1 confidence + ms shown per move.
- WHEN `pytest` runs THEN unit + property tests SHALL pass (hypothesis ≥100).

Out of scope: multiplayer beyond 2 seats, wild-bluff modeling, training.
