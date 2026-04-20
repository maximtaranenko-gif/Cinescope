from conftest import movie_data, movie_data_incorrect, multiple_movies, faker, super_admin, common_user
import allure
from pytest_check import check
from models.movies_models import MovieResponse, MovieModel


class TestMovieAPI:
    @allure.feature("API фильмы")
    @allure.story("Создание фильмов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на  создание фильма")
    def test_create_movie(self, movie_data:dict, super_admin):
        with allure.step("Создание фильма"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)

        with allure.step("Валидация ответа через Pydantic"):
            validated_movie = MovieResponse(**response.json())

        with allure.step("Проверки"):
            assert validated_movie.id is not None, "ID не должен быть None"
            assert validated_movie.name == movie_data["name"], "Название не совпадает"
            assert validated_movie.price == movie_data["price"], "Цена не совпадает"
            assert validated_movie.location == movie_data["location"], "Локация не совпадает"
            assert validated_movie.genreId == movie_data["genreId"], "Жанр не совпадает"
        with allure.step("Удаление фильма"):
            super_admin.api.movie_api.delete_movie(validated_movie.id, expected_status=200)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на создание нескольких фильмов при помощи фикстуры")
    def test_create_multiple_movies(self, multiple_movies:dict, super_admin):
        created_ids = []
        with allure.step("Создание фильмов"):
            for movie in multiple_movies:
                response = super_admin.api.movie_api.create_movie(movie, expected_status=201)

                with allure.step("Валидация ответа через Pydantic"):
                    validated_movie = MovieResponse(**response.json())

                created_ids.append(validated_movie.id)
                with check:
                    check.equal(validated_movie.name, movie["name"], f"Имя фильма  не совпадает")
                    check.equal(validated_movie.price, movie["price"], f"Цена фильма  не совпадает")
                    check.equal(validated_movie.location, movie["location"], f"Локация фильма  не совпадает")
                    check.equal(validated_movie.genreId,movie["genreId"], f"Жанр фильма не совпадает")

            with allure.step("Проверка на создание количества фильмов(можно только 3)"):
                assert len(created_ids) == len(multiple_movies), "Создано неверное количество фильмов"
        with allure.step("Удаление фильмов"):
            for movie_id in created_ids:
                super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест на создание фильма")
    def test_incorrect_create_movie(self, movie_data_incorrect:dict, super_admin):
        with allure.step("Создание фильма при помощи фикстуры, которая заведомо генерит неверные данные"):
            super_admin.api.movie_api.create_movie(movie_data_incorrect, expected_status=400)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест пустое тело запроса")
    def test_incorrect_create_movie_empty_body(self,super_admin):
        with allure.step("Создание фильма с пустым телом запроса"):
            super_admin.api.movie_api.create_movie({}, expected_status=400)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест на создание отзыва к фильму")
    def test_create_movie_review(self,created_movie:MovieModel, super_admin):
        movie_data = {
            "rating": 1,
            "text": "Это смотреть невозможно"
        }
        movie_id = created_movie.id
        with allure.step("Создание отзыва к фильму"):
         super_admin.api.movie_api.create_review_movie(movie_id, movie_data, expected_status=201)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: попытка передать в тело запроса невалидные(вместо цифры текст) данные")
    def test_create_movie_review_incorrect_data(self, created_movie:MovieModel, super_admin):
        movie_data = {
            "rating": "Заебись кинцо",
            "text": "У меня биполярное расстройство, кино не очень"
        }
        movie_id = created_movie.id
        with allure.step(" Создание отзыва к фильму"):
            response = super_admin.api.movie_api.create_review_movie(movie_id, movie_data, expected_status=400)
        response_data = response.json()
        with allure.step("Проверка поле rating"):
            error_str = str(response_data).lower()
            check.is_in("rating", error_str, "Ошибка должна упоминать поле rating")
            check.is_in("числом", error_str, "Ошибка должна упоминать числовой формат rating")

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Позитивный тест: создание жанра")
    def test_create_genre(self, super_admin):
        genre_data = {
            "name": faker.word()
        }
        with allure.step("Создание жанра"):
            super_admin.api.movie_api.create_genres(genre_data, expected_status=201)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Негативный тест: попытка создать фильм под ролью USER")
    def test_create_movies_from_default_user(self, movie_data:dict, common_user):
        with allure.step("Создание фильма"):
            common_user.api.movie_api.create_movie(movie_data, expected_status=403)
