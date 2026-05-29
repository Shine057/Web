from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.item import ItemResponse, ItemCreate, ItemUpdate, PaginatedItems
from app.services.item_service import ItemService
from app.dependencies import get_current_user

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/",
            response_model=PaginatedItems,
            summary="Получить список своих элементов",
            tags=["Items"],
            responses={
                200: {"description": "Список элементов с пагинацией"},
                401: {"description": "Не авторизован"}
            })
def get_items(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
              db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ItemService(db)
    return service.get_all(str(current_user.id), page, limit)

@router.get("/{item_id}",
            response_model=ItemResponse,
            summary="Получить элемент по ID",
            tags=["Items"],
            responses={
                200: {"description": "Найденный элемент"},
                401: {"description": "Не авторизован"},
                404: {"description": "Элемент не найден"}
            })
def get_item(item_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ItemService(db)
    item = service.get(item_id, user_id=str(current_user.id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/",
             response_model=ItemResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Создать новый элемент",
             tags=["Items"],
             responses={
                 201: {"description": "Элемент создан"},
                 400: {"description": "Ошибка валидации"},
                 401: {"description": "Не авторизован"}
             })
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ItemService(db)
    return service.create(item, user_id=str(current_user.id))

@router.put("/{item_id}",
            response_model=ItemResponse,
            summary="Полное обновление элемента",
            tags=["Items"],
            responses={
                200: {"description": "Элемент обновлён"},
                400: {"description": "Ошибка валидации"},
                401: {"description": "Не авторизован"},
                404: {"description": "Элемент не найден"}
            })
def update_item(item_id: str, item_update: ItemUpdate, db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    service = ItemService(db)
    updated = service.update(item_id, item_update, user_id=str(current_user.id))
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.patch("/{item_id}",
              response_model=ItemResponse,
              summary="Частичное обновление элемента",
              tags=["Items"],
              responses={
                  200: {"description": "Элемент обновлён"},
                  400: {"description": "Ошибка валидации"},
                  401: {"description": "Не авторизован"},
                  404: {"description": "Элемент не найден"}
              })
def partial_update_item(item_id: str, item_update: ItemUpdate, db: Session = Depends(get_db),
                        current_user = Depends(get_current_user)):
    service = ItemService(db)
    updated = service.update(item_id, item_update, user_id=str(current_user.id))
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.delete("/{item_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Удалить элемент (Soft Delete)",
               tags=["Items"],
               responses={
                   204: {"description": "Элемент удалён"},
                   401: {"description": "Не авторизован"},
                   404: {"description": "Элемент не найден"}
               })
def delete_item(item_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ItemService(db)
    deleted = service.delete(item_id, user_id=str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")