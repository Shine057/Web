from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import db, models

app = FastAPI()

# Создаём таблицы
db.Base.metadata.create_all(bind=db.engine)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}