import os
from fastapi import Request, HTTPException
from dotenv import load_dotenv

from app.dependencies.redis import RedisDep

load_dotenv()

async def rate_limit(request: Request, redis: RedisDep):
    ip = request.client.host 
    key = f"rate_limit:ip:{ip}"
    
    count = await redis.get(key)
    
    if count is None:
        await redis.set(key, 1, ex=60)
        
    elif int(count) >= int(os.getenv("MAX_REQUESTS_PER_MINUTE")):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    else:
        await redis.incr(key)