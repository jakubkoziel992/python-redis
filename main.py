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
    decode_responses=True
)

# 🔹 seed danych
@app.get("/seed")
def seed():
    for i in range(10):
        key = f"user:{i}"
        value = {
            "id": i,
            "name": f"user_{i}"
        }
        r.set(key, json.dumps(value))

    return {"status": "saved 10 records"}


# 🔹 pobranie wszystkich userów
@app.get("/users")
def get_users():
    result = []

    for i in range(10):
        key = f"user:{i}"
        data = r.get(key)

        if data:
            result.append(json.loads(data))

    return result


# 🔹 pobranie jednego usera
@app.get("/users/{user_id}")
def get_user(user_id: int):
    key = f"user:{user_id}"
    data = r.get(key)

    if not data:
        raise HTTPException(status_code=404, detail="not found")

    return json.loads(data)