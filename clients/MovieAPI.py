from custom_requester.custom_requester import CustomRequester
from constants import MOVIE_ENDPOINT, GENRE_ENDPOINT, MOVIE_URL


class MovieAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=f"{MOVIE_URL}")

    def create_movie(self, movie_data:dict, expected_status:int = 201):
        """
        Создание фильма
        param movie_data: Данные для создания фильма
        expected_status: Ожидаемый статус код
        """
        return self.send_request(
            method="POST",
            endpoint=MOVIE_ENDPOINT,
            data = movie_data,
            expected_status=expected_status
        )
    def create_review_movie(self, movie_id:int, review_data:dict, expected_status:int = 200):
        """
        Создание отзыва к фильму
        param movie_id: Уникальный индентификатор фильма
        param login_data: Данные для отзыва
        expected_status: Ожидаемый статус
        """
        return self.send_request(
            method="POST",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews",
            data = review_data,
            expected_status=expected_status
        )
    def create_genres(self, genre_data:dict, expected_status:int = 200):
        """Создание жанра к фильму
        """
        return self.send_request(
            method="POST",
            endpoint="/genres",
            data = genre_data,
            expected_status = expected_status
        )
    def get_movie(self, movie_id:int, expected_status:int = 200):
        """
        Получение информации о фильме
        :param movie_id: Уникальный индентификатор для фильма
        :param expected_status: Ожидаемый статус код
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )
    def get_movie_reviews(self, movie_id:int, expected_status:int = 200):
        """
        Получение информации об отзывах
        :param movie_id: Уникальный индентификатор для отзыва
        :param expected_status: Ожидаемый статус код
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews",
            expected_status=expected_status
        )

    def get_movies_poster(self, expected_status:int = 200, **kwargs):
        """
        Получение афиш фильма
        :param page_size:Размер максимальных прогружаемых фильмов(сколько фильмов можно увидеть запросив)
        :param page:Страница афиши
        :param min_price: Минимальная стоимость
        :param max_price: Максимальная стоимость
        :param locations: Местоположение(MSK= Moscow, SPB= Saint Peterburg)
        :param published: Опубликовано(True, False)
        :param genre_id:Жанр фильма(Присваиваются к значениям жанр, например 1= Драма, 2 = Комедия и т.д)
        :param created_at:Дата публикации фильма( ASC - возрастание, DESC - убывание)
        :param expected_status: Ожидаемый статус код
        :return:
        """
        params = {
            "pageSize" : 2,
            "page": 1,
            "minPrice": 50,
            "maxPrice": 1000,
            "locations": "SPB",
            "published": True,
            "genreId": 2,
            "createdAt": "desc"
        }
        params.update(kwargs)
        return self.send_request(
            method="GET",
            endpoint=MOVIE_ENDPOINT,
            params = params,
            expected_status=expected_status
        )
    def get_genre_movie(self, expected_status:int = 200):
        """Получение жанров фильмов"""
        return self.send_request(
            method="GET",
            endpoint=f"{GENRE_ENDPOINT}",
            expected_status = expected_status
        )
    def getting_genre_by_id(self, genre_id:int, expected_status:int = 200):
        """Получение жанра по ID"""
        return self.send_request(
            method="GET",
            endpoint=f"{GENRE_ENDPOINT}/{genre_id}",
            expected_status= expected_status
        )
    def update_movie(self, movie_id:int, movie_data:dict, expected_status:int = 200):
        """
        Редактирование фильма
        :param movie_id:Уникальный индентификатор для фильма
        :param expected_status:Ожидаемый статус код
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}",
            data = movie_data,
            expected_status=expected_status
        )
    def change_review_movie(self, movie_id:int, movie_data:dict, expected_status:int = 200):
        """
        Редактирование отзыва к фильму
        :param movie_id: Уникальный индентификатор фильма
        param expected_status: Ожидаемый статус код
        """
        return self.send_request(
            method="PUT",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews",
            data = movie_data,
            expected_status= expected_status
        )
    def show_review_movie(self, movie_id:int, user_id:str, expected_status = 200):
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
    def hide_review_movie(self, movie_id:int, user_id:str, expected_status = 200):
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
    def delete_movie(self, movie_id:int, expected_status:int = 200):
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
    def delete_review_movie(self, movie_id:int ,user_id:str,expected_status:int = 200):
        """Удаление отзыва к фильму
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIE_ENDPOINT}/{movie_id}/reviews/",
            params = {"userId": user_id},
            expected_status=expected_status
        )
    def delete_genre(self, genre_id:int, expected_status:int = 200):
        """Удаление жанра фильма"""
        return self.send_request(
            method="DELETE",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status
        )