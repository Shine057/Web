from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(BaseModel):
    id: UUID
    email: Optional[str]
    phone: Optional[str]
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    login: str = Field(..., description="Email или телефон")
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)