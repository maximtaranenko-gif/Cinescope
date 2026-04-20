from enum import Enum
from resources.user_creds import SuperAdminCreds
class Roles(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'

AUTH_URL = "https://auth.dev-cinescope.coconutqa.ru"
MOVIE_URL = "https://api.dev-cinescope.coconutqa.ru"
ADMIN_CREDS = (SuperAdminCreds.USERNAME, SuperAdminCreds.PASSWORD)
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
LOGIN_ENDPOINT = "/login"
LOGOUT_ENDPOINT = "/logout"
REGISTER_ENDPOINT = '/register'
REFRESH_TOKEN_ENDPOINT = '/refresh-tokens'
CREATE_USER = '/user'
GET_LIST_USER = '/user'
MOVIE_ENDPOINT = '/movies'
GENRE_ENDPOINT = "/genres"