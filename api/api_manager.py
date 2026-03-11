from clients.AuthAPI import AuthAPI
from clients.UserAPI import UserAPI

class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.user_api = UserAPI(session)
