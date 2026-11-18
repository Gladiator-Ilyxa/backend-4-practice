from pydantic import BaseModel, Field
from typing import Optional

class ServiceCreate(BaseModel):
    categoryId: int = Field(..., description="Идентификатор категории услуги")
    title: str = Field(..., min_length=1, max_length=100, description="Название услуги")
    desc: str = Field(..., min_length=1, max_length=100, description="Описание услуги")
    duration: int = Field(..., ge=30, le=180, description="Продолжительность в минутах (30-180)")
    price: float = Field(..., gt=0, description="Стоимость услуги (должна быть больше 0)")