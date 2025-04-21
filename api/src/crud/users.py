from fastapi import HTTPException
# from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist, IntegrityError
from src.auth.users import get_password_hash
from src.database.models import Users
from src.schemas.token import Status
from src.schemas.users import UserOutSchema, UserInSchema
from datetime import datetime

from typing import NewType
UserId = NewType("UserId", int)

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user_in: UserInSchema) -> UserOutSchema: # type: ignore[UserInSchema, UserOutSchema]
    # user_in.password = pwd_context.encrypt(user_in.password)
    user_in.password = get_password_hash(user_in.password)

    try:
        user_obj = await Users.create(**user_in.dict(exclude_unset=True))
    except IntegrityError:
        raise HTTPException(status_code=401, detail=f"Sorry, that username already exists.")

    return await UserOutSchema.from_tortoise_orm(user_obj)


async def delete_user(user_id: UserId, current_user: UserOutSchema) -> Status: # type: ignore[UserOutSchema]
    try:
        db_user = await UserOutSchema.from_queryset_single(Users.get(id=user_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    if db_user.id == current_user.id:
        deleted_count = await Users.filter(id=user_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return Status(message=f"Deleted user {user_id}")

    raise HTTPException(status_code=403, detail=f"Not authorized to delete")

async def update_last_login(user_id: UserId) -> None:
    try:
        user = await Users.get(id=user_id)
        user.last_login = datetime.now()
        await user.save()

    except DoesNotExist:
        print(f"嘗試更新不存在的使用者ID {user_id} 的登入時間")