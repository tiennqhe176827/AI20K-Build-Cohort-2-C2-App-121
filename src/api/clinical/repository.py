from sqlalchemy.orm import Session

from src.models.database import ClinicalNote


def save_note(
    db: Session,
    user_id: int,
    transcript: str,
    corrected_transcript: str,
    soap_note: str,
    audio_filename: str | None = None,
) -> ClinicalNote:
    note = ClinicalNote(
        user_id=user_id,
        transcript=transcript,
        corrected_transcript=corrected_transcript,
        soap_note=soap_note,
        audio_filename=audio_filename,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[ClinicalNote]:
    return (
        db.query(ClinicalNote)
        .filter(ClinicalNote.user_id == user_id)
        .order_by(ClinicalNote.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_notes_by_user(db: Session, user_id: int) -> int:
    return db.query(ClinicalNote).filter(ClinicalNote.user_id == user_id).count()


def get_note_by_id(db: Session, note_id: int, user_id: int) -> ClinicalNote | None:
    return (
        db.query(ClinicalNote)
        .filter(ClinicalNote.id == note_id, ClinicalNote.user_id == user_id)
        .first()
    )


def delete_note(db: Session, note_id: int, user_id: int) -> bool:
    note = get_note_by_id(db, note_id, user_id)
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True
