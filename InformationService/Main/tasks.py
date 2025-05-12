from celery import shared_task
from .models import Movie, Serial
from django.utils import timezone
import logging
from users.tasks import send_notification, send_bulk_notifications
from django.contrib.auth import get_user_model
from .kinopoisk_parser import KinopoiskParser
import requests

logger = logging.getLogger('Main.tasks')

User = get_user_model()



@shared_task
def notify_new_content():
    """
    Задача для отправки уведомлений о новом контенте
    """
    try:
        # Получаем пользователей, которые подписаны на уведомления
        users = User.objects.filter(is_active=True)
        user_ids = list(users.values_list('id', flat=True))
        
        # Получаем последние добавленные фильмы и сериалы
        latest_movies = Movie.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=1))
        latest_serials = Serial.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=1))
        
        if latest_movies.exists() or latest_serials.exists():
            message = "Новый контент на сайте!\n"
            if latest_movies.exists():
                message += f"Добавлено фильмов: {latest_movies.count()}\n"
            if latest_serials.exists():
                message += f"Добавлено сериалов: {latest_serials.count()}"
            
            # Отправляем уведомления
            send_bulk_notifications.delay(
                user_ids=user_ids,
                title="Новый контент",
                message=message,
                notification_type='info'
            )
            
        return "Уведомления о новом контенте отправлены"
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений о новом контенте: {str(e)}")
        raise

@shared_task
def notify_subscription_expiry():
    """
    Задача для отправки уведомлений об истечении подписки
    """
    try:
        # Получаем пользователей, у которых подписка истекает через 3 дня
        expiry_date = timezone.now() + timezone.timedelta(days=3)
        users = User.objects.filter(
            usersubscription__end_date__lte=expiry_date,
            usersubscription__end_date__gt=timezone.now(),
            usersubscription__is_active=True
        ).distinct()
        
        for user in users:
            subscription = user.usersubscription_set.filter(is_active=True).first()
            if subscription:
                days_left = (subscription.end_date - timezone.now()).days
                send_notification.delay(
                    user_id=user.id,
                    title="Подписка истекает",
                    message=f"Ваша подписка истекает через {days_left} дней. Продлите её, чтобы сохранить доступ к контенту.",
                    notification_type='warning'
                )
        
        return "Уведомления об истечении подписки отправлены"
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений об истечении подписки: {str(e)}")
        raise

@shared_task
def fetch_kinopoisk_data_task(content_type, content_id):
    """Задача для получения данных с Кинопоиска"""
    try:
        parser = KinopoiskParser()
        
        if content_type == 'movie':
            content = Movie.objects.get(id=content_id)
            logger.info(f"Получение данных для фильма: {content.title} ({content.release_year})")
            data = parser.get_movie_data(content.title, content.release_year)
        else:
            content = Serial.objects.get(id=content_id)
            logger.info(f"Получение данных для сериала: {content.title} ({content.release_year})")
            data = parser.get_serial_data(content.title, content.release_year)
        
        if data:
            # Обновляем данные контента
            content.kinopoisk_rating = data.get('kinopoisk_rating')
            content.kinopoisk_url = data.get('kinopoisk_url')
            content.trailer_url = data.get('trailer_url')
            content.watch_url = data.get('watch_url')
            
            # Сохраняем постер, если он есть
            poster_url = data.get('poster_url')
            if poster_url:
                logger.info(f"Сохраняем постер для {content.title}")
                if parser._save_image(poster_url, content, is_poster=True):
                    logger.info(f"Постер успешно сохранен для {content.title}")
                else:
                    logger.error(f"Не удалось сохранить постер для {content.title}")
            else:
                logger.warning(f"URL постера не найден для {content.title}")
            
            # Сохраняем кадры
            frame_urls = data.get('frame_urls', [])
            if frame_urls:
                logger.info(f"Начинаем сохранение {len(frame_urls)} кадров для {content.title}")
                saved_frames = 0
                for frame_url in frame_urls:
                    if parser._save_image(frame_url, content):
                        saved_frames += 1
                        logger.info(f"Сохранен кадр {saved_frames} из {len(frame_urls)} для {content.title}")
                    else:
                        logger.error(f"Не удалось сохранить кадр для {content.title}")
                logger.info(f"Всего сохранено {saved_frames} кадров для {content.title}")
            
            content.save()
            logger.info(f"Данные успешно обновлены для {content.title}")
            return True
        else:
            logger.warning(f"Не удалось получить данные для {content.title}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при выполнении задачи: {str(e)}")
        return False

@shared_task
def update_all_content_data():
    """
    Задача для обновления данных всех фильмов и сериалов
    """
    try:
        # Обновляем фильмы
        movies = Movie.objects.all()
        logger.info(f"Начинаем обновление данных для {movies.count()} фильмов")
        for movie in movies:
            fetch_kinopoisk_data_task.delay('movie', movie.id)
            logger.info(f"Задача обновления данных для фильма {movie.title} добавлена в очередь")
        
        # Обновляем сериалы
        serials = Serial.objects.all()
        logger.info(f"Начинаем обновление данных для {serials.count()} сериалов")
        for serial in serials:
            fetch_kinopoisk_data_task.delay('serial', serial.id)
            logger.info(f"Задача обновления данных для сериала {serial.title} добавлена в очередь")
        
        return f"Задачи обновления данных добавлены в очередь: {movies.count()} фильмов и {serials.count()} сериалов"
    except Exception as e:
        logger.error(f"Ошибка при создании задач обновления данных: {str(e)}")
        raise 