import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import quote
from .config import KINOPOISK_API_KEY, KINOPOISK_TIMEOUT
from django.core.files.base import ContentFile
from .models import MovieImage, SerialImage, Serial, Movie
import logging
import uuid

logger = logging.getLogger('Main.kinopoisk_parser')

class KinopoiskParser:
    BASE_URL = "https://www.kinopoisk.ru"
    API_BASE_URL = "https://kinopoiskapiunofficial.tech/api/v2.2"
    
    def __init__(self):
        self.api_key = KINOPOISK_API_KEY
        if not self.api_key:
            logger.error("API ключ Кинопоиска не найден в переменных окружения")
            raise ValueError("API ключ Кинопоиска не найден")
            
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json',
        }
        logger.info(f"Инициализация парсера с API ключом: {'*' * len(self.api_key)}")
    
    def _save_image(self, url, obj, is_poster=False):
        """Скачивает и сохраняет изображение в Cloudinary"""
        try:
            logger.info(f"Начинаем скачивание изображения с URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
            logger.info(f"Получен ответ от сервера: {response.status_code}")
            
            if response.status_code == 200:
                safe_title = re.sub(r'[^\w\s-]', '', obj.title)
                safe_title = re.sub(r'[-\s]+', '-', safe_title).strip('-_')
                
                if is_poster:
                    upload_path = 'posters/serials' if isinstance(obj, Serial) else 'posters/movies'
                    filename = f"{safe_title}_poster.jpg"
                    logger.info(f"Сохраняем постер в {upload_path}/{filename}")
                    temp_file = ContentFile(response.content)
                    logger.info(f"Создан временный файл размером {len(response.content)} байт")
                    obj.poster.save(filename, temp_file, save=True)
                    logger.info(f"Постер успешно сохранен в Cloudinary")
                    return True
                else:
                    upload_path = 'frames/serials' if isinstance(obj, Serial) else 'frames/movies'
                    filename = f"{safe_title}_frame_{uuid.uuid4().hex[:8]}.jpg"
                    logger.info(f"Сохраняем кадр в {upload_path}/{filename}")
                    image = MovieImage(movie=obj) if isinstance(obj, Movie) else SerialImage(serial=obj)
                    logger.info(f"Создан объект изображения для {'фильма' if isinstance(obj, Movie) else 'сериала'}")
                    image.image.save(filename, ContentFile(response.content), save=True)
                    logger.info(f"Кадр успешно сохранен в Cloudinary")
                    return True
            else:
                logger.error(f"Ошибка при скачивании изображения: {response.status_code}")
                logger.error(f"Текст ответа: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при сохранении изображения: {str(e)}")
            logger.exception("Полный стек ошибки:")
            return False

    def get_movie_data(self, title, year):
        """Получает данные о фильме с Кинопоиска"""
        logger.info(f"\nПолучение данных для: {title} ({year})")
        
        # Формируем URL для поиска
        search_url = f"{self.API_BASE_URL}/films"
        params = {
            'keyword': title,
            'yearFrom': year,
            'yearTo': year,
            'order': 'RATING',
            'type': 'ALL',
            'ratingFrom': 0,
            'ratingTo': 10
        }
        
        try:
            # Получаем список фильмов
            logger.info(f"Отправляем запрос к API: {search_url} с параметрами {params}")
            response = requests.get(search_url, params=params, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
            logger.info(f"Ответ API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Получены данные: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                if data.get('items'):
                    film = data['items'][0]
                    film_id = film.get('kinopoiskId')
                    logger.info(f"Найден фильм с ID: {film_id}")
                    
                    # Получаем детальную информацию о фильме
                    detail_url = f"{self.API_BASE_URL}/films/{film_id}"
                    logger.info(f"Запрашиваем детальную информацию: {detail_url}")
                    detail_response = requests.get(detail_url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        logger.info(f"Получены детальные данные: {json.dumps(detail_data, ensure_ascii=False, indent=2)}")
                        
                        # Получаем трейлеры и изображения
                        videos_url = f"{self.API_BASE_URL}/films/{film_id}/videos"
                        logger.info(f"Запрашиваем видео: {videos_url}")
                        videos_response = requests.get(videos_url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
                        
                        if videos_response.status_code == 200:
                            videos_data = videos_response.json()
                            logger.info(f"Получены данные о видео: {json.dumps(videos_data, ensure_ascii=False, indent=2)}")
                            trailer_url = None
                            for video in videos_data.get('items', []):
                                if video.get('site') == 'YOUTUBE':
                                    trailer_url = f"https://www.youtube.com/watch?v={video.get('url')}"
                                    logger.info(f"Найден трейлер: {trailer_url}")
                                    break
                            
                            # Проверяем URL постера
                            poster_url = detail_data.get('posterUrl')
                            if poster_url:
                                logger.info(f"Пробуем использовать URL постера без HEAD-проверки: {poster_url}")
                                # Просто используем этот URL, не делаем HEAD-запрос
                            
                            # Проверяем URL кадров
                            frame_urls = []
                            frames_url = f"{self.API_BASE_URL}/films/{film_id}/frames"
                            logger.info(f"Запрашиваем кадры: {frames_url}")
                            frames_response = requests.get(frames_url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
                            
                            if frames_response.status_code == 200:
                                frames_data = frames_response.json()
                                logger.info(f"Получены данные о кадрах: {json.dumps(frames_data, ensure_ascii=False, indent=2)}")
                                # Ограничиваем количество кадров до 10
                                frames = frames_data.get('frames', [])
                                logger.info(f"Найдено {len(frames)} кадров в ответе API")
                                frames = frames[:10]
                                for frame in frames:
                                    frame_url = frame.get('image')
                                    if frame_url:
                                        frame_urls.append(frame_url)
                                        logger.info(f"Добавлен URL кадра: {frame_url}")
                                    else:
                                        logger.warning(f"URL кадра не найден в данных: {frame}")
                                logger.info(f"Найдено {len(frame_urls)} валидных URL кадров")
                            
                            result = {
                                'kinopoisk_id': film_id,
                                'kinopoisk_rating': detail_data.get('ratingKinopoisk'),
                                'kinopoisk_url': f"https://www.kinopoisk.ru/film/{film_id}/",
                                'trailer_url': trailer_url,
                                'watch_url': f"https://www.kinopoisk.ru/film/{film_id}/watch/",
                                'poster_url': poster_url,
                                'frame_urls': frame_urls
                            }
                            logger.info(f"Данные из API: {json.dumps(result, ensure_ascii=False, indent=2)}")
                            return result
                        else:
                            logger.error(f"Ошибка при получении видео: {videos_response.status_code}")
                    else:
                        logger.error(f"Ошибка при получении детальной информации: {detail_response.status_code}")
                else:
                    logger.warning("Фильмы не найдены в ответе API")
            else:
                logger.error(f"Ошибка при поиске фильма: {response.status_code}")
                logger.error(f"Текст ответа: {response.text}")
            
            # Если API не нашел фильм, пробуем парсить веб-страницу
            logger.info("Фильм не найден через API, пробуем парсить веб-страницу")
            return self._parse_webpage(title, year)
            
        except Exception as e:
            logger.error(f"Ошибка при получении данных: {str(e)}")
            return None 

    def _parse_webpage(self, title, year):
        """Парсит данные с веб-страницы Кинопоиска"""
        try:
            # Формируем URL для поиска
            search_url = f"{self.BASE_URL}/index.php?kp_query={quote(title)}"
            logger.info(f"Отправляем запрос к веб-странице: {search_url}")
            
            response = requests.get(search_url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем первый результат поиска
                search_result = soup.find('div', class_='search_results')
                if search_result:
                    first_result = search_result.find('div', class_='element')
                    if first_result:
                        # Получаем ID фильма
                        film_link = first_result.find('a', class_='name')
                        if film_link:
                            film_url = film_link.get('href')
                            film_id = re.search(r'/film/(\d+)/', film_url)
                            if film_id:
                                film_id = film_id.group(1)
                                logger.info(f"Найден фильм с ID: {film_id}")
                                
                                # Получаем детальную информацию
                                detail_url = f"{self.BASE_URL}/film/{film_id}/"
                                logger.info(f"Запрашиваем детальную информацию: {detail_url}")
                                detail_response = requests.get(detail_url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
                                
                                if detail_response.status_code == 200:
                                    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                    
                                    # Получаем рейтинг
                                    rating_block = detail_soup.find('div', class_='rating')
                                    rating = None
                                    if rating_block:
                                        rating_text = rating_block.find('span', class_='rating_ball')
                                        if rating_text:
                                            rating = float(rating_text.text.strip())
                                    
                                    # Получаем URL постера
                                    poster_block = detail_soup.find('div', class_='film-poster')
                                    poster_url = None
                                    if poster_block:
                                        poster_img = poster_block.find('img')
                                        if poster_img:
                                            poster_url = poster_img.get('src')
                                            if poster_url:
                                                poster_url = f"https:{poster_url}" if poster_url.startswith('//') else poster_url
                                    
                                    # Получаем URL трейлера
                                    trailer_block = detail_soup.find('div', class_='trailer')
                                    trailer_url = None
                                    if trailer_block:
                                        trailer_link = trailer_block.find('a')
                                        if trailer_link:
                                            trailer_url = trailer_link.get('href')
                                            if trailer_url:
                                                trailer_url = f"https:{trailer_url}" if trailer_url.startswith('//') else trailer_url
                                    
                                    # Получаем кадры
                                    frame_urls = []
                                    frames_block = detail_soup.find('div', class_='film-frames')
                                    if frames_block:
                                        frame_links = frames_block.find_all('a')
                                        for frame_link in frame_links:
                                            frame_url = frame_link.get('href')
                                            if frame_url:
                                                frame_url = f"https:{frame_url}" if frame_url.startswith('//') else frame_url
                                                frame_urls.append(frame_url)
                                    
                                    result = {
                                        'kinopoisk_id': film_id,
                                        'kinopoisk_rating': rating,
                                        'kinopoisk_url': detail_url,
                                        'trailer_url': trailer_url,
                                        'watch_url': f"{self.BASE_URL}/film/{film_id}/watch/",
                                        'poster_url': poster_url,
                                        'frame_urls': frame_urls
                                    }
                                    logger.info(f"Данные из веб-страницы: {json.dumps(result, ensure_ascii=False, indent=2)}")
                                    return result
                                else:
                                    logger.error(f"Ошибка при получении детальной информации: {detail_response.status_code}")
                            else:
                                logger.warning("Не удалось извлечь ID фильма из URL")
                        else:
                            logger.warning("Не найден элемент с ссылкой на фильм")
                    else:
                        logger.warning("Не найдены результаты поиска")
                else:
                    logger.warning("Не найден блок с результатами поиска")
            else:
                logger.error(f"Ошибка при поиске фильма: {response.status_code}")
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге веб-страницы: {str(e)}")
            return None 

    def get_serial_data(self, title, year):
        """Получает данные о сериале с Кинопоиска"""
        logger.info(f"\nПолучение данных для сериала: {title} ({year})")
        
        # Формируем URL для поиска
        search_url = f"{self.API_BASE_URL}/films"
        params = {
            'keyword': title,
            'yearFrom': year,
            'yearTo': year,
            'order': 'RATING',
            'type': 'TV_SERIES',
            'ratingFrom': 0,
            'ratingTo': 10
        }
        
        try:
            # Получаем список сериалов
            logger.info(f"Отправляем запрос к API: {search_url} с параметрами {params}")
            response = requests.get(search_url, params=params, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
            logger.info(f"Ответ API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Получены данные: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                if data.get('items'):
                    serial = data['items'][0]
                    serial_id = serial.get('kinopoiskId')
                    logger.info(f"Найден сериал с ID: {serial_id}")
                    
                    # Получаем детальную информацию о сериале
                    detail_url = f"{self.API_BASE_URL}/films/{serial_id}"
                    logger.info(f"Запрашиваем детальную информацию: {detail_url}")
                    detail_response = requests.get(detail_url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        logger.info(f"Получены детальные данные: {json.dumps(detail_data, ensure_ascii=False, indent=2)}")
                        
                        # Получаем трейлеры и изображения
                        videos_url = f"{self.API_BASE_URL}/films/{serial_id}/videos"
                        logger.info(f"Запрашиваем видео: {videos_url}")
                        videos_response = requests.get(videos_url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
                        
                        if videos_response.status_code == 200:
                            videos_data = videos_response.json()
                            logger.info(f"Получены данные о видео: {json.dumps(videos_data, ensure_ascii=False, indent=2)}")
                            trailer_url = None
                            for video in videos_data.get('items', []):
                                if video.get('site') == 'YOUTUBE':
                                    video_url = video.get('url')
                                    if video_url:
                                        # Извлекаем ID видео из URL
                                        video_id = video_url.split('/')[-1]
                                        trailer_url = f"https://www.youtube.com/watch?v={video_id}"
                                        logger.info(f"Найден трейлер: {trailer_url}")
                                        break
                            
                            # Проверяем URL постера
                            poster_url = detail_data.get('posterUrl')
                            if poster_url:
                                logger.info(f"Пробуем использовать URL постера без HEAD-проверки: {poster_url}")
                                # Просто используем этот URL, не делаем HEAD-запрос
                            
                            # Проверяем URL кадров
                            frame_urls = []
                            frames_url = f"{self.API_BASE_URL}/films/{serial_id}/frames"
                            logger.info(f"Запрашиваем кадры: {frames_url}")
                            frames_response = requests.get(frames_url, headers=self.headers, timeout=KINOPOISK_TIMEOUT)
                            
                            if frames_response.status_code == 200:
                                frames_data = frames_response.json()
                                logger.info(f"Получены данные о кадрах: {json.dumps(frames_data, ensure_ascii=False, indent=2)}")
                                # Ограничиваем количество кадров до 10
                                frames = frames_data.get('frames', [])[:10]
                                for frame in frames:
                                    frame_url = frame.get('image')
                                    if frame_url:
                                        frame_urls.append(frame_url)
                                        logger.info(f"Добавлен URL кадра: {frame_url}")
                                logger.info(f"Найдено {len(frame_urls)} кадров")
                            
                            result = {
                                'kinopoisk_id': serial_id,
                                'kinopoisk_rating': detail_data.get('ratingKinopoisk'),
                                'kinopoisk_url': f"https://www.kinopoisk.ru/film/{serial_id}/",
                                'trailer_url': trailer_url,
                                'watch_url': f"https://www.kinopoisk.ru/film/{serial_id}/watch/",
                                'poster_url': poster_url,
                                'frame_urls': frame_urls
                            }
                            logger.info(f"Данные из API: {json.dumps(result, ensure_ascii=False, indent=2)}")
                            return result
                        else:
                            logger.error(f"Ошибка при получении видео: {videos_response.status_code}")
                    else:
                        logger.error(f"Ошибка при получении детальной информации: {detail_response.status_code}")
                else:
                    logger.warning("Сериалы не найдены в ответе API")
            else:
                logger.error(f"Ошибка при поиске сериала: {response.status_code}")
                logger.error(f"Текст ответа: {response.text}")
            
            # Если API не нашел сериал, пробуем парсить веб-страницу
            logger.info("Сериал не найден через API, пробуем парсить веб-страницу")
            return self._parse_webpage(title, year)
            
        except Exception as e:
            logger.error(f"Ошибка при получении данных: {str(e)}")
            return None 