from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from src.auth.users import get_password_hash
from src.database.models import Users, Offices
from src.schemas.token import Status
from src.schemas.users import UserOutSchema, UserInSchema, SimpleOfficeSchema, UserId
from datetime import datetime

async def create_user(user_in: UserInSchema) -> UserOutSchema: # type: ignore[UserInSchema, UserOutSchema]
    # user_in.password = pwd_context.encrypt(user_in.password)
    user_in.password = get_password_hash(user_in.password)

    try:
        user_obj = await Users.create(**user_in.dict(exclude_unset=True))
    except IntegrityError:
        raise HTTPException(status_code=401, detail=f"Sorry, that username already exists.")

    return await build_user_out_schema(user_obj)


async def delete_user(user_id: UserId, current_user: UserOutSchema) -> Status: # type: ignore[UserOutSchema]
    try:
        user = await Users.filter(id=user_id).only(
            'id', 'username', 'full_name', 'email', 'office_id', 
            'job_title', 'is_active', 'role', 'permissions', 'last_login'
        ).first()
        
        if not user:
            raise DoesNotExist()
            
        db_user = await build_user_out_schema(user)
        
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

async def build_user_out_schema(user: Users) -> UserOutSchema:
    """安全地從 Users 模型構建 UserOutSchema"""
    
    # 查詢辦公室資料
    office_data = None
    if hasattr(user, 'office_id') and user.office_id:
        try:
            office = await Offices.filter(id=user.office_id).only(
                'id', 'name', 'short_name', 'code', 'classification', 'is_funding_source'
            ).first()
            
            if office:
                office_data = SimpleOfficeSchema(
                    id=office.id,
                    name=office.name,
                    short_name=office.short_name,
                    code=office.code,
                    classification=office.classification,
                    is_funding_source=office.is_funding_source
                )
        except Exception as e:
            print(f"Error loading office for user {user.id}: {e}")
    
    return UserOutSchema(
        id=user.id,
        username=user.username,
        full_name=getattr(user, 'full_name', None),
        email=getattr(user, 'email', None),
        job_title=getattr(user, 'job_title', None),
        is_active=user.is_active,
        role=getattr(user, 'role', None),
        permissions=getattr(user, 'permissions', None),
        last_login=getattr(user, 'last_login', None),
        office=office_data
    )

async def get_user_by_id(user_id: UserId) -> UserOutSchema:
    """安全地根據 ID 獲取用戶"""
    try:
        user = await Users.filter(id=user_id).only(
            'id', 'username', 'full_name', 'email', 'office_id', 
            'job_title', 'is_active', 'role', 'permissions', 'last_login'
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        return await build_user_out_schema(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_user_by_username(username: str) -> UserOutSchema:
    """安全地根據用戶名獲取用戶"""
    try:
        user = await Users.filter(username=username).only(
            'id', 'username', 'full_name', 'email', 'office_id', 
            'job_title', 'is_active', 'role', 'permissions', 'last_login'
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {username} not found")
        
        return await build_user_out_schema(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))