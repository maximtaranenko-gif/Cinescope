from conftest import movie_data, movie_data_incorrect, multiple_movies, faker, super_admin, common_user
import allure
import pytest
from entities.user import User
from models.movies_models import MovieResponse, MovieModel, MovieCreateReview, MovieCreateGenre, MovieResponseGenre, \
    MovieResponseReview
from soft_assert import assert_equal


@allure.epic("Cinescope")
@allure.feature("API фильмы")
class TestMovieAPI:
    @allure.story("Создание фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на создание фильма")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.create_movie
    @pytest.mark.movies
    def test_create_movie(self, movie_data: MovieModel, super_admin: User):
        with allure.step("Создание фильма"):
            validated_movie = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)


        with allure.step("Проверки"):
            assert_equal(validated_movie.id is not None, True, "ID не должен быть None")
            assert_equal(validated_movie.name, movie_data.name, "Название не совпадает")
            assert_equal(validated_movie.price, movie_data.price, "Цена не совпадает")
            assert_equal(validated_movie.location, movie_data.location, "Локация не совпадает")
            assert_equal(validated_movie.genreId, movie_data.genreId, "Жанр не совпадает")

        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(validated_movie.id, expected_status=200)


    @allure.story("Создание фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на создание нескольких фильмов при помощи фикстуры")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.create_movie
    @pytest.mark.movies
    def test_create_multiple_movies(self, multiple_movies: list[MovieModel], super_admin: User):
        created_ids = []

        with allure.step("Создание фильмов"):
            for movie in multiple_movies:
                validated_movie = super_admin.api.movie_api.create_movie(movie, expected_status=201)
                created_ids.append(validated_movie.id)

                with allure.step("Проверки"):
                    assert_equal(validated_movie.name, movie.name, "Имя фильма не совпадает")
                    assert_equal(validated_movie.price, movie.price, "Цена фильма не совпадает")
                    assert_equal(validated_movie.location, movie.location, "Локация фильма не совпадает")
                    assert_equal(validated_movie.genreId, movie.genreId, "Жанр фильма не совпадает")

            with allure.step("Проверка количества созданных фильмов"):
                assert_equal(len(created_ids), len(multiple_movies), "Создано неверное количество фильмов")

        with allure.step("Удаление фильмов"):
            for movie_id in created_ids:
                super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)


    @allure.story("Создание фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест на создание фильма")
    @pytest.mark.create_movie
    @pytest.mark.negative
    @pytest.mark.movies
    @pytest.mark.xfail(reason="После рефактора кода, Pydantic модель не позволяет генерить заведомо ложные данные")
    def test_incorrect_create_movie(self, movie_data_incorrect: MovieModel, super_admin: User):
        with allure.step("Создание фильма при помощи фикстуры, которая заведомо генерит неверные данные"):
            super_admin.api.movie_api.create_movie(movie_data_incorrect, expected_status=400)


    @allure.story("Отзывы")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на создание отзыва к фильму")
    @pytest.mark.create_review
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.movies
    def test_create_movie_review(self, created_movie: MovieResponse, super_admin: User):
        review_data = MovieCreateReview(rating=1, text="Это смотреть невозможно")

        with allure.step("Создание отзыва к фильму"):
            created_review = super_admin.api.movie_api.create_review_movie(created_movie.id, review_data, expected_status=201)

        with allure.step("Проверка, что отзыв создан"):
            assert_equal(created_review.rating, review_data.rating, "Рейтинг отзыва не совпадает")
            assert_equal(created_review.text, review_data.text, "Текст отзыва не совпадает")
            assert_equal(created_review.userId is not None, True, "ID пользователя не получен")
            assert_equal(created_review.createdAt is not None, True, "Дата создания не получена")


    @allure.story("Жанры")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: создание жанра")
    @pytest.mark.create_genre
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.movies
    def test_create_genre(self, super_admin: User):
        genre_data = MovieCreateGenre(name=faker.word())

        with allure.step("Создание жанра"):
            created_genre = super_admin.api.movie_api.create_genres(genre_data, expected_status=201)

        with allure.step("Проверка, что жанр создан"):
            assert_equal(created_genre.id is not None, True, "ID жанра не получен")
            assert_equal(created_genre.name, genre_data.name, "Название жанра не совпадает")


    @allure.story("Права доступа")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: попытка создать фильм под ролью USER")
    @pytest.mark.create_movie
    @pytest.mark.negative
    @pytest.mark.movies
    def test_create_movies_from_default_user(self, movie_data: MovieModel, common_user: User):
        with allure.step("Создание фильма обычным пользователем"):
            common_user.api.movie_api.create_movie_raw(movie_data, expected_status=403)