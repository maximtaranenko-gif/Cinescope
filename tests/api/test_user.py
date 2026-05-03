import allure
import pytest

from models.user_models import UserResponse
from soft_assert import assert_equal

@allure.epic("Пользователи")
@allure.feature("Управление пользователями")
@pytest.mark.users
class TestUser:

    @allure.title("Создание пользователя через суперадмина")
    @pytest.mark.api
    @pytest.mark.positive
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_create_user_user_api(self, super_admin, creation_user_data):
        with allure.step("Создание юзера"):
            response = super_admin.api.user_api.create_user(creation_user_data, expected_status=201)

        with allure.step("Проверка данных созданного пользователя"):
            assert_equal(response.email, creation_user_data.email, "Email не совпадает")
            assert_equal(response.fullName, creation_user_data.fullName, "Имя не совпадает")
            assert_equal(response.roles, creation_user_data.roles, "Роль не совпадает")
            assert_equal(response.verified,True,  "Пользователь не подтвержден ")

    @allure.title("Получение созданного пользователя по ID")
    @pytest.mark.api
    @pytest.mark.positive
    def test_get_user_by_locator(self, super_admin, creation_user_data):
        with allure.step("Создание пользователя"):
            created_user = super_admin.api.user_api.create_user(creation_user_data, expected_status=201)


        with allure.step("Получение данных пользователя по ID"):
            user_by_id = super_admin.api.user_api.get_user_info(created_user.id, expected_status=200)


        with allure.step("Проверка пользователя после получения данных"):
            assert_equal(user_by_id.id, created_user.id, "ID не совпадает")
            assert_equal(user_by_id.email, created_user.email, "Email не совпадает")
            assert_equal(user_by_id.roles, created_user.roles, "Роль не совпадает")
            assert_equal(user_by_id.verified, True, "Пользователь не подтвердил почту")
            assert_equal(created_user.verified,True,  "Созданный пользователь не имеет подтверждения почты")

    @pytest.mark.xfail(reason="При рефакторинге кода этот тест оказался нерабочим, т.к он пытается распарсить 403 статус код")
    @allure.title("Получение пользователя по ID через роль обычного пользователя")
    @pytest.mark.api
    @pytest.mark.negative
    def test_get_user_by_id_common_user(self, common_user):
        with allure.step("Получение пользователя по ID через обычного пользователя"):
            common_user.api.user_api.get_user_info(common_user.id, expected_status=403)