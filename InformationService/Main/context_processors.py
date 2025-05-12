from .recommendations import get_recommendations_by_genres, get_trending_content
from django.conf import settings

def media_settings(request):
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }

def recommendations_processor(request):
    """Добавляет рекомендации в контекст всех шаблонов"""
    # Получаем трендовый контент для незарегистрированных пользователей
    trending = get_trending_content(days=7, limit=4)
    
    context = {
        'header_movies': trending['movies'],
        'header_serials': trending['serials']
    }
    
    # Если пользователь авторизован, добавляем персональные рекомендации
    if request.user.is_authenticated:
        recommendations = get_recommendations_by_genres(request.user, limit=4)
        context.update({
            'header_recommended_movies': recommendations.get('movies', []),
            'header_recommended_serials': recommendations.get('serials', [])
        })
    
    return context 