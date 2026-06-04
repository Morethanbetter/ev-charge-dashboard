from pydantic import BaseModel, Field
from datetime import datetime


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class UserInfo(BaseModel):
    id: int
    username: str
    created_at: datetime
    class Config:
        from_attributes = True
