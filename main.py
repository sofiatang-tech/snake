# === LAVENDER BATTLESNAKE: Sssugarplum Edition ===
# Author: Sofia Tang
# Battlesnake Profile: https://play.battlesnake.com
# Docs: https://docs.battlesnake.com/quickstart

from flask import Flask, request, jsonify
import os
import math

app = Flask(__name__)

# -----------------------------------------------
# Root endpoint — tells Battlesnake your style
# -----------------------------------------------
@app.get("/")
def index():
    return jsonify({
        "apiversion": "1",
        "author": "sofiatang1",
        "color": "#C8A2C8",        # Lavender theme 💜
        "head": "fang",            # Elegant fang head
        "tail": "round-bum"        # Rounded tail for charm
    })


# -----------------------------------------------
# Start endpoint — called when a game begins
# -----------------------------------------------
@app.post("/start")
def start():
    data = request.get_json()
    print("GAME START:", data["game"]["id"])
    return jsonify({
        "color": "#C8A2C8",
        "headType": "fang",
        "tailType": "round-bum"
    })


# -----------------------------------------------
# Move endpoint — core logic of your snake
# -----------------------------------------------
@app.post("/move")
def move():
    data = request.get_json()
    move = choose_best_move(data)
    print(f"Move chosen: {move}")
    return jsonify({"move": move})


# -----------------------------------------------
# End endpoint — called when game ends
# -----------------------------------------------
@app.post("/end")
def end():
    data = request.get_json()
    print("GAME OVER:", data["game"]["id"])
    return "ok", 200


# -----------------------------------------------
# STRATEGY FUNCTIONS
# -----------------------------------------------
def choose_best_move(data):
    board = data["board"]
    me = data["you"]

    head = me["head"]
    body = me["body"]
    height = board["height"]
    width = board["width"]
    food = board["food"]
    snakes = board["snakes"]

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

    if not safe_moves:
        return "up"

    if food:
        target = nearest_food(head, food)
        best_move = move_toward(head, target, safe_moves)
        if best_move:
            return best_move

    best_move = max(safe_moves, key=lambda m: open_space_score(moves[m], snakes, width, height))
    return best_move


def is_safe(coord, body, snakes, width, height, me):
    if coord["x"] < 0 or coord["x"] >= width or coord["y"] < 0 or coord["y"] >= height:
        return False
    if coord in body[:-1]:
        return False
    for s in snakes:
        if coord in s["body"][:-1]:
            return False
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
    score = 0
    for x in range(coord["x"] - 2, coord["x"] + 3):
        for y in range(coord["y"] - 2, coord["y"] + 3):
            if 0 <= x < width and 0 <= y < height:
                if not any({"x": x, "y": y} in s["body"] for s in snakes):
                    score += 1
    return score


def manhattan(a, b):
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


# -----------------------------------------------
# Run on Render or locally
# -----------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
