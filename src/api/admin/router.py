from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.admin.dependencies import require_admin
from src.api.admin.schemas import AdminStats
from src.api.admin.service import get_admin_stats
from src.api.deps import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    admin: None = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    """Lấy thống kê hệ thống (chỉ admin)."""
    return get_admin_stats(db)
