from api.api_manager import ApiManager
from constants import ADMIN_CREDS
from conftest import movie_data

class TestMovieAPI:
    def test_delete_movie(self, api_manager:ApiManager, movie_data:dict):
        """Тест на удаление конкретного фильма"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        create_response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        movie_created = create_response.json()
        movie_id = movie_created["id"]
        delete_response = api_manager.movie_api.delete_movie(movie_id, expected_status=200)
        assert delete_response.status_code == 200

        """Вызываем GET-запрос для того чтобы убедиться, что фильм удален"""
        api_manager.movie_api.get_movie(movie_id, expected_status=404)

    def test_incorrect_delete_movie(self, api_manager:ApiManager):
        """Тест на удаление несуществующего фильма"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        response = api_manager.movie_api.delete_movie(1, expected_status=404)
        assert response.status_code == 404

    def test_delete_movie_review(self, api_manager: ApiManager, movie_data:dict,):
        """Позитивный тест: тест на удаление отзыва об фильме"""
        auth_response = api_manager.auth_api.authenticate(ADMIN_CREDS)
        user_id = auth_response["user"]["id"]

        response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        response_data = response.json()
        review_data = {
            "rating": 4,
            "text": "Фильм нереально хорош"
        }
        movie_id = response_data['id']
        api_manager.movie_api.create_review_movie(movie_id, review_data, expected_status=201)
        api_manager.movie_api.delete_review_movie(movie_id,user_id, expected_status=200)
        """Проверка гет запросом на то, что мы ловим 200-ку и пустое тело после удаления отзыва"""
        get_response = api_manager.movie_api.get_movie_reviews(movie_id,expected_status=200)
        reviews = get_response.json()
        assert len(reviews) == 0, "Тело ответа должно быть пустым"

    def test_delete_movie_review_not_authorized(self, api_manager: ApiManager, movie_data: dict):
        """Негативный тест: попытка удалить отзыв без авторизации"""

        api_manager.auth_api.authenticate(ADMIN_CREDS)
        response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = response.json()['id']

        # Создаем отзыв
        review_data = {
            "rating": 5,
            "text": "Хороший фильм"
        }
        api_manager.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        auth_response = api_manager.auth_api.authenticate(ADMIN_CREDS)
        user_id = auth_response["user"]["id"]
        # Удаляем токен из сессии
        if "Authorization" in api_manager.session.headers:
            del api_manager.session.headers["Authorization"]

        # Пытаемся удалить отзыв без авторизации
        api_manager.movie_api.delete_review_movie(movie_id, user_id, expected_status=401)

    def test_delete_genre(self, api_manager: ApiManager):
        """Негативный тест: удаление жанра(Здесь та же самая история, нужен суперадмин, у Ромы только ADMIN)"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        api_manager.movie_api.delete_genre(5, expected_status=403)