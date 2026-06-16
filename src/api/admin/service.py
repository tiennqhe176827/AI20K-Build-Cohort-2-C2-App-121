from sqlalchemy.orm import Session

from src.models.database import ClinicalNote, User


def get_admin_stats(db: Session) -> dict:
    total_users = db.query(User).count()
    total_notes = db.query(ClinicalNote).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    return {
        "total_users": total_users,
        "total_notes": total_notes,
        "active_users": active_users,
    }
