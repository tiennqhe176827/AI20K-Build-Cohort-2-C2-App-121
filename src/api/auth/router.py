from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.auth.dependencies import get_current_user
from src.api.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from src.api.auth.service import authenticate_user, create_tokens, refresh_tokens, register_user
from src.api.deps import get_db
from src.models.database import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Đăng nhập và nhận access/refresh token."""
    user = authenticate_user(db, request.email, request.password)
    tokens = create_tokens(str(user.id))
    return TokenResponse(**tokens)


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Đăng ký tài khoản mới."""
    user = register_user(db, request.email, request.password, request.full_name)
    tokens = create_tokens(str(user.id))
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Làm mới access token."""
    tokens = refresh_tokens(db, request.refresh_token)
    return TokenResponse(**tokens)


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)) -> dict:
    """Lấy thông tin user hiện tại."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }
