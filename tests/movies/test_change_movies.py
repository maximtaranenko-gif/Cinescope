from api.api_manager import ApiManager
from conftest import created_movie, super_admin
from constants import ADMIN_CREDS

class TestMovieAPI:
    def test_change_movie(self, api_manager:ApiManager, created_movie:dict, super_admin):
        """Позитинвый тест: Обновление имени фильма """
        movie_id = created_movie["id"]

        response = super_admin.api.movie_api.update_movie(movie_id, {"name": "Тест"})
        assert response.status_code == 200

        # Проверяем, что название действительно обновилось
        get_response = api_manager.movie_api.get_movie(movie_id)
        movie = get_response.json()
        assert movie["name"] == "Тест"
        # Остальные поля должны остаться без изменений
        assert movie["price"] == created_movie["price"]
        assert movie["location"] == created_movie["location"]

    def test_change_movie_negative_price(self, api_manager:ApiManager, created_movie:dict):
        """Негативный тест: попытка установить отрицательную цену"""
        movie_id = created_movie["id"]
        update_data = {"price": -100}
        api_manager.movie_api.update_movie(movie_id, update_data, expected_status=400)

        get_response = api_manager.movie_api.get_movie(movie_id)
        movie = get_response.json()
        assert movie["price"] == created_movie["price"]

    def test_change_movie_review(self, api_manager: ApiManager, movie_data: dict, super_admin):
        """Позитивный тест: изменение отзыва о фильме"""
        response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        response_data = response.json()
        movie_id = response_data["id"]

        create_data = {
            "rating": 2,
            "text": "Кино на любителя"
        }
        create_response = super_admin.api.movie_api.create_review_movie(movie_id, create_data, expected_status=201)
        create_response.json()

        update_data = {
            "rating": 5,
            "text": "Пересмотрел, шедевр!"
        }
        update_response = super_admin.api.movie_api.change_review_movie(movie_id, update_data, expected_status=200)
        update_response_data = update_response.json()

        assert update_response_data["rating"] == 5
        assert update_response_data["text"] == "Пересмотрел, шедевр!"

        super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    def test_change_movie_review_incorrect_id(self, api_manager: ApiManager, movie_data: dict, super_admin):
        """Негативный тест: изменение отзыва с несуществующим movie_id"""

        response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = response.json()["id"]

        create_data = {
            "rating": 2,
            "text": "Кино на любителя"
        }
        super_admin.api.movie_api.create_review_movie(movie_id, create_data, expected_status=201)

        fake_movie_id = 999999999
        update_data = {
            "rating": 5,
            "text": "Пересмотрел, шедевр!"
        }
        super_admin.api.movie_api.change_review_movie(fake_movie_id, update_data, expected_status=404)

    def test_show_movie_review(self, api_manager: ApiManager, movie_data: dict, super_admin):
        """Позитивный тест: показ скрытого отзыва о фильме"""
        user_id = super_admin.id

        response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = response.json()['id']

        review_data = {
            "rating": 3,
            "text": "Фильм нереально плох"
        }
        super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        # Сначала скрываем отзыв
        hide_response = super_admin.api.movie_api.hide_review_movie(movie_id, user_id, expected_status=200)
        assert hide_response.json().get("hidden") == True

        # Показываем отзыв
        show_response = super_admin.api.movie_api.show_review_movie(movie_id, user_id, expected_status=200)
        show_response_data = show_response.json()

        # Проверяем что отзыв снова виден
        assert show_response_data.get("hidden") == False

        #Удаление фильма
        super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    def test_show_movie_review_invalid_movie_id(self, api_manager: ApiManager, super_admin):
        """Негативный тест: попытка показать отзыв с несуществующим movie_id"""

        fake_movie_id = 999999999
        user_id = "a76b8bf9-af13-45bb-b200-b9db86db26d3"

        super_admin.api.movie_api.show_review_movie(fake_movie_id, user_id, expected_status=404)

    def test_hide_movie_review(self, api_manager: ApiManager, movie_data: dict, super_admin):
        """Позитивный тест: скрытие отзыва о фильме"""
        user_id =super_admin.id

        response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = response.json()['id']

        review_data = {
            "rating": 4,
            "text": "Фильм нереально хорош"
        }
        super_admin.api.movie_api.create_review_movie(movie_id, review_data, expected_status=201)

        hide_response = super_admin.api.movie_api.hide_review_movie(movie_id, user_id, expected_status=200)
        hide_response_data = hide_response.json()

        assert hide_response_data.get("hidden") == True

    def test_hide_movie_review_invalid_movie_id(self, api_manager: ApiManager, super_admin):
        """Негативный тест: попытка скрыть отзыв с несуществующим movie_id"""

        fake_movie_id = 999999999
        user_id = "a76b8bf9-af13-45bb-b200-b9db86db26d3"

        super_admin.api.movie_api.hide_review_movie(fake_movie_id, user_id, expected_status=404)

