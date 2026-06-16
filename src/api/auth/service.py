from sqlalchemy.orm import Session

from src.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from src.core.logging import get_logger
from src.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from src.models.database import User

logger = get_logger("api.auth.service")


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError(detail="Email hoặc mật khẩu không đúng")
    if not user.is_active:
        raise AuthenticationError(detail="Tài khoản đã bị khóa")
    return user


def register_user(db: Session, email: str, password: str, full_name: str) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ConflictError(detail="Email đã được sử dụng")

    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("New user registered: %s", email)
    return user


def create_tokens(user_id: str) -> dict:
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
        "expires_in": 1800,
    }


def refresh_tokens(db: Session, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise AuthenticationError(detail="Refresh token không hợp lệ hoặc đã hết hạn")

    if payload.get("type") != "refresh":
        raise AuthenticationError(detail="Token không phải refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise AuthenticationError(detail="User không tồn tại hoặc đã bị khóa")

    return create_tokens(user_id)
