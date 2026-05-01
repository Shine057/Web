from fastapi import FastAPI
from app.db import engine, Base
from app.routers.item_router import router as item_router
from app.routers.auth_router import router as auth_router

app = FastAPI(title="Lab3 - Auth & CRUD")

# Автосоздание таблиц (для простоты; в проде использовать миграции)
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(item_router)

@app.get("/")
def root():
    return {"message": "Lab3 API is running"}