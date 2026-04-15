import redis
import os

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

keys = r.keys("user:*")
if keys:
    r.delete(*keys)
    print(f"Usunięto {len(keys)} wpisów: {sorted(keys)}")
else:
    print("Brak wpisów do usunięcia")
