from django.shortcuts import render, get_object_or_404, redirect
from .models import Genre, Country, Movie, Serial, Review, Subscription, UserSubscription, Payment
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from functools import wraps
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .recommendations import (
    get_recommendations_by_genres,
    get_similar_content,
    get_trending_content
)
from django.db.models import Q
from .kinopoisk_parser import KinopoiskParser


User = get_user_model()


def index(request):
    """Главная страница"""
    # Получаем последний добавленный фильм для баннера
    featured_movie = Movie.objects.order_by('-created_at').first()
    
    # Получаем последние 8 фильмов
    latest_movies = Movie.objects.order_by('-created_at')[1:9]
    
    # Получаем последние 8 сериалов
    latest_serials = Serial.objects.order_by('-created_at')[:8]
    
    # Получаем трендовый контент
    trending = get_trending_content(days=7, limit=8)
    
    context = {
        'featured_movie': featured_movie,
        'latest_movies': latest_movies,
        'latest_serials': latest_serials,
        'trending_movies': trending['movies'],
        'trending_serials': trending['serials'],
    }
    
    return render(request, 'Main/index.html', context)

def movies_list(request):
    """Список фильмов"""
    # Получаем параметры фильтрации
    genre = request.GET.get('genre', '')
    country = request.GET.get('country', '')
    
    # Получаем все жанры и страны для фильтров
    genres = Genre.objects.all()
    countries = Country.objects.all()
    
    # Базовый запрос
    movies = Movie.objects.all()
    
    # Применяем фильтры
    if genre:
        movies = movies.filter(genres__name=genre)
    if country:
        movies = movies.filter(country__name=country)
    
    context = {
        'movies': movies,
        'genres': genres,
        'countries': countries,
        'selected_genre': genre,
        'selected_country': country,
    }
    return render(request, 'Main/movies_list.html', context)

def serials_list(request):
    """Список сериалов"""
    # Получаем параметры фильтрации
    genre = request.GET.get('genre', '')
    country = request.GET.get('country', '')
    
    # Получаем все жанры и страны для фильтров
    genres = Genre.objects.all()
    countries = Country.objects.all()
    
    # Базовый запрос
    serials = Serial.objects.all()
    
    # Применяем фильтры
    if genre:
        serials = serials.filter(genres__name=genre)
    if country:
        serials = serials.filter(country__name=country)
    
    context = {
        'serials': serials,
        'genres': genres,
        'countries': countries,
        'selected_genre': genre,
        'selected_country': country,
    }
    return render(request, 'Main/serials_list.html', context)

def subscription_required(view_func):
    """Декоратор для проверки наличия активной подписки"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
            
        active_subscription = UserSubscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gt=timezone.now()
        ).exists()
        
        if not active_subscription:
            messages.warning(request, 'Для доступа к этому контенту необходима активная подписка.')
            return redirect('subscription_list')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@subscription_required
def movie_detail(request, pk):
    """Представление для конкретного фильма"""
    movie = get_object_or_404(Movie, pk=pk)
    print(f"\nЗапрос деталей фильма: {movie.title} ({movie.release_year})")
    
    # Проверяем, есть ли уже данные с Кинопоиска
    if not movie.kinopoisk_rating or not movie.trailer_url:
        print("Данные с Кинопоиска отсутствуют или неполные, получаем новые")
        parser = KinopoiskParser()
        kinopoisk_data = parser.get_movie_data(movie.title, movie.release_year, movie)
        
        if kinopoisk_data:
            print(f"Получены данные с Кинопоиска: {kinopoisk_data}")
            # Обновляем данные фильма
            movie.kinopoisk_rating = kinopoisk_data.get('kinopoisk_rating')
            movie.kinopoisk_url = kinopoisk_data.get('kinopoisk_url')
            movie.trailer_url = kinopoisk_data.get('trailer_url')
            movie.watch_url = kinopoisk_data.get('watch_url')
            movie.save()
            print("Данные фильма обновлены")
        else:
            print("Не удалось получить данные с Кинопоиска")
    else:
        print(f"Используем существующие данные с Кинопоиска: рейтинг {movie.kinopoisk_rating}")
    
    similar_movies = get_similar_content(movie, 'movie', limit=4)
    return render(request, 'Main/movie_detail.html', {
        'movie': movie,
        'genres': movie.genres.all(),
        'countries': movie.country.all(),
        'similar_movies': similar_movies,
        'images': movie.images.all()
    })

@subscription_required
def serial_detail(request, pk):
    """Представление для конкретного сериала"""
    serial = get_object_or_404(Serial, pk=pk)
    print(f"\nЗапрос деталей сериала: {serial.title} ({serial.release_year})")
    
    # Проверяем, есть ли уже данные с Кинопоиска
    if not serial.kinopoisk_rating or not serial.trailer_url:
        print("Данные с Кинопоиска отсутствуют или неполные, получаем новые")
        parser = KinopoiskParser()
        kinopoisk_data = parser.get_movie_data(serial.title, serial.release_year, serial)
        
        if kinopoisk_data:
            print(f"Получены данные с Кинопоиска: {kinopoisk_data}")
            # Обновляем данные сериала
            serial.kinopoisk_rating = kinopoisk_data.get('kinopoisk_rating')
            serial.kinopoisk_url = kinopoisk_data.get('kinopoisk_url')
            serial.trailer_url = kinopoisk_data.get('trailer_url')
            serial.watch_url = kinopoisk_data.get('watch_url')
            serial.save()
            print("Данные сериала обновлены")
        else:
            print("Не удалось получить данные с Кинопоиска")
    else:
        print(f"Используем существующие данные с Кинопоиска: рейтинг {serial.kinopoisk_rating}")
    
    similar_serials = get_similar_content(serial, 'serial', limit=4)
    return render(request, 'Main/serial_detail.html', {
        'serial': serial,
        'genres': serial.genres.all(),
        'countries': serial.country.all(),
        'similar_serials': similar_serials,
        'images': serial.images.all()
    })

@login_required
def add_movie_review(request, movie_id):
    """Добавление отзыва к фильму"""
    if request.method == 'POST':
        # Проверяем, что пользователь не является модератором
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, 'Модераторы не могут оставлять отзывы!')
            return redirect('movie_detail', pk=movie_id)
            
        movie = get_object_or_404(Movie, pk=movie_id)
        Review.objects.create(
            user=request.user,
            movie=movie,
            text=request.POST['text'],
            rating=request.POST['rating']
        )
        messages.success(request, 'Отзыв успешно добавлен!')
        return redirect('movie_detail', pk=movie_id)

@login_required
def add_serial_review(request, serial_id):
    """Добавление отзыва к сериалу"""
    if request.method == 'POST':
        # Проверяем, что пользователь не является модератором
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, 'Модераторы не могут оставлять отзывы!')
            return redirect('serial_detail', pk=serial_id)
            
        serial = get_object_or_404(Serial, pk=serial_id)
        Review.objects.create(
            user=request.user,
            serial=serial,
            text=request.POST['text'],
            rating=request.POST['rating']
        )
        messages.success(request, 'Отзыв успешно добавлен!')
        return redirect('serial_detail', pk=serial_id)

def about(request):
    """Страница о нас"""
    return render(request, 'about.html')

def user_profile(request, username):
    """Страница профиля пользователя с его рецензиями и рекомендациями"""
    user_profile = get_object_or_404(User, username=username)
    
    # Получаем все рецензии пользователя
    movie_reviews = Review.objects.filter(user=user_profile, movie__isnull=False).select_related('movie').order_by('-created_at')
    serial_reviews = Review.objects.filter(user=user_profile, serial__isnull=False).select_related('serial').order_by('-created_at')
    
    # Получаем персональные рекомендации для пользователя
    recommendations = get_recommendations_by_genres(user_profile, limit=2)
    
    # Получаем первые элементы из QuerySet безопасным способом
    recommended_movie = recommendations.get('movies', []).first() if recommendations.get('movies') else None
    recommended_serial = recommendations.get('serials', []).first() if recommendations.get('serials') else None
    
    context = {
        'user_profile': user_profile,
        'movie_reviews': movie_reviews,
        'serial_reviews': serial_reviews,
        'recommended_movie': recommended_movie,
        'recommended_serial': recommended_serial,
    }
    
    return render(request, 'Main/user_profile.html', context)

@login_required
def subscription_list(request):
    """Список доступных подписок"""
    subscriptions = Subscription.objects.all()
    user_subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()
    
    return render(request, 'Main/subscription_list.html', {
        'subscriptions': subscriptions,
        'user_subscription': user_subscription
    })

@login_required
def subscribe(request, subscription_id):
    """Подписка на тариф"""
    subscription = get_object_or_404(Subscription, pk=subscription_id)
    
    # Проверяем, нет ли уже активной подписки
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()
    
    if active_subscription:
        messages.warning(request, 'У вас уже есть активная подписка!')
        return redirect('subscription_list')
    
    # Создаем запись о подписке
    user_subscription = UserSubscription.objects.create(
        user=request.user,
        subscription=subscription,
        start_date=timezone.now(),
        end_date=timezone.now() + timezone.timedelta(days=30),
        is_active=True
    )
    
    # Создаем запись об оплате
    Payment.objects.create(
        user=request.user,
        subscription=subscription,
        amount=subscription.price,
        status='completed'
    )
    
    messages.success(request, f'Вы успешно подписались на тариф {subscription.name}!')
    return redirect('subscription_list')

@login_required
def cancel_subscription(request):
    """Отмена подписки"""
    subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()
    
    if subscription:
        subscription.is_active = False
        subscription.save()
        messages.success(request, 'Ваша подписка успешно отменена.')
    else:
        messages.warning(request, 'У вас нет активной подписки для отмены.')
    
    return redirect('subscription_list')

@login_required
def payment_history(request):
    """История платежей пользователя"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'Main/payment_history.html', {'payments': payments})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """Получение персонализированных рекомендаций для пользователя"""
    content_type = request.query_params.get('type', 'all')
    limit = int(request.query_params.get('limit', 10))
    
    recommendations = get_recommendations_by_genres(request.user, content_type, limit)
    
    if content_type == 'movies':
        serializer = MovieSerializer(recommendations['movies'], many=True)
    elif content_type == 'serials':
        serializer = SerialSerializer(recommendations['serials'], many=True)
    else:
        response_data = {
            'movies': MovieSerializer(recommendations['movies'], many=True).data,
            'serials': SerialSerializer(recommendations['serials'], many=True).data
        }
        return Response(response_data)
    
    return Response(serializer.data)

@api_view(['GET'])
def get_similar(request, content_type, pk):
    """Получение похожего контента"""
    limit = int(request.query_params.get('limit', 5))
    
    if content_type == 'movie':
        item = Movie.objects.get(pk=pk)
    else:
        item = Serial.objects.get(pk=pk)
    
    similar_items = get_similar_content(item, content_type, limit)
    
    if content_type == 'movie':
        serializer = MovieSerializer(similar_items, many=True)
    else:
        serializer = SerialSerializer(similar_items, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def get_trending(request):
    """Получение трендового контента"""
    days = int(request.query_params.get('days', 7))
    limit = int(request.query_params.get('limit', 10))
    
    trending = get_trending_content(days, limit)
    
    response_data = {
        'movies': MovieSerializer(trending['movies'], many=True).data,
        'serials': SerialSerializer(trending['serials'], many=True).data
    }
    
    return Response(response_data)

def trending(request):
    """Представление для страницы трендов"""
    # Запускаем задачу обновления популярности
    
    # Получаем все фильмы и сериалы, сортируем по дате создания
    movies = Movie.objects.prefetch_related('country', 'genres').all().order_by('-created_at')[:8]
    serials = Serial.objects.prefetch_related('country', 'genres').all().order_by('-created_at')[:8]
    
    # Если пользователь авторизован, добавляем персонализированные рекомендации
    if request.user.is_authenticated:
        recommendations = get_recommendations_by_genres(request.user, limit=4)
        recommended_movies = recommendations.get('movies', [])
        recommended_serials = recommendations.get('serials', [])
    else:
        recommended_movies = []
        recommended_serials = []
    
    context = {
        'popular_movies': movies,
        'popular_serials': serials,
        'recommended_movies': recommended_movies,
        'recommended_serials': recommended_serials,
        'new_movies': Movie.objects.prefetch_related('country', 'genres').all().order_by('-release_year')[:4],
        'new_serials': Serial.objects.prefetch_related('country', 'genres').all().order_by('-release_year')[:4],
    }
    
    return render(request, 'Main/trending.html', context)

def search(request):
    """Поиск контента по различным параметрам"""
    # Получаем параметры из GET-запроса
    query = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    country = request.GET.get('country', '').strip()
    year = request.GET.get('year', '').strip()
    content_type = request.GET.get('type', 'all')

    # Получаем все жанры и страны для фильтров
    genres = Genre.objects.all()
    countries = Country.objects.all()
    
    # Базовые запросы с предварительной загрузкой связанных данных
    movies = Movie.objects.prefetch_related('genres', 'country').all()
    serials = Serial.objects.prefetch_related('genres', 'country').all()
    
    # Применяем фильтры
    if query:
        movies = movies.filter(title__icontains=query)
        serials = serials.filter(title__icontains=query)
    
    if genre:
        movies = movies.filter(genres__name=genre)
        serials = serials.filter(genres__name=genre)
    
    if country:
        movies = movies.filter(country__name=country)
        serials = serials.filter(country__name=country)
    
    if year:
        try:
            year = int(year)
            movies = movies.filter(release_year=year)
            serials = serials.filter(release_year=year)
        except ValueError:
            pass
    
    # Фильтруем по типу контента
    if content_type == 'movies':
        serials = Serial.objects.none()
    elif content_type == 'serials':
        movies = Movie.objects.none()
    
    # Добавляем отладочную информацию
    print(f"Search parameters:")
    print(f"Query: '{query}'")
    print(f"Genre: '{genre}'")
    print(f"Country: '{country}'")
    print(f"Year: '{year}'")
    print(f"Content type: '{content_type}'")
    print(f"Movies found: {movies.count()}")
    print(f"Serials found: {serials.count()}")
    
    context = {
        'movies': movies.distinct(),
        'serials': serials.distinct(),
        'genres': genres,
        'countries': countries,
        'selected_genre': genre,
        'selected_country': country,
        'selected_year': year,
        'selected_type': content_type,
    }
    
    return render(request, 'Main/search_results.html', context)