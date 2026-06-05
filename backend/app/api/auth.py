from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_current_user, get_password_hash
from app.core.config import get_settings
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.common import success_response

router = APIRouter()
settings = get_settings()


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.username == req.username))
        user = result.scalar_one_or_none()
    except Exception as e:
        import logging
        logging.error(f"Database error during login: {e}")
        raise HTTPException(status_code=500, detail={"code": 2001, "message": "数据库连接失败，请检查 DATABASE_URL 配置", "data": None})
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail={"code": 1001, "message": "用户名或密码错误", "data": None})
    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return success_response(
        data={
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {"id": user.id, "username": user.username, "created_at": user.created_at.isoformat()},
        },
        message="登录成功",
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return success_response(
        data={"id": current_user.id, "username": current_user.username, "created_at": current_user.created_at.isoformat()}
    )


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    token = create_access_token(data={"sub": str(current_user.id), "username": current_user.username})
    return success_response(
        data={"access_token": token, "token_type": "bearer", "expires_in": settings.access_token_expire_minutes * 60},
        message="Token 已刷新",
    )
