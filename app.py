from flask import Flask, jsonify
import redis
import time
import os
import json

app = Flask(__name__)

# konfiguracja z envów
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# połączenie do Redis
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def get_expensive_data():
    time.sleep(3)
    return {"data": "To są dane z backendu", "timestamp": time.time()}

@app.route("/data")
def get_data():
    cache_key = "my_data"

    cached = r.get(cache_key)
    if cached:
        return jsonify({
            "source": "cache",
            "value": json.loads(cached)
        })

    data = get_expensive_data()

    r.setex(cache_key, 10, json.dumps(data))

    return jsonify({
        "source": "backend",
        "value": data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)