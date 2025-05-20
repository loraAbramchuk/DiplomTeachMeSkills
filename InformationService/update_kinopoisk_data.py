import os
import django
import logging

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InformationService.settings')
django.setup()

from Main.models import Movie, Serial
from Main.kinopoisk_parser import KinopoiskParser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kinopoisk_update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def update_movies():
    """Обновляет данные фильмов"""
    parser = KinopoiskParser()
    movies = Movie.objects.all()
    
    logger.info(f"Начинаем обновление {movies.count()} фильмов")
    
    for movie in movies:
        try:
            logger.info(f"Обновляем данные для фильма: {movie.title} ({movie.release_year})")
            data = parser.get_movie_data(movie.title, movie.release_year)
            
            if data:
                # Обновляем данные фильма
                movie.kinopoisk_id = data.get('kinopoisk_id', movie.kinopoisk_id)
                movie.kinopoisk_rating = data.get('kinopoisk_rating', movie.kinopoisk_rating)
                movie.kinopoisk_url = data.get('kinopoisk_url', movie.kinopoisk_url)
                movie.trailer_url = data.get('trailer_url', movie.trailer_url)
                movie.watch_url = data.get('watch_url', movie.watch_url)
                
                # Обновляем постер
                if data.get('poster_url'):
                    parser._save_image(data['poster_url'], movie, is_poster=True)
                
                # Обновляем кадры
                if data.get('frame_urls'):
                    # Удаляем старые кадры
                    movie.images.all().delete()
                    # Добавляем новые кадры
                    for frame_url in data['frame_urls']:
                        parser._save_image(frame_url, movie)
                
                movie.save()
                logger.info(f"Фильм {movie.title} успешно обновлен")
            else:
                logger.warning(f"Не удалось получить данные для фильма {movie.title}")
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении фильма {movie.title}: {str(e)}")

def update_serials():
    """Обновляет данные сериалов"""
    parser = KinopoiskParser()
    serials = Serial.objects.all()
    
    logger.info(f"Начинаем обновление {serials.count()} сериалов")
    
    for serial in serials:
        try:
            logger.info(f"Обновляем данные для сериала: {serial.title} ({serial.release_year})")
            data = parser.get_serial_data(serial.title, serial.release_year)
            
            if data:
                # Обновляем данные сериала
                serial.kinopoisk_id = data.get('kinopoisk_id', serial.kinopoisk_id)
                serial.kinopoisk_rating = data.get('kinopoisk_rating', serial.kinopoisk_rating)
                serial.kinopoisk_url = data.get('kinopoisk_url', serial.kinopoisk_url)
                serial.trailer_url = data.get('trailer_url', serial.trailer_url)
                serial.watch_url = data.get('watch_url', serial.watch_url)
                
                # Обновляем постер
                if data.get('poster_url'):
                    parser._save_image(data['poster_url'], serial, is_poster=True)
                
                # Обновляем кадры
                if data.get('frame_urls'):
                    # Удаляем старые кадры
                    serial.images.all().delete()
                    # Добавляем новые кадры
                    for frame_url in data['frame_urls']:
                        parser._save_image(frame_url, serial)
                
                serial.save()
                logger.info(f"Сериал {serial.title} успешно обновлен")
            else:
                logger.warning(f"Не удалось получить данные для сериала {serial.title}")
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении сериала {serial.title}: {str(e)}")

if __name__ == '__main__':
    logger.info("Начинаем обновление данных с Кинопоиска")
    update_movies()
    update_serials()
    logger.info("Обновление данных завершено") 