from pydantic import BaseModel, Field


class ClinicalSoapResponse(BaseModel):
    transcript: str = Field(..., description="Transcript thô từ ASR")
    corrected_transcript: str = Field(..., description="Transcript sau hiệu đính")
    soap_note: str = Field(..., description="SOAP note được tạo từ transcript")


class ClinicalNoteOut(BaseModel):
    id: int
    transcript: str
    corrected_transcript: str
    soap_note: str
    audio_filename: str | None = None
    created_at: str

    model_config = {"from_attributes": True}
