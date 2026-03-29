from clients.AuthAPI import AuthAPI
from clients.MovieAPI import MovieAPI
from clients.UserAPI import UserAPI


class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.movie_api = MovieAPI(session)
        self.user_api = UserAPI(session)

    def close_session(self):
        self.session.close()
