from sqlalchemy.orm import Session

from src.api.users.repository import (
    change_password,
    count_clinical_notes,
    get_user_by_id,
    list_users,
    update_user,
)
from src.core.exceptions import AuthenticationError, NotFoundError
from src.core.security import hash_password, verify_password


def get_profile(db: Session, user_id: int) -> dict:
    user = get_user_by_id(db, user_id)
    notes_count = count_clinical_notes(db, user_id)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "clinical_notes_count": notes_count,
    }


def update_profile(db: Session, user_id: int, full_name: str | None = None, email: str | None = None) -> dict:
    user = update_user(db, user_id, full_name=full_name, email=email)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }


def change_user_password(db: Session, user_id: int, current_password: str, new_password: str) -> dict:
    user = get_user_by_id(db, user_id)
    if not verify_password(current_password, user.hashed_password):
        raise AuthenticationError(detail="Mật khẩu hiện tại không đúng")
    change_password(db, user_id, hash_password(new_password))
    return {"message": "Đổi mật khẩu thành công"}


def get_user_list(db: Session, page: int = 1, size: int = 20) -> dict:
    skip = (page - 1) * size
    users, total = list_users(db, skip=skip, limit=size)
    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
                "updated_at": u.updated_at.isoformat(),
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }
