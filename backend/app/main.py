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
    """Return dashboard data aggregated from the uploaded_files table."""
    try:
        async with async_session() as db:
            from app.models.uploaded_file import UploadedFile
            from sqlalchemy import func, select, cast, String, extract
            from collections import defaultdict
            import os

            # Get all files
            result = await db.execute(select(UploadedFile))
            files = result.scalars().all()
            total_uploads = len(files)

            # Total data volume
            total_bytes = sum((f.file_size or 0) for f in files)
            if total_bytes >= 1024 * 1024 * 1024:
                total_data_volume = f"{total_bytes / (1024**3):.1f} GB"
            elif total_bytes >= 1024 * 1024:
                total_data_volume = f"{total_bytes / (1024**2):.1f} MB"
            elif total_bytes >= 1024:
                total_data_volume = f"{total_bytes / 1024:.1f} KB"
            else:
                total_data_volume = f"{total_bytes} B"

            # Dedup files count
            dedup_files = sum(1 for f in files if f.dedup_status == "completed")

            # Active users (distinct user_ids)
            active_users = len(set(f.user_id for f in files)) if files else 1

            # Upload trend & daily uploads: group by date
            daily_counts = defaultdict(int)
            daily_sizes = defaultdict(int)
            for f in files:
                if f.created_at:
                    date_str = f.created_at.strftime("%Y-%m-%d")
                    daily_counts[date_str] += 1
                    daily_sizes[date_str] += (f.file_size or 0)

            sorted_dates = sorted(daily_counts.keys())
            upload_trend = [{"date": d, "value": daily_counts[d]} for d in sorted_dates]
            data_volume_trend = [{"date": d, "value": round(daily_sizes[d] / (1024 * 1024), 1)} for d in sorted_dates]
            daily_uploads = upload_trend  # same data

            # File type distribution
            type_counts = defaultdict(int)
            for f in files:
                ext = os.path.splitext(f.filename)[1].lower() if f.filename else ""
                if ext in (".csv",):
                    type_counts["CSV"] += 1
                elif ext in (".json",):
                    type_counts["JSON"] += 1
                elif ext in (".xlsx", ".xls"):
                    type_counts["Excel"] += 1
                else:
                    type_counts["其他"] += 1
            file_type_distribution = [{"name": k, "value": v} for k, v in type_counts.items()]

            # Data quality radar (derive from actual data)
            total_rows_all = sum((f.row_count or 0) for f in files)
            unique_rows_all = sum((f.unique_rows or 0) for f in files)
            dup_rows_all = sum((f.duplicate_rows or 0) for f in files)
            completed_count = sum(1 for f in files if f.status == "completed")
            dedup_completed = sum(1 for f in files if f.dedup_status == "completed")

            completeness = round((completed_count / total_uploads * 100) if total_uploads > 0 else 0)
            accuracy = round((unique_rows_all / total_rows_all * 100) if total_rows_all > 0 else 0)
            consistency = round((dedup_completed / total_uploads * 100) if total_uploads > 0 else 0)
            # Timeliness: files uploaded in last 7 days
            from datetime import datetime, timedelta, timezone
            now = datetime.now(timezone.utc)
            week_ago = now - timedelta(days=7)
            recent = sum(1 for f in files if f.created_at and f.created_at.replace(tzinfo=timezone.utc) >= week_ago)
            timeliness = round((recent / total_uploads * 100) if total_uploads > 0 else 0)
            uniqueness = round((unique_rows_all / total_rows_all * 100) if total_rows_all > 0 else 0)

            data_quality = [
                {"indicator": "完整性", "value": completeness},
                {"indicator": "准确性", "value": accuracy},
                {"indicator": "一致性", "value": consistency},
                {"indicator": "时效性", "value": timeliness},
                {"indicator": "唯一性", "value": uniqueness},
            ]

            # Upload activity heatmap: group by date + hour
            activity = defaultdict(int)
            for f in files:
                if f.created_at:
                    date_str = f.created_at.strftime("%Y-%m-%d")
                    hour = f.created_at.hour
                    activity[(date_str, hour)] += 1
            upload_activity = [
                {"date": d, "hour": h, "value": activity.get((d, h), 0)}
                for d in sorted(set(d for d, _ in activity.keys()))
                for h in range(24)
            ]

            # Dedup rate
            dedup_rate = round((dup_rows_all / total_rows_all * 100) if total_rows_all > 0 else 0, 1)

            return {
                "code": 0, "message": "ok",
                "data": {
                    "stats": {
                        "total_uploads": total_uploads,
                        "total_data_volume": total_data_volume,
                        "dedup_files": dedup_files,
                        "active_users": max(active_users, 1),
                    },
                    "upload_trend": upload_trend,
                    "data_volume_trend": data_volume_trend,
                    "file_type_distribution": file_type_distribution,
                    "daily_uploads": daily_uploads,
                    "data_quality": data_quality,
                    "upload_activity": upload_activity,
                    "dedup_rate": dedup_rate,
                },
            }
    except Exception as e:
        logger.error(f"Dashboard query failed: {e}")
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
