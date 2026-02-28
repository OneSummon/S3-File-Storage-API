import os
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.core.session_dep import SessionDep


load_dotenv()

class CurrentUser(BaseModel):
    id: int
    role: str
    
    
#hashing----------------------------------------------------------

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        hashed.encode('utf-8')
    )


#create-access-token----------------------------------------------
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id or not role:
            raise HTTPException(status_code=401)
        
        if role not in ["user", "admin"]:
            raise HTTPException(status_code=403)
        
        from app.crud.auth import get_user # circle import fix
        
        user = await get_user(user_id, session)
        if not user:
            raise HTTPException(status_code=401)
        
        return user
        
    except JWTError:
        raise HTTPException(status_code=401)