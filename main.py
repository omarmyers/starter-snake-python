# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import typing
import math
import copy

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data

# Constants for move directions
MOVES = ["up", "down", "left", "right"]


def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#f7810a",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# Helper function to evaluate the game state
# Considers factors such as distance to food, distance to snakes, health, length of snake, distance etc.
def evaluate(game_state: typing.Dict) -> int:
    score = 0
    my_head = game_state["you"]["body"][0]
    food = game_state["board"]["food"]
    health = game_state["you"]["health"]
    board_height = game_state["board"]["height"]
    board_width = game_state["board"]["width"]

    # Distance to the closest food
    if food:
        food_distance = min(math.sqrt(
            (my_head["x"] - food_item["x"]) ** 2 + (my_head["y"] - food_item["y"]) ** 2) for food_item in food)
        # Adjusted weight based on distance to food
        score += (1 / (food_distance + 1)) * 10

    # Distance to the closest snake excluding myself
    min_distance = float("inf")
    for snake in game_state["board"]["snakes"]:
        if snake["id"] != game_state["you"]["id"]:
            distance = math.sqrt(
                (my_head["x"] - snake["body"][0]["x"]) ** 2 + (my_head["y"] - snake["body"][0]["y"]) ** 2)
            if distance < min_distance:
                min_distance = distance
    # Increase score for maintaining distance with the closest snake with adjusted weight
    if min_distance != float("inf"):
        score += max(0, 10 - min_distance) * 0.1

    # Dynamic score adjustment based on health
    if health < 50:
        score -= (50 - health) * 2

    # Score adjustment based on the length of the snake
    score += len(game_state["you"]["body"]) * 4

    # Score penalty for proximity to the edge of the board
    if my_head["x"] == 0:
        score -= 20
    if my_head["x"] == board_width - 1:
        score -= 20
    if my_head["y"] == 0:
        score -= 20
    if my_head["y"] == board_height - 1:
        score -= 20

    # Penalize moves that reduce the snake's freedom of movement
    for direction in MOVES:
        future_position = simulate_move_for_position(my_head, direction)
        if future_position in game_state["board"]["food"]:
            score -= 10
        if future_position in game_state["board"]["snakes"]:
            score -= 10

    # Add bonus score for moves that lead to available space around head
    if my_head["x"] > 0:
        score += 30
    if my_head["x"] < board_width - 1:
        score += 30
    if my_head["y"] > 0:
        score += 30
    if my_head["y"] < board_height - 1:
        score += 30

    return score


# Simulates move for positional evaluation
def simulate_move_for_position(position: str, direction: str) -> str:
    if direction == "up":
        return {"x": position["x"], "y": position["y"] + 1}
    if direction == "down":
        return {"x": position["x"], "y": position["y"] - 1}
    if direction == "left":
        return {"x": position["x"] - 1, "y": position["y"]}
    if direction == "right":
        return {"x": position["x"] + 1, "y": position["y"]}
    return position


# minimax function
def minimax(game_state: typing.Dict, depth: int, max_player: bool) -> int:
    if depth == 0 or game_over(game_state):
        return evaluate(game_state), ""
    if max_player:
        max_eval = float("-inf")
        best_move = ""
        for move in MOVES:
            if is_move_safe(game_state, move):
                new_game_state = simulate_move(game_state, move)
                eval, _ = minimax(new_game_state, depth - 1, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
        return max_eval, best_move
    else:
        min_eval = float("inf")
        best_move = ""
        for move in MOVES:
            if is_move_safe(game_state, move):
                new_game_state = simulate_move(game_state, move)
                eval, _ = minimax(new_game_state, depth - 1, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
        return min_eval, best_move


# Checks if the game over conditions have been met
def game_over(game_state: typing.Dict) -> bool:
    my_head = game_state["you"]["body"][0]
    my_body = game_state["you"]["body"]

    # Checks for heallth
    if game_state["you"]["health"] <= 0:
        return True

    # Checks for self collision
    if my_head in my_body[1:]:
        return True

    # Checks for wall collision
    if my_head["x"] < 0 or my_head["x"] >= game_state["board"]["width"] or my_head["y"] < 0 or my_head["y"] >= game_state["board"]["height"]:
        return True

    # Checks for collision with other snakes
    for snake in game_state["board"]["snakes"]:
        if snake["id"] != game_state["you"]["id"] and my_head in snake["body"]:
            return True

    # All other cases
    return False


# Simulates a move
def simulate_move(game_state: typing.Dict, move: str) -> typing.Dict:
    game_state_copy = copy.deepcopy(game_state)
    new_body = game_state_copy["you"]["body"][:]
    new_head = new_body[0].copy()

    if move == "up":
        new_head["y"] += 1
    elif move == "down":
        new_head["y"] -= 1
    elif move == "left":
        new_head["x"] -= 1
    elif move == "right":
        new_head["x"] += 1

    new_body.insert(0, new_head)

    # Checks to see if food was eaten
    if new_head in game_state["board"]["food"]:
        game_state_copy["board"]["food"].remove(new_head)
    else:
        new_body.pop()

    game_state_copy["you"]["body"] = new_body

    return game_state_copy


# Checks if a move is safe
def is_move_safe(game_state: typing.Dict, move: str) -> bool:
    my_head = game_state["you"]["body"][0]
    my_neck = game_state["you"]["body"][1]
    new_game_state = simulate_move(game_state, move)
    if game_over(new_game_state):
        return False
    if move == "left" and my_neck["x"] < my_head["x"]:
        return False
    if move == "right" and my_neck["x"] > my_head["x"]:
        return False
    if move == "up" and my_neck["y"] < my_head["y"]:
        return False
    if move == "down" and my_neck["y"] > my_head["y"]:
        return False
    return True


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    _, next_move = minimax(game_state, 3, True)

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
