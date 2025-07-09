from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
# from passlib.context import CryptContext
import bcrypt
from tortoise.exceptions import DoesNotExist

from src.database.models import Users
from src.schemas.users import UserDatabaseSchema

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash using bcrypt directly"""
    try:
        # Ensure inputs are byte strings
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
            
        # Verify the password
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt directly"""
    try:
        # Ensure password is a byte string
        if isinstance(password, str):
            password = password.encode('utf-8')
            
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        
        # Return the hash as a string for storage
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password",
        )

async def get_user(username: str):
    try:
        # 只查詢需要的欄位，避免關聯查詢
        user = await Users.get(username=username, is_active=True)
        
        if not user:
            raise DoesNotExist("User not found")
        
        return UserDatabaseSchema(
            id=user.id,
            username=user.username,
            password=user.password,
            is_active=user.is_active,
            role=user.role,
            permissions=user.permissions,
            last_login=user.last_login
        )
        
    except DoesNotExist:
        raise DoesNotExist("User not found")


async def validate_user(user: OAuth2PasswordRequestForm = Depends()):
    try:
        db_user = await get_user(user.username)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
        )

    return db_user