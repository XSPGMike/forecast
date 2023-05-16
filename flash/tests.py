from django.test import TestCase
from async_asgi_testclient import TestClient
from .ws_server import websocket_application

class WSTestCase(TestCase):
    async def test_server_works(self):
        async with TestClient(websocket_application)  as client:
            ws = client.websocket_connect('/ws/flash')
            self.assertNotEqual(ws, None)
            await ws.connect()
            await ws.send_text('something')
