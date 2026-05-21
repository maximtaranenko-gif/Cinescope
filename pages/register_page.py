from playwright.sync_api import Page
import allure

from pages.base_page import BasePage


class CinescopeRegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

        #Локаторы элементов
        self.full_name_input = page.get_by_role("textbox", name="Имя Фамилия Отчество")
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Пароль", exact=True)
        self.passwordRepeat_input = page.get_by_role("textbox", name="Повторите пароль")

    @allure.step("Открытие страницы")
    def open(self):
        self.open_url(self.url)

    @allure.step("Полный процесс регистрации")
    def register(self, full_name, email, password, passwordRepeat):
        """Полный процесс регистрации"""
        self.enter_text_to_element(self.full_name_input,full_name, "ФИО")
        self.enter_text_to_element(self.email_input, email, "Email")
        self.enter_text_to_element(self.password_input, password, "Пароль")
        self.enter_text_to_element(self.passwordRepeat_input, passwordRepeat, "Повторение пароля")
        self.click_element(self.register_button, "Зарегистрироваться")

    @allure.step("Переход на страницу авторизации")
    def wait_redirect_to_login(self):
        self.wait_redirect_for_url(f"{self.home_url}login")

    @allure.step("Ожидание появления/скрытия поп-апа")
    def assert_alert_was_pop(self):
        """Ожидание появление/скрытия поп-апа"""
        self.check_pop_up_element_with_text("Подтвердите свою почту")