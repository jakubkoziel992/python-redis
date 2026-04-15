from fastapi import FastAPI, HTTPException
import redis
import os
import json

app = FastAPI()

# konfiguracja z envów
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=15,
    socket_timeout=15
)

# 🔹 health check
@app.get("/health")
def health():
    return {"status": "ok"}


# 🔹 seed danych
@app.get("/seed")
def seed():
    try:
        existing = r.keys("user:*")
        next_id = max((int(k.split(":")[1]) for k in existing), default=-1) + 1
        for i in range(next_id, next_id + 10):
            r.set(f"user:{i}", json.dumps({"id": i, "name": f"user_{i}"}))
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="brak połączenia z Redis")

    return {"status": f"saved 10 records (id {next_id}–{next_id + 9})"}


# 🔹 pobranie wszystkich userów
@app.get("/users")
def get_users():
    try:
        keys = r.keys("user:*")
        result = [json.loads(r.get(key)) for key in sorted(keys, key=lambda k: int(k.split(":")[1]))]
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="brak połączenia z Redis")

    return result

# 🔹 pobranie jednego usera
@app.get("/users/{user_id}")
def get_user(user_id: int):
    key = f"user:{user_id}"
    data = r.get(key)

    if not data:
        raise HTTPException(status_code=404, detail="not found")

    return json.loads(data)