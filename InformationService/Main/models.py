from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.PositiveIntegerField()
    genres = models.ManyToManyField(Genre)
    country = models.ManyToManyField(Country)
    poster = models.ImageField(upload_to='posters/movies/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Serial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.PositiveIntegerField()
    genres = models.ManyToManyField(Genre)
    country = models.ManyToManyField(Country)
    episodes = models.PositiveIntegerField()
    poster = models.ImageField(upload_to='posters/serials/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    serial = models.ForeignKey(Serial, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField()  # от 1 до 10, например
    created_at = models.DateTimeField(auto_now_add=True)

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

