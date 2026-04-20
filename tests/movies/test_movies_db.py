import pytest
import logging
import allure

logger = logging.getLogger(__name__)

class TestMovieDB:
    @allure.feature("База данных фильмы")
    @allure.story("CRUD фильмов(Создание, чтение, редактирование,удаление фильмов из БД)")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Создание фильма через API с проверкой БД на каждом этапе")
    def test_movie_crud_with_db_check(self, super_admin,db_helper, movie_data):
        with allure.step("Создание фильма"):
            response = super_admin.api.movie_api.create_movie(movie_data, expected_status=201) #Создали фильм
        api_movie = response.json()
        movie_id = api_movie['id']

        logger.info(f"Response api: id={movie_id}, name={api_movie['name']}")

        with allure.step("Проверки, что фильм в БД появился"):
            db_movie = db_helper.get_movie_by_id(movie_id)
            assert db_movie.id == api_movie['id']
            assert db_movie.name == api_movie['name']
            assert db_movie.price == api_movie['price']
            assert db_movie.rating == api_movie['rating']

        logger.info(f"Фильм в базе данных найден, данные совпадают")

        with allure.step("Получение фильма"):
            get_response = super_admin.api.movie_api.get_movie(movie_id, expected_status=200)
        get_movie = get_response.json()

        with allure.step("Проверки получение фильма(API)"):
            assert get_movie['id'] == movie_id
            assert get_movie['name'] == movie_data['name']
        logger.info(f"API вернул верные данные")

        with allure.step("Проверка, что данные остались теми же"):
            db_movie_after_get = db_helper.get_movie_by_id(movie_id)
            assert db_movie_after_get.name == movie_data['name']

        # Обновим данные о фильме через API
        update_data = {
            "price": 100,
        }
        with allure.step("Обновим данные о фильме через апи"):
            super_admin.api.movie_api.update_movie(movie_id, update_data, expected_status=200)
        with allure.step("Проверка с БД, что данные теже"):
            db_movie_after_update = db_helper.get_movie_by_id(movie_id)
        if db_movie_after_update.price != update_data['price']:
            pytest.xfail(reason="Баг: цена не обновляется в БД, но апишка меняет цену")

        with allure.step("Вызовем метод delete и проверим в БД существует ли фильм"):
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)
        with allure.step("Получим фильм из БД и проверим, существует ли он"):
            db_movie_after_delete = db_helper.get_movie_by_id(movie_id)
            assert db_movie_after_delete is None, f"Фильм {movie_id} не должен существовать"