# app/schemas/item.py
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ItemResponse(ItemBase):
    id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

class PaginatedItems(BaseModel):
    data: List[ItemResponse]
    meta: dict