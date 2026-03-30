from api.api_manager import ApiManager
from conftest import movie_data, faker
import pytest

class TestMovieAPI:
    def test_delete_movie(self, api_manager:ApiManager, movie_data:dict, super_admin):
        """Тест на удаление конкретного фильма"""
        create_response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_created = create_response.json()
        movie_id = movie_created["id"]
        delete_response = super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)
        assert delete_response.status_code == 200

        """Вызываем GET-запрос для того чтобы убедиться, что фильм удален"""
        api_manager.movie_api.get_movie(movie_id, expected_status=404)

    def test_incorrect_delete_movie(self, api_manager:ApiManager, super_admin):
        """Тест на удаление несуществующего фильма"""
        response = super_admin.api.movie_api.delete_movie(1, expected_status=404)
        assert response.status_code == 404

    def test_delete_movie_review(self, api_manager: ApiManager, movie_data:dict,super_admin):
        """Позитивный тест: тест на удаление отзыва об фильме"""
        user_id = super_admin.id

        response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        response_data = response.json()
        review_data = {
            "rating": 4,
            "text": "Фильм нереально хорош"
        }
        movie_id = response_data['id']
        super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)
        super_admin.api.movie_api.delete_review_movie(movie_id,user_id, expected_status=200)
        """Проверка гет запросом на то, что мы ловим 200-ку и пустое тело после удаления отзыва"""
        get_response = super_admin.api.movie_api.get_movie_reviews(movie_id,expected_status=200)
        reviews = get_response.json()
        assert len(reviews) == 0, "Тело ответа должно быть пустым"

    def test_delete_movie_review_not_authorized(self, api_manager: ApiManager, movie_data: dict,super_admin):
        """Негативный тест: попытка удалить отзыв без авторизации"""

        response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = response.json()['id']

        # Создаем отзыв
        review_data = {
            "rating": 5,
            "text": "Хороший фильм"
        }
        super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        user_id = super_admin.id
        # Удаляем токен из сессии
        if "Authorization" in api_manager.session.headers:
            del api_manager.session.headers["Authorization"]

        # Пытаемся удалить отзыв без авторизации
        api_manager.movie_api.delete_review_movie(movie_id, user_id, expected_status=401)

    def test_delete_genre(self, api_manager: ApiManager, super_admin):
        """Позитивный тест: удаление жанра"""
        genre_data = {
            "name": faker.word()
        }
        create_response = super_admin.api.movie_api.create_genres(genre_data, expected_status=201)
        create_data = create_response.json()
        genre_id = create_data["id"]
        super_admin.api.movie_api.delete_genre(genre_id, expected_status=200)
        super_admin.api.movie_api.getting_genre_by_id(genre_id, expected_status=404)

@pytest.mark.parametrize("role, expected_status", [
    ("super_admin", 200),  # супер админ может удалить
    ("admin", 403),  # обычный админ не может
    ("common_user", 403),  # обычный пользователь не может
    ("unauthorized", 401)  # неавторизованный пользователь
], ids=["Super admin can delete", "Admin cannot delete", "Common user cannot delete", "Unauthorized cannot delete"])
def test_delete_movie_permission(api_manager, role, expected_status, super_admin, admin, common_user, movie_data):
    """
    Тест проверки прав доступа на удаление фильма
    Только супер админ может удалять фильмы
    """
    # 1. Супер админ создаёт фильм (который потом будем удалять)
    create_response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
    movie_id = create_response.json()["id"]

    # 2. Выбираем клиента в зависимости от роли
    if role == "super_admin":
        client = super_admin
    elif role == "admin":
        client = admin
    elif role == "common_user":
        client = common_user
    elif role == "unauthorized":
        client = api_manager  # или отдельная сессия без авторизации
    else:
        raise ValueError(f"Unknown role: {role}")

    if role == "unauthorized":
        response = api_manager.movie_api.delete_movie_no_auth(movie_id, expected_status=expected_status)
    else:
        response = client.api.movie_api.delete_movie(movie_id, expected_status=expected_status)

    assert response.status_code == expected_status

    if expected_status == 200:
        get_response = super_admin.api.movie_api.get_movie(movie_id, expected_status=404)
        assert get_response.status_code == 404, "Movie should not exist after deletion"