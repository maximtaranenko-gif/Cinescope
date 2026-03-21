import requests

from conftest import api_manager
from api.api_manager import ApiManager
import requests
from utils.data_generator import DataGenerator
from constants import EMAIL, PASSWORD, ADMIN_CREDS
import uuid


class TestAuthAPI:
    def test_register_user(self, api_manager:ApiManager, test_user:dict):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        user_creds = (test_user["email"], test_user["password"])
        api_manager.auth_api.authenticate(user_creds)

        # Проверки
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

        user_id = response_data['id']
        api_manager.auth_api.delete_user(user_id, expected_status=200)

    def test_authorization_admin(self, api_manager:ApiManager):
        """Тест на авторизацию юзера(админ креды)"""
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
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
            "email": EMAIL,
            "password": DataGenerator.generate_random_password()
        }
        api_manager.auth_api.login_user(login_data, expected_status=401)

    def test_logout_user(self, api_manager:ApiManager):
        """Выход из учетной записи(админ креды)"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        api_manager.auth_api.logout_user(expected_status=200)

    def test_logout_invalid_user(self, api_manager:ApiManager):
        """Негативный тест:Выход из учетной записи без авторизации"""
        api_manager.auth_api.logout_user(expected_status=200)

    # def test_refresh_token_user(self, api_manager:ApiManager):
    #     """Обновление refresh-token и access token"""
    #     auth_response = api_manager.auth_api.authenticate(ADMIN_CREDS)
    #     old_token = auth_response["accessToken"]
    #     refresh_response = api_manager.auth_api.refresh_token(expected_status=200)
    #     new_token = refresh_response.json()["accessToken"]
    #     assert old_token != new_token, "Токен доступа должен обновиться"
    #  Этот тест не работает, т.к апи сломано

    def test_get_user_info(self, api_manager:ApiManager, registered_user:dict):
        """получение информации о пользователе"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        user_id = registered_user["id"]
        api_manager.auth_api.get_user_info(user_id, expected_status=200)

    def test_get_user_info_not_found(self, api_manager:ApiManager):
        """Получение информации несуществующего юзера"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        user_id = "1291912"
        api_manager.auth_api.get_user_info(user_id, expected_status=200)

    def test_admin_change_user_info(self, api_manager: ApiManager, test_user: dict):
        """Негативный тест: проверка на изменения полей у юзера под кредами админа"""
        register_response = api_manager.auth_api.register_user(test_user)
        user_data = register_response.json()
        user_id = user_data["id"]

        api_manager.auth_api.authenticate(ADMIN_CREDS)

        update_data = {
            "roles": ["USER", "ADMIN"],
            "verified": True,
            "banned": False
        }

        api_manager.auth_api.change_user_info(user_id, update_data, expected_status=403)

    def test_create_user(self, api_manager: ApiManager):
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

        user_data = response.json()
        assert user_data["email"] == login_data["email"]
        assert user_data["fullName"] == login_data["fullName"]
        assert user_data["verified"] == login_data["verified"]
        assert user_data["banned"] == login_data["banned"]
        assert "id" in user_data

        user_id = user_data["id"]
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

    def test_list_user(self, api_manager:ApiManager):
        """Позитивный тест на получение списка пользователей(админ креды)"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        api_manager.auth_api.get_list_user(expected_status=200)

    def test_list_user_not_admin_role(self,test_user:dict, api_manager:ApiManager):
        """Негативный тест: попытка получить список будучи обычным юзером(по тз может только админ)"""
        # Создаем чистый менеджер без токена
        clean_session = requests.Session()
        clean_api_manager = ApiManager(clean_session)

        api_manager.auth_api.register_user(test_user)
        clean_api_manager.auth_api.get_list_user(expected_status=401)

    def test_delete_user(self, api_manager:ApiManager, registered_user:dict):
        """Удаление пользователя из системы"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        user_id = registered_user["id"]
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