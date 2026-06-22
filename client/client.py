import asyncio
import socketio
from core import conf

sio = socketio.AsyncClient()

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
    await sio.connect(f'http://{conf.SERV_IP}:{conf.SERV_PORT}', auth={
        'username': 'test1234' #TODO: get username from user input
    })

    await game_logic()

    await sio.wait()

if __name__ == "__main__":
    asyncio.run(client())