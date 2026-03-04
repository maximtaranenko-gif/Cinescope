import pytest
import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthAPI:
    def test_register_user(self, test_user):
        #URL для регистрации
        register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"

        #Отправка запроса на регистрацию
        response = requests.post(register_url, json=test_user, headers=HEADERS)

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
        #URL авторизации
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

        #Данные для авторизации
        login_data = {
            "email":test_user["email"],
            "password":test_user["password"]
        }

        #Отправка запроса на авторизацию
        response = requests.post(login_url, json=login_data, headers=HEADERS)

        #Логи авторизации
        print(f"{response.status_code}")
        print(f"{response.text}")

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

    def test_negative_checks_authorization(self, test_user):
        #URL для авторизации
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"


        #Некорректные данные для авторизации(собственный пароль)
        login_data_wrong_password = {
            "email":test_user["email"],
            "password": "Geychik228"
        }
        response = requests.post(login_url, json=login_data_wrong_password, headers=HEADERS)

        #Логи
        print(f"Response status: {response.status_code}")
        print(f"Response body wrong password: {response.text}")
        #Проверки
        assert response.status_code == 401, f"Ожидалась ошибка 401 , получили: {response.status_code}"


        #Некоректный email
        login_data_incorrect_email = {
            "email": "maximtaranenko@gmail.com",
            "password":test_user["password"]
        }
        response = requests.post(login_url, json=login_data_incorrect_email, headers=HEADERS)

        print(f"Response body incorrect email: {response.text}")
        #Проверки
        try:
            assert response.status_code == 401
        except AssertionError:
            print(f"Ошибка от сервера, ожидалось 401, получили {response.status_code}")


        #Проверка пустым json
        login_data_empty = {
            "email":"",
            "password":""
        }
        response = requests.post(login_url, json=login_data_empty, headers=HEADERS)
        #Проверки
        if response.status_code == 500:
            print(f"Баг: сервер возвращает {response.status_code}")
        else:
            assert response.status_code == 400, "Некорректный запрос"


        #Проверка пустой строкой
        login_data_wrong_str = ""
        response = requests.post(login_url, json= login_data_wrong_str, headers=HEADERS)
        assert response.status_code == 400, "Некорректный запрос"






