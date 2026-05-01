import allure
from sqlalchemy.orm import Session
from db_models.user import UserDBModel
from db_models.movies import MoviesDBModel
from models.user_models import UserModel
from models.movies_models import MovieModel
from typing import Optional

class DBHelper:
    def __init__(self, db_session:Session):
        self.db_session = db_session
        """Класс с методами, для работы с БД в тестах"""

    @allure.step("Создание тестового пользователя в БД: {user_data.email}")
    def create_test_user(self, user_data:UserModel)->UserDBModel:
        user_dict = user_data.model_dump(exclude_unset=True)
        user = UserDBModel(**user_dict)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    @allure.step("Получение пользователя по ID: {user_id}")
    def get_user_by_id(self, user_id:str)->Optional[UserDBModel]:
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    @allure.step("Получение пользователя по email: {email}")
    def get_user_by_email(self, email:str)->Optional[UserDBModel]:
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    @allure.step("Проверка существования пользователя по email: {email}")
    def user_exists_by_email(self, email: str) -> bool:
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    @allure.step("Удаление пользователя: {user.id}")
    def delete_user(self, user: UserDBModel)->None:
        self.db_session.delete(user)
        self.db_session.commit()

    @allure.step("Очищение тестовых данных")
    def cleanup_test_data(self, objects_to_delete: list):
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

    @allure.step("Создание тестового фильма в БД: {movie_data.name}")
    def create_test_movie(self, movie_data: MovieModel) -> MoviesDBModel:
        movie_dict = movie_data.model_dump(exclude_unset=True)
        movie = MoviesDBModel(**movie_dict)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    @allure.step("Получение фильма по ID из БД: {movie_id}")
    def get_movie_by_id(self, movie_id: int) -> Optional[MoviesDBModel]:
        return self.db_session.query(MoviesDBModel).filter(MoviesDBModel.id == movie_id).first()

    @allure.step("Проверка существования фильма в БД: {movie_id}")
    def movie_exists_by_id(self, movie_id: int) -> bool:
        return self.db_session.query(MoviesDBModel).filter(MoviesDBModel.id == movie_id).count() > 0

    @allure.step("Получение фильма по названию: {name}")
    def get_movie_by_name(self, name: str) -> Optional[MoviesDBModel]:
        return self.db_session.query(MoviesDBModel).filter(MoviesDBModel.name == name).first()

    @allure.step("Удаление фильма из БД: {movie.name}")
    def delete_movie(self, movie:MoviesDBModel) -> None:
        self.db_session.delete(movie)
        self.db_session.commit()