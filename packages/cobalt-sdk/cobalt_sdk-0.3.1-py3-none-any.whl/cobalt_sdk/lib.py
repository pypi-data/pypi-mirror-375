import json
from websockets.asyncio.client import connect, ClientConnection


def proto_connect() -> ClientConnection:
    """
    Connect to the protocol WebSocket server.

    プロトコルWebSocketサーバーに接続します。
    """
    return connect("ws://localhost:23787")


def data_connect() -> ClientConnection:
    """
    Connect to the data WebSocket server.

    データWebSocketサーバーに接続します。
    """
    return connect("ws://localhost:9030", max_size=10 * 1024 * 1024)


async def subscribe_objects(ws: ClientConnection):
    """
    Subscribe to object detection data on a WebSocket connection.

    WebSocket接続でオブジェクト検出データを購読します。
    """
    msg = json.dumps([{"token": "COBJ", "subscribed": True}])
    await ws.send(msg)


async def subscribe_foreground_cloud(ws: ClientConnection):
    """Subscribe to foreground cloud data on a WebSocket connection."""
    msg = json.dumps([{"token": "FGCL", "subscribed": True}])
    await ws.send(msg)


async def subscribe_background_cloud(ws: ClientConnection):
    """Subscribe to background cloud data on a WebSocket connection."""
    msg = json.dumps([{"token": "BGCL", "subscribed": True}])
    await ws.send(msg)


async def subscribe_ground_cloud(ws: ClientConnection):
    """Subscribe to ground cloud data on a WebSocket connection."""
    msg = json.dumps([{"token": "GRCL", "subscribed": True}])
    await ws.send(msg)


async def subscribe_base_cloud(ws: ClientConnection):
    """Subscribe to base cloud data on a WebSocket connection."""
    msg = json.dumps([{"token": "HCLD", "subscribed": True}])
    await ws.send(msg)
