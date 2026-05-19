import allure
import pytest
from faker import Faker

from pages.review_movie_page import CinescopeReviewMovie

@allure.epic("Тестирование UI")
@allure.feature("Тестирование страницы написания отзыва")
@allure.title("Создание отзыва под фильмом под авторизованным пользователем")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.pwreviews
class TestMoviePage:
    allure.title("Проведение успешного оставления отзыва")
    def test_create_review_movie(self, authorized_page):
        # Генерация рандомного отзыва
        fake = Faker('ru_RU')
        random_review = ' '.join(fake.words(5)) #Отзыв
        random_movie_index = fake.random_int(min=2, max=6) #Кино индекс
        random_rating = fake.random_int(min=1, max=5) #Сам рейтинг

        #Создание объекта для отправки отзыва
        create_review_movie = CinescopeReviewMovie(authorized_page)

        #Создание отзыва(рандом данные)
        create_review_movie.open()
        create_review_movie.select_movie_by_index(random_movie_index)
        create_review_movie.full_send_review(random_rating, random_review)

        #Проверка текста отзыва
        actual_text = create_review_movie.get_review_text(random_review)
        assert actual_text == random_review, f"Текст отзыва не совпадает. Ожидалось {random_review}, пришло: {actual_text}"
        create_review_movie.alert_was_pop_up()