from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.exceptions import AuthenticationError
from src.core.security import decode_token
from src.models.database import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise AuthenticationError(detail="Token không hợp lệ hoặc đã hết hạn")

    if payload.get("type") != "access":
        raise AuthenticationError(detail="Token không phải access token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError(detail="Token không hợp lệ")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise AuthenticationError(detail="User không tồn tại")
    if not user.is_active:
        raise AuthenticationError(detail="Tài khoản đã bị khóa")

    return user


def require_role(*roles: str):
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            from src.core.exceptions import ForbiddenError
            raise ForbiddenError(detail=f"Cần quyền: {', '.join(roles)}")
        return user
    return role_checker
