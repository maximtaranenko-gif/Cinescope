import pytest
import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthAPI:
    #Эндпоинт регистрации
    REGISTER_URL = f"{BASE_URL}{REGISTER_ENDPOINT}"
    #Эндпоинт авторизации
    LOGIN_URL = f"{BASE_URL}{LOGIN_ENDPOINT}"


    def test_register_user(self, test_user):
        #Отправка запроса на регистрацию
        response = requests.post(TestAuthAPI.REGISTER_URL, json=test_user, headers=HEADERS)

        #Логируем ответ для диагностики:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        #Проверки
        assert response.status_code == 201, "Ошибка регистрации пользователя"
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"

        #Проверяем, что роль USER назначена по умолчанию
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"


    def test_authorization_user(self, test_user):
        #Данные для авторизации
        login_data = {
            "email":test_user["email"],
            "password":test_user["password"]
        }

        #Отправка запроса на авторизацию
        response = requests.post(TestAuthAPI.LOGIN_URL, json=login_data, headers=HEADERS)

        #Логи авторизации
        print(f"{response.status_code}")
        print(f"{response.text}")
        print("=" * 180)

        #Проверки
        assert response.status_code == 201, "Авторизация не удалась"
        response_data = response.json()
        assert "accessToken" in response_data, "Токен в ответе отсутствует"
        assert "user" in response_data, "Поле user отсутствует в ответе"
        #Проверка email
        assert "email" in response_data["user"], "В объекте user отсутствует поле email"
        assert "email" is not None, "email равен None"
        assert "email" != "", "email пустой"
        assert "@" in response_data["user"]["email"], f"email не содержит @"


    def test_negative_incorrect_data_authorization(self, test_user):
        #Некорректные данные для авторизации(собственный пароль)
        login_data = {
            "email":test_user["email"],
            "password": "Geychik228"
        }
        response = requests.post(TestAuthAPI.LOGIN_URL, json=login_data, headers=HEADERS)

        #Логи
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print("=" * 180)
        #Проверки
        assert response.status_code == 401, f"Ожидалась ошибка 401 , получили: {response.status_code}"


    def test_negative_incorrect_email(self, test_user):
        #Некоректный email
        login_data = {
            "email": "maximtaranenko@gmail.com",
            "password":test_user["password"]
        }
        response = requests.post(TestAuthAPI.LOGIN_URL, json=login_data, headers=HEADERS)

        #Логи
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print("=" * 180)

        #Проверки
        assert response.status_code == 401, f"Ожидалась ошибка 401, получили {response.status_code}"


    def test_negative_empty_body_request(self, test_user):
        #Проверка пустым телом запроса
        response = requests.post(TestAuthAPI.LOGIN_URL, headers=HEADERS)

        #Логи
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print("=" * 180)

        assert response.status_code == 401, f"Ожидалась ошибка 401, сервер вернул {response.status_code}"


    def test_negative_empty_json(self):
        #Проверка пустым json
        login_data = {
            "email":"",
            "password":""
        }
        response = requests.post(TestAuthAPI.LOGIN_URL, json=login_data, headers=HEADERS)

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print("=" * 180)
        #Проверки

        assert response.status_code == 400, "Некорректный запрос"


    def test_negative_empty_str(self):
        #Проверка пустой строкой
        login_data = ""
        response = requests.post(TestAuthAPI.LOGIN_URL, json= login_data, headers=HEADERS)

        #Логи
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print("=" * 180)

        #Проверки
        assert response.status_code == 400, "Некорректный запрос"







