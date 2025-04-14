import Play_Scoundrel
import Scoundrel_Deck
import Scoundrel_Exceptions

import random as rand
import time
from fastapi import FastAPI, Query, Response
from fastapi.responses import HTMLResponse
from typing import Annotated
import pickle as pic
import json

app = FastAPI()

def generate_game_id():
    rand.seed(time.time())
    id_as_float = rand.random()
    id_as_string = str(id_as_float)
    return id_as_string[2:]

def card_is_monster(card:Scoundrel_Deck.Card):
    if card.suit is Scoundrel_Deck.Suit.Club:
        return True
    if card.suit is Scoundrel_Deck.Suit.Spade:
        return True
    return False

def summarize_game_state(game:Play_Scoundrel.Scoundrel) -> dict:
    state = dict()

    state["game_over"] = game.game_over
    if game.game_over:
        state["score"] = game.score

    state["life"] = game.life
    state["room"] = game.room
    state["weapon"] = 0 if not game.weapon else game.weapon.value
    state["weapon_durability"] = game.weapon_durability
    state["can_skip"] = game.can_skip

    return state

@app.get("/scoundrel/new-game")
def new_game(response:Response):
    game_id = generate_game_id()

    game = Play_Scoundrel.Scoundrel()
    game.enter_room()
    
    state = summarize_game_state(game)

    with open(f"./saved_runs/{game_id}", "wb") as file:
        pic.dump(game, file)

    response.headers["Access-Control-Allow-Origin"] = "*"
    return {"game_id": game_id, "state": state}


@app.get("/scoundrel/take-turn/")
def take_turn(response:Response,
              game_id: str,
              turn_type:str,
              card_resolve_order:Annotated[list[int],Query()]=[],
              by_hand:Annotated[list[bool],Query()]=[]):
    
    with open(f"./saved_runs/{game_id}", "rb") as file:
        game = pic.load(file)

    if turn_type == "skip":
        game.skip_room()
        game.enter_room()
    elif turn_type == "resolve":
        try:
            game.resolve_room(card_resolve_order, by_hand)
            try:
                game.enter_room()
            except Scoundrel_Exceptions.GameOverError:
                pass
            except Exception as e:
                raise e
        except:
            return {406: "bad values for resolve room"}
    else:
        return {400: "turn type not recognized"}
    
    state = summarize_game_state(game)

    with open(f"./saved_runs/{game_id}", "wb") as file:
        pic.dump(game, file)

    response.headers["Access-Control-Allow-Origin"] = "*"
    return state

@app.get("/scoundrel/", response_class=HTMLResponse)
def index():
    with open("index.html", "r") as file:
        return file.read()

