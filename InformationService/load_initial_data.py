from Main.models import Country, Genre, Movie, Serial
from django.core.files import File
from django.conf import settings
import os

# Очищаем базу данных
print("Очищаем базу данных...")
Movie.objects.all().delete()
Serial.objects.all().delete()
Genre.objects.all().delete()
Country.objects.all().delete()

# Создаем страны
print("Создаем страны...")
countries_data = ['США', 'Великобритания', 'Франция', 'Япония', 'Южная Корея']
countries = {}
for country_name in countries_data:
    country = Country.objects.create(name=country_name)
    countries[country_name] = country

# Создаем жанры
print("Создаем жанры...")
genres_data = ['Драма', 'Комедия', 'Боевик', 'Фантастика', 'Триллер', 'Романтика', 'Аниме']
genres = {}
for genre_name in genres_data:
    genre = Genre.objects.create(name=genre_name)
    genres[genre_name] = genre

# Создаем фильмы
movies = [
    {
        'title': 'Начало',
        'description': 'Фильм о внедрении идей в подсознание через сон',
        'release_year': 2010,
        'genres': ['Фантастика', 'Боевик', 'Триллер'],
        'countries': ['США', 'Великобритания'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Унесённые призраками',
        'description': 'Анимационный фильм о девочке, попавшей в мир духов',
        'release_year': 2001,
        'genres': ['Аниме', 'Фантастика'],
        'countries': ['Япония'],
        'poster': 'zaglushka.jpg'
    }
]

# Создаем сериалы
serials = [
    {
        'title': 'Игра в кальмара',
        'description': 'Участники игры рискуют жизнью ради денежного приза',
        'release_year': 2021,
        'episodes': 9,
        'genres': ['Триллер', 'Драма'],
        'countries': ['Южная Корея'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Друзья',
        'description': 'Сериал о жизни шести друзей в Нью-Йорке',
        'release_year': 1994,
        'episodes': 236,
        'genres': ['Комедия', 'Романтика'],
        'countries': ['США'],
        'poster': 'zaglushka.jpg'
    }
]

def add_poster(instance, poster_filename, media_type):
    """Добавляет постер к фильму или сериалу"""
    poster_path = os.path.join(settings.MEDIA_ROOT, 'posters', media_type, poster_filename)
    if os.path.exists(poster_path):
        with open(poster_path, 'rb') as f:
            instance.poster.save(poster_filename, File(f), save=True)

# Создаем записи фильмов
print("Создаем фильмы...")
for movie_data in movies:
    movie = Movie.objects.create(
        title=movie_data['title'],
        description=movie_data['description'],
        release_year=movie_data['release_year']
    )
    # Добавляем жанры
    for genre_name in movie_data['genres']:
        movie.genres.add(genres[genre_name])
    # Добавляем страны
    for country_name in movie_data['countries']:
        movie.country.add(countries[country_name])
    # Добавляем постер
    if 'poster' in movie_data:
        add_poster(movie, movie_data['poster'], 'movies')

# Создаем записи сериалов
print("Создаем сериалы...")
for serial_data in serials:
    serial = Serial.objects.create(
        title=serial_data['title'],
        description=serial_data['description'],
        release_year=serial_data['release_year'],
        episodes=serial_data['episodes']
    )
    # Добавляем жанры
    for genre_name in serial_data['genres']:
        serial.genres.add(genres[genre_name])
    # Добавляем страны
    for country_name in serial_data['countries']:
        serial.country.add(countries[country_name])
    # Добавляем постер
    if 'poster' in serial_data:
        add_poster(serial, serial_data['poster'], 'serials')

print("Данные успешно загружены!") 