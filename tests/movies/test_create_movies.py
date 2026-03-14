from api.api_manager import ApiManager
from conftest import ApiManager, movie_data, movie_data_incorrect
from constants import USER_CREDS


class TestMovieAPI:
    def test_create_movie(self, movie_data, api_manager):
        """Тест на создание фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        response_data = response.json()

        assert response.status_code == 201, "Не удалось создать фильм"

        assert "id" in response_data, "Поле ID отсутствует "
        assert "genre" in response_data, "Поле genre отсутствует "
        assert "name" in response_data["genre"], "У жанра нет имени"

    def test_create_multiple_movies(self, api_manager, multiple_movies):
        api_manager.auth_api.authenticate(USER_CREDS)

        for movie in multiple_movies:  # ← уже готовые разные фильмы
            response = api_manager.movie_api.create_movie(movie, expected_status=201)
            assert response.status_code == 201


    def test_incorrect_create_movie(self, movie_data_incorrect, api_manager):
        """Тест на создание фильма(негатив)"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.create_movie(movie_data_incorrect, expected_status=400)

        assert response.status_code == 400


