from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.item import ItemResponse, ItemCreate, ItemUpdate, PaginatedItems
from app.services.item_service import ItemService
from app.dependencies import get_current_user

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=PaginatedItems)
def get_items(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
              db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ItemService(db)
    return service.get_all(str(current_user.id), page, limit)

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ItemService(db)
    item = service.get(item_id, user_id=str(current_user.id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ItemService(db)
    return service.create(item, user_id=str(current_user.id))

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: str, item_update: ItemUpdate, db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    service = ItemService(db)
    updated = service.update(item_id, item_update, user_id=str(current_user.id))
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.patch("/{item_id}", response_model=ItemResponse)
def partial_update_item(item_id: str, item_update: ItemUpdate, db: Session = Depends(get_db),
                        current_user = Depends(get_current_user)):
    service = ItemService(db)
    updated = service.update(item_id, item_update, user_id=str(current_user.id))
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ItemService(db)
    deleted = service.delete(item_id, user_id=str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")