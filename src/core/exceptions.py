from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: dict | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationError(AppError):
    def __init__(self, detail: str = "Không thể xác thực", headers: dict | None = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers or {"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(AppError):
    def __init__(self, detail: str = "Không có quyền truy cập"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundError(AppError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} không tồn tại",
        )


class ValidationError(AppError):
    def __init__(self, detail: str = "Dữ liệu không hợp lệ"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ConflictError(AppError):
    def __init__(self, detail: str = "Dữ liệu đã tồn tại"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
