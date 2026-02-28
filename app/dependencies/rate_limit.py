from typing import Annotated
from fastapi import Depends

from app.core.rate_limit import rate_limit


RateLimitDep = Annotated[None, Depends(rate_limit)]