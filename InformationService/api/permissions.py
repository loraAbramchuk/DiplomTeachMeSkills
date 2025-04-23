from rest_framework import permissions


class IsAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет только администраторам и модераторам
    создавать и редактировать объекты, а остальным пользователям - только просматривать.
    """
    def has_permission(self, request, view):
        # Разрешаем GET, HEAD и OPTIONS запросы всем пользователям
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Проверяем, аутентифицирован ли пользователь
        if not request.user.is_authenticated:
            return False
            
        # Разрешаем доступ администраторам и модераторам
        return request.user.is_staff or request.user.is_superuser 