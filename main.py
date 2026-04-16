from fastapi import FastAPI, HTTPException
import redis
import psycopg2
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

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_DB = os.getenv("PG_DB", "postgres")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")

def get_pg():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

@app.get("/")
def index():
    return {
        "app": "python-redis",
        "endpoints": ["/health", "/seed", "/users", "/users/{user_id}"]
    }

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
    except (redis.ConnectionError, redis.TimeoutError):
        raise HTTPException(status_code=503, detail="brak połączenia z Redis")

    try:
        conn = get_pg()
        cur = conn.cursor()
        cur.execute("SELECT current_user, current_database()")
        pg_user, pg_db = cur.fetchone()
        print(f"[PG] połączono jako: {pg_user}, baza: {pg_db}")

        cur.execute("SHOW search_path")
        search_path = cur.fetchone()[0]
        print(f"[PG] search_path: {search_path}")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        for i in range(next_id, next_id + 10):
            cur.execute(
                "INSERT INTO users (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
                (i, f"user_{i}")
            )
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"brak połączenia z PostgreSQL: {e}")

    return {"status": f"saved 10 records (id {next_id}–{next_id + 9})"}


# 🔹 pobranie wszystkich userów
@app.get("/users")
def get_users():
    try:
        keys = r.keys("user:*")
        result = [json.loads(r.get(key)) for key in sorted(keys, key=lambda k: int(k.split(":")[1]))]
    except (redis.ConnectionError, redis.TimeoutError):
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