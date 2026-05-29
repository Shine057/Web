# app/main.py
import os
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.db import engine, Base
from app.routers.item_router import router as item_router
from app.routers.auth_router import router as auth_router

# Режим приложения из .env (по умолчанию development)
APP_ENV = os.getenv("APP_ENV", "development")

# Создаём приложение с условным отключением документации
app = FastAPI(
    title="Lab Project API",
    description="API для лабораторных работ №2-№4: управление элементами и аутентификация.",
    version="1.0.0",
    # В production-режиме отключаем все URL документации
    docs_url="/api/docs" if APP_ENV != "production" else None,
    redoc_url="/api/redoc" if APP_ENV != "production" else None,
    openapi_url="/api/openapi.json" if APP_ENV != "production" else None,
)

# Автосоздание таблиц (для разработки)
Base.metadata.create_all(bind=engine)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(item_router)

@app.get("/")
def root():
    return {"APP_ENV": APP_ENV}

# Настройка схемы безопасности (Cookie Auth) для Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "cookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "JWT Access Token (передаётся автоматически через HttpOnly cookie)"
        }
    }
    # Глобально требовать эту схему для всех эндпоинтов
    openapi_schema["security"] = [{"cookieAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi