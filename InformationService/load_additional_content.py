from Main.models import Country, Genre, Movie, Serial
from django.core.files import File
from django.conf import settings
import os

# Получаем существующие жанры и страны
genres = {genre.name: genre for genre in Genre.objects.all()}
countries = {country.name: country for country in Country.objects.all()}

# Дополнительные фильмы
new_movies = [
    {
        'title': 'Интерстеллар',
        'description': 'Фантастическая история о путешествии через червоточину в поисках нового дома для человечества',
        'release_year': 2014,
        'genres': ['Фантастика', 'Драма'],
        'countries': ['США', 'Великобритания'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Паразиты',
        'description': 'История о двух семьях из разных социальных слоев и их неожиданном переплетении судеб',
        'release_year': 2019,
        'genres': ['Драма', 'Триллер'],
        'countries': ['Южная Корея'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Форрест Гамп',
        'description': 'История жизни простого человека с необычной судьбой',
        'release_year': 1994,
        'genres': ['Драма', 'Комедия'],
        'countries': ['США'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Твоё имя',
        'description': 'Романтическая история о двух подростках, которые обмениваются телами',
        'release_year': 2016,
        'genres': ['Аниме', 'Романтика', 'Фантастика'],
        'countries': ['Япония'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Джентльмены',
        'description': 'Криминальная комедия о британском наркобизнесе',
        'release_year': 2019,
        'genres': ['Комедия', 'Боевик'],
        'countries': ['Великобритания', 'США'],
        'poster': 'zaglushka.jpg'
    }
]

# Дополнительные сериалы
new_serials = [
    {
        'title': 'Очень странные дела',
        'description': 'Научно-фантастический сериал о загадочных событиях в маленьком городке',
        'release_year': 2016,
        'episodes': 34,
        'genres': ['Фантастика', 'Драма', 'Триллер'],
        'countries': ['США'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Чёрное зеркало',
        'description': 'Антология о влиянии технологий на общество',
        'release_year': 2011,
        'episodes': 22,
        'genres': ['Фантастика', 'Триллер', 'Драма'],
        'countries': ['Великобритания'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Атака титанов',
        'description': 'Аниме о борьбе человечества с гигантскими существами',
        'release_year': 2013,
        'episodes': 87,
        'genres': ['Аниме', 'Боевик', 'Фантастика'],
        'countries': ['Япония'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Корона',
        'description': 'Историческая драма о британской королевской семье',
        'release_year': 2016,
        'episodes': 60,
        'genres': ['Драма'],
        'countries': ['Великобритания'],
        'poster': 'zaglushka.jpg'
    },
    {
        'title': 'Тед Лассо',
        'description': 'Комедия о американском тренере, работающем с британской футбольной командой',
        'release_year': 2020,
        'episodes': 34,
        'genres': ['Комедия', 'Драма'],
        'countries': ['США', 'Великобритания'],
        'poster': 'zaglushka.jpg'
    }
]

def add_poster(instance, poster_filename, media_type):
    """Добавляет постер к фильму или сериалу"""
    # Сначала проверяем в общей директории media
    poster_path = os.path.join(settings.MEDIA_ROOT, poster_filename)
    if os.path.exists(poster_path):
        with open(poster_path, 'rb') as f:
            instance.poster.save(poster_filename, File(f), save=True)
    else:
        print(f"Постер {poster_filename} не найден в {poster_path}")

# Создаем записи фильмов
print("Добавляем новые фильмы...")
for movie_data in new_movies:
    # Проверяем, существует ли фильм с таким названием и годом
    existing_movie = Movie.objects.filter(
        title=movie_data['title'],
        release_year=movie_data['release_year']
    ).first()
    
    if existing_movie:
        print(f"Фильм '{movie_data['title']}' ({movie_data['release_year']}) уже существует")
        continue
    
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
    print(f"Добавлен фильм: {movie_data['title']}")

# Создаем записи сериалов
print("\nДобавляем новые сериалы...")
for serial_data in new_serials:
    # Проверяем, существует ли сериал с таким названием и годом
    existing_serial = Serial.objects.filter(
        title=serial_data['title'],
        release_year=serial_data['release_year']
    ).first()
    
    if existing_serial:
        print(f"Сериал '{serial_data['title']}' ({serial_data['release_year']}) уже существует")
        continue
    
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
    print(f"Добавлен сериал: {serial_data['title']}")

print("\nДополнительный контент успешно загружен!") 