from conftest import api_manager
from api.api_manager import ApiManager


class TestAuthAPI:
    def test_register_user(self, api_manager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        # Проверки
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на авторизацию уже существующего пользователя
        """

        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data
        assert response_data["user"]["email"] == registered_user["email"]

    def test_login_user(self, api_manager, test_user):
        """Тест на авторизацию незарезаного юзера"""
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert response.status_code == 201, "Авторизация не удалась"
        assert "accessToken" in response_data, "Токен в ответе отсутствует"
        assert "user" in response_data, "Поле user отсутствует в ответе"
        # Проверка email
        assert "email" in response_data["user"], "В объекте user отсутствует поле email"
        assert "email" is not None, "email равен None"
        assert "email" != "", "email пустой"
        assert "@" in response_data["user"]["email"], f"email не содержит @"

    def test_negative_incorrect_data_authorization(self,api_manager: ApiManager, test_user):
        """Некорректные данные для авторизации(собственный пароль)"""
        login_data = {
            "email":test_user["email"],
            "password": "Geychik228"
        }
        response = api_manager.auth_api.login_user(login_data)

        assert response.status_code == 401, f"Ожидалась ошибка 401 , получили: {response.status_code}"

    def test_negative_incorrect_email(self,api_manager: ApiManager, test_user):
        """#Некоректный email"""
        login_data = {
            "email": "maximtaranenko@gmail.com",
            "password":test_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)

        assert response.status_code == 401, f"Ожидалась ошибка 401, получили {response.status_code}"

    def test_negative_empty_body_request(self,api_manager:ApiManager, test_user):
        """Проверка пустым телом запроса"""
        login_data = {

        }
        response = api_manager.auth_api.login_user(login_data)

        assert response.status_code == 401, f"Ожидалась ошибка 401, сервер вернул {response.status_code}"


    def test_negative_empty_json(self, api_manager: ApiManager):
        """Проверка пустым json"""
        login_data = {
            "email":"",
            "password":""
        }
        response = api_manager.auth_api.login_user(login_data)

        assert response.status_code == 400, "Некорректный запрос"


    def test_negative_empty_str(self, api_manager: ApiManager):
        """Проверка пустой строкой"""
        login_data = ""
        response = api_manager.auth_api.login_user(login_data)

        assert response.status_code == 400, "Некорректный запрос"







