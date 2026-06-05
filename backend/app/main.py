import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from app.core.database import engine, Base, async_session
from app.api import auth, files
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

logger = logging.getLogger(__name__)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


async def init_admin_user():
    try:
        async with async_session() as db:
            result = await db.execute(select(User).where(User.username == "admin"))
            if result.scalar_one_or_none() is None:
                admin = User(username="admin", password=get_password_hash("admin123"))
                db.add(admin)
                await db.commit()
                logger.info("Default admin user created")
    except Exception as e:
        logger.warning(f"Could not init admin user: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await init_admin_user()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("App starting without database - some features will be unavailable")
    yield


app = FastAPI(title="\u53ef\u89c6\u5316\u6570\u636e\u76d1\u63a7\u9762\u677f API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["\u8ba4\u8bc1"])
app.include_router(files.router, prefix="/api/v1/files", tags=["\u6587\u4ef6"])




@app.post("/api/v1/debug/init-admin")
async def force_init_admin():
    try:
        async with async_session() as db:
            result = await db.execute(select(User).where(User.username == "admin"))
            if result.scalar_one_or_none() is None:
                admin = User(username="admin", password=get_password_hash("admin123"))
                db.add(admin)
                await db.commit()
                return {"code": 0, "message": "Admin user created", "data": {"username": "admin", "password": "admin123"}}
            else:
                return {"code": 0, "message": "Admin user already exists", "data": None}
    except Exception as e:
        return {"code": 1, "message": str(e), "data": None}

@app.get("/api/v1/debug/admin")
async def debug_admin():
    try:
        async with async_session() as db:
            result = await db.execute(select(User).where(User.username == "admin"))
            user = result.scalar_one_or_none()
            if user:
                return {"code": 0, "message": "ok", "data": {"exists": True, "id": user.id, "username": user.username}}
            else:
                return {"code": 0, "message": "ok", "data": {"exists": False, "hint": "Admin user not found. Try restarting the app to trigger initialization."}}
    except Exception as e:
        return {"code": 1, "message": str(e), "data": None}

@app.get("/api/v1/health")
async def health_check():
    db_status = "unknown"
    try:
        async with async_session() as db:
            await db.execute(select(User).limit(1))
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:100]}"
    return {"code": 0, "message": "ok", "data": {"status": "healthy", "database": db_status}}



@app.get("/api/v1/dashboard")
async def get_dashboard_data():
    """Return dashboard data. Falls back to mock data if no real data exists."""
    try:
        async with async_session() as db:
            from app.models.uploaded_file import UploadedFile
            from sqlalchemy import func, select
            # Get real stats from DB
            count_result = await db.execute(select(func.count(UploadedFile.id)))
            total_uploads = count_result.scalar() or 0
            return {
                "code": 0, "message": "ok",
                "data": {
                    "stats": {
                        "total_uploads": total_uploads,
                        "total_data_volume": "0 MB",
                        "dedup_files": 0,
                        "active_users": 1,
                    },
                    "upload_trend": [],
                    "data_volume_trend": [],
                    "file_type_distribution": [],
                    "daily_uploads": [],
                    "data_quality": [],
                    "upload_activity": [],
                    "dedup_rate": 0,
                },
            }
    except Exception:
        return {
            "code": 0, "message": "ok",
            "data": {
                "stats": {"total_uploads": 0, "total_data_volume": "0 MB", "dedup_files": 0, "active_users": 1},
                "upload_trend": [], "data_volume_trend": [], "file_type_distribution": [],
                "daily_uploads": [], "data_quality": [], "upload_activity": [], "dedup_rate": 0,
            },
        }

# Serve frontend static files (must be AFTER API routes)
if os.path.isdir(FRONTEND_DIR):
    assets_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
