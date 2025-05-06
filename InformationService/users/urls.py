from django.urls import path
from django.http import HttpResponse
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    register,
    notifications_list, mark_notification_read,
    mark_all_notifications_read, get_unread_count
)
from .tasks import test_notification_system
from django.views.decorators.csrf import csrf_exempt

app_name = 'users'

def test_notifications_view(request):
    """
    View для тестирования отправки уведомлений
    """
    if not request.user.is_authenticated:
        return HttpResponse("Пожалуйста, войдите в систему для тестирования уведомлений")
    
    result = test_notification_system.delay()
    return HttpResponse(f"Тестовая задача запущена с ID: {result.id}")

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    path('test-notifications/', test_notifications_view, name='test_notifications'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),

    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark_all_read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread_count/', views.get_unread_count, name='get_unread_count'),
]
