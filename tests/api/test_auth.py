from conftest import api_manager
from api.api_manager import ApiManager
import requests
from utils.data_generator import DataGenerator
from constants import ADMIN_CREDS, Roles
from resources.user_creds import SuperAdminCreds
import uuid
import pytest
from models.user_models import RegisterUserResponse, UserModel


class TestAuthAPI:
    def test_register_user(self, api_manager:ApiManager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        register_user_response = RegisterUserResponse(**response.json())

        user_creds = (test_user.email, test_user.password)
        api_manager.auth_api.authenticate(user_creds)

        assert register_user_response.email == test_user.email, "Email не совпадает"
        assert Roles.USER in register_user_response.roles, "Роль USER должна быть у пользователя"

        user_id = register_user_response.id
        api_manager.auth_api.delete_user(user_id, expected_status=200)

    def test_authorization_admin(self, api_manager:ApiManager):
        """Тест на авторизацию юзера(админ креды)"""
        login_data = {
            "email": SuperAdminCreds.USERNAME,
            "password": SuperAdminCreds.PASSWORD
        }
        api_manager.auth_api.login_user(login_data, expected_status=200)

    def test_login_unregister_user(self, api_manager:ApiManager):
        """Тест на авторизацию незарезаного юзера"""
        login_data = {
            "email": DataGenerator.generate_random_email(),
            "password": DataGenerator.generate_random_password()
        }
        api_manager.auth_api.login_user(login_data, expected_status=401)

    def test_negative_empty_body_request(self,api_manager:ApiManager):
        """Проверка пустым телом запроса"""
        login_data = {}
        api_manager.auth_api.login_user(login_data, expected_status=401)

    def test_authenticate_user_with_incorrect_password(self, api_manager: ApiManager):
        """Авторизация юзера с неверным паролем"""
        login_data = {
            "email": SuperAdminCreds.USERNAME,
            "password": DataGenerator.generate_random_password()
        }
        api_manager.auth_api.login_user(login_data, expected_status=401)

    def test_logout_user(self, admin):
        """Выход из учетной записи(админ креды)"""
        admin.api.auth_api.logout_user(expected_status=200)

    @pytest.mark.xfail(reason= "Фича логаута может дать возможность выйти из акка без токена, баг в будущем будет пофикшено")
    def test_logout_invalid_user(self, unauthorized_user):
        """Негативный тест:Выход из учетной записи без авторизации"""
        unauthorized_user.api.auth_api.logout_user(expected_status=401)

    @pytest.mark.xfail(reason="Фича рефршен токена и доступа не работает, в будущем при её реализации тест будет pass")
    def test_refresh_token_user(self, api_manager:ApiManager):
        """Обновление refresh-token и access token"""
        auth_response = api_manager.auth_api.authenticate(ADMIN_CREDS)
        old_token = auth_response["accessToken"]
        refresh_response = api_manager.auth_api.refresh_token(expected_status=200)
        new_token = refresh_response.json()["accessToken"]
        assert old_token != new_token, "Токен доступа должен обновиться"

    def test_get_user_info(self, api_manager:ApiManager, registered_user:RegisterUserResponse):
        """получение информации о пользователе"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        user_id = registered_user.id
        api_manager.auth_api.get_user_info(user_id, expected_status=200)

    @pytest.mark.xfail(reason= "Апи работает некорректно, пропускает любой тип данных и в ответе 200-ка")
    def test_get_user_info_not_found(self, api_manager:ApiManager):
        """Получение информации несуществующего юзера"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        user_id = 1
        api_manager.auth_api.get_user_info(user_id, expected_status=404)

    def test_admin_change_user_info(self, api_manager: ApiManager, test_user:UserModel):
        """Позитивный тест тест: проверка на изменения полей у юзера под кредами админа"""
        response = api_manager.auth_api.register_user(test_user)
        register_user_response = RegisterUserResponse(**response.json())
        user_id = register_user_response.id

        api_manager.auth_api.authenticate(ADMIN_CREDS)

        update_data = {
            "roles": ["USER", "ADMIN"],
            "verified": True,
            "banned": False
        }

        api_manager.auth_api.change_user_info(user_id, update_data, expected_status=200)

    def test_create_user_auth_api(self, api_manager: ApiManager):
        """Позитивный тест на создание юзера"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)

        login_data = {
            "fullName": "ZALUPAPOPIKTRAH",
            "email": f"test_{uuid.uuid4()}@example.com",
            "password": "12345678Aa",
            "verified": True,
            "banned": False
        }

        response = api_manager.auth_api.create_user(login_data, expected_status=201)

        user_data = RegisterUserResponse(**response.json())
        assert user_data.email == login_data["email"]
        assert user_data.fullName == login_data["fullName"]
        assert user_data.verified == login_data["verified"]
        assert user_data.banned == login_data["banned"]
        assert Roles.USER in user_data.roles, "Роль USER должна быть у созданного пользователя"

        user_id = user_data.id
        api_manager.auth_api.delete_user(user_id, expected_status=200)

    def test_create_user_unauthorized(self, api_manager: ApiManager):
        """Негативный тест: попытка создать юзера без авторизации"""

        # Создаем чистый менеджер без токена
        clean_session = requests.Session()
        clean_api_manager = ApiManager(clean_session)

        login_data = {
            "fullName": "ZALUPAPOPIKTRAH",
            "email": f"test_{uuid.uuid4()}@example.com",
            "password": "12345678Aa",
            "verified": True,
            "banned": False
        }

        clean_api_manager.auth_api.create_user(login_data, expected_status=401)

    def test_list_user(self, api_manager:ApiManager, admin):
        """Позитивный тест на получение списка пользователей(админ креды)"""
        admin.api.auth_api.get_list_user(expected_status=200)

    def test_list_user_not_admin_role(self,test_user, api_manager:ApiManager, common_user):
        """Негативный тест: попытка получить список будучи обычным юзером(по тз может только админ)"""
        # Создаем чистый менеджер без токена
        common_user.api.auth_api.get_list_user(expected_status=403)

    def test_delete_user(self, api_manager:ApiManager, registered_user):
        """Удаление пользователя из системы"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        user_id = registered_user.id
        delete_response = api_manager.auth_api.delete_user(user_id, expected_status=200)
        """"проверим что пользователь удалён"""
        assert len(delete_response.content) == 0, "Тело ответа должно быть пустым"

    def test_delete_user_not_authorization(self):
        """Удаление юзера из системы без авторизации"""
        clean_session = requests.Session()
        clean_manager = ApiManager(clean_session)
        """Несуществующий юзер"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        clean_manager.auth_api.delete_user(user_id, expected_status=401)

    def test_admin_create_movie_permission(self, movie_data:dict, api_manager:ApiManager, admin):
        """Негативный тест: попытка создать фильм под ролью ADMIN(недоступная роль для создания фильма)"""
        admin.api.movie_api.create_movie(movie_data, expected_status=403)