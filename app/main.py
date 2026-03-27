# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# ---------- Настройка FastAPI ----------
app = FastAPI(title="Web App with PostgreSQL")

# ---------- Настройка базы данных ----------
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "web_db")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres_db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---------- Модель SQLAlchemy ----------
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# ---------- Pydantic-схема ----------
class ItemSchema(BaseModel):
    name: str
    description: str | None = None

# ---------- Роуты ----------
@app.get("/")
def root():
    return {"message": "Hello, FastAPI with PostgreSQL!"}

@app.get("/items")
def read_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return items

@app.post("/items")
def create_item(item: ItemSchema):
    db = SessionLocal()
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item