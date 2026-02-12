from fastapi import Depends, HTTPException, status

from src.auth.jwthandler import get_current_user
from src.database.models.user import User


def require_role(*roles: str):
    """Dependency that checks user role."""

    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not authorized",
            )
        return user

    return checker


require_seller = require_role("seller", "admin")
require_admin = require_role("admin")
