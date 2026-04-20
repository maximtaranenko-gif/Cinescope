from conftest import created_movie
import pytest
import allure

from models.movies_models import MovieResponse


class TestMovieAPI:
    @allure.feature("API фильмы")
    @allure.story("Получение фильмов")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Позитивный тест на получение фильмов с пагинацией")
    def test_get_movies_poster(self, super_admin):
        with allure.step("Получение фильма с фильтром(пагинацией)"):
            response = super_admin.api.movie_api.get_movies_poster(expected_status=200)
        response_data = response.json()
        with allure.step("Проверки"):
            assert "movies" in response_data, "Нет поля movies"
            assert isinstance(response_data["movies"], list), "movies должен быть списком"
            assert len(response_data["movies"]) > 0, "Список фильмов пуст"
            movie = response_data["movies"][0]
            assert "id" in movie, "У фильма нет id"

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Позитивный тест на получение конкретного фильма")
    def test_get_movie(self, super_admin,created_movie:MovieResponse):
        movie_id = created_movie.id
        with allure.step("Получение фильма"):
            response = super_admin.api.movie_api.get_movie(movie_id)
        assert response.status_code == 200, "Некорректный ID"

        response_data = MovieResponse(**response.json())
        with allure.step("Проверки"):
            assert response_data.id == created_movie.id
            assert response_data.name == created_movie.name
            assert response_data.price == created_movie.price

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Негативный тест на поиск несуществующего фильма")
    def test_incorrect_get_movie(self,super_admin):
        with allure.step("Получение фильма"):
            super_admin.api.movie_api.get_movie(1, expected_status=404)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Позитивный тест, проверка на получение отзыва о фильме")
    def test_get_movie_review(self, super_admin,created_movie:MovieResponse):
        movie_id = created_movie.id
        with allure.step("Получение отзыва о фильме"):
            super_admin.api.movie_api.get_movie_reviews(movie_id, expected_status=200)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Негативный тест: получение отзыва о фильме которого не существует")
    def test_get_incorrect_movie_review(self,super_admin, created_movie:MovieResponse):
        movie_id = 9999999
        super_admin.api.movie_api.get_movie_reviews(movie_id, expected_status=404)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Тест на отображение жанров фильмов")
    def test_get_movie_genres(self, super_admin):
        with allure.step("Показ жанров"):
            super_admin.api.movie_api.get_genre_movie(expected_status=200)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Тест на отображение жанра по ID")
    def test_get_genre_by_id(self, super_admin):
        with allure.step("Показ жанров по ID"):
            super_admin.api.movie_api.getting_genre_by_id(1, expected_status=200)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Негативный тест на отображение жанра по ID")
    def test_get_genre_by_incorrect_id(self, super_admin):
        with allure.step("Показ жанров по ID"):
            super_admin.api.movie_api.getting_genre_by_id("f", expected_status=404)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Позитивный тест: Пользователь с ролью USER может получать ответ от сервера с фильмами")
    def test_get_movie_by_default_user(self, super_admin,created_movie:MovieResponse, common_user):
        movie_id = created_movie.id
        with allure.step("Получение фильма через обычного пользователя"):
            common_user.api.movie_api.get_movie(movie_id, expected_status=200)


@pytest.mark.parametrize("price, locations, genreId, expected_status", [
    (500, "SPB", 2, 200),
    (-1, "MSK", 4, 400),
    (998, "TSK", 3, 400),
    (995, "MSK", "lol", 400)
], ids=["Correct data", "incorrect price", "incorrect location", "incorrect data genreId"])
@allure.severity(allure.severity_level.MINOR)
@allure.title("Негативный тест: хардкод данных фильма, с целью проверить параметризацию")
def test_get_movie_pagination(price: int, locations: str, genreId: int, expected_status: int, super_admin):
    response = super_admin.api.movie_api.get_movies_poster(
        minPrice=price,
        maxPrice = 1000,
        locations=locations,
        genreId=genreId,
        expected_status=expected_status
    )
    if expected_status == 200:
        with allure.step("Проверка успешного ответа"):
            data = response.json()
            movies = data.get("movies", [])
            assert len(movies) > 0, "Пустой массив без фильмов"
    else:
        with allure.step("Проверка ошибки"):
            assert response.status_code == expected_status