from typing import Optional, List

import requests
import allure
from custom_requester.custom_requester import CustomRequester
from constants import MOVIE_ENDPOINT, GENRE_ENDPOINT, MOVIE_URL
from models.movies_models import MovieModel, MovieCreateReview, MovieCreateGenre, MovieReceivingPosters, MovieResponse, \
    MovieUpdate, MovieUpdateReview, MoviesListResponse, MovieResponseReview, MovieResponseGenre, \
    MovieReviewsListResponse, MovieGenreListResponse


class MovieAPI(CustomRequester):
    def __init__(self, session:requests.Session):
        super().__init__(session=session, base_url=f"{MOVIE_URL}")

    @allure.step("Создание фильма")
    def create_movie(self, movie_data: MovieModel, expected_status: int = 201)->MovieResponse:
        """
        Создание фильма
        param movie_data: Данные для создания фильма
        expected_status: Ожидаемый статус код
        """
        with allure.step(f"name movie: {movie_data.name}"):
            response = self.send_request(
                method="POST",
                endpoint=MOVIE_ENDPOINT,
                data = movie_data.model_dump(),
                expected_status=expected_status
            )
            return MovieResponse(**response.json())

    @allure.step("Создание фильма(raw)")
    def create_movie_raw(self, movie_data: MovieModel, expected_status: int = 201):
        """
        Создание фильма(сырой метод без валидации Pydantic)
        param movie_data: Данные для создания фильма
        expected_status: Ожидаемый статус код
        """
        with allure.step(f"name movie: {movie_data.name}"):
            return self.send_request(
                method="POST",
                endpoint=MOVIE_ENDPOINT,
                data = movie_data.model_dump(),
                expected_status=expected_status
            )

    @allure.step("Создание отзыва к фильму: movie_id={movie_id}")
    def create_review_movie(self, movie_id: int, review_data: MovieCreateReview, expected_status: int = 200)->MovieResponseReview:
        """
        Создание отзыва к фильму
        param movie_id: Уникальный индентификатор фильма
        param login_data: Данные для отзыва
        expected_status: Ожидаемый статус
        """
        response = self.send_request(
            method="POST",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews",
            data = review_data.model_dump(),
            expected_status=expected_status
        )
        return MovieResponseReview(**response.json())

    @allure.step("Создание жанра к фильму")
    def create_genres(self, genre_data: MovieCreateGenre, expected_status: int = 200)->MovieResponseGenre:
        """Создание жанра к фильму
        """
        with allure.step(f"Имя жанра: {genre_data.name}"):
            response = self.send_request(
                method="POST",
                endpoint="/genres",
                data = genre_data.model_dump(),
                expected_status = expected_status
            )
            return MovieResponseGenre(**response.json())

    @allure.step("Получение информации о фильме по ID: {movie_id}")
    def get_movie(self, movie_id: int, expected_status: int = 200)->MovieResponse:
        """
        Получение информации о фильме
        :param movie_id: Уникальный индентификатор для фильма
        :param expected_status: Ожидаемый статус код
        """
        response =  self.send_request(
            method="GET",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )
        return MovieResponse(**response.json())

    @allure.step("Получение информации о фильме по ID: {movie_id}")
    def get_movie_raw(self, movie_id: int, expected_status: int = 200):
        """
        Получение информации о фильме
        :param movie_id: Уникальный индентификатор для фильма
        :param expected_status: Ожидаемый статус код
        метод без валидации Pydantic
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )

    @allure.step("Получение отзывов к фильму: movie_id={movie_id}")
    def get_movie_reviews(self, movie_id: int, expected_status: int = 200)->List[MovieResponseReview]:
        """
        Получение информации об отзывах
        :param movie_id: Уникальный индентификатор для отзыва
        :param expected_status: Ожидаемый статус код
        """
        response = self.send_request(
            method="GET",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews",
            expected_status=expected_status
        )
        data = response.json()
        return [MovieResponseReview(**item) for item in data]

    @allure.step("Получение отзывов к фильму: movie_id={movie_id}")
    def get_movie_reviews_raw(self, movie_id: int, expected_status: int = 200):
        """сырой метод без валидации Pydantic
        Получение информации об отзывах
        :param movie_id: Уникальный индентификатор для отзыва
        :param expected_status: Ожидаемый статус код
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews",
            expected_status=expected_status
        )

    @allure.step("Получение афиш фильмов")
    def get_movies_poster(self, params:Optional[MovieReceivingPosters] = None, expected_status: int = 200):
        """
        Получение афиш фильма
        :params page_size:Размер максимальных прогружаемых фильмов(сколько фильмов можно увидеть запросив)
        :params page:Страница афиши
        :params min_price: Минимальная стоимость
        :params max_price: Максимальная стоимость
        :params locations: Местоположение(MSK= Moscow, SPB= Saint Peterburg)
        :params published: Опубликовано(True, False)
        :params genre_id:Жанр фильма(Присваиваются к значениям жанр, например 1= Драма, 2 = Комедия и т.д)
        :params created_at:Дата публикации фильма( ASC - возрастание, DESC - убывание)
        :params expected_status: Ожидаемый статус код
        :return:
        """
        if params is None:
            params = MovieReceivingPosters()

        with allure.step(f"Параметры: page={params.page}, pageSize={params.pageSize}"):
            response = self.send_request(
                method="GET",
                endpoint=MOVIE_ENDPOINT,
                params = params.model_dump(),
                expected_status=expected_status
            )
            return MoviesListResponse(**response.json())

    @allure.step("Получение списка жанров")
    def get_genre_movie(self, expected_status: int = 200)->List[MovieResponseGenre]:
        """Получение жанров фильмов"""
        response =  self.send_request(
            method="GET",
            endpoint=f"{GENRE_ENDPOINT}",
            expected_status = expected_status
        )
        data = response.json()
        return [MovieResponseGenre(**item) for item in data]

    @allure.step("Получение жанра по ID: {genre_id}")
    def getting_genre_by_id(self, genre_id: int, expected_status: int = 200)->MovieResponseGenre:
        """Получение жанра по ID"""
        response = self.send_request(
            method="GET",
            endpoint=f"{GENRE_ENDPOINT}/{genre_id}",
            expected_status= expected_status
        )
        return MovieResponseGenre(**response.json())

    @allure.step("Обновление фильма: movie_id={movie_id}")
    def update_movie(self, movie_id: int, movie_data: MovieUpdate, expected_status: int = 200)->MovieResponse:
        """
        Редактирование фильма
        :param movie_id:Уникальный индентификатор для фильма
        :param movie_data: Данные для фильма
        :param expected_status:Ожидаемый статус код
        """
        response = self.send_request(
            method="PATCH",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}",
            data = movie_data.model_dump(exclude_none=True),
            expected_status=expected_status
        )
        return MovieResponse(**response.json())

    @allure.step("Редактирование отзыва к фильму: movie_id={movie_id}")
    def change_review_movie(self, movie_id: int, movie_data: MovieUpdateReview, expected_status: int = 200)->MovieResponseReview:
        """
        Редактирование отзыва к фильму
        param movie_id: Уникальный индентификатор фильма
        param expected_status: Ожидаемый статус код
        """
        response = self.send_request(
            method="PUT",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews",
            data = movie_data.model_dump(exclude_none=True),
            expected_status= expected_status
        )
        return MovieResponseReview(**response.json())

    @allure.step("Редактирование отзыва к фильму: movie_id={movie_id}")
    def change_review_movie_raw(self, movie_id: int, movie_data: MovieUpdateReview, expected_status: int = 200):
        """
        Редактирование отзыва к фильму
        param movie_id: Уникальный индентификатор фильма
        param expected_status: Ожидаемый статус код
        """
        self.send_request(
            method="PUT",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews",
            data = movie_data.model_dump(exclude_none=True),
            expected_status= expected_status
        )

    @allure.step("Показ отзыва: movie_id={movie_id}, user_id={user_id}")
    def show_review_movie(self, movie_id: int, user_id: str, expected_status: int = 200):
        """Показ отзыва к фильму
        :param movie_id: Уникальный индентификатор фильма
        :param user_id: Уникальный индентификатор юзера
        :param expected_status: Ожидаемый статус код
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews/show/{user_id}",
            expected_status=expected_status
        )

    @allure.step("Скрытие отзыва: movie_id={movie_id}, user_id={user_id}")
    def hide_review_movie(self, movie_id: int, user_id: str, expected_status: int = 200):
        """Скрытие отзыва к фильму
        :param movie_id: Уникальный индентификатор фильма
        :param user_id: Уникальный индентификатор юзера
        :param expected_status: Ожидаемый статус код
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews/hide/{user_id}",
            expected_status=expected_status
        )

    @allure.step("Удаление фильма: movie_id={movie_id}")
    def delete_movie(self, movie_id: int, expected_status: int = 200)->MovieResponse:
        """
        Удаление фильма
        :param movie_id:  Уникальный индентификатор для фильма
        :param expected_status: Ожидаемый статус код
        """
        response = self.send_request(
            method="DELETE",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}",
            expected_status= expected_status
        )
        return MovieResponse(**response.json())

    @allure.step("Удаление фильма: movie_id={movie_id}")
    def delete_movie_raw(self, movie_id: int, expected_status: int = 200):
        """
        Удаление фильма
        :param movie_id:  Уникальный индентификатор для фильма
        :param expected_status: Ожидаемый статус код
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}",
            expected_status= expected_status
        )

    @allure.step("Удаление отзыва: movie_id={movie_id}, user_id={user_id}")
    def delete_review_movie(self, movie_id: int ,user_id: str,expected_status: int = 200)->MovieResponseReview:
        """Удаление отзыва к фильму
        """
        response = self.send_request(
            method="DELETE",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews/",
            params = {"userId": user_id},
            expected_status=expected_status
        )
        return MovieResponseReview(**response.json())

    @allure.step("Удаление отзыва: movie_id={movie_id}, user_id={user_id}")
    def delete_review_movie_raw(self, movie_id: int ,user_id: str,expected_status: int = 200):
        """Удаление отзыва к фильму(метод без валидации Pydantic)
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews/",
            params = {"userId": user_id},
            expected_status=expected_status
        )

    @allure.step("Удаление жанра: genre_id={genre_id}")
    def delete_genre(self, genre_id: int, expected_status: int = 200)->MovieResponseGenre:
        """Удаление жанра фильма"""
        response =  self.send_request(
            method="DELETE",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status
        )
        return MovieResponseGenre(**response.json())