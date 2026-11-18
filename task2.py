from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import sqlite3
from datetime import datetime

def get_db():
    conn = sqlite3.connect("services.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoryId INTEGER NOT NULL,
            title TEXT NOT NULL,
            "desc" TEXT NOT NULL,
            duration INTEGER NOT NULL,
            price REAL NOT NULL,
            createdAt TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, выполняемый при запуске приложения (startup)
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

class ServiceCreate(BaseModel):
    categoryId: int = Field(..., description="Идентификатор категории услуги")
    title: str = Field(..., min_length=1, max_length=100, description="Название услуги")
    desc: str = Field(..., min_length=1, max_length=100, description="Описание услуги")
    duration: int = Field(..., ge=30, le=180, description="Продолжительность в минутах (30-180)")
    price: float = Field(..., gt=0, description="Стоимость услуги (должна быть больше 0)")

# Модель ответа
class ServiceResponse(BaseModel):
    id: int
    categoryId: int
    title: str
    desc: str
    duration: int
    price: float
    createdAt: str

@app.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(service: ServiceCreate):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO services (categoryId, title, "desc", duration, price, createdAt)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                service.categoryId,
                service.title,
                service.desc,
                service.duration,
                service.price,
                datetime.now().isoformat()
            )
        )
        conn.commit()
        
        service_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        created_service = cursor.fetchone()
        
        return {
            "id": created_service["id"],
            "categoryId": created_service["categoryId"],
            "title": created_service["title"],
            "desc": created_service["desc"],
            "duration": created_service["duration"],
            "price": created_service["price"],
            "createdAt": created_service["createdAt"]
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()