from api.api_manager import ApiManager
from conftest import movie_data, movie_data_incorrect, multiple_movies, faker, super_admin, common_user


class TestMovieAPI:
    def test_create_movie(self, movie_data:dict, api_manager:ApiManager, super_admin):
        """Позитивный тест на создание фильма"""
        response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        response_data = response.json()
        movie_id = response_data["id"]

        assert response.status_code == 201, "Не удалось создать фильм"

        assert "id" in response_data, "Поле ID отсутствует "
        assert "genre" in response_data, "Поле genre отсутствует "
        assert "name" in response_data["genre"], "У жанра нет имени"

        super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    def test_create_multiple_movies(self, api_manager:ApiManager, multiple_movies:dict, super_admin):
        """Позитивный тест на создание нескольких фильмов"""
        created_ids = []

        for movie in multiple_movies:
            response = super_admin.api.movie_api.create_movie(movie, expected_status=201)
            response_data = response.json()
            created_ids.append(response_data["id"])

            assert response_data["name"] == movie["name"], f"Имя фильма  не совпадает"
            assert response_data["price"] == movie["price"], f"Цена фильма  не совпадает"
            assert response_data["location"] == movie["location"], f"Локация фильма  не совпадает"
            assert response_data["genreId"] == movie["genreId"], f"Жанр фильма не совпадает"
            assert "id" in response_data

        assert len(created_ids) == len(multiple_movies), "Создано неверное количество фильмов"
        for movie_id in created_ids:
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)


    def test_incorrect_create_movie(self, movie_data_incorrect:dict, api_manager:ApiManager, super_admin):
        """Негативный тест на создание фильма"""
        super_admin.api.movie_api.create_movie(movie_data_incorrect, expected_status=400)

    def test_incorrect_create_movie_empty_body(self, api_manager:ApiManager, super_admin):
        """
        Негативный тест пустое тело запроса
        """
        super_admin.api.movie_api.create_movie({}, expected_status=400)

    def test_create_moview_review(self, api_manager:ApiManager, created_movie:dict, super_admin):
        """Позитивный тест на создание отзыва к фильму"""
        movie_data = {
            "rating": 1,
            "text": "Это смотреть невозможно"
        }
        movie_id = created_movie["id"]
        super_admin.api.movie_api.create_review_movie(movie_id, movie_data, expected_status=201)

    def test_create_moview_review_incorrect_data(self, api_manager:ApiManager, created_movie:dict, super_admin):
        """Негативный тест: попытка передать в тело запроса невалидные(вместо цифры текст) данные"""
        movie_data = {
            "rating": "Заебись кинцо",
            "text": "У меня биполярное расстройство, кино не очень"
        }
        movie_id = created_movie["id"]
        response = super_admin.api.movie_api.create_review_movie(movie_id, movie_data, expected_status=400)
        response_data = response.json()
        assert "rating" in str(response_data), "Поле rating должно содержать цифры"

    def test_create_genre(self, api_manager, super_admin):
        """Позитивный тест: создание жанра"""
        genre_data = {
            "name": faker.word()
        }
        super_admin.api.movie_api.create_genres(genre_data, expected_status=201)

    def test_create_movies_from_default_user(self, api_manager:ApiManager,movie_data:dict, common_user):
        """
        Негативный тест: попытка создать фильм под ролью USER
        """
        common_user.api.movie_api.create_movie(movie_data, expected_status=403)
