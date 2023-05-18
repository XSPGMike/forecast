import asyncio
import django
import websockets
import os
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from sesame.utils import get_user
from flash.models import Flash

connected_clients = []
game_state = {}

def other_clients(websocket):
    return [client for client in connected_clients if not client["ws"].closed and client["ws"] is not websocket]


async def handler(websocket):
    global game_state
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
                outcome = data["outcome"] == "y"
                Flash.objects.filter(active=True).update(active=False, votes=json.dumps(game_state), outcome=outcome)
    finally:
        if websocket in [client["ws"] for client in connected_clients]:
            connected_clients.remove({"ws": websocket, "user": user})
        for client in other_clients(websocket):
            await client["ws"].send(json.dumps({"event": "user_disconnected", "user": user.username }))

async def close_ws(send, code):
    await send({
        'type': 'websocket.close',
        'code': code if code else 1000
    })

async def new_handler(event, send):
    global connected_clients
    global game_state
    data = None

    if event['type'] == 'websocket.connect':
        await send({
            'type': 'websocket.accept'
        })

    if event['type'] == 'websocket.disconnect':
        return True

    if event['type'] == 'websocket.receive':
        try:
            data = json.loads(event['text'])
            if 'token' not in data:
                raise Exception('no token')
        except:
            await close_ws(send, 1003)
            return True

        user = await asyncio.to_thread(get_user, data['token'])
        print(user)

        if user is None:
            await close_ws(send, 1011)
            return True

        if len(connected_clients) == 0:
            game_state = {user.username: 5}
        else:
            game_state[user.username] = 5

        if user in connected_clients:
            print('duplicate connection')
        else:
            connected_clients.append(user)

async def websocket_application(scope, receive, send):
    while True:
        event = await receive()

        if event['type'] == 'lifespan.startup':
            await send({'type': 'lifespan.startup.complete'})
        elif event['type'] == 'lifespan.shutdown':
            await send({'type': 'lifespan.shutdown.complete'})

        if scope.get('path') != '/ws/flash':
            await close_ws(send, 1000)
            break

        if await new_handler(event, send):
            break
