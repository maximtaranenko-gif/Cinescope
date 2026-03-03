import requests

def test_get_bookings():
    response = requests.get('https://restful-booker.herokuapp.com/booking')
    assert response.status_code == 200
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.text}")