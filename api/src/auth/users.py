from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
import bcrypt
from tortoise.exceptions import DoesNotExist

from src.database.models import Users
from src.schemas.users import UserDatabaseSchema
from src.services.password_policy import (
    PASSWORD_MAX_AGE_DAYS,
    MAX_FAILED_LOGIN_ATTEMPTS,
    ACCOUNT_LOCKOUT_MINUTES,
)


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


async def check_account_locked(user: Users) -> None:
    """檢查帳號是否被鎖定"""
    if user.locked_until:
        now = datetime.now(timezone.utc)
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)

        if now < locked_until:
            remaining = int((locked_until - now).total_seconds() / 60) + 1
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"帳號已被鎖定，請於 {remaining} 分鐘後再試",
            )
        # 鎖定時間已過，重置計數
        user.locked_until = None
        user.failed_login_count = 0
        await user.save()


async def record_failed_login(user: Users) -> None:
    """記錄登入失敗並檢查是否需要鎖定"""
    user.failed_login_count = (user.failed_login_count or 0) + 1

    if user.failed_login_count >= MAX_FAILED_LOGIN_ATTEMPTS:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES)

    await user.save()


async def reset_failed_login(user: Users) -> None:
    """登入成功後重置失敗計數"""
    if user.failed_login_count > 0 or user.locked_until:
        user.failed_login_count = 0
        user.locked_until = None
        await user.save()


def check_password_expired(user: Users) -> bool:
    """檢查密碼是否已過期"""
    if not user.password_changed_at:
        return False  # 未記錄更改時間，視為未過期

    password_changed_at = user.password_changed_at
    if password_changed_at.tzinfo is None:
        password_changed_at = password_changed_at.replace(tzinfo=timezone.utc)

    expiry_date = password_changed_at + timedelta(days=PASSWORD_MAX_AGE_DAYS)
    return datetime.now(timezone.utc) > expiry_date


async def validate_user(user: OAuth2PasswordRequestForm = Depends()):
    """
    驗證用戶登入
    返回: UserDatabaseSchema (含 password_expired 欄位)
    """
    # 先查詢用戶（不透過 get_user 以便存取完整 model）
    try:
        db_user = await Users.get(username=user.username)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
        )

    # 檢查帳號是否啟用
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
        )

    # 檢查帳號是否被鎖定
    await check_account_locked(db_user)

    # 驗證密碼
    if not verify_password(user.password, db_user.password):
        await record_failed_login(db_user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼不正確",
        )

    # 登入成功，重置失敗計數
    await reset_failed_login(db_user)

    # 檢查密碼是否過期
    password_expired = check_password_expired(db_user)

    return UserDatabaseSchema(
        id=db_user.id,
        username=db_user.username,
        password=db_user.password,
        is_active=db_user.is_active,
        role=db_user.role,
        permissions=db_user.permissions,
        last_login=db_user.last_login,
        password_expired=password_expired,
    )
