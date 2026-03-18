from conftest import created_movie

class TestMovieAPI:
    def test_change_movie(self, api_manager, created_movie):
        """Негативный тест: """
        movie_id = created_movie["id"]

        response = api_manager.movie_api.update_movie(movie_id, {"name": "Тест"})
        assert response.status_code == 200

        # Проверяем, что название действительно обновилось
        get_response = api_manager.movie_api.get_movie(movie_id)
        movie = get_response.json()
        assert movie["name"] == "Тест"
        # Остальные поля должны остаться без изменений
        assert movie["price"] == created_movie["price"]
        assert movie["location"] == created_movie["location"]

    def test_change_movie_negative_price(self, api_manager, created_movie):
        """Негативный тест: попытка установить отрицательную цену"""
        movie_id = created_movie["id"]
        """Обновляем цену значением"""
        update_data = {"price": -100}
        update_response = api_manager.movie_api.update_movie(movie_id, update_data, expected_status=400)
        assert update_response.status_code == 400, "Некорректные данные"

        get_response = api_manager.movie_api.get_movie(movie_id)
        movie = get_response.json()
        assert movie["price"] == created_movie["price"]

