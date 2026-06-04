import asyncio
from app.core.database import engine, Base, async_session
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.core.security import get_password_hash
from sqlalchemy import select


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none() is None:
            admin = User(username="admin", password=get_password_hash("admin123"))
            db.add(admin)
            await db.commit()
            print("Default admin user created (admin / admin123)")
        else:
            print("Admin user already exists")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init())
