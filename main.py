# === BATTLE-SNAKE ADVANCED VERSION ===
# Deploy this to your Dev URL (e.g. Replit, Render, or local tunnel)
# Docs: https://docs.battlesnake.com/quickstart

from flask import Flask, request, jsonify
import math

app = Flask(__name__)

@app.get("/")
def index():
    return "Your advanced Battlesnake is running!", 200

@app.post("/start")
def start():
    data = request.get_json()
    print("GAME START:", data["game"]["id"])
    color = "#00CED1"  # Teal
    return jsonify({
        "color": color,
        "headType": "beluga",
        "tailType": "round-bum"
    })

@app.post("/move")
def move():
    data = request.get_json()
    move = choose_best_move(data)
    print(f"Move chosen: {move}")
    return jsonify({"move": move})


@app.post("/end")
def end():
    data = request.get_json()
    print("GAME OVER:", data["game"]["id"])
    return "ok", 200


# === STRATEGY FUNCTIONS ===

def choose_best_move(data):
    board = data["board"]
    me = data["you"]

    head = me["head"]
    body = me["body"]
    height = board["height"]
    width = board["width"]
    food = board["food"]
    snakes = board["snakes"]

    # Directions
    moves = {
        "up": {"x": head["x"], "y": head["y"] + 1},
        "down": {"x": head["x"], "y": head["y"] - 1},
        "left": {"x": head["x"] - 1, "y": head["y"]},
        "right": {"x": head["x"] + 1, "y": head["y"]}
    }

    safe_moves = []
    for move, coord in moves.items():
        if is_safe(coord, body, snakes, width, height, me):
            safe_moves.append(move)

    # If no safe moves, choose randomly
    if not safe_moves:
        return "up"

    # Food logic: choose nearest safe food if any
    if food:
        target = nearest_food(head, food)
        best_move = move_toward(head, target, safe_moves)
        if best_move:
            return best_move

    # Otherwise choose the safest (most open) move
    best_move = max(safe_moves, key=lambda m: open_space_score(moves[m], snakes, width, height))
    return best_move


def is_safe(coord, body, snakes, width, height, me):
    # Stay in bounds
    if coord["x"] < 0 or coord["x"] >= width or coord["y"] < 0 or coord["y"] >= height:
        return False

    # Avoid own body (excluding tail end if it moves)
    if coord in body[:-1]:
        return False

    # Avoid other snakes’ bodies
    for s in snakes:
        if coord in s["body"][:-1]:
            return False

    # Avoid heads of larger or equal snakes nearby (prevent head-on collisions)
    for s in snakes:
        if s["id"] == me["id"]:
            continue
        if len(s["body"]) >= len(me["body"]):
            head = s["head"]
            if abs(coord["x"] - head["x"]) + abs(coord["y"] - head["y"]) == 1:
                return False
    return True


def nearest_food(head, food_list):
    return min(food_list, key=lambda f: manhattan(head, f))


def move_toward(head, target, safe_moves):
    dx = target["x"] - head["x"]
    dy = target["y"] - head["y"]

    preferred = []
    if abs(dx) > abs(dy):
        if dx > 0:
            preferred = ["right", "up", "down", "left"]
        else:
            preferred = ["left", "up", "down", "right"]
    else:
        if dy > 0:
            preferred = ["up", "left", "right", "down"]
        else:
            preferred = ["down", "left", "right", "up"]

    for p in preferred:
        if p in safe_moves:
            return p
    return None


def open_space_score(coord, snakes, width, height):
    # Simple open-space heuristic: count available cells within Manhattan radius 2
    score = 0
    for x in range(coord["x"] - 2, coord["x"] + 3):
        for y in range(coord["y"] - 2, coord["y"] + 3):
            if 0 <= x < width and 0 <= y < height:
                if not any({"x": x, "y": y} in s["body"] for s in snakes):
                    score += 1
    return score


def manhattan(a, b):
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


# === Run on Render or locally ===
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
