from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserResponse(UserBase):
    id: int
    role_id: int
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True