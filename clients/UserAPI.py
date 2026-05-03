import requests
import allure

from custom_requester.custom_requester import CustomRequester
from models.user_models import UserModel, UserResponse, UserRoleUpdateModel, UserLocator, UsersListLocatorResponse


class UserAPI(CustomRequester):
    def __init__(self, session: requests.Session) -> None:
        super().__init__(session=session, base_url="https://auth.dev-cinescope.coconutqa.ru/")

    @allure.step("Получить информацию о пользователе по ID: {user_id}")
    def get_user_info(self, user_id: int, expected_status: int = 200) -> UserResponse:
        with allure.step(f"Запрос информации о пользователе {user_id}"):
            response = self.send_request(
                method="GET",
                endpoint=f"/user/{user_id}",
                expected_status=expected_status
            )
            return UserResponse(**response.json())

    @allure.step("Получить пользователя по локатору: {user_locator}")
    def get_user(self, user_locator: UserLocator, expected_status: int = 403) -> UsersListLocatorResponse:
        with allure.step(f"Запрос пользователей по локатору: {user_locator}"):
            response = self.send_request(
                method="GET",
                endpoint="user",
                params=user_locator.model_dump(),
                expected_status=expected_status
            )
            return UsersListLocatorResponse(**response.json())

    @allure.step("Создание нового пользователя")
    def create_user(self, user_data: UserModel, expected_status: int = 201) -> UserResponse:
        with allure.step(f"Создание пользователя: {user_data.email}"):
            response = self.send_request(
                method="POST",
                endpoint="user",
                data=user_data.model_dump(),
                expected_status=expected_status
            )
            return UserResponse(**response.json())

    @allure.step("Удаление пользователя по ID: {user_id}")
    def delete_user(self, user_id: int, expected_status: int = 204):
        with allure.step(f"Удаление пользователя {user_id}"):
            return self.send_request(
                method="DELETE",
                endpoint=f"/user/{user_id}",
                expected_status=expected_status
            )

    @allure.step("Обновление роли пользователя: user_id={user_id}")
    def update_role_user_admin(self, user_id: str, user_data: UserRoleUpdateModel, expected_status: int = 200) -> UserRoleUpdateModel:
        with allure.step(f"Обновление роли пользователя {user_id} на {user_data.roles}"):
            response = self.send_request(
                method="PATCH",
                endpoint=f"/user/{user_id}",
                data=user_data.model_dump(),
                expected_status=expected_status
            )
            return UserRoleUpdateModel(**response.json())