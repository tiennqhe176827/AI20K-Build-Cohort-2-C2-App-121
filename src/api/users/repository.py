from sqlalchemy.orm import Session

from src.core.exceptions import NotFoundError
from src.models.database import ClinicalNote, User


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError(resource="User")
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: int, **kwargs) -> User:
    user = get_user_by_id(db, user_id)
    for key, value in kwargs.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: int, new_hashed_password: str) -> User:
    user = get_user_by_id(db, user_id)
    user.hashed_password = new_hashed_password
    db.commit()
    db.refresh(user)
    return user


def count_clinical_notes(db: Session, user_id: int) -> int:
    return db.query(ClinicalNote).filter(ClinicalNote.user_id == user_id).count()


def list_users(db: Session, skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    return users, total


def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
