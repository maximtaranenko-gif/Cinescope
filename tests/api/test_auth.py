import allure

from conftest import api_manager
from api.api_manager import ApiManager
import requests

from models.movies_models import MovieModel
from models.user_models import UserLocator
from entities.user import User
from utils.data_generator import DataGenerator
from constants import Roles
from resources.user_creds import SuperAdminCreds
import uuid
import pytest
from models.user_models import UserResponse, UserModel, UserRoleUpdateModel, LoginRequest, UserUpdateData, \
    UserListFilters, UsersListResponse
from soft_assert import assert_equal


@allure.epic("Cinescope")
@allure.feature("Авторизация пользователей")
class TestAuthAPI:
    @allure.title("Создание пользователя")
    def test_register_user(self, api_manager:ApiManager, test_user:UserModel):
        with allure.step("Авторизация пользователя через api_manager"):
            response = api_manager.auth_api.register_user(test_user)
            user_creds = LoginRequest(email=test_user.email, password=test_user.password)
            api_manager.auth_api.authenticate(user_creds)

        with allure.step("Проверки"):
            assert_equal(response.email, test_user.email, "Email не совпадает")
            assert_equal(Roles.USER in response.roles, True, "Роль USER должна быть у пользователя")

        with allure.step("Удаление пользователя"):
            user_id = response.id
            api_manager.auth_api.delete_user(user_id, expected_status=200)

    @allure.title("Авторизация под данными админа")
    def test_authorization_admin(self, api_manager:ApiManager):
        with allure.step("Подготовка данных для авторизации"):
            login_data = LoginRequest(email = SuperAdminCreds.USERNAME, password= SuperAdminCreds.PASSWORD)
            api_manager.auth_api.login_user(login_data, expected_status=200)

        with allure.step("Авторизация через супер-админа"):
            api_manager.auth_api.login_user(login_data, expected_status=200)

    @allure.title("Попытка входа незарегестрированному юзеру")
    def test_login_unregister_user(self, api_manager:ApiManager):
        with allure.step("Подготовка данных"):
            login_data = LoginRequest(
                email=DataGenerator.generate_random_email(),
                password = DataGenerator.generate_random_password()
            )
        with allure.step("Авторизация:"):
            api_manager.auth_api.login_user(login_data, expected_status=401)

    @allure.title("Авторизация пользователя с неверным паролем")
    def test_authenticate_user_with_incorrect_password(self, api_manager: ApiManager):
        """Авторизация юзера с неверным паролем"""
        login_data = LoginRequest(
            email=SuperAdminCreds.USERNAME,
            password=DataGenerator.generate_random_password()
        )
        api_manager.auth_api.login_user(login_data, expected_status=401)

    @allure.title("Выход из учетной записи")
    def test_logout_user(self, admin):
        with allure.step("Выход из учетной записи под данными админа"):
            admin.api.auth_api.logout_user(expected_status=200)

    @allure.title("Попытка выхода из учетной записи без аутентификации")
    @pytest.mark.xfail(reason= "Фича логаута может дать возможность выйти из акка без токена, баг в будущем будет пофикшено")
    def test_logout_invalid_user(self, unauthorized_user):
        with allure.step("""Негативный тест:Выход из учетной записи без авторизации"""):
            unauthorized_user.api.auth_api.logout_user(expected_status=401)

    @allure.title("Обновление токена")
    @pytest.mark.xfail(reason="Фича рефреш токена не работает")
    def test_refresh_token_user(self, api_manager: ApiManager, test_user: UserModel):
        """Обновление refresh-token и access token"""

        with allure.step("Регистрация пользователя"):
            api_manager.auth_api.register_user(test_user, expected_status=201)

        with allure.step("Авторизация"):
            user_creds = LoginRequest(email=test_user.email, password=test_user.password)
            auth_response = api_manager.auth_api.authenticate(user_creds)
            old_token = auth_response["accessToken"]

        with allure.step("Попытка обновить токен доступа 'accessToken'"):
            refresh_response = api_manager.auth_api.refresh_token(expected_status=200)
            new_token = refresh_response.json()["accessToken"]

        with allure.step("Проверки"):
            assert_equal(old_token != new_token, True, "Токены не должны совпадать")

    @allure.title("Получение информации о пользователе")
    def test_get_user_info(self, api_manager:ApiManager, admin:User, registered_user:UserResponse):
        """получение информации о пользователе"""
        admin_creds = LoginRequest(email=admin.email, password=admin.password)
        api_manager.auth_api.authenticate(admin_creds)
        user_id = registered_user.id
        api_manager.auth_api.get_user_info(user_id, expected_status=200)

    @allure.title("Получение информации о пользователе, котьорого не существует")
    @pytest.mark.xfail(reason= "Апи работает некорректно, пропускает любой тип данных и в ответе 200-ка")
    def test_get_user_info_not_found(self, api_manager:ApiManager, admin:User):
        """Получение информации несуществующего юзера"""
        admin_creds = LoginRequest(email=admin.email, password=admin.password)
        api_manager.auth_api.authenticate(admin_creds)
        user_id = 1
        api_manager.auth_api.get_user_info(user_id, expected_status=404)

    @allure.title("Изменение данных у пользователя под правами суперадмина")
    def test_admin_change_user_info(self, super_admin: User, test_user: UserModel):
        """Позитивный тест: проверка на изменение полей у юзера под правами админа"""

        with allure.step("Регистрация пользователя"):
            registered_user = super_admin.api.auth_api.register_user(test_user, expected_status=201)
            user_id = registered_user.id

        with allure.step("Обновление данных пользователя (роль, verified, banned)"):
            update_data = UserUpdateData(
                roles=[Roles.USER, Roles.ADMIN],
                verified=True,
                banned=False
            )
            super_admin.api.auth_api.change_user_info(user_id, update_data, expected_status=200)

        with allure.step("Проверка, что данные обновились"):
            response = super_admin.api.user_api.get_user_info(user_id, expected_status=200)

            assert_equal(Roles.ADMIN in response.roles, True, "Роль ADMIN не добавлена")
            assert_equal(response.verified, True, "verified не обновился")
            assert_equal(response.banned, False, "banned не обновился")

    @allure.title("Создание пользователя напрямую через AuthAPI")
    def test_create_user_auth_api(self, super_admin: User):
        """Позитивный тест на создание пользователя через AuthAPI"""

        with allure.step("Подготовка данных для создания пользователя"):
            user_data = UserModel(
                fullName="ZALUPAPOPIKTRAH",
                email=f"test_{uuid.uuid4()}@example.com",
                password="12345678Aa",
                passwordRepeat="12345678Aa",
                verified=True,
                banned=False
            )

        with allure.step("Создание пользователя через AuthAPI"):
            response = super_admin.api.auth_api.create_user(user_data, expected_status=201)
            created_user = UserResponse(**response.json())
            user_id = created_user.id

        with allure.step("Проверка созданного пользователя"):
            assert_equal(created_user.email, user_data.email, "Email не совпадает")
            assert_equal(created_user.fullName, user_data.fullName, "FullName не совпадает")
            assert_equal(created_user.verified, user_data.verified, "Verified не совпадает")
            assert_equal(created_user.banned, user_data.banned, "Banned не совпадает")
            assert_equal(Roles.USER in created_user.roles, True, "Роль USER отсутствует")

        with allure.step("Очистка: удаление пользователя"):
            super_admin.api.auth_api.delete_user(user_id, expected_status=200)

    @allure.title("Попытка создать пользователя без авторизации")
    def test_create_user_unauthorized(self):
        """Негативный тест: попытка создать пользователя без авторизации"""

        with allure.step("Подготовка данных для создания пользователя"):
            user_data = UserModel(
                fullName="ZALUPAPOPIKTRAH",
                email=f"test_{uuid.uuid4()}@example.com",
                password="12345678Aa",
                passwordRepeat="12345678Aa",
                verified=True,
                banned=False
            )

        with allure.step("Создание сессии без авторизации"):
            clean_session = requests.Session()
            clean_api_manager = ApiManager(clean_session)

        with allure.step("Попытка создания пользователя без токена"):
            clean_api_manager.auth_api.create_user(user_data, expected_status=401)

    @allure.title("Получение список пользователей под правами администратора")
    def test_list_user(self, api_manager: ApiManager, admin: User):
        """Позитивный тест на получение списка пользователей (админ креды)"""

        with allure.step("Подготовка фильтров для списка пользователей"):
            filters = UserListFilters(
                page=1,
                pageSize=10,
                roles=[Roles.USER]
            )

        with allure.step("Получение списка пользователей"):
            response = admin.api.auth_api.get_list_user(filters, expected_status=200)
            users_list = UsersListResponse(**response.json())

        with allure.step("Проверка структуры ответа"):
            assert_equal(len(users_list.users) > 0, True, "Список пользователей пуст")
            assert_equal(users_list.page, 1, "Некорректная страница")
            assert_equal(users_list.pageSize, 10, "Некорректный размер страницы")

    @allure.title("Получение список пользователей")
    def test_list_user_not_admin_role(self, test_user, api_manager: ApiManager, common_user: User):
        """Негативный тест: попытка получить список будучи обычным юзером (по тз может только админ)"""

        with allure.step("Подготовка фильтров для списка пользователей"):
            filters = UserListFilters(page=1, pageSize=10, roles=[Roles.USER])

        with allure.step("Попытка получить список пользователей обычным пользователем"):
            common_user.api.auth_api.get_list_user(filters, expected_status=403)

    @allure.title("Удаление пользователя из системы")
    def test_delete_user(self, super_admin: User, registered_user: UserResponse):
        """Удаление пользователя из системы"""

        with allure.step("Удаление пользователя через супер-админа"):
            user_id = registered_user.id
            delete_response = super_admin.api.auth_api.delete_user(user_id, expected_status=200)

        with allure.step("Проверка, что ответ пустой"):
            assert_equal(len(delete_response.content) == 0, True, "Тело ответа должно быть пустым")

    @allure.title("Удаление пользователя без авторизации")
    def test_delete_user_not_authorized(self):
        """Негативный тест: удаление пользователя без авторизации"""

        with allure.step("Создание сессии без токена"):
            clean_session = requests.Session()
            clean_manager = ApiManager(clean_session)

        with allure.step("Попытка удаления пользователя без авторизации"):
            user_id = "123e4567-e89b-12d3-a456-426614174000"
            clean_manager.auth_api.delete_user(user_id, expected_status=401)

    @allure.title("Попытка создать фильм под ролью Администратора")
    def test_admin_create_movie_permission(self, movie_data:MovieModel, api_manager:ApiManager, admin):
        """Негативный тест: попытка создать фильм под ролью ADMIN(недоступная роль для создания фильма)"""
        admin.api.movie_api.create_movie_raw(movie_data, expected_status=403)

    @allure.title("Позитивный тест: Обновление роли пользователя")
    def test_update_role_user(self, registered_user: UserResponse, super_admin: User):

        with allure.step("Подготовка данных для обновления роли"):
            user_data = UserRoleUpdateModel(roles=[Roles.ADMIN])

        with allure.step("Обновление роли пользователя"):
            super_admin.api.user_api.update_role_user_admin(registered_user.id, user_data, expected_status=200)

        with allure.step("Проверка, что роль обновилась"):
            user_locator = UserLocator(id=registered_user.id)
            super_admin.api.user_api.get_user(user_locator, expected_status=200)