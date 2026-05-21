from pages.base_page import BasePage

from playwright.sync_api import Page
import allure


class CinescopeLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}/login"

        #Локаторы элементов
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Пароль")
        self.register_account = page.get_by_role("link", name="Зарегистрироваться")
        self.login_button = page.locator("form").get_by_role("button", name="Войти")

    @allure.step("Переход на страницу входа")
    def open(self):
        self.open_url(self.url)

    @allure.step("Полный процесс входа")
    def login(self, email:str, password:str):
        """Полный процесс входа"""
        self.enter_text_to_element(self.email_input, email, "Email")
        self.enter_text_to_element(self.password_input, password, "Пароль")
        self.click_element(self.login_button, "Войти")

    @allure.step("Редирект на домашнюю страницу")
    def assert_was_redirect_to_home_page(self):
        """Ожидание редиректа на домашнюю страницу"""
        self.wait_redirect_for_url(self.home_url)

    @allure.step("Ожидание появления/скрытия поп-апа")
    def assert_alert_was_pop_up(self):
        """Ожидание появления/скрытия поп-апа"""
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")