from conftest import created_movie, super_admin
from pytest_check import check
import pytest
import allure
from models.movies_models import MovieResponse, MovieModel
from entities.user import User


class TestMovieAPI:
    @allure.feature("API фильмы")
    @allure.story("Изменение фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на  изменения фильма")
    def test_change_movie(self, created_movie:MovieModel, super_admin:User):
        movie_id = created_movie.id
        new_name = {"name":"Тест"}
        with allure.step(f"Обновляем название фильма на {new_name}"):
            super_admin.api.movie_api.update_movie(movie_id, new_name, expected_status=200)

        with allure.step(f"Получаем название фильма после обновления"):
            get_response = super_admin.api.movie_api.get_movie(movie_id, expected_status=200)
        with allure.step("Валидация ответа через Pydantic"):
            movie = get_response.json()
            validated_movie = MovieResponse(**movie)

        with allure.step("Проверяем , что изменилось только имя фильма"):
            check.equal(validated_movie.name, "Тест")
            check.equal(validated_movie.price, created_movie.price)
            check.equal(validated_movie.location, created_movie.location)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: Попытка установки отрицательной цены для фильма")
    def test_change_movie_negative_price(self, super_admin:User, created_movie:MovieModel):
        movie_id = created_movie.id
        update_data = {"price": -100}
        with allure.step("Обновляем цену фильма"):
            super_admin.api.movie_api.update_movie(movie_id, update_data, expected_status=400)

        with allure.step("Получаем сам фильм после попытки обновить цену"):
            get_response = super_admin.api.movie_api.get_movie(movie_id, expected_status=200)

        with allure.step("Валидация через Pydantic"):
            movie = get_response.json()
            validated_movie = MovieResponse(**movie)

        with allure.step("Проверяем, что цена осталась той же, как и при создании фильма"):
            assert validated_movie.price== created_movie.price

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: изменение отзыва о фильме")
    def test_change_movie_review(self, movie_data: dict, super_admin:User):
        with allure.step("Создаем через суперадмина фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)

        response_data = response.json()
        movie_id = response_data["id"]
        create_data = {
            "rating": 2,
            "text": "Кино на любителя"
        }
        with allure.step("Шаг 1: Сначала создадим отзыв о фильме")    :
            super_admin.api.movie_api.create_review_movie(movie_id, create_data, expected_status=201)
        update_data = {
            "rating": 5,
            "text": "Пересмотрел, шедевр!"
        }
        with allure.step("Изменяем отзыв о фильме"):
            update_response = super_admin.api.movie_api.change_review_movie(movie_id, update_data, expected_status=200)
        update_response_data = update_response.json()
        with allure.step("Проверки, что отзыв о фильме был изменен"):
            assert update_response_data["rating"] == 5
            assert update_response_data["text"] == "Пересмотрел, шедевр!"
        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: изменение отзыва с несуществующим movie_id")
    def test_change_movie_review_incorrect_id(self, movie_data: dict, super_admin):
        with allure.step("Создаем фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = response.json()["id"]

        create_data = {
            "rating": 2,
            "text": "Кино на любителя"
        }
        with allure.step("Добавляем отзыв к фильму"):
            super_admin.api.movie_api.create_review_movie(movie_id, create_data, expected_status=201)

        fake_movie_id = 999999999
        update_data = {
            "rating": 5,
            "text": "Пересмотрел, шедевр!"
        }
        with allure.step("Попытка изменить отзыв у фильма, которого не существует"):
            super_admin.api.movie_api.change_review_movie(fake_movie_id, update_data, expected_status=404)

    @pytest.mark.xfail(reason="Баг в API. Фича показа скрытого отзыва работала до изменения API")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: показ скрытого отзыва о фильме")
    def test_show_movie_review(self, movie_data: dict, super_admin):
        user_id = super_admin.id
        with allure.step("Создаем фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = response.json()['id']

        review_data = {
            "rating": 3,
            "text": "Фильм нереально плох"
        }
        with allure.step("Создадим отзыв о фильме"):
            super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        with allure.step("Скрываем отзыв о фильме"):
            hide_response = super_admin.api.movie_api.hide_review_movie(movie_id, user_id, expected_status=200)
        assert hide_response.json().get("hidden") == True

        with allure.step("Показываем отзыв о фильме"):
            show_response = super_admin.api.movie_api.show_review_movie(movie_id, user_id, expected_status=200)
        show_response_data = show_response.json()

        with allure.step("Проверяем что отзыв снова виден"):
            assert show_response_data.get("hidden") == False

        with allure.step("Удаляем фильм"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: попытка показать отзыв с несуществующим movie_id")
    def test_show_movie_review_invalid_movie_id(self, super_admin):
        fake_movie_id = 999999999
        user_id = "a76b8bf9-af13-45bb-b200-b9db86db26d3"
        with allure.step("Показ отзыва с несуществующим movie_id"):
            super_admin.api.movie_api.show_review_movie(fake_movie_id, user_id, expected_status=404)

    @pytest.mark.xfail(reason="Баг в API. Фича о скрытия отзыва о  фильме работала до изменения Апи")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: скрытие отзыва о фильме")
    def test_hide_movie_review(self, movie_data: dict, super_admin):
        user_id =super_admin.id

        with allure.step("Создаем фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = response.json()['id']

        review_data = {
            "rating": 4,
            "text": "Фильм нереально хорош"
        }
        with allure.step("Создаем отзыв о фильме"):
            super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)
        with allure.step("Скрываем отзыв о фильме"):
            hide_response = super_admin.api.movie_api.hide_review_movie(movie_id, user_id, expected_status=200)
        hide_response_data = hide_response.json()

        assert hide_response_data.get("hidden") == True

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: попытка скрыть отзыв с несуществующим movie_id")
    def test_hide_movie_review_invalid_movie_id(self, super_admin):
        fake_movie_id = 999999999
        user_id = "a76b8bf9-af13-45bb-b200-b9db86db26d3"
        with allure.step("Попытка скрыть отзыв фильма с несуществующим movie_id"):
            super_admin.api.movie_api.hide_review_movie(fake_movie_id, user_id, expected_status=404)

