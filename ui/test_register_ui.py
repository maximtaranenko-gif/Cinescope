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
        #Создание объекта страницы регистрации Cinescope
        register_page = CinescopeRegisterPage(page_from_fixtures)

        #Регаемся на сайте при помощи модели, которая содержит в себе уже полную форму регистрации
        register_page.open()
        register_page.register(test_user.fullName, test_user.email, test_user.password, test_user.passwordRepeat)

        #Проверка редиректа на страницу авторизации и состояние локаторов
        register_page.wait_redirect_to_login()
        register_page.assert_alert_was_pop()