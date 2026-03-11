from custom_requester.custom_requester import CustomRequester


class UserAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session= session, base_url="https://auth.dev-cinescope.coconutqa.ru/")


    def get_user_info(self, user_id, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    def delete_user(self,user_id, expected_status=200):
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    def cleanup_user(self, user_data):
        """
        Удалить пользователя после теста (с проверками)
        """
        if not user_data:
            print("Нет данных пользователя для cleanup")
            return False

        user_id = user_data.get("id")
        if not user_id:
            print(f"Нет ID у пользователя {user_data.get('email', 'unknown')}")
            return False

        try:
            self.delete_user(user_id)
            print(f"Cleanup: пользователь {user_data.get('email')} удален")
            return True
        except Exception as e:
            print(f"Cleanup error: {e}")
            return False




