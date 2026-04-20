from custom_requester.custom_requester import CustomRequester

class UserAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session= session, base_url="https://auth.dev-cinescope.coconutqa.ru/")


    def get_user_info(self, user_id:int, expected_status:int=200):
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )
    def get_user(self, user_locator:dict, expected_status:int = 403):
        return self.send_request("GET", f"user/{user_locator}", expected_status=expected_status)

    def create_user(self, user_data:dict, expected_status:int = 201):
        return self.send_request(
            method="POST",
            endpoint="user",
            data = user_data,
            expected_status=expected_status
        )
    def delete_user(self,user_id, expected_status:int =204):
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )
    def update_role_user_admin(self, user_id:str, user_data:dict, expected_status:int = 200):
        """Обновление роли юзера(до админа)"""
        return self.send_request(
            method="PATCH",
            endpoint=f"/user/{user_id}",
            data = user_data,
            expected_status=expected_status
        )