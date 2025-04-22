from Main.models import Movie, Serial, Review
from django.contrib.auth import get_user_model

User = get_user_model()

# Получаем или создаем тестового пользователя
user, created = User.objects.get_or_create(
    username='test_user',
    defaults={
        'email': 'test@example.com',
        'is_active': True
    }
)
if created:
    user.set_password('test12345')
    user.save()
    print(f"Создан тестовый пользователь: {user.username}")

# Получаем фильмы и сериалы
movies = Movie.objects.all()
serials = Serial.objects.all()

# Создаем отзывы для фильмов
movie_reviews = [
    {
        'movie': 'Начало',
        'text': 'Потрясающий фильм с глубоким сюжетом. Кристофер Нолан создал настоящий шедевр, '
                'заставляющий задуматься о природе реальности и снов.',
        'rating': 9
    },
    {
        'movie': 'Унесённые призраками',
        'text': 'Великолепное аниме от Миядзаки. Волшебная история, прекрасная анимация и '
                'незабываемые персонажи. Один из лучших анимационных фильмов всех времен.',
        'rating': 10
    }
]

# Создаем отзывы для сериалов
serial_reviews = [
    {
        'serial': 'Игра в кальмара',
        'text': 'Захватывающий сериал, держащий в напряжении до последней серии. '
                'Отличная критика современного общества и человеческой природы.',
        'rating': 8
    },
    {
        'serial': 'Друзья',
        'text': 'Классический ситком, который никогда не устареет. Персонажи стали '
                'родными, а шутки до сих пор актуальны. Пересматриваю регулярно!',
        'rating': 9
    }
]

# Удаляем существующие отзывы
Review.objects.all().delete()
print("Удалены старые отзывы")

# Добавляем отзывы к фильмам
for review_data in movie_reviews:
    try:
        movie = Movie.objects.get(title=review_data['movie'])
        Review.objects.create(
            user=user,
            movie=movie,
            text=review_data['text'],
            rating=review_data['rating']
        )
        print(f"Добавлен отзыв к фильму: {movie.title}")
    except Movie.DoesNotExist:
        print(f"Фильм не найден: {review_data['movie']}")

# Добавляем отзывы к сериалам
for review_data in serial_reviews:
    try:
        serial = Serial.objects.get(title=review_data['serial'])
        Review.objects.create(
            user=user,
            serial=serial,
            text=review_data['text'],
            rating=review_data['rating']
        )
        print(f"Добавлен отзыв к сериалу: {serial.title}")
    except Serial.DoesNotExist:
        print(f"Сериал не найден: {review_data['serial']}")

print("\nГотово! Все тестовые отзывы добавлены.") 