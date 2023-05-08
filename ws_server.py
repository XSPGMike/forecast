import asyncio
import django
import websockets
import json
django.setup()
from sesame.utils import get_user
from flash.models import Flash

connected_clients = []
game_state = {}

def other_clients(websocket):
    return [client for client in connected_clients if not client["ws"].closed and client["ws"] is not websocket]

async def handler(websocket):
    global game_state
    sesame = await websocket.recv()
    user = await asyncio.to_thread(get_user, sesame)


    if user is None:
        await websocket.close(1011, "authentication failed")
        return

    if user in [client["user"] for client in connected_clients]:
        await websocket.close(1000, "duplicate connection")
        return

    if len(connected_clients) == 0:
        game_state = {user.username: 5}
    else:
        game_state[user.username] = 5

    connected_clients.append({"ws": websocket, "user": user})

    for client in other_clients(websocket):
        await client["ws"].send(json.dumps({"event": "user_connected", "user": user.username }))
        await websocket.send(json.dumps({"event": "user_connected", "user": client["user"].username }))

    try:
        async for message in websocket:
            data = json.loads(message)
            for client in other_clients(websocket):
                if data["event"] == "range":
                    game_state[user.username] = data["value"]
                    await client["ws"].send(json.dumps({
                        "event": "range",
                        "user": user.username,
                        "value": data["value"]
                    }))
                elif data["event"] == "end":
                    await client["ws"].send(json.dumps({
                        "event": "end"
                    }))
            if data["event"] == "end":
                loop = asyncio.get_event_loop()
                Flash.objects.filter(active=True).update(active=False, votes=json.dumps(game_state))
    finally:
        if websocket in [client["ws"] for client in connected_clients]:
            connected_clients.remove({"ws": websocket, "user": user})
        for client in other_clients(websocket):
            await client["ws"].send(json.dumps({"event": "user_disconnected", "user": user.username }))

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
