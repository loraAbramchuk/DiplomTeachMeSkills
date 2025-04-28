from django.db.models import Count, Avg, Q
from .models import Movie, Serial, Review, Genre
from collections import Counter
from django.db.models.functions import Coalesce

def get_user_preferred_genres(user, limit=5):
    """Получение предпочтительных жанров пользователя на основе его отзывов"""
    # Получаем все жанры из фильмов и сериалов, которые пользователь оценил положительно (рейтинг > 6)
    movie_genres = Genre.objects.filter(
        movie__review__user=user,
        movie__review__rating__gt=6
    ).values_list('id', 'name')
    
    serial_genres = Genre.objects.filter(
        serial__review__user=user,
        serial__review__rating__gt=6
    ).values_list('id', 'name')
    
    # Объединяем и подсчитываем частоту жанров
    all_genres = list(movie_genres) + list(serial_genres)
    genre_counter = Counter(all_genres)
    
    # Возвращаем наиболее частые жанры
    return [genre_id for genre_id, _ in genre_counter.most_common(limit)]

def get_recommendations_by_genres(user, content_type='all', limit=10):
    """Получение рекомендаций на основе предпочитаемых жанров"""
    preferred_genres = get_user_preferred_genres(user)
    
    # Если у пользователя нет предпочтений, возвращаем популярные items
    if not preferred_genres:
        if content_type == 'movies' or content_type == 'all':
            movies = Movie.objects.annotate(
                avg_rating=Coalesce(Avg('review__rating'), 0.0)
            ).order_by('-avg_rating')[:limit]
        if content_type == 'serials' or content_type == 'all':
            serials = Serial.objects.annotate(
                avg_rating=Coalesce(Avg('review__rating'), 0.0)
            ).order_by('-avg_rating')[:limit]
    else:
        # Получаем рекомендации с учетом предпочитаемых жанров
        if content_type == 'movies' or content_type == 'all':
            movies = Movie.objects.filter(
                genres__id__in=preferred_genres
            ).exclude(
                review__user=user
            ).annotate(
                genre_count=Count('genres', filter=Q(genres__id__in=preferred_genres)),
                avg_rating=Coalesce(Avg('review__rating'), 0.0)
            ).order_by('-genre_count', '-avg_rating')[:limit]
            
        if content_type == 'serials' or content_type == 'all':
            serials = Serial.objects.filter(
                genres__id__in=preferred_genres
            ).exclude(
                review__user=user
            ).annotate(
                genre_count=Count('genres', filter=Q(genres__id__in=preferred_genres)),
                avg_rating=Coalesce(Avg('review__rating'), 0.0)
            ).order_by('-genre_count', '-avg_rating')[:limit]
    
    if content_type == 'movies':
        return {'movies': movies}
    elif content_type == 'serials':
        return {'serials': serials}
    else:
        return {'movies': movies, 'serials': serials}

def get_similar_content(item, content_type, limit=5):
    """Получение похожего контента на основе жанров и стран"""
    if content_type == 'movie':
        similar_items = Movie.objects.filter(
            genres__in=item.genres.all()
        ).exclude(
            id=item.id
        ).annotate(
            matching_genres=Count('genres', filter=Q(genres__in=item.genres.all())),
            avg_rating=Coalesce(Avg('review__rating'), 0.0)
        ).order_by('-matching_genres', '-avg_rating')[:limit]
    else:
        similar_items = Serial.objects.filter(
            genres__in=item.genres.all()
        ).exclude(
            id=item.id
        ).annotate(
            matching_genres=Count('genres', filter=Q(genres__in=item.genres.all())),
            avg_rating=Coalesce(Avg('review__rating'), 0.0)
        ).order_by('-matching_genres', '-avg_rating')[:limit]
    
    return similar_items

def get_trending_content(days=7, limit=10):
    """Получение трендового контента за последние дни"""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg, Q
    
    date_threshold = timezone.now() - timedelta(days=days)
    
    # Получаем фильмы с отзывами за последние дни или высоким рейтингом
    trending_movies = Movie.objects.annotate(
        review_count=Count('review'),
        avg_rating=Coalesce(Avg('review__rating'), 0.0),
        recent_reviews=Count(
            'review',
            filter=Q(review__created_at__gte=date_threshold)
        )
    ).filter(
        Q(review__created_at__gte=date_threshold) |
        Q(avg_rating__gte=7.0)
    ).distinct().order_by('-recent_reviews', '-avg_rating')[:limit]
    
    # Получаем сериалы с отзывами за последние дни или высоким рейтингом
    trending_serials = Serial.objects.annotate(
        review_count=Count('review'),
        avg_rating=Coalesce(Avg('review__rating'), 0.0),
        recent_reviews=Count(
            'review',
            filter=Q(review__created_at__gte=date_threshold)
        )
    ).filter(
        Q(review__created_at__gte=date_threshold) |
        Q(avg_rating__gte=7.0)
    ).distinct().order_by('-recent_reviews', '-avg_rating')[:limit]
    
    # Если нет трендовых элементов, возвращаем самые новые
    if not trending_movies:
        trending_movies = Movie.objects.order_by('-created_at')[:limit]
    
    if not trending_serials:
        trending_serials = Serial.objects.order_by('-created_at')[:limit]
    
    return {
        'movies': trending_movies,
        'serials': trending_serials
    } 