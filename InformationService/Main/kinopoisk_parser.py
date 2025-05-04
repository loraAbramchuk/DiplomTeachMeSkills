import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import quote
from .config import KINOPOISK_API_KEY, KINOPOISK_TIMEOUT
import tempfile
from django.core.files import File
from .models import MovieImage, SerialImage

class KinopoiskParser:
    BASE_URL = "https://www.kinopoisk.ru"
    API_BASE_URL = "https://kinopoiskapiunofficial.tech/api/v2.2"
    
    def __init__(self):
        self.api_key = KINOPOISK_API_KEY
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json',
        }
        print(f"Инициализация парсера с API ключом: {'*' * len(self.api_key)}")

    def get_movie_data(self, title, year=None, movie_obj=None):
        print(f"\nПоиск фильма: {title} ({year})")
        
        try:
            # Формируем поисковый запрос
            search_url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films?order=RATING&type=ALL&ratingFrom=0&ratingTo=10&yearFrom={year}&yearTo={year}&keyword={title}"
            print(f"URL поиска: {search_url}")
            
            search_response = requests.get(search_url, headers=self.headers)
            print(f"Код ответа поиска: {search_response.status_code}")
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                print(f"Найдено результатов: {search_data.get('total', 0)}")
                
                if search_data.get('items'):
                    movie = search_data['items'][0]
                    movie_id = movie.get('kinopoiskId')
                    print(f"ID фильма: {movie_id}")
                    
                    # Получаем детальную информацию о фильме
                    details_url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{movie_id}"
                    details_response = requests.get(details_url, headers=self.headers)
                    print(f"Код ответа деталей: {details_response.status_code}")
                    
                    if details_response.status_code == 200:
                        details = details_response.json()
                        
                        # Получаем трейлеры
                        videos_url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{movie_id}/videos"
                        videos_response = requests.get(videos_url, headers=self.headers)
                        print(f"Код ответа видео: {videos_response.status_code}")
                        print(f"Ответ видео: {videos_response.text}")
                        
                        trailer_url = None
                        if videos_response.status_code == 200:
                            videos_data = videos_response.json()
                            if videos_data.get('items'):
                                # Сначала ищем YouTube трейлер
                                for video in videos_data['items']:
                                    if video.get('site') == 'YOUTUBE' and video.get('type') == 'TRAILER':
                                        url = video.get('url')
                                        if url.startswith('https://www.youtube.com/watch?v='):
                                            trailer_url = url
                                        elif url.startswith('https://www.youtube.com/v/'):
                                            video_id = url.split('/v/')[1]
                                            trailer_url = f"https://www.youtube.com/watch?v={video_id}"
                                        print(f"Найден YouTube трейлер: {trailer_url}")
                                        break
                                
                                # Если YouTube трейлер не найден, ищем трейлер от Кинопоиска
                                if not trailer_url:
                                    for video in videos_data['items']:
                                        if video.get('site') == 'KINOPOISK_WIDGET' and 'трейлер' in video.get('name', '').lower():
                                            trailer_url = video.get('url')
                                            print(f"Найден трейлер Кинопоиска: {trailer_url}")
                                            break
                        
                        # Получаем кадры из фильма
                        if movie_obj:
                            images_url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{movie_id}/images?type=STILL"
                            images_response = requests.get(images_url, headers=self.headers)
                            print(f"Код ответа изображений: {images_response.status_code}")
                            
                            if images_response.status_code == 200:
                                images_data = images_response.json()
                                if images_data.get('items'):
                                    # Сохраняем первые 5 кадров
                                    for i, image_data in enumerate(images_data['items'][:5]):
                                        image_url = image_data.get('imageUrl')
                                        if image_url:
                                            try:
                                                # Скачиваем изображение
                                                img_response = requests.get(image_url)
                                                if img_response.status_code == 200:
                                                    # Создаем временный файл
                                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                                                        tmp_file.write(img_response.content)
                                                        # Создаем объект изображения
                                                        if isinstance(movie_obj, Serial):
                                                            SerialImage.objects.create(
                                                                serial=movie_obj,
                                                                image=File(open(tmp_file.name, 'rb')),
                                                                description=f"Кадр {i+1}"
                                                            )
                                                        else:
                                                            MovieImage.objects.create(
                                                                movie=movie_obj,
                                                                image=File(open(tmp_file.name, 'rb')),
                                                                description=f"Кадр {i+1}"
                                                            )
                                            except Exception as e:
                                                print(f"Ошибка при сохранении изображения: {str(e)}")
                        
                        # Получаем постер, если он есть в деталях
                        poster_url = details.get('posterUrl')
                        if poster_url and movie_obj and not movie_obj.poster:
                            try:
                                poster_response = requests.get(poster_url)
                                if poster_response.status_code == 200:
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                                        tmp_file.write(poster_response.content)
                                        movie_obj.poster.save(
                                            f"{movie_obj.title}_poster.jpg",
                                            File(open(tmp_file.name, 'rb'))
                                        )
                            except Exception as e:
                                print(f"Ошибка при сохранении постера: {str(e)}")
                        
                        result = {
                            'kinopoisk_rating': details.get('ratingKinopoisk'),
                            'kinopoisk_url': f"https://www.kinopoisk.ru/film/{movie_id}/",
                            'trailer_url': trailer_url,
                            'watch_url': f"https://www.kinopoisk.ru/film/{movie_id}/watch/"
                        }
                        print(f"Полученные данные: {json.dumps(result, ensure_ascii=False, indent=2)}")
                        return result
                    
            print("Не удалось найти фильм через API, пробуем парсинг веб-страницы")
            return self._parse_webpage(title, year)
            
        except Exception as e:
            print(f"Ошибка при получении данных: {str(e)}")
            return None

    def _parse_webpage(self, title, year):
        print(f"\nПарсинг веб-страницы для: {title} ({year})")
        search_url = f"https://www.kinopoisk.ru/index.php?kp_query={quote(title)}"
        
        try:
            response = requests.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Ищем первый результат поиска
                first_result = soup.find('div', class_='search_results')
                if first_result:
                    movie_link = first_result.find('a', href=True)
                    if movie_link:
                        movie_url = f"https://www.kinopoisk.ru{movie_link['href']}"
                        movie_response = requests.get(movie_url)
                        if movie_response.status_code == 200:
                            movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
                            rating = movie_soup.find('span', class_='rating_ball')
                            
                            result = {
                                'kinopoisk_rating': float(rating.text) if rating else None,
                                'kinopoisk_url': movie_url,
                                'trailer_url': None,
                                'watch_url': f"{movie_url}watch/"
                            }
                            print(f"Данные из веб-парсинга: {json.dumps(result, ensure_ascii=False, indent=2)}")
                            return result
        except Exception as e:
            print(f"Ошибка при парсинге веб-страницы: {str(e)}")
        return None

    @staticmethod
    def get_serial_data(title, year):
        """Получение данных о сериале с Кинопоиска"""
        return KinopoiskParser.get_movie_data(title, year) 