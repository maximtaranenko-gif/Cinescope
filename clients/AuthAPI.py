from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT, LOGOUT_ENDPOINT, REFRESH_TOKEN_ENDPOINT, CREATE_USER, \
    GET_LIST_USER
from custom_requester.custom_requester import CustomRequester
from constants import AUTH_URL


class AuthAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session,base_url=f"{AUTH_URL}")


    def register_user(self, user_data:dict, expected_status:int = 201):
        """Register user"""
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data = user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data:dict, expected_status:int = 200):
        """Login user"""
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data = login_data,
            expected_status=expected_status
        )
    def create_user(self, login_data:dict, expected_status:int = 200):
        """create user"""
        return self.send_request(
            method="POST",
            data = login_data,
            endpoint=CREATE_USER,
            expected_status= expected_status
        )
    def get_list_user(self,expected_status:int = 200, **kwargs):
        list_user = {
            "pageSize":10,
            "page": 1,
            "roles": ["USER"],
            "createdAt": "ASC"
        }
        list_user.update(kwargs)
        return self.send_request(
            method="GET",
            data = list_user,
            endpoint=GET_LIST_USER,
            expected_status= expected_status
        )

    def logout_user(self, expected_status:int = 200):
        """Logout user"""
        return self.send_request(
            method="GET",
            endpoint=LOGOUT_ENDPOINT,
            expected_status = expected_status
        )
    def refresh_token(self, expected_status:int = 200):
        """refresh-token user"""
        return self.send_request(
            method = "GET",
            endpoint=REFRESH_TOKEN_ENDPOINT,
            expected_status= expected_status
        )
    def get_user_info(self, user_id:int, expected_status:int=200):
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )
    def delete_user(self,user_id:int, expected_status:int=204):
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )
    def change_user_info(self, user_id:int, update_data:dict, expected_status:int = 403):
        return self.send_request(
            method="PATCH",
            endpoint=f"/user/{user_id}",
            data = update_data,
            expected_status=expected_status
        )
    def authenticate(self, user_creds):
        login_data = {
            "email": user_creds[0],
            "password": user_creds[1]
        }
        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")
        token = response["accessToken"]
        self._update_session_headers(**{"authorization": "Bearer " + token})
        return response

