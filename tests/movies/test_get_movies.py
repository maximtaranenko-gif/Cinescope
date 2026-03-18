from constants import USER_CREDS
from conftest import created_movie


class TestMovieAPI:
    def test_get_movies(self, api_manager):
        """Позитивный тест на получение фильмов с пагинацией"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.get_movies_poster()
        assert response.status_code == 200, "Некорректные данные"

        response_data = response.json()
        movie = response_data["movies"][0]

        assert "movies" in response_data, "Нет поля movies"
        assert "id" in movie
        assert isinstance(response_data["movies"], list), "movies должен быть списком"

    def test_get_movie(self, api_manager, created_movie):
        """Позитивный тест на получение конкретного фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        movie_id = created_movie["id"]

        response = api_manager.movie_api.get_movie(movie_id)
        assert response.status_code == 200, "Некорректный ID"

        response_data = response.json()
        assert response_data["id"] == movie_id
        assert response_data["name"] == created_movie["name"]
        assert response_data["price"] == created_movie["price"]

    def test_get_movie_review(self, api_manager,created_movie):
        api_manager.auth_api.authenticate(USER_CREDS)
        """Позитивный тест, проверка на получение отзыва о фильме"""
        response = api_manager.movie_api.get_movie_reviews(created_movie['id'], expected_status=200)
        movie_id = created_movie["id"]
        response = api_manager.movie_api.get_movie_reviews(movie_id)
        assert response.status_code in [200, 404], f"Неожиданный статус: {response.status_code}"

    def test_incorrect_get_movie(self, api_manager):
        """Негативный тест на поиск несуществующего фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.get_movie(1, expected_status=404)
        assert response.status_code == 404, "Фильм не найден"
