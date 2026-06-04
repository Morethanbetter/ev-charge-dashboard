from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, Base, async_session
from app.api import auth, files
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select


async def init_admin_user():
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none() is None:
            admin = User(username="admin", password=get_password_hash("admin123"))
            db.add(admin)
            await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_admin_user()
    yield


app = FastAPI(title="\u53ef\u89c6\u5316\u6570\u636e\u76d1\u63a7\u9762\u677f API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["\u8ba4\u8bc1"])
app.include_router(files.router, prefix="/api/v1/files", tags=["\u6587\u4ef6"])


@app.get("/api/v1/health")
async def health_check():
    return {"code": 0, "message": "ok", "data": {"status": "healthy"}}
