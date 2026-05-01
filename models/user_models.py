from typing import Optional
import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator
from constants import Roles

class UserModel(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(..., min_length=1, max_length=20, description="passwordRepeat должен полностью совпадать с полем password")
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        # Проверяем, совпадение паролей
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value


class LoginRequest(BaseModel):
    """Модель для авторизации пользователя"""
    email: str = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=4, description="Пароль пользователя")

class LoginResponse(BaseModel):
    """Ответ при авторизации"""
    accessToken: str = Field(..., description="JWT токен доступа")
    refreshToken: Optional[str] = Field(None, description="Refresh токен")
    expiresIn: int = Field(..., description="Время жизни токена в секундах")

class TestUser(BaseModel):
    """Модель пользователя для тестов (авторизованный)"""
    email: str
    password: str
    roles: List[Roles]
    api: "ApiManager"
    id: Optional[str] = None

    @property
    def creds(self) -> LoginRequest:
        """Данные для авторизации"""
        return LoginRequest(email=self.email, password=self.password)

class UserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: bool
    roles: List[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

class UserRoleUpdateModel(BaseModel):
    """Модель для ролей пользователя"""
    roles: List[Roles]

class UserListFilters(BaseModel):
    """Модель для валидации списка юзеров с пагинацией"""
    page: Optional[int] = 1
    pageSize: Optional[int] = 10
    roles: Optional[list[Roles]] = [Roles.USER]
    createdAt: Optional[str] = "ASC"

class UsersListResponse(BaseModel):
    """Модель ответа при получении списка пользователей"""
    users: List[UserResponse]
    count: int
    page: int
    pageSize: int
    pageCount: int

class UserUpdateData(BaseModel):
    """Модель для валидации изменения данных юзера"""
    roles: Optional[list[Roles]] = None
    verified: Optional[bool] = None
    banned: Optional[bool] = None

class UserLocator(BaseModel):
    """Модель для поиска пользователя"""
    id: Optional[str] = None
    email: Optional[str] = None
    fullName: Optional[str] = None

class UsersListLocatorResponse(BaseModel):
    """Ответ на GET /user с пагинацией"""
    users: List[UserResponse]
    page: int
    pageCount: int