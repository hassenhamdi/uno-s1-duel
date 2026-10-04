#!/usr/bin/env python3
"""UNO Spectator: S1 vs Heuristic with both hands visible for OBS recording."""
import os
# MUST precede uno.player import: S1_URL is read at import time.
os.environ.setdefault("S1_URL", "http://127.0.0.1:8090/v1/systemone")
import sys
import time
sys.path.insert(0, '/home/hassenhamdi/projects/uno-s1')

import rlcard
from uno.player import s1_move, heuristic, LAST
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

# Game state
game_state = {
    "top": "r-5",
    "s1_hand": [],
    "heur_hand": [],
    "current": "S1",
    "last_move": None,
    "s1_probs": [],
    "winner": None,
    "move_num": 0
}

class SpectatorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logs
    
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        if length:
            self.rfile.read(length)
        if self.path == '/new':
            res = start_new_game()
            data = json.dumps(res).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """<!doctype html>
<html><head><meta charset="utf-8"><title>UNO: S1 vs Heuristic</title>
<style>
body{font-family:monospace;background:#0b3d2e;color:#fff;padding:20px;font-size:16px}
h1{text-align:center;color:#f2b705}
.board{max-width:1200px;margin:20px auto;border:3px solid #fff;border-radius:10px;padding:20px;background:#094d35}
.player{margin:20px 0;padding:15px;border:2px solid #aaa;border-radius:8px;background:#0a3d2e}
.player.active{border-color:#f2b705;box-shadow:0 0 10px #f2b705}
.player h2{margin:0 0 10px 0;color:#f2b705}
.hand{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.card{display:inline-block;padding:8px 12px;border-radius:6px;font-weight:bold;min-width:60px;text-align:center;border:2px solid #000}
.card.r{background:#e0261c;color:#fff}
.card.g{background:#2e9e44;color:#fff}
.card.b{background:#1c6fe0;color:#fff}
.card.y{background:#f2b705;color:#000}
.card.wild{background:linear-gradient(45deg,#e0261c 25%,#2e9e44 25%,#2e9e44 50%,#1c6fe0 50%,#1c6fe0 75%,#f2b705 75%);color:#fff;text-shadow:1px 1px 2px #000}
.top-card{font-size:24px;text-align:center;margin:20px;padding:20px;border-radius:10px}
.move-info{margin:10px 0;padding:10px;background:#0a2d1e;border-radius:5px}
.probs{margin:10px 0}
.prob-bar{background:#333;margin:5px 0;padding:5px;border-radius:3px}
.prob-fill{background:#2e9e44;height:20px;border-radius:3px;transition:width 0.3s}
</style>
</head>
<body>
<h1>🎮 UNO: S1 vs HEURISTIC 🎮</h1>
<div style="text-align:center;margin:6px">
<button id="start-btn" onclick="startGame()" style="font-size:18px;padding:10px 28px;cursor:pointer">▶ Start game</button>
</div>
<div class="board">
<div class="player" id="s1-player">
<h2>🤖 S1 (AI Decision Model)</h2>
<div class="hand" id="s1-hand"></div>
<div class="probs" id="s1-probs"></div>
</div>

<div class="top-card" id="top-card">Top: ?</div>
<div class="move-info" id="move-info">Waiting for game...</div>

<div class="player" id="heur-player">
<h2>🎯 Heuristic (Rule-Based)</h2>
<div class="hand" id="heur-hand"></div>
</div>
</div>

<script>
function cardColor(card){
  if(card.includes('wild'))return 'wild';
  return card.split('-')[0];
}
function renderCard(card){
  const c = cardColor(card);
  const face = card.split('-').slice(1).join('-').toUpperCase();
  return `<div class="card ${c}">${face}</div>`;
}
async function startGame(){
  const btn=document.getElementById('start-btn');
  btn.textContent='↻ New game';
  await fetch('/new',{method:'POST'});
}
setInterval(async ()=>{
  const r = await fetch('/state');
  const s = await r.json();
  
  document.getElementById('s1-hand').innerHTML = s.s1_hand.map(renderCard).join('');
  document.getElementById('heur-hand').innerHTML = s.heur_hand.map(renderCard).join('');
  
  const topColor = cardColor(s.top);
  document.getElementById('top-card').innerHTML = `<div class="card ${topColor}">${s.top.split('-').slice(1).join('-').toUpperCase()}</div>`;
  document.getElementById('top-card').className = 'top-card';
  
  document.getElementById('s1-player').className = s.current==='S1'?'player active':'player';
  document.getElementById('heur-player').className = s.current==='HEUR'?'player active':'player';
  
  let info = `Move ${s.move_num}`;
  if(s.last_move) info += ` | Last: ${s.last_move}`;
  if(s.winner){ info = `🏆 ${s.winner} WINS! 🏆`;
    document.getElementById('start-btn').textContent='↻ New game'; }
  document.getElementById('move-info').innerText = info;
  
  let probHtml = '';
  if(s.s1_probs.length > 0 && s.current === 'S1'){
    probHtml = '<strong>S1 Probabilities:</strong><br>';
    s.s1_probs.forEach(p=>{
      probHtml += `<div class="prob-bar">${p[0]}: <div class="prob-fill" style="width:${p[1]*100}%">${(p[1]*100).toFixed(1)}%</div></div>`;
    });
  }
  document.getElementById('s1-probs').innerHTML = probHtml;
},500);
</script>
</body></html>"""
            self.wfile.write(html.encode())
        
        elif self.path == '/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(game_state).encode())
        else:
            self.send_response(404)
            self.end_headers()

game_lock = threading.Lock()
game_thread = None
stop_event = threading.Event()


def start_new_game():
    """Stop previous game, reset env, start a fresh demo game."""
    global game_thread
    with game_lock:
        stop_event.set()  # halt running loop (wait(2) wakes instantly)
        if game_thread is not None and game_thread.is_alive():
            game_thread.join(timeout=10)
        stop_event.clear()
        game_state.update({"top": "?", "s1_hand": [], "heur_hand": [],
                           "current": "S1", "last_move": None, "s1_probs": [],
                           "winner": None, "move_num": 0})
        import random
        seed = random.randint(1, 99999)
        game_thread = threading.Thread(target=run_game, args=(seed,),
                                       daemon=True)
        game_thread.start()
        return {"ok": True, "seed": seed}

def run_game(seed=456):
    """Run S1 vs Heuristic game in background, updating state."""
    env = rlcard.make("uno")
    env.seed(seed)
    st, player = env.reset()

    from rlcard.games.uno.utils import ACTION_SPACE
    s1_mem = {}  # persistent: stall guard + just-drawn tracking need history

    for move_num in range(1, 1001):
        if stop_event.is_set():
            print("game stopped by new-game button")
            return
        raw = st["raw_obs"]
        readable = list(raw["legal_actions"])

        # Log current turn
        current_player_name = ['S1', 'HEUR'][player]
        print(f"Move {move_num}: Player {player} ({current_player_name}) | Legal: {readable}")

        if stop_event.wait(2):  # Slow down for visibility; wakes on stop
            print("game stopped by new-game button")
            return
        
        # Make move
        if player == 0:  # S1
            mv = s1_move({**raw, "legal_actions": readable}, readable,
                         None, s1_mem)
            game_state["s1_probs"] = LAST.get("probs", [])
        else:  # Heuristic
            mv, _, _ = heuristic({**raw, "legal_actions": readable}, readable)
            game_state["s1_probs"] = []
        
        # Validate move is legal
        if mv not in readable:
            print(f"⚠️  ERROR: Illegal move! {mv} not in {readable}")
            game_state["last_move"] = f"ERROR: {current_player_name} tried illegal {mv}"
            break
        
        game_state["last_move"] = f"{current_player_name} plays {mv}"
        print(f"  → Plays: {mv}")
        
        # Convert action name to ID and execute
        action_id = ACTION_SPACE[mv]
        st, player = env.step(action_id)
        
        # NOW update hands AFTER the move completes
        game = env.game
        hands = {}
        for pid in [0, 1]:
            hands[pid] = [c.get_str() for c in game.players[pid].hand]
        
        # Update display state with current game state
        game_state["move_num"] = move_num
        game_state["top"] = st["raw_obs"]["target"]
        game_state["s1_hand"] = list(hands[0])
        game_state["heur_hand"] = list(hands[1])
        game_state["current"] = "S1" if player == 0 else "HEUR"
        
        if env.is_over():
            import numpy as np
            payoffs = env.get_payoffs()
            winner_idx = int(np.argmax(payoffs))
            game_state["winner"] = ["S1", "HEURISTIC"][winner_idx]
            game_state["current"] = None
            break
    else:
        game_state["winner"] = "DRAW (move cap)"
        game_state["current"] = None

    print(f"\nGame over: {game_state['winner']} wins in {move_num} moves")

if __name__ == "__main__":
    print("="*60)
    print("UNO SPECTATOR MODE: S1 vs HEURISTIC")
    print("="*60)
    print("\nOpen in browser: http://127.0.0.1:5001")
    print("Recording with OBS: Capture this browser window")
    print("\nBoth players' hands are visible")
    print("S1 probabilities shown in real-time")
    print("Press Start game in the browser to begin.")
    print("="*60)

    # Web server only; games start on button click
    server = HTTPServer(('127.0.0.1', 5001), SpectatorHandler)
    print("\nServer running... Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
