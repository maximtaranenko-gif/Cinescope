import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthAPI:
    #Эндпоинт регистрации
    REGISTER_URL = f"{BASE_URL}{REGISTER_ENDPOINT}"
    #Эндпоинт авторизации
    LOGIN_URL = f"{BASE_URL}{LOGIN_ENDPOINT}"


    def test_register_user(self, requester, test_user):
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=test_user,
            expected_status=201
        )
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_authorization_user(self,requester, test_user):
        #Данные для авторизации
        login_data = {
            "email":test_user["email"],
            "password":test_user["password"]
        }

        #Отправка запроса на авторизацию
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=201)

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

    def test_negative_incorrect_data_authorization(self,requester, test_user):
        #Некорректные данные для авторизации(собственный пароль)
        login_data = {
            "email":test_user["email"],
            "password": "Geychik228"
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=401)

        #Проверки
        assert response.status_code == 401, f"Ожидалась ошибка 401 , получили: {response.status_code}"

    def test_negative_incorrect_email(self,requester, test_user):
        #Некоректный email
        login_data = {
            "email": "maximtaranenko@gmail.com",
            "password":test_user["password"]
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=401)

        #Проверки
        assert response.status_code == 401, f"Ожидалась ошибка 401, получили {response.status_code}"

    def test_negative_empty_body_request(self,requester, test_user):
        #Проверка пустым телом запроса
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            expected_status=401)
        #Проверки
        assert response.status_code == 401, f"Ожидалась ошибка 401, сервер вернул {response.status_code}"


    def test_negative_empty_json(self, requester):
        #Проверка пустым json
        login_data = {
            "email":"",
            "password":""
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=401)

        #Проверки

        assert response.status_code == 400, "Некорректный запрос"


    def test_negative_empty_str(self, requester):
        #Проверка пустой строкой
        login_data = ""
        response = requester.send_request(
            method="POST",
            endpoint= LOGIN_ENDPOINT,
            data=login_data,
            expected_status=400)

        #Проверки
        assert response.status_code == 400, "Некорректный запрос"







