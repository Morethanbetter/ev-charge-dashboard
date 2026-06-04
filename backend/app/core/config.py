from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/dashboard.db"
    secret_key: str = "your-secret-key-change-in-production-abc123xyz"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    upload_dir: str = "/app/uploads"
    dedup_dir: str = "/app/dedup_data"
    max_file_size: int = 52428800

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
