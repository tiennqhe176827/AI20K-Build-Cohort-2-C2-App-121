from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    message: str = "Thành công"


class ErrorResponse(BaseModel):
    detail: str
    status_code: int


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Trang hiện tại")
    size: int = Field(default=20, ge=1, le=100, description="Số item mỗi trang")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    items: list = []
    total: int = 0
    page: int = 1
    size: int = 20
    pages: int = 0
