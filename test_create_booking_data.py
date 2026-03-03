import pytest
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from conftest import booking_data
from constants import BASE_URL, HEADERS


class TestBookings:
    def test_create_booking(self, auth_session, booking_data):
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        assert create_booking.status_code == 200, "Ошибка при создании брони"

        booking_id = create_booking.json().get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"
        assert create_booking.json()["booking"]["firstname"] == booking_data["firstname"], "Заданное имя не совпадает"
        assert create_booking.json()["booking"]["totalprice"] == booking_data["totalprice"], "Заданная стоимость не совпадает"

        # Проверяем что бронирование можно получить по ID
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data["lastname"], "Заданная фамилия не совпадает"

        # Удаляем бронирование
        deleted_booking = auth_session.delete(f"{BASE_URL}/booking/{booking_id}")
        assert deleted_booking.status_code == 201, "Бронь не удалилась"

        # Проверяем, что бронирование больше недоступно
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 404, "Бронь не удалилась"

    def test_put_booking(self, auth_session, booking_data):
        updated_data = {
        "firstname": "Петр",  # Изменили имя
        "lastname": "Сидоров", # Изменили фамилию
        "totalprice": 300,     # Увеличили цену
        "depositpaid": False,  # Изменили статус депозита
        "bookingdates": {
            "checkin": "2025-01-01", # Новые даты
            "checkout": "2025-01-10"
        },
        "additionalneeds": "Ужин"
        }
        create_response = auth_session.post(
            f"{BASE_URL}/booking",
            json=booking_data
        )
        assert create_response.status_code == 200, "Не удалось создать бронирование"
        booking_id = create_response.json().get("bookingid")

        put_response = auth_session.put(
            f"{BASE_URL}/booking/{booking_id}",
            json=updated_data,
            headers = HEADERS
        )
        assert put_response.status_code == 200, "Не удалось изменить бронирование"
        get_response = auth_session.get(
            f"{BASE_URL}/booking/{booking_id}"
        )
        assert get_response.status_code == 200, "Не удалось получить ответ"

        get_data = get_response.json()
        assert get_data["firstname"] == updated_data["firstname"]
        assert get_data["lastname"] == updated_data["lastname"]
        assert get_data["totalprice"] == updated_data["totalprice"]
        assert get_data["depositpaid"] == updated_data["depositpaid"]
        assert get_data["bookingdates"] == updated_data["bookingdates"]
        assert get_data["additionalneeds"] == updated_data["additionalneeds"]

    def test_patch_booking(self, auth_session, booking_data):
        # Копия словаря
        original_data = booking_data.copy()

        post_request = auth_session.post(
            f"{BASE_URL}/booking",
            json = booking_data
        )
        booking_id = post_request.json().get("bookingid")

        updated_data = {
            "firstname" : "Alexey",
            "totalprice" : 100
        }

        patch_request = auth_session.patch(
            f"{BASE_URL}/booking/{booking_id}",
            json = updated_data ,
            headers = HEADERS
        )

        assert patch_request.status_code == 200, "Не удалось изменить конкретные поля"

        get_request = auth_session.get(
            f"{BASE_URL}/booking/{booking_id}"
        )

        get_data = get_request.json()
        assert get_data["firstname"] == updated_data["firstname"], "Поле не было изменено"
        assert get_data["totalprice"] == updated_data["totalprice"], "Поле не было изменено"
        assert get_data["lastname"] == original_data["lastname"], "Поле не было изменено"
        assert get_data["depositpaid"] == original_data["depositpaid"] , "Поле не было изменено"
        assert get_data["bookingdates"] == original_data["bookingdates"], "Поле не было изменено"
        assert get_data["additionalneeds"] == original_data["additionalneeds"], "Поле не было изменено"

    def test_negative_scenarios(self, auth_session, booking_data):

        missed_fields = {
            "firstname": "Geychik"
        }

        #Только одно поле в пост
        post_request = auth_session.post(
            f"{BASE_URL}/booking",
            json=missed_fields,
            headers=HEADERS
        )

        #Некорректная линка
        get_request = auth_session.get(
            f"{BASE_URL}/boooking",
            json = booking_data,
            headers = HEADERS
        )

        #Сразу две ошибки: Неавторизован , пустой json
        id = 1
        put_request = requests.put(
            f"{BASE_URL}/booking/{id}",
            json = {},
            headers= HEADERS
        )
        #Кривой ID
        delete_request = requests.delete(
            f"{BASE_URL}/booking/99999",
            json = booking_data,
            headers= HEADERS
        )

        assert post_request.status_code == 500, f"Ожидался 500, получен {post_request.status_code}"

        assert get_request.status_code == 404, f"Ожидался 404, получен {get_request.status_code}"

        assert put_request.status_code in [400, 401, 403, 404], f"Получен {put_request.status_code}"

        assert delete_request.status_code == 403, f"Ожидался 403, получен {delete_request.status_code}"



