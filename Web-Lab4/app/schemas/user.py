from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email пользователя", example="user@example.com")
    phone: Optional[str] = Field(None, description="Номер телефона", example="+79991234567")
    password: Optional[str] = Field(None, min_length=8, description="Пароль (мин. 8 символов)", example="secret123")

class UserResponse(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор")
    email: Optional[str] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Телефон")
    created_at: Optional[datetime] = Field(None, description="Дата регистрации")

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    login: str = Field(..., description="Email или телефон", example="user@example.com")
    password: str = Field(..., description="Пароль", example="secret123")

class ForgotPassword(BaseModel):
    email: EmailStr = Field(..., description="Email для восстановления", example="user@example.com")

class ResetPassword(BaseModel):
    token: str = Field(..., description="Токен сброса")
    new_password: str = Field(..., min_length=8, description="Новый пароль", example="newsecret123")