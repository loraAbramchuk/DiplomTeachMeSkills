import requests
from bs4 import BeautifulSoup
import time
import random

class KinopoiskParser:
    def __init__(self):
        self.base_url = "https://www.kinopoisk.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_movie_info(self, movie_id):
        """
        Получение информации о фильме по его ID
        """
        url = f"{self.base_url}/film/{movie_id}/"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлекаем основную информацию
            title = soup.find('h1', class_='styles_title__3f3kG').text.strip()
            rating = soup.find('span', class_='styles_rating__3VnXG').text.strip()
            description = soup.find('div', class_='styles_paragraph__2Otvx').text.strip()
            
            # Извлекаем жанры
            genres = [genre.text.strip() for genre in soup.find_all('span', class_='styles_genre__3Vf3k')]
            
            # Извлекаем год выпуска
            year = soup.find('span', class_='styles_year__3Vf3k').text.strip()
            
            return {
                'title': title,
                'rating': rating,
                'description': description,
                'genres': genres,
                'year': year
            }
            
        except Exception as e:
            print(f"Ошибка при парсинге фильма {movie_id}: {str(e)}")
            return None
            
    def search_movies(self, query):
        """
        Поиск фильмов по запросу
        """
        url = f"{self.base_url}/search/?q={query}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            movies = []
            for movie in soup.find_all('div', class_='styles_movie__3Vf3k'):
                title = movie.find('a', class_='styles_title__3Vf3k').text.strip()
                movie_id = movie.find('a', class_='styles_title__3Vf3k')['href'].split('/')[-2]
                rating = movie.find('span', class_='styles_rating__3VnXG').text.strip()
                
                movies.append({
                    'title': title,
                    'id': movie_id,
                    'rating': rating
                })
                
            return movies
            
        except Exception as e:
            print(f"Ошибка при поиске фильмов: {str(e)}")
            return []
            
    def get_top_movies(self, limit=10):
        """
        Получение топ фильмов
        """
        url = f"{self.base_url}/top/"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            top_movies = []
            for movie in soup.find_all('div', class_='styles_movie__3Vf3k')[:limit]:
                title = movie.find('a', class_='styles_title__3Vf3k').text.strip()
                movie_id = movie.find('a', class_='styles_title__3Vf3k')['href'].split('/')[-2]
                rating = movie.find('span', class_='styles_rating__3VnXG').text.strip()
                
                top_movies.append({
                    'title': title,
                    'id': movie_id,
                    'rating': rating
                })
                
            return top_movies
            
        except Exception as e:
            print(f"Ошибка при получении топ фильмов: {str(e)}")
            return [] 