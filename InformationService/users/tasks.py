from celery import shared_task
from django.utils import timezone
from .models import Notification, CustomUser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_notification_email(user, title, message, notification_type, created_at):
    """
    Отправка email-уведомления
    """
    try:
        logger.info(f"Начало отправки email для пользователя {user.username} ({user.email})")
        
        if not user.email:
            logger.error(f"У пользователя {user.username} не указан email")
            return
        
        context = {
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'created_at': created_at,
            'site_url': settings.SITE_URL,
        }
        
        logger.info(f"Контекст для шаблона: {context}")
        
        html_message = render_to_string(settings.NOTIFICATION_EMAIL_TEMPLATE, context)
        subject = f"{settings.NOTIFICATION_EMAIL_SUBJECT_PREFIX}{title}"
        
        logger.info(f"Параметры отправки email:")
        logger.info(f"Subject: {subject}")
        logger.info(f"From: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"To: {user.email}")
        logger.info(f"HTML message length: {len(html_message)}")
        
        # Проверяем настройки email
        logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        logger.info(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        logger.info(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        logger.info(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        logger.info(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Email успешно отправлен пользователю {user.username}")
    except Exception as e:
        logger.error(f"Ошибка при отправке email-уведомления: {str(e)}")
        logger.error(f"Тип ошибки: {type(e)}")
        logger.error(f"Детали ошибки: {e.__dict__ if hasattr(e, '__dict__') else 'Нет дополнительных деталей'}")
        raise

@shared_task
def send_notification(user_id, title, message, notification_type='info'):
    """
    Задача для отправки уведомления пользователю
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
        
        # Отправляем email-уведомление
        send_notification_email(user, title, message, notification_type, notification.created_at)
        
        logger.info(f"Уведомление отправлено пользователю {user.username}: {title}")
        return f"Уведомление отправлено: {notification.id}"
    except CustomUser.DoesNotExist:
        logger.error(f"Пользователь с ID {user_id} не найден")
        raise
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {str(e)}")
        raise

@shared_task
def send_bulk_notifications(user_ids, title, message, notification_type='info'):
    """
    Задача для массовой отправки уведомлений
    """
    try:
        notifications = []
        for user_id in user_ids:
            try:
                user = CustomUser.objects.get(id=user_id)
                notification = Notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type
                )
                notifications.append(notification)
                
                # Отправляем email-уведомление
                send_notification_email(user, title, message, notification_type, timezone.now())
                
            except CustomUser.DoesNotExist:
                logger.warning(f"Пользователь с ID {user_id} не найден")
                continue
        
        if notifications:
            Notification.objects.bulk_create(notifications)
            logger.info(f"Отправлено {len(notifications)} уведомлений")
            return f"Отправлено {len(notifications)} уведомлений"
        return "Нет уведомлений для отправки"
    except Exception as e:
        logger.error(f"Ошибка при массовой отправке уведомлений: {str(e)}")
        raise

@shared_task
def test_notification_system():
    """
    Тестовая задача для проверки работы системы уведомлений
    """
    try:
        logger.info("Начало выполнения тестовой задачи")
        
        # Получаем всех активных пользователей с email
        users = CustomUser.objects.filter(is_active=True).exclude(email='')
        user_ids = list(users.values_list('id', flat=True))
        
        logger.info(f"Найдено {len(user_ids)} активных пользователей с email")
        logger.info(f"ID пользователей: {user_ids}")
        
        if not user_ids:
            logger.warning("Нет активных пользователей с email для отправки уведомлений")
            return "Нет активных пользователей с email"
        
        # Отправляем тестовое уведомление
        result = send_bulk_notifications.delay(
            user_ids=user_ids,
            title="Тестовое уведомление",
            message="Это тестовое уведомление для проверки работы системы. Время отправки: " + timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            notification_type='info'
        )
        
        logger.info(f"Задача отправки уведомлений запущена с ID: {result.id}")
        logger.info(f"Тестовые уведомления отправлены в {timezone.now()}")
        return "Тестовые уведомления отправлены"
    except Exception as e:
        logger.error(f"Ошибка при отправке тестовых уведомлений: {str(e)}")
        logger.error(f"Тип ошибки: {type(e)}")
        logger.error(f"Детали ошибки: {e.__dict__ if hasattr(e, '__dict__') else 'Нет дополнительных деталей'}")
        raise 