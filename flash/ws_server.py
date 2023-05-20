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

async def close_ws(send, code):
    await send({
        'type': 'websocket.close',
        'code': code if code else 1000
    })

async def send_ws(ws, data):
    await ws({'type': 'websocket.send', 'text': json.dumps(data)})

async def handler(event, send):
    global connected_clients
    global game_state
    data = None

    if event['type'] == 'websocket.connect':
        await send({
            'type': 'websocket.accept'
        })

    if event['type'] == 'websocket.disconnect':
        for client in connected_clients:
            if(client["ws"] == send):
                connected_clients.remove(client)
                for curr in connected_clients:
                    await curr["ws"]({'type': 'websocket.send', 'text': json.dumps({'event': 'user_disconnected', 'user': client["user"].username})})
                break
        return True

    if event['type'] == 'websocket.receive':
        if send not in [client["ws"] for client in connected_clients]:
            try:
                data = json.loads(event['text'])
                if 'token' not in data:
                    raise Exception('no token')
            except:
                await close_ws(send, 1003)
                return True

            user = await asyncio.to_thread(get_user, data['token'])

            if user is None:
                await close_ws(send, 1011)
                return True

            if len(connected_clients) == 0:
                game_state = {user.username: 5}
            else:
                game_state[user.username] = 5

            if user not in connected_clients:
                for curr in connected_clients:
                    await send({'type': 'websocket.send', 'text': json.dumps({'event': 'user_connected', 'user': curr["user"].username})})
                    await curr["ws"]({'type': 'websocket.send', 'text': json.dumps({'event': 'user_connected', 'user': user.username})})
                connected_clients.append({"ws": send, "user": user})
        else:
            data = json.loads(event['text'])
            if data['event'] == 'range':
                val = int(data['value'])
                user = [client["user"] for client in connected_clients if client["ws"] == send][0]
                game_state[user.username] = val
                for client in list(filter(lambda client: client["ws"] != send, connected_clients)):
                    await client["ws"]({'type': 'websocket.send', 'text': json.dumps({'event': 'range', 'user': user.username, 'value': val})})
            elif data['event'] == 'end':
                outcome = data["outcome"] == "y"
                await asyncio.to_thread(Flash.objects.filter(active=True).update, active=False, votes=json.dumps(game_state), outcome=outcome)
                for client in connected_clients:
                    await client["ws"]({'type': 'websocket.send', 'text': json.dumps({'event': 'end'})})
                connected_clients = []
                game_state = {}

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

        if await handler(event, send):
            break
