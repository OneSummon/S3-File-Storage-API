from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.crud.auth import get_user_by_username, set_user
from app.core.security import create_access_token, verify_password
from app.schemas.auth import CreateUser, Token
from app.core.session_dep import SessionDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(user: CreateUser, session: SessionDep):
    existing_user = await get_user_by_username(user.username, session)
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )
    
    new_user = await set_user(user.username, user.password, session)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "created_at": new_user.created_at
    }


@router.post("/login", response_model=Token)
async def login(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
    ):
    
    existing_user = await get_user_by_username(form_data.username, session)
    
    if not existing_user:
        raise HTTPException(status_code=401)
    
    if not verify_password(form_data.password, existing_user.hashed_password):
        raise HTTPException(status_code=401)
    
    token = create_access_token(
        {
            "sub": str(existing_user.id),
            "role": existing_user.role
        }
    )
    
    return {"access_token": token}