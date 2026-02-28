from datetime import datetime
from sqlalchemy import select
from app.core.session_dep import SessionDep
from app.database.models import User

from app.core.security import hash_password

async def get_user(user_id: int, session: SessionDep):
    user_id = int(user_id)
    return await session.scalar(select(User).where(User.id == user_id))

async def get_user_by_username(username: str, session: SessionDep):
    return await session.scalar(select(User).where(User.username == username))

async def set_user(username: str, password: str, session: SessionDep):
    new_user = User(username=username, hashed_password=hash_password(password), role="user", created_at=datetime.now())
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return new_user