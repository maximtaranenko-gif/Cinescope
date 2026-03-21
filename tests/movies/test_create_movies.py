from api.api_manager import ApiManager
from conftest import movie_data, movie_data_incorrect, multiple_movies
from constants import ADMIN_CREDS


class TestMovieAPI:
    def test_create_movie(self, movie_data:dict, api_manager:ApiManager):
        """Позитивный тест на создание фильма"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        response_data = response.json()
        movie_id = response_data["id"]

        assert response.status_code == 201, "Не удалось создать фильм"

        assert "id" in response_data, "Поле ID отсутствует "
        assert "genre" in response_data, "Поле genre отсутствует "
        assert "name" in response_data["genre"], "У жанра нет имени"

        api_manager.movie_api.delete_movie(movie_id, expected_status=200)

    def test_create_multiple_movies(self, api_manager:ApiManager, multiple_movies:dict):
        """Позитивный тест на создание нескольких фильмов"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        created_ids = []

        for movie in multiple_movies:
            response = api_manager.movie_api.create_movie(movie, expected_status=201)
            assert response.status_code == 201
            response_data = response.json()
            created_ids.append(response_data["id"])

            assert response_data["name"] == movie["name"], f"Имя фильма  не совпадает"
            assert response_data["price"] == movie["price"], f"Цена фильма  не совпадает"
            assert response_data["location"] == movie["location"], f"Локация фильма  не совпадает"
            assert response_data["genreId"] == movie["genreId"], f"Жанр фильма не совпадает"
            assert "id" in response_data

        assert len(created_ids) == len(multiple_movies), "Создано неверное количество фильмов"
        for movie_id in created_ids:
            api_manager.movie_api.delete_movie(movie_id, expected_status=200)


    def test_incorrect_create_movie(self, movie_data_incorrect:dict, api_manager:ApiManager):
        """Негативный тест на создание фильма"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        api_manager.movie_api.create_movie(movie_data_incorrect, expected_status=400)

    def test_incorrect_create_movie_empty_body(self, api_manager:ApiManager):
        """
        Негативный тест пустое тело запроса
        """
        api_manager.movie_api.create_movie({}, expected_status=400)

    def test_create_moview_review(self, api_manager:ApiManager, created_movie:dict):
        """Позитивный тест на создание отзыва к фильму"""
        movie_data = {
            "rating": 1,
            "text": "Это смотреть невозможно"
        }
        movie_id = created_movie["id"]
        api_manager.movie_api.create_review_movie(movie_id, movie_data, expected_status=201)

    def test_create_moview_review_incorrect_data(self, api_manager:ApiManager, created_movie:dict):
        """Негативный тест: попытка передать в тело запроса невалидные(вместо цифры текст) данные"""
        movie_data = {
            "rating": "Заебись кинцо",
            "text": "У меня биполярное расстройство, кино не очень"
        }
        movie_id = created_movie["id"]
        response = api_manager.movie_api.create_review_movie(movie_id, movie_data, expected_status=400)
        response_data = response.json()
        assert "rating" in str(response_data), "Поле rating должно содержать цифры"

    def test_create_genre(self, api_manager):
        """Негативный тест: создание жанра (нужен суперадмин, у Ромы только ADMIN)"""
        api_manager.auth_api.authenticate(ADMIN_CREDS)
        genre_data = {
            "name": "ABOBA"
        }
        api_manager.movie_api.create_genres(genre_data, expected_status=403)