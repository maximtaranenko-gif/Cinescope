import requests
import allure
from models.user_models import UserModel, LoginRequest, UserListFilters, UserUpdateData, UserResponse
from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT, LOGOUT_ENDPOINT, REFRESH_TOKEN_ENDPOINT, CREATE_USER, \
    GET_LIST_USER
from custom_requester.custom_requester import CustomRequester
from constants import AUTH_URL


class AuthAPI(CustomRequester):
    def __init__(self, session:requests.Session)->None:
        super().__init__(session=session,base_url=f"{AUTH_URL}")

    @allure.step("Регистрация нового пользователя")
    def register_user(self, user_data: UserModel, expected_status: int = 201):
        with allure.step(f"Email: {user_data.email}"):
            response =  self.send_request(
                method="POST",
                endpoint=REGISTER_ENDPOINT,
                data = user_data.model_dump(),
                expected_status=expected_status
            )
            return UserResponse(**response.json())

    @allure.step("Авторизация пользователя")
    def login_user(self, login_data: LoginRequest, expected_status: int= 200):
        with allure.step(f"Email: {login_data.email}"):
            return self.send_request(
                method="POST",
                endpoint=LOGIN_ENDPOINT,
                data = login_data.model_dump(),
                expected_status=expected_status
            )

    @allure.step("Создание нового пользователя")
    def create_user(self, user_data: UserModel, expected_status: int = 200):
        with allure.step(f"Email: {user_data.email}"):
            return self.send_request(
                method="POST",
                data = user_data.model_dump(),
                endpoint=CREATE_USER,
                expected_status= expected_status
            )

    @allure.step("Получение списка пользователей: ")
    def get_list_user(self, list_user: UserListFilters,expected_status: int = 200):
        with allure.step(f"Список : page = {list_user.page}, pageSize = {list_user.pageSize}, roles = {list_user.roles}"):
            return self.send_request(
                method="GET",
                data = list_user.model_dump(exclude_none=True),
                endpoint=GET_LIST_USER,
                expected_status= expected_status
            )

    @allure.step("Выход из аккаунта")
    def logout_user(self, expected_status: int = 200):
        """Logout user"""
        return self.send_request(
            method="GET",
            endpoint=LOGOUT_ENDPOINT,
            expected_status = expected_status
        )

    @allure.step("Обновление токена")
    def refresh_token(self, expected_status: int = 200):
        """refresh-token user"""
        return self.send_request(
            method = "GET",
            endpoint=REFRESH_TOKEN_ENDPOINT,
            expected_status= expected_status
        )

    @allure.step("Получение информации о пользователе по ID: {user_id}")
    def get_user_info(self, user_id: int, expected_status: int = 200):
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    @allure.step("Удаление пользователя по ID: {user_id}")
    def delete_user(self,user_id: int, expected_status: int = 204)->requests.Response:
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    @allure.step("Изменение информации о пользователе по ID: {user_id}")
    def change_user_info(self, user_id: int, update_data: UserUpdateData, expected_status: int = 200):
        with allure.step(f"Обновляем пользователя: {user_id}: {update_data.model_dump(exclude_none=True)}"):
            return self.send_request(
                method="PATCH",
                endpoint=f"/user/{user_id}",
                data = update_data.model_dump(),
                expected_status=expected_status
            )

    @allure.step("Аутентификация")
    def authenticate(self, user_creds: LoginRequest):
        with allure.step(f"Email : {user_creds.email}"):
            response = self.login_user(user_creds).json()
            if "accessToken" not in response:
                raise KeyError("token is missing")
            token = response["accessToken"]
            self._update_session_headers(**{"authorization": "Bearer " + token})
            return response