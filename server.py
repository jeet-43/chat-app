import asyncio
import json
from datetime import datetime
from collections import deque

import websockets

HOST = "localhost"
PORT = 8765
MAX_MESSAGE_LENGTH = 500
RATE_LIMIT_COUNT = 5
RATE_LIMIT_WINDOW_SECONDS = 1.0

rooms = {}
client_activity = {}


def get_timestamp():
    return datetime.now().strftime("%H:%M")


def safe_json_loads(raw_message):
    try:
        return json.loads(raw_message)
    except (json.JSONDecodeError, TypeError):
        return None


async def send_message(websocket, payload):
    try:
        await websocket.send(json.dumps(payload))
    except Exception:
        pass


async def broadcast(room_name, payload, skip_websocket=None):
    if room_name not in rooms:
        return

    for websocket, _username in set(rooms[room_name]):
        if skip_websocket is not None and websocket == skip_websocket:
            continue
        await send_message(websocket, payload)


def remove_client(room_name, client):
    if room_name not in rooms:
        return

    rooms[room_name].discard(client)
    if not rooms[room_name]:
        del rooms[room_name]


def remove_client_activity(websocket):
    client_activity.pop(websocket, None)


def is_rate_limited(websocket):
    now = asyncio.get_running_loop().time()
    timestamps = client_activity.setdefault(websocket, deque())

    while timestamps and now - timestamps[0] > RATE_LIMIT_WINDOW_SECONDS:
        timestamps.popleft()

    if len(timestamps) >= RATE_LIMIT_COUNT:
        return True

    timestamps.append(now)
    return False


async def handle_join(websocket, username, room_name):
    if room_name not in rooms:
        rooms[room_name] = set()

    client = (websocket, username)
    rooms[room_name].add(client)

    await broadcast(room_name, {
        "type": "system",
        "text": f"{username} has joined the room",
        "timestamp": get_timestamp()
    })

    return client


async def handle_message(room_name, sender_username, message_text):
    await broadcast(room_name, {
        "type": "chat",
        "username": sender_username,
        "text": message_text,
        "timestamp": get_timestamp()
    })


async def handle_disconnect(room_name, client):
    remove_client(room_name, client)
    remove_client_activity(client[0])
    await broadcast(room_name, {
        "type": "system",
        "text": f"{client[1]} has left the room",
        "timestamp": get_timestamp()
    })


async def handle_connection(websocket):
    room_name = None
    client = None

    try:
        join_message = safe_json_loads(await websocket.recv())
        if not join_message:
            return

        if join_message.get("type") != "join":
            return

        username = join_message.get("username", "").strip()
        room_name = join_message.get("room", "").strip()
        if not username or not room_name:
            return
        client = await handle_join(websocket, username, room_name)

        async for message_text in websocket:
            parsed_message = safe_json_loads(message_text)
            if not parsed_message:
                continue

            if is_rate_limited(websocket):
                continue

            if parsed_message.get("type") == "message":
                text = parsed_message.get("text", "")
                if len(text) > MAX_MESSAGE_LENGTH:
                    continue
                await handle_message(room_name, username, text)
            elif parsed_message.get("type") == "typing":
                await broadcast(room_name, {
                    "type": "typing",
                    "username": parsed_message.get("username", "")
                }, skip_websocket=websocket)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if room_name and client:
            await handle_disconnect(room_name, client)


async def start_server():
    async with websockets.serve(handle_connection, HOST, PORT):
        await asyncio.Future()


asyncio.run(start_server())
