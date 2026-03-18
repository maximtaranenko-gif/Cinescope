from conftest import movie_data, movie_data_incorrect
from constants import USER_CREDS


class TestMovieAPI:
    def test_create_movie(self, movie_data, api_manager):
        """Позитивный тест на создание фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        response_data = response.json()
        movie_id = response_data["id"]

        assert response.status_code == 201, "Не удалось создать фильм"

        assert "id" in response_data, "Поле ID отсутствует "
        assert "genre" in response_data, "Поле genre отсутствует "
        assert "name" in response_data["genre"], "У жанра нет имени"

        api_manager.movie_api.delete_movie(movie_id, expected_status=200)

    def test_create_multiple_movies(self, api_manager, multiple_movies):
        """Позитивный тест на создание нескольких фильмов"""
        api_manager.auth_api.authenticate(USER_CREDS)
        created_ids = []

        for movie in multiple_movies:
            response = api_manager.movie_api.create_movie(movie, expected_status=201)
            assert response.status_code == 201
            movie_data = response.json()
            created_ids.append(movie_data["id"])


            assert movie_data["name"] == movie["name"], f"Имя фильма  не совпадает"
            assert movie_data["price"] == movie["price"], f"Цена фильма  не совпадает"
            assert movie_data["location"] == movie["location"], f"Локация фильма  не совпадает"
            assert movie_data["genreId"] == movie["genreId"], f"Жанр фильма не совпадает"
            assert "id" in movie_data

        for movie_id in created_ids:
            api_manager.movie_api.delete_movie(movie_id, expected_status=200)


    def test_incorrect_create_movie(self, movie_data_incorrect, api_manager):
        """Негативный тест на создание фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)
        response = api_manager.movie_api.create_movie(movie_data_incorrect, expected_status=400)

        assert response.status_code == 400, "Некорректные данные"

    def test_incorrect_create_movie_empty_body(self, api_manager):
        """
        Негативный тест пустое тело запроса
        """
        response = api_manager.movie_api.create_movie({}, expected_status=400)
        assert response.status_code == 400, "Некорректные данные"




