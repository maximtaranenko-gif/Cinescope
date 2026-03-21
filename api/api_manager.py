from clients.AuthAPI import AuthAPI
from clients.MovieAPI import MovieAPI


class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.movie_api = MovieAPI(session)
