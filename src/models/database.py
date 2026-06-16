from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    clinical_notes: Mapped[list["ClinicalNote"]] = relationship(back_populates="user")


class ClinicalNote(Base, TimestampMixin):
    __tablename__ = "clinical_notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_transcript: Mapped[str] = mapped_column(Text, nullable=False, default="")
    soap_note: Mapped[str] = mapped_column(Text, nullable=False)
    audio_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship(back_populates="clinical_notes")
