"""S1 UNO player: typed choice over readable legal moves. Heuristic fallback."""
import os
import requests

S1_URL = os.environ.get("S1_URL", "")
LAST = {"probs": [], "ms": 0.0}


def color_of(card):
    return card.split("-")[0] if "-" in card else "?"


def describe(raw):
    hand = raw["hand"]
    colors = {}
    for c in hand:
        colors[color_of(c)] = colors.get(color_of(c), 0) + 1
    top = raw["target"]
    foe = raw["num_cards"][1]
    threat = ("UNO! Opponent wins next turn unless disrupted."
              if foe == 1 else
              f"Opponent holds {foe} cards."
              if foe <= 3 else f"Opponent holds {foe} cards (safe).")
    playable = [a for a in raw.get("legal_actions", []) if a != "draw"]
    return (f"Your hand ({len(hand)}): {', '.join(hand)}. "
            f"Colors held: {colors}. Top card: {top}. {threat} "
            f"Playable now ({len(playable)}): {', '.join(playable) or 'none — must draw'}.")


def ground(action, raw=None):
    a = action.lower()
    raw = raw or {}
    hand = raw.get("hand", [])
    if a == "draw":
        return "draw a card (safe, turn passes, hand grows)"
    if "wild" in a:
        colors = {}
        for c in hand:
            colors[color_of(c)] = colors.get(color_of(c), 0) + 1
        best = max(colors, key=colors.get) if colors else "?"
        if "draw_4" in a or "draw4" in a:
            return (f"play {action}: +4 on foe AND set color (your best "
                    f"color is {best}); game-swinging, use when foe is low")
        return (f"play {action}: sets color (your best color is {best}); "
                f"playable anytime, best saved unless it wins or foe has UNO")
    foe = raw.get("num_cards", [0, 0])[1]
    if "skip" in a or "reverse" in a:
        return (f"play {action}: disrupts foe"
                + (" — CRITICAL, foe at UNO" if foe == 1 else "") +
                " (only useful if it matches)")
    if "draw2" in a or "+2" in a:
        return (f"play {action}: foe draws 2 and skips"
                + (" — CRITICAL, foe at UNO" if foe == 1 else ""))
    top = raw.get("target", "?")
    return (f"play {action} on {top}: sheds a card"
            + (" and changes nothing about foe" if foe > 2 else ""))


def heuristic(raw, legal):
    nonwild = [a for a in legal if "wild" not in a.lower() and a != "draw"]
    if nonwild:
        return nonwild[0], 0.6, "shed non-wild match"
    wilds = [a for a in legal if "wild" in a.lower()]
    if wilds and len(raw["hand"]) <= 3:
        return wilds[0], 0.7, "go out with wild"
    if "draw" in legal:
        return "draw", 0.5, "no good play"
    return (wilds + legal)[0], 0.4, "forced wild"


def fresh_target(raw_target, last_wild):
    """RLCard freezes UnoCard.str at init, so a played wild displays its OLD
    color. Override with the declared color tracked per game."""
    if last_wild and "wild" in raw_target:
        return last_wild
    return raw_target


def turn_state(raw):
    base = describe(raw)
    n = len(raw["hand"])
    if n == 1:
        return ("It is your turn with ONE card left. Playing it wins the "
                "game immediately. " + base)
    if n == 2:
        return ("It is your turn with TWO cards left. Prefer plays that leave "
                "a flexible last card (a number, not a wild you might need). "
                + base)
    return "It is your turn. Shed cards; fewest cards usually wins. " + base


def s1_move(raw, legal, log=None, mem=None):
    """mem: per-game dict tracking consecutive draws + last hand (stall guard)."""
    from collections import Counter
    mem = mem if mem is not None else {}
    # multiset diff: duplicates must count (two g-8s hide a drawn third)
    had, has = Counter(mem.get("prev_hand", [])), Counter(raw["hand"])
    just = sorted((has - had).elements())
    mem["prev_hand"] = list(raw["hand"])
    state = ("You are playing UNO, a shedding card game. The player who "
             "empties their hand first wins. On your turn you may play ONE "
             "matching card or draw. " + turn_state(raw))
    if just:
        state += (" You just drew " + ", ".join(just) + ", playable NOW "
                  "for free tempo — drawing again wastes it.")
    crit = {}
    for a in legal:
        g = ground(a, raw)
        if a != "draw" and len(raw["hand"]) == 1:
            g += " — WINS THE GAME NOW"
        if a in just:
            g += " — JUST DRAWN, play it now for free"
        crit[a] = g
    pick, conf, via = None, 0.0, "heuristic"
    live_url = os.environ.get("S1_URL", "")
    if live_url and len(legal) > 1:
        try:
            r = requests.post(live_url, json={
                "state": state,
                "questions": {"move": {
                    "type": "choice",
                    "instructions": "Best UNO play now",
                    "criteria": crit}}}, timeout=8)
            r.raise_for_status()
            probs = r.json()["answers"]["move"]["probabilities"]
            pick = max(probs, key=probs.get)
            conf = round(probs[pick], 3)
            LAST["probs"] = sorted(probs.items(), key=lambda kv: -kv[1])
            via = "s1"
        except Exception:
            pick = None
    if pick not in legal:
        pick, conf, why = heuristic(raw, legal)
        via = f"heuristic:{why}"
    if pick == "draw":
        mem["consec_draws"] = mem.get("consec_draws", 0) + 1
    else:
        mem["consec_draws"] = 0
    if mem["consec_draws"] >= 3:
        plays = [a for a in legal if a != "draw"]
        if plays:
            pick, _, _ = heuristic(raw, plays)
            conf, via = 0.5, "guard:stall-break"
            mem["consec_draws"] = 0
    if log is not None:
        log.append({"hand_n": len(raw["hand"]), "foe_n": raw["num_cards"][1],
                    "target": raw["target"], "move": pick, "conf": conf,
                    "via": via, "options": len(legal)})
    return pick
