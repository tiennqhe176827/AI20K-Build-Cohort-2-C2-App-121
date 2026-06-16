from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.auth.dependencies import get_current_user
from src.api.deps import get_db
from src.api.users.schemas import AccountSummary, ChangePasswordRequest, UserList, UserResponse, UserUpdate
from src.api.users.service import change_user_password, get_profile, get_user_list, update_profile
from src.models.database import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=AccountSummary)
async def get_my_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Lấy thông tin tài khoản của chính mình."""
    return get_profile(db, user.id)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    request: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Cập nhật hồ sơ của chính mình."""
    return update_profile(db, user.id, full_name=request.full_name, email=request.email)


@router.post("/me/change-password")
async def change_my_password(
    request: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Đổi mật khẩu."""
    return change_user_password(db, user.id, request.current_password, request.new_password)


@router.get("/", response_model=UserList)
async def list_all_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Danh sách tất cả users (đăng nhập mới xem được)."""
    return get_user_list(db, page=page, size=size)
