from typing import Literal

from playwright.sync_api import Page, Locator
import allure


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Открытие страницы: {url}")
    def open_url(self, url:str):
        self.page.goto(url)

    @allure.step("Ввод текста {text} в поле '{element_name}'")
    def enter_text_to_element(self, locator:Locator, text:str, element_name:str = ""):
        locator.fill(text)

    @allure.step("Клик по локатору: {element_name}")
    def click_element(self, locator:Locator, element_name:str = ""):
        locator.click()

    @allure.step("Ожидание загрузки страницы: {url}")
    def wait_redirect_for_url(self, url:str):
        self.page.wait_for_url(url)

    @allure.step("Получение текста элемента: {element_name}")
    def get_element_text(self, locator:Locator, element_name:str = "")-> str:
        return locator.text_content()

    @allure.step("Ожидание появления или исчезновения элемента: {state}")
    def wait_for_element(self, locator: Locator, state: Literal["visible", "hidden"] = "visible"):
        locator.wait_for(state=state)

    @allure.step("Получение текста отзыва: {review_text}")
    def get_review_text(self, review_text: str)->str:
        review_element = self.page.get_by_text(review_text)
        self.wait_for_element(review_element, "visible")
        return review_element.text_content()

    @allure.step("Скриншот текущей страницы")
    def make_screenshot_and_attach_this_page(self):
        screenshot_path = "screenshot.png"
        self.page.screenshot(path=screenshot_path, full_page=True)

        with open(screenshot_path, "rb") as file:
            allure.attach(file.read(), name="Screenshot after redirect", attachment_type=allure.attachment_type.PNG)

    @allure.step("Проверка всплывающего сообщения с текстом: {text}")
    def check_pop_up_element_with_text(self, text:str):

        with allure.step(f"Проверка появления алерта с текстом: {text}"):
            notification_locator = self.page.get_by_text(text)
            notification_locator.wait_for(state="visible") #Появление текста

        with allure.step(f"Проверка скрытия алерта с текстом: {text}"):
            notification_locator.wait_for(state="hidden") #Скрытие текста


class BasePage(PageAction):
    def __init__(self, page: Page):
        super().__init__(page)
        self.home_url = "https://dev-cinescope.coconutqa.ru/"

        # Общие локаторы для всех страниц на сайте
        self.home_button = page.get_by_text("Все фильмы")
        self.all_movies_button = page.get_by_role("link", name="Все фильмы")
        self.login_button = page.locator('button[type="button"]:has-text("Войти")')
        self.register_button = page.get_by_role("button", name="Зарегистрироваться")

    @allure.step("Переход на главную страницу из шапки")
    def go_to_home_page(self):
        """Переход на домашнюю страницу(главную)"""
        self.click_element(self.home_button, "Cinescope")
        self.wait_redirect_for_url(self.home_url)

    @allure.step("Переход на страницу 'Все фильмы, из шапки профиля'")
    def go_to_all_movies(self):
        """Переход ко всем фильмам"""
        self.click_element(self.all_movies_button, "Все фильмы")
        self.wait_redirect_for_url(f"{self.home_url}/movies")