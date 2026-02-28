from typing import Annotated
from fastapi import Depends
from redis import Redis

from app.core.redis import get_redis

RedisDep = Annotated[Redis, Depends(get_redis)]