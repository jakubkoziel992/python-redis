from flask import Flask, jsonify
import redis
import os
import json

app = Flask(__name__)

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

# 🔹 endpoint zapisujący dane
@app.route("/seed")
def seed():
    for i in range(10):
        key = f"user:{i}"
        value = {
            "id": i,
            "name": f"user_{i}"
        }
        r.set(key, json.dumps(value))  # brak TTL

    return jsonify({"status": "saved 10 records"})


# 🔹 endpoint zwracający wszystkie dane
@app.route("/users")
def get_users():
    result = []

    for i in range(10):
        key = f"user:{i}"
        data = r.get(key)

        if data:
            result.append(json.loads(data))

    return jsonify(result)


# 🔹 endpoint dla jednego usera
@app.route("/users/<int:user_id>")
def get_user(user_id):
    key = f"user:{user_id}"
    data = r.get(key)

    if not data:
        return jsonify({"error": "not found"}), 404

    return jsonify(json.loads(data))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)