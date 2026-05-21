from pages.login_page import CinescopeLoginPage

import allure
import pytest

@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
@pytest.mark.pwlogin
class TestloginPage:
   @allure.title("Проведение успешного входа в систему")
   def test_login_by_ui(self, test_user, registered_user, page_from_fixtures):

        with allure.step(f"Авторизация пользователя {test_user.email}"):
           login_page = CinescopeLoginPage(page_from_fixtures)
           login_page.open()
           login_page.login(test_user.email, test_user.password) # Осуществяем вход

        with allure.step("Проверка редиректа на домашнюю страницу"):
            login_page.assert_was_redirect_to_home_page() # Проверка редиректа на домашнюю страницу

        with allure.step("Прикрепление скриншота"):
            login_page.make_screenshot_and_attach_this_page()  # Прикрепляем скриншот

        with allure.step("Проверка всплывающего сообщения об успешном входе"):
            login_page.assert_alert_was_pop_up()