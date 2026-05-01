from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, Literal, List
from datetime import datetime


class MovieModel(BaseModel):
    """Модель фильма для создания/обновления"""
    name: str = Field(min_length=1, max_length=100, description="Название фильма")
    price: int = Field(ge=0, description="Цена фильма (не может быть отрицательной)")
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    location: str = Field(min_length=2, max_length=10, description="Локация (MSK, SPB)")
    genreId: int = Field(ge=1, description="ID жанра")
    rating: Optional[int] = Field(None, ge=0, le=10, description="Рейтинг фильма")
    published: Optional[bool] = None


    @field_validator("location")
    def validate_location(cls, value: str) -> str:
        allowed = ["MSK", "SPB"]
        if value not in allowed:
            raise ValueError(f"Локация должна быть одной из: {allowed}")
        return value

class MovieUpdate(BaseModel):
    """Валидация для фильмов, которые были обновлены"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название фильма")
    price: Optional[int] = Field(None, ge=0, description="Цена фильма (не может быть отрицательной)")
    location: Optional[str] = Field(None,min_length=2, max_length=10, description="Локация (MSK, SPB)")
    genreId: Optional[int] = Field(None,ge=1, description="ID жанра")
    rating: Optional[int] = Field(None, ge=0, le=10, description="Рейтинг фильма")
    imageUrl: Optional[HttpUrl] = Field(None, description="URL постера фильма")
    published: Optional[bool] = Field(None, description="Опубликован(True, False)")

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

class MovieCreateReview(BaseModel):
    """Валидация отзывов к фильму"""
    rating : int = Field(ge=1, le=5, description="Оценка к отзыву")
    text: str = Field(min_length=5, max_length=40, description="Текст к отзыву ")

class MovieUpdateReview(BaseModel):
    """Валидация редактирования отзыва к фильму"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Оценка к отзыву")
    text: Optional[str] = Field(None, min_length=5, max_length=40, description="Текст к отзыву ")

class MovieResponseReview(BaseModel):
    """Ответ API при создании/получении отзыва"""
    userId: str
    text: str = Field(min_length=5, max_length=40)
    rating: int = Field(ge=1, le=5)
    createdAt: str

class MovieReviewsListResponse(BaseModel):
    """Ответ API при получении списка отзывов"""
    reviews: List[MovieResponseReview]

class MovieCreateGenre(BaseModel):
    """Валидация жанра к фильму"""
    name: str = Field(min_length=3, max_length=12, description="Жанр к фильму")

class MovieResponseGenre(BaseModel):
    """Ответ API при валидации жанра к фильму"""
    id : int
    name: str

class MovieGenreListResponse(BaseModel):
    """Модель списка жанров"""
    genres: List[MovieResponseGenre]

class MovieReceivingPosters(BaseModel):
    """Валидация для афиш фильмов с пагинацией"""
    page : Optional[int] = 1
    pageSize : Optional[int] = 2
    minPrice: Optional[int] = 50
    maxPrice: Optional[int] = 1000
    locations: Optional[str] = "SPB"
    published: Optional[bool] = True
    genreId: Optional[int] = 2
    createdAt: Optional[Literal["asc", "desc"]] = "asc"

class MoviesListResponse(BaseModel):
    """Ответ API при получении списка фильмов (афиш)"""
    movies: List[MovieResponse] = Field(..., description="Список фильмов")
    total: Optional[int] = Field(None, description="Общее количество фильмов")
    page: Optional[int] = Field(None, description="Текущая страница")
    pageSize: Optional[int] = Field(None, description="Размер страницы")