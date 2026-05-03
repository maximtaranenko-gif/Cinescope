import pytest
import logging
import allure

from db_requester.db_helpers import DBHelper
from entities.user import User
from models.movies_models import MovieModel, MovieUpdate
from soft_assert import assert_equal

logger = logging.getLogger(__name__)


@allure.epic("Cinescope")
@allure.feature("База данных фильмы")
@pytest.mark.api
@pytest.mark.db
@pytest.mark.crud
@pytest.mark.movies
class TestMovieDB:

    @allure.story("Создание фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Создание фильма через API с проверкой в БД")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_create_movie_db_check(self, super_admin: User, db_helper: DBHelper, movie_data: MovieModel):
        with allure.step("Создание фильма через API"):
            api_movie = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = api_movie.id

        with allure.step("Проверка, что фильм появился в БД с корректными данными"):
            db_movie = db_helper.get_movie_by_id(movie_id)
            assert_equal(db_movie.id, api_movie.id, "ID фильма в БД не совпадает")
            assert_equal(db_movie.name, api_movie.name, "Название не совпадает")
            assert_equal(db_movie.price, api_movie.price, "Цена не совпадает")
            assert_equal(db_movie.rating, api_movie.rating, "Рейтинг не совпадает")

        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    @allure.story("Получение фильма")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Получение фильма через API с проверкой соответствия БД")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_movie_db_check(self, super_admin: User, db_helper: DBHelper, movie_data: MovieModel):
        with allure.step("Подготовка: создание фильма"):
            api_movie = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = api_movie.id

        with allure.step("Получение фильма через API и проверка с БД"):
            get_response = super_admin.api.movie_api.get_movie(movie_id, expected_status=200)
            db_movie = db_helper.get_movie_by_id(movie_id)

            assert_equal(get_response.id, db_movie.id, "ID не совпадает")
            assert_equal(get_response.name, db_movie.name, "Название не совпадает")
            assert_equal(get_response.price, db_movie.price, "Цена не совпадает")

        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    @allure.story("Обновление фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Обновление фильма через API с проверкой БД")
    @pytest.mark.regression
    def test_update_movie_db_check(self, super_admin: User, db_helper: DBHelper, movie_data: MovieModel):
        with allure.step("Подготовка: создание фильма"):
            api_movie = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = api_movie.id
            original_price = api_movie.price

        with allure.step("Обновление цены фильма через API"):
            update_data = MovieUpdate(price=original_price + 100)
            super_admin.api.movie_api.update_movie(movie_id, update_data, expected_status=200)

        with allure.step("Проверка обновления цены в БД"):
            db_movie = db_helper.get_movie_by_id(movie_id)
            assert_equal(db_movie.price, update_data.price, "Цена в БД не обновилась")

        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    def test_delete_movie_db(self, super_admin: User, db_helper: DBHelper, movie_data: MovieModel):
        with allure.step("Подготовка данных: создание фильма"):
            api_movie = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = api_movie.id

        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

        with allure.step("Проверка удаления фильма из БД"):
            db_movie = db_helper.get_movie_by_id(movie_id)
            assert_equal(db_movie is None, True, f"Фильм {movie_id} всё ещё существует")