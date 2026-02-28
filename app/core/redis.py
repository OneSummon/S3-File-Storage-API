import os
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

redis: Redis | None = None

async def get_redis() -> Redis:
    global redis
    
    if redis is None:
        redis = Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
        
    return redis