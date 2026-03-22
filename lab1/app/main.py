from fastapi import FastAPI
from datetime import date

app = FastAPI()

@app.get("/info")
async def get_info():
    """
    Возвращает количество дней до наступления Нового года.
    """
    today = date.today()
    next_new_year = date(today.year + 1, 1, 1)
    days_left = (next_new_year - today).days
    return {"days_before_new_year": days_left}