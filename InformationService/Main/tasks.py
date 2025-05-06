from celery import shared_task
from .models import Movie, Serial
from django.utils import timezone
import logging
from users.tasks import send_notification, send_bulk_notifications
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

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