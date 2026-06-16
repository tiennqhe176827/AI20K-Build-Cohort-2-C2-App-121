from fastapi import APIRouter

from src.api.admin.router import router as admin_router
from src.api.auth.router import router as auth_router
from src.api.clinical.router import router as clinical_router
from src.api.health.router import router as health_router
from src.api.users.router import router as users_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(clinical_router)
router.include_router(admin_router)
