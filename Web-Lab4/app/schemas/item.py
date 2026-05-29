from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Название элемента", example="Мой товар")
    description: Optional[str] = Field(None, description="Описание", example="Подробное описание товара")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Новое название", example="Обновлённый товар")
    description: Optional[str] = Field(None, description="Новое описание", example="Новое описание")

class ItemResponse(ItemBase):
    id: UUID = Field(..., description="Идентификатор элемента")
    created_at: Optional[datetime] = Field(None, description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")

    model_config = ConfigDict(from_attributes=True)

class PaginatedItems(BaseModel):
    data: List[ItemResponse] = Field(..., description="Список элементов")
    meta: dict = Field(..., description="Метаданные пагинации", example={"total": 10, "page": 1, "limit": 10, "totalPages": 1})