# redis_client.py
import redis
import os
from datetime import datetime, timezone

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    password=os.environ.get("REDIS_PASSWORD", None),
    decode_responses=True
)

def update_last_updated():
    redis_client.set("last_updated", datetime.now(timezone.utc).isoformat())

def get_last_updated():
    value = redis_client.get("last_updated")
    return datetime.fromisoformat(value) if value else None