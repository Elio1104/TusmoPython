import asyncio
import socketio
from core import conf

sio = socketio.AsyncClient()
game_started = asyncio.Event()

@sio.event
async def lobby_list(data):
    print("\nLobbies:")
    for lobby in data:
        print(f"- {lobby['id']} | players={lobby['players']}")

async def input_loop():
    while True:
        cmd = await asyncio.to_thread(input, "\n> ")

        if cmd == "create":
            res = await sio.call("create_lobby", {})
            print("Lobby created:", res)

        elif cmd.startswith("join"):
            _, lobby_id = cmd.split()
            res = await sio.call("join_lobby", {"lobby_id": lobby_id})
            print("Joined:", res)

        elif cmd.startswith("leave"):
            _, lobby_id = cmd.split()
            res = await sio.call("leave_lobby", {"lobby_id": lobby_id})
            print("Left")

        elif cmd == "ready":
            res = await sio.call("ready_lobby", {})
            print("Ready:", res)

        elif cmd == "start":
            res = await sio.call("start_lobby", {})
            print("Start:", res)
            game_started.set()

        elif cmd == "quit":
            await sio.disconnect()
            break


async def game_logic():
    """Main game loop that handles game logic and communication with the server"""

    is_won = False
    nbr_try = 0

    while not is_won and nbr_try < 6:

        ## User Input
        guess = await asyncio.to_thread(input, "Enter your guess: ")

        response = await sio.call('send_guess', {
            'guess': guess
        })

        if response["result"] == "correct":
            is_won = True
            nbr_try += 1
            print(response["message"])
        else:
            print(response["message"])
            nbr_try += 1

    print("Game Over! You won!" if is_won else "Game Over! You lost!")


async def client():
    await sio.connect(f'http://10.10.8.121:{conf.SERV_PORT}', auth={
        'username': 'test12345' #TODO: get username from user input
    })

    input_task = asyncio.create_task(input_loop())

    await game_started.wait()  # wait until server starts game

    input_task.cancel()  # stop lobby commands

    try:
        await input_task
    except asyncio.CancelledError:
        pass

    await game_logic()

    await sio.wait()

if __name__ == "__main__":
    asyncio.run(client())