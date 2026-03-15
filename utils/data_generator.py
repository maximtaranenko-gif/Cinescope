import random
import string
from faker import Faker
faker = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_password():
        letters = random.choice(string.ascii_letters) #Одна буква
        digits = random.choice(string.digits) #Одна цифра

        #Случайные символы
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18) #Остальная длина пароля
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        #Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

def generate_movie(price_range=(500, 3000), locations = None, genre_range = (1,10)):
    """Универсальная функция для генерации фильмов"""
    if locations is None:
        locations = ["MSK", "SPB"]

    return {
        "name": faker.sentence(),
        "imageUrl": "https://allwebs.ru/images/2026/03/14/5a789b9ac9178ace2c2e1c3b2564e64f.jpg",
        "price": faker.random_int(*price_range),
        "description": faker.text(),
        "location": random.choice(locations),
        "published": random.choice([True, False]),
        "genreId": random.randint(*genre_range),
    }
