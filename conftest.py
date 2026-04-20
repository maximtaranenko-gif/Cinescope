from faker import Faker
import pytest
import requests
from constants import REGISTER_ENDPOINT, AUTH_URL, Roles
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager
from entities.user import User
from models.movies_models import MovieResponse, MovieModel
from models.user_models import UserModel, RegisterUserResponse
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator, generate_movie
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
faker = Faker()


@pytest.fixture(scope="session")
def session():
    """
        Фикстура для создания HTTP-сессии.
        """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="module")
def db_session()->Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """Фикстура для создания экземпляра APiMANAGER"""
    return ApiManager(session)

@pytest.fixture(scope="function")
def db_helper(db_session)->DBHelper:
    """Фикстура для создания экземпляра хелпера"""
    db_helper = DBHelper(db_session)
    return db_helper

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
def unauthorized_user(user_session, super_admin, creation_user_data):
    """
    Фикстура для неавторизованного пользователя (есть аккаунт, но нет токена)
    """
    new_session = user_session()

    unauthorized_data = creation_user_data.model_copy()
    unauthorized_data.email = DataGenerator.generate_random_email()
    unauthorized_data.password = DataGenerator.generate_random_password()

    response = super_admin.api.user_api.create_user(unauthorized_data, expected_status=201)
    user_id = response.json()["id"]


    unauthorized = User(
        unauthorized_data.email,
        unauthorized_data.password,
        [Roles.USER],
        new_session
    )

    yield unauthorized

    # Чистим пользователя после теста
    super_admin.api.user_api.delete_user(user_id, expected_status=200)

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    response = super_admin.api.user_api.create_user(creation_user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER],
        new_session)
    common_user.id = user_id

    # Cleanup
    common_user.api.auth_api.authenticate(common_user.creds)
    yield common_user
    super_admin.api.auth_api.delete_user(user_id, expected_status=200)


@pytest.fixture
def admin(user_session, super_admin, creation_user_data, api_manager):
    new_session = user_session()

    admin_data = creation_user_data.model_copy()
    admin_data.roles = [Roles.USER, Roles.ADMIN]
    admin_data.email = DataGenerator.generate_random_email()

    admin = User(
        admin_data.email,
        admin_data.password,
        [Roles.USER],
        new_session)

    # Создаём пользователя
    create_response = super_admin.api.user_api.create_user(admin_data, expected_status=201)
    user_id = create_response.json()['id']

    # Обновляем роль
    fields_to_update = ["roles", "verified", "banned"]
    update_data = {key:getattr( admin_data,key) for key in fields_to_update}
    super_admin.api.user_api.update_role_user_admin(user_id, update_data, expected_status=200)
    # Авторизуемся
    admin.api.auth_api.authenticate(admin.creds)
    # Cleanup
    yield admin
    super_admin.api.auth_api.delete_user(user_id, expected_status=200)

@pytest.fixture(scope="function")
def super_admin(api_manager):
    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN],
        api_manager
    )

    auth_response = super_admin.api.auth_api.authenticate(super_admin.creds)
    user_id = auth_response["user"]["id"]
    super_admin.id = user_id
    return super_admin

@pytest.fixture(scope="function")
def test_user()->UserModel:

    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return UserModel(
        email = random_email,
        fullName=random_name,
        password = random_password,
        passwordRepeat=random_password,
        roles= [Roles.USER.value]
    )

@pytest.fixture(scope="function")
def creation_user_data(test_user)->UserModel:
    """
    Фикстура для обновления данных юзера
    """
    updated_user = test_user.model_copy()
    updated_user.verified = True
    updated_user.banned = False
    return updated_user

@pytest.fixture(scope='function')
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)

@pytest.fixture
def created_test_movie(db_helper, movie_data):
    """
    Создает тестовый фильм в БД и удаляет после теста
    """
    movie = db_helper.create_test_movie(movie_data)
    yield movie
    if db_helper.movie_exists_by_id(movie.id):
        db_helper.delete_movie(movie)

@pytest.fixture(scope="function")
def registered_user(auth_requester, test_user)->RegisterUserResponse:
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = auth_requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    return RegisterUserResponse(**response.json())

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
def created_movie(api_manager:ApiManager,super_admin, movie_data:dict)->MovieModel:
    """Фикстура для создания фильма"""
    response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
    movie_dict = response.json()
    movie = MovieResponse(**movie_dict)

    yield movie

    super_admin.api.movie_api.delete_movie(movie.id, expected_status=200)