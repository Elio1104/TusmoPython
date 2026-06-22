import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import uvicorn
import socketio
import uuid

from core import conf

@dataclass
class GameState:
    word: str

class ColorEnum(Enum):
    GRAY = "\033[0m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"

def read_tusmo_dict(filename: str = "../core/anime_dict.txt", encoding: str = "utf-8"):
    """Read `tusmo_dict.txt` (in the same folder) and return non-empty stripped lines."""
    p = Path(__file__).parent / filename
    if not p.exists():
        raise FileNotFoundError(f"{p} not found")
    with p.open("r", encoding=encoding, errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)
valid_words = read_tusmo_dict()

lobbies = {}

def serialize_lobbies():
    return [
        {
            "id": lobby_id,
            "owner": data["owner"],
            "players": len(data["players"]),
        }
        for lobby_id, data in lobbies.items()
    ]

async def broadcast_lobbies():
    print("\nLobby update:")
    for lobby_id, data in lobbies.items():
        print(f" - {lobby_id} | owner={data['owner']} | players={len(data['players'])}")

    await sio.emit("lobby_list", serialize_lobbies())

### Game logic ###
def get_random_word() -> str:
    """Return a random word from the valid words list."""
    return random.choice(valid_words)

gamestate = GameState(word=get_random_word())

def is_valid_guess(word: str, chosen_word: str) -> bool:
    """Check if the guessed word is in the valid words list."""
    return word in valid_words and len(word) == len(chosen_word)

def compare_guess(guess: str, chosen_word: str) -> str:
    """Compare the guessed word with the chosen word and return colored word."""
    feedback = ["GRAY"] * len(guess)
    chosen_chars = list(chosen_word)

    for i, (g_char, c_char) in enumerate(zip(guess, chosen_word)):
        if g_char == c_char:
            feedback[i] = "GREEN"
            chosen_chars[i] = None

    for i, g_char in enumerate(guess):
        if feedback[i] != "GREEN" and g_char in chosen_chars:
            feedback[i] = "YELLOW"
            chosen_chars[chosen_chars.index(g_char)] = None

    color_map = {
        "GREEN": ColorEnum.GREEN.value,
        "YELLOW": ColorEnum.YELLOW.value,
        "GRAY": ColorEnum.GRAY.value
    }

    result = ""
    for char, color in zip(guess, feedback):
        result += f"{color_map[color]}{char}"
    result += ColorEnum.GRAY.value  # Reset à la fin

    return result

### Socket.IO Events ###
@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid}") #TODO: add some logic

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}") #TODO: add some logic

@sio.event
async def create_lobby(sid, data):

    for lobby in lobbies.values():
        if sid in lobby["players"]:
            return {"error": "Already in a lobby"}

    lobby_id = str(uuid.uuid4())[:5]

    lobbies[lobby_id] = {
        "owner": sid,
        "gamestate": None,
        "players":{
            sid:{
                "is_ready": False,
                "guesses": 0
            }
        }
    }

    print(f"Lobby created: {lobby_id} by {sid}")

    await broadcast_lobbies()
    return {"lobby_id": lobby_id}

@sio.event
async def join_lobby(sid, data):

    for lobby in lobbies.values():
        if sid in lobby["players"]:
            return {"error": "Already in a lobby"}

    lobby_id = data.get("lobby_id")

    if lobby_id not in lobbies:
        return {"error": "Lobby not found"}

    lobbies[lobby_id]["players"].add(sid)

    print(f"{sid} joined lobby {lobby_id}")

    await broadcast_lobbies()
    return {"lobby_id": lobby_id}

@sio.event
async def leave_lobby(sid, data):
    lobby_id = data.get("lobby_id")

    if lobby_id not in lobbies:
        return {"error": "Lobby not found"}

    lobbies[lobby_id]["players"].remove(sid)

    if len(lobbies[lobby_id]["players"]) == 0:
        del lobbies[lobby_id]

    print(f"{sid} left lobby {lobby_id}")

    await broadcast_lobbies()
    return {"lobby_id": lobby_id}

@sio.event
async def ready_lobby(sid, data):
    for lobby in lobbies.values():
        if sid in lobby["players"]:
            lobby["players"][sid]["is_ready"] = True
            break

@sio.event
async def start_lobby(sid, data):
    async def start_game(lobby_id):
        gamestate = GameState(word=get_random_word())

        lobbies[lobby_id]["gamestate"] = gamestate

        print(lobbies[lobby_id]["gamestate"].word)

    for lobby_id, lobby in lobbies.items():
        if sid == lobby["owner"]:
            await start_game(lobby_id)
            break

### Custom events ###
@sio.on('send_guess')
async def send_guess(sid, data):
    """Receives a guess from the client and processes it"""

    guess = data.get('guess', None)
    print('Received guess from client:', sid, 'Guess:', guess)
    print('Chosen word:', gamestate.word)

    is_valid = is_valid_guess(guess, gamestate.word)
    print(f"Is the guess valid? {is_valid}")

    if is_valid:
        print(compare_guess(guess, gamestate.word)) ##changeme

        return {
            'result': 'correct',
            'message': f'You guessed correctly: {guess}'
        }
    else :
        return {
            'result': 'incorrect',
            'message': f'Incorrect guess: {guess}'
        }


if __name__ == "__main__":
    uvicorn.run('server:app', host=conf.SERV_IP, port=conf.SERV_PORT)
