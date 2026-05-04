<<<<<<< Updated upstream
﻿from fastapi import FastAPI
from datetime import date

app = FastAPI()

@app.get("/info")
async def get_info():
    today = date.today()
    next_new_year = date(today.year + 1, 1, 1)
    days_left = (next_new_year - today).days
    return {"days_before_new_year": days_left}
=======
﻿# app/main.py
from fastapi import FastAPI
from app.routers.item_router import router as item_router
from app.db import engine, Base
from app.models.item import Item  # обязательно, чтобы модель была видна в Base.metadata

# ⚠️ create_all убран! Таблицы создаются только через Alembic-миграции.

app = FastAPI(title="Web App with PostgreSQL")
app.include_router(item_router)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI with PostgreSQL!"}
>>>>>>> Stashed changes
