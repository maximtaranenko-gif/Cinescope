from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class MovieModel(BaseModel):
    """Модель фильма для создания/обновления"""
    name: str = Field(min_length=1, max_length=100, description="Название фильма")
    price: int = Field(ge=0, description="Цена фильма (не может быть отрицательной)")
    location: str = Field(min_length=2, max_length=10, description="Локация (MSK, SPB)")
    genreId: int = Field(ge=1, description="ID жанра")
    rating: Optional[int] = Field(None, ge=0, le=10, description="Рейтинг фильма")

    @field_validator("location")
    def validate_location(cls, value: str) -> str:
        allowed = ["MSK", "SPB"]
        if value not in allowed:
            raise ValueError(f"Локация должна быть одной из: {allowed}")
        return value


class MovieResponse(BaseModel):
    """Ответ API при создании/получении фильма"""
    id: int
    name: str
    price: int
    location: str
    genreId: int
    rating: Optional[int] = None
    createdAt: Optional[str] = None

    @field_validator("createdAt")
    def validate_created_at(cls, value: Optional[str]) -> Optional[str]:
        if value:
            try:
                datetime.fromisoformat(value)
            except ValueError:
                raise ValueError("Некорректный формат даты")
        return value