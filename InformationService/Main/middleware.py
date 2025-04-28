from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверка доступа к основной админке
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                messages.error(request, 'Необходима авторизация для доступа к админ-панели')
                return redirect('users:login')
            
            if not request.user.is_superuser:
                messages.error(request, 'Доступ запрещен. Только для администраторов.')
                return redirect('index')

        # Проверка доступа к модераторской панели
        if request.path.startswith('/moderator/'):
            if not request.user.is_authenticated:
                messages.error(request, 'Необходима авторизация для доступа к панели модератора')
                return redirect('users:login')
            
            if not request.user.groups.filter(name='Модераторы').exists() and not request.user.is_superuser:
                messages.error(request, 'У вас нет прав для доступа к панели модератора')
                return redirect('index')

        return self.get_response(request) 