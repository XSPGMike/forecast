from async_asgi_testclient import TestClient
import asyncio
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from sesame.utils import get_token

from .ws_server import websocket_application

class WSTestCase(TransactionTestCase):
    async def test_connection_fails_if_wrong_path(self):
        async with TestClient(websocket_application) as client:
            ws = client.websocket_connect('/wrong-path')
            self.assertIsNotNone(ws)
            with self.assertRaises(AssertionError):
                await ws.connect()

    async def test_connection_success_but_sends_non_json(self):
        async with TestClient(websocket_application) as client:
            ws = client.websocket_connect('/ws/flash')
            self.assertIsNotNone(ws)
            await ws.connect()
            await ws.send_text('non-json')
            with self.assertRaisesMessage(Exception, "{'type': 'websocket.close', 'code': 1003}"):
                await ws.receive_text()
