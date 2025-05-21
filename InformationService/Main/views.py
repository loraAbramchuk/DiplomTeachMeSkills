from django.shortcuts import render, get_object_or_404, redirect
from .models import Genre, Country, Movie, Serial, Review, Subscription, UserSubscription, Payment, MovieImage, SerialImage
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
from .tasks import fetch_kinopoisk_data_task
from django.conf import settings
import os
from django.db.models.functions import Lower
from django.db.models import Q
from django.shortcuts import render
from .models import Movie, Serial, Genre, Country


User = get_user_model()


def index(request):
    """Главная страница"""
    # Сначала пробуем получить фильм 'Очень странные дела' для баннера
    featured_movie = Movie.objects.filter(title='Начало', release_year=2010).first()
    # Если такого фильма нет, берем последний добавленный
    if not featured_movie:
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
            return redirect('Main:subscription_list')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@subscription_required
def movie_detail(request, movie_id):
    """Представление для отображения детальной информации о фильме"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Проверяем наличие постера и других данных
    #     has_poster = False
    # if movie.poster:
    #     try:
    #         has_poster = os.path.exists(movie.poster.path)
    #     except ValueError:
    #         has_poster = False
    has_poster = bool(movie.poster)
    
    # Если нет постера или других данных, запускаем задачу обновления
    if not has_poster or not movie.kinopoisk_rating or not movie.trailer_url:
        fetch_kinopoisk_data_task.delay('movie', movie.id)
    
    # Получаем отзывы для фильма
    reviews = Review.objects.filter(movie=movie).order_by('-created_at')
    
    # Получаем кадры из фильма
    frames = MovieImage.objects.filter(movie=movie)[:10]
    
    context = {
        'movie': movie,
        'reviews': reviews,
        'frames': frames,
        'has_poster': has_poster,
        'is_updating': not has_poster or not movie.kinopoisk_rating or not movie.trailer_url
    }
    
    return render(request, 'Main/movie_detail.html', context)

@subscription_required
def serial_detail(request, pk):
    """Представление для конкретного сериала"""
    serial = get_object_or_404(Serial, pk=pk)
    
    # Проверяем наличие постера и других данных
    # has_poster = False
    # if serial.poster:
    #     try:
    #         has_poster = os.path.exists(serial.poster.path)
    #     except ValueError:
    #         has_poster = False
    has_poster = bool(serial.poster)
    
    # Если нет постера или других данных, запускаем задачу обновления
    if not has_poster or not serial.kinopoisk_rating or not serial.trailer_url:
        fetch_kinopoisk_data_task.delay('serial', serial.id)
    
    # Получаем отзывы для сериала
    reviews = Review.objects.filter(serial=serial).order_by('-created_at')
    
    # Получаем кадры из сериала
    frames = SerialImage.objects.filter(serial=serial)[:10]
    
    context = {
        'serial': serial,
        'reviews': reviews,
        'frames': frames,
        'has_poster': has_poster,
        'is_updating': not has_poster or not serial.kinopoisk_rating or not serial.trailer_url
    }
    
    return render(request, 'Main/serial_detail.html', context)

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
    
    # Получаем активную подписку пользователя
    active_subscription = UserSubscription.objects.filter(
        user=user_profile,
        is_active=True,
        end_date__gt=timezone.now()
    ).select_related('subscription').first()
    
    context = {
        'user_profile': user_profile,
        'movie_reviews': movie_reviews,
        'serial_reviews': serial_reviews,
        'recommended_movie': recommended_movie,
        'recommended_serial': recommended_serial,
        'active_subscription': active_subscription,  # Добавляем информацию о подписке в контекст
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
        return redirect('Main:subscription_list')
    
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
    return redirect('Main:subscription_list')

@login_required
def cancel_subscription(request):
    """Отмена подписки или отключение автопродления"""
    if request.method == 'POST':
        action = request.POST.get('action')
        subscription = UserSubscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gt=timezone.now()
        ).first()
        
        if subscription:
            if action == 'cancel_subscription':
                subscription.is_active = False
                subscription.auto_renewal = False
                subscription.save()
                messages.success(request, 'Ваша подписка успешно отменена.')
            elif action == 'disable_auto_renewal':
                subscription.auto_renewal = False
                subscription.save()
                messages.success(request, 'Автопродление подписки отключено.')
        else:
            messages.warning(request, 'У вас нет активной подписки для отмены.')
    
    return redirect('Main:user_profile', username=request.user.username)

@login_required
def payment_history(request):
    """История платежей пользователя"""
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
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
    query = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    country = request.GET.get('country', '').strip()
    year = request.GET.get('year', '').strip()
    content_type = request.GET.get('type', 'all')

    genres = Genre.objects.all()
    countries = Country.objects.all()

    movies = Movie.objects.prefetch_related('genres', 'country').all()
    serials = Serial.objects.prefetch_related('genres', 'country').all()

    # Фильтрация по жанру (нерегистрозависимо)
    if genre:
        movies = movies.filter(genres__name__icontains=genre)
        serials = serials.filter(genres__name__icontains=genre)

    # Фильтрация по стране (нерегистрозависимо)
    if country:
        movies = movies.filter(country__name__icontains=country)
        serials = serials.filter(country__name__icontains=country)

    # Год
    if year:
        try:
            year = int(year)
            movies = movies.filter(release_year=year)
            serials = serials.filter(release_year=year)
        except ValueError:
            pass

    # Поиск по названию (нерегистрозависимый, временный костыль)
    if query:
        query_lower = query.lower()
        movies = [m for m in movies if query_lower in m.title.lower()]
        serials = [s for s in serials if query_lower in s.title.lower()]

    # Тип контента
    if content_type == 'movies':
        serials = []
    elif content_type == 'serials':
        movies = []

    context = {
        'movies': movies,
        'serials': serials,
        'genres': genres,
        'countries': countries,
        'selected_genre': genre,
        'selected_country': country,
        'selected_year': year,
        'selected_type': content_type,
        'query': query,
    }

    return render(request, 'Main/search_results.html', context)

@subscription_required
def video_player(request, content_type, content_id):
    """Представление для отображения видеоплеера"""
    if content_type == 'movie':
        content = get_object_or_404(Movie, id=content_id)
    else:
        content = get_object_or_404(Serial, id=content_id)
    
    context = {
        'video': {
            'url': content.watch_url,
            'poster': content.poster.url if content.poster else None,
            'title': content.title
        }
    }
    
    return render(request, 'video_player.html', context)

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '404.html', status=500)
