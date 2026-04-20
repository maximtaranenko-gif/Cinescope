from models.user_models import RegisterUserResponse

class TestUser:
    def test_create_user_user_api(self, super_admin, creation_user_data):
        """Создание юзера"""
        response = super_admin.api.user_api.create_user(creation_user_data)
        create_response = RegisterUserResponse(**response.json())

        assert create_response.email == creation_user_data.email, "Email не совпадает"
        assert create_response.fullName == creation_user_data.fullName, "Имя не совпадает"
        assert create_response.roles == creation_user_data.roles, "Роль не совпадает"
        assert create_response.verified, "Пользователь не подтвержден "

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        """Получение информации о юзере """
        created_user_response = super_admin.api.user_api.create_user(creation_user_data, expected_status=201)
        created_user = RegisterUserResponse(**created_user_response.json())
        response_by_id = super_admin.api.user_api.get_user(created_user.id, expected_status=200).json()

        user_by_id = RegisterUserResponse(**response_by_id)

        assert user_by_id.id == created_user.id, "ID не совпадает"
        assert user_by_id.email == created_user.email, "Email не совпадает"
        assert user_by_id.roles == created_user.roles, "Роль не совпадает"
        assert user_by_id.verified, "Пользователь не подтвердил почту "
        assert created_user.verified, "Созданный пользователь не имеет подтверждения почты"

    def test_get_user_by_id_common_user(self, common_user):
        """Негативный тест: Получение информации о юзере под авторизацией обычного юзера(нужен ADMIN, SUPER_ADMIN)"""
        common_user.api.user_api.get_user(common_user.id, expected_status=403)