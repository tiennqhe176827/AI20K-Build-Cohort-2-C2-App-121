from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="Tin nhắn từ user")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Phản hồi từ agent")
    analysis: str = Field(default="", description="Phân tích nội bộ")



class ClinicalSoapResponse(BaseModel):
    transcript: str = Field(..., description="Transcript thô từ ASR")
    corrected_transcript: str = Field(..., description="Transcript sau hiệu đính")
    soap_note: str = Field(..., description="SOAP note được tạo từ transcript")
