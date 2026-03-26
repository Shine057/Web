from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from sqlalchemy.exc import OperationalError

DATABASE_URL = "postgresql://postgres:postgres@db:5432/mydb"

# Попытка подключения с ожиданием
for i in range(10):
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        engine.connect()
        print("✅ Connected to DB")
        break
    except OperationalError:
        print("⏳ Waiting for DB...")
        time.sleep(2)
else:
    raise Exception("❌ Cannot connect to DB after 10 attempts")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()