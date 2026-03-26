# app/services/item_service.py
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from math import ceil

class ItemService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, item_id):
        return self.db.query(Item).filter(Item.id == item_id, Item.is_deleted == False).first()

    def get_all(self, page=1, limit=10):
        query = self.db.query(Item).filter(Item.is_deleted == False)
        total = query.count()
        items = query.offset((page - 1) * limit).limit(limit).all()
        return {
            "data": items,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": ceil(total / limit)
            }
        }

    def create(self, item: ItemCreate):
        db_item = Item(**item.dict())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update(self, item_id, item_update: ItemUpdate):
        item = self.get(item_id)
        if not item:
            return None
        for key, value in item_update.dict(exclude_unset=True).items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item_id):
        item = self.get(item_id)
        if not item:
            return None
        item.is_deleted = True
        self.db.commit()
        return item