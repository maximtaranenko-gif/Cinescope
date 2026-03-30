from api.api_manager import ApiManager
from conftest import created_movie
import pytest

class TestMovieAPI:
    def test_get_movies_poster(self, api_manager:ApiManager, super_admin):
        """Позитивный тест на получение фильмов с пагинацией"""
        response = super_admin.api.movie_api.get_movies_poster()
        assert response.status_code == 200, "Некорректные данные"

        response_data = response.json()
        assert "movies" in response_data, "Нет поля movies"
        assert isinstance(response_data["movies"], list), "movies должен быть списком"
        assert len(response_data["movies"]) > 0, "Список фильмов пуст"
        movie = response_data["movies"][0]
        assert "id" in movie, "У фильма нет id"

    def test_get_movie(self, api_manager:ApiManager, created_movie:dict):
        """Позитивный тест на получение конкретного фильма"""
        movie_id = created_movie["id"]
        response = api_manager.movie_api.get_movie(movie_id)
        assert response.status_code == 200, "Некорректный ID"

        response_data = response.json()
        assert response_data["id"] == movie_id
        assert response_data["name"] == created_movie["name"]
        assert response_data["price"] == created_movie["price"]

    def test_incorrect_get_movie(self, api_manager:ApiManager, super_admin):
        """Негативный тест на поиск несуществующего фильма"""
        super_admin.api.movie_api.get_movie(1, expected_status=404)

    def test_get_movie_review(self, api_manager:ApiManager,created_movie:dict):
        """Позитивный тест, проверка на получение отзыва о фильме"""
        movie_id = created_movie["id"]
        api_manager.movie_api.get_movie_reviews(movie_id, expected_status=200)

    def test_get_incorrect_movie_review(self, api_manager:ApiManager, created_movie:dict):
        """Негативный тест: получение отзыва о фильме которого не существует"""
        movie_id = 9999999
        api_manager.movie_api.get_movie_reviews(movie_id, expected_status=404)

    def test_get_movie_genres(self, api_manager:ApiManager):
        """Тест на отображение жанров фильмов"""
        api_manager.movie_api.get_genre_movie(expected_status=200)

    def test_get_genre_by_id(self, api_manager: ApiManager):
        """Тест на отображение жанра по ID"""
        api_manager.movie_api.getting_genre_by_id(1, expected_status=200)

    def test_get_genre_by_incorrect_id(self, api_manager:ApiManager):
        """Негативный тест на отображение жанра по ID"""
        api_manager.movie_api.getting_genre_by_id("f", expected_status=404)

    def test_get_movie_by_default_user(self, api_manager:ApiManager,created_movie:dict, common_user):
        """Позитивный тест: Пользователь с ролью USER может получать ответ от сервера с фильмами"""
        movie_id = created_movie["id"]
        common_user.api.movie_api.get_movie(movie_id, expected_status=200)


@pytest.mark.parametrize("price, locations, genreId, expected_status", [
    (500, "SPB", 2, 200),
    (-1, "MSK", 4, 400),
    (998, "TSK", 3, 400),
    (995, "MSK", "lol", 400)
], ids=["Correct data", "incorrect price", "incorrect location", "incorrect data genreId"])
def test_get_movie_pagination(price: int, locations: str, genreId: int, expected_status: int, api_manager: ApiManager, ):
    response = api_manager.movie_api.get_movies_poster(
        minPrice=price,
        maxPrice = 1000,
        locations=locations,
        genreId=genreId,
        expected_status=expected_status
    )
    if expected_status == 200:
        data = response.json()
        movies = data.get("movies", [])
        assert len(movies) > 0, "Пустой массив без фильмов"