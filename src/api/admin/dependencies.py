from fastapi import Depends

from src.api.auth.dependencies import get_current_user
from src.core.exceptions import ForbiddenError
from src.models.database import User


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise ForbiddenError(detail="Chỉ admin mới có quyền truy cập")
    return user
