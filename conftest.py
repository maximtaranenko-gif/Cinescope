import random
import uuid

from faker import Faker
import pytest
import requests
from constants import BASE_URL, REGISTER_ENDPOINT, ADMIN_CREDS
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator, generate_movie

faker = Faker()


@pytest.fixture(scope="session")
def session():
    """
        Фикстура для создания HTTP-сессии.
        """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """Фикстура для создания экземпляра APiMANAGER"""
    return ApiManager(session)

@pytest.fixture(scope="function")
def test_user()->dict:

    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": faker.email(),
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }


@pytest.fixture(scope="function")
def registered_user(auth_requester, test_user) ->dict:
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = auth_requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

@pytest.fixture(scope="session")
def auth_requester()->CustomRequester:
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture
def movie_data()-> dict:
    """Фикстура для генерации фильма(Валидные данные)"""
    return generate_movie()


@pytest.fixture
def multiple_movies()-> list:
    """Фикстура для генераации нескольких фильмов(Валидные данные)"""
    return [generate_movie() for i in range(3)]


@pytest.fixture
def movie_data_incorrect()->dict:
    """Фикстура для генерации фильма(Невалидные данные)"""
    return generate_movie(
        price_range=(-100, 300000),
        locations=["SPB", "MSK", "TSK", "NSK"],
        genre_range= (10, 100)
    )
@pytest.fixture
def created_movie(api_manager, movie_data:dict):
    """Фикстура для создания фильма"""
    api_manager.auth_api.authenticate(ADMIN_CREDS)
    response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
    movie = response.json()

    yield movie

    api_manager.movie_api.delete_movie(movie["id"], expected_status=200)