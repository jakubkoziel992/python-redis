# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the application:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Run with auto-reload (development):**
```bash
uvicorn main:app --reload
```

## Architecture

This is a minimal FastAPI REST API backed by Redis. All logic lives in [main.py](main.py).

**Request flow:**
```
HTTP client → FastAPI (main.py) → Redis client → Redis server
```

**Redis connection** is configured entirely through environment variables:
- `REDIS_HOST` (default: `localhost`)
- `REDIS_PORT` (default: `6379`)
- `REDIS_DB` (default: `0`)
- `REDIS_PASSWORD` (default: none)

**Data model:** Users are stored as JSON strings under keys `user:{id}` (e.g. `user:0`). The shape is `{"id": int, "name": str}`.

**Endpoints:**
- `GET /seed` — writes 10 hardcoded users (`user:0`–`user:9`) into Redis
- `GET /users` — reads `user:0`–`user:9` and returns all that exist
- `GET /users/{user_id}` — reads a single `user:{user_id}` key, returns 404 if missing

**Deployment:** The `Procfile` targets Heroku. Redis is expected as an external service (e.g. Heroku Redis add-on).
