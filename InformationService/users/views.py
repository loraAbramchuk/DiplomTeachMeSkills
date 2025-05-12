from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .forms import UserRegistrationForm
from .models import Notification, NewsletterSubscription
from .tasks import send_notification, send_bulk_notifications, test_notification_system
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('index')
        else:
            messages.error(request, 'Ошибка при регистрации. Пожалуйста, проверьте данные.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Уведомление не найдено'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Метод не разрешён'}, status=405)

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Метод не разрешён'}, status=405)

@login_required
def get_unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

def test_notifications(request):
    """
    Представление для запуска тестовой задачи уведомлений
    """
    test_notification_system.delay()
    return HttpResponse("Тестовая задача запущена. Проверьте уведомления через несколько секунд.")

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                subscription, created = NewsletterSubscription.objects.get_or_create(
                    email=email,
                    defaults={'is_active': True}
                )
                
                if created:
                    try:
                        # Подготовка HTML-сообщения
                        html_message = render_to_string('users/email/welcome.html', {
                            'email': email,
                            'site_url': settings.SITE_URL,
                        })
                        plain_message = strip_tags(html_message)
                        
                        # Отправка email
                        send_mail(
                            subject='Добро пожаловать в Movies Hub!',
                            message=plain_message,
                            html_message=html_message,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[email],
                            fail_silently=False,
                        )
                        messages.success(request, 'Вы успешно подписались на рассылку!')
                    except Exception as e:
                        logger.error(f"Ошибка при отправке email: {str(e)}")
                        messages.warning(request, 'Подписка оформлена, но возникла проблема с отправкой приветственного письма.')
                else:
                    if not subscription.is_active:
                        subscription.is_active = True
                        subscription.save()
                        messages.success(request, 'Ваша подписка восстановлена!')
                    else:
                        messages.info(request, 'Вы уже подписаны на нашу рассылку.')
            except Exception as e:
                logger.error(f"Ошибка при обработке подписки: {str(e)}")
                messages.error(request, 'Произошла ошибка при обработке подписки.')
        else:
            messages.error(request, 'Пожалуйста, введите корректный email адрес.')
    
    return redirect('about') 