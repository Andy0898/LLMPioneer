from fastapi import APIRouter
from .auth_controller import router as auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/login", tags=["login"]) 
router.include_router(auth_router, prefix="/logout", tags=["logout"])
router.include_router(auth_router, prefix="/password", tags=["password change"])
