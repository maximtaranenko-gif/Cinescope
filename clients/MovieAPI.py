from custom_requester.custom_requester import CustomRequester
from constants import MOVIE_ENDPOINT

class MovieAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru")

    def create_movie(self, movie_data, expected_status = 201):
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
    def get_movie(self, movie_id, expected_status = 200):
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
    def get_movies_poster(self, page_size=2, page=1, min_price=50, max_price=5000, locations="SPB", published=True, genre_id=None, created_at="DESC", expected_status = 200):
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
        :return:
        """
        params = {
            "pageSize" : page_size,
            "page": page,
            "min_price": min_price,
            "max_price": max_price,
            "locations": locations,
            "published": published,
            "genreId": genre_id,
            "createdAt": created_at
        }
        return self.send_request(
            method="GET",
            endpoint=MOVIE_ENDPOINT,
            data = params,
            expected_status=expected_status
        )

    def update_movie(self, movie_id, movie_data, expected_status = 200):
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
    def delete_movie(self, movie_id, expected_status = 200):
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