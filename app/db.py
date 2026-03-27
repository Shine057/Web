import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 📌 Получаем переменные окружения (из docker-compose)
DB_USER = os.getenv("DB_USER", "student")
DB_PASSWORD = os.getenv("DB_PASSWORD", "student")
DB_HOST = os.getenv("DB_HOST", "postgres")  # ВАЖНО: postgres для Docker
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "lab2")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ⏳ Ожидание запуска БД
for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        connection.close()
        print("✅ Connected to DB!")
        break
    except Exception:
        print("⏳ Waiting for DB...")
        time.sleep(2)
else:
    raise Exception("❌ Cannot connect to DB after 10 attempts")

# 📦 ORM
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()