from api.api_manager import ApiManager
from conftest import movie_data, faker
import pytest
import allure

from db_requester.db_helpers import DBHelper
from models.movies_models import MovieModel, MovieResponse

class TestMovieAPI:
    @allure.feature("API фильмы")
    @allure.story("Удаление фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на удаление конкретного фильма с проверкой в БД")
    def test_delete_movie(self,movie_data:dict, super_admin, db_helper:DBHelper):
        with allure.step("Создание фильма"):
            create_response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        with allure.step("Валидация через Pydantic"):
            validated_movie = MovieResponse(**create_response.json())
        movie_id = validated_movie.id
        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

        with allure.step("Вызываем GET-запрос для того чтобы убедиться, что фильм удален"):
            super_admin.api.movie_api.get_movie(movie_id, expected_status=404)
        with allure.step("Проверка на удаление фильма из БД"):
            deleted_movie = db_helper.get_movie_by_id(movie_id)
            assert deleted_movie is None, "Фильм не удалён из БД"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Негативный тест на удаление несуществующего фильма")
    def test_incorrect_delete_movie(self, super_admin):
        with allure.step("Удаление несуществующего фильма"):
            super_admin.api.movie_api.delete_movie(1, expected_status=404)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: тест на удаление отзыва об фильме")
    def test_delete_movie_review(self,movie_data:dict,super_admin):
        user_id = super_admin.id

        with allure.step("Создаем фильм"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            validated_movie = MovieResponse(**response.json())

        review_data = {
            "rating": 4,
            "text": "Фильм нереально хорош"
        }
        movie_id = validated_movie.id
        with allure.step("Создание отзыва о фильме"):
            super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)
        with allure.step("Удаление отзыва о фильме"):
            super_admin.api.movie_api.delete_review_movie(movie_id,user_id, expected_status=200)
        with allure.step("Получение get-запросом информации о отзывах о фильме"):
            get_response = super_admin.api.movie_api.get_movie_reviews(movie_id,expected_status=200)
        reviews = get_response.json()
        with allure.step("Проверка ответа от сервера"):
            assert len(reviews) == 0, "Тело ответа должно быть пустым"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Негативный тест: попытка удалить отзыв без авторизации")
    def test_delete_movie_review_not_authorized(self, api_manager: ApiManager, movie_data: dict,super_admin):
        with allure.step("Создаем фильм и валидируем через Pydantic"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
            validated_movie = MovieResponse(**response.json())
        movie_id = validated_movie.id
        review_data = {
            "rating": 5,
            "text": "Хороший фильм"
        }
        with allure.step("Создание отзыва о фильме"):
            super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        user_id = super_admin.id
        with allure.step("Удаляем токен из сессии"):
            if "Authorization" in api_manager.session.headers:
                del api_manager.session.headers["Authorization"]

        with allure.step("Попытка удаления токена без авторизации"):
            api_manager.movie_api.delete_review_movie(movie_id, user_id, expected_status=401)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: удаление жанра")
    def test_delete_genre(self, super_admin):
        genre_data = {
            "name": faker.word()
        }
        with allure.step("Создание жанра фильма"):
            create_response = super_admin.api.movie_api.create_genres(genre_data, expected_status=201)
        create_data = create_response.json()
        genre_id = create_data["id"]
        with allure.step("Удаление жанра фильма"):
            super_admin.api.movie_api.delete_genre(genre_id, expected_status=200)
        with allure.step("Получение жанра фильма"):
            super_admin.api.movie_api.getting_genre_by_id(genre_id, expected_status=404)

    @pytest.mark.parametrize("role, expected_status", [
        pytest.param("super_admin", 200, marks=pytest.mark.slow),  # супер админ может удалить
        pytest.param("admin", 403, marks=pytest.mark.slow),  # обычный админ не может
        pytest.param("common_user", 403, marks=pytest.mark.slow),  # обычный пользователь не может
        pytest.param("unauthorized_user", 401, marks=pytest.mark.slow)  # неавторизованный пользователь
    ], ids=["Super admin can delete", "Admin cannot delete", "Common user cannot delete", "Unauthorized cannot delete"])
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Тест проверки прав доступа на удаление фильма, только супер админ может удалять фильмы")
    def test_delete_movie_permission(self, role, expected_status, super_admin, admin, common_user, unauthorized_user, movie_data):
        with allure.step("Создание фильма"):
            create_response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]

        # 2. Выбираем клиента в зависимости от роли
        if role == "super_admin":
            client = super_admin
        elif role == "admin":
            client = admin
        elif role == "common_user":
            client = common_user
        elif role == "unauthorized_user":
            client = unauthorized_user
        else:
            raise ValueError(f"Неизвестная роль: {role}")
        response = client.api.movie_api.delete_movie(movie_id, expected_status=expected_status)

        assert response.status_code == expected_status

        if expected_status == 200:
            with allure.step("Получение фильма"):
                super_admin.api.movie_api.get_movie(movie_id, expected_status=404)