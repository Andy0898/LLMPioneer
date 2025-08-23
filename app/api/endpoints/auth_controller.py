# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.user import Token, PasswordUpdate
from app.services.auth import AuthService
from app.db.models.user import UserModel

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """统一登录接口"""
    auth_service = AuthService(db)
    result = await auth_service.authenticate(form_data.username, form_data.password)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result

@router.post("/logout")
async def logout(current_user: UserModel = Depends(get_current_user)):
    """统一登出接口"""
    return {"message": "Successfully logged out"}

@router.post("/password", response_model=dict)
async def change_password(
    password_data: PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """修改密码"""
    auth_service = AuthService(db)
    if not await auth_service.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password"
        )
    return {"message": "Password updated successfully"}