from conftest import created_movie, super_admin
import pytest
import allure
from models.movies_models import MovieResponse, MovieModel, MovieUpdate, MovieCreateReview, MovieUpdateReview, \
    MovieResponseReview
from entities.user import User
from soft_assert import assert_equal


@allure.epic("Cinescope")
@allure.feature("API фильмы")
class TestMovieAPI:
    @allure.story("Изменение фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на изменение фильма")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.change_movies
    @pytest.mark.movies
    def test_change_movie(self, created_movie: MovieResponse, super_admin: User):
        movie_id = created_movie.id
        new_name = MovieUpdate(name="Тест")

        with allure.step(f"Обновляем название фильма на {new_name}"):
            super_admin.api.movie_api.update_movie(movie_id, new_name, expected_status=200)

        with allure.step(f"Получаем название фильма после обновления"):
            get_response = super_admin.api.movie_api.get_movie(movie_id, expected_status=200)

        with allure.step("Проверяем, что изменилось только имя фильма"):
            assert_equal(get_response.name, "Тест", "Ошибка, имя не было изменено")
            assert_equal(get_response.price, created_movie.price, "Ошибка, несовпадение цены")
            assert_equal(get_response.location, created_movie.location, "Ошибка, несовпадение локации")


    @allure.story("Изменение отзывов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: изменение отзыва о фильме")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.change_reviews
    @pytest.mark.movies
    def test_change_movie_review(self, movie_data: MovieModel, super_admin: User):
        with allure.step("Создаем через суперадмина фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = response.id

        create_data = MovieCreateReview(rating=2, text="Кино на любителя")

        with allure.step("Создаём отзыв о фильме"):
            super_admin.api.movie_api.create_review_movie(movie_id, create_data, expected_status=201)
            update_data = MovieUpdateReview(rating=5, text="Пересмотрел, шедевр!")

        with allure.step("Изменяем отзыв о фильме"):
            update_response = super_admin.api.movie_api.change_review_movie(movie_id, update_data, expected_status=200)

        with allure.step("Проверки, что отзыв о фильме был изменен"):
            assert_equal(update_response.rating, 5, "Рейтинг отзыва не был изменён")
            assert_equal(update_response.text, "Пересмотрел, шедевр!", "Текст отзыва не был изменён")

        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    @allure.story("Изменение отзывов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: изменение отзыва с несуществующим movie_id")
    @pytest.mark.negative
    @pytest.mark.change_reviews
    @pytest.mark.movies
    def test_change_movie_review_incorrect_id(self, movie_data: MovieModel, super_admin: User):
        fake_movie_id = 999999999

        with allure.step("Создаем фильм через суперадмина"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = response.id

        with allure.step("Создание и добавление отзыва к фильму"):
            create_data = MovieCreateReview(rating=2, text="Феееее")
            super_admin.api.movie_api.create_review_movie(movie_id, create_data, expected_status=201)

        with allure.step("Обновление отзыва к фильму"):
            update_data = MovieUpdateReview(rating=5, text="Пересмотрел, шедевр!")

        with allure.step("Попытка изменить отзыв у фильма, которого не существует"):
            super_admin.api.movie_api.change_review_movie_raw(fake_movie_id, update_data, expected_status=404)


    @allure.story("Управление видимостью отзывов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: показ скрытого отзыва о фильме")
    @pytest.mark.xfail(reason="Баг в API. Фича показа отзыва работала до изменения API")
    @pytest.mark.positive
    @pytest.mark.review_visibility
    @pytest.mark.movies
    def test_show_movie_review(self, movie_data: MovieModel, super_admin: User):
        user_id = super_admin.id

        with allure.step("Создаем фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = response.id

        with allure.step("Создадим и добавим отзыв о фильме"):
            review_data = MovieCreateReview(rating=3, text="Фильм нереально плох")
            super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        with allure.step("Скрываем отзыв о фильме"):
            hidden_response = super_admin.api.movie_api.hide_review_movie(movie_id, user_id, expected_status=200)
            hidden_response_data = hidden_response.json()
            assert_equal(hidden_response_data.get("hidden"), True, "hidden поле")

        with allure.step("Показываем отзыв о фильме"):
            show_response = super_admin.api.movie_api.show_review_movie(movie_id, user_id, expected_status=200)
            show_response_data = show_response.json()
            assert_equal(show_response_data.get("show"), True, "show поле")

        with allure.step("Удаляем фильм"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    @allure.story("Управление видимостью отзывов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: попытка показать отзыв с несуществующим movie_id")
    @pytest.mark.negative
    @pytest.mark.review_visibility
    @pytest.mark.movies
    def test_show_movie_review_invalid_movie_id(self, super_admin: User):
        fake_movie_id = 999999999
        user_id = "a76b8bf9-af13-45bb-b200-b9db86db26d3"

        with allure.step("Показ отзыва с несуществующим movie_id"):
            super_admin.api.movie_api.show_review_movie(fake_movie_id, user_id, expected_status=404)

    @allure.story("Управление видимостью отзывов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: скрытие отзыва о фильме")
    @pytest.mark.xfail(reason="Баг в API. Фича о скрытия отзыва о фильме работала до изменения Апи")
    @pytest.mark.positive
    @pytest.mark.review_visibility
    @pytest.mark.movies
    def test_hide_movie_review(self, movie_data: MovieModel, super_admin: User):
        user_id = super_admin.id

        with allure.step("Создаем фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = response.id

        review_data = MovieCreateReview(rating=4, text="Фильм неплох")
        with allure.step("Создаем отзыв о фильме"):
            super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        with allure.step("Скрываем отзыв о фильме"):
            hide_response = super_admin.api.movie_api.hide_review_movie(movie_id, user_id, expected_status=200)
            assert_equal(hide_response.get("hidden"), True, "hidden поле")

    @allure.story("Управление видимостью отзывов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: попытка скрыть отзыв с несуществующим movie_id")
    @pytest.mark.negative
    @pytest.mark.review_visibility
    @pytest.mark.movies
    def test_hide_movie_review_invalid_movie_id(self, super_admin: User):
        fake_movie_id = 999999999
        user_id = "a76b8bf9-af13-45bb-b200-b9db86db26d3"

        with allure.step("Попытка скрыть отзыв фильма с несуществующим movie_id"):
            super_admin.api.movie_api.hide_review_movie(fake_movie_id, user_id, expected_status=404)