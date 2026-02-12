from fastapi import APIRouter, Depends, HTTPException, status
from passlib.hash import bcrypt

from src.auth.jwthandler import create_access_token, get_current_user
from src.database.models.user import User
from src.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate):
    if await User.exists(email=data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await User.exists(username=data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = await User.create(
        email=data.email,
        username=data.username,
        password_hash=bcrypt.hash(data.password),
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await User.get_or_none(username=data.username)
    if not user or not bcrypt.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user
