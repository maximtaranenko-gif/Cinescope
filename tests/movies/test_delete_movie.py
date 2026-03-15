from constants import USER_CREDS
from conftest import movie_data, movie_data_incorrect

class TestMovieAPI:
    def test_delete_movie(self, api_manager, movie_data):
        """Тест на удаление конкретного фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        """Создаем фильм и вытягиваем ID из ответа """
        create_response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        created_movie = create_response.json()
        movie_id = created_movie["id"]
        """Удаляем фильм по полученному ID"""
        delete_response = api_manager.movie_api.delete_movie(movie_id, expected_status=200)
        assert delete_response.status_code == 200, "Фильм не был найден"

        """Вызываем GET-запрос для того чтобы убедиться, что фильм удален"""
        get_response = api_manager.movie_api.get_movie(movie_id, expected_status=404)
        assert get_response.status_code == 404

    def test_incorrect_delete_movie(self, api_manager):
        """Тест на удаление несуществующего фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.delete_movie(1, expected_status=404)
        assert response.status_code == 404

