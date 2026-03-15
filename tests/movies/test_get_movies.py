from constants import USER_CREDS
from conftest import movie_data


class TestMovieAPI:
    def test_get_movies(self, api_manager):
        """Позитивный тест на получение фильмов с пагинацией"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.get_movies_poster()
        assert response.status_code == 200, "Некорректные данные"

        response_data = response.json()
        first_movie = response_data["movies"][0]
        assert "id" in first_movie
        assert first_movie["id"] == 564

    def test_get_movie(self, api_manager, movie_data):
        """Позитивный тест на получение конкретного фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        """Создаем фильм"""
        create_response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        created_movie = create_response.json()
        movie_id = created_movie["id"]

        response = api_manager.movie_api.get_movie(movie_id)
        assert response.status_code == 200, "Некорректный ID"

        response_data = response.json()
        assert response_data["id"] == movie_id
        assert response_data["name"] == movie_data["name"]
        assert response_data["price"] == movie_data["price"]

    def test_incorrect_get_movie(self, api_manager):
        """Негативный тест на поиск несуществующего фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.get_movie(1, expected_status=404)
        assert response.status_code == 404, "Фильм не найден"
