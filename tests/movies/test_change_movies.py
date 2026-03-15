from conftest import movie_data, movie_data_incorrect
from constants import USER_CREDS

class TestMovieAPI:
    def test_change_movie(self, api_manager, movie_data):
        """Тест на изменение фильма"""
        api_manager.auth_api.authenticate(USER_CREDS)

        create_response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        created_movie = create_response.json()
        movie_id = created_movie["id"]

        update_data = movie_data.copy()
        update_data["name"] = "ОБНОВЛЕННЫЙ: " + movie_data["name"][:30]
        update_data["price"] = movie_data["price"] + 500
        update_data["published"] = not movie_data["published"]

        update_response = api_manager.movie_api.update_movie(movie_id, update_data, expected_status=200)
        assert update_response.status_code == 200

        get_response = api_manager.movie_api.get_movie(movie_id)
        updated_movie = get_response.json()

        assert updated_movie["name"] == update_data["name"]
        assert updated_movie["price"] == update_data["price"]
        assert updated_movie["published"] == update_data["published"]

        assert updated_movie["id"] == movie_id

        api_manager.movie_api.delete_movie(movie_id, expected_status=200)

    def test_change_movie_negative_price(self, api_manager, movie_data):
        """Негативный тест: попытка установить отрицательную цену"""
        api_manager.auth_api.authenticate(USER_CREDS)
        """Создаем фильм"""
        create_response = api_manager.movie_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]
        """Обновляем цену значением"""
        update_data = {"price": -100}
        update_response = api_manager.movie_api.update_movie(movie_id, update_data, expected_status=400)
        assert update_response.status_code == 400, "Некорректные данные"

        get_response = api_manager.movie_api.get_movie(movie_id)
        movie = get_response.json()
        assert movie["price"] == movie_data["price"]

        api_manager.movie_api.delete_movie(movie_id, expected_status=200)
