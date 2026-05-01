from conftest import created_movie
import pytest
import allure
from entities.user import User
from models.movies_models import MovieResponse, MovieReceivingPosters
from soft_assert import assert_equal


@allure.epic("Cinescope")
@allure.feature("API фильмы")
@pytest.mark.api
@pytest.mark.movies
@pytest.mark.get_movies
class TestMovieAPI:
    @allure.story("Получение фильмов")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Позитивный тест на получение фильмов с пагинацией")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.pagination
    @pytest.mark.movies
    def test_get_movies_poster(self, super_admin: User):
        with allure.step("Получение фильма с фильтром (пагинация)"):
            movies_list = super_admin.api.movie_api.get_movies_poster(expected_status=200)

        with allure.step("Проверки структуры ответа"):
            assert_equal(len(movies_list.movies) > 0, True, "Список фильмов пуст")
            assert_equal(movies_list.movies[0].id is not None, True, "У фильма нет id")

    @allure.story("Получение фильмов")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Позитивный тест на получение конкретного фильма")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.get_movie
    @pytest.mark.movies
    def test_get_movie(self, super_admin: User, created_movie: MovieResponse):
        movie_id = created_movie.id

        with allure.step("Получение фильма"):
            movie = super_admin.api.movie_api.get_movie(movie_id, expected_status=200)

        with allure.step("Валидация и проверка ответа"):
            assert_equal(movie.id, created_movie.id, "ID не совпадает")
            assert_equal(movie.name, created_movie.name, "Название не совпадает")
            assert_equal(movie.price, created_movie.price, "Цена не совпадает")

    @allure.story("Получение фильмов")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Негативный тест на поиск несуществующего фильма")
    @pytest.mark.negative
    @pytest.mark.get_movie
    @pytest.mark.movies
    def test_incorrect_get_movie(self, super_admin: User):
        with allure.step("Получение несуществующего фильма"):
            super_admin.api.movie_api.get_movie_raw(1, expected_status=404)

    @allure.story("Отзывы")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Позитивный тест: получение отзыва о фильме")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.get_review_movie
    @pytest.mark.movies
    def test_get_movie_review(self, super_admin: User, created_movie: MovieResponse):
        movie_id = created_movie.id
        with allure.step("Получение отзыва о фильме"):
            super_admin.api.movie_api.get_movie_reviews(movie_id, expected_status=200)

    @allure.story("Отзывы")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Негативный тест: получение отзыва о фильме, которого не существует")
    @pytest.mark.negative
    @pytest.mark.get_review_movie
    @pytest.mark.movies
    def test_get_incorrect_movie_review(self, super_admin: User, created_movie: MovieResponse):
        fake_movie_id = 9999999
        with allure.step("Получение отзыва по несуществующему ID"):
            super_admin.api.movie_api.get_movie_reviews_raw(fake_movie_id, expected_status=404)

    @allure.story("Жанры")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Тест на отображение жанров фильмов")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.get_list_genres
    @pytest.mark.movies
    def test_get_movie_genres(self, super_admin: User):
        with allure.step("Получение списка жанров"):
            super_admin.api.movie_api.get_genre_movie(expected_status=200)

    @allure.story("Жанры")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Тест на отображение жанра по ID")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.get_genre
    @pytest.mark.movies
    def test_get_genre_by_id(self, super_admin: User):
        with allure.step("Получение жанра по ID"):
            super_admin.api.movie_api.getting_genre_by_id(1, expected_status=200)

    @allure.story("Права доступа")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Позитивный тест: пользователь с ролью USER может получать фильмы")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.auth
    @pytest.mark.get_movie
    @pytest.mark.movies
    def test_get_movie_by_default_user(self, super_admin: User, created_movie: MovieResponse, common_user: User):
        movie_id = created_movie.id
        with allure.step("Получение фильма через обычного пользователя"):
            common_user.api.movie_api.get_movie(movie_id, expected_status=200)

@pytest.mark.parametrize("price, locations, genreId, expected_status", [
    pytest.param(500, "SPB", 2, 200, id="Correct data"),
    pytest.param(-1, "MSK", 4, 400, id="Incorrect price"),
    pytest.param(998, "TSK", 3, 400, id="Incorrect location"),
    pytest.param(995, "MSK", "lol", 400, id="Incorrect genreId type")
])
@allure.severity(allure.severity_level.MINOR)
@allure.title("Параметризованный тест фильтрации фильмов")
@allure.story("Фильтрация")
@pytest.mark.parametrized
@pytest.mark.filter_tests
@pytest.mark.movies
@pytest.mark.xfail(reason="После рефакторинга не работает негатив кейс связанный с genreId(Pydantic модель делает это в методе)")
def test_get_movie_pagination(price: int, locations: str, genreId, expected_status: int, super_admin: User):
    with allure.step(f"Запрос с параметрами: price={price}, location={locations}, genreId={genreId}"):
        params = MovieReceivingPosters(
            minPrice=price,
            maxPrice=1000,
            locations=locations,
            genreId=genreId
        )
        response = super_admin.api.movie_api.get_movies_poster(params, expected_status=expected_status)

    if expected_status == 200:
        with allure.step("Проверка успешного ответа"):
            data = response.model_dump()
            movies = data.get("movies", [])
            assert_equal(len(movies) > 0, True, "Список фильмов пуст")
    else:
        with allure.step("Проверка ошибки"):
            assert_equal(response.status_code, expected_status, "Статус код не соответствует ожидаемому")