# Chat App

A real-time multi-room chat application built with a Python WebSocket backend and a vanilla JS frontend. No frameworks, no dependencies beyond the `websockets` library.

![dark theme](https://img.shields.io/badge/theme-dark%20%2F%20light-black) ![python](https://img.shields.io/badge/python-3.10+-blue) ![license](https://img.shields.io/badge/license-MIT-green)

<img width="1903" height="939" alt="image" src="https://github.com/user-attachments/assets/b6b6e48f-7a6f-4404-bb77-b7fb08a7c50f" />
<img width="1871" height="922" alt="image" src="https://github.com/user-attachments/assets/76923378-cf7b-46d7-b286-ea6df0c0c35c" />
<img width="1886" height="951" alt="image" src="https://github.com/user-attachments/assets/f1616b89-e0ba-484a-b056-5f55998df1a8" />



---

## Features

- **Real-time messaging** over WebSockets — no polling
- **Multi-room support** — join any named room, isolated from others
- **Typing indicators** with debounce so they don't spam
- **Dark / light theme** toggle, persisted in localStorage
- **Connection status** dot with live feedback and a reconnect button on drop
- **Character counter** (500 char limit enforced on both client and server)
- **Rate limiting** — max 5 messages per second per client, handled server-side
- **Particle canvas** on the welcome screen with mouse repulsion
- **Browser history API** — back/forward navigation works between screens

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3, `asyncio`, `websockets` |
| Frontend | Vanilla JS, HTML, CSS (no frameworks) |
| Transport | WebSocket (`ws://`) |

---

## Getting Started

**Requirements:** Python 3.10+

```bash
# Install the dependency
pip install websockets

# Start the server
python server.py
```

Then open `index.html` in your browser. That's it.

> By default the server runs on `ws://localhost:8765`. To change it, edit `WS_URL` at the top of the `<script>` block in `index.html`, and `HOST`/`PORT` in `server.py`.

---

## Architecture

```
Browser (index.html)
    │
    │  WebSocket (ws://localhost:8765)
    ▼
server.py
    ├── rooms{}          # dict of room_name → set of (websocket, username)
    ├── client_activity  # per-client deque of timestamps for rate limiting
    └── broadcast()      # fans out a message to all clients in a room
```

Each client sends a `join` message on connect with a username and room name. After that, the server routes `chat` and `typing` messages to everyone else in the same room. Disconnects are caught in a `finally` block so the room always gets a leave notification.

---

## Project Structure

```
├── index.html    # entire frontend — UI, WebSocket logic, canvas animation
├── server.py     # async WebSocket server
└── favicon.svg
```

---

## License

MIT
