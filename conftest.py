import random

from faker import Faker
import pytest
import requests
from constants import BASE_URL, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator

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

@pytest.fixture(scope="session")
def test_user():

    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }


@pytest.fixture(scope="function")
def registered_user(auth_requester, test_user):
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
def auth_requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture
def movie_data():
    """Фикстура для создания рандомного фильма(валидные данные)"""
    data = {
        "name": faker.sentence(),
        "imageUrl": "https://allwebs.ru/images/2026/03/14/5a789b9ac9178ace2c2e1c3b2564e64f.jpg",
        "price": faker.random_int(500, 3000),
        "description": faker.text(),
        "location": random.choice(["MSK", "SPB"]),
        "published": random.choice([True, False]),
        "genreId": random.randint(1, 20),
    }
    return data

@pytest.fixture
def multiple_movies():
    """Фикстура с тремя разными фильмами"""
    movies = []
    for i in range(3):
        movie = {
            "name": faker.sentence(),
            "imageUrl": "https://allwebs.ru/images/2026/03/14/5a789b9ac9178ace2c2e1c3b2564e64f.jpg",
            "price": faker.random_int(10, 30000),
            "description": faker.text(),
            "location": random.choice(["MSK", "SPB"]),
            "published": random.choice([True, False]),
            "genreId": random.randint(1, 5),
        }
        movies.append(movie)
    return movies

@pytest.fixture
def movie_data_incorrect():
    """Фикстура для создания рандомного фильма(невалидные данные)"""
    data = {
        "name": faker.sentence(),
        "imageUrl": "https://allwebs.ru/images/2026/03/14/5a789b9ac9178ace2c2e1c3b2564e64f.jpg",
        "price": faker.random_int(500, 300000),
        "description": faker.text(),
        "location": random.choice(["MSK", "SPB"]),
        "published": random.choice([True, False]),
        "genreId": random.randint(1, 100),
    }
    return data




