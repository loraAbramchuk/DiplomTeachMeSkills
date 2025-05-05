from rest_framework import permissions


class IsModeratorOrReadOnly(permissions.BasePermission):
    """
    Разрешение для модераторов на редактирование,
    остальные только на чтение.
    """
    def has_permission(self, request, view):
        # Разрешаем GET, HEAD и OPTIONS запросы всем пользователям
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Проверяем, аутентифицирован ли пользователь
        if not request.user.is_authenticated:
            return False
            
        # Разрешаем доступ только модераторам и суперпользователям
        return request.user.groups.filter(name='Модераторы').exists() or request.user.is_superuser


class IsSuperuserOnly(permissions.BasePermission):
    """
    Разрешение только для суперпользователей.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser