from conftest import api_manager
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator
from constants import USER_CREDS, EMAIL, PASSWORD


class TestAuthAPI:
    def test_register_user(self, api_manager, test_user):
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
        api_manager.user_api.delete_user(user_id, expected_status=200)

    def test_authorization_admin(self, api_manager):
        """Тест на авторизацию юзера(админ креды)"""
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        response = api_manager.auth_api.login_user(login_data, expected_status=200)
        assert response.status_code == 200, "Неверныйл логин или пароль"

    def test_login_unregister_user(self, api_manager):
        """Тест на авторизацию незарезаного юзера"""
        login_data = {
            "email": DataGenerator.generate_random_email(),
            "password": DataGenerator.generate_random_password()
        }
        response = api_manager.auth_api.login_user(login_data, expected_status=401)

        #Проверки
        assert response.status_code == 401, "Авторизация не удалась"


    def test_negative_empty_body_request(self,api_manager:ApiManager, test_user):
        """Проверка пустым телом запроса"""
        login_data = {

        }
        response = api_manager.auth_api.login_user(login_data, expected_status=401)

        assert response.status_code == 401, f"Ожидалась ошибка 401, сервер вернул {response.status_code}"


    def test_authenticate_user_with_incorrect_password(self, api_manager: ApiManager):
        """Авторизация юзера с неверным паролем"""
        login_data = {
            "email": EMAIL,
            "password": DataGenerator.generate_random_password()
        }
        response = api_manager.auth_api.login_user(login_data, expected_status=401)
        assert response.status_code == 401, "Неверный логин или пароль"