# Redis Chat Memory

A small, beginner-friendly Python project that shows how to give a chatbot **short-term memory** using **Redis**.
Every user's messages are stored in a Redis list, the most recent ones can be fetched at any time, and the whole conversation **expires automatically** after a set time (TTL).

This is the same pattern used to feed conversation history to an LLM chatbot, without a heavy database.

---

## Why Redis for chat memory?

| Need | How Redis helps |
|---|---|
| Speed | Data lives in RAM, so reads and writes take well under a millisecond |
| Ordered history | Redis **lists** keep messages in the order they arrive |
| Auto cleanup | `EXPIRE` deletes old chats by itself, no cron job needed |
| Simplicity | Three commands (`LPUSH`, `LRANGE`, `EXPIRE`) cover the whole feature |

---

## Features

- Store chat messages per user (`chat:<user_id>` key)
- Fetch the latest N messages
- Automatic expiry of a conversation after `CHAT_TTL_SECONDS`
- TTL timer resets on every new message
- Two versions to compare: with and without expiry

---

## Project structure

```
Redis chat memory/
├── redis_client.py      # Creates the Redis connection
├── chat_memory.py       # Basic memory: add + get messages (no expiry)
├── chat_memory_ttl.py   # Memory with TTL: chat auto-deletes after N seconds
├── app.py               # Demo: add messages, read them, wait, read again
├── main.py              # Placeholder entry point
├── steps.txt            # Quick setup notes
├── pyproject.toml       # Project metadata (uv)
└── .python-version      # Python version used (3.14)
```

---

## How it works

```
   add_message(user, "hii")
            │
            ▼
   LPUSH chat:user "hii"      ← newest message goes to the front of the list
   EXPIRE chat:user 20        ← (TTL version) restart the countdown
            │
            ▼
   get_recent_messages(user)
            │
            ▼
   LRANGE chat:user 0 4       ← latest 5 messages, newest first
```

- **Key format:** `chat:<user_id>`, for example `chat:sourabh`
- **Order:** because `LPUSH` adds to the front, `get_recent_messages` returns the **newest message first**
- **TTL:** after `CHAT_TTL_SECONDS` without a new message, Redis deletes the key and the history becomes an empty list `[]`

---

## Prerequisites

- Python 3.14 (see `.python-version`)
- [uv](https://docs.astral.sh/uv/) package manager
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (to run Redis)

---

## Setup

### 1. Create and activate a virtual environment

```powershell
uv venv
.venv\Scripts\activate
```

### 2. Install the dependency

```powershell
uv pip install redis
```

### 3. Start Redis with Docker

Turn on Docker Desktop and wait until it shows **Engine running**, then:

```powershell
docker run -d -p 6379:6379 --name redis redis
```

Check that it is running:

```powershell
docker ps
docker exec -it redis redis-cli ping
```

You should see `PONG`.

> Next time, do not run `docker run` again. Use `docker start redis` and `docker stop redis`.

---

## Run the demo

```powershell
python app.py
```

What the demo does:

1. Adds three messages for the user `sourabh`
2. Prints the recent chat history
3. Waits 20 seconds (the TTL)
4. Reads the history again, which is now empty

Expected output:

```
recent chat history
- r u okay
- how's u
- hii
waiting for time to delete...
after ttl expiry:
[]
```

The empty list at the end is the correct result. It proves the chat expired.

---

## Usage in your own code

```python
from chat_memory_ttl import add_message, get_recent_messages

add_message("user_1", "Hello")
add_message("user_1", "I have a headache")

history = get_recent_messages("user_1", limit=5)   # newest first
history = list(reversed(history))                  # oldest first, ready for an LLM prompt
```

---

## Configuration

| Setting | File | Default | Meaning |
|---|---|---|---|
| `host` / `port` / `db` | `redis_client.py` | `localhost` / `6379` / `0` | Where Redis is running |
| `decode_responses` | `redis_client.py` | `True` | Returns normal strings instead of bytes |
| `CHAT_TTL_SECONDS` | `chat_memory_ttl.py` | `20` | Seconds before a chat expires (use `3600` for 1 hour in real use) |
| `limit` | `get_recent_messages` | `5` | How many recent messages to return |

---

## Inspect data directly in Redis

```powershell
docker exec -it redis redis-cli
```

```
LRANGE chat:sourabh 0 -1     # see all messages
TTL chat:sourabh             # seconds left before expiry (-2 means the key is gone)
KEYS chat:*                  # list all chats
DEL chat:sourabh             # delete one chat manually
```

---

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `docker` is not recognized | Docker Desktop is not installed, or the terminal is old. Restart VS Code, or add `C:\Program Files\Docker\Docker\resources\bin` to PATH |
| `pull access denied for name` | Typo in the command. Use `--name` (no space), not `-- name` |
| `module 'redis' has no attribute 'redis'` | The class is `redis.Redis` with a capital R |
| `ConnectionError` / connection refused | The container is stopped. Run `docker start redis` |
| `'int' object has no attribute 'lpush'` | `redis_client` was overwritten by a number. Keep `redis_client = get_redis_client()` on its own line, with `()` |
| History returns `[]` too early | TTL is only 20 seconds. Increase `CHAT_TTL_SECONDS` |

---

## Roadmap

- [ ] Limit history length with `LTRIM` (keep only the last N messages)
- [ ] Store the role (`user` / `assistant`) with each message as JSON
- [ ] Connect it to an LLM chatbot (for example a FastAPI + Groq app)
- [ ] Read Redis host and port from environment variables (`.env`)
- [ ] Add tests

---

## Tech stack

Python, Redis, Docker, uv

---

## Note

Redis keeps data in memory, so this is meant for **temporary** conversation context. For permanent chat history, store messages in a regular database as well.
