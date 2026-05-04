from fastapi import FastAPI
from app.routers.item_router import router as item_router
from app.db import engine, Base
from app.models.item import Item  # обязательно, чтобы модель зарегистрировалась в Base.metadata

# Таблицы создаются теперь только через миграции Alembic.
# Вызов Base.metadata.create_all() удалён!

app = FastAPI(title="Web App with PostgreSQL")
app.include_router(item_router)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI with PostgreSQL!"}