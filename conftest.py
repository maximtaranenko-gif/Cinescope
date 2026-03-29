import random
import uuid


from faker import Faker
import pytest
import requests
from constants import REGISTER_ENDPOINT, ADMIN_CREDS, AUTH_URL, Roles
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager
from entities.user import User
from resources.user_creds import SuperAdminCreds
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

@pytest.fixture
def user_session():
    """Фикстура для создания сессии юзеров"""
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user


@pytest.fixture
def admin(user_session, super_admin, creation_user_data):
    new_session = user_session()

    admin_data = creation_user_data.copy()
    admin_data['roles'] = [Roles.USER.value,Roles.ADMIN.value]

    admin = User(
        admin_data['email'],
        admin_data['password'],
        [Roles.USER.value],
        new_session)

    # Создаём пользователя
    create_response = super_admin.api.user_api.create_user(admin_data, expected_status=201)
    user_id = create_response.json()['id']

    # Обновляем роль (только нужные поля, динамически)
    fields_to_update = ["roles", "verified", "banned"]
    update_data = {key: admin_data[key] for key in fields_to_update}

    super_admin.api.user_api.update_role_user_admin(user_id, update_data, expected_status=200)

    # Авторизуемся
    admin.api.auth_api.authenticate(admin.creds)

    return admin


@pytest.fixture
def super_admin(user_session, api_manager):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )

    auth_response = super_admin.api.auth_api.authenticate(super_admin.creds)
    user_id = auth_response["user"]["id"]
    super_admin.id = user_id
    return super_admin

@pytest.fixture(scope="function")
def test_user()->dict:

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
        "roles": [Roles.USER.value]
    }

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data

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
    return CustomRequester(session=session, base_url=AUTH_URL)

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