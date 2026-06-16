from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.api.clinical.schemas import ClinicalNoteOut, ClinicalSoapResponse
from src.api.clinical.service import ALLOWED_AUDIO_EXTENSIONS, process_audio_upload, validate_audio_extension
from src.api.auth.dependencies import get_current_user
from src.api.deps import get_db
from src.core.exceptions import AppError, ValidationError
from src.models.database import User

router = APIRouter(prefix="/clinical", tags=["Clinical"])


@router.post("/soap-note", response_model=ClinicalSoapResponse)
async def create_soap_note(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClinicalSoapResponse:
    """Nhận file âm thanh khám bệnh và trả về SOAP note."""
    try:
        validate_audio_extension(file.filename)
    except ValueError as e:
        raise ValidationError(detail=str(e))

    content = await file.read()
    if not content:
        raise ValidationError(detail="File âm thanh trống")

    try:
        result = await process_audio_upload(content, file.filename)
    except (ValueError, RuntimeError) as e:
        raise AppError(status_code=500, detail=str(e))

    from src.api.clinical.repository import save_note

    save_note(
        db=db,
        user_id=user.id,
        transcript=result["transcript"],
        corrected_transcript=result["corrected_transcript"],
        soap_note=result["soap_note"],
        audio_filename=file.filename,
    )

    return ClinicalSoapResponse(**result)


@router.get("/history", response_model=list[ClinicalNoteOut])
async def get_clinical_history(
    skip: int = 0,
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ClinicalNoteOut]:
    """Lấy lịch sử SOAP notes của user."""
    from src.api.clinical.repository import get_notes_by_user

    notes = get_notes_by_user(db, user.id, skip=skip, limit=limit)
    return [
        ClinicalNoteOut(
            id=n.id,
            transcript=n.transcript,
            corrected_transcript=n.corrected_transcript,
            soap_note=n.soap_note,
            audio_filename=n.audio_filename,
            created_at=n.created_at.isoformat(),
        )
        for n in notes
    ]
