from pages.base_page import BasePage

from playwright.sync_api import Page
import allure


class CinescopeReviewMovie(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}movies"

        #Локаторы элементов
        self.write_review = page.get_by_role("textbox", name="Написать отзыв") #Поле отзыва
        self.rating = page.locator('button[role="combobox"][data-state="closed"]') #Сама кнопка меню оценки
        self.rating_option = lambda rating: page.locator(f'[role="option"]:has-text("{rating}")') #Сам выбор конкретной оценки
        self.send_review = page.get_by_role("button", name="Отправить") # Кнопка отправить

    @allure.step("Переход на домашнюю страницу(/movies)")
    def open(self):
        self.page.goto(self.url)

    @allure.step("Выбор фильма по индексу(default=2)")
    def select_movie_by_index(self, movie_index: int = 2):
        movie_selector = self.page.locator(f"div:nth-child({movie_index}) > .items-center.p-6 > a > .inline-flex")
        self.click_element(movie_selector, f"Фильм номер {movie_index}")
        self.wait_for_element(self.write_review, "visible")
        return self

    @allure.step("Установить рейтинг")
    def set_rating(self, rating:int):
        self.click_element(self.rating, "Элемент оценки")
        self.click_element(self.rating_option(rating), f"Выбор оценки {rating}")

    @allure.step("Полный процесс отправки отзыва")
    def full_send_review(self, rating: int, random_review):
        """Полный метод для отправки отзыва"""
        self.set_rating(rating)
        self.enter_text_to_element(self.write_review, random_review, "Написание отзыва" )
        self.click_element(self.send_review, "Отправка отзыва")
        self.make_screenshot_and_attach_this_page()
        return self

    @allure.step("Появление/скрытие поп-апа")
    def alert_was_pop_up(self):
        self.check_pop_up_element_with_text("Отзыв успешно создан")