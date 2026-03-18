from constants import USER_CREDS
from conftest import movie_data

class TestMovieAPI:
    def test_delete_movie(self, api_manager, movie_data):
        """Тест на удаление конкретного фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        create_response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        movie_created = create_response.json()
        movie_id = movie_created["id"]
        delete_response = api_manager.movie_api.delete_movie(movie_id, expected_status=200)
        assert delete_response.status_code == 200

        """Вызываем GET-запрос для того чтобы убедиться, что фильм удален"""
        get_response = api_manager.movie_api.get_movie(movie_id, expected_status=404)
        assert get_response.status_code == 404

    def test_incorrect_delete_movie(self, api_manager):
        """Тест на удаление несуществующего фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.delete_movie(1, expected_status=404)
        assert response.status_code == 404

