from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class CustomUser(AbstractUser):
    # Дополнительные поля для профиля пользователя
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.username

    # Переопределяем метод save для автоматического управления правами
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Если пользователь новый и он в группе модераторов
            moderators_group = Group.objects.filter(name='Модераторы').first()
            if moderators_group and self.groups.filter(id=moderators_group.id).exists():
                self.is_staff = True  # Даем доступ к сайту
                self.is_superuser = False  # Запрещаем доступ к админке
                super().save()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
