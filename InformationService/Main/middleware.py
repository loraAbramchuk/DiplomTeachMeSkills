from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse, resolve
from django.http import Http404

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, является ли текущий URL частью админки
        resolved = resolve(request.path)
        if resolved.app_name == 'admin' or request.path.startswith('/admin/'):
            # Если пользователь не суперпользователь, запрещаем доступ
            if not request.user.is_superuser:
                raise Http404()

        # Проверка доступа к модераторской панели
        if request.path.startswith('/moderator/'):
            if not request.user.is_authenticated:
                messages.error(request, 'Необходима авторизация для доступа к панели модератора')
                return redirect('users:login')
            
            if not request.user.groups.filter(name='Модераторы').exists() and not request.user.is_superuser:
                messages.error(request, 'У вас нет прав для доступа к панели модератора')
                return redirect('index')

        return self.get_response(request) 