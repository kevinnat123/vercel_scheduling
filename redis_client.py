# redis_client.py
import redis
import os
import config
from datetime import datetime, timezone

redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    decode_responses=True
)

def update_last_updated():
    redis_client.set("last_updated", datetime.now(timezone.utc).isoformat())

def get_last_updated():
    value = redis_client.get("last_updated")
    return datetime.fromisoformat(value) if value else None