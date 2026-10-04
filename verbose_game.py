#!/usr/bin/env python3
"""Verbose UNO game logger - S1 vs Heuristic"""
import os
# MUST precede uno.player import: S1_URL is read at import time.
os.environ.setdefault("S1_URL", "http://127.0.0.1:8090/v1/systemone")
import sys
import time
sys.path.insert(0, '/home/hassenhamdi/projects/uno-s1')

import rlcard
from uno.player import s1_move, heuristic, LAST

print("="*80)
print("UNO VERBOSE GAME LOG: S1 vs HEURISTIC")
print("="*80)
print()

env = rlcard.make("uno")
env.seed(789)  # Different seed for new game
st, player = env.reset()

from rlcard.games.uno.utils import ACTION_SPACE

print(f"GAME START: Player {player} ({['S1', 'HEUR'][player]}) goes first")
print()

for move_num in range(1, 200):
    raw = st["raw_obs"]
    readable = list(raw["legal_actions"])
    
    # Get both hands
    game = env.game
    hands = {pid: [c.get_str() for c in game.players[pid].hand] for pid in [0, 1]}
    
    # Verbose logging
    print(f"{'='*80}")
    print(f"MOVE {move_num}")
    print(f"{'='*80}")
    print(f"Current Player: {player} ({['S1', 'HEUR'][player]})")
    print(f"Top Card: {raw['target']}")
    print(f"S1 Hand ({len(hands[0])}): {hands[0]}")
    print(f"HEUR Hand ({len(hands[1])}): {hands[1]}")
    print(f"Legal Actions: {readable}")
    
    old_hand = list(hands[player])
    old_hand_size = len(old_hand)
    
    # Make move
    if player == 0:  # S1
        print(f"\nS1 deciding...")
        mv = s1_move({**raw, "legal_actions": readable}, readable)
        probs = LAST.get("probs", [])
        if probs:
            print(f"S1 Probabilities:")
            for opt, prob in probs[:5]:
                print(f"  {opt}: {prob:.3f}")
    else:  # Heuristic
        print(f"\nHEURISTIC deciding...")
        mv, conf, reason = heuristic({**raw, "legal_actions": readable}, readable)
        print(f"Heuristic logic: {reason} (confidence: {conf})")
    
    # Validate
    if mv not in readable:
        print(f"\n⚠️  ERROR: ILLEGAL MOVE!")
        print(f"  Attempted: {mv}")
        print(f"  Legal options: {readable}")
        break
    
    print(f"\n→ PLAYS: {mv}")
    
    # Execute
    action_id = ACTION_SPACE[mv]
    st, player = env.step(action_id)
    
    # Check result
    new_hands = {pid: [c.get_str() for c in game.players[pid].hand] for pid in [0, 1]}
    prev_player = 1 - player
    new_hand = new_hands[prev_player]
    new_hand_size = len(new_hand)
    
    print(f"\nAfter move:")
    print(f"  Player who moved hand: {old_hand_size} → {new_hand_size} cards")
    
    if mv == "draw":
        expected = old_hand_size + 1
        if new_hand_size == expected:
            print(f"  ✓ Draw validated: added 1 card")
        else:
            print(f"  ⚠️  DRAW BUG: Expected {expected}, got {new_hand_size}")
            print(f"    Old: {old_hand}")
            print(f"    New: {new_hand}")
    else:
        expected = old_hand_size - 1
        if new_hand_size == expected:
            print(f"  ✓ Play validated: removed 1 card")
            removed = set(old_hand) - set(new_hand)
            if removed:
                print(f"    Removed: {list(removed)}")
        else:
            print(f"  ⚠️  PLAY BUG: Expected {expected}, got {new_hand_size}")
            print(f"    Old: {old_hand}")
            print(f"    New: {new_hand}")
    
    print(f"\nNext player: {player} ({['S1', 'HEUR'][player]})")
    print()
    
    if env.is_over():
        import numpy as np
        payoffs = env.get_payoffs()
        winner_idx = int(np.argmax(payoffs))
        print(f"{'='*80}")
        print(f"GAME OVER!")
        print(f"{'='*80}")
        print(f"Winner: {['S1', 'HEURISTIC'][winner_idx]}")
        print(f"Total moves: {move_num}")
        print(f"Final hands:")
        print(f"  S1: {len(new_hands[0])} cards - {new_hands[0]}")
        print(f"  HEUR: {len(new_hands[1])} cards - {new_hands[1]}")
        print(f"Payoffs: S1={payoffs[0]}, HEUR={payoffs[1]}")
        print(f"{'='*80}")
        break

print("\nGame log complete")
