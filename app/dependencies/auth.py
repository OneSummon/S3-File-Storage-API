from typing import Annotated

from fastapi import Depends

from app.core.security import get_current_user
from app.database.models import User


CurrentUserDep = Annotated[User, Depends(get_current_user)]