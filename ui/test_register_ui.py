import allure
import pytest

from pages.register_page import CinescopeRegisterPage

@allure.epic("Тестирование UI")
@allure.feature("Тестирование страницы регистрации")
@pytest.mark.ui
@pytest.mark.pwregister
class TestRegisterPage:
    @allure.title("Проведение успешной регистрации в системе")
    def test_register_by_ui(self, test_user, page_from_fixtures):

        with allure.step(f"Регистрация пользователя: {test_user.email}"):
            register_page = CinescopeRegisterPage(page_from_fixtures)
            register_page.open()
            register_page.register(test_user.fullName, test_user.email, test_user.password, test_user.passwordRepeat)

        with allure.step("Проверка редиректа на страницу авторизации"):
            register_page.wait_redirect_to_login()

        with allure.step("Проверка появления всплывающего окна об подтверждении почты"):
            register_page.assert_alert_was_pop()