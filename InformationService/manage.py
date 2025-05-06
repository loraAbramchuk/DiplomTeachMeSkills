#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.core.mail import send_mail
from django.conf import settings

def test_email():
    try:
        send_mail(
            subject='Тестовое письмо',
            message='Это тестовое письмо для проверки настроек email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['larachka.06@gmail.com'],
            fail_silently=False,
        )
        print("Тестовое письмо успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке тестового письма: {str(e)}")
        print(f"Тип ошибки: {type(e)}")
        print(f"Детали ошибки: {e.__dict__ if hasattr(e, '__dict__') else 'Нет дополнительных деталей'}")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InformationService.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test_email':
        test_email()
    else:
        execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
