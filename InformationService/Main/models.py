from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Определение моделей

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

class MovieImage(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='movie_images/')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Изображение фильма"
        verbose_name_plural = "Изображения фильмов"

class SerialImage(models.Model):
    serial = models.ForeignKey('Serial', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='serial_images/')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Изображение сериала"
        verbose_name_plural = "Изображения сериалов"

class Movie(models.Model):
    """Модель фильма"""
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    release_year = models.IntegerField(verbose_name="Год выпуска")
    poster = models.ImageField(upload_to='posters/movies/', null=True, blank=True, verbose_name="Постер")
    trailer_url = models.URLField(max_length=255, null=True, blank=True, verbose_name="URL трейлера")
    watch_url = models.URLField(max_length=255, null=True, blank=True, verbose_name="URL для просмотра")
    kinopoisk_rating = models.FloatField(null=True, blank=True, verbose_name="Рейтинг Кинопоиска")
    kinopoisk_url = models.URLField(max_length=255, null=True, blank=True, verbose_name="URL на Кинопоиске")
    genres = models.ManyToManyField(Genre, verbose_name="Жанры")
    country = models.ManyToManyField(Country, verbose_name="Страны")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
        ordering = ['-created_at']

class Serial(models.Model):
    """Модель сериала"""
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    release_year = models.PositiveIntegerField(verbose_name="Год выпуска")
    genres = models.ManyToManyField(Genre, verbose_name="Жанры")
    country = models.ManyToManyField(Country, verbose_name="Страны")
    episodes = models.PositiveIntegerField(verbose_name="Количество эпизодов")
    poster = models.ImageField(upload_to='posters/serials/', blank=True, null=True, verbose_name="Постер")
    trailer_url = models.URLField(max_length=255, null=True, blank=True, verbose_name="URL трейлера")
    watch_url = models.URLField(max_length=255, null=True, blank=True, verbose_name="URL для просмотра")
    kinopoisk_rating = models.FloatField(null=True, blank=True, verbose_name="Рейтинг Кинопоиска")
    kinopoisk_url = models.URLField(max_length=255, null=True, blank=True, verbose_name="URL на Кинопоиске")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Сериал"
        verbose_name_plural = "Сериалы"
        ordering = ['-created_at']


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    serial = models.ForeignKey(Serial, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField()  # от 1 до 10, например
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На модерации'),
            ('approved', 'Одобрен'),
            ('rejected', 'Отклонен')
        ],
        default='pending'
    )

    def clean(self):
        if not self.movie and not self.serial:
            raise ValidationError('Необходимо указать фильм или сериал')
        if self.movie and self.serial:
            raise ValidationError('Нельзя одновременно указывать и фильм, и сериал')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.movie:
            return f"{self.user.username} - Фильм: {self.movie.title} ({self.rating})"
        return f"{self.user.username} - Сериал: {self.serial.title} ({self.rating})"
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

class Subscription(models.Model):
    """Модель подписки"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    duration_days = models.IntegerField(verbose_name="Длительность (в днях)")

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

class UserSubscription(models.Model):
    """Модель активной подписки пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT, verbose_name="Тип подписки")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    auto_renewal = models.BooleanField(default=True, verbose_name="Автопродление")

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = timezone.now() + timedelta(days=self.subscription.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.subscription.name}"

    class Meta:
        verbose_name = "Подписка пользователя"
        verbose_name_plural = "Подписки пользователей"

class Payment(models.Model):
    """Модель платежа"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT, verbose_name="Тип подписки")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'В обработке'),
        ('completed', 'Выполнен'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возвращен')
    ], default='pending', verbose_name="Статус")

    def __str__(self):
        return f"{self.user.username} - {self.amount} руб. ({self.get_status_display()})"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

