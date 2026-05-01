from api.api_manager import ApiManager
from conftest import movie_data, faker
import pytest
import allure
from db_requester.db_helpers import DBHelper
from models.movies_models import MovieModel, MovieResponse, MovieCreateReview, MovieCreateGenre, MovieResponseGenre, MovieResponseReview
from soft_assert import assert_equal
from entities.user import User


@allure.epic("Cinescope")
@allure.feature("API фильмы")
class TestMovieAPI:
    @allure.story("Удаление фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на удаление конкретного фильма с проверкой в БД")
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.db
    @pytest.mark.delete_movie
    @pytest.mark.movies
    def test_delete_movie(self, movie_data: MovieModel, super_admin: User, db_helper: DBHelper):
        with allure.step("Создание и валидация фильма"):
            movie = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = movie.id

        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

        with allure.step("Проверка, что фильм удалён из БД"):
            deleted_movie = db_helper.get_movie_by_id(movie_id)
            assert_equal(deleted_movie is None, True, "Фильм не удалён из БД")


    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Негативный тест на удаление несуществующего фильма")
    @pytest.mark.regression
    @pytest.mark.negative
    @pytest.mark.delete_movie
    @pytest.mark.movies
    def test_incorrect_delete_movie(self, super_admin):
        with allure.step("Удаление несуществующего фильма"):
            super_admin.api.movie_api.delete_movie_raw(1, expected_status=404)


    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: тест на удаление отзыва об фильме")
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.delete_movie
    @pytest.mark.movies
    def test_delete_movie_review(self, movie_data: MovieModel, super_admin: User):
        user_id = super_admin.id

        with allure.step("Создание фильма"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = response.id

        with allure.step("Создание отзыва о фильме"):
            review_data = MovieCreateReview(rating=4, text="Фильм неплох")
            super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        with allure.step("Удаление отзыва о фильме"):
            super_admin.api.movie_api.delete_review_movie(movie_id, user_id, expected_status=200)

        with allure.step("Получение get-запросом информации о отзывах о фильме"):
            super_admin.api.movie_api.get_movie_reviews(movie_id, expected_status=200)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Негативный тест: попытка удалить отзыв без авторизации")
    @pytest.mark.regression
    @pytest.mark.negative
    @pytest.mark.auth
    @pytest.mark.delete_review
    @pytest.mark.movies
    def test_delete_movie_review_not_authorized(self, api_manager: ApiManager, movie_data: MovieModel,super_admin: User):
        with allure.step("Создаем фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = response.id

        with allure.step("Создание отзыва о фильме"):
            review_data = MovieCreateReview(rating=5, text="Отличный фильм!")
            super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        with allure.step("Удаляем токен из сессии"):
            if "Authorization" in api_manager.session.headers:
                del api_manager.session.headers["Authorization"]

        with allure.step("Попытка удалить отзыв без авторизации"):
            api_manager.movie_api.delete_review_movie_raw(movie_id, super_admin.id, expected_status=401)


    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: удаление жанра")
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.delete_genre
    @pytest.mark.movies
    def test_delete_genre(self, super_admin: User):
        genre_data = MovieCreateGenre(name="Абоба")

        with allure.step("Создание и валидация жанра фильма"):
            create_response = super_admin.api.movie_api.create_genres(genre_data, expected_status=201)
            genre_id = create_response.id
            assert_equal(create_response.name, "Абоба", "Ошибка, ожидалось создание имени жанра")

        with allure.step("Удаление жанра"):
            super_admin.api.movie_api.delete_genre(genre_id, expected_status=200)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Тест проверки прав доступа на удаление фильма, только супер админ может удалять фильмы")
    @pytest.mark.slow
    @pytest.mark.regression
    @pytest.mark.movies
    @pytest.mark.parametrize("role, expected_status", [
        pytest.param("super_admin", 200, marks=[pytest.mark.smoke, pytest.mark.slow]),
        pytest.param("admin", 403, marks=[pytest.mark.slow]),
        pytest.param("common_user", 403, marks=[pytest.mark.slow]),
        pytest.param("unauthorized_user", 401, marks=[pytest.mark.slow])
    ], ids=["Super admin can delete", "Admin cannot delete", "Common user cannot delete", "Unauthorized cannot delete"])
    def test_delete_movie_permission(self, role: str, expected_status: int, super_admin: User, admin: User, common_user: User, unauthorized_user: User, movie_data: MovieModel):
        with allure.step("Создание фильма и валидация"):
            create_response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            movie_id = create_response.id

        # 2. Выбираем клиента в зависимости от роли
        match role:
            case "super_admin":
                client = super_admin
            case "admin":
                client = admin
            case "common_user":
                client = common_user
            case _:
                client = unauthorized_user

        response = client.api.movie_api.delete_movie_raw(movie_id, expected_status=expected_status)
        assert response.status_code == expected_status

        if expected_status == 200:
            with allure.step("Проверка, что фильм удален"):
                super_admin.api.movie_api.get_movie_raw(movie_id, expected_status=404)