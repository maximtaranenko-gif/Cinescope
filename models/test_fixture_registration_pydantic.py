from pydantic import BaseModel, EmailStr, Field, field_validator
from venv import logger
from typing import List, Optional
from constants import Roles

# Модель проверки регистрации данных
class RegistrationUserData(BaseModel):
    email: EmailStr
    fullName: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=6, max_length=18)
    passwordRepeat: str
    roles: List[Roles] = [Roles.USER]
    banned: Optional[bool] = Field(default=False, description="Забанен ли пользователь")
    verified: Optional[bool] = Field(default=False, description="Верифицирован ли пользователь")

    @field_validator('email')
    @classmethod
    def email_match(cls, value:str)->str:
        if '@' not in value:
            raise ValueError('Email должен содержать символ @')
        return value

    @field_validator('password')
    @classmethod
    def password_match(cls, value:str)->str:
        if len(value) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        return value

    @field_validator('passwordRepeat')
    @classmethod
    def passwords_match(cls, value:str, info)->str:
        if 'password' in info.data and value != info.data['password']:
            raise ValueError('Пароли не совпадают')
        return value

class TestRegistrationUserData:
    def test_registration_user_data_fixture(self, test_user):
        user_data = RegistrationUserData(**test_user.model_dump())
        assert user_data.email == test_user.email
        assert user_data.password == test_user.password
        assert user_data.password == test_user.passwordRepeat
        assert user_data.roles[0] == Roles.USER
        assert user_data.banned is None or user_data.banned is False
        assert user_data.verified is None or user_data.verified is False
        json_data = user_data.model_dump_json(exclude_unset=True)
        logger.info(json_data)

    def test_creation_user_data_fixture(self, creation_user_data):
        """Проверка creation_user_data через Pydantic"""
        user_data = RegistrationUserData(**creation_user_data.model_dump())
        assert user_data.email == creation_user_data.email
        assert user_data.password == creation_user_data.password
        assert user_data.password == creation_user_data.passwordRepeat
        assert user_data.roles[0] == Roles.USER