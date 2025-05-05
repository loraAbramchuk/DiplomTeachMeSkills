import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем API ключ из переменных окружения или используем значение по умолчанию
KINOPOISK_API_KEY = os.getenv('KINOPOISK_API_KEY')

# Другие настройки
KINOPOISK_RATE_LIMIT = 20  # Ограничение запросов в секунду
KINOPOISK_TIMEOUT = 10  # Таймаут для запросов в секундах 